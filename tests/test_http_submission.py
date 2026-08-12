"""The HTTP boundary: credentials, limits, safe errors and the preview gate.

The WSGI application is called directly rather than through a socket. A socket
would add a server's behaviour to every assertion without testing anything this
repository owns; `wsgiref.validate` is used instead, so the responses are proven
to be well-formed WSGI rather than merely accepted by one client.
"""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path

import pytest
from wsgiref.validate import validator

from adapters.artifacts.filesystem import FilesystemArtifactStore
from adapters.http.cors import (
    ALLOWED_ORIGINS_VARIABLE,
    ALLOWED_REQUEST_HEADERS,
    CorsConfigurationError,
    CorsPolicy,
)
from adapters.http.credentials import (
    MIN_SECRET_LENGTH,
    PRINCIPALS_VARIABLE,
    AuthenticationFailed,
    CredentialError,
    ServicePrincipalRegistry,
    secret_digest,
)
from adapters.http.wsgi import SUBMISSION_PATH, SnapshotSubmissionApplication
from application.authorization import AuthorizationContext
from application.errors import PersistenceError
from application.foundry.import_service import SnapshotImportService
from application.foundry.preview_service import SnapshotPreviewService
from application.foundry.submission import SnapshotSubmissionService
from domain.foundry import OBSERVED_DEPLOYMENT
from domain.foundry_profile import PROFILE
from tests import foundry_fixtures as fx
from tests.fakes import FakeAuthorization, FakeStore, admit, unit_of_work_factory

SECRET = "s" * MIN_SECRET_LENGTH
PRINCIPAL_ID = "foundry-the-guild"
CREDENTIAL = f"{PRINCIPAL_ID}.{SECRET}"
COUNCIL_USER = 4200000000000000001
ORDINARY_USER = 4200000000000000002


def environment(digest: str | None = None) -> dict[str, str]:
    return {
        PRINCIPALS_VARIABLE: (
            f"{PRINCIPAL_ID}|foundry:snapshot:submit|{digest or secret_digest(SECRET)}"
        )
    }


@pytest.fixture()
def store() -> FakeStore:
    store = FakeStore()
    admit(store, PRINCIPAL_ID)
    return store


@pytest.fixture()
def artifacts(tmp_path: Path) -> FilesystemArtifactStore:
    store = FilesystemArtifactStore(tmp_path / "artifacts")
    yield store
    store.close()


@pytest.fixture()
def application(store, artifacts) -> SnapshotSubmissionApplication:
    submissions = SnapshotSubmissionService(
        unit_of_work_factory(store),
        deployment=OBSERVED_DEPLOYMENT,
        artifacts=artifacts,
    )
    return SnapshotSubmissionApplication(
        submissions, ServicePrincipalRegistry.from_mapping(environment())
    )


def call(
    application,
    *,
    method: str = "POST",
    path: str = SUBMISSION_PATH,
    body: bytes = b"",
    headers: dict[str, str] | None = None,
    query: str = "",
    content_length: str | None = None,
    content_type: str | None = "application/json",
    validate: bool = True,
    stream=None,
):
    """Invoke the application through `wsgiref.validate`.

    `validate=False` is for the handful of cases where the *request* is
    deliberately malformed in a way `wsgiref.validate` refuses to pass on. A
    real server can and does hand such values through, so the application still
    has to cope; the validator is checking this repository's responses, not
    standing in for the server's own input checks.
    """
    environ = {
        "REQUEST_METHOD": method,
        "SCRIPT_NAME": "",
        "PATH_INFO": path,
        "QUERY_STRING": query,
        "SERVER_NAME": "freedom.example",
        "SERVER_PORT": "443",
        "SERVER_PROTOCOL": "HTTP/1.1",
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": "https",
        "wsgi.input": stream if stream is not None else io.BytesIO(body),
        "wsgi.errors": io.StringIO(),
        "wsgi.multithread": False,
        "wsgi.multiprocess": False,
        "wsgi.run_once": False,
    }
    if content_type is not None:
        environ["CONTENT_TYPE"] = content_type
    length = content_length if content_length is not None else str(len(body))
    if length != "":
        environ["CONTENT_LENGTH"] = length
    for key, value in (headers or {}).items():
        environ[f"HTTP_{key.upper().replace('-', '_')}"] = value

    captured: dict[str, object] = {}

    def start_response(status, response_headers, exc_info=None):
        captured["status"] = int(status.split(" ")[0])
        captured["headers"] = dict(response_headers)
        return lambda data: None

    target = validator(application) if validate else application
    result = target(environ, start_response)
    try:
        chunks = list(result)
    finally:
        close = getattr(result, "close", None)
        if close is not None:
            close()
    body_bytes = b"".join(chunks)
    # A `204` preflight is genuinely body-less, so there is nothing to decode.
    payload = json.loads(body_bytes.decode("utf-8")) if body_bytes else None
    return captured["status"], captured["headers"], payload


def submit(application, body: bytes, **kwargs):
    headers = {
        "Authorization": f"Bearer {CREDENTIAL}",
        "Idempotency-Key": "foundry-module:key",
        "X-Snapshot-SHA256": hashlib.sha256(body).hexdigest(),
    }
    headers.update(kwargs.pop("headers", {}))
    return call(application, body=body, headers=headers, **kwargs)


# -- the happy path -----------------------------------------------------------


def test_an_authenticated_valid_submission_returns_a_bounded_receipt(application):
    body = fx.encode(fx.bundle())

    status, headers, payload = submit(application, body)

    assert status == 201
    assert payload["status"] == "pending"
    assert payload["checksum"] == hashlib.sha256(body).hexdigest()
    assert payload["actor_count"] == 1
    assert payload["duplicate"] is False
    assert "Testcharacter" not in json.dumps(payload)
    assert "abilities" not in json.dumps(payload)


def test_safe_headers_are_present_on_every_response(application):
    _, headers, _ = submit(application, fx.encode(fx.bundle()))

    assert headers["Content-Type"] == "application/json; charset=utf-8"
    assert headers["Cache-Control"] == "no-store"
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["Referrer-Policy"] == "no-referrer"
    # No `Origin` was sent, so there is nothing to permit. See the CORS section
    # below for what happens when a browser does send one.
    assert "Access-Control-Allow-Origin" not in headers


def test_a_retry_returns_the_original_receipt_with_status_200(application):
    body = fx.encode(fx.bundle())
    _, _, first = submit(application, body)
    status, _, second = submit(application, body)

    assert status == 200
    assert second["duplicate"] is True
    assert second["snapshot_id"] == first["snapshot_id"]
    assert second["correlation_id"] == first["correlation_id"]


def test_the_same_key_with_different_bytes_conflicts(application):
    submit(application, fx.encode(fx.bundle()))
    other = fx.encode(fx.bundle(actors=(fx.actor(fx.SECOND_ACTOR_ID),)))

    status, _, payload = submit(application, other)

    assert status == 409
    assert payload["error"]["code"] == "request_key_conflict"


def test_the_same_bytes_under_another_key_deduplicates_storage(
    application, store, artifacts
):
    body = fx.encode(fx.bundle())
    submit(application, body, headers={"Idempotency-Key": "key-a"})
    status, _, payload = submit(application, body, headers={"Idempotency-Key": "key-b"})

    assert status == 200
    assert payload["duplicate"] is True
    assert len(store.snapshots) == 1
    assert len(list(artifacts.root.glob("*.json"))) == 1


# -- authentication and authorization ----------------------------------------


@pytest.mark.parametrize(
    "header",
    [
        None,
        "",
        "Bearer",
        "Bearer ",
        "Basic abc",
        f"Bearer nosuchprincipal.{SECRET}",
        f"Bearer {PRINCIPAL_ID}.wrongsecretwrongsecretwrongsecret",
        f"Bearer {PRINCIPAL_ID}",
        f"Bearer .{SECRET}",
    ],
)
def test_a_missing_or_wrong_credential_is_401_and_stores_nothing(
    application, store, header
):
    headers = {"Idempotency-Key": "k", "X-Snapshot-SHA256": "a" * 64}
    if header is not None:
        headers["Authorization"] = header

    status, response_headers, payload = call(
        application, body=fx.encode(fx.bundle()), headers=headers
    )

    assert status == 401
    assert payload["error"]["code"] == "unauthenticated"
    assert response_headers["WWW-Authenticate"].startswith("Bearer")
    assert store.snapshots == {}


def test_every_authentication_failure_gives_the_same_message(application):
    messages = set()
    for header in (
        f"Bearer nosuchprincipal.{SECRET}",
        f"Bearer {PRINCIPAL_ID}.{'w' * MIN_SECRET_LENGTH}",
        "Bearer malformed",
    ):
        _, _, payload = call(
            application,
            body=fx.encode(fx.bundle()),
            headers={
                "Authorization": header,
                "Idempotency-Key": "k",
            },
        )
        messages.add(payload["error"]["message"])
    assert len(messages) == 1


def test_a_short_secret_cannot_authenticate_even_if_it_is_configured(store, artifacts):
    short = "x" * (MIN_SECRET_LENGTH - 1)
    registry = ServicePrincipalRegistry.from_mapping(
        {
            PRINCIPALS_VARIABLE: (
                f"{PRINCIPAL_ID}|foundry:snapshot:submit|"
                f"{hashlib.sha256(short.encode()).hexdigest()}"
            )
        }
    )
    with pytest.raises(AuthenticationFailed):
        registry.authenticate(f"{PRINCIPAL_ID}.{short}")


def test_no_configured_principal_means_every_request_is_unauthenticated(
    store, artifacts
):
    submissions = SnapshotSubmissionService(
        unit_of_work_factory(store),
        deployment=OBSERVED_DEPLOYMENT,
        artifacts=artifacts,
    )
    empty = SnapshotSubmissionApplication(
        submissions, ServicePrincipalRegistry.from_mapping({})
    )

    status, _, payload = submit(empty, fx.encode(fx.bundle()))

    assert status == 401
    assert payload["error"]["code"] == "unauthenticated"


def test_a_revoked_principal_stops_working_after_a_reload(store, artifacts):
    """Revocation is a configuration change plus a reload, and it takes effect."""
    submissions = SnapshotSubmissionService(
        unit_of_work_factory(store),
        deployment=OBSERVED_DEPLOYMENT,
        artifacts=artifacts,
    )
    live = SnapshotSubmissionApplication(
        submissions, ServicePrincipalRegistry.from_mapping(environment())
    )
    assert submit(live, fx.encode(fx.bundle()))[0] == 201

    revoked = SnapshotSubmissionApplication(
        submissions, ServicePrincipalRegistry.from_mapping({PRINCIPALS_VARIABLE: ""})
    )
    assert submit(revoked, fx.encode(fx.bundle()))[0] == 401


def test_a_principal_configured_without_the_submit_scope_is_forbidden(store, artifacts):
    """There is no other scope yet, so an empty scope list is a configuration error."""
    with pytest.raises(CredentialError):
        ServicePrincipalRegistry.from_mapping(
            {PRINCIPALS_VARIABLE: f"{PRINCIPAL_ID}||{secret_digest(SECRET)}"}
        )


@pytest.mark.parametrize(
    "entry",
    [
        "no-separators",
        "id|foundry:snapshot:submit|not-a-digest",
        "id|nosuchscope|" + "a" * 64,
        "UPPERCASE|foundry:snapshot:submit|" + "a" * 64,
        "id|foundry:snapshot:submit|" + "a" * 63,
    ],
)
def test_malformed_configuration_is_refused_at_startup(entry):
    with pytest.raises(CredentialError):
        ServicePrincipalRegistry.from_mapping({PRINCIPALS_VARIABLE: entry})


def test_a_duplicate_principal_id_is_refused(store):
    entry = f"{PRINCIPAL_ID}|foundry:snapshot:submit|{secret_digest(SECRET)}"
    with pytest.raises(CredentialError, match="more than once"):
        ServicePrincipalRegistry.from_mapping(
            {PRINCIPALS_VARIABLE: f"{entry};{entry}"}
        )


def test_the_configured_secret_is_a_digest_and_the_secret_is_not_stored():
    entry = f"{PRINCIPAL_ID}|foundry:snapshot:submit|{secret_digest(SECRET)}"
    assert SECRET not in entry
    registry = ServicePrincipalRegistry.from_mapping({PRINCIPALS_VARIABLE: entry})
    assert SECRET not in repr(registry.__dict__ if hasattr(registry, "__dict__") else "")


def test_secret_digest_refuses_a_short_secret():
    with pytest.raises(CredentialError):
        secret_digest("short")


# -- request shape ------------------------------------------------------------


def test_a_wrong_method_is_refused(application):
    status, _, payload = call(application, method="GET", body=b"")
    assert status == 405
    assert payload["error"]["code"] == "method_not_allowed"


def test_an_unknown_path_is_404(application):
    status, _, payload = call(application, path="/api/v1/other")
    assert status == 404


def test_a_wrong_content_type_is_refused_before_the_body_is_read(application, store):
    status, _, payload = submit(
        application, fx.encode(fx.bundle()), content_type="text/plain"
    )
    assert status == 415
    assert payload["error"]["code"] == "unsupported_media_type"
    assert store.snapshots == {}


def test_a_charset_parameter_on_the_content_type_is_accepted(application):
    status, _, _ = submit(
        application,
        fx.encode(fx.bundle()),
        content_type="application/json; charset=utf-8",
    )
    assert status == 201


def test_a_missing_idempotency_key_is_refused(application):
    status, _, payload = call(
        application,
        body=fx.encode(fx.bundle()),
        headers={"Authorization": f"Bearer {CREDENTIAL}"},
    )
    assert status == 400
    assert payload["error"]["code"] == "missing_idempotency_key"


def test_a_body_without_a_declared_length_is_refused(application):
    status, _, payload = submit(
        application, fx.encode(fx.bundle()), content_length=""
    )
    assert status == 411
    assert payload["error"]["code"] == "length_required"


@pytest.mark.parametrize("declared", ["abc", "-1"])
def test_a_malformed_length_is_refused(application, declared):
    # `validate=False`: `wsgiref.validate` refuses to pass a malformed
    # CONTENT_LENGTH through at all, and the point of the test is that the
    # application copes if a real server does.
    status, _, payload = submit(
        application,
        fx.encode(fx.bundle()),
        content_length=declared,
        validate=False,
    )
    assert status == 400
    assert payload["error"]["code"] == "malformed_length"


def test_an_oversized_declared_length_is_refused_without_reading_the_body(
    store, artifacts
):
    from application.foundry.artifact import IngestionLimits

    submissions = SnapshotSubmissionService(
        unit_of_work_factory(store),
        deployment=OBSERVED_DEPLOYMENT,
        artifacts=artifacts,
        ingestion_limits=IngestionLimits(max_bytes=64),
    )
    small = SnapshotSubmissionApplication(
        submissions, ServicePrincipalRegistry.from_mapping(environment())
    )

    status, _, payload = submit(small, fx.encode(fx.bundle()))

    assert status == 413
    assert payload["error"]["code"] == "artifact_too_large"
    assert store.snapshots == {}


def test_a_truncated_body_is_refused_rather_than_hashed(application, store):
    body = fx.encode(fx.bundle())
    status, _, payload = submit(
        application, body, content_length=str(len(body) + 10)
    )
    assert status == 400
    assert payload["error"]["code"] == "incomplete_body"
    assert store.snapshots == {}


class _UnboundedInput:
    """`wsgi.input` as a real server hands it over: the raw socket.

    `wsgiref.simple_server` supplies exactly this — a stream that blocks rather
    than returning short when asked for more than the body holds. PEP 3333
    permits it, so an application that reads past `CONTENT_LENGTH` deadlocks
    against it. A `BytesIO` cannot show that, which is why this double exists:
    an over-read raises here instead of hanging the suite.
    """

    def __init__(self, data: bytes) -> None:
        self._data = data
        self._position = 0
        self.requested = 0

    def read(self, size: int = -1) -> bytes:
        if size < 0:
            raise AssertionError(
                "The application must never read wsgi.input without a bound."
            )
        self.requested += size
        if self.requested > len(self._data):
            raise AssertionError(
                f"The application asked for {self.requested} bytes of a "
                f"{len(self._data)}-byte body. PEP 3333 forbids reading past "
                "CONTENT_LENGTH, and against a real socket this call would "
                "block until the connection died."
            )
        chunk = self._data[self._position : self._position + size]
        self._position += len(chunk)
        return chunk


def test_the_body_is_never_read_past_its_declared_length(application):
    """The regression: reading one byte past CONTENT_LENGTH hangs a real server.

    An earlier revision read `length + 1` to detect an over-long body. Every
    `BytesIO`-backed test passed, and the first request against the rehearsal
    server blocked until it was killed.
    """
    body = fx.encode(fx.bundle())
    stream = _UnboundedInput(body)

    status, _, payload = submit(application, body, stream=stream, validate=False)

    assert status == 201
    assert stream.requested <= len(body)


def test_an_over_long_body_is_the_server_s_framing_problem_not_the_application_s(
    application, store
):
    """The application reads its declared length and no more.

    Trailing bytes are the next request on the connection as far as the server
    and the proxy are concerned, and both reject them. The application cannot
    detect the case without committing the over-read that this package's
    regression was caused by, so it deliberately does not try — it processes
    exactly the bytes that were declared.
    """
    body = fx.encode(fx.bundle())
    status, _, payload = call(
        application,
        body=body + b"trailing",
        content_length=str(len(body)),
        headers={
            "Authorization": f"Bearer {CREDENTIAL}",
            "Idempotency-Key": "k",
            # The digest of the *declared* body, which is what the server reads.
            "X-Snapshot-SHA256": hashlib.sha256(body).hexdigest(),
        },
    )

    assert status == 201
    assert payload["checksum"] == hashlib.sha256(body).hexdigest()


def test_trailing_bytes_still_cannot_forge_a_checksum(application, store):
    """The declared prefix is hashed, so a claim about the whole body fails."""
    body = fx.encode(fx.bundle())
    status, _, payload = call(
        application,
        body=body + b"trailing",
        content_length=str(len(body)),
        headers={
            "Authorization": f"Bearer {CREDENTIAL}",
            "Idempotency-Key": "k",
            "X-Snapshot-SHA256": hashlib.sha256(body + b"trailing").hexdigest(),
        },
    )

    assert status == 400
    assert payload["error"]["code"] == "checksum_mismatch"
    assert store.snapshots == {}


def test_an_empty_body_is_refused(application, store):
    status, _, payload = submit(application, b"")
    assert status == 400
    assert payload["error"]["code"] == "artifact_rejected"
    assert store.snapshots == {}


def test_a_claimed_checksum_mismatch_is_refused(application, store):
    body = fx.encode(fx.bundle())
    status, _, payload = call(
        application,
        body=body,
        headers={
            "Authorization": f"Bearer {CREDENTIAL}",
            "Idempotency-Key": "k",
            "X-Snapshot-SHA256": "f" * 64,
        },
    )
    assert status == 400
    assert payload["error"]["code"] == "checksum_mismatch"
    assert store.snapshots == {}


def test_a_malformed_bundle_reports_the_artifact_code(application):
    status, _, payload = submit(application, b'{"not":"a bundle"}\n')
    assert status == 400
    assert payload["error"]["code"] == "artifact_rejected"
    assert payload["error"]["artifact_code"] == "missing_top_level_key"


# -- error safety -------------------------------------------------------------


def test_an_error_body_carries_no_secret_path_sql_or_actor_value(application):
    status, _, payload = submit(application, b"{not json")
    rendered = json.dumps(payload)

    assert SECRET not in rendered
    assert CREDENTIAL not in rendered
    assert "/opt/" not in rendered
    assert "Traceback" not in rendered
    assert "SELECT" not in rendered


def test_a_database_failure_says_what_it_knows_and_no_more(store, artifacts):
    """Review finding I-1. The artifact is written before the transaction
    commits, deliberately, so this path cannot assert that the filesystem is
    unchanged — only that nothing was recorded and that a retry is safe."""

    class Failing(SnapshotSubmissionService):
        def submit(self, *args, **kwargs):
            raise PersistenceError("injected")

    application = SnapshotSubmissionApplication(
        Failing(
            unit_of_work_factory(store),
            deployment=OBSERVED_DEPLOYMENT,
            artifacts=artifacts,
        ),
        ServicePrincipalRegistry.from_mapping(environment()),
    )

    status, _, payload = submit(application, fx.encode(fx.bundle()))

    assert status == 503
    assert payload["error"]["code"] == "database_unavailable"
    message = payload["error"]["message"]
    assert "nothing was stored" not in message.lower()
    assert "recorded or confirmed" in message
    assert "Idempotency-Key" in message


def test_an_unexpected_exception_makes_no_claim_about_the_filesystem(
    store, artifacts
):
    class Exploding(SnapshotSubmissionService):
        def submit(self, *args, **kwargs):
            raise RuntimeError("injected")

    application = SnapshotSubmissionApplication(
        Exploding(
            unit_of_work_factory(store),
            deployment=OBSERVED_DEPLOYMENT,
            artifacts=artifacts,
        ),
        ServicePrincipalRegistry.from_mapping(environment()),
    )

    _, _, payload = submit(application, fx.encode(fx.bundle()))

    message = payload["error"]["message"]
    assert "nothing was stored" not in message.lower()
    assert "recorded or confirmed" in message


def test_every_refusal_reaches_the_wire_with_its_wording_intact(store, artifacts):
    """The adapter renders `str(refusal)`, so a truthful application message can
    still be lost if a boundary rewrites it. It does not: this drives real
    refusals through a real request and checks the *body* the Foundry module
    would parse (review finding I-1).
    """
    application = SnapshotSubmissionApplication(
        SnapshotSubmissionService(
            unit_of_work_factory(store),
            deployment=OBSERVED_DEPLOYMENT,
            artifacts=artifacts,
        ),
        ServicePrincipalRegistry.from_mapping(environment()),
    )
    data = fx.encode(fx.bundle())
    other = fx.encode(fx.bundle(actors=(fx.actor(fx.SECOND_ACTOR_ID),)))

    # A spent key, reused for different bytes: raised from `_replay`, which is
    # reachable both before and after the store has run.
    submit(application, data, headers={"Idempotency-Key": "spent"})
    status, _, conflict = submit(
        application, other, headers={"Idempotency-Key": "spent"}
    )

    assert status == 409
    assert conflict["error"]["code"] == "request_key_conflict"
    message = conflict["error"]["message"]
    assert "nothing was stored" not in message.lower()
    assert "This attempt recorded nothing" in message
    assert "earlier submission's record is unchanged" in message

    # A claimed digest that disagrees: refused before the store, and allowed to
    # say so specifically rather than broadly.
    status, _, mismatch = submit(
        application,
        data,
        headers={"Idempotency-Key": "fresh", "X-Snapshot-SHA256": "0" * 64},
    )
    assert status == 400
    assert "nothing was stored" not in mismatch["error"]["message"].lower()
    assert (
        "artifact store was never asked to hold these bytes"
        in mismatch["error"]["message"]
    )


def test_an_unconfirmed_durability_refusal_reaches_the_wire_truthfully(
    store, artifacts, monkeypatch
):
    """The 503 a Foundry client actually receives when publication created the
    checksum entry and the directory `fsync` could not be acknowledged. The file
    is demonstrably present while the response is being rendered."""
    import os
    import stat as stat_module

    application = SnapshotSubmissionApplication(
        SnapshotSubmissionService(
            unit_of_work_factory(store),
            deployment=OBSERVED_DEPLOYMENT,
            artifacts=artifacts,
        ),
        ServicePrincipalRegistry.from_mapping(environment()),
    )
    data = fx.encode(fx.bundle())
    real = os.fsync

    def refuse_directories(descriptor: int) -> None:
        if stat_module.S_ISDIR(os.fstat(descriptor).st_mode):
            raise OSError(5, "injected")
        real(descriptor)

    monkeypatch.setattr(os, "fsync", refuse_directories)

    status, _, payload = submit(application, data)

    assert status == 503
    assert payload["error"]["code"] == "storage_unavailable"
    message = payload["error"]["message"]
    assert "nothing was stored" not in message.lower()
    assert "nothing was recorded" in message
    assert "cannot create a second snapshot" in message
    # The claim the old wording denied.
    assert len(list(artifacts.root.glob("*.json"))) == 1


def test_an_unexpected_exception_becomes_a_plain_500(store, artifacts, caplog):
    class Exploding(SnapshotSubmissionService):
        def submit(self, *args, **kwargs):
            raise RuntimeError("secret detail /srv/freedom/snapshots/x.json")

    submissions = Exploding(
        unit_of_work_factory(store),
        deployment=OBSERVED_DEPLOYMENT,
        artifacts=artifacts,
    )
    application = SnapshotSubmissionApplication(
        submissions, ServicePrincipalRegistry.from_mapping(environment())
    )

    status, _, payload = submit(application, fx.encode(fx.bundle()))

    assert status == 500
    assert payload["error"]["code"] == "internal_error"
    assert "/srv/freedom" not in json.dumps(payload)
    assert "secret detail" not in caplog.text


# -- browser CORS -------------------------------------------------------------
#
# Review findings B-1 and S-I-1. The module submits from a browser with four
# non-safelisted headers, so the browser sends an unauthenticated `OPTIONS`
# preflight and refuses to send the POST unless it is answered. `curl` cannot
# show any of this — it does not enforce CORS — so these tests reproduce the
# preflight the browser actually performs, and the real-browser-origin check is
# recorded as a maintainer-supervised step in the operations document.


ALLOWED_ORIGIN = "https://foundry1.example.org"
OTHER_ORIGIN = "https://evil.example"

#: The exact header set `foundry-module/scripts/transport.js` sends, in the
#: lower-case comma-separated form a browser puts in the preflight.
REQUESTED_HEADERS = "authorization,content-type,idempotency-key,x-snapshot-sha256"


@pytest.fixture()
def browser_application(store, artifacts) -> SnapshotSubmissionApplication:
    """A composition with one trusted browser origin configured."""
    submissions = SnapshotSubmissionService(
        unit_of_work_factory(store),
        deployment=OBSERVED_DEPLOYMENT,
        artifacts=artifacts,
    )
    return SnapshotSubmissionApplication(
        submissions,
        ServicePrincipalRegistry.from_mapping(environment()),
        cors=CorsPolicy.from_mapping({ALLOWED_ORIGINS_VARIABLE: ALLOWED_ORIGIN}),
    )


def preflight(
    application,
    *,
    origin: str | None = ALLOWED_ORIGIN,
    method: str = "POST",
    headers: str | None = REQUESTED_HEADERS,
):
    request_headers: dict[str, str] = {}
    if origin is not None:
        request_headers["Origin"] = origin
    if method is not None:
        request_headers["Access-Control-Request-Method"] = method
    if headers is not None:
        request_headers["Access-Control-Request-Headers"] = headers
    return call(
        application,
        method="OPTIONS",
        headers=request_headers,
        content_type=None,
        content_length="",
    )


def test_an_allowed_preflight_succeeds_and_permits_exactly_what_is_needed(
    browser_application,
):
    status, headers, _ = preflight(browser_application)

    assert status == 204
    assert headers["Access-Control-Allow-Origin"] == ALLOWED_ORIGIN
    assert headers["Access-Control-Allow-Methods"] == "POST"
    permitted = {
        name.strip() for name in headers["Access-Control-Allow-Headers"].split(",")
    }
    assert permitted == set(ALLOWED_REQUEST_HEADERS)
    assert int(headers["Access-Control-Max-Age"]) > 0
    # No cookie authority is granted, ever.
    assert "Access-Control-Allow-Credentials" not in headers
    # A 204 declares no media type for content it does not have.
    assert "Content-Type" not in headers


def test_the_preflight_needs_no_credential(browser_application):
    """A browser does not put `Authorization` on a preflight, so requiring it
    would make the supported workflow unreachable."""
    status, headers, _ = preflight(browser_application)

    assert status == 204
    assert "WWW-Authenticate" not in headers


def test_an_unlisted_origin_gets_no_permission(browser_application):
    status, headers, payload = preflight(browser_application, origin=OTHER_ORIGIN)

    assert status == 403
    assert payload["error"]["code"] == "origin_not_allowed"
    assert "Access-Control-Allow-Origin" not in headers


@pytest.mark.parametrize(
    "origin",
    [
        "null",
        "",
        "https://foundry1.example.org.evil.example",
        "https://foundry1.example.org:8443",
        "http://foundry1.example.org",
        "https://Foundry1.Example.Org/",
        "not an origin",
        "*",
    ],
)
def test_a_malformed_or_near_miss_origin_is_refused(browser_application, origin):
    """Exact match only: no suffix, no scheme swap, no port drift, no wildcard.

    `https://Foundry1.Example.Org/` is included deliberately. A browser never
    sends that form — it lower-cases the host and omits the path — so accepting
    it would mean the comparison had been loosened rather than the case handled.
    """
    status, headers, _ = preflight(browser_application, origin=origin)

    assert status == 403
    assert "Access-Control-Allow-Origin" not in headers


def test_a_preflight_for_the_wrong_method_is_refused(browser_application):
    status, headers, payload = preflight(browser_application, method="DELETE")

    assert status == 403
    assert payload["error"]["code"] == "preflight_method_not_allowed"
    assert "Access-Control-Allow-Origin" not in headers


def test_a_preflight_asking_for_an_extra_header_is_refused(browser_application):
    status, headers, payload = preflight(
        browser_application, headers=f"{REQUESTED_HEADERS},x-forwarded-for"
    )

    assert status == 403
    assert payload["error"]["code"] == "preflight_header_not_allowed"
    assert "Access-Control-Allow-Origin" not in headers


def test_a_preflight_asking_for_fewer_headers_is_allowed(browser_application):
    """A subset is what a browser sends when the caller sends fewer headers."""
    status, _, _ = preflight(browser_application, headers="content-type")
    assert status == 204


def test_a_preflight_header_list_is_matched_case_insensitively(browser_application):
    status, _, _ = preflight(
        browser_application, headers="Authorization, Content-Type, Idempotency-Key"
    )
    assert status == 204


def test_an_allowed_origin_post_succeeds_and_carries_the_permission(
    browser_application,
):
    status, headers, payload = submit(
        browser_application,
        fx.encode(fx.bundle()),
        headers={"Origin": ALLOWED_ORIGIN},
    )

    assert status == 201
    assert payload["status"] == "pending"
    assert headers["Access-Control-Allow-Origin"] == ALLOWED_ORIGIN
    assert "Access-Control-Allow-Credentials" not in headers


@pytest.mark.parametrize(
    ("authorization", "expected_status"),
    [("Bearer wrong.credentialcredentialcredentialcred", 401), (None, 401)],
)
def test_an_allowed_origin_error_response_is_still_readable_by_the_browser(
    browser_application, authorization, expected_status
):
    """A response the browser may not read reaches the module as an opaque
    network failure, which would make "your credential is wrong" and "the server
    is down" the same event."""
    headers = {"Origin": ALLOWED_ORIGIN, "Idempotency-Key": "k"}
    if authorization is not None:
        headers["Authorization"] = authorization

    status, response_headers, payload = call(
        browser_application, body=fx.encode(fx.bundle()), headers=headers
    )

    assert status == expected_status
    assert payload["error"]["code"] == "unauthenticated"
    assert response_headers["Access-Control-Allow-Origin"] == ALLOWED_ORIGIN


def test_an_allowed_origin_refusal_is_still_readable_by_the_browser(
    browser_application,
):
    status, headers, payload = submit(
        browser_application, b'{"not":"a bundle"}\n', headers={"Origin": ALLOWED_ORIGIN}
    )

    assert status == 400
    assert payload["error"]["code"] == "artifact_rejected"
    assert headers["Access-Control-Allow-Origin"] == ALLOWED_ORIGIN


def test_an_unexpected_500_is_still_readable_by_the_browser(store, artifacts):
    class Exploding(SnapshotSubmissionService):
        def submit(self, *args, **kwargs):
            raise RuntimeError("injected")

    application = SnapshotSubmissionApplication(
        Exploding(
            unit_of_work_factory(store),
            deployment=OBSERVED_DEPLOYMENT,
            artifacts=artifacts,
        ),
        ServicePrincipalRegistry.from_mapping(environment()),
        cors=CorsPolicy.from_mapping({ALLOWED_ORIGINS_VARIABLE: ALLOWED_ORIGIN}),
    )

    status, headers, _ = submit(
        application, fx.encode(fx.bundle()), headers={"Origin": ALLOWED_ORIGIN}
    )

    assert status == 500
    assert headers["Access-Control-Allow-Origin"] == ALLOWED_ORIGIN


def test_an_unlisted_origin_post_is_processed_but_gets_no_permission(
    browser_application,
):
    """The server does not refuse it; the *browser* does, on the caller's own
    machine, because no permission header came back. Refusing here as well would
    be a second, weaker access control that a non-browser caller bypasses
    trivially — the bearer credential is the access control."""
    status, headers, _ = submit(
        browser_application, fx.encode(fx.bundle()), headers={"Origin": OTHER_ORIGIN}
    )

    assert status == 201
    assert "Access-Control-Allow-Origin" not in headers


def test_a_non_browser_request_is_untouched_by_any_of_this(browser_application):
    """`curl`, the documented smoke test and the loopback rehearsal send no
    `Origin` and must keep working exactly as before."""
    status, headers, payload = submit(browser_application, fx.encode(fx.bundle()))

    assert status == 201
    assert payload["status"] == "pending"
    assert "Access-Control-Allow-Origin" not in headers


def test_the_default_composition_permits_no_browser_origin(application):
    """Unconfigured is closed, not open."""
    status, headers, payload = preflight(application)

    assert status == 403
    assert payload["error"]["code"] == "origin_not_allowed"
    assert "Access-Control-Allow-Origin" not in headers


def test_vary_names_origin_on_every_submission_response(browser_application):
    """Including the ones carrying no permission: otherwise a shared cache could
    hand an allowed origin the header-less answer stored for another."""
    _, allowed, _ = submit(
        browser_application, fx.encode(fx.bundle()), headers={"Origin": ALLOWED_ORIGIN}
    )
    _, unlisted, _ = submit(
        browser_application,
        fx.encode(fx.bundle()),
        headers={"Origin": OTHER_ORIGIN, "Idempotency-Key": "other"},
    )
    _, none, _ = submit(
        browser_application,
        fx.encode(fx.bundle()),
        headers={"Idempotency-Key": "third"},
    )

    for headers in (allowed, unlisted, none):
        assert "Origin" in headers["Vary"]
        assert "Authorization" in headers["Vary"]


def test_vary_on_a_preflight_names_the_request_headers_too(browser_application):
    _, headers, _ = preflight(browser_application)

    vary = {field.strip() for field in headers["Vary"].split(",")}
    assert vary == {
        "Origin",
        "Authorization",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    }


def test_the_preview_route_gets_no_preflight(browser_application):
    """One CORS surface, for one route. A second is a new decision."""
    status, headers, payload = call(
        browser_application,
        method="OPTIONS",
        path=f"/api/v1/foundry/snapshots/{'a' * 64}/preview",
        headers={
            "Origin": ALLOWED_ORIGIN,
            "Access-Control-Request-Method": "GET",
        },
        content_type=None,
        content_length="",
    )

    assert status == 405
    assert "Access-Control-Allow-Origin" not in headers


def test_a_preflight_reaches_no_application_service(browser_application, store):
    preflight(browser_application)
    assert store.snapshots == {}
    assert store.audit_events == []


# -- over a real socket -------------------------------------------------------


def test_the_preflight_and_the_post_are_well_formed_over_a_real_connection(
    browser_application,
):
    """`wsgiref.validate` proves the response is well-formed WSGI; it does not
    prove a server can put it on a socket. A `204` is where those differ — it
    must carry no body and no `Content-Type`, and a server that disagreed with
    the application about that would hang or frame the next response wrongly.

    The regression this guards is real and this package already had one of its
    shape: an earlier revision passed every `BytesIO`-backed test and then
    blocked the first request against the rehearsal server.

    Still not proof that *browser* CORS works — no client here enforces it. The
    real-browser check is a maintainer-supervised step in
    `docs/operations/foundry-snapshot-submission.md` §8.
    """
    import http.client
    import threading
    from wsgiref.simple_server import WSGIRequestHandler, make_server

    class Quiet(WSGIRequestHandler):
        def log_message(self, format, *args):  # noqa: A002
            pass

    body = fx.encode(fx.bundle())
    with make_server("127.0.0.1", 0, browser_application, handler_class=Quiet) as server:
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", port, timeout=10)

            connection.request(
                "OPTIONS",
                SUBMISSION_PATH,
                headers={
                    "Origin": ALLOWED_ORIGIN,
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": REQUESTED_HEADERS,
                },
            )
            response = connection.getresponse()
            preflight_headers = dict(response.getheaders())
            assert response.status == 204
            assert response.read() == b""
            assert preflight_headers["Access-Control-Allow-Origin"] == ALLOWED_ORIGIN
            assert "Content-Type" not in preflight_headers

            # The same connection: if the 204 had been framed wrongly, this
            # would read the previous response's phantom body instead.
            connection.request(
                "POST",
                SUBMISSION_PATH,
                body=body,
                headers={
                    "Origin": ALLOWED_ORIGIN,
                    "Authorization": f"Bearer {CREDENTIAL}",
                    "Content-Type": "application/json",
                    "Idempotency-Key": "socket-key",
                    "X-Snapshot-SHA256": hashlib.sha256(body).hexdigest(),
                    "Content-Length": str(len(body)),
                },
            )
            response = connection.getresponse()
            payload = json.loads(response.read().decode("utf-8"))
            assert response.status == 201
            assert payload["checksum"] == hashlib.sha256(body).hexdigest()
            assert response.getheader("Access-Control-Allow-Origin") == ALLOWED_ORIGIN
            connection.close()
        finally:
            server.shutdown()
            thread.join(timeout=10)


# -- CORS configuration -------------------------------------------------------


def test_an_absent_origin_allowlist_is_valid_and_empty():
    assert len(CorsPolicy.from_mapping({})) == 0
    assert len(CorsPolicy.from_mapping({ALLOWED_ORIGINS_VARIABLE: "  "})) == 0


def test_configured_origins_are_normalised_to_what_a_browser_sends():
    policy = CorsPolicy.from_mapping(
        {
            ALLOWED_ORIGINS_VARIABLE: (
                "https://Foundry1.Example.Org/, https://foundry2.example.org:443 "
                "https://foundry3.example.org:8443"
            )
        }
    )

    assert policy.origins == (
        "https://foundry1.example.org",
        "https://foundry2.example.org",
        "https://foundry3.example.org:8443",
    )


@pytest.mark.parametrize(
    "value",
    [
        "*",
        "null",
        "https://foundry.example/path",
        "https://foundry.example?q=1",
        "https://foundry.example#f",
        "https://user:pw@foundry.example",
        "http://foundry.example",
        "ftp://foundry.example",
        "foundry.example",
        "https://",
    ],
)
def test_a_malformed_origin_allowlist_is_refused_at_startup(value):
    with pytest.raises(CorsConfigurationError):
        CorsPolicy.from_mapping({ALLOWED_ORIGINS_VARIABLE: value})


def test_loopback_http_is_permitted_for_a_same_host_rehearsal():
    """The same narrow exception `transport.js` makes, and no wider."""
    policy = CorsPolicy.from_mapping(
        {ALLOWED_ORIGINS_VARIABLE: "http://localhost:30001, http://127.0.0.1:30002"}
    )
    assert policy.allows("http://localhost:30001")
    assert policy.allows("http://127.0.0.1:30002")
    assert not policy.allows("http://localhost:30003")


# -- preview ------------------------------------------------------------------


def test_the_preview_route_fails_closed_without_a_phase_3_composition(application):
    status, _, payload = call(
        application,
        method="GET",
        path=f"/api/v1/foundry/snapshots/{'a' * 64}/preview",
        content_type=None,
        content_length="",
    )
    assert status == 503
    assert payload["error"]["code"] == "authentication_unavailable"


def _with_preview(store, artifacts, *, council: int = COUNCIL_USER, caller: int):
    """A composition using a **test** authorization adapter, never a production one."""
    submissions = SnapshotSubmissionService(
        unit_of_work_factory(store),
        deployment=OBSERVED_DEPLOYMENT,
        artifacts=artifacts,
    )
    authorization = FakeAuthorization.with_council(council)
    authorization.grant(
        AuthorizationContext(discord_user_id=ORDINARY_USER, guild_member=True)
    )
    imports = SnapshotImportService(
        unit_of_work_factory(store),
        deployment=OBSERVED_DEPLOYMENT,
        profile=PROFILE,
        authorization=authorization,
    )
    preview = SnapshotPreviewService(
        imports, artifacts=artifacts, authorization=authorization
    )
    application = SnapshotSubmissionApplication(
        submissions,
        ServicePrincipalRegistry.from_mapping(environment()),
        preview=preview,
        preview_user_resolver=lambda environ: caller,
    )
    return application, authorization


def test_an_authorized_council_preview_is_read_only(store, artifacts):
    application, _ = _with_preview(store, artifacts, caller=COUNCIL_USER)
    body = fx.encode(fx.bundle())
    _, _, receipt = submit(application, body)

    status, _, payload = call(
        application,
        method="GET",
        path=f"/api/v1/foundry/snapshots/{receipt['checksum']}/preview",
        content_type=None,
        content_length="",
    )

    assert status == 200
    assert payload["checksum"] == receipt["checksum"]
    assert payload["folder_id"] == fx.ACTIVE_FOLDER_ID
    assert payload["would_create"] == 1
    # Read-only: no character, mapping or import row exists.
    assert store.characters == {}
    assert store.external_actor_mappings == []
    assert store.snapshot_imports == []


def test_an_ordinary_member_cannot_preview(store, artifacts):
    application, _ = _with_preview(store, artifacts, caller=ORDINARY_USER)
    _, _, receipt = submit(application, fx.encode(fx.bundle()))

    status, _, payload = call(
        application,
        method="GET",
        path=f"/api/v1/foundry/snapshots/{receipt['checksum']}/preview",
        content_type=None,
        content_length="",
    )

    assert status == 403
    assert payload["error"]["code"] == "not_guild_council"


def test_a_revoked_council_member_cannot_preview(store, artifacts):
    application, authorization = _with_preview(store, artifacts, caller=COUNCIL_USER)
    _, _, receipt = submit(application, fx.encode(fx.bundle()))
    authorization.revoke(COUNCIL_USER)

    status, _, payload = call(
        application,
        method="GET",
        path=f"/api/v1/foundry/snapshots/{receipt['checksum']}/preview",
        content_type=None,
        content_length="",
    )

    assert status == 403


def test_a_checksum_that_is_not_held_is_404(store, artifacts):
    application, _ = _with_preview(store, artifacts, caller=COUNCIL_USER)

    status, _, payload = call(
        application,
        method="GET",
        path=f"/api/v1/foundry/snapshots/{'b' * 64}/preview",
        content_type=None,
        content_length="",
    )

    assert status == 404
    assert payload["error"]["code"] == "snapshot_not_held"


def test_the_service_credential_cannot_be_used_to_preview(store, artifacts):
    """The submit-only principal has no route to Council data."""
    application, _ = _with_preview(store, artifacts, caller=ORDINARY_USER)
    _, _, receipt = submit(application, fx.encode(fx.bundle()))

    status, _, _ = call(
        application,
        method="GET",
        path=f"/api/v1/foundry/snapshots/{receipt['checksum']}/preview",
        headers={"Authorization": f"Bearer {CREDENTIAL}"},
        content_type=None,
        content_length="",
    )

    # The bearer credential is not even consulted on this route: the resolver
    # decides, and it resolved an ordinary member.
    assert status == 403
