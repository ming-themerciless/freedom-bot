# Prompt for Gemini — P3.4 Step 5: ordinary-member character pages

Date: 2026-08-20 · Status: **RELEASED BY PETER / ACCEPTANCE AUTHORITY** · Step: 5 of 13

Peter/Acceptance Authority explicitly released this bounded Step 5 prompt on
2026-08-20 after accepting Step 4. Perform Step 5 only, deliver its checkpoint,
and stop. This release does not authorize Step 6 or any later step, P3.G4
closure, staging, deployment, production use, external/live-service contact,
secrets, real-player data, or creation/use of a database outside the existing
disposable-test rules.

You are Gemini, the P3.4 production frontend implementer. Perform Step 5 only,
deliver its checkpoint, and stop.

## Read completely before acting

1. `.agents/AGENTS.md` and `docs/implementation-plan.md`;
2. the corrected P3.4 master implementation prompt;
3. `docs/review/phase-3-p3-4-gemini-execution-plan.md`, especially Step 5;
4. the Step 1 baseline, Steps 2–4 acceptance records, every Step 4 review and
   remediation record, and the current handover note;
5. `docs/contracts/README.md` and all Phase 3 contracts in their prescribed
   order, especially route authorization R-20/R-21 and §2.3, view models VM-05
   and VM-06, threat model, data-migration register, and test traceability;
6. the production implementations of `CharacterPortrait`, `CharacterSummary`,
   `MyCharactersView`, `SnapshotField`, `MigrationDeferred`, `AccessFact`,
   `Provenance`, and `CharacterDetailView`;
7. the R-20/R-21 production handlers and existing database fixtures/tests;
8. the frozen prototype pages `my-characters.html` and
   `character-detail.html`, as reference only; and
9. the complete current diff and `git status --short`.

Verify all starting hashes and required absences before writing. Preserve all
unrelated dirty/untracked work and every stash exactly. Do not inspect, apply,
drop, or alter a stash.

## Objective

Convert only these two inherited page bodies to the accepted production visual
system while preserving their frozen route and view-model contracts:

- `my_characters.html` — VM-05 / R-20; and
- `character_detail.html` — VM-06 / R-21.

Implement the ready, empty, truncated, nullable-value, snapshot-absence,
migration-deferred, access, provenance, active/inactive, and portrait-fallback
states carried by the accepted view models. Both pages are read-only. Add no
character mutation control and make every navigation work without JavaScript.

## Starting hashes

Verify exactly:

| File | Required SHA-256 |
|---|---|
| `adapters/web/templates/my_characters.html` | `28eb6391c37e50383103ad05ef98d0fd3d6669117edb73251de570f0871ccf72` |
| `adapters/web/templates/character_detail.html` | `7be58ab1bb9436fda39801ff4a31e4c938301b1c335e0fe53e1411ca795c4cf4` |
| `adapters/web/templates/base.html` | `d095f37624d1ce37a9f92ecccde9b6a8d0d407aba55052bb79f1f6050fe1c79d` |
| `adapters/web/templates/includes/header.html` | `ede238e9d6f83c70eb228b54d58d40fa5b01d6df4c82ce8479c641dc28a46796` |
| `adapters/web/templates/includes/footer.html` | `2f1068b436a38a7ef79580aec4b55ed23dcaa5a3b827596509caa000ed72f7c3` |
| `adapters/web/static/css/freedom-blades.da727b328510.css` | `da727b32851014c26d2131bcab24be4cf660c8a3f83360acf3330281c2a0b1a9` |
| `adapters/web/static/asset-integrity.sha256` | `e04efc4f036f70e18b8096184174642ce4bbfdf727f446961d1876c6830822ae` |
| `tests/web/test_p3_4_auth_and_system_views.py` | `90553f30b516d64832fe813ed591ffd2aa028d07b92b60de5171882692758da6` |
| `tests/web/test_p3_4_shell_and_components.py` | `9b314c04b16ed96d1d010913bf8432fd9abca71fbf48921bd0066e38440e9b1d` |
| `tests/web/test_p3_4_static_assets.py` | `edcf0e3bb0ce8339f72f0522619656d16d1e76d5a798fb0f608826c1890e7217` |
| `tests/web/test_static_asset_surface.py` | `dfd7ff956ea8f61d6cbbb98f9273dc9627f34365a8ec1da3d544c389abaf9b19` |

`tests/web/test_p3_4_member_views.py` must be absent. The accepted HTMX and
emblem must retain these full digests:

- HTMX: `71ea67185bfa8c98c39d31717c6fce5d852370fcdfd129db4543774d3145c0de`;
- emblem: `eab0d13128f55b7a367ce9e3ba88a2bad967e37768f7e28d9728186d9d322371`.

Stop and report any mismatch, unexpected presence, or overlapping edit. Do not
normalize it or silently adopt it.

## Exact write allowlist

Only these paths may change:

- `adapters/web/templates/my_characters.html`;
- `adapters/web/templates/character_detail.html`;
- `adapters/web/templates/base.html`, solely to replace the exact CSS filename;
- removal of
  `adapters/web/static/css/freedom-blades.da727b328510.css`;
- one replacement
  `adapters/web/static/css/freedom-blades.<12-lowercase-hex>.css`, whose filename
  fingerprint equals the first 12 lowercase hex characters of its full content
  SHA-256;
- `adapters/web/static/asset-integrity.sha256`, solely for that CSS replacement;
- `tests/web/test_p3_4_shell_and_components.py`, solely to transition the two
  authorized template digests, retain exact digest protection for all other
  templates, and permit/test only Step 5 CSS scope;
- `tests/web/test_p3_4_static_assets.py`, only for the exact CSS filename/digest
  or a Step-4-only selector-scope assertion made obsolete by Step 5;
- `tests/web/test_static_asset_surface.py`, only for the exact CSS filename;
  and
- new `tests/web/test_p3_4_member_views.py`.

Do not create an include. All other templates—including all eight accepted
Step 4 pages—header, footer, HTMX, emblem, backend Python, handlers, view models,
contracts, dependencies, configuration, operations/project-management/review
records, prompts, and `design-prototype/` must remain byte-identical.

## Shared rules

- Retain `{% extends "base.html" %}`, one page-owned `<h1>`, meaningful heading
  order, semantic regions, visible focus, and ordinary same-origin navigation.
- Render only accepted VM-05/VM-06 fields. Never infer authority, identity,
  game facts, missing values, timestamps, URLs, or actions.
- Preserve Jinja autoescaping. Use no `|safe`, `Markup`, inline event handler,
  `hx-on:`, inline executable script, remote origin/font, dynamic include, or
  production reference to `design-prototype/`.
- These pages require no HTMX behavior. Essential content and navigation must
  work without JavaScript.
- Render zero `<form>`, editable control, mutation link/button, CSRF token,
  version input, or invented POST action. `version` is display-only if shown.
- Keep all VM bounds layout-safe without hiding authoritative facts: VM-05 has
  at most 50 characters; VM-06 has at most 200 snapshot fields, 200 deferred
  fields, and 25 access facts.
- Make no browser, WCAG-conformance, real-device, assistive-technology,
  database-execution, staging, deployment, or production-readiness claim unless
  that evidence was actually run in the authorized environment.

## `my_characters.html` — VM-05 / R-20

- Render both `ready` and `empty` as first-class states.
- The empty state says Guild Council manages character links and offers no
  self-service action.
- Render stable ordinary anchors using only each accepted `detail_path`; do not
  construct a route from `character_id` in the template.
- Render each bounded character summary: escaped display name, active/inactive,
  access kind, default status, portrait fallback, level, and optional last
  snapshot facts.
- `level is None` must render `not recorded`, never `0`, blank, unknown numeric
  text, or a fabricated level.
- `CharacterPortrait` contains only `state`, `initials`, and
  `accessible_label`. It supplies an accessible initials fallback; there is no
  image URL and no request for a remote/local portrait file.
- Make default status understandable without relying on color alone.
- If `truncated` is true, state that only the bounded first results are shown;
  do not invent pagination or a search/filter control.
- Display `SnapshotStamp` only when present and only from its accepted bounded
  fields. Its short checksum is display-only.

## `character_detail.html` — VM-06 / R-21

- Render escaped display name and optional long name, nullable level,
  active/inactive status, accessible portrait fallback, and the viewer's access
  kind. `viewer_access_kind is None` means Council-by-role, not “no access.”
- Separate snapshot/database-authoritative fields, migration-deferred fields,
  access facts, and provenance into understandable semantic sections.
- For `SnapshotField.value is None`, render an explicit unavailable state from
  the closed `unavailable_reason`; never render zero, blank, or an old value.
- Render `authority` as a controlled classification, not as permission to edit.
- Every `MigrationDeferred` renders `migration deferred` and its controlled
  `owning_package`. It carries no value and must have no control of any kind.
- Access facts are read-only reachability facts. Render only accepted bounded
  member-facing fields; do not expose the Council-only
  `discord_subject_display`, hidden authority, or mutation affordances.
- Render mapped and absent snapshot provenance distinctly, using only accepted
  `Provenance`/`SnapshotStamp` fields. Do not turn external identifiers,
  checksums, profile versions, or optimistic version into browser authority.
- Do not weaken R-21 object non-enumeration: inaccessible, absent, and malformed
  identifiers remain governed by the accepted byte-identical `404` contract.

## CSS requirements

- Preserve every accepted Step 2 foundation and Step 3/4 shell/auth/system
  selector and behavior.
- Add only selectors actually used by these two pages: bounded character card
  layout, accessible initials portrait fallback, status/default/access badges,
  character-profile header, read-only fact grids/tables, unavailable/deferred
  facts, and provenance/access sections.
- Use accepted tokens and system fonts, visible focus, reduced motion,
  reflow-safe sizing, and local horizontal overflow for wide data only. Do not
  hide an authoritative field at narrow widths.
- Do not add Council mutation, identity administration, snapshot workflow,
  job/polling, import/audit, dialog/modal, or later-step selectors.
- Rename the CSS by its new content fingerprint, update `base.html` and the
  integrity manifest atomically, and remove the superseded CSS file.

## Tests

Create `tests/web/test_p3_4_member_views.py` and use production templates and
shared production-validation helpers for positive and corresponding negative
cases. Prove at least:

1. strict Jinja rendering of both actual templates with representative
   synthetic VM-shaped values and every applicable branch;
2. VM-05 ready, empty and truncated states, stable `detail_path` navigation,
   accessible portrait initials, default/access/active facts, and optional
   snapshot facts;
3. `level=None` renders exactly as not recorded on both pages and cannot be
   mistaken for numeric zero (TC-VM-05);
4. both templates contain zero forms, editable controls, mutation actions,
   hidden inputs, or invented POST routes;
5. VM-06 renders present and absent snapshot fields distinctly, including both
   closed unavailable reasons and both authority classifications;
6. every deferred field renders its owning package, no value, and no control
   (TC-VM-03);
7. mapped/unmapped provenance, optional long name, active/inactive state,
   viewer access kind including Council-by-role, and bounded access facts;
8. portrait markup has an accessible name/fallback and no image URL or network
   request;
9. exact bounds are enforced or proven from the frozen view-model constructors:
   VM-05 ≤ 50; VM-06 snapshot/deferred ≤ 200 each and access ≤ 25;
10. adversarial strings render inert and bounded where the two view models
    accept user-influenced display text;
11. R-20 ordinary-member HTTP ready/empty behavior and R-21 authorized detail,
    absent/inaccessible/malformed byte-identical `404` behavior, using existing
    application/database fixtures when a disposable `TEST_DATABASE_URL` is
    already configured;
12. all non-Step-5 templates retain their accepted exact digests, and the two
    transitioned templates receive exact new digest protection;
13. CSS selector scope, selector use, content fingerprint, integrity manifest,
    M-01 cache behavior, and unchanged HTMX/emblem bytes; and
14. falsifications through the same helpers used by positive production checks,
    including at least: `None` rendered as `0`, an invented mutation form, a
    deferred value/control, a portrait URL, a hidden authoritative field, an
    unused or later-step CSS selector, and changed CSS bytes without matching
    fingerprint/manifest updates.

Structural/direct-render tests must run without a database. Database-backed
HTTP tests may skip only when `TEST_DATABASE_URL` is absent, must say so
accurately, and must use existing safe disposable-database guards and
post-yield cleanup. Do not provision a database, read `.env`, or point tests at
staging/production. A skip is not PostgreSQL execution evidence.

## Required verification

Run and report literal commands, exit codes, pass/skip counts, and failures:

```bash
sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256
sha256sum -c adapters/web/static/asset-integrity.sha256
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_member_views.py
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_member_views.py tests/web/test_p3_4_auth_and_system_views.py tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py tests/web/test_structural_guards.py -m "not database"
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_member_views.py tests/web/test_p3_4_auth_and_system_views.py tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py tests/web/test_structural_guards.py
./venv-web/bin/python -m compileall -q tests/web/test_p3_4_member_views.py tests/web/test_p3_4_auth_and_system_views.py tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py
git diff --check
git status --short
```

Also report exact before/after SHA-256 for every changed/created/removed file,
prove every non-allowlisted production/test file remained at its starting
digest, and classify every check as source, response/HTTP, PostgreSQL, browser,
or supervised evidence. Report anything not run and why.

## Stop conditions and handoff

Stop immediately on a contract/backend mismatch, missing view-model field,
required backend edit, starting-hash mismatch, overlapping edit, unsafe database
configuration, inability to preserve object non-enumeration, or need to cross
the allowlist. Return the issue to Peter; do not approximate or expand scope.

At completion, report the change map, final hashes, state/branch coverage,
falsification/restoration evidence, literal verification results, database
tests run or skipped, residual risks, and the disposition:

`READY FOR INDEPENDENT STEP 5 REVIEW`

Then stop. Do not begin Step 6 and do not describe Step 5 as accepted.
