# Prompt for Gemini — P3.4 Step 6 remediation 01

Date: 2026-08-20 · Status: **RELEASED BY PETER / ACCEPTANCE AUTHORITY**

Peter's instruction to document the Step 6 review and write this prompt for
Gemini to fix the issues is the single required authorization and release. Do
not request or wait for another approval. Perform this remediation only, report
its checkpoint, and stop. Step 7 and every later step remain unreleased.

## Read and stop rules

Read `.agents/AGENTS.md`, `docs/implementation-plan.md`, the released Step 6
prompt, `phase-3-p3-4-step-06-review.md`, accepted contracts, and production
R-22–R-27/view-model code. Record initial status/diff and preserve all prior
accepted and unrelated work. Stop on a starting-hash mismatch, contract
discrepancy, required backend change, or need outside the allowlist.

## Starting hashes

| Path | Required SHA-256 |
|---|---|
| `adapters/web/templates/council_characters.html` | `8485873859fdfa14822a0b069a9b3408744da185b194c3ba178376c393ebced1` |
| `adapters/web/templates/character_links.html` | `e194492971afe044e4c09859a18246a374f8af16bee9b5892b1ee131264b0711` |
| `adapters/web/templates/identity_search.html` | `dbf71918e30601ebefffbd62487993b024fddd37455cb39cabd76dbe230086dc` |
| `tests/web/test_p3_4_council_character_views.py` | `27eb3fcff002e392b1a721970e4dfc029cd5f7f5208781ec695879511d61667b` |
| `tests/web/test_p3_4_member_views.py` | `4e48cc82f6ffcbe80c05908c7a6a0fb3f344e511f127557d4e5295ffb0ed3435` |
| `tests/web/test_p3_4_auth_and_system_views.py` | `32823d1e13721178a0a2fe7be185c23dbd1e52625f8022c5b65e7d6a3be9c977` |
| `tests/web/test_p3_4_shell_and_components.py` | `080f643e06b0a76c44c3fda928369ee1889f63d64dd26a4bc1102abe20cd8b91` |
| `tests/web/test_p3_4_static_assets.py` | `739c1326f42a93f2a1657bc63bdf69fe47a2a0269ddf4e5bcd7a25a32aa70970` |
| `tests/web/test_static_asset_surface.py` | `b13b8173be1bee59395d4d130d7be386daf496ced8588fa3278ef0d725ef815e` |

Immutable controls: `base.html`
`0455cb45deb77dada5a7758468ab6bac4f279002caea4a58c198145a349970fe`;
active CSS `fe0678db747dd3a56a7afd1b2a005e5da44b27e9c74d0f29ea56abcef9f2717a`;
asset manifest `98827527722a2f8cf9be0f7cc1667929aa4019334335e8ca22b68701cde45598`;
HTMX `71ea67185bfa8c98c39d31717c6fce5d852370fcdfd129db4543774d3145c0de`;
emblem `eab0d13128f55b7a367ce9e3ba88a2bad967e37768f7e28d9728186d9d322371`.

## Exact write allowlist

Only the three Step 6 templates above, the focused Step 6 test, and the five
existing test files above may change. In those five existing tests, change only
transitioned template digests that are actually necessary. Do not edit CSS,
base/includes, assets/manifests, backend Python, routes, view models, contracts,
configuration, dependencies, other tests, or documentation.

## Required corrections

### 1. Complete VM-08 evidence and invariants

Active links must render account/subject when present, access kind,
active/default state, granted-by, granted-at, nullable expires-at, reason, and
correlation. Historical links must render the same evidence plus nullable
revoked-at. Show explicit human-readable absence for nullable facts without
fabricating timestamps.

Accurately explain `LinkInvariants`: plainly state the one-active-owner
consequence; describe `revoking_last_owner_leaves_unresolved` without claiming
it reports current owner state; and render every UUID in the bounded
`default_character_held_elsewhere` tuple with an explicit empty state. These
facts explain but never authorize. Preserve exact R-25/R-26/R-27 forms.

### 2. Remove the broken optional HTMX binding

Remove the R-24 HTMX attributes and unused target/indicator from the R-25
`subject` control. R-24 remains a standalone fragment and manual snowflake entry
remains the canonical no-JavaScript workflow. Do not rename `subject`, add a
successful field, JavaScript, inline handlers, `hx-on:`, or backend parameters.

### 3. URL-encode R-22 navigation

Use the existing Jinja URL-encoding facility for opaque cursor and echoed query
component values. Preserve `q` and `include_inactive`; never decode or transform
the cursor. Add tests proving `&`, `=`, quotes, spaces, and Unicode remain inside
their intended values after HTML parsing and URL query parsing.

### 4. Render VM-09 query echo consistently

Render escaped bounded `query_echo` in ready, empty, and invalid states while
preserving standalone-fragment semantics, candidate evidence, truncation, and
the controlled notice. Add no selection authority or JS-only workflow.

### 5. Replace substring selector validation

Make the positive validator use the existing exact active CSS selector and
exact active template class-token extraction helpers after stripping CSS/Jinja
comments. Relevant negative probes must call that same positive helper. Prove
rejection of comment-only, multiline-comment, longer selector/token,
declaration-value, Jinja-comment, unused, prohibited, and unterminated-comment
falsifications. Raw substring membership may not decide validity.

### 6. Add real HTTP/security/mutation evidence

Replace the placeholder engine assertion with database-backed HTTP tests using
the accepted disposable fixtures and production app. Cover:

- R-22/R-23/R-24 Council and CA success;
- ordinary member, administrator-alone, and continuity refusal;
- unauthenticated direct R-24 fragment `401`, not login redirect;
- object substitution/non-enumeration;
- successful R-25/R-26/R-27 no-JS payloads, redirects, and state effects;
- valid, invalid, and missing CSRF; and
- stale versions with no partial write.

Use isolated IDs. Cleanup must occur after yield through a fresh bound
connection and verification must prove created rows are gone. If
`TEST_DATABASE_URL` is absent, database tests may skip, but their source must
still implement and structurally demonstrate real HTTP/caller/mutation/cleanup
behavior—not a placeholder. Do not discover/provision a database or read `.env`.

Strengthen direct-render tests so every corrected branch fails if removed.
Update only necessary transitioned template digests and preserve all earlier
assertions and immutable digests.

## Verification

Run and report literally:

```bash
sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256
sha256sum -c adapters/web/static/asset-integrity.sha256
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_council_character_views.py
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_council_character_views.py tests/web/test_p3_4_member_views.py tests/web/test_p3_4_auth_and_system_views.py tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py tests/web/test_structural_guards.py -m "not database"
./venv-web/bin/python -m pytest -q tests/web/test_p3_4_council_character_views.py tests/web/test_p3_4_member_views.py tests/web/test_p3_4_auth_and_system_views.py tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py tests/web/test_structural_guards.py
./venv-web/bin/python -m compileall -q tests/web/test_p3_4_council_character_views.py tests/web/test_p3_4_member_views.py tests/web/test_p3_4_auth_and_system_views.py tests/web/test_p3_4_shell_and_components.py tests/web/test_p3_4_static_assets.py tests/web/test_static_asset_surface.py
git diff --check
git status --short
```

Report final hashes, immutable checks, exact pass/skip counts, whether database
evidence ran, and checks not run. A skip is not database evidence.

## Stop and handoff

Report `READY FOR INDEPENDENT STEP 6 REMEDIATION REVIEW`, then stop. Do not
begin Step 7, update documentation, commit, push, deploy, access secrets/real
data, contact live services, or claim Step 6 acceptance.
