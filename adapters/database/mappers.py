from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from domain.identity import Character, DiscordUser


def character_from_row(row: Mapping[str, Any]) -> Character:
    return Character(
        id=row["id"],
        display_name=row["display_name"],
        long_name=row["long_name"],
        level=row["level"],
        active=row["active"],
        version=row["version"],
    )


def discord_user_from_row(row: Mapping[str, Any]) -> DiscordUser:
    return DiscordUser(
        discord_id=row["id"],
        username=row["username"],
        global_name=row["global_name"],
    )
