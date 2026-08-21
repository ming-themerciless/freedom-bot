# P3.4 Step 4 remediation independent re-review

Date: 2026-08-20

Status: **SUPERSEDED BY REMEDIATION 02 RE-REVIEW; STEP 4 STILL OPEN**

Implementer: Gemini

Independent reviewer: Codex

Acceptance and release authority: Peter Duscha

## Scope and result

Codex independently re-reviewed Gemini's completed Step 4 remediation against
the authorized remediation prompt. The four original production/evidence
findings were addressed, but two test-only defects remain. This review does not
accept Step 4 or release Step 5.

## Original findings now resolved

1. A database-marked VM-22 HTTP test now requests inaccessible, absent, and
   malformed character identifiers and compares their `404` response bytes.
2. The positive CSS-scope helper now rejects named later-step selectors, with a
   real `.char-portrait-hero` falsification.
3. `emergency.html` honors both VM-04 availability facts, with all four boolean
   combinations covered and R-09 present only when recovery is available.
4. `.auth-lead` was removed from production CSS and the fingerprint/manifest
   chain was updated consistently.

## Remaining findings

### R1 — database test does not clean its character rows after execution

`test_vm22_http_absent_and_inaccessible_byte_identity` calls
`clean_p3_2_tables` before it seeds data but has no post-test character cleanup.
The shared `clean_portal_tables` autouse fixture removes identity/session data,
not `character_access` or `characters`. This can leave rows that pollute later
database tests and differs from the established D-03 module's bounded
post-test cleanup.

### R2 — `.auth-lead` falsification bypasses the selector-use validator

The `.auth-lead` negative test invokes `validate_css_scope_and_primitives`, not
`validate_step4_selectors_usage`. The usage helper called by the positive test
only checks the fixed required selector tuple and cannot reject an unexpected
unused Step 4 selector. Therefore the required positive/negative shared-helper
evidence is not present.

## Verification evidence

All executed commands returned exit code 0:

| Check | Result |
|---|---|
| Visual freeze manifest | 14 files OK |
| Static integrity manifest | 3 files OK |
| Focused Step 4 suite | 26 passed, 1 database skip |
| Supporting suite | 108 passed, 64 database-dependent skips |
| Combined suite | 134 passed, 65 database-dependent skips |
| Compilation | passed |
| `git diff --check` | passed |

`TEST_DATABASE_URL` was absent, so the new VM-22 HTTP case was collected but not
executed. That skip is permitted; it does not excuse the teardown defect visible
in source.

## Review-time digests

| File | SHA-256 |
|---|---|
| `tests/web/test_p3_4_auth_and_system_views.py` | `052380269bde3f492a1a5ed689e6db88cdb1d490811295aab818a650b3db9ce1` |
| `tests/web/test_p3_4_shell_and_components.py` | `da586ae7270b29a6d53a0543003047feaaa2e5ca0123383310aa802cde402384` |

## Verdict

This was the remediation-01 re-review verdict. Gemini completed remediation 02;
independent re-review confirmed R1 and R2 were corrected but found one
comment-handling defect in the selector-use helper. See
`phase-3-p3-4-step-04-remediation-02-review.md`. Step 4 remains open and Step 5
remains unreleased.
