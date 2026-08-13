# Gemini handoff — remediate the Phase 3 visual prototype review

Copy everything below this line into Gemini as one prompt.

---

You are the frontend design implementer remediating the first independent review
of the Freedom Blades Phase 3 visual prototype.

Repository: `/opt/discord-bots/freedom-bot`

Current date: 2026-08-12

Maintainer and Acceptance Authority: Peter Duscha

Frontend implementer: Gemini

Backend implementer: Claude

Independent and security-focused reviewer: Codex

Public review URL: `https://freedom-blades.rpgworld.org`

## 1. Objective

Correct every Blocking and Important finding below, improve the Freedom Blades
visual identity, and return the static prototype for independent re-review.

This remains the implementation-plan §12.1 **static visual prototype**. Do not
start Phase 3 production integration. Do not add or imply working authentication,
authorization, uploads, imports, approvals, persistence or game-state mutation.

The result must be:

1. functionally clear;
2. genuinely usable at narrow and wide widths;
3. accessible to the documented WCAG 2.2 AA target; and
4. visually polished and recognizably Freedom Blades rather than a generic dark
   administration dashboard.

File completion is not acceptance. Codex re-reviews the result and Peter decides
the visual gate.

## 2. Mandatory context

Before planning or editing, read completely:

1. `AGENTS.md`
2. `.agents/AGENTS.md`
3. `docs/implementation-plan.md`, especially §12.1 and Phase 3
4. `docs/adr/0002-web-application-stack.md`
5. `docs/adr/0004-discord-oauth2-authentication.md`
6. `docs/rules/field-ownership.md`
7. closed OD-16 and OD-17 in `docs/discovery/open-decisions.md`
8. `docs/review/phase-3-visual-prototype-gemini-prompt.md`
9. `docs/review/phase-3-visual-prototype-implementation-plan.md`
10. `docs/review/phase-3-visual-prototype-handoff.md`
11. every current file under `design-prototype/`

Check `git status` before editing. The worktree contains maintainer and reviewer
changes. Preserve them. Do not reset, revert, clean, stage, commit or overwrite
unrelated work.

## 3. Authorized scope

You may edit only:

- `design-prototype/**`; and
- `docs/review/phase-3-visual-prototype-handoff.md`.

Do not edit the prompt, controlled implementation plan, implementation baseline,
ADRs, decisions, project status, production code, Caddy configuration or any
other file.

The public review route already serves `design-prototype/` directly, so saved
prototype changes can become externally visible immediately. Use only obviously
synthetic content and never place a secret, real player identity or production
record in those files.

## 4. Preserve the reviewer’s existing corrections

Codex already applied a narrow safety patch before publishing the review build.
Do not remove or weaken it:

- `.card-grid` uses `minmax(min(100%, 320px), 1fr)`;
- `.responsive-stack` collapses to one column at narrow widths;
- the Council modal moves focus in, traps Tab, handles Escape and returns focus;
- role-view controls expose `aria-pressed` and announce the active state;
- reconciliation progress exposes progressbar semantics;
- real maintainer identity references were replaced with synthetic identities;
- the character page no longer claims that every view is audited; and
- the token is served locally from
  `design-prototype/assets/freedom-blades-token.png`.

You may improve these implementations, but the resulting behavior must remain at
least as strong and must be evidenced rather than asserted.

## 5. Findings to remediate

### B-1 — modal accessibility and false evidence

The submitted modal declared `aria-modal="true"` and claimed focus trapping, but
only toggled `display`. The reviewer added a minimal focus implementation.

Complete and verify the pattern:

- focus enters on a predictable control;
- Tab and Shift+Tab remain inside;
- Escape closes it;
- focus returns to the exact opener;
- background content is not exposed as an active interaction surface while the
  modal is open; use a local inert/ARIA strategy appropriate to this static
  prototype;
- the dialog has an accessible name and useful description; and
- no alert claims that a transaction was recorded.

Test it with keyboard input, not source inspection alone.

### I-1 — character-detail mobile layout

The fixed `2fr 1fr` layout did not collapse because `responsive-stack` had no
rule. Preserve the reviewer’s correction and inspect the real page at 320 px,
768 px and 1280 px. Check long IDs, checksum content, ability cards, Council
controls and financial facts for overflow and sensible reading order.

### I-2 — card-grid overflow at 320 px

The original `minmax(320px, 1fr)` exceeded the content width after page padding.
Preserve or improve the correction. Verify that the index, My Characters and
component catalogue do not cause full-page horizontal scrolling at 320 px.

### I-3 — real identity and identity-shaped data

No prototype page may use Peter’s name, another real person’s name, real Discord
identity or a plausible real snowflake. Search the entire public prototype.

Use unmistakably synthetic identities such as:

- `Synthetic Member A`;
- `Synthetic Council Reviewer`;
- `synthetic-discord-user-001`; and
- visibly fictional character data that is not copied from real exports.

The documentation may record that the asset was confirmed by “the maintainer”;
the public prototype does not need the maintainer’s personal name.

### I-4 — invented security and audit guarantees

Remove statements that claim backend behavior not established by an accepted
Claude contract. In particular, do not say that every character read is audited,
that an action wrote a receipt, that a token is encrypted, or that a server check
happens on a particular cadence unless the accepted architecture explicitly
guarantees it.

Use accurate prototype language:

- “Production access must be enforced server-side.”
- “This control is an inert visual example.”
- “Exact security behavior is pending the accepted backend contract.”

Do not replace false certainty with vague reassurance.

### I-5 — inaccessible state demonstrations

For My Characters, role-view toggles, asynchronous progress and any other state
demonstrator:

- expose selected state with `aria-pressed`, tabs semantics or another correct
  pattern;
- announce meaningful state changes through a restrained live region;
- keep focus in a sensible place;
- ensure the content is useful with JavaScript disabled; and
- never present a visual toggle as production authorization.

### I-6 — reconciliation timing and progress semantics

The submitted button said “9.57s” but completed after three seconds. The measured
9.57 seconds is evidence that the production flow must be asynchronous, not a
required animation duration.

Prefer a presentation-state selector over a fake timer: queued, running,
completed, stale and failed. If a timed demonstration remains, label it clearly
as accelerated and never imply the animation models backend timing.

Progress must provide:

- accessible name;
- minimum, maximum and current value when determinate;
- an indeterminate treatment where appropriate;
- announced status text; and
- reconnect-safe job/batch identity language without inventing the polling
  interval or backend mechanism.

### I-7 — incomplete and suspect contrast evidence

Recalculate actual rendered foreground/background pairs. Do not report a token
against one surface if the component uses a different or translucent background.

Cover at minimum:

- normal and muted text on every surface;
- links in normal, hover, active and focus states;
- primary, secondary and danger buttons, including hover and disabled states;
- badges and alerts on their actual composed backgrounds;
- form text, labels, borders, errors and disabled states;
- table headers and responsive labels;
- focus indicators against every adjacent surface; and
- important non-text boundaries required by WCAG 1.4.11.

Record the calculation method and actual ratios. Adjust colors that fail. Do not
claim a blanket WCAG pass from a small sample.

### I-8 — verification claims exceeded the evidence

The first handoff claimed browser widths, keyboard behavior and complete WCAG
compliance but listed only Git and grep commands. Rewrite the handoff so each
claim is tied to evidence actually produced in this remediation.

If a browser, validator, accessibility engine or contrast tool is unavailable,
say so plainly. Do not substitute source inspection and call it browser testing.

### O-1 — the visual language is too generic

Keep the clean, serious dark interface, but make it recognizably Freedom Blades:

- use the circular seal as a deliberate identity anchor;
- derive restrained dividers, framing, directional accents or rhythm from the
  wing/sword geometry without tracing or repeating the logo;
- improve hierarchy, alignment, spacing and composition rather than adding
  ornamental clutter;
- distinguish calm member views from denser Council operational views within one
  design system; and
- avoid parchment, faux-medieval type, excessive glow, generic fantasy art and
  protected D&D publication imagery.

Do a genuine polish pass over every page. A few blue borders are not a brand
system.

## 6. Requested enhancement — character portraits

Add character imagery to the existing approved character surfaces:

- thumbnail portraits on `my-characters.html`;
- one larger portrait on `character-detail.html`; and
- an attractive initials-based fallback for a missing/unavailable portrait.

Portrait requirements:

- every portrait is entirely synthetic and contains no real player or Foundry
  asset;
- use repository-local raster files under
  `design-prototype/assets/portraits/`;
- record provenance and how each image was created;
- do not hotlink, use a CDN, embed base64, copy protected D&D art or use an
  identifiable real person;
- crop with `object-fit: cover`, preserve useful focal points and avoid layout
  shift with explicit dimensions/aspect ratio;
- provide meaningful alt text when the portrait adds identity, and empty alt
  text when the adjacent name makes it redundant; and
- make missing-image fallback part of the designed state, not a broken-image
  icon.

If you cannot create safely licensed synthetic raster portraits with the tools
available, implement polished local placeholders/fallbacks and record the image
generation as outstanding. Do not download arbitrary web images.

This enhancement does **not** authorize production Foundry image URLs. The
future backend/view-model contract must decide authorization, caching/proxying,
size/type limits, retention and fallback behavior.

## 7. Explicit non-goal — future content administration

Do not add an administrator editor for tools, languages, homebrew items, sources
or other vocabularies in this remediation. Peter directed the team to stay with
the current plan and only keep that later requirement in mind. It belongs to the
relevant typed Phase 5 packages and later approval workflow, not this Phase 3
prototype remediation.

Do not create a generic “add anything” form or key/value editor.

## 8. Page-by-page completion check

Review and refine every page, not only the files named by a finding:

- `index.html`: clear review-only scope and coherent visual introduction;
- `login.html`: identity, privacy-conscious copy and no invented security claim;
- `my-characters.html`: portraits, fallback, all state demonstrations and mobile
  usability;
- `character-detail.html`: portrait, read-only facts, OD-16 distinction,
  provenance and responsive behavior;
- `reconciliation.html`: accurate async concept, full required states, mappings,
  unresolved identities and deferred fields;
- `council-approval.html`: unmistakably forward-looking Phase 6 example, safe
  modal and no implication that Phase 3 mutates game state;
- `components.html`: components used by the pages, long-content stress examples,
  complete state patterns and corrected accessibility examples; and
- `README.md`: accurate tokens, contrast results, state inventory, asset
  provenance, responsive notes and backend questions without invented routes.

Keep shared behavior in shared CSS/JS where practical. Reduce excessive inline
styles and duplicated inline scripts when doing so materially improves the
eventual Jinja/HTMX handoff; do not perform a risky wholesale rewrite solely for
style purity.

## 9. Required verification

### 9.1 Mechanical checks

- Run `git diff --check`.
- Confirm Gemini changed only the authorized paths.
- Search for remote URLs, external fonts/scripts/styles, `fetch`, XHR, service
  workers, browser storage, form actions and production imports.
- Search for real identities and identity-shaped values.
- Confirm every local image and stylesheet is publicly readable from the review
  URL after saving.
- Validate HTML with a local standards-aware validator if available; otherwise
  report it as unavailable and perform named structural checks.

### 9.2 Browser and usability checks

Use a real browser if available and record the browser/tool and method:

- open every page from the public review URL or via `file://` with network
  disabled as appropriate;
- inspect every page at 320 px, 768 px and 1280 px;
- check for full-page horizontal overflow;
- keyboard-walk navigation, state controls, form examples and the modal using
  Tab, Shift+Tab, Enter, Space and Escape;
- verify focus visibility and order;
- inspect at 200% zoom and enlarged text;
- verify reduced-motion behavior;
- exercise normal, empty, loading/running, validation, denied, stale and
  system-error states; and
- inspect representative screenshots for alignment, hierarchy, density,
  portrait cropping and visual polish.

### 9.3 Accessibility and contrast checks

Run an available automated accessibility checker where possible, then manually
check the interaction patterns it cannot establish. Record exact results and
limitations. Automated output does not replace keyboard testing.

Calculate and record contrast for actual component pairs as specified in I-7.

## 10. Handoff requirements

Update `docs/review/phase-3-visual-prototype-handoff.md` in place. Do not create
another competing handoff.

The corrected handoff must contain:

- each review finding and its exact disposition;
- file list and meaningful changes;
- portrait provenance and fallback behavior;
- actual viewport/state coverage matrix;
- actual browser, keyboard, zoom, reduced-motion and accessibility evidence;
- actual contrast method and ratios;
- commands run and exact results;
- checks not run and why;
- known limitations and Claude contract questions;
- visual rationale and rejected alternatives; and
- explicit statements that the work is static, carries no independent approval,
  changes no production behavior and closes no gate.

Do not use “PASS,” “verified,” “accessible” or “WCAG compliant” without the
specific evidence that supports the word.

## 11. Stop conditions

Stop and report rather than guessing if:

- a requirement would require production/backend work;
- a portrait source or licence is unclear;
- the current reviewer patch conflicts with the design direction;
- a real identity or production-derived record is discovered;
- meaningful browser/accessibility verification cannot be performed; or
- a fix would require editing outside the authorized paths.

Do not commit, push, deploy, modify Caddy or claim acceptance. Return the result
for Codex independent re-review and Peter’s visual review.
