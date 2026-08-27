# P3.5 accessibility and browser evidence

**Artifact 4 of `phase-3-p3-5-readiness-and-execution-plan.md` §12.1**, created by
**EX-7**. **Opened:** 2026-08-26 by Claude, P3.5 working Technical Lead.

**Repository:** `/opt/freedom-blades/platform` · **Branch:** `docs/platform-plan`

> **The rule this document is written under.** An automated pass, a source review
> or a static contrast calculation is **never** promoted to satisfy a row whose
> accepted evidence level is a browser, a device or an assistive technology
> (execution plan §10.5). Where the level was not met, the row says so.

**This document closes nothing. R-23 remains Active.**

---

## 1. The row numbering, reconciled first (finding F-1)

The P3.4 submission's accessibility matrix **renumbered** the TC-UI rows relative
to the accepted `docs/contracts/phase-3-test-traceability.md` §16. It is
reconciled here before any result is recorded, because a package that cited a
passing test against the wrong accepted row would be misreporting even when every
test passes.

**The code was never wrong.** The tests are named for the *contract's* numbering —
`test_tc_ui_04_prefers_reduced_motion_media_query` and
`test_tc_ui_07_wcag_contrast_matrix` sit exactly where §16 puts those subjects. It
is the submission's **labels** that drifted. The consequence F-1 identified is
real: two accepted rows, **TC-UI-03** and **TC-UI-05**, ended up with no citation
under their own ID even though passing evidence for both exists. They are given
their citations below.

**No accepted contract row is changed by this reconciliation.**

| Accepted ID | What §16 actually requires | Accepted evidence level |
|---|---|---|
| TC-UI-01 | Every page renders at 320, 768 and 1280 CSS pixels with no horizontal body overflow | browser |
| TC-UI-02 | 200% reflow loses no content or function | browser |
| TC-UI-03 | Primary navigation and every control keyboard reachable, with a visible focus indicator | browser |
| TC-UI-04 | `prefers-reduced-motion` suppresses transitions while preserving focus indicators | browser |
| TC-UI-05 | Empty, loading, stale, denied, validation and system-error states each render from a **real view model** | browser |
| TC-UI-06 | No production template imports, links to or serves anything under `design-prototype/` | structural |
| TC-UI-07 | Contrast of production surfaces meets **WCAG 2.2** AA | source-derived tool + supervised |
| TC-UI-08 | Real-device check on Peter's hardware | **real device** |
| TC-UI-09 | Screen-reader traversal | **assistive technology** |

---

## 2. Results

### 2.1 The one browser session that has happened

**2026-08-24**, operator **Peter Duscha**, on the deployed staging service after
the S-1 restart. Recorded in full in
`phase-3-p3-5-supervised-session-evidence-2026-08-24.md` §3; summarised here under
the accepted numbering.

| Field | Value |
|---|---|
| Browser | **Google Chrome** — exact build **not recorded** |
| Operating system | **macOS 26** |
| Origin | `https://freedom-blades-test.rpgworld.org`, through the proxy password gate |
| Viewports | 320, 768, 1280 CSS pixels |
| Zoom | 100% and 200% |
| Assistive technology | **None used** |
| Views covered | **All seven**: anonymous `/v1/login`, member `/v1/characters`, Council `/v1/council/characters`, administrator `/v1/admin/role-capabilities`, denial/error `?failure=invalid`, emergency `/v1/auth/emergency`, sign-out |

**One browser, one platform.** That is why R-23 stays Active regardless of how
well the session went.

### 2.2 Row by row

| ID | Status | Evidence, and what is missing |
|---|---|---|
| **TC-UI-01** | **Passed** — one browser, one platform | All seven views at 320 / 768 / 1280. No horizontal overflow, clipping or unreachable content reported at any width. The operator could shrink the emergency view to roughly **100 CSS pixels**, well below the 320 the criterion requires, so the 320 column rests on a width narrower than specified rather than an approximation of it. Static support, cited as support and not as the row: `test_stylesheet_uses_responsive_relative_units`, `test_table_containers_have_overflow_scroll_guards` |
| **TC-UI-02** | **Passed** — one browser, one platform | 200% zoom on all seven views; no content or function lost. Includes emergency access and a **keyboard-actuated** sign-out under a live session |
| **TC-UI-03** | **Partly evidenced — recorded `Not Run` against the full row** | **This is one of F-1's two uncited rows, and it now has its citations.** *Browser half, observed:* keyboard traversal on the emergency view ("Tabs work fine", focus resting on usable elements with a visible indicator), and on the continuity shell the operator reached **Sign out** by Tab and actuated it with Enter, no mouse. *Static support:* `test_stylesheet_defines_high_contrast_focus_visible_indicators`, `test_stylesheet_has_no_unreplaced_outline_none`, `test_skip_link_visible_on_focus`, `test_form_controls_have_accessible_labels_and_valid_tabindex`, `test_buttons_and_links_have_accessible_names`, `test_base_template_landmarks_and_skip_link_order`. **Missing:** focus *order* across the full corpus, and **skip links observed reaching the right landmark in a browser** — the static test proves the link becomes visible on focus, not where it lands |
| **TC-UI-04** | **Not Run at its accepted level** | `test_tc_ui_04_prefers_reduced_motion_media_query` passes, with falsification `test_falsification_6_omitted_reduced_motion_fails`. That is the **static** half. The accepted level is a browser, and `prefers-reduced-motion` was never exercised in a real engine |
| **TC-UI-05** | **Partly evidenced — recorded `Not Run` against the full row** | **F-1's second uncited row.** *Observed in a browser:* the denial/error view at all widths and at 200%. *Automated, from real view models:* `test_validation_and_error_alert_roles_and_focusability`, `test_job_status_semantics_and_polling_silence`, the VM-22 `DeniedView` rows in `test_d03_contract_correction.py`, and the stale-state refusals in `test_p3_3_jobs.py` and `test_p3_2_success_cells.py`. **Missing:** the remaining five states — empty, loading, stale, validation, system-error — each rendered and inspected **in a browser** |
| **TC-UI-06** | **Passed** at its accepted level | `test_tc_ui_06_prototype_isolation_structural`, falsified by `test_falsification_5_prototype_reference_fails`; backend half `TC-SEC-14`. The accepted level **is** structural, so this row is complete. **Note the standing condition F-9:** `freedom-blades.rpgworld.org` currently serves `design-prototype/` as a static site, and the portal's site block replaces it at cutover |
| **TC-UI-07** | **Not Run at its accepted level** | `test_tc_ui_07_wcag_contrast_matrix` passes against **WCAG 2.2 AA**, falsified by `test_falsification_7_contrast_drop_fails`. That is the source-derived half. The accepted level is *source-derived tool **plus supervised***, and **real-engine contrast was never observed** |
| **TC-UI-08** | **Not Run** | Peter's own hardware. Not available to the Technical Lead by construction |
| **TC-UI-09** | **Not Run — permanently, for Phase 3** | Decision **D-f**, 2026-08-23: the Operations Owner confirms no current community member is known to rely on assistive technology, and **knowingly accepts the residual**. This row is **never** reclassified as passed. R-23 stays Active |

### 2.3 The no-JavaScript path, observed

Not a TC-UI row of its own, but the branch finding **F-15** lived in, so it is
recorded rather than left implicit.

The operator disabled JavaScript in Chrome and reloaded `/v1/auth/emergency`.
Where the security-key button would be, the page read exactly: *"Security key
sign-in requires browser script support. Use the recovery grant below if
JavaScript is disabled."* **No dead control appeared.**

**The recovery form was not submitted.** Exercising it needs a host-local recovery
grant, which is A-05 criterion 8 and a separate procedure; the form's presence
here is structural only.

**The HTMX-*enhanced* paths were not exercised at all.** Only the scriptless path
was. That is half of §13.4 criterion 4.

---

### 2.2 The second browser session — 2026-08-26, inside the SP-29 gate-off window

**Operator:** Peter Duscha. **Window:** `21:24:46Z` → `22:01:01Z` (decision D-r).

| Field | Value |
|---|---|
| Browser | **Google Chrome 151.0.7922.172 (Official Build) (arm64)** — the exact build, which the 2026-08-24 session did not record |
| Platform | macOS |
| Device (TC-UI-08) | **iPhone 15, iOS 26.6**, Safari |

**The gate had to come off first.** With the `basic_auth` gate in place, the
early-response case would have observed **Caddy's `401`** rather than the
application's own refusal — evidence that would have looked complete and been
wrong. That is finding **N-14**, and it is the reason this session could not
simply have been run at any time.

#### Results

| Check | Result |
|---|---|
| **CSP enforced by a real engine** | **Confirmed** — and it produced finding **N-23** below, which is a violation the engine reported and acted on |
| **OAuth redirect under `form-action 'self'`** (TC-SEC-07) | **Passed.** A Discord sign-in completed with **no `form-action` violation** in the console. A `GET`-initiated redirect is a navigation, not a form submission, and the engine agrees |
| **Skip link** | **Passed.** `<a href="#main-content" class="skip-link">Skip to main content</a>` targeting `<main id="main-content">` — a genuine landmark (`base.html:13,15`). Observed appearing on `Tab` and activating, the URL becoming `…#main-content`. No visible scroll is expected on a short page whose main content is already in view |
| **`prefers-reduced-motion`** | **Mechanism verified; effect imperceptible by design.** The frozen stylesheet carries a correct `@media (prefers-reduced-motion: reduce)` block over `*, *::before, *::after`. The only motion in the entire stylesheet is **10 short hover transitions**; with the setting enabled they become instant — a change no operator would perceive. The operator reported no visible difference, which is **consistent with correct behaviour, not with a defect** |
| **TC-UI-08, real device** | **Partly.** iPhone 15 / iOS 26.6, every view checked, zoom exercised, no defect reported. **768 and 1280 CSS pixels are not covered** — a phone offers only its own width (~393). An iPad (portrait ≈ 820, landscape ≈ 1180) would cover both remaining bands on real hardware and is queued |
| **HTMX-enhanced path exercised** | **Not Run** |
| **Real-engine contrast ratios** | **Not Run** |

#### N-23 — a live CSP violation, found only because a real engine ran the page

```text
htmx-2.0.10.min.js:1 Applying inline style violates the following Content Security
Policy directive 'style-src 'self'. … The action has been blocked.
```

HTMX 2.0.10 ships `includeIndicatorStyles: true` and injects an inline `<style>`
for `.htmx-indicator` at load; N-26's `style-src 'self'` has no nonce, so the
engine blocks it. **The CSP is working correctly.**

**No functional impact:** no template uses `hx-indicator`, and the stylesheet
defines no `.htmx-indicator` rules — HTMX is styling a feature the portal does not
use. **Still worth fixing**, because a violation on every HTMX page load is
console noise that would **mask a genuine one**. Proposed remediation, not
applied: `<meta name="htmx-config" content='{"includeIndicatorStyles":false}'>` in
`base.html` — no inline script, no stylesheet change, no touch to the frozen
assets.

**Parsed-DOM automation could not have found this.** It does not execute HTMX
inside an engine enforcing a policy.

#### An unprompted observation from the operator

Of the reconciliation job page, during the performance session the same evening:
*"the text should be smaller as I can't really read everything."* The cards are
generously sized and content overflows at his window width.

**Not blocking, and not a contrast or semantics defect.** It is recorded because
it is exactly what R-23 exists to collect — a usability judgement from the person
who will operate the screen, which no automated check produces and no contrast
inspector would have raised.

---

## 3. R-23 — where the residual actually stands

| §13.4 criterion | Status |
|---|---|
| 1. Keyboard-only operation, no traps, visible and logical focus order, skip links | **Partly, and improved 2026-08-26** — traversal and visible focus observed; **the skip link now Passed**, appearing on `Tab`, activating, and targeting a genuine `<main>` landmark. **Focus order across the full corpus remains Not Run** |
| 2. Semantics, headings, labels, descriptions, tables | **Not Run in a browser.** Parsed-DOM automation is extensive and passes; the accepted level is a browser |
| 3. Six states from a real view model | **Partly** — one of six observed |
| 4. HTMX-enhanced **and** JavaScript-disabled paths | **Half** — the scriptless path was observed, which is the half F-15 lived in. HTMX-enhanced was not |
| 5. 320 / 768 / 1280 and 200% zoom | **Passed** on one browser (TC-UI-01/02). **TC-UI-08 partly evidenced 2026-08-26** — a real iPhone 15 / iOS 26.6 at its native width, every view, zoom exercised. **768 and 1280 not covered**; an iPad would close both on real hardware |
| 6. Real-engine contrast and reduced motion | **Reduced motion: mechanism verified 2026-08-26** in a real engine, its imperceptibility explained by the stylesheet containing only 10 short hover transitions. **Real-engine contrast remains Not Run** |
| 7. Screen-reader traversal | **Not Run — permanently for Phase 3 (D-f)** |
| 8. Browser/OS/viewport/zoom/AT recorded for every result | **Met.** The exact Chrome build — **151.0.7922.172 (arm64)** — was recorded on 2026-08-26, closing the gap the 2026-08-24 session left |

### 3.1 The production-readiness consequence, stated plainly

Required by §13.4 and by the honest-outcome rule, and it belongs in the
submission verbatim:

> The portal would be exposed **without direct evidence that a screen-reader user
> can complete its essential workflows**. Every accessibility check that has
> actually been performed was performed by a sighted operator using a mouse and a
> keyboard in one browser on one platform. The automated suite is extensive and
> proves the markup carries the right semantics — it cannot prove a person using
> assistive technology can sign in, find their character and read it. That is an
> accessibility risk the Operations Owner accepts **knowingly** under decision
> D-f, rather than one that was tested away.

**R-23 is not closed by automation, and P3.4's acceptance did not close it.**

---

## 4. What is still to be observed, and by whom

| Procedure | Rows it would close | Owner |
|---|---|---|
| SP-23 remainder — skip-link landmark targeting, focus order across the corpus, the five unobserved states, HTMX-enhanced paths, real-engine contrast, `prefers-reduced-motion` | TC-UI-03, TC-UI-04, TC-UI-05, TC-UI-07 | Peter, his own browser (~30 min) |
| SP-18 — real-device inspection at 320/768/1280 and 200% | TC-UI-08 | **Peter only** (~15 min) |
| SP-19 — screen-reader traversal | TC-UI-09 | **Remains Not Run under D-f** |
| Record the exact Chrome build | completeness of §2.1 | Peter, one line |

**A second browser engine is not required by any accepted row.** It is worth
saying, because "one browser, one platform" appears throughout this document as a
limitation: the limitation is real and bounds what the evidence supports, but no
accepted criterion asks for Firefox or Safari. R-23 stays Active on the
assistive-technology row, not on the engine count.

---

## 5. What this document does not claim

- It does **not** promote any automated, structural or source-derived pass to a
  browser, device or assistive-technology row.
- It does **not** close R-23, TC-UI-03, TC-UI-04, TC-UI-05, TC-UI-07, TC-UI-08 or
  TC-UI-09.
- It does **not** change any accepted contract row; §1 reconciles labels only.
- It records **no** screenshot. None was captured during the 2026-08-24 session,
  so the synthetic-data screenshot rule (§10.4) has not yet had to be applied.
