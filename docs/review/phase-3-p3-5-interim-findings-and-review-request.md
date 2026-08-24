# P3.5 interim findings and independent-review request

**Date:** 2026-08-23 · **Author:** Claude, P3.5 backend/integration Technical Lead

**Status:** **Interim. P3.5 is not complete and no gate decision is requested.**
This document exists because the first deployed run of the portal produced
findings that a reviewer should see now rather than at submission.

**Reviewer:** Codex — independent implementation pass and a distinct
security-focused pass. **Decision authority:** Peter Duscha, alone.

---

## 1. Why this document exists now

The P3.5 plan was approved at SG-1 on 2026-08-23. Peter then authorized and
performed the host build, and the portal ran under its restricted service account
for the first time in the project's history.

Three of the four defects below **could not have been found by the test suite**,
and were found within the first hour of the portal actually running. That is the
substance of RAID **I-06** — "staging-class evidence cannot be produced because
staging does not exist" — and it is now evidenced rather than asserted.

Every suite was green before and after. Nothing here was caught by a test.

## 2. Environment these findings come from

| Fact | Value |
|---|---|
| Host | the shared production host (OD-22), alongside three live Foundry instances and the Discord bot |
| Address | `freedom-blades-test.rpgworld.org`, Cloudflare-proxied, temporary |
| Environment marker | `WEB_ENVIRONMENT=staging` |
| Database | `freedom_staging`, separate from `freedom_dev` and `freedom_test`; schema at revision `0013` |
| Runtime role | `freedomweb`, non-superuser, peer authentication, restricted grants applied |
| Discord | a **separate** test application and test guild; no live community identity involved |
| Data | none. No real player data, no production backup, no snapshot artifact |
| Exposure | password-gated at the proxy; not open to the internet |
| Credentials | two real WebAuthn credentials enrolled — the first in the project's history |

## 3. Findings, in the order a reviewer should weigh them

### F-15 — blocking — the passkey break-glass login cannot be completed in a browser

`emergency.html` renders the security-key section as a heading and one sentence,
with no control. `adapters/web/static/` ships three files — stylesheet, emblem,
vendored HTMX — and **no application JavaScript**, so `navigator.credentials.get()`
cannot be invoked. R-07 and R-08 exist, are service-tested, and are unreachable
from a browser. The recovery grant, designed as the last resort for when every
passkey is lost, is the only working emergency route.

**It is a scope gap, not an implementation failure.** The P3.4 Step 4 prompt
instructed: *"Do not invent passkey/WebAuthn JavaScript in this step. Existing
R-07/R-08 remain backend contract routes, not authorization for new script here."*
That was correct for that step, and no later package was commissioned to supply
the client half.

**Disposition:** routed to Gemini —
`phase-3-p3-5-gemini-security-key-emergency-access-prompt.md`. Frontend-only;
crosses no contract. **A-05 cannot close and the portal cannot be exposed until a
passkey login succeeds in a browser.**

**Reviewer question:** is the empty `allowCredentials` non-enumeration property
preserved by the remediation, and does the failure rendering remain free of any
account, credential or grant-state signal?

### F-14 — blocking, **fixed and re-tested** — the restricted role could not start the portal

The portal refused every start with S-14: *"WEB_DATABASE_URL could not be queried
for its Alembic revision."* The runtime-grants template grants every table in the
ORM metadata and **`alembic_version` is not in that metadata**, so the restricted
role had no `SELECT` on the one table S-14 must read. The documented restricted-role
deployment could therefore never have started, in staging or in production.

**Fix:** a separate, documented section of `infra/postgresql/runtime-grants.sql.tmpl`
granting `SELECT` only — migrations run as the schema owner, and a runtime role
able to write that table could misreport which schema the next startup is serving.
`REVOKE ALL … FROM PUBLIC` and `FROM __APP_ROLE__` precede it, matching the file's
existing O-1 normalisation.

**Tests:** the two metadata equalities now exclude that one non-application table
with a stated reason, and a new regression test
`test_the_runtime_role_can_read_the_schema_version_and_cannot_write_it` asserts
`SELECT` is granted and the three writing bands are not. **Falsified:** with the
grant line removed the new test fails; restored, it passes. `tests/test_runtime_grants.py`
and `tests/test_runtime_grants_live.py` — **57 passed**.

**Reviewer question:** is a separate section the right shape, or should
`alembic_version` be added to the metadata-driven lists and the equalities widened?

### F-17 — important — the shell is static, and there is no way to sign out

`base.html` always includes a header that renders the same three links to every
caller: Characters, Emergency Access, **Login**. A signed-in administrator is shown
"Login". **No template contains a logout control** — `grep -rln logout` over the
corpus returns nothing — while `POST /v1/auth/logout` exists as accepted route
R-05. No privileged surface is linked from anywhere.

**A second scope gap, like F-15:** no P3.4 prompt asked for a capability-aware
header or a logout control. No authorization boundary is weakened — every route
still authorizes server-side — but a portal with no logout control will not satisfy
the delivery plan's session revocation expectations at the gate, and the
administration surface is unreachable without typing a URL.

**Disposition:** added to the Gemini prompt beside F-15.

**Reviewer question:** the remediation must link only what the caller may reach, so
the header does not become an enumeration oracle. Is that the right rule?

### F-13 — minor — `/healthz` fails closed on a permissions fault

`build_health_view` calls `settings.kill_switch_file.exists()` unguarded, and
`Path.exists()` raises `PermissionError` rather than returning `False` when the
process cannot traverse the directory. A mis-permissioned kill-switch directory
therefore turns the health endpoint into a `500` instead of a health report saying
`kill_switch: false`. Observed directly; the safe-error boundary behaved correctly
and leaked nothing but a correlation id.

**Not fixed here** — `application/web/startup.py` is accepted P3.1/P3.3 surface.
Raised because a health endpoint that fails closed on a permissions fault is least
useful exactly when an operator most needs it.

### F-16 — important — nothing asserts that a human can complete break-glass login

P3.1 proves R-07/R-08 by posting synthesized payloads. P3.4 proves the template
renders, escapes and carries no inline script. Both pass with the browser half
absent, which is how F-15 survived two gates. The traceability must carry TC-BG-02's
browser half as **Not Run**, beside TC-SEC-07's, rather than inheriting a pass from
the service-level cases.

## 4. Deployment artifacts authored, and why they did not exist

| Finding | Artifact |
|---|---|
| F-2 — no `freedom-web` unit template existed at all | `infra/systemd/freedom-web.service.tmpl` |
| F-3 — no proxy site block or body limits were defined | `infra/caddy/freedom-blades-test.caddy` |
| F-7 — the enrollment tool pointed at a registration page in `docs/operations/` that had never been written, so its two arguments could not be produced | `infra/ceremony/passkey-registration.html`, `tools/webauthn_registration.py` |
| — | `tools/portal_server.py`: `create_app()` requires exactly one configuration authority and refuses a no-argument call, so an ASGI `--factory` cannot call it directly |
| — | `infra/staging/setup-portal-host.sh`, `enable-test-site.sh`, `portal-run.sh` |

`tools/webauthn_registration.py` verifies the full registration response through
`webauthn.verify_registration_response` and **refuses when the ceremony's
relying-party identifier does not match the running configuration** — the F-8 trap,
where a credential created at the wrong address enrols cleanly and can never
authenticate.

Its stated limitation, for the security pass: the challenge is the page's own,
carried with the response, because a server-issued challenge would require a route
and the absence of an enrollment route is the control (TC-BG-10). What is proved is
that the response is internally consistent and genuinely from an authenticator, not
that it is fresh. Compensating: the operator performs the ceremony themselves and
must hold host authority to spend its result, and replaying a response only
re-registers the same public key.

## 5. Host observations outside this package's authority

| # | Observation |
|---|---|
| F-11 | `/etc/ssl/rpgworld/cloudflare.key` — the origin private key shared by all four sites — was mode `0644`, world-readable. Reported to the Operations Owner and corrected to `0640 root:caddy`. **The file was never read**; the finding came from directory metadata. Note the correct mode is group-readable, not owner-only: Caddy runs as `caddy` |
| F-10 | TLS is a Cloudflare **Origin CA** wildcard, trusted by Cloudflare alone, so the DNS record must stay proxied. Consequence: without a rewrite the right-most `X-Forwarded-For` entry is Cloudflare's address and N-34 would hand the N-30/N-31 limiter one bucket for the entire internet. The site block sets it from `CF-Connecting-IP`. **Residual:** a request reaching the origin directly could spoof that header; restricting the origin to Cloudflare's ranges is a deployment-gate item |
| F-12 | The pre-existing block for the live address injects its own CSP and `X-Frame-Options`. The portal owns those headers and omits `X-Frame-Options` deliberately. The new block adds none |
| F-9 | The live address currently serves `design-prototype/` statically. Replacing it is a cutover step with a stated consequence |

## 6. Decisions taken and recorded

D-a…D-j in `phase-3-p3-5-readiness-and-execution-plan.md` §0.2. Two are worth a
reviewer's attention because they were **reversed by observation**:

- **D-i** — Cloudflare mode. Recommended DNS-only; reversed on discovering the
  Origin CA certificate (F-10).
- **D-h → D-j** — test address. The Operations Owner chose the production hostname
  and the application refused it: **S-02**, *"is the accepted production origin but
  this process is not production."* Testing moved to a separate hostname. The
  control worked exactly as designed, against a decision two humans had agreed.

## 6a. The authorization boundary, observed on the deployed portal

Not a finding — the first live confirmation that the accepted §5.2 matrix is
enforced in both directions, by a real Discord identity holding real roles:

| Observation | Accepted matrix | Result |
|---|---|---|
| Discord OAuth login completed; session created, `auth.login.succeeded` audited | — | works |
| Discord reported all three test-guild roles; only the protected administrator mapping existed | — | capabilities resolved to `{platform_administrator}` alone |
| My Characters (R-20) refused the administrator | `A = ✗ 403` | **refused as specified** |
| Role capabilities (R-32) admitted the administrator | `A = ✓` | **admitted as specified** |
| Administrator mapped the Council role through R-33 | administrator-only | succeeded, `role_capability.mapped` audited |

Administrator did not imply Council: the Council capability existed only once an
administrator deliberately created the mapping. That is the invariant the design
rests on, and it held against a live identity rather than a fixture.

## 7. What is not claimed

- No RAID item is closed. **I-06, A-05 and A-06 remain open; R-23 remains active.**
- A-05 has its **first real enrollment** — two credentials on a deployed host — and
  that is the rehearsal, not the assumption's validation: the credentials are bound
  to the test address's relying-party identifier and cannot authenticate against
  production (F-8), and no passkey login has yet succeeded (F-15).
- No browser, device, assistive-technology or performance evidence exists.
- No formatter, linter or type checker is configured in this repository; recorded
  as unavailable, never as passed.
- No Phase 3 gate decision is requested by this document.

## 8. What is asked of the reviewer

1. The F-14 fix and its regression test: right shape, right band, right scope.
2. The F-15 remediation prompt: does it preserve non-enumeration and safe failure,
   and is the allowlist tight enough?
3. `tools/webauthn_registration.py`: the challenge limitation in §4, and whether
   refusing on a relying-party mismatch is the right control placement.
4. The new deployment artifacts, particularly the `X-Forwarded-For` rewrite against
   N-34's exactly-one-hop rule.
5. F-13: whether the health endpoint's failure mode warrants a P3.1 change.
6. Whether any of these findings should reopen a closed gate rather than being
   carried as P3.5 remediation.
