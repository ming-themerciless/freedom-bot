"""Drive an application's **real** ASGI lifespan, exactly as a server does.

`httpx.ASGITransport` — the suite's only client, because
`docs/contracts/phase-3-configuration-and-dependency-contract.md` §1.3 keeps
`starlette.testclient` and its `requests` dependency out of the test set — sends
`{"type": "http", ...}` scopes and nothing else. It never opens a `lifespan`
scope, in the installed HTTPX 0.28.1 or in any version. So a test that builds an
application, makes requests through that transport and then asserts something
about shutdown is asserting about an event **that never happened**, and would
pass with no lifespan installed at all. That is the shape of the finding this
module exists for (2026-08-16, P3.G1 lifecycle remediation, finding 2): the
previous evidence for production cleanup was `await composition.aclose()` written
in the test, which proves the method and not the process.

`asgi-lifespan` is not in `requirements-web-dev.txt` and this module does not add
it. What is written below is the lifespan half of the ASGI specification and
nothing more: a `lifespan` scope, `lifespan.startup` and `lifespan.shutdown` on
the receive channel, and the four reply messages on the send channel. Uvicorn —
the server `infra/systemd/` starts — sends the same two messages in the same
order, so what an application does here is what it does in production.

Failures are **surfaced, not swallowed**. Starlette's router answers a raising
lifespan with `lifespan.startup.failed` or `lifespan.shutdown.failed` and then
re-raises, so this helper re-raises too: a shutdown that could not release its
resources is not a clean shutdown, and a helper that hid it would let the
failure-path regression pass on a broken implementation.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager, suppress
from dataclasses import dataclass
from typing import Any, AsyncIterator

#: A lifespan reply that takes longer than this is a hung shutdown, which is a
#: failure with a name rather than a test run that never ends.
LIFESPAN_TIMEOUT_SECONDS = 10.0


class LifespanProtocolError(AssertionError):
    """The application did not answer a lifespan message within the timeout."""


@dataclass(frozen=True, slots=True)
class RefusedStartup:
    """What an application that refused to start sent, and what it raised.

    Both halves are needed and neither can be recovered from the other.
    `failure` is the exception an operator sees and the one a case asserts the
    *type* of — a startup refusal that surfaced as something other than the
    configured refusal would be a regression however correct the cleanup was.
    `messages` is the ASGI conversation, which is where
    `lifespan.startup.failed` and the traceback the specification has the
    application put in it can be inspected: that message is the one place on
    this path where source text crosses a protocol boundary, so a case that
    asserts no secret is transmitted has to be able to read it.
    """

    failure: BaseException
    messages: tuple[dict[str, Any], ...]

    @property
    def message_types(self) -> tuple[str, ...]:
        return tuple(message["type"] for message in self.messages)


async def refused_startup(app) -> RefusedStartup:
    """Drive `app`'s startup expecting it to **refuse**, and report what happened.

    The counterpart to `application_lifespan` for the path that has no body to
    run: a resource check that refuses means the application never reaches
    `lifespan.startup.complete`, so there is no window in which a request could
    be served and nothing for an `async with` block to wrap. A server that
    receives `lifespan.startup.failed` stops rather than binding a socket, which
    is what "no request is served after a refused startup" means at this layer —
    asserting it by sending an HTTP scope afterwards would assert about a
    situation no server produces.

    Fails the calling test if the startup *completed*, so a case cannot pass by
    accidentally exercising a healthy application.
    """
    driver = _LifespanDriver(app)
    try:
        await driver.start()
    except Exception as failure:  # noqa: BLE001 - the refusal is the result
        return RefusedStartup(failure=failure, messages=tuple(driver.messages))
    finally:
        await driver.cancel()
    raise AssertionError(
        "the application answered lifespan.startup.complete; this helper is for "
        "the refusal path and a completed startup means the case proved nothing"
    )


@asynccontextmanager
async def application_lifespan(app) -> AsyncIterator[list[dict[str, Any]]]:
    """Enter `app`'s lifespan on the way in and leave it on the way out.

    Yields the list of lifespan messages the application has sent so far, so a
    case can assert on the protocol itself — that startup completed, that
    shutdown completed rather than failed — beside asserting on what cleanup did.

    The body runs **between** `lifespan.startup.complete` and
    `lifespan.shutdown`, which is where requests belong: an integration case can
    open an `httpx.ASGITransport` client inside this block and observe both the
    request identity a started application serves with and the cleanup its
    shutdown performs.

    If the body raises, the lifespan task is cancelled rather than shut down
    cleanly. A test that fails half-way has not established anything about
    shutdown, and running one anyway would attribute the body's failure to
    cleanup.
    """
    driver = _LifespanDriver(app)
    try:
        await driver.start()
        yield driver.messages
        await driver.stop()
    finally:
        await driver.cancel()


class _LifespanDriver:
    """The lifespan half of the ASGI specification, and nothing more.

    Extracted so `application_lifespan` and `refused_startup` drive the *same*
    protocol implementation rather than two that could drift: the whole value of
    this module is that what an application does here is what it does under
    uvicorn, and two copies of the conversation would be two chances to get that
    wrong.
    """

    def __init__(self, app) -> None:
        self.messages: list[dict[str, Any]] = []
        self._inbox: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._startup = asyncio.Event()
        self._shutdown = asyncio.Event()
        scope = {
            "type": "lifespan",
            "asgi": {"version": "3.0", "spec_version": "2.0"},
            # Starlette only writes here when the lifespan context yields state,
            # and this application's does not. Present because the specification
            # says a server that supports it provides it, and its absence would
            # make a future state-yielding lifespan fail for a reason unrelated
            # to the test.
            "state": {},
        }
        self._runner = asyncio.ensure_future(app(scope, self._receive, self._send))

    async def _receive(self) -> dict[str, Any]:
        return await self._inbox.get()

    async def _send(self, message: dict[str, Any]) -> None:
        self.messages.append(message)
        if message["type"].startswith("lifespan.startup"):
            self._startup.set()
        elif message["type"].startswith("lifespan.shutdown"):
            self._shutdown.set()

    async def start(self) -> None:
        await self._inbox.put({"type": "lifespan.startup"})
        await _answered(self._startup, self._runner, "startup")
        if self.messages[-1]["type"] == "lifespan.startup.failed":
            await self._runner  # the router re-raises; this is where it surfaces

    async def stop(self) -> None:
        await self._inbox.put({"type": "lifespan.shutdown"})
        await _answered(self._shutdown, self._runner, "shutdown")
        if self.messages[-1]["type"] == "lifespan.shutdown.failed":
            await self._runner
        await self._runner

    async def cancel(self) -> None:
        if not self._runner.done():
            self._runner.cancel()
            with suppress(asyncio.CancelledError):
                await self._runner


async def _answered(event: asyncio.Event, runner, phase: str) -> None:
    """Wait for the application's reply, or for the lifespan task to die trying."""
    waiter = asyncio.ensure_future(event.wait())
    try:
        await asyncio.wait(
            {waiter, runner},
            return_when=asyncio.FIRST_COMPLETED,
            timeout=LIFESPAN_TIMEOUT_SECONDS,
        )
    finally:
        waiter.cancel()
        with suppress(asyncio.CancelledError):
            await waiter
    if event.is_set():
        return
    if runner.done():
        # It failed without answering at all, which the specification does not
        # allow but a broken application can still do. Raise what it failed with.
        await runner
    raise LifespanProtocolError(
        f"the application sent no lifespan.{phase} reply within "
        f"{LIFESPAN_TIMEOUT_SECONDS} seconds"
    )


__all__ = [
    "LIFESPAN_TIMEOUT_SECONDS",
    "LifespanProtocolError",
    "RefusedStartup",
    "application_lifespan",
    "refused_startup",
]
