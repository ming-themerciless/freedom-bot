# Prompt for Gemini — P3.4 Step 5 bounded remediation 03

Date: 2026-08-20 · Status: **RELEASED BY PETER / ACCEPTANCE AUTHORITY**

This prompt addresses only R3-1 from
`phase-3-p3-4-step-05-remediation-02-review.md`. Peter's single instruction to
write it for Gemini to fix the reviewed issue authorized and released it, as
clarified in `phase-3-p3-4-remediation-release-policy-clarification.md`.

Edit one test file only, verify it, report for independent
re-review, and stop. Do not change production or begin Step 6.

## Read and verify before acting

Read completely:

1. `.agents/AGENTS.md` and `docs/implementation-plan.md`;
2. the P3.4 master prompt and execution plan;
3. the released Step 5 prompt and all three Step 5 review records;
4. the prepared remediation-01 and remediation-02 prompts;
5. `tests/web/test_p3_4_member_views.py`; and
6. the complete current diff and `git status --short`.

The sole permitted write is:

`tests/web/test_p3_4_member_views.py`

Its required starting SHA-256 is:

`630bb8df4cdf23160006b153460a5468e842b9fe319514ee0fdf9770af81ec0a`

Verify it before writing. Every production file, other test, asset, template,
prompt, contract, documentation record, dependency and configuration file is
immutable. Preserve unrelated changes and all stashes. Stop on mismatch,
overlap, or need for another file.

## R3-1 — prove database resolution occurs only after yield

Strengthen the existing shared `validate_member_cleanup_fixture` AST validator.
In addition to its current checks, it must prove all of the following:

1. Exactly one call has the semantic shape
   `request.getfixturevalue("migrated_database")`:
   - the receiver is the fixture's `request` argument;
   - the method is exactly `getfixturevalue`;
   - there is exactly one positional argument;
   - that argument is the literal string `migrated_database`; and
   - no keyword argument or alternative database resolution call is accepted.
2. The resolution call occurs strictly after the sole yield.
3. The resolution call is structurally inside the post-yield branch guarded by
   the `migrated_database` membership check, so non-database tests cannot resolve
   the database fixture.
4. The resolved variable is the same engine whose `.begin()` context binds the
   connection passed to `clean_p3_2_tables`.
5. Cleanup remains strictly after yield, inside the transaction context, and
   receives the bound connection rather than the engine.

Retain all existing positive properties and error specificity.

Use this exact shared validator for the production fixture and every negative
probe. Add at least these new negative cases:

- database resolution before yield with cleanup after yield;
- database resolution outside the membership guard but after yield;
- resolution of a different fixture name;
- resolution through a different receiver/method shape; and
- one resolution feeding a different variable than the engine whose `.begin()`
  supplies the cleanup connection.

Each case must fail for the intended reason. Do not duplicate AST assertions in
the tests and do not merely search source strings.

Retain the existing negative cases for cleanup before yield, missing cleanup,
and passing the engine directly. Retain all Step 5 selector, deferred,
manifest, zero-control, rendering, and HTTP evidence unchanged.

## Independent falsification requirement

Before handoff, run an in-memory probe equivalent to the exact bad fixture from
the review record. The strengthened shared validator must reject it with a
specific assertion showing database resolution occurred before yield. Report
the literal probe result. Do not modify production or test files during the
probe.

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

Report exact before/after hash, pass/skip counts, immutable-hash confirmation,
the independent pre-yield probe, and whether PostgreSQL actually ran. A skip is
not database evidence.

## Stop and handoff

Stop on any required production/shared-test/backend change, unsafe database
configuration, mismatch, overlap, or contract discrepancy. At successful
completion report:

`READY FOR INDEPENDENT STEP 5 REMEDIATION 03 RE-REVIEW`

Then stop. Do not begin Step 6 and do not claim Step 5 acceptance.
