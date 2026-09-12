# Claude — reservation-to-harness binding remediation, R5

Date: 2026-09-11. Direction: C-P5.0-LAB-1, reserved disposable laboratory.
Review: [project-review-2026-09-11-r5.md](project-review-2026-09-11-r5.md).

## Assignment and boundary

Address **PR-20260911-R5-1** in one bounded local pass. Bind the harness run's
durable start to the reservation it owns, enforce that binding through terminal
publication and stored-history validation, submit runner contract r6, and return
one handback to Codex for technical re-review. Existing bounded local
authorization persists; do not ask for it again.

Keep the r5 architecture and terminal order. This is a missing identity binding,
not permission to redesign the lifecycle store, add a scheduler, or choose a new
isolation mechanism. Prefer the existing `lifecycle_storage.py`, fixture and
regression modules.

Allowed edits: pure schemas/codecs/validators, bounded in-memory lifecycle
models, regressions, supporting contract and evidence corrections, necessary
structural declarations, and non-executing manifest/plan regeneration. Do not
implement a real filesystem writer, privileged mechanism, lock adapter, host
runner, preflight or operational integration. No permission or provisioning
change is approved.

## Required context

Read `.agents/AGENTS.md` completely; the implementation plan's reading map,
§§0, 16, 20 and relevant Phase 5/testing requirements; the active handover; and
the disposable-server document with its restriction banner. Then read:

- the R5 review and its reproduction in full;
- the R4 remediation prompt and handback, runner contract r5 and its dated
  supersession/errata chain;
- `reservation.py`, `lifecycle_storage.py`, `durability_model.py`,
  `lifecycle_fixtures.py`, `test_r3_lifecycle.py`, `test_r4_remediation.py`,
  structural guards and manifest/non-executing generation contracts;
- affected package-plan §2.13 rules and the reserved-laboratory direction.

Check Git status and preserve unrelated work. Trace `RunLedger.begin`,
`RunLedger.complete`, `check_participant_history`, `conclude_reservation`, the
fixture helpers, stored-byte survey and final admission conjunction. A binding
checked only by a writer is incomplete; planted bytes must refuse on read too.

## 1. Reproduce the wrong-reservation completion first — R5-1, Blocking

Add a failing-before regression through the existing `Laboratory` fixture and
public APIs for the exact review case:

```text
initialize
ADMITTED A
begin B-harness as HARNESS_CLI
RUNNING A
conclude_reservation(reservation=A, run_id=B-harness)
```

r5 returns `concluded=True`, publishes both entries and marks `B-harness`
completed. After the repair, the attempt must refuse **before publishing the
wrong completion**, preserve B's started bytes, and leave the ledger blocking
every successor. State precisely what happens to A's already-published RELEASED
entry under the adopted release-before-completion order and demonstrate the
bounded attributable recovery; do not hide this intermediate state.

Also plant syntactically valid stored bytes that mismatch the start's
reservation and completion evidence. The survey must classify them invalid and
the connected admission path must refuse. A safe writer does not excuse an
unsafe reader of records written by r5 or by a corrupt implementation.

## 2. Establish one durable reservation binding

The harness's `participant_started` entry must durably name the reservation it
owns. The completion must name the same reservation, and terminal publication
must require exact equality among:

1. the reservation recorded in the stored harness start;
2. `ReservationRequest.reservation_id`;
3. `ReleasePublication.reservation_id`;
4. `CompletionEvidence.reservation_id`; and
5. any reservation identity carried by the terminal result.

Continue binding the run ID to the stored start and run filename as r5 already
does. Do **not** infer reservation identity from a run-name prefix, suffix or
other unchecked string convention. If r6 adopts a filename convention as an
additional invariant, define its grammar, validate it on both writer and reader
paths, and explain why it is necessary; it cannot replace the stored field.

Make the participant-start record schema explicit. For the six participants
whose completion conditions are external, either require an empty reservation
field or define a separate bounded shape; choose one coherent representation
and validate it. For `HARNESS_CLI`, missing, empty, changed or mismatched
reservation identity must refuse. Do not create a generic metadata bag or make
the parser silently accept both old and new meanings.

Read the stored start before deriving lifecycle-owned completion facts. A caller
supplied `participant`, `run_id`, reservation or release publication is a checked
claim, not authority. Keep the required completion profile derived from the
stored participant. Ensure `conclude_reservation()` cannot append a RELEASED
entry and then settle an unrelated run merely because both calls succeeded.

Use the same participant-history semantic validator before append and during
survey. Evidence that merely contains a nonempty reservation is insufficient;
compare its value. Invalid publication must leave existing run bytes unchanged.

## 3. Required regression matrix and lifecycle controls

Cover writer and planted-byte reader paths for:

- A's release offered to B's harness run — the exact reproduction;
- missing and empty reservation on a harness start;
- completion evidence naming a different reservation from its start;
- release publication naming a different reservation from its start;
- request, publication and completion disagreement in each direction;
- a non-harness start or completion carrying a reservation when its profile
  does not own lifecycle conditions;
- a matching harness start, request, release and completion succeeding;
- sequential reservations with distinct harness runs, read from stored bytes
  after process restart;
- failure after the release publication but before the completion, showing the
  unsettled correctly bound run blocks reuse and can be recovered; and
- identity reuse and stale release evidence remaining refused.

The tests must prove the new cases fail against r5, not only pass after the
repair. Report the failing-before count or exact named failures from a scratch
copy without modifying or discarding the submitted tree. Do not weaken a guard,
manufacture lifecycle facts beside the store, or use the model's durable-state
oracle as protocol input.

Re-run the existing R4 matrix and complete connected lifecycle. Preserve the
positively reviewed current-reservation transition state machine, cross-
participant refusal, required-ledger behavior, evidence codec, successor
re-seal, process-restart/power-loss distinction and release-before-completion
order. The repair must not reopen those paths.

## 4. Contract, schema and historical evidence

Write `phase-5-0-reserved-laboratory-runner-contract-r6.md`, marked **submitted
for technical review, not accepted and not implemented**, superseding r5. Keep
the complete contract and correct §§5.5, 5.7, 5.11.1, 5.12–5.14 and the proof
matrix wherever the new stored binding affects them. State the exact record
schema, parser, writer and interface changes and the compatibility consequence
for r5 participant-start records.

Preserve r5 with a dated supersession notice and erratum rather than silently
rewriting its historical claim. Add a dated correction to the R4 handback for
the claim that reservation binding was complete. Record whether the permission
and provisioning delta changes; it should remain ten items unless the design
demonstrates otherwise, and any change remains proposed and unapproved.

R4-1's stale-transition defect has a positive technical recommendation. R4-2
and R4-3 remain open until Codex reviews this binding. Do not close any finding
on the implementer's authority.

Preserve EH-R16-1 Open and its privileged remedy unbuilt. LAB-1 remains
Important and unrepaired. Preserve all three unresolved C-7 cases, target-fact
refusals, producer-review controls, `is_executable=False`, the CRP fix,
synthetic skills fixture, sanitized crafting report and production alias fix.
Do not restart the bot.

## 5. Restrictions and verification

No SSH, oracle-test synchronization, host inspection/provisioning, dependency
installation, database operation, destructive drill, service change, credential
access, generated-vector execution, `--execute`, armed real boundary/materializer
or privileged implementation. Only local synthetic execution with injected
effects is permitted. No stage, commit, push, reset or history rewrite. No VM
expansion, migration 0014, product implementation, deployment, cutover or
Package 5.1+ work. The later Codex target preflight remains after implementation
review and is not performed or expanded here.

Verify fallback interpreter paths and versions before use. The canonical test
environment remains `/opt/freedom-blades/runtime/venv-web/bin/python` on
oracle-test; the historical local paths below are restricted-pass exceptions.
Keep `TEST_DATABASE_URL` unset. Run bot/web serially because they share a
database. Run structural, focused and complete available non-database checks
against the final submitted tree:

```bash
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_no_execution.py
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_r4_remediation.py
# Run the new R5 regression module here.
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence
env -u TEST_DATABASE_URL /opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
node --test 'foundry-module/tests/'*.test.mjs
git diff --check
```

Run scoped `compileall` on changed Python and configured formatter, linter and
type checks. Distinguish unavailable or unconfigured tooling from a pass. Report
every skip as unverified: the database-disabled web suite can pass with 1362
skips; the documented database-enabled baseline is 80. Do not evade the
restriction elsewhere.

R5 independent baseline: structural plus R4 regressions **293 passed**; complete
synthetic harness **1801 passed**, zero skips. Bot, web, database and Foundry
suites were not rerun by that review. Historical counts are comparisons, not
evidence for the new tree.

If covered sources change, regenerate the manifest and plan twice through the
non-executing CLI, compare bytes, independently recompute every covered hash and
compare installed artifacts with generated output. Explain coverage or schema
changes. Never hand-edit generated artifacts. Current digest
`39cea2904f66606a66664f6835633a83a57780f4edc3570d6e8a3942edd196cd`
and every replacement are review input only; never pass them to `--execute`.

## 6. Handback and checkpoint

Write `project-review-remediation-2026-09-11-r5-handback.md` with:

- the disposition and traceability of PR-20260911-R5-1;
- the exact failing-before reproduction and passing-after result;
- the durable start/request/publication/evidence binding and its reader/writer
  enforcement;
- schema, interface, compatibility and permission impacts;
- the release-published/completion-refused intermediate state and recovery;
- preserved R4 fixes and connected sequential lifecycle controls;
- commands, interpreters, results, skips, unavailable checks, manifest
  integrity and review-only digest; and
- remaining proof obligations, unapproved decisions and next checkpoint.

Update the active handover, project status and implementation-plan §20 pointers
concisely. Return to Codex for technical re-review. Do not request privileged
implementation approval before this checkpoint. Package 5.0 remains not ready,
P5.0-R5 Blocking, OD-62 Open and EH-R16-1 Open. Passing tests accepts no risk and
advances no operational gate.
