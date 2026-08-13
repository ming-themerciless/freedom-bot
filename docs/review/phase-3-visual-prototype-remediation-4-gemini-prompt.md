# Gemini handoff — Phase 3 token and contrast audit correction

Copy everything below this line into Gemini as one prompt.

---

You are the frontend implementer performing a fourth, strictly corrective
remediation of the Freedom Blades Phase 3 static visual prototype.

Repository: `/opt/discord-bots/freedom-bot`

Current date: 2026-08-12

Maintainer and Acceptance Authority: Peter Duscha

Frontend implementer: Gemini

Backend implementer: Claude

Independent reviewer: Codex

Public review URL: `https://freedom-blades.rpgworld.org`

## 1. Required outcome

Repair the design-token regression introduced by the third remediation, correct
the contrast calculator, make every audit pair correspond to actual CSS, and
rewrite the handoff so it reports only reproducible evidence.

This is a correction, not a redesign. Preserve the accepted visual direction,
portraits, responsive layouts, modal structure, five reconciliation states and
static Phase 3 boundary.

Completion is not acceptance. Codex will re-review the result and Peter decides
the visual gate.

## 2. Mandatory preparation

Read completely before editing:

1. `AGENTS.md`
2. `.agents/AGENTS.md`
3. `docs/implementation-plan.md`, especially §12.1 and Phase 3
4. `docs/review/phase-3-visual-prototype-remediation-2-gemini-prompt.md`
5. `docs/review/phase-3-visual-prototype-remediation-3-gemini-prompt.md`
6. `docs/review/phase-3-visual-prototype-handoff.md`
7. `design-prototype/css/tokens.css`
8. `design-prototype/css/styles.css`
9. `design-prototype/tools/calc_contrast.py`
10. every prototype HTML file and `design-prototype/README.md`

Capture a before-edit inventory for every authorized file, including SHA-256
hashes, in `/tmp/freedom-blades-remediation-4-before.sha256`. This evidence is
outside the repository and must not be committed. Record the exact command in
the handoff.

The worktree contains untracked prototype files and unrelated pre-existing
changes. Do not reset, clean, revert, stage, commit or modify unrelated work.

## 3. Authorized scope

You may edit only:

- `design-prototype/**`; and
- `docs/review/phase-3-visual-prototype-handoff.md`.

Do not edit prompts, plans, decisions, project status, ADRs, production code or
Caddy configuration. Do not install packages or download external assets.

## 4. Blocking finding — restore a coherent token contract

The third remediation replaced `tokens.css` without updating all consumers.
Thirteen variables used by `styles.css` or the HTML are now undefined:

- `--fb-font-family`
- `--fb-focus-ring`
- `--fb-focus-offset`
- `--fb-color-border-brand`
- `--fb-color-primary-dark`
- `--fb-color-bg-surface-hover`
- `--fb-color-danger-bg`
- `--fb-color-success-bg`
- `--fb-color-warning-bg`
- `--fb-color-info-bg`
- `--fb-color-info-border`
- `--fb-color-info-text`
- `--fb-color-deferred-border`

Repair the token contract before changing audit documentation.

Preferred approach:

1. Restore definitions for every token that remains meaningfully consumed.
2. Where a replacement token already exists, update all consumers consistently
   and remove the obsolete name only after proving it has zero consumers.
3. Preserve the intended system-font stack, visible focus ring and offset,
   primary/secondary hover treatments, brand borders, and every status
   background/text/border triplet.
4. Preserve reduced-motion tokens and rules.
5. Do not paper over missing variables with fallback values scattered throughout
   HTML or CSS.

Add a repository-local, read-only token-reference check such as
`design-prototype/tools/check_css_tokens.py`. It must:

- scan `design-prototype/css/*.css` and `design-prototype/*.html`;
- collect every `var(--token)` reference;
- collect every custom-property definition;
- print all undefined references with source locations;
- return a nonzero exit status when any referenced token is undefined; and
- require only the Python standard library.

The required result is zero undefined referenced tokens. Unused definitions may
be reported but must not fail the check automatically.

## 5. Important finding — correct alpha compositing

`calc_contrast.py` currently parses background channels incorrectly:

```python
bg = [int(bg_hex.lstrip('#')[i:i+2], 16) for i in range(3)]
```

Offsets `0, 1, 2` overlap. Parse both foreground and background channels at
offsets `0, 2, 4`. Refactor through one validated hex parser so the bug cannot be
duplicated.

The parser must:

- accept exactly six-digit hexadecimal colors with an optional leading `#`;
- reject malformed values with a clear error;
- return the three correct RGB channels; and
- be used by luminance and alpha-compositing code.

Add deterministic self-tests using standard-library `unittest` or assertions.
At minimum test:

- `#111827` parses as `(17, 24, 39)`;
- opaque alpha returns the foreground color;
- zero alpha returns the background color;
- a known 0.35-alpha composition returns the independently expected result; and
- symmetry/basic known contrast cases such as identical colors producing
  `1.0:1` and black/white producing approximately `21.0:1`.

The test command must return nonzero on failure and be recorded in the handoff.

## 6. Important finding — audit actual CSS states

The current script hard-codes several pairs that do not match the rendered CSS.
Correct each mismatch, including:

- active navigation actually uses `--fb-color-accent` on
  `--fb-color-bg-subtle`;
- selected secondary buttons actually use the accent text, subtle background and
  primary border defined in `.btn-secondary[aria-pressed="true"]`;
- danger hover retains whatever text color the CSS actually specifies over its
  actual translucent hover background unless you deliberately change the CSS;
- primary hover must use the restored/selected hover token;
- focus-ring tests must use the restored focus-ring color and actual adjacent
  surfaces;
- badges and alerts must use their actual restored status tokens; and
- disabled-state reporting must account for CSS opacity compositing against the
  real underlying surface rather than pretending it directly uses different
  foreground/background tokens.

Use one of these robust approaches:

1. Preferred: define the audited palette/state data in a small repository-local
   machine-readable source consumed by both the audit tool and checked against
   CSS token definitions; or
2. Parse the simple `:root` token definitions directly from `tokens.css`, resolve
   token references, and describe selector/state mappings in the audit tool.

Whichever approach you choose, the tool must detect token drift. It must fail if
an audited token is absent or its expected CSS value differs from the value used
for calculation.

Do not claim that the script proves browser-computed styles. It is a static
token/selector audit. State that limitation explicitly.

## 7. Contrast tool behavior

Upgrade `design-prototype/tools/calc_contrast.py` so it:

- uses corrected parsing and compositing;
- reads or verifies real token values;
- records actual foreground, raw background, underlying surface, alpha and
  composed background when translucency is involved;
- applies the correct threshold for normal text, large text and non-text UI;
- treats disabled controls accurately as exempt from contrast requirements while
  still reporting their computed informational ratio;
- prints unrounded ratios with enough precision and a documented display-rounding
  rule;
- counts evaluated, passed, failed, exempt and informational cases;
- lists every failure clearly;
- exits nonzero if any required pair fails or an audited token/state mapping is
  inconsistent; and
- never labels non-text contrast as A/AA/AAA.

Re-evaluate the complete matrix required by remediation 3. Do not delete
categories simply to obtain a passing result. If a real pair fails, adjust the
actual token/CSS and rerun the audit.

Pay particular attention to:

- nav active text/background and border/background;
- selected state button text/background and border/adjacent background;
- hover states;
- translucent danger/success/warning/info surfaces;
- disabled opacity composition;
- focus indicators;
- form and table boundaries;
- progress track/fills for all five states; and
- inline literal colors.

## 8. Important finding — withdraw false prior claims

The previous “47/47 pass” claim is invalid because the calculator had a parsing
bug, audited fictional pairs and did not detect missing CSS variables.

In `design-prototype/README.md` and the handoff:

- explicitly state that the previous result was superseded after the defects
  were found;
- replace all prior ratios with corrected output;
- do not retain an old ratio merely because it was close;
- describe the audit as static token/selector verification, not rendered-browser
  verification;
- report the exact evaluated/pass/fail/exempt/informational totals produced by
  the corrected tool; and
- retain the existing disclosure that graphical browser, accessibility-tree,
  keyboard, viewport, zoom, reduced-motion, fallback and automated-accessibility
  runtime checks were not performed.

Do not claim “WCAG compliant,” “fully accessible,” or “all rendered states
verified.”

## 9. Normal finding — reproducible scope evidence

The previous handoff asserted that baseline checksums existed but did not provide
them or a retrievable artifact.

Use the before inventory captured in `/tmp` and generate
`/tmp/freedom-blades-remediation-4-after.sha256` using the same deterministic
command. Compare them and record:

- the exact baseline and after commands;
- the exact `/tmp` paths;
- the comparison command;
- the remediation-specific changed-file list derived from that comparison;
- pre-existing Git modifications separately; and
- the limitation that `/tmp` artifacts are session-local and not durable project
  records.

Do not claim that `git status` alone proves attribution. Do not copy checksum
inventories containing unrelated or sensitive files into the repository.

## 10. Preserve resolved work

Do not regress:

- modal placement outside `#app-shell`;
- prior inert-state restoration;
- modal focus-management source logic;
- removal of unsupported audit, lock and reconnect claims;
- five reconciliation states, selected-state semantics and live status updates;
- genuine local PNG portraits and HTML/CSS fallbacks;
- non-clickable portrait behavior;
- synthetic identities;
- narrow card grid, responsive stack and long-value wrapping;
- local-only assets;
- visual identity and overall layout; or
- truthful runtime-verification disclosures.

Do not add the deferred administrator editor for tools, languages, homebrew items
or other vocabularies. Do not add backend behavior.

## 11. Required verification commands

Run and record exact commands and results for:

- before/after SHA-256 inventories and comparison;
- `python3 design-prototype/tools/check_css_tokens.py`;
- contrast-tool self-tests;
- `python3 design-prototype/tools/calc_contrast.py`;
- `git diff --check`;
- `git status --short`;
- searches for external URLs, network APIs, browser storage, service workers and
  form actions;
- searches for real identities and plausible Discord snowflakes;
- searches for unsupported security, audit, lock, transaction and recovery
  claims;
- portrait file-format inspection; and
- HTML validation if a validator is already installed, otherwise record that it
  was unavailable.

Also run a direct undefined-variable check independent of the new helper where
practical. Never report a pass without including the command’s actual summary.

## 12. Handoff update

Update `docs/review/phase-3-visual-prototype-handoff.md` in place. Do not create a
competing handoff.

It must include:

- the blocking token-contract finding and exact disposition;
- the alpha-parser, CSS-state mapping, false-audit-claim and scope-evidence
  findings with exact dispositions;
- the full final defined/undefined token check summary;
- corrected contrast methodology, state mappings and totals;
- any actual CSS color changes made to resolve failures;
- exact test commands and outputs;
- the remediation-specific file list derived from the recorded baseline;
- the continuing runtime-test limitations;
- remaining backend-contract questions without speculative answers; and
- explicit no-approval/no-production-impact language.

## 13. Stop conditions

Stop and report instead of guessing if:

- token restoration materially changes the approved visual direction;
- a contrast pair cannot be mapped to actual CSS with confidence;
- a required pair fails and fixing it requires a significant redesign;
- a change would require backend behavior;
- an edit is required outside authorized scope; or
- existing maintainer or Codex changes conflict with the correction.

Do not commit, stage, push, deploy, modify Caddy or claim acceptance. Return the
result for Codex independent re-review and Peter’s visual review.
