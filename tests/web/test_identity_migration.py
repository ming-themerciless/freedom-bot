"""TC-MIG-01 to TC-MIG-06: the staged Discord-reference migration, on real PostgreSQL.

Stage A's backfill is **total and computed** — every Discord id maps to exactly
one account, with no name anywhere in the derivation. That is the difference
between M-1 and M-2 in the migration contract, and it is why these tests assert
an equality between the old key and the new one rather than a plausible-looking
result.

Each test takes the database down to a chosen revision and always brings it back
to head in a `finally`: the engine is shared with the whole suite.
"""
from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import inspect, select, text

from tests.conftest import run_alembic

pytestmark = pytest.mark.database

HEAD = "head"
STAGE_A = "0006"
STAGE_B = "0007"
BEFORE_STAGE_A = "0005"


def _seed_legacy_rows(engine, *, users: int = 3) -> list[int]:
    """Discord users and one `character_access` row, as Phases 1-2 would leave them.

    Written at revision 0005, so the rows have the shape the migration will
    actually meet: Discord-keyed, with no account column in existence.
    """
    discord_ids = [700000000000010000 + index for index in range(users)]
    with engine.begin() as connection:
        for discord_id in discord_ids:
            connection.execute(
                text(
                    "INSERT INTO discord_users (id, username) VALUES (:id, :name)"
                ),
                {"id": discord_id, "name": f"legacy-{discord_id}"},
            )
        character_id = uuid4()
        connection.execute(
            text(
                "INSERT INTO characters (id, display_name) VALUES (:id, 'Legacy Hero')"
            ),
            {"id": character_id},
        )
        connection.execute(
            text(
                "INSERT INTO character_access (id, character_id, discord_user_id, "
                "access_kind, granted_by_discord_user_id, reason, audit_correlation_id) "
                "VALUES (:id, :character, :owner, 'owner', :grantor, 'legacy grant', :c)"
            ),
            {
                "id": uuid4(),
                "character": character_id,
                "owner": discord_ids[0],
                "grantor": discord_ids[1],
                "c": uuid4(),
            },
        )
    return discord_ids


@pytest.fixture()
def legacy_database(database_url, migrated_database):
    """A database at 0005 holding legacy rows, restored to head afterwards."""
    run_alembic(database_url, "downgrade", BEFORE_STAGE_A)
    discord_ids = _seed_legacy_rows(migrated_database)
    try:
        yield discord_ids
    finally:
        run_alembic(database_url, "upgrade", HEAD)
        with migrated_database.begin() as connection:
            connection.execute(text("DELETE FROM character_access"))
            connection.execute(text("DELETE FROM characters"))
            connection.execute(text("DELETE FROM external_identities"))
            connection.execute(text("DELETE FROM platform_accounts"))
            connection.execute(text("DELETE FROM discord_users"))


# ---------------------------------------------------------------------------
# TC-MIG-01, TC-MIG-02
# ---------------------------------------------------------------------------


def test_stage_a_gives_every_discord_user_one_account_and_one_active_identity(
    database_url, migrated_database, legacy_database
):
    """TC-MIG-01 and control totals T1-T3, T6.

    T6 is the one that matters: a **full-table equality** between the old key and
    the new key. It is the evidence that the migration *mapped* rather than
    guessed, and a pairing bug would show up here as a mismatch rather than as a
    plausible-looking set of rows.
    """
    discord_ids = legacy_database
    run_alembic(database_url, "upgrade", STAGE_A)

    with migrated_database.connect() as connection:
        accounts = connection.execute(
            text("SELECT count(*) FROM platform_accounts")
        ).scalar_one()
        identities = connection.execute(
            text(
                "SELECT count(*) FROM external_identities WHERE provider_key = 'discord'"
            )
        ).scalar_one()
        distinct = connection.execute(
            text(
                "SELECT count(DISTINCT subject) FROM external_identities "
                "WHERE provider_key = 'discord'"
            )
        ).scalar_one()
        pairs = connection.execute(
            text(
                "SELECT subject, platform_account_id FROM external_identities "
                "WHERE provider_key = 'discord' ORDER BY subject"
            )
        ).all()
        mismatched = connection.execute(
            text(
                """
                SELECT count(*) FROM character_access ca
                 WHERE NOT EXISTS (
                        SELECT 1 FROM external_identities e
                         WHERE e.platform_account_id = ca.platform_account_id
                           AND e.provider_key = 'discord'
                           AND e.state = 'active'
                           AND e.subject = ca.discord_user_id::text
                       )
                """
            )
        ).scalar_one()

    assert accounts == len(discord_ids)  # T1
    assert identities == len(discord_ids)  # T2
    assert distinct == identities  # T3
    assert mismatched == 0  # T6
    assert {subject for subject, _ in pairs} == {str(i) for i in discord_ids}
    assert len({account for _, account in pairs}) == len(discord_ids), (
        "two Discord users share an account; the backfill paired them wrongly"
    )


def test_the_character_access_row_resolves_to_its_own_users_accounts(
    database_url, migrated_database, legacy_database
):
    """T4/T5, and the specific failure a row-number pairing would have produced."""
    discord_ids = legacy_database
    run_alembic(database_url, "upgrade", STAGE_A)

    with migrated_database.connect() as connection:
        row = connection.execute(
            text(
                """
                SELECT ca.discord_user_id, ca.granted_by_discord_user_id,
                       owner.subject AS owner_subject,
                       grantor.subject AS grantor_subject
                  FROM character_access ca
                  JOIN external_identities owner
                    ON owner.platform_account_id = ca.platform_account_id
                   AND owner.provider_key = 'discord'
                  JOIN external_identities grantor
                    ON grantor.platform_account_id = ca.granted_by_account_id
                   AND grantor.provider_key = 'discord'
                """
            )
        ).mappings().one()

    assert row["owner_subject"] == str(discord_ids[0])
    assert row["grantor_subject"] == str(discord_ids[1])
    assert row["discord_user_id"] == discord_ids[0]
    assert row["granted_by_discord_user_id"] == discord_ids[1]


# ---------------------------------------------------------------------------
# TC-MIG-03
# ---------------------------------------------------------------------------


def test_re_running_the_backfill_inserts_nothing(
    database_url, migrated_database, legacy_database
):
    """TC-MIG-03. Idempotent by construction, not by a flag somebody checks.

    The insert selects `discord_users` that have no Discord identity, so a
    re-run — including one after a partial failure — completes the remainder and
    adds nothing else. That is ADR 0003's "idempotency from mapping constraints".
    """
    run_alembic(database_url, "upgrade", STAGE_A)
    with migrated_database.connect() as connection:
        first = connection.execute(
            text("SELECT count(*) FROM platform_accounts")
        ).scalar_one()

    # Down to 0005 and up again: the backfill runs a second time over the same
    # sources. (Stage A's downgrade drops the accounts, so this also exercises
    # the reversal.)
    run_alembic(database_url, "downgrade", BEFORE_STAGE_A)
    run_alembic(database_url, "upgrade", STAGE_A)

    with migrated_database.connect() as connection:
        second = connection.execute(
            text("SELECT count(*) FROM platform_accounts")
        ).scalar_one()
        orphans = connection.execute(
            text(
                "SELECT count(*) FROM character_access "
                "WHERE platform_account_id IS NULL OR granted_by_account_id IS NULL"
            )
        ).scalar_one()
    assert second == first
    assert orphans == 0


# ---------------------------------------------------------------------------
# TC-MIG-04
# ---------------------------------------------------------------------------


def test_each_stage_round_trips_leaving_identical_data(
    database_url, migrated_database, legacy_database
):
    """TC-MIG-04. `upgrade -> downgrade -> upgrade` for stages A, B and C.

    The legacy Discord columns are what is compared: they are the ones that must
    survive untouched, because they are what a rollback would fall back to.
    """
    def legacy_snapshot():
        with migrated_database.connect() as connection:
            return connection.execute(
                text(
                    "SELECT id, character_id, discord_user_id, "
                    "granted_by_discord_user_id, access_kind, reason "
                    "FROM character_access ORDER BY id"
                )
            ).all()

    run_alembic(database_url, "upgrade", HEAD)
    before = legacy_snapshot()

    for stage, previous in ((HEAD, STAGE_B), (STAGE_B, STAGE_A), (STAGE_A, BEFORE_STAGE_A)):
        run_alembic(database_url, "downgrade", previous)
        run_alembic(database_url, "upgrade", stage)
        assert legacy_snapshot() == before, f"{stage} did not round-trip"


# ---------------------------------------------------------------------------
# TC-MIG-05
# ---------------------------------------------------------------------------


def test_stage_b_enforces_both_index_sets_at_once(
    database_url, migrated_database, legacy_database
):
    """TC-MIG-05. Both invariant sets enforce simultaneously, which is the reversibility.

    While both stand, a wrong mapping is rejected loudly by one of them before
    any user sees an authorization they should not have.
    """
    from sqlalchemy.exc import IntegrityError

    discord_ids = legacy_database
    run_alembic(database_url, "upgrade", STAGE_B)

    inspector = inspect(migrated_database)
    indexes = {index["name"] for index in inspector.get_indexes("character_access")}
    assert "uq_character_access_one_active_link" in indexes
    assert "uq_character_access_one_active_link_account" in indexes
    assert "uq_character_access_one_active_default_per_user" in indexes
    assert "uq_character_access_one_active_default_per_account" in indexes
    # OD-37's owner rule never referenced the user column, so it has no
    # account-keyed counterpart. Stated so a reader counting two new indexes for
    # three old ones finds the answer rather than infers an omission.
    assert "uq_character_access_one_active_owner" in indexes

    with migrated_database.connect() as connection:
        character_id, account_id = connection.execute(
            text(
                "SELECT character_id, platform_account_id FROM character_access LIMIT 1"
            )
        ).one()

    with pytest.raises(IntegrityError):
        with migrated_database.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO character_access (id, character_id, discord_user_id, "
                    "platform_account_id, access_kind, granted_by_discord_user_id, "
                    "granted_by_account_id, reason, audit_correlation_id) "
                    "VALUES (:id, :character, :owner, :account, 'co_owner', :owner, "
                    ":account, 'a duplicate active link', :c)"
                ),
                {
                    "id": uuid4(),
                    "character": character_id,
                    "owner": discord_ids[0],
                    "account": account_id,
                    "c": uuid4(),
                },
            )


# ---------------------------------------------------------------------------
# TC-MIG-06
# ---------------------------------------------------------------------------


def test_stage_c_keeps_the_shadow_current_and_refuses_an_unexpressible_row(
    database_url, migrated_database, legacy_database
):
    """TC-MIG-06. The trigger maintains the legacy column and guards the point of no return.

    A row whose account has no active Discord identity could not be expressed
    both ways, so it could not survive a downgrade. It is refused rather than
    written, which is what keeps stage D a decision rather than an accident.
    """
    from sqlalchemy.exc import DatabaseError

    discord_ids = legacy_database
    run_alembic(database_url, "upgrade", HEAD)

    with migrated_database.begin() as connection:
        character_id = uuid4()
        connection.execute(
            text("INSERT INTO characters (id, display_name) VALUES (:id, 'Shadowed')"),
            {"id": character_id},
        )
        owner_account, grantor_account = connection.execute(
            text(
                "SELECT platform_account_id FROM external_identities "
                "WHERE provider_key = 'discord' AND subject IN (:a, :b) "
                "ORDER BY subject"
            ),
            {"a": str(discord_ids[0]), "b": str(discord_ids[1])},
        ).scalars().all()
        access_id = uuid4()
        # The new path writes **only** the account columns; the trigger fills in
        # the Discord shadow.
        connection.execute(
            text(
                "INSERT INTO character_access (id, character_id, platform_account_id, "
                "granted_by_account_id, access_kind, discord_user_id, "
                "granted_by_discord_user_id, reason, audit_correlation_id) "
                "VALUES (:id, :character, :account, :grantor, 'owner', 0, 0, "
                "'written by the new path', :c)"
            ),
            {
                "id": access_id,
                "character": character_id,
                "account": owner_account,
                "grantor": grantor_account,
                "c": uuid4(),
            },
        )

    with migrated_database.connect() as connection:
        row = connection.execute(
            text(
                "SELECT discord_user_id, granted_by_discord_user_id "
                "FROM character_access WHERE id = :id"
            ),
            {"id": access_id},
        ).mappings().one()
    assert row["discord_user_id"] == discord_ids[0]
    assert row["granted_by_discord_user_id"] == discord_ids[1]

    # An account with no active Discord identity cannot receive access.
    with migrated_database.begin() as connection:
        stranded = uuid4()
        connection.execute(
            text(
                "INSERT INTO platform_accounts (id, status, is_protected_admin) "
                "VALUES (:id, 'active', false)"
            ),
            {"id": stranded},
        )

    with pytest.raises(DatabaseError) as refusal:
        with migrated_database.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO character_access (id, character_id, platform_account_id, "
                    "granted_by_account_id, access_kind, discord_user_id, "
                    "granted_by_discord_user_id, reason, audit_correlation_id) "
                    "VALUES (:id, :character, :account, :account, 'viewer', 0, 0, "
                    "'an account with no Discord identity', :c)"
                ),
                {
                    "id": uuid4(),
                    "character": character_id,
                    "account": stranded,
                    "c": uuid4(),
                },
            )
    assert "active Discord identity" in str(refusal.value)


# ---------------------------------------------------------------------------
# T7 / T8 as refusals
# ---------------------------------------------------------------------------


def test_the_protected_bootstrap_mapping_is_inserted_by_the_migration(
    migrated_database,
):
    """ADR 0010 D10. Exactly one, `ordinary` by construction, and uneditable.

    It is `ordinary` because it has to be: it is the anchor of the ratification
    path, and an anchor whose own provenance were emergency-derived would leave
    nobody able to ratify anything.
    """
    with migrated_database.connect() as connection:
        rows = connection.execute(
            text(
                "SELECT capability, protected, created_under_scope, provenance, "
                "created_by_account_id FROM role_capability_mappings WHERE protected"
            )
        ).mappings().all()
    assert len(rows) == 1
    row = rows[0]
    assert row["capability"] == "platform_administrator"
    assert row["created_under_scope"] == "full"
    assert row["provenance"] == "ordinary"
    # Null only for this row, permitted only by `creator_named_unless_bootstrap`:
    # the migration inserts it at a moment when no platform account exists.
    assert row["created_by_account_id"] is None
