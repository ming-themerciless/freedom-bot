# Phase 3 threat model

Status: **Accepted 2026-08-13 at P3.G0** after independent architecture and
security-focused re-review. Verification remains assigned to later packages.

Remediated in this revision: **T-10b is new** — indirect escalation from a
break-glass session through a role-capability mapping and a later ordinary login,
which T-10 did not cover and which the first revision's controls did not stop.
T-52 and T-53 are corrected. RR-13 and RR-14 are new residuals. The model now
carries 54 threat entries.

Package: P3.0 · Owner: Claude · Scope: the `freedom-web` portal, the
`freedom-worker` process, their PostgreSQL state and their host boundary, from
P3.1 through P3.5.

Amended 2026-08-14 by the OD-44 re-review remediation, **by addition**: T-05b
(cross-provider completion) and T-05c (a branching or crossing rotation chain)
are new; RR-15 is recorded closed by T-05c's controls, with its original text
preserved. No threat entry was removed or rewritten.

Amended 2026-08-15 by the OD-44 session-lifetime remediation, **by addition**:
T-05d covers stale-record revival, absolute-lifetime extension and
method-confused idle refresh across both session-continuation operations. It is
adjacent to T-05c — same chain, different property — and is stated separately
rather than folded into it because its controls are the two conditional
statements rather than the rotation-chain constraints. No threat entry was
removed or rewritten.

Controls are cited as `N-nn` ([numeric register](phase-3-numeric-policy-register.md)),
`R-nn` ([routes](phase-3-route-authorization-contract.md)),
`SM-nn` ([state machines](phase-3-state-machines.md)),
`VM-nn` ([view models](phase-3-view-model-contract.md)), and `TC-…`
([test traceability](phase-3-test-traceability.md)).

**Extended 2026-08-19 under the accepted D-03 correction (change-log
`C-P3.4-A`, item D-03-1), by addition only.** §2 gains the M-01 `/static/*` entry
point and §4 gains T-54 (traversal and directory disclosure through the static
surface) and T-55 (session or authorization state leaking through a cached
asset), continuing the numbering after the existing T-53 rather than reusing an
identifier. No existing threat, control, residual risk or verification row is
rewritten, and no attacker profile changes.

## 1. Assets

| # | Asset | Why it matters | Worst realistic loss |
|---|---|---|---|
| A-01 | Character ownership (`character_access`) | It is the authorization fact for every future mutation, in the bot as well as the web | A player acts as another player's character |
| A-02 | Append-only audit and import history | The only record of who did what; corrections are compensating, never edits | History that cannot be trusted, which cannot be repaired by adding more history |
| A-03 | Platform accounts and external identities | Identity continuity across a provider change | Account takeover, or two people merged into one |
| A-04 | Sessions | Bearer authority for every request | Impersonation of a Council member |
| A-05 | Encrypted OAuth tokens | Read access to a member's Discord identity/membership | Provider-side impersonation of the platform |
| A-06 | Break-glass credentials and recovery grants | The last route to administrative control | Permanent, unnoticed administrative access |
| A-07 | Raw Foundry snapshots | Every exported Actor's full mechanics | Bulk disclosure of the guild's character data |
| A-08 | Role→capability mappings | The definition of who is Council or administrator | Silent privilege grant, or administrator lockout |
| A-09 | Reconciliation jobs and results | The path by which identity data enters PostgreSQL | Duplicate or unauthorized import |
| A-10 | Host availability (bot, three Foundry worlds, PostgreSQL) | Co-located with the portal (OD-20) | The portal degrades services that have nothing to do with it |
| A-11 | Member personal data (snowflakes, usernames, membership) | Privacy obligation (plan §9.4) | Disclosure of who plays here to someone who should not know |

## 2. Trust boundaries and entry points

```text
  Internet
     │  TLS
┌────▼──────────────────────────────────────────────┐  Boundary 1: Caddy
│ Caddy :443   exact host N-01, HSTS, body N-55     │  the only public surface
└────┬───────────────────────────────┬──────────────┘
     │ 127.0.0.1:8000                │ 127.0.0.1 (existing)
┌────▼───────────────┐      ┌────────▼─────────────┐  Boundary 2: application
│ freedom-web        │      │ snapshot submission  │  cookies vs service principal
│ cookies, CSRF,     │      │ WSGI (ADR 0009)      │
│ sessions           │      └──────────────────────┘
└────┬───────────────┘
     │ claims jobs (DB)                    Boundary 3: process
┌────▼───────────────┐
│ freedom-worker     │  no listener, parses artifacts
└────┬───────────────┘
     │ restricted runtime role             Boundary 4: database
┌────▼──────────────────────────────────────────────┐
│ PostgreSQL 16, loopback only, append-only triggers│
└───────────────────────────────────────────────────┘
     │                                     Boundary 5: outbound
     └──▶ discord.com (OAuth, membership)   Boundary 6: filesystem
     └──▶ artifact store 0700, outside the repository
```

| Entry point | Boundary | Authentication |
|---|---|---|
| `/v1/*`, `/auth/discord/callback` | 1 → 2 | Cookie session, or none |
| `/api/v1/foundry/snapshots` | 1 → 2 | Service-principal credential (Phase 2, unchanged) |
| `/static/*` (M-01) | 1 → 2 | **None, deliberately.** Public read-only assets. Host check applies; `GET`/`HEAD` only; reaches no session, no database, no application service. Added 2026-08-19 by the accepted D-03 correction |
| `/healthz` | loopback only, **not** published by Caddy | none needed |
| Operator CLI (C-01…C-07) | host shell | existing host/operator authority |
| Discord's callback redirect | 5 | state + PKCE + transaction cookie |

## 3. Attackers considered

| # | Attacker | Capability assumed |
|---|---|---|
| X-1 | Internet stranger | Can reach Caddy; no account, no guild membership |
| X-2 | Guild member | Valid session, ordinary capability, can read the HTML they are served |
| X-3 | Malicious or careless Council member | Full Council capability; the design bounds damage and guarantees attribution rather than preventing action |
| X-4 | Someone with a stolen session cookie | Bearer access until rotation, expiry or revocation |
| X-5 | Someone who compromises a Council member's Discord account | Legitimate-looking authentication |
| X-6 | Malicious Foundry module or browser extension on a GM's machine | Can observe what the GM types (RAID R-11 residual) |
| X-7 | Another local account on the shared host | Filesystem and process visibility; not root |
| X-8 | A future replacement identity provider behaving badly | Controls subjects it issues |
| X-9 | Automated scanner / credential-stuffing botnet | Volume, no targeting |

Out of scope, stated: a host root compromise, a PostgreSQL superuser, Discord
itself acting maliciously, and physical access. Each defeats the platform by
definition, and pretending otherwise would make the rest of this document less
honest.

## 4. Threats and controls

### OAuth, state, PKCE and return targets

| # | Threat | Attacker | Controls | Residual |
|---|---|---|---|---|
| T-01 | Authorization-code interception or injection | X-1 | PKCE S256; code exchanged server-side only; single-use transaction (SM-01); `state` compared in constant time against a stored hash | None material |
| T-02 | CSRF on the login flow (victim logged in as attacker) | X-1 | `state` is bound to the `__Host-fb_login_txn` cookie **in the browser that started the flow**; an attacker cannot install their transaction cookie in the victim's browser (route contract §6.4) | A prefetcher can supersede a pending transaction; failure is a safe "sign in again" (RR-02) |
| T-03 | Open redirect through the return target | X-1 | Return target is a **path** from a server-side allowlist, stored on the transaction row, check-constrained `LIKE '/%' AND NOT LIKE '//%'`, re-validated at use. No absolute URL reaches a `Location` header | None |
| T-04 | CSP blocks the Discord redirect, and the fix weakens the policy | — | Validated in P3.0: OAuth start is a `GET` navigation, so `form-action 'self'` never applies and N-26 stands **unweakened** | Fallback option (adding `https://discord.com` to `form-action`) is recorded as requiring security review if option 3 fails in practice |
| T-05 | Replay of a consumed transaction | X-1, X-4 | Conditional single-statement consumption; replay matches zero rows (SM-01) | None |
| T-05a | Session completion is invoked without, or more than once for, a consumed OAuth transaction | X-1, X-4 | Atomic `completion_claimed_at` update; required FK and unique `sessions.oauth_transaction_id` for Discord OAuth; claim, session and success audit share one provider-I/O-free transaction (SM-01, schema §9.1–§9.2). Evidence: TC-AUTH-13, including the direct internal call and the constraints with the application bypassed | A consumed-but-unclaimed transaction survives a provider refusal or process death until N-04's reaper removes it. It cannot be replayed at the consumption and no route can reach a completion for it, but a **future in-process caller** invoking `complete()` with that id inside the retention window would still find it claimable. Bounding the claim by `expires_at` was considered and rejected: it would refuse a legitimate login whose provider round trip crossed the N-04 boundary. Recorded for the P3.2 review as RR-05a |

### Account linking, issuer/subject and provider retirement

| # | Threat | Attacker | Controls | Residual |
|---|---|---|---|---|
| T-05b | A completion spends a consumed transaction using **another provider's** verified identity and tokens (added 2026-08-14, OD-44 §8.1) | X-1, X-4 | The claim compares the row's `provider_key` inside the claiming `UPDATE`, and the expected key is derived from `VerifiedCompletion` — one indivisible verified result whose identity and tokens must name the same provider, each stamped by the adapter that made the call from its own constant rather than from a provider response. A provider adapter additionally refuses to verify another provider's tokens, so the two facts cannot be laundered into agreement. Evidence: TC-AUTH-15 | The route is not trusted to have called the adapter the transaction was started with, and nothing here depends on it having done so. P3.1 registers one provider, so the finding was reachable only by an internal caller; a second registered provider would make it reachable by ordinary flows, which is why the control is durable rather than ordering |
| T-05c | A rotation chain branches, or a rotation crosses an account, an authentication method or an OAuth binding, producing a second live session for one login (added 2026-08-14, OD-44 §8) | X-4 | `UNIQUE (rotated_from_session_id) WHERE NOT NULL`; two composite foreign keys make a successor's account, method and binding its predecessor's own; the successor's insertion and the predecessor's revocation are one locked transactional operation requiring a live, unrotated predecessor; no creation path accepts a rotation label at all (SM-02, schema §9.1). Evidence: TC-AUTH-16, TC-AUTH-17 | Rotation is not yet wired into a request path; the P3.2 package that wires it must still handle `SessionRotationRefused` as an end-the-session outcome rather than a retry |
| T-06 | Account takeover through subject reuse or collision | X-8 | `UNIQUE (provider_key, subject)` covering retired rows; a colliding subject is **refused**, never merged | Refusal is a support incident for a legitimate reuse (RR-04) |
| T-07 | Account merge by name, username or email | X-2, X-8 | No such column exists on `external_identities`; no merge operation exists anywhere; N-16 | None structurally |
| T-08 | Issuer confusion between two OIDC providers | X-8 | `provider_key` binds the exact issuer byte-for-byte; startup refuses an unknown key | Depends on the future provider package's review |
| T-08b | An account stranded with no usable identity | X-3 (careless) | Unlink refuses when no other active identity and no reviewed recovery route exists (SM-04) | Operator must resolve stranded accounts after a whole-provider retirement |

### Break-glass and emergency escalation

| # | Threat | Attacker | Controls | Residual |
|---|---|---|---|---|
| T-09 | Emergency account becomes a permanent backdoor | X-1, X-3 | No permanent password; grants are single-use with a 10-minute life (N-14, N-61); credentials are phishing-resistant (N-13); sessions are 15/60 minutes with no extension (N-15) | A grant is a bearer token for its 10 minutes |
| T-10 | Emergency session acquires Council or import authority **directly** | X-3, X-4 | Capability resolution short-circuits on `auth_method` (SM-02); route-level refusal (N-65); both tested independently (TC-BG-04) | None if both controls hold; they are deliberately redundant |
| T-10b | Emergency session acquires that authority **indirectly**, by writing a role-capability mapping and then logging in through Discord | X-3, X-4, X-5 | **The finding the first revision missed.** N-67 allowlist (application service); `CHECK (created_under_scope = 'full' OR capability = 'platform_administrator')`; mapping **provenance**, which keeps administrator capability derived from an emergency mapping continuity-scoped through any number of ordinary logins; ratification (R-38) reachable only by a full-scope administrator on an ordinary-provider session (schema §8.1, SM-07). Proven as a *sequence* by TC-BG-05a…05e, not hop by hop | The emergency path can leave durable continuity-scoped administrator capability behind it — persistence, not escalation (RR-13) |
| T-11 | Attacker enrolls their own authenticator | X-4 | Enrollment is host-local C-03 only. **No web route exists** | Requires host compromise, which is out of scope |
| T-12 | Recovery grant issued remotely | X-1 | No HTTP route issues a grant (delivery plan §9.8) | None |
| T-13 | Grant replay, or a race between two redeemers | X-1 | Single-statement conditional consumption; one live grant per account (N-61); per-grant attempt cap (N-33) | None |
| T-14 | Break-glass endpoint used to enumerate accounts | X-1, X-9 | VM-04 is identical for every failure reason; rate limits N-32/N-33; audit distinguishes reasons, the response does not | Timing differences; mitigated by constant-time comparison on the hot path |
| T-15 | Cloned authenticator | X-5 | `sign_count` must not decrease; a decrease refuses the login and audits it | An authenticator that reports no counter cannot be checked this way; C-03 records which |

### Sessions, CSRF, origin and framing

| # | Threat | Attacker | Controls | Residual |
|---|---|---|---|---|
| T-16 | Session fixation | X-1 | Session id is generated server-side after authentication; rotation on login (N-08) | None |
| T-17 | Session theft by XSS | X-2 | `HttpOnly`; N-26 CSP with no inline script; autoescaping on with **zero** `\|safe` usages; no value ever rendered into a script context | An escaping defect in a template; TC-SEC-08 is the check |
| T-18 | Session theft over the network | X-1 | `Secure`, HSTS, TLS at Caddy, host-only `__Host-` prefix | None |
| T-19 | Session outliving a privilege change | X-2, X-5 | `privilege_fingerprint` recomputed from freshly resolved capability; rotation on change; N-09 cache bound (SM-02, SM-06) | Up to N-09 (5 minutes) of stale privilege on reads; accepted and stated |
| T-05d | **A session outlives its own expiry, or its emergency idle policy, because a continuation operation trusted a stale record** (added 2026-08-15, OD-44 session-lifetime review). Three ways: (a) *revival* — a caller holding a `SessionRecord` resolved while the session was valid rotates or refreshes it after its idle bound, and because an expired row is still unrevoked the write succeeds and pushes the bound into the future; (b) *lifetime extension* — a continuation writes a fresh `absolute_expires_at`, so repeated refreshes or privilege rotations extend one login without limit; (c) *method-confused idle refresh* — a WebAuthn or recovery-grant session is refreshed with N-06's 60-minute window instead of N-15's 15-minute one, so an emergency session idles for its whole absolute lifetime | X-2, X-4, X-5 | Liveness is tested **in the same conditional statement that performs the write**, never before it: `revoked_at IS NULL AND idle_expires_at > :now AND absolute_expires_at > :now`, strict at both bounds, in `rotate()`'s locked read and in `touch()`'s `UPDATE` (schema §9.1, SM-02). Neither writes `absolute_expires_at`: rotation inherits the predecessor's, touch clamps to it, so the chain-wide bound is set once by the login. The idle duration is selected inside the same statement by `CASE auth_method`, from an immutable validated `SessionIdlePolicy` injected once at composition, so it is a function of the persisted row and not of any argument. **Amended 2026-08-15 (second session-lifetime review):** this sentence previously said the duration was selected from the persisted method *and that method verified in the statement*, and concluded that the ordinary window could not reach a break-glass row "from either layer". That conclusion was false. The equality predicate refused a false method and could not see the `idle` argument beside it, so `touch(break_glass_id, idle=60 minutes, expected_auth_method=WEBAUTHN)` — the row's own method, with the wrong duration — matched and extended that session's idle window to its absolute bound, leaving N-15's 15 minutes inoperative for a `platform_administrator` session. The correction removes the duration and the method from the API rather than adding another predicate. **Amended again 2026-08-15 (third session-lifetime review):** removing the two arguments was not sufficient either, because the same authority moved into `SessionIdlePolicy`'s public constructor. It was a frozen dataclass taking `tuple[tuple[AuthMethod, timedelta], ...]`, and a mapping giving *every* method N-06's sixty minutes satisfies every invariant it validated (complete, duplicate-free, positive), so `SessionRepository(connection, idle_policy=that)` selected sixty minutes for persisted WebAuthn and recovery-grant rows — N-15 bypassed again, up to the sixty-minute emergency absolute bound. The invalid pairing had moved from the call into construction rather than ceasing to be representable. The policy now has **no public constructor**; its one factory takes `SessionSettings` and derives the mapping internally from `AuthMethod.is_break_glass`, so no supported shape at any layer names an `AuthMethod` beside a `timedelta`. `SessionSettings` remains the sole numeric source and any values its contract accepts are honoured, including an ordinary window shorter than the emergency one; the policy owns only the classification. One instance is built at the composition root and injected into both the repository and the service, which previously derived a second policy independently — equivalent in production, but two derivations that an alternate construction site could have made disagree. **Amended a fourth time 2026-08-15 (idle-policy-construction review): the two sentences above are retained as history and their conclusion was false.** `from_settings()` validated only positivity while `SessionSettings` was a public frozen dataclass with no construction-time validation, so `SessionSettings(..., emergency_idle_minutes=60, ...)` was an accepted object and the derived policy gave both break-glass methods sixty minutes (F1); the refresh statement was generated by iterating the policy's public, overridable `__iter__`, so an ordinary subclass inheriting the supported factory replaced the SQL's mapping while `for_method()` reported fifteen minutes (F2); and `SessionService` accepted a policy beside the repository without requiring them to be the same object, so a supported caller could create sessions under one window and refresh them under another (F3). `SessionIdlePolicy` is now **deleted**. `SessionSettings` enforces the accepted register in its own constructor, so an out-of-register instance cannot exist; `SessionRepository` **derives** its `SessionPolicy` from settings, reading each number once, and accepts no policy object, so there is nothing to subclass into the SQL; the `CASE` branches come from walking `AuthMethod` and asking the explicit `_SESSION_CLASSES` table, so an unclassified future method refuses at startup and at construction rather than inheriting a window; and `SessionService` reads its bounds from the repository and has no policy argument, so two bounds sources are not constructible. The statement, its predicates and the lifetime guarantees are unchanged. A zero-row write is the typed `SessionRotationRefused` / `SessionTouchRefused` and writes nothing. **No check constraint covers any of this** — `idle <= absolute` relates the bounds to each other, not to `now`. Evidence: TC-AUTH-18, TC-AUTH-19 | Neither operation is wired into a P3.1 request path, so this is a control proven at the service and repository boundary and **not** in request handling. The P3.2 package that wires them must treat both typed refusals as end-the-session outcomes rather than retries — the same residual carried by T-05c |
| T-20 | CSRF on a mutation | X-1 | Synchronizer token bound to session (N-17), verified **before** the application service; `Origin` must equal N-01; `SameSite=Lax` as defence in depth | None material |
| T-21 | Host-header or absolute-URI injection | X-1 | Exact host check before routing; Caddy matches one site block; no URL is built from the `Host` header | None |
| T-22 | CORS misuse | X-1 | No CORS header on any `/v1/*` route. The Phase 2 submission route keeps its **exact-origin allowlist** and is unchanged | None |
| T-23 | Clickjacking | X-1 | `frame-ancestors 'none'`; `X-Frame-Options` deliberately omitted as duplication (route contract §7.2) | Old browsers honouring only the header; accepted |
| T-24 | Cached authenticated page served to another user | X-1 | `Cache-Control: no-store` on every authenticated response; `Vary` on `Cookie` | None |

### Object substitution and confused deputy

| # | Threat | Attacker | Controls | Residual |
|---|---|---|---|---|
| T-25 | Reading another member's character by substituting a UUID | X-2 | Object-level check inside the reading transaction; `404` for object denials so identifiers cannot be probed (route contract §2.3); UUIDs are unguessable | None |
| T-26 | Acting on another character through a Council form | X-2 | Capability check precedes object resolution; every Council route refuses `M` with `403` before any lookup | None |
| T-27 | Confused deputy: the server acts on a browser-supplied account id | X-2, X-3 | The grant target is resolved server-side from a selected **snowflake**, never from an account id in the form (R-25); route contract §2.4 lists everything that is non-authoritative | None |
| T-28 | Job-id enumeration to learn about imports | X-2 | `403` on capability before the job row is read; N-22 bounds polling; results carry no artifact content | None |
| T-29 | Administrator applies an import by holding folder selection | X-3 | R-41 and R-46 are separate capabilities; `A` is refused on R-42/R-46; `AuthorizationContext.require_council` already encodes it | None |

### Stale membership and Discord outage

| # | Threat | Attacker | Controls | Residual |
|---|---|---|---|---|
| T-30 | Revoked Council role still applies an import | X-5 | Authority re-resolved **at apply**, in the apply transaction (SM-05); plan §6.5 | Up to N-09 on reads |
| T-31 | Discord outage causes fail-open | X-1 | N-10: mutations fail immediately, reads degrade for at most 15 minutes from the last success, then VM-03 `503` | The portal is unusable during a long outage — the intended trade |
| T-32 | Discord rate limiting mistaken for revocation | — | The projection distinguishes "refresh failed" from "membership absent"; a failure never writes an absence | A prolonged 429 storm exhausts the grace and fails closed |
| T-33 | Administrator locked out during an outage | X-3 (as a victim) | Break-glass is Discord-independent by construction (ADR 0010 D8) | Requires the credentials to have been enrolled beforehand (RAID assumption A-05) |

### Injection, rendering and disclosure

| # | Threat | Attacker | Controls | Residual |
|---|---|---|---|---|
| T-34 | XSS through an Actor name or a warning | X-3, X-6 | Warnings cross as **closed-vocabulary codes**, never artifact text (view contract §3.3); the few Actor names shown are `SafeText`, bounded, Council-only, autoescaped | A template defect; TC-SEC-08/TC-SEC-09 |
| T-35 | XSS through a grant reason or username | X-2, X-3 | Autoescaping; input bounds; no `\|safe` | Same |
| T-36 | SQL injection | X-1, X-2 | SQLAlchemy parameter binding throughout; no string-built SQL; cursors are signed opaque values, not fragments (N-64) | None |
| T-37 | Exception or log leakage | X-1 | VM-20 carries a UUID and nothing else (N-25); structured logging with no tokens, artifacts, SQL or player data; the existing `adapters/safe_logging.py` pattern | An unexpected third-party exception string reaching a log; TC-SEC-12 |
| T-38 | Raw snapshot disclosure | X-1, X-2, X-3 | **No route serves an artifact** anywhere in the inventory; results carry counts and codes; the store is `0700`, outside the repository, with checksum-derived names (Phase 2 R-10) | Backup handling, which is the existing operations procedure |
| T-39 | Audit payload leaking private data | X-2 | Audit reads are Council/admin only; VM-18 projects bounded key/before/after facts and redacts unrecognized keys | A future writer putting sensitive data in a payload; `application/audit.py`'s payload policy is the existing guard |
| T-40 | Personal data over-collection | — | Scopes limited to N-03; no email is ever requested or stored; IP and user-agent kept as salted digests only | None |

### Upload, parsing and resource abuse

| # | Threat | Attacker | Controls | Residual |
|---|---|---|---|---|
| T-41 | Oversized or malicious snapshot | X-6 | N-20 limits, unchanged from Phase 2: 64 MiB, 500 Actors, depth 64, documented format only, archives and path-bearing uploads rejected, parsing outside the transaction | Existing Phase 2 residuals |
| T-42 | Proxy and application limits disagree | X-1 | N-55 states both, and TC-SEC-06 tests parity rather than asserting it | Configuration drift; the test is the control |
| T-43 | Malicious filename | X-6 | Artifacts are named for their own SHA-256; no caller-supplied name is used for storage or display (Phase 2) | None |
| T-44 | Resource exhaustion via job flooding | X-3 | N-42 queue bound, N-41 concurrency 1, N-45 runtime cap, N-47 memory ceiling | A Council member can still occupy the queue; attribution is the control, not prevention |
| T-45 | Slow-loris / connection exhaustion | X-9 | Caddy timeouts, N-51/N-52 application timeouts, bounded keep-alive | Caddy tuning is an operations item (register §4) |
| T-46 | Credential stuffing and scanning | X-9 | There is **no password endpoint to stuff**; N-18/N-32/N-33 limits; `/healthz` unpublished; no directory listing | Fixed-window burst at boundaries (RR-03) |
| T-54 | **Path traversal or directory disclosure through the static surface.** Added 2026-08-19 with M-01 (accepted D-03 correction, item D-03-1) | X-1, X-9 | Four layers, and the first two are independent of each other: a URL grammar refusing any segment that does not start alphanumeric, checked before the filesystem is touched; Starlette's own `realpath` + `commonpath` containment against one root; `html=False`, so a directory is `404` with no listing and no implicit index; and a root that is **not configurable**, so there is no operator-supplied path to point elsewhere. Every refusal is the same safe `404` with no exception text, filesystem path or stack frame, so a grammar violation and a missing file are indistinguishable | The mount is only as contained as Starlette's containment check; TC-STATIC-02/03 assert both layers, and the grammar is proved load-bearing rather than decorative |
| T-55 | **Session or authorization state leaking through a cached asset.** Added 2026-08-19 with M-01 | X-1, X-9 | The surface is unauthenticated and reaches no session, so an asset response is byte-identical for every caller; it sets and refreshes **no** cookie, so an asset fetch cannot extend an idle timeout (N-06) or refresh a CSRF token; and its `Cache-Control` is decided by the filename's fingerprint rather than by whether the caller is signed in, so a shared cache never holds a caller-varying body under a cacheable header | A future asset that embedded per-caller data would defeat this by construction; the root is repository-owned and reviewed, and TC-STATIC-05/06 assert both properties |
| T-47 | Co-located host degradation | X-3, X-9 | Worker isolated as its own service with `MemoryMax`; bounded pools (N-53/N-54); job concurrency 1; kill switch stops the portal without stopping the bot or Foundry | Peak worker memory is **unmeasured** (RR-05) |

### Jobs, retries and audit integrity

| # | Threat | Attacker | Controls | Residual |
|---|---|---|---|---|
| T-48 | Duplicate apply from double-click or two browsers | X-3 | One live apply per input (partial unique index); the existing `uq_snapshot_imports_applied_input` and `request_key` fence the durable effect | None |
| T-49 | Lease theft or two workers on one attempt | X-7 | `FOR UPDATE SKIP LOCKED` claim; every write carries `AND lease_owner = $2` | A slow attempt may overlap a requeued one; the durable effect is still fenced (SM-05) |
| T-50 | Expired lease treated as failure, hiding a committed apply | — | The reaper requeues rather than failing; only attempt exhaustion fails; a retry finds the existing import and returns it as a duplicate | None |
| T-51 | Audit write fails while state commits | — | Both in one transaction (plan §6.5); a refusal event may follow in its own transaction with the same correlation ID and no claim of partial state | None |
| T-52 | Audit tampering | X-3, X-7 | Runtime role has `SELECT, INSERT` only; **migration 0002's** trigger refuses `UPDATE`/`DELETE` **even for the owner**, and it still does after the P3.1 constraint swap, which is DDL and never reaches a row trigger (TC-AUD-13); no application use case exists | Database-owner recovery outside the application, which is documented and visible |
| T-53 | Capability mapping used to escalate or to lock out the administrator | X-3 | Administrator-only routes; protected row is trigger-protected and insert-once; resolution is a union so additions cannot subtract; append-only mapping events recording refusals as well as changes | A **full-scope** administrator can grant Council to a role — that is the job, and it is audited. A continuity-scoped one cannot (N-67, T-10b) |

## 5. Residual risks

| # | Residual | Severity | Owner | Disposition |
|---|---|---|---|---|
| RR-01 | Up to N-09 (5 minutes) of stale privilege on **reads** after a Discord role change | Medium | Security Reviewer | Accepted in delivery plan §7; mutations always re-resolve |
| RR-02 | A link prefetcher can supersede a pending OAuth transaction | Low | Technical Lead | Accepted; failure is a safe retry |
| RR-03 | Fixed-window rate limiting permits a 2× burst at window boundaries | Low | Security Reviewer | Accepted for N-30; revisit if abuse is observed |
| RR-04 | A future OIDC provider reusing subjects causes refusal rather than takeover | Low | Data Owner | Accepted; the replacement-provider package must review it |
| RR-05 | Peak worker memory near N-20's 64 MiB input ceiling is **unmeasured**; N-47's `MemoryMax=2G` is a guard, not a measurement | Medium | Operations Owner | **Amended 2026-08-27.** The original text — *"Peak worker memory for a real folder is unmeasured; N-47's 1 GiB is a guard, not a measurement"*, treated as *"must be measured in staging before production (TC-PERF-01)"* — is kept for the record and is no longer true of a **real folder**: TC-PERF-01 measured a real 32-Actor folder at **302 MiB** on 2026-08-27. N-47 was raised 1 GiB → 2 GiB the same day (C-P3.5-Z) on the **extrapolation** to N-20's ceiling (~1 GiB, N-26), which is arithmetic on two real points and not an observation: no corpus near that ceiling exists, so nothing near it has been run. The residual is therefore narrowed, not removed, and its disposition is **proposed for closure at the Phase 3 gate** — this row does not close it |
| RR-06 | ~~Real-folder **apply** duration has never been measured~~ — **measured 2026-08-27** | Medium | Technical Lead | **Amended 2026-08-27.** The original text — *"Real-folder apply duration has never been measured (rehearsal B applied nothing)"*, treated as *"P3.3 measures it; the durable-job design already assumes it is slow"* — is kept for the record and is no longer true: TC-PERF-02 applied a real 32-Actor folder in **19,927 ms**, inside the N-45 300 s cap, with `/healthz` p95 at 61.2 ms and zero non-200 throughout. Disposition is **proposed for closure at the Phase 3 gate** — this row does not close it |
| RR-07 | Escaping correctness ultimately rests on templates Gemini writes in P3.4 | Medium | Security Reviewer | Autoescaping-on test, zero-`\|safe` test, and Codex source review at P3.G4 |
| RR-08 | Break-glass is a second authentication path and therefore a second surface | Medium | Security Reviewer | Accepted deliberately; ADR 0010 states why |
| RR-09 | A 10-minute recovery grant is a bearer token in the operator's terminal | Low | Operations Owner | Accepted; single use, one live, audited |
| RR-10 | OD-25 (Foundry ports 30001–30003 possibly reachable directly) is **still open** and shares this host | Medium | Operations Owner | **Not addressed by Phase 3.** P3.0 does not claim any firewall state |
| RR-11 | The bot remains unauthorized until Phase 5 (OD-17) | High | Product Owner | Outside Phase 3 scope; neither widened nor closed here |
| RR-12 | Assistive-technology and real-device evidence for the portal does not exist yet | Medium | Accessibility reviewer | Explicitly labelled in the test traceability as requiring later evidence |
| RR-13 | A break-glass session can leave a durable, continuity-scoped `platform_administrator` mapping behind it | Medium | Security Reviewer | **Accepted as the price of recovery.** It is persistence, not escalation: the capability reaches no Council, character or import route, provenance keeps it continuity-scoped through later ordinary logins, and ratification requires a full-scope administrator. Every attempt, including refusals, is in the append-only mapping-event table (T-10b) |
| RR-14 | `attempts` exhaustion now terminates a job from the reaper rather than from a claim, so a job's terminal `failed` state can be written by a process that never executed it | Low | Technical Lead | Accepted and deliberate. The alternative — waiting for a claim that the constraint forbids — is the defect being fixed. The failure is attributed to the job and its lease history, not to the reaper (SM-05) |
| RR-05a | A consumed-but-unclaimed OAuth transaction stays claimable by an **in-process** caller until N-04's reaper removes it | Low | Security Reviewer | Added 2026-08-14 with OD-44. No route can reach it: the callback's only path to `complete()` runs through a consumption that now matches zero rows. Bounding the claim by `expires_at` was considered and rejected — it would refuse a legitimate login whose provider round trip crossed the boundary. Any P3.2 package that adds a second completion caller must be reviewed against this row |
| RR-15 | The unique binding index is scoped to non-rotated sessions, so two concurrent rotations of one session could in principle produce two live sessions sharing a transaction id | Low | Security Reviewer | **Closed 2026-08-14 by the OD-44 §8 condition** — the branch is now refused by `UNIQUE (rotated_from_session_id) WHERE NOT NULL` and by the locked one-successor transition, with the race proved in TC-AUTH-16d. The original text is kept for the record: added 2026-08-14 with OD-44. **Pre-existing and not introduced here:** N-08 rotation could already produce two live sessions from one login, and no route calls `rotate_if_privileges_changed` in P3.1. An unscoped `UNIQUE` would not fix it either — it would make rotating a Discord OAuth session impossible. The P3.2 package that wires rotation into the request path must serialize it |

## 6. Verification mapping

| Threat group | Test group | Package |
|---|---|---|
| T-01…T-05 | TC-AUTH-01…08, TC-AUTH-12 | P3.1 |
| T-06…T-08b | TC-ID-01…07, TC-MIG-09…11 | P3.1/P3.2 |
| T-09…T-15 | TC-BG-01…09, TC-BG-15 | P3.1 |
| T-10b | TC-BG-05a…05e, TC-CAP-08…10 | P3.1/P3.2 |
| T-16…T-24 | TC-SESS-01…08, TC-SEC-01…07 | P3.1 |
| T-25…T-29 | TC-OBJ-01…06, TC-CAP-01…05 | P3.2/P3.3 |
| T-30…T-33 | TC-OUT-01…04 | P3.1/P3.3 |
| T-34…T-40 | TC-SEC-08…13 | P3.2–P3.4 |
| T-41…T-47 | TC-LIM-01…05, TC-PERF-01…02 | P3.1/P3.3/P3.5 |
| T-48…T-53 | TC-JOB-01…16, TC-AUD-01…06 | P3.3 |
| T-54…T-55 | TC-STATIC-01…07, TC-SEC-14 | D-03 correction (2026-08-19); re-verified in P3.4 |

## 7. What this model deliberately does not claim

- It does not claim the host firewall is configured (OD-25 is open).
- It does not claim staging exists (delivery plan §10 records it as open).
- It does not claim the portal is secure. It claims a set of controls, each with a
  named verification, and a set of residuals, each with an owner. The Phase 3 gate
  decision belongs to Peter after both reviews.
