"""`freedom-worker`: claim and execute durable reconciliation jobs.

    python -m tools.freedom_worker
    python -m tools.freedom_worker --once          # one tick, then exit
    python -m tools.freedom_worker --reap-only     # reap and recover, claim nothing

Not an operator command in the C-01…C-07 sense: it is a **service**, started by
systemd, and it exposes no listener at all (N-50). It is here rather than under
`adapters/` because it is a process entry point, which is what `tools/` holds.

## What it refuses to start without

Everything `WebSettings.from_environment()` validates, plus two of its own:
`WORKER_ENABLED` must be **true** — the mirror of S-11, which refuses a web
process that claims jobs — and `WORKER_ARTIFACT_ROOT` must name a store that
passes the existing Phase 2 filesystem checks (S-12). Both refuse here, at
startup, where an operator is watching, and both name the variable and never its
value.

## A thread the worker could not stop

`WorkerRuntime` cannot kill an execution thread — Python offers no way — so when
it stops watching one that is still alive it records it and **claims nothing
else** (N-41). This loop reports that condition once when it starts and once when
it clears, rather than every second: a stalled worker must be visible in the
journal, and a stalled worker that printed a line per poll would bury the reason
it stalled. Nothing is at risk while it lasts — the commit fence makes an
outstanding thread unable to commit, and the reaper and the effect-publication
recovery both keep running without asking the stalled attempt anything — but the
worker is idle and an operator should restart it.

## Shutdown

`SIGTERM` and `SIGINT` ask the loop to stop. The current attempt finishes or is
abandoned at its next heartbeat, and an abandoned attempt is **recoverable**
rather than failed. Systemd's `TimeoutStopSec` is set below the 60-second lease
(N-52) so a restarting process never holds a claim it cannot heartbeat.

## Exit codes

`0` clean shutdown · `1` configuration refused · `4` usage.
"""
from __future__ import annotations

import argparse
import logging
import os
import signal
import socket
import sys
import time
from collections.abc import Sequence

from adapters.worker.composition import WorkerComposition
from application.web.config import ConfigurationError, ProcessRole, WebSettings
from application.worker.runtime import WorkerRuntime

EXIT_OK = 0
EXIT_REFUSED = 1
EXIT_USAGE = 4

#: How long the loop sleeps when it claimed nothing. Short enough that a Council
#: member's preview starts promptly, long enough that an idle worker is not a
#: busy poll: the reaper interval (N-44) already sets the rhythm the process
#: needs, and claiming is cheap on the partial index.
IDLE_POLL_SECONDS = 1.0

LOGGER = logging.getLogger("freedom.worker")


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--once",
        action="store_true",
        help="run a single tick and exit; used by supervised rehearsals",
    )
    parser.add_argument(
        "--reap-only",
        action="store_true",
        help="run one reaper pass and exit; claims no job",
    )
    return parser.parse_args(argv)


def instance_name() -> str:
    """The worker's identity, for the lease's fencing token.

    Host and process id, which is what an operator has when they are looking at
    `lease_owner` in a failed job's audit payload and trying to find out which
    process stopped answering. Never a credential and never a configured value.
    """
    return f"{socket.gethostname()}/{os.getpid()}"


def build(environ=None) -> tuple[WorkerComposition, WorkerRuntime]:
    """Compose, or refuse. Nothing here catches its own refusal."""
    # `process=WORKER` is what makes S-11 read the other way round here: this
    # process **requires** `WORKER_ENABLED=true`, where the web process refuses
    # it. One variable, two refusals, and neither can be satisfied by accident.
    settings = WebSettings.from_environment(
        environ if environ is not None else os.environ, process=ProcessRole.WORKER
    )
    composition = WorkerComposition(settings)
    kill_switch_file = composition.settings.kill_switch_file
    runtime = WorkerRuntime(
        composition=composition,
        worker_settings=composition.worker,
        bounds=composition.settings.bounds,
        guild_id=composition.settings.discord.guild_id,
        instance=instance_name(),
        # Layer 1 of the operator kill switch, in the worker: **claim no new
        # work**, and abandon the current attempt at its next heartbeat. The
        # same file the portal watches, so one operator action closes both.
        kill_switch=kill_switch_file.exists,
    )
    return composition, runtime


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_arguments(argv)
    logging.basicConfig(
        level=logging.INFO,
        # Structured enough to correlate, and carrying no identity, character or
        # token data — monitoring output is checked for that (TC-OPS-05).
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    try:
        composition, runtime = build()
    except ConfigurationError as refusal:
        # The refusal names variables and never values, so it is safe to print
        # to a journal an operator will read and paste.
        print(refusal.render(), file=sys.stderr)
        return EXIT_REFUSED

    def request_stop(signum, _frame) -> None:
        LOGGER.info("shutdown requested (signal %s); draining", signum)
        runtime.stop()

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)

    try:
        if arguments.reap_only:
            reaped = runtime.reap()
            # The other half of a maintenance pass: an expired lease over a
            # committed effect is a result this platform owes, not an expiry, and
            # an operator running `--reap-only` to clear a backlog needs both.
            recovered = runtime.recover()
            LOGGER.info(
                "reaper pass complete: %d job(s) transitioned, "
                "%d committed effect(s) published",
                len(reaped),
                len(recovered),
            )
            return EXIT_OK
        stalled = False
        while True:
            tick = runtime.tick()
            if tick.claimed is not None:
                LOGGER.info("job %s finished: %s", tick.claimed, tick.outcome)
            if tick.reaped:
                LOGGER.info("reaper transitioned %d job(s)", len(tick.reaped))
            for job_id in tick.recovered:
                # One line per job rather than a count: publishing a result for an
                # effect whose process died is rare, is the platform completing a
                # job on a dead worker's behalf, and is the first thing an operator
                # wants to correlate against a restart. Job id only (N-25).
                LOGGER.warning(
                    "published the result of job %s from its committed effect; "
                    "the worker that ran it did not return",
                    job_id,
                )
            if tick.outcome == "attempt_outstanding":
                if not stalled:
                    stalled = True
                    for job_id, owner, reason in runtime.outstanding_report():
                        # Job id, lease owner and why. Never a checksum, a
                        # requester or anything the artifact contained (N-25).
                        LOGGER.warning(
                            "claiming nothing: job %s (%s) was released for %s "
                            "and its thread is still running",
                            job_id,
                            owner,
                            reason,
                        )
            elif stalled:
                stalled = False
                LOGGER.info("outstanding attempt ended; claiming again")
            if arguments.once:
                return EXIT_OK
            if tick.outcome == "stopped":
                return EXIT_OK
            if tick.claimed is None:
                time.sleep(IDLE_POLL_SECONDS)
    finally:
        composition.close()


if __name__ == "__main__":  # pragma: no cover - process entry point
    raise SystemExit(main())
