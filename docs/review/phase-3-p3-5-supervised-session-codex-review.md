# P3.5 supervised session — Codex independent review

Date: 2026-08-24

Role: Independent Reviewer under implementation-plan §0.3 and §16.4

Reviewed request:
`phase-3-p3-5-supervised-session-codex-review-request.md`

Reviewed evidence:
`phase-3-p3-5-supervised-session-evidence-2026-08-24.md`

Commit under test: `0c95e72bc9a3c274b5683161b17ceb0fe53f8902`

Evidence-record commit reviewed: `52ea1624bcde726abb9dc4349e104a0d1af910fa`

This is an independent evidence and procedure review. It is not a gate decision,
does not close a RAID item, and does not authorize public exposure or Phase 4.

## Recommendation

**Accept the completed §4 browser observations as credible evidence for the exact
rows and environment stated, and accept SP-21 as strong evidence of the recovery
grant's single-use and expiry behavior. Do not yet treat the evidence package as
complete enough to support A-05 closure.**

S-5 and S-6 prevent A-05 criterion 7 from being satisfied. S-7 requires an
explicit limiter-policy correction or accepted security/availability disposition.
SP-22 remains partial: its two named POST boundaries have not been observed on the
deployed build. The evidence record also needs a small consistency correction
before it is used in a later gate package.

## Findings

### Blocking F1 — break-glass refusal auditing is incomplete, and S-5 is narrower than the defect

S-5 is valid and blocks A-05 criterion 7. Both N-32 limiter refusals in R-08
return a correlation reference without recording an audit event
(`adapters/web/app.py:1092-1113`). The same class of omission also exists on R-07's
per-address limiter refusal (`:1062-1069`) and in R-09 for an empty token and a
per-address limiter refusal (`:1153-1164`). Origin and malformed-request paths may
be governed separately, but the accepted SM-03 statement that every emergency
attempt and outcome is audited cannot coexist with these unaudited, correlation-
bearing refusal paths.

Required remediation: route every counted emergency refusal through one durable
failure-audit helper, retain the same coarse caller response, and add PostgreSQL-
backed route tests proving that each limiter boundary writes exactly one refusal
event with the displayed correlation ID. Avoid recording raw IP addresses,
tokens, assertions, or credential material.

### Blocking F2 — logout audit attribution is false for break-glass sessions

S-6 is a defect and blocks A-05 criterion 7. `SessionService.logout()` hardcodes
`guild_member` (`application/web/sessions.py:658-661`) even when the persisted
session's authentication method proves that the actor is a continuity-scoped
Platform Administrator with no guild membership. The `auth_method` payload is a
useful mitigation but does not make a false capability column correct.

Required remediation: derive the authority used for logout from the trusted
persisted session/authentication context. At minimum, both break-glass methods must
record `platform_administrator`; ordinary sessions should record the effective
trusted logout attribution defined by the audit contract. Add regressions for
WebAuthn, recovery-grant, ordinary member, Council, and ordinary administrator
sessions.

### Important F3 — SP-22's POST half is live-testable without handling the cookie

The suite evidence for R-41 and R-46 is strong: the caller-matrix tests provide a
valid CSRF token and assert `403`, so they measure authorization rather than CSRF.
It is not, however, the deployed observation required by the named SP-22 procedure
and A-05 criterion 6's wording “by route.”

The cookie constraint does not prevent a safe observation. While holding the live
break-glass session, the operator can use a same-origin browser request. The
browser attaches its HttpOnly cookie without exposing it; the operator can reuse
the CSRF value already rendered in an allowed page and submit synthetic UUIDs.
`enter_mutation()` validates session/origin/content type/CSRF and then refuses the
continuity-scoped capability before either handler parses or looks up the supplied
object identifier. Thus no real job, snapshot, preview token, or mutation is
needed. Record status and coarse body only, and do not record the cookie or CSRF
value.

Required disposition: observe R-41 and R-46 in this manner before criterion 6 is
used for A-05 closure. R-20/R-22/R-40 are accepted as valid deployed observations.

### Important F4 — the evidence record is internally stale after SP-21/SP-22 were appended

The document preserves several pre-completion states: §1 still leaves browser/OS
and authenticators as Not Run; §4 begins “Not started”; §8.2 says criterion 8 is
Not Run; and §8.4 lists only the earlier six findings, omitting S-8 and S-9. The
session-end field also gives no exact end timestamp even though the accepted
evidence rules request exact timestamps. Separately, readiness-plan §9.2 A-9 says
SP-21 records the grant record ID, while the published SP-21 table does not.

These do not invalidate the timestamped audit observations, but they make the
document unsafe to cite wholesale without accidentally citing a contradicted
status.

Required remediation: reconcile the header, §4, §8.2 and §8.4 with the final
state; record exact end time(s) if available; add the non-secret grant record UUIDs
or explicitly document and approve a deviation from A-9's evidence contract.

## Disposition of the eight requested findings

| Finding | Independent disposition | Effect |
|---|---|---|
| S-1 | Valid operational deployment defect; restart fixed this run, not the deploy/reload gap | Important; blocks future evidence unless build/process identity is verified after deployment |
| S-2 | Not a health-code defect as written: `_worker_liveness()` explicitly defines an empty queue as healthy and directs unit liveness monitoring to systemd | Operational prerequisite for I-06; inactive worker must be corrected before worker procedures, but `/healthz` is behaving to its documented contract |
| S-4 | Valid monitoring defect | Important and blocks I-06/TC-OPS-05 until a real bounded provider check exists or VM-16 is changed through controlled contract governance; do not report a constant as health |
| S-5 | Valid, with broader affected paths described in F1 | Blocking for A-05 criterion 7 |
| S-6 | Valid audit-integrity defect | Blocking for A-05 criterion 7 |
| S-7 | Valid limiter-policy/availability defect | Important; split challenge issuance from assertion verification rather than merely increasing the coupled number. Revalidate numeric budgets under N-32 before A-05 readiness |
| S-8 | Valid Product Owner observation, not a defect | Optional/scope decision; the frozen visual baseline means any change needs the stated authority |
| S-9 | Valid forensic-quality defect | Important; does not erase SP-21's behavioral proof, but should be fixed before A-05 readiness is confirmed |

For S-9, keep the atomic conditional `UPDATE`. After a zero-row result, perform a
read-only classification by token hash inside the same transaction and pass only a
non-secret grant record UUID and closed internal reason (`consumed`, `expired`,
`invalidated`, or `unknown`) into the audit event. The caller must continue to see
the same neutral response and timing should not be intentionally differentiated.

## Answers to the review questions

1. **Yes.** S-5 blocks A-05 criterion 7.
2. **S-6 is a defect**, not an accepted simplification.
3. **Split the buckets.** Challenge issuance and assertion verification protect
   different resources. Preserve an assertion-verification budget of five only if
   the accepted N-32 policy intends five actual assertions; define and test a
   separate issuance budget from measured resource/availability needs.
4. **Fix S-4 as monitoring.** `identity_provider` has defined VM-16 meaning and is
   useful during the outage break-glass exists to survive. Removing it merely to
   avoid probing would weaken operations and requires contract change control.
4a. **Yes.** Record the closed internal cause and grant record UUID after failed
   redemption, without changing atomic consumption or caller presentation.
5. **No.** Suite evidence is strong but SP-22 explicitly calls for route proof;
   safely observe R-41 and R-46 as described in F3.
6. **No closed gate is reopened by this package.** The findings constrain open
   A-05 and I-06 work. S-1 should be carried into deployment/operations evidence.
7. **The underlying observations are honest enough to retain**, including the
   signed-out near-miss and operator-report labels. The document itself needs F4's
   reconciliation before a later gate decision cites it as a coherent final record.

## Verification

The focused repository verification completed against the disposable PostgreSQL
database:

```text
node --test tests/web/webauthn_client.test.mjs                    50 passed
./venv-web/bin/python -m pytest -q \
  tests/web/test_p3_5_webauthn_and_shell_presentation.py          9 passed
TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
  ./venv-web/bin/python -m pytest -q \
  tests/web/test_break_glass_login.py                             17 passed
sha256sum -c adapters/web/static/asset-integrity.sha256           4/4 OK
git diff --check                                                  clean before review records
```

No staging host, real authenticator, credential, session cookie, recovery token,
external account, or production database was accessed by this review.
