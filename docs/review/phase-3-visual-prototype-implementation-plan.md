# Phase 3 visual prototype — controlled implementation plan

Status: proposed for maintainer approval

Date: 2026-08-12

Frontend design implementer: Gemini

Backend implementer: Claude

Independent and security-focused reviewer: Codex

Acceptance Authority: Peter Duscha

Governing handoff:
`docs/review/phase-3-visual-prototype-gemini-prompt.md`

## 1. Objective and acceptance standard

Produce the static visual direction required by implementation-plan §12.1. The
prototype must establish a coherent Freedom Blades design system and demonstrate
the Phase 3 and forward-looking Council screens with synthetic data.

The deliverable must meet all four standards together:

1. **Functional clarity:** a user can understand navigation, information
   hierarchy, read-only boundaries, authority, provenance, progress and error
   states without explanation from the designer.
2. **Usability:** representative tasks are operable by keyboard and understandable
   at mobile, tablet and desktop widths; dense operational data remains usable.
3. **Accessibility:** semantic structure, focus, contrast, reduced motion,
   labelling and responsive behaviour meet the documented WCAG 2.2 AA target.
4. **Visual quality:** the result is cohesive, deliberate and attractive enough
   for Peter to accept as the production visual direction. A wireframe with
   colours is not sufficient.

Completion of files or checks is evidence, not acceptance. Codex reviews the
prototype and Peter accepts or rejects the visual direction.

## 2. Scope boundary

All prototype implementation lives under `design-prototype/`. The only other
file Gemini may create or edit is
`docs/review/phase-3-visual-prototype-handoff.md`.

The prototype is static and inert:

- no FastAPI, Jinja production templates, routes, API endpoints or web process;
- no authentication, sessions, authorization implementation or CSRF;
- no application services, repositories, database access or migrations;
- no Discord, Foundry, Google Sheets, PostgreSQL or external network access;
- no production configuration or imports from `design-prototype/`;
- no React, Vue, SPA framework, npm, bundler or build step;
- no CDN, remote font, analytics or tracker; and
- no real login, upload, import, approval, correction or mutation.

Small local JavaScript is permitted only to demonstrate presentation states,
navigation disclosure or an accessible dialog. It must be dependency-free,
work without a server, make no request, persist nothing, remain understandable
when disabled, and be removable during Jinja/HTMX integration.

Production frontend integration is a later task. It begins only after this
visual direction is accepted and Claude's route/view-model contracts are stable
and accepted.

## 3. Inputs and mandatory reading

Before editing, Gemini reads completely:

1. `AGENTS.md`
2. `.agents/AGENTS.md`
3. `docs/implementation-plan.md`, especially §§4, 5, 6.2, 9, 12.1, Phase 3,
   §13.3 and §16.4
4. `docs/adr/0002-web-application-stack.md`
5. `docs/adr/0004-discord-oauth2-authentication.md`
6. `docs/rules/field-ownership.md`
7. `docs/discovery/open-decisions.md`, especially closed OD-16 and OD-17
8. `docs/project-management/status.md`
9. `docs/review/phase-3-visual-prototype-gemini-prompt.md`

Gemini checks `git status` first and preserves all existing user changes,
including the maintainer-supplied image files and controlled records. It does
not reset, clean, revert, stage, commit or reformat unrelated work.

## 4. Brand and asset use

`docs/Freedom Blades Token.png` is the required identity asset. It is a clean
1024×1024 PNG supplied and confirmed by Peter on 2026-08-12.

The design uses the token's circular seal, blue wings, steel-grey ring, black and
white as its starting language. It must not merely sample a few colours and place
the image in a corner. The seal should anchor the login/header identity while the
wing geometry and steel character inform restrained layout, separators, states
and rhythm.

Rules:

- use the PNG itself without tracing, redrawing, distorting or generating a
  near-copy;
- preserve its aspect ratio and source quality;
- use meaningful alternative text only when it conveys identity; decorative
  repetitions use empty alternative text;
- reference it locally with a path that works when pages open by `file://`;
- do not use it as a tiled texture or low-contrast watermark behind content; and
- inventory it as a maintainer-supplied project asset confirmed 2026-08-12.

The untracked JPG is not an implementation input unless Peter separately directs
otherwise. The PNG is canonical for this track.

## 5. Design-system work

Create at minimum:

- `design-prototype/css/tokens.css`
- `design-prototype/css/styles.css`

Optional local files such as `prototype.js` are added only when justified by a
required presentation demonstration.

Define tokens for:

- brand, surface, text, border, focus and semantic-state colours;
- font families, sizes, line heights and weights;
- spacing, content widths, radii and touch targets;
- borders and restrained elevation;
- focus rings;
- motion duration/easing with a reduced-motion override; and
- narrow, tablet and wide breakpoints.

Gemini may begin with the slate/steel/wing-blue palette it proposed, but the
hex values are hypotheses, not approved tokens. Before freezing them, calculate
and record contrast for every foreground/background pairing actually used,
including text, muted text, links, buttons, focus indicators, badges, alerts,
form borders and disabled states. Adjust values that fail. Semantic status must
never depend on colour alone.

Use a system font stack. Avoid faux-medieval display faces, parchment textures,
ornamental clutter and protected D&D art. The interface is a dependable guild
operations product, not a themed character sheet.

## 6. Required pages and their contracts

### 6.1 Prototype index

`design-prototype/index.html` links to every page and state demonstration. It
identifies the prototype as inert and provides a concise viewport/state matrix.

### 6.2 Login

`design-prototype/login.html` includes:

- the emblem as the primary identity anchor;
- plain Discord sign-in and privacy copy;
- a clearly inert sign-in control; and
- normal, unavailable and denied examples without simulating OAuth.

### 6.3 My Characters

`design-prototype/my-characters.html` demonstrates:

- multiple linked characters;
- immutable identity distinguished from mutable display name;
- normal, empty, loading and unavailable states; and
- a useful mobile layout rather than a desktop grid squeezed narrow.

All identities and facts are obviously synthetic. Do not display sensitive
financial values on overview cards unless the design rationale establishes a
real overview need; avoid turning privacy-sensitive detail into decoration.

### 6.4 Character detail

`design-prototype/character-detail.html` is read-only and demonstrates:

- profile information and provenance;
- snapshot/profile version and freshness;
- representative financial facts in the detail view;
- a linked-member view; and
- a visibly elevated Council inspection view.

OD-16 governs the concept: ordinary members see linked characters only and
Council may inspect any character. State-switching in the prototype is a visual
demonstration, not authorization. The page must say that access is enforced on
the server in production; a hidden selector is not a control.

### 6.5 Reconciliation

`design-prototype/reconciliation.html` demonstrates:

- checksum, world, folder, exporter and profile scope;
- mappings, create candidates, explicit unresolved identities and warnings;
- `legacy_authority_deferred` with the owning migration package;
- normal, queued, running, completed, stale and failed states; and
- a Council confirmation composition that is explicitly inert.

The measured real preview took 9.57 seconds. Do not model this as a synchronous
button whose page appears frozen. Show an asynchronous job concept with durable
identity and reconnect-safe status language. A timer animation is not evidence
of background processing and must not dictate Claude's eventual implementation.

The page must not offer or imply a Phase 3 character-game-state correction.
Folder selection, import triggering and Council authority remain distinct.

### 6.6 Council queue and diff

`design-prototype/council-approval.html` is a forward-looking component design
for later phases, marked clearly as unavailable/inert in Phase 3. It demonstrates:

- queue, empty and denied states;
- before/after facts and provenance;
- warning, stale and conflict states;
- confirmation and required-reason compositions; and
- a narrow-screen alternative to a wide side-by-side diff.

It must not imply that Phase 3 supplies a generic approval engine or permits a
game-state mutation.

### 6.7 Component catalogue

`design-prototype/components.html` inventories:

- shell, primary/secondary navigation and breadcrumbs;
- cards, descriptions, tables and responsive record lists;
- forms, fieldsets, inputs and validation;
- buttons and links in every state;
- badges, alerts and provenance/status treatments;
- tabs, pagination and progress;
- empty, loading/skeleton, validation, denied, stale and system-error states;
- dialogs with labelled intent and focus behaviour; and
- long text, long identifiers and overflow stress examples.

Every component appears in context on at least one page or is identified as
forward-looking. Do not grow a decorative component library without a consumer.

## 7. Shared accessibility and responsive requirements

Every page includes:

- semantic landmarks and one logical `h1`;
- a skip link;
- logical heading order;
- meaningful link/button names;
- keyboard reachability and visible `:focus-visible`;
- no hover-only information;
- text and icon/state labels in addition to colour;
- reduced-motion support;
- browser zoom and text resizing without disabled scaling; and
- useful behaviour at 320 px, 768 px and 1280 px.

Targets must be practically touchable. Dense tables need a designed mobile
representation—prioritized columns, labelled records or controlled overflow—not
an unexamined full-page horizontal scrollbar. Dialog demonstrations document
initial focus, focus containment intent, Escape behaviour and focus return even
if their static fallback is always visible.

## 8. Visual-quality iteration

Visual acceptance is not deferred to the final review. Gemini works in three
passes:

1. **Foundation:** shell, tokens, login and one dense content page establish the
   visual thesis.
2. **System:** remaining pages apply the same components and expose weak or
   inconsistent decisions.
3. **Polish:** inspect representative screenshots at all three widths, correct
   hierarchy, alignment, rhythm, overflow, repeated ornament, empty space and
   visual noise, then reconcile every page back to the component catalogue.

The handoff includes representative screenshots or exact local paths and a
short rationale explaining why the design fits Freedom Blades. Gemini must call
out any composition it considers weak; completeness is not a reason to preserve
it.

## 9. Documentation and production mapping

Create `design-prototype/README.md` with:

- direct local opening instructions for every page;
- design tokens and contrast results;
- component and state inventory;
- responsive and accessibility decisions;
- asset provenance;
- a page/component mapping to likely Jinja layouts/templates and modest HTMX
  partials;
- assumptions Claude must resolve in accepted route/view-model contracts; and
- explicit production-integration exclusions.

The mapping describes semantic needs, not invented route names, request payloads
or authorization logic. Gemini does not dictate backend contracts.

Create `docs/review/phase-3-visual-prototype-handoff.md` with:

- complete file list;
- design rationale and important rejected alternatives;
- state/viewport coverage matrix;
- accessibility and contrast evidence;
- keyboard and reduced-motion observations;
- asset record;
- exact commands/checks run and checks not run;
- limitations and backend assumptions; and
- an explicit statement that the work carries no acceptance and changes no
  production surface.

## 10. Verification

### 10.1 Static checks

- `git diff --check` passes.
- No file outside the authorized paths is changed by Gemini.
- Every page opens through `file://` with no server.
- Search all prototype files for `http://`, `https://`, protocol-relative URLs,
  external fonts/scripts/styles, production imports and request APIs.
- Search for forms/actions, `fetch`, XHR, storage APIs, service workers and other
  accidental state/network behaviour; each occurrence must be absent or
  explicitly justified as inert local presentation.
- Validate HTML with an available local standards-aware validator. If none is
  installed, report that fact and perform a documented structural check rather
  than claiming validation.
- Check for secrets, real names/IDs, production data and copied third-party art.

### 10.2 Manual checks

- Open every page with networking disabled.
- Inspect every page at 320 px, 768 px and 1280 px.
- Keyboard-walk global navigation and every representative control using Tab,
  Shift+Tab, Enter, Space and Escape where applicable.
- Verify focus is always visible and focus order follows reading order.
- Verify content at browser zoom and enlarged text.
- Verify reduced-motion behaviour.
- Inspect normal, empty, loading, validation, denied, stale and system-error
  states.
- Record contrast ratios for actual pairings, not token colours in isolation.
- Inspect representative screenshots for visual polish, consistency and useful
  density.

## 11. Review and exit conditions

Gemini stops and returns the work for review when:

- all required pages, components, states and documents exist;
- static and manual evidence is recorded truthfully;
- the prototype contains no production or external behaviour;
- no known WCAG AA contrast failure remains;
- the result has completed the visual-polish pass; and
- limitations and Claude contract questions are explicit.

Codex then reviews visual consistency, accessibility, responsive behaviour,
asset use, scope isolation and architecture fit. Peter decides the visual gate.
Only after acceptance may Gemini adapt the design into production Jinja/static
assets, and only against Claude's stable accepted contracts.

Gemini does not commit, push, deploy or claim the visual gate closed.
