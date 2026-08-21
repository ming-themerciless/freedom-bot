# P3.4 Step 5 independent review

Date: 2026-08-20

Status: **SUPERSEDED BY REMEDIATION RE-REVIEW; STEP 6 NOT RELEASED**

Implementer: Gemini

Independent reviewer: Codex

Acceptance and release authority: Peter Duscha

## Scope and result

Codex independently reviewed Gemini's Step 5 ordinary-member character pages
against the released Step 5 prompt, the corrected Gemini implementation plan,
accepted contracts, starting hashes, allowlist, and required verification.

The production rendering is broadly aligned and the focused suite passes, but
five findings prevent Step 5 acceptance. One finding is a contradiction in the
released prompt's test allowlist and is recorded as a coordinator-owned prompt
defect rather than a Gemini scope violation. This review does not accept Step 5
or release Step 6.

## Findings

### F1 — prescribed suite fails because the released prompt froze a stale digest owner

`tests/web/test_p3_4_auth_and_system_views.py` still classifies
`my_characters.html` and `character_detail.html` among its 15 untouched
non-Step-4 templates and requires their pre-Step-5 digests. The released Step 5
prompt required both templates to change while declaring this test module
immutable. Gemini correctly did not edit the module, but the prescribed suite
therefore fails on the new `character_detail.html` digest (and would next fail
on `my_characters.html`).

This is a prompt/allowlist defect. Remediation must authorize only the two
Step-5 digest transitions and corresponding wording in that existing test.

### F2 — duplicate detail link introduces expressly prohibited button styling

`my_characters.html` already links the character title through the accepted
`detail_path`, then adds a second `View details` anchor using `.btn`,
`.btn-secondary`, `.btn-sm`, and `.char-card-actions`. The corrected
implementation plan explicitly prohibits button styling and requires zero
buttons/controls in this read-only step. Remove the duplicate action and the
four now-unused selectors from production CSS.

### F3 — database evidence lacks teardown and R-20 empty HTTP coverage

`test_r20_r21_http_behavior_with_database` cleans the character tables before
seeding but has no post-test cleanup. It may leave character/access rows after
success or assertion failure. It also exercises only the populated R-20 HTTP
state although the prompt requires R-20 ready and empty response evidence.

Add a yield-based finalizer using the shared `clean_p3_2_tables` helper and
prove structurally that cleanup occurs after yield. Exercise an ordinary member
with no active links over HTTP and confirm the first-class empty response.

### F4 — deferred-value/control falsification does not test its claim

`validate_deferred_fields_strict` checks only that each key, package, and the
words `migration deferred` occur somewhere in the whole rendered page. A
deferred entry can also contain a fabricated value or editable control and
still pass. The negative test removes the required phrase rather than injecting
the prohibited value/control.

Make the helper inspect each deferred entry and reject value-bearing or control
markup. Add separate deterministic mutations for a fabricated value and an
editable control, both through the same positive helper.

### F5 — required shared-helper falsification evidence is incomplete

The test module claims a hidden-authoritative-field falsification but contains
none. Its later-step selector case and CSS-tamper case reproduce local
assertions rather than invoking the same validators used by the positive
production check. Refactor the positive CSS/fingerprint/manifest checks into
callable helpers and route the negative cases through them. Add a real hidden
authoritative-field mutation and rejection through the zero-authority/control
helper.

## Verification evidence

| Check | Result |
|---|---|
| Visual freeze manifest | 14/14 passed |
| Static integrity manifest | 3/3 passed |
| Focused Step 5 suite | 22 passed, 1 database-dependent skip |
| Prescribed non-database combined suite | **1 failed**, 165 passed, 64 skipped, 2 deselected |
| Supporting combined suite | **1 failed**, 143 passed, 65 skipped |
| Compilation reached in chained command | not reached after suite failure |
| `git diff --check` | passed independently |

The PostgreSQL tests were collected but skipped because `TEST_DATABASE_URL` was
not configured. No database-backed Step 5 behavior was executed.

## Review-time digests

| File | SHA-256 |
|---|---|
| `adapters/web/templates/my_characters.html` | `2afdd64b487fc517e93336cf88a17871bf44a7bc54c643cb9911a8cad78b31fd` |
| `adapters/web/templates/character_detail.html` | `7524e43e0e2ee814b5c8b65365f4e0d72bcb9c1e42e4087ea927e3934c0c9890` |
| `adapters/web/templates/base.html` | `59368ce280fe0f9925bed48bc252d81349a048f8dc5bbfd0e5d8ec4c721ec829` |
| `adapters/web/static/css/freedom-blades.f434a78cdfee.css` | `f434a78cdfee9d45a43b8b02065474e4fde1d8456356e75050c6e9944c57a498` |
| `adapters/web/static/asset-integrity.sha256` | `b65f8badbc104f26ab8f16ec2877218221ca7544b61c4b233260cd605c6a7a69` |
| `tests/web/test_p3_4_member_views.py` | `81edec2c290a0d04a71527f0b5f38a87c93b0ded30b5962a49984d09b058f29f` |
| `tests/web/test_p3_4_auth_and_system_views.py` | `90553f30b516d64832fe813ed591ffd2aa028d07b92b60de5171882692758da6` |
| `tests/web/test_p3_4_shell_and_components.py` | `86cc9a44e918945eeb43bdf8d59b5ba534ac40bc5b8ddf5348bbcaa55eddd379` |
| `tests/web/test_p3_4_static_assets.py` | `61c612d254f4fbf409dd5368e424aafc074e92fbd966a68d4048a232ff5b83d0` |
| `tests/web/test_static_asset_surface.py` | `f44f266e3f4826b37ee855411152ba6b9b13a018c9a127860105fc21885758fe` |

The accepted HTMX, emblem, header, footer, Step 4 auth/system test, and all
non-Step-5 production template digests were otherwise preserved.

## Verdict

Peter's instruction to write the bounded remediation prompt also authorized and
released it under the subsequently clarified single-approval rule. Gemini
completed it and Codex re-reviewed it. See
`phase-3-p3-4-step-05-remediation-review.md`. Step 6 and every later step remain
unreleased.
