# Claude implementation prompt — Phase 2 I-02 Foundry snapshot milestone

Continue work in `/opt/discord-bots/freedom-bot`.

Issue I-01 is closed: Codex independently reviewed the mapped-name normalization
correction, Peter Duscha accepted it on 2026-08-02, and commit `1695122` is the
accepted starting point. Do not reopen or weaken that fail-closed identity
policy.

Your objective is to implement and prepare independent-review evidence for
**I-02: the incomplete Phase 2 Foundry snapshot milestone**. This work may make
I-02 technically ready for review, but it does not authorize you to close the
issue, approve the Phase 2 gate, conduct the supervised real-snapshot rehearsal,
or begin Phase 3. Those decisions and operational actions belong to the named
maintainer roles.

Do not begin the Phase 3 website UI, Phase 5 command migrations, the magic-item
catalogue, or the Phase 7 live Foundry connector. Do not commit, push, stash,
reset, discard, or overwrite unrelated work. Inspect the actual worktree before
acting and preserve anything that appeared after commit `1695122`.

## Delivery sequence and review stops

Phase 2 is managed as five evidence-bearing packages. Treat the accepted Sheet
identity slice as the existing portion of package 2.4; do not mistake it for the
Foundry milestone. Implement I-02 in this order:

1. **2.1 — immutable artifact, parser, exporter contract and exhaustive field
   profile**;
2. **2.2 — preview, mapping, reconciliation, snapshot-only projections and
   idempotent import**;
3. **2.3 — correction, current-role authorization and append-only audit
   controls**;
4. **2.4 — decide and document the narrow Sheet/manual bootstrap boundary,
   retaining only what the accepted field profile needs**; and
5. **2.5 — PostgreSQL concurrency, runtime-role, failure/recovery and operational
   evidence, followed by a handoff for the maintainer-supervised real-snapshot
   rehearsal**.

Before editing, write a package-level plan with dependencies, explicit scope
exclusions, three-point effort ranges, confidence, test/evidence mapping and
review/remediation allowance. At the end of each package, run its narrow tests
and inspect the diff before continuing. If implementation reveals a decision
that would change data authority, correction semantics, privacy/retention,
authorization, schema identity, or rollback strategy, stop and ask the
maintainer; do not choose policy by convenience.

## Required reading and initial audit

Before planning or editing:

1. Read `AGENTS.md` and `.agents/AGENTS.md` completely.
2. Read `docs/implementation-plan.md` completely, especially §§6.1–6.5,
   Phase 2, Phase 3, §13.3 and §15.
3. Read `docs/adr/0006-foundry-integration-boundary.md` completely.
4. Read `docs/discovery/foundry-mapping.md`,
   `docs/rules/field-ownership.md`, `docs/discovery/sheet-inventory.md`,
   `docs/discovery/open-decisions.md`, and the current Phase 2 submission.
5. Inspect `git status`, the complete diff, migrations, database tables,
   repository interfaces, import services and tests.
6. Trace the current Sheet importer and identify exactly which fields it imports;
   do not assume its existing scope matches the amended plan.
7. Do not read `.env`, credentials, raw player exports, live Foundry LevelDB,
   live Google Sheets, Discord, or a production database.

Prepare a short working plan mapped to the Phase 2 acceptance criteria. Work
only within the gate after completing the audit.

## Maintainer rulings that supersede earlier Phase 2 assumptions

- The live Discord bot still depends on Google Sheets. Preserve its connector,
  credentials contract and runtime behavior until the database-backed Manager
  has replaced and verified those paths. Do not scrap the legacy connector.
- Google Sheets is not the ongoing Manager authority. Fields currently owned by
  the Sheet become PostgreSQL authority through validated manual bootstrap or,
  only where genuinely simpler, a narrow one-time import.
- The existing general Sheet-import effort is not automatically approved merely
  because it exists. Reuse only code that serves the amended field profile.
  Remove or de-scope unnecessary Phase 2 Sheet-import code without disturbing
  the legacy bot connector. Explain every retained part.
- The Manager never reads live Foundry and never reads Foundry LevelDB. A Guild
  Council member deliberately creates an offline snapshot artifact.
- The snapshot is immutable and content-addressed. Preserve its original bytes,
  calculate SHA-256 before parsing, and bind preview, import, mapping,
  reconciliation, correction and audit records to that checksum.
- The supervised first import is a one-time bootstrap and needs no separate
  approval. It still records the named supervisor and full safe audit facts.
- Later imports require one currently authorized Guild Council member. No
  second approver or four-eyes workflow is required.
- Phase 2 implements the exporter/importer/application/database contracts. The
  authenticated website controls belong to Phase 3 and must not be scaffolded
  here.
- The initial folder is `Characters (active)`. Folder identity uses the stable
  Foundry folder ID plus its displayed path/name, never the name alone. Phase 3
  will let a Platform Administrator select a folder and a Council member confirm
  the exact preview.
- PostgreSQL is authoritative for Sheet-era and homebrew/platform fields,
  including race/species, class, subclass, background, abilities, feats, level,
  tool/language/special-weapon proficiencies, money, downtime, living cost,
  Moradinium, Bastion state, magic/homebrew items, missions, debt, weekly
  expenses, specials and no-shows.
- Foundry snapshot-only mechanics—such as skill proficiencies, mundane items,
  resistances, speed, conditions and other non-homebrew Actor mechanics—remain
  read-only snapshot inputs. Do not create an independently editable duplicate
  character model for them.
- Database-owned values represented in Foundry are compared. A difference says
  the Foundry Actor is out of date and should be updated manually. Do not write
  back to Foundry in this phase.
- Any one Council member may correct every database-managed current-state field.
  Standard fields use validated correction; identity/progression fields use a
  protected before/after confirmation; transaction/history-backed fields use
  compensating actions. No correction may erase or rewrite history.
- Council members and Platform Administrators can read/search the append-only
  audit history. Neither can modify or delete it through the application.

## Task A — reconcile the Foundry ADR and define the offline export contract

ADR 0006 currently rejects offline snapshot import and says ordinary Actor
exports have `"_id": null`, with the real ID present only in a filename. That
conflicts with the new maintainer ruling and cannot be ignored.

Amend or supersede the affected ADR text explicitly while preserving its still
valid decisions:

- no LevelDB access;
- no Manager-initiated live Foundry access;
- world ID, not instance, defines world identity;
- exact Foundry/system version validation;
- stable platform character IDs independent of Foundry IDs;
- no Foundry write-back in this phase.

Define a versioned, deterministic Council-side export bundle. It must be created
through an explicit Foundry UI/macro/module action using supported Foundry APIs,
not by reading LevelDB. It must include at least:

- exporter schema/version;
- world ID and title;
- Foundry core and game-system ID/version;
- export timestamp;
- folder IDs, names and parent relationships needed to present a folder path;
- every exported Actor's real Foundry `_id`, folder ID and supported field data;
- deterministic encoding/canonicalization rules where required for comparison;
  and
- no credentials, user tokens, chat, journals or unrelated world collections.

Decide and document whether the bundle contains one deliberately selected folder
or a bounded set of folders from which the Manager can select. Preserve the
maintainer requirement that Phase 3 can select the import folder from the
artifact. Reject ambiguous, missing and duplicate Actor/folder IDs.

Do not use or commit real Actor content. Add only small synthetic fixtures shaped
like the contract.

## Task B — create the exhaustive versioned field profile

Update `docs/rules/field-ownership.md` and implement the corresponding typed
profile. Every supported snapshot path must have exactly one snapshot mode:

- `snapshot-only`;
- `compare` against PostgreSQL authority;
- eligible for explicitly selected Council correction; or
- `ignored`.

Every database-managed field must have exactly one correction mode:

- standard;
- protected; or
- compensating.

Requirements:

- Unknown snapshot paths are reported and are never writable.
- A newly supported schema field without a classification fails closed.
- Profile versions are stored on previews, imports, comparisons, calculations
  and snapshot-based corrections.
- Name matching is never identity. Use explicit world/Actor mappings.
- Use stable Foundry identifiers such as class/system identifiers where the
  discovery document says display names are customized.
- Define deterministic normalization and comparison for skill proficiencies and
  magic items. Distinguish `different` from `unable to compare`.
- Magic-item comparisons should use stable catalogue/mapping identity where
  available, with explicit aliases rather than fuzzy name matching.
- Snapshot-only roll inputs cannot be selected for database overwrite.
- Every database-managed current-state field remains correctable by one Council
  member through its assigned domain-aware correction operation.

If a field's ownership or comparison cannot be derived from the maintainer
rulings and existing discovery evidence, mark the exact row unresolved and stop
before enabling apply for that row. Do not silently invent authority.

## Task C — implement immutable snapshot ingestion and reconciliation

Implement the Phase 2 backend/application/database contracts from plan §§6.4,
6.5 and Phase 2:

- bounded safe file ingestion;
- checksum before parsing;
- immutable artifact metadata and restricted artifact storage abstraction;
- parser/schema/world/version/folder validation;
- dry-run/preview with no character or mapping writes;
- explicit stable external mappings;
- deterministic reconciliation report;
- snapshot-only projection/input access for later roll consumers;
- Foundry-out-of-date warnings for database-owned mismatches;
- no implicit deletion/deactivation/unmapping when an Actor is absent;
- atomic apply;
- idempotency;
- optimistic concurrency and stale-preview refusal;
- audit and provenance;
- rollback/recovery documentation.

Preview must bind snapshot checksum, selected folder ID, profile version,
aggregate versions, selected corrections and request/idempotency key. Apply must
recheck all of them. A changed snapshot, folder, profile or database version
makes the preview stale and applies nothing.

Parsing occurs before opening the state-change transaction. Reject oversized,
excessively nested, archive, executable, path-bearing and unknown top-level
input. Never log raw snapshot data or unsafe exception detail.

Do not implement a live HTTP Foundry connector or Foundry write-back.

## Task D — implement correction and audit application contracts

Implement framework-independent Phase 2 services for corrections; leave web
routes/templates for Phase 3.

- One current Council authorization is sufficient.
- Recheck guild membership and Council role at apply time, not only preview.
- Standard corrections validate and require a reason.
- Protected corrections cover name, race/species, class, subclass, background,
  ability scores, feats, level and other profile-marked identity/progression
  fields. Require a dedicated confirmation and show dependent effects, but no
  second person.
- Compensating corrections cover balances, inventory, downtime, missions, debt,
  expenses and other transaction/history-backed state. Append a compensating
  record; never update/delete original history.
- State change, mappings, reconciliation effects, transaction entries and
  success audit commit in one PostgreSQL transaction.
- Audit failure rolls back state. A failed apply writes no success event; after
  rollback it may record one safe attempted/refused event with the same
  correlation ID.
- Repeated/concurrent requests cannot duplicate state or audit effects.
- Every audit record contains the acting Discord user, current authorization
  context, time, source, reason, before/after facts, correlation ID and snapshot
  checksum/profile version where applicable.
- Audit records contain no raw artifact, credential, arbitrary traceback or
  unrelated private Actor data.

Enforce append-only behavior below the service layer. The runtime database role
must have `SELECT`/`INSERT` but not `UPDATE`/`DELETE`/`TRUNCATE` on audit and
transaction-history tables, with constraints/triggers where appropriate. Do not
edit an applied migration; add a new migration if the schema or grants change.

## Task E — constrain Google Sheet bootstrap to the actual need

The legacy bot connector stays. Separately determine whether any of the new
Phase 2 Sheet importer is useful for the finalized field profile.

Default to validated manual bootstrap because the live population is small. If
retaining a narrow one-time Sheet bootstrap:

- it may read only fields explicitly classified as
  Sheet-era/database-authoritative;
- it previews every value and validation issue;
- it writes PostgreSQL only and never writes the Sheet;
- it is unavailable after successful bootstrap;
- it cannot establish ongoing Sheet authority or dual writes;
- it produces the same database state and audit semantics as manual entry; and
- it has regression and PostgreSQL integration tests.

Do not retain a general Sheet importer merely to avoid deleting earlier work.
Do not delete or alter `connectors/sheets.py` or current bot Sheet behavior.
Remove obsolete read-only-credential configuration, CLI, docs and tests if they
have no role after this analysis, while preserving unrelated user changes.

## Task F — one-time supervised bootstrap

Implement bootstrap as an explicit operational mode:

- requires a named supervisor and explicit bootstrap flag;
- validates the exact disposable/approved database target before connecting;
- only runs against an uninitialized Manager dataset;
- creates/imports from the immutable snapshot and any validated manual/narrow
  Sheet-era values;
- records checksum, folder, profile, supervisor, time, result and correlation;
- disables itself after the first successful initialization; and
- cannot be used as an authorization bypass later.

No real import is authorized during development. Provide the command/service and
operations procedure; the maintainer-supervised real rehearsal is a separate
review-gate check.

## Required tests and gate evidence

Implement every mandatory Phase 2 test listed in the amended plan. At minimum,
cover:

- valid synthetic preview/apply and bootstrap;
- checksum tampering and immutable-artifact identity;
- malformed/oversized/nested/path-bearing/unsupported input;
- wrong world/version/system/folder/schema;
- missing/duplicate/ambiguous Actor and folder mappings;
- rename under stable Actor ID and absence without deletion;
- exhaustive field classification and unknown-path fail-closed behavior;
- database-owned match/mismatch warnings;
- snapshot-only skill/stat roll inputs and provenance;
- missing roll inputs never silently default;
- standard/protected/compensating corrections for every database-managed field;
- one Council member allowed; ordinary/revoked user denied;
- required reason and protected confirmation;
- stale previews after snapshot/folder/profile/database changes;
- retries, duplicate submissions and real concurrent applies;
- injected parser, constraint, state-write and audit-write failure;
- one-transaction rollback and no false success audit;
- PostgreSQL uniqueness, optimistic locking, idempotency and mapping constraints;
- runtime-role denial of audit/history update, delete and truncate;
- audit read/search authorization at the application/repository boundary;
- safe logging with synthetic secret/player-data canaries; and
- manual versus retained narrow Sheet-bootstrap equivalence, if retained.

Use table-driven coverage tied to the field profile so a new field cannot be
added without a correction/ownership test.

Run narrow tests first, then the full available suite. Run PostgreSQL integration
tests only against the repository's validated disposable test database. Do not
read `.env` or substitute SQLite for PostgreSQL claims. Run migration upgrade,
downgrade/recovery and drift checks, `compileall`, configured formatter/linter/
type checks, and `git diff --check`. Do not install unconfigured tooling merely
to claim a check.

Produce the §13.3 traceability table mapping every Phase 2 acceptance criterion
and mandatory scenario to a named test or supervised operational check. Report
exact commands and passed/failed/skipped results. A mock call does not prove a
PostgreSQL constraint, role permission, transaction or concurrent outcome.

## Documentation and handoff

Update the implementation plan only where implementation reveals a genuine
contradiction; do not weaken its acceptance criteria. Update the ADR, field
profile, operations documentation and Phase 2 submission so they describe the
actual implementation and current maintainer rulings.

The old Phase 2 submission and old Claude prompt contain obsolete Sheet-first
assumptions. Do not copy their conclusion that the Sheet slice closes Phase 2.

Before handoff:

- review the full diff for secrets, raw snapshots, player data, unsafe logs,
  generated files and unrelated changes;
- list every retained, removed and repurposed part of the earlier Sheet work;
- prove the legacy bot connector and behavior remain intact;
- report migrations and recovery steps;
- report the real-snapshot rehearsal as pending unless the maintainer separately
  performs it;
- state each unmet acceptance criterion plainly;
- do not claim Phase 2 closed unless every criterion and required gate check is
  satisfied;
- do not begin Phase 3; and
- do not commit or push.

Stop at the Phase 2 review handoff for independent Codex review and maintainer
acceptance.
