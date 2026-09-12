# Claude remediation prompt — Package 5.0 evidence harness, pre-execution R11

Work in `/opt/freedom-blades/platform`.

## Authority and required outcome

Peter Duscha accepted Codex's recommendation on 2026-09-06, recorded in
package-plan §2.12.2 and change-log **C-P5.0-AH**: resolve R10 conflict **C-2
with Option B**, an explicitly named Python interpreter in every reviewed
case-program vector.

Implement the bounded case program, its dependent C-3 symlink operation and C-5
late binding. Preserve the accepted C-1 root boundary and R10 C-4 configuration
materializer. The required result is a fully specified dry-run concrete plan
and review manifest with no unresolved items and `executable: True` on paper.
That state is **not permission to execute it**.

This prompt does **not** authorize `--execute`, an armed real process boundary
or materializer, execution of a generated vector, SSH, host inspection,
privileged or mutation-bearing commands, mutation of `oracle-test`, database
operations, the destructive backup/restore drill, Package 5.0 product
implementation, migration `0014`, deployment, cutover, OD-62's binding ruling,
or Package 5.1+ work. Package 5.0 remains `not ready`; P5.0-R5 remains Blocking.

## Required reading and worktree discipline

Before editing, read completely `.agents/AGENTS.md`,
`docs/implementation-plan.md`, `docs/operations/disposable-test-server.md`,
`docs/review/Handover information`, this prompt, the R10 prompt and R10
handback, package-plan §2.12–§2.13, and every file under
`tools/phase_5_0_evidence/` and `tests/phase_5_0_evidence/`. Check `git status`
and preserve the complete dirty worktree. Do not reset, revert, stage, commit,
push or alter unrelated files.

Treat every existing generated plan and manifest digest as superseded review
input, never as execution authority. Do not pass any digest to `--execute`.

## C-2 — explicit, isolated Python case-program runtime

Use the Python 3.12 interpreter documented for `oracle-test`. Every generated
case-program argument vector must explicitly name the interpreter as `argv[0]`,
then `-I`, `-S`, the absolute case-program path beneath the validated disposable
root, and the exact reviewed verb and arguments. Do not depend on a shebang and
do not compile on the target.

Add the interpreter only through a dedicated case-program vector validator. Do
not make arbitrary Python commands members of the general command surface. The
validator must admit exactly:

- the one approved absolute interpreter path;
- flags exactly `-I -S`, in that order, with no `-c`, `-m`, interactive or
  environment-derived code path;
- the one case-program path strictly inside the validated disposable root;
- one verb from the already-required closed operation vocabulary; and
- each verb's exact arity, flags and absolute target positions.

Unknown verbs, additional interpreter flags, omitted isolation flags, reordered
prefixes, relative paths, targets outside the disposable root, arbitrary script
paths and trailing arguments must be refused before process creation and again
by the case program.

The case program may implement only the operations already required by the
package-plan cases: exact `open` flag combinations, `pwrite`, `ftruncate`,
`rename`, `unlink`, `symlink`, `statvfs`, `FS_IOC_GETFLAGS`,
`FS_IOC_SETFLAGS`, bounded identity/status observations and the Stage-4 target
operation. It must not invoke a shell, execute another program, access the
network, import a database driver, accept arbitrary paths or provide a general
file-operation interface. Use no third-party package and no site initialization.

Keep source bytes equal to installed bytes. Cover the complete source and its
installation digest in the review manifest. Do not use generated or downloaded
binary code.

## Interpreter preflight and evidence boundary

Preflight must record and validate, before any dependent case can pass:

- the interpreter's exact absolute path;
- Python major/minor version `3.12`;
- SHA-256 of the interpreter executable bytes; and
- the fact that the effective vector includes `-I -S` and imports no
  third-party distribution.

The expected executable digest must be a reviewed target fact, not learned and
trusted from the same execution being judged. Keep it out of generic vector
permission logic. A missing interpreter, changed path, wrong version, digest
mismatch, unusable isolated mode, or third-party import makes dependent evidence
`inconclusive` and prevents a pass. Report only safe fixed classifications.

Do not claim that hashing the interpreter covers the operating system, dynamic
loader, shared libraries or standard library. State those as disposable-host
prerequisites consistent with the other distribution executables already used
by the harness. If implementation reveals that a stable expected interpreter
digest cannot be established without inspecting or mutating the host, stop and
return that exact dependency; this prompt grants neither action.

## C-3 — symlink through the reviewed case program

Implement the existing `symlink` verb in the case program and use it only for
the reviewed disposable `journal/current` link. Require an absolute link path
inside the disposable root and the exact reviewed relative generation target;
refuse absolute targets, `..`, separators or any target other than the generated
name the plan expects. Declare the mutation before execution and preserve the
existing cleanup and residue state machine. Do not add `ln` or another general
filesystem executable.

## C-5 — exact late binding

Late-bind only the four exact disposable names already identified by R10.
Resolve each through the injected NSS boundary immediately before the dependent
step, require exactly one result, validate the expected name and numeric form,
and substitute only the reviewed uid/gid fields. Refuse every other symbolic
name, missing or duplicate lookup, malformed or negative number, overflow, and
any vector change outside declared substitution sites.

Pin the symbolic vector, permitted binding sites and revalidation rule in the
manifest. After substitution, revalidate the complete final vector—including
the Option-B interpreter prefix and case-program grammar—immediately before
process creation. Dry-run generation and tests must use injected results and
must not consult host NSS.

## Safety and regression requirements

Preserve without weakening:

- C-1's exact-root-only exception and non-recursive cleanup;
- C-4's two-file closed materialization table, destination checks, digest
  checks, capture-before-write rule and restoration path;
- all R9 identity/group consistency and backup-drill corrections;
- default inert process and materializer boundaries;
- complete mutation declarations, cleanup derivation and residue reporting;
- positive controls, errno attribution and `inconclusive` outcomes; and
- the rule that no generated artifact or digest is execution authority.

Add focused positive and negative tests for the interpreter prefix, exact
digest/version preflight, isolated import behavior, case-program verb grammar,
every operation, symlink target restrictions, source/install-byte identity,
late-binding sites, final-vector revalidation and all fail-closed outcomes.
Tests must not start a real privileged process, read host accounts or PostgreSQL
configuration, alter flags, invoke systemd, use SSH or touch `oracle-test`.

Update `test_no_execution.py` so the new source remains inside the intended
review/execution tiers and so forbidden subprocess, shell, network and
third-party-import surfaces remain mechanically checked. Do not relax a guard
merely to make the new program pass it; introduce the smallest explicit case
for the ruled vector shape.

## Generated artifacts and verification

Regenerate the concrete plan and review manifest from covered sources. Generate
each twice and compare byte-for-byte; independently re-hash every covered
source. Never hand-edit generated artifacts. Report the new digest as review
material only. The final dry run must have zero unresolved items and
`executable: True`, while neither executor nor materializer is armed.

Run serially with the documented interpreters and exported
`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'`:

1. the complete `tests/phase_5_0_evidence` suite under bot and web test
   interpreters;
2. the non-destructive backup/layout selection, with the same seven destructive
   database cases explicitly deselected as R10;
3. the complete bot suite with those same seven cases deselected;
4. the complete web suite, reporting the expected skip count;
5. Foundry's Node test suite;
6. `compileall` for changed Python modules under both interpreters; and
7. `git diff --check`.

Do not run a destructive case to improve a total. Report exact commands,
passes, skips and deselections from the final tree.

## Required R11 handback and stop

Update `docs/review/phase-5-0-evidence-harness-implementation-handback.md` with
a new R11 section and make `docs/review/Handover information` point to it. The
handback must state:

- how Option B is enforced at planning, manifest and immediately-before-exec
  boundaries;
- the exact interpreter prerequisite and what its digest does and does not
  cover;
- the complete case-program verb/path grammar;
- C-3 and C-5 implementation and cleanup behavior;
- changed files and generated-artifact digest;
- exact final verification results;
- every unrun privileged or destructive check;
- confirmation that nothing was executed or mutated; and
- any judgement call, residual or newly discovered dependency.

Then stop for Codex's separate independent pre-execution review. Do not execute
the plan and do not ask Codex to infer execution authority from a clean review.
Only a later explicit maintainer authorization may permit the disposable-server
evidence run. OD-62 remains open until the required operational evidence and
independent review exist.
