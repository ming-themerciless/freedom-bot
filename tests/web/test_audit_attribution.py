"""TC-AUD-09 to TC-AUD-14 and TC-MIG-14/15/16: the constraint swap, against PostgreSQL.

This is the one place in the package where a design error would be discovered in
production as *"the emergency login does not work"*, so it carries named tests
rather than a general assurance.

Several of these drive Alembic up and down. They **always restore head**, in a
`finally`, because the session-scoped database is shared with every other test in
the suite and a module that left it at `0005` would fail everything that ran
afterwards rather than only itself.
"""
from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import insert, select, text

from adapters.database.tables import audit_events
from tests.conftest import run_alembic
from tests.web.conftest import link_discord, make_account

pytestmark = pytest.mark.database

HEAD = "head"
BEFORE_THE_SWAP = "0005"


def _stage_a_module():
    """Load migration 0006, whose filename is not a Python identifier."""
    import importlib.util
    from pathlib import Path

    path = (
        Path(__file__).resolve().parents[2]
        / "migrations"
        / "versions"
        / "0006_platform_identity_stage_a.py"
    )
    spec = importlib.util.spec_from_file_location("_stage_a", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def at_previous_revision(database_url, migrated_database):
    """Take the database back to before the swap, and always bring it forward again."""
    run_alembic(database_url, "downgrade", BEFORE_THE_SWAP)
    try:
        yield
    finally:
        run_alembic(database_url, "upgrade", HEAD)


def _human_event(**overrides):
    values = {
        "id": uuid4(),
        "actor_capability": "guild_council",
        "action": "character_access.granted",
        "entity_type": "character",
        "entity_id": str(uuid4()),
        "source": "web",
        "correlation_id": uuid4(),
        "payload": {},
    }
    values.update(overrides)
    return values


# ---------------------------------------------------------------------------
# TC-AUD-10 — the "before" half
# ---------------------------------------------------------------------------


def test_before_the_swap_a_discord_independent_human_event_is_refused(
    migrated_database, at_previous_revision
):
    """TC-AUD-10's control case, and the whole reason the swap exists.

    At revision 0005 there is no account column at all, and
    `ck_audit_events_human_action_has_an_actor` requires a Discord user for every
    human capability. A break-glass administrator acting during a Discord outage
    has neither — so the audit event, and with it the login that shares its
    transaction, was **illegal** before migration 0006.
    """
    from sqlalchemy.exc import IntegrityError

    with migrated_database.connect() as connection:
        constraints = {
            row[0]
            for row in connection.execute(
                text(
                    "SELECT conname FROM pg_constraint c JOIN pg_class t "
                    "ON t.oid = c.conrelid WHERE t.relname = 'audit_events' "
                    "AND c.contype = 'c'"
                )
            )
        }
    assert "ck_audit_events_human_action_has_an_actor" in constraints
    assert "ck_audit_events_human_action_has_an_attribution" not in constraints

    with pytest.raises(IntegrityError) as refusal:
        with migrated_database.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO audit_events (id, actor_capability, action, "
                    "entity_type, entity_id, source, correlation_id, payload) "
                    "VALUES (:id, 'platform_administrator', 'auth.emergency.login', "
                    "'session', :entity, 'web', :c, '{}'::jsonb)"
                ),
                {"id": uuid4(), "entity": str(uuid4()), "c": uuid4()},
            )
    assert "human_action_has_an_actor" in str(refusal.value)


# ---------------------------------------------------------------------------
# TC-AUD-10 — the "after" half
# ---------------------------------------------------------------------------


def test_account_attributed_inserts_succeed_in_both_forms(migrated_database):
    """TC-AUD-10. An ordinary-provider event and a break-glass one, both legal."""
    with migrated_database.begin() as connection:
        account_id = make_account(connection)
        connection.execute(
            insert(audit_events).values(
                **_human_event(
                    actor_capability="guild_council",
                    actor_platform_account_id=account_id,
                )
            )
        )
        connection.execute(
            insert(audit_events).values(
                **_human_event(
                    actor_capability="platform_administrator",
                    action="auth.emergency.webauthn.succeeded",
                    actor_platform_account_id=account_id,
                )
            )
        )

    with migrated_database.connect() as connection:
        rows = connection.execute(
            select(audit_events).where(
                audit_events.c.actor_platform_account_id == account_id
            )
        ).mappings().all()
    assert len(rows) == 2
    assert all(row["actor_discord_user_id"] is None for row in rows)


# ---------------------------------------------------------------------------
# TC-AUD-11, TC-AUD-12
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "capability",
    ["guild_member", "character_owner", "dm", "guild_council", "platform_administrator"],
)
def test_an_unattributed_human_action_is_rejected_by_the_database(
    migrated_database, capability
):
    """TC-AUD-11, database half. The rule was widened, not relaxed."""
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError) as refusal:
        with migrated_database.begin() as connection:
            connection.execute(
                insert(audit_events).values(_human_event(actor_capability=capability))
            )
    assert "human_action_has_an_attribution" in str(refusal.value)


@pytest.mark.parametrize(
    "capability",
    ["guild_member", "character_owner", "dm", "guild_council", "platform_administrator"],
)
def test_an_unattributed_human_action_is_rejected_by_the_python_guard(capability):
    """TC-AUD-11, application half.

    `application/audit.py` enforces a copy of the same rule, and it moved in the
    same revision as the constraint. A guard that refused in Python what the
    database now permits would produce the same outage with a different
    traceback.
    """
    from application.audit import ActorCapability, AuditEvent, AuditSource

    with pytest.raises(ValueError) as refusal:
        AuditEvent(
            action="a",
            entity_type="character",
            entity_id="x",
            source=AuditSource.WEB,
            actor_capability=ActorCapability(capability),
            correlation_id=uuid4(),
            payload={},
        )
    assert "identified actor" in str(refusal.value)


@pytest.mark.parametrize("capability", ["system", "service_principal"])
def test_machine_capabilities_remain_valid_with_no_attribution_at_all(
    migrated_database, capability
):
    """TC-AUD-12. Both machine cases survive the swap, exactly as before.

    The Foundry module's submissions (`service_principal`) and bootstrap,
    importer and scheduled work (`system`) name no human because there is none.
    """
    with migrated_database.begin() as connection:
        connection.execute(
            insert(audit_events).values(
                _human_event(actor_capability=capability, source="system")
            )
        )


# ---------------------------------------------------------------------------
# TC-AUD-13
# ---------------------------------------------------------------------------


def test_append_only_denial_still_holds_after_the_swap(migrated_database):
    """TC-AUD-13. Including the `UPDATE` a well-meaning backfill would issue.

    That last case is the one worth naming: setting only the *new* column looks
    harmless and is exactly the statement the migration was designed never to
    need. The trigger refuses it for the schema owner too.
    """
    from sqlalchemy.exc import DatabaseError

    with migrated_database.begin() as connection:
        account_id = make_account(connection)
        event = _human_event(actor_discord_user_id=None, actor_capability="system")
        connection.execute(insert(audit_events).values(**event))

    for statement, parameters in (
        (
            "UPDATE audit_events SET actor_platform_account_id = :account WHERE id = :id",
            {"account": account_id, "id": event["id"]},
        ),
        ("UPDATE audit_events SET action = 'edited' WHERE id = :id", {"id": event["id"]}),
        ("DELETE FROM audit_events WHERE id = :id", {"id": event["id"]}),
    ):
        with pytest.raises(DatabaseError) as refusal:
            with migrated_database.begin() as connection:
                connection.execute(text(statement), parameters)
        assert "append-only table audit_events" in str(refusal.value)


# ---------------------------------------------------------------------------
# TC-AUD-09, TC-MIG-14
# ---------------------------------------------------------------------------


def test_history_is_byte_identical_across_the_swap_including_its_row_versions(
    database_url, migrated_database
):
    """TC-AUD-09. `xmin` is unchanged, which is the strongest available evidence.

    A comparison of column values proves the rows *look* the same. `xmin` is
    PostgreSQL's own record of which transaction last wrote each row, so an
    unchanged `xmin` proves no row **was written** — which is the claim the
    migration actually makes.
    """
    seeded = _human_event(actor_capability="system", source="system")
    with migrated_database.begin() as connection:
        connection.execute(insert(audit_events).values(**seeded))

    def snapshot():
        with migrated_database.connect() as connection:
            return connection.execute(
                text(
                    "SELECT id, xmin::text, actor_discord_user_id, actor_capability, "
                    "action, entity_type, entity_id, source, payload::text, occurred_at "
                    "FROM audit_events ORDER BY id"
                )
            ).all()

    before = snapshot()
    assert before, "there is history to compare"

    run_alembic(database_url, "downgrade", BEFORE_THE_SWAP)
    try:
        run_alembic(database_url, "upgrade", HEAD)
    finally:
        run_alembic(database_url, "upgrade", HEAD)

    assert snapshot() == before


def test_the_swap_round_trips_on_a_database_holding_account_attributed_rows(
    database_url, migrated_database
):
    """TC-MIG-14. The case a validating restore would fail.

    The downgrade restores the legacy constraint **`NOT VALID`** precisely
    because the table may by then hold rows the legacy rule is false of. A
    validating `ADD CONSTRAINT` would scan, find them, and fail — leaving the
    downgrade half-applied.
    """
    with migrated_database.begin() as connection:
        account_id = make_account(connection)
        connection.execute(
            insert(audit_events).values(
                **_human_event(
                    actor_capability="platform_administrator",
                    actor_platform_account_id=account_id,
                )
            )
        )

    try:
        run_alembic(database_url, "downgrade", BEFORE_THE_SWAP)

        with migrated_database.connect() as connection:
            constraint = connection.execute(
                text(
                    "SELECT convalidated FROM pg_constraint c JOIN pg_class t "
                    "ON t.oid = c.conrelid WHERE t.relname = 'audit_events' "
                    "AND c.conname = 'ck_audit_events_human_action_has_an_actor'"
                )
            ).scalar_one()
        assert constraint is False, "the restored legacy constraint must be NOT VALID"
    finally:
        run_alembic(database_url, "upgrade", HEAD)

    with migrated_database.connect() as connection:
        constraints = {
            row[0]
            for row in connection.execute(
                text(
                    "SELECT conname FROM pg_constraint c JOIN pg_class t "
                    "ON t.oid = c.conrelid WHERE t.relname = 'audit_events' "
                    "AND c.contype = 'c'"
                )
            )
        }
    assert "ck_audit_events_human_action_has_an_attribution" in constraints
    assert "ck_audit_events_human_action_has_an_actor" not in constraints


# ---------------------------------------------------------------------------
# TC-MIG-15, TC-MIG-16
# ---------------------------------------------------------------------------


def test_the_constraint_inventory_of_all_three_tables_is_exactly_as_documented(
    migrated_database,
):
    """TC-MIG-15 / control total T8.

    Guards against a later migration quietly reintroducing a Discord-only
    attribution rule — and against `foundry_snapshots` acquiring one it must not
    have, because a supervised-bootstrap row that names no human is legitimate.
    """
    # Imported by path, because a revision module's filename is not an
    # identifier. Reading the *migration's own* inventory rather than a copy is
    # what makes T8 and this test the same statement.
    EXPECTED_CHECK_CONSTRAINTS = _stage_a_module().EXPECTED_CHECK_CONSTRAINTS

    with migrated_database.connect() as connection:
        for table, expected in EXPECTED_CHECK_CONSTRAINTS.items():
            found = {
                row[0]
                for row in connection.execute(
                    text(
                        "SELECT c.conname FROM pg_constraint c "
                        "JOIN pg_class t ON t.oid = c.conrelid "
                        "JOIN pg_namespace n ON n.oid = t.relnamespace "
                        "WHERE c.contype = 'c' AND n.nspname = current_schema() "
                        "AND t.relname = :table AND c.conname NOT LIKE '%_not_null'"
                    ),
                    {"table": table},
                )
            }
            assert found == set(expected), table


def test_foundry_snapshots_gained_a_column_and_no_constraint(migrated_database):
    """The asymmetry, asserted rather than described.

    This is the table the naive symmetric fix would have broken: migration 0004
    records that the supervised bootstrap has no interactive user, so a "must
    name somebody" rule here would be false of legitimate rows.
    """
    from sqlalchemy import inspect

    inspector = inspect(migrated_database)
    columns = {c["name"] for c in inspector.get_columns("foundry_snapshots")}
    assert "received_by_account_id" in columns

    with migrated_database.connect() as connection:
        checks = {
            row[0]
            for row in connection.execute(
                text(
                    "SELECT conname FROM pg_constraint c JOIN pg_class t "
                    "ON t.oid = c.conrelid WHERE t.relname = 'foundry_snapshots' "
                    "AND c.contype = 'c'"
                )
            )
        }
    assert not any("attribution" in name for name in checks)


# ---------------------------------------------------------------------------
# TC-AUD-14
# ---------------------------------------------------------------------------


def test_validating_the_new_constraint_succeeds_and_modifies_nothing(
    migrated_database,
):
    """TC-AUD-14. Validation is possible and safe — merely not required.

    `NOT VALID` already binds every insert and update, so nothing depends on
    this. When an operator does run it, `VALIDATE CONSTRAINT` takes
    `SHARE UPDATE EXCLUSIVE`, scans, and modifies no row — so it fires no row
    trigger and cannot violate the append-only guarantee.
    """
    seeded = _human_event(actor_capability="system", source="system")
    with migrated_database.begin() as connection:
        connection.execute(insert(audit_events).values(**seeded))

    def snapshot():
        with migrated_database.connect() as connection:
            return connection.execute(
                text("SELECT id, xmin::text FROM audit_events ORDER BY id")
            ).all()

    before = snapshot()
    with migrated_database.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE audit_events VALIDATE CONSTRAINT "
                "ck_audit_events_human_action_has_an_attribution"
            )
        )
        connection.execute(
            text(
                "ALTER TABLE audit_events VALIDATE CONSTRAINT "
                "fk_audit_events_actor_platform_account_id_platform_accounts"
            )
        )
    assert snapshot() == before
