# P3.5 supervised-session remediation — Codex security re-review

Date: 2026-08-24

Reviewed submission:
`phase-3-p3-5-supervised-session-remediation-submission.md`

Related security review:
`phase-3-p3-5-supervised-session-codex-security-review.md`

Related independent re-review:
`phase-3-p3-5-supervised-session-remediation-codex-re-review.md`

This is a distinct defensive security-focused source re-review. It is not a
penetration test, external scanner result, Security Reviewer acceptance, RAID
closure, or gate decision.

## Recommendation

**Security re-review accepts the repository remediation of prior S1 through S5.**
No new Blocking or Important security code finding was found. The Security
Reviewer should still withhold A-05 criterion 10 confirmation until the live and
operator-owned evidence listed below is complete and N-32a has an authorized
disposition.

## Prior security findings

### S1 — closed in repository

Every counted emergency refusal named by the prior review now reaches a durable,
request-scoped exactly-once audit boundary. Limiter activation no longer silences
the emergency audit stream, and the displayed correlation resolves to the row.
The new reasons distinguish defensive boundaries internally without exposing
account or credential existence to the caller.

### S2 — closed in repository

Both break-glass authentication methods now attribute logout to
`platform_administrator`, derived from persisted session provenance. Ordinary
Discord logout remains attributed to `guild_member`. The mapping is explicit and
complete rather than defaulting future methods.

### S3 — implementation accepted; numeric authority pending

Challenge issuance and assertion verification no longer consume the same address
bucket. This removes the observed emergency-lockout amplification while preserving
N-32's verification, account and unknown-credential controls. The proposed N-32a
budget is bounded and construction-validated. It must be accepted or replaced by
the Acceptance Authority before the changed policy becomes effective.

### S4 — closed in repository

Failed recovery redemption retains atomic consume semantics and produces a useful
internal forensic distinction. Caller non-enumeration is preserved across
consumed, expired, invalidated and unknown tokens, and neither token nor token hash
enters audit.

### S5 — closed in repository

Identity-provider health is now a real, bounded, anonymous reachability probe.
The probe carries no application credential, privileged scope, response body or
exception detail. Its broad failure catch is appropriate at this health boundary:
it yields `false` and a controlled `503`, not a false healthy answer or an
unhandled error.

## Residual security and operational conditions

- Complete live R-41 and R-46 denial observations with valid CSRF context. An
  invalid-CSRF `403` is not authorization evidence.
- Obtain the Operations Owner's exact session end, safe grant record UUIDs, and
  truthful non-sensitive authenticator description; do not treat credential
  nicknames as authenticator identity.
- Accept or revise N-32a through change control, then observe its limiter behavior
  in the intended environment.
- Resolve S-1 deployment/process identity and S-2 worker readiness before relying
  on I-06 operational evidence.
- Complete A-05 criteria 3, 4 and 9 before asking the Security Reviewer for
  criterion 10 confirmation.
- Set a conservative health-monitor polling interval so the anonymous Discord
  probe does not create avoidable rate-limit noise; verify that behavior under
  TC-OPS-05.

## Verification boundary

The security-relevant focused set passed 320 tests, and the full portal suite
passed 2,330 with 80 documented caller-matrix skips. Review included refusal audit
payloads and correlation, limiter independence, persisted logout attribution,
grant classification and response equality, provider request contents/timeouts,
configuration validation, structural import guards and the frontend freeze guard.

No network probing, real credential use, staging mutation, external account access
or non-test database access was performed.

## Gate effect

No closed gate is reopened or closed. A-05 and I-06 remain open, public exposure
and Phase 4 remain unauthorized, and acceptance remains with the maintainer.

## Subsequent Acceptance Authority decision

Peter Duscha accepted N-32a on 2026-08-24 at 10 WebAuthn challenge issuances per
source IP per 10 minutes, separate from N-32's unchanged assertion budgets. The
remaining security and operational conditions in this review are unchanged.
