"""Publishing the result of an effect whose process died before it could.

Added by the 2026-08-18 P3.3 effect-publication remediation, for the second of the
two blocking findings: *a committed effect can become `failed` on attempt three.*

## The window, and why the old answer ran out

An apply is two commits with a gap between them:

```text
    T1  SnapshotImportService.apply → import, characters, mappings, applied audit
                                      event, and the commit fence               COMMIT
                       ←── the gap: the job is still `running` here ──→
    T2  WorkerRuntime._publish_result → result row + state = 'completed'        COMMIT
```

The commit fence closed the gap against everything that would have **denied** the
effect — a cancellation, a self-abandon, R-41's invalidation, R-46's expiry. It did
not answer the other question: who publishes T2 when the process dies inside the
gap?

The answer used to be "the reaper requeues the job and the next attempt recovers
the import as a duplicate". That answer:

- **spends one of N-43's three attempts** on work whose effect is already durable;
- **has none left at `attempts = 3`**, where the reaper wrote `failed` with
  `attempts_exhausted` over a real import — the finding;
- re-parses the artifact and re-resolves Council authority, so it can end `stale`
  (authority revoked, folder moved) or `failed` (artifact unreadable) for reasons
  that say nothing about the import that committed; and
- depends on a *re-execution* succeeding, which is a much larger surface than the
  publication it is trying to reach.

## What replaces it

Nothing is re-executed. The fence now writes the publication payload —
`reconciliation_jobs.effect_result` — in the same statement, and therefore the same
transaction, as the effect. Recovery is then two durable reads and one write
transaction:

1. `effect_result`, for what the run produced: the bounded summary and the blocked
   create-candidates;
2. the immutable `snapshot_imports` row named by the job's `request_key`, for the
   import's identity and its committed counts; and
3. one transaction that inserts the result, completes the job and records the
   completion event.

`recovered_summary` below is step 2's merge, and it is deliberately the *same five
keys* `JobExecutor._apply` merges from the live `ImportOutcome`. A recovered result
and the result the dead process would have published are the same document but for
the `recovered` marker.

**Nothing here is derived from caller input, from a cache, or from the database as
it stands now.** Every value is read from a row that was written inside the
transaction that committed the effect, which is what makes the published summary
answer for the instant the import committed rather than for the instant the
recovery ran. That is Phase 2 finding B-1R's rule, applied to the job's result.
"""
from __future__ import annotations

from typing import Any

#: Marks a result published by recovery rather than by the process that ran the
#: attempt. Carried in the stored summary and in the completion audit payload, so
#: an operator reading either can tell which hand published it.
#:
#: It is **not** rendered as a different outcome: the job is `completed`, the import
#: is durable, and the Council member's receipt is the same receipt. What the marker
#: answers is the operational question "did the worker that ran this ever come
#: back", which belongs in the record and not on the screen.
RECOVERED_KEY = "recovered"


class EffectPublicationUnavailable(RuntimeError):
    """A committed effect could not be published from durable data.

    Raised rather than worked around, and deliberately never turned into `failed`:
    the import is real, and a job that denied it would be the defect this module
    exists to remove. The job stays `running` with an expired lease, which is
    exactly what VM-16's `expired_lease_age_seconds` alarm is for, and the next
    recovery pass tries again.

    Reaching it means a row this schema forbids exists — migration 0013's
    `CHECK ((effect_committed_at IS NULL) = (effect_result IS NULL))` and the
    fence's single transaction make both causes unrepresentable — so the message
    names the job and the missing half and nothing else.
    """

    __slots__ = ("job_id",)

    def __init__(self, job_id, *, missing: str) -> None:
        super().__init__(
            f"Reconciliation job {job_id} recorded a committed import effect but "
            f"its {missing} cannot be read, so no result can be published from "
            "durable data. The import itself is unaffected and is recorded in "
            "`snapshot_imports`; nothing was written and the job remains "
            "recoverable."
        )
        self.job_id = job_id


def recovered_result(job, receipt) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """`(summary, blocked_entries)` for a job whose effect committed unpublished.

    `job` is the `reconciliation_jobs` row and `receipt` is the `snapshot_imports`
    row its `request_key` names. Both are durable; neither is recomputed.

    Raises `EffectPublicationUnavailable` rather than inventing a value, for the
    same reason `SnapshotImportService._original_facts` refuses rather than
    recomputing: a result that cannot be answered with the original operation's own
    facts must not be answered with fresh ones.
    """
    stored = job["effect_result"]
    if not isinstance(stored, dict):
        raise EffectPublicationUnavailable(job["id"], missing="publication payload")
    summary = stored.get("summary")
    if not isinstance(summary, dict):
        raise EffectPublicationUnavailable(job["id"], missing="bounded summary")
    blocked = stored.get("blocked_entries")
    if not isinstance(blocked, list):
        raise EffectPublicationUnavailable(job["id"], missing="blocked entries")
    if receipt is None:
        raise EffectPublicationUnavailable(job["id"], missing="import receipt")

    recovered = dict(summary)
    recovered.update(
        {
            # The five keys `JobExecutor._apply` merges from the live
            # `ImportOutcome`, read here from the immutable row that outcome was
            # built from. `duplicate` is `False` because nothing was applied
            # twice: this job's own first and only effect wrote this import, and
            # calling it a duplicate would describe an attempt that never
            # happened.
            "import_id": str(receipt["id"]),
            "duplicate": False,
            "created_count": int(receipt["created_count"]),
            "updated_count": int(receipt["updated_count"]),
            "warning_count": int(receipt["warning_count"]),
            RECOVERED_KEY: True,
        }
    )
    return recovered, [dict(entry) for entry in blocked]


def recovery_payload(job, summary) -> dict[str, Any]:
    """The completion audit payload for a recovered publication.

    The same shape `WorkerRuntime._completion_payload` builds — counts, codes and
    identifiers, never content — plus what makes this one different: that it was
    published by recovery, how many attempts the job had actually taken, and the
    lease that stopped answering. An operator reading the append-only record can
    then tell a job the worker finished from a job the platform finished for it.
    """
    from application.worker.runtime import completion_payload

    payload = completion_payload(job, summary)
    payload.update(
        {
            RECOVERED_KEY: True,
            "recovery_reason": "effect_committed_unpublished",
            "attempts": job["attempts"],
            # The lease that held the job when its process stopped answering. It
            # is a worker instance and a random token — never a credential, a
            # requester or anything the artifact contained (N-25).
            "lease_owner": job["lease_owner"],
        }
    )
    return payload


__all__ = [
    "RECOVERED_KEY",
    "EffectPublicationUnavailable",
    "recovered_result",
    "recovery_payload",
]
