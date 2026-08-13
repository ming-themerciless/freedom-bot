# Gemini handoff — visual refinement Step 1 navigation correction

Copy everything below this line into Gemini as one prompt.

---

You are implementing the final **navigation-only correction for Phase 3 visual
refinement Step 1**.

Repository: `/opt/discord-bots/freedom-bot`

Current date: 2026-08-13

Public review URL: `https://freedom-blades.rpgworld.org`

Frontend implementer: Gemini

Independent reviewer: Codex

Visual acceptance authority: Peter Duscha

## 1. Objective

Replace the current loosely wrapping header navigation with a deliberate,
well-aligned, code-native navigation component.

Peter specifically dislikes the visibly misaligned navigation text. The target
is a polished set of consistently sized navigation buttons—not bitmap button
images—with Login last.

The accepted portrait work is frozen for this correction. Do not begin portrait
hover/preview Step 2 or perform a broader redesign.

## 2. Read before editing

Read completely:

1. `AGENTS.md`
2. `.agents/AGENTS.md`
3. `docs/implementation-plan.md`, especially §12.1
4. `docs/review/phase-3-visual-refinement-work-program.md`
5. `docs/review/phase-3-visual-refinement-step-1-correction-gemini-prompt.md`
6. `design-prototype/css/tokens.css`
7. `design-prototype/css/styles.css`
8. all seven current prototype HTML pages

Run `git status --short` before editing. Preserve existing maintainer, Codex and
Gemini work. Do not reset, clean, revert, stage, commit or overwrite unrelated
changes.

## 3. Authorized scope

You may edit only:

- `design-prototype/css/styles.css`;
- `design-prototype/index.html`;
- `design-prototype/login.html`;
- `design-prototype/my-characters.html`;
- `design-prototype/character-detail.html`;
- `design-prototype/reconciliation.html`;
- `design-prototype/council-approval.html`; and
- `design-prototype/components.html`.

Do not edit tokens, assets, portraits, README, handoff documents, audit tools,
production code or Caddy configuration.

## 4. Required header architecture

Use a consistent two-level header on every page:

### Header identity row

The first row contains:

- Freedom Blades brand/seal and platform name on the left; and
- the current synthetic user/account-status presentation on the right.

This row must:

- align both regions vertically;
- have stable spacing and height;
- wrap or stack deliberately on narrow screens;
- avoid competing with the navigation for the same horizontal line; and
- remain visually secondary to page content while clearly anchoring identity.

### Navigation row

Place the navigation in its own full-width row beneath the identity row.

The navigation must use this exact order on every page:

1. Overview
2. My Characters
3. Character Detail
4. Reconciliation
5. Council Queue
6. Components
7. Login

Login must remain last in DOM and visual order.

You may introduce clear shared wrapper classes such as:

- `.app-header-top`;
- `.app-navigation`;
- `.nav-menu`; and
- `.nav-link-login`.

Choose sensible names and apply the same structure on all seven pages.

## 5. Code-native navigation buttons

Do not generate raster or text-in-image buttons. Build the navigation from
semantic links and CSS.

Every navigation link must have:

- the same height, preferably at least 40 px and ideally 44 px;
- identical vertical padding and text baseline;
- consistent border thickness and radius;
- centered horizontal and vertical label alignment;
- a stable transparent border in the default state so active/hover borders do
  not move neighbouring content;
- a sufficiently large pointer target;
- no clipped text; and
- no dependence on fixed pixel widths that cannot accommodate the longest label.

Use a grid or deliberately distributed flex layout so the navigation reads as
one coherent component. On wide screens, seven aligned columns or another
balanced full-width distribution is preferred over content-width pills.

Avoid excessive rounding that makes every item resemble an unrelated capsule.
A restrained segmented rail or steel-framed button row is appropriate for the
Freedom Blades identity.

## 6. Visual states

### Default

- Muted but clearly legible text.
- Stable border and background.
- Equal dimensions across all items.

### Hover

- Subtle surface lift or steel-blue border emphasis.
- No movement, resizing or glow-heavy animation.

### Current page

- Keep `aria-current="page"`.
- Use more than color alone: for example a visible lower edge, inset marker,
  border treatment or restrained sword-line accent.
- Do not change item height, padding, font metrics or grid dimensions.

### Keyboard focus

- Preserve the existing high-contrast focus indicator.
- Ensure the outline is not clipped by the navigation container.
- Do not remove focus styling in favor of hover styling.

### Visited

- Navigation and button-like links must retain their intended component colors.
- Generic content-link visited rules must not override navigation styling.

## 7. Login treatment

Login is the final account-entry action.

- Keep it in the same aligned grid as the other navigation items.
- Give it a restrained account-action distinction, such as a slightly different
  border or subtle surface.
- Do not add extra margins that break column alignment.
- Do not make it the dominant primary action.
- On `login.html`, its active state must combine coherently with its account
  treatment.
- Do not add authentication behavior.

The synthetic user-status pill remains in the identity row because this is a
static screen catalogue. Record as a future production contract question that
Login and authenticated account/logout presentation should normally be mutually
exclusive; do not solve that backend state in this prototype correction.

## 8. Responsive navigation

### Wide desktop

- Brand/user identity row above.
- One well-aligned seven-item navigation row below.
- No unpredictable wrapping of individual items.
- No item should sit higher or lower than another.

### Tablet/intermediate widths

- Use a deliberate grid, for example four items followed by three, or another
  balanced arrangement.
- Maintain equal heights and aligned column edges.
- Do not let the browser arbitrarily wrap content-width pills.

### Narrow mobile

- Prefer a stable two-column grid.
- Keep DOM order row by row.
- Place Login deliberately last; it may span both columns if that produces a
  cleaner final row.
- The brand and synthetic user region may stack above the navigation.
- Ensure all seven choices are fully visible without horizontal scrolling.

Remove or override the older narrow rule that sets `.nav-menu` to
`overflow-x: auto`. The final responsive design must not depend on horizontal
scrolling or show partially clipped navigation choices.

Do not add a JavaScript hamburger menu in this step.

## 9. Semantics and accessibility

These are ordinary page-navigation links, not tabs.

- Preserve `<nav aria-label="Main Navigation">` and list semantics.
- Do not add `role="tab"`, `tablist`, `menu` or custom arrow-key behavior.
- Keep exactly one `aria-current="page"` per page.
- Keep link order identical across all pages.
- Preserve DOM-order keyboard traversal.
- Use visible labels; do not replace text with icons alone.
- Ensure focus outlines have space to render.

Small decorative CSS or inline SVG accents are permitted only if they are hidden
from assistive technology and do not disturb text alignment. They are not
required. Do not generate button images.

## 10. Preserve frozen Step 1 work

Do not change:

- character portrait layout, crop, dimensions or fallback behavior;
- character card responsive corrections;
- detail-page identity layout;
- state-selector or live-region behavior;
- reconciliation state configuration;
- Council modal behavior;
- OD-16 role demonstration;
- page body content;
- local assets or synthetic identities; or
- static/inert Phase 3 scope.

Do not edit the contrast/evidence tooling. Its audit may be stale until Claude
repairs it after visual freeze.

Do not add portrait hover, zoom, lightbox or preview interaction.

## 11. Verification

Run and report exact results for:

- `git diff --check`;
- `python3 design-prototype/tools/check_css_tokens.py`;
- a mechanical check that all seven pages use the exact required link order;
- a check that every page has exactly one `aria-current="page"`;
- a check that every navigation link retains visible text;
- a search proving the final nav CSS no longer uses horizontal overflow;
- a changed-path check; and
- HTML validation if an installed validator is available.

If a real browser is available, inspect all seven headers at 320 px, 768 px,
992 px and 1280 px. Record exact tooling and results. If not, explicitly state
that rendering, visual alignment, wrapping and keyboard interaction were not
runtime-tested.

Do not claim visual or keyboard verification from source inspection alone.

## 12. Return and stop

Return:

- exact files changed;
- final header DOM structure;
- desktop, tablet and mobile navigation layout;
- default, hover, active, visited and focus treatment;
- how Login is distinguished while remaining aligned;
- commands actually run and results;
- unavailable runtime checks; and
- public URLs Peter should inspect.

Then stop. Do not begin Step 2, alter portraits, update formal Phase 3 handoff,
edit audit tools, commit, push, deploy, modify Caddy or claim Step 1/Phase 3
acceptance.
