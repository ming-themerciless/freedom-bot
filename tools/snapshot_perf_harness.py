"""C-6: the SP-15/SP-16 measurement harness, and the bounds stated **before** the run.

Execution plan §11.3 requires each bound to be recorded before the measurement,
not chosen after it. That rule is the whole reason this module exists as code
rather than as a paragraph in a run sheet: `python -m tools.snapshot_perf_harness
bounds` prints a dated record that goes into the evidence document *first*, and
the measurement subcommands print the same bounds beside every observation, so a
reader can see what was promised and what happened without trusting the order in
which someone typed them.

## What it measures, and why this way

**Peak worker memory (TC-PERF-01, against N-47's 2 GiB).** Read from
`/proc/<pid>/status` `VmHWM` — the kernel's own high-water mark — rather than by
sampling `VmRSS` on a timer. A sampler can miss the peak between two samples,
and the peak is the entire quantity N-47 bounds. `VmRSS` is still sampled, but
only to show the shape of the curve alongside the authoritative figure.

**Wall-clock preview and apply duration (TC-PERF-02).** Timed by the operator
around the observable transition, because the job runs in the worker process and
the honest boundary is the one an operator can see.

**Portal responsiveness under a running preview (TC-PERF-03).** This harness
polls `/healthz` only, and deliberately does **not** poll the Council job-status
route (R-44). That route needs a Council session cookie, and the standing
redaction rule forbids handling one: passing it in `argv` would put it in `ps`
output, and storing it would put a live session credential in a measurement
artifact. The status-poll half of TC-PERF-03 is therefore observed by the
operator in the browser that already holds the session, and its timing recorded
in the run sheet. Stated here rather than discovered during the sitting.

## Bounds: derived where an accepted number exists, proposed where none does

Three of the five bounds below are **already accepted policy** and are cited, not
invented. Two — the latency pair — have no accepted figure anywhere in the
numeric register, so they are marked `proposed` and **must be accepted before the
run they judge**. A bound invented after a measurement is not a bound.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

#: N-47, the accepted worker memory ceiling. Raised 1G -> 2G on 2026-08-27
#: (C-P3.5-Z) once TC-PERF-01 measured a real folder at 302 MiB and put the
#: extrapolation to N-20's ceiling near the old bound. Must equal `MemoryMax`
#: in `infra/systemd/freedom-worker.service.tmpl`; a test pins the pair.
N47_MEMORY_MAX_BYTES = 2 * 1024 * 1024 * 1024

#: N-45, the accepted per-attempt runtime cap and its soft warning.
N45_SOFT_WARNING_SECONDS = 60
N45_HARD_CAP_SECONDS = 300

#: C-9/C-11's accepted throughput criterion, in the one unit that survives a
#: change of corpus: 728 ms/MB was observed synthetic, 587 ms/MB real, and the
#: limit carries headroom for a shared host.
#:
#: Restated here rather than imported from `tests.benchmark_snapshot_500`,
#: because an operator entry point that imports the test package would only work
#: where the tests happen to be deployed. The drift risk that import would have
#: closed is closed instead by a test asserting the two constants are equal.
THROUGHPUT_LIMIT_MS_PER_MB = 1200.0


class HarnessError(RuntimeError):
    """The harness refused, or could not observe what it was asked to observe."""


@dataclass(frozen=True, slots=True)
class Bound:
    """One numeric expectation, with where it comes from."""

    identifier: str
    subject: str
    limit: str
    source: str
    #: `accepted` — already policy, cited above. `proposed` — new, and not
    #: usable as a criterion until the Acceptance Authority accepts it.
    standing: str

    def render(self) -> str:
        mark = "ACCEPTED" if self.standing == "accepted" else "PROPOSED"
        return f"[{mark}] {self.identifier}  {self.subject}\n    limit: {self.limit}\n    source: {self.source}"


BOUNDS: tuple[Bound, ...] = (
    Bound(
        identifier="TC-PERF-01",
        subject="worker peak resident memory, real 32-Actor folder and synthetic worst case",
        limit=f"peak RSS <= {N47_MEMORY_MAX_BYTES} bytes (2 GiB)",
        source="N-47, accepted numeric register. Reported at 75% as a warning line, which changes no policy.",
        standing="accepted",
    ),
    Bound(
        identifier="TC-PERF-02a",
        subject="preview throughput",
        limit=f"<= {THROUGHPUT_LIMIT_MS_PER_MB} ms/MB, measured from the slowest sample",
        source="Change-log C-11's throughput criterion, accepted for Phase 2 and unit-independent of corpus size.",
        standing="accepted",
    ),
    Bound(
        identifier="TC-PERF-02b",
        subject="apply duration, single attempt",
        limit=(
            f"< {N45_HARD_CAP_SECONDS} s hard cap; exceeding "
            f"{N45_SOFT_WARNING_SECONDS} s is reportable, not a failure"
        ),
        source=(
            "N-45, accepted per-attempt runtime cap and its soft warning. The "
            "warning was raised 30 -> 60 s and **implemented** on 2026-08-27 "
            "(C-P3.5-Z); before that it existed only in the register."
        ),
        standing="accepted",
    ),
    Bound(
        identifier="TC-PERF-03a",
        subject="/healthz latency while a preview is running",
        limit="p95 <= 500 ms and max <= 2000 ms",
        source=(
            "ACCEPTED by Peter Duscha, Acceptance Authority, 2026-08-26 "
            "(decision D-s), on the working Technical Lead's proposal. Rationale: "
            "the worker is a separate process (N-41 concurrency 1), so a preview "
            "should barely touch the portal. **This is a tripwire for a design "
            "assumption, not a speed target**: a miss means the worker is blocking "
            "the portal, and is investigated rather than relaxed. 2000 ms max is "
            "well inside N-51's 30 s read timeout, and a health check slower than "
            "that is useless to the monitor it exists for."
        ),
        standing="accepted",
    ),
    Bound(
        identifier="TC-PERF-03b",
        subject="Council job-status poll latency while a preview is running",
        limit="p95 <= 1000 ms and max <= 3000 ms, observed in the operator's browser",
        source=(
            "ACCEPTED by Peter Duscha, Acceptance Authority, 2026-08-26 "
            "(decision D-s). Looser than TC-PERF-03a because the route "
            "authenticates a session and reads a job row, where /healthz does "
            "neither. A miss is investigated, not relaxed."
        ),
        standing="accepted",
    ),
)


def proposed_bounds() -> tuple[Bound, ...]:
    return tuple(bound for bound in BOUNDS if bound.standing != "accepted")


# ---------------------------------------------------------------------------
# Memory
# ---------------------------------------------------------------------------

_STATUS_FIELDS = {"VmHWM": "peak_rss_bytes", "VmRSS": "current_rss_bytes"}


def parse_proc_status(text: str) -> dict[str, int]:
    """Extract the two resident-memory figures from `/proc/<pid>/status`.

    Values are reported in kB by the kernel and converted here, once, so no
    caller has to remember the unit — a unit mistake in this particular number
    is a factor of 1024 against a multi-gigabyte ceiling.
    """
    found: dict[str, int] = {}
    for line in text.splitlines():
        name, _, remainder = line.partition(":")
        key = _STATUS_FIELDS.get(name.strip())
        if key is None:
            continue
        parts = remainder.split()
        if len(parts) != 2 or parts[1] != "kB":
            raise HarnessError(
                f"{name} was reported as {remainder.strip()!r}, which is not the "
                "kB form this parser was written against. Refusing to guess a unit."
            )
        found[key] = int(parts[0]) * 1024
    missing = set(_STATUS_FIELDS.values()) - set(found)
    if missing:
        raise HarnessError(f"/proc status carried no {', '.join(sorted(missing))}.")
    return found


def read_memory(pid: int) -> dict[str, int]:
    try:
        text = Path(f"/proc/{pid}/status").read_text(encoding="utf-8")
    except OSError as error:
        raise HarnessError(f"Could not read /proc/{pid}/status: {error}") from error
    return parse_proc_status(text)


def reset_peak_rss(pid: int) -> bool:
    """Reset `VmHWM` so the next reading is this job's peak, not the process's.

    Returns whether it worked. It needs the same user or root, and the harness
    treats a refusal as information rather than an error: an un-reset peak is
    still a valid upper bound, it is just a less precise one, and saying so is
    better than failing the sitting over it.
    """
    try:
        Path(f"/proc/{pid}/clear_refs").write_text("5", encoding="utf-8")
    except OSError:
        return False
    return True


def main_pid_of_unit(unit: str) -> int:
    import subprocess

    result = subprocess.run(
        ["systemctl", "show", unit, "--property=MainPID", "--value"],
        capture_output=True,
        text=True,
        check=False,
    )
    value = result.stdout.strip()
    if not value.isdigit() or int(value) == 0:
        raise HarnessError(
            f"{unit} reported MainPID {value!r}. The unit must be active before "
            "its memory can be observed."
        )
    return int(value)


# ---------------------------------------------------------------------------
# Latency
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class LatencySummary:
    samples: int
    failures: int
    min_ms: float
    median_ms: float
    p95_ms: float
    max_ms: float

    def render(self) -> str:
        return (
            f"samples {self.samples}  failures {self.failures}  "
            f"min {self.min_ms:.1f} ms  median {self.median_ms:.1f} ms  "
            f"p95 {self.p95_ms:.1f} ms  max {self.max_ms:.1f} ms"
        )


def summarise(samples_ms: list[float], failures: int) -> LatencySummary:
    if not samples_ms:
        raise HarnessError("No successful sample was taken; there is nothing to report.")
    ordered = sorted(samples_ms)
    # Nearest-rank p95, `ceil(p * n)`: with the sample counts a 30-second poll
    # produces, interpolation would invent a value between two real observations.
    rank = max(math.ceil(0.95 * len(ordered)) - 1, 0)
    return LatencySummary(
        samples=len(ordered),
        failures=failures,
        min_ms=ordered[0],
        median_ms=statistics.median(ordered),
        p95_ms=ordered[min(rank, len(ordered) - 1)],
        max_ms=ordered[-1],
    )


def poll(url: str, *, host_header: str | None, seconds: float, interval: float) -> tuple[LatencySummary, str]:
    """Poll one URL for `seconds`, returning latencies and the last body seen.

    The body is returned because `/healthz` answers with check names and booleans
    and nothing else (VM-16) — no connection string, no identity, no queue
    contents — so recording it is safe and is the only way to show the portal was
    answering *correctly* rather than merely answering.
    """
    samples: list[float] = []
    failures = 0
    last_body = ""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        request = urllib.request.Request(url)
        if host_header:
            request.add_header("Host", host_header)
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                last_body = response.read().decode("utf-8", "replace")
            samples.append((time.perf_counter() - started) * 1000.0)
        except (urllib.error.URLError, OSError, TimeoutError):
            failures += 1
        time.sleep(interval)
    return summarise(samples, failures), last_body


# ---------------------------------------------------------------------------
# Operator entry point
# ---------------------------------------------------------------------------


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _print_bounds() -> None:
    print(f"# Bounds record, stated before the run — {_stamp()}")
    print()
    for bound in BOUNDS:
        print(bound.render())
        print()
    outstanding = proposed_bounds()
    if outstanding:
        print(
            "REQUIRES ACCEPTANCE BEFORE THE RUN IT JUDGES: "
            + ", ".join(bound.identifier for bound in outstanding)
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tools.snapshot_perf_harness",
        description="SP-15/SP-16 measurement helper. Reads; never mutates the platform.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    subcommands.add_parser("bounds", help="Print the bounds record. Run this FIRST.")

    memory = subcommands.add_parser("memory", help="Read a unit's resident memory.")
    memory.add_argument("--unit", default="freedom-worker.service")
    memory.add_argument(
        "--reset-peak",
        action="store_true",
        help="Reset VmHWM first, so the next reading is this job's peak.",
    )

    latency = subcommands.add_parser("poll", help="Poll a URL and summarise latency.")
    latency.add_argument("--url", default="http://127.0.0.1:8001/healthz")
    latency.add_argument("--host-header", default=None)
    latency.add_argument("--seconds", type=float, default=30.0)
    latency.add_argument("--interval", type=float, default=0.5)

    arguments = parser.parse_args(argv)

    try:
        if arguments.command == "bounds":
            _print_bounds()
            return 0

        if arguments.command == "memory":
            pid = main_pid_of_unit(arguments.unit)
            if arguments.reset_peak:
                reset = reset_peak_rss(pid)
                print(f"peak reset       {'yes' if reset else 'NO - permission refused'}")
                if not reset:
                    print(
                        "                 the figure below is the process lifetime "
                        "peak, an upper bound rather than this job's peak"
                    )
            memory_now = read_memory(pid)
            peak = memory_now["peak_rss_bytes"]
            print(f"observed at      {_stamp()}")
            print(f"unit             {arguments.unit} (pid {pid})")
            print(f"peak rss bytes   {peak}")
            print(f"current rss      {memory_now['current_rss_bytes']}")
            print(f"N-47 ceiling     {N47_MEMORY_MAX_BYTES}")
            print(f"fraction of N-47 {peak / N47_MEMORY_MAX_BYTES:.3f}")
            print(f"within N-47      {peak <= N47_MEMORY_MAX_BYTES}")
            if peak > N47_MEMORY_MAX_BYTES * 0.75:
                print(
                    "WARNING          over 75% of N-47. Execution plan stop rule: "
                    "this is a finding, not a reason to raise N-47."
                )
            return 0

        summary, body = poll(
            arguments.url,
            host_header=arguments.host_header,
            seconds=arguments.seconds,
            interval=arguments.interval,
        )
        print(f"observed at      {_stamp()}")
        print(f"url              {arguments.url}")
        print(f"latency          {summary.render()}")
        for bound in BOUNDS:
            if bound.identifier == "TC-PERF-03a":
                print(f"bound            {bound.limit} [{bound.standing}]")
        try:
            print(f"last body        {json.dumps(json.loads(body), sort_keys=True)}")
        except ValueError:
            print(f"last body        {body.strip()[:200]!r}")
        return 0
    except HarnessError as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover - operator entry point
    raise SystemExit(main())
