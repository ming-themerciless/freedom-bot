"""C-6's harness has to be right about two things: a unit, and a promise.

The unit: `/proc/<pid>/status` reports memory in kB, and N-47 is a byte figure.
A missed conversion here is a factor of 1024 against a 2 GiB ceiling — it would
report a worker at 70% of the limit as one at 0.07%, and the measurement would
look comfortable precisely when it was not.

The promise: execution plan §11.3 requires every bound to be stated before the
run. A bound with no source, or a newly invented figure presented as accepted
policy, defeats that rule while appearing to satisfy it.
"""
from __future__ import annotations

import pytest

from tools.snapshot_perf_harness import (
    BOUNDS,
    N45_HARD_CAP_SECONDS,
    N45_SOFT_WARNING_SECONDS,
    N47_MEMORY_MAX_BYTES,
    THROUGHPUT_LIMIT_MS_PER_MB,
    HarnessError,
    parse_proc_status,
    proposed_bounds,
    summarise,
)

_STATUS = """\
Name:\tpython3
State:\tS (sleeping)
VmPeak:\t  912345 kB
VmSize:\t  812345 kB
VmHWM:\t   69792 kB
VmRSS:\t   69792 kB
Threads:\t4
"""


def test_kilobytes_are_converted_to_bytes():
    parsed = parse_proc_status(_STATUS)
    assert parsed["peak_rss_bytes"] == 69792 * 1024
    assert parsed["current_rss_bytes"] == 69792 * 1024


def test_an_unexpected_unit_is_refused_rather_than_guessed():
    """The failure this test exists for is silent, not loud.

    If a kernel ever reported these in bytes or MB, a parser that ignored the
    unit would keep working and keep being wrong by three orders of magnitude.
    """
    with pytest.raises(HarnessError, match="not the kB form"):
        parse_proc_status("VmHWM:\t 69792 MB\nVmRSS:\t 69792 kB\n")


def test_a_status_file_without_the_figures_is_refused():
    with pytest.raises(HarnessError, match="carried no"):
        parse_proc_status("Name:\tpython3\nThreads:\t4\n")


def test_the_peak_is_never_below_the_current_reading_in_a_real_status_file():
    parsed = parse_proc_status(_STATUS)
    assert parsed["peak_rss_bytes"] >= parsed["current_rss_bytes"]


def test_p95_is_nearest_rank_and_is_a_real_observation():
    samples = [float(value) for value in range(1, 101)]
    summary = summarise(samples, failures=0)
    assert summary.samples == 100
    assert summary.max_ms == 100.0
    assert summary.min_ms == 1.0
    # Nearest-rank: an observation that actually happened, not an interpolation
    # between two that did.
    assert summary.p95_ms in samples
    assert summary.p95_ms == 95.0


def test_failures_are_counted_and_reported_separately_from_latency():
    summary = summarise([10.0, 20.0], failures=3)
    assert summary.failures == 3
    assert summary.samples == 2


def test_no_successful_sample_is_refused_rather_than_reported_as_zero():
    with pytest.raises(HarnessError, match="nothing to report"):
        summarise([], failures=5)


def test_every_bound_names_a_source_and_a_standing():
    for bound in BOUNDS:
        assert bound.standing in {"accepted", "proposed"}, bound.identifier
        assert bound.source.strip(), bound.identifier
        assert bound.limit.strip(), bound.identifier


def test_every_bound_is_now_accepted():
    """All five carry an accepted figure as of 2026-08-26 (decision D-s).

    The two latency bounds were `proposed` until the Acceptance Authority
    accepted them. This asserts the current state; the mechanism that flags an
    *unaccepted* bound is asserted separately below, so accepting these did not
    quietly remove the guard.
    """
    assert proposed_bounds() == ()


def test_an_unaccepted_bound_is_still_flagged_loudly():
    """The guard that survives all five bounds being accepted.

    Without this, adding a new invented figure later would print alongside the
    accepted ones with nothing marking it out — which is the failure the
    `standing` field exists to prevent.
    """
    from tools.snapshot_perf_harness import Bound

    invented = Bound(
        identifier="TC-PERF-99",
        subject="a figure nobody accepted",
        limit="<= 1 ms",
        source="NO ACCEPTED FIGURE EXISTS. Invented for this test.",
        standing="proposed",
    )

    # The bracketed marker, not the bare word: "NO ACCEPTED FIGURE EXISTS"
    # legitimately contains "ACCEPTED" in the source text.
    assert "[PROPOSED]" in invented.render()
    assert "[ACCEPTED]" not in invented.render()


def test_accepted_bounds_cite_the_policy_they_come_from():
    accepted = [bound for bound in BOUNDS if bound.standing == "accepted"]
    citations = " ".join(bound.source for bound in accepted)
    assert "N-47" in citations
    assert "N-45" in citations
    assert "C-11" in citations


def test_the_accepted_numbers_match_the_policy_they_claim_to_restate():
    """Restated constants, pinned to their originals so they cannot drift apart.

    The harness deliberately does not import the test package — an operator
    entry point that did would only work where the tests are deployed — so this
    is the check that keeps the restatement honest.
    """
    from tests.benchmark_snapshot_500 import (
        THROUGHPUT_LIMIT_MS_PER_MB as benchmark_limit,
    )

    assert THROUGHPUT_LIMIT_MS_PER_MB == benchmark_limit
    assert N45_HARD_CAP_SECONDS == 300


def test_the_memory_ceiling_matches_the_shipped_worker_unit():
    """The harness restates N-47; the systemd unit *is* N-47. Pin them together.

    Pinned to a literal until 2026-08-27, which is precisely how it drifted: the
    C-P3.5-Z raise reached the register and the unit, the harness kept 1 GiB, and
    the literal kept the suite green while the measuring tool disagreed with the
    policy it measured against. Reading the unit makes the next raise a one-place
    change or a failing test, never a silent disagreement.
    """
    from pathlib import Path

    unit = Path(__file__).resolve().parents[1] / "infra" / "systemd" / "freedom-worker.service.tmpl"
    declared = [
        line.split("=", 1)[1].strip()
        for line in unit.read_text().splitlines()
        if line.startswith("MemoryMax=")
    ]
    assert declared == ["2G"], declared

    suffixes = {"K": 1024, "M": 1024**2, "G": 1024**3}
    value = declared[0]
    assert value[-1] in suffixes, value
    assert N47_MEMORY_MAX_BYTES == int(value[:-1]) * suffixes[value[-1]]


def test_the_soft_warning_matches_the_shipped_worker_constant():
    """The harness restates N-45; the worker implements it. Pin them together.

    Before 2026-08-27 the worker implemented nothing and this constant was a
    copy of a register row — the drift it now guards against could not have been
    detected, because there was nothing to drift from.
    """
    from application.worker.runtime import SOFT_WARNING_SECONDS

    assert N45_SOFT_WARNING_SECONDS == SOFT_WARNING_SECONDS
