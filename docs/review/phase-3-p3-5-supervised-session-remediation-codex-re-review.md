# P3.5 supervised-session remediation — Codex independent re-review

Date: 2026-08-24

Role: Independent Reviewer under implementation-plan §0.3 and §16.4

Reviewed submission:
`phase-3-p3-5-supervised-session-remediation-submission.md`

Related review:
`phase-3-p3-5-supervised-session-codex-review.md`

Baseline: `52ea1624bcde726abb9dc4349e104a0d1af910fa`, with the submitted
working-tree changes

This is an independent repository-remediation re-review. It is not a gate
decision, does not close a RAID item, does not accept N-32a on behalf of the
Acceptance Authority, and does not authorize public exposure or Phase 4.

## Recommendation

**Accept the repository remediation for F1/S-5, F2/S-6, S-4, S-7 and S-9.**
The two Blocking code findings from the prior independent review are corrected.
No new Blocking or Important code finding was found.

The package is not complete as an A-05 evidence package. Prior finding F3 remains
open for live R-41/R-46 observations, and F4 remains partially open for facts only
the Operations Owner can provide. At the time of this re-review N-32a remained a
pending numeric-policy decision; the subsequent decision is recorded at the end
of this document. The re-review found its implementation coherent but did not
itself supply authority acceptance.

## Closure of prior repository findings

### F1 / S-5 — closed in repository

`EmergencyRefusalRecorder` gives one request-scoped exactly-once boundary to
route-generated and service-described emergency refusals. R-07's challenge
limiter, R-08's address/account/credential limiters and malformed body, and R-09's
address limiter, absent token and per-grant cap now write a durable
`auth.emergency.refused` row with the correlation shown to the caller. The payload
uses a closed reason and bounded internal references without recording an address,
user agent, token, token hash, assertion or caller-supplied credential id.

The malformed-JSON and empty-token paths are deliberately placed after their
address budget. This makes their audit growth bounded and removes the former free
probe. PostgreSQL-backed route tests cover the correlation and exactly-one-row
properties at every named boundary.

### F2 / S-6 — closed in repository

Logout attribution is now derived from the trusted persisted `auth_method` through
an explicit, completeness-checked mapping. WebAuthn and recovery-grant sessions
record `platform_administrator`; ordinary Discord sessions record `guild_member`,
including an ordinary member who also holds Council or administrator capability.
That distinction matches logout as termination of the provider-authenticated
session rather than exercise of a game-policy capability. Future authentication
methods fail closed until their attribution is decided.

### S-7 — repository implementation accepted, policy acceptance pending

R-07 challenge issuance and R-08 assertion verification now use distinct fixed-
window actions. The accepted N-32 assertion values are unchanged; per-account and
per-credential assertion budgets remain independent. The proposed N-32a value of
ten challenge issuances per address per ten minutes is consistently represented in
configuration, validation, documentation and tests. It is a reasonable correction
to the observed coupling, but §0.2/§5 acceptance remains with the Acceptance
Authority.

### S-9 — closed in repository

The single conditional `UPDATE` remains the sole consumption decision. After a
zero-row result, one read-only query in the same transaction classifies the stored
row as consumed, invalidated, expired or unknown. Audit receives the closed reason
and non-secret grant record UUID where a row exists; the four caller responses
remain equal apart from their per-request correlation. Tests cover all states and
prove classification does not consume, invalidate or increment the grant.

### S-4 — closed in repository

R-10 now awaits the identity provider's bounded probe instead of passing a literal
`True`. The Discord adapter uses an unauthenticated `GET /gateway`, sends no client
credential or OAuth token, reads no response body, caps the call at two seconds or
the tighter configured timeout, and converts all failures into a boolean. A failed
probe produces VM-16's existing `degraded`/`503` result without changing the other
checks.

The operational consequence is accepted and documented: each health poll makes
one outbound anonymous request, and Discord unavailability or throttling degrades
the endpoint. Monitor cadence should be set conservatively during I-06.

## Remaining evidence finding

### F4 — partially remediated; authenticator row still needs operator correction

The progressive-state contradictions in the evidence header, §4, §8.2 and §8.4
are corrected, and the exact end time and grant UUIDs are honestly left
outstanding. One replacement is not equivalent to the requested field:

`Authenticator(s)` now lists database credential nicknames (`puppetmaster`,
`puppetphone`, `macbook`, `iphone`). The same evidence record explains that these
portal-held nicknames are not what the platform passkey UI displays and that the
operator could not use them to distinguish authenticators. They therefore are not
a non-sensitive authenticator description or model, and SP-21 did not use an
authenticator at all.

Required evidence correction: the Operations Owner should supply the original
plan's non-sensitive authenticator description (for example, built-in platform
authenticator and device class, without credential material), or the row should
remain explicitly Not Recorded. Do not infer a device or authenticator model from
credential nicknames.

F4 remains Important evidence hygiene, not a code blocker. The exact session-end
timestamp and SP-21 grant record UUIDs also remain outstanding as the submission
states.

## Still outside repository closure

- F3 remains open: observe R-41 and R-46 on the deployed build under a live
  break-glass session, with valid same-origin and CSRF context, so the `403`
  measures capability rather than an earlier guard.
- S-1's deploy/reload control and S-2's inactive worker remain operational work.
- S-8 remains a Product Owner visual-scope decision.
- A-05 criteria 3, 4, 9 and 10 remain open, as do I-06 and the Phase 3 gate.

## Verification

Independently run against the disposable PostgreSQL database:

```text
Focused remediation and regression set: 320 passed in 4.48s
Full portal suite:                    2330 passed, 80 skipped in 131.17s
```

The focused set covered all four new test modules plus limiter/outage,
break-glass, settings construction, structural guards and the frontend freeze
guard. The 80 full-suite skips are the documented permitted caller-matrix cells.
`git diff --check` was clean after the review records were written.

No staging host, authenticator, credential, cookie, recovery token, external
account, production service or production database was accessed.

## Subsequent Acceptance Authority decision

Peter Duscha accepted N-32a on 2026-08-24 at the reviewed value: 10 WebAuthn
challenge issuances per source IP per 10 minutes. N-32's assertion budgets remain
unchanged. This subsequent numeric-policy decision changes none of the open
evidence, RAID or gate conditions above.
