"""Withdrawn settlement conditions, and every false miss each of them permitted.

**§9 no longer performs any of the settlement modelled here.** C-24 replaced it
with the admission fence — see `tests/test_submission_admission_postgresql.py`
for the live procedure's evidence and `application/admissions.py` for why an
observation could never have closed finding B-1.

This file is retained as the record of *why* each withdrawn condition went. Every
test below reproduces a false miss that a previous version of §9 permitted: the
probe's, the one an endpoint-only stop permits while the proxy still holds a
request it has not dialled upstream for, the one an unenumerated ingress commits
between two readings, the one it commits after the closing reading while the miss
is being written down, and the one it commits the instant S-D.3's lock is
released. Read together they are the argument the tenth review made: each
condition was sound about what it measured, and not one of them could exclude a
request that had not yet arrived.

The original description of what this file proved follows.

The late-commit race the lost-pin reconciliation has to survive.

Finding B-1, 2026-08-10. The §9 procedure used to let an operator record a
**miss** — and authorize a fresh export — after the client's request had timed
out and two acceptance-event queries had returned nothing. A client timeout
proves only that the browser stopped waiting. This sequence stayed reachable:

1. the POST reaches the server and keeps processing;
2. the client times out, the Foundry page is reloaded, the in-memory pin and its
   derived idempotency key are lost;
3. both reconciliation queries run before the server transaction commits;
4. both return nothing, so the procedure authorizes a fresh export;
5. the original request commits.

The fresh export mints a new checksum, so the checksum uniqueness constraint
cannot merge them: one real submission becomes two pending artifacts.

`test_the_late_commit_sequence_...` reproduces exactly that, deterministically,
against the real `SnapshotSubmissionService`. It is the regression test for the
defect: it is what "two immediate misses" was measuring, and it shows the answer
was wrong.

Two attempts to settle the question against a **running** endpoint were made and
both are withdrawn, because neither could establish that nothing would arrive
later:

- a probe answered by the same process. It proves only that every request the
  endpoint had already *accepted* was already served, and the submission travels
  browser → Caddy → loopback while the probe goes straight to loopback, so a
  submission Caddy is still holding has not reached the endpoint at all;
- Caddy's `caddy_http_requests_in_flight`, which Caddy documents as the requests
  *currently being handled* — not an accepted connection whose request has not
  entered the handler, and not body bytes still arriving on an established one.

`test_a_probe_can_be_answered_before_...` is the reproduction of the false miss
the probe rule permitted, kept as the record of why it is gone.

A third settled an episode by **state rather than observation** — the endpoint is
not running, and does not run again until the outcome is recorded — and scoped
that state to the endpoint alone. An unserved port cannot accept, and nothing on
this path commits without first being accepted, so that disposes of every request
that had reached the endpoint. It does not reach a request the proxy holds and
has **not dialled upstream for**: that one has made no attempt to fail, so no
retry rule governs it, and its first dial can land after the restart.
`test_a_request_held_by_the_proxy_commits_after_the_endpoint_restarts` is the
reproduction of that false miss, and it is the reason §9 now terminates the proxy
as well (S-I) and retires the route the episode used.

Four tests establish the current rule, all against a real
`wsgiref.simple_server` over the real WSGI application:

- `test_a_submission_queued_at_the_endpoint_commits_nothing_once_it_stops` takes
  the hardest case S-A covers: a submission connected, fully sent, and waiting in
  the endpoint's accept queue — where a request Caddy forwarded an instant before
  the stop would be — and shows it commits nothing when the endpoint stops
  without serving it;
- `test_nothing_can_be_delivered_to_the_endpoint_once_it_has_stopped` shows the
  other half: what committed before the stop is visible to the query, and a
  delivery attempted afterwards is refused at the socket and reaches no handler;
- the two `_a_request_held_by_the_proxy_` tests are S-I, and they are each
  other's control. They run **the same** episode — `_held_request_episode`, one
  function, one sequence — and differ in one statement inside it: terminate the
  proxy, and the held request stops existing; leave it running, and it commits
  across the restart. Sharing the scenario is what makes that claim checkable
  rather than asserted: delete `proxy.terminate()` and the two tests execute
  identical code, so the one that expects the request to have died fails on
  `assert not episode.proxy.dialled`, which is where the proxy forwarded across
  the restart. An earlier version of this pair was two hand-written copies whose
  sequences diverged, and the same deletion blocked on a `join()` instead —
  the control was described rather than committed.

A fourth settlement rule was **S-D.2's first two readings** — `caddy.service`'s
`InvocationID` and enter timestamp, and a listener sample — compared at the two
ends of the down window, on the stated grounds that a start mechanism nobody
enumerated "still mints a new `InvocationID`". It does not, when what it starts is
not that unit. `test_a_transient_alternate_ingress_is_caught_only_by_the_commit_watermark`
is the reproduction: an ingress that is not Caddy runs, commits a submission and
exits entirely between the two readings, leaving every one of them identical.
`test_the_commit_watermark_is_unchanged_when_the_window_was_actually_quiet` is its
control, and the two are one episode with one variable in the same way the S-I
pair is. What catches the transient ingress is the third reading S-D.2 now takes,
the **commit watermark** over the append-only tables — the destination rather than
the route.

A fifth rule was **the watermark comparison on its own**, which closed the window
by ordering: the closing reading was made the last thing done before the outcome
was written. The outcome is still written afterwards, by hand, and the same
unenumerated mechanism can commit in between — so the reading a miss rests on can
be obsolete by the time the miss is recorded from it.
`test_a_commit_after_the_closing_reading_is_a_false_miss_without_the_settlement_lock`
is the reproduction: every reading matches at both ends, the ingress runs *after*
the closing one, and the recorded miss is false anyway. §9 answers it with
**S-D.3** — the decisive reading is taken inside a transaction holding
`LOCK TABLE foundry_snapshots, audit_events IN SHARE MODE`, and the lock is held
until the outcome has been written down, so the reading is a state spanning the
recording rather than an instant preceding it.

A sixth rule was **S-D.3 on its own**, which was described as leaving no gap
before step 4's route retirement. It leaves one, and it is the same false miss
again: `SHARE` blocks a conflicting `INSERT` rather than disposing of it, so a
submission delivered while the lock is held **waits** — inside PostgreSQL, past
every address the retirement can take away — and commits the instant the lock is
released, before step 4 runs.
`test_a_writer_queued_behind_the_settlement_lock_is_a_false_miss_without_the_drain_read`
is the reproduction, and it is the same episode as the fifth with the lock taken.
§9 answers it with **S-D.4**: the queue behind the lock is read with the decisive
reading and again before the `COMMIT`, any waiting writer is Unsettled, and the
miss is confirmed against a **drain read** — the same lock taken a second time,
granted only behind whatever was queued — before a fresh export is authorized.
`test_an_empty_queue_and_an_unmoved_drain_read_are_what_a_true_miss_rests_on` is
the control, the same episode with nothing ever delivered.

Nothing here contacts Foundry, a real database, a network peer off loopback, or
any real Actor data. The bundle is the committed synthetic fixture. The lock is
modelled at the commit boundary, so what these two establish is the shape of the
procedure; that PostgreSQL behaves as modelled — blocking rather than failing,
queuing visibly in `pg_locks`, committing on release, and granting a second
`SHARE` only behind the queue — is established against a real database in
`tests/test_snapshot_settlement_postgresql.py`.
"""
from __future__ import annotations

import contextlib
import http.client
import socket
import threading
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from wsgiref.simple_server import WSGIRequestHandler, make_server

import pytest

from adapters.artifacts.filesystem import FilesystemArtifactStore
from adapters.http.credentials import (
    MIN_SECRET_LENGTH,
    PRINCIPALS_VARIABLE,
    ServicePrincipalRegistry,
    secret_digest,
)
from adapters.http.wsgi import SUBMISSION_PATH, SnapshotSubmissionApplication
from application.foundry.audit_policy import SUBMISSION_ACCEPTED
from application.foundry.submission import SnapshotSubmissionService
from domain.foundry import OBSERVED_DEPLOYMENT
from tests import foundry_fixtures as fx
from tests.fakes import FakeStore, FakeUnitOfWork, admit

SECRET = "s" * MIN_SECRET_LENGTH
PRINCIPAL_ID = "foundry-the-guild"
CREDENTIAL = f"{PRINCIPAL_ID}.{SECRET}"
WORLD_ID = OBSERVED_DEPLOYMENT.world_id

#: How long a test may wait for a thread it expects to make progress. Generous:
#: it bounds a hang, and is never the thing being measured.
PATIENCE = 30.0


def _principals() -> ServicePrincipalRegistry:
    return ServicePrincipalRegistry.from_mapping(
        {
            PRINCIPALS_VARIABLE: (
                f"{PRINCIPAL_ID}|foundry:snapshot:submit|{secret_digest(SECRET)}"
            )
        }
    )


class GatedUnitOfWork(FakeUnitOfWork):
    """A unit of work whose commit blocks until a test releases it.

    This is the late commit, and it is the *only* thing injected: the artifact
    is still stored, the snapshot row is still built, the audit event is still
    recorded, and every one of them becomes visible at the same instant the real
    transaction would make them visible. Holding `commit` is what a server does
    while its transaction is open.
    """

    def __init__(self, store: FakeStore, *, reached: threading.Event,
                 release: threading.Event) -> None:
        super().__init__(store)
        self._reached = reached
        self._release = release

    def commit(self) -> None:
        self._reached.set()
        if not self._release.wait(PATIENCE):
            raise TimeoutError("the test never released the gated commit")
        super().commit()


def gated_factory(store: FakeStore, *, reached: threading.Event,
                  release: threading.Event):
    """A factory whose *first* unit is gated; later ones commit immediately.

    Only the submission under test is held open. A second unit — the refusal
    recorder, or a later submission — must not inherit the gate, or the test
    would be measuring its own scaffolding.
    """
    units: list[FakeUnitOfWork] = []

    def factory() -> FakeUnitOfWork:
        if not units:
            unit = GatedUnitOfWork(store, reached=reached, release=release)
        else:
            unit = FakeUnitOfWork(store)
        units.append(unit)
        return unit

    factory.units = units  # type: ignore[attr-defined]
    return factory


def reconciliation_hits(store: FakeStore) -> list[object]:
    """The §9 query, over the committed state.

    The same three predicates the documented SQL uses — the accepted action, the
    `foundry_snapshot` entity type, and the episode's `world_id` — against what
    a reader in another transaction could actually see. `FakeUnitOfWork` commits
    by copying pending state onto the shared store, so reading the store here is
    reading committed state, exactly as `psql` would.
    """
    return [
        event
        for event in store.audit_events
        if event.action == SUBMISSION_ACCEPTED
        and event.entity_type == "foundry_snapshot"
        and event.payload.get("world_id") == WORLD_ID
    ]


@pytest.fixture()
def artifacts(tmp_path: Path):
    store = FilesystemArtifactStore(tmp_path / "artifacts")
    yield store
    store.close()


def test_the_late_commit_sequence_makes_two_immediate_queries_miss(artifacts):
    """B-1 reproduced: the query runs, misses twice, and the commit still lands.

    This is the sequence Rehearsal A did **not** exercise. Rehearsal A faulted
    the *response* of a request the server had already served, so its acceptance
    event was committed before the operator queried — the hit branch. Here the
    transaction is still open while the queries run.
    """
    store = FakeStore()
    admit(store, PRINCIPAL_ID)
    reached = threading.Event()
    release = threading.Event()
    service = SnapshotSubmissionService(
        gated_factory(store, reached=reached, release=release),
        deployment=OBSERVED_DEPLOYMENT,
        artifacts=artifacts,
    )
    payload = fx.encode(fx.bundle())
    principal = _principals().authenticate(CREDENTIAL)

    submitted: dict[str, object] = {}

    def submit() -> None:
        submitted["receipt"] = service.submit(
            payload, principal=principal, request_key="pinned-episode-key"
        )

    worker = threading.Thread(target=submit, daemon=True)
    worker.start()
    assert reached.wait(PATIENCE), "the submission never reached its commit"

    # The operator's two queries, both while the POST is still in flight. This
    # is what "repeat it once" measured, and repeating it changes nothing: the
    # second observation is the same open transaction as the first.
    assert reconciliation_hits(store) == []
    assert reconciliation_hits(store) == []
    assert store.snapshots == {}

    # …and then the request the operator had written off commits.
    release.set()
    worker.join(PATIENCE)
    assert not worker.is_alive()

    events = reconciliation_hits(store)
    assert len(events) == 1
    assert events[0].payload["duplicate"] is False
    assert len(store.snapshots) == 1
    assert submitted["receipt"].checksum in store.snapshots


def test_a_fresh_export_is_a_second_artifact_that_uniqueness_cannot_merge(
    artifacts,
):
    """Why the false miss matters: the checksum constraint does not save you.

    The uniqueness constraint makes *identical bytes* one row, which is what
    makes a same-key retry harmless. A fresh export is not identical bytes — it
    is re-serialised from the world at a later moment and carries its own
    checksum — so a fresh export authorized on a false miss lands beside the
    original rather than merging with it. That is the second pending artifact
    the reconciliation exists to prevent.

    Deliberately sequential. Two overlapping transactions each committing their
    own row is a property of PostgreSQL's isolation, and `FakeUnitOfWork`
    commits by copying its pending state over the store, so a concurrent version
    of this test would be asserting the fake's last-writer-wins behaviour rather
    than the database's. The claim that needs establishing here is about the two
    exports, not about the concurrency: they are different bytes, so nothing in
    the schema can collapse them.
    """
    store = FakeStore()
    admit(store, PRINCIPAL_ID)
    service = SnapshotSubmissionService(
        lambda: FakeUnitOfWork(store),
        deployment=OBSERVED_DEPLOYMENT,
        artifacts=artifacts,
    )
    principal = _principals().authenticate(CREDENTIAL)
    original = fx.encode(fx.bundle())
    # A later export of the same folder: same Actors, a later `exportedAt`.
    fresh = fx.encode(fx.bundle(exported_at="2026-08-02T09:47:00Z"))
    assert fresh != original

    first = service.submit(
        original, principal=principal, request_key="pinned-episode-key"
    )
    second = service.submit(
        fresh, principal=principal, request_key="fresh-export-key"
    )

    assert first.checksum != second.checksum
    assert second.duplicate is False
    assert len(store.snapshots) == 2
    assert len(reconciliation_hits(store)) == 2


class _SilentHandler(WSGIRequestHandler):
    def log_message(self, format, *args):  # noqa: A002 - the base class's name
        return


def test_a_probe_can_be_answered_before_an_earlier_submission_is_accepted(
    artifacts,
):
    """Why the probe was withdrawn: issuance order is not the accept order.

    A probe settles only the requests the endpoint had already accepted when it
    accepted the probe's connection. A submission still inside Caddy — taken
    from the browser, not yet forwarded upstream — has not reached the endpoint,
    so the endpoint answers the later probe first and the operator's query still
    runs before the submission is even read. Caddy's in-flight gauge does not
    cover it either: Caddy counts the requests it is *currently handling*, which
    is not the same as everything it has accepted or is still reading.

    Modelled at the only place the difference is visible, the endpoint's
    listening socket: the episode's request exists and the GM has sent it, but
    its connection to the endpoint is not made until after the probe has been
    answered and both queries have missed. Under the withdrawn rule this is a
    settled miss, and it authorizes a fresh export while the original is still
    to arrive. This is the regression record for that rule, not evidence for the
    current one.
    """
    store = FakeStore()
    admit(store, PRINCIPAL_ID)
    service = SnapshotSubmissionService(
        lambda: FakeUnitOfWork(store),
        deployment=OBSERVED_DEPLOYMENT,
        artifacts=artifacts,
    )
    application = SnapshotSubmissionApplication(service, _principals())
    payload = fx.encode(fx.bundle())

    with make_server(
        "127.0.0.1", 0, application, handler_class=_SilentHandler
    ) as server:
        port = server.server_port
        serving = threading.Thread(target=server.serve_forever, daemon=True)
        serving.start()
        try:
            # The operator probes, and is answered, while the submission is
            # still upstream of the endpoint.
            probe = _connect_and_send(port, b"", headers={})
            assert _status(probe) == 401

            # Settlement "established", so the operator interprets the query.
            assert reconciliation_hits(store) == []
            assert reconciliation_hits(store) == []

            # …and only now does the proxy forward the episode's submission.
            submission = _connect_and_send(
                port,
                payload,
                headers={
                    "Authorization": f"Bearer {CREDENTIAL}",
                    "Idempotency-Key": "pinned-episode-key",
                },
            )
            assert _status(submission) == 201
        finally:
            server.shutdown()
            serving.join(PATIENCE)

    # The miss was recorded against a submission that had not arrived yet. A
    # fresh export authorized on it carries a different checksum, so uniqueness
    # cannot merge the two.
    assert len(reconciliation_hits(store)) == 1
    assert len(store.snapshots) == 1


def test_a_submission_queued_at_the_endpoint_commits_nothing_once_it_stops(
    artifacts,
):
    """§9 S-A at its hardest point: connected, fully sent, never accepted.

    This is the request the withdrawn conditions could not account for. It is
    exactly where a submission that Caddy forwarded an instant before the stop
    sits: its connection to the endpoint is complete, its bytes are all in the
    kernel's buffers, and the server has not accepted, read or begun to handle
    it. No probe and no in-flight gauge distinguishes this from an empty system.

    Stopping the endpoint does. The listening socket goes away with the process,
    the connection is never accepted, no handler ever runs, and nothing is
    committed — which is what makes a query run while the endpoint is down the
    whole truth about the episode. Established against a real
    `wsgiref.simple_server` over the real WSGI application, because the claim is
    about acceptance at a real socket rather than about the application.
    """
    store = FakeStore()
    admit(store, PRINCIPAL_ID)
    reached = threading.Event()
    release = threading.Event()
    service = SnapshotSubmissionService(
        gated_factory(store, reached=reached, release=release),
        deployment=OBSERVED_DEPLOYMENT,
        artifacts=artifacts,
    )
    application = SnapshotSubmissionApplication(service, _principals())
    payload = fx.encode(fx.bundle())

    server = make_server("127.0.0.1", 0, application, handler_class=_SilentHandler)
    port = server.server_port
    # Deliberately never served: the submission is queued at the endpoint rather
    # than handled by it, and `reached` proves that rather than assuming it.
    queued = _connect_and_send(
        port,
        payload,
        headers={
            "Authorization": f"Bearer {CREDENTIAL}",
            "Idempotency-Key": "pinned-episode-key",
        },
    )
    assert not reached.is_set(), (
        "the submission was handled before the server began serving; the test "
        "is no longer establishing the queued case"
    )

    # S-A: the endpoint stops. Nothing accepts the queued connection, ever.
    server.server_close()

    with pytest.raises((http.client.HTTPException, OSError)):
        _read(queued)

    # The commit gate was never even reached, so this is not a late commit held
    # open — it is a request that never became one.
    assert not reached.is_set()
    assert reconciliation_hits(store) == []
    assert store.snapshots == {}
    assert store.audit_events == []
    release.set()

    # …and it cannot arrive later either: the port is unserved, so a delivery
    # attempt is refused before any handler exists to run.
    with pytest.raises(ConnectionRefusedError):
        _connect_and_send(port, payload, headers={})

    assert reconciliation_hits(store) == []


def test_nothing_can_be_delivered_to_the_endpoint_once_it_has_stopped(artifacts):
    """§9 S-A's other half: what committed before the stop, and nothing after it.

    The step-2 query runs while the endpoint is down, and this is why its result
    is complete: an acceptance that committed before the stop is durable and
    visible to it, and a delivery attempted after the stop — the stranded
    submission §9 cannot see inside the proxy — is refused at the socket and
    reaches no handler.

    The second delivery is deliberately *different* bytes under a *different*
    idempotency key, so being served would create a second acceptance event and
    a second snapshot row. If the endpoint were still running, this test would
    fail rather than pass for an uninteresting reason.
    """
    store = FakeStore()
    admit(store, PRINCIPAL_ID)
    service = SnapshotSubmissionService(
        lambda: FakeUnitOfWork(store),
        deployment=OBSERVED_DEPLOYMENT,
        artifacts=artifacts,
    )
    application = SnapshotSubmissionApplication(service, _principals())
    payload = fx.encode(fx.bundle())
    stranded = fx.encode(fx.bundle(exported_at="2026-08-02T09:47:00Z"))
    assert stranded != payload

    server = make_server("127.0.0.1", 0, application, handler_class=_SilentHandler)
    port = server.server_port
    serving = threading.Thread(target=server.serve_forever, daemon=True)
    serving.start()
    try:
        accepted = _connect_and_send(
            port,
            payload,
            headers={
                "Authorization": f"Bearer {CREDENTIAL}",
                "Idempotency-Key": "pinned-episode-key",
            },
        )
        assert _status(accepted) == 201
    finally:
        server.shutdown()
        serving.join(PATIENCE)
        server.server_close()

    # The query the operator runs with the endpoint down sees the commit that
    # landed before the stop. This is the hit branch, and it stays a hit.
    settled = reconciliation_hits(store)
    assert len(settled) == 1
    assert len(store.snapshots) == 1

    with pytest.raises(ConnectionRefusedError):
        _connect_and_send(
            port,
            stranded,
            headers={
                "Authorization": f"Bearer {CREDENTIAL}",
                "Idempotency-Key": "stranded-delivery-key",
            },
        )

    assert reconciliation_hits(store) == settled
    assert len(store.snapshots) == 1
    assert [event.action for event in store.audit_events] == [SUBMISSION_ACCEPTED]


class _HoldingProxy:
    """A proxy holding a complete request it has not yet dialled upstream for.

    This is the request S-A alone does not reach, and the one the reviewer's
    fourth finding is about. It is not in the client's socket, it is not queued
    at the endpoint, and it has made **no** upstream attempt — so no retry rule
    governs it, and stopping the endpoint disposes of everything except it.

    Modelled rather than mocked: a real listening socket, a real client
    connection, the whole request read off it, and a real upstream dial made only
    when `release()` says the proxy has got round to it. `terminate()` is what
    `systemctl stop caddy` does to it — the sockets close and the request ceases
    to exist anywhere, without ever having been forwarded.

    The upstream address may be supplied at `release()` instead of at
    construction. That is not a convenience: it is the hop *in front of* this
    host, whose origin address has no listener at all when the request arrives
    and only becomes reachable later. A proxy released with no upstream never
    dials, which is the same outcome as a terminated one and is how the control
    run below ends.
    """

    def __init__(self, upstream_port: int | None = None) -> None:
        self._upstream_port = upstream_port
        self._listener = socket.create_server(("127.0.0.1", 0))
        self.port: int = self._listener.getsockname()[1]
        #: A complete request has been read and is held, undialled.
        self.holding = threading.Event()
        #: An upstream connection was made and the response came back.
        self.forwarded = threading.Event()
        #: Whether an upstream dial was ever attempted at all.
        self.dialled = False
        self._release = threading.Event()
        self._terminated = False
        self._client: socket.socket | None = None
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        try:
            client, _ = self._listener.accept()
        except OSError:  # terminated before a client arrived
            return
        self._client = client
        try:
            request = _read_request(client)
        except OSError:
            return
        self.holding.set()

        if not self._release.wait(PATIENCE):
            return
        if self._terminated:
            # The proxy is gone. It never dialled, so the request it was holding
            # never becomes anything.
            return
        if self._upstream_port is None:
            # Released with nowhere to go: the origin never came back, so the
            # request ends here just as surely.
            return

        self.dialled = True
        try:
            with socket.create_connection(
                ("127.0.0.1", self._upstream_port), timeout=PATIENCE
            ) as upstream:
                upstream.sendall(request)
                while upstream.recv(65536):
                    pass
        except OSError:
            return
        self.forwarded.set()

    def release(self, upstream_port: int | None = None) -> None:
        """The proxy gets round to the request it was holding.

        `upstream_port` names the origin for a proxy constructed without one —
        the moment an address that was dead becomes reachable again.
        """
        if upstream_port is not None:
            self._upstream_port = upstream_port
        self._release.set()

    def terminate(self) -> None:
        """S-I: the process is stopped, so everything it held goes with it."""
        self._terminated = True
        self._listener.close()
        if self._client is not None:
            self._client.close()
        self._release.set()

    def join(self) -> None:
        self._thread.join(PATIENCE)
        assert not self._thread.is_alive(), "the proxy thread never finished"


def _read_request(client: socket.socket) -> bytes:
    """Read one complete HTTP request — headers and the whole declared body."""
    client.settimeout(PATIENCE)
    buffered = b""
    while b"\r\n\r\n" not in buffered:
        chunk = client.recv(65536)
        if not chunk:
            raise OSError("the client closed before sending a complete request")
        buffered += chunk

    head, body = buffered.split(b"\r\n\r\n", 1)
    length = 0
    for line in head.split(b"\r\n")[1:]:
        name, _, value = line.partition(b":")
        if name.strip().lower() == b"content-length":
            length = int(value.strip())
    while len(body) < length:
        chunk = client.recv(65536)
        if not chunk:
            raise OSError("the client closed mid-body")
        body += chunk
    return head + b"\r\n\r\n" + body


def _raw_submission(payload: bytes, *, request_key: str) -> bytes:
    """The bytes a browser sends, built here so a raw socket can carry them."""
    head = (
        f"POST {SUBMISSION_PATH} HTTP/1.1\r\n"
        "Host: 127.0.0.1\r\n"
        "Content-Type: application/json\r\n"
        f"Authorization: Bearer {CREDENTIAL}\r\n"
        f"Idempotency-Key: {request_key}\r\n"
        f"Content-Length: {len(payload)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode("ascii")
    return head + payload


def _serve(server) -> threading.Thread:
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return thread


def _stop(server, thread: threading.Thread) -> None:
    server.shutdown()
    thread.join(PATIENCE)
    server.server_close()


@dataclass(frozen=True)
class _Episode:
    """What the shared lost-pin episode leaves behind for a test to read."""

    store: FakeStore
    proxy: _HoldingProxy
    client: socket.socket


@contextlib.contextmanager
def _held_request_episode(
    artifacts, *, terminate_the_proxy: bool
) -> Iterator[_Episode]:
    """One lost-pin episode, with S-I as the only variable in it.

    The two tests below are each other's control, and that only means anything
    if the control is real: every step here — the held-and-undialled request,
    the endpoint stop, the two missing queries, the restart on the same port and
    path, the release, and waiting for the proxy thread to finish — happens
    identically in both. `terminate_the_proxy` guards exactly one statement,
    `proxy.terminate()`, which is S-I. Delete that statement and the two tests
    run the same code over the same sequence, so the one that asserts the
    request died has nothing left to make it pass.

    An earlier version of this pair was two hand-written copies described as
    differing in one line. They did not: the S-I copy called `proxy.join()`
    immediately after terminating, where the other waited on `forwarded`, so
    deleting the terminate call blocked the join instead of reaching any
    assertion about the request. The claimed mutation could not happen. Keeping
    the sequence in one place is what makes the claim checkable.
    """
    store = FakeStore()
    admit(store, PRINCIPAL_ID)
    service = SnapshotSubmissionService(
        lambda: FakeUnitOfWork(store),
        deployment=OBSERVED_DEPLOYMENT,
        artifacts=artifacts,
    )
    application = SnapshotSubmissionApplication(service, _principals())
    payload = fx.encode(fx.bundle())

    server = make_server("127.0.0.1", 0, application, handler_class=_SilentHandler)
    port = server.server_port
    serving = _serve(server)
    proxy = _HoldingProxy(port)
    client = socket.create_connection(("127.0.0.1", proxy.port), timeout=PATIENCE)
    try:
        client.sendall(_raw_submission(payload, request_key="pinned-episode-key"))
        assert proxy.holding.wait(PATIENCE), "the proxy never held the request"
        assert not proxy.dialled, (
            "the proxy dialled upstream; the test is no longer establishing the "
            "held-but-undialled case"
        )

        # S-A: the endpoint's process is gone and its port is unserved.
        _stop(server, serving)

        # S-I — the only difference between the two tests.
        if terminate_the_proxy:
            proxy.terminate()

        # The operator's two queries, run with the endpoint down. They miss in
        # both runs: the difference is not what the query sees now, it is what
        # arrives afterwards.
        assert reconciliation_hits(store) == []
        assert reconciliation_hits(store) == []

        # Step 4 restarts the endpoint, on the same port and the same path so
        # that what this isolates is S-I and not the retired route.
        restarted = make_server(
            "127.0.0.1", port, application, handler_class=_SilentHandler
        )
        serving_again = _serve(restarted)
        try:
            # Release, then wait for the proxy thread to finish, with the
            # endpoint up and reachable throughout. Waiting is what makes the
            # negative assertion mean anything: asserting straight after
            # `release()` would pass whether or not the proxy went on to dial.
            # The wait is also what lets both runs share this line — a
            # terminated proxy's thread returns without dialling, a live one's
            # dials, forwards and then returns.
            proxy.release()
            proxy.join()
            yield _Episode(store=store, proxy=proxy, client=client)
        finally:
            _stop(restarted, serving_again)
    finally:
        proxy.terminate()
        client.close()


def test_a_request_held_by_the_proxy_commits_after_the_endpoint_restarts(
    artifacts,
):
    """B-1, fourth finding: stopping only the endpoint is not settlement.

    The rule this reproduces is the one C-15 wrote: S-A satisfied exactly — the
    endpoint's process gone, its port unserved, and down until the miss has been
    recorded — with the proxy left running. The episode's request is nonetheless
    alive, because it is inside the proxy and has not been dialled upstream for.
    §5.4's "no upstream retry window" does not reach it: a retry window governs
    what happens after a *refused* dial, and this request has not made one.

    Step 4 then restarts the endpoint, the proxy makes its first dial, and the
    submission commits after the settled miss authorized a fresh export. This is
    the regression record for the endpoint-only stop, kept for the same reason
    the probe's false miss is kept.
    """
    with _held_request_episode(artifacts, terminate_the_proxy=False) as episode:
        # The proxy outlived the endpoint, so it dialled across the restart.
        assert episode.proxy.dialled
        assert episode.proxy.forwarded.is_set()

        # The settled miss was false. One real submission, and a fresh export
        # was authorized against it under a different checksum.
        assert len(reconciliation_hits(episode.store)) == 1
        assert len(episode.store.snapshots) == 1


def test_a_request_held_by_the_proxy_dies_when_the_proxy_is_terminated(artifacts):
    """§9 S-I: the same episode, settled, with the proxy terminated too.

    Every step matches the test above; `terminate_the_proxy` is the difference,
    and it guards one statement. The proxy's thread then ends without ever
    dialling upstream, so the request stops existing rather than waiting for an
    endpoint to come back to. A settled miss recorded here is a true miss.
    """
    with _held_request_episode(artifacts, terminate_the_proxy=True) as episode:
        # No dial was ever made, and the client's connection died where it
        # stood — before the restart, and it stayed dead across it.
        assert not episode.proxy.dialled
        assert not episode.proxy.forwarded.is_set()
        assert episode.client.recv(65536) == b""

        # Nothing arrived across the restart, so the recorded miss stands.
        assert reconciliation_hits(episode.store) == []
        assert episode.store.snapshots == {}
        assert episode.store.audit_events == []


class _SupervisedUnit:
    """`caddy.service` as S-D.2's first reading sees it.

    Not a mock of systemd, and deliberately not a constant either. The two
    figures the reading rests on exist *because a start produces them* —
    `InvocationID` is minted by systemd on every start and
    `ActiveEnterTimestampMonotonic` moves with it — so here they are produced by
    `start()` and by nothing else in this module.

    That is what makes the counterexample below mean anything. Its closing
    reading equals its opening reading because no code path started this unit,
    not because a test declined to change a value it had made up.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.active = False
        self.invocation_id: str | None = None
        self.active_enter_monotonic: int | None = None
        self._starts = 0

    def start(self) -> None:
        self._starts += 1
        self.invocation_id = f"{self.name}-invocation-{self._starts}"
        self.active_enter_monotonic = self._starts * 1_000_000
        self.active = True

    def stop(self) -> None:
        self.active = False

    def show(self) -> tuple[str | None, int | None]:
        """`systemctl show caddy -p InvocationID -p ActiveEnterTimestamp...`."""
        return (self.invocation_id, self.active_enter_monotonic)


def commit_watermark(store: FakeStore) -> tuple[int, int]:
    """S-D.2's third reading, over committed state.

    The two counts §9 records at both ends of the down window: rows in
    `foundry_snapshots`, and `audit_events` rows for the `foundry_snapshot`
    entity. Both tables are append-only, so both counts are monotone and an
    acceptance inside the window moves at least the second of them — whatever
    accepted it, by whatever route, and whether or not that process still exists
    when the closing reading is taken.

    Unlike `reconciliation_hits`, this deliberately does **not** filter on the
    episode's `world_id` or on the accepted action. It is not looking for the
    episode's submission; it is looking for evidence that anything at all served
    this path while the operator believed nothing could.
    """
    return (
        len(store.snapshots),
        len(
            [
                event
                for event in store.audit_events
                if event.entity_type == "foundry_snapshot"
            ]
        ),
    )


def _listening(*ports: int) -> tuple[int, ...]:
    """S-D.2's second reading: `ss -ltn`, as a test can take it.

    A sample, and treated as one — which is the property under test.
    """
    answered: list[int] = []
    for port in ports:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1.0):
                answered.append(port)
        except OSError:
            pass
    return tuple(answered)


@dataclass(frozen=True)
class _Readings:
    """One end of S-D.2's down window."""

    caddy: tuple[str | None, int | None]
    listeners: tuple[int, ...]
    watermark: tuple[int, int]


@dataclass(frozen=True)
class _TransientEpisode:
    """What the transient-ingress episode leaves behind for a test to read."""

    store: FakeStore
    opening: _Readings
    closing: _Readings
    served: bool


@contextlib.contextmanager
def _transient_ingress_episode(
    artifacts, *, start_the_transient_ingress: bool
) -> Iterator[_TransientEpisode]:
    """One down window, with an unenumerated mid-window ingress as the variable.

    B-1, seventh finding. S-D.2's first two readings are about `caddy.service`
    and about two instants of a port, and neither survives an ingress that is
    neither of those things:

    1. both opening readings are clean and the query returns no row;
    2. something nobody enumerated starts the endpoint and a proxy on the public
       port — no part of it is `caddy.service`, and no part of it is in the
       component table S-I.3d bounds itself by;
    3. a request held in front of this host is delivered through it and commits;
    4. both transient processes exit;
    5. the closing readings are identical to the opening ones.

    Everything except step (2) is shared by both runs, and both runs take the
    same three readings at the same two points. `start_the_transient_ingress`
    guards the transient block alone.

    The hop holding the request is modelled by a `_HoldingProxy` constructed
    with **no** upstream: at the moment it takes the request there is nothing on
    the public port to dial, which is exactly the state S-I leaves the host in.
    """
    store = FakeStore()
    admit(store, PRINCIPAL_ID)
    service = SnapshotSubmissionService(
        lambda: FakeUnitOfWork(store),
        deployment=OBSERVED_DEPLOYMENT,
        artifacts=artifacts,
    )
    application = SnapshotSubmissionApplication(service, _principals())
    payload = fx.encode(fx.bundle())

    caddy = _SupervisedUnit("caddy.service")
    caddy.start()

    server = make_server("127.0.0.1", 0, application, handler_class=_SilentHandler)
    endpoint_port = server.server_port
    serving = _serve(server)

    # The hop in front of the host. S-A and S-I cannot reach it — that is what
    # step 4's route retirement is for — and it is not what this episode tests.
    # It is here because a stranded request has to exist for a transient ingress
    # to have anything to deliver.
    edge = _HoldingProxy()
    client = socket.create_connection(("127.0.0.1", edge.port), timeout=PATIENCE)
    try:
        client.sendall(_raw_submission(payload, request_key="pinned-episode-key"))
        assert edge.holding.wait(PATIENCE), "the hop never held the request"

        # S-A and S-I: the endpoint's process is gone, and Caddy is stopped.
        _stop(server, serving)
        caddy.stop()

        # S-D.2's opening reading, and step 2's query.
        opening = _Readings(
            caddy=caddy.show(),
            listeners=_listening(endpoint_port),
            watermark=commit_watermark(store),
        )
        assert reconciliation_hits(store) == []

        served = False
        if start_the_transient_ingress:
            # Neither of these is `caddy.service`, and neither is a mechanism
            # the topology record documents. Both exist only between the two
            # readings.
            transient_endpoint = make_server(
                "127.0.0.1", endpoint_port, application, handler_class=_SilentHandler
            )
            transient_serving = _serve(transient_endpoint)
            transient_proxy = _HoldingProxy(endpoint_port)
            try:
                edge.release(upstream_port=transient_proxy.port)
                assert transient_proxy.holding.wait(PATIENCE), (
                    "the transient ingress never received the held request"
                )
                transient_proxy.release()
                assert transient_proxy.forwarded.wait(PATIENCE), (
                    "the transient ingress never reached the endpoint"
                )
                transient_proxy.join()
                # The transient ingress exits, which is what lets the hop's own
                # connection end. Both are gone before anything is read.
                transient_proxy.terminate()
                edge.join()
                served = True
            finally:
                # …and then they are gone again, before anything is read.
                _stop(transient_endpoint, transient_serving)
                transient_proxy.terminate()

        # S-D.2's closing reading. The transient listeners were bound and closed
        # entirely between this sample and the opening one, which is why a
        # sample cannot see them.
        closing = _Readings(
            caddy=caddy.show(),
            listeners=_listening(endpoint_port),
            watermark=commit_watermark(store),
        )
        yield _TransientEpisode(
            store=store, opening=opening, closing=closing, served=served
        )
    finally:
        edge.terminate()
        client.close()


def test_a_transient_alternate_ingress_is_caught_only_by_the_commit_watermark(
    artifacts,
):
    """B-1, seventh finding: the Caddy readings do not cover the other paths.

    A submission commits inside the down window through an ingress that is not
    `caddy.service` and is not running at either reading. `InvocationID`, the
    enter timestamp and both listener samples are identical across the window,
    so a miss recorded on those readings alone would be false — and this is the
    counterexample the sixth remediation asserted could not exist, on the
    grounds that an unenumerated start "still mints a new `InvocationID`". It
    does not, when what it starts is not that unit.

    The commit watermark is what catches it, because it reads what a submission
    must durably write rather than what served the request.
    """
    with _transient_ingress_episode(
        artifacts, start_the_transient_ingress=True
    ) as episode:
        # A real acceptance landed inside the window.
        assert episode.served
        assert len(reconciliation_hits(episode.store)) == 1
        assert len(episode.store.snapshots) == 1

        # And every reading that names caddy.service, or samples a port, says
        # the window was quiet.
        assert episode.closing.caddy == episode.opening.caddy
        assert episode.opening.listeners == ()
        assert episode.closing.listeners == ()

        # The watermark is the one that moved. §9 makes that Unsettled.
        assert episode.opening.watermark == (0, 0)
        assert episode.closing.watermark == (1, 1)
        assert episode.closing.watermark != episode.opening.watermark


def test_the_commit_watermark_is_unchanged_when_the_window_was_actually_quiet(
    artifacts,
):
    """The control, without which the watermark would prove nothing.

    The same episode with the transient ingress never started: the held request
    is never delivered, nothing commits, and all three readings match at both
    ends. A watermark that differed here would be measuring the test harness
    rather than the window.
    """
    with _transient_ingress_episode(
        artifacts, start_the_transient_ingress=False
    ) as episode:
        assert not episode.served
        assert reconciliation_hits(episode.store) == []
        assert episode.store.snapshots == {}

        assert episode.closing.caddy == episode.opening.caddy
        assert episode.closing.listeners == episode.opening.listeners == ()
        assert episode.closing.watermark == episode.opening.watermark == (0, 0)


class _SettlementLock:
    """S-D.3's `LOCK TABLE ... IN SHARE MODE`, as a test can hold one.

    Two properties of PostgreSQL's lock modes are modelled, because the
    procedure now rests on both:

    - `SHARE` conflicts with the `ROW EXCLUSIVE` an `INSERT` takes, so while the
      locking transaction is open **no** commit reaches `foundry_snapshots` or
      `audit_events` — whatever is serving, and whether or not anyone enumerated
      it. Modelled at the only place a test can observe it, the commit boundary
      of the unit of work;
    - a blocked writer **waits** rather than failing, and while it waits it is
      an ungranted request another session can read. `queued_writers()` is
      S-D.4's `pg_locks` reading, and `drain()` is S-D.4's second acquisition of
      the same lock, which PostgreSQL grants only behind the requests already
      queued — which is what makes the watermark read inside it include their
      commits.

    What is deliberately *not* modelled is the acquire side of the first lock: a
    real `LOCK TABLE` also waits for an insert already in flight, and §9 sets
    `lock_timeout` so that waiting for one ends the episode as Unsettled rather
    than as a miss. That path needs no test double — it cannot produce a
    recorded miss at all.
    """

    def __init__(self) -> None:
        self._state = threading.Condition()
        self._held = False
        self._queued = 0
        #: Something reached its commit and found the door shut. A positive
        #: signal, so the test below never has to assert on elapsed time.
        self.blocked = threading.Event()

    def acquire(self) -> None:
        """`BEGIN; LOCK TABLE foundry_snapshots, audit_events IN SHARE MODE;`"""
        with self._state:
            self._held = True

    def release(self) -> None:
        """`COMMIT` — run only after the outcome has been written down."""
        with self._state:
            self._held = False
            self._state.notify_all()

    def queued_writers(self) -> int:
        """S-D.4's queue reading: ungranted conflicting requests, other backends.

        The documented query counts rows in `pg_locks` where `NOT granted` for
        these two relations and another `pid`. Here it counts writers parked at
        the commit boundary and not yet through it — the same population.
        """
        with self._state:
            return self._queued

    def wait_for_release(self) -> None:
        with self._state:
            if not self._held:
                return
            # From here the writer is a waiting `RowExclusiveLock`: it has not
            # failed, it has not gone away, and it will commit as soon as the
            # door opens.
            self._queued += 1
            self._state.notify_all()
            self.blocked.set()
            if not self._state.wait_for(lambda: not self._held, PATIENCE):
                raise TimeoutError("the settlement lock was never released")

    def writer_finished(self) -> None:
        """The queued writer's own transaction has ended, lock released with it."""
        with self._state:
            if self._queued:
                self._queued -= 1
            self._state.notify_all()

    def drain(self) -> None:
        """S-D.4's drain read: take the lock again, behind whatever was queued.

        A new conflicting request queues behind requests already waiting rather
        than overtaking them, so this returns only once every writer that was
        blocked by the first lock has ended its transaction. A watermark read
        after this call therefore includes their commits.
        """
        with self._state:
            if not self._state.wait_for(
                lambda: self._queued == 0 and not self._held, PATIENCE
            ):
                raise TimeoutError("the settlement drain never completed")


class _LockAwareUnitOfWork(FakeUnitOfWork):
    """A unit of work that commits through the settlement lock.

    `reached` is set at the commit boundary and `visible` once the work is
    committed, and the two are separated by exactly what separates them in
    PostgreSQL: the lock. With the lock released they are one instant apart,
    which is why the run without it is deterministic rather than timed.

    `writer_finished()` is called after the work is visible, because that is
    when a real writer's transaction ends and its `ROW EXCLUSIVE` is released —
    and it is what a second `LOCK TABLE` is waiting for.
    """

    def __init__(
        self,
        store: FakeStore,
        *,
        lock: _SettlementLock,
        reached: threading.Event,
        visible: threading.Event,
    ) -> None:
        super().__init__(store)
        self._lock = lock
        self._reached = reached
        self._visible = visible

    def commit(self) -> None:
        self._reached.set()
        self._lock.wait_for_release()
        super().commit()
        self._visible.set()
        self._lock.writer_finished()


@dataclass(frozen=True)
class _PostReadingEpisode:
    """What the post-closing-reading episode leaves behind for a test to read."""

    store: FakeStore
    opening: _Readings
    #: S-D.2's closing reading — the one the outcome is written from.
    closing: _Readings
    #: The watermark and query result *at the moment the operator writes the
    #: outcome down*, which is the reading that has to be true and the one the
    #: withdrawn rule never took.
    recorded: _Readings
    recorded_hits: int
    #: S-D.4's queue reading, taken at the same instant as `recorded`: how many
    #: writers are waiting behind the lock while the outcome is being written.
    #: Any at all is Unsettled, because the lock delays them rather than
    #: disposing of them.
    queued_writers_at_the_record: int
    #: S-D.4's drain read: the watermark inside a second acquisition of the same
    #: lock, taken after the release and before any fresh export is authorized.
    #: A figure that has moved retracts the miss.
    drain_read: tuple[int, int]
    blocked_at_the_lock: bool


@contextlib.contextmanager
def _post_reading_episode(
    artifacts,
    *,
    hold_the_settlement_lock: bool,
    deliver_the_held_request: bool = True,
) -> Iterator[_PostReadingEpisode]:
    """One down window, with S-D.3's lock and the delivery as the variables.

    B-1, eighth and ninth findings. S-D.2's watermark closes the interval
    between its two readings, and nothing closed the interval between the
    closing reading and the recording of the outcome. The outcome is written by
    hand, afterwards, from figures already taken:

    1. both opening readings are clean and the query returns no row;
    2. every closing reading matches — Caddy, both listener samples, and the
       watermark;
    3. **after** that reading, an unenumerated endpoint and proxy start;
    4. a request held in front of this host is delivered through them;
    5. the operator writes the miss down;
    6. the lock, if one was taken, is released — and S-D.4's drain read is taken
       behind whatever was queued behind it.

    Everything here is shared by every run, including the order of (1) to (6)
    and the point the transient ingress reaches. `hold_the_settlement_lock`
    guards two statements — the `acquire()` before the closing reading and the
    `release()` after the outcome is recorded — and `deliver_the_held_request`
    guards the transient ingress alone, which is what makes the true-miss run
    the same episode rather than a different one.

    The hop holding the request is a `_HoldingProxy` with **no** upstream, as in
    the episode above: at the moment it takes the request there is nothing on
    the public port to dial, which is the state S-I leaves the host in. Released
    with nowhere to go, it never dials, which is the run in which nothing is
    delivered at all.
    """
    store = FakeStore()
    admit(store, PRINCIPAL_ID)
    lock = _SettlementLock()
    reached = threading.Event()
    visible = threading.Event()
    service = SnapshotSubmissionService(
        lambda: _LockAwareUnitOfWork(
            store, lock=lock, reached=reached, visible=visible
        ),
        deployment=OBSERVED_DEPLOYMENT,
        artifacts=artifacts,
    )
    application = SnapshotSubmissionApplication(service, _principals())
    payload = fx.encode(fx.bundle())

    caddy = _SupervisedUnit("caddy.service")
    caddy.start()

    server = make_server("127.0.0.1", 0, application, handler_class=_SilentHandler)
    endpoint_port = server.server_port
    serving = _serve(server)

    edge = _HoldingProxy()
    client = socket.create_connection(("127.0.0.1", edge.port), timeout=PATIENCE)
    transient_endpoint = None
    transient_serving = None
    transient_proxy = None
    try:
        client.sendall(_raw_submission(payload, request_key="pinned-episode-key"))
        assert edge.holding.wait(PATIENCE), "the hop never held the request"

        # S-A and S-I: the endpoint's process is gone, and Caddy is stopped.
        _stop(server, serving)
        caddy.stop()

        opening = _Readings(
            caddy=caddy.show(),
            listeners=_listening(endpoint_port),
            watermark=commit_watermark(store),
        )
        assert reconciliation_hits(store) == []

        # S-D.3, and the only difference between the two runs: the door is held
        # shut *before* the reading the outcome will be written from.
        if hold_the_settlement_lock:
            lock.acquire()

        closing = _Readings(
            caddy=caddy.show(),
            listeners=_listening(endpoint_port),
            watermark=commit_watermark(store),
        )

        # …and only now, after the closing reading, does the unenumerated
        # mechanism start. Neither of these is `caddy.service` and neither is in
        # the component table S-I.3d bounds itself by.
        if deliver_the_held_request:
            transient_endpoint = make_server(
                "127.0.0.1", endpoint_port, application, handler_class=_SilentHandler
            )
            transient_serving = _serve(transient_endpoint)
            transient_proxy = _HoldingProxy(endpoint_port)
            edge.release(upstream_port=transient_proxy.port)
            assert transient_proxy.holding.wait(PATIENCE), (
                "the transient ingress never received the held request"
            )
            transient_proxy.release()

            # Every delivering run gets this far: the submission reached the
            # commit boundary.
            assert reached.wait(PATIENCE), "the submission never reached its commit"
            if hold_the_settlement_lock:
                assert lock.blocked.wait(PATIENCE), (
                    "the commit did not wait for the settlement lock"
                )
            else:
                assert visible.wait(PATIENCE), "the commit never became visible"
        else:
            # Nothing came back on the public port, so the hop is released with
            # nowhere to dial and the request ends where it stands.
            edge.release()
            edge.join()
            assert not reached.is_set(), "a submission was handled after S-I"

        # The operator writes the outcome down. This is the instant the miss is
        # a claim about, and the readings it is actually written from — plus
        # S-D.4's queue reading, which is what says whether the door the miss
        # was read through is empty as well as shut.
        recorded = _Readings(
            caddy=caddy.show(),
            listeners=_listening(endpoint_port),
            watermark=commit_watermark(store),
        )
        recorded_hits = len(reconciliation_hits(store))
        queued_writers_at_the_record = lock.queued_writers()
        blocked_at_the_lock = lock.blocked.is_set()

        # `COMMIT`. Only after the outcome is on paper.
        if hold_the_settlement_lock:
            lock.release()
            if deliver_the_held_request:
                assert visible.wait(PATIENCE), (
                    "the commit never landed once the lock was released"
                )

        # S-D.4's drain read: the same lock taken a second time, granted only
        # behind whatever was queued behind the first, and the watermark read
        # inside it. This is what the miss is confirmed against before any fresh
        # export is authorized.
        lock.drain()
        drain_read = commit_watermark(store)

        if deliver_the_held_request:
            assert transient_proxy is not None
            assert transient_proxy.forwarded.wait(PATIENCE), (
                "the transient ingress never reached the endpoint"
            )
        yield _PostReadingEpisode(
            store=store,
            opening=opening,
            closing=closing,
            recorded=recorded,
            recorded_hits=recorded_hits,
            queued_writers_at_the_record=queued_writers_at_the_record,
            drain_read=drain_read,
            blocked_at_the_lock=blocked_at_the_lock,
        )
    finally:
        lock.release()
        if transient_proxy is not None:
            transient_proxy.terminate()
        if transient_endpoint is not None and transient_serving is not None:
            _stop(transient_endpoint, transient_serving)
        edge.terminate()
        client.close()


def test_a_commit_after_the_closing_reading_is_a_false_miss_without_the_settlement_lock(
    artifacts,
):
    """B-1, eighth finding: the watermark comparison alone stops one instant short.

    All three of S-D.2's readings are identical at both ends — the transient
    ingress ran entirely after the closing one — so the comparison passes and
    the procedure permits a miss. By the time the operator writes it down the
    submission has committed, and the figures the miss was written from are
    obsolete. This is the regression record for the withdrawn ordering rule, not
    evidence for the current one.
    """
    with _post_reading_episode(
        artifacts, hold_the_settlement_lock=False
    ) as episode:
        # The closing comparison passes in every field, watermark included.
        assert episode.closing.caddy == episode.opening.caddy
        assert episode.closing.listeners == episode.opening.listeners == ()
        assert episode.closing.watermark == episode.opening.watermark == (0, 0)

        # And the state the miss is actually recorded from is not that state:
        # a submission committed in between, so the recorded miss is false.
        assert not episode.blocked_at_the_lock
        assert episode.recorded.watermark == (1, 1)
        assert episode.recorded.watermark != episode.closing.watermark
        assert episode.recorded_hits == 1


def test_a_writer_queued_behind_the_settlement_lock_is_a_false_miss_without_the_drain_read(
    artifacts,
):
    """B-1, ninth finding: the lock delays the race, it does not close it.

    The same episode with S-D.3's lock taken before the closing reading and
    released only after the outcome is written down. Everything S-D.3 claims
    holds: the transient ingress receives the held request, reaches its commit,
    and **cannot complete it**, so the watermark the miss is recorded from is
    the watermark that was read and could not have been anything else.

    And the miss is still false. `SHARE` conflicts with `ROW EXCLUSIVE`, so the
    blocked submission does not fail and does not go away — it waits, inside the
    database, past every hop S-A, S-I and step 4's route retirement can act on.
    The instant the lock is released it commits, before step 4 has retired
    anything, and the fresh export the miss authorized becomes a second artifact
    under a different checksum.

    What sees it is S-D.4: the queue is non-empty at the moment the outcome is
    written, and the drain read taken after the release has moved. Either is
    enough to make the episode Unsettled; this test is the record that the lock
    alone is not.
    """
    with _post_reading_episode(
        artifacts, hold_the_settlement_lock=True
    ) as episode:
        assert episode.closing.caddy == episode.opening.caddy
        assert episode.closing.listeners == episode.opening.listeners == ()
        assert episode.closing.watermark == episode.opening.watermark == (0, 0)

        # S-D.3 did everything it claims: the ingress reached the destination,
        # the door was shut, and the reading the outcome was written from is the
        # reading that was taken.
        assert episode.blocked_at_the_lock
        assert episode.recorded.watermark == episode.closing.watermark
        assert episode.recorded_hits == 0

        # S-D.4's first reading. A writer is queued behind the lock while the
        # miss is being written, which is a commit postponed and not one
        # prevented — Unsettled, not a miss.
        assert episode.queued_writers_at_the_record == 1

        # S-D.4's second. The drain read is taken behind that writer, so it sees
        # the commit that the release let through — before step 4 runs at all,
        # which is why the retirement cannot be what covers this one.
        assert episode.drain_read == (1, 1)
        assert episode.drain_read != episode.recorded.watermark
        assert len(reconciliation_hits(episode.store)) == 1


def test_an_empty_queue_and_an_unmoved_drain_read_are_what_a_true_miss_rests_on(
    artifacts,
):
    """S-D.4's control: the same episode where nothing was ever delivered.

    `deliver_the_held_request` guards the transient ingress alone. Without it
    the hop is released with nowhere to dial, exactly as S-I leaves the host,
    and nothing reaches a commit. Both of S-D.4's readings are then clean — no
    writer queued while the outcome was written, and a drain read identical to
    the decisive one — and this is the only shape in which §9 permits a fresh
    export.

    Without this run the readings above would prove nothing: a queue count and a
    drain read that were always positive would be measuring the harness.
    """
    with _post_reading_episode(
        artifacts, hold_the_settlement_lock=True, deliver_the_held_request=False
    ) as episode:
        assert episode.closing.caddy == episode.opening.caddy
        assert episode.closing.listeners == episode.opening.listeners == ()
        assert episode.closing.watermark == episode.opening.watermark == (0, 0)

        # Nothing ever reached the door, so nothing is behind it.
        assert not episode.blocked_at_the_lock
        assert episode.queued_writers_at_the_record == 0
        assert episode.recorded.watermark == episode.closing.watermark
        assert episode.recorded_hits == 0

        # And the drain read confirms the miss rather than retracting it.
        assert episode.drain_read == episode.recorded.watermark == (0, 0)
        assert reconciliation_hits(episode.store) == []
        assert episode.store.snapshots == {}


def _connect_and_send(
    port: int, body: bytes, *, headers: dict[str, str]
) -> http.client.HTTPConnection:
    """Complete the handshake and send the request, without reading the answer.

    Separating those two is the whole point: it is what lets a test place a
    request in the endpoint's accept queue and then observe what the server does
    with a connection made after it.
    """
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=PATIENCE)
    connection.connect()
    connection.request(
        "POST",
        SUBMISSION_PATH,
        body=body,
        headers={"Content-Type": "application/json", **headers},
    )
    return connection


def _status(connection: http.client.HTTPConnection) -> int:
    return int(_read(connection)["status"])


def _read(connection: http.client.HTTPConnection) -> dict[str, object]:
    try:
        with connection.getresponse() as response:
            return {"status": response.status, "body": response.read()}
    finally:
        connection.close()
