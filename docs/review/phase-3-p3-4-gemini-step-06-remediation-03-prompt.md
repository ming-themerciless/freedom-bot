# Prompt for Gemini — P3.4 Step 6 remediation 03

Date: 2026-08-20 · Status: **RELEASED BY PETER / ACCEPTANCE AUTHORITY**

Peter's instruction to document the remediation-02 review and write this prompt
is the single required authorization and release. Do not request another
approval. Make this test-only correction, report the checkpoint, and stop.
Step 7 and every later step remain unreleased.

## Preconditions and sole write

Read `.agents/AGENTS.md`, `docs/implementation-plan.md`, the Step 6 prompt and
all three Step 6 review records, accepted denial/test contracts, and existing
shared HTTP/cleanup helpers. Record initial status and preserve all prior work.

Edit only:

`tests/web/test_p3_4_council_character_views.py`

Its required starting SHA-256 is:

`078b2c19eae82c9df0dfcb8e8da84bc49efedde94eb665db9604641350e937ae`

Stop on mismatch or if any production/backend/helper/documentation change is
needed. All templates, CSS, assets, manifests, routes, view models, contracts,
configuration, dependencies, and other tests are immutable.

## Correction 1 — prove no partial audit writes

For every missing-CSRF, invalid-CSRF and stale-version case across R-25, R-26
and R-27, capture the relevant character version, access-row state and audit
event count/set immediately before the refused request, then query them through
a fresh bound connection immediately afterward. Assert exact equality and the
expected refusal status. A later successful mutation is not a substitute for
the immediate no-write proof. Use stable case-specific identifiers/correlation
facts where the accepted schema permits exact audit selection; do not weaken
the assertion to a global `>=` count.

Add structural/source falsification evidence showing that removing the audit
before/after comparison from any of the nine refusal cases fails the shared
positive validator. The validator must inspect semantics, not comments or
docstrings.

## Correction 2 — complete denial-response identity

For the accepted absent/malformed or otherwise contract-equivalent object
denial pair, assert identical status, body, and the security-relevant headers
defined by the existing shared denial-response convention. Ignore only headers
that the accepted helper explicitly treats as nondeterministic; do not invent a
new exception list or compare merely status/body. Reuse the shared helper if it
fits, otherwise implement equivalent exact semantics locally and falsify a
single changed status, body, or protected header.

## Correction 3 — semantic ID-specific cleanup proof

Track the exact character/access identifiers created by the database case in a
fixture-owned mutable record supplied before yield. After yield:

1. resolve the existing database fixture only on the guarded path;
2. clean through one bound connection;
3. open a separate fresh connection; and
4. query by every tracked ID and assert each is absent.

Keep the repository's broader portal cleanup responsible for accounts,
identities, sessions and audit tables; do not duplicate or reorder that global
cleanup. The Step 6 fixture must precisely verify the character/access IDs it
created and owns.

Strengthen the shared AST validator so it proves data flow from the pre-yield
tracked-ID record into post-cleanup parameterized absence queries on the fresh
connection, followed by assertions on those query results. It must reject:

- `assert True`;
- unrelated `SELECT 1` or table-wide count assertions;
- literal/untracked IDs;
- verification before cleanup;
- verification on the cleanup connection rather than a fresh connection;
- checking only characters or only access rows; and
- comments/docstrings containing the expected words without executable proof.

Every negative case must invoke the same positive validator used on the real
fixture.

If `TEST_DATABASE_URL` is absent, the HTTP case may skip, but all structural
tests must run. Do not discover/provision a database or read `.env`.

## Verification

Run and report:

```bash
sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256
sha256sum -c adapters/web/static/asset-integrity.sha256
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_council_character_views.py
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_council_character_views.py tests/web/test_p3_4_member_views.py tests/web/test_p3_4_auth_and_system_views.py tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py tests/web/test_structural_guards.py -m "not database"
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_council_character_views.py tests/web/test_p3_4_member_views.py tests/web/test_p3_4_auth_and_system_views.py tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py tests/web/test_structural_guards.py
./venv-web/bin/python -m compileall -q tests/web/test_p3_4_council_character_views.py
git diff --check
git status --short
```

Report the final test-file hash, confirmation that every other file retained its
starting hash, exact pass/skip counts, whether PostgreSQL ran, and all checks not
run. A skip is not database evidence.

## Stop

Report `READY FOR INDEPENDENT STEP 6 REMEDIATION 03 REVIEW`, then stop. Do not
begin Step 7, update documentation, commit, push, deploy, access secrets/real
data, contact live services, or claim Step 6 acceptance.
