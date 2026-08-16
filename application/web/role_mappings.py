"""Role-capability administration, and the guard that makes N-67 more than a delay.

**Scope note.** P3.1 owns the *foundation*: the table, its constraints and
triggers, capability resolution over it, and this service. The administration
**routes** R-32 to R-34 and R-38, and the screen behind them, belong to P3.2 and
are deliberately not registered here. What is here is what the break-glass
package needs in order to be provably bounded — the three tests TC-BG-05a, 05c
and 05e exercise this service directly, because a boundary that is only testable
through a route that does not exist yet is a boundary nobody has checked.

## The invariant, in one sentence a reviewer can test

> No sequence of mapping changes that begins in a break-glass session and passes
> through any number of ordinary logins yields Council, character or import
> authority, until a full-scope administrator ratifies.

That is a property of *sequences*, not of sessions, and it is why the first
revision's control — short-circuiting capability resolution on `auth_method` —
was insufficient. See `application/web/capabilities.py` for the attack it misses.

## Three controls, deliberately redundant

| # | Control | Fails safe if |
|---|---|---|
| 1 | This service resolves the caller's administrator scope and refuses a disallowed capability **before any row is read or written** | The route layer is bypassed |
| 2 | `CHECK (created_under_scope = 'full' OR capability = 'platform_administrator')` | This service is wrong, or a future one forgets |
| 3 | N-65's route surface refuses a continuity-scoped session outside identity/capability administration and audit reads | Either of the above is bypassed |

Control 2 is the one that does not depend on the session at all: it depends on
what is being written. That is why it exists, and why this module does not treat
its own check as sufficient.

## Every attempt is recorded, including every refusal

A refusal that leaves no trace is indistinguishable afterwards from an attack that
never happened. `role_capability_mapping_events` carries the attempted capability
even when the write was refused, because *"a break-glass session tried to map a
role to Council"* is precisely the sentence an incident review needs and it
exists nowhere else if the refusal writes only a counter.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from application.audit import ActorCapability, AuditEvent, AuditSource
from application.web.capabilities import (
    MAPPABLE_CAPABILITIES,
    AdministratorScope,
    MappingProvenance,
    WebAuthorizationContext,
)
from application.web.errors import (
    EmergencyScopeRefused,
    InsufficientCapability,
    RefusalCode,
    WebRefusal,
)

#: N-62. Bounds capability resolution and the administration view.
MAX_ACTIVE_MAPPINGS_PER_GUILD = 50


@dataclass(frozen=True, slots=True)
class MappingOutcome:
    mapping_id: UUID
    event_id: UUID


@dataclass(frozen=True, slots=True)
class MappingRefusal:
    """A refused attempt, described but not yet written.

    It cannot be written in the transaction that is about to roll back — that
    transaction is rolling back *because of* this refusal, and the record would
    go with it. SM-07 puts it in its own transaction, after the rollback,
    carrying the same correlation id, and `run_mapping_change` is where that
    happens.
    """

    operation: str
    refusal_code: RefusalCode
    guild_id: int
    role_id: int
    capability: ActorCapability
    actor_account_id: UUID
    auth_method: object
    scope: AdministratorScope
    reason: str
    correlation_id: UUID
    mapping_id: UUID | None = None

    def as_event_kwargs(self) -> dict:
        return {
            "mapping_id": self.mapping_id,
            "operation": self.operation,
            "outcome": "refused",
            "refusal_code": self.refusal_code.value,
            "guild_id": self.guild_id,
            "role_id": self.role_id,
            "capability": self.capability,
            "actor_account_id": self.actor_account_id,
            "auth_method": self.auth_method,
            "scope": self.scope,
            "reason": self.reason,
            "correlation_id": self.correlation_id,
        }


class MappingRefused(Exception):
    """Carries both the refusal to answer with and the record to write afterwards."""

    __slots__ = ("refusal", "record")

    def __init__(self, refusal: Exception, record: MappingRefusal) -> None:
        super().__init__(str(refusal))
        self.refusal = refusal
        self.record = record


def run_mapping_change(engine, change):
    """Run a mapping change so that **a refusal is recorded even though it failed**.

    Two transactions, and the second one is the whole point:

    1. `change(connection)` runs in a transaction that commits on success and
       rolls back on refusal — so a refused attempt writes no mapping, exactly as
       required.
    2. If it was refused, a **fresh** transaction writes the
       `role_capability_mapping_events` row, with the same correlation id. That
       row survives precisely because it is not in the transaction that failed.

    Doing this at each call site instead would be five copies of a rule that has
    to hold in all five, so it lives here and the call sites pass a function.
    """
    from adapters.web.repositories import RoleMappingRepository

    try:
        with engine.begin() as connection:
            return change(connection)
    except MappingRefused as refused:
        with engine.begin() as connection:
            RoleMappingRepository(connection).record_event(
                **refused.record.as_event_kwargs()
            )
        raise refused.refusal from None


class RoleMappingService:
    """The only writer of `role_capability_mappings`. Transactions belong to the caller."""

    __slots__ = ("_mappings", "_audit")

    def __init__(self, *, role_mappings, audit) -> None:
        self._mappings = role_mappings
        self._audit = audit

    # -- create -----------------------------------------------------------
    def create(
        self,
        *,
        context: WebAuthorizationContext,
        guild_id: int,
        role_id: int,
        capability: ActorCapability,
        reason: str,
        correlation_id: UUID,
    ) -> MappingOutcome:
        context.require_platform_administrator()
        self._require_reason(reason)

        # N-67, control 1: refused **before any row is read or written**. The
        # refusal is recorded, in its own right, with the attempted capability.
        if capability not in MAPPABLE_CAPABILITIES:
            raise MappingRefused(
                InsufficientCapability(correlation_id),
                self._record_refusal(
                    context,
                    operation="create",
                    refusal_code=RefusalCode.UNKNOWN_CAPABILITY,
                    guild_id=guild_id,
                    role_id=role_id,
                    capability=capability,
                    reason=reason,
                    correlation_id=correlation_id,
                ),
            )
        if context.is_continuity_scoped and capability is not ActorCapability.PLATFORM_ADMINISTRATOR:
            raise MappingRefused(
                EmergencyScopeRefused(correlation_id),
                self._record_refusal(
                    context,
                    operation="create",
                    refusal_code=RefusalCode.EMERGENCY_SCOPE_REFUSED,
                    guild_id=guild_id,
                    role_id=role_id,
                    capability=capability,
                    reason=reason,
                    correlation_id=correlation_id,
                ),
            )

        if self._mappings.active_count(guild_id) >= MAX_ACTIVE_MAPPINGS_PER_GUILD:
            raise MappingRefused(
                WebRefusal(
                    RefusalCode.MAPPING_LIMIT, status=409, correlation_id=correlation_id
                ),
                self._record_refusal(
                    context,
                    operation="create",
                    refusal_code=RefusalCode.MAPPING_LIMIT,
                    guild_id=guild_id,
                    role_id=role_id,
                    capability=capability,
                    reason=reason,
                    correlation_id=correlation_id,
                ),
            )

        mapping_id = self._mappings.create(
            guild_id=guild_id,
            role_id=role_id,
            capability=capability,
            created_by=context.account_id,
            auth_method=context.auth_method,
            scope=context.administrator_scope,
            reason=reason,
            correlation_id=correlation_id,
        )
        event_id = self._record_applied(
            context,
            operation="create",
            mapping_id=mapping_id,
            guild_id=guild_id,
            role_id=role_id,
            capability=capability,
            reason=reason,
            correlation_id=correlation_id,
        )
        self._audit.record(
            self._event(
                "role_capability.mapped",
                mapping_id,
                context,
                correlation_id,
                {
                    "guild_id": guild_id,
                    "role_id": role_id,
                    "capability": capability.value,
                    "scope": context.administrator_scope.value,
                },
            )
        )
        return MappingOutcome(mapping_id=mapping_id, event_id=event_id)

    # -- revoke -----------------------------------------------------------
    def revoke(
        self,
        *,
        context: WebAuthorizationContext,
        mapping_id: UUID,
        expected_version: int,
        reason: str,
        correlation_id: UUID,
        now: datetime,
    ) -> MappingOutcome:
        context.require_platform_administrator()
        self._require_reason(reason)

        row = self._mappings.get(mapping_id)
        if row is None or not row["active"]:
            raise WebRefusal(
                RefusalCode.OBJECT_NOT_REACHABLE, status=404, correlation_id=correlation_id
            )
        capability = ActorCapability(row["capability"])
        guild_id, role_id = row["guild_id"], row["role_id"]

        if row["protected"]:
            # Refused for **every** caller, ordinary administrators included
            # (OD-24). The trigger refuses it independently; this refusal exists
            # so the answer is a typed `403` rather than a database error.
            raise MappingRefused(
                WebRefusal(
                    RefusalCode.PROTECTED_MAPPING,
                    status=403,
                    correlation_id=correlation_id,
                ),
                self._record_refusal(
                    context,
                    operation="revoke",
                    refusal_code=RefusalCode.PROTECTED_MAPPING,
                    guild_id=guild_id,
                    role_id=role_id,
                    capability=capability,
                    reason=reason,
                    correlation_id=correlation_id,
                    mapping_id=mapping_id,
                ),
            )

        if context.is_continuity_scoped and capability is not ActorCapability.PLATFORM_ADMINISTRATOR:
            raise MappingRefused(
                EmergencyScopeRefused(correlation_id),
                self._record_refusal(
                    context,
                    operation="revoke",
                    refusal_code=RefusalCode.EMERGENCY_SCOPE_REFUSED,
                    guild_id=guild_id,
                    role_id=role_id,
                    capability=capability,
                    reason=reason,
                    correlation_id=correlation_id,
                    mapping_id=mapping_id,
                ),
            )

        if not self._mappings.revoke(
            mapping_id=mapping_id,
            revoked_by=context.account_id,
            auth_method=context.auth_method,
            scope=context.administrator_scope,
            expected_version=expected_version,
            at=now,
        ):
            raise WebRefusal(
                RefusalCode.STALE_VERSION, status=409, correlation_id=correlation_id
            )

        event_id = self._record_applied(
            context,
            operation="revoke",
            mapping_id=mapping_id,
            guild_id=guild_id,
            role_id=role_id,
            capability=capability,
            reason=reason,
            correlation_id=correlation_id,
        )
        self._audit.record(
            self._event(
                "role_capability.revoked",
                mapping_id,
                context,
                correlation_id,
                {
                    "guild_id": guild_id,
                    "role_id": role_id,
                    "capability": capability.value,
                    "scope": context.administrator_scope.value,
                },
            )
        )
        return MappingOutcome(mapping_id=mapping_id, event_id=event_id)

    # -- ratify (R-38) ----------------------------------------------------
    def ratify(
        self,
        *,
        context: WebAuthorizationContext,
        mapping_id: UUID,
        expected_version: int,
        reason: str,
        correlation_id: UUID,
        now: datetime,
    ) -> MappingOutcome:
        """The one operation that converts emergency authority into ordinary authority.

        Therefore the one that must not be reachable *from* emergency authority.
        `require_full_administrator_scope` demands `discord_oauth` **and** scope
        `full`; a `403` here during an incident is the boundary, not a defect —
        ratification waits until an administrator can authenticate normally.
        """
        row = self._mappings.get(mapping_id)
        capability = (
            ActorCapability(row["capability"])
            if row is not None
            else ActorCapability.PLATFORM_ADMINISTRATOR
        )
        guild_id = row["guild_id"] if row is not None else 0
        role_id = row["role_id"] if row is not None else 0

        try:
            context.require_full_administrator_scope()
        except (EmergencyScopeRefused, InsufficientCapability) as refusal:
            raise MappingRefused(
                refusal,
                self._record_refusal(
                    context,
                    operation="ratify",
                    refusal_code=RefusalCode.EMERGENCY_SCOPE_REFUSED,
                    guild_id=guild_id,
                    role_id=role_id,
                    capability=capability,
                    reason=reason,
                    correlation_id=correlation_id,
                    mapping_id=mapping_id,
                ),
            ) from refusal
        self._require_reason(reason)

        if row is None or not row["active"]:
            raise WebRefusal(
                RefusalCode.OBJECT_NOT_REACHABLE, status=404, correlation_id=correlation_id
            )
        if MappingProvenance(row["provenance"]) is not MappingProvenance.EMERGENCY_CONTINUITY:
            # Nothing to ratify. Answering `409` rather than pretending it worked
            # keeps "ratified once" observable to the caller.
            raise WebRefusal(
                RefusalCode.STALE_VERSION, status=409, correlation_id=correlation_id
            )

        if not self._mappings.ratify(
            mapping_id=mapping_id,
            ratified_by=context.account_id,
            expected_version=expected_version,
            at=now,
        ):
            raise WebRefusal(
                RefusalCode.STALE_VERSION, status=409, correlation_id=correlation_id
            )

        event_id = self._record_applied(
            context,
            operation="ratify",
            mapping_id=mapping_id,
            guild_id=guild_id,
            role_id=role_id,
            capability=capability,
            reason=reason,
            correlation_id=correlation_id,
        )
        self._audit.record(
            self._event(
                "role_capability.ratified",
                mapping_id,
                context,
                correlation_id,
                {
                    "guild_id": guild_id,
                    "role_id": role_id,
                    "capability": capability.value,
                    "previous_provenance": MappingProvenance.EMERGENCY_CONTINUITY.value,
                },
            )
        )
        return MappingOutcome(mapping_id=mapping_id, event_id=event_id)

    # -- helpers ----------------------------------------------------------
    @staticmethod
    def _require_reason(reason: str) -> None:
        if not reason or not reason.strip():
            raise ValueError("A capability change requires a non-blank reason.")

    def _record_applied(
        self,
        context: WebAuthorizationContext,
        *,
        operation: str,
        mapping_id: UUID,
        guild_id: int,
        role_id: int,
        capability: ActorCapability,
        reason: str,
        correlation_id: UUID,
    ) -> UUID:
        return self._mappings.record_event(
            mapping_id=mapping_id,
            operation=operation,
            outcome="applied",
            refusal_code=None,
            guild_id=guild_id,
            role_id=role_id,
            capability=capability,
            actor_account_id=context.account_id,
            auth_method=context.auth_method,
            scope=context.administrator_scope,
            reason=reason,
            correlation_id=correlation_id,
        )

    def _record_refusal(
        self,
        context: WebAuthorizationContext,
        *,
        operation: str,
        refusal_code: RefusalCode,
        guild_id: int,
        role_id: int,
        capability: ActorCapability,
        reason: str,
        correlation_id: UUID,
        mapping_id: UUID | None = None,
    ) -> "MappingRefusal":
        """Describe the refusal. **Deliberately does not write it.**

        The refusal has to survive the rollback that the raise about to follow
        will cause, so it cannot be written in the transaction being rolled back
        (SM-07: refusals are recorded in their own transaction, after the
        rollback, carrying the same correlation id). Writing it here would
        produce a refusal record that is discarded exactly when the refusal
        happened — the one case it exists for.

        `run_mapping_change` owns the second transaction. Returning the record
        rather than a `None` is what lets it.
        """
        return MappingRefusal(
            mapping_id=mapping_id,
            operation=operation,
            refusal_code=refusal_code,
            guild_id=guild_id,
            role_id=role_id,
            capability=capability,
            actor_account_id=context.account_id,
            auth_method=context.auth_method,
            scope=context.administrator_scope,
            reason=reason,
            correlation_id=correlation_id,
        )

    @staticmethod
    def _event(
        action: str,
        mapping_id: UUID,
        context: WebAuthorizationContext,
        correlation_id: UUID,
        payload: dict,
    ) -> AuditEvent:
        return AuditEvent(
            action=action,
            entity_type="role_capability_mapping",
            entity_id=str(mapping_id),
            source=AuditSource.WEB,
            actor_capability=ActorCapability.PLATFORM_ADMINISTRATOR,
            correlation_id=correlation_id,
            actor_platform_account_id=context.account_id,
            payload={**payload, "auth_method": context.auth_method.value},
        )


__all__ = [
    "MAX_ACTIVE_MAPPINGS_PER_GUILD",
    "MappingOutcome",
    "MappingRefusal",
    "MappingRefused",
    "RoleMappingService",
    "run_mapping_change",
]
