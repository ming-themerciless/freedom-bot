"""Who may do what, resolved at the moment the work is done.

Two rules, and the second is the one that is easy to get wrong:

1. **One currently authorized Guild Council member is sufficient.** There is no
   second approver and no four-eyes workflow for a snapshot import or a
   correction (maintainer ruling; plan §8.2).
2. **Preview permission is not apply permission.** Guild membership and the
   Council role are re-resolved when the change is applied, not carried over
   from when it was previewed. A role revoked in between refuses the action
   (plan §6.5, *role changes take effect at apply*).

Rule 2 is why `AuthorizationPort` exists at all rather than the caller simply
passing a context object around: a context is a *reading*, and a reading has a
time. The port is asked again.

A cached Discord role is display data. The port implementation is responsible
for resolving effective privilege server-side; nothing here treats a value the
caller supplied as proof of anything.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from application.audit import ActorCapability


class NotAuthorizedError(PermissionError):
    """The acting user does not currently hold the required capability."""

    def __init__(self, message: str, *, code: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class AuthorizationContext:
    """One resolution of one user's current effective privilege."""

    discord_user_id: int
    guild_member: bool = False
    guild_council: bool = False
    platform_administrator: bool = False

    def __post_init__(self) -> None:
        if self.discord_user_id <= 0:
            raise ValueError("Discord IDs must be positive snowflakes.")

    @property
    def capability(self) -> ActorCapability:
        """The authority an action taken now would be recorded under."""
        if self.guild_council:
            return ActorCapability.GUILD_COUNCIL
        if self.platform_administrator:
            return ActorCapability.PLATFORM_ADMINISTRATOR
        return ActorCapability.GUILD_MEMBER

    def require_council(self, action: str) -> None:
        """One current Council member is enough — and is also required."""
        if not self.guild_member:
            raise NotAuthorizedError(
                f"{action} requires membership of the Freedom Blades guild, "
                "which this user does not currently hold.",
                code="not_a_guild_member",
            )
        if not self.guild_council:
            # Platform Administrator is an operational role and deliberately
            # does not imply game-policy authority (plan §4.1). An administrator
            # who is not also Council cannot apply an import or a correction.
            raise NotAuthorizedError(
                f"{action} requires current Guild Council authorization.",
                code="not_guild_council",
            )

    def require_platform_administrator(self, action: str) -> None:
        if not self.guild_member or not self.platform_administrator:
            raise NotAuthorizedError(
                f"{action} requires current Platform Administrator authorization.",
                code="not_platform_administrator",
            )


class AuthorizationPort(Protocol):
    """Resolves current effective privilege. Asked again at apply time."""

    def context_for(self, discord_user_id: int) -> AuthorizationContext: ...


@dataclass(frozen=True, slots=True)
class SupervisedBootstrap:
    """The one path that does not require a Council member.

    The supervised first import is a bootstrap operation and needs no separate
    approval (plan §6.4). It still records the named supervisor, and it is
    available only against an uninitialized dataset — which is enforced by the
    `platform_initialization` singleton, not by this object.
    """

    supervisor: str

    def __post_init__(self) -> None:
        if not self.supervisor.strip():
            raise ValueError("A supervised bootstrap requires a named supervisor.")
        if len(self.supervisor) > 120:
            raise ValueError("A supervisor name is at most 120 characters.")

    @property
    def capability(self) -> ActorCapability:
        return ActorCapability.SYSTEM
