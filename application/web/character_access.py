"""Character-link administration: one service, four callers, one set of rules.

R-25, R-26 and R-27 are the Council screen's grant, revoke and default-change.
R-29 — confirming a Sheet-era identity proposal — creates its link *through the
same `grant()` below*, which is the migration contract's requirement in §7.2 and
is the reason this module exists as a boundary rather than as three route
handlers. A second grant path would be a second place for the one-active-owner
invariant, the reason requirement, the optimistic version, the audit event and
the atomicity to be got right, and only one of them would be under test.

## One kind of authority

`grant()` takes a `WebAuthorizationContext`: a **live** resolution of the
caller's current Discord roles, taken on the request that is granting. All four
callers are request handlers and all four hold one, R-29 included.

**Simplified 2026-08-17 (change-log entry C-P3.2-A, OD-46).** This module used to
define a `LinkAuthority` protocol with two implementations, because a withdrawn
command C-05 materialized confirmed proposals from a host-local process with no
session and had to be attributed to the Council member who had confirmed earlier.
`RecordedCouncilDecision` was that second authority, and the abstraction existed
solely to hold the two apart. Immediate activation removes the case: a
confirmation is taken by a Council member who is present, so the authority is the
one already being resolved for the request. The protocol and the recorded-decision
object are gone rather than kept for symmetry — an authority type with one
implementation is indirection, and one that could be constructed from a database
row is a second way for an authorization to be attributed.

## What the caller supplies, and what is resolved here

Nothing authorization-bearing arrives from the browser. The route hands this
service a `WebAuthorizationContext` it resolved **now** from the membership
projection, a character id, a target Discord **snowflake**, and a version. The
target *platform account* is resolved server-side from the snowflake
(TC-ID-08): a `platform_account_id` in the form is ignored because the form has
no such field and the service has no parameter for one.

## Atomicity, and where the transaction belongs

Every method here runs inside the caller's transaction and writes both the state
change and its audit event into it. A failure in either rolls back both, which is
TC-ACC-01's *"an injected audit failure rolls the change back"* — not because
this module catches anything, but because it catches **nothing**. There is no
`try` around a `record()` call anywhere below, and adding one would turn an
atomic pair into a claim.

## The three invariants the database owns

| Invariant | Enforced by |
|---|---|
| At most one active `owner` per character | `uq_character_access_one_active_owner` |
| At most one active link per (character, account) | `uq_character_access_one_active_link_account` |
| At most one active default character per account | `uq_character_access_one_active_default_per_account` |

This service checks the first and the third before writing, so the ordinary
answer is a typed refusal rather than an integrity error. That check is **not**
the control: two concurrent grants both pass it and one of them is refused by
PostgreSQL, which is what TC-ACC-02 and TC-ACC-03 exercise with real connections.
The service's job is to make the common case legible; the index's job is to make
the racing case impossible.

## OD-37, stated where it is implemented

*At least one owner* cannot be a constraint — the Phase 2 importer creates a
character before Council has resolved who owns it — so revoking the last active
owner is **permitted** and produces the explicit `unresolved_owner` state that
VM-07 and VM-08 render. Refusing the revocation would trap a mis-assigned owner;
inventing a replacement would fabricate authority. The third option is to let the
state be visible, and it is the one the decision took.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from application.audit import ActorCapability, AuditEvent, AuditSource
from application.web.capabilities import WebAuthorizationContext
from application.web.errors import (
    ObjectNotReachable,
    RefusalCode,
    WebRefusal,
)

#: §3.2 of the view-model contract. A longer reason is **refused** at input
#: validation with `422`, not silently cut: a truncated justification is a
#: different justification, and the person writing it should be told.
REASON_BOUND = 500

ACCESS_KINDS = ("owner", "co_owner", "delegate", "viewer")


class BlankReason(WebRefusal):
    """A grant, revoke or default change with no stated reason.

    `422` with the form re-rendered, per the route contract's validation row —
    the Council member can correct it, and a bare `400` would not tell them how.
    """

    def __init__(self, correlation_id: UUID | None = None) -> None:
        super().__init__(
            RefusalCode.INSUFFICIENT_CAPABILITY, status=422, correlation_id=correlation_id
        )


class StaleVersion(WebRefusal):
    """The character moved under the form. `409` with the current state (VM-19).

    Never applied on top: the conditional update matched no row, so nothing was
    written and the caller is shown what the character is *now* rather than a
    success that overwrote somebody else's change.
    """

    def __init__(self, correlation_id: UUID | None = None) -> None:
        super().__init__(
            RefusalCode.STALE_VERSION, status=409, correlation_id=correlation_id
        )


class InvalidAccessKind(WebRefusal):
    def __init__(self, correlation_id: UUID | None = None) -> None:
        super().__init__(
            RefusalCode.UNKNOWN_CAPABILITY, status=422, correlation_id=correlation_id
        )


@dataclass(frozen=True, slots=True)
class AccessChange:
    """The receipt of one applied change. Small on purpose.

    A route redirects after a mutation (post/redirect/get), so it needs the
    identifiers and nothing else; anything richer would be a second rendering of
    state the next `GET` re-reads under fresh authorization.
    """

    access_id: UUID
    character_id: UUID
    account_id: UUID
    character_version: int


class CharacterAccessService:
    """The only writer of `character_access`. Transactions belong to the caller."""

    __slots__ = ("_access", "_accounts", "_audit")

    def __init__(self, *, access, accounts, audit) -> None:
        self._access = access
        self._accounts = accounts
        self._audit = audit

    # -- R-25 -------------------------------------------------------------
    def grant(
        self,
        *,
        context: WebAuthorizationContext,
        character_id: UUID,
        subject: str,
        access_kind: str,
        reason: str,
        expected_version: int,
        correlation_id: UUID,
        now: datetime,
        make_default: bool = False,
    ) -> AccessChange:
        """Link one platform account to one character, under Council authority.

        `subject` is a Discord snowflake as a canonical decimal string — the
        stable identity — and the platform account is resolved from it here. A
        snowflake with no account, or with no *active* identity, is refused as
        unreachable rather than causing an account to be created: creating one
        would mint a platform identity from a Council form, which is ADR 0010's
        boundary in the wrong direction.

        `context` is the caller's live authorization context. R-25 and R-29 pass
        the one resolved for their own request, and everything below is identical
        for both, which is the point — the migration path is not a second grant.
        """
        context.require_council()
        reason = self._require_reason(reason, correlation_id)
        if access_kind not in ACCESS_KINDS:
            raise InvalidAccessKind(correlation_id)

        self._require_character(character_id, correlation_id)
        account_id = self._accounts.account_for_active_identity("discord", subject)
        if account_id is None:
            # Byte-identical to "no such character": a Council member learns
            # that this combination cannot be linked, and not which half of it
            # the platform has never heard of.
            raise ObjectNotReachable(correlation_id)

        if access_kind == "owner":
            existing_owner = self._access.active_owner(character_id)
            if existing_owner is not None and existing_owner["platform_account_id"] != account_id:
                # The index would refuse this anyway. Checking first is what
                # turns an integrity error into the sentence a Council member
                # can act on — revoke the current owner, then grant.
                raise WebRefusal(
                    RefusalCode.DUPLICATE_ACTIVE_MAPPING,
                    status=409,
                    correlation_id=correlation_id,
                )

        version = self._bump(character_id, expected_version, now, correlation_id)

        if make_default:
            self._access.clear_default_for_account(account_id, at=now)

        access_id = self._access.grant(
            character_id=character_id,
            platform_account_id=account_id,
            access_kind=access_kind,
            granted_by_account_id=context.account_id,
            default_character=make_default,
            reason=reason,
            correlation_id=correlation_id,
            at=now,
        )
        self._audit.record(
            self._event(
                "character_access.granted",
                access_id,
                context,
                correlation_id,
                {
                    "character_id": str(character_id),
                    "platform_account_id": str(account_id),
                    "access_kind": access_kind,
                    "default_character": make_default,
                    "before": {"active_link": False},
                    "after": {"active_link": True},
                    "character_version": version,
                    "reason": reason,
                },
            )
        )
        return AccessChange(
            access_id=access_id,
            character_id=character_id,
            account_id=account_id,
            character_version=version,
        )

    # -- R-26 -------------------------------------------------------------
    def revoke(
        self,
        *,
        context: WebAuthorizationContext,
        character_id: UUID,
        access_id: UUID,
        reason: str,
        expected_version: int,
        correlation_id: UUID,
        now: datetime,
    ) -> AccessChange:
        """Deactivate one link, **keeping the row**.

        The historical row keeps its grantor, reason, timestamps and correlation
        id; re-granting the same account inserts a new row rather than reviving
        this one, which is the compensating-action model the platform uses
        everywhere instead of erased history.

        Revoking the last active `owner` is permitted (OD-37). The response says
        so through `unresolved_owner`; nothing here refuses it and nothing here
        invents a replacement.
        """
        context.require_council()
        reason = self._require_reason(reason, correlation_id)
        self._require_character(character_id, correlation_id)

        row = self._access.get(access_id)
        # The access id is caller input, so "belongs to this character" is
        # checked rather than assumed: an id from another character would
        # otherwise revoke a link the Council member is not looking at.
        if row is None or row["character_id"] != character_id or not row["active"]:
            raise ObjectNotReachable(correlation_id)

        version = self._bump(character_id, expected_version, now, correlation_id)
        # The revocation's reason and actor go into the audit event below, not
        # onto the row: `character_access.reason` is why the link was *granted*,
        # and overwriting it would erase why somebody was given access in order
        # to record why they lost it.
        if not self._access.revoke(access_id=access_id, at=now):
            # Somebody else revoked it between the read and the write. Nothing
            # was applied twice; the caller is told the state moved.
            raise StaleVersion(correlation_id)

        self._audit.record(
            self._event(
                "character_access.revoked",
                access_id,
                context,
                correlation_id,
                {
                    "character_id": str(character_id),
                    "platform_account_id": str(row["platform_account_id"]),
                    "access_kind": row["access_kind"],
                    "before": {"active": True},
                    "after": {"active": False},
                    "character_version": version,
                    "reason": reason,
                    "left_character_without_active_owner": (
                        row["access_kind"] == "owner"
                        and self._access.active_owner(character_id) is None
                    ),
                },
            )
        )
        return AccessChange(
            access_id=access_id,
            character_id=character_id,
            account_id=row["platform_account_id"],
            character_version=version,
        )

    # -- R-27 -------------------------------------------------------------
    def set_default(
        self,
        *,
        context: WebAuthorizationContext,
        character_id: UUID,
        access_id: UUID,
        reason: str,
        expected_version: int,
        correlation_id: UUID,
        now: datetime,
    ) -> AccessChange:
        """Move the per-account default character to this link.

        The default is a property of the **account**, not of the character, so
        moving it clears the account's other active default in the same
        transaction. `uq_character_access_one_active_default_per_account` is what
        makes two concurrent moves resolve to one; clearing first is what makes
        the ordinary case a move rather than a refusal.
        """
        context.require_council()
        reason = self._require_reason(reason, correlation_id)
        self._require_character(character_id, correlation_id)

        row = self._access.get(access_id)
        if row is None or row["character_id"] != character_id or not row["active"]:
            raise ObjectNotReachable(correlation_id)

        account_id = row["platform_account_id"]
        previous = self._access.active_default_for_account(account_id)
        version = self._bump(character_id, expected_version, now, correlation_id)

        self._access.clear_default_for_account(account_id, at=now)
        if not self._access.set_default(access_id=access_id, at=now):
            raise StaleVersion(correlation_id)

        self._audit.record(
            self._event(
                "character_access.default_changed",
                access_id,
                context,
                correlation_id,
                {
                    "character_id": str(character_id),
                    "platform_account_id": str(account_id),
                    "before": {
                        "default_character_id": (
                            str(previous["character_id"]) if previous else None
                        )
                    },
                    "after": {"default_character_id": str(character_id)},
                    "character_version": version,
                    "reason": reason,
                },
            )
        )
        return AccessChange(
            access_id=access_id,
            character_id=character_id,
            account_id=account_id,
            character_version=version,
        )

    # -- helpers ----------------------------------------------------------
    def _require_character(self, character_id: UUID, correlation_id: UUID):
        character = self._access.character(character_id)
        if character is None:
            raise ObjectNotReachable(correlation_id)
        return character

    @staticmethod
    def _require_reason(reason: str | None, correlation_id: UUID) -> str:
        """Non-blank, and within §3.2's bound. Both refuse; neither truncates."""
        text = (reason or "").strip()
        if not text:
            raise BlankReason(correlation_id)
        if len(text) > REASON_BOUND:
            raise BlankReason(correlation_id)
        return text

    def _bump(
        self, character_id: UUID, expected_version: int, now: datetime, correlation_id: UUID
    ) -> int:
        """Take the character's optimistic version, or refuse `409`.

        This is the **first** write of every mutation, deliberately. It is a
        conditional `UPDATE … WHERE version = :expected`, so two concurrent
        Council members meet at that row: the loser matches zero rows and is
        refused before it has written anything at all, rather than after having
        inserted an access row it then has to be trusted to roll back.
        """
        version = self._access.bump_character_version(
            character_id=character_id, expected_version=expected_version, at=now
        )
        if version is None:
            raise StaleVersion(correlation_id)
        return version

    @staticmethod
    def _event(
        action: str,
        access_id: UUID,
        context: WebAuthorizationContext,
        correlation_id: UUID,
        payload: dict,
    ) -> AuditEvent:
        return AuditEvent(
            action=action,
            entity_type="character_access",
            entity_id=str(access_id),
            # The context's own. Every caller of this service is a request
            # handler, so it is always `WEB`; taking it from the context rather
            # than hard-coding the literal keeps the origin a property of who is
            # acting rather than of this module's current caller list.
            source=context.audit_source,
            # Council authority, always: these three operations exist under
            # OD-18's governance rule and are recorded under the authority that
            # makes them legal, not under whatever else the actor also holds.
            actor_capability=ActorCapability.GUILD_COUNCIL,
            correlation_id=correlation_id,
            actor_platform_account_id=context.account_id,
            payload=payload,
        )


__all__ = [
    "ACCESS_KINDS",
    "AccessChange",
    "BlankReason",
    "CharacterAccessService",
    "InvalidAccessKind",
    "REASON_BOUND",
    "StaleVersion",
]
