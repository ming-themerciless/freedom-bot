# Phase 3 numeric policy register

Status: **Accepted 2026-08-13 at P3.G0** by Peter Duscha after Codex independent
architecture/security re-review. Acceptance includes corrected N-43, widened
N-65 and new N-67. Later evidence gates remain; acceptance does not claim that
the specified implementation tests have run.

Changed by the P3.0 remediation of the same date and accepted at the re-review:

| ID | Change | Why |
|---|---|---|
| N-43 | **Corrected definition accepted**, replacing the withheld one | The withheld semantics had no reachable terminal state (§3.2) |
| N-65 | **Subject widening accepted**, value and surface unchanged | The restriction must survive an ordinary login, or the escalation path stays open |
| N-67 | **Accepted** | The approved D-3 boundary requires a defined and tested administrator-continuity allowlist |

No other provisionally accepted value is changed, tightened or reinterpreted by
the remediation.

### Clarification of N-07, N-08 and N-15 (2026-08-15, OD-44 session-lifetime remediation)

**No numeric value changes.** These notes record what the accepted values already
meant, after review found the implementation and the surrounding prose reading
them more loosely than the delivery plan does. Each is a clarification of scope,
not a change requiring §5 change control.

| ID | Clarified as | Why the clarification was needed |
|---|---|---|
| N-07 | **12 hours from the login**, not from the most recent event in the session. The absolute bound belongs to the login at the root of a rotation chain and is written exactly once, when the session is created. An idle refresh never writes it, and a rotation inherits the predecessor's value rather than taking a fresh `now + 12h` | The delivered rotation set a fresh absolute expiration on each successor, so a chain of privilege rotations could extend one login indefinitely — 12 hours per rotation rather than 12 hours per login |
| N-08 | Rotation on privilege change **continues a session; it does not restart one.** The successor inherits account, authentication method, OAuth binding and absolute bound from the predecessor, and its idle window is clamped to that inherited bound. Rotation is available only to a session that is still live at the moment of the write | "Rotate on every detected privilege change" was read as issuing a new session with new bounds. It issues a new *row* for the same login |
| N-15 | The 15-minute idle window applies to **every** break-glass session — `webauthn` and `recovery_grant` alike — on **every** idle refresh, not only at creation. "No extension beyond the absolute bound" is a statement about the 60-minute absolute value specifically, and does not license the ordinary 60-minute idle window in the meantime | The delivered idle refresh applied N-06's 60 minutes to break-glass sessions, bounded only by the 60-minute absolute clamp. Formally inside "no extension beyond the absolute bound", but it made the 15-minute idle value inoperative for the whole life of the session |

Enforcement for all three is recorded in
[`phase-3-logical-schema.md`](phase-3-logical-schema.md) §9.1 and
[`phase-3-state-machines.md`](phase-3-state-machines.md) SM-02; evidence is
TC-AUTH-18 and TC-AUTH-19.

### Where the session bounds are enforced (2026-08-15, idle-policy-construction remediation)

**No numeric value changes, and no variable is renamed.** This records *where*
N-04, N-06, N-07, N-15 and N-66's session bounds became enforceable, after review
found that the environment reader was the only thing checking them.

`application/web/config.py` now holds `SESSION_CEILINGS`, a single table of
`(ceiling, policy id)` per field, and it is read by **both** the environment
reader and `SessionSettings.__post_init__`. Two consequences worth stating:

- an out-of-register `SessionSettings` cannot be constructed at all — not by the
  reader, a test, an operator tool or direct Python — where previously only the
  reader refused one, so `SessionSettings(..., emergency_idle_minutes=60, ...)`
  was an accepted object that made N-15 inoperative for every break-glass session
  in the graph built from it;
- the ceiling doubles as the accepted default, because a value that may only be
  tightened has nothing looser to fall back to. This is how the reader already
  behaved; it now takes the number from the register instead of restating it.

Every bound remains a **ceiling with a floor of 1** (S-10): a deployment may
tighten an accepted policy and never loosen it. Enforcement of the second half —
which authentication methods N-15 governs — is the explicit `_SESSION_CLASSES`
table in `application/web/capabilities.py`; a method absent from it refuses at
startup rather than inheriting a window.

### What these numbers *are* (2026-08-15, session-policy numeric-validation remediation)

**No numeric value changes, and no variable is renamed.** This records the
**type** half of the register, after review found the two enforcement gates
holding different answers to it.

`SESSION_CEILINGS` gave both gates the same *bounds* and left each to state
independently what a value of these fields may **be**.
`SessionSettings.__post_init__` said "an actual `int`, not a `bool`, positive,
within its ceiling"; the derived-policy gate said only `value < 1` and
`value > ceiling`. Two ordering comparisons are not a whole-number rule, because
`float("nan")` makes both of them false. A non-finite `max_sessions_per_account`
therefore reached `SessionPolicy`, and `len(live) >= maximum` was false for every
live-session count — **N-66 revoked nothing.**

The accepted type for every registered session-policy field is therefore recorded
here explicitly:

- an actual `int`, and **never** a `bool` (`bool` subclasses `int`, so `True`
  would be a maximum of one and `False` a maximum of zero — neither is a number
  an operator can have meant);
- **no** float, whether integral-looking (`10.0`), fractional, infinite or NaN;
  the rule is stated as a type so that it covers the class rather than the one
  non-finite value a review happened to find;
- positive, and no greater than its `SESSION_CEILINGS` entry.

`application/web/config.py` holds that as **one runtime definition**,
`session_policy_problem` / `session_policy_problems`, beside the ceilings table.
Both `SessionSettings.__post_init__` and `_validate_policy_values` in
`application/web/sessions.py` — the function `SessionPolicy.__post_init__` and
`SessionPolicy.derive()` both go through — call it. A restatement in either place
is the drift that produced the defect, so there is deliberately no second copy.
Evidence is TC-AUTH-19(l) and TC-SESS-08b.

### An **exact** built-in `int`, and one enforcement point per number (2026-08-15, settings-construction remediation)

**No numeric value changes, no variable is renamed, and no accepted bound moves.**
This records two corrections to *how* the numbers above are enforced.

**1. The accepted integer type is `type(value) is int`, not `isinstance`.** The
previous entry recorded the type half of the session register as "an actual
`int`, and never a `bool`", implemented as
`isinstance(value, int) and not isinstance(value, bool)`. That refuses `bool` and
every float and accepts **every other subclass of `int`**. An `int` subclass may
override `__lt__`, `__gt__`, `__le__` and `__ge__`, and Python gives the
right-hand operand's reflected comparison priority when the right-hand type is a
subclass of the left's — so `len(live) >= maximum` is answered by the *subclass*
when `maximum` is one. A subclass answering `False` to every comparison therefore
reproduced the NaN outcome exactly: it survived `SessionSettings` construction,
`dataclasses.replace()` and `SessionPolicy.derive()`, and N-66 revoked nothing.

The rule is stated as an exact type for the same reason the float rule was: it
covers the class rather than the one member of it a review happened to construct.
It is deliberately **not** expressed as `isinstance`, an annotation, a coercion, a
list of excluded subclasses, or a check of one comparison result — the last of
which would ask the value under test to grade itself.

**2. Every registered number has one runtime `PolicyBound`, and every gate calls
it.** `application/web/config.py` holds `PolicyBound` (minimum, maximum, policy
id) and `policy_number_problem`, which is now the single definition of accepted
type *and* range for every number in this register. Six tables cite it:

| Table | Numbers it holds |
|---|---|
| `SESSION_CEILINGS` / `SESSION_BOUNDS` | N-04, N-06, N-07, N-15, N-66 |
| `RATE_LIMIT_BOUNDS` | N-18, N-30, N-31, N-32, N-33 |
| `REQUEST_BOUNDS` | N-09, N-10, N-19, N-21, N-22, N-34 |
| `WEBAUTHN_BOUNDS` | N-14 |
| `DATABASE_POOL_BOUNDS` | N-53 |
| `WORKER_BOUNDS` | N-23, N-41, N-42, N-43, N-45 |

`SESSION_BOUNDS` is **derived** from `SESSION_CEILINGS` rather than written out
again, so the numbers still appear once. Each table is read by exactly two
places: the environment reader (`_Reader.registered_integer`) and the
`__post_init__` of the settings type that carries the field. The reader produces
its own operator-facing *wording* — a `ConfigurationError` names the variable and
never its value — but not its own decision. Since the accepted value of a
ceiling-with-a-floor is also the accepted default, `PolicyBound.default` is
derived rather than stored: a separately written default is a second number able
to drift from the bound it should equal.

Two register entries are not plain ceilings and are recorded as such: N-34's
proxy hop count is an **exact** value (neither zero nor two is a tightening), and
N-22's polling interval is a **floor with no accepted ceiling**, so none is
invented. No relationship between N-23's lease and heartbeat, or between N-09 and
N-10, is enforced anywhere, because no accepted document states one; see the open
question in
`../review/phase-3-p3-1-settings-construction-validation-remediation-submission.md`.

> **Corrected 2026-08-15 by the N-23 exact-lease remediation.** A **third** entry
> is not a plain ceiling: N-23's lease is an **exact** value of 60 seconds, and
> the implementation this paragraph described had it as a 1…60 ceiling. The
> open question referred to above is **withdrawn** — see the next section. This
> paragraph is left as written and corrected here rather than rewritten, because
> it is the record of what the settings-construction package delivered.

Evidence is TC-AUTH-19(m), TC-STRUCT-07 and TC-LIM-06. RAID I-09 and I-10 both
remain open pending re-review and maintainer acceptance.

### N-23's lease is a value, not a ceiling (2026-08-15, N-23 exact-lease remediation)

**No accepted value changes, no variable is renamed, and the N-23 row in §7 below
is unchanged and remains the authority.** This records a correction to how that
row was *implemented*, after independent review found the runtime entry reading
it more loosely than the row states.

The accepted row is:

```text
N-23 | Job lease | 60 seconds, heartbeat at most every 20 seconds
```

One sentence, two kinds of number. The lease is given as a **value**; the
heartbeat interval is given as a **maximum**. The settings-construction
remediation read both halves as ceilings and wrote
`PolicyBound(minimum=1, maximum=60, policy="N-23")`, which accepted every exact
integer from 1 to 60 as a lease.

That was not a permitted tightening. It contradicted three accepted documents
that read N-23 as a fixed 60:

| Document | What it states |
|---|---|
| [`phase-3-state-machines.md`](phase-3-state-machines.md) SM-05 | the renewal statement writes `lease_expires_at = now() + 60s` |
| [`phase-3-logical-schema.md`](phase-3-logical-schema.md) §10.1 | the claim and lease-renewal statements write the same 60, and recovery is bounded by `N-23 + N-44` = 60 s + 15 s |
| [`phase-3-operational-contract.md`](phase-3-operational-contract.md) | the reaper's liveness signal and the wedged-worker procedure are both calculated from a 60-second lease |

It was also operationally wrong in its own terms: under a one-second lease,
ordinary heartbeat scheduling — accepted up to every 20 seconds — would lose a
live claim between beats.

`application/web/config.py` therefore now holds

```python
"lease_seconds": PolicyBound(minimum=60, maximum=60, policy="N-23"),
```

the same exact-value shape N-41's `concurrency` and N-34's `trusted_proxy_hops`
already had. `heartbeat_seconds` is **unchanged** at a ceiling of 20 with a floor
of 1, because "at most every 20 seconds" is a maximum. Either side of an exact
value is refused as `S-10`, since neither side is a tightening.

**The lease/heartbeat ordering question is withdrawn, not answered.**
`lease_seconds=1, heartbeat_seconds=20` was recorded as an in-register
configuration proving that an ordering rule was missing. It was never in the
register; it was in the implementation. With the lease at exactly 60, every
accepted heartbeat is already far inside every accepted lease, so **no ordering
rule was added and none is needed**. **No relationship involving N-45 has been
accepted**, and none may be added without a separately accepted policy decision.
Nothing about N-23 blocks P3.3; what P3.3 still owns is the *consumer* evidence
for the worker's lease, heartbeat, attempt, timeout and queue bounds.

Evidence is TC-STRUCT-07 and TC-LIM-06, extended; the submission is
`../review/phase-3-p3-1-n-23-exact-lease-remediation-submission.md`. RAID I-09
and I-10 both remain open pending re-review and maintainer acceptance.

Package: P3.0 · Owner: Claude (Working Technical Lead) · Baseline:
implementation plan v1.5, `docs/review/phase-3-delivery-plan.md` accepted
2026-08-13.

## 1. Why this file exists

The P3.0 prompt requires that *"every numeric policy has one authoritative
definition"* and that conflicting copies are not created. This register is that
single index. Every other P3.0 artifact cites a **policy ID** (`N-nn`) instead of
restating a number.

Two kinds of row appear:

| Origin | Meaning |
|---|---|
| **Accepted** | The value was accepted by Peter Duscha on 2026-08-13 in `docs/review/phase-3-delivery-plan.md` §7 or §8. **That document is authoritative.** The value is mirrored here once, for reviewer convenience; a disagreement between the two is a defect in *this* file and is resolved in favour of the delivery plan. |
| **Proposed (P3.0)** | P3.0 is the definer. The value has **no acceptance yet** and is listed in the P3.0 handoff as a decision requiring Peter. |

There is exactly one mirror (this file) and no other. If a P3.1–P3.5 artifact
needs a number, it cites the ID.

## 2. Accepted values (delivery plan §7 and §8 are authoritative)

| ID | Policy | Accepted value | Source |
|---|---|---|---|
| N-01 | Production origin | exactly `https://freedom-blades.rpgworld.org` | §7; OD-19 |
| N-02 | OAuth redirect URI | exactly `https://freedom-blades.rpgworld.org/auth/discord/callback` | §7 |
| N-03 | OAuth scopes | `identify guilds.members.read` only | §7; ADR 0004 |
| N-04 | OAuth state/PKCE transaction | single use; 10-minute maximum | §7 |
| N-05 | Session cookie | host-only opaque identifier; `Secure`, `HttpOnly`, `SameSite=Lax`, `Path=/`; no `Domain` | §7 |
| N-06 | Session idle expiry | 60 minutes | §7 |
| N-07 | Session absolute expiry | 12 hours | §7 |
| N-08 | Session rotation | on login and on every detected privilege change | §7 |
| N-09 | Membership/role cache | 5 minutes maximum | §7 |
| N-10 | Discord outage behaviour | mutations fail immediately; protected reads may use a previously successful membership result for at most 15 minutes total, then fail closed | §7 |
| N-11 | OAuth token retention | encrypted server-side only; deleted on logout/revocation and no later than the session's absolute expiry unless an active refresh operation requires it | §7 |
| N-12 | Break-glass privilege ceiling | Platform Administrator only; never Council, character ownership or import-apply authority by implication | §7; OD-24; OD-43 |
| N-13 | Break-glass primary credential | at least two pre-enrolled WebAuthn/passkey credentials; no permanent local password | §7 |
| N-14 | Break-glass recovery grant | host-local operator command only; random; stored only as a hash; single use; 10-minute expiry; purpose-bound to recovery login; fully audited without storing the token | §7 |
| N-15 | Break-glass session | 15-minute idle, 60-minute absolute; rotate on login; no extension beyond the absolute bound | §7 |
| N-16 | External identity linking | exact provider plus immutable provider subject; no display-name or email auto-link; strong reauthentication and audited confirmation required | §7; §9.2; OD-43 |
| N-17 | CSRF | session-bound synchronizer token on every cookie-authenticated mutation; rotates with the session; rejected before the application service runs | §7 |
| N-18 | Authentication rate limit | 10 OAuth starts and 20 callbacks per source IP per 10 minutes | §7 |
| N-19 | General request body | 1 MiB, except the existing snapshot submission/import path | §7 |
| N-20 | Snapshot body | existing accepted 64 MiB, 500 Actors, depth 64 and package parser limits; proxy and application limits must match | §7; ADR 0009 |
| N-21 | Audit pagination | default 50, maximum 100 records per page; stable cursor; no unbounded offset scan | §7 |
| N-22 | Reconciliation polling | no faster than every 2 seconds; server may back off; response contains no raw artifact | §7 |
| N-23 | Job lease | 60 seconds, heartbeat at most every 20 seconds; an expired lease is recoverable, never proof of failure | §7; §8.3 |
| N-24 | Job result metadata retention | 30 days for preview/job presentation records unless an applied import/audit rule requires indefinite typed history; raw artifacts follow the existing snapshot-retention procedure (change-log C-8) | §7 |
| N-25 | Safe error correlation | UUID correlation ID returned; exception text, paths, SQL, tokens and raw Actor content omitted | §7 |
| N-26 | CSP starting point | `default-src 'self'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'; form-action 'self'; img-src 'self' data:; script-src 'self'; style-src 'self'` | §7 |
| N-27 | Job states | exactly `queued`, `running`, `completed`, `stale`, `failed`, `cancelled` | §8.2 |

**N-26 validation result.** P3.0 validated the CSP against the exact Discord
authorization redirect and vendored HTMX and concluded it can stand **unweakened**
if OAuth start is an ordinary navigation rather than a form submission. See
`phase-3-route-authorization-contract.md` §6 and `phase-3-threat-model.md` T-04.
The alternative — adding `https://discord.com` to `form-action` — is a documented
weakening and is recorded there as the rejected option.

## 3. Values defined by P3.0 and accepted at P3.G0

These are the numbers the delivery plan deliberately left to P3.0, plus the ones
P3.0 found were missing. Peter accepted each at P3.G0.

### 3.1 Rate limiting and authentication abuse

| ID | Policy | Proposed value | Rationale |
|---|---|---|---|
| N-30 | Rate-limiter storage and algorithm | PostgreSQL table `auth_rate_limits`, fixed 10-minute window keyed by `(bucket, window_start)`, incremented by one `INSERT … ON CONFLICT DO UPDATE … RETURNING` statement | §7 states an in-process limiter is insufficient across processes. PostgreSQL is already a required, shared, transactional dependency; adding Redis for one counter is not the smallest justified dependency set. The known cost of a fixed window is a 2× burst at the boundary, recorded as residual risk RR-03 |
| N-31 | Rate-limit window cleanup | rows with `window_start` older than 60 minutes are deleted opportunistically, at most once per minute per process | Bounds table growth without a scheduler |
| N-32 | WebAuthn assertion attempts | 5 per source IP per 10 minutes, and 10 per platform account per 60 minutes | §7 sets no break-glass limit; §9.7 requires break-glass attempts to be rate limited. Deliberately lower than N-18: the credential set is two keys held by one person |
| N-33 | Recovery-grant login attempts | 3 per source IP per 10 minutes, and 5 per grant record for all time | The grant is single-use, so more than a handful of attempts against one grant is an attack, not a retry |
| N-34 | Client address determination | exactly one proxy hop, trusted only when the transport peer is `127.0.0.1`; the right-most `X-Forwarded-For` entry is used; a request that reaches the app port from any other peer is refused | Bounds header spoofing; matches the loopback-only bind in OD-20 |

### 3.2 Durable job execution

| ID | Policy | Proposed value | Rationale |
|---|---|---|---|
| N-40 | Job execution process | a separate `freedom-worker` systemd service claims jobs; `freedom-web` never executes one | See `phase-3-operational-contract.md` §3. The measured 9.566-second preview is GIL-holding work (`json.loads` plus pure-Python NFC normalization), so executing it inside the web process stalls polling, health and every other request |
| N-41 | Worker job concurrency | 1 in-flight job per worker process; 1 worker process | Bounds peak memory on a host shared with three Foundry instances, the live bot and PostgreSQL (RAID R-24) |
| N-42 | Queue admission bound | at most 5 jobs in `queued` for the whole platform; a further request is refused with a typed `queue_full` result and no job row | Prevents an unbounded backlog of 10-second jobs |
| N-43 | Job attempt cap | **Corrected and accepted 2026-08-13.** `attempts` is **the number of claims made against a job**, incremented by the claim statement and by nothing else. At most **3**. A `queued` job always has a remaining attempt (`CHECK (state <> 'queued' OR attempts < 3)`). The reaper is the only writer of the expiry transition and takes it in **one statement with two branches**: an expired lease with `attempts < 3` returns to `queued`; an expired lease with `attempts = 3` goes **directly to `failed` with `attempts_exhausted`**. There is no fourth claim | An expired lease is recoverable while the reaper remains live (N-23/N-44). The withheld version could strand an exhausted job. The bound is at most 225 seconds of lease-expiry recovery across three expired claims, assuming a live reaper and excluding queue waiting, successful execution time and N-45's separate runtime cap. Schema §10.1, SM-05 |
| N-44 | Abandoned-lease reaper interval | every 15 seconds | Three checks inside one 60-second lease. It is also the only writer of the expiry transition (N-43), so its liveness bounds how long a job can sit with a dead lease: `N-23 + N-44` per remaining attempt |
| N-45 | Per-attempt runtime cap | soft warning at 30 seconds; hard cap 300 seconds, after which the attempt is abandoned and the job returns to `queued` (subject to N-43) | 300 s is ~31× the measured 32-Actor preview and ~5× a hypothetical 500-Actor real folder at the measured 587 ms/MB |
| N-46 | Preview validity window | a `completed` preview older than 30 minutes is treated as `stale` and cannot be confirmed | Bounds the window in which authorization, snapshot, folder, profile and aggregate versions are assumed unchanged. Independent of, and additional to, the version rechecks |
| N-47 | Worker memory ceiling | systemd `MemoryMax=1G` for `freedom-worker`; a job killed by the ceiling is an abandoned attempt, not a failure verdict | Peak resident size for a parsed real folder is **not measured**; 1 GiB is a guard, and staging measurement is required before production (RR-05) |

### 3.3 Transport, database and process bounds

| ID | Policy | Proposed value | Rationale |
|---|---|---|---|
| N-50 | Application bind | `127.0.0.1:8000` for `freedom-web`; the worker exposes no listener | OD-20; topology §4 |
| N-51 | HTTP read timeout | 30 seconds for every browser route; the existing snapshot submission route keeps its accepted 64 MiB/300-second budget | Browser routes carry at most N-19 |
| N-52 | HTTP keep-alive / graceful shutdown | 5-second keep-alive; 30-second graceful shutdown | A shutdown longer than the lease (N-23) would let a restarting process hold a claim it cannot heartbeat |
| N-53 | Web database pool | `pool_size=5`, `max_overflow=5`, `pool_timeout=5s`, `statement_timeout=10s` | Bounds co-located database load; a web request that needs more than 10 s of SQL is a defect |
| N-54 | Worker database pool | `pool_size=2`, `max_overflow=0`, `statement_timeout=120s` | The apply transaction is the only long statement |
| N-55 | Caddy body limit | 1 MiB for every browser route; 64 MiB only on the existing submission route | Proxy and application limits must match (N-19, N-20) |
| N-56 | Kill-switch poll | the kill-switch file is stat-ed at most once per second per process | Bounds syscall cost while keeping the switch effective within a second |

### 3.4 Identity, session and administration bounds

| ID | Policy | Proposed value | Rationale |
|---|---|---|---|
| N-60 | WebAuthn relying party | RP ID exactly `freedom-blades.rpgworld.org`; allowed origin exactly N-01; user verification **required**; attestation `none`; discoverable credentials permitted but not required | RP ID must not be a registrable-domain suffix shared with the Foundry hosts |
| N-61 | Outstanding recovery grants | at most one unconsumed, unexpired grant per platform account; issuing a second invalidates the first in the same transaction | Two live grants double the window with no operational benefit |
| N-62 | Role-capability mappings | at most 50 active mappings per guild | Bounds capability resolution and the administration view |
| N-63 | Audit search input bounds | free-text filter at most 120 characters; at most 5 simultaneous filters; time range at most 366 days per query | Bounds query cost on an append-only table that grows forever |
| N-64 | Pagination cursor | opaque, HMAC-signed `(occurred_at, id)` pair; an unverifiable cursor is refused, never silently reset to page one | A silently reset cursor hides tampering |
| N-65 | Continuity-scoped surface | a **continuity-scoped** session may reach only the identity/capability administration and audit-read surface; every import, preview, apply and folder-selection route refuses it | Tightening beyond N-12. Emergency access exists to restore administrative continuity, not to operate imports. **Subject widening accepted at P3.G0** from "a break-glass session" to "a continuity-scoped session", which is every break-glass session **plus** an ordinary-provider session whose administrator capability descends only from emergency-provenance mappings. The value and surface are unchanged; the restriction can no longer be shed by logging in through Discord |
| N-66 | Concurrent sessions | at most 10 active sessions per platform account; creating an 11th revokes the oldest and audits the revocation | Bounds session-table growth and limits an undetected stolen-session population |
| N-67 | Break-glass mapping allowlist (**accepted at P3.G0**) | A continuity-scoped caller may perform exactly two role-capability operations: **create** a mapping whose capability is `platform_administrator`, and **revoke** a non-protected mapping whose capability is `platform_administrator`. Every other capability, and every other operation including ratification (R-38), is refused `403 emergency_scope_refused`. Enforced in the application service, by `CHECK (created_under_scope = 'full' OR capability = 'platform_administrator')`, and by the N-65 route surface — three controls, none of them the session's own capability set | Emergency authority must not be convertible into later Council, character or import authority. An allowlist alone is insufficient, so N-67 travels with mapping **provenance** (schema §8.1, SM-07); without provenance, a break-glass session maps a role to administrator, logs in ordinarily, and then maps anything at all |

## 4. Numbers P3.0 deliberately does **not** define

| Subject | Why not, and who owns it |
|---|---|
| Production Caddy connection/concurrency limits | Requires the Operations Owner's view of the host's existing Foundry and bot load. Owned by the P3.5 staging rehearsal and the deployment gate |
| Firewall rules for ports 30001–30003 | OD-25 is an open Operations Owner verification. P3.0 must not claim the firewall is configured |
| Backup retention and off-host copy | OD-21 left these as operational configuration before production data exists |
| Real-folder apply runtime | **Never measured.** Rehearsal B previewed only and applied nothing. P3.3 must measure it in staging before any production apply |
| Monitoring alert thresholds | Depend on measured staging behaviour (RR-05) |

## 5. Change control

A change to an **Accepted** row follows the delivery plan's change-control and
security-review requirements (§7). A change to a **Proposed** row before P3.G0 is
an ordinary revision of this package. After P3.G0 it is a change request against
the accepted contract.

Tightening N-26 requires no policy decision; weakening it does (§7).
