"""The snapshot submission endpoint, as a dependency-free WSGI application.

Two routes and no more:

| Route | Caller | Authority |
|---|---|---|
| `POST /api/v1/foundry/snapshots` | the Freedom Blades Foundry module | a submit-only service principal |
| `GET  /api/v1/foundry/snapshots/{checksum}/preview` | a Guild Council member | resolved server-side, per request |

The second route is **inert without a Phase 3 authentication composition**. With
no preview service composed it answers `503 authentication_unavailable` and
reaches no application service at all. This is the honest form of "the
Discord-authenticated boundary does not exist yet": the contract is implemented
and tested, and production cannot serve it because production has nothing to
authenticate with. Faking a session here would be the alternative, and it would
be worse than the gap it papered over.

## What this adapter is responsible for

Transport, and nothing that decides anything:

- bound the request before reading it, so an oversized body is refused rather
  than buffered;
- resolve the credential to a principal;
- pass the bytes, the request key and the claimed digest through unchanged;
- translate a typed application result into a status code and a safe body.

Every decision about *what the bytes mean* belongs to
`SnapshotSubmissionService`, which is where it can be tested without a socket.

## Why nothing from the request is trusted beyond the bytes

A filename, a declared Actor count, a folder path, a world id and a content
length are all things the client could simply be wrong about, and the server
derives each of them from its own parse instead. The exception that proves it is
`X-Snapshot-SHA256`: the client's claim is compared to the server's own digest
of what arrived, and a disagreement is a refusal — the claim is never *used* as
the identity.

## The browser is the caller, so CORS is part of the contract

The module submits from a Foundry browser client, with four headers that are not
CORS-safelisted. In the deployed cross-origin topology the browser therefore
sends an unauthenticated `OPTIONS` preflight *first* and will not send the POST
at all unless that preflight is answered. Review findings B-1 and S-I-1 are that
this adapter answered `405` and emitted no permission, so the supported workflow
could not reach application code.

`adapters/http/cors.py` owns that policy — an explicit allowlist of exact
origins, a bounded preflight for this route only, no cookie authority, and the
`Vary` handling that keeps a cache from confusing one origin's answer with
another's. This module owns only *where* it is applied:

- the preflight is answered **before** authentication, because a browser does
  not put the credential on a preflight;
- the permission header goes on **every** actual response for the submission
  route, including refusals and the unexpected-`500` path, because a response the
  browser may not read reaches the module as an indistinguishable network
  failure; and
- nothing else on the route changes: a caller with no `Origin` — `curl`, the
  smoke test, the loopback rehearsal — is untouched by any of it.

## Safety of what goes back out

Every response is JSON, `no-store`, `nosniff`, and carries a fixed message drawn
from a closed vocabulary. No exception text, no SQL, no path, no artifact byte
and no Actor value crosses this boundary. Unexpected exceptions become a plain
500 whose body says only that something failed; the exception itself is logged
through `adapters.safe_logging`, which records a category and a class name and
nothing else.

**What a failure response may claim.** Implementation review I-1: the artifact
is stored before the database transaction commits, deliberately, so a database
or unexpected failure *may* leave a correct content-addressed file with no row
pointing at it. A response that said "nothing was stored" was therefore
asserting something the failing path had not established. Every such message now
says what is actually known — no submission was **recorded or confirmed**, and
retrying the same `Idempotency-Key` is safe — which is also the only part the
caller can act on.
"""
from __future__ import annotations

import json
import logging
import re
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import parse_qs

from adapters.http.cors import CorsPolicy, PreflightAllowed, origin_of
from adapters.http.credentials import (
    AuthenticationFailed,
    ServicePrincipalRegistry,
    parse_bearer,
)
from adapters.safe_logging import log_expected_failure
from application.authorization import NotAuthorizedError
from application.errors import PersistenceError, UniquenessConflict
from application.foundry.import_service import ImportRefused
from application.foundry.preview_service import (
    PreviewUnavailable,
    SnapshotPreviewService,
)
from application.foundry.submission import (
    SnapshotSubmissionService,
    SubmissionRefused,
)

logger = logging.getLogger(__name__)

SUBMISSION_PATH = "/api/v1/foundry/snapshots"
_PREVIEW_PATH = re.compile(r"^/api/v1/foundry/snapshots/([0-9a-fA-F]{64})/preview$")

#: The one body type accepted. A parameter such as `; charset=utf-8` is allowed;
#: anything else is refused before the body is read.
_JSON_MEDIA_TYPE = "application/json"

#: Headers on every response, success or failure. `Content-Type` is added
#: separately, because a preflight answers `204` and a `204` must carry none.
_SAFE_HEADERS = (
    # An artifact receipt names a snapshot a Council member has not yet seen.
    ("Cache-Control", "no-store"),
    ("X-Content-Type-Options", "nosniff"),
    ("Referrer-Policy", "no-referrer"),
)

_JSON_CONTENT_TYPE = ("Content-Type", "application/json; charset=utf-8")


@dataclass(frozen=True, slots=True)
class _Response:
    """One answer: a status, an optional JSON body, and any extra headers.

    `payload=None` is a genuinely body-less response — only the `204` preflight
    produces one — and it deliberately carries no `Content-Type`, because a
    `204` that declares a media type for content it does not have is malformed.
    """

    status: int
    payload: dict[str, Any] | None = None
    headers: tuple[tuple[str, str], ...] = field(default=())

#: How a refusal from the application maps onto a status code. Everything not
#: named here is a client error the caller can correct, hence 400.
_REFUSAL_STATUS = {
    "request_key_conflict": 409,
    "concurrent_submission": 409,
    "original_result_unavailable": 409,
    "storage_unavailable": 503,
    # `403`, and the choice matters more than it looks. `409` and `503` both
    # mean "try again" to a client library, and the module's own retry would
    # then hammer a credential that can never succeed while a settlement is in
    # progress. A closed admission is a permanent refusal *for this credential*:
    # the way forward is a new credential from an operator, not a later attempt.
    "admission_closed": 403,
}

_PREVIEW_STATUS = {
    "snapshot_not_held": 404,
    "artifact_unreadable": 503,
}


class SnapshotSubmissionApplication:
    """The WSGI callable.

    `preview` is optional and is `None` until a Phase 3 authentication
    composition can supply one. That absence is the deployment control, not a
    flag somebody could flip by accident: there is no code path that constructs
    a preview service without an `AuthorizationPort`.
    """

    def __init__(
        self,
        submissions: SnapshotSubmissionService,
        credentials: ServicePrincipalRegistry,
        *,
        cors: CorsPolicy | None = None,
        preview: SnapshotPreviewService | None = None,
        preview_user_resolver: Callable[[Mapping[str, Any]], int] | None = None,
    ) -> None:
        self._submissions = submissions
        self._credentials = credentials
        # An absent policy is an empty allowlist, not an open one: no browser
        # origin is permitted until an operator names one.
        self._cors = cors if cors is not None else CorsPolicy()
        self._preview = preview
        self._preview_user_resolver = preview_user_resolver

    def __call__(
        self,
        environ: Mapping[str, Any],
        start_response: Callable[[str, list[tuple[str, str]]], Any],
    ) -> Iterable[bytes]:
        # Read before routing, so the unexpected-exception path below still
        # emits the permission the browser needs in order to read the failure.
        origin = origin_of(environ)
        submission_route = environ.get("PATH_INFO", "") == SUBMISSION_PATH
        preflight = (
            submission_route
            and environ.get("REQUEST_METHOD", "GET").upper() == "OPTIONS"
        )
        try:
            response = self._route(environ)
        except Exception as error:  # noqa: BLE001 - the boundary's whole job
            # A defect must not become a response body. The category and the
            # exception's class name are logged; nothing else about it exists
            # outside this process.
            log_expected_failure(logger, "http_unhandled", error, level=logging.ERROR)
            response = _Response(
                500,
                _error(
                    "internal_error",
                    # Not "nothing was stored" (review finding I-1). An
                    # unexpected exception can be raised after the artifact was
                    # written and before the transaction committed, and this
                    # path has established nothing about which.
                    "The request could not be completed. No submission was "
                    "recorded or confirmed. Retrying with the same "
                    "Idempotency-Key is safe. If it keeps happening, an "
                    "operator should check the service log.",
                ),
            )

        headers = list(_SAFE_HEADERS)
        if submission_route:
            headers.append(("Vary", self._cors.vary_for(preflight=preflight)))
            if not preflight:
                headers.extend(self._cors.response_headers(origin))
        else:
            headers.append(("Vary", "Authorization"))
        headers.extend(response.headers)

        if response.payload is None:
            body = b""
        else:
            body = json.dumps(response.payload, separators=(",", ":")).encode("utf-8")
            headers.append(_JSON_CONTENT_TYPE)
            headers.append(("Content-Length", str(len(body))))
        if response.status == 401:
            headers.append(("WWW-Authenticate", 'Bearer realm="freedom-blades"'))
        start_response(_status_line(response.status), headers)
        return [body]

    # -- routing --------------------------------------------------------------

    def _route(self, environ: Mapping[str, Any]) -> _Response:
        path = environ.get("PATH_INFO", "")
        method = environ.get("REQUEST_METHOD", "GET").upper()

        if path == SUBMISSION_PATH:
            if method == "OPTIONS":
                # Answered before authentication, deliberately: a browser does
                # not present `Authorization` on a preflight, so requiring it
                # would make the check unpassable and the workflow unreachable.
                return self._preflight(environ)
            if method != "POST":
                return _Response(
                    405,
                    _error("method_not_allowed", "This endpoint accepts POST only."),
                )
            return _Response(*self._submit(environ))

        preview_match = _PREVIEW_PATH.match(path)
        if preview_match is not None:
            if method != "GET":
                return _Response(
                    405,
                    _error("method_not_allowed", "This endpoint accepts GET only."),
                )
            return _Response(
                *self._preview_snapshot(environ, preview_match.group(1).lower())
            )

        return _Response(404, _error("not_found", "No such endpoint."))

    # -- preflight ------------------------------------------------------------

    def _preflight(self, environ: Mapping[str, Any]) -> _Response:
        """Answer one bounded `OPTIONS` for the submission route.

        Reaches no application service, authenticates nothing and stores
        nothing. A refusal carries no permission header, which is what makes the
        browser refuse the POST on the caller's own machine.
        """
        decision = self._cors.preflight(
            origin=origin_of(environ),
            requested_method=environ.get("HTTP_ACCESS_CONTROL_REQUEST_METHOD"),
            requested_headers=environ.get("HTTP_ACCESS_CONTROL_REQUEST_HEADERS"),
        )
        if isinstance(decision, PreflightAllowed):
            return _Response(204, None, decision.headers)
        return _Response(403, _error(decision.code, decision.message))

    # -- submission -----------------------------------------------------------

    def _submit(self, environ: Mapping[str, Any]) -> tuple[int, dict[str, Any]]:
        try:
            principal = self._credentials.authenticate(
                parse_bearer(environ.get("HTTP_AUTHORIZATION"))
            )
        except AuthenticationFailed as failure:
            # Deliberately not audited. Writing an append-only row per rejected
            # credential would let an unauthenticated caller append to permanent
            # history at will.
            return 401, _error("unauthenticated", str(failure))

        media_type = (environ.get("CONTENT_TYPE") or "").split(";")[0].strip().lower()
        if media_type != _JSON_MEDIA_TYPE:
            return 415, _error(
                "unsupported_media_type",
                f"The snapshot bundle must be sent as {_JSON_MEDIA_TYPE}.",
            )

        request_key = (environ.get("HTTP_IDEMPOTENCY_KEY") or "").strip()
        if not request_key:
            return 400, _error(
                "missing_idempotency_key",
                "An Idempotency-Key header is required, so that a retry returns "
                "the original receipt instead of submitting twice.",
            )
        claimed = (environ.get("HTTP_X_SNAPSHOT_SHA256") or "").strip() or None

        limit = self._submissions.max_bytes
        declared = environ.get("CONTENT_LENGTH")
        if declared is None or not str(declared).strip():
            # A chunked body has no declared length, and this endpoint refuses
            # to start reading one: the size bound has to be checkable before
            # the first byte is buffered, not discovered part-way through.
            return 411, _error(
                "length_required",
                "A Content-Length header is required. Chunked bodies are not "
                "accepted, because the size bound must hold before anything is "
                "read.",
            )
        try:
            length = int(str(declared).strip())
        except ValueError:
            return 400, _error(
                "malformed_length", "The Content-Length header is not a number."
            )
        if length < 0:
            return 400, _error(
                "malformed_length", "The Content-Length header is negative."
            )
        if length > limit:
            return 413, _error(
                "artifact_too_large",
                f"The bundle is {length} bytes, over the {limit}-byte limit. It "
                "was not read.",
            )

        # **Exactly** `length` bytes, never one more.
        #
        # PEP 3333: an application "should not attempt to read more data than is
        # specified by the CONTENT_LENGTH variable". A server *may* hand over a
        # bounded stream, and many do — but `wsgiref.simple_server` hands over
        # the raw socket, where a read for one byte past the body blocks until
        # the peer sends something or the connection dies. An earlier revision
        # read `length + 1` in order to detect an over-long body; it passed every
        # test, because `io.BytesIO` returns a short read at end of file, and
        # then hung the first real request against the rehearsal server.
        #
        # Detecting an over-long body is therefore not the application's job and
        # cannot be: framing belongs to the server and the proxy, both of which
        # treat trailing bytes as the start of the next request on the connection
        # and reject them. What the application still detects is the opposite
        # case — a body that ends early — because a truncated document would hash
        # to something neither end recognises.
        stream = environ.get("wsgi.input")
        data = _read_exactly(stream, length)
        if len(data) < length:
            return 400, _error(
                "incomplete_body",
                # Refused before the application service is called at all, so
                # this one could truthfully be specific about the store. It is
                # not, because the only thing the caller can act on is that the
                # submission did not happen and should be repeated.
                "The body ended before its declared Content-Length. No "
                "submission was recorded; submit again.",
            )

        try:
            receipt = self._submissions.submit(
                data,
                principal=principal,
                request_key=request_key,
                claimed_checksum=claimed,
            )
        except NotAuthorizedError as refusal:
            return 403, _error(refusal.code, str(refusal))
        except SubmissionRefused as refusal:
            status = _REFUSAL_STATUS.get(refusal.code, 400)
            payload = _error(refusal.code, str(refusal))
            if refusal.artifact_code is not None:
                payload["error"]["artifact_code"] = refusal.artifact_code
            return status, payload
        except (PersistenceError, UniquenessConflict) as error:
            log_expected_failure(logger, "database_unavailable", error)
            return 503, _error(
                "database_unavailable",
                # Review finding I-1. The artifact is written before the
                # transaction commits, on purpose, so this path cannot say the
                # filesystem is unchanged — only that nothing was recorded or
                # confirmed, which is the part the caller can act on.
                "The submission could not be recorded or confirmed. Retry with "
                "the same Idempotency-Key: a retry cannot create a second "
                "snapshot.",
            )

        # 200 for a duplicate rather than 201: nothing was created by this
        # request, and a client that treats 201 as "new" would be misled.
        return (200 if receipt.duplicate else 201), receipt.as_payload()

    # -- preview --------------------------------------------------------------

    def _preview_snapshot(
        self, environ: Mapping[str, Any], checksum: str
    ) -> tuple[int, dict[str, Any]]:
        if self._preview is None or self._preview_user_resolver is None:
            return 503, _error(
                "authentication_unavailable",
                "Snapshot preview requires the Discord-authenticated web "
                "boundary, which this deployment does not have yet. The "
                "submitted snapshot is unaffected and remains pending.",
            )
        try:
            discord_user_id = self._preview_user_resolver(environ)
        except AuthenticationFailed as failure:
            return 401, _error("unauthenticated", str(failure))

        query = parse_qs(environ.get("QUERY_STRING", ""))
        folder_id = (query.get("folder") or [None])[0]
        request_key = (query.get("request_key") or [f"preview:{checksum}"])[0]

        try:
            view = self._preview.preview(
                checksum,
                discord_user_id=discord_user_id,
                request_key=request_key,
                folder_id=folder_id,
            )
        except NotAuthorizedError as refusal:
            return 403, _error(refusal.code, str(refusal))
        except PreviewUnavailable as refusal:
            return _PREVIEW_STATUS.get(refusal.code, 400), _error(
                refusal.code, str(refusal)
            )
        except ImportRefused as refusal:
            return 409, _error(refusal.code, str(refusal))
        except (PersistenceError, UniquenessConflict) as error:
            log_expected_failure(logger, "database_unavailable", error)
            return 503, _error(
                "database_unavailable",
                "The preview could not be produced. Nothing was changed.",
            )
        return 200, view.as_payload()


_STATUS_TEXT = {
    200: "OK",
    201: "Created",
    204: "No Content",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    409: "Conflict",
    411: "Length Required",
    413: "Payload Too Large",
    415: "Unsupported Media Type",
    500: "Internal Server Error",
    503: "Service Unavailable",
}


#: How much of the body is pulled per read. Bounded so a large declared length
#: is not one enormous allocation before a single byte has arrived.
_READ_CHUNK = 256 * 1024


def _read_exactly(stream: Any, length: int) -> bytes:
    """Read up to `length` bytes, and never request more than that in total.

    Returns short when the stream ends early, which is what lets the caller
    report `incomplete_body`. It never over-reads, so it cannot block against a
    server that hands over an unbounded stream — see the note at the call site.
    """
    if stream is None or length == 0:
        return b""
    chunks: list[bytes] = []
    remaining = length
    while remaining > 0:
        chunk = stream.read(min(remaining, _READ_CHUNK))
        if not chunk:
            break
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def _status_line(status: int) -> str:
    return f"{status} {_STATUS_TEXT[status]}"


def _error(code: str, message: str) -> dict[str, Any]:
    """The one error shape. A code to branch on, a sentence to show a human."""
    return {"error": {"code": code, "message": message}}
