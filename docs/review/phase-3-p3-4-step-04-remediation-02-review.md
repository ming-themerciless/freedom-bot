# P3.4 Step 4 remediation 02 independent re-review

Date: 2026-08-20

Status: **BLOCKED — ONE TEST-ONLY FINDING REMAINS; STEP 5 NOT RELEASED**

Implementer: Gemini

Independent reviewer: Codex

Acceptance and release authority: Peter Duscha

## Result

Gemini completed the authorized Step 4 remediation 02. Independent re-review
confirmed that post-yield character cleanup and the `.auth-lead` shared-helper
falsification were implemented correctly. One selector-parser defect remains.
This review does not accept Step 4 or release Step 5.

## Resolved remediation-02 findings

1. `tests/web/test_p3_4_auth_and_system_views.py` now has an autouse,
   yield-based finalizer that calls shared `clean_p3_2_tables` after every
   database-bearing test, including assertion-failure teardown.
2. Non-database structural/falsification tests distinguish post-yield cleanup
   from pre-yield or missing cleanup.
3. `.auth-lead` is now passed directly through
   `validate_step4_selectors_usage` using an expanded selector tuple and fails
   because no Step 4 template uses that exact class token.

## Remaining finding R3 — CSS comments count as real selector definitions

`validate_step4_selectors_usage` searches raw CSS with a regular expression and
does not remove CSS comments. Codex replaced the real `.auth-card` rule in
memory with a comment-only mention:

```css
/* .auth-card { } */
```

The helper still passed and emitted the diagnostic `CSS_COMMENT_ACCEPTED`.
Therefore it does not satisfy remediation 02's explicit requirement that a
comment, substring, different class name, or prose mention cannot count as a
real CSS selector. This was an explicit stop condition.

## Verification evidence

All commands returned exit code 0:

| Check | Result |
|---|---|
| Visual freeze manifest | 14 files OK |
| Static integrity manifest | 3 files OK |
| Focused Step 4 suite | 29 passed, 1 database skip |
| Supporting suite | 108 passed, 64 database-dependent skips |
| Combined suite | 137 passed, 65 database-dependent skips |
| Compilation | passed |
| `git diff --check` | passed |

The VM-22 HTTP test was collected but skipped because `TEST_DATABASE_URL` was
absent, which is permitted.

## Review-time digest

`tests/web/test_p3_4_shell_and_components.py`:
`d14660edf0098befcf8cdcbda9ef9b5d0f1ff3e98d0cd2f45a7bb1ecc09420dd`

## Verdict

Step 4 remains **BLOCKED** pending one single-file, test-only correction and
independent re-review. Step 5 and every later step remain unreleased.

