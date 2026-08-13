# Freedom Blades Platform — Visual Design Prototype Documentation

This directory (`design-prototype/`) contains the static, inert frontend visual prototype for the Freedom Blades Platform, created under **Implementation Plan §12.1** and remediated under prompt `docs/review/phase-3-visual-prototype-remediation-6-gemini-prompt.md`.

## 1. How to Open & View Locally

Every page is pure local HTML/CSS/JS and can be opened directly in any modern web browser **without starting a web server, database, or external service**, and without network access:

1. Open `design-prototype/index.html` in your web browser:
   `file:///opt/discord-bots/freedom-bot/design-prototype/index.html`
2. Navigate between prototype screens using the sticky header navigation:
   - **Login**: `login.html`
   - **My Characters**: `my-characters.html`
   - **Character Detail**: `character-detail.html`
   - **Reconciliation**: `reconciliation.html`
   - **Council Queue**: `council-approval.html`
   - **Component Catalogue**: `components.html`

---

## 2. Evidence-Based Static Source Consistency Audit

All visual styles derive strictly from `css/tokens.css` and `css/styles.css`.

### Repository-Local Verification Tools

1. **Token Reference Contract Checker**:
   `python3 design-prototype/tools/check_css_tokens.py`
   Scans all CSS and HTML files for `var(--token)` usages and verifies zero undefined references.

2. **Evidence Integrity & Static Contrast Audit Tool**:
   `python3 design-prototype/tools/calc_contrast.py`
   Run unit test suite (`--test`) covering 11 negative, drift, and structural extraction self-tests.
   Statically resolves CSS selectors, inline HTML styles, and JS state objects to evaluate WCAG relative luminance contrast ratios:
   $$L = 0.2126 R' + 0.7152 G' + 0.0722 B'$$
   $$\text{Contrast Ratio} = \frac{L_1 + 0.05}{L_2 + 0.05}$$

### Evidence Classification Rules
- **extracted**: Foreground/background declarations parsed directly from CSS selectors, inline HTML styles, or JS state objects.
- **derived**: Documented inheritance or opacity compositing operations whose inputs are all extracted.
- **manual assumption**: Surface/layout boundary assumptions (e.g. adjacent focus outline placement over container surfaces).

### Complete 49-Pair Audited Matrix with Evidence Classifications

> [!NOTE]  
> **Superseded Audit Notice**: Remediation-5 audit estimates are superseded by this evidence-classified matrix.

| Category & Pair Name | Evidence | Source Location | Foreground | Composed BG | Ratio | Result |
|---|---|---|---|---|---|---|
| 1.1 Body Text on Base Bg | extracted | `tokens.css:--fb-color-text-main` | `#f8fafc` | `#0b0f19` | **18.30:1** | PASS AAA (> 7.0:1) |
| 1.2 Card Text on Surface | extracted | `tokens.css:--fb-color-bg-surface` | `#f8fafc` | `#111827` | **16.96:1** | PASS AAA (> 7.0:1) |
| 1.3 Elevated Text on Surface | extracted | `tokens.css:--fb-color-bg-surface-elevated` | `#f8fafc` | `#1f2937` | **14.03:1** | PASS AAA (> 7.0:1) |
| 1.4 Muted Subtext on Surface | extracted | `tokens.css:--fb-color-text-muted` | `#94a3b8` | `#111827` | **6.92:1** | PASS AA (> 4.5:1) |
| 1.5 Dim Metadata on Surface | extracted | `tokens.css:--fb-color-text-dim` | `#cbd5e1` | `#111827` | **11.95:1** | PASS AAA (> 7.0:1) |
| 2.1 Nav Link Normal | extracted | `styles.css:.nav-link` | `#94a3b8` | `#111827` | **6.92:1** | PASS AA (> 4.5:1) |
| 2.2 Nav Link Hover | extracted | `styles.css:.nav-link:hover` | `#f8fafc` | `#1f2937` | **14.03:1** | PASS AAA (> 7.0:1) |
| 2.3 Nav Link Active | extracted | `styles.css:.nav-link.active` | `#60a5fa` | `#1e293b` | **5.75:1** | PASS AA (> 4.5:1) |
| 3.1 Link Normal | extracted | `styles.css:a` | `#60a5fa` | `#111827` | **6.98:1** | PASS AA (> 4.5:1) |
| 3.2 Link Hover | extracted | `styles.css:a:hover` | `#93c5fd` | `#111827` | **9.84:1** | PASS AAA (> 7.0:1) |
| 3.3 Link Visited | extracted | `styles.css:a:visited` | `#60a5fa` | `#111827` | **6.98:1** | PASS AA (> 4.5:1) |
| 4.1 Primary Btn Normal | extracted | `styles.css:.btn-primary` | `#ffffff` | `#2563eb` | **5.17:1** | PASS AA (> 4.5:1) |
| 4.2 Primary Btn Hover | extracted | `styles.css:.btn-primary:hover` | `#ffffff` | `#1e40af` | **8.72:1** | PASS AAA (> 7.0:1) |
| 4.3 Primary Btn Disabled (Composed) | derived | `styles.css:.btn:disabled opacity 0.5` | `#566274` | `#18202f` | **2.64:1** | EXEMPT (Disabled) |
| 5.1 Secondary Btn Normal | extracted | `styles.css:.btn-secondary` | `#f8fafc` | `#1f2937` | **14.03:1** | PASS AAA (> 7.0:1) |
| 5.2 Secondary Btn Hover | extracted | `styles.css:.btn-secondary:hover` | `#f8fafc` | `#1e293b` | **13.98:1** | PASS AAA (> 7.0:1) |
| 5.3 Secondary Btn Selected (`aria-pressed`) | extracted | `styles.css:.btn-secondary[aria-pressed="true"]` | `#60a5fa` | `#1e293b` | **5.75:1** | PASS AA (> 4.5:1) |
| 5.4 Secondary Btn Selected Border vs Surface | derived | `styles.css:.btn-secondary[aria-pressed="true"] border` | `#2563eb` | `#111827` | **3.43:1** | PASS UI Non-Text (> 3.0:1) |
| 6.1 Danger Btn Normal | derived | `styles.css:.btn-danger (0.35 alpha over surface)` | `#fca5a5` | `#411923` | **7.97:1** | PASS AAA (> 7.0:1) |
| 6.2 Danger Btn Hover | derived | `styles.css:.btn-danger:hover (0.55 alpha over surface)` | `#fca5a5` | `#5c1a20` | **6.81:1** | PASS AA (> 4.5:1) |
| 7.1 Discord Btn Normal | extracted | `login.html:.discord-btn` | `#ffffff` | `#5865F2` | **4.61:1** | PASS AA (> 4.5:1) |
| 7.2 Discord Btn Hover | extracted | `login.html:.discord-btn:hover` | `#ffffff` | `#4752C4` | **6.42:1** | PASS AA (> 4.5:1) |
| 8.1 Primary Badge Text | derived | `styles.css:.badge-primary (0.25 alpha over surface)` | `#60a5fa` | `#162b58` | **5.43:1** | PASS AA (> 4.5:1) |
| 8.2 Success Badge Text | derived | `styles.css:.badge-success (0.35 alpha over surface)` | `#4ade80` | `#13332c` | **7.84:1** | PASS AAA (> 7.0:1) |
| 8.3 Warning Badge Text | derived | `styles.css:.badge-warning (0.35 alpha over surface)` | `#fdba74` | `#412220` | **8.45:1** | PASS AAA (> 7.0:1) |
| 8.4 Danger Badge Text | derived | `styles.css:.badge-danger (0.35 alpha over surface)` | `#fca5a5` | `#411923` | **7.97:1** | PASS AAA (> 7.0:1) |
| 8.5 Deferred Badge Text | extracted | `styles.css:.badge-deferred` | `#f1f5f9` | `#334155` | **9.45:1** | PASS AAA (> 7.0:1) |
| 8.6 Info Alert Text | derived | `styles.css:.alert-info (0.35 alpha over surface)` | `#93c5fd` | `#16244a` | **8.41:1** | PASS AAA (> 7.0:1) |
| 9.1 Form Label | extracted | `styles.css:label` | `#cbd5e1` | `#111827` | **11.95:1** | PASS AAA (> 7.0:1) |
| 9.2 Form Input Text | extracted | `styles.css:input` | `#f8fafc` | `#1f2937` | **14.03:1** | PASS AAA (> 7.0:1) |
| 9.3 Form Select Option Text | extracted | `styles.css:select` | `#f8fafc` | `#1f2937` | **14.03:1** | PASS AAA (> 7.0:1) |
| 9.4 Validation Error Text | extracted | `styles.css:.alert-danger` | `#fca5a5` | `#111827` | **9.35:1** | PASS AAA (> 7.0:1) |
| 9.5 Form Help Text | extracted | `styles.css:.form-help` | `#94a3b8` | `#111827` | **6.92:1** | PASS AA (> 4.5:1) |
| 10.1 Table Header Text | extracted | `styles.css:.data-table th` | `#f8fafc` | `#1f2937` | **14.03:1** | PASS AAA (> 7.0:1) |
| 10.2 Table Cell Text | extracted | `styles.css:.data-table td` | `#f8fafc` | `#111827` | **16.96:1** | PASS AAA (> 7.0:1) |
| 10.3 Responsive Data Label | extracted | `styles.css:.data-table-responsive td::before` | `#94a3b8` | `#111827` | **6.92:1** | PASS AA (> 4.5:1) |
| 11.1 Focus Ring on Base Bg | manual assumption | `styles.css:focus-visible over base bg` | `#60a5fa` | `#0b0f19` | **7.53:1** | PASS UI Non-Text (> 3.0:1) |
| 11.2 Focus Ring on Surface | manual assumption | `styles.css:focus-visible over surface bg` | `#60a5fa` | `#111827` | **6.98:1** | PASS UI Non-Text (> 3.0:1) |
| 11.3 Focus Ring on Elevated Surface | manual assumption | `styles.css:focus-visible over elevated surface` | `#60a5fa` | `#1f2937` | **5.77:1** | PASS UI Non-Text (> 3.0:1) |
| 11.4 Focus Ring on Primary Button (Offset Surface) | manual assumption | `styles.css:focus-visible 2px offset over container surface` | `#60a5fa` | `#111827` | **6.98:1** | PASS UI Non-Text (> 3.0:1) |
| 12.1 Form Border vs Surface | manual assumption | `styles.css:input border vs surface` | `#64748b` | `#111827` | **3.73:1** | PASS UI Non-Text (> 3.0:1) |
| 12.2 Button Border vs Surface | manual assumption | `styles.css:.btn-secondary border vs surface` | `#64748b` | `#111827` | **3.73:1** | PASS UI Non-Text (> 3.0:1) |
| 12.3 Progress Bar Track Border/Fill | manual assumption | `styles.css:.progress-bar-fill vs track` | `#3b82f6` | `#1f2937` | **3.99:1** | PASS UI Non-Text (> 3.0:1) |
| 13.1 Queued Progress Fill | extracted | `reconciliation.html:RECONCILIATION_STATES.queued` | `#3b82f6` | `#1f2937` | **3.99:1** | PASS UI Non-Text (> 3.0:1) |
| 13.2 Running Progress Fill | extracted | `reconciliation.html:RECONCILIATION_STATES.running` | `#3b82f6` | `#1f2937` | **3.99:1** | PASS UI Non-Text (> 3.0:1) |
| 13.3 Completed Progress Fill | extracted | `reconciliation.html:RECONCILIATION_STATES.completed` | `#16a34a` | `#1f2937` | **4.45:1** | PASS UI Non-Text (> 3.0:1) |
| 13.4 Stale Progress Fill | extracted | `reconciliation.html:RECONCILIATION_STATES.stale` | `#ea580c` | `#1f2937` | **4.12:1** | PASS UI Non-Text (> 3.0:1) |
| 13.5 Failed Progress Fill | extracted | `reconciliation.html:RECONCILIATION_STATES.failed` | `#dc2626` | `#1f2937` | **3.04:1** | PASS UI Non-Text (> 3.0:1) |
| 14.1 Inline GP Gold (`#f59e0b`) on Surface | extracted | `character-detail.html:L181 inline style` | `#f59e0b` | `#111827` | **8.26:1** | PASS AAA (> 7.0:1) |

---

## 3. Character Portrait Provenance & HTML/CSS Fallback System

- **Genuine PNG Portraits**:
  - `assets/portraits/thorin.png` (Dwarf Paladin - genuine PNG image data)
  - `assets/portraits/valerius.png` (Elf Fighter - genuine PNG image data)
  - `assets/portraits/lyra.png` (Human Rogue - genuine PNG image data)
- **Provenance**: Created using synthetic AI art generation tool. Format verified via `file` utility.
- **Rendering**: Scaled with `object-fit: cover` to avoid layout shift.
- **HTML/CSS Initials Fallback**: A styled HTML/CSS initials fallback `div` (`.avatar-portrait-fallback`) renders via `onerror` if an image fails to load. Images carry no `onclick` handlers and do not acquire button semantics.

---

## 4. Modal Architecture & Accessibility Features

### Modal Dialog Architecture (B-2 & N-3)
- `#demo-dialog` lives OUTSIDE `<div id="app-shell">`.
- When opened, `openDialog()` records prior background inert state (`priorAppShellInert`) and applies native `inert` to `#app-shell`, rendering background UI non-interactive without placing `aria-hidden` on an ancestor of the dialog.
- On close, `closeDialog()` restores the exact prior inert state of `#app-shell` and returns focus to `#open-dialog-button`.
- Focus traps forward (`Tab`) and reverse (`Shift+Tab`) navigation within dialog controls, and `Escape` dismisses the dialog.

### 5 Reconciliation Job States (I-10 & I-15)
`reconciliation.html` exposes five discrete presentation job states via `aria-pressed="true/false"` selectors using an explicit `RECONCILIATION_STATES` JS configuration object:
1. **Queued**: `#3b82f6` fill, `aria-valuenow="10"`, progressbar width 10%, text "Job is waiting in queue."
2. **Running**: `#3b82f6` fill, `aria-valuenow="50"`, progressbar width 50%, text "Processing snapshot records (50%)."
3. **Completed**: `#16a34a` fill, `aria-valuenow="100"`, progressbar width 100%, text "All 32 snapshot actors reconciled."
4. **Stale**: `#ea580c` fill, indeterminate warning state, text "Snapshot checksum differs from database state."
5. **Failed**: `#dc2626` fill, indeterminate error state, status message *"Synthetic schema-validation failure state. Production recovery behavior is pending the accepted backend contract."*

---

## 5. Assumptions for Backend Route & View-Model Contracts

Before production Phase 3 integration begins, backend owner (Claude) must settle:
1. Session cookie attributes (`SameSite=Lax`, `Secure`, `HttpOnly`).
2. Structure of `character_access` authorization view-models (linked character list vs Council scope).
3. Async reconciliation polling mechanism for HTMX (`hx-get="/reconciliation/status"`).
4. Representation of integer copper currency in Jinja filter context (`formatted_gp` vs raw `balance_copper`).
