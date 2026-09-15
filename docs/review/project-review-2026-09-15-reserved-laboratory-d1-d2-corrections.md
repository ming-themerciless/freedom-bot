# Codex independent re-review — corrected D1/D2 contract amendment

Date: 2026-09-15.
Submission: [Claude correction handback](phase-5-0-reserved-laboratory-r6-d1-d2-correction-handback.md).
Contract: [runner contract r6](phase-5-0-reserved-laboratory-runner-contract-r6.md).

## Recommendation

**Changes requested.** The correction repairs the inconsistent operative
`renameat2` sites, restores the re-seal descriptor, describes D1's additional
interruption state accurately, adds real-filesystem regressions and records the
unimplemented `execveat` route honestly. One Blocking admission defect remains:
an interrupted lifecycle-record publication does not refuse all seven
participants.

The read-only target preflight remains authorized but queued behind remediation
and independent re-review. No provisioning, permission change, database
operation, generated-vector execution, participant wiring, real execution or
`--execute` is authorized.

## Finding

### PR-20260915-LAB-D12-1 — Blocking — lifecycle publication temporary does not block every participant

After the exclusive `linkat` succeeds and `unlinkat` fails, the final lifecycle
record and its temporary are two names for one inode. The final record is valid
and readable. `read_and_admit()` re-seals and parses that record but does not
check `record.temporary_present()`. The six ordinary participants can therefore
admit while the interrupted T1 publication remains unresolved; only the harness
later refuses when T7 attempts another publication.

Required correction:

1. Make the authoritative admission path refuse whenever the lifecycle
   publication temporary is present, before any of the seven may proceed.
2. Retain the temporary and final record unchanged.
3. Add a public regression covering all seven participants in D1's
   link-succeeded/unlink-failed state.
4. Keep the existing authoritative record parser, ledger survey and re-seal
   ordering; do not add a second admission state machine.

## Other dispositions

- Injecting an `OSError` on the real `unlinkat` after a real `linkat` is
  acceptable evidence for the resulting filesystem state. A signal-specific
  duplicate is unnecessary.
- The unresolved `execveat` route needs an explicit owner and execution stop
  condition before execution readiness.
- T1/T6 recovery must require an immediately preceding identity comparison of
  the final and temporary names before removing the temporary.

## V6 decision

Peter approves V6 as a **read-only prerequisite survey**, on Codex's
recommendation. It may record filesystem and mount type,
`fs.protected_hardlinks`, the execution identity, file ownership and mode
assumptions, and relevant capability state. It does **not** prove that the real
`linkat` publication succeeds and does not close I3. A controlled write
verification requires separate authorization before execution.

## Evidence and limits

Restricted local command with `TEST_DATABASE_URL` unset:

```text
env -u TEST_DATABASE_URL /opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q tests/phase_5_0_evidence
```

Result: **2 229 passed, zero skips**, with two warnings for unavailable pytest
asyncio configuration options. Passing tests do not cover the Blocking
admission path above.

No SSH, synchronization, target inspection, preflight, provisioning, database
operation, generated-vector execution, real participant, real
boundary/materializer or `--execute` was used.
