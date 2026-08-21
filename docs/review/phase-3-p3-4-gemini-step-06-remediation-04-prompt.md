# Prompt for Gemini — P3.4 Step 6 remediation 04

Date: 2026-08-20 · Status: **RELEASED BY PETER / ACCEPTANCE AUTHORITY**

Peter's instruction to document the remediation-03 review and write this prompt
is the single authorization and release. Do not request another approval. Make
this test-only correction, report the checkpoint, and stop. Step 7 and every
later step remain unreleased.

## Sole write and precondition

Edit only `tests/web/test_p3_4_council_character_views.py`.

Required starting SHA-256:

`e495b16e925802d5fb2078449cbae9501083f6e91cc245acf88918323a0d512f`

Read the Step 6 prompts/reviews, accepted R-22–R-27 behavior and existing shared
security tests first. Preserve the dirty tree. Stop on hash mismatch or any need
to change production, helpers, contracts, configuration, dependencies,
documentation, assets, or other tests.

## 1. Immediate complete no-write snapshots

For each missing-CSRF, invalid-CSRF and stale-version request across R-25,
R-26 and R-27, take a complete relevant snapshot immediately before and after
the request using fresh bound read connections, then assert exact equality:

- R-25: character version, audit-event identity set/count, and absence/count of
  the candidate active link for the target character/account.
- R-27: character version, audit-event identity set/count, and the target
  access row's `default_character` plus other fields that the operation owns.
- R-26: character version, audit-event identity set/count, and the target
  access row's `active`, `revoked_at`, and other fields the operation owns.

Make the snapshot helpers return immutable comparable values and use
case-specific predicates. Do not rely on a later successful request as proof.
Extend the same positive structural validator so deletion or substitution of
any version, audit, or access-state equality for any of the nine cases fails.
Falsifications must call the positive validator and must not pass through
comments, variable names, or unrelated comparisons.

## 2. Accepted denial-header semantics

Do not maintain an ignored-header exception list. Compare an explicit closed
set of security/deterministic response headers required by the accepted web
response policy, including at least content type, cache control, CSP,
`X-Content-Type-Options`, and referrer policy, and prove forbidden disclosure
headers such as `Location` and `Set-Cookie` are absent from both denials. Compare
status and body byte-for-byte as before. Derive the set from existing production
security tests/constants or reproduce that accepted closed set exactly; do not
invent nondeterministic exemptions.

Falsify changed status, body, every protected header value, a missing protected
header, and an introduced forbidden header through the same positive helper.

## 3. Cleanup-validator data flow

Strengthen `validate_council_cleanup_fixture` to prove for each tracked
collection separately:

- the loop iterates `tracked_state.character_ids` or
  `tracked_state.access_ids`;
- the fresh bound connection executes exactly one parameterized query;
- the SQL is a literal `SELECT count(*)` from the matching `characters` or
  `character_access` table with `WHERE id = :id`;
- the parameter mapping is exactly `{"id": <that loop variable>}`;
- the scalar result is assigned to a variable; and
- an assertion in that loop compares that exact result variable to integer zero.

Reject SQL for the wrong table, missing/changed ID predicate, wrong parameter
key/value, literal or untracked ID, unassigned result, assertion on another
variable, `assert 0 == 0`, table-wide count, verification before cleanup, same
connection reuse, and checking only one collection. Each negative probe must
invoke the production positive validator.

The actual fixture must continue to clean after yield and verify tracked IDs on
a separate fresh connection. When `TEST_DATABASE_URL` is absent, database HTTP
evidence may skip but all structural/falsification tests must run. Do not read
`.env` or provision/discover a database.

## Verification and stop

Run both integrity manifests, the focused Step 6 suite, the exact non-database
and full combined suites from remediation 03, compile the focused test,
`git diff --check`, and `git status --short`. Report exact hashes/counts,
immutable confirmation, database execution/skips, and every unrun check.

Report `READY FOR INDEPENDENT STEP 6 REMEDIATION 04 REVIEW`, then stop. Do not
begin Step 7, update documentation, commit, push, deploy, access secrets/real
data, contact live services, or claim Step 6 acceptance.
