# Claude remediation prompt — project review R2, 2026-09-07

Work in `/opt/freedom-blades/platform`.

## Scope and authority

Remediate the three findings below from Codex's follow-up project review. This
is a bounded correction of the backup/restore drill, its recovery documentation,
and the production-file scope guard. Preserve the previous remediation and the
current R13 evidence harness. This prompt does not authorize Package 5.0 product
implementation or constitute complete R13 pre-execution approval.

The finding IDs below belong to this follow-up review. They do not replace
earlier IDs or close earlier findings. Package 5.0 remains `not ready`;
P5.0-R5 remains Blocking. No assumption, decision, residual risk or gate closes
through this work.

The existing pre-execution restrictions remain binding: no SSH, target-host
inspection or mutation, database operation, destructive drill, `--execute`, armed
real process boundary or materializer, execution of a generated vector,
deployment, migration `0014`, cutover, OD-62 ruling or Package 5.1+ work.
Local synthetic tests using recording boundaries or stub PostgreSQL clients
are permitted. Never let a stub test fall through to a real PostgreSQL client.

## Required context and worktree discipline

Before planning or editing, read:

- `.agents/AGENTS.md`, `docs/implementation-plan.md` and
  `docs/operations/disposable-test-server.md` completely;
- the current section of `docs/review/Handover information`;
- `docs/review/project-review-remediation-2026-09-07-claude-prompt.md` and
  `docs/review/project-review-remediation-2026-09-07-handback.md`, including its
  execution deviations and undiagnosed PostgreSQL drill failure;
- `infra/postgresql/backup-restore-drill.sh`,
  `infra/postgresql/runtime-grants.sql.tmpl`, the recovery section of
  `docs/operations/database-development.md`, and
  `tests/test_database_backup_restore.py`;
- the scope guard and allowlists in `tests/web/test_p3_4_static_assets.py`,
  together with the R13 handback and source inventory establishing which
  evidence-harness files are already in the submitted scope.

Check `git status --short --untracked-files=all`. Preserve existing modifications
and untracked files, including the live-bot skills fix, agent instructions,
prior handbacks, and generated review artifacts. Do not reset, revert, stage,
commit, push or reformat unrelated work. Keep changes within the files and
supporting tests/documentation needed for these findings.

## PR-20260907-R2-1 — Blocking: newline-bearing role identities are still changed

`RUNTIME_ROLE_REPORT="$(detect_runtime_role)"` strips trailing newlines before
the role guard sees the value. The subsequent line reader drops empty lines and
uses newlines as record boundaries, although a quoted PostgreSQL role name may
itself contain newlines. Consequently the guard still validates a different name
from the catalog identity.

Codex reproduced these cases with the existing `run_drill_against_stubs()`
helper. The notation below uses Python string escapes: `\n` denotes an actual
newline inside one role name, not two literal characters.

| One catalog role supplied to the stub | Exit | DROP reached in stub log | Runtime grant artifact |
|---|---:|---|---|
| `"freedom_runtime_test"` | 0 | yes | present, correct positive control |
| `"MixedCase"` | 2 | no | absent, existing refusal preserved |
| `"freedom_runtime_test\n"` | 0 | yes | present, names the wrong role |
| `"\nfreedom_runtime_test"` | 0 | yes | present, names the wrong role |
| `"\n"` | 0 | yes | absent, mistaken for zero roles |

These are stub reproductions, not PostgreSQL executions. Stub success does not
establish that the rendered SQL works; it establishes that the destructive step
was reached with a corrupted identity.

Required correction:

1. Preserve record cardinality and exact identity before deciding whether a
   role is supported. Either validate catalog names before emitting a safe
   representation, or transport them in an unambiguous encoding with strict
   decoding. Do not attempt to repair this only by another regex after lossy
   line splitting or command substitution.
2. Retain the narrow supported-role contract. Unsupported names must refuse
   before DROP or restore; do not broaden support for quoted names merely to
   avoid refusal. Preserve lowercase-name, reserved/special-role and `pg_`
   checks, the multiple-role refusal, and exact handling of zero rows.
3. Refuse unreadable or malformed transport and client failures. Do not infer
   zero roles from missing or invalid data. Report fixed safe failure text,
   without echoing arbitrary catalog-name contents.
4. Add regression-first cases for leading/trailing/embedded newlines,
   newline-only names, multiple line breaks, and a valid role alongside an
   unsupported newline-bearing role. Retain positive controls for zero roles,
   `freedom_runtime` and `freedom_runtime_test`, and existing invalid-name cases.
5. Adapt the stub to the actual new query/output contract. If validation moves
   into SQL, a stub that simply returns the expected refusal marker does not
   prove that SQL correctly classifies names: distinguish transport evidence
   from database-semantic evidence, and add PostgreSQL regressions for a later
   authorized run. Do not execute them now.

Acceptance: no unsupported name becomes a supported name or vanishes as a
record, and every tested unsupported input refuses before destruction without
a recovery-required banner.

## PR-20260907-R2-2 — Blocking: recovery restarts an already completed restore

`on_exit()` prints the same `pg_restore --single-transaction --exit-on-error`
step for every failure while `SCHEMA_DROPPED` is set. That flag remains set
through schema grants, runtime grants and verification. A failure in those
later stages occurs after the data restore has committed. Repeating the printed
restore against those existing objects fails instead of reaching grant repair.

Codex made the stub `psql` fail with exit 42 only when applying
`runtime-grants.sql`. The stub log showed a successful `pg_restore` followed by
the grant failure, but the emitted recovery procedure still began its mutation
steps with the same full restore. The current recovery tests inject failure
before the restore commits and therefore do not cover this branch.

Required correction:

1. Track enough progress to distinguish a failed/not-completed data restore
   from a successfully committed restore followed by grant or verification
   failure. Advance completion state only after the corresponding command
   succeeds. Describe any uncertain outcome honestly rather than treating it
   as known empty or known complete.
2. Emit recovery instructions appropriate to the reached stage. Once data is
   known restored, resume safe grant restoration and verification without
   running the same data restore over existing objects. Do not solve this by
   adding an unconditional DROP, `--clean`, or another destructive reset to
   every recovery path.
3. Preserve the pre-destruction, checksummed dump/schema/runtime grant artifacts,
   exact validated role, explicit zero-runtime-role case, and privilege-loss
   check. Recovery must also verify the data inventory where applicable before
   declaring completion. A verification failure cannot become success merely
   because the restore command previously exited zero.
4. Make the banner accurate at each failure point; do not universally call the
   database empty or partially restored after a known successful data restore.
   Keep the instruction that rerunning the destructive drill is not recovery.
5. Update `docs/operations/database-development.md` to match the emitted paths.
   State prerequisites and the handling of an uncertain restore outcome.
6. Extend the stub boundary with stateful failure injection for restore failure,
   schema-grant failure, runtime-grant failure and verification failure. Assert
   the actual emitted sequence, not just the presence of artifact filenames.
   Demonstrate that the post-restore branch does not repeat data restoration;
   cover the zero-role branch as well.
7. Add or extend real PostgreSQL tests for later authorized execution, following
   the emitted recovery path after a successful restore and an injected grant
   failure. Assert preserved rows, runtime usability and privilege verification.
   Do not run these tests under this prompt.

Acceptance: the documented recovery path can resume from each tested stage
without a redundant data restore or an unrequested destructive reset. Remaining
uncertainty and unexecuted database checks must be explicit in the handback.

## PR-20260907-R2-3 — Important: collapsed untracked directories bypass the scope guard

`test_no_unrelated_production_files_modified()` runs `git status --short`.
Git collapses wholly untracked directories, and the allowlist accepts the
directory entries. The guard therefore does not inspect their individual files.

Codex ran the existing `status_paths()` and `scope_violation()` functions over
both status forms. Default status produced no violation. Status with
`--untracked-files=all` exposed six undeclared files in the current submission:

- `tools/phase_5_0_evidence/binding.py`
- `tools/phase_5_0_evidence/case_runtime.py`
- `tools/phase_5_0_evidence/execution/case_program.py`
- `tools/phase_5_0_evidence/execution/materializer.py`
- `tools/phase_5_0_evidence/expectations.py`
- `tools/phase_5_0_evidence/materialization.py`

Required correction:

1. Enumerate individual untracked files explicitly. Make the production guard
   inspect them rather than relying on a collapsed parent-directory allowance.
   Keep tracked modifications and renames covered.
2. Reconcile the six files against the existing R13 submission and its bounded
   authorization. Add exact file entries with their scope rationale where
   supported; do not treat this prompt as authority for new production modules.
   Remove or render unnecessary the collapsed-directory escape hatch.
3. Preserve separate package/maintenance allowlists and watched prefixes. Do
   not whitelist `tools/`, a harness prefix, or arbitrary descendants.
4. Add a regression exercising discovery through classification: create a
   synthetic temporary Git repository with an untracked nested directory and
   an undeclared source file, then use the actual discovery path to prove it
   is rejected. Do not write synthetic unauthorized files into this worktree.
5. Prove that the reviewed file set passes and an additional undeclared file
   inside the same package still fails. A direct call to `scope_violation()`
   alone does not demonstrate that Git discovery supplies that file.

Acceptance: the guard's result no longer depends on Git collapsing an untracked
directory, and the exact submitted source files are accounted for.

## Verification constraints and required evidence

Add regressions first and record their actual pre-fix failures. Run permitted
focused checks serially against the final tree. Do not run a broad test command
first and rely on stopping it before it reaches a database fixture.

The documented Python environment is on `oracle-test` at
`/opt/freedom-blades/runtime/venv-web/bin/python`; the repository is
`/opt/freedom-blades/platform`. The no-SSH restriction prevents using that
remote environment for this correction. Do not copy historical
`/opt/discord-bots/` paths from prior handbacks or install into a production
runtime. If a permitted local test environment is unavailable, finish the
correction and static evidence and report the execution dependency. Do not
claim a pass or relax an execution restriction to obtain one.

Permitted verification includes:

- synthetic backup-drill regressions with all PostgreSQL clients stubbed;
- scope-discovery tests using a temporary synthetic Git repository;
- affected filesystem/layout and web static checks where dependencies permit;
- the synthetic evidence-harness suite where dependencies permit, preserving
  the strict runtime/identity capture behavior;
- Foundry Node tests, `bash -n`, Python compilation and `git diff --check`;
- configured lint/format/type checks, or an explicit statement of unavailable
  tooling or checks that are not configured.

Explicitly exclude every database-touching test, including the nine previously
deselected cases and any new PostgreSQL regressions. Identify excluded tests
by name in the handback. The previous undiagnosed pristine-schema drill failure
remains unresolved operational evidence unless separately established; do not
re-run it here or present stub success as its resolution. Full bot/web database
suites and disposable-server drills require a later authorized run. Whenever
database suites are eventually run, they must be serial and use the documented
exported socket URL; this prompt does not authorize that run.

Codex's follow-up checks were limited: five role-name stub cases, a post-restore
grant-failure stub, focused capture/contract checks, scope-discovery comparison,
28 matching source hashes, 171 local Foundry tests, shell syntax and diff
whitespace checks. Full Python/PostgreSQL suites were not run. Do not carry any
of these figures forward as results for your changed tree.

No evidence-harness production source needs changing for these findings. If
all covered sources remain unchanged, verify the manifest hashes and leave
generated artifacts untouched. If an unavoidable in-scope change affects a
covered source, explain why, regenerate through the existing inert command
twice, compare bytes, independently re-hash sources, and report the resulting
digest as review material only. Never hand-edit generated artifacts or pass a
digest to `--execute`. Leave all unconfirmed interpreter and E7 target facts
unconfirmed.

## Handback

Create `docs/review/project-review-remediation-2026-09-07-r2-handback.md` with:

- each finding, changed files, correction and remaining limitation;
- pre-fix failures and actual final-tree verification commands/results;
- the role transport/validation contract and pre-destruction refusals;
- the recovery-stage table and exact emitted recovery paths;
- scope-discovery evidence and the reconciled file inventory;
- passed, skipped, deselected and not-run checks, exact interpreters and reasons;
- manifest verification or justified regeneration evidence;
- confirmation that unrelated changes and execution restrictions were preserved.

Prepend a concise dated pointer to that handback in
`docs/review/Handover information`, retaining the prior submission as history.
Do not overwrite either earlier prompt or handback. Do not alter roadmap, RAID,
decision or gate records, close findings, or claim complete R13 approval.
Return to Codex for independent re-review and stop before operational execution.
