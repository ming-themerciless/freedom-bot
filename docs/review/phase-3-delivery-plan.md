# Phase 3 delivery plan — authentication, read-only portal and Council administration

**Prepared:** 2026-08-13

**Status:** Accepted by Peter Duscha on 2026-08-13; P3.0 authorized

**Plan baseline:** `docs/implementation-plan.md` v1.5

**Predecessors:** Phases 0–2 accepted; §12.1 visual direction accepted

**Production implementation:** Not started by this plan

## 1. Outcome and gate

Phase 3 delivers the first production Freedom Blades web application: Discord
authentication, server-side authorization and sessions, read-only member
character views, Council character-link administration, protected offline
snapshot import/reconciliation controls, searchable immutable audit views, and
production Jinja/HTMX integration of the accepted visual direction.

Discord is the initial community identity provider, not an eternal platform
identity key. Phase 3 also establishes a provider-neutral platform account
boundary and an independently usable, narrowly privileged break-glass login for
the Server Administrator. A future decision to leave Discord must require a new
identity-provider adapter and controlled account-link migration—not a rewrite of
character ownership, sessions or audit attribution.

The phase closes only at the implementation plan's authentication,
authorization and web-security gate. Peter Duscha records the decision after a
Security Reviewer recommendation and an Independent Reviewer recommendation.
Passing tests alone does not approve the phase.

Peter Duscha accepted this readiness and delivery plan on 2026-08-13. The
acceptance releases P3.0 contract and security design work only. P3.1 remains
blocked behind P3.G0.

## 2. Authority and delivery assignments

| Responsibility | Assignment | Boundary |
|---|---|---|
| Product Sponsor, Acceptance Authority, Product Owner, Data Owner, Operations Owner and Delivery Lead | Peter Duscha | Accountable decisions and gate approval |
| Working Technical Lead and backend implementer | Claude, operating under Peter's designation | Packages P3.0–P3.3; cannot independently approve them |
| Production frontend implementer | Gemini, operating under Peter's designation | Package P3.4 only, against accepted contracts |
| Independent Reviewer resource | Codex | Independent implementation/integration recommendation |
| Accountable Security Reviewer | Peter Duscha, assisted by Codex in a distinct security-focused pass | Authentication, authorization, session, CSRF, upload and privacy recommendation |
| Accountable accessibility reviewer | Peter Duscha, assisted by Codex source/automated review | Production templates and interactions; live assistive-technology evidence remains explicitly identified |

Codex did not implement the production work described here and may review it.
The independent and security-focused reviews are separate passes even when the
same tool assists both. Peter remains the accountable human decision-maker.

## 3. Included scope

- a separate `freedom-web` FastAPI/uvicorn process;
- typed web configuration independent of the bot's import-time `config.py`;
- Discord OAuth2 authorization-code flow with PKCE and scopes `identify` and
  `guilds.members.read`;
- stable internal platform accounts and separately linked external identities;
  Discord provider/subject is one external identity, never the primary key of
  authorization-bearing domain relationships;
- a provider interface and versioned provider identifier so a later approved
  OpenID Connect or other reviewed provider can authenticate an existing
  platform account without name/email matching;
- Server Administrator break-glass authentication independent of Discord,
  using pre-enrolled phishing-resistant credentials plus a host-local,
  short-lived one-time recovery path;
- current membership and stable role-ID verification for guild
  `1052698198180892733`, Council role `1052702392728178688`, DM role
  `1124406915783475241` and Platform Administrator role
  `1124405581298552933`;
- opaque server-side PostgreSQL sessions, logout and revocation;
- server-side capability and object-level authorization;
- Server-Administrator-only management of Discord-role-to-platform-capability
  mappings, with the administrator bootstrap mapping protected from lockout;
- synchronizer-token CSRF protection for every cookie-authorized mutation;
- security headers, restrictive same-origin policy, safe errors, input bounds
  and authentication rate limiting;
- Council-managed `character_access` grant, revoke and default-character flows
  with reason, optimistic concurrency and append-only audit;
- Council-reviewed migration/reconciliation of `Characters C` (`Player Name`)
  and `Players A/B/D` identity evidence into Discord snowflakes and
  `character_access`, with explicit unresolved records and no name-derived
  authorization;
- My Characters and character-detail read models;
- protected field-profile, reconciliation and bounded audit read models;
- Council-only import trigger and Platform-Administrator-only folder selection,
  preserving the rule that administrator alone cannot apply an import;
- a durable asynchronous reconciliation-preview job because the measured real
  32-Actor preview takes 9.57 seconds;
- idempotent/stale-safe import confirmation using the existing Phase 2 service;
- production Jinja templates/static assets and modest vendored HTMX, adapted
  from—not imported from—`design-prototype/`;
- migrations required by real Phase 3 use cases, PostgreSQL tests, configuration
  examples, systemd/Caddy templates, health/monitoring and rollback docs; and
- a complete gate evidence/traceability package.

## 4. Explicit exclusions

- no ordinary-member website mutation;
- no general local username/password database and no second ordinary-member
  identity provider in this phase; the provider-neutral boundary is delivered,
  while selection and rollout of a Discord replacement requires a later
  approved provider/privacy/migration package;
- no character game-state correction or generic edit endpoint;
- no generic approval centre (Phase 6);
- no editor for tools, languages, homebrew items or controlled vocabularies;
- no Sheet-era character game-state migration, generic interim character state
  or Sheet retirement; the narrowly included player/character identity-linkage
  evidence migration in P3.2 is the only Sheet-era migration in this phase;
- no Foundry write, live LevelDB access or broad Phase 7 connector;
- no bot-command authorization cutover or mutation migration;
- no mission, attendance, reward, settlement, Bastion or facility work;
- no SPA, React, Vue, npm, bundler, CDN, remote font or frontend build step;
- no production data in fixtures or automated tests; and
- no deployment to production before the Phase 3 gate and deployment gate are
  separately approved.

## 5. Package sequence and stop gates

### P3.0 — contract and security design baseline

Owner: Claude. Review: Codex independent architecture/security review.

Deliver:

- exact route inventory, HTTP method and capability matrix;
- versioned view-model definitions for login/session, character summaries,
  character detail, character links, profile classifications, reconciliation
  jobs/results and audit search;
- logical schema artifact and schema decision table for sessions, encrypted
  OAuth credentials, platform accounts, external identities, break-glass
  credentials/recovery grants, capability mappings and durable jobs;
- migration design replacing Discord snowflakes as foreign keys of
  authorization-bearing relationships, including `character_access`, while
  retaining Discord identity/membership as an adapter projection;
- explicit state machines for sessions and reconciliation jobs;
- a proposed ADR for provider-neutral identity and break-glass administration,
  including account-linking, unlinking, provider-retirement and recovery rules;
- configuration contract and dependency proposal;
- threat model covering OAuth, session fixation/theft, CSRF, confused deputy,
  object substitution, stale roles, upload abuse, unsafe rendering, retries and
  concurrent apply; and
- acceptance/test traceability refined from §10.

No protected production route is added in P3.0. No migration or framework
scaffold is implemented. Material changes to authority, data ownership,
privacy, topology or the accepted ADRs return to Peter before coding.

**Stop gate P3.G0:** Peter accepts the route/view-model, schema and numeric
security contracts after Codex review. P3.1 may then start. Gemini may not start
production integration.

### P3.1 — authentication and security foundation

Owner: Claude. Review: Codex independent review plus distinct security pass.

Deliver:

- deliberately bounded FastAPI, uvicorn, Jinja2, OAuth/HTTP client and test
  dependencies;
- application factory and typed startup validation;
- OAuth start/callback/logout with state, PKCE and safe return targets;
- platform-account/external-identity repositories and a reversible migration of
  existing Discord-linked access/audit attribution with exact control totals;
- Server Administrator break-glass login that remains available when Discord is
  unavailable, cannot imply Council game-policy capability, and cannot silently
  become an ordinary-member authentication bypass;
- pre-enrolled WebAuthn/passkey credentials for normal break-glass use and a
  host-local operator command that can issue a hashed, single-use, 10-minute
  recovery grant when every enrolled credential is lost;
- encrypted server-side OAuth-token storage and opaque PostgreSQL sessions;
- current membership/role adapter and capability resolver;
- session rotation, expiry and revocation;
- CSRF middleware/service, same-origin enforcement, security headers, safe error
  handling and authentication rate limits;
- migrations and runtime grants for this package only;
- health endpoint without secrets or player data;
- minimal integration templates sufficient to test the contracts; and
- configuration, migration, recovery and operator documentation.

**Stop gate P3.G1:** authentication/authorization and schema/security review.
No member or Council production query package proceeds on a blocking finding.
Per the 2026-08-14 I-08 ruling, this gate requires TC-BG-05a, TC-BG-05d and the
service/database portions of TC-BG-05b/c/e. It does not accept the corresponding
P3.2 HTTP boundary.

Per the 2026-08-14 I-07 ruling, this gate also requires the OD-44 durable
completion binding and its evidence, TC-AUTH-13 and TC-AUTH-14. Both were
delivered on 2026-08-14 in
[`phase-3-p3-1-od-44-remediation-submission.md`](phase-3-p3-1-od-44-remediation-submission.md)
and await the Codex independent implementation re-review and the distinct
security-focused pass that this gate turns on. The migration deliverable for this
package is therefore revisions **0006–0009**.

### P3.2 — member reads, identity reconciliation and access administration

Owner: Claude. Review: Codex independent/security review of object boundaries.

Deliver:

- framework-free My Characters and character-detail queries;
- object-level authorization for linked characters and Council-wide reach;
- Council grant/revoke/default-character commands with reasons, optimistic
  versions, atomic audit and the one-active-owner invariant;
- Server-Administrator-only role-capability mapping commands; the protected
  administrator bootstrap mapping cannot be revoked, replaced or demoted by the
  application, and administrator capability still does not imply Council;
- a dry-runnable identity-evidence migration for `Characters C` and
  `Players A/B/D`, using the read-only Sheet boundary, exact source-to-target
  control totals and explicit unresolved/ambiguous rows;
- Council preview and confirmation of every proposed Discord-snowflake link;
  player name, Discord display name and `Active DM` are evidence only and never
  effective authorization;
- migration idempotency, atomic apply, backup/restore rerun and rollback to the
  legacy linkage-evidence workflow without mutating Google Sheets;
- bounded search/selection of Discord identities and characters without relying
  on mutable display names;
- explicit linking of an additional external identity to an existing platform
  account only after strong reauthentication or a separately audited Council/
  Server-Administrator recovery decision; provider display name or email never
  links accounts automatically;
- route/view-model implementations and minimal contract templates; and
- denial, stale, concurrent and audit-failure tests.

Character detail remains limited to Phase 2 identity/snapshot data and fields
whose typed database package is already authoritative. Legacy fields render
`migration deferred` and their owning package.

**Stop gate P3.G2:** read-path, identity migration and Council-link/role-mapping
authorization review. The direct-HTTP portions of TC-BG-05b/c/e must pass here
against the real R-33, R-34 and R-38 handlers; they are blocking evidence, not a
waiver inherited from P3.G1. Accepted contracts are frozen for P3.4 integration.

### P3.3 — Council import, durable reconciliation jobs and audit views

Owner: Claude. Review: Codex independent/security-focused review.

Deliver:

- Platform-Administrator folder selection, defaulting to
  `/actors/Characters (active)`, without granting Council apply authority;
- Guild-Council-only preview/import controls;
- PostgreSQL-backed reconciliation job state and bounded result references;
- job claim/lease, heartbeat, retry and abandoned-job recovery;
- polling endpoints/view models suitable for modest HTMX;
- stale-scope invalidation on snapshot, folder, profile or aggregate-version
  change;
- exact checksum/world/folder/Actor-count/mapping/warning confirmation;
- idempotent apply using existing Phase 2 application services;
- bounded searchable audit/reconciliation history; and
- upload, malicious-content, escaping, retry, double-click, concurrent apply,
  runtime-role and recovery tests.

No restart-unsafe in-memory queue is permitted. A separate long-running worker
is introduced only if P3.0 shows that a durable database-claimed job executed by
`freedom-web` cannot meet bounded recovery and operational requirements.

**Stop gate P3.G3:** Council/import authorization, concurrency, audit and
recovery review. Accepted view models are frozen for P3.4.

### P3.4 — production frontend integration

Owner: Gemini. Backend contract owner: Claude. Review: Codex; visual and
real-device acceptance: Peter.

Deliver:

- production Jinja base/layout/templates, static assets and vendored HTMX;
- adaptation of the accepted visual language without serving or importing
  `design-prototype/`;
- login, My Characters, character detail, reconciliation, character-link and
  audit views using only accepted contracts;
- keyboard, focus, denied, empty, loading, stale, validation and system-error
  states;
- responsive operation at 320, 768 and 1280 CSS pixels and 200% reflow;
- safe escaped rendering and progressive enhancement; and
- frontend contract, accessibility and browser tests.

Gemini may not change authentication, authorization, persistence, route or
view-model contracts. A necessary cross-boundary change returns to Claude,
Codex review and Peter's decision rather than being absorbed in templates.

**Stop gate P3.G4:** frontend/integration/accessibility review and maintainer
visual acceptance.

### P3.5 — phase integration and gate package

Owner: Claude for backend findings, Gemini for frontend findings. Review:
Codex independent pass and distinct security pass. Decision: Peter.

Deliver:

- all blocking and important findings remediated and re-reviewed;
- final requirements-to-evidence traceability;
- narrow then full suites, real PostgreSQL integration evidence and explained
  skips;
- formatter, linter, type checker, migration consistency and compile checks;
- synthetic staging end-to-end OAuth/member/Council/import flows;
- security-header, CORS/CSRF, revocation and object-substitution evidence;
- deployment, health, monitoring, backup, rollback and recovery rehearsal; and
- requested Phase 3 authentication/security gate decision.

No Phase 4 implementation starts before Peter records the Phase 3 gate.

## 6. Estimates and capacity assumptions

Effort is focused working days and excludes waiting time. The ranges include
implementation, tests and documentation. Review/remediation is explicit rather
than hidden in coding estimates.

| Package | Optimistic | Likely | Pessimistic | Confidence |
|---|---:|---:|---:|---|
| P3.0 contracts/security/identity design | 3 | 5 | 8 | Medium-low |
| P3.1 authentication/account/security foundation | 6 | 10 | 16 | Low |
| P3.2 member reads/identity evidence/access | 5 | 9 | 14 | Medium-low |
| P3.3 Council import/async jobs/audit | 5 | 8 | 13 | Medium-low |
| P3.4 production frontend integration | 4 | 7 | 11 | Medium |
| P3.5 integration/gate evidence | 3 | 5 | 8 | Medium-low |
| **Total focused effort** | **26** | **44** | **70** | **Low** |

The original 10–18 day roadmap range is no longer credible for the decomposed
scope and evidence burden. Rebaselining the forecast does not change product
scope; it corrects an early rough-order estimate after the measured async-job
constraint and mandatory review evidence became known.

Capacity assumption: one focused implementer at a time, Peter available for
policy decisions and supervised checks, and Codex available at each stop gate.
P3.4 may overlap late P3.3 only for already accepted, non-conflicting contracts.
No calendar dates are promised until Peter records availability windows.

Review/remediation contingency: reserve 30% of each implementation package's
likely effort, already reflected in the pessimistic range. Any blocking finding
or contract change returns through its stop gate; contingency is not permission
to compress evidence.

## 7. Accepted numeric security and operational contract

Peter accepted these values on 2026-08-13. A later change follows the plan's
change-control and security-review requirements.

| Control | Accepted value |
|---|---|
| Production origin | exactly `https://freedom-blades.rpgworld.org` |
| OAuth redirect | exactly `https://freedom-blades.rpgworld.org/auth/discord/callback` |
| OAuth scopes | `identify guilds.members.read` only |
| OAuth state/PKCE transaction | single use; 10-minute maximum |
| Session cookie | host-only opaque identifier; `Secure`, `HttpOnly`, `SameSite=Lax`, `Path=/`; no `Domain` attribute |
| Session idle expiry | 60 minutes |
| Session absolute expiry | 12 hours |
| Session rotation | login and every detected privilege change |
| Membership/role cache | 5 minutes maximum |
| Discord outage | mutations fail immediately; protected reads may use a previously successful membership result for at most 15 minutes total, then fail closed |
| OAuth token retention | encrypted server-side only; deleted on logout/revocation and no later than the session's absolute expiry unless an active refresh operation requires it |
| Break-glass privilege | Platform Administrator only; never Council, character ownership or import-apply authority by implication |
| Break-glass primary credential | at least two pre-enrolled WebAuthn/passkey credentials for the accountable Server Administrator; no permanent local password |
| Break-glass recovery grant | created only by a host-local operator command; random, stored only as a hash, single use, 10-minute expiry, purpose-bound to recovery login, and fully audited without storing the token |
| Break-glass session | 15-minute idle, 60-minute absolute expiry; rotate on login; no extension beyond the absolute bound |
| External identity linking | exact provider plus immutable provider subject; no display-name or email auto-link; strong reauthentication and audited confirmation required |
| CSRF | session-bound synchronizer token on every cookie-authenticated mutation; rotate with session; reject missing/mismatched token before application service |
| Auth rate limit | 10 OAuth starts and 20 callbacks per source IP per 10 minutes; bounded in-process limiter is insufficient across processes, so storage/algorithm is settled in P3.0 |
| General request body | 1 MiB except the existing snapshot submission/import path |
| Snapshot body | existing accepted 64 MiB, 500 Actors, depth 64 and package parser limits; proxy and application limits must match |
| Audit pagination | default 50, maximum 100 records per page; stable cursor, no unbounded offset scan |
| Reconciliation polling | no faster than every 2 seconds; server may back off; response contains no raw artifact |
| Job lease | 60 seconds with heartbeat at most every 20 seconds; an expired lease is recoverable, never proof of failure |
| Job result metadata retention | 30 days for preview/job presentation records unless an applied import/audit rule requires indefinite typed history; raw artifacts follow the existing snapshot-retention procedure |
| Safe error correlation | UUID correlation ID returned; exception text, paths, SQL, tokens and raw Actor content omitted |
| CSP starting point | `default-src 'self'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'; form-action 'self'; img-src 'self' data:; script-src 'self'; style-src 'self'` |

P3.0 must validate the CSP against the exact Discord authorization redirect and
vendored HTMX behaviour. It may tighten it without a policy decision; weakening
it, adding a remote asset origin or allowing inline script/style requires
documented security review.

## 8. Durable reconciliation-job contract

The P3.0 logical design must preserve these invariants:

1. A job records stable ID, requester, current authorization context, snapshot
   checksum, selected world/folder, field-profile version, aggregate versions,
   request key, state, attempts, timestamps and correlation ID.
2. States are `queued`, `running`, `completed`, `stale`, `failed` and
   `cancelled`; transitions are constrained and append-only audit facts record
   every terminal outcome.
3. A database claim or equivalent lease prevents two workers executing the same
   attempt. Expiry permits recovery but cannot duplicate an apply.
4. Parsing and preview run outside the apply transaction. Apply rechecks current
   Council authorization, checksum, folder, profile and aggregate versions.
5. Polling is object-authorized on every request. Ordinary members cannot infer
   job existence, Actor names, warnings or raw snapshot content.
6. Retry uses the same idempotency key and returns the existing outcome where
   appropriate. Double-click and two-browser concurrency yield one durable
   effect and one success audit effect.
7. Process restart, lost response, expired lease and audit failure have explicit
   recovery tests. No state named `completed` precedes durable commit.
8. Cancellation is best effort for queued/preview work and cannot cancel an
   already committed apply or erase history.
9. Results are bounded summaries/references; raw snapshot bytes are never placed
   in session, HTML, JSON responses, logs or job payloads.

## 9. Provider-neutral identity and emergency-access contract

P3.0 must design and P3.1 must implement these invariants:

1. A `platform_account` has a stable internal identifier independent of every
   identity provider. Sessions, `character_access`, acting-user audit attribution
   and human authorization refer to that account.
2. An `external_identity` is unique on `(provider, subject)` and links to exactly
   one platform account. Discord snowflakes remain typed Discord facts, not
   platform account IDs.
3. Migration accounts for every existing Discord user, character-access link,
   membership/role projection and attributable audit reference. It is dry-
   runnable, idempotent, transactional, reversible before cutover and has exact
   source/target control totals.
4. Neither display name, username nor email establishes identity equivalence.
   Ambiguous or unverified links remain unresolved and grant no access.
5. Provider unlink/retirement refuses to strand an account without a usable
   accepted identity or reviewed recovery route. Historical audit attribution
   remains readable after provider retirement.
6. The protected Server Administrator bootstrap mapping cannot be edited through
   ordinary capability administration. Break-glass authentication yields only
   Platform Administrator capability and does not make imports or game-policy
   changes legal.
7. Every break-glass attempt and outcome is rate-limited and audited. Audit
   records identify the credential/grant record, account, time, source and
   correlation ID, but never authenticator secrets or recovery tokens.
8. The host-local recovery command requires existing host/operator authority;
   it is not exposed as a remote API. Loss of Discord plus loss of every passkey
   therefore remains recoverable by the Operations Owner without a permanent
   password backdoor.
9. Adding an ordinary-member replacement provider later requires an accepted
   provider, privacy, account-linking and migration package. The Phase 3 provider
   interface makes that bounded; it does not pre-approve an unknown provider.
10. Authentication providers are replaceable adapters. Session integrity,
    authorization, CSRF, origin/host validation, request and concurrency bounds,
    rate limiting, audit and safe failure remain provider-independent core
    controls and cannot be weakened by replacing Discord.
11. The public web perimeter exposes only the reverse proxy. Unknown hosts are
    rejected; application and PostgreSQL ports remain private; bounded
    connections/timeouts and an operator kill switch can disable the portal
    without stopping the Discord bot or Foundry.

## 10. Environment and deployment readiness

| Environment | Required state | Current evidence | Readiness |
|---|---|---|---|
| Development | Python 3.12; separate web virtualenv; synthetic configuration; `freedom_dev` | Python and repository venv exist; separate web venv not yet created | Open |
| Disposable PostgreSQL | guarded `freedom_test`, owner/test login and restricted runtime role; full DB suite | Proven in Phase 2; `TEST_DATABASE_URL` was not configured in the 2026-08-13 reconciliation session | Must be re-confirmed before P3.1 |
| Staging | separate DB/login, web service, Discord application/guild, credentials, loopback port and non-production Foundry world | topology is designed in `docs/operations/topology.md`; no current deployed staging web evidence | Open; required before P3.5, configuration contract required before P3.1 |
| Production | separate web venv/service/runtime role/environment file; loopback bind behind Caddy | hostname/topology decided; no `freedom-web` service exists | Deployment work only after Phase 3 gate |

No implementation package may use the production Discord application or guild
for automated tests. Staging never receives a production database backup.

## 11. Acceptance and mandatory-test traceability

The implementing handoff must expand these rows to exact test names. No row may
be removed; `not applicable` requires written reviewer acceptance.

| Requirement/scenario | Owning package | Required evidence |
|---|---|---|
| Unauthenticated users cannot access protected data | P3.1 | route and application denial tests |
| Discord outage still permits narrow Server Administrator recovery | P3.1 | WebAuthn/recovery-grant success, Discord-unavailable and privilege-boundary tests |
| Break-glass cannot acquire Council or character authority | P3.1/P3.2 | direct service/HTTP capability and forged-submission denial tests |
| Recovery grant is host-local, hashed, single-use and expires in 10 minutes | P3.1 | CLI, storage, replay, expiry, audit and lost-response tests |
| Platform accounts survive provider unlink/retirement without identity ambiguity | P3.0–P3.2 | migration/control-total, uniqueness, unresolved-link and historical-attribution tests |
| No name/email auto-link can merge accounts | P3.1/P3.2 | collision, case/Unicode, duplicate-name and forged-claim tests |
| Non-member, ordinary member, Council and administrator matrix for every protected endpoint | P3.1–P3.3 | parameterized direct-HTTP and service tests |
| Council uses stable role ID; administrator does not imply Council | P3.1/P3.3 | capability and forged-role tests |
| Revoked membership/role and privilege change | P3.1/P3.3 | cache-expiry, live recheck, session rotation/revocation tests |
| Multiple linked characters and object substitution | P3.2 | query/service/HTTP cross-character tests |
| Character-link grant/revoke/default changes | P3.2 | authorization, invariant, optimistic concurrency, atomic audit and PostgreSQL constraint tests |
| Legacy identity evidence is fully accounted for and never auto-authorizes | P3.2 | dry-run/control totals, ambiguous/unresolved, idempotent apply, injected failure, backup/restore rerun and Council-confirmation tests |
| Only administrator manages role-capability mappings and cannot remove protected bootstrap mapping | P3.2 | role matrix, lockout-prevention, stale/concurrent and audit tests |
| Ordinary member cannot see or call import | P3.3/P3.4 | hidden-control plus direct-call denial tests |
| Administrator folder change invalidates preview | P3.3 | stale-version service and HTTP tests |
| Council confirmation exact scope | P3.3/P3.4 | view-model/escaping contract tests |
| No character-game-state correction endpoint | P3.0–P3.5 | route inventory plus negative structural/direct-call tests |
| Legacy fields show migration package and no control | P3.2–P3.4 | controlled-register mapping/render tests |
| CSRF, origin, cookie and safe redirects | P3.1 | positive/negative HTTP tests |
| Request/file limits, content type and malicious filename | P3.1/P3.3 | boundary and proxy/application parity tests |
| Escaped Actor, warning and user-controlled text | P3.2–P3.4 | template and response tests |
| Async job restart/lease/retry/recovery | P3.3 | real PostgreSQL concurrency/restart simulations |
| Double-click, retry and two-browser concurrent apply | P3.3 | real PostgreSQL/service/HTTP test with one effect |
| Audit search authorization and bounded pagination | P3.3 | role matrix, cursor and maximum-size tests |
| Audit update/delete impossible | P3.3 | absence of use case plus runtime-role PostgreSQL denial |
| Raw snapshot unauthorized download and disclosure | P3.1/P3.3 | route absence/denial, log and response-content tests |
| Security headers and CSP | P3.1/P3.4 | exact response-header tests and staging browser check |
| Responsive/keyboard/focus/reduced motion/error states | P3.4 | automated browser checks, source review and Peter's real-device check |
| Migration apply/downgrade/upgrade and recovery | each schema package/P3.5 | disposable PostgreSQL rehearsal |
| Full gate package | P3.5 | §13.3 evidence checklist and reviewer recommendations |

## 12. Risks and controls

- **Authentication boundary defect:** fail closed, keep protected routes behind
  P3.G1, and require a distinct security review.
- **Permanent backdoor or overpowered emergency account:** no permanent local
  password, pre-enrolled phishing-resistant credentials, host-local one-time
  recovery, short emergency sessions and Platform-Administrator-only authority.
- **Provider migration account takeover:** stable internal accounts, exact
  provider subjects, no name/email auto-link and explicit reviewed linking.
- **Discord outage or rate limiting:** bounded cache/grace policy, mutation
  refusal, safe user state, metrics without identity data.
- **Session/token compromise:** opaque cookie, encrypted tokens, bounded expiry,
  rotation/revocation and no token logging.
- **Async duplicate or abandoned work:** PostgreSQL claims/leases, idempotency,
  recovery and real concurrency tests.
- **Frontend contract drift:** contract freeze at P3.G2/P3.G3 and explicit
  cross-boundary change review.
- **Accessibility regression during production adaptation:** automated browser
  checks plus source and real-device review; static prototype evidence is not
  silently promoted to production evidence.
- **Co-located-host resource contention:** bound job concurrency, request size,
  database pool and worker use; observe staging under a representative 64 MiB
  refusal and 32-Actor preview before deployment.
- **Environment confusion:** typed environment validation, separate credentials,
  host-only production origin and destructive-test database guards.

These risks are added to the RAID register during readiness reconciliation and
remain active until their owning package gate closes.

## 13. Readiness decision checklist

### Satisfied

- outcome, included scope and exclusions are written;
- predecessor Phase 2 gate is approved;
- OD-16/17 and relevant Phase 3 architecture decisions are closed;
- delivery-agent responsibilities are separated;
- work is decomposed into reviewable packages with stop gates;
- three-point estimates, confidence and contingency are recorded;
- acceptance and mandatory-test categories are traced;
- material risks and proposed controls are written; and
- accepted visual direction and freeze evidence exist.

### Accepted by Peter Duscha on 2026-08-13

1. Accepted the P3.0–P3.5 package boundaries and the re-estimated 26/44/70-day
   focused-effort range.
2. Confirmed Peter's accountable roles and availability in principle; calendar
   windows may be recorded before each package rather than promised now.
3. Confirmed Peter's accountable Security Reviewer and accessibility-review roles,
   with Codex supplying the Independent Reviewer recommendation and a distinct
   security-focused pass as recorded in §2.
4. Accepted every numeric policy in §7 and the
   provider-neutral identity and break-glass contract in §9.
5. Confirmed that P3.0 is the first authorized package after readiness—not P3.1
   implementation and not Gemini production integration.
6. Confirmed the environment rule: disposable PostgreSQL before P3.1, staging
   configuration contract before P3.1, and deployed staging before P3.5.

### Still operationally open after plan acceptance

- re-confirm the disposable PostgreSQL URL/role without recording credentials;
- establish the separate web virtualenv and safe development configuration as
  P3.1 implementation work after P3.G0;
- create or confirm staging Discord application/guild identifiers and secrets
  outside the repository before staging execution; and
- record actual maintainer/reviewer availability when a calendar forecast is
  requested.

Plan acceptance releases P3.0 contract work only. P3.1 remains behind P3.G0.
