# Gemini handoff — Phase 3 visual prototype second remediation

Copy everything below this line into Gemini as one prompt.

---

You are the frontend design implementer performing the second, narrowly scoped
remediation of the Freedom Blades Phase 3 static visual prototype.

Repository: `/opt/discord-bots/freedom-bot`

Current date: 2026-08-12

Maintainer and Acceptance Authority: Peter Duscha

Frontend implementer: Gemini

Backend implementer: Claude

Independent and security-focused reviewer: Codex

Public review URL: `https://freedom-blades.rpgworld.org`

## 1. Outcome required

Correct every finding in this prompt and return the prototype for another Codex
re-review. Preserve the successful portrait, responsive-layout, synthetic-data,
role-toggle and visual-polish work from the previous iteration.

This remains the implementation-plan §12.1 static visual prototype. Do not add
production integration, persistence, authentication, authorization, uploads,
imports, approval execution or backend routes. A visually simulated control must
not claim that a production event occurred.

Do not treat file completion as acceptance. Codex performs the next independent
review and Peter decides the visual gate.

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
10. `docs/review/phase-3-visual-prototype-remediation-gemini-prompt.md`
11. `docs/review/phase-3-visual-prototype-handoff.md`
12. every current file under `design-prototype/`

Run `git status` before editing. The worktree contains changes from the
maintainer, Codex and earlier Gemini work. Preserve them. Do not reset, clean,
revert, stage, commit or overwrite unrelated work.

## 3. Authorized scope

You may edit only:

- `design-prototype/**`; and
- `docs/review/phase-3-visual-prototype-handoff.md`.

Do not edit either Gemini prompt, the controlled implementation plan, project
status, decisions, ADRs, production code, Caddy configuration or any other file.

The public URL serves `design-prototype/` directly. Saved changes may become
public immediately. Use only synthetic data and repository-local assets. Do not
place secrets, real identities, production exports or production records there.

## 4. Findings to correct

### B-2 — dialog is hidden from the accessibility tree

This is blocking.

The dialog currently lives inside `#main-content`. `openDialog()` then applies
`aria-hidden="true"` to `#main-content`, which hides the dialog itself from
assistive technology. At the same time, the header and footer are not made inert.

Implement a sound modal structure:

- place the dialog/overlay outside the application shell that becomes inert;
- wrap all background UI—including skip link, header, main and footer—in one
  suitable application-shell element, or otherwise manage every background
  region explicitly;
- while open, make the complete background non-interactive using the native
  `inert` property, with appropriate `aria-hidden` handling only where needed;
- never put `aria-hidden="true"` on an ancestor of the active dialog;
- on close, restore the exact prior `inert` and ARIA state rather than assuming
  it was absent;
- move focus to a predictable dialog control;
- trap forward and reverse Tab navigation within the dialog;
- close on Escape;
- return focus to the exact opener;
- retain an accessible dialog name and useful description; and
- prevent background pointer interaction while the overlay is open.

Test accessibility-tree exposure and keyboard behavior in a real browser. Source
inspection alone is not sufficient. If the test environment cannot inspect the
accessibility tree, say so and do not claim that part was verified.

### I-9 — invented provenance and audit event remain

Remove the statement that the proposal came from an “authenticated Foundry
snapshot” and that an audit event was logged. Neither behavior is established by
an accepted backend contract.

The proposal may display clearly synthetic provenance identifiers as static
examples, but label them accurately, for example:

- “Synthetic snapshot reference shown for layout only.”
- “Production provenance and audit behavior are pending the accepted backend
  contract.”

Search every prototype page for similar unsupported claims. Do not claim that a
login, audit, receipt, import, lock or transaction occurred.

### I-10 — reconciliation selector is inaccessible and incomplete

The current Queued, Running and Completed buttons do not expose selection. The
live-region text remains unchanged, and the stale and failed states required by
the first remediation prompt are missing.

Implement five presentation states:

1. queued;
2. running;
3. completed;
4. stale; and
5. failed.

Use an appropriate single-selection pattern. A group of toggle buttons with
exactly one `aria-pressed="true"` is acceptable; a correctly implemented tablist
or radio group is also acceptable. Do not mix patterns.

For every state:

- expose the selected state programmatically;
- update visible status text;
- update a restrained `aria-live="polite"` status message;
- give the user enough information to understand the state without color;
- keep focus on the activated selector control;
- update step styling consistently;
- use determinate progress semantics only when a meaningful value exists;
- for an indeterminate running state, omit `aria-valuenow` and provide status
  text; if the visual example deliberately uses a determinate 50%, explain it;
- represent stale and failed states as terminal/error presentations without
  inventing retry, polling or backend behavior; and
- retain the synthetic batch/job identity and reconnect-safe design language.

The default HTML must remain understandable when JavaScript is disabled.

### I-11 — contrast audit is inaccurate and incomplete

Discard the current reported ratios and recompute them from the actual rendered
foreground and background colors. Several existing figures are mathematically
wrong. For reference, an independent calculation found approximately:

- `#f8fafc` on `#0b0f19`: `18.30:1`, not `16.2:1`;
- `#ffffff` on `#2563eb`: `5.17:1`, not `4.6:1`; and
- `#60a5fa` on `#111827`: `6.98:1`, not `8.2:1`.

Recalculate independently; do not blindly copy these reference values.

For translucent colors, alpha-composite the foreground/background layer over
the actual underlying surface before calculating contrast. Record the composed
hex color or the full compositing inputs so the result is reproducible.

Audit actual rendered pairs for at least:

- body, card, elevated-surface, muted and dim text;
- normal, hover, active, focus and visited links where applicable;
- primary, secondary and danger buttons in normal, hover and disabled states;
- selected state-selector buttons;
- all badge and alert variants on their real surfaces;
- form labels, values, placeholders, help, errors and disabled examples;
- table headers, cells and responsive `data-label` text;
- focus indicators against every adjacent surface on which they appear;
- borders or component boundaries subject to WCAG 1.4.11; and
- any inline color not represented by a token.

Correct failures. Record the calculator/script/tool used, inputs, results and
rounding convention. Do not label a non-text focus ratio “AAA”; WCAG non-text
contrast has a pass threshold but no A/AA/AAA grading in that manner.

Do not claim blanket WCAG compliance. State precisely what was checked and what
remains unverified.

### I-12 — verification claims are still unsupported

The handoff claims browser widths, keyboard behavior, zero overflow, image
loading and fallback behavior, but its recorded command list contains only Git
and grep. This repeats the previous evidence problem.

Run the checks you claim and record:

- browser name and version;
- automation or manual method;
- exact page URL;
- viewport dimensions;
- exact interaction sequence for the dialog and state controls;
- how horizontal overflow was measured;
- accessibility-tree or automated-checker tool and result, if used;
- screenshot filenames or another durable artifact where produced; and
- limitations and checks not run.

If browser automation is available, use it. If it is unavailable, do not invent
manual browser evidence. Restrict claims to source/mechanical inspection and
make the missing browser check explicit for Peter or Codex to perform.

The handoff’s “Verification Commands Run” section must include all commands and
tools that support its claims. “Verified” is not evidence by itself.

### I-13 — portrait files have incorrect formats

All three files currently named `.png` contain JPEG/JFIF data. Correct this in
one of two ways:

- convert them to genuine PNG files while retaining `.png`; or
- rename them to `.jpg`/`.jpeg` and update every HTML and documentation
  reference.

Confirm the result with `file` or an equivalent format inspector. Ensure the web
server returns an appropriate MIME type at the public URL. Preserve synthetic
portrait provenance and do not regenerate or replace the artwork unnecessarily.

### N-1 — portraits are incorrectly clickable

Remove the portrait `onclick` handlers that hide successfully loaded images.
Portraits are not controls and must not acquire button semantics or keyboard
behavior. Show the initials fallback only from `onerror` or an equivalent
load-failure mechanism.

After an image error:

- hide the broken-image presentation;
- reveal the correctly sized initials fallback;
- avoid announcing duplicate character names; and
- preserve the card/hero layout without shift.

Test at least one fallback deliberately, then restore the normal production-like
prototype state.

### N-2 — fallback documentation is inaccurate

The fallback is a styled HTML `<div>`, not an SVG. Describe it accurately as an
HTML/CSS initials fallback unless you actually replace it with a real SVG-based
implementation. Keep implementation and handoff terminology consistent.

## 5. Preserve these successful corrections

Do not regress:

- the local Freedom Blades token asset and visual identity;
- synthetic character portraits and identities;
- the portrait thumbnail and hero layouts;
- `.card-grid` using a narrow-safe minimum;
- `.responsive-stack` collapsing at narrow widths;
- long ID and checksum wrapping;
- character state and OD-16 role controls exposing selected state;
- the absence of the fake 9.57-second timer;
- static/inert Phase 3 scope language;
- local-only assets with no remote fonts, scripts, CSS or images; or
- reduced-motion and visible-focus behavior.

Do not add the future administration editor for tools, languages, homebrew items
or other vocabularies. Keep that requirement for its later typed package and
approval workflow, as already directed by Peter.

## 6. Mechanical verification

Run and record at minimum:

- `git status --short` before and after;
- `git diff --check`;
- a changed-path check proving this remediation stayed within authorized scope;
- searches for external URLs, network APIs, browser storage, service workers and
  form actions;
- searches for real identities, plausible Discord snowflakes and unsupported
  audit/security/transaction claims;
- format inspection for every portrait;
- an HTML validator if available; and
- a reproducible contrast-calculation command or named tool.

Do not state that `git status` proves only authorized paths were changed unless
you distinguish pre-existing worktree changes from changes made during this
specific remediation.

## 7. Browser verification matrix

If a real browser is available, inspect every page at 320 px, 768 px and 1280 px.
At minimum verify:

- no full-page horizontal overflow;
- navigation remains operable;
- portraits crop correctly and fallbacks preserve layout;
- dialog accessibility-tree visibility and complete keyboard cycle;
- reconciliation selection, announcements and all five states;
- character and role state controls;
- visible focus order;
- 200% zoom or equivalent reflow;
- reduced-motion behavior; and
- representative normal, empty, running, completed, stale, failed, validation,
  denied and system-error states.

Record actual results rather than a generic pass sentence.

## 8. Handoff update

Update `docs/review/phase-3-visual-prototype-handoff.md` in place. Do not create a
second competing handoff.

The corrected handoff must:

- add B-2, I-9 through I-13, N-1 and N-2 with exact dispositions;
- correct or withdraw all inaccurate statements from the earlier handoff;
- identify the modal DOM/inert strategy;
- document all five reconciliation states and their accessibility behavior;
- give reproducible contrast inputs and results;
- state the true portrait formats and provenance;
- describe the fallback accurately;
- list exact commands, browser/tool versions and interaction evidence;
- separate checks actually run from checks not run;
- identify remaining limitations and Claude contract questions; and
- repeat that this is static work with no independent approval or production
  behavior.

Avoid “B-1 compliant,” “WCAG compliant,” “fully accessible,” “verified” and
similar categorical language unless every relevant assertion is backed by
specific evidence.

## 9. Stop conditions

Stop and report instead of guessing if:

- a change would require backend or production integration;
- the dialog cannot be kept outside the inert background shell;
- portrait conversion would alter or corrupt the artwork;
- a source/licence or identity is uncertain;
- meaningful browser/accessibility testing cannot be run;
- a required fix needs a file outside the authorized scope; or
- existing maintainer or Codex work conflicts with the requested change.

Do not commit, push, deploy, modify Caddy or claim acceptance. Return the result
for Codex independent re-review and Peter’s visual review.
