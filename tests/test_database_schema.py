from sqlalchemy import BIGINT, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from adapters.database.metadata import metadata
from adapters.database import tables  # noqa: F401


PHASE_1_TABLES = {
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

PHASE_2_TABLES = {
    "foundry_snapshots",
    "platform_initialization",
    "snapshot_imports",
    # C-24. The admission fence: which credential generation may still turn a
    # submission into a durable acceptance. See `application/admissions.py`.
    "submission_admissions",
}

#: Phase 3 P3.1 (migration 0006). The set is the identity boundary ADR 0010
#: decides: an account is the identity of a person here, an external identity is
#: an exact `(provider_key, subject)` link to one, and everything else in this
#: group is a credential, a session or a bound on authenticating.
#:
#: `role_capability_mappings` and its append-only event log belong to the
#: administration UI of P3.2, but the **table** is P3.1's: capability resolution
#: reads it on every request, the protected bootstrap row is inserted by
#: migration 0006, and the N-67 allowlist lives in its check constraints.
PHASE_3_TABLES = {
    "platform_accounts",
    "external_identities",
    "oauth_token_grants",
    "sessions",
    "oauth_transactions",
    "webauthn_credentials",
    "webauthn_challenges",
    "recovery_grants",
    "auth_rate_limits",
    "role_capability_mappings",
    "role_capability_mapping_events",
}

#: Phase 3 P3.2 (migration 0010). The Sheet-era identity-evidence pipeline of
#: migration contract M-2, and **the whole of the schema P3.2 adds** — everything
#: else it needs was created and cut over by revisions 0006-0009.
#:
#: The accepted schema decision table names one of these three. The run carries
#: §7.4's source-side control totals, which have nowhere to live on a proposal
#: (a player with no character produces no proposal row); the candidate rows
#: carry §7.6's durable ambiguity as typed child rows, because plan §7.3.1
#: prohibits the delimited, JSON and array alternatives. Both additions are
#: recorded in the P3.2 submission.
#:
#: None of them is authorization-bearing. A `character_access` row is still the
#: only thing that confers reach over a character, and a proposal can name one
#: only when it is `confirmed` — a check constraint, not a convention.
PHASE_3_P3_2_TABLES = {
    "identity_migration_runs",
    "identity_link_proposals",
    "identity_link_proposal_candidates",
}

EXPECTED_TABLES = (
    PHASE_1_TABLES | PHASE_2_TABLES | PHASE_3_TABLES | PHASE_3_P3_2_TABLES
)

#: Tables the Acceptance Authority rejected with ADR 0008 on 2026-08-02. Named
#: rather than merely absent, so that reintroducing one fails a test that says
#: why instead of only widening a set nobody rereads.
REJECTED_TABLES = {
    "character_state_values",
    "character_balances",
    "character_transactions",
}


def constraint_columns(constraint):
    return tuple(column.name for column in constraint.columns)


def test_every_expected_table_is_registered_and_no_others():
    # Listed per phase so that a table added without a milestone is visible as
    # such, rather than merely swelling one set.
    assert set(metadata.tables) == EXPECTED_TABLES


def test_no_generic_state_balance_or_transaction_table_exists():
    """Threshold T-5, as a schema inventory rather than an inspection.

    ADR 0008 proposed a profile-driven key/value store for character state; the
    Acceptance Authority rejected it, and each field group now migrates once
    into the typed model its owning package introduces (plan §7.3).
    """
    assert set(metadata.tables) & REJECTED_TABLES == set()


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

    # Migration 0006 **replaced** `human_action_has_an_actor`, which required a
    # Discord user id for every human capability. It had to go: a break-glass
    # administrator acting during a Discord outage is a human capability with no
    # Discord user, so the old rule refused the audit event ADR 0010 D8's
    # recovery path must write — and with it the emergency login, because the
    # session and its event share a transaction.
    #
    # The rule was not relaxed. Both halves are asserted, because "the new one is
    # present" alone would also pass if the replacement had quietly dropped a
    # case: an identified person is still required, and only the two machine
    # capabilities may act unattributed.
    assert "ck_audit_events_human_action_has_an_actor" not in checks
    attribution = checks["ck_audit_events_human_action_has_an_attribution"]
    assert "actor_platform_account_id IS NOT NULL" in attribution
    assert "actor_discord_user_id IS NOT NULL" in attribution
    assert "service_principal" in attribution and "system" in attribution
    for human in ("guild_council", "platform_administrator", "character_owner"):
        assert human not in attribution, (
            f"{human} must not be able to act without an identified actor"
        )


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
