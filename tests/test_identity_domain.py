from uuid import UUID, uuid4

import pytest

from domain.identity import Character, DiscordUser


def test_character_create_assigns_stable_application_uuid():
    character = Character.create("Test Hero")

    assert isinstance(character.id, UUID)
    assert character.display_name == "Test Hero"
    assert character.version == 0


@pytest.mark.parametrize("name", ["", " ", "\t"])
def test_character_rejects_blank_display_name(name):
    with pytest.raises(ValueError, match="display name"):
        Character.create(name)


def test_discord_user_rejects_non_positive_snowflake():
    with pytest.raises(ValueError, match="positive snowflakes"):
        DiscordUser(discord_id=0, username="synthetic")


@pytest.mark.parametrize("level", [0, 21])
def test_character_rejects_level_outside_dnd_range(level):
    with pytest.raises(ValueError, match="between 1 and 20"):
        Character(id=uuid4(), display_name="Test Hero", level=level)
