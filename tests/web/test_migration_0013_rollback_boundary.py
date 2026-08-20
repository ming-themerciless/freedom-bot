"""Migration 0013's rollback boundary, proved against a database that has done work.

`tests/web/test_migration_0013_round_trip.py` rehearses `upgrade -> downgrade ->
upgrade` on a schema whose reconciliation tables are **empty**. That is real
evidence for exactly one claim — the revision's statements are structurally
reversible — and the 2026-08-18 independent review found it being read as a
second, much larger claim it does not support: that a database which has
processed a normal P3.3 apply can be rolled back and rolled forward again.

It cannot. The interleaving, which this module reproduces rather than describes:

1. at `0013`, an apply commits. `effect_committed_at` and `effect_result` are
   written by the fence **in the effect's own transaction**, and the immutable
   `snapshot_imports` receipt is written by the same transaction;
2. `alembic downgrade 0012` drops `effect_result` and deliberately keeps
   `effect_committed_at` — 0012's column is 0012's to remove;
3. `alembic upgrade 0013` runs `_refuse_rows_this_revision_cannot_describe()`,
   which counts every row with `effect_committed_at IS NOT NULL`;
4. every truthfully completed apply is in that count, because step 2 destroyed the
   payload `ck_..._effect_result_accompanies_the_fence` requires; and
5. the re-upgrade refuses. The database is stuck one revision below head, and the
   only remedies its message offered were remedies this platform forbids —
   deleting committed job history, or clearing the fence.

So the loss is not, as the submission claimed, merely "the ability to publish a
result for an effect that commits while the schema is down-level". **The downgrade
makes the database un-re-upgradeable.**

## The strategy this module holds the migration to

Stated in full in `docs/operations/web-portal.md` §"Migration 0013 rollback
boundary" and in the submission's §14 and §15; the predicate the guard enforces,
and the one every case below is written against, is:

> **Downgrade below 0013 is refused while any *retained* reconciliation job
> records a committed effect. It becomes available only when no such job exists;
> in normal operation that means either no apply has committed, or every
> completed committed-effect job and its result has been removed by the approved
> N-24 retention process and no committed-but-unpublished job remains.**

That is a statement about **rows that survive**, not about history. It admits
four database states, and this module exercises all four:

1. a database that never committed an effect — downgrade is available
   (`…succeeds_below_the_boundary_with_realistic_rows`);
2. a retained completed committed-effect job — refused
   (`…refuses_a_published_committed_effect`);
3. a retained committed-but-unpublished job — refused, and retention cannot
   remove it at any age (`…refuses_a_committed_but_unpublished_effect`,
   `…blocks_the_downgrade_at_any_age`); and
4. a database where approved N-24 retention removed every completed job and
   result while preserving `snapshot_imports` and the append-only audit history
   — available again (`…retention_reopens_the_boundary…`).

An earlier wording of this module said rollback was closed "past the first
apply". That was a claim about a historical event; the guard records no such
event and this schema holds none. It is superseded, and manual deletion,
truncation of production history, shortened retention and early retention are
**not** rollback techniques — see the runbook.

The refusal is the conservative half of the strategy and is implemented. The
half that changes the operational contract — that while such a job is retained,
rolling P3.3 back is application rollback/roll-forward rather than schema
downgrade — is documented as a **proposal awaiting Peter/Acceptance Authority
ratification** and is not self-approved here. Refusing to destroy a payload
nothing may truthfully reconstruct is correct under either policy, which is why
it is implemented now.

## What is asserted, and against what

Every case below drives the **production** Alembic revisions through the same
guarded subprocess helper the rest of the suite uses. Nothing is stubbed, no
schema is hand-approximated, and no case skips when `TEST_DATABASE_URL` is set —
which is the only configuration these are allowed to be read as evidence in.

| Case | Requirement |
|---|---|
| `…refuses_a_published_committed_effect` | a truthfully completed apply, with its receipt and its durable result, follows the strategy |
| `…refuses_a_committed_but_unpublished_effect` | …and so does an effect awaiting recovery, **without losing the ability to publish it** |
| `…names_both_populations_separately` | completed and committed-but-unpublished differ in the refusal, because they differ in what a downgrade would cost |
| `…succeeds_below_the_boundary_with_realistic_rows` | downgrade **is** supported while no retained job records a committed effect, with realistic rows, and re-upgrade restores them |
| `…leaves_history_untouched` | result, receipt and append-only audit rows are not updated, deleted or replaced — compared on `xmin` |
| `…an_interrupted_downgrade_…` / `…an_interrupted_upgrade_…` | a failed migration leaves the **complete** pre-migration schema and data, never a partial state |
| `…the_offline_script_carries_the_same_guard` | `--sql` mode never connects, so the guard is emitted as SQL that raises rather than as a comment nobody has to run |
| `…the_operations_document_records_the_boundary` | the controlled document and the migration cannot silently disagree |
| `…retention_reopens_the_boundary_and_the_round_trip_is_exact` | state 4: the predicate is retention-aware, driven through the production N-24 sweep |
| `…an_unpublished_effect_blocks_the_downgrade_at_any_age` | state 3: retention is not, and cannot become, a rollback bypass |
| `…a_downgrade_started_during_an_in_flight_effect_…` | the guard decides under a lock it took **before** its count, so an in-flight fence is counted rather than destroyed |
| `…a_fence_writer_starting_under_the_held_lock_…` | a writer that starts after the migration's lock is **granted** cannot commit until the migration transaction ends |
| `…a_fence_writer_arriving_behind_a_pending_lock_request_…` | *separately*: PostgreSQL lock-queue fairness — a later writer cannot overtake a still-pending conflicting request |

Metadata parity at head is `tests/test_database_postgresql.py::
test_migration_matches_table_metadata` (`alembic check`), which is unchanged and
still exact — this revision adds no metadata.
"""
from __future__ import annotations

import contextlib
import importlib.util
import os
import queue
import subprocess
import sys
import threading
import time
from datetime import timedelta
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.engine import make_url

from adapters.artifacts.filesystem import FilesystemArtifactStore, TrustedAncestors
from adapters.database.repositories import (
    SqlAlchemyReconciliationJobLeaseRepository,
)
from application.artifacts import ArtifactStorageError
from application.foundry.artifact import ingest_bytes
from application.web.jobs import JobKind, JobState
from application.worker.fence import PendingEffectResult
from application.worker.recovery import RECOVERED_KEY

from tests import foundry_fixtures as fx
from tests.conftest import resolve_test_database_url, run_alembic, start_alembic
from tools.job_retention import RetentionSweep
from tests.web.p3_3_fixtures import (
    clean_p3_3_tables,
    complete_preview,
    expire_lease,
    job_row,
    open_artifact_store,
    seed_import,
    seed_job,
    seed_snapshot,
    select_folder,
    snapshot_bytes,
    utcnow,
)
from tests.web.test_migration_0011_round_trip import history, schema_fingerprint
from tests.web.test_migration_0013_round_trip import (
    ACCOMPANIES,
    COLUMN,
    NEVER_DENIED,
    PRESERVED,
    has_column,
    has_constraint,
)

# The harness that produces a **real** committed effect: one web app and one
# worker over one database, driving the production apply path end to end. Imported
# rather than rebuilt, because a hand-seeded `effect_committed_at` would prove the
# rollback boundary against a row the platform never wrote.
from tests.web.test_p3_3_effect_recovery import (  # noqa: F401  — pytest fixtures
    artifact_root,
    callers,
    confirm,
    crash_after_the_effect,
    crashed_state,
    published,
    repository,
    runtime,
    snapshot,
    stored,
    worker_composition,
    worker_settings,
)

pytestmark = pytest.mark.database

PREVIOUS = "0012"
REVISION = "0013"

#: Comfortably past N-24's 30 days, matching `tests/web/test_p3_3_job_retention.py`.
RETENTION_AGE_DAYS = 45


def alembic_revision(connection) -> str:
    return connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()


def revision_objects_present(connection) -> tuple[bool, bool, bool]:
    """The three things `0013` adds, as one comparable value."""
    return (
        has_column(connection, COLUMN),
        has_constraint(connection, ACCOMPANIES),
        has_constraint(connection, NEVER_DENIED),
    )


def committed_effects(connection) -> tuple[int, int]:
    """`(published, unpublished)`, the two counts the refusal has to distinguish."""
    row = connection.execute(
        text(
            "SELECT count(*) FILTER (WHERE state = 'completed') AS published, "
            "count(*) FILTER (WHERE state <> 'completed') AS unpublished "
            "FROM reconciliation_jobs WHERE effect_committed_at IS NOT NULL"
        )
    ).one()
    return int(row[0]), int(row[1])


def durable_rows(connection) -> dict:
    """Every durable row a downgrade must not touch, each with its `xmin`.

    `xmin` is the transaction that last wrote the row, so a statement that
    rewrote a row to an identical value would still show here. Comparing rendered
    values alone would not.
    """
    return {
        "jobs": [
            tuple(row)
            for row in connection.execute(
                text(
                    "SELECT id, state, effect_committed_at, effect_result::text, "
                    "attempts, version, xmin::text FROM reconciliation_jobs ORDER BY id"
                )
            ).all()
        ],
        "results": [
            tuple(row)
            for row in connection.execute(
                text(
                    "SELECT id, job_id, summary::text, blocked_entries::text, "
                    "produced_at, xmin::text FROM reconciliation_job_results "
                    "ORDER BY id"
                )
            ).all()
        ],
        "imports": [
            tuple(row)
            for row in connection.execute(
                text(
                    "SELECT id, request_key, status, created_count, updated_count, "
                    "warning_count, summary::text, xmin::text FROM snapshot_imports "
                    "ORDER BY id"
                )
            ).all()
        ],
        "audit": history(connection),
    }


def durable_rows_without_effect_result(connection) -> dict:
    """`durable_rows` for a schema at `0012`, where `effect_result` does not exist."""
    rows = {
        "results": [
            tuple(row)
            for row in connection.execute(
                text(
                    "SELECT id, job_id, summary::text, blocked_entries::text, "
                    "produced_at, xmin::text FROM reconciliation_job_results "
                    "ORDER BY id"
                )
            ).all()
        ],
        "imports": [
            tuple(row)
            for row in connection.execute(
                text(
                    "SELECT id, request_key, status, created_count, updated_count, "
                    "warning_count, summary::text, xmin::text FROM snapshot_imports "
                    "ORDER BY id"
                )
            ).all()
        ],
        "audit": history(connection),
    }
    rows["jobs"] = [
        tuple(row)
        for row in connection.execute(
            text(
                "SELECT id, state, effect_committed_at, attempts, version, xmin::text "
                "FROM reconciliation_jobs ORDER BY id"
            )
        ).all()
    ]
    return rows


def second_snapshot(engine, stored, callers) -> tuple:
    """A second, genuinely different synthetic snapshot, stored and folder-selected.

    Different Actor bytes, therefore a different checksum, therefore a different
    `(snapshot_id, folder_id, profile_version)` input — which is what lets a second
    apply commit a second effect rather than being recognised as a duplicate of
    the first.
    """
    store, _checksum, _payload = stored
    payload = snapshot_bytes(
        actors=(fx.actor(fx.SECOND_ACTOR_ID, name="Second Testcharacter Brightlantern"),)
    )
    artifact = ingest_bytes(payload)
    store.store(artifact)
    with engine.begin() as connection:
        snapshot_id, checksum = seed_snapshot(connection, payload=payload)
        select_folder(
            connection, snapshot_id=snapshot_id, account_id=callers["A"].account_id
        )
    return snapshot_id, checksum


def refuse_downgrade(database_url) -> str:
    """Run the real `alembic downgrade 0012` and return the operator-facing text."""
    with pytest.raises(subprocess.CalledProcessError) as refusal:
        run_alembic(database_url, "downgrade", PREVIOUS)
    # Alembic runs as a deployment would, in a subprocess, so the refusal reaches
    # an operator on stderr — which is where it is read from here.
    return refusal.value.stderr


def assert_nothing_changed(engine, before: dict, fingerprint: dict) -> None:
    """The database is at `0013`, complete, and holding exactly the rows it held."""
    with engine.begin() as connection:
        assert revision_objects_present(connection) == (True, True, True), (
            "the refusal happened after a schema change"
        )
        assert has_column(connection, "effect_committed_at")
        assert has_constraint(connection, PRESERVED)
        assert alembic_revision(connection) == REVISION
        assert schema_fingerprint(connection) == fingerprint
        assert durable_rows(connection) == before


# ---------------------------------------------------------------------------
# Above the boundary: a database that has committed an effect
# ---------------------------------------------------------------------------


def test_the_downgrade_refuses_a_published_committed_effect(
    runtime, worker_composition, migrated_database, database_url, callers, snapshot
):
    """A truthfully completed apply is enough to close schema rollback.

    The whole of it, written by the production path: the import, the characters,
    the mappings, the applied audit event, the fence's `effect_committed_at` and
    `effect_result`, the durable `reconciliation_job_results` row and the
    completion event. Nothing here is seeded into a shape a real run cannot reach.

    The submission read this case as safe — "dropping `effect_result` loses no
    fact that is not also in `snapshot_imports`". It is not safe, and the reason
    is not the fact but the **constraint**: `0013` requires the payload back on
    re-upgrade, `snapshot_imports.summary` is a different bounded document
    (`issue_codes`, not `issue_counts`; no `would_create`, no `would_update`, no
    `selected_folder_path`, and no blocked-entry list at all), and nothing may
    invent the difference. A database downgraded here could never return to head.
    """
    _preview_id, apply_id = confirm(migrated_database, runtime, callers, snapshot)
    assert runtime.tick().outcome == "completed"

    with migrated_database.begin() as connection:
        job = job_row(connection, apply_id)
        assert job["state"] == JobState.COMPLETED.value
        assert job["effect_committed_at"] is not None
        assert job["effect_result"] is not None
        assert job["result_id"] is not None
        assert committed_effects(connection) == (1, 0)
        before = durable_rows(connection)
        fingerprint = schema_fingerprint(connection)

    message = refuse_downgrade(database_url)

    assert "committed import effect" in message, message
    assert "1 completed" in message, message
    assert "0 committed but unpublished" in message, message
    # The remedy an operator can actually act on, rather than a constraint name.
    assert "roll forward" in message.lower(), message
    assert_nothing_changed(migrated_database, before, fingerprint)


def test_the_downgrade_refuses_a_committed_but_unpublished_effect(
    runtime, worker_composition, migrated_database, database_url, callers, snapshot
):
    """The effect awaiting recovery, and the publication that must survive intact.

    This is the population the downgrade would have hurt worst and the one the
    submission's own words admitted it hurt: dropping `effect_result` destroys the
    only durable record of what the publication owes, and the recovery path is
    then unable to publish anything truthful — there is no other row holding the
    bounded summary and the blocked-entry list this run produced.

    So the refusal is asserted **and** the consequence of it: after the refused
    downgrade, `WorkerRuntime.recover()` still publishes exactly the result it
    would have published had no operator ever tried.
    """
    _preview_id, apply_id = confirm(migrated_database, runtime, callers, snapshot)
    crash_after_the_effect(migrated_database, worker_composition, apply_id)
    crashed_state(migrated_database, apply_id, attempts=1)

    with migrated_database.begin() as connection:
        assert committed_effects(connection) == (0, 1)
        stored_payload = job_row(connection, apply_id)["effect_result"]
        before = durable_rows(connection)
        fingerprint = schema_fingerprint(connection)

    message = refuse_downgrade(database_url)

    assert "0 completed" in message, message
    assert "1 committed but unpublished" in message, message
    assert "publish" in message.lower(), message
    assert_nothing_changed(migrated_database, before, fingerprint)

    # And the ability the refusal exists to protect is still there.
    with migrated_database.begin() as connection:
        expire_lease(connection, apply_id)
    assert list(runtime.recover()) == [apply_id]
    assert published(migrated_database, apply_id) == {"results": 1, "completions": 1}

    with migrated_database.begin() as connection:
        result = (
            connection.execute(
                text(
                    "SELECT summary, blocked_entries FROM reconciliation_job_results "
                    "WHERE job_id = :id"
                ),
                {"id": apply_id},
            )
            .mappings()
            .one()
        )
    assert result["summary"][RECOVERED_KEY] is True
    for key, value in stored_payload["summary"].items():
        assert result["summary"][key] == value, key
    assert result["blocked_entries"] == stored_payload["blocked_entries"]


def test_the_refusal_names_both_populations_separately(
    runtime,
    worker_composition,
    migrated_database,
    database_url,
    callers,
    snapshot,
    stored,
):
    """Completed and committed-but-unpublished are counted apart, because they cost apart.

    A completed job loses the ability to **return to head**. An unpublished one
    loses that *and* the ability to be published at all. An operator deciding what
    to do next needs to know which they have, and a single total would not say.
    """
    _preview_id, published_apply = confirm(
        migrated_database, runtime, callers, snapshot
    )
    assert runtime.tick().outcome == "completed"

    # A **second snapshot**, not a second apply of the first: `uq_snapshot_imports_
    # applied_input` makes a repeat of one input a duplicate that returns the
    # existing receipt before the fence is ever reached, so it would produce no
    # second committed effect to count.
    second = second_snapshot(migrated_database, stored, callers)
    _preview_id_2, unpublished_apply = confirm(
        migrated_database, runtime, callers, second
    )
    crash_after_the_effect(
        migrated_database, worker_composition, unpublished_apply, owner="crashing:bbbb"
    )

    with migrated_database.begin() as connection:
        assert committed_effects(connection) == (1, 1)
        before = durable_rows(connection)
        fingerprint = schema_fingerprint(connection)

    message = refuse_downgrade(database_url)

    assert "1 completed" in message, message
    assert "1 committed but unpublished" in message, message
    assert str(published_apply) not in message, "counts, never a row dump"
    assert str(unpublished_apply) not in message, "counts, never a row dump"
    assert_nothing_changed(migrated_database, before, fingerprint)


def test_the_refusal_leaves_history_untouched_and_the_database_usable(
    runtime, worker_composition, migrated_database, database_url, callers, snapshot
):
    """`xmin` on every durable row, and a write afterwards to prove it still works.

    "Left unchanged" is asserted the strong way — the transaction id that last
    wrote each row — because a guard that ran an `UPDATE ... SET x = x` before
    refusing would pass a value comparison. "Still usable" is asserted by doing
    the thing a refused-but-healthy database must still be able to do: publish the
    effect it is holding.
    """
    _preview_id, apply_id = confirm(migrated_database, runtime, callers, snapshot)
    crash_after_the_effect(migrated_database, worker_composition, apply_id)

    with migrated_database.begin() as connection:
        before = durable_rows(connection)
        fingerprint = schema_fingerprint(connection)
    assert before["imports"], "the immutable receipt exists to be compared"
    assert before["audit"], "and so does the append-only history"

    refuse_downgrade(database_url)
    assert_nothing_changed(migrated_database, before, fingerprint)

    with migrated_database.begin() as connection:
        expire_lease(connection, apply_id)
    assert list(runtime.recover()) == [apply_id], "the database is still usable"


# ---------------------------------------------------------------------------
# Below the boundary: a database that has not committed an effect
# ---------------------------------------------------------------------------


def test_the_downgrade_and_re_upgrade_succeed_below_the_boundary_with_realistic_rows(
    migrated_database, database_url, callers, snapshot
):
    """State 1: rows are not the boundary; a *retained committed effect* is.

    A database that has run previews, refused an apply, recorded an import
    receipt and written audit history — but retains no job recording a committed
    import effect — is still genuinely reversible, and this asserts it with those
    rows present rather than on an empty schema. `upgrade -> downgrade -> upgrade`
    restores the identical catalogue and leaves every durable row exactly as it
    was, `xmin` included.
    """
    snapshot_id, checksum = snapshot
    account_id = callers["C"].account_id
    with migrated_database.begin() as connection:
        for index in range(2):
            connection.execute(
                text(
                    "INSERT INTO audit_events (id, actor_capability, action, "
                    "entity_type, entity_id, source, correlation_id, payload) "
                    "VALUES (:id, 'system', :action, 'probe', :entity, 'system', "
                    ":correlation, '{}'::jsonb)"
                ),
                {
                    "id": uuid4(),
                    "action": f"probe.below_the_0013_boundary.{index}",
                    "entity": str(index),
                    "correlation": uuid4(),
                },
            )
        complete_preview(
            connection,
            snapshot_id=snapshot_id,
            account_id=account_id,
            checksum=checksum,
        )
        seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=account_id,
            checksum=checksum,
            kind=JobKind.APPLY,
            state=JobState.FAILED,
            failure_code="artifact_unreadable",
        )
        seed_import(
            connection,
            snapshot_id=snapshot_id,
            account_id=account_id,
            checksum=checksum,
            status="refused",
        )
        assert committed_effects(connection) == (0, 0)
        at_head = schema_fingerprint(connection)
        before = durable_rows(connection)
        before_at_previous = durable_rows_without_effect_result(connection)

    run_alembic(database_url, "downgrade", PREVIOUS)
    try:
        with migrated_database.begin() as connection:
            assert revision_objects_present(connection) == (False, False, False)
            assert has_column(connection, "effect_committed_at"), "0012's, not 0013's"
            assert has_constraint(connection, PRESERVED)
            assert durable_rows_without_effect_result(connection) == before_at_previous
    finally:
        run_alembic(database_url, "upgrade", "head")

    with migrated_database.begin() as connection:
        assert schema_fingerprint(connection) == at_head
        assert revision_objects_present(connection) == (True, True, True)
        assert durable_rows(connection) == before, (
            "the round trip rewrote a durable row"
        )


# ---------------------------------------------------------------------------
# Atomicity: a failed migration leaves no partial state
# ---------------------------------------------------------------------------


def test_an_interrupted_downgrade_leaves_the_complete_pre_migration_schema(
    migrated_database, database_url, callers, snapshot
):
    """A downgrade that fails part-way leaves `0013` whole, not half-removed.

    Alembic runs the whole `downgrade` inside one transaction (`migrations/env.py`
    wraps `run_migrations()` in `context.begin_transaction()`), and PostgreSQL's
    DDL is transactional — so this is asserted rather than assumed. The failure is
    injected where it can only be caused by the revision's **own** statements: the
    second constraint it drops is removed first, so `downgrade()` succeeds in
    dropping `committed_effect_is_never_denied` and then fails.

    If the transaction were not doing its job, that first drop would survive the
    failure and the database would be at `0013` with one of its two constraints
    missing — a partial state no `alembic` command could name or repair.
    """
    with migrated_database.begin() as connection:
        assert committed_effects(connection) == (0, 0), "the guard must not fire here"
        fingerprint = schema_fingerprint(connection)
        connection.execute(
            text(f"ALTER TABLE reconciliation_jobs DROP CONSTRAINT {ACCOMPANIES}")
        )
    try:
        with pytest.raises(subprocess.CalledProcessError) as failure:
            run_alembic(database_url, "downgrade", PREVIOUS)
        assert ACCOMPANIES in failure.value.stderr, failure.value.stderr

        with migrated_database.begin() as connection:
            assert has_constraint(connection, NEVER_DENIED), (
                "the first drop survived a failed transaction"
            )
            assert has_column(connection, COLUMN)
            assert alembic_revision(connection) == REVISION
    finally:
        with migrated_database.begin() as connection:
            connection.execute(
                text(
                    f"ALTER TABLE reconciliation_jobs ADD CONSTRAINT {ACCOMPANIES} "
                    "CHECK ((effect_committed_at IS NULL) = (effect_result IS NULL))"
                )
            )

    with migrated_database.begin() as connection:
        assert schema_fingerprint(connection) == fingerprint, (
            "the injected failure was not fully undone"
        )


def test_an_interrupted_upgrade_leaves_the_complete_pre_migration_schema_and_rows(
    migrated_database, database_url, callers, snapshot, tmp_path
):
    """The re-upgrade guard's other branch, and the same atomicity from below.

    A `0012` database holding a job that both carries a committed effect **and**
    sits in a state denying it is a row this revision's second constraint forbids.
    `upgrade()` counts it before it adds anything and refuses; the column is not
    added, the version stays at `0012`, and the row is left exactly as it was for
    the operator to resolve.
    """
    snapshot_id, checksum = snapshot
    run_alembic(database_url, "downgrade", PREVIOUS)
    try:
        with migrated_database.begin() as connection:
            job_id = seed_job(
                connection,
                snapshot_id=snapshot_id,
                account_id=callers["C"].account_id,
                checksum=checksum,
                kind=JobKind.APPLY,
                state=JobState.FAILED,
                failure_code="attempts_exhausted",
            )
            connection.execute(
                text(
                    "UPDATE reconciliation_jobs SET effect_committed_at = now() "
                    "WHERE id = :id"
                ),
                {"id": job_id},
            )
            before = durable_rows_without_effect_result(connection)

        with pytest.raises(subprocess.CalledProcessError) as refusal:
            run_alembic(database_url, "upgrade", "head")
        assert "denies a committed import effect" in refusal.value.stderr

        with migrated_database.begin() as connection:
            assert not has_column(connection, COLUMN), "nothing was added"
            assert not has_constraint(connection, ACCOMPANIES)
            assert not has_constraint(connection, NEVER_DENIED)
            assert alembic_revision(connection) == PREVIOUS
            assert durable_rows_without_effect_result(connection) == before
    finally:
        with migrated_database.begin() as connection:
            clean_p3_3_tables(connection)
        run_alembic(database_url, "upgrade", "head")


# ---------------------------------------------------------------------------
# Offline mode, and the controlled document
# ---------------------------------------------------------------------------


def test_the_offline_downgrade_script_carries_the_same_guard(database_url):
    """`--sql` never connects, so a comment would be the only protection there is.

    The upgrade can afford a comment: its two `ADD CONSTRAINT` statements validate
    every existing row, so an offline upgrade of a database this revision cannot
    describe fails on its own. **The downgrade has no such backstop** — `DROP
    CONSTRAINT` and `DROP COLUMN` succeed against any data at all — so the guard
    is emitted as SQL that raises, and an operator who runs the generated script
    gets the same refusal an online downgrade would have given them.
    """
    script = run_alembic(database_url, "downgrade", f"{REVISION}:{PREVIOUS}", "--sql")

    assert "RAISE EXCEPTION" in script.stdout, script.stdout
    assert "effect_committed_at IS NOT NULL" in script.stdout
    assert "committed import effect" in script.stdout
    # And it is emitted *before* the statements it protects.
    assert script.stdout.index("RAISE EXCEPTION") < script.stdout.index("DROP COLUMN")


def test_the_operations_document_records_the_rollback_boundary():
    """The controlled document and the migration cannot silently disagree.

    `docs/operations/web-portal.md` is what an operator reads at 03:00; a rollback
    boundary that existed only in a revision file would be a boundary nobody meets
    until the refusal surprises them.
    """
    document = (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "operations"
        / "web-portal.md"
    ).read_text()
    assert "Migration 0013 rollback boundary" in document
    assert "effect_result" in document
    assert "roll-forward" in document


# ---------------------------------------------------------------------------
# Concurrency: the guard decides under a lock (2026-08-18 second remediation)
# ---------------------------------------------------------------------------
#
# The independent re-review's blocking finding: the guard counted under an
# ordinary MVCC snapshot and only then let the first `ALTER TABLE` queue for its
# DDL lock, so a worker that committed its fence in that window was counted by
# nobody and had its publication payload dropped. These cases drive the real
# Alembic revision against real PostgreSQL and observe the real lock.
#
# **No sleeping is used as proof.** Every wait is a bounded poll of `pg_locks`
# and `pg_stat_activity` for a named, granted-or-not lock, and a poll that times
# out fails with what it last saw rather than passing by luck.

LOCK_WAIT_SECONDS = 60.0
POLL_SECONDS = 0.05

#: Ceilings for **failure-path cleanup**, deliberately far below
#: `LOCK_WAIT_SECONDS`. Cleanup runs when a case has already failed, so it must be
#: short as well as bounded: a release that took the 60-second production-test
#: ceiling would be bounded and still useless. Added by the 2026-08-19 fifth
#: correction for the finding that a surviving migration child was collected with
#: an unbounded `communicate()`.
CLEANUP_REAP_SECONDS = 5.0
CLEANUP_JOIN_SECONDS = 15.0

#: Per **database** cleanup call — the holder's `rollback()` and its `close()`.
#: Added by the 2026-08-19 **sixth** correction, for the finding that the fifth
#: correction's ceiling counted only the subprocess reap and the writer join while
#: `release()` also made two synchronous SQLAlchemy calls that nothing bounded. A
#: `rollback()` that never returns is not made bounded by catching its exception,
#: and it kept every later step from running at all.
CLEANUP_DATABASE_SECONDS = 5.0

#: The independent, server-side disposal of last resort: when a bounded database
#: call did **not** return, the connection object belongs to a thread that may
#: still be inside it, so it is never touched again from here. What is disposed of
#: instead is the *backend* — from a different connection — which is what actually
#: releases the `alembic_version` row lock into the shared disposable database.
CLEANUP_DISPOSE_SECONDS = 5.0

#: How long PostgreSQL is given to finish tearing down a killed backend before the
#: bounded-cleanup regression calls the residue a leak. Catalog visibility, not a
#: race the cleanup itself has to win.
CLEANUP_SETTLE_SECONDS = 15.0

#: The guard's own statement, read from the revision file rather than retyped, so
#: a test cannot pass against a lock the migration does not actually take.
_REVISION_SPEC = importlib.util.spec_from_file_location(
    "p3_3_revision_0013_under_test",
    Path(__file__).resolve().parents[2]
    / "migrations"
    / "versions"
    / "0013_effect_publication_recovery.py",
)
_REVISION = importlib.util.module_from_spec(_REVISION_SPEC)
_REVISION_SPEC.loader.exec_module(_REVISION)
DOWNGRADE_LOCK = _REVISION.DOWNGRADE_LOCK

#: What the fence makes durable with the effect. Bounded, synthetic, and no real
#: player, Actor, guild or credential value anywhere.
FENCE_PAYLOAD = PendingEffectResult(
    summary={"actors": 1, "would_create": 1, "would_update": 0, "issue_counts": []},
    blocked_entries=[],
).payload()


def _await(probe, *, what: str, seconds: float = LOCK_WAIT_SECONDS):
    """Poll `probe` until it returns something truthy, or fail with what it saw.

    Bounded, and the bound is the failure: a concurrency case that waited
    forever would hang the suite, and one that slept a fixed interval and then
    asserted would be asserting about the scheduler.
    """
    deadline = time.monotonic() + seconds
    last = None
    while time.monotonic() < deadline:
        last = probe()
        if last:
            return last
        time.sleep(POLL_SECONDS)
    raise AssertionError(
        f"timed out after {seconds:.0f}s waiting for {what}; last saw {last!r}"
    )


def _ungranted(engine, mode: str):
    """**Any** session whose request for `mode` on `reconciliation_jobs` is queued.

    Reads only `pg_locks`, `pg_stat_activity` and `pg_class` — never the job
    table itself, which is important: while an `ACCESS EXCLUSIVE` request is
    pending, a `SELECT` on that table would queue behind it and the probe would
    deadlock against the thing it is observing.

    **Deliberately broad, and only usable for claims that are broad.** It is
    scoped to the relation and the lock mode, and to nothing else: it proves
    *that someone is queued*, which is precisely the condition
    `…arriving_behind_a_pending_lock_request_…` exists to observe, because there
    the ordering — not the identity — is the property. It cannot prove that a
    particular writer is queued, and the 2026-08-19 fourth correction records the
    finding that TC-MIG-37 was reading it as though it could. Any case that must
    bind a queued request to a known backend and transaction uses
    `_the_writers_queued_fence()` below instead.
    """

    def probe():
        with engine.connect() as connection:
            return [
                dict(row)
                for row in connection.execute(
                    text(
                        "SELECT a.pid, a.query, a.wait_event_type FROM pg_locks l "
                        "JOIN pg_stat_activity a ON a.pid = l.pid "
                        "WHERE l.locktype = 'relation' "
                        "AND l.relation = 'reconciliation_jobs'::regclass "
                        "AND l.mode = :mode AND NOT l.granted"
                    ),
                    {"mode": mode},
                )
                .mappings()
                .all()
            ]

    return probe


def _reap(process, *, seconds: float = LOCK_WAIT_SECONDS):
    """Always collect the child, so no test can leave a lock holder behind.

    The **success**-path reap: it returns what the child said, and a child that
    outlives `seconds` is a failure of the case rather than something to report
    and continue past.

    Both waits are bounded. The second one — the collection that follows the
    kill — was itself an unbounded `communicate()` until the 2026-08-19 fifth
    correction; a `kill()` whose pipe collection stalls is exactly the hang that
    correction's finding was about, and it is no more acceptable here than on the
    failure path.
    """
    try:
        stdout, stderr = process.communicate(timeout=seconds)
    except subprocess.TimeoutExpired:
        process.kill()
        try:
            stdout, stderr = process.communicate(timeout=CLEANUP_REAP_SECONDS)
        except subprocess.TimeoutExpired:
            raise AssertionError(
                "the migration process never finished, and did not die within "
                f"{CLEANUP_REAP_SECONDS:.0f}s of SIGKILL either"
            ) from None
        raise AssertionError("the migration process never finished") from None
    return process.returncode, stdout, stderr


def _bounded_reap(process, *, seconds: float = CLEANUP_REAP_SECONDS) -> str | None:
    """The **failure**-path reap: end and collect `process` within `2 * seconds`.

    Added by the 2026-08-19 fifth correction. The shape it replaces was

    ```python
    if migration is not None and migration.poll() is None:
        migration.kill()
        migration.communicate()      # <- no timeout: an unbounded wait in `finally`
    ```

    which could stall before the rest of the cleanup ran at all — before the
    `alembic_version` row lock was rolled back, before the holder was closed and
    before the writer was joined.

    Differences from `_reap()`, both deliberate:

    * it **never raises**. It returns `None` when the child was collected, or a
      description of what was left behind. Cleanup runs while an assertion is
      already failing, and a cleanup helper that raises there would replace the
      failure under diagnosis with a report about the cleanup; and
    * it never waits without a bound, including after the kill. A child that
      survives both bounded collections is reported and stepped over, so one
      stuck process cannot strand the connection, transaction and thread the
      caller still has to release.

    `kill()` rather than `terminate()`, and that is a safety property, not a
    style choice: `SIGKILL` cannot run a signal handler, so a migration ended
    this way provably cannot issue the `COMMIT` that would make its drops
    durable. `SIGTERM` gives the child the opportunity, however unlikely, to run
    one. Ending the child also releases its locks, which is what unblocks a
    writer still queued behind the migration's table lock.
    """
    if process is None:
        return None
    name = f"child pid {getattr(process, 'pid', '?')}"
    for _attempt in (1, 2):
        try:
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=seconds)
        except subprocess.TimeoutExpired:
            continue
        except Exception as error:  # pragma: no cover - reported, never raised
            return f"collecting the migration {name} raised {error!r}"
        return None
    return (
        f"the migration {name} was neither killed nor collected within "
        f"{2 * seconds:.0f}s; its locks and connection may survive this test"
    )


def _bounded_call(what: str, action, *, seconds: float):
    """Run one cleanup call on a thread of its own and wait for it, **bounded**.

    Added by the 2026-08-19 **sixth** correction. `_bounded_reap()` above bounds a
    subprocess because `subprocess` offers a timeout; SQLAlchemy's `rollback()` and
    `close()` offer none, and neither does psycopg once it is inside a synchronous
    round trip. Catching an exception does not bound an operation that never
    returns — it only describes one that ended — so the call is moved off the
    calling thread and it is the *wait* that is bounded, which is the only part
    this test can actually control.

    Returns `(problem, orphan)`:

    * `problem` is `None` when the call returned and reported nothing, or a
      description when it raised, timed out, or returned a description of its own;
      and
    * `orphan` is the still-running thread when the bound expired, and `None`
      otherwise. It is **returned rather than hidden**: the caller records it, the
      release reports it, and no later step touches the object that thread owns.

    The owner thread is a **daemon**, so a call that never returns cannot keep the
    interpreter — or the pytest process — alive at the end of the session. That is
    a deliberate trade and it is the reason an orphan is always reported: a daemon
    thread nobody named would be exactly the "declare success while the thread and
    its database resources may still be alive" this correction exists to avoid.
    """
    outcome: dict = {}

    def run() -> None:
        try:
            outcome["value"] = action()
        except BaseException as error:  # noqa: BLE001 - reported, never raised
            outcome["error"] = repr(error)

    owner = threading.Thread(target=run, name=f"held-lock cleanup: {what}", daemon=True)
    owner.start()
    owner.join(timeout=seconds)
    if owner.is_alive():
        return (
            f"{what} did not return within {seconds:.0f}s; the thread that owns "
            f"that call ({owner.name!r}) is still running and still owns what it "
            "was called on, so nothing else here touches it",
            owner,
        )
    if "error" in outcome:
        return (f"{what} raised {outcome['error']}", None)
    value = outcome.get("value")
    return (value if value else None, None)


def _backend_identity(connection) -> dict:
    """The backend `connection` is speaking to, named so it can never be confused.

    `backend_start` is read beside the pid deliberately: PostgreSQL reuses process
    ids, and a disposal that named a pid alone could terminate an innocent backend
    that inherited it. Both together identify one backend and only one.
    """
    return dict(
        connection.execute(
            text(
                "SELECT pg_backend_pid() AS pid, "
                "(SELECT backend_start FROM pg_stat_activity "
                "   WHERE pid = pg_backend_pid()) AS backend_start"
            )
        )
        .mappings()
        .one()
    )


def _backend_disposal(engine, *, pid: int, backend_start):
    """The independent disposal: end the holder's **backend**, not its connection.

    Added by the 2026-08-19 sixth correction for requirement 2 — a blocked
    `rollback()` must not prevent an independent close/disposal attempt. It cannot
    be a second `close()` on the same connection: another thread may still be
    inside it, and closing it from here would either race that thread or, worse,
    hand a connection it is still using back to the pool. So the disposal is aimed
    at the resource that actually matters to the next case in a **shared**
    disposable database — the server-side backend, and with it the
    `alembic_version` row lock it holds — and it is issued from a *different*
    connection, which is why a stuck one cannot prevent it.

    The disposal connection is itself detached from the pool before it is used, so
    that if this call is the one that blocks, the thread left owning it owns
    nothing the pool can hand to anybody else.

    Returns `None` when there was nothing left to dispose of, and a description
    when there was — needing this disposal at all means the client-side release
    did not complete, and that is reported rather than quietly accepted.
    """

    def dispose() -> str | None:
        connection = engine.connect()
        connection.detach()
        try:
            terminated = (
                connection.execute(
                    text(
                        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                        "WHERE pid = :pid AND backend_start = :backend_start"
                    ),
                    {"pid": pid, "backend_start": backend_start},
                )
                .scalars()
                .all()
            )
        finally:
            connection.close()
        if not terminated:
            return None
        return (
            f"the holder's backend {pid} was still live after its bounded rollback "
            f"and close, and was terminated ({terminated!r}) so the alembic_version "
            "row lock it held could not survive into the next case"
        )

    return dispose


@pytest.fixture()
def head_restored(migrated_database, database_url):
    """Return the disposable database to head however the case ended.

    A concurrency case that fails part-way can leave the schema at `0012` —
    including, against the pre-fix revision, at `0012` holding a stranded
    committed effect that `upgrade 0013` refuses. The remedy the refusal names
    for a disposable database is applied here, and only here.
    """
    yield
    with migrated_database.begin() as connection:
        if (
            connection.execute(
                text("SELECT to_regclass('public.reconciliation_jobs')")
            ).scalar_one()
            is not None
        ):
            clean_p3_3_tables(connection)
    run_alembic(database_url, "upgrade", "head")


def _in_flight_fence(migrated_database, callers, snapshot, apply_id, *, owner):
    """A real worker/effect transaction, held open immediately before its commit.

    The production claim, the production `snapshot_imports` receipt and the
    production commit fence — `hold_for_effect`, the same statement
    `JobLeaseFence` issues — in one transaction this test controls the boundary
    of. The executor is not used because it commits its own unit of work, and
    what has to exist here is the interval *before* that commit; adding a pause
    hook to production code to reach it was refused (see the handover's
    prohibition on a production pause hook).

    Returns `(connection, transaction)`; the caller owns both.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        claimed = repository(connection).claim(owner=owner, now=utcnow())
    assert claimed is not None and claimed["id"] == apply_id

    holder = migrated_database.connect()
    transaction = holder.begin()
    seed_import(
        holder,
        snapshot_id=snapshot_id,
        account_id=callers["C"].account_id,
        checksum=checksum,
        # The receipt the recovery reads by the job's own `request_key`, so the
        # publication this case proves is still possible is a real one.
        request_key=claimed["request_key"],
    )
    held = SqlAlchemyReconciliationJobLeaseRepository(holder).hold_for_effect(
        job_id=apply_id, owner=owner, now=utcnow(), result=FENCE_PAYLOAD
    )
    assert held is True, "the production fence took the row, and has not committed"
    return holder, transaction


def test_a_downgrade_started_during_an_in_flight_effect_refuses_after_it_commits(
    runtime,
    worker_composition,
    migrated_database,
    database_url,
    callers,
    snapshot,
    head_restored,
):
    """The blocking finding's interleaving, driven end to end and now excluded.

    1. a worker transaction is applying an import and has **not** committed its
       fence;
    2. the real `alembic downgrade 0012` starts;
    3. it is observed waiting — at the guard's own `LOCK TABLE … ACCESS
       EXCLUSIVE`, proved from `pg_stat_activity.query`, not at a later `ALTER
       TABLE` and not at nothing;
    4. the worker commits `effect_committed_at` and `effect_result`;
    5. the migration is granted the lock, counts the **now committed** row, and
       refuses before any drop; and
    6. revision, schema, payload, receipt, audit history and the ability to
       publish the effect are all intact.

    **Against the pre-fix revision this case fails at step 3**: the only
    ungranted `ACCESS EXCLUSIVE` request is `ALTER TABLE reconciliation_jobs DROP
    CONSTRAINT …`, which is the old unsafe interleaving itself — the count has
    already run and seen zero, and the drop is merely queued behind the worker.
    The assertion message says so, and the recorded pre-fix run shows the
    downgrade going on to succeed and remove `effect_result`.
    """
    _preview_id, apply_id = confirm(migrated_database, runtime, callers, snapshot)
    holder, transaction = _in_flight_fence(
        migrated_database, callers, snapshot, apply_id, owner="worker:inflight"
    )
    migration = start_alembic(database_url, "downgrade", PREVIOUS)
    try:
        waiting = _await(
            _ungranted(migrated_database, "AccessExclusiveLock"),
            what="the downgrade to queue for its table lock",
        )
        blocked = " ".join(waiting[0]["query"].split())
        wait_event = waiting[0]["wait_event_type"]
        assert migration.poll() is None, "the migration exited before it waited"
        transaction.commit()
        returncode, _stdout, stderr = _reap(migration)
    finally:
        if transaction.is_active:
            transaction.rollback()
        holder.close()
        # Bounded, like every other reap in this module since the 2026-08-19
        # fifth correction: a `kill()` followed by an unbounded `communicate()`
        # can stall cleanup indefinitely.
        left_behind = _bounded_reap(migration)

    assert left_behind is None, left_behind
    assert wait_event == "Lock", wait_event
    assert DOWNGRADE_LOCK in blocked, (
        "the migration was not waiting at the guard's lock but at "
        f"{blocked!r} — which is the pre-fix interleaving: the count has already "
        "run under its own snapshot and only the DDL is queued behind the worker"
    )
    assert returncode != 0, "the downgrade did not refuse"
    assert "retained reconciliation job(s) record a committed import effect" in stderr
    assert "0 completed" in stderr and "1 committed but unpublished" in stderr

    with migrated_database.begin() as connection:
        assert alembic_revision(connection) == REVISION
        assert revision_objects_present(connection) == (True, True, True)
        assert committed_effects(connection) == (0, 1)
        assert job_row(connection, apply_id)["effect_result"] == FENCE_PAYLOAD
        assert (
            connection.execute(
                text("SELECT count(*) FROM snapshot_imports")
            ).scalar_one()
            == 1
        )
        expire_lease(connection, apply_id)

    # The capability the refusal exists to protect, exercised rather than claimed.
    assert list(runtime.recover()) == [apply_id]
    assert published(migrated_database, apply_id) == {"results": 1, "completions": 1}


def test_a_fence_writer_arriving_behind_a_pending_lock_request_cannot_overtake_it(
    runtime,
    worker_composition,
    migrated_database,
    database_url,
    callers,
    snapshot,
    stored,
    head_restored,
):
    """**Lock-queue fairness only** — named for what it proves, not for more.

    Renamed and re-scoped by the 2026-08-19 third correction. Under its previous
    name it was offered as proof that a writer starting after the migration
    *holds* its lock cannot commit until the migration finishes. It is not that,
    and cannot be: throughout this case the migration's `ACCESS EXCLUSIVE`
    request is **ungranted**. The condition it does establish is the sibling one,
    which is worth keeping because the guard depends on both:

    > While the migration's conflicting lock request is still queued, a *later*
    > writer cannot overtake it. PostgreSQL puts a new conflicting requester
    > behind the existing waiter rather than granting it ahead.

    The held-lock condition is proved separately, and by observing a **granted**
    lock, in `…a_fence_writer_starting_under_the_held_lock_…` below.

    The arrangement: an ordinary reader holds `ACCESS SHARE`, so the migration's
    `LOCK TABLE` is granted nothing and queues; a fence writer arriving
    afterwards conflicts with that *pending* request and queues behind it.
    Releasing the reader lets the migration run to its refusal, and only then
    does the writer proceed.

    What is asserted is exactly that ordering: the writer's own statement is
    still an ungranted `ROW EXCLUSIVE` request in `pg_locks` while the
    migration's request is ahead of it in the queue, and the migration's refusal
    counts **one** committed-but-unpublished effect — the pre-existing one, never
    the writer's. No claim is made here about a lock the migration was granted.
    """
    _preview_id, blocking_apply = confirm(migrated_database, runtime, callers, snapshot)
    crash_after_the_effect(migrated_database, worker_composition, blocking_apply)

    second = second_snapshot(migrated_database, stored, callers)
    _preview_id_2, late_apply = confirm(migrated_database, runtime, callers, second)
    with migrated_database.begin() as connection:
        claimed = repository(connection).claim(owner="worker:late", now=utcnow())
    assert claimed is not None and claimed["id"] == late_apply

    reader = migrated_database.connect()
    reader_transaction = reader.begin()
    reader.execute(text("SELECT count(*) FROM reconciliation_jobs")).scalar_one()

    writer_outcome: dict = {}

    def write_the_fence():
        connection = migrated_database.connect()
        try:
            with connection.begin():
                writer_outcome["held"] = SqlAlchemyReconciliationJobLeaseRepository(
                    connection
                ).hold_for_effect(
                    job_id=late_apply,
                    owner="worker:late",
                    now=utcnow(),
                    result=FENCE_PAYLOAD,
                )
        except BaseException as error:  # pragma: no cover - reported by assertion
            writer_outcome["error"] = repr(error)
        finally:
            connection.close()

    writer = threading.Thread(target=write_the_fence, daemon=True)
    migration = start_alembic(database_url, "downgrade", PREVIOUS)
    try:
        _await(
            _ungranted(migrated_database, "AccessExclusiveLock"),
            what="the downgrade to queue behind the reader",
        )
        writer.start()
        queued = _await(
            _ungranted(migrated_database, "RowExclusiveLock"),
            what="the fence writer to queue behind the migration's lock request",
        )
        assert writer.is_alive(), "the writer committed while the migration waited"
        assert writer_outcome == {}, writer_outcome
        reader_transaction.rollback()
        returncode, _stdout, stderr = _reap(migration)
    finally:
        if reader_transaction.is_active:
            reader_transaction.rollback()
        reader.close()
        # Bounded (2026-08-19 fifth correction), and before the writer is joined,
        # so ending the migration releases the lock the writer may still be
        # queued behind.
        left_behind = _bounded_reap(migration)
        # `is_alive()` rather than an unconditional join: an assertion that fails
        # before `writer.start()` would otherwise raise `cannot join thread
        # before it is started` from the cleanup and hide the real failure.
        if writer.is_alive():
            writer.join(timeout=LOCK_WAIT_SECONDS)

    assert left_behind is None, left_behind
    assert queued, "the writer never queued, so nothing about ordering was proved"
    assert returncode != 0
    assert "1 committed but unpublished" in stderr, (
        "the migration counted the late writer's fence, so the writer was not "
        "excluded after all"
    )
    assert not writer.is_alive(), "the writer never finished"
    assert writer_outcome.get("held") is True, writer_outcome

    with migrated_database.begin() as connection:
        assert alembic_revision(connection) == REVISION
        assert committed_effects(connection) == (0, 2), (
            "the late fence committed only after the migration released the lock"
        )


# ---------------------------------------------------------------------------
# Concurrency: a writer that starts while the migration **holds** its lock
# ---------------------------------------------------------------------------
#
# Added by the 2026-08-19 third correction, for the finding that the case above
# proves lock-queue fairness and was being read as proof of a different and
# stronger condition:
#
#     a writer that begins after the migration has **acquired and holds** its
#     `ACCESS EXCLUSIVE` lock cannot commit until the migration transaction
#     finishes.
#
# Establishing that needs the migration observably stopped at a point *after*
# the grant and *before* the end of its transaction. The revision has no such
# point and must not grow one: the handover forbids a production pause hook, and
# a revision carrying one would no longer be the program a deployment runs.
#
# So the hold is taken from PostgreSQL instead of from the migration. Alembic
# updates its own `alembic_version` row **inside the migration transaction**,
# after the revision body has run, so a single `SELECT … FOR UPDATE` on that row
# — issued by this test, on its own connection — stops the production child
# exactly here:
#
#     LOCK TABLE reconciliation_jobs IN ACCESS EXCLUSIVE MODE   <- granted, held
#     count -> zero -> the three ALTER TABLE statements
#     UPDATE alembic_version SET version_num='0012' …           <- waits here
#     (COMMIT is never reached)
#
# Nothing in `migrations/versions/0013_effect_publication_recovery.py`, in
# `migrations/env.py` or in any production module is changed, and the SQL the
# child emits is byte for byte what a deployment emits — the row lock is applied
# from outside, to a table Alembic owns. `pg_cancel_backend` then ends that
# transaction by **rollback**, which is the same finish the guard's own refusal
# produces, and the writer is watched across the boundary.
#
# Every wait below is a bounded poll of `pg_locks`/`pg_stat_activity` scoped to
# `reconciliation_jobs` and to the holding backend. No sleep is used as proof.

#: The table Alembic updates last, inside the migration's own transaction.
VERSION_TABLE = "alembic_version"

#: The lease owner the late writer claims under, so the fence it commits is the
#: production statement for a job it really holds.
HELD_LOCK_OWNER = "worker:under-the-held-lock"

#: The same, for the bounded-cleanup regression below, which runs the same
#: scenario and must not share a lease owner with the case it is about.
CLEANUP_WRITER_OWNER = "worker:bounded-cleanup-regression"


def _holding_after_the_grant(engine):
    """The migration's backend, *while* it holds a granted lock and is waiting.

    Returns the single `pg_locks`/`pg_stat_activity` row for a backend that

    * holds a **granted** `AccessExclusiveLock` on `reconciliation_jobs`, and
    * is itself blocked (`wait_event_type = 'Lock'`) on the `alembic_version`
      row this test holds — which is what makes the interval observable without
      a sleep, and identifies the backend as the migration rather than as an
      unrelated session.

    `None` unless exactly one backend matches, so an unrelated lock cannot
    satisfy the assertion. Reads only the catalogs: a probe that touched
    `reconciliation_jobs` would queue behind the very lock it is observing.
    """

    def probe():
        with engine.connect() as connection:
            rows = [
                dict(row)
                for row in connection.execute(
                    text(
                        "SELECT l.pid, l.granted, l.virtualtransaction, "
                        "a.query, a.wait_event_type, a.state, a.xact_start "
                        "FROM pg_locks l JOIN pg_stat_activity a ON a.pid = l.pid "
                        "WHERE l.locktype = 'relation' "
                        "AND l.relation = 'reconciliation_jobs'::regclass "
                        "AND l.mode = 'AccessExclusiveLock' AND l.granted"
                    )
                )
                .mappings()
                .all()
            ]
        held = [
            row
            for row in rows
            if row["wait_event_type"] == "Lock"
            and VERSION_TABLE in " ".join((row["query"] or "").split())
        ]
        return held[0] if len(rows) == 1 and len(held) == 1 else None

    return probe


def _lock_identity(row: dict) -> tuple:
    """What must not change while the writer waits: the same backend, same transaction."""
    return (row["pid"], row["virtualtransaction"], row["xact_start"])


#: The production commit fence's statement **shape**, as `pg_stat_activity.query`
#: reports it, matched after whitespace normalisation.
#:
#: Tokens rather than the literal SQL, and no token depends on how a driver
#: spells a placeholder: `SqlAlchemyReconciliationJobLeaseRepository.hold_for_effect`
#: writes `:now`, SQLAlchemy renders `%(now)s`, and psycopg sends `$1` — none of
#: which is part of the production contract, and any of which could change with a
#: driver upgrade without the fence changing at all. Every token below *is* part
#: of the contract: the table the effect writes, the two columns it makes durable,
#: the optimistic-concurrency bump, and the once-only predicate that makes the
#: fence a fence.
FENCE_STATEMENT_SHAPE = (
    "UPDATE reconciliation_jobs SET",
    "effect_committed_at =",
    "effect_result =",
    "version = version + 1",
    "AND effect_committed_at IS NULL",
)

#: The receipt the same writer transaction inserts **before** the fence. A lock
#: observed while the backend is still in `seed_import()` says nothing about the
#: fence, so the statement match excludes it by name rather than by timing.
RECEIPT_TABLE = "snapshot_imports"


def _is_the_fence_statement(query: str | None) -> bool:
    """True only for the production `hold_for_effect` UPDATE, whatever spells it."""
    normalised = " ".join((query or "").split())
    return RECEIPT_TABLE not in normalised and all(
        token in normalised for token in FENCE_STATEMENT_SHAPE
    )


def _transaction_identity(row: dict) -> tuple:
    """PostgreSQL-native identity of one writer transaction.

    The backend, its virtual transaction, the real xid it acquired when it wrote
    its receipt, and when it began. Compared across observations this proves the
    *same* transaction is still open — which thread liveness does not: a live
    thread may be between transactions, before its connection, or inside a
    different statement entirely.
    """
    return (
        row["pid"],
        row["virtualtransaction"],
        row["backend_xid"],
        row["xact_start"],
    )


#: The columns every writer-identity probe below reads, so the two observations
#: that are compared are literally the same projection.
_WRITER_COLUMNS = (
    "SELECT l.pid, l.granted, l.virtualtransaction, a.query, a.wait_event_type, "
    "a.state, a.xact_start, a.backend_xid "
    "FROM pg_locks l JOIN pg_stat_activity a ON a.pid = l.pid "
    "WHERE l.locktype = 'relation' "
    "AND l.relation = 'reconciliation_jobs'::regclass "
    "AND l.mode = 'RowExclusiveLock' AND l.pid = :pid "
)


def _the_writers_queued_fence(engine, *, pid: int):
    """**Backend `pid`'s own** ungranted `ROW EXCLUSIVE` request, issued by the fence.

    Narrowly named, and separate from `_ungranted()`, because it proves a
    narrower thing. Added by the 2026-08-19 fourth correction for the finding
    that this case previously accepted *any* queued `RowExclusiveLock` on
    `reconciliation_jobs` and asserted only that it was not the migration's — a
    predicate an unrelated session could satisfy while the intended writer had
    not yet requested its lock at all.

    A row satisfies this probe only when **all** of the following hold, so no
    other session's request can:

    * `pg_locks.pid` is exactly `pid` — the backend the writer connection
      announced from inside its own transaction, not merely "not the migration";
    * the request is for `RowExclusiveLock` on `reconciliation_jobs` and is
      **not** granted;
    * `pg_stat_activity.query` for that same backend is the production
      `hold_for_effect` fence (`_is_the_fence_statement`), so the writer is
      neither in `seed_import()`, nor in connection setup, nor in an unrelated
      statement; and
    * it is waiting on a `Lock` and already holds a real xid, which its receipt
      insert acquired — that xid is half of the transaction identity the caller
      re-observes later.

    `None` unless exactly one row matches. Reads only the catalogues, never
    `reconciliation_jobs`, which under a pending `ACCESS EXCLUSIVE` request would
    queue the probe behind the thing it is observing.
    """

    def probe():
        with engine.connect() as connection:
            rows = [
                dict(row)
                for row in connection.execute(
                    text(_WRITER_COLUMNS + "AND NOT l.granted"), {"pid": pid}
                )
                .mappings()
                .all()
            ]
        fencing = [
            row
            for row in rows
            if _is_the_fence_statement(row["query"])
            and row["wait_event_type"] == "Lock"
            and row["backend_xid"] is not None
        ]
        return fencing[0] if len(fencing) == 1 else None

    return probe


def _the_writers_open_fence_transaction(engine, *, pid: int):
    """The same backend once its fence has run, **granted** and still uncommitted.

    The other half of the identity claim: the queued request and the transaction
    that commits are one transaction, re-observed from PostgreSQL rather than
    inferred. Matches only a backend that now **holds** the `ROW EXCLUSIVE` lock
    the probe above saw queued, whose last statement is still the fence, and
    which is `idle in transaction` — the fence has executed and the `COMMIT` has
    not been issued.
    """

    def probe():
        with engine.connect() as connection:
            rows = [
                dict(row)
                for row in connection.execute(
                    text(_WRITER_COLUMNS + "AND l.granted"), {"pid": pid}
                )
                .mappings()
                .all()
            ]
        holding = [
            row
            for row in rows
            if _is_the_fence_statement(row["query"])
            and row["state"] == "idle in transaction"
        ]
        return holding[0] if len(holding) == 1 else None

    return probe


class _HeldLockCleanup:
    """Everything TC-MIG-37 holds, and the one bounded, ordered release of it.

    Added by the 2026-08-19 **fifth** correction, for the finding that the case's
    `finally` killed a surviving migration child and then called
    `migration.communicate()` **with no timeout**. If termination or pipe
    collection stalled there, cleanup could hang indefinitely *before* it rolled
    back `holding`, closed `holder` or joined the writer — contradicting the
    mandatory requirement that cleanup stay bounded and release every connection,
    transaction, thread and process on every assertion-failure path, and
    contradicting the case's own claim that its waits are bounded.

    **The 2026-08-19 sixth correction, and what the fifth one still got wrong.**
    The fifth correction bounded the subprocess reap and the writer join and then
    claimed `release()` was bounded on *every* path. It was not. `release()` also
    called

    ```python
    self._holding.rollback()
    self._holder.close()
    ```

    directly, on the calling thread, and neither SQLAlchemy nor psycopg offers a
    timeout for either. Catching an exception does not bound an operation that
    never returns. A blocked `rollback()` meant `close()` and the writer join were
    never reached; a blocked `close()` meant the writer join was never reached; and
    `seconds_ceiling` counted neither call, so the documented 25 seconds described
    a release that could not be shown to end at all. That is the same class of
    defect as the fifth correction's own finding — an unbounded cleanup step
    preventing later resources from being released, and contaminating the next
    case's evidence in the **shared** disposable `freedom_test` database.

    Every database call is now made by a thread of its own through
    `_bounded_call()`, and it is the *wait* that is bounded, because the wait is
    the only part a test can control. What that buys, and what it costs, are both
    stated rather than glossed:

    * a call that does not return within its bound leaves a thread that still owns
      the object it was called on. That thread is **recorded in
      `orphaned_threads`, reported as a problem, and is a daemon**, so it cannot
      keep the pytest process alive at the end of the session;
    * no later step ever touches an object such a thread owns — in particular the
      holder is **not** closed out from under a running `rollback()`, because
      closing it would either race that thread or hand a connection it is still
      using back to the pool; and
    * the holder is **detached from its pool** at construction, while only the
      calling thread owns it. A detached connection is never returned to the pool
      when it is closed, so no orphaned thread can be left owning a connection the
      pool might hand to the next case, on any path, whether or not anything
      blocked.

    Because a stuck connection object is off limits, the close step alone cannot
    satisfy "a blocked rollback must not prevent an independent close/disposal
    attempt". So an independent disposal is attempted in its place: `dispose`
    ends the holder's **backend** from a different connection, which is what
    actually releases the `alembic_version` row lock the rest of the module's
    evidence depends on. See `_backend_disposal()`.

    The order below is the one the case needs, and **every step runs even when an
    earlier one raised, timed out or never returned**:

    1. **release the writer's commit event first**, unconditionally, so a failure
       anywhere cannot leave the writer parked inside an open transaction until
       its own `LOCK_WAIT_SECONDS` bound expires. It costs nothing on the paths
       that already released it;
    2. **end and boundedly reap a surviving migration child before the externally
       held `alembic_version` row lock is released.** Order, not preference: a
       migration *released* rather than *ended* would go on to commit the drops
       the case asserts were undone. Ending it also drops its `ACCESS EXCLUSIVE`
       lock, which is what unblocks a writer still queued behind it — so no
       failure path leaves the writer waiting on a lock holder that outlives the
       test;
    3. **roll back the `alembic_version` row lock**, bounded;
    4. **close the holder**, bounded — a separate step from the rollback, so a
       rollback that raises cannot leak the connection, and one that never returns
       cannot stop the close being attempted;
    5. **dispose of the holder's backend independently**, bounded, when and only
       when step 3 or step 4 did not return — there is nothing to dispose of when
       both completed, and terminating a backend that is already closing would
       report a leak this cleanup does not have; and
    6. **join the writer, bounded, and only if it was started and is still
       alive.** An unconditional join would raise `cannot join thread before it
       is started` out of a failure that happened before `writer.start()`, and
       hide it.

    `attempted` records each step as it is entered, on every path, so "every later
    step was attempted" is observable rather than asserted about the source.

    `release()` **never raises.** It returns a list of problem descriptions. The
    caller — `_released()` below — attaches them to the exception already in
    flight instead of replacing it, which is what keeps the primary assertion
    failure diagnosable while a cleanup failure is still reported.

    Every bound is explicit and every one of them is counted by `seconds_ceiling`,
    which is far below the 60-second production-test ceiling: nothing here is
    allowed to *approach* a hang, let alone reach one.
    """

    def __init__(
        self,
        *,
        may_commit: threading.Event,
        holder,
        holding,
        writer: threading.Thread | None,
        reap_seconds: float = CLEANUP_REAP_SECONDS,
        database_seconds: float = CLEANUP_DATABASE_SECONDS,
        dispose_seconds: float = CLEANUP_DISPOSE_SECONDS,
        join_seconds: float = CLEANUP_JOIN_SECONDS,
        reap=None,
        dispose=None,
    ):
        self._may_commit = may_commit
        self._holder = holder
        self._holding = holding
        self._writer = writer
        self._reap_seconds = reap_seconds
        self._database_seconds = database_seconds
        self._dispose_seconds = dispose_seconds
        self._join_seconds = join_seconds
        #: The subprocess seam. Only the bounded-cleanup regression passes
        #: anything but the default, and only to drive the timeout branch against
        #: a fake child; the real PostgreSQL cases use the real helper.
        self._reap = reap if reap is not None else _bounded_reap
        #: The independent disposal, supplied by the cases that have a database.
        self._dispose = dispose
        #: Recorded the instant the child exists, so no window can leak one.
        self.migration = None
        #: Each release step, in the order it was entered, on every path.
        self.attempted: list[str] = []
        #: Every thread a bounded call outlived. Never hidden: reported as a
        #: problem, and available here so a case can assert what was left.
        self.orphaned_threads: list[threading.Thread] = []
        #: Set when a bounded database call did not return. While it is set, the
        #: holder belongs to that thread and nothing here touches it again.
        self.holder_orphaned = False
        #: Whether the holder could be taken out of the pool's reach. Recorded
        #: rather than assumed: a connection that could not be detached is one an
        #: orphaned thread could still be sharing with the next case.
        self.pool_detached, self._detach_problem = self._detach_the_holder()

    def _detach_the_holder(self) -> tuple[bool, str | None]:
        """Take the holder out of the pool while only this thread owns it.

        Pure bookkeeping inside SQLAlchemy's pool — no round trip, nothing that can
        block — and it is done here, at construction, precisely because it is the
        one moment at which no other thread can possibly be inside this connection.
        Afterwards `close()` closes the DBAPI connection outright instead of
        returning it, so requirement "never return a connection to the pool while
        another thread may still operate on it" holds on **every** path rather than
        only on the paths that noticed a problem.
        """
        detach = getattr(self._holder, "detach", None)
        if detach is None:
            return (False, None)
        try:
            detach()
        except BaseException as error:  # noqa: BLE001 - reported, never raised
            return (
                False,
                f"the holder connection could not be detached from its pool "
                f"({error!r}), so a thread left owning it could still be sharing "
                "a pooled connection with a later case",
            )
        return (True, None)

    @property
    def seconds_ceiling(self) -> float:
        """The worst case `release()` can take, counting **every** bounded wait.

        Two bounded child collections, the bounded rollback, the bounded close, the
        bounded independent disposal and the bounded writer join. The fifth
        correction's ceiling counted only the first and the last of those and was
        wrong by exactly the two database calls this correction bounds.
        """
        return (
            2 * self._reap_seconds
            + 2 * self._database_seconds
            + self._dispose_seconds
            + self._join_seconds
        )

    def started(self, migration):
        """Record and return the migration child, for `migration = cleanup.started(...)`."""
        self.migration = migration
        return migration

    def release(self) -> list[str]:
        """Release everything, in order, within `seconds_ceiling`. Never raises."""
        problems: list[str] = []
        if self._detach_problem:
            problems.append(self._detach_problem)

        def step(what: str, action) -> None:
            self.attempted.append(what)
            try:
                problem = action()
            except BaseException as error:  # noqa: BLE001 - reported, never raised
                problems.append(f"cleanup step {what!r} raised {error!r}")
            else:
                if problem:
                    problems.append(problem)

        step("release the fence writer to commit", self._release_the_writer)
        step("reap the migration child", self._reap_the_migration)
        step("roll back the alembic_version row lock", self._roll_back)
        step("close the holder connection", self._close_the_holder)
        step("dispose of the holder backend independently", self._dispose_of_the_backend)
        step("join the fence writer", self._join_the_writer)
        return problems

    def _orphaned(self, thread: threading.Thread) -> None:
        self.orphaned_threads.append(thread)
        self.holder_orphaned = True

    def _release_the_writer(self) -> str | None:
        self._may_commit.set()
        return None

    def _reap_the_migration(self) -> str | None:
        return self._reap(self.migration, seconds=self._reap_seconds)

    def _roll_back(self) -> str | None:
        if self._holding is None or not self._holding.is_active:
            return None
        problem, orphan = _bounded_call(
            "rolling back the alembic_version row lock",
            self._holding.rollback,
            seconds=self._database_seconds,
        )
        if orphan is not None:
            self._orphaned(orphan)
        return problem

    def _close_the_holder(self) -> str | None:
        if self._holder is None:
            return None
        if self.holder_orphaned:
            # Deliberate, and the reason the independent disposal exists: another
            # thread is still inside this connection. Closing it from here would
            # race that thread, and on a pooled connection would be worse than the
            # leak — it would hand a connection still in use back to the pool.
            return (
                "the holder connection was deliberately not closed: the thread "
                "that owns the call before it never returned and may still be "
                "operating on it, so it is disposed of independently instead"
            )
        problem, orphan = _bounded_call(
            "closing the holder connection",
            self._holder.close,
            seconds=self._database_seconds,
        )
        if orphan is not None:
            self._orphaned(orphan)
        return problem

    def _dispose_of_the_backend(self) -> str | None:
        if not self.holder_orphaned:
            # Both database calls returned, so the connection is resolved and
            # there is nothing left to dispose of. Terminating a backend that is
            # already closing would report a leak this cleanup does not have.
            return None
        if self._dispose is None:
            return (
                "the holder connection was orphaned and no independent disposal "
                "was configured, so its backend and the alembic_version row lock "
                "it holds may survive this test"
            )
        problem, orphan = _bounded_call(
            "disposing of the holder backend",
            self._dispose,
            seconds=self._dispose_seconds,
        )
        if orphan is not None:
            self.orphaned_threads.append(orphan)
        return problem

    def _join_the_writer(self) -> str | None:
        writer = self._writer
        # `is_alive()` rather than an unconditional join: a failure before
        # `writer.start()` must not turn into `cannot join thread before it is
        # started` and hide the real assertion.
        if writer is None or not writer.is_alive():
            return None
        writer.join(timeout=self._join_seconds)
        if writer.is_alive():
            self.orphaned_threads.append(writer)
            return (
                f"the fence writer thread was still alive {self._join_seconds:.0f}s "
                "after its commit event was released; its transaction may survive "
                "this test"
            )
        return None


@contextlib.contextmanager
def _released(cleanup: _HeldLockCleanup):
    """Run `cleanup.release()` on **every** exit path without masking the failure.

    On the failing path the original exception is re-raised unchanged and each
    cleanup problem is attached to it with `add_note()`, so pytest reports the
    assertion that actually failed *and*, underneath it, whatever cleanup could
    not release. Raising the cleanup problem instead — which is what a `finally`
    block that lets its own helper raise does — would substitute a report about
    the cleanup for the failure under diagnosis.

    On the passing path an unreported cleanup problem is itself a failure: that
    this case's cleanup is bounded and total is part of what it claims.
    """
    try:
        yield cleanup
    except BaseException as primary:
        for problem in cleanup.release():
            primary.add_note(f"cleanup also failed: {problem}")
        raise
    problems = cleanup.release()
    assert not problems, "the case passed but its cleanup did not: " + "; ".join(problems)


def test_a_fence_writer_starting_under_the_held_lock_cannot_commit_until_it_ends(
    runtime,
    worker_composition,
    migrated_database,
    database_url,
    callers,
    snapshot,
    head_restored,
):
    """The condition the queue-fairness case does not establish, from a **granted** lock.

    Added by the 2026-08-19 third correction; its lock-identity assertions
    rewritten by the **fourth**, which found that the queued request it accepted
    was never bound to the writer. Every step is read from observable database
    state, in this order, and none of them is a sleep:

    1. the production `alembic downgrade 0012` transaction holds a **granted**
       `AccessExclusiveLock` on `reconciliation_jobs` (`pg_locks.granted`);
    2. no `COMMIT` or other transaction boundary has released it — the same
       backend pid, the same `virtualtransaction` and the same `xact_start` are
       still holding it when the writer has queued, and the child process has not
       exited;
    3. only after that grant is observed does a fence-capable writer begin: the
       production `hold_for_effect` statement, for an apply job it has really
       claimed, beside the receipt the recovery path reads. It announces its
       PostgreSQL backend pid over a bounded queue, from inside its own
       transaction, before it issues any production statement;
    4. the ungranted `RowExclusiveLock` request the assertion uses has **exactly
       that pid**, and `pg_stat_activity` for that pid is the production fence
       statement — not `seed_import`, not connection setup, not an unrelated
       session. A queued request from any other backend cannot satisfy the poll;
    5. while that exact request is ungranted, the migration still holds its
       granted lock on the same backend and transaction, and the fence has
       returned nothing;
    6. the migration transaction finishes, by rollback;
    7. the writer's fence executes and is held open before its `COMMIT`, and the
       transaction observed there — pid, `virtualtransaction`, `backend_xid` and
       `xact_start` — is **identical** to the one whose request was queued in
       step 4; and
    8. only then is it released, and it commits, leaving one committed effect
       that the migration provably did not see.

    **The identity this proves, stated exactly.** Two distinct backends are named
    throughout and never conflated: the *migration holder* (`granted`, bound to
    the guard's transaction by holding `AccessExclusiveLock` while blocked on the
    `alembic_version` row) and the *fence writer* (`writer_pid`, bound by the pid
    it announced and by the fence statement PostgreSQL reports for it). What is
    asserted is that the writer's own transaction was excluded — not merely that
    somebody was.

    **The coordination is a test-only seam.** The writer thread is this module's
    code; it announces its pid and pauses before `COMMIT` on a bounded
    `threading.Event`. No production module, revision statement or emitted SQL
    is changed, no production pause hook exists, and no wait is unbounded or a
    fixed sleep.

    **Cleanup is bounded, ordered and total on every path, and that is proved
    rather than claimed.** Every resource here — the writer's commit event, the
    migration child, the `alembic_version` row lock, the holder connection and
    the writer thread — is owned by `_HeldLockCleanup`, and `_released()` runs its
    single ordered `release()` on every exit path. `release()` cannot wait without
    a bound and cannot raise, so a cleanup problem is attached to the failing
    assertion instead of replacing it. The 2026-08-19 fifth correction added that
    object for the finding that this `finally` block previously called
    `migration.communicate()` with no timeout;
    `test_the_held_lock_cleanup_is_bounded_and_total_when_the_case_fails` drives a
    controlled assertion failure with the migration and the writer both live and
    proves the release is bounded and leaves nothing behind.

    The 2026-08-19 **sixth** correction found that claim still overstated: the
    release's `holding.rollback()` and `holder.close()` were synchronous database
    calls that nothing bounded, and `seconds_ceiling` counted neither. Both are now
    made on threads of their own with bounds of their own, the holder is detached
    from its pool before anything can block it, and a blocked call is reported and
    its backend disposed of independently rather than being closed out from under
    the thread still inside it.
    `…when_the_row_lock_rollback_never_returns` and
    `…when_closing_the_holder_never_returns` drive those two paths deterministically.

    The database is deliberately **below the boundary** when the guard counts, so
    the downgrade proceeds past its refusal into the drops and reaches the
    `alembic_version` update this case holds it at. The rollback puts the three
    dropped objects back, which is asserted rather than assumed.

    **What this case does not prove**, stated so it is not read for more than it
    is: it does not bind the granted lock to the *guard's* `LOCK TABLE`. By the
    hold point the three `ALTER TABLE` statements have run, and each of those
    requires `ACCESS EXCLUSIVE` on its own, so this case still passes against a
    revision whose guard takes no lock at all — verified, and recorded in the
    submission. That the lock is taken **before the count** is the separate
    claim, and it is held by
    `test_a_downgrade_started_during_an_in_flight_effect_refuses_after_it_commits`,
    which asserts the migration waits at `DOWNGRADE_LOCK` itself and fails
    against a guard with that statement removed.
    """
    _preview_id, apply_id = confirm(migrated_database, runtime, callers, snapshot)
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        claimed = repository(connection).claim(owner=HELD_LOCK_OWNER, now=utcnow())
        assert claimed is not None and claimed["id"] == apply_id
        assert committed_effects(connection) == (0, 0), (
            "the guard must count zero, or the downgrade refuses before it ever "
            "reaches the point this case holds it at"
        )
        at_head = schema_fingerprint(connection)

    fence: dict = {}
    #: How the writer names itself to the controlling test, and how the test
    #: releases it. Both bounded: a handshake that never arrives fails the case
    #: with what it saw rather than hanging the suite, and the writer refuses to
    #: wait forever for a release the test may never send.
    announced: "queue.Queue[int]" = queue.Queue(maxsize=1)
    fence_executed = threading.Event()
    may_commit = threading.Event()

    def commit_the_fence():
        connection = migrated_database.connect()
        try:
            with connection.begin():
                # The first statement in the writer's **own** transaction, so
                # what is announced is the backend that will issue the fence and
                # the transaction that will commit it — not a pid read before the
                # transaction existed.
                announced.put(
                    connection.execute(text("SELECT pg_backend_pid()")).scalar_one()
                )
                seed_import(
                    connection,
                    snapshot_id=snapshot_id,
                    account_id=callers["C"].account_id,
                    checksum=checksum,
                    request_key=claimed["request_key"],
                )
                fence["held"] = SqlAlchemyReconciliationJobLeaseRepository(
                    connection
                ).hold_for_effect(
                    job_id=apply_id,
                    owner=HELD_LOCK_OWNER,
                    now=utcnow(),
                    result=FENCE_PAYLOAD,
                )
                # The fence has executed and has **not** committed. Hand that
                # interval to the controlling test, which re-observes this exact
                # transaction in it, then release and commit.
                fence_executed.set()
                assert may_commit.wait(
                    timeout=LOCK_WAIT_SECONDS
                ), "the controlling test never released the fence writer to commit"
            fence["committed"] = True
        except BaseException as error:  # pragma: no cover - reported by assertion
            fence["error"] = repr(error)
        finally:
            connection.close()

    writer = threading.Thread(target=commit_the_fence, daemon=True)
    holder = migrated_database.connect()
    holding = holder.begin()
    # Named before anything can block, so the independent disposal of last resort
    # can end exactly this backend and no other, even if the connection object
    # itself becomes unusable.
    holder_backend = _backend_identity(holder)
    # One object owns every resource this case holds and the single bounded,
    # ordered release of them; `_released()` runs that release on every exit path
    # and, when the case fails, attaches whatever it could not release to the
    # failing assertion rather than in place of it. Every wait inside it is
    # bounded — including the two database calls the 2026-08-19 sixth correction
    # found unbounded — and `seconds_ceiling` counts all of them.
    cleanup = _HeldLockCleanup(
        may_commit=may_commit,
        holder=holder,
        holding=holding,
        writer=writer,
        dispose=_backend_disposal(migrated_database, **holder_backend),
    )
    migration = None
    with _released(cleanup):
        # The hold point, taken before the migration starts so it cannot be
        # missed: Alembic's own version row, locked from outside Alembic.
        assert (
            holder.execute(
                text(f"SELECT version_num FROM {VERSION_TABLE} FOR UPDATE")
            ).scalar_one()
            == REVISION
        )
        migration = cleanup.started(
            start_alembic(database_url, "downgrade", PREVIOUS)
        )

        # (1) and (2): a granted lock, held by a transaction that has not ended.
        granted = _await(
            _holding_after_the_grant(migrated_database),
            what="the downgrade to hold a granted ACCESS EXCLUSIVE lock on "
            "reconciliation_jobs while waiting on the alembic_version row",
        )
        assert granted["granted"] is True
        assert migration.poll() is None, "the migration exited before it was observed"

        # (3): the writer begins only now, under the lock the migration holds,
        # and names the backend every assertion below is bound to.
        writer.start()
        try:
            writer_pid = announced.get(timeout=LOCK_WAIT_SECONDS)
        except queue.Empty:
            raise AssertionError(
                "the fence writer never announced its backend pid, so no "
                f"observation could be bound to it; it reported {fence!r}"
            ) from None
        assert writer_pid != granted["pid"], (
            f"the writer opened on the migration's own backend {writer_pid}, so "
            "an ungranted request from it would prove nothing about exclusion"
        )

        # (4): the ungranted request is *this writer's*, and it is the fence.
        try:
            queued = _await(
                _the_writers_queued_fence(migrated_database, pid=writer_pid),
                what=f"backend {writer_pid} — the fence writer, and no other "
                "session — to hold an ungranted ROW EXCLUSIVE request on "
                "reconciliation_jobs while pg_stat_activity shows it executing "
                "the production hold_for_effect fence",
            )
        except AssertionError as unmet:  # pragma: no cover - reported as the failure
            raise AssertionError(f"{unmet}; the writer reported {fence!r}") from None
        assert queued["pid"] == writer_pid and queued["granted"] is False
        assert _is_the_fence_statement(queued["query"]), queued["query"]
        waiting_transaction = _transaction_identity(queued)

        # (5): and the migration's grant is still the same backend, same
        # transaction, with the writer's fence having returned nothing.
        still_held = _holding_after_the_grant(migrated_database)()
        assert still_held is not None and _lock_identity(still_held) == _lock_identity(
            granted
        ), (
            "the migration transaction ended, or a different one now holds the "
            f"lock: {still_held!r} against {granted!r}"
        )
        assert migration.poll() is None, "the migration finished before the writer waited"
        assert fence == {}, (
            f"the fence writer's transaction was not excluded after all: {fence!r}"
        )

        # (6): the transaction ends — by rollback, the same finish the guard's
        # own refusal produces.
        with migrated_database.connect() as canceller:
            assert (
                canceller.execute(
                    text("SELECT pg_cancel_backend(:pid)"), {"pid": granted["pid"]}
                ).scalar_one()
                is True
            )
        returncode, _stdout, stderr = _reap(migration)
        assert returncode != 0, stderr
        assert "canceling statement due to user request" in stderr, stderr[-2000:]

        # (7): the fence proceeds — in the *same* transaction whose request was
        # queued in (4), re-observed from PostgreSQL rather than inferred from
        # the thread still being alive.
        assert fence_executed.wait(timeout=LOCK_WAIT_SECONDS), (
            "the fence never executed after the migration transaction ended: "
            f"{fence!r}"
        )
        still_open = _await(
            _the_writers_open_fence_transaction(migrated_database, pid=writer_pid),
            what=f"backend {writer_pid} to hold its ROW EXCLUSIVE lock granted, "
            "idle in the transaction that ran the fence and has not committed",
        )
        assert _transaction_identity(still_open) == waiting_transaction, (
            "the transaction that ran the fence is not the one whose request was "
            f"queued: {still_open!r} against {queued!r}"
        )
        assert fence.get("held") is True, fence
        assert "committed" not in fence, f"the fence committed before release: {fence!r}"

        # (8): released, that same transaction commits.
        may_commit.set()
        writer.join(timeout=LOCK_WAIT_SECONDS)
        assert not writer.is_alive(), "the writer never finished"
        assert fence.get("committed") is True, fence

    with migrated_database.begin() as connection:
        assert alembic_revision(connection) == REVISION
        assert revision_objects_present(connection) == (True, True, True), (
            "the rolled-back downgrade did not put its three dropped objects back"
        )
        assert schema_fingerprint(connection) == at_head
        assert committed_effects(connection) == (0, 1), (
            "the late fence committed, and only after the migration transaction "
            "had ended"
        )
        committed = job_row(connection, apply_id)
        assert committed["effect_committed_at"] is not None
        assert committed["effect_result"] == FENCE_PAYLOAD
        assert _holding_after_the_grant(migrated_database)() is None
        assert _the_writers_open_fence_transaction(migrated_database, pid=writer_pid)() is None


# ---------------------------------------------------------------------------
# The failure path itself (2026-08-19 fifth correction, finding F1)
# ---------------------------------------------------------------------------
#
# TC-MIG-37 passing proves the exclusion property. It says nothing at all about
# what happens when one of its assertions **fails**, which is the path the fifth
# correction's finding is about: cleanup there killed a surviving migration child
# and then collected it with an unbounded `communicate()`, so a stall could hang
# the suite before the row lock, the holder and the writer were released.
#
# The cases below hold the cleanup to its claim. The first drives a *controlled*
# assertion failure against real PostgreSQL, with the real Alembic child and the
# real fence writer both live, and proves the release is bounded and total. The
# rest drive the branches a real child cannot be made to take on demand — a
# process that will not die, and the earliest failures, before anything started —
# through the same `_HeldLockCleanup.release()` the case itself runs.


def _job_table_residue(engine, *, writer_pid: int, migration_pid: int) -> dict:
    """What a leaked TC-MIG-37 would leave behind, counted from the catalogues.

    Reads only `pg_locks` and `pg_stat_activity`, never `reconciliation_jobs`
    itself — the same rule every probe in this module follows.
    """
    with engine.connect() as connection:
        return dict(
            connection.execute(
                text(
                    "SELECT (SELECT count(*) FROM pg_locks "
                    "          WHERE locktype = 'relation' "
                    "            AND relation = 'reconciliation_jobs'::regclass "
                    "            AND mode IN ('AccessExclusiveLock', "
                    "                         'RowExclusiveLock')) "
                    "         AS job_table_locks, "
                    "       (SELECT count(*) FROM pg_stat_activity "
                    "          WHERE pid = :writer AND xact_start IS NOT NULL) "
                    "         AS open_writer_transactions, "
                    "       (SELECT count(*) FROM pg_stat_activity "
                    "          WHERE pid = :migration) "
                    "         AS surviving_migration_backends"
                ),
                {"writer": writer_pid, "migration": migration_pid},
            )
            .mappings()
            .one()
        )


def _await_quiet(probe, *, what: str, seconds: float = CLEANUP_SETTLE_SECONDS) -> dict:
    """Poll a counting probe until every count is zero, or fail with what remained.

    Bounded, like `_await()`, and it exists because the interesting assertion here
    is the *absence* of rows: `_await()` cannot distinguish "nothing left" from
    "probe returned nothing useful", and the failure message has to name what
    survived.
    """
    deadline = time.monotonic() + seconds
    while True:
        remaining = probe()
        if not any(remaining.values()):
            return remaining
        if time.monotonic() >= deadline:
            raise AssertionError(
                f"timed out after {seconds:.0f}s waiting for {what}; "
                f"still saw {remaining!r}"
            )
        time.sleep(POLL_SECONDS)


#: The controlled failure this regression injects, recognisable in the report so
#: the test can prove the *original* assertion is what surfaced.
CONTROLLED_FAILURE = "controlled failure injected by the bounded-cleanup regression"


class _RecordingChild:
    """The **real** migration child, wrapped so the test can see *how* it was collected.

    Not a stub, not a fake and not a seam that replaces anything: every call is
    delegated to the real `subprocess.Popen` `start_alembic()` returned, the real
    process runs the production Alembic revision against the disposable database,
    and the real signal is sent to it. What the wrapper adds is a record of the
    `timeout` each `communicate()` carried, and of how often the child was killed.

    **Why a real case needs this to falsify the finding.** A real Alembic child
    killed with `SIGKILL` is collected immediately, so the pre-fix
    `kill(); communicate()` shape returns at once: no assertion about elapsed
    time, about the child being reaped, or about surviving locks can distinguish
    it from the bounded form. The defect is not "cleanup was slow" — it is
    "cleanup asked for a collection it could not bound", and that is a property of
    the *call*, observable only at the call. Recording it is what lets TC-MIG-38,
    driving the production revision and the production fence statement, fail
    deterministically against the pre-fix shape rather than passing blind.
    """

    def __init__(self, process):
        self.process = process
        self.collected_with: list[float | None] = []
        self.kills = 0

    @property
    def pid(self):
        return self.process.pid

    @property
    def returncode(self):
        return self.process.returncode

    def poll(self):
        return self.process.poll()

    def kill(self):
        self.kills += 1
        self.process.kill()

    def terminate(self):  # pragma: no cover - cleanup kills, deliberately
        self.kills += 1
        self.process.terminate()

    def communicate(self, timeout=None):
        self.collected_with.append(timeout)
        return self.process.communicate(timeout=timeout)


@pytest.mark.parametrize(
    "failure_point",
    ["while the writer is queued", "after the fence executed"],
)
def test_the_held_lock_cleanup_is_bounded_and_total_when_the_case_fails(
    runtime,
    worker_composition,
    migrated_database,
    database_url,
    callers,
    snapshot,
    head_restored,
    failure_point,
):
    """TC-MIG-37's own cleanup, driven from a controlled assertion failure.

    The scenario is the case's: the `alembic_version` row is held from outside
    Alembic, the production `alembic downgrade 0012` runs until it holds a granted
    `AccessExclusiveLock` on `reconciliation_jobs` and blocks on that row, and a
    fence-capable writer then opens its own transaction and issues the production
    `hold_for_effect` statement behind that lock. Nothing is stubbed and no
    production code is involved in the coordination: the child is the real
    Alembic process, wrapped only by `_RecordingChild`, which delegates every call
    and adds nothing but a record of how the child was collected.

    Then an assertion fails — deliberately, at a named point — and what is
    measured is the cleanup:

    * it **returns within an explicit bound**, `cleanup.seconds_ceiling`, which is
      far below the 60-second production-test ceiling and is asserted as a wall
      clock measurement taken from the moment of failure;
    * the migration child is **reaped**, not merely signalled;
    * the writer thread and its transaction are **released**;
    * the holder's transaction is rolled back and its connection closed; and
    * PostgreSQL is left with **no** `ACCESS EXCLUSIVE`/`ROW EXCLUSIVE` lock on
      `reconciliation_jobs`, no open transaction for the writer's backend and no
      surviving migration backend.

    Two failure points, because they leave different things to release:

    * `while the writer is queued` — the migration child is **alive** and holds the
      table lock, and the writer is blocked behind it. This is the path the finding
      is about: cleanup must end and collect that child, and doing so is also what
      frees the writer; and
    * `after the fence executed` — the migration transaction has already ended and
      the writer is parked inside an open, uncommitted fence transaction. Nothing
      but the cleanup's own release can get it out.

    The original assertion is checked to have survived: it is what `pytest.raises`
    catches, and the cleanup reported nothing to attach to it.

    **This case falsifies the finding.** Against the pre-fix
    `kill(); communicate()` shape both parameters fail: the surviving child is
    collected with `timeout=None`, and the already-exited child is not collected
    at all. That is asserted at the call rather than through elapsed time on
    purpose — a real Alembic child killed with `SIGKILL` is collected
    immediately, so an unbounded collection returns at once and every timing,
    reaping and residue assertion here would still pass. An earlier draft of this
    module left that gap and relied on TC-MIG-39's fake process alone; the fake
    still covers the branch where the child genuinely never dies, which no real
    child can be made to do on demand.
    """
    _preview_id, apply_id = confirm(migrated_database, runtime, callers, snapshot)
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        claimed = repository(connection).claim(
            owner=CLEANUP_WRITER_OWNER, now=utcnow()
        )
        assert claimed is not None and claimed["id"] == apply_id
        assert committed_effects(connection) == (0, 0)
        at_head = schema_fingerprint(connection)

    report: dict = {}
    announced: "queue.Queue[int]" = queue.Queue(maxsize=1)
    fence_executed = threading.Event()
    may_commit = threading.Event()

    def commit_the_fence():
        # The same writer TC-MIG-37 runs: its own transaction, its pid announced
        # before any production statement, the receipt, the production fence, then
        # the transaction held open on a bounded event until it is released.
        connection = migrated_database.connect()
        try:
            with connection.begin():
                announced.put(
                    connection.execute(text("SELECT pg_backend_pid()")).scalar_one()
                )
                seed_import(
                    connection,
                    snapshot_id=snapshot_id,
                    account_id=callers["C"].account_id,
                    checksum=checksum,
                    request_key=claimed["request_key"],
                )
                report["held"] = SqlAlchemyReconciliationJobLeaseRepository(
                    connection
                ).hold_for_effect(
                    job_id=apply_id,
                    owner=CLEANUP_WRITER_OWNER,
                    now=utcnow(),
                    result=FENCE_PAYLOAD,
                )
                fence_executed.set()
                assert may_commit.wait(
                    timeout=LOCK_WAIT_SECONDS
                ), "the cleanup never released the fence writer to commit"
            report["committed"] = True
        except BaseException as error:  # pragma: no cover - reported by assertion
            report["error"] = repr(error)
        finally:
            connection.close()

    writer = threading.Thread(target=commit_the_fence, daemon=True)
    holder = migrated_database.connect()
    holding = holder.begin()
    holder_backend = _backend_identity(holder)
    cleanup = _HeldLockCleanup(
        may_commit=may_commit,
        holder=holder,
        holding=holding,
        writer=writer,
        dispose=_backend_disposal(migrated_database, **holder_backend),
    )
    migration = None
    failed_at = None

    with pytest.raises(AssertionError) as raised:
        with _released(cleanup):
            assert (
                holder.execute(
                    text(f"SELECT version_num FROM {VERSION_TABLE} FOR UPDATE")
                ).scalar_one()
                == REVISION
            )
            # The real child, wrapped only so the test can observe the timeout its
            # collection carries. Everything about the process is real.
            migration = cleanup.started(
                _RecordingChild(start_alembic(database_url, "downgrade", PREVIOUS))
            )
            granted = _await(
                _holding_after_the_grant(migrated_database),
                what="the downgrade to hold a granted ACCESS EXCLUSIVE lock on "
                "reconciliation_jobs while waiting on the alembic_version row",
            )
            migration_pid = granted["pid"]

            writer.start()
            try:
                writer_pid = announced.get(timeout=LOCK_WAIT_SECONDS)
            except queue.Empty:  # pragma: no cover - reported as the failure
                raise AssertionError(
                    f"the fence writer never announced its pid; it reported {report!r}"
                ) from None
            assert writer_pid != migration_pid

            queued = _await(
                _the_writers_queued_fence(migrated_database, pid=writer_pid),
                what=f"backend {writer_pid} — the fence writer — to hold an "
                "ungranted ROW EXCLUSIVE request on reconciliation_jobs while "
                "executing the production hold_for_effect fence",
            )
            assert queued["pid"] == writer_pid and queued["granted"] is False

            if failure_point == "after the fence executed":
                # Let the migration transaction end so the fence can run; the child
                # is deliberately **not** reaped here, so cleanup still has to
                # collect it.
                with migrated_database.connect() as canceller:
                    assert (
                        canceller.execute(
                            text("SELECT pg_cancel_backend(:pid)"),
                            {"pid": migration_pid},
                        ).scalar_one()
                        is True
                    )
                assert fence_executed.wait(timeout=LOCK_WAIT_SECONDS), report
                _await(
                    _the_writers_open_fence_transaction(
                        migrated_database, pid=writer_pid
                    ),
                    what=f"backend {writer_pid} to hold its fence transaction open "
                    "and uncommitted",
                )

            # The controlled failure. Everything above is live: the writer is
            # inside an open transaction, and — at the first failure point — the
            # migration child is alive and holding the table lock. Asserted rather
            # than assumed, because which of the two shapes cleanup has to handle
            # is exactly what this parameter selects.
            surviving_child = failure_point == "while the writer is queued"
            if surviving_child:
                assert migration.poll() is None, (
                    "the migration child exited before the controlled failure, so "
                    "this parameter did not exercise the surviving-child path"
                )
            else:
                _await(
                    lambda: migration.poll() is not None,
                    what="the cancelled migration child to exit before the "
                    "controlled failure",
                )
            failed_at = time.monotonic()
            raise AssertionError(CONTROLLED_FAILURE)

    elapsed = time.monotonic() - failed_at

    # The failure under diagnosis is what surfaced, and cleanup added nothing,
    # because cleanup had nothing to report.
    assert CONTROLLED_FAILURE in str(raised.value)
    assert getattr(raised.value, "__notes__", []) == [], raised.value.__notes__

    # Bounded, and explicitly so.
    assert elapsed < cleanup.seconds_ceiling, (
        f"cleanup took {elapsed:.1f}s, past its own {cleanup.seconds_ceiling:.0f}s "
        "ceiling"
    )
    assert elapsed < CLEANUP_SETTLE_SECONDS, f"cleanup took {elapsed:.1f}s"

    # The migration child was reaped, not left signalled.
    assert migration.poll() is not None, "the migration child survived cleanup"
    assert migration.returncode is not None

    # …and it was collected **with a bound**. This, not the elapsed time, is what
    # makes the real case a falsifier: a real Alembic child killed with SIGKILL is
    # collected immediately, so the pre-fix `kill(); communicate()` shape returns
    # at once and every timing, reaping and lock assertion above still passes. The
    # defect is a property of the call, so it is asserted at the call.
    assert None not in migration.collected_with, (
        "cleanup collected the real migration child with no timeout — that is the "
        f"pre-fix unbounded shape: {migration.collected_with!r}"
    )
    assert migration.collected_with == [CLEANUP_REAP_SECONDS], (
        "the real migration child was not collected exactly once with the bounded "
        f"reap's own timeout: {migration.collected_with!r}. An empty record means "
        "cleanup skipped an already-exited child instead of collecting its pipes"
    )
    assert migration.kills == (1 if surviving_child else 0), (
        f"the surviving child was killed {migration.kills} time(s); a child that "
        "had already exited must not be signalled, and a live one must be"
    )

    # The writer thread and its transaction were released, and the holder with it.
    assert not writer.is_alive(), report
    assert report.get("held") is True, report
    assert report.get("committed") is True, report
    assert holding.is_active is False
    assert holder.closed is True

    # …and the release entered **every** step, in order, on a path where nothing
    # blocked. Added by the 2026-08-19 sixth correction: the two database calls are
    # now steps of their own with bounds of their own, and `attempted` is what makes
    # "every later step was attempted" observable rather than read off the source.
    assert cleanup.attempted == [
        "release the fence writer to commit",
        "reap the migration child",
        "roll back the alembic_version row lock",
        "close the holder connection",
        "dispose of the holder backend independently",
        "join the fence writer",
    ], cleanup.attempted
    # Nothing blocked, so nothing was left owning anything…
    assert cleanup.orphaned_threads == [], cleanup.orphaned_threads
    assert cleanup.holder_orphaned is False
    # …and the holder was out of the pool's reach for the whole case, so no path
    # here — blocked or not — could have handed a connection still in use back to
    # the pool the rest of the suite draws from.
    assert cleanup.pool_detached is True, (
        "the holder was never detached from its pool, so an orphaned cleanup "
        "thread could have left a pooled connection in use behind it"
    )

    # And PostgreSQL is left with nothing.
    _await_quiet(
        lambda: _job_table_residue(
            migrated_database, writer_pid=writer_pid, migration_pid=migration_pid
        ),
        what="no lock on reconciliation_jobs, no open writer transaction and no "
        "surviving migration backend after cleanup",
    )

    # The killed/cancelled migration rolled back, exactly as the case assumes.
    with migrated_database.begin() as connection:
        assert alembic_revision(connection) == REVISION
        assert revision_objects_present(connection) == (True, True, True)
        assert schema_fingerprint(connection) == at_head
        assert committed_effects(connection) == (0, 1)


class _UnreapableProcess:
    """A migration child that will not die, so only cleanup's own bound can end it.

    The seam the finding needs. A genuinely hung Alembic child cannot be produced
    on demand, and a regression that hung for real would hang the suite rather
    than report — so this fake stands in for "forever" with
    `STAND_IN_FOR_FOREVER` seconds and records **the timeout it was collected
    with**, which is the property under test. A run against the pre-fix
    `kill(); communicate()` shape therefore fails on three independent
    assertions instead of never returning: the recorded `None`, the elapsed
    bound, and the problem cleanup failed to report.

    It is used only for the subprocess-timeout branch. The real PostgreSQL
    concurrency case above still drives the production Alembic revision and the
    production fence statement.
    """

    STAND_IN_FOR_FOREVER = 3.0

    def __init__(self):
        self.pid = -1
        self.kills = 0
        self.collected_with: list[float | None] = []

    def poll(self):
        return None

    def kill(self):
        self.kills += 1

    def terminate(self):  # pragma: no cover - cleanup kills, deliberately
        self.kills += 1

    def communicate(self, timeout=None):
        self.collected_with.append(timeout)
        if timeout is None:
            time.sleep(self.STAND_IN_FOR_FOREVER)
            return "", ""
        time.sleep(min(timeout, self.STAND_IN_FOR_FOREVER))
        raise subprocess.TimeoutExpired(cmd="alembic", timeout=timeout)


class _FakeTransaction:
    """The holder's transaction, without a database, for the branch tests."""

    def __init__(self):
        self.is_active = True
        self.rolled_back = False

    def rollback(self):
        self.rolled_back = True
        self.is_active = False


class _FakeConnection:
    """The holder's connection, without a database, for the branch tests."""

    def __init__(self):
        self.closed = False
        self.detached = False

    def detach(self):
        self.detached = True

    def close(self):
        self.closed = True


def _parked_writer(may_commit: threading.Event) -> tuple:
    """A thread parked exactly where the real writer parks: on the commit event."""
    parked = threading.Event()

    def wait_to_be_released():
        parked.set()
        may_commit.wait(timeout=LOCK_WAIT_SECONDS)

    return threading.Thread(target=wait_to_be_released, daemon=True), parked


def test_the_held_lock_cleanup_is_bounded_when_the_migration_child_will_not_die():
    """The branch a real child cannot be made to take: it never gets collected.

    Proves, deterministically and without a database:

    * cleanup collects the child **with a timeout**, twice, and never once
      without one — the pre-fix defect, asserted directly on what the child was
      asked;
    * it returns well inside its own ceiling even though the child never dies;
    * the stuck child is **reported**, not swallowed; and
    * the rest of the release still happened — the writer was let go, the row
      lock rolled back, the connection closed and the thread joined — so one
      unkillable process cannot strand every other resource.

    The last point is the reason cleanup steps over a failed reap instead of
    raising: a child that survives `SIGKILL` twice is beyond the test's reach,
    while the row lock and the writer transaction are not.
    """
    may_commit = threading.Event()
    writer, parked = _parked_writer(may_commit)
    holding, holder = _FakeTransaction(), _FakeConnection()
    process = _UnreapableProcess()
    cleanup = _HeldLockCleanup(
        may_commit=may_commit,
        holder=holder,
        holding=holding,
        writer=writer,
        reap_seconds=0.25,
        join_seconds=5.0,
    )
    cleanup.started(process)
    writer.start()
    assert parked.wait(timeout=LOCK_WAIT_SECONDS), "the stand-in writer never parked"

    started = time.monotonic()
    problems = cleanup.release()
    elapsed = time.monotonic() - started

    assert None not in process.collected_with, (
        "cleanup collected the migration child with no timeout — that is the "
        f"pre-fix unbounded shape: {process.collected_with!r}"
    )
    assert process.collected_with == [0.25, 0.25], process.collected_with
    assert process.kills == 2, process.kills
    assert elapsed < cleanup.seconds_ceiling, elapsed
    assert elapsed < 2.0, (
        f"cleanup waited {elapsed:.2f}s on a child that never dies; the fake only "
        f"stands in for 'forever' for {_UnreapableProcess.STAND_IN_FOR_FOREVER}s"
    )
    assert len(problems) == 1, problems
    assert "neither killed nor collected" in problems[0], problems

    assert may_commit.is_set()
    assert holding.rolled_back is True and holding.is_active is False
    assert holder.closed is True
    assert not writer.is_alive()


def test_the_held_lock_cleanup_is_bounded_before_the_migration_or_the_writer_starts():
    """The earliest failure paths: no child yet, and a thread never started.

    A failure before `start_alembic()` or before `writer.start()` — including one
    before the pid announcement, which is the same shape — must still release the
    holder, must not join an unstarted thread, and must not report a problem it
    does not have.
    """
    may_commit = threading.Event()
    writer = threading.Thread(target=lambda: None, daemon=True)  # never started
    holding, holder = _FakeTransaction(), _FakeConnection()
    cleanup = _HeldLockCleanup(
        may_commit=may_commit,
        holder=holder,
        holding=holding,
        writer=writer,
        reap_seconds=0.25,
        join_seconds=5.0,
    )

    started = time.monotonic()
    problems = cleanup.release()
    elapsed = time.monotonic() - started

    assert problems == [], problems
    assert elapsed < 1.0, elapsed
    assert may_commit.is_set()
    assert holding.rolled_back is True
    assert holder.closed is True
    assert not writer.is_alive()


def test_a_cleanup_problem_is_reported_without_replacing_the_failure_under_diagnosis():
    """Requirement 3, asserted directly: cleanup must not mask the real failure.

    A `finally` block whose own helper raises substitutes a report about the
    cleanup for the assertion being diagnosed. `_released()` cannot: it re-raises
    the original exception and attaches the cleanup's problems to it as notes.

    The passing path is the mirror image — there is no failure to preserve, so an
    unreported cleanup problem becomes the failure.
    """
    may_commit = threading.Event()
    holding, holder = _FakeTransaction(), _FakeConnection()
    failing = _HeldLockCleanup(
        may_commit=may_commit,
        holder=holder,
        holding=holding,
        writer=None,
        reap_seconds=0.25,
        join_seconds=5.0,
    )
    failing.started(_UnreapableProcess())

    with pytest.raises(AssertionError) as raised:
        with _released(failing):
            raise AssertionError("the assertion under diagnosis")

    assert "the assertion under diagnosis" in str(raised.value)
    notes = getattr(raised.value, "__notes__", [])
    assert any("neither killed nor collected" in note for note in notes), notes
    # …and the resources were still released while that was reported.
    assert holding.rolled_back is True and holder.closed is True

    quiet_holding, quiet_holder = _FakeTransaction(), _FakeConnection()
    passing = _HeldLockCleanup(
        may_commit=threading.Event(),
        holder=quiet_holder,
        holding=quiet_holding,
        writer=None,
        reap_seconds=0.25,
        join_seconds=5.0,
    )
    passing.started(_UnreapableProcess())
    with pytest.raises(AssertionError, match="the case passed but its cleanup did not"):
        with _released(passing):
            pass


# ---------------------------------------------------------------------------
# The database half of the failure path (2026-08-19 sixth correction, finding F1)
# ---------------------------------------------------------------------------
#
# The fifth correction bounded the subprocess reap and the writer join and then
# claimed `_HeldLockCleanup.release()` was bounded on **every** path. It was not:
# `release()` also called `holding.rollback()` and `holder.close()` directly, and
# neither SQLAlchemy nor psycopg offers a timeout for either. A `rollback()` that
# never returns is not made bounded by catching its exception; it simply never
# returns, and `close()`, the independent disposal and the writer join are never
# reached at all. In a **shared** disposable database that also means the next case
# inherits a live backend holding the `alembic_version` row lock.
#
# Neither branch can be produced on demand from healthy PostgreSQL — that is the
# whole point of the finding, and the reason the fifth correction's real-database
# regression and its instant fake transaction/connection falsified neither. The two
# cases below drive them with deterministic stand-ins that block **exactly** where
# the real calls would, record the thread they were called on, and stand in for
# "forever" with a bounded period so that a regression against the unbounded shape
# fails rather than hangs.


class _BlockingCall:
    """A database call that does not return, and remembers how it was made.

    `STAND_IN_FOR_FOREVER` is what "never returns" is approximated by: a stand-in
    that really never returned would strand its own thread and leave this module
    unable to clean up after itself, and the assertions below are all satisfied
    well inside it. The bounded release never waits for the whole of it — that it
    does not is one of the things each case asserts.

    What makes these cases falsifiers of the *unbounded* shape is not elapsed time
    alone but `called_on`: the pre-fix code makes the call on the calling thread,
    where no bound is possible, and the corrected code cannot. That is the same
    "assert at the call" technique `_RecordingChild` uses for the subprocess
    collection, applied to the two database calls.
    """

    STAND_IN_FOR_FOREVER = 3.0

    def __init__(self):
        self.called_on: list[threading.Thread] = []
        self.entered = threading.Event()
        self._may_return = threading.Event()

    def _block(self) -> None:
        self.called_on.append(threading.current_thread())
        self.entered.set()
        self._may_return.wait(timeout=self.STAND_IN_FOR_FOREVER)

    def let_it_return(self) -> None:
        """End the stand-in, so this module leaves no thread of its own running."""
        self._may_return.set()


class _BlockingTransaction(_BlockingCall):
    """The holder's transaction, whose `rollback()` does not return."""

    def __init__(self):
        super().__init__()
        self.is_active = True

    def rollback(self):
        self._block()
        self.is_active = False


class _BlockingConnection(_BlockingCall):
    """The holder's connection, whose `close()` does not return."""

    def __init__(self):
        super().__init__()
        self.closed = False
        self.detached = False

    def detach(self):
        self.detached = True

    def close(self):
        self._block()
        self.closed = True


class _RecordingDisposal:
    """The independent disposal, recorded rather than executed against a database.

    It stands where `_backend_disposal()` stands in the two real-PostgreSQL cases
    and reports what that helper reports when it finds something to end: needing
    the disposal at all means the client-side release did not complete, so it is a
    problem, not a silent success.
    """

    REPORT = "the holder's backend was still live and was disposed of independently"

    def __init__(self):
        self.calls = 0
        self.called_on: list[threading.Thread] = []

    def __call__(self) -> str:
        self.calls += 1
        self.called_on.append(threading.current_thread())
        return self.REPORT


#: The six steps `release()` enters, in order, on every path.
CLEANUP_STEPS = [
    "release the fence writer to commit",
    "reap the migration child",
    "roll back the alembic_version row lock",
    "close the holder connection",
    "dispose of the holder backend independently",
    "join the fence writer",
]

#: Bounds for the two blocked-call regressions. Small, so each case is prompt, and
#: all of them well inside `_BlockingCall.STAND_IN_FOR_FOREVER`, so a release that
#: waited for the stand-in instead of its own bound is visible as a failure.
BLOCKED_REAP_SECONDS = 0.25
BLOCKED_DATABASE_SECONDS = 0.25
BLOCKED_DISPOSE_SECONDS = 0.25
BLOCKED_JOIN_SECONDS = 5.0


def _blocked_cleanup(*, holding, holder, may_commit, writer, dispose):
    return _HeldLockCleanup(
        may_commit=may_commit,
        holder=holder,
        holding=holding,
        writer=writer,
        reap_seconds=BLOCKED_REAP_SECONDS,
        database_seconds=BLOCKED_DATABASE_SECONDS,
        dispose_seconds=BLOCKED_DISPOSE_SECONDS,
        join_seconds=BLOCKED_JOIN_SECONDS,
        dispose=dispose,
    )


def _assert_the_orphan_was_accounted_for(cleanup, blocking, *, owns: str) -> None:
    """Requirement 4, in one place, for both blocked-call cases.

    A bound imposed with a helper thread is only honest if the helper thread is
    itself accounted for. So: exactly one thread was left, it is **not** the
    calling thread, it is a daemon, it is the one that entered the blocked call,
    and it is recorded on the cleanup rather than hidden. The connection it owns is
    out of the pool's reach, and nothing else touched it.
    """
    assert len(cleanup.orphaned_threads) == 1, cleanup.orphaned_threads
    orphan = cleanup.orphaned_threads[0]
    assert orphan is not threading.current_thread()
    assert orphan.daemon is True, (
        f"the thread left owning {owns} is not a daemon, so a call that never "
        "returned would keep the pytest process alive at the end of the session"
    )
    assert blocking.called_on == [orphan], (
        f"{owns} was not called on the thread the release then reported: "
        f"{blocking.called_on!r} against {orphan!r}"
    )
    assert cleanup.holder_orphaned is True
    assert cleanup.pool_detached is True, (
        "the holder was left in its pool while a thread was still inside it, so "
        "the pool could hand a connection in use to the next case"
    )


def _assert_the_orphan_ends(cleanup, blocking) -> None:
    """This module cleans up after its own stand-in: end it, and prove it ended."""
    blocking.let_it_return()
    for orphan in cleanup.orphaned_threads:
        orphan.join(timeout=BLOCKED_JOIN_SECONDS)
        assert not orphan.is_alive(), (
            "the regression's own stand-in thread outlived the case; a bounded "
            "cleanup test must not leak the thread it used to prove the bound"
        )


def test_the_held_lock_cleanup_is_bounded_when_the_row_lock_rollback_never_returns():
    """The first path the fifth correction's ceiling did not cover: `rollback()`.

    The finding, exactly: `release()` called `self._holding.rollback()` on the
    calling thread. Nothing bounds that call — catching its exception describes an
    operation that ended, it does not bound one that never does — and while it was
    blocked, `close()`, the independent disposal and the writer join were never
    reached at all.

    Proved here, deterministically and without waiting for the stand-in's full
    period:

    * `release()` returns inside its **complete** documented ceiling, which now
      counts the two database calls and the disposal as well as the reap and the
      join;
    * the blocked step is **reported**, naming the call and its bound;
    * **every later step was still attempted** — `attempted` lists all six, in
      order;
    * the writer's commit event was set and its bounded join was attempted, and
      the parked writer really was released by it;
    * the holder connection is **not** closed out from under the thread still
      inside it, and the independent disposal is attempted in its place;
    * the thread left owning that call is a daemon, is recorded, and owns a
      connection that was taken out of the pool before anything blocked; and
    * the assertion under diagnosis is what surfaces, with the cleanup problems as
      notes on it.

    Against the pre-fix shape — a direct `self._holding.rollback()` — this case
    fails on `called_on` (the call was made on the calling thread, where no bound
    is possible), on the elapsed bound, and on the absent report and disposal. It
    fails in about `STAND_IN_FOR_FOREVER` seconds rather than hanging.
    """
    may_commit = threading.Event()
    writer, parked = _parked_writer(may_commit)
    holding = _BlockingTransaction()
    holder = _FakeConnection()
    disposal = _RecordingDisposal()
    cleanup = _blocked_cleanup(
        holding=holding,
        holder=holder,
        may_commit=may_commit,
        writer=writer,
        dispose=disposal,
    )
    writer.start()
    assert parked.wait(timeout=LOCK_WAIT_SECONDS), "the stand-in writer never parked"

    started = time.monotonic()
    with pytest.raises(AssertionError) as raised:
        with _released(cleanup):
            raise AssertionError(CONTROLLED_FAILURE)
    elapsed = time.monotonic() - started

    # Asserted **at the call**, before anything about elapsed time: the release
    # could bound this wait only because it did not make the call itself. The
    # pre-fix `self._holding.rollback()` is caught here even on a run where it
    # happened to return quickly, which no timing assertion can do — the same
    # reason `_RecordingChild` records the timeout the subprocess collection
    # carried rather than how long it took.
    assert holding.called_on and holding.called_on[0] is not threading.current_thread(), (
        "the rollback was made on the calling thread; that is the pre-fix shape, "
        "in which no bound on it is possible at all"
    )

    # Bounded — by the release's own ceiling, and well inside the period the
    # stand-in stands in for "forever" with.
    assert elapsed < cleanup.seconds_ceiling, (
        f"cleanup took {elapsed:.2f}s, past its own {cleanup.seconds_ceiling:.2f}s "
        "ceiling"
    )
    assert elapsed < _BlockingCall.STAND_IN_FOR_FOREVER, (
        f"cleanup waited {elapsed:.2f}s on a rollback that does not return; the "
        f"stand-in only stands in for 'forever' for "
        f"{_BlockingCall.STAND_IN_FOR_FOREVER}s, so this is the unbounded shape"
    )

    # Every later step was attempted, in order.
    assert cleanup.attempted == CLEANUP_STEPS, cleanup.attempted

    # The primary assertion is what surfaced; the cleanup problems are notes on it.
    assert CONTROLLED_FAILURE in str(raised.value)
    notes = getattr(raised.value, "__notes__", [])
    assert any(
        "rolling back the alembic_version row lock did not return" in note
        for note in notes
    ), notes
    assert any("deliberately not closed" in note for note in notes), notes
    assert any(_RecordingDisposal.REPORT in note for note in notes), notes

    # The blocked call's own object was never touched again, and the independent
    # disposal was attempted in its place — on a thread of its own, bounded.
    assert holder.closed is False, (
        "the holder was closed while another thread was still inside its "
        "rollback; that is the ownership violation the disposal exists to avoid"
    )
    assert disposal.calls == 1, disposal.calls
    assert disposal.called_on and disposal.called_on[0] is not threading.current_thread()

    # The writer was released and its bounded join really joined it.
    assert may_commit.is_set()
    assert not writer.is_alive()

    _assert_the_orphan_was_accounted_for(
        cleanup, holding, owns="the holder's rollback"
    )
    _assert_the_orphan_ends(cleanup, holding)


def test_the_held_lock_cleanup_is_bounded_when_closing_the_holder_never_returns():
    """The second path: the rollback returns, and `holder.close()` does not.

    Requirement 3 stated directly — a blocked close must not prevent the writer
    cleanup from being attempted — and the mirror of the case above: here the row
    lock really is rolled back, and it is the connection's own `close()` that never
    returns. The same properties are asserted, plus the one specific to this path:
    the rollback completed **before** the close blocked, so the block is provably
    the close and not something inherited from the step before it.

    Against the pre-fix shape — a direct `self._holder.close()` — this case fails
    on `called_on`, on the elapsed bound, and on the absent report and disposal,
    in about `STAND_IN_FOR_FOREVER` seconds rather than hanging.
    """
    may_commit = threading.Event()
    writer, parked = _parked_writer(may_commit)
    holding = _FakeTransaction()
    holder = _BlockingConnection()
    disposal = _RecordingDisposal()
    cleanup = _blocked_cleanup(
        holding=holding,
        holder=holder,
        may_commit=may_commit,
        writer=writer,
        dispose=disposal,
    )
    assert holder.detached is True, (
        "the holder was not detached from its pool at construction, so a thread "
        "left inside its close would still own a poolable connection"
    )
    writer.start()
    assert parked.wait(timeout=LOCK_WAIT_SECONDS), "the stand-in writer never parked"

    started = time.monotonic()
    with pytest.raises(AssertionError) as raised:
        with _released(cleanup):
            raise AssertionError(CONTROLLED_FAILURE)
    elapsed = time.monotonic() - started

    # Asserted at the call, for the same reason as the case above.
    assert holder.called_on and holder.called_on[0] is not threading.current_thread(), (
        "the close was made on the calling thread; that is the pre-fix shape, in "
        "which no bound on it is possible at all"
    )

    assert elapsed < cleanup.seconds_ceiling, (
        f"cleanup took {elapsed:.2f}s, past its own {cleanup.seconds_ceiling:.2f}s "
        "ceiling"
    )
    assert elapsed < _BlockingCall.STAND_IN_FOR_FOREVER, (
        f"cleanup waited {elapsed:.2f}s on a close that does not return; the "
        f"stand-in only stands in for 'forever' for "
        f"{_BlockingCall.STAND_IN_FOR_FOREVER}s, so this is the unbounded shape"
    )

    assert cleanup.attempted == CLEANUP_STEPS, cleanup.attempted

    # The step before it completed, so what blocked is provably the close.
    assert holding.rolled_back is True and holding.is_active is False
    assert holder.entered.is_set(), "the close was never entered at all"

    assert CONTROLLED_FAILURE in str(raised.value)
    notes = getattr(raised.value, "__notes__", [])
    assert any(
        "closing the holder connection did not return" in note for note in notes
    ), notes
    assert any(_RecordingDisposal.REPORT in note for note in notes), notes

    assert disposal.calls == 1, disposal.calls
    assert disposal.called_on and disposal.called_on[0] is not threading.current_thread()

    assert may_commit.is_set()
    assert not writer.is_alive()

    _assert_the_orphan_was_accounted_for(cleanup, holder, owns="the holder's close")
    _assert_the_orphan_ends(cleanup, holder)


@pytest.mark.parametrize("blocked_call", ["rollback", "close"])
def test_a_blocked_database_cleanup_call_fails_the_case_that_otherwise_passed(
    blocked_call,
):
    """Requirement 6's mirror for the two database calls: a passing path still fails.

    `_released()` has no failure to preserve on the passing path, so an unreported
    cleanup problem has to become the failure — otherwise a case could pass while
    leaving a live backend holding the `alembic_version` row lock in the shared
    disposable database, which is exactly the contamination this correction is
    about.
    """
    may_commit = threading.Event()
    if blocked_call == "rollback":
        holding, holder = _BlockingTransaction(), _FakeConnection()
        blocking = holding
    else:
        holding, holder = _FakeTransaction(), _BlockingConnection()
        blocking = holder
    cleanup = _blocked_cleanup(
        holding=holding,
        holder=holder,
        may_commit=may_commit,
        writer=None,
        dispose=_RecordingDisposal(),
    )

    started = time.monotonic()
    with pytest.raises(
        AssertionError, match="the case passed but its cleanup did not"
    ) as raised:
        with _released(cleanup):
            pass
    elapsed = time.monotonic() - started

    named = (
        "rolling back the alembic_version row lock"
        if blocked_call == "rollback"
        else "closing the holder connection"
    )
    assert elapsed < _BlockingCall.STAND_IN_FOR_FOREVER, elapsed
    assert cleanup.attempted == CLEANUP_STEPS, cleanup.attempted
    assert f"{named} did not return within" in str(raised.value)
    assert _RecordingDisposal.REPORT in str(raised.value)
    assert blocking.called_on == cleanup.orphaned_threads, blocking.called_on

    _assert_the_orphan_ends(cleanup, blocking)


# ---------------------------------------------------------------------------
# Offline (--sql): the same lock, in the same transaction, before the drops
# ---------------------------------------------------------------------------


def _generated_downgrade(database_url) -> str:
    return run_alembic(
        database_url, "downgrade", f"{REVISION}:{PREVIOUS}", "--sql"
    ).stdout


def test_the_offline_script_locks_inside_its_own_transaction_before_it_decides():
    """Framing and order, asserted positionally rather than by keyword presence.

    A script containing the words `LOCK TABLE` and `RAISE EXCEPTION` proves
    nothing: what matters is that the lock is taken **after** `BEGIN`, **before**
    the count, and that no `COMMIT` stands between it and the last `DROP` — a
    released lock guards nothing, and PostgreSQL releases a table lock only when
    its transaction ends.
    """
    script = _generated_downgrade(database_url_for_offline())
    body = script[script.index("BEGIN;") :]

    assert body.count("BEGIN;") == 1, "more than one transaction in the script"
    assert body.count("COMMIT;") == 1, "the script commits more than once"

    lock = body.index(DOWNGRADE_LOCK)
    guard = body.index("DO $rollback_boundary$")
    count = body.index("FROM reconciliation_jobs")
    refusal = body.index("RAISE EXCEPTION")
    first_drop = body.index("ALTER TABLE reconciliation_jobs DROP CONSTRAINT")
    last_drop = body.index("DROP COLUMN effect_result")
    commit = body.index("COMMIT;")

    assert 0 < lock < guard < count < refusal < first_drop < last_drop < commit, (
        "the generated statements are not in the safe order"
    )
    # Transaction control only: the guard's PL/pgSQL block has its own
    # `BEGIN … END`, which is a statement block and not a transaction.
    protected = body[lock:last_drop]
    assert "COMMIT;" not in protected and "BEGIN;" not in protected, (
        "the lock is released between the guard and the drops"
    )


def database_url_for_offline() -> str:
    """The disposable URL, resolved through the suite's own guard."""
    return resolve_test_database_url()


def test_the_generated_script_refuses_an_effect_that_commits_while_it_waits(
    runtime,
    worker_composition,
    migrated_database,
    database_url,
    callers,
    snapshot,
    tmp_path,
    head_restored,
):
    """The online case's interleaving, run against the **generated script**.

    Executed with `psql` exactly as an operator would apply it, against the
    disposable database, with an in-flight effect transaction held open. The
    script must wait at its own `LOCK TABLE`, see the fence the worker commits
    afterwards, and refuse with nothing dropped.
    """
    url = make_url(database_url)
    assert url.host in (None, ""), "offline execution is local-socket only"
    assert url.database == "freedom_test"
    script_path = tmp_path / "downgrade-0013-0012.sql"
    script_path.write_text(_generated_downgrade(database_url))

    _preview_id, apply_id = confirm(migrated_database, runtime, callers, snapshot)
    holder, transaction = _in_flight_fence(
        migrated_database, callers, snapshot, apply_id, owner="worker:offline"
    )
    applier = subprocess.Popen(
        ["psql", "-v", "ON_ERROR_STOP=1", "-d", url.database, "-f", str(script_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        waiting = _await(
            _ungranted(migrated_database, "AccessExclusiveLock"),
            what="the generated script to queue for its table lock",
        )
        blocked = " ".join(waiting[0]["query"].split())
        transaction.commit()
        returncode, _stdout, stderr = _reap(applier)
    finally:
        if transaction.is_active:
            transaction.rollback()
        holder.close()
        # Bounded (2026-08-19 fifth correction). `psql` is a child like any other
        # and an unbounded collection here can hang the suite just as easily.
        left_behind = _bounded_reap(applier)

    assert left_behind is None, left_behind
    assert DOWNGRADE_LOCK in blocked, blocked
    assert returncode != 0, "the generated script applied a destructive downgrade"
    assert "committed import effect" in stderr, stderr

    with migrated_database.begin() as connection:
        assert alembic_revision(connection) == REVISION
        assert revision_objects_present(connection) == (True, True, True)
        assert committed_effects(connection) == (0, 1)


# ---------------------------------------------------------------------------
# The retention-aware boundary (2026-08-18 second remediation, finding F2)
# ---------------------------------------------------------------------------


def _age(connection, job_id, *, days: int) -> None:
    """Move one terminal job and its result past N-24's retention age."""
    connection.execute(
        text(
            "UPDATE reconciliation_jobs SET finished_at = now() - "
            "make_interval(days => :days) WHERE id = :id"
        ),
        {"days": days, "id": job_id},
    )
    connection.execute(
        text(
            "UPDATE reconciliation_job_results SET "
            "produced_at = now() - make_interval(days => :days), "
            "expires_at = now() - make_interval(days => :days) + interval '30 days' "
            "WHERE job_id = :id"
        ),
        {"days": days, "id": job_id},
    )


def test_approved_retention_reopens_the_boundary_and_the_round_trip_is_exact(
    runtime,
    worker_composition,
    migrated_database,
    database_url,
    callers,
    snapshot,
    head_restored,
):
    """The predicate the guard actually enforces, proved rather than reworded.

    The controlled documents used to say downgrade was refused *forever* after
    the first committed apply. The guard does not record that historical fact; it
    counts **retained** jobs. So this drives the truth: a real completed apply,
    the production N-24 sweep with its normal audit behaviour, and then the round
    trip the old wording said was impossible.

    What must survive is exactly what N-24 promises: the immutable
    `snapshot_imports` receipt and the append-only audit history, compared on
    `xmin` so a rewrite to an identical value would still show.
    """
    preview_id, apply_id = confirm(migrated_database, runtime, callers, snapshot)
    assert runtime.tick().outcome == "completed"
    with migrated_database.begin() as connection:
        assert committed_effects(connection) == (1, 0)
        _age(connection, apply_id, days=RETENTION_AGE_DAYS)
        _age(connection, preview_id, days=RETENTION_AGE_DAYS)

    with migrated_database.begin() as connection:
        swept = RetentionSweep().apply(
            connection, now=utcnow(), limit=100, operator="remediation-evidence"
        )
    assert swept.removed == 2, swept

    with migrated_database.begin() as connection:
        assert committed_effects(connection) == (0, 0), (
            "retention removed the only rows a downgrade could have destroyed"
        )
        assert (
            connection.execute(
                text("SELECT count(*) FROM reconciliation_job_results")
            ).scalar_one()
            == 0
        )
        assert (
            connection.execute(
                text("SELECT count(*) FROM snapshot_imports")
            ).scalar_one()
            == 1
        ), "the immutable receipt is retained indefinitely"
        at_head = schema_fingerprint(connection)
        before = durable_rows(connection)
        before_at_previous = durable_rows_without_effect_result(connection)

    run_alembic(database_url, "downgrade", PREVIOUS)
    try:
        with migrated_database.begin() as connection:
            assert revision_objects_present(connection) == (False, False, False)
            assert durable_rows_without_effect_result(connection) == before_at_previous
    finally:
        run_alembic(database_url, "upgrade", "head")

    with migrated_database.begin() as connection:
        assert schema_fingerprint(connection) == at_head, "schema parity is not exact"
        assert durable_rows(connection) == before, "the round trip rewrote a row"


def test_an_unpublished_effect_blocks_the_downgrade_at_any_age(
    runtime,
    worker_composition,
    migrated_database,
    database_url,
    callers,
    snapshot,
    head_restored,
):
    """Retention is not, and cannot become, a rollback bypass.

    A committed-but-unpublished effect is a `running` job. N-24 removes only
    **terminal** jobs, so no age makes it eligible — asserted with a sweep run
    ten years into the future, which is stronger than moving the rows back. The
    downgrade still refuses, and the preview above it is retained whole because
    its apply child is not being removed.
    """
    _preview_id, apply_id = confirm(migrated_database, runtime, callers, snapshot)
    crash_after_the_effect(migrated_database, worker_composition, apply_id)

    with migrated_database.begin() as connection:
        swept = RetentionSweep().apply(
            connection,
            now=utcnow() + timedelta(days=3650),
            limit=100,
            operator="remediation-evidence",
        )
    assert swept.removed == 0, swept

    with migrated_database.begin() as connection:
        assert committed_effects(connection) == (0, 1)
        assert job_row(connection, apply_id)["effect_result"] is not None

    message = refuse_downgrade(database_url)
    assert "1 committed but unpublished" in message, message
    assert "retained reconciliation job(s)" in message, message


# ---------------------------------------------------------------------------
# Fixture portability (2026-08-18 second remediation, finding F3)
# ---------------------------------------------------------------------------


def _untrusted_parent(tmp_path):
    """A parent directory the production ancestor rule must refuse.

    Group-writable without the sticky bit — the condition `TrustedAncestors`
    exists to catch, because an account able to rename entries there could stage
    the root-replacement attack S-B-2 is about. Reproduced here rather than
    depending on the host having such a directory, so this case says the same
    thing on every machine.
    """
    untrusted = tmp_path / "untrusted-parent"
    untrusted.mkdir()
    untrusted.chmod(0o775)
    basetemp = untrusted / "pytest-base"
    basetemp.mkdir(mode=0o700)
    return untrusted, basetemp


def test_the_production_ancestor_rule_still_refuses_an_untrusted_parent(tmp_path):
    """The control: the bounded seam is a test seam, not a weakened policy.

    `FilesystemArtifactStore(...)` built with no `ancestors` still walks to `/`
    and still refuses this parent. If this case ever passes for the wrong reason
    — because the production default became bounded — the seam below would be
    proving nothing.
    """
    untrusted, basetemp = _untrusted_parent(tmp_path)
    root = basetemp / "artifacts"

    production = FilesystemArtifactStore(root)
    assert production.ancestors.ceiling is None, "the production default is unbounded"
    with pytest.raises(ArtifactStorageError) as refusal:
        production.ensure_ready()
    assert "root_ancestor_untrusted" in str(refusal.value)

    # And the same directory, with the ordinary-test seam, is usable.
    bounded = open_artifact_store(root, TrustedAncestors(ceiling=basetemp))
    try:
        assert bounded.ancestors.ceiling == basetemp
    finally:
        bounded.close()


def test_the_realistic_rollback_cases_run_below_an_untrusted_parent(
    tmp_path, database_url
):
    """The module itself, run with pytest's base temporary directory under one.

    This is the review host's configuration reproduced deliberately: the seven
    realistic data-bearing cases failed there during fixture setup with
    `root_ancestor_untrusted`, because the production unbounded walk was asking
    about `/opt` and `/`. A nested run is used rather than an assertion about a
    fixture, because what failed was the *run*.

    One representative data-bearing case is driven rather than the whole module,
    for the same reason the suite is serial: the disposable database is shared,
    and a nested run migrates it.
    """
    _untrusted, basetemp = _untrusted_parent(tmp_path)
    module = Path(__file__).resolve()
    nested = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            f"{module}::test_the_downgrade_refuses_a_published_committed_effect",
            f"--basetemp={basetemp / 'run'}",
        ],
        cwd=Path(__file__).resolve().parents[2],
        env={**os.environ, "TEST_DATABASE_URL": database_url},
        capture_output=True,
        text=True,
    )
    output = nested.stdout + nested.stderr
    assert "root_ancestor_untrusted" not in output, output[-3000:]
    assert nested.returncode == 0, output[-3000:]
