# Gemini prompt — P3.4 Step 7 remediation 02

Date: 2026-08-20  
Status: **RELEASED FOR GEMINI EXECUTION — STEP 7 REMAINS OPEN**  
Scope: one test file only  
Independent reviewer: Codex  
Acceptance authority: Peter Duscha

Copy this entire document into Gemini as one prompt.

---

You are Gemini, the Production Frontend Implementer for Phase 3 package P3.4.
Remediation 01 removed the empty database test and substantially improved the
non-database validators. Independent re-review found that the new database
evidence still gives false assurance: every refusal snapshot filters for audit
facts that production does not write, so the audit count remains zero even if a
forbidden real audit event is emitted. The database test also implements only a
subset of the HTTP/security/no-write matrix explicitly required by remediation
01. Correct these defects in the single allowed test file, verify the result,
report it for independent re-review, and stop.

## Governing records

Read completely before editing:

1. `.agents/AGENTS.md` and `docs/implementation-plan.md`, especially Phase 3;
2. `docs/review/phase-3-p3-4-gemini-implementation-prompt.md`;
3. `docs/review/phase-3-p3-4-gemini-step-07-identity-and-role-administration-prompt.md`;
4. `docs/review/phase-3-p3-4-gemini-step-07-remediation-prompt.md`;
5. `docs/contracts/phase-3-route-authorization-contract.md`, especially
   R-28–R-38 and the accepted denial/non-enumeration semantics;
6. `docs/contracts/phase-3-view-model-contract.md`, especially VM-10–VM-13;
7. `application/web/identity_evidence.py`, `application/web/role_mappings.py`
   and `application/web/account_identities.py`, including their `_event`
   constructors and exact applied/refused actions;
8. the relevant route handlers, repositories, tables, shared web fixtures and
   accepted Step 4–6 database/HTTP test patterns; and
9. current `git status`, the complete diff and this review finding.

Accepted contracts and executable production behavior are authoritative. Do
not invent audit vocabulary, entity attribution, statuses, headers or caller
semantics in the test.

## Starting integrity and sole allowed write

Edit only:

`tests/web/test_p3_4_identity_and_role_views.py`

Before editing, verify its SHA-256 is exactly:

`8cc82a6c84f8b391a81701df9c5fc250bf6b5603f07a2fff8d4bdb665b71af2b`

If it differs, stop and report the overlap. Do not edit templates, CSS, static
assets, manifests, backend Python, contracts, earlier prompts, handover or
baseline records, migrations, fixtures or any other test. Do not stage, commit,
push, stash, deploy, install dependencies, access secrets/real data, contact
live services, or inspect or alter any stash.

The accepted Step 7 template, stylesheet and manifest hashes recorded in
remediation 01 must remain unchanged.

## Blocking finding 1 — refusal audit snapshots select impossible facts

Correct every snapshot helper and its structural validator/falsification probes
to select the exact audit action, singular entity type and entity ID produced by
the corresponding production `_event` constructor:

- R-29 confirm: action `identity_migration.confirmed`, entity type
  `identity_link_proposal`, entity ID = proposal ID;
- R-30 reject: action `identity_migration.rejected`, entity type
  `identity_link_proposal`, entity ID = proposal ID;
- R-34 revoke: action `role_capability.revoked`, entity type
  `role_capability_mapping`, entity ID = mapping ID;
- R-38 ratify: action `role_capability.ratified`, entity type
  `role_capability_mapping`, entity ID = mapping ID; and
- R-37 unlink: action `identity.unlinked`, entity type `external_identity`,
  entity ID = identity ID.

The current wrong filters—plural `identity_link_proposals`,
`role_capability_mapping.revoked`, `role_capability_mapping.ratified`, and
`account_identity.unlinked`—must not remain. Each snapshot must require all
three dimensions (`action`, `entity_type`, `entity_id`) and return the actual
case-specific count alongside all relevant mutable row state.

Add or correct negative probes so the structural validator rejects a wrong
action, wrong entity type, wrong entity-ID parameter/argument, omitted predicate,
or a return tuple that drops the audit result. Do not validate mere substrings:
prove the SQL literal, bound parameter data flow, returned value and before/
request/after call sequence.

For successful R-29, R-30, R-33, R-34, R-37 and R-38 requests, assert the exact
applied audit event and relevant durable event row where the accepted design
requires both. A mutation status/redirect and changed business row alone are
not complete audit evidence.

## Blocking finding 2 — remediation 01's required HTTP/no-write matrix remains incomplete

Complete the database-backed R-28–R-38 evidence rather than describing it in
the module docstring. Preserve existing correct cases and add the missing
contract-derived cases, including:

- exact GET caller matrices for R-28, R-31, R-32, R-35 and R-36 across every
  applicable U/N/M/C/A/CA/BG/AC state, including response state where a status
  alone is insufficient;
- direct POST caller matrices for R-29, R-30, R-33, R-34, R-37 and R-38, not
  only one representative unauthorized caller;
- separate missing/invalid CSRF and missing/invalid Origin refusals for every
  mutation family;
- R-33 refusal snapshots covering role mappings, capability-mapping events and
  audit events, including the AC non-allowlisted capability refusal;
- immediate complete before/after snapshots for every unauthorized,
  CSRF/Origin, stale, protected, unavailable, cross-account/object and other
  refused mutation, including the existing R-38 AC refusal;
- safe absent versus unreachable object 404 equivalence using the accepted
  exact status/body/header policy for each object-bearing family where the
  route contract requires non-enumeration. A malformed UUID is not a substitute
  for an existing-but-unreachable object unless the contract explicitly says
  so;
- direct refusal and zero side effects for already-decided/non-confirmable
  proposals, protected/non-revocable mappings, non-ratifiable mappings,
  another account's identity, retired identity, last usable identity and
  emergency-session unlink;
- ready and empty VM-10–VM-13 HTTP presentations, collection bounds/cursor
  behavior, balanced totals and confirmed-active versus confirmed-revoked
  rendering backed by database rows;
- exact success results: business-row state/version, fixed `co_owner`, no link
  on rejection, mapping provenance/activity/version, identity retirement,
  redirect and exact audit/event effects; and
- proof that the R-31 field-profile surface has no mutation route without
  accepting an ambiguous `404 or 405` assertion where the accepted route table
  specifies one exact result.

Use focused helpers/tests or a clearly data-driven matrix so failures identify
the violated contract. Do not rely on a single monolithic test name as proof.
No placeholder, unconditional assertion (such as comparing a string literal to
`""`), broad status alternative, or skipped database case may be reported as
execution evidence.

Database tests must use only disposable `TEST_DATABASE_URL`. Keep database
resolution after fixture yield. Track every case-created identifier required to
prove cleanup, pass bound connections to cleanup helpers, and verify absence
using a fresh post-cleanup connection. If the variable is absent, skip only the
database-dependent cases with the standard reason and report them as not run.
Never use `DATABASE_URL`, SQLite, production data or real records.

## Scope preservation

Keep the corrected active-selector/template-use parsing, exact form
multiplicity/method/action checks, adversarial escaping checks, immutable
template digests, asset manifest verification and post-yield cleanup controls.
Do not weaken non-database evidence to make the focused suite pass. Every
security/structure validator must retain a meaningful falsification probe for
the exact property it claims.

## Verification

Run and report exact commands, exit codes, pass/skip/failure counts and skip
reasons:

```bash
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_identity_and_role_views.py
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_static_assets.py tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_auth_and_system_views.py tests/web/test_p3_4_member_views.py tests/web/test_p3_4_council_character_views.py tests/web/test_p3_4_identity_and_role_views.py tests/web/test_static_asset_surface.py
./venv-web/bin/python -m compileall -q adapters/web application/web tests/web
git diff --check
```

Also run the accepted visual-freeze, static-integrity manifest, template digest,
read-only allowlist/hash and all falsification checks. If
`TEST_DATABASE_URL` is configured, the focused and combined database-backed
suites are mandatory. If it is absent, explicitly report the database cases as
not executed; source/AST checks and collection do not replace runtime evidence.

## Stop conditions and handoff

Stop `BLOCKED` without expanding scope if the starting digest differs, the
single allowed file has overlapping user changes, an accepted contract and
production behavior conflict, the correction cannot be made in this test file,
an immutable production/template/static hash changes, a required non-database
check fails, or a configured database check fails.

Report:

- the sole file changed and its before/after SHA-256;
- the corrected action/entity/entity-ID facts for every snapshot helper;
- a route-by-route R-28–R-38 caller/security/success/refusal evidence table;
- exact applied and refused audit/event facts asserted;
- database cases actually executed versus skipped;
- structural validators and their negative probes;
- all commands with exact results;
- unchanged production/template/static hashes;
- remaining risks and final `git status --short`; and
- verdict `READY FOR INDEPENDENT STEP 7 REMEDIATION 02 REVIEW` or `BLOCKED`.

Then stop. Do not claim Step 7 acceptance, release Step 8, or begin Step 8.
