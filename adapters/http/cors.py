"""The cross-origin policy for the snapshot submission route, and nothing else.

The Foundry module submits from a **browser**. `main.js` calls `fetch` with
`Authorization`, `Content-Type: application/json`, `Idempotency-Key` and
`X-Snapshot-SHA256`, none of which are CORS-safelisted, so unless Foundry and
this application are served from one origin the browser sends an
unauthenticated `OPTIONS` preflight first and refuses to send the POST at all
unless that preflight is answered correctly.

Review findings B-1 and S-I-1 are both about that: the adapter answered `405`
to `OPTIONS` and emitted no CORS permission, so the *supported* workflow could
never reach application code in the deployed topology. `curl` could not show it,
because `curl` does not enforce CORS — it is the browser, not the server, that
refuses.

## What this module decides, and what it refuses to decide

It decides one thing: **whether this exact origin may have the browser make this
exact request.** It is transport policy, it holds no game or application rule,
and it is the only place in the adapter that looks at `Origin`.

- **An explicit allowlist of exact origins.** No wildcard, no reflection of
  whatever arrived, no suffix or regular-expression matching. `*` is refused by
  configuration validation rather than accepted as a shortcut, and an origin
  that is not configured gets no permission header at all — so the browser
  refuses the request on the caller's own machine.
- **No credentials.** `Access-Control-Allow-Credentials` is never emitted. The
  module sends `credentials: "omit"` and authenticates with a bearer header;
  adding cookie authority to this endpoint would make it reachable by any page
  a logged-in browser happens to have open, which is the whole class of attack a
  bearer-only endpoint does not have.
- **A bounded preflight.** `OPTIONS` is answered only for the submission route,
  only for `POST`, and only for exactly the four request headers the module
  sends. A preflight asking for anything else is refused rather than widened.
- **No authentication on the preflight.** Browsers do not put the
  `Authorization` header on a preflight — it is one of the headers being *asked
  about*. Requiring it would make the check unpassable. The preflight therefore
  authenticates nothing and reveals nothing: it says which methods and headers
  this route accepts, which is already public in this repository's
  documentation, and it reaches no application service.
- **`Vary`, so a cache cannot mix answers up.** Every response on this route
  varies on `Origin`, including the ones that carry no permission — otherwise a
  shared cache could serve an allowed origin the header-less answer it stored
  for a different one. Preflights additionally vary on the two
  `Access-Control-Request-*` headers.

## Configuration

`FREEDOM_SNAPSHOT_ALLOWED_ORIGINS` holds a comma- or whitespace-separated list
of exact origins:

    FREEDOM_SNAPSHOT_ALLOWED_ORIGINS='https://foundry1.example.org,https://foundry2.example.org'

**Unset or empty is a valid configuration and the default.** It means "no
browser origin may call this endpoint": no preflight succeeds, no permission
header is emitted, and the non-browser paths — the documented `curl` smoke test
and the loopback rehearsal — are entirely unaffected, because a request with no
`Origin` header is not a cross-origin browser request and this module does not
touch it. A deployment that has not yet been told which Foundry origins exist
therefore fails closed rather than open.

Each entry is validated at startup: scheme and host only, no path, no query, no
fragment, no userinfo, no `*`, no `null`, and HTTP permitted only for a loopback
host — the same narrow exception `transport.js` makes so a same-host rehearsal
is possible. Configuration is normalised to the form a browser actually sends
(lower-case scheme and host, default port omitted) so that the comparison at
request time can be an exact string match with nothing clever in it.

## What is deliberately not here

No `Access-Control-Expose-Headers`: the module reads the response status and the
JSON body, both of which are available to it without one. No preflight for the
Council preview route: that route is inert until the Phase 3 authentication
boundary exists, and a second CORS surface is a decision for whoever builds it.
"""
from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from urllib.parse import urlsplit

#: The environment variable holding the trusted Foundry origins.
ALLOWED_ORIGINS_VARIABLE = "FREEDOM_SNAPSHOT_ALLOWED_ORIGINS"

#: The only method a preflight may ask about on this route.
ALLOWED_METHOD = "POST"

#: Exactly the request headers `foundry-module/scripts/transport.js` sends,
#: lower-cased because a preflight's `Access-Control-Request-Headers` is
#: case-insensitive. A preflight asking for a fifth header is refused: the set is
#: a contract with one known client, not a list to grow when something breaks.
ALLOWED_REQUEST_HEADERS = frozenset(
    {"authorization", "content-type", "idempotency-key", "x-snapshot-sha256"}
)

#: How long a browser may reuse one preflight result, in seconds. Ten minutes:
#: long enough that a retry loop does not re-preflight every attempt, short
#: enough that revoking an origin takes effect without asking anybody to clear a
#: browser cache.
PREFLIGHT_MAX_AGE = 600

#: Hosts for which plain HTTP is permitted, matching `transport.js`. An origin
#: on one of these cannot reach the network, which is what makes the exception
#: safe to have for a same-host rehearsal.
_LOOPBACK_HOSTS = frozenset({"localhost", "127.0.0.1", "[::1]"})

_SEPARATORS = re.compile(r"[,\s]+")


class CorsConfigurationError(ValueError):
    """The configured origin allowlist is unusable. Raised at startup."""


@dataclass(frozen=True, slots=True)
class PreflightRefused:
    """The preflight is answered, but with no permission and a reason code."""

    code: str
    message: str


@dataclass(frozen=True, slots=True)
class PreflightAllowed:
    """The preflight succeeds. `headers` carry the permission, and there is no body."""

    headers: tuple[tuple[str, str], ...]


class CorsPolicy:
    """Which browser origins may drive the submission request, and how.

    Immutable once built. Adding or removing an origin is a configuration change
    plus a reload, which is what makes "this origin is no longer trusted" a fact
    about the running process rather than a row somebody might forget to check.
    """

    __slots__ = ("_origins",)

    def __init__(self, origins: Iterable[str] = ()) -> None:
        self._origins = frozenset(origins)

    def __len__(self) -> int:
        return len(self._origins)

    @property
    def origins(self) -> tuple[str, ...]:
        """The configured origins, for an operator-facing startup summary."""
        return tuple(sorted(self._origins))

    @classmethod
    def from_mapping(cls, environ: Mapping[str, str]) -> CorsPolicy:
        """Build the policy from configuration, or refuse to start."""
        raw = (environ.get(ALLOWED_ORIGINS_VARIABLE) or "").strip()
        if not raw:
            return cls()
        origins = {
            _validated_origin(entry)
            for entry in _SEPARATORS.split(raw)
            if entry
        }
        return cls(origins)

    def allows(self, origin: str | None) -> bool:
        """Exact match against the allowlist. No pattern, no suffix, no wildcard."""
        return origin is not None and origin in self._origins

    def response_headers(self, origin: str | None) -> list[tuple[str, str]]:
        """Permission headers for an *actual* response on the submission route.

        Emitted on every outcome the browser must be able to read — a receipt, a
        `401`, a refused bundle, an unexpected `500` — because a response the
        browser is not permitted to read is reported to the module as an opaque
        network failure, and "the credential is wrong" would then be
        indistinguishable from "the server is down".

        An origin that is absent or unlisted gets no permission header at all.
        The `Vary` handling that goes with this lives in `vary_for`, which
        applies whether or not permission was granted.
        """
        if not self.allows(origin):
            return []
        return [("Access-Control-Allow-Origin", origin or "")]

    def preflight(
        self,
        *,
        origin: str | None,
        requested_method: str | None,
        requested_headers: str | None,
    ) -> PreflightAllowed | PreflightRefused:
        """Answer one `OPTIONS` preflight for the submission route.

        Nothing here authenticates, and nothing here reaches an application
        service. Every refusal carries a code an operator can act on and no
        detail an attacker can use: whether an origin is configured is exactly
        what the caller is asking, and the answer is no.
        """
        if not self.allows(origin):
            return PreflightRefused(
                "origin_not_allowed",
                "This origin is not configured as a trusted Foundry origin for "
                "snapshot submission. An operator configures the allowlist.",
            )
        if (requested_method or "").strip().upper() != ALLOWED_METHOD:
            return PreflightRefused(
                "preflight_method_not_allowed",
                f"This endpoint accepts {ALLOWED_METHOD} only.",
            )
        requested = _requested_headers(requested_headers)
        if not requested <= ALLOWED_REQUEST_HEADERS:
            return PreflightRefused(
                "preflight_header_not_allowed",
                "The request asks to send a header this endpoint does not "
                "accept.",
            )
        return PreflightAllowed(
            (
                ("Access-Control-Allow-Origin", origin or ""),
                ("Access-Control-Allow-Methods", ALLOWED_METHOD),
                # The declared set, not whatever was asked for. Echoing the
                # request back would make the answer a function of the question.
                (
                    "Access-Control-Allow-Headers",
                    ", ".join(sorted(ALLOWED_REQUEST_HEADERS)),
                ),
                ("Access-Control-Max-Age", str(PREFLIGHT_MAX_AGE)),
            )
        )

    @staticmethod
    def vary_for(*, preflight: bool) -> str:
        """The `Vary` value for a response on the submission route.

        `Origin` is present even when no permission was granted, so a shared
        cache cannot hand one origin the answer it stored for another.
        """
        fields = ["Origin", "Authorization"]
        if preflight:
            fields += [
                "Access-Control-Request-Method",
                "Access-Control-Request-Headers",
            ]
        return ", ".join(fields)


def origin_of(environ: Mapping[str, object]) -> str | None:
    """The request's `Origin`, or `None` for a non-browser caller.

    A request with no `Origin` is not a cross-origin browser request: `curl`,
    the documented smoke test and the loopback rehearsal all arrive this way and
    are unaffected by any of this. An empty or `null` origin is treated as
    absent — `null` is what a browser sends from an opaque origin, and an opaque
    origin is exactly what must not be allowlistable.
    """
    origin = environ.get("HTTP_ORIGIN")
    if not isinstance(origin, str):
        return None
    origin = origin.strip()
    if not origin or origin.lower() == "null":
        return None
    return origin


def _requested_headers(value: str | None) -> frozenset[str]:
    if not value:
        return frozenset()
    return frozenset(
        name.strip().lower() for name in value.split(",") if name.strip()
    )


def _validated_origin(entry: str) -> str:
    """Normalise one configured origin, or refuse to start."""
    candidate = entry.strip()
    if candidate in {"*", "null"}:
        raise CorsConfigurationError(
            f"{ALLOWED_ORIGINS_VARIABLE} contains {candidate!r}. This endpoint "
            "accepts an explicit list of exact origins only: a wildcard would "
            "let any page in any browser drive a submission, and 'null' is what "
            "an opaque origin sends."
        )
    parts = urlsplit(candidate)
    if parts.scheme not in {"https", "http"}:
        raise CorsConfigurationError(
            f"{ALLOWED_ORIGINS_VARIABLE} entry {candidate!r} is not an origin. "
            "Write the scheme and host a browser sends, such as "
            "'https://foundry1.example.org'."
        )
    if parts.path not in {"", "/"} or parts.query or parts.fragment:
        raise CorsConfigurationError(
            f"{ALLOWED_ORIGINS_VARIABLE} entry {candidate!r} carries a path, "
            "query or fragment. An origin is a scheme, a host and a port — a "
            "browser never sends more than that, so more than that can never "
            "match."
        )
    if "@" in parts.netloc:
        raise CorsConfigurationError(
            f"{ALLOWED_ORIGINS_VARIABLE} entry {candidate!r} carries userinfo, "
            "which is not part of an origin and would never be compared."
        )
    host = (parts.hostname or "").lower()
    if not host:
        raise CorsConfigurationError(
            f"{ALLOWED_ORIGINS_VARIABLE} entry {candidate!r} names no host."
        )
    try:
        port = parts.port
    except ValueError:
        raise CorsConfigurationError(
            f"{ALLOWED_ORIGINS_VARIABLE} entry {candidate!r} has a malformed "
            "port."
        ) from None
    bracketed = f"[{host}]" if ":" in host else host
    if parts.scheme == "http" and bracketed not in _LOOPBACK_HOSTS:
        raise CorsConfigurationError(
            f"{ALLOWED_ORIGINS_VARIABLE} entry {candidate!r} is plain HTTP. A "
            "snapshot carries every exported Actor's mechanics and is never "
            "sent in clear text; HTTP is permitted only for a loopback host, "
            "for a same-host rehearsal."
        )
    default_port = 443 if parts.scheme == "https" else 80
    suffix = "" if port in (None, default_port) else f":{port}"
    return f"{parts.scheme}://{bracketed}{suffix}"
