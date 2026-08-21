# Gemini implementation prompt — P3.4 Step 7 identity and role administration

Date released: 2026-08-20

Status: **RELEASED — STEP 7 ONLY**

Implementer: Gemini

Independent reviewer: Codex

Acceptance authority: Peter Duscha

## Authorization and stop boundary

Peter accepted Step 6 and, in the same instruction, authorized and released
this Step 7 prompt under the recorded single-approval rule. No duplicate
approval is required. Implement only Step 7, report its checkpoint, and stop.
Do not begin Step 8. Do not stage, commit, push, deploy, access secrets or real
data, contact live/external services, or inspect/alter any stash.

## Read first

Read completely before editing:

1. `.agents/AGENTS.md` and `docs/implementation-plan.md`;
2. `docs/review/phase-3-p3-4-authorisation-and-conditions.md`;
3. the P3.4 master prompt, execution plan, baseline, and Step 6 acceptance;
4. `docs/contracts/phase-3-route-authorization-contract.md`, especially R-28
   through R-38, §2.3, §5.1, N-16, N-17 and N-67;
5. `docs/contracts/phase-3-view-model-contract.md`, especially VM-10 through
   VM-13 and the bounded collection rules;
6. the accepted identity-migration, field-profile, role-capability, account-
   identity and audit contracts and current production services/routes; and
7. the complete current Git status and diff. Preserve every existing change.

The backend, route inventory and view-model classes are accepted inputs, not a
Step 7 redesign surface. If an accepted record and implementation materially
conflict, stop and report the exact conflict instead of silently choosing one.

## Exact write allowlist

You may change only:

- `adapters/web/templates/identity_migration.html`;
- `adapters/web/templates/field_profile.html`;
- `adapters/web/templates/role_capabilities.html`;
- `adapters/web/templates/account_identities.html`;
- `adapters/web/templates/base.html`, only to replace the production CSS
  fingerprint after an authorized CSS change;
- the current `adapters/web/static/css/freedom-blades.<12-hex>.css`, replacing
  it with exactly one correctly fingerprinted successor;
- `adapters/web/static/asset-integrity.sha256`, only for that CSS replacement;
- new `tests/web/test_p3_4_identity_and_role_views.py`; and
- existing digest-owner tests only where their exact template/CSS/manifest
  digest assertions necessarily change:
  `test_p3_4_council_character_views.py`, `test_p3_4_member_views.py`,
  `test_p3_4_auth_and_system_views.py`, `test_p3_4_shell_and_components.py`,
  `test_p3_4_static_assets.py`, and `test_static_asset_surface.py`.

Do not edit Python production code, migrations, contracts, governance/review
records, shared includes, vendored HTMX, the emblem, or any Step 8+ template.

Verify these starting SHA-256 values before writing; stop on a mismatch:

| File | Required starting SHA-256 |
|---|---|
| `identity_migration.html` | `ededffd5adb842bd0a33bb6f3f098c0497d3d6935d5827ecac02727af849a878` |
| `field_profile.html` | `06a2b6a5e389b6c936f016df95069b82c26741dba5e402ae2c9ad0d306181e91` |
| `role_capabilities.html` | `bf1ce7d09096b8d41fcde29fc170bf43615d462a7e7015a13de89b3f3d4a0b3b` |
| `account_identities.html` | `f3ab67ec4f0eb9b10555fe5263b871b15c1d18bfd15dc2ae6bf0a8c39bf7f0d5` |
| `base.html` | `0455cb45deb77dada5a7758468ab6bac4f279002caea4a58c198145a349970fe` |
| current CSS | `fe0678db747dd3a56a7afd1b2a005e5da44b27e9c74d0f29ea56abcef9f2717a` |
| integrity manifest | `98827527722a2f8cf9be0f7cc1667929aa4019334335e8ca22b68701cde45598` |

The existing test digests are recorded in the Step 6 acceptance and baseline;
capture and report them before changing any allowed digest owner.

## Required implementation

Build accessible, server-rendered, progressively enhanced pages for VM-10 to
VM-13 and R-28 to R-38. Reuse the accepted shell/components and visual tokens.
All navigation, disclosures and forms must remain complete without JavaScript.
Use semantic headings, tables/lists, labels, captions, status text and focus
behavior; escape all Actor names, role labels, reasons, provider values,
subjects and other untrusted text. Never add inline script/style or inline
event handlers.

### VM-10 — identity migration (R-28 to R-30)

Render the run metadata, dry-run/profile/source evidence, bounded proposals,
cursor and all control totals. Assert and visibly represent balanced totals;
do not invent an apply or bulk-confirm operation. Names and `active_dm_flag`
are evidence only and never authority. Display candidate truncation/count,
fixed `resulting_access_kind = co_owner`, and the exact distinction among
outstanding, rejected, confirmed-and-active, and confirmed-and-revoked.

Render R-29 only when the proposal facts say it is confirmable and undecided.
Its standard POST form contains exactly `csrf_token`, `version` (from
`character_version`) and `reason`; it must not submit subject, access kind,
candidate, character or proposal identifiers as body authority. Render R-30
only for an undecided proposal and submit exactly `csrf_token` and `reason` —
no `version`. Reasons are required and bounded to the accepted 500-character
limit. C and CA may use this page; continuity actors and all other unauthorized
callers receive the existing refusal behavior. Mutations retain CSRF, Origin,
authorization, optimistic-concurrency and non-enumeration enforcement.

### VM-11 — field profile (R-31)

Render the profile version, all bounded path rows (`path`, `snapshot_mode`,
optional `reports_field`), all bounded field rows (`field_key`, `authority`,
optional `difference_direction`, optional `owning_package`), and the closed
unknown-path policy. This page is strictly read-only: no form or mutation-like
control. C, A and CA are allowed by the accepted route policy; continuity
sessions are refused.

### VM-12 — role capabilities (R-32 to R-34 and R-38)

Render the canonical guild ID, administrator scope, bounded mappings,
unratified count, scope/lockout notices, stable role snowflakes, presentation-
only role labels, capability, provenance, authentication method, creator/time,
ratifier/time and protected/revocable/ratifiable facts.

R-33 contains exactly `csrf_token`, `role_id`, `capability`, `reason`; the
capability choices must come only from `available_capabilities`. R-34 contains
exactly `csrf_token`, `version`, `reason` and appears only when `revocable`.
R-38 contains exactly `csrf_token`, `version`, `reason` and appears only when
`ratifiable`. Reasons use the accepted required 500-character bound. Never
offer revocation for the protected bootstrap mapping.

For `emergency_continuity`, make the restricted scope explicit: the only
available creation capability is the server-supplied N-67 allowlist value
(`platform_administrator`); no ratification control is available; and mapping
controls follow the server-supplied revocable/ratifiable facts. Do not infer
authority from labels or hidden fields. A, CA, BG and AC may reach R-32 under
their accepted scopes; R-38 remains unavailable to continuity sessions.

### VM-13 — account identities (R-35 to R-37)

Render the caller's account ID and bounded identity list with provider key/name,
full own subject, linked/last-authenticated times, active/retired state and
current-session fact. Historical retired identities remain visible but have no
unlink control. Explain `no_additional_provider` honestly.

R-36 is not an OAuth redirect for an authenticated caller: it returns `200`
HTML using VM-13 with `state = denied` and
`additional_provider = no_additional_provider`. The caller-matrix `U: 303`
continues to mean unauthenticated navigation to login. R-37 standard POST forms
contain exactly `csrf_token`; render them only for eligible active identities
when `unlink_blocked_reason` is absent. Never permit the browser to override
account, provider or subject. BG and AC may view R-35 but are refused for R-36
and R-37. Preserve the last-usable-identity and emergency-session safeguards.

## CSS and immutable assets

Add only the selectors needed by these four pages, within the accepted token
system, responsive breakpoints, reduced-motion and focus-visible rules. Do not
pre-build Step 8+ snapshot, job, audit or import UI. If CSS bytes change:

1. compute the full SHA-256;
2. name the sole CSS file with its first 12 lowercase hex characters;
3. update only the base reference and CSS entry in the integrity manifest; and
4. update only necessary digest assertions.

The HTMX file and emblem are immutable and must remain respectively:

- `71ea67185bfa8c98c39d31717c6fce5d852370fcdfd129db4543774d3145c0de`;
- `eab0d13128f55b7a367ce9e3ba88a2bad967e37768f7e28d9728186d9d322371`.

## Required tests

Create `tests/web/test_p3_4_identity_and_role_views.py`. Include direct-render
and structural tests that run without PostgreSQL, plus database-backed HTTP
tests when `TEST_DATABASE_URL` is configured. Cover at minimum:

- every ready/empty/denied state and collection bound for VM-10–VM-13;
- exact accepted form action/method/input-name sets for R-29, R-30, R-33,
  R-34, R-37 and R-38, including prohibited extra fields;
- conditional absence of confirm/reject/revoke/ratify/unlink controls;
- confirmed-active versus confirmed-revoked migration rendering and balanced
  totals, candidate truncation, fixed co-owner outcome and evidence-only names;
- the field-profile classifications and proof it contains no forms;
- protected bootstrap, full-admin and emergency-continuity presentations;
- R-36 authenticated `200 denied`, unauthenticated login redirect, and BG/AC
  refusal;
- route caller matrices for R-28–R-38, CSRF/Origin rejection, stale-version
  conflicts, safe 404 non-enumeration equivalence and zero mutation/audit side
  effects on refused requests;
- hostile HTML, Unicode and quote payload escaping in every relevant value;
- functional standard-POST/no-JavaScript navigation; and
- exact CSS selector use, fingerprint, manifest and immutable-asset checks.

Database tests must use only the disposable `TEST_DATABASE_URL`, resolve/open
database resources after fixture yield, track case-created identifiers, and
perform verified post-yield cleanup through a connection using the accepted
test-helper pattern. If the variable is absent, skip only database-dependent
cases with the standard reason. Never use `DATABASE_URL`, SQLite, a production
database or real records. A skip is not execution evidence.

Falsification tests must make each security/structure validator fail for its
intended reason when the protected property is locally mutated. Avoid weak
substring, test-name, variable-name or assertion-count checks; validate the
relevant AST/data flow and runtime outcome.

## Verification

Run and report:

```bash
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_identity_and_role_views.py
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_static_assets.py tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_auth_and_system_views.py tests/web/test_p3_4_member_views.py tests/web/test_p3_4_council_character_views.py tests/web/test_p3_4_identity_and_role_views.py tests/web/test_static_asset_surface.py
./venv-web/bin/python -m compileall -q adapters/web application/web tests/web
git diff --check
```

Also run the accepted visual-freeze and static-integrity manifest checks and
read-only diff/allowlist/hash checks. If `TEST_DATABASE_URL` exists, run the
database-backed focused and combined suites; otherwise report the permitted
skips explicitly. Do not install browser/dependency software or use network or
live services.

## Stop conditions and handoff

Stop `BLOCKED` without expanding scope if a starting digest differs, an
allowlisted file has overlapping user changes, a contract/code conflict cannot
be resolved within templates/tests/CSS, an immutable asset changes, a required
non-database check fails, or a required configured database check fails.

Report:

- files changed and before/after SHA-256;
- exact behavior delivered for VM-10–VM-13 and R-28–R-38;
- CSS fingerprint/manifest facts and immutable-asset hashes;
- every command, exit code, pass/skip/failure count and skip reason;
- database evidence actually run versus not run;
- falsification results, remaining risks and final Git status; and
- verdict `READY FOR INDEPENDENT STEP 7 REVIEW` or `BLOCKED`.

Then stop. Do not claim Step 7 acceptance, release Step 8, or begin Step 8.
