"""P3.3: snapshot folder selection, durable reconciliation jobs and their results.

Schema §10, and the corrected N-43 in particular. Three tables, one of which the
accepted schema does not name — and the exception is stated here rather than
discovered in review.

## Why `snapshot_folder_selections` exists

R-41 sets the Actor folder for a snapshot and R-40 renders it, so the selection
must be durable and changeable. It cannot live on `foundry_snapshots`: schema
§11 classifies that table `SELECT, INSERT` for the runtime role, and migration
0002's trigger refuses `UPDATE` and `DELETE` on it **for the schema owner too**.
§10 defines only the two job tables and §11 names no table for the selection, so
the decomposition is this package's.

This follows the precedent P3.2 set and the gate accepted: migration 0010 added
`identity_migration_runs` and `identity_link_proposal_candidates`, two tables §11
does not name, because the accepted behaviour required a representation the
decision table had not spelled out — and recorded the addition in the submission.
The same is done here. Nothing about data authority, authorization, privacy,
migration or rollback moves: the folder selection is operational state whose one
writer is R-41, whose one authority is Platform Administrator, and whose history
is the append-only `snapshot.folder_selected` audit event the route contract
already requires.

## What the constraints are doing, and why they are constraints

The state machine SM-05 is not a set of rules the worker follows. Every one of
them that can be expressed as a check constraint is one, because the runtime role
holds `UPDATE` on `reconciliation_jobs` and a rule that lived only in Python
would be one direct statement away from being false:

- `completed` without a durable result is unrepresentable, which is delivery plan
  §8.7's "no state named `completed` precedes durable commit";
- a terminal state without `finished_at`, a `failed` without a code, a `stale`
  without a reason are each unrepresentable;
- `running` and holding a lease are the same fact, in both directions;
- and `state <> 'queued' OR attempts < 3` makes **the stranded state
  unrepresentable**. That is the constraint the first revision of the contract
  lacked, and its absence is what let a job whose third lease expired sit
  `running` with nobody running it: the reaper requeued only while
  `attempts < 3`, and a fourth claim would have violated the cap anyway.

`uq_reconciliation_jobs_one_live_apply` is the second half of an idempotency
argument whose first half already exists. `uq_snapshot_imports_applied_input`
(migration 0001) already stops two applies of one input from both committing;
this index stops the second from starting and spending ten seconds of parsing to
discover it.

## The foreign-key cycle, and why it is not avoided

A job names its result and a result names its job. The alternative — dropping
`reconciliation_jobs.result_id` and joining from the result side — would make
`CHECK ((state = 'completed') = (result_id IS NOT NULL))` inexpressible, and that
check is the one that makes the durable-commit rule a property of the table. The
cycle is created with `use_alter`: both tables are created without the two keys,
then each key is added. `downgrade()` drops them in the opposite order.

## Reversible, and rehearsed

`downgrade()` removes exactly what `upgrade()` added and nothing else. It drops
no pre-existing object, and it touches no row of `foundry_snapshots`,
`snapshot_imports` or `audit_events` — the three append-only tables this package
reads and never rewrites. `tests/web/test_migration_0011_round_trip.py` runs
upgrade → downgrade → upgrade against real PostgreSQL and asserts the schema is
identical either side and that seeded history is untouched.
"""
from __future__ import annotations

from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0011"
down_revision: str | None = "0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "snapshot_folder_selections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("snapshot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("folder_id", sa.String(64), nullable=False),
        sa.Column("folder_path", sa.Text(), nullable=False),
        sa.Column(
            "selected_by_account_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column(
            "selected_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("correlation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.ForeignKeyConstraint(
            ["snapshot_id"],
            ["foundry_snapshots.id"],
            name="fk_snapshot_folder_selections_snapshot_id_foundry_snapshots",
            ondelete="RESTRICT",
        ),
        # `RESTRICT`: the administrator who chose a folder cannot be removed out
        # from under the record of the choice.
        sa.ForeignKeyConstraint(
            ["selected_by_account_id"],
            ["platform_accounts.id"],
            name="fk_snapshot_folder_selections_selected_by_account_id_accounts",
            ondelete="RESTRICT",
        ),
        # One live selection per snapshot. A second row would be a second answer
        # to "which folder is selected", which is the question R-42 asks.
        sa.UniqueConstraint(
            "snapshot_id", name="uq_snapshot_folder_selections_snapshot"
        ),
        sa.CheckConstraint("length(trim(folder_id)) > 0", name="folder_id_not_blank"),
        sa.CheckConstraint(
            "length(trim(folder_path)) > 0", name="folder_path_not_blank"
        ),
        sa.CheckConstraint("version > 0", name="version_positive"),
    )

    op.create_table(
        "reconciliation_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("kind", sa.String(10), nullable=False),
        sa.Column("state", sa.String(12), nullable=False),
        sa.Column("snapshot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("folder_id", sa.String(64), nullable=False),
        sa.Column("profile_version", sa.String(64), nullable=False),
        sa.Column("scope_fingerprint", sa.LargeBinary(), nullable=False),
        sa.Column(
            "requested_by_account_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("requested_capability", sa.String(30), nullable=False),
        sa.Column("request_key", sa.String(255), nullable=False),
        sa.Column("parent_job_id", postgresql.UUID(as_uuid=True)),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("lease_owner", sa.String(120)),
        sa.Column("lease_expires_at", sa.DateTime(timezone=True)),
        sa.Column("heartbeat_at", sa.DateTime(timezone=True)),
        sa.Column(
            "queued_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("cancel_requested_at", sa.DateTime(timezone=True)),
        sa.Column("stale_reason", sa.String(40)),
        sa.Column("failure_code", sa.String(40)),
        sa.Column("result_id", postgresql.UUID(as_uuid=True)),
        sa.Column("correlation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.ForeignKeyConstraint(
            ["snapshot_id"],
            ["foundry_snapshots.id"],
            name="fk_reconciliation_jobs_snapshot_id_foundry_snapshots",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["requested_by_account_id"],
            ["platform_accounts.id"],
            name="fk_reconciliation_jobs_requested_by_account_id_accounts",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["parent_job_id"],
            ["reconciliation_jobs.id"],
            name="fk_reconciliation_jobs_parent_job_id_reconciliation_jobs",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("request_key", name="uq_reconciliation_jobs_request_key"),
        sa.CheckConstraint("kind IN ('preview', 'apply')", name="kind"),
        sa.CheckConstraint(
            "state IN ('queued', 'running', 'completed', 'stale', 'failed', 'cancelled')",
            name="state",
        ),
        sa.CheckConstraint(
            "(state = 'running') = (lease_owner IS NOT NULL)",
            name="running_holds_a_lease",
        ),
        sa.CheckConstraint(
            "(state IN ('completed', 'stale', 'failed', 'cancelled')) "
            "= (finished_at IS NOT NULL)",
            name="terminal_states_have_finished",
        ),
        sa.CheckConstraint(
            "(state = 'completed') = (result_id IS NOT NULL)",
            name="completed_has_a_result",
        ),
        sa.CheckConstraint(
            "(state = 'failed') = (failure_code IS NOT NULL)", name="failed_states_why"
        ),
        sa.CheckConstraint(
            "(state = 'stale') = (stale_reason IS NOT NULL)", name="stale_states_why"
        ),
        sa.CheckConstraint("attempts >= 0 AND attempts <= 3", name="attempts_within_n43"),
        sa.CheckConstraint(
            "state <> 'queued' OR attempts < 3", name="queued_can_be_claimed"
        ),
        sa.CheckConstraint(
            "length(scope_fingerprint) = 32", name="scope_fingerprint_sha256"
        ),
        sa.CheckConstraint("length(trim(request_key)) > 0", name="request_key_not_blank"),
        sa.CheckConstraint("version > 0", name="version_positive"),
        sa.CheckConstraint(
            "(kind = 'apply') OR (parent_job_id IS NULL)",
            name="only_an_apply_has_a_parent",
        ),
    )

    op.create_table(
        "reconciliation_job_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("summary", postgresql.JSONB(), nullable=False),
        sa.Column("blocked_entries", postgresql.JSONB(), nullable=False),
        sa.Column(
            "produced_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("expires_at > produced_at", name="expiry_after_production"),
    )

    # The cycle, closed once both ends exist.
    op.create_foreign_key(
        "fk_reconciliation_job_results_job_id_reconciliation_jobs",
        "reconciliation_job_results",
        "reconciliation_jobs",
        ["job_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_reconciliation_jobs_result_id_reconciliation_job_results",
        "reconciliation_jobs",
        "reconciliation_job_results",
        ["result_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    # The claim path, and nothing else, uses this.
    op.create_index(
        "ix_reconciliation_jobs_claimable",
        "reconciliation_jobs",
        ["queued_at"],
        postgresql_where=sa.text("state = 'queued'"),
    )
    op.create_index(
        "uq_reconciliation_jobs_one_live_apply",
        "reconciliation_jobs",
        ["snapshot_id", "folder_id", "profile_version"],
        unique=True,
        postgresql_where=sa.text("kind = 'apply' AND state IN ('queued', 'running')"),
    )
    op.create_index(
        "ix_reconciliation_jobs_snapshot",
        "reconciliation_jobs",
        ["snapshot_id", sa.text("queued_at DESC")],
    )
    # The reaper's sweep, and the `expired_leases` health check that watches it.
    op.create_index(
        "ix_reconciliation_jobs_expired_leases",
        "reconciliation_jobs",
        ["lease_expires_at"],
        postgresql_where=sa.text("state = 'running'"),
    )
    op.create_index(
        "ix_reconciliation_job_results_job", "reconciliation_job_results", ["job_id"]
    )
    # N-24's retention sweep reads this.
    op.create_index(
        "ix_reconciliation_job_results_expiry",
        "reconciliation_job_results",
        ["expires_at"],
    )


def downgrade() -> None:
    # The cycle first, so neither table depends on the other while it is dropped.
    op.drop_constraint(
        "fk_reconciliation_jobs_result_id_reconciliation_job_results",
        "reconciliation_jobs",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_reconciliation_job_results_job_id_reconciliation_jobs",
        "reconciliation_job_results",
        type_="foreignkey",
    )
    op.drop_index(
        "ix_reconciliation_job_results_expiry", table_name="reconciliation_job_results"
    )
    op.drop_index(
        "ix_reconciliation_job_results_job", table_name="reconciliation_job_results"
    )
    op.drop_table("reconciliation_job_results")
    op.drop_index(
        "ix_reconciliation_jobs_expired_leases", table_name="reconciliation_jobs"
    )
    op.drop_index("ix_reconciliation_jobs_snapshot", table_name="reconciliation_jobs")
    op.drop_index(
        "uq_reconciliation_jobs_one_live_apply", table_name="reconciliation_jobs"
    )
    op.drop_index("ix_reconciliation_jobs_claimable", table_name="reconciliation_jobs")
    op.drop_table("reconciliation_jobs")
    op.drop_table("snapshot_folder_selections")
