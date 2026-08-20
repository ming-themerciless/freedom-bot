"""N-24: remove reconciliation job and result records past their retention.

    python -m tools.job_retention --report
    python -m tools.job_retention --apply --operator "…"

**An operator command, run as the schema owner, and that is a control rather
than an inconvenience.** The restricted runtime role holds no `DELETE` on
`reconciliation_jobs` (schema §11.2, and the grants template says why): a web
process or a worker that could delete a job could delete the record of a refused
apply. So the sweep is a deliberate act by somebody with host authority, and it
is auditable because it is a command rather than a background timer nobody
watches.

## What it removes, and what it must never touch

Removed: terminal `reconciliation_jobs` rows whose retention has elapsed, and —
by `ON DELETE CASCADE` from the job — the `reconciliation_job_results` rows that
belong to them. Both are **presentation records**: disposable, never read by a
calculation, never a source of authority, and reproducible by re-running the job
against the immutable snapshot.

Never touched, and the distinction is the whole of N-24:

- `snapshot_imports` — the immutable receipt of what was applied, append-only and
  retained indefinitely;
- `audit_events` — append-only and retained indefinitely (OD-23);
- `foundry_snapshots` — append-only; the artifact itself follows the separate
  snapshot-retention procedure (change-log C-8);
- any job that is **not terminal**. A `queued` or `running` job has no retention
  age, and deleting one would delete work in flight;
- any job a **retained** job still needs. An apply names the preview it was
  confirmed from with `parent_job_id … ON DELETE RESTRICT`, so a preview whose
  apply is younger than the retention age stays, and so does the whole graph
  above it.

## What was wrong before this file was rewritten (2026-08-18 remediation)

Two defects, both of which made the command fail rather than under-delete:

1. It ran `UPDATE reconciliation_jobs SET result_id = NULL` before deleting, to
   "break the foreign-key cycle". Migration 0011 enforces
   `CHECK ((state = 'completed') = (result_id IS NOT NULL))`, so that statement
   raises for **every completed job** — which is most of what a sweep removes.
   The cycle needs no breaking: deleting the job cascades to its result, and the
   `RESTRICT` on `reconciliation_jobs.result_id` is satisfied because the only
   row that referenced the result is the one already being deleted.
2. It selected expired previews without regard to their apply children, so a
   sweep could raise on `fk_reconciliation_jobs_parent_job_id_reconciliation_jobs`
   and abort — leaving an operator with an error where the answer is "that graph
   is not eligible yet".

Neither is fixed by disabling a constraint, by catching the integrity error, or
by widening the cascade. The eligible set is computed so that the constraints
never have anything to object to, and it is computed inside the same transaction
that deletes.

## Eligibility, stated once

A job is a **candidate** when all of these hold:

- its state is terminal (`completed`, `stale`, `failed`, `cancelled`);
- it finished more than N-24's 30 days ago; and
- if it has a result row, that row's own `expires_at` has passed.

The second and third conditions are both applied because they can disagree: a
result's `expires_at` is set from when the result was *produced*, and the job's
retention runs from when it reached a terminal state. A job with no result row —
a `failed` or `cancelled` job that never produced one — is eligible on the first
two conditions alone, which is what stops those accumulating forever.

A candidate is **removed** only if every job that names it as a parent is also
being removed in this same statement. That is computed as a fixed point rather
than one pass, so a chain of any depth is retained whole rather than partly.

## Atomicity, and the audit event that can veto it

One transaction: the candidate lock, the delete, and the bounded audit event.
The audit event is written *in* that transaction on purpose — if it cannot be
written, the deletions roll back, so the platform never removes working papers
without recording that it did.

## Exit codes

`0` completed · `1` refused · `4` usage.
"""
from __future__ import annotations

import argparse
import os
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, text

from adapters.database.config import DatabaseSettings
from adapters.database.safety import ConnectionPolicy
from application.web.jobs import RESULT_RETENTION_DAYS

EXIT_OK = 0
EXIT_REFUSED = 1
EXIT_USAGE = 4

#: The largest `--limit` the command accepts. One sweep is one transaction, and
#: a transaction that deleted a million rows would hold locks on the job table
#: for as long as it took — which is the backlog problem the limit exists to
#: prevent, reintroduced by an operator typing a big number. Sweeping repeatedly
#: is safe and removes zero once the backlog is gone, so a bound costs nothing.
MAX_LIMIT = 10_000
DEFAULT_LIMIT = 500


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class LimitRefused(ValueError):
    """`--limit` was not a positive, bounded number of jobs."""


def validated_limit(value: int) -> int:
    """Refuse a nonsensical limit **before** a connection is opened.

    Deliberately a function rather than an `argparse` type: the refusal has to be
    a documented exit code with a sentence an operator can act on, and an
    `argparse` type error is a usage dump.
    """
    if value < 1:
        raise LimitRefused(
            f"--limit must be at least 1; {value} would sweep nothing while "
            "reporting success."
        )
    if value > MAX_LIMIT:
        raise LimitRefused(
            f"--limit must be at most {MAX_LIMIT}; {value} would make one sweep "
            "one long transaction holding locks on the job table. Run the "
            "command repeatedly instead — a sweep that has caught up removes "
            "zero."
        )
    return value


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--apply",
        action="store_true",
        help="actually delete; without it the command reports and changes nothing",
    )
    parser.add_argument(
        "--operator",
        help="the person running the sweep; required with --apply, recorded in the "
        "audit event and never a credential",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help="maximum jobs removed in one pass, so a backlog cannot become one "
        f"long transaction (default: {DEFAULT_LIMIT}, maximum: {MAX_LIMIT})",
    )
    return parser.parse_args(argv)


#: The candidate set: terminal, past N-24's age, and — if it produced one — past
#: its result's own expiry.
#:
#: `LEFT JOIN`, not `JOIN`: a `failed` or `cancelled` job that never produced a
#: result has no row to join to, and an inner join is what made those invisible
#: to every sweep that ever ran.
_CANDIDATES = """
    SELECT j.id, j.parent_job_id
    FROM reconciliation_jobs j
    LEFT JOIN reconciliation_job_results r ON r.job_id = j.id
    WHERE j.state IN ('completed', 'stale', 'failed', 'cancelled')
      AND j.finished_at < :cutoff
      AND (r.id IS NULL OR r.expires_at < :now)
    ORDER BY j.finished_at
    LIMIT :limit
"""

#: Report mode. The same predicate, and **no lock**: a report that took row locks
#: would block the enqueue path while somebody read a count.
_REPORT = text(f"WITH candidate AS ({_CANDIDATES}) SELECT count(*) FROM candidate")

#: Apply mode. `FOR UPDATE OF j SKIP LOCKED` does two things at once:
#:
#: - it makes the eligible set concurrency-safe, so two sweeps take disjoint sets
#:   rather than blocking or double-counting; and
#: - it is what makes the parent/child check hold until the commit. Inserting an
#:   apply child takes a `KEY SHARE` lock on its parent row, which conflicts with
#:   `FOR UPDATE`, so no new child can appear beneath a locked candidate between
#:   the check and the delete.
_LOCKED_CANDIDATES = text(f"{_CANDIDATES} FOR UPDATE OF j SKIP LOCKED")

#: The delete, with the retained-graph rule as a fixed point.
#:
#: `blocked` starts from candidates that have a child nobody is deleting, and
#: grows upward through parents of blocked candidates until it stops changing. A
#: single `NOT EXISTS` pass would be correct only for a two-level graph; the
#: recursion is correct for any depth, which is what "retains a parent while any
#: required child remains" actually requires.
_DELETE = text(
    """
    WITH RECURSIVE candidate AS (
        SELECT id, parent_job_id FROM reconciliation_jobs
        WHERE id = ANY(:ids)
    ), blocked AS (
        SELECT c.id
        FROM candidate c
        WHERE EXISTS (
            SELECT 1 FROM reconciliation_jobs child
            WHERE child.parent_job_id = c.id
              AND NOT (child.id = ANY(:ids))
        )
        UNION
        SELECT parent.id
        FROM blocked b
        JOIN reconciliation_jobs child ON child.id = b.id
        JOIN candidate parent ON parent.id = child.parent_job_id
    )
    DELETE FROM reconciliation_jobs
    WHERE id = ANY(:ids)
      AND id NOT IN (SELECT id FROM blocked)
    """
)

#: The sweep is itself an audited administrative act. The payload carries a
#: **count and the operator's name** — never a job id, a checksum or a requester,
#: because a retention record that listed what it removed would outlive the thing
#: it was removing.
_AUDIT = text(
    "INSERT INTO audit_events (id, actor_capability, action, "
    "entity_type, entity_id, source, correlation_id, payload) "
    "VALUES (gen_random_uuid(), 'system', "
    "'reconciliation.retention_swept', 'reconciliation_job', "
    "'n-24', 'system', gen_random_uuid(), "
    # Cast explicitly: `jsonb_build_object` is variadic `"any"`, so PostgreSQL
    # cannot infer a bare placeholder's type and refuses the statement rather
    # than guessing. `CAST(… AS …)` rather than `::`, because `::` is what
    # SQLAlchemy's own `:name` bind-parameter syntax collides with.
    "jsonb_build_object('removed', CAST(:removed AS int), "
    "'considered', CAST(:considered AS int), "
    "'operator', CAST(:operator AS text)))"
)


@dataclass(frozen=True, slots=True)
class SweepResult:
    """What one pass considered and what it actually removed.

    The two numbers differ exactly when a candidate was retained because a job
    that needs it is not eligible yet, which is the case an operator most wants
    to be able to see without reading SQL.
    """

    considered: int
    removed: int

    @property
    def retained_graphs(self) -> int:
        return self.considered - self.removed


class RetentionSweep:
    """N-24's sweep as one object, so the tests exercise the production statement.

    The command below is a thin argument parser around this class. A test that
    re-implemented the statement would prove nothing about the command, and a
    test that could only drive the command through `main()` could not assert the
    intermediate counts — so the transaction is here and both callers use it.
    """

    __slots__ = ("_retention_days",)

    def __init__(self, *, retention_days: int = RESULT_RETENTION_DAYS) -> None:
        self._retention_days = retention_days

    def cutoff(self, now: datetime) -> datetime:
        return now - timedelta(days=self._retention_days)

    def report(self, connection, *, now: datetime, limit: int) -> int:
        """How many jobs a sweep would consider. **Writes nothing, locks nothing.**"""
        return int(
            connection.execute(
                _REPORT,
                {"now": now, "cutoff": self.cutoff(now), "limit": limit},
            ).scalar_one()
        )

    def apply(
        self, connection, *, now: datetime, limit: int, operator: str
    ) -> SweepResult:
        """Lock the eligible set, delete the removable graphs, audit the pass.

        Every part of it is in the caller's transaction — this method opens none
        of its own — so an audit failure rolls the deletions back with it.
        """
        candidates = [
            row[0]
            for row in connection.execute(
                _LOCKED_CANDIDATES,
                {"now": now, "cutoff": self.cutoff(now), "limit": limit},
            ).all()
        ]
        removed = 0
        if candidates:
            # `ON DELETE CASCADE` from job to result carries each result with its
            # job. Nothing nulls `result_id` first: that update would violate
            # `CHECK ((state = 'completed') = (result_id IS NOT NULL))`, and the
            # `RESTRICT` it was meant to appease is satisfied anyway, because the
            # only row referencing a deleted result is the job deleted with it.
            removed = connection.execute(_DELETE, {"ids": candidates}).rowcount
        connection.execute(
            _AUDIT,
            {
                "removed": removed,
                "considered": len(candidates),
                "operator": operator,
            },
        )
        return SweepResult(considered=len(candidates), removed=removed)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_arguments(argv)
    if arguments.apply and not (arguments.operator or "").strip():
        print("Refused: --apply requires --operator naming the person running it.")
        return EXIT_USAGE
    # Before the settings are read and before any connection exists: an argument
    # that can be refused from its own value is refused from its own value.
    try:
        limit = validated_limit(arguments.limit)
    except LimitRefused as refusal:
        print(f"Refused: {refusal}")
        return EXIT_USAGE

    try:
        settings = DatabaseSettings.from_mapping(
            os.environ,
            environment=os.environ.get("APP_ENVIRONMENT", "development"),
            environ=os.environ,
            policy=ConnectionPolicy.SOCKET_OR_LOOPBACK,
        )
    except ValueError as refusal:
        print(f"Refused: {refusal}")
        return EXIT_REFUSED

    engine = create_engine(settings.url)
    sweep = RetentionSweep()
    now = utcnow()
    try:
        with engine.begin() as connection:
            if not arguments.apply:
                considered = sweep.report(connection, now=now, limit=limit)
                print(f"{considered} terminal job(s) past their N-24 retention.")
                print("Nothing removed. Re-run with --apply --operator to remove them.")
                return EXIT_OK

            result = sweep.apply(
                connection,
                now=now,
                limit=limit,
                operator=arguments.operator.strip(),
            )
            print(
                f"{result.considered} terminal job(s) past their N-24 retention."
            )
            print(f"Removed {result.removed} job(s) and their results.")
            if result.retained_graphs:
                print(
                    f"Retained {result.retained_graphs} job(s) whose apply child "
                    "has not yet reached its own retention age."
                )
            print(
                "snapshot_imports, audit_events and foundry_snapshots are "
                "untouched: N-24 removes presentation records, not history."
            )
    finally:
        engine.dispose()
    return EXIT_OK


if __name__ == "__main__":  # pragma: no cover - operator entry point
    raise SystemExit(main())
