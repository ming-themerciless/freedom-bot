"""Capability resolution, administrator scope, and the guard SM-07 exists for.

Two questions are answered here, and confusing them is the defect the P3.0
remediation was written to close:

1. **What may this session do right now?** A union over the active
   role-capability mappings that match the caller's *currently observed* Discord
   roles — never a value read from the session row, the request, or the page that
   was rendered.
2. **Where did this session's administrator authority come from?** Its
   *administrator scope*. A session whose `platform_administrator` capability
   descends only from mappings created under emergency authority is itself
   continuity-scoped, and stays so through an ordinary login, until a full-scope
   administrator ratifies (R-38).

## Why question 2 is not answerable by question 1

The first revision of ADR 0010 held that short-circuiting capability resolution
on `auth_method` was sufficient. It is not, and the reason is worth keeping in
front of anyone editing this module. Short-circuiting bounds what an emergency
session may *do while it exists*; it says nothing about what that session may
**arrange**:

    compromised break-glass session
      └─ map a role the attacker holds -> guild_council
           └─ log in through Discord as an ordinary member holding that role
                └─ capability resolution returns {guild_council}: no
                   short-circuit applies, because auth_method is now
                   discord_oauth
                     └─ apply an import

Every individual control held. The authority was laundered through a durable row.
And a narrower allowlist alone does not close it either: a mapping to
`platform_administrator` yields an ordinary administrator who may then map
anything, as administrators legitimately may.

So the guard travels with the **mapping**, not with the session:
`administrator_scope` is transitive by construction, and the second hop resolves
to `emergency_continuity` exactly as the first did.

This module is one of three independent controls. The other two are the check
constraint `created_under_scope = 'full' OR capability = 'platform_administrator'`
in PostgreSQL, which depends on what is being written rather than on who is
writing it, and N-65's route surface. None of them is the only one.
"""
from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import Iterable
from uuid import UUID

from application.audit import ActorCapability
from application.web.errors import (
    EmergencyScopeRefused,
    InsufficientCapability,
    NotAMember,
)


class AuthMethod(Enum):
    """How the session was authenticated. `sessions.auth_method`."""

    DISCORD_OAUTH = "discord_oauth"
    WEBAUTHN = "webauthn"
    RECOVERY_GRANT = "recovery_grant"

    @property
    def session_class(self) -> "SessionClass":
        """Which lifetime rule governs this method's sessions. Looked up, not inferred."""
        return session_class_of(self)

    @property
    def is_ordinary_provider(self) -> bool:
        return self.session_class is SessionClass.ORDINARY

    @property
    def is_break_glass(self) -> bool:
        return self.session_class is SessionClass.BREAK_GLASS


class SessionClass(Enum):
    """Which body of lifetime rules a session falls under.

    `ORDINARY` is N-06/N-07 — sixty-minute idle, twelve-hour absolute.
    `BREAK_GLASS` is N-15 — fifteen-minute idle, sixty-minute absolute.

    It exists as a named concept rather than as a boolean because the thing that
    must be *explicit* for every authentication method is which of the two it is
    (see `_SESSION_CLASSES`). "Not the ordinary provider" is an inference; a
    `SessionClass` written next to a method is a decision.
    """

    ORDINARY = "ordinary"
    BREAK_GLASS = "break_glass"


class UnclassifiedAuthMethod(Exception):
    """An authentication method whose lifetime class nobody decided.

    Raised at import of this module (so an unclassified method is a startup
    failure) and again wherever a classification is looked up (so it is a
    construction failure even if the table is reached in some other state).

    It is deliberately not a `KeyError`: a caller that caught `KeyError` around a
    lookup and fell back to a default would be reintroducing exactly the silent
    default this refusal exists to prevent.
    """


#: **Every** authentication method's lifetime class, written out. Requirement 5
#: of the 2026-08-15 idle-policy-construction remediation.
#:
#: This replaced `is_break_glass = not is_ordinary_provider` (removed the same
#: day). That derivation classified a *future* method automatically, and the
#: direction it chose — break-glass, the shorter window — was defended as the
#: safe default. It is not safe enough, and the reason is that it is silent: a
#: method added for a new ordinary provider, or for a machine-to-machine grant
#: with lifetime rules of its own, would quietly acquire N-15's fifteen minutes
#: and nobody would be asked. A window nobody chose is a window nobody reviewed,
#: whichever of the two it happens to be.
#:
#: Adding a member to `AuthMethod` without adding it here therefore fails at
#: import — visibly, at startup, naming the method — rather than being governed
#: by inference. Adding it here is one line, and that line is the decision.
_SESSION_CLASSES: Mapping[AuthMethod, SessionClass] = MappingProxyType(
    {
        AuthMethod.DISCORD_OAUTH: SessionClass.ORDINARY,
        AuthMethod.WEBAUTHN: SessionClass.BREAK_GLASS,
        AuthMethod.RECOVERY_GRANT: SessionClass.BREAK_GLASS,
    }
)


def unclassified_methods(
    methods: Iterable[Enum], classification: Mapping[Enum, SessionClass]
) -> tuple[str, ...]:
    """The members of `methods` that `classification` does not govern, by value.

    Generic over the enum deliberately, and that is not abstraction for its own
    sake: it is what lets the guard below be *tested* honestly. A test cannot add
    a member to `AuthMethod` — enums are closed — so a test that wanted to prove
    "a future method is refused" would otherwise have to assert on the shape of
    the source. Given a synthetic enum with a member the table omits, this runs
    the same code the real check runs.
    """
    return tuple(
        sorted(
            str(method.value)
            for method in methods
            if method not in classification
        )
    )


def require_complete_classification(
    methods: Iterable[Enum], classification: Mapping[Enum, SessionClass]
) -> None:
    """Refuse a classification table that does not govern every method."""
    missing = unclassified_methods(methods, classification)
    if missing:
        raise UnclassifiedAuthMethod(
            "every authentication method must be explicitly classified as "
            "ordinary or break-glass before it can govern a session; "
            f"unclassified: {', '.join(missing)}. Add it to _SESSION_CLASSES in "
            "application/web/capabilities.py — deciding its session lifetime is "
            "the point of the entry, not a formality."
        )


# The startup half of requirement 5. An `AuthMethod` member added without an
# entry above makes this module unimportable, which is what "fail safely and
# visibly" means for a value that would otherwise be inferred in silence.
require_complete_classification(AuthMethod, _SESSION_CLASSES)


def session_class_of(auth_method: AuthMethod) -> SessionClass:
    """This method's lifetime class, or a refusal. Never a default.

    The type check is not decoration. `"webauthn"` — the persisted string rather
    than the member — is not a key of the table, and a lookup that fell back on
    `KeyError` would give it whichever branch the fallback named. A value that is
    not an `AuthMethod` has no session class, and that is the answer.
    """
    if not isinstance(auth_method, AuthMethod):
        raise TypeError(
            "a session class is defined for AuthMethod members, not "
            f"{auth_method!r}"
        )
    try:
        return _SESSION_CLASSES[auth_method]
    except KeyError:
        raise UnclassifiedAuthMethod(
            f"{auth_method.value} has no explicit session class; it cannot "
            "govern a session lifetime until one is decided in "
            "application/web/capabilities.py"
        ) from None


class AdministratorScope(Enum):
    """Whether administrator authority is ordinary or emergency-derived."""

    FULL = "full"
    EMERGENCY_CONTINUITY = "emergency_continuity"


class MappingProvenance(Enum):
    ORDINARY = "ordinary"
    EMERGENCY_CONTINUITY = "emergency_continuity"


#: N-12. A break-glass session resolves to exactly this, whatever Discord roles
#: the same human holds. Never Council, never character ownership, never
#: import-apply authority by implication.
BREAK_GLASS_CAPABILITIES = frozenset({ActorCapability.PLATFORM_ADMINISTRATOR})

#: N-67. The only capability a continuity-scoped caller may name when creating or
#: revoking a role-capability mapping.
CONTINUITY_ALLOWED_CAPABILITY = ActorCapability.PLATFORM_ADMINISTRATOR

#: A Discord role may confer any of these. The two machine capabilities are
#: absent: a human holding a role is not a service.
MAPPABLE_CAPABILITIES = frozenset(
    {
        ActorCapability.GUILD_MEMBER,
        ActorCapability.CHARACTER_OWNER,
        ActorCapability.DM,
        ActorCapability.GUILD_COUNCIL,
        ActorCapability.PLATFORM_ADMINISTRATOR,
    }
)


@dataclass(frozen=True, slots=True)
class RoleCapabilityMapping:
    """One active mapping, as capability resolution needs to see it."""

    id: UUID
    guild_id: int
    role_id: int
    capability: ActorCapability
    provenance: MappingProvenance
    protected: bool = False


@dataclass(frozen=True, slots=True)
class MembershipProjection:
    """What the adapter last successfully observed at the provider (SM-06).

    It is a **projection**, not proof: `observed_at` is what N-09 and N-10 bound,
    and a projection older than the grace cannot authorize anything.
    """

    guild_id: int
    is_member: bool
    role_ids: frozenset[int]
    observed_at: datetime

    def is_fresh(self, *, now: datetime, cache_seconds: int) -> bool:
        return (now - self.observed_at).total_seconds() <= cache_seconds

    def within_grace(self, *, now: datetime, grace_seconds: int) -> bool:
        return (now - self.observed_at).total_seconds() <= grace_seconds


@dataclass(frozen=True, slots=True)
class WebAuthorizationContext:
    """One resolution of one session's current effective privilege.

    A *reading*, and a reading has a time — which is why it is produced fresh on
    every request rather than carried on the session row. Nothing here is ever
    taken from something the caller supplied.
    """

    account_id: UUID
    auth_method: AuthMethod
    capabilities: frozenset[ActorCapability]
    administrator_scope: AdministratorScope
    membership: MembershipProjection | None

    @property
    def guild_member(self) -> bool:
        return ActorCapability.GUILD_MEMBER in self.capabilities

    @property
    def guild_council(self) -> bool:
        return ActorCapability.GUILD_COUNCIL in self.capabilities

    @property
    def platform_administrator(self) -> bool:
        return ActorCapability.PLATFORM_ADMINISTRATOR in self.capabilities

    @property
    def is_continuity_scoped(self) -> bool:
        """`BG` **or** `AC`: the eighth caller state and the one it descends from.

        Route contract §3.3: every matrix cell's `BG` value applies unchanged to
        `AC`. Expressing that as one property rather than two columns is what
        stops the two drifting apart in a later edit.
        """
        return self.administrator_scope is AdministratorScope.EMERGENCY_CONTINUITY

    @property
    def capability(self) -> ActorCapability:
        """The authority an action taken now would be **recorded** under.

        Council outranks administrator, matching the existing
        `application.authorization.AuthorizationContext`: when both are held, an
        act is a Council act, because that is the authority that makes it legal.
        """
        if self.guild_council:
            return ActorCapability.GUILD_COUNCIL
        if self.platform_administrator:
            return ActorCapability.PLATFORM_ADMINISTRATOR
        return ActorCapability.GUILD_MEMBER

    @property
    def privilege_fingerprint(self) -> bytes:
        """N-08's rotation trigger.

        Over the sorted capability set, guild membership **and the administrator
        scope**. The scope belongs in it because ratification (R-38) can change
        an account's scope without changing its capability set, and TC-CAP-10
        requires the affected sessions to rotate on that change rather than carry
        the old scope to their next request.
        """
        member = "1" if self.guild_member else "0"
        capabilities = ",".join(sorted(c.value for c in self.capabilities))
        material = (
            f"{capabilities}|member={member}|scope={self.administrator_scope.value}"
        )
        return hashlib.sha256(material.encode("utf-8")).digest()

    def require_guild_member(self) -> None:
        if not self.guild_member:
            raise NotAMember()

    def require_council(self) -> None:
        """One current Council member is enough — and is also required.

        A break-glass session never reaches here with Council, because resolution
        short-circuited its capability set; and it is refused again at the route
        surface by N-65. Two controls, neither of them the only one.
        """
        self.require_guild_member()
        if not self.guild_council:
            # Platform Administrator is an operational role and deliberately does
            # not imply game-policy authority (plan §4.1, OD-24).
            raise InsufficientCapability()

    def require_platform_administrator(self) -> None:
        if not self.platform_administrator:
            raise InsufficientCapability()

    def require_full_administrator_scope(self) -> None:
        """R-38's precondition, and the door between emergency and ordinary.

        A `403` here during an incident is not a defect to be worked around: it
        is the boundary. Ratification waits until an administrator can
        authenticate normally.
        """
        self.require_platform_administrator()
        if self.auth_method is not AuthMethod.DISCORD_OAUTH:
            raise EmergencyScopeRefused()
        if self.administrator_scope is not AdministratorScope.FULL:
            raise EmergencyScopeRefused()

    def require_mapping_capability_allowed(self, capability: ActorCapability) -> None:
        """N-67, control 1 of 3: refused **before any row is read or written**.

        The other two are the check constraint in PostgreSQL — which does not
        depend on the session at all, only on what is being written — and N-65's
        route surface.
        """
        if capability not in MAPPABLE_CAPABILITIES:
            raise InsufficientCapability()
        if not self.is_continuity_scoped:
            return
        if capability is not CONTINUITY_ALLOWED_CAPABILITY:
            raise EmergencyScopeRefused()


def resolve_capabilities(
    *,
    account_id: UUID,
    auth_method: AuthMethod,
    membership: MembershipProjection | None,
    mappings: Iterable[RoleCapabilityMapping],
) -> WebAuthorizationContext:
    """Produce the caller's current authority. The only place capability is decided.

    Break-glass short-circuits first and completely: an emergency session gets
    exactly `{platform_administrator}` and **no membership projection at all**,
    because break-glass never touches the Discord projection (route contract
    §7.3). Whatever roles the same human holds on Discord are irrelevant to what
    this session may do.
    """
    if auth_method.is_break_glass:
        return WebAuthorizationContext(
            account_id=account_id,
            auth_method=auth_method,
            capabilities=BREAK_GLASS_CAPABILITIES,
            administrator_scope=AdministratorScope.EMERGENCY_CONTINUITY,
            membership=None,
        )

    if membership is None or not membership.is_member:
        # Caller state `N`: a session whose membership has since been revoked.
        # It keeps its account and its session and holds no capability at all.
        return WebAuthorizationContext(
            account_id=account_id,
            auth_method=auth_method,
            capabilities=frozenset(),
            administrator_scope=AdministratorScope.FULL,
            membership=membership,
        )

    matching = [
        mapping
        for mapping in mappings
        if mapping.guild_id == membership.guild_id
        and mapping.role_id in membership.role_ids
    ]
    # A **union**. Adding a mapping can never subtract a capability, which is
    # half of why there is no application path to administrator lockout (the
    # other half is the trigger refusing any change to the protected row).
    capabilities = {mapping.capability for mapping in matching}
    capabilities.add(ActorCapability.GUILD_MEMBER)

    scope = _administrator_scope(matching, capabilities)
    return WebAuthorizationContext(
        account_id=account_id,
        auth_method=auth_method,
        capabilities=frozenset(capabilities),
        administrator_scope=scope,
        membership=membership,
    )


def _administrator_scope(
    matching: list[RoleCapabilityMapping], capabilities: set[ActorCapability]
) -> AdministratorScope:
    """`emergency_continuity` when *every* conferring mapping is emergency-derived.

    "Every", not "any": an administrator who also holds the authority through an
    ordinary mapping — in practice the protected bootstrap row, which is
    `ordinary` by construction and cannot be edited — is a full-scope
    administrator. That is what makes ratification reachable at all, and it is
    why the protected row's provenance is fixed by migration rather than by the
    application.
    """
    if ActorCapability.PLATFORM_ADMINISTRATOR not in capabilities:
        # Scope is a property of administrator authority. A member or Council
        # member holds none, so there is nothing to confine and `FULL` is the
        # neutral answer rather than a claim about them.
        return AdministratorScope.FULL

    conferring = [
        mapping
        for mapping in matching
        if mapping.capability is ActorCapability.PLATFORM_ADMINISTRATOR
    ]
    if conferring and all(
        mapping.provenance is MappingProvenance.EMERGENCY_CONTINUITY
        for mapping in conferring
    ):
        return AdministratorScope.EMERGENCY_CONTINUITY
    return AdministratorScope.FULL


__all__ = [
    "AdministratorScope",
    "AuthMethod",
    "BREAK_GLASS_CAPABILITIES",
    "CONTINUITY_ALLOWED_CAPABILITY",
    "MAPPABLE_CAPABILITIES",
    "MappingProvenance",
    "MembershipProjection",
    "RoleCapabilityMapping",
    "SessionClass",
    "UnclassifiedAuthMethod",
    "WebAuthorizationContext",
    "require_complete_classification",
    "resolve_capabilities",
    "session_class_of",
    "unclassified_methods",
]
