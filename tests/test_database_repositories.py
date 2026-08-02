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
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from application.audit import ActorCapability, AuditEvent, AuditSource
from application.errors import ConcurrencyConflictError
from application.imports import SheetRowMapping
from adapters.database.repositories import (
    SqlAlchemyAuditRepository,
    SqlAlchemyCharacterRepository,
    SqlAlchemyDiscordUserRepository,
    SqlAlchemySheetRowMappingRepository,
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


def test_character_repository_finds_by_display_name_ignoring_case(session):
    repository = SqlAlchemyCharacterRepository(session)
    character = Character.create("Synthetic Hero")
    repository.add(character)
    session.flush()

    assert repository.find_by_display_name("synthetic hero") == (character,)
    assert repository.find_by_display_name("Synthetic Villain") == ()


def test_character_repository_returns_every_display_name_match(session):
    """Display names carry no uniqueness rule, so a caller must see all of them."""
    repository = SqlAlchemyCharacterRepository(session)
    first = Character.create("Synthetic Twin")
    second = Character.create("synthetic twin")
    repository.add(first)
    repository.add(second)
    session.flush()

    found = repository.find_by_display_name("Synthetic Twin")

    assert {character.id for character in found} == {first.id, second.id}


def test_sheet_row_mapping_repository_round_trip(session):
    characters_repository = SqlAlchemyCharacterRepository(session)
    repository = SqlAlchemySheetRowMappingRepository(session)
    character = Character.create("Synthetic Hero")
    characters_repository.add(character)
    mapping = SheetRowMapping(character.id, "Characters", 3)

    repository.add(mapping)
    session.flush()

    assert repository.get_character_id("Characters", 3) == character.id
    assert repository.get_character_id("Characters", 4) is None
    assert repository.get_character_id("Retired", 3) is None
    assert repository.list_for_tab("Characters") == (mapping,)


def test_sheet_row_mapping_repository_lists_a_tab_in_row_order(session):
    characters_repository = SqlAlchemyCharacterRepository(session)
    repository = SqlAlchemySheetRowMappingRepository(session)
    for row_index in (9, 3, 5):
        character = Character.create(f"Synthetic Hero {row_index}")
        characters_repository.add(character)
        repository.add(SheetRowMapping(character.id, "Characters", row_index))
    session.flush()

    assert [m.row_index for m in repository.list_for_tab("Characters")] == [3, 5, 9]


def test_the_database_refuses_two_characters_on_one_sheet_row(session):
    """Idempotency is a constraint, not a convention (ADR 0003)."""
    characters_repository = SqlAlchemyCharacterRepository(session)
    repository = SqlAlchemySheetRowMappingRepository(session)
    first = Character.create("Synthetic Hero")
    second = Character.create("Synthetic Rival")
    characters_repository.add(first)
    characters_repository.add(second)
    repository.add(SheetRowMapping(first.id, "Characters", 3))
    session.flush()

    # A Core insert reaches the server immediately, so the constraint fires here
    # rather than at flush time.
    with pytest.raises(IntegrityError):
        repository.add(SheetRowMapping(second.id, "Characters", 3))


def test_audit_repository_appends_an_unattended_import_event(session):
    characters_repository = SqlAlchemyCharacterRepository(session)
    repository = SqlAlchemyAuditRepository(session)
    character = Character.create("Synthetic Hero")
    characters_repository.add(character)
    event = AuditEvent(
        action="sheet_import.character.created",
        entity_type="character",
        entity_id=str(character.id),
        source=AuditSource.IMPORT,
        actor_capability=ActorCapability.SYSTEM,
        correlation_id=character.id,
        payload={"sheet_tab": "Characters", "row_index": 3},
    )

    repository.record(event)
    session.flush()

    stored = session.execute(
        text(
            "SELECT actor_discord_user_id, actor_capability, source, payload "
            "FROM audit_events WHERE id = :id"
        ),
        {"id": event.id},
    ).one()
    assert stored.actor_discord_user_id is None
    assert stored.actor_capability == "system"
    assert stored.source == "import"
    assert stored.payload == {"sheet_tab": "Characters", "row_index": 3}


def test_a_nested_frozen_payload_still_stores_as_the_json_it_describes(session):
    """The freeze is recursive; the column is JSONB, and neither may bend.

    `MappingProxyType` and `tuple` are what the recursive freeze produces and
    neither is JSON-serializable, so the adapter converts back at the
    persistence boundary. If it stopped doing that this test fails at the
    driver, and if it converted by mutating the event the assertion below on
    the in-memory payload fails instead.
    """
    characters_repository = SqlAlchemyCharacterRepository(session)
    repository = SqlAlchemyAuditRepository(session)
    character = Character.create("Synthetic Hero")
    characters_repository.add(character)
    event = AuditEvent(
        action="sheet_import.character.updated",
        entity_type="character",
        entity_id=str(character.id),
        source=AuditSource.IMPORT,
        actor_capability=ActorCapability.SYSTEM,
        correlation_id=character.id,
        payload={
            "sheet_tab": "Characters",
            "changes": {
                "level": {"from": None, "to": 5},
                "active": {"from": True, "to": False},
            },
            "rows": [3, 4],
        },
    )

    repository.record(event)
    session.flush()

    stored = session.execute(
        text("SELECT payload FROM audit_events WHERE id = :id"), {"id": event.id}
    ).scalar_one()
    assert stored == {
        "sheet_tab": "Characters",
        "changes": {
            "level": {"from": None, "to": 5},
            "active": {"from": True, "to": False},
        },
        "rows": [3, 4],
    }
    # The event itself is unchanged, and still refuses mutation.
    with pytest.raises(TypeError):
        event.payload["changes"]["level"]["to"] = 20  # type: ignore[index]


def test_finite_numbers_survive_the_jsonb_round_trip_at_every_depth(session):
    """The other side of the non-finite refusal: finite numbers must still store.

    `AuditEvent` refuses `NaN` and the infinities because PostgreSQL rejects them
    as JSONB — `invalid input syntax for type json`, which fails the transaction
    and therefore the mutation being audited. That refusal is only correct if it
    is narrow, so this stores finite values nested in both a mapping and a
    sequence and reads them back through the column.

    The values are ordinary magnitudes on purpose. JSONB stores a number as
    `numeric`, so an extreme float such as `1e308` comes back as the exact
    308-digit integer rather than the float that went in. That is a faithful
    JSON round trip and not a defect, but it is a distinct property from the one
    under test here.
    """
    characters_repository = SqlAlchemyCharacterRepository(session)
    repository = SqlAlchemyAuditRepository(session)
    character = Character.create("Synthetic Hero")
    characters_repository.add(character)
    event = AuditEvent(
        action="sheet_import.character.updated",
        entity_type="character",
        entity_id=str(character.id),
        source=AuditSource.IMPORT,
        actor_capability=ActorCapability.SYSTEM,
        correlation_id=character.id,
        payload={
            "changes": {
                "downtime": {"from": 0.0, "to": 1.125},
                "level": {"from": 4, "to": 5},
            },
            "amounts": [-2.5, 0.0, 1234.5],
            "flags": [True, False, None],
        },
    )

    repository.record(event)
    session.flush()

    stored = session.execute(
        text("SELECT payload FROM audit_events WHERE id = :id"), {"id": event.id}
    ).scalar_one()
    assert stored == {
        "changes": {
            "downtime": {"from": 0.0, "to": 1.125},
            "level": {"from": 4, "to": 5},
        },
        "amounts": [-2.5, 0.0, 1234.5],
        "flags": [True, False, None],
    }


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
