"""R-40 to R-49: the P3.3 route surface, and nothing else.

The same shape as `portal_routes.py`, deliberately, and for the same reasons: one
`GUARDS` table transcribing the accepted matrix once, one `_preamble` performing
the contract's steps in the contract's order, and handlers that establish the
caller, parse input, invoke **one** use case and render its typed result.

## What is different here, and why

**Nothing in a request does the work.** R-42 and R-46 enqueue; R-43 and R-44
read. A handler that produced a preview would be a handler that holds the process
for ~9.6 seconds of GIL-bound parsing, which is the measured constraint the whole
package exists to respect (plan §12 Phase 3, change-log C-11).

**Per-route body bounds.** The contract's `Body` column gives R-41, R-42 and R-45
4 KiB and R-46 8 KiB. These are *tighter* than N-19's 1 MiB, which the middleware
already applies before routing; the guard's bound can only narrow it. A form that
needs more than eight kilobytes is not one of these forms.

**Polling is a read with no audit effect.** R-44 answers a bounded fragment and a
`Retry-After` honouring N-22. Auditing a poll would flood the append-only table
with the fact that somebody looked at their own guild's operational state, at up
to one event every two seconds per watcher, forever.

**A member learns nothing from a job id.** `403` is answered on capability
*before* the job row is read — the guard runs in the preamble and the repository
is not touched until the handler — so a job UUID is worth nothing to a member and
the property holds without relying on timing (route contract §6.3, F-2).
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.concurrency import run_in_threadpool

from application.web import csrf
from application.web.access_control import (
    Requirement,
    RouteGuard,
    SessionAbsent,
    authorize,
    close_request,
    open_request,
)
from application.web.audit_search import FilterBounds
from application.web.errors import NotAMember, RefusalCode, WebRefusal
from application.web.jobs import ConfirmationRefused, JobState
from application.web.pagination import InvalidCursor, page_size
from application.web.view_models import (
    ConflictView,
    Correlation,
    DeniedReason,
    DenialCategory,
    DeniedView,
    FieldError,
    Instant,
    NonMemberView,
    ServiceDegradedView,
    ValidationView,
)

#: The closed P3.3 inventory, by contract identifier. Merged into `app.py`'s
#: `ROUTE_INVENTORY` so `TC-STRUCT-01` still asserts **one** registered set
#: against the parsed contract document.
P3_3_ROUTE_INVENTORY: dict[str, tuple[str, str]] = {
    "R-40": ("GET", "/v1/council/snapshots"),
    "R-41": ("POST", "/v1/admin/snapshots/{snapshot_id}/folder"),
    "R-42": ("POST", "/v1/council/snapshots/{snapshot_id}/preview-jobs"),
    "R-43": ("GET", "/v1/council/jobs/{job_id}"),
    "R-44": ("GET", "/v1/council/jobs/{job_id}/status"),
    "R-45": ("POST", "/v1/council/jobs/{job_id}/cancel"),
    "R-46": ("POST", "/v1/council/jobs/{job_id}/apply"),
    "R-47": ("GET", "/v1/council/imports/{import_id}"),
    "R-48": ("GET", "/v1/audit"),
    "R-49": ("GET", "/v1/audit/results"),
}

KIB = 1024

#: Route contract §6.2, as data.
#:
#: **`continuity_allowed` is `True` on exactly two rows.** N-65 states it in as
#: many words: a continuity-scoped session may reach only the identity/capability
#: administration and audit-read surface, and *every import, preview, apply and
#: folder-selection route refuses it*. So R-40 through R-47 are all `False`,
#: including R-41 — an emergency administrator may not choose a folder, because
#: emergency access exists to restore administrative continuity rather than to
#: operate imports.
GUARDS: dict[str, RouteGuard] = {
    "R-40": RouteGuard(
        "R-40", Requirement.COUNCIL_OR_ADMINISTRATOR, navigation=True
    ),
    "R-41": RouteGuard(
        "R-41", Requirement.ADMINISTRATOR, mutation=True, body_bytes=4 * KIB
    ),
    "R-42": RouteGuard(
        "R-42", Requirement.COUNCIL, mutation=True, body_bytes=4 * KIB
    ),
    "R-43": RouteGuard("R-43", Requirement.COUNCIL, navigation=True),
    # An HTMX fragment, so an absent session is `401` rather than a redirect: a
    # `303` swapped into a fragment target would render the login page inside the
    # job screen.
    "R-44": RouteGuard("R-44", Requirement.COUNCIL),
    "R-45": RouteGuard(
        "R-45", Requirement.COUNCIL, mutation=True, body_bytes=4 * KIB
    ),
    "R-46": RouteGuard(
        "R-46", Requirement.COUNCIL, mutation=True, body_bytes=8 * KIB
    ),
    "R-47": RouteGuard(
        "R-47", Requirement.COUNCIL_OR_ADMINISTRATOR, navigation=True
    ),
    "R-48": RouteGuard(
        "R-48", Requirement.AUDIT_READ, navigation=True, continuity_allowed=True
    ),
    "R-49": RouteGuard("R-49", Requirement.AUDIT_READ, continuity_allowed=True),
}

FORM_CONTENT_TYPE = "application/x-www-form-urlencoded"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class _Refused(Exception):
    """A response the preamble produced, carried rather than returned."""

    def __init__(self, response: Response) -> None:
        super().__init__("refused")
        self.response = response


def register(app: FastAPI, composition, authority) -> None:
    """Bind R-40 to R-49 to **this** composition and **this** graph, once."""
    settings = authority.settings

    # -- the chain, once ---------------------------------------------------
    async def _preamble(request: Request, guard: RouteGuard):
        """Route contract §2.1, steps 1 to 6, in the contract's order.

        Identical in order and in reasoning to `portal_routes._preamble`, with
        the one addition this package's contract rows carry: the per-route body
        bound is checked with the origin, **before** the body is read and before
        anything authorization-dependent happens.
        """
        # -- 1. session resolution ----------------------------------------
        token = request.cookies.get(settings.session.cookie_name)
        try:
            gate = await run_in_threadpool(_open, composition, settings, token)
        except SessionAbsent:
            raise _Refused(_unauthenticated(guard)) from None
        except WebRefusal as refusal:
            raise _Refused(_refusal_response(request, refusal, guard)) from None

        form = None
        if guard.mutation:
            # -- 2. origin, content type and this route's own body bound ----
            _require_origin(request)
            _require_form_content_type(request)
            _require_body_bound(request, guard)

            # -- 3. CSRF ---------------------------------------------------
            form = await request.form()
            presented = form.get("csrf_token") or request.headers.get("x-csrf-token")
            if not csrf.verify(settings.csrf_key, gate.session_id, presented):
                raise _Refused(
                    JSONResponse(
                        {"error": RefusalCode.CSRF_INVALID.value}, status_code=403
                    )
                )

        # -- 4. current capability resolution, including provider refresh ---
        context = gate.context
        if gate.refresh is not None:
            from adapters.web.portal_routes import _observe_membership

            observation = await _observe_membership(composition, gate)
            try:
                context = await run_in_threadpool(
                    _close, composition, gate, observation, settings, guard.mutation
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
        gate, context, _form = await _preamble(request, guard)
        return gate, context

    async def enter_mutation(request: Request, guard: RouteGuard):
        gate, context, form = await _preamble(request, guard)
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

    def _require_body_bound(request: Request, guard: RouteGuard) -> None:
        """The contract's `Body` column, refused **before** the body is read.

        A missing `Content-Length` is refused too, for the reason the middleware
        refuses it: a chunked upload with no declared length is precisely the
        shape that bypasses a limit applied to a header.
        """
        if guard.body_bytes is None:
            return
        declared = request.headers.get("content-length")
        if declared is None:
            raise _Refused(
                JSONResponse(
                    {"error": RefusalCode.BODY_TOO_LARGE.value}, status_code=411
                )
            )
        try:
            length = int(declared)
        except ValueError:
            raise _Refused(
                JSONResponse(
                    {"error": RefusalCode.BODY_TOO_LARGE.value}, status_code=413
                )
            ) from None
        if length > guard.body_bytes:
            raise _Refused(
                JSONResponse(
                    {"error": RefusalCode.BODY_TOO_LARGE.value}, status_code=413
                )
            )

    def _unauthenticated(guard: RouteGuard) -> Response:
        if guard.navigation:
            return RedirectResponse("/v1/login", status_code=303)
        return JSONResponse(
            {"error": RefusalCode.NOT_AUTHENTICATED.value}, status_code=401
        )

    def _refusal_response(
        request: Request, refusal: WebRefusal, guard: RouteGuard
    ) -> Response:
        if refusal.status == 503 and refusal.code is RefusalCode.SERVICE_DEGRADED:
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

        The `404` for a job or import this account cannot reach and the `404` for
        one that does not exist have to be byte-identical, and a correlation id
        differs per request — printing one would make the two distinguishable by
        exactly the amount it varies.

        **The carrier changed on 2026-08-19** (accepted D-03 correction, item
        D-03-6). This used to be a `NonMemberView` (VM-02) with an empty guild
        name, an empty `Instant` and the nil UUID; `DeniedView` simply has no such
        field to print, so the byte-identity above is enforced by the type rather
        than by `denied.html` continuing to ignore what it is handed.
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

    def _validation(request: Request, field: str, code: str = "required") -> HTMLResponse:
        return authority.render(
            request,
            "validation.html",
            view=ValidationView(
                state="invalid",
                form=None,
                errors=(FieldError(field=field, code=code),),
            ),
            status_code=422,
        )

    def unit(work):
        def run():
            with composition.engine.begin() as connection:
                return work(composition.services(connection))

        return run_in_threadpool(run)

    def _object_id(raw: str) -> UUID | None:
        """A malformed UUID is answered exactly as an unreachable one.

        Parsing it here and answering `404` keeps a caller from distinguishing
        "not a UUID" from "not yours" from "does not exist".
        """
        try:
            return UUID(raw)
        except ValueError:
            return None

    # -- R-40 --------------------------------------------------------------
    @app.get("/v1/council/snapshots", name="council_snapshots")
    async def council_snapshots(request: Request) -> Response:
        """R-40. VM-14. Council **and** administrator; the controls differ."""
        guard = GUARDS["R-40"]
        try:
            gate, context = await enter(request, guard)
        except _Refused as refused:
            return refused.response
        try:
            view = await unit(
                lambda services: services.snapshot_admin.snapshot_list(
                    context=context,
                    cursor_token=request.query_params.get("cursor"),
                    csrf_token=gate.csrf_token,
                    size=page_size(request.query_params.get("size")),
                )
            )
        except (InvalidCursor, WebRefusal) as refusal:
            return _refusal_response(request, refusal, guard)
        return authority.render(
            request, "council_snapshots.html", view=view, status_code=200
        )

    # -- R-41 --------------------------------------------------------------
    @app.post("/v1/admin/snapshots/{snapshot_id}/folder", name="admin_snapshot_folder")
    async def admin_snapshot_folder(request: Request, snapshot_id: str) -> Response:
        """R-41. Administrator-only, and the invalidation is atomic with it.

        Council alone is refused `403`: selecting a folder is not a game-policy
        act, and applying an import is not an operational one.
        """
        guard = GUARDS["R-41"]
        try:
            _gate, context, form = await enter_mutation(request, guard)
        except _Refused as refused:
            return refused.response
        identifier = _object_id(snapshot_id)
        if identifier is None:
            return JSONResponse(
                {"error": RefusalCode.OBJECT_NOT_REACHABLE.value}, status_code=404
            )
        folder_id = (form.get("folder_id") or "").strip()
        if not folder_id:
            return _validation(request, "folder_id")
        try:
            await unit(
                lambda services: services.snapshot_admin.select_folder(
                    context=context,
                    snapshot_id=identifier,
                    folder_id=folder_id,
                    now=utcnow(),
                )
            )
        except WebRefusal as refusal:
            return _mutation_refusal(request, refusal, guard)
        return RedirectResponse("/v1/council/snapshots", status_code=303)

    # -- R-42 --------------------------------------------------------------
    @app.post(
        "/v1/council/snapshots/{snapshot_id}/preview-jobs",
        name="council_preview_job_create",
    )
    async def council_preview_job_create(
        request: Request, snapshot_id: str
    ) -> Response:
        """R-42. Enqueues, then `303` to R-43 — never the result, which does not
        exist yet.

        A double-click with the same request identity returns the **existing**
        job's redirect rather than creating a second, which is what makes a
        double-click indistinguishable from a single click at the user's level
        while remaining one durable effect.
        """
        guard = GUARDS["R-42"]
        try:
            _gate, context, form = await enter_mutation(request, guard)
        except _Refused as refused:
            return refused.response
        identifier = _object_id(snapshot_id)
        if identifier is None:
            return JSONResponse(
                {"error": RefusalCode.OBJECT_NOT_REACHABLE.value}, status_code=404
            )
        # The nonce is what makes two *deliberate* previews distinct and two
        # submissions of the same form identical. A form that omits it is one
        # request whose identity the platform cannot establish, so it is refused
        # rather than given a fresh identity that would defeat the idempotency.
        nonce = (form.get("nonce") or "").strip()
        if not nonce:
            return _validation(request, "nonce")
        try:
            enqueued = await unit(
                lambda services: services.jobs.enqueue_preview(
                    context=context,
                    snapshot_id=identifier,
                    nonce=nonce,
                    now=utcnow(),
                )
            )
        except WebRefusal as refusal:
            return _mutation_refusal(request, refusal, guard)
        return RedirectResponse(
            f"/v1/council/jobs/{enqueued.job_id}", status_code=303
        )

    # -- R-43 --------------------------------------------------------------
    @app.get("/v1/council/jobs/{job_id}", name="council_job_page")
    async def council_job_page(request: Request, job_id: str) -> Response:
        """R-43. VM-15, the navigable page.

        A Council member who did not request the job may view it: Council reach
        is role-derived (OD-37), and import work is Council-wide business.
        """
        guard = GUARDS["R-43"]
        try:
            gate, context = await enter(request, guard)
        except _Refused as refused:
            return refused.response
        identifier = _object_id(job_id)
        if identifier is None:
            return _denied(
                request, WebRefusal(RefusalCode.OBJECT_NOT_REACHABLE, status=404)
            )
        try:
            view = await unit(
                lambda services: services.jobs.status(
                    context=context, job_id=identifier, csrf_token=gate.csrf_token
                )
            )
        except WebRefusal as refusal:
            return _refusal_response(request, refusal, guard)
        return authority.render(
            request, "job_status.html", view=view, status_code=200
        )

    # -- R-44 --------------------------------------------------------------
    @app.get("/v1/council/jobs/{job_id}/status", name="council_job_status")
    async def council_job_status(request: Request, job_id: str) -> Response:
        """R-44. The fragment R-43 polls, authorized exactly like the page.

        It does not rely on having been reached from R-43, and the denial tests
        prove that by issuing the request without ever rendering one.

        `Retry-After` carries N-22's floor from the validated bound, so the
        number the response asks a browser to honour is the number the settings
        graph accepted, and the server is free to back off further.
        """
        guard = GUARDS["R-44"]
        try:
            gate, context = await enter(request, guard)
        except _Refused as refused:
            return refused.response
        identifier = _object_id(job_id)
        if identifier is None:
            return JSONResponse(
                {"error": RefusalCode.OBJECT_NOT_REACHABLE.value}, status_code=404
            )
        try:
            view = await unit(
                lambda services: services.jobs.status(
                    context=context, job_id=identifier, csrf_token=gate.csrf_token
                )
            )
        except WebRefusal as refusal:
            return _refusal_response(request, refusal, guard)
        response = authority.render(
            request, "job_status_fragment.html", view=view, status_code=200
        )
        response.headers["Retry-After"] = str(view.poll_after_seconds)
        return response

    # -- R-45 --------------------------------------------------------------
    @app.post("/v1/council/jobs/{job_id}/cancel", name="council_job_cancel")
    async def council_job_cancel(request: Request, job_id: str) -> Response:
        """R-45. Best effort, and truthful about which effort it was.

        A job whose apply has already committed **cannot** be cancelled: both
        cancel statements filter `effect_committed_at IS NULL`, match zero rows,
        and this answers `409` with VM-19 carrying the committed result — the
        difference between "your cancellation was too late" and "your cancellation
        worked".

        The conflict word comes from the **refusal**, not from the current job
        state (2026-08-18 effect-publication remediation). A `running` apply whose
        import has committed is the case the two disagree on: its state says
        `running`, which would have been rendered `stale_version`, and the truth is
        `already_applied`.
        """
        guard = GUARDS["R-45"]
        try:
            gate, context, _form = await enter_mutation(request, guard)
        except _Refused as refused:
            return refused.response
        identifier = _object_id(job_id)
        if identifier is None:
            return JSONResponse(
                {"error": RefusalCode.OBJECT_NOT_REACHABLE.value}, status_code=404
            )
        try:
            await unit(
                lambda services: services.jobs.cancel(
                    context=context, job_id=identifier, now=utcnow()
                )
            )
        except WebRefusal as refusal:
            if refusal.status == 409:
                current = await unit(
                    lambda services: services.jobs.status(
                        context=context,
                        job_id=identifier,
                        csrf_token=gate.csrf_token,
                    )
                )
                return _conflict(
                    request,
                    refusal,
                    conflict=_cancel_conflict(refusal, current.job_state),
                    current=current,
                )
            return _mutation_refusal(request, refusal, guard)
        return RedirectResponse(f"/v1/council/jobs/{identifier}", status_code=303)

    # -- R-46 --------------------------------------------------------------
    @app.post("/v1/council/jobs/{job_id}/apply", name="council_import_confirm")
    async def council_import_confirm(request: Request, job_id: str) -> Response:
        """R-46. The one route in Phase 3 that changes durable character-identity
        state, and it does so by **enqueuing**.

        Why an enqueue rather than an inline apply: the apply re-parses the same
        artifact, so its floor is the same ~9.6 seconds the preview measured, and
        no real-data apply has ever been measured at all (route contract §6.3,
        F-1). Modelling it as a synchronous handler would repeat the mistake the
        plan corrected for preview.
        """
        guard = GUARDS["R-46"]
        try:
            gate, context, form = await enter_mutation(request, guard)
        except _Refused as refused:
            return refused.response
        identifier = _object_id(job_id)
        if identifier is None:
            return JSONResponse(
                {"error": RefusalCode.OBJECT_NOT_REACHABLE.value}, status_code=404
            )
        token = (form.get("preview_token") or "").strip()
        nonce = (form.get("nonce") or "").strip()
        if not token:
            return _validation(request, "preview_token")
        if not nonce:
            return _validation(request, "nonce")
        try:
            outcome = await unit(
                lambda services: services.jobs.enqueue_apply(
                    context=context,
                    job_id=identifier,
                    preview_token=token,
                    nonce=nonce,
                    now=utcnow(),
                )
            )
        except WebRefusal as refusal:
            if refusal.status == 409:
                # `blocked_by_running_apply`: another confirmation of the same
                # input is already in flight, and this one starts nothing.
                current = await unit(
                    lambda services: services.jobs.status(
                        context=context,
                        job_id=identifier,
                        csrf_token=gate.csrf_token,
                    )
                )
                return _conflict(
                    request, refusal, conflict="duplicate_request", current=current
                )
            return _mutation_refusal(request, refusal, guard)
        if isinstance(outcome, ConfirmationRefused):
            # **A refusal that committed.** Marking the preview `stale` is a
            # state change, so the service returns rather than raising — an
            # exception would roll the mark back with the transaction, and the
            # next confirmation would rediscover the same staleness instead of
            # being told about it. The status read below therefore sees the mark
            # this request made, which is what puts the exact changed scope in
            # front of the Council member.
            current = await unit(
                lambda services: services.jobs.status(
                    context=context, job_id=identifier, csrf_token=gate.csrf_token
                )
            )
            return _conflict(
                request,
                WebRefusal(RefusalCode.PREVIEW_NOT_CONFIRMABLE, status=409),
                conflict="stale_preview",
                current=current,
            )
        return RedirectResponse(f"/v1/council/jobs/{outcome.job_id}", status_code=303)

    # -- R-47 --------------------------------------------------------------
    @app.get("/v1/council/imports/{import_id}", name="council_import_result")
    async def council_import_result(request: Request, import_id: str) -> Response:
        """R-47. The immutable receipt. **No artifact download exists anywhere.**"""
        guard = GUARDS["R-47"]
        try:
            _gate, context = await enter(request, guard)
        except _Refused as refused:
            return refused.response
        identifier = _object_id(import_id)
        if identifier is None:
            return _denied(
                request, WebRefusal(RefusalCode.OBJECT_NOT_REACHABLE, status=404)
            )
        try:
            view = await unit(
                lambda services: services.import_receipts.receipt(
                    context=context, import_id=identifier
                )
            )
        except WebRefusal as refusal:
            return _refusal_response(request, refusal, guard)
        return authority.render(
            request, "import_result.html", view=view, status_code=200
        )

    # -- R-48 --------------------------------------------------------------
    @app.get("/v1/audit", name="audit_search")
    async def audit_search(request: Request) -> Response:
        """R-48. VM-18, the navigable page. Council, administrator, break-glass."""
        guard = GUARDS["R-48"]
        try:
            _gate, context = await enter(request, guard)
        except _Refused as refused:
            return refused.response
        try:
            view = await unit(
                lambda services: services.audit_search.search(
                    context=context,
                    query=request.query_params,
                    cursor_token=request.query_params.get("cursor"),
                    size=page_size(request.query_params.get("size")),
                )
            )
        except (InvalidCursor, FilterBounds, WebRefusal) as refusal:
            return _refusal_response(request, refusal, guard)
        return authority.render(
            request, "audit_search.html", view=view, status_code=200
        )

    # -- R-49 --------------------------------------------------------------
    @app.get("/v1/audit/results", name="audit_search_results")
    async def audit_search_results(request: Request) -> Response:
        """R-49. The fragment R-48 polls, authorized exactly like the page."""
        guard = GUARDS["R-49"]
        try:
            _gate, context = await enter(request, guard)
        except _Refused as refused:
            return refused.response
        try:
            view = await unit(
                lambda services: services.audit_search.search(
                    context=context,
                    query=request.query_params,
                    cursor_token=request.query_params.get("cursor"),
                    size=page_size(request.query_params.get("size")),
                )
            )
        except (InvalidCursor, FilterBounds, WebRefusal) as refusal:
            return _refusal_response(request, refusal, guard)
        return authority.render(
            request, "audit_results.html", view=view, status_code=200
        )

    # -- shared rendering --------------------------------------------------
    def _conflict(
        request: Request, refusal: WebRefusal, *, conflict: str, current
    ) -> HTMLResponse:
        """`409` with VM-19, always carrying the **current** state.

        A conflict that said only "no" would leave the user to retry blindly. The
        current view is what makes the next action informed — and for an
        already-applied confirmation it is the original receipt, which is what
        makes a double-click indistinguishable from a single click at the user's
        level while remaining one durable effect.
        """
        return authority.render(
            request,
            "conflict.html",
            view=ConflictView(
                state="stale",
                conflict=conflict,
                current=current,
                correlation=Correlation(refusal.correlation_id),
            ),
            status_code=409,
        )

    def _mutation_refusal(
        request: Request, refusal: WebRefusal, guard: RouteGuard
    ) -> Response:
        if refusal.status == 422:
            return _validation(
                request, _field_for(refusal), code=_code_for(refusal)
            )
        return JSONResponse({"error": refusal.code.value}, status_code=refusal.status)


def _cancel_conflict(refusal: WebRefusal, job_state: str) -> str:
    """VM-19's closed `conflict` vocabulary for R-45's `409`.

    From the refusal when it carries one — `CancellationRefused` knows whether the
    statement lost to a committed effect, which the job's state does not say — and
    from the state otherwise, so a `409` raised by anything else still renders a
    word from the same closed set.
    """
    carried = getattr(refusal, "conflict", None)
    if carried is not None:
        return carried
    if job_state == JobState.CANCELLED.value:
        return "already_cancelled"
    if job_state == JobState.COMPLETED.value:
        return "already_applied"
    return "stale_version"


def _field_for(refusal: WebRefusal) -> str:
    if refusal.code is RefusalCode.FOLDER_UNSELECTED:
        return "folder_id"
    if refusal.code is RefusalCode.FILTER_BOUNDS:
        return "filters"
    return "folder_id"


def _code_for(refusal: WebRefusal) -> str:
    if refusal.code is RefusalCode.OBJECT_NOT_REACHABLE:
        # `not_found` rather than `not_permitted`, matching the route contract's
        # `404` rule, so validation cannot become the enumeration oracle the
        # status code refuses to be.
        return "not_found"
    if refusal.code is RefusalCode.FILTER_BOUNDS:
        return "too_long"
    return "not_a_choice"


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


def _open(composition, settings, token):
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


__all__ = ["GUARDS", "P3_3_ROUTE_INVENTORY", "register"]
