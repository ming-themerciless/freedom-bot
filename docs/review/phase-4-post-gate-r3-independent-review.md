# Phase 4 post-gate remediation R3 — independent review and disposition

Date: 2026-09-02
Implementer: Claude
Independent reviewer: Codex
Acceptance authority: Peter Duscha

## Decision

**P4-PG4 and P4-PG5 are Closed.** Peter Duscha accepted the independent
review on 2026-09-02. Phase 4 was already approved and remains closed; this
decision records correction of two post-gate defects and does not reopen its
gate.

P4-PG4 is corrected at the shared idempotency-key validator: type is
established before value rules, malformed values retain the documented
`invalid_request_key` vocabulary at every caller, and no coercion or decoding
occurs. P4-PG5 is corrected at `CommandReceipt` construction: malformed stored
command names become `StoredReceiptUnreadable`, and a spent ledger key is never
re-executed or answered with an invented receipt.

## Independent evidence

Codex reviewed the production paths, caller inventory, regression-first
handback, typed translations and replay behavior, then ran the required suites
serially against `postgresql+psycopg:///freedom_test`:

- bot: **3103 passed**;
- web: **2824 passed, 80 expected skips**;
- Foundry module: **171 passed**;
- `git diff --check`: passed; and
- static asset integrity: passed.

No new Blocking or Important Phase 4 finding was identified. Package 5.0
readiness work may resume at its existing `not ready` state. This disposition
does not authorize Package 5.0 implementation, migration `0014`, host or
database mutation, deployment, cutover, or Package 5.1+.
