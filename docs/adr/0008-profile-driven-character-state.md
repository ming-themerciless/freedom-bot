# ADR 0008 — Profile-driven storage for database-managed character state

Status: **Rejected 2026-08-02 by Peter Duscha, Acceptance Authority.** The
profile-driven store will not be used as an interim migration target. Sheet-era
state migrates once, into the typed domain model introduced by its owning
package. This ADR is retained as the considered alternative and rationale.

Date: 2026-08-02

Supersedes nothing. Extends [ADR 0003](0003-postgresql-and-alembic.md).

## Context

Phase 2 must let one Guild Council member correct **every** database-managed
current-state field, and plan §12 Phase 2 requires *"correction tests [that]
cover every database-managed field"*. The versioned field profile
([field-ownership.md](../rules/field-ownership.md)) names 34 such fields today:
money, Moradinium, debt, inspiration, downtime, living-cost weeks, weekly
expenses, missions, no-shows, CRP per artisan, magic items, lifestyle, Bastion
flags, proficiencies, ranks, identity and progression facts.

Almost none of them has a Phase 4/5 domain table yet, and plan §7.3 is explicit:

> Do not create every future table in the first migration. Add tables when a
> milestone has a real use case, domain model, and tests.

So Phase 2 sits between two rules. It must be able to correct fields whose
normalized homes belong to migrations that Phase 5 packages own, and it must not
pre-build those homes.

## Proposed decision (rejected)

Store database-managed current state in **two profile-driven tables**, with the
versioned field profile supplying the key set, the value type and the correction
mode:

| Table | Holds | Correction modes |
|---|---|---|
| `character_state_values` | one row per (character, profile field key), with a JSONB value and its own optimistic version | standard, protected |
| `character_balances` + `character_transactions` | a balance per (character, field key, subject), and the append-only movements that produced it | compensating |

Four fields that already exist as `characters` columns — display name, long
name, level and active — keep those columns and are read and written through the
same interface (`application/character_state.py`).

**The profile is the schema.** A field key that the profile does not define
cannot be written: `CorrectionService` refuses it before any repository is
touched, and the correction tests are parametrised off the profile, so a field
added without a correction path fails the suite.

## Why not the alternatives

**Model each field group as its own normalized table now.** This is where the
platform ends up, and plan §7.3 sketches most of it. Rejected *for Phase 2*
because it would mean designing and migrating `wallet_balances`,
`resource_transactions`, `character_proficiencies`, `character_languages`,
`lifestyle_states`, `bastions`, `learning_projects`, `crafting_projects` and
`character_items` — the schema of nine Phase 5 packages — before any of those
packages has a domain model, a rule decision or a use case. Each would be
designed against a guess and migrated twice.

**Correct nothing until Phase 5.** Rejected: it fails a Phase 2 acceptance
criterion outright, and it would leave the supervised bootstrap unable to record
the Sheet-era values it exists to carry over.

**Put the values on `characters` as columns.** Rejected: 34 columns whose
meaning is defined elsewhere is the same coupling with worse ergonomics and a
migration per field.

## Consequences

**Positive.**

- Phase 2 can correct and bootstrap every field the maintainer rulings name,
  with real transactions, real audit and real optimistic concurrency.
- Adding a field is a profile change plus a documentation row — no migration —
  which keeps the field profile genuinely authoritative rather than descriptive.
- Compensating fields get an append-only history from day one, so a Phase 5
  migration inherits history rather than starting one.

**Negative, and stated plainly.**

- **It is a key/value store, and key/value stores hide type errors.** The
  mitigation is that the profile declares a `ValueKind` per field and
  `CorrectionService` validates against it before writing, so an invalid value
  is refused at the application boundary rather than discovered at read time.
  That is a weaker guarantee than a typed column and it should not be described
  as an equal one.
- **The database cannot enforce per-field constraints.** PostgreSQL can check
  that `version >= 0` and that a field key is non-blank; it cannot check that
  `character.level` is between 1 and 20. That check lives in the application,
  which is a real reduction against the Phase 1 pattern where `characters.level`
  has a `CHECK`.
- **A future migration has to move the data.** That is the point at which each
  Phase 5 package normalizes its own fields. The move is mechanical and
  non-lossy — a state row becomes a column, a balance plus its transactions
  become a typed ledger — and the transaction history transfers as history.
- **Query ergonomics are poor** for anything that needs to filter on a value.
  Phase 2 has no such query; Phase 3's read views are per character.

## Maintainer ruling

Peter Duscha rejected the interim representation on 2026-08-02. Phase 2 retains
immutable snapshot ingestion, identity, mappings, reconciliation, provenance
and audit. Each later typed domain package owns its Sheet migration,
reconciliation, corrections, cutover and recovery evidence. Until that gate,
the accepted legacy path remains authoritative for the affected field.

No production data was placed in these tables. The uncommitted implementation
must be reconciled with controlled baseline v1.1 before Phase 2 review resumes.
