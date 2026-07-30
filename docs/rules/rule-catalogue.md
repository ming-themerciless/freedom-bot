# Rule Catalogue

Status: Phase 0 deliverable — awaiting maintainer and Codex review. Five rule
mismatches corrected under the maintainer ruling of 2026-07-29.

Primary source: `Freedom Blades - Homebrew Rules.pdf` (42 pages, in-repo).
Page numbers below are **PDF page numbers**, counted from the first page.

This catalogue maps each rule the platform implements — or must implement — to
its source section, and records whether the current code agrees with it.

It **cites** rules; it does not reproduce them. Where a numeric table is
reflected in the code, the catalogue states that the code matches or differs, and
gives the constant's location. Official D&D 2024 / 5.5 content is referenced by
name only, per `.agents/AGENTS.md`.

## Precedence

Per `.agents/AGENTS.md`, in descending order:

1. explicit Freedom Blades rulings supplied by maintainers;
2. `Freedom Blades - Homebrew Rules.pdf`;
3. official D&D 2024 / 5.5 rules;
4. existing behavior, where the above are silent.

## Status legend

| Status | Meaning |
|---|---|
| **Implemented ✓** | Code verified against the PDF, cell by cell where a table exists |
| **Corrected ✓** | Code and PDF disagreed; corrected to the PDF on maintainer ruling, with regression tests |
| **Mismatch ✗** | Code and PDF disagree; needs a maintainer ruling before Phase 5 |
| **Ambiguous ?** | PDF is genuinely open to more than one reading |
| **Not implemented** | Rule exists; no code implements it |
| **Level 4** | No PDF rule; current behavior stands by precedence rule 4 |

## Maintainer ruling of 2026-07-29

The maintainer reviewed the five mismatches found in Phase 0, confirmed all five,
and ruled that **the PDF is the leading rules document** and the code must follow
it rather than the previous implementation.

RC-02, RC-03, RC-04, RC-06 and RC-09 were corrected accordingly and are marked
**Corrected ✓** below. **RC-07 was not changed** — the PDF is silent there, so
there is no PDF rule to implement; see RC-07 for what is still needed.

---

## A. Missions, rewards and advancement

Not implemented in code today. Required for Phases 8–9.

| ID | Rule | Source | Status |
|---|---|---|---|
| RC-A1 | Mission difficulty badge; join within two ranks; mentor rule forgoes advancement credit | §2.1 p.3 | Not implemented |
| RC-A2 | Join priority by longest time since last played (`last_played`, column H) | §2.1 p.3 | Not implemented |
| RC-A3 | Campaign counter, lowest counter gets priority; at least one character kept free | §2.1 p.3 | Not implemented |
| RC-A4 | Advancement credit requires ≥3 hours and a reasonable threat; DM chooses which character | §2.1.1 p.3–4 | Not implemented |
| RC-A5 | Guild reward and report reward by rank | §2.1.2 p.4, table §3 p.8–9 | Not implemented |
| RC-A6 | Advancement-for-gold: forgo the mission count for 30 GP per level already achieved | §2.1.2 p.4 | Not implemented |
| RC-A7 | Moradinium accounting rate — **50 GP per 1 Moradinium**, Council-adjustable, changes apply to future conversions only | §2.1.2 p.4 | Not implemented |
| RC-A8 | Extra rewards default to sale at 100% market value (200% crafting cost for magic items); equal split | §2.1.3 p.4–5 | Not implemented |
| RC-A9 | Item claim compensates the rest of the party pro rata | §2.1.3 p.5 | Not implemented |
| RC-A10 | Maximum extra reward = **10 × the guild reward of the mission's difficulty badge** (not the character's) | §2.1.3.1 p.5 | Not implemented |
| RC-A11 | Item-distribution dispute: d20 per participant, claim in descending order, ties re-rolled within their band | §2.1.3.2 p.6 | Not implemented |
| RC-A12 | Badge / level / rank / guild reward / max extra / report reward table (10 rows, Iron→Adamantine) | §3 p.8–9 | Not implemented |
| RC-A13 | Missions-per-level and cumulative-missions table (levels 1→20) | §3.1 p.9–10 | Not implemented |
| RC-A14 | All guild members start their first mission at level 4 | §3 p.8 | Not implemented |
| RC-A15 | Rewards are credited only after confirmation posted in `#goodies-confirmation` | §2.1.2 p.4 | Not implemented — informs the Phase 6 approval flow |

RC-A12 is the anchor table for Phase 9. RC-A7 and RC-A10 are the two constants
most likely to change by Council decision, so both must carry a **policy
version** on every settlement (plan §7.6).

## B. Combat and play rules

Table-side rules with no platform representation. Catalogued for completeness;
none is a candidate for automation.

| ID | Rule | Source |
|---|---|---|
| RC-B1 | Better criticals — max normal damage plus rolled dice | §2.2 p.6 |
| RC-B2 | Hardcore healing — hit-dice limits on short and long rests | §2.3 p.6–7 |
| RC-B3 | Wilderness rest — CON save, escalating DC | §2.4 p.7 |
| RC-B4 | Inspiration coins — d6 table, one at a time | §2.5 p.7 |
| RC-B5 | Scroll-carrying limit tied to proficiency bonus | §2.6 p.7–8 |
| RC-B6 | Potion/brew/poison fragility; potion bandolier | §2.7 p.8 |
| RC-B7 | Flanking | §2.8 p.8 |
| RC-B8 | Character creation constraints (27-point buy, average HP, no evil alignments) | §1.1 p.1 |
| RC-B9 | Extra ASI; barbarian resistance choice; stacking resistances | §1.3–1.4 p.2–3 |

`inspiration` (column D) is round-tripped by the bot but never validated against
RC-B4; it is currently opaque free text.

## C. Buying and selling

### RC-01 — Sale percentage — **Implemented ✓**

- **Source:** §4.1 p.11 (140% of crafting cost), §4.1.1 p.11 (haggling adds the
  Persuasion Earning Roll to the percentage; cap 180%; natural 20 adds +10%),
  §4.2.1 p.11–12 (own shop adds +20%; overall maximum 190%).
- **Code:** `Resource.sale()` — `models/resource.py:151`.
- **Verified:** the PDF worked example on p.12 (140 + 20 Persuasion + 10 nat-20 +
  20 shop-owner = 190%) is reproduced exactly. The 180% cap is applied before the
  nat-20 bonus, which is what makes 190% reachable — matching the PDF's stated
  stacking.

### RC-03 — Sale percentage floor — **Corrected ✓**

- **Source:** §4.2.1 p.12 — *"The base selling percentage starts at the minimum
  of 140 %."*
- **Was:** `models/resource.py` applied no lower bound, so a character with a
  negative Persuasion modifier could roll a total below 0 and sell below 140%.
- **Now:** the haggling contribution is clamped to `>= 0` before the 180% cap.
  The calculation was also restructured into named steps, because the previous
  single expression made the ordering of cap and natural-20 bonus hard to verify.
- **Verified:** both PDF worked examples reproduce exactly — p.11 (375 GP cost,
  roll 15 → 581.25 GP at 155%) and p.12 (25 GP greatsword, natural 20, shop
  owner → 47 GP 5 SP at 190%).
- **Tests:** `tests/test_resource.py` — base, floor, haggling, 180% cap, natural
  20 stacking past the cap, and the p.12 own-shop maximum.

### RC-C1 — Vendor items — **Not implemented**

§4.1 p.11: items with no use beyond their stated gold value sell at 200% of
crafting cost **if sold directly after the mission**. `/sale` has no concept of
a vendor item or of mission adjacency.

### RC-C2 — Magic Item Shop inventory — **Not implemented**

§4.1 p.10: items sold to the guild enter the shop at 200% of crafting cost;
1d4 items are removed weekly in FIFO order. No inventory exists in the platform.

### RC-C3 — Shop stall purchase — **Not implemented**

§4.2 p.11: a one-time 100 GP purchase grants the Shop Owner role. `/sale` checks
for the role by **name**, and the purchase itself is manual.

## D. Lifestyle

### RC-05 — Lifestyle weekly costs — **Implemented ✓**

- **Source:** §5.1 p.12 (wretched, 0), §5.2 p.12 (modest, 7 GP), §5.3 p.13
  (comfortable, 14 GP), §5.4 p.13 (wealthy, 28 GP), §5.5 p.13 (aristocratic,
  70 GP).
- **Code:** `Lifestyle.LIFESTYLE_COSTS` — `models/lifestyle.py:7`. All five match.

### RC-D1 — Downtime accrual and cap — **Implemented ✓ (with a coupling question)**

- **Source:** §6 p.14 — 5 DT per week, maximum 60.
- **Code:** `models/lifestyle.py:62` — `min(downtime + weeks * 5, 60)`.
- **Question ([OD-03](../discovery/open-decisions.md)):** the PDF says DT is
  awarded every Sunday by the Guild Council, independently of payment. The bot
  grants it when LC is paid. Both produce the same total for a player who always
  pays, and diverge for one who does not.

### RC-D2 — Aristocratic lock-out — **Not implemented**

§5.5 p.13: choosing a lower lifestyle for even one week bars aristocratic for one
year. Column `O` (`aristocratic_flag`) is mapped in `Actor.COLUMNS` but never
read or written — plausibly the sheet-side marker for this rule
([OD-02](../discovery/open-decisions.md)).

### RC-D3 — Wretched lifestyle consequences — **Not implemented**

§5.1 p.12: theft roll or exhaustion, DC 10 CON save against disease, −1 AC and
attack rolls. All mission-time effects; no platform representation is required
unless missions are automated.

### RC-D4 — Frank the Money Lender — **Not implemented**

§5.6 p.14: 20% interest per week; collection begins above 500 GP debt.
`Actor.debt` is constructed as a `Resource` (`models/actor.py:49`) and column
`AC` is mapped, but neither is ever loaded, written or used. This is dead code
against a live rule ([OD-04](../discovery/open-decisions.md)).

### RC-D5 — Modest lifestyle paid with downtime — **Not implemented**

§5.2–5.3 p.12–13: a modest lifestyle week may be paid with a week of downtime
instead of gold. `/lc` only deducts gold.

## E. Downtime — rolls, learning and mining

### RC-D6 — Roll types — **Partially implemented**

§6.2 p.15 defines three roll types: **Learning Roll** (base ability modifier
only, no proficiency/feats/items), **Earning Roll** (with tool proficiency and
permanent modifiers), **Mining Roll** (straight d20, no modifiers).

`/mine` correctly passes `modifier=0` and `roll_mode="normal"`
(`models/resource.py:123`). `/work` and `/learn` accept a caller-supplied
`modifier`, so the *composition* of the modifier is on the honour system. A
database-backed platform can compute all three types authoritatively once ability
scores are imported from Foundry.

### RC-08 — Learning costs per category — **Implemented ✓**

- **Source:** §6.3 p.15 (general 10 GP/week; special proficiencies ≥50 GP),
  §6.3.2 p.16 (martial weapon 20; weapon mastery 25), §6.3.3.1 p.16–17
  (journeyman 0; expert 25; master 100), §6.3.3.2 p.17 (gaming sets ~10),
  §6.3.3.3 p.17 (instruments 10), §6.3.3.5 p.18 (thieves' tools ≥50),
  §6.3.3.6 p.18 (vehicles 0), §6.3.3.7 p.18 (scroll proficiency ≥50).
- **Code:** `Skills.learn_proficiency()` `gp_costs` — `models/skills.py:361`.
- **Verified:** every entry matches its cited section.
- **Note:** several PDF figures are *minimums* ("at least 50 GP", "around 10 GP",
  "negotiated with the teacher"). The `gp_cost` override option exists precisely
  for that; it is currently unbounded above and only guarded against negatives at
  the cog boundary (`ext/commands/learn.py:49`).

### RC-D7 — Learning mechanics — **Implemented ✓**

§6.3 p.15: one roll per 5 DT; d20 plus the relevant ability modifier; accumulate
to 100; overflow is lost; natural 20 adds +1%. All four reproduced at
`models/skills.py:381–413`, including the overflow clamp.

### RC-09 — Master rank prerequisite — **Corrected ✓ (partial)**

- **Source:** §6.3.3.1 p.17. A master contacts the character only after **100 CRP
  in that tool**; the character must then craft an uncommon item and give it to
  the master before lessons may begin.
- **Was:** `Skills.learn_proficiency()` enforced the one-Master-tool limit but
  neither the 100-CRP gate nor the tribute item, so a character could begin and
  complete Master lessons without ever earning CRP.
- **Now:** starting a Master project requires `Skills.MASTER_CRP_REQUIREMENT`
  (100) points for that tool, resolved by `Skills.get_tool_crp()`. The
  one-Master-tool scan was extracted to `_find_other_master_tool()` and is checked
  **first**, so a character who already holds a Master rank gets that accurate
  message rather than a misleading reputation message.
- **Applied at project start only.** A Master project already under way is not
  retroactively blocked, so nobody is stranded mid-lesson by the correction.
- **Legacy CRP data:** a sheet holding a single untagged CRP total (the
  `"general"` bucket, which predates per-tool tracking) counts toward whichever
  tool is being learned. Once any per-tool value exists, the untagged bucket is
  ignored.
- **Tests:** `tests/test_skills.py` — the gate, the threshold being met, lower
  ranks being unaffected, the one-Master message winning, in-progress projects
  continuing, and the legacy-bucket behaviour.

**Still not implemented — needs maintainer input.** The tribute item (*"craft an
uncommon item ... give that item to the master for free"*) is not enforced,
because nothing in the sheet records that it happened. Adding it needs new
persistent state, which is Phase 5 work rather than a rule correction. It remains
a Council check today — [OD-28](../discovery/open-decisions.md).

**Unchanged compounding defect.** On completion the code still sets
`crp = "Master"` and clears `crp_dict` (`models/skills.py`), destroying per-tool
CRP the rules require to be tracked separately. This is a data-model defect rather
than a rule mismatch, and fixing it means changing what column W stores — it
belongs with the Phase 5 `/learn` migration.

### RC-D8 — Kit proficiencies price — **Ambiguous ?**

§6.3.3.4 p.18: disguise and forgery kits require an NPC teacher who *"will agree
on a price with you"*. The code falls through to the generic 10 GP default
(`gp_costs.get(level, 10)`). Whether 10 GP is the intended default or whether the
override should be mandatory for these two kits is [OD-09](../discovery/open-decisions.md).

### RC-D9 — Learning disadvantage rules — **Not implemented**

§6.3.1 p.15 (learning from a book), §6.3.2 p.16 (martial weapon mastery),
§6.3.3.5 p.18 (thieves' tools unless Bard), §6.3.3.7 p.18 (scrolls unless
Wizard). All are left to the caller's `roll_mode` option.

### RC-D10 — Language script advantage — **Not implemented**

§6.3.1 p.16: advantage when the character already knows a language sharing the
same script; the PDF lists common and uncommon languages. The `/learn` language
dropdown lists 19 languages but carries no script metadata.

### RC-10 — Moradinium mining — **Implemented ✓**

- **Source:** §6.4 p.18–19. Base 2 Moradinium, +1 per 4 full points above 1;
  natural 20 grants +1 bonus for a maximum of 7. 5 DT per roll.
- **Code:** `Resource.mine_moradinium()` — `models/resource.py:126`,
  `(total + 7) // 4 + (1 if nat20 else 0)`.
- **Verified against every band of the PDF result table:**

  | Roll total | PDF | Code |
  |---|---|---|
  | 1–4 | 2 | 2 |
  | 5–8 | 3 | 3 |
  | 9–12 | 4 | 4 |
  | 13–16 | 5 | 5 |
  | 17–20 | 6 | 6 |
  | natural 20 | 7 | 7 |

### RC-02 — Earning money with tool proficiencies — **Corrected ✓**

- **Source:** §6.6 p.28. Earnings table by roll total; **natural 20 increases the
  final gold by 20%**.
- **Code:** `Resource.earn_money()` — `models/resource.py:138–139`.
- **Bands verified — correct:**

  | Roll total | PDF | Code |
  |---|---|---|
  | 0–10 | 7 GP | 7 GP |
  | 11–15 | 14 GP | 14 GP |
  | 16–20 | 28 GP | 28 GP |
  | 21–25 | 56 GP | 56 GP |
  | 26+ | 112 GP | 112 GP |

- **Was:** on a natural 20 the code computed `Money(base_gold * 150)`. `Money` is
  denominated in copper, so that is `base_gold × 1.5` gold — a **50% bonus**,
  over-paying 33.6 GP per natural 20 on the top band.
- **Now:** `Money(base_gold * 120)`, i.e. the +20% the rule specifies. Every band
  is exact in copper (840 / 1 680 / 3 360 / 6 720 / 13 440), so no rounding is
  involved.
- **Tests:** `tests/test_resource.py` — the natural-20 bonus at two bands, the
  fractional-coin case (7 GP → 8 GP 4 SP), and a table-driven check of all five
  earnings bands at both boundaries.
- **Outstanding Council decision:** this over-paid players for as long as the
  code ran. Correcting it going forward is done; whether to reconcile historical
  earnings remains open — [OD-10](../discovery/open-decisions.md).

### RC-D11 — Natural-1 consequences — **Not implemented**

§6.6 p.28–29 lists six tool/skill pairs with automatic consequences on a natural
1, two of which deduct downtime (−20 DT) and two of which deduct gold (−30 GP).
None is implemented. The advantage rule for holding both the tool proficiency and
the relevant skill is likewise left to the caller.

## F. Crafting

The crafting implementation is the most faithful part of the codebase. Every
numeric table below was compared cell by cell against the PDF.

### RC-F1 — Tool and rarity gating — **Implemented ✓**

§6.5.2 p.19: journeyman crafts standard and common; expert adds uncommon; master
adds rare, very rare and legendary. `helpers/craft_calculator.py:90` matches.

§6.5.1 p.19 (Arcana proficiency not required) needs no implementation.

### RC-F2 — Tool → item-type table — **Not implemented (by design)**

§6.5.2 p.19–21 maps 19 tools to item categories, and the PDF itself states the
table is *not exhaustive* and that the Guild Council decides in doubt. The code
enforces only the five unambiguous constraints —
scroll→Calligrapher, tattoo→Painter, brew→Brewer, meal→Cook,
gather-ingredients→Herbalism (`helpers/craft_calculator.py:78–87`).

Leaving the rest to Council judgement is consistent with the rule. The Phase 11
facility catalogue should keep it that way rather than encoding a lookup that the
rules explicitly decline to make binding.

### RC-F3 — Non-consumables — **Implemented ✓**

§6.5.2.3 p.22. Verified: standard (GP÷2 cost; DT = price÷10 / ÷25 / ÷75),
common (50 GP, 1 Mor, 5/3/1 DT), uncommon (200 GP, 4 Mor, −/5/3),
rare (2 000 GP, 16 Mor, −/−/5), very rare (20 000 GP, 64 Mor, −/−/20),
legendary (100 000 GP, 256 Mor, roll-based).
Code: `helpers/craft_calculator.py:133–153`.

### RC-F4 — Legendary progression — **Implemented ✓**

§6.5.2.3 p.22 footnote ³: 1d20 per 5 days of downtime, complete at 100%.
Code: `ext/commands/craft.py:164–182`. Materials are charged once at project
creation.

### RC-F5 — Consumables — **Implemented ✓**

§6.5.2.4 p.23. Verified: standard (DT = price÷25 / ÷50 / ÷100),
common (25 GP, 1/½/¼), uncommon (50 GP, −/1/½), rare (200 GP, −/−/1),
very rare (400 GP, −/−/5), legendary (1 000 GP, −/−/20).
Code: `helpers/craft_calculator.py:155–175`.

The footnote — spell material costs are paid additionally — is served by the
`extra_cost` option.

### RC-F6 — Spell scrolls and spellwrought tattoos — **Implemented ✓**

§6.5.2.5 p.23–24. All ten spell levels verified against
`SCROLL_TATTOO_TABLE` (`helpers/craft_calculator.py:25`), including the
tattoo `None` entries at levels 6–9 and the correct journeyman/expert/master
availability per level.

### RC-F7 — Poisons — **Implemented ✓**

§6.5.2.6 p.24–25. All sixteen poisons verified against `POISON_TABLE`
(`helpers/craft_calculator.py:5`), including per-level availability and the
2½-day master entries for Midnight Tears and Yserthrax's Corruption.

### RC-F8 — Brews — **Implemented ✓**

§6.5.4.2 p.27. All seven (spell level, concentration) rows verified against
`BREW_TABLE` (`helpers/craft_calculator.py:40`), including the ⅛-day master
cantrip entry.

The brew *eligibility* criteria (§6.5.4.2 p.26–27: beneficial only, 1 minute to
1 hour, no costly components, targets creatures, no radius) and the
multiple-brew CON save are **not implemented** — they are DM adjudication.

### RC-F9 — Fancy meals — **Implemented ✓ with an ambiguity**

§6.5.4.1 p.26. Rarity ↔ effect count (common 1, uncommon 2, rare 3) is enforced
(`helpers/craft_calculator.py:108`). The 5% cost is applied to GP
(`helpers/craft_calculator.py:177`).

**[OD-05](../discovery/open-decisions.md):** the PDF says a fancy meal *"costs
just 5% of a regular consumable to craft"*. Whether "cost" includes downtime is
not stated. The code applies 5% to GP only.

### RC-F10 — Herbalism gathering — **Implemented ✓ (over-broad)**

§6.5.4.3 p.28: gathering your own ingredients doubles DT and removes the GP cost.
Code: `helpers/craft_calculator.py:250`. The PDF scopes this to healing potions,
antidotes, drugs and ointments; the code allows it for any non-consumable-excluded
craft made with a Herbalism Kit.

### RC-F11 — Crafting reputation points — **Implemented ✓, gated by an uncited policy**

§6.3.3.1 p.17 CRP table: common 2.5 (non-consumable) / 0.5 (consumable);
uncommon 7.5 / 1.5. Code: `helpers/craft_calculator.py:258–272`. Values match.

### RC-07 — CRP suppression for masters — **Implemented ✓ (confirmed ruling)**

`ext/commands/craft.py:84` computes `has_master_tool` across **all** the
character's tools and passes it to `calculate_craft`, which then awards zero CRP
(`helpers/craft_calculator.py:260`).

The PDF tracks CRP *per tool* and uses it to gate *that tool's* Master rank. It
says nothing about ceasing CRP accrual once any Master rank is held. Commit
`3f41a2e` describes this as intentional ("prevent CRP gain for master-level
crafters"), so it is likely a deliberate Council ruling — but it is a precedence
level 1 ruling that is not written down anywhere.

**Confirmed correct by the maintainer on 2026-07-29, with this reasoning:**

> The PDF says you can be master in one tool only, so gaining more CRP doesn't
> make sense.

That follows from the rules rather than overriding them. §6.3.3.1 p.17 gives CRP
exactly one function — at 100 points in a tool, a master contacts you to teach
that tool — and the same section limits a character to *"only become a Master in
one artisan's tool"*. Once that one Master rank is held, no amount of further CRP
in any tool can lead anywhere, so continuing to track it would be recording a
quantity that can never be spent.

The behaviour is therefore a **derived consequence of the one-Master rule**, not
an undocumented policy. The earlier concern in this catalogue — that it was a
ruling existing only in commit `3f41a2e` — is resolved.

**Note the boundary is correct too:** suppression keys on *holding* a Master rank
(`has_master_tool`), not on being part-way toward one. A character with no Master
rank still accrues CRP in every tool independently, which is what lets them reach
100 in the tool they choose to master. [OD-29](../discovery/open-decisions.md) is
closed.

**Now protected by tests** (`tests/test_craft_calculator.py`), including the full
CRP table, quantity scaling, and an explicit case asserting that holding a Master
rank withholds reputation while still charging full crafting cost. The test
carries a comment warning against "fixing" it from the CRP table alone.

### RC-06 — Masterpiece rarity — **Corrected ✓**

- **Source:** §6.3.3.1 p.17 — on finishing Master lessons the character creates
  *"a rare item of your choice"*, paying the crafting cost without spending extra
  downtime.
- **Was:** `calculate_craft()` required master level and non-consumable and zeroed
  DT, but did not constrain rarity, so a masterpiece could be declared at common,
  uncommon, rare or very rare. A *legendary* non-consumable was additionally
  routed to the legendary roll-progression branch before the masterpiece DT
  override was reached, so the two features interacted in an undefined way.
- **Now:** `is_masterpiece` requires `rarity == "rare"`. Because that check sits
  in the masterpiece validation block, which runs **before** `is_legendary_project`
  is computed, the legendary interaction is rejected outright rather than
  producing undefined behaviour.
- **Result:** a masterpiece is 2 000 GP, 16 Moradinium and 0 downtime — the rare
  non-consumable cost with the downtime waived, exactly as §6.3.3.1 describes.
- **Tests:** `tests/test_craft_calculator.py` — the rare masterpiece costs, every
  rejected rarity, the master-level and non-consumable guards, the ordering
  relative to the general tool/rarity gate, and a check that an ordinary rare
  craft still costs its 5 days.

### RC-F12 — Assistants — **Not implemented**

§6.5.3 p.25–26: a full table of assistance ratios by rank pair and rarity, plus
three constraints (artisan spends ≥20% themselves; assistant spends ≥ the artisan's
time; ≤50% assistance on items the assistant could not craft alone).

This is the largest unimplemented crafting rule and a strong candidate for the
Phase 4 domain layer once single-character crafting is migrated.

### RC-F13 — Raw materials and cosmetic donors — **Not implemented**

§6.5.2.2 p.21 defines Mechanical Benefit versus Cosmetic Feature and the rules
for cosmetic donor items. Entirely narrative/DM adjudication; no automation
proposed.

## G. Bastions

### RC-04 — Special facility limits — **Corrected ✓**

- **Source:** §7.1 p.29–30, and the per-lifestyle caps in §5.3–5.5 p.13.
- **Code:** `Bastion.MAX_SPECIAL_FACILITIES` — `models/bastion.py:14`.
- **Cell-by-cell comparison:**

  | Level band | Lifestyle | PDF §7.1 | Code | |
  |---|---|---|---|---|
  | 1–4 | all | 0 | 0 | ✓ |
  | 5–8 | comfortable | 1 | 1 | ✓ |
  | 5–8 | wealthy | 2 | 2 | ✓ |
  | 5–8 | **aristocratic** | **3** | **3** (was 2) | **corrected** |
  | 9–12 | comfortable | 2 | 2 | ✓ |
  | 9–12 | wealthy | 4 | 4 | ✓ |
  | 9–12 | aristocratic | 5 | 5 | ✓ |
  | 13–16 | comfortable | 3 | 3 | ✓ |
  | 13–16 | wealthy | 5 | 5 | ✓ |
  | 13–16 | aristocratic | 6 | 6 | ✓ |
  | 17–20 | comfortable | 4 | 4 | ✓ |
  | 17–20 | wealthy | 6 | 6 | ✓ |
  | 17–20 | aristocratic | 7 | 7 | ✓ |
  | any | wretched / modest | 0 | 0 | ✓ |

  One cell of thirteen differed, which reads as a transcription slip rather than
  a ruling. It under-charged an aristocratic character at levels 5–8 by 5 GP per
  accrued maintenance week.

- **Second defect, also corrected:** `get_max_special_facilities()` returned a
  default of **1** for an unrecognised lifestyle. Since wretched and modest are 0
  at every level and an unknown value is a data error, the default is now **0**.
  This also matches the codebase's existing convention of treating an unparseable
  lifestyle as modest (`Lifestyle.LIFESTYLE_COSTS.get(..., 7)`).
- **Tests:** `tests/test_bastion.py` — the full thirteen-cell table, both
  sub-comfortable lifestyles at every level band, the unknown-lifestyle default,
  level-band boundaries, and maintenance cost, turn consumption and failure
  atomicity.

**Note on an unrelated pre-existing gap.** With the default now 0, a character
holding a bastion on an unrecognised lifestyle would maintain it for 0 GP. That
is a consequence of RC-G1 (bastion loss on dropping below a qualifying lifestyle)
still being unimplemented, not of this correction — the previous default of 1 was
equally arbitrary. Implementing RC-G1 closes it properly.

### RC-11 — Bastion maintenance cost — **Implemented ✓**

§5.3–5.5 p.13: each special facility costs 5 GP per week extra. Code:
`weeks_of_maintenance * special_facilities * 5` (`models/bastion.py:81`).

**Caveat:** `special_facilities` comes from a user-supplied command option and is
replaced by the computed maximum only when `<= 0`. A player may declare fewer
facilities than they hold and pay less. Phase 10 must derive this from stored
Bastion state rather than trusting the caller.

### RC-12 — Bastion turn availability — **Implemented ✓**

§7.2 p.30: one Bastion turn per LC week; orders may only be given when LC is set
to 0. `Lifestyle.pay_for_weeks()` sets `turn_available_flag = 1` when
`living_weeks` reaches 0 and a bastion is owned (`models/lifestyle.py:64`);
`maintain_bastion()` requires and then clears the flag.

### RC-G1 — Bastion loss conditions — **Not implemented**

- §7.2 p.30: twelve missed LC weeks → Bastion lost to neglect.
- §7.1 p.29: dropping below a qualifying lifestyle → Bastion lost immediately.

Neither is enforced. Column `L` accrues without bound and `/lc` accepts any
lifestyle change without checking Bastion ownership.

### RC-G2 — Basic facilities — **Not implemented**

§7.3.1 p.30: money to add or expand a basic facility is halved; no time
requirement. No basic-facility state exists.

### RC-G3 — Special facility hirelings — **Not implemented**

§7.3.2 p.30: hirelings hold the minimum rank required (journeyman for
standard/common, expert for uncommon, master for rare and above). One Bastion
turn counts as 5 days of downtime for crafting.

### RC-G4 — Specific special facilities — **Not implemented**

§7.3.3 p.30–31 adjusts four facilities: Arcane Study (§7.3.3.1), Laboratory
(§7.3.3.2), Scriptorium (§7.3.3.3), Training Area (§7.3.3.4). These are the
concrete first targets for the Phase 11 catalogue, and the Training Area's
"gain journeyman, or expert if already journeyman" effect is a good test of
whether the facility framework can express character-state mutation without a
scripting language.

### RC-G5 — Bastion mapping requirement — **Not implemented**

§7.3 p.30: facilities and hirelings must be documented in
`#characters-and-bastions` and mapped in the Foundry world `The Guild` for any
benefit to apply. This is a cross-system prerequisite that the Phase 7 Foundry
connector should be able to verify.

## H. Currency exchange — **Level 4**

`/xchange` and `models/exchange.py` implement 1 pp = 10 gp = 100 sp = 1 000 cp
with no fee and no loss. **No rule in the Homebrew PDF governs coin exchange.**
By precedence rule 4, current behavior stands; the ratios are the official 5e
ones.

If the Council ever introduces an exchange fee, it belongs in the rules document
first.

## I. Homebrew content — catalogued, not automated

§8 p.31–42 defines homebrew classes (Gunbreaker, §8.1.1 p.31), subclasses
(§8.2 p.32–34 including the Magic Colour table), weapons (§8.3 p.34–36) and
standard items (§8.4 p.36 onward). None affects the platform's calculations.
They are relevant only as Foundry-side content and as a reason the Foundry
connector must tolerate non-SRD items in a character's inventory.

---

## Summary of mismatches

All five were confirmed by the maintainer on 2026-07-29 and corrected to the PDF.

| ID | Rule | Was | Now — per PDF | Command |
|---|---|---|---|---|
| **RC-02** | Natural-20 earning bonus | +50% | **+20%** (§6.6 p.28) | `/work` |
| **RC-04** | Special facilities, levels 5–8, aristocratic | 2 | **3** (§7.1 p.29) | `/bastion` |
| **RC-06** | Masterpiece rarity | any | **rare only** (§6.3.3.1 p.17) | `/craft` |
| **RC-03** | Sale percentage floor | none | **140% floor** (§4.2.1 p.12) | `/sale` |
| **RC-09** | Master rank prerequisite | none | **100 CRP for that tool** (§6.3.3.1 p.17) | `/learn` |

### Resolved alongside the corrections

| ID | Item | Outcome |
|---|---|---|
| **RC-07** | CRP suppressed once any tool is mastered | **Confirmed correct** — it follows from the one-Master rule (§6.3.3.1 p.17). Now documented in code and covered by tests |
| **RC-02** | Historical over-payment | **No reconciliation and no announcement.** The maintainer assesses that a natural 20 on `/work` has almost certainly never occurred, as the command sees little use |
| **RC-04** | Historical under-charging | **No impact.** No character has ever held an aristocratic lifestyle below level 9, so the incorrect cell was never reached |

### Still open

| ID | Item | Needs |
|---|---|---|
| **RC-09** (part) | Tribute item — craft an uncommon item for the master | Not tracked in the sheet; needs new persistent state, so it belongs to the Phase 5 `/learn` migration — [OD-28](../discovery/open-decisions.md) |
| **RC-09** (part) | `crp = "Master"` wipes per-tool CRP on completion | A data-model defect; fixing it changes what column W stores — Phase 5 |

**No community announcement is required.** Both corrected payout rules were
assessed by the maintainer as never having been triggered in practice, so no
player's recorded state was affected.
