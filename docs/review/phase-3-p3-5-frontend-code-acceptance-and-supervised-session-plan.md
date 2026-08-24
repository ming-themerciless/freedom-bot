# P3.5 frontend code acceptance and supervised evidence session plan

**Date:** 2026-08-24

**Repository:** `/opt/discord-bots/freedom-bot`

**Decision:** frontend repository remediation accepted by Codex; supervised evidence remains pending
**Acceptance authority:** no Phase 3 gate decision taken

## 1. Decision and current state

Codex independently reviewed Gemini's final P3.5 frontend remediation for F-15
and F-17 and accepted the repository implementation. The review covered the
truthful no-JavaScript state, CSP-safe WebAuthn control, complete browser-side
ceremony workflow, strict R-07/R-08 refusal presentation, strict Base64URL
handling, safe redirect behavior, duplicate-activation protection, the VM-23
server-owned shell presentation, static-asset integrity and durable executable
tests.

No frontend code finding remains from G35/G36. This is an implementation-review
decision, not evidence that a real browser or authenticator has completed the
workflow.

The following remain **Not Run** and open:

- TC-UI-01: 320, 768 and 1280 CSS-pixel rendering without horizontal body overflow;
- TC-UI-02: 200% reflow without loss of content or function;
- TC-BG-02's browser/physical-authenticator path: break-glass succeeds while the
  Discord provider is unavailable;
- A-05's successful use criterion: the protected administrator's two enabled
  credentials are demonstrated against the intended RP ID and origin;
- the associated real-device portions of R-23.

Consequently F-15 and F-17 remain formally open as operational findings until
the supervised session below succeeds and its evidence is accepted. I-06,
A-05, A-06, R-23 and the Phase 3 gate are not closed by this document. Public
exposure and Phase 4 remain unauthorized.

## 2. Independent evidence already complete

On 2026-08-24 Codex independently obtained:

- `node --test tests/web/webauthn_client.test.mjs`: **50 passed**;
- `pytest -q tests/web/test_p3_5_webauthn_and_shell_presentation.py`: **9 passed**;
- **10,240** independent randomized Base64URL encode/decode probes, all passed;
- independent refusal probes for the exact closed vocabulary
  `origin_invalid`, `rate_limited`, `invalid`, `expired`, all passed;
- `sha256sum -c adapters/web/static/asset-integrity.sha256`: **4/4 OK**;
- `git diff --check`: clean.

Gemini additionally reported the sequential full verification set as 50 Node
tests, 2,286 web tests with 80 documented skips, 2,346 bot tests, 155 Foundry
tests, both manifests and both compilation passes clean. Codex had independently
run the complete web suite immediately before the final remediation at 2,285
passed and 80 skipped; the one added structural case was then run directly.

## 3. Supervised session prerequisites

Before starting, the Operations Owner resolves and records, without secrets:

1. the named isolated staging host/build and commit SHA;
2. the intended HTTPS origin and exact `WEB_WEBAUTHN_RP_ID`;
3. confirmation that the origin is not publicly exposed beyond its approved gate;
4. the protected administrator account and two enabled test credentials;
5. an operator-controlled browser and physical authenticator(s);
6. a safe way to make Discord unavailable to the portal for the TC-BG-02 check
   without affecting the live bot or real users;
7. rollback access through the host-local recovery procedure;
8. a synthetic/test identity only—no credential material, tokens, assertions,
   cookies, secrets or personal data in screenshots or notes.

If any prerequisite cannot be resolved, record **Blocked** or **Not Run** and
stop. Do not improvise against production.

## 4. Bounded execution checklist

### 4.1 Baseline

- Record UTC time, commit SHA, staging environment identifier, browser/OS and
  authenticator model at a non-sensitive level.
- Confirm the service and restricted health checks are healthy through the
  approved operator path.
- Confirm static asset hashes match the committed integrity manifest.
- Confirm both credentials are enabled through the protected operator/startup
  check without recording IDs, public keys or credential material.

### 4.2 TC-UI-01 and TC-UI-02

Using the real browser, visit representative anonymous, member, Council,
administrator, denial/error, emergency-access and sign-out views.

- At 320, 768 and 1280 CSS pixels, check for horizontal body overflow, clipped
  controls, unreadable navigation and unreachable content.
- At 200% zoom, repeat essential navigation, emergency-access and sign-out
  actions; verify no content or function is lost.
- Use keyboard only to traverse the skip link, navigation, WebAuthn control,
  recovery form and sign-out control; verify logical order and visible focus.
- Check supported and unsupported WebAuthn presentation if an unsupported
  browser/profile is available; otherwise record that branch as automated-only.
- Check the initial/no-JavaScript page separately: no usable dead security-key
  action, truthful explanation, and functional recovery form.
- Record Passed/Failed per viewport and state. Screenshots must contain only
  synthetic data and no browser developer-tool credential payloads.

### 4.3 A-05 and TC-BG-02

- Confirm the ceremony is running on the exact intended HTTPS origin/RP ID.
- With Discord-provider access deliberately unavailable to this isolated
  staging service, open emergency access.
- Activate **Use security key**, complete a real assertion, and confirm the
  response reaches exactly `/v1/admin/role-capabilities`.
- Confirm the resulting continuity-scoped shell exposes only the accepted
  break-glass destinations and provides a working POST sign-out control.
- Sign out and confirm the session no longer reaches protected routes.
- Repeat authentication with the second enrolled credential, then sign out.
- Exercise neutral user cancellation once and verify that the control becomes
  usable again without technical disclosure or automatic retry.
- Confirm no assertion, credential ID, challenge, session cookie or recovery
  token appears in the captured evidence.
- Restore the provider dependency and verify ordinary staging login/health.

Any unexpected route, authority, redirect, disclosure, failure to clear busy
state, failed sign-out, RP mismatch or inability to use either credential is a
failure. Stop exposure and return the finding to implementation/security review.

## 5. Evidence record required after the session

Append or create a dated results document containing:

- build/commit and named environment;
- UTC start/end time;
- operator and reviewer roles;
- browser, OS, viewport, zoom and authenticator descriptions;
- each checklist item as Passed, Failed, Blocked or Not Run;
- sanitized screenshots or observations where useful;
- confirmation that Discord unavailability was isolated and restored;
- confirmation that both credentials authenticated successfully, without their
  identifiers or material;
- confirmation that sign-out invalidated each session;
- deviations, failures, rollback actions and residual risks;
- explicit Security Reviewer and Operations Owner decisions;
- Peter's separate acceptance decision for A-05, R-23 residual disposition and
  the Phase 3 gate.

Do not close A-05, TC-BG-02, TC-UI-01/02, R-23, I-06 or the Phase 3 gate merely
because the session occurred. Their state moves only on recorded successful
evidence and the required authority's dated acceptance.
