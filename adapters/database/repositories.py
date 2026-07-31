from __future__ import annotations

from uuid import UUID

from sqlalchemy import insert, select, update
from sqlalchemy.orm import Session

from application.errors import ConcurrencyConflictError
from domain.identity import Character, DiscordUser

from .mappers import character_from_row, discord_user_from_row
from .tables import characters, discord_users


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
