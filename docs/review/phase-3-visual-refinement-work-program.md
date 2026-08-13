# Phase 3 visual refinement — staged work program

**Date:** 2026-08-13
**Frontend implementer:** Gemini
**Independent reviewer:** Codex
**Visual acceptance authority:** Peter Duscha

## Purpose

Refine the accepted visual direction without mixing design iteration with the
remaining contrast-audit repair. Work proceeds through small visual gates so the
maintainer can inspect each result before the next change is authorized.

The prototype remains static and inert under implementation-plan §12.1.

## Operating rules

- Execute only one authorized step at a time.
- Stop after each step and return the public review URL plus an evidence-limited
  handoff.
- Peter visually inspects and either accepts the step or requests correction.
- Do not begin the next step until Peter explicitly authorizes it.
- Do not edit the contrast/token audit tools during visual refinement.
- Do not claim browser, keyboard or accessibility verification unless it was
  actually performed and the exact tool/method is recorded.
- Do not commit, push, deploy, modify Caddy or claim Phase 3 acceptance.
- Preserve synthetic identities, local-only assets and static/inert scope.

## Step 1 — stable portrait composition

Correct the current portrait overlap and establish a strong, non-interactive
default composition for character cards and character detail.

Deliverable:

- every character portrait is fully visible in the normal state;
- portraits cannot overlap adjacent portraits, text, controls or cards;
- imagery is more prominent without relying on hover;
- cards remain readable and balanced at narrow and wide widths;
- the existing image-error fallback remains stable; and
- no preview/lightbox interaction is added yet.

Gate: Peter inspects My Characters and Character Detail on desktop and mobile.

## Step 2 — accessible portrait emphasis and preview

After Step 1 acceptance, add restrained interaction:

- subtle in-frame emphasis on hover and keyboard focus;
- an explicit control for a larger preview;
- equivalent tap/click operation for touch devices;
- Escape, outside-click and focus-return behavior for an overlay if used;
- no layout shift or overlap with surrounding content; and
- reduced-motion behavior.

Hover must be an enhancement, never the only way to reveal content.

Gate: Peter tests mouse and phone interaction; Codex reviews interaction source
and accessibility boundaries.

## Step 3 — restrained liveliness and Freedom Blades identity

After Step 2 acceptance, perform a page-wide polish pass without redesigning the
information architecture:

- strengthen hierarchy and visual rhythm;
- use the Freedom Blades seal and sword/wing geometry as restrained identity
  cues;
- improve calm member views versus denser Council operational views;
- add depth and state feedback without excessive glow or generic fantasy
  ornament; and
- keep all text and controls legible.

Gate: Peter reviews every prototype page for visual direction and usability.

## Step 4 — responsive and state correction pass

After Step 3 acceptance, correct issues found during real visual inspection:

- 320 px, 768 px and 1280 px layouts;
- 200% zoom/reflow where available;
- portrait fallback presentation;
- empty, pending, completed, stale, failed, denied and error states;
- navigation wrapping and horizontal overflow; and
- visible focus and reduced motion.

This step is correction-only. It does not introduce another visual direction.

Gate: Peter accepts the visual prototype or returns a finite correction list.

## Step 5 — visual freeze and evidence closure

After visual acceptance:

- freeze the prototype HTML/CSS/JS except for reviewer-approved corrections;
- update the existing prototype handoff truthfully;
- record the final visual decisions and remaining runtime-test limitations; and
- verify the repository-local contrast and evidence tools against the frozen
  source and record their evidence classification accurately.

**Accepted 2026-08-13.** Peter Duscha accepted Step 5 and directed Codex to
reconcile the project before any further implementation. Codex reran the token
checker, the contrast tool's 11 self-tests, its 49-pair matrix, the freeze
manifest and `git diff --check`; all passed. The proposed Claude tooling task is
therefore superseded without execution. This acceptance closes only the §12.1
visual-design gate. It does not open production Phase 3 implementation.

## Explicitly deferred

- Production frontend/backend integration.
- Authentication, authorization and persistence.
- Foundry image contracts or production asset proxying.
- The future administrator editor for tools, languages, homebrew items and other
  controlled vocabularies.
- Phase transition or acceptance claims.
