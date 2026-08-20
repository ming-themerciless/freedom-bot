"""A committed effect is never denied, and is always published.

Added by the 2026-08-18 P3.3 effect-publication remediation, for the two blocking
findings the independent implementation and security re-review raised against the
first one:

1. **A committed effect could be cancelled after reaping.** The `queued` branch of
   `ReconciliationJobRepository.request_cancel` matched `id = :job_id AND state =
   'queued'` and nothing else, and the reaper deliberately requeued a job whose
   effect had committed but whose result had not been published. R-45 arriving in
   that window produced a `cancelled` job over a durable import.

2. **A committed effect could become `failed` on attempt three.** The reaper chose
   between `queued` and `failed` from `attempts < max_attempts` alone, so an apply
   whose effect committed on its last attempt and whose process died before
   publishing was written `failed` with `attempts_exhausted` — over an import the
   database was still holding.

## What changed, and therefore what these cases assert

The reaper no longer touches an expired lease whose `effect_committed_at IS NOT
NULL`. That is not an expiry to retry or exhaust; it is a **publication the
platform owes**. `WorkerRuntime.recover()` takes it instead: under the job row's
write lock it reads the publication payload the commit fence made durable in the
effect's own transaction, reads the immutable `snapshot_imports` receipt that same
transaction wrote, and publishes one `completed` result — in one transaction,
without re-parsing an artifact, re-resolving authority, minting a lease or spending
one of N-43's three attempts.

**The intermediate state therefore changed.** The handover describes the reaper
"moving the job into its recovery state"; under this design the recovery state is
the one the crash already left — `running`, with a lapsed lease and no result — and
what the reaper does is *decline to move it*. `test_the_reaper_leaves_a_committed_
effect_for_publication_at_every_attempt_count` asserts exactly that, at every
attempt count including the cap.

## Disciplines

- **Real PostgreSQL, production statements.** Every state is reached through the
  production claim, the production commit fence, the production reaper and the
  production recovery. The one exception is `test_the_queued_branch_of_r45_refuses_
  a_committed_effect`, which seeds the row directly *because* no production
  statement can produce it any more — that is the point of the case.
- **No sleeping.** Leases are moved into the past; concurrency is driven with an
  explicit row lock held by a second connection.
- **Rows, not return values.** A runtime that returned `"completed"` while writing
  a second import would pass an outcome assertion and fail every one of these.
- **No live service and no real player data.** The artifacts are the synthetic
  Phase 2 bundles the other P3.3 suites use.
"""
from __future__ import annotations

import threading
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from adapters.web.repositories import ReconciliationJobRepository
from adapters.worker.composition import WorkerComposition
from application.audit import ActorCapability
from application.foundry.artifact import ingest_bytes
from application.foundry.audit_policy import IMPORT_APPLIED
from application.web.config import ProcessRole, WebSettings
from application.web.jobs import JobKind, JobState, StaleCode
from application.worker.recovery import RECOVERED_KEY
from application.worker.runtime import WorkerRuntime
from tests.web.p3_3_fixtures import (
    clean_p3_3_tables,
    expire_lease,
    job_row,
    open_artifact_store,
    seed_job,
    seed_snapshot,
    select_folder,
    snapshot_bytes,
    utcnow,
)
from tests.web.portal_fixtures import clean_p3_2_tables, csrf_token_for, seed_callers
from tests.web_fixtures import web_environment

pytestmark = pytest.mark.database

LEASE_SECONDS = 60
MAX_ATTEMPTS = 3
FORM = "application/x-www-form-urlencoded"


# ---------------------------------------------------------------------------
# The harness: one web app and one worker, over one database
# ---------------------------------------------------------------------------


@pytest.fixture()
def artifact_root(tmp_path):
    return tmp_path / "artifacts"


@pytest.fixture()
def worker_settings(tmp_path, artifact_root) -> WebSettings:
    """The worker's own settings graph, over the same synthetic environment.

    Deliberately a second graph rather than the `settings` fixture with a flag
    flipped: S-11 makes `WORKER_ENABLED` the one variable that distinguishes the
    two processes, and a test that shared one graph between them would be testing
    a process topology the platform refuses to run.
    """
    return WebSettings.from_environment(
        web_environment(
            tmp_path,
            WORKER_ENABLED="true",
            WORKER_ARTIFACT_ROOT=str(artifact_root),
        ),
        process=ProcessRole.WORKER,
    )


@pytest.fixture()
def stored(artifact_root, bounded_ancestors):
    """A real restricted artifact store holding one synthetic bundle.

    Returns `(store, checksum, payload)`. The store is the Phase 2 one, with its
    real ownership, mode, symlink and hard-link checks — a fake would prove
    nothing about the path the worker actually reads through.

    Built through `open_artifact_store`, so the **ancestor walk is bounded at
    pytest's temporary root** (2026-08-18 second migration-rollback remediation).
    The production unbounded walk asks whether the host's `/`, `/tmp` and `/opt`
    are trustworthy, which is a question about the machine rather than about this
    code, and it made seven realistic rollback cases fail during fixture setup on
    the independent-review host. The production default is unchanged and is still
    covered by `tests/test_artifact_store.py`.
    """
    store = open_artifact_store(artifact_root, bounded_ancestors)
    payload = snapshot_bytes()
    artifact = ingest_bytes(payload)
    store.store(artifact)
    try:
        yield store, artifact.checksum.hex_digest, payload
    finally:
        store.close()


@pytest.fixture()
def worker_composition(
    worker_settings, stored, migrated_database, bounded_ancestors
):
    composition = WorkerComposition(
        worker_settings, engine=migrated_database, ancestors=bounded_ancestors
    )
    try:
        yield composition
    finally:
        composition.close()


@pytest.fixture()
def runtime(worker_composition, worker_settings):
    return WorkerRuntime(
        composition=worker_composition,
        worker_settings=worker_composition.worker,
        bounds=worker_settings.bounds,
        guild_id=worker_settings.discord.guild_id,
        instance="test-host/1",
    )


@pytest.fixture()
def callers(migrated_database, settings):
    """Seeded against the **web** graph, because the HTTP half of R-45 uses it.

    Both graphs are built from the same synthetic environment, so the guild, the
    role ids and the signing keys are the same values — which is what lets one
    module drive the route and the worker over one database.
    """
    yield seed_callers(migrated_database, settings, states=("C", "A"))
    with migrated_database.begin() as connection:
        clean_p3_3_tables(connection)
        clean_p3_2_tables(connection)


@pytest.fixture()
def snapshot(migrated_database, callers, stored):
    _store, checksum, payload = stored
    with migrated_database.begin() as connection:
        snapshot_id, _ = seed_snapshot(connection, payload=payload)
        select_folder(
            connection, snapshot_id=snapshot_id, account_id=callers["A"].account_id
        )
    return snapshot_id, checksum


def repository(connection) -> ReconciliationJobRepository:
    return ReconciliationJobRepository(
        connection, lease_seconds=LEASE_SECONDS, max_attempts=MAX_ATTEMPTS
    )


def _row(engine, job_id):
    with engine.begin() as connection:
        return job_row(connection, job_id)


async def _post(client, settings, caller, path, body):
    return await client.post(
        path,
        cookies=caller.cookies(settings),
        headers={"Origin": settings.public_origin, "Content-Type": FORM},
        content=f"csrf_token={csrf_token_for(settings, caller)}&{body}",
    )


def effects(engine) -> dict:
    """Every durable trace an apply leaves, counted in one place."""
    with engine.begin() as connection:
        return {
            "imports": connection.execute(
                text("SELECT count(*) FROM snapshot_imports")
            ).scalar_one(),
            "characters": connection.execute(
                text("SELECT count(*) FROM characters")
            ).scalar_one(),
            "mappings": connection.execute(
                text("SELECT count(*) FROM external_actor_mappings")
            ).scalar_one(),
            "applied_audit": connection.execute(
                text("SELECT count(*) FROM audit_events WHERE action = :applied"),
                {"applied": IMPORT_APPLIED},
            ).scalar_one(),
        }


ONE_APPLY = {"imports": 1, "characters": 1, "mappings": 1, "applied_audit": 1}


def published(engine, job_id) -> dict:
    """The publication, counted from both sides of the transaction that makes it.

    A result row without its completion event, or two of either, is the failure
    mode every idempotency case here exists to exclude — so both are counted
    together rather than one being taken as evidence of the other.
    """
    with engine.begin() as connection:
        return {
            "results": connection.execute(
                text(
                    "SELECT count(*) FROM reconciliation_job_results "
                    "WHERE job_id = :id"
                ),
                {"id": job_id},
            ).scalar_one(),
            "completions": connection.execute(
                text(
                    "SELECT count(*) FROM audit_events "
                    "WHERE entity_type = 'reconciliation_job' AND entity_id = :id "
                    "AND action LIKE 'reconciliation.%_completed'"
                ),
                {"id": str(job_id)},
            ).scalar_one(),
        }


def confirm(engine, runtime, callers, snapshot):
    """A completed preview and the apply job R-46 would have enqueued from it."""
    snapshot_id, checksum = snapshot
    with engine.begin() as connection:
        preview_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
    assert runtime.tick().outcome == "completed"
    preview = _row(engine, preview_id)
    with engine.begin() as connection:
        apply_id = repository(connection).insert(
            kind=JobKind.APPLY,
            snapshot_id=snapshot_id,
            folder_id=preview["folder_id"],
            profile_version=preview["profile_version"],
            fingerprint=bytes(preview["scope_fingerprint"]),
            requested_by_account_id=callers["C"].account_id,
            requested_capability=ActorCapability.GUILD_COUNCIL,
            request_key=f"p3.3:apply:{uuid4().hex}",
            parent_job_id=preview_id,
            correlation_id=preview["correlation_id"],
            now=utcnow(),
        )
    return preview_id, apply_id


def crash_after_the_effect(
    engine, composition, apply_id, *, owner="crashing:aaaa", attempts_before=0
):
    """Commit the effect through the production path, then stop existing.

    The executor is driven directly rather than through `WorkerRuntime._run`,
    because what has to be reproduced is **process death between the two
    commits** — the runtime's own publication is the thing that must not happen.
    A daemon thread that eventually returns would be a different case, and the
    handover names process death as the required one.

    `attempts_before` is written before the claim, and the claim increments it, so
    `attempts_before=MAX_ATTEMPTS - 1` reproduces the finding's exact interleaving:
    the effect commits on attempt three.
    """
    if attempts_before:
        with engine.begin() as connection:
            connection.execute(
                text("UPDATE reconciliation_jobs SET attempts = :n WHERE id = :id"),
                {"n": attempts_before, "id": apply_id},
            )
    with engine.begin() as connection:
        claimed = repository(connection).claim(owner=owner, now=utcnow())
    assert claimed is not None and claimed["id"] == apply_id

    executor = composition.executor()
    with engine.begin() as connection:
        services = composition.job_services(connection)
        snapshot_row = services.snapshots.snapshot(claimed["snapshot_id"])
        selection = services.snapshots.folder_selection(claimed["snapshot_id"])
        subject = services.accounts.discord_subject(claimed["requested_by_account_id"])
    executor.for_requester(int(subject), claimed["requested_by_account_id"]).execute(
        job=claimed,
        snapshot=snapshot_row,
        selection=selection,
        cancelled=lambda: False,
        owner=owner,
    )
    return claimed


def crashed_state(engine, apply_id, *, attempts):
    """Assert the window this whole module is about, before acting on it."""
    row = _row(engine, apply_id)
    assert row["state"] == JobState.RUNNING.value, "the publication never happened"
    assert row["effect_committed_at"] is not None, "but the effect did"
    assert row["effect_result"] is not None, (
        "and the fence made the publication durable with it"
    )
    assert row["result_id"] is None
    assert row["attempts"] == attempts
    return row


# ---------------------------------------------------------------------------
# Blocking defect 1 — cancellation over a committed effect
# ---------------------------------------------------------------------------


async def test_r45_refuses_to_cancel_an_effect_awaiting_recovery(
    client, settings, runtime, worker_composition, migrated_database, callers, snapshot
):
    """The finding's interleaving, end to end, through the route.

    1. the apply commits its import, characters, mapping, applied audit event and
       `effect_committed_at`;
    2. the process dies before publishing the job result;
    3. the lease expires and the **production reaper** runs;
    4. R-45 is issued **through the HTTP route** and is refused; and
    5. the job is not `cancelled`, `cancel_requested_at` was never written, and the
       next legitimate recovery completes it without a second effect.

    Step 3 is where this design differs from the handover's description. The
    reaper's two branches both assert that the attempt produced nothing, so it now
    declines the row entirely rather than requeueing it — which is what removes the
    `queued` window the finding's cancellation matched. The recovery state is the
    one the crash left: `running`, lease lapsed, no result.
    """
    _preview_id, apply_id = confirm(
        migrated_database, runtime, callers, snapshot
    )
    crash_after_the_effect(migrated_database, worker_composition, apply_id)
    assert effects(migrated_database) == ONE_APPLY
    crashed_state(migrated_database, apply_id, attempts=1)

    with migrated_database.begin() as connection:
        expire_lease(connection, apply_id)
    assert list(runtime.reap()) == [], "the reaper does not touch a committed effect"
    assert _row(migrated_database, apply_id)["state"] == JobState.RUNNING.value

    response = await _post(
        client, settings, callers["C"], f"/v1/council/jobs/{apply_id}/cancel", ""
    )
    assert response.status_code == 409, response.text
    assert "already_applied" in response.text, (
        "VM-19's word for a committed apply, not `stale_version` — which is what "
        "deriving the conflict from the job's `running` state produced"
    )

    row = _row(migrated_database, apply_id)
    assert row["state"] == JobState.RUNNING.value, "not cancelled"
    assert row["cancel_requested_at"] is None, "and no request was recorded"
    assert effects(migrated_database) == ONE_APPLY

    # No audit event claims the cancellation request succeeded.
    with migrated_database.begin() as connection:
        requests = connection.execute(
            text(
                "SELECT count(*) FROM audit_events "
                "WHERE action = 'reconciliation.job_cancel_requested' "
                "AND entity_id = :id"
            ),
            {"id": str(apply_id)},
        ).scalar_one()
    assert requests == 0

    # And the job is still recoverable, which is the other half of "refused".
    assert list(runtime.recover()) == [apply_id]
    assert _row(migrated_database, apply_id)["state"] == JobState.COMPLETED.value
    assert effects(migrated_database) == ONE_APPLY, "no second effect"
    assert published(migrated_database, apply_id) == {"results": 1, "completions": 1}


def test_the_queued_branch_of_r45_refuses_a_committed_effect(
    migrated_database, callers, snapshot
):
    """The predicate the finding named, asserted on the statement itself.

    No production statement can put a committed effect in `queued` any more — the
    reaper's requeue was the only one, and it now declines the row — so the state is
    seeded directly. That is deliberate: the finding is about *this statement's
    predicate*, and a case that could only reach it through a path this remediation
    deleted would stop being a regression the moment the path came back.

    Migration 0013 leaves `queued` representable for a committed effect on purpose
    (a re-executed attempt that finds its own import is wasteful, not wrong), so
    this is a state the schema permits and the cancellation must refuse.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            kind=JobKind.APPLY,
            state=JobState.QUEUED,
            attempts=1,
        )
        connection.execute(
            text(
                "UPDATE reconciliation_jobs SET effect_committed_at = now(), "
                "effect_result = '{\"summary\": {}, \"blocked_entries\": []}'::jsonb "
                "WHERE id = :id"
            ),
            {"id": job_id},
        )

    with migrated_database.begin() as connection:
        outcome = repository(connection).request_cancel(job_id=job_id, now=utcnow())

    assert outcome.accepted is False
    assert outcome.effect_committed is True
    assert outcome.conflict == "already_applied"
    row = _row(migrated_database, job_id)
    assert row["state"] == JobState.QUEUED.value, "not cancelled"
    assert row["cancel_requested_at"] is None, "and `cancel_requested_at` is not set"


def test_an_ordinary_queued_job_is_still_cancelled_outright(
    migrated_database, callers, snapshot
):
    """The predicate narrows nothing R-45 was for.

    The control for the case above: the same statement, the same transaction shape,
    a job with no committed effect — cancelled immediately, exactly as before.
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
        outcome = repository(connection).request_cancel(job_id=job_id, now=utcnow())

    assert outcome.accepted is True
    assert outcome.state is JobState.CANCELLED
    row = _row(migrated_database, job_id)
    assert row["state"] == JobState.CANCELLED.value
    assert row["cancel_requested_at"] is not None


def test_cancellation_and_invalidation_cannot_win_before_or_after_lease_expiry(
    runtime, worker_composition, migrated_database, callers, snapshot
):
    """Every statement that would deny the effect, on both sides of the expiry.

    The handover asks for R-45 and R-41/R-46 to be excluded "both before and after
    lease expiry", because a live lease and a lapsed one are different rows to
    every one of these predicates. The self-abandon is here too: it is the third
    writer, it carries the same predicate, and its `Abandonment` is what tells the
    worker "your effect committed" apart from "the reaper got there first".
    """
    snapshot_id, _checksum = snapshot
    _preview_id, apply_id = confirm(migrated_database, runtime, callers, snapshot)
    claimed = crash_after_the_effect(
        migrated_database, worker_composition, apply_id, owner="crashing:bbbb"
    )
    assert claimed["id"] == apply_id

    for phase in ("lease-live", "lease-expired"):
        if phase == "lease-expired":
            with migrated_database.begin() as connection:
                expire_lease(connection, apply_id)
        with migrated_database.begin() as connection:
            jobs = repository(connection)
            cancellation = jobs.request_cancel(job_id=apply_id, now=utcnow())
            withdrawn = jobs.mark_stale(
                job_id=apply_id, reason=StaleCode.FOLDER_CHANGED, now=utcnow()
            )
            invalidated = jobs.invalidate_for_snapshot(
                snapshot_id=snapshot_id, reason=StaleCode.FOLDER_CHANGED, now=utcnow()
            )
            abandonment = jobs.abandon(
                job_id=apply_id, owner="crashing:bbbb", now=utcnow()
            )
        assert cancellation.accepted is False, f"R-45 refused ({phase})"
        assert cancellation.effect_committed is True
        assert withdrawn is False, f"R-46's N-46 expiry refused ({phase})"
        assert apply_id not in invalidated, f"R-41's folder change refused ({phase})"
        assert abandonment.state is None, f"the self-abandon refused ({phase})"
        assert abandonment.effect_committed is True

        row = _row(migrated_database, apply_id)
        assert row["state"] == JobState.RUNNING.value, phase
        assert row["cancel_requested_at"] is None, phase
        assert row["stale_reason"] is None, phase
        assert row["failure_code"] is None, phase

    # Still recoverable after all of that, which is what "refused" has to mean.
    assert list(runtime.recover()) == [apply_id]
    assert _row(migrated_database, apply_id)["state"] == JobState.COMPLETED.value
    assert effects(migrated_database) == ONE_APPLY


# ---------------------------------------------------------------------------
# Blocking defect 2 — the reaper, the attempt cap, and the publication
# ---------------------------------------------------------------------------


def test_an_effect_committed_on_the_last_attempt_is_completed_not_failed(
    runtime, worker_composition, migrated_database, callers, snapshot
):
    """The finding, exactly: attempt three commits, the process dies, the lease lapses.

    Before the remediation the reaper read `attempts = 3`, took its exhaustion
    branch and wrote `failed` with `attempts_exhausted` over a durable import. Now
    it declines the row and `recover()` publishes it.

    `attempts` is still 3 afterwards, and no claim happened, so N-43 is neither
    spent nor disguised: the publication is not a fourth execution.
    """
    _preview_id, apply_id = confirm(migrated_database, runtime, callers, snapshot)
    crash_after_the_effect(
        migrated_database,
        worker_composition,
        apply_id,
        attempts_before=MAX_ATTEMPTS - 1,
    )
    crashed_state(migrated_database, apply_id, attempts=MAX_ATTEMPTS)

    with migrated_database.begin() as connection:
        expire_lease(connection, apply_id)
    assert list(runtime.reap()) == [], "the exhaustion branch does not fire"
    assert _row(migrated_database, apply_id)["state"] == JobState.RUNNING.value

    assert list(runtime.recover()) == [apply_id]

    row = _row(migrated_database, apply_id)
    assert row["state"] == JobState.COMPLETED.value, "not failed"
    assert row["failure_code"] is None
    assert row["attempts"] == MAX_ATTEMPTS, "and no fourth attempt was granted"
    assert row["lease_owner"] is None
    assert row["result_id"] is not None
    assert row["finished_at"] is not None
    assert effects(migrated_database) == ONE_APPLY
    assert published(migrated_database, apply_id) == {"results": 1, "completions": 1}


@pytest.mark.parametrize("attempts_before", [0, 1, MAX_ATTEMPTS - 1])
def test_the_reaper_leaves_a_committed_effect_for_publication_at_every_attempt_count(
    attempts_before,
    runtime,
    worker_composition,
    migrated_database,
    callers,
    snapshot,
):
    """Neither reaper branch may fire, whatever `attempts` says.

    Parameterised across the whole of N-43 because the finding was written against
    the cap and the *other* branch is just as wrong: requeueing a committed effect
    spends an attempt re-running work whose effect is already durable, and can end
    `stale` or `failed` for reasons that say nothing about the import.
    """
    _preview_id, apply_id = confirm(migrated_database, runtime, callers, snapshot)
    crash_after_the_effect(
        migrated_database,
        worker_composition,
        apply_id,
        attempts_before=attempts_before,
    )
    with migrated_database.begin() as connection:
        expire_lease(connection, apply_id)

    assert list(runtime.reap()) == []
    row = _row(migrated_database, apply_id)
    assert row["state"] == JobState.RUNNING.value
    assert row["attempts"] == attempts_before + 1
    assert row["failure_code"] is None


def test_an_expired_lease_with_no_committed_effect_is_still_reaped(
    runtime, migrated_database, callers, snapshot
):
    """The control: the reaper's ordinary branches are untouched.

    The predicate added to its locking sub-select must narrow it to committed
    effects and nothing else, so an ordinary expired attempt is still requeued and
    an exhausted one is still failed — both in the same pass.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        recoverable = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            state=JobState.RUNNING,
            attempts=1,
            lease_owner="dead:aaaa",
            lease_expires_at=utcnow(),
        )
        exhausted = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            state=JobState.RUNNING,
            attempts=MAX_ATTEMPTS,
            lease_owner="dead:bbbb",
            lease_expires_at=utcnow(),
        )
        expire_lease(connection, recoverable)
        expire_lease(connection, exhausted)

    assert set(runtime.reap()) == {recoverable, exhausted}
    assert _row(migrated_database, recoverable)["state"] == JobState.QUEUED.value
    failed = _row(migrated_database, exhausted)
    assert failed["state"] == JobState.FAILED.value
    assert failed["failure_code"] == "attempts_exhausted"


def test_the_recovered_result_names_the_original_import_and_says_it_was_recovered(
    runtime, worker_composition, migrated_database, callers, snapshot
):
    """Every published value comes from a row the effect's transaction wrote.

    The bounded summary is the one the commit fence stored in
    `reconciliation_jobs.effect_result`; the import identity and the committed
    counts are the immutable `snapshot_imports` receipt's own columns. Nothing is
    recomputed against the database as it stands now — which is Phase 2 finding
    B-1R's rule, applied to the job's result — and nothing comes from a caller.

    `duplicate` is `false` and `recovered` is `true`, which is the truthful pair:
    this job's own first and only effect wrote this import, and what was recovered
    is the *publication*, not the import.
    """
    _preview_id, apply_id = confirm(migrated_database, runtime, callers, snapshot)
    crash_after_the_effect(migrated_database, worker_composition, apply_id)
    stored = _row(migrated_database, apply_id)["effect_result"]

    assert list(runtime.recover()) == [], "a live lease is still the worker's to publish"
    with migrated_database.begin() as connection:
        expire_lease(connection, apply_id)
    assert list(runtime.recover()) == [apply_id]

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
        receipt = (
            connection.execute(text("SELECT * FROM snapshot_imports")).mappings().one()
        )
    summary = result["summary"]

    assert summary["import_id"] == str(receipt["id"]), "tied to the immutable receipt"
    assert summary["created_count"] == receipt["created_count"]
    assert summary["updated_count"] == receipt["updated_count"]
    assert summary["warning_count"] == receipt["warning_count"]
    assert summary["duplicate"] is False
    assert summary[RECOVERED_KEY] is True
    # And the bounded half is byte-for-byte what the fence made durable, so the
    # published summary and the one the dead process would have published differ
    # only by the five outcome keys and the marker.
    for key, value in stored["summary"].items():
        assert summary[key] == value, key
    assert result["blocked_entries"] == stored["blocked_entries"]

    # The completion event says the same thing, from the same summary.
    with migrated_database.begin() as connection:
        event = (
            connection.execute(
                text(
                    "SELECT payload FROM audit_events "
                    "WHERE entity_id = :id AND action = 'reconciliation.apply_completed'"
                ),
                {"id": str(apply_id)},
            )
            .mappings()
            .one()
        )["payload"]
    assert event[RECOVERED_KEY] is True
    assert event["recovery_reason"] == "effect_committed_unpublished"
    assert event["import_id"] == str(receipt["id"])
    assert event["attempts"] == 1
    assert event["lease_owner"] == "crashing:aaaa", (
        "the lease that stopped answering, so an operator can find the process"
    )
    assert "checksum" in event and "actor_count" in event


def test_repeated_recovery_passes_publish_once(
    runtime, worker_composition, migrated_database, callers, snapshot
):
    """Idempotent by state, not by a flag somebody has to remember to set.

    After the first pass the job is `completed`, and `lock_unpublished_effect`
    selects only `running` rows — so the second, third and fourth passes find
    nothing and write nothing. The reaper is run alongside them because a
    `completed` job must not become interesting to it either.
    """
    _preview_id, apply_id = confirm(migrated_database, runtime, callers, snapshot)
    crash_after_the_effect(migrated_database, worker_composition, apply_id)
    with migrated_database.begin() as connection:
        expire_lease(connection, apply_id)

    assert list(runtime.recover()) == [apply_id]
    for _ in range(3):
        assert list(runtime.recover()) == []
        assert list(runtime.reap()) == []

    assert published(migrated_database, apply_id) == {"results": 1, "completions": 1}
    assert effects(migrated_database) == ONE_APPLY


def test_two_recovery_passes_serialize_to_one_publication(
    runtime, worker_composition, migrated_database, callers, snapshot
):
    """`FOR UPDATE SKIP LOCKED`, driven by a lock rather than by a schedule.

    A second connection takes the row lock through the **production** selecting
    statement and holds it. A concurrent recovery therefore skips the row, finds
    nothing to publish and writes nothing — rather than blocking and then inserting
    a second result behind the first. When the lock is released the row is
    published exactly once.

    This is a lock, not a race: no case here depends on which of two threads the
    scheduler happens to run first.
    """
    _preview_id, apply_id = confirm(migrated_database, runtime, callers, snapshot)
    crash_after_the_effect(migrated_database, worker_composition, apply_id)
    with migrated_database.begin() as connection:
        expire_lease(connection, apply_id)

    holder = migrated_database.connect()
    transaction = holder.begin()
    try:
        locked = repository(holder).lock_unpublished_effect()
        assert locked is not None and locked["id"] == apply_id
        assert list(runtime.recover()) == [], "the concurrent pass skipped the row"
        assert published(migrated_database, apply_id) == {
            "results": 0,
            "completions": 0,
        }
    finally:
        transaction.rollback()
        holder.close()

    assert list(runtime.recover()) == [apply_id]
    assert published(migrated_database, apply_id) == {"results": 1, "completions": 1}


def test_concurrent_recovery_threads_publish_exactly_one_result(
    runtime, worker_composition, worker_settings, migrated_database, callers, snapshot
):
    """Two real workers, two real connections, one publication.

    The invariant rather than the ordering: whichever runtime reaches the row
    first, the other must produce no second result row and no second completion
    event. Both are production `WorkerRuntime`s over the production composition.
    """
    _preview_id, apply_id = confirm(migrated_database, runtime, callers, snapshot)
    crash_after_the_effect(migrated_database, worker_composition, apply_id)
    with migrated_database.begin() as connection:
        expire_lease(connection, apply_id)

    second = WorkerRuntime(
        composition=worker_composition,
        worker_settings=worker_composition.worker,
        bounds=worker_settings.bounds,
        guild_id=worker_settings.discord.guild_id,
        instance="test-host/2",
    )
    outcomes: list = []
    barrier = threading.Barrier(2, timeout=30)

    def publish(which) -> None:
        barrier.wait()
        outcomes.append(tuple(which.recover()))

    threads = [
        threading.Thread(target=publish, args=(runtime,), name="recover-1"),
        threading.Thread(target=publish, args=(second,), name="recover-2"),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=60)
        assert not thread.is_alive()

    assert sorted(len(outcome) for outcome in outcomes) == [0, 1], (
        "exactly one of the two published it"
    )
    assert published(migrated_database, apply_id) == {"results": 1, "completions": 1}
    assert effects(migrated_database) == ONE_APPLY
    assert _row(migrated_database, apply_id)["state"] == JobState.COMPLETED.value


def test_an_audit_failure_during_recovery_rolls_the_publication_back(
    runtime, worker_composition, migrated_database, callers, snapshot
):
    """The result, the state change and the event are one transaction, proved in the database.

    Injected as a real `BEFORE INSERT` trigger on `audit_events` rather than as a
    patched Python object, so what is proved is that PostgreSQL takes the result row
    and the completion down with the event — the property the platform relies on.

    The trigger is committed rather than session-local because the recovery runs on
    its own connection from the worker's pool, which is the whole point of the case:
    a failure in *that* transaction must leave the job exactly as recoverable as it
    was, and the retry after the trigger is dropped must then succeed.
    """
    _preview_id, apply_id = confirm(migrated_database, runtime, callers, snapshot)
    crash_after_the_effect(migrated_database, worker_composition, apply_id)
    with migrated_database.begin() as connection:
        expire_lease(connection, apply_id)

    with migrated_database.begin() as connection:
        connection.execute(
            text(
                "CREATE FUNCTION refuse_recovery_audit() RETURNS trigger AS $$ "
                "BEGIN RAISE EXCEPTION 'injected audit failure'; END; $$ "
                "LANGUAGE plpgsql"
            )
        )
        connection.execute(
            text(
                "CREATE TRIGGER injected_recovery_audit_failure "
                "BEFORE INSERT ON audit_events "
                "FOR EACH ROW EXECUTE FUNCTION refuse_recovery_audit()"
            )
        )
    try:
        with pytest.raises(Exception, match="injected audit failure"):
            runtime.recover()

        row = _row(migrated_database, apply_id)
        assert row["state"] == JobState.RUNNING.value, "the transition rolled back"
        assert row["result_id"] is None
        assert row["effect_committed_at"] is not None
        assert published(migrated_database, apply_id) == {
            "results": 0,
            "completions": 0,
        }, "the result row went with the event"
    finally:
        with migrated_database.begin() as connection:
            connection.execute(
                text(
                    "DROP TRIGGER injected_recovery_audit_failure ON audit_events"
                )
            )
            connection.execute(text("DROP FUNCTION refuse_recovery_audit()"))

    # Safely retryable: the same pass, on the same row, with nothing cleaned up.
    assert list(runtime.recover()) == [apply_id]
    assert published(migrated_database, apply_id) == {"results": 1, "completions": 1}
    assert effects(migrated_database) == ONE_APPLY


def test_a_live_lease_is_left_to_the_worker_that_holds_it(
    runtime, worker_composition, migrated_database, callers, snapshot
):
    """Recovery is what happens *after* the lease lapses, and not before.

    While the lease is alive the process that ran the attempt may still publish —
    that is what `EFFECT_PUBLICATION_GRACE_HEARTBEATS` is for — so the platform
    publishing on its behalf would be two writers for one result. The predicate
    `lease_expires_at < now()` is what keeps them apart.
    """
    _preview_id, apply_id = confirm(migrated_database, runtime, callers, snapshot)
    crash_after_the_effect(migrated_database, worker_composition, apply_id)

    assert list(runtime.recover()) == []
    assert published(migrated_database, apply_id) == {"results": 0, "completions": 0}
    assert _row(migrated_database, apply_id)["state"] == JobState.RUNNING.value


def test_a_tick_recovers_even_while_the_worker_is_stalled(
    runtime, worker_composition, worker_settings, migrated_database, callers, snapshot
):
    """A Council member owed a receipt does not wait for this worker to be healthy.

    `tick` runs the reaper and the recovery before it consults the kill switch and
    before it consults its own outstanding threads, because neither of those is a
    reason to withhold the result of an import that has already committed.

    The stalled worker is a **second** runtime rather than the one that seeded the
    fixtures, so its reaper interval has never fired and the tick under test is its
    first — a case that reset another runtime's `_last_reap` would be a case about
    the interval rather than about the stall.
    """
    from application.worker.runtime import _Attempt

    _preview_id, apply_id = confirm(migrated_database, runtime, callers, snapshot)
    crash_after_the_effect(migrated_database, worker_composition, apply_id)
    with migrated_database.begin() as connection:
        expire_lease(connection, apply_id)

    stalled = WorkerRuntime(
        composition=worker_composition,
        worker_settings=worker_composition.worker,
        bounds=worker_settings.bounds,
        guild_id=worker_settings.discord.guild_id,
        instance="test-host/2",
    )
    release = threading.Event()
    thread = threading.Thread(target=release.wait, kwargs={"timeout": 30})
    thread.start()
    stalled._outstanding.append(
        _Attempt(
            job_id=None,
            owner="test-host/2:dead",
            thread=thread,
            finished=threading.Event(),
            cancel=threading.Event(),
            box={},
            released_for="timeout",
        )
    )
    try:
        tick = stalled.tick()
    finally:
        release.set()
        thread.join(timeout=30)

    assert tick.outcome == "attempt_outstanding", "the worker still claims nothing"
    assert list(tick.recovered) == [apply_id], "and still publishes what it owes"
    assert _row(migrated_database, apply_id)["state"] == JobState.COMPLETED.value


# ---------------------------------------------------------------------------
# The constraints, falsified rather than assumed
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("state", "extra"),
    [
        ("failed", "failure_code = 'attempts_exhausted', finished_at = now()"),
        ("cancelled", "finished_at = now()"),
        ("stale", "stale_reason = 'folder_changed', finished_at = now()"),
    ],
)
def test_direct_sql_cannot_write_a_state_that_denies_a_committed_effect(
    state, extra, runtime, worker_composition, migrated_database, callers, snapshot
):
    """`committed_effect_is_never_denied`, tried rather than trusted.

    The application statements all carry the matching predicate, so they refuse.
    This is the other half of the guarantee: a statement that did **not** carry it —
    a future edit, an operator at `psql` with the runtime role, a path nobody
    thought of — is refused by PostgreSQL rather than quietly writing a job that
    denies a durable import.
    """
    _preview_id, apply_id = confirm(migrated_database, runtime, callers, snapshot)
    crash_after_the_effect(migrated_database, worker_composition, apply_id)

    with pytest.raises(IntegrityError, match="committed_effect_is_never_denied"):
        with migrated_database.begin() as connection:
            connection.execute(
                text(
                    f"UPDATE reconciliation_jobs SET state = '{state}', {extra}, "
                    "lease_owner = NULL, lease_expires_at = NULL, "
                    "heartbeat_at = NULL WHERE id = :id"
                ),
                {"id": apply_id},
            )

    assert _row(migrated_database, apply_id)["state"] == JobState.RUNNING.value
    assert effects(migrated_database) == ONE_APPLY


def test_an_ordinary_job_still_reaches_every_terminal_state(
    migrated_database, callers, snapshot
):
    """The control for the constraint: it forbids nothing a live job may do.

    A job with no committed effect — which is every preview and every apply that
    has not applied — reaches `failed`, `cancelled` and `stale` exactly as before.
    """
    snapshot_id, checksum = snapshot
    for state, extra in (
        ("failed", "failure_code = 'internal'"),
        ("cancelled", ""),
        ("stale", "stale_reason = 'folder_changed'"),
    ):
        with migrated_database.begin() as connection:
            job_id = seed_job(
                connection,
                snapshot_id=snapshot_id,
                account_id=callers["C"].account_id,
                checksum=checksum,
            )
            connection.execute(
                text(
                    f"UPDATE reconciliation_jobs SET state = '{state}', "
                    f"finished_at = now(){', ' + extra if extra else ''} "
                    "WHERE id = :id"
                ),
                {"id": job_id},
            )
        assert _row(migrated_database, job_id)["state"] == state


def test_a_committed_effect_cannot_be_recorded_without_its_publication(
    migrated_database, callers, snapshot
):
    """`effect_result_accompanies_the_fence`, in both directions.

    The fence writes both columns in one statement, so this constraint is what makes
    "an effect whose publication cannot be reconstructed from durable data" an
    unrepresentable row rather than a code path nobody has taken yet.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            kind=JobKind.APPLY,
            state=JobState.RUNNING,
            attempts=1,
            lease_owner="worker:aaaa",
            lease_expires_at=utcnow(),
        )

    with pytest.raises(IntegrityError, match="effect_result_accompanies_the_fence"):
        with migrated_database.begin() as connection:
            connection.execute(
                text(
                    "UPDATE reconciliation_jobs SET effect_committed_at = now() "
                    "WHERE id = :id"
                ),
                {"id": job_id},
            )

    with pytest.raises(IntegrityError, match="effect_result_accompanies_the_fence"):
        with migrated_database.begin() as connection:
            connection.execute(
                text(
                    "UPDATE reconciliation_jobs SET effect_result = '{}'::jsonb "
                    "WHERE id = :id"
                ),
                {"id": job_id},
            )
