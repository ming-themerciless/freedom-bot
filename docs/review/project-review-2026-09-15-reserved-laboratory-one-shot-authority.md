# Codex technical and security re-review — reserved-laboratory one-shot authority

Date: 2026-09-15. Authorization: C-P5.0-LAB-I-R2 independent re-review.
Submission: [Claude one-shot authority handback](phase-5-0-reserved-laboratory-live-authority-r2-handback.md).
Design basis: [runner contract r6](phase-5-0-reserved-laboratory-runner-contract-r6.md).

## Recommendation

**Accepted with no new finding.** PR-20260914-LABI-R2-1 is closed within the
explicitly stated trust boundary. Each `run()` or `run_harness()` invocation
owns one `_WorkInvocation`: issuance is its single `OPEN -> ISSUED` transition,
consumption is its single `ISSUED -> SPENT` transition, and the work's end moves
it to `ENDED`. A second issuance, a second consumption, a constructed permit or
a replaced registration reaches no effect.

The accepted scope is important. This mechanism protects the reviewed ordinary
callback object graph; it is not, and does not claim to be, a security boundary
against arbitrary Python running with the same process credentials. Such code
can inspect frames, replace methods or call operating-system interfaces
directly. Adversarial isolation would require a process boundary and is an
architecture decision outside C-P5.0-LAB-I-R2.

This recommendation approves no digest and authorizes no execution, preflight,
provisioning or server action. C-7 remains unresolved, EH-R16-1 remains Open,
`is_executable` remains False, the twelve target facts remain unconfirmed, D1
and D2 remain proposed, V6 remains unconfirmed, Package 5.0 remains not ready,
P5.0-R5 remains Blocking, OD-62 remains Open and LAB-R6 remains Open.

## Review result

The re-review traced the path from the durable participant start through the
first effect and terminal publication. The remediation preserves the accepted
current-session identity, cooperative-lock hold, authoritative
`ParticipantRunLedger.read_run` check, authoritative
`check_reservation_history` walk, derived release evidence and T2--T17 order.

The two prior reproductions now refuse:

- calling `_issue_authority()` after the genuine permit has been spent meets
  the same invocation in `SPENT` and constructs or registers no replacement;
- assigning a fully bound constructed permit to `_authority` fails the identity
  conjunction between the invocation's issued permit, the registration and the
  offered permit.

The additional controls establish that issuance refuses before and after the
spend, wrong invocation bindings register nothing, registration replacement
fails closed, restoring every ordinary reachable attribute does not re-arm the
spent invocation, and return, exception and interruption end the authority.
The successful composition still reaches one armed executor exactly once.

The handback reports one reversal, the absent-record branch in consumption, as
not independently load-bearing. That is not a residual finding: invocation
ownership is independently covered, and the absent-record check is a
fail-closed conjunct rather than the sole control for an accepted path.

## Independent evidence and limits

Restricted-local commands, with `TEST_DATABASE_URL` unset:

```text
env -u TEST_DATABASE_URL /opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q \
  tests/phase_5_0_evidence/test_lab_live_authority.py \
  tests/phase_5_0_evidence/test_lab_call_graph.py \
  tests/phase_5_0_evidence/test_lab_integration.py \
  tests/phase_5_0_evidence/test_lab_implementation.py \
  tests/phase_5_0_evidence/test_lab_remediation.py \
  tests/phase_5_0_evidence/test_executor.py
```

Result: **306 passed**, with two `PytestConfigWarning`s for unavailable asyncio
configuration options in the local environment.

```text
env -u TEST_DATABASE_URL /opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q \
  tests/phase_5_0_evidence
```

Result: **2 225 passed, zero skips**, with the same two warnings.

No bot, web, database-enabled or Foundry suite was rerun by this reviewer. No
real participant, process boundary, boundary/materializer, generated vector,
`--execute`, SSH, synchronization, host inspection, provisioning, database
operation, credential access or service change was used.

## Next action

Maintainer direction is required before further work. The local one-shot
remediation is complete, but it does not resolve the standing Package 5.0
blockers or authorize the proposed r6 amendments, target preflight,
provisioning, six-participant wiring or execution.
