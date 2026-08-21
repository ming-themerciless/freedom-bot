# P3.4 Step 5 remediation 02 independent re-review

Date: 2026-08-20

Status: **SUPERSEDED BY FINAL STEP 5 ACCEPTANCE; STEP 6 RELEASED**

Implementer: Gemini

Independent reviewer: Codex

Acceptance and release authority: Peter Duscha

## Scope and governance result

Codex independently reviewed Gemini's completed Step 5 remediation 02 against
the prepared remediation-02 prompt, accepted contracts, intended one-file
allowlist, and prescribed verification.

The record initially labelled remediation 02 “not released.” Peter subsequently
clarified that his single instruction to write it for Gemini to fix the issues
was its authorization and release. The former remediation-01/remediation-02
authorization-gap interpretation is closed as a Codex documentation/workflow
error, not unauthorized Gemini execution.

## Technically resolved findings

1. `clean_between_member_cases` now resolves the engine after yield, opens
   `engine.begin()` and passes the resulting connection to
   `clean_p3_2_tables`.
2. A shared teardown-source validator is used by the positive fixture test and
   negative cases for cleanup before yield, missing cleanup, and passing the
   engine directly.
3. The Step 5 selector validator now requires exact active CSS definitions and
   exact active class-token use in the two Step 5 templates.
4. Positive and negative selector probes cover unused, prohibited,
   comment-only, multiline-comment, longer selector, declaration value,
   Jinja-comment, longer template-token and unterminated-comment cases.
5. The one-file write boundary was respected and every production/immutable
   digest stayed exact.

## Remaining technical finding R3-1 — validator permits pre-yield database resolution

The remediation prompt required the structural validator to prove that both
database resolution and cleanup occur only after yield. The production fixture
does this correctly, but `validate_member_cleanup_fixture` checks only the
cleanup call's position. It never locates or orders
`request.getfixturevalue("migrated_database")`.

Codex passed this deliberately bad source to the shared validator:

```python
def bad_clean_fixture(request):
    engine = request.getfixturevalue("migrated_database")
    yield
    if "migrated_database" not in request.fixturenames:
        return
    with engine.begin() as connection:
        clean_p3_2_tables(connection)
```

The validator accepted it and emitted:

`PRE_YIELD_RESOLUTION_PROBE: ACCEPTED`

Add exact AST validation for one `request.getfixturevalue` call with the
literal `migrated_database` argument, require it after yield and inside the
guarded post-yield path, and add a negative probe using the shape above.

## Verification evidence

| Check | Result |
|---|---|
| Visual freeze manifest | 14/14 passed |
| Static integrity manifest | 3/3 passed |
| Focused Step 5 suite | 39 passed, 1 database-dependent skip |
| Non-database combined suite | 183 passed, 64 skipped, 2 deselected |
| Combined suite | 183 passed, 66 skipped |
| Compilation | passed |
| `git diff --check` | passed |
| Independent pre-yield-resolution probe | **accepted incorrectly** |

No PostgreSQL evidence ran because `TEST_DATABASE_URL` was absent.

## Review-time digest

`tests/web/test_p3_4_member_views.py`:
`630bb8df4cdf23160006b153460a5468e842b9fe319514ee0fdf9770af81ec0a`

All production and other test hashes remain those recorded in
`phase-3-p3-4-step-05-remediation-review.md`.

## Verdict

Gemini completed remediation 03 and Codex independently re-reviewed it with no
remaining finding. Peter accepted Step 5 and released the separate bounded Step
6 prompt. See `phase-3-p3-4-step-05-review-and-acceptance.md`. Step 7 and every
later step remain unreleased.
