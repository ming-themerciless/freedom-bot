# R5 remediation re-review and finding disposition

Date: 2026-09-12. Reviewer: Codex. Maintainer disposition: accepted.

Scope: the R5 reservation-to-harness binding remediation in runner contract r6,
its implementation, and its synthetic regressions. This is a local technical
review under the active handover restrictions. No privileged implementation,
operational configuration, host, database, or generated artifact was changed.

## Disposition

| Finding | Review conclusion | Maintainer disposition |
|---|---|---|
| **PR-20260911-R5-1 — Blocking:** a release can settle another reservation's harness run | The stored start now durably binds the harness run to its reservation. The writer and reader paths enforce the binding, and conclusion checks it before publishing either terminal entry. No new defect was found in the reviewed scope. | **Closed** |
| **PR-20260911-R4-2 — Blocking:** participant completion is not bound to the started run | The shared participant-history validator requires a valid start, binds participant/run/identity and completion evidence, and is used before append and when reading stored histories. The connected admission path refuses absent or invalid ledger evidence. R5's stored reservation binding completes the remaining harness-specific binding. No new defect was found in the reviewed scope. | **Closed** |
| **PR-20260911-R4-3 — Important:** successful trace assumes a future release | The terminal order is reachable: check the binding, decide release, publish RELEASED, publish harness completion, then release the lock. Lifecycle-owned completion facts are derived from those operations; tests cover the intervening failure state, refusal, and recovery. R5's step-zero binding check prevents that order from settling another run. No new defect was found in the reviewed scope. | **Closed** |

R4-1 retains its prior positive technical recommendation; this disposition does
not record its closure. These finding dispositions do not close the package-level
P5.0-R5 readiness blocker or any operational, provisioning, permission, or
execution gate.

## Evidence

From `/opt/freedom-blades/platform`, with `TEST_DATABASE_URL` unset:

```text
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs \
  tests/phase_5_0_evidence/test_r5_remediation.py \
  tests/phase_5_0_evidence/test_r4_remediation.py \
  tests/phase_5_0_evidence/test_r3_lifecycle.py
  192 passed in 0.26s

env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs \
  tests/phase_5_0_evidence/test_no_execution.py
  217 passed in 1.28s

env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs \
  tests/phase_5_0_evidence
  1859 passed in 8.98s; zero skips
```

The 192-test focused command overlaps the two broader harness runs and is
reported separately as the direct R3/R4/R5 regression set. No SSH,
synchronization, host inspection, database operation, provisioning, preflight,
privileged test, or real evidence execution ran. The active handover prohibits
those actions. This review makes no new claim about bot, web, Foundry, formatter,
linter, or type-checker results.

## Review reasoning

The stored `participant_started` entry now carries the reservation identity for
the harness and an exactly empty field for participants whose completion
conditions are external. Schema version 2 refuses r5 records under the old
shape. `check_participant_history()` validates the same reservation binding
before publication and when surveying stored bytes; `RunLedger.complete()` reads
the stored start before deriving the completion profile or evidence; and
`conclude_reservation()` checks the stored reservation and in-progress harness
state before evaluating release. The regressions cover mismatches in both
directions, planted invalid histories, old-schema refusal, matching completion,
and recovery of a refused run.

The re-review found no new Blocking, Important, or Optional finding in this
bounded scope. The original R5 review remains the historical changes-requested
review; this disposition closes its listed finding and the two dependent R4
findings only.
