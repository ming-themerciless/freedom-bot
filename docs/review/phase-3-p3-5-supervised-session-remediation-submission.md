# P3.5 supervised session — remediation submission

**Date:** 2026-08-24
**Author:** Claude, P3.5 working Technical Lead
**Answers:**
`docs/review/phase-3-p3-5-supervised-session-codex-review.md` and
`docs/review/phase-3-p3-5-supervised-session-codex-security-review.md`
**Baseline commit:** `52ea162` ("Record P3.5 supervised session evidence and eight
findings"), working tree otherwise clean
**Status requested:** independent re-review and a distinct security re-review.
**No gate decision is requested and no RAID item is proposed for closure.** One
numeric policy addition (**N-32a**) is placed before the Acceptance Authority.

---

## 1. What was done, against what was asked

| Finding | Review's requirement | Status |
|---|---|---|
| **F1 / S-5 / S1** (blocking) | Route every counted emergency refusal through one durable failure-audit helper; same coarse caller response; PostgreSQL-backed route tests proving each limiter boundary writes exactly one refusal event with the displayed correlation id; no addresses, tokens, assertions or credential material | **Done** — §2 |
| **F2 / S-6 / S2** (blocking) | Derive the logout authority from the trusted persisted session; both break-glass methods record `platform_administrator`; regressions for WebAuthn, recovery-grant, ordinary member, Council and ordinary administrator | **Done** — §3 |
| **S-7 / S3** (important) | Split challenge issuance from assertion verification rather than raising the coupled number; define and test a separate issuance budget; keep per-account and per-credential controls independent | **Done** — §4, and it adds **N-32a**, which needs acceptance |
| **S-9 / S4** (important) | Keep the atomic conditional `UPDATE`; classify read-only by token hash in the same transaction after a zero-row result; audit a closed reason plus the non-secret grant record UUID; unchanged neutral caller response and no deliberate timing difference | **Done** — §5 |
| **S-4 / S5** (important) | Make `identity_provider` a bounded, side-effect-free check with a strict timeout and safe failure handling, using the least privileged documented endpoint, exposing no OAuth secret or response content | **Done** — §6 |
| **F4** (important) | Reconcile the evidence record's header, §4, §8.2 and §8.4 with its final state; record exact end times if available; add the grant record UUIDs or document a deviation | **Partly done — two items need the Operations Owner** — §7 |
| **F3 / live-boundary completion** (important) | Observe R-41 and R-46 on the deployed build under a live break-glass session | **Not done. It cannot be done from the repository** — §8 |
| **S-1, S-2** (operational) | Deployment/reload gap; inactive worker unit | **No repository change proposed** — §8 |
| **S-8** | Product Owner scope decision against a frozen visual baseline | **Untouched, deliberately** — §8 |

Every code change is enumerated in the freeze guard's allowlist
(`tests/web/test_p3_4_static_assets.py::PERMITTED_P3_5_BACKEND`) against the
finding that authorized it, so the guard names *why* each file was opened rather
than acquiring a general backend exemption.

---

## 2. F1 / S-5 / S1 — the emergency audit no longer goes silent at the limiter

**The defect.** Both N-32 limiter refusals in R-08 returned a correlation
reference and wrote nothing, and the same omission stood on R-07's per-address
limiter and on R-09's empty-token and per-address paths. An attacker could
therefore make the emergency audit stream stop at exactly the point the defensive
control activated, while the interface went on issuing references that resolved
to no row — which is the inverse of SM-03's accepted "every attempt and outcome
is audited".

**The fix is a boundary, not five call sites.** `EmergencyRefusalRecorder`
(`application/web/refusals.py`) is the break-glass twin of the
`OAuthRefusalRecorder` that already exists for R-04, deliberately built to the
same shape:

* constructed once per attempt, and **at most one** event per attempt is a
  property of the object rather than a rule an editor has to remember;
* it writes in its **own** transaction, because the transaction whose refusal it
  records has already rolled back;
* it accepts both a route-recorded `EmergencyRefusalReason` and a service-described
  `FailureAudit`, so a branch that records a reason and then raises still produces
  one row; and
* a failed audit write propagates to the safe-error handler rather than being
  swallowed. No session exists on any of these paths, so that can never convert a
  refusal into a login.

**Two refusals were moved so that they could be audited safely.** R-08's malformed
body and R-09's empty token were refused *before* their limiter. Auditing an
unbounded path would have handed an attacker an audit-growth lever, so each is now
refused *after* its budget is spent: counted first, recorded second, and bounded by
N-32/N-33 thereafter. This is also the stricter behaviour on its own terms — an
empty `token` was previously a free, uncounted probe of R-09.

**What a refusal payload may contain** is unchanged in kind: a closed reason, and
where one was resolved, an id of **our** rows. Never an address, a user-agent
digest, a token, a token hash, an assertion, a public key, or a presented
credential id. The per-account refusal names the protected account, which is what
tells an operator that the protected administrator is under sustained attack
rather than that some address was throttled; the per-credential refusal names
nothing, because the credential resolved to no account and the id is the caller's
bytes.

**One free function was removed, and a layer violation went with it.**
`record_authentication_failure` in `application/web/errors.py` committed a
described audit and nothing else, so a route using it had no way to state *"this
attempt has already been recorded"* — and the break-glass routes need exactly
that property, since one attempt there can reach both a route-recorded refusal
and a service-described one. Both recorders own it; a second, weaker writer
beside them would have been a second answer to "how many rows does one refused
attempt write". Its deferred `adapters.web.repositories` import was also
`errors.py`'s only outward one, so the module came **off**
`APPLICATION_WEB_ADAPTER_IMPORTS_STILL_OPEN` — the architectural ratchet in
`tests/web/test_structural_guards.py` failed until the list was shrunk, which is
that guard working exactly as designed.

**Refusals that are not counted stay unaudited, deliberately.** Origin and host
checks are the cheapest shield the routes have and are unbounded by design; the
independent review noted they may be governed separately, and they are.

**Evidence.** `tests/web/test_emergency_refusal_audit.py`, eight cases against
PostgreSQL through the real routes (TC-BG-18). Each asserts a row exists, that
there is exactly one of it, and that its correlation id is the reference the
caller was actually shown — read from the JSON body or the redirect, whichever
the route uses.

---

## 3. F2 / S-6 / S2 — logout records the authority the actor held

**The defect.** `SessionService.logout()` wrote a literal
`ActorCapability.GUILD_MEMBER` for every session it revoked. The supervised
session caught it twice, once for each break-glass method: a continuity
administrator with no proven guild membership, signing out during a verified
Discord outage, audited as `guild_member`. The `auth_method` payload made the row
correctable *by a reader who knew to look*, which is not the same as correct, and
it defeats the migration-0006 constraint swap whose whole purpose was to make
non-Discord attribution expressible.

**The fix.** `_AUDIT_ATTRIBUTION` in `application/web/capabilities.py`: an explicit
table from `AuthMethod` to `ActorCapability`, written out member by member, with
`audit_capability_of()` reading it and refusing rather than defaulting. It is
deliberately the same shape as `_SESSION_CLASSES`, including the import-time
completeness guard — adding a member to `AuthMethod` without deciding its
authority fails at startup, naming the method, rather than acquiring a silent
default. `discord_oauth` maps to `guild_member`, which is the word
`auth.login.succeeded` already records for the same session; both break-glass
methods map to `platform_administrator`.

The value is derived from `record.auth_method` — the persisted `sessions` column
the conditional resolve statement already matched on — and never from anything the
request supplied.

**Evidence.** `tests/web/test_logout_attribution.py` (TC-BG-20). Both break-glass
methods are named separately rather than parametrized past: the session the
operator actually signed out of was a `recovery_grant` one, and a fix verified
only against `webauthn` would have left the observed case untested. Ordinary
member, Council and administrator sessions are covered too, because a regression
that fixed break-glass by breaking ordinary logins would be the same defect
pointing the other way. The future-method guard is exercised over a synthetic enum,
since `AuthMethod` is closed.

---

## 4. S-7 / S3 — the two halves of a ceremony no longer compete for one budget

**The defect.** R-07 (issuance) and R-08 (verification) shared one five-unit
per-address bucket. A completed sign-in spent two units and a cancelled
authenticator prompt spent one, so about two complete ceremonies were available
per window — and the operator cannot distinguish a live passkey from a retired one
in the platform UI, which is how the session's incident I-1 happened.

**The fix, in the direction the review required.** `LimitedAction` gains
`WEBAUTHN_CHALLENGE`, and `RateLimitSettings` gains `webauthn_challenges_per_ip`,
registered as **N-32a** at 10 per source address per 10 minutes. The coupled number
was *not* raised. The two budgets bound different things and cannot be set
correctly by one number: issuing a challenge inserts one short-lived row that N-31
sweeps and verifies nothing, so it is an availability and storage bound; verifying
an assertion is the guess N-32 exists to make tedious, so it is a security bound.

**N-32's accepted values are unchanged**, and the split makes the assertion budget
stricter in practice rather than looser: five verifications now buy five
verifications instead of two-and-a-half ceremonies. The per-account and
per-credential controls are untouched and remain independent.

**This needs acceptance.** N-32a is recorded in
`docs/contracts/phase-3-numeric-policy-register.md` §3 with its reasoning and the
rejected alternative, and flagged there and in the change log as **pending
maintainer acceptance** rather than presented as accepted.

**Evidence.** `tests/web/test_rate_limits_and_outage.py` (TC-BG-19): the eleventh
issuance from one address is refused, the sixth verification from one address is
refused, and ten issue-then-verify pairs from one address show every issuance
served with the assertion budget deciding. TC-BG-11's per-address case now drives
**R-08** rather than R-07 — it could only ever have been driven through R-07
because the buckets were shared, so the test that was supposed to prove the
assertion budget proved it without making an assertion.

---

## 5. S-9 / S4 — a replay and an expiry are one answer outside and two inside

**The defect.** A replayed grant and an expired one wrote byte-identical audit
payloads, `{"reason": "grant_not_live"}`, naming no grant. Those two events mean
opposite things — a replay is a compromise signal, an expiry is a delay — and an
investigator could tell neither them nor *which grant* apart.

**The fix, exactly as prescribed.** The single conditional `UPDATE` still decides
consumption, alone. Only after it matches zero rows does
`RecoveryGrantRepository.classify_refusal()` run: one read-only `SELECT`, in the
same transaction, using the consume statement's own predicate including
`purpose = 'emergency_login'`, returning `consumed`, `invalidated`, `expired` or
`unknown` with the grant record id on the first three. Precedence is consumed,
then invalidated, then expired — the first two are mutually exclusive by
construction, and a consumed grant that has since passed its ceiling is still,
first and foremost, a replay.

The caller sees the identical neutral `invalid` for all four. There is no new
timing branch: the same one extra read runs on every failed redemption, including
`unknown`.

**Evidence.** `tests/web/test_recovery_grant_forensics.py` (TC-BG-21). All four
states are driven through the real R-09 route; the four caller responses are
asserted **equal** rather than described; the classification is shown to consume
nothing, write nothing and leave the attempt counter alone; and neither the token
nor its hash reaches the payload.

---

## 6. S-4 / S5 — `identity_provider` is a probe

**The defect.** `/healthz` passed `provider_ok=True`, a literal. The session
severed the portal's egress to Discord, verified the outage in both directions,
ran two real ceremonies under it — and the endpoint reported the identity provider
healthy throughout.

**The fix.** `IdentityProvider` gains `probe()`, with its contract written into the
protocol: bounded, side-effect-free, **total** (it answers, it never raises), and
silent (a boolean, never a status, body, URL or exception). The Discord adapter
implements it as one `GET` to `/gateway` — unauthenticated, documented, and the
least privileged endpoint available, so no client id, client secret, token or
scope is presented and no privileged quota is spent. Its body is never read.
Classification is the rule the rest of the adapter already uses: 5xx, 429 and
transport failures are unavailable, anything else is an answer.

The timeout is its own two-second ceiling, or the configured
`WEB_DISCORD_API_TIMEOUT_SECONDS` when that is tighter — configuration can narrow
it and never widen it. A hanging provider must not hold open the endpoint an
operator reaches for during an incident.

`build_health_view` still does not decide the value; the route awaits the probe and
hands it the boolean, because provider I/O is async and database work crosses the
threadpool, and this file's rule is that the seam stays visible at the call site.

**One operational consequence, stated rather than discovered.** `/healthz` now
makes one outbound request per poll, and an unreachable Discord makes the endpoint
answer `503` / `degraded` with `identity_provider: false`. That is the intended
behaviour and it is a change a monitor will see.

**Evidence.** `tests/web/test_provider_health_probe.py` (TC-OPS-18), seventeen
cases: the request itself is inspected for absent credentials, every status class
and three transport failures are classified, an unexpected error still answers
`False`, and the request's timeout is asserted against the configured one. No
socket is opened — the adapter runs over `httpx.MockTransport`. The route half
asserts the `503` / `degraded` report and that every other check still answers for
itself.

---

## 7. F4 — the evidence record reconciled, with two items outstanding

`docs/review/phase-3-p3-5-supervised-session-evidence-2026-08-24.md` is reconciled
**from its own contents**. No timestamped observation was altered:

* the header status now says the §4 procedure completed, and carries a note naming
  the reconciliation and what it did not invent;
* §1 records **Chrome on macOS 26** and the two enabled authenticators by nickname,
  both taken from §3 and the A-6 table rather than newly reported;
* §4's "Not started" opening — written before the sitting and never revised — is
  replaced by the execution record the rows below it already were;
* §8.2 records criterion 8 as evidenced by SP-21, states criterion 6's evidenced
  and remaining halves precisely, and counts six A-05-bearing findings rather than
  four; and
* §8.4 lists all nine findings; it listed six, omitting S-3, S-8 and S-9, all of
  which §6 had recorded all along.

**Two items are outstanding and need the Operations Owner.** They are marked in
the document rather than filled in:

1. **The exact session-end timestamp.** The latest time the document records is
   SP-21's expiry refusal at 21:02:45Z, which is a lower bound and not the end.
2. **The SP-21 grant record UUIDs**, which readiness-plan §9.2's A-9 row asks for.
   They are non-secret references to rows, readable host-locally from
   `recovery_grants` beside the timestamps already transcribed. Either they are
   added, or a deviation from A-9 is documented and approved.

---

## 8. What is deliberately not in this package

**F3 — R-41 and R-46 on the deployed build.** The review's method is sound and I
have no objection to it: a same-origin browser request under a live break-glass
session, reusing a CSRF value from an allowed page, with synthetic UUIDs, because
`enter_mutation()` refuses the continuity-scoped capability before either handler
parses or looks up the identifier. It requires the staging host, the Operations
Owner and a live session, and **cannot be performed from the repository**. It
remains the open half of A-05 criterion 6.

**S-1 (deploy/reload gap) and S-2 (inactive worker).** Operational, and the review
classes them so. No repository change is proposed for either; S-1 belongs in
deployment/operations evidence and S-2 is a prerequisite for I-06's worker
procedures.

**S-8 (the unpolished sign-out destination).** A Product Owner scope decision
against a frozen visual baseline, requiring the stated authority. Not touched.

**S-3 (no HSTS).** Recorded by the session as out of scope; unchanged here.

---

## 9. Verification

Every command below was run in this working tree, against the disposable
PostgreSQL database, serially:

```text
TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
  ./venv-web/bin/python -m pytest -q tests/web    2330 passed, 80 skipped
./venv/bin/python -m pytest -q tests              2079 passed, 267 skipped
node --test tests/web/webauthn_client.test.mjs    50 passed, 0 failed
sha256sum -c adapters/web/static/asset-integrity.sha256   4/4 OK
git diff --check                                  clean
```

The portal baseline before this package was 2286 passed / 80 skipped, so the 44
new cases are additions and nothing previously passing was removed or weakened.
Three existing cases changed, each for a stated reason: TC-BG-11's per-address
assertion half now drives R-08 (§4); the frontend freeze guard's backend
allowlist gains one entry per finding, so it names *why* each file was opened
rather than acquiring a general exemption; and the architectural ratchet's list
of `application/web` modules importing an adapter **shrank** by one.

A note on how the suite was run, since the earlier evidence session's S-1 turned
on exactly this kind of detail: the portal suite and the bot suite share one
disposable database and must run **serially**. An interleaved run of this package
produced two failures and 1,350 collection errors that vanished on a serial
re-run; the numbers above are from serial runs.

No staging host, real authenticator, credential, session cookie, recovery token,
external account or production database was accessed. No migration is included and
none is required: the audit table already expressed everything these corrections
needed.
