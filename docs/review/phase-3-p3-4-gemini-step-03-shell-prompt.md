# Prompt for Gemini — P3.4 Step 3: shared shell and design system

Date: 2026-08-20 · Status: **RELEASED BY PETER / ACCEPTANCE AUTHORITY** · Step: 3 of 13

Peter/Acceptance Authority explicitly released this bounded Step 3 prompt on
2026-08-20. Perform Step 3 only, deliver its checkpoint, and stop. This release
does not authorize Step 4, P3.G4 closure, staging, deployment, production use,
external/live-service contact, or real-player data.

You are Gemini, the P3.4 production frontend implementer. Build the shared
production shell and design-system layer on the accepted Step 2 static
foundation. Do not convert or redesign any page body in this step.

## Read completely before acting

1. `.agents/AGENTS.md` and `docs/implementation-plan.md`;
2. the corrected P3.4 master implementation prompt;
3. `docs/review/phase-3-p3-4-gemini-execution-plan.md`, Step 3;
4. the Step 1 baseline;
5. the released Step 2 prompt, Step 2 remediation prompt, and
   `phase-3-p3-4-step-02-review-and-acceptance.md`;
6. `docs/contracts/README.md` and every Phase 3 contract in prescribed order,
   especially route authorization, view models, threat model, and test
   traceability;
7. `docs/operations/web-portal.md` §9 and M-01 `/static/`;
8. the visual-prototype handoff and freeze manifest; and
9. all 24 current production templates and every relevant structural/static
   test, read-only except for the files explicitly allowlisted below.

Record initial `git status --short` and verify all starting hashes before any
write. Preserve all unrelated dirty and untracked work and every stash exactly.

## Step 3 objective

Implement:

- the semantic `base.html` document shell;
- a shared header/navigation include;
- a shared footer include;
- same-origin references to the accepted fingerprinted CSS, HTMX, and emblem;
- shell-only CSS for the forged-steel two-level header, navigation, main
  container, footer, focus treatment, reduced motion, and responsive behavior;
  and
- focused source/rendering tests for shell structure and safety.

The shell must remain useful with JavaScript disabled. HTMX is loaded with
`defer` as progressive enhancement and must not be necessary for navigation or
any existing page body.

## Authority and navigation boundary

`base.html` receives `request` from the existing Starlette/Jinja rendering
boundary and the page's existing `view`; it receives no shared authenticated
principal, capability list, role, display name, or navigation view model.

Therefore:

- do not invent a context field or read application state;
- do not display a username, guild name, capability, role, emergency status, or
  sign-in status in the shared shell;
- do not use navigation visibility as authorization;
- use `request.url.path` only to choose presentation state such as
  `aria-current`, never to infer authority;
- keep shared navigation to stable, ordinary GET destinations already in the
  route contract; and
- do not render mutation controls in the shell.

Restricted route existence is not an authorization fact, but the shared shell
should not advertise Council/administrator actions to callers for whom it has no
capability context. Later page steps may add contextual links only where their
accepted view model supports them.

## Starting hashes

Verify exactly:

| File | Required SHA-256 |
|---|---|
| `adapters/web/templates/base.html` | `51f45cf7ae559923c1f37c14d7d8dec19ab4004a8200d8a653569c06e9d855d9` |
| `adapters/web/static/asset-integrity.sha256` | `fa4176a25cb0d51fcbc72a112d44862c060dee82e78137d8cee2b3c1ce9fabba` |
| `adapters/web/static/css/freedom-blades.fc5190225c5c.css` | `fc5190225c5c4943be9ce5af3e4c9d1bf11b9e7c87118244c551260609c0cdc2` |
| `adapters/web/static/vendor/htmx-2.0.10.71ea67185bfa.min.js` | `71ea67185bfa8c98c39d31717c6fce5d852370fcdfd129db4543774d3145c0de` |
| `adapters/web/static/images/freedom-blades-token.eab0d13128f5.png` | `eab0d13128f55b7a367ce9e3ba88a2bad967e37768f7e28d9728186d9d322371` |
| `tests/web/test_p3_4_static_assets.py` | `ad14c56c5bdfdeaa74dedb212933aa3be8c7b95f9d1c2fd8edc42a54f0b81be0` |
| `tests/web/test_static_asset_surface.py` | `2b3718460c3d1d1eee2b31c8abf6a06914ee4b83a7fd2aa1e43a591bd2876c8e` |

These paths must be absent before work:

- `adapters/web/templates/includes/header.html`;
- `adapters/web/templates/includes/footer.html`; and
- `tests/web/test_p3_4_shell_and_components.py`.

Stop on any mismatch or overlap.

## Allowlist

Only these paths may change:

- `adapters/web/templates/base.html`;
- new `adapters/web/templates/includes/header.html`;
- new `adapters/web/templates/includes/footer.html`;
- removal of
  `adapters/web/static/css/freedom-blades.fc5190225c5c.css`;
- one replacement
  `adapters/web/static/css/freedom-blades.<12-lowercase-hex>.css` whose filename
  fingerprint equals its content SHA-256;
- `adapters/web/static/asset-integrity.sha256`;
- `tests/web/test_p3_4_static_assets.py`, only to replace Step 2's now-obsolete
  prohibition of Step 3 shell selectors while retaining all inventory,
  integrity, provenance, forbidden-origin, and audit-claim controls;
- `tests/web/test_static_asset_surface.py`, only to update the exact CSS
  filename after its fingerprint changes; and
- new `tests/web/test_p3_4_shell_and_components.py`.

The HTMX and emblem files must remain byte-identical. Do not edit any child or
fragment template, backend Python, route, view model, contract, dependency,
configuration, operation document, project-management record, prior review
record, prompt, or `design-prototype/` file.

## Shell requirements

### `base.html`

- Preserve `<!doctype html>`, `lang="en"`, UTF-8, viewport, and the existing
  overridable title block.
- Reference the exact fingerprinted stylesheet and emblem through M-01
  same-origin `/static/` URLs. Reference the exact vendored HTMX script with
  `defer`; use no inline script or inline event handler.
- The first focusable body element is a skip link targeting `#main-content`.
- Render one semantic `<header>`, one labelled `<nav>`, one
  `<main id="main-content">`, and one `<footer>` in that order.
- Keep `{% block content %}` inside the main landmark and do not introduce an
  `<h1>` in the shell; each page body owns its one page heading as it is converted
  in later steps.
- Add small extension blocks only when a concrete later consumer is already
  identified, and keep defaults inert.
- Use includes without `ignore missing`, dynamic filenames, dynamic template
  names, or context widening.

### Shared header/navigation

- Extend the accepted two-level forged-steel visual direction using static,
  translatable-safe text and the approved emblem.
- Provide ordinary anchor navigation that works without JavaScript.
- Ensure exactly one navigation item has `aria-current="page"` for every path
  rendered through the shell, using a deterministic fallback and only
  `request.url.path`.
- Do not claim caller identity or authority and do not expose privileged action
  controls.
- Do not create a JavaScript mobile-menu dependency. Navigation must wrap or
  reflow in CSS while remaining present and keyboard reachable.

### Shared footer

- Keep it static and non-sensitive. Do not render environment, version,
  correlation, guild, account, role, or operational state.

### CSS

- Retain every accepted Step 2 token and primitive unless a demonstrated shell
  need requires a compatible refinement.
- Add only classes used by `base.html`, `header.html`, or `footer.html` for the
  header, brand, navigation, main container, footer, and responsive shell.
- Provide visible `:focus-visible`, a skip-link reveal, 320/768/1280-friendly
  wrapping, 200% reflow-safe sizing, no horizontal body overflow, and reduced
  motion without suppressing focus.
- Use system fonts and same-origin assets only. No dialog, modal, page-specific,
  character/profile, progress, diff, approval-queue, or hidden mobile-navigation
  component belongs in Step 3.
- Make no WCAG conformance/audit claim; final contrast evidence remains later.

## Test requirements

Create `tests/web/test_p3_4_shell_and_components.py` proving at least:

1. all starting child templates remain byte-identical and still extend
   `base.html`;
2. the base source references exactly the manifest-listed CSS, HTMX, and emblem
   under `/static/`, with HTMX `defer` and no remote fallback;
3. source and representative safe rendering contain header, labelled nav, main,
   footer, skip link, and correct landmark order;
4. the skip link is the first focusable body element and targets the sole
   `main-content` id;
5. representative paths select exactly one `aria-current="page"`, including an
   unknown/error-path fallback;
6. shell rendering introduces no username, guild, capability, role, emergency,
   correlation, environment, or object facts;
7. no shell file contains `|safe`, `hx-on:`, an inline event handler, inline
   executable script, remote origin/font, `design-prototype/` reference, or
   dynamic include;
8. navigation is made from ordinary anchors and has no JavaScript-only toggle;
9. CSS contains only permitted Step 2 foundation plus Step 3 shell selectors,
   with responsive wrapping, no horizontal body overflow, visible focus, and
   reduced motion;
10. the full 24-template corpus still contains zero `|safe`, `hx-on:`, inline
    executable script, remote origin/font, and `design-prototype/` reference;
11. `TC-UI-06` passes structurally for the complete production template/static
    corpus; and
12. Step 2 inventory, exact provenance, fingerprint, manifest, and M-01 tests
    remain green after the CSS rename.

Use the real Jinja environment or an equivalent strict rendering that includes
the actual files. Representative test data must be synthetic and bounded. Do
not weaken autoescape, instantiate a second application settings authority, or
require a database merely to prove shell structure.

## Required verification

Run locally without network or live services:

```bash
sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256
sha256sum -c adapters/web/static/asset-integrity.sha256
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_shell_and_components.py
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py tests/web/test_structural_guards.py -m "not database"
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py tests/web/test_structural_guards.py
./venv-web/bin/python -m compileall -q tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py
git diff --check
git diff --name-only
git status --short
```

Report commands literally with exit codes and pass/skip counts. Database skips
are acceptable only when `TEST_DATABASE_URL` is absent; any source/rendering
failure is a blocker. Do not install or run a browser in this step.

## Required falsification

Demonstrate and restore by digest:

1. removing the skip-link target or moving the skip link after another
   focusable element fails the shell test;
2. adding a second `aria-current="page"` fails for a representative path;
3. adding an inline handler, remote origin, `|safe`, or
   `design-prototype/` reference fails the corpus guard;
4. adding a dynamic/ignored include fails the include guard; and
5. changing the CSS bytes without changing its fingerprint and manifest fails
   both fingerprint and integrity checks.

Leave no mutation or temporary file behind.

## Stop conditions

Stop and report `BLOCKED` if:

- a starting digest or required absence differs;
- any child or fragment template must change;
- shell requirements need a new backend/context/view-model field;
- correct navigation would require inferring caller authority;
- any route, template-body, dependency, configuration, contract, or frozen
  prototype change appears necessary;
- HTMX or emblem bytes move;
- a falsification does not fail for the intended reason; or
- any final non-database check fails.

## Checkpoint and stop

Report:

- every changed file with before/after SHA-256 (`absent` where new);
- old and replacement CSS names, full digest, and manifest result;
- shell structure, navigation destinations/current-path mapping, includes, and
  CSS selector scope;
- tests, literal results, and evidence classes;
- falsification and restoration results;
- skipped/not-run checks and residual risks;
- confirmation that all non-allowlisted files, HTMX, emblem, and visual freeze
  remained byte-identical;
- final `git diff --check`, `git diff --name-only`, and status; and
- verdict `READY FOR STEP 4 REVIEW` or `BLOCKED`.

Then stop. Do not convert a page body, begin or release Step 4, close P3.G4,
deploy, contact a live service, use external network access, or access secrets
or real data.
