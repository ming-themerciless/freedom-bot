"""In-memory doubles for the application-service tests.

The fake unit of work models the one behaviour those tests depend on that a
dictionary does not have: uncommitted work disappears. Each `with` block edits
a copy of the store and publishes it only on `commit()`, so a test can assert
that a dry run left nothing behind without needing PostgreSQL.

The fake repositories raise `UniquenessConflict` with the **same rule names**
the SQLAlchemy adapter translates PostgreSQL constraint violations into
(`adapters/database/translation.py`). That is what lets an application-service
test exercise the conflict-resolution path at all: a fake that raised a generic
`ValueError` could only ever prove that something failed. It does not replace
the PostgreSQL evidence — a fake cannot lose a real race — and the two-connection
tests in `test_snapshot_database.py` remain the proof that the rules fire.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from uuid import UUID, uuid4

from application.audit import AuditEvent
from application.authorization import AuthorizationContext
from application.errors import ConcurrencyConflictError, UniquenessConflict
from application.idempotency import IdempotencyRecord
from application.imports import SheetRowMapping
from application.snapshots import (
    ExternalActorMapping,
    PlatformInitialization,
    SnapshotImportRecord,
    SnapshotRecord,
)
from application.admissions import AdmissionState, SubmissionAdmission
from domain.identity import Character, DiscordUser
from domain.names import DisplayName


@dataclass
class FakeStore:
    """The committed state, shared by every unit of work built from it."""

    characters: dict[UUID, Character] = field(default_factory=dict)
    discord_users: dict[int, DiscordUser] = field(default_factory=dict)
    sheet_row_mappings: list[SheetRowMapping] = field(default_factory=list)
    audit_events: list[AuditEvent] = field(default_factory=list)
    external_actor_mappings: list[ExternalActorMapping] = field(default_factory=list)
    snapshots: dict[str, SnapshotRecord] = field(default_factory=dict)
    snapshot_imports: list[SnapshotImportRecord] = field(default_factory=list)
    idempotency: dict[tuple[str, str], IdempotencyRecord] = field(default_factory=dict)
    #: The admission fence, keyed by principal id — the same identity the real
    #: table makes unique, so a fake cannot model a credential holding two.
    submission_admissions: dict[str, SubmissionAdmission] = field(default_factory=dict)
    initialization: PlatformInitialization | None = None

    def copy(self) -> FakeStore:
        return FakeStore(
            characters=dict(self.characters),
            discord_users=dict(self.discord_users),
            sheet_row_mappings=list(self.sheet_row_mappings),
            audit_events=list(self.audit_events),
            external_actor_mappings=list(self.external_actor_mappings),
            snapshots=dict(self.snapshots),
            snapshot_imports=list(self.snapshot_imports),
            idempotency=dict(self.idempotency),
            submission_admissions=dict(self.submission_admissions),
            initialization=self.initialization,
        )


def admit(
    store: FakeStore,
    principal_id: str,
    *,
    generation: int = 1,
    state: AdmissionState = AdmissionState.OPEN,
) -> SubmissionAdmission:
    """Give `principal_id` an admission generation, as an operator would.

    Every test that expects a submission to succeed has to call this, and that
    is deliberate rather than an inconvenience: a deployment that has run
    migration 0005 and not opened a generation accepts nothing, so a fixture
    that admitted by default would let the suite prove a state production is
    never in. `tools.submission_admission open` is the real thing this stands
    for.
    """
    admission = SubmissionAdmission(
        id=uuid4(),
        generation=generation,
        principal_id=principal_id,
        state=state,
    )
    store.submission_admissions[principal_id] = admission
    return admission


def close_admission(store: FakeStore, principal_id: str) -> SubmissionAdmission:
    """Close a generation in the committed store — the settlement operation.

    Mutates the *committed* store, so a unit of work that is already open sees
    it on its next read. That is what a real closure committed by another
    session looks like from inside a `READ COMMITTED` transaction, and it is how
    the paused-request orderings are reproduced without threads.
    """
    admission = store.submission_admissions[principal_id]
    closed = replace(admission, state=AdmissionState.CLOSED)
    store.submission_admissions[principal_id] = closed
    return closed


class FakeCharacterRepository:
    def __init__(self, store: FakeStore) -> None:
        self._store = store

    def add(self, character: Character) -> None:
        if character.id in self._store.characters:
            raise ValueError(f"Character {character.id} already exists.")
        self._store.characters[character.id] = character

    def get(self, character_id: UUID) -> Character | None:
        return self._store.characters.get(character_id)

    def save(self, character: Character, *, expected_version: int) -> Character:
        current = self._store.characters.get(character.id)
        if current is None or current.version != expected_version:
            raise ConcurrencyConflictError(
                f"Character {character.id} was changed by another transaction."
            )
        saved = replace(character, version=expected_version + 1)
        self._store.characters[character.id] = saved
        return saved

    def find_by_display_name(self, display_name: str) -> tuple[Character, ...]:
        """The same comparison the PostgreSQL repository makes, on the same rule.

        A fake that folded names differently from the adapter would let the
        application suite prove a decision the database would not reach — which
        is how the Phase 2 normalisation defect stayed invisible to it.
        """
        wanted = DisplayName(display_name)
        return tuple(
            character
            for character in self._store.characters.values()
            if character.name.claims_same_identity_as(wanted)
        )


class FakeDiscordUserRepository:
    def __init__(self, store: FakeStore) -> None:
        self._store = store

    def add(self, user: DiscordUser) -> None:
        self._store.discord_users[user.discord_id] = user

    def get(self, discord_id: int) -> DiscordUser | None:
        return self._store.discord_users.get(discord_id)


class FakeSheetRowMappingRepository:
    def __init__(self, store: FakeStore) -> None:
        self._store = store

    def add(self, mapping: SheetRowMapping) -> None:
        for existing in self._store.sheet_row_mappings:
            if (
                existing.sheet_tab == mapping.sheet_tab
                and existing.row_index == mapping.row_index
            ) or (
                existing.sheet_tab == mapping.sheet_tab
                and existing.character_id == mapping.character_id
            ):
                raise ValueError(
                    "sheet_row_mappings uniqueness violated for "
                    f"{mapping.sheet_tab}!{mapping.row_index}."
                )
        self._store.sheet_row_mappings.append(mapping)

    def get_character_id(self, sheet_tab: str, row_index: int) -> UUID | None:
        for mapping in self._store.sheet_row_mappings:
            if mapping.sheet_tab == sheet_tab and mapping.row_index == row_index:
                return mapping.character_id
        return None

    def list_for_tab(self, sheet_tab: str) -> tuple[SheetRowMapping, ...]:
        return tuple(
            sorted(
                (m for m in self._store.sheet_row_mappings if m.sheet_tab == sheet_tab),
                key=lambda mapping: mapping.row_index,
            )
        )


class FakeAuditRepository:
    def __init__(self, store: FakeStore) -> None:
        self._store = store

    def record(self, event: AuditEvent) -> None:
        self._store.audit_events.append(event)


class FakeExternalActorMappingRepository:
    """Deliberate links only. There is no lookup by name here, on purpose."""

    def __init__(self, store: FakeStore) -> None:
        self._store = store

    def add(self, mapping: ExternalActorMapping) -> None:
        for existing in self._store.external_actor_mappings:
            if (
                existing.world_id == mapping.world_id
                and existing.external_actor_id == mapping.external_actor_id
            ):
                raise UniquenessConflict("external_actor_mapping.world_actor")
            if (
                existing.world_id == mapping.world_id
                and existing.character_id == mapping.character_id
            ):
                raise UniquenessConflict("external_actor_mapping.character_world")
        self._store.external_actor_mappings.append(mapping)

    def get_by_actor(
        self, world_id: str, external_actor_id: str
    ) -> ExternalActorMapping | None:
        for mapping in self._store.external_actor_mappings:
            if (
                mapping.world_id == world_id
                and mapping.external_actor_id == external_actor_id
            ):
                return mapping
        return None

    def list_for_world(self, world_id: str) -> tuple[ExternalActorMapping, ...]:
        return tuple(
            sorted(
                (m for m in self._store.external_actor_mappings if m.world_id == world_id),
                key=lambda mapping: mapping.external_actor_id,
            )
        )


class FakeSnapshotRepository:
    def __init__(self, store: FakeStore) -> None:
        self._store = store

    def add(self, record: SnapshotRecord) -> SnapshotRecord:
        if record.checksum in self._store.snapshots:
            raise UniquenessConflict("foundry_snapshot.checksum")
        self._store.snapshots[record.checksum] = record
        return record

    def get_by_checksum(self, checksum: str) -> SnapshotRecord | None:
        return self._store.snapshots.get(checksum)


class FakeSnapshotImportRepository:
    def __init__(self, store: FakeStore) -> None:
        self._store = store

    def add(self, record: SnapshotImportRecord) -> None:
        for existing in self._store.snapshot_imports:
            if existing.request_key == record.request_key:
                raise UniquenessConflict("snapshot_import.request_key")
            if (
                record.status.value == "applied"
                and existing.status.value == "applied"
                and (existing.snapshot_id, existing.folder_id, existing.profile_version)
                == (record.snapshot_id, record.folder_id, record.profile_version)
            ):
                raise UniquenessConflict("snapshot_import.applied_input")
        self._store.snapshot_imports.append(record)

    def find_by_request_key(self, request_key: str) -> SnapshotImportRecord | None:
        for record in self._store.snapshot_imports:
            if record.request_key == request_key:
                return record
        return None

    def find_applied(
        self, snapshot_id: UUID, folder_id: str, profile_version: str
    ) -> SnapshotImportRecord | None:
        for record in self._store.snapshot_imports:
            if (
                record.status.value == "applied"
                and record.snapshot_id == snapshot_id
                and record.folder_id == folder_id
                and record.profile_version == profile_version
            ):
                return record
        return None


class FakeIdempotencyRepository:
    """`(scope, key)` uniqueness, with the adapter's own rule name."""

    def __init__(self, store: FakeStore) -> None:
        self._store = store

    def add(self, record: IdempotencyRecord) -> None:
        identity = (record.scope, record.key)
        if identity in self._store.idempotency:
            raise UniquenessConflict("idempotency_key.scope_key")
        self._store.idempotency[identity] = record

    def find(self, scope: str, key: str) -> IdempotencyRecord | None:
        return self._store.idempotency.get((scope, key))


class FakeSubmissionAdmissionRepository:
    """The admission fence, with the timing that makes it a fence.

    Two details are modelled deliberately, because a fake that got either wrong
    would let the application suite prove something PostgreSQL would not.

    **Reads go to the *committed* store, not to this transaction's pending
    copy.** `state_of` stands for a `READ COMMITTED` statement, which takes a
    fresh snapshot and therefore observes a closure another session committed
    while this transaction was open. A fake that read the pending copy would
    never see one, and the fence would pass its tests by being untestable.

    **`hold_against_closure` can run a side effect.** It stands for the advisory
    lock a real transaction takes first, and a test uses `on_hold` to commit a
    closure at exactly that instant — which is how the "closure got in first"
    ordering is reproduced without threads.
    """

    def __init__(self, committed: FakeStore) -> None:
        self._committed = committed
        #: Set by a test: run at the moment the lock would be taken.
        self.on_hold: object | None = None

    def hold_against_closure(self) -> None:
        if self.on_hold is not None:
            self.on_hold()

    def find_for_principal(self, principal_id: str) -> SubmissionAdmission | None:
        return self._committed.submission_admissions.get(principal_id)

    def state_of(self, admission_id: UUID) -> AdmissionState | None:
        for admission in self._committed.submission_admissions.values():
            if admission.id == admission_id:
                return admission.state
        return None


class FakePlatformInitializationRepository:
    def __init__(self, store: FakeStore) -> None:
        self._store = store

    def get(self) -> PlatformInitialization | None:
        return self._store.initialization

    def record(self, initialization: PlatformInitialization) -> None:
        if self._store.initialization is not None:
            raise UniquenessConflict("platform_initialization.singleton")
        self._store.initialization = initialization

    def is_dataset_empty(self) -> bool:
        return not (
            self._store.characters
            or self._store.external_actor_mappings
            or self._store.snapshots
        )


class FakeUnitOfWork:
    """One `with` block, one transaction, exactly as the real one behaves."""

    def __init__(self, store: FakeStore) -> None:
        self._committed = store
        self._pending = store.copy()
        self.committed_count = 0
        self.rolled_back_count = 0
        #: Set by a test to make one repository call fail, so an injected
        #: failure can be shown to roll the whole transaction back.
        self.fail_on: str | None = None
        #: What it fails *with*. An exception, or a zero-argument callable
        #: returning one — the callable form lets a test run a side effect (such
        #: as committing the row that won a race) at the moment of failure.
        self.failure: object | None = None

    def build_failure(self, name: str) -> BaseException:
        if self.failure is None:
            return InjectedFailure(f"injected {name} failure")
        if callable(self.failure):
            return self.failure()
        return self.failure  # type: ignore[return-value]

    def __enter__(self) -> FakeUnitOfWork:
        self._pending = self._committed.copy()
        # Every repository an import writes through is failable, so the
        # injected-failure matrix can cover each write point rather than the two
        # that happened to be wrapped first. `fail_on` names one of them.
        self.characters = _failing(
            FakeCharacterRepository(self._pending), self, "characters"
        )
        self.discord_users = FakeDiscordUserRepository(self._pending)
        self.sheet_row_mappings = FakeSheetRowMappingRepository(self._pending)
        self.audit = _failing(FakeAuditRepository(self._pending), self, "audit")
        self.external_actor_mappings = _failing(
            FakeExternalActorMappingRepository(self._pending),
            self,
            "external_actor_mappings",
        )
        self.snapshots = _failing(
            FakeSnapshotRepository(self._pending), self, "snapshots"
        )
        self.snapshot_imports = _failing(
            FakeSnapshotImportRepository(self._pending), self, "snapshot_imports"
        )
        self.idempotency = _failing(
            FakeIdempotencyRepository(self._pending), self, "idempotency"
        )
        # Built over the *committed* store, not the pending copy. See the
        # repository's docstring: the fence's whole job is to observe a closure
        # another session committed while this transaction was open.
        self.submission_admissions = FakeSubmissionAdmissionRepository(self._committed)
        self.initialization = FakePlatformInitializationRepository(self._pending)
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if exc_type is not None:
            self.rollback()

    def commit(self) -> None:
        restored = self._pending.copy()
        for name, value in vars(restored).items():
            setattr(self._committed, name, value)
        self.committed_count += 1

    def rollback(self) -> None:
        # Mutated in place rather than rebound: the repositories hold this
        # object, so rebinding would leave them writing to a discarded copy.
        restored = self._committed.copy()
        for name, value in vars(restored).items():
            setattr(self._pending, name, value)
        self.rolled_back_count += 1


class _FailingProxy:
    """Wraps a repository so a named unit of work can be made to fail on it.

    `failure` chooses *what* it fails with. It defaults to `InjectedFailure`,
    which is what the atomicity matrix wants: an arbitrary mid-transaction fault
    with no meaning attached. A conflict test sets it to the typed exception the
    real adapter would raise, and may pass a callable — which is how a test can
    commit the *winning* row at the exact moment this attempt loses, reproducing
    the ordering of a real race without threads.
    """

    def __init__(self, wrapped: object, unit: FakeUnitOfWork, name: str) -> None:
        self._wrapped = wrapped
        self._unit = unit
        self._name = name

    def __getattr__(self, attribute: str):
        target = getattr(self._wrapped, attribute)
        if not callable(target):
            return target

        def call(*args, **kwargs):
            if self._unit.fail_on == self._name:
                raise self._unit.build_failure(self._name)
            return target(*args, **kwargs)

        return call


class InjectedFailure(RuntimeError):
    """A deliberate mid-transaction failure, for the rollback tests."""


def _failing(repository: object, unit: FakeUnitOfWork, name: str):
    return _FailingProxy(repository, unit, name)


class FakeAuthorization:
    """Resolves current privilege, and records that it was asked.

    `asked` matters: the apply path must consult the port again rather than
    reuse the preview's answer, and the only way to show that is to count.
    """

    def __init__(self, **contexts: AuthorizationContext) -> None:
        self._contexts: dict[int, AuthorizationContext] = {}
        self.asked: list[int] = []

    @classmethod
    def with_council(cls, discord_user_id: int) -> FakeAuthorization:
        port = cls()
        port.grant(
            AuthorizationContext(
                discord_user_id=discord_user_id, guild_member=True, guild_council=True
            )
        )
        return port

    def grant(self, context: AuthorizationContext) -> FakeAuthorization:
        self._contexts[context.discord_user_id] = context
        return self

    def revoke(self, discord_user_id: int) -> None:
        """Whatever they held, they no longer do — as of the next question."""
        self._contexts[discord_user_id] = AuthorizationContext(
            discord_user_id=discord_user_id, guild_member=False
        )

    def context_for(self, discord_user_id: int) -> AuthorizationContext:
        self.asked.append(discord_user_id)
        return self._contexts.get(
            discord_user_id, AuthorizationContext(discord_user_id=discord_user_id)
        )


def unit_of_work_factory(store: FakeStore):
    """A factory the service can call once per run, recording each unit.

    Setting `factory.fail_on` makes **every unit it creates from then on** fail
    on that repository. Setting `fail_on` on an existing unit does not affect
    the next one, and an apply opens a fresh unit — so a test that only touched
    the units created during the preview would inject nothing and pass for the
    wrong reason.
    """
    units: list[FakeUnitOfWork] = []

    def factory() -> FakeUnitOfWork:
        unit = FakeUnitOfWork(store)
        unit.fail_on = factory.fail_on  # type: ignore[attr-defined]
        unit.failure = factory.failure  # type: ignore[attr-defined]
        units.append(unit)
        return unit

    factory.units = units  # type: ignore[attr-defined]
    factory.fail_on = None  # type: ignore[attr-defined]
    factory.failure = None  # type: ignore[attr-defined]
    return factory
