"""The worker loop: claim, lease, heartbeat, publish, abandon, reap.

Everything here is about **who is entitled to write a verdict**, and the answer
is always the same: the holder of the lease named on the row, at the moment of
the write. Every statement the runtime issues carries `AND lease_owner = :owner`,
so a worker that lost its lease — because it was slow and the reaper acted —
matches zero rows and exits quietly rather than stamping a stale verdict on a job
somebody else now owns.

## The fencing token, and why the worker's name is not enough

`lease_owner` is minted **per claim**, not per process: `{instance}:{token}`,
where the token is fresh random hex. A worker identity alone would let the same
process satisfy its own expired lease after the reaper requeued the job and the
process reclaimed it — the classic fencing failure, where a slow writer's write
lands because the fence only checks *who* and not *which attempt*. With a
per-claim token, the first attempt's publish matches zero rows even when the
second attempt belongs to the same worker.

## The heartbeat, and the honest bound on it

The work is executed on a thread while the main thread heartbeats at most every
N-23 seconds, observes cancellation, and enforces N-45's cap. That is what lets a
cancellation be observed "at the next heartbeat" and a run be abandoned at the
hard cap, both of which SM-05 requires.

**The heartbeat can be delayed by one GIL-holding call.** `json.loads` on a
multi-megabyte artifact does not release the GIL, so the heartbeat thread cannot
run during it. The rest of the parse — pure-Python NFC normalization and
canonical-key ordering, which is the majority of the measured 9.566 seconds —
does release it. The lease is 60 seconds, roughly six times the whole measured
preview, so the delay is comfortably inside it at the observed scale; at the
accepted 64 MiB bound it has never been measured. That is recorded as a residual
risk with a staging measurement rather than argued away: the failure mode if the
bound were exceeded is an expired lease, which is **recoverable** (N-23) and not
a failure verdict, and the durable effect is fenced by the existing unique
constraints rather than by the job's state.

## The thread the runtime cannot kill, and the two things it does about it

`_run` executes the work on a daemon thread. Python cannot kill a thread, and
until the 2026-08-18 remediation this runtime returned from `_run` on lease loss,
on cancellation and at N-45's cap while that thread was **still running** — and
then published `cancelled`, `queued`, `stale` or `failed` for a job whose
abandoned thread could still commit character, import, mapping and audit state.

Two changes, and neither of them is a thread join with a timeout:

1. **The effect is fenced where it commits.** `application/worker/fence.py` puts
   the lease check inside the transaction that commits the import, so an
   abandoned thread's commit is *impossible* rather than merely unlikely. That is
   what makes the outcomes this runtime publishes true.
2. **The thread is tracked, not forgotten.** A thread this worker can no longer
   stop is recorded as an outstanding attempt, and `tick` claims nothing while
   one is alive. N-41 — one in-flight job per worker — is thereby enforced
   against the thread that is actually still running rather than against the job
   this worker stopped watching.

The second is a liveness bound, not a correctness one: correctness is (1). A
worker holding an outstanding attempt does no further work and says so, which is
an operator-visible stall rather than a silent double-execution.

## The reaper is the only writer of the expiry transition

One statement, two branches (schema §10.1). The runtime runs it on its own
interval (N-44) whether or not it is executing a job, and it is safe to run
concurrently with another reaper because `FOR UPDATE SKIP LOCKED` gives each
expired row to exactly one of them. A terminal branch writes its
`reconciliation.job_failed` audit event in the **same transaction**, so a job may
be failed by a process that never executed it and the event names the job's lease
history rather than pretending the reaper did the work.

## An expired lease over a committed effect is a publication, not an expiry

Added by the 2026-08-18 effect-publication remediation. The reaper's two branches
both assume the attempt produced nothing: one retries it, and the other declares
it exhausted. Neither can describe an apply whose import committed and whose
result was never published, and the second of them wrote `failed` with
`attempts_exhausted` over a durable import — the blocking finding.

So the reaper now takes only expiries with `effect_committed_at IS NULL`, and
`recover()` takes the rest. Recovery reads the publication payload the commit fence
made durable in the effect's own transaction, reads the immutable
`snapshot_imports` receipt the same transaction wrote, and publishes one
`completed` result — in one transaction, under the job row's write lock, without
re-parsing an artifact, re-resolving authority, minting a lease or spending one of
N-43's three attempts. It runs on the reaper's interval, before the kill switch and
before the outstanding-thread check, because a Council member owed a receipt for a
durable import must not have to wait for this worker to be healthy.
"""
from __future__ import annotations

import secrets
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable
from uuid import UUID

from application.audit import ActorCapability, AuditEvent, AuditSource
from application.web.jobs import (
    REAPER_INTERVAL_SECONDS,
    RESULT_RETENTION_DAYS,
    FailureCode,
    JobKind,
    JobState,
    StaleCode,
)
from application.worker.authorization import WorkerAuthorizationPort
from application.worker.execution import Cancelled, Executed, Failed, JobExecutor, Stale
from application.worker.fence import FenceLost
from application.worker.recovery import (
    EffectPublicationUnavailable,
    recovered_result,
    recovery_payload,
)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


#: How many heartbeats the runtime will keep a job alive for while waiting for a
#: thread whose **effect has already committed** to hand back its result.
#:
#: Not an extension of N-45's cap. The cap bounds *execution*; by this point
#: execution is over — the import committed — and only the return path is left.
#: It is bounded rather than unbounded because "wait forever for an unkillable
#: thread" is not a fix: when it elapses the job is left `running`, its lease
#: lapses within `N-23 + N-44`, and `recover()` publishes the result from the
#: payload the fence made durable. Nothing is lost, no attempt is spent and no
#: worker is held indefinitely.
EFFECT_PUBLICATION_GRACE_HEARTBEATS = 3

#: How many committed-but-unpublished effects one recovery pass will publish.
#:
#: The same bound, and the same reason, as the reaper's `limit`: a backlog must not
#: turn one tick into an unbounded series of transactions while the queue waits.
#: Twenty is the reaper's number, and a platform running one worker (N-41) with a
#: five-job queue bound (N-42) cannot produce a backlog anywhere near it — it is a
#: ceiling on a pathological case rather than a throughput setting.
EFFECT_RECOVERY_LIMIT = 20


@dataclass(frozen=True, slots=True)
class Tick:
    """What one pass of the loop did. Returned so a test can drive the loop
    deterministically rather than sleeping and hoping."""

    claimed: UUID | None
    outcome: str | None
    reaped: tuple[UUID, ...]
    #: Jobs whose import effect had committed and whose result this pass
    #: published on the dead process's behalf. Reported separately from `reaped`
    #: because they are the opposite outcome: a reaped job is one the platform is
    #: retrying or giving up on, and a recovered one is a job it has just
    #: completed truthfully.
    recovered: tuple[UUID, ...] = ()


@dataclass(slots=True)
class _Attempt:
    """One execution thread, the events it answers to, and what it produced.

    Held as an object rather than as four local variables because the runtime now
    has to be able to **hand it on** — to an orphan list, or to a bounded wait
    for a result whose effect already committed — and four locals cannot be
    handed anywhere.
    """

    job_id: UUID
    owner: str
    thread: threading.Thread
    finished: threading.Event
    cancel: threading.Event
    box: dict
    #: Why the runtime stopped watching this attempt. Recorded rather than
    #: logged and forgotten, because "which job, and what happened to it" is the
    #: first question about a worker that has stopped taking work.
    released_for: str | None = None

    @property
    def alive(self) -> bool:
        return self.thread.is_alive()

    def ask_to_stop(self) -> None:
        """Set the cooperative flag. It is a courtesy, not a control: the fence
        is what makes an ignored request harmless."""
        self.cancel.set()


class WorkerRuntime:
    """One worker process's loop. One in-flight job (N-41), one settings graph.

    **The settings are the process's canonical `WorkerSettings`**, handed in once
    and read from nowhere else. The runtime reads no environment variable, builds
    no second engine and constructs no second provider: a worker that could
    answer a second time about its own lease would be a worker whose lease is not
    a fact.
    """

    __slots__ = (
        "_composition",
        "_worker",
        "_bounds",
        "_guild_id",
        "_instance",
        "_clock",
        "_kill_switch",
        "_stopped",
        "_last_reap",
        "_outstanding",
    )

    def __init__(
        self,
        *,
        composition,
        worker_settings,
        bounds,
        guild_id: int,
        instance: str,
        clock: Callable[[], datetime] = utcnow,
        kill_switch: Callable[[], bool] = lambda: False,
    ) -> None:
        self._composition = composition
        self._worker = worker_settings
        self._bounds = bounds
        self._guild_id = guild_id
        self._instance = instance
        self._clock = clock
        self._kill_switch = kill_switch
        self._stopped = threading.Event()
        self._last_reap: datetime | None = None
        #: Threads this worker could not stop. Python offers no way to kill one,
        #: so the honest thing is to know they exist and to claim nothing else
        #: while they do — rather than to return from `_run` and call the attempt
        #: over. Correctness does not rest on this list; the commit fence makes an
        #: outstanding thread unable to commit. This is N-41's liveness half.
        self._outstanding: list[_Attempt] = []

    # -- the loop ----------------------------------------------------------
    def stop(self) -> None:
        """Ask the loop to finish the current attempt and exit.

        Graceful shutdown is bounded below the lease (N-52), so a restarting
        process never holds a claim it cannot heartbeat.
        """
        self._stopped.set()

    def tick(self) -> Tick:
        """One pass: reap if due, then claim and run at most one job.

        Returns what happened, so the loop can be driven a step at a time by a
        test. A test that had to sleep for a lease would be a test that is slow
        and, worse, occasionally wrong.
        """
        reaped = ()
        recovered = ()
        now = self._clock()
        if self._last_reap is None or (
            now - self._last_reap
        ).total_seconds() >= REAPER_INTERVAL_SECONDS:
            reaped = self.reap()
            # **Before the kill switch and before the outstanding-thread check**,
            # deliberately, and for the same reason reaping is: publishing the
            # result of an effect that already committed asks nothing of this
            # worker's execution capacity and must not be withheld by a worker
            # that has stopped taking work. A Council member waiting on a job
            # whose import is durable is owed the receipt whatever state the
            # worker that ran it left behind.
            recovered = self.recover()
            self._last_reap = now

        if self._kill_switch():
            # Layer 1 of the operator kill switch: **claim no new work.** A job
            # already in flight finishes or is abandoned at the next heartbeat,
            # and an abandoned attempt is recoverable rather than failed.
            return Tick(
                claimed=None,
                outcome="kill_switch",
                reaped=reaped,
                recovered=recovered,
            )
        if self._stopped.is_set():
            return Tick(
                claimed=None,
                outcome="stopped",
                reaped=reaped,
                recovered=recovered,
            )
        if self.outstanding_attempts():
            # N-41 against the **thread**, not against the job this worker
            # stopped watching. Reaping still ran above, so the platform recovers
            # this worker's abandoned job even while this worker is stalled — and
            # the stall is reported rather than hidden, so `/healthz` and an
            # operator can see a worker that has stopped taking work.
            return Tick(
                claimed=None,
                outcome="attempt_outstanding",
                reaped=reaped,
                recovered=recovered,
            )

        claim = self._claim()
        if claim is None:
            return Tick(
                claimed=None, outcome=None, reaped=reaped, recovered=recovered
            )
        job, owner = claim
        outcome = self._run(job=job, owner=owner)
        return Tick(
            claimed=job["id"],
            outcome=outcome,
            reaped=reaped,
            recovered=recovered,
        )

    # -- claiming ----------------------------------------------------------
    def _claim(self):
        """One claim, in its own transaction, with a fresh fencing token."""
        owner = f"{self._instance}:{secrets.token_hex(8)}"
        with self._composition.engine.begin() as connection:
            jobs = self._composition.jobs(connection)
            job = jobs.claim(owner=owner, now=self._clock())
        return None if job is None else (job, owner)

    # -- running one job ---------------------------------------------------
    def _run(self, *, job, owner: str) -> str:
        """Execute on a thread; heartbeat, watch for cancellation and cap here.

        The job's context — its snapshot, its folder selection and its
        requester's Discord subject — is read in one transaction *before* the
        work starts, so the ten seconds of parsing are not spent holding a
        database connection.

        **Every exit from this loop is either a verdict the fence has made true
        or no verdict at all.** The thread may outlive the call; what it cannot do
        is commit, because its commit runs the fence under this exact `owner`.
        """
        attempt = self._start(job=job, owner=owner)
        started = self._clock()

        while not attempt.finished.wait(timeout=self._worker.heartbeat_seconds):
            beat = self._heartbeat(job_id=job["id"], owner=owner)
            if beat is None:
                # The lease is gone: the reaper acted while this attempt ran.
                # Nothing is published, because publishing would be writing a
                # verdict on a job somebody else now owns — and nothing can be
                # committed either, because the fence names a token the row no
                # longer carries.
                return self._release(attempt, reason="lease_lost", outcome="lease_lost")
            if beat["cancel_requested_at"] is not None:
                # SM-05: a `running` job is cancelled **at its next heartbeat**.
                #
                # Observing the request is proof that no effect has committed:
                # the cancel statement carries `AND effect_committed_at IS NULL`,
                # so a request that is recorded is a request that won the race
                # with the fence. Publishing `cancelled` here is therefore a true
                # statement even while the thread is still running.
                attempt.ask_to_stop()
                outcome = self._publish_cancelled(job_id=job["id"], owner=owner)
                return self._release(attempt, reason="cancelled", outcome=outcome)
            if (self._clock() - started).total_seconds() >= (
                self._worker.attempt_timeout_seconds
            ):
                # N-45's hard cap. The attempt is **abandoned**, not failed: an
                # abandoned attempt is recoverable and the two-branch statement
                # decides between requeue and exhaustion under this worker's own
                # lease.
                return self._stop(attempt, job=job, owner=owner, reason="timeout")
            if self._kill_switch():
                return self._stop(attempt, job=job, owner=owner, reason="kill_switch")

        return self._publish(job=job, owner=owner, attempt=attempt)

    def _start(self, *, job, owner: str) -> _Attempt:
        """Read the job's context, then hand the work to a thread."""
        with self._composition.engine.begin() as connection:
            services = self._composition.job_services(connection)
            snapshot = services.snapshots.snapshot(job["snapshot_id"])
            selection = services.snapshots.folder_selection(job["snapshot_id"])
            subject = services.accounts.discord_subject(job["requested_by_account_id"])
            # Has this attempt's key already been spent? Read here, in the
            # transaction that reads the rest of the job's context, so the
            # executor needs no repository of its own.
            #
            # **No production path reaches this any more** (2026-08-18
            # effect-publication remediation): the fence writes the request key's
            # import and `effect_committed_at` in one transaction, and a job with
            # `effect_committed_at` set is never requeued — it is published by
            # `recover()`. It is kept because migration 0013 deliberately leaves
            # `queued` representable for a committed effect, so if such a row ever
            # arises the attempt reaches the import service and is told it is a
            # duplicate, rather than being stopped by a scope check that the
            # effect itself moved. A wasteful correct outcome, not a wrong one.
            already_applied = services.snapshots.import_by_request_key(
                job["request_key"]
            )

        cancel_seen = threading.Event()
        finished = threading.Event()
        box: dict[str, object] = {}

        executor = self._composition.executor().for_requester(
            int(subject) if subject is not None else None,
            job["requested_by_account_id"],
        )

        def work() -> None:
            try:
                box["result"] = executor.execute(
                    job=job,
                    snapshot=snapshot,
                    selection=selection,
                    already_applied=already_applied,
                    cancelled=cancel_seen.is_set,
                    owner=owner,
                )
            except Cancelled:
                box["result"] = "cancelled"
            except FenceLost:
                # The attempt lost the race at the commit boundary and committed
                # **nothing**. Deliberately not folded into the `internal`
                # failure below: an internal failure consumes an attempt, and
                # this is not a failure at all — it is the designed outcome of a
                # race whose winner has already written, or is entitled to write,
                # the job's verdict.
                box["result"] = "fenced"
            except BaseException as error:  # noqa: BLE001 - one outcome, recorded
                # An unexpected exception is `internal` and is **not**
                # deterministic: the platform does not know why it happened, so
                # the attempt is retried rather than the job condemned. The text
                # never leaves this process — VM-20 carries a correlation id and
                # nothing else (N-25).
                box["error"] = error
                box["result"] = Failed(code=FailureCode.INTERNAL, deterministic=False)
            finally:
                finished.set()

        thread = threading.Thread(target=work, name=f"job-{job['id']}", daemon=True)
        attempt = _Attempt(
            job_id=job["id"],
            owner=owner,
            thread=thread,
            finished=finished,
            cancel=cancel_seen,
            box=box,
        )
        thread.start()
        return attempt

    def _stop(self, attempt: _Attempt, *, job, owner: str, reason: str) -> str:
        """N-45's cap or the kill switch, told apart from a committed effect.

        The abandon statement carries `AND effect_committed_at IS NULL`, so it
        refuses to requeue or fail a job whose import already committed. That
        refusal is not an error: it means this attempt won its race and owes a
        result, so the runtime waits a bounded moment for it rather than writing
        `queued` or `failed` over a real import.
        """
        abandonment = self._abandon(job_id=job["id"], owner=owner)
        if abandonment.state is not None:
            return self._release(
                attempt,
                reason=reason,
                outcome=f"abandoned:{abandonment.state}:{reason}",
            )
        if abandonment.effect_committed:
            return self._await_publication(
                job=job, owner=owner, attempt=attempt, reason=reason
            )
        return self._release(attempt, reason="lease_lost", outcome="lease_lost")

    def _await_publication(
        self, *, job, owner: str, attempt: _Attempt, reason: str
    ) -> str:
        """Keep the lease alive for a bounded moment, then publish what committed.

        Not "wait forever for an unkillable thread": the wait is
        `EFFECT_PUBLICATION_GRACE_HEARTBEATS` heartbeats, and when it elapses the
        job is left `running` with its lease about to lapse. `recover()` then
        publishes the result from the payload the fence made durable, so the bound
        costs a delay of at most `N-23 + N-44` and never an effect, an attempt or a
        re-execution.
        """
        remaining = EFFECT_PUBLICATION_GRACE_HEARTBEATS
        while not attempt.finished.wait(timeout=self._worker.heartbeat_seconds):
            if self._heartbeat(job_id=job["id"], owner=owner) is None:
                return self._release(
                    attempt, reason="lease_lost", outcome="lease_lost"
                )
            remaining -= 1
            if remaining <= 0:
                return self._release(
                    attempt,
                    reason=f"{reason}:effect_committed",
                    outcome="effect_committed_unpublished",
                )
        return self._publish(job=job, owner=owner, attempt=attempt)

    def _publish(self, *, job, owner: str, attempt: _Attempt) -> str:
        """Turn what the thread produced into the job's one durable verdict."""
        result = attempt.box.get("result")
        if result == "cancelled":
            return self._publish_cancelled(job_id=job["id"], owner=owner)
        if result == "fenced":
            # Somebody else won at the commit boundary. The one verdict this
            # worker may still owe is its **own** cancellation, which is a
            # request until a holder of the lease transitions it — and
            # `cancel_under_lease` carries `AND lease_owner = :owner AND state =
            # 'running'`, so it matches only in exactly that case and matches
            # zero rows when the winner was a reaper or an abandonment.
            outcome = self._publish_cancelled(job_id=job["id"], owner=owner)
            return outcome if outcome == "cancelled" else "fenced"
        if isinstance(result, Failed):
            return self._publish_failure(job=job, owner=owner, failure=result)
        if isinstance(result, Stale):
            return self._publish_stale(job=job, owner=owner, stale=result)
        if isinstance(result, Executed):
            return self._publish_result(job=job, owner=owner, executed=result)
        # Defensive: `work()` sets a result on every path, so reaching here means
        # the thread ended without one. Abandoning is the recoverable answer, and
        # the two reasons the abandon can match nothing are still told apart —
        # reporting `lease_lost` over a committed effect is the confusion this
        # remediation exists to remove.
        abandonment = self._abandon(job_id=job["id"], owner=owner)
        if abandonment.state is not None:
            return f"abandoned:{abandonment.state}:no_result"
        return (
            "effect_committed_unpublished"
            if abandonment.effect_committed
            else "lease_lost"
        )

    # -- the thread this runtime cannot kill -------------------------------
    def _release(self, attempt: _Attempt, *, reason: str, outcome: str) -> str:
        """Stop watching an attempt, and record it if its thread is still alive.

        Asking it to stop is a courtesy the work may honour at its next phase
        boundary; the control is the fence, which makes anything the thread still
        tries to commit match zero rows. What this adds is that the worker does
        not pretend the thread ended: an outstanding attempt blocks the next
        claim, so one worker never runs two.
        """
        attempt.ask_to_stop()
        attempt.released_for = reason
        if attempt.alive:
            self._outstanding.append(attempt)
        return outcome

    def outstanding_attempts(self) -> tuple[UUID, ...]:
        """The jobs whose threads this worker could not stop, still alive now.

        Called by `tick` before it claims and by the operator-facing health path.
        A **method, not a property**: it prunes the dead ones as it answers, and a
        property that mutated would be exactly the surprising access this
        project's design rules keep out of properties. Pruned on read rather than
        on a timer, because "is it still alive" is a question with a live answer
        and a cached one would be a second truth.
        """
        self._outstanding = [attempt for attempt in self._outstanding if attempt.alive]
        return tuple(attempt.job_id for attempt in self._outstanding)

    def outstanding_report(self) -> tuple[tuple[UUID, str, str], ...]:
        """`(job id, lease owner, why)` for each thread still outstanding.

        The operator-facing form of the method above. Job ids and lease owners
        only — never a checksum, a requester or anything the artifact contained.
        """
        self.outstanding_attempts()
        return tuple(
            (attempt.job_id, attempt.owner, attempt.released_for or "unknown")
            for attempt in self._outstanding
        )

    # -- publishing --------------------------------------------------------
    def _heartbeat(self, *, job_id: UUID, owner: str):
        with self._composition.engine.begin() as connection:
            jobs = self._composition.jobs(connection)
            return jobs.heartbeat(job_id=job_id, owner=owner, now=self._clock())

    def _publish_result(self, *, job, owner: str, executed: Executed) -> str:
        """The result row and the state change, in **one** transaction.

        `CHECK ((state = 'completed') = (result_id IS NOT NULL))` is what turns
        "no state named `completed` precedes durable commit" from an ordering
        convention into a fact: the result is inserted, then named by the update,
        and if the transaction does not commit neither exists.
        """
        now = self._clock()
        with self._composition.engine.begin() as connection:
            jobs = self._composition.jobs(connection)
            audit = self._composition.audit(connection)
            result_id = jobs.store_result(
                job_id=job["id"],
                summary=executed.summary,
                blocked_entries=executed.blocked_entries,
                now=now,
                expires_at=now + timedelta(days=RESULT_RETENTION_DAYS),
            )
            if not jobs.complete(
                job_id=job["id"],
                owner=owner,
                result_id=result_id,
                fingerprint=executed.fingerprint,
                now=now,
            ):
                # The lease went while the result was being written. The whole
                # transaction rolls back, including the orphan result row.
                raise _LeaseLost()
            audit.record(
                AuditEvent(
                    action=f"reconciliation.{job['kind']}_completed",
                    entity_type="reconciliation_job",
                    entity_id=str(job["id"]),
                    source=AuditSource.IMPORT,
                    actor_capability=ActorCapability.SYSTEM,
                    correlation_id=job["correlation_id"],
                    payload=completion_payload(job, executed.summary),
                )
            )
        return "completed"

    def _publish_failure(self, *, job, owner: str, failure: Failed) -> str:
        if not failure.deterministic:
            # A failure the platform cannot attribute to the artifact is an
            # abandoned attempt, so the remaining attempts are used.
            abandonment = self._abandon(job_id=job["id"], owner=owner)
            if abandonment.state is None:
                return "lease_lost"
            return f"abandoned:{abandonment.state}:{failure.code.value}"
        now = self._clock()
        with self._composition.engine.begin() as connection:
            jobs = self._composition.jobs(connection)
            audit = self._composition.audit(connection)
            if not jobs.fail(job_id=job["id"], owner=owner, code=failure.code, now=now):
                raise _LeaseLost()
            audit.record(
                AuditEvent(
                    action="reconciliation.job_failed",
                    entity_type="reconciliation_job",
                    entity_id=str(job["id"]),
                    source=AuditSource.IMPORT,
                    actor_capability=ActorCapability.SYSTEM,
                    correlation_id=job["correlation_id"],
                    payload={
                        "kind": job["kind"],
                        "failure_code": failure.code.value,
                        "attempts": job["attempts"],
                        "lease_owner": owner,
                    },
                )
            )
        return "failed"

    def _publish_stale(self, *, job, owner: str, stale: Stale) -> str:
        now = self._clock()
        with self._composition.engine.begin() as connection:
            jobs = self._composition.jobs(connection)
            audit = self._composition.audit(connection)
            if not jobs.mark_stale_under_lease(
                job_id=job["id"], owner=owner, reason=stale.reason, now=now
            ):
                raise _LeaseLost()
            audit.record(
                AuditEvent(
                    action="reconciliation.job_stale",
                    entity_type="reconciliation_job",
                    entity_id=str(job["id"]),
                    source=AuditSource.IMPORT,
                    actor_capability=ActorCapability.SYSTEM,
                    correlation_id=job["correlation_id"],
                    payload={"kind": job["kind"], "stale_reason": stale.reason.value},
                )
            )
        return "stale"

    def _publish_cancelled(self, *, job_id: UUID, owner: str) -> str:
        with self._composition.engine.begin() as connection:
            jobs = self._composition.jobs(connection)
            if not jobs.cancel_under_lease(
                job_id=job_id, owner=owner, now=self._clock()
            ):
                return "lease_lost"
        return "cancelled"

    def _abandon(self, *, job_id: UUID, owner: str):
        """The same two-branch statement the reaper uses, under our own lease.

        Returns an `Abandonment`. Zero rows has **two** causes now — the reaper
        already acted, or this attempt's effect committed — and they need
        opposite responses, so the statement tells them apart rather than
        leaving the caller to guess from a `None`.
        """
        with self._composition.engine.begin() as connection:
            jobs = self._composition.jobs(connection)
            return jobs.abandon(job_id=job_id, owner=owner, now=self._clock())

    # -- publishing an effect whose process died ----------------------------
    def recover(self, *, limit: int = EFFECT_RECOVERY_LIMIT) -> tuple[UUID, ...]:
        """Publish the results of effects whose processes died before they could.

        One transaction per job, deliberately. Reaping is one statement over up to
        twenty rows; publishing a result is two durable reads, an insert, an update
        and an audit event, and folding several of those into one transaction would
        let one unpublishable job roll back every publication beside it.

        Bounded by `limit` for the same reason the reaper's pass is: a backlog must
        not turn one tick into a long transaction — or, here, into a long series of
        them while the queue waits.

        This is **not** an execution path. No artifact is read, no import service is
        called, no authority is re-resolved, no lease is minted and `attempts` is
        not touched, so N-43's cap is neither spent nor disguised as recovery.
        """
        recovered: list[UUID] = []
        for _ in range(limit):
            job_id = self._recover_one()
            if job_id is None:
                break
            recovered.append(job_id)
        return tuple(recovered)

    def _recover_one(self):
        """One job, one transaction, under the row lock that makes it exclusive.

        The lock taken by `lock_unpublished_effect` is held for the whole of this
        transaction, so the insert, the completion and the audit event are one
        atomic publication that a second reaper cannot duplicate — it `SKIP
        LOCKED`s the row, finds nothing, and writes nothing.

        If anything here raises — the receipt cannot be read, the audit table
        refuses the event, the process dies — the transaction rolls back whole. The
        job is left `running` with `effect_committed_at` set and no result, which is
        exactly the state this method looks for, so the next pass retries it. That
        is the only idempotency mechanism it needs and the only one it has.
        """
        now = self._clock()
        with self._composition.engine.begin() as connection:
            jobs = self._composition.jobs(connection)
            job = jobs.lock_unpublished_effect()
            if job is None:
                return None
            services = self._composition.job_services(connection)
            audit = self._composition.audit(connection)
            # The immutable receipt the effect's own transaction wrote. Found by
            # the job's request key, which is what that transaction put in
            # `snapshot_imports.request_key` and what
            # `uq_reconciliation_jobs_request_key` makes unique to this job.
            receipt = services.snapshots.import_by_request_key(job["request_key"])
            summary, blocked = recovered_result(job, receipt)
            result_id = jobs.store_result(
                job_id=job["id"],
                summary=summary,
                blocked_entries=blocked,
                now=now,
                # N-24 runs from the moment the result is **produced**, and this
                # is that moment. Dating it from the effect's commit instead would
                # shorten the retention of exactly the results an operator is most
                # likely to be investigating.
                expires_at=now + timedelta(days=RESULT_RETENTION_DAYS),
            )
            if not jobs.complete_recovered_effect(
                job_id=job["id"], result_id=result_id, now=now
            ):
                # Under the held lock this cannot happen, so it is a fault rather
                # than a race: raising rolls the result row back with it.
                raise EffectPublicationUnavailable(
                    job["id"], missing="publishable state"
                )
            audit.record(
                AuditEvent(
                    action=f"reconciliation.{job['kind']}_completed",
                    entity_type="reconciliation_job",
                    entity_id=str(job["id"]),
                    source=AuditSource.SYSTEM,
                    actor_capability=ActorCapability.SYSTEM,
                    correlation_id=job["correlation_id"],
                    payload=recovery_payload(job, summary),
                )
            )
            return job["id"]

    # -- the reaper --------------------------------------------------------
    def reap(self) -> tuple[UUID, ...]:
        """One reaper pass, and the audit events its terminal branch owes.

        The transition and the event are in the same transaction, satisfying
        delivery plan §8.2's requirement that append-only audit facts record
        every terminal outcome. A job may therefore be failed by a process that
        never executed it, and the event names the job's lease history rather
        than pretending the reaper did the work (residual risk RR-14).
        """
        with self._composition.engine.begin() as connection:
            jobs = self._composition.jobs(connection)
            audit = self._composition.audit(connection)
            rows = jobs.reap()
            for row in rows:
                if row["state"] != JobState.FAILED.value:
                    continue
                audit.record(
                    AuditEvent(
                        action="reconciliation.job_failed",
                        entity_type="reconciliation_job",
                        entity_id=str(row["id"]),
                        source=AuditSource.SYSTEM,
                        actor_capability=ActorCapability.SYSTEM,
                        correlation_id=row["correlation_id"],
                        payload={
                            "kind": row["kind"],
                            "failure_code": FailureCode.ATTEMPTS_EXHAUSTED.value,
                            "attempts": row["attempts"],
                            # The lease this job last held, so an operator can
                            # find the process that stopped answering. `NULL`
                            # after the statement cleared it, which is why it is
                            # read from `RETURNING` rather than queried after.
                            "lease_owner": row["lease_owner"],
                            "reaped_by": self._instance,
                        },
                    )
                )
            return tuple(row["id"] for row in rows)


class _LeaseLost(RuntimeError):
    """Raised inside a publish transaction so the whole of it rolls back.

    Not an error condition to report: it is the correct outcome of a race the
    design anticipates, and the caller turns it into `lease_lost`.
    """


def completion_payload(job, summary: dict) -> dict:
    """The audit payload of a completed job. Counts and codes, never content.

    Built from the **stored summary's** own keys rather than from the report, so
    what the audit says and what the result holds cannot disagree. It takes the
    summary rather than the `Executed` because a recovered publication has no
    `Executed` — its summary was read back from durable rows — and the two must
    produce the same payload from the same keys rather than two payload builders
    that agree by inspection. `application/worker/recovery.py` adds the three keys
    that describe the recovery itself on top of what this returns.
    """
    payload = {
        "kind": job["kind"],
        "checksum": summary.get("checksum"),
        "folder_id": summary.get("folder_id"),
        "profile_version": summary.get("profile_version"),
        "actor_count": summary.get("actors"),
        "mapped": summary.get("mapped"),
        "unmapped": summary.get("unmapped"),
        "blocked": summary.get("blocked"),
        "would_create": summary.get("would_create"),
        "would_update": summary.get("would_update"),
        "issue_codes": sorted(
            {entry["code"] for entry in summary.get("issue_counts", ())}
        ),
    }
    if job["kind"] == JobKind.APPLY.value:
        payload.update(
            {
                "import_id": summary.get("import_id"),
                "duplicate": summary.get("duplicate"),
                "created_count": summary.get("created_count"),
                "updated_count": summary.get("updated_count"),
                "warning_count": summary.get("warning_count"),
            }
        )
    return payload


__all__ = [
    "EFFECT_PUBLICATION_GRACE_HEARTBEATS",
    "EFFECT_RECOVERY_LIMIT",
    "Tick",
    "WorkerAuthorizationPort",
    "WorkerRuntime",
    "completion_payload",
    "utcnow",
]
