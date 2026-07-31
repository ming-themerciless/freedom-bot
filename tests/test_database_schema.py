from sqlalchemy import BIGINT, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from adapters.database.metadata import metadata
from adapters.database import tables  # noqa: F401


EXPECTED_TABLES = {
    "audit_events",
    "character_access",
    "characters",
    "discord_guild_memberships",
    "discord_membership_roles",
    "discord_users",
    "external_actor_mappings",
    "idempotency_keys",
    "sheet_row_mappings",
}


def constraint_columns(constraint):
    return tuple(column.name for column in constraint.columns)


def test_phase_1_foundation_tables_are_registered():
    assert set(metadata.tables) == EXPECTED_TABLES


def test_discord_snowflakes_use_bigint():
    for table_name, column_name in (
        ("discord_users", "id"),
        ("discord_guild_memberships", "discord_user_id"),
        ("discord_guild_memberships", "guild_id"),
        ("discord_membership_roles", "role_id"),
        ("character_access", "discord_user_id"),
    ):
        assert isinstance(metadata.tables[table_name].c[column_name].type, BIGINT)


def test_character_ids_are_postgresql_uuids():
    assert isinstance(metadata.tables["characters"].c.id.type, UUID)


def test_external_and_sheet_mapping_keys_are_unique():
    external_uniques = {
        constraint_columns(c)
        for c in metadata.tables["external_actor_mappings"].constraints
        if isinstance(c, UniqueConstraint)
    }
    sheet_uniques = {
        constraint_columns(c)
        for c in metadata.tables["sheet_row_mappings"].constraints
        if isinstance(c, UniqueConstraint)
    }

    assert ("world_id", "external_actor_id") in external_uniques
    assert ("sheet_tab", "row_index") in sheet_uniques


def test_mutable_character_has_optimistic_version_constraint():
    table = metadata.tables["characters"]
    checks = {c.name: str(c.sqltext) for c in table.constraints if isinstance(c, CheckConstraint)}

    assert table.c.version.nullable is False
    assert checks["ck_characters_version_non_negative"] == "version >= 0"


def test_character_access_supports_approved_link_model():
    table = metadata.tables["character_access"]
    checks = {
        c.name: str(c.sqltext)
        for c in table.constraints
        if isinstance(c, CheckConstraint)
    }

    assert {
        "default_character",
        "expires_at",
        "reason",
        "audit_correlation_id",
    } <= set(table.c.keys())
    assert checks["ck_character_access_access_kind"] == (
        "access_kind IN ('owner', 'co_owner', 'delegate', 'viewer')"
    )
    unique_indexes = {index.name for index in table.indexes if index.unique}
    assert "uq_character_access_one_active_default_per_user" in unique_indexes
    assert "uq_character_access_one_active_link" in unique_indexes
    assert "uq_character_access_one_active_owner" in unique_indexes


def test_guild_council_is_not_a_per_character_access_kind():
    """OD-37: Council reach comes from the Discord role, not an access row."""
    table = metadata.tables["character_access"]
    checks = {c.name: str(c.sqltext) for c in table.constraints if isinstance(c, CheckConstraint)}

    assert "guild_council" not in checks["ck_character_access_access_kind"]
    assert "role_id" in metadata.tables["discord_membership_roles"].c


def test_audit_records_the_authorization_context():
    """Plan §4.3 and OD-37: who acted, and under what authority."""
    table = metadata.tables["audit_events"]
    checks = {c.name: str(c.sqltext) for c in table.constraints if isinstance(c, CheckConstraint)}

    assert table.c.actor_capability.nullable is False
    assert "guild_council" in checks["ck_audit_events_actor_capability"]
    assert "character_owner" in checks["ck_audit_events_actor_capability"]
    assert "ck_audit_events_human_action_has_an_actor" in checks


def test_character_access_uniqueness_does_not_erase_revocation_history():
    """A whole-table unique key would force a re-grant to overwrite the revocation."""
    table = metadata.tables["character_access"]

    table_wide_uniques = {
        constraint_columns(c)
        for c in table.constraints
        if isinstance(c, UniqueConstraint)
    }
    assert ("character_id", "discord_user_id") not in table_wide_uniques

    active_link = next(
        index
        for index in table.indexes
        if index.name == "uq_character_access_one_active_link"
    )
    assert constraint_columns(active_link) == ("character_id", "discord_user_id")
    assert active_link.dialect_options["postgresql"]["where"] is not None


def test_grant_timestamps_are_ordered_by_constraint():
    table = metadata.tables["character_access"]
    checks = {c.name: str(c.sqltext) for c in table.constraints if isinstance(c, CheckConstraint)}

    assert checks["ck_character_access_revoked_after_grant"] == (
        "revoked_at IS NULL OR revoked_at >= granted_at"
    )
    assert checks["ck_character_access_expiry_after_grant"] == (
        "expires_at IS NULL OR expires_at > granted_at"
    )


def test_every_foreign_key_states_its_delete_behaviour():
    unspecified = [
        f"{table.name}.{key.parent.name}"
        for table in metadata.tables.values()
        for key in table.foreign_keys
        if key.ondelete is None
    ]

    assert unspecified == []


def test_mutable_rows_refresh_updated_at():
    for table_name in ("characters", "discord_users"):
        column = metadata.tables[table_name].c.updated_at
        assert column.onupdate is not None, f"{table_name}.updated_at never advances"


def test_character_level_is_nullable_pending_council_and_range_checked():
    table = metadata.tables["characters"]
    checks = {c.name: str(c.sqltext) for c in table.constraints if isinstance(c, CheckConstraint)}

    assert table.c.level.nullable is True
    assert checks["ck_characters_level_range"] == "level IS NULL OR level BETWEEN 1 AND 20"


def test_audit_event_has_no_mutating_timestamp_or_version_columns():
    columns = set(metadata.tables["audit_events"].c.keys())

    assert "occurred_at" in columns
    assert "updated_at" not in columns
    assert "version" not in columns
