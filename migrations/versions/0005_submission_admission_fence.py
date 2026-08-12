"""Make "this credential may still write" a durable fact the database enforces.

Review finding B-1 survived nine remediations because every one of them tried to
establish *quiescence by observation*: no process, no socket, no backend in
`pg_stat_activity`, an unmoved commit watermark, an empty lock queue. None of
those can exclude a request that has been **accepted** but has not yet reached
the resource being observed. C-23's drain read moved that window rather than
closing it: a request paused before its first conflicting statement queues behind
the drain, is invisible to the drain's own reading, and commits immediately
afterwards — after a miss has been recorded and a fresh export authorized.

So this revision stops observing and starts **revoking**.

## What it adds

`submission_admissions` — one row per submission credential, holding the
generation that credential may write under and whether it is still open.

`idempotency_keys.admission_id` — a foreign key naming the admission a receipt
was earned under. Every successful submission writes exactly one row here, on
the new-bytes path and on the duplicate-bytes path alike, so it is the single
choke point an acceptance cannot avoid.

## Why a foreign key is the concurrency rule, and not merely provenance

Checking a foreign key takes a row-level `KEY SHARE` lock on the referenced
admission row. Closure takes `FOR UPDATE` on the same row. Those two conflict, so
a closure and an acceptance can never interleave — one strictly precedes the
other:

- **acceptance first** — it holds `KEY SHARE`, the closure waits, the acceptance
  commits, and the closure then runs against a database that already contains it.
  Settlement sees the submission. There is no miss to record.
- **closure first** — it holds `FOR UPDATE`, the acceptance's `INSERT` waits. Once
  the closure commits, the `INSERT` is granted, and the submission's **state
  re-read, taken after that `INSERT` and inside the same transaction**, returns
  `closed`. The transaction rolls back and the caller gets a typed refusal.

That second case is the exact sequence the reviewer described, and the re-read is
what answers it: it does not matter where the old request was paused, because the
thing it is checked against is its own credential's admission and it cannot be
silently upgraded to a newer one.

**A plain `UPDATE … SET state = 'closed'` is not a closure.** An update of a
non-key column takes `FOR NO KEY UPDATE`, which does **not** conflict with the
foreign key's `KEY SHARE`, so it would sail past a waiting acceptance and fence
nothing while looking exactly like a fence. Closure must take `FOR UPDATE`
explicitly first. That was measured against this host's PostgreSQL 16.14, not
reasoned about, and `tests/test_submission_admission_postgresql.py` keeps the
measurement.

## Why `principal_id` is unique for all time

A lock delays a request; it does not revoke its authority. What revokes authority
is that the credential's admission is closed **and cannot be replaced**. The
unique constraint is what makes that structural: there is at most one admission
row per principal id, ever, so no operator, script or later migration can open a
second one for a credential whose first was closed. Recovery therefore issues a
*new* credential (operations §5.2) and opens a new admission naming it. An old
request cannot present a credential it was never sent with.

## Why the state transition is a trigger

`open` → `closed`, once, and nothing else: no reopen, no `DELETE`, no rewriting
of who opened it or when. A reopened admission is indistinguishable afterwards
from one that was never closed, which would make every settlement record
unfalsifiable. The trigger applies to the schema owner too, exactly as the
append-only triggers from 0002 do, so exceptional recovery is a deliberate,
recorded `ALTER TABLE … DISABLE TRIGGER` outside the application.

## Backfill

Receipts written before this revision were accepted under no admission at all.
Rather than invent one, the upgrade creates a single **closed** generation 0 row
under the reserved principal `<pre-admission-fence>` and points them at it. The
name is deliberately not a legal service principal id (`ServicePrincipal` refuses
the angle brackets), so no credential can ever authenticate as it and nothing can
be accepted under it. On a database with no such receipts, no row is created.

Revision ID: 0005
Revises: 0004
Create Date: 2026-08-12
"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

#: Kept in step with `application.foundry.submission.SUBMISSION_SCOPE`. Repeated
#: as a literal because a migration must keep meaning what it meant when it ran,
#: and importing the constant would let a later rename rewrite history.
SUBMISSION_SCOPE = "foundry.snapshot.submission"

#: The principal the backfilled generation 0 is attributed to. Not a legal
#: service principal id, on purpose — see the module docstring.
PRE_FENCE_PRINCIPAL = "<pre-admission-fence>"


def upgrade() -> None:
    op.create_table(
        "submission_admissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("generation", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column("principal_id", sa.String(64), nullable=False),
        sa.Column("state", sa.String(16), nullable=False),
        sa.Column(
            "opened_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("opened_by", sa.String(120), nullable=False),
        sa.Column("open_reason", sa.Text(), nullable=False),
        sa.Column("correlation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_by", sa.String(120), nullable=True),
        sa.Column("close_reason", sa.Text(), nullable=True),
        sa.Column(
            "closed_correlation_id", postgresql.UUID(as_uuid=True), nullable=True
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_submission_admissions")),
        sa.UniqueConstraint("generation", name="uq_submission_admissions_generation"),
        sa.UniqueConstraint(
            "principal_id", name="uq_submission_admissions_principal_id"
        ),
        sa.CheckConstraint(
            "state IN ('open', 'closed')", name=op.f("ck_submission_admissions_state")
        ),
        sa.CheckConstraint(
            "generation >= 0",
            name=op.f("ck_submission_admissions_generation_not_negative"),
        ),
        sa.CheckConstraint(
            "(state = 'closed') = (closed_at IS NOT NULL)",
            name=op.f("ck_submission_admissions_closed_state_is_dated"),
        ),
        sa.CheckConstraint(
            "(state = 'closed') = (closed_by IS NOT NULL)",
            name=op.f("ck_submission_admissions_closed_state_names_its_operator"),
        ),
        sa.CheckConstraint(
            "(state = 'closed') = (close_reason IS NOT NULL)",
            name=op.f("ck_submission_admissions_closed_state_gives_a_reason"),
        ),
        sa.CheckConstraint(
            "(state = 'closed') = (closed_correlation_id IS NOT NULL)",
            name=op.f("ck_submission_admissions_closed_state_is_correlated"),
        ),
    )

    # One direction, once. Every other transition — reopening, re-attributing the
    # opening, changing which principal the generation belongs to — is refused
    # here rather than left to the application, because the application is not
    # the only thing with a connection.
    op.execute(
        """
        CREATE OR REPLACE FUNCTION reject_admission_reversal() RETURNS trigger AS $$
        BEGIN
            IF TG_OP = 'DELETE' THEN
                RAISE EXCEPTION
                    'submission_admissions: DELETE is refused. An admission that '
                    'can be removed is an admission that can be reopened, and a '
                    'reopened generation cannot be told apart from one that was '
                    'never closed.'
                    USING ERRCODE = 'restrict_violation';
            END IF;

            IF NEW.id IS DISTINCT FROM OLD.id
                OR NEW.generation IS DISTINCT FROM OLD.generation
                OR NEW.principal_id IS DISTINCT FROM OLD.principal_id
                OR NEW.opened_at IS DISTINCT FROM OLD.opened_at
                OR NEW.opened_by IS DISTINCT FROM OLD.opened_by
                OR NEW.open_reason IS DISTINCT FROM OLD.open_reason
                OR NEW.correlation_id IS DISTINCT FROM OLD.correlation_id
            THEN
                RAISE EXCEPTION
                    'submission_admissions: the identity and opening of an '
                    'admission are immutable. Only the transition to closed may '
                    'be written.'
                    USING ERRCODE = 'restrict_violation';
            END IF;

            IF NOT (OLD.state = 'open' AND NEW.state = 'closed') THEN
                RAISE EXCEPTION
                    'submission_admissions: % -> % is refused. An admission moves '
                    'from open to closed once and never back.',
                    OLD.state, NEW.state
                    USING ERRCODE = 'restrict_violation';
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER submission_admissions_monotone
        BEFORE UPDATE OR DELETE ON submission_admissions
        FOR EACH ROW EXECUTE FUNCTION reject_admission_reversal();
        """
    )

    op.add_column(
        "idempotency_keys",
        sa.Column("admission_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_idempotency_keys_admission_id",
        "idempotency_keys",
        "submission_admissions",
        ["admission_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    # Backfill before the check constraint, so the constraint is validated
    # against a table that already satisfies it rather than added as NOT VALID.
    #
    # Written as two statements that read nothing and decide nothing in Python.
    # `alembic upgrade --sql` emits a reviewable script without a connection, and
    # a backfill expressed as "query, then branch" would either fail to generate
    # or generate a script that silently skipped the rows — after which the check
    # constraint below would refuse the database it produced. Both statements are
    # no-ops on a fresh database, which is exactly what they should be.
    op.execute(
        sa.text(
            f"""
            INSERT INTO submission_admissions (
                id, generation, principal_id, state,
                opened_at, opened_by, open_reason, correlation_id,
                closed_at, closed_by, close_reason, closed_correlation_id
            )
            SELECT
                gen_random_uuid(), 0, '{PRE_FENCE_PRINCIPAL}', 'closed',
                now(), 'migration 0005',
                'Generation 0 stands for the receipts written before the '
                'admission fence existed. It is created closed and its principal '
                'is not a legal service principal id, so nothing can ever be '
                'accepted under it.',
                gen_random_uuid(),
                now(), 'migration 0005',
                'Closed at creation; this generation was never open.',
                gen_random_uuid()
            WHERE EXISTS (
                SELECT 1 FROM idempotency_keys
                WHERE scope = '{SUBMISSION_SCOPE}' AND admission_id IS NULL
            )
            """
        )
    )
    op.execute(
        sa.text(
            f"""
            UPDATE idempotency_keys SET admission_id = (
                SELECT id FROM submission_admissions
                WHERE principal_id = '{PRE_FENCE_PRINCIPAL}'
            )
            WHERE scope = '{SUBMISSION_SCOPE}' AND admission_id IS NULL
            """
        )
    )

    op.create_check_constraint(
        op.f("ck_idempotency_keys_submission_names_its_admission"),
        "idempotency_keys",
        "scope <> 'foundry.snapshot.submission' OR admission_id IS NOT NULL",
    )


def downgrade() -> None:
    """Reverse the revision, and take a backup first.

    Downgrading discards **which admission generation each accepted submission
    was written under**, and every open/close record with it. `alembic upgrade
    0005` afterwards recreates the table and the column but not their values, and
    the backfill will then attribute every surviving receipt to a fresh
    generation 0 rather than to the generation that actually admitted it.

    It also removes the fence itself. A deployment left downgraded accepts
    submissions from any authenticated credential regardless of any settlement in
    progress, which is the pre-C-24 behaviour that finding B-1 is open against.
    Downgrade only to recover from a failed upgrade, and re-upgrade before the
    endpoint serves again.
    """
    op.drop_constraint(
        op.f("ck_idempotency_keys_submission_names_its_admission"),
        "idempotency_keys",
        type_="check",
    )
    op.drop_constraint(
        "fk_idempotency_keys_admission_id", "idempotency_keys", type_="foreignkey"
    )
    op.drop_column("idempotency_keys", "admission_id")

    op.execute(
        "DROP TRIGGER IF EXISTS submission_admissions_monotone ON submission_admissions;"
    )
    op.execute("DROP FUNCTION IF EXISTS reject_admission_reversal();")
    op.drop_table("submission_admissions")
