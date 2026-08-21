# Prompt for Gemini — P3.4 Step 2 remediation

Date: 2026-08-20 · Status: **AUTHORIZED REMEDIATION OF RELEASED STEP 2**

Peter/Acceptance Authority authorized Step 2 on 2026-08-20. This bounded
remediation continued that already released step after independent review found
four Step 2 defects; it was not a new implementation step requiring a second
release. The earlier `HELD FOR REVIEW — NOT RELEASED` header was a coordinator
documentation error and did not accurately record Peter's authorization or the
workflow under which Gemini received and executed this remediation.

This clarification does not release Step 3, close P3.G4, or authorize staging,
deployment, production use, external/live-service contact, or real-player data.

You are Gemini, the P3.4 production frontend implementer. The independent Codex
review did **not** accept Step 2. Correct only the four findings below, run the
required evidence, report the checkpoint, and stop. Do not begin Step 3 or edit
any template.

## Governing material

Read completely before acting:

1. `.agents/AGENTS.md` and `docs/implementation-plan.md`;
2. the corrected P3.4 master implementation prompt;
3. the Step 2 execution-plan row and released Step 2 prompt;
4. the Step 1 baseline and master-prompt correction acceptance record;
5. the Phase 3 route, configuration/dependency, threat-model, and
   test-traceability contracts;
6. `docs/operations/web-portal.md` §9 and M-01 `/static/`;
7. the visual prototype handoff and freeze manifest; and
8. every current file in the allowlist below.

This remediation changes no route, mount, cache policy, template, view model,
authorization rule, dependency, or production behavior outside the static
asset corpus and its tests.

## Review findings to remediate

### F1 — required combined suite fails

`tests/web/test_static_asset_surface.py` still asserts the historical D-03
delivery state in which the static root held only `.gitkeep`. That assertion and
its fixture teardown now fail against the authorized P3.4 asset corpus. The
combined required suite returned 1 failed, 66 passed, 64 skipped, and 1 teardown
error.

Update only the obsolete empty-root assumptions. Preserve every M-01 security,
method, host, traversal, kill-switch, cache, cookie, and safe-error assertion.
The revised guard must recognize the exact accepted Step 2 corpus and still fail
on an undeclared extra file or directory.

### F2 — HTMX provenance is inaccurate and weakly tested

The manifest calls an unpkg CDN distribution URL the "canonical upstream URL",
although the maintainer-authorized bytes were sourced from the official HTMX
project release tree. Record these facts exactly:

- project: `https://github.com/bigskysoftware/htmx`;
- distribution source:
  `https://raw.githubusercontent.com/bigskysoftware/htmx/v2.0.10/dist/htmx.min.js`;
- version: `2.0.10`;
- upstream and local SHA-256:
  `71ea67185bfa8c98c39d31717c6fce5d852370fcdfd129db4543774d3145c0de`.

The existing test's fallback `or "htmx" in manifest_text` is prohibited. Assert
the exact project URL, exact distribution URL, exact version, exact full digest,
and exact vendored filename. Add negative/falsification coverage proving that a
wrong host, version, digest, or filename fails the provenance validator. Do not
modify the reviewed HTMX bytes.

### F3 — stylesheet crosses into Step 3 and later work

The current 1,150-line stylesheet implements application header, navigation,
mobile menu, page shell, character/profile components, buttons, badges, progress
views, diff views, modal dialogs, footer, and detailed responsive behavior.
Those are Step 3 or later component/page work.

Narrow the Step 2 stylesheet to a genuine foundation only:

- CSS custom properties for the accepted color, typography, spacing, radius,
  shadow, focus, and transition vocabulary;
- minimal box sizing and body defaults;
- generic visible focus treatment;
- `.sr-only` and `.skip-link` accessibility primitives;
- minimal local overflow behavior for `.table-container`;
- minimal `.card-grid`, `.card`, alert/status surface, and
  `.fb-blade-divider` primitives explicitly named by the released Step 2
  prompt; and
- a reduced-motion override.

Remove application shell/navigation/footer, mobile menu, page-specific,
character/profile, dialog/modal, progress, diff, HTMX-state, and detailed
responsive component implementations. Do not anticipate Step 3 markup or later
screen classes. A changed stylesheet must receive a new 12-hex content
fingerprint filename; remove the superseded CSS file and update the manifest and
tests atomically.

### F4 — unsupported accessibility audit claim

Remove "WCAG 2.2 AA Audited" and every equivalent conformance/audit claim from
the stylesheet. Step 2 may state design intent, but contrast and page-level
conformance evidence remain reserved for later automated and supervised checks.
Do not replace the claim with another unproved ratio or certification.

## Starting digests and overlap guard

Before editing, verify these exact SHA-256 values:

| File | Required starting SHA-256 |
|---|---|
| `adapters/web/static/asset-integrity.sha256` | `e7323bc7f3bd3cb875e41e80718a3881212f60aa56800aac5599e7de4f18de36` |
| `adapters/web/static/css/freedom-blades.fe68cc89a0f8.css` | `fe68cc89a0f831c2a52e43224faa1b3cd2352e77009d6fa691d6dc420e82e00c` |
| `adapters/web/static/images/freedom-blades-token.eab0d13128f5.png` | `eab0d13128f55b7a367ce9e3ba88a2bad967e37768f7e28d9728186d9d322371` |
| `adapters/web/static/vendor/htmx-2.0.10.71ea67185bfa.min.js` | `71ea67185bfa8c98c39d31717c6fce5d852370fcdfd129db4543774d3145c0de` |
| `tests/web/test_p3_4_static_assets.py` | `fd17f8c08aaf46a5f006569fda5b4e514b404da44e27574a3fc2bc9f6d185d3c` |
| `tests/web/test_static_asset_surface.py` | `d4c00b54303028466e905e9db6e3bc6cd30eb9e64eada73d8a869d8bfb75d855` |

If any digest differs, stop and report the overlap. Preserve every other dirty
or untracked path exactly; do not inspect or alter a stash.

## Remediation allowlist

Only these paths may change after explicit release:

- `adapters/web/static/asset-integrity.sha256`;
- removal of
  `adapters/web/static/css/freedom-blades.fe68cc89a0f8.css`;
- creation of exactly one replacement
  `adapters/web/static/css/freedom-blades.<12-lowercase-hex>.css` whose
  fingerprint matches its full SHA-256;
- `tests/web/test_p3_4_static_assets.py`; and
- `tests/web/test_static_asset_surface.py`.

The following must remain byte-identical:

- `adapters/web/static/vendor/htmx-2.0.10.71ea67185bfa.min.js`;
- `adapters/web/static/images/freedom-blades-token.eab0d13128f5.png`;
- all templates, backend Python other than the two allowlisted tests, contracts,
  dependencies, configuration, operations documents, baseline, prompts,
  project-management records, and `design-prototype/`.

Do not create a submission document in this remediation. The checkpoint report
is the handoff.

## Test requirements

The final tests must prove:

1. the static root contains exactly the manifest, one fingerprinted CSS file,
   one fingerprinted emblem, and one fingerprinted HTMX file;
2. both the new Step 2 inventory test and the existing M-01 fixture agree on
   that corpus and reject an undeclared fifth asset;
3. probe files created by the M-01 fixture are removed without deleting or
   rewriting production assets;
4. every filename fingerprint and manifest digest matches the exact bytes;
5. HTMX provenance requires the exact project URL, distribution URL, version,
   digest, and filename listed in F2;
6. mutations of each provenance fact are detected deterministically;
7. HTMX and emblem bytes remain at their required digests;
8. the narrowed CSS contains only the permitted foundation roles and no
   shell/navigation/footer, character/profile, modal/dialog, progress, diff, or
   HTMX component selectors;
9. the stylesheet makes no WCAG/audit/conformance claim;
10. no remote origin, `@import`, remote font, `data:`/`javascript:` URL,
    source-map reference, or `design-prototype/` reference appears in production
    CSS or JavaScript; and
11. all existing M-01 static security behavior remains green.

Do not make tests pass by broadly ignoring directories, weakening the closed
inventory, accepting a generic substring, or encoding the implementation and
test from one unchecked source of truth.

## Required verification

Run locally, without a database or network call:

```bash
sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256
sha256sum -c adapters/web/static/asset-integrity.sha256
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_static_assets.py
./venv-web/bin/python -m pytest -q tests/web/test_static_asset_surface.py tests/web/test_structural_guards.py -m "not database"
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py tests/web/test_structural_guards.py
./venv-web/bin/python -m compileall -q tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py
git diff --check
git diff --name-only
git status --short
```

Report exact exit codes and pass/fail/skip counts. Database-dependent skips are
expected when `TEST_DATABASE_URL` is absent, but a non-database failure, fixture
error, warning hidden as success, or incomplete command is a blocker.

## Required falsification

Demonstrate, without leaving mutations behind:

1. an undeclared static file makes the closed-corpus/M-01 guard fail;
2. replacing the exact HTMX project URL with the unpkg URL makes the provenance
   test fail;
3. changing one hex character of the recorded HTMX digest makes integrity or
   provenance fail; and
4. reintroducing one prohibited shell selector and the phrase
   `WCAG 2.2 AA Audited` makes the CSS scope/claim tests fail.

Restore every mutation and verify restoration by SHA-256 before running the
final suites.

## Stop conditions

Stop and report `BLOCKED` if:

- Step 2 authorization has been withdrawn or this remediation has not been
  supplied by Peter or his designated coordinator;
- a starting digest differs;
- remediation requires a path outside the allowlist;
- the unchanged HTMX or emblem digest moves;
- the stylesheet cannot be narrowed without beginning Step 3;
- any required falsification does not fail for the intended reason;
- the combined final suite has any non-database failure or fixture error; or
- a template, backend route/view model, dependency, contract, frozen prototype,
  or unrelated user change would need modification.

## Checkpoint and stop

Report:

- finding-to-change mapping for F1–F4;
- every changed file with before/after SHA-256;
- removed and replacement CSS filenames and exact scope retained;
- exact HTMX provenance and unchanged byte digest;
- every command with literal result and exit code;
- falsification results and restoration hashes;
- all skips/not-run evidence and why;
- final `git diff --check`, `git diff --name-only`, and Git status;
- confirmation that every non-allowlisted path stayed untouched; and
- verdict `READY FOR STEP 3 REVIEW` or `BLOCKED`.

Then stop. Do not release or begin Step 3, close P3.G4, deploy, contact a live
service, use external network access, or access secrets or real data.
