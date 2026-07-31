from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class DiscordUser:
    discord_id: int
    username: str
    global_name: str | None = None

    def __post_init__(self) -> None:
        if self.discord_id <= 0:
            raise ValueError("Discord IDs must be positive snowflakes.")
        if not self.username.strip():
            raise ValueError("A Discord username is required.")


@dataclass(frozen=True, slots=True)
class Character:
    id: UUID
    display_name: str
    long_name: str | None = None
    level: int | None = None
    active: bool = True
    version: int = 0

    def __post_init__(self) -> None:
        if not self.display_name.strip():
            raise ValueError("A character display name is required.")
        if self.level is not None and not 1 <= self.level <= 20:
            raise ValueError("A character level must be between 1 and 20.")
        if self.version < 0:
            raise ValueError("A character version cannot be negative.")

    @classmethod
    def create(cls, display_name: str, long_name: str | None = None) -> Character:
        return cls(id=uuid4(), display_name=display_name, long_name=long_name)
