# Gemini handoff — visual refinement Step 1: stable portrait composition

Copy everything below this line into Gemini as one prompt.

---

You are implementing **Step 1 only** of the staged Freedom Blades Phase 3 visual
refinement program.

Repository: `/opt/discord-bots/freedom-bot`

Current date: 2026-08-13

Public review URL: `https://freedom-blades.rpgworld.org`

Frontend implementer: Gemini

Independent reviewer: Codex

Visual acceptance authority: Peter Duscha

## 1. Read before editing

Read completely:

1. `AGENTS.md`
2. `.agents/AGENTS.md`
3. `docs/implementation-plan.md`, especially §12.1
4. `docs/review/phase-3-visual-refinement-work-program.md`
5. `design-prototype/css/tokens.css`
6. `design-prototype/css/styles.css`
7. `design-prototype/my-characters.html`
8. `design-prototype/character-detail.html`

Inspect the current public pages and local source if your environment permits.
Peter reports that the character pictures overlap: only the last portrait and
parts of the others are visible. Treat that first-hand report as authoritative
even if your preview does not reproduce it.

Check `git status --short` before editing. Preserve all existing maintainer,
Codex and Gemini work. Do not reset, clean, revert, stage or commit.

## 2. Step 1 objective

Create a stable, attractive default portrait composition in which every
character image is fully visible and visually important without depending on
hover, focus, JavaScript or a preview overlay.

This step establishes the base layout only. Stop when it is complete.

## 3. Authorized files

You may edit only:

- `design-prototype/css/styles.css`;
- `design-prototype/my-characters.html`; and
- `design-prototype/character-detail.html`.

Do not edit assets, tokens, README, handoff documents, contrast tools, other
pages, production code or Caddy configuration.

## 4. Required character-card treatment

On `my-characters.html`:

- show one prominent portrait per card;
- ensure portraits never overlap one another, adjacent cards, text or controls;
- prefer a deliberate card-media region rather than a small account-avatar
  treatment;
- use an explicit aspect ratio and dimensions to prevent layout shift;
- use `object-fit: cover` and a sensible `object-position`;
- keep the character’s name, mutable display name, status and core facts easy to
  scan;
- keep the profile action clearly associated with the character;
- make cards feel character-led rather than administration-led; and
- preserve all three characters and their synthetic data.

A strong default is a full-width card image with a restrained aspect ratio above
the character information. You may choose another composition if it solves the
overlap more clearly and remains usable.

Do not create a stacked deck of portraits, negative-margin collage or overlapping
gallery.

## 5. Required character-detail treatment

On `character-detail.html`:

- make the portrait a clear identity anchor;
- keep the stable ID, character name, display name, class/species and badges
  readable beside or below it;
- avoid squeezing the text into an unusably narrow column;
- stack the portrait and identity content cleanly on narrow screens;
- preserve the facts, provenance, OD-16 role demonstration and Council content;
  and
- prevent the portrait from overlapping the snapshot-freshness block.

## 6. Responsive requirements

Source and layout design must account for at least:

- 320 px narrow mobile;
- 768 px tablet; and
- 1280 px desktop.

At narrow widths:

- cards must remain within the viewport;
- images must not exceed their containers;
- identity blocks must wrap without clipping;
- buttons must remain reachable; and
- long identifiers must retain the existing wrapping safeguards.

Do not use fixed positioning, negative margins or transforms for the default
portrait layout.

## 7. Fallback and semantics

Preserve the current local PNG images and HTML/CSS initials fallback.

- The fallback must occupy the same media region and aspect ratio as the image.
- Keep fallback activation limited to image load failure.
- Images remain non-clickable in Step 1.
- Do not add `tabindex`, button roles, modal markup, hover enlargement or click
  handlers.
- Avoid duplicate accessible names between the image and adjacent character
  heading. Choose alt text deliberately and document the choice in your response.

## 8. Visual boundaries

Keep the established dark, restrained Freedom Blades design. Improve portrait
framing, spacing, hierarchy and card balance without starting the broader Step 3
polish pass.

Do not add:

- a lightbox or enlarged preview;
- hover/focus zoom;
- carousels;
- new generated images;
- ornamental fantasy frames;
- remote assets, fonts or scripts; or
- backend behavior.

## 9. Preserve existing behavior

Do not regress:

- state-selector `aria-pressed` behavior;
- live-region text updates;
- OD-16 role-view behavior;
- responsive card-grid safety;
- the responsive detail stack;
- focus styles and reduced-motion rules;
- synthetic identities;
- local-only assets; or
- static/inert prototype language.

Do not touch the contrast/evidence audit. It will be repaired by Claude only
after the visual design is frozen.

## 10. Verification and truthful reporting

Run:

- `git diff --check`;
- the existing CSS token-reference check;
- searches confirming portrait paths remain local;
- searches confirming portrait images have no `onclick` or interactive role;
- a changed-path check; and
- HTML validation if a validator is already available.

If a real browser is available, inspect both pages at 320 px, 768 px and 1280 px
and record the exact browser/tool and results. If not, explicitly state that
rendering and overlap were not runtime-tested.

Do not modify the audit tool merely because its current contrast report becomes
stale after this visual change.

## 11. Return and stop

Return:

- exact files changed;
- concise design rationale;
- description of the desktop, tablet and mobile composition;
- fallback and alt-text decisions;
- commands actually run and results;
- runtime checks not performed; and
- the public URLs Peter should inspect.

Then stop. Do not begin Step 2, add hover behavior, update the formal Phase 3
handoff, commit, push, deploy, modify Caddy or claim acceptance.
