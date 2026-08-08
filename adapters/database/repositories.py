from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import func, insert, select, update
from sqlalchemy.orm import Session

from application.audit import ActorCapability, AuditEvent
from application.errors import ConcurrencyConflictError
from application.idempotency import IdempotencyRecord, IdempotencyStatus
from application.imports import SheetRowMapping
from application.snapshots import (
    ExternalActorMapping,
    ImportMode,
    ImportStatus,
    PlatformInitialization,
    SnapshotImportRecord,
    SnapshotRecord,
    SnapshotSource,
)
from domain.identity import Character, DiscordUser
from domain.names import DisplayName

from .mappers import character_from_row, discord_user_from_row, sheet_row_mapping_from_row
from .tables import (
    audit_events,
    characters,
    discord_users,
    external_actor_mappings,
    foundry_snapshots,
    idempotency_keys,
    platform_initialization,
    sheet_row_mappings,
    snapshot_imports,
)


class SqlAlchemyCharacterRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, character: Character) -> None:
        self._session.execute(
            insert(characters).values(
                id=character.id,
                display_name=character.display_name,
                long_name=character.long_name,
                level=character.level,
                active=character.active,
                version=character.version,
            )
        )

    def get(self, character_id: UUID) -> Character | None:
        row = self._session.execute(
            select(characters).where(characters.c.id == character_id)
        ).mappings().one_or_none()
        return character_from_row(row) if row else None

    def save(self, character: Character, *, expected_version: int) -> Character:
        next_version = expected_version + 1
        result = self._session.execute(
            update(characters)
            .where(
                characters.c.id == character.id,
                characters.c.version == expected_version,
            )
            .values(
                display_name=character.display_name,
                long_name=character.long_name,
                level=character.level,
                active=character.active,
                version=next_version,
            )
        )
        if result.rowcount != 1:
            raise ConcurrencyConflictError(
                f"Character {character.id} was changed by another transaction."
            )
        return Character(
            id=character.id,
            display_name=character.display_name,
            long_name=character.long_name,
            level=character.level,
            active=character.active,
            version=next_version,
        )

    def find_by_display_name(self, display_name: str) -> tuple[Character, ...]:
        """Compared in Python, on `domain/names.py`, over the whole table.

        The protocol's comparison is NFC-normalised full case folding. SQL
        `lower()` is **not** that comparison and must not be presented as it:
        PostgreSQL's `lower()` leaves `ß` alone, so `Test Straße` and
        `Test STRASSE` compare equal in Python and unequal in the database. A
        `WHERE` clause that narrowed the scan by `lower()` would therefore
        *skip* real matches, and the caller would be told a claimed name is
        free. There is no cheaper predicate that is safe in that direction:
        anything the database can evaluate today is narrower than the fold, and
        a narrower filter is the defect, not an optimisation.

        So this reads the characters and compares them here. The cost is one
        sequential scan and one `DisplayName` fold per row per call, and the
        importer calls it once per created or re-spelled row — quadratic in the
        size of the table across a run. That is deliberate and bounded: the
        bootstrap population is the live Sheet's roughly 150 characters, on a
        Unix socket, in an operator tool that runs occasionally.

        **The threshold at which this must change**: when `characters` passes
        roughly 2,000 rows, or when any request path — the Phase 3 portal, a
        Discord command — starts calling this, the fix is a schema one. Store
        the fold beside the name as a generated column, index it, and add the
        uniqueness rule that would let the database refuse a duplicate outright
        (§11 item 8 of the Phase 2 submission). That is a migration and a
        decided uniqueness policy, which is more than this correction is scoped
        to make.
        """
        wanted = DisplayName(display_name)
        rows = self._session.execute(
            select(characters).order_by(characters.c.created_at, characters.c.id)
        ).mappings().all()
        return tuple(
            character
            for character in (character_from_row(row) for row in rows)
            if character.name.claims_same_identity_as(wanted)
        )


class SqlAlchemyDiscordUserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, user: DiscordUser) -> None:
        self._session.execute(
            insert(discord_users).values(
                id=user.discord_id,
                username=user.username,
                global_name=user.global_name,
            )
        )

    def get(self, discord_id: int) -> DiscordUser | None:
        row = self._session.execute(
            select(discord_users).where(discord_users.c.id == discord_id)
        ).mappings().one_or_none()
        return discord_user_from_row(row) if row else None


class SqlAlchemySheetRowMappingRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, mapping: SheetRowMapping) -> None:
        self._session.execute(
            insert(sheet_row_mappings).values(
                id=uuid4(),
                character_id=mapping.character_id,
                sheet_tab=mapping.sheet_tab,
                row_index=mapping.row_index,
            )
        )

    def get_character_id(self, sheet_tab: str, row_index: int) -> UUID | None:
        return self._session.execute(
            select(sheet_row_mappings.c.character_id).where(
                sheet_row_mappings.c.sheet_tab == sheet_tab,
                sheet_row_mappings.c.row_index == row_index,
            )
        ).scalar_one_or_none()

    def list_for_tab(self, sheet_tab: str) -> tuple[SheetRowMapping, ...]:
        rows = self._session.execute(
            select(sheet_row_mappings)
            .where(sheet_row_mappings.c.sheet_tab == sheet_tab)
            .order_by(sheet_row_mappings.c.row_index)
        ).mappings().all()
        return tuple(sheet_row_mapping_from_row(row) for row in rows)


class SqlAlchemyExternalActorMappingRepository:
    """Deliberate links only. There is no lookup by name here, on purpose."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, mapping: ExternalActorMapping) -> None:
        self._session.execute(
            insert(external_actor_mappings).values(
                id=mapping.id,
                character_id=mapping.character_id,
                world_id=mapping.world_id,
                external_actor_id=mapping.external_actor_id,
                relink_fingerprint=mapping.relink_fingerprint,
                folder_id=mapping.folder_id,
                established_by_snapshot_id=mapping.established_by_snapshot_id,
            )
        )

    def get_by_actor(
        self, world_id: str, external_actor_id: str
    ) -> ExternalActorMapping | None:
        row = (
            self._session.execute(
                select(external_actor_mappings).where(
                    external_actor_mappings.c.world_id == world_id,
                    external_actor_mappings.c.external_actor_id == external_actor_id,
                )
            )
            .mappings()
            .one_or_none()
        )
        return _mapping_from_row(row) if row else None

    def list_for_world(self, world_id: str) -> tuple[ExternalActorMapping, ...]:
        rows = (
            self._session.execute(
                select(external_actor_mappings)
                .where(external_actor_mappings.c.world_id == world_id)
                .order_by(external_actor_mappings.c.external_actor_id)
            )
            .mappings()
            .all()
        )
        return tuple(_mapping_from_row(row) for row in rows)


class SqlAlchemySnapshotRepository:
    """Append-only. An artifact is recorded once and never edited."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, record: SnapshotRecord) -> SnapshotRecord:
        self._session.execute(
            insert(foundry_snapshots).values(
                id=record.id,
                checksum=record.checksum,
                size_bytes=record.size_bytes,
                schema_version=record.schema_version,
                exporter_id=record.exporter_id,
                exporter_version=record.exporter_version,
                exported_at=record.exported_at,
                world_id=record.world_id,
                world_title=record.world_title,
                core_version=record.core_version,
                system_id=record.system_id,
                system_version=record.system_version,
                actor_count=record.actor_count,
                selected_folder_ids=list(record.selected_folder_ids),
                artifact_location=record.artifact_location,
                received_by_discord_user_id=record.received_by_discord_user_id,
                received_via=record.received_via.value,
                submitted_by_principal=record.submitted_by_principal,
                correlation_id=record.correlation_id,
            )
        )
        return record

    def get_by_checksum(self, checksum: str) -> SnapshotRecord | None:
        row = (
            self._session.execute(
                select(foundry_snapshots).where(
                    foundry_snapshots.c.checksum == checksum
                )
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            return None
        return SnapshotRecord(
            id=row["id"],
            checksum=row["checksum"],
            size_bytes=row["size_bytes"],
            schema_version=row["schema_version"],
            exporter_id=row["exporter_id"],
            exporter_version=row["exporter_version"],
            exported_at=row["exported_at"],
            world_id=row["world_id"],
            world_title=row["world_title"],
            core_version=row["core_version"],
            system_id=row["system_id"],
            system_version=row["system_version"],
            actor_count=row["actor_count"],
            selected_folder_ids=tuple(row["selected_folder_ids"]),
            artifact_location=row["artifact_location"],
            received_by_discord_user_id=row["received_by_discord_user_id"],
            received_via=SnapshotSource(row["received_via"]),
            submitted_by_principal=row["submitted_by_principal"],
            correlation_id=row["correlation_id"],
        )


class SqlAlchemySnapshotImportRepository:
    """Append-only. Two uniqueness rules, for the attempt and for the input."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, record: SnapshotImportRecord) -> None:
        self._session.execute(
            insert(snapshot_imports).values(
                id=record.id,
                snapshot_id=record.snapshot_id,
                folder_id=record.folder_id,
                folder_path=record.folder_path,
                profile_version=record.profile_version,
                request_key=record.request_key,
                operation_digest=record.operation_digest,
                status=record.status.value,
                mode=record.mode.value,
                actor_discord_user_id=record.actor_discord_user_id,
                actor_capability=record.actor_capability.value,
                supervisor=record.supervisor,
                created_count=record.created_count,
                updated_count=record.updated_count,
                warning_count=record.warning_count,
                summary=dict(record.summary),
                correlation_id=record.correlation_id,
            )
        )

    def find_by_request_key(self, request_key: str) -> SnapshotImportRecord | None:
        return self._one(snapshot_imports.c.request_key == request_key)

    def find_applied(
        self, snapshot_id: UUID, folder_id: str, profile_version: str
    ) -> SnapshotImportRecord | None:
        return self._one(
            (snapshot_imports.c.snapshot_id == snapshot_id)
            & (snapshot_imports.c.folder_id == folder_id)
            & (snapshot_imports.c.profile_version == profile_version)
            & (snapshot_imports.c.status == ImportStatus.APPLIED.value)
        )

    def _one(self, condition) -> SnapshotImportRecord | None:
        row = (
            self._session.execute(select(snapshot_imports).where(condition))
            .mappings()
            .one_or_none()
        )
        if row is None:
            return None
        return SnapshotImportRecord(
            id=row["id"],
            snapshot_id=row["snapshot_id"],
            folder_id=row["folder_id"],
            folder_path=row["folder_path"],
            profile_version=row["profile_version"],
            request_key=row["request_key"],
            operation_digest=row["operation_digest"],
            status=ImportStatus(row["status"]),
            mode=ImportMode(row["mode"]),
            actor_capability=ActorCapability(row["actor_capability"]),
            actor_discord_user_id=row["actor_discord_user_id"],
            supervisor=row["supervisor"],
            created_count=row["created_count"],
            updated_count=row["updated_count"],
            warning_count=row["warning_count"],
            summary=row["summary"],
            correlation_id=row["correlation_id"],
        )


class SqlAlchemyIdempotencyRepository:
    """Receipts for completed operations. Insert and read, never update.

    `(scope, key)` is unique in the database, so two concurrent requests
    carrying one key cannot both write a receipt: the loser arrives here as
    `UniquenessConflict("idempotency_key.scope_key")` and re-reads the winner's
    row rather than assuming what it says.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, record: IdempotencyRecord) -> None:
        self._session.execute(
            insert(idempotency_keys).values(
                id=record.id,
                scope=record.scope,
                key=record.key,
                request_hash=record.request_hash,
                status=record.status.value,
                response=None if record.response is None else dict(record.response),
            )
        )

    def find(self, scope: str, key: str) -> IdempotencyRecord | None:
        row = (
            self._session.execute(
                select(idempotency_keys).where(
                    (idempotency_keys.c.scope == scope)
                    & (idempotency_keys.c.key == key)
                )
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            return None
        return IdempotencyRecord(
            id=row["id"],
            scope=row["scope"],
            key=row["key"],
            # psycopg returns `bytes` for `bytea`; `memoryview` appears with some
            # drivers and would compare unequal to the digest the caller holds.
            request_hash=bytes(row["request_hash"]),
            status=IdempotencyStatus(row["status"]),
            response=row["response"],
        )


class SqlAlchemyPlatformInitializationRepository:
    """The one row whose existence disables the supervised bootstrap."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self) -> PlatformInitialization | None:
        row = (
            self._session.execute(select(platform_initialization))
            .mappings()
            .one_or_none()
        )
        if row is None:
            return None
        return PlatformInitialization(
            supervisor=row["supervisor"],
            profile_version=row["profile_version"],
            correlation_id=row["correlation_id"],
            snapshot_checksum=row["snapshot_checksum"],
            initialized_at=row["initialized_at"],
        )

    def record(self, initialization: PlatformInitialization) -> None:
        self._session.execute(
            insert(platform_initialization).values(
                singleton=True,
                supervisor=initialization.supervisor,
                snapshot_checksum=initialization.snapshot_checksum,
                profile_version=initialization.profile_version,
                correlation_id=initialization.correlation_id,
            )
        )

    def is_dataset_empty(self) -> bool:
        """No characters, mappings, snapshots or history exist yet.

        Checked against the database rather than remembered, because the
        bootstrap's precondition is a property of the dataset, not of this
        process.
        """
        for table in (
            characters,
            external_actor_mappings,
            foundry_snapshots,
        ):
            count = self._session.execute(
                select(func.count()).select_from(table)
            ).scalar_one()
            if count:
                return False
        return True


def _mapping_from_row(row) -> ExternalActorMapping:
    return ExternalActorMapping(
        id=row["id"],
        character_id=row["character_id"],
        world_id=row["world_id"],
        external_actor_id=row["external_actor_id"],
        relink_fingerprint=row["relink_fingerprint"],
        folder_id=row["folder_id"],
        established_by_snapshot_id=row["established_by_snapshot_id"],
    )


class SqlAlchemyAuditRepository:
    """Append-only. The runtime role holds `SELECT, INSERT` and nothing else."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def record(self, event: AuditEvent) -> None:
        self._session.execute(
            insert(audit_events).values(
                id=event.id,
                actor_discord_user_id=event.actor_discord_user_id,
                actor_capability=event.actor_capability.value,
                action=event.action,
                entity_type=event.entity_type,
                entity_id=event.entity_id,
                source=event.source.value,
                correlation_id=event.correlation_id,
                # The event holds a deeply frozen payload; JSON serialization
                # needs plain dicts and lists, so it is converted back here at
                # the persistence boundary rather than stored mutable.
                payload=event.json_payload(),
            )
        )
