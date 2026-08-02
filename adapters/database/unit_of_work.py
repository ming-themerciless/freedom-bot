from __future__ import annotations

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from .repositories import (
    SqlAlchemyAuditRepository,
    SqlAlchemyCharacterRepository,
    SqlAlchemyDiscordUserRepository,
    SqlAlchemySheetRowMappingRepository,
)


class SqlAlchemyUnitOfWork:
    """One application use case owns one instance and one transaction.

    The transaction boundary is the caller's (ADR 0003): repositories join the
    session opened here and never commit. Leaving the block without calling
    `commit()` discards the work.
    """

    characters: SqlAlchemyCharacterRepository
    discord_users: SqlAlchemyDiscordUserRepository
    sheet_row_mappings: SqlAlchemySheetRowMappingRepository
    audit: SqlAlchemyAuditRepository

    def __init__(self, engine: Engine) -> None:
        self._session_factory = sessionmaker(bind=engine, expire_on_commit=False)
        self._session: Session | None = None

    def __enter__(self) -> SqlAlchemyUnitOfWork:
        self._session = self._session_factory()
        self.characters = SqlAlchemyCharacterRepository(self._session)
        self.discord_users = SqlAlchemyDiscordUserRepository(self._session)
        self.sheet_row_mappings = SqlAlchemySheetRowMappingRepository(self._session)
        self.audit = SqlAlchemyAuditRepository(self._session)
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
