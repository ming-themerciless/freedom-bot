# Prompt for Gemini — P3.4 Step 2: static asset foundation

Date: 2026-08-20 · Status: **RELEASED BY PETER / ACCEPTANCE AUTHORITY** · Step: 2 of 13

Peter/Acceptance Authority explicitly released this bounded Step 2 prompt on
2026-08-20. Gemini may perform Step 2 only and must stop at its checkpoint.
This release does not authorize Step 3, P3.G4 closure, staging, deployment,
production use, external/live-service contact, or real-player data.

You are Gemini, the P3.4 production frontend implementer. When this prompt is
released, perform **only Step 2**, deliver its checkpoint, and stop. Do not edit
templates or begin the shared shell, design system, or any later step.

## Read completely before acting

1. `.agents/AGENTS.md` and `docs/implementation-plan.md`;
2. the corrected, re-released
   `docs/review/phase-3-p3-4-gemini-implementation-prompt.md`, whose accepted
   SHA-256 is
   `cfe0517b45abc7d4dda4427c453af71348f8e147558373e581250dd851735fbb`;
3. `docs/review/phase-3-p3-4-gemini-execution-plan.md`, Step 2;
4. `docs/review/phase-3-p3-4-gemini-baseline.md`, especially the static-root
   inventory, Step 2 asset roles, overlap analysis, risks, and current verdict;
5. `docs/review/phase-3-p3-4-master-prompt-correction-acceptance.md`;
6. `docs/contracts/README.md` and every Phase 3 contract in its prescribed
   order, especially the route, configuration/dependency, threat-model, and
   test-traceability contracts;
7. `docs/operations/web-portal.md` §9 and M-01 `/static/`;
8. `docs/review/phase-3-visual-prototype-handoff.md` and the visual freeze
   manifest; and
9. every file under `design-prototype/`, read-only.

Before writing, verify the accepted master-prompt SHA-256, the visual freeze,
the current Git status, and the SHA-256 of every existing allowlisted file.
Treat every pre-existing modification as user work. Never inspect or alter a
stash.

## Step 2 objective

Create the bounded, same-origin static asset corpus needed by later P3.4 steps:

- one production CSS foundation adapted from the frozen visual language;
- one reviewed, vendored HTMX distribution file;
- one approved Freedom Blades guild-emblem copy or web derivative from the
  frozen emblem source;
- one integrity manifest covering every production static asset; and
- focused static-corpus structural and security tests.

Assets need not be referenced by a production template in this step. Step 3
owns the first template integration.

## Allowlist

Only these paths may change after this prompt is explicitly released:

- exactly one `adapters/web/static/css/freedom-blades.<12-lowercase-hex>.css`;
- exactly one `adapters/web/static/vendor/htmx-<version>.<12-lowercase-hex>.min.js`;
- exactly one `adapters/web/static/images/freedom-blades-token.<12-lowercase-hex>.png`;
- `adapters/web/static/asset-integrity.sha256`;
- `tests/web/test_p3_4_static_assets.py`; and
- `adapters/web/static/.gitkeep`, removal only after the real asset files exist.

The 12-hex fingerprint in each asset filename is the first 12 lowercase
hexadecimal characters of that file's full SHA-256. If content changes, its
filename and integrity entry change together. Do not create an unhashed alias,
source map, extra font, extra image, generated cache, temporary file, or second
stylesheet/script.

Do not edit backend Python, middleware, routes, view models, contracts,
operations documents, templates, dependencies, lock files, configuration,
other tests, project-management records, `design-prototype/`, or this prompt.

## Asset requirements

### Production CSS foundation

- Adapt only the tokens and foundational primitives needed for later P3.4
  screens: color, typography using a local system-font stack, spacing, radii,
  shadows, layout/container primitives, table overflow, status/alert surfaces,
  visible focus, and reduced-motion behavior.
- Preserve the accepted visual language without copying prototype-only page
  markup or the excluded portrait dialog/approval workflow.
- Use no remote URL, font, import, data URL, executable behavior, preprocessor,
  build step, or reference to `design-prototype/` in the production file.
- Keep the stylesheet useful at 320, 768, and 1280 CSS pixels and under 200%
  reflow, while reserving full page-level responsive evidence for Step 11.

### Vendored HTMX

- Use only a locally available, maintainer-authorized upstream distribution
  whose version and exact bytes can be identified. Do not download it, contact
  a CDN, install npm, add a package manager, or reconstruct/minify a library by
  hand.
- Record version, canonical upstream project URL, full upstream-file SHA-256,
  and local vendored-file SHA-256 in a leading preserved comment when the
  distribution format permits it and in the integrity manifest in all cases.
- Do not add extensions, source maps, plugins, or remote fallbacks.
- If the authorized HTMX distribution bytes are not already available in the
  workspace or explicitly supplied with the released prompt, stop before any
  write and report `BLOCKED: approved HTMX source bytes unavailable`.

### Guild emblem

- Derive only from
  `design-prototype/assets/freedom-blades-token.png`, leaving the frozen source
  byte-identical.
- Preserve aspect ratio and transparency. Strip unnecessary metadata and do not
  add player, character, external, or generated imagery.
- Record the frozen source SHA-256 and production derivative SHA-256 in the
  integrity manifest.

### Integrity manifest

- Use standard `sha256sum -c` syntax for each production asset, with paths
  relative to the repository root and sorted by path.
- Add comment lines for HTMX version/upstream provenance and emblem source
  provenance without weakening `sha256sum -c` compatibility.
- The manifest must not list itself or `.gitkeep`.

## Required tests

Create `tests/web/test_p3_4_static_assets.py` proving at least:

1. the static corpus equals the closed Step 2 inventory exactly;
2. every asset filename has the required kind and fingerprint grammar;
3. every filename fingerprint equals the first 12 characters of its content
   SHA-256 and every manifest digest equals the full digest;
4. `sha256sum -c adapters/web/static/asset-integrity.sha256` succeeds;
5. the HTMX version and provenance are present and its bytes match the recorded
   digest;
6. the emblem provenance points only to the frozen approved source and that
   source still matches the visual freeze manifest;
7. CSS and JavaScript contain no remote origin, `@import`, remote font,
   `data:`/`javascript:` URL, source-map reference, or
   `design-prototype/` production reference;
8. the CSS includes visible `:focus-visible`, reduced-motion, local table
   overflow, and the required responsive foundation without hiding content;
9. no template, backend, route, view model, dependency, or configuration file
   changed as part of Step 2; and
10. the existing M-01 route/static structural guards still pass without a
    backend change.

Tests must inspect bytes and structure; do not weaken an existing guard or use
an assertion that merely restates a manifest produced by the same unchecked
code path.

## Required verification

Run only local, non-network checks:

```bash
sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256
sha256sum -c adapters/web/static/asset-integrity.sha256
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py tests/web/test_structural_guards.py
./venv-web/bin/python -m compileall tests/web/test_p3_4_static_assets.py
git diff --check
git diff --name-only
git status --short
```

Report literal commands, exit codes, pass/skip counts, and unavailable evidence
accurately. Do not point tests at a database, run migrations, install a browser
or dependency, or substitute a network fetch for unavailable HTMX bytes.

## Stop conditions

Stop without expanding scope if:

- this prompt is still held or has not been explicitly released;
- the accepted master-prompt hash or visual freeze differs;
- an allowlisted existing file overlaps unidentified user work;
- approved HTMX source bytes and provenance are unavailable locally;
- the emblem's frozen-source digest differs;
- an asset cannot satisfy M-01's filename grammar or cache policy;
- a required correction would touch a template, backend, contract, dependency,
  configuration, or later-step file; or
- any required structural/security check fails for a reason within Step 2.

## Checkpoint report and stop

Report:

- every file changed and its before/after SHA-256 (`absent` where new);
- the closed asset inventory, filenames, versions, provenance, and full hashes;
- the exact visual tokens/primitives adapted and prototype-only behavior
  excluded;
- tests and commands with literal results;
- skipped and not-run checks with reasons;
- confirmation that templates, backend, contracts, dependencies,
  configuration, the frozen prototype, and user-owned changes were untouched;
- residual risks and any contract question;
- `git diff --check`, `git diff --name-only`, and final Git status; and
- verdict `READY FOR STEP 3` or `BLOCKED`, with reasons.

Then stop. Do not edit a template, begin Step 3, close P3.G4, contact a live
service, or claim staging/deployment/production authorization.
