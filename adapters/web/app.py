"""The application factory and the ten P3.1 routes (route contract §4).

**The route set is closed.** A route that is not in §4-§8 of the accepted
contract does not exist, and registering one is a contract violation rather than
an implementation detail. `ROUTE_INVENTORY` below is the machine-checkable
statement of that: `TC-STRUCT-01` parses the contract document and asserts set
equality against what this factory registers.

**And so is the mount set.** From 2026-08-19 the factory registers exactly one
Starlette `Mount` — M-01, the `/static/` asset surface of route contract §1.2 —
declared in `MOUNT_INVENTORY` and asserted by the same test. It is called out
separately because a `Mount` carries no `methods`, so before the accepted D-03
correction it was invisible to the guard that keeps the URL surface closed.

## Where the sync/async seam is, and why

Provider I/O is `async` over `httpx`; PostgreSQL work is synchronous SQLAlchemy.
`.agents/AGENTS.md` forbids blocking database work on the event loop, so every
database unit of work goes through `run_in_threadpool` and every provider call is
awaited directly. The seam is explicit at each call site rather than hidden in a
wrapper, because a reader needs to see that **no database transaction is held
open across a network call to Discord**.

## What this file deliberately does not contain

No import route and no audit route. Those are P3.3, behind stop gate P3.G2, and
the absence is the control the delivery plan asked for: no Council import or
audit package proceeds before its gate.

The P3.2 member, Council, administration and account routes live in
`adapters/web/portal_routes.py` — the nineteen handlers and the matrix that
guards them, kept beside each other rather than appended here, because the
matrix is the thing a reviewer reads and it should not sit nine hundred lines
away from the routes it governs. Their identifiers are merged into
`ROUTE_INVENTORY` below, so `TC-STRUCT-01` still asserts one registered set
against the parsed contract rather than two that have to be kept in step.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import AsyncIterator, Callable
from uuid import UUID, uuid4

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.concurrency import run_in_threadpool

from adapters.web.composition import STATIC_ROOT, TEMPLATE_ROOT, WebComposition
from adapters.web.import_routes import P3_3_ROUTE_INVENTORY
from adapters.web.import_routes import register as register_p3_3_routes
from adapters.web.portal_routes import P3_2_ROUTE_INVENTORY
from adapters.web.portal_routes import register as register_p3_2_routes
from adapters.web.middleware import (
    SECURITY_HEADERS,
    BodyBound,
    ClientAddressPolicy,
    HostGuard,
    KillSwitch,
    SecurityHeaders,
    json_refusal,
)
from adapters.web.static_assets import STATIC_URL_PREFIX, StaticAssets
from application.web import WEB_APPLICATION_VERSION
from application.web.capabilities import AuthMethod, resolve_capabilities
from application.web.config import (
    SettingsAuthorityError,
    WebSettings,
    require_canonical_web_settings,
)
from application.web.crypto import keyed_digest
from application.web.errors import AuthenticationFailure, record_authentication_failure
from application.web.oauth import safe_return_path
from application.web.providers import (
    ProviderRefused,
    ProviderUnavailable,
    VerifiedCompletion,
)
from application.web.refusals import LoginRefusalReason, OAuthRefusalRecorder
from application.web.startup import build_health_view, run_resource_checks
from application.web.view_models import (
    Correlation,
    DeniedReason,
    DenialCategory,
    EmergencyFailure,
    EmergencyLoginView,
    LoginFailure,
    LoginPageView,
    NonMemberView,
    ProviderOption,
    SafeErrorView,
    ServiceDegradedView,
    Instant,
)

#: The closed inventory this package registers, by contract identifier. Asserted
#: against the parsed route contract by `TC-STRUCT-01`, so a route added without
#: a contract entry fails a test rather than a review.
ROUTE_INVENTORY: dict[str, tuple[str, str]] = {
    "R-01": ("GET", "/"),
    "R-02": ("GET", "/v1/login"),
    "R-03": ("GET", "/v1/auth/discord/start"),
    "R-04": ("GET", "/auth/discord/callback"),
    "R-05": ("POST", "/v1/auth/logout"),
    "R-06": ("GET", "/v1/auth/emergency"),
    "R-07": ("POST", "/v1/auth/emergency/webauthn/options"),
    "R-08": ("POST", "/v1/auth/emergency/webauthn/verify"),
    "R-09": ("POST", "/v1/auth/emergency/recovery"),
    "R-10": ("GET", "/healthz"),
    # P3.2's nineteen, defined beside their handlers in `portal_routes.py` and
    # merged here so `TC-STRUCT-01` still asserts **one** registered set against
    # the parsed contract document rather than two that have to agree.
    **P3_2_ROUTE_INVENTORY,
    # P3.3's ten, in `import_routes.py`, for the same reason.
    **P3_3_ROUTE_INVENTORY,
}

#: Routes a later package owns. Named rather than merely absent so `TC-STRUCT-01`
#: can assert they are *absent from this build*, and so a reader can tell "not
#: yet" from "never".
#:
#: **Empty from P3.3 onward.** It held R-40 to R-49 while the import, job and
#: audit package was behind stop gate P3.G2; those ten are registered above, and
#: the accepted inventory is now complete. A later phase that adds a route adds
#: it to the contract first and to this mapping second.
DEFERRED_ROUTES: dict[str, str] = {}

#: The closed **mount** inventory, by contract identifier (route contract §1.2).
#:
#: **Added 2026-08-19 by the accepted D-03 correction (`C-P3.4-A`, item D-03-1).**
#: `ROUTE_INVENTORY` above is a set of `(method, path)` pairs and `TC-STRUCT-01`
#: asserted it by reading `getattr(route, "methods", ...)` off every registered
#: route. A Starlette `Mount` has no `methods` attribute, so it contributed
#: nothing to that set and the one machine check protecting the closed inventory
#: was **blind to mounts**: `app.mount("/anything", SomeApp())` would have added a
#: whole URL subtree and passed the guard. A separate identifier space is used
#: rather than another `R-nn` because a mount is a different kind of thing — it
#: claims a prefix rather than one method on one path, and numbering it as a route
#: would have made the contract's `(method, path)` grammar lie about it.
#:
#: `TC-STRUCT-01` now asserts this mapping against the registered `Mount` objects
#: and against the contract's own §1.2 table, so an undeclared mount fails a test
#: exactly as an undeclared route does.
MOUNT_INVENTORY: dict[str, str] = {
    "M-01": STATIC_URL_PREFIX,
}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class RequestAuthority:
    """The objects a request reads, captured when `create_app()` accepted them.

    **This exists because `app.state` is not a boundary** (2026-08-16, P3.G1
    request-authority and lifecycle remediation, finding 1). The previous
    correction bound the *composition* to the routes and left a
    `_settings(request)` helper that read `request.app.state.settings` on every
    call — for the client and user-agent digests, mutation-origin validation,
    cookie names and attributes, CSRF key selection and the health view. Starlette's
    `State` is an ordinary mutable namespace with an ordinary `__setattr__`, so
    `app.state.settings = graph_b` gave an already-validated application a second
    complete settings graph to serve from: a different accepted `Origin`, a
    different CSRF key, a different cookie contract, and different keyed audit and
    rate-limit identities than the graph `create_app()` checked. That is the same
    post-validation replacement shape the provider and engine remediation removed,
    one level further out.

    The correction is **which object the handler holds**, not another check.
    `create_app()` builds one of these from the canonical graph it accepted and
    passes it into route registration and the error handler; the closures below
    read from it. There is no per-request dereference of mutable state to
    intercept, so there is nothing for a per-request canonicality check to detect
    and none is made — comparing a captured graph against `app.state` would be a
    second authority admitted and then argued with, which is the defect rather
    than the fix.

    `app.state.settings`, `app.state.composition`, `app.state.templates` and
    `app.state.address_policy` remain as **diagnostic** references an operator and
    the suite read. Replacing any of them changes what is reported and nothing
    that serves a request; `TC-STRUCT-10` asserts that production request code
    reads none of them.

    The three members are the whole per-request read set:

    * `settings` — the canonical exact-base graph, the one authority;
    * `address_policy` — N-34's hop count, already fixed at construction from
      `settings.bounds`, and the object every client-IP resolution goes through;
      and
    * `templates` — the Jinja environment whose `autoescape` is set once at
      construction (TC-SEC-08). Captured for the same reason as the other two: a
      replaced environment is a replaced escaping policy.
    """

    settings: WebSettings
    address_policy: ClientAddressPolicy
    templates: Jinja2Templates

    def client_address(self, request: Request) -> str:
        return self.address_policy.resolve(request) or "unknown"

    def client_digest(self, request: Request) -> bytes | None:
        address = self.address_policy.resolve(request)
        if address is None:
            return None
        return keyed_digest(self.settings.client_digest_key, address)

    def user_agent_digest(self, request: Request) -> bytes | None:
        agent = request.headers.get("user-agent")
        if not agent:
            return None
        return keyed_digest(self.settings.client_digest_key, agent)

    def origin_is_ours(self, request: Request) -> bool:
        """Step 5. Missing or mismatched `Origin` on a mutation is refused.

        Missing counts as mismatched, deliberately. Every browser that can reach
        this application sends `Origin` on a cross-site form post, and treating
        its absence as permission would make the check optional for exactly the
        caller it exists to stop.

        The origin compared against is the captured graph's, so the set of
        accepted origins is fixed when the application is built rather than
        whenever the check runs.
        """
        return request.headers.get("origin") == self.settings.public_origin

    def render(
        self, request: Request, template: str, *, view, status_code: int
    ) -> HTMLResponse:
        return self.templates.TemplateResponse(
            request=request,
            name=template,
            context={"view": view},
            status_code=status_code,
        )


def _attach_cleanup_failure(failure: BaseException, cleanup: BaseException) -> None:
    """Record `cleanup` beneath `failure` without letting it take `failure`'s place.

    Both halves of a failed startup that also failed to clean up matter, and they
    matter differently. The refusal is *why the process must not serve* and is the
    exception an operator has to act on; the cleanup failure is a second,
    consequential fault that must not be silently dropped either. Python's default
    would surface the wrong one: an exception raised inside an `except` block
    replaces the exception being handled, so a provider whose transport failed to
    shut down would hide the `ConfigurationError` that refused the boot behind it.

    So the refusal is re-raised and the cleanup failure is attached to the **tail**
    of its `__context__` chain, where a traceback prints it under "During handling
    of the above exception, another exception occurred" without displacing it.
    Attaching at the tail rather than directly on `failure` is what keeps any
    context `failure` already carried; the `seen` set is what keeps a chain that
    already reaches `cleanup` from being extended into a cycle.

    Nothing is rendered, formatted or logged here. Both exceptions are attached as
    they were raised, and `WebComposition.aclose()` states that it adds no settings
    value, database URL or provider configuration to what it re-raises.
    """
    # Python has already set `cleanup.__context__` to `failure`, because `cleanup`
    # was raised while `failure` was being handled. Clearing that back-reference is
    # what stops the attachment below from closing a loop, and it loses nothing:
    # `failure` is the very exception `cleanup` is about to be attached beneath.
    cleanup.__context__ = None
    cleanup.__suppress_context__ = False
    tail = failure
    seen = {id(failure)}
    while tail.__context__ is not None and id(tail.__context__) not in seen:
        tail = tail.__context__
        seen.add(id(tail))
    if id(cleanup) not in seen:
        tail.__context__ = cleanup
        tail.__suppress_context__ = False


def _portal_lifespan(
    composition: WebComposition,
    authority: RequestAuthority,
    *,
    run_startup_checks: bool,
) -> Callable[[FastAPI], "AsyncIterator[None]"]:
    """The ASGI lifespan that owns `composition` — including on a refused startup.

    **Installed because `aclose()` had no caller in production** (2026-08-16,
    P3.G1 request-authority and lifecycle remediation, finding 2).
    `WebComposition.aclose()` closed the provider and disposed an owned engine
    correctly, and `create_app()` registered no lifespan and no shutdown handler,
    so an ordinary ASGI stop left the production HTTP client and the SQLAlchemy
    engine and its pool open. Tests calling `composition.aclose()` by hand proved
    the method, never the process.

    **The resource checks run here, not in the factory** (2026-08-16, P3.G1
    request-authority and lifecycle re-review, remaining finding). `create_app()`
    used to construct the composition, call `run_resource_checks()`, and only
    afterwards build the `FastAPI` object this lifespan is installed on. On the
    production construction path both process-lifetime resources — the provider's
    HTTP client and the owned SQLAlchemy engine — already existed by the time that
    call ran, and a refusal propagated out of the factory: no application was
    returned, so no lifespan could ever execute, so `aclose()` had no caller on the
    one path where the process was being told to stop. A composition that owns
    process-lifetime resources has to release them on every failed startup as well
    as on a normal shutdown, and "startup refused" is a failed startup.

    Running them inside the lifespan makes a refusal an **ASGI startup failure**:
    the checks complete before `lifespan.startup.complete` is sent, so an
    application whose checks refused never serves a request, exactly as a factory
    that raised never returned one. What changes is that the `finally` below now
    covers that path.

    The checks cross the sync/async seam through `run_in_threadpool` for the same
    reason every other database unit of work in this module does: S-14 and S-15
    open connections and query, and `.agents/AGENTS.md` forbids blocking database
    work on the event loop. In the factory this was synchronous code on a
    synchronous call path; on a lifespan it would be blocking the loop that has
    to answer the startup message.

    The composition and the authority are both **closed over**, not looked up.
    Resolving either from `app.state` would mean a replaced `app.state.composition`
    could redirect cleanup to an intruder — leaving the real provider and engine
    open while reporting a clean stop — or point the checks at an engine other than
    the one every request will transact on. `authority.settings` is the same
    canonical graph object every route reads, so the configuration S-12/S-14/S-15
    are evaluated against is the configuration the application serves from, by
    identity rather than by agreement.

    **A composition is claimed before anything else happens** (2026-08-16, P3.G1
    test-clock-authority re-review). `WebComposition.aclose()` permanently closes
    the provider and disposes an owned engine, and this lifespan performed no
    live-or-closed check on the way *in*: a composition handed to two applications,
    or one application whose lifespan was entered twice, answered
    `lifespan.startup.complete` the second time and served requests against a
    closed Discord HTTP client until an OAuth route dereferenced it. With
    `run_startup_checks=False` that was immediate; with the checks enabled it was
    not caught either, because a disposed SQLAlchemy engine builds a replacement
    pool and S-14/S-15 pass against a resource nobody may use.

    `claim_for_startup()` is therefore the first statement below, before the
    checks and before the `yield` that admits requests, and outside the cleanup
    `try` — a composition this application was refused is one it must not close.

    Everything about *what* is closed, what is only borrowed, and what a repeated
    shutdown does is `WebComposition.aclose()`'s to state, and is stated there
    rather than duplicated here. What a startup failure that *also* fails to clean
    up surfaces is `_attach_cleanup_failure`'s, immediately above.
    """

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        # **The claim is first, and it is deliberately outside the `try` below.**
        # A composition that is already started, closing or closed is not this
        # application's to run and not this application's to clean up: in the
        # first case the lifespan that holds it is still serving requests through
        # the provider and the engine, and closing them here would turn a caller's
        # mistake into an outage; in the other two there is nothing left to
        # release. A refusal here is an ASGI startup failure like any other, so no
        # request is served — which is the whole point, because the resource
        # checks below cannot detect the condition (`WebComposition.aclose()`
        # leaves the provider closed and `Engine.dispose()` silently builds a
        # replacement pool, so S-14 and S-15 would both report health).
        composition.claim_for_startup()
        try:
            if run_startup_checks:
                composition.startup_warnings = await run_in_threadpool(
                    run_resource_checks, authority.settings, composition.engine
                )
            yield
        except BaseException as failure:
            # Not `finally`, because the two paths differ in one way that matters:
            # here the cleanup runs *while* an exception is in flight, and a
            # cleanup failure must be recorded beneath that exception rather than
            # be allowed to replace it.
            try:
                await composition.aclose()
            except BaseException as cleanup_failure:  # noqa: BLE001 - re-attached
                _attach_cleanup_failure(failure, cleanup_failure)
            raise
        await composition.aclose()

    return lifespan


def create_app(
    settings: WebSettings | None = None,
    *,
    composition: WebComposition | None = None,
    run_startup_checks: bool = True,
) -> FastAPI:
    """Build the portal. Its startup refuses on a failed resource check (S-12/14/15).

    **The refusal is the application's, not this function's** (2026-08-16, P3.G1
    request-authority and lifecycle re-review). S-12, S-14 and S-15 are evaluated
    by the ASGI lifespan installed below, before `lifespan.startup.complete`, so a
    refused portal still never serves a request — and, unlike a factory that raised
    with a live provider and a live engine in hand, it releases them on the way
    out. `create_app()` returning is therefore no longer a statement that the
    resource checks passed; entering the returned application's lifespan is.

    **Exactly one configuration authority** (2026-08-16, P3.G1 canonical-graph
    remediation). Either `settings`, from which the composition is built, or a
    `composition` that already holds the canonical graph — never both.

    **And a composition backs exactly one running application** (2026-08-16, P3.G1
    test-clock-authority re-review). Building two applications over one
    composition is not refused here — the factory opens nothing and closes
    nothing, so there is no resource for a second call to endanger — but only one
    of them can *start*: the lifespan installed below claims the composition, and
    the second startup fails rather than serving requests against the provider and
    engine the first shutdown released.

    This signature previously took both and required no relationship between
    them: `create_app(settingsa, composition=composition_b)` produced an
    application whose middleware, routes, cookies, digests and startup checks
    used A while every service used B, with no private mutation and no
    unsupported API anywhere in it. The fix is not a comparison of the two — two
    authorities that agree today are still two authorities — but the removal of
    the second. From the line below, `settings` *is* `composition.settings` and
    the argument is out of scope for the rest of this function.

    **The provider is not checked here, because it can no longer be replaced**
    (2026-08-16, P3.G1 provider/engine authority remediation). This factory used
    to call `_require_provider_from()` once, comparing the composition's provider
    against the graph. That comparison was true at startup and said nothing about
    the object R-03 and R-04 would dereference afterwards: `provider` was a
    public attribute, and the regression offered as proof only replaced it and
    called `create_app` *again*. `WebComposition` now derives the provider from
    its own canonical `settings.discord` and holds it write-once behind a
    read-only property, so the check had nothing left to detect and has been
    removed rather than kept as security theatre. What survives is the graph
    requirement below, which does detect a supported state: a `WebComposition`
    subclass — the test harness is one — whose `settings` is not the canonical
    exact-base graph.
    """
    if (settings is None) == (composition is None):
        raise SettingsAuthorityError(
            "create_app takes exactly one configuration authority: either "
            "`settings`, from which it builds the composition, or a "
            "`composition` that already holds the canonical settings graph. "
            "Both together are two authorities nothing can require to agree, "
            "and neither is not a configuration at all."
        )
    if composition is None:
        composition = WebComposition(settings=settings)
    # The composition's graph, and nothing else, for the rest of this factory and
    # for every request the application serves. Required rather than assumed:
    # `WebComposition.settings` is write-once and canonicalised by its own
    # constructor, but `composition` is a parameter and a *subclass* may answer
    # this property with something else — the portal suite's harness is such a
    # subclass. This is the one place where "the canonical graph" becomes a
    # property of the application rather than of how it happened to be built.
    settings = require_canonical_web_settings(
        composition.settings, subject="create_app"
    )
    # The resource checks are **not** run here. They run inside the lifespan
    # installed below, so that a refusal releases the provider and the owned
    # engine this composition is already holding — see `_portal_lifespan`.

    templates = Jinja2Templates(directory=str(TEMPLATE_ROOT))
    # Autoescaping for every configured extension, set at environment
    # construction rather than per template (TC-SEC-08). No template in this
    # package calls `|safe` on any value, and a test asserts that too.
    templates.env.autoescape = True
    # The canonical graph's exact-base request bounds (2026-08-15, I-10;
    # 2026-08-16, canonical graph). `BodyBound` and `ClientAddressPolicy` keep
    # these numbers for the process's lifetime, so the read that was checked has
    # to be the read they are given — a subclass answering `1 MiB` here and
    # something larger to the middleware would be a body bound that never
    # applied. It is read directly rather than rebuilt a second time: the graph
    # was canonicalised once, at the composition root, and a second rebuild here
    # would be a second authority for the same numbers.
    bounds = settings.bounds
    # The one object every handler below reads from, built here from the graph
    # this factory accepted and handed to route registration and the error
    # handler (2026-08-16, P3.G1 request-authority remediation). See
    # `RequestAuthority` for why a captured object rather than `app.state`.
    authority = RequestAuthority(
        settings=settings,
        address_policy=ClientAddressPolicy(trusted_hops=bounds.trusted_proxy_hops),
        templates=templates,
    )

    app = FastAPI(
        title="Freedom Blades portal",
        version=WEB_APPLICATION_VERSION,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        # Startup checks *and* production cleanup, both wired to the ASGI
        # lifecycle rather than left to a caller (2026-08-16, P3.G1 lifecycle
        # remediation and its re-review). The composition and the authority are
        # closed over by `_portal_lifespan`, so neither the checks nor the
        # shutdown can be redirected by a later `app.state` assignment, and a
        # refused startup releases what this composition already holds.
        lifespan=_portal_lifespan(
            composition, authority, run_startup_checks=run_startup_checks
        ),
    )
    # Diagnostics and test inspection only, from here on. Every one of these is
    # already held by `authority` or by the closures below, so replacing one
    # changes what an operator is shown and nothing the application does —
    # asserted by `TC-STRUCT-10` rather than left as a convention.
    app.state.composition = composition
    app.state.settings = settings
    app.state.templates = templates
    app.state.address_policy = authority.address_policy

    # Registration order is reverse execution order in Starlette, so this reads
    # bottom-up: headers wrap everything, then the body bound, then the kill
    # switch, then the host check outermost. Each takes its values from the same
    # captured graph the routes use.
    app.add_middleware(SecurityHeaders, session_cookie_name=settings.session.cookie_name)
    app.add_middleware(BodyBound, max_bytes=bounds.max_request_bytes)
    app.add_middleware(KillSwitch, settings=settings)
    app.add_middleware(HostGuard, allowed_hosts=settings.allowed_hosts)

    # M-01, the one mount (route contract §1.2, operational contract §4.4).
    # Registered before the routes so a reader meets the whole URL surface in one
    # place, and named so `url_for("static", path=…)` works for P3.4's templates
    # without a hard-coded prefix in twenty-four files. It is inside every
    # middleware registered above — the host check refuses an unknown `Host` on an
    # asset exactly as on a page (D-03-1), the security headers apply, and the
    # kill switch deliberately lets this prefix through.
    app.mount(
        STATIC_URL_PREFIX, StaticAssets(directory=STATIC_ROOT), name="static"
    )
    _register_routes(app, composition, authority)
    # P3.2's routes take the same two objects, closed over in the same way, for
    # the same reason: `app.state` is a mutable namespace and a per-request read
    # of it is one more path to a provider, engine, origin, key or cookie other
    # than the ones this factory accepted.
    register_p3_2_routes(app, composition, authority)
    # P3.3's ten, likewise. Registered after P3.2's so the inventory reads in
    # contract order; the framework matches on path and method, so the order
    # carries no behaviour of its own.
    register_p3_3_routes(app, composition, authority)
    _register_error_handlers(app, authority)
    return app


# ---------------------------------------------------------------------------
# Request helpers
# ---------------------------------------------------------------------------


#: The only body encoding the portal's form routes accept. A multipart body on a
#: form route is not a form submission the application has any use for, and
#: accepting one would mean parsing an upload on a route that has no upload
#: (TC-LIM-03). Refused explicitly rather than left to fail deeper in the stack:
#: a `415` is an answer, and an unhandled parser assertion is a `500`.
FORM_CONTENT_TYPE = "application/x-www-form-urlencoded"


def _form_content_type_is_supported(request: Request) -> bool:
    declared = (request.headers.get("content-type") or "").split(";", 1)[0].strip()
    return declared == FORM_CONTENT_TYPE


def _set_session_cookie(response: Response, settings: WebSettings, issued) -> None:
    """N-05, exactly: host-only, `Secure`, `HttpOnly`, `SameSite=Lax`, `Path=/`.

    **No `Domain` attribute**, which is what host-only means; the `__Host-`
    prefix makes the browser enforce it rather than trusting us to omit it.
    """
    response.set_cookie(
        settings.session.cookie_name,
        issued.token,
        max_age=int((issued.absolute_expires_at - utcnow()).total_seconds()),
        secure=settings.session.cookie_secure,
        httponly=True,
        samesite="lax",
        path="/",
    )


def _clear_session_cookie(response: Response, settings: WebSettings) -> None:
    response.delete_cookie(
        settings.session.cookie_name, path="/", httponly=True, samesite="lax"
    )


def _login_transaction_cookie_name(settings: WebSettings) -> str:
    return settings.session.login_transaction_cookie_name


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


def _register_routes(
    app: FastAPI, composition: WebComposition, authority: RequestAuthority
) -> None:
    """Bind the routes to **this** composition and **this** graph, once.

    Both are closed over rather than dereferenced from `app.state` per request
    (2026-08-16, P3.G1 provider/engine authority remediation). `app.state` is an
    ordinary mutable namespace, so a per-request `request.app.state.composition`
    was one more route to a different provider and a different engine than the
    factory validated — the same shape as the assignable `composition.provider`
    the remediation removed, one level out.

    **The settings graph now arrives the same way** (2026-08-16, P3.G1
    request-authority remediation). This function used to open by reading
    `app.state.settings` — which was the captured graph and was fine — while the
    request helpers it called went back to `request.app.state.settings` per call.
    Closing over the graph *here* and leaving that door open elsewhere meant the
    cookie name a route branched on came from the factory's object and the origin
    the same route validated came from whatever `app.state` held at the time. The
    graph is now handed in as part of `authority`, and every helper reads from
    that object.

    `app.state.composition`, `app.state.settings`, `app.state.templates` and
    `app.state.address_policy` remain as the diagnostic references an operator
    and the suite read; replacing any of them changes what is *reported*, and
    cannot change which provider serves an OAuth start, which engine a
    transaction opens on, or which origin, key, cookie or digest a request uses.
    """
    settings: WebSettings = authority.settings

    @app.get("/", name="root")
    async def root(request: Request) -> Response:
        """R-01. Exists so the bare hostname is not a `404`.

        No content, no view model, no session effect.
        """
        if settings.session.cookie_name in request.cookies:
            return RedirectResponse("/v1/characters", status_code=303)
        return RedirectResponse("/v1/login", status_code=303)

    @app.get("/v1/login", name="login_page")
    async def login_page(request: Request) -> Response:
        """R-02. Unauthenticated HTML, VM-01. **No CSRF token** — there is no session yet."""
        failure_code = request.query_params.get("failure")
        view = LoginPageView(
            state="error" if failure_code else "ready",
            providers=(
                ProviderOption(
                    key="discord",
                    display_name="Discord",
                    start_path="/v1/auth/discord/start",
                    enabled="discord" in settings.provider_registry,
                ),
            ),
            emergency_access_available=True,
            failure=(
                LoginFailure(
                    code=_login_failure_code(failure_code),
                    correlation=Correlation(_correlation_from(request)),
                )
                if failure_code
                else None
            ),
        )
        return authority.render(request, "login.html", view=view, status_code=200)

    @app.get("/v1/auth/discord/start", name="oauth_start")
    async def oauth_start(request: Request) -> Response:
        """R-03. A `GET` navigation, deliberately — see `application/web/oauth.py`.

        A `POST` start answering `303` to Discord would be blocked by
        `form-action 'self'`, and adding `https://discord.com` to that directive
        is a documented weakening of the accepted CSP. A navigation is not a form
        submission, so N-26 stands unweakened.
        """
        correlation_id = uuid4()
        address = authority.client_address(request)
        digest = authority.client_digest(request)
        return_path = safe_return_path(request.query_params.get("return"))

        decision = await run_in_threadpool(
            _consume_rate_limit,
            composition,
            _oauth_start_action(),
            client_ip=address,
        )
        if not decision.allowed:
            response = _redirect_to_login("rate_limited", correlation_id)
            response.headers["Retry-After"] = str(decision.retry_after_seconds)
            return response

        def unit(connection):
            return composition.services(connection).oauth.start(
                provider=composition.provider,
                return_path=return_path,
                now=utcnow(),
                client_ip_hash=digest,
            )

        started, _state = await run_in_threadpool(
            _in_transaction, composition.engine, unit
        )

        response = RedirectResponse(started.authorization_url, status_code=303)
        response.set_cookie(
            _login_transaction_cookie_name(settings),
            str(started.transaction_id),
            max_age=settings.session.oauth_transaction_minutes * 60,
            secure=settings.session.cookie_secure,
            httponly=True,
            samesite="lax",
            path="/",
        )
        return response

    @app.get("/auth/discord/callback", name="oauth_callback")
    async def oauth_callback(request: Request) -> Response:
        """R-04. The one route outside `/v1`, because it is registered at the provider.

        Steps run in the order the route contract sets, and every one of them
        must pass. The transaction is consumed **before** the provider is
        contacted, so a provider failure cannot leave a replayable transaction
        behind.

        **This route is orchestration, not enforcement** (OD-44). It hands
        `complete()` the transaction id it validated, and `complete()` claims it
        atomically from durable state before creating anything. Reordering the
        statements below, or calling `complete()` from somewhere else entirely,
        cannot produce a session: the claim matches zero rows and the check and
        unique constraints on `sessions` refuse the row independently. The claim
        also compares the transaction's recorded `provider_key` against the key
        carried by the verified result, so the *provider* half of the completion
        is durable state too — this route is not trusted to have called the
        adapter the transaction was started with.

        **Every terminal refusal below goes through `recorder`**, which writes
        exactly one `auth.login.refused` event for this attempt with the same
        correlation id the caller is shown (TC-AUTH-11). The recorder is
        constructed once and records once, so a branch added later cannot return
        silently and a branch that both raises and records cannot double-write.
        See `application/web/refusals.py` for what may appear in the payload —
        the short answer is a reason and, when one has been validated, a
        transaction id.
        """
        correlation_id = uuid4()
        address = authority.client_address(request)
        recorder = OAuthRefusalRecorder(
            composition.engine, correlation_id=correlation_id
        )

        decision = await run_in_threadpool(
            _consume_rate_limit,
            composition,
            _oauth_callback_action(),
            client_ip=address,
        )
        if not decision.allowed:
            # An authentication-attempt audit, not a separate rate-limit audit
            # and not both: TC-AUTH-11 requires exactly one event per attempt.
            await _record_refusal(recorder, LoginRefusalReason.RATE_LIMITED)
            response = _redirect_to_login("rate_limited", correlation_id)
            response.headers["Retry-After"] = str(decision.retry_after_seconds)
            return response

        raw_transaction = request.cookies.get(_login_transaction_cookie_name(settings))
        state = request.query_params.get("state")
        code = request.query_params.get("code")
        if not raw_transaction or not state or not code:
            await _record_refusal(
                recorder, LoginRefusalReason.CALLBACK_PARAMETERS_MISSING
            )
            return _clear_transaction(
                _redirect_to_login("transaction_unknown", correlation_id), settings
            )
        try:
            transaction_id = UUID(raw_transaction)
        except ValueError:
            # The cookie value is attacker input and is **not** echoed into the
            # audit row; the event names the `unbound` category instead.
            await _record_refusal(
                recorder, LoginRefusalReason.TRANSACTION_COOKIE_MALFORMED
            )
            return _clear_transaction(
                _redirect_to_login("transaction_unknown", correlation_id), settings
            )

        def consume(connection):
            services = composition.services(connection)
            return services.oauth.consume(
                transaction_id=transaction_id,
                state=state,
                now=utcnow(),
                correlation_id=correlation_id,
            )

        try:
            recovered = await run_in_threadpool(
                _in_transaction, composition.engine, consume
            )
        except AuthenticationFailure as failure:
            # The service's transaction has rolled back, which is what "nothing
            # was consumed" means. Only now can the refusal be recorded durably.
            await run_in_threadpool(recorder.record_failure, failure)
            return _clear_transaction(
                _redirect_to_login(failure.code, failure.correlation_id), settings
            )

        # Outside any transaction, deliberately: a database transaction held open
        # across a network call to Discord would hold a connection for as long as
        # Discord takes to answer.
        try:
            tokens = await composition.provider.exchange(
                code=code, code_verifier=recovered.code_verifier
            )
            identity = await composition.provider.verify(tokens)
            # One indivisible verified result, and the only shape `complete()`
            # accepts. Both halves carry the key the adapter stamped on them, and
            # this construction is where they are required to agree — so the
            # provider the completion binds to is a property of what was verified
            # rather than of which branch of this route ran.
            verified = VerifiedCompletion(identity=identity, tokens=tokens)
        except ProviderUnavailable:
            # An outage and a refusal are one sentence to the caller and two
            # different sentences to an operator, so the redirect code is shared
            # and the audit reason is not.
            await _record_refusal(
                recorder,
                LoginRefusalReason.PROVIDER_UNAVAILABLE,
                transaction_id=transaction_id,
            )
            return _clear_transaction(
                _redirect_to_login("provider_error", correlation_id), settings
            )
        except ProviderRefused:
            await _record_refusal(
                recorder,
                LoginRefusalReason.PROVIDER_REFUSED,
                transaction_id=transaction_id,
            )
            return _clear_transaction(
                _redirect_to_login("provider_error", correlation_id), settings
            )

        digest = authority.client_digest(request)
        agent = authority.user_agent_digest(request)

        def complete(connection):
            services = composition.services(connection)
            return services.oauth.complete(
                # OD-44. The same validated id the cookie carried and `consume()`
                # matched. The service claims it from durable state before it
                # creates anything, so this argument is a *reference* the database
                # checks, not a fact the route is trusted to have established.
                transaction_id=transaction_id,
                completion=verified,
                return_path=recovered.return_path,
                now=utcnow(),
                correlation_id=correlation_id,
                client_ip_hash=digest,
                user_agent_digest=agent,
            )

        try:
            completed = await run_in_threadpool(
                _in_transaction, composition.engine, complete
            )
        except AuthenticationFailure as failure:
            await run_in_threadpool(recorder.record_failure, failure)
            if failure.code == "not_a_member":
                # ADR 0004's rejection step: **no session is created**, the
                # transaction is already consumed so it cannot be replayed, and
                # the person leaves no session row and no token record.
                view = NonMemberView(
                    state="denied",
                    reason=DeniedReason(DenialCategory.NOT_A_MEMBER),
                    guild_display_name="Freedom Blades",
                    checked_at=Instant.of(utcnow()),
                    correlation=Correlation(failure.correlation_id),
                )
                response = authority.render(
                    request, "non_member.html", view=view, status_code=403
                )
                return _clear_transaction(response, settings)
            return _clear_transaction(
                _redirect_to_login(failure.code, failure.correlation_id), settings
            )

        response = RedirectResponse(completed.return_path, status_code=303)
        _set_session_cookie(response, settings, completed.session)
        return _clear_transaction(response, settings)

    @app.post("/v1/auth/logout", name="logout")
    async def logout(request: Request) -> Response:
        """R-05. `POST` only, CSRF and origin required.

        A forced logout is a real, if minor, nuisance attack, and the uniform
        rule — every cookie-authenticated mutation carries a token — is easier to
        review than an exception for this one.
        """
        token = request.cookies.get(settings.session.cookie_name)
        if not token:
            return JSONResponse({"error": "not_authenticated"}, status_code=401)
        if not authority.origin_is_ours(request):
            return JSONResponse({"error": "origin_invalid"}, status_code=403)
        if not _form_content_type_is_supported(request):
            return JSONResponse(
                {"error": "unsupported_media_type"}, status_code=415
            )

        form = await request.form()
        presented = form.get("csrf_token") or request.headers.get("x-csrf-token")
        correlation_id = uuid4()

        def unit(connection):
            from application.web import csrf

            services = composition.services(connection)
            record = services.session_service.resolve(token, now=utcnow())
            if record is None:
                return "not_authenticated"
            if not csrf.verify(settings.csrf_key, record.id, presented):
                return "csrf_invalid"
            services.session_service.logout(
                record=record,
                account_id=record.platform_account_id,
                now=utcnow(),
                correlation_id=correlation_id,
            )
            return "ok"

        outcome = await run_in_threadpool(_in_transaction, composition.engine, unit)
        if outcome == "not_authenticated":
            return JSONResponse({"error": "not_authenticated"}, status_code=401)
        if outcome == "csrf_invalid":
            return JSONResponse({"error": "csrf_invalid"}, status_code=403)

        response = RedirectResponse("/v1/login", status_code=303)
        _clear_session_cookie(response, settings)
        return response

    @app.get("/v1/auth/emergency", name="emergency_login_page")
    async def emergency_login_page(request: Request) -> Response:
        """R-06. Reachable when Discord is down — that is its purpose.

        It reveals **no** account existence: the page is identical whether or not
        a credential is enrolled, and both flags below are configuration rather
        than lookups.
        """
        failure_code = request.query_params.get("failure")
        view = EmergencyLoginView(
            state="ready",
            webauthn_supported_hint=True,
            recovery_form_available=True,
            failure=(
                EmergencyFailure(
                    code=_emergency_failure_code(failure_code),
                    correlation=Correlation(_correlation_from(request)),
                )
                if failure_code
                else None
            ),
        )
        response = authority.render(request, "emergency.html", view=view, status_code=200)
        response.headers["X-Robots-Tag"] = "noindex"
        return response

    @app.post("/v1/auth/emergency/webauthn/options", name="emergency_webauthn_options")
    async def emergency_webauthn_options(request: Request) -> Response:
        """R-07. `application/json`, because the WebAuthn API requires script."""
        correlation_id = uuid4()
        if not authority.origin_is_ours(request):
            return json_refusal(403, "origin_invalid", correlation_id)
        address = authority.client_address(request)
        digest = authority.client_digest(request)

        decision = await run_in_threadpool(
            _consume_rate_limit, composition, _webauthn_action(), client_ip=address
        )
        if not decision.allowed:
            response = json_refusal(429, "rate_limited", correlation_id)
            response.headers["Retry-After"] = str(decision.retry_after_seconds)
            return response

        def unit(connection):
            return composition.services(connection).break_glass.begin_assertion(
                now=utcnow(), client_ip_hash=digest
            )

        options = await run_in_threadpool(_in_transaction, composition.engine, unit)
        return JSONResponse(options.payload, status_code=200)

    @app.post("/v1/auth/emergency/webauthn/verify", name="emergency_webauthn_verify")
    async def emergency_webauthn_verify(request: Request) -> Response:
        """R-08. A successful verification creates a break-glass session (N-15)."""
        correlation_id = uuid4()
        if not authority.origin_is_ours(request):
            return json_refusal(403, "origin_invalid", correlation_id)
        address = authority.client_address(request)
        digest = authority.client_digest(request)
        agent = authority.user_agent_digest(request)
        try:
            payload = await request.json()
        except Exception:  # noqa: BLE001 - malformed JSON is one outcome
            return json_refusal(400, "invalid", correlation_id)

        decision = await run_in_threadpool(
            _consume_rate_limit, composition, _webauthn_action(), client_ip=address
        )
        if not decision.allowed:
            response = json_refusal(429, "rate_limited", correlation_id)
            response.headers["Retry-After"] = str(decision.retry_after_seconds)
            return response

        # N-32's **second** budget, which the per-address one above does not
        # cover: ten assertions per platform account per sixty minutes, whatever
        # addresses they arrive from. It is consumed here, after the presented
        # credential has been resolved and before anything is verified, in its
        # own committed transaction — the refusal below rolls its transaction
        # back, and a budget that rolled back with it would bound nothing.
        account_decision = await run_in_threadpool(
            _consume_assertion_account_budget, composition, payload
        )
        if account_decision is not None and not account_decision.allowed:
            response = json_refusal(429, "rate_limited", correlation_id)
            response.headers["Retry-After"] = str(
                account_decision.retry_after_seconds
            )
            return response

        def unit(connection):
            return composition.services(connection).break_glass.complete_assertion(
                credential_payload=payload,
                now=utcnow(),
                correlation_id=correlation_id,
                client_ip_hash=digest,
                user_agent_digest=agent,
            )

        try:
            login = await run_in_threadpool(
                _in_transaction, composition.engine, unit
            )
        except AuthenticationFailure as failure:
            await run_in_threadpool(
                record_authentication_failure, composition.engine, failure
            )
            return json_refusal(403, failure.code, failure.correlation_id)

        response = JSONResponse(
            {"status": "ok", "redirect": "/v1/admin/role-capabilities"}, status_code=200
        )
        _set_session_cookie(response, settings, login.session)
        return response

    @app.post("/v1/auth/emergency/recovery", name="emergency_recovery_login")
    async def emergency_recovery_login(request: Request) -> Response:
        """R-09. Consumes a host-issued grant (N-14). No route can issue one."""
        correlation_id = uuid4()
        if not authority.origin_is_ours(request):
            return JSONResponse({"error": "origin_invalid"}, status_code=403)
        if not _form_content_type_is_supported(request):
            return JSONResponse({"error": "unsupported_media_type"}, status_code=415)
        address = authority.client_address(request)
        digest = authority.client_digest(request)
        agent = authority.user_agent_digest(request)
        form = await request.form()
        token = (form.get("token") or "").strip()
        if not token:
            return _redirect_to_emergency("invalid", correlation_id)

        decision = await run_in_threadpool(
            _consume_rate_limit, composition, _recovery_action(), client_ip=address
        )
        if not decision.allowed:
            response = _redirect_to_emergency("rate_limited", correlation_id)
            response.headers["Retry-After"] = str(decision.retry_after_seconds)
            return response

        # N-33's per-grant cap, spent in its own transaction for the same reason
        # the per-address one is: the redemption below rolls back on every
        # refusal, and this counter's whole purpose is to survive refusals. No
        # `Retry-After` accompanies it — the per-grant budget is for all time,
        # and a hint would promise a window that does not exist.
        attempt_refusal = await run_in_threadpool(
            _consume_grant_attempt, composition, token, correlation_id
        )
        if attempt_refusal is not None:
            await run_in_threadpool(
                record_authentication_failure, composition.engine, attempt_refusal
            )
            return _redirect_to_emergency(
                attempt_refusal.code, attempt_refusal.correlation_id
            )

        def unit(connection):
            return composition.services(connection).break_glass.redeem_recovery_grant(
                token=token,
                now=utcnow(),
                correlation_id=correlation_id,
                client_ip_hash=digest,
                user_agent_digest=agent,
            )

        try:
            login = await run_in_threadpool(
                _in_transaction, composition.engine, unit
            )
        except AuthenticationFailure as failure:
            await run_in_threadpool(
                record_authentication_failure, composition.engine, failure
            )
            return _redirect_to_emergency(failure.code, failure.correlation_id)

        response = RedirectResponse("/v1/admin/role-capabilities", status_code=303)
        _set_session_cookie(response, settings, login.session)
        return response

    @app.get("/healthz", name="health")
    async def health(request: Request) -> Response:
        """R-10. Loopback only; **not published by Caddy**, which is why it is open.

        Contains no secret, no player data, no identity, no database URL and no
        configuration value — only check names and pass/fail (VM-16).
        """
        view = await run_in_threadpool(
            build_health_view, settings, composition.engine, provider_ok=True
        )
        return JSONResponse(
            view.as_payload(), status_code=200 if view.status == "ok" else 503
        )


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _in_transaction(engine, unit):
    """One unit of work, one transaction. Called only from a worker thread."""
    with engine.begin() as connection:
        return unit(connection)


async def _record_refusal(
    recorder: OAuthRefusalRecorder,
    reason: LoginRefusalReason,
    *,
    transaction_id: UUID | None = None,
) -> None:
    """The recorder's write is PostgreSQL work, so it crosses the same seam.

    Not wrapped in a `try`: a refusal that cannot be recorded becomes a safe
    error (VM-20), which is the same fail-closed direction SM-01 requires of the
    success path. No session exists on any refusal path, so this can never turn a
    refusal into a login.
    """
    await run_in_threadpool(recorder.record, reason, transaction_id=transaction_id)


def _consume_rate_limit(composition, action, *, client_ip: str):
    """Count the attempt in its **own** transaction, before the work begins.

    This is not a style choice. Almost every rate-limited attempt here ends in a
    refusal, and a refusal rolls its transaction back — so a counter incremented
    inside the work transaction would be rolled back too, and the limit would
    never be reached however many times an attacker tried. The budget has to
    outlive the attempt it is counting.
    """
    with composition.engine.begin() as connection:
        return composition.services(connection).rate_limiter.check_ip(
            action, client_ip=client_ip, now=utcnow()
        )


def _consume_assertion_account_budget(composition, payload):
    """N-32's per-account budget, in its **own** transaction, before verification.

    Two statements in one short transaction: resolve the presented credential to
    the account it protects, then spend that account's budget. Both have to be
    here rather than inside the assertion, because the assertion's transaction is
    rolled back by every refusal — and an assertion budget that only counted
    successful logins would be a budget on nobody.

    A credential that resolves to no account spends an equivalent per-credential
    budget instead, so the caller cannot tell an enrolled credential from an
    invented one by which attempt starts answering `rate_limited`. A payload
    carrying no credential id at all spends neither and returns `None`: the
    per-address budget above already counted it, and the assertion refuses it a
    moment later.
    """
    from application.web.rate_limit import LimitedAction

    now = utcnow()
    with composition.engine.begin() as connection:
        services = composition.services(connection)
        subject = services.break_glass.assertion_subject(credential_payload=payload)
        if subject.account_id is not None:
            return services.rate_limiter.check_account(
                LimitedAction.WEBAUTHN_ASSERTION,
                account_id=subject.account_id,
                now=now,
            )
        if subject.credential_id is not None:
            return services.rate_limiter.check_credential(
                LimitedAction.WEBAUTHN_ASSERTION,
                credential_id=subject.credential_id,
                now=now,
            )
        return None


def _consume_grant_attempt(composition, token: str, correlation_id: UUID):
    """N-33's per-grant attempt, in its **own** transaction, before redemption.

    Returns the refusal to raise rather than raising it, because raising inside
    this transaction would roll back the increment that produced it.
    """
    with composition.engine.begin() as connection:
        return composition.services(connection).break_glass.note_recovery_attempt(
            token=token, correlation_id=correlation_id
        )


def _redirect_to_login(code: str, correlation_id: UUID) -> RedirectResponse:
    return RedirectResponse(
        f"/v1/login?failure={code}&correlation={correlation_id}", status_code=303
    )


def _redirect_to_emergency(code: str, correlation_id: UUID) -> RedirectResponse:
    return RedirectResponse(
        f"/v1/auth/emergency?failure={code}&correlation={correlation_id}",
        status_code=303,
    )


def _clear_transaction(response: Response, settings: WebSettings) -> Response:
    response.delete_cookie(
        settings.session.login_transaction_cookie_name,
        path="/",
        httponly=True,
        samesite="lax",
    )
    return response


def _correlation_from(request: Request) -> UUID:
    raw = request.query_params.get("correlation")
    try:
        return UUID(raw) if raw else uuid4()
    except ValueError:
        return uuid4()


_LOGIN_FAILURE_CODES = {
    "transaction_expired",
    "transaction_unknown",
    "state_mismatch",
    "provider_error",
    "rate_limited",
    "not_available",
}
_EMERGENCY_FAILURE_CODES = {"invalid", "expired", "consumed", "rate_limited", "not_available"}


def _login_failure_code(candidate: str | None) -> str:
    """A query parameter is caller-supplied, so it is mapped into the closed set.

    Rendering it back unmapped would put a caller's string into the page — which
    autoescaping would make inert, and which would still be a caller-controlled
    value in a response that promises a closed vocabulary.
    """
    return candidate if candidate in _LOGIN_FAILURE_CODES else "not_available"


def _emergency_failure_code(candidate: str | None) -> str:
    return candidate if candidate in _EMERGENCY_FAILURE_CODES else "not_available"


def _oauth_start_action():
    from application.web.rate_limit import LimitedAction

    return LimitedAction.OAUTH_START


def _oauth_callback_action():
    from application.web.rate_limit import LimitedAction

    return LimitedAction.OAUTH_CALLBACK


def _webauthn_action():
    from application.web.rate_limit import LimitedAction

    return LimitedAction.WEBAUTHN_ASSERTION


def _recovery_action():
    from application.web.rate_limit import LimitedAction

    return LimitedAction.RECOVERY_LOGIN


def _register_error_handlers(app: FastAPI, authority: RequestAuthority) -> None:
    """The safe error page renders through the captured Jinja environment too.

    It is the one handler that runs for *any* unhandled exception on *any* route,
    so leaving it to dereference `app.state.templates` would have kept a mutable
    escaping policy on the single response path a caller is most likely to be
    able to provoke.
    """

    @app.exception_handler(Exception)
    async def unexpected(request: Request, exc: Exception) -> Response:
        """VM-20: a correlation id and nothing else (N-25).

        No exception text, no path, no SQL, no stack frame and no token reaches
        the response — or the log line the user can quote. The operator
        correlates through their own logs; the user quotes the UUID.
        """
        correlation_id = uuid4()
        import logging

        logging.getLogger("freedom.web").exception(
            "unhandled request failure correlation_id=%s path=%s",
            correlation_id,
            request.url.path,
        )
        view = SafeErrorView(state="error", correlation=Correlation(correlation_id))
        try:
            response = authority.render(request, "error.html", view=view, status_code=500)
        except Exception:  # noqa: BLE001 - the error page must never fail twice
            response = JSONResponse(
                {"error": "unexpected_error", "correlation_id": str(correlation_id)},
                status_code=500,
            )
        for header, value in SECURITY_HEADERS.items():
            response.headers.setdefault(header, value)
        response.headers["Cache-Control"] = "no-store"
        return response


__all__ = [
    "DEFERRED_ROUTES",
    "MOUNT_INVENTORY",
    "ROUTE_INVENTORY",
    "RequestAuthority",
    "create_app",
]
