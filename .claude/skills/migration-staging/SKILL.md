---
name: migration-staging
description: Stage a database schema or data migration reversibly for the Freedom Blades platform. Use when adding or changing anything under migrations/, altering the PostgreSQL schema, planning a Sheets-to-database cutover, or handling dual writes, imports and reconciliation. Covers the seven reversible stages, the never-edit rule and the retirement gate.
---

# Migrating data and schema

**This skill is a procedural aid, not a source of rules.** The authority is
`.agents/AGENTS.md` "Database migration" and the phase contracts in
`docs/implementation-plan.md`. If this file disagrees with either, they win.

## Two absolutes

* **Never edit an applied migration.** Add a new one. Several migrations in this
  repository carry that rule in their own docstrings.
* **Do not delete the Sheets adapter, its credentials or the rollback path**
  until the verification and retirement gate in `docs/implementation-plan.md`
  §15.1 has closed and been approved.

## The seven reversible stages

Migrate in this order. Each stage is independently reversible.

1. Extract repository interfaces and characterize existing Sheet behavior.
2. Add the database adapter and schema **without changing production reads**.
3. Build a repeatable, dry-runnable import with validation and a report.
4. Shadow-read or reconcile database results against Sheets.
5. Cut reads over behind configuration or feature flags.
6. Cut writes over with backups and a rollback procedure.
7. Keep Sheets read-only for a defined verification period, then retire its
   credentials and adapter.

## Schema requirements

* Store Discord snowflakes as 64-bit integers or canonical strings, never 32-bit.
* Use UTC timestamps and integer copper pieces for money, never a binary float.
* Add foreign keys, uniqueness rules, check constraints, and optimistic
  concurrency or version fields wherever bot and web edits can collide.
* Keep audit and transaction history append-only. Corrections are explicit
  compensating actions, not erased history.

## Dual writes

Avoid an indefinite dual-write period. If a short one is necessary: make one
store authoritative, record failures durably, reconcile automatically, and
document recovery. Imports must be idempotent and must retain the mapping from
Sheet rows to stable database IDs.

## Testing a migration

* Database integration tests exercising **real migrations and constraints**.
* Migration tests using anonymized representative rows, never real player data.
* A drill for backup and restore where the phase requires one.

Every data change needs a tested migration **and** a rollback or recovery story
before it is done.

## Stop conditions

Stop and ask a maintainer before: applying a migration to any non-disposable
database; changing data ownership or authority; a cutover or rollback rehearsal
against live state; or any migration whose gate has not been approved.
