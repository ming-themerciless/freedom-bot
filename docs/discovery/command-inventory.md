# Command and Use-Case Inventory

Status: Phase 0 deliverable — **accepted 2026-07-30 after maintainer and
independent Codex review.** Five rule mismatches corrected under the maintainer
ruling of 2026-07-29.

Scope: every slash command registered by `main.py` as of the current
`docs/platform-plan` branch. The former music extension was **removed** from the
implementation under OD-40 (recorded as a duplicate "OD-38" until 2026-08-01) and
is not deferred to a later phase, so it no longer appears in this inventory.

Purpose: satisfy the Phase 0 acceptance criterion *"every current bot command
has known reads, writes, and rule sources"*, and give Phases 4–5 a concrete
migration target list.

## 1. How to read this document

Every game command follows the same shape today:

```text
slash command
  → channel-ID check (only)
  → ctx.defer()
  → Actor(name).load_from_sheet()      # full-range read
  → in-memory mutation on model objects
  → Actor.save_to_sheet()              # fixed 26-cell write
  → rendered follow-up message
```

Two facts apply to *every* mutating command and are therefore not repeated in
each row:

- **Read set is always the same.** `Actor.load_from_sheet()`
  (`models/actor.py:75`) reads `Characters!A3:AL150` in full and linearly scans
  for a case-insensitive exact match on column `A`. There is no per-command
  narrowing.
- **Write set is always the same.** `Actor.sheet_updates()`
  (`models/actor.py:101`) emits one single-cell range per mapped column,
  regardless of which fields the command actually changed. See
  [§4](#4-the-fixed-write-set) — this is a data-integrity finding, not a detail.

## 2. Game commands

### `/info` — `ext/commands/info.py`

| Aspect | Value |
|---|---|
| Channel restriction | **none** |
| Authorization | **none** |
| Reads | `Characters!A3:AL150` |
| Writes | none |
| Rule source | n/a (presentation) |
| Target application service | `GetCharacterSummary` (query) |

Renders name, level, badge, lifestyle, bastion summary, money, Moradinium and
downtime via `Actor.get_summary()`.

**Finding (privacy):** any guild member can read any character's full financial
state from any channel, non-ephemerally. Phase 3/5 must decide whether `/info`
stays open, becomes ephemeral, or becomes owner-scoped. Tracked as
[OD-16](open-decisions.md).

### `/lc` — `ext/commands/lc.py`

| Aspect | Value |
|---|---|
| Channel restriction | `DT_CHANNEL_ID` |
| Authorization | none |
| Options | `character`, `lifestyle?`, `weeks?`, `expenses?` (silver, float) |
| Domain entry point | `Lifestyle.pay_for_weeks()` (`models/lifestyle.py:35`) |
| Rule source | Homebrew §5.2–5.5 p.12–13 (costs); §6 p.14 (DT accrual + 60 cap); §7.2 p.30 (turn availability) |

Mutations:

- `lifestyle_type` (N) — set from the option when supplied, unvalidated against
  the aristocratic lock-out rule;
- `living_weeks` (J) — decremented by `weeks`;
- money (P–S) — deducts `cost_per_week * weeks` gold plus extra expenses;
- `downtime` (I) — **incremented** by `weeks * 5`, capped at 60;
- `bastion_turn_flag` (M) — set to 1 when `living_weeks` reaches 0 and a bastion
  is owned.

**Findings:**

- Downtime is granted *as a side effect of paying LC*. Homebrew §6 p.14 states
  DT is awarded every Sunday by the Guild Council, independently of payment.
  Whether the bot's coupling is intended is [OD-03](open-decisions.md).
- `expenses` is a float in silver; `to_currency()` routes it through
  `Money.from_gold()`, so it is exact at the boundary, but the parameter type
  itself is a binary float.
- The aristocratic one-year lock-out (§5.5 p.13) is not enforced.

### `/mine` — `ext/commands/mine.py`

| Aspect | Value |
|---|---|
| Channel restriction | `DT_CHANNEL_ID` |
| Authorization | none |
| Options | `character`, `downtime?` (default 5) |
| Domain entry point | `Resource.mine_moradinium()` (`models/resource.py:117`) |
| Rule source | Homebrew §6.4 p.18–19 (result table); §6.2 p.15 (Mining Roll = straight d20) |

Mutations: `moradinium` (T) increased, `downtime` (I) decreased. One d20 per
5 DT. Each roll is echoed to `ROLL_CHANNEL_ID`.

Formula `(total + 7) // 4 + (1 if nat20 else 0)` was verified against the PDF
result table for every band (1–4→2, 5–8→3, 9–12→4, 13–16→5, 17–20→6, nat 20→7).
**Correct.**

### `/work` — `ext/commands/work.py`

| Aspect | Value |
|---|---|
| Channel restriction | `DT_CHANNEL_ID` |
| Authorization | none |
| Options | `character`, `tool?`, `modifier?`, `downtime?`, `roll_mode?` |
| Domain entry point | `Resource.earn_money()` (`models/resource.py:131`) |
| Rule source | Homebrew §6.6 p.28 (earnings table); §6.2 p.15 (Earning Roll) |

Mutations: money (P–S) increased, `downtime` (I) decreased.

The band formula `min(2 ** (max(total-6,0)//5) * 7, 112)` reproduces the PDF
table exactly at every boundary (0–10→7, 11–15→14, 16–20→28, 21–25→56, 26+→112).

**Corrected (RC-02).** The natural-20 bonus was `Money(base_gold * 150)` —
**+50%** — where §6.6 p.28 specifies +20%. Now `Money(base_gold * 120)`, with
table-driven boundary tests. The maintainer decided that no historical
reconciliation or announcement is required ([OD-10](open-decisions.md)).

Also unimplemented: the natural-1 consequence table (§6.6 p.28–29), and the
`tool` option is cosmetic — it is echoed in the reply but never validated
against the character's proficiencies.

### `/sale` — `ext/commands/sale.py`

| Aspect | Value |
|---|---|
| Channel restriction | `TRADE_CHANNEL_ID` |
| Authorization | Discord role **name** `shop owner` gates `point_of_sale` |
| Options | `character`, `item`, `cost`, `point_of_sale?`, `quantity?`, `persuasion?`, `material?` |
| Domain entry point | `Resource.sale()` (`models/resource.py:147`) |
| Rule source | Homebrew §4.1 p.11 (140% base), §4.1.1 p.11 (haggling, 180% cap, nat 20 +10%), §4.2.1 p.11–12 (own shop +20%, 190% cap) |

Mutations: money (P–S) increased.

Percentage logic verified against the PDF worked example (140 + 20 persuasion +
10 nat-20 + 20 shop-owner = 190%). **Correct at the cap.**

**Findings:**

- **RC-03 — corrected.** There was no 140% floor, so a negative persuasion
  total yielded below-140% percentages; §4.2.1 p.12 states the base *"starts at
  the minimum of 140%"*. The haggling contribution is now clamped to `>= 0`, and
  the calculation was split into named steps so the cap/natural-20 ordering is
  verifiable. Both PDF worked examples are covered by tests.
- **Money representation:** `crafting_cost` is a float and
  `earnings = crafting_cost * earnings_percent` is binary-float arithmetic —
  a direct violation of the money rule in `.agents/AGENTS.md`.
- **Authorization:** role matched by lowercase name, not snowflake
  (`.agents/AGENTS.md` requires stable role IDs).
- The 200%-for-vendor-items-sold-directly-after-mission rule (§4.1 p.11) is not
  implemented.

### `/trade` — `ext/commands/trade.py`

| Aspect | Value |
|---|---|
| Channel restriction | `TRADE_CHANNEL_ID` |
| Authorization | none |
| Options | `buyer?`, `seller?`, `good?`, `platinum?`, `gold?`, `silver?`, `copper?`, `moradinium?` |
| Domain entry point | `Trade.perform_trade()` (`models/trade.py:22`) |
| Rule source | Homebrew §4.2 p.11 (player-to-player deals) |

Either side may be the literal string `Shop`/`Store`, in which case that side is
not loaded or written. Buyer is debited, seller credited. Both actors' updates
are concatenated into **one** `batch_update` call, so the two-sided write is
atomic *at the Google API level*.

**Findings:**

- Negative `moradinium` is the documented mechanism for buying Moradinium
  (see the option description). `Resource.deduct()` deliberately excludes
  Moradinium from its negativity guard (`models/resource.py:67`), so this works,
  but it is an undocumented-in-rules encoding that Phase 5 should replace with an
  explicit direction.
- No read-modify-write concurrency control: two concurrent trades on the same
  actor from *different processes* will silently lose one. `actor_locks` is
  in-process only (`application/actor_locks.py:11`).
- Same-actor trades are rejected (`Trade._is_same_actor`), preferring
  `row_index` and falling back to case-folded name.

### `/bastion` — `ext/commands/bastion.py`

| Aspect | Value |
|---|---|
| Channel restriction | `BASTION_CHANNEL_ID` |
| Authorization | none |
| Options | `character`, `special_facilities?` |
| Domain entry point | `Bastion.maintain_bastion()` (`models/bastion.py:73`) |
| Rule source | Homebrew §7.1 p.29–30 (facility limits), §5.3–5.5 p.13 (5 GP/week per special facility), §7.2 p.30 (turns) |

Mutations: gold (Q) decreased by `weeks_of_maintenance * special_facilities * 5`;
`bastion_maintenance` (L) → 0; `bastion_turn_flag` (M) → 0.

**Findings:**

- **RC-04 — corrected.** `MAX_SPECIAL_FACILITIES[((5,8), 'aristocratic')]` was
  `2`; the PDF table on p.29 gives **3**. Every other cell already matched.
- **Corrected.** `get_max_special_facilities()` fell back to `1` for an
  unrecognised lifestyle; the rules give `0` for wretched/modest at every level,
  so the default is now `0`. `tests/test_bastion.py` covers the full table.
- Not implemented: Bastion loss after twelve missed LC (§7.2 p.30) and immediate
  Bastion loss on dropping below a qualifying lifestyle (§7.1 p.29).
- The `special_facilities` option lets a caller *undercount* their facilities and
  pay less; it is only replaced by the computed maximum when `<= 0`.

### `/learn` — `ext/commands/learn.py`

| Aspect | Value |
|---|---|
| Channel restriction | `DT_CHANNEL_ID` |
| Authorization | none |
| Options | `character`, `modifier`, `downtime?`, `gp_cost?`, `tool?`, `language?`, `new_target?`, `new_type?`, `roll_mode?` |
| Domain entry point | `Skills.learn_proficiency()` (`models/skills.py:243`) |
| Rule source | Homebrew §6.3 p.15 (5 DT/roll, 100% threshold, nat 20 +1%); §6.3.1–6.3.3 p.15–18 (per-category costs); §6.3.3.1 p.16–17 (artisan ranks, one-Master limit) |

Mutations: gold (Q) decreased per roll; `downtime` (I) decreased;
`downtime_progress` (V); on completion also `skills` (X), `proficiencies` (Y),
`languages` (Z), and `crp` (W) when a Master rank completes.

Every GP cost in the table was verified against the PDF — see
[rule-catalogue.md](../rules/rule-catalogue.md) RC-08. **All correct.**

**Findings:**

- **RC-09 — partly corrected.** The 100-CRP prerequisite (§6.3.3.1 p.17) is now
  enforced when a Master project starts, via `Skills.get_tool_crp()`. Projects
  already under way are not retroactively blocked. The tribute item (craft a free
  uncommon item for the master) is **still not enforced** — nothing records that
  it happened, so it needs new state and belongs to the Phase 5 migration
  ([OD-28](open-decisions.md)).
- **Data loss:** completing a Master sets `self.crp = "Master"` and clears
  `crp_dict` (`models/skills.py:423`), destroying per-tool CRP values that the
  rules require to be tracked separately per tool.
- **Non-atomic:** gold is deducted per roll inside the loop before any write. An
  exception mid-loop leaves the in-memory actor mutated and unsaved; a failure in
  `save_to_sheet` discards all rolls but the player has consumed nothing —
  inconsistent in the opposite direction if the write partially succeeds.
- **Key mismatch (latent bug):** projects are stored under
  `target_name.lower()` but popped on completion under the *cleaned* name
  (`models/skills.py:420`). A sheet value such as `45% (expert) Smith's Tools`
  parses to key `smith's tools` but is popped as `smith`, orphaning the entry.
  Phase 4 should pin this with a characterization test before changing it.
- **Cosmetic bug:** `learn.py:97` compares a `dict` against a string tuple, which
  is always true, so the raw dict repr is printed to Discord.
- Disadvantage rules (thieves' tools unless Bard §6.3.3.5; scrolls unless Wizard
  §6.3.3.7; martial weapon mastery §6.3.2) are left to the caller's `roll_mode`.

### `/craft` — `ext/commands/craft.py`

| Aspect | Value |
|---|---|
| Channel restriction | `DT_CHANNEL_ID` |
| Authorization | none |
| Options | 16, incl. `item_name`, `rarity`, `type`, `tool`, `quantity`, `base_price`, `spell_level`, `has_concentration`, `extra_cost`, `is_masterpiece`, `gather_ingredients`, `legendary_dt_spend` |
| Domain entry point | `calculate_craft()` (`helpers/craft_calculator.py:50`) |
| Rule source | Homebrew §6.5.2 p.19–21 (tool/rarity gating), §6.5.2.3 p.22, §6.5.2.4 p.23, §6.5.2.5 p.23–24, §6.5.2.6 p.24–25, §6.5.4.1 p.26, §6.5.4.2 p.27, §6.5.4.3 p.28, §6.3.3.1 p.17 (CRP) |

Mutations: gold (Q), Moradinium (T), `downtime` (I), `notable_items` (AA) or
`masterpiece` (AB), `crp` (W), and `downtime_progress` (V) for legendary
projects.

All five rule tables (`POISON_TABLE`, `SCROLL_TATTOO_TABLE`, `BREW_TABLE`, the
non-consumable matrix and the consumable matrix) were compared cell by cell
against the PDF. **All match.** This is the most faithful rules implementation in
the codebase.

**Findings:**

- **RC-06 — corrected.** Masterpiece rarity was unconstrained; §6.3.3.1 p.17
  specifies *"a rare item of your choice"*. `is_masterpiece` now requires
  `rarity == "rare"`, which also resolves the previously undefined interaction
  with the legendary roll-progression branch.
- **RC-07 — confirmed correct.** CRP is suppressed whenever the character has a
  Master rank in *any* tool. This follows from §6.3.3.1 p.17: CRP exists only to
  make a master contact you at 100 points, and a character may hold one Master
  rank for life, so once it is held further CRP can never be spent. Confirmed by
  the maintainer on 2026-07-29; the rationale is recorded in the code and covered
  by tests ([OD-29](open-decisions.md) closed).
- **CRP identity — corrected 2026-07-30** (Codex Phase 0 re-review, *Important*).
  The command wrote `actor.skills.crp_dict[tool_clean]` directly, which disagreed
  with the normalised lookup in `Skills.get_tool_crp()`: a cell holding
  `2.5 (Smith's Tools)` gained a second `(Smith)` entry instead of accumulating, and
  the Master gate then saw half the total. CRP mutation now lives in
  `Skills.add_tool_crp()`, which resolves the tool by the same rules, folds
  duplicate spellings into one entry and validates the numbers — see
  [sheet-inventory.md F-S3b](sheet-inventory.md#32-column-w--crafting-reputation-points-crp).
- **New refusal path, same correction round.** If a reputation award is due but
  column W could not be parsed in full (or holds the terminal `Master` literal), the
  command now refuses **before** deducting anything, rather than saving a craft whose
  award would overwrite a cell the adapter did not understand
  ([F-S3a](sheet-inventory.md#32-column-w--crafting-reputation-points-crp)). The
  affected row needs Guild Council reconciliation.
- **Meal DT ambiguity ([OD-05](open-decisions.md)):** §6.5.4.1 p.26 says a fancy
  meal costs *"just 5% of a regular consumable to craft"*. The code applies 5% to
  GP only, not to downtime. Genuinely ambiguous.
- **Non-atomic legendary projects:** materials are deducted when the project is
  created; progress rolls mutate `downtime_progress` incrementally. Any save
  failure mid-project is unrecoverable without manual sheet repair.
- The tool→item-type table (p.19–21) is enforced only for scroll/tattoo/brew/
  meal/herbalism. Everything else is unvalidated by design.
- Assistants (§6.5.3 p.25–26) are not implemented at all.

### `/xchange` — `ext/commands/xchange.py`

| Aspect | Value |
|---|---|
| Channel restriction | `TRADE_CHANNEL_ID` |
| Authorization | none |
| Options | `character`, `from_denomination`, `amount`, `to_denomination` |
| Domain entry point | `calculate_exchange()` (`models/exchange.py:18`) |
| Rule source | **none found in the Homebrew PDF** — standard 5e coin ratios (1pp=10gp=100sp=1000cp), precedence level 4 ("existing behavior") |

Mutations: money (P–S) redistributed at par, no fee.

This is the cleanest module in the codebase: pure function, no I/O, no
mutation, integer-only, fully unit-tested. It is the natural template for the
Phase 4 domain layer. Package 5.2 owns its migration. `/info` is not a platform
feature: linked-character pages replace its underlying read need, while package
5.1 owns any transitional command migration before terminal bot retirement.

## 3. The fixed write set

`Actor.sheet_updates()` unconditionally emits these cells on **every** save:

| Column | Field | Written by |
|---|---|---|
| A | name | always |
| D | inspiration | always |
| E | badge | always |
| F | level | always |
| G | missions | always |
| H | last_played | always |
| I | downtime | always |
| J | living_weeks | always |
| K | bastion_flag | always |
| L | bastion_maintenance | always |
| M | bastion_turn_flag | always |
| N | lifestyle | always |
| P–S | platinum/gold/silver/copper | always |
| T | moradinium | always |
| V | downtime_progress | always |
| W | crp | only when `crp_modified` |
| X | skills | always |
| Y | proficiencies | always |
| Z | languages | always |
| AA | notable_items | always |
| AB | masterpiece | always |
| AK | no_shows | always |
| AL | active_flag | always |

**Consequence.** A `/mine` that only changes Moradinium and downtime also
rewrites the character's badge, level, mission count, last-played date and
no-show counter with whatever those cells held *at load time*. If a Guild Council
member edits any of those cells between a player's `load` and `save` — a window
of seconds to minutes, since the load happens before the dice roll and the save
after — the Council's edit is silently overwritten.

This is a live data-loss vector, and it is the strongest single argument for the
Phase 1 database foundation. It is also why Phase 5 must migrate reads and writes
per command rather than leaving the Sheets adapter writing whole rows.

Two further round-trip losses come from the same mechanism:

- **Notable items lose detail.** `/craft` constructs an `Item` with
  `description`, `benefits`, `link` and `rarity`, but
  `Item.serialize_notable_items()` writes only `Rarity: name, name` lines
  (`models/item.py:68`). Description, benefits and link never reach the sheet and
  are gone on the next load.
- **Free-text fields are normalised on every save.** `skills`, `proficiencies`,
  `languages` and `downtime_progress` are parsed into dictionaries and
  re-serialised, so any human formatting, ordering or unrecognised annotation in
  those cells is rewritten to the parser's canonical form.

## 4. Cross-cutting gaps

These apply to all mutating commands and become explicit requirements for
Phases 3–5.

| # | Gap | Evidence | Plan phase |
|---|---|---|---|
| G-1 | **No character-ownership authorization.** Any guild member may run any mutating command against any character by typing its name. | no cog inspects `ctx.author` except `/sale`'s role-name check | 3, 5 |
| G-2 | **Channel restriction is treated as authorization.** | `ctx.channel.id != X` is the only gate | 3, 5 |
| G-3 | **No idempotency.** A Discord retry or double-click applies the mutation twice. `ctx.interaction.id` is used only in log lines. | `craft.py:211`, `xchange.py:71` | 4, 5 |
| G-4 | **No optimistic concurrency.** The sheet has no version column; `actor_locks` is per-process. | `application/actor_locks.py:11` | 1, 4 |
| G-5 | **No audit trail.** No record of who invoked what, for which character, with what result. | — | 1, 6 |
| G-6 | **Money is not consistently integer.** `Money` (integer copper) exists and is used by `to_currency`/`earn_money`, but `Resource` keeps four ints, `downtime` is a float, and `/sale` multiplies floats. | `models/resource.py`, `helpers/utils.py:29` | 4 |
| G-7 | **Identity is a mutable display name.** Characters are addressed by column-A string, matched case-insensitively; the first match wins on duplicates. | `models/actor.py:77` | 1, 2 |
| G-8 | **Silent row cap.** `A3:AL150` supports 148 characters; the 149th is invisible to the bot with no error. | `models/actor.py:75` | 2 |
| G-9 | **Read amplification.** Every command fetches the entire character table to find one row. | `models/actor.py:75` | 1 |

## 5. Proposed application services

The migration order in plan §12 Phase 5 maps onto these use cases. Names are
proposals for the Phase 4 ADR, not settled API.

| Use case | Kind | Replaces | Phase |
|---|---|---|---|
| `GetCharacterSummary` | query | `/info` | 5.1 |
| `ExchangeCurrency` | command | `/xchange` | 5.2 |
| `PayLifestyle` | command | `/lc` | 5.3 |
| `MineMoradinium` | command | `/mine` | 5.4 |
| `EarnMoneyWithTool` | command | `/work` | 5.4 |
| `AdvanceLearningProject` | command | `/learn` | 5.5 |
| `CraftItem` / `AdvanceLegendaryCraft` | command | `/craft` | 5.6 |
| `SellItem` | command | `/sale` | 5.7 |
| `TransferResources` | command | `/trade` | 5.8 |
| `RunBastionMaintenance` | command | `/bastion` | 5.9 |

Every one of these needs, at minimum: a caller identity, an authorized character
reference, an idempotency key derived from the Discord interaction ID, a
transactional repository boundary, and an audit event.
