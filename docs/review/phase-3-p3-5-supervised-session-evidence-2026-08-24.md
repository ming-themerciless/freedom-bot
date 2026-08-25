# P3.5 supervised session evidence — 2026-08-24

**Repository:** `/opt/discord-bots/freedom-bot`
**Procedure:** `docs/review/phase-3-p3-5-frontend-code-acceptance-and-supervised-session-plan.md` §4
**Status:** **Complete for what it covers. No RAID item closed. No gate decision
requested.** The §4 procedure ran in full, and SP-21 and the observable part of
SP-22 were added after it closed.

This document is filled only by checks that actually ran. Every row that has not
been executed says **Not Run** and stays that way until it is.

**Reconciled 2026-08-24 (independent review finding F4).** The document was
written progressively and kept several pre-completion states after the work they
described had finished: §1 left the browser and authenticators Not Run while §3
and the A-6 table named both, §4 still opened "Not started" above a table of
Passed rows, §8.2 listed criterion 8 as Not Run after SP-21 evidenced it, and
§8.4 tallied six findings after nine had been raised. None of that invalidated a
single timestamped observation, and none of it is corrected by *changing* one:
every fact below is drawn from elsewhere in this same document, and the two
things that could only come from the host — an exact session-end timestamp and
the SP-21 grant record UUIDs — are marked **outstanding** rather than filled in.

---

## 1. Session identity

| Field | Value |
|---|---|
| Session start (UTC) | 2026-08-24T08:29:24Z |
| Session end (UTC) | 2026-08-24 — **exact end time still outstanding**, with a raised lower bound. §4.2 and §4.3 ran in two sittings, suspended 09:33Z and resumed the same day. SP-21's expiry refusal at 21:02:45Z was the latest timestamp this document recorded; a host-local read of `audit_events` on 2026-08-24 (below) shows four later rows — two ordinary `discord_oauth` login/logout pairs at **21:30:04Z, 21:30:07Z, 21:30:18Z and 21:30:43Z**, after the deliberate provider outage had been restored — so the lower bound is now **21:30:43.196749Z**. Whether those four rows are the session's closing normal-login check or unrelated later use is not something the audit stream states, so this remains a **lower bound and not the end**. The accepted evidence rules ask for exact timestamps, and only the Operations Owner can supply this one |
| Commit under test | `0c95e72bc9a3c274b5683161b17ceb0fe53f8902` ("Complete Phase 3.5 portal remediation package", 2026-08-24T01:31:54Z) |
| Branch | `docs/platform-plan` |
| Working tree | clean (`git status --short` empty) |
| Environment identifier | `staging` (reported by `/healthz`) |
| Intended origin | `https://freedom-blades-test.rpgworld.org` (Caddy site block → `127.0.0.1:8001`) |
| `WEB_WEBAUTHN_RP_ID` | **Not confirmed** — held in `/etc/freedom-web/portal.env`, not readable by the review account and not read |
| Operator | Peter Duscha (Operations Owner) |
| Reviewer | Claude (working Technical Lead) |
| Browser / OS | **Chrome on macOS 26**, for every observation in §3, §4, SP-21 and SP-22. Taken from §3's and §4's own records rather than newly reported. This is a single browser on a single platform, which is why R-23 stays active (§8.2) |
| Authenticator(s) | **Two enabled platform authenticators.** The portal's **credential-record nicknames** are `puppetmaster` and `puppetphone`, plus the retired pair `macbook` and `iphone` presented once and refused. Nicknames only, which §9.2's A-1 row permits; no credential id, public key or COSE material was ever selected by any query in this session. See the A-6 evidence table |
| Authenticator description | **Not Recorded.** A truthful non-sensitive description — built-in platform authenticator plus device class — can only come from the Operations Owner, and it was not captured while the session ran. The four nicknames above are **not** it: §8.4 of this document records that they are not what the platform passkey UI displays, so no authenticator model or device may be inferred from them. This row stays **Not Recorded** until the Operations Owner supplies one |

---

## 2. §4.1 Baseline

| # | Check | Result | Evidence |
|---|---|---|---|
| B-1 | UTC time, commit SHA, environment recorded | **Passed** | §1 above |
| B-2 | Working tree clean; no whitespace defects | **Passed** | `git status --short` empty; `git diff --check` clean |
| B-3 | Static asset hashes match the committed manifest | **Passed** | `sha256sum -c adapters/web/static/asset-integrity.sha256` → **4/4 OK** (css, token png, `webauthn-emergency.9e0c073e9e6c.js`, htmx vendor) |
| B-4 | Repository-level ceremony proofs re-run independently | **Passed** | `node --test tests/web/webauthn_client.test.mjs` → **50 passed, 0 failed**; `pytest -q tests/web/test_p3_5_webauthn_and_shell_presentation.py` → **9 passed**; `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' pytest -q tests/web/test_break_glass_login.py` → **17 passed** |
| B-5 | Service healthy through the approved operator path | **Passed** | `GET http://127.0.0.1:8001/healthz` (Host `freedom-blades-test.rpgworld.org`) → `200` · `{"status":"ok","checks":{"database":true,"migrations":true,"artifact_store":true,"worker_heartbeat":true,"expired_leases":true,"identity_provider":true,"kill_switch":true},"version":"phase-3-p3.1","environment":"staging"}` |
| B-6 | **The deployed process serves the commit under test** | **Passed after operator restart — see §6 S-1** | Before: `GET /v1/auth/emergency` → **500**. Operator restarted `freedom-web.service` at **2026-08-24T08:36:54Z** (PID 3436943). After: → **200** |
| B-8 | Deployed page carries the remediated WebAuthn control | **Passed** | Served markup contains `<button type="button" id="webauthn-signin-btn" … hidden>Use security key</button>` plus `#webauthn-desc`, `#webauthn-fallback-msg`, `#webauthn-unsupported-msg`, `#webauthn-status-msg` |
| B-9 | Deployed no-JavaScript state is truthful | **Passed** | The button ships `hidden`; the visible default text is "Security key sign-in requires browser script support. Use the recovery grant below if JavaScript is disabled."; the unsupported message ships `hidden`; the recovery form is a real `<form method="post" action="/v1/auth/emergency/recovery">` with a `token` field and a submit control |
| B-10 | CSP admits the external client and forbids inline script | **Passed** | `content-security-policy: default-src 'self'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'; form-action 'self'; img-src 'self' data:; script-src 'self'; style-src 'self'`. Both scripts are external (`/static/js/webauthn-emergency.9e0c073e9e6c.js`, htmx vendor); no inline `<script>` on the page |
| B-7 | Both credentials enabled via the protected operator check | **Passed** | Operator ran `sudo bash /opt/discord-bots/freedom-bot/infra/staging/portal-run.sh -m tools.webauthn_enrollment list --operator "Peter Duscha"` → **`Enabled credentials: 2 (minimum 2)`**. Record UUIDs and nicknames deliberately not transcribed |

---

## 3. §4.2 TC-UI-01 / TC-UI-02 — responsive, zoom, keyboard, no-JavaScript

**Executed in full 2026-08-24, operator Peter Duscha, on the deployed staging
service after the S-1 restart.** **All seven required views** were observed at 320,
768 and 1280 CSS pixels and at 200% zoom. The member and Council views were taken
last, under an ordinary Discord session, because a break-glass session cannot reach
them at all — which is A-4 working, not an obstacle.

**Operator's closing observation, verbatim:** "I checked all pages. They all worked
perfect (resizing and zoom)."

**TC-UI-01 and TC-UI-02 are satisfied at the browser-observation level**, for one
browser and one platform: Chrome on macOS 26. They are **not** evidence for other
engines, and TC-UI-08's device matrix and TC-UI-09's screen-reader traversal remain
separate rows — the latter accepted as permanently Not Run for Phase 3 under
decision D-f, with R-23 staying active.

Operator environment: **Google Chrome on macOS 26**, the Operations Owner's own
workstation, against `https://freedom-blades-test.rpgworld.org` through the proxy
password gate. Exact Chrome build not recorded.

| Item | 320px | 768px | 1280px | 200% zoom |
|---|---|---|---|---|
| Anonymous view (`/v1/login`) | **Passed** | **Passed** | **Passed** | **Passed** |
| Member view (`/v1/characters`) | **Passed** | **Passed** | **Passed** | **Passed** |
| Council view (`/v1/council/characters`) | **Passed** | **Passed** | **Passed** | **Passed** |
| Administrator view (`/v1/admin/role-capabilities`) | **Passed** | **Passed** | **Passed** | **Passed** |
| Denial / error view (`?failure=invalid`) | **Passed** | **Passed** | **Passed** | **Passed** |
| Emergency-access view (`/v1/auth/emergency`) | **Passed** | **Passed** | **Passed** | **Passed** |
| Sign-out view | **Passed** | **Passed** | **Passed** | **Passed** |

**On the administrator and sign-out views (observed while holding a break-glass
session):** "narrow, medium, wide, 200% looks good, nothing breaks or runs off
edges." The sign-out view is the anonymous sign-in page, which the operator
reached by signing out and which was independently checked at all three widths and
at 200% as the anonymous view row above; it is marked Passed on that basis and a
reviewer may disagree with the equivalence.

**Operator's observation on the emergency-access view, verbatim:** "Buttons stay basically the same when I
change the window (they get slightly narrower and I can only shrink it to about
100px but that's fine by me). 200% makes everything bigger. Tabs work fine."

The reported floor of roughly 100 CSS pixels is well below the 320 the criterion
requires, so the 320 column rests on a width narrower than the one specified, not
on an approximation of it. No horizontal body overflow, clipped control or
unreadable navigation was reported at any width.

| # | Check | Result |
|---|---|---|
| U-1 | No horizontal body overflow, no clipped controls, no unreachable content at each viewport | **Passed** on all seven views. No horizontal overflow, clipping or unreadable navigation reported at any width |
| U-2 | 200% reflow loses no content or function; navigation, emergency access and sign-out still work | **Passed** on all seven views, including emergency access and a keyboard-actuated sign-out under a live session |
| U-3 | Keyboard-only traversal: skip link → navigation → WebAuthn control → recovery form → sign-out, logical order, visible focus | **Passed, both halves.** On the emergency-access view the operator reports "Tabs work fine", with focus resting on the usable elements and looking "like with every other website" — a visible indicator. On the continuity shell, holding a live break-glass session, he reached the **Sign out** control by Tab and actuated it with Enter, using no mouse. The POST sign-out control is therefore keyboard-operable, not merely keyboard-reachable |
| U-4 | Unsupported-WebAuthn presentation observed, or recorded as automated-only | **Automated-only**, as the plan permits. Chrome on macOS 26 supports WebAuthn, and no unsupported browser or profile was available. The `#webauthn-unsupported-msg` branch is covered by the Node suite (B-4) and by served markup (B-9), never by a real unsupported browser |
| U-5 | No-JavaScript page: no dead security-key action, truthful explanation, working recovery form | **Passed** for the first two criteria, observed in a real scriptless browser. Operator disabled JavaScript in Chrome, reloaded `/v1/auth/emergency`, and reports that where the button would be the page instead reads "Security key sign-in requires browser script support. Use the recovery grant below if JavaScript is disabled." No dead control appeared. **The recovery form was not submitted** — exercising it needs a host-local recovery grant, which is A-05 criterion 8 and a separate procedure; the form's presence is structural only (B-9). This is the branch F-15 lived in, and it is now observed rather than inferred |

---

## 4. §4.3 A-05 / TC-BG-02 — break-glass ceremony

**Executed in full 2026-08-24**, operator Peter Duscha present (SG-3), after the
S-1 restart that B-6 records. Every row below is Passed; none Failed; none was
skipped. The "Not started" note that stood here until the F4 reconciliation was
written before the sitting and never revised.

| # | Check | Result |
|---|---|---|
| A-1 | Ceremony runs on the exact intended HTTPS origin and RP ID | **Passed by demonstration.** A WebAuthn assertion only verifies when the browser's origin matches the server's expected origin and the credential's RP ID matches the server's configured `WEB_WEBAUTHN_RP_ID`. The ceremony succeeded from `https://freedom-blades-test.rpgworld.org`, so both matched. The configured value itself was never read — it lives in `/etc/freedom-web/portal.env`, which the review account cannot read — and it did not need to be: the authenticator enforced the binding |
| A-2 | Discord provider deliberately unavailable to this isolated service | **Passed** — see A-2 evidence below |
| A-3 | **Use security key** completes a real assertion; response reaches exactly `/v1/admin/role-capabilities` | **Passed** — first credential. Real passkey ceremony in Chrome on macOS 26, against `https://freedom-blades-test.rpgworld.org`, with Discord unreachable to the portal (A-2). Operator reports the address bar reading exactly `https://freedom-blades-test.rpgworld.org/v1/admin/role-capabilities`. Nothing unexpected was asked of the operator |
| A-4 | Continuity shell exposes only accepted break-glass destinations | **Passed.** Operator read off the navigation unprompted — the expected list was deliberately withheld from him beforehand so that he reported his screen rather than matched an answer. Offered: **Role capabilities**, **My account**, **Sign out**. Withheld: **Characters**, **Council characters**, **Snapshots**. That is exactly `application/web/shell.py:241-271` for a continuity-scoped caller: `IDENTITIES` (R-35) plus `ROLE_CAPABILITIES` (R-32), with the `not continuity_scoped` branch — R-20/R-21, R-22 and R-40 — correctly skipped |
| A-5 | POST sign-out control works; session no longer reaches protected routes | **Passed** — first credential. Sign-out returned the operator to the sign-in page. Re-navigating directly to `https://freedom-blades-test.rpgworld.org/v1/admin/role-capabilities` also returned the sign-in page rather than the protected content, so the session was invalidated server-side and not merely cleared from view |
| A-6 | Second enrolled credential authenticates, then signs out | **Passed, re-run under a genuine outage.** The 09:36:26Z ceremony had run *after* the provider was restored, so it was repeated with the `iptables` rule re-applied. The second enrolled credential (`puppetmaster`) authenticated, landed on `/v1/admin/role-capabilities`, and the operator then signed out — reaching the control by keyboard and actuating it with Enter, no mouse. Both ceremonies are now evidenced under provider unavailability |
| A-7 | Neutral user cancellation leaves the control usable, no technical disclosure, no auto-retry | **Passed.** The operator pressed **Use security key**, then dismissed the macOS passkey prompt. The page displayed exactly **"Security key operation was cancelled or timed out."** — `webauthn-emergency.9e0c073e9e6c.js:423`, a client-side status write. No closed-vocabulary code (`origin_invalid`, `rate_limited`, `invalid`, `expired`) reached the interface; cancellation and timeout are deliberately not distinguished. The control remained usable and unchanged, and no second prompt appeared unprompted |
| A-8 | No assertion, credential ID, challenge, cookie or recovery token in captured evidence | **Passed, verified by scanning this document rather than asserted.** No string of 40+ base64url/hex characters appears anywhere in it except the commit SHA `0c95e72…` and a test filename. No cookie value, bearer token, recovery token, challenge or assertion appears. The UUIDs recorded are the correlation references shown to the caller (`cd2275e1-…`, `a4890d68-…`, `341a2706-…`), which §9.2's A-6 row explicitly requires, and — added 2026-08-24 — SP-21's two **grant record ids** (`233b8199-…`, `b8437d11-…`), which §9.2's A-9 row explicitly requires. A grant record id is a reference to a row of ours; it is not the token, is not derived from the token, and does not yield it. Credential **nicknames** (`macbook`, `iphone`, `puppetmaster`, `puppetphone`) are recorded, which §9.2's A-1 row explicitly permits; credential ids, public keys and COSE material were never selected by any query run in this session — the `webauthn_credentials` read named only `nickname`, `created_at`, `disabled_at`, `last_used_at`. No screenshot was captured |
| A-9 | Provider dependency restored; ordinary staging login and health verified | **Passed.** Egress restored and verified: `sudo -u freedomweb curl … https://discord.com/api/v10/oauth2/token` → **`405`**, Discord's own answer to a GET on a POST-only endpoint, i.e. a real HTTP response rather than a connection failure. Compare the blocked state's `curl: (7) … after 1 ms` / code `000` (A-2). **Passed in full.** An ordinary Discord staging login was then performed in the browser and succeeded, returning the complete member/Council/administrator navigation |

### Incident I-1 — second-credential attempts refused (2026-08-24, during A-6)

**What happened, in the operator's words:** "I may have tried the wrong one and
then I tried my phone but it somehow didn't work. Now I can't use it anymore:
Emergency sign-in did not complete. Reference `cd2275e1-afaf-491f-9f6d-eb0adc6c7256`."

**Assessment: expected behaviour, not a defect — but with a correction.** This was
first read as pure rate-limiting. The operator has since clarified that the
credential he presented was one of the **retired** pair, so the two audited
refusals at 09:24 are most likely retirement being enforced, and only the later,
unaudited attempts were the limiter. The corrected reading is in the A-6 evidence
section. Several assertion attempts in a short window is still precisely what
N-32's budgets exist to refuse. The limiter is a
**fixed (tumbling) window** — `application/web/rate_limit.py:150-159` derives
`window_start(now, minutes=…)` and compares a per-window count against the budget —
so it clears itself when the window rolls over. There is no lockout, no
administrative unlock, and further attempts cannot push the reset later.

Two budgets could have produced it, and the refusal deliberately does not say
which (non-enumeration):

| Budget | Bound | Window |
|---|---|---|
| `webauthn_assertions_per_ip` (N-32) | ≤ 5 | ≤ 10 min (`window_minutes`) |
| `webauthn_assertions_per_account` / `per_credential` (N-32) | ≤ 10 | ≤ 60 min |

The deployed values are in `/etc/freedom-web/portal.env` and were not read.

**What this incidentally evidences — the refusal presentation is correct.** The
operator saw "Emergency sign-in did not complete." plus a correlation reference,
and no technical disclosure: no limiter name, no budget, no retry-after, no
credential or account existence signal, and none of the closed vocabulary
(`origin_invalid`, `rate_limited`, `invalid`, `expired`) leaked into the
interface. This is a real-browser observation of the R-07/R-08 refusal
presentation that the plan's §2 could only probe automatically.

**Correlation reference:** `cd2275e1-afaf-491f-9f6d-eb0adc6c7256`. Recorded because
the plan's §9.2 A-6 row requires the correlation ID; it is an audit handle, not
credential material.

**Busy-state question resolved — no defect.** The operator confirms the control
"works fine, just does nothing (it seems)": it remains clickable and is not stuck
disabled or spinning. The attempts were being refused by the limiter, which is the
correct behaviour. The control clears its busy state, so the §4.3 failure
condition "failure to clear busy state" does **not** apply.

**Audit trail of the incident** (read by the operator from `audit_events`):

| Time (UTC) | `actor_capability` | `action` |
|---|---|---|
| 09:17:20 | `platform_administrator` | `auth.emergency.webauthn.succeeded` |
| 09:21:47 | `guild_member` | `auth.logout` |
| 09:24:19 | `system` | `auth.emergency.refused` |
| 09:24:30 | `system` | `auth.emergency.refused` |

The single success and single logout match A-3/A-5 exactly. **Two rows in that
table are wrong, and each is a separate finding: S-5 and S-6 below.**

The correlation reference the operator was shown, `cd2275e1-…`, returned **0 rows**
— see S-5.

---

### SP-21 — the host-local recovery grant, issued, used once, replayed and expired

**Added after the §4 procedure closed.** A-05 criterion 8. Executed by the
Operations Owner; the grant tokens were never transmitted to the reviewer, never
recorded here, and never entered a shell history — `tools/emergency_recovery.py:160`
prints the token from inside the program rather than taking it as an argument.

| Step | Action | Result |
|---|---|---|
| 1 | Grant issued host-locally via `portal-run.sh -m tools.emergency_recovery issue` | Issued; token displayed once and stored only as a hash. Grant record **`233b8199-2371-4ee6-88b9-a8e134bdd9a5`** (`created_at` 20:44:12.738527Z, `expires_at` 20:54:12.738468Z, `consumed_at` 20:44:49.396104Z) |
| 2 | Token submitted to the R-09 recovery form | **Accepted** — session established, landing on `/v1/admin/role-capabilities` |
| 3 | **The same token submitted again** after sign-out | **Refused.** "Emergency sign-in did not complete. Reference `a4890d68-835b-4ce3-bb1a-007274efe2c5`." The page did not change; the message appeared in place |
| 4 | A second grant issued, then left **unused for 15 minutes** (ceiling is `GRANT_MINUTES = 10`) | Grant record **`b8437d11-2ae0-4ef9-83e4-02f5325736d9`** (`created_at` 20:47:07.711073Z, `expires_at` 20:57:07.711019Z, `consumed_at` null) |
| 5 | The expired token submitted | **Refused.** Reference `341a2706-ec29-4a9a-900e-00828b532636` |

**Single-use and expiry are both enforced.** The 15-minute wait deliberately
exceeded the 10-minute ceiling, and also let the N-33 per-address recovery window
(≤ 3 attempts) roll over, so step 5 is an expiry refusal and not a limiter refusal
wearing the same words.

**Both refusals are identical in presentation** — the same neutral sentence and a
correlation reference — so a replayed grant and an expired one are
indistinguishable to the caller. That is consistent with the non-enumeration
discipline applied to credentials and to the retired-credential path.

**The audit trail confirms every step.** Read from `audit_events` (the `session_id`
present in one payload is deliberately not transcribed here):

| Time (UTC) | action | actor_capability | payload reason |
|---|---|---|---|
| 20:44:12 | `auth.emergency.recovery.issued` | `platform_administrator` | operator and `expires_at 20:54:12` |
| 20:44:49 | `auth.emergency.recovery.consumed` | `platform_administrator` | `auth_method: recovery_grant` |
| 20:45:35 | `auth.logout` | **`guild_member`** | `auth_method: recovery_grant` |
| 20:45:43 | `auth.emergency.refused` | `system` | **`grant_not_live`** (replay) |
| 20:47:07 | `auth.emergency.recovery.issued` | `platform_administrator` | `expires_at 20:57:07` |
| 21:02:45 | `auth.emergency.refused` | `system` | **`grant_not_live`** (expiry, 5m38s past) |

Issue, consumption, replay refusal and expiry refusal are all recorded, with the
issuing operator named and the expiry stated in the row. The replay attempt at
20:45:43 is 54 seconds after consumption, and the expiry attempt is 5m38s past the
stated `expires_at` — both unambiguous.

**The logout row is a second, independent instance of S-6:** a session established
by recovery grant, whose own payload says `auth_method: recovery_grant`, audited as
`guild_member`.

**Recovery refusals are audited, unlike the rate-limited assertion refusals of
S-5.** `adapters/web/app.py:1194-1198` routes redemption failures through
`record_authentication_failure`, and `:1174-1177` does the same for the per-grant
attempt cap. S-5 is therefore specific to the two limiter short-circuits at
`:1092-1113`, and is not a general property of break-glass refusals. Note however
that this route repeats the same shape at `:1154` (empty token) and `:1159-1163`
(per-address limiter), both of which return without auditing.

**A-9's grant record IDs — recorded 2026-08-24 (F4 remediation).** §9.2's A-9 row
asks SP-21 to record the **grant record ID** of each grant, and the table above did
not. The two ids are now in it, read host-locally from `recovery_grants` on the
staging database with a single read-only `SELECT` naming `id`, `purpose`,
`created_at`, `expires_at`, `consumed_at` and `invalidated_at` **and no other
column** — `token_hash` was never selected, is not derivable from an id, and appears
nowhere in this document. Each row's timestamps match the audit times already
transcribed above to the second, which is what identifies them as SP-21's two
grants rather than an assumption that they are: `233b8199…` was consumed at
20:44:49.396104Z (the accepted redemption) and is the grant replayed at 20:45:43Z,
and `b8437d11…` was never consumed and expired at 20:57:07.711019Z, 5m38s before
the refusal at 21:02:45Z.

**Still Not Run for criterion 8's neighbours:** the `revoke` subcommand and its
`invalidate_all` path were not exercised, and criterion 9 (custody, replacement,
loss) is documentation not yet written.

---

### SP-22 — the break-glass boundary observed at the route, not only in the frame

**Completed 2026-08-25.** The navigation half was observed on 2026-08-24; the
import-apply half on 2026-08-25, recorded at the end of this section.

**Added after the §4 procedure closed**, because §4 evidenced only the presentation
half of A-05 criterion 6. A withheld navigation link is not an enforced boundary.

Method: hold a live break-glass session — confirmed live by landing on
`/v1/admin/role-capabilities` — then request each withheld destination **directly by
URL**, without signing out.

| Route | Path | Result |
|---|---|---|
| R-20 | `/v1/characters` | **Refused** — the denial page, "Not available" |
| R-22 | `/v1/council/characters` | **Refused** — same |
| R-40 | `/v1/council/snapshots` | **Refused** — same |

The response is `adapters/web/templates/denied.html`, whose heading is literally
"Not available". It is deliberately non-specific: it does not say which capability
was missing, which is the same non-enumeration discipline the refusal vocabulary
and the credential lookup follow.

**A false pass was avoided here and it is worth recording why.** The first attempt
at this check returned the **Discord sign-in page** for all three URLs. That is the
signature of *no session at all* — `adapters/web/portal_routes.py:415-423` answers a
sessionless GET navigation with `303` to `/v1/login` — and not of a break-glass
session being refused, which takes the `require_guild_member()` →
`NotAMember()` → denial path instead. Two different mechanisms that a person
reading a browser cannot tell apart without knowing to look. Re-run while genuinely
holding a break-glass session, the result was the denial page. **Had the first
result been recorded, this document would carry a pass for a test performed
signed-out.**

**Completed 2026-08-25 — the import-apply half of criterion 6 is now observed.**
R-41 and R-46 are POST routes taking an identifier, so they cannot be driven from a
browser address bar, and driving them from a shell would mean handling the
operator's session cookie — which A-8 forbids recording and which the reviewer must
not do. Both constraints are met by issuing the requests **from inside the
already-authenticated page**: the browser attaches the HttpOnly cookie itself, so it
is never read, copied, printed or recorded, and the CSRF value is taken from the
hidden field the page had already rendered and is likewise never recorded.

Executed by the Operations Owner from `/v1/admin/role-capabilities`, holding a live
break-glass session, on the identity-verified process PID 3785672 (see the
post-remediation operational addendum §2). Path identifiers were **synthetic**
well-formed UUIDs — `00000000-0000-4000-8000-000000000001` — naming no real
snapshot and no real job. Bodies were minimal and form-encoded, carrying the valid
CSRF value.

| Route | Path | Time (UTC) | Status | Refusal |
|---|---|---|---|---|
| R-41 | `POST /v1/admin/snapshots/{synthetic}/folder` | 2026-08-25T05:22:31.435Z | **403** | `emergency_surface_refused` |
| R-46 | `POST /v1/council/jobs/{synthetic}/apply` | 2026-08-25T05:22:31.608Z | **403** | `emergency_surface_refused` |

**Both are passes, and at a stricter point than criterion 6 asks for.**
`emergency_surface_refused` is raised by the **first** statement in
`application/web/access_control.py:318-319` — N-65's continuity-surface check, which
`authorize()` evaluates *before* the route's capability requirement, deliberately,
"so a break-glass session on a Council route is refused for being emergency-scoped
rather than for lacking Council". The refusal therefore proves more than that the
caller lacked import-apply authority: it proves the continuity surface excluded the
route outright, before the requirement was consulted and long before any handler ran.

**Why neither result is a false pass.** The preamble
(`adapters/web/import_routes.py:150-230`) refuses in a fixed order — session, then
origin and content type and body bound, then CSRF, then capability — so each way of
failing early is distinguishable from this outcome by its own observable:

- a sessionless attempt answers `401`, or `303` on a navigation route;
- a foreign origin answers `403 origin_invalid`;
- a wrong content type answers `415`, and a missing length `411`;
- a bad or absent CSRF value answers `403` with a JSON body of exactly
  `{"error": "csrf_invalid"}`, from step 3, **before** step 5 is reached.

None of those was observed; both routes answered `403 emergency_surface_refused`,
which only step 5 produces. Nor did either request reach object lookup: a handler
that had run would have answered `snapshot_absent`, `job_absent` or
`object_not_reachable` for a synthetic identifier naming nothing, and neither did.
That absence is the criterion-6 property — the route refuses **before** it looks the
object up, so an emergency administrator cannot use it to discover whether an
identifier exists.

The earlier §4 observation that R-40 (`/v1/council/snapshots`) is refused already
showed the emergency administrator cannot *navigate* to the import surface. These
two rows show the mutating endpoints refuse even when addressed directly, with a
valid session and a valid CSRF value. Criterion 6 no longer rests on suite-level
evidence alone; `tests/web/test_break_glass_login.py` and the TC-BG-05 rows now
corroborate an observation rather than substitute for one.

---

### A-4 corroboration — the same shell, two authorities, observed back to back

The continuity shell was compared against an ordinary session on the same deployed
build, by the same operator, minutes apart:

| Session | Navigation offered |
|---|---|
| Break-glass (continuity-scoped) | Role capabilities · My account · Sign out |
| Ordinary Discord login (member + Council + administrator) | Characters · Council characters · Snapshots · Role capabilities · My account · Sign out |

The three destinations withheld from break-glass — `CHARACTERS` (R-20/R-21),
`COUNCIL_CHARACTERS` (R-22) and `SNAPSHOTS` (R-40) — are exactly the ones
`application/web/shell.py:245-264` places behind `not continuity_scoped`, and they
appear for the same person the moment his authority arrives through the ordinary
provider. This is A-4 demonstrated by contrast rather than by absence alone, and it
is stronger evidence than either observation on its own.

---

### A-6 evidence — two distinct enabled credentials, and no disabled one accepted

The operator **presented a retired credential during the session and it was
refused** — his devices show the retired and current passkeys under
indistinguishable names. He did not authenticate with one. The credential records
below confirm the outcome. Read from `webauthn_credentials` (nicknames and timestamps only; no
credential id, public key or COSE material was selected):

| nickname | created_at | disabled_at | last_used_at |
|---|---|---|---|
| `macbook` | 2026-08-23 17:49:50Z | **2026-08-23 20:48:48Z** | *(null)* |
| `iphone` | 2026-08-23 17:53:34Z | **2026-08-23 20:48:48Z** | *(null)* |
| `puppetmaster` | 2026-08-23 20:41:25Z | — | **2026-08-24 09:36:26Z** |
| `puppetphone` | 2026-08-23 20:45:35Z | — | **2026-08-24 09:17:20Z** |

Three facts follow directly:

1. **Both of today's sessions used enabled credentials.** `puppetphone` at
   09:17:20Z is the first ceremony (A-3, matching the `auth.emergency.webauthn.succeeded`
   audit row to the same second); `puppetmaster` at 09:36:26Z is the second.
2. **They are different credentials**, which is exactly what A-6 requires — not the
   same authenticator twice.
3. **Neither disabled credential has ever produced a session.** `macbook` and
   `iphone` are the first enrollment pair, retired 2026-08-23 20:48:48Z once the
   replacement pair existed, and both carry a **null** `last_used_at` — a column
   only a successful use writes. No disabled credential has been accepted at any
   point in this environment.

Point 3 is the one that mattered: had a row with a non-null `disabled_at` shown a
fresh `last_used_at`, break-glass would have been accepting a retired credential,
and that would have stopped the session outright.

**A retired credential was presented and refused — real evidence, obtained by
accident.** The operator reports that the passkey he tried before the successful
second ceremony was one of the retired pair, chosen because his authenticator lists
retired and current passkeys under names he cannot tell apart. Retirement is
therefore not merely recorded in a column: it was enforced against a live
ceremony, in a real browser, on the deployed service. Two `auth.emergency.refused`
rows at 09:24:19Z and 09:24:30Z are the candidate records.

**Confirmed.** Both refusal rows carry `{"reason": "unknown_credential"}`:

| occurred_at | payload |
|---|---|
| 2026-08-24 09:24:19Z | `{"reason": "unknown_credential"}` |
| 2026-08-24 09:24:30Z | `{"reason": "unknown_credential"}` |

That is retirement being enforced, and the mechanism is exact:
`adapters/web/repositories.py:1280-1285` — `find_by_credential_id` filters
`disabled_at.is_(None)`, so a retired credential resolves to no record at all;
`application/web/breakglass.py:244-246` then refuses it as `unknown_credential`,
surfacing the coarse code `invalid` to the browser. The attempts reached
verification and were rejected there — they were not turned away earlier by the
limiter.

**A retired credential is deliberately indistinguishable from one that was never
enrolled.** Both answer `invalid`. That is the same non-enumeration discipline
`RateLimiter.check_credential` documents at `application/web/rate_limit.py:109-127`,
and it is correct: an operator who could tell "retired" from "never existed" would
have a credential-existence oracle.

**This closes the rejection half of A-05 criterion 3 by observation** — a real
retired passkey, presented in a real browser to the deployed service, refused at
verification. The *other* half of criterion 3 — that retiring below two enabled
credentials is refused — is a different procedure (SP-22) and remains **Not Run**.

**Usability observation, not a defect:** the operator cannot distinguish retired
from current credentials in his authenticator, because the nicknames the portal
holds (`macbook`/`puppetmaster`) are the portal's own labels and are not what the
platform passkey UI displays. This is worth a line in the A-05 custody
documentation (§9.2 A-10): an operator who cannot tell his live credentials from
his dead ones during an actual emergency will burn limiter budget on the wrong
key, which is exactly what happened here in rehearsal.

---

### A-2 evidence — provider unavailability, and its isolation

Method: one `iptables` OUTPUT rule matched on the portal service account's uid,
applied by the Operations Owner at his own console:

```
sudo iptables -I OUTPUT -m owner --uid-owner freedomweb -p tcp --dport 443 \
  -j REJECT --reject-with icmp-port-unreachable
```

The portal runs as `freedomweb` (uid 994); the live bot runs as `discordbot`, a
different uid, so the rule cannot match it. Inbound traffic is untouched, so Caddy
still reaches the portal, and the database is a Unix socket.

| Probe | Result |
|---|---|
| `sudo -u freedomweb curl … https://discord.com/api/v10/oauth2/token` | **`curl: (7) Failed to connect to discord.com port 443 after 1 ms: Couldn't connect to server`**, code `000` — the portal's own identity cannot reach Discord |
| `sudo -u discordbot curl … https://discord.com/api/v10/gateway` | **`200`** — the live bot is unaffected |

The 1 ms failure is the local `REJECT` answering immediately, not a timeout, so
the unavailability is unambiguous rather than slow.

**The outage is evidenced here and not from `/healthz`**, which reports
`identity_provider: true` throughout — see finding S-4.

---

## 5. Sanitization

No credential material, token, assertion, challenge, cookie, secret or personal
datum has been recorded in this document — **verified by scanning it**, see A-8.
`/etc/freedom-web/portal.env` was not read; it is not readable by the review
account, and `WEB_WEBAUTHN_RP_ID` was never needed because the authenticator
enforced the binding instead (A-1).

Every database read performed in this session selected named non-sensitive
columns. No query selected `credential_id`, `public_key`, `aaguid` or any session
or token column.

The same holds for the two reads added on 2026-08-24 while completing this
document's outstanding fields: `recovery_grants` was read for `id`, `purpose`,
`created_at`, `expires_at`, `consumed_at` and `invalidated_at` — **not**
`token_hash` — and `audit_events` was read for `occurred_at`, `action`,
`actor_capability` and the `auth_method` key of the payload. Both were read-only
`SELECT`s against the staging database. No session, token or credential column was
named by either.

---

## 6. Findings raised during this session

### S-1 — the deployed staging process predates the commit under test (blocking, not a code defect)

- **Observed:** `GET /v1/auth/emergency` on the running service returns **HTTP 500**
  `{"error":"unexpected_error"}`. Static assets and `/healthz` return 200.
- **Cause:** `freedom-web.service` has been running since **2026-08-23T16:45:09Z**
  (PID 3074124). `adapters/web/app.py` was last modified 2026-08-23T23:10:01Z and
  `adapters/web/templates/emergency.html` 2026-08-24T01:10:12Z. Jinja reads
  templates from disk per render, so the **old Python is rendering the new
  templates**. Commit `0c95e72` changed `RequestAuthority.render()` to pass a
  server-owned `shell` into the template context (C35-05); the running process
  passes only `{"view": view}`, and `base.html` now requires `shell`.
- **Not a defect in the commit under test:** the same request path renders
  correctly under `0c95e72` in-process — `tests/web/test_break_glass_login.py`
  **17 passed** against the disposable database, plus B-4 above.
- **Remedy:** restart `freedom-web.service` so it loads `0c95e72`. This needs root;
  the review account has passworded `sudo` only, so it is an operator action.
- **Resolved:** the Operations Owner restarted the service at **2026-08-24T08:36:54Z**.
  `GET /v1/auth/emergency` now returns **200** and serves the remediated control
  (B-8…B-10). No repository change was required and none was made.
- **Consequence for the record:** no browser observation was taken before the
  restart, so no §4.2 or §4.3 evidence rests on superseded code.
- **Consequence for the project:** the service does not reload on deploy. Any
  future staging evidence run must confirm the running PID postdates the commit
  under test before it observes anything. Recorded here because a green suite and
  a healthy `/healthz` both reported fine while the page under test was returning
  500 — `/healthz` does not render a template.

### S-2 — `freedom-worker.service` is inactive (observation, not yet a finding)

`systemctl is-active freedom-worker.service` → `inactive`, while `/healthz`
reports `worker_heartbeat: true`. Not on this session's critical path — the
break-glass ceremony does not depend on the worker — but it is recorded because
TC-OPS and the I-06 worker rows will need it running, and because a heartbeat
check reporting healthy for a stopped worker deserves its own look.

---

### S-3 — no `Strict-Transport-Security` anywhere (observation, out of today's scope)

The application sets CSP, `Referrer-Policy`, `X-Content-Type-Options` and
`Permissions-Policy`, and the proxy deliberately adds no security headers
(F-12: `frame-ancestors 'none'` replaces `X-Frame-Options`). HSTS appears in
neither, and in no accepted contract. It may be supplied by the Cloudflare edge,
which this loopback observation cannot see. **Not a blocker for TC-UI-01/02 or
TC-BG-02.** It belongs to the TC-SEC-07 security-header evidence run, which the
proxy configuration already says must happen with the 401 gate removed, since a
gate response is not the application's own answer.

---

### S-4 — `/healthz` reports `identity_provider: true` unconditionally (important)

- **Observed:** with outbound HTTPS rejected for the portal's service account,
  `/healthz` continued to answer `{"status":"ok", … "identity_provider":true …}`.
- **Cause:** `adapters/web/app.py:1212` calls
  `build_health_view(settings, composition.engine, provider_ok=True)`. The value
  is a **literal**, not a probe. `application/web/startup.py:267` faithfully
  reports whatever it is handed, and every other check in that function does real
  work — database `SELECT 1`, `alembic_version` against `migration_head()`,
  artifact-root stat, worker liveness, kill-switch file. `identity_provider` alone
  is a constant, and carries no comment saying so.
- **Consequence:** the portal cannot report a Discord outage. During exactly the
  event break-glass exists for, `/healthz` answers `ok` on every check and returns
  200 rather than 503. An operator paging on that endpoint would see nothing.
- **Not a blocker for TC-BG-02**, which needs the outage to be *real*, not to be
  *reported*. Provider unavailability is therefore evidenced at the network and
  application level instead (§4.3 A-2), not from the health body.
- **Bearing:** I-06 criterion 9, TC-OPS-05 monitoring evidence, and the VM-16
  health vocabulary. Recorded for the Security Reviewer rather than fixed here: no
  repository change belongs in the middle of an evidence session.
- **Pattern worth naming.** This is the third green-signal-over-reality defect in
  this package's history: F-16 (no test asserted a human could complete
  break-glass), S-1 (a healthy `/healthz` and a fully green suite while the page
  under test returned 500), and now S-4. Each was found by looking at the running
  system rather than at its self-report.

### S-5 — a rate-limited break-glass refusal is shown a correlation ID but writes no audit record (important, security)

- **Observed:** the operator was shown "Emergency sign-in did not complete.
  Reference `cd2275e1-afaf-491f-9f6d-eb0adc6c7256`." A `SELECT … WHERE
  correlation_id = 'cd2275e1-…'` against `audit_events` returned **0 rows**. The
  two earlier refusals, before the limiter engaged, *were* recorded as
  `auth.emergency.refused`.
- **Cause:** in `adapters/web/app.py:1092-1113`, both N-32 budget checks in
  `emergency_webauthn_verify` return `json_refusal(429, "rate_limited",
  correlation_id)` directly. Neither path calls `record_authentication_failure`,
  which every other refusal in that route reaches via `AuthenticationFailure`.
  `application/web/breakglass.py:498` builds refusals that always carry a
  `FailureAudit` — but the limiter refuses in the route, before the service that
  would have built one is ever called.
- **Why it matters:** the refusals that stop being recorded are precisely the ones
  that indicate an attack. The first few failed assertions against break-glass are
  audited; once someone is trying hard enough to hit the budget, the audit trail
  goes silent, and the sustained attempt is the event an investigator most needs.
  The correlation reference handed to the person on screen resolves to nothing,
  so the one identifier offered for follow-up cannot be followed up.
- **It contradicts the codebase's own stated rule**, twice:
  `application/web/errors.py:250` — "A refusal that leaves no trace is
  indistinguishable afterwards from an attempt that never happened";
  `application/web/breakglass.py:516` — "SM-03 requires every attempt and outcome
  to be audited, and a record that vanishes with the refusal would satisfy that
  only on paper."
- **Bearing:** A-05 criterion 7 (limiter, audit, correlation), SM-03, N-32, and
  the §9.2 A-8 row. **A-05 should not close while this stands.**

### S-6 — every logout is audited as `guild_member`, including a break-glass administrator (important)

- **Observed:** the operator's break-glass sign-out recorded
  `actor_capability = guild_member`, in the same session whose login had correctly
  recorded `platform_administrator`.
- **Cause:** `application/web/sessions.py:658-661` hardcodes
  `actor_capability=ActorCapability.GUILD_MEMBER` in `logout()`. It is not derived
  from the session or the context, and no comment defends the choice — unusual in
  a file that documents its reasoning heavily elsewhere.
- **Why it matters:** the column is defined as "the authority the action was taken
  under", and the schema comment at `adapters/database/tables.py:251` insists a
  Council member acting on a character they do not own must be distinguishable in
  the audit from the owner. A break-glass administrator is recorded here as
  holding a capability they demonstrably did not have — during a Discord outage
  they have no guild membership at all, which is why migration `0006` widened the
  attribution constraint specifically for this actor. The audit answers "who ended
  this session, under what authority" incorrectly for every break-glass session,
  and imprecisely for every ordinary one.
- **Partly mitigated:** `payload` carries `{"auth_method": …}`, so the true method
  is recoverable by an investigator who knows to look past the capability column.
- **Bearing:** A-05 criterion 7, SM-03 audit integrity, TC-OPS-05.

### S-9 — the audit cannot distinguish a replayed recovery grant from an expired one (important, security)

- **Observed:** the replay attempt (20:45:43Z) and the expiry attempt (21:02:45Z)
  produced **byte-identical audit payloads**: `{"reason": "grant_not_live"}`. Neither
  row carries a grant record id, so there is no handle back to which grant was
  presented.
- **Cause:** `adapters/web/repositories.py` — recovery-grant `consume` is "One
  statement. Replay, expiry and concurrency all yield zero rows", a single
  conditional `UPDATE`. `application/web/breakglass.py:422-423` then maps the `None`
  to `grant_not_live`. The distinction exists in the row — `consumed_at`,
  `expires_at`, `invalidated_at` are all stored — but nothing reads it after the
  zero-row result.
- **The atomicity is correct and should not change.** A single conditional update is
  exactly right: it closes the check-then-consume window, and the comment says so.
  The finding is not about how the grant is consumed; it is about what is recorded
  once consumption fails.
- **Why it matters:** identical presentation to the *caller* is correct
  non-enumeration. Identical presentation to the *investigator* is not. "A token
  that was already used was presented again" and "the operator was too slow" are
  different security events — the first can mean a recovery token leaked, which is
  the scenario N-14's single-use rule exists to contain. Today's evidence needed the
  reviewer to reconstruct which was which from wall-clock timestamps and from
  knowing what the operator had been asked to do. An investigator months later,
  reading the table alone, could not.
- **Contrast within the same session:** the retired-credential refusals recorded a
  specific `unknown_credential`, and `_refuse` already supports attaching a
  `credential_record_id`. The equivalent grant reference is simply not passed.
- **Bearing:** A-05 criterion 8, SM-03, N-14.

### S-8 — the sign-out destination is unpolished (cosmetic, Product Owner observation)

The Operations Owner, unprompted: "The sign out page is not nice. Just fyi."

Recorded because it comes from the Product Owner about his own product, not because
it is a defect. Signing out lands on `/v1/login`, which **passes** every functional
and accessibility check this session applied — three widths, 200% zoom, keyboard
traversal, visible focus. The observation is aesthetic and concerns the
post-sign-out experience specifically, not the sign-in page in general.

No action is proposed here. The Phase 3 visual baseline is accepted and frozen
(`phase-3-visual-freeze-manifest.sha256`), so a change would be a scope decision for
the Acceptance Authority rather than a remediation.

### S-7 — a cancelled ceremony still spends per-address limiter budget, and a successful one spends two (important, operational)

- **Mechanism:** `adapters/web/app.py:1063` (R-07 options) and `:1092` (R-08
  verify) both call `_consume_rate_limit(..., _webauthn_action(), ...)` — the
  **same** `LimitedAction`, so the same per-address bucket
  `webauthn_assertion:ip:<digest>`.
- **Consequences, with `webauthn_assertions_per_ip` bounded at ≤ 5 per ≤ 10 minutes
  (`application/web/config.py:955`):**
  - one **completed** ceremony costs **two** units — options, then verify;
  - a ceremony **cancelled at the authenticator** costs **one**, because the
    options call has already happened before the prompt appears. The cancellation
    itself never reaches the server — it is a client-side status write — but the
    budget is already spent.
  - so an operator gets roughly **two complete attempts per window**, and every
    fumble costs one more.
- **Why it matters for break-glass specifically.** This is the door used when
  Discord is down and someone needs in. Combine it with the two facts this session
  already established — the operator **cannot tell his live passkeys from his
  retired ones** in the authenticator UI, and a rate-limited refusal **writes no
  audit record** (S-5) — and the realistic emergency is: a few wrong picks, budget
  exhausted, a refusal that says nothing specific, and no trace of any of it.
  That happened in rehearsal today, under no time pressure.
- **Not obviously a bug.** Limiting challenge issuance is correct — unbounded
  `begin_assertion` calls would be a resource attack. The question for the Security
  Reviewer is whether options and verify should share **one** bucket, and whether a
  budget of five per ten minutes is the right size once each attempt costs two.
  Nothing in the code or contracts acknowledges the doubling.
- **Bearing:** A-05 criteria 5 and 7, N-32, and break-glass availability — the
  property A-05 exists to guarantee.

---

## 7. Decisions

| Authority | Decision | Date |
|---|---|---|
| Operations Owner — SG-3 (credential ceremony) | **Approved**: "I approve the testing suit." | 2026-08-24 |
| Security Reviewer | *(none requested)* | — |
| Operations Owner | *(none requested)* | — |
| Peter — A-05, R-23 residual, Phase 3 gate | *(none requested)* | — |

**Nothing in this document closes A-05, TC-BG-02, TC-UI-01/02, R-23, I-06 or the
Phase 3 gate.**

---

## 8. Outcome, and what this does not close

**The §4 procedure completed.** Every checklist row in §4.2 and §4.3 is Passed;
none is Failed; none was skipped. It ran in two sittings on 2026-08-24, suspended
at 09:33Z and resumed the same day.

### 8.1 What was demonstrated

- A real WebAuthn ceremony, twice, on two distinct enabled credentials, in Chrome
  on macOS 26, against `https://freedom-blades-test.rpgworld.org`, **both under a
  genuine and independently verified Discord outage**.
- The break-glass session resolves to a continuity-scoped shell offering exactly
  `Role capabilities` and `My account` — proven by contrast against the same
  operator's ordinary session, which offers all six.
- Sign-out invalidates the session server-side; the protected route refuses a
  returning browser.
- The sign-out control is keyboard-operable, not merely keyboard-reachable.
- A **retired** credential was presented and refused at verification.
- Cancellation is neutral, non-disclosing, non-retrying, and leaves the control
  usable.
- All seven required views render at 320/768/1280 CSS pixels and at 200% zoom.
- The no-JavaScript page shows no dead security-key control — the F-15 branch,
  observed in a scriptless browser rather than inferred from markup.

### 8.2 What remains open, and why the gate does not move

**A-05 does not close on this session.** Criteria 1, 2, 2a and 5 are evidenced by
§4. **Criterion 8** (recovery grant issued, used once, replay and expiry refused)
**is evidenced by SP-21**, with the `revoke` / `invalidate_all` path still Not
Run. **Criterion 6** is evidenced **in full as of 2026-08-25**: presentation, the
three GET routes SP-22 observed on 2026-08-24, and the two POST routes R-41 and
R-46 observed on 2026-08-25 against the identity-verified deployed process, each
answering `403 emergency_surface_refused` from N-65's continuity-surface check
before any handler ran. **F3 is answered**; criterion 6 no longer rests on
suite-level evidence. **Criteria 3 (retiring below two is
refused), 4 (startup and `/healthz` below and at the threshold), 9 (custody,
replacement, loss) and 10 (Security Reviewer confirmation) are Not Run.**

**Five findings from this session bear on A-05 and are undispositioned:** S-4,
S-5, S-6, S-7 and S-9. The sixth — the SP-22 gap on criterion 6's remaining half,
recorded as F3 — was **closed by observation on 2026-08-25** (see SP-22 above). S-5 and
S-6 go to criterion 7 (limiter, audit, correlation, logout/revocation) directly,
and the independent review holds both **blocking** for it; S-9 goes to criterion
8's forensic quality without disturbing SP-21's behavioural proof.

**I-06 is untouched.** Its ten criteria include TC-OPS-01…05, TC-PERF-01…03,
TC-LIM-02, TC-SEC-07's browser half and observed startup refusals. This session
performed none of them.

**R-23 stays active.** TC-UI-01/02 are satisfied for **one browser on one
platform**. TC-UI-08's device matrix is not covered, and TC-UI-09's screen-reader
traversal is permanently Not Run under decision D-f.

### 8.3 Host state left behind

- `freedom-web.service` restarted at 08:36:54Z onto commit `0c95e72`; it stays
  there. **The service does not reload on deploy** — see S-1.
- The provider-outage `iptables` rule was applied and removed twice, and is
  **removed**. This is not merely attested: the ordinary Discord OAuth login that
  closed A-9 required the portal to reach Discord from its own service account, so
  the successful login is itself proof the rule is gone.
- `freedom-worker.service` remains inactive — see S-2.
- No repository file was changed by this session. The working tree that produced
  every result above is clean at `0c95e72`.

### 8.4 The findings this session produced

| # | Finding | Bearing |
|---|---|---|
| S-1 | The deployed process served code 8½ hours older than the commit under test; the page under test returned 500 while the suite was green and `/healthz` reported `ok` | Resolved by restart. The deploy/reload gap remains |
| S-2 | `freedom-worker.service` inactive while `/healthz` reports `worker_heartbeat: true` | I-06, TC-OPS |
| S-4 | `/healthz` reports `identity_provider: true` unconditionally — a literal, not a probe | I-06 criterion 9, TC-OPS-05 |
| S-5 | Rate-limited break-glass refusals write **no** audit record, while showing the user a correlation reference that resolves to nothing | **A-05 criterion 7**, SM-03, N-32 |
| S-6 | Every logout is audited as `guild_member`, including a break-glass administrator who holds no guild membership | **A-05 criterion 7**, SM-03 |
| S-7 | Options and verify share one limiter bucket: a completed ceremony costs two units of five, a cancelled one costs one | **A-05 criteria 5 and 7**, break-glass availability |
| S-3 | No `Strict-Transport-Security` anywhere | Observation, out of today's scope — see §6 |
| S-8 | The sign-out destination is unpolished | Cosmetic, Product Owner observation. The visual baseline is frozen, so any change needs the stated authority |
| S-9 | A replayed recovery grant and an expired one produce byte-identical audit payloads, with no grant reference in either | **A-05 criterion 8**, SM-03, N-14 |

The table above lists **nine** findings, reconciled 2026-08-24 (F4). It listed six
until then, omitting S-3, S-8 and S-9 — which §6 had recorded all along, and which
the review request had already carried for disposition.

**Not one of these was found by a test suite.** All were found by observing the
running system: S-1 by fetching the page, S-4 and S-7 by reading the code behind a
surprising observation, S-5 and S-6 by reading the audit trail the ceremony wrote,
S-2 by checking a service the health endpoint had already called healthy. That is
the same pattern as F-15 and F-16, and it is the argument for this kind of session
existing at all.

**A usability finding with no code defect behind it** is recorded in the A-6
evidence section: the operator cannot distinguish live from retired credentials in
his authenticator, because the portal's nicknames are not what the platform passkey
UI displays. With S-7's budget arithmetic, that is a genuine break-glass
availability risk and belongs in the §9.2 A-10 custody documentation.
