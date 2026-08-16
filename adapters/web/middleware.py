"""The authorization chain's outer links, in the order route contract §2.1 sets.

    1. Host check          -> 400 before routing
    2. Kill switch         -> 503 for everything except /healthz
    3. Body bound          -> 413 before the body is read
    4. Session resolution   (route dependency)
    5. Origin check         (route dependency, mutations only)
    6. CSRF check           (route dependency, cookie-authenticated mutations)
    7. Capability resolution(route dependency)
    8. Object authorization (application service)
    9. Application service

Steps 1 to 3 are middleware because they must run **before routing**: a request
to an unknown host should not reach a handler in order to be told so, and a body
over the bound should be refused before anything reads it. Steps 4 to 7 are route
dependencies because they need the matched route to know which of them apply.

**Order is the design.** A body bound applied after routing would have let the
request be buffered first; a kill switch applied after the session lookup would
have made the maintenance page depend on the database it may be protecting.
"""
from __future__ import annotations

import time
from dataclasses import dataclass

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, Response

from application.web.config import WebSettings

#: The one path that answers while the kill switch is engaged. It is on the
#: loopback bind and is not published by Caddy, so leaving it up during
#: maintenance exposes nothing and is what lets an operator watch recovery.
HEALTH_PATH = "/healthz"

#: N-26, exactly. Tightening it needs no policy decision; weakening it, adding a
#: remote asset origin or allowing inline script/style requires documented
#: security review (delivery plan §7).
CONTENT_SECURITY_POLICY = (
    "default-src 'self'; base-uri 'none'; object-src 'none'; "
    "frame-ancestors 'none'; form-action 'self'; img-src 'self' data:; "
    "script-src 'self'; style-src 'self'"
)

#: §7.2. `X-Frame-Options` is omitted **deliberately**: `frame-ancestors 'none'`
#: supersedes it, and duplicating one rule in two syntaxes is how they drift
#: apart.
SECURITY_HEADERS = {
    "Content-Security-Policy": CONTENT_SECURITY_POLICY,
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "same-origin",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
    "Permissions-Policy": "geolocation=(), camera=(), microphone=(), payment=()",
}


class HostGuard(BaseHTTPMiddleware):
    """Step 1. An unknown `Host` is `400` **before routing**.

    Host validation is not decoration: the session cookie is host-only and the
    OAuth redirect is origin-bound, so a request arriving under a hostname the
    operator did not configure is either a misrouted proxy or an attempt to make
    the application generate links for somebody else's domain.
    """

    def __init__(self, app, *, allowed_hosts: tuple[str, ...]) -> None:
        super().__init__(app)
        self._allowed = frozenset(host.lower() for host in allowed_hosts)

    async def dispatch(self, request: Request, call_next):
        host = (request.headers.get("host") or "").split(":", 1)[0].lower()
        if host not in self._allowed:
            return PlainTextResponse("Unknown host.", status_code=400)
        return await call_next(request)


class KillSwitch(BaseHTTPMiddleware):
    """Step 2. Layer 1 of the operator kill switch (N-56, operational contract §4.3).

    A file's presence disables the portal **without stopping the Discord bot or
    Foundry**, which is the property that makes it usable during an incident. The
    file is `stat`-ed at most once per second per process, so the switch is
    effective within a second and costs one syscall.
    """

    def __init__(self, app, *, settings: WebSettings) -> None:
        super().__init__(app)
        self._path = settings.kill_switch_file
        self._checked_at = 0.0
        self._engaged = False

    def engaged(self) -> bool:
        now = time.monotonic()
        if now - self._checked_at >= 1.0:
            self._engaged = self._path.exists()
            self._checked_at = now
        return self._engaged

    async def dispatch(self, request: Request, call_next):
        if request.url.path != HEALTH_PATH and self.engaged():
            response = PlainTextResponse(
                "The Freedom Blades portal is temporarily unavailable for "
                "maintenance. The Discord bot is unaffected.",
                status_code=503,
            )
            response.headers["Retry-After"] = "300"
            return response
        return await call_next(request)


class BodyBound(BaseHTTPMiddleware):
    """Step 3. `Content-Length` over N-19 is `413` **before the body is read**.

    A missing `Content-Length` on a method that carries a body is refused too: a
    chunked upload with no declared length is precisely the shape that would
    bypass a limit applied to a header.
    """

    _BODY_METHODS = frozenset({"POST", "PUT", "PATCH"})

    def __init__(self, app, *, max_bytes: int) -> None:
        super().__init__(app)
        self._max_bytes = max_bytes

    async def dispatch(self, request: Request, call_next):
        if request.method in self._BODY_METHODS:
            raw = request.headers.get("content-length")
            if raw is None:
                if request.headers.get("transfer-encoding", "").lower() == "chunked":
                    return PlainTextResponse("Length required.", status_code=411)
            else:
                try:
                    length = int(raw)
                except ValueError:
                    return PlainTextResponse("Malformed length.", status_code=400)
                if length > self._max_bytes:
                    return PlainTextResponse("Body too large.", status_code=413)
        return await call_next(request)


class SecurityHeaders(BaseHTTPMiddleware):
    """§7.2, on every response this application produces.

    `Cache-Control: no-store` is added to every authenticated response — an
    intermediary or a browser's back button holding a rendered protected page is
    the same disclosure as an unauthenticated read of it.
    """

    def __init__(self, app, *, session_cookie_name: str) -> None:
        super().__init__(app)
        self._cookie = session_cookie_name

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        for header, value in SECURITY_HEADERS.items():
            response.headers.setdefault(header, value)
        authenticated = self._cookie in request.cookies
        if authenticated or request.url.path.startswith("/v1/"):
            response.headers["Cache-Control"] = "no-store"
        return response


@dataclass(frozen=True, slots=True)
class ClientAddressPolicy:
    """N-34. Exactly one proxy hop, trusted only from a loopback peer.

    The right-most `X-Forwarded-For` entry is used, because that is the one the
    trusted proxy appended; every entry to its left was supplied by whoever was
    talking to the proxy and is worth nothing. A request that reaches the
    application port from any other peer is refused rather than believed, which
    bounds header spoofing to "an attacker who is already on this host".
    """

    trusted_hops: int = 1

    def resolve(self, request: Request) -> str | None:
        peer = request.client.host if request.client else None
        if peer is None:
            return None
        if peer not in ("127.0.0.1", "::1"):
            # Not from the trusted proxy. The peer *is* the client, and no
            # forwarded header is believed.
            return peer
        forwarded = request.headers.get("x-forwarded-for")
        if not forwarded:
            return peer
        entries = [entry.strip() for entry in forwarded.split(",") if entry.strip()]
        if not entries:
            return peer
        return entries[-1]


def json_refusal(status: int, code: str, correlation_id) -> JSONResponse:
    """The JSON shape R-07/R-08 refuse with: a code and a correlation id.

    No provider text, no exception text, no path, no SQL — the same rule as
    VM-20, expressed for the two routes that answer `application/json` because
    the WebAuthn API requires script-driven credential exchange.
    """
    return JSONResponse(
        {"error": code, "correlation_id": str(correlation_id)}, status_code=status
    )


__all__ = [
    "BodyBound",
    "CONTENT_SECURITY_POLICY",
    "ClientAddressPolicy",
    "HEALTH_PATH",
    "HostGuard",
    "KillSwitch",
    "SECURITY_HEADERS",
    "SecurityHeaders",
    "json_refusal",
]
