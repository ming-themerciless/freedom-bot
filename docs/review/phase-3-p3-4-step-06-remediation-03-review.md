# P3.4 Step 6 remediation 03 independent re-review

Date: 2026-08-20

Status: **REMEDIATION 04 REQUIRED AND RELEASED**

Implementer: Gemini · Independent reviewer: Codex · Acceptance authority: Peter Duscha

## Result

Remediation 03 respected its one-file boundary and added audit comparisons for
all nine refused mutations, runtime tracked-ID cleanup, and denial-response
header comparison. Three test-only evidence defects remain:

1. Refused requests compare version and audit count but not the relevant access
   row immediately before/after: R-25 row absence, R-27 default state, and R-26
   active/revocation state.
2. The denial helper invents an ignored-header list rather than deriving the
   exact deterministic/security header set from accepted response semantics.
3. The cleanup validator does not verify the SQL table, `WHERE id` predicate,
   loop-variable parameter binding, query-result assignment, or that the
   assertion compares that result. Unrelated queries and `assert 0 == 0` can
   satisfy it.

Verification: both integrity manifests passed; focused suite 51 passed and one
database skip; non-database combined suite 239 passed, 64 skipped and three
deselected; combined suite 239 passed and 67 skipped; compilation and
`git diff --check` passed. PostgreSQL did not run because `TEST_DATABASE_URL`
was absent.

Peter's instruction to document and prompt the correction is the single
authorization and release of remediation 04. Step 6 remains unaccepted and
Step 7 remains unreleased.
