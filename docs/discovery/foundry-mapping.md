# Foundry VTT Field Samples and Mapping

Status: **VERIFIED 2026-07-30.** E-2 is satisfied. The maintainer supplied two real
Actor exports (a level-9 Paladin, 128 items; a level-14 Sorceress, 364 items), and
every path in §4.2 was checked against both.

- **Verified** (§2, §3): deployment baseline and topology, from configuration
  manifests.
- **Verified** (§4): the field mapping, against two real documents. Most paths held;
  **five corrections** were needed and are marked **F-F1**–**F-F5** below. One of them
  reverses a §4.3 claim outright.

The exports were read for structure only; per `.agents/AGENTS.md` the committed
fixture is hand-written to match rather than derived from them, and neither export is
committed.

## 1. What was and was not done

**Done.** The deployment baseline was verified by reading two manifest files —
`worlds/the-guild/world.json` and `systems/dnd5e/system.json`. These are
configuration manifests containing no player or character data.

**Also done, 2026-07-30.** Two real Actor documents were read — **exports the
maintainer supplied**, not world data — and every path in [§4.2](#42-character-mechanics--verified-against-two-real-actors)
was checked against them. They were read for structure only, no value from either is
reproduced here, and both are held outside the repository (see
[fixture-strategy.md §4](fixture-strategy.md#4-obtaining-a-real-shape--satisfied-2026-07-30)).

**Deliberately not done.** The live world databases under `worlds/the-guild/data/`
were never opened.

`.agents/AGENTS.md` permits offline read-only snapshots only for
*maintainer-authorized* discovery, and no such authorization existed for this
milestone. The operative reason is technical rather than a privacy one: the servers
were running, so the LevelDB stores were held open, and reading them would have been
unsafe as well as unauthorized. Supplying an export sidesteps both problems, which is
why it was the route taken. (The maintainer has since confirmed the game data is
fictional characters, not personal information — so the constraint here is the
authorization rule and the live-database rule, not a data-sensitivity one.)

**Consequence.** The field mapping in [§4](#4-field-mapping) started as a proposal
derived from the `dnd5e` 5.3.3 system's documented data model and from what the
Freedom Blades rules and the Google Sheet require. **It is now verified against two
real documents**, and five of its paths were wrong — see F-F1–F-F5. Each correction is
recorded in place with the original reasoning kept.

## 2. Verified deployment baseline (historical Phase 0 observation)

This section records the deployment inspected on 2026-07-29. The current
observed reference moved to Foundry `14.367` on 2026-08-27; the compatibility
policy is the scoped baseline v1.6 policy in §2.1. The original observation is
retained rather than rewritten as if Phase 0 inspected the later deployment.

Read from `/home/foundry/foundry1/foundrydata/Data/worlds/the-guild/world.json`
and `.../systems/dnd5e/system.json`:

| Property | Value | Matches plan §6.3? |
|---|---|---|
| World ID | `the-guild` | ✓ |
| World title | `The Guild` | ✓ |
| System | `dnd5e` | ✓ |
| System version | `5.3.3` | ✓ |
| Core version | `14.365` | ✓ |
| World compatibility | minimum `14`, verified `14.365` | — |
| System compatibility | minimum `13.347`, verified `14` | — |

Every value asserted in the then-current `docs/implementation-plan.md` §6.3 was
confirmed. The source
folder **`Characters (active)` is confirmed by the maintainer**, with no sub-folders —
one character (Xirla) is in the sheet but not in that folder, so the sheet↔Foundry
correspondence is **not** 1:1 and the importer must treat an unmapped character as an
expected case, not an error.

The world's collections are: `actors`, `cards`, `combats`, `effects`, `fog`,
`folders`, `items`, `journal`, `macros`, `messages`, `playlists`, `scenes`,
`settings`, `tables`, `users`. Only `actors`, `items` and `folders` are relevant
to the platform; `journal` is relevant to Bastion documentation (rules §7.3 p.30).

### 2.1 Version negotiation requirement

The system declares `compatibility.verified: "14"` while the core is `14.365`,
and the system's own minimum is `13.347`. The Phase 7 connector must therefore
negotiate on **two** axes — core version and system version — and treat the
tuple, not either value alone, as the compatibility key.

**Resolved 2026-07-30 and superseded 2026-08-27
([OD-14](open-decisions.md), controlled baseline v1.6).** The connector remains
built for **one deployment, not for distribution**, with scoped ranges:

| Aspect | Policy |
|---|---|
| Supported deployment | Exact world/system identities; numeric Foundry **`14.x`**; numeric dnd5e **`5.3.x`**. The observed reference is core `14.367`, dnd5e `5.3.3` |
| Anything else | **Fail closed** with a diagnostic naming observed and accepted series. No degrading, guessing or partial import (plan §12 Phase 7) |
| On a Foundry or system upgrade | In-range builds/patches proceed through real-export and preview validation. A generation, minor/major, identity or malformed-version change stops synchronization pending a controlled decision |
| Backwards compatibility | None is owed. There is no third-party consumer to support |

The per-instance upgrade path in §3 is what makes this a live concern: one
instance can be upgraded against the shared world without the others, so the
connector may meet an unexpected tuple even though the world never changed.

## 3. Topology: one shared world behind three instances

**Corrected 2026-07-30 on a maintainer answer.** Phase 0 originally reported this
as *"three instances, three `the-guild` worlds"* and treated choosing the
authoritative one as a blocker. That reading was wrong.

Three Foundry servers run on this host (ports 30001–30003), but
`/home/foundry/shared/worlds` is **bind-mounted** onto each one's
`foundrydata/Data/worlds`. There is one world directory, seen three times.

Verified: all three paths to `the-guild` resolve to **inode 4388511 on device
64769**, and `/etc/fstab` declares the binds. The maintainer confirms this is
deliberate — the game *The Guild* is shared, and the instances are alternative
front doors to it.

**Consequences for the platform, and they are simplifying:**

| Original assumption | Corrected |
|---|---|
| Three parallel copies; importing from the wrong one yields stale data | One store. No stale-copy risk exists |
| A maintainer must declare an authoritative instance ([OD-12](open-decisions.md)) | **Resolved.** There is nothing to choose. The *world* is the identity; an instance is a transport endpoint |
| `external_worlds` keys on **(instance, world ID)** | Keys on **world ID**. The instance is connection configuration, not identity — see §4.1 |
| One service principal per instance, three in total | One principal for the connector, because there is one world |

**What genuinely is per-instance:** the Foundry binary
(`/home/foundry/foundryN/foundry/`) and the system/module trees
(`/home/foundry/dist/foundryN/{systems,modules}`). Observed 2026-07-30:

| Instance | Core | `dnd5e` |
|---|---|---|
| foundry1 | 14.365 | 5.3.3 |
| foundry2 | 14.365 | 5.3.3 |
| foundry3 | 14.365 | 5.3.3 |

Identical today, **independently upgradable tomorrow.** One instance can be
upgraded without the others, against the same world. This is why §2.1's
(core, system) validation survives the correction: the world no longer varies, but
the code reading it still does.

**Operational constraint (topology F-2a).** Foundry holds the world's LevelDB
stores open while the world is launched, and LevelDB takes an exclusive lock. On
this local bind mount the lock works, so only one instance can host `the-guild` at
a time and a second launch attempt fails cleanly rather than corrupting anything.
The connector's endpoint is therefore *whichever instance currently hosts the
world*, and it must be repointable by configuration without touching world or
actor identity.

The three instances are reverse-proxied by Caddy as `foundry1`/`foundry2`/
`foundry3.rpgworld.org`. See [operations/topology.md](../operations/topology.md).

## 4. Field mapping

Direction is from the platform's point of view. "Owner" values are proposals
that [rules/field-ownership.md](../rules/field-ownership.md) carries forward.

**Verified against two real actors, 2026-07-30.** The five corrections:

| # | Finding | Consequence |
|---|---|---|
| **F-F1** | **A manual export has no `_id`.** Both files carry `"_id": null`; the real ID survives only in the *filename* (`fvtt-Actor-…-52ywI3ttEcgf9iBv.json`) | Mappings cannot be established from exports. They must come from the module/API — which is what [ADR 0006](../adr/0006-foundry-integration-boundary.md) already requires, now for a second reason |
| **F-F2** | **Derived values are absent, not just derived.** `abilities.*.mod`, `attributes.hp.max`, `attributes.ac.flat` and `attributes.prof` are all missing or `null`; `details.level` does not exist | The platform must **compute** the ability modifier from `.value`, not read it. AC may even be a custom formula string (`@attributes.ac.armor + @abilities.cha.mod`) |
| **F-F3** | **`system.tools` keys are artisan names — the same vocabulary as Sheet columns W/X** | The tool code table is shared with Foundry rather than translated. See §4.6 |
| **F-F4** | **Bastions *are* represented in Foundry, richly.** §4.3 claimed they were not | A whole contested group the matrix did not have. See §4.5 |
| **F-F5** | **An actor is 1.1–3.3 MB of JSON**, with no embedded images — it is genuine item volume (172 consumables on one) | Phase 7's snapshot endpoint needs request limits sized for megabytes, and content-hash idempotency hashes megabytes per actor |

Also observed: class **`name` is player-customised** while `system.identifier` is
stable — `name: "Sorceress"` / `identifier: "sorcerer"`, `race: "Tiefling; Infernal
Legacy"`, `subclass: "Pyromancer (PSK)"`. **Map on `identifier`, never on `name`.**

`ownership` was `{"default": 0}` on both, carrying no per-user grants — which
independently confirms §5: Foundry holds nothing that links an actor to a person.

### 4.1 Identity and mapping keys

| Platform concept | Foundry source | Notes |
|---|---|---|
| `external_actor_mappings.external_actor_id` | Actor `_id` (16-char alphanumeric **string**, not a UUID) | Stable per world; **not** stable across a world export/import |
| `external_worlds.world_id` | `world.json` → `id` (`the-guild`) | **The world is the identity.** Do *not* compose it with an instance identifier — the world is shared by all three instances (§3). The instance is connection configuration |
| `external_worlds.system_id` / `system_version` | `dnd5e` / `5.3.3` | Store per sync run for auditability |
| `characters.id` | — | Platform-side UUID; never derived from a Foundry ID |
| Foundry user ↔ Discord user | **no reliable link exists** | See §5 |

The Foundry `_id` is the mapping key, not the identity. Plan §7.6 requires stable
application IDs; a Foundry world rebuild would invalidate every `_id`, so
`external_actor_mappings` must additionally record a human-verifiable
fingerprint (name plus class/level at mapping time) to support re-linking.

**Maintainer requirement, 2026-07-30:** *"You also have to write the UUID from foundry
in there."* Confirmed — the Foundry actor ID is recorded against the character, and
looking up a character shows its Foundry actor. It is held in this mapping row rather
than as a column on `characters` because a character has two external identities
(Foundry actor *and* sheet row), because a world rebuild invalidates every `_id` and
re-linking should replace a mapping rather than edit the character, and because the
link is a Council action that has to stay auditable
([ADR 0006](../adr/0006-foundry-integration-boundary.md)).

Note the type: the Foundry `_id` is a short alphanumeric **string**, so the column is
`TEXT`, not `uuid`. The UUID in this design is the platform's own `characters.id`
([ADR 0003](../adr/0003-postgresql-and-alembic.md)).

### 4.2 Character mechanics — **verified against two real actors**

These correspond to the plan §6.1 row *"Ability scores and character
mechanics — Foundry"*.

| Platform field | Foundry path (dnd5e 5.3.3) | Verified 2026-07-30 | Owner |
|---|---|---|---|
| ability scores | `system.abilities.<abbr>.value` | ✅ `{str: 16, dex: 8, … cha: 20}` | Foundry |
| ability modifiers | **absent** — compute as `(value − 10) // 2` | ❌ `.mod` not in the document (F-F2) | Derived |
| proficiency bonus | **absent** — compute from level | ❌ `attributes.prof` not present | Derived |
| hit points, current | `system.attributes.hp.value` | ✅ `76`, `86` | Foundry |
| hit points, max | **absent** — `hp.max` is `null` | ❌ computed at runtime | Derived |
| temp hit points | `system.attributes.hp.temp` | ✅ `5`, `10` | Foundry |
| armour class | `system.attributes.ac` = `{calc, flat, formula}` | ⚠️ `flat: null`; one actor is `calc: "custom"` with a **formula string** `@attributes.ac.armor + @abilities.cha.mod` | Derived |
| skills | `system.skills.<key>.value` | ✅ `0`/`1` observed; `2` = expertise | Foundry |
| species | `items[]` `type == "race"` | ✅ `"Human"`, `"Tiefling; Infernal Legacy"` | Foundry |
| classes and levels | `items[]` `type == "class"` → `system.levels`, `system.identifier` | ✅ Paladin/9, Sorceress/14 — **key on `identifier`** | Foundry, subject to review |
| subclasses | `items[]` `type == "subclass"` | ✅ `"Oath of Redemption"`, `"Pyromancer (PSK)"` | Foundry, subject to review |
| background | `items[]` `type == "background"` | ✅ `"Entertainer"` | Foundry |
| character level | sum of class levels | ✅ single-class on both | Foundry, subject to review |
| **D&D experience** | `system.details.xp.value` | ✅ `48000`, `140000` — **see the warning** | Foundry |
| portrait | `img` | ✅ a path; no embedded image data | Display-only |
| name | `name` | ✅ | Foundry, subject to review |
| character detail | `system.details.*` — age, alignment, appearance, biography, bond, eyes, faith, flaw, gender, hair, height, ideal, skin, trait, weight | ✅ all present | Display-only |
| weapon / armour proficiency | `system.traits.weaponProf`, `system.traits.armorProf` | ✅ present — feeds [OD-13](open-decisions.md) | Contested |

> **⚠️ "Experience" means two different things, and they must never be reconciled.**
> Sheet column G is *"Experience (Missions)"* — a mission count driving level and badge
> through the homebrew tables (§3.1 p.9–10). Foundry's `system.details.xp.value` is
> standard D&D XP (48 000 and 140 000 on these actors). Same word, unrelated
> quantities. A field named "experience" on both sides is precisely what an importer
> matches by name and gets catastrophically wrong.

**Classes carry customised display names.** `name: "Sorceress"` with
`identifier: "sorcerer"`; `"Tiefling; Infernal Legacy"`; `"Pyromancer (PSK)"`;
`"Guild Artisan: Alchemists and Apothecaries"`. **Map on `system.identifier`, never on
`name`** — the same lesson as character names, one level down.

**Modules in play**, from actor `flags`: `midi-qol`, `tidy5e-sheet`,
`optional-rules-dnd5e`, `scene-packer`, `sequencer`, `core`, `dnd5e`. A Freedom Blades
module must coexist with these, and `tidy5e-sheet` replaces the character sheet UI —
relevant to where Phase 7 would surface anything in the client.

**Ability modifiers are what the platform actually needs.** The rules require a
Learning Roll to use the base ability modifier with no proficiency, feats, items
or features (§6.2 p.15) — precisely what `system.abilities.<abbr>.mod` gives
before any active-effect layering. Importing ability scores would let the
platform compute all three roll types authoritatively instead of trusting the
`modifier` option that `/work` and `/learn` accept today.

The Earning Roll additionally needs the proficiency bonus and tool proficiency,
both derivable from the same import.

### 4.3 Fields the Sheet owns — never overwritten by Foundry

Every Freedom Blades homebrew concept lives only in the Sheet today and has no
Foundry representation. These become PostgreSQL-owned:

`missions`, `last_played`, `badge`, `no_shows`, `active_flag`, `living_weeks`,
`downtime`, `downtime_progress`, `crp`, `masterpiece`, `debt`,
`aristocratic_flag`, and all Discord ownership links.

A Foundry sync must **never** write to any of these, and a Foundry-side value
that appears to correspond to one must be ignored rather than reconciled.

> **F-F4 — correction, 2026-07-30.** This list originally included
> `bastion_flag`, `bastion_maintenance` and `bastion_turn_flag` on the stated
> grounds that *"every Freedom Blades homebrew concept lives only in the Sheet
> today and has no Foundry representation."* **That is false for Bastions.**
> `dnd5e` 5.3.3 models them natively, and one of the two sample actors has a named
> Bastion with eight facilities. Moved to §4.5, which is now a contested group
> rather than a footnote.

### 4.4 The three genuinely contested field groups

Plan §6.1 already flags these as *"explicit reconciliation required"*. The
reasons are specific and each needs a decision.

#### Currency — [OD-13](open-decisions.md)

| Side | Representation |
|---|---|
| Foundry | `system.currency.{pp,gp,ep,sp,cp}` — **five** denominations, including electrum |
| Sheet | four columns P–S — **no electrum** |
| Platform | one integer copper balance plus a transaction ledger |

Three problems were identified. **The first is now resolved:**

1. ~~**Electrum has no home.**~~ **Resolved 2026-07-30.** The maintainer confirms
   **no actor holds electrum and the game does not use it** — it never comes up.
   The Sheet has no electrum column and the rules never mention it, so all three
   systems now agree.

   Two things follow. First, the importer needs no conversion policy: a nonzero
   `system.currency.ep` is an **anomaly**, and the correct behaviour is to warn and
   refuse to convert, never to silently fold it in at 5 sp. Second — flagged by the
   maintainer and worth recording, because it is exactly the kind of thing an
   importer gets wrong — **"Electrum" is also a badge tier name** in the Freedom
   Blades badge table (rules §3 p.8–9, Iron→Adamantine). A cell reading `Electrum`
   in Sheet column **E** is a *badge*, with no relationship to currency. The two
   must never be conflated by a name match.
2. **Foundry currency is player-editable in the client.** Players update their own
   Foundry sheets (rules §6 p.14 makes this explicit: *"You are responsible for
   updating your personal character sheet in Foundry"*). Treating Foundry as
   authoritative for money would let any player mint gold.
3. **The Sheet is authoritative today** and is the store the Council reconciles
   against.

**Recommendation:** currency is **PostgreSQL-owned** after migration, per plan
§6.1. Foundry differences produce a reconciliation *report*, never a write, in
either direction, until a Council decision says otherwise.

#### Inventory and notable items — [OD-13](open-decisions.md)

| Side | Representation |
|---|---|
| Foundry | full `items[]` array with type, rarity, quantity, weight, attunement, description |
| Sheet | column AA — rarity-grouped **names only**, and only "notable" items |
| Platform | `items` + `character_items` |

The Sheet holds a curated subset; Foundry holds everything including mundane
gear. There is no key to match them beyond fuzzy name comparison, and the Sheet
round-trip already discards description, benefits and link
(see [sheet-inventory.md §3.4](sheet-inventory.md#34-column-aa--notable-items)).

**Recommendation:** import Foundry inventory read-only into a
`sync_snapshots`-backed view for Phase 3's reconciliation page. Do not attempt
automated matching to column AA in Phase 2. Item identity becomes a real problem
only when Phase 9 loot handling needs it, and by then the platform will be
creating items itself.

#### Languages and tool proficiencies — [OD-13](open-decisions.md)

| Side | Representation |
|---|---|
| Foundry | `system.traits.languages.value` (SRD keys) + `.custom`; `system.tools.<key>` |
| Sheet | columns Z and Y — free text |
| Platform | `character_languages`, `character_proficiencies` |

Two mismatches:

1. **Vocabulary.** Foundry uses SRD keys (`common`, `elvish`, `thieves`);
   the Sheet holds whatever a human typed. A code table is required, and it must
   cover the homebrew entries the rules add — *Common Sign Language* and
   *Druidic* appear in the `/learn` dropdown (`ext/commands/learn.py:30`).
2. **Rank has no Foundry equivalent.** Freedom Blades has three artisan ranks —
   journeyman, expert, master (§6.3.3.1 p.16–17). `dnd5e` models tool proficiency
   as proficient / expertise only. **Rank cannot round-trip.** The mapping is
   necessarily lossy: journeyman → proficient, master → expertise, and expert has
   no representation.

**Recommendation:** rank is **PostgreSQL-owned** and one-way-projected to Foundry
if outbound sync is ever enabled. Foundry's proficiency list is imported only as
evidence for a Council reconciliation view.

### 4.6 The tool vocabularies already agree (F-F3)

**The best news in the verification.** `system.tools` is keyed by **artisan name** —
the same vocabulary Sheet columns W and X use
([sheet-inventory.md §3.1](sheet-inventory.md#31-columns-x-and-y--crafting-ranks-and-tool-proficiencies)).
Observed keys across the two actors:

```text
alchemist  calligrapher  glassblower  jeweler  weaver  smith  woodcarver  cook
disg  scrolls
lute  drum  handdrum  flute  horn  lyre
```

So `_clean_tool_name("Calligrapher's Supplies") → "Calligrapher"` lands on Foundry's
own `calligrapher` key. The sheet, the bot and Foundry are describing tools the same
way — the code table is **shared, not translated**.

Three exceptions the alias table must carry:

| Foundry key | Platform artisan | Note |
|---|---|---|
| `disg` | `Disguise` | dnd5e abbreviates; the code does not |
| `scrolls` | `Scroll` | Plural vs singular. `_clean_tool_name` already normalises `Scrolls`/`Scroll`/`Scroll Proficiency` → `Scroll`, so only the Foundry side needs the alias. Note this is a **Freedom Blades homebrew proficiency that exists in Foundry too** |
| `lute`, `drum`, `handdrum`, `flute`, `horn`, `lyre` | *(instruments)* | Not crafting tools. Sheet column Y may list them, and the vocabulary must hold them without implying a crafting rank |

**Proficiency levels confirm the lossy mapping.** `value` is `1` = proficient,
`2` = expertise (observed: `alchemist: 2`). Freedom Blades has **three** ranks —
journeyman, expert, master (§6.3.3.1 p.16–17) — against Foundry's two. Rank cannot
round-trip, exactly as §4.4 predicted, which is why rank stays PostgreSQL-owned.

### 4.5 Bastions — a contested group, discovered 2026-07-30 (F-F4)

**`dnd5e` 5.3.3 has native Bastion support, and it is in use.** Phase 0 asserted the
opposite. Observed on the level-14 Sorceress:

```text
system.bastion = { name: "Hightower Mansion", description: "<p>…</p>" }
items[] where type == "facility"   -> 8 facilities
```

Each facility carries real structure:

| Facility | `type.value` | `type.subtype` | `size` | `order` |
|---|---|---|---|---|
| Arcane Study | special | `arcaneStudy` | roomy | craft |
| Laboratory | special | `laboratory` | roomy | craft |
| Scriptorium | special | `scriptorium` | roomy | craft |
| Storehouse | special | `storehouse` | roomy | trade |
| Stable | special | `stable` | vast | trade |
| Manifest Zone | special | *(empty — homebrew)* | vast | empower |
| Bedroom | basic | `bedroom` | cramped | — |
| Parlor | basic | `parlor` | roomy | — |

**Foundry holds far richer Bastion data than the Sheet does.** The Sheet has three
integers (`bastion_flag`, `bastion_maintenance`, `bastion_turn_flag`); Foundry has
named, typed, sized facilities with assigned orders. That inverts the assumption in
§4.3 for this group.

> **Coverage is partial, and that is the decisive constraint.** The maintainer,
> 2026-07-30: *"not all people enter the bastion facilities in their character sheet,
> but it probably is a good start. We might have to tell everyone to do that."*
>
> So Foundry facility data is **opt-in and incomplete.** Three rules follow, and they
> are not negotiable for Phase 11:
>
> 1. **Absence is not evidence of absence.** A character with no `facility` items may
>    still have a fully built Bastion. No rule check may treat an empty list as a
>    finding, and no import may delete or contradict Sheet-side Bastion state on the
>    strength of it.
> 2. **It is a reconciliation input, never an authority.** Present facilities are
>    useful evidence to show the Council; missing ones are simply unknown. The
>    difference between "no facilities" and "facilities not recorded" must be
>    representable in the data model — a nullable *last observed* rather than a count
>    defaulting to zero.
> 3. **Coverage may improve, so do not design for today's completeness.** If the
>    community is asked to fill these in, the same field graduates from sparse to
>    near-complete without any schema change — which argues for storing what is
>    observed with its observation time, rather than deriving a boolean from it.

Three consequences:

1. **The facility count is checkable against the rules — in one direction only.**
   `models/bastion.py` computes a maximum from level × lifestyle (§7.1 p.29–30, the
   table RC-04 corrected). This actor is level 14 with **6 special** facilities. Because
   coverage is partial, *exceeding* the maximum is a real finding worth surfacing, while
   *falling short* of it says nothing at all.
2. **Phase 11 gets a data source instead of a blank slate.** The special-facility
   engine can seed its vocabulary from `type.subtype` — and the empty subtype on
   *Manifest Zone* shows homebrew facilities exist, so the vocabulary needs an
   "other/homebrew" path rather than a closed enum.
3. **Ownership is complementary rather than contested**, which makes this the
   easiest of the groups — but it still needs its own row in
   [field-ownership.md](../rules/field-ownership.md) rather than a copy of the currency
   one. The Sheet's flags are Council-managed economy state (maintenance weeks, turn
   taken) and stay **database-owned**; Foundry's facilities are the physical build-out
   and are imported **read-only as evidence**, with partial coverage assumed. Neither
   side overwrites the other, and there is no reconciliation *conflict* to resolve —
   only a gap to display.

**On the journal requirement.** Rules §7.3 p.30 asks for facilities to be documented
in `#characters-and-bastions` **and mapped within The Guild in Foundry**, *"generally
in a journal entry"*. In practice they are modelled as facility items on the actor,
which is strictly better — structured rather than prose. The `journal` collection may
still hold Bastion write-ups, but it is no longer the primary source it appeared to be.

## 5. There is no Foundry ↔ Discord identity link

Foundry `User` documents carry a name and role. Nothing in the world data links a
Foundry user to a Discord snowflake.

The mapping must therefore be established **inside the platform**, and the only
trustworthy direction is:

```text
Discord OAuth2 identity  →  platform user  →  Council-managed CharacterAccess
                                                      ↓
                                       external_actor_mappings → Foundry Actor _id
```

The Council links a platform character to a Foundry Actor `_id` explicitly, as an
audited action. Never infer the link from a matching character name — names are
mutable display values (plan §3 principle 6), and the Sheet lookup already
demonstrates the failure mode (`.../command-inventory.md` G-7).

This makes Council character-link management (plan §12 Phase 3) a hard
prerequisite for the Phase 7 connector, which the plan's phase ordering already
reflects.

## 6. Integration constraints carried into Phase 7

Restating from `.agents/AGENTS.md` and plan §6.3, with the specifics this
discovery adds:

| Constraint | Phase 0 note |
|---|---|
| No direct LevelDB access in production | The world DB is held open by a running server; a snapshot read is not merely disallowed, it is unsafe |
| Versioned HTTPS API through a Freedom Blades module | Caddy already terminates TLS for all three instances |
| Compatible-version check, fail safely | Keys on (core, system), **pinned to the deployed tuple**, fail closed — §2.1 |
| Scoped, revocable credentials | **One** service principal — there is one shared world (§3), not three |
| One-way sync first | Read-only snapshots. Of §4.4's three reasons not to write, electrum is resolved; the two substantive ones — player-editable Foundry currency, and the Sheet's present authority — stand |
| Field-level ownership before writes | [rules/field-ownership.md](../rules/field-ownership.md) |
| Duplicate snapshots idempotent | Key on (world, actor `_id`, content hash) |

## 7. What a maintainer had to supply — **all five answered 2026-07-30**

Retained as the record of what was asked and how each item closed. **Nothing in this
section is outstanding.**

| # | Item | Status |
|---|---|---|
| 1 | Which instance is authoritative | **Resolved.** The question does not apply — one shared world, §3. OD-12 closed |
| 2 | The `Characters (active)` folder name, and sub-folders | **Confirmed:** correct, no sub-folders. Both sample actors sit in folder `smob5eya6XVBAuIb` — note the field holds a folder **ID**, not a name |
| 3 | **Actor export validating §4.2's field paths** | **SATISFIED 2026-07-30.** Two exports supplied and checked; five corrections resulted (F-F1–F-F5). OD-30 closed |
| 4 | Whether any actor holds electrum | **Resolved: none does** — `ep: 0` on both, confirming it directly. Electrum is unused in the game |
| 5 | The supported version range | **Resolved:** pin to the deployed tuple, fail closed on anything else. OD-14, §2.1 |

### 7.1 How item 3 was obtained — **historical**

This section described the routes available *before* item 3 was satisfied. In the
event the maintainer took the fallback route and supplied two real exports, which is
why §4.2 is now verified. It is retained because it is the right procedure for the
*next* unverified structure, and because it records the safer route that was
available.

**Preferred route — a purpose-built throwaway actor, which involves no player data
at all.** Create a new actor in a scratch world on the same system version, fill in
only what the platform reads, and export that:

- ability scores; HP; AC; a couple of skills
- `currency` — include a nonzero **electrum** value even though the game does not
  use it, so the importer's warning path can be tested
- one tool proficiency; two languages, one of them homebrew (Common Sign Language
  or Druidic)
- a class item, a race item, and two inventory items of different rarity

This is *synthetic by construction* in the sense
[fixture-strategy.md §1](fixture-strategy.md#1-principle-synthetic-by-construction-not-anonymized-after-the-fact)
requires, and it is the recommended route.

**Fallback route — an anonymised real actor** the maintainer owns. Before it
leaves the machine, strip `name`, `img`, `prototypeToken.name`, all of
`system.details.*` (biography, appearance, trait/ideal/bond/flaw), the whole
`ownership` block and the whole `_stats` block — the last two carry Foundry user
IDs. **Keep the key structure intact:** placeholder values are fine, absent keys
are not, because the field *paths* are the entire point.

**What actually happened.** The two exports were supplied unmodified. They were read
for structure only, never committed, and are now held outside the repository, with a
narrow `fvtt-Actor-*.json` rule in `.gitignore` to keep any future export out of the
index. The committed fixtures — `tests/fixtures/foundry_actor_sample.json` and
`tests/fixtures/foundry_actor_anomalies.json` — were then hand-written to the
**verified** shape and are validated by `tests/test_fixtures.py`. They are the
contract, not a placeholder.
