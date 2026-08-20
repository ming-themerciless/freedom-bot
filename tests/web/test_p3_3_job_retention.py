"""N-24's retention sweep, against real PostgreSQL and its real constraints.

Added by the 2026-08-18 P3.3 remediation. The command it exercises could not
work: it ran

```sql
UPDATE reconciliation_jobs SET result_id = NULL WHERE id = ANY(:ids)
```

before deleting, and migration 0011 enforces
`CHECK ((state = 'completed') = (result_id IS NOT NULL))` — so the statement
raised for **every completed job**, which is most of what a sweep removes. It
also selected expired previews without regard to their apply children, so a
`parent_job_id … ON DELETE RESTRICT` violation could abort a sweep that should
simply have retained that graph.

Every case here runs the **production transaction** — `RetentionSweep`, the
object `tools.job_retention.main` is a thin argument parser around — or the
command itself. A case that re-implemented the statement would prove nothing
about the command.

**No real player data.** The snapshots are the synthetic Phase 2 bundles the
other P3.3 suites use, and nothing here contacts a live service.
"""
from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

import pytest
from sqlalchemy import insert, text

from adapters.database.tables import reconciliation_job_results
from application.web.jobs import JobKind, JobState
from tools.job_retention import (
    EXIT_OK,
    EXIT_USAGE,
    MAX_LIMIT,
    LimitRefused,
    RetentionSweep,
    main,
    validated_limit,
)
from tests.web.p3_3_fixtures import (
    clean_p3_3_tables,
    seed_import,
    seed_job,
    seed_snapshot,
    select_folder,
    utcnow,
)
from tests.web.portal_fixtures import clean_p3_2_tables, seed_callers

pytestmark = pytest.mark.database

#: Comfortably past N-24's 30 days, and past it by enough that no case depends on
#: how long the case itself takes to run.
LONG_AGO_DAYS = 45
RECENT_DAYS = 2


@pytest.fixture()
def callers(migrated_database, settings):
    yield seed_callers(migrated_database, settings, states=("C", "A"))
    with migrated_database.begin() as connection:
        clean_p3_3_tables(connection)
        clean_p3_2_tables(connection)


@pytest.fixture()
def snapshot(migrated_database, callers):
    with migrated_database.begin() as connection:
        snapshot_id, checksum = seed_snapshot(connection)
        select_folder(
            connection, snapshot_id=snapshot_id, account_id=callers["A"].account_id
        )
    return snapshot_id, checksum


@pytest.fixture()
def sweep() -> RetentionSweep:
    return RetentionSweep()


def terminal_job(
    connection,
    *,
    snapshot_id,
    account_id,
    checksum,
    kind: JobKind = JobKind.PREVIEW,
    state: JobState = JobState.COMPLETED,
    age_days: int = LONG_AGO_DAYS,
    with_result: bool = True,
    result_age_days: int | None = None,
    parent_job_id=None,
):
    """One terminal job of a chosen age, with or without its result row.

    Built in the order the worker builds it — result first, then the job naming
    it — because `CHECK ((state = 'completed') = (result_id IS NOT NULL))` admits
    no other order. Ages are applied by moving `finished_at`, `produced_at` and
    `expires_at`, never by waiting: a retention test that slept for thirty days
    would not be a test.
    """
    finished = utcnow() - timedelta(days=age_days)
    result_id = None
    if with_result:
        produced = utcnow() - timedelta(
            days=result_age_days if result_age_days is not None else age_days
        )
        result_id = uuid4()
    job_id = seed_job(
        connection,
        snapshot_id=snapshot_id,
        account_id=account_id,
        checksum=checksum,
        kind=kind,
        state=JobState.RUNNING if state is JobState.COMPLETED else state,
        lease_owner="fixture:seed" if state is JobState.COMPLETED else None,
        lease_expires_at=(
            utcnow() + timedelta(seconds=60) if state is JobState.COMPLETED else None
        ),
        attempts=1,
        parent_job_id=parent_job_id,
        request_key=f"seeded:{kind.value}:{uuid4().hex}",
    )
    if with_result:
        connection.execute(
            insert(reconciliation_job_results).values(
                id=result_id,
                job_id=job_id,
                summary={"actors": 1},
                blocked_entries=[],
                produced_at=produced,
                expires_at=produced + timedelta(days=30),
            )
        )
    if state is JobState.COMPLETED:
        connection.execute(
            text(
                "UPDATE reconciliation_jobs SET state = 'completed', "
                "result_id = :result, finished_at = :finished, lease_owner = NULL, "
                "lease_expires_at = NULL, heartbeat_at = NULL "
                "WHERE id = :job"
            ),
            {"result": result_id, "finished": finished, "job": job_id},
        )
    else:
        connection.execute(
            text(
                "UPDATE reconciliation_jobs SET finished_at = :finished WHERE id = :job"
            ),
            {"finished": finished, "job": job_id},
        )
    return job_id, result_id


def jobs_present(engine) -> set:
    with engine.begin() as connection:
        return {
            row[0]
            for row in connection.execute(text("SELECT id FROM reconciliation_jobs"))
        }


def results_present(engine) -> set:
    with engine.begin() as connection:
        return {
            row[0]
            for row in connection.execute(
                text("SELECT id FROM reconciliation_job_results")
            )
        }


def immutable_counts(engine) -> dict:
    with engine.begin() as connection:
        return {
            "snapshots": connection.execute(
                text("SELECT count(*) FROM foundry_snapshots")
            ).scalar_one(),
            "imports": connection.execute(
                text("SELECT count(*) FROM snapshot_imports")
            ).scalar_one(),
            "audit": connection.execute(
                text("SELECT count(*) FROM audit_events")
            ).scalar_one(),
        }


def sweep_events(engine) -> list:
    with engine.begin() as connection:
        return (
            connection.execute(
                text(
                    "SELECT payload FROM audit_events "
                    "WHERE action = 'reconciliation.retention_swept' "
                    "ORDER BY occurred_at"
                )
            )
            .scalars()
            .all()
        )


def run_sweep(engine, sweep, *, limit=500, operator="Test Operator"):
    with engine.begin() as connection:
        return sweep.apply(connection, now=utcnow(), limit=limit, operator=operator)


# ---------------------------------------------------------------------------
# 1 and 2 — the two shapes a completed job comes in
# ---------------------------------------------------------------------------


def test_an_expired_completed_preview_and_its_result_are_removed(
    migrated_database, sweep, callers, snapshot
):
    """The case the previous command could not do at all.

    A `completed` job names its result, and the constraint requires it to. The
    old sweep nulled the pointer first and was refused by that constraint every
    time; this one deletes the job and lets `ON DELETE CASCADE` carry the result.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id, result_id = terminal_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )

    outcome = run_sweep(migrated_database, sweep)

    assert (outcome.considered, outcome.removed) == (1, 1)
    assert job_id not in jobs_present(migrated_database)
    assert result_id not in results_present(migrated_database)


def test_an_expired_completed_apply_goes_while_its_import_receipt_stays(
    migrated_database, sweep, callers, snapshot
):
    """N-24's whole distinction, in one case.

    The job and its result are **working papers**: disposable, never read by a
    calculation, reproducible from the immutable snapshot. The
    `snapshot_imports` row is the receipt of what was applied, and it is
    append-only and retained indefinitely. A sweep that removed it would be
    deleting the record of a decision.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        import_id = seed_import(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
        job_id, result_id = terminal_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            kind=JobKind.APPLY,
        )

    run_sweep(migrated_database, sweep)

    assert job_id not in jobs_present(migrated_database)
    assert result_id not in results_present(migrated_database)
    with migrated_database.begin() as connection:
        surviving = connection.execute(
            text("SELECT id FROM snapshot_imports")
        ).scalars().all()
    assert surviving == [import_id], "the receipt outlives the working papers"


# ---------------------------------------------------------------------------
# 3 — the result linked only from the result side
# ---------------------------------------------------------------------------


def test_a_stale_preview_whose_result_is_linked_from_the_result_side_is_removed(
    migrated_database, sweep, callers, snapshot
):
    """A `stale` job cannot name its result — the constraint forbids it.

    R-41 transitions a completed-but-unconfirmed preview to `stale` and must null
    `result_id` to satisfy `CHECK ((state = 'completed') = (result_id IS NOT
    NULL))`. The result row survives, reachable from its own `job_id`, which is
    how a Council member still sees what the withdrawn preview said. A sweep that
    joined only through `reconciliation_jobs.result_id` would never find it, and
    the row would outlive its retention indefinitely.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id, result_id = terminal_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
        connection.execute(
            text(
                "UPDATE reconciliation_jobs SET state = 'stale', "
                "stale_reason = 'folder_changed', result_id = NULL WHERE id = :job"
            ),
            {"job": job_id},
        )
    with migrated_database.begin() as connection:
        assert connection.execute(
            text("SELECT result_id FROM reconciliation_jobs WHERE id = :job"),
            {"job": job_id},
        ).scalar_one() is None

    outcome = run_sweep(migrated_database, sweep)

    assert outcome.removed == 1
    assert job_id not in jobs_present(migrated_database)
    assert result_id not in results_present(migrated_database)


# ---------------------------------------------------------------------------
# 4 — failed and cancelled, with and without a result
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("state", [JobState.FAILED, JobState.CANCELLED])
@pytest.mark.parametrize("with_result", [True, False])
def test_failed_and_cancelled_jobs_follow_the_documented_age_policy(
    migrated_database, sweep, callers, snapshot, state, with_result
):
    """N-24 is "30 days after terminal", not "30 days after a result".

    A `failed` or `cancelled` job need never have produced a result — a
    deterministic `parse_refused` produces none at all — so a sweep that could
    only find jobs through an inner join to `reconciliation_job_results` left
    every one of them in the table forever. The documented rule is the job's own
    terminal age, with the result's expiry as an additional condition where a
    result exists.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        old_id, _ = terminal_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            state=state,
            with_result=with_result,
        )
        young_id, _ = terminal_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            state=state,
            with_result=with_result,
            age_days=RECENT_DAYS,
        )

    outcome = run_sweep(migrated_database, sweep)

    assert outcome.removed == 1
    remaining = jobs_present(migrated_database)
    assert old_id not in remaining
    assert young_id in remaining, "a job inside its retention is not a working paper yet"


def test_a_job_whose_result_has_not_expired_is_retained_even_when_it_is_old(
    migrated_database, sweep, callers, snapshot
):
    """The two conditions can disagree, so both are applied.

    A result's `expires_at` runs from when it was **produced**; the job's
    retention runs from when it reached a terminal state. A job that finished
    long ago whose result was produced recently still holds a live result, and
    removing the job would cascade that result away before its own expiry.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id, _ = terminal_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            age_days=LONG_AGO_DAYS,
            result_age_days=RECENT_DAYS,
        )

    outcome = run_sweep(migrated_database, sweep)

    assert (outcome.considered, outcome.removed) == (0, 0)
    assert job_id in jobs_present(migrated_database)


def test_a_queued_or_running_job_is_never_removed(
    migrated_database, sweep, callers, snapshot
):
    """A live job has no retention age, whatever its `queued_at` says.

    Deleting one would delete work in flight — and a `running` job's deletion
    would take a lease the worker is still heartbeating.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        queued_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            queued_at=utcnow() - timedelta(days=LONG_AGO_DAYS),
        )
        running_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            state=JobState.RUNNING,
            attempts=1,
            lease_owner="worker:aaaa",
            lease_expires_at=utcnow() + timedelta(seconds=60),
            queued_at=utcnow() - timedelta(days=LONG_AGO_DAYS),
        )

    outcome = run_sweep(migrated_database, sweep)

    assert (outcome.considered, outcome.removed) == (0, 0)
    assert {queued_id, running_id} <= jobs_present(migrated_database)


# ---------------------------------------------------------------------------
# 5, 6 and 7 — the preview/apply graph
# ---------------------------------------------------------------------------


def test_an_expired_preview_with_an_unexpired_apply_child_is_retained(
    migrated_database, sweep, callers, snapshot
):
    """`parent_job_id … ON DELETE RESTRICT` is a requirement, not an obstacle.

    An apply names the preview a Council member confirmed. While that apply is
    still retained, the preview it names is part of a record somebody can still
    read — so the whole graph stays. The previous command selected the preview
    regardless and would have aborted the sweep on the foreign key.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        preview_id, _ = terminal_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
        apply_id, _ = terminal_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            kind=JobKind.APPLY,
            age_days=RECENT_DAYS,
            parent_job_id=preview_id,
        )

    outcome = run_sweep(migrated_database, sweep)

    assert outcome.considered == 1, "the preview was eligible on its own age"
    assert outcome.removed == 0, "and retained because its apply still needs it"
    assert {preview_id, apply_id} <= jobs_present(migrated_database)


def test_a_wholly_eligible_graph_is_removed_without_a_constraint_failure(
    migrated_database, sweep, callers, snapshot
):
    """Both ends past their retention: the graph goes, in one statement.

    Nothing disables a constraint, nothing catches an integrity error, and
    nothing widens a cascade. The eligible set is computed so the constraints
    have nothing to object to.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        preview_id, preview_result = terminal_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
        apply_id, apply_result = terminal_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            kind=JobKind.APPLY,
            parent_job_id=preview_id,
        )

    outcome = run_sweep(migrated_database, sweep)

    assert (outcome.considered, outcome.removed) == (2, 2)
    assert jobs_present(migrated_database) == set()
    assert results_present(migrated_database).isdisjoint({preview_result, apply_result})


def test_mixed_graphs_under_one_limit_remove_only_the_removable_ones(
    migrated_database, sweep, callers, snapshot
):
    """One pass, three graphs, and each answered on its own facts.

    The removable graph goes; the graph held open by a young apply stays whole;
    the young standalone job is not even a candidate. `considered` and `removed`
    differ, which is what tells an operator that something was retained rather
    than missed.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        gone_preview, _ = terminal_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
        gone_apply, _ = terminal_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            kind=JobKind.APPLY,
            parent_job_id=gone_preview,
        )
        held_preview, _ = terminal_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
        held_apply, _ = terminal_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            kind=JobKind.APPLY,
            age_days=RECENT_DAYS,
            parent_job_id=held_preview,
        )
        young, _ = terminal_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            age_days=RECENT_DAYS,
        )

    outcome = run_sweep(migrated_database, sweep, limit=10)

    assert (outcome.considered, outcome.removed) == (3, 2)
    assert outcome.retained_graphs == 1
    remaining = jobs_present(migrated_database)
    assert remaining == {held_preview, held_apply, young}


def test_the_limit_bounds_one_pass_and_the_next_pass_finishes_it(
    migrated_database, sweep, callers, snapshot
):
    """A backlog is several bounded transactions, never one long one."""
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        for _ in range(5):
            terminal_job(
                connection,
                snapshot_id=snapshot_id,
                account_id=callers["C"].account_id,
                checksum=checksum,
            )

    first = run_sweep(migrated_database, sweep, limit=2)
    assert (first.considered, first.removed) == (2, 2)
    second = run_sweep(migrated_database, sweep, limit=10)
    assert (second.considered, second.removed) == (3, 3)
    assert jobs_present(migrated_database) == set()


# ---------------------------------------------------------------------------
# 8, 10 and 11 — report mode, immutability, and idempotence
# ---------------------------------------------------------------------------


def test_report_mode_counts_and_writes_nothing(
    migrated_database, sweep, callers, snapshot
):
    """`--report` is the default because a retention sweep is irreversible.

    It writes nothing at all — not even the audit event, because nothing
    happened — and takes no row lock, because a report that blocked the enqueue
    path while somebody read a count would be a report with a cost.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id, result_id = terminal_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
    before = immutable_counts(migrated_database)

    with migrated_database.begin() as connection:
        considered = sweep.report(connection, now=utcnow(), limit=500)

    assert considered == 1
    assert job_id in jobs_present(migrated_database)
    assert result_id in results_present(migrated_database)
    assert immutable_counts(migrated_database) == before
    assert sweep_events(migrated_database) == []


def test_the_immutable_tables_are_untouched_but_for_the_sweeps_own_event(
    migrated_database, sweep, callers, snapshot
):
    """OD-23 and change-log C-8, asserted rather than asserted about.

    `snapshot_imports`, `foundry_snapshots` and every pre-existing audit row are
    exactly as they were; the only difference is the one bounded event recording
    that the sweep ran, carrying a count and the operator's name and **never** a
    job id, a checksum or a requester.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        seed_import(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
        terminal_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
    before = immutable_counts(migrated_database)

    run_sweep(migrated_database, sweep, operator="Peter Duscha")

    after = immutable_counts(migrated_database)
    assert after["snapshots"] == before["snapshots"]
    assert after["imports"] == before["imports"]
    assert after["audit"] == before["audit"] + 1, "exactly one new event: the sweep's"
    events = sweep_events(migrated_database)
    assert len(events) == 1
    assert events[0] == {"removed": 1, "considered": 1, "operator": "Peter Duscha"}
    assert checksum not in str(events[0])


def test_a_repeated_sweep_is_safe_and_removes_zero(
    migrated_database, sweep, callers, snapshot
):
    """Idempotent by construction: the second pass finds no candidate."""
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        terminal_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )

    first = run_sweep(migrated_database, sweep)
    second = run_sweep(migrated_database, sweep)

    assert first.removed == 1
    assert (second.considered, second.removed) == (0, 0)
    assert len(sweep_events(migrated_database)) == 2, (
        "both passes are audited, including the one that removed nothing"
    )


# ---------------------------------------------------------------------------
# 9 — the audit event can veto the whole sweep
# ---------------------------------------------------------------------------


def test_an_audit_failure_rolls_back_every_deletion(
    migrated_database, sweep, callers, snapshot
):
    """The audit event is in the sweep's transaction, and it can refuse it.

    Injected as a real `BEFORE INSERT` trigger on `audit_events` rather than as a
    patched Python object, so what is proved is that PostgreSQL takes the
    deletions down with the event — the property the platform actually relies on.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id, result_id = terminal_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )

    connection = migrated_database.connect()
    transaction = connection.begin()
    try:
        connection.execute(
            text(
                "CREATE FUNCTION pg_temp.refuse_audit() RETURNS trigger AS $$ "
                "BEGIN RAISE EXCEPTION 'injected audit failure'; END; $$ "
                "LANGUAGE plpgsql"
            )
        )
        connection.execute(
            text(
                "CREATE TRIGGER injected_audit_failure BEFORE INSERT ON audit_events "
                "FOR EACH ROW EXECUTE FUNCTION pg_temp.refuse_audit()"
            )
        )
        with pytest.raises(Exception, match="injected audit failure"):
            sweep.apply(
                connection, now=utcnow(), limit=500, operator="Test Operator"
            )
    finally:
        transaction.rollback()
        connection.close()

    assert job_id in jobs_present(migrated_database), "the deletion rolled back"
    assert result_id in results_present(migrated_database)
    assert sweep_events(migrated_database) == []


# ---------------------------------------------------------------------------
# 12 — the limit, refused before anything is opened
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("value", [0, -1, -500, MAX_LIMIT + 1, 10**9])
def test_a_nonsensical_limit_is_refused_before_a_connection_exists(value, monkeypatch):
    """Argument validation that needs no database must not need a database.

    `create_engine` is replaced with something that fails loudly, so a refusal
    that happened *after* the connection was opened would fail this case rather
    than pass it. The command is driven end to end, which is also what proves the
    exit code an operator's script reads.
    """

    def refuse_to_connect(*_args, **_kwargs):
        raise AssertionError(
            "the limit must be refused before a connection is opened"
        )

    monkeypatch.setattr("tools.job_retention.create_engine", refuse_to_connect)
    code = main(["--apply", "--operator", "Test Operator", "--limit", str(value)])
    assert code == EXIT_USAGE


@pytest.mark.parametrize("value", [1, 500, MAX_LIMIT])
def test_a_sensible_limit_is_accepted(value):
    assert validated_limit(value) == value


@pytest.mark.parametrize("value", [0, -1, MAX_LIMIT + 1])
def test_the_validator_names_what_is_wrong(value):
    with pytest.raises(LimitRefused) as refusal:
        validated_limit(value)
    assert "--limit" in str(refusal.value)


def test_apply_without_an_operator_is_refused(monkeypatch):
    """An unattributed retention sweep is not an audited administrative act."""

    def refuse_to_connect(*_args, **_kwargs):
        raise AssertionError("no connection should be opened")

    monkeypatch.setattr("tools.job_retention.create_engine", refuse_to_connect)
    assert main(["--apply", "--operator", "   "]) == EXIT_USAGE


def test_report_mode_through_the_command_writes_nothing(
    migrated_database, database_url, callers, snapshot, monkeypatch, capsys
):
    """The command itself, in its default mode, against the real database.

    Driven through `main` rather than through `RetentionSweep`, so the argument
    parsing, the settings read, the exit code and the operator-facing output are
    all the production ones. The engine is the suite's, so the case and the
    command see one database and one transaction timeline.
    """
    monkeypatch.setenv("APP_ENVIRONMENT", "test")
    monkeypatch.setenv("DATABASE_URL", database_url)
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id, _ = terminal_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
    monkeypatch.setattr(
        "tools.job_retention.create_engine", lambda *_a, **_k: migrated_database
    )
    monkeypatch.setattr(migrated_database, "dispose", lambda: None, raising=False)
    before = immutable_counts(migrated_database)

    assert main([]) == EXIT_OK

    assert "1 terminal job(s)" in capsys.readouterr().out
    assert job_id in jobs_present(migrated_database)
    assert immutable_counts(migrated_database) == before
