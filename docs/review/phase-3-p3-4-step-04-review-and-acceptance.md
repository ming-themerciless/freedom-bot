# P3.4 Step 4 independent final re-review and acceptance

Date: 2026-08-20

Status: **ACCEPTED — STEP 4 CLOSED; STEP 5 SUBSEQUENTLY RELEASED**

Implementer: Gemini

Independent reviewer: Codex

Acceptance authority: Peter Duscha

## Decision

Peter accepted P3.4 Step 4 on 2026-08-20 after Gemini completed the
authentication and system-state pages and three bounded remediation passes,
and Codex completed independent final re-review. No Step 4 finding remains
open.

This acceptance closed Step 4 only. Peter subsequently and separately released
the bounded Step 5 prompt on 2026-08-20. Neither decision closes P3.G4,
authorizes staging or deployment, authorizes secrets or live services, or
authorizes use of real data.

## Closed review history

1. The initial review found four issues: missing VM-22 HTTP byte-identity
   evidence, missing later-step CSS falsification, ignored VM-04 availability
   facts, and the unused `.auth-lead` selector.
2. Remediation 01 closed those four issues. Re-review found two test-only
   defects: incomplete database teardown and a selector-use falsification that
   bypassed the shared helper.
3. Remediation 02 closed those two defects. Re-review found one final test-only
   defect: CSS comments could count as active selector definitions.
4. Remediation 03 stripped CSS block comments before selector parsing, rejected
   unterminated comments safely, required exact active class selectors, and
   added positive and negative probes through the production validator.
5. Codex independently reproduced the original comment-only mutation and
   confirmed that it is now rejected with the intended assertion.

## Accepted final digests

| File | Accepted SHA-256 |
|---|---|
| `adapters/web/templates/base.html` | `d095f37624d1ce37a9f92ecccde9b6a8d0d407aba55052bb79f1f6050fe1c79d` |
| `adapters/web/templates/emergency.html` | `0eec75c17bb6ea602fabc7aace0aaf1453e70fd102e61da5298759e094980a99` |
| `adapters/web/static/css/freedom-blades.da727b328510.css` | `da727b32851014c26d2131bcab24be4cf660c8a3f83360acf3330281c2a0b1a9` |
| `adapters/web/static/asset-integrity.sha256` | `e04efc4f036f70e18b8096184174642ce4bbfdf727f446961d1876c6830822ae` |
| `tests/web/test_p3_4_auth_and_system_views.py` | `90553f30b516d64832fe813ed591ffd2aa028d07b92b60de5171882692758da6` |
| `tests/web/test_p3_4_shell_and_components.py` | `9b314c04b16ed96d1d010913bf8432fd9abca71fbf48921bd0066e38440e9b1d` |

The other seven Step 4 templates retain the accepted digests recorded by the
Step 4 validation suite. The accepted vendored HTMX file and guild emblem also
remain byte-identical to Step 2.

## Final independent evidence

| Check | Result |
|---|---|
| Visual freeze manifest | 14/14 passed |
| Static integrity manifest | 3/3 passed |
| Focused Step 4 suite | 29 passed, 1 permitted database-dependent skip |
| Non-database supporting suite | 115 passed, 64 database-dependent skips |
| Combined suite | 144 passed, 65 database-dependent skips |
| Python compilation | passed |
| `git diff --check` | passed |
| Independent comment-only selector probe | rejected as required |

The database-dependent tests were collected but skipped because
`TEST_DATABASE_URL` was not configured. The released Step 4 prompt explicitly
permits that environment-dependent skip.

## Next-step boundary

Peter explicitly released the separate bounded Step 5 prompt on 2026-08-20.
Gemini may execute Step 5 only and must stop at its checkpoint. Step 6 and every
later step remain unreleased.
