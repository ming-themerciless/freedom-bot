# Phase 0 — Review Submission

> ## ⚠️ This document is a historical record. Do not read it as current status.
>
> It is the submission made on **2026-07-29** and the outcome of the Codex review of
> that submission. Every statement in it describes the repository **as it was on that
> date** and is deliberately left unrewritten, because a review record that is edited
> to match later facts is no longer a record.
>
> **For current status, read
> [../discovery/phase-0-handoff.md](../discovery/phase-0-handoff.md).**
>
> Materially superseded since 2026-07-29, all on 2026-07-30:
>
> | This document says | Now |
> |---|---|
> | Production shape is unverified; no Sheet read and no Actor document read | **Both verified.** E-1 answered by the maintainer; E-2 satisfied by two real Actor exports read for structure. Twelve corrections resulted |
> | All seven ADRs are status **Proposed** | **All seven `Accepted`**, three amended first (0003, 0005, 0006) |
> | OD-34 and OD-35 await a maintainer ruling | **Both ruled.** ADR 0003 amended and unblocked |
> | ADR 0005 uses eighth-days (D-8) | **Thousandth-days.** Eighth-days withdrawn under OD-08 |
> | `foundry-mapping.md` §4 is a proposal (D-11) | **Verified.** Five paths were wrong (F-F1–F-F5) |
> | Fixtures: 26-line CSV, 147-line JSON, reconstructed headers | **Regenerated and validated** against the verified structure, plus a third anomaly fixture and `tests/test_fixtures.py` |
> | Test count 127 | **203** — 7 column W regression tests, 28 fixture-validation tests, 27 from the first Codex re-review's corrections, and 14 from the second's |
> | The column W fix of 2026-07-30 is complete | **It was not.** The Codex re-review found that it still accepted valid *fragments* while ignoring the rest, which was the same data loss in miniature, and that `/craft` could create a second identity for one tool. Both fixed 2026-07-30 — see [phase-0-handoff.md §4.8](../discovery/phase-0-handoff.md) |
> | …and neither was the fix to *that* | A **second** Codex re-review found a third path to the same loss: a duplicate or case-variant entry overwrote the earlier one at read time, so `"2.5 (Smith), 2.5 (SMITH)"` silently became 2.5. Fixed 2026-07-30 by consolidating duplicates — see [phase-0-handoff.md §4.9](../discovery/phase-0-handoff.md) |
> | "No real player data was accessed" (§10) | Accurate on 2026-07-29. **Not accurate afterwards:** two real Actor exports were read for structural verification. Nothing was committed, and both files are now outside the repository |
> | Phase 0 recorded as NOT complete | **All eight deliverables and all four acceptance criteria met.** The maintainer's half of the gate closed 2026-07-30; the independent Codex re-review is still open, so the gate itself is not closed |

Submitted for: **independent Codex review** at the Phase 0 review gate
(*architecture and data handling*, implementation plan §12)

Branch: `docs/platform-plan`

Date: 2026-07-29

Repository state at that date: nothing committed; all changes were working-tree changes

**Review outcome, 2026-07-29:** Codex review received. Full suite re-verified at
127 passed with the one pre-existing `audioop` warning; no files were changed by
the review. Two blocking findings (incomplete production-shape discovery; the
architecture gate still open) and two important findings (legacy untagged CRP,
ADR 0003's ID rationale) were raised. **Phase 0 was consequently recorded as NOT
complete at that point** — see
[phase-0-handoff.md](../discovery/phase-0-handoff.md), whose §1a registers the
sanitized evidence that was required, and OD-34 / OD-35 in
[open-decisions.md](../discovery/open-decisions.md). *All four findings have since
been resolved: the evidence was supplied on 2026-07-30 and both decisions were
ruled the same day.*

**Re-review outcome, 2026-07-30:** the Codex re-review of the 2026-07-30 state returned
two findings, both against the column W data-loss fix made that day, and **both are now
fixed**:

- **Blocking — partial CRP parsing and data loss.** The fix matched canonical pairs with
  `findall()`, so `"7.5 (Brewer), BROKEN"` was accepted as `{"brewer": 7.5}` and the next
  `/craft` rewrote the cell without `BROKEN`. Per-tool parsing is now all-or-nothing, and
  a cell that is not understood in full keeps its raw value and pins column W read-only.
- **Important — CRP identity when adding earned CRP.** `/craft` wrote `crp_dict` with the
  cleaned key while `get_tool_crp()` normalised both sides, so `"2.5 (Smith's Tools)"`
  gained a second `(Smith)` entry and the Master gate saw half the total. CRP mutation is
  now encapsulated in `Skills.add_tool_crp()`.

Suite after the corrections: **189 passed**, same one pre-existing `audioop` warning.
Detail in [phase-0-handoff.md §2e, §4.8 and §6b](../discovery/phase-0-handoff.md).
No Phase 1 work was begun.

**Second re-review outcome, 2026-07-30 (later).** This entry is **appended** to the one
above rather than replacing it: the first re-review's outcome stands as recorded, and
this is a further round against the state that resulted from it. The second Codex
re-review returned **one Blocking finding**, again on column W, and it **is now fixed**:

- **Blocking — a duplicate entry overwrote the earlier one.** `_parse_crp_cell()`
  lower-cased each tool name and assigned it straight into the dictionary, so
  `"2.5 (Smith), 2.5 (SMITH)"` read as `{"smith": 2.5}`; a `+2.5` award then saved
  `"5 (Smith)"` where the correct total is 7.5. The loss happened at read time, one
  layer below `add_tool_crp()`'s consolidation, and applied to the legacy and mixed
  notations too. Duplicate entries that differ only in case are now **summed** under
  the first spelling seen, keeping its position; names differing by more than case
  stay separate, so read-time identity does not depend on `_clean_tool_name()`'s
  first-word heuristic. A value that overflows `float()` to infinity is now unreadable
  rather than stored.

Suite after this correction: **203 passed**, same one pre-existing `audioop` warning
(189 → 203 is 14 new regression tests, all of which failed before the change). Detail
in [phase-0-handoff.md §2f, §4.9 and §6c](../discovery/phase-0-handoff.md) and
[sheet-inventory.md §3.2 F-S3c](../discovery/sheet-inventory.md). No Phase 1 work was
begun.

---

## 0. How this document is meant to be used

This is a **statement of what was done and why**. It deliberately does **not**
nominate focus areas, rank concerns by risk, or suggest where defects are likely.
Those would bias the review toward confirming the author's framing and away from
whatever the author missed, which defeats the purpose of an independent review.

What it does contain is factual disclosure that a reviewer needs in order to
judge the work fairly:

- the scope boundary, so in-scope and out-of-scope work are not confused;
- every decision taken, with its reasoning and the alternatives rejected;
- which statements are **verified observations** and which are **proposals or
  assumptions** — §8;
- what was deliberately left incomplete, and why — §9;
- exactly which checks were run, with their real output, and which were not — §6
  and §7.

Findings are expected to be classified per implementation plan §16.4 as
**Blocking**, **Important**, or **Optional**.

Note on the implementation plan: §16.3 lists *"proposed reviewer focus areas"* as
a required handoff field. That field is supplied in the maintainer-facing handoff
(`docs/discovery/phase-0-handoff.md` §10) but is **intentionally absent here**, at
the maintainer's instruction, so that this review is not steered. A reviewer who
wishes to remain unbiased should not read that section before forming their own
view.

---

## 1. Scope

### In scope

1. **Phase 0 — Discovery and architecture** (plan §12). A documentation and
   design milestone: eight required deliverables plus an unresolved-decision list
   and a milestone handoff.
2. **Five rule corrections**, authorised afterwards as an explicitly scoped task
   when the maintainer confirmed the mismatches found during discovery and ruled
   that the homebrew PDF is the leading rules document.
3. **One rule behaviour confirmed and documented**, not changed (§4.6).

### Out of scope, and not begun

Phase 1 and later remain behind this gate. Specifically **not** implemented:

- no web framework, HTTP route, template or static asset;
- no database schema, ORM model, migration or Alembic setup;
- no PostgreSQL instance, connection or configuration;
- no repository interfaces or database adapters;
- no Foundry connector, module or API;
- no authentication, session or authorization code;
- no changes to `.env`, `.env.example`, systemd units or any deployment file;
- no change to the Google Sheets adapter or its access pattern.

The seven ADRs in `docs/adr/` are all status **Proposed**. None authorises
implementation; approval of them is part of what this gate decides. *(All seven were
`Accepted` on 2026-07-30, three after amendment.)*

---

## 2. Documentation produced

All new. 21 files, ~4 300 lines. *Line counts are as of 2026-07-29 and have since grown;
the fixture rows in particular were regenerated on 2026-07-30.*

| Path | Lines | Content |
|---|---|---|
| `docs/discovery/README.md` | 63 | Index and provenance statement |
| `docs/discovery/command-inventory.md` | 409 | All 10 game commands + 6 music commands: read set, write set, domain entry point, rule citation, findings |
| `docs/discovery/sheet-inventory.md` | 276 | Reconstructed `Characters` tab contract, 38 columns, parse/serialise behaviour |
| `docs/discovery/foundry-mapping.md` | 282 | Deployment baseline, field mapping proposal, contested field groups |
| `docs/discovery/fixture-strategy.md` | 194 | Synthetic-fixture rules, reserved ID ranges, 26 coverage cases |
| `docs/discovery/open-decisions.md` | 415 | 36 decisions requiring maintainer input, with what each blocks (33 at submission; OD-34/OD-35 added by the review, OD-36 by the 2026-07-30 answers) |
| `docs/discovery/phase-0-handoff.md` | 395 | Maintainer-facing handoff per plan §16.3 |
| `docs/rules/rule-catalogue.md` | 636 | Every rule in the 42-page PDF, cited by section and page, with implementation status |
| `docs/rules/field-ownership.md` | 216 | Draft ownership matrix per plan §6.1 |
| `docs/operations/topology.md` | 272 | Observed production topology; proposed dev and staging |
| `docs/adr/0001`–`0007` + README | 919 | Architecture decisions, all **Proposed** |
| `tests/fixtures/README.md` | 55 | Fixture rules restated at point of use |
| `tests/fixtures/sheet_characters_sample.csv` | 26 | 22 synthetic character rows |
| `tests/fixtures/foundry_actor_sample.json` | 147 | Synthetic dnd5e 5.3.3 actor |

---

## 3. Code changed

```text
 ext/commands/craft.py          |   5 +-     RC-07 rationale comment only
 helpers/craft_calculator.py    |  12 +-     RC-06 fix + RC-07 rationale comment
 models/bastion.py              |   8 +-     RC-04 fix
 models/resource.py             |  18 +-     RC-02 and RC-03 fixes
 models/skills.py               |  66 +-     RC-09 fix + helper extraction
 tests/test_craft_calculator.py | 140 +      masterpiece, CRP table
 tests/test_resource.py         |  89 +-     earnings bands, natural 20, sale percentages
 tests/test_bastion.py          | new        facility table, maintenance, atomicity
 tests/test_skills.py           | new        CRP gate, one-Master limit, legacy CRP
```

Net: 306 insertions, 32 deletions across 7 tracked files, plus 2 new test modules.

Test count: **43 → 127**.

---

## 4. The five corrections

Each states the rule source, the previous behaviour, and the current behaviour, so
that correctness can be checked against the PDF directly rather than against the
author's reading of it.

### 4.1 RC-02 — natural-20 earning bonus (`/work`)

- **Source:** homebrew §6.6, PDF p.28.
- **Was:** `Money(base_gold * 150)`. `Money` is denominated in copper, so this is
  ×1.5 — a 50% bonus.
- **Now:** `Money(base_gold * 120)` — a 20% bonus.
- **Location:** `models/resource.py`, `Resource.earn_money()`.
- **Note:** the underlying band formula was not changed.

### 4.2 RC-03 — sale percentage floor (`/sale`)

- **Source:** homebrew §4.1, §4.1.1, §4.2.1, PDF p.11–12.
- **Was:** a single expression with no lower bound, so a negative Persuasion total
  produced a percentage below the 140% base.
- **Now:** the haggling contribution is clamped to `>= 0`; the expression was split
  into named steps (`haggling_bonus`, `own_shop_bonus`, `percent_over_cost`).
- **Location:** `models/resource.py`, `Resource.sale()`.
- **Note:** the restructuring changes no other behaviour — cap at 180% before the
  natural-20 bonus, maximum 190% — but it was not a purely mechanical edit, so it
  is a behaviour-preserving refactor bundled with a behaviour change in one commit.

### 4.3 RC-04 — special facility limits (`/bastion`)

- **Source:** homebrew §7.1, PDF p.29–30.
- **Was:** `MAX_SPECIAL_FACILITIES[((5, 8), 'aristocratic')] = 2`.
- **Now:** `3`. The other twelve cells were already correct.
- **Also changed:** `get_max_special_facilities()` returned `1` for an
  unrecognised lifestyle; it now returns `0`.
- **Location:** `models/bastion.py`.

### 4.4 RC-06 — masterpiece rarity (`/craft`)

- **Source:** homebrew §6.3.3.1, PDF p.17.
- **Was:** `is_masterpiece` required master level and non-consumable but did not
  constrain rarity.
- **Now:** additionally requires `rarity == "rare"`.
- **Location:** `helpers/craft_calculator.py`, `calculate_craft()`, step 3.
- **Ordering note:** step 3 runs before `is_legendary_project` is computed at
  step 6, so a legendary masterpiece is rejected before reaching the legendary
  roll-progression branch. Previously the two features interacted with no defined
  result.

### 4.5 RC-09 — Master rank prerequisite (`/learn`)

- **Source:** homebrew §6.3.3.1, PDF p.17.
- **Was:** the one-Master-tool limit was enforced; the 100-CRP prerequisite was
  not.
- **Now:** starting a Master project requires `Skills.MASTER_CRP_REQUIREMENT`
  (100) points for that tool, via a new `Skills.get_tool_crp()`.
- **Also changed:** the inline one-Master scan was extracted to
  `Skills._find_other_master_tool()` and is now called from two places — the
  original site (behaviour unchanged) and the new project-creation gate.
- **Location:** `models/skills.py`, `Skills.learn_proficiency()`.
- **Not implemented:** the tribute item required by the same section (craft an
  uncommon item and give it to the master free of charge). Nothing in the sheet
  records whether it happened, so enforcing it requires new persistent state.

### 4.6 RC-07 — CRP suppression: confirmed, not changed

`/craft` awards zero crafting reputation once the character holds a Master rank in
any tool (`has_master_tool`). Phase 0 flagged this as a behaviour with no cited
rule.

The maintainer confirmed it as correct, reasoning that §6.3.3.1 p.17 gives CRP a
single function — a master contacts the character at 100 points in a tool — and
the same section permits one Master rank for life, so once that rank is held no
further CRP can ever be used.

**No behaviour was changed.** Two explanatory comments were added
(`helpers/craft_calculator.py`, `ext/commands/craft.py`) and tests were added that
assert the behaviour, including one carrying a comment against "fixing" it from
the CRP table alone.

---

## 5. Decisions taken

Decisions where a different choice was defensible, with the reasoning used and the
alternatives rejected. Architecture decisions are in `docs/adr/`; this section
covers choices made during the work itself.

| # | Decision | Reasoning used | Alternatives rejected |
|---|---|---|---|
| D-1 | RC-09 gate applies at **project creation**, not per roll | The rule governs when a master agrees to teach; gating every roll would block characters already mid-lesson under the old code | Gate every roll; gate and cancel in-progress projects |
| D-2 | A legacy untagged CRP total (the `"general"` bucket) counts toward whichever tool is being learned | Sheets predating per-tool tracking would otherwise block those characters on a data-format artefact | Require per-tool CRP strictly; require Council migration first |
| D-3 | The one-Master check runs **before** the CRP check at project creation | A character already holding a Master rank would otherwise get a reputation message when the real reason is the one-Master limit | Leave the original ordering |
| D-4 | Unknown lifestyle → `0` special facilities | Wretched and modest are 0 at every level; an unknown value is a data error. Matches the existing convention of treating an unparseable lifestyle as modest (`LIFESTYLE_COSTS.get(..., 7)`) | Keep `1`; raise an exception |
| D-5 | RC-03 restructured into named steps rather than minimally patched | The original single expression made the cap/natural-20 ordering hard to verify against the PDF | Insert `max(..., 0)` into the existing expression |
| D-6 | `_find_other_master_tool()` extracted rather than duplicated | Two call sites needed the same scan | Duplicate the loop; inline at the new site only |
| D-7 | Fixtures are **synthetic by construction**, never anonymised exports | A scrubbed row keeps its shape, and a distinctive shape identifies a player in a community this size | Export and scrub; commit an anonymised sample |
| D-8 | Downtime smallest unit proposed as **eighth-days** (ADR 0005) | `BREW_TABLE[(0, False)]["m"] = 0.125` (§6.5.4.2 p.27) is the finest step in any table | Quarter-days; `NUMERIC`; `Decimal` |
| D-9 | Money as integer copper, single `BIGINT` (ADR 0005) | `.agents/AGENTS.md` requires it; collapses `Resource.deduct()`'s recursive carry logic | Four denomination columns; `Decimal`; `NUMERIC` |
| D-10 | Application-generated UUID keys (ADR 0003) | Import idempotency is far simpler when the importer can compute an ID before writing | `bigserial`; natural keys |
| D-11 | Foundry Actor documents **not** read | No maintainer authorisation was given, the databases are held open by running servers, and every Actor is player data | Read an offline snapshot |
| D-12 | Field ownership defaults to **database-owned** when unlisted (ADR 0007) | An unlisted field is an unanalysed field; the safe failure mode is to leave it alone | Default to Foundry-owned; require exhaustive listing |
| D-13 | Documentation updated in place when the corrections landed | Documents describing the corrections as unfixed would misinform this review | Leave Phase 0 docs frozen and note changes only here |

---

## 6. Verification performed

Exact commands and their real output, **as run on 2026-07-29**. The suite has grown to
162 tests since; current results are in
[phase-0-handoff.md §6](../discovery/phase-0-handoff.md#6-commands-run-and-exact-results).

| Command | Result |
|---|---|
| `./venv/bin/python -m pytest -q` (before any change) | `43 passed, 1 warning` |
| `./venv/bin/python -m pytest -q` (current) | `127 passed, 1 warning` |
| `./venv/bin/python -m pytest -q` ×5 consecutive | `127 passed` each time — no flakiness from patched dice |
| `./venv/bin/python -m pytest -q --collect-only` | `127 tests collected` |
| `git status --short` | 7 modified tracked files, 7 untracked paths |
| `git diff --stat` | 306 insertions, 32 deletions |

The single warning is pre-existing and unrelated: `discord/player.py:29` imports
`audioop`, which is deprecated and slated for removal in Python 3.13. The
deployment runs Python 3.12.3, so this is a forward-looking deprecation rather
than a current failure — but it does mean the music extension will break on a
Python 3.13 upgrade.

### Independent numeric re-verification

Run outside the test suite, against the PDF tables directly:

- **RC-02** — all five earnings bands computed at both boundaries; every
  natural-20 result is exactly ×1.20 of its base, and every value is integral in
  copper (840 / 1 680 / 3 360 / 6 720 / 13 440), so no rounding is involved.
- **RC-04** — all twelve populated cells of the §7.1 p.29 table compared against
  `MAX_SPECIAL_FACILITIES`: 12/12 match.
- **RC-03** — both PDF worked examples reproduced: p.11 (375 GP crafting cost,
  Persuasion 15 → 581.25 GP at 155%) and p.12 (25 GP greatsword, natural 20, shop
  owner → 47 GP 5 SP at 190%).
- **Fixture** — `sheet_characters_sample.csv` parsed with `csv`: 38 columns, 24
  records, no row-width mismatch, and every column letter aligns with
  `Actor.COLUMNS`.
- **Fixture** — `foundry_actor_sample.json` parsed with `json`: valid, 7 items.

### Secret and data scans

- `grep -rInE '(DISCORD_TOKEN|private_key|BEGIN.*PRIVATE KEY|client_secret|password[:=])'` over `docs/`, `tests/`, `models/`, `helpers/` — one hit, a documentation reference to `.gitignore`'s contents. No secret.
- `grep -rnoE '[0-9]{15,20}'` over new files — only synthetic IDs inside the reserved ranges declared in `fixture-strategy.md` §3.

---

## 7. Verification **not** performed

| Check | Why not |
|---|---|
| Formatter | None configured in the repository |
| Linter | None configured |
| Type checker | None configured |
| Database / migration tests | No database exists; Phase 1 |
| Foundry contract tests | No connector exists; Phase 7 |
| Discord command tests | No test doubles for Pycord interactions exist yet |
| Live behaviour of any changed command | Would require running against production Discord and the live Sheet |

`requirements-dev.txt` contains only `pytest`. Adding a formatter, linter and type
checker is called for by `.agents/AGENTS.md` and was **not** done, because Phase 0
is a documentation milestone and introducing tooling would have exceeded its scope.

No changed command was executed end to end. The corrections are covered by unit
tests at the domain level only; the cog layer that calls them is untested, as it
was before.

---

## 8. Provenance of claims

*As of 2026-07-29. Every item in "Proposals, not observations" and "Assumptions stated
as such" below was verified or answered on 2026-07-30 — see the table at the top of this
document.*

Which statements in the documentation are observations and which are not. This
distinction matters because several documents read as authoritative but are
partly inference.

### Verified by direct observation

- All source, test and configuration content in the repository.
- The homebrew rules PDF: 42 pages, extracted and read in full. All section and
  page citations were taken from that text.
- Foundry deployment baseline — read from `world.json` and `system.json`
  **manifests** only: world `the-guild`, title `The Guild`, core `14.365`, system
  `dnd5e` `5.3.3`, system compatibility minimum `13.347` / verified `14`.
- Three Foundry instances exist on this host (ports 30001–30003), each containing
  a world directory named `the-guild`.
- Caddy reverse-proxy configuration, listening sockets, and the two systemd unit
  templates in `infra/systemd/`.

### Proposals, not observations

- **`foundry-mapping.md` §4, the entire field mapping.** Derived from the
  documented `dnd5e` data model and from what the rules and the sheet require. No
  Actor document was read (D-11). The document says so in place.
- **`sheet-inventory.md` §4, formula hypotheses.** Reads use
  `UNFORMATTED_VALUE`, so no spreadsheet formula is visible to the code. Which
  columns carry formulas is unknown and is recorded as OD-07.
- **All seven ADRs.** Status **Proposed**.
- **`field-ownership.md`.** A draft with seven groups explicitly UNRESOLVED.

### Assumptions stated as such

- Rows 1–2 of the `Characters` tab are headers, inferred solely from reads
  starting at `A3`. The real header text is unknown.
- The purpose of eleven columns (B, C, O, U, AD–AJ) is unknown (OD-02).
- The `Characters (active)` Actor folder name is carried from the implementation
  plan and was **not** confirmed, as confirming it would require reading world
  data.
- The historical-impact assessments for RC-02 and RC-04 are the maintainer's
  judgement about community usage, not verified fact. Recorded as such in OD-10.

---

## 9. Deliberately incomplete

Known gaps as of 2026-07-29, left open on purpose rather than overlooked. **The first
three closed on 2026-07-30**; the rest stand.

| Item | Reason |
|---|---|
| ~~Verified production shape for the Sheet and Foundry~~ **CLOSED 2026-07-30** | Was: deliberately never observed. E-1 was answered by the maintainer and E-2 satisfied by two real Actor exports read for structure only. Still true that no live Sheet was read and no world database was opened |
| ~~Legacy untagged CRP vs the per-tool Master gate (OD-34)~~ **RULED 2026-07-30** | Resolved once by hand at import, not by a code policy; current behaviour stays |
| ~~Import idempotency and ID generation (OD-35)~~ **RULED 2026-07-30** | ID assigned at row creation, never derived; ADR 0003 amended and accepted |
| RC-09 tribute item (craft a free uncommon item for the master) | Nothing in the sheet records it; needs new persistent state — Phase 5 |
| `crp = "Master"` wipes per-tool CRP on completion | A data-model defect; fixing it changes what column W stores — Phase 5 |
| Bastion loss rules (RC-G1: twelve missed LC; dropping below a qualifying lifestyle) | Not a mismatch — an unimplemented rule. Interacts with D-4 |
| Natural-1 consequence table (§6.6 p.28–29) | Unimplemented rule, not in the correction scope |
| Aristocratic one-year lock-out (§5.5 p.13) | Unimplemented rule |
| Frank the Money Lender (§5.6 p.14) | Unimplemented rule; `Actor.debt` and column AC are dead |
| Crafting assistants (§6.5.3 p.25–26) | Unimplemented rule |
| Float arithmetic in `Resource.sale()` | Violates the money rule in `.agents/AGENTS.md`; fixing it is a representation change belonging to Phase 4/5, not a rule correction |
| No authorization on any bot command | Pre-existing; Phases 3 and 5 |
| No idempotency on any mutation | Pre-existing; Phases 4 and 5 |
| 26-cell whole-row write on every save | Pre-existing; the primary motivation for Phase 1 |
| Formatter, linter, type checker | §7 |

---

## 10. Constraints observed

Stated so that any breach is checkable. **As of 2026-07-29.** One item changed the next
day and is flagged in place: two real Actor exports were read for structural
verification, with the maintainer supplying them for that purpose.

- No live service was contacted, mutated, restarted or reconfigured — Discord,
  Google Sheets, Foundry, Lavalink, Caddy, systemd.
- No credential was read: not `.env`, not `yt-cookies.txt`, not service-account
  material.
- No live Google Sheet was read. `sheet-inventory.md` is reconstructed entirely
  from source code.
- No Foundry world data was read (D-11). *Still true: the world databases were never
  opened. But on 2026-07-30 the maintainer supplied two Actor **exports**, which were
  read for structure — see the table at the top of this document.*
- No real player data was accessed or committed. *The "committed" half still holds
  without exception. The "accessed" half was accurate on 2026-07-29 and stopped being
  accurate on 2026-07-30; the current, accurate statement is in
  [phase-0-handoff.md §5](../discovery/phase-0-handoff.md#5-security-and-privacy-implications).*
- No production code was modified during Phase 0 itself. The five corrections were
  made only **after** the maintainer confirmed the mismatches and ruled that the
  PDF governs.
- The Phase 0 review gate was not crossed: no Phase 1 work was begun (§1).

---

## 11. Repository state

*As of 2026-07-29.* Nothing was committed; all changes were working-tree changes on
`docs/platform-plan`. Nothing has been committed since either, but the working tree has
grown — `docs/review/`, `tests/test_fixtures.py`, `tests/fixtures/foundry_actor_anomalies.json`
and a one-rule `.gitignore` change. The current listing is in
[phase-0-handoff.md §2](../discovery/phase-0-handoff.md#2-files-changed).

```text
 M ext/commands/craft.py
 M helpers/craft_calculator.py
 M models/bastion.py
 M models/resource.py
 M models/skills.py
 M tests/test_craft_calculator.py
 M tests/test_resource.py
?? docs/adr/
?? docs/discovery/
?? docs/operations/
?? docs/review/
?? docs/rules/
?? tests/fixtures/
?? tests/test_bastion.py
?? tests/test_skills.py
```

`docs/implementation-plan.md` is tracked and **unmodified**.

---

## 12. Source material for the review

| Subject | Where |
|---|---|
| Milestone contract and acceptance criteria | `docs/implementation-plan.md` §12 (Phase 0) |
| Working agreement | `.agents/AGENTS.md` |
| Rules authority | `Freedom Blades - Homebrew Rules.pdf` (42 pages) |
| Rule citations and status | `docs/rules/rule-catalogue.md` |
| Command behaviour | `docs/discovery/command-inventory.md` |
| Sheet contract | `docs/discovery/sheet-inventory.md` |
| Architecture decisions | `docs/adr/0001`–`0007` |
| Open decisions | `docs/discovery/open-decisions.md` |

The PDF is the authority for every rule claim in this submission. Section and page
references are given throughout so each can be checked against it directly rather
than against this document.
