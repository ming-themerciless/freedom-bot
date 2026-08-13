# Gemini handoff — visual refinement Step 1 correction

Copy everything below this line into Gemini as one prompt.

---

You are correcting **Step 1 only** of the staged Freedom Blades Phase 3 visual
refinement program.

Repository: `/opt/discord-bots/freedom-bot`

Current date: 2026-08-13

Public review URL: `https://freedom-blades.rpgworld.org`

Frontend implementer: Gemini

Independent reviewer: Codex

Visual acceptance authority: Peter Duscha

## 1. Outcome

Preserve the successful prominent portrait composition, correct its remaining
narrow-screen defects, remove one stale unsupported announcement, and refine the
shared navigation across every prototype page.

Peter specifically requests better alignment and presentation for the top
navigation and wants Login placed last, following familiar website conventions.

This remains a static Phase 3 §12.1 prototype. Stop after this correction and
return it for Step 1 visual acceptance. Do not begin Step 2.

## 2. Read before editing

Read completely:

1. `AGENTS.md`
2. `.agents/AGENTS.md`
3. `docs/implementation-plan.md`, especially §12.1
4. `docs/review/phase-3-visual-refinement-work-program.md`
5. `docs/review/phase-3-visual-refinement-step-1-gemini-prompt.md`
6. every current file under `design-prototype/`

Run `git status --short` before editing. Preserve existing maintainer, Codex and
Gemini work. Do not reset, clean, revert, stage, commit or overwrite unrelated
changes.

## 3. Authorized scope

You may edit only:

- `design-prototype/css/styles.css`;
- `design-prototype/my-characters.html`;
- `design-prototype/character-detail.html`;
- `design-prototype/index.html`;
- `design-prototype/login.html`;
- `design-prototype/reconciliation.html`;
- `design-prototype/council-approval.html`; and
- `design-prototype/components.html`.

Do not edit assets, tokens, README, formal handoff documents, audit tools,
production code or Caddy configuration.

## 4. Preserve the accepted Step 1 direction

Keep:

- full-width 16:9 character-card media regions;
- one fully visible portrait per card;
- prominent but non-interactive imagery;
- the detail-page portrait as an identity anchor;
- stable `object-fit` cropping and image-error fallbacks;
- local PNG assets;
- no portrait overlap, negative-margin collage or stacked deck;
- no hover enlargement, preview overlay or lightbox yet; and
- the existing character data, state controls and OD-16 role demonstration.

## 5. Correct the portrait/card responsive findings

### 5.1 Detail identity group at 320 px

`.profile-identity-group` currently has `min-width: 280px`. The narrow media rule
changes direction but does not reset this minimum, so the group may exceed the
usable inner width of a 320 px viewport.

In the narrow rule:

- set `min-width: 0`;
- set `width: 100%`;
- ensure the portrait and identity text remain inside the card; and
- preserve wrapping for stable IDs and long class/display-name text.

### 5.2 Character card heading/status row

Replace the repeated inline flex style around each character name and status with
a named shared class. The row must:

- allow the name region to shrink with `min-width: 0`;
- keep the badge legible;
- wrap or stack predictably on narrow screens;
- avoid clipping long names; and
- retain clear hierarchy between stable ID, character name and status.

Do not solve this with text truncation that hides the character’s name.

### 5.3 Character fact rows

Make `.char-details-list li` resilient:

- add a deliberate gap;
- allow labels and values to wrap;
- align values consistently on wider cards; and
- stack label/value pairs at very narrow widths when necessary.

Long values such as “Blade Officer (Tier 2)” and “485 gp (48,500 cp)” must not
collide with their labels or cause horizontal overflow.

### 5.4 Neutral sync-pending announcement

In `showState()`, replace the live-region wording “Data Locked.” It implies a
production locking behavior that is not established.

Use neutral prototype language such as:

`[Showing Sync Pending Preview State]`

Do not introduce other lock, audit, transaction or backend guarantees.

## 6. Refine the shared top navigation

These are navigation links, not tabs. Keep semantic `<nav>`, list markup and
`aria-current="page"`. Do not add `role="tab"`, tablist semantics or arrow-key
tab behavior.

Apply the same link order on every prototype page:

1. Overview
2. My Characters
3. Character Detail
4. Reconciliation
5. Council Queue
6. Components
7. Login

Login must be last.

### 6.1 Alignment and rhythm

Refine the shared navigation CSS so:

- brand, navigation and user-status region align cleanly on the cross axis;
- links share a consistent minimum height, vertical centering, padding, radius
  and text baseline;
- spacing is uniform;
- active borders do not change an item’s dimensions or shift neighbouring links;
- hover, active and focus states are restrained and clearly distinguishable;
- the navigation looks like one coherent component rather than separate uneven
  pills; and
- no item appears accidentally higher, lower, narrower or more padded than the
  others.

A transparent border in the normal state is a sound way to prevent active-state
layout shift.

### 6.2 Login treatment

Login may receive a subtle separated/outlined action treatment because it is an
account entry point, but:

- keep it within the navigation list and last in DOM order;
- do not style it as the page’s dominant primary action;
- ensure its active state on `login.html` remains coherent;
- do not add authentication behavior; and
- do not contradict the static prototype’s synthetic user indicator.

Use a shared class such as `nav-link-login` if needed, applied consistently on
all pages.

### 6.3 Responsive behavior

At desktop widths, keep the navigation aligned and balanced between brand and
user status.

At narrow widths:

- do not show partially clipped navigation choices;
- do not rely on an unexplained horizontal scrollbar as the only access method;
- prefer a deliberate wrapped layout or another simple CSS-only arrangement;
- preserve DOM order and large enough pointer targets;
- keep the active page and Login visually understandable; and
- avoid overlapping the brand or user indicator.

Do not add a JavaScript hamburger menu in this correction. A CSS-only responsive
layout is sufficient for the static prototype.

## 7. Accessibility and interaction boundaries

- Preserve visible `:focus-visible` styling.
- Keep every link keyboard reachable in DOM order.
- Do not use color alone to indicate the active page.
- Keep `aria-current="page"` only on the current page’s link.
- Portraits remain non-clickable and unfocusable in Step 1.
- Keep portrait fallback activation limited to image errors.
- Preserve reduced-motion behavior.

For portrait alt text, either retain the descriptive text or change to empty alt
when the adjacent heading makes it redundant. Apply the decision consistently
and explain it in the return note. Do not add ARIA solely to compensate for
visual styling.

## 8. Project-level safeguards

The global `a`, `a:hover` and `a:visited` rules added during earlier audit work
can override component-specific navigation and button-link colors because of
cascade and specificity.

As part of the shared navigation correction:

- ensure `.nav-link`, `.brand-title`, `.btn` links and the Login treatment retain
  their intended normal, visited, hover, active and focus colors;
- scope generic content-link styling if necessary;
- do not let visited navigation or button links unexpectedly turn into the
  generic content-link color; and
- preserve underlining for ordinary inline content links where useful without
  underlining navigation or button components.

Do not edit the contrast audit tools during this visual correction. Record that
their report may be stale until Claude repairs it after visual freeze.

## 9. Preserve Phase 3 behavior and scope

Do not regress:

- state-selector `aria-pressed` and live-region behavior;
- reconciliation’s five presentation states;
- Council modal structure and inert restoration;
- OD-16 member/Council view distinction;
- responsive card-grid and detail-stack safeguards;
- synthetic identities and local-only assets;
- truthful inert/static language; or
- existing security boundaries.

Do not add production authentication, authorization, persistence, imports,
backend calls or the deferred tools/languages/homebrew administration editor.

## 10. Verification and evidence

Run and report:

- `git diff --check`;
- `python3 design-prototype/tools/check_css_tokens.py`;
- a check that all seven HTML pages use the required navigation order;
- a check that each page has exactly one `aria-current="page"`;
- searches confirming no portrait has `onclick`, interactive roles or `tabindex`;
- searches confirming all portrait paths remain repository-local;
- a changed-path check; and
- HTML validation if an installed validator is available.

If a real browser is available, inspect every page’s navigation and both
character pages at 320 px, 768 px and 1280 px. Record the browser/tool, exact
method and results. If not, say explicitly that rendering, overlap and responsive
behavior were designed and source-inspected but not runtime-verified.

Do not claim viewport or keyboard testing without real browser evidence.

## 11. Return and stop

Return:

- exact files changed;
- portrait/mobile corrections made;
- navigation order and styling rationale;
- desktop and narrow-screen intended behavior;
- alt-text decision;
- commands actually run and their results;
- unavailable runtime checks; and
- public URLs Peter should inspect.

Then stop. Do not begin Step 2, add portrait hover/preview behavior, update the
formal Phase 3 handoff, modify audit tools, commit, push, deploy, modify Caddy or
claim Step 1/Phase 3 acceptance.
