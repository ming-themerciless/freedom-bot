# P3.4 Step 6 remediation 04 independent re-review

Date: 2026-08-20

Status: **REMEDIATION 05 REQUIRED AND RELEASED**

Implementer: Gemini · Independent reviewer: Codex · Acceptance authority: Peter Duscha

## Result

Remediation 04 respected the one-file boundary. Runtime refusal snapshots now
cover version, audit count and relevant access state. Cleanup validation now
proves exact table, SQL predicate, parameter binding, result assignment and
zero comparison. Two test-evidence defects remain:

1. `cache-control` is absent from the closed denial header set, and the helper
   compares header values only to each other rather than to the accepted exact
   security-policy values.
2. The refusal snapshot validator checks only nine variable-name equalities. It
   does not validate snapshot-helper fields/queries, case-specific audit
   selection, helper arguments, immediate before/request/after ordering, or
   correct R-25/R-26/R-27 helper selection.

Verification: both integrity manifests passed; focused suite 73 passed and one
database skip; non-database combined suite 261 passed, 64 skipped and three
deselected; combined suite 261 passed and 67 skipped; compilation and
`git diff --check` passed. PostgreSQL did not run because `TEST_DATABASE_URL`
was absent.

Peter's instruction to document and prompt the correction is the single
authorization and release of remediation 05. Step 6 remains unaccepted and
Step 7 remains unreleased.
