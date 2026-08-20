"""P3.3 remediation: the column that fences the import *effect*, not its publication.

Added by the 2026-08-18 P3.3 remediation, as a **successor** to 0011 rather than
an edit of it. 0011 has been applied to development and disposable test
databases, and `.agents/AGENTS.md` says "never edit an applied migration"; a
successor is also the only form in which the round-trip evidence this remediation
owes — upgrade → downgrade → upgrade against real PostgreSQL — means anything.

## What was wrong, stated so the column is checkable against it

SM-05's forbidden-transition table says a committed apply cannot be cancelled,
and names its mechanism: *"the apply's commit sets `state='completed'`; the
cancel statement filters `state IN ('queued','running')` and matches zero rows"*.

That mechanism did not exist. The apply's commit and the job's completion were
**two transactions**: `SnapshotImportService.apply` committed the import,
characters, mappings and success audit, and only afterwards did the worker
publish `completed` in a second transaction. In between, the job was still
`running`, so a cancellation matched, transitioned it to `cancelled` — and the
import stayed committed. The same gap let a timeout self-abandon, a kill-switch
self-abandon and a reaper requeue leave a job saying `queued`, `stale`, `failed`
or `cancelled` while an abandoned worker thread committed the effect afterwards.

Neither `uq_snapshot_imports_applied_input` nor `snapshot_imports.request_key`
closes it. Uniqueness prevents a **second** effect; it does not prevent the
**first** effect from an attempt that has already been cancelled.

## What the column is

`effect_committed_at` is the durable fact "an import effect committed for this
job", written **inside the transaction that commits that effect** and by nothing
else. It is one timestamp, and it turns three separate races into one row-level
serialization on the job row:

- the fence's `UPDATE … SET effect_committed_at = now() WHERE id = $1 AND
  lease_owner = $2 AND state = 'running' AND cancel_requested_at IS NULL AND
  effect_committed_at IS NULL` takes the job row's write lock as the last
  statement before the import commits;
- every writer that would invalidate the attempt — the cancellation request and
  the worker's self-abandon — carries `AND effect_committed_at IS NULL`, so it
  blocks on that lock and then re-evaluates its predicate under `READ COMMITTED`;
- the reaper's `FOR UPDATE SKIP LOCKED` skips a locked row rather than reaping it.

Exactly one side therefore wins, and the loser writes nothing.

## Why it is nullable, and why the check constraint is narrow

A preview commits no effect, so the column is `NULL` for every preview and the
check constraint says so. It is not `NOT NULL` with a sentinel because "no effect
has committed" is the ordinary state of a job for its whole life, including every
terminal state a preview can reach.

The column is deliberately **not** cleared by the reaper's requeue. A crash
between the effect's commit and the job's result publication must leave the
requeued attempt able to recover the same import as a duplicate (SM-05's process
restart), and the recovery path never reaches the fence: it returns the existing
import before any write. Clearing the column would erase the only durable record
that the effect exists.

## Reversible, and rehearsed

`downgrade()` drops exactly what `upgrade()` added. Because the column is only
ever `NULL` for a preview and a timestamp for an apply whose effect committed,
dropping it loses no fact that is not also in `snapshot_imports` — the immutable
receipt of what was applied — so the downgrade destroys no history.
`tests/web/test_migration_0012_round_trip.py` runs upgrade → downgrade → upgrade
against real PostgreSQL and asserts the schema is identical either side.
"""
from __future__ import annotations

from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0012"
down_revision: str | None = "0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "reconciliation_jobs",
        sa.Column("effect_committed_at", sa.DateTime(timezone=True), nullable=True),
    )
    # A preview writes only its own result row, so it has no effect to fence.
    op.create_check_constraint(
        "only_an_apply_commits_an_effect",
        "reconciliation_jobs",
        "(kind = 'apply') OR (effect_committed_at IS NULL)",
    )


def downgrade() -> None:
    op.drop_constraint(
        # The **unqualified** name: the metadata's naming convention
        # (`ck_%(table_name)s_%(constraint_name)s`) is applied on the way out, so
        # passing the rendered name here would render it a second time.
        "only_an_apply_commits_an_effect",
        "reconciliation_jobs",
        type_="check",
    )
    op.drop_column("reconciliation_jobs", "effect_committed_at")
