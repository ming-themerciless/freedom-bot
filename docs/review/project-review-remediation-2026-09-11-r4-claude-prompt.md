# Claude — lifecycle validation and completion ordering, R4

Date: 2026-09-11. Direction: C-P5.0-LAB-1, reserved disposable laboratory.
Review: [project-review-2026-09-11-r4.md](project-review-2026-09-11-r4.md).

## Assignment and boundary

Address all three R4 findings in one bounded local pass. Repair pure history
validation and the connected synthetic lifecycle model, submit runner contract
r5, and return one handback to Codex for technical re-review. Existing local
remediation authorization persists; do not ask for it again.

Keep the current architecture and the complete-lifecycle focus. The remaining
work is to make stored histories enforce the intended transitions and bind
completion evidence to the operation that actually started. Do not build a
general event store, scheduler or a new isolation architecture.

Allowed edits: pure validators/codecs, bounded in-memory lifecycle/effect models,
regressions, supporting design and evidence corrections, necessary structural
declarations, and non-executing manifest/plan regeneration. Prefer the existing
modules. No real filesystem writer, privileged mechanism, lock adapter, host
runner or operational integration may be implemented. Design acceptance and any
required maintainer permission decisions still precede that work.

## Required context

Read `.agents/AGENTS.md` completely; the implementation plan's reading map,
§§0, 16, 20 and relevant Phase 5/testing requirements; the active handover; and
the disposable-server document with its restriction banner. Then read:

- the R4 review in full, including its positive recommendations and limits;
- `project-review-remediation-2026-09-11-r3-handback.md`, runner contract r4,
  and the R3 remediation prompt's complete-lifecycle requirements;
- `reservation.py`, `lifecycle_storage.py`, `durability_model.py`, their tests,
  structural guards and manifest/non-executing generation contracts;
- the affected package-plan §2.13 rules and reserved-laboratory direction.

Check Git status and preserve unrelated work. Trace callers as well as validators:
a safe writer does not excuse an unsafe reader of pre-existing records, and a
safe reader does not excuse publishing a contradictory history.

## 1. Enforce the current reservation's transitions — R4-1, Blocking

First add regressions for the exact stored-history reproduction:

```text
FIRST_USE → ADMITTED A → RELEASED A → ADMITTED B → RUNNING B → RELEASED A
```

It currently admits C because A was admitted at some point and the reader takes
the final RELEASED entry. An unresolved B must never disappear behind A's stale
completion. Cover the analogous stale operator-recovery entry.

Replace historical membership checks with validation of the current reservation,
its current state and legal transitions. Apply the accepted reservation rules;
do not invent a second contradictory transition table. Operator recovery is an
attributed addition for the applicable quarantined predecessor, not permission
to revive or rewrite a terminal reservation. Preserve the distinction between
the quarantined run's terminal state and permission for a new run.

Use the same semantic validation before appending a proposed entry and when
reading the complete stored history. Invalid appends must leave the existing
bytes intact. Syntactically valid invalid histories must refuse on read, even
if a corrected writer could no longer produce them. Do not discard a bad tail
or select an earlier convenient release.

Required cases: stale release/recovery after newer ADMITTED and RUNNING states;
wrong-current-ID transitions; transitions after RELEASED or QUARANTINED except
the explicitly permitted recovery; duplicate terminal events; terminal ID reuse;
invalid state transitions; and valid sequential reservations and recovery.
Exercise both public append and direct stored-byte input. If duplicate delivery
is handled idempotently, it must not append a new terminal event or hide a newer
run; otherwise refuse explicitly. State the policy and test it.

## 2. Bind participant history and require the ledger — R4-2, Blocking

Add the exact regression before repair:

```text
begin web-1 as WEB_SUITE
complete web-1 as FOUNDRY_TESTS with only Foundry conditions observed
```

The completion must refuse without altering the web run's stored history, and
every successor must still refuse. The current implementation publishes that
completion and admits even though no web/database completion was observed.

Create one participant-history semantic validator used by both writers and the
ledger survey. Require exactly the supported start/terminal progression, stable
run ID, participant and identity across entries, binding to the actual run
filename, host/target agreement, and attributable completion/recovery evidence.
Reject terminal-without-start, repeated or incompatible terminal events and
unknown participant values. Apply the same rules to recovery as to completion.

Read and validate the start before choosing the completion profile. The required
conditions come from the operation that started, not a participant value the
completion caller supplies. Keep any caller parameter only as a checked claim.
Validate evidence content and completeness as well as field presence; an empty
or arbitrary string must not become proof merely because the final kind says
COMPLETED. Represent lifecycle-owned evidence so its run binding can be checked.
External observations remain injected and attributable; the model must not claim
to verify real processes or database backends.

In the connected admission path, missing or unreadable ledger evidence must
refuse. The current `ledger=None` path skips accounting and admits with an
unfinished web run. Separate intentionally isolated unit tests from this path;
do not give the full protocol an option to treat unavailable accounting as an
empty ledger. Preserve the valid, provisioned, observed-empty ledger control.

Required cases, through writer and stored-byte reader paths: wrong participant;
wrong run ID or filename; changed identity; wrong host/target; completion or
recovery without a start; missing/malformed evidence; duplicate terminal entry;
reuse of a recovered identity; missing/unreadable ledger; and matching success
and recovery for all seven participants. Check that every successor refuses an
invalid predecessor, including harness and environment reset.

## 3. Make terminal publication order achievable — R4-3, Important

The harness profile requires a durably published release before participant
completion, while r4's sequence and successful test publish completion first.
The test's `_observed(HARNESS_CLI)` sets a future fact to True. Correct the
protocol and test together; simply moving an assertion is insufficient.

Evaluate and recommend this order: validate the release decision against observed
conditions, durably publish the reservation release, then complete the harness
participant record, holding the lock throughout. Explain how the still-started
ledger blocks reuse between the terminal publications, and how a restart finishes
or recovers that state. If another order is preferable, state the concrete
dependencies and show it has a reachable successful path without relaxing release
requirements. No order may authorize reuse from only one satisfied half.

Derive lifecycle-owned facts from earlier modeled operations and stored records.
Do not inject “release durable” while the reservation history says RUNNING.
Connect the release decision, publication outcome, matching reservation/run
binding and completion evidence. Keep the model's durable-state map for test
assertions only; protocol code must use observations a real participant could
obtain under the specified writer/barrier contract.

Exercise normal completion, a refused release decision, failure before/after
each rename and directory barrier, and process restart between the two terminal
publications. Keep power loss a distinct scenario. Show no premature successor
admission, preserved prior history, and a successful bounded recovery for every
intermediate state. Include stale release evidence from another reservation.
Correct the previous successful-trace claim with a dated erratum.

## 4. One coherent submission and preserved controls

Write `phase-5-0-reserved-laboratory-runner-contract-r5.md`, marked **submitted
for technical review, not accepted and not implemented**, superseding r4. Retain
the complete contract and correct every affected transition, publication,
completion, refusal and evidence-matrix row. Preserve r4 with a dated notice and
add dated errata to the R3 handback; do not silently rewrite historical findings.

Keep validation responsibilities explicit: schema parsing, reservation semantics,
participant semantics and the final conjunction of admission conditions. State
the exact interface/record-schema impact and whether the proposed permission
delta changes. Do not expand permissions merely to repair pure validation.
If any expansion is necessary, propose it explicitly and leave it unapproved.

Before handback, run a bounded table-driven audit of legal and illegal transitions
and cross-run evidence for both history types. Include multiple sequential runs,
not only one fresh run. Trace the corrected full lifecycle from a fresh process
using stored bytes, and verify both a successful successor and refusals at the
intermediate boundaries. Tests must detect the original defects and must not
manufacture lifecycle facts beside the store to make a sequence pass.

Preserve the positively reviewed target/attribution repair, successor directory
barrier under the file-before-rename writer contract, distinction between process
restart and power loss, accounting for all seven participants, R2 state-shape
repair, usable descriptors, recovery-parent barrier and corrected post-unlink
evidence. Preserve C1 → C2 → C5 and the withdrawn JNL-47 criterion split.
No new architecture or criterion decision is needed for these repairs.

EH-R16-1 remains Open and its privileged remedy remains unbuilt. LAB-1 remains
Important and unrepaired with its labelled reproduction unchanged. Preserve the
CRP fix, synthetic skills fixture, sanitized crafting report and production alias
fix; do not restart the bot. All three C-7 cases remain unresolved, producer-review
claims and coverage controls unchanged, `is_executable=False`, all twelve target
facts unconfirmed, and real-execution refusal retained.

## 5. Restrictions and verification

No SSH, oracle-test synchronization, host inspection/provisioning, dependency
installation, database operation, destructive drill, service change, credential
access, generated-vector execution, `--execute`, armed real boundary/materializer
or privileged implementation. Only local synthetic execution with injected effects
is permitted. No stage, commit, push, reset or history rewrite. No VM expansion,
migration 0014, product implementation, deployment, cutover or Package 5.1+ work.
The later Codex target preflight remains after implementation review and is not
performed or expanded here.

Verify fallback interpreter paths and versions before use. The canonical test
environment remains `/opt/freedom-blades/runtime/venv-web/bin/python` on
oracle-test; the historical local paths below are restricted-pass exceptions.
Keep TEST_DATABASE_URL unset. Run bot/web serially because they share a database.
Run structural, then focused, then complete available non-database checks against
the final submitted tree:

```bash
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_no_execution.py
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_reservation.py tests/phase_5_0_evidence/test_r2_proposal_models.py tests/phase_5_0_evidence/test_r3_lifecycle.py tests/phase_5_0_evidence/test_feasibility.py tests/phase_5_0_evidence/test_r16_1_ownership_reproduction.py
# Run additional changed/new regression modules here.
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence
env -u TEST_DATABASE_URL /opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
node --test 'foundry-module/tests/'*.test.mjs
git diff --check
```

Run scoped compileall on changed Python and configured format/lint/type checks.
Distinguish unavailable or unconfigured tooling from a pass. Report every skip
as unverified: the database-disabled web suite can pass with 1362 skips; the
documented database-enabled baseline is 80. Do not evade the restriction elsewhere.
R4 independent baseline: 217 structural and 1723 harness tests passed, zero skips;
36 hashes and generated artifacts matched. Bot/web/Foundry were not rerun by that
review. Historical counts do not establish results for the new tree.

If covered sources change, regenerate manifest and plan through the non-executing
CLI twice, compare bytes, independently recompute all covered hashes and compare
installed artifacts with generated output. Explain any coverage/schema changes.
If none change, verify existing artifacts instead. Never hand-edit generated
artifacts. Current digest
`45b3c6c0313e5cb8b48e116aea7716b47f1a2d231f12719975d63166d3458201`
and every replacement remain review input only; never pass them to `--execute`.

## 6. Handback and checkpoint

Write `project-review-remediation-2026-09-11-r4-handback.md` with:

- disposition of all three R4 findings and r5 section/test traceability;
- pure-code/model changes versus proposed, unbuilt mechanisms;
- failing-before/passing-after writer and reader regressions, including the
  exact reproductions, cross-run cases and omitted-ledger refusal;
- the achievable terminal-publication order, intermediate crash states and
  connected successful/recovery controls;
- dated evidence corrections and exact interface/schema/permission impacts;
- commands/interpreters, results/skips, unavailable checks, manifest integrity
  and review-only digest;
- remaining proof obligations, unapproved decisions and next owner/checkpoint.

Update handover, project status and implementation-plan §20 pointers concisely.
Return to Codex for technical re-review. Do not close findings on the implementer's
authority or request privileged implementation approval before this checkpoint.
Package 5.0 remains not ready, P5.0-R5 Blocking, OD-62 Open and EH-R16-1 Open.
Passing tests accepts no risk and advances no operational gate.
