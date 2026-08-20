"""R-20 to R-38: the P3.2 route surface, and nothing else.

A handler here does four things and no more: it establishes the caller, parses
input, invokes **one** use case, and renders that use case's typed result. Every
decision it looks like it is making has already been made somewhere a test can
reach without a request object — the authorization chain in
`application/web/access_control.py`, the matrix in `GUARDS` below, and the
services in `application/web/`.

## Why the matrix is a table and not nineteen `if` statements

`GUARDS` is route contract §5.2, transcribed once. A handler that forgot its
check would be a handler with no guard, which is visible at a glance and
assertable by a test; a handler with a subtly different inline check would be
neither. `test_p3_2_matrix.py` parses the accepted contract and asserts these
rows against it, so the transcription is checked rather than trusted.

## The order of the mutation preamble is the contract's order

Session → origin → CSRF → capability resolution (including any provider
refresh) → capability decision → object → service. One function, `_preamble`,
performs the first five in that sequence, and it matters in both directions: an
unauthenticated mutation answers `401` rather than leaking that its origin was
also wrong, a forged synchronizer token is refused before the platform makes a
single network call on the request's behalf, and a capability refusal happens
**before** the application service runs, so a refused request performs no
unauthorized read and no unauthorized write.

Object-level authorization is deliberately *not* in this file. It belongs inside
the transaction that reads the object, which is where
`CharacterAccessRepository.access_for()` puts it — a route that resolved an
object before step 7 would be a defect even if the response were later
suppressed.

## Denial bodies carry the category and nothing else

`denied.html` renders a closed-vocabulary category and **no correlation id**.
That is not an omission: route contract §2.3 requires the `404` for an
inaccessible object and the `404` for an absent one to be byte-identical, and a
correlation id differs per request, so printing one would make the two
distinguishable by exactly the amount it varies (TC-OBJ-07).

Since the accepted D-03 correction of 2026-08-19 the carrier is **VM-22
`DeniedView`**, which has exactly `state` and `reason`. Every generic denial on
this surface renders it. The non-member page keeps VM-02 and its
membership-recovery context, because that page is *meant* to be distinguishable
from "not signed in" — that distinction is its entire content.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.concurrency import run_in_threadpool

from application.audit import ActorCapability
from application.web import csrf
from application.web.access_control import (
    Requirement,
    RouteGuard,
    SessionAbsent,
    authorize,
    close_request,
    open_request,
)
from application.web.capabilities import (
    AdministratorScope,
    MAPPABLE_CAPABILITIES,
    MappingProvenance,
)
from application.web.errors import (
    NotAMember,
    RefusalCode,
    WebRefusal,
)
from application.web.pagination import InvalidCursor, page_size
from application.web.providers import (
    ProviderRefused,
    ProviderTokens,
    ProviderUnavailable,
)
from application.web.role_mappings import MappingRefused, run_mapping_change
from application.web.view_models import (
    ROLE_MAPPING_BOUND,
    Actor,
    ConflictView,
    Correlation,
    DeniedReason,
    DenialCategory,
    DeniedView,
    Instant,
    NonMemberView,
    RoleCapabilityView,
    RoleMappingRow,
    SafeText,
    ServiceDegradedView,
    bounded_tuple,
)

#: The closed P3.2 inventory, by contract identifier. Merged into `app.py`'s
#: `ROUTE_INVENTORY` so `TC-STRUCT-01` still asserts one set against the parsed
#: contract document.
P3_2_ROUTE_INVENTORY: dict[str, tuple[str, str]] = {
    "R-20": ("GET", "/v1/characters"),
    "R-21": ("GET", "/v1/characters/{character_id}"),
    "R-22": ("GET", "/v1/council/characters"),
    "R-23": ("GET", "/v1/council/characters/{character_id}/links"),
    "R-24": ("GET", "/v1/council/identity-search"),
    "R-25": ("POST", "/v1/council/characters/{character_id}/links"),
    "R-26": ("POST", "/v1/council/characters/{character_id}/links/{access_id}/revoke"),
    "R-27": ("POST", "/v1/council/characters/{character_id}/links/{access_id}/default"),
    "R-28": ("GET", "/v1/council/identity-migration"),
    "R-29": ("POST", "/v1/council/identity-migration/{proposal_id}/confirm"),
    "R-30": ("POST", "/v1/council/identity-migration/{proposal_id}/reject"),
    "R-31": ("GET", "/v1/council/field-profile"),
    "R-32": ("GET", "/v1/admin/role-capabilities"),
    "R-33": ("POST", "/v1/admin/role-capabilities"),
    "R-34": ("POST", "/v1/admin/role-capabilities/{mapping_id}/revoke"),
    "R-35": ("GET", "/v1/account/identities"),
    "R-36": ("GET", "/v1/account/identities/link/start"),
    "R-37": ("POST", "/v1/account/identities/{identity_id}/unlink"),
    "R-38": ("POST", "/v1/admin/role-capabilities/{mapping_id}/ratify"),
}

#: Route contract §5.2, as data. `continuity_allowed` is N-65's surface: a
#: continuity-scoped session — every break-glass session, and every
#: ordinary-provider session whose administrator authority descends only from
#: emergency-provenance mappings — reaches R-32, R-33, R-34 and R-35 and
#: nothing else in this package. **R-38 is deliberately absent from that set**:
#: ratification is the door between emergency and ordinary authority, and a
#: session on the emergency side does not hold the handle.
GUARDS: dict[str, RouteGuard] = {
    "R-20": RouteGuard("R-20", Requirement.MEMBER_READ, navigation=True),
    "R-21": RouteGuard("R-21", Requirement.MEMBER_READ, navigation=True),
    "R-22": RouteGuard("R-22", Requirement.COUNCIL, navigation=True),
    "R-23": RouteGuard("R-23", Requirement.COUNCIL, navigation=True),
    # An HTMX partial, so an absent session is `401` rather than a redirect: a
    # `303` swapped into a fragment target would render the login page inside
    # the Council screen.
    "R-24": RouteGuard("R-24", Requirement.COUNCIL),
    "R-25": RouteGuard("R-25", Requirement.COUNCIL, mutation=True),
    "R-26": RouteGuard("R-26", Requirement.COUNCIL, mutation=True),
    "R-27": RouteGuard("R-27", Requirement.COUNCIL, mutation=True),
    "R-28": RouteGuard("R-28", Requirement.COUNCIL, navigation=True),
    "R-29": RouteGuard("R-29", Requirement.COUNCIL, mutation=True),
    "R-30": RouteGuard("R-30", Requirement.COUNCIL, mutation=True),
    "R-31": RouteGuard("R-31", Requirement.COUNCIL_OR_ADMINISTRATOR, navigation=True),
    "R-32": RouteGuard(
        "R-32", Requirement.ADMINISTRATOR, navigation=True, continuity_allowed=True
    ),
    "R-33": RouteGuard(
        "R-33", Requirement.ADMINISTRATOR, mutation=True, continuity_allowed=True
    ),
    "R-34": RouteGuard(
        "R-34", Requirement.ADMINISTRATOR, mutation=True, continuity_allowed=True
    ),
    "R-35": RouteGuard(
        "R-35", Requirement.SESSION, navigation=True, continuity_allowed=True
    ),
    "R-36": RouteGuard("R-36", Requirement.SESSION, navigation=True),
    "R-37": RouteGuard("R-37", Requirement.SESSION, mutation=True),
    "R-38": RouteGuard("R-38", Requirement.FULL_ADMINISTRATOR, mutation=True),
}

FORM_CONTENT_TYPE = "application/x-www-form-urlencoded"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class _Refused(Exception):
    """A response the preamble produced. Carried rather than returned.

    The handlers below are `async` FastAPI callables, and a preamble that
    returned `Response | tuple[...]` would make every one of them start with an
    `isinstance` check. Raising keeps the successful path linear, which is the
    path a reviewer has to be able to read.
    """

    def __init__(self, response: Response) -> None:
        super().__init__("refused")
        self.response = response


def register(app: FastAPI, composition, authority) -> None:
    """Bind the P3.2 routes to **this** composition and **this** graph, once.

    Both are closed over rather than dereferenced from `app.state` per request,
    for the reason `RequestAuthority` states: `app.state` is an ordinary mutable
    namespace, and a per-request read of it is one more route to a provider,
    engine, origin, cookie or key other than the ones `create_app()` accepted.
    """
    settings = authority.settings

    # -- the chain, once ---------------------------------------------------
    async def _preamble(request: Request, guard: RouteGuard):
        """Route contract §2.1, steps 1 to 6, in the contract's order. Once.

        The order is the whole of this function, so it is written out rather than
        described:

        | # | Step | Where |
        |---|---|---|
        | 1 | session resolution | `_open` → `open_request()` |
        | 2 | origin validation, for mutations | `_require_origin` |
        | 3 | CSRF validation, for cookie-authenticated mutations | `csrf.verify` |
        | 4 | current capability resolution, including any provider refresh | `_observe_membership` → `_close` |
        | 5 | capability decision | `authorize` |
        | 6 | object authorization | inside the handler's own transaction |
        | 7 | application service | the handler |

        **Steps 2 and 3 used to run after step 4.** `enter()` performed the
        membership/provider refresh and the capability decision, and
        `enter_mutation()` then parsed the form and verified the synchronizer
        token on top of the value it returned. A mutation with a missing or
        forged CSRF token therefore reached Discord over the network, wrote a
        membership projection row, resolved capability and took an authorization
        decision before anything looked at the token — so a cross-site request
        from a logged-in Council member's browser was cheap to make and drove
        real provider I/O and a real write, and the CSRF refusal it eventually
        received was the *last* thing that happened rather than the first.

        Now nothing between the session and the token check touches the network
        or reads anything authorization-dependent: an invalid token is refused
        with zero provider calls, zero service calls, zero state changes and no
        success audit event, for an otherwise-authorized caller and an
        unauthorized one alike.

        Returns `(gate, context, form)`; `form` is the parsed body for a mutation
        and `None` for a read. Raises `_Refused` carrying the response otherwise.
        """
        # -- 1. session resolution ----------------------------------------
        token = request.cookies.get(settings.session.cookie_name)
        try:
            gate = await run_in_threadpool(_open, composition, settings, token)
        except SessionAbsent:
            raise _Refused(_unauthenticated(guard)) from None
        except WebRefusal as refusal:
            # Step 1 can refuse for a reason that is not "no session": an account
            # holding two active identities for one provider is an ambiguity the
            # platform will not resolve, and it arrives here as `ServiceDegraded`.
            # Without this branch it escaped the preamble and became a `500` — the
            # opposite of failing closed, since a `500` tells the caller nothing and
            # tells the operator only that something threw.
            raise _Refused(_refusal_response(request, refusal, guard)) from None

        form = None
        if guard.mutation:
            # -- 2. origin validation --------------------------------------
            # Cheaper than a network call and cheaper than a parse, and the
            # contract puts it first: a cross-origin mutation is refused without
            # asking Discord anything and without reading a byte of the body.
            _require_origin(request)
            _require_form_content_type(request)

            # -- 3. CSRF validation ----------------------------------------
            # Every session in Phase 3 is a cookie session, so every mutation is
            # a cookie-authenticated mutation and every one of them passes here.
            # `gate.session_id` is all the token is bound to, and step 1 already
            # produced it — which is why this can precede step 4 rather than
            # depending on it.
            form = await request.form()
            presented = form.get("csrf_token") or request.headers.get("x-csrf-token")
            if not csrf.verify(settings.csrf_key, gate.session_id, presented):
                raise _Refused(
                    JSONResponse(
                        {"error": RefusalCode.CSRF_INVALID.value}, status_code=403
                    )
                )

        # -- 4. current capability resolution, including provider refresh ---
        # The provider call happens **between** the two transactions, never
        # inside one: a database connection held open across a network call to
        # Discord is a connection held for as long as Discord takes to answer.
        # Moving CSRF ahead of this did not change that — `_open` commits before
        # the token is examined, and `_close` opens a new transaction after it.
        context = gate.context
        if gate.refresh is not None:
            observation = await _observe_membership(composition, gate)
            try:
                context = await run_in_threadpool(
                    _close,
                    composition,
                    gate,
                    observation,
                    settings,
                    guard.mutation,
                )
            except WebRefusal as refusal:
                raise _Refused(_refusal_response(request, refusal, guard)) from None

        # -- 5. capability decision ----------------------------------------
        try:
            authorize(context, guard)
        except WebRefusal as refusal:
            raise _Refused(_refusal_response(request, refusal, guard)) from None
        return gate, context, form

    async def enter(request: Request, guard: RouteGuard):
        """The preamble for a read. `guard.mutation` is `False`, so no form is parsed."""
        gate, context, _form = await _preamble(request, guard)
        return gate, context

    async def enter_mutation(request: Request, guard: RouteGuard):
        """The preamble for a mutation, returning the body it already had to parse.

        The parse belongs to step 3 rather than to the handler: the synchronizer
        token arrives in the body, so verifying it before step 4 means reading
        the body before step 4, and handing the parsed result back is what stops
        a handler parsing it a second time.
        """
        gate, context, form = await _preamble(request, guard)
        # A read guard reaching here would be a mutation handler whose row of
        # `GUARDS` says otherwise, and `form` would be `None` — a `TypeError`
        # three lines later in the handler rather than an unchecked token. Made
        # explicit so the failure names the cause.
        if form is None:  # pragma: no cover - a guard-table defect, not a request
            raise RuntimeError(
                f"{guard.route} is handled as a mutation but its guard is not one"
            )
        return gate, context, form

    def _require_origin(request: Request) -> None:
        if not authority.origin_is_ours(request):
            raise _Refused(
                JSONResponse(
                    {"error": RefusalCode.ORIGIN_INVALID.value}, status_code=403
                )
            )

    def _require_form_content_type(request: Request) -> None:
        declared = (request.headers.get("content-type") or "").split(";", 1)[0].strip()
        if declared != FORM_CONTENT_TYPE:
            raise _Refused(
                JSONResponse({"error": "unsupported_media_type"}, status_code=415)
            )

    def _unauthenticated(guard: RouteGuard) -> Response:
        """`303` for a `GET` navigation, `401` for everything else (§2.3).

        A redirect for a mutation would be a silent no-op: the browser would
        follow it, render a login page, and the caller would have no way to tell
        that their change was never applied.
        """
        if guard.navigation:
            return RedirectResponse("/v1/login", status_code=303)
        return JSONResponse(
            {"error": RefusalCode.NOT_AUTHENTICATED.value}, status_code=401
        )

    def _refusal_response(
        request: Request, refusal: WebRefusal, guard: RouteGuard
    ) -> Response:
        if refusal.status == 503:
            return authority.render(
                request,
                "degraded.html",
                view=ServiceDegradedView(
                    state="error",
                    reason=DeniedReason(DenialCategory.SERVICE_DEGRADED),
                    subsystem="identity_provider",
                    grace_expired=True,
                    correlation=Correlation(refusal.correlation_id),
                ),
                status_code=503,
            )
        if isinstance(refusal, NotAMember) and guard.navigation:
            return authority.render(
                request,
                "non_member.html",
                view=NonMemberView(
                    state="denied",
                    reason=DeniedReason(DenialCategory.NOT_A_MEMBER),
                    guild_display_name="Freedom Blades",
                    checked_at=Instant.of(utcnow()),
                    correlation=Correlation(refusal.correlation_id),
                ),
                status_code=403,
            )
        if guard.navigation:
            return _denied(request, refusal)
        return JSONResponse({"error": refusal.code.value}, status_code=refusal.status)

    def _denied(request: Request, refusal: WebRefusal) -> HTMLResponse:
        """VM-22. A state and a closed-vocabulary category, and nothing else.

        **No correlation id**, deliberately (TC-OBJ-07) — and, from the accepted
        D-03 correction of 2026-08-19, no field that could carry one. This used to
        hand `denied.html` a `NonMemberView` (VM-02) with an empty guild name, an
        empty `Instant` and the nil UUID: the rendered bytes were right, but only
        because the template did not print three fields it was given, and P3.4
        rewrites that template. `DeniedView` has the two fields the page may show
        and no others, so byte-identity between an unreachable object's `404` and
        an absent object's `404` is a property of the type rather than of a
        template author's memory.
        """
        return authority.render(
            request,
            "denied.html",
            view=DeniedView(
                state="denied",
                reason=DeniedReason(_category(refusal)),
            ),
            status_code=refusal.status,
        )

    def _conflict(request: Request, refusal: WebRefusal, current=None) -> HTMLResponse:
        return authority.render(
            request,
            "conflict.html",
            view=ConflictView(
                state="stale",
                conflict="stale_version",
                current=current,
                correlation=Correlation(refusal.correlation_id),
            ),
            status_code=409,
        )

    def unit(work):
        """One unit of work, one transaction, on a worker thread."""

        def run():
            with composition.engine.begin() as connection:
                return work(composition.services(connection))

        return run_in_threadpool(run)

    # -- R-20 --------------------------------------------------------------
    @app.get("/v1/characters", name="my_characters")
    async def my_characters(request: Request) -> Response:
        """R-20. VM-05. No pagination, no audit: a read of one's own characters."""
        try:
            _gate, context = await enter(request, GUARDS["R-20"])
        except _Refused as refused:
            return refused.response
        view = await unit(lambda services: services.characters.my_characters(context))
        return authority.render(request, "my_characters.html", view=view, status_code=200)

    # -- R-21 --------------------------------------------------------------
    @app.get("/v1/characters/{character_id}", name="character_detail")
    async def character_detail(request: Request, character_id: str) -> Response:
        """R-21. Object authorization is **below** this handler, inside the read.

        A malformed UUID is answered exactly as an unreachable one: parsing it
        here and answering `404` keeps a caller from distinguishing "not a UUID"
        from "not yours" from "does not exist".
        """
        guard = GUARDS["R-21"]
        try:
            _gate, context = await enter(request, guard)
        except _Refused as refused:
            return refused.response
        try:
            identifier = UUID(character_id)
        except ValueError:
            return _denied(request, WebRefusal(RefusalCode.OBJECT_NOT_REACHABLE, status=404))
        try:
            view = await unit(
                lambda services: services.characters.character_detail(context, identifier)
            )
        except WebRefusal as refusal:
            return _refusal_response(request, refusal, guard)
        return authority.render(
            request, "character_detail.html", view=view, status_code=200
        )

    # -- R-22 --------------------------------------------------------------
    @app.get("/v1/council/characters", name="council_character_index")
    async def council_character_index(request: Request) -> Response:
        guard = GUARDS["R-22"]
        try:
            _gate, context = await enter(request, guard)
        except _Refused as refused:
            return refused.response
        try:
            view = await unit(
                lambda services: services.characters.council_index(
                    context,
                    query=request.query_params.get("q"),
                    cursor_token=request.query_params.get("cursor"),
                    size=page_size(request.query_params.get("size")),
                )
            )
        except InvalidCursor as refusal:
            # N-64: refused, never silently reset to page one — a reset cursor
            # hides tampering behind a page that looks like it worked.
            return _refusal_response(request, refusal, guard)
        return authority.render(
            request, "council_characters.html", view=view, status_code=200
        )

    # -- R-23 --------------------------------------------------------------
    @app.get("/v1/council/characters/{character_id}/links", name="council_character_links")
    async def council_character_links(request: Request, character_id: str) -> Response:
        guard = GUARDS["R-23"]
        try:
            gate, context = await enter(request, guard)
        except _Refused as refused:
            return refused.response
        try:
            identifier = UUID(character_id)
        except ValueError:
            return _denied(request, WebRefusal(RefusalCode.OBJECT_NOT_REACHABLE, status=404))
        try:
            view = await unit(
                lambda services: services.characters.character_links(
                    context,
                    identifier,
                    cursor_token=request.query_params.get("cursor"),
                    csrf_token=gate.csrf_token,
                )
            )
        except WebRefusal as refusal:
            return _refusal_response(request, refusal, guard)
        return authority.render(
            request, "character_links.html", view=view, status_code=200
        )

    # -- R-24 --------------------------------------------------------------
    @app.get("/v1/council/identity-search", name="council_identity_search")
    async def council_identity_search(request: Request) -> Response:
        """R-24. A fragment, authorized exactly like a page.

        It does not rely on having been reached from the grant form, and the
        denial tests prove that by issuing the request without ever rendering
        one (route contract §2.2).
        """
        guard = GUARDS["R-24"]
        try:
            _gate, context = await enter(request, guard)
        except _Refused as refused:
            return refused.response
        raw = request.query_params.get("character_id")
        character_id = None
        if raw:
            try:
                character_id = UUID(raw)
            except ValueError:
                character_id = None
        view = await unit(
            lambda services: services.characters.identity_search(
                context,
                guild_id=settings.discord.guild_id,
                query=request.query_params.get("q"),
                character_id=character_id,
            )
        )
        return authority.render(
            request, "identity_search.html", view=view, status_code=200
        )

    # -- R-25 --------------------------------------------------------------
    @app.post("/v1/council/characters/{character_id}/links", name="council_link_grant")
    async def council_link_grant(request: Request, character_id: str) -> Response:
        guard = GUARDS["R-25"]
        try:
            _gate, context, form = await enter_mutation(request, guard)
        except _Refused as refused:
            return refused.response
        try:
            identifier = UUID(character_id)
        except ValueError:
            return JSONResponse(
                {"error": RefusalCode.OBJECT_NOT_REACHABLE.value}, status_code=404
            )
        correlation_id = uuid4()
        try:
            version = int(form.get("version") or "")
        except ValueError:
            return _validation(request, "version")
        subject = (form.get("subject") or "").strip()
        if not subject.isdigit():
            # A snowflake is a canonical decimal string. Anything else is not an
            # identity this platform recognises, and it is refused as input
            # rather than looked up.
            return _validation(request, "subject")

        try:
            await unit(
                lambda services: services.character_access.grant(
                    context=context,
                    character_id=identifier,
                    subject=subject,
                    access_kind=(form.get("access_kind") or "").strip(),
                    reason=form.get("reason") or "",
                    expected_version=version,
                    correlation_id=correlation_id,
                    now=utcnow(),
                )
            )
        except WebRefusal as refusal:
            return _mutation_refusal(request, refusal, guard)
        return RedirectResponse(
            f"/v1/council/characters/{identifier}/links", status_code=303
        )

    # -- R-26 --------------------------------------------------------------
    @app.post(
        "/v1/council/characters/{character_id}/links/{access_id}/revoke",
        name="council_link_revoke",
    )
    async def council_link_revoke(
        request: Request, character_id: str, access_id: str
    ) -> Response:
        guard = GUARDS["R-26"]
        try:
            _gate, context, form = await enter_mutation(request, guard)
        except _Refused as refused:
            return refused.response
        try:
            identifier, access = UUID(character_id), UUID(access_id)
            version = int(form.get("version") or "")
        except ValueError:
            return JSONResponse(
                {"error": RefusalCode.OBJECT_NOT_REACHABLE.value}, status_code=404
            )
        try:
            await unit(
                lambda services: services.character_access.revoke(
                    context=context,
                    character_id=identifier,
                    access_id=access,
                    reason=form.get("reason") or "",
                    expected_version=version,
                    correlation_id=uuid4(),
                    now=utcnow(),
                )
            )
        except WebRefusal as refusal:
            return _mutation_refusal(request, refusal, guard)
        return RedirectResponse(
            f"/v1/council/characters/{identifier}/links", status_code=303
        )

    # -- R-27 --------------------------------------------------------------
    @app.post(
        "/v1/council/characters/{character_id}/links/{access_id}/default",
        name="council_link_set_default",
    )
    async def council_link_set_default(
        request: Request, character_id: str, access_id: str
    ) -> Response:
        guard = GUARDS["R-27"]
        try:
            _gate, context, form = await enter_mutation(request, guard)
        except _Refused as refused:
            return refused.response
        try:
            identifier, access = UUID(character_id), UUID(access_id)
            version = int(form.get("version") or "")
        except ValueError:
            return JSONResponse(
                {"error": RefusalCode.OBJECT_NOT_REACHABLE.value}, status_code=404
            )
        try:
            await unit(
                lambda services: services.character_access.set_default(
                    context=context,
                    character_id=identifier,
                    access_id=access,
                    reason=form.get("reason") or "",
                    expected_version=version,
                    correlation_id=uuid4(),
                    now=utcnow(),
                )
            )
        except WebRefusal as refusal:
            return _mutation_refusal(request, refusal, guard)
        return RedirectResponse(
            f"/v1/council/characters/{identifier}/links", status_code=303
        )

    # -- R-28 --------------------------------------------------------------
    @app.get("/v1/council/identity-migration", name="council_identity_migration")
    async def council_identity_migration(request: Request) -> Response:
        guard = GUARDS["R-28"]
        try:
            gate, context = await enter(request, guard)
        except _Refused as refused:
            return refused.response
        try:
            view = await unit(
                lambda services: services.identity_migration.overview(
                    context,
                    cursor_token=request.query_params.get("cursor"),
                    csrf_token=gate.csrf_token,
                    size=page_size(request.query_params.get("size")),
                )
            )
        except WebRefusal as refusal:
            return _refusal_response(request, refusal, guard)
        return authority.render(
            request, "identity_migration.html", view=view, status_code=200
        )

    # -- R-29 --------------------------------------------------------------
    @app.post(
        "/v1/council/identity-migration/{proposal_id}/confirm",
        name="council_identity_migration_confirm",
    )
    async def council_identity_migration_confirm(
        request: Request, proposal_id: str
    ) -> Response:
        """R-29. One transaction: the link, the decision and both audit events.

        Migration contract §7.2 as the maintainer ruled it (change-log entry
        C-P3.2-A, OD-46): **a confirmation is the activation.** The
        `character_access` row is created here, through the same
        `CharacterAccessService.grant()` R-25 uses, under the Council capability
        `enter_mutation` resolved live for *this* request — not a durable claim
        recorded earlier, and not anything the browser sent.

        The request carries three things and no more: the proposal id in the
        path, a bounded non-blank reason, and the character's optimistic
        `version`. The subject, the platform account, the access kind and the
        granting authority are all resolved server-side, and none of them has a
        parameter here to arrive through — a body that names a subject, an
        account, an actor, an access kind or an authority is a body whose extra
        fields are read by nothing.

        `version` is the same field R-25's grant form carries, and it is here
        because a confirmation now changes the character. A page rendered before
        somebody else's change must not be applied on top of it: the conditional
        bump inside `grant()` refuses `409` with the current state (VM-19), and
        so does `decide()` when two Council members act in the same instant.
        """
        guard = GUARDS["R-29"]
        try:
            _gate, context, form = await enter_mutation(request, guard)
        except _Refused as refused:
            return refused.response
        try:
            identifier = UUID(proposal_id)
        except ValueError:
            return JSONResponse(
                {"error": RefusalCode.OBJECT_NOT_REACHABLE.value}, status_code=404
            )
        try:
            version = int(form.get("version") or "")
        except ValueError:
            return _validation(request, "version")
        try:
            await unit(
                lambda services: services.identity_migration.confirm(
                    context=context,
                    proposal_id=identifier,
                    reason=form.get("reason") or "",
                    expected_version=version,
                    correlation_id=uuid4(),
                    now=utcnow(),
                )
            )
        except WebRefusal as refusal:
            return _mutation_refusal(request, refusal, guard)
        return RedirectResponse("/v1/council/identity-migration", status_code=303)

    # -- R-30 --------------------------------------------------------------
    @app.post(
        "/v1/council/identity-migration/{proposal_id}/reject",
        name="council_identity_migration_reject",
    )
    async def council_identity_migration_reject(
        request: Request, proposal_id: str
    ) -> Response:
        guard = GUARDS["R-30"]
        try:
            _gate, context, form = await enter_mutation(request, guard)
        except _Refused as refused:
            return refused.response
        try:
            identifier = UUID(proposal_id)
        except ValueError:
            return JSONResponse(
                {"error": RefusalCode.OBJECT_NOT_REACHABLE.value}, status_code=404
            )
        try:
            await unit(
                lambda services: services.identity_migration.reject(
                    context=context,
                    proposal_id=identifier,
                    reason=form.get("reason") or "",
                    correlation_id=uuid4(),
                    now=utcnow(),
                )
            )
        except WebRefusal as refusal:
            return _mutation_refusal(request, refusal, guard)
        return RedirectResponse("/v1/council/identity-migration", status_code=303)

    # -- R-31 --------------------------------------------------------------
    @app.get("/v1/council/field-profile", name="council_field_profile")
    async def council_field_profile(request: Request) -> Response:
        guard = GUARDS["R-31"]
        try:
            _gate, context = await enter(request, guard)
        except _Refused as refused:
            return refused.response
        view = await unit(lambda services: services.characters.field_profile(context))
        return authority.render(request, "field_profile.html", view=view, status_code=200)

    # -- R-32 --------------------------------------------------------------
    @app.get("/v1/admin/role-capabilities", name="admin_role_capabilities")
    async def admin_role_capabilities(request: Request) -> Response:
        guard = GUARDS["R-32"]
        try:
            gate, context = await enter(request, guard)
        except _Refused as refused:
            return refused.response
        view = await unit(
            lambda services: _role_capability_view(services, context, gate.csrf_token, settings)
        )
        return authority.render(
            request, "role_capabilities.html", view=view, status_code=200
        )

    # -- R-33 --------------------------------------------------------------
    @app.post("/v1/admin/role-capabilities", name="admin_role_capability_create")
    async def admin_role_capability_create(request: Request) -> Response:
        """R-33. N-67's allowlist is refused here, in the service, and by the database.

        This handler enforces none of it. The service refuses a disallowed
        capability before any row is read or written and records the attempt;
        the check constraint refuses the insert regardless of what the service
        decided. Three controls, and this route is not one of them — which is
        why TC-BG-05b can issue the request without rendering R-32 and still get
        `403`.
        """
        guard = GUARDS["R-33"]
        try:
            _gate, context, form = await enter_mutation(request, guard)
        except _Refused as refused:
            return refused.response
        role_id = (form.get("role_id") or "").strip()
        if not role_id.isdigit() or int(role_id) <= 0:
            return _validation(request, "role_id")
        capability = _capability_or_none(form.get("capability"))
        if capability is None:
            return _validation(request, "capability")
        reason = form.get("reason") or ""
        if not reason.strip():
            return _validation(request, "reason")

        correlation_id = uuid4()

        def change(connection):
            services = composition.services(connection)
            return services.role_mappings.create(
                context=context,
                guild_id=settings.discord.guild_id,
                role_id=int(role_id),
                capability=capability,
                reason=reason,
                correlation_id=correlation_id,
            )

        try:
            await run_in_threadpool(run_mapping_change, composition.engine, change)
        except WebRefusal as refusal:
            return _mutation_refusal(request, refusal, guard)
        return RedirectResponse("/v1/admin/role-capabilities", status_code=303)

    # -- R-34 --------------------------------------------------------------
    @app.post(
        "/v1/admin/role-capabilities/{mapping_id}/revoke",
        name="admin_role_capability_revoke",
    )
    async def admin_role_capability_revoke(request: Request, mapping_id: str) -> Response:
        guard = GUARDS["R-34"]
        try:
            _gate, context, form = await enter_mutation(request, guard)
        except _Refused as refused:
            return refused.response
        try:
            identifier = UUID(mapping_id)
            version = int(form.get("version") or "")
        except ValueError:
            return JSONResponse(
                {"error": RefusalCode.OBJECT_NOT_REACHABLE.value}, status_code=404
            )
        reason = form.get("reason") or ""
        if not reason.strip():
            return _validation(request, "reason")
        correlation_id = uuid4()

        def change(connection):
            services = composition.services(connection)
            return services.role_mappings.revoke(
                context=context,
                mapping_id=identifier,
                expected_version=version,
                reason=reason,
                correlation_id=correlation_id,
                now=utcnow(),
            )

        try:
            await run_in_threadpool(run_mapping_change, composition.engine, change)
        except WebRefusal as refusal:
            return _mutation_refusal(request, refusal, guard)
        return RedirectResponse("/v1/admin/role-capabilities", status_code=303)

    # -- R-38 --------------------------------------------------------------
    @app.post(
        "/v1/admin/role-capabilities/{mapping_id}/ratify",
        name="admin_role_capability_ratify",
    )
    async def admin_role_capability_ratify(request: Request, mapping_id: str) -> Response:
        """R-38. The one exit from emergency-derived authority, and one-way.

        `FULL_ADMINISTRATOR` demands `discord_oauth` **and** scope `full`, so a
        `BG` or `AC` caller is refused by the guard before this body runs. A
        `403` here during an incident is the boundary, not a defect to work
        around: ratification waits until an administrator can authenticate
        normally.
        """
        guard = GUARDS["R-38"]
        try:
            _gate, context, form = await enter_mutation(request, guard)
        except _Refused as refused:
            return refused.response
        try:
            identifier = UUID(mapping_id)
            version = int(form.get("version") or "")
        except ValueError:
            return JSONResponse(
                {"error": RefusalCode.OBJECT_NOT_REACHABLE.value}, status_code=404
            )
        reason = form.get("reason") or ""
        if not reason.strip():
            return _validation(request, "reason")
        correlation_id = uuid4()

        def change(connection):
            services = composition.services(connection)
            return services.role_mappings.ratify(
                context=context,
                mapping_id=identifier,
                expected_version=version,
                reason=reason,
                correlation_id=correlation_id,
                now=utcnow(),
            )

        try:
            await run_in_threadpool(run_mapping_change, composition.engine, change)
        except WebRefusal as refusal:
            return _mutation_refusal(request, refusal, guard)
        return RedirectResponse("/v1/admin/role-capabilities", status_code=303)

    # -- R-35 --------------------------------------------------------------
    @app.get("/v1/account/identities", name="account_identities")
    async def account_identities(request: Request) -> Response:
        guard = GUARDS["R-35"]
        try:
            gate, context = await enter(request, guard)
        except _Refused as refused:
            return refused.response
        view = await unit(
            lambda services: _identities_view(services, context, gate)
        )
        return authority.render(
            request, "account_identities.html", view=view, status_code=200
        )

    # -- R-36 --------------------------------------------------------------
    @app.get("/v1/account/identities/link/start", name="account_identity_link_start")
    async def account_identity_link_start(request: Request) -> Response:
        """R-36. The boundary is real and answers `no_additional_provider`.

        Phase 3 has exactly one ordinary provider, so there is nothing to
        redirect to. The route exists so the linking flow's rules — strong
        reauthentication (N-16), or the separately audited Council /
        Server-Administrator recovery decision — are refused by something rather
        than being absent until a later package invents them. A second provider
        package is what makes this a redirect, and that is its work, not this
        one's.
        """
        guard = GUARDS["R-36"]
        try:
            gate, context = await enter(request, guard)
        except _Refused as refused:
            return refused.response
        view = await unit(
            lambda services: _identities_view(services, context, gate, state="denied")
        )
        return authority.render(
            request, "account_identities.html", view=view, status_code=200
        )

    # -- R-37 --------------------------------------------------------------
    @app.post("/v1/account/identities/{identity_id}/unlink", name="account_identity_unlink")
    async def account_identity_unlink(request: Request, identity_id: str) -> Response:
        guard = GUARDS["R-37"]
        try:
            _gate, context, _form = await enter_mutation(request, guard)
        except _Refused as refused:
            return refused.response
        try:
            identifier = UUID(identity_id)
        except ValueError:
            return JSONResponse(
                {"error": RefusalCode.OBJECT_NOT_REACHABLE.value}, status_code=404
            )
        try:
            await unit(
                lambda services: services.account_identities.unlink(
                    context=context,
                    identity_id=identifier,
                    correlation_id=uuid4(),
                    now=utcnow(),
                )
            )
        except WebRefusal as refusal:
            return _mutation_refusal(request, refusal, guard)
        return RedirectResponse("/v1/account/identities", status_code=303)

    # -- shared rendering --------------------------------------------------
    def _validation(request: Request, field: str) -> HTMLResponse:
        from application.web.view_models import FieldError, ValidationView

        return authority.render(
            request,
            "validation.html",
            view=ValidationView(
                state="invalid", form=None, errors=(FieldError(field=field, code="required"),)
            ),
            status_code=422,
        )

    def _mutation_refusal(
        request: Request, refusal: WebRefusal, guard: RouteGuard
    ) -> Response:
        if refusal.status == 409:
            return _conflict(request, refusal)
        if refusal.status == 422:
            return _validation(request, "reason")
        return JSONResponse({"error": refusal.code.value}, status_code=refusal.status)


async def _observe_membership(composition, gate):
    """Ask the provider what this person's membership is **now**, outside any transaction.

    Returns the verified identity, or `None` when the provider could not be
    reached or refused. `None` is *no observation* and never an absence: the
    caller records nothing, so a rate-limit storm cannot write `is_member =
    false` and revoke a guild (TC-OUT-04).
    """
    from application.web.crypto import token_grant_aad

    grant = gate.refresh.grant
    try:
        access_token = composition.envelope.open(
            grant.access,
            aad=token_grant_aad(
                grant.grant_id, grant.external_identity_id, grant.access.key_version
            ),
        ).decode("utf-8")
    except Exception:  # noqa: BLE001 - an unopenable grant is one outcome
        return None
    tokens = ProviderTokens(
        provider_key=composition.provider.provider_key,
        access_token=access_token,
        refresh_token=None,
        # Both values are the ones this platform stored, not ones invented to
        # fill the shape: a token result that could say something nobody
        # observed is the class of value the provider binding exists to refuse.
        expires_at=grant.access_expires_at,
        scopes=grant.scopes,
    )
    try:
        return await composition.provider.verify(tokens)
    except (ProviderUnavailable, ProviderRefused):
        return None


def _open(composition, settings, token):
    """`open_request` inside its own transaction, on a worker thread.

    The transaction is opened here rather than inside `open_request` because
    transaction boundaries belong to the adapter: the application layer states
    the rule that a change and its audit share one transaction, and it can only
    do that if it is never the thing that opens one.
    """
    with composition.engine.begin() as connection:
        return open_request(
            services=composition.services(connection),
            settings=settings,
            token=token,
            now=utcnow(),
        )


def _close(composition, gate, observation, settings, mutation):
    with composition.engine.begin() as connection:
        return close_request(
            services=composition.services(connection),
            settings=settings,
            gate=gate,
            observation=observation,
            now=utcnow(),
            mutation=mutation,
        )


def _category(refusal: WebRefusal) -> DenialCategory:
    mapping = {
        RefusalCode.NOT_AUTHENTICATED: DenialCategory.NOT_AUTHENTICATED,
        RefusalCode.NOT_A_MEMBER: DenialCategory.NOT_A_MEMBER,
        RefusalCode.INSUFFICIENT_CAPABILITY: DenialCategory.INSUFFICIENT_CAPABILITY,
        RefusalCode.EMERGENCY_SCOPE_REFUSED: DenialCategory.EMERGENCY_SESSION_RESTRICTED,
        RefusalCode.EMERGENCY_SURFACE_REFUSED: DenialCategory.EMERGENCY_SESSION_RESTRICTED,
        RefusalCode.SERVICE_DEGRADED: DenialCategory.SERVICE_DEGRADED,
    }
    return mapping.get(refusal.code, DenialCategory.NOT_AVAILABLE)


def _capability_or_none(raw):
    try:
        capability = ActorCapability((raw or "").strip())
    except ValueError:
        return None
    return capability if capability in MAPPABLE_CAPABILITIES else None


def _role_capability_view(services, context, csrf_token, settings) -> RoleCapabilityView:
    """VM-12 from the live mapping rows. Rendering hints, never controls."""
    guild_id = settings.discord.guild_id
    rows = services.mappings.rows_for_guild(guild_id, limit=ROLE_MAPPING_BOUND)
    continuity = context.administrator_scope is AdministratorScope.EMERGENCY_CONTINUITY
    labels = services.accounts.labels_for(
        [row["created_by_account_id"] for row in rows]
        + [row["ratified_by_account_id"] for row in rows]
    )
    mappings, _ = bounded_tuple(
        (
            RoleMappingRow(
                mapping_id=row["id"],
                role_snowflake=str(row["role_id"]),
                capability=ActorCapability(row["capability"]),
                protected=row["protected"],
                provenance=row["provenance"],
                # False whenever protected, and — under continuity scope — for
                # every capability outside N-67. The route refuses regardless.
                revocable=(
                    not row["protected"]
                    and (
                        not continuity
                        or row["capability"] == ActorCapability.PLATFORM_ADMINISTRATOR.value
                    )
                ),
                ratifiable=(
                    row["provenance"] == MappingProvenance.EMERGENCY_CONTINUITY.value
                    and not continuity
                ),
                created_by=Actor(
                    account_id=row["created_by_account_id"],
                    label=SafeText.bounded(
                        labels.get(row["created_by_account_id"])
                        or f"Account {str(row['created_by_account_id'])[:8]}",
                        80,
                    ),
                    capability=ActorCapability.PLATFORM_ADMINISTRATOR,
                ),
                created_under_auth_method=row["created_under_auth_method"],
                created_at=Instant.of(row["created_at"]),
                version=row["version"],
                ratified_at=(
                    Instant.of(row["ratified_at"]) if row["ratified_at"] else None
                ),
            )
            for row in rows
        ),
        ROLE_MAPPING_BOUND,
    )
    return RoleCapabilityView(
        state="ready" if mappings else "empty",
        guild_id=str(guild_id),
        administrator_scope=context.administrator_scope.value,
        mappings=mappings,
        # N-67-filtered. When the caller is continuity-scoped this holds exactly
        # `platform_administrator`, and R-33 refuses everything else whether or
        # not this page was ever fetched.
        available_capabilities=(
            (ActorCapability.PLATFORM_ADMINISTRATOR,)
            if continuity
            else tuple(sorted(MAPPABLE_CAPABILITIES, key=lambda c: c.value))
        ),
        csrf_token=csrf_token,
        unratified_count=sum(
            1
            for row in rows
            if row["provenance"] == MappingProvenance.EMERGENCY_CONTINUITY.value
        ),
        scope_notice_code="emergency_continuity_allowlist" if continuity else None,
    )


def _identities_view(services, context, gate, state: str = "ready"):
    subject = services.accounts.discord_subject(context.account_id)
    view = services.account_identities.overview(
        context, current_subject=subject, state=state
    )
    from dataclasses import replace

    return replace(view, csrf_token=gate.csrf_token)


__all__ = ["GUARDS", "P3_2_ROUTE_INVENTORY", "register"]
