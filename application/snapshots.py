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
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if self.size_bytes <= 0:
            raise ValueError("A snapshot record needs the artifact's size.")
        if self.actor_count < 0:
            raise ValueError("An Actor count cannot be negative.")
        if not self.selected_folder_ids:
            raise ValueError("A snapshot record needs its exported folders.")


@dataclass(frozen=True, slots=True)
class SnapshotImportRecord:
    """One apply attempt, applied or refused."""

    snapshot_id: UUID
    folder_id: str
    folder_path: str
    profile_version: str
    request_key: str
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
        if min(self.created_count, self.updated_count, self.warning_count) < 0:
            raise ValueError("Import counts cannot be negative.")


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
