# Phase 4 post-gate remediation R2 — independent review

Date: 2026-08-31
Reviewer: Codex, Independent Reviewer
Outcome: **changes requested before Phase 5 preparation resumes**

## Disposition

The authorized R2 correction is materially correct:

- **P4-PG1 — Closed:** `CommandCaller.discord_user_id` requires a positive
  non-boolean integer and rejects malformed values through `invalid_caller`.
- **P4-PG2 — Closed:** `ExpectedVersion.aggregate_type` requires text before
  applying its nonblank rule and rejects malformed values through
  `invalid_expected_version`.
- **P4-PG3 — Closed:** `CommandCaller.principal_id` requires text before
  applying its nonblank rule, performs no coercion or decoding, and leaves
  current authority resolution to `LedgerPrincipalPort`.

Independent focused evidence against the R2 tree:

- `tests/test_p4_commands.py`: **121 passed**;
- combined P4-PG1/P4-PG2/P4-PG3 selection: **62 passed, 59 deselected**;
- `compileall` under both prescribed interpreters: exit 0; and
- scoped `git diff --check`: clean.

Claude's submitted full-suite evidence is internally consistent: bot/application
**2989 passed**, web **2824 passed and 80 expected skips**, and Foundry **171
passed**. The full suites were not repeated by this re-review because the two
remaining counterexamples require another correction and a final submitted-tree
run.

## Additional findings confirmed

### P4-PG4 — Important — malformed idempotency keys escape the typed envelope boundary

`application.idempotency.validate_key()` calls `key.strip()` before proving the
key is text. `CommandEnvelope` catches `IdempotencyKeyError`, but malformed
integers, booleans, floats, `None`, collections and bytes instead escape as
`AttributeError` or `TypeError`. This violates the envelope's documented
`InvalidEnvelopeError(code="invalid_request_key")` contract at the value that
defines retry identity. The shared validator also serves `IdempotencyRecord` and
the Foundry submission boundary, so the correction must preserve those accepted
consumers and test them.

### P4-PG5 — Important — malformed stored receipt commands escape the unreadable-receipt contract

`CommandReceipt.__post_init__()` calls `self.command.strip()` before proving the
command is text. Direct construction leaks `AttributeError` or accepts bytes.
More importantly, `CommandReceipt.from_payload()` intentionally converts
malformed stored rows into `StoredReceiptUnreadable`, but its catch list does not
include `AttributeError`. A spent key whose stored command is malformed can
therefore escape the typed replay refusal instead of returning
`original_result_unavailable`; the effect may already have committed, so it must
never be re-executed or reconstructed.

## Governance effect

Phase 4 remains approved; this review does not reopen its architecture or gate.
P4-PG4 and P4-PG5 are narrow post-gate defects and require no policy, schema,
migration, authorization or deployment decision. The maintainer directed that
Phase 4 defects be repaired before Phase 5 continues, so Package 5.0 preparation
pauses for one bounded remediation and independent re-review. Package 5.0 remains
`not ready`, and its implementation remains unauthorized independently of this
pause.

This record corrects the reviewer's earlier conversational statement that no
Important Phase 4 finding remained. That statement was made before the residual
section of the R2 handback was inspected and is not the durable disposition.
