# Freedom Blades Platform — Master Implementation Plan

Status: Controlled baseline v1.6 — accepted 2026-08-27

Baseline date: 2026-08-27

Document owner: Peter Duscha, Product Owner

Acceptance authority: Peter Duscha, Maintainer and Product Sponsor

Audience: Maintainers, implementation agents, reviewers, and operators

Repository: `freedom-bot` (to evolve into the Freedom Blades platform)

Primary rules source: `Freedom Blades - Homebrew Rules.pdf`

## 0. Document control and project governance

### 0.1 Purpose of this document

This document is the product roadmap and technical milestone contract. It says
what outcomes and controls each phase must deliver. It is not, by itself, a
calendar commitment or a substitute for a phase delivery plan.

Detailed project controls live under `docs/project-management/`:

- [`README.md`](project-management/README.md) — governance, roles, gate process,
  estimation rules and management definition of ready/done;
- [`status.md`](project-management/status.md) — current phase, gate, forecast,
  evidence and blockers;
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
- the existing Discord bot, reduced over time to a Discord adapter;
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
integration, live data, or deployment configuration. The legacy Discord bot
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
Discord bot ───────────────────┼─> Application services ─> Domain
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
existing Sheets connector remains untouched because the live Discord bot still
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
| 5.2 Wallet and `/xchange` | typed wallet/ledger schema; package-owned balance migration and reconciliation; atomic, idempotent currency exchange | 5.0 | first economy-migration/mutation review |
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

## 15. Google Sheets retirement

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
   for the numeric verification period defined by the package plan;
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
path is then a rollback implementation during verification, not a secondary
authority.

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

1. Replace the superseded pre-v1.1 Phase 2 package plan and baseline a four-package
   remediation plan with named implementer, Independent Reviewer, Data Owner and
   Operations Owner; three-point estimates; review/remediation allowance;
   environment readiness; and rehearsal windows.
2. Remove ADR 0008's rejected generic state, balance, transaction, correction
   and Sheet-bootstrap implementation while preserving immutable snapshot,
   identity, mapping, authorization, provenance and audit behavior.
3. Implement and test `legacy_authority_deferred`, remove impossible legacy
   comparisons, and close all blocking independent-review findings.
4. Exercise upgrade/downgrade/upgrade, backup/restore/rerun and direct
   restricted-runtime-role denial in the named disposable or staging
   environment.
5. Conduct the maintainer-supervised real-export preview and store the Data
   Owner attestation defined by the Phase 2 evidence contract; commit no real
   Actor data or artifact.
6. Submit the complete Phase 2 gate package; Phase 3 remains not ready until the
   Acceptance Authority records an approved data-integrity/identity/migration
   gate.
7. Before Phase 3, baseline its read-only/security packages and prove that no
   character-game-state correction surface exists.
8. Maintain current decisions, risks, dependencies and forecast in
   `docs/project-management/` throughout delivery.

The replacement Phase 2 plan is not ready for approval unless it records the
named environment; named implementer, Independent Reviewer, Data Owner and
Operations Owner; optimistic/likely/pessimistic effort and confidence; explicit
review/remediation contingency; maintainer and staging availability windows;
artifact/import size and runtime limits; reconciliation success thresholds;
backup-restore success criteria; rollback triggers; runtime-role evidence
method; monitoring/observation period; and the date or bounded window for the
supervised real-export rehearsal.
