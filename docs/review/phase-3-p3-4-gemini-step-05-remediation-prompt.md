# Prompt for Gemini — P3.4 Step 5 bounded remediation 01

Date: 2026-08-20 · Status: **RELEASED BY PETER / ACCEPTANCE AUTHORITY**

This bounded remediation prompt was authorized and released by Peter's single
instruction to write it for Gemini to fix the reviewed issues, as clarified in
`phase-3-p3-4-remediation-release-policy-clarification.md`. Correct only
findings F1–F5 below, run the required verification, report for independent
re-review, and stop. This is not Step 5
acceptance and does not release Step 6 or later work, P3.G4 closure, database
provisioning, staging, deployment, secrets, live services, or real data.

## Read before acting

Read completely:

1. `.agents/AGENTS.md` and `docs/implementation-plan.md`;
2. the corrected P3.4 master prompt and execution plan;
3. the released Step 5 prompt;
4. `phase-3-p3-4-step-05-review.md`;
5. the accepted VM-05/VM-06 and R-20/R-21 contracts;
6. the current production/test files in the allowlist; and
7. the complete current diff and `git status --short`.

Preserve unrelated changes and all stashes exactly. Verify every starting hash
below before writing. Stop on mismatch or overlap.

## Starting hashes

Use the review-time hashes in `phase-3-p3-4-step-05-review.md`, including:

- `my_characters.html`: `2afdd64b487fc517e93336cf88a17871bf44a7bc54c643cb9911a8cad78b31fd`;
- `character_detail.html`: `7524e43e0e2ee814b5c8b65365f4e0d72bcb9c1e42e4087ea927e3934c0c9890`;
- `base.html`: `59368ce280fe0f9925bed48bc252d81349a048f8dc5bbfd0e5d8ec4c721ec829`;
- CSS: `f434a78cdfee9d45a43b8b02065474e4fde1d8456356e75050c6e9944c57a498`;
- manifest: `b65f8badbc104f26ab8f16ec2877218221ca7544b61c4b233260cd605c6a7a69`;
- member tests: `81edec2c290a0d04a71527f0b5f38a87c93b0ded30b5962a49984d09b058f29f`;
- auth/system tests: `90553f30b516d64832fe813ed591ffd2aa028d07b92b60de5171882692758da6`;
- shell tests: `86cc9a44e918945eeb43bdf8d59b5ba534ac40bc5b8ddf5348bbcaa55eddd379`;
- static-asset tests: `61c612d254f4fbf409dd5368e424aafc074e92fbd966a68d4048a232ff5b83d0`;
- static-surface tests: `f44f266e3f4826b37ee855411152ba6b9b13a018c9a127860105fc21885758fe`.

The HTMX, emblem, header and footer must still have their previously accepted
full digests. `character_detail.html` is immutable in this remediation.

## Exact remediation allowlist

Only these paths may change:

- `adapters/web/templates/my_characters.html`;
- `adapters/web/templates/base.html`, CSS filename only;
- removal/replacement of the one fingerprinted CSS file;
- `adapters/web/static/asset-integrity.sha256`, CSS entry only;
- `tests/web/test_p3_4_member_views.py`;
- `tests/web/test_p3_4_auth_and_system_views.py`, **only** the two Step 5
  template digests and directly corresponding count/name/docstring wording;
- `tests/web/test_p3_4_shell_and_components.py`, only new remediation template
  and CSS digests plus removal of the four disallowed selector expectations;
- `tests/web/test_p3_4_static_assets.py`, exact replacement CSS facts only; and
- `tests/web/test_static_asset_surface.py`, exact replacement CSS filename only.

Everything else is immutable, including `character_detail.html`, all other
templates, header/footer, backend Python, routes, view models, contracts,
prompts/review records, HTMX, emblem, dependencies and prototype files.

## F1 — repair the prompt-owned stale digest map

In `test_p3_4_auth_and_system_views.py`, transition only the expected digests
for `my_characters.html` and `character_detail.html` to the final remediation
digests. Adjust the directly corresponding test name/docstring/count wording so
it accurately describes the protected non-Step-4 corpus after Step 5. Do not
change any auth/system behavior, helper, database test, fixture, or assertion.

Because `my_characters.html` changes again below, compute its final digest
before inserting it. `character_detail.html` must remain exactly
`7524e43e0e2ee814b5c8b65365f4e0d72bcb9c1e42e4087ea927e3934c0c9890`.

## F2 — remove the duplicate button-styled action

From `my_characters.html`, remove the duplicate `char-card-actions` block and
its `View details` anchor. Retain the character-title anchor using the accepted
`detail_path`; it is the sole detail navigation for each card.

Remove exactly these now-unused selectors/rules from CSS:

- `.char-card-actions`;
- `.btn`;
- `.btn-secondary` (including visited/hover variants); and
- `.btn-sm`.

Remove them from Step 5 selector expectations and add a falsification proving
that a `.btn*` class or button-styled duplicate action is rejected by the same
zero-control/authority helper used on production output. Do not remove accepted
form-button styling used by the Step 4 emergency page.

Recompute the CSS fingerprint, rename the file, update `base.html`, the
integrity manifest, and exact CSS expectations atomically.

## F3 — database teardown and R-20 empty HTTP evidence

In the member-view test module, add an autouse yield-based finalizer equivalent
to the accepted Step 4 cleanup pattern:

- yield before cleanup;
- resolve `migrated_database` only for a test that requests it;
- invoke shared `clean_p3_2_tables` after the test, including assertion failure;
  and
- add non-database structural falsifications that reject cleanup before yield
  and missing cleanup after yield.

Extend the database-marked HTTP evidence to request R-20 as a valid ordinary
member with no active character links and assert the `200` first-class empty
state and Council-managed recovery text. Preserve populated R-20, authorized
R-21, and byte-identical inaccessible/absent/malformed `404` evidence.

Do not provision a database. Skip only when `TEST_DATABASE_URL` is absent and
report that no PostgreSQL evidence ran.

## F4 — make deferred rejection entry-specific and real

Refactor `validate_deferred_fields_strict` so it finds each rendered deferred
entry by exact field identity and verifies within that entry:

- exact owning package;
- the `migration deferred` marker;
- no displayed value beyond the controlled key/package/marker presentation;
- no `form`, `input`, `button`, `select`, `textarea`, editable/contenteditable,
  action/method, or hidden-authority control.

Use unambiguous structural attributes or markup as necessary in the existing
member test/helper only; `character_detail.html` is immutable, so the validator
must validate its current `data-field-key` entry structure.

Add separate negative probes that preserve the marker/package but inject:

1. a fabricated value such as `500 gp`; and
2. an editable or hidden control.

Both must fail through the same helper used for the production render.

## F5 — shared production validators and missing falsification

Extract callable helpers from the positive Step 5 checks for:

- zero mutation/button-styled/hidden-authority controls;
- active CSS selector scope and exact template use; and
- CSS filename fingerprint plus manifest byte integrity against an explicit
  root/path, so temporary copied/tampered bytes can be validated.

Use those exact helpers in positive production tests and in negative tests.
Add/repair falsifications proving rejection of:

- a hidden authoritative field/control;
- a `.btn*` duplicate action;
- an unused selector and a prohibited Step 6+ selector;
- comment-only, longer-name and declaration-value selector mentions where
  relevant to exact use; and
- temporary CSS bytes modified without matching filename/manifest updates.

Do not merely compare strings or restate the helper logic inside the negative
test. Copy the CSS and manifest to `tmp_path`, prove the shared positive helper
passes before mutation, mutate the temporary CSS, then prove that same helper
fails. Leave production bytes untouched.

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

Also report exact before/after hashes, allowlist compliance, database execution
or skips, evidence class, and every check not run.

## Stop and handoff

Stop on any starting-hash mismatch, overlap, required backend/template change
outside the allowlist, unsafe database configuration, or contract discrepancy.
At successful completion report:

`READY FOR INDEPENDENT STEP 5 REMEDIATION RE-REVIEW`

Then stop. Do not begin Step 6 and do not claim Step 5 acceptance.
