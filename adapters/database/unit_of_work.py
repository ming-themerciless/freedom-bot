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
)


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
    initialization: SqlAlchemyPlatformInitializationRepository

    def __init__(self, engine: Engine) -> None:
        self._session_factory = sessionmaker(bind=engine, expire_on_commit=False)
        self._session: TranslatingSession | None = None

    def __enter__(self) -> SqlAlchemyUnitOfWork:
        session = TranslatingSession(self._session_factory())
        self._session = session
        self.characters = SqlAlchemyCharacterRepository(session)
        self.discord_users = SqlAlchemyDiscordUserRepository(session)
        self.sheet_row_mappings = SqlAlchemySheetRowMappingRepository(session)
        self.audit = SqlAlchemyAuditRepository(session)
        self.external_actor_mappings = SqlAlchemyExternalActorMappingRepository(session)
        self.snapshots = SqlAlchemySnapshotRepository(session)
        self.snapshot_imports = SqlAlchemySnapshotImportRepository(session)
        self.idempotency = SqlAlchemyIdempotencyRepository(session)
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
