"""The commit fence: seven races at the boundary where the effect commits.

Added by the 2026-08-18 P3.3 remediation. The defect these cases exist for is
that P3.3 fenced the **publication of a job result** and left the **effect**
unfenced. Those were two transactions:

```text
    T1: SnapshotImportService.apply → import, characters, mappings, audit  COMMIT
                          ← the window: the job is still `running` here →
    T2: WorkerRuntime._publish_*   → result row + terminal state           COMMIT
```

Anything that transitioned the job inside that window — a cancellation observed
at a heartbeat, a timeout self-abandon, a kill-switch self-abandon, a reaper
requeue after lease expiry — produced a job saying `cancelled`, `queued`, `stale`
or `failed` whose abandoned thread had already committed real state.

Every case below therefore asserts the **rows**, not the runtime's return string:
`snapshot_imports`, `characters`, `external_actor_mappings` and the
`snapshot_import.applied` audit event. A runtime that returned
`"cancelled"` while the import committed would pass an outcome assertion and fail
every one of these.

## How the interleaving is made deterministic

`WorkerComposition.executor(fences=…)` builds the apply's commit fence. These
cases wrap **the production `JobLeaseFence`** in `_BarrierFence`, which runs a
callback immediately before or immediately after the real fence statement — that
is, inside the import's own transaction and either side of the row lock the fence
takes. The competing writer is then the production statement the runtime or the
route would have issued, on its own real connection.

No case sleeps, and no case treats elapsed time as evidence. The one case whose
competing statement genuinely blocks (case 5) asserts the *outcome* both
schedulings must produce, so it is deterministic whether or not the block is
observed.

**No live service and no real player data.** The artifacts are the synthetic
Phase 2 bundles the other P3.3 suites use.
"""
from __future__ import annotations

import threading

import pytest
from sqlalchemy import text

from adapters.web.repositories import ReconciliationJobRepository
from adapters.worker.composition import WorkerComposition
from application.audit import ActorCapability
from application.foundry.artifact import ingest_bytes
from application.foundry.audit_policy import IMPORT_APPLIED
from application.web.config import ProcessRole, WebSettings
from application.web.jobs import JobKind, JobState, StaleCode
from adapters.database.repositories import (
    SqlAlchemyReconciliationJobLeaseRepository,
)
from application.worker.fence import JobLeaseFence, PendingEffectResult
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
from tests.web.portal_fixtures import clean_p3_2_tables, seed_callers
from tests.web_fixtures import web_environment

pytestmark = pytest.mark.database

LEASE_SECONDS = 60
MAX_ATTEMPTS = 3


# ---------------------------------------------------------------------------
# The harness
# ---------------------------------------------------------------------------


class _BarrierFence:
    """The production fence, with a place to stand on either side of it.

    `before` runs in the import's transaction immediately *before* the fence
    statement takes the job row's write lock; `after` runs immediately after it
    and before the transaction commits. Both run on the worker's execution
    thread, which is exactly where the window being tested lives.
    """

    __slots__ = ("_inner", "_before", "_after")

    def __init__(self, inner, *, before=None, after=None) -> None:
        self._inner = inner
        self._before = before
        self._after = after

    def hold(self, unit_of_work) -> None:
        if self._before is not None:
            self._before()
        self._inner.hold(unit_of_work)
        if self._after is not None:
            self._after()


class _FencedComposition:
    """A `WorkerComposition` whose executor's fence carries the case's barriers.

    Delegates everything else, so the engine, the artifact store, the settings
    graph, the authorization port and the import service are the production ones
    the runtime would have used.
    """

    def __init__(self, inner: WorkerComposition, *, before=None, after=None) -> None:
        self._inner = inner
        self._before = before
        self._after = after

    def __getattr__(self, name):
        return getattr(self._inner, name)

    def executor(self, **kwargs):
        def build(job_id, owner, pending):
            return _BarrierFence(
                JobLeaseFence(
                    job_id=job_id, owner=owner, clock=utcnow, pending=pending
                ),
                before=None if self._before is None else (lambda: self._before(owner)),
                after=None if self._after is None else (lambda: self._after(owner)),
            )

        return self._inner.executor(fences=build, **kwargs)


@pytest.fixture()
def artifact_root(tmp_path):
    return tmp_path / "artifacts"


@pytest.fixture()
def worker_settings(tmp_path, artifact_root) -> WebSettings:
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
    composition = WorkerComposition(
        worker_settings, engine=migrated_database, ancestors=bounded_ancestors
    )
    try:
        yield composition
    finally:
        composition.close()


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


@pytest.fixture()
def runtimes(composition, worker_settings):
    """A factory: `runtimes(before=…, after=…)` gives a runtime whose apply fence
    carries those barriers, and `runtimes()` gives the plain production one."""

    def build(*, before=None, after=None, instance="test-host/1", kill_switch=None):
        graph = (
            composition
            if before is None and after is None
            else _FencedComposition(composition, before=before, after=after)
        )
        return WorkerRuntime(
            composition=graph,
            worker_settings=composition.worker,
            bounds=worker_settings.bounds,
            guild_id=worker_settings.discord.guild_id,
            instance=instance,
            kill_switch=kill_switch or (lambda: False),
        )

    return build


def repository(connection) -> ReconciliationJobRepository:
    return ReconciliationJobRepository(
        connection, lease_seconds=LEASE_SECONDS, max_attempts=MAX_ATTEMPTS
    )


def _row(engine, job_id):
    with engine.begin() as connection:
        return job_row(connection, job_id)


def _confirm(engine, runtime, callers, snapshot):
    """A completed preview and the apply job R-46 would have enqueued from it."""
    from uuid import uuid4

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


def effects(engine) -> dict:
    """Every durable trace an apply leaves, counted in one place.

    A runtime return string is not evidence, and neither is the job's state: what
    the fence exists to prevent is **these rows**, so every case asserts them.
    """
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
                text(
                    "SELECT count(*) FROM audit_events WHERE action = :applied"
                ),
                {"applied": IMPORT_APPLIED},
            ).scalar_one(),
        }


NOTHING = {"imports": 0, "characters": 0, "mappings": 0, "applied_audit": 0}
ONE_APPLY = {"imports": 1, "characters": 1, "mappings": 1, "applied_audit": 1}

#: The smallest publication payload migration 0013 will accept beside a committed
#: effect. Used only by the case that drives `hold_for_effect` directly; every
#: other case reaches the fence through the executor, which builds the real one
#: from the run's own preview.
MINIMAL_SUMMARY = {"actors": 1, "mapped": 0, "unmapped": 1, "blocked": 0, "absent": 0}


def current_owner(engine, job_id) -> str:
    return _row(engine, job_id)["lease_owner"]


# ---------------------------------------------------------------------------
# 1 — cancellation wins after the final cooperative check, before the commit
# ---------------------------------------------------------------------------


def test_cancellation_after_the_last_python_check_leaves_no_effect(
    runtimes, migrated_database, callers, snapshot
):
    """The race the executor's `if cancelled():` cannot cover, and never could.

    The cooperative check happens before `SnapshotImportService.apply` is called.
    Everything after it — the re-parse, the reconciliation, the character
    creation, the import row, the audit event — is one window in which a
    cancellation lands and the effect commits anyway.

    The cancellation here is the **production** statement R-45 issues, on its own
    connection, committed before the fence runs. The fence then matches zero rows
    and the whole apply transaction rolls back.
    """
    plain = runtimes()
    _preview_id, apply_id = _confirm(migrated_database, plain, callers, snapshot)

    def cancel(_owner):
        with migrated_database.begin() as connection:
            repository(connection).request_cancel(job_id=apply_id, now=utcnow())

    runtime = runtimes(before=cancel)
    tick = runtime.tick()
    assert tick.claimed == apply_id

    assert effects(migrated_database) == NOTHING, "a cancelled attempt commits nothing"
    row = _row(migrated_database, apply_id)
    assert row["state"] == JobState.CANCELLED.value
    assert row["effect_committed_at"] is None
    assert row["cancel_requested_at"] is not None
    with migrated_database.begin() as connection:
        results = connection.execute(
            text("SELECT count(*) FROM reconciliation_job_results WHERE job_id = :id"),
            {"id": apply_id},
        ).scalar_one()
    assert results == 0, "and no success result either"


# ---------------------------------------------------------------------------
# 2 and 3 — the worker's own self-abandon, both branches
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("attempts_before", "expected_state"),
    [(1, JobState.QUEUED.value), (MAX_ATTEMPTS, JobState.FAILED.value)],
    ids=["timeout-requeues", "kill-switch-at-the-last-attempt-fails"],
)
def test_a_self_abandon_in_the_commit_window_leaves_no_effect(
    runtimes, migrated_database, callers, snapshot, attempts_before, expected_state
):
    """N-45's cap and the kill switch issue the *same* statement, so both are here.

    `WorkerRuntime._run` abandons on the timeout branch and on the kill-switch
    branch through one repository method; what differs between them is only the
    reason string and, through `attempts`, which branch of the two-branch update
    fires. Both branches are parameterised here, and neither may leave an effect
    behind from the attempt it abandoned.

    Before the remediation the abandon carried no `effect_committed_at`
    predicate, so it requeued or failed the job while the thread it abandoned
    went on to commit an import.
    """
    plain = runtimes()
    _preview_id, apply_id = _confirm(migrated_database, plain, callers, snapshot)
    if attempts_before > 1:
        with migrated_database.begin() as connection:
            connection.execute(
                text("UPDATE reconciliation_jobs SET attempts = :n WHERE id = :id"),
                {"n": attempts_before - 1, "id": apply_id},
            )

    def abandon(owner):
        with migrated_database.begin() as connection:
            outcome = repository(connection).abandon(
                job_id=apply_id, owner=owner, now=utcnow()
            )
        assert outcome.state == expected_state, "the abandon won the race"

    runtime = runtimes(before=abandon)
    runtime.tick()

    assert effects(migrated_database) == NOTHING, "an abandoned attempt commits nothing"
    row = _row(migrated_database, apply_id)
    assert row["state"] == expected_state
    assert row["lease_owner"] is None
    assert row["effect_committed_at"] is None


# ---------------------------------------------------------------------------
# 4 — lease expiry, reaper, and a new claim while the old thread runs on
# ---------------------------------------------------------------------------


def test_a_reaped_lease_and_a_new_claim_stop_the_old_token_writing_anything(
    runtimes, migrated_database, callers, snapshot
):
    """The classic fencing case, driven at the commit boundary.

    The original attempt's lease expires, the reaper requeues the job, and a
    **different** worker claims it — all while the original thread is inside its
    apply transaction. The original token no longer names the row, so its fence
    matches zero rows and its effect is rolled back entirely. The job belongs to
    the new claim, and the new claim's `attempts` is the only one that moved.
    """
    plain = runtimes()
    _preview_id, apply_id = _confirm(migrated_database, plain, callers, snapshot)
    successor = {}

    def reap_and_reclaim(_owner):
        with migrated_database.begin() as connection:
            expire_lease(connection, apply_id)
        with migrated_database.begin() as connection:
            reaped = repository(connection).reap()
        assert [row["id"] for row in reaped] == [apply_id]
        with migrated_database.begin() as connection:
            claimed = repository(connection).claim(
                owner="other-host/2:beef", now=utcnow()
            )
        assert claimed is not None and claimed["id"] == apply_id
        successor["owner"] = "other-host/2:beef"

    runtime = runtimes(before=reap_and_reclaim)
    runtime.tick()

    assert effects(migrated_database) == NOTHING, "a stale token commits nothing"
    row = _row(migrated_database, apply_id)
    assert row["state"] == JobState.RUNNING.value
    assert row["lease_owner"] == successor["owner"], "the successor still owns it"
    assert row["effect_committed_at"] is None


# ---------------------------------------------------------------------------
# 5 — the apply commits first, and the cancellation is refused
# ---------------------------------------------------------------------------


def test_an_apply_that_commits_first_refuses_the_cancellation_that_follows(
    runtimes, migrated_database, callers, snapshot
):
    """The other direction, which the fence must not break.

    The cancellation is issued from a second thread on its own connection while
    the import transaction holds the job row's write lock. It blocks, the effect
    commits, and it then re-evaluates its predicate and matches zero rows — so
    R-45 answers "already committed" rather than cancelling a job whose import is
    durable.

    The assertion does not depend on the block being observed: if the second
    thread arrives after the commit instead, `effect_committed_at IS NOT NULL`
    refuses it just the same. Exactly one outcome is reachable, which is what
    makes this deterministic rather than timing-dependent.
    """
    plain = runtimes()
    _preview_id, apply_id = _confirm(migrated_database, plain, callers, snapshot)

    issued = threading.Event()
    outcome: dict = {}

    def request_cancel() -> None:
        issued.set()
        with migrated_database.begin() as connection:
            outcome["cancellation"] = repository(connection).request_cancel(
                job_id=apply_id, now=utcnow()
            )

    canceller = threading.Thread(target=request_cancel, name="canceller")

    def start_cancellation(_owner):
        canceller.start()
        issued.wait(timeout=10)

    runtime = runtimes(after=start_cancellation)
    tick = runtime.tick()
    canceller.join(timeout=30)
    assert not canceller.is_alive()

    assert tick.outcome == "completed", tick.outcome
    assert effects(migrated_database) == ONE_APPLY
    row = _row(migrated_database, apply_id)
    assert row["state"] == JobState.COMPLETED.value
    assert row["effect_committed_at"] is not None
    assert row["cancel_requested_at"] is None, "the cancellation was refused"
    refusal = outcome["cancellation"]
    assert refusal.accepted is False, (
        "R-45 reports the committed apply rather than a cancellation"
    )
    assert refusal.effect_committed is True
    assert refusal.conflict == "already_applied", (
        "and says so in VM-19's word rather than `stale_version`, which is what "
        "the job's own `running` state would have produced"
    )


# ---------------------------------------------------------------------------
# 5b — R-41 and R-46 are the fourth writer in the same window
# ---------------------------------------------------------------------------


def test_an_invalidation_in_the_commit_window_leaves_no_effect(
    runtimes, migrated_database, callers, snapshot
):
    """R-41's folder change wins the race: the apply commits nothing.

    `mark_stale` and `invalidate_for_snapshot` transition **live** jobs, and a
    `running` apply is a live job — so R-41's folder change and R-46's N-46
    expiry are a fourth writer in the fence's window, alongside cancellation, the
    self-abandon and the reaper. The fence requires `state = 'running'`, so an
    invalidation that lands first leaves the attempt nothing to commit.
    """
    plain = runtimes()
    _preview_id, apply_id = _confirm(migrated_database, plain, callers, snapshot)
    snapshot_id, _checksum = snapshot

    def invalidate(_owner):
        with migrated_database.begin() as connection:
            invalidated = repository(connection).invalidate_for_snapshot(
                snapshot_id=snapshot_id,
                reason=StaleCode.FOLDER_CHANGED,
                now=utcnow(),
            )
        assert apply_id in invalidated, "R-41 won the race"

    runtime = runtimes(before=invalidate)
    runtime.tick()

    assert effects(migrated_database) == NOTHING
    row = _row(migrated_database, apply_id)
    assert row["state"] == JobState.STALE.value
    assert row["effect_committed_at"] is None


def test_an_apply_whose_effect_committed_can_no_longer_be_made_stale(
    runtimes, migrated_database, callers, snapshot
):
    """The other direction, asserted on the statements rather than on a race.

    `stale` means *nothing was applied*, so it cannot describe an apply whose
    import is durable. The repository already refused to rewrite a `completed`
    apply for exactly that reason; both statements now carry
    `AND effect_committed_at IS NULL`, so the refusal holds from the instant the
    effect became durable rather than from the instant it was published — which
    is the whole window this remediation exists to close.

    Driven directly, with the job left in the state the window produces: an apply
    still `running` under its lease whose effect has committed. A barrier race
    would prove less here, not more — whichever of the two transactions commits
    first is a scheduling detail, and the property being asserted is that this
    row cannot be made `stale` at all.

    The second half of the case matters as much as the first: a preview and an
    apply with **no** committed effect are still invalidated, so the predicate
    narrows nothing R-41 and R-46 were for.
    """
    plain = runtimes()
    _preview_id, apply_id = _confirm(migrated_database, plain, callers, snapshot)
    snapshot_id, checksum = snapshot
    # A second, ordinary live job for the same snapshot. The confirmed preview
    # cannot serve as the control here: an apply already names it, so R-41
    # deliberately leaves it alone for a different reason entirely.
    with migrated_database.begin() as connection:
        untouched_by_any_effect = seed_job(
            connection,
            snapshot_id=snapshot_id,
            account_id=callers["C"].account_id,
            checksum=checksum,
        )

    # The window's own state: claimed, running, effect durable, result not yet
    # published. Reached through the production claim and the production fence.
    with migrated_database.begin() as connection:
        claimed = repository(connection).claim(owner="worker:1111", now=utcnow())
    assert claimed is not None and claimed["id"] == apply_id
    with migrated_database.begin() as connection:
        held = SqlAlchemyReconciliationJobLeaseRepository(connection).hold_for_effect(
            job_id=apply_id,
            owner="worker:1111",
            now=utcnow(),
            # The publication payload the fence makes durable with the effect.
            # Required rather than defaulted, and asserted through the production
            # statement, because migration 0013 forbids the one without the other.
            result=PendingEffectResult(summary=dict(MINIMAL_SUMMARY)).payload(),
        )
    assert held is True

    with migrated_database.begin() as connection:
        jobs = repository(connection)
        refused_one = jobs.mark_stale(
            job_id=apply_id, reason=StaleCode.FOLDER_CHANGED, now=utcnow()
        )
        invalidated = jobs.invalidate_for_snapshot(
            snapshot_id=snapshot_id, reason=StaleCode.FOLDER_CHANGED, now=utcnow()
        )

    assert refused_one is False, "R-46 cannot withdraw an apply that applied"
    assert apply_id not in invalidated, "and neither can R-41"
    row = _row(migrated_database, apply_id)
    assert row["state"] == JobState.RUNNING.value
    assert row["lease_owner"] == "worker:1111"
    assert row["stale_reason"] is None

    # And the predicate has not stopped R-41 doing its job: the queued preview,
    # which can never carry a committed effect, was withdrawn by the very same
    # statement in the very same transaction.
    assert untouched_by_any_effect in invalidated
    assert (
        _row(migrated_database, untouched_by_any_effect)["state"]
        == JobState.STALE.value
    )


# ---------------------------------------------------------------------------
# 6 — crash after the effect commits, before the result is published
# ---------------------------------------------------------------------------


def test_a_crash_between_the_effect_and_the_result_recovers_one_import(
    runtimes, composition, migrated_database, callers, snapshot
):
    """The fence must not break SM-05's process-restart recovery.

    The attempt commits its effect — and therefore its `effect_committed_at` and
    the publication payload beside it — and then dies before publishing. The job is
    left `running` with a lapsed lease, and the platform finishes it.

    **The intermediate state changed on 2026-08-18**, with the effect-publication
    remediation. It used to be `queued`: the reaper requeued the job and a fourth
    kind of hope — that a *re-execution* would reach the import service, find the
    spent request key and return a duplicate — produced the result. That path spent
    one of N-43's three attempts, had none to spend at the cap (where the reaper
    wrote `failed` over the import instead), and could end `stale` or `failed` for
    reasons that said nothing about the import that had committed. The reaper now
    declines the row and `recover()` publishes it from the two durable rows the
    effect's own transaction wrote.

    One import, one character, one applied-audit event, one result, and a job that
    ends `completed` on the same attempt that committed it.
    """
    plain = runtimes()
    _preview_id, apply_id = _confirm(migrated_database, plain, callers, snapshot)

    with migrated_database.begin() as connection:
        claimed = repository(connection).claim(owner="crashing:aaaa", now=utcnow())
    assert claimed is not None and claimed["id"] == apply_id
    executor = composition.executor()
    with migrated_database.begin() as connection:
        services = composition.job_services(connection)
        snapshot_row = services.snapshots.snapshot(claimed["snapshot_id"])
        selection = services.snapshots.folder_selection(claimed["snapshot_id"])
        subject = services.accounts.discord_subject(claimed["requested_by_account_id"])
    executor.for_requester(int(subject), claimed["requested_by_account_id"]).execute(
        job=claimed,
        snapshot=snapshot_row,
        selection=selection,
        cancelled=lambda: False,
        owner="crashing:aaaa",
    )

    assert effects(migrated_database) == ONE_APPLY, "the effect landed before the crash"
    crashed = _row(migrated_database, apply_id)
    assert crashed["effect_committed_at"] is not None
    assert crashed["effect_result"] is not None, (
        "and the fence stored what the publication owes, in the same statement"
    )
    assert crashed["state"] == JobState.RUNNING.value, "the publication never happened"

    with migrated_database.begin() as connection:
        expire_lease(connection, apply_id)
    assert list(plain.reap()) == [], "an expired committed effect is not an expiry"
    awaiting = _row(migrated_database, apply_id)
    assert awaiting["state"] == JobState.RUNNING.value
    assert awaiting["attempts"] == 1, "and no attempt was spent recovering it"

    assert list(plain.recover()) == [apply_id]

    assert effects(migrated_database) == ONE_APPLY, "exactly one durable effect"
    final = _row(migrated_database, apply_id)
    assert final["state"] == JobState.COMPLETED.value
    assert final["attempts"] == 1
    with migrated_database.begin() as connection:
        summary = connection.execute(
            text("SELECT summary FROM reconciliation_job_results WHERE job_id = :id"),
            {"id": apply_id},
        ).scalar_one()
    assert summary["recovered"] is True, (
        "the publication was recovered; the import was not a duplicate of anything"
    )
    assert summary["duplicate"] is False


# ---------------------------------------------------------------------------
# 7 — the same worker instance cannot revalidate its own old attempt
# ---------------------------------------------------------------------------


def test_the_same_instance_reclaiming_cannot_make_its_old_attempt_valid(
    runtimes, migrated_database, callers, snapshot
):
    """A worker identity is not a fencing token, proved where the effect commits.

    The lease owner is `{instance}:{token}` with the token minted per claim. Here
    the *same* instance reclaims the job after the reaper requeues it, so a fence
    that checked the worker's name would pass and the abandoned attempt would
    commit under the successor's authority. It checks the token, so it matches
    zero rows.
    """
    plain = runtimes(instance="test-host/1")
    _preview_id, apply_id = _confirm(migrated_database, plain, callers, snapshot)
    tokens: dict = {}

    def reclaim_as_the_same_instance(owner):
        tokens["original"] = owner
        with migrated_database.begin() as connection:
            expire_lease(connection, apply_id)
        with migrated_database.begin() as connection:
            repository(connection).reap()
        with migrated_database.begin() as connection:
            claimed = repository(connection).claim(
                owner="test-host/1:cafe", now=utcnow()
            )
        assert claimed is not None and claimed["id"] == apply_id

    runtime = runtimes(before=reclaim_as_the_same_instance, instance="test-host/1")
    runtime.tick()

    assert tokens["original"].startswith("test-host/1:")
    assert tokens["original"] != "test-host/1:cafe", "a claim mints a fresh token"
    assert effects(migrated_database) == NOTHING
    row = _row(migrated_database, apply_id)
    assert row["lease_owner"] == "test-host/1:cafe"
    assert row["effect_committed_at"] is None


# ---------------------------------------------------------------------------
# The runtime's own bookkeeping for a thread it cannot stop
# ---------------------------------------------------------------------------


def test_a_worker_holding_an_outstanding_thread_claims_nothing_else(
    runtimes, migrated_database, callers, snapshot
):
    """N-41 enforced against the thread, not against the job it stopped watching.

    Python cannot kill a thread, and the previous runtime returned from `_run`
    with one still executing and then claimed the next job — two attempts in one
    worker whose pool holds two connections. Correctness no longer depends on
    this (the fence does), but a worker that has lost control of a thread must
    say so and stop taking work rather than pretend the attempt ended.
    """
    release = threading.Event()
    reached = threading.Event()
    plain = runtimes()
    _preview_id, apply_id = _confirm(migrated_database, plain, callers, snapshot)

    def block(_owner):
        reached.set()
        release.wait(timeout=30)

    runtime = runtimes(before=block)
    loop = threading.Thread(target=runtime.tick, name="tick")
    loop.start()
    try:
        assert reached.wait(timeout=30), "the attempt reached the commit boundary"
        # The lease goes while the thread is parked inside its transaction, so
        # the runtime stops watching an attempt it cannot stop.
        with migrated_database.begin() as connection:
            expire_lease(connection, apply_id)
        # Drive the runtime's own release path rather than waiting a heartbeat:
        # the reaper is a production statement and the runtime runs it every tick.
        second = runtimes()
        assert list(second.reap()) == [apply_id]
    finally:
        release.set()
        loop.join(timeout=60)
    assert not loop.is_alive()

    # The blocked thread has finished by now, so the runtime reports nothing
    # outstanding and is free to work again — the list is pruned from the live
    # thread rather than cached.
    assert runtime.outstanding_attempts() == ()
    assert effects(migrated_database) == NOTHING, "the reaped token committed nothing"


def test_an_outstanding_attempt_blocks_the_next_claim(runtimes, migrated_database):
    """The refusal itself, without a database race to arrange it.

    `tick` consults the live threads before it claims. A worker with one still
    running claims nothing and says `attempt_outstanding`, which is what an
    operator reads on `/healthz` instead of guessing why the queue is not moving.
    """
    from application.worker.runtime import _Attempt

    runtime = runtimes()
    release = threading.Event()
    thread = threading.Thread(target=release.wait, kwargs={"timeout": 30})
    thread.start()
    runtime._outstanding.append(
        _Attempt(
            job_id=None,
            owner="test-host/1:dead",
            thread=thread,
            finished=threading.Event(),
            cancel=threading.Event(),
            box={},
            released_for="timeout",
        )
    )
    try:
        tick = runtime.tick()
        assert tick.claimed is None
        assert tick.outcome == "attempt_outstanding"
        assert runtime.outstanding_report()[0][1] == "test-host/1:dead"
        assert runtime.outstanding_report()[0][2] == "timeout"
    finally:
        release.set()
        thread.join(timeout=30)
    assert runtime.outstanding_attempts() == ()
