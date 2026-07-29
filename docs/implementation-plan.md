# Freedom Blades Platform — Master Implementation Plan

Status: Draft for maintainer approval  
Audience: Maintainers, Claude Code, reviewers, and operators  
Repository: `freedom-bot` (to evolve into the Freedom Blades platform)  
Primary rules source: `Freedom Blades - Homebrew Rules.pdf`

## 1. Purpose

This document is the implementation contract for evolving the current
Freedom Bot into a secure, database-backed Freedom Blades platform.

The target product consists of:

- a branded web application;
- the existing Discord bot, reduced over time to a Discord adapter;
- a PostgreSQL database and immutable transaction/audit history;
- Discord authentication, role verification, events, attendance, and
  notifications;
- controlled synchronization with the Foundry VTT world `The Guild`;
- Guild Council approval workflows;
- automated homebrew workflows for downtime, crafting, learning, mining,
  lifestyle, missions, rewards, and Bastions; and
- a future, optional AI-assisted report-writing workflow.

This is an incremental replacement of a live system. It is not a rewrite and
does not authorize deleting the current bot, Google Sheet integration, live
data, or deployment configuration.

## 2. Repository strategy

### 2.1 Decision

Develop the platform inside this repository.

Do not create a temporary sibling application that will later replace the
repository. Do not delete the Discord bot after the website is introduced.
The bot remains the Discord-facing adapter for notifications, event
integration, voice attendance, and optional lightweight commands.

The repository may be renamed from `freedom-bot` to a platform-oriented name
after the database-backed web application is operating reliably. A rename is
an administrative change, not an architectural milestone.

### 2.2 Intended repository layout

The layout should evolve incrementally toward:

```text
freedom-bot/
├── application/             # use cases shared by web, bot, and Foundry
├── domain/                  # framework-free game and platform policy
├── adapters/
│   ├── database/
│   ├── discord/
│   ├── foundry/
│   └── sheets/
├── web/                     # HTTP routes, forms, templates, static assets
├── ext/commands/            # existing Discord commands during migration
├── migrations/              # database migrations
├── tests/
│   ├── unit/
│   ├── application/
│   ├── integration/
│   ├── contract/
│   └── e2e/
├── docs/
│   ├── adr/
│   ├── operations/
│   ├── rules/
│   └── implementation-plan.md
├── foundry-module/          # versioned Freedom Blades Foundry module
└── infra/                   # systemd, reverse proxy, database, deployment
```

Do not perform a mass move merely to obtain this layout. Move a module only
when its current feature is being migrated and protected by tests.

## 3. Governing principles

1. PostgreSQL becomes the authoritative operational store.
2. The website, bot, and Foundry connector call the same application services.
3. Domain rules do not import Discord, web, Google, Foundry, or ORM libraries.
4. No advancement, reward, or imported Foundry change is official without the
   required Guild Council approval.
5. All state changes are transactional, idempotent where applicable, and
   auditable.
6. Stable IDs identify users, characters, and external records. Names are
   mutable display values.
7. Foundry is accessed through supported APIs and a narrow module. Never write
   directly to Foundry LevelDB.
8. Google Sheets is retired through a measured migration, not an indefinite
   dual-write arrangement.
9. Authorization is enforced on the server for every request and command.
10. AI may draft or extract proposals but never decides or applies game state.
11. Production data is never used in automated tests or committed fixtures.
12. Existing behavior is preserved until a documented requirement changes it.

## 4. Product roles and authorization

### 4.1 Roles

The application recognizes capabilities, not only role names:

- **Visitor**: not authenticated; sees only a login page and explicitly public
  material.
- **Guild Member**: authenticated and currently a member of the configured
  Freedom Blades Discord guild.
- **Character Owner**: a Guild Member with an active access link to one or more
  characters.
- **DM**: a Guild Member permitted to create and operate mission drafts.
- **Guild Council**: a Guild Member with the configured Discord role ID and
  approval/edit capabilities.
- **Platform Administrator**: a narrowly assigned operational role for
  deployment and exceptional recovery. It must not silently imply game-policy
  authority.
- **Service Principal**: the bot, Foundry module, import worker, or scheduled
  worker using scoped credentials.

Discord role names are presentation only. Configuration and authorization use
stable Discord guild and role snowflakes.

### 4.2 Character access

Use a many-to-many relationship:

```text
DiscordUser 1 ── * CharacterAccess * ── 1 Character
```

`CharacterAccess` includes:

- user ID;
- character ID;
- access kind: `owner`, `co_owner`, `delegate`, or `viewer`;
- active/revoked state;
- default-character flag;
- grantor;
- grant/revoke timestamps;
- optional expiry;
- reason; and
- audit correlation ID.

A user may have multiple characters. A character may have multiple authorized
users. Guild Council manages links. Ordinary bot character choices are limited
to active, linked characters permitted for that command.

### 4.3 Authorization rules

- Website direct mutations require Guild Council unless a later requirement
  explicitly delegates a narrow action.
- Ordinary users initially have a read-only website.
- Ordinary users may perform existing approved mutations through bot commands,
  limited to linked characters and authorized channels.
- DMs may edit their own mission drafts but cannot apply settlements.
- Guild Council may edit proposals and approve them.
- Role verification occurs server-side. Cached roles are not permanent proof.
- Every privileged mutation records the acting Discord user and current
  authorization context.
- Removing a Discord role or guild membership must revoke effective
  authorization promptly.

## 5. System architecture

### 5.1 Components

```text
Browser
   │ HTTPS
   ▼
Web application ───────────────┐
                               │
Discord bot ───────────────────┼─> Application services ─> Domain
                               │             │
Foundry module ────────────────┘             ▼
                                         Repositories
                                             │
                  ┌──────────────────────────┼──────────────────┐
                  ▼                          ▼                  ▼
              PostgreSQL              Google Sheets       External APIs
             authoritative              temporary        Discord/Foundry
```

### 5.2 Technology baseline

Record final choices as ADRs before framework scaffolding. Recommended
baseline:

- Python version matching deployment;
- FastAPI for the versioned API and HTTP application;
- server-rendered Jinja templates with modest HTMX-style enhancements;
- SQLAlchemy 2.x for database mapping;
- Alembic for migrations;
- PostgreSQL in production;
- pytest for all test levels;
- existing Pycord bot as the Discord Gateway process;
- Caddy or nginx for TLS termination and reverse proxying.

Avoid a large SPA initially. The product is dominated by forms, tables,
approval queues, diffs, and reports. A separate frontend build ecosystem is
not justified until a measured interaction requirement demands it.

### 5.3 Processes

Run at least:

- `freedom-web`: HTTP application;
- `freedom-bot`: Discord Gateway and commands;
- PostgreSQL;
- reverse proxy;
- Foundry VTT; and
- optionally `freedom-worker` when durable background work becomes necessary.

Do not implement an in-memory job queue for work that must survive restarts.
Initial small jobs may execute synchronously outside the event loop. Introduce
a durable worker only for concrete needs such as imports, sync, or large
settlements.

## 6. Data ownership and synchronization

### 6.1 Required field ownership matrix

Before enabling writes, create `docs/rules/field-ownership.md`. Every synced
field must be one of:

- **Foundry-owned**: database imports changes; database does not overwrite it.
- **Database-owned**: Foundry differences create warnings or receive approved
  database updates.
- **Council-approved shared**: Foundry differences create approval proposals.
- **Derived**: calculated from authoritative inputs and never edited directly.
- **Display-only**: cached for presentation and safe to refresh.

Initial recommendation:

| Field group | Initial owner |
|---|---|
| Foundry Actor ID and world ID | external mapping |
| Name, image, class, species, level | Foundry, subject to review |
| Ability scores and character mechanics | Foundry |
| Discord ownership links | PostgreSQL |
| Missions, badges, last played | PostgreSQL |
| Downtime and learning progress | PostgreSQL |
| Lifestyle and Moradinium | PostgreSQL |
| CRP and homebrew crafting state | PostgreSQL |
| Bastion state | PostgreSQL |
| Currency | PostgreSQL after migration |
| Inventory/notable items | explicit reconciliation required |
| Languages and tool proficiencies | explicit reconciliation required |

### 6.2 Conflict policy

Never silently apply a bidirectional last-write-wins rule.

A sync comparison records:

- external and internal values;
- field owner;
- external record/version;
- internal version;
- detection time;
- proposed action;
- conflict state; and
- resolution/approver.

Council-approved shared fields generate proposals. Database-owned fields do
not get overwritten by Foundry imports. Foundry-owned fields may be refreshed
automatically only after the mapping and validation rules are approved.

### 6.3 Foundry constraints

The deployed baseline currently identified is:

- world: `The Guild`;
- world ID: `the-guild`;
- Foundry core: `14.365`;
- system: `dnd5e`;
- system version: `5.3.3`;
- source folder: `Characters (active)`.

The connector must check compatible versions and fail safely on unsupported
versions. It must use a Foundry module and authenticated HTTPS API. Reading or
writing the live LevelDB database is not an application integration.

## 7. Database model

The exact physical schema is finalized through migrations and ADRs. The
following logical model is required.

### 7.1 Identity and authorization

- `discord_users`
- `discord_guild_memberships`
- `discord_role_snapshots`
- `characters`
- `character_access`
- `service_principals`
- `sessions`

### 7.2 External mappings

- `external_worlds`
- `external_actor_mappings`
- `sheet_row_mappings`
- `sync_runs`
- `sync_snapshots`
- `sync_differences`
- `sync_resolutions`

### 7.3 Character and game state

- `character_profiles`
- `character_resources`
- `wallet_balances`
- `resource_transactions`
- `items`
- `character_items`
- `proficiencies`
- `character_proficiencies`
- `languages`
- `character_languages`
- `learning_projects`
- `crafting_projects`
- `lifestyle_states`
- `bastions`
- `bastion_facilities`
- `bastion_turns`

Do not create every future table in the first migration. Add tables when a
milestone has a real use case, domain model, and tests.

### 7.4 Missions and reports

- `missions`
- `mission_sessions`
- `mission_registrations`
- `attendance_intervals`
- `mission_participants`
- `mission_reports`
- `mission_report_revisions`
- `loot_lots`
- `loot_entries`
- `loot_claims`
- `reward_policies`
- `mission_settlements`
- `settlement_entries`
- `discord_event_mappings`

### 7.5 Approval and audit

- `approval_requests`
- `approval_decisions`
- `audit_events`
- `idempotency_keys`
- `outbox_events`

Audit records are append-only. Corrections create new compensating actions.
They do not mutate or delete historical transactions.

### 7.6 Data representation rules

- Store currency in integer copper.
- Store Discord snowflakes safely as 64-bit integers or canonical strings.
- Use UUIDs or another documented stable application ID format.
- Store UTC-aware timestamps.
- Use foreign keys, uniqueness constraints, and check constraints.
- Add optimistic concurrency/version columns to mutable aggregates.
- Store policy/rule versions with calculated settlements.
- Do not use binary floats for persisted money or divisible resources.
- Prefer normalized records over comma-separated Sheet-era strings.

## 8. Approval workflow

### 8.1 General states

```text
Draft → Submitted → Pending Council Review
      → Approved and Applied
      → Rejected
      → Cancelled
```

An approved record may later enter a correction workflow, but the original
approval remains immutable.

### 8.2 Requirements

- No approval applies changes before the transaction commits.
- The preview shows every affected aggregate and before/after value.
- Council may edit proposals before approval.
- Overrides require a reason.
- Approval records the actor, role context, timestamp, policy version, source,
  and correlation ID.
- Application is atomic across all affected characters.
- Double-clicks and retries cannot apply a proposal twice.
- Stale proposals fail with a clear conflict and must be recalculated.
- Optional two-person approval may later be enabled for configured thresholds.

## 9. Security baseline

Security work is part of each milestone, not a final hardening phase.

### 9.1 Authentication

- Discord OAuth2 with minimum required scopes.
- Verify current guild membership.
- Resolve authorization through configured stable role IDs.
- Use server-side sessions or a comparably safe design.
- Rotate sessions after login and privilege changes.
- Support logout and server-side revocation.

### 9.2 Web security

- HTTPS only in production.
- Secure, HTTP-only, SameSite cookies.
- CSRF protection for cookie-authenticated mutations.
- Restrictive CORS.
- Input validation at every boundary.
- Context-aware output escaping.
- Content Security Policy.
- Rate limits on authentication and sensitive endpoints.
- Request size limits.
- Safe error pages without secrets or internal details.
- No database, OAuth, Discord, or Foundry credentials in browser code.

### 9.3 Database and infrastructure

- PostgreSQL is not exposed to the public internet.
- Use a restricted application database role.
- Store secrets in protected environment/service configuration.
- Encrypt backups and test restoration.
- Separate production, staging, and development configuration.
- Use structured logging without access tokens or unnecessary player data.
- Apply dependency and container/package security updates deliberately.

### 9.4 Privacy

- Collect only necessary Discord identity and role data.
- Define retention for OAuth tokens, attendance, audit data, and reports.
- Do not record voice audio in the initial product.
- Attendance uses Discord voice-state join/leave events only.
- Provide administrative export/deletion handling consistent with legal and
  operational obligations.

## 10. Mission and attendance model

### 10.1 Lifecycle

```text
Mission draft
  → Discord event published
  → player registration and character selection
  → session attendance observed
  → DM roster and report review
  → calculated settlement
  → Guild Council edit and approval
  → atomic application and Discord announcement
```

### 10.2 Attendance

Track:

- Discord user;
- channel;
- join and leave timestamps;
- reconnect intervals;
- total observed duration;
- registered character;
- DM/player/spectator classification; and
- manual confirmation state.

Voice attendance is evidence, not proof. It never grants rewards by itself.
The DM confirms the roster, and Guild Council approves the settlement.

### 10.3 Reports

Reports are structured and versioned:

- title and summary;
- mission/session references;
- DM and participants;
- locations and NPCs;
- objectives and outcomes;
- discoveries and lore;
- encounters;
- loot;
- council-only notes;
- publication status; and
- revision history.

### 10.4 Reward settlement

The deterministic rules engine proposes:

- guild rewards;
- report compensation;
- advancement credit;
- advancement-for-gold alternative;
- historical Moradinium conversion;
- extra-reward caps;
- equal loot distribution;
- item-claim compensation;
- DM rewards;
- mission counts;
- last-played dates;
- campaign counters; and
- badge/level eligibility proposals.

No automatic advancement is allowed. Council approval is mandatory.

## 11. Bastion strategy

### 11.1 Basic Bastions

First migrate existing behavior:

- ownership flag;
- lifestyle relationship;
- maintenance weeks;
- turn availability;
- special-facility limit;
- maintenance cost;
- turn history; and
- approval/correction flow.

### 11.2 Special facilities

Do not implement all facilities as ad hoc conditionals or an unrestricted
expression language.

Create a facility catalogue that can represent:

- rule source and version;
- prerequisites;
- size/space;
- construction cost and duration;
- staffing;
- available orders;
- cooldowns;
- inputs and outputs;
- rolls;
- character and mission interactions;
- upgrade/replacement paths; and
- exceptional bespoke behavior.

Implement in increasing complexity:

1. informational facilities;
2. fixed-cost/fixed-output facilities;
3. inventory-producing facilities;
4. facilities involving rolls;
5. cross-character or mission interactions; and
6. exceptional facilities requiring dedicated policy objects.

Every facility requires rule citations, boundary tests, preview behavior, and
Council-approved application.

## 12. Implementation phases

Each phase ends at a review gate. Claude Code must not silently continue across
a blocking gate.

### Phase 0 — Discovery and architecture

Target: 3–5 working days

Deliver:

- Sheet schema/formula inventory;
- command/use-case inventory;
- Foundry field samples and mapping;
- rule catalogue with PDF references;
- field-ownership draft;
- initial ADRs;
- anonymized fixtures;
- documented local/staging topology.

Acceptance:

- every current bot command has known reads, writes, and rule sources;
- no secrets or real player records are committed;
- unresolved ownership questions are listed explicitly;
- maintainer approves architecture ADRs.

Review gate: architecture and data handling.

### Phase 1 — Database foundation

Target: 4–7 working days

Deliver:

- PostgreSQL development setup;
- migration framework;
- identity, character, access, external mapping, audit, and idempotency tables;
- repository interfaces and database adapters;
- transaction boundary conventions;
- database integration-test setup;
- backup/restore development procedure.

Acceptance:

- migrations apply to an empty database;
- downgrade/recovery strategy is documented;
- constraints reject invalid data;
- repository contract tests pass;
- current bot remains unchanged in production behavior.

Review gate: schema, migrations, constraints, and transaction safety.

### Phase 2 — Import and reconciliation

Target: 4–7 working days

Deliver:

- dry-runnable Sheet importer;
- Foundry active-character snapshot importer through a safe adapter;
- stable external mappings;
- validation and reconciliation reports;
- repeatable/idempotent imports;
- no production writes.

Acceptance:

- all active characters map or are explicitly unresolved;
- duplicates and malformed fields are reported;
- repeated imports do not create duplicates;
- import failure cannot partially commit;
- real data is not copied into tests.

Review gate: data integrity and migration safety.

### Phase 3 — Authentication and read-only portal

Target: 5–8 working days

Deliver:

- Discord OAuth login/logout;
- membership and role verification;
- secure session handling;
- Council character-link management;
- Freedom Blades visual baseline;
- My Characters page;
- character detail page;
- read-only reconciliation view;
- security headers and CSRF foundation.

Acceptance:

- unauthenticated users cannot access protected data;
- ordinary members cannot access Council functions;
- Council authorization uses role ID;
- revoked membership/role is handled;
- multiple characters per user work;
- security tests cover common authorization failures.

Review gate: authentication, authorization, and web security.

### Phase 4 — Shared application services

Target: 5–10 working days

Deliver:

- framework-free money and resource domain objects;
- application command/query interfaces;
- transaction ledger;
- typed errors;
- idempotent command execution;
- characterization tests for Sheet-era behavior;
- first read-only bot command using the new application layer.

Acceptance:

- domain imports no infrastructure frameworks;
- money uses integer copper;
- duplicate mutations are safe;
- concurrent stale updates are detected;
- tests characterize intended current behavior.

Review gate: dependency direction and domain correctness.

### Phase 5 — Existing automation migration

Target: 10–15 working days

Migrate in order:

1. `/info`;
2. `/xchange`;
3. lifestyle;
4. mining and work;
5. learning;
6. crafting;
7. sales;
8. trades; and
9. existing Bastion maintenance.

For each command:

- authorize linked character;
- call one application service;
- execute atomically;
- use Discord interaction ID for idempotency;
- emit ledger and audit records;
- render safe responses;
- compare with Sheet-era behavior.

Acceptance:

- no command can mutate an unlinked character;
- trade/crafting cannot partially apply;
- database and domain tests pass;
- feature flags permit controlled cutover;
- Sheet rollback path exists during verification.

Review gates: first mutation, trade atomicity, crafting/learning rules, and final
bot cutover.

### Phase 6 — Council approval centre

Target: 5–8 working days

Deliver:

- approval queues;
- editable proposals;
- before/after diffs;
- approve/reject flows;
- override reasons;
- corrections through compensating transactions;
- audit search;
- stale-proposal detection.

Acceptance:

- no proposal applies before approval;
- approval is atomic and idempotent;
- ordinary users cannot call approval endpoints;
- stale data cannot be approved silently;
- history cannot be erased through normal UI.

Review gate: authorization, auditability, and correction safety.

### Phase 7 — Foundry connector

Target: 7–10 working days

Deliver:

- minimal versioned Foundry module;
- scoped service authentication;
- compatible-version check;
- active-folder character snapshots;
- field-level comparison;
- Council review for shared fields;
- sync diagnostics and retry behavior.

Acceptance:

- no direct LevelDB access in production integration;
- unsupported versions fail safely;
- credentials are scoped and revocable;
- database-owned values are not overwritten;
- duplicate snapshots are idempotent;
- sync failures are visible and recoverable.

Review gate: Foundry security and conflict semantics.

### Phase 8 — Missions, Discord events, and attendance

Target: 7–12 working days

Deliver:

- mission/session records;
- Discord Scheduled Event mapping;
- registration with linked-character selection;
- voice-state attendance intervals;
- DM roster confirmation;
- mission states and permissions;
- Discord notifications.

Acceptance:

- reconnects do not inflate attendance;
- spectators and DMs can be classified;
- attendance never grants rewards automatically;
- event deletion does not destroy mission records;
- Discord API retries are safe.

Review gate: attendance correctness and privacy.

### Phase 9 — Reports and reward settlements

Target: 8–12 working days

Deliver:

- structured report editor;
- report revisions;
- loot entry, sale, assignment, and claims;
- deterministic reward calculation;
- settlement preview;
- Council editing and approval;
- atomic multi-character application;
- Discord result announcement.

Acceptance:

- rules cite approved sources/policy versions;
- every affected character shows before/after values;
- reward caps and alternatives have boundary tests;
- no advancement occurs without Council approval;
- partial settlement is impossible;
- correction flow preserves history.

Review gate: rules correctness and financial integrity.

### Phase 10 — Basic Bastions

Target: 4–7 working days

Deliver:

- database-backed existing Bastion state;
- maintenance and turn history;
- existing special-facility limit calculation;
- Council previews and corrections;
- bot and web views using shared services.

Acceptance:

- existing behavior is characterized;
- turns cannot be spent twice;
- resource deductions are atomic;
- Council approval policy is enforced.

Review gate: Bastion state machine.

### Phase 11 — Facility framework and initial catalogue

Target: 10–20 working days for framework and first useful batch

Deliver:

- facility definition contract;
- prerequisite evaluation;
- order lifecycle;
- preview/apply separation;
- rule-version handling;
- first representative facilities from each low-complexity category;
- facility-specific tests.

Acceptance:

- facility definitions cannot execute arbitrary code;
- unsupported effects fail explicitly;
- previews match applied transactions;
- each implemented facility has rule citations and tests;
- framework accommodates at least one bespoke facility without becoming a
  general-purpose scripting engine.

Review gates: facility abstraction, first complex facility, and catalogue batch.

### Phase 12 — Optional AI report helper

Begin only after manual reports and settlements are reliable.

Deliver:

- report-draft interface;
- explicit human review;
- proposed entity/loot extraction;
- provenance and AI-use disclosure;
- retention and privacy policy;
- provider abstraction.

AI output cannot mutate game state. Voice recording remains a separate future
decision requiring explicit consent, privacy review, and deletion guarantees.

## 13. Testing strategy

### 13.1 Test pyramid

- Unit tests: calculations, value objects, state transitions, permissions.
- Application tests: use cases with fake repositories and clocks.
- Contract tests: repositories and external adapter contracts.
- Integration tests: PostgreSQL migrations, constraints, locking, transactions.
- Web tests: sessions, CSRF, authorization, validation, stale forms.
- Discord tests: interactions, ownership, retries, channel/role denial.
- Foundry tests: schema/version contracts, retries, conflicts, duplicates.
- End-to-end tests: a small set of staging flows with synthetic data.

### 13.2 Mandatory scenarios

- insufficient resources;
- invalid and negative values;
- duplicate Discord interaction;
- double approval;
- stale optimistic version;
- concurrent trade/edit;
- partial external failure;
- authorization denied;
- guild role removed;
- Actor renamed;
- Foundry duplicate/missing mapping;
- Sheet malformed row;
- migration failure and recovery;
- mission settlement affecting multiple characters;
- correction after approval;
- attendance reconnect and late join;
- unsupported Foundry version.

Tests must never contact production Discord, Sheets, Foundry, or PostgreSQL.

## 14. Deployment and operations

### 14.1 Environments

- Development: synthetic/anonymized data.
- Staging: production-like topology with separate credentials and database.
- Production: live services with restricted access.

### 14.2 Deployment gate

Before each production deployment:

1. review diff and migrations;
2. run unit, application, and integration tests;
3. run formatter, linter, and type checker;
4. scan for secrets and unsafe logging;
5. back up the production database;
6. verify rollback/recovery steps;
7. deploy database-compatible application versions;
8. run health and smoke checks;
9. monitor logs and error rates; and
10. record the deployment.

### 14.3 Backup and recovery

- Automated encrypted PostgreSQL backups.
- Defined retention and off-host copy.
- Restore tests, not merely backup success messages.
- Pre-migration backup.
- Foundry backup before any approved outbound sync batch.
- Sheet retained read-only for a defined verification window.

Applied migrations are never edited. Roll forward or create a documented
recovery migration.

## 15. Google Sheets retirement

Use these stages:

1. characterize Sheet behavior;
2. import into PostgreSQL;
3. shadow-read and reconcile;
4. cut selected reads over behind flags;
5. cut selected writes over;
6. make Sheet read-only;
7. verify for an agreed period;
8. export/archive the Sheet;
9. remove service-account credentials and adapter.

Avoid indefinite dual writes. If temporary dual writes are approved, designate
one authority, durably record secondary-write failures, and provide automated
reconciliation.

## 16. Claude Code working protocol

### 16.1 Before each milestone

Claude Code must:

1. read `.agents/AGENTS.md` completely;
2. read this document and applicable ADRs;
3. inspect `git status`;
4. preserve unrelated changes;
5. trace affected production paths;
6. identify rules and source sections;
7. state assumptions and unresolved decisions;
8. propose a milestone-sized plan; and
9. wait for maintainer approval when a decision changes architecture, data
   ownership, permissions, or production behavior.

### 16.2 Implementation rules

- Work on one milestone or explicitly scoped slice.
- Add tests before or with behavior.
- Do not use real credentials or player data.
- Do not mutate live Sheets, Foundry, Discord, or production PostgreSQL.
- Do not bypass failing tests or authorization.
- Do not introduce drive-by frameworks or mass rewrites.
- Update migrations, configuration examples, and operations docs together.
- Keep external I/O outside the domain.
- Use application services from both web and bot adapters.
- Stop on ambiguous rule conflicts and document them.

### 16.3 Milestone handoff

Claude Code reports:

- requirements implemented;
- files changed;
- migrations added;
- security implications;
- commands/tests run and exact results;
- checks not run;
- configuration/deployment changes;
- rollback/recovery steps;
- unresolved questions; and
- proposed reviewer focus areas.

### 16.4 Reviewer checkpoints

Codex review is required for:

- architecture and initial schema;
- authentication and authorization;
- first database mutation;
- import/reconciliation;
- bot write cutover;
- trades and multi-actor atomicity;
- Foundry connector;
- approval centre;
- mission attendance;
- reward settlement;
- Bastion state machine;
- facility framework; and
- production readiness.

Review findings are classified:

- **Blocking**: security, data loss, authorization, rule correctness, migration,
  atomicity, or production reliability issue.
- **Important**: material maintainability, testing, performance, or operational
  weakness.
- **Optional**: improvement that does not block the milestone.

Blocking findings must be resolved and re-reviewed before proceeding.

## 17. Decision log required before Phase 1 completion

Maintainers must decide and record:

- exact Discord guild and Council role IDs through configuration;
- which Discord roles grant DM capabilities;
- ordinary-user website mutation policy;
- character co-ownership/delegation policy;
- field ownership for currency, inventory, languages, and proficiencies;
- initial source of truth during Sheet migration;
- mission approval rules;
- whether an approver may approve their own draft;
- thresholds requiring a second approver, if any;
- event/announcement channel mappings;
- production domain and reverse proxy;
- PostgreSQL deployment/backup method;
- staging strategy;
- retention policy for attendance and reports; and
- supported Foundry/D&D5e version range.

## 18. Initial release definition

The first releasable version contains:

- PostgreSQL and migrations;
- Discord OAuth;
- guild and Council-role verification;
- Council-managed multi-character links;
- imported active Foundry characters;
- read-only Sheet/database/Foundry reconciliation;
- My Characters and character detail pages;
- audit foundation;
- Freedom Blades branding;
- automated tests;
- staging deployment; and
- backup/restore documentation.

It intentionally does not yet:

- mutate character state from the website;
- write to Foundry;
- retire Google Sheets;
- calculate mission rewards;
- automate special facilities;
- record or transcribe voice.

## 19. Definition of platform completion

The platform is not “complete” merely because pages exist.

A production feature is complete when:

- its requirement and rule source are documented;
- domain behavior is reusable across interfaces;
- authorization is enforced server-side;
- state changes are transactional and auditable;
- retries and concurrency are safe;
- tests cover success and failure paths;
- migration and recovery are documented;
- production monitoring exists;
- sensitive data and secrets are protected; and
- maintainers have accepted the user workflow.

## 20. Immediate next actions

1. Maintainer reviews and approves or amends this plan.
2. Add ADRs for repository strategy, web stack, database, authentication, and
   field ownership.
3. Catalogue Google Sheet schema, bot commands, and rules.
4. Create a sanitized Foundry/Sheet mapping fixture.
5. Establish PostgreSQL development and test environments.
6. Begin Phase 1 only after the Phase 0 review gate.

