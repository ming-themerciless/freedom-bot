# Prompt for Gemini — P3.4 Step 4 remediation 03

Date: 2026-08-20 · Status: **AUTHORIZED CONTINUATION OF RELEASED STEP 4 REMEDIATION**

Peter/Acceptance Authority requested this final single-file correction after
independent re-review found R3. This continues the already released Step 4; it
does not release Step 5.

This authorization does not accept or close Step 4, release or begin Step 5,
close P3.G4, or authorize staging, deployment, production use, external/live
service contact, secrets, or real-player data.

You are Gemini, the P3.4 production frontend implementer. Correct only R3 in
the one allowlisted test module, run all required evidence, report the
checkpoint, and stop.

## Read completely before acting

1. `.agents/AGENTS.md` and `docs/implementation-plan.md`;
2. the released Step 4 prompt and all three Step 4 remediation prompts;
3. `docs/review/phase-3-p3-4-step-04-remediation-02-review.md`; and
4. `tests/web/test_p3_4_shell_and_components.py` in full.

Record initial `git status --short` and verify every starting/immutable digest
before writing. Preserve unrelated dirty/untracked work and every stash exactly.

## R3 — comments cannot define CSS selectors

`validate_step4_selectors_usage` currently searches raw CSS. A selector
mentioned only inside `/* ... */` is accepted as a real definition when its
class token is used by a template.

Refactor the helper so CSS block comments are removed before selector-definition
validation. The comment remover must:

- remove every `/* ... */` block across lines;
- handle multiple comments in one input;
- leave active CSS outside comments available for checking; and
- fail safely on an unterminated block comment rather than silently treating
  commented text as active CSS.

Then validate each supplied selector against comment-free active CSS as a real
class selector token. Preserve exact token behavior: `.auth-card` must not be
satisfied by `.not-auth-card`, `.auth-card-extra`, a declaration value, prose,
or an escaped/commented occurrence. Template usage must continue to require an
exact class token from active template markup with Jinja comments removed.

Do not add a dependency or implement a general CSS parser. A small,
deterministic helper for this bounded structural guard is sufficient.

## Required positive and negative coverage

The existing production positive test must continue to pass the real stylesheet
and accepted `STEP_4_SELECTORS` through
`validate_step4_selectors_usage`.

Add parameterized falsification through this exact helper proving an otherwise
template-used selector is rejected when it appears only as:

1. a single-line CSS block comment;
2. a multiline CSS block comment;
3. prose inside a CSS block comment;
4. a longer/different selector such as `.auth-card-extra`; and
5. a declaration/string value rather than a selector.

For comment cases, remove the selector's real production rule in memory before
adding the comment-only occurrence. Assert the specific failure:

`Selector '.auth-card' is not defined as an active CSS class selector in stylesheet`

Also add positive probes proving:

- real `.auth-card { ... }` outside comments is accepted;
- comments before/after a real selector do not hide it; and
- multiple unrelated comments do not affect active selector detection.

Add a separate falsification for an unterminated `/*` comment with a specific
failure reason. Positive and negative cases must use the same comment-removal
and selector-use helpers.

Retain the `.auth-lead` expanded-selector falsification, later-step selector
falsification, template token matching, CSS fingerprint/manifest tampering, and
all prior shell/security guards unchanged in effect.

## Starting digest and exact allowlist

Verify before editing:

| File | Required starting SHA-256 |
|---|---|
| `tests/web/test_p3_4_shell_and_components.py` | `d14660edf0098befcf8cdcbda9ef9b5d0f1ff3e98d0cd2f45a7bb1ecc09420dd` |

Only that file may change.

The following must remain byte-identical:

| File | Required immutable SHA-256 |
|---|---|
| `tests/web/test_p3_4_auth_and_system_views.py` | `90553f30b516d64832fe813ed591ffd2aa028d07b92b60de5171882692758da6` |
| `adapters/web/templates/emergency.html` | `0eec75c17bb6ea602fabc7aace0aaf1453e70fd102e61da5298759e094980a99` |
| `adapters/web/templates/base.html` | `d095f37624d1ce37a9f92ecccde9b6a8d0d407aba55052bb79f1f6050fe1c79d` |
| `adapters/web/static/css/freedom-blades.da727b328510.css` | `da727b32851014c26d2131bcab24be4cf660c8a3f83360acf3330281c2a0b1a9` |
| `adapters/web/static/asset-integrity.sha256` | `e04efc4f036f70e18b8096184174642ce4bbfdf727f446961d1876c6830822ae` |
| `adapters/web/static/vendor/htmx-2.0.10.71ea67185bfa.min.js` | `71ea67185bfa8c98c39d31717c6fce5d852370fcdfd129db4543774d3145c0de` |
| `adapters/web/static/images/freedom-blades-token.eab0d13128f5.png` | `eab0d13128f55b7a367ce9e3ba88a2bad967e37768f7e28d9728186d9d322371` |
| `tests/web/test_p3_4_static_assets.py` | `edcf0e3bb0ce8339f72f0522619656d16d1e76d5a798fb0f608826c1890e7217` |
| `tests/web/test_static_asset_surface.py` | `dfd7ff956ea8f61d6cbbb98f9273dc9627f34365a8ec1da3d544c389abaf9b19` |

All templates/includes and all 23 accepted template digests must remain green.
Stop on any mismatch or overlap.

## Test-design constraints

- The production helper and every falsification use the same active-CSS
  normalization and exact selector validation.
- Do not make a negative test prove only that its mutation string exists.
- Do not count CSS comments, declaration values, prose, or longer selector names.
- Do not weaken the template-side exact class-token check.
- No production, database, route/view-model, contract, configuration,
  dependency, documentation, or frozen-prototype file may change.
- No database, network, browser, secret, live service, or real data is needed.

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

Report literal commands, exit codes, and pass/fail/skip counts. The existing
VM-22 HTTP test may skip only when `TEST_DATABASE_URL` is absent. Every new R3
test must execute without a database. Do not install or run a browser.

## Stop conditions

Stop and report `BLOCKED` if:

- any starting/immutable digest differs;
- a path outside the one-file allowlist must change;
- a selector present only in a CSS comment, value, prose, or longer class name
  passes usage validation;
- an unterminated comment is silently accepted;
- a real active selector is rejected;
- `.auth-lead` or any prior falsification stops using its accepted positive
  helper or stops failing for the intended reason;
- any final non-database check fails; or
- satisfying the work would begin Step 5.

## Checkpoint and stop

Report:

- R3 change mapping and the test file's before/after SHA-256;
- active-CSS normalization contract;
- every comment/value/longer-name falsification and every positive probe;
- all verification commands with literal result and pass/fail/skip counts;
- immutable hashes, final diff/status, and residual risks; and
- verdict `READY FOR STEP 4 RE-REVIEW` or `BLOCKED`.

Then stop. Do not accept or close Step 4, release or begin Step 5, close P3.G4,
deploy, contact a live service, use external network access, access secrets, or
access real data.

