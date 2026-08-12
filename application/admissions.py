"""Which credential may still turn a submission into a durable acceptance.

This is the answer to review finding B-1, and the whole of the argument is that
it is **not an observation**.

Nine remediations tried to establish that nothing was in flight by looking at
something: a process table, a listening socket, `pg_stat_activity`, a commit
watermark, a lock queue. Every one of them was defeated the same way, because
they share one flaw — an observation of a resource cannot exclude work that has
been *accepted* and has not yet reached that resource. A request paused before
its first statement is invisible to every reading anyone can take, and it commits
whenever it eventually wakes.

So the question changes. Instead of asking "is anything still coming?", which is
unanswerable, settlement asks "**may anything still be accepted?**", and makes
the answer a durable fact it can change.

## The invariant

    Once settlement closes the admission generation a credential writes under, no
    request presenting that credential can create or reuse an accepted snapshot,
    return a successful receipt, or write an acceptance audit event — regardless
    of where that request was paused. A fresh export is accepted only under a
    newly authorized generation belonging to a credential the old request was
    never sent with.

Three properties make it hold, and each is load-bearing:

**The identity is carried in the request's own bytes.** A submission is checked
against the admission of *the principal id in its own `Authorization` header*,
never against "whichever generation is open now". That distinction is the whole
fence. A server-side "current generation" lookup would silently upgrade a request
that was paused before it — which is exactly the hole this replaces.

**A principal holds at most one admission, ever.** `principal_id` is unique
across the whole table for all time, so a closed admission cannot be succeeded by
an open one for the same credential. Recovery issues a new credential and opens a
generation naming *that*. An old request cannot guess it, inherit it, or be
upgraded into it, because it does not hold its secret.

**Closure and acceptance are serialized by the database, not by timing.** The
acceptance writes a row whose foreign key references the admission; the check
takes a row-level `KEY SHARE` lock. Closure takes `FOR UPDATE` on the same row.
Those conflict, so the two can never interleave, and the acceptance's own state
re-read — taken *after* that write and before the commit — sees a closure that
got in first. See `migrations/versions/0005_submission_admission_fence.py` for
the measured behaviour this rests on, including the trap that a plain `UPDATE`
does **not** take a conflicting lock.

## What this deliberately is not

It is not authorization. An admission does not say *who* may submit or *what*
they may submit — `ServicePrincipal` and its scopes still answer both. It says
only whether a credential's generation is still able to produce a durable
acceptance, which is a recovery concept and belongs to recovery.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from uuid import UUID

#: The advisory-lock key every submission transaction and every closure
#: contends on. One key for the whole fence rather than one per admission: a
#: closure is a rare, deliberate operator action, and a single key makes "no
#: submission transaction overlaps a closure" a statement about one lock instead
#: of a claim about which rows two sessions happened to pick.
#:
#: Derived once, then pinned as a literal, because it has to keep meaning the
#: same thing across every process that ever holds it:
#:
#:     int.from_bytes(
#:         hashlib.sha256(b"freedom-blades/submission-admission-fence").digest()[:8],
#:         "big", signed=True,
#:     )
#:
#: `pg_advisory_xact_lock*` needs no grant at all, which is what lets the
#: restricted runtime role take it while holding `SELECT` and nothing else on
#: `submission_admissions`.
ADMISSION_LOCK_KEY = -5869345091194089832

#: The reserved principal migration 0005 attributes pre-fence receipts to. It is
#: deliberately **not** a legal `ServicePrincipal` id — the angle brackets are
#: outside that vocabulary — so no credential can ever authenticate as it and
#: nothing can be accepted under generation 0.
PRE_FENCE_PRINCIPAL = "<pre-admission-fence>"


class AdmissionState(Enum):
    """Open, or closed. There is no third state and no way back."""

    OPEN = "open"
    CLOSED = "closed"


@dataclass(frozen=True, slots=True)
class SubmissionAdmission:
    """One credential's generation, and whether it may still write."""

    id: UUID
    generation: int
    principal_id: str
    state: AdmissionState

    @property
    def is_open(self) -> bool:
        return self.state is AdmissionState.OPEN
