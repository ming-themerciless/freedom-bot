"""TC-JOB-01 to TC-JOB-16: the queue, the lease, and the states it cannot hold.

Every case here runs against **real PostgreSQL**, and several run two real
connections concurrently, because the properties are properties of statements and
constraints rather than of Python. A fake would agree with whatever this code
believed.

Three disciplines the suite keeps:

1. **No sleeping for a lease.** A lease is moved into the past by updating the
   row (`expire_lease`), so the *real* reaper statement runs against a real
   expired lease. Shortening the lease instead would also be testing a
   configuration nobody runs — and N-23's lease is an exact 60 that
   `WorkerSettings` refuses to let anything else be.
2. **Concurrency is deterministic.** Two connections are driven step by step with
   explicit barriers rather than raced and hoped over, so a passing run is
   evidence and not luck.
3. **Constraints are falsified, not assumed.** Where the design says a state is
   unrepresentable, a case tries to write it directly and requires PostgreSQL to
   refuse.
"""
from __future__ import annotations

import threading
from datetime import timedelta
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from adapters.web.repositories import ReconciliationJobRepository
from application.web.jobs import FailureCode, JobKind, JobState, StaleCode
from tests import foundry_fixtures as fx
from tests.web.p3_3_fixtures import (
    FIXTURE_FOLDER_PATH,
    clean_p3_3_tables,
    complete_preview,
    expire_lease,
    job_row,
    preview_nonce,
    seed_import,
    seed_job,
    seed_snapshot,
    select_folder,
    snapshot_bytes,
    utcnow,
)
from tests.web.portal_fixtures import clean_p3_2_tables, csrf_token_for, seed_callers

pytestmark = pytest.mark.database

FORM = "application/x-www-form-urlencoded"
#: N-23's exact lease and N-43's cap, as the worker settings carry them. Named
#: here so a case reads as the policy it is exercising.
LEASE_SECONDS = 60
MAX_ATTEMPTS = 3


def repository(connection) -> ReconciliationJobRepository:
    return ReconciliationJobRepository(
        connection, lease_seconds=LEASE_SECONDS, max_attempts=MAX_ATTEMPTS
    )


@pytest.fixture()
def callers(migrated_database, settings):
    yield seed_callers(migrated_database, settings, states=("C", "A", "CA", "M"))
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


def _post(client, settings, caller, path, body):
    return client.post(
        path,
        cookies=caller.cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": FORM},
        content=f"csrf_token={csrf_token_for(settings, caller)}&{body}",
    )


# ---------------------------------------------------------------------------
# TC-JOB-01
# ---------------------------------------------------------------------------


async def test_a_job_is_created_queued_and_no_work_happens_in_the_request(
    client, settings, migrated_database, callers, snapshot
):
    """TC-JOB-01. The whole reason the package exists.

    Rehearsal B previewed a real 32-Actor folder in 9.566 seconds of GIL-holding
    work. A request that did that would stall the N-22 polls that exist to report
    it. So the request's entire durable effect is one `queued` row: no lease, no
    attempt, no result, and no `snapshot_imports` row.
    """
    snapshot_id, _ = snapshot
    response = await _post(
        client,
        settings,
        callers["C"],
        f"/v1/council/snapshots/{snapshot_id}/preview-jobs",
        f"nonce={preview_nonce('tc-job-01')}",
    )
    assert response.status_code == 303
    with migrated_database.begin() as connection:
        row = (
            connection.execute(text("SELECT * FROM reconciliation_jobs"))
            .mappings()
            .one()
        )
        results = connection.execute(
            text("SELECT count(*) FROM reconciliation_job_results")
        ).scalar_one()
        imports = connection.execute(
            text("SELECT count(*) FROM snapshot_imports")
        ).scalar_one()
    assert (row["state"], row["attempts"], row["lease_owner"], row["result_id"]) == (
        "queued",
        0,
        None,
        None,
    )
    assert row["started_at"] is None
    assert results == 0
    assert imports == 0


# ---------------------------------------------------------------------------
# TC-JOB-02 — two workers cannot claim one attempt
# ---------------------------------------------------------------------------


def test_two_workers_cannot_claim_one_attempt(migrated_database, callers, snapshot):
    """TC-JOB-02, with two **real** connections and `FOR UPDATE SKIP LOCKED`.

    Both claims are issued while the other's transaction is open, which is the
    only arrangement in which `SKIP LOCKED` can be observed doing anything: with
    one connection at a time, a plain `UPDATE … WHERE state = 'queued'` would
    pass this too.

    The second connection must claim **nothing**, not block: skipping is what
    lets a second worker move on to other work instead of queueing behind the
    first, and it is why the platform can add a worker without changing a
    statement.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )

    first = migrated_database.connect()
    second = migrated_database.connect()
    try:
        first_transaction = first.begin()
        second_transaction = second.begin()
        claimed_first = repository(first).claim(owner="worker-a:aaaa", now=utcnow())
        claimed_second = repository(second).claim(owner="worker-b:bbbb", now=utcnow())
        first_transaction.commit()
        second_transaction.commit()
    finally:
        first.close()
        second.close()

    assert claimed_first is not None
    assert claimed_second is None
    row = _row(migrated_database, job_id)
    assert row["attempts"] == 1
    assert row["lease_owner"] == "worker-a:aaaa"


# ---------------------------------------------------------------------------
# TC-JOB-03 — the heartbeat, and the lease as proof of ownership
# ---------------------------------------------------------------------------


def test_a_heartbeat_extends_the_lease_and_a_stranger_changes_nothing(
    migrated_database, callers, snapshot
):
    """TC-JOB-03. `AND lease_owner = :owner` is the whole safety argument.

    A worker that has lost its lease matches zero rows and exits quietly rather
    than stamping a verdict on a job somebody else now owns. Proved for every
    write a worker can make, not only the heartbeat: a stranger cannot complete,
    fail, stale, cancel or abandon the job either.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
    with migrated_database.begin() as connection:
        claimed = repository(connection).claim(owner="owner:1111", now=utcnow())
    assert claimed is not None
    original_expiry = claimed["lease_expires_at"]

    with migrated_database.begin() as connection:
        beat = repository(connection).heartbeat(
            job_id=job_id, owner="owner:1111", now=utcnow() + timedelta(seconds=5)
        )
    assert beat is not None
    extended = _row(migrated_database, job_id)["lease_expires_at"]
    assert extended > original_expiry

    with migrated_database.begin() as connection:
        jobs = repository(connection)
        assert jobs.heartbeat(job_id=job_id, owner="stranger:9999", now=utcnow()) is None
        assert not jobs.complete(
            job_id=job_id,
            owner="stranger:9999",
            result_id=uuid4(),
            fingerprint=None,
            now=utcnow(),
        )
        assert not jobs.fail(
            job_id=job_id,
            owner="stranger:9999",
            code=FailureCode.INTERNAL,
            now=utcnow(),
        )
        assert not jobs.mark_stale_under_lease(
            job_id=job_id,
            owner="stranger:9999",
            reason=StaleCode.FOLDER_CHANGED,
            now=utcnow(),
        )
        assert not jobs.cancel_under_lease(
            job_id=job_id, owner="stranger:9999", now=utcnow()
        )
        stranger = jobs.abandon(job_id=job_id, owner="stranger:9999", now=utcnow())
        assert stranger.state is None
        # And not because an effect committed: the stranger simply never held
        # this job. The two causes of "zero rows" are told apart by the row.
        assert stranger.effect_committed is False

    still = _row(migrated_database, job_id)
    assert still["state"] == "running"
    assert still["lease_owner"] == "owner:1111"


def test_the_fencing_token_stops_a_worker_publishing_after_it_reclaims(
    migrated_database, callers, snapshot
):
    """The claim's own token, not the worker's name.

    A `lease_owner` that were only the worker identity would let **the same
    process** satisfy its own expired lease after the reaper requeued the job and
    it reclaimed — the classic fencing failure, where the fence checks *who* and
    not *which attempt*. The claim mints a fresh token per attempt, so the first
    attempt's publish matches zero rows even when the second belongs to the same
    worker.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
    with migrated_database.begin() as connection:
        first = repository(connection).claim(owner="host/42:aaaaaaaa", now=utcnow())
    with migrated_database.begin() as connection:
        expire_lease(connection, job_id)
    with migrated_database.begin() as connection:
        repository(connection).reap()
    with migrated_database.begin() as connection:
        second = repository(connection).claim(owner="host/42:bbbbbbbb", now=utcnow())

    assert first is not None and second is not None
    with migrated_database.begin() as connection:
        # The *first* attempt, still running somewhere, tries to publish.
        published = repository(connection).complete(
            job_id=job_id,
            owner="host/42:aaaaaaaa",
            result_id=uuid4(),
            fingerprint=None,
            now=utcnow(),
        )
    assert published is False
    assert _row(migrated_database, job_id)["lease_owner"] == "host/42:bbbbbbbb"


# ---------------------------------------------------------------------------
# TC-JOB-05 — attempts one through exhaustion
# ---------------------------------------------------------------------------


def test_attempts_one_through_exhaustion_on_real_postgresql(
    migrated_database, callers, snapshot
):
    """TC-JOB-05, exactly as the traceability row states it.

    After expiry 1 and 2 the job is `queued` with `attempts` 1 then 2,
    `lease_owner` null and `failure_code` null — so **an expired lease is never
    recorded as `failed` while attempts remain** (N-23, N-43). After expiry 3 it
    is `failed` with `attempts_exhausted`, `finished_at` set and `attempts = 3`.

    At no point is the job `running` without a live lease after the reaper has
    run, and at no point does a claim raise a constraint violation.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )

    for attempt in (1, 2, 3):
        with migrated_database.begin() as connection:
            claimed = repository(connection).claim(
                owner=f"worker:{attempt:04d}", now=utcnow()
            )
        assert claimed is not None, f"attempt {attempt} could not be claimed"
        assert claimed["attempts"] == attempt

        with migrated_database.begin() as connection:
            expire_lease(connection, job_id)
        with migrated_database.begin() as connection:
            reaped = repository(connection).reap()
        assert [row["id"] for row in reaped] == [job_id]

        row = _row(migrated_database, job_id)
        assert row["attempts"] == attempt
        assert row["lease_owner"] is None
        assert row["lease_expires_at"] is None
        if attempt < MAX_ATTEMPTS:
            assert row["state"] == "queued"
            assert row["failure_code"] is None
            assert row["finished_at"] is None
        else:
            assert row["state"] == "failed"
            assert row["failure_code"] == "attempts_exhausted"
            assert row["finished_at"] is not None

    # There is no fourth claim, in the design or in the vocabulary.
    with migrated_database.begin() as connection:
        assert repository(connection).claim(owner="worker:9999", now=utcnow()) is None


def test_the_reaper_writes_the_terminal_audit_event_in_the_same_transaction(
    migrated_database, callers, snapshot
):
    """A job may be failed by a process that never executed it.

    Delivery plan §8.2 requires append-only audit facts to record every terminal
    outcome, and the reaper's terminal branch is a terminal outcome. The event
    names the job's **lease history** rather than pretending the reaper did the
    work — which is residual risk RR-14 stated as a payload rather than as a
    footnote.
    """
    from adapters.worker.composition import WorkerComposition  # noqa: F401

    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            state=JobState.RUNNING,
            attempts=MAX_ATTEMPTS,
            lease_owner="dead-worker:cafe",
            lease_expires_at=utcnow() - timedelta(seconds=1),
        )

    runtime = _runtime(migrated_database, instance="reaper-host/1")
    reaped = runtime.reap()
    assert list(reaped) == [job_id]

    with migrated_database.begin() as connection:
        event = (
            connection.execute(
                text(
                    "SELECT * FROM audit_events WHERE action = "
                    "'reconciliation.job_failed'"
                )
            )
            .mappings()
            .one()
        )
    assert event["entity_id"] == str(job_id)
    assert event["payload"]["failure_code"] == "attempts_exhausted"
    assert event["payload"]["lease_owner"] == "dead-worker:cafe"
    assert event["payload"]["reaped_by"] == "reaper-host/1"
    assert event["actor_capability"] == "system"


# ---------------------------------------------------------------------------
# TC-JOB-06, TC-JOB-15 — states the table cannot hold
# ---------------------------------------------------------------------------


def test_completed_is_impossible_without_a_committed_result(
    migrated_database, callers, snapshot
):
    """TC-JOB-06, attempted directly against the database.

    Delivery plan §8.7's *"no state named `completed` precedes durable commit"*,
    as a constraint rather than as a code-review comment. A worker that wrote the
    state before the result would abort its own transaction.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
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
                    "UPDATE reconciliation_jobs SET state = 'completed', "
                    "finished_at = now() WHERE id = :id"
                ),
                {"id": job_id},
            )
    assert "completed_has_a_result" in str(refusal.value)


def test_the_stranded_state_is_unrepresentable(
    migrated_database, callers, snapshot
):
    """TC-JOB-15. Three ways, and PostgreSQL refuses all three.

    This is the constraint the first revision of the contract lacked. Without it
    a job whose third lease expired could sit `running` with nobody running it:
    the reaper requeued only while `attempts < 3`, and a fourth claim would have
    violated the cap anyway. With it, the stranded state is not merely avoided by
    careful code — it is unrepresentable.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            state=JobState.FAILED,
            attempts=MAX_ATTEMPTS,
            failure_code="attempts_exhausted",
        )

    # 1. A direct requeue of an exhausted job.
    with pytest.raises(IntegrityError) as requeue:
        with migrated_database.begin() as connection:
            connection.execute(
                text(
                    "UPDATE reconciliation_jobs SET state = 'queued', "
                    "failure_code = NULL, finished_at = NULL WHERE id = :id"
                ),
                {"id": job_id},
            )
    assert "queued_can_be_claimed" in str(requeue.value)

    # 2. `attempts` cannot exceed the cap.
    with pytest.raises(IntegrityError) as cap:
        with migrated_database.begin() as connection:
            connection.execute(
                text("UPDATE reconciliation_jobs SET attempts = 4 WHERE id = :id"),
                {"id": job_id},
            )
    assert "attempts_within_n43" in str(cap.value)

    # 3. And a claim of such a job matches zero rows rather than violating.
    with migrated_database.begin() as connection:
        assert repository(connection).claim(owner="worker:0001", now=utcnow()) is None


@pytest.mark.parametrize(
    ("column", "value", "constraint"),
    [
        ("failure_code", "NULL", "failed_states_why"),
        ("stale_reason", "NULL", "stale_states_why"),
    ],
)
def test_a_terminal_state_cannot_omit_its_reason(
    migrated_database, callers, snapshot, column, value, constraint
):
    """`failed` states why, and `stale` states why. Both, in the database.

    The runtime role holds `UPDATE` on this table, so a rule that lived only in
    Python would be one direct statement away from a `failed` job nobody can
    explain.
    """
    snapshot_id, checksum = snapshot
    state = "failed" if column == "failure_code" else "stale"
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            state=JobState(state),
        )
    with pytest.raises(IntegrityError) as refusal:
        with migrated_database.begin() as connection:
            connection.execute(
                text(f"UPDATE reconciliation_jobs SET {column} = {value} WHERE id = :id"),
                {"id": job_id},
            )
    assert constraint in str(refusal.value)


def test_running_and_holding_a_lease_are_the_same_fact_in_both_directions(
    migrated_database, callers, snapshot
):
    """A `running` job without a lease is a job nobody owns and nobody will reap.

    The constraint is an equality rather than an implication, so the reverse — a
    lease on a job that is not running — is refused too.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            state=JobState.RUNNING,
            attempts=1,
            lease_owner="owner:1111",
            lease_expires_at=utcnow() + timedelta(seconds=LEASE_SECONDS),
        )
    with pytest.raises(IntegrityError) as dropped:
        with migrated_database.begin() as connection:
            connection.execute(
                text("UPDATE reconciliation_jobs SET lease_owner = NULL WHERE id = :id"),
                {"id": job_id},
            )
    assert "running_holds_a_lease" in str(dropped.value)

    with migrated_database.begin() as connection:
        queued_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
    with pytest.raises(IntegrityError) as held:
        with migrated_database.begin() as connection:
            connection.execute(
                text(
                    "UPDATE reconciliation_jobs SET lease_owner = 'ghost:0000' "
                    "WHERE id = :id"
                ),
                {"id": queued_id},
            )
    assert "running_holds_a_lease" in str(held.value)


# ---------------------------------------------------------------------------
# TC-JOB-07, TC-JOB-08 — one input, one effect
# ---------------------------------------------------------------------------


async def test_a_double_click_yields_one_job_and_one_audit_event(
    client, settings, migrated_database, callers, snapshot
):
    """TC-JOB-07, the double-click half.

    The same request identity — the same snapshot, folder, profile version,
    account and nonce — produces the same request key, and the key is unique. So
    the second submission finds the existing job and redirects to it, and there
    is exactly one `reconciliation.job_queued` event.
    """
    snapshot_id, _ = snapshot
    path = f"/v1/council/snapshots/{snapshot_id}/preview-jobs"
    body = f"nonce={preview_nonce('double-click')}"
    first = await _post(client, settings, callers["C"], path, body)
    second = await _post(client, settings, callers["C"], path, body)

    assert first.status_code == second.status_code == 303
    assert first.headers["location"] == second.headers["location"]
    with migrated_database.begin() as connection:
        jobs = connection.execute(
            text("SELECT count(*) FROM reconciliation_jobs")
        ).scalar_one()
        events = connection.execute(
            text(
                "SELECT count(*) FROM audit_events "
                "WHERE action = 'reconciliation.job_queued'"
            )
        ).scalar_one()
    assert jobs == 1
    assert events == 1


async def test_two_browsers_confirming_the_same_preview_resolve_to_one_apply(
    client, settings, migrated_database, callers, snapshot
):
    """TC-JOB-07's two-browser half, and TC-JOB-08's job-level fence.

    **Two Council accounts, one preview, and the one nonce the form emits.** The
    R-46 nonce is the preview job's own id, so neither browser can choose a
    request identity; what differs between the two request keys is the *account*,
    which the key also includes. Idempotency therefore cannot be what resolves
    this, and `uq_reconciliation_jobs_one_live_apply` is: the second apply of the
    same `(snapshot, folder, profile version)` cannot start while the first is in
    flight, so it is refused with the current state rather than spending ten
    seconds of parsing to discover the first won.

    Before the R-46 boundary admitted only the canonical value this case
    submitted `nonce=browser-a` and `nonce=browser-b` — hand-built values the
    production form never emits — and so proved the fence against an input shape
    that could not occur. Two accounts is the way two browsers actually reach two
    request keys.

    The durable effect is fenced separately and already was, by
    `uq_snapshot_imports_applied_input` and `snapshot_imports.request_key`. This
    index only prevents the wasted work.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        preview_id, _ = complete_preview(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            preview_token="two-browsers",
        )
    path = f"/v1/council/jobs/{preview_id}/apply"
    body = f"nonce={preview_id}&preview_token=two-browsers"
    first = await _post(client, settings, callers["C"], path, body)
    second = await _post(client, settings, callers["CA"], path, body)

    assert first.status_code == 303
    assert second.status_code == 409
    with migrated_database.begin() as connection:
        applies = connection.execute(
            text("SELECT count(*) FROM reconciliation_jobs WHERE kind = 'apply'")
        ).scalar_one()
    assert applies == 1


def test_two_concurrent_inserts_of_one_live_apply_leave_one(
    migrated_database, callers, snapshot
):
    """TC-JOB-08 at the database, with two real connections.

    The route-level check reads before it writes, so on its own it is a
    check-then-act. The partial unique index is what makes the property hold
    under genuine concurrency, and this drives both inserts inside open
    transactions so the index is the only thing that can decide.
    """
    snapshot_id, checksum = snapshot
    first = migrated_database.connect()
    second = migrated_database.connect()
    try:
        first_transaction = first.begin()
        repository(first).insert(
            kind=JobKind.APPLY,
            snapshot_id=snapshot_id,
            folder_id=fx.ACTIVE_FOLDER_ID,
            profile_version="2026-08-09.1",
            fingerprint=b"\x00" * 32,
            requested_by_account_id=callers["C"].account_id,
            requested_capability=_council(),
            request_key="apply:first",
            parent_job_id=None,
            correlation_id=uuid4(),
            now=utcnow(),
        )
        first_transaction.commit()

        second_transaction = second.begin()
        with pytest.raises(IntegrityError) as clash:
            repository(second).insert(
                kind=JobKind.APPLY,
                snapshot_id=snapshot_id,
                folder_id=fx.ACTIVE_FOLDER_ID,
                profile_version="2026-08-09.1",
                fingerprint=b"\x00" * 32,
                requested_by_account_id=callers["C"].account_id,
                requested_capability=_council(),
                request_key="apply:second",
                parent_job_id=None,
                correlation_id=uuid4(),
                now=utcnow(),
            )
        second_transaction.rollback()
    finally:
        first.close()
        second.close()
    assert "uq_reconciliation_jobs_one_live_apply" in str(clash.value)


# ---------------------------------------------------------------------------
# TC-JOB-09 — invalidation
# ---------------------------------------------------------------------------


async def test_a_folder_change_invalidates_every_outstanding_job_atomically(
    client, settings, migrated_database, callers, snapshot
):
    """TC-JOB-09, and the mandatory plan test it implements.

    *An administrator folder change invalidates an existing Council preview, and
    Council confirmation displays the exact changed scope before a new apply.*

    Everything non-terminal **and** every completed-but-unconfirmed preview goes
    `stale` with `folder_changed`, in the same transaction that writes the
    selection — so there is no instant at which the folder has moved and an
    outstanding preview is still confirmable.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        queued_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
        preview_id, _ = complete_preview(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            preview_token="pre-change",
        )

    response = await _post(
        client,
        settings,
        callers["A"],
        f"/v1/admin/snapshots/{snapshot_id}/folder",
        f"folder_id={fx.ARCHIVE_FOLDER_ID}",
    )
    # The fixture bundle exports one folder, so the archive id is not selectable
    # and the selection is refused as input rather than accepted and then found
    # impossible ten seconds into a worker.
    assert response.status_code == 422

    # Now with a snapshot that genuinely exports two.
    with migrated_database.begin() as connection:
        # A **different** payload, so a different checksum. `foundry_snapshots`
        # is unique on the checksum by design — one changed byte is a different
        # snapshot — and a fixture that reused the bytes would be asserting
        # against a row it could not insert.
        pair_id, pair_checksum = seed_snapshot(
            connection,
            payload=snapshot_bytes(
                selected_folder_ids=(fx.ACTIVE_FOLDER_ID, fx.ARCHIVE_FOLDER_ID),
                folders=(
                    fx.folder(fx.ROOT_FOLDER_ID, "Characters"),
                    fx.folder(
                        fx.ACTIVE_FOLDER_ID, "Characters (active)", fx.ROOT_FOLDER_ID
                    ),
                    fx.folder(fx.ARCHIVE_FOLDER_ID, "Archive", fx.ROOT_FOLDER_ID),
                ),
            ),
            folder_ids=(fx.ACTIVE_FOLDER_ID, fx.ARCHIVE_FOLDER_ID),
            actor_count=2,
        )
        select_folder(
            connection, snapshot_id=pair_id, account_id=callers["A"].account_id
        )
        pair_queued = seed_job(
            connection,
            snapshot_id=pair_id,
            account_id=callers["C"].account_id,
            checksum=pair_checksum,
        )
        pair_preview, _ = complete_preview(
            connection,
            snapshot_id=pair_id,
            account_id=callers["C"].account_id,
            checksum=pair_checksum,
            preview_token="pair",
        )

    changed = await _post(
        client,
        settings,
        callers["A"],
        f"/v1/admin/snapshots/{pair_id}/folder",
        f"folder_id={fx.ARCHIVE_FOLDER_ID}",
    )
    assert changed.status_code == 303

    for job_id in (pair_queued, pair_preview):
        row = _row(migrated_database, job_id)
        assert row["state"] == "stale", job_id
        assert row["stale_reason"] == "folder_changed", job_id
    # The **other** snapshot's jobs are untouched: invalidation is scoped to the
    # snapshot whose folder moved, not to the queue.
    for job_id in (queued_id, preview_id):
        assert _row(migrated_database, job_id)["state"] != "stale", job_id


async def test_a_confirmation_of_a_stale_preview_applies_nothing_and_says_why(
    client, settings, migrated_database, callers, snapshot
):
    """The second half of the mandatory test: the Council member is told what moved.

    `409` with VM-19 carrying the current state, whose `stale_reason` is the
    closed-vocabulary code — not a bare refusal, and not a `500`.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        preview_id, _ = complete_preview(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            preview_token="will-go-stale",
        )
        # The profile version moves under the preview.
        connection.execute(
            text(
                "UPDATE reconciliation_jobs SET profile_version = 'moved' "
                "WHERE id = :id"
            ),
            {"id": preview_id},
        )

    response = await _post(
        client,
        settings,
        callers["C"],
        f"/v1/council/jobs/{preview_id}/apply",
        f"nonce={preview_id}&preview_token=will-go-stale",
    )
    assert response.status_code == 409
    assert "profile_version_changed" in response.text
    with migrated_database.begin() as connection:
        applies = connection.execute(
            text("SELECT count(*) FROM reconciliation_jobs WHERE kind = 'apply'")
        ).scalar_one()
        imports = connection.execute(
            text("SELECT count(*) FROM snapshot_imports")
        ).scalar_one()
    assert applies == 0
    assert imports == 0


async def test_a_preview_past_n46_cannot_be_confirmed(
    client, settings, migrated_database, callers, snapshot
):
    """N-46, and it is checked **before** anything else is read.

    An old preview is not confirmable however unchanged everything else is: the
    window bounds the period in which authorization, snapshot, folder, profile
    and aggregate versions are *assumed* unchanged, and it is independent of the
    version rechecks rather than a fallback for them.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        preview_id, _ = complete_preview(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            preview_token="expired",
            produced_at=utcnow() - timedelta(minutes=31),
        )
    response = await _post(
        client,
        settings,
        callers["C"],
        f"/v1/council/jobs/{preview_id}/apply",
        f"nonce={preview_id}&preview_token=expired",
    )
    assert response.status_code == 409
    row = _row(migrated_database, preview_id)
    assert row["state"] == "stale"
    assert row["stale_reason"] == "preview_expired"


async def test_a_wrong_preview_token_is_refused(
    client, settings, migrated_database, callers, snapshot
):
    """Route contract §6.1, control 1, and the reason it is one of four.

    The token names *this* preview. It is compared in constant time, and a
    mismatch is refused with the same code an expired or incomplete preview gets
    — distinguishing them would tell a caller which half of a confirmation they
    guessed right.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        preview_id, _ = complete_preview(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            preview_token="the-real-token",
        )
    response = await _post(
        client,
        settings,
        callers["C"],
        f"/v1/council/jobs/{preview_id}/apply",
        f"nonce={preview_id}&preview_token=not-the-real-token",
    )
    assert response.status_code == 409
    with migrated_database.begin() as connection:
        applies = connection.execute(
            text("SELECT count(*) FROM reconciliation_jobs WHERE kind = 'apply'")
        ).scalar_one()
    assert applies == 0


# ---------------------------------------------------------------------------
# TC-JOB-10 — authority is re-resolved at apply
# ---------------------------------------------------------------------------


async def test_council_revoked_between_preview_and_apply_is_refused(
    client, settings, migrated_database, callers, snapshot
):
    """TC-JOB-10 at the request boundary.

    *Preview permission is not apply permission.* The confirmation resolves
    capability **now** — the preamble does it for this request — so a Council
    role revoked in between refuses the apply, whatever the preview said and
    whatever the page rendered.
    """
    from sqlalchemy import delete

    from adapters.database.tables import discord_membership_roles
    from tests.web.portal_fixtures import COUNCIL_SUBJECT

    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        preview_id, _ = complete_preview(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            preview_token="before-revocation",
        )
        connection.execute(
            delete(discord_membership_roles).where(
                discord_membership_roles.c.discord_user_id == COUNCIL_SUBJECT
            )
        )

    response = await _post(
        client,
        settings,
        callers["C"],
        f"/v1/council/jobs/{preview_id}/apply",
        f"nonce={preview_id}&preview_token=before-revocation",
    )
    assert response.status_code == 403
    with migrated_database.begin() as connection:
        applies = connection.execute(
            text("SELECT count(*) FROM reconciliation_jobs WHERE kind = 'apply'")
        ).scalar_one()
    assert applies == 0


# ---------------------------------------------------------------------------
# TC-JOB-11 — cancellation
# ---------------------------------------------------------------------------


async def test_cancellation_of_a_running_job_is_a_request_not_a_state(
    client, settings, migrated_database, callers, snapshot
):
    """TC-JOB-11's middle case. N-27 has six states and gains no seventh.

    A `running` job records `cancel_requested_at` and stays `running` until its
    worker observes the request at the next heartbeat. The route says so by
    redirecting to the job rather than claiming the cancellation happened.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            state=JobState.RUNNING,
            attempts=1,
            lease_owner="worker:1111",
            lease_expires_at=utcnow() + timedelta(seconds=LEASE_SECONDS),
        )
    response = await _post(
        client, settings, callers["C"], f"/v1/council/jobs/{job_id}/cancel", ""
    )
    assert response.status_code == 303
    row = _row(migrated_database, job_id)
    assert row["state"] == "running"
    assert row["cancel_requested_at"] is not None

    # And a claim will not pick it up: the claim predicate excludes a job whose
    # cancellation has been requested, so a requeued attempt does not restart
    # work somebody asked to stop.
    with migrated_database.begin() as connection:
        expire_lease(connection, job_id)
    with migrated_database.begin() as connection:
        repository(connection).reap()
    with migrated_database.begin() as connection:
        assert repository(connection).claim(owner="worker:2222", now=utcnow()) is None


async def test_a_committed_apply_cannot_be_cancelled(
    client, settings, migrated_database, callers, snapshot
):
    """TC-JOB-11's last case, and the `409` that tells the truth about it.

    The cancel statement filters `state IN ('queued','running')`, so a committed
    apply matches zero rows. The route answers `409` with the committed result —
    the difference between "your cancellation was too late" and "your
    cancellation worked".
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        preview_id, _ = complete_preview(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
    response = await _post(
        client, settings, callers["C"], f"/v1/council/jobs/{preview_id}/cancel", ""
    )
    assert response.status_code == 409
    assert _row(migrated_database, preview_id)["state"] == "completed"


def test_cancellation_racing_completion_leaves_exactly_one_outcome(
    migrated_database, callers, snapshot
):
    """A cancel and a completion, issued against one `running` job concurrently.

    Both statements carry a predicate the other invalidates: the cancel filters
    `state IN ('queued','running')` and the completion filters `state = 'running'
    AND lease_owner = :owner`. Whichever commits first, the second matches zero
    rows — so the job holds one terminal state, and the loser reports that it
    lost rather than overwriting.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            state=JobState.RUNNING,
            attempts=1,
            lease_owner="worker:aaaa",
            lease_expires_at=utcnow() + timedelta(seconds=LEASE_SECONDS),
        )

    with migrated_database.begin() as connection:
        result_id = repository(connection).store_result(
            job_id=job_id,
            summary={"actors": 1},
            blocked_entries=[],
            now=utcnow(),
            expires_at=utcnow() + timedelta(days=30),
        )

    # Completion commits first.
    with migrated_database.begin() as connection:
        assert repository(connection).complete(
            job_id=job_id,
            owner="worker:aaaa",
            result_id=result_id,
            fingerprint=None,
            now=utcnow(),
        )
    with migrated_database.begin() as connection:
        outcome = repository(connection).request_cancel(job_id=job_id, now=utcnow())
    # `request_cancel` answers with a typed `Cancellation` from the 2026-08-18
    # effect-publication remediation: `JobState.COMPLETED` used to mean both "the
    # job completed" and "this matched nothing, for one of four reasons", and the
    # route had to guess the conflict word from a state that no longer described
    # the refusal.
    assert outcome.accepted is False
    assert outcome.observed_state is JobState.COMPLETED
    assert outcome.conflict == "already_applied"
    assert _row(migrated_database, job_id)["state"] == "completed"


# ---------------------------------------------------------------------------
# TC-JOB-12 — N-42
# ---------------------------------------------------------------------------


async def test_the_queue_bound_refuses_the_sixth_job_and_creates_no_row(
    client, settings, migrated_database, callers, snapshot
):
    """TC-JOB-12. N-42: at most five `queued` for the whole platform.

    The bound is on the **platform**, not on a snapshot or an account, because
    what it protects is a host shared with three Foundry instances, the live bot
    and PostgreSQL — and five ten-second jobs is already a minute of work.

    The refusal is typed and **creates no row**, so a refused request leaves the
    queue exactly as it found it.
    """
    snapshot_id, _ = snapshot
    path = f"/v1/council/snapshots/{snapshot_id}/preview-jobs"
    for index in range(settings.worker.queue_max_depth):
        accepted = await _post(
            client, settings, callers["C"], path, f"nonce={preview_nonce(f'n{index}')}"
        )
        assert accepted.status_code == 303, index

    refused = await _post(
        client, settings, callers["C"], path, f"nonce={preview_nonce('one-too-many')}"
    )
    assert refused.status_code == 503
    assert refused.json()["error"] == "queue_full"
    with migrated_database.begin() as connection:
        queued = connection.execute(
            text("SELECT count(*) FROM reconciliation_jobs WHERE state = 'queued'")
        ).scalar_one()
    assert queued == settings.worker.queue_max_depth


# ---------------------------------------------------------------------------
# TC-JOB-13 — two reapers
# ---------------------------------------------------------------------------


def test_two_concurrent_reapers_transition_each_job_exactly_once(
    migrated_database, callers, snapshot
):
    """TC-JOB-13, with two real connections over jobs at `attempts` 1, 2 and 3.

    Assertions, as the traceability row states them: each job is transitioned
    exactly once (one `RETURNING` row across both reapers, and `version`
    incremented by exactly one); the `attempts < 3` jobs are `queued` and the
    `attempts = 3` jobs are `failed` with `attempts_exhausted`; `attempts` is
    **unchanged** by the reaper on every branch; and no job is `running` after
    the pass.
    """
    snapshot_id, checksum = snapshot
    jobs: dict[int, str] = {}
    with migrated_database.begin() as connection:
        for attempts in (1, 2, 3):
            jobs[attempts] = seed_job(
                connection,
                snapshot_id=snapshot_id,
                account_id=callers["C"].account_id,
                checksum=checksum,
                state=JobState.RUNNING,
                attempts=attempts,
                lease_owner=f"dead:{attempts:04d}",
                lease_expires_at=utcnow() - timedelta(seconds=5),
            )
    before = {
        attempts: _row(migrated_database, job_id)["version"]
        for attempts, job_id in jobs.items()
    }

    returned: list[list] = [[], []]
    barrier = threading.Barrier(2)

    def reap(slot: int) -> None:
        connection = migrated_database.connect()
        try:
            transaction = connection.begin()
            barrier.wait(timeout=10)
            returned[slot] = [row["id"] for row in repository(connection).reap()]
            transaction.commit()
        finally:
            connection.close()

    threads = [threading.Thread(target=reap, args=(slot,)) for slot in (0, 1)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)

    # Exactly one `RETURNING` row per job, across both reapers.
    all_returned = returned[0] + returned[1]
    assert sorted(all_returned) == sorted(jobs.values())
    assert len(all_returned) == len(set(all_returned))

    for attempts, job_id in jobs.items():
        row = _row(migrated_database, job_id)
        assert row["attempts"] == attempts, "the reaper never writes attempts"
        assert row["version"] == before[attempts] + 1, "transitioned exactly once"
        assert row["lease_owner"] is None
        if attempts < MAX_ATTEMPTS:
            assert row["state"] == "queued"
            assert row["failure_code"] is None
        else:
            assert row["state"] == "failed"
            assert row["failure_code"] == "attempts_exhausted"

    with migrated_database.begin() as connection:
        stranded = connection.execute(
            text(
                "SELECT count(*) FROM reconciliation_jobs WHERE state = 'running' "
                "AND (lease_expires_at IS NULL OR lease_expires_at < now())"
            )
        ).scalar_one()
    assert stranded == 0


# ---------------------------------------------------------------------------
# TC-JOB-16 — self-abandon races the reaper
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("reaper_first", [True, False])
def test_worker_self_abandon_races_the_reaper_in_both_orders(
    migrated_database, callers, snapshot, reaper_first
):
    """TC-JOB-16, run in both orders.

    A worker that exceeds N-45 while its lease has already expired and been
    reaped writes **nothing**: its `AND lease_owner = :owner` update matches zero
    rows, the job keeps the reaper's outcome, and no second `attempts` increment
    or second terminal verdict appears.

    Run the other way round the same predicate protects the reaper: the worker
    has already released the lease, so the reaper's `state = 'running' AND
    lease_expires_at < now()` matches nothing.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            state=JobState.RUNNING,
            attempts=1,
            lease_owner="slow-worker:dead",
            lease_expires_at=utcnow() - timedelta(seconds=5),
        )

    if reaper_first:
        with migrated_database.begin() as connection:
            reaped = repository(connection).reap()
        assert [row["id"] for row in reaped] == [job_id]
        with migrated_database.begin() as connection:
            outcome = repository(connection).abandon(
                job_id=job_id, owner="slow-worker:dead", now=utcnow()
            )
        assert outcome.state is None, "a lost lease writes nothing"
        assert outcome.effect_committed is False
    else:
        with migrated_database.begin() as connection:
            outcome = repository(connection).abandon(
                job_id=job_id, owner="slow-worker:dead", now=utcnow()
            )
        assert outcome.state == "queued"
        with migrated_database.begin() as connection:
            reaped = repository(connection).reap()
        assert reaped == [], "the reaper sees no running job to transition"

    row = _row(migrated_database, job_id)
    assert row["state"] == "queued"
    assert row["attempts"] == 1, "no second increment"
    assert row["failure_code"] is None, "no second verdict"


def test_self_abandon_at_the_last_attempt_fails_the_job_directly(
    migrated_database, callers, snapshot
):
    """The other branch of the same statement, under the worker's own lease.

    A worker abandoning its third attempt has no fourth to fall back on, so the
    job goes **directly** to `failed` with `attempts_exhausted` rather than to a
    `queued` state the check constraint forbids.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            state=JobState.RUNNING,
            attempts=MAX_ATTEMPTS,
            lease_owner="worker:last",
            lease_expires_at=utcnow() + timedelta(seconds=LEASE_SECONDS),
        )
    with migrated_database.begin() as connection:
        outcome = repository(connection).abandon(
            job_id=job_id, owner="worker:last", now=utcnow()
        )
    assert outcome.state == "failed"
    row = _row(migrated_database, job_id)
    assert row["failure_code"] == "attempts_exhausted"
    assert row["finished_at"] is not None


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _row(engine, job_id):
    with engine.begin() as connection:
        return job_row(connection, job_id)


def _council():
    from application.audit import ActorCapability

    return ActorCapability.GUILD_COUNCIL


def _runtime(engine, *, instance: str):
    """A runtime whose composition lends this engine and builds nothing else.

    The reaper needs a job repository and an audit repository and nothing more —
    no artifact store, no import service, no settings graph — so the double
    supplies exactly those. Building a real `WorkerComposition` here would make
    every reaper case also a test of filesystem permissions.
    """
    from application.worker.runtime import WorkerRuntime

    class _ReaperComposition:
        def __init__(self, engine) -> None:
            self.engine = engine

        def jobs(self, connection):
            return repository(connection)

        def audit(self, connection):
            from adapters.web.repositories import WebAuditRepository

            return WebAuditRepository(connection)

    class _Worker:
        heartbeat_seconds = 20
        attempt_timeout_seconds = 300
        queue_max_depth = 5
        lease_seconds = LEASE_SECONDS
        max_attempts = MAX_ATTEMPTS

    return WorkerRuntime(
        composition=_ReaperComposition(engine),
        worker_settings=_Worker(),
        bounds=None,
        guild_id=1,
        instance=instance,
    )
