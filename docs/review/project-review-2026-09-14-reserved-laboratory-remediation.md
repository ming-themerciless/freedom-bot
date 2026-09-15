# Codex technical and security re-review — reserved-laboratory remediation

Date: 2026-09-14. Authorization: C-P5.0-LAB-I-R1 independent re-review.
Submission: [Claude remediation handback](phase-5-0-reserved-laboratory-implementation-remediation-handback.md).
Design basis: [runner contract r6](phase-5-0-reserved-laboratory-runner-contract-r6.md).

## Recommendation

**Changes requested.** PR-20260913-LABI-1 and PR-20260913-LABI-2 are repaired
in the reviewed local mechanism. The recovery publisher now validates the exact
bound set before creating its run directory and verifies the correspondence used
by discovery and restoration. Descriptor-bound flag and removal effects now
require a present, non-empty and equal creating-step identity before issuing the
effect.

PR-20260913-LABI-3 is not repaired in the harness's executable call graph. The
CLI constructs a `ParticipantIntegration`, but neither it nor the executor calls
`ParticipantIntegration.run_harness()`, `run()` or any underlying admission,
ledger-begin or terminal-publication operation. The executor treats the mere
presence of any object in `session` as proof that the run is accounted. This is
a Blocking fail-open integration defect because, once the standing plan and
target gates are separately resolved, the armed executor can reach its first
effect without taking the cooperative lock or durably publishing
`participant_started`.

C-7 remains unresolved, EH-R16-1 remains Open, `is_executable` remains False,
the twelve target facts remain unconfirmed, Package 5.0 remains not ready,
P5.0-R5 remains Blocking and OD-62 remains Open. No digest is approved and no
execution, preflight, provisioning or server action is authorized.

## Finding

### PR-20260914-LABI-R1-1 — Blocking — the executable harness still bypasses the participant protocol

The CLI's `--execute` branch creates `integration = ParticipantIntegration(...)`
and passes it to `ExecutingRunner(session=integration)`, then calls
`runner.execute()` directly. Repository-wide call-site inspection finds no call
from the CLI or executor to `ParticipantIntegration.run_harness()` or `run()`.
The only production calls to `session.admit()` remain inside those two unused
methods.

`ExecutingRunner._require_accounted_run()` does not establish any protocol
state. For an armed `DescriptorBoundEffects`, it refuses only when `session is
None` or `run_id` is empty. It neither requires a `ParticipantIntegration` nor
obtains an `EffectPermit`, checks admission, verifies that `begin()` published,
or binds the session's participant/run/reservation to the executor. Consequently
`session=object()` satisfies this guard just as the real integration object does.

The resulting executable order is currently:

```text
construct ParticipantIntegration (no lock or I/O)
  -> construct armed boundary/materializer/effects
  -> ExecutingRunner.execute()
  -> check only session is non-None and run_id is non-empty
  -> issue the first reviewed step/effect
```

The required order is:

```text
take cooperative lock
  -> re-seal/read/validate lifecycle and ledger
  -> admit
  -> durably publish participant_started
  -> hand the resulting permit to the executor
  -> execute
  -> derive the harness release evidence
  -> publish release and harness completion in r6 §5.12 order
  -> release the lock
```

This is the same substance as LABI-3, not a new scope expansion. The remediation
prompt explicitly required the CLI and executor to use the same session, record
and ledger objects and preserve r6 §5.12. Constructing the objects without
calling their protocol does not enforce it.

Required correction:

1. Make `ParticipantIntegration.run_harness()` own the executable harness call,
   or introduce an equivalently single, typed orchestration path that performs
   its complete sequence.
2. Replace the non-`None` sentinel check with an unforgeable run permit produced
   only after durable `begin()`, bound to the exact harness participant, run id
   and reservation id.
3. Feed the executor's actual cleanup/reload/residue outcome into the terminal
   release decision and publish release and completion before releasing the
   lock. Exceptions and interruptions must leave the durable start unsettled.
4. Add a public behavioral regression in which an armed executor receives
   `session=object()` (and a non-empty run id) and prove that no effect is
   reached. Add a focused reversal that restores the current presence-only
   check and makes that regression fail.
5. Add a CLI composition test that observes the actual admit -> durable start ->
   executor -> terminal sequence, rather than asserting construction or source
   substrings.

## Other integration boundary

The six non-harness participant wrappers exist and are exercised over local
stores, but no bot-suite, web-suite, Foundry-suite, synchronization, dependency-
update or environment-reset entry point calls them. This remains explicitly
incomplete as LAB-R6. It should not be wired onto an unprovisioned host: the
correct fail-closed wrapper would stop all six paths because the persistent lock
and lifecycle objects do not yet exist. Closing this gap therefore needs a
separately authorized, ordered provisioning-and-wiring rollout; it is not a
reason to weaken the wrapper or create its lock on demand.

## D1 and D2

The separate D1/D2 amendment is correctly labelled proposed and r6 remains
unedited. This re-review does not accept the amendment, close V6 or authorize
either deviation operationally. The proposed text can be reviewed after the
Blocking executable-call-graph defect is remediated; it does not cause the
finding above.

## Independent evidence and limits

- Focused remediation/integration/no-execution set: **328 passed**.
- Complete local synthetic evidence suite: **2,165 passed, zero skipped**.
- Interpreter: `/opt/discord-bots/venv-web/bin/python` with
  `TEST_DATABASE_URL` explicitly unset, under the active local-only exception.
- Read-only repository call-site inspection established that the only
  non-test `ParticipantIntegration` construction is in the CLI, and no caller
  invokes its `run()` or `run_harness()` method.

The green suite is evidence that the isolated participant protocol and the two
earlier safety fixes behave as tested; it is not evidence that the CLI calls the
protocol. Bot, web and Foundry suites were not rerun in this re-review because
the Blocking defect is confined to the evidence-harness call graph and the
submission already reports their local-only results. No SSH, synchronization,
host inspection, preflight, provisioning, database operation, generated-vector
execution, `--execute`, real boundary/materializer use or service change was
performed.
