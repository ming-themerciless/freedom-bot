# Phase 3 route and authorization contract

Status: **Accepted 2026-08-13 at P3.G0.** No route existed at acceptance;
implementation remains bounded by the owning P3.1–P3.3 packages and gates.

Remediated in this revision: R-38 is added (ratification of an emergency-created
role-capability mapping); R-33/R-34 carry the N-67 administrator-continuity
allowlist; an eighth caller state `AC` is defined in §3.1 and bound to the `BG`
column by §3.3; and R-03/R-04 now state PKCE verifier handling consistently with
the schema — the previous text said the verifier was hashed, which contradicted
the schema and describes a flow that cannot complete.

**Corrected 2026-08-19 under the accepted D-03 correction (change-log
`C-P3.4-A`), and dated rather than folded into the text above.** Two items land
in this document:

- **D-03-1** — §1.2 is new. It adds the application-served `/static/` asset
  surface, M-01, as the one Starlette mount this application registers, states
  its URL grammar, caller state, host and kill-switch behaviour and cache policy,
  and brings mounts inside the closed inventory `TC-STRUCT-01` asserts. Before
  this the contract defined no static path at all while N-26 required same-origin
  CSS, script and images, and the structural guard could not see a mount.
- **D-03-5** — R-36's *Response* cell in the §5 table said `303` to provider,
  which contradicted §5.1's own prose and the accepted implementation. It now
  reads `200` HTML · VM-13 (`denied`). This corrects a record, not behaviour: no
  handler changed, and Phase 3 still has exactly one ordinary identity provider.

No caller state, capability, denial code, matrix cell, CSRF, origin or body rule
is changed by either item.

Package: P3.0 · Owner: Claude · Implemented by: P3.1 (§4), P3.2 (§5), P3.3 (§6)
· Frozen for Gemini at P3.G2/P3.G3.

Numbers cited as `N-nn` are defined once in
[`phase-3-numeric-policy-register.md`](phase-3-numeric-policy-register.md).
View models cited as `VM-nn` are defined in
[`phase-3-view-model-contract.md`](phase-3-view-model-contract.md).

## 1. Scope and the exhaustiveness claim

This document names **every** HTTP route the Freedom Blades portal will have at
the end of P3.3. The set is closed:

> A route that is not in §4–§8 of this document does not exist, and a mount that
> is not in §1.2 does not exist. A P3.1–P3.3 implementation that registers one is
> a contract violation, not an implementation detail.

This is the structural control behind the plan's requirement that *"no Phase 3
route or form mutates character game state"* (plan §12 Phase 3) and behind the
mandatory test *"direct HTTP and application-service tests prove no
character-game-state correction endpoint exists"*. The control is machine-checked:
`test_route_inventory_matches_contract` (P3.1, see
[`phase-3-test-traceability.md`](phase-3-test-traceability.md) TC-STRUCT-01)
parses the tables below and asserts set equality against the application's
registered routes, in the same way `tests/test_field_ownership_document.py`
already checks the field-ownership matrix against the profile.

**The guard covers mounts from 2026-08-19.** It previously read
`getattr(route, "methods", …)` off each registered route, and a Starlette `Mount`
has no `methods` — so a mount contributed nothing to the compared set and an
`app.mount("/anything", …)` would have added a whole URL subtree without failing
anything. TC-STRUCT-01 now asserts §1.2's mount table against the registered
`Mount` objects as well, and the falsification evidence for that assertion is
recorded in the D-03 correction submission.

### 1.1 Routes that already exist and are not changed

| Route | Owner | Status in Phase 3 |
|---|---|---|
| `POST /api/v1/foundry/snapshots` | Phase 2 I-03, ADR 0009 | Unchanged. Service-principal credential, no cookie authority, no session |
| `GET /api/v1/foundry/snapshots/{checksum}/preview` | Phase 2 I-03 | **Retired by P3.3.** It was built inert pending a Phase 3 authentication composition; P3.3 supersedes it with the job routes in §6. Retirement is a route removal, not a behaviour change: it has never served an authenticated request |

`/api/v1/*` is the **machine boundary** (service principals, no cookies).
`/v1/*` is the **browser boundary** (cookie sessions, CSRF, HTML and HTML
partials). The two prefixes exist so that a reader can tell from the path alone
which authentication model applies, and so that the Foundry module's hard-coded
submission path (module 1.0.7, deployed) does not move.

### 1.2 The one mount — M-01, the application-served static asset surface

**Added 2026-08-19 by the accepted D-03 correction (`C-P3.4-A`, item D-03-1).**

N-26 is `default-src 'self'; … script-src 'self'; style-src 'self'; img-src
'self' data:`. P3.4's production CSS, its vendored HTMX and its emblem therefore
have to be served from this origin, and until this section existed there was no
accepted surface to serve them from — while the set above was closed and named
none. This is that surface, decided here rather than in a template.

| # | Mount | Prefix | Served by | Kind |
|---|---|---|---|---|
| M-01 | `static` | `/static` | `freedom-web` (`adapters/web/static_assets.py`) | Starlette `Mount` over one directory |

**Why the application and not Caddy.** The operational contract's §4.1 table
gives Caddy exactly two jobs — TLS and HSTS — and assigns every other header to
the application so that each header has one authority. A Caddy `file_server`
would have split that: the CSP and `nosniff` on an asset would come from the
application's middleware only if the request reached the application, which by
construction it would not. Serving assets from `freedom-web` keeps one authority
per header, keeps the surface inside the closed inventory a test can assert, and
keeps development and production identical. §4.4 of the operational contract
records the deployment consequence.

#### Contract

| Property | Value |
|---|---|
| Methods | `GET` and `HEAD` only. Every other method is `405`, uniformly for every path under the prefix, so the refusal confirms no filename |
| Caller states | **All eight** — `U` `N` `M` `C` `A` `CA` `BG` `AC`. Public: no session, no capability, no CSRF token and no `Origin` requirement |
| Host check | **Applies** (N-01, §2.1 step 1). An asset request under an unknown `Host` is `400` before routing, exactly as a page is |
| Kill switch | **Exempt.** Assets keep serving while the switch is engaged (N-56), so the maintenance body, the login page and the safe error page keep their presentation during an incident. Every `/v1/*` route retains its `503` unchanged |
| Body bound | Not applicable; the methods carry no body |
| Session effect | **None.** A static response sets no cookie and refreshes no session, login-transaction or CSRF cookie. It cannot: the mount reaches no handler that issues one |
| Audit effect | None. Reads of a public asset are not audited (plan §9.4, *collect only necessary data*) |
| Origins | Same-origin only, N-26 unweakened. **No CDN, no remote font, no remote script and no remote image origin is permitted**, in this contract or in a P3.4 template |

#### URL grammar

```text
/static/<segment>[/<segment>…]
segment := [A-Za-z0-9][A-Za-z0-9._-]*
```

A path that does not match is `404`, **not** `400`: a grammar violation and a
missing file are the same fact to a caller, and distinguishing them would make
the grammar enumerable. The leading character may not be a dot, so every dotfile
in the root — the `.gitkeep` below included — is unreachable.

The grammar is checked before the filesystem is touched. It sits *in front of*
Starlette's own protection, which normalises `..` out of the request path and
then refuses any resolved path outside the root by `realpath` + `commonpath`;
both are asserted, over plain and percent-encoded traversal, by TC-STATIC-03.

#### Filesystem root

Exactly one directory: `adapters/web/static/`, resolved from the package rather
than from configuration. **There is no environment variable for it**, deliberately
— a configurable static root is an operator-supplied path to serve files from, and
"outside the approved root" should have one answer rather than one per deployment.
Directory listing is off, an implicit `index.html` is off, and a directory request
is `404`.

A missing root refuses at **construction**, not per request, so a mis-deployed
application does not start and then answer `404` to every asset. Git does not
track an empty directory, so the root holds one empty `.gitkeep` and nothing else.
That file is a placeholder that makes the root real; it is not an asset, it is
unreachable through the grammar above, and P3.4 owns everything that will
actually live here.

#### Cache policy

| Filename shape | `Cache-Control` |
|---|---|
| Fingerprinted — `<stem>.<16 lowercase hex>.<ext>`, e.g. `styles.9f2a1c4b8e7d6f50.css` | `public, max-age=31536000, immutable` |
| Anything else | `public, max-age=0, must-revalidate` |

The conservative branch is the default, so an asset that forgets to fingerprint
is slow rather than stale. Both are `public` and neither is `no-store`: §7.2's
`no-store` rule exists because a *rendered protected page* varies by caller, and
an asset does not — it is byte-identical for everyone and carries nothing about
the session that fetched it. Without that scoping the header would be decided by
whether the reader happened to be signed in. The six security headers of §7.2
still apply to every asset; only the cache rule is scoped out.

#### Missing assets

`404` with a safe body: no exception text, no filesystem path, no directory
listing, no stack frame. Same rule as VM-20 (N-25), and asserted by TC-STATIC-03.

#### What this section does not authorize

No production CSS, HTMX, image or other visual asset is added by it, and none is
in the tree. This is the surface and its rules; filling it is P3.4's work, under
Gemini, after Peter accepts the corrected D-03 contract and releases the
implementation prompt.


## 2. How authorization is decided

### 2.1 The chain, in order, for every `/v1/*` route

1. **Host check.** `Host` must equal the configured allowed host (N-01). Anything
   else is refused `400` before routing.
2. **Kill switch.** If the operator kill switch is engaged, every route except
   `GET /healthz` and the M-01 asset surface (§1.2) returns `503` with the static
   maintenance body (N-56). Both exemptions are closed and named: one is
   loopback-only and unpublished, the other is an unauthenticated directory of
   files that reaches no application service, and keeping them up is what lets an
   operator watch recovery and lets the maintenance page look like the platform.
3. **Body bound.** Content-Length over N-19 is refused `413` before the body is
   read.
4. **Session resolution.** The opaque cookie (N-05) is looked up by hash. Idle
   (N-06) and absolute (N-07) expiry are evaluated server-side; an expired
   session is treated as absent and its row is marked revoked.
5. **Origin check** (mutations only). `Origin` must be exactly N-01. Missing or
   mismatched is refused `403` before any application service runs.
6. **CSRF check** (cookie-authenticated mutations only). The synchronizer token
   (N-17) is verified in constant time, before the application service runs.
7. **Capability resolution.** The `AuthorizationContext` is produced *now* by
   `application/authorization.py`'s port, from the membership projection subject
   to N-09/N-10 — never from a value in the request, the session row, or the
   rendered page.
8. **Object-level authorization.** For any route naming a character, job or
   access record, the application service checks that *this* account may reach
   *that* object, inside the same transaction that reads it.
9. **Application service.** Only now does domain work begin.

Steps 5–8 are the boundary. A route handler that resolves an object before
step 7 is a defect even if the response is later suppressed.

### 2.2 UI hiding is not authorization — the explicit proof

Every protected route below carries a **direct-call denial test** in
[`phase-3-test-traceability.md`](phase-3-test-traceability.md) that:

1. authenticates as each role in the matrix (§3);
2. issues the request **without ever rendering the page that contains the
   control**, using the raw HTTP client and, separately, the application service;
3. asserts the exact refusal code and that no state changed and no audit success
   event was written.

The rendering rule is stated the other way round for Gemini in P3.4: a template
may hide a control the caller cannot use, but hiding it is a courtesy. The
server refuses the request whether or not the control was rendered, and the test
suite proves it by never rendering the control.

### 2.3 Denial-code rule

| Situation | Status | Reason |
|---|---|---|
| No session, protected route | `303` to `/v1/login` for `GET` navigation; `401` for HTMX partials and all mutations | A redirect for a mutation would be a silent no-op |
| Session exists, capability missing on a Council/admin route | `403` | The route's existence is not a secret; the caller's own capability is the fact being refused |
| Session and capability fine, but this object is not reachable by this account | `404` | Prevents an existence oracle over character, job and access identifiers (plan §12 Phase 3, *cross-character identifier substitution*) |
| Session valid but not currently a guild member | `403` with the non-member view (VM-02) | Distinguishable from *not logged in*, which is what a user needs to recover |
| Continuity-scoped session on a route outside N-65 | `403` | Emergency access is not general administration. A break-glass session is always continuity-scoped; so is an ordinary-provider session whose administrator capability derives only from an emergency-created mapping (schema §8.1) |
| Continuity-scoped session on R-33/R-34 with a capability outside N-67 | `403`, typed `emergency_scope_refused` | The administrator-continuity allowlist. Refused before any write, and refused again by a check constraint if the service is bypassed |
| Membership unknown and the N-10 grace is exhausted | `503` with the degraded view (VM-03) | Fail closed, not fail open |

A `404` for an object-level denial and a `404` for a genuinely absent object are
byte-identical. That is deliberate.

**The denial body is VM-22 `DeniedView` from 2026-08-19** (accepted D-03
correction, item D-03-6). Every row above that renders the safe denial page —
`401`, `403` and `404` alike — renders a view model carrying exactly `state` and a
closed-vocabulary `reason`. It previously rendered VM-02 with an empty guild name,
an empty `Instant` and the nil UUID; the bytes were right, but only because
`denied.html` did not print three fields it was handed, and P3.4 rewrites that
template. The byte-identity above is now a property of the type: there is no
correlation id, timestamp, guild name or object identifier for a template to
print. The non-member row keeps VM-02 and its recovery context, because that page
is *meant* to be distinguishable from "not signed in". No status code changes.

### 2.4 What is never authoritative from the browser

Per plan §9.2 and `.agents/AGENTS.md`: character IDs, job IDs, access-record IDs,
role claims, capability names, counts, checksums, Actor counts, prices, balances,
profile versions and preview tokens supplied by the browser are **inputs to a
server-side lookup**, never assertions. Each is re-resolved and re-authorized
server-side on every request, including the second request of a two-step
confirmation.

## 3. Role matrices

### 3.1 The seven caller states

| Code | Caller state | How it arises |
|---|---|---|
| `U` | Unauthenticated | No session cookie, or an expired/revoked session |
| `N` | Non-member holding a session | A session that was created while the person was a member, whose membership has since been revoked (§4.1, R-04). Login itself never produces this state |
| `M` | Member | Currently in the guild; no Council or administrator role |
| `C` | Council | Member holding role `1052702392728178688` (OD-18) |
| `A` | Platform Administrator | Member holding role `1124405581298552933` (OD-24), authenticated through Discord |
| `CA` | Council **and** Administrator | Both roles; the union of `C` and `A`, never more |
| `BG` | Break-glass | Authenticated by WebAuthn (N-13) or a recovery grant (N-14). Capability is exactly `platform_administrator` (N-12), restricted further by N-65 and N-67. **Never** Council, never character owner, whatever Discord roles the same human holds |
| `AC` | Continuity-scoped administrator | An **ordinary-provider** session whose `platform_administrator` capability is conferred only by mappings with `provenance = 'emergency_continuity'` (schema §8.1). It is not a break-glass session — `auth_method` is `discord_oauth` — but its administrator authority descends from one, so it reaches exactly the `BG` surface and no more, until a full-scope administrator ratifies (R-38) |

`DM` (role `1124406915783475241`) grants no Phase 3 web capability. It is stored
as a capability mapping and displayed, because Phase 8 will use it; no Phase 3
route consults it. That is recorded so a reviewer does not read its absence as an
omission.

### 3.2 Matrix legend

`✓` permitted · `✗` refused (with the §2.3 code) · `–` not applicable ·
`obj` permitted only for objects this account may reach ·
`✓ N-67` permitted only for the operations on the administrator-continuity
allowlist, everything else refused `403 emergency_scope_refused`.

### 3.3 Why `AC` has no column of its own

The matrices below keep seven columns. `AC` is defined by one rule instead:

> **Every matrix cell's `BG` value applies unchanged to `AC`.**

That is not a shortcut; it is the guard of schema §8.1 stated where a route
reader will meet it. A continuity-scoped administrator is confined to exactly the
break-glass surface *because* its authority descends from a break-glass session,
and expressing it as a duplicate column would invite the two from drifting apart
in a later edit. The tests carry the eighth state explicitly:
`[MATRIX]` is parametrized over the seven states, and TC-CAP-09 re-runs the whole
inventory for `AC`, asserting cell-for-cell equality with the `BG` column.

`AC` ends when the mapping conferring its administrator capability is ratified
(R-38), or when the account gains that capability through an ordinary-provenance
mapping by any other route. Both make the next capability resolution `full`, and
N-08 rotates the session on the detected privilege change.

## 4. P3.1 — authentication, session and health routes

| # | Route name | Method | Path | Kind | Response |
|---|---|---|---|---|---|
| R-01 | `root` | GET | `/` | navigation | `303` to `/v1/characters` (session) or `/v1/login` |
| R-02 | `login_page` | GET | `/v1/login` | navigation | `200` HTML · VM-01 |
| R-03 | `oauth_start` | GET | `/v1/auth/discord/start` | navigation | `303` to Discord authorization URL |
| R-04 | `oauth_callback` | GET | `/auth/discord/callback` | navigation | `303` to the safe return target |
| R-05 | `logout` | POST | `/v1/auth/logout` | form | `303` to `/v1/login` |
| R-06 | `emergency_login_page` | GET | `/v1/auth/emergency` | navigation | `200` HTML · VM-04 |
| R-07 | `emergency_webauthn_options` | POST | `/v1/auth/emergency/webauthn/options` | JSON (fetch) | `200` `application/json` |
| R-08 | `emergency_webauthn_verify` | POST | `/v1/auth/emergency/webauthn/verify` | JSON (fetch) | `200` `application/json` |
| R-09 | `emergency_recovery_login` | POST | `/v1/auth/emergency/recovery` | form | `303` to `/v1/admin/role-capabilities` |
| R-10 | `health` | GET | `/healthz` | operator | `200`/`503` `application/json` |

### 4.1 Route detail

**R-01 `root`.** Unauthenticated: `303` to `/v1/login`. No content, no view model,
no session effect. Exists so the bare hostname is not a `404`.

**R-02 `login_page`.** Unauthenticated HTML. Renders VM-01, which carries the
provider list, the degraded-provider banner when Discord is unreachable, and the
emergency-access link. **No CSRF token is issued** — there is no session yet.
An authenticated caller is `303`-ed to `/v1/characters` rather than being shown a
second login. Audit: none. Rate limit: none (it is a static render).

**R-03 `oauth_start`.** A `GET` navigation, deliberately, and this is the CSP
decision from N-26. See §6.4 below for the full reasoning. It:

- enforces N-18 (10 per source IP per 10 minutes, N-30 storage, N-34 address);
- generates a 256-bit `state`, a PKCE `code_verifier` and its S256 challenge;
- writes an `oauth_transactions` row holding the **SHA-256 hash of the `state`**
  and the **encrypted `code_verifier`**, the requested return target and an expiry
  of N-04. The two are stored differently because they are used differently: the
  `state` is only ever *compared*, so a hash is sufficient and a plaintext copy
  would be a liability; the verifier must be *presented to Discord* at the code
  exchange, so it has to be recoverable, and is protected by encryption instead
  (schema §9.2). An earlier revision of this document said "hashes of state and
  verifier", which contradicted the schema and would have produced a flow that
  cannot complete;
- sets the `__Host-fb_login_txn` cookie (`Secure`, `HttpOnly`, `SameSite=Lax`,
  `Path=/`, no `Domain`, lifetime N-04) holding the transaction's opaque id;
- redirects to Discord with scopes N-03 and redirect URI N-02.

Return target: only a **path** from a server-side allowlist (`/v1/characters`,
`/v1/characters/{uuid}`, `/v1/council/...`, `/v1/admin/...`) is accepted, and it is
stored server-side on the transaction row. No absolute URL, no scheme, no host, no
protocol-relative `//host` value ever reaches a `Location` header. Audit: none on
start (a start is not yet an identity claim); the transaction row itself is the
record. Session: none created.

**R-04 `oauth_callback`.** Path is fixed by N-02 and is the one route outside the
`/v1` prefix, because it is registered with Discord and changing it is a
configuration change at the provider. Steps, in order, all of which must pass:

1. N-18 callback limit (20 per source IP per 10 minutes);
2. the `__Host-fb_login_txn` cookie is present and names an unexpired,
   unconsumed transaction (N-04);
3. `state` hashes to the stored value, compared in constant time;
4. the transaction is marked consumed **in the same statement that reads it**, and
   that statement is also the only place the PKCE verifier is ever recovered: it
   returns the pre-update ciphertext and erases the columns in one pass, so a
   replay finds neither a live transaction nor a verifier (schema §9.2);
5. the recovered verifier is decrypted with its `key_version` and an AAD binding
   it to *this* transaction, then the code is exchanged with PKCE for tokens over
   the server's own HTTP client;
6. `identify` gives the Discord `subject`; `guilds.members.read` gives current
   membership and role IDs for the configured guild only;
7. the external identity `(discord, subject)` is resolved to a platform account,
   or an account is created (§5 of the schema contract);
8. a session is created (N-05, N-06, N-07) with `auth_method = discord_oauth`,
   and the login-transaction cookie is cleared;
9. the browser is redirected to the stored return target, or `/v1/characters`.

An error at 1–4 renders the safe login-failure view with a correlation ID (N-25)
and **no** provider error text. Discord unreachable at 5–6 → VM-03 degraded state.

**A non-member receives no session.** ADR 0004 requires the callback to *"reject
if the user is not a current member of that guild"* before a session is created,
and this contract follows it: step 8 does not run, the response is `403` rendering
VM-02, and the login transaction is still consumed so it cannot be replayed. A
person who authorizes the Discord application but is not in the guild therefore
leaves no session row, no token record and no account-linked state beyond the
audit event.

Caller state `N` in the matrices below is consequently **not** reachable through
login. It arises only when membership or the guild itself is lost *during* an
existing session — which is exactly the acceptance criterion *"revoked
membership/role is handled"* (plan §12 Phase 3), and the reason the state is
enumerated at all.

Audit: `auth.login.succeeded` or `auth.login.refused`, source `web`, capability
`guild_member` or `system`, with correlation ID and **never** the code, tokens,
state or verifier.

**R-05 `logout`.** `POST` only. Session + CSRF (N-17) + origin (§2.1). Revokes the
session row, deletes the account's stored OAuth token record (N-11), clears the
cookie, and audits `auth.logout`. A logout with a missing or stale CSRF token is
refused `403` — a forced logout is a real, if minor, nuisance attack, and the
uniform rule is easier to review than an exception.

**R-06 `emergency_login_page`.** Unauthenticated HTML, VM-04. Renders the WebAuthn
entry point and the recovery-grant form. It reveals **no** account existence: the
page is identical whether or not a credential is enrolled. It is reachable when
Discord is down — that is its purpose — and it is `noindex`.

**R-07/R-08 `emergency_webauthn_*`.** `application/json` over `fetch`, because the
WebAuthn API requires script-driven credential exchange. Both are unauthenticated
and rate-limited by N-32. Options are bound to a server-side challenge row with an
N-04 lifetime; the verify step checks challenge, RP ID and origin (N-60), user
verification, and the signature counter. A successful verification creates a
break-glass session (N-15, `auth_method = webauthn`). Both audit
`auth.emergency.webauthn.*` with the credential **record id**, never the public
key, never the raw assertion (§9.7 of the delivery plan).

**R-09 `emergency_recovery_login`.** Consumes a host-issued grant (N-14). The
submitted token is hashed and looked up; consumption is the same
single-statement `UPDATE … WHERE consumed_at IS NULL AND expires_at > now()
RETURNING` pattern, so a replay and a race both find nothing. Purpose-bound: a
grant row whose `purpose` is not `emergency_login` never matches. Creates a
break-glass session (N-15, `auth_method = recovery_grant`). Audits
`auth.emergency.recovery.consumed` naming the grant record id — never the token.
Rate limit N-33.

**R-10 `health`.** `application/json`: `{"status": "ok"|"degraded",
"checks": {...}, "version": "..."}`. Contains **no** secrets, no player data, no
identity, no database URL, no configuration values — only check names and
pass/fail (VM-16). It is **not published by Caddy**: it is reachable on the
loopback bind only (N-50). That is why it needs no authentication and why the
table below marks every browser caller state `–`.

### 4.2 P3.1 matrix

| # | Route | U | N | M | C | A | CA | BG | CSRF | Origin | Rate limit | Body |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R-01 | `root` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | – | – | – |
| R-02 | `login_page` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | – | – | – |
| R-03 | `oauth_start` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | – | N-18 | – |
| R-04 | `oauth_callback` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | – | N-18 | – |
| R-05 | `logout` | ✗ 401 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | required | required | – | 1 KiB |
| R-06 | `emergency_login_page` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | – | – | – |
| R-07 | `emergency_webauthn_options` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | required | N-32 | 4 KiB |
| R-08 | `emergency_webauthn_verify` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | required | N-32 | 16 KiB |
| R-09 | `emergency_recovery_login` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | required | N-33 | 4 KiB |
| R-10 | `health` | – | – | – | – | – | – | – | – | – | – | – |

“`✓`” on R-03/R-04/R-06–R-09 means *the route accepts the request*; it does not
mean the caller obtains anything. An existing session does not entitle a caller to
a break-glass session: R-08 and R-09 succeed only for the protected Server
Administrator account and only on presentation of the enrolled credential or a
valid grant.

## 5. P3.2 — member reads, character links and role-capability mappings

| # | Route name | Method | Path | Kind | Response |
|---|---|---|---|---|---|
| R-20 | `my_characters` | GET | `/v1/characters` | navigation | `200` HTML · VM-05 |
| R-21 | `character_detail` | GET | `/v1/characters/{character_id}` | navigation | `200` HTML · VM-06 |
| R-22 | `council_character_index` | GET | `/v1/council/characters` | navigation | `200` HTML · VM-07 |
| R-23 | `council_character_links` | GET | `/v1/council/characters/{character_id}/links` | navigation | `200` HTML · VM-08 |
| R-24 | `council_identity_search` | GET | `/v1/council/identity-search` | HTMX partial | `200` HTML fragment · VM-09 |
| R-25 | `council_link_grant` | POST | `/v1/council/characters/{character_id}/links` | form | `303` to R-23 |
| R-26 | `council_link_revoke` | POST | `/v1/council/characters/{character_id}/links/{access_id}/revoke` | form | `303` to R-23 |
| R-27 | `council_link_set_default` | POST | `/v1/council/characters/{character_id}/links/{access_id}/default` | form | `303` to R-23 |
| R-28 | `council_identity_migration` | GET | `/v1/council/identity-migration` | navigation | `200` HTML · VM-10 |
| R-29 | `council_identity_migration_confirm` | POST | `/v1/council/identity-migration/{proposal_id}/confirm` | form | `303` to R-28 |
| R-30 | `council_identity_migration_reject` | POST | `/v1/council/identity-migration/{proposal_id}/reject` | form | `303` to R-28 |
| R-31 | `council_field_profile` | GET | `/v1/council/field-profile` | navigation | `200` HTML · VM-11 |
| R-32 | `admin_role_capabilities` | GET | `/v1/admin/role-capabilities` | navigation | `200` HTML · VM-12 |
| R-33 | `admin_role_capability_create` | POST | `/v1/admin/role-capabilities` | form | `303` to R-32 |
| R-34 | `admin_role_capability_revoke` | POST | `/v1/admin/role-capabilities/{mapping_id}/revoke` | form | `303` to R-32 |
| R-35 | `account_identities` | GET | `/v1/account/identities` | navigation | `200` HTML · VM-13 |
| R-36 | `account_identity_link_start` | GET | `/v1/account/identities/link/start` | navigation | `200` HTML · VM-13 (`denied`) |
| R-37 | `account_identity_unlink` | POST | `/v1/account/identities/{identity_id}/unlink` | form | `303` to R-35 |
| R-38 | `admin_role_capability_ratify` | POST | `/v1/admin/role-capabilities/{mapping_id}/ratify` | form | `303` to R-32 |

R-38 is new in the P3.0 remediation. It is numbered after R-37 rather than
inserted beside R-33/R-34 because the identifiers R-35–R-37 are already cited in
this package's other artifacts, and renumbering an identifier to make a table
prettier is how cross-references quietly stop meaning what they say.

### 5.1 Route detail

**R-20 `my_characters`.** Lists characters with an active `character_access` row
for the caller's **platform account** (never for a Discord ID). Empty state is a
first-class outcome, not an error: a member with no links sees VM-05's empty
variant naming the Council as the route to a link. Sorted by default-character
first, then display name, then character id, so the order is stable. No
pagination in Phase 3: the bound is the number of characters one person may be
linked to; if that ever exceeds 50 the view truncates and says so (VM-05 carries
`truncated`). Audit: none — reads of one's own characters are not audited, per
plan §9.4 (*collect only necessary data*).

**R-21 `character_detail`.** Object-level authorization, and the single most
substituted identifier in the product. Permitted when the caller has an active
access row for this character, **or** holds Council (OD-37: Council reach is
role-derived, not an access row). Anything else is `404` (§2.3). Content is
limited to Phase 2 identity/snapshot data plus fields whose typed package is
already authoritative; every other field renders `migration deferred` with its
owning package from `data-migration-register.md` (VM-06). There is **no** edit
control, no form, and no `POST` sibling — that absence is the acceptance criterion
*"no Phase 3 route or form mutates character game state"*, and TC-STRUCT-01 is
what proves it.

**R-22/R-23 Council link administration.** R-22 is a bounded, searchable index of
characters (cursor pagination, N-21 bounds reused). R-23 shows one character's
access rows — active and historical — with grantor, reason, timestamps and
correlation IDs (VM-08). Council-only; `A` alone is refused `403`, because
administrator does not imply Council (OD-24, and
`AuthorizationContext.require_council` already encodes it).

**R-24 `council_identity_search`.** The HTMX partial behind the grant form. Takes
`q` (≤ 120 characters) and returns at most 25 candidate Discord identities from
the **membership projection**, showing snowflake, username and global name, with
an explicit “names are evidence, not identity” notice (OD-42, VM-09). It never
searches by display name to *establish* anything: the operator selects a
snowflake, and the snowflake is what the grant carries. Council-only. Bounded,
rate-limited by the general request path only; `q` shorter than 2 characters
returns the empty state rather than the whole guild.

**R-25 `council_link_grant`.** Council-only mutation. Inputs: target platform
account (resolved from the selected Discord snowflake server-side — the browser's
account id is not trusted), `access_kind` ∈ {`owner`, `co_owner`, `delegate`,
`viewer`}, required non-blank `reason`, and the character's optimistic `version`.
Enforces, in one transaction: the one-active-owner invariant
(`uq_character_access_one_active_owner`), the one-active-link invariant, the audit
event, and the version bump. A stale version is refused `409` with VM-19 and the
current state — never applied on top. Audit: `character_access.granted`, capability
`guild_council`, source `web`, before/after facts, correlation ID.

**R-26 `council_link_revoke`.** Sets `active = false` and `revoked_at`, keeping the
historical row (the schema's `revocation_state` check already requires this
pairing). Revoking the last active `owner` is permitted but produces the
reconciliation exception OD-37 §2 describes; the view says so. Audit:
`character_access.revoked`.

**R-27 `council_link_set_default`.** Moves the per-account default character.
Enforced by `uq_character_access_one_active_default_per_user`, which P3.2's
migration re-expresses on the platform account (see the schema contract §7).
Audit: `character_access.default_changed`.

**R-28–R-30 identity-evidence migration.** The Sheet-era `Characters C` /
`Players A/B/D` linkage evidence (migration register, *Player fields*) is
dry-run by an operator CLI, which writes **proposals**, not links. R-28 lists
them with their evidence and confidence; R-29 confirms one, creating the real
`character_access` row through the same service R-25 uses; R-30 rejects one with
a reason. Council-only. `Active DM` and player names are displayed as evidence and
carry an explicit non-authorization notice. Nothing is auto-confirmed, nothing is
confirmed in bulk, and an ambiguous proposal cannot be confirmed at all — it must
be resolved to one snowflake first. Audit: `identity_migration.confirmed` /
`.rejected`.

**R-29 activates immediately** (change-log entry C-P3.2-A, 2026-08-17; migration
contract §7.2). The confirmation is not an instruction recorded for a later apply:
in one database transaction it takes the character's optimistic version, writes the
`character_access` row through `CharacterAccessService.grant()` — the one R-25
uses, attributed to the **confirming** Council member's live server-side
authorization resolution — records the proposal's `confirmed` transition with its
reason and the access row it produced, and writes both the
`character_access.granted` and the `identity_migration.confirmed` audit events.
Any failure among them rolls back all of them. The confirmable subject is the one
C-04 recorded and R-28 displayed; R-29 resolves no name and accepts no subject,
account, actor, access kind or authority from the request body. The access kind a
confirmed proposal creates is `co_owner`, fixed by the service and shown on the
form before the Council member submits: `owner` is a decision taken explicitly
through R-25 under OD-37's one-active-owner invariant, not one a spreadsheet
column takes on Council's behalf. A proposal that is ambiguous, unresolved,
missing, already decided, or whose character or existing links have moved under
the form is refused with the current state and writes nothing.

**R-30 remains a rejection only.** It records a decision and its audit event and
can never create a link; nothing in its path reaches a grant.

**R-28 reports each confirmation's link as it stands today** (change-log entry
C-P3.2-C, 2026-08-17). A link created at R-29 may afterwards be revoked at R-26,
so R-28 reads `character_access.active` for the **exact**
`identity_link_proposals.granted_access_id` the confirmation recorded, and says
*"is active now"* only when that row is active. It does not infer activation from
another active link on the same character or account, and it does not re-decide
the proposal: the confirmation stays `confirmed` with its decider, reason and
audit events, rendered `confirmed-and-revoked` and counted in `confirmed_revoked`
rather than in `confirmed` (VM-10; migration contract §7.4). The read stays
bounded — one set-based query for the rendered page and one aggregate for the
run's totals, no per-row lookup.

**R-31 `council_field_profile`.** Read-only render of the versioned field profile
(`domain/foundry_profile.py`): each path's snapshot mode, each field's authority, and
for `legacy_authority_deferred` fields the owning package. Council and
administrator; both are entitled to read it and neither can change it — there is
no write route, because the profile is code under change control.

**R-32–R-34, R-38 role-capability mappings.** Administrator-only (OD-18, OD-24).
R-33 creates a mapping from a stable Discord role snowflake to a platform
capability; R-34 revokes one; R-38 ratifies an emergency-created one. The
protected bootstrap mapping (guild `1052698198180892733`, role
`1124405581298552933` → `platform_administrator`) cannot be revoked, edited,
demoted or shadowed: the database refuses it (schema contract §8), the application
refuses it, and both refusals are tested. `C` alone is refused `403`: Council does
not imply administrator any more than the reverse. Audit:
`role_capability.mapped` / `.revoked` / `.ratified` with the role snowflake and
capability, plus a `role_capability_mapping_events` row for **every attempt,
including every refusal**.

R-33 and R-34 additionally enforce the **administrator-continuity allowlist
(N-67)**, which is the remediation of the escalation described in schema §8.1:

1. The service resolves the caller's **administrator scope** — `full`, or
   `emergency_continuity` for a break-glass session (`BG`) and for an
   ordinary-provider session whose administrator capability comes only from
   emergency-provenance mappings (`AC`).
2. A continuity-scoped caller may create a mapping whose capability is exactly
   `platform_administrator`, and may revoke a non-protected mapping whose
   capability is exactly `platform_administrator`. Every other capability —
   `guild_council`, `dm`, `character_owner`, `guild_member` — is refused `403`
   with the typed code `emergency_scope_refused`, **before any row is read or
   written**, and the refusal is recorded.
3. The mapping is written with the creating session's scope and auth method, so
   a mapping created under continuity scope is itself `emergency_continuity` and
   confers only continuity-scoped authority (schema §8.1). The chain does not
   launder clean through an ordinary login.
4. The database refuses the same thing independently:
   `CHECK (created_under_scope = 'full' OR capability = 'platform_administrator')`.
   Neither control is the only one, which is the point.

**R-38 `admin_role_capability_ratify`.** The one operation that converts
emergency-derived authority into ordinary authority, and therefore the one that
must not be reachable from emergency-derived authority. Requires, all of them:
`auth_method = 'discord_oauth'`, administrator scope `full`, CSRF, origin, a
non-blank reason, and the mapping's optimistic `version`. It sets `ratified_at`
and `ratified_by_account_id` and flips `provenance` to `ordinary`, once and
irreversibly (schema §8 trigger). `BG` and `AC` are refused `403`; a `403` here is
not a defect to be worked around during an incident but the boundary itself —
ratification waits until an administrator can authenticate normally. Audit:
`role_capability.ratified`.

**R-35–R-37 account identities.** R-35 lists the caller's own external identities
(provider, subject, linked-at, last-used, state). R-36 begins linking an
*additional* identity to the existing account; per N-16 it requires strong
reauthentication first — in Phase 3 the only ordinary provider is Discord, so R-36
exists to make the boundary real and is refused with VM-13's `no_additional_provider`
state until a later approved provider package.

**R-36's table cell was corrected on 2026-08-19** (accepted D-03 correction, item
D-03-5). The §5 table's *Response* column read `303` to provider, which
contradicted this paragraph and the accepted implementation; it now reads `200`
HTML · VM-13 (`denied`), which is what the route has always answered. There is
nothing to redirect *to*: a redirect presupposes a second ordinary provider, and
Phase 3 has exactly one. The route answers `200` rendering
`account_identities.html` with `state="denied"` and
`additional_provider="no_additional_provider"`, so the refusal is a page a person
can read rather than a bounce to the provider they are already signed in with. A
second provider package is what makes this a redirect, and that is its work. The
matrix cell below is unchanged: `U` is still `✗ 303` to the login page, which is
§2.3's unauthenticated-navigation rule and a different thing entirely. R-37 unlinks, and **refuses** when
it would leave the account with no usable identity and no reviewed recovery route
(§9.5 of the delivery plan). Unlink marks the identity `retired`; it never deletes
the row, because historical audit attribution must stay readable (schema contract
§6.3). The last-identity decision is serialized on the stable platform-account
row and identity state is re-read under that lock, so concurrent requests aimed at
two different identities cannot both observe a count of two and retire both.
Audit: `identity.link_refused`, `identity.unlinked`.

### 5.2 P3.2 matrix

| # | Route | U | N | M | C | A | CA | BG | CSRF | Origin | Body |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R-20 | `my_characters` | ✗ 303 | ✗ 403 | ✓ | ✓ | ✗ 403 | ✓ | ✗ 403 | – | – | – |
| R-21 | `character_detail` | ✗ 303 | ✗ 403 | obj | ✓ | ✗ 403 | ✓ | ✗ 403 | – | – | – |
| R-22 | `council_character_index` | ✗ 303 | ✗ 403 | ✗ 403 | ✓ | ✗ 403 | ✓ | ✗ 403 | – | – | – |
| R-23 | `council_character_links` | ✗ 303 | ✗ 403 | ✗ 403 | ✓ | ✗ 403 | ✓ | ✗ 403 | – | – | – |
| R-24 | `council_identity_search` | ✗ 401 | ✗ 403 | ✗ 403 | ✓ | ✗ 403 | ✓ | ✗ 403 | – | – | – |
| R-25 | `council_link_grant` | ✗ 401 | ✗ 403 | ✗ 403 | ✓ | ✗ 403 | ✓ | ✗ 403 | required | required | 8 KiB |
| R-26 | `council_link_revoke` | ✗ 401 | ✗ 403 | ✗ 403 | ✓ | ✗ 403 | ✓ | ✗ 403 | required | required | 4 KiB |
| R-27 | `council_link_set_default` | ✗ 401 | ✗ 403 | ✗ 403 | ✓ | ✗ 403 | ✓ | ✗ 403 | required | required | 4 KiB |
| R-28 | `council_identity_migration` | ✗ 303 | ✗ 403 | ✗ 403 | ✓ | ✗ 403 | ✓ | ✗ 403 | – | – | – |
| R-29 | `..._confirm` | ✗ 401 | ✗ 403 | ✗ 403 | ✓ | ✗ 403 | ✓ | ✗ 403 | required | required | 8 KiB |
| R-30 | `..._reject` | ✗ 401 | ✗ 403 | ✗ 403 | ✓ | ✗ 403 | ✓ | ✗ 403 | required | required | 8 KiB |
| R-31 | `council_field_profile` | ✗ 303 | ✗ 403 | ✗ 403 | ✓ | ✓ | ✓ | ✗ 403 | – | – | – |
| R-32 | `admin_role_capabilities` | ✗ 303 | ✗ 403 | ✗ 403 | ✗ 403 | ✓ | ✓ | ✓ | – | – | – |
| R-33 | `admin_role_capability_create` | ✗ 401 | ✗ 403 | ✗ 403 | ✗ 403 | ✓ | ✓ | ✓ N-67 | required | required | 4 KiB |
| R-34 | `admin_role_capability_revoke` | ✗ 401 | ✗ 403 | ✗ 403 | ✗ 403 | ✓ | ✓ | ✓ N-67 | required | required | 4 KiB |
| R-35 | `account_identities` | ✗ 303 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | – | – |
| R-36 | `account_identity_link_start` | ✗ 303 | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ 403 | – | – | – |
| R-37 | `account_identity_unlink` | ✗ 401 | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ 403 | required | required | 4 KiB |
| R-38 | `admin_role_capability_ratify` | ✗ 401 | ✗ 403 | ✗ 403 | ✗ 403 | ✓ | ✓ | ✗ 403 | required | required | 4 KiB |

Four rows deserve a sentence, because they look like mistakes and are not:

- **`A` is refused on R-20/R-21.** A Platform Administrator who is not also a
  character owner has no business reading a character sheet; the operational role
  is not a game-data role (plan §4.1). `CA` may, through Council.
- **`BG` is permitted on R-32–R-34, but only within N-67.** That is the whole
  point of break-glass: an administrator locked out of Discord must be able to
  repair *administrator* mappings. N-65 confines it to that surface plus audit
  reads, and N-67 confines what it may write there to the
  `platform_administrator` capability — the remediation of the escalation in
  schema §8.1.
- **`BG` is refused on R-38.** Ratification is the door between emergency and
  ordinary authority, and a session on the emergency side of it does not hold the
  handle. This is the row that makes the allowlist more than a delay.
- **`BG` is refused on R-36/R-37.** An emergency session must not be able to
  re-point the account's own identities; that would convert a temporary
  authentication event into a permanent one.

## 6. P3.3 — snapshot import, durable jobs and audit search

| # | Route name | Method | Path | Kind | Response |
|---|---|---|---|---|---|
| R-40 | `council_snapshots` | GET | `/v1/council/snapshots` | navigation | `200` HTML · VM-14 |
| R-41 | `admin_snapshot_folder` | POST | `/v1/admin/snapshots/{snapshot_id}/folder` | form | `303` to R-40 |
| R-42 | `council_preview_job_create` | POST | `/v1/council/snapshots/{snapshot_id}/preview-jobs` | form | `303` to R-43 |
| R-43 | `council_job_page` | GET | `/v1/council/jobs/{job_id}` | navigation | `200` HTML · VM-15 |
| R-44 | `council_job_status` | GET | `/v1/council/jobs/{job_id}/status` | HTMX poll | `200` HTML fragment · VM-15 |
| R-45 | `council_job_cancel` | POST | `/v1/council/jobs/{job_id}/cancel` | form | `303` to R-43 |
| R-46 | `council_import_confirm` | POST | `/v1/council/jobs/{job_id}/apply` | form | `303` to R-43 |
| R-47 | `council_import_result` | GET | `/v1/council/imports/{import_id}` | navigation | `200` HTML · VM-17 |
| R-48 | `audit_search` | GET | `/v1/audit` | navigation | `200` HTML · VM-18 |
| R-49 | `audit_search_results` | GET | `/v1/audit/results` | HTMX partial | `200` HTML fragment · VM-18 |

### 6.1 Route detail

**R-40 `council_snapshots`.** Lists submitted snapshots that have not been applied,
with checksum (abbreviated for display, full on the detail row), world, exporter
version, Actor count, selected folder and received-at. Council **and**
administrator can see it — the administrator needs it to choose a folder — but the
preview and apply controls are Council-only, and the server enforces that
independently of what the page rendered.

**R-41 `admin_snapshot_folder`.** Platform-Administrator-only (plan §6.4). Sets the
Actor folder for a snapshot; default `/actors/Characters (active)`. Selecting a
folder **invalidates every non-terminal job and every completed-but-unconfirmed
preview for that snapshot**, transitioning them to `stale` in the same transaction
(state machine SM-05). This is the mandatory test *"an administrator folder/profile
change invalidates an existing Council preview"*. Council alone is refused `403`;
selecting a folder is not a game-policy act, and applying an import is not an
operational one. Audit: `snapshot.folder_selected`.

**R-42 `council_preview_job_create`.** Council-only. Enqueues a durable
`reconciliation_jobs` row of kind `preview` (N-27 states, N-42 admission bound).
Idempotent on a request key derived from `(snapshot, folder, profile version,
account, submitted nonce)`: a double-click returns the **existing** job's redirect
rather than creating a second. Returns `303` to R-43 — never the result, which does
not exist yet. Refusals: `queue_full` (N-42), `snapshot_absent`, `folder_unselected`,
`blocked_by_running_apply`. Audit: `reconciliation.job_queued`.

**R-43/R-44 job page and poll.** R-43 is the navigable page; R-44 is the HTMX
fragment it polls at no faster than N-22, with the server free to answer
`Retry-After` and back off. **Both are object-authorized on every single request**
(delivery plan §8.5): the job's requester and current Council capability are
re-checked, so a member who obtains a job UUID learns nothing — `403` before the
object is loaded, because they are not Council at all. A Council member who did not
request the job *may* view it: Council reach is role-derived (OD-37), and import
work is Council-wide business. The response carries the bounded summary only
(counts, issue codes, folder identity, checksum, profile version) — never Actor
names, never warning text drawn from the artifact, never raw bytes (delivery plan
§8.9). Audit: none for polling; a poll is a read of one's own guild's operational
state and auditing it would flood the append-only table.

**R-45 `council_job_cancel`.** Best effort (delivery plan §8.8). Sets
`cancel_requested_at`; a `queued` job becomes `cancelled` immediately, a `running`
job is cancelled at its next heartbeat, and a job whose apply has already committed
**cannot** be cancelled — the route answers `409` with VM-19 and the committed
result. Audit: `reconciliation.job_cancel_requested`.

**R-46 `council_import_confirm`.** The one route in Phase 3 that changes durable
character-identity state, and the most carefully bounded. Council-only, CSRF,
origin, and:

1. the submitted `preview_token` must equal the job's stored token (the Phase 2
   `SnapshotPreviewView.preview_token` mechanism, reused unchanged);
2. the job must be `completed` and within N-46;
3. current Council authorization is re-resolved **now**, not carried from the
   preview (plan §6.5, and `application/authorization.py`'s stated reason for
   existing);
4. checksum, selected folder, field-profile version and database aggregate
   versions are re-checked; any change is `stale` and applies nothing;
5. an `apply` job is enqueued with the caller's `request_key`, and the existing
   `SnapshotImportService.apply` performs the atomic commit, so idempotency comes
   from `uq_snapshot_imports_applied_input` and `snapshot_imports.request_key` —
   already built, already tested, not reimplemented.

Why an enqueue rather than an inline apply: the apply re-parses the same artifact,
and no real-data apply has ever been measured (§6.3). Double-click, retry and
two-browser concurrency all resolve to one durable effect and one success audit
event through the existing key. Audit: `reconciliation.apply_requested`, then the
existing `snapshot_imports` row and its audit event on commit.

**R-47 `council_import_result`.** The immutable receipt: status, counts, folder,
checksum, profile version, capability, correlation ID, warnings as bounded issue
**codes** (VM-17). Council and administrator (plan §6.4: import and reconciliation
audit history is visible to both). No download of the artifact exists anywhere in
the inventory — *"audit visibility does not by itself grant permission to download
the raw artifact"*.

**R-48/R-49 audit search.** Council and administrator only. Cursor pagination
(N-21, N-64), bounded filters (N-63), stable ordering `(occurred_at DESC, id DESC)`.
Filters: action prefix, entity type, entity id, capability, source, time range,
correlation ID. Renders VM-18, whose payload rendering rule is *structured
before/after facts only* — never raw snapshot bytes, never exception text, never
secrets (plan §6.5, *safe audit content*). There is deliberately **no** audit
export route, no audit mutation route and no audit deletion route: the application
exposes no such use case, and the restricted runtime role holds only
`SELECT, INSERT` on `audit_events` with a trigger refusing `UPDATE`/`DELETE`
(already implemented in migration 0002).

### 6.2 P3.3 matrix

| # | Route | U | N | M | C | A | CA | BG | CSRF | Origin | Body |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R-40 | `council_snapshots` | ✗ 303 | ✗ 403 | ✗ 403 | ✓ | ✓ | ✓ | ✗ 403 | – | – | – |
| R-41 | `admin_snapshot_folder` | ✗ 401 | ✗ 403 | ✗ 403 | ✗ 403 | ✓ | ✓ | ✗ 403 | required | required | 4 KiB |
| R-42 | `council_preview_job_create` | ✗ 401 | ✗ 403 | ✗ 403 | ✓ | ✗ 403 | ✓ | ✗ 403 | required | required | 4 KiB |
| R-43 | `council_job_page` | ✗ 303 | ✗ 403 | ✗ 403 | ✓ | ✗ 403 | ✓ | ✗ 403 | – | – | – |
| R-44 | `council_job_status` | ✗ 401 | ✗ 403 | ✗ 403 | ✓ | ✗ 403 | ✓ | ✗ 403 | – | – | – |
| R-45 | `council_job_cancel` | ✗ 401 | ✗ 403 | ✗ 403 | ✓ | ✗ 403 | ✓ | ✗ 403 | required | required | 4 KiB |
| R-46 | `council_import_confirm` | ✗ 401 | ✗ 403 | ✗ 403 | ✓ | ✗ 403 | ✓ | ✗ 403 | required | required | 8 KiB |
| R-47 | `council_import_result` | ✗ 303 | ✗ 403 | ✗ 403 | ✓ | ✓ | ✓ | ✗ 403 | – | – | – |
| R-48 | `audit_search` | ✗ 303 | ✗ 403 | ✗ 403 | ✓ | ✓ | ✓ | ✓ | – | – | – |
| R-49 | `audit_search_results` | ✗ 401 | ✗ 403 | ✗ 403 | ✓ | ✓ | ✓ | ✓ | – | – | – |

`A` is refused on R-42 and R-46: **Platform Administrator alone cannot apply an
import** (plan §12 Phase 3 acceptance). `CA` may, and acts under capability
`guild_council`, which is what `AuthorizationContext.capability` already returns
when both are held.

### 6.3 Two findings that shaped this section

**F-1. The apply is as slow as the preview, and has never been measured.**
Rehearsal B previewed a real 32-Actor folder in 9.566 s and **applied nothing**
(`phase-2-supervised-rehearsal-b-2026-08-09.md` step 6). The 500-Actor benchmark's
1.31 s apply used synthetic Actors ~233× smaller than real ones — the calibration
error already recorded as RA-5. An apply re-parses the same artifact before it can
re-check anything, so its floor is the same ~9.6 s of parsing. Modelling apply as a
synchronous handler would repeat the mistake the plan corrected for preview.
**Therefore apply is a durable job of the same lifecycle**, and P3.3 must measure a
real-folder apply in staging before any production apply (traceability TC-PERF-02).

**F-2. Polling must not be able to enumerate.** N-22 bounds frequency, but the
stronger control is that `403` is returned on capability before the job row is read
(§2.3). A job UUID is therefore worth nothing to a member, and the delivery plan's
requirement that *"ordinary members cannot infer job existence"* holds without
relying on timing.

### 6.4 The CSP validation N-26 required

The accepted CSP contains `form-action 'self'`. Chrome and Firefox enforce
`form-action` across the **redirect chain** that a form submission produces, so a
`POST /v1/auth/discord/start` that answers `303` to `https://discord.com/...`
would be blocked by the policy the project already accepted. Three options were
considered:

| Option | Effect on N-26 | Verdict |
|---|---|---|
| `POST` start, add `https://discord.com` to `form-action` | **Weakens** the accepted CSP; requires documented security review (§7 of the delivery plan) | Rejected as the default; recorded as the fallback if option 3 is found wanting |
| `POST` start → `303` to a self route → `302` to Discord | Depends on browsers treating the second hop as a fresh navigation; behaviour is not uniform and would be a silent breakage on some browsers | Rejected: security behaviour must not rest on an ambiguity |
| **`GET` start as an ordinary navigation** (chosen) | **No change to N-26.** `form-action` never applies, because no form is submitted | **Recommended** |

The usual objection to a `GET` start is login CSRF. It does not apply here: the
callback (R-04) accepts a `state` only when it matches the `__Host-fb_login_txn`
cookie **in the browser that started the flow**. An attacker who initiates a flow
gets the transaction cookie in their own browser and cannot install it in the
victim's. Forcing a victim's browser to hit R-03 therefore starts a flow the victim
themselves completes as themselves — a wasted rate-limit slot, not a session
confusion. The residual cost is that a link prefetcher can replace a pending
transaction; the failure is a safe, recoverable “please sign in again”. This is
recorded as residual risk RR-02.

`style-src 'self'` and `script-src 'self'` are compatible with vendored HTMX:
`hx-*` attributes are not inline scripts and need no `unsafe-inline`. **Gemini must
not use `hx-on:` handlers in P3.4** — those are inline script and would force a CSP
weakening. Recorded here because the constraint is a contract, not a style
preference.

## 7. Cross-cutting response contract

### 7.1 Outcomes every route defines

| Outcome | Representation | Rule |
|---|---|---|
| Success | `200` HTML, `200` fragment, or `303` + redirect | A mutation always answers `303` (post/redirect/get), so a refresh cannot resubmit |
| Empty | `200` with the view model's empty variant | Never `404`, never an error page. An empty list is a fact |
| Loading / polling | `200` fragment with `state = queued\|running` and a `Retry-After`-respecting poll hint | N-22 |
| Stale | `409` for a confirmation; `200` with `state = stale` for a status poll | A stale confirmation must not look like a server error |
| Denied | Per §2.3 | Body is the safe denial view, **VM-22 `DeniedView`**; no object detail, no reason beyond the category, and no field able to carry one |
| Validation failure | `422` with the form re-rendered and field-level messages | Never a bare `400`; the user must be able to correct it |
| Safe error | `500` with VM-20: a UUID correlation ID and nothing else (N-25) | Exception text, paths, SQL, tokens, Actor content and stack traces never reach the response or the log line the user can quote |

### 7.2 Security headers on every `/v1/*` response

`Content-Security-Policy` (N-26), `X-Content-Type-Options: nosniff`,
`Referrer-Policy: same-origin`, `Cross-Origin-Opener-Policy: same-origin`,
`Cross-Origin-Resource-Policy: same-origin`, `Permissions-Policy` denying
geolocation/camera/microphone/payment, `Cache-Control: no-store` on every
authenticated response, and HSTS at the Caddy boundary. `X-Frame-Options` is
omitted deliberately: `frame-ancestors 'none'` supersedes it and duplicating the
rule in two syntaxes is how they drift apart.

### 7.3 Session, cache and audit effects, by route class

| Route class | Session effect | Role-cache effect | Audit effect |
|---|---|---|---|
| Login/callback | Creates and rotates (N-08) | Populates the membership projection | `auth.login.*` |
| Break-glass | Creates a restricted session (N-15, N-65) | **None** — break-glass never touches the Discord projection | `auth.emergency.*` |
| Logout | Revokes; deletes OAuth tokens (N-11) | None | `auth.logout` |
| Protected read | Extends idle expiry; rotates on detected privilege change (N-08) | Refreshes when older than N-09, subject to N-10 | None |
| Council/admin mutation | Rotates on privilege change only | Forces a fresh resolution before the service runs | One append-only event per attempt, success or refusal |
| Job poll | Extends idle expiry | Refreshes per N-09 | None |
| Apply | Rotates on privilege change only | Fresh resolution at apply, per plan §6.5 | The existing `snapshot_imports` row plus its audit event |

## 8. Operator-only CLI surface (no HTTP route)

These are host-local commands, run by an operator with existing host authority.
None is exposed as an API — that is the §9.8 boundary of the delivery plan.

| # | Command | Purpose | Package |
|---|---|---|---|
| C-01 | `python -m tools.emergency_recovery issue` | Issue a hashed, single-use, purpose-bound 10-minute recovery grant (N-14, N-61). Prints the token **once** to the operator's terminal; stores only the hash | P3.1 |
| C-02 | `python -m tools.emergency_recovery revoke` | Invalidate outstanding grants | P3.1 |
| C-03 | `python -m tools.webauthn_enrollment` | Enroll or retire a break-glass credential for the protected account, host-local, with the operator named in the audit record | P3.1 |
| C-04 | `python -m tools.identity_migration --dry-run --player-tab Players` | Produce identity-evidence proposals and control totals from the legacy Sheet; writes no `character_access` row and never writes Google. Temporary migration utility, run from the separate operator environment of migration contract §7.7. Peter Duscha confirmed `Players` as the one-time source tab on 2026-08-17 (`C-P3.2-B`); the argument remains required so this migration input is explicit rather than a portal default | P3.2 |
| C-06 | `python -m tools.portal_kill_switch on\|off` | Engage or release the operator kill switch (N-56) without stopping the Discord bot or Foundry | P3.1 |
| C-07 | `python -m tools.session_revoke --account …` | Revoke every session for an account after a suspected compromise | P3.1 |

Each command audits with capability `system` or `platform_administrator`, the
named operator, a correlation ID, and never the secret it handled.

**C-05 is withdrawn** (change-log entry C-P3.2-A, 2026-08-17). It named a
`--apply` step that materialized confirmed identity proposals into
`character_access`. Under the maintainer's immediate-activation decision the
Council confirmation at R-29 creates the link itself, so there is nothing left for
a later step to materialize. The identifier is retired rather than reused, so that
a reference to C-05 in an older document reads as withdrawn rather than as some
other command.

## 9. Traceability

| Contract element | Plan / decision source | Owning package |
|---|---|---|
| Route set is closed; no game-state mutation | plan §12 Phase 3 acceptance; delivery plan §4 | P3.1–P3.3, tested continuously |
| Council uses stable role ID; administrator does not imply Council | OD-18, OD-24; `application/authorization.py` | P3.1/P3.2 |
| Council reach is role-derived, not an access row | OD-37 | P3.2 |
| One Council member is sufficient to import | plan §6.4, §8.2 | P3.3 |
| Administrator selects folder; cannot apply | plan §6.4; delivery plan §5 P3.3 | P3.3 |
| Ordinary users are read-only | OD-31; plan §4.3 | P3.1–P3.3 |
| `/info`-style object scoping (linked characters plus Council) | OD-16 | P3.2 (R-21) |
| Durable job, not a synchronous handler | plan §12 Phase 3 measured constraint; delivery plan §8 | P3.3 |
| Break-glass is administrator-only and Discord-independent | OD-43; delivery plan §9 | P3.1 |
| Emergency authority is not convertible into Council, character or import authority | D-3 (2026-08-13); N-65, N-67; schema §8.1 | P3.1/P3.2 |
| Provider-neutral account identity | OD-43; ADR 0010 (accepted) | P3.1/P3.2 |
| Audit is append-only and unexportable | plan §6.5; migration 0002 | P3.3 |
