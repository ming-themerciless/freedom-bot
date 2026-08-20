"""P3.3 second remediation: a committed effect can never be denied, and can always be published.

Added by the 2026-08-18 P3.3 effect-publication remediation, as a **successor** to
0012 rather than an edit of it or of 0011. Both have been applied to development
and disposable test databases, `.agents/AGENTS.md` says "never edit an applied
migration", and a successor is the only form in which the round-trip evidence this
remediation owes — upgrade -> downgrade -> upgrade against real PostgreSQL — means
anything.

## The two defects this revision exists for

Migration 0012 gave the job the durable fact `effect_committed_at`, and the
cancellation request, the self-abandon, `mark_stale` and `invalidate_for_snapshot`
all learned to refuse when it is set. Two writers did not:

1. **`request_cancel`'s `queued` branch.** It matched `id = :job_id AND state =
   'queued'` and nothing else. The reaper deliberately requeued a job whose effect
   had committed but whose result had not been published, so a cancellation
   arriving in that window produced a `cancelled` job over a durable import.

2. **The reaper itself.** It chose between `queued` and `failed` from `attempts <
   max_attempts` alone. An apply whose effect committed on attempt three and whose
   process died before publishing became `failed` with `attempts_exhausted` — a
   job denying an import the database is still holding.

Both are the same mistake in two places: a terminal or restartable state chosen
without asking whether the effect is already durable.

## What this revision adds

### `effect_result` — the publication, made durable where the effect is

The result the worker owes was only ever an in-memory `Executed` value on the
thread that produced it. When the process died, it died with it, and the only
recovery available was to re-run the whole attempt and hope the import service
recognised the spent request key. That costs an execution attempt, re-parses a
multi-megabyte artifact, re-resolves Council authority, and can end in `stale` or
`failed` for reasons that have nothing to do with the import that already
committed.

`effect_result` is the bounded summary and blocked-entry list of the run, written
by the **commit fence, in the transaction that commits the effect**. Recovery is
then a read of two durable rows — this column and the immutable `snapshot_imports`
receipt the same transaction wrote — and one publication transaction. No artifact
is re-parsed, no attempt is consumed, and the effect is never run again.

`CHECK ((effect_committed_at IS NULL) = (effect_result IS NULL))` is what makes
that a guarantee rather than a hope: a job cannot record that its effect committed
without also recording what the publication owes, because the fence writes both in
one statement.

### `committed_effect_is_never_denied` — the invariant, at the write boundary

`CHECK (effect_committed_at IS NULL OR state NOT IN ('failed', 'cancelled',
'stale'))`.

Every one of those three states asserts that *nothing was applied*. None of them
can describe an apply whose import is durable. The application statements each
carry the matching predicate so they **refuse** rather than violate — a statement
that matches zero rows lets a worker exit quietly, where a check violation aborts
its transaction — but the constraint is what makes the invariant true for direct
runtime-role SQL, for a future statement nobody remembered to write the predicate
into, and for a reviewer who wants to read the guarantee rather than audit eleven
call sites for it.

`queued` is deliberately **not** in the forbidden list. A committed effect is no
longer requeued by any production statement, but leaving `queued` representable
keeps the import service's spent-request-key path a working safety net instead of
a constraint violation, and a re-executed attempt that finds its own import is a
correct if wasteful outcome. `running` and `completed` are the states the recovery
design actually uses.

## Why no new job state

An earlier draft of this design added a seventh state, `recovering`. It is not
here. The recovery is one transaction taken under the job row's write lock — read
the two durable rows, insert the result, complete the job, record the completion
event — so there is no interval during which a distinguishable state would be
observable, and N-27's six states are an accepted register value that a purely
internal convenience must not spend. The job is `running` with an expired lease
until it is `completed`, which is exactly what it already was between a crash and
the reaper's next pass.

## Reversible below its rollback boundary, and refusing above it

**Corrected by the 2026-08-18 migration-rollback remediation.** The paragraph that
stood here claimed a general reversibility this revision does not have, and the
independent review was right to reject it. What it said was that dropping
`effect_result` "loses no fact that is not also in `snapshot_imports`", so the
only cost of a downgrade was the inability to publish an effect committed while
the schema was down-level. Both halves were wrong:

- `snapshot_imports` holds the **import's** receipt, not the **run's** bounded
  result. The blocked create-candidate list, the `{code, severity, count}` issue
  counts (the receipt keeps bare `issue_codes`), `would_create`, `would_update`
  and `selected_folder_path` exist in `effect_result` and nowhere else. For a
  committed effect awaiting publication they exist *only* there.
- The real cost is worse than an unpublishable effect. `effect_committed_at` is
  deliberately preserved by this downgrade — it is 0012's column — so after
  `downgrade 0012` every truthfully completed apply is a row carrying a committed
  effect and no payload. `upgrade 0013` then refuses on exactly those rows, and
  the database is **stranded one revision below head**, with no remedy this
  platform permits: reconstructing the payload would be inventing a durable fact,
  and clearing the fence or deleting the job/import history is forbidden.

So the boundary is stated rather than discovered. **Corrected again by the
2026-08-18 second migration-rollback remediation**, which found the previous
wording ("available until the first apply commits an effect, and refused
afterwards") claiming a permanent historical fact the guard does not record and
this schema does not hold:

> **Downgrade below 0013 is refused while any retained reconciliation job
> records a committed effect. It becomes available only when no such job exists;
> in normal operation that means either no apply has committed, or every
> completed committed-effect job and its result has been removed by the approved
> N-24 retention process and no committed-but-unpublished job remains.**

The difference is N-24. Retention deletes a *completed terminal* job and its
result once the retention conditions are met, and deliberately preserves the
immutable `snapshot_imports` receipt and the append-only audit history. Once
every completed committed-effect job has aged out and no committed-but-
unpublished job survives, there is no row whose `effect_result` a downgrade
could destroy and none the re-upgrade's
`ck_reconciliation_jobs_effect_result_accompanies_the_fence` could refuse — so
the count is zero and the downgrade is truthfully safe again. The guard counts
surviving rows because surviving rows are exactly what a downgrade can hurt.

**Retention is not a rollback bypass, and it cannot be used as one.** It never
removes a running job, so a committed-but-unpublished effect blocks the
downgrade at any age; eligibility, the operator command, its audit event and the
30-day age are unchanged by this remediation and nothing here shortens them.

`downgrade()` enforces the boundary *before it changes anything*
(`_refuse_a_downgrade_that_cannot_be_undone`), naming both populations —
completed, and committed-but-unpublished — because they differ in what a
downgrade would cost, and naming what the operator does instead.

**The decision is taken under `ACCESS EXCLUSIVE` on `reconciliation_jobs`, not
under an ordinary MVCC snapshot.** That is the second blocking finding of the
independent re-review, and the reason the lock is part of the guard rather than
an optimisation: a plain `SELECT` that returns zero and *then* lets the first
`ALTER TABLE` queue for its own lock leaves a window in which an in-flight
worker commits its fence, the drops proceed, and the database ends in exactly
the unpublishable, un-re-upgradeable state this revision exists to prevent. See
`_refuse_a_downgrade_that_cannot_be_undone` for the interleaving and the
lock-conflict reasoning. Offline (`--sql`) mode gets the same lock and the same
guard as executable statements rather than a comment: unlike the upgrade, whose
`ADD CONSTRAINT` statements validate every existing row and therefore refuse on
their own, a `DROP CONSTRAINT`/`DROP COLUMN` pair succeeds against any data at
all, so a comment would be no protection.

That rollback boundary changes the **operational contract**, and this file does
not self-approve it: it is written up in `docs/operations/web-portal.md`
("Migration 0013 rollback boundary") and in the submission's §14 as a proposal
awaiting Peter/Acceptance Authority ratification. What is implemented here is only
the conservative half — refusing to destroy a payload nothing may truthfully
reconstruct — which is correct under either policy.

Below the boundary the revision is genuinely reversible, and the evidence is now
separated so neither can be read as the other:

- `tests/web/test_migration_0013_round_trip.py` — the **empty/unused** schema
  round trip. Evidence that the statements are structurally reversible, and
  evidence of nothing else.
- `tests/web/test_migration_0013_rollback_boundary.py` — the **data-bearing**
  cases against real PostgreSQL: a truthfully completed apply, an effect awaiting
  recovery, a realistic database below the boundary that still round-trips, and
  the atomicity of a failed migration in both directions.

`upgrade()` refuses rather than corrupts if it meets a row this revision cannot
describe: a job whose effect committed with no durable publication payload, or one
already sitting in a state that denies its effect. With the downgrade guard in
place the first can no longer be produced by rolling this revision back; it
remains reachable by a pre-0013 database and by direct SQL, so the guard stays,
and its message now distinguishes the two ways a database can hold one.
"""
from __future__ import annotations

from typing import Sequence

import sqlalchemy as sa
from alembic import context, op
from sqlalchemy.dialects import postgresql

revision: str = "0013"
down_revision: str | None = "0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


#: The states that assert *nothing was applied*, and therefore cannot describe an
#: apply whose import is durable. Written once, here, and rendered into the check
#: constraint below — the same list appears in `adapters/database/tables.py`, and
#: the metadata-parity test is what holds the two together.
DENYING_STATES = ("failed", "cancelled", "stale")

_DENIED = ", ".join(f"'{state}'" for state in DENYING_STATES)

#: The lock the downgrade takes **before it decides**, held until the migration
#: transaction commits or rolls back.
#:
#: Added by the 2026-08-18 second migration-rollback remediation. `ACCESS
#: EXCLUSIVE` is chosen rather than argued down to something narrower for two
#: reasons: it conflicts with *every* lock mode, so no statement capable of
#: creating or changing a committed-effect row can run between the count and the
#: drops; and the three `ALTER TABLE` statements this revision's `downgrade()`
#: runs require exactly this mode anyway, so taking it up front adds no
#: concurrency cost and removes the lock **upgrade** the previous design
#: performed silently — `ROW EXCLUSIVE`-and-then-`ACCESS EXCLUSIVE` is the shape
#: that deadlocks against a concurrent writer taking the same pair in the other
#: order.
#:
#: Written once, here, so the online guard, the offline script and the tests all
#: name the same statement.
DOWNGRADE_LOCK = "LOCK TABLE reconciliation_jobs IN ACCESS EXCLUSIVE MODE"

#: What an offline (`--sql`) script says instead of the precondition counts.
#:
#: Offline mode never connects, so the guard below cannot run. The two check
#: constraints still validate every existing row, so the protection is intact and
#: the migration cannot half-apply; what is lost is the explanation. This puts the
#: explanation in the script, where the operator running it will read it. The same
#: pattern, and the same reasoning, as revision 0009's precondition notice.
OFFLINE_PRECONDITION_NOTICE = """
-- ---------------------------------------------------------------------------
-- REVISION 0013 -- THE PRECONDITION COUNTS ARE NOT IN THIS SCRIPT
--
-- Online, this revision first counts reconciliation jobs that migration 0012
-- could produce and this revision cannot describe -- a committed import effect
-- with no `effect_result` payload, or one already sitting in a state that denies
-- it -- and refuses with those counts and a remedy. Offline mode never connects,
-- so the counts cannot run.
--
-- The two ADD CONSTRAINT statements below still refuse: they validate existing
-- rows, so the migration cannot half-apply. What is lost is the explanation, not
-- the protection. If either fails, the offending jobs' imports are unaffected and
-- are recorded in the append-only `snapshot_imports` table; in a disposable
-- development database, TRUNCATE the reconciliation tables and re-run.
-- ---------------------------------------------------------------------------
"""

#: The rollback boundary, as SQL, for the offline (`--sql`) downgrade script.
#:
#: The upgrade can afford a comment: its two `ADD CONSTRAINT` statements validate
#: every existing row, so an offline upgrade of a database this revision cannot
#: describe fails on its own and the protection survives without the explanation.
#: **The downgrade has no such backstop.** `DROP CONSTRAINT` and `DROP COLUMN`
#: succeed against any data at all, so a comment would be the only thing standing
#: between an operator and a database that can never return to head — and a
#: comment is not a control.
#:
#: So the guard is emitted as statements that lock and raise. It is the same lock,
#: the same two counts and the same refusal the online path computes, expressed
#: where the script will run them, and it is emitted **before** the statements it
#: protects so a script applied top to bottom stops before the first drop.
#:
#: **The lock is inside the script's own transaction and is not released between
#: the guard and the drops.** `migrations/env.py` runs the offline migration
#: inside `context.begin_transaction()`, and PostgreSQL's dialect is
#: transactional, so Alembic frames the generated script with `BEGIN;` … `COMMIT;`
#: — one transaction holding this lock from here through the last `DROP` and the
#: `alembic_version` update. A `LOCK TABLE` outside a transaction block would be
#: released the moment its own statement ended and would guard nothing, which is
#: why `tests/web/test_migration_0013_rollback_boundary.py` asserts the framing
#: and the statement order rather than the presence of the words.
OFFLINE_DOWNGRADE_GUARD = f"""
-- ---------------------------------------------------------------------------
-- REVISION 0013 -- THE ROLLBACK BOUNDARY, ENFORCED BY THIS SCRIPT
--
-- Downgrade below 0013 is refused while any retained reconciliation job records
-- a committed import effect. Dropping `effect_result` would destroy the
-- publication payload the commit fence wrote inside each effect's own
-- transaction; `snapshot_imports` does not hold it, and nothing may invent it.
-- See docs/operations/web-portal.md, "Migration 0013 rollback boundary".
--
-- THE LOCK BELOW IS PART OF THE GUARD, NOT AN OPTIMISATION, AND MUST NOT BE
-- EDITED OUT OR MOVED. Without it the count runs under an ordinary MVCC
-- snapshot, the DO block ends, and the DROP statements queue for their own locks
-- afterwards -- so a worker transaction already applying an import commits its
-- fence in between, is counted by nobody, and has its publication payload
-- dropped. With it, a writer already in flight must finish before this lock is
-- granted and its committed row is therefore visible to the count, and a writer
-- that starts later waits until this script commits or rolls back. Do not split
-- this script's transaction: the lock is released when it ends.
-- ---------------------------------------------------------------------------
{DOWNGRADE_LOCK};

DO $rollback_boundary$
DECLARE
    completed_effects   bigint;
    unpublished_effects bigint;
BEGIN
    SELECT count(*) FILTER (WHERE state = 'completed'),
           count(*) FILTER (WHERE state <> 'completed')
      INTO completed_effects, unpublished_effects
      FROM reconciliation_jobs
     WHERE effect_committed_at IS NOT NULL;

    IF completed_effects + unpublished_effects > 0 THEN
        RAISE EXCEPTION
            'Refusing to downgrade revision 0013: % retained reconciliation '
            'job(s) record a committed import effect (% completed, % committed '
            'but unpublished). Dropping `effect_result` would destroy the '
            'publication payload the commit fence wrote inside each effect''s '
            'own transaction, so an unpublished effect could never be published '
            'and this database could never be upgraded back to 0013. Nothing has '
            'been changed. Roll forward at 0013 instead; see '
            'docs/operations/web-portal.md, "Migration 0013 rollback boundary".',
            completed_effects + unpublished_effects,
            completed_effects,
            unpublished_effects;
    END IF;
END
$rollback_boundary$"""


def upgrade() -> None:
    connection = op.get_bind()
    _refuse_rows_this_revision_cannot_describe(connection)

    op.add_column(
        "reconciliation_jobs",
        sa.Column("effect_result", postgresql.JSONB(), nullable=True),
    )
    # The fence writes both columns in one statement, so a job that records a
    # committed effect always records what its publication owes.
    op.create_check_constraint(
        "effect_result_accompanies_the_fence",
        "reconciliation_jobs",
        "(effect_committed_at IS NULL) = (effect_result IS NULL)",
    )
    # The invariant R-45 and the reaper each broke, stated once where neither can
    # reach around it.
    op.create_check_constraint(
        "committed_effect_is_never_denied",
        "reconciliation_jobs",
        f"effect_committed_at IS NULL OR state NOT IN ({_DENIED})",
    )


def downgrade() -> None:
    _refuse_a_downgrade_that_cannot_be_undone(op.get_bind())

    op.drop_constraint(
        # The **unqualified** names: the metadata's naming convention
        # (`ck_%(table_name)s_%(constraint_name)s`) is applied on the way out, so
        # passing a rendered name here would render it a second time.
        "committed_effect_is_never_denied",
        "reconciliation_jobs",
        type_="check",
    )
    op.drop_constraint(
        "effect_result_accompanies_the_fence",
        "reconciliation_jobs",
        type_="check",
    )
    op.drop_column("reconciliation_jobs", "effect_result")


def _refuse_rows_this_revision_cannot_describe(connection) -> None:
    """Stop with a sentence an operator can act on, rather than a constraint name.

    Both conditions are states migration 0012's code could produce and this
    revision's constraints forbid. Neither can exist in a deployed database — P3.3
    has not been accepted and nothing has been deployed — so this is a guard for a
    development database that has been driven through the pre-remediation paths,
    and it names the count and the remedy rather than the rows.

    Offline (`--sql`) mode never connects, so the counts cannot run. The two check
    constraints still validate every existing row, so the protection is intact and
    the migration cannot half-apply; the script carries the explanation instead.
    """
    if context.is_offline_mode():
        op.execute(sa.text(OFFLINE_PRECONDITION_NOTICE))
        return

    # Every pre-0013 row carrying a committed effect violates the new
    # `effect_result_accompanies_the_fence` constraint, because the column it
    # names did not exist when the fence wrote the timestamp. The state does not
    # narrow it: a `running` one is an unpublished effect and a `completed` one
    # is a published effect whose payload was never stored.
    unpublishable = connection.execute(
        sa.text(
            "SELECT count(*) FROM reconciliation_jobs "
            "WHERE effect_committed_at IS NOT NULL"
        )
    ).scalar_one()
    denied = connection.execute(
        sa.text(
            "SELECT count(*) FROM reconciliation_jobs "
            f"WHERE effect_committed_at IS NOT NULL AND state IN ({_DENIED})"
        )
    ).scalar_one()
    if denied:
        raise RuntimeError(
            f"{denied} reconciliation job(s) are in a state that denies a "
            "committed import effect. Those rows were produced by the "
            "pre-remediation reaper or cancellation statements and this revision "
            "forbids the state. Each one's import is still valid and is recorded "
            "in `snapshot_imports`; resolve the jobs (in a disposable development "
            "database, TRUNCATE the reconciliation tables) before upgrading."
        )
    if unpublishable:
        raise RuntimeError(
            f"{unpublishable} reconciliation job(s) record a committed import "
            "effect and carry no durable publication payload, so they cannot "
            "satisfy `ck_reconciliation_jobs_effect_result_accompanies_the_fence`."
            " There are two ways to hold such a row, and they need different "
            "answers. (a) The database ran 0012's code and never reached this "
            "revision: the payload was never written, because the column did not "
            "exist. In a disposable development database, TRUNCATE the "
            "reconciliation tables and re-run. (b) The database was at 0013 and "
            "was downgraded past this revision by something other than this "
            "revision's own `downgrade()`, which refuses exactly to prevent it: "
            "the payload existed and was destroyed, no truthful reconstruction "
            "is possible, and neither clearing `effect_committed_at` nor deleting "
            "the jobs is permitted. Restore the pre-downgrade backup and roll "
            "forward; see docs/operations/web-portal.md, \"Migration 0013 "
            "rollback boundary\". In every case each job's import itself is "
            "unaffected and is recorded in the append-only `snapshot_imports`."
        )


def _refuse_a_downgrade_that_cannot_be_undone(connection) -> None:
    """The rollback boundary, decided under a lock, before this revision changes anything.

    Added by the 2026-08-18 migration-rollback remediation, for the finding that
    `downgrade 0012` on a database which had processed a normal apply destroyed
    the payload `upgrade 0013` then demanded back — stranding the database one
    revision below head with no permitted remedy. Made **atomic** by the
    2026-08-18 second remediation, for the blocking finding described next.

    ## Why the count is taken under `ACCESS EXCLUSIVE` rather than plainly

    The first version of this guard ran an ordinary `SELECT`, returned when the
    count was zero, and only then let the first `ALTER TABLE` queue for its own
    DDL lock. It held nothing that excluded the commit fence while it decided, so
    this interleaving destroyed a committed effect:

    1. a worker transaction is applying an import and has not committed its fence;
    2. this guard's `SELECT` runs under its own MVCC snapshot and sees zero
       committed effects, because the worker has not committed;
    3. the worker commits `effect_committed_at` **and** `effect_result`;
    4. the first `ALTER TABLE` is granted its lock *after* that commit;
    5. `effect_result` is dropped; and
    6. the database holds the exact unpublishable, un-re-upgradeable row this
       revision exists to make unreachable.

    Stopping the workers first is required operational practice
    (`docs/operations/web-portal.md` §3.6) and it is defence in depth, not a
    substitute: this migration claims to be the backstop for the operator who
    misses that step or whose process is still draining, and a backstop that
    races is not one.

    So the lock is taken **first**, before the snapshot the count will use:

        acquire ACCESS EXCLUSIVE on reconciliation_jobs
        → count from the committed state that lock now freezes
        → refuse, or perform all three drops
        → COMMIT or ROLLBACK, which is what releases the lock

    `ACCESS EXCLUSIVE` conflicts with every lock mode PostgreSQL has, so it
    excludes `INSERT`, `UPDATE`, `DELETE` (`ROW EXCLUSIVE`), `SELECT … FOR
    UPDATE` (`ROW SHARE`) and every other statement able to create or change a
    row carrying `effect_committed_at` — the commit fence's `UPDATE` above all.
    A writer already in flight holds `ROW EXCLUSIVE` until it commits or rolls
    back, so this `LOCK TABLE` waits for it and the count therefore sees its
    committed row. A writer arriving later conflicts with this lock — and, while
    it is still pending, with the *request* for it, because PostgreSQL queues a
    conflicting requester behind an existing waiter — so it cannot commit a fence
    until this migration has finished.

    It is also the mode the three `ALTER TABLE` statements below need anyway, so
    taking it here costs no additional concurrency and removes a lock
    **upgrade**: the previous shape took a weaker lock implicitly and then
    escalated, which is the classic deadlock pair against a session taking the
    same two locks in the other order. There is one lock, taken once, at the
    start. `lock_timeout` is deliberately not set: an operator running a
    migration wants it to wait for a draining worker, and PostgreSQL's deadlock
    detector still resolves a genuine cycle.

    Advisory locks are not used and would not work here: workers take none, so an
    advisory lock would exclude only other migrations.

    ## The predicate, and what N-24 retention does to it

    **Corrected by the second remediation.** The guard does not record the
    historical fact "an apply has committed at some point"; it counts the
    reconciliation jobs that are **still retained**:

    > Downgrade below 0013 is refused while any retained reconciliation job
    > records a committed effect. It becomes available only when no such job
    > exists — either no apply has committed, or the approved N-24 retention
    > process has removed every completed committed-effect job and its result and
    > no committed-but-unpublished job remains.

    That is a truthful boundary rather than a weakened one. What a downgrade can
    destroy is a surviving `effect_result`; once retention has removed the job
    and its result, there is nothing left for the drop to take and nothing for the
    re-upgrade's `effect_result_accompanies_the_fence` to refuse, because the row
    it would refuse is gone. The immutable `snapshot_imports` receipt and the
    append-only audit history that retention preserves obstruct neither
    direction: no constraint in this revision reads them, and no column of theirs
    is added or dropped here.

    Retention cannot be turned into a rollback bypass. It removes only
    **terminal** jobs past their age, so a committed-but-unpublished effect —
    always `running`, never terminal — is never eligible and blocks the downgrade
    at any age. Nothing in this remediation changes eligibility, the retention
    period, the operator command or its audit event, and the operations document
    forbids early or manual deletion as a rollback route.

    **Two populations, counted apart**, because a downgrade costs them different
    things and an operator deciding what to do next has to know which they hold:

    - `completed` — the publication already happened, so what a downgrade would
      take is only the ability to return to head. Only, and that is enough: the
      re-upgrade would refuse on every one of these rows.
    - anything else (in practice `running` with a lapsed lease) — the effect is
      durable and its result has never been published. `effect_result` is the
      only row holding the bounded summary and the blocked create-candidate list
      the run produced, so a downgrade would make the publication impossible as
      well as the re-upgrade.

    **`queued` is included by `state <> 'completed'` and that is deliberate.** No
    production statement requeues a committed effect any more, but the column is
    still representable there (see the module docstring), and a row this guard
    did not count would be a row a downgrade silently broke.

    Raised **before** the first `DROP`, so a refused downgrade leaves the database
    at 0013, complete and usable — which is what makes the refusal safe to retry
    and safe to ignore. The whole revision runs inside one transaction
    (`migrations/env.py`), so even a failure after this point leaves the complete
    pre-migration schema rather than half of it, and rolling that transaction back
    is also what releases the lock.
    """
    if context.is_offline_mode():
        # Not a comment: see `OFFLINE_DOWNGRADE_GUARD`. The generated script
        # carries the same lock, the same two counts, and refuses in the server
        # that runs it.
        op.execute(sa.text(OFFLINE_DOWNGRADE_GUARD))
        return

    # First, and on the connection Alembic's transaction owns, so it is held
    # until that transaction ends. Everything below decides from the state this
    # lock has frozen.
    connection.execute(sa.text(DOWNGRADE_LOCK))

    completed_effects, unpublished_effects = connection.execute(
        sa.text(
            "SELECT count(*) FILTER (WHERE state = 'completed'), "
            "count(*) FILTER (WHERE state <> 'completed') "
            "FROM reconciliation_jobs WHERE effect_committed_at IS NOT NULL"
        )
    ).one()
    total = completed_effects + unpublished_effects
    if not total:
        return

    raise RuntimeError(
        f"Refusing to downgrade revision 0013: {total} retained reconciliation "
        f"job(s) record a committed import effect ({completed_effects} completed, "
        f"{unpublished_effects} committed but unpublished). Dropping "
        "`effect_result` would destroy the publication payload the commit fence "
        "wrote inside each effect's own transaction, and nothing may truthfully "
        "reconstruct it: `snapshot_imports` holds the import's own immutable "
        "receipt, not the run's blocked create-candidate list, issue counts or "
        "would-create/would-update figures. The two consequences are that a "
        "committed effect awaiting publication could never be published, and "
        "that this database could never be upgraded back to 0013, because "
        "`ck_reconciliation_jobs_effect_result_accompanies_the_fence` requires "
        "the payload back. NOTHING HAS BEEN CHANGED: the database is still at "
        "0013, complete and usable. Schema rollback below 0013 is refused while "
        "any retained job records a committed effect - roll forward at 0013 "
        "instead. It becomes available again only when no such job survives, "
        "which in normal operation means the approved N-24 retention process has "
        "removed every completed committed-effect job and its result and no "
        "committed-but-unpublished job remains; deleting job history by hand, or "
        "shortening retention to clear this refusal, is not a supported rollback "
        "route. See docs/operations/web-portal.md, \"Migration 0013 rollback "
        "boundary\", for the preflight, the worker shutdown and version order, "
        "and the recovery procedure. In a disposable development database with "
        "no history worth keeping, TRUNCATE the reconciliation tables first and "
        "this downgrade will proceed."
    )
