"""Repository contract tests.

ADR 0003 requires these to run against real PostgreSQL and against the schema
the migration produces, not against tables created from metadata in another
engine. A second implementation (the Sheets adapter) does not exist yet, so the
suite is not parameterised over implementations until one does.
"""
from __future__ import annotations

from dataclasses import replace

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from application.errors import ConcurrencyConflictError
from adapters.database.repositories import (
    SqlAlchemyCharacterRepository,
    SqlAlchemyDiscordUserRepository,
)
from adapters.database.unit_of_work import SqlAlchemyUnitOfWork
from domain.identity import Character, DiscordUser

pytestmark = pytest.mark.database


@pytest.fixture()
def session(db_connection):
    """A session inside the fixture's transaction, so nothing is ever committed."""
    with Session(bind=db_connection, join_transaction_mode="create_savepoint") as session:
        yield session


def test_character_repository_round_trip(session):
    repository = SqlAlchemyCharacterRepository(session)
    character = Character.create("Synthetic Hero", "Synthetic Hero the Long")

    repository.add(character)
    session.flush()

    assert repository.get(character.id) == character


def test_character_repository_returns_none_for_an_unknown_id(session):
    repository = SqlAlchemyCharacterRepository(session)

    assert repository.get(Character.create("Absent").id) is None


def test_discord_user_repository_round_trip(session):
    repository = SqlAlchemyDiscordUserRepository(session)
    user = DiscordUser(100000000000000001, "synthetic-user", "Synthetic User")

    repository.add(user)
    session.flush()

    assert repository.get(user.discord_id) == user


def test_discord_user_repository_preserves_full_snowflake_precision(session):
    """A 64-bit snowflake must survive the round trip exactly."""
    repository = SqlAlchemyDiscordUserRepository(session)
    user = DiscordUser(9_223_372_036_854_775_807, "synthetic-max")

    repository.add(user)
    session.flush()

    assert repository.get(user.discord_id).discord_id == user.discord_id


def test_character_repository_increments_the_version_on_save(session):
    repository = SqlAlchemyCharacterRepository(session)
    original = Character.create("Synthetic Hero")
    repository.add(original)
    session.flush()

    updated = repository.save(
        replace(original, display_name="Updated Synthetic Hero"), expected_version=0
    )

    assert updated.version == 1
    assert repository.get(original.id) == updated


def test_character_repository_detects_a_stale_optimistic_version(session):
    repository = SqlAlchemyCharacterRepository(session)
    original = Character.create("Synthetic Hero")
    repository.add(original)
    session.flush()
    repository.save(replace(original, display_name="First Writer"), expected_version=0)

    with pytest.raises(ConcurrencyConflictError):
        repository.save(replace(original, display_name="Second Writer"), expected_version=0)

    assert repository.get(original.id).display_name == "First Writer"


def test_character_repository_rejects_saving_an_unknown_character(session):
    repository = SqlAlchemyCharacterRepository(session)

    with pytest.raises(ConcurrencyConflictError):
        repository.save(Character.create("Never Persisted"), expected_version=0)


def test_saving_a_character_advances_updated_at(committed_database):
    """Regression: `updated_at` kept its insert value through every update.

    `now()` is the transaction timestamp, so the update runs in its own
    transaction — which is also how a real use case would run it.
    """
    character = Character.create("Synthetic Hero")
    with SqlAlchemyUnitOfWork(committed_database) as unit_of_work:
        unit_of_work.characters.add(character)
        unit_of_work.commit()

    with SqlAlchemyUnitOfWork(committed_database) as unit_of_work:
        unit_of_work.characters.save(replace(character, level=3), expected_version=0)
        unit_of_work.commit()

    with committed_database.connect() as connection:
        row = connection.execute(
            text("SELECT created_at, updated_at FROM characters WHERE id = :id"),
            {"id": character.id},
        ).one()
    assert row.updated_at > row.created_at


def test_a_repository_write_is_not_visible_before_the_use_case_commits(
    committed_database,
):
    """The transaction boundary belongs to the caller, never to the repository."""
    character = Character.create("Uncommitted Synthetic Hero")

    with SqlAlchemyUnitOfWork(committed_database) as unit_of_work:
        unit_of_work.characters.add(character)
        with committed_database.connect() as observer:
            visible = observer.execute(
                text("SELECT count(*) FROM characters WHERE id = :id"),
                {"id": character.id},
            ).scalar_one()

    assert visible == 0


def test_unit_of_work_commits_only_when_the_application_asks(committed_database):
    committed = Character.create("Committed Synthetic Hero")
    rolled_back = Character.create("Rolled Back Synthetic Hero")

    with SqlAlchemyUnitOfWork(committed_database) as unit_of_work:
        unit_of_work.characters.add(committed)
        unit_of_work.commit()

    with SqlAlchemyUnitOfWork(committed_database) as unit_of_work:
        unit_of_work.characters.add(rolled_back)

    with SqlAlchemyUnitOfWork(committed_database) as unit_of_work:
        assert unit_of_work.characters.get(committed.id) == committed
        assert unit_of_work.characters.get(rolled_back.id) is None


def test_a_failed_use_case_leaves_no_partial_state(committed_database):
    """Multi-write atomicity: an error after the first write persists neither."""
    user = DiscordUser(100000000000000021, "synthetic-user")
    character = Character.create("Synthetic Hero")

    with pytest.raises(RuntimeError, match="synthetic failure"):
        with SqlAlchemyUnitOfWork(committed_database) as unit_of_work:
            unit_of_work.discord_users.add(user)
            unit_of_work.characters.add(character)
            raise RuntimeError("synthetic failure")

    with SqlAlchemyUnitOfWork(committed_database) as unit_of_work:
        assert unit_of_work.discord_users.get(user.discord_id) is None
        assert unit_of_work.characters.get(character.id) is None


def test_a_constraint_violation_rolls_the_whole_use_case_back(committed_database):
    """A database constraint failure must not leave the earlier write behind."""
    good = Character.create("Valid Synthetic Hero")

    with pytest.raises(Exception):
        with SqlAlchemyUnitOfWork(committed_database) as unit_of_work:
            unit_of_work.characters.add(good)
            unit_of_work.characters.add(
                Character(id=good.id, display_name="Duplicate Identifier")
            )
            unit_of_work.commit()

    with SqlAlchemyUnitOfWork(committed_database) as unit_of_work:
        assert unit_of_work.characters.get(good.id) is None
