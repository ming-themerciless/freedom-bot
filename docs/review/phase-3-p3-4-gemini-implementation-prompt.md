# Prompt for Gemini — P3.4 production frontend integration

**Prepared:** 2026-08-19 · **Author:** Claude, backend contract owner and working
Technical Lead · **Reviewer:** Codex, independent implementation pass plus a
distinct security-focused pass · **Decision:** Peter / Acceptance Authority

> [!IMPORTANT]
> **RELEASED 2026-08-20 by Peter/Acceptance Authority.** The corrected D-03
> backend route/view-model contract passed an independent Codex implementation
> review and a distinct security-focused review, and Peter accepted it. Gemini
> may begin the bounded P3.4 production frontend integration described here.
> This release does not close P3.G4 and does not authorize staging exposure,
> deployment, production use, live-service contact or real-player-data use.
> I-06 and A-05 remain open. Review and acceptance record:
> [`phase-3-d-03-codex-reviews-and-acceptance.md`](phase-3-d-03-codex-reviews-and-acceptance.md).
>
> **Execution is checkpointed.** Follow
> [`phase-3-p3-4-gemini-execution-plan.md`](phase-3-p3-4-gemini-execution-plan.md),
> one separately released step prompt at a time. Do not combine steps or begin a
> later step before its prompt is released. Step 1 is
> [`phase-3-p3-4-gemini-step-01-baseline-prompt.md`](phase-3-p3-4-gemini-step-01-baseline-prompt.md).

---

## 1. Who you are and what you own

You are the **production frontend implementer** for package **P3.4** only.
Claude owns the backend contracts, Codex reviews independently, and Peter alone
accepts. You cannot close P3.G4, you cannot accept your own work, and you cannot
resolve a cross-boundary question by changing a template.

Package boundary, from the accepted delivery plan §5 P3.4:

> *Gemini may not change authentication, authorization, persistence, route or
> view-model contracts. A necessary cross-boundary change returns to Claude,
> Codex review and Peter's decision rather than being absorbed in templates.*

## 2. Read completely before planning or editing

1. `.agents/AGENTS.md` and `docs/implementation-plan.md`;
2. `docs/review/phase-3-delivery-plan.md`, especially §4 exclusions, §5 P3.4 and
   P3.G4, §7's numeric contract, §11 traceability and §12 risks;
3. `docs/review/phase-3-p3-4-authorisation-and-conditions.md` and change-log
   `C-P3.3-K`, `C-P3.3-L`, `C-P3.4-A`, `C-P3.4-B` and `C-P3.4-C`;
4. `docs/contracts/README.md`, then every Phase 3 contract in its prescribed
   order — the route-authorization, view-model, numeric-policy, threat-model and
   test-traceability contracts above all;
5. **`docs/review/phase-3-p3-4-gemini-readiness-report.md` §§A1–A10**, which is
   the current-tree matrix. §§1–12 of that file are the historical 2026-08-14
   analysis; §A3 lists the seven places it is now wrong. Do not implement from
   §§1–12;
6. `docs/review/phase-3-visual-prototype-handoff.md` and
   `docs/review/phase-3-visual-freeze-manifest.sha256`;
7. every file under `design-prototype/`, **read-only**;
8. every current template in `adapters/web/templates/`, and the handlers that
   render them: `adapters/web/app.py`, `adapters/web/portal_routes.py`,
   `adapters/web/import_routes.py`;
9. `application/web/view_models.py` in full — it is the authoritative shape of
   every object your templates receive; and
10. the P3.4-relevant tests and structural guards, especially
    `tests/web/test_structural_guards.py`.

Where an accepted contract and the implementation disagree, **stop and return
the discrepancy**. Do not choose the convenient side, and do not paper over a
backend defect with a template.

## 3. Scope — what P3.4 delivers

### 3.1 Templates

Replace each **existing** minimal contract template with its production
rendering. The filenames are fixed by the route handlers; renaming one is a
backend change:

`base.html` · `login.html` · `emergency.html` · `non_member.html` ·
`degraded.html` · `denied.html` · `conflict.html` · `validation.html` ·
`error.html` · `my_characters.html` · `character_detail.html` ·
`council_characters.html` · `character_links.html` · `identity_search.html` ·
`identity_migration.html` · `field_profile.html` · `role_capabilities.html` ·
`account_identities.html` · `council_snapshots.html` · `job_status.html` ·
`job_status_fragment.html` · `import_result.html` · `audit_search.html` ·
`audit_results.html`

New shared includes under `adapters/web/templates/components/` and
`adapters/web/templates/partials/` are permitted where something is genuinely
shared. Neither directory is a dumping ground, and page logic is not duplicated
into a second place.

### 3.2 Static assets

Production-owned CSS, one vendored HTMX file and the guild emblem, served
same-origin under N-26's `script-src 'self'` / `style-src 'self'` /
`img-src 'self' data:`.

**Their URL surface is the accepted D-03-1 mount M-01.** Serve them from the
application-owned `/static/` surface exactly as contracted: same-origin,
`GET`/`HEAD`, public, trusted-host protected, available during the portal kill
switch and fingerprint-aware for `Cache-Control`. Do not invent another asset
surface or change its backend behavior.

The vendored HTMX file is committed as a **single reviewed file** with its
version, upstream URL and SHA-256 in the file header, verified by a test — the
discipline the visual freeze manifest already uses
(configuration contract §1.5).

### 3.3 Visual language

Adapt the accepted §12.1 visual direction — the forged-steel palette, the
two-level header, the card grid, the table container, the blade divider, the
focus ring, the reduced-motion override. **Reimplement it in production-owned
files.** Do not copy, move, import, link to or serve anything under
`design-prototype/`, and do not alter the 14-file freeze or its manifest.

Two prototype behaviours are **not** Phase 3 components:

- the portrait preview dialog and `js/portrait-preview.js`. Phase 3 renders no
  character image (view-model contract §3.4): `CharacterPortrait` carries
  `state`, `initials` and `accessible_label`, and the fallback is the only path;
- `council-approval.html`'s approval-queue concept, which is Phase 6 and
  explicitly excluded by delivery plan §4. Its table and diff *patterns* may be
  adapted; its workflow may not.

### 3.4 Screens

Every screen in the §A5 route matrix, covering VM-01…VM-21. Four have **no**
frozen prototype page and must be built by extending the accepted visual
language: **VM-10** identity migration, **VM-12** role-capability
administration, **VM-13** account identities, **VM-18** audit search. Peter's
visual acceptance of that new work is reserved to P3.G4.

### 3.5 States

Every applicable state of `PageState` — `ready`, `empty`, `loading`, `stale`,
`denied`, `invalid`, `error` — renders from a real view model, together with
keyboard operation, visible focus, and the denied/validation/system-error
bodies. An empty list is a fact and renders as one; it is never a `404` and
never an error page.

### 3.6 Responsive and progressive enhancement

- 320, 768 and 1280 CSS pixels, and 200% reflow, with no horizontal body
  overflow and no lost content or function;
- **every essential flow completes with JavaScript disabled.** HTMX is modest
  enhancement over working links and forms, never the only path;
- `prefers-reduced-motion: reduce` suppresses transitions while preserving
  focus indicators.

### 3.7 Tests

Frontend contract, escaping, response-header, accessibility, structural and
browser tests, under `tests/web/`. §7 lists the required set.

## 4. Hard prohibitions

You may not:

- **change any route** — no new path, no removed path, no changed method. The
  set is closed at 39 and `TC-STRUCT-01` asserts it;
- **change any view model**, its fields, its types or its bounds;
- change authentication, authorization, capability resolution, session handling,
  CSRF, origin or host validation, persistence, migrations, runtime grants,
  application services, adapters, `composition.py`, `middleware.py`,
  `repositories.py`, dependencies, `requirements-web*.txt`,
  `requirements-web.lock` or `.env.example`;
- **serve, import, link to, copy or move anything under `design-prototype/`**,
  or modify the freeze manifest;
- introduce an SPA, a browser JSON API, npm, a bundler, a CDN, a remote font,
  analytics or a tracker. R-07 and R-08 are the only browser JSON routes in
  Phase 3 and exist solely because the WebAuthn API requires script;
- use `hx-on:`, any inline event handler (`onclick=`, `onerror=`, …), any inline
  executable `<script>` block, or anything requiring `unsafe-inline` — each
  would force a weakening of the accepted N-26 CSP, which requires documented
  security review;
- use `|safe`, `Markup`, or any pre-rendered user-influenced HTML. Phase 3
  permits `|safe` on **zero** values;
- compute an authoritative value client-side. Counts, totals, checksums,
  capabilities and versions are rendered as received; HTMX swaps content, it
  does not calculate;
- read the CSRF token from a cookie. N-17 is a session-bound synchronizer token,
  rendered server-side from the view model's `csrf_token` into a hidden input or
  a server-rendered `hx-headers`;
- **render a control the view model does not pre-authorize.** `confirmable`,
  `revocable`, `ratifiable`, `cancel_available`, `can_select_folder`,
  `can_preview` and `unlink_blocked_reason` exist so the page is honest. They
  are not the control — the server refuses regardless, and the tests prove it by
  never rendering the control;
- render `guild_display_name`, `checked_at`, `correlation`, an object identifier,
  a timestamp, or free-form details on the generic **denial** body.
  `denied.html` receives VM-22 `DeniedView`, containing only `state` and the
  closed-vocabulary `reason`. The carrier deliberately has no correlation ID,
  guild name, timestamp, object identifier, or free-form reason, preserving the
  byte-identical absent-object and unreachable-object `404` requirement of route
  contract §2.3 (accepted D-03-6). `non_member.html` alone retains VM-02 and its
  intentional membership-recovery context;
- claim TC-UI-08, TC-UI-09, staging, deployment or production readiness;
- install a browser, package or dependency without explicit authorization;
- run migrations, live services, external network calls, or anything against
  real Actor, player, guild or production data;
- read `.env`, credential or secret files;
- commit, push or deploy;
- touch the pre-existing stash `stash@{0}: On main: temp before rebase`, or
  discard any other user change in the working tree.

**If you need any of the above, stop and return the need to Claude, Codex and
Peter.** A cross-boundary change is a backend change with its own review, not a
template workaround.

## 5. The contract facts your templates depend on

The complete matrix is readiness report §A5. The facts most easily got wrong:

1. **Fragments are pages too.** R-24 pairs with R-23, R-44 with R-43, R-49 with
   R-48. Each fragment is independently authorized and answers `401` — not a
   redirect — when unauthenticated, so a login page is never swapped into a
   fragment target.
2. **Polling.** `job_status_fragment.html` emits `hx-get`/`hx-trigger` **only**
   while `job_state` is `queued` or `running`. It must stop dead on `completed`,
   `stale`, `failed` and `cancelled`. The interval is `poll_after_seconds`,
   which is the validated N-22 floor and is also echoed in `Retry-After`.
3. **Reasons and versions.** R-25 submits `version`, `subject`, `access_kind`,
   `reason`; R-26/R-27/R-29/R-34/R-38 submit `version` and `reason`; R-30
   submits `reason`; R-33 submits `role_id`, `capability`, `reason`; R-41
   submits `folder_id`; R-42 submits `nonce`; R-46 submits `preview_token` and
   `nonce`; **R-37 and R-45 submit the CSRF token and nothing else.**
4. **R-46 submits no version.** Checksum, folder, profile version and aggregate
   versions are re-read server-side. Do not put them in the form.
5. **R-36 is not a redirect.** It answers `200` HTML, rendering VM-13 in its
   `denied` state with `additional_provider = "no_additional_provider"`. The
   accepted route-contract response table, its §5.1 prose, and the implementation
   agree; D-03-5 corrected the former `303` record. The P3.2 caller-matrix value
   `U: ✗ 303` remains correct and means an unauthenticated navigation redirects
   to login—it is not R-36's authenticated response.
6. **Administrator is not Council.** `A` alone is refused on R-20, R-21, R-22,
   R-23, R-24, R-25, R-26, R-27, R-28, R-29, R-30, R-42, R-43, R-44, R-45 and
   R-46. Council alone is refused on R-32, R-33, R-34, R-38 and R-41. Render
   accordingly, and rely on the server anyway.
7. **A continuity-scoped session** (`BG`, and `AC`) reaches only R-32, R-33,
   R-34, R-35, R-48 and R-49 — and on R-33/R-34 only the `platform_administrator`
   capability (N-67). VM-12's `administrator_scope`, `available_capabilities`,
   `revocable`, `ratifiable` and `scope_notice_code` are how the page explains
   that; they are not how it is enforced.
8. **Warnings are codes.** Reconciliation issues cross the boundary as
   closed-vocabulary `ISSUE_CODES` plus counts. The human sentence is a
   **template-side lookup table owned by the platform**. No artifact text is
   forwarded, ever. The only Actor name that crosses is a Council-only,
   bounded `BlockedEntry.display_name`.
9. **`level = None` renders "not recorded", never `0`** (TC-VM-05).
10. **Deferred fields carry no value.** `MigrationDeferred(field_key,
    owning_package)` renders the package name from the controlled manifest and
    no control of any kind.
11. **No character image.** `CharacterPortrait` gives you `state`, `initials`
    and `accessible_label`. There is no image URL to request.
12. **Bounds are layout facts.** VM-05 ≤ 50 with `truncated`; VM-06 ≤ 200
    snapshot fields, ≤ 200 deferred fields, ≤ 25 access facts; VM-08 ≤ 25 active
    and ≤ 100 historical links; VM-09 ≤ 25 candidates; VM-10 page 50 / max 100;
    VM-11 ≤ 500 paths and ≤ 500 fields; VM-12 ≤ 50 mappings; VM-13 ≤ 10
    identities; VM-14 ≤ 50 snapshots and ≤ 50 folders; VM-15 ≤ 30 issue counts
    and ≤ 50 blocked entries; VM-18 page 50 / max 100 with ≤ 40 facts per row;
    VM-21 ≤ 20 field errors. Cursors are opaque and HMAC-signed — never offsets.
13. **`ConfirmScope` (VM-15) and `CharacterFilters` (VM-07) are defined by the
    accepted D-03 correction.** Render only their recorded fields and types.
    `ConfirmScope` is display scope except for the submitted `preview_token`;
    R-46 also submits `nonce`, while checksum, folder, profile and aggregate
    versions are re-read server-side. A character display-name query is a
    search fact, never an identity or authorization fact.

## 6. Accessibility requirements

- semantic landmarks, one `<h1>` per page, a correct heading order, a skip link,
  and `aria-current="page"` on exactly one navigation item;
- every control labelled; every error programmatically associated with its
  field; a validation summary that moves focus;
- keyboard reachability with a visible focus indicator on every interactive
  element, including after an HTMX swap — focus must not be lost into the void
  when content is replaced;
- status and error announcements that inform without flooding a live region; a
  poll that replaces content every two seconds must not announce every tick;
- tables that remain readable at 320 CSS pixels through a local
  `overflow-x: auto` container, **without hiding an authoritative fact**;
- 200% zoom and increased text spacing without loss of content or function;
- `prefers-reduced-motion` honoured;
- WCAG 2.2 AA contrast on production surfaces, evidenced by a source-derived
  matrix **and** a supervised confirmation — the prototype's matrix is not
  production evidence.

Dialogs only where an accepted interaction contract already requires one. Phase
3 requires none.

## 7. P3.G4 verification — the literal minimum

Run, and report literally, with the command and its real output:

1. the **complete** existing web suite and the complete bot suite, with any skip
   explained;
2. **TC-UI-01…TC-UI-05** — browser checks at 320/768/1280 CSS pixels, 200%
   reflow, keyboard reachability with visible focus, reduced motion, and every
   state rendered from a real view model. **Only with an already-installed
   browser.** If none is installed, report the rows as not run and request
   authorization; do not install one;
3. **TC-UI-06** — a new structural test proving no production template imports,
   links to or serves anything under `design-prototype/`. This test does not
   exist yet and is yours to write;
4. **TC-SEC-05** — exact response headers on every `/v1/*` response: CSP equal
   to N-26, `nosniff`, `Referrer-Policy`, COOP, CORP, `Permissions-Policy`, and
   `Cache-Control: no-store` on authenticated responses;
5. **TC-SEC-08** — Jinja autoescaping on for every configured extension, and
   **zero** templates using `|safe`;
6. **TC-SEC-09** — escaping parametrization: `<script>`,
   `"><img onerror>`, `{{7*7}}`, a 10 000-character name, RTL overrides and
   NFC/NFD variants, in Actor names, reasons, usernames and audit values, all
   rendering inert and bounded;
7. **TC-SEC-10** — no template contains an `hx-on:` attribute;
8. **TC-SEC-11** — no view-model field reaches a `<script>` context anywhere in
   the rendered corpus;
9. structural proof of **zero** inline executable script, CDN reference and
   remote-font reference across the production corpus;
10. **TC-STRUCT-01 and TC-STRUCT-02** still green — the route set and the
    view-model set are unchanged by your package;
11. response tests for denial, validation, stale and safe-error bodies, proving
    in particular that the denial body carries the category and nothing else;
12. no-JavaScript coverage of every essential flow;
13. the visual freeze manifest verified **before and after**:
    `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256`;
14. `python -m compileall` for every changed Python file, the configured
    formatter/linter/type checker on what you changed, and `git diff --check`;
15. `git status --short` before and after, with every edited region's before and
    after SHA-256.

**Left explicitly to Peter, and never claimed by you:**

- **TC-UI-08** — real-device inspection on Peter's own hardware;
- **TC-UI-09** — screen-reader traversal of login, My Characters, character
  detail, reconciliation and audit. Still *not yet scheduled*; Phase 3 inherits
  no pass from the visual baseline.

A source test passing is not a browser test passing. Say which class each result
belongs to, and never report an unrun check as run.

## 8. Working rules

1. Record `git status --short` before you start. Preserve every pre-existing
   user change. Do not inspect, apply, drop or modify `stash@{0}`.
2. Record each file's SHA-256 before you edit it, and give before/after values
   at handoff.
3. Keep the diff scoped. No opportunistic rewrites, no reformatting of files
   your package did not change.
4. Update a template and its tests together.
5. If a screen cannot be built faithfully from the accepted contracts — a
   missing field, an undefined type, an authority the view model does not carry
   — **stop, and return it**. Do not approximate it, and do not add a control
   the backend would refuse.

## 9. Deliverables

1. the production templates, static assets and vendored HTMX;
2. the P3.4 test suite;
3. `docs/review/phase-3-p3-4-submission.md`: the change map, the screen-by-screen
   view-model coverage, every command with its literal result, the evidence class
   of each result, every check not run and why, the residual risks, and the
   review request for Codex's independent and distinct security-focused passes;
4. exact files changed with before/after SHA-256;
5. the remaining P3.G4 manual evidence, named and left to Peter.

Then stop. Do not close P3.G4, do not begin P3.5, and do not represent any part
of this package as staging, deployment or production readiness.
