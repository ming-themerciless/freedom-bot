"""Migration 0011: upgrade, downgrade, upgrade, and the history it must not touch.

The rollback evidence the package owes, run against real PostgreSQL rather than
argued from the diff. Three things are asserted, and the third is the one a
downgrade usually gets wrong:

1. the schema **after** `upgrade → downgrade → upgrade` is identical to the
   schema after the first upgrade — every column, constraint and index;
2. the downgrade leaves the 0010 schema exactly as 0010 left it, so the revision
   is genuinely reversible rather than merely runnable in reverse;
3. **append-only history seeded before the revision is unchanged by it**, and
   unchanged by rolling it back — count, ids, and each row's `xmin`, which is
   the strongest available evidence that no row was rewritten rather than that it
   merely looks the same.
"""
from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import text

from tests.conftest import run_alembic

pytestmark = pytest.mark.database

REVISION = "0011"
PREVIOUS = "0010"

P3_3_TABLES = (
    "snapshot_folder_selections",
    "reconciliation_jobs",
    "reconciliation_job_results",
)


def schema_fingerprint(connection) -> dict:
    """Columns, constraints and indexes, as PostgreSQL reports them.

    Read from the catalogue rather than from the metadata, because the question
    is what the migration built and not what the application believes.
    """
    columns = connection.execute(
        text(
            "SELECT table_name, column_name, data_type, is_nullable, column_default "
            "FROM information_schema.columns WHERE table_schema = 'public' "
            "ORDER BY table_name, column_name"
        )
    ).all()
    constraints = connection.execute(
        text(
            "SELECT conrelid::regclass::text, conname, pg_get_constraintdef(oid) "
            "FROM pg_constraint WHERE connamespace = 'public'::regnamespace "
            "ORDER BY 1, 2"
        )
    ).all()
    indexes = connection.execute(
        text(
            "SELECT tablename, indexname, indexdef FROM pg_indexes "
            "WHERE schemaname = 'public' ORDER BY tablename, indexname"
        )
    ).all()
    return {
        "columns": [tuple(row) for row in columns],
        "constraints": [tuple(row) for row in constraints],
        "indexes": [tuple(row) for row in indexes],
    }


def history(connection) -> list:
    """Every append-only row, with its `xmin`.

    `xmin` is the transaction that last wrote the row. If a migration rewrote a
    row — even to a value that looks identical — `xmin` changes. Comparing the
    rendered values alone would pass for an `UPDATE ... SET x = x`.
    """
    return [
        tuple(row)
        for row in connection.execute(
            text(
                "SELECT id, action, entity_type, entity_id, actor_capability, "
                "occurred_at, xmin::text FROM audit_events ORDER BY id"
            )
        ).all()
    ]


@pytest.fixture()
def seeded_history(migrated_database, database_url):
    """Append-only rows written **before** the revision is rolled back.

    Written at head and then carried down and up again, which is the ordering
    that matters: a downgrade that dropped a table nothing in 0011 created, or an
    upgrade that rewrote history to "fix" it, would show here.
    """
    with migrated_database.begin() as connection:
        for index in range(3):
            connection.execute(
                text(
                    "INSERT INTO audit_events (id, actor_capability, action, "
                    "entity_type, entity_id, source, correlation_id, payload) "
                    "VALUES (:id, 'system', :action, 'probe', :entity, 'system', "
                    ":correlation, '{}'::jsonb)"
                ),
                {
                    "id": uuid4(),
                    "action": f"probe.before_0011.{index}",
                    "entity": str(index),
                    "correlation": uuid4(),
                },
            )
    with migrated_database.begin() as connection:
        yield history(connection)
    with migrated_database.begin() as connection:
        connection.execute(text("TRUNCATE TABLE audit_events"))


def test_the_revision_round_trips_and_the_schema_is_identical(
    migrated_database, database_url, seeded_history
):
    """`upgrade → downgrade → upgrade`, with the catalogue compared each way."""
    with migrated_database.begin() as connection:
        at_head = schema_fingerprint(connection)
        for table in P3_3_TABLES:
            assert connection.execute(
                text("SELECT to_regclass(:name)"), {"name": table}
            ).scalar_one() is not None, table

    run_alembic(database_url, "downgrade", PREVIOUS)
    with migrated_database.begin() as connection:
        at_previous = schema_fingerprint(connection)
        for table in P3_3_TABLES:
            assert (
                connection.execute(
                    text("SELECT to_regclass(:name)"), {"name": table}
                ).scalar_one()
                is None
            ), f"{table} survived the downgrade"
        # And nothing the revision did not create was removed with it.
        assert (
            connection.execute(
                text("SELECT to_regclass('foundry_snapshots')")
            ).scalar_one()
            is not None
        )
        assert (
            connection.execute(text("SELECT to_regclass('audit_events')")).scalar_one()
            is not None
        )
        assert history(connection) == seeded_history, "the downgrade touched history"

    run_alembic(database_url, "upgrade", "head")
    with migrated_database.begin() as connection:
        assert schema_fingerprint(connection) == at_head
        assert history(connection) == seeded_history, "the re-upgrade touched history"

    assert at_previous != at_head, "the comparison would be vacuous if they matched"


def test_the_downgrade_leaves_no_orphaned_constraint_or_index(
    migrated_database, database_url
):
    """The cycle is dropped explicitly, in the right order.

    `reconciliation_jobs.result_id` and `reconciliation_job_results.job_id`
    reference each other, so a downgrade that dropped the tables without first
    dropping the keys would fail — and one that dropped the keys and stopped
    would leave them behind. Both are checked by name.
    """
    run_alembic(database_url, "downgrade", PREVIOUS)
    try:
        with migrated_database.begin() as connection:
            leftovers = connection.execute(
                text(
                    "SELECT conname FROM pg_constraint "
                    "WHERE conname LIKE '%reconciliation%'"
                )
            ).all()
            indexes = connection.execute(
                text(
                    "SELECT indexname FROM pg_indexes WHERE schemaname = 'public' "
                    "AND indexname LIKE '%reconciliation%'"
                )
            ).all()
        assert leftovers == []
        assert indexes == []
    finally:
        run_alembic(database_url, "upgrade", "head")


def test_the_revision_descends_from_0010_on_a_single_head(migrated_database):
    """One linear chain. A branch would make "upgrade head" ambiguous.

    0011 stopped being the head on 2026-08-18, when the P3.3 remediation added
    0012 as a **successor** rather than editing this revision — which is why this
    case now asserts a single head and this revision's place in the chain,
    instead of asserting that this revision is the head.
    """
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    script = ScriptDirectory.from_config(Config("alembic.ini"))
    heads = script.get_heads()
    assert len(heads) == 1, heads
    revision = script.get_revision(REVISION)
    assert revision.down_revision == PREVIOUS


def test_the_revision_chain_is_unbroken():
    """No applied migration is edited — the rule, asserted rather than trusted.

    A revision that has run somewhere cannot be changed, because the database
    that ran it will never run it again. This checks the property that matters
    for review: every file's `down_revision` chain is unbroken and linear, so a
    correction arrives as a successor rather than as an edit to a revision some
    database has already applied.
    """
    from pathlib import Path
    import re

    root = Path(__file__).resolve().parents[2] / "migrations" / "versions"
    chain = {}
    for path in sorted(root.glob("[0-9][0-9][0-9][0-9]_*.py")):
        body = path.read_text()
        revision = re.search(r'^revision: str = "(\d+)"', body, re.MULTILINE).group(1)
        down = re.search(
            r'^down_revision: str \| None = (?:"(\d+)"|None)', body, re.MULTILINE
        ).group(1)
        chain[revision] = down
    assert chain["0001"] is None
    for revision in sorted(chain):
        if revision == "0001":
            continue
        assert chain[revision] == f"{int(revision) - 1:04d}", revision
    assert REVISION in chain
