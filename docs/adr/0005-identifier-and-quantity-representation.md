# ADR 0005 — Identifier, money and quantity representation

Status: **Accepted** — approved by the maintainer 2026-07-30. That satisfies the
Phase 0 acceptance criterion *"maintainer approves architecture ADRs"* (plan §12).
The independent Codex review required by plan §16.4 approved Phase 0 on
2026-07-30, and the maintainer accepted the milestone. This ADR is the contract
Phase 1 will be reviewed against.

Date: 2026-07-29

## Context

`.agents/AGENTS.md` requires integer copper for money, an explicit smallest unit
for other divisible resources, and stable IDs distinct from display names. Plan
§7.6 repeats this. Phase 0 discovery found the current code partially compliant
and partially not:

- `Money` exists and is correct — a frozen dataclass over integer copper with
  exact `Decimal`-based construction (`models/money.py`). It is used by
  `to_currency()` and `earn_money()`.
- `Resource` still holds four separate integers and does its own carry arithmetic
  in `deduct()` (`models/resource.py:66`).
- `/sale` multiplies binary floats: `earnings = crafting_cost * earnings_percent`
  (`models/resource.py:153`).
- `downtime` is a float via `safe_number` (`models/resource.py:18`), and crafting
  charges fractional days.
- Character identity is the display name in Sheet column A, matched
  case-insensitively, first match wins (`models/actor.py:77`).
- CRP is polymorphic — `int`, `float`, a raw string, or the literal `"Master"`
  (`models/skills.py:17`, `:423`).

The quantity question is not merely stylistic. The crafting tables use quarter-
and eighth-day steps, computed costs produce tenths, and the CRP table uses halves.

## Decision

### Money — integer copper

One canonical unit: **copper pieces, as a Python `int` and a PostgreSQL
`BIGINT`.** Ratios are 1 pp = 10 gp = 100 sp = 1 000 cp, matching
`models/exchange.py:3`.

- The existing `Money` value object is promoted to the domain unchanged in
  behaviour. It is the only money type crossing an application boundary.
- Denominated pp/gp/sp/cp are **presentation**, produced by
  `Money.denominations()`. They are not stored and not passed between layers.
- A binary `float` never touches a monetary value. Where a rule is expressed as a
  percentage — `/sale`'s 140–190% (rules §4.1.1 p.11) — the calculation is
  integer: `copper * percent_points // 100`, with the rounding rule stated at the
  call site.
- Persisted as a single `balance_copper BIGINT` per wallet, plus an append-only
  `resource_transactions` ledger. The four Sheet columns collapse into one number.

### Divisible resources — explicit integer smallest units

| Resource | Smallest unit | Reason |
|---|---|---|
| **Downtime** | **thousandth-day** (`downtime_millis`) | Revised 2026-07-30 — see below. Represents every value in every crafting table *and* every value the maintainer's rounding rule can produce, exactly |
| **Crafting reputation** | **tenth-point** (`crp_tenths`) | The CRP table uses 2.5 / 7.5 / 0.5 / 1.5 (rules §6.3.3.1 p.17) |
| **Learning progress** | **whole percent** | Rolls are integers; the natural-20 bonus is +1% (rules §6.3 p.15) |
| **Moradinium** | **whole unit** | Always integral in every rule |
| **Living weeks** | **whole week** | Rules §5 p.12 |

The 60-day downtime cap (rules §6 p.14) becomes `60000` thousandths. The migration
must convert existing float values and **report any value that does not land
exactly on a thousandth** rather than rounding it silently — `.agents/AGENTS.md`:
*"do not silently coerce invalid persistent data. Imports should report the
offending row and field."*

#### Why thousandth-days and not eighth-days — revised 2026-07-30

The original decision was **eighth-days**, justified by
`BREW_TABLE[(0, False)]["m"] = 0.125` being the finest step in any table. That was
wrong, because it only looked at the *table constants* and not at the *computed*
costs.

**The maintainer's ruling ([OD-08](../discovery/open-decisions.md)):** *"Crafting
days are rounded to one digit after the dot."*

The maintainer initially answered that computed crafting costs should round to one
decimal. The more specific follow-up ruling below superseded that answer: computed
costs round to **three decimals**, while fixed table constants remain exact.
Standard-item crafting divides a base price by a level divisor
(`helpers/craft_calculator.py:141`, `:163`, `:243`), producing arbitrary fractions
such as `7/25 = 0.28` and `100/75 = 1.3333…`.

Eighth-days cannot represent all results of that calculation, so the original unit
was unusable for the commonest crafting path. The three candidate units considered
at the time of the initial ruling were:

| Unit | `0.1` (computed) | `0.25` (master common) | `0.125` (master cantrip brew) |
|---|---|---|---|
| eighth-day | ✗ | ✓ | ✓ |
| tenth-day | ✓ | ✗ | ✗ |
| **thousandth-day** | **✓** `100` | **✓** `250` | **✓** `125` |

Thousandths represent all three exactly and cost nothing extra: a `BIGINT`
of milli-days is no harder to store than eighths, and the presentation layer
converts to days regardless.

**The rounding rule lives at the call site, not in the unit.** Per §"Rounding" below: a
computed crafting cost is rounded to the nearest **whole milli-day** (three decimals)
with the maintainer's ruling cited, and has a boundary test. Fixed table constants are
charged exactly, since they come from the PDF.

**Confirmed 2026-07-30, and it settles the unit.** Asked whether the fixed master-tier
constants `0.25` and `0.125` are charged exactly or rounded, the maintainer answered:

> *"Make the number exact. Maybe round after three digits, that should be enough."*

So:

- **Table constants are charged exactly.** `0.25` stays `0.25` (`250` millis) and
  `0.125` stays `0.125` (`125` millis). The PDF is preserved verbatim, and no
  master-tier cost changes.
- **Computed costs round to three decimals** — the nearest thousandth, which is one
  unit. `100/75 = 1.3333…` charges `1.333` (`1333` millis).

This supersedes the earlier *"one digit after the dot"* answer, which was given before
the distinction between computed and constant values had been put to the maintainer.
The newer answer is the specific one, and it is also the better outcome: **the rounding
rule and the storage unit now coincide.** Rounding to three decimals *is* rounding to
the nearest whole `downtime_millis`, so there is no second rounding step between the
domain and the database, and no representable value the rule can produce that the unit
cannot hold. [OD-08](../discovery/open-decisions.md) is closed.

### Identifiers

> **Resolved 2026-07-30 ([OD-35](../discovery/open-decisions.md)).** `characters.id` is
> assigned when the row is created and is **never derived** from a sheet row, a name,
> or a Foundry actor ID. Import idempotency comes from uniquely-constrained mapping
> rows — see [ADR 0003](0003-postgresql-and-alembic.md), *Identifier assignment and
> import idempotency*.

| Concept | Identifier |
|---|---|
| Character | application-generated UUID (`characters.id`) |
| Discord user / guild / role / channel | snowflake as `BIGINT` |
| Foundry actor | `external_actor_mappings.external_actor_id` — a **16-character alphanumeric string**, not a UUID. A mapping key, never an identity |
| Sheet row | `sheet_row_mappings` — a mapping key, never an identity |
| Tool, language, rarity, lifestyle, badge | short stable **code** (`smiths_tools`, `elvish`, `very_rare`) |

**Display names are never identifiers.** A character's name is a mutable
attribute. The Sheet's name lookup is retained only inside the Sheets adapter
during migration, and is deleted with it.

**Codes, not free text, for controlled vocabularies.** The Sheet's free-text tool
and language columns are normalised on import, and any value that does not map to
a known code is reported for Council resolution, not guessed. This directly
replaces `_clean_tool_name()`'s first-word heuristic
(`models/skills.py:198`), which collapses `Painter's Supplies` and any other
`Painter's *` to the same key.

### Equality

Domain value objects (`Money`, codes, dates) compare by value. Entities
(`Character`, `Mission`) compare by identity — the UUID — never by name.
`.agents/AGENTS.md`: *"Database IDs and mutable display names should not
accidentally define domain equality."*

### Rounding

Every rule calculation that can produce a fraction states its rounding at the
point of calculation, cites the rule, and has a boundary test. There is no
global default.

The known cases from Phase 0:

| Calculation | Rule | Current behaviour |
|---|---|---|
| Sale price percentage | §4.1.1 p.11 | float multiply, then `Money.from_gold` with `ROUND_HALF_UP` |
| Lifestyle extra expenses | §5 p.12 | silver decimal ÷ 10 → `to_currency` |
| Crafting standard-item cost | §6.5.2.3 p.22 | `base_price / 2.0` |
| Crafting standard-item DT | §6.5.2.3 p.22 | `base_price / dt_div` — produces arbitrary fractions |

**The last row is ruled, 2026-07-30 ([OD-08](../discovery/open-decisions.md)).** A
computed crafting cost is rounded to **three decimals** — the nearest whole
`downtime_millis` — at the call site, citing the ruling, with a boundary test.
`100/75 = 1.3333…` charges `1.333`; `7/25 = 0.28` charges `0.28` exactly, needing no
rounding at all. Fixed table constants are never rounded.

Note that the code performs **no rounding at all today** — `dt_cost` is a raw float
all the way through `helpers/craft_calculator.py`. Applying this ruling is a small
behaviour change, and it belongs to the Phase 5 `/craft` migration rather than to
Phase 0 or 1.

## Consequences

**Positive.**

- One money type, exactly representable, with no float in any monetary path.
- Integer downtime removes accumulated float drift from repeated `-=` operations
  on `Resource.downtime`.
- Stable IDs make import idempotency (plan §12 Phase 2) and Foundry mapping
  (plan §7.2) tractable.
- Controlled vocabularies turn today's silent parse failures into explicit
  import warnings.

**Negative.**

- Thousandth-days are unintuitive to read in the database. Mitigated by never
  showing them: the presentation layer converts to days.
- Existing float downtime values may not convert exactly. This is a **feature** —
  the import reports them rather than hiding a pre-existing data problem.
- The code vocabularies need seeding, and every homebrew addition (Common Sign
  Language, Druidic, homebrew weapons in rules §8.3 p.34–36) needs an entry.

## Alternatives considered

**`Decimal` for money.** Rejected: exact, but it invites arbitrary precision into
the domain and does not answer "what is the smallest unit?". Integer copper does.

**Separate pp/gp/sp/cp columns, as today.** Rejected: `Resource.deduct()`'s
recursive carry logic (`models/resource.py:76`) exists solely to work around this
representation, and it is a class of bug that disappears entirely with one
integer.

**Eighth-days for downtime.** The original decision in this ADR, **withdrawn
2026-07-30.** It was derived only from the table constants and missed the computed
division cases, which produce tenths. It cannot represent `0.1` at all — the
commonest crafting path.

**Tenth-days for downtime.** Rejected. It cannot represent the fixed master-tier
constants `0.25` and `0.125`, and the maintainer confirmed on 2026-07-30 that those are
charged **exactly** — so adopting tenths would have silently changed three costs the PDF
specifies.

**Quarter-days for downtime.** Rejected: represents neither the ⅛-day master cantrip
brew nor a computed tenth.

**Storing downtime as `NUMERIC`.** Rejected: exact, but it leaves "what is a
valid value?" undefined, and every comparison becomes a decimal comparison.
`.agents/AGENTS.md` asks for an *explicit smallest unit*.
