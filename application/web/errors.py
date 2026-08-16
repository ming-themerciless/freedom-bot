"""Typed refusals for the portal, and the closed vocabulary of denial codes.

Every refusal the web layer can produce is one of these. The rule they exist to
enforce is the route contract's: **the body of a denial says the category and
nothing else**. A free-text reason is a disclosure, and a reason assembled from
the object that was refused is an enumeration oracle.

The status code each maps to is the route contract §2.3 table, restated here as
data so a handler cannot pick a different one by accident:

| Situation | Status |
|---|---|
| No session on a protected route | `303` for `GET` navigation, `401` otherwise |
| Session, capability missing | `403` |
| Session and capability fine, object out of reach | `404`, byte-identical to absent |
| Session valid, not currently a member | `403` with VM-02 |
| Continuity-scoped session outside N-65's surface | `403` |
| Continuity-scoped caller outside N-67's allowlist | `403 emergency_scope_refused` |
| Membership unknown and N-10's grace spent | `503` with VM-03 |
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from uuid import UUID, uuid4


class RefusalCode(Enum):
    """The closed set. A code that is not here cannot reach a response."""

    NOT_AUTHENTICATED = "not_authenticated"
    NOT_A_MEMBER = "not_a_member"
    INSUFFICIENT_CAPABILITY = "insufficient_capability"
    OBJECT_NOT_REACHABLE = "object_not_reachable"
    EMERGENCY_SCOPE_REFUSED = "emergency_scope_refused"
    EMERGENCY_SURFACE_REFUSED = "emergency_surface_refused"
    SERVICE_DEGRADED = "service_degraded"
    RATE_LIMITED = "rate_limited"
    CSRF_INVALID = "csrf_invalid"
    ORIGIN_INVALID = "origin_invalid"
    HOST_INVALID = "host_invalid"
    BODY_TOO_LARGE = "body_too_large"
    KILL_SWITCH_ENGAGED = "kill_switch_engaged"
    PROTECTED_MAPPING = "protected_mapping"
    DUPLICATE_ACTIVE_MAPPING = "duplicate_active_mapping"
    UNKNOWN_CAPABILITY = "unknown_capability"
    MAPPING_LIMIT = "mapping_limit"
    STALE_VERSION = "stale_version"


class WebRefusal(Exception):
    """A refusal the portal can render safely.

    Carries a correlation id so an operator can find the log line the user
    quotes, and **no** detail about the object that was refused.
    """

    __slots__ = ("code", "status", "correlation_id")

    def __init__(
        self,
        code: RefusalCode,
        *,
        status: int,
        correlation_id: UUID | None = None,
    ) -> None:
        super().__init__(code.value)
        self.code = code
        self.status = status
        self.correlation_id = correlation_id or uuid4()


class NotAuthenticated(WebRefusal):
    def __init__(self, correlation_id: UUID | None = None) -> None:
        super().__init__(
            RefusalCode.NOT_AUTHENTICATED, status=401, correlation_id=correlation_id
        )


class NotAMember(WebRefusal):
    def __init__(self, correlation_id: UUID | None = None) -> None:
        super().__init__(
            RefusalCode.NOT_A_MEMBER, status=403, correlation_id=correlation_id
        )


class InsufficientCapability(WebRefusal):
    def __init__(self, correlation_id: UUID | None = None) -> None:
        super().__init__(
            RefusalCode.INSUFFICIENT_CAPABILITY,
            status=403,
            correlation_id=correlation_id,
        )


class EmergencyScopeRefused(WebRefusal):
    """N-67. The administrator-continuity allowlist, refused before any write.

    Distinct from `InsufficientCapability` on purpose: the caller *does* hold
    `platform_administrator`. What it does not hold is the authority to write
    *this* capability, and an incident review needs those two sentences to be
    different.
    """

    def __init__(self, correlation_id: UUID | None = None) -> None:
        super().__init__(
            RefusalCode.EMERGENCY_SCOPE_REFUSED,
            status=403,
            correlation_id=correlation_id,
        )


class EmergencySurfaceRefused(WebRefusal):
    """N-65. A continuity-scoped session outside the identity/audit surface."""

    def __init__(self, correlation_id: UUID | None = None) -> None:
        super().__init__(
            RefusalCode.EMERGENCY_SURFACE_REFUSED,
            status=403,
            correlation_id=correlation_id,
        )


class ObjectNotReachable(WebRefusal):
    """`404`, byte-identical to a genuinely absent object. That is deliberate."""

    def __init__(self, correlation_id: UUID | None = None) -> None:
        super().__init__(
            RefusalCode.OBJECT_NOT_REACHABLE, status=404, correlation_id=correlation_id
        )


class ServiceDegraded(WebRefusal):
    """N-10's grace is spent and authorization cannot be confirmed. Fail closed."""

    def __init__(self, correlation_id: UUID | None = None) -> None:
        super().__init__(
            RefusalCode.SERVICE_DEGRADED, status=503, correlation_id=correlation_id
        )


class RateLimited(WebRefusal):
    def __init__(self, correlation_id: UUID | None = None) -> None:
        super().__init__(
            RefusalCode.RATE_LIMITED, status=429, correlation_id=correlation_id
        )


class AuthenticationFailure(Exception):
    """A login attempt that did not produce a session.

    The `code` is the one the browser sees; it is deliberately coarser than what
    the audit record holds. `invalid`, `expired` and `consumed` are one outcome
    to a caller and three different sentences to an operator.

    A plain exception rather than a frozen dataclass, and the reason is worth a
    line: a frozen dataclass refuses `__setattr__`, and Python sets
    `__traceback__` on an exception as it propagates. One made frozen raises a
    confusing `TypeError` from inside `contextlib` instead of the refusal it was
    supposed to carry.

    **The refusal record travels with the exception, unwritten.** A refused login
    rolls its transaction back — that is what "no session was created" means — so
    an audit event written inside it would be discarded exactly when the refusal
    happened. SM-01 and SM-03 require the opposite: every attempt and outcome is
    audited. The event is therefore described here and committed by
    `record_authentication_failure` in a **fresh** transaction, carrying the same
    correlation id.
    """

    __slots__ = ("code", "correlation_id", "audit")

    def __init__(
        self,
        *,
        code: str,
        correlation_id: UUID,
        audit: "FailureAudit | None" = None,
    ) -> None:
        super().__init__(f"{code} ({correlation_id})")
        self.code = code
        self.correlation_id = correlation_id
        self.audit = audit


@dataclass(frozen=True, slots=True)
class FailureAudit:
    """The audit event a refused authentication owes, before it is written."""

    action: str
    entity_type: str
    entity_id: str
    capability: object
    payload: dict
    account_id: UUID | None = None


def record_authentication_failure(engine, failure: AuthenticationFailure) -> None:
    """Commit a refusal's audit event, after the transaction that failed rolled back.

    Called by the route rather than by the service, because only the route knows
    that the service's transaction is over. A refusal that leaves no trace is
    indistinguishable afterwards from an attempt that never happened.
    """
    if failure.audit is None:
        return
    from adapters.web.repositories import WebAuditRepository
    from application.audit import AuditEvent, AuditSource

    with engine.begin() as connection:
        WebAuditRepository(connection).record(
            AuditEvent(
                action=failure.audit.action,
                entity_type=failure.audit.entity_type,
                entity_id=failure.audit.entity_id,
                source=AuditSource.WEB,
                actor_capability=failure.audit.capability,
                correlation_id=failure.correlation_id,
                actor_platform_account_id=failure.audit.account_id,
                payload=failure.audit.payload,
            )
        )


__all__ = [
    "AuthenticationFailure",
    "FailureAudit",
    "EmergencyScopeRefused",
    "EmergencySurfaceRefused",
    "InsufficientCapability",
    "NotAMember",
    "NotAuthenticated",
    "ObjectNotReachable",
    "RateLimited",
    "RefusalCode",
    "ServiceDegraded",
    "WebRefusal",
    "record_authentication_failure",
]
