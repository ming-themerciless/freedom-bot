# P3.4 Step 4 independent review

Date: 2026-08-20

Status: **SUPERSEDED BY REMEDIATION RE-REVIEW; STEP 4 STILL OPEN**

Implementer: Gemini

Independent reviewer: Codex

Acceptance and release authority: Peter Duscha

## Scope

Codex independently reviewed Gemini's Step 4 authentication and system-state
page delivery against the released Step 4 prompt, accepted contracts, exact
allowlist, starting/immutable hashes, and required verification commands.

This review does not accept Step 4 or release Step 5.

## Findings

### F1 — VM-22 HTTP byte-identity evidence is absent

`tests/web/test_p3_4_auth_and_system_views.py` claims HTTP coverage for the
absent-versus-inaccessible `404` body but contains no HTTP test. The released
Step 4 combined command does not select the pre-existing D-03 correction module,
so the Step 4 checkpoint contains no executed HTTP evidence for this mandatory
row. Add a database-marked case using the established disposable-database
fixtures and production application client. It must prove inaccessible, absent,
and malformed character identifiers all answer `404` with byte-identical
bodies.

### F2 — required later-step CSS falsification is absent

The positive CSS scope assertion rejects named later-step selectors, but no
negative test adds one and passes it through the same validator. The released
prompt explicitly required this falsification. Refactor the positive scope
logic into a shared helper and prove a representative unauthorized selector
fails for the intended reason.

### F3 — VM-04 availability facts are ignored

`emergency.html` always renders both the WebAuthn section and R-09 recovery
form. It does not read `webauthn_supported_hint` or
`recovery_form_available`, and tests exercise only `True/True`. Render each
configuration-controlled option only when its corresponding accepted VM-04
fact is true, use a static non-sensitive unavailable notice when false, and test
all four boolean combinations plus failure/no-failure without introducing an
account, enrollment, credential, grant-state, or caller-state oracle.

### F4 — unused Step 4 selector

The new `.auth-lead` selector is not used by any Step 4 template. Remove it.
Step 4 CSS may contain only selectors actually used by the eight Step 4 pages,
in addition to the accepted Step 2 foundation and Step 3 shell selectors.

## Verification evidence

All commands completed with exit code 0:

| Check | Result |
|---|---|
| Visual freeze manifest | 14 files OK |
| Static integrity manifest | 3 files OK |
| Focused Step 4 suite | 20 passed |
| Supporting suite | 106 passed, 64 database-dependent skips because `TEST_DATABASE_URL` is absent |
| Combined suite | 126 passed, 64 database-dependent skips |
| Compilation | passed |
| `git diff --check` | passed |

Passing execution does not close F1–F4 because the missing conditions are not
currently exercised or enforced.

## Review-time digests

| File | SHA-256 |
|---|---|
| `adapters/web/templates/emergency.html` | `589ab11b291a0d24866ed341cb0ecd33ea0c63f076abde3b58947b473762d6ff` |
| `adapters/web/templates/base.html` | `7a135ee0ff6865d9c0de517c1b42662df64dfa694c76f1c32960139cb27f4115` |
| `adapters/web/static/css/freedom-blades.f72398a9d642.css` | `f72398a9d642749e0a20f370365498d33cecfdfee970c8aa60621a4e3ab06686` |
| `adapters/web/static/asset-integrity.sha256` | `39e9183ce283d781a021d6f7d7a1fee2fd3418aaad70cf6a29ea385a37e38977` |
| `tests/web/test_p3_4_auth_and_system_views.py` | `985ea8386cc1bca5f4c1a647a8071c76bbe5c194dc4f24c6c4dd294530ff1421` |
| `tests/web/test_p3_4_shell_and_components.py` | `d73560d8135211f458d6795834d08c2a31b9bba5356f42c1bab95750d75dc443` |
| `tests/web/test_p3_4_static_assets.py` | `edcf0e3bb0ce8339f72f0522619656d16d1e76d5a798fb0f608826c1890e7217` |
| `tests/web/test_static_asset_surface.py` | `810861c26beed7c33bd6762290c1ea5f01698d29bd1585a8bff23b9db656849f` |

## Verdict

This was the first-review verdict. Gemini completed the authorized remediation;
independent re-review confirmed F1–F4 were addressed but found two test-only
follow-up defects. See `phase-3-p3-4-step-04-remediation-review.md`. Step 4
remains open and Step 5 remains unreleased.
