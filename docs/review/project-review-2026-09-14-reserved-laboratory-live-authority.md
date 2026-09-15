# Codex technical and security re-review — reserved-laboratory live authority

Date: 2026-09-14. Authorization: C-P5.0-LAB-I-R1 independent re-review.
Submission: [Claude live-authority handback](phase-5-0-reserved-laboratory-call-graph-remediation-r2-handback.md).
Design basis: [runner contract r6](phase-5-0-reserved-laboratory-runner-contract-r6.md).

## Recommendation

**Changes requested.** The submitted correction now re-reads the current lock,
run-ledger and reservation state at the executor guard, and it revokes the
registered permit when the synchronous callback returns. Those conjuncts repair
the retained-after-return reproduction. They do not make the authority one-shot
inside the live callback.

PR-20260914-LABI-R1-1 remains **Blocking**. The callback can register a fresh
permit after the genuine permit has been consumed, while the same session,
cooperative-lock hold and durable T6--T8 state remain current. It can also build
a fully bound permit through the ordinary callable factory and assign it to the
mutable `_authority` field. In both public synthetic reproductions an armed
executor reaches its reviewed plan instead of refusing.

C-7 remains unresolved, EH-R16-1 remains Open, `is_executable` remains False,
the twelve target facts remain unconfirmed, Package 5.0 remains not ready,
P5.0-R5 remains Blocking, OD-62 remains Open and LAB-R6 remains Open. No digest
is approved and no execution, preflight, provisioning or server action is
authorized.

## Finding

### PR-20260914-LABI-R2-1 — Blocking — spent authority can be replaced during the same invocation

`EffectPermit.consume()` clears only `integration._authority`. It records no
non-reusable fact saying that this invocation or durable start has already
spent its authority. `ParticipantIntegration._issue_authority()` then assigns a
new permit without refusing an earlier issuance or consumption. The durable
ledger remains `participant_started`, the reservation remains `running`, the
same session remains open and its lock remains held, so every conjunct in the
new permit's `consume()` succeeds.

The accepted path is therefore:

```text
T6 participant_started -> T7 admitted -> T8 running
  -> issue genuine permit -> first armed executor consumes it and reaches effects
  -> callback calls _issue_authority() again
  -> second armed executor consumes the replacement and reaches effects
  -> one durable start has authorized two executions
```

The registration is mutable by a still simpler path. `_grant_permit()` accepts
the live integration and session references as ordinary arguments, and
`ParticipantIntegration._authority` is an assignable dataclass field. During
the callback, assigning the resulting permit to `_authority` satisfies the
identity check. The lock and durable-state checks then establish that the
surrounding invocation is live, but not that this permit was issued by its one
authorized transition.

This is not a claim that underscore-prefixed names form an access boundary.
The remediation itself correctly rejects that premise and explicitly treats
direct factory calls and mutable object constructions as review inputs. The
new paths use the same ordinary Python object graph and callable interfaces.

The handback's statements that “nothing a caller can write registers an
object” and that clearing `_authority` makes the capability “once, ever” are
therefore false. Clearing a replaceable reference is revocation of that object;
it is not durable or invocation-scoped consumption state.

Required correction:

1. Make authority issuance a single transition for the invocation and refuse
   every second issuance, including one attempted after consumption.
2. Make the final consuming transition depend on non-replaceable
   invocation-owned state, not solely on caller-writable permit and integration
   fields. Do not describe Python naming conventions as enforcement.
3. Preserve the current-session identity, held-lock, authoritative ledger read,
   authoritative reservation-history walk, callback-finally revocation and
   T2--T17 ordering.
4. Keep both public failing reproductions. Add focused reversals proving the
   issuance-once and registration-integrity controls are independently
   load-bearing, plus the existing successful one-execution control.
5. Review the complete reachable callback object graph, including the
   integration reachable through the executor's `session` field, before making
   a stronger claim than the mechanism supports.

## Reviewer questions from the handback

- Keeping the harness reservation-state conjunct in the integration-owned live
  authority check is consistent with the current design; moving it does not
  address this finding.
- The stated boundary that a caller performing T2/T6/T7/T8 has executed the
  protocol is not enough here. These reproductions do not create another
  lifecycle: they reuse the one current invocation and current durable start to
  authorize an additional execution.
- The registration conjunct is useful defence in depth, but its reported
  coverage is not acceptable as a one-shot authority claim while the
  registration and issuing method remain replaceable in the reviewed object
  graph.

## Independent evidence and limits

Two public behavioral regressions were added to
`tests/phase_5_0_evidence/test_lab_live_authority.py`:

- `test_the_live_invocation_cannot_issue_a_second_authority`
- `test_the_live_registration_cannot_be_replaced_by_mutable_state`

Restricted-local command, with `TEST_DATABASE_URL` unset:

```text
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q \
  tests/phase_5_0_evidence/test_lab_live_authority.py \
  -k 'live_invocation_cannot_issue or live_registration_cannot_be_replaced'
```

Result: **2 failed, 20 deselected**. Both failures are `Failed: DID NOT RAISE
ExecutorRefused`; each synthetic armed executor reached the plan. No process
boundary, real participant, real boundary/materializer, generated vector,
`--execute`, SSH, synchronization, host inspection, provisioning, database
operation, credential access or service change was used. Broader suites were
not run after this Blocking reproduction; a green unrelated suite cannot close
the failed one-shot invariant.

