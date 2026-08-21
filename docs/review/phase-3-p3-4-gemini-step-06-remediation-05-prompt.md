# Prompt for Gemini — P3.4 Step 6 remediation 05

Date: 2026-08-20 · Status: **RELEASED BY PETER / ACCEPTANCE AUTHORITY**

Peter's instruction to document the remediation-04 review and write this prompt
is the single authorization and release. Do not request another approval. Make
this test-only correction, report the checkpoint, and stop. Step 7 and every
later step remain unreleased.

## Sole write

Edit only `tests/web/test_p3_4_council_character_views.py`.

Required starting SHA-256:

`24c4a7fe575b485c8096f29d3efc5ee026f5a147fdbe398c62353e1ea439b72f`

Read the Step 6 prompts/reviews and existing production security-policy tests
before editing. Preserve all other work. Stop on mismatch or need to alter any
production file, shared helper, contract, configuration, dependency,
documentation, asset, manifest, or other test.

## 1. Exact accepted denial policy

Replace the required-header name tuple with a closed mapping of header names to
the exact accepted production values, derived from the existing security-policy
constants/tests. It must include at least:

- `content-type` for the HTML denial response;
- `cache-control` (`no-store`);
- `content-security-policy` with the exact production CSP;
- `x-content-type-options`;
- `referrer-policy`;
- `cross-origin-opener-policy`;
- `cross-origin-resource-policy`; and
- `permissions-policy`.

For both denial responses, assert every required header is present and equals
the exact accepted value. Then assert the two values are equal. Continue to
assert status/body byte identity and absence of `location` and `set-cookie`.
Do not add ignored/nondeterministic-header lists.

Through the same positive helper, falsify for every required header: wrong
value in only one response, the same wrong value in both responses, and missing
header from either response. Retain status/body/forbidden-header falsifications.

## 2. Semantic snapshot validator

Strengthen the positive structural validator to prove executable semantics,
not names alone.

### Snapshot helpers

For each of `snapshot_r25_state`, `snapshot_r26_state`, and
`snapshot_r27_state`, validate its AST against the accepted shape:

- correct connection/UUID arguments;
- `character_version(connection, character_id)` included;
- an audit query with a stable case-specific predicate tied to the relevant
  character/access/correlation facts, returning an immutable identity set or
  exact count;
- R-25 query for matching character/account access-row absence/count;
- R-26 query/returned fields covering `active`, `revoked_at`, and every
  operation-owned field asserted by the test;
- R-27 query/returned fields covering `default_character` and every
  operation-owned field asserted by the test; and
- an immutable tuple return containing all required results.

Do not accept a global unfiltered audit count, constants, aliases without data
flow, comments, or docstrings as evidence.

### Nine refusal sequences

For each missing-CSRF, invalid-CSRF and stale request across R-25/R-26/R-27,
validate in source order:

1. a fresh bound-connection context calls the correct snapshot helper with the
   correct character/account/access identifiers and assigns `<case>_before`;
2. the corresponding awaited client request occurs;
3. its exact expected refusal status is asserted;
4. a later fresh bound-connection context calls the same helper with identical
   identifiers and assigns `<case>_after`; and
5. the exact before/after equality is asserted immediately afterward.

Require distinct before/after connections from the request boundary. Reject a
wrong helper, wrong/swapped/literal identifiers, constant-return helper,
missing helper field/query, global audit count, reordered snapshot, intervening
mutation, missing/wrong status assertion, comparison of unrelated variables,
and equality placed before the after snapshot.

Every negative probe must mutate one semantic property and invoke the same
positive validator used on the real helpers/database test. PostgreSQL may skip
when `TEST_DATABASE_URL` is absent, but all structural/falsification cases must
run. Do not read `.env` or discover/provision a database.

## Verification and stop

Run both integrity manifests, the focused suite, the exact non-database and full
combined suites from remediation 04, focused compileall, `git diff --check`, and
`git status --short`. Report final hash, immutable confirmation, exact counts,
database execution/skips, and every unrun check.

Report `READY FOR INDEPENDENT STEP 6 REMEDIATION 05 REVIEW`, then stop. Do not
begin Step 7, update documentation, commit, push, deploy, access secrets/real
data, contact live services, or claim Step 6 acceptance.
