# Prompt for Gemini — P3.4 Step 4 remediation 02

Date: 2026-08-20 · Status: **AUTHORIZED CONTINUATION OF RELEASED STEP 4 REMEDIATION**

Peter/Acceptance Authority requested this final bounded, test-only remediation
after independent re-review found R1 and R2. This continues the already
released Step 4; it does not release Step 5.

This authorization does not accept or close Step 4, release or begin Step 5,
close P3.G4, or authorize staging, deployment, production use, external/live
service contact, secrets, or real-player data.

You are Gemini, the P3.4 production frontend implementer. Correct only R1 and
R2 in the two allowlisted test modules, run the required evidence, report the
checkpoint, and stop.

## Read completely before acting

1. `.agents/AGENTS.md` and `docs/implementation-plan.md`;
2. the released Step 4 prompt and both Step 4 remediation/review records;
3. `tests/web/conftest.py`, especially `clean_portal_tables`;
4. the bounded cleanup fixture in
   `tests/web/test_d03_contract_correction.py`; and
5. both allowlisted test modules in full.

Record initial `git status --short` and verify every starting/immutable digest
before writing. Preserve unrelated dirty/untracked work and every stash exactly.

## R1 — guarantee post-test character cleanup

In `tests/web/test_p3_4_auth_and_system_views.py`, add bounded teardown for any
test that requests `migrated_database`:

- use a yield-based fixture consistent with the established D-03 pattern;
- after the test, resolve the already requested disposable engine and call the
  shared `clean_p3_2_tables` inside `engine.begin()`;
- do not duplicate table lists or SQL cleanup logic;
- do not instantiate a second database, settings, application, or client
  authority; and
- allow the repository's existing `clean_portal_tables` fixture to perform its
  separate identity/session cleanup.

The cleanup must run even if the HTTP test assertion fails. Do not rely on a
cleanup statement at the bottom of the test body or only on pre-test cleanup.

Add a non-database structural test that inspects the module's fixture contract
or otherwise deterministically proves the yield/finalizer invokes
`clean_p3_2_tables` after yielding for database-bearing cases. This guard must
fail through the same validation helper if the teardown call is removed or
moved before `yield`. Do not require PostgreSQL merely to prove fixture order.

The real database HTTP test must remain marked `database`, retain its existing
pre-test bounded cleanup if needed, and continue to prove inaccessible, absent,
and malformed `404` bodies are byte-identical.

## R2 — make selector-use validation reject unexpected Step 4 selectors

Refactor `validate_step4_selectors_usage` in
`tests/web/test_p3_4_shell_and_components.py` so it accepts an explicit set or
tuple of Step 4 selectors to validate rather than reading only a hidden fixed
constant. It must prove for every supplied selector that:

1. the selector is present as a real CSS class selector; and
2. the exact class token is used in at least one of the eight Step 4 template
   sources.

Use token-aware matching. A substring, comment, different class name, or prose
mention must not count as template usage.

The positive production test must call this helper with the accepted
`STEP_4_SELECTORS` and production CSS/templates.

For falsification, create in-memory CSS containing `.auth-lead`, pass the
expanded selector set `STEP_4_SELECTORS + (".auth-lead",)` to this exact same
usage helper, and assert a specific failure that `.auth-lead` is not used by any
of the eight Step 4 templates. The negative test must not rely on
`validate_css_scope_and_primitives` to produce the expected failure.

Retain the separate positive scope helper's prohibition on `.auth-lead`, the
later-step `.char-portrait-hero` falsification, and every prior shell/security,
fingerprint, manifest, and template-digest guard.

## Starting digests and exact allowlist

Verify exactly:

| File | Required starting SHA-256 |
|---|---|
| `tests/web/test_p3_4_auth_and_system_views.py` | `052380269bde3f492a1a5ed689e6db88cdb1d490811295aab818a650b3db9ce1` |
| `tests/web/test_p3_4_shell_and_components.py` | `da586ae7270b29a6d53a0543003047feaaa2e5ca0123383310aa802cde402384` |

Only those two files may change.

The following production files must remain byte-identical:

| File | Required immutable SHA-256 |
|---|---|
| `adapters/web/templates/emergency.html` | `0eec75c17bb6ea602fabc7aace0aaf1453e70fd102e61da5298759e094980a99` |
| `adapters/web/templates/base.html` | `d095f37624d1ce37a9f92ecccde9b6a8d0d407aba55052bb79f1f6050fe1c79d` |
| `adapters/web/static/css/freedom-blades.da727b328510.css` | `da727b32851014c26d2131bcab24be4cf660c8a3f83360acf3330281c2a0b1a9` |
| `adapters/web/static/asset-integrity.sha256` | `e04efc4f036f70e18b8096184174642ce4bbfdf727f446961d1876c6830822ae` |
| `adapters/web/static/vendor/htmx-2.0.10.71ea67185bfa.min.js` | `71ea67185bfa8c98c39d31717c6fce5d852370fcdfd129db4543774d3145c0de` |
| `adapters/web/static/images/freedom-blades-token.eab0d13128f5.png` | `eab0d13128f55b7a367ce9e3ba88a2bad967e37768f7e28d9728186d9d322371` |
| `tests/web/test_p3_4_static_assets.py` | `edcf0e3bb0ce8339f72f0522619656d16d1e76d5a798fb0f608826c1890e7217` |
| `tests/web/test_static_asset_surface.py` | `dfd7ff956ea8f61d6cbbb98f9273dc9627f34365a8ec1da3d544c389abaf9b19` |

All other Step 4 templates retain the immutable digests recorded in the first
remediation prompt, and all 15 untouched templates must continue to pass their
digest guards. Stop on any mismatch or overlap.

## Test-design requirements

- Positive and negative cases must use the exact same validation helper.
- Teardown proof must distinguish code after `yield` from pre-test cleanup.
- The finalizer must execute under assertion failure as a fixture property.
- Selector usage must match exact class tokens in real template markup.
- No production files, database schema, routes, view models, settings,
  dependencies, contracts, or documentation may change.
- Tests must use synthetic data only and must not contact network/live services.

## Required verification

Run locally without network or live services:

```bash
sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256
sha256sum -c adapters/web/static/asset-integrity.sha256
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_auth_and_system_views.py
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py tests/web/test_structural_guards.py -m "not database"
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_auth_and_system_views.py tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py tests/web/test_structural_guards.py
./venv-web/bin/python -m compileall -q tests/web/test_p3_4_auth_and_system_views.py tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py
git diff --check
git diff --name-only
git status --short
```

Report literal commands, exit codes, and pass/fail/skip counts. The VM-22 HTTP
test may skip only when `TEST_DATABASE_URL` is absent. All structural and
falsification tests must execute without a database. Do not install or run a
browser.

## Required falsification checkpoint

Report:

1. the teardown-order helper's positive result on the real fixture;
2. an in-memory mutation moving/removing post-yield cleanup and the helper's
   specific failure;
3. production Step 4 selector-use validation result;
4. expanded selector-set `.auth-lead` falsification through the exact usage
   helper and its specific failure; and
5. confirmation that prior R-09, VM-04, VM-22, later-step CSS, CSS-tamper, and
   template-security falsifications remain green.

## Stop conditions

Stop and report `BLOCKED` if:

- any starting/immutable digest differs;
- a file outside the two-test allowlist must change;
- character/access cleanup is not guaranteed after `yield` on assertion failure;
- teardown proof needs PostgreSQL to run;
- `.auth-lead` does not fail through `validate_step4_selectors_usage` itself;
- selector matching accepts substrings/comments/prose as class usage;
- a prior falsification or any final non-database test fails;
- any production/database schema/configuration/contract file changes; or
- satisfying the work would begin Step 5.

## Checkpoint and stop

Report:

- R1/R2 finding-to-change mapping;
- both changed test files with before/after SHA-256;
- finalizer structure and teardown-order falsification;
- selector-use helper contract and `.auth-lead` falsification;
- every command with literal result and pass/fail/skip counts;
- immutable production hashes, final diff/status, and residual risks; and
- verdict `READY FOR STEP 4 RE-REVIEW` or `BLOCKED`.

Then stop. Do not accept or close Step 4, release or begin Step 5, close P3.G4,
deploy, contact a live service, use external network access, access secrets, or
access real data.

