from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import bindparam, func, insert, select, text, update
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session

from application.admissions import (
    ADMISSION_LOCK_KEY,
    AdmissionState,
    SubmissionAdmission,
)
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
    submission_admissions,
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
                actor_account_id=record.actor_account_id,
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
        """Write the receipt — and, for a fenced scope, take the admission lock.

        The `admission_id` foreign key is checked as part of this statement, and
        checking it takes a row-level `KEY SHARE` lock on the admission row. That
        lock is the reason a settlement closure and an acceptance cannot
        interleave, so this call is a synchronisation point and not only a write.
        Core `insert()` through `session.execute` issues the statement here
        rather than deferring it to a flush, which is what makes "the lock is
        held when this returns" true.
        """
        self._session.execute(
            insert(idempotency_keys).values(
                id=record.id,
                scope=record.scope,
                key=record.key,
                request_hash=record.request_hash,
                status=record.status.value,
                response=None if record.response is None else dict(record.response),
                admission_id=record.admission_id,
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
            admission_id=row["admission_id"],
        )


class SqlAlchemySubmissionAdmissionRepository:
    """The admission fence. Read-only, because the runtime role is.

    There is no `open` and no `close` here, and their absence is the control:
    `infra/postgresql/runtime-grants.sql.tmpl` grants this role `SELECT` on
    `submission_admissions` and nothing else, so a method that tried to write
    would be refused by PostgreSQL. Opening and closing a generation is an
    operator action taken by `tools.submission_admission` as the schema owner.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def hold_against_closure(self) -> None:
        """`pg_advisory_xact_lock_shared`, released by this transaction's end.

        A transaction lock rather than a session lock, deliberately: a session
        lock outlives its transaction and would have to be released by hand,
        which is a leak waiting for the one path that raises before it gets
        there. Held until commit or rollback, whichever happens, with no
        `unlock` for anyone to forget.

        It needs no privilege, so the restricted runtime role takes it while
        holding `SELECT` and nothing else on `submission_admissions`.
        """
        self._session.execute(
            select(func.pg_advisory_xact_lock_shared(ADMISSION_LOCK_KEY))
        )

    def find_for_principal(self, principal_id: str) -> SubmissionAdmission | None:
        row = (
            self._session.execute(
                select(submission_admissions).where(
                    submission_admissions.c.principal_id == principal_id
                )
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            return None
        return SubmissionAdmission(
            id=row["id"],
            generation=row["generation"],
            principal_id=row["principal_id"],
            state=AdmissionState(row["state"]),
        )

    def state_of(self, admission_id: UUID) -> AdmissionState | None:
        """One statement, one column, taken under the acceptance's own lock.

        Deliberately narrow. It reads `state` and not the row, so that nothing
        about it can be mistaken for a general re-fetch that a caller might move
        somewhere more convenient — its correctness depends entirely on *when* it
        runs, and that is documented at the call site in
        `application/foundry/submission.py`.
        """
        value = self._session.execute(
            select(submission_admissions.c.state).where(
                submission_admissions.c.id == admission_id
            )
        ).scalar_one_or_none()
        if value is None:
            return None
        return AdmissionState(value)


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
                actor_platform_account_id=event.actor_platform_account_id,
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


class SqlAlchemyReconciliationJobLeaseRepository:
    """The one write P3.3's fence needs, and it lives on the *import's* session.

    ## Why it is here rather than beside the other job statements

    Every other `reconciliation_jobs` statement belongs to
    `adapters/web/repositories.py`, because every other one runs in a transaction
    of its own — a claim, a heartbeat, a publication. This one is different in
    exactly the way that matters: it must run in the **same PostgreSQL
    transaction that commits the import effect**, which is the unit of work
    `SnapshotImportService` opens. So it joins that unit of work, and putting it
    anywhere else would mean it could not.

    ## What the statement proves

    That, at the commit boundary of the effect, the job still

    1. is `running`;
    2. carries this exact per-claim fencing token;
    3. has no cancellation request;
    4. has not been abandoned or reaped (both clear `lease_owner`, so (2) covers
       them); and
    5. has not been superseded by another claim (a new claim mints a **new**
       token, so (2) covers that too).

    A `SELECT` proving the same thing would not be a fence. This is an `UPDATE`
    because the row's write lock is the serialization: it is taken here, held
    until the import commits, and every writer that would invalidate the attempt
    carries `AND effect_committed_at IS NULL` and therefore blocks on it and
    re-evaluates its own predicate afterwards under `READ COMMITTED`. Exactly one
    side wins, and the loser writes nothing.

    `effect_committed_at IS NULL` in the predicate is what makes the fence
    single-use: a second effect for one job is not merely prevented downstream by
    `uq_snapshot_imports_applied_input`, it cannot take the fence.

    ## What else the statement writes, and why here

    Added by the 2026-08-18 effect-publication remediation. The same statement
    stores `effect_result`: the bounded summary and blocked-entry list this run
    produced. Before it, the result the worker owed lived only as an in-memory
    `Executed` value on the execution thread, so a process that died between the
    effect and the publication took the publication with it — and the only recovery
    left was to requeue the job and spend one of N-43's three attempts re-running
    work whose effect was already durable. At `attempts = 3` there was none to
    spend and the reaper wrote `failed` over a real import.

    Writing it **here** rather than in a second statement is the whole point: this
    transaction is the one that commits the effect, so the publication payload
    becomes durable if and only if the effect does. Migration 0013's
    `CHECK ((effect_committed_at IS NULL) = (effect_result IS NULL))` is the
    database saying the same thing.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def hold_for_effect(
        self, *, job_id: UUID, owner: str, now: datetime, result: dict
    ) -> bool:
        """Take the job row's write lock, record the effect and what it owes, or refuse.

        Returns `False` when the attempt is no longer entitled to commit, which
        the caller turns into a rolled-back transaction and no effect at all.

        `result` is required, not defaulted. A fence able to stamp
        `effect_committed_at` without it would be a fence able to make an effect
        durable that no later process can publish from durable data — which is the
        second of the two defects this remediation exists for.
        """
        return (
            self._session.execute(
                text(
                    """
                    UPDATE reconciliation_jobs SET
                        effect_committed_at = :now,
                        effect_result = :result,
                        version = version + 1
                    WHERE id = :job_id
                      AND lease_owner = :owner
                      AND state = 'running'
                      AND cancel_requested_at IS NULL
                      AND effect_committed_at IS NULL
                    """
                    # `bindparams` rather than a `::jsonb` cast in the text: the
                    # type belongs to the parameter, so a caller cannot pass a
                    # string that happens to parse and a reader does not have to
                    # check whether the cast is still there.
                ).bindparams(bindparam("result", type_=JSONB)),
                {"job_id": job_id, "owner": owner, "now": now, "result": result},
            ).rowcount
            == 1
        )
