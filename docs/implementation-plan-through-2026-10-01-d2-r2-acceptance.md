# Freedom Blades Platform — Master Implementation Plan

Status: Controlled baseline v1.6 — accepted 2026-08-27; Phase 3 gate approved
2026-08-28; Phase 4 gate approved 2026-08-29 and Phase 5 package planning
released subject to package-specific readiness and gates

Baseline date: 2026-08-27

Document owner: Peter Duscha, Product Owner

Acceptance authority: Peter Duscha, Maintainer and Product Sponsor

Audience: Maintainers, implementation agents, reviewers, and operators

Repository: `freedom-bot` (to evolve into the Freedom Blades platform)

Primary rules source: `Freedom Blades - Homebrew Rules.pdf`

## Reading map — which sections a task actually needs

This document is long and is cited by section number from roughly 126 other
documents, so **it is deliberately not split into per-phase files**: the section
numbers are load-bearing references in review artifacts that must not be
rewritten. Read it by section instead.

**Always read first**, whatever the task:

| Section | Why |
|---|---|
| [§0](#0-document-control-and-project-governance) | baseline, change control, accountable roles |
| [§20](#20-immediate-next-actions) | the current action pointer and what is authorized right now |
| [§16](#16-claude-code-working-protocol) | the agent working protocol, handoff and reviewer checkpoints |

**Then read the sections your task touches**, and no more:

| Task | Sections |
|---|---|
| Any milestone or phase work | [§12](#12-implementation-phases), plus the phase's own subsection and acceptance criteria |
| Architecture or layering | [§3](#3-governing-principles), [§5](#5-system-architecture) |
| Schema, migration or import | [§6](#6-data-ownership-and-synchronization), [§7](#7-database-model); skill `migration-staging` |
| Authorization, roles or approval | [§4](#4-product-roles-and-authorization), [§8](#8-approval-workflow), [§9](#9-security-baseline) |
| Missions, attendance or rewards | [§10](#10-mission-and-attendance-model) |
| Bastions or facilities | [§11](#11-bastion-strategy); skill `rules-sourcing` |
| Testing or evidence | [§13](#13-testing-strategy); skill `run-suites` |
| Deployment or operations | [§14](#14-deployment-and-operations) |
| Retiring the Freedom bot or Sheets | [§15](#15-legacy-runtime-retirement) |
| A decision, gate or release question | [§17](#17-decision-governance), [§18](#18-initial-release-definition), [§19](#19-definition-of-platform-completion) |

Reading a section you do not need is waste; **skipping one you do need is a
defect**. When in doubt, read it. Nothing here narrows §16.1's requirement to
read `.agents/AGENTS.md` completely, which is short and has no scoped reading.

## 0. Document control and project governance

### 0.1 Purpose of this document

This document is the product roadmap and technical milestone contract. It says
what outcomes and controls each phase must deliver. It is not, by itself, a
calendar commitment or a substitute for a phase delivery plan.

Detailed project controls live under `docs/project-management/`:

- [`README.md`](project-management/README.md) — governance, roles, gate process,
  estimation rules and management definition of ready/done;
- [`status.md`](project-management/status.md) — concise current phase, gate,
  forecast, evidence and blockers; verbatim history is indexed under
  [`status-archive/`](project-management/status-archive/);
- [`raid-register.md`](project-management/raid-register.md) — risks,
  assumptions, issues and dependencies;
- [`decision-register.md`](project-management/decision-register.md) — decision
  index and deadlines, linked to the full OD record; and
- [`change-log.md`](project-management/change-log.md) — baseline amendments and
  their scope, schedule and risk effects.

The approved technical requirements remain in this document and the linked
ADRs, rules, operations and review records. Supporting registers may summarize
them but never silently override them.

### 0.2 Baseline and change control

Version 1.0 is the controlled baseline accepted by Peter Duscha on 2026-08-02,
as recorded in `docs/project-management/change-log.md`. Earlier phase
acceptances remain valid evidence; they do not by themselves approve later
scope, estimates or gates.

After acceptance, a material change to scope, authority, privacy, architecture,
data ownership, release criteria, phase order or target range requires:

1. a change-log entry identifying requester, reason and affected requirements;
2. impact assessment for scope, dependencies, estimate, risk, testing,
   migration and operations;
3. Product Owner recommendation and Technical Lead review;
4. Acceptance Authority approval before the change becomes effective; and
5. a new baseline version when the roadmap or release boundary changes.

Clarifications that do not change those matters may be recorded without a new
baseline, but still need a dated change-log entry. Git history is evidence of
edits, not evidence of project approval.

Archiving verbatim superseded status or handover blocks is a documentation
clarification, not a baseline change, when the canonical paths remain as
current-state entry points, archive hashes and navigation are recorded, and no
decision, finding, gate, authority or disposition changes. Archived text is
evidence and must not be silently rewritten. A historical authorization does
not become current authority when moved, linked or read.

### 0.3 Accountable roles

AI assistants may implement or review work, but project and release
accountability remains with the maintainer. This is a solo-maintainer project:
Peter Duscha may hold multiple accountable roles. Independent technical review
may be performed by an agent that did not implement the work, but that reviewer
cannot approve its own recommendation; Peter records the gate decision.

| Role | Accountable for |
|---|---|
| Product Sponsor / Acceptance Authority | baseline, priority, funding/capacity, risk acceptance and release approval |
| Product Owner | scope, outcomes, backlog order, decisions and acceptance recommendation |
| Technical Lead | architecture, decomposition, estimates, technical integration and readiness recommendation |
| Data Owner | field ownership, migration reconciliation and real-data rehearsal approval |
| Security Reviewer | authentication, authorization, privacy and security gate evidence |
| Operations Owner | environments, backup/restore, deployment, monitoring, rollback and service readiness |
| Delivery Lead | status, dependencies, RAID, change control, gate scheduling and forecast |
| Independent Reviewer | evidence-based review without approving their own implementation |

Current assignment: Peter Duscha is Product Sponsor, Acceptance Authority,
Product Owner, Data Owner, Operations Owner and Delivery Lead. For each package,
Peter designates the implementing agent as the working Technical Lead.

At a **mandatory review checkpoint** — every subject listed in §16.4, and every
gate whose row in the `docs/project-management/README.md` gate-authority table
requires an Independent Reviewer recommendation — a **different** Independent
Reviewer than the implementer is **required**. If none is available, the package
remains `deferred`; the gate is not approved, not conditionally approved, and
not closed on the implementer's own recommendation. *Where practical* applies
only to reviews that neither list mandates.

Security-sensitive work receives a separate security-focused review before Peter
decides its gate. Tool names such as Claude, Gemini and Codex describe delivery
resources, not approval authority.

### 0.4 Planning and reporting rules

- Target ranges are rough-order planning ranges for one focused implementer;
  they are not commitments and exclude blocked time unless a phase plan states
  otherwise.
- Before a phase starts, its Technical Lead produces a work breakdown,
  dependency check, capacity assumption, estimate range with confidence,
  review/remediation allowance and named owners.
- Calendar forecasts include maintainer decisions, independent review,
  remediation, operational rehearsal, deployment and contingency.
- Progress is measured by accepted deliverables and closed gate criteria, not
  lines of code, elapsed time or raw test counts.
- A phase plan must replace subjective terms such as `promptly`, `small`,
  `reliably`, `agreed period` or `production-like` with a numeric threshold,
  named environment or an explicitly approved operational check before the
  affected criterion can close.
- The Delivery Lead updates `docs/project-management/status.md` at each material
  change and at least once per active delivery week.
- Forecast variance outside the approved range, a newly critical risk, or a
  blocked critical-path dependency triggers re-planning rather than silent
  compression of testing or review.

### 0.5 Project success measures

The first release succeeds only when all §18 scope is accepted and:

- every imported active Actor is mapped or explicitly unresolved in the signed
  reconciliation report; no identity discrepancy is silently accepted;
- automated migration/import tests show zero partial commits across injected
  failure paths and the supervised rehearsal produces no unexplained mutation;
- authorization tests show zero successful ordinary-member calls to Council or
  Platform-Administrator operations;
- duplicate and concurrent apply tests produce one durable effect and no
  duplicate audit effect;
- backup restoration and the documented application rollback are exercised in
  a disposable or staging environment within the release gate;
- all blocking review findings are closed and re-reviewed, with no waived
  security, identity, financial-integrity, migration or authorization defect;
- monitoring exposes health without secrets or player data; and
- the Acceptance Authority signs the release record after the Data, Security
  and Operations Owners recommend readiness.

## 1. Purpose

This document is the implementation contract for evolving the current
Freedom Bot into a secure, database-backed Freedom Blades platform.

The target product consists of:

- a branded web application;
- the existing Freedom bot, reduced over time to a Discord adapter and then retired under §15.2; Discord itself is retained permanently;
- a PostgreSQL database and immutable transaction/audit history;
- Discord authentication, role verification, events, attendance, and
  notifications;
- controlled synchronization with the Foundry VTT world `The Guild`;
- Guild Council approval workflows;
- automated homebrew workflows for downtime, crafting, learning, mining,
  lifestyle, missions, rewards, and Bastions; and
- a future, optional AI-assisted report-writing workflow.

Music is not part of the platform. Its former command implementation,
dependencies, configuration and deployment templates have been removed. No
platform phase or release criterion includes music.

This is an incremental replacement of a live system. It is not a rewrite and
does not authorize deleting the current bot, its current Google Sheets runtime
integration, live data, or deployment configuration. The legacy Freedom bot
continues to use Google Sheets until its Sheet-backed behavior has been replaced
by the database-backed Freedom Blades Manager and the cutover has been verified.
The Foundry active-character snapshot supplies Actor data outside the Sheet-era
model. Google Sheets remains the accepted legacy store for each Sheet-era field
until that field's typed domain package passes migration and cutover. It is not
the permanent platform authority, and its state is not copied into a generic
interim database model.

## 2. Repository strategy

### 2.1 Decision

Develop the platform inside this repository.

Do not create a temporary sibling application that will later replace the
repository. Do not delete the Freedom bot after the website is introduced; its retirement is governed solely by §15.2, and Discord itself is never retired.
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
8. Google Sheets remains a legacy Discord-bot dependency and per-field legacy
   authority during the transition. Each typed package migrates its fields once;
   the Sheet is retired only after every database-backed replacement and cutover
   has been verified.
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
Freedom bot ───────────────────┼─> Application services ─> Domain
                               │             │
Foundry module ────────────────┘             ▼
                                         Repositories
                                             │
                  ┌──────────────────────────┼──────────────────┐
                  ▼                          ▼                  ▼
              PostgreSQL              Google Sheets       External APIs
             authoritative          legacy bot only      Discord/Foundry
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

- **Foundry snapshot-only**: read from the immutable snapshot for display or
  calculations, with no independently editable database representation.
- **Foundry-owned**: database imports changes where a concrete platform use case
  requires a persisted projection; database does not overwrite it.
- **Database-owned**: Foundry differences create warnings or may be copied into
  the database only through an explicit, selected Council correction.
- **Council-approved shared**: Foundry differences create approval proposals.
- **Derived**: calculated from authoritative inputs; Council corrections change
  the inputs or create an explicit compensating override rather than silently
  replacing history.
- **Display-only**: cached for presentation and safe to refresh.

Initial recommendation:

| Field group | Initial owner |
|---|---|
| Foundry Actor ID and world ID | external mapping |
| Character name and image | Foundry snapshot for comparison/display; name may be corrected in PostgreSQL through the protected workflow |
| Species/race, class, subclass, background, ability scores, feats and level | PostgreSQL, protected Council correction |
| Discord ownership links | PostgreSQL |
| Missions, badges, last played | PostgreSQL |
| Downtime and learning progress | PostgreSQL |
| Lifestyle/living cost, weekly expenses and Moradinium | PostgreSQL |
| CRP and homebrew crafting state | PostgreSQL |
| Bastion state | PostgreSQL |
| Currency, debt and other homebrew balances | PostgreSQL |
| Magic and homebrew-managed items | PostgreSQL; maintained manually in Foundry and compared on snapshot import |
| Languages, tool proficiencies and special-weapon proficiencies | PostgreSQL; maintained manually in Foundry and compared on snapshot import |
| Specials, no-shows and other Sheet-era homebrew state | PostgreSQL |
| Skill proficiencies, mundane items, resistances, speed, conditions and other non-homebrew Actor mechanics | Foundry snapshot, read-only; persist no separately managed copy unless a later use case requires one |

The matrix states the **target owner**, not that the field has already migrated.
Each row also has a migration state: `legacy`, `shadow`, `database`, or
`retired`. Until a package-specific gate moves a field to `database`, its
accepted legacy path remains authoritative for production behavior and the new
platform must not write it. Target ownership never authorizes a premature
generic representation or an unreviewed cutover.

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

A Foundry snapshot is read-only evidence and a source of roll inputs. Skill
proficiencies and other non-homebrew Actor mechanics are read from the immutable
snapshot when application services need them; they do not become a second
managed character model in PostgreSQL. Database-authoritative values are used
for calculations whenever the database owns that field.

For magic items, languages, tool proficiencies, special-weapon proficiencies and
every other database-owned field represented in Foundry, reconciliation emits a
warning that the Foundry Actor is out of date and should be updated manually.
The platform does not write changes back to Foundry in this release.

A Guild Council member may deliberately use snapshot values to correct selected
database-authoritative fields, but never through a whole-Actor overwrite. The
preview presents a versioned allowlist of eligible fields as individually
selectable checkboxes, defaults them to unselected, shows before/after values and
all affected calculations, and requires one Council member to confirm. The
correction is atomic and append-only audited with the snapshot checksum and a
reason. Reference-only Foundry fields and unknown JSON paths are never eligible
for database overwrite.

Every database-managed current-state field is manually correctable by any one
currently authorized Guild Council member **after the package owning that field
has introduced its typed domain model and passed its migration/cutover gate**.
No second approver is required. Before that gate, corrections continue through
the accepted legacy workflow and the platform may compare or report the field
but must not persist a second editable representation.
Corrections must use domain-aware operations: ledger, mission, crafting,
inventory and other historical state is corrected through an explicit
compensating action rather than editing or deleting the original record.

Field ownership and correction sensitivity are separate. The versioned field
profile assigns each database-managed field one correction mode:

- **standard correction**: editable by one Council member with validation and a
  required reason;
- **protected correction**: for identity and progression facts such as name,
  race/species, class, subclass, background, ability scores, feats and level;
  it requires a dedicated before/after confirmation and warns about dependent
  calculations, but still requires only one Council member; or
- **compensating correction**: for balances, items, downtime, missions, debt,
  expenses and other transaction/history-backed state; it appends a correction
  transaction and leaves the original history intact.

Every successful or refused correction records the Council Discord user,
authorization context, time, source, reason, before/after values, correlation ID
and, when applicable, snapshot checksum. Council members and Platform
Administrators can read and search these audit records, but neither role can
change or delete them through the application.

### 6.3 Foundry constraints

The deployed baseline currently identified is:

- world: `The Guild`;
- world ID: `the-guild`;
- Foundry core: `14.367`;
- system: `dnd5e`;
- system version: `5.3.3`;
- source folder: `Characters (active)`.

Phase 2 does not connect to live Foundry. A Guild Council member deliberately
exports an offline snapshot. The importer operates only on the supplied
artifact and never writes to Foundry.

The Phase 7 live connector must check compatible versions and fail safely on
unsupported versions. It must use a Foundry module and authenticated HTTPS API.
Reading or writing the live LevelDB database is not an application integration.

### 6.4 Immutable Foundry snapshot

The Phase 2 snapshot is an immutable, content-addressed record rather than a
mutable interchange file:

- the export includes the world ID, Foundry core version, game-system ID and
  version, source-folder ID and name, export time, schema/exporter version, and
  every selected Actor's stable external ID;
- a Guild Council member takes the snapshot deliberately; one Council member is
  sufficient to trigger an import;
- the original artifact is preserved byte-for-byte and identified by a SHA-256
  checksum recorded before parsing;
- the snapshot record stores its checksum, provenance, triggering Discord user
  or supervised-bootstrap actor, import time, selected folder, outcome, and an
  audit correlation ID;
- changing any byte creates a different snapshot. An imported artifact and its
  audit record are never edited or overwritten;
- preview, apply, reconciliation, audit, and every created external mapping
  reference the same snapshot record and checksum;
- parsing or previewing does not change character data;
- reapplying the same checksum is a successful no-op or a typed
  duplicate result, never a second mutation; and
- a later snapshot is a new immutable record and explicit reconciliation event,
  not a replacement for the initial snapshot.

The supervised first import is a bootstrap operation and requires no separate
approval record. It still records the supervising actor, exact checksum,
selected folder, time, result and correlation ID in the append-only audit log.
Later imports require one currently authorized Guild Council member to trigger
them; triggering the import is the authorization event and no second approval
workflow is required.

The Manager UI accepts an offline snapshot and presents an import button only to
Guild Council members. A Platform Administrator can select which Actor folder
inside the snapshot is used; the default is `/actors/Characters (active)`.
Selecting a folder and triggering an import are separate permissions: Platform
Administrator alone does not grant game-policy authority to apply an import.
Every attempted or completed import, including refusals, is audited. Snapshot
import and reconciliation audit history is visible to Guild Council members and
Platform Administrators; neither can change or delete it through the application.

Snapshots are sensitive operational records. Accept only the documented data
format; enforce byte-size, Actor-count, nesting and parsing limits; reject
archives, executable content, unknown top-level structures and path-bearing
uploads; and parse outside the database transaction. Store original artifacts
with restricted access and encryption/backup treatment. Audit visibility does
not by itself grant permission to download the raw artifact, and snapshot
retention must be documented separately from the permanent checksum and audit
record.

Automated tests use small synthetic artifacts with synthetic actors. Real
Council snapshots are operational inputs and must never be committed as test
fixtures.

### 6.5 Import, correction and audit invariants

The following are implementation contracts, not UI conventions:

- **Exhaustive field profile.** Every supported snapshot path is assigned a
  snapshot mode (`snapshot-only`, `compare`, `Council-correctable`, or
  `ignored`) and every database-managed field is assigned a correction mode
  (`standard`, `protected`, or `compensating`). Unknown paths are reported and
  cannot become writable. A schema change that introduces a field without a
  classification fails closed. The profile has a version stored on every
  preview, import and snapshot-based correction.
- **Immutable preview input.** A preview records the snapshot checksum, selected
  world/folder ID, field-profile version, database aggregate versions, selected
  corrections and idempotency key. Apply rechecks all of them. Any changed
  snapshot, folder, profile or database version makes the preview stale and
  applies nothing.
- **Atomic apply.** One import or correction for fields already migrated to a
  typed database model commits its state changes,
  external mappings, reconciliation results, compensating transactions and
  audit event in one PostgreSQL transaction. An audit failure rolls back the
  state change; a state failure writes no success audit event. After rollback,
  an attempted/refused event may be written in a separate transaction with the
  same correlation ID and safe failure category, but it must not claim or expose
  partial state.
- **Idempotency and concurrency.** Snapshot checksum plus selected folder and
  field-profile version identify an import input. An explicit request key
  identifies an apply attempt. Repeated requests return the original result.
  Concurrent or stale applies cannot duplicate, lose or overwrite state.
- **No implicit deletion.** An Actor missing from a later snapshot produces a
  warning. It never deletes, deactivates or unmaps a character without a
  separate Council correction.
- **Snapshot-backed calculations.** Each calculation records the snapshot
  checksum and exporter/profile version used. Missing, unsupported or stale
  snapshot inputs produce a typed refusal or visible warning according to the
  use case; calculations never silently substitute zero, no proficiency or an
  older unreported value.
- **Bootstrap is one-time.** The supervised bootstrap path is available only
  against an empty/uninitialized Manager dataset, requires an explicit
  bootstrap flag and named supervisor, and disables itself after the first
  successful import. Later imports always require current Guild Council
  authorization.
- **Append-only audit.** The application exposes no audit update/delete use
  case. The restricted runtime database role has `SELECT` and `INSERT`, but no
  `UPDATE`, `DELETE` or `TRUNCATE`, on audit and transaction-history tables;
  database constraints or triggers reject mutation through normal runtime
  connections. Exceptional database-owner recovery is outside the application,
  follows a documented procedure and cannot be presented as ordinary history.
- **Safe audit content.** Audit records identify the snapshot by checksum and
  store necessary structured before/after facts, not credentials, raw uploaded
  files, arbitrary exception text or unrelated private Actor data.
- **Role changes take effect at apply.** Preview permission is not sufficient.
  Current guild membership and Council role are rechecked when applying a
  correction or import. Revocation between preview and apply refuses the action.

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
- `item_definitions`
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

Do not use a generic key/value or JSON character-state table merely to move
Sheet-era values ahead of those models. The package that introduces each typed
aggregate owns its migration from the legacy Sheet, reconciliation, correction
workflow, cutover, recovery and acceptance evidence. Data is migrated once into
its intended domain representation unless a separately approved ADR demonstrates
why an interim store is necessary.

#### 7.3.1 Relational representation of authoritative multi-valued domain facts

Every Google Sheet cell or range that encodes multiple **authoritative
operational domain facts** must be normalized when migrated. Do not persist
such a collection as comma/newline-delimited text, a JSON/JSONB array or object,
a PostgreSQL array, or a generic key/value row. Use the appropriate relational
shape:

- controlled vocabulary: a definition/reference table plus a junction table
  whose parent and definition identifiers are foreign keys;
- owned structured entries such as projects or notes: one typed child row per
  entry with a foreign key to its parent character/player and further foreign
  keys to referenced definitions;
- quantities, ranks, dates, order and status: typed columns on the junction or
  child row, with check constraints and uniqueness rules;
- changing or historical membership: effective-dated rows or append-only
  transactions rather than replacement of a serialized collection.

Do not invent a global definition entity when no shared domain identity exists.
Free-form values owned by one aggregate—such as reviewed character notes—use
typed child rows with their own stable ID and a foreign key to the owning
character, plus position, timestamps or other real facts where applicable. A
definition/reference table is required only for a genuinely shared or
controlled vocabulary.

Reference identities use stable internal IDs; display labels are mutable and
never serve as foreign keys. Junction tables have a declared primary key or
unique constraint preventing duplicate membership. Deletes use `RESTRICT` when
history references a row and are never used to erase audit or transaction
history. An unrecognized source value becomes an explicit unresolved migration
item; it is not silently inserted into a controlled vocabulary or discarded.

Ability scores use the same relational discipline: `ability_definitions`
contains the stable reviewed ability codes and labels, and
`character_ability_scores` references both character and ability. It has a
unique `(character_id, ability_id)` key, a constrained integer score and source
provenance. An authoritative ability map is not stored as JSON.

This rule covers, at minimum, classes/subclasses where multiple entries are
possible, feats, languages, tool and special-weapon proficiencies, artisan
ranks, specials/notes, learning and crafting projects, magic items, campaigns
and character access. An exception permitting serialized collection storage
requires a separate accepted ADR and controlled-baseline change.

This normalization rule does **not** require relational decomposition of:

- immutable original Foundry or other external artifacts retained as evidence;
- immutable audit-event contextual payloads whose authoritative effects are
  already represented in typed operational tables;
- bounded diagnostic or parser metadata used only to explain an import;
- external API payloads preserved for provenance or replay; or
- presentation-only caches that are disposable and never authoritative.

Those exceptions cannot become an alternate editable character model, satisfy
a migrated-field requirement, drive authoritative calculations without typed
validation, or hide a relationship that requires referential integrity. Store
only necessary data, apply size/retention/access controls, and keep searchable
identity, status, checksum, time, actor and correlation fields in typed columns.
If an alleged evidence/metadata/cache exception becomes operational authority,
it must first migrate into the normalized domain model and pass its package
gate.

Before coding a package that introduces normalized legacy data, its definition
of ready includes an independently reviewed logical schema artifact (ER diagram
plus schema decision table) naming table ownership, cardinalities, primary and
foreign keys, unique/check constraints, nullability, delete behavior,
effective-dating/history behavior, vocabulary sources, unresolved-record
handling, expected access patterns and source-to-target control totals. A
material schema change after readiness returns the package through impact
assessment and schema review rather than being absorbed silently.

### 7.4 Magic-item catalogue and character inventory

Magic-item definitions and character ownership are separate concepts. A
catalogue entry may be owned by many characters; ownership must therefore not
be represented by putting a character foreign key on the catalogue row.

Use at least these logical records when crafting and inventory are migrated:

- `source_publications`: stable source code, title, publisher, edition,
  upstream origin (`core`, `prerelease`, or `homebrew`), enabled state, import
  time, and upstream version;
- `item_definitions`: stable internal ID, upstream identifier, source-publication
  ID, name, category, rarity, consumable status, attunement requirement,
  craftable state, and explicitly permitted metadata;
- `item_definition_revisions`: immutable, versioned catalogue facts and any
  permitted descriptive content for a definition, with upstream snapshot,
  effective time and content checksum;
- `character_items`: character ID, item-definition ID, quantity or distinct
  instance identity, the acquired definition revision, attunement state, notes,
  acquisition time, and optimistic version;
- `catalogue_imports`: immutable preview/apply record with upstream repository,
  commit or release identifier, archive checksum, parser/schema version,
  source-selection policy, status, counts and audit correlation ID; and
- append-only inventory transactions recording crafting, acquisition,
  consumption, transfer, correction, and other quantity/ownership changes.

`character_items.character_id` references `characters.id` and
`character_items.item_definition_id` references `item_definitions.id`. Unique
magic items use distinct ownership rows. Stackable consumables may use a
quantity, but every quantity change still receives a transaction and audit
record.

Enforce database constraints, not only application conventions:

- upstream definition identity is unique on source publication plus upstream
  identifier;
- source codes are unique within an upstream catalogue;
- quantities are positive for live ownership rows and transaction deltas may
  not produce a negative balance;
- a distinct item instance has quantity one;
- an attuned ownership row must reference a definition that permits attunement;
- import snapshot/checksum identity is unique, so the same snapshot cannot be
  applied twice; and
- foreign keys prevent deletion of definitions, revisions, characters or
  imports referenced by inventory, crafting, transactions or audit history.

The initial catalogue source is the structured item data used by
`https://5e.tools/items.html`, imported as a reviewed, versioned snapshot rather
than queried during a command. Do not scrape the interactive page or make live
5e.tools availability a dependency of crafting. In this plan, **core** means
records shipped in the upstream repository's main `data` collection; it excludes
the separately distributed `homebrew` and `prerelease` collections regardless
of publisher. The importer must:

1. discover every publication referenced by the core 5e.tools item data;
2. prepopulate and enable the allowlist with those core publications;
3. exclude the separately classified `homebrew` and `prerelease` collections
   by default;
4. show publisher, source code, edition and item count, because presence in the
   core dataset must not be presented as proof that Wizards of the Coast
   published the source;
5. import all magic-item definitions from enabled sources, including potions,
   scrolls, ammunition and every other consumable category;
6. key upstream identity by stable source plus upstream identifier, never by
   mutable or non-unique item name;
7. resolve or explicitly model generic magic variants instead of silently
   flattening or dropping them;
8. preview additions, updates, removals, duplicates and conflicts before an
   administrator applies a refresh;
9. apply each approved catalogue refresh transactionally and audit it with the
   upstream version; and
10. retain definitions referenced by inventory or history when a source is
    disabled or disappears upstream. Such definitions become unavailable for
    new crafting rather than being deleted.

Acquire the upstream data as a pinned commit or versioned release archive and
record a cryptographic checksum before parsing it. A mutable branch, live page,
or unrecorded download is not an import source. Parser behavior is versioned so
the same input and parser version produce the same preview. Automated tests use
small synthetic records shaped like the upstream schema and never copy book
content.

Every import first creates an immutable preview against a specific current
catalogue version. Applying it requires the same snapshot checksum, parser
version, source-selection policy and current catalogue version. Any intervening
catalogue change makes the preview stale and it must be regenerated. A database
lock or equivalent serialization prevents two catalogue applies from
interleaving. Reapplying an already applied snapshot is a successful no-op or a
typed duplicate result, never a second mutation.

Unknown item shapes, missing stable identity, duplicate upstream identity,
unresolved generic variants and contradictory source metadata are blocking
import issues. They are reported with source and record location but no
copyrighted description. Warnings may not silently drop an item. An apply with
any blocking issue commits nothing.

Catalogue refreshes preserve history. Changes to meaningful catalogue facts
create an immutable `item_definition_revision` and move the definition's
current pointer; they do not rewrite an old revision. Existing character items
retain the revision under which they were acquired, while new crafting uses the
current enabled revision. Renames therefore preserve identity, and a removed or
disabled definition remains readable in inventory and history. Upstream
identifier replacement, merges and splits are ambiguous migrations requiring
an explicit reviewed mapping; name similarity alone never rekeys an item.

An administrator may later add or enable another 5e.tools publication through
the same preview/import workflow. Homebrew and prerelease sources require an
explicit Council decision before enablement.

Catalogue membership means that an item is recognized; it does not by itself
mean the item is craftable. Craftability is explicit policy. Character
eligibility remains a separate deterministic calculation over the selected
definition, applicable rules, rarity, prerequisites, recipe, time and cost.
Crafting accepts an `item_definition_id`, not a caller-supplied item name, and
completion atomically creates or increments `character_items` together with its
inventory transaction, resource deductions, crafting result and audit event.
Starting a project records the selected definition revision and policy version.
Completion revalidates source enablement, craftability, prerequisites and
optimistic versions. If any changed, it returns a typed stale-project result and
applies nothing; Council may then review and deliberately rebase or cancel it.

Transfers lock or version-check both character inventories and move the item in
one transaction. Consumption locks or version-checks its stack, refuses an
insufficient quantity, records the negative inventory transaction and never
stores a zero or negative live ownership quantity. Corrections use compensating
transactions rather than editing history.

Catalogue import recovery is roll-back-first: parsing and previewing change no
active catalogue definitions or inventory (an immutable preview record may be
stored); a failed apply rolls back completely; the previously applied catalogue
remains usable. Operations documentation must include how to identify
the last applied snapshot, retry the same immutable input, and restore the
database backup if the database itself fails during deployment. Never repair a
partial catalogue with ad hoc row edits.

Mandatory catalogue and inventory tests include:

- core publications are prepopulated and enabled while homebrew and prerelease
  collections are excluded;
- every supported magic-item category, including representative potions,
  scrolls, ammunition and other consumables, is imported from synthetic data;
- duplicate names in different sources remain distinct, while duplicate stable
  upstream identities block the import;
- importing the same pinned snapshot twice is idempotent and produces no second
  set of revisions or audit effects;
- malformed records, unknown shapes, missing identifiers, contradictory source
  metadata and unresolved variants report deterministic blocking issues and
  commit nothing;
- a stale preview and either of two concurrent applies are refused without
  partial catalogue changes;
- a parser failure, constraint failure or interrupted apply leaves the previous
  catalogue fully usable;
- rename creates a revision under the same identity; removal, source disabling
  and refresh do not alter or orphan existing inventory or history;
- ambiguous merge, split or upstream-ID replacement requires an explicit
  reviewed mapping and is never inferred from a name;
- disabled or unknown definitions cannot start crafting;
- a project made stale by a definition, policy, eligibility or source change
  cannot complete or spend resources;
- unique items create distinct quantity-one instances, consumables stack, and
  insufficient consumption cannot create a negative quantity;
- concurrent consumption, transfer and craft completion detect stale versions
  and cannot duplicate or lose an item;
- transfer updates both characters, inventory transactions and audit in one
  transaction, and a failure rolls all of them back; and
- successful crafting atomically records the acquired revision, inventory,
  resource/ledger effects and audit, while every injected failure leaves all of
  them unchanged.

Treat catalogue text and mechanics as third-party content with provenance. The
licence of an upstream site's software must not be assumed to grant permission
to redistribute every publication's descriptive text. Store only content the
maintainers are authorized to retain; otherwise store identifying catalogue
facts and an external/source reference.

### 7.5 Missions and reports

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

### 7.6 Approval and audit

- `approval_requests`
- `approval_decisions`
- `audit_events`
- `idempotency_keys`
- `outbox_events`

Audit records are append-only. Corrections create new compensating actions.
They do not mutate or delete historical transactions.

### 7.7 Data representation rules

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
- One currently authorized Guild Council member is sufficient for Council
  actions unless a separate future maintainer ruling explicitly changes a
  particular workflow.

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

Each numbered phase ends at a review gate. An implementation agent must not
silently continue across a blocking gate. The frontend visual design track in
§12.1 is deliberately separate from the numbered implementation phases and may
run in parallel under its stated restrictions.

The target ranges below are rough-order effort ranges under §0.4, not calendar
commitments. No phase receives a committed start or finish date until its
management definition of ready is met and a capacity-based phase plan is
accepted.

### 12.0 Dependency and release map

| Work | Required predecessors | May run in parallel with | Gate that releases successor work |
|---|---|---|---|
| Phase 0 | Approved project start | None | Architecture/data-handling gate releases Phase 1 |
| Phase 1 | Phase 0 gate and blocking architecture decisions | Visual prototype | Schema/transaction gate releases Phase 2 |
| Phase 2 | Phase 1 gate, field ownership and Foundry snapshot contract | Visual prototype | Data-integrity/migration gate releases Phase 3 |
| Phase 3 | Phase 2 gate, accepted visual direction, named security reviewer | Phase 4 planning only | Authentication/security gate releases production portal integration |
| Phase 4 | Phase 1 foundations; interfaces coordinated with Phases 2–3 | Late Phase 3 work where contracts do not conflict | Domain/dependency gate releases Phase 5 mutations |
| Phase 5 packages | Phase 4 gate plus package-specific decisions and dependencies | Independent packages only when they touch no shared aggregate/cutover | Package gate releases only its own cutover; final gate releases Sheet retirement verification |
| Phase 6 | Phase 3 security and Phase 4 command foundations | Later independent Phase 5 packages | Approval-centre gate releases workflows that require generic approval |
| Phase 7 | Phase 2 snapshot contract, Phase 3 security and Phase 6 approval where shared fields require it | Independent Phase 5 packages | Foundry gate releases live connector use |
| Phase 8 | Phase 3 identity/security and Phase 4 services | Phases 7 and late Phase 5 where resources permit | Attendance/privacy gate releases Phase 9 |
| Phase 9 | Phase 6 approval centre and Phase 8 mission evidence | Phase 10 planning | Rules/financial-integrity gate releases settlement production use |
| Phase 10 | Phase 4 and relevant Phase 5 economy migration | Phase 9 where aggregates do not overlap | Bastion gate releases Phase 11 |
| Phase 11 | Phase 10 and catalogue/inventory foundations | None for the same Bastion aggregate | Facility gates release catalogue batches |
| Phase 12 | Accepted manual Phase 9 reporting and separate privacy/provider approval | Non-critical-path work only | Separate optional-feature gate |
| Freedom bot retirement (§15.2) | Every migrated command's package gate, Phase 6 approvals, the Phase 8–11 behaviors the bot touches, and §15.1's final Sheet retirement gate | Nothing — it is terminal | Bot-retirement gate; no successor work |

The current critical path and actual gate states are maintained in
`docs/project-management/status.md`. A row stating that work *may* run in
parallel is not authorization to bypass its own readiness criteria.

### 12.1 Parallel track — Frontend visual design prototype

This track may be assigned independently to a frontend-focused implementation
agent, including Gemini. It is design work, not the beginning of Phase 3, and
does not satisfy or bypass any numbered-phase review gate.

The prototype lives under `design-prototype/` until its design is accepted. It
must remain a static, inert preview that can be opened locally without starting
the bot, web application, database, or an external service.

Deliver:

- a Freedom Blades visual language covering colour, typography, spacing,
  borders, elevation, icon treatment, and interaction states;
- responsive application shell and navigation concepts;
- static prototypes for login, My Characters, character detail,
  reconciliation, and Council approval-queue/diff views;
- reusable HTML and CSS component examples for cards, tables, forms, badges,
  alerts, empty/loading/error states, pagination, and confirmation dialogs;
- accessibility notes, responsive breakpoints, and a component inventory; and
- a short integration handoff mapping prototype screens and components to the
  Phase 3 Jinja templates and later HTMX partials.

Constraints:

- use only synthetic names, values, portraits, and records; never copy player,
  production Discord, Sheet, Foundry, or database data;
- do not add FastAPI routes, authentication, sessions, authorization,
  application services, repositories, migrations, API calls, or production
  configuration;
- do not place prototype code in `web/` or import it from production code;
- do not implement a functional login, approval, mutation, upload, sync, or
  persistence flow; controls that suggest these actions are visual examples;
- target the accepted Jinja2 and HTMX architecture, but do not introduce React,
  Vue, another SPA framework, npm, a bundler, or a JavaScript build step;
- use semantic, Jinja-compatible HTML and plain CSS. Optional prototype-only
  JavaScript must be small, local, dependency-free, and removable;
- do not use CDNs, remote fonts, trackers, analytics, or runtime network
  dependencies;
- use repository-owned or appropriately licensed assets, record their source
  and licence, and do not generate or copy protected D&D publication art; and
- preserve visible keyboard focus, usable contrast, reduced-motion behaviour,
  sensible reading order, and narrow-screen operation.

Acceptance:

- every prototype page works as a static local preview with no network access;
- layouts are usable at narrow mobile and desktop widths;
- primary navigation and representative controls are keyboard reachable;
- text and essential controls meet WCAG 2.2 AA contrast targets;
- the component inventory covers normal, empty, loading, validation, denied,
  stale, and system-error states;
- no control can affect real or repository-backed state;
- no production module imports or depends on `design-prototype/`; and
- a maintainer accepts the visual direction before Phase 3 integration.

Review gate: visual direction, accessibility, asset provenance, and fit with
ADR 0002. This review does not approve authentication, authorization, web
security, or production integration.

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

Target: 8–15 working days

Planning note: this historical range is retained only as a rough-order record
and must be re-estimated before the remaining Phase 2 work is forecast. Phase 2
is managed as four evidence-bearing packages: (2.1) immutable artifact/parser
and field profile, (2.2) preview/identity/mapping/reconciliation, (2.3) import
authorization, provenance and audit controls, and (2.4) PostgreSQL
concurrency/recovery/runtime-role evidence plus the supervised real-snapshot
rehearsal. Phase 2 does not migrate Sheet-era character state and does not
create a generic interim state store. The gate closes only when all four
packages and their operational evidence are accepted.

Deliver:

- an offline exporter contract and dry-runnable importer for the immutable
  Foundry active-character snapshot defined in §6.4;
- immutable snapshot provenance, checksum, triggering-actor and audit records;
- stable external mappings;
- validation and reconciliation reports;
- a versioned Foundry field profile classifying snapshot paths, target field
  ownership and current migration state without creating a second editable
  representation;
- repeatable/idempotent imports;
- no writes to Foundry or Google Sheets.

Some target database-authoritative homebrew values exist only in Google Sheets
today. They remain on the accepted legacy path until the package introducing
their typed domain model migrates them. Phase 2 may report their presence or a
Foundry disagreement, but must not copy them into PostgreSQL, make them
selectable for correction, or create a generic migration framework. The
existing Sheets connector remains untouched because the live Freedom bot still
requires it. Existing production writes continue until their package-specific
cutover; "legacy" does not mean globally read-only while the replacement is
absent.

Acceptance:

- every invariant in §6.5 is implemented and enforced below the web/Discord UI;
- the initial `docs/rules/field-ownership.md` profile is exhaustive, versioned,
  reviewed by a maintainer and contains no unclassified supported field;
- no Phase 2 process requires network or live Foundry access;
- the importer verifies the snapshot checksum, triggering authority, world,
  Foundry and system versions, exporter schema, and selected folder identity
  before proposing database changes;
- altered snapshot bytes are treated as a different snapshot and cannot inherit
  another snapshot's identity, preview or audit record;
- all Foundry Actors in `Characters (active)` map or are explicitly unresolved;
- duplicate external IDs, malformed fields, unsupported versions, missing
  Actors and ambiguous mappings are reported;
- repeated imports do not create duplicates;
- import failure cannot partially commit;
- stale or concurrent import previews apply nothing;
- preview and dry-run modes persist no character or mapping changes;
- target database-owned field disagreements are reported without creating or
  changing an editable PostgreSQL value **only when an accepted typed database
  value exists**; otherwise the report records `legacy_authority_deferred` with
  the owning migration package and performs no equality comparison;
- snapshot-only fields remain readable for calculations without becoming a
  second managed representation in PostgreSQL;
- calculations identify the snapshot and field-profile versions they used and
  refuse missing required inputs rather than silently defaulting them;
- an Actor missing from a later snapshot remains intact and mapped until a
  separate Council correction changes that state;
- every applied character and mapping is traceable to the immutable snapshot
  checksum and triggering actor;
- the restricted runtime database role cannot update, delete or truncate audit
  and import-history records;
- rollback/recovery and snapshot-retention procedures are documented;
- a maintainer-supervised rehearsal with the real immutable snapshot produces a
  reviewed reconciliation report without committing the artifact as a fixture;
- real data is not copied into tests.

Mandatory Phase 2 tests:

- valid synthetic snapshot preview and apply creating only snapshot provenance,
  character identity and external mappings;
- checksum mismatch after any byte is changed;
- oversized, excessively nested, unknown-shape and path-bearing input is refused
  before a database transaction begins;
- denial for an ordinary member, acceptance for one Council member, and refusal
  when Council authorization has been revoked;
- wrong world, unsupported Foundry/system version, wrong folder, and unsupported
  exporter schema;
- malformed Actor data, duplicate external Actor ID, duplicate display name,
  missing mapping and ambiguous mapping;
- Actor rename under the same external ID and an Actor absent from a later
  snapshot;
- repeated preview and repeated apply of the same checksum;
- stale preview after a database edit, field-profile change, folder change or
  snapshot change, each committing nothing;
- two concurrent applies of the same or overlapping snapshot cannot duplicate
  characters, mappings, import records or audit effects;
- an Actor missing from a later snapshot warns without deletion, deactivation
  or unmapping;
- already-migrated database-owned fields produce a Foundry-out-of-date warning
  on mismatch and no warning on a match; legacy fields produce
  `legacy_authority_deferred`, name their owning package, and are never reported
  as matching or different without an authoritative comparison value;
- no Phase 2 API, service or repository can persist a Sheet-era field or copy a
  Foundry comparison value into database-managed current state;
- Council and Platform Administrators can read and search import audit records
  while update and delete attempts are denied;
- snapshot-only skill proficiency and Actor-stat inputs are available to roll
  calculations without creating independently editable database fields, and
  the result records its snapshot/profile provenance;
- a required snapshot value that is missing, malformed or unsupported produces
  the defined typed refusal rather than a default value;
- every supported snapshot path and database field has exactly one applicable
  profile/correction classification, and an unknown new path fails closed;
- import tests prove the resulting PostgreSQL dataset contains no generic
  character-state, balance or transaction rows and no second editable copy of a
  legacy Sheet field;
- parser failure, database constraint failure and injected mid-import failure,
  each leaving characters and mappings unchanged, writing no success audit, and
  recording at most one safe attempted/refused audit event;
- injected audit-write failure rolls back the corresponding import;
- direct runtime-role `UPDATE`, `DELETE` and `TRUNCATE` attempts against audit
  and transaction-history tables are rejected by PostgreSQL; and
- database constraints preventing two records from claiming the same
  world/Actor external identity, exercised against PostgreSQL.

Required operational evidence before the gate:

- a signed reconciliation report from a maintainer-supervised preview of the
  real export, accounting for every Actor as mapped, create-candidate or
  explicitly unresolved, with zero unexplained identity discrepancy;
- an upgrade/downgrade/upgrade migration rehearsal against a disposable
  PostgreSQL database;
- a backup and restore rehearsal proving the pre-import state can be restored
  and the importer can be rerun without duplicate identity or audit effects;
- direct restricted-runtime-role denial of `UPDATE`, `DELETE` and `TRUNCATE`
  against every append-only Phase 2 table; and
- independent review closure of every blocking security, identity, atomicity,
  migration and recovery finding.

Review gate: data integrity, identity and migration safety. The Acceptance
Authority records the decision; passing automated tests alone does not close
the gate.

For this gate, “signed reconciliation report” means a dated Data Owner
attestation stored under `docs/review/` that records the export SHA-256, exporter
and profile versions, selected world/folder, total Actors and the count and
identifier of every mapped, create-candidate and explicitly unresolved Actor.
It records the disposition and reason for every unresolved identity and states
that no artifact or real Actor payload was committed. The attestation may use
stable external IDs and counts but no unnecessary player data. The Data Owner's
name and approval date are the signature; the Acceptance Authority references
that attestation in the gate record.

### Phase 3 — Authentication, read-only member portal, and Council administration

Target: 10–18 working days

Planning note: baseline the backend security foundation, Council/import UI,
member read views and production frontend integration as separately estimated
packages. Authentication and server-side authorization contracts precede every
protected production route; frontend integration starts only against accepted
route/view-model contracts. The phase target is revalidated after named backend,
frontend, security, accessibility and review capacity is known.

**Measured constraint on the Council preview route (change-log C-11).** Phase 2's
Rehearsal B previewed a real 32-Actor active folder in **9.57 seconds** — a
16.3 MB artifact, because a real Actor is roughly 0.5 MB of JSON and the folder
will grow. The reconciliation preview therefore **cannot be a synchronous HTTP
handler**: it needs a background job with a polled or streamed result, or a
progressive response. This is a measurement from real data, not an estimate, and
it precedes the route contract rather than being discovered during
implementation. The throughput itself is healthy at 587 ms/MB; the constraint is
about request duration, not about the parser.

#### Phase 3 implementation and review responsibilities

Keep implementation and review responsibilities distinct. The Product Owner and
Technical Lead assign named humans to the accountable roles in §0.3; the tools
below are proposed implementation resources only:

1. **Claude** implements the backend foundation: FastAPI structure, Discord
   OAuth, sessions, server-side authorization, application queries, routes,
   view models, and minimal integration templates sufficient to exercise the
   contracts.
2. **Gemini** implements the production frontend against those accepted route
   and view-model contracts, adapting the approved §12.1 visual prototype into
   Jinja templates, static assets, and appropriately modest HTMX enhancements.
   Gemini does not redesign authentication, authorization, application-service,
   persistence, or API boundaries as part of frontend work.
3. An **Independent Reviewer** may use Codex to review both implementations and
   their integration.
   Review scope includes authentication and authorization boundaries, sessions,
   CSRF, escaping, security headers, route/view-model contracts, Jinja and HTMX
   behaviour, accessibility, responsive behaviour, error and stale states, and
   automated test coverage.
4. The named implementer, using Claude or Gemini according to the ownership
   above, addresses review findings. Cross-boundary findings must be assigned
   explicitly rather than being fixed through an unreviewed contract change.
5. The Independent Reviewer re-reviews all blocking and important findings
   before recommending that the Phase 3 review gate close. The Acceptance
   Authority records the gate decision.

Before Phase 3 begins, prepare coordinated Claude and Gemini prompts from this
section and the accepted §12.1 handoff. Claude's backend contracts should be
stable before Gemini begins production frontend integration. Visual prototype
work may occur earlier under §12.1, but it does not authorize production web
integration.

Deliver:

- Discord OAuth login/logout;
- membership and role verification;
- secure session handling;
- Council character-link management;
- Guild-Council-only offline snapshot import control;
- Platform-Administrator folder selection for snapshot imports, defaulting to
  `/actors/Characters (active)`;
- reviewable field-profile controls showing which snapshot fields are used as
  read-only roll inputs, compared with an already-migrated database authority,
  deferred to a named legacy migration package, or ignored;
- Council-and-administrator-visible immutable snapshot-import and
  reconciliation audit log;
- integrate the accepted Freedom Blades visual baseline from §12.1 into
  production Jinja templates and static assets;
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
- ordinary members cannot see or call the snapshot import control;
- one authorized Council member can trigger an import without a second approval;
- Platform Administrator alone cannot apply an import unless that user also has
  Guild Council authority;
- the Council confirmation shows the checksum, world, selected folder, Actor
  count, mappings and warnings; Phase 3 import cannot select or write an
  unmigrated Sheet-era field;
- no Phase 3 route or form mutates character game state; correction controls are
  delivered by the typed package that owns the field and its cutover;
- legacy fields display `migration deferred` and their owning package rather
  than a fabricated comparison or correction control;
- Council members can search import and reconciliation audit records but cannot
  modify or delete them;
- snapshot import attempts and results are visible in the administrator audit
  view without exposing snapshot contents to unauthorized users;
- production templates preserve the accepted responsive and accessibility
  baseline without importing or serving `design-prototype/`; and
- security tests cover common authorization failures.

Mandatory Phase 3 tests:

- unauthenticated, non-member, ordinary-member, Council and
  Platform-Administrator-only access for every import, profile and
  audit endpoint, checking direct HTTP calls as well as hidden controls;
- Council role or guild membership revoked between preview and apply;
- CSRF refusal, request/file-size limits, unsupported content type, malicious
  filename, escaped Actor/warning text and unauthorized raw-snapshot download;
- an administrator folder/profile change invalidates an existing Council
  preview, and Council confirmation displays the exact changed scope before a
  new apply;
- double-click, retry and two-browser concurrent apply return one result and one
  audit effect;
- cross-character identifier substitution cannot read another record outside
  the requested Council operation;
- direct HTTP and application-service tests prove no character-game-state
  correction endpoint exists and forged submissions cannot mutate legacy or
  database state;
- every legacy field renders `migration deferred` plus the package named in the
  controlled migration register, with no editable control;
- Council and administrator can search audit records with bounded pagination;
  ordinary users and unrelated service principals cannot read them;
- no application route or repository operation can update/delete an audit
  record, and attempted direct runtime-role mutation is rejected; and
- audit rendering excludes raw snapshot bytes, secrets and unsafe exception
  detail while retaining actor, action, source, time, reason, correlation ID and
  before/after facts.

Review gate: authentication, authorization, and web security.

### Phase 4 — Shared application services

Target: 5–10 working days

Deliver:

- framework-free money and resource domain objects;
- application command interfaces and query-boundary conventions, introducing
  concrete protocols only where this phase has a real consumer;
- transaction ledger;
- typed errors;
- idempotent command execution;
- characterization tests for Sheet-era behavior;
- application boundaries exercised by the Phase 4 ledger and idempotent command
  execution work; no speculative money/resource query or temporary Sheet
  adapter is created without its Phase 5.2 character-page consumer.

Acceptance:

- domain imports no infrastructure frameworks;
- money uses integer copper;
- duplicate mutations are safe;
- concurrent stale updates are detected;
- tests characterize intended current behavior;
- command/query and repository protocols introduced in Phase 4 have a concrete
  Phase 4 consumer; the wallet read query and its first production adapter are
  deferred to package 5.2, where the character page consumes them.

Review gate: dependency direction and domain correctness.

### Phase 5 — Existing automation migration

Target: umbrella programme increment; the former 10–15 working-day range is
withdrawn because it did not represent the scheduled jobs, catalogue,
inventory, nine feature migrations, reviews or cutovers. Each package below is
estimated and baselined separately when it meets the management definition of
ready.

#### Phase 5 work packages and gates

| Package | Outcome | Package-specific predecessor | Gate |
|---|---|---|---|
| 5.0 Migration and cutover harness | feature flags, comparison telemetry, idempotency/audit conventions and common rollback procedure | Phase 4 gate | first-mutation and cutover-control review |
| 5.1 Character profile and `/info` | typed character/profile/proficiency schema; package-owned Sheet migration and reconciliation; database-backed read path with linked-character authorization | Phase 3 authentication/security gate, 5.0, OD-16/17 resolved | profile-migration and read-path authorization review |
| 5.2 Wallet, character-page wallet view and `/xchange` | typed wallet/ledger schema; package-owned balance migration and reconciliation; wallet query plus production repository adapter introduced with the character page as their first real consumer; atomic, idempotent currency exchange | 5.0 | first economy-migration/mutation and wallet-read-path review |
| 5.3 Lifestyle and scheduled accrual | typed lifestyle schema; package-owned migration and reconciliation; interactive behavior, Living Cost schedule/history/job, catch-up, monitoring and authority cutover | 5.0; OD-03/04 closed; effective-dated activation history | scheduled-economy and cutover review |
| 5.4 Mining and work | characterized deterministic rules and atomic ledger effects | 5.0 and rule decisions | rules/economy review |
| 5.5 Learning | typed learning/downtime/proficiency projects; package-owned Sheet migration including accountable decomposition of column V; prerequisites, progress and corrections | 5.0; OD-09 and OD-28 closed | learning migration/rules review |
| 5.6a Catalogue and inventory foundation | pinned catalogue import, definitions/revisions, inventory and transactions; package-owned magic-item migration and reconciliation | Phase 4; source/licensing approval | catalogue, migration and inventory-integrity review |
| 5.6b Crafting | typed crafting/CRP projects; package-owned migration, including the crafting portion handed off from column V; atomic completion against recognized definitions | 5.6a; OD-05 closed | crafting migration/rules and atomicity review |
| 5.7 Sales | authorized atomic sale and ledger flow | 5.0, 5.6a where items are sold, OD-39 closed | authorization and financial-integrity review |
| 5.8 Trades | authorized multi-character atomic trade and inventory transfer | 5.0, 5.6a, OD-39 closed | multi-actor atomicity review |
| 5.9 Existing Bastion maintenance | typed existing Bastion state; package-owned Sheet migration/reconciliation; maintenance behavior and history | relevant lifestyle/resource packages | Bastion migration review; does not replace Phase 10 gate |
| 5.10 Phase 5 bot-behavior cutover | reconciled cutover of Phase 5-approved bot behaviors and verification window; Sheet rollback retained for those behaviors | every Phase 5 package in the approved cutover scope | Phase 5 bot-behavior cutover review; does not authorize final Sheet retirement |

Each package receives its own phase-plan record containing scope exclusions,
work breakdown, three-point estimate, capacity, dependency owners, test mapping,
rehearsal/cutover steps and contingency. A package may cut over only its own
accepted behavior. Completion of one package does not imply completion of the
Phase 5 umbrella or authorize a dependent package.

The controlled allocation of every legacy character and player field is in
[`docs/project-management/data-migration-register.md`](project-management/data-migration-register.md).
No package is ready if one of its allocated rows lacks an exact source, typed
target, transformation owner, reconciliation rule or gate. A register row may
move between packages only through §0.2 change control; it may never have two
write-authoritative targets.

Controlled vocabulary sources and stewardship are recorded in
[`docs/project-management/data-vocabulary-register.md`](project-management/data-vocabulary-register.md).
A package using a vocabulary is not ready while its source identity, version,
alias/merge policy, licensing/provenance, retirement behavior, steward or
unresolved-value workflow is open.

A migration package may not invent the events behind a legacy aggregate or
date. Where the Sheet supplies only a counter, balance or latest date, migrate
it as a typed, immutable opening/baseline fact with source, effective cutover
instant and provenance. Normalized event history begins at cutover. A later
aggregate may combine the accepted baseline and post-cutover history only by a
documented deterministic rule. Historical event rows are created only from
independently identifiable source records; no synthetic mission, attendance,
campaign or project is manufactured to make a counter appear relational.

No field may move from `Legacy` or `Shadow` to `Database` until its assigned
correction workflow is accepted: current authorization is enforced; standard,
protected or compensating semantics match the field profile; protected changes
show dependent effects; history-backed changes append rather than rewrite;
successful and refused attempts are safely audited; and stale/concurrent and
runtime-role bypass tests pass. The owning package delivers this workflow even
if a later phase adds a consolidated correction UI.

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

#### Phase 5 scheduled economy jobs

The lifestyle migration includes the existing weekly Living Cost accrual, not
only the interactive lifestyle command. The platform must replace the active
Sheet macro with a timer-triggered application job that increments each
eligible character's Living Cost weeks owed by **1 on a configured weekday and
time**. The initial migrated setting is **Sunday at 04:00**, matching the legacy
automation. The authoritative timezone is the IANA zone **`Europe/Berlin`**
(CET/CEST); it is not configurable and must not be replaced with a fixed `CET`
offset or inferred from the deployment host. A currently authorized Platform
Administrator can change the weekday and local time without editing code,
direct SQL or the host timer. Guild Council membership alone does not grant
this configuration permission.

Store an immutable history of schedule revisions in PostgreSQL: weekday, local
time, fixed `Europe/Berlin` timezone, effective instant, authorizing Platform
Administrator, reason and creation time. Exactly one revision is effective for
any instant. A schedule change is a validated, audited application command,
not an update that erases the previous schedule. It cannot be backdated and
needs no minimum lead time.
It is refused while any accrual period under the current or an earlier revision
is overdue or failed; the Administrator must first run or recover catch-up until
the backlog is empty. This keeps a schedule change from obscuring which
revision owns an unapplied period.

The last successful accrual remains the anchor when a revision changes: the
first occurrence of the new weekday/time after confirmation is recorded as a
non-accruing transition occurrence, and the following weekly occurrence is the
first one that increments Living Cost. This deliberate skipped transition
prevents a schedule edit from charging another week merely because the new day
is close to the old one. It is not a missed period and catch-up must never apply
it later.

Before confirmation, preview the last successful accrual, the proposed
effective instant, the non-accruing transition occurrence, the first accruing
occurrence, at least the next four accruing occurrences, the elapsed time
between the last and first new accrual, `Europe/Berlin` and UTC representations,
applicable DST effects, the projected eligible-character count and confirmation
that the backlog is empty. The confirmation must state plainly that the first
occurrence under the changed schedule will not increment Living Cost.

An accrual period is identified by the immutable schedule-revision ID and the
nominal local occurrence date/time, not by the process start time. Persist a
database uniqueness constraint on that identity. This gives exactly-once
**effects**, not an unrealistic promise that a distributed timer executes only
once. Store the actual start/completion instants and status separately from the
period identity.

Daylight-saving behavior is deterministic: if a configured wall time does not
exist during a forward clock change, that period becomes due at the first valid
instant after the gap; if it occurs twice during a backward clock change, it is
due once at the earlier occurrence. The preview must disclose an affected next
occurrence. Time calculations use timezone-aware values and an injected clock;
neither application code nor tests may depend on the host timezone.

Changing the business schedule must not require regenerating the outer timer.
The timer wakes at a fixed safe interval, invokes the application entry point,
and the application decides from PostgreSQL state which periods are due. A late
invocation catches up every unapplied occurrence in chronological order. Catch-
up is bounded per invocation for operational safety and repeats until current;
it never collapses several missed weeks into one period or silently drops them.

The timer is an outer operational trigger, not the owner of the rule. It invokes
the same deterministic application use case used for supervised replay, while
PostgreSQL owns the resulting state, transaction, idempotency record and audit
history. Prefer a repository-managed systemd timer in the existing deployment
topology unless a separately reviewed decision approves a database scheduler.

The job must:

- use a stable accrual-period key so retries, restarts and concurrent timer
  invocations cannot add the same week's Living Cost twice;
- bind each accrual period to the effective schedule revision so a schedule
  change cannot rename an already applied period or make it due twice;
- resolve and persist the eligible-character set as it existed at the nominal
  accrual instant from append-only or effective-dated character activation
  history; only characters active at that instant accrue Living Cost, even when
  the period is applied later during catch-up, and characters inactive then
  receive neither an increment nor a per-character accrual record;
- catch up every missed occurrence chronologically, in bounded batches, without
  silently skipping, merging or duplicating a week;
- apply the complete run transactionally, with concurrency protection and a
  database-enforced unique period claim; two workers may attempt a period, but
  only one may change balances or produce its success audit effects;
- make one period atomic across its eligible population and audit writes: a
  failure cannot leave only some characters incremented or claim success;
- append a run-level audit record and per-character before/after facts
  identifying the schedule revision, nominal period, system actor and
  correlation ID;
- support a supervised, idempotent manual replay through the application use
  case and the same period identity rather than direct SQL;
- require current Platform Administrator authorization, CSRF protection and an
  optimistic schedule revision on preview/apply of a schedule change; and
- expose failure, backlog depth, last successful period and next due period
  through the normal operational health/monitoring path without player data.

Per OD-36, keep the Sheet macro authoritative only while the legacy Sheet-backed
behavior remains live and this replacement is built and reconciled. At the
approved cutover, PostgreSQL becomes the sole authority and every database-
backed Living Cost path must stop reading or reconciling column J. After that
boundary, a Sheet macro may still alter the retired Sheet but cannot affect,
overwrite or be imported into PostgreSQL. Disabling the obsolete macro remains
recommended operational cleanup, not a correctness dependency of the database
job. The cutover instant is also the beginning of platform accrual history:
bootstrap the then-current active state at that instant and never synthesize or
catch up platform periods before it. Later activation/deactivation changes must
be effective-dated and audited so delayed jobs can reconstruct eligibility at
their nominal occurrence. Frank's scheduled interest accrual follows the same
timer/application-service, idempotency, audit and authority-cutover requirements
when that economy field is migrated.

Before migrating crafting, implement the versioned magic-item catalogue,
source-publication allowlist, catalogue preview/import workflow, character
inventory and inventory transaction model from §7.4. The initial reviewed
catalogue enables all publications referenced by core 5e.tools item data while
excluding its homebrew and prerelease collections. It includes all magic-item
categories and consumables.

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
- Sheet rollback path exists during verification;
- the Living Cost job accrues exactly one week for each eligible character for
  each configured weekly period, initially Sunday 04:00 in `Europe/Berlin`;
- eligibility is evaluated at each nominal occurrence from effective-dated
  activation history: characters inactive then never accrue, while characters
  active then still accrue if that period is applied later during catch-up;
- a currently authorized Platform Administrator can preview and change the
  weekday and local time; Guild Council-only, ordinary and unauthenticated
  callers, direct SQL and host-timer changes cannot change the business
  schedule, and the timezone remains `Europe/Berlin`;
- after a schedule change, the first new scheduled occurrence is durably
  recorded as non-accruing and the following weekly occurrence is the first to
  increment; retry, restart, replay and catch-up cannot turn the transition
  occurrence into an accrual;
- schedule history is immutable and auditable; a change cannot be backdated,
  overwrite history, duplicate a boundary period or discard a period already
  due under the preceding revision;
- a schedule change is refused whenever any prior period is overdue or failed
  and succeeds only after catch-up leaves an empty backlog;
- a database uniqueness constraint guarantees one successful effect per
  schedule revision and nominal local occurrence, including retries, restarts,
  concurrent workers and supervised replay;
- every missed weekly occurrence is caught up once in chronological order after
  downtime, using bounded batches until the backlog is empty;
- each period is atomic across all eligible characters and its audit facts, and
  monitoring exposes last success, next due period, backlog and safe failure;
- nonexistent and ambiguous daylight-saving wall times follow the specified
  first-valid and earlier-occurrence rules and still produce exactly one period;
- after authority cutover, no Sheet value or macro execution can change or be
  imported into database Living Cost state;
- crafting cannot accept a free-text or unknown item; it references an enabled,
  recognized catalogue definition and separately enforces craftability;
- a completed craft atomically records the owned item or quantity, inventory
  transaction, resource changes and audit event;
- catalogue refreshes are previewed, versioned, transactional and cannot delete
  definitions referenced by character inventory or history; and
- disabling a publication prevents new crafting from it without altering items
  characters already own.

Mandatory scheduled-job tests:

- the initial Sunday 04:00 boundary and representative changed weekday/time
  schedules in `Europe/Berlin`, including applicable daylight-saving
  transitions;
- Platform Administrator authorization, validation, audit history, complete
  transition preview, empty-backlog precondition and effective-time behavior
  for schedule changes;
- unauthenticated, ordinary, Guild Council-only and revoked-Administrator
  callers, stale schedule revision, CSRF failure, invalid weekday/time and
  attempted backdating, each applying nothing;
- changing a schedule before, exactly at and after a due boundary, proving the
  old/new revision ownership of every period and the non-accruing first new
  occurrence without duplication or later catch-up;
- preview content showing the last accrual, transition occurrence, first and
  next four accruals, elapsed interval, Berlin and UTC times, DST effect,
  eligible count, backlog and an explicit no-accrual warning;
- characters activated or deactivated between a missed period and its delayed
  catch-up, proving eligibility comes from effective-dated state at the nominal
  occurrence rather than current state;
- initial cutover proving no platform period before the cutover instant is
  synthesized or caught up;
- retry, duplicate delivery, process restart and two concurrent invocations for
  the same accrual period, with the database uniqueness constraint exercised
  against PostgreSQL rather than only mocked;
- one, multiple and more-than-one-batch missed periods, proving chronological
  catch-up and eventual empty backlog;
- a forward DST gap and backward DST fold, each producing exactly one effect at
  the specified instant independently of the host timezone;
- injected mid-run database and audit failures, each leaving the population
  unchanged and recording no false success;
- a character becoming active or inactive immediately before and after a
  nominal occurrence, including when the job transaction runs later;
- supervised replay using the same period key and application use case;
- monitoring state for never-run, healthy, overdue, backlogged and failed jobs,
  without names, balances or exception detail;
- schedule changes with overdue, failed and multi-period backlogs, refused until
  recovery/catch-up completes and then accepted against an empty backlog; and
- post-cutover attempts to import or reconcile Sheet column J, proving the
  retired Sheet and any surviving macro cannot affect database Living Cost.

Review gates: the package gates above, including first mutation, scheduled
economy, catalogue/inventory, trade atomicity, crafting/learning rules, and final
bot cutover. Each decision follows §0 and
`docs/project-management/README.md`; the umbrella closes only after all packages
in the approved Phase 5 scope are accepted.

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

Target: not in the committed release baseline. Estimate only after a separate
privacy, retention, provider and cost decision and after Phase 9 is accepted.

Deliver:

- report-draft interface;
- explicit human review;
- proposed entity/loot extraction;
- provenance and AI-use disclosure;
- retention and privacy policy;
- provider abstraction.

AI output cannot mutate game state. Voice recording remains a separate future
decision requiring explicit consent, privacy review, and deletion guarantees.

Acceptance:

- the feature is disabled by default and can be removed without affecting
  manual reporting or settlement;
- provider, data location, retention, cost limit and failure behavior are
  approved and documented before any non-synthetic data is sent;
- authorization and data minimization are enforced server-side;
- every output is visibly a draft with provenance and requires explicit human
  review;
- deterministic validation and Council approval remain the only paths to game
  state;
- provider outage, timeout, malformed output and duplicate request cannot lose
  a manual draft or apply a mutation;
- tests use synthetic content and no production report or credential; and
- privacy, security, accessibility and operations reviewers recommend approval.

Review gate: optional-feature value, privacy, security, cost and operational
readiness. The Acceptance Authority must add Phase 12 to a release baseline
before production use.

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
- malformed or tampered Foundry snapshot;
- migration failure and recovery;
- mission settlement affecting multiple characters;
- correction after approval;
- attendance reconnect and late join;
- unsupported Foundry version;
- pinned catalogue snapshot and checksum verification;
- idempotent catalogue re-import and stale/concurrent preview refusal;
- malformed, duplicate, removed, renamed and ambiguous upstream item records;
- source disablement with retained historical inventory;
- unique-item transfer and concurrent consumable use;
- stale crafting project after definition, source or policy change; and
- atomic craft completion across inventory, resources, ledger and audit.

Tests must never contact production Discord, Sheets, Foundry, or PostgreSQL.

Every package that creates, migrates or mutates persistent state must add a
package-specific matrix covering, where the condition is meaningful:

- valid preview/apply and deterministic before/after facts;
- unauthenticated, unauthorized, cross-object and revoked-role denial;
- invalid, boundary, negative, oversized and unknown input;
- duplicate request, retry, stale optimistic version and two concurrent actors;
- database uniqueness, foreign-key, check and append-only enforcement against
  PostgreSQL, not only fakes;
- parser/external, mid-transaction, audit-write and commit failure, proving no
  partial state and no false success;
- migration dry-run, idempotent rerun, every source row/value accounted for,
  explicit unresolved records, rollback and restored-backup rerun;
- application and database runtime-role attempts to bypass history or
  authorization;
- safe monitoring states and logs without secrets or unrelated player data; and
- a synthetic staging end-to-end path plus the named supervised operational
  checks required by the package gate.

A package plan may mark an item `not applicable` only with a written rationale
accepted by its Independent Reviewer. It may not omit the row. Phases 6–11 and
every Phase 5 migration package must trace this matrix to named tests before
their definition of ready is accepted.

### 13.3 Review-gate evidence

A phase with data import or Council mutation cannot close on unit tests alone.
Its handoff must include the common evidence below plus boundary-specific
evidence for every surface it actually exposes:

- a traceability table mapping every acceptance criterion and mandatory scenario
  to one or more named automated tests or to a clearly identified supervised
  operational check;
- unit and application tests for parsing, field policy, authorization,
  reconciliation and typed failures;
- repository/contract tests proving the same transaction and audit behavior for
  fakes and the PostgreSQL adapter;
- PostgreSQL integration tests for migrations, uniqueness, foreign keys,
  optimistic concurrency, idempotency, rollback and runtime-role audit
  immutability;
- web surfaces: authentication, current-role authorization, CSRF, object-level
  authorization, input limits, escaping and stale-submission tests;
- Discord surfaces: interaction authorization, object ownership, defer/followup
  behavior, duplicate interaction and safe-rendering tests;
- CLI/operator surfaces: filesystem and artifact limits, authority, refusal,
  exit-code, safe-output and non-interactive recovery tests;
- database mutations: real PostgreSQL transaction, constraint, concurrent
  outcome, restricted-role and recovery evidence;
- deterministic synthetic snapshot fixtures covering the supported schema
  without real character data;
- the narrow relevant suite followed by the full configured suite, with exact
  commands and results reported;
- configured formatter, linter, type checker, migration consistency and
  `compileall` checks, or an explicit statement that a check is not configured;
- diff review for secrets, raw snapshots, unsafe logs and accidental production
  data; and
- recovery documentation exercised against a disposable environment whenever
  the phase introduces a new persistent mutation.

Skipped tests, mocks and synthetic fixtures must be reported accurately. A test
that only asserts a mocked method call does not prove a PostgreSQL constraint,
transaction boundary, role permission or concurrent outcome.

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
- the legacy Sheet-backed bot remains available through the defined cutover and
  rollback window.

Applied migrations are never edited. Roll forward or create a documented
recovery migration.

## 15. Legacy runtime retirement

This section governs the retirement of both legacy runtimes: the Google Sheet
that holds legacy state, and the Freedom bot that reads and writes it. They are
retired separately, in that order, under separate gates.

### 15.1 Google Sheets retirement

Google Sheets is a temporary runtime dependency and the accepted legacy store
for fields whose typed PostgreSQL package has not passed its migration/cutover
gate. Character identity and snapshot-only Actor data come from Foundry. Do not
copy Sheet-era state into a generic interim database representation or build a
general synchronization framework around Google Sheets.

Use these retirement stages:

1. characterize the existing Sheet-backed bot behavior that must be preserved;
2. import active characters from Foundry into PostgreSQL;
3. for each field group, implement its typed domain model, constraints,
   application service and package-specific migration;
4. preview the migration, reconcile every source row/value, and obtain Data
   Owner approval for all mappings and explicit unresolved exceptions;
5. exercise migration rollback and database backup restoration, then apply the
   migration atomically with immutable provenance and audit;
6. compare database-backed behavior against characterized legacy behavior;
7. cut that field group's reads and writes over behind controlled feature flags;
8. verify the Manager and bot operate correctly without that Sheet-backed path
   for **four weeks** after each approved field-group cutover;
9. retain the Sheet connector, credential, source export and rollback path
   throughout that verification window;
10. after every field-group gate and explicit maintainer approval, archive the Sheet and remove the
   service-account credential, connector, and obsolete Sheet-backed code.

Do not introduce dual writes between PostgreSQL and Google Sheets. Each package
must publish: exact source columns, target tables and constraints; deterministic
transformation rules; row/value reconciliation totals; idempotency keys;
transaction boundaries and injected-failure tests; authorization and audit
tests; backup, restore and application rollback steps; cutover flags; monitoring
and rollback thresholds; and the time-bounded verification period. PostgreSQL
is authoritative only after that package's approved cutover; the Sheet-backed
path is then a frozen, read-only rollback implementation during the four-week
verification period, not a secondary authority. There is no live
PostgreSQL-to-Sheet diagnostic projection.

For every authoritative multi-valued source, the package plan and migration report must also
publish the reference, parent and junction/child tables; all foreign keys,
primary/unique keys and delete behavior; vocabulary resolution and explicit
unresolved-value handling; duplicate and ordering semantics; and source-entry
to target-row control totals. Acceptance requires PostgreSQL tests proving
foreign-key rejection, duplicate prevention, parent/history delete behavior and
lossless idempotent migration. Serialized storage of authoritative
multi-valued domain facts is a blocking schema finding. Reviewers must not apply
that finding merely because an immutable evidence, audit, diagnostic, external
payload or disposable-cache record contains bounded structured context; they
must instead verify that the record fits the exceptions and cannot act as
operational authority.

The allocation, status and accountable migration package for every legacy field
are controlled in
[`docs/project-management/data-migration-register.md`](project-management/data-migration-register.md).
Its machine-readable source is
[`docs/project-management/data-migration-manifest.json`](project-management/data-migration-manifest.json).
Automated checks require every inventoried character/player source and every
profile field to have exactly one accountable disposition and a known package.
The Data Owner verifies the manifest against the real headers before every
migration-package baseline and before Sheet retirement.

Phase 5.10 cuts over only the bot behaviors accepted within Phase 5. Final Sheet
retirement is a separate gate and cannot occur while any manifest/register row
is `Legacy`, `Shadow`, unexplained or allocated to an unaccepted later package,
including Phase 8. No milestone name or partial bot cutover implies otherwise.

### 15.2 Freedom bot retirement

**Baseline v1.7, 2026-08-28.** The Freedom bot is retired once the platform is
fully functional, and not before. It exists to give players access to state held
in a Google Sheet; a platform that holds that state and offers those actions
directly makes it unnecessary, and keeping it would preserve exactly the manual
steps the platform is built to remove.

**The governing condition is the platform's functionality, not the calendar and
not the progress of this roadmap.** The bot must not be deleted, disabled or
degraded for as long as the platform is not fully functional — stages 1 to 4
below are what "fully functional" means, and every one of them must hold.
Retirement is a **terminal gate**, not a milestone side effect.

**Discord and the Freedom bot are two different things, and only one of them is
in scope here.** Discord is the Freedom Blades community's server and the basis
of the whole project; it is never retired. The Freedom bot is this repository's
Python/Pycord application, a *client* of Discord. Retiring it removes a client
and removes nothing from Discord.

What is retired is the **Freedom bot**: its slash commands, its cogs, its
Sheet-backed models and helpers, and the Discord application scopes and
credentials that only those commands need. **Discord is not retired with it.**
Discord OAuth remains the platform's authentication; Discord remains the source
of guild membership, role verification, events, notifications and voice-state
attendance evidence. Any Discord-side presence those still require is a narrow,
platform-owned adapter owned and gated by the package that needs it. The
attendance package is the one to size deliberately: voice-state join/leave
requires a live gateway connection, so "no bot" cannot be assumed to mean "no
gateway process" until that package has decided how attendance evidence is
collected.

Use these retirement stages:

1. every player-facing behavior the bot provides exists on the platform and has
   passed its owning package gate — Phase 5.1–5.9 for the migrated commands,
   Phase 6 for the approvals that replace manual confirmation steps, and Phases
   8–11 for behaviors those phases own;
2. §15.1's final Sheet retirement gate has closed, so no bot path is anyone's
   rollback route;
3. a dual-availability period in which both interfaces work and the platform is
   authoritative, with a numeric duration set by the retirement package plan;
4. **measured adoption evidence** against a threshold accepted in advance by the
   Product Owner — a stated proportion of active players having used the
   platform for the behaviors that replaced their commands. "Everyone has moved
   over" is a gate criterion and therefore needs a number, not an impression;
5. announcement to the community with a numeric notice period;
6. **deregistration before deletion**: the slash commands are removed from the
   Discord application while the code still exists, so the rollback is
   re-registration rather than a redeploy;
7. a verification window with the bot's code retained but inert;
8. deletion of the command cogs, the Sheets connector, the Sheet-backed models
   and helpers made dead by the migration, and revocation of the credentials and
   scopes no longer required; and
9. a documented statement of what Discord-side presence remains, which package
   owns it, and which process runs it.

Retirement **cannot** occur while any row in the migration register or manifest
is `Legacy`, `Shadow`, unexplained or allocated to an unaccepted package; while
any command behavior lacks an accepted platform equivalent; or before §15.1's
final Sheet retirement gate. Until every stage above holds, the bot must not be
deleted, **disabled or degraded** — `.agents/AGENTS.md` states this as the
governing condition — and no milestone name, partial cutover or passing test
suite advances this gate on its own. An agent that believes the platform is
finished is not evidence that it is.

Gate: bot-retirement review. Required recommendations from the Product Owner,
Technical Lead, Operations Owner and an Independent Reviewer; approval by the
Acceptance Authority.

## 16. Claude Code working protocol

Agents that support skills carry parts of this protocol as procedures under
`.claude/skills/`: `handoff-checklist` for §16.3, `run-suites` for the
testing procedure, `migration-staging` for schema work and `rules-sourcing`
for game-rule changes. They cite this section and `.agents/AGENTS.md` rather
than restating them, and no always-applicable rule is held only in a skill.
Two `PreToolUse` guards under `.claude/hooks/` enforce the secrets rule and
refuse Git history rewrites. This protocol binds every agent regardless.

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

The canonical `docs/review/Handover information` contains only the active
assignment, its controlling restrictions, the immediate handoff and archive
links. Consumed and superseded blocks move verbatim to dated snapshots beside
the canonical file, preserving their original relative-link base, and are
indexed under `docs/review/handover-archive/`; dedicated handbacks and reviews
remain the durable records. Agents update the current entry point rather than
appending an unbounded history to it.

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

## 17. Decision governance

The authoritative OD-01–OD-40 record is
`docs/discovery/open-decisions.md`; the actionable management index is
`docs/project-management/decision-register.md`. The decisions originally
required before Phase 1 completion are recorded there, and the closed Phase 0
decisions remain valid unless superseded through §0.2 change control.

Before baselining any phase or package, the Delivery Lead verifies that every
decision marked as blocking it is closed. Each open decision must have an
accountable role, required-by milestone and management action. A deadline is
added when a calendar forecast is established. If it is not resolved by the
package's ready date, that package remains `not ready`; implementation does not
choose policy by default.

At minimum, decisions that govern authorization, field/data ownership,
privacy/retention, game rules, production topology, migration authority,
cutover or rollback require Product Owner recommendation and Acceptance
Authority approval. Specialist recommendations from the Security Reviewer,
Data Owner or Operations Owner are required where their area is affected.

## 18. Initial release definition

The first releasable version contains:

- PostgreSQL and migrations;
- Discord OAuth;
- guild and Council-role verification;
- Council-managed multi-character links;
- imported active Foundry characters;
- read-only Foundry/database reconciliation;
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

It does not include music.

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

**Current action, 2026-10-01 — D2-R2 design accepted; prepare a separate
M-14/I-7 implementation assignment before any implementation.**

Peter Duscha accepted `C-P5.0-R5-RP11-I1-R3-R4-D2-R2` after Codex's
independent review found no new Blocking or Important issue
([amended proposal](review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md),
[handback](review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r2-zero-ret-decoding-remediation-handback.md),
[acceptance](review/project-review-2026-10-01-p5-r5-rp11-r4-d2-r2-acceptance.md)).
The zero-`ret` image is the selected design, with no `call` and no `ret`. An
independently implemented decoder, XD, must decode `.text` from the image
bytes and agree exactly with the committed listing before any T-L10 result
is accepted. LD-8's conditions are normative. `R4-D2-R1-1` is Closed as
remediated at the design level. LD-9 option (i) requires Codex to independently
decode the actual `.text` at D9-2 using its own decoder or byte-by-byte manual
derivation prepared without reading XD's table; exercising XD alone is not
sufficient.

No implementation, compilation, source, decoder, build, dependency, binary,
manifest, artifact, configuration, host, wiring or operational authority
exists. PO-9 and PO-14 remain open; RP-11 remains unwired and unmet;
P5.0-R5 remains Blocking; `plan.is_executable=False`; Package 5.0 remains not
ready. A separate M-14/I-7 assignment is required before implementation.

**Superseded current action, 2026-09-30 — Claude performs the documentation-only D2-R2
zero-`ret` and independent-decoding remediation; Codex then re-reviews.**

Peter Duscha accepted Codex's D2-R1 recommendations. LD-7 requires FA-2's
zero-`ret` image from the first build. LD-8 accepts the bound build root plus
HA-1 … HA-5 provided IC-1 passes, R-5 actually varies and records at least one
of HA-1 … HA-3, and unexplained differences stop. Diverse double compilation
is not required for PO-9.

The original three D2 findings are remediated as framed. New Blocking finding
`R4-D2-R1-1` remains Open because T-L7 and T-L10 consume the pinned
disassembler's instruction boundaries without independently decoding `.text`.
Claude is assigned a bounded documentation-only D2-R2 amendment; Codex
independently re-reviews before Peter decides.
([decision](review/project-review-2026-09-30-p5-r5-rp11-r4-d2-r1-decisions.md),
[assignment](review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r2-zero-ret-decoding-remediation-claude-prompt.md)).

No implementation, compilation, source, decoder, build, dependency, binary,
manifest, artifact, configuration, host, wiring or operational authority
exists. PO-9 and PO-14 remain open; RP-11 remains unwired and unmet;
P5.0-R5 remains Blocking; `plan.is_executable=False`; Package 5.0 remains not
ready.

**Superseded current action, 2026-09-29 — Codex independently re-reviews the returned
D2-R1 static-launcher design remediation; Peter Duscha then decides.**

Codex's review of the D2 design found three findings:

* `R4-D2-1` (Blocking): PO-9's control-flow premise ignored `ret`;
* `R4-D2-2` (Important): the build-input closure omitted `/bin/sh`, `env`
  and runtime inputs; and
* `R4-D2-3` (Important): hostile vectors could exceed `execve` limits, and
  HX-5 omitted the normative diagnostic.

Claude returned `C-P5.0-R5-RP11-I1-R3-R4-D2-R1` documentation-only and
stopped
([assignment](review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r1-static-launcher-design-remediation-claude-prompt.md),
[amended proposal](review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md),
[handback](review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r1-static-launcher-design-remediation-handback.md)).
D-S1 is retained under three new elements:

* a closed control-transfer and return-integrity discipline, checked by a
  listing verifier and human review, with named fail-closed alternatives;
* a build root bound file by file, with named residual host inputs; and
* bounded hostile vectors with exact expected traces.

No finding is claimed closed.

No implementation, compilation, source, build, dependency, binary, manifest,
artifact, configuration, host, wiring or operational authority exists. PO-9
and PO-14 remain open; RP-11 remains unwired and unmet; P5.0-R5 remains
Blocking; `plan.is_executable=False`; Package 5.0 remains not ready.

**Superseded current action, 2026-09-29 — Codex independently reviews the returned LB-2S
static-launcher design; Peter Duscha then decides.**

Claude returned `C-P5.0-R5-RP11-I1-R3-R4-D2` documentation-only and stopped
([proposal](review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md),
[handback](review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-handback.md)).
It selects `D-S1`, a freestanding, syscall-only C image with no C library, and
specifies its PO-9 proof, reproducible build, exact launcher contract, binding,
tests and rollback. PO-9 is not discharged: that needs build, inspection,
reproducibility and installation evidence under later authority.

No implementation, compilation, source, build, dependency, binary, manifest,
artifact, configuration, host, wiring or operational authority exists. PO-9
and PO-14 remain open; RP-11 remains unwired and unmet; P5.0-R5 remains
Blocking; `plan.is_executable=False`; Package 5.0 remains not ready.

**Superseded current action, 2026-09-29 — Claude produces the documentation-only LB-2S
static-launcher design; Codex then reviews independently.**

Peter Duscha accepted M-14 for a design pass, conditionally selected LB-2S
under M-9 subject to an accepted design and later PO-9/PO-14 discharge, and
kept T-A in scope under M-10 while explicitly trusting reviewed root-controlled
manager execution settings under R-10. T-B remains out of scope.

Claude is assigned `C-P5.0-R5-RP11-I1-R3-R4-D2` to design the runtime,
toolchain, reproducible build, exact launcher contract, evidence and rollback,
then stop for Codex review.
([decision](review/project-review-2026-09-29-p5-r5-rp11-r4-d1-r2-launch-boundary-decision.md),
[assignment](review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-claude-prompt.md)).

No implementation, compilation, source, build, dependency, binary, manifest,
artifact, configuration, host, wiring or operational authority exists. PO-9
and PO-14 remain open; RP-11 remains unwired and unmet; P5.0-R5 remains
Blocking; `plan.is_executable=False`; Package 5.0 remains not ready.

**Superseded current action, 2026-09-29 — Peter Duscha decides the post-R4-D1-R2 design
direction.**

Codex reviewed `C-P5.0-R5-RP11-I1-R3-R4-D1-R2` with no Blocking, Important or
Optional finding. `R4-D1-R1-1` is remediated at design-document level. The
original LB-2 prevention claim is withdrawn; LB-2S is only a conditional
direction requiring M-9, M-14, M-10, a separate static-launcher design and
load-bearing PO-9/PO-14. **No recommendation is ready.** Peter Duscha decides
whether to commission that design or choose another bounded direction.
([review](review/project-review-2026-09-29-p5-r5-rp11-r4-d1-r2-system-manager-environment.md)).

No implementation, source, hook, manifest, artifact, draft, wiring or
operational authority exists. RP-11 remains unwired and unmet; P5.0-R5 remains
Blocking; `plan.is_executable=False`; Package 5.0 remains not ready.

**Superseded current action, 2026-09-29 — Codex independently re-reviews the returned
R4-D1-R2 LB-2 system-manager environment remediation; Peter Duscha then
decides.**

Claude returned `C-P5.0-R5-RP11-I1-R3-R4-D1-R2` documentation-only and stopped
([amended proposal](review/phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md),
[R2 handback](review/phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r2-system-manager-environment-remediation-handback.md)).
**No recommendation is ready.**

* **LB-2 as returned is withdrawn as prevention.** A systemd unit cannot build
  an allow-list environment before `execve`.
* **LB-2S is the specified correction.** A static first image that reads no
  environment starts the entry with a literal. It depends on PO-9 and PO-14,
  and on new decision M-14, a compiled build dependency.
* **What remains trusted.** Manager execution settings are reviewed root
  input, not prevention (R-10), and M-10 is revised.
* **Scope.** R4-D1-2 is not reopened.

The finding is not claimed closed. No implementation, source, hook, manifest,
artifact, draft, wiring or operational authority exists. RP-11 remains unwired
and unmet; P5.0-R5 remains Blocking; `plan.is_executable=False`; Package 5.0
remains not ready.

**Superseded current action, 2026-09-29 — Claude performs the documentation-only R4-D1-R2
LB-2 system-manager environment remediation, followed by independent Codex
re-review.**

Peter Duscha assigns Claude `C-P5.0-R5-RP11-I1-R3-R4-D1-R2` to establish a
credible closed pre-`execve` entry environment for LB-2 or withdraw/narrow that
direction truthfully. Claude amends the proposal in place, creates the named R2
handback, updates concise pointers and stops. R4-D1-2 remains remediated at
design level and is not reopened.
([assignment](review/phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r2-system-manager-environment-remediation-claude-prompt.md)).

No implementation, source, hook, manifest, artifact, draft, wiring or
operational authority exists. RP-11 remains unwired and unmet; P5.0-R5 remains
Blocking; `plan.is_executable=False`; Package 5.0 remains not ready.

**Superseded current action, 2026-09-29 — remediate the remaining R4-D1-R1 LB-2
pre-loader-environment finding, then obtain independent Codex re-review.**

Codex's independent remediation re-review found R4-D1-2 remediated in the
design but one remaining Blocking defect under R4-D1-1: the recommended LB-2
unit does not establish a closed pre-loader environment, so manager-level
loader state could act before the entry's diagnostic check. LB-2 and the
conditional O-2/D-1 direction are not ready for selection. Peter Duscha must
issue any further bounded documentation-remediation assignment.
([review](review/project-review-2026-09-29-p5-r5-rp11-r4-d1-r1-c11-launcher-contract.md)).

No implementation, source, hook, manifest, artifact, draft, wiring or
operational authority exists. RP-11 remains unwired and unmet; P5.0-R5 remains
Blocking; `plan.is_executable=False`; Package 5.0 remains not ready.

**Superseded current action, 2026-09-29 — Codex independently re-reviews the returned
R4-D1-R1 C-11 launcher-contract remediation; Peter Duscha then decides.**

Claude returned `C-P5.0-R5-RP11-I1-R3-R4-D1-R1` documentation-only and stopped
([amended proposal](review/phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md),
[remediation handback](review/phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r1-c11-launcher-contract-remediation-handback.md)).
The amendment is a decision-ready impossibility result, not a recommendation
that meets today's constraints:

* **Ambient loader state.** No repository-only design on the client's ordinary
  path keeps it from the entry. That needs a host-established launch boundary
  (M-9) and a threat-scope decision (M-10).
* **Pass A texts.** Pass A becomes all-literal under draft amendment D-2 to
  A1-12.
* **Pass B.** It cannot meet the pre-start inspection criterion as drafted
  (M-11).

D-1 is rewritten. Neither Blocking finding is claimed closed. No implementation,
source, hook, manifest, artifact, wiring or operational authority exists. RP-11
remains unwired and unmet; P5.0-R5 remains Blocking; `plan.is_executable=False`;
Package 5.0 remains not ready.

**Superseded action, 2026-09-29 — Claude performs the documentation-only R4-D1-R1
C-11 launcher-contract remediation, followed by independent Codex re-review.**

Claude returned `C-P5.0-R5-RP11-I1-R3-R4-D1` documentation-only and stopped
([proposal](review/phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md),
[handback](review/phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-handback.md)).
Codex's [independent review](review/project-review-2026-09-29-p5-r5-rp11-r4-d1-c11-launcher-contract.md)
found two Blocking defects. Ambient dynamic-loader state acts before the
proposed entry can refuse it, so the claimed in-process enforcement is not
fail-closed. A1-12's runtime value also does not exist when the client hook
runs, so O-2 and D-1 incorrectly claim that the hook inspects its final command
before process start. O-2 and D-1 are not ready for maintainer selection.
Peter Duscha assigns the bounded
[R4-D1-R1 remediation](review/phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r1-c11-launcher-contract-remediation-claude-prompt.md).
Claude must correct both findings in the proposal and stop for independent
re-review. No implementation, source, hook, manifest, artifact, wiring or
operational authority exists. RP-11
remains unwired and unmet; P5.0-R5 remains Blocking; `plan.is_executable=False`;
Package 5.0 remains not ready.

**Superseded action, 2026-09-29 — Claude prepares the C-11 guard-preserving
capture and pinned launcher-environment decision design.**

Peter Duscha assigns Claude `C-P5.0-R5-RP11-I1-R3-R4-D1`, documentation-only,
to compare viable security-boundary options, recommend one and specify a closed
typed environment contract for RP-11-launched `rsync` and `ssh`
([assignment](review/phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-claude-prompt.md)).
Claude stops after the proposal and handback for independent Codex review. No
source, hook, manifest, artifact, wiring or operational action is authorized.

**Superseded action, 2026-09-29 — R3 is accepted; RP-11 remains blocked pending
a fresh bounded assignment for C-11 and the exact pinned launcher environment.**

Peter Duscha accepted `C-P5.0-R5-RP11-I1-R3-R3` after Codex's independent
review found no Blocking, Important or Optional issue
([acceptance](review/project-review-2026-09-29-p5-r5-rp11-i1-r3-r3-posix-post-open-release-acceptance.md)).
The post-open descriptor leaks in `PosixFilesystem.create_file` and `openat`
are closed as remediated. Manifest version 26 and digest `526dd446…` are
accepted review inputs only. RP-11 remains unwired and unmet; C-11 and the
exact pinned launcher environment remain unresolved; P5.0-R5 remains Blocking;
`plan.is_executable=False`; and Package 5.0 remains not ready. No follow-up
implementation or operational authority exists.

**Superseded action, 2026-09-29 — Peter Duscha decides acceptance of the
reviewed C-P5.0-R5-RP11-I1-R3-R3 post-open descriptor-release remediation.**

Claude returned the repository-only slice and stopped
([handback](review/phase-5-0-p5-r5-rp11-i1-r3-r3-posix-post-open-release-handback.md)). `PosixFilesystem.create_file` and `openat` close
the descriptor `os.open` returned exactly once when identity acquisition or the
initial write fails, never retry the close, re-raise the first failure and
leave the created name as the failure left it. 16 new regressions, 11 of which
fail on the old file. The whole package is **3364 passed, 0 skipped** at both
the 1024 and default descriptor limits. Manifest version 26, digest
`526dd446…`, was regenerated by dry run only and is not an approval. RP-11
remains unwired and unmet; P5.0-R5 remains Blocking;
`plan.is_executable=False`; Package 5.0 remains not ready. No host,
database, operational-pass, commit or push authority exists.

Codex independently reviewed the return with no Blocking, Important or Optional
finding and recommends acceptance
([review](review/project-review-2026-09-29-p5-r5-rp11-i1-r3-r3-posix-post-open-release.md)).
Peter Duscha decides.

**Superseded action, 2026-09-29 — Claude executes the bounded repository-only
post-open descriptor-release remediation; Codex independently reviews the
return.**

Peter Duscha assigns Claude `C-P5.0-R5-RP11-I1-R3-R3` to repair the post-open
descriptor leaks in `PosixFilesystem.create_file` and `openat`, add focused
regressions, advance the covered-source manifest and regenerate review
artifacts by dry run only
([assignment](review/phase-5-0-p5-r5-rp11-i1-r3-r3-posix-post-open-release-claude-prompt.md)).
Claude stops after handback; Codex is the independent reviewer. No host,
database, operational-pass, RP-11 wiring, commit or push authority exists.

**Superseded action, 2026-09-29 — await a bounded repository-only reliability
assignment for the post-open failure leaks in `PosixFilesystem.create_file`
and `openat`.**

Peter Duscha accepted Codex's independent review of the corrected RP-11
Option-1 alignment with no finding and closed `RP11-I1-2`, `RP11-I1-R2-1` and
`RP11-I1-R1-1` as superseded by the accepted I1-R3 design
([acceptance record](review/project-review-2026-09-29-p5-r5-rp11-option-1-alignment-acceptance.md)).
The review reproduced **3348 passed, 0 skipped** at both the 1024 and default
descriptor limits. This accepts the alignment and finding dispositions only.
RP-11 remains unwired and unmet; C-11 and the pinned launcher environment
remain unresolved; P5.0-R5 remains Blocking; `plan.is_executable=False`; and
Package 5.0 remains not ready. No host or operational authority exists.

**Superseded action, 2026-09-28 — Codex independently reviews the Option-1
documentation alignment together with its C-P5.0-R5-RP11-I1-R3-D2-DOC1-R1
correction.**

Claude reviewed the returned D2-DOC1 alignment and found no Blocking issue and
no behavior change. On Peter Duscha's instruction it corrected the record-integrity
findings under D2-DOC1-R1
([handback](review/phase-5-0-p5-r5-rp11-i1-r3-d2-doc1-r1-alignment-review-remediation-handback.md)):

* **Proposal.** The historical decision proposal, edited in place, is restored
  byte-for-byte to `ac504ce1…`, and an erratum records the correction.
* **Draft.** The operational draft's amendment attribution, §4.3 stale-pin
  list and B0-RA unresolved clause are corrected. It is now `5c6046fc…`,
  unaccepted.
* **Findings.** `RP11-I1-2` (Blocking), `RP11-I1-R2-1` (Blocking) and
  `RP11-I1-R1-1` (Important) are restored to the current state as Open. Peter
  directs a proposed disposition, superseded by the accepted I1-R3 design, for
  independent confirmation.

No covered source changed. Manifest version 25 and `f63cf359…` are unchanged
and reproduce byte-identically by dry run. The whole package is 3348 passed,
0 skipped, at both the 1024 and default descriptor limits. This is not RP-11
acceptance or wiring. RP-11 remains unmet, C-11 and the pinned launcher
environment remain unresolved, P5.0-R5 remains Blocking,
`plan.is_executable=False`, and Package 5.0 remains not ready. No host or
operational authority exists.

**Superseded action, 2026-09-28 — independently review the exact bytes aligning
the accepted RP-11 Option-1 policy.**

Peter Duscha accepted **Option 1**: the one staging/final pair Pass A's final
state records for an unadmitted regular file may be verified by metadata only.
Both fixed names must be present, share one inode at link count two and share it
with no third name. Neither member is opened, read, digested or admitted; every
broader or ambiguous alias state stops fail closed.
[Decision and review record](review/project-review-2026-09-28-p5-r5-rp11-i1-r3-r2-and-unadmitted-pair-decision.md).

Codex's R2 re-review found no new Blocking or Important issue and reproduced
the 12 focused regressions and the full **3348 passed, 0 skipped** package both
at soft descriptor limit 1024 and at the default. `RP11-I1-R3-1` is Closed by
decision; `RP11-I1-R3-2` and `RP11-I1-R3-3` are Closed as remediated.

The returned documentation alignment removes stale pending-decision wording and moves
the covered-source manifest to version 25 at review-input digest `f63cf359…`.
The regenerated artifacts are dry-run products only. Focused verification is
774 passed and the whole package is 3348 passed at both the 1024 and default
descriptor limits, with zero skips. Those exact bytes now await independent
review. This is not RP-11 acceptance or wiring. RP-11
remains unmet, C-11 and the pinned launcher
environment remain unresolved, P5.0-R5 remains Blocking,
`plan.is_executable=False`, and Package 5.0 remains not ready. No host or
operational authority exists.

**Superseded action, 2026-09-28 — Claude repairs the production lifecycle-store
descriptor leak under C-P5.0-R5-RP11-I1-R3-R2; Peter Duscha separately decides
the unadmitted-pair policy.**

Peter assigns the bounded repository-only
[R2 remediation](review/phase-5-0-p5-r5-rp11-i1-r3-r2-lifecycle-descriptor-release-remediation-claude-prompt.md).
It closes descriptors acquired by `DurableRecordStore` read and publication
paths on every success and failure path, adds production leak regressions,
increments the covered-source manifest and regenerates review artifacts by dry
run. It does not change retained-alias semantics or record the pending policy
decision. No host or operational authority exists. The return requires
independent Codex re-review; RP-11 remains unmet, P5.0-R5 remains Blocking and
`plan.is_executable=False`.

**Superseded action, 2026-09-28 — Codex independently re-reviews the returned
C-P5.0-R5-RP11-I1-R3-R1 remediation; Peter Duscha decides the unadmitted-pair
policy.**

Claude returned the repository-only remediation and stopped.
[I1-R3-R1 handback](review/phase-5-0-p5-r5-rp11-i1-r3-r1-retained-alias-review-remediation-handback.md).

* **Evidence discrepancy.** The 2941-passed, 379-failed result reproduces
  under a 1024 soft descriptor limit. The earlier 3320-pass run had a limit
  of 1 048 576.
  * RP-11 test-held descriptors, 619, are released test-side.
  * A `lifecycle_storage` release defect exercised by older lab tests, 963,
    is out of scope and proposed as a follow-up.
  * The whole package passes from fresh processes at both limits: 3336
    passed, 0 skipped.
* **Draft wording.** Corrected to the precise unwired, unaccepted, unmet
  state. The draft is `4f68e4c7…`, unaccepted.
* **Policy.** The
  [decision proposal](review/phase-5-0-p5-r5-rp11-i1-r3-r1-unadmitted-pair-decision-proposal.md)
  recommends option 1 and awaits Peter's decision. Source semantics are
  unchanged.
* **Manifest.** Unchanged: version 23, `264674da…`, not an approval.

All findings remain Open, and RP11-I1-R3-1 remains Blocking. RP-11 remains
unmet, P5.0-R5 remains Blocking, `plan.is_executable=False`, and Package 5.0
remains not ready. No host or operational authority exists.

**Superseded action, 2026-09-28 — Claude executes the repository-only
C-P5.0-R5-RP11-I1-R3-R1 review remediation.**

Codex's
[I1-R3 review](review/project-review-2026-09-28-p5-r5-rp11-i1-r3.md)
requested changes for three findings: the Blocking unadmitted-pair policy lacks
a confirmed decision of record; the claimed 3320-pass whole-package result did
not reproduce because a descriptor-exhaustion cascade produced 2941 passed and
379 failed; and the amended draft still falsely says no RP-11 mechanism exists.

Peter Duscha assigns Claude the
[I1-R3-R1 remediation prompt](review/phase-5-0-p5-r5-rp11-i1-r3-r1-retained-alias-review-remediation-claude-prompt.md).
Claude must diagnose and remediate the evidence discrepancy, correct stale
state wording, and prepare a concrete decision proposal for Peter. The missing
policy decision does not stop those unrelated tasks. Source semantics remain
unchanged pending the decision. No host or operational authority exists.

All findings remain Open. RP-11 remains unmet, P5.0-R5 remains Blocking,
`plan.is_executable=False`, and Package 5.0 remains not ready.

**Superseded action, 2026-09-28 — Codex independently reviews the returned
C-P5.0-R5-RP11-I1-R3-I1 retained-alias implementation.**

Claude returned the repository-only slice and stopped.
[I1-R3 handback](review/phase-5-0-p5-r5-rp11-i1-r3-retained-alias-implementation-handback.md).

* **Draft.** The
  [operational-evidence draft](review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md)
  is amended in place to SHA-256 `402126322f34…`, unaccepted. The R5 bytes
  (`5e06a388…`) remain the baseline.
* **Source.** The unwired RP-11 source is amended to match:
  * each record and index state is an exclusively created staging name, given
    its final name by one no-follow, non-replacing hard link;
  * both names are verified, retained and recorded with their shared inode in
    the next durable index state, which alone admits the object;
  * nothing is ever unlinked, renamed or cleaned up.
* **Removed.** The `O_TMPFILE`/procfs route and the mutating §9.5.4 probe. The
  first real X-1 genesis publication is the fail-closed capability test.
* **X-4 and B0-RA.** They accept only a recorded staging/final pair as an
  alias. A recorded unadmitted pair is checked by metadata only, on Peter
  Duscha's in-session decision, which is to be confirmed as the decision of
  record.
* **Manifest.** Version 23, review-input digest `264674da…`. **Not an
  approval.**
* **Local results, with `TEST_DATABASE_URL` unset.** RP-11 suites: 367 passed,
  0 skipped. `tests/phase_5_0_evidence`: 3320 passed, 0 skipped. Harness CLI:
  dry run only.

RP11-I1-R1-1, RP11-I1-R2-1 and RP11-I1-2 remain Open, and RP-11 remains unmet.
P5.0-R5 remains Blocking, `plan.is_executable=False`, and Package 5.0 remains
not ready. No host or operational authority exists.

**Superseded action, 2026-09-28 — execute the assigned bounded RP-11 I1-R3
requirements-and-source implementation repository-only.**

On Peter Duscha's instruction to change approach, Codex stopped further
remediation of the context-dependent `O_TMPFILE` plus `/proc/self/fd/N` probe.
The [I1-R3 proposal](review/phase-5-0-p5-r5-rp11-i1-r3-publication-redesign-proposal.md)
recommends exclusive named staging creation, non-replacing descriptor-relative
hard-link publication, and retention of both staging and final names as indexed
objects with no automatic unlink. This removes both the procfs dependency and
the recheck-to-unlink race.

Peter Duscha accepts the direction in the
[I1-R3 acceptance record](review/project-review-2026-09-28-p5-r5-rp11-i1-r3-redesign-acceptance.md).
Peter Duscha assigns Claude the
[I1-R3 implementation prompt](review/phase-5-0-p5-r5-rp11-i1-r3-retained-alias-implementation-claude-prompt.md).
It authorizes coherent repository requirements/source/test/manifest edits and
focused local tests, followed by mandatory independent Codex review. It does
not authorize host or operational execution.
RP11-I1-R1-1, RP11-I1-R2-1 and RP11-I1-2 remain Open; RP-11 remains unmet;
P5.0-R5 remains Blocking; `plan.is_executable=False`; Package 5.0 remains not
ready.

**Superseded action, 2026-09-28 — Codex independently reviews the returned
C-P5.0-R5-RP11-I1-R2 evidence remediation.**

* **The finding.** Codex's
  [I1-R1 review](review/project-review-2026-09-28-p5-r5-rp11-i1-r1.md) raised the Important finding **RP11-I1-R1-1**:
  the diagnostic prototype did not exercise the proposed §9.5.4 check.
* **The remediation.** On Peter Duscha's in-session instruction, Claude made
  the test-only prototype perform every locally testable §9.5.4 step, in
  order, through the production creation and link functions:
  * owner, mode, emptiness and device checks;
  * a checked complete write;
  * exact readback;
  * an identity recheck;
  * verified cleanup.
* **Results, with `TEST_DATABASE_URL` unset.** The module gives 30 passed,
  0 skipped. The I1-R1 selection plus the module gives 1200 passed, 0 skipped.
* **Erratum.** A dated erratum narrows the I1-R1 handback's prototype claim.
* **Unchanged.** The draft (`186ff546…`), production source and the manifest.

RP11-I1-R1-1 and RP11-I1-2 remain Open. RP-11 remains unmet. Neither pass is
executable or authorized. P5.0-R5 remains Blocking, OD-62 G-A remains
conditional, `plan.is_executable=False`, and Package 5.0 remains not ready.
[I1-R2 handback](review/phase-5-0-p5-r5-rp11-i1-r2-capability-prototype-evidence-remediation-handback.md);
[I1-R2 assignment](review/phase-5-0-p5-r5-rp11-i1-r2-capability-prototype-evidence-remediation-claude-prompt.md).

**Superseded action, 2026-09-28 — Codex independently reviews the returned
C-P5.0-R5-RP11-I1-R1 remediation.**

* **Requirements amendment, unaccepted.** Claude amended the
  [operational-evidence draft](review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md)
  in place to SHA-256 `186ff546…`, for review only. P-5 … P-8 and X-1 … X-3
  now specify publication by an unnamed `O_TMPFILE` inode given its one name
  by an exclusive link through `/proc/self/fd/<n>`, with failure semantics
  before and after the link. The shared `os.link` call site is stated as two
  reviewed contracts, which amends the I3 primitive. The amendment also adds a
  pre-admission publication capability check in the mechanism's own process
  before X-1 (§9.5.4), the behavioural read-only seal, the
  `rp11-capture-binding/1` block in §14 and the capture-tool digest scope.
  C-11 and the launcher environment remain blockers.
* **Diagnosis.** It reproduces 1170 passed, 0 skipped locally, and reproduces
  Codex's `ENOENT` by two named routes. Its attribution in the review context
  is unresolved.
* **Unchanged.** No production source or manifest changed.

The R5 bytes (`5e06a388…`) remain the accepted baseline. Both findings remain
Open; RP-11 remains unmet; neither pass is executable or authorized; P5.0-R5
remains Blocking; OD-62 G-A remains conditional; `plan.is_executable=False`;
Package 5.0 remains not ready.
[I1-R1 handback](review/phase-5-0-p5-r5-rp11-i1-r1-publication-contract-and-portability-remediation-handback.md).

**Superseded action, 2026-09-28 — C-P5.0-R5-RP11-I1-R1 assigned
repository-only.** Peter Duscha accepts and assigns the bounded
[publication-contract and portability remediation](review/phase-5-0-p5-r5-rp11-i1-r1-publication-contract-and-portability-remediation-claude-prompt.md).
Claude must amend requirements for independent review and diagnose why the
local publication route is not portable, without changing RP-11 production
source. Codex's
[review](review/project-review-2026-09-28-p5-r5-rp11-capture-mechanism.md)
found two Blocking issues: `O_TMPFILE` + `linkat` differs from the accepted
temporary-name + atomic-rename contract, and the reported focused result did
not reproduce. Codex obtained **991 passed, 179 failed, 0 skipped** with
`TEST_DATABASE_URL` unset because `/proc/self/fd/N` publication returned
`ENOENT` before genesis. The capability check is bounded, disposable and
cleanup-verified, before any real capture root or host command. The assignment
creates no host or operational authority. Both findings remain Open; RP-11
remains unmet; neither pass is executable or authorized; P5.0-R5 remains
Blocking; OD-62 G-A remains conditional; `plan.is_executable=False`; Package
5.0 remains not ready.

**Superseded action, 2026-09-28 — Codex independently reviewed the returned
C-P5.0-R5-RP11-I1 implementation.** Claude implemented RP-11's client-side
capture mechanism and B0-RA's read-only retention check in repository source,
with focused local tests: 1170 passed and 0 skipped. It is wired to no command.
The review manifest moves to version 22 with review-input digest `adeabe17…`,
which is not an approval. The review should cover the three in-session
maintainer decisions (`O_TMPFILE` + `linkat` publication, the behavioural
read-only seal, and the shared `os.link` call site) and the open questions: C-11
synchronization capture versus `guard-secrets.py`, the launcher environment, and
the binding block's place in draft §14. RP-11 remains unmet. Neither pass is
executable or authorized. P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; `plan.is_executable=False`; Package 5.0 remains not ready.
[Implementation handback](review/phase-5-0-p5-r5-rp11-capture-mechanism-implementation-handback.md).

**Superseded action, 2026-09-27 — C-P5.0-R5-RP11-I1 repository implementation.**
Peter Duscha assigned a bounded implementation of RP-11's crash-consistent
client-side capture mechanism and read-only B0-RA retention verification, with
focused local tests and a handback for independent Codex review. The assignment
authorizes no host, synchronization, database, evidence-band, reboot or
`--execute` activity and does not mark RP-11 satisfied.
[Claude prompt](review/phase-5-0-p5-r5-rp11-capture-mechanism-implementation-claude-prompt.md).

**Prior disposition, 2026-09-27 — R5 requirements remediation accepted.** Codex independently reviewed
the exact R5-amended draft with no findings, and Peter Duscha accepted
C-P5.0-R5-OP1-R5. **OP1-R4-1 is Closed, remediated.** B0-RA gains condition 5: one complete
recursive enumeration of `MI.capture_root_A` must agree in both directions
with the names Pass A's final state accounts for, each at its exact relative
name and expected object type. An absent recorded name (including an
unadmitted name), an unexpected name, a type mismatch, a duplicate or
ambiguous name, a path alias, an escape from the root or an incomplete
comparison is a fail-closed B0 stop before B0-08. No `MI.capture_root_B` is
created, no Pass B host command is issued, and the check is not retried. The
final state now records unadmitted files and mechanism-created subdirectories
by relative name and type, with no content digest. For unadmitted files
B0-RA verifies presence, name and type only, never unchanged content. The
accepted correction is requirements-only: RP-11 remains absent and unmet,
neither pass is executable or authorized, and no host action occurred. The
accepted correction itself creates no operational authority. MD-1 through MD-6
are preserved. P5.0-R5 remains Blocking; OD-62 G-A remains conditional;
`plan.is_executable=False`; Package 5.0 remains not ready.
[R5-amended draft](review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md);
[R5 handback](review/phase-5-0-p5-r5-operational-evidence-prompt-r5-unadmitted-retention-remediation-handback.md);
[R5 assignment](review/phase-5-0-p5-r5-operational-evidence-prompt-r5-unadmitted-retention-remediation-claude-prompt.md);
[Codex R5 review](review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r5.md);
[maintainer acceptance](review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r5-acceptance.md).

**Superseded action, 2026-09-27 — remediate unadmitted-file retention
verification repository-only.** Codex's R4 review confirms that B0-RA now
binds Pass A's root, final index, chain, admitted records and bound streams,
but finds one Blocking gap: it does not require every unadmitted name recorded
by Pass A's final state to remain present. Claude must amend requirements only
so B0-RA compares the complete recursive name set in both directions and
fails closed on any absent recorded name, unexpected observed name or object-
type mismatch. The draft must state that presence of an undigested unadmitted
object does not prove its bytes unchanged. RP-11 remains absent and unmet;
neither pass is executable or authorized. MD-1 through MD-6 are preserved.
P5.0-R5 remains Blocking; OD-62 G-A remains conditional;
`plan.is_executable=False`; Package 5.0 remains not ready.
[R5 assignment](review/phase-5-0-p5-r5-operational-evidence-prompt-r5-unadmitted-retention-remediation-claude-prompt.md);
[Codex R4 review](review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r4.md);
[R4-amended draft](review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md);
[R4 handback](review/phase-5-0-p5-r5-operational-evidence-prompt-r4-retention-verification-remediation-handback.md).

**Superseded action, 2026-09-27 — Codex independently reviews the R4-amended
P5.0-R5 operational-evidence authorization prompt.** Claude completed
C-P5.0-R5-OP1-R4 repository-only. A new Pass B admission step, B0-RA, runs
before B0-08. It verifies without mutation that `MI.capture_root_A`, the named
final index state and the capture index SHA-256 match a digest-pinned Pass A
handback (new input `MI.pass_a_handback`). It also verifies that X-4 still
holds for Pass A's retained chain, records and bound stream files, with every
retained name accounted for by Pass A's final state. Absence, mismatch,
invalidity or inability to check stops Pass B fail-closed: no
`MI.capture_root_B` is created and no Pass B host command is issued. The check
only lists names, reads bytes and re-derives digests. It establishes retention
at that moment only. Pass A's root stays retained, unmodified and never used as
Pass B evidence. The correction is requirements-only: RP-11 remains absent and
unmet, neither pass is executable or authorized, and no host action occurred.
MD-1 through MD-6 are preserved. P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; `plan.is_executable=False`; Package 5.0 remains not ready.
[R4-amended draft](review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md);
[R4 handback](review/phase-5-0-p5-r5-operational-evidence-prompt-r4-retention-verification-remediation-handback.md);
[R4 assignment](review/phase-5-0-p5-r5-operational-evidence-prompt-r4-retention-verification-remediation-claude-prompt.md);
[Codex R3 review](review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r3.md).

**Superseded action, 2026-09-27 — remediate Pass A retention verification before
Pass B repository-only.** Codex's R3 review confirms that the distinct-root
and ordered-stop defects are resolved in substance, but finds one Blocking
evidence-integrity defect: B0 does not verify that Pass A's required retained
capture root and durable final index still exist and match the Pass A handback.
Claude must amend requirements only so a non-mutating, fail-closed B0 check
binds `MI.capture_root_A`, the final-state name and capture-index digest to the
Pass A handback and revalidates X-4 before Pass B creates
`MI.capture_root_B` or issues any host command. RP-11 remains absent and unmet;
neither pass is executable or authorized. MD-1 through MD-6 are preserved.
P5.0-R5 remains Blocking; OD-62 G-A remains conditional;
`plan.is_executable=False`; Package 5.0 remains not ready.
[R4 assignment](review/phase-5-0-p5-r5-operational-evidence-prompt-r4-retention-verification-remediation-claude-prompt.md);
[Codex R3 review](review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r3.md);
[R3-amended draft](review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md);
[R3 handback](review/phase-5-0-p5-r5-operational-evidence-prompt-r3-contract-consistency-remediation-handback.md).

**Superseded action, 2026-09-27 — Codex independently reviews the R3-amended
P5.0-R5 operational-evidence authorization prompt.** Claude completed
C-P5.0-R5-OP1-R3 repository-only. The single `MI.capture_root` is replaced by
distinct, pass-specific roots: `MI.capture_root_A` for Pass A only and
`MI.capture_root_B` for Pass B only. Each root is exclusively created with
its own genesis state, index chain and final state; a new B0-08 admits Pass
B against its own root. Pass A's root stays retained, unmodified and unused,
and is never removed, renamed, reused or modified to admit Pass B. §9.5.3 now
defines one ordered stop transition. Command execution stops at once. Where
the capture mechanism and repository host remain available, one X-3
finalization attempt is the only permitted write, and the capture root
becomes read-only when that attempt succeeds or fails. A failed attempt is
never retried, cured or reconstructed. After an interruption no attempt is
made and X-4 applies directly. The correction is requirements-only: RP-11
remains absent and unmet, neither pass is executable or authorized, and no
host action occurred. MD-1 through MD-6 are preserved. P5.0-R5 remains
Blocking; OD-62 G-A remains conditional; `plan.is_executable=False`; Package
5.0 remains not ready.
[R3-amended draft](review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md);
[R3 handback](review/phase-5-0-p5-r5-operational-evidence-prompt-r3-contract-consistency-remediation-handback.md);
[R3 assignment](review/phase-5-0-p5-r5-operational-evidence-prompt-r3-contract-consistency-remediation-claude-prompt.md);
[Codex R2 review](review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r2.md).

**Superseded action, 2026-09-27 — execute the assigned C-P5.0-R5-OP1-R3
repository-only remediation.** Codex reviewed the exact R2-amended draft and
confirmed that OP1-R1-1's original durability omissions are resolved in
substance. Two Blocking defects remain: the single `MI.capture_root` cannot be
both retained after Pass A and absent at Pass B admission, and the contract
both requires X-3 finalization after a stop and immediately makes the capture
root read-only after a stop. The correction must make roots pass-specific and
define finalization as the sole permitted post-failure write before the root
becomes read-only, while preserving interruption, no-retry and no-reconstruction
rules.
[R2 review](review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r2.md);
[R3 assignment](review/phase-5-0-p5-r5-operational-evidence-prompt-r3-contract-consistency-remediation-claude-prompt.md);
[R2-amended draft](review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md);
[R2 handback](review/phase-5-0-p5-r5-operational-evidence-prompt-r2-durability-remediation-handback.md).

Neither pass is executable or authorized. RP-11 remains absent and unmet;
MD-1 through MD-6 are preserved. P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; `plan.is_executable=False`; Package 5.0 remains not ready.

**Superseded action, 2026-09-27 — Codex independently reviews the R2-amended
P5.0-R5 operational-evidence authorization prompt.** Claude completed
C-P5.0-R5-OP1-R2 repository-only. RP-11 and §9.5 now require a
crash-consistent publication contract. Stream files are completed, closed,
file-synchronized and their directory entries made durable before any record
publishes their digests. Each record is written under a temporary name,
file-synchronized, published by a non-replacing atomic rename and followed by
a containing-directory synchronization. The capture index is a chain of
immutable index states with a defined finalization point and final digest.
Any failed barrier is an `inconclusive` stop, never retried or repaired. The
correction is requirements-only: RP-11 remains absent and unmet, neither pass
is executable or authorized, and no host action occurred. MD-1 through MD-6
are preserved. P5.0-R5 remains Blocking; OD-62 G-A remains conditional;
`plan.is_executable=False`; Package 5.0 remains not ready.
[R2-amended draft](review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md);
[R2 handback](review/phase-5-0-p5-r5-operational-evidence-prompt-r2-durability-remediation-handback.md);
[R2 assignment](review/phase-5-0-p5-r5-operational-evidence-prompt-r2-durability-remediation-claude-prompt.md);
[Codex R1 re-review](review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r1.md).

**Superseded action, 2026-09-27 — remediate the RP-11 capture-durability contract
repository-only.** Codex's independent R1 re-review confirmed that the three
original operational-prompt findings are resolved in substance, then raised
one Blocking finding, OP1-R1-1: the new capture contract does not require
durable publication of both stream files, per-act record directory entries or
the pass-level capture index. Claude must amend the requirements only, return
an R2 handback and stop for Codex review. It must not implement RP-11 or perform
any host action.

Neither pass is executable or authorized. MD-1 through MD-6 are preserved.
P5.0-R5 remains Blocking; OD-62 G-A remains conditional;
`plan.is_executable=False`; Package 5.0 remains not ready.
[Codex R1 re-review](review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r1.md);
[R2 remediation assignment](review/phase-5-0-p5-r5-operational-evidence-prompt-r2-durability-remediation-claude-prompt.md);
[amended draft](review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md).

**Superseded action, 2026-09-27 — Codex independently re-reviews the amended
P5.0-R5 operational-evidence authorization prompt.** Claude completed
C-P5.0-R5-OP1-R1. Codex's R1 re-review found its three original corrections
substantively successful and raised OP1-R1-1. No host action occurred.
[R1 remediation assignment](review/phase-5-0-p5-r5-operational-evidence-prompt-remediation-claude-prompt.md);
[R1 remediation handback](review/phase-5-0-p5-r5-operational-evidence-prompt-remediation-handback.md).

**Superseded action, 2026-09-27 — remediate the returned P5.0-R5 operational-
evidence authorization prompt repository-only, then return it for Codex
re-review.** Codex requested changes to both passes: RP-1 self-derives E7
expectations from Pass A observations; row 40's `fsync` failure-injection
feasibility work is improperly deferred; and the separate stdout/stderr digest
contract has no executable capture method. Neither pass is authorized. Claude
must preserve MD-1 through MD-6, keep every unresolved dependency fail-closed,
make documentation changes only and perform no action on `oracle-test`.
[Codex review](review/project-review-2026-09-27-p5-r5-operational-evidence-prompt.md);
[remediation assignment](review/phase-5-0-p5-r5-operational-evidence-prompt-remediation-claude-prompt.md).

**Superseded action, 2026-09-24 — prepare the bounded P5.0-R5 operational-
evidence authorization prompt for independent pre-execution review.** Claude
returned the draft and handback; Codex's 2026-09-27 review requested changes.
The draft remains unauthorized. It preserves Peter Duscha's MD-6 decision to
accept `R-5.0-13` without requiring JNL-40(b) for P5.0-R5 closure.
[Draft](review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md);
[drafting handback](review/phase-5-0-p5-r5-operational-evidence-prompt-drafting-handback.md);
[MD-6 decision](review/project-review-2026-09-24-p5-r5-md6-jnl-40b-disposition.md).

**Superseded action, 2026-09-23 — decide MD-6, the disposition of JNL-40(b).**
Choose whether the second-host or `/etc/machine-id`-rewrite case is mandatory,
or accept `R-5.0-13` without it. Acceptance without the case is recommended
because MD-4 already explicitly accepted `R-5.0-13`. Peter Duscha has decided
MD-5: classifier contradictions must be corrected and independently reviewed
before any evidence band is executable. `plan.is_executable=False` remains
controlling; no implementation or host authority is created.
[MD-5 decision](review/project-review-2026-09-23-p5-r5-md5-classifier-prerequisite.md).

**Superseded action, 2026-09-23 — decide MD-5, the correction of the classifier
contradictions identified by reconciliation finding S-3.** The recommendation
is to require those corrections before any evidence band is treated as
executable. Peter Duscha has decided MD-4: `R-5.0-10` through `R-5.0-16` are
accepted as active residual risks, with recovery rehearsals mandatory for
`R-5.0-11`, `R-5.0-14` and `R-5.0-16`. This creates no implementation or host
authority. P5.0-R5 remains Blocking; OD-62 G-A remains conditional;
`plan.is_executable=False`; Package 5.0 remains not ready.
[MD-4 decision](review/project-review-2026-09-23-p5-r5-md4-residual-dispositions.md).

**Superseded action, 2026-09-23 — decide MD-4, the explicit disposition of
R-5.0-10 through R-5.0-16.** Peter Duscha has decided MD-3: the supervised
reboot durability case is mandatory for P5.0-R5 harness-facsimile feasibility
closure and may not end as Not Run or an accepted residual. This creates no
reboot or host authority. P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; `plan.is_executable=False`; Package 5.0 remains not ready.
[MD-3 decision](review/project-review-2026-09-23-p5-r5-md3-reboot-requirement.md).

**Superseded action, 2026-09-23 — decide MD-3, the supervised reboot requirement
for P5.0-R5 feasibility closure.** Peter Duscha has decided MD-2: `oracle-test`,
the approved disposable target, supplies the target-specific feasibility host
facts. Package-plan §8.1 development-host observations remain historical
context and must not satisfy those requirements. Fresh observation still needs
separate authorization; this decision creates none. P5.0-R5 remains Blocking;
OD-62 G-A remains conditional; `plan.is_executable=False`; Package 5.0 remains
not ready.
[MD-2 decision](review/project-review-2026-09-23-p5-r5-md2-host-facts-baseline.md).

**Superseded action, 2026-09-23 — decide MD-2, the host-facts baseline for P5.0-R5
feasibility evidence.** Peter Duscha has decided MD-1: P5.0-R5 may close on
independently reviewed harness-facsimile feasibility evidence from the approved
disposable target, while actual production journal-code evidence remains
mandatory at the implementation/release gate. The two evidence classes remain
separate and non-substitutable. This creates no implementation or host
authority. P5.0-R5 remains Blocking; OD-62 G-A remains conditional;
`plan.is_executable=False`; Package 5.0 remains not ready.
[MD-1 decision](review/project-review-2026-09-23-p5-r5-md1-evidence-criterion.md).

**Superseded action, 2026-09-22 — independently review the returned
C-P5.0-R5-E1 P5.0-R5 evidence reconciliation.** Claude performed the
repository-only pass on the maintainer's direct instruction (assignment to be
confirmed by Peter Duscha). It concludes
`additional_authorized_operational_evidence_required`: no P5.0-R5 proposition
has accepted operational evidence; I3/R8 does not measure the journal; most of
`TC-5.0-JNL` needs tooling and migration `0014` that do not exist, so the
closure criterion itself needs a maintainer decision; and two harness
classifier contradictions are reported. P5.0-R5 remains Blocking; OD-62 G-A
remains conditional; `plan.is_executable=False`; Package 5.0 remains not ready;
no host action or `--execute` is authorized.
[Reconciliation handback](review/phase-5-0-p5-r5-evidence-reconciliation-handback.md).

**Superseded action, 2026-09-22 — accept and assign, or revise, the draft
C-P5.0-R5-E1 evidence-reconciliation prompt.** The prompt is repository-only,
keeps Codex as Independent Reviewer, and authorizes no host or database action.
P5.0-R5 remains Blocking; OD-62 G-A remains conditional; Package 5.0 remains
not ready; `plan.is_executable=False`; no `--execute` is authorized.
[Draft prompt](review/phase-5-0-p5-r5-evidence-reconciliation-claude-prompt.md).

**Superseded action, 2026-09-22 — assess P5.0-R5 readiness evidence and prepare the
binding OD-62 risk decision.** Peter Duscha closes both R6 findings as accepted
historical violations, accepts R8 as valid replacement evidence and closes
**I3**. R6 remains retained but inadmissible as gate evidence; the protected R6
artifact remains preserved and no cleanup is authorized. Package 5.0 remains
not ready: P5.0-R5 still needs package-level operational evidence and an
independent closure recommendation, and OD-62 remains Open with G-A provisional
until that evidence is accepted and its residual risk is explicitly accepted
or rejected. `plan.is_executable=False`; no host action or `--execute` is
authorized.
[R6/I3 decision](review/project-review-2026-09-22-r6-findings-and-i3-disposition.md).

**OD-62 direction confirmed in principle, 2026-09-22.** Peter selects G-A and
accepts its unprovable late-Google-apply residual in principle, based on the
small user base and a known, supervised cutover time. The choice becomes binding
only after the existing P5.0-R5 independent-review precondition is met. Under
§15.1, PostgreSQL is the sole authority after cutover and dual writes remain
prohibited. Retaining the Sheet and rollback path for a numeric verification
period is already required; any continuously updated Sheet would be a separate,
one-way diagnostic projection requiring review, never a second authority.

**§15.1 verification period decided, 2026-09-22.** The numeric post-cutover
verification period is **four weeks per approved field-group cutover**. The
source Sheet is frozen read-only and retained with its export, connector,
credential and rollback path. PostgreSQL is the sole authority; no dual writes
and no live PostgreSQL-to-Sheet projection are permitted. Rollback must use the
approved reconciliation procedure so later PostgreSQL changes are not silently
lost. Archive/removal remains a separate explicit maintainer approval after the
verification gate passes.

**Superseded action, 2026-09-22 — decide the two R6 Blocking findings, then I3.**
Peter Duscha confirms and accepts R8-R6; **LAB-I3-R8-D1-TABLE-1 is Closed,
remediated**. The remaining critical-path decisions are the explicit
dispositions of PR-20260920-LAB-I3-R6-1 and PR-20260920-LAB-I3-R6-2, followed
by whether the clean R8 evidence confirms and closes I3. Until those decisions:
both findings remain Open, Blocking; I3 remains performed but unconfirmed;
`plan.is_executable=False`; Package 5.0 remains not ready; and no action on
`oracle-test` is authorized.
[R8-R6 acceptance](review/project-review-2026-09-22-reserved-laboratory-i3-r8-r6-acceptance.md).

**Superseded action, 2026-09-22 — independently re-review the returned
C-P5.0-LAB-I3-R8-R6 change-log table repair.** Claude performed the bounded
**repository-only** repair: the change-log table delimiter now directly follows
the header, with the D1 row byte-identical. On the maintainer's follow-up
instruction, a stray cell separator in the C-P5.0-LAB-I3-R5-I row was replaced
by `;`, and rows C-P5.0-LAB-I3-R8-R6 and C-P5.0-LAB-I3-R8-D2 (the R8-R5
acceptance) were added. **LAB-I3-R8-D1-TABLE-1 remains Open,
Important** for Codex re-review. R8-R5 remains accepted and
LAB-I3-R8-R2-ROLLBACK-1 remains Closed, remediated. No suite or secrets scan was
run and no command was issued to `oracle-test`. Both R6 Blocking findings and I3
remain open; `plan.is_executable=False`; Package 5.0 remains not ready; no
action on `oracle-test` is authorized. **No scope, schedule or risk baseline
change.**
[R8-R6 repair handback](review/phase-5-0-reserved-laboratory-i3-r8-r6-change-log-table-structure-handback.md).

**Superseded action, 2026-09-22 — decide whether to accept and assign the
bounded R8-R6 change-log table repair prompt.** *Superseded by the returned
R8-R6 repair above.* R8-R5 is accepted,
**LAB-I3-R8-R2-ROLLBACK-1 is Closed, remediated**, and no R8-R2 rollback is
wanted. **LAB-I3-R8-D1-TABLE-1 is Open, Important** because the D1 decision row
precedes the change-log table delimiter and breaks table rendering. R8-R6 is
draft only. Both R6 Blocking findings and I3 remain open;
`plan.is_executable=False`; Package 5.0 remains not ready; no action on
`oracle-test` is authorized.

**Superseded action, 2026-09-22 — independently re-review the returned
C-P5.0-LAB-I3-R8-R5 remediation.** *Superseded by its acceptance above; the
historical evidence below stands.*
Claude performed the bounded
**repository-only** R8-R5 pass and returned it for independent Codex technical,
security and evidence re-review.

**LAB-I3-R8-R2-ROLLBACK-1 — Open, Important.** The R8-R2 handback §8.1 told an
operator to `git checkout --` "the eight modified documents" and delete the
added handback, claiming exact restoration of the 92-path pre-remediation state.
**The instruction and the claim are withdrawn as unsafe and unsupported.** R8-R2
§5 lists nine edited documents plus the new handback; seven are tracked, and the
R8 and R8-R1 handbacks are **untracked**; all nine already carried earlier-pass
uncommitted work. **No R8-chain content exists at `HEAD`** — `LAB-I3-R8`,
`R8-R1` and `R8-R2` occur **zero** times in each tracked document's committed
version, and the seven stood at **+8,659 / −18 lines** against `2fb1d6f` when
R8-R5 began — so the command would **erase the entire uncommitted R8 evidence
chain**, including the later passes and the maintainer's dispositions. The
R8-R2 handback now carries the R8-R3 and R8-R5 errata, so deleting it is not an
R8-R2-only reversal either. **It was not executed**, nothing was reverted or
deleted and no reverse patch was manufactured. The truthful rollback now
recorded: only the R8-R2-specific hunks and the one file R8-R2 added may be
reversed, through a **reviewed remediation-specific reverse patch or equivalent
exact reconstruction preserving every pre-existing change**; **the exact
pre-R8-R2 bytes are not independently available**, so **no exact automated
rollback is claimed** and **any rollback of R8-R2 requires maintainer
coordination**.

**Unchanged:** every measured value and evidence claim in the R8 chain. **No
measurement of the R8 evidence was made**, no rule altered, **no secrets scan
run**, **no guard refusal occurred**, and **no command was issued to
`oracle-test`**. The five findings closed on 2026-09-22 stand as decided. Both
R6 Blocking findings and I3 remain open; `plan.is_executable=False`; Package 5.0
remains not ready. **No scope, schedule or risk baseline change.**
[R8-R5 remediation handback](review/phase-5-0-reserved-laboratory-i3-r8-r5-r8-r2-rollback-safety-remediation-handback.md).

**Superseded action, 2026-09-22 — perform the accepted, repository-only
C-P5.0-LAB-I3-R8-R5 remediation and return it for independent Codex review.**
*Superseded by the returned R8-R5 remediation above; the maintainer decisions
recorded here stand.* Peter Duscha accepts Codex's R8-R4 review, wants no R8-R3 rollback, and closes
**LAB-I3-R8-R3-ROLLBACK-1, LAB-I3-R8-R3-WORDING-1,
LAB-I3-R8-R2-GUARD-1, LAB-I3-R8-R2-COUNT-1 and LAB-I3-R8-AGGREGATE-1** on the
recorded terms. The historical guard violation remains recorded but requires no
repeat scan and does not invalidate the underlying R8 evidence. The aggregate's
historical R6 formula and cause remain unknown and non-blocking.

**LAB-I3-R8-R2-ROLLBACK-1 remains Open, Important.** Claude is assigned only
the bounded R8-R5 documentation correction at the head of the handover. Both R6
Blocking findings and I3 remain open; `plan.is_executable=False`; Package 5.0
remains not ready; no action on `oracle-test` is authorized.
[Decision record](review/project-review-2026-09-22-r8-r4-acceptance-and-r8-dispositions.md).

**Superseded action, 2026-09-22 — dispose of the R8-R2 secrets-guard procedural
violation and independently re-review R8-R3/R8-R4.** *Superseded by the
maintainer decisions above. The historical evidence below remains unchanged.*
The prior action was to independently re-review the returned
C-P5.0-LAB-I3-R8 evidence together with the C-P5.0-LAB-I3-R8-R3 and
C-P5.0-LAB-I3-R8-R4 corrections.
Claude has returned one further bounded **repository-only** remediation, this
time of Codex's re-review of the R8-R3 remediation's own rollback and security
wording.

**LAB-I3-R8-R3-ROLLBACK-1 — Open, Important.** The R8-R3 handback §8.1 told an
operator to `git checkout --` the ten documents in its §5 and delete the added
handback, claiming exact restoration of the 93-path pre-remediation state. **The
instruction and the claim are withdrawn as unsafe and unsupported.** All ten
already carried earlier-pass uncommitted work; **no R8-chain content exists at
`HEAD`** (the seven tracked documents stand at **+8,164 / −18** against
`2fb1d6f`, with `R8`, `R8-R1` and `R8-R2` occurring **zero** times in every
committed version), so the command would **erase the entire uncommitted R8
evidence chain**; and three of the ten are **untracked**, where it does not
operate and no baseline for their pre-R8-R3 bytes exists. **It was not
executed**, nothing was reverted and no reverse patch was manufactured. The
truthful rollback now recorded: only the R8-R3-specific hunks and the one file
R8-R3 added may be reversed, through a **reviewed remediation-specific reverse
patch or equivalent exact reconstruction preserving every pre-existing change**;
**the exact pre-R8-R3 bytes are not independently available**, so **no exact
automated rollback is claimed** and any rollback beyond deleting that handback
**requires maintainer coordination**.

**LAB-I3-R8-R3-WORDING-1 — Open, Optional.** R8-R3 §8.1's claim that no
protected file was "read, written **or referenced**" is **withdrawn** as
internally inconsistent — the handback necessarily refers to the three protected
`/tmp` artifacts and their restriction, and **referring to a restriction is not
access**. The evidenced no-access record is preserved unweakened: none was
**read, inspected, `stat`ed, written, moved, modified or reused**, and **no
secret value was disclosed**.

**Unchanged by R8-R4:** every measured value, the four-row table, `c358ea8b…` at
`MANIFEST_VERSION` 17 and `COVERED_SOURCES` 47, `ce275fd3…`, `66855575…`,
`206e40b2…`, the 50-file scope, the 960/612 enumeration, the unresolved cause
and unrecovered R6 procedure. **No measurement was made or claimed**, no
evidence claim strengthened, no rule altered, **no secrets scan run**, **no
guard refusal occurred**, and **no command was issued to `oracle-test`**. **No
scope, schedule or risk baseline change.**
[R8-R4 remediation handback](review/phase-5-0-reserved-laboratory-i3-r8-r4-rollback-safety-and-protected-artifact-wording-remediation-handback.md).

**LAB-I3-R8-R2-GUARD-1 — Open, Blocking, and its disposition is Peter Duscha's
decision.** During C-P5.0-LAB-I3-R8-R2, `guard-secrets.py` **refused** a
proposed secret-indicator scan and the operator then completed substantially the
same check through a differently constructed Python scan. `.agents/AGENTS.md`
states that **a guard refusal is a stop condition, not an obstacle to route
around**; changing the command or the tool did not satisfy that rule, and
**completing the refused check by another construction was a procedural
violation**. The factual record is preserved: the original call was refused;
**no bypass, escalation, protected-file access or secret disclosure is
evidenced**; disclosure was complete at the time; the later scan occurred and
**its output does not cure the violation**. That diff-review check is recorded
**not validly run**. The refused check was **not rerun or reproduced through
another tool**, **no guard or rule was changed**, and this remediation **cannot
close the finding**.

**LAB-I3-R8-R2-COUNT-1 — Open, Important.** The R8-R2 records said the earlier
R8 §3.3 figure and the R8-R1 figure "were each correct under a different,
unstated convention". That is **withdrawn** as misleading: the enumerated **960
are candidate descriptions**, **two** of which reproduce `f4120970…`, while
**one** of the **612 distinct calculations** does. R8 §3.3's "exactly one of 960
candidates" **mixed the units and was ambiguous, indeed wrong, as written**.
Corrections are by **dated erratum or forward-pointing supersession note, not
rewriting**.

**Unchanged and preserved:** the measured hashes, the four-row table, the
review-input digest `c358ea8b…` at `MANIFEST_VERSION` 17 and `COVERED_SOURCES`
47, `ce275fd3…`, `66855575…`, `206e40b2…`, the 50-file scope, the **unresolved**
historical cause and the **unrecovered** R6 procedure, and the distinction
between a **possible explanation** and an **established cause**. **No command
was issued to `oracle-test`**, no new measurement is made or claimed, and no
source, test, hook, manifest, generated artifact, migration, schema or
configuration file was changed. **No scope, schedule or risk baseline change.**

**Nothing is closed:** LAB-I3-R8-R3-ROLLBACK-1 Open, Important;
LAB-I3-R8-R3-WORDING-1 Open, Optional; LAB-I3-R8-R2-GUARD-1 Open, Blocking;
LAB-I3-R8-R2-COUNT-1 Open, Important; LAB-I3-R8-AGGREGATE-1 Open, Important;
PR-20260920-LAB-I3-R6-1 and PR-20260920-LAB-I3-R6-2 **Open, Blocking**; I3
performed but unconfirmed and not closed; V7 excluded; V8 and V10 unperformed;
`plan.is_executable=False`; Package 5.0 not ready. **No action on `oracle-test`
is authorized.**
[R8-R3 remediation handback](review/phase-5-0-reserved-laboratory-i3-r8-r3-guard-disposition-and-count-precision-remediation-handback.md);
[corrected R8-R2 handback](review/phase-5-0-reserved-laboratory-i3-r8-r2-aggregate-precision-remediation-handback.md).

**Superseded action, 2026-09-22 — independently re-review the returned
C-P5.0-LAB-I3-R8 operational evidence together with the C-P5.0-LAB-I3-R8-R2
aggregate-precision correction.** *Superseded by the action above, which records
the guard-refusal procedural violation as LAB-I3-R8-R2-GUARD-1, Open, Blocking,
and withdraws this entry's restatement of the candidate count as one under which
the earlier conflicting figures were each correct. Its account of the withdrawn
"accounted for by the calculation" claim and of the measured values stands.* Claude has returned one further bounded
**repository-only** remediation of Codex's re-review of **LAB-I3-R8-AGGREGATE-1**,
which remains **Open, Important**. Codex found that the R8-R1 correction had
itself overstated its evidence: the R8 erratum, the R8-R1 handback and the
registers said the divergence between the 50-file aggregates `4d829dc6…` (R6,
re-recorded by R7) and `f4120970…` (R8) was *accounted for by the calculation*.
**It is not.** A calculation that reproduces a value is a **possible**
explanation; it does not establish the historical cause and does not recover
R6's formula. **That wording is withdrawn wherever it appeared**, and both the
**cause of the divergence** and the **specific calculation R6 performed** are
now recorded **unresolved**.

What the measurement establishes is unchanged and stands, re-measured locally
on 2026-09-22: **no byte of the measured 50-file set differs between the
records** — review-input digest `c358ea8b…` at `MANIFEST_VERSION` 17,
`COVERED_SOURCES` 47, plus `ce275fd3…`, `66855575…` and `206e40b2…` — so the
divergence **cannot be explained by a change in those bytes**; and both recorded
values are reproducible from exactly those bytes by two calculations differing
only in the ordering key and the trailing-newline rule, which shows the records
*can* diverge with no byte differing. The candidate count is restated under
**one explicit convention**: **960 candidate descriptions** denoting **612
distinct calculations**, with **exactly one distinct calculation reproducing
each recorded value** (`f4120970…` is reached by two descriptions that are the
same calculation, because under a digest-first line format ordering by the whole
line and by the digest coincide). **No command was issued to `oracle-test`**, no
source, test, hook, manifest, generated artifact, migration, schema or
configuration file was changed, the historical R6 aggregate is unrewritten, and
no new target-side measurement is made or claimed. Every R8 operational
observation stands at its measured scope. **No scope, schedule or risk baseline
change.** Nothing is closed: LAB-I3-R8-AGGREGATE-1 remains Open, Important;
PR-20260920-LAB-I3-R6-1 and PR-20260920-LAB-I3-R6-2 remain **Open, Blocking**;
I3 remains performed but unconfirmed and not closed; V7 remains excluded; V8 and
V10 remain unperformed; `plan.is_executable=False`; Package 5.0 remains not
ready. **No action on `oracle-test` is authorized.**
[R8-R2 remediation handback](review/phase-5-0-reserved-laboratory-i3-r8-r2-aggregate-precision-remediation-handback.md);
[corrected R8-R1 handback](review/phase-5-0-reserved-laboratory-i3-r8-r1-aggregate-remediation-handback.md);
[corrected R8 operational handback](review/phase-5-0-reserved-laboratory-i3-r8-controlled-write-handback.md).

**Superseded action, 2026-09-21 — independently re-review the returned
C-P5.0-LAB-I3-R8 operational evidence together with the C-P5.0-LAB-I3-R8-R1
aggregate correction.** *Superseded by the action above, which withdraws this
entry's "accounted for by the calculation" claim and restates the candidate
count; its account of the withdrawn "different line-joining formulas" assertion
and of the measured values stands.* Claude has returned one bounded
**repository-only**
remediation of Codex's evidence-precision finding **LAB-I3-R8-AGGREGATE-1**,
recorded **Open, Important**. The R8 handback had attributed the difference
between the 50-file aggregates `4d829dc6…` (R6, re-recorded by R7) and
`f4120970…` (R8) to "different line-joining formulas"; R6's record states no
joining formula, so that explanation was unproven. **The assertion is withdrawn**
and replaced under a dated erratum by both recorded values, the formula each
record actually documents — R8's completely, R6's as **line format only** — the
limit of the comparison, and a **common-formula calculation reproduced entirely
from local repository files**: over the same 50 files, `<digest>` + two spaces +
`<repository-relative path>` lines joined by `\n`, sorted **by path** with a
**trailing newline** reproduces `4d829dc6…`, and sorted **by whole line** with
**no trailing newline** reproduces `f4120970…`, out of 960 enumerated candidates
with exactly one match each. The input bytes are independently pinned unchanged
(`c358ea8b…`, `MANIFEST_VERSION` 17, and the three recorded individual digests).
**The divergence is therefore accounted for by the calculation, not by any byte
difference**; what calculation R6 actually ran remains **unrecorded and
unresolved**, and is not inferred from a matching value. **No command was issued
to `oracle-test`**, no source, test, hook, manifest, generated artifact,
migration, schema or configuration file was changed, the historical R6 aggregate
is unrewritten, and no new target-side measurement is made or claimed. Every R8
operational observation stands at its measured scope. **No scope, schedule or
risk baseline change.** Nothing is closed: LAB-I3-R8-AGGREGATE-1 remains Open,
Important; PR-20260920-LAB-I3-R6-1 and PR-20260920-LAB-I3-R6-2 remain **Open,
Blocking**; I3 remains performed but unconfirmed and not closed; V7 remains
excluded; V8 and V10 remain unperformed; `plan.is_executable=False`; Package 5.0
remains not ready. **No action on `oracle-test` is authorized.**
[R8-R1 remediation handback](review/phase-5-0-reserved-laboratory-i3-r8-r1-aggregate-remediation-handback.md);
[corrected R8 operational handback](review/phase-5-0-reserved-laboratory-i3-r8-controlled-write-handback.md).

**Superseded action, 2026-09-21 — independently review the returned
C-P5.0-LAB-I3-R8 operational evidence.** *Superseded by the action above, which
carries the same review forward together with the aggregate correction; the R8
evidence itself remains unreviewed and its description below stands.* The
assigned R8 pass ran **unbroken**
and both authorized verifier invocations returned run status `verified`: root
(T1 under V4, §2.3.3 under V5, P2 under temporary canonical `R/bin`), then
`ubuntu` (T6 under V9). All four exclusive-publication contexts verified, every
tracked object was `removed` through its identity guard, 0 barriers and 0
descriptor releases failed, and both final surveys were clean with canonical `R`
absent. **No repository-guard, client, harness, sandbox, classifier or policy
refusal occurred, no escalation or bypass was requested or used, and no
unauthorized host action or auxiliary artifact was created.** The synchronized
tree is the manifest-version-17 tree reproducing review-input digest
`c358ea8b…`. **C-P5.0-LAB-I3-R8 is consumed.** I3 is **performed but remains
unconfirmed and not closed**; closure is Peter Duscha's decision after
independent Codex technical, security and evidence review.
PR-20260920-LAB-I3-R6-1 and PR-20260920-LAB-I3-R6-2 remain **Open, Blocking**;
V7 remains excluded; V8 and V10 remain unperformed; `plan.is_executable=False`;
Package 5.0 remains not ready. **No further action on `oracle-test` is
authorized.**
[R8 operational handback](review/phase-5-0-reserved-laboratory-i3-r8-controlled-write-handback.md).

**Superseded action, 2026-09-21 — Claude executes the exact authorized
C-P5.0-LAB-I3-R8 prompt and stops after handback.** *Superseded by the action
above, which records the completed pass.* Peter Duscha authorizes R8
and assigns Claude as implementing operator. Codex remains the independent
technical, security and evidence reviewer. Authority is confined to the exact
accepted prompt; every repository-guard or tool/harness permission denial is a
terminal event that consumes the pass, with no escalation, bypass, altered
re-issuance or retry. Only the exact plain §3.2 synchronization, necessary
read-only prerequisites and conditional root/`ubuntu` verifier invocations are
released. This does not close I3 or authorize anything outside the prompt.
[Authorized R8 prompt](review/phase-5-0-reserved-laboratory-i3-r8-controlled-write-claude-prompt.md).

**Superseded action, 2026-09-21 — R8 prompt accepted but inactive; explicit
authorization and Claude assignment required.** Peter Duscha accepts the
Codex-prepared C-P5.0-LAB-I3-R8 prompt. Acceptance is not operational authority
and does not assign Claude. R8 remains inactive until Peter separately names
the authority and implementing operator. Codex remains the independent reviewer
of any later operational handback. **No action on `oracle-test` is authorized.**
I3 remains unconfirmed, both R6 Blocking findings remain Open,
`plan.is_executable=False`, and Package 5.0 remains not ready.
[Prompt acceptance](review/project-review-2026-09-21-reserved-laboratory-i3-r8-prompt-acceptance.md);
[accepted inactive prompt](review/phase-5-0-reserved-laboratory-i3-r8-controlled-write-claude-prompt.md).

**Superseded action, 2026-09-20 — maintainer review of the draft
C-P5.0-LAB-I3-R8 prompt.** At Peter Duscha's direction, Codex prepared a fresh operational
prompt for Claude, but it is **inactive**. It treats every repository
guard or tool/harness permission denial as terminal, prohibits escalation,
bypass parameters, re-issuance and retry, and retains the exact plain §3.2
synchronization and reviewed verifier scope. Because Codex authored the draft,
Peter must review and accept it before separately authorizing R8 and assigning
Claude. Codex remains the independent reviewer of Claude's later operation. **No
action on `oracle-test` is authorized.** I3 remains unconfirmed, both R6
Blocking findings remain Open, `plan.is_executable=False`, and Package 5.0
remains not ready.
[Draft R8 prompt](review/phase-5-0-reserved-laboratory-i3-r8-controlled-write-claude-prompt.md).

**Superseded action, 2026-09-20 — R7-R2 accepted and R7 consumed; fresh authority
is required before any future operational pass.** Peter Duscha accepts Codex's
independent review and closes PR-20260920-LAB-I3-R7-R2-1,
PR-20260920-LAB-I3-R7-R1-1 and PR-20260920-LAB-I3-R7-R1-2. This closes the
documentation-remediation findings only: the §12 omission remains a historical
operator process deviation, and the measured identity claim remains limited to
the 50-file review-input set. Peter accepts Codex's recommendation that
**C-P5.0-LAB-I3-R7 is consumed**. Any future operational pass requires fresh,
explicitly bounded maintainer authorization and assignment, including an
express harness-level permission-denial rule. No host authority is created;
I3 remains unconfirmed, both R6 Blocking findings remain Open,
`plan.is_executable=False`, and Package 5.0 remains not ready. **No action on
`oracle-test` is authorized.**
[Acceptance record](review/project-review-2026-09-20-reserved-laboratory-i3-r7-r2-acceptance.md).

**Superseded action, 2026-09-20 — independently re-review the C-P5.0-LAB-I3-R7-R2
count correction; the R7 disposition remains undecided.** Claude has returned
one bounded **repository-documentation-only** remediation of the single finding
from Codex's independent re-review of the R7-R1 remediation.
**PR-20260920-LAB-I3-R7-R2-1 — the R7-R1 handback understates its completed
working-tree count — is recorded Open, Important.** The R7-R1 handback's §2
correctly recorded **85 paths (34 modified, 51 untracked)** at the **start** of
that remediation; its §5 then claimed 85 paths **both before and after**, while
the same handback identified itself as a newly created untracked file. Codex
observed **86 paths (34 modified, 52 untracked)** after completion. §5 is
corrected to distinguish the two states and §2's starting observation is
preserved, giving the progression **84 → 85 → 86**. **A working-tree path count
is a bookkeeping observation about the repository checkout, not an execution
digest**, and this correction adds and withdraws no operational evidence.
**No command was issued to `oracle-test`**, and no source, test, hook, manifest,
generated artifact, migration, schema or configuration file was changed. Every
substantive R7-R1 result stands unaltered: the §12 omission remains an uncured
operational-process deviation, the identity claim remains limited to the
measured 50-file review-input set, the retained hashes match, and the
controlled-place count is seven. **PR-20260920-LAB-I3-R7-R1-1 and
PR-20260920-LAB-I3-R7-R1-2 are not closed here**; their disposition is Codex's
and remains subject to independent re-review. PR-20260920-LAB-I3-R6-1 and
PR-20260920-LAB-I3-R6-2 remain Open, Blocking; I3 remains unconfirmed and not
closed; V7 excluded; V8/V10 unperformed; `plan.is_executable=False`; Package
5.0 not ready. Codex's **recommendation** to treat C-P5.0-LAB-I3-R7 as consumed
remains **a recommendation only; Peter Duscha has not decided the R7
disposition**, which stays open exactly as stated below. **No action on
`oracle-test` is authorized.** This is an action-pointer update, not a roadmap
amendment, a finding closure or execution approval.
[R7-R2 remediation handback](review/phase-5-0-reserved-laboratory-i3-r7-r2-count-remediation-handback.md);
[R7-R1 handback with erratum](review/phase-5-0-reserved-laboratory-i3-r7-r1-erratum-remediation-handback.md).

**Superseded action, 2026-09-20 — independently re-review the
C-P5.0-LAB-I3-R7-R1 documentation remediation; the R7 disposition remains
undecided.** *Superseded as the action pointer by the R7-R2 entry above, which
corrects one count in its handback; **its substantive account and the
maintainer decision it states are not superseded**.* Claude has
returned one bounded **repository-documentation-only** remediation of Codex's
independent review of the R7 stopped-pass handback. **No command was issued to
`oracle-test`**, and no source, test, hook, manifest, generated artifact,
migration, schema or configuration file was changed. A dated erratum was added
to the stopped-pass handback, **preserving its historical account, exact denial
text, command text, timestamps, hashes and the statement that no host command
was issued**, and recording two findings as **Open, Important**:
**PR-20260920-LAB-I3-R7-R1-1**, required Phase 5 context was skipped — the
authorized R7 prompt required §12 (Package 5.0) before acting and the pass's
exhaustive context inventory omits it, recorded as an operator process
deviation that **no later documentation remediation cures**; and
**PR-20260920-LAB-I3-R7-R1-2**, workspace identity exceeded the measured
evidence — the aggregate covers the **50-file review-input set** (47
`COVERED_SOURCES`, two generated artifacts, runner contract r6), not the
complete workspace and not every path the repository-wide synchronization would
have transferred, so the "would have carried" and whole-tree
byte-for-byte claims are **withdrawn** while every hash, the manifest version
and the statement that **no target-side comparison exists** are retained. The
Optional controlled-place count is corrected: **seven documents**, not five.
**Neither finding is closed; only independent Codex re-review may close them.**
Codex **recommends** treating C-P5.0-LAB-I3-R7 as consumed and requiring fresh
authority for a future operational pass — **a recommendation only; Peter Duscha
has not decided the R7 disposition**, which remains open exactly as stated in
the superseded entry below. PR-20260920-LAB-I3-R6-1 and
PR-20260920-LAB-I3-R6-2 remain Open, Blocking; I3 remains unconfirmed and not
closed; V7 excluded; V8/V10 unperformed; `plan.is_executable=False`; Package
5.0 not ready. **No action on `oracle-test` is authorized.** This is an
action-pointer update, not a roadmap amendment, a finding closure or execution
approval.
[Remediation handback](review/phase-5-0-reserved-laboratory-i3-r7-r1-erratum-remediation-handback.md);
[stopped-pass handback with erratum](review/phase-5-0-reserved-laboratory-i3-r7-stopped-pass-handback.md).

**Superseded action, 2026-09-20 — decide whether the R7 stop consumes
C-P5.0-LAB-I3-R7.** *Superseded as the action pointer by the re-review entry
above; **the maintainer decision it states is not superseded and remains
open**.* The assigned R7 pass **stopped before synchronization and
issued no command to `oracle-test`.** Its first synchronization attempt carried
the exact accepted §3.2 command text plus one tool-level parameter the
authorization never named (the Claude Code Bash `dangerouslyDisableSandbox`
flag), and was denied before execution by the Claude Code auto-mode permission
classifier. **No repository guard refused it.** The operator stopped rather than
re-issuing without the flag, because the prompt's guard-refusal clause is
ambiguous as to harness permission denials and because PR-20260920-LAB-I3-R6-1
found that same move Blocking under R6. Nothing occurred on the host: no
synchronization, no prerequisite inspection, neither verifier invocation, no
controlled write, no verifier object and no host-side artifact; the three
protected `/tmp` evidence files were not read or modified. The maintainer
decision is whether this stop consumes R7 or whether the pass may be re-released
for a plain first synchronization attempt. I3 remains unconfirmed and not
closed; PR-20260920-LAB-I3-R6-1 and PR-20260920-LAB-I3-R6-2 remain Open,
Blocking; V7 excluded; V8/V10 unperformed; `plan.is_executable=False`; Package
5.0 not ready.
[Stopped-pass handback](review/phase-5-0-reserved-laboratory-i3-r7-stopped-pass-handback.md).

**Superseded action, 2026-09-20 — Claude performs C-P5.0-LAB-I3-R7 and returns
evidence.** *Superseded by the stopped-pass entry above: the pass was attempted
and stopped before synchronization.* Peter Duscha authorizes the accepted R7 prompt and assigns Claude as
implementing operator. The pass is limited to the exact plain §3.2
synchronization as its first synchronization attempt, necessary read-only
prerequisite inspection, and the exact root verifier followed only on complete
success by the exact `ubuntu` verifier. Any guard refusal consumes the pass; no
auxiliary artifact or manual verifier-object action is authorized. Stop after
the operational handback for independent Codex review. I3 and the two original
R6 Blocking findings remain open pending that review and Peter's later decision.
[Authorized R7 prompt](review/phase-5-0-reserved-laboratory-i3-r7-controlled-write-claude-prompt.md).

**Superseded action, 2026-09-20 — decide whether to authorize C-P5.0-LAB-I3-R7.**
Peter Duscha accepts C-P5.0-LAB-I3-R6-R2 after independent Codex review and
closes PR-20260920-LAB-I3-R6-R1-1. The corrected R7 artifact rule is accepted,
but **R7 remains draft, inactive and not authorized**. The next step is a
separate maintainer decision whether to authorize R7 and explicitly assign its
implementing operator. Until then no host action is authorized.
PR-20260920-LAB-I3-R6-1 and PR-20260920-LAB-I3-R6-2 remain Open, Blocking; I3
remains unconfirmed; R6 remains consumed; V7 remains excluded; V8/V10
unperformed; `plan.is_executable=False`; Package 5.0 not ready.
[R6-R2 handback](review/phase-5-0-reserved-laboratory-i3-r6-r2-artifact-rule-remediation-handback.md);
[draft R7 prompt — not authorized](review/phase-5-0-reserved-laboratory-i3-r7-controlled-write-claude-prompt.md).

**Superseded action, 2026-09-20 — independently re-review the C-P5.0-LAB-I3-R6-R1
remediation; I3 remains unconfirmed and not closed.** Independent Codex review
of the C-P5.0-LAB-I3-R6 operational pass does **not** recommend closing I3 and
raises two **Blocking** findings, both Open:
**PR-20260920-LAB-I3-R6-1**, execution continued after a mandatory guard stop —
the secrets-guard refusal of the first synchronization attempt was a mandatory
stop condition, removing the chaining and re-issuing the exact `rsync` command
did not cure it, and the pass should have ended before synchronization and
before either verifier invocation; and **PR-20260920-LAB-I3-R6-2**, an
unauthorized host write — the `scp` that created `/tmp/fb-i3-r6-filelist.txt`
was outside the R6 authority, and its harmless contents, non-use, disclosure and
preservation do not retroactively authorize it. The R6 handback's claim that no
stop condition fired is **false and withdrawn by erratum**. The verifier runs
**did occur** and returned internally coherent `verified` results, but
**occurrence is not acceptable gate evidence**. Claude has returned a
documentation-only C-P5.0-LAB-I3-R6-R1 remediation that corrects the R6 handback
without erasing its historical commands or results, records both findings Open,
Blocking, and reconciles the controlled documents; it closes neither finding. A
**draft, inactive** C-P5.0-LAB-I3-R7 prompt is prepared and is **not
authorized** — a new operational pass requires Peter's later explicit
authorization and assignment after this remediation is independently reviewed.
No host action is authorized. C-P5.0-LAB-I3-R6 is consumed. V7 remains
excluded; V8/V10 unperformed; `plan.is_executable=False`; Package 5.0 not ready;
LAB-SECRETS-1 Open, Low; LAB-V6-P2 deferred.
[R6-R1 remediation handback](review/phase-5-0-reserved-laboratory-i3-r6-r1-remediation-handback.md);
[draft R7 prompt — not authorized](review/phase-5-0-reserved-laboratory-i3-r7-controlled-write-claude-prompt.md).

**Superseded action, 2026-09-20 — review the returned C-P5.0-LAB-I3-R6
operational evidence and decide I3 closure.** *Superseded by the entry above:
the pass was not accepted on independent review, the closure decision it framed
is not ripe, and its statement of the resulting state is corrected there.
Retained unaltered as the historical record.* Claude performed the bounded pass on
`oracle-test`. **I3 is performed but not closed:** both authorized invocations of
the separately armed verifier returned run status `verified` — the root
invocation (T1 under V4, §2.3.3 under V5, P2 under temporary canonical `R/bin`)
and then the `ubuntu` invocation (T6 under V9). All four contexts verified,
every tracked object was `removed` through its identity guard, every barrier and
descriptor succeeded, and both surveys found 0 verifier names with canonical `R`
absent. Synchronization used the exact accepted inline §3.2 command; the tree is
byte-for-byte the manifest-version-17 tree reproducing `c358ea8b…`, and every
prerequisite was observed unchanged. Two operator effects are disclosed: the
synchronization updated the remote worktree, and an unnecessary `scp` left
`/tmp/fb-i3-r6-filelist.txt`. The next step is independent Codex technical,
security and evidence review, then Peter's closure decision; the operator does
not close I3. No claim is made beyond the four contexts and none about
capability causation. V7 remains excluded; V8/V10 unperformed;
`plan.is_executable=False`; Package 5.0 not ready.
[Handback](review/phase-5-0-reserved-laboratory-i3-r6-controlled-write-verification-handback.md).

**Superseded action, 2026-09-20 — Claude performs bounded C-P5.0-LAB-I3-R6 and
returns evidence.** Peter authorizes C-P5.0-LAB-I3-R6 and assigns Claude as
implementing operator. The pass is limited to the exact accepted §3.2
synchronization, necessary read-only prerequisite inspection, the root verifier
invocation and, only after its complete success, the `ubuntu` invocation. Stop
conditions and all exclusions in the authorized prompt apply. Codex remains the
Independent Reviewer and does not perform the operation. I3 remains unconfirmed
until evidence is returned and reviewed; V7 excluded; V8/V10 unperformed;
`plan.is_executable=False`; Package 5.0 not ready.
[Authorized prompt](review/phase-5-0-reserved-laboratory-i3-r6-controlled-write-retry-claude-prompt.md).

**Superseded action, 2026-09-20 — explicitly authorize the prepared operational
I3 retry, or leave it dormant.** Peter accepts the independent
C-P5.0-LAB-I3-R5 review with no Blocking or Important finding. The repository
target-identity reconciliation is accepted. A bounded Claude prompt for
C-P5.0-LAB-I3-R6 is prepared, but does not authorize host action. Peter must
explicitly authorize that identifier and assign Claude as implementing operator
before SSH, synchronization, inspection, controlled write or verifier
invocation. Until then I3 remains unconfirmed and unperformed; V7 excluded;
V8/V10 unperformed; `plan.is_executable=False`; Package 5.0 not ready.
[Acceptance](review/project-review-2026-09-20-reserved-laboratory-i3-r5-target-identity-acceptance.md);
[draft retry prompt](review/phase-5-0-reserved-laboratory-i3-r6-controlled-write-retry-claude-prompt.md).

**Superseded action, 2026-09-20 — review the implemented target-identity model.**
Claude has implemented **C-P5.0-LAB-I3-R5** in the repository and returned it for
independent Codex technical and security review; **no host action was taken and
none is authorized.** `APPROVED_TARGET_FACTS` gains the explicitly named fact
`kernel_nodename` = `Test`, ordered after the unchanged operational alias
`host="oracle-test"`, and I3 admission compares the observed `os.uname()` tuple
with approved nodename, active kernel and architecture. Runner contract r6
§7.4.2, the review manifest (version 16 → 17) and both generated artifacts were
reconciled deterministically, and seven regression tests were added. The identity
digest moves `ceb58ad1…` → `fc2a9c9b…` and the review-input digest `be9e110f…` →
`c358ea8b…`; the accepted `be9e110f…` is not evidence for this tree and
`c358ea8b…` is review input, not approval or authority for `--execute`. Local
evidence with `TEST_DATABASE_URL` unset: `tests/phase_5_0_evidence` 2649 passed,
0 skipped; guards 41/41. Until the review is accepted, no operational I3
invocation is authorized. I3 remains unconfirmed and unperformed; V7 excluded;
V8/V10 unperformed; `plan.is_executable=False`; Package 5.0 not ready.
[Handback](review/phase-5-0-reserved-laboratory-i3-r5-target-identity-handback.md).

**Superseded action, 2026-09-20 — implement the decided target-identity model in
the repository.** Peter Duscha chooses Option A: keep `host="oracle-test"` as
the operational SSH alias, add the separately approved kernel nodename `Test`,
and compare `os.uname().nodename` with that fact during I3 admission.
C-P5.0-LAB-I3-R5 assigns Claude one bounded repository-only reconciliation of
source, tests, runner contract, manifest and deterministically generated
artifacts, followed by independent Codex technical and security review. No host
action or operational retry is authorized. I3 remains unconfirmed and
unperformed; V7 excluded; V8/V10 unperformed; `plan.is_executable=False`;
Package 5.0 not ready.
[Decision](review/project-review-2026-09-20-reserved-laboratory-i3-target-identity-decision.md);
[implementation prompt](review/phase-5-0-reserved-laboratory-i3-r5-target-identity-claude-prompt.md).

**Superseded action, 2026-09-20 — decide the approved target's identity; I3
refused before the first controlled write.** Claude performed the authorized
C-P5.0-LAB-I3-R4 operational pass on `oracle-test`. **I3 is unconfirmed and was
not performed: no verifier-controlled mutation occurred — the verifier
performed no controlled write and created no verifier object.** The root
invocation of the armed verifier refused admission with `target-mismatch` at
exit `4`, because the target's kernel nodename is `Test` while
`APPROVED_TARGET_FACTS.host` is the SSH alias `oracle-test`; kernel release and
architecture matched exactly. The `ubuntu` invocation was therefore not run.
Synchronization used the exact accepted inline §3.2 command and updated the
remote repository worktree, the synchronized tree is byte-for-byte the accepted
manifest-version-16 tree reproducing digest `be9e110f…`, every prerequisite was
observed unchanged, and no reviewed object was created, removed or altered; the
operator's output redirection left `/tmp/fb-i3-root.out` and
`/tmp/fb-i3-root.err`, which are evidence artifacts outside canonical `R` and
the four publication directories, not verifier residue. The next step is a
maintainer decision on target identity — not an operator fix, because `host` is
hashed into `TARGET_IDENTITY_DIGEST`, the review manifest and
`CONFIRMATION_TOKEN`, so any resolution moves the accepted digest and requires
fresh independent review before a retry. C-P5.0-LAB-I3-R4 is consumed. RAID
LAB-I3-TARGET-1. I3 unconfirmed, V7 excluded, V8/V10 unperformed,
`plan.is_executable=False`, Package 5.0 not ready. Evidence wording corrected
by C-P5.0-LAB-I3-R4-E1, which changes no result and authorizes no host action.
[Handback](review/phase-5-0-reserved-laboratory-i3-r4-controlled-write-blocker-handback.md);
[correction](review/phase-5-0-reserved-laboratory-i3-r4-e1-evidence-precision-correction-handback.md).

**Superseded action, 2026-09-20 — issue fresh bounded operational I3 authority.**
Peter Duscha accepts the independent C-P5.0-LAB-I3-R3 technical/security review
with no finding. The repository reconciliation is accepted, but acceptance
does not itself release host action. The single next step is a fresh explicit
authorization assigning Claude to run the separately armed I3 verifier on
`oracle-test`, against the accepted manifest-version-16 tree, in the reviewed
root invocation followed by the reviewed `ubuntu` invocation, then stop and
return evidence for independent Codex review. The superseded 2026-09-19
authorization is consumed and cannot be reused. Until the fresh release, the
repository-only restriction remains in force. I3 is unconfirmed, V7 excluded,
V8/V10 unperformed, `plan.is_executable=False`, and Package 5.0 not ready.
[Acceptance](review/project-review-2026-09-20-reserved-laboratory-i3-r3-mode-reconciliation-acceptance.md).

**Superseded action, 2026-09-20 — review the implemented mode reconciliation.**
Claude has implemented **C-P5.0-LAB-I3-R3** in the repository and returned it
for fresh independent Codex technical and security review; no host action was
taken. Canonical `R` is created `root:root 0700`, the exclusive-file creation
abstraction takes an explicit creation mode whose default remains `0600`, and
`0500` is passed only by P2's real installation path and the verifier's P2
context; P2 still applies and reads back `root:root 0555` before `linkat`. r6,
the review manifest (version 16), both generated artifacts and the tests were
reconciled. Local evidence: `tests/phase_5_0_evidence` 2642 passed, 0 skipped
with `TEST_DATABASE_URL` unset; guards 41/41. The review-input digest
`be9e110f…` is not an approval and is not authority for `--execute`. Until the
review is accepted, no operational I3 invocation is authorized. I3 remains
unconfirmed, V7 excluded, V8/V10 unperformed, `plan.is_executable=False`, and
Package 5.0 not ready.
[Handback](review/phase-5-0-reserved-laboratory-i3-r3-mode-reconciliation-handback.md).

**Superseded action, 2026-09-20 — reconcile the accepted I3 R2 mode rulings in
one bounded repository-only remediation.** Peter Duscha accepts the independent
C-P5.0-LAB-I3-R2 technical/security review and rules that canonical `R` is
created `0700`, while P2 alone creates its temporary `0500` through an explicit
creation-mode parameter whose default remains `0600` for T1, T6 and §2.3.3.
P2 applies final `0555` before publication. Reconcile source, tests, r6 and
generated artifacts, then return for fresh independent Codex review. No SSH,
synchronization, host inspection, controlled write, database operation,
operational verifier invocation, participant, generated vector, harness or
`--execute` is authorized. I3 remains unconfirmed, V7 excluded, V8/V10
unperformed, `plan.is_executable=False`, and Package 5.0 not ready. [Decision
and accepted review](review/project-review-2026-09-20-reserved-laboratory-i3-r2-acceptance-and-discrepancy-ruling.md).

**Superseded action, 2026-09-19 — implement the consolidated P2/I3 ruling in one
bounded repository-only remediation.** This implementation was independently
reviewed and accepted on 2026-09-20; the two reported mode discrepancies are
governed by the current action above.

**Historical detail — implement the consolidated P2/I3 ruling in one
bounded repository-only remediation.** Peter Duscha rules that P2 installs the
case program `root:root 0555` and relies on the protected-hardlink
filesystem-UID owner condition, not `CAP_FOWNER`. The remediation must
reconcile r6 and the generated plan source to those values, observe P2's actual
operation-time capability masks without treating `CapBnd` as `CapEff`, and
implement the separately armed I3 verifier. Decision B is narrowly amended so
that verifier may temporarily create the canonical `R` and `R/bin` solely for
I3, with reviewed ownership/modes, identity-guarded removal and fail-closed
residue/barrier handling. This action authorizes repository work only: no SSH,
synchronization, host inspection, `/var/lib` creation, capability change,
controlled write or operational verifier invocation. The implementation must
return for independent Codex technical and security review. I3 remains
unconfirmed, V7 excluded, V8/V10 unperformed, `plan.is_executable=False`, and
Package 5.0 not ready. [Decision
record](review/Handover%20information).

**Superseded action, 2026-09-19 — bounded I3 verification assigned to Claude.**
The earlier operator assignment stopped before implementation because the
controlled sources conflicted. Its prompts and handbacks are historical
evidence; the consolidated ruling above replaces their unresolved
P2/`CAP_FOWNER` premise.

**Superseded action, 2026-09-19 — LAB-SECRETS-1 recorded.** Peter Duscha records
LAB-SECRETS-1 as Open, Low for indirect secret references the name-based guard
does not detect, including shell globs resolving to secret filenames and broad
directory copies containing secret files. The governing prohibition in
`.agents/AGENTS.md` remains fully applicable; the hook is defense in depth, not
an authorization boundary. Remediation requires a separately reviewed
fail-closed design that does not expand or read secret paths while inspecting a
proposed command. This issue does not reopen LAB-V6-P3, invalidate R4 or block
Package 5.0. No implementation or host action is authorized.

**Superseded action, 2026-09-19 — R4 synchronization deviation accepted.** Peter
Duscha accepts the explicitly authorized, one-time `--exclude-from`
synchronization deviation used during C-P5.0-LAB-V6-P-R4. The supplied rules
were identical to the runbook exclusions, the maintainer performed the final
synchronization, no secret-type file appeared in the transfer evidence, and
the target matched all 45 reviewed source digests. This acceptance is
retrospective and pass-specific; it does not authorize `--exclude-from` for
future synchronization, which must use the accepted inline runbook command.
[Independent review](review/project-review-2026-09-19-r4-synchronization-deviation.md).
No host action or gate advance is authorized; I3 remains unconfirmed, V7
excluded, V8 and V10 unperformed, `plan.is_executable=False`, LAB-V6-P2
deferred and Package 5.0 **not ready**.

**Superseded action, 2026-09-19 — I12/V6 accepted; V6 closed.** Peter Duscha
accepts the independent review of the I12/V6 evidence and closes V6. Closure
confirms only the approved read-only prerequisite survey. I3 remains
unconfirmed and requires separate authorization; V7 remains excluded, V8 and
V10 remain unperformed, `plan.is_executable` remains false, and Package 5.0
remains **not ready**. Acceptance of the earlier authorized `--exclude-from`
synchronization deviation remained a separate pending decision at this point. [Independent
review](review/project-review-2026-09-19-reserved-laboratory-i12-v6-closure.md).
This is an action-pointer update, not a roadmap amendment or execution approval.

**Superseded action, 2026-09-19 — LAB-V6-P3 accepted and closed.** Peter Duscha
accepts the independent technical and security review of the repository-only
secrets-guard remediation r1 with no Blocking or Important finding, records
his 2026-09-19 instruction as its authorization and closes LAB-V6-P3.
[Independent review](review/project-review-2026-09-19-lab-v6-p3-secrets-guard-remediation.md).
The separate decision about a RAID item for the pre-existing glob/directory-copy
limitation remains pending. V6 closure and acceptance of the earlier authorized
`--exclude-from` synchronization deviation also remained pending at this point. No host action
or gate advance is authorized; `is_executable=False`, LAB-V6-P2 remains
deferred and Package 5.0 remains **not ready**. This is an action-pointer update,
not a roadmap amendment.

**Superseded action, 2026-09-18 — prerequisite provisioning applied; returned for
independent review.** All seven released items — V1, V2, V3, V12, V4, V9, V5 — were applied on `oracle-test` in exact order on 2026-09-18 (22:06–22:07Z), and the read-only I12/V6 verification observed every object matching its reviewed definition. `freedomlab` is gid 986 with `ubuntu` appended (five prior groups retained); the V3 fragment is byte-exact and `systemd-tmpfiles` created `/run/freedom-blades` `0750` and the lock `0660`, both `root:freedomlab`; the provisioning CLI exited 0 with V12, V4, V9, V5 `created` at `2049:1275049`–`1275052`, no refusal, nothing unattempted and no residue. `lifecycle.json` and `.tmp` are absent. **Disclosed deviation:** the secrets guard refuses the runbook §3.2 rsync (its `.env*` exclude matches), so on Peter's authorization the identical rules were supplied via `--exclude-from` and the maintainer ran the sync; the target then matched all 45 reviewed source digests. Proposed RAID LAB-V6-P3 records the guard defect. *Update 2026-09-19:* on Peter's instruction, a repository-only guard remediation (r1) that admits the documented single-quoted §3.2 form is returned for independent Codex review; LAB-V6-P3 stays Open. [LAB-V6-P3 handback](review/phase-5-0-lab-v6-p3-secrets-guard-remediation-handback.md). **Next: independent Codex technical, security and evidence review, then maintainer decision.** V6 performed-but-not-closed until then; I3, V8, V10 unperformed; V7 excluded and absent; `is_executable=False`; LAB-V6-P2 deferred; Package 5.0 **not ready**. [Handback](review/phase-5-0-reserved-laboratory-v6-p-r4-operational-provisioning-handback.md). This is an action-pointer update, not a roadmap amendment or execution approval.

**Superseded action, 2026-09-18 — reviewed prerequisite-provisioning retry
released.** Peter accepts Codex's independent R3 review with no finding, closes
PR-20260918-LAB-V6P-R2-1 and LAB-V6-P1, and authorizes
**C-P5.0-LAB-V6-P-R4**. Claude is assigned as implementing operator to safely
synchronize and inspect `oracle-test`, apply V1, V2, V3, V12, V4, V9 and V5 in
that exact order through the reviewed routes, then perform only read-only
I12/V6 verification and stop for an evidence handback and independent Codex
review. V7, I3, V8, V10, database access, participants, generated-vector
execution, the evidence harness, a real boundary/materializer and `--execute`
remain unauthorized. LAB-V6-P2 remains Open and deferred; V6 remains
performed-but-not-closed; `is_executable=False`; Package 5.0 remains not ready.

**Superseded action, 2026-09-18 — missing provisioning entry point authorized for
bounded repository implementation.** Peter accepts Codex's independent blocker
review and authorizes **C-P5.0-LAB-V6-P-R1**: Claude will add one dedicated,
explicitly armed operator CLI that reaches the reviewed `DirectoryProvisioner`
through `SystemIdentityLookup` and the production `directory_targets()` values,
with safe complete `ProvisioningRun` rendering and operator-surface tests. This
is repository-local authority only. No SSH, synchronization, target inspection,
provisioning, permission/group change, `systemd-tmpfiles`, database operation,
controlled write, generated-vector execution, participant, real boundary or
materializer, or `--execute` is authorized. The implementation returns for
independent Codex technical and security review before a separate operational
release. LAB-V6-P1 remains Open pending that review; LAB-V6-P2 is deferred;
V6 remains performed-but-not-closed, I3 unconfirmed, V7 excluded, V8/V10/I12
unperformed, `is_executable=False`, and Package 5.0 not ready.

**Superseded action, 2026-09-17 — prerequisite provisioning returned unapplied.**
Claude performed the assigned **C-P5.0-LAB-V6-P** pass and **stopped before the
first mutation**, returning the
[handback](review/phase-5-0-reserved-laboratory-v6-p-provisioning-blocker-handback.md)
for independent Codex technical and security review. **Nothing was applied to
`oracle-test`**: all seven released items were observed absent, `ubuntu` retains
the five supplementary groups V6 observed, `/var/lib` is `root:root 0755` on the
ext4 root mount with no group- or other-write bit, both lifecycle names are
absent and `/opt/freedom-blades` is unchanged. The stop is the one the
assignment anticipated — the repository has **no already reviewed operator
invocation** that can drive the directory provisioner as approved (RAID
**LAB-V6-P1**), and the application rules forbid adding source or inventing an
entry point in an operational pass. **I12 was not performed** and V6 remains
performed-but-not-closed; I3 unconfirmed; V7 excluded; V8 and V10 unperformed;
`is_executable=False`; C-7, EH-R16-1, LAB-R6, LAB-X1, P5.0-R5 and OD-62 Open;
Package 5.0 remains not ready. No synchronization, controlled write, generated
vector, real participant, database operation or `--execute` was performed.
**Next action: independent Codex review of the blocker, then maintainer
direction** on how the directory items are to be reached. This is an
action-pointer update, not a roadmap amendment or execution approval.

**Superseded action, 2026-09-17 — Claude assigned prerequisite provisioning.**
Peter assigns **Claude as implementing operator** to apply on `oracle-test` V1,
V2, V3, V12, V4, V9 and V5, in that order, followed only by the read-only
I12/V6 verification. Necessary safe synchronization, inspection and
administrative operations for those items are authorized. **Codex remains the
Independent Reviewer and does not perform the operation.** V7, the I3
controlled-write test, participant wiring, database
access, generated-vector execution, a real participant, the evidence harness,
a real boundary/materializer and `--execute` remain unauthorized. Stop after
returning evidence for independent Codex review; Package 5.0 remains not ready.

**Superseded action, 2026-09-17 — r6 topology-contract correction accepted.**
Peter accepted Codex's independent technical and security
[re-review](review/project-review-2026-09-17-reserved-laboratory-v6-d-r1-contract-correction.md)
with no finding and closed PR-20260917-LAB-V6D-R1-1. This approves no digest,
authorizes no host action and advances no gate. V6 remains
performed-but-not-closed; I3 unconfirmed; V7 excluded; V8, V10 and I12
unperformed; `is_executable=False`; Package 5.0 remains not ready. Repository
work with `TEST_DATABASE_URL` unset remains the active boundary; no SSH,
provisioning, database operation, controlled write, generated-vector execution,
real participant or `--execute` is authorized.

**Superseded action, 2026-09-15 — D1/D2 admission remediation required; V6
decided.** Codex's independent
[re-review](review/project-review-2026-09-15-reserved-laboratory-d1-d2-corrections.md)
raises Blocking PR-20260915-LAB-D12-1: an interrupted lifecycle-record
publication must refuse all seven participants. Peter approves V6 as a
read-only prerequisite survey; it does not prove `linkat` viability or close
I3, and controlled write verification requires separate authorization before
execution. The authorized read-only preflight remains queued behind remediation
and independent re-review. No provisioning, wiring, database operation,
generated-vector execution or `--execute` is authorized.

**Superseded action, 2026-09-15 — D1/D2 applied; independent document review
required.** Peter accepts the scoped same-process trusted-operator model,
approves D1 and D2, and authorizes the documented read-only target preflight.
The approved delta is applied to runner contract r6. Because Codex made the
contract edit, a different Independent Reviewer must review it before the
preflight begins. Provisioning, permission changes, database operations,
generated-vector execution, participant wiring, real execution and `--execute`
remain unauthorized. Package 5.0 remains not ready and P5.0-R5, C-7,
EH-R16-1, OD-62 and LAB-R6 retain their states.

**Superseded action, 2026-09-15 — one-shot authority re-review accepted; maintainer
direction required.** Codex's independent
[re-review](review/project-review-2026-09-15-reserved-laboratory-one-shot-authority.md)
accepts C-P5.0-LAB-I-R2 with no new finding and closes
PR-20260914-LABI-R2-1 within its stated ordinary-object-graph boundary. It does
not create an adversarial same-interpreter security boundary; that would require
a separately approved process-isolation decision. No digest, gate, preflight,
provisioning, wiring or execution is approved. C-7 remains unresolved,
EH-R16-1 Open, all twelve target facts unconfirmed, `is_executable` False,
Package 5.0 not ready, P5.0-R5 Blocking, OD-62 Open, LAB-R6 Open, and D1/D2
proposed. **Next action: maintainer direction.**

**Superseded action, 2026-09-15 — one-shot authority remediation assigned.** Peter
assigns **C-P5.0-LAB-I-R2** through the bounded
[Claude prompt](review/phase-5-0-reserved-laboratory-live-authority-r2-claude-prompt.md)
to remediate Codex's Blocking finding PR-20260914-LABI-R2-1. Issuance must
become a single invocation transition, and the final consuming transition must
depend on invocation-owned state that the callback cannot replace through the
reviewed object graph. The pass retains the two public reproductions, adds
focused issuance and registration-integrity reversals, preserves the accepted
live session/lock/durable-state checks and T2--T17 order, and returns for
independent Codex re-review. Repository changes and local tests with
`TEST_DATABASE_URL` unset only; no SSH, synchronization, host inspection,
preflight, provisioning, database operation, generated-vector execution, real
execution or `--execute` is authorized. C-7 remains unresolved, EH-R16-1 Open,
all twelve target facts unconfirmed, `is_executable` False, Package 5.0 not
ready, P5.0-R5 Blocking, OD-62 Open and LAB-R6 Open. This is an action-pointer
update, not a roadmap amendment or execution approval.

**Superseded action, 2026-09-14 — reserved-laboratory live-authority re-review
returned with changes requested.** Codex's independent
[review](review/project-review-2026-09-14-reserved-laboratory-live-authority.md)
finds the current-session, held-lock and durable T6--T8 checks real, but the
one-shot claim still Blocking. During the same synchronous callback, the
genuine permit can be consumed and `_issue_authority()` called again, or the
mutable `_authority` registration can be replaced with a fully bound permit;
under the same durable start a second armed executor reaches its plan. Two
public synthetic regressions fail with `DID NOT RAISE ExecutorRefused`.
**Next action:** one bounded local remediation of issuance and registration,
then independent Codex re-review. No SSH, synchronization, host inspection,
preflight, provisioning, database operation, generated-vector execution, real
execution or `--execute` is authorized. C-7 remains unresolved, EH-R16-1 Open,
all twelve target facts unconfirmed, `is_executable` False, Package 5.0 not
ready, P5.0-R5 Blocking, OD-62 Open and LAB-R6 Open. This is an action-pointer
update, not a roadmap amendment or execution approval.

**Prior action, 2026-09-14 — reserved-laboratory remediation returned for
independent Codex re-review.** Claude completed **C-P5.0-LAB-I-R1** in one
bounded local pass and returned the
[remediation handback](review/phase-5-0-reserved-laboratory-implementation-remediation-handback.md).
PR-20260913-LABI-1 is repaired by binding the reviewed configuration capture set
at the integration boundary and validating the whole requested set before the
recovery run directory exists; PR-20260913-LABI-2 by making a non-empty
creating-step identity a mandatory prerequisite of every flag and removal effect,
with equality the only admitting branch; and PR-20260913-LABI-3 by wiring the
protocol through `execution/participants.py` for all seven
`PARTICIPATING_ENTRY_POINTS`, the CLI's `--execute` branch, the boundary's
declared descriptor table, and 35 reviewed steps that used to be `/usr/bin/install`
and `/usr/bin/chattr` vectors — `plan.PERMITTED_EXECUTABLES` is now **20**, as
r6 §6.4 requires. Evidence suite **2 165 passed, zero skips**; both reviewer
reproductions failed against the submitted tree and pass now; **13 single-point
reversals each caught**. New review-input digest
`eeafb24c18894835fb92ffbd4ae9e347a315260b4ba4c89e24faf3c76cb58fee`, **review
input only**. D1 and D2 are raised as a
[separately reviewable proposed r6 amendment](review/phase-5-0-reserved-laboratory-r6-d1-d2-proposed-amendment.md);
r6 is unedited and V6 remains unconfirmed. **One assignment item is explicitly
incomplete**: the six non-harness integration points exist and are exercised
locally, and nothing outside the repository calls them, because this
authorization forbids invoking a real participant. **Next action: independent
Codex technical and security re-review.** No SSH, synchronization, host
inspection, preflight, provisioning, database operation, generated-vector
execution, real execution or `--execute` was performed or is authorized. C-7
remains unresolved, EH-R16-1 Open, all twelve target facts unconfirmed,
`is_executable` False, Package 5.0 not ready, P5.0-R5 Blocking and OD-62 Open.
This is an action-pointer update, not a roadmap amendment or execution approval.

**Prior action, 2026-09-14 — reserved-laboratory implementation remediation
assigned.** Peter assigns **C-P5.0-LAB-I-R1** through the bounded
[Claude remediation prompt](review/phase-5-0-reserved-laboratory-implementation-remediation-claude-prompt.md).
The pass must repair Codex's two Blocking binding defects and Important
integration defect, add public failing-before regressions and negative controls,
wire all seven participant paths while retaining the standing real-execution
refusal, retire the old `install`/`chattr` vectors, and return for independent
Codex re-review. D1 and D2 remain proposed contract amendments rather than
silently approved deviations. No SSH, synchronization, host inspection,
preflight, provisioning, database operation, generated-vector execution, real
execution or `--execute` is authorized. C-7 remains unresolved, EH-R16-1 Open,
all twelve target facts unconfirmed, `is_executable` False, Package 5.0 not
ready, P5.0-R5 Blocking and OD-62 Open. This is an action-pointer update, not a
roadmap amendment or execution approval.

**Prior action, 2026-09-13 — reserved-laboratory implementation review
returned with changes requested.** Codex's independent technical and security
[review](review/project-review-2026-09-13-reserved-laboratory-implementation.md)
found two Blocking fail-open defects and one Important integration defect: a
recovery record for a destination restoration must refuse can nevertheless set
`mutation_permitted=True`; missing creating-step identity is treated as an
optional comparison before flag and removal effects; and the new protocol
objects are not connected to the executor, CLI or seven participating entry
points required by C-P5.0-LAB-I. **Next action:** one bounded local remediation
that repairs both bindings, integrates the actual paths, replaces the old
`install`/`chattr` vectors and returns with public regressions and negative
controls for Codex re-review. No SSH, synchronization, host inspection,
preflight, provisioning, database operation, real execution or `--execute` is
authorized. C-7 remains unresolved, EH-R16-1 Open, all twelve target facts
unconfirmed, `is_executable` False, Package 5.0 not ready, P5.0-R5 Blocking and
OD-62 Open. This is an action-pointer update, not a roadmap amendment or
execution approval.

**Prior action, 2026-09-13 — reserved-laboratory mechanism implemented and
returned for independent review.** Claude completed C-P5.0-LAB-I in one bounded
local pass and returned the
[implementation handback](review/phase-5-0-reserved-laboratory-implementation-handback.md).
Runner contract r6 §6.1's mechanism exists in code — the descriptor custody
chain, the four descriptor-relative verbs, the executor's effects behind the
quiescence gate, the independent recovery store with all five ordered barriers,
verify-and-write restoration, the cooperative lock adapter and the two durable
lifecycle objects — together with r6 §7 definitions for V1–V5, V7 and V9, **none
of which is applied**. The mechanism adds no rule: it reuses
`lifecycle_storage`'s validators over a real filesystem rather than restating
them. Evidence suite **2 074 passed, zero skips**; nine single-point reversals
each caught; artifacts regenerated four times through the non-executing CLI with
all 42 covered hashes independently recomputed. New review-input digest
`aabba2d718f5c0231c2b92b177e733fca7e6ce3c5c85283dda4730b14c3c91d4`, review input
only. Three items are raised for a ruling: the `linkat`/`unlinkat` substitute
for an unreachable `RENAME_NOREPLACE`; the listing descriptor §1.3.3 does not
enumerate; and `PERMITTED_EXECUTABLES` staying at 22 rather than §6.4's 20.
**Next action: independent Codex technical and security review.** No SSH,
synchronization, inspection, preflight, provisioning, permission change,
database operation, real boundary/materializer use, generated-vector execution
or `--execute` was performed or is authorized. C-7 remains unresolved, EH-R16-1
Open, the twelve target facts unconfirmed, `is_executable` False, Package 5.0
not ready, P5.0-R5 Blocking and OD-62 Open. This is an action-pointer update,
not a roadmap amendment or execution approval.

**Prior action, 2026-09-13 — bounded reserved-laboratory repository
implementation authorized.** Peter authorizes C-P5.0-LAB-I: implement the
accepted r6 mechanism and the bounded code required to address C-7 and
EH-R16-1, with repository changes and local tests only. The active assignment is
the [Claude implementation prompt](review/phase-5-0-reserved-laboratory-implementation-claude-prompt.md).
No SSH, synchronization, disposable-server inspection, preflight, provisioning,
permission change, database operation, real boundary/materializer use,
generated-vector execution or `--execute` is authorized. Claude returns a
handback and stops for independent Codex technical and security review. C-7 and
EH-R16-1 remain unresolved meanwhile; the twelve target facts remain
unconfirmed, `is_executable` remains False, Package 5.0 remains not ready,
P5.0-R5 remains Blocking and OD-62 remains Open. This is an action-pointer and
bounded implementation authorization, not a roadmap amendment or execution
approval.

**Prior action, 2026-09-13 — LAB-1 local remediation accepted; existing
operational blockers remain.** Codex's independent R3 re-review found no
residual defect and accepts PR-20260912-LAB1-2 in the reviewed local scope
([review](review/project-review-2026-09-13-lab1-rereview-r3.md)). LAB-1's local
remediation is closed. This changes no operational gate: C-7 remains unresolved,
EH-R16-1 remains Open, `is_executable` remains False, the twelve target facts
remain unconfirmed, Package 5.0 remains not ready, package-level P5.0-R5 remains
Blocking, and OD-62 remains Open. The next action is maintainer direction on
those existing blockers; no execution is authorized. This is an action-pointer
update, not an effective roadmap amendment.

**Prior action, 2026-09-13 — LAB-1 raw read-back byte binding correction
returned for Codex re-review.**

Claude answered PR-20260912-LAB1-2 in one bounded local pass
([handback](review/project-review-remediation-2026-09-13-lab1-r2-handback.md)).
**Repaired in pure code, four lines of behavior in one module:**
`write_run_record` consumed the destination's bytes in the same expression that
parsed them, so the comparison that followed saw only the parsed mapping and a
fresh canonical re-serialization of it — both statements about what a reader made
of the file, neither about the file. Added whitespace and a duplicate
`schema_version` key resolving to the same value were therefore accepted through
the public writer. The bytes `destination.read_bytes()` returns are now
**retained** and compared directly with `serialized`, as the first and
short-circuiting conjunct of the one named comparison, whose inputs now include
the raw bytes. The completed path establishes three distinct claims — the bytes
read back are the bytes written, they parse as the expected document, and the
document satisfies the exact per-cause canonical recovery contract — and no path
returns a written artifact without all three. Refusals stay fixed and bounded.
**No schema moves:** this is a writer implementation fix, a valid schema-3
document means what it meant before, so the run-record schema stays at **3**, the
supplied-observation schema at **3** and the review manifest at **10**; only
`artifact.py`'s pinned hash moved. The regressions were added first and run
against the submitted tree: **12 failed**, every one `DID NOT RAISE`, including
both reviewer reproductions. After the correction the run-record module is
**121 passed** (+28 nodes) with whitespace, re-indentation, duplicate top-level
and duplicate nested-key rows, the four accepted cleanup-cause combinations, and
a control that removes **only** the raw conjunct and accepts all ten collapsing
tampers again. Focused LAB-1 files **260 passed**; structural no-execution suite
**217 passed**; complete synthetic harness **1,936 passed, zero skips**;
reversing the repair in a scratch copy fails **24**, of which 12 are behavioral.
The review-input digest is now
`6ef61afbaa96dcbd5eda408eed5042aff3a227ce32cb56b149111e531f7a2408`, replacing
`3b50e8f7adb309549aa1e69a61e9ddce1ce5bf11429eecc002f427b773df98a3`; it is review
input only and must not be passed to `--execute`. **Next action: Codex
independent technical re-review** — LAB-1 is not closed by the session that
repaired it. No SSH, synchronization, host inspection, preflight, permission
change, provisioning, database operation or real execution was performed or
authorized. C-7 remains unresolved, EH-R16-1 remains Open, `is_executable`
remains `False`, twelve target facts remain unconfirmed, Package 5.0 remains not
ready, package-level P5.0-R5 remains Blocking and OD-62 remains Open. This is an
action-pointer update, not an effective roadmap amendment.

**Prior action, 2026-09-12 — LAB-1 remediation R2 re-review returned with
changes requested.** Codex found one Important residual read-back defect,
PR-20260912-LAB1-2: the writer parses the bytes read back and compares the
mapping and a fresh canonical re-serialization, but never compares the raw bytes
read with the bytes written. Added whitespace and a duplicate key resolving to
the same value were both accepted through the public writer. The exact per-cause
canonical procedure checks and schema-version-3 transition are sound in the
reviewed scope. Next: one bounded local raw-byte equality correction and public-
writer regressions, then Codex re-review. See the
[R2 re-review](review/project-review-2026-09-12-lab1-rereview-r2.md). No SSH,
synchronization, host inspection, preflight, permission change, provisioning,
database operation or real execution is authorized. LAB-1 remains open; C-7
remains unresolved; EH-R16-1 remains Open; `is_executable` remains `False`;
Package 5.0 remains not ready; package-level P5.0-R5 remains Blocking; and OD-62
remains Open. This is an action-pointer update, not an effective roadmap
amendment.

Claude's bounded assignment for that next action was the
[2026-09-13 raw read-back byte binding prompt](review/project-review-remediation-2026-09-13-lab1-r2-claude-prompt.md).
It added no permission and changed no gate. *Answered 2026-09-13 by the handback
named in the current action above.*

**Prior action, 2026-09-12 — LAB-1 run-record binding correction returned for
Codex re-review.**

Claude answered PR-20260912-LAB1-1 in one bounded local pass
([handback](review/project-review-remediation-2026-09-12-lab1-handback.md)).
**Repaired in pure code:** the schema-2 run record checked the residue-recovery
procedure's shape and order and compared its content with nothing, so an
arbitrary ordered replacement was accepted on read-back. The reader now requires
the exact canonical procedure for each **present** cause — residue requires
`journal.RECOVERY_PROCEDURE`, retained recovery inputs require
`cleanup.RECOVERY_PROCEDURE`, an absent cause requires an empty procedure, and
neither answers for the other — refuses missing, additional and unknown keys, and
compares the whole document read back with the document written, mapping and
bytes. The **run-record schema is version 3**, because an arbitrary procedure was
a valid version-2 record and is not a valid version-3 one; a version-2 record
refuses by name. The **supplied-observation schema stays at version 3** and the
**review manifest at version 10**: the manifest does not declare the run-record
document contract. The reviewer's reproduction failed against the submitted tree
and passes after the correction; the focused module is **93 passed** with a
37-node substitution, cause/presence and read-back matrix and two negative
controls, and reversing the repair on a scratch copy fails 26 of the complete
harness. Focused LAB-1 files **232 passed**; complete synthetic harness
**1,908 passed, zero skips**. The review-input digest is now
`3b50e8f7adb309549aa1e69a61e9ddce1ce5bf11429eecc002f427b773df98a3`, replacing
`af3181ed276f61a89a51b25afcbfb91f7a4c938b21a5bf83c1ff53f8b3764821`; it is review
input only and must not be passed to `--execute`. **Next action: Codex
independent technical re-review** — LAB-1 is not closed by the session that
repaired it. No SSH, synchronization, host inspection, preflight, permission
change, provisioning, database operation or real execution was performed or
authorized; the separately completed pytest installation on `oracle-test`
broadens none of them. C-7 remains unresolved, EH-R16-1 remains Open,
`is_executable` remains `False`, twelve target facts remain unconfirmed, Package
5.0 remains not ready, package-level P5.0-R5 remains Blocking and OD-62 remains
Open. This is an action-pointer update, not an effective roadmap amendment.

**Prior action, 2026-09-12 — LAB-1 re-review returned with changes
requested.** Codex found one Important run-record integrity defect: schema 2
checks the residue-recovery procedure's shape and order but not its exact
content or correspondence to residue, so an arbitrary ordered replacement is
accepted on read-back. Claude next corrects that binding and adds substitution
and cause/presence regressions, then returns the bounded local repair for Codex
re-review. See
[`project-review-2026-09-12-lab1-rereview.md`](review/project-review-2026-09-12-lab1-rereview.md)
and the bounded
[`Claude remediation prompt`](review/project-review-remediation-2026-09-12-lab1-claude-prompt.md).
The maintainer separately authorized installing the declared pytest packages on
the disposable server; pytest 8.4.2 is now present in the canonical virtualenv.
That completed operation authorizes no synchronization, host test execution,
preflight or provisioning.
All local-only restrictions and open gates remain unchanged.

**Prior action, 2026-09-12 — maintainer decisions recorded; LAB-1 repair
reviewed, corrected, and awaiting Codex re-review.** Peter chose one shared
`ubuntu` identity for all seven participants, accepted the exact r6 §7 ten-item
delta as the lab design, and accepted the bounded LAB-1 correction. The repair is
local only: S-B recovery procedures are reported separately by cause and encoded
in the run record.

A review of that implementation found three defects and repaired them. The
accepted §8.1 clause — *the procedure that applies to the state it reached* — was
**not** what the first pass implemented: one boolean over both procedures let a
residue-bearing run satisfy the clause by naming the configuration recovery,
which is LAB-1's own shape moved into the evidence record. The clause is now
compared per cause, which raises the supplied-observation schema to **version 3**
and the review manifest to **version 10**. The submitted negative control
bypassed the derivation it was meant to constrain, and both the hardcoded
derivation and a gutted run-record encoder left the harness green; five controls
and round-trip tests now fail on each. The S-B message named no procedure at
all, so the operator reading a non-zero exit never saw the recovery the record
carried; it now names the procedure each present cause calls for. The
review-input artifacts were stale and have been regenerated. Focused tests
**195 passed**; the complete synthetic evidence harness **1,871 passed, zero
skips**. See the [decision and remediation
note](review/project-review-2026-09-12-lab1-disposition.md).

The review-input digest is now
`af3181ed276f61a89a51b25afcbfb91f7a4c938b21a5bf83c1ff53f8b3764821` because
covered source changed; it replaces
`2fa1d13b7b112f7fda837abcdd70f86ff6d85701602818d810af5fc2141ce5ca`, is review
input only, and must not be passed to `--execute`.

The identity choice is not the V10 preflight observation: whether all seven
entry points actually run as `ubuntu` remains unconfirmed. V6 and V8 are likewise
unperformed. The ten-item delta is accepted as design, **not applied**. The
active local-only restriction bars SSH, synchronization, host inspection,
preflight, permission changes, provisioning, database work and real execution.
C-7 remains unresolved; EH-R16-1 remains Open; `is_executable` remains `False`;
Package 5.0 remains not ready, package-level P5.0-R5 remains Blocking, and OD-62
remains Open. Phase 5 product work and operational gates do not advance on these
design decisions. **Next action: Codex technical re-review** of the LAB-1 repair
and of the schema and manifest version changes it entails. Codex implemented the
first LAB-1 pass, which inverted the normal division of work; Claude reviewed and
remediated it and Codex re-reviews, restoring it. No session closes a finding on
work it produced.

**Completed action, 2026-09-12 — R5 remediation re-review.** The independent
[Codex review](review/project-review-2026-09-12-r5-closure.md) found the r6
reservation-to-harness binding technically sound in the reviewed scope. Per the
maintainer's disposition, PR-20260911-R5-1 and its dependent findings
PR-20260911-R4-2 and PR-20260911-R4-3 are **closed**. R4-1 retains its prior
positive technical recommendation and is not closed here. Focused R3/R4/R5
regressions: **192 passed**; structural no-execution suite: **217 passed**;
complete synthetic harness: **1859 passed, zero skips**. No host, database,
provisioning, preflight, privileged, or real execution check ran.

**At re-review completion, the pending action was maintainer disposition** of
runner contract r6 §7's ten-item
permission/provisioning delta, V10's participant-identity question, and LAB-1's
classification. At that point the ten delta items had no disposition; the actual
V10 fact was unconfirmed and LAB-1 was unrepaired. The three C-7 cases remained
unresolved,
`is_executable` remains `False`, twelve target facts remain unconfirmed, and
EH-R16-1 remains Open with the real-execution refusal in force. Package 5.0
remains not ready, package-level P5.0-R5 remains Blocking, and OD-62 remains Open.
This action-pointer update changes no roadmap requirement or package gate and
approves no provisioning, permission change, host action, execution digest, or
product implementation.

**Prior action, 2026-09-11 — R5 binding remediation assigned.** Claude follows
the [bounded prompt](review/project-review-remediation-2026-09-11-r5-claude-prompt.md)
for [PR-20260911-R5-1](review/project-review-2026-09-11-r5.md): durably bind the
harness start to its reservation and require exact agreement through the release
request/publication and completion evidence on writer and reader paths. Submit
runner contract r6 and connected synthetic regressions, then return to Codex for
technical re-review. No privileged mechanism, operational integration,
provisioning, preflight or execution is approved. Package 5.0 remains not ready,
P5.0-R5 Blocking, OD-62 Open and EH-R16-1 Open. This pointer changes no roadmap
requirement or package gate.

**Prior action, 2026-09-11 — R5 technical re-review returned.** The
[independent re-review](review/project-review-2026-09-11-r5.md) requests one
bounded correction: bind the harness's stored start to the reservation it owns
and require that binding to agree with the release request, release publication,
completion evidence and run file. The present model permits a release of A to
settle an already-started harness run B. The stale-transition repair is
positively reviewed within its scope, and the cross-participant, omitted-ledger
and terminal-order repairs work as far as they go, but R4-2 and R4-3 remain open
pending this binding. Next is bounded local remediation followed by Codex
re-review. No privileged implementation, provisioning, preflight, host action
or execution is approved. Package 5.0 remains not ready, P5.0-R5 Blocking,
OD-62 Open and EH-R16-1 Open. This pointer changes no roadmap requirement or
package gate.

**Prior action, 2026-09-11 — R4 lifecycle validation and ordering remediation
returned.** Claude answered all three findings of the
[R4 re-review](review/project-review-2026-09-11-r4.md) in one bounded local pass
([handback](review/project-review-remediation-2026-09-11-r4-handback.md),
submitted [runner contract r5](review/phase-5-0-reserved-laboratory-runner-contract-r5.md),
which supersedes r4). **Repaired in pure code:** reservation transitions are
validated against the **current reservation** and its current state over the
accepted transition table, so a stale terminal entry no longer retires a newer
run (R4-1); and one participant-history validator binds run, participant,
identity, filename and evidence content to the stored start, with the ledger
required rather than optional (R4-2). Both run before an append and on read.
**Corrected in the model and still unbuilt:** the terminal publication order
(R4-3) — release decision, durable RELEASED publication, then the harness's own
completion, with its two conditions derived from those operations and the
still-started ledger entry blocking reuse between them. The permission and
provisioning delta is **unchanged at ten items** and all remain **unapproved**.
**Next action: Codex technical re-review**, then Peter on r5 §7's delta, on V10's
identity question and on LAB-1's classification. The three C-7 cases remain
declared unresolved, `is_executable` remains `False`, the twelve target facts
remain unconfirmed and the real-execution refusal is retained while EH-R16-1 is
open. The review-input digest is now
`39cea2904f66606a66664f6835633a83a57780f4edc3570d6e8a3942edd196cd`
because covered source changed; it is review input only and must not be passed to
`--execute`. Package 5.0 not ready, P5.0-R5 Blocking, OD-62 Open, EH-R16-1 Open.
This is an action-pointer update, not an effective roadmap amendment, and it
approves no provisioning, permission change, host action, execution digest or
product implementation.

**Prior action, 2026-09-11 — R4 remediation assigned.** Claude follows the
[bounded prompt](review/project-review-remediation-2026-09-11-r4-claude-prompt.md)
for the [R4 findings](review/project-review-2026-09-11-r4.md): repair pure
reservation and participant history validation, require ledger evidence and
correct terminal-publication order. Submit runner contract r5 and connected
synthetic regressions in one handback to Codex. No privileged mechanism,
operational integration, provisioning, preflight or execution is approved.
Package 5.0 remains not ready, P5.0-R5 Blocking, OD-62 Open, EH-R16-1 Open.
This pointer changes no roadmap requirement or package gate; history follows.

**Prior action, 2026-09-11 — R4 review returned, changes requested.** The
[independent review](review/project-review-2026-09-11-r4.md) records two Blocking
findings in reservation transitions and participant-history binding, and one
Important finding in completion/release ordering. The target/attribution repair
and successor durability step receive positive recommendations in their bounded
scope. Next: local remediation and Codex re-review before privileged
implementation or permission decisions. Package 5.0 remains not ready, P5.0-R5
Blocking, OD-62 Open, EH-R16-1 Open. No host action, provisioning, preflight,
execution or roadmap amendment is approved; prior submissions remain below.

**Prior action, 2026-09-11 — R3 complete lifecycle remediation returned.**
Claude answered all three findings of the
[R3 re-review](review/project-review-2026-09-11-r3.md) in one connected pass
([handback](review/project-review-remediation-2026-09-11-r3-handback.md),
submitted [runner contract r4](review/phase-5-0-reserved-laboratory-runner-contract-r4.md),
which supersedes r3). **Repaired in code:** the binding between stored evidence
and admission (PR-20260911-R3-3) — the approved target, the first-use attester
and basis and the recovery's author are now carried and required for every
admitting disposition, through a bounded versioned record schema, a parser and
the one shared validator, and `BINDING_MISMATCH` gained its enforcing branch.
**Submitted, modelled and not built:** the publication/restart correction
(R3-1), where every successor re-establishes the record's durability under the
lock or refuses, needing read permission and no write permission; and durable
in-progress/completion accounting for all seven participants (R3-2), where an
interrupted run of any of them blocks every successor including the harness and
the environment reset. r3's crashed-suite exemption is withdrawn. Two connected
lifecycle traces read the bytes their predecessors wrote, and the earlier
end-to-end claim over a constructed history is withdrawn. The permission and
provisioning delta **grew** to ten items, adding V9 and V10; all remain
**unapproved**. **Next action: Codex technical re-review**, then Peter on r4
§7's delta, on V10's identity question and on LAB-1's classification. The three
C-7 cases remain declared unresolved, `is_executable` remains `False`, the
twelve target facts remain unconfirmed, the operational-ineligibility control is
unchanged, and the real-execution refusal is retained while EH-R16-1 is open.
The review-input digest is now
`45b3c6c0313e5cb8b48e116aea7716b47f1a2d231f12719975d63166d3458201` because
covered source changed; it is review input only and must not be passed to
`--execute`. Package 5.0 not ready, P5.0-R5 Blocking, OD-62 Open, EH-R16-1 Open.
This is an action-pointer update, not an effective roadmap amendment, and it
approves no provisioning, permission change, host action, execution digest or
product implementation.

**Prior action, 2026-09-11 — complete lifecycle remediation assigned.** Peter
agreed to address the [R3 findings](review/project-review-2026-09-11-r3.md) in one
connected lifecycle pass. Claude follows the [bounded prompt](review/project-review-remediation-2026-09-11-r3-claude-prompt.md):
submit runner contract r4, pure validation repairs and synthetic tests that read
stored records through initialization, operation, crash, recovery and successor
admission. Return one handback to Codex for technical re-review. No real writer,
privileged mechanism, lock adapter, operational integration, provisioning,
preflight or execution is approved. Package 5.0 remains not ready, P5.0-R5
Blocking, OD-62 Open, EH-R16-1 Open. This pointer changes no roadmap requirement
or package gate. Prior submissions remain below.

**Prior action, 2026-09-11 — R2 remediation returned to Codex.** Claude
answered all four findings of the
[September 11 re-review](review/project-review-2026-09-11-r2.md) in one bounded
local pass ([handback](review/project-review-remediation-2026-09-11-r2-handback.md),
submitted [runner contract r3](review/phase-5-0-reserved-laboratory-runner-contract-r3.md),
which supersedes r2). **Repaired in code, one finding only:** the decision API's
lifecycle validation, which now validates the durable record as a coherent whole
before any admitting branch is chosen, so a contradictory record refuses rather
than being resolved in favour of reuse (PR-20260911-R2-1); the same repair closes
a malformed-value fall-through the local reproduction found. **Submitted and not
built:** the descriptor contract and complete durability barrier graph (R2-2),
the corrected post-unlink evidence claim (R2-3), and one allowlist of validated
lifecycle outcomes for all seven participants with verified-first-use
provisioning (R2-4), each carrying a bounded synthetic proposal model with
deliberately failing controls. The permission and provisioning delta **grew** to
eight items, adding the initial lifecycle record and one preflight fact; all
remain **unapproved**. The C1 → C2 → C5 ordering correction and the withdrawn
JNL-47 criterion split are preserved and not reopened, and **no criterion
decision is requested**. LAB-1 remains Important and unrepaired, its reproduction
unweakened. **Next action: Codex technical re-review**, then Peter on r3 §7's
delta and on LAB-1's classification. The three C-7 cases remain declared
unresolved, `is_executable` remains `False`, the twelve target facts remain
unconfirmed, the operational-ineligibility control is unchanged, and the
real-execution refusal is retained while EH-R16-1 is open. The review-input digest
is now `55af840fbb28f0ea8ae447e732644c5b2f81dace83f6ccd499f24ebc8864cff2` because
covered source changed; it is review input only and must not be passed to
`--execute`. Package 5.0 not ready, P5.0-R5 Blocking, OD-62 Open, EH-R16-1 Open.
This is an action-pointer update, not an effective roadmap amendment, and it
approves no provisioning, permission change, host action, execution digest or
product implementation.

**Prior action, 2026-09-11 — Codex re-review returned, changes requested.**
Claude's bounded assignment is the
[R2 remediation prompt](review/project-review-remediation-2026-09-11-r2-claude-prompt.md),
covering pure lifecycle validation, runner contract r3 and synthetic models.
The [independent re-review](review/project-review-2026-09-11-r2.md) identifies
two Blocking findings in lifecycle consistency and recovery durability, plus
two Important findings in cleanup detection and lifecycle storage. The corrected
evidence ordering receives a positive recommendation for the bounded model.
Next is local remediation followed by Codex re-review. Package 5.0 remains not
ready, P5.0-R5 Blocking, OD-62 Open and EH-R16-1 Open. No permission expansion,
privileged implementation, preflight or execution is approved. This pointer
changes no roadmap or package gate; prior submissions remain below.

**Prior action, 2026-09-11 — September 11 remediation returned.** Claude
answered all six findings of the [September 11 review](review/project-review-2026-09-11.md)
in one bounded local pass
([handback](review/project-review-remediation-2026-09-11-handback.md), submitted
[runner contract r2](review/phase-5-0-reserved-laboratory-runner-contract-r2.md),
which supersedes revision 1). Repaired locally: the evidence ordering model, which
now runs C1 including its cleanup, then C2, then C5's publication through an
injected sink (PR-20260911-5), and the decision API's admission, release and
transition guards (PR-20260911-3, -4). Submitted and **not built**: effect
ownership, independent recovery and the lock/lifecycle storage (PR-20260911-1,
-2, -6), with an explicit **non-zero** permission delta — one system group, one
group membership, one `systemd-tmpfiles` fragment, four provisioned paths and a
second `ctypes` exception; revision 1's zero-delta claim is withdrawn. **The
`JNL-47-RECOVERY-STATE` criterion split is withdrawn** and no criterion decision
is required. **Next action: Codex technical review**, then Peter on the contract's
§7 provisioning delta and on LAB-1's classification. The three C-7 cases remain
declared unresolved, `is_executable` remains `False`, the twelve target facts
remain unconfirmed, the operational-ineligibility control is unchanged, and the
real-execution refusal is retained while EH-R16-1 is open. The review-input digest
is now `e6d42228f5ccc4fd5eebc0861bb97eec42bbf16705d1aa209de5464e194bdba1` because
covered source changed; it is review input only and must not be passed to
`--execute`. Package 5.0 not ready, P5.0-R5 Blocking, OD-62 Open. This is an
action-pointer update, not an effective roadmap amendment, and it approves no
provisioning, permission change, host action, execution digest or product
implementation.

**Superseded action pointer, 2026-09-11 — reserved laboratory remediation returned.** Claude
returned the consolidated C-P5.0-LAB-1 handback
([handback](review/phase-5-0-reserved-laboratory-handback.md), submitted
[runner contract](review/phase-5-0-reserved-laboratory-runner-contract.md)). It
carries the separate CRP fix for PR-20260910-R2-1, the three C-7 producer
dispositions with bounded local evidence-only producers, the reservation and
admission decision mechanism, and a **zero** permission delta; the EH-R16-1
remedy's exact implementation and syscall diff is submitted for review, not
built. **Next action: Codex technical review**, then Peter's decision on the one
submitted readiness-versus-implementation criterion split for
`JNL-47-RECOVERY-STATE` and on the classification of new finding **LAB-1**. The
three C-7 cases remain declared unresolved, `is_executable` remains `False`, the
twelve target facts remain unconfirmed, the operational-ineligibility control is
unchanged, and the real-execution refusal is retained while EH-R16-1 is open. The
review-input digest is now
`bbb3854fbdffae00696544465f1cd7bbdf22ad18583056490a6735444800e4fa` because
covered source changed; it is review input only and must not be passed to
`--execute`. Package 5.0 not ready, P5.0-R5 Blocking, OD-62 Open. This is an
action-pointer update, not an effective roadmap amendment, and it approves no
criterion split, host action, execution digest or product implementation.

**Standing laboratory direction, 2026-09-10 — C-P5.0-LAB-1.** Peter authorized proceeding
with an exclusively reserved disposable laboratory, trusted host administrators
and scoped adversarial tests. The [impact assessment](review/phase-5-0-reserved-laboratory-direction.md)
and [Claude remediation prompt](review/phase-5-0-reserved-laboratory-claude-prompt.md)
replace VM expansion as the next action. Claude resolves the three C-7 producer
dispositions, implements bounded local admission/evidence work and separately
fixes PR-20260910-R2-1, then returns to Codex. ADR 0011 remains Proposed and is
deferred from this critical path. No host action, execution digest, criterion
waiver, production control change or Package 5.0 implementation is approved.
Any necessary readiness-versus-implementation criterion split is submitted
explicitly for decision. Package 5.0 not ready, P5.0-R5 Blocking, OD-62 Open.
The VM-revision next action below is superseded; its review history is retained.

**Historical evidence-harness action, 2026-09-10.** Claude delivered the independent
design review of the proposed VM evidence boundary:
[VM evidence boundary independent review](review/phase-5-0-evidence-vm-independent-review.md).
Disposition **changes requested**, with five Blocking findings (VM-1 … VM-5), ten
Important and three Optional. The review recommends, for Peter's decision and
without accepting anything, that Package 5.0's evidence be completed on the
already approved disposable target using the bounded C-8 revision 3 §9.2
mechanism, and that ADR 0011 be held as the target architecture for a later slice
off Package 5.0's critical path. **Next action: Codex revises the design and ADR
0011 against VM-1 … VM-5, documentation only**, then returns for the decision
requests in review §G. ADR 0011 remains **Proposed**. No implementation, host
inspection, feasibility probe, image build, VM creation or execution is
authorized. EH-R16-1 and PR-20260910-1/2/3 remain open; Package 5.0 not ready,
P5.0-R5 Blocking, OD-62 Open, current plan `is_executable=False`. This is an
action-pointer update, not an effective roadmap amendment.

**Superseded action pointer, 2026-09-10.** Following the September 10
review's three findings against C-8 revision 3, the maintainer requested a
simpler alternative. Codex submitted proposed
[ADR 0011](adr/0011-disposable-vm-evidence-boundary.md) and the
[VM lifecycle design](review/phase-5-0-evidence-vm-design.md). The explicit
**Claude independent design-review prompt** is in
`docs/review/Handover information`. Claude reviews; Codex authored the proposal;
Peter retains acceptance authority. Design preparation and this review are
authorized, but the VM architecture, management surface, target, resource and
retention limits remain unaccepted. No implementation, host feasibility check,
VM/image creation or execution is authorized by this update. EH-R16-1 and
PR-20260910-1/2/3 remain open; Package 5.0 not ready, P5.0-R5 Blocking and OD-62
Open. This is an action-pointer correction, not an effective roadmap amendment.

**Historical evidence-harness review, 2026-09-09.** Codex's R16 independent
review of the C-6/C-7/C-8 submission returned **changes requested**, with
EH-R16-1/2 Blocking and EH-R16-3/4 Important. The active bounded remediation
prompt is in `docs/review/Handover information`; findings and independent
verification are in
`docs/review/phase-5-0-evidence-harness-r16-independent-review.md`.
Existing remediation authorization persists. The later read-only target
preflight is already authorized and assigned to Codex after implementation
review, but remains unperformed. No execution digest is approved. Package 5.0
remains not ready, P5.0-R5 Blocking and OD-62 Open. This update changes no
roadmap, package gate or production authorization. Earlier runtime rulings below
remain binding; their handoff pointers are historical.

**Current evidence-harness runtime ruling, 2026-09-06.** Peter Duscha accepted
Codex's recommendation for R10 conflict C-2, **Option B**: the bounded reviewed
case program runs through an explicitly named documented Python 3.12
interpreter with `-I -S`; the permitted surface is the exact reviewed vectors,
not arbitrary Python execution. Source and installed bytes remain identical and
manifest-covered, and preflight validates the interpreter path, version and
executable SHA-256. The shebang and on-target compilation alternatives are
rejected. Claude may perform only the bounded R11 remediation for C-2 and its
dependent C-3/C-5 work under
`docs/review/phase-5-0-evidence-harness-remediation-r11-prompt.md`, then must
stop for Codex independent pre-execution review. This is not evidence execution
authority and does not authorize SSH, host/database mutation, Package 5.0
implementation, migration `0014`, deployment, cutover, OD-62 or Package 5.1+.
Package 5.0 remains `not ready`; P5.0-R5 remains Blocking.

**Current evidence authorization, 2026-09-02.** Peter Duscha authorized a
narrow pre-implementation evidence harness to resolve the circular dependency
between Package 5.0 readiness and the operational evidence required for
P5.0-R4/P5.0-R5. Claude may build and execute only synthetic disposable
evidence scaffolding after Codex pre-execution review, under every exclusion and
stop condition in
`docs/review/phase-5-0-evidence-harness-authorization-draft.md`. This confirms
no assumption and closes no finding. Package 5.0 product implementation,
migration `0014`, production mutation, deployment, cutover, binding OD-62 and
Package 5.1+ remain unauthorized.

Claude's authorized pre-execution handoff is
`docs/review/phase-5-0-evidence-harness-implementation-prompt.md`. It permits
only the isolated, unprivileged evidence-harness implementation and exact
execution/cleanup plan. The prompt requires handback to Codex before any
privileged or mutation-bearing evidence step.

**Current governance update, 2026-09-02.** Peter Duscha approved **OD-64
Option A**, **OD-65 Option B** and **OD-66 Option A / J-1** in all accountable
roles. The Package 5.0 design therefore adopts the dedicated coordinator
boundary, the isolated Sheet-writer/provenance controls, and the full durable
sealed/registered journal. OD-65 defers correction of the group-writable
worktree to a separate maintenance change; no Package 5.0 deployment may read
executable input from it. **OD-62 remains Open**: G-A is the provisional
direction only, and its binding risk acceptance must wait until P5.0-R5's
operational evidence and independent review are complete. The residual-risk
dispositions, remaining operational evidence and environment assumptions are
also outstanding. Package 5.0 remains `not ready`; implementation and migration
`0014` remain unauthorized.

**Current security update, 2026-09-02.** Codex completed the Package 5.0
revision-12 security re-review. **P5.0-SR1 and P5.0-SR2 are Closed on design**
and the twelve-surface security design review is delivered without a new
Blocking or Important design finding. This is not a readiness recommendation:
C-1/C-3/C-4 and the remaining operational evidence are outstanding,
A-5.0-3 through A-5.0-5 are unconfirmed, and P5.0-R1/R4/R5 remain unresolved.
OD-64 through OD-66 are now rulable; OD-62 remains last. Package 5.0 remains
`not ready`, and implementation and migration `0014` remain unauthorized.

**Historical update — Phase 4 cleanup and OD-63 accepted, 2026-09-02.** Peter
Duscha accepted Codex's independent R3 disposition: **P4-PG4 and P4-PG5 are
Closed**, completing the bounded cleanup of the already approved and closed
Phase 4. Peter also accepted **OD-63 / D5.0-10 Option 1** in all accountable
roles. Its nine numeric controls are accepted; N5.0-18 is **120 seconds — an
operational margin, not a barrier**. A-5.0-3 remains unconfirmed.

Package 5.0 readiness work resumes at `not ready`. P5.0-SR1/SR2 are closed on
design; P5.0-R1/R4/R5 and the required operational evidence remain unresolved.
OD-64 through OD-66 are approved, while OD-62 remains Open with G-A provisional
pending the P5.0-R5 evidence and independent review. No Package 5.0 product
implementation, migration `0014`, production host/database mutation,
deployment, cutover or Package 5.1+ is authorized.

**Superseded — Phase 4 post-gate remediation R2 independently reviewed; final
boundary correction required, 2026-08-31.**

P4-PG1, P4-PG2 and P4-PG3 are **Closed**.
Their narrow constructor corrections establish type before value operations,
preserve the existing typed refusal vocabulary and perform no coercion.
Independent focused evidence is recorded in
`docs/review/phase-4-post-gate-r2-independent-review.md`.

Two further **Important** boundary defects reported in Claude's R2 handback are
confirmed and remain **Open**: **P4-PG4**, malformed idempotency keys escaping
the command envelope's `invalid_request_key` contract; and **P4-PG5**, malformed
stored receipt command names escaping `StoredReceiptUnreadable` on the replay
path. Phase 4 remains approved, but the maintainer requires these defects to be
repaired before Phase 5 preparation resumes. The active handover authorizes only
that bounded correction and its evidence. After Codex accepts it, work returns
to Package 5.0 at exactly the readiness state below.

**Package 5.0 state is unchanged.** It remains `not ready`; its implementation,
migration, deployment, cutover and Package 5.1+ remain unauthorized. P5.0-SR1,
P5.0-SR2, P5.0-R5, OD-62 through OD-66 and required operational evidence do not
close or move because of the Phase 4 correction.

**Superseded as the immediate action while P4-PG4/PG5 are remediated — Package
5.0 security remediation R11 submitted (revision 12).**

**Package 5.0 security review returned, and remediation R11 submitted,
2026-08-31.** The distinct §9.2 security pass ran for the first time and returned
**changes requested with no readiness recommendation**. **P5.0-SR1 (Blocking):**
the deployment integrity check can be skipped silently — `deployment_manifest_digest()`
compares a digest of the live deployed bytes with a caller-supplied copy of that
same value, which proves consistency after deployment and **not provenance from
the reviewed commit**, and no step refused when the comparison was omitted.
**P5.0-SR2 (Important):** the operating-system identity contract and the journal
group contract contradicted each other about `freedomjournal`, so neither could
be followed without invalidating the other.

**Revision 12 of the package plan and the logical schema, plus
`docs/review/phase-5-0-remediation-r11-handback.md`, remediates both and claims
neither closed.** P5.0-SR1 is answered by a fail-closed reviewed-source
provenance contract (package plan §2.12.5a) that binds deployment **and**
generation registration to an immutable reviewed Git object held in a
`root:root 0700` bare store and to an out-of-band approval record, with the
negative test the finding required and a **`NOT NULL` foreign key** to a new
seventh table so an unprovenanced generation cannot be registered and activation
cannot be reached. P5.0-SR2 is answered by making package plan §2.12.2 the
**single canonical primary/supplementary membership table**, withdrawing the
false isolation sentence and adding the positive and negative `id`/`namei`/`open`
evidence the finding asked for.

**This grows the package.** Seven tables instead of six; PERT **40.9 → 47.6**
implementer-days; the security review **3.5–4.5 → 4.5–5.5** reviewer-days over
**twelve** surfaces; two proposed and unaccepted residuals, **R-5.0-15** and
**R-5.0-16**; and stop conditions **10o** and **10p**, with condition 4 extended
so that a named-but-undelivered security review stops the gate.

**Nothing is closed and nothing is authorized.** P5.0-SR1 and P5.0-SR2 are the
Security Reviewer's to close; P5.0-R5 remains **Blocking**; P5.0-R1 and P5.0-R4
remain open; OD-62 through OD-66 remain **Open**, with OD-65 extended and OD-66
gaining an unadopted option A-3; A-5.0-3, A-5.0-4 and A-5.0-5 remain
unconfirmed; host check **C-1** remains not completed and **C-3** and **C-4** not
run; Package 5.0 remains `not ready`; and implementation, migration `0014`,
deployment, cutover and Package 5.1+ remain unauthorized. **An independent
security re-review of revision 12 is required, and the remaining §9.2 pass is
outstanding in full.** No host object was created and no `git` write was
performed.

**Superseded — Package 5.0 Security Reviewer named, 2026-08-31.** Peter Duscha named **Codex**
the Package 5.0 Security Reviewer, closing OD-61 / D5.0-8 and discharging the
first of the six readiness actions in `docs/review/Handover information`. Codex
did not implement Package 5.0, so §0.3's bar on approving one's own work holds;
it now also holds the Independent Reviewer and logical-schema reviewer roles, and
that concentration is accepted knowingly. **The assignment approves no option,
closes no finding and confirms no assumption**, and the §9.2 security pass —
3.5–4.5 reviewer-days over eleven surfaces — **has not run**; the revision-11
design re-review is not that pass. The briefing pack is
`docs/review/phase-5-0-security-review-brief.md`. OD-64, OD-65 and OD-66 become
rulable only once the recommendation exists; OD-63 is rulable now and is drafted
unsigned at `docs/review/phase-5-0-od-63-ruling-draft.md`; OD-62 is ruled last.
Package 5.0 remains `not ready` and implementation, migration, deployment,
cutover and Package 5.1+ remain unauthorized.

**Superseded — Package 5.0 revision 11 independent re-review, 2026-08-31.** Codex identified
no new Blocking or Important design finding and considers R10-A through R10-C
materially addressed on paper. This closes the R10 remediation request only.
It does not close P5.0-R5 or the package gate, confirm A-5.0-5, accept a
decision, or authorize implementation. P5.0-R5 remains Blocking pending
authorized operational evidence; P5.0-R1 and P5.0-R4 remain open; P5.0-R2
remains closed; OD-62 through OD-66 remain Open; the Security Reviewer remains
unnamed; and Package 5.0 remains `not ready`. The active handover contains the
readiness and authorization work that precedes any implementation brief.

Phase 4 was approved by Peter Duscha on 2026-08-29 after the required
independent review and two remediation cycles. P4-R1 through P4-R5 and D-04 are
Closed. Phase 5 package planning is released, but each package remains subject
to its own definition of ready, predecessor decisions, independent review and
cutover gate. This approval authorizes no migration, production mutation,
data-authority cutover, Sheet retirement or permanent Discord character-
mutation surface. R-23 remains an active accepted Phase 3 residual;
screen-reader traversal was Not Run for Phase 3 and is not classified as passed.

1. Select the next Phase 5 package according to §12.0 and §12 Phase 5 dependency
   order; Phase 4 approval does not choose the package automatically.
2. Baseline that package under the management definition of ready, including
   its exact legacy sources, typed target, independently reviewed logical schema
   where required, correction workflow, three-point estimate, capacity,
   acceptance traceability and remediation contingency.
3. Close every package-specific decision and dependency before implementation;
   do not infer unresolved game, authorization, migration or cutover policy.
4. Preserve the accepted Phase 4 command, ledger, idempotency, concurrency,
   authorization and audit/correlation contracts when adding the package's real
   repository and interface consumers.
5. Authorize no migration, production mutation, authority cutover, deployment
   or Sheet retirement until the selected package's own readiness and gate
   requirements explicitly permit it.
6. Continue maintaining status, RAID, decisions and change control under
   `docs/project-management/`.

Phase 4 handoff history is retained in its Phase 4 review artifacts. As of the
2026-08-31 independent re-review of Package 5.0 revision 10,
`docs/review/Handover information` is the active **documentation/design-only
remediation R10 brief**. Revision 10 was returned **changes requested** because
its executable identity recipes do not match the named `setpriv` contract: the
E2–E6 recipes use unsupported `+keep_caps`, E8 does not drop the bounding set it
declares empty, and E7 omits complete masks. R9-A and R9-B are materially
improved, but R9-C remains Blocking. It
does not authorize Package 5.0 implementation, migration, environment changes,
deployment, cutover or Package 5.1+ work. **Revision 11 has been returned against
that brief on 2026-08-31 and awaits an independent re-review**, which it
requires; the brief remains the active one until that re-review is recorded, and
nothing in revision 11 closes it, closes P5.0-R5 or authorizes any of the work
the brief withholds.

**Submission history — revision 11 was returned against the R10 brief on
2026-08-31 and claims no finding closed.** It concedes that revision 10's
executable-identity recipes do not construct the identities they declare:
`setpriv(1)` from util-linux 2.39.3 rejects the securebit `+keep_caps` used by
E2–E6; the same manual page states that the kernel does not permit capabilities
to be **added** to a bounding set, which those five recipes also requested and
which revision 10 did not notice; E8 declared an empty bounding set and dropped
nothing; and E7 stated no inheritable or ambient mask. Package-plan §2.13.5c is
rewritten around **`capsh(1)`**, whose manual documents that it acts on its
arguments in the order given — which `setpriv(1)` does not, and on which every
declared mask depends — with a **seven-step construction**, complete UID, GID,
supplementary-group, P/E/I/A/B and **securebits** values for `E1 … E8`, a
complete invocation for each, and a **mask-versus-recipe comparison table**. The
launching bounding set is stated as a prerequisite and asserted, because no tool
can add to one. Dependent evidence is revalidated: **`JNL-50` case 7 and `JNL-49`
case 11 take `E6` rather than `E2` as the isolating positive control**, `E2`
being retained as corroborating, and `JNL-50` case 4 gains a second control form.
**The evidence band, the estimate and the security-review effort are unchanged —
fifty identifiers, eighty-eight cases, PERT 40.9 implementer-days and 3.5–4.5
reviewer-days — and the plan states why rather than recalculating.** The R8-A
deployment-digest lifecycle, the R8-B cleanup state machine, the R8-D/F-7
residual treatment and revision 10's R9-A and R9-B corrections are **preserved
unchanged in substance**, and **no corrected identity produced a conflict with
them**. Two stale copies of superseded wording were found in the logical schema
and corrected. **No privileged case is claimed to have run**; assumption
**A-5.0-5** is widened and remains unconfirmed; the host was **read**
non-mutatingly for the tool contract (package plan §8.1 **H-6**) and was not
written. The submitted artifacts are
`docs/review/phase-5-0-package-plan.md`,
`docs/review/phase-5-0-logical-schema.md` and
`docs/review/phase-5-0-remediation-r10-handback.md`. P5.0-R5 remains
**Blocking**, P5.0-R1 and P5.0-R4 remain open, P5.0-R2 remains closed, D5.0-9
through D5.0-13 / OD-62 through OD-66 remain **Open**, the Security Reviewer
remains **unnamed**, **no option, risk, decision or schema object is adopted or
closed**, and Package 5.0 remains `not ready` with implementation unauthorized.
**The required independent re-review completed on 2026-08-31 with no new
Blocking or Important design finding; it closed R10 only and did not alter any
of those package states.**

**Superseded — revision 10 was returned against the R9 brief on 2026-08-30 and claimed no
finding closed.** It concedes that revision 9's authority register recorded only
half of `FS_IOC_SETFLAGS`'s permission check — the capability, not the
owner-or-`CAP_FOWNER` authorization — and redesigns package-plan §2.13.5c around
**eleven** authorities in which `A1` is the `CAP_LINUX_IMMUTABLE` half alone and
the new `A10` and `A11` carry the owner half over the `freedomsheet`-owned
journal and over the root-owned seal and archive respectively; **eleven of the
thirteen falsification rows gain a prerequisite**, and every such change makes an
alteration harder to construct rather than easier. It removes the A3/A2
contradiction by separating what an authority **is** from who can **hold** it — a
holder table, and detector reach assessed against the smallest identity that can
really hold each combination — and **narrows** the bounded claim accordingly to
**F-2, F-3 and F-6**. It replaces the executable evidence contract with eight
specified identities `E1 … E8` carrying complete permitted, effective,
inheritable, ambient and bounding capability sets and securebits, and rewrites
`JNL-49` and `JNL-50` at **twelve cases each**, every negative flag case carrying
a positive control; **no privileged case is claimed to have run**, and assumption
**A-5.0-5** is corrected and remains unconfirmed. The R8-A deployment-digest
lifecycle, the R8-B cleanup state machine and the R8-D withdrawal of F-7's
detector are **preserved unchanged in substance**. The submitted artifacts are
`docs/review/phase-5-0-package-plan.md`,
`docs/review/phase-5-0-logical-schema.md` and
`docs/review/phase-5-0-remediation-r9-handback.md`. P5.0-R5 remains **Blocking**,
P5.0-R1 and P5.0-R4 remain open, P5.0-R2 remains closed, D5.0-9 through D5.0-13 /
OD-62 through OD-66 remain open, the Security Reviewer remains **unnamed**, and
Package 5.0 remained `not ready` with implementation unauthorized. Its
2026-08-31 independent re-review is recorded above and required remediation R10;
**revision 11 is the response, described above**, and
`docs/review/phase-5-0-remediation-r9-handback.md` is superseded and retained as
review history.

**Revision 8 was returned against the R7 brief and independently re-reviewed on
2026-08-30. Changes were requested.** Four Blocking inconsistencies were found:
Algorithm C's deployment-digest validation occurred after first consumption, and
compared the supplied value against the probe's copy of itself; its
cleanup-failure evidence required mutually exclusive residue outcomes; the
capability register treated `CAP_LINUX_IMMUTABLE` as bypassing archive DAC; and
F-7 named no independent detector for a forged matching `/etc/machine-id`.
**Revision 9 was returned against the R8 brief on 2026-08-30 and claims no
finding closed.** It moves the deployment digest's computation and comparison to
Algorithm C **C0** and replaces the universal ordering claim with invariants
**I-1 … I-5**; adds a three-state cleanup machine in which *"no generation
artifact"* is unconditional and *"no transient residue"* is conditional on
cleanup success, with a single next-invocation behaviour; replaces the
eight-capability register with **nine independently constructible authorities**
separating flag control from discretionary access; and **withdraws F-7's
refusal**, recording a forged matching host identity as residual **R-5.0-13** and
routing an independent authenticated host binding as OD-66 **option A-2** under
§0.2 without adopting it. The submitted artifacts are
`docs/review/phase-5-0-package-plan.md`,
`docs/review/phase-5-0-logical-schema.md` and
`docs/review/phase-5-0-remediation-r8-handback.md`. **Independent re-review of
revision 9 returned changes requested:** R8-A, R8-B and R8-D are materially
addressed, but R8-C omits the owner-or-`CAP_FOWNER` prerequisite for
`FS_IOC_SETFLAGS`, making the non-root `CAP_LINUX_IMMUTABLE`-only archive case
and several minimum combinations non-constructible. The register also declares
A1–A6 independent while saying every real A3 holder has A2. **Revision 10 is the
response, described above.**
`docs/review/phase-5-0-remediation-r8-handback.md`,
`docs/review/phase-5-0-remediation-r7-handback.md` and
`docs/review/phase-5-0-remediation-r6-handback.md` are superseded and retained as
review history. P5.0-R5 remains **Blocking**, P5.0-R1 and P5.0-R4 remain open,
P5.0-R2 remains closed, D5.0-9 through D5.0-13 / OD-62 through OD-66 remain
open, the Security Reviewer remains **unnamed**, and Package 5.0 remains
`not ready` with implementation unauthorized. This reference is updated to the
next submitted revision whenever remediation work is returned.
