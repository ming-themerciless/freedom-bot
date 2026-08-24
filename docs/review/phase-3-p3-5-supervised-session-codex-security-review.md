# P3.5 supervised session — Codex security-focused review

Date: 2026-08-24

Reviewed request:
`phase-3-p3-5-supervised-session-codex-review-request.md`

Related independent review:
`phase-3-p3-5-supervised-session-codex-review.md`

This is a distinct defensive security-focused review of the authorized local
project and its sanitized evidence. It is not a penetration test, external scanner
result, security acceptance, RAID closure, or gate decision.

## Recommendation

**Do not confirm break-glass readiness yet.** The successful real-authenticator
and provider-outage observations are meaningful, and the continuity authorization
model is strong. The refusal audit goes silent at rate-limit boundaries, logout
misstates the authority used, and the shared limiter leaves only about two complete
ceremonies in a five-unit window. Those weaknesses converge on the exact incident
path break-glass is meant to preserve.

## Blocking security findings

### S1 — attack-indicating limiter refusals are not auditable

S-5 is confirmed and extends beyond the two R-08 branches. R-07's address limiter
and R-09's empty-token/address-limiter paths also bypass the durable failure audit.
An attacker can therefore make the emergency audit stream stop at the point the
defensive control activates, while the UI continues issuing correlation references
that do not resolve.

This violates the accepted “every attempt and outcome” audit property and blocks
A-05 criterion 7. Use one safe refusal recorder for all counted emergency paths
and verify exactly-once events against PostgreSQL. Payloads must remain free of
tokens, assertions, raw addresses, user-agent strings, and credential material.

### S2 — break-glass logout is attributed to authority the actor did not hold

S-6 is confirmed. A continuity administrator during provider outage has no proven
guild membership, yet the primary audit capability column records `guild_member`.
That damages forensic reconstruction of session termination and defeats the schema
work that permits correct non-Discord attribution. Derive the value from trusted
session provenance and test both break-glass methods independently.

## Important security findings

### S3 — the shared WebAuthn bucket creates emergency lockout pressure

S-7 is confirmed. Options issuance and assertion verification consume the same
five-unit address bucket, so a success costs two and a local authenticator cancel
costs one. Coupled with indistinguishable retired passkeys, this can exhaust the
emergency path during an ordinary operator mistake. Splitting buckets is preferable
to resizing the coupled bucket because it makes each security policy explicit and
measurable. Keep per-account/per-credential verification controls independent.

### S4 — recovery audit loses the distinction between compromise signal and delay

S-9 is confirmed. Replayed and expired grants should remain indistinguishable to
the caller but not to investigators. Preserve the single conditional consume
statement. On zero rows, classify the already-hashed token with a read-only lookup
and audit a closed reason plus non-secret grant record UUID. Unknown tokens must
remain `unknown`; no token fragment or hash belongs in audit.

### S5 — provider health is a constant during the outage it claims to describe

S-4 is confirmed as an operational-security weakness. A loopback health endpoint
that says the identity provider is healthy must perform a bounded, side-effect-free
check with strict timeout and safe failure handling. If Discord offers no suitable
probe, use the least privileged documented endpoint and ensure no OAuth secret or
response content is exposed. A constant `true` is not an acceptable security
signal.

## Security controls that held

- Two distinct enabled credentials authenticated only at the intended HTTPS
  origin/RP binding while Discord was unavailable to the portal identity.
- A retired credential was refused without becoming an existence oracle.
- Cancellation and recovery failures used neutral caller presentation.
- Recovery grants were stored hashed, displayed once, consumed atomically, refused
  on replay, and refused after expiry.
- Sign-out invalidated the server-side session despite its incorrect audit
  capability.
- Continuity scope withheld member, Council, snapshot, folder-selection and apply
  authority in the guard tables and PostgreSQL-backed caller-matrix tests.
- The provider outage was isolated by service-account UID and independently shown
  not to affect the live bot identity.
- The evidence does not contain a token, assertion, challenge, cookie, credential
  ID, public key, or authenticator secret.

## Live-boundary completion

R-41 and R-46 should be observed before security readiness is confirmed. The
operator can make same-origin browser requests under the live break-glass session;
the browser supplies its HttpOnly cookie, and a CSRF token from an allowed page
lets the request reach capability authorization. Synthetic UUIDs are sufficient
because authorization refuses before object parsing/lookup. Record only response
status/body and correlation metadata. Never expose or copy the cookie or CSRF
value into the evidence record.

## Gate effect

No closed gate is reopened. A-05 and I-06 are already open. The Security Reviewer
should not provide A-05 criterion 10 confirmation until S1 and S2 are remediated
and re-reviewed, S3/S4 have accepted dispositions, and the remaining A-05
procedures—including the two POST route observations—are complete. Acceptance
remains with the maintainer.

