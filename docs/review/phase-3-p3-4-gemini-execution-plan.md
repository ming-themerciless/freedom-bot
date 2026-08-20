# P3.4 Gemini execution plan

Date: 2026-08-20 · Owner: Gemini · Backend contract owner: Claude · Review:
Codex · Acceptance: Peter

## 1. Authority and purpose

This plan sequences the released
`phase-3-p3-4-gemini-implementation-prompt.md` into small, independently
verifiable increments. The released prompt, accepted contracts, delivery plan
and repository working agreement remain authoritative. This plan changes none
of their scope, ownership, gates or prohibitions.

Gemini performs **one step per prompt and stops**. Passing a step authorizes no
later step. Peter or his designated coordinator releases the next prompt after
reviewing the checkpoint. A missing backend field, route, authority, invariant
or test fixture is a stop condition, never permission to improvise.

## 2. Rules for every step

1. Read the released master prompt and this plan completely before acting.
2. Read the step prompt and change only its allowlisted files.
3. Preserve all pre-existing changes and the pre-existing stash. Never read
   `.env`, credentials, secrets or real player/guild/Actor data.
4. Record `git status --short` and SHA-256 for every allowlisted existing file
   before editing. Use `absent` for an allowed new file.
5. Work from accepted route and view-model contracts. Do not change backend
   Python, routes, view models, middleware, persistence, migrations,
   dependencies, configuration or `design-prototype/`.
6. Add or update the focused tests in the same step as the production files.
7. Run the step's narrow checks. Run no live service, external network call,
   migration or dependency installation.
8. If a required check cannot run, report it accurately; do not substitute a
   weaker evidence class or silently continue.
9. End with the checkpoint report defined by the step, then stop.

Each checkpoint reports: files changed; before/after SHA-256; routes, view
models and states covered; commands and literal results; skips/not-run checks;
contract questions; residual risks; `git diff --check`; and `git status --short`.

## 3. Step sequence

### Step 1 — baseline and closed work map

Read-only inspection of production and reference material. Create only
`docs/review/phase-3-p3-4-gemini-baseline.md`. Record the dirty-tree baseline,
the 24-template inventory, the static-root inventory, template-to-route-to-view
model ownership, applicable page states, existing focused tests, prototype
reference mapping and all anticipated files by later step. Verify the visual
freeze and existing structural guards. Make no production or test edit.

**Gate:** the baseline is complete, contains no invented route/field/control,
and identifies every existing change that later work could overlap.

### Step 2 — static asset foundation

Add only the production stylesheet foundation, the vendored HTMX file, the
approved guild emblem copy/derivative allowed by the master prompt, asset
integrity metadata, and static-corpus structural tests. Do not edit templates.
Use M-01 `/static/`; do not change its backend implementation.

**Gate:** fingerprint/cache naming, vendored-file SHA-256, no remote origin,
no prototype reference and static security tests pass.

### Step 3 — shared shell and design system

Implement `base.html`, shared includes, semantic landmarks, skip link,
two-level navigation, CSS tokens/components, focus treatment, reduced motion
and responsive shell. Add shell/source tests. Do not convert page bodies yet.

**Gate:** shell renders with representative safe view data, remains useful
without JavaScript, and passes structural, escaping and responsive source checks.

### Step 4 — authentication and system-state pages

Implement `login.html`, `emergency.html`, `non_member.html`, `degraded.html`,
`denied.html`, `conflict.html`, `validation.html` and `error.html` for VM-01 to
VM-04 and VM-19 to VM-22. Preserve VM-22's minimal denial body and VM-02's
distinct recovery context.

**Gate:** ready/denied/stale/invalid/error responses and escaping tests pass;
denied/absent `404` bytes remain identical.

### Step 5 — ordinary member character pages

Implement `my_characters.html` and `character_detail.html` for VM-05 and VM-06,
including empty/truncated/missing-value/migration-deferred states and portrait
fallbacks. No character mutation control is permitted.

**Gate:** ordinary-member response, absence, bounds, escaping and no-control
tests pass.

### Step 6 — Council character access pages

Implement `council_characters.html`, `character_links.html` and
`identity_search.html` for VM-07 to VM-09 and R-22 to R-27, including the R-24
fragment. Controls render only from accepted pre-authorization facts and submit
the exact accepted fields.

**Gate:** navigation and fragment forms work without JavaScript; CSRF, version,
object-denial and direct-call tests pass.

### Step 7 — identity and role administration

Implement `identity_migration.html`, `field_profile.html`,
`role_capabilities.html` and `account_identities.html` for VM-10 to VM-13 and
R-28 to R-38. Preserve the one-provider R-36 denied behavior and synchronizer
CSRF tokens.

**Gate:** capability-specific controls, exact form fields, R-36, escaping,
continuity-session and no-JavaScript tests pass.

### Step 8 — snapshots and preview entry

Implement `council_snapshots.html` for VM-14 and R-40 to R-42, including folder
selection and preview creation only where pre-authorized.

**Gate:** empty/bounded/error states, exact form inputs, CSRF and authorization
tests pass.

### Step 9 — job status and HTMX polling

Implement `job_status.html` and `job_status_fragment.html` for VM-15 and R-43
to R-46. Poll only while the accepted state requires it. R-46 submits only
`preview_token` and `nonce`; server-owned checksum, folder and versions are not
browser authority.

**Gate:** full-page and fragment equivalence, polling stop rules,
confirm/cancel availability, no-JavaScript fallback and concurrency-facing form
tests pass.

### Step 10 — import result and audit

Implement `import_result.html`, `audit_search.html` and `audit_results.html` for
VM-17 and VM-18 and R-47 to R-49. Treat warnings as codes, respect bounds and
make the R-49 fragment meaningful by itself.

**Gate:** bounded search/results, fragment, escaping, authorization and
no-JavaScript tests pass.

### Step 11 — whole-corpus accessibility and responsive pass

Make only cross-page frontend corrections needed for semantic structure,
keyboard operation, visible focus, 320/768/1280 layouts, 200% reflow, reduced
motion and state consistency. Add or complete TC-UI-01 to TC-UI-06 where the
available evidence class permits.

**Gate:** automated source/browser checks pass where runnable; uninstalled
browser, real-device and screen-reader checks remain explicitly not run and are
not simulated.

### Step 12 — whole-corpus security and progressive-enhancement pass

Complete TC-SEC-05 and TC-SEC-08 to TC-SEC-11, hostile escaping cases, zero
`|safe`, zero `hx-on:`, zero inline executable script, zero remote origins,
zero prototype references, exact denial bodies, and no-JavaScript essential
flows. Remediate only frontend defects.

**Gate:** security/source/response checks pass and TC-STRUCT-01/02 prove no
route or view-model drift. Any backend finding stops and returns to its owner.

### Step 13 — complete verification and submission

Run the complete web and bot suites, visual freeze, compile checks and all
configured frontend checks. Create `docs/review/phase-3-p3-4-submission.md` with
the screen matrix, exact evidence, hashes, not-run checks, residual risks and
requests for independent Codex implementation and distinct security reviews.

**Gate:** handoff only. Gemini stops and does not close P3.G4 or begin P3.5.

## 4. Prompt control

The first released step prompt is
`phase-3-p3-4-gemini-step-01-baseline-prompt.md`. Later prompts must restate
their allowlist, tests, checkpoint and stop condition. A later prompt may refine
mechanics after learning from an accepted checkpoint, but may not combine steps
or widen the master prompt without a recorded decision.
