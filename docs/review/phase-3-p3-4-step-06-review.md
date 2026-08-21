# P3.4 Step 6 independent review

Date: 2026-08-20

Status: **REMEDIATION REQUIRED; REMEDIATION 01 RELEASED**

Implementer: Gemini · Independent reviewer: Codex · Acceptance authority: Peter Duscha

## Governance result

Codex reviewed Gemini's first Step 6 implementation against the released Step
6 prompt, accepted Step 5 backend contracts, write allowlist, and prescribed
verification. Peter's instruction to document this review and write a
remediation prompt is itself the one required authorization and release under
the standing single-approval rule. No second or third approval is required.

Step 6 is not accepted. Step 6 remediation 01 is released. Step 7 and every
later step remain unreleased.

## Findings

1. **S6-1 — Required database HTTP/security evidence is absent.** The sole
   database-marked test skips without `TEST_DATABASE_URL`; otherwise it only
   resolves the engine and asserts it is non-null. It tests no R-22–R-27 HTTP
   route, authorization/refusal, R-24 `401`, CSRF, stale version, object
   substitution, successful mutation, redirect, state effect, or verified
   cleanup.
2. **S6-2 — VM-08 evidence is incomplete.** Active links omit correlation and
   expiry. Historical links omit granted time, expiry, and default-state
   evidence. The prompt requires all accepted Council-visible `AccessFact`
   evidence.
3. **S6-3 — The optional R-24 HTMX request is nonfunctional.** The R-25 input
   submits its value as `subject`, but R-24 accepts `q`. Removal is the preferred
   bounded correction because HTMX is optional and manual snowflake entry is
   canonical.
4. **S6-4 — `LinkInvariants` is presented incorrectly.** The one-owner
   consequence is not plainly stated; `default_character_held_elsewhere` is a
   tuple of UUIDs but is treated only as a boolean; and the false revoke branch
   makes an unsupported claim about current ownership.
5. **S6-5 — R-22 cursor navigation does not URL-encode values.** HTML escaping
   alone does not preserve query-component boundaries after URL parsing.
6. **S6-6 — Selector validation uses substrings.** The positive validator and
   negative probes do not consistently use the available exact active-selector
   and exact class-token extraction helpers.

## Verification evidence

| Check | Result |
|---|---|
| Visual freeze manifest | 14/14 passed |
| Static integrity manifest | 3/3 passed |
| Focused Step 6 suite | 25 passed, 1 database skip |
| Non-database combined suite | 213 passed, 64 skipped, 3 deselected |
| Combined suite | 213 passed, 67 skipped |
| Compilation | passed |
| `git diff --check` | passed |
| PostgreSQL HTTP/mutation evidence | **not run; `TEST_DATABASE_URL` absent** |

Passing structural tests do not close these findings. A database skip is not
database or HTTP evidence.

## Review-time hashes

- `council_characters.html`: `8485873859fdfa14822a0b069a9b3408744da185b194c3ba178376c393ebced1`
- `character_links.html`: `e194492971afe044e4c09859a18246a374f8af16bee9b5892b1ee131264b0711`
- `identity_search.html`: `dbf71918e30601ebefffbd62487993b024fddd37455cb39cabd76dbe230086dc`
- focused test: `27eb3fcff002e392b1a721970e4dfc029cd5f7f5208781ec695879511d61667b`
- active CSS: `fe0678db747dd3a56a7afd1b2a005e5da44b27e9c74d0f29ea56abcef9f2717a`
- asset manifest: `98827527722a2f8cf9be0f7cc1667929aa4019334335e8ca22b68701cde45598`

## Verdict

**REMEDIATION REQUIRED.** Execute only
`phase-3-p3-4-gemini-step-06-remediation-prompt.md`, report
`READY FOR INDEPENDENT STEP 6 REMEDIATION REVIEW`, and stop. Step 6 remains
unaccepted and Step 7 remains unreleased.
