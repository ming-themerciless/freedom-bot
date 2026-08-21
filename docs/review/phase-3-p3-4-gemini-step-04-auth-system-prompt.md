# Prompt for Gemini — P3.4 Step 4: authentication and system-state pages

Date: 2026-08-20 · Status: **RELEASED BY PETER / ACCEPTANCE AUTHORITY** · Step: 4 of 13

Peter/Acceptance Authority explicitly released this bounded Step 4 prompt on
2026-08-20 after accepting Step 3. Perform Step 4 only, deliver its checkpoint,
and stop. This release does not authorize Step 5 or any later step, P3.G4
closure, staging, deployment, production use, external/live-service contact,
secrets, or real-player data.

You are Gemini, the P3.4 production frontend implementer. Perform Step 4 only,
deliver its checkpoint, and stop.

## Read completely before acting

1. `.agents/AGENTS.md` and `docs/implementation-plan.md`;
2. the corrected P3.4 master implementation prompt;
3. `docs/review/phase-3-p3-4-gemini-execution-plan.md`, Step 4;
4. the Step 1 baseline and Step 2 acceptance record;
5. every released Step 3 prompt/remediation, review record, and Step 3
   acceptance record;
6. `docs/contracts/README.md` and all Phase 3 contracts in their prescribed
   order, especially route authorization §§2.3, 3.3 and 5.1, view models VM-01
   through VM-04 and VM-19 through VM-22, threat model, and test traceability;
7. the production route handlers that render the eight allowlisted templates;
8. `docs/operations/web-portal.md` and M-01 `/static/`; and
9. the visual-prototype handoff/freeze manifest and the eight current templates.

Record initial `git status --short`. Verify all starting hashes and required
absences before writing. Preserve unrelated dirty/untracked work and every stash
exactly.

## Objective

Convert only these eight inherited page bodies to the accepted production
visual system while preserving their frozen route and view-model contracts:

- `login.html` — VM-01, R-02;
- `emergency.html` — VM-04, R-06 and recovery form R-09;
- `non_member.html` — VM-02;
- `degraded.html` — VM-03;
- `denied.html` — VM-22;
- `conflict.html` — VM-19;
- `validation.html` — VM-21; and
- `error.html` — VM-20.

Add only Step 4 CSS used by those pages and focused structural/rendering tests.
Every essential link/form flow must work without JavaScript. Do not alter routes,
handlers, view models, authorization, response status/headers, or application
logic.

## Starting hashes

Verify exactly:

| File | Required SHA-256 |
|---|---|
| `adapters/web/templates/login.html` | `1fee4161bddea58712de35ab952cdaa7c892450d0c2ee20b47ee8d333c7879a4` |
| `adapters/web/templates/emergency.html` | `8d2b4bb671e8c8b4b9fbef4b37f745d46622b6be5e965e2fcbb712faea7dd61a` |
| `adapters/web/templates/non_member.html` | `565e9f1697e66fae2e0db3e4f0dd7bd1a0b3bf12fc5817652b424968fb0b76c7` |
| `adapters/web/templates/degraded.html` | `56ea9c866df7d883abe8a62197acefcec9d5d5ad3da59f31c37206ce1f2fd799` |
| `adapters/web/templates/denied.html` | `5f29922f6b48739d03874b3afb3a41953dc0bd0185b25d982800e860dd0c5305` |
| `adapters/web/templates/conflict.html` | `3aa735cde72995d016782b6308ddc61e310a4a6bfde6258441351380306d6d86` |
| `adapters/web/templates/validation.html` | `54deb119e685eb264405db013ee43b3076214e4f0d9026d84821a606764a2a65` |
| `adapters/web/templates/error.html` | `60ac158aebf5758a6e7f219b7230d372843bff77a0d395fbcaf8bb36154a20c2` |
| `adapters/web/templates/base.html` | `3048bd5bb561dfc5f26bfbf30353f7ddd474d804ebe65c2c5349a1b2f5566585` |
| `adapters/web/templates/includes/header.html` | `ede238e9d6f83c70eb228b54d58d40fa5b01d6df4c82ce8479c641dc28a46796` |
| `adapters/web/templates/includes/footer.html` | `2f1068b436a38a7ef79580aec4b55ed23dcaa5a3b827596509caa000ed72f7c3` |
| `adapters/web/static/css/freedom-blades.e82fec19acd3.css` | `e82fec19acd3322066330a8a48a7d832446227fc9f805a0ffe54e6c7d9c12599` |
| `adapters/web/static/asset-integrity.sha256` | `08f6c81f09488749b6caefcc0da6c86efef03e220da8a2d2dc7334429a1f394b` |
| `tests/web/test_p3_4_shell_and_components.py` | `340e311602d8396bf38a7bf20b0d7206de87feec3e2ed96a7127406483657248` |
| `tests/web/test_p3_4_static_assets.py` | `f9d0076f6a2dfdebf486f0087939772f2c9174842a78230c592f56de8c4efdfa` |
| `tests/web/test_static_asset_surface.py` | `c11f0c6624ecd5a45034a87f1d38beeed07347038081dec8c94d116cebf6eff2` |

These paths must be absent:

- `tests/web/test_p3_4_auth_and_system_views.py`; and
- any Step 4-specific include under `adapters/web/templates/includes/`.

The HTMX and emblem must retain their accepted full digests:

- HTMX: `71ea67185bfa8c98c39d31717c6fce5d852370fcdfd129db4543774d3145c0de`;
- emblem: `eab0d13128f55b7a367ce9e3ba88a2bad967e37768f7e28d9728186d9d322371`.

Stop on any mismatch, unexpected presence, or overlap.

## Allowlist

Only these paths may change after explicit release:

- the eight templates named in the objective;
- `adapters/web/templates/base.html`, only to replace the exact CSS filename;
- removal of `adapters/web/static/css/freedom-blades.e82fec19acd3.css`;
- one replacement
  `adapters/web/static/css/freedom-blades.<12-lowercase-hex>.css`, whose filename
  fingerprint equals its full content SHA-256;
- `adapters/web/static/asset-integrity.sha256`, only for the CSS replacement;
- `tests/web/test_p3_4_shell_and_components.py`, only to transition its template
  preservation map for the eight authorized Step 4 templates, retain exact
  digest protection for all 15 untouched page/fragment templates, update the
  accepted CSS digest used by falsification, and permit only Step 4 CSS scope;
- `tests/web/test_p3_4_static_assets.py`, only where an exact CSS filename or
  Step 3-only selector-scope assertion becomes obsolete;
- `tests/web/test_static_asset_surface.py`, only to update the exact CSS
  filename; and
- new `tests/web/test_p3_4_auth_and_system_views.py`.

Do not create new includes in Step 4. Header, footer, all 15 non-Step-4
page/fragment templates, HTMX, emblem, backend Python, routes, view models,
contracts, dependencies, configuration, operations/project-management/review
records, prompts, and `design-prototype/` must remain byte-identical.

## Shared page requirements

- Retain `{% extends "base.html" %}`, one page-owned `<h1>`, meaningful heading
  order, semantic regions, ordinary links/forms, labelled controls, and visible
  focus supplied by the accepted shell/CSS.
- Render only accepted view-model fields and closed-vocabulary codes. Do not
  infer facts, authority, identity, status, totals, timestamps, or prose.
- Preserve autoescaping; use no `|safe`, `Markup`, inline handler, `hx-on:`,
  inline executable script, remote origin/font, dynamic include, or prototype
  reference.
- User-controlled synthetic probes such as `<script>`, `"><img onerror>`,
  `{{7*7}}`, long values, RTL overrides, and NFC/NFD variants must render inert
  and remain bounded by the existing view-model authority.
- Do not add page-specific JavaScript, HTMX dependency, dialog, modal, client
  calculation, hidden authority fact, or mutation control not already required
  below.
- Make no WCAG audit/conformance, browser, real-device, AT, staging, deployment,
  or production-readiness claim.

## Screen requirements

### Login — VM-01 / R-02

- Render `ready` and `error` states from `view.providers`, `view.degraded`, and
  `view.failure` only.
- Enabled providers are ordinary same-origin path anchors using accepted
  `start_path`; disabled providers are visibly unavailable and not actionable.
- Preserve controlled provider display/key data, degradation code, failure code,
  and correlation reference without provider error prose.
- Show the emergency-access link only when
  `view.emergency_access_available` is true.
- Do not create a login POST form or remote Discord URL.

### Emergency access — VM-04 / R-06 and R-09

- Preserve the non-enumerating page: no account, credential nickname,
  enrollment, recovery-grant state, or caller-state disclosure.
- The recovery form is exactly `method="post"`, action
  `/v1/auth/emergency/recovery`, and contains one successful named field:
  `token`. It contains no `csrf_token`, username, account, redirect, nonce,
  credential ID, or other named input.
- Label the password/token control and retain ordinary no-JavaScript submission.
- Render failure only from the accepted closed code and correlation.
- Do not invent passkey/WebAuthn JavaScript in this step. Existing R-07/R-08
  remain backend contract routes, not authorization for new script here.

### Non-member — VM-02

- Retain the distinct membership-recovery context: closed denial category,
  guild display name, checked-at display value, and correlation.
- Render no role, character, other-member, capability, or raw provider detail.

### Degraded — VM-03

- Explain fail-closed temporary unavailability using only state, closed denial
  category, subsystem, grace-expired fact where useful, and correlation.
- Do not display cached roles/authority, infrastructure details, tracebacks, or
  retry promises not present in the view model.

### Generic denial — VM-22

- This page may render only `state` and `reason.category`, plus static text and
  a stable ordinary recovery/navigation link.
- It must contain no correlation, timestamp, guild, object identifier,
  free-form reason/detail, username, role, capability, or conditional object
  fact.
- Preserve byte-identical bodies for absent-object and unreachable-object 404
  responses (route contract §2.3, TC-OBJ-07). Do not add request-varying shell
  data or attributes.

### Conflict — VM-19

- Render stale/conflict state, `conflict`, accepted `current` display facts, and
  correlation without creating a blind retry or mutation form.
- Preserve the existing P3.3 `stale_reason` and `confirm` conditional facts;
  render them as escaped server-provided closed/display values only.
- Do not submit checksum, folder, profile version, aggregate version, nonce, or
  any action from this system-state page.

### Validation — VM-21

- Render a visible validation summary with at most the accepted bounded errors,
  using `field`, closed `code`, and optional `limit` only.
- Provide deterministic focusable anchors only when there is a real matching
  field target already present in the same response. Because this generic page
  owns no original form fields, do not fabricate target controls or broken
  fragment links; a focusable summary container is sufficient.
- Do not echo rejected input or free-form validation prose.

### Safe error — VM-20

- Render only static safe text, `message_code`, and correlation.
- Never render exception text, traceback, SQL, filesystem path, request body,
  secret, object detail, or arbitrary diagnostic data.

## CSS requirements

- Retain all accepted Step 2 foundation and Step 3 shell selectors.
- Add only selectors actually used by the eight Step 4 templates: bounded auth
  panels, provider actions, system-state/error surfaces, labelled form fields,
  validation summary/list, reference text, and conflict/current-state display.
- Use the accepted tokens, system fonts, responsive/reflow-safe sizing, local
  overflow only, visible focus, and reduced motion.
- Do not add character/profile, Council, identity-administration, snapshot,
  polling/job, audit, receipt, dialog/modal, or later-step component selectors.
- Rename the CSS by its new 12-hex content fingerprint, update `base.html` and
  the integrity manifest atomically, and remove the superseded CSS file.

## Test requirements

Create `tests/web/test_p3_4_auth_and_system_views.py` proving at least:

1. strict Jinja rendering of all eight actual templates with representative
   synthetic VM-shaped data and every applicable state/conditional branch;
2. exactly one page `<h1>`, safe heading order, inherited shell landmarks, and
   no-JavaScript links/forms;
3. login enabled/disabled/degraded/failure/emergency-link behavior without
   inventing fields or remote URLs;
4. R-09 exact action/method and exact successful named-field set `{token}`, with
   explicit absence of `csrf_token` and all unrelated fields;
5. emergency page non-enumeration across representative enrollment/grant/caller
   facts not present in VM-04;
6. VM-02 membership-recovery fields remain distinct from VM-22;
7. VM-03 subsystem/correlation behavior and no cached-authority disclosure;
8. VM-22 source/rendered field minimization and HTTP byte identity for the
   accepted absent-versus-denied 404 case using existing backend fixtures when
   a disposable database is available;
9. VM-19 stale/current/conditional scope rendering without a mutation form;
10. VM-21 bounded field/code/limit rendering, focusable summary, and no broken
    target anchors;
11. VM-20 correlation/code rendering and absence of diagnostic detail;
12. autoescape/inert rendering for the required adversarial strings across
    every user-influenced field these eight views receive;
13. zero `|safe`, inline handler, `hx-on:`, inline executable script, remote
    origin/font, dynamic include, and prototype reference across the complete
    production template corpus;
14. exact template set and digest protection for all 15 untouched templates;
15. CSS scope, fingerprint, manifest integrity, M-01 inventory/cache behavior,
    and unchanged HTMX/emblem bytes; and
16. falsification through shared validators for at least: an added R-09 field,
    a VM-22 correlation/object detail, a broken validation anchor, an inline
    handler/`|safe`, an unauthorized later-step CSS selector, and CSS bytes
    changed without fingerprint/manifest updates.

Tests must use production helpers for positive and corresponding negative
cases, with specific expected failures. Do not merely assert that a mutation
string exists. Structural/direct-render tests must run without a database.
Database-backed HTTP rows may skip only when `TEST_DATABASE_URL` is absent and
must say so explicitly; do not replace HTTP evidence with a source claim.

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

Report commands literally with exit codes and pass/fail/skip counts. Database
skips are acceptable only when `TEST_DATABASE_URL` is absent. Browser checks are
not part of Step 4 and must not be installed or claimed. Any non-database
failure, fixture error, warning hidden as success, or incomplete command is a
blocker.

## Stop conditions

Stop and report `BLOCKED` if:

- Step 4 authorization has been withdrawn;
- any starting hash/absence differs;
- a backend, route, view model, authorization rule, response status/header,
  contract, dependency, configuration, or non-allowlisted template must change;
- a screen needs a fact or authority not carried by its accepted view model;
- VM-22 cannot remain minimal or absent/denied 404 bytes diverge;
- R-09 requires any named field other than `token`;
- a later-step component/page is needed;
- HTMX, emblem, header, footer, or an untouched template digest moves;
- falsification does not fail through the positive validator for the intended
  reason; or
- any final non-database check fails.

## Checkpoint and stop

Report:

- screen-by-screen VM/route/state/change mapping;
- every changed file with before/after SHA-256 (`absent` where new);
- old/new CSS names, exact digest, selector scope, and manifest result;
- exact R-09 field inventory and VM-22 minimization/byte-identity evidence;
- tests with literal results and evidence classes;
- all falsification/restoration results;
- skipped/not-run checks and residual risks;
- immutable hashes for header, footer, HTMX, emblem, visual freeze, and all 15
  untouched templates;
- final `git diff --check`, `git diff --name-only`, and status; and
- verdict `READY FOR STEP 5 REVIEW` or `BLOCKED`.

Then stop. Do not begin or release Step 5, close P3.G4, deploy, contact a live
service, use external network access, access secrets, or access real data.
