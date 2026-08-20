# Phase 3 package P3.4 Gemini readiness report — read-only frontend integration readiness analysis

**Prepared:** 2026-08-14
**Author:** Gemini (Production Frontend Implementer)
**Target Repository:** `/opt/discord-bots/freedom-bot`
**Sole Permitted Deliverable:** `docs/review/phase-3-p3-4-gemini-readiness-report.md`
**Status:** Planning and contract analysis only; **P3.4 implementation remains NO-GO**

---

## 1. Scope, authority and current no-go state

This document is the durable readiness analysis for the future Phase 3 package **P3.4** (production frontend integration). Its purpose is to make future P3.4 template, static asset, and HTMX integration work faster, safer, and strictly compliant with accepted platform contracts without changing any runtime behavior, accepted contract, frozen prototype asset, or gate state.

### 1.1 Scope and boundary

Package P3.4 encompasses the production Jinja2 base layouts, page templates, fragment partials, static CSS assets, vendored HTMX library, and frontend contract/accessibility test suite. P3.4 translates the accepted visual direction (`design-prototype/`) into production-owned templates rendered by `freedom-web` from pre-authorized view models.

This analysis is strictly **read-only planning and contract analysis**. It introduces zero production Jinja templates, partials, CSS, JavaScript, or HTMX attributes, and alters zero existing repository files outside this report.

### 1.2 Accountable project roles

Per `.agents/AGENTS.md` and `docs/review/phase-3-delivery-plan.md` §2:

| Role | Accountable Entity | Scope & Responsibilities |
|---|---|---|
| **Product Sponsor, Acceptance Authority, Product Owner, Data Owner, Operations Owner, Delivery Lead** | **Peter Duscha** | Accountable maintainer decisions, policy acceptances, visual/real-device approvals, and gate decisions. |
| **Backend Implementer & Working Technical Lead** | **Claude** | Packages P3.0–P3.3 and P3.5 backend implementation, route/view-model contracts, database models, and authorization services. |
| **Production Frontend Implementer** | **Gemini** | Package P3.4 production frontend integration against accepted contracts, accessibility compliance, and this readiness analysis. |
| **Independent Reviewer & Security Assistant** | **Codex** | Independent architecture, code, schema, contract, accessibility, and security-focused reviews. |

Neither Gemini nor Claude can approve their own work or close review gates; gate approval rests solely with Peter Duscha following Codex review.

### 1.3 Predecessor gate status and mandatory NO-GO decision

As of 2026-08-14:
- **P3.G0** (Contract and security baseline gate) is **CLOSED** (accepted by Peter Duscha on 2026-08-13).
- **P3.G1** (Authentication foundation gate) is **OPEN**. Package P3.1 was delivered, reviewed by Codex, remediated with OD-44 (migration `0009` durable completion binding) on 2026-08-14, and currently awaits Codex independent re-review and a distinct security pass.
- **P3.2** (Member reads, identity evidence, access administration) is **NOT IMPLEMENTED**. Gate **P3.G2** remains **OPEN**.
- **P3.3** (Council import, durable reconciliation jobs, audit views) is **NOT IMPLEMENTED**. Gate **P3.G3** remains **OPEN**.
- **P3.4 view-model freeze gates** (P3.G2 and P3.G3) have **NOT CLOSED**.

> [!IMPORTANT]
> **Authorization Disposition:** Gemini is **NOT AUTHORIZED** to begin P3.4 production frontend implementation. P3.4 implementation remains **NO-GO** until stop gates P3.G2 and P3.G3 are formally closed by Peter Duscha.

---

## 2. Sources read and precedence

This readiness analysis is derived from an exhaustive review of all eight required project sources:

1. **Governance & Roadmap:** `AGENTS.md`, `.agents/AGENTS.md`, and `docs/implementation-plan.md` (v1.5 baseline).
2. **Phase 3 Delivery Contract:** `docs/review/phase-3-delivery-plan.md` (accepted 2026-08-13), specifically §§3–5, P3.2–P3.5, P3.G2–P3.G4, §11 traceability, and §12 risks.
3. **Accepted Interface & Security Contracts:** `docs/contracts/README.md` and all ten Phase 3 contract specifications in order:
   - `phase-3-numeric-policy-register.md` (`N-01` through `N-67`)
   - `phase-3-route-authorization-contract.md` (`R-01` through `R-49`, `C-01` through `C-07`)
   - `phase-3-view-model-contract.md` (`VM-01` through `VM-21`, version `vm-1`)
   - `phase-3-logical-schema.md` (schema decision table & Alembic revisions `0006`–`0009`)
   - `phase-3-identity-migration-contract.md` (stages A–D and linkage evidence pipeline)
   - `phase-3-state-machines.md` (`SM-01` through `SM-07`)
   - `phase-3-threat-model.md` (`T-01` through `T-53`, `RR-01` through `RR-15`)
   - `phase-3-configuration-and-dependency-contract.md` (typed web config & 15 startup refusals)
   - `phase-3-operational-contract.md` (`freedom-web` & `freedom-worker` topology, kill switch)
   - `phase-3-test-traceability.md` (`TC-AUTH-01` through `TC-PERF-02`)
4. **Architecture Decisions:** `docs/adr/0010-provider-neutral-identity-and-emergency-administration.md` (accepted 2026-08-13).
5. **Visual Design Freeze:** `docs/review/phase-3-visual-prototype-handoff.md` and `docs/review/phase-3-visual-freeze-manifest.sha256` (14 frozen files verified).
6. **Frozen Visual Prototype Assets:** `design-prototype/` (all 14 HTML, CSS, JS, and PNG files, read-only).
7. **Project Governance Records:** `docs/project-management/status.md`, `decision-register.md`, `raid-register.md`, and `change-log.md` (including 2026-08-14 I-07/OD-44 and I-08/OD-45 rulings).
8. **Minimal Implementation Inventory:** `adapters/web/templates/` (minimal P3.1 contract templates for test execution only; not production templates).

### 2.1 Precedence hierarchy and discrepancy rule

When evaluating project documentation and implementation state, the following strict hierarchy of precedence applies:

```text
1. Explicit maintainer rulings (Peter Duscha) & change-log amendments
   └─▶ 2. Accepted Phase 3 contracts (docs/contracts/*) & ADR 0010
        └─▶ 3. Master Implementation Plan (docs/implementation-plan.md v1.5) & Delivery Plan
             └─▶ 4. Provisional current code implementations (application/, adapters/, web/)
                  └─▶ 5. Static design prototype (design-prototype/)
```

**Rule on Discrepancies:** Accepted contracts are authoritative. Current backend implementation files (`adapters/web/`, `application/web/`) are provisional until their owning gates close. Where current code and accepted contracts disagree, the discrepancy is documented as a finding or gap; code is never quietly treated as the source of truth, and frontend templates must never invent new behavior.

---

## 3. VM-01–VM-21 contract-to-screen matrix

The table below provides a disposition for every view model identifier from `VM-01` to `VM-21` defined in `phase-3-view-model-contract.md` (version `vm-1`). No view model is omitted or collapsed into a generic row.

| VM ID | View Model Name | Owning Package & Gate | Route / Response Source | Intended Full Page / Partial Pairing | Closest Frozen Prototype Source | Reusable Visual Patterns | Applicable States | Required Actions & Permitted Authority | Progressive Enhancement / No-JS Behavior | User-Controlled Text & Escaping | Bounds & Pagination Limits | Traceability Tests | Readiness Classification |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **VM-01** | `LoginPageView` | P3.1 / P3.G1 | `R-02` (`GET /v1/login`) | Full page | `login.html` | Card container, brand emblem, primary action button, alert banner | `ready`, `error`, `degraded`, `failure` | **Visitor / Unauthenticated.** Action: trigger OAuth start (`R-03`). | Standard `<a>` link to `R-03`; works without JS. | `SafeText` provider names; `LoginFailure` carries coarse code + correlation ID (`N-25`), never raw provider error string. | Max 1 provider (`discord`), `N-18` rate limit (10 starts / 10 min). | `TC-SEC-11`, `TC-UI-01`, `TC-VM-01` | `contract-fixed` |
| **VM-02** | `NonMemberView` | P3.1 / P3.G1 | `R-04` (`403` body) & any protected route in state `N` | Full page | `components.html` (denied alert) | Warning card, correlation callout, clear guidance prose | `denied` | **Caller State `N`** (Session held, guild membership lost). | Full static HTML render; works without JS. | Autoescaped `guild_display_name` (config); coarse `DeniedReason` enum (`not_a_member`). | Single record render. | `TC-SEC-11`, `TC-UI-02` | `contract-fixed` |
| **VM-03** | `ServiceDegradedView` | P3.1 / P3.G1 | Any protected route when `N-10` grace is exhausted (`503`) | Full page | `components.html` (error alert) | Alert card, system error badge, correlation UUID | `error` | **Any Authenticated Caller.** Fail closed when Discord/DB unavailable. | Full static HTML render; works without JS. | Autoescaped correlation UUID (`N-25`); subsystem enum (`identity_provider`, `database`). | Single record render. | `TC-SEC-11`, `TC-UI-02` | `contract-fixed` |
| **VM-04** | `EmergencyLoginView` | P3.1 / P3.G1 | `R-06` (`GET /v1/auth/emergency`) | Full page | `login.html` / `components.html` | Emergency banner, passkey section, recovery token form | `ready`, `failure` | **Visitor / Server Admin.** Actions: WebAuthn (`R-07`/`R-08`), Recovery grant (`R-09`). | Recovery form uses standard `POST /v1/auth/emergency/recovery` (works without JS). WebAuthn uses `fetch` JSON with JS. | Coarse failure codes (`invalid`, `expired`, `consumed`, `rate_limited`). Discloses no account/credential existence. | `N-32` (5 assertions / 10 min), `N-33` (3 recovery logins / 10 min). | `TC-SEC-11`, `TC-UI-01`, `TC-BG-10` | `contract-fixed` |
| **VM-05** | `MyCharactersView` | P3.2 / P3.G2 | `R-20` (`GET /v1/characters`) | Full page | `my-characters.html` | Card grid (`.card-grid`), portrait media box, default badge, access kind pill | `ready`, `empty` | **Guild Member (`M`, `C`, `CA`).** View owned/linked characters; nav to detail (`R-21`). | Standard HTML links to `R-21`; works without JS. | `SafeText` `display_name` (bounded 120 chars); short checksum (12 hex); null `level` renders "not recorded". | Max 50 characters, `truncated` flag, `N-21`. | `TC-UI-03`, `TC-VM-05` | `revalidate at P3.G2` |
| **VM-06** | `CharacterDetailView` | P3.2 / P3.G2 | `R-21` (`GET /v1/characters/{id}`) | Full page | `character-detail.html` | Stat grid, field profile table, portrait fallback, deferred migration badge | `ready` | **Character Owner (`obj`) or Council (`C`, `CA`).** Read-only character sheet. | Full static HTML render; no edit forms or POST routes exist. | `SafeText` `display_name` (120), `long_name` (240); `MigrationDeferred` renders `owning_package` from manifest, no value. | Max 200 snapshot fields, max 200 deferred fields, max 25 access facts. | `TC-UI-04`, `TC-VM-06` | `revalidate at P3.G2` |
| **VM-07** | `CouncilCharacterIndexView` | P3.2 / P3.G2 | `R-22` (`GET /v1/council/characters`) | Full page | `council-approval.html` (table layout) | Data table (`.table-container`), search/filter bar, pagination controls, unresolved owner alert | `ready`, `empty` | **Guild Council (`C`, `CA`).** Browse characters; nav to links admin (`R-23`). | Standard `GET` pagination links; works without JS. | `SafeText` character display name; `unresolved_owner` flag renders explicit warning. | Page size `N-21` (default 50, max 100), cursor pagination (`N-64`). | `TC-UI-05`, `TC-VM-07` | `revalidate at P3.G2` |
| **VM-08** | `CharacterLinksView` | P3.2 / P3.G2 | `R-23` (`GET /v1/council/characters/{id}/links`) | Full page (pairs with HTMX `R-24`) | `council-approval.html` (detail & diff queue) | Active/historical access table, grant form, revoke form, invariant warning alerts | `ready` | **Guild Council (`C`, `CA`).** Grant link (`R-25`), revoke (`R-26`), set default (`R-27`). | Forms submit via standard `POST` (works without JS). HTMX enhances identity search (`R-24`). | `SafeText` reason (bounded 500 chars); `discord_subject_display` Council-visible evidence only. | Max 25 active links, max 100 historical links, character `version` check. | `TC-UI-05`, `TC-VM-08` | `revalidate at P3.G2` |
| **VM-09** | `IdentitySearchResultsView` | P3.2 / P3.G2 | `R-24` (`GET /v1/council/identity-search`) | HTMX partial (pairs with `R-23`) | `council-approval.html` (search dropdown/table) | Candidate selection list, "names are not identity" warning banner | `ready`, `empty`, `invalid` | **Guild Council (`C`, `CA`).** Search Discord membership projection for grant candidate. | Progressive enhancement: without JS, operator manually inputs Discord snowflake into `R-25` grant form. | `SafeText` `query_echo` (bounded 120), `username` (80), `global_name` (80). | Max 25 candidates, query `q` ≥ 2 chars. | `TC-UI-05`, `TC-VM-09` | `revalidate at P3.G2` |
| **VM-10** | `IdentityMigrationView` | P3.2 / P3.G2 | `R-28` (`GET /v1/council/identity-migration`) | Full page | `none` (new visual work) | Proposal table, evidence side-by-side comparison, control totals summary header | `ready`, `empty` | **Guild Council (`C`, `CA`).** Confirm proposal (`R-29`), reject proposal (`R-30`). | Forms submit via standard `POST`; works without JS. | `SafeText` `sheet_player_name`, `sheet_discord_name`; candidate snowflakes. | Page size 50, max 100 proposals; control totals `MigrationTotals`. | `TC-UI-06`, `TC-VM-10` | `new visual work for P3.G4` |
| **VM-11** | `FieldProfileView` | P3.2 / P3.G2 | `R-31` (`GET /v1/council/field-profile`) | Full page | `reconciliation.html` (field profile tab) | Path mapping table, snapshot mode badges, deferred package column | `ready` | **Council (`C`, `CA`) & Admin (`A`, `CA`).** Read-only view of versioned field profile. | Full static HTML render; no write routes exist. | Fixed profile string keys; `owning_package` present only when deferred. | Max 500 paths, max 500 fields. | `TC-UI-07`, `TC-VM-11` | `revalidate at P3.G2` |
| **VM-12** | `RoleCapabilityView` | P3.2 / P3.G2 | `R-32` (`GET /v1/admin/role-capabilities`) | Full page | `none` (new visual work) | Mapping table, role snowflake, capability badge, provenance tag (`ordinary`/`emergency_continuity`), lockout guard alert | `ready` | **Platform Admin (`A`, `CA`, `BG`, `AC`).** Map role (`R-33`), revoke (`R-34`), ratify (`R-38`). | Form submissions use standard `POST`; works without JS. | `SafeText` `role_label` (presentation only); `provenance` & auth method tags. | Max `N-62` (50) mappings; `N-67` allowlist restricts `BG`/`AC`. | `TC-UI-08`, `TC-VM-12` | `new visual work for P3.G4` |
| **VM-13** | `AccountIdentitiesView` | P3.2 / P3.G2 | `R-35` (`GET /v1/account/identities`) | Full page | `none` (new visual work) | Identity list, active/retired status badges, current session indicator, unlink action | `ready` | **Any Authenticated User (`M`, `C`, `A`, `CA`, `BG`, `N`).** Unlink identity (`R-37`). | Form submission uses standard `POST`; works without JS. | `subject_display` shows caller's own snowflake in full; `retired` identities kept for audit. | Max 10 identities; unlink blocked if last usable identity (`N-16`). | `TC-UI-09`, `TC-VM-13` | `new visual work for P3.G4` |
| **VM-14** | `SnapshotListView` | P3.3 / P3.G3 | `R-40` (`GET /v1/council/snapshots`) | Full page | `reconciliation.html` | Snapshot table, metadata badges, folder select form, preview job trigger form | `ready`, `empty` | **Council (`C`, `CA`) & Admin (`A`, `CA`).** Admin selects folder (`R-41`); Council triggers preview (`R-42`). | Forms submit via standard `POST`; works without JS. | `SafeText` `world_title`, `folder_path`; short & full hex checksums. | Max 50 snapshots, max 50 selectable folders per snapshot. | `TC-UI-10`, `TC-VM-14` | `revalidate at P3.G3` |
| **VM-15** | `JobStatusView` | P3.3 / P3.G3 | `R-43` (full page) & `R-44` (HTMX poll fragment) | Full page (pairs with HTMX `R-44`) | `reconciliation.html` (progress step sequence & summary) | Progress bar/step sequence, summary stats, issue counts table, blocked entries list, cancel/apply forms | `ready`, `queued`, `running`, `completed`, `stale`, `failed`, `cancelled` | **Guild Council (`C`, `CA`).** View progress; cancel job (`R-45`); confirm apply (`R-46`). | `R-43` full page works via manual browser refresh. `R-44` HTMX fragment polls automatically with JS. | `SafeText` `display_name`; closed-vocabulary `ISSUE_CODES` (no raw artifact text forwarded). | Max 30 issue counts, max 50 blocked entries, poll interval `poll_after_seconds` ≥ `N-22` (2s). | `TC-UI-10`, `TC-VM-15` | `revalidate at P3.G3` |
| **VM-16** | `HealthView` | P3.1 / P3.G1 | `R-10` (`GET /healthz`) | `none` (JSON endpoint) | `none` (JSON API on loopback) | Machine JSON payload (`status`, `checks`, `version`, `environment`) | `ok`, `degraded` | **Operator / Loopback only (`127.0.0.1`).** Read operational health. | N/A (JSON API; not published by reverse proxy `N-50`). | No player data, no secrets, no DB connection strings. | Fixed check names (`database`, `migrations`, `expired_leases`, etc.). | `TC-SEC-11` | `contract-fixed` |
| **VM-17** | `ImportResultView` | P3.3 / P3.G3 | `R-47` (`GET /v1/council/imports/{id}`) | Full page | `reconciliation.html` (import receipt card) | Immutable receipt card, created/updated counters, issue summary table, duplicate notice | `ready` (`applied`/`refused`) | **Council (`C`, `CA`) & Admin (`A`, `CA`).** Read-only view of committed import receipt. | Full static HTML render; read-only navigation. | Full SHA-256 checksum; closed `ISSUE_CODES` summary; correlation UUID. | Single receipt record; duplicate submission returns original receipt (`duplicate_of`). | `TC-UI-10`, `TC-VM-17` | `revalidate at P3.G3` |
| **VM-18** | `AuditSearchView` | P3.3 / P3.G3 | `R-48` (full page) & `R-49` (HTMX partial) | Full page (pairs with HTMX `R-49`) | `none` (new visual work; table pattern from `council-approval.html`) | Filter form, event log table, structured before/after fact key-values, immutability notice banner | `ready`, `empty` | **Council (`C`, `CA`) & Admin (`A`, `CA`, `BG`, `AC`).** Search immutable audit events. | `R-48` form submits via `GET` (works without JS). `R-49` HTMX partial updates results table. | `SafeText` `entity_id`, fact `before`/`after` (bounded 200 chars); structured key-value triples only. | Page size `N-21` (default 50, max 100), `N-63` filters (max 5 simultaneous, max 120 chars, max 366 days). | `TC-UI-11`, `TC-VM-18` | `new visual work for P3.G4` |
| **VM-19** | `ConflictView` | P3.1 / P3.G1 | Any `409 Conflict` response | Full page | `components.html` (stale/conflict state) | Stale alert banner, embedded current state view, refresh action button | `stale` | **Any Caller.** Informed response when submitting stale version or preview. | Full static HTML render; offers link back to current state. | `conflict` enum (`stale_version`, `stale_preview`, `already_applied`, etc.); current VM embedded. | Single response render. | `TC-UI-02`, `TC-VM-19` | `contract-fixed` |
| **VM-20** | `SafeErrorView` | P3.1 / P3.G1 | Any `500 Internal Server Error` | Full page | `components.html` (error state) | Generic error card, prominent UUID correlation ID display, support guidance | `error` | **Any Caller.** Safe failure display. | Full static HTML render; works without JS. | `message_code = "unexpected_error"`; UUID correlation ID (`N-25`) ONLY. No stack traces, no SQL, no paths. | Single response render. | `TC-UI-02`, `TC-VM-20` | `contract-fixed` |
| **VM-21** | `ValidationView` | P3.1 / P3.G1 | Any `422 Unprocessable Entity` | Full page | `components.html` (form validation state) | Re-rendered form with inline field-level error messages and alert summary | `invalid` | **Any Caller.** Re-correct form input. | Full static HTML render; re-populates submitted form fields safely. | Field names, closed `FieldError` codes (`required`, `too_long`, `not_a_choice`, `not_found`, `not_permitted`, `malformed`). | Max 20 field errors per validation failure. | `TC-UI-02`, `TC-VM-21` | `contract-fixed` |

---

## 4. P3.1–P3.3 route and interaction inventory

The Phase 3 route set is **closed and exhaustive**. Per `phase-3-route-authorization-contract.md` §1: *A route that is not in §4–§6 of the route contract does not exist.*

### 4.1 Route inventory table

The table below maps every P3.1–P3.3 HTTP route and operator CLI command to its method, path, caller state matrix, capability, CSRF/Origin requirements, body limits, success responses, and refusal codes.

Caller states: `U` (Unauthenticated), `N` (Non-member session), `M` (Guild Member), `C` (Council), `A` (Platform Admin), `CA` (Council & Admin), `BG` (Break-glass), `AC` (Continuity-scoped Admin, behaves identically to `BG`).

| Route ID | Method | Path | Kind | Caller Permitted States | Capability Required | CSRF Req. | Origin Req. | Body Limit | Success Response & View Model | Refusal Code / Behavior |
|---|---|---|---|---|---|---|---|---|---|---|
| **R-01** | `GET` | `/` | Navigation | `U`, `N`, `M`, `C`, `A`, `CA`, `BG` | None | No | No | N/A | `303` to `/v1/characters` or `/v1/login` | None (static redirect) |
| **R-02** | `GET` | `/v1/login` | Navigation | `U`, `N`, `M`, `C`, `A`, `CA`, `BG` | None | No | No | N/A | `200` HTML (`VM-01`) | Authenticated callers redirected `303` to `/v1/characters` |
| **R-03** | `GET` | `/v1/auth/discord/start` | Navigation | `U`, `N`, `M`, `C`, `A`, `CA`, `BG` | None | No | No | N/A | `303` to Discord OAuth URL (`N-18` rate limit) | `429` if rate limited (`N-18`) |
| **R-04** | `GET` | `/auth/discord/callback` | Navigation | `U`, `N`, `M`, `C`, `A`, `CA`, `BG` | None | No | No | N/A | `303` to safe return path (`N-18` rate limit) | `403` rendering `VM-02` if non-member; safe error if state/cookie invalid |
| **R-05** | `POST` | `/v1/auth/logout` | Form | `N`, `M`, `C`, `A`, `CA`, `BG` | `guild_member` / `system` | **Yes** | **Yes** | 1 KiB | `303` to `/v1/login` | `401` if unauthenticated (`U`); `403` if CSRF/Origin mismatch |
| **R-06** | `GET` | `/v1/auth/emergency` | Navigation | `U`, `N`, `M`, `C`, `A`, `CA`, `BG` | None | No | No | N/A | `200` HTML (`VM-04`) | None |
| **R-07** | `POST` | `/v1/auth/emergency/webauthn/options` | Fetch JSON | `U`, `N`, `M`, `C`, `A`, `CA`, `BG` | `platform_administrator` target | No | **Yes** | 4 KiB | `200` JSON (WebAuthn options, `N-32` rate limit) | `429` if rate limited; `400` if invalid account |
| **R-08** | `POST` | `/v1/auth/emergency/webauthn/verify` | Fetch JSON | `U`, `N`, `M`, `C`, `A`, `CA`, `BG` | `platform_administrator` target | No | **Yes** | 16 KiB | `200` JSON (Creates `BG` session, `N-32` rate limit) | `400`/`401` rendering `VM-04` coarse failure |
| **R-09** | `POST` | `/v1/auth/emergency/recovery` | Form | `U`, `N`, `M`, `C`, `A`, `CA`, `BG` | `platform_administrator` target | No | **Yes** | 4 KiB | `303` to `/v1/admin/role-capabilities` (`BG` session) | `400`/`401` rendering `VM-04` coarse failure; `429` if rate limited (`N-33`) |
| **R-10** | `GET` | `/healthz` | Operator | Loopback `127.0.0.1` only | None | No | No | N/A | `200`/`503` JSON (`VM-16`) | Not published on public reverse proxy |
| **R-20** | `GET` | `/v1/characters` | Navigation | `M`, `C`, `CA` | `guild_member` | No | No | N/A | `200` HTML (`VM-05`) | `303` to `/v1/login` if `U`; `403` if `N`, `A`, `BG` |
| **R-21** | `GET` | `/v1/characters/{id}` | Navigation | `M` (`obj`), `C`, `CA` | `character_owner` / `guild_council` | No | No | N/A | `200` HTML (`VM-06`) | `303` to `/v1/login` if `U`; `404` if unlinked `M`, `N`, `A`, `BG` |
| **R-22** | `GET` | `/v1/council/characters` | Navigation | `C`, `CA` | `guild_council` | No | No | N/A | `200` HTML (`VM-07`) | `303` to `/v1/login` if `U`; `403` if `N`, `M`, `A`, `BG` |
| **R-23** | `GET` | `/v1/council/characters/{id}/links` | Navigation | `C`, `CA` | `guild_council` | No | No | N/A | `200` HTML (`VM-08`) | `303` to `/v1/login` if `U`; `403` if `N`, `M`, `A`, `BG`; `404` if absent |
| **R-24** | `GET` | `/v1/council/identity-search` | HTMX Partial | `C`, `CA` | `guild_council` | No | No | N/A | `200` HTML fragment (`VM-09`) | `401` if `U`; `403` if `N`, `M`, `A`, `BG` |
| **R-25** | `POST` | `/v1/council/characters/{id}/links` | Form | `C`, `CA` | `guild_council` | **Yes** | **Yes** | 8 KiB | `303` to `R-23` (Grant access link) | `401` if `U`; `403` if `N`, `M`, `A`, `BG`; `409` if stale `version` (`VM-19`) |
| **R-26** | `POST` | `/v1/council/characters/{id}/links/{access_id}/revoke` | Form | `C`, `CA` | `guild_council` | **Yes** | **Yes** | 4 KiB | `303` to `R-23` (Revoke access link) | `401` if `U`; `403` if `N`, `M`, `A`, `BG` |
| **R-27** | `POST` | `/v1/council/characters/{id}/links/{access_id}/default` | Form | `C`, `CA` | `guild_council` | **Yes** | **Yes** | 4 KiB | `303` to `R-23` (Set default character) | `401` if `U`; `403` if `N`, `M`, `A`, `BG` |
| **R-28** | `GET` | `/v1/council/identity-migration` | Navigation | `C`, `CA` | `guild_council` | No | No | N/A | `200` HTML (`VM-10`) | `303` to `/v1/login` if `U`; `403` if `N`, `M`, `A`, `BG` |
| **R-29** | `POST` | `/v1/council/identity-migration/{proposal_id}/confirm` | Form | `C`, `CA` | `guild_council` | **Yes** | **Yes** | 8 KiB | `303` to `R-28` (Confirm link proposal) | `401` if `U`; `403` if `N`, `M`, `A`, `BG`; `422` if ambiguous |
| **R-30** | `POST` | `/v1/council/identity-migration/{proposal_id}/reject` | Form | `C`, `CA` | `guild_council` | **Yes** | **Yes** | 8 KiB | `303` to `R-28` (Reject link proposal) | `401` if `U`; `403` if `N`, `M`, `A`, `BG` |
| **R-31** | `GET` | `/v1/council/field-profile` | Navigation | `C`, `A`, `CA` | `guild_council` / `platform_administrator` | No | No | N/A | `200` HTML (`VM-11`) | `303` to `/v1/login` if `U`; `403` if `N`, `M`, `BG` |
| **R-32** | `GET` | `/v1/admin/role-capabilities` | Navigation | `A`, `CA`, `BG`, `AC` | `platform_administrator` | No | No | N/A | `200` HTML (`VM-12`) | `303` to `/v1/login` if `U`; `403` if `N`, `M`, `C` |
| **R-33** | `POST` | `/v1/admin/role-capabilities` | Form | `A`, `CA`, `BG` (`N-67`), `AC` (`N-67`) | `platform_administrator` | **Yes** | **Yes** | 4 KiB | `303` to `R-32` (Create role mapping) | `401` if `U`; `403` if `N`, `M`, `C`; `403 emergency_scope_refused` if `BG`/`AC` non-admin capability |
| **R-34** | `POST` | `/v1/admin/role-capabilities/{id}/revoke` | Form | `A`, `CA`, `BG` (`N-67`), `AC` (`N-67`) | `platform_administrator` | **Yes** | **Yes** | 4 KiB | `303` to `R-32` (Revoke role mapping) | `401` if `U`; `403` if `N`, `M`, `C`; `403` if protected bootstrap mapping; `403 emergency_scope_refused` if `BG`/`AC` non-admin capability |
| **R-35** | `GET` | `/v1/account/identities` | Navigation | `N`, `M`, `C`, `A`, `CA`, `BG` | `guild_member` / `platform_administrator` | No | No | N/A | `200` HTML (`VM-13`) | `303` to `/v1/login` if `U` |
| **R-36** | `GET` | `/v1/account/identities/link/start` | Navigation | `N`, `M`, `C`, `A`, `CA` | `guild_member` / `platform_administrator` | No | No | N/A | `303` to provider (`VM-13` `no_additional_provider` in P3) | `303` to `/v1/login` if `U`; `403` if `BG` |
| **R-37** | `POST` | `/v1/account/identities/{id}/unlink` | Form | `N`, `M`, `C`, `A`, `CA` | `guild_member` / `platform_administrator` | **Yes** | **Yes** | 4 KiB | `303` to `R-35` (Unlink external identity) | `401` if `U`; `403` if `BG`; `403` if last usable identity (`N-16`) |
| **R-38** | `POST` | `/v1/admin/role-capabilities/{id}/ratify` | Form | `A`, `CA` | `platform_administrator` (`full` scope only) | **Yes** | **Yes** | 4 KiB | `303` to `R-32` (Ratify emergency mapping) | `401` if `U`; `403` if `N`, `M`, `C`; `403` if `BG` / `AC` (emergency scope cannot ratify) |
| **R-40** | `GET` | `/v1/council/snapshots` | Navigation | `C`, `A`, `CA` | `guild_council` / `platform_administrator` | No | No | N/A | `200` HTML (`VM-14`) | `303` to `/v1/login` if `U`; `403` if `N`, `M`, `BG` |
| **R-41** | `POST` | `/v1/admin/snapshots/{id}/folder` | Form | `A`, `CA` | `platform_administrator` | **Yes** | **Yes** | 4 KiB | `303` to `R-40` (Sets folder, invalidates previews) | `401` if `U`; `403` if `N`, `M`, `C` (Council alone cannot select folder), `BG` |
| **R-42** | `POST` | `/v1/council/snapshots/{id}/preview-jobs` | Form | `C`, `CA` | `guild_council` | **Yes** | **Yes** | 4 KiB | `303` to `R-43` (Enqueues preview job) | `401` if `U`; `403` if `N`, `M`, `A` (Admin alone cannot preview), `BG`; `422` if folder unselected |
| **R-43** | `GET` | `/v1/council/jobs/{id}` | Navigation | `C`, `CA` | `guild_council` | No | No | N/A | `200` HTML (`VM-15`) | `303` to `/v1/login` if `U`; `403` if `N`, `M`, `A`, `BG`; `403` if object unauthorized |
| **R-44** | `GET` | `/v1/council/jobs/{id}/status` | HTMX Poll | `C`, `CA` | `guild_council` | No | No | N/A | `200` HTML fragment (`VM-15`, `N-22` poll) | `401` if `U`; `403` if `N`, `M`, `A`, `BG`; `403` before job lookup if unauthorized |
| **R-45** | `POST` | `/v1/council/jobs/{id}/cancel` | Form | `C`, `CA` | `guild_council` | **Yes** | **Yes** | 4 KiB | `303` to `R-43` (Cancel non-terminal job) | `401` if `U`; `403` if `N`, `M`, `A`, `BG`; `409` if already committed |
| **R-46** | `POST` | `/v1/council/jobs/{id}/apply` | Form | `C`, `CA` | `guild_council` | **Yes** | **Yes** | 8 KiB | `303` to `R-43` (Enqueues atomic apply job) | `401` if `U`; `403` if `N`, `M`, `A`, `BG`; `409` if preview stale (`VM-19`) |
| **R-47** | `GET` | `/v1/council/imports/{id}` | Navigation | `C`, `A`, `CA` | `guild_council` / `platform_administrator` | No | No | N/A | `200` HTML (`VM-17`) | `303` to `/v1/login` if `U`; `403` if `N`, `M`, `BG`; `404` if absent |
| **R-48** | `GET` | `/v1/audit` | Navigation | `C`, `A`, `CA`, `BG`, `AC` | `guild_council` / `platform_administrator` | No | No | N/A | `200` HTML (`VM-18`) | `303` to `/v1/login` if `U`; `403` if `N`, `M` |
| **R-49** | `GET` | `/v1/audit/results` | HTMX Partial | `C`, `A`, `CA`, `BG`, `AC` | `guild_council` / `platform_administrator` | No | No | N/A | `200` HTML fragment (`VM-18`) | `401` if `U`; `403` if `N`, `M` |
| **C-01** | CLI | `python -m tools.emergency_recovery issue` | Operator | Host shell | Host authority | N/A | N/A | N/A | Prints recovery token once; stores SHA-256 hash | Host permission denied if not host operator |
| **C-02** | CLI | `python -m tools.emergency_recovery revoke` | Operator | Host shell | Host authority | N/A | N/A | N/A | Revokes outstanding recovery grants | Host permission denied |
| **C-03** | CLI | `python -m tools.webauthn_enrollment` | Operator | Host shell | Host authority | N/A | N/A | N/A | Enrolls / retires break-glass passkey credential | Refuses if fewer than 2 credentials remain (`N-13`) |
| **C-04** | CLI | `python -m tools.identity_migration --dry-run --player-tab Players` | Operator | Separate temporary migration environment | Host authority | N/A | N/A | N/A | Reads the confirmed one-time legacy tab through the read-only boundary and produces linkage proposals; writes no access rows and never writes Google | Proposal/control-total transaction; Council confirmation at R-29 activates one link immediately |
| **C-05 (withdrawn)** | — | — | — | — | — | — | — | — | Retired by OD-46 / `C-P3.2-A`; there is no deferred materialization command | — |
| **C-06** | CLI | `python -m tools.portal_kill_switch on\|off` | Operator | Host shell | Host authority | N/A | N/A | N/A | Toggles portal kill switch (`N-56`) | Host permission denied |
| **C-07** | CLI | `python -m tools.session_revoke --account ...` | Operator | Host shell | Host authority | N/A | N/A | N/A | Revokes all active sessions for an account | Database update + audit event |

### 4.2 Specific interaction constraints

1. **Fragment / Full-Page Pairings:** Every HTMX fragment route has an exact full-page fallback:
   - `R-44` (`GET /v1/council/jobs/{id}/status`) is the fragment for `R-43` (`GET /v1/council/jobs/{id}`).
   - `R-49` (`GET /v1/audit/results`) is the fragment for `R-48` (`GET /v1/audit`).
   - `R-24` (`GET /v1/council/identity-search`) is the fragment for `R-23` (`GET /v1/council/characters/{id}/links`).
   A user without JavaScript receives the full page (`R-43`, `R-48`, `R-23`) with static forms/links and complete operational capability.
2. **Pre-authorized Control Rendering:** Mutation controls (`R-25`, `R-26`, `R-27`, `R-29`, `R-30`, `R-33`, `R-34`, `R-38`, `R-41`, `R-42`, `R-45`, `R-46`, `R-37`) must only be rendered when pre-authorized by server-side view-model flags (e.g., `confirmable`, `revocable`, `can_select_folder`, `can_preview`). Hiding controls is a UI courtesy; server-side capability resolution enforces authorization regardless of template presentation.
3. **Polling Constraints:** `R-44` polling respects `poll_after_seconds` (≥ `N-22` / 2 seconds). Server responds with `Retry-After` headers if needed. Polling stops immediately when `job_state` reaches a terminal state (`completed`, `stale`, `failed`, `cancelled`).
4. **Optimistic Concurrency & Reasons:**
   - Forms requiring optimistic version checks: `R-25` (character `version`), `R-38` (mapping `version`), `R-46` (job `preview_token` & versions).
   - Forms requiring non-blank reasons: `R-25` (link grant reason), `R-26` (link revoke reason), `R-30` (proposal rejection reason), `R-37` (identity unlink reason), `R-38` (ratification reason). All reasons are bounded at 500 characters and validated server-side (`422`).
5. **Object Substitution & Oracle Protections:**
   - `R-21` returns `404` for unauthorized character requests (byte-identical to nonexistent characters).
   - `R-43`/`R-44` return `403` on caller capability *before* job lookup to prevent job existence probing.
   - `R-48`/`R-49` pagination cursors are HMAC-signed opaque tokens (`N-64`) preventing offset scanning.
   - `R-24` candidate searches display non-identity warning banners (`OD-42`) and output snowflakes for server-side resolution.
6. **OD-45 Direct-HTTP Readiness Gate:** Direct-HTTP test cases for `R-33`, `R-34`, and `R-38` (`TC-BG-05b`, `TC-BG-05c`, `TC-BG-05e` direct-HTTP portions) belong to gate **P3.G2** per the 2026-08-14 `I-08` ruling. They are mandatory blocking evidence at P3.G2 before P3.4 frontend templates consume those routes.

---

## 5. Frozen-design adaptation map

The accepted visual direction is frozen under `design-prototype/` (14 files verified against `phase-3-visual-freeze-manifest.sha256`). P3.4 adapts the visual patterns into production Jinja templates and static CSS assets.

> [!WARNING]
> **Boundary Rule:** No file under `design-prototype/` may be copied, moved, imported, or served directly by `freedom-web`. Production assets live in `adapters/web/static/` and `adapters/web/templates/`.

### 5.1 Design token & primitive inventory

All 71 accepted CSS design tokens from `design-prototype/css/tokens.css` are reimplemented in production static CSS (`adapters/web/static/css/tokens.css`):

- **Color System:** Dark metallic background (`--fb-color-bg: #0b0f19`), forged-steel surface (`--fb-color-surface: #111827`), subtle panel border (`--fb-color-border: #1f2937`), steel-blue primary accent (`--fb-color-primary: #3b82f6` / `--fb-color-primary-hover: #60a5fa`), status alert colors (success `#10b981`, warning `#f59e0b`, danger `#ef4444`, info `#6366f1`).
- **Typography:** System font stack (`Inter`, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `Roboto`, `sans-serif`), fixed scale (`--fb-text-xs: 0.75rem` through `--fb-text-3xl: 1.875rem`), font weights (400, 500, 600, 700).
- **Layout Primitives:** Two-level header structure (Level 1 brand emblem row + user role pill; Level 2 primary navigation bar `#main-nav-menu`), 7-destination nav grid, responsive card grid (`.card-grid` with `repeat(auto-fit, minmax(min(100%, 270px), 1fr))`), horizontally scrollable table container (`.table-container` with `overflow-x: auto`), blade-divider motif (`.fb-blade-divider` with `--fb-color-blade-line`).
- **Focus Ring & Motion:** High-contrast focus ring (`--fb-focus-ring: 2px solid #60a5fa`, `outline-offset: 2px`), smooth transitions (150ms ease), reduced-motion override (`0.01ms` duration under `prefers-reduced-motion: reduce`).

### 5.2 Production screen adaptation mapping

| Production Screen | Owning View Models | Closest Frozen Prototype Source | Required Adaptation |
|---|---|---|---|
| **Sign In** | `VM-01`, `VM-04` | `design-prototype/login.html` | Adapt form layout, brand emblem, provider OAuth start button (`R-03`), emergency login link (`R-06`), degraded provider banner (`VM-01`), and WebAuthn/recovery grant forms (`VM-04`). |
| **My Characters** | `VM-05` | `design-prototype/my-characters.html` | Adapt character card grid, 16:9 portrait media box with initials fallback, level display (`None` -> "not recorded"), default character badge, access kind pill (`owner`, `co_owner`, `delegate`, `viewer`), and empty state illustration. |
| **Character Detail** | `VM-06` | `design-prototype/character-detail.html` | Adapt character header, stat block, access history table, snapshot field key-value table, deferred migration badges (`MigrationDeferred` with owning package name), and non-interactive portrait fallback. |
| **Snapshot List & Import** | `VM-14`, `VM-15`, `VM-17` | `design-prototype/reconciliation.html` | Adapt snapshot table, folder selection dropdown (`R-41`), preview trigger form (`R-42`), 3-step progress sequence (`.progress-step-row` stacking to 1 column on mobile), issue counts table, blocked entries list, and import receipt summary card (`R-47`). |
| **Council Character Index & Links** | `VM-07`, `VM-08`, `VM-09` | `design-prototype/council-approval.html` | Adapt character list table, access management panel, grant/revoke forms, optimistic concurrency alerts, and HTMX identity search candidate list (`VM-09`) with non-identity warning banner. |
| **Field Profile** | `VM-11` | `design-prototype/reconciliation.html` (tab 2) | Adapt path/field classification table, snapshot mode badges (`snapshot-only`, `reported`, `ignored`), database authority vs deferred badges, and owning package indicators. |
| **Identity Migration** | `VM-10` | `none` (new visual work) | **New Screen:** Adapt table and alert visual patterns from `council-approval.html`. Implement side-by-side evidence comparison (Sheet player name vs Discord subject), control totals header (`MigrationTotals`), and confirm/reject forms (`R-29`/`R-30`). |
| **Role Capabilities** | `VM-12` | `none` (new visual work) | **New Screen:** Adapt table and badge patterns. Implement role snowflake input, capability selector, protected bootstrap mapping alert banner, provenance tags (`ordinary` vs `emergency_continuity`), and ratify button (`R-38`). |
| **Account Identities** | `VM-13` | `none` (new visual work) | **New Screen:** Adapt card and list patterns. Implement linked identities list, active/retired status badges, current session indicator, unlink action form (`R-37`), and "last usable identity" lockout protection alert. |
| **Audit Search** | `VM-18` | `none` (new visual work) | **New Screen:** Adapt filter bar from `council-approval.html` and data table patterns. Implement 5-filter search form, cursor pagination controls, structured before/after fact key-value pairs, and immutability notice banner. |

---

## 6. Four new-screen semantic outlines

Four production screens have no direct frozen prototype page in `design-prototype/`. The Phase 6 `council-approval.html` queue pattern **must not** be repurposed as a Phase 3 workflow. The semantic outlines below establish the visual structure using accepted design tokens and components.

### 6.1 VM-10: Identity Migration (`council_identity_migration`)

- **Route & View Model:** `R-28` (`GET /v1/council/identity-migration`), `VM-10` (`IdentityMigrationView`).
- **Semantic Structure:**
  ```html
  <header class="fb-page-header">
    <h1>Identity Link Migration</h1>
    <p class="fb-lead">Review and confirm legacy Sheet-era character ownership evidence into platform access links.</p>
  </header>
  <section class="fb-summary-cards" aria-label="Control Totals">
    <!-- MigrationTotals summary: source_characters, source_players, proposed, ambiguous, confirmed, rejected -->
  </section>
  <main class="fb-main-content">
    <div class="fb-blade-divider" role="separator"><span class="fb-blade-divider-mark">Migration Proposals</span></div>
    <div class="table-container">
      <table class="fb-data-table">
        <thead>
          <tr>
            <th>Character</th>
            <th>Sheet Evidence (Player / Discord / DM)</th>
            <th>Proposed Discord Identity</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <!-- Loop over proposals; render SafeText, candidate subjects, confirm/reject forms -->
        </tbody>
      </table>
    </div>
  </main>
  ```
- **Reusability & Controls:** Uses `.fb-summary-cards`, `.table-container`, `.fb-blade-divider`. Forms for `R-29` (confirm) and `R-30` (reject) submit via standard `POST`. Requires Peter's visual acceptance at P3.G4.

### 6.2 VM-12: Role-Capability Administration (`admin_role_capabilities`)

- **Route & View Model:** `R-32` (`GET /v1/admin/role-capabilities`), `VM-12` (`RoleCapabilityView`).
- **Semantic Structure:**
  ```html
  <header class="fb-page-header">
    <h1>Role-Capability Administration</h1>
    <div class="fb-badge-group">
      <span class="fb-badge fb-badge-info">Scope: {{ vm.administrator_scope }}</span>
      {% if vm.unratified_count > 0 %}<span class="fb-badge fb-badge-warning">{{ vm.unratified_count }} Emergency Mappings Unratified</span>{% endif %}
    </div>
  </header>
  {% if vm.administrator_scope == 'emergency_continuity' %}
  <div class="fb-alert fb-alert-warning" role="alert">
    <p><strong>Emergency Continuity Scope Active:</strong> Mapping changes are restricted to the <code>platform_administrator</code> capability under rule N-67.</p>
  </div>
  {% endif %}
  <main class="fb-main-content">
    <section class="fb-card">
      <h2>Map New Role Capability</h2>
      <form action="/v1/admin/role-capabilities" method="POST">
        <input type="hidden" name="csrf_token" value="{{ vm.csrf_token }}">
        <!-- Role Snowflake input, Capability select dropdown, Submit button -->
      </form>
    </section>
    <div class="table-container">
      <table class="fb-data-table">
        <thead>
          <tr><th>Role Snowflake</th><th>Label</th><th>Capability</th><th>Provenance</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <!-- Loop mappings; render protected status, provenance tags, revoke/ratify forms -->
        </tbody>
      </table>
    </div>
  </main>
  ```
- **Reusability & Controls:** Protected bootstrap mapping renders `revocable = false` and warning alert. `R-38` ratify button rendered only when `ratifiable = true`. Requires Peter's visual acceptance at P3.G4.

### 6.3 VM-13: Account Identities (`account_identities`)

- **Route & View Model:** `R-35` (`GET /v1/account/identities`), `VM-13` (`AccountIdentitiesView`).
- **Semantic Structure:**
  ```html
  <header class="fb-page-header">
    <h1>Account Identities & Security</h1>
  </header>
  <main class="fb-main-content">
    <section class="fb-card">
      <h2>Linked External Identities</h2>
      <ul class="fb-identity-list">
        {% for id in vm.identities %}
        <li class="fb-identity-item">
          <div>
            <strong>{{ id.provider_display_name }}</strong> ({{ id.subject_display }})
            {% if id.is_current_session_identity %}<span class="fb-badge fb-badge-success">Current Session</span>{% endif %}
            <span class="fb-badge fb-badge-secondary">{{ id.state }}</span>
          </div>
          {% if id.state == 'active' and not id.is_current_session_identity %}
          <form action="/v1/account/identities/{{ id.identity_id }}/unlink" method="POST">
            <input type="hidden" name="csrf_token" value="{{ vm.csrf_token }}">
            <button type="submit" class="btn btn-danger btn-sm">Unlink</button>
          </form>
          {% endif %}
        </li>
        {% endfor %}
      </ul>
    </section>
  </main>
  ```
- **Reusability & Controls:** Renders full snowflake for caller's own account. Unlink form submits via `POST /v1/account/identities/{id}/unlink`. Requires Peter's visual acceptance at P3.G4.

### 6.4 VM-18: Audit Search (`audit_search`)

- **Route & View Model:** `R-48` (`GET /v1/audit`), `R-49` (HTMX partial), `VM-18` (`AuditSearchView`).
- **Semantic Structure:**
  ```html
  <header class="fb-page-header">
    <h1>Platform Audit Log</h1>
    <div class="fb-alert fb-alert-info" role="status">
      <p>Audit entries are immutable and append-only. Corrections are made through explicit compensating actions.</p>
    </div>
  </header>
  <main class="fb-main-content">
    <section class="fb-card fb-filter-card">
      <form action="/v1/audit" method="GET" hx-get="/v1/audit/results" hx-target="#audit-results-container" hx-swap="outerHTML">
        <!-- Action prefix, Entity type, Entity ID, Capability select, Source select, Time range inputs -->
        <button type="submit" class="btn btn-primary">Filter Audit Log</button>
      </form>
    </section>
    <div id="audit-results-container" class="table-container">
      <table class="fb-data-table">
        <thead>
          <tr><th>Timestamp (UTC)</th><th>Actor</th><th>Capability</th><th>Action</th><th>Entity</th><th>Facts</th></tr>
        </thead>
        <tbody>
          <!-- Loop audit rows; render structured key/before/after facts only -->
        </tbody>
      </table>
      <!-- Cursor pagination controls (N-21 / N-64) -->
    </div>
  </main>
  ```
- **Reusability & Controls:** Structured key-value fact list (no raw JSON/bytes). Form works without JS (standard `GET`), enhanced with HTMX `hx-get="/v1/audit/results"`. Requires Peter's visual acceptance at P3.G4.

---

## 7. Accessibility and responsive acceptance plan

P3.4 implementation must adhere strictly to WCAG 2.1 Level AA standards, responsive reflow requirements, and progressive enhancement principles.

### 7.1 Testable accessibility & responsive checklist

| Category | Requirement & Standard | Implementation Rule | Traceability ID | Verification Method |
|---|---|---|---|---|
| **Landmarks & Structure** | Semantic HTML5 elements | Exactly one `<main>`, `<header>`, `<footer>`, `<nav>` per page. Headings hierarchy `<h1>` -> `<h2>` -> `<h3>` with no skipped levels. | `TC-UI-01`..`11` | Source review & automated DOM audit |
| **Labels & Associations** | Input labeling & error binding | Every form control has an explicit `<label for="...">`. Inline errors bound via `aria-invalid="true"` and `aria-describedby="err-id"`. | `TC-UI-02` | Source review & automated DOM audit |
| **Keyboard Navigation** | Complete keyboard operability | All interactive elements (links, buttons, forms) focusable via `Tab`. Logical tabbing order matching visual flow. | `TC-UI-01`..`11` | Manual keyboard pass & automated audit |
| **Visible Focus** | Distinct focus ring | High-contrast focus outline (`outline: 2px solid #60a5fa`, `outline-offset: 2px`). `outline: none` strictly forbidden unless custom focus ring supplied. | `TC-UI-01`..`11` | Source review & visual inspection |
| **Skip Links** | Skip to main content | Top-level skip link `<a href="#main-content" class="skip-link">Skip to main content</a>` as first focusable element. | `TC-UI-01` | Source review & keyboard pass |
| **Focus Management** | Post-action focus placement | Focus placed on first invalid input after `422` validation failure; focus returned to trigger button after native `<dialog>` closure. | `TC-UI-02`, `TC-UI-04` | Automated browser check |
| **Screen Announcements** | Non-disruptive status updates | HTMX swaps and status changes use `role="status"` or `aria-live="polite"`. High-priority errors use `role="alert"` / `aria-live="assertive"`. | `TC-UI-02`, `TC-UI-10` | Source review |
| **Modal Dialogs** | Native `<dialog>` behavior | Native `<dialog id="portrait-preview-dialog">` with `.showModal()`. Focus trapped inside modal, Escape key closes modal, focus returned to trigger. | `TC-UI-04` | Automated browser check |
| **Table Responsiveness** | Responsive tabular data | Tables wrapped in `<div class="table-container">` with `overflow-x: auto`. No content truncated or hidden without accessible alternative. | `TC-UI-05`..`11` | Viewport testing (320px) |
| **Responsive Viewports** | 320px, 768px, 1280px layouts | 320px: 1-column layout, touch targets ≥ 44px × 44px. 768px: 4-column nav, 2-column cards. 1280px: full 7-column nav, multi-column grids. | `TC-UI-01`..`11` | Multi-viewport automated checks & Peter's real-device check |
| **Zoom & Text Spacing** | 200% zoom reflow | Page reflows cleanly at 200% zoom without horizontal scrolling for main text containers. Line height ≥ 1.5, paragraph spacing ≥ 2× font size. | `TC-UI-01`..`11` | Viewport & zoom check |
| **Reduced Motion** | Motion sensitivity override | `@media (prefers-reduced-motion: reduce)` sets transition durations to `0.01ms` while preserving static focus rings. | `TC-UI-01`..`11` | CSS audit |
| **Color Contrast** | WCAG AA contrast ratios | Normal text ≥ 4.5:1, large text ≥ 3:1, UI controls/borders ≥ 3:1 against background. Checked via `calc_contrast.py`. | `TC-UI-01`..`11` | Source-derived contrast matrix |
| **No-JavaScript Operation** | Progressive enhancement | 100% of essential flows (login, character viewing, link management, migration confirmation, job status check, audit search) complete without JS. | `TC-UI-01`..`11` | Automated browser pass with JS disabled |

### 7.2 Evidence classification matrix for accessibility

| Evidence Item | Scope & Method | Classification | Required Executant / Reviewer |
|---|---|---|---|
| **Jinja Template Semantics & ARIA** | Source audit of HTML tags, ARIA attributes, IDs | `automated (source audit)` | Gemini automated suite / Codex review |
| **CSS Token & Contrast Conformance** | `calc_contrast.py` & token contract verification | `automated (source audit)` | Gemini automated suite |
| **No-JS Functional Completion** | Playwright test suite with `javaScriptEnabled: false` | `automated (browser)` | Gemini automated suite / Codex review |
| **Viewport Reflow (320, 768, 1280px)** | Playwright automated screenshot & layout assertions | `automated (browser)` | Gemini automated suite |
| **Keyboard Focus & Trapping** | Playwright keyboard navigation and focus tracking | `automated (browser)` | Gemini automated suite |
| **Real-Mobile Physical Inspection** | Physical mobile device testing (header, menu, touch) | `real-device` | **Peter Duscha** (Acceptance Authority) |
| **Maintainer Visual Acceptance** | Aesthetic review across all production screens | `maintainer visual inspection` | **Peter Duscha** (Acceptance Authority) |
| **Assistive Technology Traversal** | Screen reader audio traversal (VoiceOver / NVDA) | `assistive-technology` | Explicitly unrun / pending maintainer testing |

---

## 8. Security-preserving template checklist

Frontend Jinja templates must preserve all backend security guarantees. Templates cannot grant authority; hidden controls do not replace direct-HTTP authorization enforcement.

### 8.1 Implementation checklist

1. **Jinja2 Autoescaping Mandatory:** Autoescaping enabled for all `.html` / `.html.j2` files (`TC-SEC-11`). Zero `|safe` usages across the entire template codebase.
2. **Static HTMX Attributes Only:** HTMX attributes limited to static strings (`hx-get`, `hx-post`, `hx-target`, `hx-swap`, `hx-headers`). Strict prohibition of `hx-on:` handlers (inline script).
3. **No Inline Scripts or Event Handlers:** No `<script>` blocks carrying server values, no inline event handlers (`onclick=`, `onchange=`), no inline `style=` attributes (violates CSP `N-26`).
4. **Synchronizer CSRF Tokens:** All `POST` forms include `<input type="hidden" name="csrf_token" value="{{ vm.csrf_token }}">` (`N-17`). HTMX requests include CSRF token via `hx-headers`.
5. **CSP Compatibility:** Templates strictly compatible with `N-26` CSP (`default-src 'self'; script-src 'self'; style-src 'self'`). No remote fonts, CDN scripts, or external images.
6. **Safe URL Generation:** All navigation links and form targets use `url_for`-style route helpers with typed parameters (UUIDs, enums). No string concatenation of user-supplied paths.
7. **Safe Image Fallbacks:** Character portraits use metadata fallbacks with SVG initials (`CharacterPortrait`). No arbitrary external image URLs rendered.
8. **Bounded Template Iteration:** All `{% for %}` loops iterate over bounded view-model tuples (max 50 characters, max 100 table rows, max 30 issues).
9. **Safe Warning Rendering:** Warnings rendered via platform-owned closed-vocabulary lookup tables (`ISSUE_CODES`). No raw artifact text or exception strings rendered.
10. **Server-Authoritative Values Only:** All displayed counts, calculations, status codes, and capabilities originate from frozen view models. Zero client-side computation.
11. **No Secret or Raw Payload Disclosure:** No OAuth tokens, passkey secrets, raw JSON audit payloads, SQL queries, stack traces, or credentials present in view models or templates.

### 8.2 Security control verification mapping

| Security Control | Contract / Policy ID | Threat Mitigated | Automated Test Proving Control |
|---|---|---|---|
| Autoescaping / No `\|safe` | `VM-06`, `TC-SEC-11` | `T-17`, `T-34`, `T-35` (XSS via text) | `TC-SEC-11` (AST scan asserting 0 `\|safe`) |
| Prohibition of `hx-on:` / Script | `N-26`, route §6.4 | `T-04`, `T-17` (CSP bypass) | `TC-STRUCT-02` (Template linter) |
| Synchronizer CSRF Token | `N-17` | `T-20` (CSRF on mutations) | `TC-SESS-10`, `TC-SEC-01` |
| Safe Denial Views (`404` / `403`) | route §2.3 | `T-25`, `T-28` (Identifier oracle) | `TC-OBJ-01`, `TC-OBJ-07` |
| Coarse Failure Codes | `N-25`, `VM-04`, `VM-20` | `T-14`, `T-37` (Information disclosure) | `TC-SEC-12`, `TC-BG-14` |
| Pre-authorized Control Hiding | route §2.2 | `T-26`, `T-29` (Confused deputy) | `TC-OBJ-06` (Direct-HTTP denial) |

---

## 9. Proposed P3.4 file, test and implementation plan

### 9.1 Proposed minimal production file tree

```text
adapters/web/
├── templates/
│   ├── base.html                           # Root layout, 2-level header, nav, footer, skip link
│   ├── login.html                          # Sign in page (VM-01, VM-04)
│   ├── my_characters.html                  # Member characters page (VM-05)
│   ├── character_detail.html               # Character sheet page (VM-06)
│   ├── council_character_index.html        # Council character list (VM-07)
│   ├── council_character_links.html        # Character access management (VM-08)
│   ├── identity_migration.html             # Identity link migration (VM-10)
│   ├── field_profile.html                  # Versioned field profile (VM-11)
│   ├── role_capabilities.html              # Role capability administration (VM-12)
│   ├── account_identities.html             # Linked account identities (VM-13)
│   ├── council_snapshots.html              # Snapshot list & folder selection (VM-14)
│   ├── job_status.html                     # Reconciliation job status & poll (VM-15)
│   ├── import_result.html                  # Import receipt summary (VM-17)
│   ├── audit_search.html                   # Platform audit log search (VM-18)
│   ├── components/
│   │   ├── header.html                     # Two-level header partial
│   │   ├── footer.html                     # Platform footer partial
│   │   ├── portrait_fallback.html          # Character portrait initials SVG fallback
│   │   ├── summary_cards.html              # Control totals & stat cards
│   │   └── alert_banner.html               # Standard alert cards (ready, empty, stale, denied, error)
│   └── partials/
│       ├── identity_search_results.html    # HTMX fragment for R-24 (VM-09)
│       ├── job_status_fragment.html        # HTMX fragment for R-44 (VM-15)
│       └── audit_results_fragment.html     # HTMX fragment for R-49 (VM-18)
└── static/
    ├── css/
    │   ├── tokens.css                      # 71 design tokens
    │   └── styles.css                      # Layout primitives, components, utility classes
    ├── js/
    │   ├── htmx.min.js                     # Vendored HTMX library (v1.9.10+)
    │   └── portrait-preview.js             # Accessible native <dialog> script
    └── assets/
        └── freedom-blades-token.png        # Guild emblem token
```

### 9.2 Recommended implementation sequence

Implementation is strictly ordered by backend gate readiness:

```text
Phase 3.4 Implementation Sequence:

  [Gate P3.G0 & P3.G1 Closed]
             │
             ▼
  Stage 1: Base Assets & Login Views (VM-01, VM-02, VM-03, VM-04, VM-19, VM-20, VM-21)
             │  (Can overlap late P3.3 only for accepted non-conflicting contracts)
             ▼
  [Gate P3.G2 Closed & OD-45 Direct-HTTP Evidence Accepted]
             │
             ▼
  Stage 2: Member & Council Admin Views (VM-05, VM-06, VM-07, VM-08, VM-09, VM-10, VM-11, VM-12, VM-13)
             │
             ▼
  [Gate P3.G3 Closed & Durable Job Polling Contracts Frozen]
             │
             ▼
  Stage 3: Import, Jobs & Audit Search Views (VM-14, VM-15, VM-17, VM-18)
             │
             ▼
  Stage 4: Integration Evidence & Gate P3.G4 Submission
             │  (Automated browser suite, keyboard/reflow checks, Peter's visual & real-device acceptance)
             ▼
  [Gate P3.G4 Closed]
```

### 9.3 Relative complexity & risk concentration

- **Low Risk / Complexity:** Base layout (`base.html`), login page (`login.html`), static CSS tokens, health JSON endpoint.
- **Medium Risk / Complexity:** Member character sheets (`character_detail.html`), field profile (`field_profile.html`), account identities (`account_identities.html`), HTMX partial swaps (`R-24`, `R-49`).
- **High Risk / Complexity:**
  1. **Job Status & HTMX Polling (`job_status.html` / `R-44`):** Managing multi-state transitions (`queued`, `running`, `completed`, `stale`, `failed`, `cancelled`), handling backoff headers, and ensuring progressive enhancement without JS.
  2. **Role-Capability Administration (`role_capabilities.html`):** Rendering N-67 allowlist alerts, provenance tags (`ordinary` vs `emergency_continuity`), and ratify actions (`R-38`).
  3. **New Screen Layouts (VM-10, VM-12, VM-13, VM-18):** Building four visual screens without prior prototype pages, requiring Peter's visual acceptance at P3.G4.

---

## 10. Readiness gaps, owners and gate deadlines

| Gap ID | Source Artifact & Section | Observed Gap, Ambiguity or Dependency | Consequence if Unresolved | Accountable Owner | Gate Deadline | Safest Default Action |
|---|---|---|---|---|---|---|
| **GAP-01** | `status.md`, `delivery-plan.md` §5 | **Stop Gate P3.G1 is Open.** P3.1 OD-44 remediation (`migration 0009`) delivered 2026-08-14, awaiting Codex re-review and security pass. | P3.2 backend cannot start; P3.4 contracts remain unvalidated in code. | `Codex/review` & `Peter/decision` | **P3.G1** | Stop; await P3.G1 gate decision. |
| **GAP-02** | `delivery-plan.md` §5 (P3.2) | **Package P3.2 Not Implemented.** Member reads, identity migration, link admin, and role mapping backend routes do not exist. | View models `VM-05` through `VM-13` cannot be rendered by production code. | `Claude/backend` & `Peter/decision` | **P3.G2** | Stop; await P3.2 completion & P3.G2 gate. |
| **GAP-03** | `delivery-plan.md` §5 (P3.3) | **Package P3.3 Not Implemented.** Snapshot list, folder selection, durable reconciliation jobs, and audit search do not exist. | View models `VM-14`, `VM-15`, `VM-17`, `VM-18` cannot be rendered or polled. | `Claude/backend` & `Peter/decision` | **P3.G3** | Stop; await P3.3 completion & P3.G3 gate. |
| **GAP-04** | `threat-model.md` `RR-05` & `RR-06` | **Real-Folder Apply Runtime & Worker Memory Unmeasured.** Rehearsal B previewed only; apply duration and peak memory on real 32-Actor folder unmeasured. | Production worker memory limit (`N-47` 1G) and job timeout (`N-45`) unvalidated under real load. | `Claude/backend` & `Operations Owner` | **P3.G3 / P3.G4** | Revalidate in staging before P3.G4 release. |
| **GAP-05** | `view-model-contract.md` §10 | **Four Screens Lack Prototype Pages.** Identity migration (VM-10), role capabilities (VM-12), account identities (VM-13), audit search (VM-18) have no page in `design-prototype/`. | Frontend layouts for these four screens must be constructed extending visual tokens without an accepted static HTML page. | `Gemini/frontend` & `Peter/decision` | **P3.G4** | Build using accepted visual patterns; require Peter's visual approval at P3.G4. |
| **GAP-06** | `test-traceability.md` §18 | **Assistive Technology Testing Unrun.** Screen reader audio traversal (VoiceOver/NVDA) explicitly unrun in project baseline. | Accessibility evidence rests on source/automated checks and manual keyboard passes. | `Peter/decision` | **P3.G4** | Label AT evidence as unrun; perform maintainer testing before release. |

---

## 11. Post-P3.G2/P3.G3 go/no-go checklist

This checklist must be evaluated by the maintainer prior to authorizing P3.4 production frontend template implementation:

| Check Item | Required Condition | Present Status | Satisfied? |
|---|---|---|---|
| **1. Gate P3.G0 Closed?** | Contract & security baseline accepted by Peter Duscha. | Accepted 2026-08-13 | **YES** |
| **2. Gate P3.G1 Closed?** | P3.1 authentication foundation accepted after Codex re-review & security pass. | OD-44 remediated 2026-08-14; review open | **NO** |
| **3. Gate P3.G2 Closed?** | P3.2 member reads, link admin, role capabilities accepted by Peter Duscha. | Package P3.2 not started | **NO** |
| **4. Gate P3.G3 Closed?** | P3.3 snapshot import, durable jobs, audit views accepted by Peter Duscha. | Package P3.3 not started | **NO** |
| **5. View Models Frozen?** | View-model contract `vm-1` (`VM-01`..`VM-21`) frozen at P3.G2 and P3.G3. | Freeze gates open | **NO** |
| **6. OD-45 Direct-HTTP Passed?** | Direct-HTTP tests for R-33, R-34, R-38 passed at P3.G2 (`TC-BG-05b/c/e`). | P3.G2 open | **NO** |
| **7. Freeze Manifest Intact?** | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` passes 14/14. | Verified 14/14 OK | **YES** |
| **OVERALL P3.4 DISPOSITION** | All predecessor gates closed and contracts frozen. | **P3.G1, P3.G2, P3.G3 OPEN** | **NO-GO FOR P3.4** |

---

## 12. Commands, freeze verification and diff account

### 12.1 Commands executed and verification results

1. **Pre-Analysis Repository Status:**
   ```bash
   git status --short
   ```
   *Result:* Recorded 24 pre-existing modified files and 28 untracked files from earlier P3.0/P3.1 package submissions. Zero changes made by Gemini prior to report creation.

2. **Visual Freeze Manifest Verification (Before Analysis):**
   ```bash
   sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256
   ```
   *Result:* All 14 visual prototype files passed verification cleanly (`OK`).
   - `design-prototype/assets/freedom-blades-token.png`: OK
   - `design-prototype/assets/portraits/lyra.png`: OK
   - `design-prototype/assets/portraits/thorin.png`: OK
   - `design-prototype/assets/portraits/valerius.png`: OK
   - `design-prototype/character-detail.html`: OK
   - `design-prototype/components.html`: OK
   - `design-prototype/council-approval.html`: OK
   - `design-prototype/css/styles.css`: OK
   - `design-prototype/css/tokens.css`: OK
   - `design-prototype/index.html`: OK
   - `design-prototype/js/portrait-preview.js`: OK
   - `design-prototype/login.html`: OK
   - `design-prototype/my-characters.html`: OK
   - `design-prototype/reconciliation.html`: OK

3. **Visual Freeze Manifest Verification (After Analysis):**
   ```bash
   sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256
   ```
   *Result:* All 14 visual prototype files passed verification cleanly (`OK`).

4. **Deliverable Diff & Cleanliness Verification:**
   ```bash
   git diff --check -- docs/review/phase-3-p3-4-gemini-readiness-report.md
   git status --short
   ```
   *Result:* Zero whitespace errors; sole untracked file added is `docs/review/phase-3-p3-4-gemini-readiness-report.md`.

### 12.2 Deliverable and repository modification accounting

- **Sole File Created:** `docs/review/phase-3-p3-4-gemini-readiness-report.md`.
- **Repository Modifications:** Zero runtime code files, Jinja templates, CSS assets, JavaScript files, database migrations, contract specifications, project management records, or frozen prototype assets were edited, created, or deleted.
- **Visual Freeze Status:** All 14 frozen prototype files under `design-prototype/` remain 100% untouched and match their SHA-256 manifest.
- **Evidence Classes Deliberately Not Run:** Live production services, database migrations, package installations, network requests, browser automation test suites, and assistive technology audio traversals were deliberately not run for this read-only planning task.
- **Collisions or Inconsistencies:** No file collision occurred. `docs/review/phase-3-p3-4-gemini-readiness-report.md` did not previously exist in the repository.

---

P3.4 readiness analysis complete; P3.4 implementation remains NO-GO until P3.G2 and P3.G3 close, and no production or frozen-prototype file was changed.

---

# Addendum — current-state reconciliation, 2026-08-19

**Added by:** Claude, as backend contract owner and working Technical Lead
**Basis:** the accepted P3.1–P3.3 tree at `c318231` plus uncommitted P3.3 work
**Nothing above this line is rewritten.** §§1–12 are the 2026-08-14 analysis and
its NO-GO conclusion. That conclusion was correct on its own date: P3.G1, P3.G2
and P3.G3 were all open. This addendum records what changed, corrects the parts
of the 2026-08-14 analysis that the accepted implementation falsified, and
states the current disposition.

## A1. Gate state as at 2026-08-19

| Gate | State | Record |
|---|---|---|
| P3.G0 — contract and security design baseline | **Closed 2026-08-13** | `docs/contracts/README.md`; change-log *Phase 3 P3.G0 final acceptance and P3.1 authorization* |
| P3.G1 — authentication and security foundation | **Closed 2026-08-16** | `phase-3-p3-g1-independent-and-security-re-review-2026-08-16.md`; RAID *P3.G1 closure amendment — 2026-08-16* |
| P3.G2 — member reads, identity reconciliation, access administration | **Closed 2026-08-18** | change-log `C-P3.2-D` |
| P3.G3 — Council import, durable jobs, audit views | **Closed 2026-08-19** | change-log `C-P3.3-K` |
| P3.G4 — frontend/integration/accessibility and visual acceptance | **Open** | Peter only. Claude, Gemini and Codex cannot close it |
| D-03 backend route/view-model approval | **Open** | RAID D-03; `C-P3.3-K`; `C-P3.3-L`; `phase-3-p3-4-authorisation-and-conditions.md` §5 |
| I-06 isolated staging evidence | **Open** | RAID I-06; `C-P3.3-L` |
| A-05 protected administrator / WebAuthn readiness | **Open** | RAID A-05; `C-P3.3-L` |

`C-P3.3-K` authorizes **P3.4 development**. It authorizes no deployment, no
public exposure, no live-service contact and no live-data use. `C-P3.3-L` fixes
the order: P3.4 development → isolated staging and I-06 → A-05 → **D-03 before
Gemini production integration** → a separate exposure decision.

## A2. Reconciliation of the 2026-08-14 gaps

| 2026-08-14 gap | Disposition now | Evidence |
|---|---|---|
| GAP-01 — P3.G1 open | **Closed** 2026-08-16 | RAID P3.G1 closure amendment |
| GAP-02 — P3.2 not implemented | **Closed.** R-20…R-38 are implemented and accepted | `adapters/web/portal_routes.py`; `C-P3.2-D` |
| GAP-03 — P3.3 not implemented | **Closed.** R-40…R-49 are implemented and accepted | `adapters/web/import_routes.py`; `C-P3.3-K` |
| GAP-04 — real-folder apply runtime and worker memory unmeasured | **Still open; moved to I-06.** TC-PERF-01…03 are staging evidence and cannot be produced locally | traceability §17, §20; RAID I-06 |
| GAP-05 — four screens lack prototype pages | **Still open, unchanged, and confirmed exact.** The four are VM-10, VM-12, VM-13 and VM-18 | view-model contract §10, re-read 2026-08-19 |
| GAP-06 — assistive-technology testing unrun | **Still open; belongs to P3.G4** as TC-UI-09 | traceability §16, §20 |
| *(new)* six backend-contract items | **Open; they are the substance of D-03.** See §A6 | this addendum |

## A3. Corrections to the 2026-08-14 analysis

These are recorded because the sections above are preserved unedited and a
reader must not carry their errors into implementation.

1. **The TC-UI identifiers in §3 are wrong.** The accepted set is TC-UI-01…09
   only (traceability §16). §3's matrix cites `TC-UI-10` and `TC-UI-11`, which do
   not exist, and assigns `TC-UI-08` to VM-12 and `TC-UI-09` to VM-13 as though
   they were per-screen automated cases. **TC-UI-08 is a real-device check on
   Peter's own hardware and TC-UI-09 is a screen-reader traversal.** Neither is
   per-screen, neither is automatable, and traceability §16 states in terms that
   they "must not be reported as passing on automated evidence".
2. **`TC-VM-05` … `TC-VM-21` in §3 do not exist.** The accepted set is
   TC-VM-01…05, and TC-VM-05 is specifically *`level = None` renders as "not
   recorded", never `0`*.
3. **R-37 requires no reason.** §4.2 item 4 lists "identity unlink reason" among
   the forms requiring a non-blank reason. The route contract §5.1 requires none,
   and the handler reads none — it takes the CSRF token and the path identifier
   and nothing else.
4. **R-46 submits no version.** §4.2 item 4 says "`preview_token` & versions".
   The form carries `preview_token` and `nonce`; the checksum, folder, profile
   version and aggregate versions are **re-read server-side** and are not
   browser inputs (route contract §6.1, step 4).
5. **R-36 does not redirect.** §4.1's inventory follows the route contract's
   *Response* column (`303` to provider). The accepted implementation answers
   `200` rendering VM-13 in its `denied` state — which is what the same
   contract's §5.1 prose requires. See D-03-5 below.
6. **§9.1's proposed file tree already conflicts with the accepted tree.** It
   proposes `council_character_index.html` and `council_character_links.html`;
   the accepted templates are `council_characters.html` and
   `character_links.html`, and the accepted fragments are
   `identity_search.html`, `job_status_fragment.html` and `audit_results.html`
   at the template root rather than under `partials/`. §A7 supersedes it.
7. **§9.1 proposes `portrait-preview.js`.** Phase 3 renders no character image
   (view-model contract §3.4): `CharacterPortrait` carries `state`, `initials`
   and `accessible_label`, and there is nothing to preview. The prototype's
   dialog is not a Phase 3 component.

## A4. The accepted implementation, proved rather than assumed

Read-only comparisons run against the current tree on 2026-08-19. Commands and
literal output are in §A9.

| Claim | Result |
|---|---|
| The registered route inventory equals the accepted contract exactly | **39 = 39**; no contract-only route, no implementation-only route, no method or path difference |
| Routes deferred to a later package | `DEFERRED_ROUTES == {}` — the accepted inventory is complete |
| The implemented view-model set equals the documented `vm-1` set | **21 = 21**; `DEFERRED_VIEW_MODELS == {}` |
| Version identifier | `VIEW_MODEL_VERSION == "vm-1"` |
| Field-level comparison of all 21 view models against the contract's own type sketches | One implementation-only field (VM-13 `csrf_token`) and one ordering difference (VM-12). No field is missing, renamed or removed |
| No character-game-state mutation affordance | `CharacterDetailView` has no form token, no editable field and no action list; `my_characters.html` and `character_detail.html` contain zero `<form>` elements |
| Deferred legacy fields cannot carry a value | `MigrationDeferred` fields are exactly `{field_key, owning_package}` |
| Safe error carries nothing else | `SafeErrorView` fields are exactly `{state, correlation, message_code}` |
| Current minimal templates are already CSP-clean | zero `\|safe`, zero `hx-on:`, zero `<script>`, zero `design-prototype/` references, zero absolute URLs, CDN or remote-font references across all 24 templates |

**Conclusion on drift:** on everything a static comparison can decide — the
closed route set, the view-model set, the version, the field shapes, and the
absence controls — the accepted implementation matches the frozen contract.
The six items in §A6 are gaps *in* the contract or inconsistencies *within* it,
not places where the implementation departed from an accepted sentence.

## A5. Current-tree route matrix — what Gemini may consume

Authority column uses the route contract's caller states. `obj` = object-scoped.
`cont` = reachable by a continuity-scoped session (`BG`/`AC`) within N-65/N-67.
Every mutation additionally requires the exact `Origin` (N-01) and a
session-bound synchronizer CSRF token (N-17) read from the view model, never
from a cookie.

### P3.1 — `adapters/web/app.py`

| R | Method · path | Kind | Authority | View model | Template | Inputs | Success | Bound |
|---|---|---|---|---|---|---|---|---|
| R-01 | GET `/` | navigation | all | – | – | – | `303` `/v1/characters` or `/v1/login` | – |
| R-02 | GET `/v1/login` | full page | all | **VM-01** | `login.html` | – | `200` | – |
| R-03 | GET `/v1/auth/discord/start` | navigation | all | – | – | `return` (server-side allowlist) | `303` to provider | N-18 |
| R-04 | GET `/auth/discord/callback` | navigation | all | **VM-02** on refusal | `non_member.html` | provider `code`, `state` | `303` to stored target; `403` VM-02 for a non-member | N-18 |
| R-05 | POST `/v1/auth/logout` | form | session | – | – | `csrf_token` | `303` `/v1/login` | 1 KiB |
| R-06 | GET `/v1/auth/emergency` | full page | all | **VM-04** | `emergency.html` | – | `200` | – |
| R-07 | POST `…/emergency/webauthn/options` | JSON `fetch` | all | – | – | JSON | `200` JSON | N-32 · 4 KiB |
| R-08 | POST `…/emergency/webauthn/verify` | JSON `fetch` | all | – | – | JSON assertion | `200` JSON | N-32 · 16 KiB |
| R-09 | POST `…/emergency/recovery` | form | all | – | – | grant token | `303` `/v1/admin/role-capabilities` | N-33 · 4 KiB |
| R-10 | GET `/healthz` | operator JSON | loopback only (N-50) | **VM-16** | – | – | `200`/`503` JSON | – |

R-07 and R-08 are the **only** browser JSON routes in Phase 3, and they exist
solely because the WebAuthn API requires script-driven credential exchange.
Nothing else in P3.4 may use `fetch`.

### P3.2 — `adapters/web/portal_routes.py`

| R | Method · path | Kind | Authority | View model | Template | Inputs | Success |
|---|---|---|---|---|---|---|---|
| R-20 | GET `/v1/characters` | full page | `M` `C` `CA` | **VM-05** | `my_characters.html` | – | `200` |
| R-21 | GET `/v1/characters/{character_id}` | full page | `M`(obj) `C` `CA` | **VM-06** | `character_detail.html` | – | `200`; `404` otherwise |
| R-22 | GET `/v1/council/characters` | full page | `C` `CA` | **VM-07** | `council_characters.html` | `q`, `cursor`, `size` | `200` |
| R-23 | GET `/v1/council/characters/{character_id}/links` | full page | `C` `CA` | **VM-08** | `character_links.html` | `cursor` | `200` |
| R-24 | GET `/v1/council/identity-search` | **fragment** of R-23 | `C` `CA` | **VM-09** | `identity_search.html` | `q` (≥2, ≤120), `character_id` | `200` fragment; `401` unauthenticated |
| R-25 | POST `/v1/council/characters/{character_id}/links` | form | `C` `CA` | – | – | `csrf_token`, `version`, `subject`, `access_kind`, `reason` | `303` R-23 |
| R-26 | POST `…/links/{access_id}/revoke` | form | `C` `CA` | – | – | `csrf_token`, `version`, `reason` | `303` R-23 |
| R-27 | POST `…/links/{access_id}/default` | form | `C` `CA` | – | – | `csrf_token`, `version`, `reason` | `303` R-23 |
| R-28 | GET `/v1/council/identity-migration` | full page | `C` `CA` | **VM-10** | `identity_migration.html` | `cursor`, `size` | `200` |
| R-29 | POST `…/identity-migration/{proposal_id}/confirm` | form | `C` `CA` | – | – | `csrf_token`, `version`, `reason` | `303` R-28 |
| R-30 | POST `…/identity-migration/{proposal_id}/reject` | form | `C` `CA` | – | – | `csrf_token`, `reason` | `303` R-28 |
| R-31 | GET `/v1/council/field-profile` | full page | `C` `A` `CA` | **VM-11** | `field_profile.html` | – | `200` |
| R-32 | GET `/v1/admin/role-capabilities` | full page | `A` `CA` `cont` | **VM-12** | `role_capabilities.html` | – | `200` |
| R-33 | POST `/v1/admin/role-capabilities` | form | `A` `CA` `cont`(N-67) | – | – | `csrf_token`, `role_id`, `capability`, `reason` | `303` R-32 |
| R-34 | POST `…/role-capabilities/{mapping_id}/revoke` | form | `A` `CA` `cont`(N-67) | – | – | `csrf_token`, `version`, `reason` | `303` R-32 |
| R-35 | GET `/v1/account/identities` | full page | any session, `cont` | **VM-13** | `account_identities.html` | – | `200` |
| R-36 | GET `/v1/account/identities/link/start` | full page | any session (not `BG`) | **VM-13** `state="denied"` | `account_identities.html` | – | **`200`**, not a redirect — see D-03-5 |
| R-37 | POST `/v1/account/identities/{identity_id}/unlink` | form | any session (not `BG`) | – | – | `csrf_token` **only** | `303` R-35 |
| R-38 | POST `…/role-capabilities/{mapping_id}/ratify` | form | `A` `CA` full scope only | – | – | `csrf_token`, `version`, `reason` | `303` R-32 |

### P3.3 — `adapters/web/import_routes.py`

| R | Method · path | Kind | Authority | View model | Template | Inputs | Success | Body |
|---|---|---|---|---|---|---|---|---|
| R-40 | GET `/v1/council/snapshots` | full page | `C` `A` `CA` | **VM-14** | `council_snapshots.html` | `cursor`, `size` | `200` | – |
| R-41 | POST `/v1/admin/snapshots/{snapshot_id}/folder` | form | `A` `CA` | – | – | `csrf_token`, `folder_id` | `303` R-40 | 4 KiB |
| R-42 | POST `/v1/council/snapshots/{snapshot_id}/preview-jobs` | form | `C` `CA` | – | – | `csrf_token`, `nonce` | `303` R-43 | 4 KiB |
| R-43 | GET `/v1/council/jobs/{job_id}` | full page | `C` `CA` | **VM-15** | `job_status.html` | – | `200` | – |
| R-44 | GET `/v1/council/jobs/{job_id}/status` | **fragment** of R-43 | `C` `CA` | **VM-15** | `job_status_fragment.html` | – | `200` + `Retry-After`; `401` unauthenticated | – |
| R-45 | POST `/v1/council/jobs/{job_id}/cancel` | form | `C` `CA` | – | – | `csrf_token` | `303` R-43 | 4 KiB |
| R-46 | POST `/v1/council/jobs/{job_id}/apply` | form | `C` `CA` | – | – | `csrf_token`, `preview_token`, `nonce` | `303` R-43 | 8 KiB |
| R-47 | GET `/v1/council/imports/{import_id}` | full page | `C` `A` `CA` | **VM-17** | `import_result.html` | – | `200` | – |
| R-48 | GET `/v1/audit` | full page | `C` `A` `CA` `cont` | **VM-18** | `audit_search.html` | `action`, `entity_type`, `entity_id`, `capability`, `source`, `from`, `to`, `correlation_id`, `cursor`, `size` | `200` | – |
| R-49 | GET `/v1/audit/results` | **fragment** of R-48 | `C` `A` `CA` `cont` | **VM-18** | `audit_results.html` | as R-48 | `200` fragment; `401` unauthenticated | – |

### Cross-cutting responses

| Outcome | Status | View model | Template |
|---|---|---|---|
| Non-member | `403` | VM-02 | `non_member.html` |
| Membership unconfirmable, N-10 grace exhausted | `503` | VM-03 | `degraded.html` |
| Denied (any closed category) | `401`/`403`/`404` | **VM-02 used as the carrier** — see D-03-6 | `denied.html` |
| Conflict | `409` | VM-19 (`stale_version`, `stale_preview`, `already_applied`, `already_cancelled`, `duplicate_request` — all five in use) | `conflict.html` |
| Validation failure | `422` | VM-21 | `validation.html` |
| Safe error | `500` | VM-20 | `error.html` |

### The four confirmations the handover required

1. **Every HTMX fragment is independently authorized and also reachable as a
   full page.** R-24/R-23, R-44/R-43, R-49/R-48. Each fragment carries its own
   `RouteGuard` row with its own requirement, and each answers `401` rather than
   `303` when unauthenticated so a login page is never swapped into a fragment
   target.
2. **Polling honours `poll_after_seconds` and stops on a terminal state.**
   `job_status_fragment.html` emits `hx-get`/`hx-trigger`/`hx-swap` **only**
   when `job_state in ("queued", "running")`; `completed`, `stale`, `failed` and
   `cancelled` render no polling attribute at all. The interval and the
   `Retry-After` header are both the validated N-22 floor.
3. **Ordinary members receive no import control and direct calls remain
   denied.** `M` is refused `403` on R-40…R-47, before the job row is read, so a
   job UUID discloses nothing. VM-14's `can_select_folder`/`can_preview` are
   rendering hints computed from the same resolution the server performs again.
4. **Administrator status does not imply Council apply authority.** R-42 and
   R-46 carry `Requirement.COUNCIL`; `A` alone is refused `403`. R-41 carries
   `Requirement.ADMINISTRATOR`; `C` alone is refused `403`. A continuity-scoped
   session reaches **no** import route, R-41 included.
5. **No character-game-state correction route or form exists.** The closed
   inventory is 39 routes, all accounted for; VM-06 exposes no mutation
   affordance by type; the two member templates contain zero forms.
6. **Deferred legacy fields carry their owning package and no control.**
   `MigrationDeferred(field_key, owning_package)` — there is no value field to
   render and no control to attach.
7. **Raw snapshot bytes, exception text, SQL, paths, tokens and unsafe detail
   cannot reach a response.** Reconciliation warnings cross the boundary as
   closed-vocabulary codes plus counts (9 `ISSUE_CODES`); `SafeErrorView` carries
   a correlation UUID and one message code; the denial body carries a category
   and nothing else; the only Actor name that crosses is a Council-only bounded
   `BlockedEntry.display_name`.
8. **The four screens with no frozen prototype page are exactly VM-10, VM-12,
   VM-13 and VM-18** (view-model contract §10, unchanged).

## A6. D-03 disposition — **not closable on the existing gate record**

The question the handover set was whether the accepted P3.G2/P3.G3 records and
the contract freeze already supply the backend route/view-model approval D-03
requires. **They do not**, for two independent reasons.

**First, as a matter of record.** `C-P3.3-K` and `C-P3.3-L` were both decided on
2026-08-19 — the same day P3.G3 closed, and after P3.G2 closed on 2026-08-18.
Both restate D-03 as in force and as the thing that must close *before* Gemini
production integration. Peter recorded that with the gate closures in front of
him. Reading P3.G2/P3.G3 as having silently closed D-03 would overturn a dated
decision by inference, which is exactly what the handover forbids.

**Second, and substantively.** Six concrete items remain. Two of them would stop
a faithful P3.4 implementation on its first file; four are record corrections
that should not be left for a frontend package to absorb.

| # | Item | Why it is a backend-contract issue | Owner | Safest resolution |
|---|---|---|---|---|
| **D-03-1** | **No accepted static-asset surface exists.** N-26 is `default-src 'self'; … script-src 'self'; style-src 'self'; img-src 'self' data:`, so production CSS, vendored HTMX and the emblem must be served same-origin. The route contract's set is **closed** and contains no static path; the operational contract's Caddy table (§4.1) defines no static handler and assigns everything but HSTS to the application. Worse, `TC-STRUCT-01` would **not** catch a `StaticFiles` mount: it reads `getattr(route, "methods", …)`, and a Starlette `Mount` has none — so the one machine check protecting the closed set is blind here | A URL surface, its authorization state, its kill-switch and host behaviour, its cache headers and its place in the closed inventory are all route-contract decisions. A frontend package cannot invent them | Claude/backend, then Codex, then Peter | Add the static surface to the route contract (path, method, caller states, kill-switch behaviour, `Cache-Control`, and whether Caddy or `freedom-web` serves it), and extend `TC-STRUCT-01` to assert over mounts as well as routes. **Blocking for P3.4** |
| **D-03-2** | **`ConfirmScope` is referenced by VM-15 and never defined in `vm-1`.** The implementation carries eight fields (`preview_token`, `checksum_full`, `folder`, `profile_version`, `expires_at`, `would_create`, `would_update`, `blocked`); the frozen contract carries the name only | *"Council confirmation exact scope"* is a mandatory delivery-plan §11 evidence row owned jointly by P3.3 and **P3.4**. Gemini cannot render an exact scope whose shape the contract does not state | Claude/backend | Define `ConfirmScope` in view-model contract §7 from the accepted implementation. Additive under §1 rule 5; no new version. **Blocking for faithful P3.4** |
| **D-03-3** | **`CharacterFilters` is referenced by VM-07 and never defined in `vm-1`.** The implementation carries `query: SafeText \| None` and `include_inactive: bool` | The Council character index's filter bar is a P3.4 surface with no stated shape | Claude/backend | Define it in §5 alongside `CouncilCharacterRow`. Additive |
| **D-03-4** | **VM-13 carries an implemented `csrf_token` the frozen block does not list.** It is genuinely additive and genuinely required — R-37 is a cookie-authenticated mutation, so N-17 obliges a server-rendered synchronizer token, and VM-13 is the only view model carrying a mutation control without one. §1 rule 5 permits the addition. But the field's own docstring says *"Recorded in the P3.2 submission"*, and it is not: `phase-3-p3-2-submission.md` contains no occurrence of `csrf_token` | An accepted-record claim that cannot be located is a provenance defect, not a code defect | Claude/backend | Add `csrf_token` to the VM-13 block and correct or remove the docstring's provenance claim |
| **D-03-5** | **R-36's two halves of the route contract disagree.** The §5 table's *Response* column says `303` to provider; §5.1's prose says it is *"refused with VM-13's `no_additional_provider` state"*. The implementation follows the prose and answers `200` with VM-13 in `denied` | An internal inconsistency in the frozen contract, resolved by the implementation without the table being corrected | Claude/backend | Correct the table's *Response* cell to `200` HTML · VM-13 (`denied`) and say why, so the closed set reads consistently |
| **D-03-6** | **The safe denial body has no view model of its own.** `denied.html` is rendered from a `NonMemberView` (VM-02) whose `guild_display_name` is `""`, `checked_at` is `Instant("", "")` and `correlation` is the nil UUID, for **every** denial category — the placeholders exist because §2.3 requires an object-denial `404` and an absent-object `404` to be byte-identical. `vm-1` names no general denial view; §7.1 says only *"the safe denial view"* | A P3.4 template that rendered `view.guild_display_name` or `view.correlation.id` on a denial page would print an empty string and `00000000-0000-0000-0000-000000000000`, and printing the correlation id would break TC-OBJ-07's byte-identity requirement | Claude/backend to record; Gemini constrained by it | Either define a `DeniedView` carrying only `state` and `reason`, or record in §8 that the denial body is VM-02-shaped with three deliberately inert fields that **must not** be rendered |

**Recommended disposition, for Peter's decision.** Items D-03-2 through D-03-6
are additive definitions and record corrections that change no runtime
behaviour; D-03-1 is a genuine missing contract surface that must be decided
before any production template writes a `<link>` or a `<script src>`. All six
return through Claude/backend, an independent Codex review and Peter's decision
— none may be absorbed into templates. A proposed change-log entry presenting
this is filed as **`C-P3.4-A`**, deliberately **not** marked accepted.

## A7. What Gemini may and may not change in P3.4

### May change or create

| Path | Responsibility |
|---|---|
| `adapters/web/templates/base.html` | Production layout: skip link, landmarks, two-level header, navigation, footer, the stylesheet reference decided by D-03-1 |
| `adapters/web/templates/*.html` — the 24 existing files | Replace each minimal contract template with its production rendering, **keeping the filename and the view-model contract identical** |
| `adapters/web/templates/components/`, `adapters/web/templates/partials/` | New shared includes, if genuinely shared. Not a dumping ground |
| the static asset location settled by **D-03-1** | Production CSS, vendored HTMX (single reviewed file, version + upstream URL + SHA-256 in its header), the emblem image |
| `tests/web/test_p3_4_*.py` and equivalents | Frontend contract, escaping, header, accessibility, structural and browser tests |
| `docs/review/phase-3-p3-4-submission.md` | The P3.4 handoff |

The 24 template filenames the accepted routes render are fixed by the handlers:
`base`, `login`, `emergency`, `non_member`, `degraded`, `denied`, `conflict`,
`validation`, `error`, `my_characters`, `character_detail`,
`council_characters`, `character_links`, `identity_search`,
`identity_migration`, `field_profile`, `role_capabilities`,
`account_identities`, `council_snapshots`, `job_status`,
`job_status_fragment`, `import_result`, `audit_search`, `audit_results`.
Renaming one is a route-handler change and therefore a backend change.

### Must not change

`adapters/web/app.py`, `adapters/web/portal_routes.py`,
`adapters/web/import_routes.py`, `adapters/web/composition.py`,
`adapters/web/middleware.py`, `adapters/web/repositories.py`,
`adapters/web/discord_provider.py`, anything under `application/`, `domain/`,
`adapters/database/`, `adapters/http/`, `adapters/worker/`, `migrations/`,
`infra/`, `tools/`, `docs/contracts/`, `design-prototype/`,
`docs/review/phase-3-visual-freeze-manifest.sha256`, `requirements-web*.txt`,
`requirements-web.lock`, `.env.example`, and every existing test module that
is not a P3.4 frontend test.

## A8. P3.4 evidence classes — what may and may not be claimed

| Class | Rows | Who produces it |
|---|---|---|
| Automated, source/structural | TC-UI-06, TC-SEC-08, TC-SEC-10, TC-SEC-11, TC-STRUCT-01, TC-STRUCT-02 | Gemini |
| Automated, response | TC-SEC-05, TC-SEC-09, and the denial/error/stale/validation state rows | Gemini |
| Automated, browser | TC-UI-01, TC-UI-02, TC-UI-03, TC-UI-04, TC-UI-05 | Gemini — **only** with an already-installed browser; installing one requires explicit authorization |
| Supervised | TC-UI-07 contrast | Gemini's source-derived matrix **plus** a supervised confirmation |
| **Real-device, manual** | **TC-UI-08** | **Peter only.** Never an automated pass |
| **Assistive technology, manual** | **TC-UI-09** | **Peter only**, and still *not yet scheduled*. Phase 3 inherits no pass from the prototype |
| Staging | TC-SEC-07 browser half, TC-LIM-02, TC-OPS-01…05, TC-PERF-01…03 | **Not P3.4.** These belong to I-06 and require isolated staging |

`TC-UI-06` — *no production template imports, links to or serves anything under
`design-prototype/`* — **does not exist yet**. It is P3.4's to write, and it is
the structural proof the delivery plan asks for.

## A9. Commands run and literal results, 2026-08-19

```bash
$ sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256
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
# exit status 0 — 14/14
```

```bash
$ git diff --check
# no output; exit status 0
```

Route and view-model comparison, run under `./venv-web/bin/python` against the
current tree:

```text
contract routes: 39   implemented inventory: 39   deferred: {}
contract - inventory: []
inventory - contract: []
method/path drift: {}
documented VMs: 21    implemented: 21             deferred: {}
documented - implemented: []
implemented - documented: []
VIEW_MODEL_VERSION: vm-1
```

Field-level comparison of all 21 view models against the contract's own type
sketches:

```text
checked 21
('VM-13', 'AccountIdentitiesView', {'contract_only': [], 'impl_only': ['csrf_token'], 'order_identical': False})
('VM-12', 'RoleCapabilityView',    {'contract_only': [], 'impl_only': [],             'order_identical': False})
```

Template corpus audit across all 24 files in `adapters/web/templates/`:

```text
|safe                : 0 occurrences (one prose mention in a base.html comment)
hx-on:               : 0 occurrences (two prose mentions in comments)
<script              : 0
design-prototype     : 0
http:// or https://  : 0
cdn / fonts.google   : 0
```

**Not run, deliberately:** the portal and bot pytest suites, because they run
Alembic migrations against the disposable database and this preparation task is
forbidden to run migrations; any browser; any package installation; any
network call; any live Discord, Google, Foundry or production service; any
real Actor, player or guild data. No `.env`, secret or credential file was
read. The pre-existing stash was neither inspected nor touched.

## A10. Literal readiness result

> **NO-GO for P3.4 production frontend implementation.**

P3.G0, P3.G1, P3.G2 and P3.G3 are closed and `C-P3.3-K` authorizes P3.4
development, so the 2026-08-14 blockers are gone. The result is nevertheless
NO-GO for one reason and one reason only: **D-03's backend route/view-model
approval is open**, `C-P3.3-L` requires it to close before Gemini production
integration, and §A6 records six concrete contract items that must be resolved
in that decision. GO is permitted only after Peter accepts the D-03 disposition
and explicitly releases
`docs/review/phase-3-p3-4-gemini-implementation-prompt.md`.

Nothing in this addendum is staging, deployment or production-readiness
evidence. I-06 and A-05 remain open and continue to prohibit public exposure.
