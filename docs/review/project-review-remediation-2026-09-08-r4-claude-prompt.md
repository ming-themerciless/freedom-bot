# Claude remediation prompt — project review R4, 2026-09-08

Work in `/opt/freedom-blades/platform`.

## Scope and authority

Correct the remaining **Blocking PR-20260908-R3-1** recovery finding from
Codex's independent review of
`docs/review/project-review-remediation-2026-09-08-r3-handback.md`.
This is a continuation of that finding, not a replacement finding ID.

The `destroy_attempted` / `destroyed` split is sound, but the new state report
does not establish everything the recovery instructions claim. Correct the
report or narrow the recovery decision to what the evidence actually proves.

R3-2's pre-decode NUL rejection and R3-3's machine-readable Git path discovery
were satisfactory within the reviewed scope. Preserve them, the earlier R1/R2
corrections, the live-bot skills fix and the current R13 evidence harness.

This authorizes only a bounded drill/recovery-documentation correction and its
synthetic tests. Package 5.0 remains `not ready`; P5.0-R5 remains Blocking.
It is not product implementation or complete R13 pre-execution approval.

The existing execution restrictions remain binding: **no SSH, target-host
inspection or mutation, database operation, destructive drill, `--execute`,
armed real process boundary or materializer, execution of a generated vector,
deployment, migration `0014`, cutover, OD-62 ruling or Package 5.1+ work**.
Local synthetic tests using recording boundaries, stub PostgreSQL clients and
temporary Git repositories are permitted. Every PostgreSQL client invoked by
a stub test must remain stubbed; never fall through to a real client.

## Required reading and worktree discipline

Before planning or editing, read completely:

- `.agents/AGENTS.md`, `docs/implementation-plan.md`, and
  `docs/operations/disposable-test-server.md`;
- the current section of `docs/review/Handover information`;
- the R3 prompt and handback named above, and the preceding R2 prompt and
  handback;
- `docs/review/project-review-remediation-2026-09-07-handback.md`, including
  its execution deviations and undiagnosed pristine-schema failure;
- `infra/postgresql/backup-restore-drill.sh`,
  `infra/postgresql/runtime-grants.sql.tmpl`, the recovery section of
  `docs/operations/database-development.md`, and
  `tests/test_database_backup_restore.py`.

Check `git status --short --untracked-files=all`. Preserve unrelated changes
and untracked files. Do not reset, revert, stage, commit, push, reformat unrelated
files or overwrite earlier prompts/handbacks. Expected implementation edits are
confined to the drill, its tests and recovery documentation. Explain any
necessary expansion before proceeding with it.

## Remaining Blocking finding: zero relations does not mean no schema objects

At review time, the `destroy_attempted` banner says:

> If the baseline itself records relations=0, then the database held no objects
> before the drill … Nothing was lost either way … no data restore is required.

It directs the operator to skip the restore and apply grants. The preceding
matching-diffs branch also declares the schema intact and no recovery required.
The operations guide repeats these claims.

The structural report only checks whether `public` exists and counts its
`pg_class` relations and base tables. **A schema containing only a function
also reports `schema_present=true|relations=0|base_tables=0`.** The function
is represented in `pg_proc`, not `pg_class`, and the table/row inventory does
not observe it either. If DROP commits and recreates `public`, but the client
result is lost, both before/after reports match while the function is gone.
The procedure then skips the restoration that would recover it.

PostgreSQL 16's primary references:

- [pg_class](https://www.postgresql.org/docs/16/catalog-pg-class.html)
  describes relations; it is not an inventory of every schema object.
- [pg_proc](https://www.postgresql.org/docs/16/catalog-pg-proc.html)
  describes routines and their namespaces.
- [DROP SCHEMA](https://www.postgresql.org/docs/16/sql-dropschema.html)
  describes the scope of cascading removal.

### Independent reproduction already performed

Codex imported the existing test helper and changed only its in-memory stub
answers to model a schema containing a function but no relations:

- pre-destruction schema report: `schema_present=true|relations=0|base_tables=0`;
- table/row inventory: empty before and after;
- the existing dropped-state schema report was already zero relations.

For each scenario, Codex ran the real drill through the stub boundary, then ran
both printed report commands against that same stub and compared their outputs
with the retained baselines:

| Scenario | Drill exit | Both reports match | Banner claims no recovery / nothing to lose |
|---|---:|---|---|
| DROP refused, schema intact | 42 | yes | yes |
| DROP applied, result lost | 42 | yes | yes |

This demonstrates the emitted decision's false premise under the modeled
catalog state. **It is synthetic evidence, not a PostgreSQL execution.**

## Required correction

1. Add a regression first that fails against the submitted R3 tree for the
   function-only schema and lost-DROP-result case. Include the refused-DROP
   counterpart. Model whether the function still exists separately from the
   command's exit status and from the relation count; do not merely add another
   assertion requiring a sentence in the banner.
2. Make the recovery decision safe for non-relation schema objects. Either
   capture sufficient evidence to distinguish the supported states, or leave
   this case explicitly unresolved pending operator inspection. A conservative
   stop is acceptable and does not require a new generic schema-recovery engine.
   Adding a function count alone must not become another unqualified claim
   that all schema objects are accounted for; standalone types and other schema
   objects must not be silently classified as absent.
3. Remove every inference that `relations=0` means no objects existed or nothing
   could have been lost. Revisit both the matching-diffs branch and the
   zero-baseline special case. Equal counts are not an object-identity inventory.
   No branch may declare recovery unnecessary or complete beyond what its
   observations establish.
4. Preserve responsibility before DROP and confirmed destruction only after
   success. Preserve the absent/unexpected-state stop and query-failure-as-unknown
   behavior. Do not prescribe restoration over known existing objects or add an
   unconditional DROP, `--clean`, TRUNCATE or other destructive reset.
5. Preserve the confirmed post-restore resume points, checksummed recovery
   artifacts, exact runtime-role handling, explicit zero-role behavior and both
   final verifications. If this correction exposes the same unsupported
   inference in another recovery branch, correct that dependent instruction
   within the same bounded scope and explain it in the handback.
6. Update the operations guide and comments to match the corrected evidence
   contract. State exactly what each report observes, what it cannot establish,
   and where operator resolution is required. Ensure regression tests protect
   truthful decisions rather than making the old false claim mandatory.

Acceptance: after an uncertain DROP, a schema with non-relation objects cannot
be declared intact, empty of all objects, or safely recovered merely because
relation and row-count reports match. A lost object cannot be dismissed as
“nothing to lose.” A genuinely unresolved state remains unresolved without an
automatic recovery mutation.

## Verification constraints

Run permitted focused checks serially against the final tree after inspecting
their fixtures. Do not launch a broad suite hoping to stop before database access.
The documented interpreter is on `oracle-test` at
`/opt/freedom-blades/runtime/venv-web/bin/python`; the no-SSH restriction prevents
using it here. Verify local interpreter availability directly, label any local
fallback accurately and do not install into production runtimes.

Codex independently ran the following against R3 using the locally verified
`/opt/discord-bots/venv-web/bin/python` (Python 3.12.3, pytest 8.4.2), with
`TEST_DATABASE_URL` unset:

- drill/filesystem modules: **185 passed, 11 deselected**;
- `tests/web/test_p3_4_static_assets.py`: **111 passed**;
- shell syntax and diff whitespace checks: passed;
- manifest verification: **28 source hashes, 0 mismatches**.

These figures describe R3, not your corrected tree. The historical local path
is evidence of that run, not the documented default environment.

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
drill. Any database-semantic regression may be written for a later authorized
run but must not execute here. The pristine-schema failure remains unresolved;
do not rerun it or claim synthetic results diagnose it.

Verify every manifest source hash. No evidence-harness production source needs
changing; leave generated artifacts untouched if covered bytes still match.
Never pass a digest to `--execute`. Keep all unconfirmed target facts unconfirmed.
Report unavailable or unconfigured lint/format/type checks accurately.

## Handback and stop

Create `docs/review/project-review-remediation-2026-09-08-r4-handback.md` with:

- the remaining finding, correction, changed files and chosen evidence contract;
- actual pre-fix regression failures and final-tree commands/results;
- function-only intact/lost-result scenarios and the recovery decisions emitted;
- other object kinds considered, observations retained and unresolved cases;
- precise synthetic-versus-PostgreSQL evidence limitations;
- passed, skipped, deselected and not-run checks, interpreters and reasons;
- manifest hash verification and preservation of unrelated work;
- confirmation that execution restrictions and existing package states remain.

Prepend a concise dated pointer in `docs/review/Handover information`, retaining
prior submissions as history. Do not alter roadmap, RAID, decision or gate
records, close findings, accept risks or claim complete R13 approval. Return
to Codex for independent re-review and stop before operational execution.
