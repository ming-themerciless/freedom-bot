# Phase 3 package P3.4 Gemini Step 1 baseline and closed work map

**Date:** 2026-08-20  
**Status:** RELEASED · Step 1 of 13 Checkpoint Deliverable  
**Author:** Gemini (Production Frontend Implementer)  
**Target Repository:** `/opt/discord-bots/freedom-bot`  
**Sole Permitted Deliverable:** `docs/review/phase-3-p3-4-gemini-baseline.md`  

---

## 1. Scope and evidence-class statement

This document is the baseline deliverable for **Step 1** of package **P3.4** (production frontend integration), executed in accordance with:
1. `docs/review/phase-3-p3-4-gemini-step-01-baseline-prompt.md`;
2. `docs/review/phase-3-p3-4-gemini-implementation-prompt.md`;
3. `docs/review/phase-3-p3-4-gemini-execution-plan.md`;
4. `docs/review/phase-3-delivery-plan.md` (§4 exclusions, §5 P3.4/P3.G4, §7 numeric policy, §11 traceability);
5. `docs/review/phase-3-p3-4-authorisation-and-conditions.md` (including D-03 acceptance & Gemini release 2026-08-20);
6. `docs/contracts/README.md` and all accepted Phase 3 contracts;
7. `docs/review/phase-3-p3-4-gemini-readiness-report.md` §§A1–A10;
8. `docs/review/phase-3-visual-prototype-handoff.md` and the 14-file visual freeze manifest;
9. `.agents/AGENTS.md` and `docs/implementation-plan.md`.

### 1.1 Scope boundary

Step 1 performs **only read-only baseline inspection, verification, and mapping**. It creates this single baseline record (`docs/review/phase-3-p3-4-gemini-baseline.md`). It makes zero edits to existing template files, zero edits to backend Python files, introduces zero static CSS/JS/image assets, creates zero test files, executes zero database migrations, contacts zero external or live services, and accesses zero `.env` credentials, secrets, or real player/guild/Actor data.

### 1.2 Evidence classification

All assertions and findings in this baseline document are classified according to the delivery plan §11 / readiness report §A8 standard:

| Evidence Class | Status in Step 1 | Justification / Description |
|---|---|---|
| **Automated (source / structural)** | **Run & Verified** | Static AST and contract comparisons, visual freeze manifest `sha256sum`, template inventory, `git diff --check`, non-database pytest structural guards in `test_structural_guards.py` and `test_static_asset_surface.py`. |
| **Automated (response / HTTP)** | **Deferred to Steps 4–12** | Direct HTTP test cases for view model rendering, response headers, and safe error bodies will be added alongside production templates in later steps. |
| **Automated (browser)** | **Not Run in Step 1** | Headless browser execution (Playwright) requires production templates and static assets delivered in Steps 2–11. |
| **Supervised / Source Contrast** | **Partially Verified** | Prototype CSS token contract verified; production-owned contrast matrix to be confirmed in Step 11. |
| **Real-Device (TC-UI-08)** | **Explicitly Not Run** | Reserved exclusively for Peter Duscha on maintainer hardware. |
| **Assistive Technology (TC-UI-09)** | **Explicitly Not Run** | Reserved exclusively for Peter Duscha / maintainer live traversal. |
| **Disposable PostgreSQL / DB** | **Not Run in Step 1** | Baseline checks are strictly non-mutating and non-database; DB suite skipped per step instructions. |
| **Staging / Live Environment** | **Explicitly Prohibited** | Belongs to I-06; no live Discord, Google, Foundry or staging interaction. |

---

## 2. Dirty-tree baseline

Literal output of `git status --short` executed in `/opt/discord-bots/freedom-bot` prior to creating this document:

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

**Stash status:** `stash@{0}: On main: temp before rebase` was neither inspected nor touched.

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

**Exit code:** `0`  
**Result:** All 14 visual prototype files under `design-prototype/` match the accepted visual freeze manifest exactly (14/14 OK).

---

## 4. Current production template & static root file inventory with SHA-256

Literal SHA-256 checksums computed across all 24 existing template files in `adapters/web/templates/` and the static root (`adapters/web/static/`):

| File Path | SHA-256 Checksum | Status |
|---|---|---|
| `adapters/web/templates/account_identities.html` | `f3ab67ec4f0eb9b10555fe5263b871b15c1d18bfd15dc2ae6bf0a8c39bf7f0d5` | present (tracked) |
| `adapters/web/templates/audit_results.html` | `11ee0efcba8892970dee0870b5612d0fbf9c5091d5cf954ddf77e4af4f98291e` | present (untracked P3.3) |
| `adapters/web/templates/audit_search.html` | `c54db1a4cc1779a52921269641330f79d295a843086eb198916a2f07c6e61c15` | present (untracked P3.3) |
| `adapters/web/templates/base.html` | `51f45cf7ae559923c1f37c14d7d8dec19ab4004a8200d8a653569c06e9d855d9` | present (tracked) |
| `adapters/web/templates/character_detail.html` | `7be58ab1bb9436fda39801ff4a31e4c938301b1c335e0fe53e1411ca795c4cf4` | present (tracked) |
| `adapters/web/templates/character_links.html` | `fbdbfe0c761304a77928b569568a8b79be3ef25ed4ae4a51fee6eb57c89cfa8b` | present (tracked) |
| `adapters/web/templates/conflict.html` | `3aa735cde72995d016782b6308ddc61e310a4a6bfde6258441351380306d6d86` | present (modified P3.3) |
| `adapters/web/templates/council_characters.html` | `cffc9bbb63773028deb4b0056c9a9d2c82a185c8f00a91530a623efd62c81661` | present (tracked) |
| `adapters/web/templates/council_snapshots.html` | `0b216a54636e3d8d9715fa08028fcf853af888d5ca26611da5155656ba04bf4d` | present (untracked P3.3) |
| `adapters/web/templates/degraded.html` | `56ea9c866df7d883abe8a62197acefcec9d5d5ad3da59f31c37206ce1f2fd799` | present (tracked) |
| `adapters/web/templates/denied.html` | `5f29922f6b48739d03874b3afb3a41953dc0bd0185b25d982800e860dd0c5305` | present (tracked) |
| `adapters/web/templates/emergency.html` | `8d2b4bb671e8c8b4b9fbef4b37f745d46622b6be5e965e2fcbb712faea7dd61a` | present (tracked) |
| `adapters/web/templates/error.html` | `60ac158aebf5758a6e7f219b7230d372843bff77a0d395fbcaf8bb36154a20c2` | present (tracked) |
| `adapters/web/templates/field_profile.html` | `06a2b6a5e389b6c936f016df95069b82c26741dba5e402ae2c9ad0d306181e91` | present (tracked) |
| `adapters/web/templates/identity_migration.html` | `ededffd5adb842bd0a33bb6f3f098c0497d3d6935d5827ecac02727af849a878` | present (tracked) |
| `adapters/web/templates/identity_search.html` | `fe5cb51fdfdcf5a829a7569766321ad6b8b555f8dbc3b520b94158a028c53f6e` | present (tracked) |
| `adapters/web/templates/import_result.html` | `152b84f766211b886ddd67ca1ce03c53cb37ceefc9ea5678cd22f7f2b7f3fff6` | present (untracked P3.3) |
| `adapters/web/templates/job_status.html` | `b106fe0f2e7f807fef4462504bf23e669e731accac309a1157cdcdc17146a0ea` | present (untracked P3.3) |
| `adapters/web/templates/job_status_fragment.html` | `4993979df628907b7639916e6e3e47d0b1ed795854e393c5bc47e4af7682b2b1` | present (untracked P3.3) |
| `adapters/web/templates/login.html` | `1fee4161bddea58712de35ab952cdaa7c892450d0c2ee20b47ee8d333c7879a4` | present (tracked) |
| `adapters/web/templates/my_characters.html` | `28eb6391c37e50383103ad05ef98d0fd3d6669117edb73251de570f0871ccf72` | present (tracked) |
| `adapters/web/templates/non_member.html` | `565e9f1697e66fae2e0db3e4f0dd7bd1a0b3bf12fc5817652b424968fb0b76c7` | present (tracked) |
| `adapters/web/templates/role_capabilities.html` | `bf1ce7d09096b8d41fcde29fc170bf43615d462a7e7015a13de89b3f3d4a0b3b` | present (tracked) |
| `adapters/web/templates/validation.html` | `54deb119e685eb264405db013ee43b3076214e4f0d9026d84821a606764a2a65` | present (tracked) |
| `adapters/web/static/.gitkeep` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | present (untracked) |
| `adapters/web/static/css/tokens.css` | `absent` | planned Step 2 |
| `adapters/web/static/css/styles.css` | `absent` | planned Step 2 |
| `adapters/web/static/js/htmx.min.js` | `absent` | planned Step 2 |
| `adapters/web/static/assets/freedom-blades-token.png` | `absent` | planned Step 2 |
| `adapters/web/templates/components/header.html` | `absent` | planned Step 3 |
| `adapters/web/templates/components/footer.html` | `absent` | planned Step 3 |
| `adapters/web/templates/components/portrait_fallback.html` | `absent` | planned Step 3 |
| `adapters/web/templates/components/summary_cards.html` | `absent` | planned Step 3 |
| `adapters/web/templates/components/alert_banner.html` | `absent` | planned Step 3 |

---

## 5. Complete template / route / view-model / state / flow / reference / step matrix

The following table establishes the complete, closed mapping for all 24 production templates in `adapters/web/templates/`:

| # | Production Template | Rendering Route(s) & Handler | View Model ID & Type | Applicable `PageState` & Nested States | Caller / Capability Class | Full-Page / Fragment Role | Essential No-JavaScript Flow | Prototype Reference | Planned Step |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `base.html` | None (inherited root layout for all 20 full pages) | Layout context (`vm`, `title`, etc.) | Layout envelope (`ready`, `empty`, `stale`, `denied`, `invalid`, `error`) | All callers (`U`, `N`, `M`, `C`, `A`, `CA`, `BG`, `AC`) | Shared shell layout | Complete semantic HTML5 landmarks (`header`, `nav`, `main`, `footer`), skip link (`#main-content`), navigation links. 100% functional without JS. | `index.html` & `components.html` | **Step 3** |
| 2 | `login.html` | R-02 (`GET /v1/login`) · `_login` in `app.py` | VM-01 · `LoginPageView` | `ready`, `error`, `degraded`, `failure` (`LoginFailure` code + correlation UUID) | All callers (`U` primary; auth callers redirected 303) | Full page | Standard `<a href="/v1/auth/discord/start">` link; link to `/v1/auth/emergency`. Works without JS. | `login.html` | **Step 4** |
| 3 | `emergency.html` | R-06 (`GET /v1/auth/emergency`) · `_emergency_login` in `app.py` | VM-04 · `EmergencyLoginView` | `ready`, `failure` (`EmergencyLoginFailure`) | All callers / Server Admin recovery target | Full page | Recovery grant form submits via standard `POST /v1/auth/emergency/recovery` (R-09). Passkey WebAuthn is progressive enhancement with JS. | `login.html` & `components.html` | **Step 4** |
| 4 | `non_member.html` | R-04 refusal & 403 on protected routes · `_discord_callback` & route guards in `app.py` | VM-02 · `NonMemberView` | `denied` (with `guild_display_name`, `checked_at`, `correlation`) | Caller state `N` (valid session, not in guild) | Full page (403 error page) | Static HTML notification with recovery instructions and correlation UUID. Works without JS. | `components.html` | **Step 4** |
| 5 | `degraded.html` | Cross-cutting 503 response · `_degraded` in `portal_routes.py` & `import_routes.py` | VM-03 · `ServiceDegradedView` | `error` (`degraded`, with subsystem & correlation UUID) | Any authenticated caller when N-10 grace exhausted | Full page (503 Service Unavailable) | Static HTML notification of external provider outage with correlation UUID. Works without JS. | `components.html` | **Step 4** |
| 6 | `denied.html` | Cross-cutting 401/403/404 denial · `_denied` in `portal_routes.py` & `import_routes.py` | VM-22 · `DeniedView` | `denied` (`state` and `reason: DeniedReason` only; NO correlation, timestamp, guild, or object ID) | Any caller encountering object-level or capability denial | Full page (401/403/404 safe denial) | Static HTML denial page explaining closed category. Byte-identical across 404 absent/denied (TC-OBJ-07). Works without JS. | `components.html` | **Step 4** |
| 7 | `conflict.html` | Cross-cutting 409 Conflict · `_conflict` in `portal_routes.py` & `import_routes.py` | VM-19 · `ConflictView` | `stale` (`conflict: ConflictKind` enum) | Any caller submitting conflicting version or preview | Full page (409 Conflict) | Static HTML explaining conflict and providing link back to reload fresh state. Works without JS. | `components.html` | **Step 4** |
| 8 | `validation.html` | Cross-cutting 422 Unprocessable · `_validation_error` in `portal_routes.py` & `import_routes.py` | VM-21 · `ValidationView` | `invalid` (`errors: tuple[FieldError, ...]`) | Any caller submitting invalid form fields | Full page (422 Unprocessable Entity) | Static HTML summary of field validation errors with focusable anchors. Works without JS. | `components.html` | **Step 4** |
| 9 | `error.html` | Cross-cutting 500 Safe Error · `_register_error_handlers` in `app.py` | VM-20 · `SafeErrorView` | `error` (`correlation: UUID` and `message_code` only; no traces/SQL) | Any caller | Full page (500 Internal Server Error) | Static HTML error card displaying support correlation UUID. Works without JS. | `components.html` | **Step 4** |
| 10 | `my_characters.html` | R-20 (`GET /v1/characters`) · `characters_index` in `portal_routes.py` | VM-05 · `MyCharactersView` | `ready`, `empty` (`truncated` flag if >50; `level=None` -> "not recorded") | `M`, `C`, `CA` (`guild_member`) | Full page | Standard `<a href="/v1/characters/{id}">` links. Zero `<form>` elements. Read-only. Works without JS. | `my-characters.html` | **Step 5** |
| 11 | `character_detail.html` | R-21 (`GET /v1/characters/{id}`) · `character_detail` in `portal_routes.py` | VM-06 · `CharacterDetailView` | `ready` (`MigrationDeferred` with `owning_package`, portrait fallback) | `M` (`obj`), `C`, `CA` (`character_owner` / `guild_council`) | Full page | Static HTML character sheet with stat blocks and field profile table. Zero mutation forms. Works without JS. | `character-detail.html` | **Step 5** |
| 12 | `council_characters.html` | R-22 (`GET /v1/council/characters`) · `council_characters_index` in `portal_routes.py` | VM-07 · `CouncilCharacterIndexView` | `ready`, `empty` (cursor pagination N-21/N-64, `CharacterFilters`) | `C`, `CA` (`guild_council`) | Full page | Search form submits via `GET /v1/council/characters`; pagination uses `<a>` hrefs with cursor tokens. Works without JS. | `council-approval.html` (table/filter layout) | **Step 6** |
| 13 | `character_links.html` | R-23 (`GET /v1/council/characters/{id}/links`) · `council_character_links` in `portal_routes.py` | VM-08 · `CharacterLinksView` | `ready` (active ≤25, historical ≤100, character `version`) | `C`, `CA` (`guild_council`) | Full page (pairs with HTMX partial R-24) | Grant form (`POST R-25`), revoke form (`POST R-26`), default form (`POST R-27`) submit via standard POST with CSRF token, version, reason. Manual snowflake entry without JS. | `council-approval.html` (access management panel) | **Step 6** |
| 14 | `identity_search.html` | R-24 (`GET /v1/council/identity-search`) · `council_identity_search` in `portal_routes.py` | VM-09 · `IdentitySearchResultsView` | `ready`, `empty`, `invalid` (candidate list ≤25, OD-42 non-identity banner) | `C`, `CA` (`guild_council`) | HTMX fragment (pairs with R-23) | Dynamic enhancement for R-23. Without JS, operator uses R-23 manual input. Standalone GET answers 200 fragment or 401 unauthenticated. | `council-approval.html` (candidate dropdown/table) | **Step 6** |
| 15 | `identity_migration.html` | R-28 (`GET /v1/council/identity-migration`) · `council_identity_migration` in `portal_routes.py` | VM-10 · `IdentityMigrationView` | `ready`, `empty` (page 50 / max 100, `MigrationTotals` summary) | `C`, `CA` (`guild_council`) | Full page | Proposal table with confirm (`POST R-29`) and reject (`POST R-30`) forms submitting via standard POST with CSRF token, version, reason. Works without JS. | `none` (new visual work; adapts table & summary cards) | **Step 7** |
| 16 | `field_profile.html` | R-31 (`GET /v1/council/field-profile`) · `council_field_profile` in `portal_routes.py` | VM-11 · `FieldProfileView` | `ready` (path classifications ≤500, field classifications ≤500) | `C`, `A`, `CA` (`guild_council` / `platform_administrator`) | Full page | Static HTML classification table with snapshot mode badges and deferred package indicators. Read-only. Works without JS. | `reconciliation.html` (field profile tab) | **Step 7** |
| 17 | `role_capabilities.html` | R-32 (`GET /v1/admin/role-capabilities`) · `admin_role_capabilities` in `portal_routes.py` | VM-12 · `RoleCapabilityView` | `ready` (mappings ≤50, `administrator_scope`, `unratified_count`) | `A`, `CA`, `BG`, `AC` (`platform_administrator`; N-67 restricts `BG`/`AC`) | Full page | Create mapping (`POST R-33`), revoke (`POST R-34`), ratify (`POST R-38`) submit via standard POST with CSRF token and reason. Bootstrap mapping non-revocable. Works without JS. | `none` (new visual work; adapts table & alert cards) | **Step 7** |
| 18 | `account_identities.html` | R-35 (`GET /v1/account/identities`) & R-36 (`GET /v1/account/identities/link/start`) · in `portal_routes.py` | VM-13 · `AccountIdentitiesView` | `ready` (identities ≤10, CSRF token) or `denied` (R-36 response with `additional_provider = "no_additional_provider"`) | Any authenticated caller (`N`, `M`, `C`, `A`, `CA`, `BG`) | Full page | Unlink form (`POST R-37`) submits via standard POST with CSRF token; link start link (`GET R-36`) returns 200 denied view. Works without JS. | `none` (new visual work; adapts identity card list) | **Step 7** |
| 19 | `council_snapshots.html` | R-40 (`GET /v1/council/snapshots`) · `council_snapshots` in `import_routes.py` | VM-14 · `SnapshotListView` | `ready`, `empty` (snapshots ≤50, selectable folders ≤50) | `C`, `A`, `CA` (`guild_council` / `platform_administrator`) | Full page | Folder select form (`POST R-41`, admin only) and preview trigger form (`POST R-42`, Council only) submit via standard POST with CSRF token and nonce. Works without JS. | `reconciliation.html` (snapshot ledger & forms) | **Step 8** |
| 20 | `job_status.html` | R-43 (`GET /v1/council/jobs/{id}`) · `council_job_detail` in `import_routes.py` | VM-15 · `JobStatusView` | `ready`, `queued`, `running`, `completed`, `stale`, `failed`, `cancelled` (`ConfirmScope`, issues ≤30, blocked ≤50) | `C`, `CA` (`guild_council`) | Full page (hosts HTMX container polling R-44) | Displays full job stats; manual refresh updates state; cancel (`POST R-45`) and apply (`POST R-46` with `preview_token` and `nonce`) submit via standard POST. Works without JS. | `reconciliation.html` (progress step sequence & stats) | **Step 9** |
| 21 | `job_status_fragment.html` | R-44 (`GET /v1/council/jobs/{id}/status`) · `council_job_status_fragment` in `import_routes.py` | VM-15 · `JobStatusView` | `ready`, `queued`, `running`, `completed`, `stale`, `failed`, `cancelled` | `C`, `CA` (`guild_council`) | HTMX fragment (polled by R-43 container) | Fragment polled via `hx-get` every N-22 seconds ONLY while `queued` or `running`. Stops dead on terminal states. Answers 401 unauthenticated. | `reconciliation.html` (progress step sequence fragment) | **Step 9** |
| 22 | `import_result.html` | R-47 (`GET /v1/council/imports/{id}`) · `council_import_result` in `import_routes.py` | VM-17 · `ImportResultView` | `ready` (`applied` or `refused`, created/updated counters, issue summary) | `C`, `A`, `CA` (`guild_council` / `platform_administrator`) | Full page | Static HTML immutable import receipt card. Read-only. Works without JS. | `reconciliation.html` (import receipt card) | **Step 10** |
| 23 | `audit_search.html` | R-48 (`GET /v1/audit`) · `audit_search` in `import_routes.py` | VM-18 · `AuditSearchView` | `ready`, `empty` (filters, cursor pagination N-21/N-64, events ≤50) | `C`, `A`, `CA`, `BG`, `AC` (`guild_council` / `platform_administrator`) | Full page (pairs with HTMX partial R-49) | Filter form submits via standard `GET /v1/audit?...`; pagination links use cursor tokens. Works without JS. | `none` (new visual work; adapts filter card & table) | **Step 10** |
| 24 | `audit_results.html` | R-49 (`GET /v1/audit/results`) · `audit_results_fragment` in `import_routes.py` | VM-18 · `AuditSearchView` | `ready`, `empty` | `C`, `A`, `CA`, `BG`, `AC` (`guild_council` / `platform_administrator`) | HTMX fragment (swapped by R-48 form) | Enhanced results table swapped by HTMX with JS. Without JS, R-48 full page handles form GET. Answers 401 unauthenticated. | `none` (new visual work; table layout) | **Step 10** |

---

## 6. Existing-test and planned-test map

### 6.1 Inventory of existing P3.4-relevant tests

The repository contains 50 web test modules under `tests/web/`. Key existing modules relevant to frontend integration include:
- `test_structural_guards.py`: TC-STRUCT-01 (closed 39 routes + 1 static mount M-01), TC-STRUCT-02/TC-VM-01 (frozen slotted view models), TC-VM-02 (text bounds), TC-VM-03 (deferred fields), TC-VM-06 (DeniedView byte-identity fields), TC-STRUCT-05/06 (web config independence & startup refusals).
- `test_static_asset_surface.py`: TC-STATIC-01 to TC-STATIC-07 (M-01 methods, approved root, traversal/dotfile refusals, trusted host, kill switch availability, fingerprint cache policy, no cookie mutation, URL grammar).
- `test_d03_contract_correction.py`: D-03-2 (ConfirmScope 8 fields), D-03-3 (CharacterFilters), D-03-4 (VM-13 CSRF token & synchronizer design), D-03-5 (R-36 200 HTML VM-13 denied), D-03-6 (DeniedView VM-22 & byte-identical 404 responses).
- `test_security_controls.py`: TC-SEC-01 to TC-SEC-13 (synchronizer CSRF, security headers, rate limits, session bounds).
- `test_p3_2_matrix.py`, `test_p3_2_success_cells.py`, `test_p3_3_matrix.py`, `test_p3_3_success_cells.py`: Route authorization matrices and permitted response cells.

### 6.2 Planned tests by execution-plan step

The following new and updated tests will be added across Steps 2–12 (never edited or created during Step 1):

| Step | Focus Area | Planned New / Updated Test Module | Key Assertions & Traceability |
|---|---|---|---|
| **Step 2** | Static Asset Foundation | `tests/web/test_p3_4_static_assets.py` | Static directory inventory; vendored HTMX file integrity, header metadata (version, upstream URL, SHA-256); `tokens.css` 71 design tokens completeness; `styles.css` structure; emblem presence; static cache control headers (TC-STATIC-05). |
| **Step 3** | Shared Shell & Design System | `tests/web/test_p3_4_shell_and_components.py` | `base.html` HTML5 landmarks (single `header`, `nav`, `main`, `footer`); skip link `#main-content` presence and first focusable position; 2-level header & 7-destination nav grid; single `aria-current="page"`; CSRF synchronizer token rendering; zero `\|safe`, zero `hx-on:`, zero inline executable `<script>`; reduced motion CSS and focus rings; shared component partials. |
| **Step 4** | Auth & System-State Views | `tests/web/test_p3_4_auth_and_system_views.py` | `login.html` (VM-01) `ready`/`error`/`degraded`/`failure` rendering & R-03/R-06 links; `emergency.html` (VM-04) recovery grant POST & passkey container; `non_member.html` (VM-02) with correlation UUID; `degraded.html` (VM-03); `denied.html` (VM-22) proving ONLY `state` and `reason` are rendered (no correlation, timestamp, guild, or object ID) and preserving byte-identical 404 responses (TC-OBJ-07); `conflict.html` (VM-19); `validation.html` (VM-21); `error.html` (VM-20); escaping on all inputs. |
| **Step 5** | Member Character Views | `tests/web/test_p3_4_member_views.py` | `my_characters.html` (VM-05) card grid, 16:9 initials fallback, access kind pills, default badge, empty/truncated states, `level=None` -> "not recorded" (TC-VM-05), zero forms; `character_detail.html` (VM-06) stat blocks, profile table, `MigrationDeferred` with owning package and zero controls, zero forms; display name escaping up to 120/240 chars. |
| **Step 6** | Council Character Views | `tests/web/test_p3_4_council_character_views.py` | `council_characters.html` (VM-07) cursor pagination, filter bar, empty state; `character_links.html` (VM-08) active/historical tables, grant (R-25), revoke (R-26), default (R-27) forms rendering ONLY pre-authorized controls with CSRF token, version, reason; `identity_search.html` (VM-09) fragment `ready`/`empty`/`invalid` rendering, OD-42 non-identity warning, 401 unauthenticated. |
| **Step 7** | Identity & Role Administration | `tests/web/test_p3_4_identity_and_role_views.py` | `identity_migration.html` (VM-10) `MigrationTotals` summary, proposal table, confirm (R-29) & reject (R-30) forms; `field_profile.html` (VM-11) classification table & snapshot mode badges; `role_capabilities.html` (VM-12) role mappings table, create (R-33), revoke (R-34), ratify (R-38) forms, bootstrap mapping non-revocable alert, N-67 emergency continuity restrictions; `account_identities.html` (VM-13) linked identities list, current session badge, unlink (R-37) form with CSRF token, R-36 200 denied view. |
| **Step 8** | Snapshots & Preview Entry | `tests/web/test_p3_4_snapshot_views.py` | `council_snapshots.html` (VM-14) snapshot metadata ledger, folder selection form (R-41, rendered only if `can_select_folder=True`), preview trigger form (R-42, rendered only if `can_preview=True`) with nonce and CSRF token. |
| **Step 9** | Job Status & Polling | `tests/web/test_p3_4_job_status_views.py` | `job_status.html` (VM-15) full page states (`queued`, `running`, `completed`, `stale`, `failed`, `cancelled`), stats summary, issues ≤30, blocked ≤50, cancel form (R-45), apply form (R-46) with `preview_token` and `nonce`; `job_status_fragment.html` (VM-15) fragment emitting `hx-get`/`hx-trigger` ONLY while `queued` or `running`, stopping dead on terminal states, N-22 floor poll interval, 401 unauthenticated. |
| **Step 10** | Import Result & Audit Views | `tests/web/test_p3_4_import_and_audit_views.py` | `import_result.html` (VM-17) applied/refused receipt card, created/updated counters, closed `ISSUE_CODES` summary; `audit_search.html` (VM-18) 5-filter search form, cursor pagination, immutability notice; `audit_results.html` (VM-18) fragment with structured before/after triples, 401 unauthenticated. |
| **Step 11** | Whole-Corpus Accessibility | `tests/web/test_p3_4_accessibility.py` | TC-UI-01 through TC-UI-05; **TC-UI-06** (new structural test asserting 0 template imports/links to `design-prototype/`); WCAG 2.2 AA contrast matrix verification across all tokens/components; 100% no-JavaScript completion across essential flows. |
| **Step 12** | Whole-Corpus Security | `tests/web/test_p3_4_security_and_escaping.py` | TC-SEC-05 exact response headers (CSP N-26, `nosniff`, `Referrer-Policy`, COOP, CORP, `Permissions-Policy`, `Cache-Control: no-store` on auth responses); TC-SEC-08 Jinja autoescaping on all extensions & 0 `\|safe`; TC-SEC-09 hostile escaping parametrization (XSS, template injection, 10k chars, RTL, NFC/NFD); TC-SEC-10 zero `hx-on:`; TC-SEC-11 zero view-model fields in `<script>` context; 0 inline script/CDN/remote font references; byte-identical 404 denial bodies; TC-STRUCT-01 and TC-STRUCT-02 green. |

---

## 7. Later-step overlap analysis

Analysis of pre-existing dirty-tree changes versus planned P3.4 allowlists:

### 7.1 Dirty-tree paths overlapping P3.4 allowlists

| Working Tree Path | Current Git Status | Ownership & Characterization | P3.4 Step Overlap | P3.4 Handling Rule |
|---|---|---|---|---|
| `adapters/web/templates/conflict.html` | `M` (modified) | Pre-existing minimal contract template from P3.1/P3.2/P3.3 backend delivery. | **Step 4** | Will be replaced in Step 4 with production-styled 409 conflict rendering. |
| `adapters/web/templates/audit_results.html` | `??` (untracked) | Pre-existing minimal fragment template from P3.3 backend delivery. | **Step 10** | Will be replaced in Step 10 with production-styled audit results table fragment. |
| `adapters/web/templates/audit_search.html` | `??` (untracked) | Pre-existing minimal contract template from P3.3 backend delivery. | **Step 10** | Will be replaced in Step 10 with production-styled audit search full page. |
| `adapters/web/templates/council_snapshots.html` | `??` (untracked) | Pre-existing minimal contract template from P3.3 backend delivery. | **Step 8** | Will be replaced in Step 8 with production-styled snapshot list full page. |
| `adapters/web/templates/import_result.html` | `??` (untracked) | Pre-existing minimal contract template from P3.3 backend delivery. | **Step 10** | Will be replaced in Step 10 with production-styled import receipt full page. |
| `adapters/web/templates/job_status.html` | `??` (untracked) | Pre-existing minimal contract template from P3.3 backend delivery. | **Step 9** | Will be replaced in Step 9 with production-styled job status full page. |
| `adapters/web/templates/job_status_fragment.html` | `??` (untracked) | Pre-existing minimal fragment template from P3.3 backend delivery. | **Step 9** | Will be replaced in Step 9 with production-styled job polling fragment. |
| `adapters/web/static/` | `??` (untracked directory) | Contains pre-existing `.gitkeep` from accepted D-03 delivery (`C-P3.4-A`). | **Step 2** | Production CSS, vendored HTMX, and emblem will be added under this directory in Step 2. |

### 7.2 Non-overlapping dirty-tree paths (strictly out of bounds for P3.4)

All other modified and untracked files in the working tree belong to backend implementations, migrations, database adapters, application services, or project management records (e.g. `adapters/web/app.py`, `portal_routes.py`, `import_routes.py`, `static_assets.py`, `composition.py`, `middleware.py`, `repositories.py`, `application/`, `migrations/`, `docs/contracts/`, `docs/project-management/`, `tests/web/test_p3_3_*.py`, `tests/web/test_d03_contract_correction.py`, `tests/web/test_static_asset_surface.py`).
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

### 8.2 Anticipated Step 2 assets

The following production assets will be introduced in Step 2 without prematurely locking final fingerprinted filenames:
1. `adapters/web/static/css/tokens.css` (or fingerprinted equivalent): Reimplementation of all 71 accepted CSS custom properties / design tokens from `design-prototype/css/tokens.css`.
2. `adapters/web/static/css/styles.css` (or fingerprinted equivalent): Production layout primitives (`.table-container`, `.card-grid`, `.fb-blade-divider`, 2-level header, focus rings, reduced-motion overrides).
3. `adapters/web/static/js/htmx.min.js` (or fingerprinted equivalent): Single reviewed vendored HTMX library (v1.9.10+) with version, upstream URL, and SHA-256 header comment.
4. `adapters/web/static/assets/freedom-blades-token.png` (or fingerprinted equivalent): Guild emblem token image served same-origin.
5. Static asset manifest / integrity metadata mapping.

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
$ ./venv-web/bin/pytest tests/web/test_structural_guards.py tests/web/test_static_asset_surface.py -m "not database" -v
```
- **Exit Code:** `0`
- **Output Summary:**
```text
======================== 58 passed, 64 skipped in 0.25s ========================
```
*(64 tests requiring PostgreSQL skipped as expected for non-database baseline execution)*

Key passing structural assertions:
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

---

## 10. Checks not run and why

The following check classes were deliberately not run during Step 1, with technical justification:

1. **Full PostgreSQL Database Test Suites (`tests/test_database_schema.py`, `tests/web/test_p3_2_*.py`, `tests/web/test_p3_3_*.py`):**
   *Why Not Run:* Step 1 is strictly non-mutating and non-database. Running database suites requires an active `TEST_DATABASE_URL` and executes Alembic database migrations.
2. **Headless Browser Test Suites (Playwright):**
   *Why Not Run:* Automated browser suites require production templates, static CSS, and vendored HTMX assets, which will be implemented in Steps 2–11. Installing new browser binaries without authorization is prohibited.
3. **Real-Device Physical Hardware Inspection (TC-UI-08):**
   *Why Not Run:* Reserved exclusively for Acceptance Authority Peter Duscha on maintainer physical hardware. Cannot be claimed or simulated by agent inspection.
4. **Assistive Technology Screen Reader Audio Traversal (TC-UI-09):**
   *Why Not Run:* Reserved exclusively for Peter Duscha / live maintainer assistive technology evaluation. Cannot be claimed or simulated by agent inspection.
5. **Staging Environment Deployments & Network Calls:**
   *Why Not Run:* Staging exposure is not authorized (I-06 remains open); no live Discord OAuth, Google Sheets, or Foundry VTT endpoints may be contacted.

---

## 11. Discrepancies, questions and residual risks

### 11.1 Discrepancies and contract alignment
- **Zero Contract-Implementation Discrepancies:** All six items of the D-03 backend contract correction (`C-P3.4-A`) have been implemented in backend code and verified:
  1. D-03-1: M-01 `/static/` surface implemented in `adapters/web/static_assets.py` and `composition.py`.
  2. D-03-2: `ConfirmScope` 8-field definition implemented in `application/web/view_models.py`.
  3. D-03-3: `CharacterFilters` definition implemented in `application/web/view_models.py`.
  4. D-03-4: `csrf_token` added to `AccountIdentitiesView` (VM-13).
  5. D-03-5: R-36 implemented as 200 HTML returning VM-13 in `denied` state (`additional_provider = "no_additional_provider"`).
  6. D-03-6: `DeniedView` (VM-22) implemented with only `state` and `reason`, preserving byte-identical 404 responses.
- **Visual Freeze Intact:** 14/14 files match `docs/review/phase-3-visual-freeze-manifest.sha256`.
- **Closed Route & View-Model Sets:** Exactly 39 routes and 22 view models (VM-01..VM-22).

### 11.2 Open questions for maintainer review
- No open technical questions block Step 2. Four screens lacking prototype pages (VM-10, VM-12, VM-13, VM-18) are scheduled for visual construction in Steps 7 and 10 and visual acceptance by Peter at P3.G4.

### 11.3 Residual risks
- **RR-01 (Static Asset Delivery):** Ensuring fingerprinted CSS and vendored HTMX cache policies match deployment expectations without broken asset links under reverse proxy. Mitigated by `test_static_asset_surface.py` and M-01 contract.
- **RR-02 (Assistive Technology & Focus Management):** Ensuring dynamic HTMX swaps preserve focus and do not flood live regions. Mitigated by progressive enhancement and manual AT reservation for Peter (TC-UI-09).
- **RR-03 (Visual Acceptance on New Screens):** Four screens (VM-10, VM-12, VM-13, VM-18) extend the visual system without prior prototype pages. Mitigated by explicit P3.G4 visual review gate.

---

## 12. Step 1 checkpoint verdict

### Verdict: **`READY FOR STEP 2`**

### Reasons:
1. **Visual Freeze Verified:** `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` exited `0` with 14/14 files OK.
2. **Template & Static Root Inventory Complete:** All 24 production templates in `adapters/web/templates/` and `adapters/web/static/.gitkeep` inventoried with exact SHA-256 digests.
3. **Closed Work Map Established:** Complete 24-row matrix mapping templates to route handlers, view models, `PageState` values, capability classes, full-page/fragment roles, no-JS flows, prototype references, and execution-plan steps.
4. **Static Surface Contract M-01 Verified:** Public `/static/` contract, grammar rules, and cache policies verified against `adapters/web/static_assets.py` and passing pytest structural guards.
5. **Dirty-Tree Baseline Accounted For:** Pre-existing backend changes separated and documented; zero unrelated files modified.
6. **No Discrepancies or Blockers:** Backend contracts, route inventory (39), view-model inventory (22), and structural guards match 100%.
7. **Sole Write Constraint Satisfied:** Only `docs/review/phase-3-p3-4-gemini-baseline.md` created.

---

*Step 1 complete. In accordance with prompt instructions, Gemini stops here. Step 2 (static asset foundation) will begin only upon maintainer review and release of the Step 2 prompt.*
