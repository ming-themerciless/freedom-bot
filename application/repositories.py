from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID

from application.admissions import AdmissionState, SubmissionAdmission
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


class SubmissionAdmissionRepository(Protocol):
    """The admission fence, read from inside the submission transaction.

    Read-only, deliberately. Opening and closing a generation is an operator
    action taken by `tools.submission_admission` as the schema owner, and the
    runtime role holds `SELECT` on this table and nothing else — so the
    application physically cannot admit itself, close a generation, or reopen
    one. `tests/test_submission_admission_postgresql.py` proves that against
    PostgreSQL rather than asserting it here.
    """

    def hold_against_closure(self) -> None:
        """Take the shared side of the fence lock, for this whole transaction.

        **Must be the first statement of any transaction that reads an admission
        in order to act on it**, replays included. Closure takes the exclusive
        side, so after this returns no closure can commit until this transaction
        ends — and any closure that got in first has already committed, so every
        read that follows sees it.

        This is what covers the paths that write nothing. A replay produces a
        successful receipt without inserting a row, so it takes no foreign-key
        lock and the structural half of the fence does not reach it; this does.
        """
        ...

    def find_for_principal(self, principal_id: str) -> SubmissionAdmission | None:
        """The one admission this credential has ever held, if it has one.

        `principal_id` comes from the presented credential — that is, from the
        request's own bytes — and never from a lookup of "which generation is
        open now". A request paused before this call must resolve to the same
        admission when it wakes, and this is what guarantees it does.
        """
        ...

    def state_of(self, admission_id: UUID) -> AdmissionState | None:
        """Re-read one admission's state, and nothing else. **This is the fence.**

        It must be issued *after* the acceptance's own write has taken the
        foreign-key lock on the admission row, and before the commit. Under
        `READ COMMITTED` the statement takes a fresh snapshot, so it observes any
        closure that committed before that lock was granted — and no closure can
        commit after it, because the lock is held until this transaction ends.

        Returns `None` if the row is gone, which nothing may treat as
        permission: the trigger in migration 0005 refuses `DELETE`, so a missing
        row means the schema is not what this code requires.
        """
        ...


class PlatformInitializationRepository(Protocol):
    def get(self) -> PlatformInitialization | None: ...

    def record(self, initialization: PlatformInitialization) -> None: ...

    def is_dataset_empty(self) -> bool:
        """No characters, mappings, snapshots or history exist yet."""
        ...


class ReconciliationJobLeaseRepository(Protocol):
    """The fence a durable effect is committed behind (P3.3, migration 0012).

    It lives on the unit of work rather than beside the other job statements
    because its whole meaning is *which transaction it runs in*: the one that
    commits the effect, so that "this attempt is still entitled to commit" and
    "the effect committed" are one atomic fact rather than two hopeful ones.
    """

    def hold_for_effect(
        self, *, job_id: UUID, owner: str, now: datetime, result: dict
    ) -> bool:
        """Record the effect and what it owes, under this fencing token, or refuse.

        `False` means the attempt lost the race — cancelled, abandoned, reaped or
        superseded — and the caller must commit nothing at all.

        `result` is the bounded publication payload the run produced (migration
        0013). It is written in this same statement so that an effect which
        becomes durable always leaves behind the result a later process can
        publish from it, without re-running the attempt.
        """
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
    submission_admissions: SubmissionAdmissionRepository
    initialization: PlatformInitializationRepository
    job_leases: ReconciliationJobLeaseRepository

    def __enter__(self) -> UnitOfWork: ...

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
