# Phase 3 Visual Design Prototype — Contrast & Evidence Tooling Remediation Prompt for Claude

> **Superseded without execution — 2026-08-13.** During project reconciliation,
> Codex ran the current tracked tooling against the frozen `v=6` source. All 11
> contrast-tool self-tests passed; the 49-pair matrix reported 48 passes, one
> valid disabled-state exemption and zero failures; the token checker reported
> zero undefined references; and all 14 freeze-manifest entries verified. Peter
> Duscha accepted Step 5. This prompt is retained as planning history and must
> not be used as either a tooling task or a production backend handoff.

**Target Repository**: `/opt/discord-bots/freedom-bot`
**Assigned Implementer**: Claude (Backend & Tooling Implementer)
**Prerequisite State**: Visual Steps 1–4 accepted by maintainer Peter Duscha; visual prototype frozen at `v=6` under `docs/review/phase-3-visual-freeze-manifest.sha256`.
**Objective**: Remediate repository-local contrast and evidence audit tools (`calc_contrast.py` and `check_css_tokens.py`) to accurately audit the frozen `v=6` visual prototype source without altering the accepted visual design or interface layout.

---

## 1. Context & Authority Breakdown

Steps 1–4 of the Phase 3 visual prototype for the Freedom Blades Platform have been visually accepted by maintainer Peter Duscha and verified by independent Codex source reviews. Maintainer Peter Duscha confirmed on a real mobile device that the final responsive Reconciliation progress-step correction works.

The visual implementation is frozen. The SHA-256 visual freeze manifest is located at:
`docs/review/phase-3-visual-freeze-manifest.sha256`

### Roles & Responsibilities
- **Peter Duscha**: Visual Acceptance Authority (visually accepted Steps 1–4).
- **Codex**: Independent AI Source Reviewer (performs independent source code review, contract evaluation, accessibility auditing, and git diff judgment).
- **Gemini**: Frontend Visual Implementer (completed visual prototype design, responsive reflow, Step 1–4 visual corrections, visual freeze manifest, and this prompt).
- **Claude (You)**: Backend & Tooling Implementer (assigned to remediate contrast and evidence audit scripts without altering frozen UI code).

> [!IMPORTANT]
> Historical instruction only: had this task run, Claude would have been the
> tooling implementer rather than the visual designer. The superseding notice at
> the head of this file controls; no work remains authorized by this prompt.

---

## 2. Authorized Scope & Edit Boundaries

### Authorized Default Edit Scope
You are authorized to edit ONLY the following files:
1. `design-prototype/tools/calc_contrast.py`
2. `design-prototype/tools/check_css_tokens.py` (only if a genuine checker defect requires it)
3. Tests or fixtures belonging directly to those audit tools under `design-prototype/tools/` or `tests/`
4. `design-prototype/README.md` (audit command/result sections ONLY)
5. `docs/review/phase-3-visual-prototype-handoff.md` (final audit evidence sections ONLY)
6. A new focused remediation report or walkthrough under `docs/review/` (e.g. `docs/review/phase-3-contrast-tooling-remediation-report.md`)

### Strictly Forbidden Edits
You MUST NOT edit any frozen prototype implementation or visual asset file:
- `design-prototype/index.html`
- `design-prototype/login.html`
- `design-prototype/my-characters.html`
- `design-prototype/character-detail.html`
- `design-prototype/reconciliation.html`
- `design-prototype/council-approval.html`
- `design-prototype/components.html`
- `design-prototype/css/tokens.css`
- `design-prototype/css/styles.css`
- `design-prototype/js/portrait-preview.js`
- `design-prototype/assets/*`
- `docs/review/phase-3-visual-freeze-manifest.sha256`

### Protocol for Genuine Visual Contrast Failures
If you discover a genuine contrast failure in the frozen visual source that cannot be resolved through an audit tool mapping correction:
1. **DO NOT** silently edit frozen HTML, CSS, or JS files.
2. **STOP** and report the failure with full details:
   - Exact CSS selector and element state
   - Foreground and background color hex values
   - Alpha compositing formula and layer stack
   - Calculated relative luminance contrast ratio
   - Applicable WCAG 2.2 criterion and threshold (e.g. 4.5:1 AA, 7.0:1 AAA, 3.0:1 UI Non-text)
   - Smallest proposed visual color adjustment
   - Affected SHA-256 freeze manifest hashes
3. Wait for maintainer authorization and Codex review before regenerating the freeze manifest.

---

## 3. Tooling Remediation Requirements

Inspect the existing `design-prototype/tools/calc_contrast.py` and `design-prototype/tools/check_css_tokens.py` scripts rather than trusting prior claims. Remediate `calc_contrast.py` to ensure it satisfies all of the following criteria:

### A. Token Resolution & Mapping
- Parse token definitions directly from the frozen repository file `design-prototype/css/tokens.css`.
  - *Note*: `v=6` is only the accepted browser asset-reference query parameter used in HTML link tags and CSS imports (`tokens.css?v=6`). Audit tooling MUST read the local filesystem file `design-prototype/css/tokens.css` directly without a query parameter suffix on filesystem calls.
  - Audit tooling should separately confirm that frozen HTML files and `styles.css` specify `?v=6` in their asset URL references.
- Safely resolve token references, including nested or composite custom properties (`var(--token)`).
- Detect and fail on undefined or cyclic token references.
- Map audited color pairs to real CSS selectors in `design-prototype/css/styles.css`, inline styles in HTML files, or JS state definitions in `reconciliation.html`.

### B. Element & State Coverage
Audit all interactive and presentation states across the prototype:
- Normal body text, card text, muted subtext, and dim metadata.
- Navigation links (normal, hover, active, focus).
- Buttons (primary, secondary, danger, discord, selected `aria-pressed`, disabled).
- Badges & Alerts (primary, success, warning, danger, deferred, info).
- Form controls (labels, input text, select options, help text, validation error alerts).
- Operational data tables (headers, body cells, responsive data labels).
- Focus rings on base background, surface, and elevated surface.
- Form and button borders vs. surfaces (UI Non-Text 3.0:1 threshold).
- Reconciliation job states (queued, running, completed, stale, failed progress fills and text alerts).
- Special inline elements (e.g., GP gold inline style `#f59e0b`).

### C. Mathematical Precision & Compositing
- Use standard WCAG 2.2 relative luminance formula:
  $$L = 0.2126 R' + 0.7152 G' + 0.0722 B'$$
  $$\text{Contrast Ratio} = \frac{L_1 + 0.05}{L_2 + 0.05}$$
- Correctly alpha-composite translucent layers (`rgba(...)` or CSS opacity) over underlying dark surface backgrounds (`#0b0f19`, `#111827`, `#1f2937`).
- Correctly distinguish text contrast thresholds (4.5:1 AA / 7.0:1 AAA) from non-text UI component thresholds (3.0:1 AA).
- Handle exempt states (such as disabled buttons) cleanly without false failures.

### D. Evidence Classification & Source Citations
- Classify every audited pair into one of three explicit evidence classes:
  - `extracted`: Declarations parsed directly from CSS selectors, inline HTML styles, or JS state objects.
  - `derived`: Documented compositing operations whose input colors are all extracted.
  - `manual assumption`: Layout boundary assumptions (e.g. adjacent focus outline placement over container surfaces).
- Include exact repository source file and line/selector citations for every pair.

### E. Test Suite & Robustness
- Include an automated test mode (`python3 design-prototype/tools/calc_contrast.py --test`) with negative drift tests, malformed syntax tests, cyclic token tests, and extraction tests.
- Fail closed (return non-zero exit code) on any unresolved token mapping, contrast threshold failure, or tool self-test failure.
- Ensure output is 100% deterministic and reproducible across environments.

---

## 4. Required Verification Protocol for Claude

Before completing your handoff, execute and report the exact results of the following verification commands:

```bash
# 1. CSS Token Reference Validator
python3 design-prototype/tools/check_css_tokens.py

# 2. Contrast Tool Self-Test Suite
python3 design-prototype/tools/calc_contrast.py --test

# 3. Complete Contrast Matrix Calculation
python3 design-prototype/tools/calc_contrast.py

# 4. Visual Freeze Manifest Integrity Verification
sha256sum --check docs/review/phase-3-visual-freeze-manifest.sha256

# 5. Git Diff Cleanliness Check
git diff --check
```

### Additional Verification Steps
- Run Python syntax compile checks on all modified Python scripts (`python3 -m py_compile design-prototype/tools/calc_contrast.py`).
- Confirm using `sha256sum --check` that every frozen file in `docs/review/phase-3-visual-freeze-manifest.sha256` remains byte-for-byte identical.
- Provide a clear diff-scope inventory proving only authorized files were edited.
- Disclose any manual assumptions or remaining untested behavior honestly.
- Do NOT claim Phase 3 acceptance.

---

## 5. Deferred Scope Reminder

The following remain explicitly deferred:
- Production FastAPI routes, Jinja templates, and database schemas.
- Discord OAuth2 authentication and live session state.
- Database persistence for character records, reconciliation jobs, or council approvals.
- Foundry VTT image proxying or API contracts.
- Deferred administrator editor for controlled vocabularies.
- Final Phase 3 acceptance and phase transition.
