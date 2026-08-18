"""P3.2: durable Sheet-era identity-evidence proposals (migration contract M-2).

The only schema P3.2 adds. Everything else it needs — `platform_accounts`,
`external_identities`, `character_access` on its account key, the
account-keyed partial unique indexes, `role_capability_mappings` and its
append-only event log — was created and cut over by revisions 0006 to 0009, and
this revision changes none of it.

## Three tables where the accepted schema names one

`docs/contracts/phase-3-logical-schema.md` §11 gives `identity_link_proposals` a
one-line row: UUID primary key, `character` foreign key `CASCADE`, uniqueness on
`(run_id, character_id)`, written by C-04, read by R-28, retained 90 days after
the run, holding Sheet names as personal data. It does not give the column list
that §4-§10 give the tables P3.1 built, so the decomposition is this package's
to make. Two requirements in the migration contract decide it, and both point
away from a single flat row:

1. **§7.4's source-side control totals.** `source_characters` and
   `source_players` are facts about a *run*. `source_players` cannot hang off a
   proposal at all — a player row with no character produces no proposal — so
   there is nowhere on a proposal for it to live. `identity_migration_runs`
   is that place, and it also carries the run's immutable bucket counts, which
   are the right-hand side of the second balance. Counting those live from the
   proposal rows would make the balance true by construction, because a Council
   confirmation changes a row's `resolution` in place.

2. **§7.6's durable ambiguity.** An ambiguous proposal must persist as an
   explicit record naming *every* candidate and choosing none. Implementation
   plan §7.3.1 prohibits delimited text, JSON/JSONB collections and PostgreSQL
   arrays for multi-valued facts and prescribes typed foreign-keyed child rows
   instead, and TC-STRUCT-03 asserts that this schema grows no third JSONB
   column. `identity_link_proposal_candidates` is therefore the compliant
   representation rather than a preference; the alternatives are the ones the
   plan names as prohibited.

The addition is recorded in the P3.2 submission rather than made quietly.

## Two lifecycle positions, and the schema keeps them apart

Migration contract §7.2's pipeline has two steps and this schema has a column
group for each:

| Step | Written by | Columns |
|---|---|---|
| C-04 produces the evidence | `python -m tools.identity_migration --dry-run --player-tab Players` | `identity_migration_runs.*`, `identity_link_proposals` evidence and `resolution` |
| Council decides one proposal, and a confirmation **is** the link | R-29 / R-30 | `decided_at`, `decided_by_account_id`, `decision_reason`, `granted_access_id` |

**Every row of `identity_migration_runs` is a C-04 evidence run.** `dry_run` is
`CHECK`-ed `true` rather than merely defaulted to it, so "this table holds
evidence runs" is a fact about the table and not about which code path happened
to insert the row.

**There is no apply state here** (change-log entry C-P3.2-A, OD-46). An earlier
draft of this revision carried `applied_at`, `apply_outcome` and an
`apply_correlation_id` on the run, for a withdrawn command `C-05 --apply` that
materialized confirmed proposals afterwards. The maintainer ruled that a Guild
Council confirmation activates the link immediately, so there is nothing between
`confirmed` and the access row and no state to record about the gap. The columns
are removed rather than left nullable and unused: a column no writer sets is a
column a later reader will interpret.

This revision is uncommitted in the P3.2 worktree, so it is **rewritten** to
describe the approved final schema rather than amended by an eleventh revision.
No applied migration (0001–0009) is edited.

## Nothing here can authorize anything by itself

A proposal is evidence. `granted_access_id` is the *only* link between this
schema and authorization, and one check constraint —
`ck_identity_link_proposals_a_confirmation_is_a_link` — makes it non-null
**exactly** on a `confirmed` row. So three properties are facts about the table
rather than about the services:

- C-04 writes no `character_access` row: every row it writes is `proposed`,
  `ambiguous` or `unresolved`, and none of those may carry a grant;
- a rejection creates no link: `rejected` may not carry one either; and
- a confirmation is not a promise: a `confirmed` row that named no access row
  would be refused, so the state "decided but not linked" cannot be stored.

`ck_identity_link_proposals_a_decision_states_its_reason` closes the same kind of
gap on the reason (change-log entry C-P3.2-C). R-29 and R-30 both require one and
the application validates it, but the restricted runtime role holds `UPDATE` on
this table, so a rule that lived only in the service would admit a `confirmed`
row with `decision_reason IS NULL` from one direct statement. Together with
`ck_identity_link_proposals_decision_reason_not_blank`, a decided row carries a
non-null, non-blank trimmed reason and an outstanding one carries none at all.

The row that confers reach is written by the one service R-25 uses,
`CharacterAccessService.grant()`, in the same transaction that records the
proposal's confirmed transition. `RESTRICT` on the foreign key means the access
row cannot be removed out from under the decision that created it.

`resolution` admits exactly VM-10's five values. `already_linked` is a run-level
count and deliberately not a resolution: there is no proposal to make when the
character already has an active access row for that account.

## Reversibility and retention

`downgrade()` drops the three tables. They hold evidence and decisions, never
authorization: a `character_access` row created by a confirmation is untouched by
the downgrade and keeps its own grantor, reason, timestamps and correlation id,
so downgrading loses the record of *which proposal* prompted a link and never the
link itself or its audit events. What that costs, stated where an operator will
read it: after a downgrade the Council decisions are gone and cannot be recomputed
from the surviving access rows, so re-upgrading and re-running C-04 produces a
fresh run whose proposals must be decided again. The already-created links are
then counted into `already_linked` rather than re-proposed, so nothing is granted
twice. Rolling back to the legacy linkage-evidence workflow needs nothing undone
in Google Sheets, because nothing was ever done to it (migration contract §7.5).

Retention is 90 days after the run, applied by
`IdentityProposalRepository.purge_runs_older_than`, which deletes runs and
cascades to their proposals and candidates.

Revision ID: 0010
Revises: 0009
Create Date: 2026-08-16
"""
from __future__ import annotations

from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# Every `CheckConstraint` below names itself in the **short** form the project's
# naming convention expects (`adapters/database/metadata.py`:
# `ck_%(table_name)s_%(constraint_name)s`). Spelling the full name here instead
# produces `ck_identity_migration_runs_ck_identity_migration_runs_b_642c` — the
# prefix twice and then a hash, because the convention applies to whatever it is
# given and PostgreSQL truncates at 63 characters. The result is a constraint
# whose name disagrees with `adapters/database/tables.py`'s declaration of the
# same table and which no test can identify by name.

revision: str = "0010"
down_revision: str | None = "0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "identity_migration_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "produced_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "dry_run", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        # A label for the source ranges. **Never** the spreadsheet id and never a
        # credential: an operator reading this column needs to know which ranges
        # were read, and nothing in it should be worth stealing.
        sa.Column("source_label", sa.String(120), nullable=False),
        sa.Column("profile_version", sa.String(64), nullable=False),
        sa.Column("source_characters", sa.Integer(), nullable=False),
        sa.Column("source_players", sa.Integer(), nullable=False),
        sa.Column("already_linked", sa.Integer(), nullable=False),
        sa.Column("proposed", sa.Integer(), nullable=False),
        sa.Column("ambiguous", sa.Integer(), nullable=False),
        sa.Column("unresolved", sa.Integer(), nullable=False),
        sa.Column("correlation_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Every row here is a C-04 evidence run, stated where it cannot be
        # bypassed by a writer who believes otherwise.
        sa.CheckConstraint("dry_run", name="run_is_a_c04_evidence_run"),
        sa.CheckConstraint(
            "length(trim(source_label)) > 0",
            name="source_label_not_blank",
        ),
        sa.CheckConstraint(
            "length(trim(profile_version)) > 0",
            name="profile_version_not_blank",
        ),
        sa.CheckConstraint(
            "source_characters >= 0",
            name="source_characters_non_negative",
        ),
        sa.CheckConstraint(
            "source_players >= 0",
            name="source_players_non_negative",
        ),
        sa.CheckConstraint(
            "already_linked >= 0 AND proposed >= 0 AND ambiguous >= 0 AND unresolved >= 0",
            name="buckets_non_negative",
        ),
        # §7.4's first balance, enforced by PostgreSQL. An unbalanced report is a
        # refusal to proceed, not a warning (plan §0.5), and the cheapest place
        # to make that true for every writer is here.
        sa.CheckConstraint(
            "already_linked + proposed + ambiguous + unresolved = source_characters",
            name="buckets_balance_against_source",
        ),
    )

    op.create_table(
        "identity_link_proposals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("character_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sheet_player_name", sa.Text(), nullable=False),
        sa.Column("sheet_discord_name", sa.Text()),
        sa.Column(
            "active_dm", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column("proposed_subject", sa.String(255)),
        sa.Column("resolution", sa.String(20), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True)),
        sa.Column("decided_by_account_id", postgresql.UUID(as_uuid=True)),
        sa.Column("decision_reason", sa.Text()),
        # The `character_access` row this confirmation created. Non-null exactly
        # on a `confirmed` row — see the constraint below — and written in the
        # same statement as the decision, so no writer can pass through a state
        # where a confirmation exists without its link.
        sa.Column("granted_access_id", postgresql.UUID(as_uuid=True)),
        sa.Column("audit_correlation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["run_id"],
            ["identity_migration_runs.id"],
            name="fk_identity_link_proposals_run_id_identity_migration_runs",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["character_id"],
            ["characters.id"],
            name="fk_identity_link_proposals_character_id_characters",
            ondelete="CASCADE",
        ),
        # `RESTRICT` on both: a decision names a person and a grant, and neither
        # may be removed out from under the record of the decision.
        sa.ForeignKeyConstraint(
            ["decided_by_account_id"],
            ["platform_accounts.id"],
            name="fk_identity_link_proposals_decided_by_account_id_accounts",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["granted_access_id"],
            ["character_access.id"],
            name="fk_identity_link_proposals_granted_access_id_character_access",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "run_id", "character_id", name="uq_identity_link_proposals_run_character"
        ),
        sa.CheckConstraint(
            "resolution IN ('proposed', 'ambiguous', 'unresolved', 'confirmed', 'rejected')",
            name="resolution",
        ),
        sa.CheckConstraint(
            "length(trim(sheet_player_name)) > 0",
            name="player_name_not_blank",
        ),
        # A resolved snowflake is exactly what `proposed` and `confirmed` mean.
        # An `ambiguous` or `unresolved` row carrying one would be a choice the
        # resolver refused to make, appearing anyway.
        sa.CheckConstraint(
            "(resolution IN ('proposed', 'confirmed')) = (proposed_subject IS NOT NULL)",
            name="resolved_subject_matches_resolution",
        ),
        sa.CheckConstraint(
            "(resolution IN ('confirmed', 'rejected')) = (decided_at IS NOT NULL)",
            name="decision_state",
        ),
        sa.CheckConstraint(
            "(decided_at IS NULL) = (decided_by_account_id IS NULL)",
            name="decider",
        ),
        # §7.2's whole pipeline, as one constraint: a confirmation **is** a link
        # and nothing else is. A `proposed`, `ambiguous`, `unresolved` or
        # `rejected` row that carried a grant is refused, and so is a `confirmed`
        # row that named none — so neither "C-04 authorized something" nor "a
        # confirmation was recorded without its access row" is a state this table
        # can hold, whatever a writer believes.
        sa.CheckConstraint(
            "(granted_access_id IS NOT NULL) = (resolution = 'confirmed')",
            name="a_confirmation_is_a_link",
        ),
        sa.CheckConstraint(
            "decision_reason IS NULL OR length(trim(decision_reason)) > 0",
            name="decision_reason_not_blank",
        ),
        # R-29 and R-30 both require a reason, and the restricted runtime role
        # holds `UPDATE` here — so a rule only the service checked would be one
        # direct statement away from a `confirmed` row nobody gave a reason for.
        # With the constraint above: a decided row carries a non-null, non-blank
        # trimmed reason and an outstanding one carries none at all.
        sa.CheckConstraint(
            "(resolution IN ('confirmed', 'rejected')) = (decision_reason IS NOT NULL)",
            name="a_decision_states_its_reason",
        ),
    )
    # R-28 pages one run's proposals in a stable order; the trailing `id` is what
    # makes the cursor total (N-64) rather than merely usually total.
    op.create_index(
        "ix_identity_link_proposals_run",
        "identity_link_proposals",
        ["run_id", "resolution", "id"],
    )
    # "Is this character already proposed anywhere?" — asked by every run.
    op.create_index(
        "ix_identity_link_proposals_character",
        "identity_link_proposals",
        ["character_id"],
    )

    op.create_table(
        "identity_link_proposal_candidates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("proposal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("observed_username", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["proposal_id"],
            ["identity_link_proposals.id"],
            name="fk_identity_link_proposal_candidates_proposal_id_proposals",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "proposal_id",
            "subject",
            name="uq_identity_link_proposal_candidates_subject",
        ),
        sa.CheckConstraint(
            "length(trim(subject)) > 0",
            name="subject_not_blank",
        ),
    )


def downgrade() -> None:
    # Children first. `CASCADE` on the foreign keys would do it, but a downgrade
    # that names what it removes is a downgrade a reviewer can check.
    op.drop_table("identity_link_proposal_candidates")
    op.drop_index("ix_identity_link_proposals_character", table_name="identity_link_proposals")
    op.drop_index("ix_identity_link_proposals_run", table_name="identity_link_proposals")
    op.drop_table("identity_link_proposals")
    op.drop_table("identity_migration_runs")
