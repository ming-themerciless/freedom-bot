# Google Sheet Schema and Formula Inventory

Status: **VERIFIED against the maintainer's description, 2026-07-30.** E-1 is
satisfied. The real headers for all 38 columns, the contents of the eleven
previously-unknown columns, the formula question and the true CRP format were all
supplied by the maintainer, who authored the sheet and the rules.

Every column the code maps lines up exactly with the real header at that letter,
which independently validates `Actor.COLUMNS`. Four findings came out of the
verification and are marked **F-S1**–**F-S4** below; one of them was a live
data-loss defect, now fixed.

A second round of answers on the same day resolved [OD-01](open-decisions.md)
(scope is `Characters` plus a player tab — §2), [OD-06](open-decisions.md) (the sheet
uses two vocabularies, tool and artisan — §3.1) and [OD-08](open-decisions.md)
(crafting days round to one decimal). A later round supplied the **player tab's eight
column headers** (§2.1) and closed OD-08 completely. **No Sheet structural question is
outstanding.** What remains is survey depth rather than structure: the free-text columns
V, X, Y, Z and AA have not been examined the way column W was — §6, item 6.

**Sources.** Structural facts about the *code* — field keys, parse and serialise
behaviour, the read range — come from `models/actor.py`, `models/resource.py`,
`models/lifestyle.py`, `models/bastion.py`, `models/skills.py`, `models/item.py` and
`connectors/sheets.py`. Structural facts about the *sheet* — headers, column
contents, formulas, macros, the CRP format, row count, tab scope — come from the
maintainer and are attributed inline. No live spreadsheet was read, no
service-account credential was used, and no player row appears here.

[§6](#6-verification-status-of-the-original-six-unknowns) tracks which of the
original unknowns each answer closed.

## 1. Access contract

`connectors/sheets.py` exposes exactly two operations against one spreadsheet
(`GUILD_SHEET_ID`), authenticated by a service account with the
`https://www.googleapis.com/auth/spreadsheets` scope — **read/write on the whole
document**, not a narrower scope.

| Operation | Signature | Used by |
|---|---|---|
| Read | `get_values(a1_range, value_render_option="UNFORMATTED_VALUE")` | `Actor.load_from_sheet` |
| Write | `batch_update(updates, value_input_option="USER_ENTERED")` | `Actor.save_to_sheet`, `Trade.perform_trade` |

The service object is a module-level singleton built lazily
(`connectors/sheets.py:10`), constructed from `SERVICE_ACCOUNT_INFO` parsed at
import time in `config.py`. Both calls are synchronous and blocking; cogs push
them onto a thread via `run_in_executor`.

Two properties of this contract matter for the migration:

- `UNFORMATTED_VALUE` on read means the bot receives **computed formula results**
  as raw values, never the formulas themselves. Any spreadsheet formula is
  therefore invisible to the code — see [§4](#4-formulas-and-macros). In the event
  there are none, so this hazard is moot; the `USER_ENTERED` one below is not.
- `USER_ENTERED` on write means values the bot sends are **re-interpreted by
  Sheets** as if typed by a human. A string beginning with `=` would become a
  formula; a date-like string may be coerced to a date serial. This is a latent
  injection/coercion hazard for the free-text columns (`AA` notable items, `X`/`Y`
  skills and proficiencies), which are round-tripped verbatim from player input.

## 2. Tabs

Only one tab is referenced anywhere in the codebase:

| Tab | Range read | Notes |
|---|---|---|
| `Characters` | `A3:AL150` | Rows 1–2 are headers; data starts at row 3. **33 characters** as of 2026-07-30, so the `150` ceiling is not close |
| *player tab* | **not read by the bot** | **In scope for migration.** 8 columns — see [§2.1](#21-the-player-tab) |

**The sheet is already a two-level model, and the schema should keep it that way.**
The maintainer, 2026-07-30:

> *"Only players and characters are relevant because last session, is DM, last time
> DMed, and campaigns are player based not character based."*

| Level | Facts | Platform home |
|---|---|---|
| **Player** | last session, is DM, last time DMed, campaigns | `players` / platform users |
| **Character** | the 38 columns below | `characters` |
| **Join** | column **C**, Player Name | `character_access` |

So column C is a **foreign key**, not a loose hint (F-S1), and `is DM` is existing
per-player authorization *evidence* to reconcile against
[OD-18](open-decisions.md) — though effective privilege still resolves from Discord
role IDs server-side per [ADR 0004](../adr/0004-discord-oauth2-authentication.md).
`campaigns` being player-scoped shapes the Phase 6–8 mission model.

**Migration scope is these two tabs only.** Shop inventory (§4.1 p.10), Moradinium
accounting (§2.1.2 p.4) and mission logs (§2.1 p.3) exist as rules but are confirmed
out of scope.

### 2.1 The player tab

Columns supplied by the maintainer, 2026-07-30. The bot has never read this tab.

| Col | Header | Becomes | Notes |
|---|---|---|---|
| A | Player Name | `players.display_name` | Join key from `Characters` column C |
| B | **Discord Name** | `players.discord_username` | **The Discord link already exists — F-S5** |
| C | Last date played | derived | **Also on `Characters` (H)** — see F-S6 |
| D | **Active DM** | `players.is_dm` (evidence) | Feeds the DM capability question, [OD-18](open-decisions.md) |
| E | Last date DMed | `players.last_dmed_at` | |
| F | **Latest date to DM** | *unmodelled rule* — see F-S7 | A deadline, not an observation |
| G | Campaign Counter | `players.campaign_count` | Campaigns are player-scoped |
| H | No shows | derived? | **Also on `Characters` (AK)** — see F-S6 |

**F-S5 — the Discord link exists, one level up from where Phase 0 looked for it.**
Column C of `Characters` gives player *name*; column B here gives that player's
**Discord name**. So the chain `character → player → Discord` is already complete in
the spreadsheet:

```text
Characters.C (Player Name) ──> player tab.A ──> player tab.B (Discord Name)
```

This is a genuinely better starting point than Phase 0 assumed. Two caveats keep it
*evidence* rather than authorization:

- It is a **username, not a snowflake.** Discord usernames change, and a display name
  differs from the account handle. [ADR 0004](../adr/0004-discord-oauth2-authentication.md)
  requires effective privilege to resolve from role **IDs** server-side, so this seeds
  a Council-verified matching pass and nothing more.
- It is **one Discord name per player**, and one player per character — while the
  product invariant allows several authorized users per character. The import creates
  the obvious links; anything beyond that is a Council action.

**F-S6 — two fields are recorded at both levels.** *Last date played* is column H of
`Characters` **and** column C here; *No shows* is column AK **and** column H here. The
maintainer's framing — *"last session … [is] player based not character based"* —
suggests the player-level value is authoritative and the character-level column is the
per-character detail, i.e. the player figure is a `MAX`/`SUM` across that player's
characters.

That is an inference, not a statement, and it is the kind that goes wrong quietly. The
importer should **compute the aggregate, compare it with the stored player-level value,
and report any disagreement** rather than trusting either side. If they always agree,
the player-level columns are derived and need no storage of their own.

**F-S7 — *"Latest date to DM"* looks like an unimplemented rule.** Columns E and F are
different in kind: *Last date DMed* records what happened, *Latest date to DM* is a
**deadline** — the date by which a player must next run a session. Nothing in
[rule-catalogue.md](../rules/rule-catalogue.md) covers a DM rotation obligation, and
nothing in the bot touches it. Either it is a convention the Council tracks by hand, or
it is a rule the catalogue is missing. Worth confirming before Phase 6 designs the
mission workflow around it.

## 3. Column map — `Characters`

**Real headers supplied by the maintainer, 2026-07-30.** The `Field key` and
`Access` columns come from `Actor.COLUMNS` (`models/actor.py:11`) and the
sub-model `load_from_sheet_data`/`get_sheet_data` pairs.

The maintainer described the range as "A–AG", but the list they gave contains
**38 labels**, which lands exactly on **AL** — and `No shows` / `Active` fall on
AK / AL, precisely where the code maps `no_shows` and `active_flag`. The read
range `A3:AL150` is therefore correct and every mapped column matches its real
header. That is a strong independent validation of `Actor.COLUMNS`.

Legend — **R** read by the bot, **W** written by the bot, **RW** both,
**unmapped** = the column exists in the sheet but the code ignores it.

| Col | Real header | Field key | Access | Notes / owner after migration |
|---|---|---|---|---|
| A | Character Name (short) | `name` | RW | The lookup key today. Becomes a display attribute; identity moves to a surrogate ID |
| B | Character Name (long) | — | **unmapped** | Full/formal name. Display data — PostgreSQL |
| C | **Player Name** | — | **unmapped** | **The player↔character link, and it already exists.** See **F-S1** |
| D | Inspiration Coin | `inspiration` | RW | Raw value, no coercion |
| E | Badge | `badge` | RW | Defaults to `"Bronze"`. Derived from level — see §5 |
| F | Character Level | `level` | RW | `safe_int`, default 1. Ownership is [OD-15](open-decisions.md) |
| G | Experience (Missions) | `missions` | RW | Cumulative mission count; drives level and badge |
| H | Last Time Played | `last_played` | RW | Date serial or string, round-tripped |
| I | Downtime (In days) | `downtime` | RW | `safe_number` → **float**. Becomes integer **thousandth-days** ([ADR 0005](../adr/0005-identifier-and-quantity-representation.md), revised 2026-07-30) |
| J | Lifestyle Costs (In Weeks) | `living_weeks` | RW | Weeks of living cost **owed**. `+1` weekly by an **active** macro — see **F-S2** |
| K | Bastion flag | `bastion_flag` | RW | `int` (0/1) |
| L | Bastion maintenance (in weeks) | `bastion_maintenance` | RW | `int` weeks |
| M | Bastion turn flag | `bastion_turn_flag` | RW | `int` (0/1) |
| N | Lifestyle | `lifestyle` | RW | Lowercased, default `"modest"` |
| O | Aristocratic lifestyle flag | `aristocratic_flag` | mapped, **never used** | The §5.5 p.13 one-year lock-out marker |
| P | Platinum | `platinum` | RW | Collapses into one `balance_copper` |
| Q | Gold | `gold` | RW | ″ |
| R | Silver | `silver` | RW | ″ |
| S | Copper | `copper` | RW | ″ |
| T | Moradinium | `moradinium` | RW | Integer resource row |
| U | **Weekly Expenses** | — | **unmapped** | Previously unknown. Relates to lifestyle cost per week (§5.2–5.5 p.12–13) |
| V | Downtime Progress | `downtime_progress` | RW | Structured parse — see §3.3 |
| W | CRP | `crp` | R, conditional W | Structured parse — see §3.2. **Format defect found and fixed: F-S3** |
| X | Crafting Skills | `skills` | RW | Crafting ranks — see §3.1 |
| Y | Tool Proficiencies | `proficiencies` | RW | Tool proficiencies — see §3.1 |
| Z | Languages | `languages` | RW | Comma-split; `"-"` when empty |
| AA | Notable Items | `notable_items` | RW | Rarity-grouped — see §3.4 |
| AB | Masterpiece | `masterpiece` | RW | `str`, stripped |
| AC | **Frank** | `debt` | mapped, **never used** | Frank the Money Lender (§5.6 p.14). Interest is applied by macro — see **F-S2** |
| AD | Background | — | **unmapped** | Character detail |
| AE | **Classes/Subclasses** | — | **unmapped** | **Also in Foundry** — see **F-S4** |
| AF | **Race/Species** | — | **unmapped** | **Also in Foundry** — see **F-S4** |
| AG | **Abilities (STR/DEX/CON/INT/WIS/CHA)** | — | **unmapped** | **Also in Foundry, and the platform needs it** — see **F-S4** |
| AH | Feats/ASIs | — | **unmapped** | Also in Foundry — see **F-S4** |
| AI | Special Notes | — | **unmapped** | Free text |
| AJ | Mounts | — | **unmapped** | Free text |
| AK | No shows | `no_shows` | RW | `safe_int`, default 0 |
| AL | Active | `active_flag` | RW | `int` (0/1) |

**Column E holds a badge tier, and one of those tiers is `Electrum`** (rules §3
p.8–9, Iron→Adamantine; maintainer-confirmed). It is **not** currency — the game
uses no electrum. An importer must key badge on a controlled tier code and must
never resolve a coin denomination by name match against this column. See
[foundry-mapping.md §4.4](foundry-mapping.md#currency--od-13).

### 3.0 Findings from the verification

**F-S1 — the player link already exists, in column C.** Phase 0 assumed the
Discord↔character association had to be built from nothing in Phase 3. Column C
holds a player name for every character, which makes it a **seed** for
`character_access` rather than a blank slate. Two caveats: it is a *name*, not a
Discord snowflake, so it needs one Council-verified mapping pass to become an
authorization fact; and it is one name per character, whereas the product
invariant allows several authorized users per character. Treat it as evidence for
an audited linking step, never as authorization in itself.

**F-S2 — there are no formulas, but there are three timed macros. The sheet has a
third writer.** See [§4](#4-formulas-and-macros). This is the answer to OD-07 and
it is good news for the migration and bad news for concurrency.

**F-S3 — column W's real format was not the one the code parsed. This was live
data loss, now fixed.** See [§3.2](#32-column-w--crafting-reputation-points-crp).
Two Codex re-reviews then found narrower versions of the same loss in the fix
itself — **F-S3a** (a partial parse rewrote the rest of the cell) and **F-S3c**
(a duplicate entry overwrote the earlier one) — plus **F-S3b**, an award creating
a second identity for one tool. All are fixed and all are in §3.2.

**F-S4 — the sheet holds character mechanics that were assumed to be
Foundry-only.** Columns AE, AF, AG and AH hold classes/subclasses, race/species,
ability scores and feats. [foundry-mapping.md §4.2](foundry-mapping.md#42-character-mechanics--verified-against-two-real-actors)
assumed these existed *only* in Foundry and assigned them Foundry ownership; in
fact they are **dual-recorded today**, which creates a contested group that the
field-ownership matrix did not have.

The most useful consequence concerns **AG, ability scores**. The rules require a
Learning Roll to use the base ability modifier with no proficiency, feats, items
or features (§6.2 p.15). Today `/work` and `/learn` accept a `modifier` **typed in
by the player** and trust it. With AG available, the platform can source the
modifier from data it holds, which removes a player-supplied number from a reward
calculation *without* requiring the Foundry connector to exist first. That is a
correctness win available in Phase 5 rather than Phase 7.

### 3.1 Columns X and Y — crafting ranks and tool proficiencies

Both are comma/semicolon/period-separated lists parsed by
`Skills._parse_item_level()` (`models/skills.py:211`), which accepts two forms:

- `Tool Name (journeyman|expert|master)`
- `Journeyman|Expert|Master Tool Name`

Anything else yields `(item, None)` — the entry survives with an unknown level.

Column **X** (`skills`) holds *crafting* ranks and defaults an unparseable level
to `"journeyman"`. Column **Y** (`proficiencies`) holds tool proficiencies and
keeps `None` for a level-less entry.

**Two vocabularies, one per column group — maintainer-confirmed 2026-07-30:**

> *"Y is the tool, W, X is the artisan (e.g. Weaver's Tools - Weaver)."*

| Column | Vocabulary | Example |
|---|---|---|
| **Y** Tool Proficiencies | the **tool** | `Weaver's Tools` |
| **W** CRP, **X** Crafting Skills | the **artisan** | `Weaver` |

This reframes `_clean_tool_name()`. It reduces a name to its **first word with the
possessive stripped** — `Smith's Tools` → `Smith`, `Herbalism Kit` → `Herbalism` —
which is not a lossy shortcut that happens to work: it is **the documented bridge
from the tool vocabulary to the artisan vocabulary.** Verified across all 22
`TOOL_CHOICES`, every result is the correct artisan for its tool. (`Scrolls`,
`Scroll` and `Scroll Proficiency` are separately normalised to `Scroll`.)

**Schema consequence ([OD-06](open-decisions.md), resolved).** Identity is the
**artisan code**; the tool name is a display label on the same row. One `tools`
vocabulary table holding both, keyed on artisan, with column Y normalising into it
on import.

**Residual risk.** W, X and Y are free text, so a typo or a non-canonical artisan
resolves to **0.0 silently** — and the RC-09 Master gate reads that value. The
importer must reject an unrecognised artisan and report the row, never default. The
theoretical `Painter's Supplies` / `Painter's Easel` collision remains a reason not
to relax matching into prefix comparison.

### 3.2 Column W — crafting reputation points (CRP)

#### F-S3 — the parser did not understand the real format, and a save destroyed data

**The canonical form, per the maintainer:** `7.5 (Brewer), 2.5 (Calligrapher)` —
**amount first, tool in parentheses**. A mastered tool is recorded as the literal
`Master`, because one Master rank is permitted for life and further CRP can never
be spent (§6.3.3.1 p.17, [OD-29](open-decisions.md)).

The parser only recognised `Brewer: 7.5` — **colon form, opposite order**. It
required a `:` to attempt per-tool parsing at all, so on the real format it fell
through to a bare-number parse, failed, and left `crp_dict` **empty**.

Verified before the fix:

```text
cell "7.5 (Brewer), 2.5 (Calligraph)"  ->  crp_dict = {}   get_tool_crp(...) = 0.0
```

Two consequences, one of them live:

1. **Data loss on every `/craft`.** `ext/commands/craft.py:204` adds the award to
   `crp_dict` and sets `crp_modified`, and the whole cell is then rewritten from
   that dict. Starting from an empty dict, the cell was replaced by the single
   tool just crafted:

   ```text
   before: "7.5 (Brewer), 2.5 (Calligraph)"   craft awards 2.5 Brewer
   after:  "Brewer: 2.5"
   ```

   Brewer's 7.5 was discarded rather than accumulated, Calligrapher was erased
   entirely, and the maintainer's format was rewritten into the colon form. This
   was **pre-existing**, not introduced by the RC-09 correction.

2. **The RC-09 Master gate refused everyone.** The 100-CRP prerequisite reads
   `get_tool_crp()`, which returned `0.0` for every tool, so a character with
   `150 (Brewer)` was told they had 0. That gate was in the working tree and had
   not been committed, so no player ever met it.

**Fixed 2026-07-30** in `models/skills.py`: the canonical `amount (Tool)` form is
now parsed by pattern rather than by splitting on commas — necessary because the
amount may itself use a comma as its decimal separator (`7,5 (Brewer)`) — the
legacy colon form is still accepted for rows the bot already rewrote, and
`get_sheet_data()` now writes the canonical form back so a save never changes the
convention. Seven regression tests in `tests/test_skills.py` cover both forms, the
comma decimal, the `Master` literal, accumulation, and the gate.

**Open, and now consequential — [OD-06](open-decisions.md) tool identity.** Lookup
reduces a tool to its first word with the possessive stripped, so
`Calligrapher's Supplies` → `Calligrapher`. A cell abbreviated to `(Calligraph)`
therefore matches nothing and yields `0.0` **silently**. Since the Master gate
reads this value, an abbreviation is enough to refuse a qualified character. The
canonical cleaned names the commands use are `Alchemist`, `Brewer`,
`Calligrapher`, `Carpenter`, `Cartographer`, `Cobbler`, `Cook`, `Glassblower`,
`Herbalism`, `Jeweler`, `Leatherworker`, `Mason`, `Painter`, `Poisoner`, `Potter`,
`Smith`, `Tinker`, `Weaver`, `Woodcarver`, `Disguise`, `Forgery`, `Thieves`.
Current behaviour is pinned by
`test_an_abbreviated_tool_name_silently_resolves_to_zero`; it must **not** be
"fixed" with prefix matching, which would make `Painter`/`Potter`-style collisions
silent instead of loud.

#### F-S3a — the first fix still accepted valid *fragments*, which was the same defect

Found by the **Codex Phase 0 re-review, 2026-07-30**, and classified **Blocking**.
The fix above matched the canonical pairs with `findall()`, which keeps whatever
fragments happen to match and silently ignores everything else:

```text
cell "7.5 (Brewer), BROKEN"  ->  crp_dict = {"brewer": 7.5}
```

That is a partial parse, and a partial parse is what the whole cell is later
rewritten from — so the next `/craft` wrote a cell that no longer contained
`BROKEN`. Narrower than F-S3, identical in kind, and it also applied to the legacy
form (`Brewer: 7.5, BROKEN`).

**Fixed 2026-07-30**, in `Skills._parse_crp_cell()`:

- a cell is read as a per-tool list only when **every** fragment parses *and*
  everything outside the matched fragments is a separator (whitespace, `,`, `;`);
- both notations are matched by one pattern, so a mixed cell
  (`7.5 (Brewer), Smith: 2.5`) is now read in full instead of half;
- anything else keeps its raw value, sets `crp_unparsed`, and **pins column W
  read-only**: `Skills.get_sheet_data()` omits the column entirely, so the adapter
  writes no range for it and the stored text survives untouched;
- `Skills.add_tool_crp()` refuses such a row, and `/craft` refuses the craft before
  spending anything rather than saving a craft whose award cannot be recorded;
- `Skills.get_summary()` shows the raw text and says it is unreadable, so the row
  surfaces for reconciliation instead of appearing as a silent `0`.

The one write that still replaces an unparsed cell is a completed Master rank,
which deliberately replaces column W with the literal `Master` whatever it held
before (that this discards per-tool totals is the Phase 5 item already recorded in
[phase-0-handoff.md](phase-0-handoff.md)).

#### F-S3b — an award could create a second identity for the same tool

Also found by the Codex Phase 0 re-review and classified **Important**. `/craft`
updated `actor.skills.crp_dict` itself, keyed by `_clean_tool_name(tool).lower()`,
while `get_tool_crp()` compares keys *after* cleaning both sides. A cell written by
hand as `2.5 (Smith's Tools)` therefore gained a second entry rather than
accumulating:

```text
before: "2.5 (Smith's Tools)"   /craft awards 2.5 CRP with Smith's Tools
after:  "2.5 (Smith's tools), 2.5 (Smith)"
```

Both entries name the same artisan, and the Master gate reads whichever it meets
first — so 5 points read as 2.5.

**Fixed 2026-07-30:** CRP mutation is encapsulated in `Skills.add_tool_crp()`,
which resolves the tool with the same normalisation `get_tool_crp()` uses, adds to
the existing entry under its stored spelling, folds any duplicate spellings already
present into that one entry, marks the column modified, and validates the numbers.
`/craft` calls it instead of writing `crp_dict`. **No entry is added for a tool that
already has one under another spelling.**

#### F-S3c — a duplicate entry overwrote the earlier one, discarding its CRP

Found by the **second Codex Phase 0 re-review, 2026-07-30**, and classified
**Blocking**. F-S3a made parsing all-or-nothing at the level of the *cell*, but
inside it `_parse_crp_cell()` still lower-cased each tool name and assigned it
straight into the dictionary. A second fragment naming the same tool therefore
replaced the first rather than adding to it:

```text
stored:       "2.5 (Smith), 2.5 (SMITH)"
parsed:       {"smith": 2.5}          -- the first 2.5 is gone
/craft award: +2.5
saved:        "5 (Smith)"             -- correct total is 7.5
```

Same mechanism as F-S3 and F-S3a — the whole cell is rewritten from the parsed
dictionary — and the same class of loss, at the level of a single entry rather
than the whole cell. It applied equally to the legacy notation
(`Smith: 2.5, SMITH: 2.5`) and to a cell mixing the two
(`2.5 (Smith), Smith: 2.5`).

**Policy chosen: consolidate by summing.** Duplicate entries are summed at read
time under the **first spelling seen**, keeping that spelling's position in the
cell, so the serialisation stays deterministic. The alternative — treating the
whole cell as unreadable and pinning column W read-only, as F-S3a does for
unrecognised text — was rejected because the entries are not ambiguous: the names
differ only in case, so there is exactly one arithmetic reading, and no
maintainer judgement is needed to arrive at it. Marking such a row unreadable
would block a character's `/craft` for a cell whose meaning is not in doubt,
which is a worse outcome than the repair.

**The consolidation is deliberately narrow.** Only names that are equal after
case-folding are merged. Names that differ by more than case stay separate, so
read-time identity never depends on `_clean_tool_name()`'s tool-to-artisan bridge.
That bridge collapses a name to its first word and merges anything sharing one,
including a non-canonical spelling nobody has validated;
[OD-06](open-decisions.md)'s standing rule is that an unrecognised free-text
artisan must fail loudly at import rather than be guessed at, and a silent
read-time merge is exactly that guess. `Smith` beside `Smith's Tools` therefore
still reads as two entries and is folded by `add_tool_crp()` when that tool is
next awarded, exactly as F-S3b describes; that behaviour is unchanged.

**Consolidation never triggers a write on its own.** `crp_modified` is still set
only by `add_tool_crp()`, so a duplicate row is repaired in memory and the stored
cell is left alone until CRP is actually awarded.

**One further fail-closed case was added in the same change.** A digit run long
enough to overflow `float()` to infinity — on its own, or once a duplicate was
added to it — previously entered `crp_dict` as `inf` and could be written back.
Such a cell is now unreadable: raw value preserved, `crp_unparsed` set, column W
pinned read-only.

Fourteen regression tests in `tests/test_skills.py` cover identical duplicates,
case variants, duplicates in the legacy notation, duplicates across mixed
notations, comma decimals, first-spelling and position determinism, the complete
read → award → serialisation path, non-consolidation of distinct and of
merely-equivalent names, a duplicate beside malformed text, and the three
overflow cases.

#### Accepted encodings after the fixes

| Sheet value | Parsed to |
|---|---|
| `""`, `"-"`, `"0"` | `crp = 0`, `crp_dict = {}` |
| `"7.5 (Brewer), 2.5 (Calligrapher)"` | `crp_dict = {"brewer": 7.5, "calligrapher": 2.5}` — **canonical** |
| `"7,5 (Brewer)"` | `crp_dict = {"brewer": 7.5}` — comma decimal |
| `"Master"` | `crp = "Master"`, `crp_dict = {}` — mastered, no total kept |
| `"Brewer: 7.5"` | `crp_dict = {"brewer": 7.5}` — legacy, still read |
| `"Brewer: 7,5"` | `crp_dict = {"brewer": 7.5}` — legacy with a comma decimal (the pre-F-S3a code read this as `7`) |
| `"7.5 (Brewer), Smith: 2.5"` | `crp_dict = {"brewer": 7.5, "smith": 2.5}` — mixed notations, both read |
| `"12.5"` | `crp_dict = {"general": 12.5}` — untagged legacy, [OD-34](open-decisions.md) |
| `"2.5 (Smith), 2.5 (SMITH)"` | `crp_dict = {"smith": 5}` — duplicates differing only in case are **summed** under the first spelling, F-S3c (the pre-F-S3c code read this as `2.5`) |
| `"Smith: 2.5, SMITH: 2.5"`, `"2.5 (Smith), Smith: 2.5"` | `crp_dict = {"smith": 5}` — the same, in the legacy and mixed notations |
| `"2.5 (Smith's tools), 2.5 (Smith)"` | `crp_dict = {"smith's tools": 2.5, "smith": 2.5}` — **not** merged at read time; names differing by more than case keep separate entries, folded by `add_tool_crp()` when awarded (F-S3b, OD-06) |
| a value too long to represent, e.g. 400 digits | `crp = <raw value>`, `crp_dict = {}`, `crp_unparsed = True` — `float()` overflows to infinity, so the cell is unreadable rather than written back as `inf`, F-S3c |
| anything else, incl. a valid pair with unrecognised text beside it | `crp = <raw value>`, `crp_dict = {}`, `crp_unparsed = True` — **column W is not written at all until a maintainer reconciles it** |

`crp` remains **polymorphic** — `int`, `float`, raw string, or `"Master"` — which
is a data-model defect that Phase 5 resolves by storing per-tool rows and a
separate mastered flag. Column W is written back only when `crp_modified` is set,
the single piece of write-narrowing in the whole adapter.

CRP values are fractional by rule (2.5 / 7.5 / 0.5 / 1.5 per §6.3.3.1 p.17). The
database must store them as an exact decimal or as tenths in an integer, **not**
as a float.

### 3.3 Column V — downtime progress

Free text holding zero or more comma-separated learning/crafting projects. The
parser (`models/skills.py:76`) extracts a percentage and then attempts, in order:

1. a parenthesised level — `45% (expert) Smith`;
2. one of a known-level word list — `journeyman`, `expert`, `master`,
   `language`, `instrument`, `vehicle`, `scroll`, `scroll proficiency`,
   `weapon mastery`, `martial weapon`, `thieves tools`, `gaming set`;
3. otherwise defaults the level to `language`.

Duplicate target keys are **merged by summing percentages, capped at 100** — an
explicit repair for a historical bug (commit `2d6b276`). `/craft` legendary
projects reuse the same column with a synthesised name
`crafting <item> (<tool>)` and level `legendary` (`ext/commands/craft.py:141`).

This column is the strongest argument for normalisation: it currently encodes an
entire project table — target, category, percent complete — in one free-text
cell, shared between two unrelated workflows.

### 3.4 Column AA — notable items

Multi-line, rarity-grouped:

```text
Legendary: Item A
Rare: Item B, Item C
Common: Item D
```

Parsed by `Item.parse_notable_items()`; an ungrouped line falls back to a
`(rarity)` suffix match, and anything unrecognised is classified `common`.

**Round-trip loss:** `Item.serialize_notable_items()` writes only names grouped
by rarity. The `description`, `benefits` and `link` that `/craft` collects and
displays are never persisted. Phase 2 imports must treat column AA as
*name + rarity only*, and Phase 5 must add real item records.

## 4. Formulas and macros

**F-S2 — answered by the maintainer, 2026-07-30 ([OD-07](open-decisions.md) closed).**

> **There are no formulas in the sheet.** Phase 0's formula hypotheses for badge,
> level, living weeks, downtime and Frank's interest were all **wrong**. Nothing
> is computed by a cell formula.

**Phase 2 is therefore a migration, not a repair.** This was the single largest
open question, and the answer is the good one: the bot's 26-cell whole-row write
has never destroyed a formula, because there were none to destroy.

### 4.1 But there are three timed macros, and they are a third writer

The accrual the rules describe is implemented in **Apps Script macros**, not
formulas and not the bot:

| Macro | Writes | Rule basis | Previously known? |
|---|---|---|---|
| Weekly living-cost accrual | **`J`** — `+1` week, every week, to every character | §5 p.12 | **No. Never documented anywhere** |
| Living cost paid → downtime | **`I`** — `+5` days per week paid | §6 p.14 | Yes, and **the bot does this now** |
| Frank's interest | **`AC`** — interest on outstanding loans | §5.6 p.14 | No — assumed to be a formula, is a timed script |

Three consequences, in order of importance:

**1. The sheet has a writer nobody modelled.** Phase 0 documented two writers, the
bot and the Council. There is a third, it runs on a timer, and it mutates `J` and
`AC` without any coordination. Every concurrency statement in
[ADR 0003](../adr/0003-postgresql-and-alembic.md) and
[command-inventory.md §4](command-inventory.md#4-the-fixed-write-set) was written
against a two-writer model.

**2. The 26-cell blind write can silently revert a macro.** `Actor.sheet_updates()`
writes `J` on every save using its **load-time** value. If the weekly accrual fires
between a command's read and its write — the window contains a dice roll and a
Discord round-trip — the `+1` is overwritten and that week's living cost is lost
for that character. The same applies to `AC` and Frank's interest. This is the
existing whole-row-write hazard, but with a concrete automated trigger rather than
a hypothetical Council edit.

**3. Migration has to decide the macros' fate explicitly.** They are not in this
repository, are not version-controlled, and will keep writing to the sheet
throughout any verification period. Phase 2 must either disable them at cutover
and reimplement the accrual in the platform, or leave them running and treat `J`
and `AC` as macro-owned for the duration. Recorded as
[OD-36](open-decisions.md).

### 4.2 What this changes about derived values

`E` badge and `F` level are **not** computed anywhere — not by formula, not by
macro, not by the bot. They are maintained by hand. Combined with the rules making
both pure functions of mission count (§3 p.8–9, §3.1 p.9–10), that means the
platform can compute them correctly and present the sheet's value as a
reconciliation difference. §5 keeps classifying them as derived.

### 4.3 The read/write contract is unaffected

`UNFORMATTED_VALUE` still means the bot sees values rather than expressions, and
`USER_ENTERED` still means a bot-written string beginning with `=` would become a
formula. With no formulas in the sheet today, the injection hazard in §1 is the
live half of that pair, not the clobbering hazard.

## 5. Derived versus stored

The rules define several values as functions of others. The sheet stores them
flat, and the bot treats them as stored:

| Value | Rule | Function of | Current handling |
|---|---|---|---|
| Badge (E) | §3 p.8–9 | level | stored, round-tripped |
| Guild reward | §3 p.8–9 | badge | not in the sheet at all |
| Max extra reward | §2.1.3.1 p.5, §3 p.9 | mission badge | not in the sheet |
| Report reward | §3 p.9 | badge | not in the sheet |
| Level (F) | §3.1 p.9–10 | cumulative missions | stored, round-tripped |
| Max special facilities | §7.1 p.29–30 | level × lifestyle | computed in code (`models/bastion.py:14`) |
| Lifestyle cost | §5.2–5.5 p.12–13 | lifestyle | computed in code (`models/lifestyle.py:7`) |

The Phase 1 schema should classify badge, guild reward, report reward and
max-extra-reward as **derived** in the field-ownership matrix, and store the
rule-table version alongside any settlement that used them (plan §7.6).

## 6. Verification status of the original six unknowns

All but one were answered by the maintainer on 2026-07-30.

| # | Original unknown | Status |
|---|---|---|
| 1 | **Header rows** | **Answered.** All 38 headers in §3; rows 1–2 are headers, data from row 3, and every code mapping matches its real header |
| 2 | **Unmapped columns B, C, O, U, AD–AJ** | **Answered.** All eleven identified in §3. The two that change design: **C** is the player link (F-S1) and **AE–AH** duplicate Foundry's character mechanics (F-S4) |
| 3 | **Formula presence** | **Answered: there are none.** But there are three timed macros — §4.1, F-S2. Phase 2 is a migration, not a repair |
| 4 | **Other tabs** | **Answered — [OD-01](open-decisions.md) closed.** Migration scope is `Characters` plus the player tab (§2.1), whose eight headers were supplied. Shop inventory (§4.1 p.10), Moradinium accounting rate (§2.1.2 p.4) and mission logs (§2.1 p.3) exist as rules but are confirmed **out of scope**; campaign counters turn out to be player-scoped and sit on the player tab (column G) |
| 5 | **Row count and duplicates** | **Answered: 33 characters**, so the 150-row ceiling is far off. Duplicate names not specifically addressed; the first-match-wins lookup (G-7) remains a latent hazard regardless |
| 6 | **Data quality** | **Partly answered, and it mattered.** Column W's real format was not the one the parser expected, which was live data loss — F-S3, §3.2. The remaining free-text columns V, X, Y, Z, AA have not been surveyed the same way |

**The lesson worth carrying into Phase 2.** Item 6 is why this section existed.
Phase 0's reconstruction of column W was internally consistent, matched the code,
and was wrong about production — and the gap was not cosmetic, it was destroying
player data on every craft. The remaining unsurveyed free-text columns (V, X, Y, Z,
AA) are parsed by the same never-reject, always-coerce code, so the importer must
report and refuse rather than default. `.agents/AGENTS.md`: *"do not silently coerce
invalid persistent data. Imports should report the offending row and field."*

## 7. Implications for the Phase 1 schema

| Sheet artefact | Target representation |
|---|---|
| Name as identity (A) | surrogate `characters.id` (UUID); name becomes a mutable display attribute with a uniqueness rule to be decided. Column **B** (long name) becomes a second display attribute |
| **Player name (C)** | seed for `character_access`, via one Council-verified pass that resolves each name to a Discord snowflake. **Never** authorization on its own — F-S1 |
| **Weekly expenses (U)** | reconcile against the computed lifestyle cost (`models/lifestyle.py:7`) rather than importing as authoritative |
| **Abilities (AG)** | `character_abilities`, six integers. Lets the platform compute the Learning/Earning roll modifier instead of trusting a player-typed one — F-S4 |
| **Classes/subclasses (AE), race (AF), feats (AH)** | import as platform-held character detail, and add to the field-ownership matrix as **contested with Foundry** — F-S4 |
| **Macro-written J and AC** | ownership decided by [OD-36](open-decisions.md) before any dual-run period |
| Four coin columns (P–S) | one integer `balance_copper`, plus a `resource_transactions` ledger |
| Moradinium (T) | integer `character_resources` row keyed by resource type |
| Downtime as float (I) | integer **thousandth-days** (`downtime_millis`); 60-day cap = `60000`. See the note below |
| CRP string (W) | `character_tool_reputation(character_id, artisan_code, points_tenths)`, plus a `mastered` flag replacing the `"Master"` literal |
| Progress string (V) | `learning_projects` and `crafting_projects` tables |
| Skills/proficiencies (X, Y) | `character_proficiencies(character_id, artisan_code, rank)` — keyed on the **artisan**, with the tool name as a display label (§3.1) |
| Languages (Z) | `character_languages(character_id, language_code)` |
| Notable items (AA) | `items` + `character_items`, with rarity, description, benefits and link |
| Flags (K, M, AL) | booleans with explicit NOT NULL defaults |
| Row index | `sheet_row_mappings(sheet_tab, row_index, character_id)` for idempotent re-import |

**The downtime unit, ruled 2026-07-30 ([OD-08](open-decisions.md)).** The maintainer:
*"Crafting days are rounded to one digit after the dot."* Standard-item crafting
divides a base price by a level divisor, producing arbitrary fractions (`7/25 = 0.28`),
so the charged cost is a **tenth**. An eighth-day unit — this document's original
proposal — cannot represent a tenth at all, and was withdrawn.

**Thousandth-days** represent every relevant value exactly: `0.1` computed = `100`,
`0.25` master common = `250`, `0.125` master cantrip brew = `125`. **Confirmed the same
day:** the fixed table constants are charged **exactly** while computed values round to
three decimals, which lands precisely on the thousandth-day unit. OD-08 is fully closed
and tenth-days are ruled out.

**Player-level fields (the second tab)** need their own table — `players` with last
session, DM flag, last time DMed and campaign membership — joined to `characters`
through column C. See §2.
