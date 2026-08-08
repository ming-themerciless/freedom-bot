"""Record how a snapshot artifact arrived, and who presented it.

Until now every artifact reached the Manager the same way: an operator placed a
file on the host and ran `tools.bootstrap_manager` as themselves.
`foundry_snapshots.received_by_discord_user_id` was enough provenance for that,
and it is nullable because the supervised bootstrap has no interactive user.

The Foundry module introduces a second route with a different chain of custody:
a **service principal** presents a submit-only credential over HTTPS and there
is no acting Discord user at all. A row written on that path and left with a
null `received_by_discord_user_id` would name nobody, which plan §6.4 does not
permit — "the snapshot record stores its checksum, provenance, triggering
Discord user or supervised-bootstrap actor, import time, selected folder,
outcome, and an audit correlation ID".

So this revision adds:

- `received_via` — `operator` or `foundry_module`, defaulted to `operator`
  because that is truthfully how every existing row arrived; and
- `submitted_by_principal` — the configured principal id, on the module path.

A check constraint makes the pair consistent in both directions: a module
submission must name its principal, and an operator-supplied artifact must not,
so a row can never assert a chain of custody it did not have.

## Why a follow-on revision

`0002` and `0003` are in history and under independent review, and
`.agents/AGENTS.md` requires that an applied migration is never edited. This is
an ordinary additive, reversible revision.

## Why the server default is safe here, unlike `0003`

`0003` refused to backfill because no truthful value existed for a row written
before its binding existed. The opposite is true here: every row written before
this revision *did* arrive by the operator path, so `operator` is a statement of
fact rather than an invented one.

## `foundry_snapshots` is append-only

A trigger from `0002` rejects `UPDATE` and `DELETE` on this table even for the
schema owner, and the runtime role holds `SELECT, INSERT` only. Neither affects
`ALTER TABLE`: adding a column is DDL by the schema owner, which is the
deliberate, visible act the append-only rule is meant to require. No runtime
grant changes, because no table is created or dropped.

Revision ID: 0004
Revises: 0003
Create Date: 2026-08-04
"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "foundry_snapshots",
        sa.Column(
            "received_via",
            sa.String(20),
            nullable=False,
            server_default="operator",
        ),
    )
    op.add_column(
        "foundry_snapshots",
        sa.Column("submitted_by_principal", sa.String(64), nullable=True),
    )
    op.create_check_constraint(
        op.f("ck_foundry_snapshots_received_via"),
        "foundry_snapshots",
        "received_via IN ('operator', 'foundry_module')",
    )
    op.create_check_constraint(
        op.f("ck_foundry_snapshots_module_submission_names_its_principal"),
        "foundry_snapshots",
        "(received_via = 'foundry_module') = (submitted_by_principal IS NOT NULL)",
    )


def downgrade() -> None:
    """Reverse the revision.

    Downgrading discards the distinction between an operator-supplied artifact
    and a module submission, including which principal presented it. That is
    provenance, so take a backup first: `alembic upgrade 0004` afterwards
    restores the columns but not their values.
    """
    op.drop_constraint(
        op.f("ck_foundry_snapshots_module_submission_names_its_principal"),
        "foundry_snapshots",
        type_="check",
    )
    op.drop_constraint(
        op.f("ck_foundry_snapshots_received_via"),
        "foundry_snapshots",
        type_="check",
    )
    op.drop_column("foundry_snapshots", "submitted_by_principal")
    op.drop_column("foundry_snapshots", "received_via")
