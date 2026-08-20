"""The worker: real artifacts, a real lease, a real apply, and the races round it.

This is where the package stops being a queue and becomes an import. Every case
runs the **actual** Phase 2 `SnapshotImportService` against a real
`FilesystemArtifactStore` and real PostgreSQL, because the properties that matter
— one durable effect under retry, a scope re-checked at the commit, an
authorization re-resolved at the commit — are properties of that service and its
constraints rather than of anything this package added.

**No live service and no real player data.** The artifacts are the synthetic
Phase 2 bundles; the accounts, subjects and guild are the synthetic ones the
portal suites already use.

## Why the loop is driven a tick at a time

`WorkerRuntime.tick()` returns what it did. A test that started the loop and
slept would be slow, would occasionally pass for the wrong reason, and could not
say *which* pass produced the outcome it asserts.
"""
from __future__ import annotations

import threading
from dataclasses import replace
from datetime import timedelta

import pytest
from sqlalchemy import text

from adapters.web.repositories import ReconciliationJobRepository
from adapters.worker.composition import WorkerComposition
from application.foundry.artifact import ingest_bytes
from application.web.config import ProcessRole, WebSettings
from application.web.jobs import JobKind, JobState, scope_fingerprint
from application.worker.runtime import WorkerRuntime
from tests import foundry_fixtures as fx
from tests.web.p3_3_fixtures import (
    FIXTURE_FOLDER_PATH,
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
from tests.web.portal_fixtures import (
    COUNCIL_SUBJECT,
    clean_p3_2_tables,
    seed_callers,
)
from tests.web_fixtures import web_environment

pytestmark = pytest.mark.database

LEASE_SECONDS = 60
MAX_ATTEMPTS = 3


@pytest.fixture()
def artifact_root(tmp_path):
    return tmp_path / "artifacts"


@pytest.fixture()
def worker_settings(tmp_path, artifact_root) -> WebSettings:
    """The web graph, with the one variable that distinguishes a worker flipped.

    `WORKER_ENABLED=true` is refused by the web process (S-11) and **required**
    by this one. Both processes run the same code from the same virtualenv, and
    each refuses the other's value — which is the whole of the topology's "they
    differ by one variable".
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
def composition(worker_settings, stored, migrated_database, bounded_ancestors):
    """A production `WorkerComposition`, lending it the suite's engine.

    The engine is lent rather than built so the case and the worker see one
    database and one transaction timeline. Everything else — the artifact store,
    the import service, the authorization port — is the production construction.
    """
    composition = WorkerComposition(
        worker_settings, engine=migrated_database, ancestors=bounded_ancestors
    )
    try:
        yield composition
    finally:
        composition.close()


@pytest.fixture()
def runtime(composition, worker_settings):
    return WorkerRuntime(
        composition=composition,
        worker_settings=composition.worker,
        bounds=worker_settings.bounds,
        guild_id=worker_settings.discord.guild_id,
        instance="test-host/1",
    )


@pytest.fixture()
def callers(migrated_database, worker_settings):
    yield seed_callers(migrated_database, worker_settings, states=("C", "A"))
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


def repository(connection):
    return ReconciliationJobRepository(
        connection, lease_seconds=LEASE_SECONDS, max_attempts=MAX_ATTEMPTS
    )


def _row(engine, job_id):
    with engine.begin() as connection:
        return job_row(connection, job_id)


# ---------------------------------------------------------------------------
# The startup refusals
# ---------------------------------------------------------------------------


def test_s11_reads_both_ways_and_neither_process_can_take_the_others_value(
    tmp_path, artifact_root
):
    """One variable, two refusals, and neither is satisfiable by accident.

    S-11 is a statement about the **web** process, and until P3.3 it was enforced
    unconditionally at the one environment reader — which was right while there
    was only one process and would have made the worker unable to read its own
    configuration at all. It is now symmetric rather than relaxed: each process
    refuses the other's value, both under `S-11`, both naming the variable and
    neither echoing it.
    """
    from application.web.config import ConfigurationError

    web_with_worker = web_environment(
        tmp_path, WORKER_ENABLED="true", WORKER_ARTIFACT_ROOT=str(artifact_root)
    )
    worker_without_worker = web_environment(
        tmp_path, WORKER_ENABLED="false", WORKER_ARTIFACT_ROOT=str(artifact_root)
    )

    with pytest.raises(ConfigurationError) as web_refusal:
        WebSettings.from_environment(web_with_worker)
    with pytest.raises(ConfigurationError) as worker_refusal:
        WebSettings.from_environment(
            worker_without_worker, process=ProcessRole.WORKER
        )

    for refusal in (web_refusal, worker_refusal):
        rendered = refusal.value.render()
        assert "S-11" in rendered
        assert "WORKER_ENABLED" in rendered
        # The refusal names the variable and never the value it held.
        assert "true" not in rendered.replace("must be true", "")

    # And each is accepted by the process it belongs to.
    assert WebSettings.from_environment(worker_without_worker).worker.enabled is False
    assert (
        WebSettings.from_environment(
            web_with_worker, process=ProcessRole.WORKER
        ).worker.enabled
        is True
    )


def test_the_worker_composition_refuses_a_web_graph_independently(
    tmp_path, artifact_root
):
    """The second control, at the composition rather than at the reader.

    A `WebSettings` built for the web process — legitimately, with
    `WORKER_ENABLED=false` — must not become a worker by being handed to one.
    The reader cannot catch that: the graph is already valid. This can.
    """
    from application.web.config import ConfigurationError

    settings = WebSettings.from_environment(
        web_environment(
            tmp_path, WORKER_ENABLED="false", WORKER_ARTIFACT_ROOT=str(artifact_root)
        )
    )
    with pytest.raises(ConfigurationError) as refusal:
        WorkerComposition(settings)
    assert "S-11" in refusal.value.render()
    assert "WORKER_ENABLED" in refusal.value.render()


def test_a_worker_refuses_to_start_without_an_artifact_root(tmp_path):
    """S-12. The worker is the process that reads artifacts.

    Without a root, every job would fail with `artifact_unavailable` — a refusal
    about the artifact rather than about the configuration that was never set,
    which is exactly the misdiagnosis a startup refusal exists to prevent.
    """
    from application.web.config import ConfigurationError

    settings = WebSettings.from_environment(
        web_environment(tmp_path, WORKER_ENABLED="true"), process=ProcessRole.WORKER
    )
    with pytest.raises(ConfigurationError) as refusal:
        WorkerComposition(settings)
    assert "S-12" in refusal.value.render()
    assert "WORKER_ARTIFACT_ROOT" in refusal.value.render()


# ---------------------------------------------------------------------------
# The preview
# ---------------------------------------------------------------------------


def test_a_preview_job_runs_and_publishes_a_bounded_result(
    runtime, migrated_database, callers, snapshot
):
    """The whole preview path, end to end, against a real artifact.

    The result is a bounded summary and the job's scope fingerprint is
    **rewritten** to the scope the run observed — the aggregate versions folded
    in — in the same transaction that publishes it. Before the run the
    fingerprint covers the checksum, folder and profile version with the
    aggregate component `unobserved`; a `completed` preview can therefore never
    carry the unobserved scope.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
    before = _row(migrated_database, job_id)["scope_fingerprint"]

    tick = runtime.tick()
    assert tick.claimed == job_id
    assert tick.outcome == "completed"

    row = _row(migrated_database, job_id)
    assert row["state"] == "completed"
    assert row["result_id"] is not None
    assert row["attempts"] == 1
    assert row["lease_owner"] is None
    assert bytes(row["scope_fingerprint"]) != bytes(before)
    assert bytes(row["scope_fingerprint"]) != bytes(
        scope_fingerprint(
            checksum=checksum,
            folder_id=fx.ACTIVE_FOLDER_ID,
            folder_path=FIXTURE_FOLDER_PATH,
            profile_version="2026-08-09.1",
        )
    )

    with migrated_database.begin() as connection:
        result = (
            connection.execute(
                text("SELECT * FROM reconciliation_job_results WHERE job_id = :job"),
                {"job": job_id},
            )
            .mappings()
            .one()
        )
    summary = result["summary"]
    assert summary["checksum"] == checksum
    assert summary["actors"] == 1
    assert summary["unmapped"] == 1
    assert summary["preview_token"]
    # And nothing artifact-derived: no Actor name, no field value, no bytes.
    assert "Aurelia" not in str(summary)
    assert result["blocked_entries"] == []


def test_a_preview_result_carries_no_issue_message_only_codes(
    runtime, migrated_database, callers, snapshot
):
    """§3.3, enforced where the record is **built** rather than where it renders.

    An issue's message quotes Actor data, so the only reliable place to remove it
    is before it is stored — which is what makes "artifact text never reaches a
    response" a property of the row instead of a property of a template nobody
    forgot to change.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
    runtime.tick()
    with migrated_database.begin() as connection:
        summary = connection.execute(
            text("SELECT summary FROM reconciliation_job_results")
        ).scalar_one()
    for entry in summary["issue_counts"]:
        assert set(entry) == {"code", "severity", "count"}
        assert isinstance(entry["count"], int)


def test_an_absent_artifact_fails_deterministically_without_consuming_attempts(
    runtime, migrated_database, callers, stored
):
    """A refusal that would recur on every attempt is failed **immediately**.

    Retrying `artifact_unavailable` three times is thirty seconds of work to
    reach the conclusion the first attempt already had. `attempts` stays at 1
    because one claim was made — the counter means claims, and the job is
    terminal after that one.
    """
    _store, _checksum, _payload = stored
    with migrated_database.begin() as connection:
        # A snapshot whose bytes were never stored.
        snapshot_id, missing = seed_snapshot(
            connection, payload=snapshot_bytes(exported_at="2026-08-04T09:15:00Z")
        )
        select_folder(
            connection, snapshot_id=snapshot_id, account_id=callers["A"].account_id
        )
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=missing,
        )
    tick = runtime.tick()
    assert tick.outcome == "failed"
    row = _row(migrated_database, job_id)
    assert row["state"] == "failed"
    assert row["failure_code"] == "artifact_unavailable"
    assert row["attempts"] == 1


# ---------------------------------------------------------------------------
# The apply
# ---------------------------------------------------------------------------


def _confirm(migrated_database, runtime, callers, snapshot):
    """Run the preview, then enqueue its apply the way R-46 does. Returns both ids."""
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        preview_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
    assert runtime.tick().outcome == "completed"
    preview = _row(migrated_database, preview_id)
    with migrated_database.begin() as connection:
        apply_id = repository(connection).insert(
            kind=JobKind.APPLY,
            snapshot_id=snapshot_id,
            folder_id=preview["folder_id"],
            profile_version=preview["profile_version"],
            # Inherited, exactly as `enqueue_apply` inherits it.
            fingerprint=bytes(preview["scope_fingerprint"]),
            requested_by_account_id=callers["C"].account_id,
            requested_capability=_council(),
            request_key=f"p3.3:apply:{apply_id_seed()}",
            parent_job_id=preview_id,
            correlation_id=preview["correlation_id"],
            now=utcnow(),
        )
    return preview_id, apply_id


def apply_id_seed() -> str:
    from uuid import uuid4

    return uuid4().hex


def _council():
    from application.audit import ActorCapability

    return ActorCapability.GUILD_COUNCIL


def test_an_apply_job_commits_one_import_and_one_audit_event(
    runtime, migrated_database, callers, snapshot
):
    """The apply, through the **existing** `SnapshotImportService.apply`.

    One `snapshot_imports` row, the character the reconciliation said it would
    create, and the audit event the import service writes in the same
    transaction. Nothing here reimplements any of that: the job model decides
    *when* the service runs and records the outcome.
    """
    _preview_id, apply_id = _confirm(migrated_database, runtime, callers, snapshot)
    tick = runtime.tick()
    assert tick.claimed == apply_id
    assert tick.outcome == "completed", tick.outcome

    with migrated_database.begin() as connection:
        imports = (
            connection.execute(text("SELECT * FROM snapshot_imports")).mappings().all()
        )
        characters = connection.execute(
            text("SELECT count(*) FROM characters")
        ).scalar_one()
    assert len(imports) == 1
    assert imports[0]["status"] == "applied"
    assert imports[0]["actor_capability"] == "guild_council"
    assert imports[0]["actor_account_id"] == callers["C"].account_id
    assert characters == 1


def test_a_retried_apply_finds_the_existing_import_and_creates_nothing_new(
    runtime, migrated_database, callers, snapshot
):
    """TC-JOB-04's *exactly one durable effect*, under a genuine re-execution.

    The job is put back to `queued` after it committed — which is what a crash
    between the commit and the state publication looks like — and run again. The
    durable effect is fenced by `uq_snapshot_imports_applied_input` and
    `snapshot_imports.request_key`, **not** by the job's state, so the second
    execution finds the existing import and returns it as a duplicate.
    """
    _preview_id, apply_id = _confirm(migrated_database, runtime, callers, snapshot)
    assert runtime.tick().outcome == "completed"

    with migrated_database.begin() as connection:
        first = (
            connection.execute(text("SELECT id, request_key FROM snapshot_imports"))
            .mappings()
            .one()
        )
        # The crash: the effect committed, the job's state did not.
        connection.execute(
            text(
                "UPDATE reconciliation_jobs SET state = 'queued', result_id = NULL, "
                "finished_at = NULL, attempts = 1 WHERE id = :id"
            ),
            {"id": apply_id},
        )
        connection.execute(
            text("DELETE FROM reconciliation_job_results WHERE job_id = :id"),
            {"id": apply_id},
        )

    second = runtime.tick()
    assert second.claimed == apply_id
    assert second.outcome == "completed"

    with migrated_database.begin() as connection:
        imports = (
            connection.execute(text("SELECT id FROM snapshot_imports")).mappings().all()
        )
        characters = connection.execute(
            text("SELECT count(*) FROM characters")
        ).scalar_one()
        summary = connection.execute(
            text(
                "SELECT summary FROM reconciliation_job_results WHERE job_id = :id"
            ),
            {"id": apply_id},
        ).scalar_one()
    assert len(imports) == 1, "exactly one durable effect"
    assert imports[0]["id"] == first["id"]
    assert characters == 1
    assert summary["duplicate"] is True, "and the second run says it was a retry"


def test_a_moved_scope_is_detected_inside_the_attempt_and_applies_nothing(
    runtime, migrated_database, callers, snapshot
):
    """The one equality comparison, where the write happens.

    The apply recomputes the fingerprint from the artifact in hand and the
    database as it stands *now*, and compares it to the scope the confirmation
    inherited. A mismatch applies nothing and names what moved — so the Council
    member is told *what* changed rather than that something did.
    """
    _preview_id, apply_id = _confirm(migrated_database, runtime, callers, snapshot)
    with migrated_database.begin() as connection:
        # A character this import would touch moves underneath it: the aggregate
        # versions change, and nothing else does.
        connection.execute(
            text(
                "UPDATE reconciliation_jobs SET scope_fingerprint = :moved "
                "WHERE id = :id"
            ),
            {"moved": b"\x11" * 32, "id": apply_id},
        )
    tick = runtime.tick()
    assert tick.outcome == "stale"
    row = _row(migrated_database, apply_id)
    assert row["state"] == "stale"
    assert row["stale_reason"] == "aggregate_version_changed"
    with migrated_database.begin() as connection:
        imports = connection.execute(
            text("SELECT count(*) FROM snapshot_imports")
        ).scalar_one()
        characters = connection.execute(
            text("SELECT count(*) FROM characters")
        ).scalar_one()
    assert imports == 0
    assert characters == 0


def test_council_revoked_after_the_confirmation_refuses_the_apply_at_the_commit(
    runtime, migrated_database, callers, snapshot
):
    """SM-05: `SnapshotImportService.apply` re-resolves through `AuthorizationPort`.

    R-46 already refuses a caller who is no longer Council — that is asserted at
    the route. This is the *other* window: authority revoked **after** the job
    was enqueued, when no request is involved at all. The worker resolves it at
    the commit, and the apply is refused.
    """
    from sqlalchemy import delete

    from adapters.database.tables import discord_membership_roles

    _preview_id, apply_id = _confirm(migrated_database, runtime, callers, snapshot)
    with migrated_database.begin() as connection:
        connection.execute(
            delete(discord_membership_roles).where(
                discord_membership_roles.c.discord_user_id == COUNCIL_SUBJECT
            )
        )
    tick = runtime.tick()
    assert tick.outcome == "stale"
    row = _row(migrated_database, apply_id)
    assert row["stale_reason"] == "authorization_changed"
    with migrated_database.begin() as connection:
        applied = connection.execute(
            text("SELECT count(*) FROM snapshot_imports WHERE status = 'applied'")
        ).scalar_one()
        characters = connection.execute(
            text("SELECT count(*) FROM characters")
        ).scalar_one()
    assert applied == 0
    assert characters == 0


def test_a_stale_membership_observation_refuses_the_apply(
    runtime, migrated_database, callers, snapshot
):
    """N-10, at the mutation. The worker performs **no provider I/O**.

    A mutation gets no grace: it is refused the moment the platform cannot
    confirm the caller's current roles. The worker has no event loop and no OAuth
    transport, so a projection older than N-09 is not something it can refresh —
    and failing closed is the correct direction, stricter than the web path
    rather than looser.
    """
    from tests.web.portal_fixtures import stale_membership

    _preview_id, apply_id = _confirm(migrated_database, runtime, callers, snapshot)
    with migrated_database.begin() as connection:
        stale_membership(connection, subject=COUNCIL_SUBJECT, minutes=60)
    tick = runtime.tick()
    assert tick.outcome == "stale"
    assert _row(migrated_database, apply_id)["stale_reason"] == "authorization_changed"
    with migrated_database.begin() as connection:
        applied = connection.execute(
            text("SELECT count(*) FROM snapshot_imports WHERE status = 'applied'")
        ).scalar_one()
    assert applied == 0


# ---------------------------------------------------------------------------
# Cancellation, the kill switch and restart
# ---------------------------------------------------------------------------


def test_the_kill_switch_stops_the_worker_claiming_new_work(
    composition, worker_settings, migrated_database, callers, snapshot
):
    """Operator kill switch, layer 1, in the worker.

    Claim no new work, and leave the bot and Foundry entirely alone. The job
    stays `queued` — not failed, not cancelled — because a switch an operator
    threw is not a verdict on the work.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
    engaged = WorkerRuntime(
        composition=composition,
        worker_settings=composition.worker,
        bounds=worker_settings.bounds,
        guild_id=worker_settings.discord.guild_id,
        instance="test-host/1",
        kill_switch=lambda: True,
    )
    tick = engaged.tick()
    assert tick.claimed is None
    assert tick.outcome == "kill_switch"
    assert _row(migrated_database, job_id)["state"] == "queued"


def test_a_cancellation_requested_before_the_claim_stops_the_job_being_claimed(
    runtime, migrated_database, callers, snapshot
):
    """The claim predicate excludes `cancel_requested_at IS NOT NULL`.

    A queued job the route already cancelled is `cancelled`, so this is the
    narrower case: a cancellation recorded on a job that was requeued by the
    reaper must not be restarted by the next claim.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            attempts=1,
        )
        connection.execute(
            text(
                "UPDATE reconciliation_jobs SET cancel_requested_at = now() "
                "WHERE id = :id"
            ),
            {"id": job_id},
        )
    tick = runtime.tick()
    assert tick.claimed is None
    assert _row(migrated_database, job_id)["state"] == "queued"


def test_a_worker_crash_after_the_effect_commits_leaves_one_effect_and_a_readable_job(
    runtime, migrated_database, callers, snapshot
):
    """TC-JOB-04's hardest ordering: the commit landed, the publication did not.

    The lease expires and the platform publishes the result the dead process owed,
    from the payload the commit fence made durable inside the effect's own
    transaction. **Exactly one** durable effect exists, and the Council member ends
    up looking at a terminal job with a result rather than at a spinner over a job
    nobody is running.

    **The intermediate state changed on 2026-08-18** with the effect-publication
    remediation: the reaper used to requeue this job and a re-execution used to
    produce the result as a duplicate. That spent one of N-43's three attempts,
    had none to spend when the effect committed on attempt three — where the reaper
    wrote `failed` over the import instead — and could end `stale` or `failed` for
    reasons that said nothing about what had committed. The reaper now declines an
    expired lease over a committed effect and `recover()` publishes it.
    `tests/web/test_p3_3_effect_recovery.py` is that design's own suite; this case
    keeps the first-attempt coverage where TC-JOB-04 asks for it.
    """
    _preview_id, apply_id = _confirm(migrated_database, runtime, callers, snapshot)

    # Attempt 1 commits the import and then "crashes": the job is left `running`
    # with a lease nobody will renew.
    with migrated_database.begin() as connection:
        claimed = repository(connection).claim(owner="crashing:aaaa", now=utcnow())
    assert claimed is not None and claimed["id"] == apply_id
    executor = runtime._composition.executor()
    with migrated_database.begin() as connection:
        services = runtime._composition.job_services(connection)
        snapshot_row = services.snapshots.snapshot(claimed["snapshot_id"])
        selection = services.snapshots.folder_selection(claimed["snapshot_id"])
        subject = services.accounts.discord_subject(claimed["requested_by_account_id"])
    executor.for_requester(int(subject), claimed["requested_by_account_id"]).execute(
        job=claimed,
        snapshot=snapshot_row,
        selection=selection,
        cancelled=lambda: False,
        # This claim's own fencing token, because the effect's commit fence
        # proves it inside the transaction that commits — an attempt that could
        # run without one could commit an effect nothing entitles it to.
        owner="crashing:aaaa",
    )
    with migrated_database.begin() as connection:
        committed = connection.execute(
            text("SELECT count(*) FROM snapshot_imports WHERE status = 'applied'")
        ).scalar_one()
    assert committed == 1, "the effect landed before the crash"

    # The lease expires; the reaper leaves it alone; the platform publishes it.
    with migrated_database.begin() as connection:
        expire_lease(connection, apply_id)
    assert list(runtime.reap()) == [], "an expired committed effect is not an expiry"
    assert _row(migrated_database, apply_id)["state"] == "running"

    assert list(runtime.recover()) == [apply_id]
    assert _row(migrated_database, apply_id)["attempts"] == 1, "no attempt was spent"
    assert _row(migrated_database, apply_id)["state"] == "completed"

    with migrated_database.begin() as connection:
        imports = connection.execute(
            text("SELECT count(*) FROM snapshot_imports WHERE status = 'applied'")
        ).scalar_one()
        characters = connection.execute(
            text("SELECT count(*) FROM characters")
        ).scalar_one()
        summary = connection.execute(
            text("SELECT summary FROM reconciliation_job_results WHERE job_id = :id"),
            {"id": apply_id},
        ).scalar_one()
    assert imports == 1, "exactly one durable effect"
    assert characters == 1
    assert summary["recovered"] is True, "published by the platform, not by the worker"
    assert summary["duplicate"] is False, (
        "and not a duplicate of anything: this job's own first and only effect "
        "wrote this import"
    )


def test_a_lost_lease_publishes_nothing(
    runtime, migrated_database, callers, snapshot
):
    """A worker whose lease went while it worked writes no verdict.

    Publishing would be writing a verdict on a job somebody else now owns, so the
    whole publish transaction rolls back — including the result row it had
    already inserted, which is why the result and the state change are one
    transaction rather than two.
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
        claimed = repository(connection).claim(owner="loser:aaaa", now=utcnow())
    assert claimed is not None
    # The reaper acts while the attempt is still executing.
    with migrated_database.begin() as connection:
        expire_lease(connection, job_id)
    runtime.reap()

    from application.worker.execution import Executed
    from application.worker.runtime import _LeaseLost

    with pytest.raises(_LeaseLost):
        runtime._publish_result(
            job=claimed,
            owner="loser:aaaa",
            executed=Executed(
                summary={"actors": 1}, blocked_entries=[], fingerprint=None
            ),
        )
    with migrated_database.begin() as connection:
        orphans = connection.execute(
            text("SELECT count(*) FROM reconciliation_job_results")
        ).scalar_one()
    assert orphans == 0, "the result rolled back with the state change"
    assert _row(migrated_database, job_id)["state"] == "queued"


# ---------------------------------------------------------------------------
# TC-LIM-06's named P3.3 consumer obligation
# ---------------------------------------------------------------------------


def test_the_worker_consumes_the_validated_lease_and_attempt_bounds(
    composition, migrated_database, callers, snapshot
):
    """N-23's exact lease and N-43's cap, proved **at the consumer**.

    TC-LIM-06 records lease, heartbeat, attempt, timeout and queue consumer
    evidence as a named P3.3 obligation, because P3.1 had no consumer for them
    and manufacturing one there would have been starting a package that was not
    authorised. This is that obligation.

    The claim statement's lease is not read from a literal: it comes from
    `WorkerSettings.lease_seconds`, which the register pins to an exact 60 and
    which `WorkerSettings` refuses to let be 59 or 61.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        job_id = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )
    assert composition.worker.lease_seconds == 60
    assert composition.worker.max_attempts == 3
    assert composition.worker.concurrency == 1

    before = utcnow()
    with migrated_database.begin() as connection:
        claimed = composition.jobs(connection).claim(owner="probe:aaaa", now=before)
    assert claimed is not None
    span = claimed["lease_expires_at"] - before
    assert abs(span.total_seconds() - composition.worker.lease_seconds) < 1.0

    with migrated_database.begin() as connection:
        beat = composition.jobs(connection).heartbeat(
            job_id=job_id, owner="probe:aaaa", now=before + timedelta(seconds=30)
        )
    assert beat is not None
    extended = _row(migrated_database, job_id)["lease_expires_at"] - (
        before + timedelta(seconds=30)
    )
    assert abs(extended.total_seconds() - composition.worker.lease_seconds) < 1.0


def test_the_worker_holds_its_own_canonical_settings_not_the_callers(
    tmp_path, artifact_root, bounded_ancestors
):
    """The canonicalisation boundary, at this composition.

    `WorkerComposition` reads the worker graph **once**, into an exact
    `WorkerSettings`, before anything uses a number from it — the same property
    the web composition holds, asserted for the second process. So the object the
    lease, the heartbeat, the attempt cap and the queue bound come from is one
    this composition built from one read, not the object the caller kept a
    reference to and could answer differently from on a later read.
    """
    from application.web.config import WorkerSettings

    settings = WebSettings.from_environment(
        web_environment(
            tmp_path, WORKER_ENABLED="true", WORKER_ARTIFACT_ROOT=str(artifact_root)
        ),
        process=ProcessRole.WORKER,
    )
    composition = WorkerComposition(settings, ancestors=bounded_ancestors)
    try:
        held = composition.worker
        assert type(held) is WorkerSettings, "canonicalised to the exact base type"
        assert held is not settings.worker, "not the caller's object"
        assert held.lease_seconds == 60
        assert held.max_attempts == 3
        assert held.queue_max_depth == 5
        assert held.attempt_timeout_seconds == 300
        assert held.heartbeat_seconds == 20
    finally:
        composition.close()


def test_two_workers_running_concurrently_execute_one_job_each(
    composition, worker_settings, migrated_database, callers, snapshot
):
    """N-41 is one job per worker, and the queue is safe for more than one worker.

    Two runtimes tick simultaneously against two queued jobs. Each claims a
    different one — `FOR UPDATE SKIP LOCKED` again, this time through the whole
    runtime rather than the statement alone — and both complete.
    """
    snapshot_id, checksum = snapshot
    with migrated_database.begin() as connection:
        first = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            request_key="concurrent:1",
        )
        second = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
            request_key="concurrent:2",
        )

    runtimes = [
        WorkerRuntime(
            composition=composition,
            worker_settings=composition.worker,
            bounds=worker_settings.bounds,
            guild_id=worker_settings.discord.guild_id,
            instance=f"host/{index}",
        )
        for index in (1, 2)
    ]
    outcomes: list = [None, None]
    barrier = threading.Barrier(2)

    def run(slot: int) -> None:
        barrier.wait(timeout=10)
        outcomes[slot] = runtimes[slot].tick()

    threads = [threading.Thread(target=run, args=(slot,)) for slot in (0, 1)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=60)

    claimed = {tick.claimed for tick in outcomes if tick is not None}
    assert claimed == {first, second}
    for job_id in (first, second):
        assert _row(migrated_database, job_id)["state"] == "completed"


def test_a_blocked_entrys_name_is_bounded_where_it_is_stored():
    """§3.2's 120-character bound, applied at the **write** rather than at render.

    A bound applied only at rendering leaves the untruncated value in the
    database for the next reader — a later view, an export somebody adds, an
    operator running a query. Bounding it where the durable record is built is
    what makes "the untruncated value is never sent" a property of the row.

    Driven directly against `_blocked_entries` with a minimal stand-in report,
    because the property is about that function and building a real 10 000-
    character Actor collision would make the case about the parser instead.
    """
    from types import SimpleNamespace

    from application.foundry.reconciliation import ActorOutcome
    from application.worker.execution import ACTOR_NAME_BOUND, _blocked_entries

    report = SimpleNamespace(
        entries=(
            SimpleNamespace(
                actor_id="A" * 16,
                actor_name="x" * 10_000,
                outcome=ActorOutcome.BLOCKED,
                character_id=None,
            ),
        ),
        issues=(),
    )
    entries = _blocked_entries(report)
    assert len(entries) == 1
    assert len(entries[0]["display_name"]) == ACTOR_NAME_BOUND == 120


def test_the_blocked_entry_list_is_capped_at_fifty():
    """VM-15's bound, applied at the write for the same reason.

    An unbounded list is an availability defect on a co-located host: a folder
    with a thousand collisions would produce a result row a page then has to
    render. Fifty is the accepted cap, and the remainder is not stored.
    """
    from types import SimpleNamespace

    from application.foundry.reconciliation import ActorOutcome
    from application.web.view_models import BLOCKED_ENTRY_BOUND
    from application.worker.execution import _blocked_entries

    report = SimpleNamespace(
        entries=tuple(
            SimpleNamespace(
                actor_id=f"A{index:015d}",
                actor_name=f"Collision {index}",
                outcome=ActorOutcome.BLOCKED,
                character_id=None,
            )
            for index in range(200)
        ),
        issues=(),
    )
    assert len(_blocked_entries(report)) == BLOCKED_ENTRY_BOUND == 50
