"""Migration 0012: upgrade, downgrade, upgrade, and the history it must not touch.

The rollback evidence the 2026-08-18 P3.3 remediation owes for the one schema
change it makes — `reconciliation_jobs.effect_committed_at` and the check
constraint that keeps it `NULL` for a preview.

It is a **successor** to 0011 rather than an edit of it. 0011 has been applied to
development and disposable test databases, `.agents/AGENTS.md` says never to edit
an applied migration, and a revision that is edited in place cannot produce the
round-trip evidence below: the database that ran the old text will never run the
new text.

Three things are asserted, and the third is the one a downgrade usually gets
wrong:

1. the schema **after** `upgrade → downgrade → upgrade` is identical to the
   schema after the first upgrade;
2. the downgrade leaves the 0011 schema exactly as 0011 left it — the column and
   its constraint gone, and every other P3.3 object untouched;
3. **append-only history seeded before the revision is unchanged**, by both
   directions, compared on `xmin` so an `UPDATE … SET x = x` would show.
"""
from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import text

from tests.conftest import run_alembic
from tests.web.test_migration_0011_round_trip import history, schema_fingerprint

pytestmark = pytest.mark.database

REVISION = "0012"
PREVIOUS = "0011"

COLUMN = "effect_committed_at"
CONSTRAINT = "ck_reconciliation_jobs_only_an_apply_commits_an_effect"


def has_column(connection) -> bool:
    return (
        connection.execute(
            text(
                "SELECT count(*) FROM information_schema.columns "
                "WHERE table_schema = 'public' "
                "AND table_name = 'reconciliation_jobs' AND column_name = :name"
            ),
            {"name": COLUMN},
        ).scalar_one()
        == 1
    )


def has_constraint(connection) -> bool:
    return (
        connection.execute(
            text("SELECT count(*) FROM pg_constraint WHERE conname = :name"),
            {"name": CONSTRAINT},
        ).scalar_one()
        == 1
    )


@pytest.fixture()
def seeded_history(migrated_database):
    """Append-only rows written at head, then carried down and up again."""
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
                    "action": f"probe.before_0012.{index}",
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
        assert has_column(connection)
        assert has_constraint(connection)

    run_alembic(database_url, "downgrade", PREVIOUS)
    try:
        with migrated_database.begin() as connection:
            at_previous = schema_fingerprint(connection)
            assert not has_column(connection), "the column survived the downgrade"
            assert not has_constraint(connection)
            # Everything 0011 built is still there: this revision adds one column
            # and must remove exactly that on the way back.
            for table in (
                "snapshot_folder_selections",
                "reconciliation_jobs",
                "reconciliation_job_results",
            ):
                assert (
                    connection.execute(
                        text("SELECT to_regclass(:name)"), {"name": table}
                    ).scalar_one()
                    is not None
                ), table
            assert history(connection) == seeded_history, "the downgrade touched history"
    finally:
        run_alembic(database_url, "upgrade", "head")

    with migrated_database.begin() as connection:
        assert schema_fingerprint(connection) == at_head
        assert history(connection) == seeded_history, "the re-upgrade touched history"

    assert at_previous != at_head, "the comparison would be vacuous if they matched"


def test_a_preview_cannot_carry_a_committed_effect(migrated_database, database_url):
    """The constraint, falsified rather than assumed.

    A preview rolls its own transaction back and writes nothing, so it has no
    effect to fence. The column is therefore `NULL` for every preview, and the
    database is what enforces that rather than a comment in the worker.
    """
    from sqlalchemy.exc import IntegrityError

    from tests.web.p3_3_fixtures import clean_p3_3_tables, seed_job, seed_snapshot
    from tests.web.portal_fixtures import clean_p3_2_tables, seed_callers
    from application.web.config import WebSettings
    from tests.web_fixtures import web_environment
    from pathlib import Path
    import tempfile

    with tempfile.TemporaryDirectory() as directory:
        settings = WebSettings.from_environment(web_environment(Path(directory)))
        callers = seed_callers(migrated_database, settings, states=("C",))
        try:
            with migrated_database.begin() as connection:
                snapshot_id, checksum = seed_snapshot(connection)
                job_id = seed_job(
                    connection,
                    snapshot_id=snapshot_id,
                    account_id=callers["C"].account_id,
                    checksum=checksum,
                )
            with pytest.raises(IntegrityError) as refusal:
                with migrated_database.begin() as connection:
                    connection.execute(
                        text(
                            "UPDATE reconciliation_jobs SET effect_committed_at = now(), "
                            # Set too, so **this** constraint is the only one the
                            # statement can violate. 0013 added
                            # `effect_result_accompanies_the_fence`, and which of
                            # two violated checks PostgreSQL names is not
                            # something a case should depend on.
                            "effect_result = '{}'::jsonb "
                            "WHERE id = :id"
                        ),
                        {"id": job_id},
                    )
            assert CONSTRAINT in str(refusal.value)
        finally:
            with migrated_database.begin() as connection:
                clean_p3_3_tables(connection)
                clean_p3_2_tables(connection)


def test_the_revision_descends_from_0011_on_a_single_head():
    """One linear chain. A branch would make "upgrade head" ambiguous.

    0012 stopped being the head later on 2026-08-18, when the effect-publication
    remediation added 0013 as a **successor** rather than editing this revision —
    so this case asserts a single head and this revision's place in the chain,
    instead of asserting that this revision is the head.
    """
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    script = ScriptDirectory.from_config(Config("alembic.ini"))
    heads = script.get_heads()
    assert len(heads) == 1, heads
    assert script.get_revision(REVISION).down_revision == PREVIOUS
