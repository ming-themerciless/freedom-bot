# Prompt for Gemini — P3.4 Step 3 remediation

Date: 2026-08-20 · Status: **AUTHORIZED REMEDIATION OF RELEASED STEP 3**

Peter/Acceptance Authority released Step 3 on 2026-08-20 and has now requested
this bounded remediation after independent review. This is an authorized
continuation of the already released Step 3, not a release of Step 4.

This authorization does not accept or close Step 3, release or begin Step 4,
close P3.G4, or authorize staging, deployment, production use, external or live
service contact, secrets, or real-player data.

You are Gemini, the P3.4 production frontend implementer. Correct only findings
F1–F3 below, run the required evidence, deliver the checkpoint, and stop.

## Read completely before acting

1. `.agents/AGENTS.md` and `docs/implementation-plan.md`;
2. the corrected P3.4 master implementation prompt;
3. `docs/review/phase-3-p3-4-gemini-execution-plan.md`, Step 3;
4. the Step 1 baseline;
5. the released Step 2 prompt, Step 2 remediation prompt, and Step 2 acceptance
   record;
6. the released Step 3 prompt and its full required-falsification section;
7. all Phase 3 contracts in their prescribed order, especially test
   traceability and threat model; and
8. both files in the remediation allowlist below.

Record initial `git status --short` and verify every starting digest before any
write. Preserve all unrelated dirty and untracked work and every stash exactly.

## Independent-review findings to remediate

### F1 — falsification does not exercise the production guards

The three tests under `Falsification Tests` currently mutate or hard-code a bad
string and merely assert that the defect exists. They do not pass the mutation
through the same validator used by the positive production guard and do not
prove that the guard fails for the intended reason. The released Step 3 prompt
made ineffective falsification a stop condition.

Refactor the test module to expose focused assertion helpers used by both the
positive tests and falsification tests. Each falsification must pass mutated
input through the real helper and assert the expected failure with
`pytest.raises(AssertionError, match=...)` (or an equally specific, deterministic
exception contract). Do not duplicate a weaker expression in the falsification
test.

The real helpers and falsifications must cover all five originally required
classes:

1. skip-link target removal and skip-link movement after another focusable
   element;
2. a second `aria-current="page"` for a representative route;
3. each forbidden corpus class: inline handler, remote origin, `|safe`, and
   `design-prototype/` reference;
4. a dynamic include and an `ignore missing` include; and
5. CSS byte tampering without updating the filename fingerprint or manifest,
   proving failure of both the fingerprint validator and integrity validator.

Mutations may be in-memory or use a bounded temporary directory. Do not mutate
the production files for falsification. If a production-file mutation is truly
unavoidable, restore it byte-for-byte and prove restoration by SHA-256 before
any final suite; prefer not to do this.

### F2 — unsupported extension block

`base.html` contains `{% block head_extra %}{% endblock %}`, but the Step 3
checkpoint identifies no concrete existing consumer. The released prompt
permitted a new extension block only where a concrete later consumer was
already identified.

Remove this block. Retain the existing title and content blocks and all accepted
shell behavior. Add a focused assertion that the unneeded `head_extra` block is
absent; do not prohibit existing contractually required blocks.

### F3 — child-template preservation is not actually enforced

`test_child_templates_extend_base_and_remain_intact` claims that all 23
starting page/fragment templates remain intact, but it only counts them and
checks that non-fragments extend `base.html`. A byte change could pass.

Define an explicit immutable mapping in the test module from each of the 23
Step 1 paths below to its accepted SHA-256. Assert exact set equality and digest
equality before checking the child/fragment structural role. Do not derive the
expected map from current files, Git state, another mutable manifest, or the
implementation under test.

| Template | Accepted Step 1 SHA-256 |
|---|---|
| `account_identities.html` | `f3ab67ec4f0eb9b10555fe5263b871b15c1d18bfd15dc2ae6bf0a8c39bf7f0d5` |
| `audit_results.html` | `11ee0efcba8892970dee0870b5612d0fbf9c5091d5cf954ddf77e4af4f98291e` |
| `audit_search.html` | `c54db1a4cc1779a52921269641330f79d295a843086eb198916a2f07c6e61c15` |
| `character_detail.html` | `7be58ab1bb9436fda39801ff4a31e4c938301b1c335e0fe53e1411ca795c4cf4` |
| `character_links.html` | `fbdbfe0c761304a77928b569568a8b79be3ef25ed4ae4a51fee6eb57c89cfa8b` |
| `conflict.html` | `3aa735cde72995d016782b6308ddc61e310a4a6bfde6258441351380306d6d86` |
| `council_characters.html` | `cffc9bbb63773028deb4b0056c9a9d2c82a185c8f00a91530a623efd62c81661` |
| `council_snapshots.html` | `0b216a54636e3d8d9715fa08028fcf853af888d5ca26611da5155656ba04bf4d` |
| `degraded.html` | `56ea9c866df7d883abe8a62197acefcec9d5d5ad3da59f31c37206ce1f2fd799` |
| `denied.html` | `5f29922f6b48739d03874b3afb3a41953dc0bd0185b25d982800e860dd0c5305` |
| `emergency.html` | `8d2b4bb671e8c8b4b9fbef4b37f745d46622b6be5e965e2fcbb712faea7dd61a` |
| `error.html` | `60ac158aebf5758a6e7f219b7230d372843bff77a0d395fbcaf8bb36154a20c2` |
| `field_profile.html` | `06a2b6a5e389b6c936f016df95069b82c26741dba5e402ae2c9ad0d306181e91` |
| `identity_migration.html` | `ededffd5adb842bd0a33bb6f3f098c0497d3d6935d5827ecac02727af849a878` |
| `identity_search.html` | `fe5cb51fdfdcf5a829a7569766321ad6b8b555f8dbc3b520b94158a028c53f6e` |
| `import_result.html` | `152b84f766211b886ddd67ca1ce03c53cb37ceefc9ea5678cd22f7f2b7f3fff6` |
| `job_status.html` | `b106fe0f2e7f807fef4462504bf23e669e731accac309a1157cdcdc17146a0ea` |
| `job_status_fragment.html` | `4993979df628907b7639916e6e3e47d0b1ed795854e393c5bc47e4af7682b2b1` |
| `login.html` | `1fee4161bddea58712de35ab952cdaa7c892450d0c2ee20b47ee8d333c7879a4` |
| `my_characters.html` | `28eb6391c37e50383103ad05ef98d0fd3d6669117edb73251de570f0871ccf72` |
| `non_member.html` | `565e9f1697e66fae2e0db3e4f0dd7bd1a0b3bf12fc5817652b424968fb0b76c7` |
| `role_capabilities.html` | `bf1ce7d09096b8d41fcde29fc170bf43615d462a7e7015a13de89b3f3d4a0b3b` |
| `validation.html` | `54deb119e685eb264405db013ee43b3076214e4f0d9026d84821a606764a2a65` |

Also add a falsification using a temporary copied corpus or a helper input that
changes one byte of one child template and proves the same preservation helper
fails with a path-specific digest mismatch. Do not change a production child or
fragment template.

## Starting digests and overlap guard

Before editing, verify exactly:

| File | Required starting SHA-256 |
|---|---|
| `adapters/web/templates/base.html` | `553e4afc5044320083ec120aca945231ca0127adb585d0dd44e3d7455da1395e` |
| `tests/web/test_p3_4_shell_and_components.py` | `f3797eb177ceb211ab869e3a94bf5aed749ecc24b09327d7e7fa948de116c87c` |
| `adapters/web/templates/includes/header.html` | `ede238e9d6f83c70eb228b54d58d40fa5b01d6df4c82ce8479c641dc28a46796` |
| `adapters/web/templates/includes/footer.html` | `2f1068b436a38a7ef79580aec4b55ed23dcaa5a3b827596509caa000ed72f7c3` |
| `adapters/web/static/css/freedom-blades.e82fec19acd3.css` | `e82fec19acd3322066330a8a48a7d832446227fc9f805a0ffe54e6c7d9c12599` |
| `adapters/web/static/asset-integrity.sha256` | `08f6c81f09488749b6caefcc0da6c86efef03e220da8a2d2dc7334429a1f394b` |
| `adapters/web/static/vendor/htmx-2.0.10.71ea67185bfa.min.js` | `71ea67185bfa8c98c39d31717c6fce5d852370fcdfd129db4543774d3145c0de` |
| `adapters/web/static/images/freedom-blades-token.eab0d13128f5.png` | `eab0d13128f55b7a367ce9e3ba88a2bad967e37768f7e28d9728186d9d322371` |
| `tests/web/test_p3_4_static_assets.py` | `f9d0076f6a2dfdebf486f0087939772f2c9174842a78230c592f56de8c4efdfa` |
| `tests/web/test_static_asset_surface.py` | `c11f0c6624ecd5a45034a87f1d38beeed07347038081dec8c94d116cebf6eff2` |

Verify the 23 template digests in F3 as well. Stop and report `BLOCKED` on any
mismatch or overlap.

## Remediation allowlist

Only these files may change:

- `adapters/web/templates/base.html`, solely to remove the unused `head_extra`
  block; and
- `tests/web/test_p3_4_shell_and_components.py`, solely for F1–F3.

Everything else must remain byte-identical, including header, footer, CSS,
manifest, HTMX, emblem, all 23 child/fragment templates, Step 2 tests, backend
Python, routes, view models, contracts, dependencies, configuration, operations
documents, project-management records, prior review records/prompts, and the
frozen prototype. Do not create a submission document; the checkpoint report is
the handoff.

## Test-design constraints

- One production validator/helper must govern each positive and corresponding
  negative assertion; do not make a negative test prove only its own mutation.
- Helpers must accept explicit text, rendered markup, paths/root, or manifest
  data so bounded mutations can traverse the same logic.
- Failure matching must identify the intended invariant, not merely accept any
  exception.
- Keep the real strict Jinja rendering and complete production corpus checks.
- Preserve all currently passing Step 3 and Step 2 controls; do not weaken an
  assertion, inventory, autoescape, M-01 behavior, or security pattern.
- Synthetic and temporary data must be bounded and contain no player data.
- Tests must not require a database, network, browser, secret, alternate
  settings authority, or live service.

## Required verification

Run locally without network or live services:

```bash
sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256
sha256sum -c adapters/web/static/asset-integrity.sha256
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_shell_and_components.py
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py tests/web/test_structural_guards.py -m "not database"
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py tests/web/test_structural_guards.py
./venv-web/bin/python -m compileall -q tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py
git diff --check
git diff --name-only
git status --short
```

Report commands literally with exit codes and pass/fail/skip counts. Database
skips are acceptable only when `TEST_DATABASE_URL` is absent. Any non-database
failure, fixture error, warning hidden as success, or incomplete command is a
blocker.

## Required falsification checkpoint

Report every F1 and F3 falsification with:

- the mutation supplied to the production helper;
- the exact helper invoked by both positive and negative tests;
- the expected failure message/invariant;
- the observed passing falsification-test result; and
- confirmation that no production file was changed, or its before/restored
  SHA-256 if an unavoidable file mutation occurred.

A mutation being detectable by inspection is not evidence. The validator must
raise for the intended reason, and the `pytest.raises` assertion must pass.

## Stop conditions

Stop and report `BLOCKED` if:

- a starting or immutable digest differs;
- any remediation requires a path outside the two-file allowlist;
- a child/fragment template, include, CSS, manifest, asset, Step 2 test,
  backend, contract, configuration, dependency, or frozen prototype would need
  modification;
- any positive test and its falsification do not use the same helper;
- a falsification does not fail for its intended, specifically asserted reason;
- temporary or mutation residue remains;
- any final non-database check fails; or
- satisfying the work would begin Step 4.

## Checkpoint and stop

Report:

- finding-to-change mapping for F1–F3;
- both changed files with before/after SHA-256;
- exact removal of `head_extra` and confirmation that title/content behavior is
  retained;
- all 23 immutable-template digest results;
- validator/helper mapping and every falsification result;
- every verification command with literal output summary, exit code, and
  pass/fail/skip counts;
- final `git diff --check`, `git diff --name-only`, and `git status --short`;
- confirmation that all non-allowlisted paths and the visual freeze remained
  byte-identical; and
- verdict `READY FOR STEP 3 RE-REVIEW` or `BLOCKED`.

Then stop. Do not accept or close Step 3, release or begin Step 4, close P3.G4,
deploy, contact a live service, use external network access, access secrets, or
access real data.
