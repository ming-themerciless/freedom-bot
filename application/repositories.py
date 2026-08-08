from __future__ import annotations

from typing import Protocol
from uuid import UUID

from application.audit import AuditEvent
from application.idempotency import IdempotencyRecord
from application.imports import SheetRowMapping
from application.snapshots import (
    ExternalActorMapping,
    PlatformInitialization,
    SnapshotImportRecord,
    SnapshotRecord,
)
from domain.identity import Character, DiscordUser


class CharacterRepository(Protocol):
    def add(self, character: Character) -> None: ...

    def get(self, character_id: UUID) -> Character | None: ...

    def save(self, character: Character, *, expected_version: int) -> Character: ...

    def find_by_display_name(self, display_name: str) -> tuple[Character, ...]:
        """Every character claiming the same identity as `display_name`.

        The comparison is `DisplayName.claims_same_identity_as` — NFC-normalised
        full case folding — and every implementation must answer for the whole
        of that domain, not for the part a particular database collation happens
        to agree with. A narrower implementation would silently reintroduce the
        Phase 2 normalisation defect: a name the caller believes is free while
        the platform already holds it.

        This returns a tuple rather than one character because display names
        carry no uniqueness constraint: two matches are a reconciliation
        finding for the caller to report, not an error to raise here.
        """
        ...


class DiscordUserRepository(Protocol):
    def add(self, user: DiscordUser) -> None: ...

    def get(self, discord_id: int) -> DiscordUser | None: ...


class SheetRowMappingRepository(Protocol):
    def add(self, mapping: SheetRowMapping) -> None: ...

    def get_character_id(self, sheet_tab: str, row_index: int) -> UUID | None: ...

    def list_for_tab(self, sheet_tab: str) -> tuple[SheetRowMapping, ...]: ...


class AuditRepository(Protocol):
    def record(self, event: AuditEvent) -> None:
        """Append one event. There is deliberately no update or delete."""
        ...


class ExternalActorMappingRepository(Protocol):
    """Links between platform characters and Foundry Actors.

    Established deliberately, never inferred from a name (ADR 0006). There is no
    `find_by_name` here, and adding one would be the defect rather than a
    convenience.
    """

    def add(self, mapping: ExternalActorMapping) -> None: ...

    def get_by_actor(
        self, world_id: str, external_actor_id: str
    ) -> ExternalActorMapping | None: ...

    def list_for_world(self, world_id: str) -> tuple[ExternalActorMapping, ...]: ...


class SnapshotRepository(Protocol):
    def add(self, record: SnapshotRecord) -> SnapshotRecord: ...

    def get_by_checksum(self, checksum: str) -> SnapshotRecord | None: ...


class SnapshotImportRepository(Protocol):
    def add(self, record: SnapshotImportRecord) -> None: ...

    def find_by_request_key(self, request_key: str) -> SnapshotImportRecord | None: ...

    def find_applied(
        self, snapshot_id: UUID, folder_id: str, profile_version: str
    ) -> SnapshotImportRecord | None: ...


class IdempotencyRepository(Protocol):
    """Receipts for completed operations, keyed by scope and caller key.

    There is deliberately no `update`: a record is written when its operation
    commits and never changed afterwards. A receipt that could be rewritten
    would let a later request quietly redefine what an earlier one returned.
    """

    def add(self, record: IdempotencyRecord) -> None: ...

    def find(self, scope: str, key: str) -> IdempotencyRecord | None: ...


class PlatformInitializationRepository(Protocol):
    def get(self) -> PlatformInitialization | None: ...

    def record(self, initialization: PlatformInitialization) -> None: ...

    def is_dataset_empty(self) -> bool:
        """No characters, mappings, snapshots or history exist yet."""
        ...


class UnitOfWork(Protocol):
    characters: CharacterRepository
    discord_users: DiscordUserRepository
    sheet_row_mappings: SheetRowMappingRepository
    audit: AuditRepository
    external_actor_mappings: ExternalActorMappingRepository
    snapshots: SnapshotRepository
    snapshot_imports: SnapshotImportRepository
    idempotency: IdempotencyRepository
    initialization: PlatformInitializationRepository

    def __enter__(self) -> UnitOfWork: ...

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
