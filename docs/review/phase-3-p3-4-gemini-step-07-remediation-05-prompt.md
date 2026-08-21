# Gemini prompt — P3.4 Step 7 remediation 05

Date: 2026-08-21  
Status: **RELEASED FOR GEMINI EXECUTION — STEP 7 REMAINS BACKEND-BLOCKED**  
Scope: one test file only  
Independent reviewer: Codex  
Acceptance authority: Peter Duscha

Copy this entire document into Gemini as one prompt.

---

You are Gemini, the Production Frontend Implementer for Phase 3 package P3.4.
Remediation 04 substantially completed the executed R-28–R-38 caller matrix and
correctly preserved the contract-revealing R-37 refusal-audit assertion.
Independent re-review found one remaining Gemini-owned structural defect: the
matrix validator does not verify the caller for assigned U cells. Correct this
single validator weakness, remove one duplicate snapshot assignment, verify the
one-file change, report the still-open backend blocker, and stop.

## Read before editing

Read completely:

1. `.agents/AGENTS.md` and `docs/implementation-plan.md`;
2. the Step 7 prompt and remediation 01–04 prompts;
3. route-contract §5.2 and the R-37 audit prose;
4. the current complete `tests/web/test_p3_4_identity_and_role_views.py`;
5. `AccountIdentityService.unlink()`, `portal_routes.unit()` and
   `run_mapping_change()` for the already-recorded backend conflict; and
6. current Git status and complete diff.

## Sole allowed write and starting hash

Edit only:

`tests/web/test_p3_4_identity_and_role_views.py`

Verify its SHA-256 is exactly:

`08887310a86625ba47a34c13ba61d862b3d418596acb194f377c4f126f1f6bed`

If it differs, stop for overlap. Do not edit backend Python, templates, CSS,
assets, manifests, contracts, prompts, fixtures, migrations or other tests. Do
not stage, commit, push, stash, deploy, install, access real data/secrets or
contact live services. Preserve all accepted production hashes.

## Finding — U caller attribution is not validated

In `validate_matrix_execution_in_db_test()`, assigned response variables such
as `res_rNN_u` enter this branch:

```python
if caller_tag == "U":
    pass
```

That means a response named for U can pass `m.cookies(settings)`, another
authenticated caller's cookies, a literal session cookie, or another
credential-bearing expression and still be counted as the U cell. This violates
remediation 04's requirement that the validator prove the request uses the
caller named by the matrix key.

For every assigned and inline U cell, require exactly one accepted unauthenticated
shape:

- the `cookies` keyword is omitted; or
- it is exactly `u.cookies(settings)`, where the seeded U caller returns the
  empty cookie mapping.

Reject every other cookies expression, including M/CA/BG/AC callers, a literal
non-empty dictionary, a variable of unknown provenance, or an arbitrary helper.
Also ensure the request has no direct `Cookie` header that would re-authenticate
it. Validate AST/data flow rather than variable names or source substrings.

Add falsification probes proving rejection when:

1. an assigned `res_r*_u` request is changed to `m.cookies(settings)`;
2. an inline U matrix request is changed to `ca.cookies(settings)`;
3. U receives a literal non-empty cookie dictionary; and
4. U keeps empty/omitted cookies but gains a direct `Cookie` request header.

Keep the existing CA wrong-caller, missing-cell, duplicate-cell and status
mismatch probes. The positive validator must continue proving every route and
caller cell in the actual database test.

Remove the duplicated consecutive assignment of
`r38_no_csrf_snap_after` in the R-38 after-snapshot block. Preserve its single
snapshot call and immediate equality assertion. Do not make any other cleanup
or redesign.

## Backend blocker must remain visible

Do not weaken, delete, skip specially, mock or broaden the exact
`identity.link_refused == 1` assertion. The accepted contract requires that
durable refusal audit, while current backend transaction structure appears to
roll it back. This remains outside Gemini's authority.

If disposable PostgreSQL confirms zero durable refusal events, the verdict is:

`BLOCKED: backend R-37 refusal-audit transaction correction required`

If PostgreSQL is unavailable, report this runtime evidence as not executed and
retain the same unresolved backend blocker. Do not claim Step 7 acceptance.

## Verification

Run and report exact commands, exit codes, counts and skip reasons:

```bash
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_identity_and_role_views.py
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_static_assets.py tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_auth_and_system_views.py tests/web/test_p3_4_member_views.py tests/web/test_p3_4_council_character_views.py tests/web/test_p3_4_identity_and_role_views.py tests/web/test_static_asset_surface.py
./venv-web/bin/python -m compileall -q adapters/web application/web tests/web
git diff --check
```

Also run the matrix falsification group, visual/static integrity, template
digests and allowlist/hash checks. With configured `TEST_DATABASE_URL`, focused
and combined database execution is mandatory; otherwise report it as not run.

## Handoff and stop

Report the sole file and before/after hash, exact U-cookie semantics validated,
all four new negative probes, removal of the duplicate call, commands/results,
database run/skip facts, unchanged production hashes, Git status and the R-37
backend blocker.

Verdict must be either:

- `READY FOR INDEPENDENT STEP 7 REMEDIATION 05 REVIEW — BACKEND R-37 BLOCKER REMAINS`; or
- `BLOCKED: backend R-37 refusal-audit transaction correction required` if
  confirmed by PostgreSQL.

Then stop. Do not edit backend code, claim Step 7 acceptance, release Step 8 or
begin Step 8.
