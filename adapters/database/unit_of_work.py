from __future__ import annotations

from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker

from .translation import TranslatingSession
from .repositories import (
    SqlAlchemyAuditRepository,
    SqlAlchemyCharacterRepository,
    SqlAlchemyDiscordUserRepository,
    SqlAlchemyExternalActorMappingRepository,
    SqlAlchemyIdempotencyRepository,
    SqlAlchemyPlatformInitializationRepository,
    SqlAlchemySheetRowMappingRepository,
    SqlAlchemySnapshotImportRepository,
    SqlAlchemySnapshotRepository,
    SqlAlchemySubmissionAdmissionRepository,
)

#: The isolation level every unit of work runs at, pinned rather than inherited.
#:
#: `application/foundry/submission.py` re-reads its admission state as the last
#: statement before its commit, and that re-read is only a *fresh* reading under
#: `READ COMMITTED`, where each statement takes its own snapshot. The code said
#: so in a comment while the session took whatever `default_transaction_isolation`
#: the database or the login role happened to carry — so a single `ALTER ROLE …
#: SET default_transaction_isolation = 'repeatable read'`, outside this
#: repository and invisible to it, would have changed what that statement means.
#:
#: **Measured, not assumed.** The decisive interleaving — a closure holding the
#: exclusive advisory lock while the submission's first statement takes its
#: snapshot and then blocks, with the closure committing before it wakes — was
#: run against PostgreSQL 16.14 at all three levels:
#:
#: - `READ COMMITTED` — the submission refuses itself with the typed
#:   `admission_closed`, which is the designed outcome;
#: - `REPEATABLE READ` and `SERIALIZABLE` — the foreign-key `KEY SHARE` lock in
#:   `idempotency_keys.add` cannot be taken against a row updated after the
#:   snapshot, so PostgreSQL aborts the transaction with **SQLSTATE 40001**.
#:
#: So the invariant held at every level and no post-closure acceptance was ever
#: durable: the non-default levels fail *closed*, which is hardening evidence
#: rather than a new B-1 failure. What they lose is the typed refusal — the
#: caller gets a generic `PersistenceError` instead of `403 admission_closed`,
#: and an operator reading it cannot tell a settlement from a database fault.
#: Pinning the level here keeps the documented contract true and keeps the
#: refusal the runbook tells operators to expect.
#:
#: Pinned on the unit of work rather than on the cluster, the database or the
#: role: this is the transaction boundary that depends on it, and nothing about
#: an unrelated future consumer's isolation needs is decided here. It is also
#: PostgreSQL's own default, so this changes no behaviour on a cluster nobody
#: has reconfigured — it makes the assumption enforced instead of hopeful.
UNIT_OF_WORK_ISOLATION_LEVEL = "READ COMMITTED"


class SqlAlchemyUnitOfWork:
    """One application use case owns one instance and one transaction.

    The transaction boundary is the caller's (ADR 0003): repositories join the
    session opened here and never commit. Leaving the block without calling
    `commit()` discards the work.

    Every repository below shares that one session, which is what makes an
    import's characters, mappings, immutable import record and audit event
    commit or roll back **together**.

    That session is a `TranslatingSession`, so no ORM or driver exception leaves
    this adapter: a lost uniqueness race arrives in application code as
    `UniquenessConflict` naming a rule, and anything else as `PersistenceError`.
    Wrapping the session rather than each repository method is deliberate — a
    repository that forgot to wrap one `execute` would leak, and nothing here
    could see the omission.
    """

    characters: SqlAlchemyCharacterRepository
    discord_users: SqlAlchemyDiscordUserRepository
    sheet_row_mappings: SqlAlchemySheetRowMappingRepository
    audit: SqlAlchemyAuditRepository
    external_actor_mappings: SqlAlchemyExternalActorMappingRepository
    snapshots: SqlAlchemySnapshotRepository
    snapshot_imports: SqlAlchemySnapshotImportRepository
    idempotency: SqlAlchemyIdempotencyRepository
    submission_admissions: SqlAlchemySubmissionAdmissionRepository
    initialization: SqlAlchemyPlatformInitializationRepository

    def __init__(self, engine: Engine) -> None:
        self._session_factory = sessionmaker(bind=engine, expire_on_commit=False)
        self._session: TranslatingSession | None = None

    def __enter__(self) -> SqlAlchemyUnitOfWork:
        session = TranslatingSession(self._session_factory())
        # Before anything else, and before any statement of this transaction:
        # the level is a property of the transaction and cannot be chosen once
        # it has begun. See `UNIT_OF_WORK_ISOLATION_LEVEL`.
        session.begin_at_isolation_level(UNIT_OF_WORK_ISOLATION_LEVEL)
        self._session = session
        self.characters = SqlAlchemyCharacterRepository(session)
        self.discord_users = SqlAlchemyDiscordUserRepository(session)
        self.sheet_row_mappings = SqlAlchemySheetRowMappingRepository(session)
        self.audit = SqlAlchemyAuditRepository(session)
        self.external_actor_mappings = SqlAlchemyExternalActorMappingRepository(session)
        self.snapshots = SqlAlchemySnapshotRepository(session)
        self.snapshot_imports = SqlAlchemySnapshotImportRepository(session)
        self.idempotency = SqlAlchemyIdempotencyRepository(session)
        self.submission_admissions = SqlAlchemySubmissionAdmissionRepository(session)
        self.initialization = SqlAlchemyPlatformInitializationRepository(session)
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if exc_type is not None:
            self.rollback()
        self._require_session().close()
        self._session = None

    def commit(self) -> None:
        self._require_session().commit()

    def rollback(self) -> None:
        self._require_session().rollback()

    def _require_session(self) -> TranslatingSession:
        if self._session is None:
            raise RuntimeError("The unit of work must be entered before use.")
        return self._session
