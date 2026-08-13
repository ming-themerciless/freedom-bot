# Gemini handoff — Phase 3 evidence-integrity remediation

Copy everything below this line into Gemini as one prompt.

---

You are the frontend implementer performing a sixth, evidence-focused
remediation of the Freedom Blades Phase 3 static visual prototype.

Repository: `/opt/discord-bots/freedom-bot`

Current date: 2026-08-13

Maintainer and Acceptance Authority: Peter Duscha

Frontend implementer: Gemini

Backend implementer: Claude

Independent reviewer: Codex

## 1. Objective

Make the contrast report and its source citations truthful, reproducible and no
broader than the tool can prove. Correct the two remaining wrong color mappings,
mechanically link reconciliation audit values to the JavaScript state object,
and repair remediation-specific scope reporting.

The visible interface is not the principal problem in this iteration. The
problem is evidence integrity. Do not create another “complete mechanical audit”
by attaching source-like labels to hard-coded assumptions.

This remains a static Phase 3 prototype. Completion is not acceptance; Codex
re-reviews it and Peter decides the visual gate.

## 2. Mandatory preparation and scope

Read completely before editing:

1. `AGENTS.md`
2. `.agents/AGENTS.md`
3. `docs/implementation-plan.md`, especially §12.1
4. `docs/review/phase-3-visual-prototype-remediation-5-gemini-prompt.md`
5. `docs/review/phase-3-visual-prototype-handoff.md`
6. `design-prototype/css/tokens.css`
7. `design-prototype/css/styles.css`
8. all inline `<style>` attributes and blocks in `design-prototype/*.html`
9. `RECONCILIATION_STATES` and `setJobState()` in
   `design-prototype/reconciliation.html`
10. `design-prototype/tools/calc_contrast.py`
11. `design-prototype/README.md`

You may edit only:

- `design-prototype/**`; and
- `docs/review/phase-3-visual-prototype-handoff.md`.

Do not reset, clean, revert, stage, commit, push, deploy, install packages or
modify Caddy. Preserve unrelated work.

## 3. Capture a correct remediation-6 baseline

Before editing, capture every authorized file, including tools and the handoff:

```bash
find design-prototype -type f -print0 | sort -z | xargs -0 sha256sum > /tmp/freedom-blades-remediation-6-before.sha256
sha256sum docs/review/phase-3-visual-prototype-handoff.md >> /tmp/freedom-blades-remediation-6-before.sha256
```

After **all implementation and documentation edits are finished**, create the
after inventory using the identical command and write it to
`/tmp/freedom-blades-remediation-6-after.sha256`.

Do not edit the handoff after the after inventory. Because including a document’s
own final hash inside that same document is self-referential, report the handoff
as an authorized documentation edit separately and explain this limitation. For
the implementation-specific comparison, either:

- compare prototype files before/after and list the handoff separately; or
- create the final comparison after the handoff and quote the result outside the
  handoff/walkthrough without claiming the handoff embeds its own final hash.

Never claim a file changed unless the recorded comparison demonstrates it.
Explicitly supersede remediation 5’s four-file claim: its recorded diff proved
only `reconciliation.html` and `calc_contrast.py` changed before its after
snapshot, while the handoff was updated afterward.

## 4. Evidence classification is mandatory

Every contrast row must have one of these evidence classes:

1. **extracted** — foreground/background declarations are parsed from an actual
   CSS selector, inline style, token, or JavaScript state object;
2. **derived** — a documented inheritance/compositing operation whose inputs are
   all extracted; or
3. **manual assumption** — a reviewer-authored environmental/background
   assumption not mechanically derived.

For each row, record:

- evidence class;
- real file path;
- real selector, element/style locator, token, or JS state/property;
- extracted declaration text;
- inherited-from source when applicable;
- resolved foreground/background;
- underlying surface and alpha when applicable; and
- ratio and threshold.

Never cite a selector or file location that does not exist. The tool must fail if
an `extracted` or `derived` row refers to a missing source. Manual assumptions
must not be counted as mechanically verified.

It is acceptable—and preferable—to reduce the mechanically verified matrix to
the states the scoped parser can genuinely resolve. Keep other useful rows in a
separate “manual/static review assumptions” section with honest limitations.

## 5. Correct known wrong rows

### Selected secondary buttons

Actual CSS for `.btn-secondary[aria-pressed="true"]` uses:

- foreground: `--fb-color-accent` (`#60a5fa`);
- background: `--fb-color-bg-subtle` (`#1e293b`); and
- border: `--fb-color-primary`.

The current audit incorrectly supplies white foreground. Extract all three
declarations from the selector and resolve them through `tokens.css`. Audit both
text/background and meaningful border/adjacent-background contrast.

### Focus ring

There is no `.btn-primary:focus-visible` rule and no white focus ring. The shared
focus rule uses `--fb-focus-ring`, which resolves recursively to
`--fb-color-accent`.

Parse the grouped focus selector and nested variable value. Audit the accent ring
against its relevant adjacent surfaces, including the primary button background
where applicable. Cite the real grouped rule, not a fictional selector.

## 6. Remove or replace nonexistent source citations

The current report cites sources that do not exist, including:

- `styles.css:a`, `a:hover`, `a:visited`;
- `styles.css:label`, `input`, `select`, `.form-help`;
- `styles.css:.btn-primary:focus-visible`; and
- `my-characters.html:gp text color`.

For each row:

- locate the actual inline style or applicable class and extract it; or
- reclassify it as inherited/manual with the real source chain; or
- remove it from the mechanically verified matrix.

The `#f59e0b` literal is currently in `character-detail.html`, not
`my-characters.html`. Cite and parse the actual element/style occurrence.

Generic anchor states are not defined globally in `styles.css`. Do not invent
them. Audit concrete link classes such as `.nav-link`, `.brand-title`, `.btn`, or
the real inline/class styling that exists.

Form examples use inline styles in `components.html`. Either parse those inline
styles by a stable element ID or label them as manual inspection; do not cite
nonexistent global selectors.

## 7. Mechanically extract reconciliation states

Parse `RECONCILIATION_STATES` directly from
`design-prototype/reconciliation.html`. Do not duplicate its five colors as
independent Python constants.

The parser may be narrowly scoped to this literal object, but it must:

- find the object by name;
- extract exactly queued, running, completed, stale and failed;
- extract `fill`, `width`, `valuenow` and `alertClass` for each;
- reject duplicate/missing states or properties;
- reject unsupported/dynamic expressions;
- verify that `setJobState()` consumes the selected object’s properties; and
- feed the extracted fill colors directly into contrast evaluation.

Changing any state’s `fill` in a temporary test fixture must change the extracted
audit value or trigger the expected failure without editing an audit constant.

## 8. Build real drift and negative tests

The current tests check only a few positive values. Add fixture-based or
temporary-copy mutation tests that never alter the working prototype.

At minimum prove:

- changing `.btn-secondary[aria-pressed="true"]` foreground is detected and the
  resolved audit value changes or fails an expectation;
- removing a required selector causes a clear failure;
- removing a required property causes a clear failure;
- inserting an unresolved token causes a clear failure;
- changing the shared focus-ring token changes the resolved focus color;
- changing each reconciliation state fill is detected from the JS object;
- removing a reconciliation state/property causes a clear failure;
- a nonexistent claimed source cannot be emitted as extracted evidence; and
- malformed CSS/JS supported syntax fails closed rather than silently falling
  back to a hard-coded value.

Test names must describe these behaviors. “3/3 tests passed” is not sufficient if
one broad test contains only positive assertions. Report the actual test count.

## 9. Audit architecture requirements

Refactor `calc_contrast.py` as needed so:

- every mechanically verified row receives colors from extraction functions;
- inherited values are resolved from real base selectors;
- nested CSS variables resolve recursively with cycle detection;
- `rgba()` values retain raw color, alpha and underlying-surface evidence;
- manual assumptions are stored separately and not counted as extracted passes;
- missing sources/properties/tokens fail the command;
- required contrast failures return nonzero;
- exempt and informational cases are not counted as passes;
- output totals distinguish extracted, derived, manual, pass, fail, exempt and
  informational rows; and
- output wording says “static source consistency audit,” never browser/rendered
  verification.

Do not claim to parse inline HTML styles unless the tool actually does so.

## 10. Scope-evidence correction

Generate the remediation-6 after inventory only after implementation and README
edits are complete. Compare it with the baseline and derive the implementation
changed-file list from that diff.

Update the handoff last. State separately:

- implementation files proven changed by the prototype inventory;
- the handoff itself was updated as the final documentation action;
- pre-existing Git changes; and
- `/tmp` evidence is session-local.

Do not use `git status` to attribute untracked-file changes to this run.

## 11. Documentation corrections

Update `design-prototype/README.md` and the existing handoff in place.

They must:

- mark remediation 5’s 47-pass/1-exempt report as superseded because extraction
  coverage and citations were incomplete;
- replace false source locations and wrong selected/focus colors;
- separate extracted/derived evidence from manual assumptions;
- state the parser’s exact supported CSS/inline-style/JS subset;
- list negative drift tests and results;
- give honest totals;
- retain all eight unperformed browser/runtime disclosures;
- report remediation-6 scope evidence accurately; and
- state that no acceptance, full accessibility or production behavior is
  implied.

## 12. Preserve resolved work

Do not regress:

- zero undefined token references;
- corrected color parsing and alpha compositing;
- coherent token definitions;
- explicit reconciliation state configuration and UI consumption;
- modal placement, inert restoration and focus-management source logic;
- five state selectors, live-region changes and ARIA values;
- removal of unsupported backend claims;
- genuine local portraits and fallbacks;
- responsive layouts, focus CSS and reduced motion;
- synthetic identities and local-only assets; or
- runtime-test disclosures.

Do not add backend behavior or the deferred administration editor.

## 13. Required verification

Run and record:

- remediation-6 before/after prototype inventories and comparison;
- `python3 design-prototype/tools/check_css_tokens.py`;
- the complete test suite with actual test count;
- `python3 design-prototype/tools/calc_contrast.py`;
- `git diff --check`;
- `git status --short`;
- external URL/network/storage/service-worker/form-action searches;
- identity/snowflake searches;
- unsupported backend-claim searches;
- portrait format inspection; and
- HTML validation if already installed, otherwise state unavailable.

## 14. Stop conditions

Stop and report rather than guessing if:

- a row cannot be linked to a real source;
- inheritance or an underlying surface is ambiguous;
- the scoped parser cannot safely handle required syntax;
- a contrast failure requires material redesign;
- a change requires backend behavior; or
- an edit is needed outside authorized scope.

Do not stage, commit, push, deploy, modify Caddy or claim acceptance. Return the
result for Codex independent re-review and Peter’s visual review.
