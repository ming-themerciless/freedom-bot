# Prompt for Gemini — P3.4 Step 5 bounded remediation 02

Date: 2026-08-20 · Status: **RELEASED BY PETER / ACCEPTANCE AUTHORITY**

This prompt addresses only R2-1 through R2-3 from
`phase-3-p3-4-step-05-remediation-review.md`. Peter's single instruction to
write it for Gemini to fix the reviewed issues authorized and released it, as
clarified in `phase-3-p3-4-remediation-release-policy-clarification.md`.

Edit one test file only, run the required verification, report
for independent re-review, and stop. Do not begin Step 6 or change production.

## Read before acting

Read completely:

1. `.agents/AGENTS.md` and `docs/implementation-plan.md`;
2. the P3.4 master prompt and execution plan;
3. the released Step 5 prompt, remediation-01 prompt, initial Step 5 review,
   and remediation-01 re-review;
4. the accepted VM-05/VM-06 and R-20/R-21 contracts;
5. `tests/web/test_p3_4_member_views.py` and the shared portal fixtures; and
6. the complete current diff and `git status --short`.

Preserve all unrelated changes and stashes. Do not provision a database, read
secrets/`.env`, contact external services, or use real data.

## Starting state and one-file allowlist

The sole permitted write is:

`tests/web/test_p3_4_member_views.py`

Its required starting SHA-256 is:

`ab9ee88d3ea06ed689169919466f9725dd64bd52bf7eadfd08c98b7b6578de4a`

Verify it before writing. Every production file, other test, asset, template,
prompt, contract, documentation record, dependency and configuration file is
immutable. In particular, preserve every review-time digest listed in
`phase-3-p3-4-step-05-remediation-review.md` other than the sole allowed test.

Stop on any mismatch, overlap, or need for another file.

## R2-1 — pass a real connection to cleanup

Correct `clean_between_member_cases` to use the accepted safe pattern after
yield:

```python
engine = request.getfixturevalue("migrated_database")
with engine.begin() as connection:
    clean_p3_2_tables(connection)
```

Continue resolving `migrated_database` only when the test requests it. Cleanup
must run after success or assertion failure. Do not change shared fixtures or
database production code.

## R2-2 — one teardown validator, two real falsifications

Create one callable structural validator for the member cleanup fixture. It
must prove from the actual fixture source/AST that:

- exactly one yield occurs;
- database resolution and cleanup occur only after yield;
- cleanup is conditional on `migrated_database` being requested;
- the engine opens a transaction/context yielding a connection; and
- `clean_p3_2_tables` receives that connection, not the engine.

Use the same validator for the positive production fixture and for separate
negative fixture/source probes that fail specifically when:

1. cleanup occurs before yield;
2. cleanup is absent after yield; and
3. the engine is passed directly instead of a connection.

Do not duplicate validator assertions inside individual negative tests.

## R2-3 — exact selector definition and template use

Extend the shared Step 5 CSS validator so every selector supplied as required:

1. is defined as an exact active CSS class selector after stripping CSS block
   comments; and
2. is used as an exact active class token in `my_characters.html` or
   `character_detail.html`, after stripping Jinja comments.

The helper must distinguish exact tokens from prefixes/substrings and must not
count selector names occurring only in CSS comments, selector longer names,
declaration values, Jinja comments, prose, data attributes, or unrelated text.
Accept compound selectors and comma-separated selector groups when the exact
class token is genuinely active.

Use this same helper in the positive production CSS/template test. Add
deterministic probes through it for:

- a genuine active and used selector (positive);
- an otherwise permitted active selector that is not used by either Step 5
  template;
- a required selector mentioned only in a single-line CSS block comment;
- a multiline CSS comment/prose mention;
- a longer selector such as `.character-card-extra`;
- a declaration/string value containing `.character-card`;
- a class appearing only in a Jinja comment;
- a longer template class token; and
- an unterminated CSS block comment, which must fail safely.

Where a mutation needs the real production rule removed, do so only in memory
with a deterministic helper and prove the active exact selector is absent
before appending the probe. Do not mutate production files.

Retain the existing prohibited-selector check, manifest/fingerprint helper,
temporary tamper evidence, deferred-field evidence, zero-control evidence, and
database-marked HTTP test.

## Required verification

Run and report literally:

```bash
sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256
sha256sum -c adapters/web/static/asset-integrity.sha256
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_member_views.py
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_member_views.py tests/web/test_p3_4_auth_and_system_views.py tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py tests/web/test_structural_guards.py -m "not database"
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_member_views.py tests/web/test_p3_4_auth_and_system_views.py tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py tests/web/test_structural_guards.py
./venv-web/bin/python -m compileall -q tests/web/test_p3_4_member_views.py tests/web/test_p3_4_auth_and_system_views.py tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py
git diff --check
git status --short
```

Report pass/skip counts, exact before/after test hash, proof that every immutable
digest stayed exact, and whether PostgreSQL actually ran. A skip is not database
evidence.

## Stop and handoff

Stop on any required production/shared-test/backend change, unsafe database
configuration, mismatch, overlap or contract discrepancy. At successful
completion report:

`READY FOR INDEPENDENT STEP 5 REMEDIATION 02 RE-REVIEW`

Then stop. Do not begin Step 6 and do not claim Step 5 acceptance.
