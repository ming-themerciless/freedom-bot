# Claude — complete lifecycle remediation, September 11 R3

Date: 2026-09-11. Direction: C-P5.0-LAB-1, reserved disposable laboratory.
Review: [project-review-2026-09-11-r3.md](project-review-2026-09-11-r3.md).

## Assignment and finish line

Peter agreed to focus the next pass on one complete lifecycle: initialization,
admission, operation, crash, recovery and reuse, with tests reading the actual
stored model records. Address PR-20260911-R3-1, -2 and -3 together, then return
one consolidated submission to Codex. Do not ask for the same bounded local
remediation authorization again.

The deliverable is a coherent runner contract r4 plus a connected, bounded
synthetic lifecycle model and pure validation repairs. A successful scenario
must write its record, read and parse those bytes through the shared validator,
perform injected effects, publish completion, and admit a successor from stored
evidence. A failure scenario must follow that same path through interruption,
restart and recovery. Separate helper tests remain useful but cannot substitute
for these connected scenarios.

Do not implement a real filesystem writer, privileged mechanism, lock adapter,
host runner or operational integration. Do not reopen architecture selection,
build a general scheduler or expand the product scope. VM work remains deferred;
ADR 0011 remains Proposed. Design review and any required maintainer permission
decisions precede operational implementation.

## Required context and allowed edits

Work in `/opt/freedom-blades/platform`. Read `.agents/AGENTS.md` completely;
the implementation plan's reading map, §§0, 16, 20, relevant Phase 5 and testing
requirements; the active handover; and the disposable-server document and its
restriction banner. Then read:

- the R3 review in full, including the recommendations on earlier findings;
- `project-review-remediation-2026-09-11-r2-handback.md` and runner contract r3;
- the reserved-laboratory direction and affected package-plan §2.13 contracts;
- `reservation.py`, `lifecycle_storage.py`, `durability_model.py`, their tests,
  structural guards, and the manifest/non-executing generation contracts;
- the actual interfaces and entry points the proposed protocol would serve.

Check Git status and preserve unrelated work. Allowed implementation is limited
to pure lifecycle decision/record validation, bounded in-memory storage and effect
models, their regressions, necessary structural/manifest declarations and
non-executing artifact regeneration. A parser of supplied bytes is allowed; a
reader of live host state is not. Prefer extending the existing model modules.
Explain any new module's concrete responsibility and consumer.

## 1. Specify one protocol before patching individual cases

Write `phase-5-0-reserved-laboratory-runner-contract-r4.md`, marked **submitted
for technical review, not accepted and not implemented**, superseding r3. Make
it the complete proposed contract, with retained ownership/recovery operation
tables, revised lifecycle rules, exact interfaces, permissions and test matrix.
Preserve r3 and earlier handbacks with dated errata rather than silently changing
their historical conclusions.

Provide one transition/publication table covering every phase from initial
provisioning to reuse. For each transition identify the actor, required lock
custody, bytes read/written, identity binding, file and directory barriers,
permitted effects, uncertain outcome, restart observation and recovery owner.
State the reader/writer order under the cooperative lock. Include failed release
publication and interrupted operator recovery as well as admission failures.

Recommend durable in-progress/completion accounting for all seven participants
that can leave relevant effects. Keep a single lifecycle admission rule, with
operation-specific completion and recovery evidence. If proposing an exemption,
justify it with a concrete containment/completion contract and a falsifiable
test; calling a run “not a reservation” is insufficient. Resolve the permissions
implications in the proposal rather than pretending ordinary users can write
the current root-owned record. Any new writer, helper or authority remains
proposed and unbuilt pending review and maintainer decision.

## 2. Close the publication/restart gap — R3-1, Blocking

Reproduce failure after the first-use record rename but before its directory
barrier: initialization reports NOT_DURABLE, the final record is visible, and a
retry reports ALREADY_INITIALIZED. Model a process-only restart that loses the
initializer's memory but retains the filesystem's visible state. Keep power loss
as a distinct event; do not call the model's power-loss operation for both.

Define how a successor under the lock either establishes the required durability
or refuses pending attributable recovery. Specify who can perform that action,
which bytes and parent entry are synchronized, and what happens if it fails.
An existing name or a stored “durable” boolean cannot prove a barrier succeeded
after that record was written. Do not give the modeled participant access to
the test oracle's durable-state map as an observation a real reader could make.

Cover concurrent participant arrival during initialization, process death after
rename, failed barrier and retry, an already valid record, and successful durable
initialization. Trace the same uncertainty through ADMITTED/RUNNING, release and
operator-recovery publication. Recovery must not overwrite a valid prior history
or convert an unknown predecessor into first use. Explain how a partial or corrupt
history refuses instead of selecting an earlier convenient admitting entry.

## 3. Account for every participant's interrupted effects — R3-2, Blocking

Enumerate all seven entry points: bot tests, web tests, Foundry tests,
synchronization, dependency updates, environment reset and harness CLI.
Define each participant's identity, lifecycle writer, lock lifetime, effects,
completion evidence and recovery. Persist the non-reusable state before its
first relevant effect; publish reusable completion only after its conditions
are observed. A free lock or wrapper exit is never completion evidence by itself.

The connected model must include wrapper death with a surviving child or
server-side effect, partial synchronization, interrupted dependency update/reset,
and clean completion. Use injected effects only. For every participant, assert
that an uncertain predecessor blocks every successor, including the harness and
reset, until the specified recovery succeeds. Demonstrate clean completion and
verified recovery admitting a new run without an indefinite accidental dead end.
Preserve quarantine history and reject reuse of a recovered run's own identity.

Do not infer settlement from a stopped client, permit reset to erase unresolved
evidence, kill unknown processes, or turn a deadline into takeover authority.
Name operation-specific proof obligations that require future target evidence.

## 4. Bind stored evidence to admission — R3-3, Important

Carry host and approved target identity through serialization, parsing and the
shared validator for every admitting disposition, including FIRST_USE and
OPERATOR_RECOVERED. Preserve predecessor/run identity and attributable first-use,
release and recovery evidence. Validate the required author, basis/reference and
other required fields instead of dropping them between storage and decision.

Use a bounded, explicit record schema. Refuse malformed, truncated, unsupported,
contradictory, missing-binding and wrong-binding records without normalizing them
into success. State schema/version and history-order rules as needed for this
protocol; do not create a generic event-storage system. Give BINDING_MISMATCH an
enforcing path or explicitly withdraw its unsupported implementation claim.

Add failing-before regressions for the same-host/different-target case and
missing attestation. Successful tests must consume the bytes their initializer
or predecessor wrote; remove the end-to-end claim from tests that instead inject
`environment_reset_history(...)`. Keep such helpers only for clearly labelled
unit tests. Tamper with stored fields and confirm the subsequent reader refuses.

## 5. Consolidated evidence, preserved controls and review preparation

Map each R3 finding to r4 sections and named regressions. For every crash window
in the transition table, state whether implemented in the synthetic model or
still a future implementation check. Assert both blocked effects and successful
controls. Distinguish writer-visible state, reader-visible state, test-oracle
knowledge and durability guarantees. A power loss may retain unsynchronized
changes; model limitations must not turn a possible outcome into a Linux promise.

Verify technical claims against primary open(2), fsync(2), rename(2) and flock(2)
documentation as relevant. Label documented semantics, design inferences, model
observations and unperformed target checks separately. Before handback, trace
the whole lifecycle once from the perspective of a fresh process with no prior
memory. Resolve related defects within this slice together, and report any
remaining dependency explicitly instead of claiming completeness from test counts.

Preserve the positively reviewed R2 contradictory-state repair, usable directory
descriptor design, recovery-parent barrier, corrected post-unlink evidence,
C1 → C2 → C5 ordering and withdrawal of the JNL-47 criterion split. LAB-1 remains
Important and unrepaired, with its labelled reproduction unchanged. EH-R16-1
remains Open; do not weaken real-execution refusal or implement its gated remedy.
Preserve the CRP fix, synthetic skills fixture, sanitized crafting report and
production alias fix. Do not restart the bot.

All three C-7 cases remain unresolved; producer-review claims and missing-coverage
controls remain unchanged; `is_executable=False`; all twelve target facts remain
unconfirmed. The current digest
`55af840fbb28f0ea8ae447e732644c5b2f81dace83f6ccd499f24ebc8864cff2`
and all replacement digests are review input only, never execution approval.

## 6. Restrictions and verification

No SSH, oracle-test synchronization, host inspection/provisioning, dependency
installation, database operation, destructive drill, service change, credential
access, generated-vector execution, `--execute`, or armed real boundary/materializer.
Only local synthetic execution with injected effects is allowed. No stage,
commit, push, reset or history rewrite. No VM expansion, migration 0014, product
implementation, deployment, cutover or Package 5.1+ work. The later Codex target
preflight stays after implementation review; proposed facts are not authorized
collection steps.

Verify fallback interpreters and versions before use. The canonical interpreter
remains `/opt/freedom-blades/runtime/venv-web/bin/python` on oracle-test; the
historical local interpreters below are exceptions for this restricted pass.
Keep TEST_DATABASE_URL unset and run bot/web serially. Run structural checks,
then focused regressions, then complete available non-database suites on the
final submitted tree:

```bash
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_no_execution.py
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_reservation.py tests/phase_5_0_evidence/test_r2_proposal_models.py tests/phase_5_0_evidence/test_feasibility.py tests/phase_5_0_evidence/test_r16_1_ownership_reproduction.py
# Run any additional changed/new lifecycle regression modules here.
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence
env -u TEST_DATABASE_URL /opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
node --test 'foundry-module/tests/'*.test.mjs
git diff --check
```

Run scoped compileall on changed Python and configured format/lint/type checks.
Distinguish unavailable/unconfigured tooling from a pass. Report every skip as
unverified: the database-disabled web run can pass with 1362 skips; the documented
database-enabled baseline is 80. Do not evade the database restriction elsewhere.
Independent R3 baseline: 217 structural and 1657 harness tests passed, zero skips;
other suites were not rerun by that review. These are comparisons, not new-tree
results.

If covered sources change, regenerate through the non-executing CLI twice,
compare bytes, independently recompute all covered hashes and compare installed
artifacts with generated output. Explain coverage-list changes. If none change,
verify existing hashes/artifacts instead. Never hand-edit generated artifacts.

## 7. Handback and stop point

Write `project-review-remediation-2026-09-11-r3-handback.md` containing:

- disposition of all three R3 findings, with r4 sections and tests;
- the complete lifecycle trace, including restart and successor admission;
- pure-code/model changes versus proposed, unbuilt operational mechanisms;
- failing-before/passing-after regressions, connected model evidence and limits;
- exact proposed interface, writer, identity, permission, path, syscall and
  provisioning deltas, with every required approval still pending;
- dated evidence-claim corrections, remaining proof obligations and decisions;
- exact commands/interpreters, results/skips, unperformed checks, manifest
  integrity and the review-only digest.

Update handover, project status and implementation-plan §20 pointers concisely.
Return to Codex for technical re-review of the complete lifecycle. Do not close
findings on the implementer's authority or request implementation approval before
this checkpoint. Package 5.0 remains not ready, P5.0-R5 Blocking, OD-62 Open and
EH-R16-1 Open. Passing tests accepts no risk and advances no operational gate.
