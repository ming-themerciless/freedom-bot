# Unresolved Decisions

Status: Phase 0 deliverable. **Sixteen of the 36 were closed by maintainer answers on
2026-07-29 and 2026-07-30**, including every question that blocked Phase 1 or the
architecture gate. The remainder are marked with when they must be settled. The
independent Codex re-review approved Phase 0 on 2026-07-30, the maintainer accepted
the milestone, and the gate is closed.

Phase 0 acceptance criterion: *"unresolved ownership questions are listed
explicitly"* (plan §12).

Every decision below was reached during Phase 0 discovery and **cannot be made by
an agent**, because each one changes rules, data authority, authorization,
privacy, production behaviour or migration strategy — the exact categories
`.agents/AGENTS.md` requires an agent to stop for.

## How to use this list

Each entry states the question, why it is open, what it blocks, and — where there
is one — a recommendation with its reasoning. Maintainers should record the
decision inline (or accept the recommendation), and the decisions in plan §17 must
be settled **before Phase 1 completes**.

| Urgency | Meaning |
|---|---|
| **Blocking now** | Phase 1 cannot start or finish without it |
| **Blocking Phase 2** | Import work cannot begin |
| **Blocking Phase 3+** | Needed later, but decide early if convenient |

---

## A. Google Sheet structure

### OD-01 — Are there other tabs? · **CLOSED 2026-07-30**

**There is a player-level tab, and it is in scope.** The maintainer:

> *"Only players and characters are relevant because last session, is DM, last time
> DMed, and campaigns are player based not character based."*

**Migration scope is therefore two tabs: `Characters` and the player tab.** Anything
else in the document is out of scope.

**This is a structural finding, not just a scope answer.** The sheet already
separates *player-level* facts from *character-level* facts, and the platform's
schema should mirror that split rather than flattening it:

| Level | Facts | Platform home |
|---|---|---|
| **Player** | last session, is DM, last time DMed, campaigns | `players` / platform users |
| **Character** | the 38 columns of `Characters` | `characters` |
| **Join** | `Characters` column **C** (Player Name) | `character_access` |

Three consequences:

1. **Column C is the foreign key**, not merely a helpful hint. The two tabs are
   already a normalised two-table model joined on player name, which is much closer
   to the target schema than Phase 0 assumed.
2. **`is DM` is authorization data that already exists.** Plan §4.1 needs a DM
   capability and [OD-18](#od-18--discord-guild-council-and-dm-role-snowflakes--blocking-phase-3)
   asks which Discord roles grant it. There is an existing answer in the sheet to
   reconcile against — a per-player flag maintained by the people who actually know.
   It is *evidence*, not authorization: effective privilege still resolves from
   Discord role IDs server-side per
   [ADR 0004](../adr/0004-discord-oauth2-authentication.md).
3. **`campaigns` being player-based** matters for the mission/attendance model in
   Phases 6–8. A player belongs to campaigns; a character is played within them. The
   plan's mission records should attach campaign membership at the player level.

**Column headers supplied 2026-07-30 — the Sheet side of discovery is complete.**

`Player Name`, `Discord Name`, `Last date played`, `Active DM`, `Last date DMed`,
`Latest date to DM`, `Campaign Counter`, `No shows`. Full analysis in
[sheet-inventory.md §2.1](sheet-inventory.md#21-the-player-tab); three findings:

- **F-S5 — the Discord link already exists.** `Characters.C → player.A → player.B`
  completes `character → player → Discord`. It is a *username*, not a snowflake, so it
  seeds a Council-verified matching pass rather than granting authorization.
- **F-S6 — *Last date played* and *No shows* are recorded at both levels.** Probably
  player-level aggregates of the character rows, but that is an inference; the importer
  should compute the aggregate, compare, and report disagreement rather than trust
  either side.
- **F-S7 — *"Latest date to DM"* is a deadline with no rule behind it.** Nothing in the
  rule catalogue covers a DM rotation obligation. Either a hand-kept Council convention
  or a missing rule. Worth confirming before Phase 6.

*Import scope settled:* shop inventory, Moradinium accounting and mission logs are
confirmed out of scope.

*Closed.*

### OD-36 — What happens to the sheet macros at cutover? · Blocking Phase 2

Raised 2026-07-30 by the answer to OD-07. **Two** timed Apps Script macros write to
the sheet: `+1` week to `J` weekly, and Frank's interest on `AC`. A third, the
living-cost→downtime grant, exists but is **switched off** — the bot does it.

They are **not in this repository**, not version-controlled, and will keep writing
throughout any verification or dual-run period.

Two problems to settle:

1. ~~**Overlap with the bot today.**~~ **Resolved 2026-07-30: the downtime macro is
   not active.** The bot alone grants the `+5` days (`models/lifestyle.py:62`), so
   downtime is **not** being granted twice. That was the one live-economy risk in this
   entry and it is closed.

   **Two macros remain active:** the weekly `+1` to `J` (living cost owed) and
   Frank's interest on `AC`.
2. **Cutover.** Either disable the macros and reimplement the accrual in the
   platform as a scheduled, audited, idempotent job — the accrual is a rule (§5
   p.12, §5.6 p.14) and belongs in the domain — or leave them running and record
   `J` and `AC` as **macro-owned** in the field-ownership matrix for the duration,
   with the platform reading and never writing them.

*Recommendation:* reimplement in the platform, because a Bastion turn or a week of
living cost must not be applied twice under retry (`.agents/AGENTS.md`), and a
timed spreadsheet script has no idempotency key. But **do not disable anything
before** the platform's equivalent is running and reconciled — the accrual is what
the whole living-cost economy rests on.

*Also worth a look while deciding:* whether the macro source is backed up
anywhere. It is currently a single point of failure holding live game rules.

### OD-02 — What do the unmapped columns hold? · ~~Blocking Phase 2~~ **CLOSED**

**Answered by the maintainer 2026-07-30.** All eleven identified; the full 38-column
map with real headers is
[sheet-inventory.md §3](sheet-inventory.md#3-column-map--characters).

| Col | Holds | Consequence |
|---|---|---|
| B | Character Name (long) | Display attribute |
| **C** | **Player Name** | **The player↔character link already exists** — seed for `character_access` (F-S1) |
| O | Aristocratic lifestyle flag | As guessed — the §5.5 p.13 lock-out marker |
| U | Weekly Expenses | Reconcile against the computed lifestyle cost |
| AD | Background | Character detail |
| **AE–AH** | **Classes/Subclasses, Race/Species, Abilities, Feats/ASIs** | **Dual-recorded with Foundry** — a contested group the matrix did not have (F-S4) |
| AI, AJ | Special Notes, Mounts | Free text |

Two of these change design rather than merely filling a gap:

- **C** means Phase 3 seeds character access from existing data rather than from
  nothing. It is a *name*, not a snowflake, and one name per character where the
  invariant allows several users — so it is evidence for an audited linking pass,
  never authorization in itself.
- **AG (abilities)** means the platform can compute the Learning/Earning roll
  modifier from data it holds, replacing a number the player currently types in,
  **without waiting for the Foundry connector.**

*Closed.*

### OD-07 — Does any bot-written column contain a formula? · ~~Blocking Phase 2~~ **CLOSED**

**Answered by the maintainer 2026-07-30: there are no formulas in the sheet.**

Phase 0's hypotheses — badge, level, living weeks, downtime and Frank's interest as
formula candidates — were all wrong. **Phase 2 is a migration, not a repair.** The
bot's 26-cell whole-row write has never destroyed a formula, because there were
none to destroy.

**But the accrual is real, and it runs as timed Apps Script macros:** `+1` week to
`J` every week; `+5` downtime days when living cost is paid (the bot does this now);
and Frank's interest on `AC`. The weekly `+1` to `J` had never been documented
anywhere before this answer.

That makes the sheet a **three-writer system** — bot, Council, macros — where every
prior concurrency statement assumed two. It also gives the whole-row-write hazard an
automated trigger: a save writes `J` from its load-time value, so an accrual that
fires inside a command's read→write window is silently reverted.

Full analysis in
[sheet-inventory.md §4](sheet-inventory.md#4-formulas-and-macros). The remaining
decision is what happens to the macros at cutover — **[OD-36](#od-36--what-happens-to-the-sheet-macros-at-cutover--blocking-phase-2)**.

*Closed, and it is the good outcome.*

### OD-08 — Downtime smallest unit and rounding · **CLOSED 2026-07-30**

**Maintainer ruling:** *"Crafting days are rounded to one digit after the dot."*

That answers the question directly. Standard-item crafting computes
`base_price / dt_div` (rules §6.5.2.3 p.22), producing arbitrary fractions —
`7/25 = 0.28`, `100/75 = 1.3333…`. Those are charged as **0.3** and **1.3**.

**Consequence: ADR 0005's eighth-days is withdrawn.** It was derived only from the
table constants and could not represent a tenth at all — the commonest crafting
path. The unit is now **thousandth-days** (`downtime_millis`), which represents every
relevant value exactly:

| Unit | `0.1` computed | `0.25` master common | `0.125` master cantrip brew |
|---|---|---|---|
| eighth-day *(withdrawn)* | ✗ | ✓ | ✓ |
| tenth-day | ✓ | ✗ | ✗ |
| **thousandth-day** | **✓** `100` | **✓** `250` | **✓** `125` |

Note that the code performs **no rounding at all today** — `dt_cost` stays a raw
float throughout `helpers/craft_calculator.py`. Applying the ruling is a small
behaviour change belonging to the Phase 5 `/craft` migration, not to Phase 0 or 1.

**Fully closed 2026-07-30.** Asked whether the fixed constants `0.25` and `0.125` are
charged exactly or rounded, the maintainer answered:

> *"Make the number exact. Maybe round after three digits, that should be enough."*

- **Table constants are exact** — `0.25` = `250` millis, `0.125` = `125` millis. No
  master-tier cost changes; the PDF is preserved verbatim.
- **Computed costs round to three decimals** — `100/75 = 1.3333…` charges `1.333`.

This supersedes the earlier *"one digit after the dot"*, which was given before the
computed/constant distinction had been put to the maintainer. The newer answer is the
specific one and the better outcome: **rounding to three decimals is rounding to the
nearest whole `downtime_millis`**, so the rule and the storage unit coincide — no second
rounding step between domain and database, and no value the rule can produce that the
unit cannot hold exactly.

*Closed.* [ADR 0005](../adr/0005-identifier-and-quantity-representation.md) is amended
and accepted.

---

## B. Rules corrections

**Resolved 2026-07-29.** The maintainer confirmed all five mismatches and ruled
that the PDF is the leading rules document. RC-02, RC-03, RC-04, RC-06 and the
CRP half of RC-09 are implemented; see
[rule-catalogue.md](../rules/rule-catalogue.md#summary-of-mismatches).

A follow-up ruling on the same day closed OD-11, OD-27 and OD-29 entirely and
settled the historical question on OD-10. **No community announcement is
required** — the maintainer assessed that neither corrected payout rule was ever
triggered in practice (see OD-10 and OD-11).

What remains open in this section is the untracked tribute item (OD-28), the
**legacy untagged CRP policy the RC-09 gate exposed (OD-34)**, and the per-command
questions OD-03, OD-04, OD-05 and OD-09.

### OD-10 — RC-02: natural-20 earning bonus is 50%, should be 20% · Blocking Phase 5.4

`models/resource.py:139` computes `Money(base_gold * 150)` = +50%. Rules §6.6
p.28 specify +20% (`* 120`). Over-pays 33.6 GP per natural 20 on the top band.

**Corrected: the code now applies +20%.**

**Resolved — no reconciliation, no announcement.** The maintainer assessed that a
natural 20 on `/work` has almost certainly never occurred, because the command
sees very little use. No player's recorded state is affected.

*Residual uncertainty, recorded honestly:* this is a judgement about usage rather
than a verified fact. The roll channel (`ROLL_CHANNEL_ID`) does receive every
roll, but `roll_dice()` emits an identical message format for `/work`, `/learn`,
`/mine` and `/sale`, so its history cannot cleanly attribute a natural 20 to
`/work`. If certainty is ever wanted, it would have to come from the sheet's
revision history instead.

### OD-11 — RC-04: special facilities, levels 5–8, aristocratic · Blocking Phase 5.9 / 10

`models/bastion.py:23` has `2`; rules §7.1 p.29 give `3`. One cell of thirteen
disagrees; every other cell matches. Under-charges maintenance by 5 GP per
accrued week.

**Corrected: the code now uses `3`.** The unrecognised-lifestyle default was
also changed from `1` to `0`, since the rules grant no allowance below a
comfortable lifestyle.

**Resolved — no historical impact.** The maintainer confirms that no character
has ever held an aristocratic lifestyle below level 9, so the incorrect cell was
never reached. The correction is forward-looking only and needs no announcement.

*Closed.*

### OD-26 — RC-06: masterpiece rarity unconstrained · Blocking Phase 5.6

Rules §6.3.3.1 p.17 specify *"a rare item of your choice"*. The code accepts any
rarity a Master may craft, and legendary interacts with the legendary
roll-progression branch in an undefined way.

**Corrected: `is_masterpiece` now requires `rarity == "rare"`**, which also
rejects the previously undefined legendary combination.

*Nothing further required.*

### OD-27 — RC-03: no 140% sale floor · Blocking Phase 5.7

Rules §4.2.1 p.12: *"The base selling percentage starts at the minimum of 140 %."*
A negative Persuasion total previously sold below 140%.

**Corrected: 140% is now a hard floor.** The haggling contribution is clamped to
`>= 0` before the 180% cap. Both PDF worked examples (p.11 and p.12) reproduce
exactly and are covered by tests.

*Nothing further required.*

### OD-28 — RC-09: Master rank prerequisite not enforced · Blocking Phase 5.5

Rules §6.3.3.1 p.17 require 100 CRP in the tool **and** crafting a free uncommon
item for the master before lessons begin. Neither is enforced; the Council catches
it manually.

**Partly corrected: the 100-CRP gate is now enforced** when a Master project
starts. Projects already under way are not retroactively blocked.

*Still open:* the tribute item (craft an uncommon item and give it to the master
free of charge) is **not** enforced, because nothing in the sheet records that it
happened. Enforcing it needs new persistent state, which belongs to the Phase 5
`/learn` migration rather than to a rule correction.

*Decide:* does the tribute item stay a Council check, or should Phase 5 add state
to track it?

### OD-34 — Legacy untagged CRP and the 100-CRP Master gate · **RULED 2026-07-30**

**Maintainer ruling:** *"We will decide on any CRP not connected to a tool once in
the beginning. Actually I don't think this is an actual real issue."*

**Related ruling, 2026-07-30 — both column W formats are acceptable.** *"I have no
issue with Tool: CRP format, we have both. It will be all right as everyone can see
it and we got no complaints."* So `7.5 (Brewer)` and `Brewer: 7.5` coexist by design;
the parser reads both, and which one a save writes back is a **cosmetic** choice, not
a correctness one.

**This ruling covers the format, not the loss.** The two are separable and only the
first is cosmetic: before the 2026-07-30 fix, a `/craft` did not merely rewrite the
notation, it **dropped every other tool's balance and reset the crafted tool to the
new award alone** (`7.5 (Brewer), 2.5 (Calligrapher)` → `Brewer: 2.5`). That is
invisible to a reader who does not remember the prior value, which is consistent with
no complaints having been raised. The parser fix stops it; what was already
overwritten is only recoverable from Sheets version history.

Recorded as **option (a), lightweight**: untagged CRP is resolved **once, by hand,
at import** rather than by a code policy. Current behaviour stays as-is until then.

The ruling is well-founded, and the 2026-07-30 format finding is why: the canonical
form of column W is **per-tool** (`7.5 (Brewer)`), so the untagged `general` bucket
only arises from a bare number with no tool at all. It is a rare legacy shape, not
the normal case — which is exactly what makes a one-time manual assignment the
proportionate answer instead of a migration project.

**Consequently unchanged:** the `general` fallback in `get_tool_crp()`
(`models/skills.py`) stays, `test_untagged_legacy_total_counts_for_any_tool` stays,
and the Phase 2 importer must surface any bare-number cell in its report for the
one-time assignment.

**One consequence of the ruling, recorded 2026-07-30 while fixing the Codex re-review
findings:** the `general` bucket counts for a tool only while it is the **sole** entry,
so the first per-tool award a legacy character earns shadows their untagged total —
`120` plus a 2.5 Smith award reads 2.5 at the gate, not 122.5. That is a direct
consequence of resolving untagged CRP by hand rather than in code, and it makes the
import assignment time-sensitive for any character still holding a bare number. It is
pinned by `test_an_award_beside_an_untagged_legacy_total_shadows_it`, which records it
as the ruling's consequence rather than as intended behaviour. The `Painter`-style abbreviation problem in
[OD-06](#od-06--tool-identity--resolved-2026-07-30-residual-free-text-validation) is the
*sharper* version of this concern and is still open.

*Closed as a policy question. Retained below for the reasoning and for the import
report requirement.*

---

Original write-up, 2026-07-29. **This was an ambiguity, not a recommendation — the
code embodied one reading of the rules and it might have been the wrong one.**

**The rule.** §6.3.3.1 p.17: a master takes a student on once they have
accumulated 100 crafting reputation points **with that tool**. CRP is per-tool by
rule.

**The data.** Column W has two historical encodings
([sheet-inventory.md §3.2](sheet-inventory.md#32-column-w--crafting-reputation-points-crp)).
A per-tool list (`Smith: 40, Alchemist: 12.5`) parses into `crp_dict` keyed by
tool. But a **bare number** — the older encoding, written before per-tool
tracking existed — parses into the single untagged bucket
`crp_dict = {"general": n}`. That bucket carries no record of which tool earned it.

**What the code currently does.** `Skills.get_tool_crp()` (`models/skills.py:232`)
returns an exact per-tool match if one exists. Failing that, if `crp_dict` is
*exactly* `["general"]`, it returns the untagged total **for whichever tool was
asked about** (`models/skills.py:241`). So a character whose sheet reads `120`
satisfies the 100-CRP Master prerequisite for **any** tool — including one they
have demonstrably never used. Once any per-tool key exists alongside `general`,
the fallback stops applying (`test_untagged_total_is_ignored_once_tools_are_tracked_separately`).

**Why it may be wrong.** It grants a Master prerequisite the rule ties to a
specific tool, on evidence that does not identify a tool. It is permissive in the
one direction the rules are strict about, and §6.3.3.1 permits one Master rank
*for life* — so an incorrectly granted Master rank is not correctable by a later
ruling.

**Why it was written that way.** It preserves existing production behaviour for
characters whose reputation predates per-tool tracking. Removing it without a
migration would silently revoke a prerequisite those characters may legitimately
hold, mid-project, with no notice.

**The maintainer must choose. Options, with what each costs:**

| Option | Behaviour | Cost |
|---|---|---|
| **(a) Council assignment** | Untagged CRP counts for **no** tool. The Council migrates each legacy balance to a named tool as an audited action; `get_tool_crp()` drops the fallback | Correct by the rule, and auditable. Needs a Council pass over every legacy row **before** the gate is safe to enforce strictly, and blocks affected players until then |
| **(b) Grandfather** | Untagged CRP counts as today, but only for characters holding it **at a recorded cutoff date**; anything written afterwards must be per-tool | Nobody is blocked. Requires a cutoff and per-character state to record it, and still permits one wrong-tool Master grant per legacy character |
| **(c) Interim Council review** | Untagged CRP never auto-satisfies the gate; the command refuses and directs the player to the Council, which rules case by case | No migration project, no wrong grant. Manual work per case, and a worse player experience |
| **(d) Status quo** | Keep the current fallback as a documented, accepted deviation | Zero work. Accepts that a legacy balance can satisfy the gate for an unrelated tool |

*Also decide, whichever option is chosen:* whether the RC-09 gate belongs at
**project start** (current behaviour, which deliberately lets pre-existing
under-qualified Master projects finish) or on **every roll**.

*Resolved above by the 2026-07-30 ruling: option (a), applied by hand once at
import.* `get_tool_crp()` and
`test_untagged_legacy_total_counts_for_any_tool` are unchanged.

### OD-29 — RC-07: CRP suppressed once any tool is mastered · Blocking Phase 5.6

`ext/commands/craft.py:84` awards zero CRP if the character holds a Master rank in
**any** tool. The rules track CRP per tool and say nothing about this. Commit
`3f41a2e` suggests it was deliberate.

**Resolved 2026-07-29 — the current behaviour is correct.** The maintainer's
reasoning:

> The PDF says you can be master in one tool only, so gaining more CRP doesn't
> make sense.

This derives from the rules rather than overriding them. §6.3.3.1 p.17 gives CRP
one purpose — a master contacts you at 100 points in a tool — and limits a
character to one Master rank for life. Once that rank is held, further CRP can
never be spent, so tracking it would be meaningless.

The rationale is now recorded in `helpers/craft_calculator.py` and
`ext/commands/craft.py`, and locked in by tests that warn against "fixing" it
from the CRP table alone.

*Closed.*

### OD-03 — Is downtime granted by paying LC? · Blocking Phase 5.3 — **mostly answered**

`models/lifestyle.py:62` grants `weeks * 5` downtime when LC is paid. Rules §6
p.14 say DT is awarded every Sunday by the Guild Council, independently.

**Answered 2026-07-30.** The maintainer: *"Every week every Character has to pay
living cost. When they are paid, 5 days of Downtime are added (this is actually now
done by the Bot)."* So downtime **is** granted by paying, the current code is
correct, and the weekly `+1` to column `J` is what tracks weeks owed.

*One thing left to confirm:* there is also a **macro** that grants the `+5`
(see [OD-36](#od-36--what-happens-to-the-sheet-macros-at-cutover--blocking-phase-2)).
If both the macro and the bot are active, downtime may be granted twice for the
same week. **Worth checking before anything else in this list** — it would be a live
economy bug, not a migration concern.

### OD-04 — Frank the Money Lender · Blocking Phase 5.3 — **partly answered**

Rules §5.6 p.14 define 20% weekly interest and collection above 500 GP.
`Actor.debt` and column `AC` exist and are entirely unused **by the bot**.

**Answered 2026-07-30:** column AC is *Frank*, and interest **is** applied today —
by a timed macro, not a formula and not the bot. So the debt economy is live; only
the bot is unaware of it.

*Still to decide:* whether the platform takes over the interest accrual (see
[OD-36](#od-36--what-happens-to-the-sheet-macros-at-cutover--blocking-phase-2))
and whether it enforces the 500 GP collection threshold.

### OD-05 — Do fancy meals cost 5% downtime too? · Blocking Phase 5.6

Rules §6.5.4.1 p.26: a fancy meal *"costs just 5% of a regular consumable to
craft"*. The code applies 5% to GP only. Genuinely ambiguous.

### OD-06 — Tool identity · **RESOLVED 2026-07-30** (residual: free-text validation)

`_clean_tool_name()` reduces a tool to its first word with the possessive
stripped, so `Painter's Supplies` → `Painter`. Is the canonical identity the full
tool name or the short code?

*Recommendation:* a controlled vocabulary of short codes
([ADR 0005](../adr/0005-identifier-and-quantity-representation.md)), with the full
name as a display label. The current heuristic collides on any two tools sharing a
first word.

**Answered 2026-07-30, and the answer is a clean rule.** The maintainer:

> *"Y is the tool, W, X is the artisan (e.g. Weaver's Tools - Weaver)."*

So the sheet deliberately uses **two vocabularies**, one per column group:

| Column | Vocabulary | Example |
|---|---|---|
| **Y** Tool Proficiencies | the **tool** | `Weaver's Tools` |
| **W** CRP, **X** Crafting Skills | the **artisan** | `Weaver` |

`_clean_tool_name()` is therefore not a lossy heuristic that happens to work — it is
**the documented bridge between the two vocabularies**, converting a tool name to
its artisan. Verified across all 22 `TOOL_CHOICES`: `Alchemist`, `Brewer`,
`Calligrapher`, `Carpenter`, `Cartographer`, `Cobbler`, `Cook`, `Glassblower`,
`Herbalism`, `Jeweler`, `Leatherworker`, `Mason`, `Painter`, `Poisoner`, `Potter`,
`Smith`, `Tinker`, `Weaver`, `Woodcarver`, `Disguise`, `Forgery`, `Thieves` — every
one is the correct artisan for its tool.

The earlier `(Calligraph)` alarm was shorthand in chat, not a sheet value: the
artisan for `Calligrapher's Supplies` is `Calligrapher`, and that matches.

**Resolution for the schema.** Identity is the **artisan code**; the tool name is a
display label attached to it. One `tools` vocabulary table with both, keyed on the
artisan code, and column Y normalises into it on import. This is what
[ADR 0005](../adr/0005-identifier-and-quantity-representation.md) means by
*"controlled vocabulary keyed by a tool code"* — now with the two names distinguished
rather than conflated.

**What stays open, and it is smaller than it was.** W, X and Y remain free text, so
a genuine typo or a non-canonical artisan still resolves to **0.0 silently**, and the
RC-09 Master gate reads that value. The import must therefore reject an unrecognised
artisan and report the row rather than defaulting — not guess. Current behaviour is
pinned by `test_an_abbreviated_tool_name_silently_resolves_to_zero`, which is
retained as a description of the hazard. It must **not** be "fixed" with prefix
matching: that would silently merge `Painter`/`Potter`-style collisions instead of
failing loudly.

**Applied 2026-07-30 (Codex re-review, *Important*).** Writes now use the same bridge
as reads: `Skills.add_tool_crp()` resolves the artisan with `_clean_tool_name()`, so a
CRP award lands on the existing entry rather than adding a second spelling of the same
artisan, and duplicate spellings already in a cell are folded into one. This closes the
*write* half of the identity question; the residual above is about unrecognised
free-text values, which remains an import-validation problem.

**Boundary confirmed 2026-07-30 (second Codex re-review, *Blocking* — F-S3c).**
Duplicate CRP entries that differ **only in case** are now summed at read time, since
case is not an identity question. The bridge is deliberately **not** applied at read
time: it collapses a name to its first word, so merging on it would silently commit a
free-text cell to that collapse — including for an unrecognised artisan, which the
residual above says must fail loudly at import rather than be guessed. `Smith` beside
`Smith's Tools` therefore still reads as two entries and is folded only when
`add_tool_crp()` awards CRP for that tool. See
[sheet-inventory.md §3.2 F-S3c](sheet-inventory.md#32-column-w--crafting-reputation-points-crp).

### OD-09 — Disguise and forgery kit learning cost · Blocking Phase 5.5

Rules §6.3.3.4 p.18: the NPC *"will agree on a price with you"*. The code
defaults to 10 GP. Is 10 GP the intended default, or should the override be
mandatory for these two?

---

## C. Data ownership

### OD-13 — Contested field groups · Blocking write-enablement

Four groups need explicit ownership rulings. Full analysis in
[field-ownership.md](../rules/field-ownership.md).

| Group | Question | Recommendation |
|---|---|---|
| ~~**Electrum**~~ | ~~Foundry has `ep`; the Sheet and the rules do not~~ | **CLOSED 2026-07-30.** The maintainer confirms no actor holds electrum and the game does not use it, so all three systems agree. A nonzero `ep` is an **anomaly**: warn and refuse, never convert. Note also that **`Electrum` is a badge tier name** (rules §3 p.8–9) — a `Electrum` in Sheet column **E** is a badge, not currency, and the two must never be conflated by a name match |
| **Notable items** | Automated Foundry↔Sheet matching, or Council linking? | Council linking. Fuzzy name matching fails worst on the high-value items where a mistake matters most |
| **Languages** | Which code table; who owns additions? | Platform code table seeded from the `/learn` dropdown plus rules §6.3.1 p.16; Council owns additions |
| **Weapon proficiencies / masteries** | Platform-granted or Foundry-recorded? | Platform-granted — rules §6.3.2 p.16 make them a downtime purchase |

### OD-15 — Who owns character level? · Blocking Phase 7, decide by Phase 1

Plan §6.1 puts level under Foundry. Rules §3.1 p.9–10 derive it from cumulative
mission count, and rules §2.1.1 p.3–4 plus `.agents/AGENTS.md` require Council
approval with **no automatic advancement**.

If Foundry owns level, a player editing their own Foundry sheet grants themselves
a level and the platform imports it. If the platform owns level, the two disagree
whenever a player levels in Foundry before approval.

*Recommendation:* **Council-approved shared.** The platform computes the eligible
level from mission count; Foundry reports the actual level; a mismatch becomes an
approval proposal. Satisfies the invariant without pretending Foundry is not where
levelling happens.

*This is the most consequential unresolved item in Phase 0.*

### OD-16 — Should `/info` remain unrestricted? · Blocking Phase 3

`/info` has no channel restriction and no authorization, and replies
non-ephemerally. Any guild member can read any character's full financial state
from any channel.

*Decide:* leave open (a deliberate transparency choice), make ephemeral, or scope
to linked characters plus Council.

### OD-17 — How long may the bot remain unauthorized? · Blocking Phase 3 planning

Phase 3 gives the **web app** authorization. The bot keeps its current
no-ownership-check behaviour until each command is migrated in Phase 5.

*Decide:* is that acceptable for the Phase 3–5 window, or should a
`character_access` check be back-ported to the bot as soon as the table exists?

*Recommendation:* back-port as soon as `character_access` is populated. It is a
small change at the cog boundary, and it closes the largest live authorization
gap months earlier than Phase 5 would.

---

## D. Foundry

**Resolved 2026-07-30.** Maintainer answers closed OD-12 and OD-14 and the
electrum half of OD-13. **OD-30 remains the only open Foundry item**, and it is the
last thing gating the Foundry half of Phase 2.

### OD-12 — Which Foundry instance is authoritative? · ~~Blocking Phase 2 and 7~~ **CLOSED**

Phase 0 reported that three instances (ports 30001–30003) each held a world
directory named `the-guild`, and concluded that a maintainer had to declare one
authoritative or risk importing a stale parallel copy of every character.

**The premise was wrong.** The maintainer clarified that the game *The Guild* is
shared: `/home/foundry/shared/worlds` is bind-mounted onto each instance's
`foundrydata/Data/worlds`, so all three see the same directory. Verified — all
three paths to `the-guild` resolve to **inode 4388511 on device 64769**, and
`/etc/fstab` declares the binds.

**Resolution: there is nothing to choose.** One world, three front doors. No
stale-copy risk exists. The consequences are recorded in
[foundry-mapping.md §3](foundry-mapping.md#3-topology-one-shared-world-behind-three-instances)
and [ADR 0006](../adr/0006-foundry-integration-boundary.md), and they simplify the
design:

- `external_worlds` keys on **world ID**, not (instance, world ID) — composing the
  instance in would split one world into three phantom identities and generate
  spurious differences between them.
- The instance is **connection configuration**, repointable without touching world
  or actor identity.
- **One** service principal, not three.

*Also confirmed:* the Actor folder is `Characters (active)` and there are no
sub-folders.

*New operational constraint, not a decision.* LevelDB takes an exclusive lock, so
only one instance can host `the-guild` at a time; a second launch fails cleanly
rather than corrupting anything (local ext4, so the lock is effective). The
connector must therefore be repointable by configuration and must not assume port
30001. Recorded as topology **F-2a**.

*Closed.*

### OD-14 — Supported Foundry and dnd5e version range · ~~Blocking Phase 7~~ **CLOSED**

Verified baseline: core `14.365`, system `dnd5e` `5.3.3`, system compatibility
`minimum 13.347 / verified 14`. Observed 2026-07-30: all three instances run that
same tuple, but the Foundry binary and the `systems/` tree are **per-instance**
(`/home/foundry/dist/foundryN/`), so they are independently upgradable against the
one shared world.

**Resolved 2026-07-30.** The maintainer's ruling: *"It's enough if we cover the
latest as these are running on my system now and I don't specifically want to give
it to anyone else."* Recorded as a **single-deployment, non-distributed** policy:

| Aspect | Policy |
|---|---|
| Supported tuple | Exactly the deployed one — core `14.365`, `dnd5e` `5.3.3` — held in **configuration**, not hard-coded |
| On mismatch | **Fail closed**, with a diagnostic naming observed and expected versions. No degrading, no guessing, no partial import |
| On upgrade | The sync stops **on purpose** until the tuple is validated and the configured value updated |
| Backwards compatibility | None owed — there is no third-party consumer |

*Carried forward as an operational obligation:* updating the pin belongs on the
Foundry upgrade checklist, or a routine upgrade will break the sync at a moment
nobody expects.

*Closed.*

### OD-30 — Foundry actor export validating the field paths · **CLOSED 2026-07-30**

**Satisfied.** The maintainer supplied two real Actor exports — a level-9 Paladin (128
items) and a level-14 Sorceress (364 items). Every path in
[foundry-mapping.md §4.2](foundry-mapping.md#42-character-mechanics--verified-against-two-real-actors)
was checked against both. Most held; **five corrections** resulted:

| # | Finding |
|---|---|
| **F-F1** | A manual export carries `"_id": null` — the real ID survives only in the filename. Mappings must come from the module/API, never from an export |
| **F-F2** | Derived values are **absent**, not merely derived: `abilities.*.mod`, `hp.max`, `ac.flat`, `attributes.prof`, `details.level`. The platform computes the ability modifier itself |
| **F-F3** | `system.tools` is keyed by **artisan name** — the same vocabulary as Sheet columns W/X. The tool code table is shared with Foundry, not translated. Three aliases needed (`disg`, `scrolls`, instruments) |
| **F-F4** | **Bastions *are* modelled in Foundry**, richly — `system.bastion` plus `facility` items with type, subtype, size and order. This reverses a §4.3 claim and creates a contested group the matrix did not have |
| **F-F5** | An actor is **1.1–3.3 MB of JSON** with no embedded images — real item volume. Phase 7's snapshot endpoint needs megabyte-scale request limits |

Two further traps worth naming, both of the match-by-name variety:

- **"Experience" means different things on each side.** Sheet column G is a *mission
  count*; Foundry's `details.xp.value` is D&D XP (48 000 / 140 000). Never reconcile
  them.
- **Class, race and subclass names are customised** (`name: "Sorceress"` /
  `identifier: "sorcerer"`). Map on `system.identifier`.

*Closed.* The committed fixture is hand-written to match the verified shape; neither
export is committed.

**Recommended route — a purpose-built throwaway actor, involving no player data at
all.** Create a new actor in a scratch world on the same system version, populate
only what the platform reads, and export that. Full field list and the anonymised
fallback route in
[foundry-mapping.md §7.1](foundry-mapping.md#71-the-remaining-item-and-the-cheapest-safe-way-to-get-it).

Worth including a nonzero `system.currency.ep` even though the game uses no
electrum, so the importer's anomaly-warning path has a fixture.

*Needed from:* a maintainer.

---

## E. Authorization and policy

### OD-18 — Discord guild, Council and DM role snowflakes · Blocking Phase 3

Plan §17 requires these as configuration. Which roles grant DM capability?

`/sale` currently matches the role **name** `shop owner`; that role's snowflake is
needed too.

### OD-24 — Platform Administrator scope · Blocking Phase 3

Plan §4.1: the administrator role *"must not silently imply game-policy
authority"*.

*Decide:* may an administrator act with Council capability in a break-glass case?
If so, how is it audited and announced?

### OD-31 — Ordinary-user website mutations · Blocking Phase 3

Plan §4.3 and `.agents/AGENTS.md`: ordinary users initially get a **read-only**
website. Confirm this holds for the initial release, and name any narrow action to
be delegated later.

### OD-32 — May an approver approve their own draft? · Blocking Phase 6

Plan §17. Also: are there thresholds requiring a second approver?

### OD-33 — Event and announcement channel mappings · Blocking Phase 8

Plan §17. The rules name `#goodies-confirmation` (§2.1.2 p.4), `#downtime` (§6
p.14), `#announcements` (§6 p.14), `#trading` (§4.1 p.10),
`#offers-player-services` (§4.2 p.11), `#bastion-turns` (§7.2 p.30),
`#keep-it-rolling` (§7.2 p.30), `#characters-and-bastions` (§7.3 p.30) and
`#lifestyle-work-and.mining` (§6.4 p.18). Snowflakes are needed for each the
platform will use.

---

## F. Operations

### OD-19 — Production domain for the web application · Blocking Phase 3

Caddy currently serves `foundry1..3.rpgworld.org`.

### OD-20 — Same host as Foundry, or separate? · Blocking Phase 3

This host already runs three Foundry instances plus the live bot.

### OD-21 — PostgreSQL deployment and backup method · Required during Phase 1

Managed service, container, or host package? Backup target, retention, and
off-host copy (plan §14.3).

### OD-22 — Staging on this host or its own? · Required during Phase 1

*Recommendation:* separate host. Staging exists to rehearse migrations; a staging
component that can reach a production resource cannot do that safely.

### OD-23 — Retention periods · Blocking Phase 3

Plan §9.4 and §17: OAuth tokens, sessions, attendance records, audit events and
reports.

### OD-25 — Are Foundry ports firewalled? · Non-blocking, but check now

The three instances bind to `*:30001-30003`, not loopback, while Caddy proxies
them from `127.0.0.1`. Unless a host firewall blocks those ports, the instances
are reachable directly, bypassing Caddy's TLS.

*This is the only item in this document that may be a live security exposure and
is worth checking independently of the platform work.*

---

## G. Schema and identifiers

### OD-35 — How import idempotency is achieved · **RULED 2026-07-30**

**Maintainer ruling:** *"Take just the database ID the character gets when you fill in
the character table. You also have to write the UUID from foundry in there."*

Recorded as **option (a)**: the ID is assigned when the row is created, never derived
from anything outside the database. ADR 0003 is amended accordingly and is **no longer
blocked**; see *Identifier assignment and import idempotency* there.

**On the second half of the ruling — storing the Foundry ID — agreed, with one
structural note.** The Foundry actor ID is recorded against the character, exactly as
asked. It lives in a one-row-per-link mapping table rather than a bare column on
`characters`, for three reasons that all show up in practice:

1. A character has **more than one** external identity — a Foundry actor *and* a sheet
   row — and both need the same treatment.
2. A Foundry world rebuild **invalidates every actor `_id`**
   ([foundry-mapping.md §4.1](foundry-mapping.md#41-identity-and-mapping-keys)).
   Re-linking then replaces a mapping row instead of editing the character, and the
   old link stays visible in history.
3. Linking is a **Council action that must be auditable** — who linked it, when, and
   the name/class/level fingerprint at the time
   ([ADR 0006](../adr/0006-foundry-integration-boundary.md)).

From the outside this is the same thing: look up a character, see its Foundry actor.
The difference only shows when a link changes.

**One factual correction:** the Foundry actor `_id` is a **16-character alphanumeric
string** (e.g. `TESTACTOR000001`), not a UUID. It affects the column type — a short
`TEXT`, not `uuid` — so it is worth stating precisely. The platform's own
`characters.id` is the UUID.

*Closed. Original write-up retained below for the reasoning.*

---

Raised by Codex review of Phase 0, 2026-07-29. **ADR 0003 was internally
inconsistent on this point and could not be approved as written.**

**The inconsistency.** ADR 0003's schema conventions require primary keys to be
*"UUID (`uuid7` preferred for index locality; `uuid4` acceptable), generated by the
application"* — both of which are **random**, so the same input produces a
different ID on every run. But ADR 0003's *Alternatives considered* rejects
`bigserial` on the grounds that *"import idempotency … is much simpler when the
importer can compute an ID deterministically before writing"* — which a random
UUID cannot do. Both statements cannot hold. The consequences section repeats the
random-UUID reading; §7 of `sheet-inventory.md` and §4.1 of `foundry-mapping.md`
both assume the mapping-table reading.

**The requirement both readings serve.** Plan §12 Phase 2: *"repeated imports do
not create duplicates."* Re-running an import must find the row it created last
time.

**The maintainer must choose. Options:**

| Option | Mechanism | Assessment |
|---|---|---|
| **(a) Random UUID + unique external mapping key** | `characters.id` is `uuid7`/`uuid4`. Idempotency comes from a `UNIQUE` constraint on the mapping table — `sheet_row_mappings(sheet_tab, row_index)` and `external_actor_mappings(instance, world_id, external_actor_id)`. The importer looks up the mapping, reuses the stored `characters.id` if present, generates a new one and inserts the mapping if not, in one transaction | **Recommended.** Idempotency becomes a database constraint rather than a property of a hash function. It survives a change of external key (a Foundry world rebuild invalidates every `_id`, per foundry-mapping §4.1) because the platform ID is independent of it. It also keeps IDs unguessable, which matters once they appear in web URLs |
| **(b) Deterministic UUIDv5** | `characters.id = uuid5(namespace, external_key)`. No lookup needed — the ID *is* the function of the source | Simpler importer. But the ID is then permanently welded to an external key that is **not stable**: a Foundry world rebuild or a Sheet row reorder changes the key and therefore the identity, which is exactly what stable IDs exist to prevent. A row imported from two sources gets two different IDs and must be merged. IDs also become guessable from a known character name or row number |
| **(c) Mapping table plus a deterministic ID** | Both | Redundant. The constraint already guarantees uniqueness; the determinism adds a second source of truth that can disagree with the first |

*Note:* under (a) the ID is generated by the application before the `INSERT` and
persisted — so it is still *"generated by the application, not the database"* as
ADR 0003 requires. Random and application-generated are compatible; random and
*deterministic* are not. That is the whole of the confusion.

*Updated on the ruling, 2026-07-30:* ADR 0003 (conventions, new *Identifier
assignment* section, alternatives), ADR 0005 (Identifiers table), and this entry. The
`sheet_row_mappings` and `external_actor_mappings` shapes in
[sheet-inventory.md §7](sheet-inventory.md#7-implications-for-the-phase-1-schema) and
[foundry-mapping.md §4.1](foundry-mapping.md#41-identity-and-mapping-keys) already
matched option (a) and needed no change.

---

## Summary by urgency

**Resolved 2026-07-29 (rule corrections):** OD-10, OD-11, OD-26, OD-27 and OD-29
are closed. OD-28 is partly closed — the 100-CRP gate is implemented; the
untracked tribute item remains.

**Resolved 2026-07-30 (Foundry answers):** **OD-12** closed — its premise was
wrong; one shared bind-mounted world, not three copies. **OD-14** closed — pin to
the deployed (core, system) tuple and fail closed. The **electrum** group of
OD-13 closed — the game does not use electrum, and `Electrum` in Sheet column E is
a *badge tier*, not currency. The `Characters (active)` folder name is confirmed;
one character (Xirla) is in the sheet but not that folder, so sheet↔Foundry is not
1:1.

**Resolved 2026-07-30 (Sheet answers):** **OD-02** closed — all eleven unmapped
columns identified, with two design consequences (column **C** is the player link;
**AE–AH** duplicate Foundry's character mechanics). **OD-07** closed — *there are no
formulas*, so Phase 2 is a migration rather than a repair; but three timed macros
write to the sheet, which is a previously unknown third writer. **OD-34** ruled —
untagged CRP is resolved by hand once at import. **OD-03** and **OD-04** mostly
answered. **Opened: OD-36** (macro fate at cutover). **Escalated: OD-06** — tool-name
abbreviations have a live false-refusal path.

**Found while verifying those answers:** column W's real format was not the one the
parser understood, and `/craft` was overwriting per-tool CRP with a single tool on
every craft. Fixed, with seven regression tests — see
[phase-0-handoff.md §4.6](phase-0-handoff.md#46-column-w-was-silently-destroying-crp-data-on-every-craft--fixed).

**Required during Phase 1, before the affected design is fixed and before the
milestone completes:** OD-15, OD-21, OD-22.
*(OD-08 and OD-35 are ruled; ADRs 0003 and 0005 were amended and accepted.)*

**Blocking live behaviour today:** none outstanding. OD-34 is ruled, the column W
data loss is fixed, and the downtime double-grant risk was disproved (the macro is
off).

**Blocking Phase 2:** **OD-36** only.
*(OD-01, OD-02, OD-06, OD-07, OD-12 and OD-30 closed.)*

**Blocking Phase 3:** OD-16, OD-17, OD-18, OD-19, OD-20, OD-23, OD-24, OD-31.

**Blocking Phase 5 (per command):** OD-03, OD-04, OD-05, OD-09, plus the tribute
item remainder of OD-28 and the gate-boundary half of OD-34.

**Blocking Phase 6–8:** OD-32, OD-33.

**Blocking write-enablement:** OD-13 (three of four groups remain), OD-15.
*(OD-14 closed.)*

**Check independently:** OD-25.

**Added by the Codex review of 2026-07-29:** OD-34 (legacy untagged CRP policy)
and OD-35 (import idempotency and ID generation). This is historical context:
both were subsequently ruled by the maintainer, as recorded below.

**Resolved 2026-07-30 (third round):** **OD-35** ruled — the ID is assigned at row
creation, never derived; ADR 0003 amended and unblocked. **OD-30** closed — two real
Foundry actors verified the field mapping, producing five corrections (F-F1–F-F5),
including the discovery that **Foundry models Bastions natively** and that the tool
vocabularies already agree.

**Resolved 2026-07-30 (second round):** **OD-01** — scope is `Characters` plus a
player-level tab; everything else is out of scope. **OD-06** — the sheet uses two
vocabularies (Y = tool, W/X = artisan) and `_clean_tool_name()` is the documented
bridge between them. **OD-08** — the initial one-decimal answer showed that
eighth-days were unsuitable; the later, more specific ruling below settled on
three decimals. **OD-03/OD-36** — the
downtime macro is off, so there is no double grant. The column W format question is
closed as cosmetic.

**Resolved 2026-07-30 (fourth round):** **all seven ADRs accepted**, satisfying the
Phase 0 acceptance criterion for ADR approval (the gate itself also needs the Codex
review, subsequently approved). **OD-01** closed — player tab columns supplied, and they contain the Discord link
(F-S5). **OD-08** closed — table constants exact, computed values rounded to three
decimals, which coincides exactly with the thousandth-day unit. **Bastion ownership**
settled as complementary rather than contested, with partial Foundry coverage binding on
the design.

**No open decision blocks Phase 1 from starting.** The Phase 0 review gate is
closed: the independent Codex re-review approved the architecture and data
handling, and the maintainer accepted the milestone on 2026-07-30.

What remains, in the order it will be needed:

| When | Decisions |
|---|---|
| Early Phase 1 | **OD-15** (who owns character level) — decide before the schema fixes it; **OD-21**, **OD-22** (PostgreSQL deployment, staging) |
| Phase 2 | **OD-36** (the two live macros at cutover), plus **F-S6** (are the player-level *Last date played* / *No shows* aggregates?) and **F-S7** (is *"Latest date to DM"* a rule?) |
| Phase 3 | OD-16, OD-17, OD-18, OD-19, OD-20, OD-23, OD-24, OD-31 — mostly authorization parameters |
| Write-enablement | OD-13's remaining groups, OD-15 |
| Phase 5–8 | OD-03, OD-04, OD-05, OD-09, OD-28 tribute item, OD-32, OD-33 |
