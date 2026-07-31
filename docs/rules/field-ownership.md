# Field Ownership Matrix

Status: **Approved ownership policy.** Phase 0 deliverable, required by
implementation plan §6.1 before any write is enabled. Character-level ownership
was settled on 2026-07-30; the remaining contested groups were settled by the
maintainer on 2026-07-31.

This document is the authority for what a synchronisation may and may not do to a
field. Plan §6.1 requires it to exist before writes are enabled; plan §12
Phase 7 makes "database-owned values are not overwritten" an acceptance
criterion. Foundry imports of Council-approved shared fields create proposals;
they never overwrite live state without Guild Council approval.

## Ownership classes

Reproduced from plan §6.1 so this document can be read on its own.

| Class | Meaning | Sync behaviour |
|---|---|---|
| **Foundry-owned** | Foundry is authoritative | Database imports changes; database never writes back |
| **Database-owned** | PostgreSQL is authoritative | Foundry differences raise a warning or an approved database update; Foundry never overwrites |
| **Council-approved shared** | Both sides may change it | Differences create an approval proposal; nothing applies without Council approval |
| **Derived** | Calculated from authoritative inputs | Never edited directly on either side; recalculated |
| **Display-only** | Cached for presentation | Safe to refresh at any time |
| **External mapping** | Identity linkage | Managed by the Council; never inferred |

Two rules apply to every row:

1. A Foundry-owned field is still subject to §6.2's conflict record — the
   platform stores external value, internal value, versions, detection time,
   proposed action and resolution for every difference, whatever the ownership.
2. No class permits a **silent bidirectional last-write-wins** (plan §6.2).

## 1. Identity and mapping

| Field | Owner | Rationale |
|---|---|---|
| `characters.id` | Database-owned | Platform surrogate UUID; never derived from an external ID |
| Foundry Actor `_id` | External mapping | Not stable across a world rebuild; needs a re-link fingerprint |
| Foundry world ID + instance | External mapping | Three instances exist — see [OD-12](../discovery/open-decisions.md) |
| `sheet_row_mappings` row index | External mapping | Enables idempotent re-import |
| Discord user snowflake | Database-owned | From OAuth2; never from Foundry |
| `character_access` links | Database-owned | Council-managed and audited (plan §4.2) |
| Character display name | **Council-approved shared** | Foundry is where players rename; the Sheet's column A is the current lookup key. A rename must not silently break either mapping |

Name deserves its class. It is Foundry-authored in practice, but the Sheet uses
it as the primary key and the Council needs to know when it changes. Treating a
rename as a proposal — rather than an automatic import — is what plan §13.2's
mandatory *"Actor renamed"* scenario is testing for.

## 2. Character mechanics — Foundry-owned

Plan §6.1: *"Ability scores and character mechanics — Foundry"*.

| Field | Owner | Notes |
|---|---|---|
| Ability scores | Foundry-owned | Needed to compute Learning Rolls (rules §6.2 p.15) |
| Ability modifiers | Derived | From scores |
| Proficiency bonus | Derived | From level |
| Hit points, AC, speed, senses | Foundry-owned | Display and DM reference only |
| Skill proficiencies and expertise | Foundry-owned | Distinct from *tool* rank — see §5 |
| Species, class, subclass | Foundry-owned, review | Plan §6.1 says "subject to review"; a class change is Council-visible |
| Portrait `img` | Display-only | Safe to refresh |
| Biography / notes | Display-only | Never imported into rule-bearing fields |

**Character level** is a special case, below.

## 3. Level and badge

| Field | Owner | Rationale |
|---|---|---|
| Character level | **Council-approved shared** — OD-15 ruled 2026-07-30 | The platform computes eligibility from mission count; a Foundry/platform difference becomes a Council proposal and never applies automatically |
| Badge | **Derived** | A pure function of level (rules §3 p.8–9). Currently *stored* in Sheet column E and round-tripped by the bot |
| Mission count | Database-owned | Sheet column G; the input to level |
| Cumulative missions | Derived | Rules §3.1 p.9–10 table |
| Guild reward / report reward / max extra reward | Derived | From badge (rules §3 p.8–9); must be stored with a policy version on each settlement |

The level conflict is the most consequential unresolved item in this document.

If Foundry owns level, then a player editing their own Foundry sheet can grant
themselves a level, and the platform will import it — contradicting *"There is no
automatic advancement"* (`.agents/AGENTS.md`) and *"No advancement... is official
until an authorized Guild Council user approves it"*.

If the platform owns level, Foundry and the platform will disagree whenever a
player levels up in Foundry before Council approval, generating a difference on
every sync.

**Maintainer decision, 2026-07-30:** level is **Council-approved shared**. The platform computes
the *eligible* level from mission count; Foundry reports the *actual* level; a
mismatch becomes an approval proposal rather than a silent import in either
direction. This satisfies both the no-automatic-advancement invariant and the
reality that Foundry is where the character actually gets levelled.

No advancement becomes official without the existing Guild Council approval
invariant.

## 4. Currency and resources

| Field | Owner | Rationale |
|---|---|---|
| Coin balance (pp/gp/sp/cp) | **Database-owned after migration** | Plan §6.1. Stored as integer copper plus a `resource_transactions` ledger (plan §7.6) |
| Foundry `system.currency.*` | Read-only evidence | Player-editable in the Foundry client (rules §6 p.14) — cannot be authoritative for money |
| Electrum (`ep`) | **Resolved 2026-07-30 — anomaly** | Absent from the Sheet and the rules, and **unused in the game** (`ep: 0` on both sampled actors). A nonzero value is an anomaly: **warn and refuse**, never convert. Note `Electrum` is also a *badge tier* name (§3 p.8–9) — never resolve a denomination by name match |
| Moradinium | Database-owned | Homebrew resource; no Foundry representation |
| Moradinium accounting rate (50 GP) | Database-owned, versioned | Rules §2.1.2 p.4; Council-adjustable, future conversions only |
| Debt (Frank) | Database-owned | Rules §5.6 p.14; Sheet column AC, currently unused |

Currency is where the "never silently apply last-write-wins" rule matters most.
A player's Foundry sheet and the platform balance **will** diverge constantly,
because players spend gold in-session and record it later. The reconciliation
view (plan §12 Phase 3) presents the difference; it never resolves it
automatically in either direction.

## 5. Proficiencies, ranks and languages

| Field | Owner | Rationale |
|---|---|---|
| Artisan tool **rank** (journeyman / expert / master) | Database-owned | Rules §6.3.3.1 p.16–17. No `dnd5e` equivalent exists |
| Foundry tool proficiency / expertise | Read-only evidence | Lossy: journeyman→proficient, master→expertise, **expert has no representation** |
| Crafting reputation points (CRP) | Database-owned | Rules §6.3.3.1 p.17; per tool, fractional (2.5 / 7.5 / 0.5 / 1.5) |
| Languages | **Council-approved shared** | Plan §6.1 requires explicit reconciliation. Vocabulary mismatch: Foundry SRD keys versus Sheet free text |
| Skill proficiencies | Foundry-owned | Distinct from tool rank |
| Weapon proficiencies and masteries | **Council-approved shared** | Rules §6.3.2 p.16 makes these learnable through platform downtime while Foundry records them; a Council member imports Foundry differences as proposals and approves application |

Rank is the clearest example of why one-way sync is the correct starting point.
The platform can project rank *onto* Foundry (as proficiency or expertise) but can
never recover it *from* Foundry, so an import that treated Foundry as
authoritative would silently demote every Expert to Journeyman.

## 6. Homebrew state — database-owned without exception

None of these has a Foundry representation. A Foundry sync must never read or
write them.

| Field | Sheet column | Rule source |
|---|---|---|
| Downtime days | I | §6 p.14 |
| Living weeks (LC) | J | §5 p.12 |
| Lifestyle type | N | §5.2–5.5 p.12–13 |
| Aristocratic lock-out | O | §5.5 p.13 |
| Learning / crafting progress | V | §6.3 p.15, §6.5.2.3 p.22 |
| Masterpiece | AB | §6.3.3.1 p.17 |
| Missions | G | §2.1.1 p.3–4 |
| Last played | H | §2.1 p.3 |
| No-shows | AK | — |
| Active flag | AL | — |
| Campaign counter | not in sheet | §2.1 p.3 |
| Inspiration coins | D | §2.5 p.7 |

## 7. Bastions

| Field | Owner | Rationale |
|---|---|---|
| Bastion ownership flag | Database-owned | Rules §7.1 p.29 ties it to lifestyle |
| Maintenance weeks | Database-owned | §7.2 p.30 |
| Turn available | Database-owned | §7.2 p.30 |
| Facility roster | Database-owned | §7.3 p.30 |
| Max special facilities | Derived | Level × lifestyle (§7.1 p.29–30) |
| `system.bastion` (name, description) | **Read-only evidence** | Native `dnd5e` field; observed populated. Display and reconciliation only |
| `items[]` `type == "facility"` | **Read-only evidence, partial coverage** | Typed, sized facilities with orders. **Resolved 2026-07-30 — see below** |

**Resolved 2026-07-30 — Bastions are *complementary*, not contested.** Phase 0 recorded
that Bastion state had no Foundry representation. That was wrong: `dnd5e` 5.3.3 models
Bastions natively, and one sampled actor has a named Bastion with eight typed facilities
([foundry-mapping.md §4.5](../discovery/foundry-mapping.md#45-bastions--a-contested-group-discovered-2026-07-30-f-f4)).

The two sides describe **different things**, which is why this needs no conflict
resolution:

- the Sheet's flags are Council-managed **economy state** — maintenance weeks owed, turn
  taken — and stay **database-owned**;
- Foundry's facilities are the **physical build-out**, imported **read-only**.

Neither overwrites the other and there is no difference to resolve, only a gap to
display.

**Coverage is partial, and that is binding.** The maintainer: *"not all people enter the
bastion facilities in their character sheet."* Therefore:

1. **Absence is not evidence of absence.** An empty facility list may mean an unrecorded
   Bastion. No rule check may treat it as a finding; no import may contradict Sheet-side
   state on the strength of it.
2. **Store what was observed, with when.** A nullable *last observed* rather than a count
   defaulting to zero — so "none" and "not recorded" stay distinguishable.
3. **Validate in one direction only.** *Exceeding* the level × lifestyle maximum is a
   real finding worth surfacing; *falling short* says nothing.

Coverage may improve if the community is asked to fill these in, and this design absorbs
that without a schema change.

**On the journal requirement.** §7.3 p.30 asks for facilities to be mapped in Foundry,
*"generally in a journal entry"* — which is why an earlier draft of this table made the
Foundry map *Council-approved shared*. In practice they are facility **items** on the
actor, which is structured rather than prose. Given partial coverage, the Foundry record
cannot gate a benefit, so it is evidence rather than a shared-ownership field.

## 8. Inventory

| Field | Owner | Rationale |
|---|---|---|
| Notable items (name + rarity) | **Council-approved shared** | Council links imported Foundry items; differences become approval proposals, never fuzzy-matched automatic mutations |
| Item description / benefits / link | Database-owned | Already lost in the Sheet round-trip; the platform will be the only store that has them |
| Full Foundry inventory | Read-only evidence | Includes mundane gear the Sheet never tracked |
| Attunement, quantity, weight | Foundry-owned | No platform rule depends on them yet |
| Loot lots and claims | Database-owned | Rules §2.1.3 p.4–6; Phase 9 |

**Recommendation for Phase 2:** do not attempt automated matching between Foundry
`items[]` and Sheet column AA. Import both into `sync_snapshots`, present them
side by side in the Phase 3 reconciliation view, and let the Council link them.
Name-based fuzzy matching on player-authored item names will produce false
positives on exactly the high-value items where a mistake matters most.

## 9. Audit and platform-internal

All database-owned, none synced, all append-only in normal operation
(`.agents/AGENTS.md`): `audit_events`, `approval_requests`, `approval_decisions`,
`idempotency_keys`, `outbox_events`, `sync_runs`, `sync_snapshots`,
`sync_differences`, `sync_resolutions`, `sessions`, `service_principals`.

## 10. Contested-field decisions

The ownership classes are settled. They do not themselves enable writes: every
Foundry import or outbound update still requires the Phase 7 authenticated
adapter, validation, proposal, audit and approval controls.

| # | Field group | Question | Open decision |
|---|---|---|---|
| 1 | Character level | **Council-approved shared** | [OD-15](../discovery/open-decisions.md) |
| 2 | Notable items | **Council-approved shared; Council linking** | [OD-13](../discovery/open-decisions.md) |
| 3 | Languages | **Council-approved shared; Council owns additions** | [OD-13](../discovery/open-decisions.md) |
| 4 | Weapon proficiencies and masteries | **Council-approved shared** | [OD-13](../discovery/open-decisions.md) |
| 5 | Character name | Confirm Council-approved shared | §1 |
| 6 | **Classes, race, abilities, feats** | Sheet columns AE–AH hold these **and** so does Foundry. Dual-recorded, newly discovered | §2, F-S4 |

**Closed 2026-07-30:** *Electrum* (unused in the game — anomaly handling, §4);
*Authoritative Foundry instance* (one shared world, so the question does not apply —
[OD-12](../discovery/open-decisions.md)); *Bastions* (complementary rather than
contested, §7).

**Newly opened the same day:** row 6. The Sheet turns out to hold classes/subclasses,
race/species, abilities and feats in columns AE–AH — which §2 assigned to Foundry on the
assumption they existed nowhere else. Ability scores are the useful half: with column AG
available, the platform can compute the Learning-Roll modifier from data it already
holds instead of trusting a player-typed number, **without** waiting for the Foundry
connector.

## 11. Safe synchronization posture

The connector operates under this conservative policy:

- **no outbound writes to Foundry, for any field, in any phase before Phase 7's
  review gate;**
- Foundry imports populate `sync_snapshots` and `sync_differences` only;
- no imported value updates a live character record without a Council approval;
- any field not listed in this document is treated as **database-owned** and is
  never overwritten by an import.

That last rule is deliberate. An unlisted field is an unanalysed field, and the
safe failure mode for an unanalysed field is to leave it alone.
