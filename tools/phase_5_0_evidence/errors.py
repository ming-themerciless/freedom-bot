"""The harness's refusals, typed so a caller cannot confuse them.

Three distinct failures, and collapsing any two of them would hide something a
reviewer needs to see:

* `TargetRefused` — the *target* is not admissible. Nothing was planned and
  nothing was classified. This is the guard that keeps the harness away from `/`,
  the repository worktree, `/var/lib`, a production database name and an
  unresolved environment variable.
* `PlanRefused` — the target is fine but the *plan* is not: a mutation-bearing
  case was assembled without the plan declaring that mutation, a cleanup step
  would delete something broad, or a step's argument vector is malformed.
* `ObservationRefused` — the *observation handed to a classifier* is not usable:
  a mask that is not an integer, a `/proc/self/status` extract missing a field a
  case must assert, a probe report missing a stage.

None of them is an assertion that a control failed. A failed control is an
evidence *result* (`Status.INCONCLUSIVE`), not an exception, because the run must
continue and record it.
"""
from __future__ import annotations


class HarnessError(Exception):
    """Base class, so a caller can catch every refusal this package raises."""


class TargetRefused(HarnessError):
    """The proposed target is not a disposable target this harness will touch."""


class PlanRefused(HarnessError):
    """The execution plan does not admit the step or cleanup being assembled."""


class ObservationRefused(HarnessError):
    """An observation handed to a classifier is malformed or incomplete."""


__all__ = [
    "HarnessError",
    "ObservationRefused",
    "PlanRefused",
    "TargetRefused",
]
