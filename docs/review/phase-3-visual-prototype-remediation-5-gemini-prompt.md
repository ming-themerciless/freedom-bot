# Gemini handoff — Phase 3 selector-audit alignment remediation

Copy everything below this line into Gemini as one prompt.

---

You are the frontend implementer performing a fifth, narrowly technical
remediation of the Freedom Blades Phase 3 static visual prototype.

Repository: `/opt/discord-bots/freedom-bot`

Current date: 2026-08-13

Maintainer and Acceptance Authority: Peter Duscha

Frontend implementer: Gemini

Backend implementer: Claude

Independent reviewer: Codex

## 1. Required outcome

Make the static contrast audit faithfully describe and mechanically verify the
actual CSS selectors and JavaScript-driven reconciliation states. Correct the
scope-evidence report. Do not redesign the interface or broaden Phase 3.

The design-token contract and color-math primitives are now repaired. Preserve
them. The remaining defect is that the audit still calculates manually invented
pairs rather than the colors the prototype actually applies.

Completion is not acceptance. Codex re-reviews the result and Peter decides the
visual gate.

## 2. Mandatory preparation and authorized scope

Read completely before editing:

1. `AGENTS.md`
2. `.agents/AGENTS.md`
3. `docs/implementation-plan.md`, especially §12.1
4. `docs/review/phase-3-visual-prototype-remediation-4-gemini-prompt.md`
5. `docs/review/phase-3-visual-prototype-handoff.md`
6. `design-prototype/css/tokens.css`
7. `design-prototype/css/styles.css`
8. every inline `<style>` block in `design-prototype/*.html`
9. reconciliation state logic in `design-prototype/reconciliation.html`
10. `design-prototype/tools/calc_contrast.py`
11. `design-prototype/tools/check_css_tokens.py`
12. `design-prototype/README.md`

You may edit only:

- `design-prototype/**`; and
- `docs/review/phase-3-visual-prototype-handoff.md`.

Do not reset, clean, revert, stage, commit, push, deploy, install packages or
modify Caddy. Preserve unrelated worktree changes.

## 3. Capture a complete remediation-5 baseline

Before any edit, produce a deterministic inventory that includes every file in
the authorized scope, including newly added tools:

```bash
find design-prototype -type f -print0 | sort -z | xargs -0 sha256sum > /tmp/freedom-blades-remediation-5-before.sha256
sha256sum docs/review/phase-3-visual-prototype-handoff.md >> /tmp/freedom-blades-remediation-5-before.sha256
```

If the environment’s `sort` lacks `-z`, use an equivalently safe deterministic
command and record it exactly. Do not edit before the baseline exists.

After editing, run the identical inventory into
`/tmp/freedom-blades-remediation-5-after.sha256` and compare them. The handoff’s
remediation-specific file list must come only from this comparison.

Explicitly state that the remediation-4 inventory showed only `tokens.css`
changing and excluded `design-prototype/tools/**`; therefore its nine-file
attribution was unsupported and is superseded.

## 4. Correct known CSS-state mismatches

For each state below, decide whether the implementation or the audit is the
intended source of truth. Prefer preserving the current interface and correcting
the audit unless an actual contrast failure requires a CSS adjustment.

Mechanically align these known mismatches:

1. `.nav-link:hover`
   - Actual CSS: `--fb-color-text-main` on
     `--fb-color-bg-surface-elevated`.
   - The prior audit incorrectly used `--fb-color-bg-surface-hover`.

2. `.btn-primary:hover`
   - Actual CSS: white text on `--fb-color-primary-dark`.
   - The prior audit incorrectly used `--fb-color-primary-hover`.
   - Either audit `primary-dark`, or deliberately update the CSS to
     `primary-hover` and verify that exact selector declaration.

3. `.btn-secondary:hover`
   - Actual CSS: `--fb-color-text-main` retained from `.btn-secondary`, on
     `--fb-color-bg-surface-hover`.
   - The prior audit used literal white on `#374151`.

4. `.btn-danger:hover`
   - Actual CSS retains `--fb-color-danger-text` and uses
     `rgba(153, 27, 27, 0.55)` over the underlying surface.
   - The prior audit used white on solid `--fb-color-danger-border`.

5. `.badge-primary`
   - Actual CSS uses `--fb-color-accent` over
     `rgba(37, 99, 235, 0.25)`.
   - The prior audit substituted info-alert colors.

6. `.data-table th`
   - Actual CSS uses `--fb-color-text-main` on
     `--fb-color-bg-surface-elevated`.
   - The prior audit used dim text on the ordinary surface.

Also recheck every other matrix row for the same class of mismatch. Do not assume
the unlisted rows are correct.

## 5. Mechanically verify selector mappings

`calc_contrast.py` must no longer rely on unverified comments or constants that
merely resemble CSS.

Implement a standard-library-only static CSS mapping verifier. A sound approach
is:

1. Parse `tokens.css` custom properties.
2. Parse the relevant simple selector blocks from `styles.css` and inline style
   blocks.
3. Extract the exact declarations used by each audited selector/state.
4. Resolve inherited/base declarations explicitly where a hover/selected state
   changes only background or border.
5. Resolve `var(--token)` references through the parsed token map.
6. Parse literal hex, `rgb()` and `rgba()` colors.
7. Fail on a missing selector, missing expected property, unresolved variable,
   unsupported color expression, or mismatch between the audited mapping and the
   stylesheet.

A narrowly scoped parser for the prototype’s known CSS syntax is acceptable. It
does not need to be a general browser CSS engine. Document its limitations.

If you prefer an explicit selector expectation table, every expected declaration
must still be compared mechanically with parsed CSS before calculating contrast.
For example, an entry for `.btn-danger:hover` must assert its background
declaration and resolve its inherited text color from `.btn-danger`. Changing the
stylesheet must cause the audit or tests to fail until the mapping is updated.

Do not claim browser-computed style verification. Call this a static
selector/token consistency audit.

## 6. Verify JavaScript-driven reconciliation states

The previous progress-state matrix did not match the JavaScript:

- the reset assigns `var(--fb-color-primary)`;
- queued, running and completed retain that reset color;
- stale assigns `var(--fb-color-warning-border)`; and
- failed assigns `var(--fb-color-danger-border)`.

The CSS default `.progress-bar-fill` color alone is not the final color after a
state button is activated.

Choose and implement one coherent approach:

- Preserve the current JavaScript behavior and audit the five actual assigned
  colors; or
- Intentionally give completed its success color and make any other desired
  state colors explicit in the state configuration, then audit those exact
  assignments.

Prefer replacing repeated conditional color assignments with a small explicit
state configuration object if it improves mechanical verification without
changing behavior. The audit must parse or import a repository-local
machine-readable state-color mapping that the UI logic also uses, or otherwise
mechanically verify the JavaScript assignments.

For every state, verify:

- fill color;
- track color;
- meaningful status/step border distinction where claimed;
- determinate versus indeterminate ARIA treatment; and
- the corresponding contrast threshold.

Changing a JavaScript state color must cause a test or audit failure if the audit
mapping is not updated.

## 7. Correct contrast-tool reporting

Keep the repaired hex parser, alpha compositing and primitive tests. Extend tests
to cover selector and state drift.

At minimum add tests proving that:

- `.nav-link:hover` resolves its actual foreground/background tokens;
- `.btn-primary:hover` resolves its actual hover background;
- `.btn-danger:hover` resolves inherited danger text and its 0.55-alpha surface;
- `.badge-primary` resolves its actual accent and 0.25-alpha background;
- `.data-table th` resolves main text on elevated surface;
- each of the five reconciliation states resolves the implemented fill color;
- a deliberately incorrect expected selector token is detected;
- a missing selector/property is detected; and
- an unresolved token causes a nonzero audit result.

The final tool must report:

- selector/state identifier;
- actual CSS/JS source location;
- foreground declaration and resolved color;
- raw background declaration;
- underlying surface and alpha where applicable;
- composed background;
- unrounded ratio and displayed two-decimal ratio;
- applicable threshold;
- pass, fail, exempt or informational status; and
- evaluated/pass/fail/exempt/informational totals.

Exit nonzero for any required contrast failure or mapping inconsistency. Do not
count exempt rows as passed.

## 8. Re-evaluate focus and disabled states accurately

Check two prior simplifications carefully:

- Focus outlines use `--fb-focus-ring`, whose color is nested through
  `var(--fb-color-accent)`. Verify that nested reference rather than substituting
  white for the primary-button case. Evaluate visibility against all immediately
  adjacent colors relevant to the outline.
- Disabled buttons use `opacity: 0.5`. If reporting an informational computed
  contrast, composite the entire disabled foreground and background against the
  underlying surface in the correct order. It remains exempt, but the calculation
  must not be fictional.

## 9. Documentation and claim correction

Update `design-prototype/README.md` and the existing handoff in place.

They must:

- mark the remediation-4 47-pass/1-exempt result as superseded because selector
  and state mappings were still inconsistent;
- replace the matrix with corrected selector/state-derived results;
- describe the tool as a static consistency and contrast audit, not a browser
  rendering audit;
- record its parser/inheritance limitations;
- include exact totals and every corrected failure/change;
- include exact commands and output summaries;
- retain all eight unperformed runtime-browser disclosures;
- correct the remediation-4 scope attribution using the actual remediation-5
  before/after comparison; and
- state that no acceptance or production behavior is implied.

Do not say “actual rendered CSS,” “browser verified,” “WCAG compliant,” or “fully
accessible.” Use “statically resolved from the prototype selectors/tokens” where
accurate.

## 10. Preserve resolved work

Do not regress:

- zero undefined token references;
- restored typography, focus, status and brand tokens;
- modal placement and prior inert-state restoration;
- five accessible reconciliation selectors and live-region updates;
- removal of unsupported backend claims;
- genuine local PNG portraits and fallbacks;
- non-clickable portraits;
- responsive layout corrections;
- synthetic identities and local-only assets;
- reduced-motion CSS; or
- truthful runtime-test limitations.

Do not add backend behavior or the deferred tools/languages/homebrew
administration editor.

## 11. Required verification

Run and record exact commands/results for:

- complete remediation-5 before/after inventories and `diff -u`;
- `python3 design-prototype/tools/check_css_tokens.py`;
- the full selector/state audit test suite;
- `python3 design-prototype/tools/calc_contrast.py`;
- `git diff --check`;
- `git status --short`;
- searches for external URLs, network/browser-storage/service-worker/form-action
  behavior;
- searches for real identities and plausible Discord snowflakes;
- searches for unsupported audit/security/lock/transaction/recovery claims;
- portrait format inspection; and
- HTML validation if already available, otherwise an explicit unavailable note.

## 12. Stop conditions

Stop and report instead of guessing if:

- a selector cannot be resolved safely by the scoped parser;
- inheritance or compositing is ambiguous;
- a genuine contrast failure requires material redesign;
- a change requires backend behavior;
- a required edit falls outside authorized scope; or
- existing maintainer/Codex work conflicts with the correction.

Do not stage, commit, push, deploy, modify Caddy or claim acceptance. Return the
result for Codex independent re-review and Peter’s visual review.
