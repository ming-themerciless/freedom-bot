"""Bind a request key to the operation it was spent on.

`snapshot_imports.request_key` identifies an apply *attempt*, so a retry returns
the original result instead of applying twice. It does not identify the
*operation*: independent review of `ba42467` found (B-1, blocking) that a
different artifact, folder, profile or exporter could be presented under an
already-spent key and receive the original import's identity and correlation ID
alongside the new checksum and a caller-supplied report — a receipt describing
no single operation.

This revision adds `operation_digest`, the SHA-256 of the immutable bound inputs
of the operation the key was first spent on, so the application can tell a retry
from a reuse by comparing what the caller presents against what was recorded.
The separate applied-input rule — one applied row per (snapshot, folder, profile
version) — is untouched and still holds.

## Why a follow-on revision and not a replacement of `0002`

`0002` explains that it *replaced* an earlier revision in place, on the grounds
that the earlier one "was never committed and never applied to a durable
environment — only to the disposable `freedom_test` database". Half of that
reasoning no longer holds for `0002` itself: it was committed in `ba42467` and is
part of the history now under independent review. The accepted remediation plan
allows replacement in place "only while it is true that the former revision
existed solely in disposable `freedom_test`", which was a statement about that
earlier revision, not a standing licence.

So `0002` is left exactly as reviewed and this is an ordinary additive,
reversible migration — which is also what `.agents/AGENTS.md` asks for
("Never edit an applied migration", "commit every schema migration").

## Why the column can be `NOT NULL` without a backfill

No durable environment has ever run `0002`; the only database that has is the
disposable `freedom_test`, which every test run migrates from empty. The
`ALTER TABLE ... SET NOT NULL` below is therefore expected to run against an
empty table. Should it ever meet rows, it fails loudly rather than inventing a
digest: a fabricated digest in an append-only table would assert that a past
import was bound to inputs nobody verified, and a failed migration is a far
better outcome than that.

Revision ID: 0003
Revises: 0002
Create Date: 2026-08-03
"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "snapshot_imports",
        sa.Column("operation_digest", sa.String(64), nullable=True),
    )
    # Deliberately no backfill. See the module docstring: there is no truthful
    # value for a row written before the binding existed, and the only database
    # that holds such rows is disposable.
    op.alter_column("snapshot_imports", "operation_digest", nullable=False)
    op.create_check_constraint(
        op.f("ck_snapshot_imports_operation_digest_sha256_hex"),
        "snapshot_imports",
        "operation_digest ~ '^[0-9a-f]{64}$'",
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("ck_snapshot_imports_operation_digest_sha256_hex"),
        "snapshot_imports",
        type_="check",
    )
    op.drop_column("snapshot_imports", "operation_digest")
