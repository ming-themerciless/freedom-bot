# Gemini handoff — Phase 3 visual prototype final focused remediation

Copy everything below this line into Gemini as one prompt.

---

You are the frontend design implementer performing a third, tightly bounded
remediation of the Freedom Blades Phase 3 static visual prototype.

Repository: `/opt/discord-bots/freedom-bot`

Current date: 2026-08-12

Maintainer and Acceptance Authority: Peter Duscha

Frontend implementer: Gemini

Backend implementer: Claude

Independent and security-focused reviewer: Codex

Public review URL: `https://freedom-blades.rpgworld.org`

## 1. Required outcome

Correct the six remaining findings in this prompt and return the prototype for
Codex re-review. There are no remaining blocking findings. Make the smallest
sound changes needed and preserve all successful work from the previous
iterations.

This remains the implementation-plan §12.1 static visual prototype. Do not add
backend behavior, production integration, persistence, authentication,
authorization, imports, locks, audit logging, transactions or recovery logic.

Completion is not acceptance. Codex performs independent re-review and Peter
decides the visual gate.

## 2. Mandatory context and worktree safety

Before editing, read completely:

1. `AGENTS.md`
2. `.agents/AGENTS.md`
3. `docs/implementation-plan.md`, especially §12.1 and Phase 3
4. `docs/rules/field-ownership.md`
5. `docs/review/phase-3-visual-prototype-remediation-gemini-prompt.md`
6. `docs/review/phase-3-visual-prototype-remediation-2-gemini-prompt.md`
7. `docs/review/phase-3-visual-prototype-handoff.md`
8. every current file under `design-prototype/`

Capture `git status --short` before editing. The worktree contains pre-existing
maintainer, Codex and Gemini changes, and the prototype is currently untracked.
Do not reset, clean, revert, stage, commit or overwrite unrelated work.

## 3. Authorized scope

You may edit only:

- `design-prototype/**`; and
- `docs/review/phase-3-visual-prototype-handoff.md`.

Do not edit prompts, plans, decisions, status documents, ADRs, production code,
Caddy configuration or any other file.

The public URL serves the prototype directly. Never add secrets, real identities,
production exports or externally hosted assets.

## 4. Remaining findings

### I-14 — unsupported audit and locking claims

Remove or rewrite these two statements in `my-characters.html`:

- character linkages “are audited”; and
- character records “are temporarily locked to prevent stale reads.”

Neither is established by an accepted backend contract. Use precise static
prototype language, for example:

- “No active character ownership links are shown in this prototype state.”
- “A reconciliation preview is represented as pending. Production availability
  behavior is pending the accepted backend contract.”

Search every prototype file again for claims or implications that a production
login, import, audit, lock, receipt, transaction, encryption, recovery process or
authorization event occurred. Synthetic identifiers may remain when clearly
labelled as layout examples.

### I-15 — invented reconciliation recovery instruction

Remove “Reconnect required” from the failed reconciliation state. It invents a
recovery procedure.

The failed state should say what the visual state represents and explicitly
defer operational behavior, for example:

“Synthetic schema-validation failure state. Production recovery behavior is
pending the accepted backend contract.”

Do not add retry, polling, reconnect, escalation or rollback instructions unless
an accepted backend contract already defines them.

### I-16 — complete the contrast audit

The existing ratios are plausible but the matrix is incomplete. Expand the
reproducible audit to cover every material rendered state, not merely one example
per component family.

At minimum calculate and record:

1. body, card, elevated, muted and dim text;
2. navigation links in normal, hover and active states;
3. ordinary content links in normal, hover, active, visited and focus states, or
   explicitly document when a distinct state is not styled;
4. primary buttons in normal, hover and disabled presentations;
5. secondary buttons in normal, hover, disabled and selected
   (`aria-pressed="true"`) presentations;
6. danger buttons in normal and hover presentations;
7. the Discord login button in normal and hover presentations;
8. primary, success, warning, danger, deferred and info badges/alerts on their
   actual composed surfaces;
9. form labels, input/select values, placeholder/help text if present,
   validation-error text, disabled controls if present, and their actual
   backgrounds;
10. table headers, table cells and narrow-screen `data-label` text;
11. focus indicators against every adjacent background on which they appear;
12. component boundaries governed by WCAG 1.4.11, including form borders,
    meaningful button borders, card/table boundaries, progress track/fill and
    status distinctions;
13. state-specific reconciliation borders and fills; and
14. every inline literal color, including `#f59e0b`.

For translucent colors, alpha-composite against the real underlying surface
before calculating. If the same component can occur on multiple surfaces,
calculate the relevant worst-case pair or list each actual pair.

Use a reproducible repository-local calculation artifact under
`design-prototype/`—for example `design-prototype/tools/calc_contrast.py`—rather
than relying solely on a scratch file outside the repository. The script must be
read-only with respect to prototype files and require no network access.

Record:

- exact inputs;
- composed colors;
- unrounded ratios and displayed rounding convention;
- applicable threshold (4.5:1, 3:1, or not applicable);
- result; and
- any state for which contrast is not the applicable success criterion.

Correct any failures in CSS/tokens and recalculate. Do not call non-text contrast
“AAA,” and do not claim that the entire prototype is WCAG compliant. State only
the tested conformance evidence and limitations.

### I-17 — make verification reporting fully truthful

No Chromium, Firefox, Playwright, Puppeteer or Axe installation was found during
Codex’s review. Unless you actually locate and run suitable tooling, explicitly
state that these checks were **not performed**:

- graphical browser rendering;
- accessibility-tree inspection;
- keyboard interaction testing;
- viewport and horizontal-overflow measurement;
- 200% zoom/reflow testing;
- reduced-motion runtime testing;
- image fallback runtime testing; and
- automated accessibility scanning.

Do not list “keyboard cycle,” “dynamic DOM inspection,” “browser verified,”
“zero overflow,” or similar runtime claims as evidence when you only inspected
HTML, CSS and JavaScript source.

Source inspection may support carefully limited statements such as:

- “The script contains Tab/Shift+Tab boundary handling.”
- “The dialog is structurally outside `#app-shell`.”
- “Five selector buttons have initial `aria-pressed` attributes.”

If you do find and run a real browser or accessibility tool, record its exact
name, version, invocation, URL, viewport, interaction sequence, output and
limitations. Never infer runtime success from source alone.

### N-3 — preserve and restore prior inert state

The modal currently always removes `inert` from `#app-shell` on close. Instead:

- record whether `#app-shell` was inert before opening;
- record the exact prior inert attribute/property state needed for restoration;
- apply inert while the dialog is open; and
- on close, restore the prior state rather than always removing it.

Keep the dialog outside the inert shell. Preserve focus entry, Tab/Shift+Tab
boundary handling, Escape dismissal, exact opener focus return, accessible name
and description, and overlay pointer blocking.

Do not claim runtime keyboard or accessibility-tree verification unless it was
actually performed with suitable tooling.

### N-4 — report Git scope honestly

The prototype is untracked and the worktree already contains unrelated changes.
The current `git status` output cannot prove which edits were made during one
Gemini run.

Before editing, create a non-destructive inventory or checksums of files within
the authorized paths and save the evidence outside the repository or quote it in
the handoff. After editing, compare against that baseline. In the handoff:

- list files changed during this remediation based on the before/after evidence;
- separately list pre-existing worktree changes visible in Git;
- do not say Git status alone proves authorized scope; and
- state any attribution limitation plainly.

Do not modify unrelated files merely to make Git output look cleaner.

## 5. Preserve successful work

Do not regress:

- the corrected modal placement outside `#app-shell`;
- complete background inerting while the modal is open;
- focus entry, focus-loop code, Escape and focus-return code;
- all five reconciliation presentation states;
- single selected `aria-pressed` state and changing live-region content;
- genuine PNG portrait formats;
- non-clickable portraits and `onerror`-only HTML/CSS initials fallbacks;
- synthetic identities and local-only assets;
- card-grid and responsive-stack corrections;
- long-value wrapping;
- character and OD-16 role selector semantics;
- reduced-motion CSS and visible focus styling;
- Freedom Blades visual identity and portrait composition; and
- explicit static/inert Phase 3 scope.

Do not add the later administrator editor for tools, languages, homebrew items or
other vocabularies. That remains deferred to its typed package and approval
workflow.

## 6. Required mechanical checks

Run and record exact commands and results for:

- `git status --short` before and after;
- the authorized-path before/after comparison;
- `git diff --check`;
- searches for external URLs, network APIs, browser storage, service workers and
  form actions;
- searches for real identities and plausible Discord snowflakes;
- searches for unsupported audit, authentication, lock, transaction, receipt,
  encryption and recovery claims;
- `file design-prototype/assets/portraits/*`;
- the repository-local contrast script;
- an HTML validator if installed, otherwise state that it was unavailable; and
- discovery checks for browser/accessibility tooling.

Do not install packages, download tools or access arbitrary external services
solely to manufacture verification evidence.

## 7. Handoff requirements

Update `docs/review/phase-3-visual-prototype-handoff.md` in place. Do not create a
competing handoff.

The handoff must:

- add I-14 through I-17 and N-3 through N-4 with exact dispositions;
- remove or correct contradictory evidence claims from earlier versions;
- include the complete contrast matrix or link it to a repository-local report
  while summarizing all categories and failures/fixes;
- identify the repository-local contrast command and rounding method;
- distinguish source inspection from runtime verification;
- explicitly enumerate unavailable/unperformed browser checks;
- describe exact inert-state preservation logic;
- give a defensible remediation-specific changed-file list;
- preserve portrait format/provenance and fallback documentation;
- list remaining backend-contract questions without answering them speculatively;
  and
- state that this work has no independent approval and changes no production
  behavior.

Avoid categorical “verified,” “accessible,” “WCAG compliant,” “B-2 compliant,”
or “all checks pass” language unless the exact claim is supported by recorded
evidence.

## 8. Stop conditions

Stop and report instead of guessing if:

- a fix would require backend or production behavior;
- contrast cannot be reproduced from actual component colors;
- an existing color failure cannot be corrected without material redesign;
- any asset identity, provenance or licence is uncertain;
- a required edit falls outside authorized paths; or
- existing maintainer or Codex work conflicts with the remediation.

Do not commit, push, deploy, modify Caddy or claim acceptance. Return the result
for Codex independent re-review and Peter’s visual review.
