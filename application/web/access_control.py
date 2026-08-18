"""The authorization chain of route contract §2.1, steps 4 to 8, framework-free.

The web adapter authenticates, parses, invokes a use case and renders a typed
result. *Deciding* whether the caller may reach the route, and whether the
membership projection behind that decision is still trustworthy, is here — so
the rules can be exercised without a request object and so there is one
implementation of them rather than nineteen.

## The three-step shape, and why it is three

A protected request needs a database transaction, sometimes a network call to
the identity provider, and then a database transaction again. `.agents/AGENTS.md`
forbids holding a transaction open across a network call, so the sequence cannot
be one function:

1. `open_request()` — one transaction: resolve the session, refresh its idle
   window, read the membership projection and the active role-capability
   mappings, and resolve the caller's authority. When the projection is fresh
   (N-09) this is the **whole** request path and no network call happens at all,
   which is the common case for every page load inside a five-minute window.
2. If it is not fresh, the adapter awaits `provider.verify()` **outside** any
   transaction, and hands the result — or the failure — to:
3. `close_request()` — a second transaction: record what the provider said and
   re-resolve, or apply N-10's grace to what the provider did not say.

`RequestGate` is what carries state between them, so the adapter holds a value
rather than a half-finished decision.

## Fail closed, and the asymmetry that makes it a control

N-10 gives a **read** at most fifteen minutes on the last successful
observation. A **mutation** gets none: it is refused the moment the provider
cannot confirm the caller's current roles, and it does not consume the grace
either. That asymmetry is the whole of TC-OUT-02, and the reason is that a stale
role is a display inaccuracy on a read and an unauthorized write on a mutation.

A provider failure never writes an absence. `ProviderUnavailable` reaches
`close_request()` as *no observation*, and the projection is left exactly as it
was — "refresh failed" and "membership absent" are different facts, and a
rate-limit storm that recorded the first as the second would revoke a guild
(TC-OUT-04).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from application.web.capabilities import (
    AuthMethod,
    MembershipProjection,
    WebAuthorizationContext,
    resolve_capabilities,
)
from application.web.errors import (
    AmbiguousProviderIdentity,
    EmergencySurfaceRefused,
    InsufficientCapability,
    NotAMember,
    NotAuthenticated,
    ServiceDegraded,
)


class Requirement(Enum):
    """What a route requires of the caller, as the §5.2 matrix states it."""

    #: R-35 to R-37. A session, and nothing more: these routes are about the
    #: caller's own identities, so a person whose guild membership has been
    #: revoked still reaches them. That is deliberate — caller state `N` is `✓`
    #: on all three — because an account's identity list is how somebody
    #: recovers, and gating it on membership would lock the door from inside.
    SESSION = "session"
    #: R-20 and R-21. Member or Council, and **not** an administrator who is
    #: neither. See `_member_read` for why that is not a mistake.
    MEMBER_READ = "member_read"
    #: R-22 to R-30. Council only; administrator alone is `403`, because
    #: administrator is an operational role and this is game governance
    #: (OD-18, OD-24).
    COUNCIL = "council"
    #: R-31. Council **and** administrator may read the field profile, and
    #: neither can change it — there is no write route.
    COUNCIL_OR_ADMINISTRATOR = "council_or_administrator"
    #: R-32 to R-34. Platform Administrator; Council alone is `403`.
    ADMINISTRATOR = "administrator"
    #: R-38. Administrator on an **ordinary-provider** session whose authority is
    #: full-scope. The one door between emergency and ordinary authority, and
    #: therefore the one that must not open from the emergency side.
    FULL_ADMINISTRATOR = "full_administrator"


@dataclass(frozen=True, slots=True)
class RouteGuard:
    """One route's row of the §5.2 matrix, as data.

    Written as a table rather than as `if` statements inside each handler so
    that the matrix can be read in one place and asserted against the contract
    document. A handler that forgot a check would be a handler with no guard,
    which is visible; a handler with a subtly different inline check would not
    be.
    """

    route: str
    requirement: Requirement
    #: `GET` navigation answers `303` to the login page when there is no
    #: session; everything else — HTMX partials and every mutation — answers
    #: `401`. A redirect for a mutation would be a silent no-op.
    navigation: bool = False
    mutation: bool = False
    #: N-65. `False` on every route outside the identity/capability
    #: administration surface, which is what confines a break-glass session and,
    #: identically, a continuity-scoped ordinary session (route contract §3.3).
    continuity_allowed: bool = False


class SessionAbsent(Exception):
    """No live session. The adapter turns this into `303` or `401` per the guard.

    Not a `WebRefusal`, because the two answers differ by route kind and this
    module does not decide status codes for the navigation case.
    """


@dataclass(frozen=True, slots=True)
class MembershipRefresh:
    """What the adapter must ask the provider, between the two transactions.

    `None` from `open_request()` means "nothing to ask": the projection is
    inside N-09 and the authority already resolved is the answer.

    It carries the grant **as it was stored** — ciphertext, scopes and expiry —
    because the adapter has to rebuild a `ProviderTokens` from it, and every
    field of that object must be a value the platform actually persisted rather
    than one invented to fill the shape.
    """

    grant: object


@dataclass(frozen=True, slots=True)
class RequestGate:
    """The state of one protected request between its two transactions."""

    account_id: UUID
    session_id: UUID
    auth_method: AuthMethod
    context: WebAuthorizationContext
    refresh: MembershipRefresh | None
    csrf_token: str


def open_request(
    *,
    services,
    settings,
    token: str | None,
    now: datetime,
) -> RequestGate:
    """Steps 4 and 7 of the chain, in one transaction. Raises `SessionAbsent`.

    The session's idle window is refreshed here, so a live session's own
    activity keeps it live (N-06/N-15). A refused refresh is treated as an
    **absent** session and never retried: `SessionRepository.touch()` refuses
    exactly when the row is revoked or past one of its bounds, and retrying a
    refusal is how an expired session gets revived.
    """
    from application.web import csrf
    from application.web.sessions import SessionTouchRefused

    if not token:
        raise SessionAbsent()
    record = services.session_service.resolve(token, now=now)
    if record is None:
        raise SessionAbsent()
    try:
        services.session_service.touch(record, now=now)
    except SessionTouchRefused:
        raise SessionAbsent() from None

    auth_method = record.auth_method
    if auth_method.is_break_glass:
        # A break-glass session never touches the Discord projection (route
        # contract §7.3), so there is nothing to refresh and nothing to grace.
        context = resolve_capabilities(
            account_id=record.platform_account_id,
            auth_method=auth_method,
            membership=None,
            mappings=(),
        )
        return RequestGate(
            account_id=record.platform_account_id,
            session_id=record.id,
            auth_method=auth_method,
            context=context,
            refresh=None,
            csrf_token=csrf.issue(settings.csrf_key, record.id),
        )

    guild_id = settings.discord.guild_id
    # An account holding two active identities for one provider is an ambiguity the
    # repository refuses to resolve, and it arrives here as one. It becomes
    # `ServiceDegraded` — the same fail-closed answer as a provider the platform
    # cannot reach — because the platform cannot say whose roles this person holds,
    # and a capability decision it cannot make is one it must not guess. Letting the
    # repository's exception escape instead produced a `500` on every protected
    # request by such an account.
    try:
        subject = services.accounts.discord_subject(record.platform_account_id)
    except AmbiguousProviderIdentity:
        raise ServiceDegraded() from None
    projection = None
    if subject is not None:
        projection = services.membership.load(
            discord_user_id=int(subject), guild_id=guild_id
        )
    context = _resolve(services, record, projection, guild_id)

    refresh = None
    stale = projection is None or not projection.is_fresh(
        now=now, cache_seconds=settings.bounds.membership_cache_seconds
    )
    if stale and subject is not None:
        refresh = _refresh_plan(services, record.platform_account_id, subject)

    return RequestGate(
        account_id=record.platform_account_id,
        session_id=record.id,
        auth_method=auth_method,
        context=context,
        refresh=refresh,
        csrf_token=csrf.issue(settings.csrf_key, record.id),
    )


def close_request(
    *,
    services,
    settings,
    gate: RequestGate,
    observation,
    now: datetime,
    mutation: bool,
) -> WebAuthorizationContext:
    """Step 7 again, with whatever the provider said — or did not.

    `observation` is a `ProviderMembership` when the refresh succeeded and
    `None` when it failed. The failure branch writes **nothing**: the projection
    keeps its last successful `observed_at`, and N-10 is applied to that.
    """
    if observation is not None:
        projection = services.membership.record(
            discord_user_id=int(observation.subject),
            username=observation.username,
            global_name=observation.global_name,
            guild_id=observation.membership.guild_id,
            is_member=observation.membership.is_member,
            role_ids=observation.membership.role_ids,
            observed_at=observation.membership.observed_at,
        )
        return _resolve_projection(
            services, gate, projection, observation.membership.guild_id
        )

    if mutation:
        # N-10, first half: a mutation is refused **immediately** and does not
        # consume the grace. A stale role is a display inaccuracy on a read and
        # an unauthorized write here.
        raise ServiceDegraded()

    guild_id = settings.discord.guild_id
    try:
        subject = services.accounts.discord_subject(gate.account_id)
    except AmbiguousProviderIdentity:
        raise ServiceDegraded() from None
    projection = (
        services.membership.load(discord_user_id=int(subject), guild_id=guild_id)
        if subject is not None
        else None
    )
    if projection is None or not projection.within_grace(
        now=now, grace_seconds=settings.bounds.membership_grace_seconds
    ):
        # Fail closed, not fail open. The point at which this is raised is
        # exactly the point at which cached authorization stopped being
        # trustworthy, which is why VM-03 carries no cached role data.
        raise ServiceDegraded()
    return _resolve_projection(services, gate, projection, guild_id)


def authorize(context: WebAuthorizationContext, guard: RouteGuard) -> None:
    """Step 7's decision, and step 8's precondition. Raises a typed refusal.

    Order matters and is the route contract's: the continuity surface (N-65) is
    checked **before** the capability requirement, so a break-glass session on a
    Council route is refused for being emergency-scoped rather than for lacking
    Council — two different sentences, and an incident review needs the right
    one.
    """
    if context.is_continuity_scoped and not guard.continuity_allowed:
        raise EmergencySurfaceRefused()

    requirement = guard.requirement
    if requirement is Requirement.SESSION:
        return
    if requirement is Requirement.MEMBER_READ:
        _member_read(context)
        return
    if requirement is Requirement.COUNCIL:
        context.require_council()
        return
    if requirement is Requirement.COUNCIL_OR_ADMINISTRATOR:
        context.require_guild_member()
        if not (context.guild_council or context.platform_administrator):
            raise InsufficientCapability()
        return
    if requirement is Requirement.ADMINISTRATOR:
        context.require_platform_administrator()
        return
    if requirement is Requirement.FULL_ADMINISTRATOR:
        context.require_full_administrator_scope()
        return
    raise InsufficientCapability()


def _member_read(context: WebAuthorizationContext) -> None:
    """R-20 and R-21: `M` and `CA` and `C` may; `A` may not.

    The refusal of a Platform Administrator who is not also Council looks like a
    mistake and is the accepted matrix (route contract §5.2): the operational
    role is not a game-data role, so an administrator has no standing to read a
    character sheet merely by being an administrator. `CA` reaches these routes
    **through Council**, which is why the test below is "administrator and not
    Council" rather than "administrator".
    """
    context.require_guild_member()
    if context.guild_council:
        return
    if context.platform_administrator:
        raise InsufficientCapability()


def _resolve(services, record, projection, guild_id: int) -> WebAuthorizationContext:
    if projection is None:
        return resolve_capabilities(
            account_id=record.platform_account_id,
            auth_method=record.auth_method,
            membership=None,
            mappings=(),
        )
    return resolve_capabilities(
        account_id=record.platform_account_id,
        auth_method=record.auth_method,
        membership=projection,
        mappings=services.mappings.active_mappings(guild_id),
    )


def _resolve_projection(
    services, gate: RequestGate, projection: MembershipProjection, guild_id: int
) -> WebAuthorizationContext:
    return resolve_capabilities(
        account_id=gate.account_id,
        auth_method=gate.auth_method,
        membership=projection,
        mappings=services.mappings.active_mappings(guild_id),
    )


def _refresh_plan(services, account_id: UUID, subject: str) -> MembershipRefresh | None:
    identity_id = services.accounts.identity_id("discord", subject)
    if identity_id is None:
        return None
    grant = services.tokens.load(identity_id)
    if grant is None:
        # No stored token means no way to ask the provider. The projection is
        # then all there is, and N-10's grace governs it — the caller is not
        # refused for a token the platform deleted at logout.
        return None
    return MembershipRefresh(grant=grant)


def require_not_a_member_view(context: WebAuthorizationContext) -> None:
    """Caller state `N`, rendered as VM-02 rather than as a bare `403`.

    The distinction from *not logged in* is the whole content of that view: the
    person authenticated successfully and is not in the guild, which is what
    they need in order to recover.
    """
    if not context.guild_member and not context.is_continuity_scoped:
        raise NotAMember()


__all__ = [
    "MembershipRefresh",
    "RequestGate",
    "Requirement",
    "RouteGuard",
    "SessionAbsent",
    "authorize",
    "close_request",
    "open_request",
    "require_not_a_member_view",
]
