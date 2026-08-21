# P3.4 Step 6 remediation 05 independent re-review

Date: 2026-08-20

Status: **REMEDIATION 06 REQUIRED AND RELEASED**

Implementer: Gemini · Independent reviewer: Codex · Acceptance authority: Peter Duscha

## Result

Remediation 05 respected the one-file boundary and corrected the denial helper
to require exact production security headers, including `cache-control`. It
also expanded structural validation of snapshot helpers and refusal sequences.
Two related defects remain:

1. `snapshot_r25_state` filters `audit_events.entity_id` with the character ID.
   Production `CharacterAccessService._event()` always assigns the access ID to
   `entity_id`; R-25 generates that access ID only during a successful grant.
   Therefore an erroneous R-25 audit event would not be detected by the current
   character-ID predicate.
2. The structural validator accepts any audit SQL containing `audit_events`,
   `WHERE`, and `entity_id`, without verifying SQL/parameter data flow against
   production attribution. It also accepts any awaited client call rather than
   the correct POST route and does not reject an intervening mutation.

The correct R-25 stable predicate is based on production audit facts available
without knowing the generated access ID: `action = 'character_access.granted'`,
`entity_type = 'character_access'`, and JSON payload
`character_id = str(character_id)` (optionally also the target account payload).
R-26/R-27 may continue to use their already-known access ID as `entity_id`, with
the exact expected action where useful.

Verification: integrity manifests passed; focused suite 94 passed and one
database skip; non-database combined suite 282 passed, 64 skipped and three
deselected; combined suite 282 passed and 67 skipped; compilation and
`git diff --check` passed. PostgreSQL did not run because `TEST_DATABASE_URL`
was absent.

Peter's instruction to document and include all context authorizes and releases
remediation 06. Step 6 remains unaccepted; Step 7 remains unreleased.
