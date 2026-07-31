from __future__ import annotations

from typing import Protocol
from uuid import UUID

from domain.identity import Character, DiscordUser


class CharacterRepository(Protocol):
    def add(self, character: Character) -> None: ...

    def get(self, character_id: UUID) -> Character | None: ...

    def save(self, character: Character, *, expected_version: int) -> Character: ...


class DiscordUserRepository(Protocol):
    def add(self, user: DiscordUser) -> None: ...

    def get(self, discord_id: int) -> DiscordUser | None: ...


class UnitOfWork(Protocol):
    characters: CharacterRepository
    discord_users: DiscordUserRepository

    def __enter__(self) -> UnitOfWork: ...

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
