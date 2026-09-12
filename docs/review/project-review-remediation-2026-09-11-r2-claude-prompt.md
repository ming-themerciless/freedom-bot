# Claude — bounded remediation of the September 11 re-review

Date: 2026-09-11. Direction: C-P5.0-LAB-1, reserved disposable laboratory.
Review: [project-review-2026-09-11-r2.md](project-review-2026-09-11-r2.md).

## Assignment and boundary

Address PR-20260911-R2-1 through -4 in one consolidated local pass, then return
to Codex for technical re-review. Preserve the reserved-laboratory direction;
VM work remains deferred and ADR 0011 remains Proposed. Do not restart
architecture selection or expand the harness beyond these findings.

Implement the pure lifecycle-validation correction and its regressions. Revise
the proposed runner contract and add bounded synthetic models for its corrected
durability, removal and admission rules. **Do not implement the privileged
mechanism, filesystem writer, lock adapter or operational integrations.**
Design acceptance and any required maintainer permission decisions remain
prerequisites of that implementation.

Before work, read `.agents/AGENTS.md` completely; the implementation plan's
reading map, §§0, 16, 20 and relevant Phase 5/testing requirements;
`docs/review/Handover information`; and
`docs/operations/disposable-test-server.md`, including its restriction banner.
Then read:

- the linked re-review, all four findings and its evidence limits;
- `project-review-remediation-2026-09-11-handback.md` and the submitted
  `phase-5-0-reserved-laboratory-runner-contract-r2.md` completely;
- the reserved-laboratory direction and preceding remediation prompt;
- affected package-plan §2.13 requirements, including Algorithm C, §2.13.2b
  and JNL-47, and the ownership/recovery reviews cited by the contract;
- `reservation.py`, `feasibility.py`, affected cleanup/execution contracts and
  their tests under `tools/phase_5_0_evidence/` and `tests/phase_5_0_evidence/`;
- current status, generated plan, manifest and non-executing generator.

Check Git status and preserve unrelated work. Do not stage, commit, push, reset
or rewrite history. Preserve the CRP fix, synthetic skills fixture, sanitized
crafting report and production alias fix. Do not restart the bot.

## 1. Repair contradictory lifecycle admission — R2-1, Blocking

Add failing regressions before changing the decision code. Reproduce the review's
case with a readable, complete synthetic history, a free observed lock, a complete
inventory, a matching release record and RELEASED disposition: setting
`predecessor_state` to RUNNING or QUARANTINED currently admits.

Validate the lifecycle record as a coherent whole before choosing an admitting
branch. A release record does not override contradictory state. Require the
state, disposition, predecessor identity and attached evidence to agree; reject
missing, unknown or contradictory combinations with useful typed refusals.
Do not silently normalize them into a successful disposition.

Use a table covering RELEASED disposition paired with ADMITTED, RUNNING,
RECOVERING, QUARANTINED, REQUESTED, missing state and the valid RELEASED control.
Retain wrong-host, wrong-target and wrong-reservation release tests. Audit every
other admitting branch as well:

- verified first use must carry no incompatible predecessor or release/recovery
  evidence, and must remain distinguishable from missing history;
- operator recovery must name the predecessor and its recovery evidence
  consistently, permit only a new reservation, and preserve the quarantined
  reservation's history;
- unclassified or malformed lifecycle values must not fall through to admission.

State the accepted combinations explicitly in code/tests and the revised design.
Keep this a pure decision repair over injected observations. Do not add a reader,
storage implementation or host effect to validate the inputs. Preserve omitted
residue refusals, guarded transitions, quarantine behavior and real-execution
gates. Distinguish decision validation from an operationally enforced reservation.

## 2. Correct descriptor and publication durability — R2-2, Blocking

Write `phase-5-0-reserved-laboratory-runner-contract-r3.md`, marked **submitted
for technical review, not accepted and not implemented**. It supersedes r2;
preserve r2 with a dated supersession/erratum notice. Make r3 a coherent complete
contract, including retained operation tables, recovery, privilege inventory,
residuals and tests. Do not leave contradictory old rows authoritative.

For every descriptor, specify its open flags, owner, lifetime, permitted uses
and transfer policy. P2's `fsync(bin_fd)` and restoration's `fsync(pgconf_fd)`
cannot operate on the O_PATH descriptors r2 assigns them. Choose a concrete
usable directory-descriptor design. If separate O_RDONLY descriptors are used,
explain how they are obtained and bound to the intended directories without
reintroducing an unchecked pathname lookup. Include any extra permissions and
arguments in the exact proposed interface delta.

Enumerate the complete durability dependency graph for installation, capture,
recovery-record publication, configuration replacement and lifecycle publication.
In particular, after creating a new recovery `<run-id>` directory, its entry
in the recovery parent must be synchronized before configuration mutation is
permitted. Syncing the child's contents alone does not make that entry durable.
Include required file and containing-directory barriers, their ordering and
their failure dispositions. A read-back/digest check is not a durability barrier.

No first configuration mutation may occur until both recoverable bytes and all
metadata needed to discover and verify them after a crash are durably published.
Preserve held-buffer verification/write binding, destination custody, ordered
multi-file restoration, reload checks, quarantine and independent recovery when
R or executor memory is lost. Account for failure after a restoration rename
but before its directory sync; do not report durable restoration from a rename
alone.

Add a bounded synthetic model with distinct volatile and durable namespace/data
state and explicit descriptor modes. Inject failure at every required barrier.
Verify that pre-mutation failure prevents M1, and that a modeled crash after a
successful capture publication retains discoverable, verifiable recovery inputs.
The old omitted-parent-barrier sequence must fail this property. Include a
positive sequence and invalid-O_PATH-operation control. These are proposal-model
tests, not Linux runtime proof. Specify separately the eventual implementation
checks for actual descriptor modes, filesystem support and crash recovery.

Verify semantics against primary [open(2)](https://man7.org/linux/man-pages/man2/open.2.html)
and [fsync(2)](https://man7.org/linux/man-pages/man2/fsync.2.html) documentation.
Separate documented semantics, design inference, modeled results and unperformed
target verification. Do not run a real filesystem durability drill in this pass.

## 3. Correct post-unlink evidence — R2-3, Important

Correct §1.4.5 and the corresponding proof-matrix rows. The post-check observes
whether a name exists; it cannot establish which inode unlink removed.

Model the exact counterexample: pre-check succeeds for A, A is renamed away,
B is installed at the original name, unlink removes B, and the post-check returns
ENOENT. Track A, B and the namespace separately. Assert that A survives, B is
removed and the post-check is indistinguishable from a successful intended unlink.
Do not pretend the production observation learns B's identity merely because
the synthetic test oracle knows it.

Keep prevention separate: verified experimental quiescence is a prerequisite of
name-based removal. Unobserved, false or incomplete quiescence refuses the effect
and dependent work, reports residue and preserves independent recovery. Model
these refusals and a successful removal under the declared exclusion premise.
An injected violation demonstrates the check's detection limit; it is not a
passing safety invariant or proof that the violation occurs under valid premises.

Retain the trusted-administrator premise without claiming DAC constrains root.
Do not invent a new isolation architecture to fix the evidence claim. Review
[unlink(2)](https://man7.org/linux/man-pages/man2/unlink.2.html), correct all
repeated claims in r3, and add dated errata to the prior handback where needed.

## 4. Complete lifecycle storage and first use — R2-4, Important

Specify one explicit allowlist of validated lifecycle outcomes for **all seven**
participants. Share its decision semantics with the corrected pure model;
do not leave ordinary participants with a weaker denylist than the executor.
ADMITTED is active and refuses reuse even if the process lock is free. Unknown,
malformed, incomplete and contradictory history also refuses.

Define initial verified-first-use record creation as a provisioning operation:
creator and authority, exact host/target binding, path, ownership/modes,
exclusive creation/no-overwrite rule, file/parent durability, and what evidence
supports first use. Missing history on a previously used host must never be
reinitialized as first use. Specify refusal/recovery when initialization is
interrupted or prior use cannot be excluded. This is a proposed addition to the
provisioning inventory; **do not provision anything**.

Cover normal fresh provisioned first use, absent/unreadable record, interrupted
initialization, crash after durable ADMITTED but before RUNNING, and valid
released/recovered predecessors. Include each participant in a table-driven
synthetic admission check, including environment reset. Preserve the persistent
lock inode and separate durable history; no expiry or free lock authorizes reuse.
Explain how records remain attributable and historical entries survive updates.

Update r3's exact permission/provisioning delta, including initialization and
any descriptor changes. State proposed module/interface, syscall, verb,
identity, path/mode, sudoers/capability and manifest changes accurately. Unchanged
executable names do not establish zero permission delta. All additions remain
unapproved pending the established review/maintainer sequence.

## 5. Preserve accepted corrections and open controls

The C1 cleanup → C2 → C5 ordering correction and withdrawal of the incorrect
JNL-47 criterion split received a positive technical recommendation for the
bounded model. Preserve them and their negative controls; do not reopen the
criterion decision or build a second product coordinator.

LAB-1 remains Important and unimplemented. Retain its labelled reproduction
and separate proposed residue/configuration recovery procedures. Do not repair
the gated cleanup mechanism or weaken the reproduction during this pass.

Keep all three C-7 cases declared unresolved, producer-review claims unchanged,
`is_executable=False`, operational-ineligibility/missing-coverage controls and
all twelve target facts unconfirmed. EH-R16-1 remains Open. The current digest
`e6d42228f5ccc4fd5eebc0861bb97eec42bbf16705d1aa209de5464e194bdba1`
is review input only; never pass it or a replacement digest to `--execute`.

## 6. Restrictions and verification

No SSH, oracle-test synchronization, host inspection, provisioning, database
operation, service change, credential access, generated-vector execution,
`--execute`, armed real boundary/materializer or privileged mechanism
implementation. Only local synthetic execution with injected effects is allowed.
No VM expansion, migration 0014, product implementation, deployment, cutover or
Package 5.1+ work. The later Codex target preflight remains after implementation
review; this assignment does not perform or expand it.

Verify the local fallback interpreters and versions before use. The canonical
test interpreter remains `/opt/freedom-blades/runtime/venv-web/bin/python` on
oracle-test; these historical local paths are restricted-pass exceptions.
Keep TEST_DATABASE_URL unset and bot/web runs serial. The bot interpreter is
needed for tests importing Discord, including skills tests.

Run structural checks first, then changed focused tests, then the available
non-database suites against the final submitted tree:

```bash
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_no_execution.py
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_reservation.py tests/phase_5_0_evidence/test_feasibility.py tests/phase_5_0_evidence/test_r16_1_ownership_reproduction.py
# Run each additional changed/new proposal-model regression module here.
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence
env -u TEST_DATABASE_URL /opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
node --test 'foundry-module/tests/'*.test.mjs
git diff --check
```

Run scoped compileall on changed Python files and configured format/lint/type
checks; distinguish unconfigured or unavailable tools from passed checks.
Report every skip as unverified. Without TEST_DATABASE_URL, the web suite can
exit successfully with 1362 skipped tests; the documented database-enabled
baseline is 80. Do not run database tests elsewhere to evade the restriction.

Independent re-review baseline: structural 205 passed, harness 1546 passed with
no skips. Bot/web/Foundry suites were not rerun by that review. Earlier handback
figures are historical comparisons, not results for your new tree.

If covered sources change, regenerate manifest and plan through the non-executing
CLI twice, compare output bytes, and independently recompute every covered source
hash. Compare installed artifacts to generated output and explain coverage-list
changes. Do not hand-edit generated artifacts or invent producer acceptance.
If no covered source changes, verify existing hashes/artifacts instead of
inventing a new version. Every resulting digest remains review input only.

## 7. Handback and stop point

Write `project-review-remediation-2026-09-11-r2-handback.md` with:

- disposition of all four R2 findings and traceability to r3 sections/tests;
- implemented pure-code fixes versus proposed, unbuilt mechanisms;
- failing-before/passing-after admission regressions and separately labelled
  proposal-model observations, including successful and deliberately defective
  controls;
- exact descriptor/durability contract and revised provisioning/permission delta;
- dated corrections to prior evidence claims, preserving historical submissions;
- exact commands, interpreter versions, results, skips, unavailable checks,
  manifest integrity and review-only digest;
- remaining proof obligations, risks and decisions, and next owner/checkpoint.

Update `docs/review/Handover information`, project status and implementation-plan
§20 pointers concisely. Preserve earlier review artifacts and link rather than
silently replace their conclusions. Do not close findings on the implementer's
authority. Package 5.0 remains not ready, P5.0-R5 Blocking, OD-62 Open and
EH-R16-1 Open pending independent review and the applicable gates.

Return to Codex after this bounded pass. Technical acceptance of the revised
design and required maintainer permission decisions precede privileged
implementation; implementation review precedes target preflight and a separate
execution decision. Passing tests advances none of those gates.
