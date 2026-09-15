# Phase 3.4 Submission — Web Platform Frontend Integration & Verification

**Date:** 2026-08-23  
**Package:** Phase 3, Milestone P3.4 (Production Frontend Integration)  
**Implementer:** Gemini (Frontend Integrator role)  
**Acceptance Authority:** Peter Duscha  
**Independent Reviewers:** Codex (Implementation Review & Distinct Security Review)  
**Current Gate:** Stop Gate **P3.G4 is OPEN**; Step 13 Verification is **SUBMITTED FOR INDEPENDENT REVIEW**.

---

## 1. Authority, Stop Conditions, and Gate State

1. **Starting Authority & Remediation Authorization:**
   - On 2026-08-20, Peter Duscha accepted the corrected D-03 backend route/view-model contracts (`C-P3.4-C`) and released the P3.4 master implementation prompt (`docs/review/phase-3-p3-4-gemini-implementation-prompt.md`).
   - Following step-by-step review checkpoints 1 through 10, Peter accepted Step 10 on 2026-08-22 (`docs/review/phase-3-p3-4-step-10-final-independent-review-and-acceptance.md`).
   - Peter authorized and released Step 11 accessibility/responsive pass (`docs/review/phase-3-p3-4-step-11-accessibility-handoff.md`), followed by Step 11.2 and Step 11.3 verification (`docs/review/phase-3-p3-4-step-11-3-final-verification-handoff.md`).
   - Peter authorized and released Step 12 security and progressive enhancement pass (`docs/review/phase-3-p3-4-step-12-security-and-progressive-enhancement-handoff.md`). Step 12 remains formally accepted.
   - On 2026-08-23, Peter released Step 13 complete verification under `docs/review/Handover information`. Codex independent review identified findings R13-01 through R13-09 followed by evidence integrity findings R13-10 through R13-13. Peter authorized bounded, **documentation-only** Step 13 remediation in response.
2. **Current Gate Boundary:**
   - **Gate P3.G4 remains OPEN.**
   - Milestone P3.5 remains **HELD**.
   - RAID items **I-06** and **A-05** remain **OPEN**.
   - This submission is a **verification and documentation handoff only**. Gemini makes zero self-acceptance decisions and claims zero deployment, staging, or production exposure authorization.
3. **Execution Environment & Isolation:**
   - All verification was executed strictly in `/opt/discord-bots/freedom-bot` using the disposable PostgreSQL Unix-domain socket `TEST_DATABASE_URL=postgresql+psycopg:///freedom_test`.
   - Zero live Discord APIs, Google Sheets APIs, Foundry VTT instances, production databases, external network endpoints, or staging environments were contacted.
   - Zero production secrets, OAuth credentials, bot tokens, or `.env` files were accessed or inspected. Zero real player data or live guild identifiers appear anywhere in this package.
   - The pre-existing uncommitted worktree state and pre-existing stashes were preserved intact without reset, checkout, rebase, or commit.

---

## 2. Scope, Allowlist, and Dirty-Tree Preservation

Under the strict Step 13 remediation instructions (`docs/review/Handover information`), only three repository files were permitted to be created or edited:
1. `docs/review/phase-3-p3-4-submission.md` (Created / Remediated)
2. `docs/project-management/status.md` (Updated)
3. `docs/project-management/change-log.md` (Updated)

All production source code, tests, fixtures, templates, stylesheets, images, vendored scripts, manifests, contracts, and migrations remained strictly frozen.

### Literal Starting `git status --short` (Pre-Remediation Baseline)
```text
 M adapters/web/app.py
 M adapters/web/middleware.py
 M adapters/web/static/asset-integrity.sha256
RM adapters/web/static/css/freedom-blades.b0a1f3305683.css -> adapters/web/static/css/freedom-blades.58a9b9eed003.css
 M adapters/web/templates/audit_results.html
 M adapters/web/templates/audit_search.html
 M adapters/web/templates/base.html
 M adapters/web/templates/character_links.html
 M adapters/web/templates/council_characters.html
 M adapters/web/templates/council_snapshots.html
 M adapters/web/templates/error.html
 M adapters/web/templates/import_result.html
 M adapters/web/templates/includes/header.html
 M adapters/web/templates/job_status_fragment.html
 M adapters/web/templates/validation.html
 M application/web/audit_search.py
 M application/web/view_models.py
 M docs/contracts/phase-3-view-model-contract.md
 M docs/project-management/change-log.md
 M docs/project-management/status.md
 M "docs/review/Handover information"
 M tests/web/test_identity_migration_command.py
 M tests/web/test_oauth_refusal_audit.py
 M tests/web/test_p3_3_audit_search.py
 M tests/web/test_p3_3_disclosure_and_bounds.py
 M tests/web/test_p3_4_auth_and_system_views.py
 M tests/web/test_p3_4_council_character_views.py
 M tests/web/test_p3_4_identity_and_role_views.py
 M tests/web/test_p3_4_job_status_views.py
 M tests/web/test_p3_4_member_views.py
 M tests/web/test_p3_4_shell_and_components.py
 M tests/web/test_p3_4_snapshot_views.py
 M tests/web/test_security_controls.py
 M tests/web/test_static_asset_surface.py
?? docs/review/phase-3-p3-4-step-10-final-independent-review-and-acceptance.md
?? docs/review/phase-3-p3-4-step-11-1-scope-integrity-handoff.md
?? docs/review/phase-3-p3-4-step-11-2-focused-evidence-handoff.md
?? docs/review/phase-3-p3-4-step-11-3-final-verification-handoff.md
?? docs/review/phase-3-p3-4-step-11-accessibility-handoff.md
?? docs/review/phase-3-p3-4-step-12-security-and-progressive-enhancement-handoff.md
?? docs/review/phase-3-p3-4-submission.md
?? tests/web/no_js_helpers.py
?? tests/web/template_digests.py
?? tests/web/test_p3_4_accessibility.py
?? tests/web/test_p3_4_import_and_audit_views.py
?? tests/web/test_p3_4_security_and_escaping.py
```

---

## 3. Changed-File Inventory & SHA-256 Digest Registry

### A. Allowlisted Repository Files Modified / Remediated by Step 13
The pre-remediation baseline SHA-256 digests observed by Codex and verified at the start of this remediation are recorded below. To avoid self-referential digest invalidation, the final byte-for-byte SHA-256 digest of this submission document is computed externally and recorded in the final Gemini walkthrough artifact outside the repository after all repository edits are complete.

| Repository File Path | Action | Pre-Remediation Baseline SHA-256 | Final Digest Location |
|---|---|---|---|
| `docs/review/phase-3-p3-4-submission.md` | Remediated | `ff42a69351111ece1f29cf668f13492d5fa98aca4fa386f6a9191964be069f1a` | Recorded externally in Gemini walkthrough |
| `docs/project-management/status.md` | Modified | `6972ff387c83b14010e8c7d0d623878dc590709a50bac73dc90a85439b3f522c` | Recorded externally in Gemini walkthrough |
| `docs/project-management/change-log.md` | Modified | `545a5ace88012fb04577e6aaf684710b39798a1540f94a0532a67a65a5cc66e0` | Recorded externally in Gemini walkthrough |

### B. Complete Candidate Inventory for Phase 3.4
**Inclusion Rule:** The live P3.4 presentation candidate inventory contains the production files and direct test/support files created or modified by the accepted P3.4 integration steps, plus unchanged templates/static assets deliberately carried as the complete 26-template and three-asset presentation corpus. Accepted pre-existing backend route/service modules (`adapters/web/portal_routes.py`, `adapters/web/import_routes.py`, `adapters/web/static_assets.py`, `adapters/web/composition.py`) are referenced by traceability but are not claimed as P3.4-authored or P3.4-modified candidate artifacts.

The table below records **53 live candidate artifacts plus 1 rename-provenance row = 54 evidence rows** with candidate role, current Git worktree state, and exact SHA-256 digest:

| File Path | Candidate Role | Current Git State | SHA-256 Digest |
|---|---|---|---|
| `adapters/web/app.py` | Production Web Application & Route Handlers | Modified | `b219f3f48ef3f83f894c74e4d01336c53fb5bc21f4bcc6e6311ed0177a99e75a` |
| `adapters/web/middleware.py` | Security & Middleware Layer | Modified | `7fee13273f1036d3f12672f39e2d623e1ee475d7be80c6c084b7f1faf4d3771a` |
| `application/web/audit_search.py` | Audit Search Application Service | Modified | `36ea24a103b63c763c36deb68074e413e5981fc9951373bebef506ee7794f9f4` |
| `application/web/view_models.py` | Typed Frozen View Models (`vm-1`) | Modified | `f26ffbcbeac1fdd768db007115f73e51114cb1b5fd3013ed00f8725eb7f9907a` |
| `docs/contracts/phase-3-view-model-contract.md` | Accepted View Model Contract | Modified | `67c1e0b993639a7ed9d8f7156f95762b8a049645bb72db0a4b389578b420fd28` |
| `adapters/web/static/asset-integrity.sha256` | Production Static Asset Integrity Manifest | Modified | `299a8a26ec64e862677e61e46cb432c632fc3d9dc48c29f0648dc03b9f31bf2b` |
| `adapters/web/static/css/freedom-blades.58a9b9eed003.css` | Production Design System Stylesheet | Renamed (New) | `58a9b9eed003c44b0b4e63d25910ecd704cdac03b0dcea6d2e105d63b8756649` |
| `adapters/web/static/css/freedom-blades.b0a1f3305683.css` | Former Production Stylesheet (Renamed to 58a9b9eed003) | Renamed (Old) | `absent (renamed)` |
| `adapters/web/static/images/freedom-blades-token.eab0d13128f5.png` | Production Emblem Token Asset | Unmodified | `eab0d13128f55b7a367ce9e3ba88a2bad967e37768f7e28d9728186d9d322371` |
| `adapters/web/static/vendor/htmx-2.0.10.71ea67185bfa.min.js` | Vendored HTMX 2.0.10 JavaScript Asset | Unmodified | `71ea67185bfa8c98c39d31717c6fce5d852370fcdfd129db4543774d3145c0de` |
| `adapters/web/templates/base.html` | Shared Shell Base Template | Modified | `818f0ff60eb4ad7a9d6c5ac0720ccc7c3a3688f908a5ceae3f44ead5bcfba31e` |
| `adapters/web/templates/includes/header.html` | Header Navigation Include | Modified | `bf2d9a81ce9614c43461a7cedb0db9d2c7e0ba5050e14a7cda8e46f02d426857` |
| `adapters/web/templates/includes/footer.html` | Footer Include | Unmodified | `2f1068b436a38a7ef79580aec4b55ed23dcaa5a3b827596509caa000ed72f7c3` |
| `adapters/web/templates/login.html` | Login View Template (VM-01) | Unmodified | `eafd7635be0b6b8dfb7d60df7a827a49863b5b12bb1cdc0e49ddbd4c0f7d5e3b` |
| `adapters/web/templates/emergency.html` | Emergency Recovery Template (VM-04) | Unmodified | `0eec75c17bb6ea602fabc7aace0aaf1453e70fd102e61da5298759e094980a99` |
| `adapters/web/templates/non_member.html` | Non-Member View Template (VM-02) | Unmodified | `de43a127d11f77bfccfb515fa93e3a2ef9373b123c880c1290dcedc1f1721f02` |
| `adapters/web/templates/degraded.html` | Degraded Service Template (VM-03) | Unmodified | `98f3ac888788d24e173fb4a497e0b138c23987b459d29d37b4131c9bbd211915` |
| `adapters/web/templates/denied.html` | Safe Denial View Template (VM-22) | Unmodified | `197913db5909d6d9801f599b0a0b2eed47b6384f4e5bd3e38de6e9ae6c686c20` |
| `adapters/web/templates/conflict.html` | Conflict View Template (VM-19) | Unmodified | `1dda40f2e43212631fba5001e4982748fc5a090b0a32a6be57965daae4805648` |
| `adapters/web/templates/validation.html` | Validation Refusal Template (VM-21) | Modified | `3f71db358dbd5a83bd85b520fe3541b93d5a04f6cd1db2c4047a9a3bc9b18c39` |
| `adapters/web/templates/error.html` | Safe 500 Error Template (VM-20) | Modified | `269e72e427a7166ebf22ca12f46827c2ee30671a2f48fdde9a504ca87f1c4f33` |
| `adapters/web/templates/my_characters.html` | Member Characters Template (VM-05) | Unmodified | `3705fbcd3e0803b2190746102cf6a67e20aa607432de128e3127a5a8987ce042` |
| `adapters/web/templates/character_detail.html` | Character Detail Template (VM-06) | Unmodified | `7524e43e0e2ee814b5c8b65365f4e0d72bcb9c1e42e4087ea927e3934c0c9890` |
| `adapters/web/templates/council_characters.html` | Council Characters Index Template (VM-07) | Modified | `671e8308f5f746941bcd875cb66ccc368e8c4a18dc5738e8f5411e6f62be5c87` |
| `adapters/web/templates/identity_search.html` | Identity Search Partial Template (VM-09) | Unmodified | `36978ca19d5366188ae42892111cb5425ece1b6e2355710a32b71e2c6ef1e394` |
| `adapters/web/templates/character_links.html` | Character Links Template (VM-08) | Modified | `78fdaac512f3bddc2073e20b03fc610f8afb0243db5907e8c1cadf904c5bed49` |
| `adapters/web/templates/identity_migration.html` | Identity Migration Template (VM-10) | Unmodified | `66f3669661c40f2a73d250122c35e0f8af397d6f8bd94a4571402e7a8a63134b` |
| `adapters/web/templates/field_profile.html` | Field Profile Template (VM-11) | Unmodified | `06277334db018cd82e313af0556a35e658c86841e06602a7bd65d0edde15f703` |
| `adapters/web/templates/role_capabilities.html` | Role Capabilities Template (VM-12) | Unmodified | `e297c26dc326a2a28c9439948fcd781c29b12d3cda74911d9f747727d760613a` |
| `adapters/web/templates/account_identities.html` | Account Identities Template (VM-13) | Unmodified | `5f458b6fe335d34b7ba400d4f7c4c0dcbcceadabd613bfbd5c25890af37f1287` |
| `adapters/web/templates/council_snapshots.html` | Council Snapshots Template (VM-14) | Modified | `4aca2c0e057f94a061e10af1640dcae5ec43ecb66765db8ff629a3f616a00229` |
| `adapters/web/templates/job_status.html` | Job Status Page Template (VM-15) | Unmodified | `9a7a62892f9983ccd1a359f213f4feab0f85b1a084dccdabdbb0cb68a380deb3` |
| `adapters/web/templates/job_status_fragment.html` | Job Status Polling Fragment Template (VM-15) | Modified | `a2e5c106ac44c4f38c203286918219fec61858d9909e2a851a5a2eb6fb0096e3` |
| `adapters/web/templates/import_result.html` | Import Result Template (VM-17) | Modified | `15735d60fdb5a5b3c8435a7ee389af7e6ec027c2f386cdee55f3d109bd42c86e` |
| `adapters/web/templates/audit_search.html` | Audit Search Page Template (VM-18) | Modified | `6453c99cd068918be029d7f592b8a934654b11f05e324400ef080d83e878ec23` |
| `adapters/web/templates/audit_results.html` | Audit Search Results Fragment Template (VM-18) | Modified | `42883ac57fd38b342cb4471c46f001b549818e07faa7c772d8f2a2df09ba0e38` |
| `tests/web/test_identity_migration_command.py` | Identity Migration Command Suite | Modified | `a41f5d94109ad363a6c05b7698e240d81b129268cef51d053299fba7807221a4` |
| `tests/web/test_oauth_refusal_audit.py` | OAuth Refusal & Audit Error Suite | Modified | `60cdc27d71fba839fbabbfa81badcb3d0e0f1a0562b3787e63b9c61627833798` |
| `tests/web/test_p3_3_audit_search.py` | Audit Search Backend Suite | Modified | `71fc56d6c3117121a22a4bbf08d0bf301c9cb0105b136911ad90c5f4026ddfce` |
| `tests/web/test_p3_3_disclosure_and_bounds.py` | Disclosure & Field Bounds Suite | Modified | `7fcf701e41296d0ad8020892e54ac43b069c3a0fe74d7bc1e378b90b816ccd22` |
| `tests/web/test_p3_4_accessibility.py` | P3.4 Accessibility & Contrast Suite | Untracked | `4cd3e0c3e6ad24fe52169552a8bffe2f4fe091c8f96bc09616112ca4be91097a` |
| `tests/web/test_p3_4_auth_and_system_views.py` | Auth & System State Views Suite | Modified | `ad2f6ba17aca5f1646017f67e67a79d65aae4536b120330bd485f01390d0c699` |
| `tests/web/test_p3_4_council_character_views.py` | Council Character Views Suite | Modified | `c893ee6c385b663375caee959ef532baf4c60fa52daad7b950195a2e96dd88e1` |
| `tests/web/test_p3_4_identity_and_role_views.py` | Identity & Role Capability Views Suite | Modified | `186e98641073716aafc130ef40faeebabce0eff6418b3d5a5cf4f20a1619e3b8` |
| `tests/web/test_p3_4_import_and_audit_views.py` | Import & Audit Search Views Suite | Untracked | `ea769375c6e965dbaa98c20f3b227ec8793873e4f306bef0f114e9cc20c1cddd` |
| `tests/web/test_p3_4_job_status_views.py` | Job Status & Polling Views Suite | Modified | `0d23252d3f75e270168769eb3ffa732a74c037f75b04feadfe94f544a80ac75f` |
| `tests/web/test_p3_4_member_views.py` | Member Characters Views Suite | Modified | `113b027ce0decaef3f0fe42a59ba35d5d11230ad1c7e33d616c3301f51bcc6a0` |
| `tests/web/test_p3_4_security_and_escaping.py` | Security, Escaping & Inertness Suite | Untracked | `ca9966f9ac60cc350eb253898adce7c9b7e3d7a90023d0bf2b4101e4df32dd18` |
| `tests/web/test_p3_4_shell_and_components.py` | Shell & Shared Component Suite | Modified | `1d484c038e52e87ad6577b1e68f44efcf75631e20e5d17a54d00dd60daf2c72c` |
| `tests/web/test_p3_4_snapshot_views.py` | Council Snapshot Views Suite | Modified | `99ebe60abc0b408dbc74908615b2a87cf462f470d9647f3582cc4e109b7d43b6` |
| `tests/web/test_security_controls.py` | Web Security Controls Suite | Modified | `46a7c26bde933ca76ae40f8760d11c0fc4a896736efd239380ed672d7808dedb` |
| `tests/web/test_static_asset_surface.py` | Static Asset Surface Suite | Modified | `5ad617a4893069aa5b731a7b2f29f9e3062c753f51c7b7855ca4ce553598ec74` |
| `tests/web/no_js_helpers.py` | Test Helper: No-JS Validator & Utilities | Untracked | `5b6b2fe9ac781b894a5de06b028026eeb7fda629173cbf67688d1f17052a5d21` |
| `tests/web/template_digests.py` | Test Helper: Template Digest Registry | Untracked | `ad4056d8d6c8a4235e0689d29b02609f848874473e271ff28c6d1eed0c2765c0` |

---

## 4. Complete Screen Matrix (All 26 Production Templates & Fragments)

Reconstructed mechanically from `docs/contracts/phase-3-route-authorization-contract.md`, `docs/contracts/phase-3-view-model-contract.md`, production route handlers in `adapters/web/app.py`, `adapters/web/portal_routes.py`, and `adapters/web/import_routes.py`, and actual template render sites. Exactly 26 production templates exist under `adapters/web/templates/` and exactly 26 unique rows are detailed below:

| Template Name | Route & HTTP Method | View Model Class | Auth / Capability Boundary | Applicable States Handled | No-JavaScript Behavior | Supporting Test Symbol(s) |
|---|---|---|---|---|---|---|
| `base.html` | Shared shell for all full pages | Context inherited from page VM (no standalone class) | Inherited from page | `ready`, `empty`, `loading`, `stale`, `denied`, `invalid`, `error` | Full semantic landmarks (`<header>`, `<nav>`, `<main id="main-content">`, `<footer>`), skip link; 0 script dependency | `tests/web/test_p3_4_shell_and_components.py::test_landmark_order_and_skip_link_positive`, `tests/web/test_p3_4_accessibility.py::test_base_template_landmarks_and_skip_link_order` |
| `includes/header.html` | Include for `base.html` | Context inherited from page VM | Inherited from page | Dynamic 2-tier nav: anonymous vs member vs Council vs Admin | Semantic `<nav>` with static anchor links | `tests/web/test_p3_4_shell_and_components.py::test_aria_current_page_selection_positive`, `tests/web/test_p3_4_accessibility.py::test_header_navigation_aria_current_page_rendering` |
| `includes/footer.html` | Include for `base.html` | Context inherited from page VM | Inherited from page | Platform version badge, copyright notice | Static semantic `<footer>` | `tests/web/test_p3_4_shell_and_components.py::test_shared_includes_preservation_positive` |
| `login.html` | `GET /v1/login` (R-02) | `LoginPageView` (VM-01) | Anonymous / Public (`U`, `N`, `M`, `C`, `A`, `CA`, `BG`) | `ready` (Discord OAuth start link R-03, emergency link R-06, degraded banner if Discord degraded) | Native `<a href="/v1/auth/discord/start">` anchor links | `tests/web/test_p3_4_auth_and_system_views.py::test_login_rendering_all_branches` |
| `emergency.html` | `GET /v1/auth/emergency` (R-06), with recovery form submitting to `POST /v1/auth/emergency/recovery` (R-09) | `EmergencyLoginView` (VM-04) | Anonymous / Break-Glass entry (`U`, `N`, `M`, `C`, `A`, `CA`, `BG`) | `ready` (WebAuthn trigger JS, recovery grant form R-09), `invalid` (failure reason mapped to closed message) | Native HTML `<form method="post" action="/v1/auth/emergency/recovery">` with recovery token input | `tests/web/test_p3_4_auth_and_system_views.py::test_emergency_access_rendering_all_combinations` |
| `non_member.html` | Rendered on `403` non-member rejection from `GET /auth/discord/callback` (R-04) or protected route caller state `N` | `NonMemberView` (VM-02) | Non-member holding valid Discord OAuth identity (`N`) | `denied` (Guild join instructions, checked_at instant, correlation UUID) | Static informational page with return link | `tests/web/test_p3_4_auth_and_system_views.py::test_non_member_rendering` |
| `degraded.html` | Rendered on `503` when provider/subsystem outage occurs (e.g., N-10 grace exhausted or Discord unreachable during OAuth) | `ServiceDegradedView` (VM-03) | Any caller during degraded subsystem state | `degraded` (`data-state="degraded"`, degraded provider name, safe outage explanation) | Static informational page | `tests/web/test_p3_4_auth_and_system_views.py::test_degraded_rendering` |
| `denied.html` | Rendered on generic safe denials: `401 Unauthorized`, `403 Forbidden`, `404 Not Found` (object-level denial / absent object) across all protected routes | `DeniedView` (VM-22) | Any caller encountering access denial | `denied` (`data-state="denied"`, closed-vocabulary `reason.category`). Zero leaked correlation UUID, timestamp, guild name, or stack traces | Static error layout with return navigation link | `tests/web/test_p3_4_auth_and_system_views.py::test_denied_rendering_and_minimization`, `tests/web/test_p3_4_auth_and_system_views.py::test_vm22_http_absent_and_inaccessible_byte_identity` |
| `conflict.html` | Rendered on `409 Conflict` across optimistic concurrency / collision boundaries | `ConflictView` (VM-19) | Authenticated callers encountering stale version / race collision | `invalid` / `conflict` (Specific conflict message and return link) | Static notice with navigation return link | `tests/web/test_p3_4_auth_and_system_views.py::test_conflict_rendering_and_conditional_scope` |
| `validation.html` | Rendered on `422 Unprocessable Entity` form validation refusals across mutation routes | `ValidationView` (VM-21) | Any caller submitting invalid payload | `invalid` (`data-state="invalid"`, list of `FieldError` with field name and closed error code) | Re-rendered form or structured error summary with back navigation | `tests/web/test_p3_4_auth_and_system_views.py::test_validation_rendering_and_anchors` |
| `error.html` | Rendered on `500 Internal Server Error` across all application routes | `SafeErrorView` (VM-20) | Any caller encountering unexpected internal failure | `error` (`data-state="error"`, exactly one canonical lowercase hyphenated UUID correlation ID in `.reference-code`, zero exception tracebacks/SQL/internal paths) | Static failure notice with reference code | `tests/web/test_p3_4_auth_and_system_views.py::test_error_rendering`, `tests/web/test_oauth_refusal_audit.py::test_correlation_of_semantics_and_falsification` |
| `my_characters.html` | `GET /v1/characters` (R-20) | `MyCharactersView` (VM-05) | Member (`M`, `C`, `CA`) | `ready` (Character cards list), `empty` (First-class empty state guiding user to Council for link), `truncated` (True if linked characters exceed 50) | Native `<a href="/v1/characters/{id}">` links | `tests/web/test_p3_4_member_views.py::test_my_characters_ready_state_rendering`, `tests/web/test_p3_4_member_views.py::test_my_characters_empty_state_rendering` |
| `character_detail.html` | `GET /v1/characters/{character_id}` (R-21) | `CharacterDetailView` (VM-06) | Member Owner (`M` obj, `C`, `CA`) | `ready` (Character facts, stats, currencies, skills, inventory, bastions, `MigrationDeferred` badges for deferred packages), `empty` (Defaults for unassigned fields). Zero mutation controls | Static semantic article layout with tabs/sections | `tests/web/test_p3_4_member_views.py::test_character_detail_populated_rendering`, `tests/web/test_p3_4_member_views.py::test_character_detail_null_level_and_council_access_and_unmapped_provenance` |
| `council_characters.html` | `GET /v1/council/characters` (R-22) | `CouncilCharacterIndexView` (VM-07) | Guild Council (`C`, `CA`) | `ready` (Searchable character index table with name, player, active links count, default status), `empty` (No matches for search filter `CharacterFilters`) | Native HTML `<form method="get" action="/v1/council/characters">` with query input `q` | `tests/web/test_p3_4_council_character_views.py::test_vm07_council_character_index_ready_and_filter`, `tests/web/test_p3_4_council_character_views.py::test_vm07_council_character_index_empty` |
| `identity_search.html` | `GET /v1/council/identity-search` (R-24 fragment) | `IdentitySearchResultsView` (VM-09) | Guild Council (`C`, `CA`) | `ready` (List of candidate Discord identities with username, global name, canonical decimal snowflake in `code[data-field="subject"]`), `empty` (No candidates found or query < 2 chars) | Standalone partial HTML fragment rendered on direct GET | `tests/web/test_p3_4_council_character_views.py::test_vm09_identity_search_fragment`, `tests/web/test_p3_4_council_character_views.py::test_vm09_identity_search_empty_and_invalid` |
| `character_links.html` | `GET /v1/council/characters/{character_id}/links` (R-23), `POST /v1/council/characters/{character_id}/links` (R-25 grant), `POST /v1/council/characters/{character_id}/links/{access_id}/revoke` (R-26 revoke), `POST /v1/council/characters/{character_id}/links/{access_id}/default` (R-27 set default) | `CharacterLinksView` (VM-08) | Guild Council (`C`, `CA`) | `ready` (Active and historical access links table, grant form with identity search, revoke form, set-default form), `empty` (Zero active links warning) | Native HTML forms with hidden `csrf_token` and optimistic `version` | `tests/web/test_p3_4_council_character_views.py::test_vm08_character_links_complete_evidence_and_invariants`, `tests/web/test_p3_4_council_character_views.py::test_r25_r26_r27_form_actions_and_named_fields` |
| `identity_migration.html` | `GET /v1/council/identity-migration` (R-28), `POST /v1/council/identity-migration/{proposal_id}/confirm` (R-29 confirm proposal), `POST /v1/council/identity-migration/{proposal_id}/reject` (R-30 reject proposal) | `IdentityMigrationView` (VM-10) | Guild Council (`C`, `CA`) | `ready` (Migration runs, proposal list with evidence/confidence, confirmation/rejection action forms with CSRF), `empty` (No proposals pending) | Native HTML forms with `csrf_token` and `version` | `tests/web/test_p3_4_identity_and_role_views.py::test_render_identity_migration_ready_state`, `tests/web/test_p3_4_identity_and_role_views.py::test_form_field_exactness_validators` |
| `field_profile.html` | `GET /v1/council/field-profile` (R-31) | `FieldProfileView` (VM-11) | Guild Council and Platform Administrator (`C`, `A`, `CA`) | `ready` (Read-only table of profile paths, snapshot modes, and field authorities; zero mutation forms) | Static structured table layout | `tests/web/test_p3_4_identity_and_role_views.py::test_render_field_profile_structure`, `tests/web/test_p3_4_identity_and_role_views.py::test_render_field_profile_no_forms` |
| `role_capabilities.html` | `GET /v1/admin/role-capabilities` (R-32), `POST /v1/admin/role-capabilities` (R-33 create), `POST /v1/admin/role-capabilities/{mapping_id}/revoke` (R-34 revoke), `POST /v1/admin/role-capabilities/{mapping_id}/ratify` (R-38 ratify) | `RoleCapabilityView` (VM-12) | Platform Administrator (`A`, `CA`, `BG` within N-67, `AC` within N-67; ratification R-38 requires full `A`/`CA`) | `ready` (Role mapping rows, provenance markers `ordinary` vs `emergency_continuity`, create form, revoke forms, ratify forms with CSRF) | Native HTML `<form method="post">` with `csrf_token` and `version` | `tests/web/test_p3_4_identity_and_role_views.py::test_render_role_capabilities_full_admin`, `tests/web/test_p3_4_identity_and_role_views.py::test_render_role_capabilities_emergency_continuity` |
| `account_identities.html` | `GET /v1/account/identities` (R-35), `GET /v1/account/identities/link/start` (R-36 denied), `POST /v1/account/identities/{identity_id}/unlink` (R-37) | `AccountIdentitiesView` (VM-13) | Authenticated User (`N`, `M`, `C`, `A`, `CA`, `BG`) | `ready` (List of linked identities showing provider and canonical decimal snowflake in `code.identity-subject`, unlink form with CSRF), `denied` (When R-36 accessed, renders single-provider explanatory refusal `no_additional_provider`) | Static presentation with semantic code elements; native unlink form | `tests/web/test_p3_4_identity_and_role_views.py::test_render_account_identities_ready_state`, `tests/web/test_p3_4_identity_and_role_views.py::test_render_account_identities_r36_denied_state` |
| `council_snapshots.html` | `GET /v1/council/snapshots` (R-40), `POST /v1/admin/snapshots/{snapshot_id}/folder` (R-41), `POST /v1/council/snapshots/{snapshot_id}/preview-jobs` (R-42) | `SnapshotListView` (VM-14) | Guild Council & Administrator (`C`, `A`, `CA`; folder selection R-41 is `A`/`CA`, preview R-42 is `C`/`CA`) | `ready` (Snapshots list, folder selection dropdown `FolderChoice`, preview job creation button with server-minted `preview_nonce` and `csrf_token`), `empty` (No snapshots available) | Native HTML `<form method="post">` for folder selection and preview creation | `tests/web/test_p3_4_snapshot_views.py::test_render_snapshot_list_ready_state`, `tests/web/test_p3_4_snapshot_views.py::test_render_preview_form_submits_the_view_supplied_nonce` |
| `job_status.html` | `GET /v1/council/jobs/{job_id}` (R-43 full page), `POST /v1/council/jobs/{job_id}/cancel` (R-45), `POST /v1/council/jobs/{job_id}/apply` (R-46) | `JobStatusView` (VM-15) | Guild Council (`C`, `CA`) | `ready` (Reconciliation preview summary `ReconciliationSummary`, match counters, blocked entries bounded to 120 chars, cancel button, apply/confirm button with `ConfirmScope.preview_token`), `queued`/`running` (Progress bar, polling container), `completed` (Import receipt link), `stale` (`StaleReason`), `failed` (`JobFailure`) | Full-page reload on manual browser refresh; native POST forms for cancel (R-45) and apply (R-46) with `csrf_token` | `tests/web/test_p3_4_job_status_views.py::test_every_accepted_job_state_renders_its_own_identity`, `tests/web/test_p3_4_job_status_views.py::test_the_confirmation_control_appears_only_when_the_view_carries_a_scope` |
| `job_status_fragment.html` | `GET /v1/council/jobs/{job_id}/status` (R-44 HTMX poll) | `JobStatusView` (VM-15 fragment) | Guild Council (`C`, `CA`) | `ready`, `queued`/`running` (HTMX active polling `hx-get="/v1/council/jobs/{id}/status" hx-trigger="every 2s"` while active only, stops polling on terminal states), `completed`, `stale`, `failed` | Standalone partial HTML fragment rendered on direct GET | `tests/web/test_p3_4_job_status_views.py::test_the_live_fragment_polls_on_the_server_interval_and_says_so_twice`, `tests/web/test_p3_4_job_status_views.py::test_terminal_states_carry_no_polling_and_no_refresh_control` |
| `import_result.html` | `GET /v1/council/imports/{import_id}` (R-47) | `ImportResultView` (VM-17) | Guild Council (`C`, `CA`) | `ready` (Immutable import receipt, created/updated counts, closed issue codes list, attributed actor, correlation UUID, duplicate indicator if retry) | Static structured receipt document | `tests/web/test_p3_4_import_and_audit_views.py::test_import_result_applied_council_rendering`, `tests/web/test_p3_4_import_and_audit_views.py::test_import_result_strictly_immutable_no_forms_no_downloads` |
| `audit_search.html` | `GET /v1/audit` (R-48) | `AuditSearchView` (VM-18) | Guild Council and Platform Administrator (`C`, `A`, `CA`, `BG`, `AC`) | `ready` (Audit filter form `AuditFilters`, paginated audit rows `AuditRow`, facts `AuditFact` bounded to 200 chars), `empty` (No audit events matching criteria) | Native HTML `<form method="get" action="/v1/audit">` with full-page pagination links `?page=...&cursor=...` | `tests/web/test_p3_4_import_and_audit_views.py::test_audit_search_exact_form_structure_and_8_fields`, `tests/web/test_p3_4_import_and_audit_views.py::test_audit_search_retains_all_filter_values` |
| `audit_results.html` | `GET /v1/audit/results` (R-49 HTMX partial) | `AuditSearchView` (VM-18 fragment) | Guild Council and Platform Administrator (`C`, `A`, `CA`, `BG`, `AC`) | `ready` (Standalone table rows fragment with signed cursor pagination `Cursor`), `empty` (Empty rows notice) | Standalone partial HTML fragment rendered on direct GET | `tests/web/test_p3_4_import_and_audit_views.py::test_audit_results_ready_state_rows_rendering`, `tests/web/test_p3_4_import_and_audit_views.py::test_audit_results_empty_state_rendering` |

---

## 5. Comprehensive Route, View-Model, and Requirements Traceability Matrix

### A. Route Traceability
Every HTTP route in the accepted Phase 3 inventory is mapped to its exact defining handler symbol, response kind, template / response model, and verifying test symbol(s):

| Route ID | Path & Method | Handler / Mount Site | Response Kind | Template / Response Model | Verifying Test Reference |
|---|---|---|---|---|---|
| **R-01** | `GET /` | `adapters/web/app.py::root` | Navigation Redirect | `303` to `/v1/characters` or `/v1/login` | `tests/web/test_request_authority_and_lifecycle.py::test_the_session_cookie_looked_up_and_cleared_is_still_graph_as` (HTTP redirect destinations), `tests/web/test_structural_guards.py::test_the_registered_route_set_equals_the_contract_exactly` (structural route registration) |
| **R-02** | `GET /v1/login` | `adapters/web/app.py::login_page` | Navigation HTML | `login.html` · `LoginPageView` (VM-01) | `tests/web/test_p3_4_auth_and_system_views.py::test_login_rendering_all_branches` (rendering), `tests/web/test_request_authority_and_lifecycle.py::test_the_login_cookie_emitted_still_carries_graph_as_attributes` (HTTP cookie emission) |
| **R-03** | `GET /v1/auth/discord/start` | `adapters/web/app.py::oauth_start` | Navigation Redirect | `303` to Discord OAuth URL | `tests/web/test_oauth_flow.py::test_start_mints_a_transaction_and_redirects_with_the_exact_scopes` (HTTP / Start transaction & 303 redirect) |
| **R-04** | `GET /auth/discord/callback` | `adapters/web/app.py::oauth_callback` | Navigation Redirect / HTML | `303` return target; `403` `non_member.html` (VM-02); `503` `degraded.html` (VM-03) | `tests/web/test_oauth_flow.py::test_a_member_login_creates_one_session_and_one_audit_event` (HTTP member session create & 303 redirect), `tests/web/test_oauth_flow.py::test_a_non_member_callback_creates_no_session_and_answers_403` (HTTP non-member 403 response), `tests/web/test_p3_4_auth_and_system_views.py::test_non_member_rendering` (non-member 403 HTML render), `tests/web/test_oauth_flow.py::test_a_provider_outage_at_the_exchange_creates_no_session` (HTTP degraded 503 response), `tests/web/test_p3_4_auth_and_system_views.py::test_degraded_rendering` (degraded 503 HTML render) |
| **R-05** | `POST /v1/auth/logout` | `adapters/web/app.py::logout` | Form Redirect | `303` to `/v1/login` | `tests/web/test_sessions.py::test_logout_revokes_the_session_and_deletes_the_stored_tokens` (service & database session revocation), `tests/web/test_request_authority_and_lifecycle.py::test_csrf_verification_still_uses_graph_as_key` (HTTP CSRF verification on R-05) |
| **R-06** | `GET /v1/auth/emergency` | `adapters/web/app.py::emergency_login_page` | Navigation HTML | `emergency.html` · `EmergencyLoginView` (VM-04) | `tests/web/test_p3_4_auth_and_system_views.py::test_emergency_access_rendering_all_combinations` (rendering emergency form & branches) |
| **R-07** | `POST /v1/auth/emergency/webauthn/options` | `adapters/web/app.py::emergency_webauthn_options` | JSON (fetch) | `200` `application/json` | `tests/web/test_request_authority_and_lifecycle.py::test_the_accepted_origin_is_still_graph_as_after_the_replacement` (HTTP origin validation & JSON response), `tests/web/test_break_glass_login.py::test_a_challenge_is_single_use` (service challenge single-use invariant) |
| **R-08** | `POST /v1/auth/emergency/webauthn/verify` | `adapters/web/app.py::emergency_webauthn_verify` | JSON (fetch) | `200` `application/json` | `tests/web/test_break_glass_login.py::test_one_credential_shares_one_assertion_budget_across_addresses` (HTTP assertion verify route & rate budget), `tests/web/test_break_glass_login.py::test_an_enrolled_credential_creates_a_break_glass_session_with_discord_faulted` (service-layer credential verification) |
| **R-09** | `POST /v1/auth/emergency/recovery` | `adapters/web/app.py::emergency_recovery_login` | Form Redirect | `303` to `/v1/admin/role-capabilities` | `tests/web/test_break_glass_login.py::test_the_sixth_attempt_against_one_grant_is_refused_across_addresses` (HTTP rate-limited recovery post route execution), `tests/web/test_break_glass_login.py::test_a_recovery_grant_creates_a_session_and_names_only_its_record_id` (service-layer grant redemption), `tests/web/test_p3_4_auth_and_system_views.py::test_emergency_access_rendering_all_combinations` (recovery form template render) |
| **R-10** | `GET /healthz` | `adapters/web/app.py::health` | Operator JSON | `200`/`503` `application/json` · `HealthView` (VM-16) | `tests/web/test_request_authority_and_lifecycle.py::test_health_evaluation_still_receives_graph_a` (HTTP health 200/503 evaluation), `tests/web/test_operator_commands.py::test_the_kill_switch_closes_the_portal_and_leaves_health_answering` (kill switch portal closure / health exemption), `tests/web/test_structural_guards.py::test_the_registered_route_set_equals_the_contract_exactly` (structural route registration) |
| **M-01** | `GET /static/*` | `adapters/web/static_assets.py::StaticAssets` | Static Mount | Starlette `Mount` over `adapters/web/static/` | `tests/web/test_static_asset_surface.py::test_get_and_head_serve_the_asset` (HTTP static delivery), `tests/web/test_p3_4_static_assets.py::test_static_corpus_equals_closed_step_2_inventory_exactly` (static corpus integrity) |
| **R-20** | `GET /v1/characters` | `adapters/web/portal_routes.py::my_characters` | Navigation HTML | `my_characters.html` · `MyCharactersView` (VM-05) | `tests/web/test_p3_4_member_views.py::test_my_characters_ready_state_rendering` (rendering), `tests/web/test_p3_4_member_views.py::test_r20_r21_http_behavior_with_database` (HTTP & DB) |
| **R-21** | `GET /v1/characters/{character_id}` | `adapters/web/portal_routes.py::character_detail` | Navigation HTML | `character_detail.html` · `CharacterDetailView` (VM-06) | `tests/web/test_p3_4_member_views.py::test_character_detail_populated_rendering` (rendering), `tests/web/test_p3_4_member_views.py::test_r20_r21_http_behavior_with_database` (HTTP & DB) |
| **R-22** | `GET /v1/council/characters` | `adapters/web/portal_routes.py::council_character_index` | Navigation HTML | `council_characters.html` · `CouncilCharacterIndexView` (VM-07) | `tests/web/test_p3_4_council_character_views.py::test_vm07_council_character_index_ready_and_filter` (rendering), `tests/web/test_p3_4_council_character_views.py::test_database_backed_council_character_views_and_mutations` (HTTP & DB) |
| **R-23** | `GET /v1/council/characters/{character_id}/links` | `adapters/web/portal_routes.py::council_character_links` | Navigation HTML | `character_links.html` · `CharacterLinksView` (VM-08) | `tests/web/test_p3_4_council_character_views.py::test_vm08_character_links_complete_evidence_and_invariants` (rendering), `tests/web/test_p3_4_council_character_views.py::test_database_backed_council_character_views_and_mutations` (HTTP & DB) |
| **R-24** | `GET /v1/council/identity-search` | `adapters/web/portal_routes.py::council_identity_search` | HTMX Partial HTML | `identity_search.html` · `IdentitySearchResultsView` (VM-09) | `tests/web/test_p3_4_council_character_views.py::test_vm09_identity_search_fragment` (rendering), `tests/web/test_p3_4_security_and_escaping.py::test_hostile_rendering_council_identity_search_username` (hostile boundary) |
| **R-25** | `POST /v1/council/characters/{character_id}/links` | `adapters/web/portal_routes.py::council_link_grant` | Form Redirect | `303` to R-23 | `tests/web/test_p3_4_council_character_views.py::test_r25_r26_r27_form_actions_and_named_fields` (form render), `tests/web/test_p3_4_council_character_views.py::test_database_backed_council_character_views_and_mutations` (HTTP mutation & redirect) |
| **R-26** | `POST /v1/council/characters/{character_id}/links/{access_id}/revoke` | `adapters/web/portal_routes.py::council_link_revoke` | Form Redirect | `303` to R-23 | `tests/web/test_p3_4_council_character_views.py::test_r25_r26_r27_form_actions_and_named_fields` (form render), `tests/web/test_p3_4_council_character_views.py::test_database_backed_council_character_views_and_mutations` (HTTP mutation & redirect) |
| **R-27** | `POST /v1/council/characters/{character_id}/links/{access_id}/default` | `adapters/web/portal_routes.py::council_link_set_default` | Form Redirect | `303` to R-23 | `tests/web/test_p3_4_council_character_views.py::test_r25_r26_r27_form_actions_and_named_fields` (form render), `tests/web/test_p3_4_council_character_views.py::test_database_backed_council_character_views_and_mutations` (HTTP mutation & redirect) |
| **R-28** | `GET /v1/council/identity-migration` | `adapters/web/portal_routes.py::council_identity_migration` | Navigation HTML | `identity_migration.html` · `IdentityMigrationView` (VM-10) | `tests/web/test_p3_4_identity_and_role_views.py::test_render_identity_migration_ready_state` (rendering), `tests/web/test_p3_4_identity_and_role_views.py::test_database_backed_identity_and_role_views_and_mutations` (HTTP & DB) |
| **R-29** | `POST /v1/council/identity-migration/{proposal_id}/confirm` | `adapters/web/portal_routes.py::council_identity_migration_confirm` | Form Redirect | `303` to R-28 | `tests/web/test_p3_4_identity_and_role_views.py::test_form_field_exactness_validators` (form render), `tests/web/test_p3_4_identity_and_role_views.py::test_database_backed_identity_and_role_views_and_mutations` (HTTP mutation & redirect) |
| **R-30** | `POST /v1/council/identity-migration/{proposal_id}/reject` | `adapters/web/portal_routes.py::council_identity_migration_reject` | Form Redirect | `303` to R-28 | `tests/web/test_p3_4_identity_and_role_views.py::test_form_field_exactness_validators` (form render), `tests/web/test_p3_4_identity_and_role_views.py::test_database_backed_identity_and_role_views_and_mutations` (HTTP mutation & redirect) |
| **R-31** | `GET /v1/council/field-profile` | `adapters/web/portal_routes.py::council_field_profile` | Navigation HTML | `field_profile.html` · `FieldProfileView` (VM-11) | `tests/web/test_p3_4_identity_and_role_views.py::test_render_field_profile_structure` (rendering), `tests/web/test_p3_4_identity_and_role_views.py::test_database_backed_identity_and_role_views_and_mutations` (HTTP & DB) |
| **R-32** | `GET /v1/admin/role-capabilities` | `adapters/web/portal_routes.py::admin_role_capabilities` | Navigation HTML | `role_capabilities.html` · `RoleCapabilityView` (VM-12) | `tests/web/test_p3_4_identity_and_role_views.py::test_render_role_capabilities_full_admin` (rendering), `tests/web/test_p3_4_identity_and_role_views.py::test_database_backed_identity_and_role_views_and_mutations` (HTTP & DB) |
| **R-33** | `POST /v1/admin/role-capabilities` | `adapters/web/portal_routes.py::admin_role_capability_create` | Form Redirect | `303` to R-32 | `tests/web/test_p3_4_identity_and_role_views.py::test_render_role_capabilities_full_admin` (form render), `tests/web/test_p3_4_identity_and_role_views.py::test_database_backed_identity_and_role_views_and_mutations` (HTTP mutation & redirect) |
| **R-34** | `POST /v1/admin/role-capabilities/{mapping_id}/revoke` | `adapters/web/portal_routes.py::admin_role_capability_revoke` | Form Redirect | `303` to R-32 | `tests/web/test_p3_4_identity_and_role_views.py::test_render_role_capabilities_full_admin` (form render), `tests/web/test_p3_4_identity_and_role_views.py::test_database_backed_identity_and_role_views_and_mutations` (HTTP mutation & redirect) |
| **R-35** | `GET /v1/account/identities` | `adapters/web/portal_routes.py::account_identities` | Navigation HTML | `account_identities.html` · `AccountIdentitiesView` (VM-13) | `tests/web/test_p3_4_identity_and_role_views.py::test_render_account_identities_ready_state` (rendering), `tests/web/test_p3_4_identity_and_role_views.py::test_database_backed_identity_and_role_views_and_mutations` (HTTP & DB) |
| **R-36** | `GET /v1/account/identities/link/start` | `adapters/web/portal_routes.py::account_identity_link_start` | Navigation HTML | `account_identities.html` · `AccountIdentitiesView` (`denied`, VM-13) | `tests/web/test_p3_4_identity_and_role_views.py::test_render_account_identities_r36_denied_state` (rendering & denied state), `tests/web/test_p3_4_identity_and_role_views.py::test_database_backed_identity_and_role_views_and_mutations` (HTTP 200 response) |
| **R-37** | `POST /v1/account/identities/{identity_id}/unlink` | `adapters/web/portal_routes.py::account_identity_unlink` | Form Redirect | `303` to R-35 | `tests/web/test_p3_4_identity_and_role_views.py::test_render_account_identities_unlink_blocked_reasons` (form render), `tests/web/test_p3_4_identity_and_role_views.py::test_database_backed_identity_and_role_views_and_mutations` (HTTP mutation & redirect) |
| **R-38** | `POST /v1/admin/role-capabilities/{mapping_id}/ratify` | `adapters/web/portal_routes.py::admin_role_capability_ratify` | Form Redirect | `303` to R-32 | `tests/web/test_p3_4_identity_and_role_views.py::test_render_role_capabilities_emergency_continuity` (form render), `tests/web/test_p3_4_identity_and_role_views.py::test_database_backed_identity_and_role_views_and_mutations` (HTTP mutation & redirect) |
| **R-40** | `GET /v1/council/snapshots` | `adapters/web/import_routes.py::council_snapshots` | Navigation HTML | `council_snapshots.html` · `SnapshotListView` (VM-14) | `tests/web/test_p3_4_snapshot_views.py::test_render_snapshot_list_ready_state` (rendering), `tests/web/test_p3_4_snapshot_views.py::test_database_backed_snapshot_views_and_mutations` (HTTP & DB) |
| **R-41** | `POST /v1/admin/snapshots/{snapshot_id}/folder` | `adapters/web/import_routes.py::admin_snapshot_folder` | Form Redirect | `303` to R-40 | `tests/web/test_p3_4_snapshot_views.py::test_form_field_exactness_validators` (form render), `tests/web/test_p3_4_snapshot_views.py::test_database_backed_snapshot_views_and_mutations` (HTTP mutation & redirect) |
| **R-42** | `POST /v1/council/snapshots/{snapshot_id}/preview-jobs` | `adapters/web/import_routes.py::council_preview_job_create` | Form Redirect | `303` to R-43 | `tests/web/test_p3_4_snapshot_views.py::test_render_preview_form_submits_the_view_supplied_nonce` (nonce render), `tests/web/test_p3_4_snapshot_views.py::test_database_backed_snapshot_views_and_mutations` (HTTP mutation & redirect) |
| **R-43** | `GET /v1/council/jobs/{job_id}` | `adapters/web/import_routes.py::council_job_page` | Navigation HTML | `job_status.html` · `JobStatusView` (VM-15) | `tests/web/test_p3_4_job_status_views.py::test_every_accepted_job_state_renders_its_own_identity` (rendering), `tests/web/test_p3_4_job_status_views.py::test_r43_and_r44_caller_matrices` (HTTP & caller matrix) |
| **R-44** | `GET /v1/council/jobs/{job_id}/status` | `adapters/web/import_routes.py::council_job_status` | HTMX Poll Partial | `job_status_fragment.html` · `JobStatusView` (VM-15 fragment) | `tests/web/test_p3_4_job_status_views.py::test_the_live_fragment_polls_on_the_server_interval_and_says_so_twice` (fragment polling render), `tests/web/test_p3_4_job_status_views.py::test_r43_and_r44_caller_matrices` (HTTP & caller matrix) |
| **R-45** | `POST /v1/council/jobs/{job_id}/cancel` | `adapters/web/import_routes.py::council_job_cancel` | Form Redirect | `303` to R-43 | `tests/web/test_p3_4_job_status_views.py::test_the_cancel_control_appears_only_when_the_view_allows_it` (form render), `tests/web/test_p3_4_job_status_views.py::test_r45_caller_matrix` (HTTP mutation & cancel) |
| **R-46** | `POST /v1/council/jobs/{job_id}/apply` | `adapters/web/import_routes.py::council_import_confirm` | Form Redirect | `303` to R-43 | `tests/web/test_p3_4_job_status_views.py::test_the_confirmation_control_appears_only_when_the_view_carries_a_scope` (scope form render), `tests/web/test_p3_4_job_status_views.py::test_r46_caller_matrix` (HTTP mutation & enqueue apply) |
| **R-47** | `GET /v1/council/imports/{import_id}` | `adapters/web/import_routes.py::council_import_result` | Navigation HTML | `import_result.html` · `ImportResultView` (VM-17) | `tests/web/test_p3_4_import_and_audit_views.py::test_import_result_applied_council_rendering` (rendering), `tests/web/test_p3_4_import_and_audit_views.py::test_r47_import_receipt_database_backed_rendering` (HTTP & DB) |
| **R-48** | `GET /v1/audit` | `adapters/web/import_routes.py::audit_search` | Navigation HTML | `audit_search.html` · `AuditSearchView` (VM-18) | `tests/web/test_p3_4_import_and_audit_views.py::test_audit_search_exact_form_structure_and_8_fields` (rendering), `tests/web/test_p3_4_import_and_audit_views.py::test_r48_audit_search_caller_matrix_including_bg_and_ac` (HTTP & caller matrix) |
| **R-49** | `GET /v1/audit/results` | `adapters/web/import_routes.py::audit_search_results` | HTMX Partial HTML | `audit_results.html` · `AuditSearchView` (VM-18 fragment) | `tests/web/test_p3_4_import_and_audit_views.py::test_audit_results_ready_state_rows_rendering` (fragment rendering), `tests/web/test_p3_4_import_and_audit_views.py::test_r49_audit_results_caller_matrix_including_bg_and_ac` (HTTP & caller matrix) |

### B. View-Model Traceability (VM-01 through VM-22)
Every view-model defined in `application/web/view_models.py` is mapped to its contract role, associated template or JSON response, and exact verifying test symbol(s):

| VM ID | Class Name | Output Role | Associated Template / Response | Verifying Test Reference |
|---|---|---|---|---|
| **VM-01** | `LoginPageView` | HTML Page | `login.html` | `tests/web/test_p3_4_auth_and_system_views.py::test_login_rendering_all_branches` |
| **VM-02** | `NonMemberView` | HTML Page | `non_member.html` | `tests/web/test_p3_4_auth_and_system_views.py::test_non_member_rendering` |
| **VM-03** | `ServiceDegradedView` | HTML Page | `degraded.html` | `tests/web/test_p3_4_auth_and_system_views.py::test_degraded_rendering` |
| **VM-04** | `EmergencyLoginView` | HTML Page | `emergency.html` | `tests/web/test_p3_4_auth_and_system_views.py::test_emergency_access_rendering_all_combinations` |
| **VM-05** | `MyCharactersView` | HTML Page | `my_characters.html` | `tests/web/test_p3_4_member_views.py::test_my_characters_ready_state_rendering`, `tests/web/test_p3_4_member_views.py::test_my_characters_empty_state_rendering` |
| **VM-06** | `CharacterDetailView` | HTML Page | `character_detail.html` | `tests/web/test_p3_4_member_views.py::test_character_detail_populated_rendering`, `tests/web/test_p3_4_member_views.py::test_character_detail_null_level_and_council_access_and_unmapped_provenance` |
| **VM-07** | `CouncilCharacterIndexView` | HTML Page | `council_characters.html` | `tests/web/test_p3_4_council_character_views.py::test_vm07_council_character_index_ready_and_filter`, `tests/web/test_p3_4_council_character_views.py::test_vm07_council_character_index_empty` |
| **VM-08** | `CharacterLinksView` | HTML Page | `character_links.html` | `tests/web/test_p3_4_council_character_views.py::test_vm08_character_links_complete_evidence_and_invariants`, `tests/web/test_p3_4_council_character_views.py::test_vm08_character_links_empty_invariants_and_unrecorded_fields` |
| **VM-09** | `IdentitySearchResultsView` | HTML Partial | `identity_search.html` | `tests/web/test_p3_4_council_character_views.py::test_vm09_identity_search_fragment`, `tests/web/test_p3_4_council_character_views.py::test_vm09_identity_search_empty_and_invalid` |
| **VM-10** | `IdentityMigrationView` | HTML Page | `identity_migration.html` | `tests/web/test_p3_4_identity_and_role_views.py::test_render_identity_migration_ready_state`, `tests/web/test_p3_4_identity_and_role_views.py::test_render_identity_migration_decision_states` |
| **VM-11** | `FieldProfileView` | HTML Page | `field_profile.html` | `tests/web/test_p3_4_identity_and_role_views.py::test_render_field_profile_structure`, `tests/web/test_p3_4_identity_and_role_views.py::test_render_field_profile_no_forms` |
| **VM-12** | `RoleCapabilityView` | HTML Page | `role_capabilities.html` | `tests/web/test_p3_4_identity_and_role_views.py::test_render_role_capabilities_full_admin`, `tests/web/test_p3_4_identity_and_role_views.py::test_render_role_capabilities_emergency_continuity` |
| **VM-13** | `AccountIdentitiesView` | HTML Page | `account_identities.html` | `tests/web/test_p3_4_identity_and_role_views.py::test_render_account_identities_ready_state`, `tests/web/test_p3_4_identity_and_role_views.py::test_render_account_identities_r36_denied_state` |
| **VM-14** | `SnapshotListView` | HTML Page | `council_snapshots.html` | `tests/web/test_p3_4_snapshot_views.py::test_render_snapshot_list_ready_state`, `tests/web/test_p3_4_snapshot_views.py::test_render_snapshot_list_empty_state` |
| **VM-15** | `JobStatusView` | HTML Page & Partial | `job_status.html` / `job_status_fragment.html` | `tests/web/test_p3_4_job_status_views.py::test_every_accepted_job_state_renders_its_own_identity`, `tests/web/test_p3_4_job_status_views.py::test_the_live_fragment_polls_on_the_server_interval_and_says_so_twice` |
| **VM-16** | `HealthView` | JSON (Operator / Loopback) | Explicitly JSON response (`/healthz`); no HTML template | `tests/web/test_request_authority_and_lifecycle.py::test_health_evaluation_still_receives_graph_a`, `tests/web/test_structural_guards.py::test_the_registered_route_set_equals_the_contract_exactly` |
| **VM-17** | `ImportResultView` | HTML Page | `import_result.html` | `tests/web/test_p3_4_import_and_audit_views.py::test_import_result_applied_council_rendering`, `tests/web/test_p3_4_import_and_audit_views.py::test_import_result_strictly_immutable_no_forms_no_downloads` |
| **VM-18** | `AuditSearchView` | HTML Page & Partial | `audit_search.html` / `audit_results.html` | `tests/web/test_p3_4_import_and_audit_views.py::test_audit_search_exact_form_structure_and_8_fields`, `tests/web/test_p3_4_import_and_audit_views.py::test_audit_results_ready_state_rows_rendering` |
| **VM-19** | `ConflictView` | HTML Page | `conflict.html` (`409 Conflict`) | `tests/web/test_p3_4_auth_and_system_views.py::test_conflict_rendering_and_conditional_scope` |
| **VM-20** | `SafeErrorView` | HTML Page | `error.html` (`500 Internal Server Error`) | `tests/web/test_p3_4_auth_and_system_views.py::test_error_rendering`, `tests/web/test_oauth_refusal_audit.py::test_correlation_of_semantics_and_falsification` |
| **VM-21** | `ValidationView` | HTML Page | `validation.html` (`422 Unprocessable Entity`) | `tests/web/test_p3_4_auth_and_system_views.py::test_validation_rendering_and_anchors` |
| **VM-22** | `DeniedView` | HTML Page | `denied.html` (`401` / `403` / `404` Safe Denial) | `tests/web/test_p3_4_auth_and_system_views.py::test_denied_rendering_and_minimization`, `tests/web/test_p3_4_auth_and_system_views.py::test_vm22_http_absent_and_inaccessible_byte_identity` |

### C. Requirements & Evidence Traceability Matrix

| Requirement ID | Description / Scope | Evidence Class | Supporting Test / Inspection Reference | Step 13 Verification Result |
|---|---|---|---|---|
| **TC-UI-01 / 02** | Browser automated rendering & responsive layout | Browser Execution | *None installed in test environment* | **NOT RUN** (Zero browser binaries installed; honest status) |
| **TC-UI-03** | Semantic landmarks & heading hierarchy | Parsed DOM / ASGI | `tests/web/test_p3_4_accessibility.py::test_base_template_landmarks_and_skip_link_order`, `tests/web/test_p3_4_accessibility.py::test_all_full_pages_have_single_h1_and_no_duplicate_main` | **PASS** (Single `<h1>`, `<header>`, `<main>`, `<footer>` across 26 templates) |
| **TC-UI-04** | WCAG 2.1 AA Color Contrast Ratios | Static Tokens / Math | `tests/web/test_p3_4_accessibility.py::test_tc_ui_07_wcag_contrast_matrix`, `design-prototype/tools/calc_contrast.py` | **PASS** (48/48 evaluated pairs PASS AA/AAA; 1 disabled button exempt) |
| **TC-UI-05** | Form label associations & aria attributes | Parsed DOM / ASGI | `tests/web/test_p3_4_accessibility.py::test_form_controls_have_accessible_labels_and_valid_tabindex` | **PASS** (All `<input>`/`<select>` have associated `<label for="field_id">`) |
| **TC-UI-06** | Focus indicator treatment & reduced motion | Static CSS / Source | `tests/web/test_p3_4_accessibility.py::test_stylesheet_defines_high_contrast_focus_visible_indicators`, `tests/web/test_p3_4_accessibility.py::test_tc_ui_04_prefers_reduced_motion_media_query` | **PASS** (High-contrast focus ring, `@media (prefers-reduced-motion)` rules) |
| **TC-UI-07** | Essential no-JavaScript flow fallback | Real ASGI / Stripped | `tests/web/test_p3_4_accessibility.py::test_rendered_no_javascript_fallback_evidence`, `tests/web/test_p3_4_security_and_escaping.py::test_essential_no_javascript_flows` | **PASS** (All 9 essential flows work with `hx-*` attributes stripped) |
| **TC-UI-08** | Real device layout inspection (320/768/1280) | Physical Device | *Maintainer manual acceptance* | **NOT RUN — Peter/maintainer real-device acceptance** |
| **TC-UI-09** | Screen reader / assistive tech traversal | Assistive Tech | *Human specialist review* | **NOT RUN — Assistive-technology/screen-reader review** |
| **TC-SEC-05** | Exact security response headers | Real ASGI Response | `tests/web/test_p3_4_security_and_escaping.py::test_exact_security_headers_full_pages_unauthenticated` | **PASS** (CSP N-26, nosniff, Referrer-Policy, COOP, CORP, 0 XFO, 0 CORS) |
| **TC-SEC-08** | Template autoescaping & zero bypasses | AST & Token Scan | `tests/web/test_p3_4_security_and_escaping.py::test_autoescaping_is_on_and_zero_templates_use_safe_filter_ast` | **PASS** (0 `\|safe`, 0 `Markup()`, autoescape enabled across all 26 templates) |
| **TC-SEC-09** | Hostile input matrix & boundary inertness | Real DB & ASGI | `tests/web/test_p3_4_security_and_escaping.py::test_hostile_rendering_character_display_names`, `tests/web/test_p3_4_security_and_escaping.py::test_hostile_rendering_audit_event_reasons` | **PASS** (All 7 hostile vectors render inert text in exact containers) |
| **TC-SEC-10** | Zero executable inline scripts / handlers | Static HTML Scan | `tests/web/test_p3_4_security_and_escaping.py::test_executable_contexts_and_script_guards_across_all_templates` | **PASS** (0 `hx-on:`, 0 `on*`, 0 `javascript:`, 0 inline `<script>`, 0 remote origins) |
| **TC-SEC-11** | Script context invariants | Static HTML Scan | `tests/web/test_p3_4_security_and_escaping.py::test_executable_contexts_and_script_guards_across_all_templates` | **PASS** (Vendored script in `base.html` only; zero Jinja in `src` attributes) |
| **TC-STRUCT-01** | Route & view model structural invariants | Source Inspection | `tests/web/test_structural_guards.py::test_the_registered_route_set_equals_the_contract_exactly`, `tests/web/test_structural_guards.py::test_the_registered_mount_set_equals_the_contract_exactly` | **PASS** (100% route-to-view-model contract alignment; zero drift) |
| **TC-STRUCT-02** | Static asset manifest & hash integrity | SHA-256 Digest | `sha256sum -c adapters/web/static/asset-integrity.sha256` | **PASS** (3/3 static assets match exact SHA-256 digests) |
| **TC-STRUCT-03** | Visual prototype freeze manifest | SHA-256 Digest | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | **PASS** (14/14 prototype files match exact SHA-256 digests) |
| **F-SEC-01** | Security falsification: Security headers refusal | In-Memory Mutation | `tests/web/test_p3_4_security_and_escaping.py::test_falsification_f_sec_01_security_headers` | **PASS** (Probe fails as expected when CSP/security headers are mutated) |
| **F-SEC-02** | Security falsification: Template autoescaping AST | In-Memory Mutation | `tests/web/test_p3_4_security_and_escaping.py::test_falsification_f_sec_02_template_escaping_ast` | **PASS** (Probe fails as expected when unsafe filter is introduced) |
| **F-SEC-03** | Security falsification: Hostile rendering inertness | In-Memory Mutation | `tests/web/test_p3_4_security_and_escaping.py::test_falsification_f_sec_03_hostile_rendering_inert` | **PASS** (Probe fails as expected when unescaped HTML payload renders) |
| **F-SEC-04** | Security falsification: Executable contexts scan | In-Memory Mutation | `tests/web/test_p3_4_security_and_escaping.py::test_falsification_f_sec_04_executable_contexts` | **PASS** (Probe fails as expected when inline event handler is injected) |
| **F-SEC-05** | Security falsification: Script context invariants | In-Memory Mutation | `tests/web/test_p3_4_security_and_escaping.py::test_falsification_f_sec_05_script_context_invariants` | **PASS** (Probe fails as expected when dynamic script src is injected) |
| **F-SEC-06** | Security falsification: Denial response body | In-Memory Mutation | `tests/web/test_p3_4_security_and_escaping.py::test_falsification_f_sec_06_denial_response_body` | **PASS** (Probe fails as expected when denial body leaks context) |
| **F-SEC-07** | Security falsification: Validation response body | In-Memory Mutation | `tests/web/test_p3_4_security_and_escaping.py::test_falsification_f_sec_07_validation_response_body` | **PASS** (Probe fails as expected when validation body is malformed) |
| **F-SEC-08** | Security falsification: Stale response body | In-Memory Mutation | `tests/web/test_p3_4_security_and_escaping.py::test_falsification_f_sec_08_stale_response_body` | **PASS** (Probe fails as expected when stale response body is malformed) |
| **F-SEC-09** | Security falsification: Safe error body & UUID | In-Memory Mutation | `tests/web/test_p3_4_security_and_escaping.py::test_falsification_f_sec_09_safe_error_body` | **PASS** (Probe fails as expected when safe error leaks tracebacks) |
| **F-SEC-10** | Security falsification: No-JavaScript fallback | In-Memory Mutation | `tests/web/test_p3_4_security_and_escaping.py::test_falsification_f_sec_10_no_javascript_fallback` | **PASS** (Probe fails as expected when no-JS form action is missing) |
| **F-SEC-11** | Security falsification: Council identity search | In-Memory Mutation | `tests/web/test_p3_4_security_and_escaping.py::test_falsification_council_identity_search_hostile_rendering` | **PASS** (Probe fails as expected when unescaped username HTML is admitted) |

---

## 6. Complete Verification Transcript

All required Step 13 verification commands were executed as independent runs against disposable PostgreSQL. Literal command lines, environment boundaries, and results are recorded below:

### Command 1: Complete Web Portal Test Suite
```bash
TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
  /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
```
- **Exit Code:** `0`
- **Result:** `2168 passed, 80 skipped, 1063 warnings in 127.20s (0:02:07)`
- **Explanation of Skips (80 total):**
  - `SKIPPED [54] tests/web/test_p3_2_matrix.py:155`: Permitted authorization matrix cells are asserted by dedicated per-route success test cases.
  - `SKIPPED [26] tests/web/test_p3_3_matrix.py:198`: Permitted job/audit matrix cells are asserted by dedicated per-route success test cases.
  - *No required test was skipped or deselected.*
- **Explanation of Warnings (1063 total):**
  - Non-blocking HTTPX test-harness deprecation warnings (`DeprecationWarning: Setting per-request cookies=<...> is being deprecated...`) emitted by the async test client.

### Command 2: Bot & Domain Test Suite
```bash
TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
  /opt/discord-bots/freedom-bot/venv/bin/python -m pytest -q -rs tests/test_*.py
```
- **Exit Code:** `0`
- **Result:** `2294 passed, 1 warning in 136.38s (0:02:16)`
- **Explanation of Skips:** `0`
- **Explanation of Warnings:** `1` (`DeprecationWarning: 'audioop' is deprecated and slated for removal in Python 3.13` from `discord/player.py:29`).

### Command 3: Foundry VTT Module Test Suite
```bash
node --test "foundry-module/tests/*.test.mjs"
```
- **Exit Code:** `0`
- **Result:** `tests 155, suites 0, pass 155, fail 0, cancelled 0, skipped 0, todo 0, duration_ms 212.38ms`

### Command 4: Production Static Asset Integrity
```bash
sha256sum -c adapters/web/static/asset-integrity.sha256
```
- **Exit Code:** `0`
- **Output:**
  - `adapters/web/static/css/freedom-blades.58a9b9eed003.css: OK`
  - `adapters/web/static/images/freedom-blades-token.eab0d13128f5.png: OK`
  - `adapters/web/static/vendor/htmx-2.0.10.71ea67185bfa.min.js: OK`

### Command 5: Visual Prototype Freeze Manifest
```bash
sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256
```
- **Exit Code:** `0`
- **Output:** 14/14 prototype assets and HTML/CSS/JS files verified `OK`.

### Command 6: Web Virtual Environment Bytecode Compilation
```bash
/opt/discord-bots/venv-web/bin/python -m compileall -q adapters application domain tests
```
- **Exit Code:** `0` (Clean, 0 errors)

### Command 7: Bot Virtual Environment Bytecode Compilation
```bash
/opt/discord-bots/freedom-bot/venv/bin/python -m compileall -q adapters application domain tests
```
- **Exit Code:** `0` (Clean, 0 errors)

### Command 8: Git Whitespace & Conflict Marker Verification
```bash
git diff --check
```
- **Exit Code:** `0` (Clean, 0 whitespace or conflict marker errors)

### Command 9: Repository Tooling & Checkers Discovery
- Inspected repository root for `pyproject.toml`, `setup.cfg`, `tox.ini`, `.flake8`, `mypy.ini`, `package.json`, `.ruff.toml`, `.prettierrc` — all are absent (no repository-level linter, formatter, or type-checker configuration is installed).
- Inspected `/opt/discord-bots/venv-web/bin` and `/opt/discord-bots/freedom-bot/venv/bin` — neither environment contains `ruff`, `flake8`, `black`, `isort`, `mypy`, or `eslint`.
- Executed `design-prototype/tools/check_css_tokens.py`:
  - Result: `71 defined tokens, 62 unique referenced tokens, 0 undefined tokens. SUCCESS: All referenced CSS tokens are defined.`
- Executed `design-prototype/tools/calc_contrast.py`:
  - Result: `49 evaluated matrix pairs: 48 PASS AA/AAA, 1 EXEMPT (disabled button), 0 FAIL.`

### Command 10: Standalone AST-Aware Evidence Validator & In-Memory Falsification Demonstrations

The canonical evidence validator is embedded below. Every verification command is an independently executable literal command that dynamically extracts the canonical validator block from the submission document, requires zero external scratch modules, creates zero temporary files, and executes cleanly in a fresh subshell.

#### 1. Canonical Evidence Validator Implementation
```python
# CANONICAL_SUBMISSION_VALIDATOR
import ast, glob, hashlib, os, re, sys

def validate_submission_content(raw_text, filename="submission", inject_flag=None):
    text = raw_text
    if inject_flag == "--inject-false-path":
        text = text.replace(
            "tests/web/test_oauth_flow.py::test_start_mints_a_transaction_and_redirects_with_the_exact_scopes",
            "tests/web/falsified_non_existent_file.py::test_start_mints_a_transaction_and_redirects_with_the_exact_scopes"
        )
    elif inject_flag == "--inject-false-symbol":
        text = text.replace(
            "tests/web/test_oauth_flow.py::test_start_mints_a_transaction_and_redirects_with_the_exact_scopes",
            "tests/web/test_oauth_flow.py::falsified_non_existent_symbol"
        )
    elif inject_flag == "--inject-prohibited-shorthand":
        text = text.replace("| **F-SEC-01** |", "| **F-SEC-01 through F-SEC-10** |")
    elif inject_flag == "--check-unquoted-extraction":
        text = text.replace(
            "| **R-03** | `GET /v1/auth/discord/start` | `adapters/web/app.py::oauth_start` | Navigation Redirect | `303` to Discord OAuth URL | `tests/web/test_oauth_flow.py::test_start_mints_a_transaction_and_redirects_with_the_exact_scopes` (HTTP / Start transaction & 303 redirect) |",
            "| **R-03** | `GET /v1/auth/discord/start` | `adapters/web/app.py::oauth_start` | Navigation Redirect | `303` to Discord OAuth URL | In unquoted prose, see tests/web/test_oauth_flow.py::test_start_mints_a_transaction_and_redirects_with_the_exact_scopes, which verifies HTTP 303. |"
        )

    # 1. Reject range/shorthand expressions in traceability
    trace_sections = text.split("## 5. Comprehensive Route")[1].split("## 6. Complete Verification Transcript")[0]
    for pat in [r"\bthrough\s+`?test_", r"\bthrough\s+`?F-SEC", r"\.\.\.", r"\b\.\."]:
        matches = re.findall(pat, trace_sections, re.IGNORECASE)
        if matches:
            raise AssertionError(f"Prohibited range/shorthand found in traceability: {matches}")

    # 2. 26 templates in matrix
    matrix_section = text.split("## 4. Complete Screen Matrix")[1].split("## 5. Comprehensive Route")[0]
    matrix_rows = [l for l in matrix_section.strip().splitlines() if l.startswith("| `")]
    matrix_templates = {row.split("|")[1].strip(" `") for row in matrix_rows}
    fs_templates = set(os.path.relpath(p, "adapters/web/templates") for p in glob.glob("adapters/web/templates/**/*.html", recursive=True))
    assert len(fs_templates) == 26 and fs_templates == matrix_templates and len(matrix_rows) == 26, "Template matrix mismatch"

    # 3. 49 routes/mounts
    route_section = text.split("### A. Route Traceability")[1].split("### B. View-Model Traceability")[0]
    route_rows = [l for l in route_section.strip().splitlines() if l.startswith("| **")]
    expected_routes = ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "R-07", "R-08", "R-09", "R-10", "M-01"] + [f"R-{i:02d}" for i in range(20, 39)] + [f"R-{i:02d}" for i in range(40, 50)]
    found_routes = [r.split("|")[1].strip(" *`") for r in route_rows]
    assert set(found_routes) == set(expected_routes) and len(found_routes) == len(expected_routes), "Route mismatch"

    # 4. Handler symbols existence (nested functions or classes)
    ast_cache = {}
    def get_impl_symbols(fp):
        if fp not in ast_cache:
            tree = ast.parse(open(fp, "r", encoding="utf-8").read())
            syms = set()
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    syms.add(node.name)
            ast_cache[fp] = syms
        return ast_cache[fp]

    for r in route_rows:
        parts = [p.strip() for p in r.split("|")[1:-1]]
        r_id, handler_ref = parts[0].strip("*` "), parts[2].strip("` ")
        fp, sym = handler_ref.split("::")
        assert os.path.exists(fp), f"File {fp} does not exist"
        assert sym in get_impl_symbols(fp), f"Symbol {sym} not found in {fp}"
        if r_id.startswith("R-") and int(r_id[2:]) >= 20:
            assert fp != "adapters/web/app.py", f"False app.py attribution for {r_id}"

    # 5. Extract every fully qualified test reference across traceability sections
    evidence_text = text.split("## 6. Complete Verification Transcript")[0]
    test_refs_all = re.findall(r"\b(tests/web/(?:[a-zA-Z0-9_]+/)*[a-zA-Z0-9_]+\.py::[a-zA-Z0-9_]+)\b", evidence_text)
    assert test_refs_all, "No test symbols found"
    unique_test_refs = sorted(set(test_refs_all))

    def get_top_level_tests(tf):
        tree = ast.parse(open(tf, "r", encoding="utf-8").read())
        return {stmt.name for stmt in tree.body if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)) and stmt.name.startswith("test_")}

    test_cache = {}
    for ref in unique_test_refs:
        tf, ts = ref.split("::")
        assert os.path.exists(tf), f"Cited test file does not exist: {tf}"
        if tf not in test_cache:
            test_cache[tf] = get_top_level_tests(tf)
        assert ts in test_cache[tf], f"Cited test function \'{ts}\' is not a valid top-level test in {tf}"

    # 6. VM-01 to VM-22 classes
    vm_section = text.split("### B. View-Model Traceability (VM-01 through VM-22)")[1].split("### C. Requirements & Evidence")[0]
    vm_rows = [l for l in vm_section.strip().splitlines() if l.startswith("| **")]
    defined_vms = {n.name for n in ast.walk(ast.parse(open("application/web/view_models.py").read())) if isinstance(n, ast.ClassDef)}
    assert len(vm_rows) == 22, "Expected 22 VM rows"
    for row in vm_rows:
        vm_id, vm_cls = row.split("|")[1].strip("*` "), row.split("|")[2].strip("` ")
        assert vm_cls in defined_vms, f"VM {vm_cls} not defined"

    # 7. Inventory count & digests
    inv_section = text.split("### B. Complete Candidate Inventory for Phase 3.4")[1].split("## 4. Complete Screen Matrix")[0]
    inv_rows = [l for l in inv_section.strip().splitlines() if l.startswith("| `")]
    assert len(inv_rows) == 54, "Inventory count != 54"
    live_count, rename_count = 0, 0
    for row in inv_rows:
        parts = [p.strip() for p in row.split("|")[1:-1]]
        path, role, git_state, digest = parts[0].strip("` "), parts[1].strip("` "), parts[2].strip("` "), parts[3].strip("` ")
        if path == "adapters/web/static/css/freedom-blades.b0a1f3305683.css":
            assert digest == "absent (renamed)" and git_state == "Renamed (Old)"
            rename_count += 1
        else:
            assert os.path.exists(path), f"File {path} does not exist"
            assert hashlib.sha256(open(path, "rb").read()).hexdigest() == digest, f"Digest mismatch {path}"
            live_count += 1
    assert live_count == 53 and rename_count == 1, "Count mismatch"

    # 8. Static asset integrity manifest verification
    asset_manifest = "adapters/web/static/asset-integrity.sha256"
    assert os.path.exists(asset_manifest), f"Asset manifest missing: {asset_manifest}"
    asset_count = 0
    for line in open(asset_manifest).read().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        exp_h, rel_p = line.split()
        assert os.path.exists(rel_p), f"Asset path missing: {rel_p}"
        act_h = hashlib.sha256(open(rel_p, "rb").read()).hexdigest()
        assert act_h == exp_h, f"Asset integrity mismatch for {rel_p}"
        asset_count += 1
    assert asset_count == 3, f"Expected 3 asset manifest entries, got {asset_count}"

    # 9. Visual prototype freeze manifest verification
    freeze_manifest = "docs/review/phase-3-visual-freeze-manifest.sha256"
    assert os.path.exists(freeze_manifest), f"Freeze manifest missing: {freeze_manifest}"
    freeze_count = 0
    for line in open(freeze_manifest).read().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        exp_h, rel_p = line.split()
        assert os.path.exists(rel_p), f"Freeze path missing: {rel_p}"
        act_h = hashlib.sha256(open(rel_p, "rb").read()).hexdigest()
        assert act_h == exp_h, f"Freeze integrity mismatch for {rel_p}"
        freeze_count += 1
    assert freeze_count == 14, f"Expected 14 freeze manifest entries, got {freeze_count}"

    mode_str = f" [mode: {inject_flag}]" if inject_flag else ""
    print(f"VALIDATION SUCCESS{mode_str}: 26 templates, 49 routes/mounts, 22 VMs, {len(test_refs_all)} test references ({len(unique_test_refs)} unique node IDs), 53 live candidates, 1 rename row, 3 static assets, 14 freeze assets verified cleanly.")
    return True

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "docs/review/phase-3-p3-4-submission.md"
    flag = sys.argv[2] if len(sys.argv) > 2 else None
    content = open(target, "r", encoding="utf-8").read()
    validate_submission_content(content, target, flag)
```

#### 2. Positive Verification Run (Complete Literal Command & Output)
```bash
/opt/discord-bots/venv-web/bin/python -c 'import re, sys; doc = open("docs/review/phase-3-p3-4-submission.md", "r", encoding="utf-8").read(); blocks = re.findall(r"```python\n(# CANONICAL_SUBMISSION_VALIDATOR[\s\S]*?)\n```", doc); assert len(blocks) == 1, f"Expected 1 canonical validator block, found {len(blocks)}"; sys.argv = ["validator", "docs/review/phase-3-p3-4-submission.md"]; exec(blocks[0], {"__name__": "__main__"})'
```
- **Exit Code:** `0`
- **Actual Output (stdout):**
  ```text
  VALIDATION SUCCESS: 26 templates, 49 routes/mounts, 22 VMs, 193 test references (105 unique node IDs), 53 live candidates, 1 rename row, 3 static assets, 14 freeze assets verified cleanly.
  ```

#### 3. Negative In-Memory Falsification Demonstrations & Extraction Coverage

Each command below is a complete, standalone command executable from a fresh shell at the repository root. It extracts the canonical validator block and supplies an in-memory fault injection flag without touching any tracked files:

1. **Negative Demonstration A (False Test File Path):**
   - **Literal Command:**
     ```bash
     /opt/discord-bots/venv-web/bin/python -c 'import re, sys; doc = open("docs/review/phase-3-p3-4-submission.md", "r", encoding="utf-8").read(); blocks = re.findall(r"```python\n(# CANONICAL_SUBMISSION_VALIDATOR[\s\S]*?)\n```", doc); assert len(blocks) == 1, f"Expected 1 canonical validator block, found {len(blocks)}"; sys.argv = ["validator", "docs/review/phase-3-p3-4-submission.md", "--inject-false-path"]; exec(blocks[0], {"__name__": "__main__"})'
     ```
   - **Exit Code:** `1` (Non-zero exit)
   - **Complete Diagnostic Output (stderr):**
     ```text
     Traceback (most recent call last):
       File "<string>", line 1, in <module>
       File "<string>", line 146, in <module>
       File "<string>", line 79, in validate_submission_content
     AssertionError: Cited test file does not exist: tests/web/falsified_non_existent_file.py
     ```

2. **Negative Demonstration B (False Test Symbol in Real Test File):**
   - **Literal Command:**
     ```bash
     /opt/discord-bots/venv-web/bin/python -c 'import re, sys; doc = open("docs/review/phase-3-p3-4-submission.md", "r", encoding="utf-8").read(); blocks = re.findall(r"```python\n(# CANONICAL_SUBMISSION_VALIDATOR[\s\S]*?)\n```", doc); assert len(blocks) == 1, f"Expected 1 canonical validator block, found {len(blocks)}"; sys.argv = ["validator", "docs/review/phase-3-p3-4-submission.md", "--inject-false-symbol"]; exec(blocks[0], {"__name__": "__main__"})'
     ```
   - **Exit Code:** `1` (Non-zero exit)
   - **Complete Diagnostic Output (stderr):**
     ```text
     Traceback (most recent call last):
       File "<string>", line 1, in <module>
       File "<string>", line 146, in <module>
       File "<string>", line 82, in validate_submission_content
     AssertionError: Cited test function 'falsified_non_existent_symbol' is not a valid top-level test in tests/web/test_oauth_flow.py
     ```

3. **Negative Demonstration C (Prohibited Range Shorthand 'through'):**
   - **Literal Command:**
     ```bash
     /opt/discord-bots/venv-web/bin/python -c 'import re, sys; doc = open("docs/review/phase-3-p3-4-submission.md", "r", encoding="utf-8").read(); blocks = re.findall(r"```python\n(# CANONICAL_SUBMISSION_VALIDATOR[\s\S]*?)\n```", doc); assert len(blocks) == 1, f"Expected 1 canonical validator block, found {len(blocks)}"; sys.argv = ["validator", "docs/review/phase-3-p3-4-submission.md", "--inject-prohibited-shorthand"]; exec(blocks[0], {"__name__": "__main__"})'
     ```
   - **Exit Code:** `1` (Non-zero exit)
   - **Complete Diagnostic Output (stderr):**
     ```text
     Traceback (most recent call last):
       File "<string>", line 1, in <module>
       File "<string>", line 146, in <module>
       File "<string>", line 29, in validate_submission_content
     AssertionError: Prohibited range/shorthand found in traceability: ['through F-SEC']
     ```

4. **Extraction Coverage Demonstration (Unquoted Prose & Punctuation Extraction):**
   - **Literal Command:**
     ```bash
     /opt/discord-bots/venv-web/bin/python -c 'import re, sys; doc = open("docs/review/phase-3-p3-4-submission.md", "r", encoding="utf-8").read(); blocks = re.findall(r"```python\n(# CANONICAL_SUBMISSION_VALIDATOR[\s\S]*?)\n```", doc); assert len(blocks) == 1, f"Expected 1 canonical validator block, found {len(blocks)}"; sys.argv = ["validator", "docs/review/phase-3-p3-4-submission.md", "--check-unquoted-extraction"]; exec(blocks[0], {"__name__": "__main__"})'
     ```
   - **Exit Code:** `0`
   - **Actual Output (stdout):**
     ```text
     VALIDATION SUCCESS [mode: --check-unquoted-extraction]: 26 templates, 49 routes/mounts, 22 VMs, 193 test references (105 unique node IDs), 53 live candidates, 1 rename row, 3 static assets, 14 freeze assets verified cleanly.
     ```

### Codex Review Evidence (Bounded Check Statement)
Codex's bounded focused security/accessibility/structural check found no new implementation or focused-security blocker in the exercised surfaces (174 passed, 94 warnings in 8.75s, both manifests passing). It was not the requested complete independent implementation review or distinct security-focused review; both remain pending after submission correction.

---

## 7. Security and Accessibility Pass Summary

### Summary of Accepted Step 11 Accessibility Pass
- Documented in [`docs/review/phase-3-p3-4-step-11-accessibility-handoff.md`](../../docs/review/phase-3-p3-4-step-11-accessibility-handoff.md) and finalized in [`docs/review/phase-3-p3-4-step-11-3-final-verification-handoff.md`](../../docs/review/phase-3-p3-4-step-11-3-final-verification-handoff.md).
- Enforces strict semantic HTML landmarks (`<header>`, `<nav>`, `<main>`, `<footer>`, `<article>`), a skip-to-content link, explicit form label associations (`<label for="field_id">`), table accessibility (`<th>` scopes, data-label attributes for mobile cards), visible high-contrast focus rings (`:focus-visible`), and CSS motion minimization (`@media (prefers-reduced-motion)`).

### Summary of Accepted Step 12 Security Pass (R12-01 through R12-08)
- Documented in [`docs/review/phase-3-p3-4-step-12-security-and-progressive-enhancement-handoff.md`](../../docs/review/phase-3-p3-4-step-12-security-and-progressive-enhancement-handoff.md).
- **R12-01 & R12-05 (Hostile Rendering):** `assert_hostile_renders_inert` enforces exact container targeting, exact string equality, exact code-point sequence matching, exact bounds (`len(governed_text) == bound`), and template non-evaluation within governed containers.
- **R12-02 (Presentation Boundaries):** Real database models and ASGI endpoints exercise character names (R-21, R-22, R-31), audit event reasons (R-49, 200-char bound), reconciliation candidate names (R-43, 120-char bound), and closed-vocabulary query refusals.
- **R12-03 (Consolidated No-JS Validator):** Shared `validate_rendered_no_js_fallback` in `tests/web/no_js_helpers.py` verifies all 9 essential flows with `hx-*` stripped.
- **R12-04 & R12-06 (Safe Bodies & Correlation UUID):** Validates denial (401/403/404), validation (400/422), degraded (503), and safe error (500) responses. Enforces exactly one canonical lowercase hyphenated UUID inside `.reference-code` with zero child markup, comments, or leaked tracebacks/SQL.
- **R12-08 (Real Username/Global-Name Presentation Boundary):** Identified and tested the real Discord membership projection tables (`discord_users`, `discord_guild_memberships`) and `GET /v1/council/identity-search` (R-24), exercising all 7 hostile vectors, exact 80-char bounds (`DISCORD_NAME_BOUND=80`), and database constraint refusal on over-bound inputs.

---

## 8. Honest Not-Run Checks & Verification Limitations

The following checks could not be executed automatedly in the host environment and remain honestly classified as **NOT RUN**:

1. **TC-UI-01 & TC-UI-02 (Browser Automation & Visual Viewport Rendering):**
   - *Status:* **NOT RUN**.
   - *Reason:* No browser binary (Chrome, Chromium, Firefox) or automation framework (Playwright, Puppeteer, Selenium) is installed on the host.
   - *Owner:* Operator / Maintainer in a supported staging or local environment equipped with browser automation tooling.
2. **TC-UI-08 (Real-Device Responsive Layout Verification at 320px, 768px, 1280px, and 200% Zoom):**
   - *Status:* **NOT RUN — Peter/maintainer real-device acceptance**.
   - *Reason:* Requires physical hardware devices and browser layout engine inspection.
   - *Owner:* Peter Duscha (Acceptance Authority) / maintainers.
3. **TC-UI-09 (Screen-Reader & Assistive Technology Traversal):**
   - *Status:* **NOT RUN — Assistive-technology/screen-reader review**.
   - *Reason:* Requires human traversal using assistive technologies (e.g., NVDA, JAWS, VoiceOver, Orca).
   - *Owner:* Qualified accessibility specialist or maintainer review.

---

## 9. Active Blockers, Authoritative Residual Risks & Factual Bounds

### A. Active Blockers
- **Zero active implementation blockers:** All 2,168 web tests, 2,294 bot tests, 155 Node tests, 3 asset integrity checks, 14 visual freeze checks, and bytecode compilation checks pass cleanly with exit code 0.
- **Documentation Blockers (R13-01..R13-13):** Remediated in this document, `status.md`, and `change-log.md`, and submitted for independent re-review.

### B. Authoritative RAID Residual Risks
All risk definitions derive exclusively from `docs/project-management/raid-register.md`:
1. **R-22 (Backend Route / View-Model Contract Drift during Frontend Integration):**
   - Controlled by frozen typed view models (`application/web/view_models.py`, `vm-1`) and structural tests (TC-STRUCT-01, TC-STRUCT-02) asserting route and view model set equality against contract specifications.
2. **R-23 (Production Adaptation Regresses Accessibility Despite Accepted Static Prototype):**
   - Remains active because automated browser binaries (TC-UI-01/02), real hardware devices (TC-UI-08), and screen readers (TC-UI-09) are honestly Not Run. Controlled by static token checks, automated contrast ratios (48/48 PASS AA/AAA), semantic HTML invariants, and no-JS fallbacks.
3. **RR-17 (Commit Fence Row Write Lock Duration):**
   - The commit fence holds the job row write lock for the duration of the import `COMMIT`, blocking heartbeats and concurrent cancellations for that interval.
4. **RR-18 (Failed Recovery Publication Effect):**
   - A recovery publication that cannot succeed leaves the job `running` with a lapsed lease rather than writing `failed`, allowing operator intervention via runbook.
5. **RR-19 (Roll-Forward-Only Schema Boundary):**
   - While any retained reconciliation job records a committed apply effect, schema rollback below revision `0013` is unsupported and defects must be fixed by roll-forward.

### C. Factual Implementation & Presentation Bounds
These are factual implementation characteristics and are not assigned RAID risk identifiers:
1. **Character Name Presentation Bounding:** Character display names are bounded to 120 characters (`ACTOR_NAME_BOUND = 120`) in view-model presentation adapters; longer external names are safely truncated with ellipsis (`\u2026`).
2. **Single-Provider Identity Linking Constraint:** `GET /v1/account/identities/link/start` (R-36) answers HTTP 200 rendering `account_identities.html` with `additional_provider = "no_additional_provider"` and `state = "denied"` under the active single-provider Phase 3 policy.
3. **Application Static Asset Delivery:** Static assets under `/static/*` (M-01) are served directly by `freedom-web` (`adapters/web/static_assets.py`) with strict cache policies, same-origin CSP, and path traversal protection.

---

## 10. Independent Review Requests

Gemini formally requests:
1. **Independent Codex Implementation Review:**
   - A complete review of the corrected P3.4 frontend candidate, templates, route handlers, view models, candidate inventory, and test suites.
2. **Distinct Codex Security-Focused Review:**
   - A separate security review focusing specifically on autoescaping, CSP headers, correlation UUID handling, denial responses, hostile input boundaries, CSRF token handling, and no-JavaScript fallbacks.

---

## 11. Decision Requested from Peter Duscha (Acceptance Authority)

Upon completion and consideration of:
1. the independent Codex implementation review;
2. the distinct Codex security-focused review; and
3. any maintainer real-device inspections (TC-UI-08),

**Peter Duscha is requested to determine:**
> *Whether to formally accept Milestone P3.4, close Gate P3.G4, and authorize progression to the next milestone.*

*(Gemini makes no acceptance decision, does not self-close P3.G4, and makes no deployment claims.)*

---

## 12. Literal Ending `git status --short` (Post-Remediation Baseline)

```text
 M adapters/web/app.py
 M adapters/web/middleware.py
 M adapters/web/static/asset-integrity.sha256
RM adapters/web/static/css/freedom-blades.b0a1f3305683.css -> adapters/web/static/css/freedom-blades.58a9b9eed003.css
 M adapters/web/templates/audit_results.html
 M adapters/web/templates/audit_search.html
 M adapters/web/templates/base.html
 M adapters/web/templates/character_links.html
 M adapters/web/templates/council_characters.html
 M adapters/web/templates/council_snapshots.html
 M adapters/web/templates/error.html
 M adapters/web/templates/import_result.html
 M adapters/web/templates/includes/header.html
 M adapters/web/templates/job_status_fragment.html
 M adapters/web/templates/validation.html
 M application/web/audit_search.py
 M application/web/view_models.py
 M docs/contracts/phase-3-view-model-contract.md
 M docs/project-management/change-log.md
 M docs/project-management/status.md
 M "docs/review/Handover information"
 M tests/web/test_identity_migration_command.py
 M tests/web/test_oauth_refusal_audit.py
 M tests/web/test_p3_3_audit_search.py
 M tests/web/test_p3_3_disclosure_and_bounds.py
 M tests/web/test_p3_4_auth_and_system_views.py
 M tests/web/test_p3_4_council_character_views.py
 M tests/web/test_p3_4_identity_and_role_views.py
 M tests/web/test_p3_4_job_status_views.py
 M tests/web/test_p3_4_member_views.py
 M tests/web/test_p3_4_shell_and_components.py
 M tests/web/test_p3_4_snapshot_views.py
 M tests/web/test_security_controls.py
 M tests/web/test_static_asset_surface.py
?? docs/review/phase-3-p3-4-step-10-final-independent-review-and-acceptance.md
?? docs/review/phase-3-p3-4-step-11-1-scope-integrity-handoff.md
?? docs/review/phase-3-p3-4-step-11-2-focused-evidence-handoff.md
?? docs/review/phase-3-p3-4-step-11-3-final-verification-handoff.md
?? docs/review/phase-3-p3-4-step-11-accessibility-handoff.md
?? docs/review/phase-3-p3-4-step-12-security-and-progressive-enhancement-handoff.md
?? docs/review/phase-3-p3-4-submission.md
?? tests/web/no_js_helpers.py
?? tests/web/template_digests.py
?? tests/web/test_p3_4_accessibility.py
?? tests/web/test_p3_4_import_and_audit_views.py
?? tests/web/test_p3_4_security_and_escaping.py
```
