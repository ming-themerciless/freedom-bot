# Claude remediation prompt — Package 5.0 evidence harness, pre-execution R2

Work in `/opt/freedom-blades/platform`.

## Authority and required outcome

Peter Duscha authorized the bounded Package 5.0 pre-implementation evidence
harness on 2026-09-02. Codex reviewed the completed R1 scaffolding and returned
two Blocking findings. Remediate only those findings and the directly necessary
tests and documentation.

This prompt authorizes **unprivileged evidence-scaffolding remediation only**.
It does not authorize choosing or provisioning a disposable target, privileged
or mutation-bearing execution, Package 5.0 product implementation, migration
`0014`, a production schema, production mutation, deployment, authority
transition, cutover, OD-62's binding ruling, or Package 5.1+.

Do not ask Peter to name a disposable target during this remediation.
`UNASSIGNED` remains required until Codex accepts R2. Stop after returning the
corrected harness, tests, execution plan and handback for Codex re-review.

Package 5.0 remains `not ready`. Claim no finding, assumption, readiness item
or operational check closed, passed or confirmed.

## Required reading

Before editing, read completely:

1. `.agents/AGENTS.md`;
2. `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. this prompt;
5. `docs/review/phase-5-0-evidence-harness-authorization-draft.md`;
6. `docs/review/phase-5-0-evidence-harness-implementation-prompt.md`;
7. the current evidence-harness execution plan and implementation handback;
8. `tools/phase_5_0_evidence/` in full; and
9. `tests/phase_5_0_evidence/` in full.

Check `git status` first and preserve unrelated work. Do not reset, revert,
stage, commit or push. If controlling documents conflict, stop and identify the
exact passages.

## EH-R2-1 — Blocking: positive-control status is not cross-validated

### Defect

`EvidenceRecord` stores both `positive_control_case_id` and a caller-supplied
`positive_control_status`. Classification trusts that status.
`deserialize_records()` validates each record separately but never resolves
the ID against the other records in the artifact.

An artifact can therefore contain a failed, inconclusive or not-run control
while a dependent record supplies `positive_control_status="passed"` and
classifies as passed. Recomputing from the same duplicated status does not prove
the control's actual result.

### Required correction

Make positive-control status a derived cross-record fact:

- resolve `positive_control_case_id` to exactly one record in the same
  artifact and derive the control status from that record;
- never trust a duplicated serialized status as authority;
- preferably remove `positive_control_status` from the serialized schema; if
  retained for presentation or compatibility, require exact equality with the
  referenced record;
- distinguish controls/reads from cases requiring controls through an explicit
  validated contract, not case-name prefixes or prose;
- reject missing and duplicate case IDs, self-reference, cycles, inadmissible
  control references, and a declared status contradicting the referenced
  record;
- make a dependent negative case inconclusive unless its actual control passed;
  and
- keep status and reason derived, never caller-selected.

Required regressions:

- a passed control permits an otherwise matching dependent case to pass;
- failed, inconclusive and not-run controls make it inconclusive;
- a failed control plus a dependent record claiming `passed` is refused;
- changing only duplicated serialized control status cannot create a pass;
- missing controls, duplicate IDs, self-reference and cycles are refused;
- record order does not affect resolution;
- cross-band or cross-artifact references fail closed unless explicitly allowed
  by the controlled contract; and
- valid round trips survive while tampered artifacts fail closed.

## EH-R2-2 — Blocking: restored PostgreSQL configuration is not reloaded

### Defect

Cleanup reinstalls captured `pg_hba.conf` and `pg_ident.conf`, then continues
without calling `pg_reload_conf()`. PostgreSQL may keep using the harness
authentication rules in memory after the files are restored. Filesystem
restoration alone does not restore effective configuration.

### Required correction

Make restoration of effective configuration explicit and ordered:

- restore both captured files before reloading;
- add an explicit cleanup step invoking `SELECT pg_reload_conf()` after both
  restores and before cleanup can be complete;
- verify reload success; process exit zero alone is insufficient evidence that
  PostgreSQL accepted and activated the restored configuration;
- define a bounded post-reload observation proving the temporary mapping and
  HBA behavior are no longer effective, without exposing configuration or
  credentials;
- treat restore, reload or post-reload verification failure as cleanup state
  S-B and report the effective-configuration risk;
- handle partial setup safely when only one configuration mutation was reached;
- preserve correct reverse dependency ordering for database objects, files and
  identities; and
- keep cleanup non-recursive and bounded to the disposable context.

Do not connect to PostgreSQL, edit configuration, invoke systemd or execute any
command while implementing or testing this change.

Required regressions:

- cleanup restores both files before reload;
- reload precedes steps whose safety depends on restored authentication;
- success requires reload and post-reload verification;
- either restore failing, reload failing or verification failing yields S-B;
- interruption after only one configuration mutation still produces necessary
  restoration and reload;
- rerun evaluation cannot report completion from exit status alone; and
- all tests remain process-, network- and database-free.

## Scope and safety

Expected changes are limited to `records.py`, directly affected band modules,
`cleanup.py`, `plan.py` only if the corrected plan model needs it, focused
evidence-harness tests, the execution plan, the implementation handback, and
this handover when returning control to Codex. Stop before widening to another
production or controlled project-management file.

Preserve these invariants:

- no module executes a process or reaches a socket, HTTP client or database;
- no privileged read or mutation occurs;
- no target is invented or requested; retain `UNASSIGNED`;
- no arbitrary output, configuration content, secret, credential, player data
  or unrelated host fact enters evidence;
- cleanup cannot express recursive or broad deletion; and
- uncertain reloads and unresolved references fail closed.

## Verification

Run serially with the documented interpreters:

```sh
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'
/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/phase_5_0_evidence
/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py
/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
node --test "foundry-module/tests/"*.test.mjs
/opt/discord-bots/venv/bin/python -m compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence
git diff --check
```

The web suite must retain exactly 80 expected permission-matrix skips. Report
all results exactly. Do not run privileged cases to improve coverage or call an
unrun check passed.

## Handback

Add an R2 section to the implementation handback that:

- concedes EH-R2-1 and EH-R2-2 before describing corrections;
- maps every requirement to named code and tests;
- explains any evidence-schema compatibility change;
- reproduces corrected cleanup ordering and the post-reload proof contract;
- retains target `UNASSIGNED`;
- reports exact tests, skips and checks not run;
- confirms no privileged or mutation-bearing command ran;
- claims no finding closed and no readiness consequence; and
- requests Codex independent pre-execution re-review.

Do not update the roadmap, status, RAID, decision register or change log. Stop
after the handback. Do not ask Peter for target selection or execution
authorization.
