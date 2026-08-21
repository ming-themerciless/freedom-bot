# Prompt for Gemini — P3.4 Step 3 remediation 02

Date: 2026-08-20 · Status: **AUTHORIZED CONTINUATION OF RELEASED STEP 3 REMEDIATION**

Peter/Acceptance Authority requested this second bounded remediation on
2026-08-20 after independent re-review found two remaining test-evidence
defects. This is an authorized continuation of the already released Step 3; it
is not a release of Step 4.

This authorization does not accept or close Step 3, release or begin Step 4,
close P3.G4, or authorize staging, deployment, production use, external/live
service contact, secrets, or real-player data.

You are Gemini, the P3.4 production frontend implementer. Correct only B1 and
B2 below in the single allowlisted test module, run all required evidence,
deliver the checkpoint, and stop.

## Read completely before acting

1. `.agents/AGENTS.md` and `docs/implementation-plan.md`;
2. the corrected P3.4 master implementation prompt;
3. the released Step 3 prompt;
4. the first authorized Step 3 remediation prompt;
5. `docs/review/phase-3-p3-4-step-03-remediation-review.md`; and
6. the complete current `tests/web/test_p3_4_shell_and_components.py`.

Record initial `git status --short` and verify every starting digest before any
write. Preserve all unrelated dirty/untracked work and every stash exactly.

## B1 — reject ordinary inline HTML event handlers

The shared corpus helper `validate_template_security_rules` currently rejects
`hx-on:` but accepts ordinary inline event-handler attributes. Independent
review passed this input through the helper without an exception:

```html
<button onclick="alert(1)">x</button>
```

Extend the same helper used by the positive complete-corpus test to reject any
HTML attribute whose name starts with `on` and is followed by an event name,
case-insensitively, when followed by optional whitespace and `=`. This includes
at least `onclick`, `onerror`, `onload`, mixed/upper-case forms, and whitespace
around `=`. Detect attributes in active template markup after Jinja comments
are removed. Do not reject innocent text containing the letters `on`, an
ordinary attribute such as `nonce`, or a prose/code comment that is already
excluded by the established comment-handling contract.

The positive full-corpus test must continue to invoke this helper. Add
parameterized falsification that supplies at least:

- `onclick="..."`;
- `onerror = "..."`;
- `ONLOAD='...'`; and
- one mixed-case handler name.

Each must pass through `validate_template_security_rules` and be rejected for a
specific inline-event-handler reason using `pytest.raises(AssertionError,
match=...)`. Include bounded positive probes proving `nonce="..."` and plain
text containing `onload` without attribute assignment are not false positives.
Retain all existing `|safe`, HTMX handler, remote origin/font,
`design-prototype/`, and inline-script controls and falsifications.

## B2 — make manifest falsification depend on the tampered bytes

`validate_manifest_integrity(manifest_path, static_dir)` currently ignores
`static_dir` and resolves manifest entries through global repository `ROOT`.
The negative test creates mutated temporary CSS but uses an independently wrong
zero digest against unchanged production bytes. Its failure is therefore
unrelated to the mutation.

Refactor the helper so its second argument is a deliberately named and actually
used resolution root. Manifest paths are repository-relative, so the positive
production test must call the helper with the production manifest and `ROOT`.
The helper must reject malformed entries, absent files, and digest mismatches
without consulting a hidden global path authority for file resolution.

Add a positive Step 3 test that calls this exact helper against the real
production manifest and production `ROOT`.

For falsification:

1. create a bounded temporary root containing the same repository-relative
   directories and copies of every file named by the unchanged production
   manifest;
2. copy the production manifest without changing any digest or path;
3. confirm the shared manifest helper passes against that temporary root before
   mutation;
4. append or alter one byte in the temporary CSS only;
5. pass the unchanged copied manifest and temporary root through the same
   helper and assert a path-specific CSS digest mismatch;
6. independently pass the mutated temporary CSS through
   `validate_css_fingerprint` and assert a fingerprint mismatch; and
7. prove the production CSS and manifest hashes remain unchanged.

Do not write a zero digest, alter the copied manifest, resolve the negative test
through production `ROOT`, or make failure independent of the mutated CSS.

## Starting digests and overlap guard

Verify exactly before editing:

| File | Required starting SHA-256 |
|---|---|
| `tests/web/test_p3_4_shell_and_components.py` | `b195c5f11b0fd1084a0ffa2f2b7095820c0ef6be37d73376339e54b50823835f` |
| `adapters/web/templates/base.html` | `3048bd5bb561dfc5f26bfbf30353f7ddd474d804ebe65c2c5349a1b2f5566585` |
| `adapters/web/templates/includes/header.html` | `ede238e9d6f83c70eb228b54d58d40fa5b01d6df4c82ce8479c641dc28a46796` |
| `adapters/web/templates/includes/footer.html` | `2f1068b436a38a7ef79580aec4b55ed23dcaa5a3b827596509caa000ed72f7c3` |
| `adapters/web/static/css/freedom-blades.e82fec19acd3.css` | `e82fec19acd3322066330a8a48a7d832446227fc9f805a0ffe54e6c7d9c12599` |
| `adapters/web/static/asset-integrity.sha256` | `08f6c81f09488749b6caefcc0da6c86efef03e220da8a2d2dc7334429a1f394b` |
| `adapters/web/static/vendor/htmx-2.0.10.71ea67185bfa.min.js` | `71ea67185bfa8c98c39d31717c6fce5d852370fcdfd129db4543774d3145c0de` |
| `adapters/web/static/images/freedom-blades-token.eab0d13128f5.png` | `eab0d13128f55b7a367ce9e3ba88a2bad967e37768f7e28d9728186d9d322371` |
| `tests/web/test_p3_4_static_assets.py` | `f9d0076f6a2dfdebf486f0087939772f2c9174842a78230c592f56de8c4efdfa` |
| `tests/web/test_static_asset_surface.py` | `c11f0c6624ecd5a45034a87f1d38beeed07347038081dec8c94d116cebf6eff2` |
| `docs/review/phase-3-p3-4-step-03-remediation-review.md` | `32798869d97f0243e73abc8ca80efcbe6faf95325806d378079e252ad5c8d877` |

Also run the existing 23-template preservation test before editing. Stop and
report `BLOCKED` if any digest or immutable-template check differs.

## Exact allowlist

Only this file may change:

- `tests/web/test_p3_4_shell_and_components.py`.

Everything else must remain byte-identical, including `base.html`, header,
footer, all 23 child/fragment templates, CSS, manifest, HTMX, emblem, Step 2
tests, backend Python, routes, view models, contracts, dependencies,
configuration, operations/project-management/review documents and prompts, and
the frozen prototype. Do not create a submission document; the checkpoint
report is the handoff.

## Test-design constraints

- Both positive and negative cases must invoke the exact same helper for each
  invariant.
- The inline-handler detector must be case-insensitive and attribute-aware.
- The manifest helper's explicit root argument must be its only authority for
  resolving manifest asset paths.
- The temporary manifest must be byte-identical to production and initially
  pass before the CSS mutation.
- Failure matching must identify the intended handler or CSS path/invariant;
  accepting an arbitrary exception is prohibited.
- Preserve every currently passing control and all prior falsifications.
- No production mutation, database, network, browser, secret, alternate
  settings authority, live service, or player data is permitted.

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

Report literal commands, exit codes, and pass/fail/skip counts. Database skips
are acceptable only when `TEST_DATABASE_URL` is absent. Any non-database
failure, fixture error, warning hidden as success, or incomplete command is a
blocker.

## Required falsification checkpoint

Report:

- every inline-handler mutation and exact expected/observed helper failure;
- the harmless inline-handler false-positive probes and their passing result;
- the temporary manifest's pre-mutation passing result;
- the exact CSS byte mutation;
- the post-mutation manifest-integrity and fingerprint failures, including the
  CSS path;
- confirmation that the copied manifest stayed byte-identical; and
- production CSS/manifest before-and-after hashes.

## Stop conditions

Stop and report `BLOCKED` if:

- a starting or immutable digest differs;
- the work requires any path outside the one-file allowlist;
- an ordinary `on*=` handler passes the corpus helper;
- a harmless non-attribute probe is rejected;
- the temporary tree does not pass before mutation;
- the copied manifest changes;
- either post-mutation check fails for a reason independent of the changed CSS
  byte;
- positive and negative cases use different validation logic;
- any production file is mutated;
- any final non-database check fails; or
- satisfying the work would begin Step 4.

## Checkpoint and stop

Report:

- B1/B2 finding-to-change mapping;
- the allowlisted test file's before/after SHA-256;
- all immutable starting/final hashes;
- every positive, false-positive, and falsification result required above;
- all verification commands with literal output summary, exit code, and
  pass/fail/skip counts;
- final `git diff --check`, `git diff --name-only`, and `git status --short`;
- confirmation that all non-allowlisted paths and the visual freeze remained
  byte-identical; and
- verdict `READY FOR STEP 3 RE-REVIEW` or `BLOCKED`.

Then stop. Do not accept or close Step 3, release or begin Step 4, close P3.G4,
deploy, contact a live service, use external network access, access secrets, or
access real data.

