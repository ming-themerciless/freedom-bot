# Claude remediation prompt — project review R6, 2026-09-08

Work in `/opt/freedom-blades/platform`.

## Scope and review disposition

Correct the **Optional session-visibility documentation finding** from Codex's
independent review of
`docs/review/project-review-remediation-2026-09-08-r5-handback.md`.

Codex found no new Blocking or Important issue within R5's remediation scope
and recommended closing **PR-20260908-R3-1 for the recovery-instruction
correction**. This optional correction does not reopen that finding and is not
a new prerequisite for that recommendation. It does not record a maintainer
gate decision or grant operational execution approval.

This task authorizes only the wording correction, updates to existing tests
that currently require the inaccurate wording, and a concise handback.
Preserve R5's conservative operator stop and completion-before-observation
ordering. Do not implement a completion mechanism or change recovery behavior.

## Required reading and worktree discipline

Read `.agents/AGENTS.md`, `docs/implementation-plan.md`, and
`docs/operations/disposable-test-server.md` completely before work. Also read
the current handover, the R5 prompt and handback, both uncertain-stage recovery
banners in `infra/postgresql/backup-restore-drill.sh`, the corresponding guide
sections in `docs/operations/database-development.md`, and the relevant tests
in `tests/test_database_backup_restore.py`.

Check `git status --short --untracked-files=all`. Preserve all unrelated changes
and untracked files. Do not reset, revert, stage, commit, push or reformat
unrelated files. Do not alter roadmap, RAID, decision or gate records.

## Correction

R5's handback §2 says that restrictions on viewing another role's session can
hide the session row. The banners, guide, test comments and some assertions
repeat that implication.

PostgreSQL 16 documents a different distinction: **session existence and general
properties, including session user and database, are visible to all users**.
For other roles' sessions, many restricted columns are null. Users can see full
information for sessions belonging to roles they are members of; superusers and
roles with `pg_read_all_stats` privileges can see full information for all
sessions.

Primary reference:
[PostgreSQL 16, Viewing Statistics](https://www.postgresql.org/docs/16/monitoring-stats.html#MONITORING-STATS-VIEWS).
Read it before correcting the text. Do not infer target configuration from it.

1. Correct both uncertain-stage banners and the operations guide to distinguish
   a visible session row from unavailable fields needed to identify its work or
   establish transaction completion. A null field or inability to associate a
   session with this drill is not proof of completion. Do not claim permissions
   hide entire session rows.
2. Correct relevant comments and existing wording assertions in the drill tests.
   Keep their pending-transaction scenarios and completed controls unchanged in
   substance. Protect the accurate distinction without adding a new simulation
   of PostgreSQL permissions or a completion checker.
3. Add a clearly dated erratum to the R5 handback correcting §2's second reason
   and its dependent visibility claims. Preserve the original submission as
   history; identify precisely which assertions the erratum supersedes. The
   conservative stop remains an allowed design choice even though this reason
   for rejecting a mechanism was overstated. Do not imply that checking
   completion requires terminating or cancelling a backend.
4. Preserve the unresolved stop whenever transaction completion cannot be
   established; fresh reports after completion; pid-reuse caution; all-zero
   baseline refusal; confirmed resume points; checksummed artifacts; runtime-role
   handling; both final verifications; and earlier R3/R4 corrections.

Expected edits: wording/comments in the drill, operations guide and existing
test module; the dated R5 handback erratum; the new R6 handback; and the current
handover pointer. Leave other historical submissions untouched.

## Verification and execution limits

All prior restrictions remain: **no SSH, target-host inspection or mutation,
database operation, destructive drill, real backend cancellation/termination,
`--execute`, armed real process boundary or materializer, generated-vector
execution, deployment, migration `0014`, cutover, OD-62 ruling or Package 5.1+
work**. Every PostgreSQL client used in a permitted synthetic test must be
stubbed, with no fallback to a real client.

Inspect fixtures and run permitted focused checks serially. Keep
`TEST_DATABASE_URL` unset. The documented interpreter is on `oracle-test` at
`/opt/freedom-blades/runtime/venv-web/bin/python`; the no-SSH restriction prevents
using it here. Verify any local fallback directly and label it accurately. Do
not install into production runtimes.

Use the R5 prompt's explicit eleven database-case deselections, plus any newly
identified database-touching cases. Continue excluding
`tests/test_snapshot_database.py` and
`tests/web/test_identity_migration_backup_restore.py`. Do not launch broad suites
hoping they avoid database access.

Codex independently measured R5 at **204 passed, 11 deselected** for the drill
and filesystem modules using local Python 3.12.3 / pytest 8.4.2 at
`/opt/discord-bots/venv-web/bin/python`. Shell syntax and diff whitespace checks
passed; all **28** manifest source hashes matched. These figures describe R5;
report your own final-tree results rather than carrying them forward.

Run the affected permitted selection, `bash -n` on the drill and
`git diff --check`. Verify manifest hashes and leave generated artifacts
untouched when covered bytes match. Report unavailable/unconfigured checks
accurately. A wording-only correction does not require new database tests.

## Handback and stop

Create `docs/review/project-review-remediation-2026-09-08-r6-handback.md` with
the corrected distinction, changed files, primary reference, exact checks and
results, interpreter, deselections and limitations. Prepend a concise dated
pointer to `docs/review/Handover information`, retaining prior entries as
history. Return for independent review.

No finding or package gate is closed by the implementation handback. Package
5.0 remains `not ready`, P5.0-R5 remains Blocking, and complete R13 pre-execution
approval remains outstanding. PostgreSQL validation of `schema-state.sql` and
the unresolved pristine-schema failure remain outstanding. Stop before any
operational execution.
