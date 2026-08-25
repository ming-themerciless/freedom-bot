# Freedom Blades Platform — Visual Design Prototype Documentation

This directory (`design-prototype/`) contains the static, inert frontend visual prototype for the Freedom Blades Platform, created under **Implementation Plan §12.1** and visually frozen in **Step 5**.

---

## 1. Prototype Overview & Seven Pages

The visual prototype consists of seven static HTML pages using pure local HTML5, CSS3, and JavaScript without external runtime dependencies or remote assets:

1. **`index.html` — Design Prototype Hub (Overview)**: Static prototype directory with the Phase 3 scope notice and cards linking to the six demonstrated screens.
2. **`my-characters.html` — My Characters**: Roster card view showcasing prominent portrait media, character facts, status badges, interactive state demonstrator bar, and explicit modal portrait preview triggers.
3. **`character-detail.html` — Character Detail**: Profile hero section for *Thorin Stonehelm* with portrait, attributes grid, inventory summary, gold balance, sync freshness block, and modal portrait preview.
4. **`reconciliation.html` — Snapshot Import & Reconciliation**: Asynchronous batch job status card with responsive 1-column mobile step stacking (`.progress-step-row`), progress bar, live status alerts, candidate mapping table, and diff state demonstrator controls.
5. **`council-approval.html` — Council Approval Queue & Diff**: Procedural operational ledger displaying pending character import proposals, responsive Before/After attribute diff boxes (`.diff-container`), and decision action controls.
6. **`components.html` — Component Catalogue**: Living design system showcase displaying color tokens, typography, button variants, badges, alerts, form controls, blade section dividers (`.fb-blade-divider`), and data table patterns.
7. **`login.html` — Sign In**: Distinct account entry page with brand hero section, Discord sign-in action button, privacy disclosures list, and inert login state explanation.

---

## 2. Local Assets & Visual Identity

- **Guild Emblem**: `assets/freedom-blades-token.png` (Maintainer official seal token).
- **Synthetic Character Portraits**:
  - `assets/portraits/lyra.png` — *Lyra Shadowwhisper* (Human Rogue 4, Thief)
  - `assets/portraits/thorin.png` — *Thorin Stonehelm* (Dwarf Paladin 7, Oath of Devotion)
  - `assets/portraits/valerius.png` — *Valerius Dawnblade* (Elf Fighter 5, Champion)
- **Visual Direction**: Forged-steel metallic aesthetic (`#0b0f19` base, `#111827` surface, `#1f2937` elevated surface, `#3b82f6` / `#60a5fa` steel-blue accents) with blade section dividers and restrained liveliness hover/focus emphasis.

---

## 3. Serving the Prototype Locally

To serve the prototype locally using a simple Python HTTP server:

```bash
# From the repository root (/opt/freedom-blades/platform):
python3 -m http.server 8080 --directory design-prototype
```

Then open `http://localhost:8080/index.html` in your web browser.

Alternatively, pages may be opened directly via `file://` URLs for basic layout viewing.

---

## 4. Visual Freeze Manifest (`v=6`)

All 14 implementation and asset files are frozen under the visual freeze manifest at `docs/review/phase-3-visual-freeze-manifest.sha256`. All HTML pages load `css/tokens.css?v=6` and `css/styles.css?v=6`, and `styles.css` imports `@import url('tokens.css?v=6');`.

### Freeze Manifest Verification Command
```bash
sha256sum --check docs/review/phase-3-visual-freeze-manifest.sha256
```

---

## 5. Verification Commands

Run the following repository-local verification commands:

```bash
# 1. Whitespace & diff cleanliness
git diff --check

# 2. Native dialog modal JS syntax check
node --check design-prototype/js/portrait-preview.js

# 3. CSS Token Contract Validator (verifies zero undefined CSS tokens)
python3 design-prototype/tools/check_css_tokens.py

# 4. Contrast tool self-tests and complete static contrast matrix
python3 design-prototype/tools/calc_contrast.py --test
python3 design-prototype/tools/calc_contrast.py

# 5. Visual Freeze Manifest Integrity Check
sha256sum --check docs/review/phase-3-visual-freeze-manifest.sha256
```

---

## 6. Static Boundary & Limitations

- **Static Prototype Scope**: Pure static HTML/CSS/JS frontend prototype. No live backend API calls, no Discord OAuth2 authentication, no database persistence, and no production infrastructure integration.
- **Evidence Limitations**: Visual appearance and mobile reflow were visually accepted by maintainer Peter Duscha across desktop and real mobile hardware. Formal screen reader audio traversal (VoiceOver/NVDA) and repeatable automated headless browser test matrices were not executed.
- **Contrast Evidence**: On 2026-08-13, the repository-local contrast tool's 11 self-tests passed and its frozen-source matrix reported 49 evaluated pairs, 48 passes, one disabled-state exemption, and zero failures. This is static source evidence, not a substitute for assistive-technology or browser testing.
