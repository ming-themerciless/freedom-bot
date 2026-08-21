# Prompt for Gemini — P3.4 Step 4 remediation

Date: 2026-08-20 · Status: **AUTHORIZED REMEDIATION OF RELEASED STEP 4**

Peter/Acceptance Authority requested this bounded remediation after independent
review found four Step 4 defects. This continues the already released Step 4;
it does not release Step 5.

This authorization does not accept or close Step 4, release or begin Step 5,
close P3.G4, or authorize staging, deployment, production use, external/live
service contact, secrets, or real-player data.

You are Gemini, the P3.4 production frontend implementer. Correct only F1–F4,
run the required evidence, deliver the checkpoint, and stop.

## Read completely before acting

1. `.agents/AGENTS.md` and `docs/implementation-plan.md`;
2. the corrected P3.4 master implementation prompt;
3. the released Step 4 prompt and Step 3 acceptance record;
4. `docs/review/phase-3-p3-4-step-04-review.md`;
5. route contract §2.3, VM-04 and VM-22 in the view-model contract, the threat
   model, and test traceability contract;
6. the existing disposable-database fixtures and the D-03 `404` byte-identity
   tests, read-only; and
7. every file in the allowlist below.

Record initial `git status --short` and verify every starting digest before any
write. Preserve all unrelated dirty/untracked work and every stash exactly.

## F1 — add real VM-22 HTTP byte-identity evidence

In `tests/web/test_p3_4_auth_and_system_views.py`, add a test marked
`database` that uses the established production application client, settings,
disposable migrated PostgreSQL fixture, and shared portal seed helpers. Build
the smallest synthetic world containing:

- one authenticated ordinary member;
- one character accessible to that member; and
- one real character inaccessible to that member.

Request the inaccessible character, a random absent UUID, and a malformed UUID.
Assert all three responses are `404` and their response bytes are exactly
identical. Also pass the returned body through the positive VM-22 minimization
validator and assert it contains no real character ID/name, UUID-shaped
correlation, guild/timestamp/object detail, or other identifying fact.

Reuse shared test fixtures/helpers rather than creating a second settings or
application authority. Keep database cleanup bounded and consistent with the
existing portal suite. The test must collect and skip with the repository's
standard reason only when `TEST_DATABASE_URL` is absent. Do not merely import or
cite another test, compare direct template renders, or claim HTTP evidence from
source inspection.

## F2 — shared CSS-scope falsification

Refactor the current positive CSS scope assertion in
`tests/web/test_p3_4_shell_and_components.py` into a helper that accepts CSS text
and enforces:

- required Step 2 foundation selectors;
- required Step 3 shell selectors;
- required, actually used Step 4 selectors; and
- absence of every named Step 5-or-later selector.

The existing positive production CSS test must call this helper. Add a negative
test that appends a representative later-step selector such as
`.char-portrait-hero` to in-memory CSS, passes it through the same helper, and
uses `pytest.raises(AssertionError, match=...)` for that exact selector. Do not
make the negative test simply search its own string.

Retain all prior CSS fingerprint/manifest tamper tests and template-security
falsifications.

## F3 — honor both VM-04 configuration facts

Update `emergency.html` so:

- the static WebAuthn/security-key section is rendered only when
  `view.webauthn_supported_hint` is true;
- the R-09 recovery form is rendered only when
  `view.recovery_form_available` is true;
- when either fact is false, render a static, non-sensitive notice that the
  corresponding method is unavailable; and
- the notice reveals no account, enrollment, credential nickname, grant state,
  caller state, reason, or backend/configuration detail.

The R-09 form, when present, must retain exactly `method="post"`, action
`/v1/auth/emergency/recovery`, and the sole successful named field `{token}`—no
`csrf_token` or other named field. No JavaScript/WebAuthn implementation is
authorized.

Expand direct strict-Jinja tests over all four boolean combinations. Assert
section/form presence and absence for each, apply the exact R-09 validator only
when the form is available, and test both failure `None` and an accepted failure
without varying the availability rendering from any account/grant/enrollment
fact. Add a falsification that forces a recovery form into a false-availability
render and fails through a shared availability validator for the intended
reason.

## F4 — remove unused `.auth-lead`

Remove `.auth-lead` and its complete declaration block from the stylesheet.
Add/retain a mechanical test proving each selector newly introduced by Step 4
is used by at least one of the eight Step 4 templates, with `.auth-lead` as a
negative/falsification example. Do not apply this rule to accepted generic
foundation or shell selectors whose consumers may be outside the eight pages.

Because CSS bytes change:

1. remove `freedom-blades.f72398a9d642.css`;
2. create exactly one replacement
   `freedom-blades.<12-lowercase-hex>.css` whose fingerprint matches its full
   SHA-256;
3. update only the CSS reference in `base.html`;
4. update only the CSS line in `asset-integrity.sha256`; and
5. update exact filename/hash assertions in the allowlisted tests.

## Starting digests and overlap guard

Verify exactly:

| File | Required starting SHA-256 |
|---|---|
| `adapters/web/templates/emergency.html` | `589ab11b291a0d24866ed341cb0ecd33ea0c63f076abde3b58947b473762d6ff` |
| `adapters/web/templates/base.html` | `7a135ee0ff6865d9c0de517c1b42662df64dfa694c76f1c32960139cb27f4115` |
| `adapters/web/static/css/freedom-blades.f72398a9d642.css` | `f72398a9d642749e0a20f370365498d33cecfdfee970c8aa60621a4e3ab06686` |
| `adapters/web/static/asset-integrity.sha256` | `39e9183ce283d781a021d6f7d7a1fee2fd3418aaad70cf6a29ea385a37e38977` |
| `tests/web/test_p3_4_auth_and_system_views.py` | `985ea8386cc1bca5f4c1a647a8071c76bbe5c194dc4f24c6c4dd294530ff1421` |
| `tests/web/test_p3_4_shell_and_components.py` | `d73560d8135211f458d6795834d08c2a31b9bba5356f42c1bab95750d75dc443` |
| `tests/web/test_p3_4_static_assets.py` | `edcf0e3bb0ce8339f72f0522619656d16d1e76d5a798fb0f608826c1890e7217` |
| `tests/web/test_static_asset_surface.py` | `810861c26beed7c33bd6762290c1ea5f01698d29bd1585a8bff23b9db656849f` |

The following must remain byte-identical:

- `login.html`: `eafd7635be0b6b8dfb7d60df7a827a49863b5b12bb1cdc0e49ddbd4c0f7d5e3b`;
- `non_member.html`: `de43a127d11f77bfccfb515fa93e3a2ef9373b123c880c1290dcedc1f1721f02`;
- `degraded.html`: `98f3ac888788d24e173fb4a497e0b138c23987b459d29d37b4131c9bbd211915`;
- `denied.html`: `197913db5909d6d9801f599b0a0b2eed47b6384f4e5bd3e38de6e9ae6c686c20`;
- `conflict.html`: `1dda40f2e43212631fba5001e4982748fc5a090b0a32a6be57965daae4805648`;
- `validation.html`: `ff00f7acf78f8d055c3a37af92d0f32230b98fb95aa385b4f327e3851c3e4e7d`;
- `error.html`: `6fdf24733c0b06139434c7b7198cab979438758fb6b8c18175e473b4ad404945`;
- header: `ede238e9d6f83c70eb228b54d58d40fa5b01d6df4c82ce8479c641dc28a46796`;
- footer: `2f1068b436a38a7ef79580aec4b55ed23dcaa5a3b827596509caa000ed72f7c3`;
- HTMX: `71ea67185bfa8c98c39d31717c6fce5d852370fcdfd129db4543774d3145c0de`;
- emblem: `eab0d13128f55b7a367ce9e3ba88a2bad967e37768f7e28d9728186d9d322371`;
- all 15 non-Step-4 template digests already enforced by the tests.

Stop on any mismatch or overlap.

## Remediation allowlist

Only these paths may change:

- `adapters/web/templates/emergency.html`;
- `adapters/web/templates/base.html`, CSS filename only;
- removal of
  `adapters/web/static/css/freedom-blades.f72398a9d642.css`;
- one replacement fingerprinted CSS file;
- `adapters/web/static/asset-integrity.sha256`, CSS line only;
- `tests/web/test_p3_4_auth_and_system_views.py`;
- `tests/web/test_p3_4_shell_and_components.py`;
- `tests/web/test_p3_4_static_assets.py`, only for CSS scope/hash transition;
  and
- `tests/web/test_static_asset_surface.py`, exact CSS filename only.

No other template, include, backend Python, production route/view model,
contract, dependency, configuration, operations/project-management/review
record, prompt, HTMX/emblem asset, or frozen-prototype file may change. Do not
create a submission document; the checkpoint report is the handoff.

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

Report literal commands, exit codes, and pass/fail/skip counts. The new HTTP
test may skip only when `TEST_DATABASE_URL` is absent and must report that exact
reason. All structural/direct-render/falsification tests must run without a
database. Do not install or run a browser.

## Required falsification

Demonstrate through the same helpers used by positive tests:

1. adding a second R-09 named field fails exact inventory;
2. rendering/injecting a recovery form while
   `recovery_form_available=False` fails availability validation;
3. appending `.char-portrait-hero` fails the CSS scope validator;
4. reintroducing `.auth-lead` fails the Step 4 selector-use validator;
5. leaking a correlation/object fact into VM-22 fails minimization; and
6. changing temporary CSS bytes without fingerprint/manifest updates fails both
   validators.

Use in-memory or temporary mutations. Leave no production mutation or temporary
residue.

## Stop conditions

Stop and report `BLOCKED` if:

- any starting/immutable digest differs;
- remediation requires a path outside the allowlist;
- the HTTP case does not collect or uses a second application/settings
  authority;
- any emergency availability combination lies about its accepted VM-04 facts;
- R-09 contains a named field other than `token` when available;
- a Step 5-or-later or unused Step 4 selector remains;
- any falsification does not fail through the positive helper for the intended
  reason;
- HTMX, emblem, an immutable template/include, backend, contract, or frozen
  prototype changes;
- any final non-database check fails; or
- satisfying the work would begin Step 5.

## Checkpoint and stop

Report:

- F1–F4 finding-to-change mapping;
- every changed file with before/after SHA-256;
- all four VM-04 availability combinations and exact R-09 inventory;
- HTTP byte-identity result or the exact database skip;
- old/new CSS names, full digest, removed selector, use/scope proof, and
  manifest result;
- every falsification and its intended observed failure;
- all verification commands with literal result and pass/fail/skip counts;
- immutable-file confirmations, final diff/status, and residual risks; and
- verdict `READY FOR STEP 4 RE-REVIEW` or `BLOCKED`.

Then stop. Do not accept or close Step 4, release or begin Step 5, close P3.G4,
deploy, contact a live service, use external network access, access secrets, or
access real data.

