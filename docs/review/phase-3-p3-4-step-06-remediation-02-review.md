# P3.4 Step 6 remediation 02 independent re-review

Date: 2026-08-20

Status: **REMEDIATION 03 REQUIRED AND RELEASED**

Implementer: Gemini · Independent reviewer: Codex · Acceptance authority: Peter Duscha

## Result

Remediation 02 corrected the production invariant wording, uses bound
connections for connection-only helpers, and substantially completes the
R-22–R-27 authorization, CSRF, stale-version and successful-mutation matrix.
All production findings are closed. Three test-evidence findings remain.

## Remaining findings

1. Refused R-25/R-26/R-27 requests do not compare audit-event state before and
   after, so zero audit side effects are not proved.
2. The object-denial comparison proves equal status and body only. It does not
   compare the accepted security-relevant headers or use equivalent shared
   denial-response semantics required by remediation 02.
3. The cleanup validator accepts any assertion in a second connection block.
   It would accept `assert True` or an unrelated `SELECT 1`. The real fixture
   checks table totals for two tables rather than tracking and proving absence
   of the identifiers created by the database case.

## Verification

- Both integrity manifests passed.
- Focused suite: 32 passed, 1 database skip.
- Non-database combined suite: 220 passed, 64 skipped, 3 deselected.
- Combined suite: 220 passed, 67 skipped.
- Compilation and `git diff --check` passed.
- PostgreSQL evidence did not run because `TEST_DATABASE_URL` was absent.

## Governance

Peter's instruction to update documentation and write the next remediation
prompt authorizes and releases the one-file remediation 03. No repeat approval
is required. Step 6 remains unaccepted; Step 7 remains unreleased.
