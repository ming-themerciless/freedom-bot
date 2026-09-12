# Independent technical re-review — runner contract r5

Date: 2026-09-11. Reviewer: Codex. Disposition: **changes requested**.

Scope: the R4 remediation handback, runner contract r5, the connected lifecycle
model and its synthetic regressions. This is a local, non-executing review under
the active handover restrictions. No implementation, generated artifact,
operational configuration, host or database was changed during this review.

The reservation state-machine repair correctly refuses stale transitions, and
the participant validator now rejects the cross-participant and omitted-ledger
paths reproduced in R4. The proposed release-before-completion order is also
reachable. One missing binding still lets that order complete the wrong harness
run.

## PR-20260911-R5-1 — Blocking: a release can settle another reservation's harness run

Locations: `tools/phase_5_0_evidence/lifecycle_storage.py:2462`, `:2827` and
`:3095`; runner contract r5 §§5.11.1 P7 and 5.12.

`CompletionEvidence` carries a reservation ID for the harness, but
`check_participant_history()` checks only that it is nonempty. The stored
`participant_started` entry carries no reservation field, and
`conclude_reservation()` accepts an independent caller-supplied `run_id` without
binding that run to `request.reservation_id`. It consequently publishes a valid
release for reservation A and a valid completion into any already-started
harness run file B.

Independent reproduction through the existing `Laboratory` fixture and public
model APIs:

```text
initialize
ADMITTED A
begin B-harness as HARNESS_CLI
RUNNING A
conclude_reservation(reservation=A, run_id=B-harness)

{'concluded': True,
 'release': True,
 'completion': True,
 'completed': ('B-harness',)}
```

This is not only a naming inconsistency. If B is the outstanding ledger account
for a different reservation, A's release evidence settles B and the final
conjunction admits a successor once no other unsettled file remains. The model
therefore has not established r5's claim that the harness completion "names the
reservation it concluded, so the binding can be checked." It records the name
but has no stored fact against which to check it.

Required correction: bind each harness start durably to its reservation and
require exact equality among the stored start, the release request/publication,
the completion evidence and the run filename (if the filename convention is
part of the contract). Perform the same check before append and on survey. Add a
failing-before regression for A completing B, plus planted-byte mismatches and
valid sequential controls. Do not infer the binding from an unchecked string
prefix.

## Disposition

| R4 finding | Recommendation on r5 |
|---|---|
| R4-1, stale reservation transitions | Recommend closure of this specific defect. The current reservation and state are walked over `reservation.TRANSITIONS`, and invalid proposed and stored histories refuse. |
| R4-2, participant completion binding | Keep open. The exact web-as-Foundry reproduction and absent-ledger path are repaired, but the lifecycle-owned reservation binding remains incomplete as R5-1. |
| R4-3, terminal publication order | The release-before-completion order is reachable and its intermediate ledger refusal is supported in the model. Keep the finding open pending R5-1 because the completion half can currently target another reservation's harness run. |

No privileged mechanism, filesystem writer, lock adapter or operational
integration was reviewed as implemented; none exists. The ten-item permission
and provisioning delta remains unapproved. LAB-1 remains Important and
unrepaired, EH-R16-1 remains Open, all three C-7 cases remain unresolved, twelve
target facts remain unconfirmed and `is_executable` remains false. Package 5.0
remains not ready and P5.0-R5 remains Blocking.

## Independent evidence and limits

From `/opt/freedom-blades/platform`, with `TEST_DATABASE_URL` unset:

```text
/opt/discord-bots/venv-web/bin/python -m pytest -q -rs \
  tests/phase_5_0_evidence/test_no_execution.py \
  tests/phase_5_0_evidence/test_r4_remediation.py
  293 passed in 1.36s

/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence
  1801 passed in 9.49s; zero skips
```

The reproduction was a local `python -c` invocation using the same fixture and
public APIs. The local interpreter is the restricted-pass exception; the
canonical environment remains `/opt/freedom-blades/runtime/venv-web/bin/python`
on `oracle-test`. The active restriction forbids SSH, synchronization, host
inspection, provisioning, preflight and execution, so none ran. Database, bot,
web and Foundry suites were not run, and no earlier counts are adopted as new
evidence. No formatter, linter or type-checker result is claimed. The supplied
manifest and digest were not changed or passed to `--execute`.
