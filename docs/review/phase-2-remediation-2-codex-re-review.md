# Phase 2 remediation 2 — Codex independent implementation re-review

Date: 2026-08-03

Role: Independent Reviewer under implementation plan §16.4

Scope: the uncommitted working tree on `docs/platform-plan`, with `HEAD` at
`c8a3da9`, answering the seven findings recorded in
`phase-2-codex-findings-ba42467.md`.

This is a recommendation, not approval. The Acceptance Authority records the
gate decision. The supervised real-export rehearsal was not performed, and the
two prohibited Foundry sources were not accessed.

## Result

**Recommendation: remediate again before the supervised real-export
rehearsal.** Six original findings are resolved. B-1 is partly resolved because
the new operation binding correctly refuses reuse for different input, but an
identical retry still does not return one coherent original result.

## Original findings

| Finding | Re-review result | Basis |
|---|---|---|
| B-1 — bind request keys to their operation | **Partly resolved** | `operation_digest`, its database constraint, sequential/concurrent conflict handling, and different-input refusals correctly bind the key. The retry receipt defect below remains. |
| B-2 — display-name reconciliation direction | **Resolved** | Direction is an explicit required field-profile property. A Foundry rename reports `platform_display_name_stale`, preserves the stable mapping, changes no character value, and does not advise changing Foundry. |
| I-1 — safe database/concurrency translation | **Resolved** | The unit of work supplies a translating session for every repository operation; uniqueness losers are classified from structured diagnostics and re-read in a fresh transaction, while other database failures become `PersistenceError`. Tests reject raw driver/ORM exceptions and cover real PostgreSQL races. |
| I-2 — enforce audit-content policy | **Resolved for implementation review** | Required/optional per-action policies are enforced at each write site; undeclared actions and keys fail closed; `display_name` and free-text bootstrap refusal reason were removed. The separate security review raises a data-minimization concern about verbatim request keys. |
| I-3 — validate comparable readers at composition | **Resolved** | `ComparableFieldReaders` validates every database-authority field when the import service is constructed, while the domain profile remains independent of persistence readers. |
| I-4 — strengthen negative guards | **Resolved** | Concatenated literals are folded, the limitations are documented, and migrated-schema, import-graph, ORM metadata, and behavioral no-write evidence provide the decisive checks. |
| O-1 — normalize `PUBLIC` privileges | **Resolved** | The template revokes `PUBLIC` privileges across every retained table and schema creation; live tests seed hostile grants and verify PostgreSQL's effective privileges afterward. |

## Finding

### B-1R — identical retries mix the original durable result with a new reconciliation report (Blocking)

`SnapshotImportService._duplicate_of()` says it returns the original result, but
reconciles the artifact again against the database's current state and places
that new report beside the original import ID, correlation ID and mutation
counts (`application/foundry/import_service.py:688`). Immediately after the
first import, the original report describes an unmapped/create candidate while
the retry report describes the now-mapped character. Later unrelated database
changes can make it differ further. The receipt therefore combines facts from
two times and is not the “original result” required by B-1 and plan §6.5.

The regression test at `tests/test_snapshot_import_service.py:899` checks only
that the report is service-generated and has the same checksum; it does not
compare the report with the stored original summary or test internal agreement
between the report and original counts.

Persist or reconstruct a typed immutable result sufficient to return the
original result on a same-operation retry. Add a test proving the first and
retry outcomes carry equivalent result facts, including after the database has
changed, while retaining the new different-operation refusal behavior.

Classification: **Blocking** — idempotency/rule correctness and durable receipt
consistency.

## Judgement calls from the handover §5

1. The operation-digest field cut is sound. Excluding volatile aggregate
   versions is necessary for retry semantics; including folder path is
   consistent with ADR 0006 folder identity. Authorization should remain an
   apply-time check rather than part of the operation identity.
2. The verbatim request-key decision does not alter this implementation-review
   result, but the separate security report recommends minimizing it in audit.
3. Removing `display_name` from character-created audit payloads is correct;
   stable platform and external IDs provide identity and provenance.
4. A follow-on `0003` migration is correct. Failing closed on non-empty legacy
   rows is safer than fabricating a digest. An explicit precondition with an
   operator-facing message would be clearer, but its absence is not a further
   gate finding under the documented no-durable-application premise.
5. The combined real threaded invariants, deterministic PostgreSQL branch tests,
   and fake ordering tests are sufficient concurrency evidence. Testing the
   private resolver is justified here.
6. A five-character SQLSTATE is useful classification rather than database
   content. Keeping it in `PersistenceError` is acceptable.
7. Revoking `PUBLIC` broadly is appropriate least-privilege normalization for
   this deployment. The existing operational warning is sufficient now; future
   reporting/backup roles must receive explicit grants.
8. The behavioral no-write test is the right decisive shape, supported by the
   migrated-schema and import-graph evidence rather than by AST scans alone.

## Verification performed

```text
TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv/bin/python -m pytest -q
1523 passed, 1 warning in 8.92s
```

There were no skips. The warning is the pre-existing `discord.player` `audioop`
deprecation warning. I did not rerun the destructive Alembic rehearsal because
the submitted evidence and full migrated-database suite cover it, and this
review did not mutate a database outside the test suite.

The Phase 2 gate remains open independently of this finding: the supervised
real-export reconciliation, Data Owner attestation, backup/restore rehearsal,
and unset operational windows remain Acceptance Authority/owner work.
