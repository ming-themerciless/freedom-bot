# P3.4 Step 5 remediation 01 independent re-review

Date: 2026-08-20

Status: **SUPERSEDED BY REMEDIATION 02 RE-REVIEW; STEP 6 NOT RELEASED**

Implementer: Gemini

Independent reviewer: Codex

Acceptance and release authority: Peter Duscha

## Scope and governance result

Codex independently reviewed Gemini's completed Step 5 remediation 01 against
the prepared remediation prompt, the original Step 5 prompt and plan, accepted
contracts, intended allowlist, and required verification.

The record initially labelled remediation 01 “not released.” Peter subsequently
clarified that his single instruction to write the remediation for Gemini to fix
the issues was the authorization and release. The former authorization-gap
interpretation is therefore closed as a Codex documentation/workflow error, not
unauthorized Gemini execution. Step 6 remains unreleased.

## Remediation-01 findings closed technically

1. The stale Step 5 template digests in the auth/system test were transitioned,
   so the prescribed combined suites no longer fail on the prompt-owned
   allowlist contradiction.
2. The duplicate button-styled `View details` action and its `.btn*`/
   `.char-card-actions` CSS were removed. The accepted title link remains.
3. The database-marked test now includes R-20 empty HTTP assertions as well as
   populated R-20, authorized R-21 and byte-identical inaccessible/absent/
   malformed `404` evidence.
4. Deferred-field checks are entry-specific and reject separate fabricated
   value and injected-control mutations.
5. Hidden-authority, duplicate-button, prohibited-selector and temporary CSS
   manifest-tampering probes were added through production-facing helpers.

## Remaining technical findings

### R2-1 — cleanup passes an engine where the shared helper requires a connection

`clean_between_member_cases` resolves `migrated_database` to an SQLAlchemy
engine and calls `clean_p3_2_tables(db)` directly. The shared helper accepts a
connection and calls connection operations. The accepted pattern is:

```python
engine = request.getfixturevalue("migrated_database")
with engine.begin() as connection:
    clean_p3_2_tables(connection)
```

The error is currently hidden because `TEST_DATABASE_URL` is absent and the
database case skips.

### R2-2 — teardown structural evidence is duplicated and incomplete

The positive teardown test and cleanup-before-yield negative test repeat AST
logic rather than using one validator. There is no negative case for a fixture
that yields and never performs cleanup. Remediation 01 explicitly required
both cases through shared validation.

### R2-3 — selector helper does not verify exact template use

`validate_css_selector_scope` verifies that required selectors exist and named
prohibited selectors do not, but it never collects exact active class tokens
from the two Step 5 templates. Its “unused selector” test injects `.btn`, which
is already prohibited; it does not prove rejection of an otherwise permitted
but unused selector. The required comment-only, longer-name, and
declaration-value probes are also absent.

Refactor the helper to combine active CSS definition with exact active template
class-token use, and route positive and negative cases through it.

## Verification evidence

| Check | Result |
|---|---|
| Visual freeze manifest | 14/14 passed |
| Static integrity manifest | 3/3 passed |
| Focused Step 5 suite | 28 passed, 1 database-dependent skip |
| Non-database combined suite | 172 passed, 64 skipped, 2 deselected |
| Combined suite | 172 passed, 66 skipped |
| Compilation | passed |
| `git diff --check` | passed |

No PostgreSQL evidence ran because `TEST_DATABASE_URL` was absent.

## Review-time digests

| File | SHA-256 |
|---|---|
| `adapters/web/templates/my_characters.html` | `3705fbcd3e0803b2190746102cf6a67e20aa607432de128e3127a5a8987ce042` |
| `adapters/web/templates/character_detail.html` | `7524e43e0e2ee814b5c8b65365f4e0d72bcb9c1e42e4087ea927e3934c0c9890` |
| `adapters/web/templates/base.html` | `b836aba09cc60a2917a4b783e5b49021518e15ffed91d65fb5ecc8957d2926e5` |
| `adapters/web/static/css/freedom-blades.25d24d281e2b.css` | `25d24d281e2ba5645b1a96e09ff452be8d36fda49be106fcaea25698fd9b1b64` |
| `adapters/web/static/asset-integrity.sha256` | `eb83735f66910804dc74189655fde77aa9d5a6caf58fc5debec08edb71e637d7` |
| `tests/web/test_p3_4_member_views.py` | `ab9ee88d3ea06ed689169919466f9725dd64bd52bf7eadfd08c98b7b6578de4a` |
| `tests/web/test_p3_4_auth_and_system_views.py` | `4041972076634dcb41689eabfcd570da1046f08d0db29e636ce810e5870752df` |
| `tests/web/test_p3_4_shell_and_components.py` | `86124cc1e860aaf03828e9723654fde4a168a0702c8cf73bd5fbdb1d3131d8de` |
| `tests/web/test_p3_4_static_assets.py` | `61c612d254f4fbf409dd5368e424aafc074e92fbd966a68d4048a232ff5b83d0` |
| `tests/web/test_static_asset_surface.py` | `a6128f0a29995f10fce7ca7556ea1119b66ccd1acbd4363b55c1a06d2784322a` |

## Verdict

Step 5 remained **BLOCKED** on R2-1 through R2-3. Peter's instruction to write
remediation 02 authorized and released it under the clarified single-approval
rule. Gemini completed it and Codex re-reviewed it. Step 6 and every later step
remain unreleased.
