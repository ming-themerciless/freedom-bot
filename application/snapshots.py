"""Immutable records written by a snapshot import, and the bootstrap marker.

Every one of these is append-only in the database as well as here: the Phase 2
migration puts a trigger on `foundry_snapshots` and `snapshot_imports` that
refuses `UPDATE` and `DELETE` even for the schema owner, and the runtime role
holds `SELECT, INSERT` and nothing else.

There is deliberately no transaction record here. ADR 0008's generic balance and
`character_transactions` ledger was rejected on 2026-08-02: Phase 2 imports
identity, mappings and provenance, and has no balance to move. A compensating
history belongs to the typed package that owns the balance.

They are dataclasses rather than ORM objects on purpose. A record that cannot be
mutated in Python is one fewer way for a caller to "fix" history before it is
written.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Mapping
from uuid import UUID, uuid4

from application.audit import ActorCapability


class ImportMode(Enum):
    #: The one-time supervised first import. No separate approval; a named
    #: supervisor and an uninitialized dataset instead.
    BOOTSTRAP = "bootstrap"
    #: Every later import: one currently authorized Guild Council member.
    COUNCIL = "council"


class ImportStatus(Enum):
    APPLIED = "applied"
    #: The attempt was refused. It writes no state and claims no input identity,
    #: so the corrected retry is not blocked by it.
    REFUSED = "refused"


class SnapshotSource(Enum):
    """How an artifact reached the Manager.

    Recorded because the two routes carry different provenance and different
    authority. An operator placed a file on the host and ran a command as
    themselves; a Foundry module presented a scoped service credential and no
    human at all. An audit reader who could not tell them apart would be reading
    two different chains of custody as one.
    """

    #: A file an operator supplied to `tools.bootstrap_manager`.
    OPERATOR = "operator"
    #: An HTTPS submission from the Freedom Blades Foundry module, authenticated
    #: as a submit-only service principal.
    FOUNDRY_MODULE = "foundry_module"


@dataclass(frozen=True, slots=True)
class SnapshotRecord:
    """The immutable identity and provenance of one artifact."""

    checksum: str
    size_bytes: int
    schema_version: int
    exporter_id: str
    exporter_version: str
    exported_at: datetime
    world_id: str
    world_title: str
    core_version: str
    system_id: str
    system_version: str
    actor_count: int
    selected_folder_ids: tuple[str, ...]
    correlation_id: UUID
    received_by_discord_user_id: int | None = None
    #: A reference into the restricted artifact store. Never the bytes, and
    #: never something a report renders to a user who may not download it.
    artifact_location: str | None = None
    #: How the artifact arrived. Defaults to the operator path, which is what
    #: every record written before the submission endpoint existed came from.
    received_via: SnapshotSource = SnapshotSource.OPERATOR
    #: Which service principal presented it, for a module submission. There is
    #: no Discord user on that path, so this is the only attribution there is.
    submitted_by_principal: str | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if self.size_bytes <= 0:
            raise ValueError("A snapshot record needs the artifact's size.")
        if self.actor_count < 0:
            raise ValueError("An Actor count cannot be negative.")
        if not self.selected_folder_ids:
            raise ValueError("A snapshot record needs its exported folders.")
        # Provenance is required rather than optional (plan §6.4): a module
        # submission has no Discord user, so a record that also had no principal
        # would name nobody at all.
        if (
            self.received_via is SnapshotSource.FOUNDRY_MODULE
            and not (self.submitted_by_principal or "").strip()
        ):
            raise ValueError(
                "A module submission records the service principal that "
                "presented it. There is no acting Discord user on that path, so "
                "without it the record would have no attribution."
            )
        if (
            self.received_via is SnapshotSource.OPERATOR
            and self.submitted_by_principal is not None
        ):
            raise ValueError(
                "An operator-supplied artifact has no service principal. "
                "Recording one would assert a chain of custody that did not "
                "happen."
            )


#: The longest a caller-supplied request key may be. Matches the column, so an
#: over-long key is refused where it can be explained rather than truncated by
#: the database or rejected by the driver.
REQUEST_KEY_MAX_LENGTH = 255


@dataclass(frozen=True, slots=True)
class SnapshotImportRecord:
    """One apply attempt, applied or refused.

    Two identities, and they answer different questions.

    `request_key` identifies the *attempt*: a retry carrying the same key must
    receive the original result rather than apply a second time. This column is
    the **only** place the caller's text is kept, and it is kept because an exact
    match is what an idempotency lookup does. It is not copied into audit
    payloads, which carry a one-way `request_key_digest` instead (finding S-1),
    and a refused row is keyed by that digest rather than by the text.
    `operation_digest` identifies *what that key was for* — the immutable bound
    inputs of the operation the key was first spent on. Without it, the key
    alone was enough to retrieve the original receipt, so a different artifact,
    folder or profile presented under an old key received a receipt describing
    an operation it was not (finding B-1). Idempotency now means "same key **and**
    same bound operation"; a key reused for anything else fails closed.
    """

    snapshot_id: UUID
    folder_id: str
    folder_path: str
    profile_version: str
    request_key: str
    #: SHA-256 hex digest of the bound operation. See
    #: `application.foundry.import_service.operation_digest`, which is the one
    #: place it is computed.
    operation_digest: str
    status: ImportStatus
    mode: ImportMode
    actor_capability: ActorCapability
    summary: Mapping[str, Any]
    correlation_id: UUID
    actor_discord_user_id: int | None = None
    supervisor: str | None = None
    created_count: int = 0
    updated_count: int = 0
    warning_count: int = 0
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.request_key.strip():
            raise ValueError("An import attempt requires a request key.")
        # A request key is caller-supplied and is written verbatim into this
        # append-only row, which is the last place that still holds it.
        # Validating it here bounds the column rather than the exposure: control
        # characters would corrupt a rendered record, and an over-long key would
        # be a driver error rather than an explanation. Keeping the text out of
        # audit history is `request_key_digest`'s job, not this check's.
        if len(self.request_key) > REQUEST_KEY_MAX_LENGTH:
            raise ValueError(
                f"A request key may be at most {REQUEST_KEY_MAX_LENGTH} "
                f"characters; this one is {len(self.request_key)}."
            )
        if any(character < " " or character == "\x7f" for character in self.request_key):
            raise ValueError(
                "A request key must be printable text. It is recorded verbatim "
                "in append-only history, so a control character in it would "
                "corrupt every later rendering of that record."
            )
        if not _is_sha256_hex(self.operation_digest):
            raise ValueError(
                "An import attempt requires the SHA-256 digest of the operation "
                "its request key was spent on. Without it the key alone would "
                "identify the attempt, and a reused key could return a receipt "
                "for an operation it does not describe."
            )
        if min(self.created_count, self.updated_count, self.warning_count) < 0:
            raise ValueError("Import counts cannot be negative.")


def _is_sha256_hex(value: str) -> bool:
    return len(value) == 64 and all(
        character in "0123456789abcdef" for character in value
    )


@dataclass(frozen=True, slots=True)
class ExternalActorMapping:
    """An established link between a platform character and a Foundry Actor.

    The Foundry `_id` is the mapping key, not the identity: it does not survive
    a world rebuild, so `relink_fingerprint` carries name plus class and level
    at mapping time for a human re-establishing the link afterwards. That
    fingerprint is evidence for a person, never a matching rule for the
    importer.
    """

    character_id: UUID
    world_id: str
    external_actor_id: str
    relink_fingerprint: str
    folder_id: str | None = None
    established_by_snapshot_id: UUID | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.world_id.strip():
            raise ValueError("A mapping requires a world id.")
        if not self.relink_fingerprint.strip():
            raise ValueError("A mapping requires a re-link fingerprint.")


@dataclass(frozen=True, slots=True)
class PlatformInitialization:
    """Written once. Its existence is what disables the bootstrap."""

    supervisor: str
    profile_version: str
    correlation_id: UUID
    snapshot_checksum: str | None = None
    initialized_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.supervisor.strip():
            raise ValueError("An initialization record names its supervisor.")
