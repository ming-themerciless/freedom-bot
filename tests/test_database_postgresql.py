from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError

from tests.conftest import account_for, link_platform_account, run_alembic

pytestmark = pytest.mark.database

MIGRATED_TABLES = {
    "audit_events",
    "character_access",
    "characters",
    "discord_guild_memberships",
    "discord_membership_roles",
    "discord_users",
    "external_actor_mappings",
    "foundry_snapshots",
    "idempotency_keys",
    "platform_initialization",
    "sheet_row_mappings",
    "snapshot_imports",
}


def insert_user(connection, discord_id: int, username: str = "synthetic-user") -> int:
    """A Discord user **and** the platform account stage A would have linked to it.

    The two are inseparable from migration 0007 onward: `character_access` is
    keyed by the account, and the stage C trigger refuses a row whose account has
    no active Discord identity. Creating only the Discord fact would produce a
    user no authorization row could name.
    """
    connection.execute(
        text("INSERT INTO discord_users (id, username) VALUES (:id, :username)"),
        {"id": discord_id, "username": username},
    )
    link_platform_account(connection, discord_id)
    return discord_id


def insert_character(connection, name: str = "Synthetic Hero"):
    character_id = uuid4()
    connection.execute(
        text("INSERT INTO characters (id, display_name) VALUES (:id, :name)"),
        {"id": character_id, "name": name},
    )
    return character_id


def grant_access(connection, character_id, discord_user_id, **overrides) -> None:
    values = {
        "id": uuid4(),
        "character_id": character_id,
        "discord_user_id": discord_user_id,
        "access_kind": "owner",
        "active": True,
        "default_character": False,
        "granted_by": discord_user_id,
        "granted_at": datetime(2026, 7, 30, 12, 0, tzinfo=timezone.utc),
        "revoked_at": None,
        "expires_at": None,
        "reason": "synthetic council grant",
        "correlation": uuid4(),
    }
    values.update(overrides)
    # The account is resolved from the Discord identity rather than passed in,
    # exactly as the application does after the stage C cutover: a caller that
    # could name an account directly could name one whose identity is somebody
    # else's, which is the mistake control total T6 exists to catch.
    values["platform_account_id"] = account_for(connection, values["discord_user_id"])
    values["granted_by_account_id"] = account_for(connection, values["granted_by"])
    connection.execute(
        text(
            "INSERT INTO character_access (id, character_id, discord_user_id, "
            "platform_account_id, access_kind, active, default_character, "
            "granted_by_discord_user_id, granted_by_account_id, "
            "granted_at, revoked_at, expires_at, reason, audit_correlation_id) VALUES "
            "(:id, :character_id, :discord_user_id, :platform_account_id, "
            ":access_kind, :active, :default_character, :granted_by, "
            ":granted_by_account_id, :granted_at, :revoked_at, :expires_at, "
            ":reason, :correlation)"
        ),
        values,
    )


def record_audit(connection, *, actor: int | None, capability: str = "guild_council", **overrides):
    values = {
        "id": uuid4(),
        "actor": actor,
        "capability": capability,
        "action": "character.updated",
        "entity_type": "character",
        "entity_id": str(uuid4()),
        "source": "web",
        "correlation": uuid4(),
    }
    values.update(overrides)
    connection.execute(
        text(
            "INSERT INTO audit_events (id, actor_discord_user_id, actor_capability, "
            "action, entity_type, entity_id, source, correlation_id, payload) VALUES "
            "(:id, :actor, :capability, :action, :entity_type, :entity_id, :source, "
            ":correlation, '{}'::jsonb)"
        ),
        values,
    )
    return values


# --- migrations -------------------------------------------------------------


def test_migrations_apply_to_empty_postgresql_and_downgrade(database_url):
    engine = create_engine(database_url)
    try:
        run_alembic(database_url, "downgrade", "base")
        assert not MIGRATED_TABLES & set(inspect(engine).get_table_names())

        run_alembic(database_url, "upgrade", "head")
        assert MIGRATED_TABLES <= set(inspect(engine).get_table_names())

        run_alembic(database_url, "downgrade", "base")
        assert not MIGRATED_TABLES & set(inspect(engine).get_table_names())

        run_alembic(database_url, "upgrade", "head")
        assert MIGRATED_TABLES <= set(inspect(engine).get_table_names())
    finally:
        engine.dispose()


def test_migration_matches_table_metadata(database_url):
    """`alembic check`: the migration and the mapped metadata cannot drift apart."""
    completed = run_alembic(database_url, "check")

    assert "No new upgrade operations detected." in completed.stdout


# --- physical representation (ADR 0003) -------------------------------------


def physical_columns(connection, table_name: str) -> dict[str, str]:
    rows = connection.execute(
        text(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_schema = 'public' AND table_name = :table"
        ),
        {"table": table_name},
    )
    return {name: data_type for name, data_type in rows}


def test_discord_snowflakes_are_bigint_in_postgresql(db_connection):
    assert physical_columns(db_connection, "discord_users")["id"] == "bigint"
    memberships = physical_columns(db_connection, "discord_guild_memberships")
    assert memberships["discord_user_id"] == "bigint"
    assert memberships["guild_id"] == "bigint"
    assert physical_columns(db_connection, "discord_membership_roles")["role_id"] == "bigint"
    access = physical_columns(db_connection, "character_access")
    assert access["discord_user_id"] == "bigint"
    assert access["granted_by_discord_user_id"] == "bigint"
    assert physical_columns(db_connection, "audit_events")["actor_discord_user_id"] == "bigint"


def test_application_identifiers_are_uuid_in_postgresql(db_connection):
    assert physical_columns(db_connection, "characters")["id"] == "uuid"
    access = physical_columns(db_connection, "character_access")
    assert access["id"] == "uuid"
    assert access["character_id"] == "uuid"
    assert access["audit_correlation_id"] == "uuid"
    assert physical_columns(db_connection, "audit_events")["correlation_id"] == "uuid"


def test_every_timestamp_column_is_timestamptz(db_connection):
    offenders = db_connection.execute(
        text(
            "SELECT table_name, column_name, data_type FROM information_schema.columns "
            "WHERE table_schema = 'public' AND data_type LIKE 'timestamp%' "
            "AND data_type <> 'timestamp with time zone'"
        )
    ).all()

    assert offenders == []


def test_timestamps_round_trip_as_timezone_aware_utc(db_connection):
    character_id = insert_character(db_connection)

    created_at = db_connection.execute(
        text("SELECT created_at FROM characters WHERE id = :id"), {"id": character_id}
    ).scalar_one()

    assert created_at.tzinfo is not None
    assert created_at.utcoffset() == timedelta(0)


def test_every_foreign_key_declares_delete_behaviour(db_connection):
    unspecified = db_connection.execute(
        text(
            "SELECT conrelid::regclass::text, conname, confdeltype FROM pg_constraint "
            "WHERE contype = 'f' AND connamespace = 'public'::regnamespace "
            "AND confdeltype = 'a'"
        )
    ).all()

    assert unspecified == [], "NO ACTION is the implicit default; state ON DELETE explicitly"


# --- constraints reject invalid data ----------------------------------------


def test_negative_snowflake_is_rejected(db_connection):
    with pytest.raises(IntegrityError):
        insert_user(db_connection, -1)


def test_out_of_range_character_level_is_rejected(db_connection):
    with pytest.raises(IntegrityError):
        db_connection.execute(
            text(
                "INSERT INTO characters (id, display_name, level) "
                "VALUES (:id, 'Synthetic Invalid', 21)"
            ),
            {"id": uuid4()},
        )


def test_blank_display_name_is_rejected(db_connection):
    with pytest.raises(IntegrityError):
        db_connection.execute(
            text("INSERT INTO characters (id, display_name) VALUES (:id, '   ')"),
            {"id": uuid4()},
        )


def test_duplicate_sheet_row_mapping_is_rejected(db_connection):
    first = insert_character(db_connection, "Synthetic First")
    second = insert_character(db_connection, "Synthetic Second")
    statement = text(
        "INSERT INTO sheet_row_mappings (id, character_id, sheet_tab, row_index) "
        "VALUES (:id, :character, 'Characters', 3)"
    )
    db_connection.execute(statement, {"id": uuid4(), "character": first})

    with pytest.raises(IntegrityError):
        db_connection.execute(statement, {"id": uuid4(), "character": second})


def test_duplicate_foundry_actor_mapping_is_rejected(db_connection):
    first = insert_character(db_connection, "Synthetic First")
    second = insert_character(db_connection, "Synthetic Second")
    statement = text(
        "INSERT INTO external_actor_mappings "
        "(id, character_id, world_id, external_actor_id, relink_fingerprint) VALUES "
        "(:id, :character, 'the-guild', 'AbCdEf0123456789', 'Synthetic Hero L3 sorcerer')"
    )
    db_connection.execute(statement, {"id": uuid4(), "character": first})

    with pytest.raises(IntegrityError):
        db_connection.execute(statement, {"id": uuid4(), "character": second})


def test_foundry_actor_id_shape_is_enforced(db_connection):
    character_id = insert_character(db_connection)

    with pytest.raises(IntegrityError):
        db_connection.execute(
            text(
                "INSERT INTO external_actor_mappings "
                "(id, character_id, world_id, external_actor_id, relink_fingerprint) "
                "VALUES (:id, :character, 'the-guild', 'too-short', 'fingerprint')"
            ),
            {"id": uuid4(), "character": character_id},
        )


def test_audit_actor_must_be_a_known_discord_user(db_connection):
    with pytest.raises(IntegrityError):
        db_connection.execute(
            text(
                "INSERT INTO audit_events (id, actor_discord_user_id, actor_capability, "
                "action, entity_type, entity_id, source, correlation_id, payload) VALUES "
                "(:id, 100000000000000999, 'guild_council', 'character.granted', "
                "'character', :entity, 'web', :correlation, '{}'::jsonb)"
            ),
            {"id": uuid4(), "entity": str(uuid4()), "correlation": uuid4()},
        )


def test_deleting_a_user_with_audit_history_is_refused(db_connection):
    user_id = insert_user(db_connection, 100000000000000042)
    record_audit(db_connection, actor=user_id)

    with pytest.raises(IntegrityError):
        db_connection.execute(
            text("DELETE FROM discord_users WHERE id = :id"), {"id": user_id}
        )


def test_idempotency_key_is_unique_per_scope(db_connection):
    statement = text(
        "INSERT INTO idempotency_keys (id, scope, key, request_hash, status) VALUES "
        "(:id, 'discord.interaction', 'synthetic-key', :digest, 'started')"
    )
    db_connection.execute(statement, {"id": uuid4(), "digest": b"\x00" * 32})

    with pytest.raises(IntegrityError):
        db_connection.execute(statement, {"id": uuid4(), "digest": b"\x00" * 32})


def test_idempotency_request_hash_must_be_a_sha256_digest(db_connection):
    with pytest.raises(IntegrityError):
        db_connection.execute(
            text(
                "INSERT INTO idempotency_keys (id, scope, key, request_hash, status) "
                "VALUES (:id, 'discord.interaction', 'short-digest', :digest, 'started')"
            ),
            {"id": uuid4(), "digest": b"\x00" * 16},
        )


# --- character access model (plan §4.2) -------------------------------------


def test_character_access_permits_many_users_and_many_characters(db_connection):
    first_user = insert_user(db_connection, 100000000000000001, "synthetic-one")
    second_user = insert_user(db_connection, 100000000000000002, "synthetic-two")
    first_character = insert_character(db_connection, "Synthetic First")
    second_character = insert_character(db_connection, "Synthetic Second")

    grant_access(db_connection, first_character, first_user, access_kind="owner")
    grant_access(db_connection, first_character, second_user, access_kind="co_owner")
    grant_access(db_connection, second_character, first_user, access_kind="delegate")
    grant_access(db_connection, second_character, second_user, access_kind="viewer")

    assert db_connection.execute(
        text("SELECT count(*) FROM character_access")
    ).scalar_one() == 4


def test_unknown_access_kind_is_rejected(db_connection):
    user_id = insert_user(db_connection, 100000000000000003)
    character_id = insert_character(db_connection)

    with pytest.raises(IntegrityError):
        grant_access(db_connection, character_id, user_id, access_kind="administrator")


def test_duplicate_active_link_is_rejected(db_connection):
    user_id = insert_user(db_connection, 100000000000000004)
    character_id = insert_character(db_connection)
    grant_access(db_connection, character_id, user_id)

    with pytest.raises(IntegrityError):
        grant_access(db_connection, character_id, user_id, access_kind="viewer")


def test_revoked_grant_is_kept_as_history_and_access_can_be_regranted(db_connection):
    """Regression: a full unique key forced re-grants to overwrite the revocation."""
    user_id = insert_user(db_connection, 100000000000000005)
    character_id = insert_character(db_connection)
    granted_at = datetime(2026, 7, 30, 12, 0, tzinfo=timezone.utc)
    revoked_at = granted_at + timedelta(days=1)
    grant_access(
        db_connection,
        character_id,
        user_id,
        active=False,
        granted_at=granted_at,
        revoked_at=revoked_at,
        reason="council revocation",
    )

    grant_access(
        db_connection,
        character_id,
        user_id,
        granted_at=revoked_at + timedelta(days=1),
        reason="council re-grant",
    )

    rows = db_connection.execute(
        text(
            "SELECT active, revoked_at, reason FROM character_access "
            "WHERE character_id = :character AND discord_user_id = :user "
            "ORDER BY granted_at"
        ),
        {"character": character_id, "user": user_id},
    ).all()
    assert [row.active for row in rows] == [False, True]
    assert rows[0].revoked_at == revoked_at
    assert [row.reason for row in rows] == ["council revocation", "council re-grant"]


def test_revoked_state_and_timestamp_must_agree(db_connection):
    user_id = insert_user(db_connection, 100000000000000006)
    character_id = insert_character(db_connection)

    with pytest.raises(IntegrityError):
        grant_access(db_connection, character_id, user_id, active=True, revoked_at=datetime(
            2026, 7, 31, tzinfo=timezone.utc
        ))


def test_revocation_cannot_precede_the_grant(db_connection):
    user_id = insert_user(db_connection, 100000000000000007)
    character_id = insert_character(db_connection)

    with pytest.raises(IntegrityError):
        grant_access(
            db_connection,
            character_id,
            user_id,
            active=False,
            granted_at=datetime(2026, 7, 30, tzinfo=timezone.utc),
            revoked_at=datetime(2026, 7, 29, tzinfo=timezone.utc),
        )


def test_expiry_cannot_precede_the_grant(db_connection):
    user_id = insert_user(db_connection, 100000000000000008)
    character_id = insert_character(db_connection)

    with pytest.raises(IntegrityError):
        grant_access(
            db_connection,
            character_id,
            user_id,
            granted_at=datetime(2026, 7, 30, tzinfo=timezone.utc),
            expires_at=datetime(2026, 7, 29, tzinfo=timezone.utc),
        )


def test_blank_grant_reason_is_rejected(db_connection):
    user_id = insert_user(db_connection, 100000000000000009)
    character_id = insert_character(db_connection)

    with pytest.raises(IntegrityError):
        grant_access(db_connection, character_id, user_id, reason="  ")


def test_a_character_has_at_most_one_active_owner(db_connection):
    """OD-37: a character has exactly one owner."""
    first_user = insert_user(db_connection, 100000000000000030, "synthetic-one")
    second_user = insert_user(db_connection, 100000000000000031, "synthetic-two")
    character_id = insert_character(db_connection)
    grant_access(db_connection, character_id, first_user, access_kind="owner")

    with pytest.raises(IntegrityError):
        grant_access(db_connection, character_id, second_user, access_kind="owner")


def test_one_owner_does_not_limit_co_owners_delegates_or_viewers(db_connection):
    character_id = insert_character(db_connection)
    owner = insert_user(db_connection, 100000000000000032, "synthetic-owner")
    grant_access(db_connection, character_id, owner, access_kind="owner")

    for offset, kind in enumerate(("co_owner", "delegate", "viewer", "co_owner")):
        user_id = insert_user(
            db_connection, 100000000000000040 + offset, f"synthetic-{offset}"
        )
        grant_access(db_connection, character_id, user_id, access_kind=kind)

    assert db_connection.execute(
        text("SELECT count(*) FROM character_access WHERE character_id = :character"),
        {"character": character_id},
    ).scalar_one() == 5


def test_ownership_can_be_transferred_after_the_previous_owner_is_revoked(db_connection):
    """OD-37: uniqueness covers active rows, so a handover is revoke-then-grant."""
    previous = insert_user(db_connection, 100000000000000033, "synthetic-previous")
    successor = insert_user(db_connection, 100000000000000034, "synthetic-successor")
    character_id = insert_character(db_connection)
    granted_at = datetime(2026, 7, 30, tzinfo=timezone.utc)
    grant_access(
        db_connection,
        character_id,
        previous,
        access_kind="owner",
        active=False,
        granted_at=granted_at,
        revoked_at=granted_at + timedelta(days=1),
        reason="ownership handed over",
    )

    grant_access(db_connection, character_id, successor, access_kind="owner")

    owners = db_connection.execute(
        text(
            "SELECT discord_user_id FROM character_access "
            "WHERE character_id = :character AND active AND access_kind = 'owner'"
        ),
        {"character": character_id},
    ).scalars().all()
    assert owners == [successor]


def test_guild_council_is_not_an_access_kind(db_connection):
    """OD-37: Council reach is role-derived, never a per-character access row."""
    user_id = insert_user(db_connection, 100000000000000035)
    character_id = insert_character(db_connection)

    with pytest.raises(IntegrityError):
        grant_access(db_connection, character_id, user_id, access_kind="guild_council")


# --- audit of privileged modification (plan §4.3, OD-37) ---------------------


def test_audit_records_the_capability_a_modification_was_made_under(db_connection):
    council = insert_user(db_connection, 100000000000000036, "synthetic-council")
    owner = insert_user(db_connection, 100000000000000037, "synthetic-owner")
    character_id = insert_character(db_connection)
    record_audit(
        db_connection, actor=council, capability="guild_council", entity_id=str(character_id)
    )
    record_audit(
        db_connection, actor=owner, capability="character_owner", entity_id=str(character_id)
    )

    capabilities = db_connection.execute(
        text(
            "SELECT actor_discord_user_id, actor_capability FROM audit_events "
            "WHERE entity_id = :entity ORDER BY actor_capability"
        ),
        {"entity": str(character_id)},
    ).all()
    assert [(row.actor_discord_user_id, row.actor_capability) for row in capabilities] == [
        (owner, "character_owner"),
        (council, "guild_council"),
    ]


def test_an_unknown_actor_capability_is_rejected(db_connection):
    user_id = insert_user(db_connection, 100000000000000038)

    with pytest.raises(IntegrityError):
        record_audit(db_connection, actor=user_id, capability="superuser")


def test_a_human_capability_requires_an_acting_user(db_connection):
    with pytest.raises(IntegrityError):
        record_audit(db_connection, actor=None, capability="guild_council")


@pytest.mark.parametrize("capability", ["service_principal", "system"])
def test_automated_actions_may_have_no_acting_user(db_connection, capability):
    record_audit(db_connection, actor=None, capability=capability, source="import")

    assert db_connection.execute(
        text("SELECT count(*) FROM audit_events WHERE actor_capability = :capability"),
        {"capability": capability},
    ).scalar_one() == 1


def test_a_user_has_at_most_one_active_default_character(db_connection):
    user_id = insert_user(db_connection, 100000000000000010)
    first_character = insert_character(db_connection, "Synthetic First")
    second_character = insert_character(db_connection, "Synthetic Second")
    grant_access(db_connection, first_character, user_id, default_character=True)

    with pytest.raises(IntegrityError):
        grant_access(db_connection, second_character, user_id, default_character=True)


def test_a_revoked_default_does_not_block_a_new_default(db_connection):
    user_id = insert_user(db_connection, 100000000000000011)
    first_character = insert_character(db_connection, "Synthetic First")
    second_character = insert_character(db_connection, "Synthetic Second")
    granted_at = datetime(2026, 7, 30, tzinfo=timezone.utc)
    grant_access(
        db_connection,
        first_character,
        user_id,
        default_character=True,
        active=False,
        granted_at=granted_at,
        revoked_at=granted_at + timedelta(days=1),
    )

    grant_access(db_connection, second_character, user_id, default_character=True)

    assert db_connection.execute(
        text(
            "SELECT count(*) FROM character_access "
            "WHERE discord_user_id = :user AND active AND default_character"
        ),
        {"user": user_id},
    ).scalar_one() == 1


def test_deleting_a_character_removes_its_access_and_mappings(db_connection):
    user_id = insert_user(db_connection, 100000000000000012)
    character_id = insert_character(db_connection)
    grant_access(db_connection, character_id, user_id)
    db_connection.execute(
        text(
            "INSERT INTO sheet_row_mappings (id, character_id, sheet_tab, row_index) "
            "VALUES (:id, :character, 'Characters', 7)"
        ),
        {"id": uuid4(), "character": character_id},
    )

    db_connection.execute(
        text("DELETE FROM characters WHERE id = :id"), {"id": character_id}
    )

    assert db_connection.execute(text("SELECT count(*) FROM character_access")).scalar_one() == 0
    assert db_connection.execute(text("SELECT count(*) FROM sheet_row_mappings")).scalar_one() == 0


def test_deleting_a_linked_discord_user_is_refused(db_connection):
    user_id = insert_user(db_connection, 100000000000000013)
    character_id = insert_character(db_connection)
    grant_access(db_connection, character_id, user_id)

    with pytest.raises(IntegrityError):
        db_connection.execute(
            text("DELETE FROM discord_users WHERE id = :id"), {"id": user_id}
        )


def test_membership_roles_follow_the_membership(db_connection):
    user_id = insert_user(db_connection, 100000000000000014)
    db_connection.execute(
        text(
            "INSERT INTO discord_guild_memberships (discord_user_id, guild_id) "
            "VALUES (:user, 900000000000000001)"
        ),
        {"user": user_id},
    )
    db_connection.execute(
        text(
            "INSERT INTO discord_membership_roles (discord_user_id, guild_id, role_id) "
            "VALUES (:user, 900000000000000001, 900000000000000002)"
        ),
        {"user": user_id},
    )

    db_connection.execute(
        text("DELETE FROM discord_guild_memberships WHERE discord_user_id = :user"),
        {"user": user_id},
    )

    assert db_connection.execute(
        text("SELECT count(*) FROM discord_membership_roles")
    ).scalar_one() == 0


def test_membership_role_requires_a_membership(db_connection):
    insert_user(db_connection, 100000000000000015)

    with pytest.raises(IntegrityError):
        db_connection.execute(
            text(
                "INSERT INTO discord_membership_roles (discord_user_id, guild_id, role_id) "
                "VALUES (100000000000000015, 900000000000000003, 900000000000000004)"
            )
        )
