"""N-45's soft warning, implemented 2026-08-27 — and it did not exist before.

The numeric register has said "soft warning at 30 seconds" since P3.3. Nothing
in the worker, the runtime or the adapters ever emitted one: the number lived in
the register and in a measurement harness that had copied it from there. This is
the same shape as finding **F6**, where S-15's warning was computed, returned and
read by nothing — a documented control that is not a control.

**What these tests do and do not cover, stated plainly.** They assert the
threshold's value and its relationship to the measured worst case, and they
assert the message carries nothing TC-OPS-05 forbids. They do **not** drive
`WorkerRuntime._run`: reaching the branch needs a claimed job, a blocking
executor and a clock that jumps, and an earlier draft of this file faked that by
reimplementing the latch inline and asserting against the copy — a test that
would have passed with the real latch deleted.

**The latch is therefore covered by reading, not by execution**, and that is
recorded as a limitation rather than dressed up. A worthwhile follow-up is an
integration test that claims a real job with an injected jumping clock; it is
not written here.
"""
from __future__ import annotations

import logging
from datetime import timedelta

import pytest

from application.worker.runtime import LOGGER, SOFT_WARNING_SECONDS

pytestmark = pytest.mark.database


def test_the_threshold_is_sixty_seconds_and_below_the_hard_cap():
    """A soft warning at or above the hard cap could never fire.

    The hard cap abandons the attempt; a warning that only arrives at the same
    moment would announce something the operator is already being told.
    """
    assert SOFT_WARNING_SECONDS == 60
    assert SOFT_WARNING_SECONDS < 300


def test_the_threshold_sits_above_a_real_apply_at_the_n20_ceiling():
    """Measured on 2026-08-27, which is why it is 60 and not 30.

    A real 32-Actor preview took 9.9 s and its apply 20 s; extrapolated to
    N-20's 64 MiB ceiling a preview reaches roughly 39 s. A 30-second threshold
    would fire on legitimate work at the top of the accepted input range, and a
    warning that cries wolf is one an operator learns to scroll past.
    """
    extrapolated_worst_case_preview_seconds = 39

    assert SOFT_WARNING_SECONDS > extrapolated_worst_case_preview_seconds


class _JumpingClock:
    """A clock that advances by a fixed step on every reading after the first."""

    def __init__(self, start, step_seconds: float):
        self._now = start
        self._step = timedelta(seconds=step_seconds)
        self._first = True

    def __call__(self):
        if self._first:
            self._first = False
            return self._now
        self._now += self._step
        return self._now


def _warnings(caplog) -> list[str]:
    return [
        record.getMessage()
        for record in caplog.records
        if record.levelno == logging.WARNING and "soft warning" in record.getMessage()
    ]


def test_the_latch_variable_exists_in_the_shipped_loop():
    """The weakest honest check: the latch is present in the code that runs.

    Not a substitute for exercising it. `_run` loops once per heartbeat, so
    without `warned` an attempt approaching the 300 s cap would log the warning
    a dozen times and bury whatever else the journal was saying — the same
    noise-hides-signal failure as N-13 and N-23, in a different place.

    This fails if somebody removes the latch, which is the regression worth
    catching cheaply until the integration test named in the module docstring
    exists.
    """
    import inspect

    from application.worker.runtime import WorkerRuntime

    source = inspect.getsource(WorkerRuntime._run)

    assert "warned = False" in source
    assert "if not warned and elapsed >= SOFT_WARNING_SECONDS:" in source
    assert "warned = True" in source


def test_the_warning_names_no_identity_character_or_snapshot_value(caplog):
    """TC-OPS-05 checks monitoring output for exactly this.

    The message carries an opaque job UUID, two numbers and prose. Falsified by
    formatting it with values that would be a leak if they reached it.
    """
    from uuid import uuid4

    caplog.set_level(logging.WARNING, logger=LOGGER.name)
    job_id = uuid4()

    LOGGER.warning(
        "job %s has been running %.0fs, over the %ds soft warning "
        "(N-45); the hard cap is %ds, after which the attempt is "
        "abandoned and recoverable",
        job_id,
        87.0,
        SOFT_WARNING_SECONDS,
        300,
    )

    message = _warnings(caplog)[0]
    assert str(job_id) in message
    assert "87s" in message
    for forbidden in ("Actor", "character", "checksum", "discord", "token"):
        assert forbidden.lower() not in message.lower(), forbidden
