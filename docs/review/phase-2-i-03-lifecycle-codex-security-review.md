# Codex security review — PreparedSnapshot lifecycle remediation

Date: 2026-08-08
Reviewed state: `foundry-module/` at `f632722`
Related general review: `phase-2-i-03-lifecycle-codex-review.md`

## Recommendation

Security review does not recommend acceptance yet. One Important untrusted-output finding is open, and the general review contains two Blocking production-reliability/idempotency findings. No credential-retention defect was found in the reviewed prepared-state paths.

## Important — untrusted server response values are rendered as trusted labels

An error response's `error.code` crosses the HTTP boundary without schema, allowlist, length, or character validation (`transport.js:209-218`) and is interpolated into the Foundry notification (`main.js:347-355`). The server-controlled prose was removed, but unrestricted code retains the same effective text channel. A successful receipt also supplies unbounded `actor_count` to `describeReceipt` (`workflow.js:525-535`).

I reproduced both paths with a sentence instructing the operator to disclose a credential. Foundry escapes notification content, so this is not HTML/script injection. It is a social-engineering and notification-integrity issue aimed at the privileged operator.

Severity is Important. A compromised endpoint already observes the bearer credential presented to it, reducing the incremental impact for that credential, but it can still impersonate repository-owned guidance, request other secrets, or direct unsafe operator action. The code should consistently treat every response field as untrusted.

Required controls:

- map only an allowlisted set of stable server codes to repository-owned operator text;
- use a fixed bounded fallback for unknown codes and keep detailed values in a safe server correlation/log path, not the UI;
- validate the entire success receipt before marking prepared state confirmed;
- accept `actor_count` only as a bounded non-negative integer;
- validate checksum shape and equality as a success invariant rather than merely displaying disagreement; and
- add adversarial length, control-character, Unicode, and type tests for both refusal and success receipts.

## Credential handling

The credential remains a dialog-local parameter, is sent only in the Authorization header, and was not found in prepared snapshot or `PreparedSnapshotState` entries. The existing test for state non-retention is weak because it searches for the literal word `secret`, not the actual credential; this should be corrected as part of remediation.

## Evidence boundary

The Node suite passed 126/126. Isolated reproductions used synthetic values and no network or real credential. No live Foundry installation or browser rendering rehearsal was performed. Escaping prevents markup injection, but it does not make attacker-authored text trustworthy.
