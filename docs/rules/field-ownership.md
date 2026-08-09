# Field Ownership Matrix and versioned field profile

Status: **Rewritten 2026-08-03 for the accepted Phase 2 remediation plan.**
Character-level ownership was settled on 2026-07-30, the remaining contested
groups on 2026-07-31, and the maintainer rulings of 2026-08-02 changed several
answers again. ADR 0008 was **rejected** on 2026-08-02 and controlled baseline
v1.1/v1.5 removed Sheet-era migration from Phase 2; this document records the
resulting classification.

Profile version: **`2026-08-09.1`** — implemented in
[`domain/foundry_profile.py`](../../domain/foundry_profile.py), with the types
and invariants in [`domain/field_profile.py`](../../domain/field_profile.py).

This document and that module are **kept in step by a test**
([`tests/test_field_ownership_document.py`](../../tests/test_field_ownership_document.py)):
every field in the profile appears in a table here with the same authority and
owning package, and every field named here exists in the profile. A row cannot
be added to one without the other.

## 0. The distinction this document is built on

**Target ownership and current authority are different questions**, and
conflating them is what produced the rejected design.

- **Target owner** is where a field *will* live when the platform is finished.
  It is set by plan §6.1 and does not change because a milestone slipped.
- **Current authority** is who may answer for the field's value *today*. For
  almost every field that is still the accepted legacy path, and will remain so
  until the typed package that owns the field migrates it once into its
  normalized relational model and passes its cutover gate.

The profile classifies **current authority**, because that is what an import is
entitled to act on. Target ownership is recorded below as context and never as
permission.

### What changed at profile version `2026-08-09.1`

Rehearsal A previewed a real 35-Actor export on 2026-08-09 and found ten paths
the profile did not classify (finding
[RA-1](../review/phase-2-rehearsal-a-findings-2026-08-09.md)). The behaviour was
correct — unclassified paths are reported and never written — but Phase 2
acceptance requires the profile to be exhaustive against supported data, and it
was not. Only real data could show this: no synthetic fixture carried these
paths.

| Change | Reason |
|---|---|
| `system.favorites.*` and `system.favorites[].*` classified **snapshot-only** | The character sheet's favourites bar. Foundry client presentation, not game state; nothing rolls from it and the platform will never own it |
| `system.source.*` classified **snapshot-only** | Sourcebook provenance (`book`, `custom`, `license`, `page`, `revision`, `rules`). The platform records provenance by snapshot checksum, not by publisher citation |

Two rules are needed for favourites, not one: a path inside an array element is
spelled `system.favorites[].id`, and the `system.favorites.*` prefix does not
match it, because the next character is `[` rather than `.`. Combining them
would silently restore the finding, so a test pins both prefixes.

No field gained or lost an owner, no authority changed, and nothing became
correctable. Bumping the version makes every outstanding preview stale, which is
the intended effect of any profile edit.

### What changed at profile version `2026-08-03.1`

| Change | Reason |
|---|---|
| The `council-correctable` snapshot mode is **gone** | Phase 2 corrects nothing. A snapshot value has no path into a character field |
| The standard / protected / compensating **correction modes are gone** | Correction workflows belong to the typed package that owns each field (plan §6.2, §12 Phase 5) |
| Almost every field is **`legacy_authority_deferred`** and names its owning package | There is no accepted typed PostgreSQL value to compare against, so "matches" and "differs" are both unearned claims |
| Fields with **no snapshot path were removed from the profile** | They existed here only because they were correctable. The controlled migration register is now their sole governing record |
| The `unresolved` row marker is **gone** | `character.downtime_progress` is simply deferred to package 5.5 like its neighbours. Nothing about it is undecided any more |

## 1. Ownership classes

Reproduced from plan §6.1 so this document can be read on its own.

| Class | Meaning | Sync behaviour |
|---|---|---|
| **Foundry snapshot-only** | read from the immutable snapshot | used for display and calculation; **no** independently editable database representation |
| **Database-owned** | PostgreSQL is authoritative | a Foundry difference warns that the Foundry Actor is out of date; Foundry never overwrites |
| **Council-approved shared** | both sides may change it | differences create an approval proposal — **unused in this profile** |
| **Derived** | calculated from authoritative inputs | never edited directly; corrections change the inputs |
| **Display-only** | cached for presentation | safe to refresh; not stored |
| **External mapping** | identity linkage | Council-established, never inferred |

Two rules apply to every row, unchanged:

1. every difference is recorded with external value, internal value, versions,
   detection time, proposed action and resolution; and
2. no class permits a **silent bidirectional last-write-wins**.

## 2. The two classifications

Every supported snapshot path has exactly one **snapshot mode**:

| Mode | Meaning |
|---|---|
| `snapshot-only` | read for display or calculation; no editable database copy exists |
| `reported` | read and reported against a named profile field |
| `ignored` | deliberately not read |

Every field a reported path feeds has exactly one **authority**:

| Authority | Meaning |
|---|---|
| `database_authority` | an accepted typed PostgreSQL value exists, so a real comparison is possible |
| `legacy_authority_deferred` | no accepted typed PostgreSQL authority exists. The field names the package accountable for migrating it, and **no equality comparison is performed or reported** |

A path says *where a value is read from*. A field says *what the platform is
entitled to claim about it*. `FieldProfile.comparison_for` **raises** for a
deferred field rather than returning "not comparable", so a caller cannot
obtain a value it might mistake for agreement.

## 3. The one field with database authority

| Field | Snapshot path | Comparison | Why it is not deferred |
|---|---|---|---|
| `character.display_name` | `name` | normalized text | The snapshot import **writes it itself** at character creation, from the Actor name. Comparing a later snapshot against a value the platform wrote from the same source is a real comparison |

Two qualifications, both binding:

- **The difference direction is inverted here.** Foundry is where players
  rename, so a difference means the *platform's* display record is stale — not
  that the Foundry Actor is out of date. Phase 2 reports the rename and changes
  nothing.
- **Identity is unaffected either way.** Under [OD-42](../discovery/open-decisions.md)
  display names are not unique identities, multiple characters may share one,
  and identity is the stable character ID and external Actor ID. The Sheet-era
  migration of column A remains package 5.1's; that column and this one are
  different sources for the same database column, and 5.1 resolves the overlap.

## 4. Deferred fields — reported, never compared

Each row is read from the snapshot and reported with **whether Foundry holds a
value for it — not what that value is.** The platform holds no accepted typed
value, so no verdict is offered, and the Foundry value is left out deliberately:
nothing in Phase 2 can act on it, and omitting it keeps Actor field data out of
the reconciliation summary and the audit record built from that summary. The
owning package comes from
[`data-migration-register.md`](../project-management/data-migration-register.md)
and is checked against
[`data-migration-manifest.json`](../project-management/data-migration-manifest.json)
by test.

| Field | Snapshot path | Legacy source | Owning package |
|---|---|---|---|
| `character.race` | `items[type=race].name` | Characters AF | 5.1 |
| `character.class` | `items[type=class].system.identifier` | Characters AE | 5.1 |
| `character.subclass` | `items[type=subclass].system.identifier` | Characters AE | 5.1 |
| `character.background` | `items[type=background].name` | Characters AD | 5.1 |
| `character.ability_scores` | `system.abilities.*` | Characters AG | 5.1 |
| `character.feats` | `items[type=feat].name` | Characters AH | 5.1 |
| `character.level` | `items[type=class].system.levels` | Characters F | 5.1 |
| `proficiencies.tools` | `system.tools.*` | Characters Y | 5.1 |
| `proficiencies.languages` | `system.traits.languages.*` | Characters Z | 5.1 |
| `proficiencies.special_weapons` | `system.traits.weaponProf.*` | no direct column | 5.1 |
| `wallet.balance_copper` | `system.currency.*` | Characters P–S | 5.2 |
| `inventory.magic_items` | `items[type=<physical>].system.rarity`, `.system.identifier`, `.system.source.*` | Characters AA | 5.6a |

Notes that survive from the earlier analysis and still bind:

- **Level is reported, never adopted.** Phase 2 has no write path for it, which
  keeps *no automatic advancement* true by construction rather than by policy.
- **Tool proficiencies are lossy in both directions.** `dnd5e` records
  proficient/expertise against Freedom Blades' three artisan ranks, so an
  "expert" has no Foundry representation. Package 5.1 owns that mapping; a
  naive comparison would have reported every Expert as a difference.
- **Currency is player-editable in the Foundry client**, so it could never be
  authoritative for money. Electrum is unused in the game: a nonzero `ep` is an
  anomaly to report, never to convert.
- **Special weapon proficiencies have no Sheet column.** Package 5.1 may
  populate them only from an approved source, never by inference.
- **Most magic items carry no stable catalogue identity** until the 5.6a
  catalogue exists. That is a second, independent reason this row cannot be a
  comparison today.

## 5. Legacy fields with no Foundry representation

These are **not** in the profile, because no snapshot path feeds them and there
is therefore nothing to classify at the Foundry boundary. They are governed
solely by the controlled migration register, which allocates each to exactly one
accountable package:

`character.long_name`, `character.active`, `character.last_played`,
`character.masterpiece`, `character.specials`, `character.downtime_progress`,
`crafting.artisan_ranks`, `crafting.crp_thousandths`, `lifestyle.type`,
`lifestyle.aristocratic_lockout`, `lifestyle.living_cost_weeks`,
`lifestyle.weekly_expenses_copper`, `bastion.owned`,
`bastion.maintenance_weeks`, `bastion.turn_available`, `wallet.moradinium`,
`wallet.debt_copper`, `wallet.inspiration`, `downtime.thousandth_days`,
`missions.count`, `missions.no_shows`.

They appeared in the previous profile only because it made them correctable.
Removing them removes the only place they could have been mistaken for
something Phase 2 acts on.

`missions.count` deserves its own line: Sheet column G is a **mission count**
and Foundry's `system.details.xp.value` is standard D&D experience. Same word,
unrelated quantities. `system.details.*` is `ignored` partly to prevent exactly
that reconciliation.

## 6. Snapshot-only fields — read, never stored as an editable copy

These are Foundry Actor mechanics. They are available to calculations through
the snapshot, carry the snapshot checksum and profile version as provenance, and
have **no** independently editable database representation.

| Roll input | Snapshot path | Notes |
|---|---|---|
| `skill_proficiencies` | `system.skills.*` | 0 none, 1 proficient, 2 expertise |
| `movement` | `system.attributes.movement.*` | speed |
| `senses` | `system.attributes.senses.*` | |
| `damage_resistances` | `system.traits.dr.*` | |
| `damage_immunities` | `system.traits.di.*` | |
| `damage_vulnerabilities` | `system.traits.dv.*` | |
| `condition_immunities` | `system.traits.ci.*` | conditions |
| `bastion_description` | `system.bastion.*` | native `dnd5e` Bastion name/description |
| `bastion_facilities` | `items[type=facility].*` | **partial coverage — see below** |

Additionally read-only, without a named roll input: hit points, armour class and
remaining attributes; remaining traits including armour proficiency and size;
`system.resources`; mundane inventory (`items[type=<physical>].*` other than the
three magic-item paths); and the race/class/subclass/background/feat item bodies
beyond the fields §4 names.

**A missing snapshot input is a typed refusal, never a default.** Every
extractor answers with a value or an `Unavailable` carrying a reason. Nothing
substitutes zero, an empty set or "no proficiency".

**Bastion facility coverage is partial, and that is binding.** Not every player
records facilities in Foundry. Therefore: absence is not evidence of absence; no
rule check may treat an empty facility list as a finding; no import may
contradict database Bastion state on the strength of one; and the platform
stores *what was observed, with when*, rather than a count defaulting to zero.
Only *exceeding* the level × lifestyle maximum is a real finding.

## 7. Ignored paths

Deliberately not read: `img` (portrait, display-only), `system.details.*`
(biography, appearance and D&D XP), `system.spells.*`, `system.bonuses.*` and
`items[type=spell].*`.

The export contract forbids the bundle from carrying credentials, Foundry user
documents, `ownership`, `_stats`, chat, journals or any other world collection,
and the parser refuses an Actor that carries an unexpected key — so those are
not "ignored", they are **refused**.

## 8. Derived values

- **Badge** is a pure function of level (rules §3 p.8–9). Correcting a badge
  means correcting the level it derives from — in package 5.1, not here.
- **Ability modifiers** are `(value − 10) // 2`, computed by the platform.
  `.mod` is absent from an export entirely (foundry-mapping F-F2).
- **Proficiency bonus**, **hit-point maximum** and **armour class** are computed
  by Foundry at runtime and are absent or null in an export.
- **Cumulative missions** and **guild/report/max-extra reward** derive from badge
  and mission count and are stored with a policy version on each settlement.

## 9. Identity and mapping

| Concept | Owner | Note |
|---|---|---|
| `characters.id` | Database-owned | platform UUID; never derived from a Foundry id |
| Foundry Actor `_id` | External mapping | 16 alphanumeric characters; a mapping key, not an identity |
| Foundry world id | External mapping | **the world is the identity**; the instance is a transport endpoint |
| Foundry folder | External mapping | stable folder **id together with its displayed path**, never the name |
| `sheet_row_mappings` row index | External mapping | enables idempotent re-import |
| Discord user snowflake | Database-owned | from OAuth2; never from Foundry |
| `character_access` links | Database-owned | Council-managed and audited |

**Mapping is established deliberately and never inferred from a name** (ADR
0006). Names are mutable display values, and under OD-42 a display name may be
shared by several characters; an ambiguous name-based candidate lookup fails
closed rather than choosing. This is enforced in code, not only stated here.

## 10. Audit and platform-internal

All database-owned, none synced, all append-only in normal operation:
`audit_events`, `foundry_snapshots`, `snapshot_imports`, `approval_requests`,
`approval_decisions`, `idempotency_keys`, `outbox_events`, `sessions`,
`service_principals`.

Council members and Platform Administrators can read and search this history.
Neither can modify or delete it through the application, and the restricted
runtime database role holds `SELECT` and `INSERT` on those tables and nothing
else.

## 11. Safe synchronization posture

- **no outbound writes to Foundry, for any field, in any phase before Phase 7's
  review gate;**
- a snapshot import populates snapshot, character-identity, mapping and
  reconciliation records; it changes no character game-state field at all;
- **no snapshot value reaches a database game-state field in Phase 2**, by any
  route, for any actor — there is no correction surface to reach it through;
- **any field not classified in this profile is treated as unknown**: it is
  reported, and it is never readable as classified.

That last rule is the deliberate one. An unclassified field is an unanalysed
field, and the safe failure mode for an unanalysed field is to leave it alone
and say so.
