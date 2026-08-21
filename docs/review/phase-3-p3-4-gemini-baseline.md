# Phase 3 package P3.4 Gemini Step 1 baseline and closed work map (remediated)

**Date:** 2026-08-20
**Status:** STEPS 1–6 ACCEPTED · STEP 7 RELEASED · STEP 8 NOT RELEASED
**Author:** Gemini (Production Frontend Implementer)
**Target Repository:** `/opt/discord-bots/freedom-bot`
**Sole Permitted Deliverable:** `docs/review/phase-3-p3-4-gemini-baseline.md`

---

## 1. Scope and evidence-class statement

This document is the remediated baseline deliverable for **Step 1** of package **P3.4** (production frontend integration), executed in accordance with:
1. `docs/review/phase-3-p3-4-gemini-step-01-baseline-prompt.md`;
2. `docs/review/phase-3-p3-4-gemini-implementation-prompt.md` (master prompt);
3. `docs/review/phase-3-p3-4-gemini-execution-plan.md`;
4. `docs/review/phase-3-delivery-plan.md` (§4 exclusions, §5 P3.4/P3.G4, §7 numeric policy, §11 traceability);
5. `docs/review/phase-3-p3-4-authorisation-and-conditions.md` (including D-03 acceptance & Gemini release 2026-08-20);
6. `docs/contracts/README.md` and all accepted Phase 3 contracts;
7. `docs/review/phase-3-p3-4-gemini-readiness-report.md` §§A1–A10;
8. `docs/review/phase-3-visual-prototype-handoff.md` and the 14-file visual freeze manifest;
9. `docs/review/Handover information` (R-09 caller-state remediation 6 instructions);
10. `.agents/AGENTS.md` and `docs/implementation-plan.md`.

### 1.1 Scope boundary

Step 1 performs **only read-only baseline inspection, verification, and mapping**. It creates and remediates this single baseline record (`docs/review/phase-3-p3-4-gemini-baseline.md`). It makes zero edits to existing template files, zero edits to backend Python files, introduces zero static CSS/JS/image assets, creates zero test files, executes zero database migrations, contacts zero external or live services, and accesses zero `.env` credentials, secrets, or real player/guild/Actor data.

The separate bounded Step 2 prompt was explicitly released by
Peter/Acceptance Authority on 2026-08-20 after this checkpoint closed. That
later release changes none of the historical Step 1 evidence below.

Step 2 and its bounded remediation subsequently passed independent Codex review
and were accepted on 2026-08-20. The remediation prompt's former held status was
corrected as a coordinator documentation error; it did not represent a lapse in
Gemini's authority. Peter/Acceptance Authority subsequently released the
separate bounded Step 3 prompt on 2026-08-20. At that checkpoint, no later step
was released.
Gemini completed its first Step 3 pass, and independent Codex review identified
three bounded findings concerning falsification quality, an unsupported
extension block, and unenforced child-template digests. Peter/Acceptance
Authority requested and authorized the bounded Step 3 remediation prompt on
2026-08-20. Gemini completed that remediation, but independent re-review found
two remaining blockers: ordinary inline event handlers pass the corpus helper,
and the CSS manifest falsification does not actually validate the tampered
temporary bytes through the positive production helper. Step 3 remains open
pending bounded correction and independent re-review; Step 4 remains
unreleased. Peter subsequently authorized the single-file Step 3 remediation
02 prompt to correct those two evidence defects. See
`phase-3-p3-4-step-03-remediation-review.md` and
`phase-3-p3-4-gemini-step-03-remediation-02-prompt.md`.
Gemini completed remediation 02, Codex independently re-reviewed it with no
remaining findings, and Peter accepted Step 3 on 2026-08-20. The bounded Step 4
prompt was prepared for review and Peter explicitly released it on 2026-08-20.
Gemini completed its first Step 4 pass. Independent Codex review found four
bounded defects: missing VM-22 HTTP byte-identity evidence, missing later-step
CSS falsification, ignored VM-04 availability facts, and one unused Step 4 CSS
selector. Peter authorized the bounded Step 4 remediation on 2026-08-20. Step 5
and every later step remain unreleased.
Gemini completed the first Step 4 remediation. Independent re-review confirmed
the original four findings were addressed but found two test-only defects:
missing post-test character cleanup and an `.auth-lead` falsification that
bypasses the positive selector-use helper. Peter authorized Step 4 remediation
02 on 2026-08-20. Step 5 remains unreleased.
Gemini completed remediation 02. Independent re-review confirmed its cleanup
and `.auth-lead` corrections but found that the CSS selector-use helper accepts
comment-only selector mentions. Peter authorized the single-file Step 4
remediation 03 on 2026-08-20. Step 5 remains unreleased.
Gemini completed remediation 03, Codex independently re-reviewed it with no
findings, and Peter accepted and closed Step 4 on 2026-08-20. Peter subsequently
released the separate bounded Step 5 prompt on 2026-08-20. Step 6 and every
later step remain unreleased.
Gemini completed its first Step 5 pass. Independent Codex review found five
bounded issues: one coordinator-owned stale test-allowlist contradiction, one
duplicate button-styled detail action, missing database teardown and R-20 empty
HTTP evidence, an ineffective deferred-value/control falsification, and
incomplete shared-helper falsification evidence. Codex prepared the bounded
Step 5 remediation 01 prompt for Peter's review. Peter subsequently clarified
that the instruction to write it for Gemini to fix the issues was itself its
authorization and release. Gemini executed remediation 01. Codex technically
re-reviewed the result: five earlier findings were substantially addressed, but
three test-only defects remained concerning the cleanup connection, shared
teardown falsification, and exact selector-use validation.
Codex prepared remediation 02 as a one-file test correction, authorized and
released by the same single-approval rule. Gemini executed it. Codex's technical
re-review confirmed that it closed the cleanup-connection and selector-use
findings, but the teardown validator still accepts database resolution before
yield. Remediation 03 is released as a one-file test correction. The former
authorization-gap interpretation was a Codex workflow/documentation error.
Step 6 and every later step remain unreleased.
Gemini completed remediation 03, Codex independently re-reviewed it with no
remaining finding, and Peter accepted and closed Step 5 on 2026-08-20. Peter's
same instruction authorized and released the bounded Step 6 prompt under the
single-approval rule. Step 7 and every later step remain unreleased.
Gemini completed its first Step 6 pass. Independent Codex review found six
bounded defects in required HTTP/security evidence, AccessFact evidence,
optional HTMX query binding, LinkInvariants presentation, cursor URL encoding,
and exact selector validation. Peter requested documentation and a remediation
prompt on 2026-08-20; that single instruction authorizes and releases Step 6
remediation 01 under the standing rule. Step 6 remains open. Step 7 and every
later step remain unreleased.
Gemini completed remediation 01. Independent re-review closed the five
template/selector findings but found the database test is not executable with
its accepted helper contract, omits required HTTP/security cases and verified
post-yield cleanup, and retains one false owner-replacement statement. Peter's
instruction to document and prompt the correction authorizes and releases Step
6 remediation 02. Step 6 remains open; Step 7 and later steps remain unreleased.
Gemini completed remediation 02. Independent re-review confirmed the production
copy, bound-connection and route/mutation matrix corrections, while finding
three final test-evidence gaps: no audit no-write proof for refused mutations,
incomplete denial-response comparison, and a cleanup validator that does not
prove case-created IDs absent. Peter's instruction authorizes and releases the
one-file Step 6 remediation 03. Step 6 remains open; Step 7 remains unreleased.
Gemini completed remediation 03. Independent re-review found three remaining
test-only evidence defects: missing immediate access-row no-write comparisons,
an invented denial-header exception list, and incomplete cleanup-validator data
flow. Peter's instruction authorizes and releases one-file Step 6 remediation
04. Step 6 remains open; Step 7 remains unreleased.
Gemini completed remediation 04. Independent re-review closed the runtime
access-state and cleanup data-flow findings but found two final test-evidence
defects: incomplete exact denial-header policy and insufficient structural
proof of snapshot helper semantics/order/arguments. Peter's instruction
authorizes and releases one-file Step 6 remediation 05. Step 6 remains open;
Step 7 remains unreleased.
Gemini completed remediation 05. Independent re-review confirmed exact denial
headers but found R-25 audit evidence uses character ID against a production
`entity_id` that is the generated access ID; its validator accepts the mismatch
and incompletely proves request/ordering semantics. Peter's instruction
authorizes and releases the fully contextualized one-file Step 6 remediation
06. Step 6 remains open; Step 7 remains unreleased.

Gemini completed remediation 06. Codex's final independent re-review found no
remaining defect: 113 focused tests passed with one permitted database skip,
and the combined non-database/full runs remained clean. Peter accepted and
closed Step 6 on 2026-08-20 and, in the same instruction, authorized and
released the separately bounded Step 7 identity-and-role administration
prompt. Step 8 and later work remain held.

### 1.2 Evidence classification

All assertions and findings in this baseline document are classified according to the delivery plan §11 / readiness report §A8 standard:

| Evidence Class | Status in Step 1 Remediation | Technical Basis / Scope |
|---|---|---|
| **Automated (source / structural)** | **Run & Verified** | Static AST imports inspection (`test_the_web_module_graph_never_reaches_the_bot_config`), contract document parsing (`parsed_contract_routes`, `parsed_contract_mounts`), visual freeze manifest `sha256sum`, template inventory, `git diff --check`, and non-database source unit assertions in `test_structural_guards.py` and `test_static_asset_surface.py`. |
| **Automated (response / HTTP)** | **Selected / Skipped in Step 1; Deferred to Steps 4–12** | Direct HTTP test cases in `test_structural_guards.py` and `test_static_asset_surface.py` were collected but skipped at runtime because `TEST_DATABASE_URL` is not configured. New HTTP test cases for view model rendering, exact form submissions, response headers, and safe error bodies will be added alongside production templates in later steps. |
| **Automated (browser)** | **Not Run in Step 1; Planned for Steps 5–12** | Browser execution was outside Step 1 scope. Headless browser execution (Playwright) remains governed by the master prompt's already-installed browser rule and requires production templates and static assets delivered in Steps 2–11. No browser binaries were installed or executed. |
| **Supervised / Source Contrast** | **Reference-only in Step 1; Split in Step 11** | Prototype CSS token definitions inventoried (71 declarations in `design-prototype/css/tokens.css`). In Step 11, contrast evidence is split between an automated source tool check and a supervised maintainer confirmation. |
| **Real-Device (TC-UI-08)** | **Explicitly Not Run** | Reserved exclusively for Peter Duscha on maintainer hardware. Cannot be simulated or claimed by agent inspection. |
| **Assistive Technology (TC-UI-09)** | **Explicitly Not Run** | Reserved exclusively for Peter Duscha / maintainer live traversal. Cannot be simulated or claimed by agent inspection. |
| **Disposable PostgreSQL / DB** | **Not Run in Step 1** | Baseline checks are strictly non-mutating and non-database; 64 database-dependent test cases in selected modules skipped due to unconfigured `TEST_DATABASE_URL`, and full database test suites were not selected or run. |
| **Staging / Live Environment** | **Explicitly Prohibited** | Belongs to I-06; no live Discord, Google, Foundry or staging interaction. |

---

## 2. Dirty-tree baseline and remediation status

### 2.1 Historical Step 1 dirty-tree baseline

Literal output of `git status --short` executed in `/opt/discord-bots/freedom-bot` when Gemini initially received the workspace for Step 1 (restored byte-for-byte from original baseline record):

```text
 M .env.example
 M adapters/database/repositories.py
 M adapters/database/tables.py
 M adapters/database/unit_of_work.py
 M adapters/http/composition.py
 M adapters/http/wsgi.py
 M adapters/web/app.py
 M adapters/web/composition.py
 M adapters/web/middleware.py
 M adapters/web/portal_routes.py
 M adapters/web/repositories.py
 M adapters/web/templates/conflict.html
 M application/foundry/import_service.py
 M application/repositories.py
 M application/snapshots.py
 M application/web/access_control.py
 M application/web/config.py
 M application/web/errors.py
 M application/web/startup.py
 M application/web/view_models.py
 M docs/contracts/phase-3-logical-schema.md
 M docs/contracts/phase-3-operational-contract.md
 M docs/contracts/phase-3-route-authorization-contract.md
 M docs/contracts/phase-3-state-machines.md
 M docs/contracts/phase-3-test-traceability.md
 M docs/contracts/phase-3-threat-model.md
 M docs/contracts/phase-3-view-model-contract.md
 M docs/operations/web-portal.md
 M docs/project-management/change-log.md
 M docs/project-management/raid-register.md
 M docs/project-management/status.md
 M "docs/review/Handover information"
 M docs/review/phase-3-p3-4-gemini-readiness-report.md
 M infra/postgresql/runtime-grants.sql.tmpl
 M tests/benchmark_snapshot_500.py
 M tests/conftest.py
 M tests/test_database_schema.py
 M tests/test_http_submission.py
 M tests/test_rejected_scope_absent.py
 M tests/web/conftest.py
 M tests/web/test_security_controls.py
 M tests/web/test_structural_guards.py
?? adapters/web/import_routes.py
?? adapters/web/static/
?? adapters/web/static_assets.py
?? adapters/web/templates/audit_results.html
?? adapters/web/templates/audit_search.html
?? adapters/web/templates/council_snapshots.html
?? adapters/web/templates/import_result.html
?? adapters/web/templates/job_status.html
?? adapters/web/templates/job_status_fragment.html
?? adapters/worker/
?? application/web/audit_search.py
?? application/web/jobs.py
?? application/web/snapshot_admin.py
?? application/worker/
?? docs/review/phase-3-d-03-backend-contract-correction-submission.md
?? docs/review/phase-3-d-03-codex-reviews-and-acceptance.md
?? docs/review/phase-3-p3-3-sixth-correction-security-review.md
?? docs/review/phase-3-p3-3-submission.md
?? docs/review/phase-3-p3-4-authorisation-and-conditions.md
?? docs/review/phase-3-p3-4-gemini-execution-plan.md
?? docs/review/phase-3-p3-4-gemini-implementation-prompt.md
?? docs/review/phase-3-p3-4-gemini-step-01-baseline-prompt.md
?? infra/systemd/freedom-worker.service.tmpl
?? migrations/versions/0011_reconciliation_jobs.py
?? migrations/versions/0012_job_effect_fence.py
?? migrations/versions/0013_effect_publication_recovery.py
?? tests/web/p3_3_fixtures.py
?? tests/web/test_d03_contract_correction.py
?? tests/web/test_migration_0011_round_trip.py
?? tests/web/test_migration_0012_round_trip.py
?? tests/web/test_migration_0013_rollback_boundary.py
?? tests/web/test_migration_0013_round_trip.py
?? tests/web/test_p3_3_audit_search.py
?? tests/web/test_p3_3_disclosure_and_bounds.py
?? tests/web/test_p3_3_effect_fence.py
?? tests/web/test_p3_3_effect_recovery.py
?? tests/web/test_p3_3_job_retention.py
?? tests/web/test_p3_3_jobs.py
?? tests/web/test_p3_3_matrix.py
?? tests/web/test_p3_3_success_cells.py
?? tests/web/test_p3_3_worker.py
?? tests/web/test_static_asset_surface.py
?? tools/freedom_worker.py
?? tools/job_retention.py
```

### 2.2 First remediation status snapshot (2026-08-20, start of remediation 1)

Literal output of `git status --short` executed at the start of the first remediation:

```text
 M "docs/review/Handover information"
```

- **Working tree context:** One pre-existing user modification (`docs/review/Handover information`) was present. The baseline document (`docs/review/phase-3-p3-4-gemini-baseline.md`) was unchanged at that point with hash `dc401d0e6251af4465cffbb0e15f02ac4e10ed1b96fbe4d2d850064063497cbb`.

### 2.3 Successive remediation status snapshots (2026-08-20, remediations 2–6)

Literal output of `git status --short` executed at the start of this sixth remediation:

```text
 M "docs/review/Handover information"
 M docs/review/phase-3-p3-4-gemini-baseline.md
```

- **Working tree context:** Two modified tracked files present in working tree: user instruction file `docs/review/Handover information` and the sole permitted deliverable `docs/review/phase-3-p3-4-gemini-baseline.md`. All backend Python code, templates, migrations, contracts, and tests delivered in P3.1–P3.3 and D-03 are tracked in `HEAD`.
- **Baseline SHA-256 before sixth remediation edit:** `665195d30b25b91c118382c0511c66326844c7d7c7a0f2afd8c4558f9144ee03`.
- **Pre-existing stash:** `stash@{0}: On main: temp before rebase` was neither inspected nor touched.

---

## 3. Visual freeze verification

Literal command executed in `/opt/discord-bots/freedom-bot`:

```bash
$ sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256
```

Literal output:

```text
design-prototype/assets/freedom-blades-token.png: OK
design-prototype/assets/portraits/lyra.png: OK
design-prototype/assets/portraits/thorin.png: OK
design-prototype/assets/portraits/valerius.png: OK
design-prototype/character-detail.html: OK
design-prototype/components.html: OK
design-prototype/council-approval.html: OK
design-prototype/css/styles.css: OK
design-prototype/css/tokens.css: OK
design-prototype/index.html: OK
design-prototype/js/portrait-preview.js: OK
design-prototype/login.html: OK
design-prototype/my-characters.html: OK
design-prototype/reconciliation.html: OK
```

- **Exit code:** `0`
- **Result:** All 14 visual prototype files under `design-prototype/` match the accepted visual freeze manifest exactly (14/14 OK).

---

## 4. Current production template & static root file inventory with SHA-256

Literal SHA-256 checksums computed across all 24 existing template files in `adapters/web/templates/` and `adapters/web/static/.gitkeep` (verified unique: 24 distinct template files, comprising 1 base layout, 20 child templates extending `base.html`, and 3 fragment templates):

| File Path | SHA-256 Checksum | Structural Role | Historical Step 1 Status Snapshot | Current Status in `HEAD` |
|---|---|---|---|---|
| `adapters/web/templates/account_identities.html` | `f3ab67ec4f0eb9b10555fe5263b871b15c1d18bfd15dc2ae6bf0a8c39bf7f0d5` | child (extends `base.html`) | tracked | tracked (unmodified) |
| `adapters/web/templates/audit_results.html` | `11ee0efcba8892970dee0870b5612d0fbf9c5091d5cf954ddf77e4af4f98291e` | fragment (standalone) | untracked P3.3 | tracked (unmodified) |
| `adapters/web/templates/audit_search.html` | `c54db1a4cc1779a52921269641330f79d295a843086eb198916a2f07c6e61c15` | child (extends `base.html`) | untracked P3.3 | tracked (unmodified) |
| `adapters/web/templates/base.html` | `51f45cf7ae559923c1f37c14d7d8dec19ab4004a8200d8a653569c06e9d855d9` | base root layout | tracked | tracked (unmodified) |
| `adapters/web/templates/character_detail.html` | `7be58ab1bb9436fda39801ff4a31e4c938301b1c335e0fe53e1411ca795c4cf4` | child (extends `base.html`) | tracked | tracked (unmodified) |
| `adapters/web/templates/character_links.html` | `fbdbfe0c761304a77928b569568a8b79be3ef25ed4ae4a51fee6eb57c89cfa8b` | child (extends `base.html`) | tracked | tracked (unmodified) |
| `adapters/web/templates/conflict.html` | `3aa735cde72995d016782b6308ddc61e310a4a6bfde6258441351380306d6d86` | child (extends `base.html`) | modified P3.3 | tracked (unmodified) |
| `adapters/web/templates/council_characters.html` | `cffc9bbb63773028deb4b0056c9a9d2c82a185c8f00a91530a623efd62c81661` | child (extends `base.html`) | tracked | tracked (unmodified) |
| `adapters/web/templates/council_snapshots.html` | `0b216a54636e3d8d9715fa08028fcf853af888d5ca26611da5155656ba04bf4d` | child (extends `base.html`) | untracked P3.3 | tracked (unmodified) |
| `adapters/web/templates/degraded.html` | `56ea9c866df7d883abe8a62197acefcec9d5d5ad3da59f31c37206ce1f2fd799` | child (extends `base.html`) | tracked | tracked (unmodified) |
| `adapters/web/templates/denied.html` | `5f29922f6b48739d03874b3afb3a41953dc0bd0185b25d982800e860dd0c5305` | child (extends `base.html`) | tracked | tracked (unmodified) |
| `adapters/web/templates/emergency.html` | `8d2b4bb671e8c8b4b9fbef4b37f745d46622b6be5e965e2fcbb712faea7dd61a` | child (extends `base.html`) | tracked | tracked (unmodified) |
| `adapters/web/templates/error.html` | `60ac158aebf5758a6e7f219b7230d372843bff77a0d395fbcaf8bb36154a20c2` | child (extends `base.html`) | tracked | tracked (unmodified) |
| `adapters/web/templates/field_profile.html` | `06a2b6a5e389b6c936f016df95069b82c26741dba5e402ae2c9ad0d306181e91` | child (extends `base.html`) | tracked | tracked (unmodified) |
| `adapters/web/templates/identity_migration.html` | `ededffd5adb842bd0a33bb6f3f098c0497d3d6935d5827ecac02727af849a878` | child (extends `base.html`) | tracked | tracked (unmodified) |
| `adapters/web/templates/identity_search.html` | `fe5cb51fdfdcf5a829a7569766321ad6b8b555f8dbc3b520b94158a028c53f6e` | fragment (standalone) | tracked | tracked (unmodified) |
| `adapters/web/templates/import_result.html` | `152b84f766211b886ddd67ca1ce03c53cb37ceefc9ea5678cd22f7f2b7f3fff6` | child (extends `base.html`) | untracked P3.3 | tracked (unmodified) |
| `adapters/web/templates/job_status.html` | `b106fe0f2e7f807fef4462504bf23e669e731accac309a1157cdcdc17146a0ea` | child (extends `base.html`) | untracked P3.3 | tracked (unmodified) |
| `adapters/web/templates/job_status_fragment.html` | `4993979df628907b7639916e6e3e47d0b1ed795854e393c5bc47e4af7682b2b1` | fragment (standalone) | untracked P3.3 | tracked (unmodified) |
| `adapters/web/templates/login.html` | `1fee4161bddea58712de35ab952cdaa7c892450d0c2ee20b47ee8d333c7879a4` | child (extends `base.html`) | tracked | tracked (unmodified) |
| `adapters/web/templates/my_characters.html` | `28eb6391c37e50383103ad05ef98d0fd3d6669117edb73251de570f0871ccf72` | child (extends `base.html`) | tracked | tracked (unmodified) |
| `adapters/web/templates/non_member.html` | `565e9f1697e66fae2e0db3e4f0dd7bd1a0b3bf12fc5817652b424968fb0b76c7` | child (extends `base.html`) | tracked | tracked (unmodified) |
| `adapters/web/templates/role_capabilities.html` | `bf1ce7d09096b8d41fcde29fc170bf43615d462a7e7015a13de89b3f3d4a0b3b` | child (extends `base.html`) | tracked | tracked (unmodified) |
| `adapters/web/templates/validation.html` | `54deb119e685eb264405db013ee43b3076214e4f0d9026d84821a606764a2a65` | child (extends `base.html`) | tracked | tracked (unmodified) |
| `adapters/web/static/.gitkeep` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | static root placeholder | untracked D-03 | tracked (unmodified) |

### 4.1 Unresolved future asset and component roles (planned for later steps)

The following future asset and component roles are planned for Steps 2–3 without premature path, filename, or version choices:

1. **Step 2 Static Asset Roles:**
   - *Design tokens stylesheet role:* CSS custom properties adapted from the visual prototype.
   - *Production styles stylesheet role:* Layout primitives (`.table-container`, `.card-grid`, `.fb-blade-divider`, focus indicators, reduced motion).
   - *Vendored HTMX library role:* Single reviewed vendored script file with version, upstream URL, and SHA-256 in header per configuration contract §1.5 (specific version unresolved).
   - *Guild emblem asset role:* Same-origin token image asset.
   - *Static asset integrity metadata role:* Mechanism for tracking and verifying static asset integrity and cache policy (exact packaging/manifest mechanism unresolved for Step 2).
2. **Step 3 Tentative Shared Include Roles (permitted where genuinely shared):**
   - *Shared header layout role:* Navigation and status header include.
   - *Shared footer layout role:* Landmark footer include.
   - *Portrait fallback role:* Character initials fallback SVG/HTML include.
   - *Summary cards role:* Statistical summary card layout include.
   - *Alert banner role:* Standardized status and notice banner include.

---

## 5. Complete template / route / view-model / state / flow / reference / step matrix

### 5.1 Per-route accepted form inputs reference (contract authority for forms)

Per `docs/contracts/phase-3-route-authorization-contract.md` (especially R-09, §5.1, §6.1) and master prompt §5.3, the following exact form input sets are accepted by production parsers:

| Route ID | Route Path & Method | View Model & Owning Template | Exact Form Inputs Accepted | Caller & Security Invariants |
|---|---|---|---|---|
| **R-09** | `POST /v1/auth/emergency/recovery` | VM-04 · `emergency.html` | `token` only | **Accepted Callers:** All eight states (`U`, `N`, `M`, `C`, `A`, `CA`, `BG`, `AC`).<br>**No `csrf_token`:** Session-independent; does not rely on an existing cookie session.<br>**Authority:** Possession and successful single-use redemption of a valid, unexpired, purpose-bound recovery grant creates the break-glass session. An existing session neither authorizes redemption nor bypasses exact-Origin validation or N-33 rate limits. |
| **R-25** | `POST /v1/council/characters/{character_id}/links` | VM-08 · `character_links.html` | `csrf_token`, `version`, `subject`, `access_kind`, `reason` | `character_id` from URL path. |
| **R-26** | `POST /v1/council/characters/{character_id}/links/{access_id}/revoke` | VM-08 · `character_links.html` | `csrf_token`, `version`, `reason` | `character_id`, `access_id` from URL path. |
| **R-27** | `POST /v1/council/characters/{character_id}/links/{access_id}/default` | VM-08 · `character_links.html` | `csrf_token`, `version`, `reason` | `character_id`, `access_id` from URL path. |
| **R-29** | `POST /v1/council/identity-migration/{proposal_id}/confirm` | VM-10 · `identity_migration.html` | `csrf_token`, `version`, `reason` | `proposal_id` from URL path; `resulting_access_kind` is fixed server-side. |
| **R-30** | `POST /v1/council/identity-migration/{proposal_id}/reject` | VM-10 · `identity_migration.html` | `csrf_token`, `reason` *(NO `version`)* | `proposal_id` from URL path. |
| **R-33** | `POST /v1/admin/role-capabilities` | VM-12 · `role_capabilities.html` | `csrf_token`, `role_id`, `capability`, `reason` | Server sets `provenance`, `created_at`, `created_by`. |
| **R-34** | `POST /v1/admin/role-capabilities/{mapping_id}/revoke` | VM-12 · `role_capabilities.html` | `csrf_token`, `version`, `reason` | `mapping_id` from URL path. |
| **R-37** | `POST /v1/account/identities/{identity_id}/unlink` | VM-13 · `account_identities.html` | `csrf_token` only | `identity_id` from URL path. |
| **R-38** | `POST /v1/admin/role-capabilities/{mapping_id}/ratify` | VM-12 · `role_capabilities.html` | `csrf_token`, `version`, `reason` | `mapping_id` from URL path. |
| **R-41** | `POST /v1/admin/snapshots/{snapshot_id}/folder` | VM-14 · `council_snapshots.html` | `csrf_token`, `folder_id` | `snapshot_id` from URL path. Admin only. |
| **R-42** | `POST /v1/council/snapshots/{snapshot_id}/preview-jobs` | VM-14 · `council_snapshots.html` | `csrf_token`, `nonce` | `snapshot_id` from URL path. Council only. |
| **R-45** | `POST /v1/council/jobs/{job_id}/cancel` | VM-15 · `job_status.html` | `csrf_token` only | `job_id` from URL path. |
| **R-46** | `POST /v1/council/jobs/{job_id}/apply` | VM-15 · `job_status.html` | `csrf_token`, `preview_token`, `nonce` only | `job_id` from path; `checksum_full`, `folder`, `profile_version`, aggregate versions are server-owned. |

### 5.2 Complete template / route mapping table

The following table establishes the complete, closed mapping for all 24 production templates in `adapters/web/templates/`, audited mechanically against production route handlers, exact caller permissions (including explicit AC $\leftrightarrow$ BG mirroring), and dataclass definitions in `application/web/view_models.py`:

| # | Production Template | Rendering Route(s) & Actual Handler / Symbol | View Model ID & Exact Dataclass | Applicable `PageState` Literals Delivered | Direct View Model Fields & Nested Types (from `view_models.py`) | Caller / Capability Class Permissions | Full-Page / Fragment Role | Required P3.4 no-JavaScript Flow (Acceptance Target) | Prototype Reference | Planned Step |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `base.html` | Root layout (inherited by all 20 full pages) | Layout context | N/A — inherited from the child view | Encloses child view context (`vm`, `title`, etc.) | All callers (`U`, `N`, `M`, `C`, `A`, `CA`, `BG`, `AC`) | Shared shell layout | Semantic HTML5 landmarks (`header`, `nav`, `main`, `footer`), skip link (`#main-content`), navigation grid. Fully functional without JS. | `index.html` & `components.html` | **Step 3** |
| 2 | `login.html` | R-02 (`GET /v1/login`) · `login_page` in `adapters/web/app.py` | VM-01 · `LoginPageView` | `ready`, `error` | `state: PageState`, `providers: tuple[ProviderOption, ...]`, `emergency_access_available: bool`, `degraded: DegradedProvider \| None`, `failure: LoginFailure \| None` (`LoginFailure.code: LoginFailureCode`, `correlation: Correlation`) | `U` primary (all unauthenticated callers; authenticated callers `N`, `M`, `C`, `A`, `CA`, `BG`, `AC` redirected 303) | Full page | Standard `<a href="/v1/auth/discord/start">` link; link to `/v1/auth/emergency`. Works without JS. | `login.html` | **Step 4** |
| 3 | `emergency.html` | R-06 (`GET /v1/auth/emergency`) · `emergency_login_page` in `adapters/web/app.py` | VM-04 · `EmergencyLoginView` | `ready` | `state: PageState`, `webauthn_supported_hint: bool`, `recovery_form_available: bool`, `failure: EmergencyFailure \| None` (`EmergencyFailure.code: EmergencyFailureCode`, `correlation: Correlation`) | Reachable for all caller states (`U`, `N`, `M`, `C`, `A`, `CA`, `BG`, `AC`). Page is non-enumerating; protected credential is the authority. | Full page | Recovery grant form submits via standard `POST /v1/auth/emergency/recovery` (R-09: `token` only, no `csrf_token`). Passkey WebAuthn is progressive enhancement with JS. | `login.html` & `components.html` | **Step 4** |
| 4 | `non_member.html` | R-04 refusal & 403 on navigation · `oauth_callback` in `adapters/web/app.py` & `_refusal_response` in `portal_routes.py` and `import_routes.py` (when `NotAMember` on navigation) | VM-02 · `NonMemberView` | `denied` | `state: PageState`, `reason: DeniedReason` (`category: DenialCategory.NOT_A_MEMBER`), `guild_display_name: str`, `checked_at: Instant`, `correlation: Correlation` | Caller state `N` (valid session, not in guild) | Full page (403 error page) | Static HTML notification with recovery instructions and correlation UUID. Works without JS. | `components.html` | **Step 4** |
| 5 | `degraded.html` | Cross-cutting 503 response · `_refusal_response` in `portal_routes.py` & `import_routes.py` (when `SERVICE_DEGRADED`) | VM-03 · `ServiceDegradedView` | `error` | `state: PageState`, `reason: DeniedReason` (`category: DenialCategory.SERVICE_DEGRADED`), `subsystem: Literal["identity_provider", "database"]`, `grace_expired: bool`, `correlation: Correlation` | Any authenticated caller (`N`, `M`, `C`, `A`, `CA`, `BG`, `AC`) when N-10 grace exhausted | Full page (503 Service Unavailable) | Static HTML notification of external provider outage with correlation UUID. Works without JS. | `components.html` | **Step 4** |
| 6 | `denied.html` | Cross-cutting 401/403/404 denial on navigation · `_denied` (called by `_refusal_response`) in `portal_routes.py` & `import_routes.py` | VM-22 · `DeniedView` | `denied` | `state: PageState`, `reason: DeniedReason` (`category: DenialCategory` only; NO correlation, timestamp, guild, or object ID) | Any caller encountering object-level or capability denial | Full page (401/403/404 safe denial) | Static HTML denial page explaining closed category. Byte-identical across 404 absent/denied (TC-OBJ-07). Works without JS. | `components.html` | **Step 4** |
| 7 | `conflict.html` | Cross-cutting 409 Conflict · `_conflict` (called by `_mutation_refusal`) in `portal_routes.py` & `import_routes.py` | VM-19 · `ConflictView` | `stale` | `state: PageState`, `conflict: Literal["stale_version", "stale_preview", "already_applied", "already_cancelled", "duplicate_request"]`, `current: object`, `correlation: Correlation` | Any caller submitting conflicting version or preview (`M`, `C`, `A`, `CA`, `BG`, `AC`) | Full page (409 Conflict) | Static HTML explaining conflict and providing link back to reload fresh state. Works without JS. | `components.html` | **Step 4** |
| 8 | `validation.html` | Cross-cutting 422 Unprocessable · `_validation` (called by `_mutation_refusal`) in `portal_routes.py` & `import_routes.py` | VM-21 · `ValidationView` | `invalid` | `state: PageState`, `form: object`, `errors: tuple[FieldError, ...]` (`FieldError.field: str`, `FieldError.code: FieldErrorCode`, `FieldError.limit: int \| None`) | Any caller submitting invalid form fields (`M`, `C`, `A`, `CA`, `BG`, `AC`) | Full page (422 Unprocessable Entity) | Static HTML summary of field validation errors with focusable anchors. Works without JS. | `components.html` | **Step 4** |
| 9 | `error.html` | Cross-cutting 500 Safe Error · `unexpected` (registered by `_register_error_handlers`) in `adapters/web/app.py` | VM-20 · `SafeErrorView` | `error` | `state: PageState`, `correlation: Correlation`, `message_code: Literal["unexpected_error"]` (no tracebacks, SQL, or internal paths) | Any caller (`U`, `N`, `M`, `C`, `A`, `CA`, `BG`, `AC`) | Full page (500 Internal Server Error) | Static HTML error card displaying support correlation UUID. Works without JS. | `components.html` | **Step 4** |
| 10 | `my_characters.html` | R-20 (`GET /v1/characters`) · `characters_index` in `adapters/web/portal_routes.py` | VM-05 · `MyCharactersView` | `ready`, `empty` | `state: PageState`, `characters: tuple[CharacterSummary, ...]`, `truncated: bool`, `default_character_id: UUID \| None` (`CharacterSummary.level: int \| None` -> "not recorded") | `M`, `C`, `CA` (`guild_member`); `BG`/`AC` refused `403` | Full page | Standard `<a href="/v1/characters/{character_id}">` links. Zero `<form>` elements. Read-only. Works without JS. | `my-characters.html` | **Step 5** |
| 11 | `character_detail.html` | R-21 (`GET /v1/characters/{character_id}`) · `character_detail` in `adapters/web/portal_routes.py` | VM-06 · `CharacterDetailView` | `ready` | `state: PageState`, `character_id: UUID`, `display_name: SafeText`, `long_name: SafeText \| None`, `level: int \| None`, `active: bool`, `version: int`, `portrait: CharacterPortrait`, `access: tuple[AccessFact, ...]`, `viewer_access_kind: AccessKind \| None`, `snapshot_fields: tuple[SnapshotField, ...]`, `deferred_fields: tuple[MigrationDeferred, ...]`, `provenance: Provenance` | `M` (for owned/co-owned object), `C`, `CA` (`character_owner` / `guild_council`); `BG`/`AC` refused `403` | Full page | Static HTML character sheet with stat blocks and field profile table. Zero mutation forms. Works without JS. | `character-detail.html` | **Step 5** |
| 12 | `council_characters.html` | R-22 (`GET /v1/council/characters`) · `council_characters_index` in `adapters/web/portal_routes.py` | VM-07 · `CouncilCharacterIndexView` | `ready`, `empty` | `state: PageState`, `rows: tuple[CouncilCharacterRow, ...]`, `cursor: Cursor`, `filters: CharacterFilters` | `C`, `CA` (`guild_council`); `BG`/`AC` refused `403` | Full page | Search form submits via `GET /v1/council/characters`; pagination uses `<a>` hrefs with cursor tokens. Works without JS. | `council-approval.html` (table/filter layout) | **Step 6** |
| 13 | `character_links.html` | R-23 (`GET /v1/council/characters/{character_id}/links`) · `council_character_links` in `adapters/web/portal_routes.py` | VM-08 · `CharacterLinksView` | `ready` | `state: PageState`, `character: CouncilCharacterRow`, `character_version: int`, `active_links: tuple[AccessFact, ...]`, `historical_links: tuple[AccessFact, ...]`, `cursor: Cursor`, `csrf_token: str`, `invariants: LinkInvariants` | `C`, `CA` (`guild_council`); `BG`/`AC` refused `403` | Full page (pairs with HTMX partial R-24) | Grant form (R-25: `csrf_token`, `version`, `subject`, `access_kind`, `reason`), revoke form (R-26: `csrf_token`, `version`, `reason`), default form (R-27: `csrf_token`, `version`, `reason`) submit via standard POST. Manual snowflake entry without JS. | `council-approval.html` (access management panel) | **Step 6** |
| 14 | `identity_search.html` | R-24 (`GET /v1/council/identity-search`) · `council_identity_search` in `adapters/web/portal_routes.py` | VM-09 · `IdentitySearchResultsView` | `ready`, `empty`, `invalid` | `state: PageState`, `query_echo: SafeText`, `candidates: tuple[IdentityCandidate, ...]`, `truncated: bool`, `evidence_notice_code: Literal["names_are_not_identity"]` | `C`, `CA` (`guild_council`); `BG`/`AC` refused `403` | HTMX fragment (pairs with R-23) | Dynamic enhancement for R-23. Without JS, operator uses R-23 manual input. Standalone GET answers 200 fragment or 401 unauthenticated. | `council-approval.html` (candidate dropdown/table) | **Step 6** |
| 15 | `identity_migration.html` | R-28 (`GET /v1/council/identity-migration`) · `council_identity_migration` in `adapters/web/portal_routes.py` | VM-10 · `IdentityMigrationView` | `ready`, `empty` | `state: PageState`, `run: MigrationRun \| None`, `proposals: tuple[LinkProposal, ...]`, `cursor: Cursor`, `totals: MigrationTotals`, `csrf_token: str` | `C`, `CA` (`guild_council`); `BG`/`AC` refused `403` | Full page | Proposal table with confirm (R-29: `POST /v1/council/identity-migration/{proposal_id}/confirm` with `csrf_token`, `version`, `reason`) and reject (R-30: `POST /v1/council/identity-migration/{proposal_id}/reject` with `csrf_token`, `reason`) forms submitting via standard POST. Works without JS. | `none` (new visual work; adapts table & summary cards) | **Step 7** |
| 16 | `field_profile.html` | R-31 (`GET /v1/council/field-profile`) · `council_field_profile` in `adapters/web/portal_routes.py` | VM-11 · `FieldProfileView` | `ready` | `state: PageState`, `profile_version: str`, `paths: tuple[ProfilePathRow, ...]`, `fields: tuple[ProfileFieldRow, ...]`, `unknown_path_policy_code: Literal["reported_never_writable"]` | `C`, `A`, `CA` (`guild_council` / `platform_administrator`); `BG`/`AC` refused `403` | Full page | Static HTML classification table with snapshot mode badges and deferred package indicators. Read-only. Works without JS. | `reconciliation.html` (field profile tab) | **Step 7** |
| 17 | `role_capabilities.html` | R-32 (`GET /v1/admin/role-capabilities`) · `admin_role_capabilities` in `adapters/web/portal_routes.py` | VM-12 · `RoleCapabilityView` | `ready` | `state: PageState`, `guild_id: str`, `administrator_scope: Literal["full", "emergency_continuity"]`, `mappings: tuple[RoleMappingRow, ...]`, `available_capabilities: tuple[ActorCapability, ...]`, `csrf_token: str`, `unratified_count: int`, `scope_notice_code: Literal["emergency_continuity_allowlist"] \| None`, `lockout_guard_notice_code: Literal["protected_bootstrap_mapping"]` | `A`, `CA`, `BG`, `AC` (`platform_administrator`; N-67 restricts `BG`/`AC` to emergency scope) | Full page | Create mapping (R-33: `POST /v1/admin/role-capabilities` with `csrf_token`, `role_id`, `capability`, `reason`), revoke (R-34: `POST /v1/admin/role-capabilities/{mapping_id}/revoke` with `csrf_token`, `version`, `reason`), ratify (R-38: `POST /v1/admin/role-capabilities/{mapping_id}/ratify` with `csrf_token`, `version`, `reason`) submit via standard POST. Bootstrap mapping non-revocable. Works without JS. | `none` (new visual work; adapts table & alert cards) | **Step 7** |
| 18 | `account_identities.html` | **R-35** (`GET /v1/account/identities`) & **R-36** (`GET /v1/account/identities/link/start`) · `account_identities` & `account_identity_link_start` in `adapters/web/portal_routes.py` | VM-13 · `AccountIdentitiesView` | `ready` (R-35), `denied` (R-36) | `state: PageState`, `account_id: UUID`, `identities: tuple[LinkedIdentity, ...]`, `additional_provider: Literal["no_additional_provider"] \| ProviderOption`, `unlink_blocked_reason: Literal["last_usable_identity", "emergency_session"] \| None`, `csrf_token: str` | **R-35:** `N`, `M`, `C`, `A`, `CA`, `BG`, `AC` (all authenticated callers)<br>**R-36:** `N`, `M`, `C`, `A`, `CA` (`BG` and `AC` are refused `403`)<br>**R-37 form:** `N`, `M`, `C`, `A`, `CA` (`BG` and `AC` are refused `403`) | Full page | Unlink form (R-37: `POST /v1/account/identities/{identity_id}/unlink` with `csrf_token` only) submits via standard POST; link start (R-36) answers 200 denied view. Works without JS. | `none` (new visual work; adapts identity card list) | **Step 7** |
| 19 | `council_snapshots.html` | R-40 (`GET /v1/council/snapshots`) · `council_snapshots` in `adapters/web/import_routes.py` | VM-14 · `SnapshotListView` | `ready`, `empty` | `state: PageState`, `snapshots: tuple[SnapshotRow, ...]`, `cursor: Cursor`, `can_select_folder: bool`, `can_preview: bool`, `csrf_token: str` | `C`, `A`, `CA` (`guild_council` / `platform_administrator`); `BG`/`AC` refused `403` | Full page | Folder select form (R-41: `POST /v1/admin/snapshots/{snapshot_id}/folder` with `csrf_token`, `folder_id`; admin only) and preview trigger form (R-42: `POST /v1/council/snapshots/{snapshot_id}/preview-jobs` with `csrf_token`, `nonce`; Council only) submit via standard POST. Works without JS. | `reconciliation.html` (snapshot ledger & forms) | **Step 8** |
| 20 | `job_status.html` | R-43 (`GET /v1/council/jobs/{job_id}`) · `council_job_detail` in `adapters/web/import_routes.py` | VM-15 · `JobStatusView` | `ready` | `state: PageState`, `job_id: UUID`, `kind: JobKind`, `job_state: JobState`, `progress: JobProgress \| None`, `requested_by: Actor`, `requested_at: Instant`, `attempts: int`, `poll_after_seconds: int`, `result: ReconciliationSummary \| None`, `stale_reason: StaleReason \| None`, `failure: JobFailure \| None`, `cancel_available: bool`, `confirm: ConfirmScope \| None`, `csrf_token: str`, `correlation: Correlation` | `C`, `CA` (`guild_council`); `BG`/`AC` refused `403` | Full page (hosts HTMX container polling R-44) | Displays full job stats; manual refresh updates state; cancel (R-45: `POST /v1/council/jobs/{job_id}/cancel` with `csrf_token` only) and apply (R-46: `POST /v1/council/jobs/{job_id}/apply` with `csrf_token`, `preview_token`, `nonce` only) submit via standard POST. Works without JS. | `reconciliation.html` (progress step sequence & stats) | **Step 9** |
| 21 | `job_status_fragment.html` | R-44 (`GET /v1/council/jobs/{job_id}/status`) · `council_job_status_fragment` in `adapters/web/import_routes.py` | VM-15 · `JobStatusView` | `ready` | Same `JobStatusView` fields as R-43 (emits polling headers only when `job_state` is `queued` or `running`) | `C`, `CA` (`guild_council`); `BG`/`AC` refused `403` | HTMX fragment (polled by R-43 container) | Fragment polled via `hx-get` every N-22 seconds ONLY while `queued` or `running`. Stops dead on terminal states. Answers 401 unauthenticated. | `reconciliation.html` (progress step sequence fragment) | **Step 9** |
| 22 | `import_result.html` | R-47 (`GET /v1/council/imports/{import_id}`) · `council_import_result` in `adapters/web/import_routes.py` | VM-17 · `ImportResultView` | `ready` | `state: PageState`, `import_id: UUID`, `status: Literal["applied", "refused"]`, `mode: Literal["bootstrap", "council"]`, `actor: Actor`, `capability: ActorCapability`, `snapshot: SnapshotStamp`, `checksum_full: str`, `folder: FolderChoice`, `profile_version: str`, `created_count: int`, `updated_count: int`, `warning_count: int`, `issue_counts: tuple[IssueCount, ...]`, `occurred_at: Instant`, `correlation: Correlation`, `duplicate_of: UUID \| None` | `C`, `A`, `CA` (`guild_council` / `platform_administrator`); `BG`/`AC` refused `403` | Full page | Static HTML immutable import receipt card. Read-only. Works without JS. | `reconciliation.html` (import receipt card) | **Step 10** |
| 23 | `audit_search.html` | R-48 (`GET /v1/audit`) · `audit_search` in `adapters/web/import_routes.py` | VM-18 · `AuditSearchView` | `ready`, `empty` | `state: PageState`, `filters: AuditFilters`, `rows: tuple[AuditRow, ...]`, `cursor: Cursor`, `total_is_unbounded: bool = True`, `immutability_notice_code: Literal["append_only_no_correction_here"]` | `C`, `A`, `CA`, `BG`, `AC` (`guild_council` / `platform_administrator`) | Full page (pairs with HTMX partial R-49) | Filter form submits via standard `GET /v1/audit?...`; pagination links use cursor tokens. Works without JS. | `none` (new visual work; adapts filter card & table) | **Step 10** |
| 24 | `audit_results.html` | R-49 (`GET /v1/audit/results`) · `audit_results_fragment` in `adapters/web/import_routes.py` | VM-18 · `AuditSearchView` | `ready`, `empty` | Same `AuditSearchView` fields as R-48 (renders rows fragment) | `C`, `A`, `CA`, `BG`, `AC` (`guild_council` / `platform_administrator`) | HTMX fragment (swapped by R-48 form) | Enhanced results table swapped by HTMX with JS. Without JS, R-48 full page handles form GET. Answers 401 unauthenticated. | `none` (new visual work; table layout) | **Step 10** |

---

## 6. Existing-test and planned-test map

### 6.1 Inventory of existing P3.4-relevant tests

The repository contains exactly 50 web test modules under `tests/web/test_*.py`. Key existing modules relevant to frontend integration include:
- `test_structural_guards.py`: TC-STRUCT-01 (closed 39 routes + 1 static mount M-01), TC-STRUCT-02/TC-VM-01 (frozen slotted view models), TC-VM-02 (text bounds), TC-VM-03 (deferred fields), TC-VM-06 (DeniedView byte-identity fields), TC-STRUCT-05/06 (web config independence & startup refusals).
- `test_static_asset_surface.py`: TC-STATIC-01 to TC-STATIC-07 (M-01 methods, approved root, traversal/dotfile refusals, trusted host, kill switch availability, fingerprint cache policy, no cookie mutation, URL grammar).
- `test_d03_contract_correction.py`: D-03-2 (ConfirmScope 8 fields), D-03-3 (CharacterFilters), D-03-4 (VM-13 CSRF token & synchronizer design), D-03-5 (R-36 200 HTML VM-13 denied), D-03-6 (DeniedView VM-22 & byte-identical 404 responses).
- `test_security_controls.py`: TC-SEC-01 to TC-SEC-13 (synchronizer CSRF, security headers, rate limits, session bounds).
- `test_p3_2_matrix.py`, `test_p3_2_success_cells.py`, `test_p3_3_matrix.py`, `test_p3_3_success_cells.py`: Route authorization matrices and permitted response cells.

### 6.2 Planned tests by execution-plan step (Steps 2–12)

The following mechanically checkable test plan specifies the exact modules, function names, dispositions, requirement / contract citations, production files exercised, evidence classes, and prerequisites for all future steps (none added or modified in Step 1):

| Step | Target Module | Proposed Test Function Name | Disposition | Traceability / Contract Requirement Reference | Production Files Exercised | Evidence Class | Prerequisite / Not Runnable Reason |
|---|---|---|---|---|---|---|---|
| **Step 2** | `tests/web/test_p3_4_static_assets.py` | `test_static_directory_contains_expected_production_asset_roles` | add | Master Prompt §3.2 (no dedicated accepted test ID) | `adapters/web/static/` | automated (structural) | Requires Step 2 production assets to exist |
| **Step 2** | `tests/web/test_p3_4_static_assets.py` | `test_vendored_htmx_header_carries_version_url_and_sha256` | add | Configuration contract §1.5 (no dedicated accepted test ID) | `adapters/web/static/` | automated (structural) | Requires vendored HTMX file in Step 2 |
| **Step 2** | `tests/web/test_p3_4_static_assets.py` | `test_design_tokens_stylesheet_defines_required_custom_properties` | add | Master Prompt §3.3 (no dedicated accepted test ID) | `adapters/web/static/` | automated (structural) | Requires production CSS tokens in Step 2 |
| **Step 2** | `tests/web/test_p3_4_static_assets.py` | `test_production_styles_contain_core_layout_primitives` | add | Master Prompt §3.3 (no dedicated accepted test ID) | `adapters/web/static/` | automated (structural) | Requires production styles in Step 2 |
| **Step 2** | `tests/web/test_p3_4_static_assets.py` | `test_guild_emblem_asset_references_are_same_origin` | add | TC-SEC-14 (structural origin scan) | `adapters/web/static/` | automated (structural) | Requires guild emblem asset in Step 2 |
| **Step 2** | `tests/web/test_p3_4_static_assets.py` | `test_guild_emblem_is_served_via_static_route` | add | Master Prompt §3.2 (no dedicated accepted test ID) | `adapters/web/static_assets.py` | automated (HTTP) | Requires Step 2 assets and app test client |
| **Step 2** | `tests/web/test_p3_4_static_assets.py` | `test_static_asset_fingerprint_cache_headers` | add | TC-STATIC-05, TC-SEC-05 | `adapters/web/static_assets.py` | automated (HTTP) | Requires Step 2 assets and app test client |
| **Step 3** | `tests/web/test_p3_4_shell_and_components.py` | `test_base_template_renders_html5_semantic_landmarks` | add | Master Prompt §6 (no dedicated accepted test ID) | `adapters/web/templates/base.html` | automated (structural) | Requires Step 3 `base.html` |
| **Step 3** | `tests/web/test_p3_4_shell_and_components.py` | `test_skip_link_targets_main_content_and_is_first_focusable_element` | add | Master Prompt §6 (no dedicated accepted test ID) | `adapters/web/templates/base.html` | automated (structural) | Requires Step 3 `base.html` |
| **Step 3** | `tests/web/test_p3_4_shell_and_components.py` | `test_navigation_grid_sets_single_aria_current_page` | add | Master Prompt §6 (no dedicated accepted test ID) | `adapters/web/templates/` | automated (structural) | Requires Step 3 layout |
| **Step 4** | `tests/web/test_p3_4_auth_and_system_views.py` | `test_login_page_renders_ready_and_error_states_without_script` | add | Master Prompt §3.5 / view-model contract §4 (VM-01) (no dedicated accepted test ID) | `adapters/web/templates/login.html`, `app.py` | automated (HTTP) | Requires Step 4 `login.html` |
| **Step 4** | `tests/web/test_p3_4_auth_and_system_views.py` | `test_emergency_login_page_renders_r09_recovery_form_structure` | add | Master Prompt §3.5 / route contract §3.3, §5.1 (R-09) (no dedicated accepted test ID) | `adapters/web/templates/emergency.html`, `app.py` | automated (HTTP) | Checks R-09 action `POST /v1/auth/emergency/recovery`, sole `token` field, absence of `csrf_token` and unrelated inputs. *(Runtime Origin, rate-limiting, and single-use redemption properties mapped to backend evidence)* |
| **Step 4** | `tests/web/test_p3_4_auth_and_system_views.py` | `test_non_member_view_renders_guild_name_timestamp_and_correlation` | add | view-model contract §4 (VM-02) (no dedicated accepted test ID) | `adapters/web/templates/non_member.html`, `portal_routes.py` | automated (HTTP) | Requires Step 4 `non_member.html` |
| **Step 4** | `tests/web/test_p3_4_auth_and_system_views.py` | `test_degraded_view_renders_subsystem_and_correlation_id` | add | view-model contract §4 (VM-03) (no dedicated accepted test ID) | `adapters/web/templates/degraded.html`, `portal_routes.py` | automated (HTTP) | Requires Step 4 `degraded.html` |
| **Step 4** | `tests/web/test_p3_4_auth_and_system_views.py` | `test_denied_view_renders_only_state_and_closed_category_preserving_byte_identity` | add | TC-VM-06, TC-OBJ-07 | `adapters/web/templates/denied.html`, `portal_routes.py` | automated (HTTP) | Requires Step 4 `denied.html` |
| **Step 4** | `tests/web/test_p3_4_auth_and_system_views.py` | `test_conflict_view_renders_stale_state_and_correlation` | add | view-model contract §8 (VM-19) (no dedicated accepted test ID) | `adapters/web/templates/conflict.html`, `portal_routes.py` | automated (HTTP) | Requires Step 4 `conflict.html` |
| **Step 4** | `tests/web/test_p3_4_auth_and_system_views.py` | `test_validation_view_renders_field_error_list_and_anchors` | add | view-model contract §8 (VM-21) (no dedicated accepted test ID) | `adapters/web/templates/validation.html`, `portal_routes.py` | automated (HTTP) | Requires Step 4 `validation.html` |
| **Step 4** | `tests/web/test_p3_4_auth_and_system_views.py` | `test_safe_error_view_renders_correlation_id_and_no_tracebacks` | add | TC-SEC-12 | `adapters/web/templates/error.html`, `app.py` | automated (HTTP) | Requires Step 4 `error.html` |
| **Step 5** | `tests/web/test_p3_4_member_views.py` | `test_my_characters_card_grid_renders_initials_fallback_and_badges` | add | Master Prompt §3.3 / view-model contract §4 (VM-05) (no dedicated accepted test ID) | `adapters/web/templates/my_characters.html`, `portal_routes.py` | automated (HTTP) | Requires Step 5 `my_characters.html` |
| **Step 5** | `tests/web/test_p3_4_member_views.py` | `test_my_characters_unrecorded_level_renders_not_recorded` | add | TC-VM-05 | `adapters/web/templates/my_characters.html`, `portal_routes.py` | automated (HTTP) | Requires Step 5 `my_characters.html` |
| **Step 5** | `tests/web/test_p3_4_member_views.py` | `test_my_characters_contains_zero_mutation_forms` | add | route contract §1 / Master Prompt §3.3 (no dedicated accepted test ID) | `adapters/web/templates/my_characters.html` | automated (structural) | Requires Step 5 `my_characters.html` |
| **Step 5** | `tests/web/test_p3_4_member_views.py` | `test_character_detail_renders_stat_blocks_and_profile_tables` | add | view-model contract §4 (VM-06) (no dedicated accepted test ID) | `adapters/web/templates/character_detail.html`, `portal_routes.py` | automated (HTTP) | Requires Step 5 `character_detail.html` |
| **Step 5** | `tests/web/test_p3_4_member_views.py` | `test_character_detail_deferred_fields_render_owning_package_without_controls` | add | TC-VM-03 | `adapters/web/templates/character_detail.html`, `portal_routes.py` | automated (HTTP) | Requires Step 5 `character_detail.html` |
| **Step 6** | `tests/web/test_p3_4_council_character_views.py` | `test_council_characters_renders_cursor_pagination_and_filter_form` | add | view-model contract §4 (VM-07) (no dedicated accepted test ID) | `adapters/web/templates/council_characters.html`, `portal_routes.py` | automated (HTTP) | Requires Step 6 `council_characters.html` |
| **Step 6** | `tests/web/test_p3_4_council_character_views.py` | `test_character_links_renders_active_and_historical_tables` | add | view-model contract §4 (VM-08) (no dedicated accepted test ID) | `adapters/web/templates/character_links.html`, `portal_routes.py` | automated (HTTP) | Requires Step 6 `character_links.html` |
| **Step 6** | `tests/web/test_p3_4_council_character_views.py` | `test_character_links_mutation_forms_render_exact_accepted_inputs` | add | Master Prompt §5.3 / route contract §5.1 (R-25, R-26, R-27) (no dedicated accepted test ID) | `adapters/web/templates/character_links.html`, `portal_routes.py` | automated (HTTP) | Requires Step 6 `character_links.html` |
| **Step 6** | `tests/web/test_p3_4_council_character_views.py` | `test_character_links_mutations_refuse_without_valid_csrf` | add | TC-SEC-01 (refusal half) | `adapters/web/portal_routes.py` | automated (HTTP) | Requires Step 6 routes and forms |
| **Step 6** | `tests/web/test_p3_4_council_character_views.py` | `test_identity_search_fragment_renders_candidates_and_non_identity_banner` | add | view-model contract §4 (VM-09) (no dedicated accepted test ID) | `adapters/web/templates/identity_search.html`, `portal_routes.py` | automated (HTTP) | Requires Step 6 `identity_search.html` |
| **Step 6** | `tests/web/test_p3_4_council_character_views.py` | `test_identity_search_fragment_answers_401_when_unauthenticated` | add | Master Prompt §5.1 / route contract §2.3 (no dedicated accepted test ID) | `adapters/web/templates/identity_search.html`, `portal_routes.py` | automated (HTTP) | Requires Step 6 `identity_search.html` |
| **Step 7** | `tests/web/test_p3_4_identity_and_role_views.py` | `test_identity_migration_forms_render_exact_accepted_inputs` | add | Master Prompt §5.3 / route contract §5.1 (R-29, R-30) (no dedicated accepted test ID) | `adapters/web/templates/identity_migration.html`, `portal_routes.py` | automated (HTTP) | Verifies R-29 has `csrf_token`, `version`, `reason` and R-30 has `csrf_token`, `reason` (no version) |
| **Step 7** | `tests/web/test_p3_4_identity_and_role_views.py` | `test_identity_migration_reflects_revoked_confirmation_state` | add | TC-MIG-19 (rendering reflection) | `adapters/web/templates/identity_migration.html`, `portal_routes.py` | automated (HTTP) | Requires Step 7 `identity_migration.html` |
| **Step 7** | `tests/web/test_p3_4_identity_and_role_views.py` | `test_field_profile_renders_classification_table_and_snapshot_modes` | add | view-model contract §4 (VM-11) (no dedicated accepted test ID) | `adapters/web/templates/field_profile.html`, `portal_routes.py` | automated (HTTP) | Requires Step 7 `field_profile.html` |
| **Step 7** | `tests/web/test_p3_4_identity_and_role_views.py` | `test_role_capabilities_forms_render_exact_accepted_inputs` | add | Master Prompt §5.3 / route contract §5.1 (R-33, R-34, R-38) (no dedicated accepted test ID) | `adapters/web/templates/role_capabilities.html`, `portal_routes.py` | automated (HTTP) | Requires Step 7 `role_capabilities.html` |
| **Step 7** | `tests/web/test_p3_4_identity_and_role_views.py` | `test_role_capabilities_renders_bootstrap_mapping_non_revocable` | add | route contract §5.1 / view-model contract §4 (VM-12) (no dedicated accepted test ID) | `adapters/web/templates/role_capabilities.html`, `portal_routes.py` | automated (HTTP) | Requires Step 7 `role_capabilities.html` |
| **Step 7** | `tests/web/test_p3_4_identity_and_role_views.py` | `test_account_identities_renders_linked_identities_and_r37_unlink_form` | add | Master Prompt §5.3 / view-model contract §4 (VM-13) (no dedicated accepted test ID) | `adapters/web/templates/account_identities.html`, `portal_routes.py` | automated (HTTP) | Verifies R-37 form renders `csrf_token` only |
| **Step 7** | `tests/web/test_p3_4_identity_and_role_views.py` | `test_account_identity_link_start_r36_renders_200_html_denied_view` | add | D-03-5 / route contract §5 (R-36) | `adapters/web/templates/account_identities.html`, `portal_routes.py` | automated (HTTP) | Requires Step 7 `account_identities.html` |
| **Step 8** | `tests/web/test_p3_4_snapshot_views.py` | `test_council_snapshots_renders_snapshot_ledger_and_folder_choices` | add | view-model contract §8 (VM-14) (no dedicated accepted test ID) | `adapters/web/templates/council_snapshots.html`, `import_routes.py` | automated (HTTP) | Requires Step 8 `council_snapshots.html` |
| **Step 8** | `tests/web/test_p3_4_snapshot_views.py` | `test_council_snapshots_folder_select_form_requires_admin_authorization` | add | route contract §5.1 (R-41) (no dedicated accepted test ID) | `adapters/web/templates/council_snapshots.html`, `import_routes.py` | automated (HTTP) | Verifies R-41 action `POST /v1/admin/snapshots/{snapshot_id}/folder` with `csrf_token`, `folder_id` |
| **Step 8** | `tests/web/test_p3_4_snapshot_views.py` | `test_council_snapshots_preview_trigger_form_renders_csrf_and_nonce` | add | Master Prompt §5.3 / route contract §5.1 (R-42) (no dedicated accepted test ID) | `adapters/web/templates/council_snapshots.html`, `import_routes.py` | automated (HTTP) | Verifies R-42 action `POST /v1/council/snapshots/{snapshot_id}/preview-jobs` with `csrf_token`, `nonce` |
| **Step 9** | `tests/web/test_p3_4_job_status_views.py` | `test_job_status_full_page_renders_all_job_states_and_confirm_scope` | add | Master Prompt §3.5 / view-model contract §8 (VM-15) (no dedicated accepted test ID) | `adapters/web/templates/job_status.html`, `import_routes.py` | automated (HTTP) | Requires Step 9 `job_status.html` |
| **Step 9** | `tests/web/test_p3_4_job_status_views.py` | `test_job_status_fragment_emits_polling_only_on_queued_and_running_states` | add | Master Prompt §5.2 / route contract §6.2 (no dedicated accepted test ID) | `adapters/web/templates/job_status_fragment.html`, `import_routes.py` | automated (HTTP) | Requires Step 9 `job_status_fragment.html` |
| **Step 9** | `tests/web/test_p3_4_job_status_views.py` | `test_job_status_fragment_stops_polling_on_terminal_states` | add | Master Prompt §5.2 / route contract §6.2 (no dedicated accepted test ID) | `adapters/web/templates/job_status_fragment.html`, `import_routes.py` | automated (HTTP) | Requires Step 9 `job_status_fragment.html` |
| **Step 9** | `tests/web/test_p3_4_job_status_views.py` | `test_job_status_forms_render_exact_accepted_inputs_and_forbid_server_fields` | add | Master Prompt §5.3 / route contract §5.1 (R-45, R-46) (no dedicated accepted test ID) | `adapters/web/templates/job_status.html`, `import_routes.py` | automated (HTTP) | Verifies R-45 is `csrf_token` only; R-46 is `csrf_token`, `preview_token`, `nonce` only |
| **Step 9** | `tests/web/test_p3_4_job_status_views.py` | `test_job_status_fragment_answers_401_when_unauthenticated` | add | Master Prompt §5.1 / route contract §2.3 (no dedicated accepted test ID) | `adapters/web/templates/job_status_fragment.html`, `import_routes.py` | automated (HTTP) | Requires Step 9 `job_status_fragment.html` |
| **Step 10** | `tests/web/test_p3_4_import_and_audit_views.py` | `test_import_result_renders_immutable_receipt_and_issue_summary` | add | view-model contract §8 (VM-17) (no dedicated accepted test ID) | `adapters/web/templates/import_result.html`, `import_routes.py` | automated (HTTP) | Requires Step 10 `import_result.html` |
| **Step 10** | `tests/web/test_p3_4_import_and_audit_views.py` | `test_audit_search_renders_filter_form_and_cursor_pagination` | add | view-model contract §8 (VM-18) (no dedicated accepted test ID) | `adapters/web/templates/audit_search.html`, `import_routes.py` | automated (HTTP) | Requires Step 10 `audit_search.html` |
| **Step 10** | `tests/web/test_p3_4_import_and_audit_views.py` | `test_audit_results_fragment_renders_structured_events` | add | view-model contract §8 (VM-18) (no dedicated accepted test ID) | `adapters/web/templates/audit_results.html`, `import_routes.py` | automated (HTTP) | Requires Step 10 `audit_results.html` |
| **Step 10** | `tests/web/test_p3_4_import_and_audit_views.py` | `test_audit_results_fragment_answers_401_when_unauthenticated` | add | Master Prompt §5.1 / route contract §2.3 (no dedicated accepted test ID) | `adapters/web/templates/audit_results.html`, `import_routes.py` | automated (HTTP) | Requires Step 10 `audit_results.html` |
| **Step 11** | `tests/web/test_p3_4_accessibility.py` | `test_base_template_owns_document_landmarks_and_skip_link` | add | Master Prompt §6 (no dedicated accepted test ID) | `adapters/web/templates/base.html` | automated (structural) | Requires Step 11 shell verification |
| **Step 11** | `tests/web/test_p3_4_accessibility.py` | `test_full_page_templates_render_single_page_h1_and_heading_hierarchy` | add | Master Prompt §6 (no dedicated accepted test ID) | 20 full-page child templates | automated (structural) | Requires all 20 full pages in Step 11 |
| **Step 11** | `tests/web/test_p3_4_accessibility.py` | `test_fragment_templates_render_fragment_structures_without_document_landmarks` | add | Master Prompt §6 (no dedicated accepted test ID) | 3 fragment templates | automated (structural) | Requires all 3 fragments in Step 11 |
| **Step 11** | `tests/web/test_p3_4_accessibility.py` | `test_no_production_template_imports_or_references_design_prototype` | add | TC-UI-06 | all 24 templates & static assets | automated (structural) | Requires production templates & assets |
| **Step 11** | `tests/web/test_p3_4_accessibility.py` | `test_color_contrast_tokens_source_tool_check` | add | TC-UI-07 (source tool portion) | production CSS tokens | automated (source tool) | Requires Step 11 contrast matrix |
| **Step 11** | *(manual / supervised checklist)* | `supervised_wcag_2_2_aa_surface_contrast_check` | add | TC-UI-07 (supervised confirmation portion) | production rendered surfaces | supervised verification | Requires Step 11 rendered surfaces |
| **Step 12** | `tests/web/test_p3_4_security_and_escaping.py` | `test_all_portal_and_import_responses_carry_exact_security_headers` | add | TC-SEC-05 | `app.py`, `portal_routes.py`, `import_routes.py` | automated (HTTP) | Requires Step 12 full response pass |
| **Step 12** | `tests/web/test_p3_4_security_and_escaping.py` | `test_zero_templates_use_jinja_safe_filter` | add | TC-SEC-08 | all 24 templates | automated (structural) | Requires all templates in Step 12 |
| **Step 12** | `tests/web/test_p3_4_security_and_escaping.py` | `test_hostile_input_parametrization_renders_inert_across_all_views` | add | TC-SEC-09 | all templates and view models | automated (response inspection) | Requires all templates in Step 12 |
| **Step 12** | `tests/web/test_p3_4_security_and_escaping.py` | `test_zero_templates_contain_hx_on_event_attributes` | add | TC-SEC-10 | all 24 templates | automated (structural) | Requires all templates in Step 12 |
| **Step 12** | `tests/web/test_p3_4_security_and_escaping.py` | `test_no_view_model_field_is_interpolated_inside_script_tags` | add | TC-SEC-11 | all 24 templates | automated (structural) | Requires all templates in Step 12 |
| **Step 12** | `tests/web/test_p3_4_security_and_escaping.py` | `test_all_essential_flows_provide_no_javascript_fallback_forms` | add | Master Prompt §3.6 (partial HTTP evidence) | all full pages and forms | automated (HTTP) | Requires all templates in Step 12 |
| **Step 12** | `tests/web/test_p3_4_browser.py` | `test_all_essential_flows_complete_in_browser_with_javascript_disabled` | add | Master Prompt §3.6 (browser completion evidence) | full pages and static assets | automated (browser) | Requires Playwright & installed browser; not run in Step 1 |
| **Step 12** | `tests/web/test_structural_guards.py` | `test_the_registered_route_set_equals_the_contract_exactly` | existing / rerun | TC-STRUCT-01 | `adapters/web/app.py` | automated (structural) | Verifies unchanged closed 39 routes + 1 mount |
| **Step 12** | `tests/web/test_structural_guards.py` | `test_every_view_model_is_frozen_slotted_and_holds_no_mutable_collection` | existing / rerun | TC-STRUCT-02, TC-VM-01 | `application/web/view_models.py` | automated (structural) | Verifies unchanged closed 22 view models |

---

## 7. Later-step overlap analysis

Analysis of pre-existing dirty-tree changes versus planned P3.4 allowlists:

### 7.1 Historical Step 1 dirty-tree paths overlapping P3.4 allowlists

| Working Tree Path | Historical Status (at Step 1 receipt) | Current Status in `HEAD` | Ownership & Characterization | P3.4 Step Overlap | P3.4 Handling Rule |
|---|---|---|---|---|---|
| `adapters/web/templates/conflict.html` | `M` (modified) | tracked (unmodified) | Minimal contract template from backend delivery. | **Step 4** | Will be replaced in Step 4 with production-styled 409 conflict rendering. |
| `adapters/web/templates/audit_results.html` | `??` (untracked) | tracked (unmodified) | Minimal fragment template from P3.3 backend delivery. | **Step 10** | Will be replaced in Step 10 with production-styled audit results table fragment. |
| `adapters/web/templates/audit_search.html` | `??` (untracked) | tracked (unmodified) | Minimal contract template from P3.3 backend delivery. | **Step 10** | Will be replaced in Step 10 with production-styled audit search full page. |
| `adapters/web/templates/council_snapshots.html` | `??` (untracked) | tracked (unmodified) | Minimal contract template from P3.3 backend delivery. | **Step 8** | Will be replaced in Step 8 with production-styled snapshot list full page. |
| `adapters/web/templates/import_result.html` | `??` (untracked) | tracked (unmodified) | Minimal contract template from P3.3 backend delivery. | **Step 10** | Will be replaced in Step 10 with production-styled import receipt full page. |
| `adapters/web/templates/job_status.html` | `??` (untracked) | tracked (unmodified) | Minimal contract template from P3.3 backend delivery. | **Step 9** | Will be replaced in Step 9 with production-styled job status full page. |
| `adapters/web/templates/job_status_fragment.html` | `??` (untracked) | tracked (unmodified) | Minimal fragment template from P3.3 backend delivery. | **Step 9** | Will be replaced in Step 9 with production-styled job polling fragment. |
| `adapters/web/static/` | `??` (untracked directory) | tracked directory | Contains `.gitkeep` from accepted D-03 delivery (`C-P3.4-A`). | **Step 2** | Production CSS, vendored HTMX, and emblem will be added under this directory in Step 2. |

### 7.2 Non-overlapping paths (strictly out of bounds for P3.4)

All other files belong to backend implementations, migrations, database adapters, application services, or project management records (e.g. `adapters/web/app.py`, `portal_routes.py`, `import_routes.py`, `static_assets.py`, `composition.py`, `middleware.py`, `repositories.py`, `application/`, `migrations/`, `docs/contracts/`, `docs/project-management/`, `tests/web/test_p3_3_*.py`, `tests/web/test_d03_contract_correction.py`, `tests/web/test_static_asset_surface.py`).
**Rule:** P3.4 will not edit, revert, reformat, or normalize any of these files.

---

## 8. Static-asset contract facts and anticipated assets

### 8.1 Accepted M-01 `/static/` contract facts

Per `docs/contracts/phase-3-route-authorization-contract.md` §1.2 and `adapters/web/static_assets.py` (accepted D-03 correction `C-P3.4-A`, item D-03-1):
1. **Mount Prefix:** `/static` served same-origin from repository-owned `adapters/web/static/` (`STATIC_ROOT`).
2. **Methods Permitted:** `GET` and `HEAD` only. All other HTTP methods (`POST`, `PUT`, `PATCH`, `DELETE`) are refused with `405 Method Not Allowed` across both existing and non-existent paths (preventing oracle directory enumeration).
3. **Authentication & Session:** Public, unauthenticated, zero session requirement, zero CSRF token requirement. Static asset requests set no cookies, refresh no cookies, and do not touch or extend session idle lifetimes (N-06).
4. **Host Protection (N-01):** Enforced by outermost `TrustedHostMiddleware`; requests with unknown/attacker host header are refused with `400`.
5. **Portal Kill Switch Exemption (N-56):** Static assets remain accessible when the operator kill switch is engaged, ensuring incident, maintenance, login, and error pages retain proper styling and presentation.
6. **URL Grammar:** Every path segment must match `SEGMENT` regex (`^[A-Za-z0-9][A-Za-z0-9._-]*$`). Dotfiles (including `.gitkeep`), empty segments, and encoded traversals (`%2e%2e`) are refused with safe `404` (not `400`), preventing grammar enumeration.
7. **Cache-Control Policy:**
   - **Fingerprinted filenames** (`<stem>.<16 lowercase hex>.<ext>` matching `FINGERPRINTED` regex `^.+\.[0-9a-f]{16}\.[A-Za-z0-9]+$`): `public, max-age=31536000, immutable` (1 year immutable cache).
   - **Non-fingerprinted filenames:** `public, max-age=0, must-revalidate`.
   - Exempt from the authenticated `Cache-Control: no-store` response header rule.
8. **Security Headers:** Inherits N-26 CSP, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, COOP, CORP, and `Permissions-Policy`.

### 8.2 Anticipated Step 2 asset roles (without premature version or filename selection)

The following production asset roles will be introduced in Step 2 without prematurely locking final filenames or versions:
1. **Design tokens stylesheet role:** Production CSS custom properties defining color tokens, typography, spacing, surface colors, and focus indicators adapted from the visual design language.
2. **Production layout styles role:** Production layout primitives (`.table-container`, `.card-grid`, `.fb-blade-divider`, 2-level header, focus rings, reduced-motion overrides).
3. **Vendored HTMX library role:** Single reviewed vendored HTMX library file complying with configuration contract §1.5 (version, upstream URL, and SHA-256 header comment). The specific version is to be determined in Step 2 and is not pre-selected here.
4. **Guild emblem asset role:** Guild emblem token image served same-origin.
5. **Static asset integrity metadata role:** Mechanism for tracking and verifying static asset integrity and cache policy (exact packaging/manifest mechanism unresolved for Step 2).

---

## 9. Literal commands, exit codes and results

### 9.1 Visual freeze manifest verification
```bash
$ sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256
```
- **Exit Code:** `0`
- **Output:**
```text
design-prototype/assets/freedom-blades-token.png: OK
design-prototype/assets/portraits/lyra.png: OK
design-prototype/assets/portraits/thorin.png: OK
design-prototype/assets/portraits/valerius.png: OK
design-prototype/character-detail.html: OK
design-prototype/components.html: OK
design-prototype/council-approval.html: OK
design-prototype/css/styles.css: OK
design-prototype/css/tokens.css: OK
design-prototype/index.html: OK
design-prototype/js/portrait-preview.js: OK
design-prototype/login.html: OK
design-prototype/my-characters.html: OK
design-prototype/reconciliation.html: OK
```

### 9.2 Non-database structural guards and static asset tests
```bash
$ ./venv-web/bin/python -m pytest tests/web/test_structural_guards.py tests/web/test_static_asset_surface.py -m "not database" -v
```
- **Exit Code:** `0`
- **Output Summary:** `58 passed, 64 skipped in 0.28s`
*(64 tests in the two selected modules skipped at runtime because `TEST_DATABASE_URL` is unconfigured in this non-database execution environment; full database suites in other test files were not selected or run)*

Representative passing assertions verified by this run:
- `test_the_registered_route_set_equals_the_contract_exactly`: PASSED (TC-STRUCT-01: parses all 39 contract routes and 1 mount from `docs/contracts/phase-3-route-authorization-contract.md` and verifies exact match against `ROUTE_INVENTORY` and `MOUNT_INVENTORY`)
- `test_the_web_module_graph_never_reaches_the_bot_config`: PASSED
- `test_importing_the_web_package_does_not_pull_in_the_bot_config`: PASSED
- `test_each_startup_refusal_refuses_with_its_documented_identifier` (S-01 to S-12): PASSED
- `test_every_view_model_is_frozen_slotted_and_holds_no_mutable_collection`: PASSED
- `test_the_implemented_view_models_are_a_subset_of_the_documented_set`: PASSED
- `test_bounded_text_truncates_and_says_so`: PASSED
- `test_a_deferred_field_cannot_carry_a_value`: PASSED
- `test_the_denial_view_cannot_carry_anything_that_would_break_byte_identity`: PASSED
- `test_the_denied_reason_vocabulary_stays_closed`: PASSED
- `test_the_cache_policy_reads_the_fingerprint_grammar` (9 parameter rows): PASSED
- `test_the_url_grammar_accepts_exactly_the_documented_shape` (18 parameter rows): PASSED
- `test_the_static_root_ships_only_its_placeholder`: PASSED
- `test_the_public_origin_fixture_is_the_host_the_client_uses`: PASSED

### 9.3 Git diff whitespace check
```bash
$ git diff --check
```
- **Exit Code:** `0`
- **Output:** *(empty; zero whitespace errors)*
- **Diff Scope:** `git diff --check` evaluates tracked working tree modifications against `HEAD` (covering `docs/review/phase-3-p3-4-gemini-baseline.md`).

### 9.4 Final Git status check
```bash
$ git status --short
```
- **Exit Code:** `0`
- **Output:**
```text
 M "docs/review/Handover information"
 M docs/review/phase-3-p3-4-gemini-baseline.md
```

### 9.5 Read-only count verification, uniqueness checks, and mechanical contract comparison

1. **Mechanical 39-Route and 1-Mount Contract Audit:**
   Verified by `test_the_registered_route_set_equals_the_contract_exactly` in `tests/web/test_structural_guards.py` (which passed in §9.2). It parses the Markdown table in `docs/contracts/phase-3-route-authorization-contract.md` via `parsed_contract_routes()` and `parsed_contract_mounts()`, asserting equality against `ROUTE_INVENTORY` (39 routes) and `MOUNT_INVENTORY` (1 mount) in `adapters/web/app.py`.
2. **Production Template Count and Uniqueness Check (24 unique files: 1 base + 20 children + 3 fragments):**
   ```bash
   $ ./venv-web/bin/python -c "from pathlib import Path; p = sorted(Path('adapters/web/templates').glob('*.html')); print('Total:', len(p), 'Unique:', len(set(p)))"
   Total: 24 Unique: 24
   ```
3. **Closed View Model Set (22 view models):**
   ```bash
   $ ./venv-web/bin/python -c "from application.web.view_models import IMPLEMENTED_VIEW_MODELS; print('view_models:', len(IMPLEMENTED_VIEW_MODELS))"
   view_models: 22
   ```
4. **Web Test Module Count (50 modules):**
   ```bash
   $ ls -1 tests/web/test_*.py | wc -l
   50
   ```
5. **Reference-only Prototype Token Declaration Inventory:**
   ```bash
   $ grep -E "^\s*--[a-zA-Z0-9_-]+:" design-prototype/css/tokens.css | wc -l
   71
   ```
   *(Note: 71 is the count of custom properties declared in the frozen visual prototype reference `design-prototype/css/tokens.css`, not a production acceptance contract)*

---

## 10. Checks not run and why

The following check classes were deliberately not run during Step 1, with technical justification:

1. **Full PostgreSQL Database Test Suites (`tests/test_database_schema.py`, `tests/web/test_p3_2_*.py`, `tests/web/test_p3_3_*.py`, etc.):**
   *Why Not Run:* Step 1 is strictly non-mutating and non-database. Running database suites requires an active `TEST_DATABASE_URL` and executes Alembic database migrations. In the two selected modules (`test_structural_guards.py` and `test_static_asset_surface.py`), exactly 64 tests requiring the disposable database skipped because `TEST_DATABASE_URL` was not configured.
2. **Headless Browser Test Suites (Playwright):**
   *Why Not Run:* Browser execution was outside Step 1 scope. The Step 1 prompt did not require or authorize browser installation or execution. Automated browser suites remain governed by the master prompt and require production templates, static CSS, and vendored HTMX assets to be delivered in Steps 2–11.
3. **Real-Device Physical Hardware Inspection (TC-UI-08):**
   *Why Not Run:* Reserved exclusively for Acceptance Authority Peter Duscha on maintainer physical hardware. Cannot be claimed or simulated by agent inspection.
4. **Assistive Technology Screen Reader Audio Traversal (TC-UI-09):**
   *Why Not Run:* Reserved exclusively for Peter Duscha / live maintainer assistive technology evaluation. Cannot be claimed or simulated by agent inspection.
5. **Staging Environment Deployments & Network Calls:**
   *Why Not Run:* Staging exposure is not authorized (I-06 remains open); no live Discord OAuth, Google Sheets, or Foundry VTT endpoints may be contacted.

---

## 11. Historical discrepancies, resolution, and residual risks

### 11.1 Historical blocking master-prompt contradictions

At the historical blocked checkpoint, the master prompt
(`docs/review/phase-3-p3-4-gemini-implementation-prompt.md`) released for P3.4
contained two stale statements that contradicted accepted D-03 backend facts
and current code:

1. **Master Prompt §4 Hard Prohibitions Contradiction (VM-22 vs VM-02 Placeholder Shape):**
   - **Master Prompt Text (§4, lines 187–191):** States that `denied.html` receives a `VM-02`-shaped object whose three fields (`guild_display_name`, `checked_at`, `correlation`) are "deliberately inert placeholders".
   - **Accepted Contract & Implementation:** Accepted D-03 correction item D-03-6, view-model contract §8 (`phase-3-view-model-contract.md` lines 31–34, 932–960), and `application/web/view_models.py` (lines 1028–1064, 1450) establish **VM-22 `DeniedView`**, which carries only `state: PageState` and `reason: DeniedReason`. It has deliberately **no** correlation ID, guild display name, timestamp, or object ID.
   - **Discrepancy Impact:** The master prompt's hard prohibition is stale. Step 1 cannot declare zero discrepancies when the authoritative prompt contradicts the accepted contract and implementation.

2. **Master Prompt §5.5 Contract Facts Contradiction (R-36 Route Table Cell):**
   - **Master Prompt Text (§5.5, lines 224–227):** States that *"The route contract's table cell says `303`; its §5.1 prose and the implementation say otherwise, and D-03-5 is the correction."*
   - **Accepted Contract & Implementation:** Accepted D-03 correction item D-03-5 and route authorization contract §5 (`phase-3-route-authorization-contract.md` lines 23–27, 479, 649–658) already corrected the R-36 inventory table cell to **`200` HTML · VM-13 (`denied`)**. The master prompt's claim that the route contract table cell still says `303` is stale. (The separate caller matrix notation `✗ 303` in route contract §5.2 line 689 reflects unauthenticated caller navigation redirecting to login, which is distinct from the authenticated response fact).
   - **Discrepancy Impact:** The master prompt's description of the contract record is stale.

**Remediation Action Required:** These prompt-record defects require a narrow prompt correction to `docs/review/phase-3-p3-4-gemini-implementation-prompt.md` prepared by the backend contract owner (Claude), reviewed independently by Codex, and released by Acceptance Authority Peter Duscha. Gemini is not authorized to edit the master prompt.

### 11.2 Resolution recorded 2026-08-20

The two prompt-record defects above were corrected in the master prompt by
Claude, the backend contract owner, without changing a contract, backend,
template, test, asset, route, view model, permission or runtime behavior. The
master prompt changed from SHA-256
`0a396c8f5c29c2528f41ad93510eb0b3a0f4dcf86da9a5df528471209242f8ad`
to accepted SHA-256
`cfe0517b45abc7d4dda4427c453af71348f8e147558373e581250dd851735fbb`.

Codex independently reviewed the two-hunk correction and recommended
acceptance with no blocking or important finding. Peter/Acceptance Authority
then accepted and re-released the corrected master prompt on 2026-08-20. The
correction and acceptance are recorded in
`phase-3-p3-4-master-prompt-correction-acceptance.md`.

The former blocker is therefore resolved:

1. master-prompt §4 now names VM-22 `DeniedView`, containing only `state` and
   closed-vocabulary `reason`, while VM-02 remains the distinct
   `non_member.html` recovery carrier; and
2. master-prompt §5.5 now states that R-36 answers `200` HTML with VM-13 in its
   `denied` state, while the caller-matrix `U: ✗ 303` continues to describe
   unauthenticated navigation to login.

No other Step 1 discrepancy or stop condition remains. This closes Step 1 but
does not release Step 2.

### 11.3 Open questions for maintainer review

1. Four screens lacking prototype pages (VM-10, VM-12, VM-13, VM-18) remain scheduled for visual construction in Steps 7 and 10 and visual acceptance by Peter at P3.G4.

### 11.4 Residual risks

- **RR-01 (Static Asset Delivery):** Ensuring fingerprinted CSS and vendored HTMX cache policies match deployment expectations without broken asset links under reverse proxy. Mitigated by `test_static_asset_surface.py` and M-01 contract.
- **RR-02 (Assistive Technology & Focus Management):** Ensuring dynamic HTMX swaps preserve focus and do not flood live regions. Mitigated by progressive enhancement and manual AT reservation for Peter (TC-UI-09).
- **RR-03 (Visual Acceptance on New Screens):** Four screens (VM-10, VM-12, VM-13, VM-18) extend the visual system without prior prototype pages. Mitigated by explicit P3.G4 visual review gate.

---

## 12. Step 1 checkpoint verdict

### Historical verdict: **`BLOCKED: authoritative Gemini prompt correction and release required`**

### Reasons for Blocked Disposition:
1. **Master Prompt Contradictions:** As documented in §11.1, the master prompt (`docs/review/phase-3-p3-4-gemini-implementation-prompt.md`) contains stale assertions regarding `denied.html` carrier shape (claiming VM-02 placeholder shape instead of VM-22 `DeniedView`) and R-36 route contract table status.
2. **Stop Condition Triggered:** The Step 1 prompt (`phase-3-p3-4-gemini-step-01-baseline-prompt.md`) explicitly makes contract/prompt discrepancies a stop condition. Gemini is not authorized to alter backend contracts or the master prompt.
3. **Step 2 Remains Held:** Step 2 (static asset foundation) cannot be started until the authoritative master prompt is corrected, reviewed, and released by the Acceptance Authority.

### Current verdict after corrective acceptance: **`READY FOR STEP 2`**

The three historical blocking conditions above were satisfied on 2026-08-20:
Claude corrected only the two stale prompt passages, Codex independently
reviewed them, and Peter accepted and re-released the corrected master prompt.
The baseline remains complete, the accepted contract and implementation agree,
and no other Step 1 finding remains open.

`READY FOR STEP 2` closed this checkpoint only. Peter subsequently released the
separate bounded Step 2 prompt on 2026-08-20. Gemini may now change only its
allowlisted production and test files and must stop at the Step 2 checkpoint.

---

*Steps 1–6 are closed and accepted. Peter accepted Step 6 after remediation 06
and independent Codex re-review on 2026-08-20. Peter's same instruction
authorized and released the separately bounded Step 7 prompt under the standing
single-approval rule. Step 8 and every later step remain unreleased.*
