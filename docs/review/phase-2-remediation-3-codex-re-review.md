# Phase 2 remediation 3 — Codex independent implementation re-review

Date: 2026-08-03

Role: Independent Reviewer under implementation plan §16.4

Scope: the uncommitted working tree on `docs/platform-plan`, with `HEAD` at
`c8a3da9`, answering B-1R from
`phase-2-remediation-2-codex-re-review.md`.

This is a recommendation, not approval. The Acceptance Authority records the
gate decision. The supervised real-export rehearsal was not performed, and the
two prohibited Foundry sources were not accessed.

## Result

**B-1R is resolved. I found no new blocking or important implementation
finding in this remediation.** The implementation is ready to proceed to the
remaining owner-controlled Phase 2 operational evidence; this recommendation
does not close the Phase 2 gate.

## B-1R disposition

`ImportOutcome` now distinguishes the durable result of an import from the
narrative report produced by a particular reconciliation run. The durable
result includes a typed `ReconciliationFacts` value. A first apply constructs
that value from the report whose exact rendering is stored in
`snapshot_imports.summary`; a retry reconstructs it from that immutable summary
with exact-key and exact-type validation.

This resolves the original mixed-time receipt defect:

- `_duplicate_of()` cannot accept a caller or retry-time report;
- the duplicate path performs no reconciliation against current database
  state;
- all durable result facts come from the winning applied row;
- first-apply and retry `result_facts()` are equal, including after unrelated
  state changes and in both tested concurrency shapes; and
- an unreadable or version-skewed stored summary fails closed as
  `original_result_unavailable` instead of fabricating or recomputing facts.

The retry's `report is None` is coherent rather than a hidden substitute: the
retry performed no reconciliation run. The outcome retains the original
reconciliation in the bounded typed `reconciliation` field, while avoiding
persisting Actor names, field values, and prose merely to recreate a narrative
report. This meets the prior review's requirement for a typed immutable result
sufficient to return equivalent original result facts.

Removing the unused `refusal_code` outcome field does not weaken refusal
handling: refusals remain typed exceptions and do not produce successful
receipts.

## Verification performed

```text
TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv/bin/python -m pytest -q -rs
1566 passed, 1 warning in 9.20s; no skips

./venv/bin/python -m compileall -q application adapters domain tools tests
passed

APP_ENVIRONMENT=test DATABASE_URL=postgresql+psycopg:///freedom_test ./venv/bin/python -m alembic check
No new upgrade operations detected.

git diff --check
passed
```

The warning is the pre-existing `discord.player` deprecation warning for
`audioop`. No formatter, linter, or type checker is configured in the
repository.

## Remaining gate limitations

Phase 2 remains open. The supervised real-export reconciliation, Data Owner
attestation, real-dataset backup/restore rehearsal, operational windows and
retention periods, and the Acceptance Authority's gate decision remain
pending. This review recommends; it does not perform or approve those actions.
