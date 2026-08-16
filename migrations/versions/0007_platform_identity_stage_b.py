"""Stage B of the identity migration: both invariant sets, enforced at once.

`docs/contracts/phase-3-identity-migration-contract.md` §3, stage B. It makes the
account columns `NOT NULL` and creates the account-keyed partial unique indexes
**alongside** the Discord-keyed ones from migration 0001.

## Why both index sets exist simultaneously

This is what makes the cutover reversible rather than merely reversible-sounding.
While both sets stand, an insert that violated *either* invariant is rejected
loudly — so if the stage A mapping were wrong, the database says so before any
user sees a wrong authorization, and a downgrade drops indexes that never stopped
working rather than reconstructing a key.

The three existing invariants and their account-keyed counterparts:

| Existing (0001) | Added here |
|---|---|
| `uq_character_access_one_active_link (character_id, discord_user_id)` | `(character_id, platform_account_id)` |
| `uq_character_access_one_active_owner (character_id)` | **unchanged** — it never referenced the user column (OD-37) |
| `uq_character_access_one_active_default_per_user (discord_user_id)` | `(platform_account_id)` |

`uq_character_access_one_active_owner` gets no counterpart because it has no user
column to re-key. Stating that is the point: a reader counting "two new indexes
for three old ones" should find the answer here rather than infer an omission.

## Foreign keys

Stage A already added both account foreign keys beside the columns they
constrain, rather than deferring them to this revision as the contract's stage
table sketches. The reversal boundary is unchanged — stage A drops them with the
columns — and a nullable column with its foreign key already in place cannot hold
an unresolvable account id even for the duration of one stage.

Revision ID: 0007
Revises: 0006
Create Date: 2026-08-14
"""
from __future__ import annotations

from typing import Sequence

import sqlalchemy as sa
from alembic import context, op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


OFFLINE_PRECONDITION_NOTICE = """
-- ---------------------------------------------------------------------------
-- REVISION 0007 -- THE PRECONDITION COUNT IS NOT IN THIS SCRIPT
--
-- Online, this revision first counts `character_access` rows whose account
-- columns are still null and refuses with that count rather than letting
-- `SET NOT NULL` fail with a message that names a column instead of a cause.
-- Offline mode never connects, so the count cannot run.
--
-- The `SET NOT NULL` statements below still refuse -- PostgreSQL rejects them
-- if any row is null -- so the migration cannot half-apply. What is lost is the
-- explanation, not the protection. If they fail, revision 0006's backfill has
-- not run online against this database; it is idempotent, so run it.
-- ---------------------------------------------------------------------------
"""


def upgrade() -> None:
    if context.is_offline_mode():
        op.execute(sa.text(OFFLINE_PRECONDITION_NOTICE))
    else:
        connection = op.get_bind()
        connection.execute(sa.text("SET LOCAL lock_timeout = '5s'"))

        # Refuse rather than let `SET NOT NULL` fail with a constraint message
        # that names a column instead of a cause. Stage A's control totals T4/T5
        # already proved this, and a database that reached stage B with
        # unresolved rows had something happen between the stages that an
        # operator needs told plainly.
        unresolved = connection.execute(
            sa.text(
                """
                SELECT count(*) FROM character_access
                 WHERE platform_account_id IS NULL OR granted_by_account_id IS NULL
                """
            )
        ).scalar_one()
        if unresolved:
            raise RuntimeError(
                f"Stage B refused: {unresolved} character_access row(s) still have "
                "no resolved platform account. Re-run stage A's backfill (it is "
                "idempotent) and check control totals T4-T6 before continuing."
            )

    op.alter_column("character_access", "platform_account_id", nullable=False)
    op.alter_column("character_access", "granted_by_account_id", nullable=False)

    op.create_index(
        "uq_character_access_one_active_link_account",
        "character_access",
        ["character_id", "platform_account_id"],
        unique=True,
        postgresql_where=sa.text("active"),
    )
    op.create_index(
        "uq_character_access_one_active_default_per_account",
        "character_access",
        ["platform_account_id"],
        unique=True,
        postgresql_where=sa.text("active AND default_character"),
    )
    # R-20 reads "the characters this account may reach" on every member page
    # load, and it is the only unindexed access path the account key introduces.
    op.create_index(
        "ix_character_access_account_active",
        "character_access",
        ["platform_account_id"],
        postgresql_where=sa.text("active"),
    )


def downgrade() -> None:
    op.drop_index("ix_character_access_account_active", table_name="character_access")
    op.drop_index(
        "uq_character_access_one_active_default_per_account", table_name="character_access"
    )
    op.drop_index("uq_character_access_one_active_link_account", table_name="character_access")
    op.alter_column("character_access", "granted_by_account_id", nullable=True)
    op.alter_column("character_access", "platform_account_id", nullable=True)
