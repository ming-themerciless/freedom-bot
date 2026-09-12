# Claude remediation prompt — project review R5, 2026-09-08

Work in `/opt/freedom-blades/platform`.

## Scope and authority

Correct the remaining **Blocking PR-20260908-R3-1** recovery finding from
Codex's independent review of
`docs/review/project-review-remediation-2026-09-08-r4-handback.md`.
This continues the existing finding; do not replace its ID or reopen unrelated
findings. R4 materially addresses the function/type and all-zero-baseline
cases, but its recovery decisions still assume the original server transaction
has finished when that has not been established.

This authorizes only a bounded correction to the drill's recovery instructions,
their supporting logic if necessary, the operations guide and synthetic tests.
It is not Package 5.0 product implementation or complete R13 pre-execution
approval. Package 5.0 remains `not ready`; P5.0-R5 remains Blocking.

The existing restrictions remain binding: **no SSH, target-host inspection or
mutation, database operation, destructive drill, `--execute`, armed real process
boundary or materializer, execution of a generated vector, deployment, migration
`0014`, cutover, OD-62 ruling or Package 5.1+ work**. Local synthetic tests with
recording boundaries, stub PostgreSQL clients and temporary Git repositories
are permitted. Every PostgreSQL client in a stub test must remain stubbed;
never fall through to a real client. Do not terminate or cancel a real backend.

## Required reading and worktree discipline

Before planning or editing, read completely:

- `.agents/AGENTS.md`, `docs/implementation-plan.md`, and
  `docs/operations/disposable-test-server.md`;
- the current section of `docs/review/Handover information`;
- the R4 prompt and handback, and the R3 prompt and handback they reference;
- `docs/review/project-review-remediation-2026-09-07-handback.md`, including
  its execution deviations and unresolved pristine-schema failure;
- `infra/postgresql/backup-restore-drill.sh`,
  `infra/postgresql/runtime-grants.sql.tmpl`, the recovery section of
  `docs/operations/database-development.md`, and
  `tests/test_database_backup_restore.py`.

Check `git status --short --untracked-files=all` and preserve every unrelated
change and untracked file. Do not reset, revert, stage, commit, push, reformat
unrelated files or overwrite earlier prompts/handbacks. Expected implementation
edits are confined to the drill, its tests and recovery guide. Explain any
necessary expansion before proceeding.

## Remaining finding: client exit does not establish backend completion

At review time, the `destroy_attempted` banner says that some nonzero count,
a matching whole state report and a matching row inventory establish:

> THE DESTROY DID NOT TAKE EFFECT.

It then says no data restore is required. The operations guide repeats this
decision. Neither procedure first establishes that the original PostgreSQL
backend transaction has ended.

PostgreSQL 16 documents that:

- with `client_connection_check_interval=0` (the default), the server detects
  connection loss at its next socket interaction, rather than necessarily
  stopping its query when the client disappears;
- a Read Committed `SELECT` sees data committed before the query began, not
  uncommitted changes made by another transaction.

Primary references:

- [Connection checks](https://www.postgresql.org/docs/16/runtime-config-connection.html#GUC-CLIENT-CONNECTION-CHECK-INTERVAL)
- [Transaction isolation](https://www.postgresql.org/docs/16/transaction-iso.html)

The resulting failure sequence is:

1. `public` holds one function and no base tables.
2. The DROP command reaches the server, but the client dies without reporting
   success. The server transaction is still running.
3. Both recovery reports see the old committed state: `routines=1`, with an
   empty row inventory. Both match their baselines.
4. R4 directs the operator to conclude that no restore is required.
5. The original transaction subsequently commits; the function is gone.

The dependent `restore_attempted` decision has the corresponding omission:
zero counts can mean an uncommitted restore is **still running**, not that it
rolled back. Repeating the restore on that inference is not a resolved recovery
decision.

### Independent evidence and its limits

Codex ran the real drill through the shipped stub helper, with a function-only
baseline, empty inventory, `destroy_exit=42` and `destroy_applied=False`.
Both printed report commands were then run through the same stub. Both matched
their baselines, and the banner contained the no-restore conclusion. Codex then
created the stub's `.dropped` state marker to model the original transaction
committing **after** those observations. The next state report had `routines=0`.
No restore had been invoked.

This is a controlled synthetic sequence showing the missing state in the
decision contract. It is **not** a PostgreSQL timing reproduction, does not
execute SQL, and does not establish target configuration. The backend timing
concern is an inference from the primary documentation above. Preserve that
distinction in your evidence.

## Required correction

1. Add a regression before the correction that models backend completion
   independently of client exit and visible catalog state. Cover a pending
   DROP whose reports initially match and whose commit occurs after observation.
   Include the completed refused/rolled-back and completed committed controls.
   Use deterministic state transitions or barriers, not timing-dependent sleeps.
2. Make both uncertain-stage procedures safe when backend completion is unknown.
   **A conservative operator stop is acceptable and preferred to expanding this
   into a generic recovery engine.** Reports may remain useful observations, but
   cannot by themselves prove the original transaction has ended or justify a
   no-recovery conclusion, a retry, or a resume point.
3. Either leave the outcome explicitly unresolved pending operator confirmation
   of transaction completion, or provide a bounded, reviewable completion
   mechanism. If you choose a mechanism, explain how it identifies the original
   backend/transaction and handles missing evidence, insufficient visibility,
   identity reuse and races. Client exit, a fixed delay, repeated equal reports,
   or an arbitrary count of retries is not proof. Do not add automatic backend
   termination or cancellation. If completion cannot be established safely in
   this scope, stop conservatively rather than inventing an operational authority.
4. Correct `restore_attempted` in the same scope. Model a restore still pending
   while reports show zero counts, followed by commit and rollback controls.
   Unknown completion must not be labeled rollback or partial restoration merely
   because of what a snapshot shows. Audit dependent fallback text as well as
   step 0 so no later sentence bypasses the unresolved stop.
5. Preserve R4's function/type observations, explicit limits of catalog counts,
   and all-zero-baseline refusal. Equal counts are not an identity inventory.
   Preserve absent/unexpected-state stops and query-failure-as-unknown behavior.
   Do not restore over known existing objects or prescribe an unconditional
   DROP, `--clean`, TRUNCATE or other destructive reset.
6. Preserve responsibility before DROP and confirmed destruction only after
   success; confirmed post-restore resume points; checksummed recovery artifacts;
   exact runtime-role handling; explicit zero-role behavior; both final
   verifications; R3-2's pre-decode NUL refusal; R3-3's machine-readable Git path
   discovery; the live-bot skills fix; and the unchanged R13 evidence harness.
7. Update the guide, banner and comments to state the same evidence boundary:
   current observations, completion evidence, unresolved states, and the
   conditions for any later recovery action. Do not describe the counts as a
   completion barrier or conceal the missing completion check in a footnote.

Acceptance: while the original transaction may still finish, neither uncertain
stage may classify its final outcome from current counts alone or direct an
operator to skip/repeat recovery on that basis. The pending-DROP and
pending-restore regressions fail against R4 and pass against the corrected tree.
A conservative stop must be explicit in every dependent instruction.

## Verification constraints

Inspect fixtures before running permitted focused checks, and run them serially.
Do not launch a broad suite hoping to stop before database access.

The documented interpreter is on `oracle-test` at
`/opt/freedom-blades/runtime/venv-web/bin/python`. The no-SSH restriction prevents
using it here. Verify any local fallback directly, label its host/path accurately,
and do not install dependencies into production runtimes. Keep
`TEST_DATABASE_URL` unset for these synthetic runs.

Codex's independent R4 checks used the local fallback
`/opt/discord-bots/venv-web/bin/python` (Python 3.12.3, pytest 8.4.2):

- drill/filesystem modules: **192 passed, 11 deselected**;
- `bash -n infra/postgresql/backup-restore-drill.sh`: passed;
- `git diff --check`: passed;
- manifest verification: **28 source hashes, 0 mismatches**.

These describe R4, not your corrected tree. Re-run permitted relevant checks and
report actual results. Do not quote other R4 handback counts as independent
reviewer evidence or as results against your changes.

Exclude these eleven database-touching cases in
`tests/test_database_backup_restore.py`, plus any new integration case:

1. `test_the_drill_accepts_an_explicit_unix_socket_directory`
2. `test_backup_and_restore_round_trip_preserves_data`
3. `test_the_drill_leaves_the_runtime_roles_privileges_intact`
4. `test_the_drill_fails_when_the_privilege_state_is_not_restored`
5. `test_the_drill_preserves_pristine_schema_ownership_and_privileges`
6. `test_the_drill_fails_when_schema_privileges_are_not_restored`
7. `test_the_drill_emits_recovery_instructions_with_checksum_verification_on_failure`
8. `test_the_documented_recovery_procedure_restores_runtime_table_grants`
9. `test_a_role_whose_sql_identity_differs_refuses_against_postgresql`
10. `test_a_newline_bearing_role_refuses_against_postgresql`
11. `test_the_post_restore_recovery_path_restores_grants_without_restoring_again`

Also exclude `tests/test_snapshot_database.py` and
`tests/web/test_identity_migration_backup_restore.py`, which invoke the real
drill. No database-semantic or timing test may execute here. Such tests may be
written for a later authorized run, with clear deselection and cleanup contracts.
The extended `schema-state.sql` still needs authorized PostgreSQL validation
before operational acceptance. Do not claim synthetic evidence supplies it.
The pristine-schema failure remains unresolved; do not rerun it or claim this
correction diagnoses it.

Verify every manifest source hash. No harness production source needs changing;
leave generated artifacts untouched when covered bytes match. Never pass a
digest to `--execute`. Keep unconfirmed target facts unconfirmed. Report
unavailable/unconfigured formatter, linter and type-checker checks accurately.

## Handback and stop

Create `docs/review/project-review-remediation-2026-09-08-r5-handback.md` with:

- the remaining finding, chosen correction and exact files changed;
- the completion/observation distinction and every unresolved outcome;
- actual pre-fix regression failures and corrected-tree commands/results;
- pending DROP and restore cases and their completed controls;
- synthetic-versus-PostgreSQL evidence limits and deferred operational checks;
- passed, skipped, deselected and not-run checks, interpreters and reasons;
- manifest hash verification and preservation of unrelated work;
- confirmation that execution restrictions and package states remain unchanged.

Prepend a concise dated handback pointer in `docs/review/Handover information`,
retaining earlier submissions as history. Do not alter roadmap, RAID, decision
or gate records, close findings, accept risks or claim complete R13 approval.
Return to Codex for independent re-review and stop before operational execution.
