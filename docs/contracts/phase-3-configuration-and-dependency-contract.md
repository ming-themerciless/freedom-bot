# Phase 3 configuration and dependency contract

Status: **Accepted 2026-08-13 at P3.G0.** Implementation and environment evidence
remain assigned to later packages.

### Where §2.2's bounds are enforced (2026-08-15, settings-construction remediation)

**No variable is added, renamed or removed, no accepted value changes, and §2.3's
fifteen refusals are unchanged.** This records only *where* the rules in §2.2 hold.

Principle 1 above says configuration is a frozen dataclass tree built once by
`WebSettings.from_environment(mapping)`. That describes the ordinary path and was
being read as though it were the only one: the five sub-dataclasses
`RateLimitSettings`, `BoundsSettings`, `WebAuthnSettings`,
`DatabasePoolSettings` and `WorkerSettings` had no construction-time validation,
so direct construction, `dataclasses.replace()` or a subclass attribute read
could produce an object outside the accepted register that the limiter,
middleware, WebAuthn verification, engine composition or future worker code then
trusted (RAID I-10).

Each of the five now enforces its own §2.2 rules in `__post_init__`, from the
numeric register described in
[`phase-3-numeric-policy-register.md`](phase-3-numeric-policy-register.md) — one
`PolicyBound` per field, read by both the environment reader and the constructor,
with integers required to be an **exact** built-in `int`. The accepted
non-numeric shapes in §2.2 are enforced with them: the relying-party identifier
is a lowercase hostname, allowed origins are a non-empty tuple of exact origins,
`WEB_WEBAUTHN_USER_VERIFICATION` is exactly `required` (N-60), `WORKER_ENABLED`
is an exact `bool`, and `WORKER_ARTIFACT_ROOT` is an absolute `Path` or absent.

Three consequences worth stating:

- the **relational** rules stay at the environment boundary, because the types do
  not carry both sides of them. S-05, S-09's relying-party/origin comparisons and
  S-02's origin identity compare a value against `WEB_PUBLIC_ORIGIN` or
  `WEB_ALLOWED_HOSTS`, which no sub-dataclass holds;
- principle 2 — *every* problem reported, not the first — is preserved by the
  reader substituting the accepted value after recording a refusal, so a
  constructor cannot abort the collection. Two placeholders exist for the same
  reason (`unset.invalid` and `https://unset.invalid`, in the reserved `.invalid`
  TLD); neither is ever a value the process runs under, because a run that
  recorded a problem raises and returns no settings; and
- principle 5 is unaffected: the constructors name a field and its value, which
  is correct for values that are literals in code, a test or an operator tool.
  `ConfigurationError` remains the boundary that names variables and never values.

### `WORKER_LEASE_SECONDS` is N-23's one accepted value (2026-08-15, N-23 exact-lease remediation)

**No variable is added, renamed or removed, no accepted value changes, §2.3's
fifteen refusals are unchanged, and `.env.example` is unchanged** — it already
ships `WORKER_LEASE_SECONDS=60`.

§2.2's Worker table cites `WORKER_LEASE_SECONDS` / `_HEARTBEAT_SECONDS` to N-23,
and that citation is right. The section above described an implementation that
had read the citation as two ceilings. It is one sentence stating two different
kinds of number — a lease **value** of 60 seconds, and a heartbeat **maximum** of
20 seconds — so the runtime entry for the lease is now an exact value,
`PolicyBound(minimum=60, maximum=60, policy="N-23")`, alongside N-41's
`WORKER_CONCURRENCY` and N-34's `WEB_TRUSTED_PROXY_HOPS`.
`WORKER_HEARTBEAT_SECONDS` is unchanged as a ceiling of 20 with a floor of 1.

Two consequences for an operator:

- a `WORKER_LEASE_SECONDS` of 59 or 61 now refuses startup as `S-10`, naming the
  variable and never its value, exactly as any other out-of-register number
  does. Neither side of an exact value is a tightening;
- an **unset** `WORKER_LEASE_SECONDS` still means the accepted value, which is
  now the exact 60 rather than a ceiling to sit on. No deployment that was valid
  under the accepted register becomes invalid: the accepted lease was always 60.

The rationale, and the accepted documents that read N-23 as a fixed 60, are in
[`phase-3-numeric-policy-register.md`](phase-3-numeric-policy-register.md). No
worker behaviour, consumer or deployment topology changed; the worker's lease,
heartbeat, attempt, timeout and queue **consumers** remain P3.3's.

### One canonical settings graph per web process (2026-08-16, canonical-graph remediation)

**No variable is added, renamed or removed, no accepted value changes, §2.3's
fifteen refusals are unchanged, and `.env.example` is unchanged.** This records
only *which object* the rules above are enforced on.

The sections above make each settings type valid by construction. That is a
property of an object, not of a process: a web process could still hold **two**
valid graphs and use each in different places. It did. `WebComposition` retained
the caller's `WebSettings`, `create_app` accepted a `settings` argument *beside*
a `composition` built from something else, and the composition accepted a
ready-made identity provider carrying its own Discord configuration — so
middleware, cookies, digests and startup checks could read one graph while the
services and the OAuth adapter read another, with every graph individually valid.

The rule is now structural:

- `WebComposition.__init__` canonicalises the graph it is given —
  `canonical_settings` descends the whole tree declared in
  `CANONICAL_SETTINGS_GRAPH`, reading every field once and rebuilding the exact
  base types through the constructors that hold the register — and `self.settings`
  is that one object for the life of the process;
- `create_app` takes **exactly one** configuration authority: `settings`, from
  which it builds the composition, or a `composition` that already holds the
  canonical graph. Never both;
- a consumer that *retains* settings and reads them again later
  (`OAuthLoginService`, `BreakGlassService`, `DiscordIdentityProvider`) requires
  the canonical object rather than trusting its caller; and
- the Discord adapter is **built by the composition** from its own
  `settings.discord`. It is not an argument. A test double — which is not a
  Discord provider and holds no Discord configuration — remains injectable
  through an explicitly named test-adapter seam, and an injected `httpx` client
  supplies transport only: the provider's timeout still comes from
  `WEB_DISCORD_API_TIMEOUT_SECONDS`.

Two consequences worth stating:

- the environment boundary is unchanged in both directions. Canonicalisation
  happens *after* `from_environment`, which still aggregates every problem into
  one redacted `ConfigurationError`; and a graph built from the environment is
  already exact-base, so canonicalisation of an ordinary production
  configuration removes nothing; and
- the new refusals are typed (`SettingsAuthorityError`, a `TypeError`) and name a
  type or a field path and **never a configured value**, because the graphs they
  refuse hold every secret the process has.

### The provider and the engine are derived, not supplied (2026-08-16, provider/engine authority remediation)

**Appended, not a rewrite of the section above.** No variable is added, renamed
or removed, no accepted value changes, §2.3's refusals are unchanged, and
`.env.example` is unchanged. Two statements in the section above were weaker than
they read, and this records the correction.

The first was "a test double — which is not a Discord provider and holds no
Discord configuration — remains injectable through an explicitly named
test-adapter seam". `IdentityProvider` is a **structural protocol**, so refusing
a concrete `DiscordIdentityProvider` did not establish that what arrived was a
harmless double: a wrapper, a delegating adapter or an alternate implementation
could hold a second graph's client id, secret, redirect URI, scopes, guild and
endpoints, pass the exclusion, and serve R-03 and R-04. The parameter's *name*
was the only thing making it test-only.

The second was that `WebComposition` accepted an `engine` whole, justified by
`settings.database.url` having exactly one reader. One reader and an injected
engine do not make one authority; they make the configured database selection
**ignorable**. Running S-14 and S-15 against the injected engine proves that
engine is usable and at the expected revision, not that it is the database the
canonical graph names.

The rule is now:

- `WebComposition.__init__` takes `settings` and an optional HTTP **transport**,
  and nothing else. There is no `engine`, no `provider` and no `provider_double`
  parameter, and `create_app` exposes none either;
- the serving engine comes from `build_engine(self.settings)` and the identity
  provider from `build_provider(self.settings.discord, …)`, both called once,
  from the graph this composition canonicalised;
- `settings`, `engine` and `provider` are read-only properties over write-once
  private slots. A composition's dependencies cannot be replaced after the
  application that validated them was built, which a one-time startup comparison
  never established — `create_app`'s `_require_provider_from()` is **removed**
  rather than kept as a check with nothing left to detect;
- the routes close over the composition the factory accepted rather than reading
  `request.app.state.composition` per request, so `app.state` is a diagnostic
  reference and not a second route to a different provider or engine; and
- ownership of the engine is explicit: a composition disposes the engine it
  built and never one lent to it.

Test substitution is a `WebComposition` **subclass** in
`tests/web/composition_harness.py` overriding two protected hooks. It is not
reachable by passing an argument, it is not imported by any module under
`adapters/`, `application/`, `domain/`, `tools/` or `helpers/` (asserted, not
reviewed), and the engine it lends is re-checked against the suite's existing
two-layer disposable-target guards.

**Nothing is installed by this document.** No dependency is added, no
`requirements` file is edited, no `.env.example` line is written, and no
virtualenv is created. Those are P3.1 actions after P3.G0.

Package: P3.0 · Owner: Claude · Numbers are `N-nn` from
[`phase-3-numeric-policy-register.md`](phase-3-numeric-policy-register.md).

### Startup refusals are the application's, not the factory's (2026-08-16, lifecycle re-review)

**Appended, not a rewrite of §2.3.** No variable is added, renamed or removed, no
accepted value changes, no refusal is added, removed or reclassified, no
dependency changes, and `.env.example` is unchanged. What changes is *where* three
of §2.3's refusals are evaluated, and that is recorded here because §2.3 describes
them as running at startup and a reader could reasonably have taken "startup" to
mean "inside `create_app()`".

S-12, S-14 and S-15 are the three refusals that need a resource — the filesystem,
a database connection, a query — and they are the only ones `run_resource_checks`
evaluates. They used to run inside `create_app()`, between accepting the
composition and constructing the `FastAPI` object. On the production construction
path both process-lifetime resources — the identity provider's `httpx.AsyncClient`
and the owned SQLAlchemy engine with its N-53 pool — are already built by then, and
a refusal propagated out of the factory: no application was returned, so no ASGI
lifespan could execute, so `WebComposition.aclose()` had no caller on the one path
where the process was being told not to run. A composition that owns
process-lifetime resources has to release them on a **refused startup** as well as
on a normal shutdown.

They now run inside the lifespan the factory installs, closing over the exact
accepted composition and the same canonical graph object every route reads. Three
consequences an operator or a reviewer should read as contract:

- **A refusal is an ASGI startup failure.** The checks complete before
  `lifespan.startup.complete` is sent, so a refused portal never serves a request
  — the property §2.3 promises — and a server that receives
  `lifespan.startup.failed` stops rather than binding a socket. Under
  `infra/systemd/`, uvicorn exiting non-zero is what the supervisor sees, which is
  the same observable outcome as before and the reason §2.3's "raised, never
  `sys.exit()`" rule is unaffected.
- **`create_app()` returning is no longer a statement that the checks passed.**
  Entering the returned application's lifespan is. Any future caller that builds
  the application for a purpose other than serving it — a management command, a
  smoke test — must drive the lifespan to get the refusals, and must not
  reintroduce a factory-time call to get them earlier.
- **The refusal an operator sees is unchanged.** The original typed
  `ConfigurationError`, naming variables and never values, is what surfaces. If
  releasing the provider fails while that refusal is unwinding, the refusal stays
  at the head of the exception and the cleanup failure is attached beneath it in
  the same traceback: neither is hidden, and the one an operator must act on is
  not displaced by the one they cannot.

The checks cross the sync/async seam through `run_in_threadpool`, as every other
database unit of work in `adapters/web/app.py` does. In the factory they were
synchronous code on a synchronous call path; on a lifespan they would block the
event loop that has to answer the startup message, which `.agents/AGENTS.md`
forbids. This adds no dependency: `starlette.concurrency` is already the seam §1.2
accounts for.

Related, and recorded here for the same reason: `WebComposition.__init__` now
disposes an engine it built if a later construction step raises. That path
produced no composition, so nothing else could ever have released it.

### A composition serves one application startup (2026-08-16, composition-lifecycle re-review)

**Appended, not a rewrite of the section above.** No variable is added, renamed or
removed, no accepted value changes, no refusal is added, removed or reclassified,
no dependency changes, and `.env.example` is unchanged. What is added is one
refusal that is not a *configuration* refusal at all, and it is recorded here
because it fails ASGI startup in the same place S-12/S-14/S-15 now do and an
operator meeting it will look for it beside them.

The section above wired `WebComposition.aclose()` to the ASGI lifecycle so a
refused startup releases what a normal shutdown releases. That cleanup is
**permanent** — the identity provider's `httpx.AsyncClient` is closed and an owned
engine is disposed — and nothing was asked on the way *in*. So one composition
handed to two applications, or one application whose lifespan was entered a second
time, answered `lifespan.startup.complete` and served requests against a closed
Discord client until an OAuth route dereferenced it.

The resource checks cannot stand in for this and must not be extended to try.
`run_resource_checks(settings, engine)` never receives the provider, and
`Engine.dispose()` does not invalidate an engine — it discards the pool and lets
the next checkout build a replacement — so S-14 connects successfully and reports
a healthy database that nobody may use.

Three statements to read as contract:

- **`WebComposition` has one lifetime, and it is one-way.** `new -> started ->
  closing -> closed`. `claim_for_startup()` is the only transition out of `new`;
  every other state refuses it with `CompositionLifecycleError`, and the state
  cannot be moved backwards or sideways at all.
- **The lifespan claims the composition before anything else.** Before the
  resource checks and before any request is served, so a refusal is an ASGI
  startup failure exactly as a failed S-14 is: `lifespan.startup.failed`, never
  `lifespan.startup.complete`, and a server that receives it stops rather than
  binding a socket. A caller that builds the application for a purpose other than
  serving it gets the same rule — one composition per application it intends to
  start.
- **A refused startup releases nothing.** The claimant that already holds the
  composition is the one that closes it. An application refused the claim closes no
  provider and disposes no engine, because doing so would take live resources away
  from an application that is serving requests. `CompositionLifecycleError`, like
  every refusal at this boundary, names a state and a rule and no configured value.

`aclose()`'s contract is unchanged: at most once per composition, the guard moved
before the first `await` so an overlapping call cannot pass it, an owned engine
disposed in a `finally` even when closing the provider raises, a lent engine never
disposed, and the provider's failure re-raised rather than swallowed. That
idempotency covers a repeated or overlapping **cleanup** and has never been a
licence to start again.

## 1. Dependency proposal

### 1.1 Ground rules

`.agents/AGENTS.md`: *"Add dependencies deliberately and lock them reproducibly.
Do not introduce a framework for a small utility."* Delivery plan §5 P3.1:
*"deliberately bounded FastAPI, uvicorn, Jinja2, OAuth/HTTP client and test
dependencies"*. ADR 0002 fixed the stack; this section fixes the **set** and the
**pinning strategy**.

The web application gets its **own virtualenv** (topology §1: *"`freedom-web`
needs"* a separate one, because a shared venv couples the bot's dependency set to
the portal's). The Discord bot's `requirements.txt` is not touched.

### 1.2 Proposed production set — `requirements-web.txt`

| Package | Exact purpose | Pin | Why not something else |
|---|---|---|---|
| `fastapi` | HTTP application, routing, dependency injection, request validation | `>=0.115,<0.116` | ADR 0002. Starlette alone would mean hand-rolling validation and dependency wiring that FastAPI already does |
| `uvicorn[standard]` | ASGI server behind Caddy | `>=0.32,<0.33` | ADR 0002. `[standard]` brings `httptools` and `uvloop`, which are the reason the process can hold its N-51/N-52 timeouts |
| `jinja2` | Server-rendered templates | `>=3.1.4,<3.2` | ADR 0002; `3.1.4` is the floor because earlier versions carry known sandbox/XSS advisories |
| `itsdangerous` | Signing the pagination cursor (N-64) and the CSRF derivation helper | `>=2.2,<3` | ~40 lines of HMAC would otherwise be hand-written; this is the standard, audited implementation and is already a transitive Starlette optional |
| `httpx` | Outbound HTTP to Discord (token exchange, membership) with timeouts and connection limits | `>=0.27,<0.29` | `requests` is synchronous and blocks the event loop, which `.agents/AGENTS.md` forbids. `aiohttp` is a larger surface for the same two calls |
| `webauthn` (`py_webauthn`) | WebAuthn registration/assertion verification (N-13, N-60) | `>=2.2,<3` | Implementing FIDO2 assertion verification by hand is exactly the cryptographic own-goal a dependency exists to avoid |
| `cryptography` | AES-256-GCM for OAuth-token and PKCE-verifier encryption (schema §9.5) | `>=43,<45` | Already a transitive dependency of `py_webauthn`; naming it directly makes the pin explicit |
| `sqlalchemy` | Existing | inherit `>=2.0.36,<2.1` | Already the project's mapper (ADR 0003) |
| `alembic` | Existing | inherit `>=1.14.0,<2` | Already the project's migration tool |
| `psycopg[binary]` | Existing | inherit `>=3.2.3,<4` | Already the project's driver |
| `python-dotenv` | Existing | inherit `>=1.0.1` | Configuration loading, matching the bot's convention |

**Eleven packages, four of them already in the project.** No template-cache
library, no session library, no CSRF library, no rate-limit library, no Redis, no
task queue, no ORM helper, no settings library.

**No Google client library, deliberately** (change-log entry C-P3.2-A,
2026-08-17; migration contract §7.7). `google-api-python-client` and
`google-auth` were briefly added here for C-04 and are **reverted**: Google
Sheets is legacy migration input, not a platform component, so the portal, the
Discord bot and every PostgreSQL-backed runtime path start and run without them.
`adapters/sheets/read_only.py` imports them lazily and refuses with a typed
operator-facing message when they are absent, and C-04 runs from the separate,
temporary operator environment described in
[`../operations/identity-evidence-migration.md`](../operations/identity-evidence-migration.md).
The consequence — C-04 cannot be run from `venv-web` — is the design rather than
a gap. Adding them here later is a change-controlled decision, not a convenience.

### 1.3 Proposed test set — `requirements-web-dev.txt`

| Package | Purpose | Pin |
|---|---|---|
| `pytest` | Existing | inherit `>=8.2,<9` |
| `pytest-asyncio` | Async application-service and adapter tests | `>=0.24,<0.25` |
| `httpx` | Doubles as the in-process ASGI test client (`ASGITransport`) | already listed |
| `beautifulsoup4` | Asserting rendered HTML structure and the absence of controls, without regex over markup | `>=4.12,<5` |

`starlette.testclient` is not used, because it would pull `requests` back in for
tests only.

### 1.4 Explicitly rejected

| Rejected | Reason |
|---|---|
| **Redis / valkey** | Wanted for rate limiting and sessions. Both live in PostgreSQL (N-30, schema §9.1), which is already required, already transactional, already backed up. A second datastore is a second thing to secure, monitor, back up and fail |
| **Celery / RQ / arq / dramatiq** | The job queue is a PostgreSQL table with `FOR UPDATE SKIP LOCKED` (schema §10.1). A broker would add a second durability model to reason about for one job type |
| **`fastapi-users`, `authlib`, `starlette-session`, `fastapi-csrf-protect`** | Each would own a security decision this package must own explicitly. The OAuth flow is one redirect and one token exchange; the session and CSRF designs are stated in the schema and route contracts and must be reviewable line by line |
| **`slowapi` / `limits`** | In-process limiters, which §7 of the delivery plan already ruled insufficient |
| **`pydantic-settings`** | Pydantic arrives with FastAPI, so the validation is available; a separate settings package adds surface for a `from_environment` classmethod (§2.4) |
| **`python-jose` / any JWT library** | ADR 0004 rejected JWT sessions |
| **`passlib` / `argon2-cffi`** | There is no password anywhere in the design (ADR 0010 D8), and a recovery grant is 256 bits of entropy hashed with SHA-256, not a password |
| **npm, any bundler, any CDN, any remote font** | Delivery plan §4; ADR 0002. HTMX is vendored as a single reviewed file |
| **`prometheus-client`** | Monitoring is decided at the deployment gate; adding an exporter now would pre-empt an Operations Owner decision |

### 1.5 Pinning and update strategy

- Upper bounds on every direct dependency, matching the existing
  `requirements.txt` style (`SQLAlchemy>=2.0.36,<2.1`).
- `pip freeze` output committed as `requirements-web.lock` at each P3 package
  gate, so a deployment is reproducible and a review can see exactly what changed.
- Vendored HTMX is committed with its version, upstream URL and SHA-256 recorded
  in the file header, and verified by a test — the same discipline the visual
  freeze manifest already uses.
- Security updates are applied deliberately (plan §9.3), with the lock file diff
  in the change record.

## 2. Typed configuration contract

### 2.1 Principles

Topology §5 already records the requirement: `config.py` calls `sys.exit()` on a
missing variable, *"which is fine for a bot but wrong for a web process under a
supervisor — Phase 3 should raise a typed configuration error instead."* And:
*"`ENVIRONMENT` should be validated loudly: a production process started with a
development database URL is the failure this variable exists to prevent."*

Therefore:

1. Configuration is a **frozen dataclass tree**, built once at startup by an
   explicit `WebSettings.from_environment(mapping)`.
2. Construction **raises a typed `ConfigurationError`** listing *every* problem
   found, not the first. An operator fixing four variables should learn that in
   one attempt.
3. **No default is a secret, a production identifier, or a permissive value.**
   `.agents/AGENTS.md`: never add fallback secrets or production IDs to source.
4. The web process does **not** import the bot's `config.py`, and importing it
   must fail a test (delivery plan §3: *"typed web configuration independent of
   the bot's import-time `config.py`"*).
5. **No secret value appears in this document, in `.env.example`, in a log, in
   `/healthz`, or in an error message.** Errors name the variable, never the value.

### 2.2 The variable set

Names are proposed; values below are **placeholders and policy**, never real
configuration.

#### Environment and process

| Variable | Type | Default | Rule |
|---|---|---|---|
| `WEB_ENVIRONMENT` | enum | *none* | `development` \| `test` \| `staging` \| `production`. Required |
| `WEB_BIND_HOST` | host | `127.0.0.1` | Must be loopback unless `WEB_ENVIRONMENT=development` (N-50) |
| `WEB_BIND_PORT` | port | `8000` | |
| `WEB_PUBLIC_ORIGIN` | URL | *none* | Must equal N-01 in production; must be `https` outside development |
| `WEB_ALLOWED_HOSTS` | list | *none* | Exact hostnames. A `*` anywhere is a startup refusal |
| `WEB_KILL_SWITCH_FILE` | path | *none* | Presence of the file disables the portal (N-56) |
| `WEB_SECRET_KEY_CSRF` | secret | *none* | ≥ 32 bytes of entropy. Used only for the N-17 derivation |
| `WEB_SECRET_KEY_CURSOR` | secret | *none* | ≥ 32 bytes. Signs pagination cursors (N-64). Distinct from the CSRF key |

#### Database

| Variable | Type | Rule |
|---|---|---|
| `WEB_DATABASE_URL` | DSN | Validated by the **existing** `adapters/database/config.py` against `EXPECTED_DATABASES`, with `ConnectionPolicy.SOCKET_OR_LOOPBACK` — the runtime creates and drops nothing, which is the documented condition for that policy |
| `WEB_DATABASE_POOL_SIZE` / `_MAX_OVERFLOW` / `_TIMEOUT_SECONDS` | int | N-53 |
| `WEB_DATABASE_STATEMENT_TIMEOUT_MS` | int | N-53 |

Reusing the existing validator matters: the `PGHOSTADDR` and SSH-forward analysis
in that module is real security work and must not be re-derived by a second
implementation.

#### Identity providers

| Variable | Type | Rule |
|---|---|---|
| `WEB_PROVIDER_REGISTRY` | list | Enabled provider keys. Phase 3 accepts exactly `discord` |
| `WEB_DISCORD_CLIENT_ID` | string | Required when `discord` is enabled |
| `WEB_DISCORD_CLIENT_SECRET` | secret | Required |
| `WEB_DISCORD_REDIRECT_URI` | URL | Must equal N-02 in production; must share `WEB_PUBLIC_ORIGIN`'s origin |
| `WEB_DISCORD_SCOPES` | list | Must equal N-03 exactly. A wider scope is a startup refusal, not a warning |
| `WEB_DISCORD_GUILD_ID` | snowflake | `1052698198180892733` in production |
| `WEB_DISCORD_API_TIMEOUT_SECONDS` | float | Bounded outbound call. From 2026-08-24 it is also the ceiling's ceiling for `/healthz`'s provider probe (finding S-4/S5): the probe uses its own 2-second bound, or this value when it is tighter, so configuration can narrow the health probe and never widen it |
| `WEB_BOOTSTRAP_ADMIN_ROLE_ID` | snowflake | The protected mapping's role. Read **only** by the migration that inserts it |

Council and DM role snowflakes are deliberately **not** configuration: OD-18 puts
capability mappings in the database, managed by the administrator-only workflow.
Only the guild and the protected administrator role are bootstrap configuration.

#### Sessions, CSRF and cookies

| Variable | Rule |
|---|---|
| `WEB_SESSION_COOKIE_NAME` | `__Host-fb_session` when `WEB_COOKIE_SECURE`; a distinct dev name otherwise |
| `WEB_COOKIE_SECURE` | Must be `true` outside development |
| `WEB_SESSION_IDLE_MINUTES` / `_ABSOLUTE_HOURS` | N-06 / N-07; refuse values exceeding them |
| `WEB_EMERGENCY_SESSION_IDLE_MINUTES` / `_ABSOLUTE_MINUTES` | N-15; same rule |
| `WEB_MAX_SESSIONS_PER_ACCOUNT` | N-66 |

Each bound is a **ceiling**, not merely a default: configuration may make a
session shorter than policy, never longer. A configuration file cannot quietly
raise an accepted security limit.

#### WebAuthn and recovery

| Variable | Rule |
|---|---|
| `WEB_WEBAUTHN_RP_ID` | Exactly N-60's value. Must not be a registrable-domain suffix shared with the Foundry hosts — a startup check compares it against `WEB_ALLOWED_HOSTS` |
| `WEB_WEBAUTHN_RP_NAME` | Display string |
| `WEB_WEBAUTHN_ALLOWED_ORIGINS` | Exact origins; must be a subset of `WEB_PUBLIC_ORIGIN` |
| `WEB_WEBAUTHN_USER_VERIFICATION` | `required` (N-60) |
| `WEB_RECOVERY_GRANT_MINUTES` | N-14; ceiling 10 |

#### Encryption

| Variable | Rule |
|---|---|
| `WEB_TOKEN_ENCRYPTION_KEYS` | Versioned key material, newest first, as `version:base64key`. At least one; ≥ 32 bytes each |
| `WEB_TOKEN_ENCRYPTION_ACTIVE_VERSION` | Which version encrypts new rows; older versions decrypt only |

Rotation is therefore: add a key, switch the active version, re-encrypt in the
background, remove the old key. No downtime, and no moment at which a stored token
cannot be read.

#### Membership cache, rate limits and bounds

| Variable | Rule |
|---|---|
| `WEB_MEMBERSHIP_CACHE_SECONDS` | N-09 ceiling 300 |
| `WEB_MEMBERSHIP_GRACE_SECONDS` | N-10 ceiling 900 |
| `WEB_RATE_LIMIT_*` | N-18, N-32, N-32a, N-33 ceilings |
| `WEB_RATE_LIMIT_WEBAUTHN_CHALLENGES_PER_IP` | N-32a ceiling 10. **Added 2026-08-24** (finding S-7/S3), separating challenge issuance from assertion verification. Unset means the accepted value, as every registered number does |
| `WEB_MAX_REQUEST_BYTES` | N-19 ceiling 1 MiB |
| `WEB_TRUSTED_PROXY_HOPS` | Exactly `1`; combined with the loopback peer requirement (N-34) |
| `WEB_AUDIT_PAGE_SIZE_DEFAULT` / `_MAX` | N-21 |
| `WEB_POLL_MIN_SECONDS` | N-22 floor 2 |

#### Worker

| Variable | Rule |
|---|---|
| `WORKER_ENABLED` | Whether this process claims jobs. `freedom-web` sets it `false` and a startup check refuses `true` in the web process |
| `WORKER_CONCURRENCY` | N-41, ceiling 1 in Phase 3 |
| `WORKER_LEASE_SECONDS` / `_HEARTBEAT_SECONDS` | N-23 |
| `WORKER_MAX_ATTEMPTS` | N-43 |
| `WORKER_ATTEMPT_TIMEOUT_SECONDS` | N-45 |
| `WORKER_QUEUE_MAX_DEPTH` | N-42 |
| `WORKER_ARTIFACT_ROOT` | The existing Phase 2 restricted store, validated by the existing startup checks — unchanged, not re-implemented |

### 2.3 Startup refusals

The process **refuses to start** — exits non-zero with a typed error naming every
offending variable, and never its value — when any of these holds:

| # | Refusal | Reason |
|---|---|---|
| S-01 | `WEB_ENVIRONMENT=production` and the database name is not `freedom_production` | The existing `EXPECTED_DATABASES` check; RAID R-25 |
| S-02 | `WEB_ENVIRONMENT` is not production but `WEB_PUBLIC_ORIGIN` is N-01 | A staging process claiming the production origin would receive production cookies and OAuth callbacks |
| S-03 | Production and `WEB_COOKIE_SECURE=false`, or a non-`https` public origin | |
| S-04 | `WEB_ALLOWED_HOSTS` contains `*`, is empty, or omits the public origin's host | |
| S-05 | `WEB_DISCORD_REDIRECT_URI` does not share the public origin | A callback delivered to another origin is a token-leak path |
| S-06 | `WEB_DISCORD_SCOPES` is not exactly N-03 | Scope creep is a privacy change, not a configuration convenience |
| S-07 | Production and any staging/development Discord client id or guild id is configured | Cross-environment credential use (delivery plan §10) |
| S-08 | Any of the four secret keys is missing, shorter than 32 bytes, or **equal to another** | Key separation is what stops a CSRF token being a valid cursor |
| S-09 | `WEB_WEBAUTHN_RP_ID` is not a suffix of the public origin's host, or is a registrable-domain suffix that also covers the Foundry hosts | A shared RP ID would let a Foundry-hosted page use the platform's credentials |
| S-10 | Any bound exceeds its N-nn ceiling | Configuration may tighten policy, never loosen it |
| S-11 | `WORKER_ENABLED=true` in the web process, or `false` in the worker process | Prevents the exact deployment mistake N-40 exists to avoid |
| S-12 | `WORKER_ARTIFACT_ROOT` fails the existing Phase 2 checks (ownership, mode, symlink-free, hard links, trusted ancestors) | Unchanged Phase 2 behaviour, re-used |
| S-13 | The bot's `config.py` is importable from the web process's module graph | Enforced by a test as well (delivery plan §3) |
| S-14 | Alembic head does not match the database's current revision | A process serving a schema it was not built for is a data-integrity risk |
| S-15 | Production, and the protected administrator account has fewer than two enabled WebAuthn credentials (N-13) | Starting a portal whose emergency route cannot be used is starting a portal that will lock its administrator out |

S-15 is a **warning, not a refusal, in staging and development**, because the
credentials are hardware and a development host has none.

### 2.4 Environment separation

| | Development | Test | Staging | Production |
|---|---|---|---|---|
| Database | `freedom_dev` | `freedom_test` (disposable, destructive) | `freedom_staging` | `freedom_production` |
| Discord application | staging app | none (all doubles) | staging app | production app |
| Guild | test guild | none | staging guild | `1052698198180892733` |
| Origin | `http://127.0.0.1:8000` | n/a | staging hostname | N-01 |
| Secrets | developer-generated | generated per run | staging-only | production-only, never reused |
| Foundry world | non-production | synthetic fixtures | non-production | `the-guild` |

*"No implementation package may use the production Discord application or guild
for automated tests. Staging never receives a production database backup."*
(delivery plan §10) — S-07 is the mechanical half of that rule.

### 2.5 `.env.example` changes P3.1 will make

Recorded here so that the review sees the intent before the file changes:

- a new `# ==== Freedom Blades web portal (Phase 3) ====` block containing every
  variable in §2.2 with **placeholder** values and the same comment discipline the
  existing file uses;
- an explicit statement that the bot does not read any `WEB_*` or `WORKER_*`
  variable, mirroring the existing note that the bot does not read the snapshot
  submission variables;
- no change to any existing line.

The `PUBLIC_BASE_URL`, `SESSION_SECRET`, `DISCORD_OAUTH_REDIRECT_URI`,
`COUNCIL_ROLE_ID` and `DM_ROLE_IDS` names sketched in topology §5 are
**superseded** by §2.2: the redirect path is now fixed by N-02, secrets are split
by purpose (S-08), and role snowflakes are database mappings rather than
configuration (OD-18). That divergence from an earlier operations sketch is
recorded rather than silently applied — topology §5 is a proposal document, not an
accepted contract, so this supersedes nothing that was accepted.

## 3. Traceability

| Element | Source |
|---|---|
| Bounded dependency set | delivery plan §5 P3.1; `.agents/AGENTS.md` |
| Typed configuration, not `sys.exit` | topology §5 |
| Loud environment validation | topology §5; RAID R-25 |
| Startup refusal for unsafe combinations | P3.0 prompt §6; delivery plan §12 |
| Scopes exactly `identify guilds.members.read` | N-03; ADR 0004 |
| Role mappings are data, not configuration | OD-18, OD-24 |
| Separate web virtualenv | topology §1; delivery plan §10 |
| No secret value in the repository | `.agents/AGENTS.md`; plan §9.3 |
