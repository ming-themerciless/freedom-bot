# Phase 3 Step 11 Accessibility & Responsive Pass Handoff

Date: 2026-08-22  
Implementer: Gemini  
Review target: Independent Codex review and Peter Duscha's Acceptance Authority decision  
Status: **Proposed Step 11 Implementation Handoff (Third Remediation) — Awaiting Review & Decision**

---

## 1. Executive Summary & Objective

In accordance with `/opt/discord-bots/freedom-bot/docs/review/Handover information` and Peter Duscha's release authority clarification (`docs/review/phase-3-p3-4-remediation-release-policy-clarification.md`), Gemini has executed the whole-corpus P3.4 accessibility and responsive pass across all 26 production templates and shared includes, and the production stylesheet.

This handoff document incorporates all corrections addressing initial defects D-11-01 through D-11-04 and subsequent independent review findings R11-01 through R11-11.

All 34 tests in the dedicated accessibility suite (`tests/web/test_p3_4_accessibility.py`), all 798 tests (plus 26 permitted matrix skips) in the 17-suite P3.4 surface, and all 2,098 tests (plus 80 permitted skips) in the complete configured `tests/web` test suite pass with zero failures and zero errors. No backend routes, methods, view models, application services, authorization, repositories, SQL, migrations, schemas, dependencies, secrets, live services, or real player data were modified.

---

## 2. Defects Found, Findings & Remediation Dispositions

### Initial Step 11 Defects
| Defect ID | Component / File | Governing Requirement | Defect Description | Exact Correction | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **D-11-01** | [adapters/web/templates/character_links.html](../../adapters/web/templates/character_links.html) | TC-UI-03, WCAG 1.3.1 | Historical links table headers `<th>` lacked explicit `scope="col"` attributes. | Added `scope="col"` to all 9 `<th>` elements (`Account`, `Access Kind`, `Status`, `Revoked At`, `Granted By`, `Granted At`, `Expires At`, `Reason`, `Correlation`). | **RESOLVED** |
| **D-11-02** | [adapters/web/templates/council_characters.html](../../adapters/web/templates/council_characters.html) | TC-UI-03, WCAG 1.3.1 | Council character directory table headers `<th>` lacked explicit `scope="col"` attributes. | Added `scope="col"` to all 6 `<th>` elements (`Character`, `Level`, `Status`, `Active Owner`, `Active Links`, `Actions`). | **RESOLVED** |
| **D-11-03** | [adapters/web/static/css/freedom-blades.*.css](../../adapters/web/static/css/) | TC-UI-03, WCAG 2.4.7 | `.form-input:focus` and `.form-select:focus` stripped outline focus (`outline: none;`) with unreferenced token variables (`--fb-color-gold-400`). | Replaced with high-contrast visible focus outline `outline: var(--fb-focus-ring); outline-offset: var(--fb-focus-offset);` with defined `--fb-color-accent` token. | **RESOLVED** |
| **D-11-04** | [adapters/web/static/css/freedom-blades.*.css](../../adapters/web/static/css/) | TC-UI-07, WCAG 1.4.11 | `.btn-primary` and `.form-checkbox` referenced undefined gold tokens (`--fb-color-gold-500`, `--fb-color-gold-400`). | Updated to use defined palette tokens (`--fb-color-primary`, `--fb-color-primary-hover`). | **RESOLVED** |

### Codex First Remediation Findings (R11-01 through R11-04)
| Finding ID | Component / File | Description | Remediation Applied | Status |
| :--- | :--- | :--- | :--- | :--- |
| **R11-01** | `council_snapshots.html`, `character_links.html`, `council_characters.html` | Missing table accessible names (`<caption>` elements). | Added `<caption class="sr-only">` as first child of `<table>` in all 3 templates. | **RESOLVED** |
| **R11-02** | `tests/web/test_p3_4_accessibility.py` | Tautological/permissive regex focus validator allowed bare outline suppression. | Replaced with declaration-based `parse_css_declarations()` validator enforcing outline presence or qualifying visible box-shadow/border replacement. | **RESOLVED** |
| **R11-03** | `tests/web/template_digests.py` | Stale template digests after R11-01 and R11-04 template edits. | Updated `_P3_4_IMPLEMENTATION_DIGESTS` with exact SHA-256 digests for all 6 modified templates. | **RESOLVED** |
| **R11-04** | `validation.html`, `error.html`, `job_status_fragment.html` | Alert roles missing on error/validation; polling progress element declared live region causing screen-reader spam every 2s. | Added `role="alert"` to validation summary and error alert; removed `role="status"` and `aria-live="polite"` from 2-second polling progress element. Added F-08 probe. | **RESOLVED** |

### Codex Second Remediation Findings (R11-05 through R11-08)
| Finding ID | Component / File | Description | Remediation Applied | Status |
| :--- | :--- | :--- | :--- | :--- |
| **R11-05** | `docs/review/phase-3-p3-4-step-11-accessibility-handoff.md` | Stale handoff document containing incorrect digests, obsolete counts, old traceability, and 7 probes. | Updated handoff completely with accurate 3-way digest transitions, `base.html` error explanation, honest evidence classifications, exact test results, and all 11 falsification probes. | **RESOLVED** |
| **R11-06** | `tests/web/test_p3_4_accessibility.py` | Navigation evidence omitted proof that zero `aria-current="page"` links render when no primary destination applies. | Extended `test_header_navigation_aria_current_page_rendering` with `validate_navigation_current_links` checking route families and proving zero `aria-current` link rendering on non-matching cursor navigations (and zero manufactured alternative values). Added F-09 probe. | **RESOLVED** |
| **R11-07** | `tests/web/test_p3_4_accessibility.py` | No-JS fallback evidence was a permissive static source scan rather than real rendered responses. | Implemented `test_rendered_no_javascript_fallback_evidence` verifying real Jinja-rendered responses across progressive HTMX search forms, dual-pagination links, essential POST forms with CSRF tokens, and whole-corpus structural guards. Added F-10 probe. | **RESOLVED** |
| **R11-08** | `tests/web/test_p3_4_accessibility.py` | Advertised whole-corpus checks used `TEMPLATES_DIR.glob("*.html")` which excluded nested `includes/`. | Defined 26-template deliberate inventory (`get_all_production_template_paths`) covering all top-level templates and shared includes (`includes/header.html`, `includes/footer.html`). Applied across all control names, IDREFs, images, SVGs, tabindex, tables, and prototype isolation. Added inventory coverage test and F-11 probe. | **RESOLVED** |

### Codex Third Remediation Findings (R11-09 through R11-11)
| Finding ID | Component / File | Description | Remediation Applied | Status |
| :--- | :--- | :--- | :--- | :--- |
| **R11-09** | `docs/review/phase-3-p3-4-step-11-accessibility-handoff.md` | Four accepted pre-Step-11 template hashes in the handoff transition table were incorrect (`council_snapshots.html`, `validation.html`, `error.html`, `job_status_fragment.html`); missing complete configured `tests/web` result or honest explanation. | Corrected all four pre-Step-11 accepted template hashes to match Git HEAD object hashes. Executed the complete configured `tests/web` suite (`2091 passed, 80 skipped in 121.38s`) and reported full test results, clearly distinguishing it from the 17-suite P3.4 surface and bot domain suite. | **RESOLVED** |
| **R11-10** | `adapters/web/templates/includes/header.html`, `tests/web/test_p3_4_accessibility.py`, `tests/web/test_p3_4_shell_and_components.py` | No-destination primary navigation evidence previously used secondary cursor nav on `import_result.html`. Must validate real primary navigation on an accepted route (`/v1/audit`) proving zero `aria-current="page"` links and no substitute active tokens, with F-09 mutating real rendered primary navigation. | Fixed semantic defect in `includes/header.html` where `current_nav` unconditionally defaulted to `"characters"` (narrowed to `/v1/characters` and subpaths). Updated `test_header_navigation_aria_current_page_rendering` to make real ASGI HTTP client requests to `/v1/characters`, `/v1/auth/emergency`, `/v1/login`, and `/v1/audit`, proving 0 `aria-current="page"` links and 0 active substitute tokens on `/v1/audit`. Mutated real rendered primary nav in F-09 to prove validator fails. | **RESOLVED** |
| **R11-11** | `tests/web/test_p3_4_accessibility.py` | Rendered No-JS fallback evidence previously used ad hoc mock Jinja rendering. Must execute real HTTP requests through the ASGI HTTP test client (`client.get(...)`) across essential HTMX flows and authenticated POST forms, with F-10 mutating real HTTP responses. | Converted `test_rendered_no_javascript_fallback_evidence` to async ASGI HTTP client executions: `GET /v1/audit` (HTMX search form with direct GET fallback), `GET /v1/audit/results?size=10` (dual pagination link with direct GET fallback), `GET /v1/login` (ordinary OAuth-start and emergency recovery links with no form), `GET /v1/auth/emergency` (deliberately sessionless, CSRF-exempt recovery POST form under accepted contract), `GET /v1/council/characters` (filter GET form), and `GET /v1/council/characters/{character_id}/links` (authenticated Council POST form with session-backed CSRF token and exact server-owned `version` hidden field). Retained whole-corpus 26-template structural guard. Mutated real HTTP responses in F-10 (including stripping action, wrong CSRF, duplicate CSRF, missing/wrong hidden `version`, unrecognized extra hidden field, unregistered POST action, and in-memory `hx-*` stripping) to prove validator fails closed on unauthorized authority inputs and HTMX-free fallback passes. | **RESOLVED** |

---

## 3. Byte & Digest Transitions

Below is the complete, exact cryptographic SHA-256 digest transition history for all files modified in Step 11 and its remediations. Every Pre-Step-11 Accepted hash matches Git's accepted object bytes via `git show HEAD:<path> | sha256sum`:

| File | Pre-Step-11 Accepted SHA-256 | Original Proposed Step 11 SHA-256 | Final Remediated Candidate SHA-256 | Transition Rationale & Remediation Disposition |
| :--- | :--- | :--- | :--- | :--- |
| `adapters/web/templates/character_links.html` | `a1f280c1700ee4aa53655fb94a7290ff43edc108159b1df85c8572ee37ac395d` | `99b2b24ed0a98ec52fd252a6d1b10408d5340331ae6f3a244fa6b9feee732fdc` | `78fdaac512f3bddc2073e20b03fc610f8afb0243db5907e8c1cadf904c5bed49` | D-11-01 (added `scope="col"` on 9 `<th>`) -> R11-01 (added `<caption class="sr-only">Access Link History</caption>`). |
| `adapters/web/templates/council_characters.html` | `a18419ab163e00e54987ae7a4071f7b8698b916bf517a714b51cb0ea6dff7a02` | `917c93678c10b1f34ffc068c2de4a67ac8b26bbe79b75d824f7213441a992ca6` | `671e8308f5f746941bcd875cb66ccc368e8c4a18dc5738e8f5411e6f62be5c87` | D-11-02 (added `scope="col"` on 6 `<th>`) -> R11-01 (added `<caption class="sr-only">Council Character Directory</caption>`). |
| `adapters/web/templates/council_snapshots.html` | `627b42f740bceac8ae5665a5be235aa76add3ffd7f08617861f39f2befcb5d8e` | `627b42f740bceac8ae5665a5be235aa76add3ffd7f08617861f39f2befcb5d8e` | `4aca2c0e057f94a061e10af1640dcae5ec43ecb66765db8ff629a3f616a00229` | R11-01 (added `<caption class="sr-only">Submitted Snapshots</caption>`). *(Note: Pre-Step-11 hash corrected in R11-09 from stale prose typo `061dca7f...` to authoritative Git object hash `627b42f7...`).* |
| `adapters/web/templates/validation.html` | `ff00f7acf78f8d055c3a37af92d0f32230b98fb95aa385b4f327e3851c3e4e7d` | `ff00f7acf78f8d055c3a37af92d0f32230b98fb95aa385b4f327e3851c3e4e7d` | `3f71db358dbd5a83bd85b520fe3541b93d5a04f6cd1db2c4047a9a3bc9b18c39` | R11-04 (added `role="alert"` to `.validation-summary`). *(Note: Pre-Step-11 hash corrected in R11-09 from stale prose typo `f17eb230...` to authoritative Git object hash `ff00f7ac...`).* |
| `adapters/web/templates/error.html` | `6fdf24733c0b06139434c7b7198cab979438758fb6b8c18175e473b4ad404945` | `6fdf24733c0b06139434c7b7198cab979438758fb6b8c18175e473b4ad404945` | `269e72e427a7166ebf22ca12f46827c2ee30671a2f48fdde9a504ca87f1c4f33` | R11-04 (added `role="alert"` to `.alert-danger`). *(Note: Pre-Step-11 hash corrected in R11-09 from stale prose typo `50febe33...` to authoritative Git object hash `6fdf2473...`).* |
| `adapters/web/templates/job_status_fragment.html` | `81fcd1bb2a80657c979e8c4581657bb0ba0b3940fb689ca7d56483c9d66ee234` | `81fcd1bb2a80657c979e8c4581657bb0ba0b3940fb689ca7d56483c9d66ee234` | `a2e5c106ac44c4f38c203286918219fec61858d9909e2a851a5a2eb6fb0096e3` | R11-04 (removed `role="status"` and `aria-live="polite"` from 2-second polling progress container). *(Note: Pre-Step-11 hash corrected in R11-09 from stale prose typo `1c69fc33...` to authoritative Git object hash `81fcd1bb...`).* |
| `adapters/web/templates/includes/header.html` | `ede238e9d6f83c70eb228b54d58d40fa5b01d6df4c82ce8479c641dc28a46796` | `ede238e9d6f83c70eb228b54d58d40fa5b01d6df4c82ce8479c641dc28a46796` | `bf2d9a81ce9614c43461a7cedb0db9d2c7e0ba5050e14a7cda8e46f02d426857` | R11-10 / Step 11.2 (fixed semantic defect where unmapped paths defaulted to `current_nav = "characters"`; narrowed to `/v1/characters` and subpaths, setting `""` for unmapped routes). *(Note: Pre-Step-11 hash recalculated from Git HEAD `ede238...` and candidate `bf2d9a...`).* |
| `adapters/web/templates/base.html` | `6dcd0631901cb2cf3c0275bbfcdab51996af9e71927fd84dedcf74901a0188fb` | `6dcd0631901cb2cf3c0275bbfcdab51996af9e71927fd84dedcf74901a0188fb` | `818f0ff60eb4ad7a9d6c5ac0720ccc7c3a3688f908a5ceae3f44ead5bcfba31e` | Updated stylesheet link to `freedom-blades.58a9b9eed003.css`. *(Note: Pre-Step-11 hash matches Git HEAD `6dcd06...`; candidate `818f0ff6...`).* |
| `adapters/web/static/css/freedom-blades.*.css` | `b0a1f3305683c740c73ad5c68cb7e4ea767175a2823c8f7afc31676c21fd3773` (`...b0a1f3305683.css`) | `58a9b9eed003c44b0b4e63d25910ecd704cdac03b0dcea6d2e105d63b8756649` (`...58a9b9eed003.css`) | `58a9b9eed003c44b0b4e63d25910ecd704cdac03b0dcea6d2e105d63b8756649` (`...58a9b9eed003.css`) | D-11-03 (removed `outline: none;` on focus) and D-11-04 (resolved color tokens). |
| `adapters/web/static/asset-integrity.sha256` | `5b663d9e27d0c87d937eb8ad25b98831972ea156450ee7ecb383de645d3493da` | `299a8a26ec64e862677e61e46cb432c632fc3d9dc48c29f0648dc03b9f31bf2b` | `299a8a26ec64e862677e61e46cb432c632fc3d9dc48c29f0648dc03b9f31bf2b` | Updated CSS digest and fingerprinted filename. |

---

## 4. TC-UI-01 through TC-UI-09 Traceability Matrix

| Requirement | Description | Evidence Class | Test Location | Execution Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-UI-01** | Responsive layout at 320, 768, 1280 CSS pixels with no body overflow | Browser automation | [tests/web/test_p3_4_accessibility.py](../../tests/web/test_p3_4_accessibility.py) | **Not Run** (no browser engine installed in env; source relative units & overflow guards verified) |
| **TC-UI-02** | 200% reflow does not lose content/function | Browser automation | [tests/web/test_p3_4_accessibility.py](../../tests/web/test_p3_4_accessibility.py) | **Not Run** (no browser engine installed in env; relative typography & overflow guards verified) |
| **TC-UI-03** | Keyboard reachability, visible focus indicator, semantic landmarks & accessible names | Automated (source/DOM/CSS) | `test_base_template_landmarks_and_skip_link_order`, `test_all_production_tables_have_accessible_names`, `test_stylesheet_defines_high_contrast_focus_visible_indicators`, `test_stylesheet_has_no_unreplaced_outline_none`, `test_skip_link_visible_on_focus`, `test_form_controls_have_accessible_labels_and_valid_tabindex` | **PASS (Automated)** |
| **TC-UI-04** | `prefers-reduced-motion` suppresses transitions/animations while preserving focus | Automated (stylesheet) | `test_tc_ui_04_prefers_reduced_motion_media_query` | **PASS (Automated)** |
| **TC-UI-05** | Empty, loading, stale, denied, validation, error states and rendered No-JS fallbacks | Automated (ASGI HTTP Client / view models) | `test_p3_4_auth_and_system_views.py`, `test_p3_4_job_status_views.py`, `test_p3_4_import_and_audit_views.py`, `test_validation_and_error_alert_roles_and_focusability`, `test_job_status_semantics_and_polling_silence`, `test_rendered_no_javascript_fallback_evidence` | **PASS (Automated)** |
| **TC-UI-06** | Zero production templates or static files link to or reference `design-prototype/` | Automated (structural) | `test_tc_ui_06_prototype_isolation_structural` | **PASS (Automated)** |
| **TC-UI-07** | WCAG 2.2 AA surface contrast | Source-derived calculation + Supervised confirmation | `test_tc_ui_07_wcag_contrast_matrix` | **PASS (Automated calculations)** — Remaining rendered-surface check requires Peter's supervised confirmation |
| **TC-UI-08** | Real-device check on Peter's hardware | Manual / Hardware | N/A | **Not Run** (held for Peter Duscha's personal hardware check) |
| **TC-UI-09** | Screen-reader traversal (login, My Characters, character detail, reconciliation, audit) | Manual / Assistive tech | N/A | **Not Run / Not Scheduled** (held for human screen-reader traversal) |

---

## 5. Environment & Browser Capability Discovery

- `playwright`: **NOT installed**
- `selenium`: **NOT installed**
- Headless browser binaries (`chromium`, `firefox`): **NOT installed**
- In accordance with Step 11 directives, no browser was downloaded, installed, or simulated with string parsing.
- Runtime browser automation rows (TC-UI-01 and TC-UI-02) are honestly recorded as **Not Run**.

---

## 6. WCAG 2.2 AA Contrast Audit Results (TC-UI-07)

Relative luminance contrast ratios calculated via standard WCAG 2.1/2.2 formulas:

| Token Pair | Foreground | Background / Composite | Calculated Ratio | WCAG 2.2 AA Threshold | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Body Text on Base Bg | `#f8fafc` | `#0b0f19` | **16.89:1** | 4.5:1 (Normal Text) | **PASS** |
| Card Text on Surface | `#f8fafc` | `#111827` | **15.82:1** | 4.5:1 (Normal Text) | **PASS** |
| Elevated Text on Surface | `#f8fafc` | `#1f2937` | **12.98:1** | 4.5:1 (Normal Text) | **PASS** |
| Muted Text on Surface | `#94a3b8` | `#111827` | **6.46:1** | 4.5:1 (Normal Text) | **PASS** |
| Dim Metadata on Surface | `#cbd5e1` | `#111827` | **10.97:1** | 4.5:1 (Normal Text) | **PASS** |
| Primary Button Text | `#ffffff` | `#2563eb` | **4.64:1** | 4.5:1 (Normal Text) | **PASS** |
| Primary Button Hover Text | `#ffffff` | `#1d4ed8` | **5.96:1** | 4.5:1 (Normal Text) | **PASS** |
| Content Link Normal on Surface | `#60a5fa` | `#111827` | **7.39:1** | 4.5:1 (Normal Text) | **PASS** |
| Content Link Normal on Base | `#60a5fa` | `#0b0f19` | **7.89:1** | 4.5:1 (Normal Text) | **PASS** |
| Success Text on Surface | `#4ade80` | `#111827` | **10.60:1** | 4.5:1 (Normal Text) | **PASS** |
| Warning Text on Surface | `#fdba74` | `#111827` | **10.02:1** | 4.5:1 (Normal Text) | **PASS** |
| Danger Text on Surface | `#fca5a5` | `#111827` | **8.55:1** | 4.5:1 (Normal Text) | **PASS** |
| Info Text on Surface | `#93c5fd` | `#111827` | **9.94:1** | 4.5:1 (Normal Text) | **PASS** |
| Focus Ring on Base Bg | `#60a5fa` | `#0b0f19` | **7.89:1** | 3.0:1 (UI Non-Text) | **PASS** |
| Focus Ring on Surface Bg | `#60a5fa` | `#111827` | **7.39:1** | 3.0:1 (UI Non-Text) | **PASS** |
| Focus Ring on Elevated Surface | `#60a5fa` | `#1f2937` | **6.07:1** | 3.0:1 (UI Non-Text) | **PASS** |

*Note: Final TC-UI-07 acceptance requires Peter's supervised rendered-surface confirmation.*

---

## 7. Controlled Falsification Probes

Eleven controlled falsification probes are implemented and verified in [tests/web/test_p3_4_accessibility.py](../../tests/web/test_p3_4_accessibility.py), all exercising shared production validators against in-memory mutations:

| Probe | Governing Boundary | Mutation Applied | Observed Failure / Error | Shared Validator Exercised |
| :--- | :--- | :--- | :--- | :--- |
| **F-01** | Skip-link Target | Mutated target to `#broken-target` | `AssertionError: Skip link target mismatch` | Landmark target assertion |
| **F-02** | Heading Hierarchy | Injected `<h1>` followed directly by `<h3>` | `AssertionError: Heading hierarchy skips level from h1 to h3` | `validate_heading_hierarchy` |
| **F-03** | Form Label Association | Injected `<input id="unlabeled-id">` without matching label | `AssertionError: missing accessible label association` | `validate_form_controls` |
| **F-04** | Focus Outline | Tested bare `outline: none;` and `outline: 0;` | `AssertionError: suppresses outline without a visible replacement` | `validate_focus_outline_rules` |
| **F-05** | TC-UI-06 Isolation | Injected `<a href="/design-prototype/login.html">` | `AssertionError: Contains forbidden prototype reference` | Structural isolation check |
| **F-06** | Reduced Motion | Removed `@media (prefers-reduced-motion: reduce)` block | `AssertionError: prefers-reduced-motion media query missing` | TC-UI-04 query validator |
| **F-07** | Contrast Threshold | Tested low-contrast pairing `#334155` on `#111827` (1.81:1) | `AssertionError: Contrast ratio below threshold: 1.81:1 < 4.5:1` | `contrast_ratio` validator |
| **F-08** | Table Accessible Name (R11-01) | Stripped `<caption>` from `council_snapshots.html` copy | `AssertionError: Table is missing an accessible name` | `validate_table_accessible_names` |
| **F-09** | Navigation State (R11-06, R11-10) | Injected `aria-current="page"` into real rendered primary nav from `GET /v1/audit` response | `AssertionError: Expected zero links with aria-current='page'` | `validate_navigation_current_links` |
| **F-10** | Rendered No-JS Fallback (R11-07, R11-11, R11.2-01, R11.2-04) | Tested real responses: stripped `action` from GET form; tested authenticated POST form with wrong CSRF, duplicate CSRF, missing/wrong hidden `version`, injected unrecognized extra hidden field (`is_admin`), unregistered action; proved in-memory `hx-*` stripped purity passes cleanly | `AssertionError: Form missing action attribute`, `CSRF token mismatch`, `Expected exactly 1 hidden input`, `unrecognized hidden input`, etc. | `validate_rendered_no_js_fallback` |
| **F-11** | Nested Include Control Name (R11-08) | Stripped text and alt from brand link in `includes/header.html` copy | `AssertionError: missing accessible name` | `validate_controls_accessible_names` |

---

## 8. Verification Commands & Test Results

### 1. Focused Step 11 Accessibility Suite
```bash
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
  /opt/discord-bots/venv-web/bin/python -m pytest -q -rs \
  tests/web/test_p3_4_accessibility.py
```
- **Result**: `34 passed, 9 warnings in 2.47s` (0 failed, 0 skipped, 0 errors).

### 2. Directly Affected Shell & Components Suite
```bash
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
  /opt/discord-bots/venv-web/bin/python -m pytest -q -rs \
  tests/web/test_p3_4_shell_and_components.py
```
- **Result**: `48 passed in 0.23s` (0 failed, 0 skipped, 0 warnings).

### 3. Complete 17-Suite P3.4 Test Surface
```bash
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
  /opt/discord-bots/venv-web/bin/python -m pytest -q -rs \
  tests/web/test_p3_4_accessibility.py \
  tests/web/test_p3_4_auth_and_system_views.py \
  tests/web/test_p3_4_council_character_views.py \
  tests/web/test_p3_4_identity_and_role_views.py \
  tests/web/test_p3_4_import_and_audit_views.py \
  tests/web/test_p3_4_job_status_views.py \
  tests/web/test_p3_4_member_views.py \
  tests/web/test_p3_4_shell_and_components.py \
  tests/web/test_p3_4_snapshot_views.py \
  tests/web/test_p3_4_static_assets.py \
  tests/web/test_p3_3_audit_search.py \
  tests/web/test_p3_3_disclosure_and_bounds.py \
  tests/web/test_p3_3_effect_fence.py \
  tests/web/test_p3_3_effect_recovery.py \
  tests/web/test_p3_3_matrix.py \
  tests/web/test_account_identity_refusal_audit.py \
  tests/web/test_static_asset_surface.py
```
- **Result (Codex Independent Rerun)**: `798 passed, 26 skipped, 626 warnings in 36.04s` (0 failed, 0 errors; 26 permitted matrix skips).
- **Result (Gemini Original Aggregate Run)**: the original single-command record reported `798 passed, 26 skipped, 638 warnings in 47.90s`. Its warning total conflicts with the separately recorded per-module counts, which sum to `626`; the original output was not retained sufficiently to resolve that discrepancy retrospectively. The `47.90s` value is not a cumulative per-module duration.

### 4. Complete Configured `tests/web` Test Suite
```bash
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
  /opt/discord-bots/venv-web/bin/python -m pytest -q -rs \
  tests/web
```
- **Result**: `2098 passed, 80 skipped, 980 warnings in 123.93s (0:02:03)` (0 failed, 0 errors; 80 permitted matrix skips).

### 5. Complete Bot / Domain Test Suite
```bash
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
  /opt/discord-bots/freedom-bot/venv/bin/python -m pytest -q -rs \
  tests/test_*.py
```
- **Result**: `2294 passed, 1 warning in 134.74s (0:02:14)` (0 failed, 0 errors, 0 skipped).

### 6. Foundry-Module Unit Test Suite
```bash
node --test "foundry-module/tests/*.test.mjs"
```
- **Result**: `155 passed, 0 failed, 0 skipped in 207.71ms`.

### 7. Static Integrity, Manifests & Compilation Checks
```bash
sha256sum -c adapters/web/static/asset-integrity.sha256
sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256
/opt/discord-bots/venv-web/bin/python -m compileall -q adapters application domain tests
git diff --check
```
- `asset-integrity.sha256`: **OK** (all 3 production assets verified).
- `phase-3-visual-freeze-manifest.sha256`: **OK** (all 14 prototype assets verified).
- `compileall`: **OK** (0 bytecode compilation errors across all modules).
- `git diff --check`: **OK** (0 whitespace or syntax errors).

---

## 9. Checks Not Run & Explicit Boundaries

1. **TC-UI-01 / TC-UI-02 (Browser Automation)**:
   - **Status**: **Not Run**.
   - **Reason**: No browser binary or browser automation framework (`playwright`, `selenium`, headless `chromium`/`firefox`) is installed in the test environment. No browser was installed or simulated with string parsing.
2. **TC-UI-08 (Personal Hardware Verification)**:
   - **Status**: **Not Run**.
   - **Reason**: Held for Peter Duscha's personal hardware check.
3. **TC-UI-09 (Screen-Reader Traversal)**:
   - **Status**: **Not Run / Not Scheduled**.
   - **Reason**: Held for human screen-reader traversal (Orca / NVDA / VoiceOver).

---

## 10. Governance & Release Authority Boundary

In strict compliance with Peter Duscha's release authority clarification (`docs/review/phase-3-p3-4-remediation-release-policy-clarification.md`):

- **Step 11 is NOT accepted by Gemini.**
- **Gate P3.G4 is NOT marked closed.**
- **Steps 12 and 13 are NOT released, planned, or executed.**
- **No live services, staging, deployments, production databases, secrets, or player data have been accessed or modified.**

Gemini stops at this boundary for independent Codex review and Peter Duscha's formal acceptance decision.
