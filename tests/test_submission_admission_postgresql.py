"""The admission fence, against a real PostgreSQL. Review finding B-1 (C-24).

Nine remediations tried to establish that nothing was still in flight by
*observing* something — a process, a socket, `pg_stat_activity`, a commit
watermark, a lock queue. The tenth review found the sequence that defeats all of
them, and C-23's drain read in particular:

1. the old request is accepted and pauses **before its first statement**;
2. settlement takes its lock, reads an empty queue and an unmoved watermark, and
   records a miss;
3. settlement commits, and the drain transaction takes its lock;
4. while the drain is held, the paused request finally reaches its first
   conflicting `INSERT` and queues *behind the drain*;
5. the drain reading is taken before that writer can commit, so it matches;
6. the drain commits, and the old writer commits immediately afterwards;
7. the miss has already authorized a fresh export with a different checksum, and
   route retirement cannot reach a transaction that is already inside PostgreSQL.

No observation can close that, because an observation of a resource cannot
exclude work that has been accepted and has not yet reached it. So the fence does
not observe. It **revokes**: settlement closes the admission generation the
credential writes under, and every submission transaction checks its own
credential's generation before anything of its own can become durable.

This file is the evidence, and it is deliberately built on real transaction
boundaries rather than a model of them:

- the writer is the real `SnapshotSubmissionService` over `SqlAlchemyUnitOfWork`;
- settlement is the same `FOR UPDATE`-then-`UPDATE` pair `tools.submission_admission`
  runs;
- every rendezvous is a `threading.Event`, never a sleep, so nothing here passes
  because a machine was fast enough;
- and the PostgreSQL lock behaviour the design rests on is measured here too,
  including the trap that a plain `UPDATE` takes a lock that does **not**
  conflict with a foreign key's.

All bytes are synthetic. The artifact store is a per-test temporary directory.
Nothing contacts Foundry and nothing reads a real export.
"""
from __future__ import annotations

import threading
import time
import traceback
from pathlib import Path

import pytest
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import DBAPIError

from adapters.artifacts.filesystem import FilesystemArtifactStore
from adapters.database.config import EXPECTED_DATABASES
from adapters.database.unit_of_work import SqlAlchemyUnitOfWork
from application.admissions import ADMISSION_LOCK_KEY, PRE_FENCE_PRINCIPAL
from application.errors import PersistenceError
from application.foundry.submission import (
    SUBMISSION_SCOPE,
    SnapshotSubmissionService,
    SubmissionRefused,
)
from application.service_principals import ServicePrincipal, ServicePrincipalScope
from domain.foundry import OBSERVED_DEPLOYMENT
from tests import foundry_fixtures as fx
from tests.conftest import TEST_ENVIRONMENT, close_admission, open_admission

pytestmark = pytest.mark.database

#: Bounds a hang. Never the thing being measured — every rendezvous below is an
#: event, so a slow machine makes these tests slower and never greener.
PATIENCE = 30.0

#: Long enough that a *blocked* operation is unmistakably blocked, short enough
#: that the test that wants a block reports it quickly. Only used where the
#: expected outcome is a timeout.
BLOCKED = 2.0

SUBMITTER = ServicePrincipal(
    principal_id="foundry-the-guild",
    scopes=frozenset({ServicePrincipalScope.SUBMIT_SNAPSHOT}),
)
RECOVERY = ServicePrincipal(
    principal_id="foundry-the-guild-r1",
    scopes=frozenset({ServicePrincipalScope.SUBMIT_SNAPSHOT}),
)

ACCEPTANCES = """
SELECT count(*) FROM audit_events
 WHERE action = 'snapshot_submission.accepted' AND source = 'foundry'
"""


# -- pausing the real service at a named boundary -----------------------------


class Gate:
    """One rendezvous: the worker announces it arrived, then waits to be let go."""

    def __init__(self) -> None:
        self.reached = threading.Event()
        self.release = threading.Event()

    def arrive(self) -> None:
        self.reached.set()
        assert self.release.wait(PATIENCE), "the gate was never released"

    def await_arrival(self) -> None:
        assert self.reached.wait(PATIENCE), "the worker never reached the gate"


class PausingAdmissions:
    """The real admission repository, with a gate at each interesting boundary.

    The three boundaries are the ones the review named, and they are named here
    the same way:

    `transaction_start` — the request has been accepted and has issued **no
    statement at all**. This is the state the reviewer's sequence pauses in, and
    the one no observation can see.

    `after_admission_read` — it has resolved its admission and found it open, and
    has not yet written anything.

    `before_commit` — everything is written and the transaction is one statement
    away from committing.

    `hold` exists to switch off the advisory lock. It is not a convenience: the
    fence has two independent halves, and turning one off is the only way to show
    that the other one carries the case on its own.
    """

    def __init__(self, wrapped, gates: dict[str, Gate], *, hold: bool = True) -> None:
        self._wrapped = wrapped
        self._gates = gates
        self._hold = hold

    def _pause(self, name: str) -> None:
        gate = self._gates.get(name)
        if gate is not None:
            gate.arrive()

    def hold_against_closure(self) -> None:
        self._pause("transaction_start")
        if self._hold:
            self._wrapped.hold_against_closure()

    def find_for_principal(self, principal_id: str):
        admission = self._wrapped.find_for_principal(principal_id)
        self._pause("after_admission_read")
        return admission

    def state_of(self, admission_id):
        self._pause("before_commit")
        return self._wrapped.state_of(admission_id)


class PausingIdempotency:
    """The real idempotency repository, with a gate after the key lookup.

    One boundary, and it is the one a request-key race needs: the transaction
    has taken the shared lock, resolved its admission and found the key unspent.
    Pausing there lets a second request spend the same key and commit, so the
    paused one meets a **real** 23505 from PostgreSQL rather than a modelled
    conflict — which is what makes the recovery path being tested the one
    production takes.
    """

    def __init__(self, wrapped, gates: dict[str, Gate]) -> None:
        self._wrapped = wrapped
        self._gates = gates

    def find(self, scope: str, key: str):
        found = self._wrapped.find(scope, key)
        gate = self._gates.get("after_key_lookup")
        if gate is not None:
            gate.arrive()
        return found

    def add(self, record) -> None:
        self._wrapped.add(record)


class PausingUnitOfWork:
    """`SqlAlchemyUnitOfWork` with the admission repository gated.

    Everything else is the real thing on the real connection, so the transaction
    boundaries these tests reason about are PostgreSQL's own.
    """

    def __init__(self, engine: Engine, gates: dict[str, Gate], *, hold: bool) -> None:
        self._inner = SqlAlchemyUnitOfWork(engine)
        self._gates = gates
        self._hold = hold

    def __enter__(self) -> "PausingUnitOfWork":
        inner = self._inner.__enter__()
        for name in (
            "characters",
            "discord_users",
            "sheet_row_mappings",
            "audit",
            "external_actor_mappings",
            "snapshots",
            "snapshot_imports",
            "initialization",
        ):
            setattr(self, name, getattr(inner, name))
        self.idempotency = PausingIdempotency(inner.idempotency, self._gates)
        self.submission_admissions = PausingAdmissions(
            inner.submission_admissions, self._gates, hold=self._hold
        )
        return self

    def __exit__(self, exc_type, exc, traceback_) -> None:
        self._inner.__exit__(exc_type, exc, traceback_)

    def commit(self) -> None:
        self._inner.commit()

    def rollback(self) -> None:
        self._inner.rollback()


@pytest.fixture()
def artifacts(tmp_path: Path):
    store = FilesystemArtifactStore(tmp_path / "artifacts")
    yield store
    store.close()


def service_for(engine: Engine, artifacts, gates=None, *, hold: bool = True):
    gates = gates or {}
    return SnapshotSubmissionService(
        lambda: PausingUnitOfWork(engine, gates, hold=hold),
        deployment=OBSERVED_DEPLOYMENT,
        artifacts=artifacts,
    )


def sequenced_service(engine: Engine, artifacts, plan: list[dict[str, Gate]]):
    """A service whose Nth unit of work carries `plan[N - 1]`'s gates.

    One request can span two transactions — an acceptance attempt that loses a
    uniqueness race, and the fenced replay that follows it — and the state the
    C-24-R1 counterexample turns on lives *between* them, where the request
    holds no lock at all. Gating per unit of work rather than per method is what
    lets a test pause the second transaction before its first statement and
    commit a settlement while it waits there.

    A plan entry's `unit_start` gate fires **before** the unit of work is built,
    which is a boundary outside any transaction and outside any method: it is
    reached by whatever opens the next transaction, so a test that pauses there
    does not depend on the code under test choosing to take the fence lock. That
    matters for the mutation evidence — a mutant that replays without the lock
    must still stop at this gate, so the test can go on to demonstrate that it
    answers successfully after a closure, rather than merely hanging.
    """
    plans = iter(plan)

    def factory() -> PausingUnitOfWork:
        gates = next(plans, {})
        start = gates.get("unit_start")
        if start is not None:
            start.arrive()
        return PausingUnitOfWork(engine, gates, hold=True)

    return SnapshotSubmissionService(
        factory, deployment=OBSERVED_DEPLOYMENT, artifacts=artifacts
    )


def payload(document=None) -> bytes:
    return fx.encode(document or fx.bundle())


def scalar(engine: Engine, sql: str, **parameters):
    with engine.connect() as connection:
        return connection.execute(text(sql), parameters).scalar_one()


class Worker(threading.Thread):
    """A submission on its own thread, keeping whatever it raised."""

    def __init__(self, run) -> None:
        super().__init__(daemon=True)
        self._run = run
        self.result = None
        self.error: BaseException | None = None
        self.traceback: str | None = None

    def run(self) -> None:
        try:
            self.result = self._run()
        except BaseException as error:  # noqa: BLE001 - re-raised by `outcome`
            self.error = error
            self.traceback = traceback.format_exc()

    def outcome(self):
        self.join(timeout=PATIENCE)
        assert not self.is_alive(), "the submission never finished"
        return self.result


# -- the regression the review asked for --------------------------------------


def test_a_request_paused_before_its_first_statement_is_refused_once_the_generation_closes(
    committed_database, artifacts
):
    """**The B-1 regression.** The exact sequence C-23 could not close.

    The old request is accepted and pauses before issuing any statement at all —
    so there is no process, socket, watermark, queue or lock reading that could
    see it, which is the whole point. Settlement then closes the generation and
    commits. The request wakes with nothing between it and the database.

    Under C-23 it commits, and the miss that was recorded while it slept has
    already authorized a fresh export with a different checksum. Under the fence
    it refuses itself, because the thing it is checked against is its **own
    credential's** admission, and where it was paused does not enter into it.
    """
    engine = committed_database
    open_admission(engine, SUBMITTER.principal_id)
    gates = {"transaction_start": Gate()}
    service = service_for(engine, artifacts, gates)

    worker = Worker(
        lambda: service.submit(payload(), principal=SUBMITTER, request_key="stranded")
    )
    worker.start()
    gates["transaction_start"].await_arrival()

    # Settlement, with the request paused where nothing can observe it. It does
    # not wait for anything, because the request holds nothing.
    close_admission(engine, SUBMITTER.principal_id)
    assert scalar(engine, ACCEPTANCES) == 0

    gates["transaction_start"].release.set()
    worker.outcome()

    assert isinstance(worker.error, SubmissionRefused), worker.traceback
    assert worker.error.code == "admission_closed"
    assert scalar(engine, ACCEPTANCES) == 0
    assert scalar(engine, "SELECT count(*) FROM foundry_snapshots") == 0
    assert (
        scalar(
            engine,
            "SELECT count(*) FROM idempotency_keys WHERE scope = :scope",
            scope=SUBMISSION_SCOPE,
        )
        == 0
    )


def test_a_request_paused_after_reading_its_admission_still_refuses_when_it_wakes(
    committed_database, artifacts
):
    """The second boundary: admitted, and not yet written anything.

    The advisory lock is switched off here, so this proves the *structural* half
    on its own — the foreign key and the re-read. A submission that has already
    decided its admission is open still cannot make that decision durable once a
    closure has committed.
    """
    engine = committed_database
    open_admission(engine, SUBMITTER.principal_id)
    gates = {"after_admission_read": Gate()}
    service = service_for(engine, artifacts, gates, hold=False)

    worker = Worker(
        lambda: service.submit(payload(), principal=SUBMITTER, request_key="mid")
    )
    worker.start()
    gates["after_admission_read"].await_arrival()

    close_admission(engine, SUBMITTER.principal_id)

    gates["after_admission_read"].release.set()
    worker.outcome()

    assert isinstance(worker.error, SubmissionRefused), worker.traceback
    assert worker.error.code == "admission_closed"
    assert scalar(engine, ACCEPTANCES) == 0


def test_a_request_paused_at_the_final_commit_boundary_refuses_rather_than_commits(
    committed_database, artifacts
):
    """The third boundary: everything written, one statement from committing.

    Again with the advisory lock switched off, because with it on a closure
    cannot commit while this transaction is open at all — which is the stronger
    guarantee and is proved separately below. What is proved here is that the
    last statement before the commit is decisive on its own: the snapshot row,
    the receipt and the acceptance event are all already in this transaction, and
    all three roll back.
    """
    engine = committed_database
    open_admission(engine, SUBMITTER.principal_id)
    gates = {"before_commit": Gate()}
    service = service_for(engine, artifacts, gates, hold=False)

    worker = Worker(
        lambda: service.submit(payload(), principal=SUBMITTER, request_key="last")
    )
    worker.start()
    gates["before_commit"].await_arrival()

    # The closure has to be able to take `FOR UPDATE` while this transaction
    # holds the row's `KEY SHARE` through its foreign key — it cannot, so it
    # waits. Released below; the point here is what the woken submission does.
    closure = threading.Thread(
        target=close_admission, args=(engine, SUBMITTER.principal_id), daemon=True
    )
    closure.start()
    closure.join(timeout=BLOCKED)
    assert closure.is_alive(), (
        "the closure was granted FOR UPDATE while an acceptance held the "
        "admission row's KEY SHARE lock through its foreign key. The lock modes "
        "no longer conflict, and the fence's structural half is gone."
    )

    gates["before_commit"].release.set()
    worker.outcome()
    closure.join(timeout=PATIENCE)

    # The closure was behind this acceptance, so the acceptance stands: this is
    # settlement's *hit* branch, and there is no miss to record.
    assert worker.error is None, worker.traceback
    assert worker.result.duplicate is False
    assert scalar(engine, ACCEPTANCES) == 1


# -- the ordering, in both directions -----------------------------------------


def test_a_closure_cannot_commit_while_a_submission_transaction_is_open(
    committed_database, artifacts
):
    """Acceptance first: settlement waits, and then sees the acceptance.

    This is the half of the fence that makes a *false miss* impossible rather
    than merely refusing a late acceptance. Settlement cannot read an empty
    result while an acceptance is in flight, because it cannot get to the read
    until that acceptance has committed or rolled back.
    """
    engine = committed_database
    open_admission(engine, SUBMITTER.principal_id)
    gates = {"after_admission_read": Gate()}
    service = service_for(engine, artifacts, gates)

    worker = Worker(
        lambda: service.submit(payload(), principal=SUBMITTER, request_key="ahead")
    )
    worker.start()
    gates["after_admission_read"].await_arrival()

    closure = threading.Thread(
        target=close_admission, args=(engine, SUBMITTER.principal_id), daemon=True
    )
    closure.start()
    closure.join(timeout=BLOCKED)
    assert closure.is_alive(), "settlement closed a generation under a live submission"

    gates["after_admission_read"].release.set()
    assert worker.outcome() is not None
    assert worker.error is None, worker.traceback
    closure.join(timeout=PATIENCE)
    assert not closure.is_alive()

    # Settlement now reads a database that contains the acceptance. A hit.
    assert scalar(engine, ACCEPTANCES) == 1


def test_a_submission_arriving_during_a_closure_waits_and_then_refuses(
    committed_database, artifacts
):
    """Closure first: the submission blocks on the fence and refuses when it wakes.

    The production ordering, with no test seam at all beyond holding the closure
    transaction open. The submission is not rejected at the socket, not killed,
    and not raced — it waits inside PostgreSQL and then declines to commit.
    """
    engine = committed_database
    open_admission(engine, SUBMITTER.principal_id)
    service = service_for(engine, artifacts)

    with engine.begin() as closure:
        closure.execute(
            text("SELECT pg_advisory_xact_lock(:key)"), {"key": ADMISSION_LOCK_KEY}
        )
        closure.execute(
            text(
                "SELECT id FROM submission_admissions "
                "WHERE principal_id = :p FOR UPDATE"
            ),
            {"p": SUBMITTER.principal_id},
        )
        closure.execute(
            text(
                "UPDATE submission_admissions SET state = 'closed', "
                "closed_at = now(), closed_by = 'tests', "
                "close_reason = 'Settlement.', "
                "closed_correlation_id = gen_random_uuid() "
                "WHERE principal_id = :p"
            ),
            {"p": SUBMITTER.principal_id},
        )

        worker = Worker(
            lambda: service.submit(payload(), principal=SUBMITTER, request_key="late")
        )
        worker.start()
        worker.join(timeout=BLOCKED)
        assert worker.is_alive(), "the submission did not wait for the open closure"

    worker.outcome()
    assert isinstance(worker.error, SubmissionRefused), worker.traceback
    assert worker.error.code == "admission_closed"
    assert scalar(engine, ACCEPTANCES) == 0


# -- retries, on both sides of the closure ------------------------------------


def test_a_same_key_retry_replays_while_the_generation_that_earned_it_is_open(
    committed_database, artifacts
):
    engine = committed_database
    open_admission(engine, SUBMITTER.principal_id)
    service = service_for(engine, artifacts)

    first = service.submit(payload(), principal=SUBMITTER, request_key="k")
    second = service.submit(payload(), principal=SUBMITTER, request_key="k")

    assert second.snapshot_id == first.snapshot_id
    assert second.duplicate is True
    assert scalar(engine, ACCEPTANCES) == 1


def test_a_same_key_retry_is_refused_once_its_generation_is_closed(
    committed_database, artifacts
):
    """A replay writes nothing, so the foreign key does not reach it — and it
    still may not answer.

    The invariant forbids a *successful receipt* as squarely as it forbids a new
    row: a module that received one after settlement had closed the generation
    would report success for an episode the operator has recorded as settled.
    """
    engine = committed_database
    open_admission(engine, SUBMITTER.principal_id)
    service = service_for(engine, artifacts)
    service.submit(payload(), principal=SUBMITTER, request_key="k")

    close_admission(engine, SUBMITTER.principal_id)

    with pytest.raises(SubmissionRefused) as refusal:
        service.submit(payload(), principal=SUBMITTER, request_key="k")

    assert refusal.value.code == "admission_closed"
    # The original acceptance is untouched. A refusal is not a retraction.
    assert scalar(engine, ACCEPTANCES) == 1


def _race_across(
    engine: Engine, artifacts, *, settle: bool
) -> tuple[Worker, object]:
    """The five-step interleaving of review finding C-24-R1, once.

    1. two requests authenticated as the same principal enter with the same key
       and the same bytes while the generation is open;
    2. the winner commits its accepted receipt under that generation;
    3. the loser meets the real `idempotency_key.scope_key` violation, and the
       adapter rolls its transaction back — **releasing the shared lock**;
    4. settlement closes the generation and commits, delayed by nothing,
       because the loser holds nothing; and
    5. the loser goes looking for the winner's receipt.

    Returns the loser and the winner's receipt. `settle=False` runs the same
    ordering without step 4, which is the control: it shows the interleaving
    itself is ordinary and idempotent, so what the other run demonstrates is the
    fence and not the race.
    """
    lookup = Gate()
    replay = Gate()
    loser = sequenced_service(
        engine,
        artifacts,
        [{"after_key_lookup": lookup}, {"unit_start": replay}],
    )
    winner_service = service_for(engine, artifacts)

    worker = Worker(
        lambda: loser.submit(payload(), principal=SUBMITTER, request_key="raced")
    )
    worker.start()
    lookup.await_arrival()

    winner = winner_service.submit(payload(), principal=SUBMITTER, request_key="raced")
    assert winner.duplicate is False
    assert scalar(engine, ACCEPTANCES) == 1

    # Step 3. The loser wakes, stores its (identical) bytes, finds the winner's
    # snapshot row and then loses the key on the database's own unique index.
    lookup.release.set()
    # Step 5's precondition: it is between transactions, holding no lock.
    replay.await_arrival()

    if settle:
        close_admission(engine, SUBMITTER.principal_id)

    replay.release.set()
    worker.outcome()
    return worker, winner


def test_a_request_that_loses_the_key_race_cannot_replay_across_a_closure(
    committed_database, artifacts
):
    """**The C-24-R1 regression.** A successful receipt returned after closure.

    The ordinary replay path was fenced; recovery from a lost request-key race
    was not. It opened a bare transaction, read the winning row and returned it
    — no advisory lock, no admission for the authenticated principal, no
    requirement that the generation still be open, and no check that the receipt
    was earned under it.

    No post-closure *write* is needed for that to break the invariant. Returning
    the winner's successful receipt is expressly forbidden: the module treats it
    as a submission that succeeded, while the operator has already recorded the
    episode as settled and may have authorized a fresh export.
    """
    engine = committed_database
    admission = open_admission(engine, SUBMITTER.principal_id)

    worker, winner = _race_across(engine, artifacts, settle=True)

    # The decisive outcome: a typed refusal, not a receipt.
    assert isinstance(worker.error, SubmissionRefused), worker.traceback
    assert worker.error.code == "admission_closed"
    assert worker.result is None

    # Nothing of the loser's became durable: no second snapshot, no second
    # receipt, no second acceptance event.
    assert scalar(engine, "SELECT count(*) FROM foundry_snapshots") == 1
    assert (
        scalar(
            engine,
            "SELECT count(*) FROM idempotency_keys WHERE scope = :scope",
            scope=SUBMISSION_SCOPE,
        )
        == 1
    )
    assert scalar(engine, ACCEPTANCES) == 1

    # The winner's pre-closure acceptance is intact, and it names the generation
    # it was earned under. A refusal is not a retraction.
    receipt = _rows(
        engine,
        "SELECT admission_id, response FROM idempotency_keys WHERE scope = :scope",
        scope=SUBMISSION_SCOPE,
    )[0]
    assert receipt[0] == admission
    assert receipt[1]["snapshot_id"] == str(winner.snapshot_id)

    # The closure is durable, and the old credential can do nothing with it.
    assert (
        scalar(
            engine,
            "SELECT state FROM submission_admissions WHERE principal_id = :p",
            p=SUBMITTER.principal_id,
        )
        == "closed"
    )
    with pytest.raises(SubmissionRefused) as again:
        service_for(engine, artifacts).submit(
            payload(), principal=SUBMITTER, request_key="raced"
        )
    assert again.value.code == "admission_closed"
    assert scalar(engine, ACCEPTANCES) == 1


def test_a_request_that_loses_the_key_race_replays_while_the_generation_is_open(
    committed_database, artifacts
):
    """The control. The same interleaving, one committed closure apart.

    Without the closure the loser is answered with the winner's receipt, which
    is what a lost race is *supposed* to produce: one artifact, one snapshot,
    one receipt and two callers told the same true thing. That is what makes the
    test above evidence about the fence rather than about the race.
    """
    engine = committed_database
    open_admission(engine, SUBMITTER.principal_id)

    worker, winner = _race_across(engine, artifacts, settle=False)

    assert worker.error is None, worker.traceback
    assert worker.result.snapshot_id == winner.snapshot_id
    assert worker.result.correlation_id == winner.correlation_id
    assert worker.result.duplicate is True
    assert scalar(engine, "SELECT count(*) FROM foundry_snapshots") == 1
    assert scalar(engine, ACCEPTANCES) == 1


def test_a_retry_cannot_carry_its_key_into_a_new_generation(
    committed_database, artifacts
):
    """No retry may cross a generation boundary implicitly.

    `(scope, key)` is one namespace across every credential, so the recovery
    credential *can* present a key the old generation spent. It gets a typed
    refusal rather than the old receipt: a replay is only ever answered while the
    generation that earned it is the one the presenting credential still holds.

    That is the fail-closed direction and it is the one that matters. Answering
    would hand the new generation a receipt describing an acceptance the old one
    made — a duplicate reported as a success, which is exactly the outcome
    settlement exists to prevent.
    """
    engine = committed_database
    old = open_admission(engine, SUBMITTER.principal_id, generation=1)
    service = service_for(engine, artifacts)
    service.submit(payload(), principal=SUBMITTER, request_key="shared-key")

    close_admission(engine, SUBMITTER.principal_id)
    new = open_admission(engine, RECOVERY.principal_id, generation=2)
    assert old != new

    with pytest.raises(SubmissionRefused) as refusal:
        service.submit(
            payload(fx.bundle(actors=(fx.actor(fx.SECOND_ACTOR_ID),))),
            principal=RECOVERY,
            request_key="shared-key",
        )
    assert refusal.value.code == "admission_closed"
    assert scalar(engine, ACCEPTANCES) == 1

    # Its own key succeeds, under its own generation. The refusal above is about
    # the key crossing a boundary, not about the recovery credential.
    assert service.submit(
        payload(fx.bundle(actors=(fx.actor(fx.SECOND_ACTOR_ID),))),
        principal=RECOVERY,
        request_key="recovery-key",
    )

    admissions = [
        row[0]
        for row in _rows(
            engine,
            "SELECT admission_id FROM idempotency_keys WHERE scope = :scope "
            "ORDER BY created_at",
            scope=SUBMISSION_SCOPE,
        )
    ]
    assert admissions == [old, new]


def test_the_old_credential_cannot_use_the_new_generation(
    committed_database, artifacts
):
    """The recovery generation belongs to a credential the old request never had.

    This is what makes "an old request cannot be silently upgraded" structural
    rather than procedural: `principal_id` is unique for all time, so the old
    credential's admission stays closed and there is no second row for it to
    resolve to.
    """
    engine = committed_database
    open_admission(engine, SUBMITTER.principal_id, generation=1)
    close_admission(engine, SUBMITTER.principal_id)
    open_admission(engine, RECOVERY.principal_id, generation=2)
    service = service_for(engine, artifacts)

    assert service.submit(payload(), principal=RECOVERY, request_key="fresh")

    with pytest.raises(SubmissionRefused) as refusal:
        service.submit(payload(), principal=SUBMITTER, request_key="old-route")
    assert refusal.value.code == "admission_closed"

    with pytest.raises(DBAPIError):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO submission_admissions (id, generation, "
                    "principal_id, state, opened_by, open_reason, correlation_id) "
                    "VALUES (gen_random_uuid(), 3, :p, 'open', 'x', 'y', "
                    "gen_random_uuid())"
                ),
                {"p": SUBMITTER.principal_id},
            )


# -- settlement's own edge cases ----------------------------------------------


def test_a_second_closure_of_the_same_generation_changes_nothing(
    committed_database, artifacts
):
    """Duplicate settlement. Two operators, or one repeating a lost command."""
    engine = committed_database
    open_admission(engine, SUBMITTER.principal_id)

    close_admission(engine, SUBMITTER.principal_id)
    first = _rows(engine, "SELECT closed_at, closed_by FROM submission_admissions")
    close_admission(engine, SUBMITTER.principal_id)
    second = _rows(engine, "SELECT closed_at, closed_by FROM submission_admissions")

    assert first == second


def test_a_closed_generation_cannot_be_reopened_or_deleted(committed_database):
    """Abandoned settlement fails closed, and cannot be undone quietly.

    An operator who closes a generation and walks away leaves an endpoint that
    accepts nothing. That is the fail-closed direction and it is deliberate: the
    way out is a new credential and a new generation, recorded, not a quiet
    reversal of the fence.
    """
    engine = committed_database
    open_admission(engine, SUBMITTER.principal_id)
    close_admission(engine, SUBMITTER.principal_id)

    for statement in (
        "UPDATE submission_admissions SET state = 'open', closed_at = NULL, "
        "closed_by = NULL, close_reason = NULL, closed_correlation_id = NULL",
        "DELETE FROM submission_admissions",
    ):
        with pytest.raises(DBAPIError) as refusal:
            with engine.begin() as connection:
                connection.execute(text(statement))
        # `restrict_violation`, raised by the trigger — not a privilege error and
        # not a constraint the owner could simply drop in passing.
        assert refusal.value.orig.sqlstate == "2F004" or "refused" in str(refusal.value)


def test_a_submission_with_no_admission_at_all_is_refused(
    committed_database, artifacts
):
    """A fresh deployment accepts nothing until an operator opens a generation.

    The absence of a row is never permission. This is the state between running
    migration 0005 and running `tools.submission_admission open`, and it has to
    fail closed or the fence would have a hole exactly the width of a deployment.
    """
    service = service_for(committed_database, artifacts)

    with pytest.raises(SubmissionRefused) as refusal:
        service.submit(payload(), principal=SUBMITTER, request_key="unadmitted")

    assert refusal.value.code == "admission_closed"
    assert scalar(committed_database, ACCEPTANCES) == 0


def test_the_pre_fence_generation_is_closed_and_belongs_to_no_credential(
    committed_database, artifacts
):
    """Migration 0005's generation 0 can never admit anything.

    Its principal is not a legal `ServicePrincipal` id, so no credential can
    authenticate as it, and it is created closed. Both, because either alone
    would be a single edit away from being an open generation nobody is watching.
    """
    with pytest.raises(ValueError):
        ServicePrincipal(
            principal_id=PRE_FENCE_PRINCIPAL,
            scopes=frozenset({ServicePrincipalScope.SUBMIT_SNAPSHOT}),
        )

    open_admission(
        committed_database, PRE_FENCE_PRINCIPAL, generation=0, state="closed"
    )
    assert (
        scalar(
            committed_database,
            "SELECT state FROM submission_admissions WHERE principal_id = :p",
            p=PRE_FENCE_PRINCIPAL,
        )
        == "closed"
    )


def test_an_audit_write_failure_rolls_back_the_whole_acceptance(
    committed_database, artifacts
):
    """No partial commit, with the fence in the transaction as well.

    The acceptance event is written before the fence's final re-read, so a
    failure there has to take the snapshot row, the receipt *and* the admission
    reference down with it — otherwise a receipt would exist naming a generation
    for an acceptance that was never audited.
    """
    engine = committed_database
    open_admission(engine, SUBMITTER.principal_id)

    class Exploding(PausingUnitOfWork):
        def __enter__(self):
            unit = super().__enter__()

            class RefusingAudit:
                def record(self, event):
                    raise PersistenceError("injected")

            unit.audit = RefusingAudit()
            return unit

    service = SnapshotSubmissionService(
        lambda: Exploding(engine, {}, hold=True),
        deployment=OBSERVED_DEPLOYMENT,
        artifacts=artifacts,
    )

    with pytest.raises(PersistenceError):
        service.submit(payload(), principal=SUBMITTER, request_key="audit-fails")

    assert scalar(engine, "SELECT count(*) FROM foundry_snapshots") == 0
    assert (
        scalar(
            engine,
            "SELECT count(*) FROM idempotency_keys WHERE scope = :scope",
            scope=SUBMISSION_SCOPE,
        )
        == 0
    )


def test_the_fence_survives_a_process_restart(committed_database, artifacts):
    """The admission state is in PostgreSQL, so nothing is held in a process.

    A restarted endpoint composes a new service over a new unit of work and
    reaches the same conclusion, because the fence is a row rather than a flag
    somebody would have to remember to rebuild.
    """
    engine = committed_database
    open_admission(engine, SUBMITTER.principal_id)
    close_admission(engine, SUBMITTER.principal_id)

    for _ in range(2):
        restarted = service_for(engine, artifacts)
        with pytest.raises(SubmissionRefused) as refusal:
            restarted.submit(payload(), principal=SUBMITTER, request_key="after-boot")
        assert refusal.value.code == "admission_closed"


# -- the PostgreSQL behaviour the design rests on -----------------------------
#
# The runtime role's privileges on `submission_admissions` are the other half of
# this, and they live in `tests/test_runtime_grants_live.py` because that file
# applies the real grants template before asking. See
# `test_the_admission_fence_is_readable_and_immovable_by_the_runtime_role`.


def test_a_foreign_key_insert_and_a_for_update_closure_cannot_interleave(
    committed_database
):
    """Measured, not assumed. Both directions of the row-lock conflict.

    If this ever stops holding — a PostgreSQL upgrade, a schema change that drops
    the foreign key — the structural half of the fence is gone, and the failure
    should be this test rather than a lost snapshot.
    """
    engine = committed_database
    admission = open_admission(engine, SUBMITTER.principal_id)

    # Direction 1: the acceptance's foreign key blocks a closure's `FOR UPDATE`.
    with engine.begin() as acceptance:
        acceptance.execute(
            text(
                "INSERT INTO idempotency_keys (id, scope, key, request_hash, "
                "status, admission_id) VALUES (gen_random_uuid(), :scope, 'a', "
                "decode(repeat('00', 32), 'hex'), 'completed', :admission)"
            ),
            {"scope": SUBMISSION_SCOPE, "admission": admission},
        )
        blocked = threading.Thread(
            target=_take_for_update, args=(engine, SUBMITTER.principal_id), daemon=True
        )
        blocked.start()
        blocked.join(timeout=BLOCKED)
        assert blocked.is_alive(), "FOR UPDATE was granted under a live acceptance"
    blocked.join(timeout=PATIENCE)

    # Direction 2: a held `FOR UPDATE` blocks the acceptance's foreign key.
    with engine.begin() as closure:
        closure.execute(
            text(
                "SELECT id FROM submission_admissions WHERE principal_id = :p "
                "FOR UPDATE"
            ),
            {"p": SUBMITTER.principal_id},
        )
        writer = threading.Thread(
            target=_insert_receipt, args=(engine, admission, "b"), daemon=True
        )
        writer.start()
        writer.join(timeout=BLOCKED)
        assert writer.is_alive(), "a foreign-key insert ignored a held FOR UPDATE"
    writer.join(timeout=PATIENCE)


def test_a_plain_update_does_not_conflict_with_the_foreign_key_lock(
    committed_database
):
    """The trap, kept as a test so nobody simplifies the closure into a defect.

    `UPDATE … SET state = 'closed'` takes `FOR NO KEY UPDATE`, which does **not**
    conflict with the `KEY SHARE` a foreign-key check holds. A closure written
    that way sails past an acceptance that is already waiting and fences nothing,
    while reading exactly like a fence. `tools.submission_admission` takes
    `FOR UPDATE` first for this reason and no other.
    """
    engine = committed_database
    admission = open_admission(engine, SUBMITTER.principal_id)

    with engine.begin() as acceptance:
        acceptance.execute(
            text(
                "INSERT INTO idempotency_keys (id, scope, key, request_hash, "
                "status, admission_id) VALUES (gen_random_uuid(), :scope, 'c', "
                "decode(repeat('00', 32), 'hex'), 'completed', :admission)"
            ),
            {"scope": SUBMISSION_SCOPE, "admission": admission},
        )
        naive = threading.Thread(target=_naive_close, args=(engine,), daemon=True)
        naive.start()
        naive.join(timeout=BLOCKED)
        assert not naive.is_alive(), (
            "a plain UPDATE now blocks on the foreign-key lock. If PostgreSQL "
            "has changed this, the reason `tools.submission_admission` takes "
            "FOR UPDATE first has changed with it — re-derive it before relying "
            "on either."
        )


# -- the transaction-isolation contract ---------------------------------------
#
# The re-read before the commit is only a *fresh* reading under `READ
# COMMITTED`, where every statement takes its own snapshot. The code said so in
# a comment while the unit of work took whatever `default_transaction_isolation`
# the database or the login role carried — a setting outside this repository
# that nothing here would have noticed changing.
#
# The decisive interleaving was run at all three levels against this host's
# PostgreSQL 16.14 before the pin existed, and the results are recorded in
# `adapters/database/unit_of_work.py`: `READ COMMITTED` refuses with the typed
# `admission_closed`; `REPEATABLE READ` and `SERIALIZABLE` are aborted by
# PostgreSQL with **SQLSTATE 40001** when the foreign key tries to take its
# `KEY SHARE` lock on a row updated after the snapshot. No level ever produced a
# durable post-closure acceptance, so the non-default levels fail closed — that
# is hardening evidence, not a second B-1. What they lost was the *typed*
# refusal the runbook tells an operator to expect, which is what the pin
# restores.


@pytest.mark.parametrize("engine_level", ["REPEATABLE READ", "SERIALIZABLE"])
def test_the_unit_of_work_pins_read_committed_over_any_engine_default(
    committed_database, engine_level: str
):
    """The contract, asserted directly: the pin wins over the engine's level."""
    engine = committed_database.execution_options(isolation_level=engine_level)

    with SqlAlchemyUnitOfWork(engine) as unit_of_work:
        level = unit_of_work._session.execute(
            text("SHOW transaction_isolation")
        ).scalar_one()

    assert level == "read committed", (
        f"the unit of work inherited {level!r} from the engine. The admission "
        "re-read before the commit assumes a per-statement snapshot; without "
        "one it reads its own stale view of the fence."
    )


@pytest.fixture()
def database_defaulting_to_repeatable_read(committed_database, database_url: str):
    """The threat as a deployment would actually create it, not as an option.

    `ALTER DATABASE … SET default_transaction_isolation` (or the same on a login
    role) is the configuration this pin exists to survive: it lives outside this
    repository, applies to every new connection, and nothing in the application
    would report it. A fresh engine is handed out because the setting takes
    effect at connect time, and the shared engine's pool is disposed afterwards
    so no connection carries the hostile default into a later test.
    """
    database = EXPECTED_DATABASES[TEST_ENVIRONMENT]
    with committed_database.begin() as connection:
        connection.execute(
            text(
                f'ALTER DATABASE "{database}" SET default_transaction_isolation '
                "= 'repeatable read'"
            )
        )
    engine = create_engine(database_url)
    try:
        yield engine
    finally:
        engine.dispose()
        with committed_database.begin() as connection:
            connection.execute(
                text(
                    f'ALTER DATABASE "{database}" RESET default_transaction_isolation'
                )
            )
        committed_database.dispose()


def test_the_unit_of_work_pins_read_committed_over_a_server_side_default(
    database_defaulting_to_repeatable_read,
):
    """The decisive form of the contract, against a real server-side default."""
    engine = database_defaulting_to_repeatable_read

    # The control. Without it this test could pass against a database where the
    # hostile default was never established.
    with engine.connect() as connection:
        inherited = connection.execute(text("SHOW transaction_isolation")).scalar_one()
    with SqlAlchemyUnitOfWork(engine) as unit_of_work:
        pinned = unit_of_work._session.execute(
            text("SHOW transaction_isolation")
        ).scalar_one()

    assert inherited == "repeatable read", (
        "the database default was not established, so this proves nothing"
    )
    assert pinned == "read committed"


@pytest.mark.parametrize("engine_level", ["REPEATABLE READ", "SERIALIZABLE"])
def test_a_closure_committing_while_a_submission_is_blocked_still_refuses(
    committed_database, artifacts, engine_level: str
):
    """**The isolation experiment, as a regression.**

    The one interleaving where a stale snapshot could have mattered, and it is
    reachable with the advisory lock in place rather than in spite of it:

    1. the closure takes the exclusive advisory lock and holds it;
    2. the submission's **first statement** — the shared advisory lock — begins,
       which is where its transaction snapshot is taken, and *then* blocks;
    3. the closure commits;
    4. the submission wakes holding a snapshot from before that commit.

    Under a non-default level, steps 2 and 4 mean the admission read and the
    re-read before the commit both see `open`. The pin is what makes them see
    what actually happened, so the caller gets `admission_closed` rather than
    the generic `PersistenceError` PostgreSQL's own 40001 abort produces.

    Either way nothing durable is written — which is why this is stated as
    hardening. The assertion that matters most is the last three: no snapshot,
    no receipt, no acceptance event.
    """
    engine = committed_database.execution_options(isolation_level=engine_level)
    open_admission(committed_database, SUBMITTER.principal_id)
    gates = {"transaction_start": Gate()}
    service = service_for(engine, artifacts, gates)

    holding = threading.Event()
    may_commit = threading.Event()

    def closure() -> None:
        with committed_database.begin() as connection:
            connection.execute(
                text("SELECT pg_advisory_xact_lock(:key)"),
                {"key": ADMISSION_LOCK_KEY},
            )
            holding.set()
            assert may_commit.wait(PATIENCE), "the closure was never released"
            connection.execute(
                text(
                    "SELECT id FROM submission_admissions WHERE principal_id = :p "
                    "FOR UPDATE"
                ),
                {"p": SUBMITTER.principal_id},
            )
            connection.execute(
                text(
                    "UPDATE submission_admissions SET state = 'closed', "
                    "closed_at = now(), closed_by = 'tests', "
                    "close_reason = 'Settlement, in a test.', "
                    "closed_correlation_id = gen_random_uuid() "
                    "WHERE principal_id = :p AND state = 'open'"
                ),
                {"p": SUBMITTER.principal_id},
            )

    closer = Worker(closure)
    closer.start()
    assert holding.wait(PATIENCE), "the closure never took the advisory lock"

    worker = Worker(
        lambda: service.submit(payload(), principal=SUBMITTER, request_key="stranded")
    )
    worker.start()
    gates["transaction_start"].await_arrival()
    gates["transaction_start"].release.set()
    _await_advisory_lock_waiter(committed_database)

    # Only now, with the submission's snapshot already taken and its statement
    # blocked, does the closure become durable.
    may_commit.set()
    closer.outcome()
    worker.outcome()

    assert isinstance(worker.error, SubmissionRefused), worker.traceback
    assert worker.error.code == "admission_closed"
    assert scalar(engine, ACCEPTANCES) == 0
    assert scalar(engine, "SELECT count(*) FROM foundry_snapshots") == 0
    assert (
        scalar(
            engine,
            "SELECT count(*) FROM idempotency_keys WHERE scope = :scope",
            scope=SUBMISSION_SCOPE,
        )
        == 0
    )


# -- helpers ------------------------------------------------------------------


def _await_advisory_lock_waiter(engine: Engine) -> None:
    """Block until some backend is *waiting* on the fence's advisory lock.

    A condition wait against PostgreSQL's own `pg_locks`, not a sleep: it returns
    the moment the state exists and fails the test if it never does, so a slow
    machine makes this slower and never greener. It is needed because "a
    statement has begun and is now blocked" is a state inside PostgreSQL, and no
    `threading.Event` in this process can observe it.
    """
    deadline = time.monotonic() + PATIENCE
    while time.monotonic() < deadline:
        with engine.connect() as connection:
            waiting = connection.execute(
                text(
                    "SELECT count(*) FROM pg_locks "
                    "WHERE locktype = 'advisory' AND NOT granted"
                )
            ).scalar_one()
        if waiting:
            return
        time.sleep(0.005)
    raise AssertionError("no backend ever queued for the advisory lock")


def _rows(engine: Engine, sql: str, **parameters):
    with engine.connect() as connection:
        return [tuple(row) for row in connection.execute(text(sql), parameters)]


def _take_for_update(engine: Engine, principal_id: str) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "SELECT id FROM submission_admissions WHERE principal_id = :p "
                "FOR UPDATE"
            ),
            {"p": principal_id},
        )


def _insert_receipt(engine: Engine, admission, key: str) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO idempotency_keys (id, scope, key, request_hash, "
                "status, admission_id) VALUES (gen_random_uuid(), :scope, :key, "
                "decode(repeat('00', 32), 'hex'), 'completed', :admission)"
            ),
            {"scope": SUBMISSION_SCOPE, "key": key, "admission": admission},
        )


def _naive_close(engine: Engine) -> None:
    """Closure written the obvious way, with no `FOR UPDATE`. Not the real one."""
    with engine.begin() as connection:
        connection.execute(
            text(
                "UPDATE submission_admissions SET state = 'closed', "
                "closed_at = now(), closed_by = 'naive', "
                "close_reason = 'no FOR UPDATE', "
                "closed_correlation_id = gen_random_uuid() WHERE state = 'open'"
            )
        )
