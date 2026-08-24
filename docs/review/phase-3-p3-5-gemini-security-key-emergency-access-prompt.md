# Prompt for Gemini — P3.5 remediation F-15 and F-17: emergency access and the signed-in shell

> **NOT RELEASED — pending Codex independent and security-focused re-review.**
> The blocker that held this back is gone: the server-owned shell contract
> (C35-05/R35-17) is implemented, so the fields this prompt asks you to consume
> now exist and are named exactly in §4a. Do not act on this document until Codex
> has reviewed both the backend contract and this prompt.



**Raised:** 2026-08-23 by P3.5 (Claude), from the first browser use of a deployed
portal with two real WebAuthn credentials enrolled.

**Owner:** Gemini, as production frontend implementer (delivery plan §2, §5 P3.5).

**Backend contract owner:** Claude. **Review:** Codex, independent pass plus a
distinct security-focused pass. **Decision:** Peter Duscha.

**Classification: blocking.** A-05 cannot close and the portal cannot be exposed
until a passkey login actually succeeds in a browser.

---

## 1. What is wrong

With two real credentials enrolled and the portal deployed, `GET /v1/auth/emergency`
renders this and nothing more:

```html
<section data-section="webauthn" class="auth-section">
  <h2>Security key</h2>
  <p>Present an enrolled security key.</p>
</section>
```

There is no button, no form and no script. `adapters/web/static/` contains exactly
three files — the stylesheet, the emblem and vendored HTMX — so there is **no
application JavaScript at all**, and `navigator.credentials.get()` cannot be driven
by HTMX. Routes R-07 and R-08 exist, are service-tested and are unreachable from a
browser.

The consequence: the recovery grant, designed as the last resort for when every
passkey is lost, is the **only** working emergency route, and the enrolled
credentials cannot be used.

## 2. This is a scope gap, not an implementation failure

The P3.4 Step 4 prompt said, in terms:

> Do not invent passkey/WebAuthn JavaScript in this step. Existing R-07/R-08
> remain backend contract routes, not authorization for new script here.

That instruction was correct for its step. No later package was ever given the
client half, and no test asks whether a human can complete the flow — P3.1 proves
the routes by posting synthesized payloads, P3.4 proves the template renders
safely, and both pass with the browser half absent (finding F-16). **This prompt
is the missing commission.** Nothing here criticises P3.4.

## 3. Read completely before acting

1. `.agents/AGENTS.md` and `CLAUDE.md`
2. `docs/contracts/phase-3-route-authorization-contract.md` — R-06, R-07, R-08,
   R-09, and §1.2's mount and URL grammar
3. `docs/contracts/phase-3-view-model-contract.md` — VM-04 `EmergencyLoginView`
4. `docs/review/phase-3-p3-4-gemini-step-04-auth-system-prompt.md` — the accepted
   requirements for this page, all of which still stand
5. `adapters/web/templates/emergency.html`, `adapters/web/templates/base.html`
6. `application/web/breakglass.py` — `begin_assertion`, `complete_assertion`
7. `adapters/web/app.py` — the R-07 and R-08 handlers
8. `docs/review/phase-3-p3-5-readiness-and-execution-plan.md` §14, findings F-15/F-16

## 4. Objective

**Two commissions, both the missing client half of something already built.**

**F-15.** Make a person with an enrolled passkey able to sign in at
`/v1/auth/emergency`, using only the two accepted routes that already exist.

**F-17 — the signed-in shell. The backend half is done.** The typed shell,
its caller-state matrix, the logout token rule and the reference header are all
implemented and tested (C35-05/R35-17, VM-23, TC-SHELL-01…11). What remains for
you is **styling and any presentation refinement** of the frame — the sign-out
control's appearance, focus and reduced-motion behaviour, and the responsive
treatment of a navigation that now varies in length. **Do not re-derive the
matrix.** Its original description follows for context:

 `base.html` always includes
`includes/header.html`, which renders the same three links — Characters,
Emergency Access, **Login** — to every caller on every page, with no conditional
on session state. On the deployed portal this means a signed-in administrator is
shown "Login", **no template anywhere contains a logout control** (`grep -rln
logout` over the corpus returns nothing, while `POST /v1/auth/logout` exists as
accepted route R-05), and no privileged surface — administration, Council,
reconciliation, audit — is linked from anywhere, so it is reachable only by
typing a URL.

**This is a scope gap too, not a defect of P3.4.** No P3.4 prompt asked for a
capability-aware header or a logout control; they were never commissioned. As
with F-15, this prompt is the commission.

Deliver: a header that reflects the caller — a logout control that posts to R-05
with its CSRF token when there is a session, the accepted links the caller's
capabilities actually permit, and the anonymous shell unchanged for anonymous
callers. Link only what the caller may reach: the header must not become an
enumeration oracle, and a link the caller would be refused must not be rendered.

## 4a. The shell fields you consume — they exist; do not invent any

Every full-page render receives `shell` alongside `view`. It is built at the
request boundary by `RequestAuthority.render()` from the accepted session and
capability authority. **You consume it. You never compute it, extend it, or work
around it.**

```text
shell.authenticated        bool
shell.navigation           tuple[ShellLink, ...]   already filtered to this caller
shell.logout_csrf_token    str | None              present only for a valid session
shell.logout_available     bool                    authenticated and token present
shell.home_href            str                     the brand/home destination
shell.current              ShellNav | None         at most one; resolved server-side

link.id                    ShellNav                closed vocabulary
link.label                 str
link.href                  str
```

`ShellNav` values: `login`, `emergency`, `characters`, `council_characters`,
`snapshots`, `role_capabilities`, `identities`.

Rules that are not negotiable, because each is a control rather than a style:

1. **Render `shell.navigation` as given.** Do not filter it, reorder it by
   capability, add a destination, or hide one. It is already exactly what this
   caller may reach; second-guessing it in a template is how the two authorities
   drift apart.
2. **Never infer identity or authority.** No reading cookies, no parsing URLs for
   privilege, no `view`-sniffing to decide what a caller is. If you find yourself
   wanting a fact the shell does not carry, stop and ask for it.
3. **Mark the current page from `shell.current` only.** Exactly one destination is
   ever current; the resolver guarantees it. Do not re-derive it from the path.
4. **Logout is `POST /v1/auth/logout` with `shell.logout_csrf_token`.** Render it
   only when `shell.logout_available`. Never a link, never a GET, never a token
   you obtained from anywhere else.
5. **The brand/home link is `shell.home_href`.** Never a literal path. It hard-coded
   `/v1/characters` before, which R-20 refuses to an administrator-without-Council
   and to continuity scope — the frame offered a door that answers 403.
6. The existing header at `adapters/web/templates/includes/header.html` already
   does all of this. It is the reference, not a draft to replace.

## 5. The exact protocol

**Step 1 — options.** `POST /v1/auth/emergency/webauthn/options`, no body required,
`application/json`, same-origin. It answers `200` with the standard WebAuthn JSON
produced by `webauthn.options_to_json`:

- `challenge` — **base64url string**, must be decoded to an `ArrayBuffer`;
- `allowCredentials` — **deliberately empty**. It is not an oversight and must not
  be worked around: a populated list would disclose which credentials exist to an
  unauthenticated caller. An empty list means the browser offers the user's own
  discoverable credentials, which is why registration used `residentKey: preferred`;
- `userVerification` — `"required"`;
- `rpId`, `timeout`.

**Step 2 — the browser.** `navigator.credentials.get({ publicKey: … })` with the
decoded values.

**Step 3 — verify.** `POST /v1/auth/emergency/webauthn/verify` with the assertion
as JSON, every `ArrayBuffer` field base64url-encoded: `id`, `rawId`, `type`,
`response.clientDataJSON`, `response.authenticatorData`, `response.signature`,
`response.userHandle` (may be null), `clientExtensionResults`.

**Step 4 — outcome.** `200` answers `{"status": "ok", "redirect": "/v1/admin/role-capabilities"}`
and sets the session cookie; navigate to `redirect`. A failure answers a JSON
refusal carrying a closed code and a correlation UUID; render **only** those,
exactly as the page already renders the recovery form's failures.

## 6. Requirements

1. **No inline script, no event-handler attributes, no `hx-on:`.** TC-SEC-10
   asserts zero of each across the whole template corpus. The script is a served
   file under `/static/js/`, referenced the way `base.html` already references the
   stylesheet and HTMX — a content-hashed filename, absolute `/static/…` path.
2. **Same-origin only.** CSP is `script-src 'self'`; no CDN, no remote font, no
   import from anywhere else, no new dependency, no npm, no bundler, no build step.
3. **Progressive enhancement is preserved.** With JavaScript disabled the page must
   remain exactly what it is today: the recovery form works, and the security-key
   section states plainly that it is unavailable rather than showing a dead button.
   Feature-detect `window.PublicKeyCredential`; `view.webauthn_supported_hint` is a
   static configuration hint, not a browser capability.
4. **No enumeration.** The page must not reveal, before or after a failure, whether
   an account exists, whether any credential is enrolled, any nickname, or whether
   a recovery grant is outstanding. Every failure renders from the accepted closed
   code and the correlation id, and nothing else.
5. **No credential material anywhere.** Never render, log, store or place in the
   DOM a public key, a raw assertion, a signature or a challenge beyond the
   in-flight request. Nothing in `localStorage` or `sessionStorage`.
6. **Cancellation is normal.** A user dismissing the platform prompt (`NotAllowedError`)
   is an ordinary outcome: restore the control and say nothing alarming. Do not
   retry automatically.
7. **The asset manifest is updated.** Add the new file to
   `adapters/web/static/asset-integrity.sha256`; `sha256sum -c` must pass.
8. **Accessibility.** The control is a real `<button>`, keyboard reachable, with a
   visible focus indicator and an accessible name. Status changes are announced —
   the page already has an `role="alert"` pattern; reuse it. Respect
   `prefers-reduced-motion`; add no spinner that ignores it.

## 7. Allowlist — nothing else may change

| Path | Change |
|---|---|
| `adapters/web/templates/emergency.html` | add the control and its status region |
| `adapters/web/templates/includes/header.html` | make the shell reflect the caller (F-17) |
| `adapters/web/static/js/<name>.<hash>.js` | **new** |
| `adapters/web/static/asset-integrity.sha256` | add the new asset |
| `adapters/web/static/css/freedom-blades.<hash>.css` | only if the control needs styling; rehash and update `base.html` and the manifest together |
| `adapters/web/templates/base.html` | only if the stylesheet hash changes |
| `tests/web/…` | new and amended tests |

**You may not change** any route, view model, handler, application service,
persistence, migration, configuration, authentication or authorization logic. If
the client half genuinely cannot be built against the accepted contracts, **stop**
and return the specific obstacle to Claude — do not adjust a backend contract to
suit the frontend.

## 8. Test requirements

1. The rendered page contains a real, enabled, keyboard-reachable control naming
   the security-key flow.
2. With JavaScript absent, the recovery form still submits and the page still
   renders — the existing no-JS evidence must not regress.
3. The corpus guards still pass: zero `|safe`, zero inline `<script>`, zero `on*`
   attributes, zero `hx-on:`, zero remote origins, zero `design-prototype`
   references.
4. The new asset is in the manifest and `sha256sum -c` passes.
5. A structural test asserts the script references **only** R-07 and R-08 and no
   other endpoint.
6. A test asserts no failure path renders any account, nickname, credential or
   grant-state string — only a closed code and a correlation UUID.
7. **F-17:** the anonymous shell is unchanged for an anonymous caller; a signed-in
   caller is never shown "Login"; the logout control posts to R-05 and carries a
   CSRF token; and, per capability, the header links exactly what the accepted
   §5.2 matrix permits that caller and nothing it refuses — a member is not shown
   the administration link, and an administrator is not shown My Characters.

Note honestly what your tests **cannot** prove: none of them exercises a real
authenticator. The browser half of TC-BG-02 stays **Not Run** and is closed by
Peter's supervised login on the deployed portal, not by this work. Do not report
it as passing.

## 9. Required verification

```bash
TEST_DATABASE_URL=postgresql+psycopg:///freedom_test /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
TEST_DATABASE_URL=postgresql+psycopg:///freedom_test /opt/discord-bots/freedom-bot/venv/bin/python -m pytest -q -rs tests/test_*.py
sha256sum -c adapters/web/static/asset-integrity.sha256
sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256
/opt/discord-bots/venv-web/bin/python -m compileall -q adapters application domain tests
git diff --check
```

**Run the two suites sequentially, never at the same time.** They share the one
disposable `freedom_test` database, and running them concurrently produces dozens
of false failures.

Report every command and its literal result. Do not claim a check passed unless it
was run.

## 10. Stop conditions

Stop and hand back rather than proceeding if:

- the flow appears to need a route, view model or backend change of any kind;
- `allowCredentials` being empty appears to be a problem to solve rather than a
  control to respect;
- a test that passed before your change fails after it; or
- satisfying this prompt would require an inline script, a remote origin, a new
  dependency or a build step.

## 11. Checkpoint and stop

Deliver the diff, the test results, the manifest verification and a plain
statement of what remains unproven. Do not self-accept, do not close F-15, do not
mark A-05 or TC-BG-02 satisfied, and do not touch the deployed host.
