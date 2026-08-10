"""The late-commit race the lost-pin reconciliation has to survive.

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
  other's control. They set up one episode and differ in one line: terminate the
  proxy, and the held request stops existing; leave it running, and it commits
  across the restart. Neither passes for a reason the other does not isolate,
  which is why the control is committed here rather than described.

Nothing here contacts Foundry, a real database, a network peer off loopback, or
any real Actor data. The bundle is the committed synthetic fixture.
"""
from __future__ import annotations

import http.client
import socket
import threading
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
from tests.fakes import FakeStore, FakeUnitOfWork

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
    """

    def __init__(self, upstream_port: int) -> None:
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

    def release(self) -> None:
        """The proxy gets round to the request it was holding."""
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


def test_a_request_held_by_the_proxy_commits_after_the_endpoint_restarts(
    artifacts,
):
    """B-1, fourth finding: stopping only the endpoint is not settlement.

    The rule this reproduces is the one C-15 wrote: S-A.1 to S-A.4, satisfied
    exactly — the endpoint's process is gone, its port is unserved, and it stays
    down until the miss has been recorded. The episode's request is nonetheless
    alive, because it is inside the proxy and has not been dialled upstream for.
    §5.4's "no upstream retry window" does not reach it: a retry window governs
    what happens after a *refused* dial, and this request has not made one.

    Step 4 then restarts the endpoint, the proxy makes its first dial, and the
    submission commits after the settled miss authorized a fresh export. This is
    the regression record for the endpoint-only stop, kept for the same reason
    the probe's false miss is kept.
    """
    store = FakeStore()
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

        # S-A, in full: the endpoint stops and stays down across both queries.
        _stop(server, serving)
        assert reconciliation_hits(store) == []
        assert reconciliation_hits(store) == []
        # …so the operator records a settled miss and authorizes a fresh export.

        # Step 4 restarts the endpoint. Nothing else about the path changed.
        restarted = make_server(
            "127.0.0.1", port, application, handler_class=_SilentHandler
        )
        serving_again = _serve(restarted)
        try:
            proxy.release()
            assert proxy.forwarded.wait(PATIENCE), "the proxy never forwarded"
        finally:
            _stop(restarted, serving_again)
    finally:
        proxy.terminate()
        client.close()

    # The settled miss was false. One real submission, and a fresh export was
    # authorized against it under a different checksum.
    assert len(reconciliation_hits(store)) == 1
    assert len(store.snapshots) == 1


def test_a_request_held_by_the_proxy_dies_when_the_proxy_is_terminated(artifacts):
    """§9 S-I: the same episode, settled, with one line of difference.

    Everything here matches the test above up to the point where settlement is
    established — the same held-and-undialled request, the same endpoint stop,
    the same two queries missing, the same restart. The only difference is that
    the proxy is terminated as well as the endpoint, which is what S-I requires
    and what "terminated, not drained" means.

    The proxy's own thread then ends without ever dialling upstream, so the
    request stops existing rather than waiting for an endpoint to come back to.
    A settled miss recorded here is a true miss.
    """
    store = FakeStore()
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
        assert not proxy.dialled

        # S-A: the endpoint stops. S-I: so does the proxy in front of it.
        _stop(server, serving)
        proxy.terminate()
        proxy.join()

        # The held request is gone with the process that held it: no dial was
        # ever made, and the client's connection died where it stood.
        assert not proxy.dialled
        assert not proxy.forwarded.is_set()
        assert client.recv(65536) == b""

        assert reconciliation_hits(store) == []
        assert reconciliation_hits(store) == []

        # Step 4 restarts the endpoint — on the same port and the same path, so
        # that what this establishes is S-I and not the retired route.
        restarted = make_server(
            "127.0.0.1", port, application, handler_class=_SilentHandler
        )
        serving_again = _serve(restarted)
        try:
            # Release *and wait for the proxy to finish with it*, with the
            # endpoint up and reachable the whole time. Asserting straight after
            # `release()` would pass whether or not the proxy went on to dial,
            # which is the difference this test exists to see.
            proxy.release()
            proxy.join()
            assert not proxy.dialled
            assert not proxy.forwarded.is_set()
        finally:
            _stop(restarted, serving_again)
    finally:
        client.close()

    # Nothing arrived across the restart, so the recorded miss stands.
    assert reconciliation_hits(store) == []
    assert store.snapshots == {}
    assert store.audit_events == []


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
