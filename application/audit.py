"""The append-only audit record, as an application-level concept.

Audit rows are written by the same transaction as the change they describe, so
a committed mutation always carries its trail and a rolled-back one leaves
none.
"""
from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any
from uuid import UUID, uuid4


class ActorCapability(Enum):
    """The authority an action was taken under, not merely who took it."""

    GUILD_MEMBER = "guild_member"
    CHARACTER_OWNER = "character_owner"
    DM = "dm"
    GUILD_COUNCIL = "guild_council"
    PLATFORM_ADMINISTRATOR = "platform_administrator"
    SERVICE_PRINCIPAL = "service_principal"
    SYSTEM = "system"


#: The capabilities that may act without an identified *person*. They match the
#: `human_action_has_an_attribution` check constraint installed by migration
#: 0006.
#:
#: **This guard changed with that migration, and had to.** Until Phase 3 the rule
#: was "a human capability requires an acting *Discord user*", enforced here and
#: by `ck_audit_events_human_action_has_an_actor`. A break-glass administrator
#: acting while Discord is unavailable is a human capability with **no** Discord
#: user id (ADR 0010 D8), so the old rule refused the audit event that the
#: emergency path must write — and because SM-03 commits the emergency session
#: and its audit event in one transaction, it refused the emergency login itself.
#:
#: The rule was not relaxed. Its subject was widened from *a Discord user* to
#: *an identified person*: either attribution column satisfies it, and an
#: unattributed human action is still refused. Changing the database without
#: changing this guard would have left the platform refusing in Python instead
#: of in SQL, which is why the two moved in one revision (schema §6.1.1).
UNATTENDED_CAPABILITIES = frozenset(
    {ActorCapability.SERVICE_PRINCIPAL, ActorCapability.SYSTEM}
)


class AuditSource(Enum):
    DISCORD = "discord"
    WEB = "web"
    FOUNDRY = "foundry"
    IMPORT = "import"
    SYSTEM = "system"


#: The scalar types an audit payload may hold. Deliberately narrow: an audit row
#: is serialized to JSON in the database adapter, so anything that cannot survive
#: that round trip is rejected here rather than at the driver. A `float` is
#: additionally required to be finite — `NaN` and the infinities are Python
#: floats and valid `json.dumps` output, but they are not valid JSON and
#: PostgreSQL refuses them in a JSONB column. See `_freeze_payload`.
PAYLOAD_SCALARS = (str, int, float, bool, type(None))


class UnsupportedAuditPayloadError(TypeError):
    """A payload held a value an audit row cannot faithfully record."""


def _freeze_payload(value: Any, *, path: str) -> Any:
    """Recursively return an immutable equivalent of a JSON-like value.

    Freezing only the outer mapping would leave the contract false for every
    payload this platform actually writes: `{"changes": {...}}` is nested, and a
    caller keeping its own reference to the inner dictionary could alter what the
    audit says after the event was constructed.
    """
    # bool is an int subclass and must be tested before the Mapping/Sequence
    # branches only in the sense that str is a Sequence; order matters below.
    if isinstance(value, float) and not math.isfinite(value):
        raise UnsupportedAuditPayloadError(
            f"Audit payload {path} holds {value!r}, which is not a finite number. "
            "PostgreSQL cannot store NaN or infinity in a JSONB column, so the "
            "whole audited mutation would fail at the driver. Convert it to a "
            "finite number, a string or null at the call site."
        )
    if isinstance(value, PAYLOAD_SCALARS):
        return value
    if isinstance(value, Mapping):
        return MappingProxyType(
            {
                _payload_key(key, path=path): _freeze_payload(
                    item, path=f"{path}.{key}"
                )
                for key, item in value.items()
            }
        )
    if isinstance(value, (str, bytes, bytearray)):
        # str is handled above; bytes are not JSON and must not be guessed at.
        raise UnsupportedAuditPayloadError(
            f"Audit payload {path} holds bytes, which an audit row cannot record."
        )
    if isinstance(value, Sequence):
        return tuple(
            _freeze_payload(item, path=f"{path}[{index}]")
            for index, item in enumerate(value)
        )
    raise UnsupportedAuditPayloadError(
        f"Audit payload {path} holds {type(value).__name__}, which an audit row "
        "cannot record. Convert it to a string, number, boolean, mapping or "
        "sequence at the call site so the recorded value is explicit."
    )


def _payload_key(key: Any, *, path: str) -> str:
    if not isinstance(key, str):
        raise UnsupportedAuditPayloadError(
            f"Audit payload {path} is keyed by {type(key).__name__}; JSON object "
            "keys must be strings."
        )
    return key


def _plain(value: Any) -> Any:
    """The mirror of `_freeze_payload`: a plain, JSON-serializable equivalent.

    `MappingProxyType` and `tuple` are what the freeze produces and neither is
    accepted by the JSON serializer the database adapter hands to the driver, so
    the adapter converts back at the persistence boundary rather than storing a
    mutable payload to keep the driver happy.
    """
    if isinstance(value, PAYLOAD_SCALARS):
        return value
    if isinstance(value, Mapping):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, Sequence):
        return [_plain(item) for item in value]
    raise UnsupportedAuditPayloadError(
        f"{type(value).__name__} cannot be serialized into an audit row."
    )


@dataclass(frozen=True, slots=True)
class AuditEvent:
    action: str
    entity_type: str
    entity_id: str
    source: AuditSource
    actor_capability: ActorCapability
    correlation_id: UUID
    payload: Mapping[str, Any]
    actor_discord_user_id: int | None = None
    #: The stable platform account that acted (ADR 0010 D1). New rows carry it;
    #: history keeps only its Discord column and is never rewritten, so a read
    #: resolves the older form through `external_identities` (schema §6.5).
    actor_platform_account_id: UUID | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.action.strip():
            raise ValueError("An audit event requires an action.")
        if not self.entity_type.strip():
            raise ValueError("An audit event requires an entity type.")
        if not self.entity_id.strip():
            raise ValueError("An audit event requires an entity id.")
        if (
            self.actor_discord_user_id is None
            and self.actor_platform_account_id is None
            and self.actor_capability not in UNATTENDED_CAPABILITIES
        ):
            raise ValueError(
                f"{self.actor_capability.value} is a human capability and requires "
                "an identified actor: a platform account, or the Discord user id "
                "history was written with. Either satisfies the attribution rule; "
                "neither is not an option."
            )
        if self.actor_discord_user_id is not None and self.actor_discord_user_id <= 0:
            raise ValueError("Discord IDs must be positive snowflakes.")
        # The payload is frozen with the event, all the way down: a caller that
        # keeps its dictionary — or a nested one inside it — cannot alter what
        # the audit says after the fact.
        object.__setattr__(self, "payload", _freeze_payload(dict(self.payload), path="payload"))

    def json_payload(self) -> dict[str, Any]:
        """The payload as plain JSON-serializable structures, for persistence."""
        return _plain(self.payload)
