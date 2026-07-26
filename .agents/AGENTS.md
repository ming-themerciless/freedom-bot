# AGENTS.md — Freedom Bot

This is the working agreement for humans and coding agents contributing to
Freedom Bot. It applies to the entire repository.

## Product context and direction

Freedom Bot supports the Freedom Blades Discord community. Its game behavior is
based on D&D 5.5 (the 2024 rules) plus Freedom Blades homebrew rules. Today it
is a Python/Pycord bot backed by Google Sheets, with optional Lavalink music.

The intended direction is:

1. keep the live Discord bot reliable;
2. isolate game rules and use cases from Discord and Google Sheets;
3. replace Sheets incrementally with a transactional database;
4. add a purpose-built web interface using the same application logic; and
5. integrate selected data with Foundry VTT through a narrow, authenticated,
   versioned interface.

Treat this as an evolution of a live system, not permission for a rewrite.

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
- `music.py` and `infra/lavalink/`: optional music integration.
- `infra/systemd/`: service deployment files.
- `.env.example`: documented configuration contract.

There is currently no committed automated test suite. Adding one is a priority.

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

PostgreSQL is the default production recommendation: the bot and web app will
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

## Web interface

The web interface and Discord bot must call the same application services. The
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

Tests must never contact live Discord, Sheets, production databases, Foundry,
YouTube, or Lavalink. Do not use real player data or credentials in fixtures.

## Contributor and agent workflow

Before editing:

1. read this file, relevant modules, `.env.example`, and current tests;
2. check `git status` and preserve unrelated user changes;
3. trace the complete path from input through mutation and persistence;
4. identify the applicable rule and existing behavior; and
5. state assumptions when requirements are genuinely ambiguous.

While editing:

- keep changes scoped and avoid opportunistic rewrites;
- separate mechanical refactors from behavior changes;
- add or update tests with the implementation;
- update documentation, configuration examples, migrations, and adapters when
  their contracts change;
- never mutate live services or production data during development; and
- never bypass authorization, validation, audit logging, or failing checks to
  make a feature appear complete.

Before handing off:

1. run narrow relevant tests, then the full available suite;
2. run configured formatting, linting, and type checks;
3. review the diff for secrets, generated files, unrelated changes, unsafe
   logs, and migration reversibility;
4. report commands run and checks that could not be run; and
5. call out deployment, configuration, data migration, and rollback steps.

Do not claim a check passed unless it was actually run.

## Definition of done

A change is complete when its behavior is supported by an identified rule or
requirement, core logic is reusable outside Discord, authorization and failure
modes are handled, relevant tests pass, secrets and player data remain safe,
operational changes are documented, and every data change has a tested
migration and rollback or recovery story.
