# Gemini prompt — P3.4 Step 7 remediation 01

Date: 2026-08-20  
Status: **RELEASED FOR GEMINI EXECUTION — STEP 7 REMAINS OPEN**  
Scope: one test file only  
Independent reviewer: Codex  
Acceptance authority: Peter Duscha

Copy this entire document into Gemini as one prompt.

---

You are Gemini, the Production Frontend Implementer for Phase 3 package P3.4.
Your first Step 7 implementation is not ready for acceptance because its test
file claims database-backed HTTP/security/mutation coverage for R-28–R-38 but
contains only one skipped test whose executable body is `pass`. Several
non-database validators also do not meet the released prompt's falsification
standard. Correct the evidence in the single allowed file, verify it, report
the result for independent Codex re-review, and stop.

## Governing records

Read completely before editing:

1. `.agents/AGENTS.md` and `docs/implementation-plan.md`, especially Phase 3;
2. `docs/review/phase-3-p3-4-gemini-implementation-prompt.md`;
3. `docs/review/phase-3-p3-4-gemini-step-07-identity-and-role-administration-prompt.md`;
4. `docs/review/phase-3-p3-4-gemini-baseline.md`;
5. `docs/contracts/phase-3-route-authorization-contract.md`, especially
   R-28–R-38 and the accepted denial/non-enumeration semantics;
6. `docs/contracts/phase-3-view-model-contract.md`, especially VM-10–VM-13;
7. `docs/contracts/phase-3-test-traceability.md` and the relevant security,
   state-machine and operational contracts;
8. the existing P3.3 and accepted P3.4 Step 4–6 HTTP/database test patterns and
   shared fixtures; and
9. current `git status`, the complete diff and this review finding.

Do not infer behavior from this prompt where an accepted contract is more
specific. Preserve the accepted backend and frontend contracts.

## Starting integrity and sole allowed write

Edit only:

`tests/web/test_p3_4_identity_and_role_views.py`

Before editing, verify its SHA-256 is exactly:

`0f87ee99a6d861f374a81a8274f845eee6bf2a96b9d3ced46940aa43d9708502`

If it differs, stop and report the overlap. Do not edit templates, CSS, static
assets, manifests, backend Python, contracts, prior prompts, baseline/handover
records, migrations or any other test. Do not stage, commit, push, stash,
deploy, install dependencies, access secrets/real data, contact live services,
or inspect or alter any stash.

The current production-template hashes must remain unchanged:

- `account_identities.html`:
  `5f458b6fe335d34b7ba400d4f7c4c0dcbcceadabd613bfbd5c25890af37f1287`
- `field_profile.html`:
  `06277334db018cd82e313af0556a35e658c86841e06602a7bd65d0edde15f703`
- `identity_migration.html`:
  `66f3669661c40f2a73d250122c35e0f8af397d6f8bd94a4571402e7a8a63134b`
- `role_capabilities.html`:
  `e297c26dc326a2a28c9439948fcd781c29b12d3cda74911d9f747727d760613a`
- fingerprinted stylesheet:
  `b0a1f3305683c740c73ad5c68cb7e4ea767175a2823c8f7afc31676c21fd3773`
- `asset-integrity.sha256`:
  `5b663d9e27d0c87d937eb8ad25b98831972ea156450ee7ecb383de645d3493da`

## Blocking finding 1 — the advertised HTTP/database evidence is absent

The module docstring says it provides database-backed HTTP/security/mutation
evidence across R-28–R-38. In reality,
`test_db_identity_migration_http_routes` is the only database-selected test and
its entire body is `pass`. Without `TEST_DATABASE_URL` this is hidden by a skip;
with the variable configured it would report a false pass without sending a
request or making an assertion.

Replace the placeholder with executable, contract-derived coverage for the
complete Step 7 route surface R-28–R-38. Use the accepted shared fixture and
client patterns. At minimum, prove through real HTTP requests and database
state/audit observations, wherever applicable:

- the exact caller matrices, including unauthenticated redirect behavior,
  non-member/ordinary/Council/full-administrator/emergency-continuity cases,
  and R-36's authenticated `200 denied` versus its unauthenticated redirect;
- GET ready/empty/denied presentations and bounded collection behavior for
  VM-10–VM-13;
- successful R-29, R-30, R-33, R-34, R-37 and R-38 standard form POSTs, their
  exact accepted fields, resulting redirects/responses, mutations, versions and
  case-specific audit effects;
- CSRF and Origin refusal for each mutation family;
- stale-version conflicts for versioned mutations;
- conditional absence and direct-HTTP refusal of confirm, reject, revoke,
  ratify and unlink actions when the accepted state makes them unavailable;
- safe 404 absent/unreachable non-enumeration equivalence under the accepted
  status/body/header policy;
- immediate before/after database snapshots proving refused requests change
  neither the relevant rows nor audit events;
- confirmed-active versus confirmed-revoked migration behavior, balanced
  totals, fixed `co_owner` outcome and evidence-only names;
- field-profile read-only behavior and the absence of any mutation endpoint;
- protected bootstrap and emergency-continuity restrictions; and
- unlink blocking for `last_usable_identity` and `emergency_session`.

Split this into focused tests/helpers when that makes failures attributable.
Do not retain any `pass`, empty placeholder, unconditional success, or test that
only proves a mock was called. Make the module docstring describe only evidence
the file actually executes.

Database tests must use only disposable `TEST_DATABASE_URL`. Resolve/open the
database resource after fixture yield, pass bound connections to cleanup
helpers, track every case-created identifier, and prove those identifiers are
absent using a fresh post-cleanup connection. If the variable is absent, skip
only the database-dependent cases with the standard explicit reason. Never use
`DATABASE_URL`, SQLite, production data or real records. A skip is not execution
evidence and must be reported as such.

## Blocking finding 2 — structural validators are weaker than their claims

Strengthen the non-database evidence in the same file:

1. The Step 7 selector test currently checks raw substring presence in CSS and
   never proves selectors are active CSS rules or that the corresponding class
   tokens are used by an allowed Step 7 template. Parse/normalize active CSS
   rules while excluding comments, validate exact class-token use in the
   intended template corpus, preserve the Step 8+ prohibition, and add negative
   probes that fail when a required selector exists only in a comment, is absent
   from templates, or a prohibited selector is introduced.
2. The form validators reduce input names to sets. They therefore ignore
   duplicate fields and do not prove exact method/action semantics. Validate
   each rendered R-29/R-30/R-33/R-34/R-37/R-38 form as an individual form:
   exact action, case-insensitive POST method, exact name multiplicity, accepted
   control type, and no extra browser-authoritative field. Add negative probes
   for a duplicate accepted name, extra field, wrong method and wrong action.
3. The hostile-input test merely asserts that the literal `<script>` substring
   is absent. Prove the supplied hostile HTML/Unicode/quote payloads appear only
   escaped in every relevant dynamic text/attribute context, and add a negative
   probe showing the helper rejects an unescaped payload.
4. Every security/structure helper added or retained for this remediation must
   have a meaningful falsification test that fails for the property the helper
   claims to protect. Do not accept test names, comments, variable names,
   assertion counts or unrelated substrings as evidence. Validate executable
   semantics and relevant AST/data flow where structural inspection is needed.

Keep the already-correct post-yield cleanup guarantees and existing negative
probes. Do not weaken or delete passing evidence merely to reduce the work.

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
read-only allowlist/hash and all new falsification checks. If
`TEST_DATABASE_URL` is configured, run and report the focused and combined
database-backed suites. If it is absent, report those cases as not executed and
permitted skips; do not represent collection, source inspection or a skipped
test as runtime database evidence.

## Stop conditions and handoff

Stop `BLOCKED` without expanding scope if the starting digest differs, the
single allowed file has overlapping user changes, accepted contracts conflict,
the required correction cannot be made in the one test file, an immutable
production/template/static hash changes, a required non-database check fails,
or a configured database-backed check fails.

Report:

- the sole file changed and its before/after SHA-256;
- the HTTP/security/mutation cases now executed for each R-28–R-38 route;
- which evidence actually ran against disposable PostgreSQL and which remained
  skipped;
- every structural validator and its corresponding negative probe;
- all commands with exact results;
- unchanged production/template/static hashes;
- remaining risks and final `git status --short`; and
- verdict `READY FOR INDEPENDENT STEP 7 REMEDIATION REVIEW` or `BLOCKED`.

Then stop. Do not claim Step 7 acceptance, release Step 8, or begin Step 8.
