# Package 5.0 evidence harness — R13 independent pre-execution review

Date: 2026-09-08  
Reviewer: Codex, Security Reviewer and Independent Reviewer  
Disposition: **Changes requested. Pre-execution approval withheld.**

The user requested the complete R13 pre-execution review, including execution
and cleanup. This review therefore extends beyond the narrow E7 remediation.
It does not authorize execution, host inspection, target-fact collection,
Package 5.0 implementation, migration 0014, deployment or cutover.

Reviewed manifest digest, **review identification only, not execution authority**:

`d91e996977d91bbd6229fa0311df46ff13494611cb6cdd8a4234a077ded9e402`

## R13 disposition

**EH-R12-1 is addressed on implementation review.** The generated plan contains
one direct Option-B E7 observation, P-06, alongside the seven capsh identity
observations. E7 uses the same twelve-key contract, including the existing
bounded PR_GET_SECUREBITS observation. Its ten expected environment values come
from separate reviewed target facts; all remain UNCONFIRMED. Constructor
refusal precedes process execution, and an unsatisfied P-06 stops subsequent
case-program operations. P-05 retains its separate runtime contract.

The placement after installation and runtime validation is reasonable for the
case-program identity assertion. Earlier provisioning is not thereby proved
safe; the findings below address its independent controls. Acceptance of the
E7 correction does not approve the complete harness or close P5.0-R5.

## Findings

### EH-R13-1 — Blocking: cleanup can delete pre-existing and unreached objects

Locations: `execution/executor.py:1015–1032,1060–1075` and
`concrete_plan.py:542–579,639–658` under `tools/phase_5_0_evidence/`.

Once any mutation is attempted, the executor runs the entire declared cleanup
plan. The reached-mutation list is not used to limit reversals. R-02 checks only
whether freedomjournal exists; there is no equivalent complete baseline before
the first mutation for the other accounts, groups, paths, database, role and
unit. A creation returning “already exists” is treated as a possibly reached
mutation and followed by deletion of the existing object.

**Synthetic reproduction:** use the shipped fake-boundary fixture, supply its
synthetic reviewed facts, and make B2-02 (`groupadd --system freedomcoord`)
return 9. Execution stops at B2-02. The recorded reached list contains only
`os_group:freedomjournal` and `os_group:freedomcoord`, but cleanup requests
`groupdel freedomcoord`, the other declared group deletions, and CL-08's
`DROP DATABASE IF EXISTS fb_evidence_p5_0`. No database-creation step ran.
These are requested commands observed at a fake boundary, not real deletions.

**Required correction:** establish ownership of cleanup subjects before making
changes. Refuse pre-existing objects without deleting them; derive the applicable
cleanup from verified baseline and attempted changes, preserving conservative
handling of unknown launch outcomes. Simply filtering to attempted mutation IDs
does not fix the already-exists case. Add stateful regressions for pre-existing
groups/accounts, database/role, unit and files, early failures, and uncertain
creation outcomes. Unreached PostgreSQL configuration must not be restored or
reloaded merely because an OS-group creation was attempted.

### EH-R13-2 — Blocking: failed configuration recovery deletes its recovery inputs

Locations: `execution/executor.py:1042–1120`, generated cleanup CL-01/CL-02 and
CL-15/CL-16; `cleanup.py:600–676`.

The cleanup loop continues through every reversal after a configuration restore
fails. It then deletes both byte-exact pre-change configuration captures. The
result reports S-B, but the files needed to recover the original HBA/identity
configuration have already been removed. The same loss of recovery evidence can
occur when reload or effective-configuration verification fails. This contradicts
the claim that no cleanup step depends on an earlier step's success.

**Synthetic reproduction:** with the satisfying fake run, make CL-01's
configuration restore return 1. Cleanup reports S-B and nevertheless requests
CL-15 and CL-16:

```text
rm --force -- /var/lib/fb-evidence-p5-0/before/pg_ident.conf
rm --force -- /var/lib/fb-evidence-p5-0/before/pg_hba.conf
```

**Required correction:** retain captures and recovery metadata until the
corresponding restoration and effective-configuration checks succeed. Continue
only independent safe cleanup, identify retained recovery inputs explicitly,
and provide a bounded operator recovery procedure. Add restore-, reload- and
verification-failure tests that model file contents/presence, not merely calls or
an S-B classification.

### EH-R13-3 — Blocking: non-identity prerequisites ignore their observations

Locations: `expectations.py:638–659`, `execution/executor.py:574–603,790–836`,
`concrete_plan.py:583–609,689–728,1388–1451`.

Only CASE_RUNTIME and CASE_IDENTITY receive semantic contracts. Other controls
are satisfied by exit status even when their recorded observations contradict
the stated prerequisite. The pure band classifiers are not called by the
execution loop before dependent steps. This affects launching capabilities,
membership, file attributes, mount properties and unit directives; describing
those observations as classified later does not enforce a prerequisite now.

**Synthetic reproduction through the real sanitizer:** return exit 0 for P-01
with `CapBnd: 0000000000000000`, and exit 0 for B2-10 with the group record
`freedomjournal:x:5004:freedomcoord,freedomsheet,fbprobe`. Both steps are marked
satisfied. With the remaining fixture results matching, the run returns
`completed=True` and `artifact_admissible=True`. An empty P-01 observation also
passes. No actual capability or membership was changed or inspected.

**Required correction:** integrate typed, fail-closed checks for each declared
observation-based prerequisite before dependent execution and success
classification. Reuse existing classifiers where appropriate, but actually call
them at the gate. Test missing, unreadable and mismatching observations from raw
synthetic command output through sanitation to the runner, and assert that
dependent commands never reach the boundary. Check capture formats against the
specific producing executable as part of this work.

### EH-R13-4 — Blocking: required evidence cases are absent from the executable plan

Locations: `concrete_plan.py:2008–2098,2321–2330,2368–2378`; package plan
acceptance rows 18–20 and evidence-authorization required sequence steps 5–8.

Band 5 generates seven capsh vectors ending in `identity`, and no capability
matrix operations under those constructed identities. For example, it does not
execute the required E4/E6 comparison of clearing the immutable flag on the
root-owned archive, or E5's flag-clear followed by denied open. Identity
observation is a prerequisite for those experiments, not their result.

Band 7 emits no steps and no unresolved items. Pure comparison functions over
supplied observations do not collect provenance-omission, journal-generation or
recovery evidence, and the CLI has no supplied-observation ingestion stage that
completes this band. Nonetheless `is_executable` is true because the unresolved
tuple is empty, and a scripted run can be classified complete.

**Required correction:** map every required evidence case to its actual
observation-producing steps, controls and classification. Implement the missing
bounded facsimile experiments within authorization, or explicitly report them
as incomplete and seek a separately approved narrower execution scope. No
complete-harness success may be produced with required bands missing. Add
coverage/completeness assertions that check operations and required case IDs,
not just identity names or an empty unresolved tuple.

### EH-R13-5 — Important: the CLI reports an artifact written without writing one

Location: `execution/cli.py:654–663`.

After execution, the CLI prints `artifact written : {outcome.artifact_admissible}`.
It never serializes or writes an execution evidence artifact. The only explicit
output-file paths are the pre-execution manifest and rendered plan. Thus a
successful scripted outcome would say an artifact was written while retaining
neither step observations nor traceable band records on disk.

**Required correction:** distinguish eligibility from completed persistence.
Provide the approved bounded, sanitized evidence-output path and validate its
completeness before claiming a write. Report write failures accurately. Test
that a reported artifact exists, is readable through the record validator, and
contains the required evidence; test failed persistence as well.

## Verification and limits

The documented interpreter is on oracle-test. The active pre-execution
restrictions prohibit SSH and database operations, so checks used the directly
verified **local fallback** `/opt/discord-bots/venv-web/bin/python`, Python
3.12.3 / pytest 8.4.2. `TEST_DATABASE_URL` was unset for every invocation. These
are synthetic results, not the prescribed PostgreSQL-backed bot/web totals or
their expected 80-skip baseline.

Commands run serially:

```sh
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_no_execution.py
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web/test_p3_4_static_assets.py
git diff --check
```

Results: **171 passed**, **1143 passed**, and **111 passed**, respectively, with
no skips; whitespace check clean. The first suite checks the synthetic suite's
execution boundaries. The passing full suite does not cover the reproduced
failures above.

Independent in-memory generation using `build_concrete_plan()`,
`read_covered_sources()`, `ReviewManifest.build()` and `render_plan()` twice
produced identical bytes both times and matched both checked-in generated
artifacts. There are **28 covered sources, 116 command steps, 46 cleanup steps
and zero declared unresolved items**. The latter is a generator result, not
review approval or evidence completeness. No generated file was changed.

The three runtime-logic demonstrations used
`test_executor_cleanup.runnable_plan`, `satisfying`, `runner` and
`harness_fixtures.supply_reviewed_e7_facts`, with `pytest.MonkeyPatch.context()`
supplying the existing synthetic interpreter constants. Scripted overrides were
`CommandResult(exit_status=9, timed_out=False)` at B2-02, then a separate run
with exit 1 at CL-01, then a separate run with the sanitized P-01/B2-10
observations described above. All process and materialization requests went to
the shipped fakes; no real boundary was armed.

No SSH, target inspection, account change, native identity change, generated
vector execution, database query, configuration write/reload, destructive drill,
deployment or production operation ran. The full bot/web database suites and
operational recovery checks were not run. Formatter, linter and type checker
are not configured; no tooling was introduced. Only this review document was
added; implementation, tests, generated artifacts and controlled gate records
were preserved.

## Next review boundary

Return these findings to the implementer for bounded remediation and independent
re-review. Do not collect target facts or execute this digest as the next step.
The two interpreter facts and ten E7 facts remain unconfirmed. Package 5.0
remains not ready, P5.0-R5 remains Blocking, and OD-62 remains Open. The separate
pristine-schema drill failure and PostgreSQL validation of schema-state.sql are
also unaffected by this review.
