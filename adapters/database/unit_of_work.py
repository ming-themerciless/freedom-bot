from __future__ import annotations

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from .repositories import (
    SqlAlchemyAuditRepository,
    SqlAlchemyCharacterRepository,
    SqlAlchemyDiscordUserRepository,
    SqlAlchemyExternalActorMappingRepository,
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
    """

    characters: SqlAlchemyCharacterRepository
    discord_users: SqlAlchemyDiscordUserRepository
    sheet_row_mappings: SqlAlchemySheetRowMappingRepository
    audit: SqlAlchemyAuditRepository
    external_actor_mappings: SqlAlchemyExternalActorMappingRepository
    snapshots: SqlAlchemySnapshotRepository
    snapshot_imports: SqlAlchemySnapshotImportRepository
    initialization: SqlAlchemyPlatformInitializationRepository

    def __init__(self, engine: Engine) -> None:
        self._session_factory = sessionmaker(bind=engine, expire_on_commit=False)
        self._session: Session | None = None

    def __enter__(self) -> SqlAlchemyUnitOfWork:
        session = self._session_factory()
        self._session = session
        self.characters = SqlAlchemyCharacterRepository(session)
        self.discord_users = SqlAlchemyDiscordUserRepository(session)
        self.sheet_row_mappings = SqlAlchemySheetRowMappingRepository(session)
        self.audit = SqlAlchemyAuditRepository(session)
        self.external_actor_mappings = SqlAlchemyExternalActorMappingRepository(session)
        self.snapshots = SqlAlchemySnapshotRepository(session)
        self.snapshot_imports = SqlAlchemySnapshotImportRepository(session)
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

    def _require_session(self) -> Session:
        if self._session is None:
            raise RuntimeError("The unit of work must be entered before use.")
        return self._session
