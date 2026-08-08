"""Non-human callers, and the narrow capabilities each of them holds.

A service principal is the bot, the Foundry module, an import worker or a
scheduled worker (plan §4.1). It is **not** a user: it carries no Discord
identity, no guild membership and no game-policy authority, and nothing here
converts one into the other.

The Foundry submitter holds exactly one capability, and the list below is the
whole of it. That is the control that makes a leaked module credential a bounded
problem: the worst it can do is create an unwanted **pending** artifact, which
no Council member has confirmed and which applies nothing.

Scopes are an enum rather than free-text strings because a typo in a string
scope is silently a *different* scope, and the direction it fails in is the
dangerous one — a check against `"foundry:snapshot:submitt"` passes for a
principal that was granted the same typo and fails closed for everyone else,
which looks like working authorization right up until it does not.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from application.authorization import NotAuthorizedError


class ServicePrincipalScope(Enum):
    """Every capability a service principal may be granted.

    One entry today. A second one is a decision, not a convenience: adding a
    scope here is the moment to ask which credential will hold it and what a
    leak of that credential would then permit.
    """

    #: Submit an immutable snapshot artifact for later Council review. Explicitly
    #: not: apply an import, read Council data, read audit history, mutate a
    #: character, or reach PostgreSQL other than through this one use case.
    SUBMIT_SNAPSHOT = "foundry:snapshot:submit"


#: What an identifier may look like. It is recorded in append-only audit rows and
#: rendered in operator-facing logs, so it is a short closed-vocabulary token
#: chosen by the operator, not arbitrary caller text.
_ID_CHARACTERS = set("abcdefghijklmnopqrstuvwxyz0123456789-_")
ID_MAX_LENGTH = 64


@dataclass(frozen=True, slots=True)
class ServicePrincipal:
    """One credential's identity and its granted scopes."""

    principal_id: str
    scopes: frozenset[ServicePrincipalScope]

    def __post_init__(self) -> None:
        identifier = self.principal_id
        if not identifier or len(identifier) > ID_MAX_LENGTH:
            raise ValueError(
                f"A service principal id is 1–{ID_MAX_LENGTH} characters."
            )
        if not set(identifier) <= _ID_CHARACTERS:
            raise ValueError(
                "A service principal id may hold lower-case letters, digits, "
                "'-' and '_' only. It is written into append-only audit history "
                "and into operator logs, so it is a chosen token rather than "
                "free text."
            )
        if not self.scopes:
            raise ValueError(
                f"Service principal {identifier!r} holds no scope, so it can do "
                "nothing. Grant it a scope or remove it from configuration; a "
                "credential that authenticates and then fails every check is a "
                "confusing way to say 'revoked'."
            )

    def holds(self, scope: ServicePrincipalScope) -> bool:
        return scope in self.scopes

    def require(self, scope: ServicePrincipalScope, action: str) -> None:
        """Refuse unless this principal currently holds `scope`.

        The refusal names the action and the scope, never the credential and
        never the other scopes this principal does hold: an error message is a
        reply to whoever presented the credential, and telling them what else it
        is good for is not something the reply needs to do.
        """
        if not self.holds(scope):
            raise NotAuthorizedError(
                f"{action} requires the {scope.value} scope, which this service "
                "principal does not hold.",
                code="out_of_scope",
            )
