# Claude remediation prompt — Package 5.0 evidence harness, pre-execution R3

Work in `/opt/freedom-blades/platform`.

## Authority and required outcome

Peter Duscha authorized the bounded Package 5.0 pre-implementation evidence
harness on 2026-09-02. Codex's independent review of the current R2 worktree
returned two Blocking findings and one Important documentation finding.
Remediate only those findings and the directly necessary tests and handback.

This prompt authorizes **unprivileged evidence-scaffolding remediation only**.
It does not authorize choosing or provisioning a disposable target, privileged
or mutation-bearing execution, Package 5.0 product implementation, migration
`0014`, production schema or host changes, deployment, authority transition,
cutover, OD-62's binding ruling, or Package 5.1+.

Do not ask Peter to name a disposable target. Keep `UNASSIGNED`. Stop after
returning the corrected harness, tests, execution plan and handback to Codex for
independent pre-execution re-review. Package 5.0 remains `not ready`; claim no
finding, assumption, readiness item or operational check closed or confirmed.

## Required reading and worktree discipline

Before planning or editing, read completely:

1. `.agents/AGENTS.md`;
2. `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. this prompt;
5. `docs/review/phase-5-0-evidence-harness-authorization-draft.md`;
6. `docs/review/phase-5-0-evidence-harness-implementation-prompt.md`;
7. `docs/review/phase-5-0-evidence-harness-remediation-prompt.md`;
8. the current execution plan and implementation handback;
9. `tools/phase_5_0_evidence/` in full; and
10. `tests/phase_5_0_evidence/` in full.

Check `git status` first. Preserve the complete existing dirty worktree; it is
the submission under review. Do not reset, revert, stage, commit or push. If the
controlling documents conflict, stop and identify the exact passages.

## Review evidence to reproduce first

Run the focused suite before editing and record its exact result. Codex ran:

```sh
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'
/opt/discord-bots/venv-web/bin/python -m pytest -q \
  tests/phase_5_0_evidence tests/web/test_p3_4_static_assets.py
```

It produced **35 failed, 309 passed**. The failures include stale pre-R2 test
calls and a cleanup-plan construction failure. Do not treat these as expected
red tests that may remain; the submitted harness suite must be internally
consistent and green before handback.

## EH-R3-1 — Blocking: R2 changed the contract without migrating its tests

### Defect

R2 correctly moved dependent classification from a duplicated control status
to an actual `EvidenceRecord` and introduced explicit `CaseRole`. The existing
tests were not migrated consistently. They still:

- omit required `case_role` when calling `EvidenceRecord.for_case()`;
- pass the removed `positive_control_status` argument;
- pass `control_status=` where band classifiers now require `control=`;
- construct dependent `AccessCase` and `CapabilityCase` values with the default
  `STANDALONE` role; and
- construct `CleanupStep` through the superseded `mutation_id`/
  `absent_statuses` interface.

The focused suite therefore fails before it can prove the R2 security property.
The implementation handback nevertheless records an older **289 passed** result,
which is not evidence about the submitted tree.

### Required correction

Migrate every affected test to the final R2 contract, without weakening either
the tests or the contract:

- every record explicitly declares `CaseRole.CONTROL`, `DEPENDENT`, or
  `STANDALONE` according to the band's controlled case definition;
- a dependent case supplies the actual control record, never a caller-selected
  status;
- every dependent case constructor declares `role=CaseRole.DEPENDENT` and every
  admissible control declares `role=CaseRole.CONTROL`;
- tests of malformed relationships must reach the intended validation rule,
  rather than fail earlier because their fixtures accidentally violate another
  required field;
- cleanup tests use the current `CleanupStep` vocabulary and still prove that
  recursive, wildcard and broad cleanup cannot be represented;
- retain tests proving missing, duplicated, self-referential, cyclic,
  cross-band and inadmissible control references fail closed;
- retain tests proving failed, inconclusive and not-run controls make a
  dependent result inconclusive;
- retain order-independent serialization/deserialization and tamper refusal;
  and
- do not add compatibility aliases that restore caller-controlled status merely
  to make stale tests pass.

Audit all test names and docstrings after migration. A test whose name says it
exercises a failed control must supply a failed control record; one whose name
says it tests missing identity must otherwise be a valid dependent case.

## EH-R3-2 — Blocking: PostgreSQL configuration cleanup cannot be planned

### Defect

`CleanupPlan.for_mutations()` creates a post-reload refusal verification for
each `POSTGRES_CONFIG_LINE`. `_verification_refusal_step()` uses
`mutation.maps_os_user` as `CleanupStep.run_as`. Ordinary configuration
mutations in the suite carry only `file_path`, so `maps_os_user == ""` and
`CleanupStep.__post_init__()` refuses the plan before any restore, reload or
verification ordering can be inspected.

The current data model also permits a configuration mutation to omit the OS
user/PostgreSQL-role pair even though the post-reload proof needs both. This is
an invalid plan state and must not be repaired with a default production
identity or an invented target.

### Required correction

Choose one coherent, explicit contract and apply it everywhere:

- a configuration mutation that requires a post-reload mapping refusal must
  carry a complete validated `maps_os_user` and `maps_postgres_role` pair; or
- the cleanup plan must derive that pair from a separate, explicit, validated
  mapping declaration in the same plan.

In either design:

- incomplete or mismatched mapping metadata fails at mutation/plan validation
  with `PlanRefused` before cleanup-step construction;
- no blank `run_as`, username or role reaches a `CleanupStep`;
- do not default to `foundry`, `postgres`, `freedomcoord`, `freedomsheet`, or any
  production identity;
- restore every reached configuration mutation before one reload;
- reload precedes the positive connection control and each temporary-mapping
  refusal proof;
- partial setup after only one configuration-file mutation still restores what
  was changed, reloads, and performs the applicable bounded verification;
- cleanup completion depends on restore, reload, positive control and refusal
  verification observations, not command exit status alone;
- restore, reload, control or refusal-verification failure yields S-B and names
  the effective-configuration risk; and
- the plan remains non-recursive, idempotent in its documented sense, and
  bounded to the disposable context.

Add focused regressions for a valid complete mapping plan and for every omitted
or half-specified mapping pair. Preserve the R2 tests for ordering, interruption,
reload failure, verification failure and rerun evaluation.

## EH-R3-3 — Important: handback and traceability describe the wrong tree

### Defect

The implementation handback remains titled pre-execution R1, describes schema
version 2 and the removed status-based APIs, and records old passing totals.
The current implementation declares `EVIDENCE_SCHEMA_VERSION = 3` and harness
version `0.3.0-pre-execution`.

### Required correction

Add a clearly dated **R3 remediation section** to the implementation handback.
Preserve prior history, but mark superseded claims as such and make the current
state unambiguous. The R3 section must:

- concede EH-R3-1, EH-R3-2 and EH-R3-3 before describing corrections;
- identify the exact focused pre-fix command and **35 failed / 309 passed**
  result;
- list every changed file and why;
- describe the final `CaseRole` and control-record API;
- explain schema version 3 and compatibility/refusal behavior;
- reproduce the corrected configuration cleanup ordering and mapping contract;
- map every R2 and R3 requirement to named code and tests;
- replace no old number silently: label old totals as superseded and report only
  newly run results as current evidence;
- retain target `UNASSIGNED`;
- confirm no privileged or mutation-bearing command ran; and
- request Codex independent pre-execution re-review while claiming no finding
  closed and no readiness consequence.

Review the execution plan for stale status-based terminology, schema/version
references, cleanup ordering or incomplete mapping declarations and correct only
those directly affected passages. Keep its first and last line exactly **NOT
EXECUTED — CODEX PRE-EXECUTION REVIEW REQUIRED** and keep every executable
placeholder structurally non-runnable.

## Scope and safety

Expected changes are limited to:

- focused files under `tools/phase_5_0_evidence/` needed for the cleanup-plan
  validation defect;
- `tests/phase_5_0_evidence/`;
- the execution plan;
- the implementation handback; and
- `docs/review/Handover information` when returning control to Codex.

Do not alter product application code, migrations, database schemas, deployment
files, roadmap, project status, RAID, decision register or change log. If a file
outside the list is necessary, stop and explain why before widening scope.

Preserve these invariants:

- no module or test executes a process or reaches a socket, HTTP client or
  database;
- no privileged read or mutation occurs;
- no target is invented or requested;
- no arbitrary output, configuration content, secret, credential, player data
  or unrelated host fact enters evidence;
- uncertain reloads and unresolved control references fail closed; and
- cleanup cannot express recursive, unresolved or broad deletion.

## Verification

Run serially against the final tree, with the documented interpreters:

```sh
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'

/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/phase_5_0_evidence
/opt/discord-bots/venv-web/bin/python -m pytest -q \
  tests/phase_5_0_evidence tests/web/test_p3_4_static_assets.py
/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py
/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
node --test "foundry-module/tests/"*.test.mjs
/opt/discord-bots/venv/bin/python -m compileall -q \
  tools/phase_5_0_evidence tests/phase_5_0_evidence
git diff --check
```

Run the bot and web full suites serially; they share `freedom_test`. The web
suite must retain exactly 80 expected permission-matrix skips. Report actual
totals, skips and warnings from this final tree. Do not reuse R1 or R2 totals.
Formatter, linter and type checker remain `not configured`; do not introduce
tooling or claim those checks passed.

If any focused or full suite fails, do not present the harness as remediated.
Report the failure and continue correcting only within this prompt's scope, or
stop and identify the scope conflict.

## Return to Codex

After verification, make `docs/review/Handover information` begin with a short
current handover stating that R3 is submitted for Codex independent
pre-execution re-review. It must retain `UNASSIGNED`, state that no privileged or
mutation-bearing command ran, claim no finding closed, and preserve all
superseded history below it.

Then stop. Do not select a target, request execution authority, execute the
harness, close a finding, recommend readiness, or proceed to Package 5.0
implementation.
