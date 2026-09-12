# AGENTS.md — Freedom Blades Platform

This is the working agreement for humans and coding agents contributing to
the Freedom Blades Platform. It applies to the entire repository.

## Required project context

Before planning or changing this project, read:

1. this file in full; and
2. `docs/implementation-plan.md`, including the milestone being worked on and
   its acceptance criteria.

The implementation plan is the approved product roadmap and milestone
contract. This file contains the always-applicable engineering, safety, and
contributor rules. If they conflict, stop and ask a maintainer rather than
silently choosing one.

The root `AGENTS.md` and `CLAUDE.md` files are discovery entry points. This
file is the canonical working agreement and must not be bypassed.

### Skills and enforced guards — aids, never authority

Agents that support them additionally load four procedural skills under
`.claude/skills/` and two `PreToolUse` guards under `.claude/hooks/`, registered
in `.claude/settings.json`. Three rules govern them, and they are not
negotiable.

1. **This file remains the single source.** A skill **cites** this document and
   `docs/implementation-plan.md`; it does not restate a rule as a second
   authority. Where a skill and this file disagree, this file wins and the
   disagreement is a defect to report, not a choice to make.
2. **No always-applicable rule may live in a skill.** A skill applies only when
   it is invoked, so a rule placed in one is a rule that silently did not apply
   on the run that forgot it. Product invariants, secrets rules, gate
   discipline, the Discord-versus-Freedom-bot distinction and the two
   test-environment traps in "Running the suites" stay here, in force always.
3. **An agent without skill or hook support is held to the same agreement.**
   The tooling is a convenience for one client. It creates no second standard
   and excuses nothing.

The four skills are `run-suites`, `handoff-checklist`, `migration-staging` and
`rules-sourcing`. The two guards refuse secret-file access and Git history
rewrites, and refuse commits and pushes on the default branch; a guard refusal
is a stop condition, not an obstacle to route around. Their tests are
`python3 .claude/hooks/test_guards.py`.

## Product context and direction

The Freedom Blades Platform supports the Freedom Blades Discord community. Its
game behavior is based on D&D 5.5 (the 2024 rules) plus Freedom Blades homebrew
rules. Today it is a Python/Pycord bot backed by Google Sheets. It is being
evolved in this repository into a secure, PostgreSQL-backed web platform with
Discord and Foundry adapters.

Music is not part of the platform. Its former implementation, dependencies,
configuration and deployment templates were removed under OD-40. It is removed,
not deferred: do not reintroduce it in any phase.

### Two different things, never conflated

**Discord** is the Freedom Blades community's server. It is the **basis of the
whole project**: the platform exists to serve that community, and Discord
supplies its identity, membership, roles, communication, events, notifications
and attendance evidence. Discord is **never retired**. No decision in this
repository proposes retiring it, and any instruction that appears to should be
refused and referred to a maintainer.

**The Freedom bot** is this repository's Python/Pycord application — `main.py`,
`ext/commands/`, the Sheet-backed `models/` and `helpers/`. It is a client of
Discord, not Discord itself. It is retired under implementation-plan §15.2 once
the platform is fully functional.

Retiring the Freedom bot removes a **client**. It removes nothing from Discord,
and it does not touch Discord OAuth authentication, guild membership, role
verification, events or notifications. Where these documents say "the bot", they
mean the Freedom bot; where they say "Discord", they mean the server and its
APIs. Text that conflates the two is a documentation defect, not a licence to
act on either reading.

The approved direction is:

1. keep the live Freedom bot reliable;
2. isolate game rules and use cases from Discord and Google Sheets;
3. replace Sheets incrementally with a transactional database;
4. add a purpose-built web interface using the same application logic; and
5. integrate selected data with Foundry VTT through a narrow, authenticated,
   versioned interface;
6. automate missions, attendance evidence, reports, rewards, and approvals;
7. automate basic Bastions before incrementally implementing special
   facilities; and
8. retain Discord as a platform integration for identity, communication,
   events, attendance metadata and notifications; and
9. retire the Freedom bot once the platform provides every player-facing
   behavior it provides, so that a player needs no manual step beyond the
   Council confirmations the rules require.

Treat this as an evolution of a live system, not permission for a rewrite.
**The Freedom bot remains a supported adapter and must not be deleted, disabled
or degraded for as long as the platform is not fully functional.** This is the
governing condition, and it is not satisfied by a milestone, a cutover, a
passing test suite or an agent's judgement that the work looks finished.

*Fully functional*, for this purpose, means all of: every player-facing behavior
the bot provides exists on the platform and its owning package gate is approved;
the platform meets the definition of platform completion in implementation-plan
§19 for those behaviors; the final Google Sheet retirement gate in §15.1 has
closed; and measured adoption evidence meets a threshold accepted in advance by
the Product Owner. Retirement then proceeds under §15.2 as a separate,
independently gated decision, commands deregistered before any code is deleted.

Behavioral replacement means satisfying the player's underlying task, not
preserving every Discord slash-command interface on the website. In particular,
the platform does not need an `/info` command: its linked-character pages
replace that read experience once the owning typed packages supply the data.
Until the relevant gates close, the existing Freedom-bot command remains
supported and must not be disabled or degraded.

Discord itself is **not** retired with the bot. Discord OAuth remains the
platform's authentication, and Discord remains the source of guild membership,
role verification, events, notifications and voice-state attendance evidence.
Whatever Discord-side presence those require after the bot is retired is a
narrow, platform-owned adapter, sized and gated by the package that needs it —
the attendance package in particular, because voice-state join/leave requires a
live gateway connection.

The repository may be renamed later as an explicit administrative change.

Baseline v1.7, 2026-08-28: direction items 8–9 and this paragraph were amended
on Peter Duscha's decision that the **Freedom bot** is deleted once the platform
is fully functional, because the platform makes it unnecessary. **Discord is not
in scope of that decision and never has been.** See change-log v1.7, its
correction C-1, and OD-53.

## Product invariants

- PostgreSQL is the eventual authoritative operational data store.
- A Discord user may be linked to multiple characters, and a character may
  have multiple explicitly authorized users.
- Character links are managed and audited through Guild Council workflows.
- Website direct mutations require Guild Council unless a later approved
  requirement delegates a narrower capability.
- No advancement, mission settlement, reward, or Council-controlled Foundry
  proposal is official until an authorized Guild Council user approves it.
- There is no automatic advancement.
- Attendance collected from Discord voice state is evidence only. It never
  grants rewards or advancement and must be confirmed through the mission
  workflow.
- Initial attendance tracking records join/leave metadata only. Do not record,
  receive, transcribe, or retain voice audio without a separately approved
  privacy, consent, retention, and legal design.
- AI may draft or extract proposals, but it must never calculate authoritatively
  or apply game state without deterministic validation and required human
  approval.
- Audit and transaction history is append-only in normal operation.
  Corrections use explicit compensating actions rather than erased history.

## Rules sources

Before changing game behavior, identify the rule that supports it. Use this
precedence:

1. explicit Freedom Blades rulings supplied by maintainers;
2. `Freedom Blades - Homebrew Rules.pdf`;
3. official D&D 2024/5.5 rules;
4. existing behavior, only where those sources are silent.

If sources conflict or are ambiguous, do not silently choose. Preserve current
production behavior where safe, document the ambiguity, and ask a maintainer.
Tie rule-table comments and tests to a rule name and PDF page/section where
possible. Do not reproduce copyrighted sourcebooks in this repository.

Rules are domain policy, not Discord UI code. Calculations, validation, state
transitions, and rule tables must be reusable by Discord, the future web app,
tests, and Foundry.

## Current repository map

- `main.py`: bot startup and extension registration.
- `config.py`: environment configuration and validation.
- `ext/commands/`: Discord slash-command cogs and interaction flow.
- `ext/error_handler.py`: application-command error handling.
- `models/`: current character, resource, lifestyle, trade, crafting, and
  bastion behavior. Some models still access Sheets directly.
- `helpers/`: calculations, formatting, dice, and utilities.
- `connectors/sheets.py`: Google Sheets API adapter.
- `application/`, `domain/`, `adapters/`: the platform layers introduced from
  Phase 1 onward.
- `tools/`: operator entry points, such as the Phase 2 Sheet importer.
- `infra/systemd/`: service deployment files.
- `.env.example`: documented configuration contract.
- `docs/implementation-plan.md`: approved platform roadmap, milestone
  requirements, acceptance criteria, and review gates.

There is a committed pytest suite covering parts of the existing domain
behavior. Expanding it into unit, application, repository, database,
authorization, migration, Foundry contract, and end-to-end coverage is a
priority.

## Architecture

Work toward this dependency direction:

```text
Discord commands ─┐
Web routes/UI ─────┼─> application services/use cases ─> domain
Foundry adapter ───┘                │
                                    └─> repository interfaces
                                          ├─ database adapter
                                          └─ Sheets adapter (temporary)
```

Dependencies point inward. Domain code must not import Discord, Google APIs,
web frameworks, database clients, or global configuration.

### Domain

- Represent game concepts explicitly. Prefer dataclasses, enums, value objects,
  and typed results over unstructured dictionaries.
- Keep calculations deterministic. Inject clocks and random-number generators
  into behavior that depends on time or chance.
- Use integer copper pieces for money and an explicit smallest unit for other
  divisible resources. Never persist currency as a binary float.
- Enforce invariants in domain or application code, not only in Discord option
  validation.
- Use stable IDs for actors and records. Display names are mutable and are not
  identities.

### Application services

- A Discord command or HTTP handler should authenticate/authorize, parse input,
  invoke one use case, and render its result.
- Multi-resource operations such as trades, sales, crafting, and payments must
  be atomic. Never persist half a transaction.
- Make state-changing operations safe against Discord retries and duplicate
  submissions. Use an idempotency key such as the interaction ID.
- Return typed domain/application errors. Translate them to safe user messages
  only at an outer boundary.

### Adapters

- Define repository protocols around domain needs, such as `get_actor`,
  `save_actor`, and `transfer_resources`. Do not expose A1 ranges or SQL query
  shapes to application code.
- Keep Google column/range mapping inside the Sheets adapter.
- Keep Discord embeds, mentions, response timing, and channel IDs inside the
  Discord adapter.
- Keep ORM records and database sessions outside the domain. Map explicitly
  between persistence and domain models.
- Do not perform blocking Google, database, or HTTP work on the event loop. Use
  an async client or a deliberate thread boundary.

Introduce boundaries while implementing a feature or migration. Do not add
abstractions without a real consumer.

**Phase 4 application of this rule (final OD-52 amendment, 2026-08-29).** Phase
4 does not create a temporary Sheet-backed money query without a production
caller and does not rewire `/info` merely to manufacture one. Package 5.2 owns
the wallet query and introduces it with its real character-page consumer. Phase
4 protocols must be consumed by its ledger/idempotent command execution work,
not left as speculative interfaces.

## Object-oriented design and encapsulation

Use object-oriented design where objects represent meaningful game or system
concepts. The goal is cohesive, encapsulated code with clear responsibilities,
not merely putting procedural functions inside classes.

### Classes and objects

- Give each class one clear reason to change. A class should represent one
  domain concept, application use case, or infrastructure responsibility.
- Keep state private by convention (`_field`) when callers should not mutate it
  directly. Expose intention-revealing methods such as `actor.pay_lifestyle()`
  or `wallet.transfer_to()` instead of allowing arbitrary field changes.
- Construct valid objects and keep them valid. Validate required invariants in
  constructors, factories, value objects, and mutation methods.
- Prefer immutable value objects for money, IDs, dates, rarity, proficiency
  level, and other small concepts. Use frozen dataclasses where appropriate.
- Use properties only when access is cheap and unsurprising. Use explicit
  methods for I/O, calculations with meaningful cost, and state changes.
- Keep methods short and at one level of abstraction. Public methods express
  intent; private helpers contain implementation detail.
- Do not expose internal mutable lists or dictionaries. Return immutable views,
  iterators, tuples, or defensive copies when callers only need to inspect.
- Define equality and hashing only from stable value semantics. Database IDs
  and mutable display names should not accidentally define domain equality.

### Composition and interfaces

- Prefer composition and delegation over inheritance. Use inheritance only for
  a genuine substitutable “is-a” relationship with shared behavior.
- Avoid deep class hierarchies, mixin collections, static utility classes, and
  “god objects” that combine rules, persistence, rendering, and orchestration.
- Depend on small typed protocols or abstract interfaces at architectural
  boundaries. Keep interfaces owned by the code that consumes them.
- Inject repositories, clocks, random sources, and external clients through
  constructors. Do not instantiate infrastructure dependencies inside domain
  objects or fetch them from module globals.
- Use factories when object construction requires validation or mapping from an
  external representation. Keep database and Sheet mapping out of domain
  constructors.
- Apply SOLID principles pragmatically. In particular, preserve single
  responsibility, substitutability, interface segregation, and dependency
  inversion; do not add indirection solely to satisfy a pattern.

### Separation of responsibilities

A normal state-changing request should have distinct responsibilities:

1. an adapter parses Discord or HTTP input and establishes the caller;
2. an application-service object authorizes and coordinates the use case;
3. domain objects enforce rules and calculate the state transition;
4. a repository persists the complete transition transactionally; and
5. the adapter renders the returned result.

Domain objects must never call `save_to_sheet()`, execute SQL, send Discord
messages, or read environment variables. As existing models are touched,
gradually move their Sheet loading/saving behavior behind repositories while
preserving behavior with characterization tests.

Prefer command/query separation:

- commands intentionally change state and return a small result or receipt;
- queries read and return view data without hidden mutations; and
- methods named `get`, `find`, `render`, or `calculate` must not persist state.

### Clarity and efficiency

- Optimize first for correctness, readability, and a clean dependency graph.
  Measure before adding caches, batching, or specialized data structures.
- Avoid repeated Sheet/API/database calls inside loops. Load required data in
  batches and make transaction boundaries explicit.
- Prevent N+1 database queries in bot commands and web endpoints.
- Keep network and persistence operations coarse-grained, while keeping domain
  methods small and focused.
- Use generators for streaming large inputs and bounded pagination for APIs.
  Do not load unbounded audit logs, inventories, or histories into memory.
- Document non-obvious performance tradeoffs and add a benchmark for genuinely
  performance-sensitive rules or import paths.

## Database migration

PostgreSQL is the default production recommendation: the Freedom bot and web app will
need concurrent access, transactions, constraints, and reliable migrations.
SQLite is acceptable for isolated local tests, but production code must not
rely on SQLite-only behavior. Choosing another database requires a documented
decision.

Use a migration tool and commit every schema migration. Never edit an applied
migration. The eventual schema should cover:

- Discord users, guild membership, roles, and actor ownership;
- actors/characters and stable external identifiers;
- resources, balances, items, and inventory;
- skills, proficiencies, languages, lifestyle, and bastions;
- downtime, trades, crafting, and other state transitions;
- an immutable audit/event record for administrator-visible mutations; and
- external mappings and sync metadata for Sheets and Foundry.

Store Discord snowflakes as 64-bit integers or canonical strings, never 32-bit
integers. Use UTC timestamps. Add foreign keys, uniqueness rules, check
constraints, and optimistic concurrency/version fields where bot and web edits
can collide.

Migrate in reversible stages:

1. extract repository interfaces and characterize existing Sheet behavior;
2. add the database adapter and schema without changing production reads;
3. build a repeatable, dry-runnable import with validation and a report;
4. shadow-read or reconcile database results against Sheets;
5. cut reads over behind configuration or feature flags;
6. cut writes over with backups and a rollback procedure;
7. keep Sheets read-only for a defined verification period, then retire its
   credentials and adapter.

Avoid indefinite dual writes. If a short dual-write period is necessary, make
one store authoritative, record failures durably, reconcile automatically, and
document recovery. Imports must be idempotent and retain mappings from Sheet
rows to stable database IDs.

Do not delete the Sheets adapter, credentials, or rollback path until the
verification and retirement gate in `docs/implementation-plan.md` has been
completed and approved.

## Web interface

The web interface and the Freedom bot must call the same application services. The
web app must not become a second implementation of the rules.

- Put a versioned API boundary between browser and server.
- Authenticate through Discord OAuth2. Still verify guild membership, roles,
  actor ownership, and action permissions server-side on every request.
- Distinguish player, game-master/staff, and administrator capabilities.
- Use CSRF protection for cookie sessions, secure/HTTP-only/SameSite cookies,
  restrictive CORS, input validation, output escaping, and rate limits.
- Never trust actor IDs, role claims, prices, balances, or calculated results
  supplied by the browser.
- Audit sensitive mutations with actor, action, time, source, and correlation
  ID. Provide an administrative correction flow rather than editing history.
- Treat cached Discord membership and roles as display/cache data, not
  permanent authorization. Verify effective privileges server-side.
- Use stable Discord role IDs for authorization; role names are presentation.
- Ordinary users initially receive a read-only website. Do not infer permission
  to add self-service mutations from the existence of a form or API route.

Do not choose a web or frontend framework as a drive-by change. Record material
architecture choices as short ADRs under `docs/adr/`.

## Foundry VTT integration

Foundry integration is feasible, but Foundry must be treated as an external
client and must never receive direct database access. Prefer a small Freedom
Blades Foundry module that calls a versioned HTTPS API exposed by this
application.

Before implementation, confirm the deployed Foundry version, game system and
version, network topology, and which fields are authoritative on each side.
Begin with one narrow, useful flow—usually read-only character/resource
display—before allowing writes.

The currently observed baseline for `The Guild` is Foundry `14.367`, D&D5e
`5.3.3`, world ID `the-guild`, with active characters in the Actor folder
`Characters (active)`. Treat these values as an observed deployment baseline,
not an eternal compatibility promise. The connector must negotiate or validate
supported versions.

- Map database actor IDs, Discord user IDs, and Foundry actor/world IDs
  explicitly.
- Use scoped, revocable credentials. Never ship an administrator or database
  secret in a Foundry client.
- Validate permissions server-side and audit sync operations.
- Include API/schema versions, timeouts, retry backoff, idempotency, and clear
  conflict handling.
- Prefer one-way synchronization initially. Bidirectional sync requires
  field-level ownership rules and conflict resolution.
- Use supported Foundry module hooks/APIs, and pin and test supported Foundry
  and game-system versions.
- Never use direct reads from or writes to live Foundry LevelDB as the
  production integration. Offline read-only snapshots may be used for
  maintainer-authorized discovery, but production synchronization requires the
  authenticated, versioned Foundry adapter described in the implementation
  plan.

## Missions, attendance, reports, and settlements

- Mission attendance is captured as Discord user join/leave intervals, with
  reconnect handling, and must be confirmed by the DM.
- A player selects from characters currently linked to their Discord identity.
  The DM or Guild Council may correct the selection with an audited reason.
- DMs may prepare mission facts and reports. Guild Council applies settlements.
- Reward calculations must be deterministic, rule-versioned, previewed, and
  committed atomically across all affected characters.
- Discord events are an external presentation/integration. Deleting or changing
  an event must not destroy the internal mission record.
- Report revisions, loot decisions, settlement proposals, overrides,
  approvals, and corrections must remain attributable and auditable.
- AI-authored report text is always a draft requiring human review. AI output
  cannot grant rewards, infer official attendance, or mutate character state.

## Bastions and facilities

- Migrate the existing Bastion state and maintenance behavior before building
  a comprehensive special-facility engine.
- Each implemented facility must cite its rule source and version, validate
  prerequisites, preview effects, and have boundary and failure tests.
- Prefer data-driven definitions for declarative facts, but do not introduce an
  unrestricted expression or scripting language for facility effects.
- Complex or exceptional facility behavior belongs in tested domain policy
  objects.
- A Bastion turn, resource deduction, or facility order must not be applied
  twice due to retries or concurrent requests.

## Discord practices

- Preserve the existing cog/extension organization.
- Defer interactions before work that may approach Discord's response timeout,
  then use follow-ups correctly.
- Make errors concise and ephemeral when they involve private character or
  administrative information.
- Never expose exception text, credentials, internal paths, raw Google/SQL
  errors, or another player's private state in Discord.
- Check guild, channel, role, and actor ownership at the command boundary.
  Channel restrictions alone are not authorization.
- Avoid module-level network calls and mutable global services. Initialize
  dependencies at startup and inject them into cogs/services.
- Use structured logging with correlation IDs, without logging secrets or
  sensitive player data.

## Configuration and secrets

- Configuration comes from environment variables and is validated at startup.
- Keep `.env.example` current with safe placeholders.
- Never read, print, commit, or modify `.env`, `yt-cookies.txt`,
  service-account JSON, Discord tokens, OAuth secrets, database URLs, or
  Foundry credentials.
- Never add fallback secrets or production IDs to source code.
- Request only the permissions each integration needs.
- Remove Google service-account credentials after Sheets is retired.

If a secret may have entered Git history or logs, stop and notify a maintainer.
Deleting the visible line is insufficient; the credential must be rotated.

## Coding standards

- Target the Python version documented by deployment. New code should be typed
  and compatible with that version.
- Prefer focused modules, descriptive names, and small functions.
- Use `pathlib`, context managers, timezone-aware datetimes, and specific
  exception types.
- Validate at boundaries; do not silently coerce invalid persistent data.
  Imports should report the offending row and field.
- Keep rendering separate from mutation logic.
- Preserve public behavior unless a task explicitly changes it.
- Add dependencies deliberately and lock them reproducibly. Do not introduce a
  framework for a small utility.
- Run configured formatter, linter, and type checker. Do not reformat unrelated
  files in a feature change.

Prefer English for code, identifiers, tests, and technical documentation.
Existing German comments and community terminology may remain; match the
community's selected language for Discord copy.

## Testing

Use `pytest` for new tests. Add test configuration and development dependencies
in a focused change instead of relying on globally installed tools.

Aim for:

- many unit tests for rule calculations and domain invariants;
- application-service tests using fake repositories;
- repository contract tests shared by Sheets fakes and the database;
- database integration tests exercising real migrations and constraints;
- a small number of command tests with Discord and Google mocked;
- migration tests using anonymized representative rows; and
- Foundry API contract tests for authentication, version mismatch, retries,
  duplicates, and conflicts.

Every bug fix should first add a regression test that fails for the reported
case. Use table-driven tests for rule matrices and boundary values. Cover
insufficient resources, invalid inputs, duplicate requests, concurrency,
partial external failure, and permission denial.

Tests must never contact live Discord, Sheets, production databases, Foundry, or
external media services. Do not use real player data or credentials in fixtures.

### Running the suites

Two facts about this repository make it easy to produce a green run that proves
nothing. Both are load-bearing; state them in any evidence that cites a figure.

The `run-suites` skill carries this procedure for agents that support skills.
It cites this section and does not replace it.

**The repository and test environment have different paths.** Work in
`/opt/freedom-blades/platform`. The documented disposable test environment is
`oracle-test`, where the Python interpreter is
`/opt/freedom-blades/runtime/venv-web/bin/python` for both bot and web suites.
Do not use the historical `/opt/discord-bots/` environments as the default test
setup. Interpreter paths on one host do not establish their availability on
another. Follow `docs/operations/disposable-test-server.md` for synchronization,
dependencies and execution; a missing pytest is an environment problem, not a
broken suite.

**`TEST_DATABASE_URL` must be exported**, naming the Unix-domain socket:
`postgresql+psycopg:///freedom_test`. Without it every database-marked test
skips, the web suite reports roughly *1141 passed, 1362 skipped* in about
twelve seconds, and **it still exits 0**. Check the skip count before believing
a pass: the correct figure is **80**, and `-rs` prints the reason for each.

Run the two suites **serially**. They share one disposable database (finding
F-6), so a parallel run is not a faster verification — it is a different one.

After synchronizing the current workspace using that document's secret-excluding
procedure, run the following **on `oracle-test`**, from the repository directory:

```bash
cd /opt/freedom-blades/platform
export PATH='/usr/lib/postgresql/16/bin:/usr/bin:/bin'
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'
/opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs tests/test_*.py
/opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs tests/web
node --test "foundry-module/tests/"*.test.mjs
```

These environment instructions do not override a task-specific restriction on
SSH, host inspection, database operations or destructive tests. When such a
restriction applies, report the checks not run and the reason.

Re-run the full set against the tree you are actually submitting. A figure
carried over from an earlier tree is an assertion about a state that no longer
exists.

### Disposable Linux Test Server (`oracle-test` / `138.2.182.39`)

A dedicated, explicitly disposable Linux test server (`oracle-test` / `138.2.182.39`)
is available with administrative access for isolated test execution and system drills.
See canonical [`docs/operations/disposable-test-server.md`](../docs/operations/disposable-test-server.md)
for environment specifications, safe synchronization procedures, and test execution commands.

## Contributor and agent workflow

Before editing:

1. read this file, `docs/implementation-plan.md`, relevant modules,
   `.env.example`, and current tests;
2. check `git status` and preserve unrelated user changes;
3. trace the complete path from input through mutation and persistence;
4. identify the applicable rule and existing behavior; and
5. state assumptions when requirements are genuinely ambiguous.

Work within one approved implementation-plan milestone or an explicitly scoped
slice of it. Do not silently continue past a review gate. Stop for maintainer
direction when a decision changes architecture, data authority, authorization,
privacy, production behavior, or migration/rollback strategy.

While editing:

- keep changes scoped and avoid opportunistic rewrites;
- separate mechanical refactors from behavior changes;
- add or update tests with the implementation;
- update documentation, configuration examples, migrations, and adapters when
  their contracts change;
- never mutate live services or production data during development; and
- never bypass authorization, validation, audit logging, or failing checks to
  make a feature appear complete.

Before handing off — the `handoff-checklist` skill carries this list and the
plan's §16.3 report contents together, and does not replace either:

1. run narrow relevant tests, then the full available suite;
2. run configured formatting, linting, and type checks;
3. review the diff for secrets, generated files, unrelated changes, unsafe
   logs, and migration reversibility;
4. report commands run and checks that could not be run; and
5. call out deployment, configuration, data migration, and rollback steps.

Do not claim a check passed unless it was actually run.

At the review gates named in `docs/implementation-plan.md`, provide a complete
handoff and wait for the required review. Blocking findings involving security,
data integrity, authorization, rule correctness, migrations, atomicity, or
production reliability must be fixed and re-reviewed before dependent work
continues.

## Definition of done

A change is complete when its behavior is supported by an identified rule or
requirement, core logic is reusable outside Discord, authorization and failure
modes are handled, relevant tests pass, secrets and player data remain safe,
operational changes are documented, and every data change has a tested
migration and rollback or recovery story.
