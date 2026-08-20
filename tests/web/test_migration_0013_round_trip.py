"""Migration 0013 on an **empty** schema: upgrade, downgrade, upgrade.

**Scope, corrected 2026-08-18 by the migration-rollback remediation, and the
correction is the point of this paragraph.** This module seeds `audit_events` and
nothing else; every reconciliation table is empty for the whole round trip. So it
is evidence for exactly one claim — that this revision's statements are
structurally reversible and rebuild an identical catalogue — and the independent
review found it being read as a second, much larger claim it does not support:
that a database which has processed a normal P3.3 apply can be rolled back and
rolled forward again.

It cannot, and that is now a stated boundary rather than an oversight. The
data-bearing cases live in `tests/web/test_migration_0013_rollback_boundary.py`:
a truthfully completed apply, an effect awaiting recovery, a realistic database
below the boundary that does round-trip, and the atomicity of a failed migration
in both directions. **Do not cite this module as rollback evidence for a
populated database.**

What it covers is the schema change itself: `reconciliation_jobs.effect_result`,
the check constraint that ties it to `effect_committed_at`, and the check
constraint that forbids a job denying an import it is holding.

It is a **successor** to 0012, which is itself a successor to 0011. Neither is
edited: both have been applied to development and disposable test databases,
`.agents/AGENTS.md` says never to edit an applied migration, and a revision edited
in place cannot produce round-trip evidence — the database that ran the old text
will never run the new text.

Four things are asserted, all of them on an unused schema:

1. the schema **after** `upgrade → downgrade → upgrade` is identical to the schema
   after the first upgrade;
2. the downgrade leaves the 0012 schema exactly as 0012 left it — this revision's
   column and both of its constraints gone, `effect_committed_at` and 0012's own
   constraint still there, and every other P3.3 object untouched;
3. **append-only history seeded before the revision is unchanged**, by both
   directions, compared on `xmin` so an `UPDATE … SET x = x` would show; and
4. the guard `upgrade()` runs before it adds anything refuses, with a sentence an
   operator can act on, a database holding a row this revision cannot describe.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import text

from application.web.jobs import JobKind

from tests.conftest import run_alembic
from tests.web.test_migration_0011_round_trip import history, schema_fingerprint

pytestmark = pytest.mark.database

REVISION = "0013"
PREVIOUS = "0012"

COLUMN = "effect_result"
ACCOMPANIES = "ck_reconciliation_jobs_effect_result_accompanies_the_fence"
NEVER_DENIED = "ck_reconciliation_jobs_committed_effect_is_never_denied"
#: 0012's own constraint, which this revision's downgrade must leave alone.
PRESERVED = "ck_reconciliation_jobs_only_an_apply_commits_an_effect"


def has_column(connection, name: str = COLUMN) -> bool:
    return (
        connection.execute(
            text(
                "SELECT count(*) FROM information_schema.columns "
                "WHERE table_schema = 'public' "
                "AND table_name = 'reconciliation_jobs' AND column_name = :name"
            ),
            {"name": name},
        ).scalar_one()
        == 1
    )


def has_constraint(connection, name: str) -> bool:
    return (
        connection.execute(
            text("SELECT count(*) FROM pg_constraint WHERE conname = :name"),
            {"name": name},
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
                    "action": f"probe.before_0013.{index}",
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
        assert has_constraint(connection, ACCOMPANIES)
        assert has_constraint(connection, NEVER_DENIED)

    run_alembic(database_url, "downgrade", PREVIOUS)
    try:
        with migrated_database.begin() as connection:
            at_previous = schema_fingerprint(connection)
            assert not has_column(connection), "the column survived the downgrade"
            assert not has_constraint(connection, ACCOMPANIES)
            assert not has_constraint(connection, NEVER_DENIED)
            # And exactly that much: 0012's column and constraint are 0012's to
            # remove, and every table 0011 built is still standing.
            assert has_column(connection, "effect_committed_at")
            assert has_constraint(connection, PRESERVED)
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
            assert history(connection) == seeded_history, (
                "the downgrade touched history"
            )
    finally:
        run_alembic(database_url, "upgrade", "head")

    with migrated_database.begin() as connection:
        assert schema_fingerprint(connection) == at_head
        assert history(connection) == seeded_history, "the re-upgrade touched history"

    assert at_previous != at_head, "the comparison would be vacuous if they matched"


def test_the_upgrade_refuses_a_database_holding_a_row_it_cannot_describe(
    migrated_database, database_url, tmp_path
):
    """The guard, exercised rather than described.

    Every row 0012 could produce with `effect_committed_at` set carries no
    `effect_result`, because the column did not exist — so it cannot satisfy
    `effect_result_accompanies_the_fence`. `upgrade()` counts those before it adds
    anything and stops with a sentence naming the count and the remedy, rather than
    letting `ALTER TABLE … ADD CONSTRAINT` fail with a constraint name and half the
    revision applied.

    Driven by downgrading to 0012, writing the row 0012 permits, and upgrading
    again — which is the only honest way to produce a pre-0013 state.
    """
    from application.web.config import WebSettings
    from tests.web.p3_3_fixtures import clean_p3_3_tables, seed_job, seed_snapshot
    from tests.web.portal_fixtures import clean_p3_2_tables, seed_callers
    from tests.web_fixtures import web_environment

    settings = WebSettings.from_environment(web_environment(tmp_path))
    callers = seed_callers(migrated_database, settings, states=("C",))
    run_alembic(database_url, "downgrade", PREVIOUS)
    try:
        with migrated_database.begin() as connection:
            snapshot_id, checksum = seed_snapshot(connection)
            job_id = seed_job(
                connection,
                snapshot_id=snapshot_id,
                account_id=callers["C"].account_id,
                checksum=checksum,
                kind=JobKind.APPLY,
            )
            connection.execute(
                text(
                    "UPDATE reconciliation_jobs SET effect_committed_at = now() "
                    "WHERE id = :id"
                ),
                {"id": job_id},
            )

        with pytest.raises(subprocess.CalledProcessError) as refusal:
            run_alembic(database_url, "upgrade", "head")
        # Alembic runs as a deployment would, in a subprocess, so the refusal
        # reaches an operator on stderr — which is where it is read from here.
        message = refusal.value.stderr
        assert "publication payload" in message, message
        assert "TRUNCATE" in message, "and it names the remedy"

        with migrated_database.begin() as connection:
            assert not has_column(connection), (
                "the refusal happened before anything was added"
            )
    finally:
        with migrated_database.begin() as connection:
            clean_p3_3_tables(connection)
            clean_p3_2_tables(connection)
        run_alembic(database_url, "upgrade", "head")


def test_the_revision_is_the_head_and_descends_from_0012():
    """One linear chain, and this revision at the end of it."""
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    script = ScriptDirectory.from_config(Config("alembic.ini"))
    assert tuple(script.get_heads()) == (REVISION,)
    assert script.get_revision(REVISION).down_revision == PREVIOUS


def test_the_logical_schema_document_records_the_revision():
    """The controlled document and the migration cannot silently disagree.

    Schema §10 is the accepted contract for these tables; a column and two
    constraints that exist only in a revision file would be a schema change no
    reviewer meets.
    """
    document = (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "contracts"
        / "phase-3-logical-schema.md"
    ).read_text()
    assert "effect_result" in document
    assert "committed_effect_is_never_denied" in document
    assert "effect_result_accompanies_the_fence" in document
