"""C-23's settlement lock, kept as the record of a **withdrawn** condition.

**§9 no longer does any of this.** C-24 replaced observation-based settlement
with the admission fence: settlement closes the submitting credential's
generation, and every submission checks its own generation inside its own
transaction. `tests/test_submission_admission_postgresql.py` is the evidence for
the live procedure; this file is the evidence for why the previous one went.

It is retained rather than deleted because what it establishes is exactly the
argument against reintroducing it. Everything below is true of PostgreSQL and was
true of C-23's procedure — the `SHARE` lock does delay a conflicting `INSERT`, a
waiting writer does appear as an ungranted `RowExclusiveLock`, a second `LOCK
TABLE` is granted only behind the queue — and **none of it was sufficient**,
because a request that had not yet issued its first conflicting statement was
invisible to all of it and committed when it woke. A future author who proposes a
lock-and-read settlement should be able to see both halves here: that the
mechanism works exactly as advertised, and that working exactly as advertised was
never enough.

The original description of what this file proved follows.

§9's settlement lock against a real PostgreSQL.

`tests/test_snapshot_recovery_settlement.py` models S-D.3's lock at the commit
boundary of a fake unit of work, which is where a test without a database can
observe it. What it cannot establish is the behaviour the procedure actually
rests on, and the ninth B-1 finding is precisely a claim about that behaviour:

- a `SHARE` lock **delays** a conflicting `INSERT` rather than refusing it, so a
  submission delivered while the lock is held does not go away — it waits,
  inside PostgreSQL, past every hop S-A, S-I and step 4's route retirement can
  act on;
- while it waits it is an **ungranted `RowExclusiveLock`**, visible to the
  locking session in exactly the `pg_locks` query §9 documents. That reading is
  S-D.4's, and a row in it makes the episode Unsettled rather than a miss;
- when the settlement transaction commits, the waiting submission commits **at
  once** — before step 4 has retired anything;
- and a second acquisition of the same lock is granted only **behind** the
  requests already queued, which is what makes S-D.4's drain read include their
  commits and what lets a miss be retracted before a fresh export is authorized;
- an `idle_in_transaction_session_timeout` bounds the platform-wide pause the
  lock causes. §9 sets it to ten minutes; the value `0`, which an earlier
  version used, is what removes the bound.

Every one of those is PostgreSQL's behaviour rather than the application's, so
every one of them is asserted here against the disposable `freedom_test`
database over the Unix-domain socket. The writer in the first test is the real
`SnapshotSubmissionService` over `SqlAlchemyUnitOfWork`, because the claim is
about what a real submission does when it meets the lock.

All bytes are synthetic and the artifact store is a per-test temporary
directory. Nothing here reads an existing export directory, and nothing
contacts Foundry.
"""
from __future__ import annotations

import threading
import time
import traceback
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import Connection, Engine, create_engine, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.pool import NullPool

from adapters.artifacts.filesystem import FilesystemArtifactStore
from adapters.database.unit_of_work import SqlAlchemyUnitOfWork
from application.foundry.submission import SnapshotSubmissionService
from application.service_principals import ServicePrincipal, ServicePrincipalScope
from domain.foundry import OBSERVED_DEPLOYMENT
from tests import foundry_fixtures as fx
from tests.conftest import open_admission

pytestmark = pytest.mark.database

#: How long a test may wait for something it expects to happen. Generous: it
#: bounds a hang and is never the thing being measured.
PATIENCE = 30.0

SUBMITTER = ServicePrincipal(
    principal_id="foundry-the-guild",
    scopes=frozenset({ServicePrincipalScope.SUBMIT_SNAPSHOT}),
)

#: S-D.3's lock, as §9 gives it.
SETTLEMENT_LOCK = "LOCK TABLE foundry_snapshots, audit_events IN SHARE MODE"

#: S-D.4's queue reading, as §9 gives it: ungranted requests on either table,
#: from any backend but this one. Over `pg_locks` **alone**, which is read live
#: from the lock manager — see the staleness test below for why the obvious join
#: to `pg_stat_activity` cannot be the decisive reading.
QUEUED_WRITERS = """
SELECT l.pid, l.mode, l.relation::regclass::text AS relation
  FROM pg_locks AS l
 WHERE NOT l.granted
   AND l.locktype = 'relation'
   AND l.pid <> pg_backend_pid()
   AND l.relation IN ('foundry_snapshots'::regclass, 'audit_events'::regclass)
"""

#: §9's follow-up, which names the sessions behind those pids for the record.
#: The reset is not decoration: without it this answers from the backend-status
#: snapshot taken at the transaction's first read.
IDENTIFY_QUEUED_WRITERS = """
SELECT l.pid, l.mode, a.usename, a.state, a.query_start
  FROM pg_locks AS l
  JOIN pg_stat_activity AS a ON a.pid = l.pid
 WHERE NOT l.granted
   AND l.locktype = 'relation'
   AND l.pid <> pg_backend_pid()
   AND l.relation IN ('foundry_snapshots'::regclass, 'audit_events'::regclass)
"""

#: S-D.3's `held` confirmation.
HELD = """
SELECT count(*) AS held FROM pg_locks
 WHERE locktype = 'relation' AND mode = 'ShareLock' AND granted
   AND pid = pg_backend_pid()
   AND relation IN ('foundry_snapshots'::regclass, 'audit_events'::regclass)
"""

ACCEPTANCE_EVENTS = """
SELECT count(*) FROM audit_events
 WHERE action = 'snapshot_submission.accepted'
   AND entity_type = 'foundry_snapshot'
   AND source = 'foundry'
"""


@pytest.fixture()
def submissions(committed_database: Engine, tmp_path: Path):
    """The real submission service, writing to the real database."""
    # C-24: an open admission generation, as a deployment has. These tests are
    # about the *lock* behaviour C-23 rested on, so the fence is left open here
    # and closed deliberately in `test_submission_admission_postgresql.py`.
    open_admission(committed_database, SUBMITTER.principal_id)
    store = FilesystemArtifactStore(tmp_path / "artifacts")
    service = SnapshotSubmissionService(
        lambda: SqlAlchemyUnitOfWork(committed_database),
        deployment=OBSERVED_DEPLOYMENT,
        artifacts=store,
    )
    yield service
    store.close()


def watermark(connection: Connection) -> tuple[int, int]:
    """S-D.2's commit watermark, over the two append-only tables."""
    snapshots = connection.execute(
        text("SELECT count(*) FROM foundry_snapshots")
    ).scalar_one()
    events = connection.execute(
        text(
            "SELECT count(*) FROM audit_events "
            "WHERE entity_type = 'foundry_snapshot'"
        )
    ).scalar_one()
    return (snapshots, events)


def queued_writers(connection: Connection) -> list[dict[str, object]]:
    return [
        dict(row) for row in connection.execute(text(QUEUED_WRITERS)).mappings().all()
    ]


def identify_queued_writers(connection: Connection) -> list[dict[str, object]]:
    """§9's identifying query, with the snapshot reset it requires."""
    connection.execute(text("SELECT pg_stat_clear_snapshot()"))
    return [
        dict(row)
        for row in connection.execute(text(IDENTIFY_QUEUED_WRITERS)).mappings().all()
    ]


def settlement_session(engine: Engine, *, idle_timeout: str = "10min") -> Connection:
    """A connection with §9's two session settings applied, outside a transaction."""
    connection = engine.connect()
    connection.execute(text("SET lock_timeout = '15s'"))
    connection.execute(
        text(f"SET idle_in_transaction_session_timeout = '{idle_timeout}'")
    )
    connection.commit()
    return connection


def append_snapshot_event(connection: Connection) -> None:
    """One `foundry_snapshot` audit row — a writer the settlement lock conflicts with."""
    connection.execute(
        text(
            "INSERT INTO audit_events (id, actor_discord_user_id, actor_capability, "
            "action, entity_type, entity_id, source, correlation_id, payload) VALUES "
            "(:id, NULL, 'service_principal', 'snapshot_submission.accepted', "
            "'foundry_snapshot', :entity_id, 'foundry', :correlation, '{}'::jsonb)"
        ),
        {"id": uuid4(), "entity_id": str(uuid4()), "correlation": uuid4()},
    )


def wait_until(predicate, message: str):
    """Poll until `predicate` returns something truthy, or fail with `message`."""
    deadline = time.monotonic() + PATIENCE
    while time.monotonic() < deadline:
        result = predicate()
        if result:
            return result
        time.sleep(0.02)
    raise AssertionError(message)


def test_the_settlement_lock_delays_a_real_submission_rather_than_disposing_of_it(
    committed_database, submissions
):
    """B-1, ninth finding, against the database the claim is about.

    The reviewer's sequence, executed: the lock is taken, the decisive reading
    says nothing has committed, a real submission arrives and **queues** behind
    the lock, the miss is recorded from a reading that could not move — and the
    submission commits the instant the transaction ends, which is before step 4
    can retire any route. Route retirement cannot reach a transaction that is
    already inside PostgreSQL.

    What sees it is S-D.4: the queue reading, taken inside the lock, and the
    drain read taken afterwards.
    """
    engine = committed_database
    failures: list[str] = []
    receipts: list[object] = []

    def submit() -> None:
        try:
            receipts.append(
                submissions.submit(
                    fx.encode(fx.bundle()),
                    principal=SUBMITTER,
                    request_key="pinned-episode-key",
                )
            )
        except BaseException:  # noqa: BLE001 - reported, not swallowed
            failures.append(traceback.format_exc())

    owner = settlement_session(engine)
    worker = threading.Thread(target=submit, daemon=True)
    try:
        with owner.begin():
            owner.execute(text(SETTLEMENT_LOCK))
            assert owner.execute(text(HELD)).scalar_one() == 2

            decisive = watermark(owner)
            assert decisive == (0, 0)
            # Nothing is queued yet, which is what makes the reading below mean
            # something.
            assert queued_writers(owner) == []

            # The episode's stranded request is delivered by something in front
            # of this host, and reaches its INSERT.
            worker.start()

            def queued_or_failed():
                assert not failures, failures
                return queued_writers(owner)

            waiting = wait_until(
                queued_or_failed,
                "the submission never queued behind the settlement lock",
            )

            # It is waiting, not failing and not gone: a delayed commit.
            assert len(waiting) == 1
            assert waiting[0]["mode"] == "RowExclusiveLock"
            assert waiting[0]["relation"] in ("foundry_snapshots", "audit_events")
            assert not failures, failures

            # And it can be named for the record, once the cached activity
            # snapshot is discarded.
            identified = identify_queued_writers(owner)
            assert [row["pid"] for row in identified] == [waiting[0]["pid"]]
            assert identified[0]["state"] == "active"

            # Everything S-D.3 claims is true while it waits: the door is shut,
            # the decisive reading cannot move, and the query the outcome is
            # written from returns nothing.
            assert watermark(owner) == decisive
            assert owner.execute(text(ACCEPTANCE_EVENTS)).scalar_one() == 0

            # …and the miss recorded here would still be false, which is the
            # finding. The queue reading above is what forbids recording it.
            assert queued_writers(owner)

        # The COMMIT. The waiting submission is granted its lock immediately.
        worker.join(PATIENCE)
        assert not worker.is_alive()
        assert not failures, failures
        assert len(receipts) == 1

        # S-D.4's drain read: the same lock, taken again in the same session.
        with owner.begin():
            owner.execute(text(SETTLEMENT_LOCK))
            drained = watermark(owner)
            accepted = owner.execute(text(ACCEPTANCE_EVENTS)).scalar_one()

        # It has moved, so §9 retracts the miss — before a fresh export is
        # authorized, and long before step 4 could have retired anything.
        assert drained == (1, 1)
        assert drained != decisive
        assert accepted == 1
    finally:
        owner.close()
        worker.join(PATIENCE)


def test_the_drain_read_is_granted_only_behind_the_writer_that_was_queued(
    committed_database,
):
    """Why S-D.4's second reading sees a commit it did not wait for by luck.

    PostgreSQL queues a new conflicting request behind requests that are already
    waiting rather than granting it ahead of them, so the second `LOCK TABLE` is
    granted only once the writer that was queued behind the first has ended its
    transaction. That is the whole basis of the drain read, and it is asserted
    here as ordering rather than as timing: the writer holds its transaction
    open after its `INSERT`, and the drain request is observed **ungranted**
    from a third session while it does.
    """
    engine = committed_database
    inserted = threading.Event()
    may_commit = threading.Event()
    failures: list[str] = []

    def writer() -> None:
        try:
            with engine.connect() as connection:
                with connection.begin():
                    append_snapshot_event(connection)
                    inserted.set()
                    assert may_commit.wait(PATIENCE), "the writer was never released"
        except BaseException:  # noqa: BLE001 - reported, not swallowed
            failures.append(traceback.format_exc())

    owner = settlement_session(engine)
    drain: dict[str, tuple[int, int]] = {}

    def take_the_drain_read() -> None:
        try:
            with owner.begin():
                owner.execute(text(SETTLEMENT_LOCK))
                drain["watermark"] = watermark(owner)
        except BaseException:  # noqa: BLE001 - reported, not swallowed
            failures.append(traceback.format_exc())

    worker = threading.Thread(target=writer, daemon=True)
    drainer = threading.Thread(target=take_the_drain_read, daemon=True)
    try:
        owner_pid = owner.execute(text("SELECT pg_backend_pid()")).scalar_one()
        owner.commit()

        with owner.begin():
            owner.execute(text(SETTLEMENT_LOCK))
            decisive = watermark(owner)
            worker.start()
            wait_until(
                lambda: queued_writers(owner),
                "the writer never queued behind the settlement lock",
            )
            assert not inserted.is_set(), "the INSERT ran while the lock was held"

        # The lock is released, and the writer that was queued gets in at once —
        # while still holding its own transaction open.
        assert inserted.wait(PATIENCE), "the queued writer never ran its INSERT"

        # The drain read now asks for the same lock, and must wait for it.
        drainer.start()
        with engine.connect() as observer:
            wait_until(
                lambda: observer.execute(
                    text(
                        "SELECT count(*) FROM pg_locks WHERE NOT granted "
                        "AND locktype = 'relation' AND pid = :pid "
                        "AND relation IN ('foundry_snapshots'::regclass, "
                        "'audit_events'::regclass)"
                    ),
                    {"pid": owner_pid},
                ).scalar_one(),
                "the drain read was granted without waiting for the queued writer",
            )
        assert "watermark" not in drain

        # Only when the writer's transaction ends is the drain read granted, and
        # what it reads includes that writer's commit.
        may_commit.set()
        drainer.join(PATIENCE)
        worker.join(PATIENCE)
        assert not failures, failures
        assert drain["watermark"] == (0, 1)
        assert drain["watermark"] != decisive
    finally:
        may_commit.set()
        worker.join(PATIENCE)
        drainer.join(PATIENCE)
        owner.close()


def test_the_queue_reading_cannot_be_answered_from_a_cached_activity_snapshot(
    committed_database,
):
    """Why S-D.4's decisive reading is over `pg_locks` alone.

    The obvious form of the query joins `pg_stat_activity` to name the waiting
    session — and inside S-D.3's long-lived transaction that form is **wrong**.
    `pg_locks` is read live from the lock manager, but a backend-status snapshot
    is taken at the first `pg_stat_activity` read in a transaction and reused for
    the rest of it. §9 takes the queue reading twice inside one transaction, and
    the second one is the reading that has to see a writer which arrived *while
    the outcome was being written* — a backend that, in the case that matters,
    connected after the snapshot was taken and is therefore not in it at all.
    The join then returns nothing while `pg_locks` shows the waiter, which is
    the ninth finding again with an extra step.

    The writer here connects through a `NullPool` engine so that its backend is
    genuinely new: a pooled connection that already existed when the snapshot
    was taken is present in it, with stale `state`, which hides the defect
    rather than removing it.

    This was found by running the procedure against a real database rather than
    by reasoning about it, which is what this file is for. `pg_stat_clear_
    snapshot()` is what makes the identifying query current, and the decisive
    reading does not depend on it at all.
    """
    engine = committed_database
    may_commit = threading.Event()
    failures: list[str] = []
    #: Always a new backend, never one that was connected before the snapshot.
    writer_engine = create_engine(engine.url, poolclass=NullPool)

    def writer() -> None:
        try:
            with writer_engine.connect() as connection:
                with connection.begin():
                    append_snapshot_event(connection)
                    assert may_commit.wait(PATIENCE), "the writer was never released"
        except BaseException:  # noqa: BLE001 - reported, not swallowed
            failures.append(traceback.format_exc())

    owner = settlement_session(engine)
    worker = threading.Thread(target=writer, daemon=True)
    try:
        with owner.begin():
            owner.execute(text(SETTLEMENT_LOCK))

            # The transaction's first read of the statistics: this is what gets
            # cached, and at this instant the writer has not even connected.
            assert owner.execute(text(IDENTIFY_QUEUED_WRITERS)).mappings().all() == []

            # …and only now does a writer arrive and queue behind the lock.
            worker.start()
            waiting = wait_until(
                lambda: queued_writers(owner),
                "the writer never queued behind the settlement lock",
            )
            assert len(waiting) == 1
            assert not failures, failures

            # The joined form still says the queue is empty, because the backend
            # holding that ungranted request is not in the cached snapshot.
            assert owner.execute(text(IDENTIFY_QUEUED_WRITERS)).mappings().all() == []

            # The reset is what makes the join current again.
            identified = identify_queued_writers(owner)
            assert [row["pid"] for row in identified] == [waiting[0]["pid"]]
    finally:
        may_commit.set()
        worker.join(PATIENCE)
        owner.close()
        writer_engine.dispose()
    assert not failures, failures


def test_an_empty_queue_and_an_unmoved_drain_read_are_what_a_true_miss_rests_on(
    committed_database,
):
    """The control. Without it the two readings above would prove nothing.

    The same settlement transaction with nothing delivered into the window: the
    queue reading is empty at both of its points, the drain read is granted
    without waiting, and it matches the decisive reading. This is the only shape
    in which §9 permits a fresh export.
    """
    engine = committed_database
    owner = settlement_session(engine)
    try:
        with owner.begin():
            owner.execute(text(SETTLEMENT_LOCK))
            decisive = watermark(owner)
            assert decisive == (0, 0)
            assert queued_writers(owner) == []
            # The repeat §9 takes as the last statement before the COMMIT.
            assert queued_writers(owner) == []
            assert owner.execute(text(HELD)).scalar_one() == 2

        with owner.begin():
            owner.execute(text(SETTLEMENT_LOCK))
            assert watermark(owner) == decisive
    finally:
        owner.close()


def test_a_bounded_idle_timeout_ends_the_platform_wide_pause_and_the_episode(
    committed_database,
):
    """The abandonment bound, and what it costs the episode when it fires.

    S-D.3's transaction blocks every audit insert on the platform, so §9 bounds
    how long an unattended session may hold it: `idle_in_transaction_session_
    timeout` is set to a value exceeding the recording window rather than to
    `0`, which is what an earlier version used and what removes the bound
    entirely. A tenth of a second stands in for the ten minutes here.

    Two things follow when it expires, and both are asserted: the waiting writer
    is released, so an abandoned settlement cannot pause the platform for ever;
    and the settlement session is terminated with its transaction aborted, so
    its `COMMIT` cannot succeed — which §9 classifies as Unsettled, never as a
    miss.
    """
    engine = committed_database
    committed = threading.Event()
    failures: list[str] = []

    def writer() -> None:
        try:
            with engine.connect() as connection:
                with connection.begin():
                    append_snapshot_event(connection)
            committed.set()
        except BaseException:  # noqa: BLE001 - reported, not swallowed
            failures.append(traceback.format_exc())

    owner = settlement_session(engine, idle_timeout="100ms")
    worker = threading.Thread(target=writer, daemon=True)
    try:
        transaction = owner.begin()
        owner.execute(text(SETTLEMENT_LOCK))
        worker.start()
        wait_until(
            lambda: queued_writers(owner),
            "the writer never queued behind the settlement lock",
        )

        # The operator is called away. The session is idle in transaction, and
        # the bound is what ends the pause.
        assert committed.wait(PATIENCE), (
            "the idle timeout never released the platform-wide pause"
        )
        assert not failures, failures

        # And the episode pays for it: the settlement transaction is gone, so
        # the reading was not held through the recording.
        with pytest.raises(DBAPIError):
            owner.execute(text("SELECT 1")).scalar_one()
        transaction.close()
    finally:
        worker.join(PATIENCE)
        owner.close()

    # The writer's row is durable, which is what the retracted miss would have
    # been recorded against.
    with engine.connect() as reader:
        assert watermark(reader) == (0, 1)
