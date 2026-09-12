# Claude remediation prompt — Package 5.0 evidence harness, pre-execution R10

Work in `/opt/freedom-blades/platform`.

## Authority and required outcome

Peter Duscha accepted Codex's recommendation on 2026-09-06, recorded in
package-plan §2.12.2 and change-log **C-P5.0-AG**. Codex's independent R9 review
closes **EH-R8-2** and **DS-R8-2**. Concrete-plan conflict **C-1** is also ruled:
the harness may create and later remove the exact disposable target root it
owns, as well as its descendants, after all existing `DisposableTarget`
validation succeeds. Cleanup remains non-recursive `rmdir`; an unexpected
non-empty root must leave reported residue, never trigger recursive deletion.

Resolve the remaining concrete-plan conflicts **C-2, C-3, C-4 and C-5** with
the smallest explicit, reviewable mechanisms. The required result is a fully
specified concrete plan and review manifest with no unresolved items and
`executable: True` on paper. That state is **not permission to execute it**.

This prompt does **not** authorize `--execute`, an armed real process boundary,
execution of a generated vector, SSH, host inspection, privileged or
mutation-bearing commands, mutation of `oracle-test`, execution of the
destructive backup/restore drill, Package 5.0 product implementation, migration
`0014`, deployment, cutover, OD-62's binding ruling, or Package 5.1+ work.
Package 5.0 remains `not ready`; P5.0-R5 remains Blocking.

## Required reading and worktree discipline

Before editing, read completely `.agents/AGENTS.md`,
`docs/implementation-plan.md`, `docs/operations/disposable-test-server.md`,
`docs/review/Handover information`, this prompt, the R9 prompt and handback,
package-plan §2.12–§2.13, and every file under
`tools/phase_5_0_evidence/` and `tests/phase_5_0_evidence/`. Check `git status`
and preserve the complete dirty worktree. Do not reset, revert, stage, commit,
push or alter unrelated files.

Treat the current generated plan and manifest as review inputs, never as
authority. Do not pass either digest to `--execute`.

## C-1 — preserve the ruled target-root boundary

Preserve `root_or_contained_path()` only for the exact target-root creation and
reversal operations already identified. Add or retain regressions proving:

- `/`, `/var/lib`, the repository root, production paths, shallow paths,
  unresolved variables, globs, metacharacters, sibling paths and `..` escapes
  remain refused;
- ordinary mutation paths still require containment;
- the only root cleanup vector is non-recursive `rmdir`; and
- unexpected content causes visible cleanup residue rather than deletion.

Do not generalize the exception or add another cleanup primitive.

## C-2 and C-3 — reviewed case program and symlink operation

Provide one narrowly scoped, source-reviewed probe/case program if that is the
smallest mechanism. It may implement only the operations already required by
the package-plan cases: exact `open` flag combinations, `pwrite`, `ftruncate`,
`rename`, `unlink`, `symlink`, `statvfs`, `FS_IOC_GETFLAGS`,
`FS_IOC_SETFLAGS`, bounded identity/status observations, and the Stage-4 target
operation. Refuse unknown verbs, wrong arity, relative paths and targets outside
the validated disposable root. Do not invoke a shell and do not admit a general
filesystem utility such as `ln` merely to obtain one operation.

The program's complete source, deterministic build/materialization procedure,
installed bytes and digest must be reviewable and covered by the manifest.
Use only repository-controlled source and an already-declared local toolchain;
no network access or downloaded/precompiled opaque binary. If satisfying this
requires adding a new trusted runtime, compiler assumption, broad executable or
policy choice, stop and return the exact decision and impact instead of
silently enlarging the trusted computing base.

Every command vector must name the exact program, verb, flags and absolute
validated paths. Preserve the positive controls and errno attribution: a case
must become `inconclusive`, not pass, when its prerequisite/control or asserted
identity is absent or wrong.

## C-4 — exact reviewed configuration materialization

Implement a bounded file-materialization mechanism for only the reviewed
synthetic `pg_hba.conf` and `pg_ident.conf` bytes required by the disposable
band. Pin each destination, byte sequence, owner, group, mode and content digest
in the plan and manifest. Destinations must be beneath the validated disposable
PostgreSQL configuration directory, captured before mutation and restored or
removed by the already-reviewed cleanup model.

Do not add a general write-file interface, shell redirection, heredoc, host-file
read or production configuration path. Refuse any content/digest mismatch,
unreviewed destination, existing-object type mismatch or incomplete capture.

## C-5 — late-bound disposable identities

Late-bind only the four exact disposable names the current unresolved items
identify. Resolve each with exact NSS lookup immediately before the dependent
step, require exactly one result, validate the expected name and numeric form,
and substitute only the reviewed uid/gid fields. Refuse every other symbolic
name, missing/duplicate lookup, malformed number and any vector change outside
the declared substitution sites.

The review manifest must pin the symbolic vector, the permitted binding sites
and the revalidation rule. The executor must revalidate the final absolute
vector after substitution and before process creation. Do not consult the host
during dry-run generation or tests; use injected/stubbed lookup results.

## Safety, tests and generated artifacts

Keep the closed R9 behavior intact: canonical explicit group inverses,
two-way membership consistency, exact-one NSS classification, fixed safe-launch
classifications, guaranteed cleanup, and the corrected backup-drill wording.
Do not reopen or broaden those changes.

Add focused negative tests for every new parser, operation, materialized byte
set and late-binding site. No test may start a real privileged process, read the
host account/configuration databases, alter filesystem flags, invoke systemd,
SSH, or touch `oracle-test`. Test generated vectors and executor behavior through
the existing inert/stubbed boundaries.

Regenerate the concrete plan and review manifest from covered sources. Generate
each twice and compare byte-for-byte; independently re-hash every covered source.
Never hand-edit a generated artifact. The final dry run should report zero
unresolved items and `executable: True`, while no executor is invoked.

Run serially:

```sh
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'
/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/phase_5_0_evidence
/opt/discord-bots/venv/bin/python -m pytest -q -rs \
  tests/test_database_backup_restore.py tests/test_filesystem_layout.py \
  --deselect=tests/test_database_backup_restore.py::test_the_drill_accepts_an_explicit_unix_socket_directory \
  --deselect=tests/test_database_backup_restore.py::test_backup_and_restore_round_trip_preserves_data \
  --deselect=tests/test_database_backup_restore.py::test_the_drill_leaves_the_runtime_roles_privileges_intact \
  --deselect=tests/test_database_backup_restore.py::test_the_drill_fails_when_the_privilege_state_is_not_restored \
  --deselect=tests/test_database_backup_restore.py::test_the_drill_preserves_pristine_schema_ownership_and_privileges \
  --deselect=tests/test_database_backup_restore.py::test_the_drill_fails_when_schema_privileges_are_not_restored \
  --deselect=tests/test_database_backup_restore.py::test_the_drill_emits_recovery_instructions_with_checksum_verification_on_failure
/opt/discord-bots/venv-web/bin/python -m pytest -q \
  tests/phase_5_0_evidence tests/web/test_p3_4_static_assets.py
/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py \
  --deselect=tests/test_database_backup_restore.py::test_the_drill_accepts_an_explicit_unix_socket_directory \
  --deselect=tests/test_database_backup_restore.py::test_backup_and_restore_round_trip_preserves_data \
  --deselect=tests/test_database_backup_restore.py::test_the_drill_leaves_the_runtime_roles_privileges_intact \
  --deselect=tests/test_database_backup_restore.py::test_the_drill_fails_when_the_privilege_state_is_not_restored \
  --deselect=tests/test_database_backup_restore.py::test_the_drill_preserves_pristine_schema_ownership_and_privileges \
  --deselect=tests/test_database_backup_restore.py::test_the_drill_fails_when_schema_privileges_are_not_restored \
  --deselect=tests/test_database_backup_restore.py::test_the_drill_emits_recovery_instructions_with_checksum_verification_on_failure
/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
node --test "foundry-module/tests/"*.test.mjs
/opt/discord-bots/venv/bin/python -m compileall -q \
  tools/phase_5_0_evidence tests/phase_5_0_evidence
/opt/discord-bots/venv/bin/python -m tools.phase_5_0_evidence.execution.cli
git diff --check
```

The seven database cases are deselected by authority, not passed or silently
skipped. Do not run them.

## Handback

Add a dated R10 section at the top of the implementation handback and preserve
all earlier history. Update `docs/review/Handover information` to return R10 to
Codex. Identify every changed file; map C-1 through C-5 to implementation and
named tests; state the exact generated counts/digest; report only checks actually
run; explicitly say no vector, host or destructive drill ran; and claim no
finding, assumption, evidence check or gate closed.

Then stop. A separate independent Codex pre-execution review and explicit later
maintainer authorization are required before any execution.
