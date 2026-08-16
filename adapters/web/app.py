"""The application factory and the ten P3.1 routes (route contract §4).

**The route set is closed.** A route that is not in §4-§8 of the accepted
contract does not exist, and registering one is a contract violation rather than
an implementation detail. `ROUTE_INVENTORY` below is the machine-checkable
statement of that: `TC-STRUCT-01` parses the contract document and asserts set
equality against what this factory registers.

## Where the sync/async seam is, and why

Provider I/O is `async` over `httpx`; PostgreSQL work is synchronous SQLAlchemy.
`.agents/AGENTS.md` forbids blocking database work on the event loop, so every
database unit of work goes through `run_in_threadpool` and every provider call is
awaited directly. The seam is explicit at each call site rather than hidden in a
wrapper, because a reader needs to see that **no database transaction is held
open across a network call to Discord**.

## What this file deliberately does not contain

No member route, no Council route, no administration route, no import route and
no audit route. Those are P3.2 and P3.3, behind stop gates P3.G1 and P3.G2. The
absence is the control the delivery plan asked for: no protected production query
package proceeds on a blocking finding.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.concurrency import run_in_threadpool

from adapters.web.composition import TEMPLATE_ROOT, WebComposition
from adapters.web.middleware import (
    BodyBound,
    ClientAddressPolicy,
    HostGuard,
    KillSwitch,
    SecurityHeaders,
    json_refusal,
)
from application.web import WEB_APPLICATION_VERSION
from application.web.capabilities import AuthMethod, resolve_capabilities
from application.web.config import BoundsSettings, WebSettings, canonical_settings
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
}

#: Routes P3.2 and P3.3 own. Named so `TC-STRUCT-01` can assert they are *absent*
#: from this build rather than merely unmentioned, and so a reader can tell "not
#: yet" from "never".
DEFERRED_ROUTES: dict[str, str] = {
    **{f"R-{number}": "P3.2" for number in range(20, 39)},
    **{f"R-{number}": "P3.3" for number in range(40, 50)},
}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def create_app(
    settings: WebSettings,
    *,
    composition: WebComposition | None = None,
    run_startup_checks: bool = True,
) -> FastAPI:
    """Build the portal. Refuses to start on a failed resource check (S-12/14/15)."""
    composition = composition or WebComposition(settings=settings)
    if run_startup_checks:
        composition.startup_warnings = run_resource_checks(settings, composition.engine)

    app = FastAPI(
        title="Freedom Blades portal",
        version=WEB_APPLICATION_VERSION,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.composition = composition
    app.state.settings = settings
    app.state.templates = Jinja2Templates(directory=str(TEMPLATE_ROOT))
    # Autoescaping for every configured extension, set at environment
    # construction rather than per template (TC-SEC-08). No template in this
    # package calls `|safe` on any value, and a test asserts that too.
    app.state.templates.env.autoescape = True
    # One read of each request bound, validated before either becomes a control
    # (2026-08-15, I-10). `BodyBound` and `ClientAddressPolicy` keep the numbers
    # for the process's lifetime, so the read that is checked has to be the read
    # they are given — a subclass answering `1 MiB` here and something larger to
    # the middleware would be a body bound that never applied.
    bounds = canonical_settings(settings.bounds, BoundsSettings)
    app.state.address_policy = ClientAddressPolicy(
        trusted_hops=bounds.trusted_proxy_hops
    )

    # Registration order is reverse execution order in Starlette, so this reads
    # bottom-up: headers wrap everything, then the body bound, then the kill
    # switch, then the host check outermost.
    app.add_middleware(SecurityHeaders, session_cookie_name=settings.session.cookie_name)
    app.add_middleware(BodyBound, max_bytes=bounds.max_request_bytes)
    app.add_middleware(KillSwitch, settings=settings)
    app.add_middleware(HostGuard, allowed_hosts=settings.allowed_hosts)

    _register_routes(app)
    _register_error_handlers(app)
    return app


# ---------------------------------------------------------------------------
# Request helpers
# ---------------------------------------------------------------------------


def _composition(request: Request) -> WebComposition:
    return request.app.state.composition


def _settings(request: Request) -> WebSettings:
    return request.app.state.settings


def _client_digest(request: Request) -> bytes | None:
    address = request.app.state.address_policy.resolve(request)
    if address is None:
        return None
    return keyed_digest(_settings(request).client_digest_key, address)


def _client_address(request: Request) -> str:
    return request.app.state.address_policy.resolve(request) or "unknown"


def _user_agent_digest(request: Request) -> bytes | None:
    agent = request.headers.get("user-agent")
    if not agent:
        return None
    return keyed_digest(_settings(request).client_digest_key, agent)


#: The only body encoding the portal's form routes accept. A multipart body on a
#: form route is not a form submission the application has any use for, and
#: accepting one would mean parsing an upload on a route that has no upload
#: (TC-LIM-03). Refused explicitly rather than left to fail deeper in the stack:
#: a `415` is an answer, and an unhandled parser assertion is a `500`.
FORM_CONTENT_TYPE = "application/x-www-form-urlencoded"


def _form_content_type_is_supported(request: Request) -> bool:
    declared = (request.headers.get("content-type") or "").split(";", 1)[0].strip()
    return declared == FORM_CONTENT_TYPE


def _origin_is_ours(request: Request) -> bool:
    """Step 5. Missing or mismatched `Origin` on a mutation is refused.

    Missing counts as mismatched, deliberately. Every browser that can reach this
    application sends `Origin` on a cross-site form post, and treating its
    absence as permission would make the check optional for exactly the caller it
    exists to stop.
    """
    return request.headers.get("origin") == _settings(request).public_origin


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


def _register_routes(app: FastAPI) -> None:
    settings: WebSettings = app.state.settings

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
        return _render(request, "login.html", view=view, status_code=200)

    @app.get("/v1/auth/discord/start", name="oauth_start")
    async def oauth_start(request: Request) -> Response:
        """R-03. A `GET` navigation, deliberately — see `application/web/oauth.py`.

        A `POST` start answering `303` to Discord would be blocked by
        `form-action 'self'`, and adding `https://discord.com` to that directive
        is a documented weakening of the accepted CSP. A navigation is not a form
        submission, so N-26 stands unweakened.
        """
        composition = _composition(request)
        correlation_id = uuid4()
        address = _client_address(request)
        digest = _client_digest(request)
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
        composition = _composition(request)
        correlation_id = uuid4()
        address = _client_address(request)
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

        digest = _client_digest(request)
        agent = _user_agent_digest(request)

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
                response = _render(
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
        composition = _composition(request)
        settings_ = _settings(request)
        token = request.cookies.get(settings_.session.cookie_name)
        if not token:
            return JSONResponse({"error": "not_authenticated"}, status_code=401)
        if not _origin_is_ours(request):
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
            if not csrf.verify(settings_.csrf_key, record.id, presented):
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
        _clear_session_cookie(response, settings_)
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
        response = _render(request, "emergency.html", view=view, status_code=200)
        response.headers["X-Robots-Tag"] = "noindex"
        return response

    @app.post("/v1/auth/emergency/webauthn/options", name="emergency_webauthn_options")
    async def emergency_webauthn_options(request: Request) -> Response:
        """R-07. `application/json`, because the WebAuthn API requires script."""
        composition = _composition(request)
        correlation_id = uuid4()
        if not _origin_is_ours(request):
            return json_refusal(403, "origin_invalid", correlation_id)
        address = _client_address(request)
        digest = _client_digest(request)

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
        composition = _composition(request)
        settings_ = _settings(request)
        correlation_id = uuid4()
        if not _origin_is_ours(request):
            return json_refusal(403, "origin_invalid", correlation_id)
        address = _client_address(request)
        digest = _client_digest(request)
        agent = _user_agent_digest(request)
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
        _set_session_cookie(response, settings_, login.session)
        return response

    @app.post("/v1/auth/emergency/recovery", name="emergency_recovery_login")
    async def emergency_recovery_login(request: Request) -> Response:
        """R-09. Consumes a host-issued grant (N-14). No route can issue one."""
        composition = _composition(request)
        settings_ = _settings(request)
        correlation_id = uuid4()
        if not _origin_is_ours(request):
            return JSONResponse({"error": "origin_invalid"}, status_code=403)
        if not _form_content_type_is_supported(request):
            return JSONResponse({"error": "unsupported_media_type"}, status_code=415)
        address = _client_address(request)
        digest = _client_digest(request)
        agent = _user_agent_digest(request)
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
        _set_session_cookie(response, settings_, login.session)
        return response

    @app.get("/healthz", name="health")
    async def health(request: Request) -> Response:
        """R-10. Loopback only; **not published by Caddy**, which is why it is open.

        Contains no secret, no player data, no identity, no database URL and no
        configuration value — only check names and pass/fail (VM-16).
        """
        composition = _composition(request)
        view = await run_in_threadpool(
            build_health_view, _settings(request), composition.engine, provider_ok=True
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


def _render(request: Request, template: str, *, view, status_code: int) -> HTMLResponse:
    templates: Jinja2Templates = request.app.state.templates
    return templates.TemplateResponse(
        request=request, name=template, context={"view": view}, status_code=status_code
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


def _register_error_handlers(app: FastAPI) -> None:
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
            return _render(request, "error.html", view=view, status_code=500)
        except Exception:  # noqa: BLE001 - the error page must never fail twice
            return JSONResponse(
                {"error": "unexpected_error", "correlation_id": str(correlation_id)},
                status_code=500,
            )


__all__ = ["DEFERRED_ROUTES", "ROUTE_INVENTORY", "create_app"]
