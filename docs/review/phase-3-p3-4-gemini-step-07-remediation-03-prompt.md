# Gemini prompt — P3.4 Step 7 remediation 03

Date: 2026-08-21  
Status: **RELEASED FOR GEMINI EXECUTION — STEP 7 REMAINS OPEN**  
Scope: one test file only  
Independent reviewer: Codex  
Acceptance authority: Peter Duscha

Copy this entire document into Gemini as one prompt.

---

You are Gemini, the Production Frontend Implementer for Phase 3 package P3.4.
Remediation 02 corrected the canonical audit vocabulary and expanded the HTTP
test, but independent review found multiple assertions that contradict the
accepted route matrix and at least one test case that uses the wrong caller and
therefore exercises a different refusal. These defects are hidden because the
single database-backed test is skipped when `TEST_DATABASE_URL` is absent.
Correct the one test file, verify it against disposable PostgreSQL if the
configured environment is available, report for independent re-review, and
stop.

## Governing records

Read completely before editing:

1. `.agents/AGENTS.md` and `docs/implementation-plan.md`, especially Phase 3;
2. `docs/review/phase-3-p3-4-gemini-implementation-prompt.md`;
3. the released Step 7 prompt and remediation 01/02 prompts;
4. `docs/contracts/phase-3-route-authorization-contract.md`, especially the
   exact R-28–R-38 matrix in §5.2 and its explanatory notes;
5. `docs/contracts/phase-3-view-model-contract.md`, VM-10–VM-13;
6. `application/web/account_identities.py`, `role_mappings.py` and
   `identity_evidence.py`;
7. `adapters/web/portal_routes.py`, the route guards and mutation-entry logic;
8. the shared caller/cleanup fixtures and accepted Step 4–6 HTTP test patterns;
   and
9. current Git status, complete diff and this finding.

Use the accepted route table literally. Navigation and form endpoints have
different unauthenticated behavior: protected navigation may redirect `303`,
but every R-29/R-30/R-33/R-34/R-37/R-38 mutation answers `401` for U.

## Starting integrity and sole allowed write

Edit only:

`tests/web/test_p3_4_identity_and_role_views.py`

Before editing, verify its SHA-256 is exactly:

`e6dfcff8d5940c8a381e1388f5727628d8f5ec55b014def3f0a82b51a063a94c`

If it differs, stop and report overlap. Do not edit templates, CSS, assets,
manifest, production Python, contracts, prompts, handover/baseline records,
fixtures, migrations or other tests. Do not stage, commit, push, stash, deploy,
install dependencies, access secrets/real data, contact live services, or
inspect/alter a stash.

All accepted template/static hashes from remediation 01 must remain unchanged.

## Blocking finding 1 — caller matrices contradict the accepted contract

Correct the database-backed caller evidence to match route-contract §5.2
exactly. Current known contradictions include:

- U is asserted as `303` for R-29, R-30, R-33, R-34, R-37 and R-38; every one
  must be `401` because each is a form mutation;
- R-31 incorrectly expects A to receive `403`; A is authorized and must receive
  the accepted `200` VM-11 response;
- R-32 incorrectly expects BG to receive `403`; BG is authorized on R-32 and
  must receive `200` with the correct emergency/full scope presentation; and
- the current matrices omit accepted success/refusal cells, including CA and
  the N-67-constrained BG/AC behavior. Exercise the cell's actual authorized
  request when the table says `✓ N-67`, not only a deliberately disallowed
  capability.

Audit every R-28–R-38 caller assertion against §5.2, including U/N/M/C/A/CA/BG
and the separately defined AC continuity state. Do not copy status expectations
from another route. For successful GET cells, assert the correct VM state/scope
and no cross-account disclosure rather than status alone. For mutation caller
cells, provide valid Origin, CSRF and form fields whenever authentication or
authorization—not input validation—is the property under test.

Add a non-database, data-driven route-matrix validator sourced from an explicit
accepted expectation table in this test file, plus negative probes that fail if
a mutation U cell becomes `303`, R-31 A becomes `403`, or R-32 BG becomes
`403`. This validator must inspect the actual database test calls/assertions or
drive shared data used by them; a disconnected duplicate table is not evidence.

## Blocking finding 2 — the last-usable-identity case exercises cross-account access

The current R-37 case targets `m_primary_id` but sends `n.cookies(settings)` and
an N-derived CSRF token. That identity belongs to M, so production applies the
ownership check first and returns the non-enumerating `404`; it cannot reach the
ordinary-member last-usable rule expected to return `409`.

Use M's session and M's valid CSRF token for M's sole remaining active identity.
Because M initially has an extra active identity, order or isolate the cases so
the account truly has exactly one usable identity at the moment of the request
without corrupting the later success case. Prove immediately before the request
that:

- the target identity belongs to the authenticated account and is active;
- that account has exactly one active usable identity;
- no reviewed recovery route applies; and
- the case-specific applied unlink audit count is at its expected baseline.

Then assert the exact `409`, unchanged identity/account state and the accepted
audit behavior. The contract explicitly names `identity.link_refused` and
`identity.unlinked`; distinguish an allowed/required refusal event from a
forbidden applied unlink event. Do not treat “all audit counts unchanged” as a
universal rule where the accepted service intentionally audits a refusal.

Keep a separate other-account request proving byte-identical absent/unreachable
`404`; do not use that case as last-usable evidence.

## Blocking finding 3 — successful administrative/account mutations still lack complete evidence

Remediation 02 required exact applied audit/event facts for all successes, but
the current explicit success checks cover R-29 and R-30 audit rows only. Add
complete post-success checks for R-33, R-34, R-38 and R-37:

- exact business row ID/state/provenance/version and redirect;
- exactly one corresponding `role_capability_mapping_events` row for role
  operations with correct operation/outcome/attribution;
- exactly one canonical audit row with the production action, entity type and
  exact generated entity ID; and
- no unrelated or duplicate applied event.

For R-33, capture the generated mapping ID from durable state and use it to
attribute both event and audit evidence. The current `snapshot_r33_state` audit
query counts every `role_capability.mapped` event globally and omits
`entity_id`; make the success/refusal evidence case-specific without pretending
an ID is known before creation. A before/after global control total may
supplement, but not replace, exact post-success attribution.

For refused role operations, distinguish `outcome='refused'` mapping events
that production intentionally records from forbidden applied mapping/audit
effects. Snapshot helpers must include every relevant applied and refused
channel required for that operation; equality expectations must reflect the
accepted transaction/refusal semantics rather than suppressing legitimate
auditability.

## Runtime and structural integrity

Keep the corrected canonical actions/entity types, selector/template parsing,
form exactness, adversarial escaping, template digests, manifest verification
and post-yield cleanup. Update the refusal-sequence AST validator and
falsification probes for all changed helpers/cases. Validators must prove SQL
predicates, bound parameter data flow, return tuples, request method/path/caller,
before/request/after order and exact expected status. Reject wrong callers as
well as wrong status codes.

Remove duplicate/trivial assertions such as the repeated R-28 status assertion.
Do not use broad status alternatives, literal tautologies, placeholder bodies,
or a monolithic test name as evidence.

Database work must use only disposable `TEST_DATABASE_URL`, resolve the engine
after fixture yield, use bound connections, track created IDs, and verify
cleanup through a fresh connection. If the variable is absent, skip only
database cases and explicitly report that runtime evidence was not obtained.

## Verification

Run and report exact commands, exit codes, pass/skip/failure counts and reasons:

```bash
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_identity_and_role_views.py
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_static_assets.py tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_auth_and_system_views.py tests/web/test_p3_4_member_views.py tests/web/test_p3_4_council_character_views.py tests/web/test_p3_4_identity_and_role_views.py tests/web/test_static_asset_surface.py
./venv-web/bin/python -m compileall -q adapters/web application/web tests/web
git diff --check
```

Also run visual-freeze, static-integrity, template-digest, allowlist/hash and
all falsification checks. If `TEST_DATABASE_URL` is configured, the focused and
combined database-backed suites are mandatory. If absent, report database
runtime as not executed; AST/source checks are not a substitute.

## Stop and handoff

Stop `BLOCKED` without expanding scope if the starting digest differs, overlap
exists, contract and production conflict, correction requires another file, an
immutable hash changes, a required non-database check fails, or a configured
database check fails.

Report:

- sole file changed and before/after SHA-256;
- exact corrected R-28–R-38 caller matrix;
- last-usable versus cross-account evidence;
- exact success/refusal event and audit attribution;
- database evidence run versus skipped;
- validators and negative probes;
- commands and exact results;
- unchanged production/template/static hashes;
- remaining risks and final Git status; and
- verdict `READY FOR INDEPENDENT STEP 7 REMEDIATION 03 REVIEW` or `BLOCKED`.

Then stop. Do not claim Step 7 acceptance, release Step 8, or begin Step 8.
