# Gemini prompt — P3.4 Step 7 remediation 04

Date: 2026-08-21  
Status: **RELEASED FOR GEMINI EXECUTION — STEP 7 REMAINS OPEN**  
Scope: one test file only; backend conflict must be reported, not bypassed  
Independent reviewer: Codex  
Acceptance authority: Peter Duscha

Copy this entire document into Gemini as one prompt.

---

You are Gemini, the Production Frontend Implementer for Phase 3 package P3.4.
Remediation 03 corrected several literal statuses and the last-identity caller,
but independent review found that its new caller-matrix validator is detached
from the HTTP evidence and therefore passes while required cells are absent or
duplicated. Review also found an accepted backend-contract conflict on the
durability of `identity.link_refused`. Correct only the test-evidence defect;
preserve the contract-revealing assertion and report the backend conflict as a
blocker rather than weakening it or editing backend code.

## Read before editing

Read completely:

1. `.agents/AGENTS.md` and `docs/implementation-plan.md`;
2. the Step 7 prompt and remediation 01–03 prompts;
3. `docs/contracts/phase-3-route-authorization-contract.md` §5.2 and §9.5;
4. `docs/contracts/phase-3-test-traceability.md`, especially TC-ID-07;
5. VM-10–VM-13 in the view-model contract;
6. `application/web/account_identities.py`, especially `unlink()`;
7. `adapters/web/portal_routes.py`, especially `unit()` and R-35–R-37;
8. role-mapping refusal persistence via `run_mapping_change()` as the accepted
   example of committing a refusal separately from a rolled-back mutation;
9. shared caller/database fixtures and the current complete diff.

## Sole allowed write and starting hash

Edit only:

`tests/web/test_p3_4_identity_and_role_views.py`

Verify its SHA-256 is exactly:

`c74e8d0cfc7cf258a3e4559a98c7e2f9e02f0b0fcbb025f3e8746cff8c0f8f7d`

If it differs, stop for overlap. Do not edit backend Python, templates, CSS,
assets, manifests, contracts, prompts, fixtures, migrations or other tests. Do
not stage, commit, push, stash, deploy, install, access real data/secrets or
contact live services. Preserve all accepted static/template hashes.

## Finding 1 — the route matrix is disconnected from executed HTTP cases

`ACCEPTED_ROUTE_CALLER_MATRIX` and `validate_route_caller_matrix()` validate
only a hand-written dictionary. The database test does not consume that table,
and the validator does not inspect the test's request/caller/status data flow.
It therefore passes despite these concrete omissions:

- R-35 executes C twice and never executes CA;
- R-36 executes M, U, BG and AC but omits N, C, A and CA;
- R-33 omits CA and AC authorized-success evidence and gives BG only a separate
  special case rather than binding all matrix outcomes to the table;
- R-34 omits CA/BG/AC authorized N-67 outcomes; and
- R-37 does not execute the accepted N/C/A/CA cells as isolated own-account
  operations.

Replace the disconnected proof with one shared, data-driven caller matrix that
the database HTTP test actually executes, or add a rigorous AST/data-flow
validator proving each table cell maps to a request using the named caller and
an assertion of the exact expected status. Prefer runtime parametrization or a
shared helper so the contract table is the single expectation source.

For mutation success cells, seed an isolated valid object/account per caller so
one cell cannot consume or stale the object needed by another. Supply valid
CSRF, Origin and form fields so authorization is what the cell proves. For
N-67, BG/AC must succeed only with `platform_administrator` and must separately
refuse a non-allowlisted capability with the accepted refused-event evidence.
For R-37, each authorized N/M/C/A/CA cell must target that caller's own eligible
identity; do not target M's identity with another caller.

For GET success cells, assert the correct VM state/scope and caller-specific
data isolation, not status alone. Remove duplicate C and execute CA for R-35.
Execute every R-36 success cell and prove its authenticated `200 denied` /
`no_additional_provider` presentation.

Add falsification probes that fail when:

- a runtime cell is removed while its dictionary entry remains;
- the request uses a different caller than the matrix key;
- the asserted status differs from the shared expectation; or
- duplicate execution of one caller is substituted for a missing caller.

A second disconnected dictionary or test-name/substring/count check is not
acceptable evidence.

## Finding 2 — preserve and surface the backend refusal-audit conflict

The accepted route contract says R-37 audits both `identity.link_refused` and
`identity.unlinked`. `AccountIdentityService.unlink()` records
`identity.link_refused` and then raises `UnlinkRefused`. The route runs it through
`unit()`, whose `engine.begin()` transaction rolls back on that exception. In
contrast, role-mapping refusals use `run_mapping_change()` to persist their
refusal event in a fresh transaction.

Therefore the corrected last-usable database test's expectation of exactly one
durable `identity.link_refused` is contract-correct but appears incompatible
with current backend transaction behavior. Do not change the expected count to
zero, remove the assertion, mock the audit writer, accept either value, or edit
backend code. Keep exact before/after identity state, zero applied
`identity.unlinked`, and exactly one case-specific `identity.link_refused`.

If disposable PostgreSQL confirms that the event count is zero, report:

`BLOCKED: backend R-37 refusal-audit transaction correction required`

Include the exact failing assertion and production path in the handoff. This is
a Claude/backend-contract-owner correction followed by security re-review, not
Gemini frontend authority. If PostgreSQL is unavailable, report the conflict as
an unexecuted but blocking reviewer finding; do not claim Step 7 ready merely
because the test skipped.

## Preserve other evidence

Keep canonical audit actions/entities, exact success event attribution,
non-enumeration headers/bodies, CSRF/Origin/stale/no-write snapshots, active CSS
and template-use validation, form exactness, escaping, digests, manifest checks
and post-yield cleanup. Remove trivial duplicates. Update structural validators
and negative probes for all changed matrix helpers.

Use only disposable `TEST_DATABASE_URL`; never `DATABASE_URL`, SQLite or real
records. Resolve database resources after fixture yield and retain verified
fresh-connection cleanup.

## Verification

Run and report exact commands/results:

```bash
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_identity_and_role_views.py
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_static_assets.py tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_auth_and_system_views.py tests/web/test_p3_4_member_views.py tests/web/test_p3_4_council_character_views.py tests/web/test_p3_4_identity_and_role_views.py tests/web/test_static_asset_surface.py
./venv-web/bin/python -m compileall -q adapters/web application/web tests/web
git diff --check
```

Also run all falsification, visual-freeze, integrity, digest and allowlist/hash
checks. If `TEST_DATABASE_URL` exists, focused and combined database execution
is mandatory. Otherwise report database evidence as not run.

## Handoff and stop

Report the sole file/hash change, route-by-route executed matrix, isolated
mutation fixtures, falsification results, database run/skip facts, the R-37
backend conflict, unchanged production hashes, commands/results, remaining
risks and Git status.

Use verdict:

- `READY FOR INDEPENDENT STEP 7 REMEDIATION 04 REVIEW` only if every required
  runtime test actually passes, including durable `identity.link_refused`; or
- `BLOCKED: backend R-37 refusal-audit transaction correction required` when
  the accepted event is not durable or cannot be proven due to the identified
  production conflict.

Then stop. Do not claim acceptance, release Step 8, begin Step 8, or modify the
backend.
