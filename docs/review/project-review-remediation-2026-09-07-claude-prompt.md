# Claude remediation prompt — project review, 2026-09-07

Work in `/opt/freedom-blades/platform`.

## Scope and authority

Remediate the three findings below from Codex's review of the pending worktree.
This is a bounded correction of the backup/restore drill and evidence capture,
not Package 5.0 product implementation or a complete R13 gate review. The IDs
below identify this review's findings; they do not replace earlier finding IDs.

Preserve the current R13 implementation and every previously established
security boundary. Package 5.0 remains `not ready`; P5.0-R5 remains Blocking.
No prior finding, assumption, decision or gate is closed by this prompt.

The current pre-execution restrictions remain binding: no `--execute`, armed
process boundary or materializer, execution of a generated vector, SSH, target
host inspection or mutation, database operation, destructive drill, deployment,
migration `0014`, cutover, OD-62 ruling or Package 5.1+ work. Local synthetic
tests using recording boundaries or stub PostgreSQL clients are in scope.

## Required context and worktree discipline

Read the following before editing:

- `.agents/AGENTS.md`, `docs/implementation-plan.md` and
  `docs/operations/disposable-test-server.md` completely;
- the current section of `docs/review/Handover information`, the R13 remediation
  prompt and R13 implementation handback;
- `infra/postgresql/backup-restore-drill.sh`, `runtime-grants.sql.tmpl` in the
  same directory, the recovery section of
  `docs/operations/database-development.md`, and their tests;
- `tools/phase_5_0_evidence/capture.py`, `expectations.py`, the execution
  boundary and executor, and the tests exercising those paths.

Check `git status` and preserve all existing modifications and untracked files,
including the live-bot skills fix and the updated agent instructions. Do not
reset, revert, stage, commit, push or reformat unrelated work.

## PR-20260907-1 — Blocking: recovery omits runtime table grants

The `on_exit()` recovery instructions run `pg_restore --no-privileges` and then
apply `schema-grants.sql`. That file restores schema ownership and schema ACLs
only. Unlike the successful drill path, the recovery path never restores runtime
table grants. The operations guide repeats the incomplete procedure. A recovered
database can contain every row while the application role cannot use its tables.

Required correction:

1. Make the printed recovery procedure and operations guide include the runtime
   grant restoration that the normal path requires, using the exact validated
   role identity determined before destruction.
2. Ensure any artifacts needed for that recovery survive the failure, are named
   in the recovery instructions, and have checksum verification where applicable.
   Do not require the operator to reconstruct the role from the now-empty
   database or remember an unstated manual step.
3. Include verification of restored privileges before declaring recovery
   complete. Preserve the existing schema-owner/ACL restoration and normal
   drill privilege checks.
4. Handle the zero-runtime-role case explicitly. Keep recovery instructions
   accurate about their prerequisites and failure point; do not present rerunning
   the destructive drill as a way to recover its lost state.

Add regression coverage for a failure after schema destruction but before grant
restoration. Use stub clients to demonstrate the actual emitted recovery sequence
includes table grants and verification, in order. A test that only searches for
the words `schema-grants.sql` does not establish this behavior. Add or extend a
real PostgreSQL regression for a later authorized run, asserting runtime access
and privilege state after following the recovery procedure; do not execute it
under this prompt.

## PR-20260907-2 — Blocking: role validation changes SQL identity

The role parser trims surrounding whitespace and accepts uppercase letters,
then substitutes the result into unquoted SQL. PostgreSQL preserves the case
and whitespace of quoted role names in its catalog. Thus `MixedCase` becomes
`mixedcase` in SQL, and ` padded_role ` becomes `padded_role` before SQL is even
built. Both inputs pass the current guard and reach `DROP SCHEMA`.

Codex reproduced this with `run_drill_against_stubs()`:

| Grantee returned by the stub | Result | Rendered grant |
|---|---|---|
| `MixedCase` | drop reached | `GRANT USAGE ON SCHEMA public TO MixedCase;` |
| ` padded_role ` | drop reached | `GRANT USAGE ON SCHEMA public TO padded_role;` |

The stub exits successfully because it does not parse SQL. On a real database,
grant restoration can fail after destruction or grant the wrong existing role.

Required correction:

1. Preserve the exact catalog identity. Do not trim or normalize role names.
2. Prefer a narrow pre-destruction refusal for names outside the supported role
   contract. If supporting quoted names instead, quote identifiers correctly
   throughout SQL generation and safely handle template substitution. Do not
   confuse shell quoting with SQL identifier quoting.
3. Check keyword/special-role spellings as well as character syntax: a regular
   expression alone does not prove an identifier has its literal meaning in SQL.
4. Preserve multi-role refusal and the valid zero-role and ordinary lowercase
   runtime-role paths. Do not silently discard a whitespace-only catalog record
   as though it were an empty query result.

Add regression-first stub tests for mixed case, leading/trailing whitespace,
whitespace-only names, SQL keywords/special role names, and the two existing
supported runtime names. Unsupported inputs must refuse before any drop or
restore, without a recovery banner. Keep the valid path as a positive control.
Cover the chosen SQL identity behavior in a database test for later execution.

## PR-20260907-3 — Important: capture discards malformed evidence

`capture._case_observations()` skips a line when it has no `=` separator or its
key is outside the policy's key set. The semantic contract then receives only
the remaining valid pairs and accepts them. Its unexpected/malformed observation
checks therefore cannot detect these defects in real process output.

Codex reproduced all three as accepted by constructing an E1 contract with
synthetic uid/gid/group values, serializing `expected_observations()`, and passing
the text through `sanitize(CASE_IDENTITY, text)` followed by `contract.check()`:

- the valid observation;
- the same observation plus `unexpected_key=unexpected_value`;
- the same observation plus `malformed-output-line`.

Required correction:

1. For `CASE_IDENTITY` and `CASE_RUNTIME`, make unexpected keys and malformed
   nonblank lines produce a fixed safe refusal marker or equivalent typed
   capture failure. Never preserve arbitrary unexpected text in the artifact.
2. Keep well-formed observations accepted, including normal line termination.
   State the blank-line policy explicitly.
3. Preserve duplicate-key refusal, value-shape checks, bounded capture,
   redaction, and the complete runtime and eight identity contracts.
4. Verify the complete raw-output → capture → executor path. Do not merely
   inject an unexpected tuple directly into `ObservationContract.check()`.
5. A malformed runtime or identity observation must remain unsatisfied and
   prevent dependent operations from reaching the recording process boundary.
   Cleanup must retain its existing behavior for mutations already reached.

Do not broaden unrelated capture policies merely because they share the parser.
Preserve the interpreter vector, closed verbs, executable allowlist, identity
binding sites, materializer and arming rules, root boundary, and bounded ctypes
exception. Leave all unconfirmed interpreter/E7 target facts unconfirmed.

## Verification and generated artifacts

Add regressions first, record their pre-fix failures, then make the smallest
corrections and run the permitted focused suites serially.

Follow the updated `.agents/AGENTS.md` for environment selection: the repository
is `/opt/freedom-blades/platform`; the documented test interpreter is
`/opt/freedom-blades/runtime/venv-web/bin/python` on `oracle-test`. Do not copy the
historical `/opt/discord-bots/` interpreter paths from old handbacks. This prompt
retains the no-SSH restriction, so those remote commands are not executable under
this authority. Run only tests supported by an available permitted local
environment, without installing into a production runtime. If unavailable,
complete the edits, static review and handback, and report the test execution
dependency explicitly rather than claiming a pass or bypassing the restriction.

The verification inventory is:

- complete synthetic `tests/phase_5_0_evidence`;
- non-destructive backup/layout tests with the seven destructive integration
  cases identified by name and explicitly deselected, as in R13;
- affected web structural/static-asset checks where dependencies are available;
- Foundry Node tests;
- compilation of changed Python and `git diff --check`;
- full bot/web and new PostgreSQL recovery/identity tests only in a later
  authorized environment; record these as not run when blocked here.

Regenerate the concrete plan and review manifest through their existing inert
generation commands because capture is a covered source. Generate each twice,
compare bytes, and independently re-hash every covered source. Do not hand-edit
generated artifacts. Follow existing versioning rules and report the new digest
as review material only. Never pass any digest to `--execute`.

The dry-run plan must retain zero unresolved design conflicts. Structural
`executable: True` does not supply execution authority or confirm target facts.

## Handback and independent review

Create `docs/review/project-review-remediation-2026-09-07-handback.md` containing:

- each finding, its correction, changed files and any remaining limitation;
- pre-fix failing evidence and actual post-fix results;
- recovery artifacts, exact recovery procedure and privilege verification;
- accepted/refused role-name behavior and proof of refusal before destruction;
- end-to-end capture/refusal evidence for runtime and identity observations;
- generated-artifact versions, digest and reproducibility evidence;
- exact commands, interpreters, passed/skipped/deselected counts, and checks
  not run with their reasons;
- confirmation that unrelated changes and execution restrictions were preserved.

Add a short dated pointer at the top of `docs/review/Handover information` to
this handback, retaining the prior R13 submission as review history. Do not alter
roadmap, RAID, decision or gate records, close findings, or imply that R13 has
received a complete independent approval. Return to Codex for re-review of these
three corrections and any remaining pre-execution review requirements.
