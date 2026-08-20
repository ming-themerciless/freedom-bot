"""The commit fence: proof, inside the effect's own transaction, of entitlement.

Added by the 2026-08-18 P3.3 remediation. It exists because the previous design
fenced the *publication of a job result* and left the **effect** unfenced, and
those are two transactions with a window between them:

```text
    T1:  apply()            → import, characters, mappings, success audit  COMMIT
                             ← window: the job is still `running` here →
    T2:  publish()          → result row + state = 'completed'            COMMIT
```

Anything that transitioned the job during that window — a cancellation observed
at a heartbeat, a timeout self-abandon, a kill-switch self-abandon, a reaper
requeue after a lease expiry — produced a job saying `cancelled`, `queued`,
`stale` or `failed` whose abandoned worker thread had already committed, or was
about to commit, real character and import state.

`uq_snapshot_imports_applied_input` and `snapshot_imports.request_key` do not
close it. **Uniqueness prevents a second effect; it does not prevent the first
effect from an attempt that has already been cancelled.**

## What the fence is, and what it is deliberately not

It is one `UPDATE` issued on the **same session as the effect**, as the last
statement before that session commits. It is not a Python event, not a check
before the service is called, not a re-read afterwards, and not a thread join:
each of those leaves a window, and the window is the defect.

Because it is an `UPDATE` it takes the job row's write lock, and that lock is the
serialization. Every writer that would invalidate the attempt — the cancellation
request in `ReconciliationJobRepository.request_cancel`, the worker's self-abandon
in `.abandon` — carries `AND effect_committed_at IS NULL`, so it either

- reaches the row first, commits, and the fence's `UPDATE` then re-evaluates its
  predicate under `READ COMMITTED`, matches zero rows and rolls the whole effect
  back; or
- reaches the row second, blocks on the lock the fence holds, and after the
  effect commits re-evaluates *its* predicate, matches zero rows and refuses.

The reaper is the third writer and needs no predicate: its sub-select is
`FOR UPDATE SKIP LOCKED`, so it skips a row the fence holds rather than reaping
it, and it acts on the next pass if the effect rolled back.

Exactly one side wins in every interleaving, and the loser writes nothing.

## The second thing the fence writes, and why it writes it here

Added by the 2026-08-18 effect-publication remediation. Fencing the effect made a
cancelled or abandoned attempt unable to commit; it did not make a **committed**
attempt able to publish. The result the worker owes was an in-memory `Executed`
value on the execution thread, and process death took it with it. The only
recovery left was to requeue the job and re-run the whole attempt — which spends
one of N-43's three, re-parses the artifact, re-resolves Council authority, and can
end `stale` or `failed` for reasons that have nothing to do with the import that
already committed. At `attempts = 3` there was no attempt left to spend, and the
reaper wrote `failed` over a durable import.

So the fence writes the publication payload in the same statement as the timestamp:
the bounded summary and blocked-entry list the run produced, which is everything
the result row needs except the import's own identity and counts — and those are in
the immutable `snapshot_imports` receipt the same transaction commits.

`CHECK ((effect_committed_at IS NULL) = (effect_result IS NULL))` (migration 0013)
is what turns "the fence writes both" from a convention into a fact: an effect
whose publication cannot be reconstructed from durable data is unrepresentable.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Protocol
from uuid import UUID


class FenceLost(RuntimeError):
    """The attempt is no longer entitled to commit, so it committed nothing.

    Deliberately **not** an `ImportRefused`. A refusal is a statement about the
    caller's inputs and is recorded as an attempted import in its own
    transaction; this is a statement about a race the design anticipates, and
    writing a refusal row for it would be writing exactly the kind of durable
    effect the fence exists to prevent.
    """

    __slots__ = ("job_id", "owner")

    def __init__(self, *, job_id: UUID, owner: str) -> None:
        super().__init__(
            "The job lease that authorised this apply is no longer live, so "
            "nothing was committed."
        )
        self.job_id = job_id
        self.owner = owner


@dataclass(frozen=True, slots=True)
class PendingEffectResult:
    """What the run produced, ready to be published, before the effect commits.

    The half of the durable result that is known **before** the import service
    returns: the bounded summary of the reconciliation and its blocked
    create-candidates. The other half — the import id, whether it was a duplicate,
    and the created/updated/warning counts — belongs to the `snapshot_imports` row
    the same transaction writes, so it is read from there at publication rather
    than copied into two places that can disagree.

    Frozen, and rendered to a plain mapping by `payload()`, because what goes into
    `reconciliation_jobs.effect_result` is `jsonb` and what comes back out of it is
    a mapping. The bounds are the ones `application/worker/execution.py` already
    applies at the point the values are built: counts, closed-vocabulary issue
    codes, the folder identity, the checksum, and at most 50 blocked entries
    carrying one 120-character display name each.
    """

    summary: dict[str, Any]
    blocked_entries: list[dict[str, Any]] = field(default_factory=list)

    def payload(self) -> dict[str, Any]:
        """The `jsonb` value, with the two halves named rather than merged.

        Named rather than merged because a publication has to put them in two
        different columns — `reconciliation_job_results.summary` and
        `.blocked_entries` — and a merged blob would need a rule about which keys
        belong to which.
        """
        return {
            "summary": dict(self.summary),
            "blocked_entries": [dict(entry) for entry in self.blocked_entries],
        }


class CommitFence(Protocol):
    """What a caller passes to `SnapshotImportService.apply` to fence its effect.

    A protocol rather than a concrete type because the import service must not
    depend on the job model: Phase 2's operator path and the supervised bootstrap
    have no job, pass no fence, and are unchanged.
    """

    def hold(self, unit_of_work) -> None:
        """Raise `FenceLost` unless this transaction may commit its effect."""
        ...


class JobLeaseFence:
    """One claimed job's entitlement to commit, checked where it commits.

    Holds the per-claim fencing token — `{instance}:{token}`, minted fresh by
    every claim — rather than the worker's identity, so an attempt whose lease
    expired cannot be revalidated by the *same process* reclaiming the job. That
    is the classic fencing failure and case 7 of the remediation's race suite.
    """

    __slots__ = ("_job_id", "_owner", "_clock", "_pending")

    def __init__(
        self,
        *,
        job_id: UUID,
        owner: str,
        clock: Callable[[], datetime],
        pending: PendingEffectResult,
    ) -> None:
        self._job_id = job_id
        self._owner = owner
        self._clock = clock
        #: What this attempt owes the job if it commits. Required rather than
        #: optional: a fence that could stamp `effect_committed_at` without it
        #: would be a fence able to make an effect durable that no later process
        #: can publish, and migration 0013's check constraint refuses the row
        #: anyway.
        self._pending = pending

    def hold(self, unit_of_work) -> None:
        if not unit_of_work.job_leases.hold_for_effect(
            job_id=self._job_id,
            owner=self._owner,
            now=self._clock(),
            result=self._pending.payload(),
        ):
            raise FenceLost(job_id=self._job_id, owner=self._owner)


__all__ = ["CommitFence", "FenceLost", "JobLeaseFence", "PendingEffectResult"]
