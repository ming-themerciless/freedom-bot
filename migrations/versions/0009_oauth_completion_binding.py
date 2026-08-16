"""OD-44: a Discord OAuth session is the durable product of one consumed transaction.

`docs/review/phase-3-p3-1-sm-01-completion-binding-decision.md` §7, approved by
Peter Duscha on 2026-08-14. SM-01 said session creation must run *in the same
database transaction as the consumption*. Schema §9.2.1 makes verifier recovery
and erasure one statement, and PKCE requires that verifier to be presented to
Discord **before** the identity a session attests is known — so the prescribed
transaction would necessarily span a provider network round trip, which the
accepted no-transaction-across-provider-I/O invariant forbids.

The ruling keeps the **outcome** and replaces the **mechanism**: the transaction
row gains a second, one-way step after `consumed`, and the session is made
structurally dependent on it.

    oauth_transactions.completion_claimed_at   -- claimed once, never cleared
    sessions.oauth_transaction_id              -- the authoritative relationship

There is deliberately **no** reverse `oauth_transactions.session_id`. Peter's
refinement in §7 rejected it: a redundant cyclic relationship adds a second value
that can disagree without strengthening the session-side guarantee.

## Why two constraints and not one

They fail in different directions, and neither depends on the route.

- The `CHECK` refuses a `discord_oauth` session that names no transaction, and
  refuses a WebAuthn or recovery-grant session that names one. A future
  completion path that forgot the binding cannot insert its row.
- The unique index refuses a **second** session created by a completion for the
  same transaction. A replayed or forged second completion is already refused by
  the atomic claim; this refuses it again from a different direction.

## The unique index is partial, and that is the one place this revision reads the ruling rather than transcribing it

Read literally, "`sessions.oauth_transaction_id` is `UNIQUE`" and "a check
constraint requires it exactly when `auth_method = 'discord_oauth'`" cannot both
hold while N-08 privilege rotation exists. Rotation creates a **new** session row
for the same login: under the literal pair it would need the transaction id (the
`CHECK`) and could not have it (the `UNIQUE`), so rotating a Discord OAuth
session would become impossible and N-08 would silently stop protecting the main
authentication method.

The predicate `WHERE rotated_from_session_id IS NULL` resolves that by scoping
uniqueness to exactly the set a *completion* can create — sessions that are not
rotations of an earlier one. Both of the ruling's stated purposes survive intact:
every `discord_oauth` session still names its originating transaction directly
(the `CHECK` is transcribed exactly), and a transaction still cannot yield a
second session from a second completion. What the predicate permits is the
rotation chain of one login, which is the thing N-08 exists to produce.

## The rotation chain, which the partial predicate is the other half of

Peter's 2026-08-14 approval of that predicate is **conditional**: the database and
the application must not be able to produce a branching or otherwise invalid
rotation chain. Permitting rotated rows to share a transaction id is only safe if
the set of rows that may do so is exactly one linear chain per login.

So this revision also declares, for `sessions`:

    UNIQUE (rotated_from_session_id) WHERE rotated_from_session_id IS NOT NULL
    FOREIGN KEY (rotated_from_session_id, platform_account_id, auth_method)
        REFERENCES sessions (id, platform_account_id, auth_method)
    FOREIGN KEY (rotated_from_session_id, oauth_transaction_id)
        REFERENCES sessions (id, oauth_transaction_id)

The first refuses a second successor for one predecessor — no branch, and so never
two live descendants of one login. The second and third refuse a rotation that
changes account, authentication method or OAuth binding: the successor's values
must be *the predecessor's own*, found in the row it names.

What PostgreSQL cannot state declaratively is "the predecessor must still be
live", because liveness is a `now()` comparison. That one fact is enforced in the
single locked repository operation `SessionRepository.rotate()`, which selects the
predecessor `FOR UPDATE`, refuses a revoked or already-rotated one, inserts the
successor from the locked row's own values and revokes the predecessor — all in
the caller's one transaction. Two concurrent rotations therefore meet at the row
lock: the winner revokes, the loser re-evaluates after the winner commits, matches
zero rows and is refused. No trigger was added; none was needed.

## The precondition, and the downgrade cost it is the other half of

A `discord_oauth` session that already exists when this revision runs **cannot be
bound**: the transaction that produced it was not recorded, and no value exists
to put in the new column. The restored `CHECK` would then refuse the row, and
`ADD CONSTRAINT` validates existing rows, so the revision would fail on a message
naming a constraint rather than a cause.

So it counts first and refuses with the count, the way revision 0007 refuses an
unresolved `character_access`. The remedy is one statement and it is stated in
the refusal: delete the unbindable session rows. That ends those logins — the
affected people sign in again — and it destroys no history, because a login is
recorded in the append-only `audit_events` trail and not in the session row.

This is also exactly what a **downgrade followed by a re-upgrade** costs.
`downgrade()` drops the two columns; the session rows survive and the table
returns to its pre-0009 shape, but which transaction produced which session, and
every `completion_claimed_at`, are gone and cannot be reconstructed. Re-applying
0009 therefore meets the same precondition and refuses until those sessions are
deleted. Revoking them is *not* sufficient: the constraint is evaluated over
every row, and a revoked row is still a row.

`docs/operations/web-portal.md` §"Migration stages and rollback" records the
sequence an operator follows. The rehearsal in
`tests/test_oauth_completion_binding_migration.py` executes all of it.

Revision ID: 0009
Revises: 0008
Create Date: 2026-08-14
"""
from __future__ import annotations

from typing import Sequence

import sqlalchemy as sa
from alembic import context, op
from sqlalchemy.dialects import postgresql

revision: str = "0009"
down_revision: str | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

#: Scoped to the rows a completion creates. See the module docstring for why the
#: predicate is here rather than a table-wide `UNIQUE`.
COMPLETION_BINDING_INDEX = "uq_sessions_oauth_transaction_id"

#: OD-44 condition 2. One successor per predecessor, so a chain cannot branch.
#: Partial because every chain's root has no predecessor and there are many roots.
LINEAR_ROTATION_INDEX = "uq_sessions_rotated_from_session_id"

#: The composite keys the rotation foreign keys reference. `id` is the primary
#: key, so both are trivially unique; PostgreSQL requires the declaration anyway.
ROTATION_IDENTITY_KEY = "uq_sessions_rotation_identity"
ROTATION_BINDING_KEY = "uq_sessions_rotation_binding"

ROTATION_ACCOUNT_METHOD_FK = "fk_sessions_rotation_account_method"
ROTATION_OAUTH_BINDING_FK = "fk_sessions_rotation_oauth_binding"

#: The one statement that resolves a branched pre-existing chain, quoted in the
#: refusal for the same reason as the one above it.
BRANCHED_ROTATION_REMEDY = (
    "DELETE FROM sessions WHERE rotated_from_session_id IS NOT NULL;"
)

#: The one statement that resolves the precondition. Named here so the refusal
#: can quote it exactly rather than describe it approximately.
UNBINDABLE_SESSION_REMEDY = (
    "DELETE FROM sessions WHERE auth_method = 'discord_oauth';"
)

OFFLINE_PRECONDITION_NOTICE = """
-- ---------------------------------------------------------------------------
-- REVISION 0009 -- THE PRECONDITION COUNT IS NOT IN THIS SCRIPT
--
-- Online, this revision first counts `discord_oauth` sessions that predate the
-- binding and refuses with that count, because none of them can be given an
-- `oauth_transaction_id` -- the transaction that produced them was never
-- recorded. Offline mode never connects, so the count cannot run.
--
-- The `ADD CONSTRAINT` below still refuses -- it validates existing rows -- so
-- the migration cannot half-apply. What is lost is the explanation, not the
-- protection. If it fails, run:
--
--   DELETE FROM sessions WHERE auth_method = 'discord_oauth';
--
-- which ends those logins (the people affected sign in again) and destroys no
-- history: the logins themselves are in the append-only audit trail.
-- ---------------------------------------------------------------------------
"""


def _refuse_unbindable_sessions() -> None:
    """Count the sessions this revision cannot bind, and refuse with the number.

    Deliberately *before* the column is added, because at that moment "cannot be
    bound" is simply "is a `discord_oauth` session": there is no column for a
    value to be in. Letting `ADD CONSTRAINT` fail instead would name a constraint
    where an operator needs a cause and a remedy.
    """
    if context.is_offline_mode():
        op.execute(sa.text(OFFLINE_PRECONDITION_NOTICE))
        return

    connection = op.get_bind()
    unbindable = connection.execute(
        sa.text("SELECT count(*) FROM sessions WHERE auth_method = 'discord_oauth'")
    ).scalar_one()
    if unbindable:
        raise RuntimeError(
            f"Revision 0009 refused: {unbindable} Discord OAuth session row(s) "
            "predate the completion binding and cannot be bound, because the "
            "transaction that produced each of them was never recorded. End "
            f"those logins and re-run: {UNBINDABLE_SESSION_REMEDY} Revoking is "
            "not sufficient — the constraint is evaluated over every row, and a "
            "revoked row is still a row. No history is lost: the logins are in "
            "the append-only audit trail, not in the session row."
        )


def _refuse_nonlinear_rotations() -> None:
    """Refuse a pre-existing rotation graph the new keys could not describe.

    Two shapes are possible in a database written before this revision: a chain
    that branched, and a rotation whose account or authentication method does not
    match the row it descends from. Neither can occur through `SessionService`,
    and neither is expected to exist — but `ADD CONSTRAINT` validates existing
    rows, so if one does exist the operator meets a constraint name rather than a
    cause. The count and the remedy are stated here instead.

    The OAuth binding needs no third count: `oauth_transaction_id` is added by
    this same revision, and `_refuse_unbindable_sessions` has already established
    that no `discord_oauth` session survives to carry one.
    """
    if context.is_offline_mode():
        return

    connection = op.get_bind()
    crossing = connection.execute(
        sa.text(
            """
            SELECT count(*)
              FROM sessions successor
              JOIN sessions predecessor
                ON predecessor.id = successor.rotated_from_session_id
             WHERE successor.platform_account_id <> predecessor.platform_account_id
                OR successor.auth_method <> predecessor.auth_method
            """
        )
    ).scalar_one()
    branched = connection.execute(
        sa.text(
            """
            SELECT count(*)
              FROM (
                    SELECT rotated_from_session_id
                      FROM sessions
                     WHERE rotated_from_session_id IS NOT NULL
                  GROUP BY rotated_from_session_id
                    HAVING count(*) > 1
                   ) AS branches
            """
        )
    ).scalar_one()
    if crossing or branched:
        raise RuntimeError(
            f"Revision 0009 refused: {crossing} session rotation(s) disagree with "
            f"their predecessor's account or authentication method and {branched} "
            "session(s) have more than one successor. A rotation chain must be "
            "linear and must not cross an account, an authentication method or an "
            f"OAuth binding. End the affected logins and re-run: "
            f"{BRANCHED_ROTATION_REMEDY} No history is lost: rotations are "
            "recorded in the append-only audit trail, not in the session row."
        )


def upgrade() -> None:
    _refuse_unbindable_sessions()
    _refuse_nonlinear_rotations()
    op.add_column(
        "oauth_transactions",
        sa.Column("completion_claimed_at", sa.DateTime(timezone=True), nullable=True),
    )
    # A claim without a consumption would be a completion for a transaction whose
    # verifier was never recovered, which cannot have reached the provider. The
    # claim statement already requires `consumed_at IS NOT NULL`; this is the same
    # rule stated where a future statement cannot forget it.
    op.create_check_constraint(
        op.f("ck_oauth_transactions_completion_requires_consumption"),
        "oauth_transactions",
        "completion_claimed_at IS NULL OR consumed_at IS NOT NULL",
    )

    op.add_column(
        "sessions",
        sa.Column("oauth_transaction_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    # `RESTRICT`, so the 24-hour expiry reaper in N-04 cannot delete a transaction
    # a live session still names. A session whose origin row had been deleted
    # would be a session nobody could trace back to a login.
    op.create_foreign_key(
        op.f("fk_sessions_oauth_transaction_id_oauth_transactions"),
        "sessions",
        "oauth_transactions",
        ["oauth_transaction_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        COMPLETION_BINDING_INDEX,
        "sessions",
        ["oauth_transaction_id"],
        unique=True,
        postgresql_where=sa.text("rotated_from_session_id IS NULL"),
    )
    # The forbidden state, as a database property: a Discord OAuth session with no
    # transaction behind it, or a break-glass session pretending to have one.
    op.create_check_constraint(
        op.f("ck_sessions_oauth_transaction_binding"),
        "sessions",
        "(auth_method = 'discord_oauth') = (oauth_transaction_id IS NOT NULL)",
    )

    # -- OD-44 condition 2: the rotation chain is linear and does not cross ----
    #
    # The partial index is the branching control: at most one row may name a given
    # predecessor, so a session cannot acquire two successors and two live
    # descendants of one login cannot exist.
    op.create_index(
        LINEAR_ROTATION_INDEX,
        "sessions",
        ["rotated_from_session_id"],
        unique=True,
        postgresql_where=sa.text("rotated_from_session_id IS NOT NULL"),
    )
    # The two composite unique keys exist only as foreign-key targets; `id` alone
    # is already the primary key.
    op.create_unique_constraint(
        ROTATION_IDENTITY_KEY,
        "sessions",
        ["id", "platform_account_id", "auth_method"],
    )
    op.create_unique_constraint(
        ROTATION_BINDING_KEY, "sessions", ["id", "oauth_transaction_id"]
    )
    # Equality with the predecessor, declared rather than remembered. Both keys are
    # `MATCH SIMPLE`, so each is satisfied without a lookup when any of its
    # referencing columns is null — which is precisely the behaviour wanted: a root
    # session (no predecessor) is exempt from both, and a break-glass rotation (no
    # transaction) is exempt from the second while the first still binds it to its
    # predecessor's account and method. `MATCH FULL` would forbid break-glass
    # rotation outright and was rejected for that reason; `adapters/database/
    # tables.py` records the full argument beside the metadata.
    op.create_foreign_key(
        ROTATION_ACCOUNT_METHOD_FK,
        "sessions",
        "sessions",
        ["rotated_from_session_id", "platform_account_id", "auth_method"],
        ["id", "platform_account_id", "auth_method"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        ROTATION_OAUTH_BINDING_FK,
        "sessions",
        "sessions",
        ["rotated_from_session_id", "oauth_transaction_id"],
        ["id", "oauth_transaction_id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint(ROTATION_OAUTH_BINDING_FK, "sessions", type_="foreignkey")
    op.drop_constraint(ROTATION_ACCOUNT_METHOD_FK, "sessions", type_="foreignkey")
    op.drop_constraint(ROTATION_BINDING_KEY, "sessions", type_="unique")
    op.drop_constraint(ROTATION_IDENTITY_KEY, "sessions", type_="unique")
    op.drop_index(LINEAR_ROTATION_INDEX, table_name="sessions")
    op.drop_constraint(
        op.f("ck_sessions_oauth_transaction_binding"), "sessions", type_="check"
    )
    op.drop_index(COMPLETION_BINDING_INDEX, table_name="sessions")
    op.drop_constraint(
        op.f("fk_sessions_oauth_transaction_id_oauth_transactions"),
        "sessions",
        type_="foreignkey",
    )
    op.drop_column("sessions", "oauth_transaction_id")
    op.drop_constraint(
        op.f("ck_oauth_transactions_completion_requires_consumption"),
        "oauth_transactions",
        type_="check",
    )
    op.drop_column("oauth_transactions", "completion_claimed_at")
