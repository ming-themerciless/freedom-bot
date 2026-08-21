# Prompt for Gemini — P3.4 Step 6 remediation 02

Date: 2026-08-20 · Status: **RELEASED BY PETER / ACCEPTANCE AUTHORITY**

Peter's instruction to document the remediation-01 review and write this prompt
is the single required authorization and release. Do not request another
approval. Correct only the three remaining findings, report the checkpoint,
and stop. Step 7 and every later step remain unreleased.

## Read and preconditions

Read `.agents/AGENTS.md`, `docs/implementation-plan.md`, the released Step 6 and
remediation-01 prompts, `phase-3-p3-4-step-06-review.md`,
`phase-3-p3-4-step-06-remediation-review.md`, accepted R-22–R-27 contracts, and
the production/helper code used by the tests. Record status/diff and preserve
all earlier work. Stop on mismatch, backend-contract discrepancy, unsafe
database configuration, or need outside this allowlist.

Required starting hashes:

- `character_links.html`: `bd4429204f39ff16c0584cdec256c365f1eabe650dc51bc6e662bbe059bd7de0`
- focused Step 6 test: `5e46100eebb0a8d7a49d2cc383f2b134284149927217a1bfb859ee049888dbbe`
- member digest owner: `413bdb3814639f12a1c10b6316cf3f866a3f7b43dbfc70449b5eedbe6fce9e2f`
- auth/system digest owner: `acd3d41fed68b45f6195aaa3730eea06aca6496fbc640176dc58446f3b5eb638`
- shell digest owner: `c229ecb365a29d0d1c5f22a25d010d50ac83df810a0c15f2aa2056ab3b01936f`
- static-assets test: `739c1326f42a93f2a1657bc63bdf69fe47a2a0269ddf4e5bcd7a25a32aa70970`
- static-surface test: `b13b8173be1bee59395d4d130d7be386daf496ced8588fa3278ef0d725ef815e`

Immutable controls:

- `council_characters.html`: `a18419ab163e00e54987ae7a4071f7b8698b916bf517a714b51cb0ea6dff7a02`
- `identity_search.html`: `36978ca19d5366188ae42892111cb5425ece1b6e2355710a32b71e2c6ef1e394`
- `base.html`: `0455cb45deb77dada5a7758468ab6bac4f279002caea4a58c198145a349970fe`
- active CSS: `fe0678db747dd3a56a7afd1b2a005e5da44b27e9c74d0f29ea56abcef9f2717a`
- asset manifest: `98827527722a2f8cf9be0f7cc1667929aa4019334335e8ca22b68701cde45598`

## Exact write allowlist

1. `adapters/web/templates/character_links.html`, invariant sentence only.
2. `tests/web/test_p3_4_council_character_views.py`.
3. `tests/web/test_p3_4_member_views.py`, character-links digest only if needed.
4. `tests/web/test_p3_4_auth_and_system_views.py`, character-links digest only if needed.
5. `tests/web/test_p3_4_shell_and_components.py`, character-links digest only if needed.
6. `tests/web/test_p3_4_static_assets.py`, character-links digest only if present and needed.
7. `tests/web/test_static_asset_surface.py`, character-links digest only if present and needed.

Do not edit any other template, CSS/asset/manifest, backend Python, helper,
route, view model, contract, configuration, dependency, documentation, or test.

## Corrections

### 1. Correct the invariant sentence

Replace the false “establishes or replaces” claim with contract-accurate text:
a character may have at most one active owner; when another account is the
active owner, the grant is refused and Council must revoke that owner before
granting a new owner. Do not imply automatic replacement or client authority.

### 2. Make database queries use bound connections

Every `character_version` call must receive a live bound connection, consistent
with its accepted signature. Use short read contexts and close them before HTTP
requests. Do not alter the shared helper or production code. Add a structural
or source-semantic regression that prevents passing the engine directly to
connection-only helpers in this test.

### 3. Complete the HTTP/security matrix

Using the accepted disposable database fixtures and production ASGI client,
prove:

- Council and CA success for each R-22, R-23 and R-24;
- ordinary member, administrator-alone and continuity refusal for each route;
- unauthenticated R-24 returns standalone-fragment `401` without redirect;
- the accepted object-denial/non-enumeration cases have byte-identical status,
  headers as required by the shared helper, and body—not merely one `404`;
- successful R-25, R-26 and R-27 payloads, redirects and durable state effects;
- missing and invalid CSRF for each R-25, R-26 and R-27 with no write;
- stale version for each R-25, R-26 and R-27 with `409` and explicit proof of
  no version/state/audit partial write; and
- teardown cleanup followed by a separate fresh connection proving all IDs
  created by the case are absent.

Do not weaken assertions to accommodate behavior. Reuse accepted helpers and
patterns. Keep test identities isolated. Cleanup must remain after yield. Extend
the shared structural validator and negative probes so the positive cleanup
path requires cleanup and then fresh-connection absence verification in that
order.

When `TEST_DATABASE_URL` is absent, the database case may skip. Its source must
still structurally contain the complete executable evidence above. Do not read
`.env`, discover/provision a database, or claim skipped evidence ran.

## Verification

Run the exact commands from remediation 01: both integrity manifests, focused
suite, prescribed non-database combined suite, prescribed full combined suite,
compileall, `git diff --check`, and `git status --short`. Also run any focused
structural tests added for connection-helper and cleanup ordering.

Report final hashes, immutable hashes, exact pass/skip counts, whether
PostgreSQL actually ran, and every unrun check. A skip is not database evidence.

## Stop

Report `READY FOR INDEPENDENT STEP 6 REMEDIATION 02 REVIEW`, then stop. Do not
begin Step 7, update documentation, commit, push, deploy, access secrets/real
data, contact live services, or claim Step 6 acceptance.
