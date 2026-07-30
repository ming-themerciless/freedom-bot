# Phase 0 Milestone Handoff

Status: **Accepted 2026-07-30.** All eight Phase 0 deliverables are complete and
all four acceptance criteria are met. The maintainer accepted ADRs 0001–0007,
the independent Codex re-review approved the architecture and data handling,
and the maintainer accepted the milestone. The gate is closed.

- **ADRs 0001–0007 are `Accepted`.** They are now the contract Phase 1 is reviewed
  against; changing one means superseding it, not editing it.
- **Both production-shape deliverables are verified**, not inferred — the Sheet
  inventory from the maintainer's own description of all 38 columns plus the player
  tab, and the Foundry mapping against two real Actor exports.
- That verification produced **twelve corrections** to Phase 0's conclusions and
  uncovered one **live data-loss defect**, now fixed (§4.6).
- **The fixtures were regenerated against the verified structure** and are now
  validated by `tests/test_fixtures.py` (§2d).
- **The two Actor exports have been moved out of the repository** and are covered by
  a narrow `.gitignore` rule (§7). Neither was ever committed.
- **The Codex re-review returned two findings on the column W work, and both are
  fixed** — one **Blocking** (a partial CRP parse could still overwrite the rest of
  the cell) and one **Important** (an award could create a second identity for the
  same tool). See **§4.8**; verification in **§6b**.
- **A second Codex re-review returned one further Blocking finding on the same
  cell, and it is fixed** — a duplicate or case-variant entry overwrote the
  earlier one, discarding its CRP before `add_tool_crp()` could consolidate it.
  Duplicates are now summed at read time. See **§4.9**; verification in **§6c**.
  Suite: **203 passed**.

Five rule mismatches were corrected earlier under the maintainer ruling of 2026-07-29
(§2b).

**Phase 1 was authorized on 2026-07-30 after Codex approval and final maintainer
acceptance.** This handoff records the pre-Phase-1 baseline.

Review gate: *architecture and data handling* (plan §12 Phase 0)

Reviewers required: maintainer (ADR approval) and Codex (plan §16.4 —
*"architecture and initial schema"*)

Branch: `docs/platform-plan`

Reported per plan §16.3.

---

## 1. Requirements implemented

Phase 0 is a discovery and design milestone. All eight required deliverables are
written and submitted. After the maintainer answers of 2026-07-30, **all eight are
complete or verified.** The two that described production shape are now checked against
real evidence rather than inferred, and that checking produced **twelve** corrections
(F-S1–F-S7, F-F1–F-F5) and one live defect fix.

| Plan §12 deliverable | Document | Status |
|---|---|---|
| Sheet schema/formula inventory | `docs/discovery/sheet-inventory.md` | **VERIFIED 2026-07-30** against the maintainer's own description. All 38 real headers, the 11 unknown columns, the formula answer and the real CRP format are recorded. Seven findings (F-S1–F-S7), one of them a live data-loss defect now fixed. OD-01 is closed: scope is `Characters` plus the player tab, whose eight headers were supplied |
| Command/use-case inventory | `docs/discovery/command-inventory.md` | Complete — all 10 game commands + 6 music commands |
| Foundry field samples and mapping | `docs/discovery/foundry-mapping.md` | **VERIFIED 2026-07-30** against two real Actor exports. Five corrections (F-F1–F-F5), including that Foundry models Bastions natively and that the tool vocabularies already agree |
| Rule catalogue with PDF references | `docs/rules/rule-catalogue.md` | Complete — 42 PDF pages catalogued |
| Field-ownership draft | `docs/rules/field-ownership.md` | Complete as a **draft**, 7 groups UNRESOLVED (as the plan intends at this stage) |
| Initial ADRs | `docs/adr/0001`–`0007` | **All `Accepted` 2026-07-30.** Three were amended first — 0003 (identifiers), 0005 (thousandth-days), 0006 (one shared world) |
| Anonymized fixtures | `docs/discovery/fixture-strategy.md`, `tests/fixtures/` | **Complete 2026-07-30.** Strategy plus three validated fixtures: the Sheet CSV regenerated against the real 38 headers and the canonical CRP format, the Foundry actor rewritten to the verified export shape (F-F1–F-F5), and a new anomaly actor for the two must-fail cases. `tests/test_fixtures.py` (28 tests) fails if a fixture and the documentation disagree — see §2d |
| Local/staging topology | `docs/operations/topology.md` | Complete, with 5 findings |
| Unresolved decisions (acceptance criterion) | `docs/discovery/open-decisions.md` | 36 decisions; **16 closed** by maintainer answers over 2026-07-29/30 |
| Milestone handoff (§16.3) | this document | — |

### Acceptance criteria

| Criterion | Result |
|---|---|
| Every current bot command has known reads, writes, and rule sources | **Met.** All 10 game commands documented with read set, write set, domain entry point and PDF citation |
| No secrets or real player records are committed | **Met.** Nothing is committed at all, and the working tree now contains no real player record: the two Actor exports were moved out of the repository and are ignored by pattern. All fixtures are synthetic by construction. See §5 |
| Unresolved ownership questions are listed explicitly | **Met.** `open-decisions.md`, plus `field-ownership.md` §10 |
| Maintainer approves architecture ADRs | **MET 2026-07-30.** All seven `Accepted`, three after amendment |

**All four criteria are met, and both required approvals are recorded.** The
independent Codex re-review approved the architecture and data handling, the
maintainer accepted Phase 0, and the gate is closed.

### 1a. Evidence register — what closes each provisional deliverable

None of this can be obtained safely by an agent. It requires a maintainer acting
on their own machine, and the output committed here is **structural metadata, not
data**.

| ID | Evidence | Closes | Blocks | Detail |
|---|---|---|---|---|
| **E-1** | ~~Sheet structural questionnaire~~ | ~~`sheet-inventory.md`~~ | ~~Phase 2~~ | **SATISFIED 2026-07-30.** The maintainer supplied all 38 headers, the eleven unknown columns, the formula answer (none — but three macros), the real CRP format and the row count, and in a later round the player tab's eight headers. Recorded in [sheet-inventory.md](sheet-inventory.md). [OD-01](open-decisions.md) is closed |
| **E-2** | ~~Actor export validating the §4.2 field paths~~ | ~~`foundry-mapping.md` §4~~ | ~~Phase 2, Phase 7~~ | **SATISFIED 2026-07-30.** Two real actors supplied and verified; five corrections resulted (F-F1–F-F5) — see §4.7. OD-30 closed |

**Both evidence items are now satisfied.** Every one of E-2's five original questions
is answered: the authoritative-instance question dissolved (one shared world, §4.4),
the `Characters (active)` folder is confirmed, no actor holds electrum (`ep: 0` on
both), the version range is pinned, and the field paths are verified against real
documents.

One repository rule was applied to E-2, and it is hygiene rather than privacy: per
`.agents/AGENTS.md`, **committed test fixtures are synthetic by construction.** The two
exports were read to verify field paths and the fixture was rewritten by hand to match
the verified shape. **Neither export was ever committed.** They arrived inside `docs/`
and have now been **moved** — not deleted, since they were the only copies — to
`/opt/discord-bots/foundry-actor-exports/`, outside the repository. `.gitignore` carries
a narrow `fvtt-Actor-*.json` rule so a future export cannot be staged by accident (§7).

The maintainer has confirmed the game data is fictional characters rather than personal
information, so the anonymisation ceremony originally proposed here was unnecessary. The
one genuine exception is `Characters` column **C**, which holds real player names and
stays out of fixtures.

**No production-shape deliverable is provisional any more.**

---

## 2. Files changed

### 2a. Phase 0 documentation (new files)

```text
docs/adr/README.md
docs/adr/0001-develop-platform-in-existing-repository.md
docs/adr/0002-web-application-stack.md
docs/adr/0003-postgresql-and-alembic.md
docs/adr/0004-discord-oauth2-authentication.md
docs/adr/0005-identifier-and-quantity-representation.md
docs/adr/0006-foundry-integration-boundary.md
docs/adr/0007-field-ownership-and-conflict-policy.md
docs/discovery/README.md
docs/discovery/command-inventory.md
docs/discovery/sheet-inventory.md
docs/discovery/foundry-mapping.md
docs/discovery/fixture-strategy.md
docs/discovery/open-decisions.md
docs/discovery/phase-0-handoff.md
docs/operations/topology.md
docs/rules/rule-catalogue.md
docs/rules/field-ownership.md
tests/fixtures/README.md
tests/fixtures/sheet_characters_sample.csv
tests/fixtures/foundry_actor_sample.json
tests/fixtures/foundry_actor_anomalies.json
tests/test_fixtures.py
```

One tracked file was modified as part of the same hygiene work:

```text
.gitignore                        narrow `fvtt-Actor-*.json` rule (§7)
```

### 2b. Rule corrections (2026-07-29 maintainer ruling)

After Phase 0 was delivered, the maintainer confirmed all five rule mismatches
and ruled that **the PDF is the leading rules document**. The corrections were
implemented as an explicitly scoped follow-up task — **not** as entry into
Phase 1, which remains behind this gate.

```text
helpers/craft_calculator.py       RC-06  masterpiece must be rare
                                  RC-07  rationale comment (behaviour unchanged)
ext/commands/craft.py             RC-07  rationale comment (behaviour unchanged)
models/bastion.py                 RC-04  5-8 aristocratic 2 -> 3; unknown default 1 -> 0
models/resource.py                RC-02  natural-20 earnings +50% -> +20%
                                  RC-03  140% sale floor
models/skills.py                  RC-09  100-CRP gate before Master lessons
tests/test_bastion.py       (new)        full facility table + maintenance
tests/test_skills.py        (new)        CRP gate, one-Master limit, legacy CRP
tests/test_craft_calculator.py           masterpiece rarity and cost; CRP table
tests/test_resource.py                   earnings bands, natural 20, sale percentages
```

### 2c. Column W data-loss fix (2026-07-30)

A separate, **pre-existing** defect, found when the maintainer stated column W's
real format. Not a rule change — a data-integrity repair. See §4.6.

```text
models/skills.py                  parse canonical "7.5 (Brewer)" form
                                  write the canonical form back on save
tests/test_skills.py              7 regression tests: both formats, comma
                                  decimals, "Master", accumulation, the gate,
                                  and the abbreviation hazard (pinned as-is)
```

### 2d. Fixture completion (2026-07-30)

The fixtures were the one deliverable still carrying an "update this later" note. That
note is resolved inside Phase 0 rather than deferred, because the structure they had to
match was now verified and completing them needs no production data.

```text
tests/fixtures/sheet_characters_sample.csv   regenerated: the real 38 headers, the
                                             canonical `7.5 (Brewer)` CRP form, the
                                             legacy colon form kept alongside it, the
                                             ten formerly-unknown columns populated,
                                             downtime precision case revised to
                                             thousandth-days
tests/fixtures/foundry_actor_sample.json     rewritten to the verified export shape:
                                             `"_id": null` (F-F1), derived values
                                             absent (F-F2), `system.tools` keyed by
                                             artisan with the three aliases (F-F3),
                                             `system.bastion` plus three facility
                                             items incl. a homebrew one (F-F4)
tests/fixtures/foundry_actor_anomalies.json  new: nonzero electrum and an unsupported
                                             (core, system) tuple — the two cases that
                                             must fail rather than import
tests/test_fixtures.py                (new)  28 tests pinning all three to the verified
                                             documentation, incl. column-letter
                                             alignment with `Actor.COLUMNS` and the
                                             column W formats parsed through the real
                                             adapter code path
models/skills.py                             comment only: OD-34 recorded as ruled
                                             rather than awaiting a ruling. Behaviour
                                             and tests unchanged
```

`tests/test_fixtures.py` reads `Actor.COLUMNS` out of `models/actor.py` with `ast`
instead of importing it, because importing `models.actor` pulls in `config`, which reads
`.env`. No test in this repository may touch credentials.

**What is still not verified** is narrower than the deliverable: the ten unmapped columns
now have known *meanings* but their *value formats* were described rather than observed,
and the free-text columns V, X, Y, Z and AA have not been surveyed the way column W was.
Both are recorded in `tests/fixtures/README.md` and neither affects a column the platform
parses today.

### 2e. Codex re-review corrections (2026-07-30, later)

The two findings the Codex re-review raised against the §2c column W work. Both
concern the same cell and are described in **§4.8**. No other behaviour was touched,
and nothing here begins Phase 1.

```text
models/skills.py                  BLOCKING: per-tool parsing is all-or-nothing
                                  (`_parse_crp_cell()`); a cell that is not
                                  understood in full keeps its raw value, sets
                                  `crp_unparsed`, and pins column W read-only in
                                  `get_sheet_data()`; `get_summary()` says the value
                                  is unreadable instead of showing a number
                                  IMPORTANT: `add_tool_crp()` encapsulates CRP
                                  mutation using `get_tool_crp()`'s normalisation,
                                  folds duplicate spellings into one entry, and
                                  validates the numbers
ext/commands/craft.py             calls `add_tool_crp()` instead of mutating
                                  `crp_dict`; refuses the craft before any deduction
                                  when an award cannot be recorded safely
tests/test_skills.py              27 new regression tests (44 in the file): the full
                                  canonical multi-tool cell, comma decimals,
                                  malformed text after and between valid pairs, a
                                  malformed legacy fragment, the proof that malformed
                                  input cannot be rewritten as a truncated valid
                                  cell, mixed notations, and accumulation on `Smith`,
                                  `Smith's Tools`, capitalisation variants and the
                                  canonical parsed representation
```

Documentation updated in the same round:

```text
docs/discovery/phase-0-handoff.md    this section, §4.8, §6b, §8, §9, §10, §11
docs/discovery/sheet-inventory.md    §3.2: F-S3a, F-S3b, and the accepted-encodings
                                     table (two encodings added, the "anything else"
                                     row now says column W is not written at all)
docs/discovery/command-inventory.md  `/craft`: the identity correction and the new
                                     pre-deduction refusal path
docs/discovery/open-decisions.md     OD-06 (the write half of tool identity is now
                                     closed), OD-34 (the shadowing consequence of the
                                     hand-assignment ruling)
docs/review/phase-0-submission.md    the re-review outcome, in the superseded-facts
                                     block at the top; the 2026-07-29 record itself is
                                     left unrewritten
```

### 2f. Second Codex re-review correction (2026-07-30, later still)

The one **Blocking** finding the second Codex re-review raised, again against
column W and again the same class of loss as §4.6 and §4.8. Described in **§4.9**.
No other behaviour was touched, and nothing here begins Phase 1.

```text
models/skills.py                  BLOCKING: `_parse_crp_cell()` summed duplicate
                                  entries instead of overwriting them. Two
                                  fragments naming the same tool (identical, or
                                  differing only in case, in either notation or a
                                  mix of them) are consolidated under the first
                                  spelling seen, keeping its position. A value long
                                  enough to overflow `float()` to infinity is now
                                  unreadable rather than stored as `inf`
tests/test_skills.py              14 new regression tests (58 in the file): the
                                  five required duplicate shapes, first-spelling
                                  and position determinism, the complete read ->
                                  award -> serialisation path, the proof that
                                  consolidation triggers no write of its own,
                                  distinct and merely-equivalent names staying
                                  separate, a duplicate beside malformed text, and
                                  three overflow cases
```

Documentation updated in the same round:

```text
docs/discovery/phase-0-handoff.md    this section, the status header, §4.9, §6c,
                                     §8, §9, §10, §11
docs/discovery/sheet-inventory.md    §3.2: F-S3c, the F-S3 summary line, and four
                                     new rows in the accepted-encodings table
docs/review/phase-0-submission.md    the second re-review outcome, appended below
                                     the first; neither the 2026-07-29 record nor
                                     the first re-review's entry is rewritten
```

`ext/commands/craft.py` was **not** changed in this round: it already goes through
`add_tool_crp()`, which is where the consolidated value lands.

Nothing is committed. Commit is left to the maintainer.

## 3. Migrations added

**None.** Phase 0 does not touch the database. The first migration belongs to
Phase 1, after this gate.

---

## 4. Principal findings

**The most important one is §4.6**, found on 2026-07-30: the bot has been
destroying crafting reputation data on every `/craft`. It is fixed. Read that
first, then **§4.8** — the Codex re-review found that the first fix still admitted a
narrower version of the same data loss, and that a second defect in the same cell
could split one tool's reputation across two entries — and then **§4.9**, where the
second re-review found a fourth instance of the same mechanism: a duplicate entry
overwriting the earlier one at read time. All four are fixed.

### 4.1 Rule mismatches — five, all now corrected

Full detail and page citations in `docs/rules/rule-catalogue.md`.

| ID | Command | Was | Now — per PDF |
|---|---|---|---|
| **RC-02** | `/work` | natural-20 bonus **+50%** | **+20%** (§6.6 p.28) |
| **RC-04** | `/bastion` | levels 5–8 aristocratic → **2** facilities | **3** (§7.1 p.29) |
| **RC-06** | `/craft` | masterpiece any rarity | **rare only** (§6.3.3.1 p.17) |
| **RC-03** | `/sale` | no 140% floor | **140% floor** (§4.2.1 p.12) |
| **RC-09** | `/learn` | no Master prerequisite | **100 CRP for that tool** (§6.3.3.1 p.17) |

Phase 0 delivered these as findings and changed nothing. The maintainer then
confirmed all five and ruled that the PDF governs, so they were corrected — see
§2b and §6.

**Also resolved on the same day:**

- **RC-07** — `/craft` suppressing all CRP once any tool is mastered was
  **confirmed correct**. It derives from the one-Master rule: §6.3.3.1 p.17 gives
  CRP a single purpose (a master contacts you at 100 points) and permits one
  Master rank for life, so once that rank is held further CRP can never be spent.
  The rationale is now recorded in the code and locked in by tests (OD-29 closed).
- **No historical impact, no announcement.** The maintainer confirms no character
  has ever held an aristocratic lifestyle below level 9, so RC-04's incorrect cell
  was never reached; and assesses that a natural 20 on `/work` has almost
  certainly never occurred, as the command sees little use. No player's recorded
  state was affected by either error (OD-10, OD-11 closed).

**Still open:**

- **RC-09 tribute item** — crafting a free uncommon item for the master is not
  tracked anywhere in the sheet, so enforcing it needs new state (Phase 5, OD-28).
- **`crp = "Master"` wipes per-tool CRP** on completion — a data-model defect that
  changes what column W stores, so it belongs with the Phase 5 `/learn` migration.

**The rest of the rules implementation is accurate.** Every crafting table
(poisons ×16, scrolls/tattoos ×10 levels, brews ×7, non-consumables, consumables),
the mining result table, the earnings bands, the lifestyle costs, the learning
costs and the sale percentage cap were compared cell by cell against the PDF and
match.

### 4.2 Data-integrity risk in the current Sheets adapter

`Actor.sheet_updates()` (`models/actor.py:101`) writes **26 cells on every save**,
regardless of what changed. A `/mine` that alters only Moradinium and downtime
also rewrites badge, level, mission count, last-played and no-shows with their
load-time values.

The load happens before the dice roll and the save after. Any Guild Council edit
to those cells inside that window is silently lost.

Two further round-trip losses share the mechanism: notable items lose their
description, benefits and link (`models/item.py:68`), and the free-text skill,
proficiency, language and progress columns are re-serialised to the parser's
canonical form on every save.

This is the strongest single argument for the Phase 1 database foundation.

### 4.3 No authorization

No command verifies that the invoking Discord user may act for the named
character. Channel-ID checks are the only gate. `/sale` is the sole exception and
matches a Discord role by **name**, which `.agents/AGENTS.md` forbids.

`/info` additionally has no channel restriction and replies non-ephemerally, so
any guild member can read any character's full financial state from any channel.

How long this may persist is OD-17. The recommendation is to back-port a
`character_access` check to the bot as soon as that table is populated in Phase 3,
rather than waiting for each command's Phase 5 migration.

### 4.4 Three Foundry instances, one shared world — **finding corrected 2026-07-30**

Three instances run on this host (ports 30001–30003), which the plan did not
anticipate; it speaks of "the deployed Foundry" in the singular.

Phase 0 originally reported this as **three separate `the-guild` worlds** and
called choosing between them a blocker, on the reasoning that importing from the
wrong one would yield a plausible-looking but stale copy of every character.

**That was wrong, and the maintainer corrected it.** `/home/foundry/shared/worlds`
is bind-mounted onto each instance's `foundrydata/Data/worlds`: one world
directory, seen three times. Verified — all three paths to `the-guild` resolve to
**inode 4388511 on device 64769**, with the binds declared in `/etc/fstab`.

The correction *simplifies* the design rather than complicating it: the world is
the identity, an instance is a transport endpoint, `external_worlds` keys on world
ID alone, and one service principal suffices. OD-12 is closed without a choice
being made. ADR 0006 and `foundry-mapping.md` §3 are updated; the withdrawn
alternative is kept in ADR 0006 with its reasoning, since only the premise was
wrong.

**Two things the correction does not remove:**

1. **Version validation still matters.** The Foundry binary and the `systems/` tree
   are per-instance (`/home/foundry/dist/foundryN/`), so one instance can be
   upgraded against the shared world while the others are not. All three run core
   `14.365` / `dnd5e` `5.3.3` today; they are independently upgradable tomorrow.
2. **New constraint — LevelDB is single-writer.** Only one instance can host
   `the-guild` at a time; the exclusive lock makes a second launch fail cleanly
   rather than corrupt anything (local ext4, so the lock is effective). The
   connector's endpoint must therefore be repointable by configuration and must not
   assume port 30001. Recorded as topology **F-2a**.

**This is the clearest evidence for why §1a exists.** A confidently-reasoned
finding, correctly derived from what was observable, was wrong because the premise
could not be verified without asking. The same risk applies to every unverified
statement in `sheet-inventory.md`.

The plan's stated baseline was otherwise **confirmed exactly** from the manifests:
world `the-guild`, title `The Guild`, core `14.365`, system `dnd5e` `5.3.3`.

### 4.5 The Phase 2 blocker — **resolved 2026-07-30, and it is the good answer**

Phase 0 could not see whether bot-written columns held formulas, because
`UNFORMATTED_VALUE` returns computed results. Badge, level, living weeks and
downtime all looked like natural formula candidates, which raised the possibility
that the 26-cell whole-row write had already destroyed them.

**The maintainer's answer: there are no formulas in the sheet at all.** Every
hypothesis in the original §4 of `sheet-inventory.md` was wrong. **Phase 2 is a
migration, not a repair.**

**But the accrual is real, and it runs as three timed Apps Script macros:** `+1`
week to `J` weekly; `+5` downtime days when living cost is paid (which the bot now
also does); and Frank's interest on `AC`. The weekly `+1` had never been documented
anywhere.

Three consequences:

1. **The sheet has a third writer.** Every concurrency statement in Phase 0 assumed
   two — bot and Council. The macros run on a timer and coordinate with nothing.
2. **The whole-row write now has an automated trigger, not a hypothetical one.** A
   save rewrites `J` from its load-time value, so an accrual firing inside a
   command's read→write window is silently reverted and that week's living cost is
   lost. Same mechanism for `AC`.
3. ~~A possible double grant of downtime.~~ **Checked and cleared 2026-07-30:** the
   downtime macro is **switched off**, so the bot alone grants the `+5` days and
   nothing is double-counted. **Two macros remain active** — the weekly `+1` to `J`
   and Frank's interest on `AC`.

The macros are not in this repository and are not version-controlled. Their fate at
cutover is **OD-36**; the recommendation is to reimplement the accrual in the
platform as a scheduled, audited, idempotent job, but not to disable anything until
the replacement is running and reconciled. Worth checking separately whether the
macro source is backed up anywhere — it currently holds live game rules as a single
point of failure.

### 4.6 Column W was silently destroying CRP data on every `/craft` — **fixed**

Found 2026-07-30, immediately after the maintainer stated column W's real format.
**Pre-existing defect, not introduced by the RC-09 correction.**

Column W's canonical form is `7.5 (Brewer), 2.5 (Calligrapher)` — amount first,
tool in parentheses. The parser only recognised the opposite order,
`Brewer: 7.5`, and required a `:` to attempt per-tool parsing at all. On the real
format it fell through and left `crp_dict` **empty**.

Because `/craft` rebuilds the whole cell from that dict, the sequence was:

```text
before:  "7.5 (Brewer), 2.5 (Calligraph)"      /craft awards 2.5 CRP in Brewer
after:   "Brewer: 2.5"
```

Brewer's 7.5 discarded instead of accumulated; Calligrapher erased entirely; the
maintainer's format rewritten. **Every craft by a character with per-tool CRP lost
data.** Reproduced directly against the real format before fixing.

A second consequence: the RC-09 Master gate reads the same value, so it returned
`0.0` for everyone and would have refused every character — including one holding
`150 (Brewer)`. That gate was still uncommitted, so no player ever hit it.

**Fixed** in `models/skills.py` (§2c): the canonical form is parsed by pattern
rather than by splitting on commas — necessary because the amount may itself use a
comma as its decimal mark (`7,5 (Brewer)`) — the legacy colon form is still read
for rows the bot already rewrote, and saves now write the canonical form back so
the convention stops churning. Seven regression tests.

**Two things this leaves open, both for the maintainer:**

- **How many rows are already in colon form?** Those are the characters whose CRP
  was rewritten, and possibly truncated, by past crafts. A glance down column W
  showing a mix of `7.5 (Brewer)` and `Brewer: 7.5` would say how far it spread.
  The fix stops further loss but cannot recover what was already overwritten —
  Google Sheets version history is the only route to that.
- **Tool-name abbreviations** — OD-06, now escalated. `(Calligraph)` does not match
  `Calligrapher's Supplies`, and resolves to `0.0` silently.

**Why this is the most important finding in Phase 0.** It is the exact failure mode
the whole migration is meant to eliminate: a lenient parser that never rejects, a
whole-row write that never checks, and no test holding the real data shape. It went
unnoticed because the code was self-consistent — the parser and the serialiser
agreed with each other, and only disagreed with production.

### 4.7 Foundry field mapping verified — five corrections, one of them structural

Two real Actor exports (level-9 Paladin, 128 items; level-14 Sorceress, 364 items)
were checked against every path in `foundry-mapping.md` §4.2. Most held. Five did not:

| # | Finding | Why it matters |
|---|---|---|
| **F-F1** | A manual export carries `"_id": null` — the real ID survives only in the *filename* | Mappings can never be established from an export. Reinforces ADR 0006's module-over-export design for a second, independent reason |
| **F-F2** | Derived values are **absent**, not merely derived: `abilities.*.mod`, `hp.max`, `ac.flat`, `attributes.prof`, `details.level` | The platform must **compute** the ability modifier from `.value`. My earlier claim that it could be *read* from Foundry was wrong — the conclusion survives, the mechanism changes |
| **F-F3** | `system.tools` is keyed by **artisan name** — the same vocabulary as Sheet columns W/X | The tool code table is **shared with Foundry, not translated**. Three aliases needed: `disg`, `scrolls`, and the instruments |
| **F-F4** | **Foundry models Bastions natively** — `system.bastion` plus typed, sized `facility` items with assigned orders | Reverses a §4.3 claim. Creates a contested group the ownership matrix did not have, and gives Phase 11 a real data source |
| **F-F5** | An actor is **1.1–3.3 MB of JSON**, no embedded images — genuine item volume | Phase 7's snapshot endpoint needs megabyte-scale request limits, and content-hash idempotency hashes megabytes per actor |

**Two match-by-name traps worth calling out**, because both would be silent:

- **"Experience" means different things.** Sheet column G is a *mission count*;
  Foundry's `details.xp.value` is D&D XP (48 000 and 140 000 on these actors). Same
  word, unrelated quantities, never to be reconciled.
- **Class, race and subclass names are customised.** `name: "Sorceress"` /
  `identifier: "sorcerer"`; `"Tiefling; Infernal Legacy"`; `"Pyromancer (PSK)"`. Map
  on `system.identifier`.

**The good news is F-F3.** The sheet, the bot and Foundry all describe tools by artisan
name, so the controlled vocabulary is one table shared by three systems rather than two
translations. That was the single largest piece of guesswork in the Foundry mapping, and
it turned out to already agree.

### 4.8 The two Codex re-review findings on column W — **both fixed**

Returned by the independent Codex re-review of the §2c fix, 2026-07-30.

#### Blocking — a partial parse could still overwrite the rest of the cell

The §2c fix matched the canonical pairs with `findall()`, which keeps whatever
fragments match and ignores the rest:

```text
cell:   "7.5 (Brewer), BROKEN"        read as crp_dict = {"brewer": 7.5}
craft:  awards 2.5 CRP in Brewer
saved:  "10 (Brewer)"                 -- "BROKEN" gone, permanently
```

Narrower than §4.6 but identical in kind, and it applied to the legacy colon form
too. The lesson of §4.6 was that a lenient parser plus a whole-row write is what
destroys data; accepting the fragments it happens to understand is exactly that
leniency.

**Fixed.** A cell is read as a per-tool list only when every fragment parses **and**
everything outside the matched fragments is a separator; both notations are matched
by one pattern, so a mixed cell is read in full rather than half. Anything else keeps
its raw value verbatim, sets `crp_unparsed`, and **pins column W read-only** — it is
omitted from the write set, so the adapter writes no range for it and the stored text
survives. `add_tool_crp()` refuses such a row, `/craft` refuses the craft before
spending anything, and `get_summary()` shows the raw text and says it is unreadable
so the row surfaces for reconciliation rather than reading as a silent `0`.

Two encodings are read correctly that were not before, both previously partial
parses: a legacy value with a comma decimal (`Brewer: 7,5` — read as `7`) and a
mixed-notation cell.

#### Important — an award could create a second identity for the same tool

`/craft` wrote `crp_dict` itself, keyed by the cleaned tool name, while
`get_tool_crp()` compares keys after cleaning **both** sides. A hand-written cell
therefore gained an entry instead of accumulating:

```text
before: "2.5 (Smith's Tools)"   award 2.5 with Smith's Tools
after:  "2.5 (Smith's tools), 2.5 (Smith)"    -- gate reads 2.5 of 5
```

**Fixed.** `Skills.add_tool_crp()` owns CRP mutation: it resolves the tool with the
same normalisation as `get_tool_crp()`, adds to the existing entry under its stored
spelling, folds duplicate spellings already in the cell into that one entry,
validates the amount and the stored value, keeps the canonical serialisation, and
marks the column modified. `/craft` calls it and no longer touches `crp_dict`.

#### What these two leave open

- **Rows already carrying a split identity** (`2.5 (Smith's tools), 2.5 (Smith)`) are
  consolidated only when that tool is next awarded. Until then the Master gate reads
  the first entry alone. A maintainer pass over column W is the only way to find them;
  the Phase 2 importer should report them.
- **A first per-tool award still shadows an untagged legacy total.** The `general`
  bucket counts for a tool only while it is the sole entry, so awarding 2.5 to a
  character holding a bare `120` leaves `{general: 120, smith: 2.5}` and the gate
  reads 2.5. This follows from the OD-34 ruling (untagged CRP is assigned by hand,
  once, at import) rather than from this fix, and is now pinned by a test that says so.
- **Refusing a craft is a behaviour change** for a character whose column W cannot be
  read: previously the craft succeeded and quietly damaged the cell. Refusing before
  any deduction is the atomic choice, but it does block that character until the cell
  is corrected.
- **A duplicate entry inside an otherwise valid cell still overwrote the earlier
  one.** The second Codex re-review found this; it is §4.9, and it is fixed.

### 4.9 The second Codex re-review finding on column W — **fixed**

Returned by the second independent Codex re-review, 2026-07-30, and classified
**Blocking**. This is the fourth instance of one mechanism — a lenient read feeding
a whole-cell write — and the narrowest yet.

#### The defect

§4.8 made parsing all-or-nothing at the level of the **cell**. Inside it,
`_parse_crp_cell()` still lower-cased each tool name and assigned it straight into
the dictionary, so a second fragment naming the same tool replaced the first:

```text
stored:        "2.5 (Smith), 2.5 (SMITH)"
parsed today:  {"smith": 2.5}        -- the first 2.5 is already gone
award:         +2.5
saved today:   "5 (Smith)"           -- the correct total is 7.5
```

2.5 CRP discarded silently. `add_tool_crp()` folds duplicate *spellings* it can
see in `crp_dict`, but it never saw the second entry: the loss happened one layer
earlier, at read time. It applied identically to the legacy notation
(`Smith: 2.5, SMITH: 2.5`) and to a cell mixing the two
(`2.5 (Smith), Smith: 2.5`).

#### The policy chosen, and why it is safe

The remedy offered two options. **Consolidation by summing was chosen** over
marking the cell unreadable.

**Why consolidation is safe here.** The entries are not ambiguous. Two names equal
after case-folding are the same tool by any reading, so there is exactly one
arithmetic interpretation and no maintainer judgement is needed to reach it. CRP
is a plain additive quantity, so summing is the only operation that conserves it;
nothing is dropped, nothing is invented, and the resulting total is the one the
cell already meant. The all-or-nothing rule that §4.8 established is about **not
writing back a value derived from a parse that did not understand the cell** — and
this parse understands the cell completely.

**Why the alternative was rejected.** Pinning the cell read-only would block
`/craft` for a character whose column W has no doubt about its meaning, on the
strength of a cosmetic difference in capitalisation. That is a real cost to a
player for no gain in safety, and it would leave the CRP mis-stated at the Master
gate for as long as the row went unreconciled.

**Determinism.** The first spelling seen keeps both the entry and its position in
the cell, so the serialisation is stable regardless of how the duplicates were
ordered. `7.5 (Brewer), 2.5 (Smith), 2.5 (BREWER)` reads as
`{brewer: 10, smith: 2.5}`, in that order, and writes back as
`10 (Brewer), 2.5 (Smith)`.

**Consolidation never triggers a write on its own.** `crp_modified` is still set
only by `add_tool_crp()`. A duplicate row is repaired in memory and the stored
cell is left exactly as it stands until CRP is actually awarded.

#### Deliberately narrow: what is *not* consolidated

Only names equal after case-folding are merged. Names differing by more than case
stay separate, because merging them would mean using `_clean_tool_name()`'s
tool-to-artisan bridge to decide identity at read time. That bridge collapses a
name to its first word, so it merges anything sharing one — including a
non-canonical spelling nobody has validated. Column W is free text, and OD-06's
standing rule is that an unrecognised artisan must **fail loudly at import rather
than be guessed at**; a silent read-time merge is exactly that guess.

So `2.5 (Smith's tools), 2.5 (Smith)` still reads as two entries and is folded by
`add_tool_crp()` when that tool is next awarded — §4.8's behaviour, unchanged and
still pinned by its own test.

#### One further fail-closed case, found while fixing this

A digit run long enough to overflow `float()` to infinity — on its own, or once a
duplicate was added to it — previously entered `crp_dict` as `inf` and could be
written back over the cell. Such a value is now unreadable like any other the
parser cannot represent: raw value preserved, `crp_unparsed` set, column W pinned
read-only. This was not in the finding; it is the same fail-closed rule applied to
the one numeric input that could evade it.

#### What this leaves open

Nothing new. The three items §4.8 left for the maintainer are unchanged, and the
first of them — rows already carrying a **split identity**
(`2.5 (Smith's tools), 2.5 (Smith)`) — is deliberately *not* addressed here, for
the reason given above. Rows carrying a **case-variant duplicate** no longer need
a maintainer pass: they are repaired on read, and the Phase 2 importer will see
the consolidated value.

---

## 5. Security and privacy implications

### Handled

- **No credential was read.** `.env`, `yt-cookies.txt` and any service-account
  material were left untouched, per `.agents/AGENTS.md`.
- **No live Foundry world data was read.** Only `world.json` and `system.json`
  manifests — configuration metadata containing no character data. An offline
  LevelDB snapshot would have required maintainer authorization that was not
  given, and the databases are held open by running servers.
- **No live Google Sheet was read.** The entire sheet inventory is reconstructed
  from source code plus the maintainer's own description.
- **No production service was modified**, started, stopped or reconfigured.
- **All fixtures are synthetic by construction**, using reserved ID ranges an
  order of magnitude below real Discord snowflakes so a real ID is obvious in
  review. Enforced by `tests/test_fixtures.py`, not only by review.

### Real character data: what was and was not accessed

Stated plainly, because two earlier statements in these documents were too broad.

- **Two real Foundry Actor exports were opened and read**, supplied by the maintainer
  on 2026-07-30 for exactly that purpose. That is how §4.7's five corrections were
  found. Reading them was authorised, deliberate, and the reason the Foundry mapping
  is verified rather than proposed.
- **They were read for structure only** — field paths, which values are absent,
  vocabulary keys, document size. No value from either document is reproduced
  anywhere in this repository.
- **Neither was ever committed.** They arrived inside `docs/` and are now held outside
  the repository at `/opt/discord-bots/foundry-actor-exports/`; a narrow
  `fvtt-Actor-*.json` rule in `.gitignore` prevents a future export from being staged.
- **No live Google Sheet row was ever read**, so no player-name value from column C
  has been seen at all.
- The maintainer has confirmed the Foundry/Sheet game data is fictional characters
  rather than personal information. The one genuine exception is `Characters` column
  **C**, which holds real player names and stays out of fixtures.

The acceptance criterion is *"no secrets or real player records are **committed**"*, and
that is met. "No real player data was accessed" would not be an accurate statement of
this milestone and is not claimed.

### Surfaced for maintainer attention

| # | Finding | Where |
|---|---|---|
| S-1 | **Foundry binds to `*:30001-30003`, not loopback**, while Caddy proxies from `127.0.0.1`. Unless a host firewall blocks those ports, the instances are directly reachable, bypassing Caddy's TLS. **This is the only finding that may be a live exposure and is worth checking independently of the platform work.** | `topology.md` F-1, OD-25 |
| S-2 | The Google service account holds `spreadsheets` scope — read/write on the whole document, not a narrower scope | `sheet-inventory.md` §1 |
| S-3 | `USER_ENTERED` writes mean bot-written strings are re-interpreted by Sheets; a value beginning with `=` becomes a formula. The free-text columns round-trip player input verbatim | `sheet-inventory.md` §1 |
| S-4 | `freedom-bot.service.tmpl` has none of the systemd hardening that `lavalink.service.tmpl` has, despite holding the Discord token and Google key | `topology.md` F-3 |
| S-5 | No tested recovery procedure exists for the live game data. The only rollback today is Google's own version history | `topology.md` §6 |
| S-6 | Secrets are a plain `.env` read by `python-dotenv` at import | `topology.md` F-5 |

S-1 and S-4 are pre-existing conditions unrelated to this milestone's work. They
are reported because Phase 0 discovery surfaced them, not because anything here
caused them.

---

## 6. Commands run and exact results

| Command | Result |
|---|---|
| `./venv/bin/python -m pytest -q` (Phase 0 docs) | **43 passed**, 1 warning (`audioop` deprecation from `discord/player.py`, pre-existing). Run before and after the documentation work; identical both times |
| `./venv/bin/python -m pytest -q` (after rule corrections) | **118 passed**, same 1 pre-existing warning. Run 5 consecutive times with identical results — no flakiness from the patched dice |
| `./venv/bin/python -m pytest -q` (at Codex review, 2026-07-29) | **127 passed**, same 1 pre-existing warning. Confirmed independently by Codex |
| `./venv/bin/python -m pytest -q` (after the §2c column W fix) | **134 passed**, same 1 pre-existing warning — the 7 new CRP regression tests |
| Column W defect reproduction, before the fix | `"7.5 (Brewer), 2.5 (Calligraph)"` → `crp_dict = {}`, `get_tool_crp() = 0.0`; a 2.5 Brewer award then wrote back `"Brewer: 2.5"`, losing Calligrapher entirely |
| Column W round-trip, after the fix | Same input + same award → `"10 (Brewer), 2.5 (Calligraph)"`. Accumulated, other tool preserved, canonical format preserved |
| Master gate, after the fix | `"150 (Brewer)"` → `get_tool_crp("Brewer") = 150.0` ≥ 100, so a qualified character is no longer refused |
| Tool-name cleaning, all 22 `TOOL_CHOICES` | Enumerated to confirm the canonical cleaned names; `Calligrapher's Supplies` → `Calligrapher`, which is why an abbreviated `(Calligraph)` silently yields 0.0 (OD-06) |
| Foundry world identity | All three `the-guild` paths → **inode 4388511, device 64769**; `/etc/fstab` declares the binds. One shared world |
| Foundry versions, per instance | foundry1/2/3 all core `14.365`, `dnd5e` `5.3.3`; binaries and `systems/` trees are separate per instance |
| Numeric re-verification against the PDF | RC-02: all 5 bands ×1.20 exactly; RC-04: 12/12 table cells match; RC-03: p.11 example → 581.25 GP at 155%, p.12 example → 47 GP 5 SP at 190% |
| `python3 -c "import csv; ..."` (fixture validation) | 38 columns, 24 records, 22 data rows, no width mismatch, **column alignment vs `Actor.COLUMNS` OK** |
| `python3 -c "import json; ..."` (fixture validation) | valid JSON, 7 items |
| `grep -rInE '(DISCORD_TOKEN\|private_key\|BEGIN.*PRIVATE KEY\|client_secret\|...)' docs/ tests/fixtures/` | one hit, a documentation reference to `.gitignore` contents. **No secret** |
| `grep -rnoE '[0-9]{15,20}'` over new files | only reserved-range synthetic IDs |

### 6a. The export-removal and fixture-completion round (2026-07-30, later)

| Command | Result |
|---|---|
| `md5sum docs/fvtt-Actor-*.json`, then `mv` out of the repository, then `md5sum` again | `af602fb7…` and `07a4d8a7…` **identical before and after**. Both files now at `/opt/discord-bots/foundry-actor-exports/`, 1 119 504 and 3 343 208 bytes |
| `git check-ignore -v docs/fvtt-Actor-…json fvtt-Actor-anything.json tests/fixtures/fvtt-Actor-x.json` | all three matched by `.gitignore:20: fvtt-Actor-*.json`, exit 0 |
| `git check-ignore -v tests/fixtures/foundry_actor_sample.json docs/discovery/foundry-mapping.md` | exit 1 — **not** ignored, so the rule does not shadow the synthetic fixtures |
| `git status --short` | 9 modified/deleted tracked paths and 10 untracked paths (§2, §11). **No `fvtt-Actor-*` path appears at all**, including under `--ignored` |
| `git diff --check` | clean, exit 0 — no whitespace errors, no conflict markers |
| `./venv/bin/python -m pytest -q` | **162 passed**, same 1 pre-existing `audioop` warning. 134 → 162 is the 28 new fixture-validation tests |
| `./venv/bin/python -m pytest -q tests/test_fixtures.py` | **28 passed** |
| CSV fixture re-validation | 24 records, 22 data rows, **all rows exactly 38 columns**, header row equals the verified 38 headers, and every `Actor.COLUMNS` letter lands on its documented header |
| JSON fixture re-validation | both valid. `foundry_actor_sample.json`: 11 items, `_id: null`, `ep: 0`. `foundry_actor_anomalies.json`: 1 item, `_id: null`, `ep: 7` (the deliberate anomaly) |
| `grep -rInE '(DISCORD_TOKEN\|private_key\|BEGIN.*PRIVATE KEY\|client_secret\|password[:=])' docs/ tests/` | two hits, both **documentation of this scan command itself**. No secret |
| `grep -rnoE '[0-9]{15,20}' docs/ tests/fixtures/` | 9 hits, every one a reserved-range example from `fixture-strategy.md §3` or `tests/fixtures/README.md`. Nothing at or above 1×10¹⁸, i.e. nothing at real-snowflake scale |

### 6b. The Codex re-review correction round (2026-07-30, later still)

| Command | Result |
|---|---|
| `../venv/bin/python -m pytest -q` | **189 passed**, same 1 pre-existing `audioop` warning. 162 → 189 is the 27 new CRP regression tests |
| `../venv/bin/python -m pytest -q tests/test_skills.py` | **44 passed** |
| `git diff --check` | clean, exit 0 — no whitespace errors, no conflict markers |
| `git status --short` | 9 modified/deleted tracked paths and 10 untracked paths — unchanged from §6a, no new file added or removed |
| `git diff --stat` | 523 insertions, 51 deletions across 9 tracked files (cumulative: §2b rule corrections, §2c and §2e column W work, the `.gitignore` rule, and the maintainer's own PDF move) |
| Diff reviewed for unrelated changes | Only `models/skills.py`, `ext/commands/craft.py` and `tests/test_skills.py` were touched in this round, plus the documentation listed in §2e's narrative; every code hunk is CRP parsing, CRP mutation or its tests. **No fixture, secret, credential or configuration file was touched** — `tests/fixtures/` is byte-identical to §6a |
| `grep -rInE '(DISCORD_TOKEN\|private_key\|BEGIN.*PRIVATE KEY\|client_secret\|password[:=])'` over the changed files | hits only in the two documentation lines that quote this scan command. **No secret** |
| `grep -rnoE '[0-9]{15,20}'` over the changed code and tests | no hits — nothing at snowflake scale, and no player or character data was introduced |
| Blocking finding reproduced, after the fix | `"7.5 (Brewer), BROKEN"` → `crp_dict = {}`, raw value kept verbatim, `crp_unparsed = True`, `can_record_tool_crp() = False`, the award raises, and **`get_sheet_data()` contains no `crp` key even with `crp_modified` forced true** — so the cell cannot be rewritten as `"10 (Brewer)"` |
| Same, malformed text *between* valid pairs | `"7.5 (Brewer), BROKEN, 2.5 (Smith)"` → `crp_dict = {}`, raw preserved, unparsed |
| Unreadable value surfaced | `get_summary()` → `**Crafting Reputation:** 7.5 (Brewer), BROKEN *(unreadable format -- ask the Guild Council to correct it)*` |
| Valid cells still round-trip, +2.5 award each | `"62.5 (Alchemist), 5 (Smith), 2.5 (Brewer)"` → `"62.5 (Alchemist), 7.5 (Smith), 2.5 (Brewer)"`; `"7,5 (Brewer), 2,5 (Calligrapher)"` → `"10 (Brewer), 2.5 (Calligrapher)"`; `"Brewer: 7,5"` → `"10 (Brewer)"` (previously read as 7); `"7.5 (Brewer), Smith: 2.5"` → `"7.5 (Brewer), 5 (Smith)"` (previously a half parse) |
| Important finding reproduced, after the fix | `"2.5 (Smith's Tools)"` + 2.5 with `Smith's Tools` → `"5 (Smith's tools)"`, one entry, `get_tool_crp() = 5.0` (was `"2.5 (Smith's tools), 2.5 (Smith)"` reading 2.5) |
| A row already split by the old code | `"2.5 (Smith's tools), 2.5 (Smith)"` reads **2.5** at the gate; after a 2.5 award it is consolidated to `"7.5 (Smith's tools)"` and reads **7.5** |
| Mastered cell | `"Master"` → `can_record_tool_crp() = False`; the award raises and the literal is not replaced by a per-tool total |

### 6c. The second Codex re-review correction round (2026-07-30, last)

Every command below was run from `/opt/discord-bots/freedom-bot`.

| Command | Result |
|---|---|
| `../venv/bin/python -m pytest -q tests/test_skills.py` **before** the fix | **10 failed, 48 passed**, same 1 pre-existing `audioop` warning. The regression tests were written first and all ten failed on the unfixed parser, which is the point of writing them first |
| `../venv/bin/python -m pytest -q tests/test_skills.py` **after** the fix | **58 passed** |
| `../venv/bin/python -m pytest -q` | **203 passed**, same 1 pre-existing `audioop` warning. 189 → 203 is the 14 new duplicate-consolidation tests |
| `git diff --check` | clean, **exit 0** — no whitespace errors, no conflict markers |
| `git status --short` | 9 modified/deleted tracked paths and 10 untracked paths — **unchanged from §6a and §6b**; no file added or removed |
| `git diff --stat` | 549 insertions, 51 deletions across 9 tracked files (cumulative). §6b recorded 523; the **+26** are all on `models/skills.py`, the only *tracked* file this round touched — `tests/test_skills.py` is still untracked |
| Diff reviewed for unrelated changes | This round touched **`models/skills.py`, `tests/test_skills.py`** and the three documents in §2f. The whole code hunk is inside `_parse_crp_cell()`. No fixture, secret, credential, configuration or generated file was touched; `tests/fixtures/` is byte-identical to §6a |
| `grep -rInE '(DISCORD_TOKEN\|private_key\|BEGIN.*PRIVATE KEY\|client_secret\|password[:=])'` over the changed files | hits only in the documentation lines that quote this scan command itself. **No secret** |
| `grep -rnoE '[0-9]{15,20}'` over `models/skills.py` and `tests/test_skills.py` | **no hits** — nothing at snowflake scale, and no player or character data was introduced. The overflow tests build their digit runs as `"9" * 400`, so no long literal appears in the file either |
| Formatter / linter / type checker | **None is configured in this repository.** `requirements-dev.txt` contains only `pytest`, and there is no `pyproject.toml`, `setup.cfg`, `.ruff.toml`, `.flake8`, `mypy.ini` or `.pre-commit-config.yaml`. Verified by listing the repository root. Unchanged from §6b's "Checks not run" |

**The finding, reproduced before and after:**

| | Before | After |
|---|---|---|
| `"2.5 (Smith), 2.5 (SMITH)"` parsed | `{"smith": 2.5}` — 2.5 discarded | `{"smith": 5}` |
| … then `+2.5` awarded, then saved | `"5 (Smith)"` — 2.5 CRP lost | `"7.5 (Smith)"` |
| … Master gate reads | `5.0` | `7.5` |

**The five required duplicate shapes, after the fix:**

| Stored cell | `crp_dict` |
|---|---|
| `"2.5 (Smith), 2.5 (Smith)"` — identical | `{"smith": 5}` |
| `"2.5 (Smith), 2.5 (SMITH)"` — case variant | `{"smith": 5}` |
| `"Smith: 2.5, SMITH: 2.5"` — legacy notation | `{"smith": 5}` |
| `"2.5 (Smith), Smith: 2.5"` — mixed notations | `{"smith": 5}` |
| `"2,5 (Smith), 2,5 (SMITH)"` — comma decimals | `{"smith": 5}` |
| full path: read → `+2.5` → serialise | `"7.5 (Smith)"`, one entry, `get_tool_crp() = 7.5` |

**Determinism, separation and fail-closed behaviour, after the fix:**

| Case | Result |
|---|---|
| `"7.5 (Brewer), 2.5 (Smith), 2.5 (BREWER)"` | `{"brewer": 10, "smith": 2.5}`, keys in that order; summary `Brewer: 10, Smith: 2.5` |
| Consolidation alone | `crp_modified = False`, `get_sheet_data()` has **no `crp` key**, `crp` still the raw `"2.5 (Smith), 2.5 (SMITH)"` — no write is triggered by a read-time repair |
| `"2.5 (Painter), 5 (Potter), 7.5 (Smith)"` | three separate entries — distinct tools are never merged |
| `"2.5 (Smith's tools), 2.5 (Smith)"` | two entries, unchanged from §6b; folded to `"7.5 (Smith's tools)"` only when awarded |
| `"120 (Calligraph), 5 (Calligrapher)"` | two entries — the OD-06 abbreviation is **not** silently merged into the full name |
| `"2.5 (Smith), 2.5 (SMITH), BROKEN"` | `crp_dict = {}`, raw preserved, `crp_unparsed = True`, `can_record_tool_crp() = False`, and **no `crp` key in `get_sheet_data()` even with `crp_modified` forced true** |
| 400-digit value, canonical and legacy notation | `crp_dict = {}`, raw preserved, unparsed — `inf` never reaches the dictionary |
| two 308-digit values for one tool (only the **sum** overflows) | same — the finiteness check is applied after consolidation, not only per fragment |

**The previous fixes, re-verified unweakened:**

| Case | Result |
|---|---|
| `"7.5 (Brewer), BROKEN"`, `"7.5 (Brewer), BROKEN, 2.5 (Smith)"`, `"Brewer: 7.5, BROKEN"`, `"n/a"` | all still `crp_dict = {}`, raw preserved, `crp_unparsed = True`, `can_record_tool_crp() = False`, column W omitted from the write set with `crp_modified` forced true (F-S3a) |
| `"2.5 (Smith's tools), 2.5 (Smith)"` + 2.5 with `Smith's Tools` | `{"smith's tools": 7.5}` → `"7.5 (Smith's tools)"` — one identity per tool (F-S3b) |
| `"Master"` | `can_record_tool_crp() = False`, the award raises, `crp` still `"Master"`, `crp_modified = False` |
| `"120"` untagged legacy | `{"general": 120}`, reads 120.0 for any tool; after a 2.5 Smith award `{"general": 120, "smith": 2.5}` reading 2.5 / 0.0 — the OD-34 behaviour, unchanged |

### Checks not run

| Check | Why |
|---|---|
| Formatter | None configured in the repository. `requirements-dev.txt` contains only `pytest` |
| Linter | None configured |
| Type checker | None configured |
| Integration / migration tests | No database exists yet — Phase 1 |
| Foundry contract tests | No connector exists yet — Phase 7 |

Adding a formatter, linter and type checker "in a focused change" is called for by
`.agents/AGENTS.md`. It is proposed as the first task of Phase 1 so that all new
code is covered from the start. **It was not done here** — Phase 0 is a
documentation milestone and adding tooling would have exceeded its scope.

---

## 7. Configuration and deployment changes

**None in this milestone.** No configuration file was modified and `.env.example`
is unchanged.

**One housekeeping item, now done.** The maintainer's two Foundry exports were at
`docs/fvtt-Actor-karl-vom-stein-*.json` and `docs/fvtt-Actor-seirirali-rasho-*.json` —
**4.4 MB of real character data inside a documentation deliverable.** They served their
purpose (§4.7) and have been **moved** to `/opt/discord-bots/foundry-actor-exports/`,
outside the repository. They were **moved rather than deleted**: an earlier version of
this document said working copies were held elsewhere, and that was wrong — these were
the only copies. Byte-for-byte identical after the move (MD5 verified both ways).

`.gitignore` gains one narrow rule, `fvtt-Actor-*.json`, so an export dropped anywhere in
the tree cannot be staged by accident. It is deliberately scoped to that filename prefix:
it must not shadow `tests/fixtures/foundry_actor_*.json`, which are synthetic and belong
in version control. Both halves are verified with `git check-ignore` (§6).

`docs/operations/topology.md` §5 proposes the variables Phases 1 and 3 will add
(`ENVIRONMENT`, `DATABASE_URL`, the web and OAuth block, the Foundry block). They
are documented, not applied.

Two notes for whoever implements them: `config.py:16` calls `sys.exit()` on a
missing variable, which is wrong for a web process under a supervisor; and
`ENVIRONMENT` must be validated loudly, since a production process started with a
development database URL is precisely the failure it exists to prevent.

## 8. Rollback and recovery

Nothing is committed. No production service was touched and no data was written
anywhere by this work.

**Documentation and fixtures** roll back with `rm -rf docs/adr docs/discovery
docs/operations docs/review docs/rules tests/fixtures tests/test_fixtures.py` — note
`docs/implementation-plan.md` is tracked and must be preserved.

**The `.gitignore` change** is one tracked file and reverts with
`git checkout -- .gitignore`. Do not revert it while an `fvtt-Actor-*.json` export is
inside the tree; the rule is the only thing stopping such a file being staged.

**The moved Actor exports** are not part of any rollback. They live at
`/opt/discord-bots/foundry-actor-exports/`, outside version control, and moving them
back into `docs/` would undo the whole point.

**Code changes** (§2b rule corrections, §2c column W fix, §2e and §2f re-review
corrections) are working-tree edits to `models/`, `helpers/`, `ext/commands/` and
`tests/`; `git checkout --` on those paths reverts them. Reverting §2c would restore
the CRP data loss, so it should not be reverted without reverting the RC-09 gate as
well; the same applies to §2e and §2f, each of which closes a remaining path to that
loss. The four sets sit in the same files and cannot be reverted independently by
path.

**One recovery item is outside this repository.** §4.6's data loss has already
happened for any character who crafted while holding per-tool CRP. The fix stops
further loss but cannot restore what was overwritten; **Google Sheets version
history is the only route**, and it is time-limited. If recovering those values
matters, it is worth looking sooner rather than later. This is also the concrete
case for S-5 (no tested recovery procedure exists for the live game data).

---

## 9. Unresolved questions

**36 decisions**, in `docs/discovery/open-decisions.md`, each with what it blocks
and — where there is one — a recommendation.

**Sixteen closed across 2026-07-29/30 by maintainer answers**, including: OD-01
(scope is `Characters` plus the player tab, headers supplied), OD-02 (all eleven
unmapped columns identified), **OD-07** (no formulas — Phase 2 is a migration), OD-06
(two vocabularies, `_clean_tool_name()` is the documented bridge), OD-08 (computed
crafting days round to three decimals; fixed constants remain exact; thousandth-days
confirmed), OD-12 (one shared Foundry world),
OD-14 (pin to the deployed version tuple), OD-30 (field mapping verified), OD-34
(untagged CRP resolved by hand at import), OD-35 (ID assigned at row creation), the
electrum group of OD-13, and most of OD-03 and OD-04. **Opened:** OD-36 (the sheet
macros' fate at cutover). **Escalated:** OD-06's residual — an abbreviated artisan name
still resolves to `0.0` silently, which the importer must reject rather than default.

**Both findings from the Codex review of 2026-07-29 are now ruled.** **OD-34** — untagged
CRP is resolved once by hand at import rather than by a code policy, so the existing
`general` fallback and its test stay as they are, and the Phase 2 importer must surface
any bare-number cell. **OD-35** — the ID is assigned when the character row is created
and never derived from anything outside the database, with the Foundry actor ID recorded
in a mapping row rather than a column on `characters`. ADR 0003 was amended accordingly
and is no longer blocked; it is `Accepted`.

**No live-behaviour question is outstanding.** The double-grant risk was disproved,
the column W data loss is fixed — including the narrower partial-parse path the first
Codex re-review found (§4.8) and the duplicate-entry path the second found (§4.9) —
and OD-06's false-refusal path turned out to be a shorthand in conversation rather
than a sheet value.

**Three items §4.8 leaves for the maintainer**, none of them blocking. **§4.9 adds
none**, and narrows the first of them: a row whose duplicate entries differ only in
case is now repaired on read and needs no maintainer pass at all.

1. **Rows already carrying a split tool identity** (`2.5 (Smith's tools), 2.5 (Smith)`)
   read only the first entry at the Master gate until that tool is next awarded, which
   consolidates them. Only a pass down column W will find them; the Phase 2 importer
   should report them alongside the colon-form rows.
2. **A first per-tool award shadows an untagged legacy total** — awarding 2.5 to a
   character holding a bare `120` leaves `{general: 120, smith: 2.5}` and the gate reads
   2.5. This follows from the OD-34 ruling rather than from the fix, and is pinned by a
   test that records it as such.
3. **A character whose column W cannot be read is now refused a craft** that would earn
   reputation, rather than succeeding and damaging the cell. Correct by the atomicity
   rule, but it does block that character until the cell is corrected.

**The questions that were "next" on 2026-07-30 have all been answered.** OD-35 is
ruled and ADR 0003 amended; OD-08 is fully closed — the fixed master-tier constants
`0.25` and `0.125` are charged exactly, which is what thousandth-days exist for; and
OD-01 is closed, the player tab's eight columns supplied and recorded in
[sheet-inventory.md §2.1](sheet-inventory.md#21-the-player-tab).

The most consequential design question, still open:

1. **OD-15** — who owns character level? Plan §6.1 says Foundry; the rules derive
   it from mission count and require Council approval with no automatic
   advancement. **Note that column F holds it, and the sheet also holds classes,
   race, abilities and feats (F-S4)** — so this is now a three-way question, not
   two-way. Recommendation: **Council-approved shared**. *Decide by Phase 1.*

Then, in the order Phase 1 will need them: **OD-21** and **OD-22**, and **OD-36** (the
fate of the two live sheet macros at cutover) before Phase 2 imports anything.

Grouped by when they must be settled:

- **During Phase 1, before the affected design is fixed and before the milestone
  completes:** OD-15, OD-21, OD-22
- **Live behaviour now:** none outstanding
- **Phase 2:** **OD-36**, plus OD-06's residual abbreviation risk at import
- **Phase 3:** OD-16, OD-17, OD-18, OD-19, OD-20, OD-23, OD-24, OD-31
- **Phase 5, per command:** OD-03, OD-04, OD-05, OD-09 and the remaining tribute
  item question in OD-28
- **Phases 6–8:** OD-32, OD-33
- **Write-enablement:** OD-13 and OD-15
- **Check independently:** OD-25

Plan §17 requires its own decision list before Phase 1 completes; every item on it
is covered above.

---

## 10. Proposed reviewer focus areas

**Items 1–3 below were the original asks and are all satisfied.** They are kept as the
record of what closed, not as outstanding requests.

1. ~~**Approve, amend or reject ADRs 0001–0007.**~~ **Done 2026-07-30** — all seven
   `Accepted`, three amended first (0003, 0005, 0006). The per-ADR checklist in
   [adr/README.md](../adr/README.md#maintainer-approval-checklist-phase-0-gate) is
   retained as the record of what was decided.
2. ~~**Supply E-2**~~ **Done 2026-07-30** — two Foundry actor exports supplied and
   verified; five corrections resulted (§4.7). Both E-1 and E-2 are satisfied and no
   production-shape deliverable is unverified.
3. ~~**Rule on OD-34 and OD-35.**~~ **Both ruled 2026-07-30** (§9). ADR 0003 amended
   and unblocked; the untagged-CRP fallback stays as it is by decision, not by
   omission.

Outstanding for the maintainer:

4. **OD-15, character level ownership.** It determines whether the
   no-automatic-advancement invariant survives contact with Foundry. *Decide by
   Phase 1.*

Also worth reading, though not gating:

5. **The rule corrections** (§2b, §4.1) — now settled, with no historical impact
   and no announcement needed. Worth a final read of the RC-07 rationale recorded
   in `helpers/craft_calculator.py`, since it is the one behaviour that looks
   wrong from the CRP table alone.
6. **S-1**, the Foundry port binding — independent of this work, but worth
   checking now.

For Codex (plan §16.4, *architecture and initial schema*):

1. **Dependency direction.** Do ADRs 0002–0005 actually produce the inward-pointing
   graph `.agents/AGENTS.md` requires, or does the SQLAlchemy decision in 0003 leak
   persistence into the domain despite the explicit-mapping rule?
2. **ADR 0005's smallest units, as revised.** Eighth-days were withdrawn on
   2026-07-30 because they cannot represent every computed crafting cost. Under the
   final OD-08 ruling, computed costs round to three decimals and the unit is
   **thousandth-days**. The fixed table constants `0.25` and `0.125` are charged
   exactly. Is thousandth-days the right call, and does
   the conversion behave correctly at the 60-day cap and on a value carrying more
   precision than the unit (`tests/fixtures/sheet_characters_sample.csv`, `Test
   Fraction S`)?
3. **ADR 0007's default-deny posture** — is "any unlisted field is database-owned
   and never overwritten" implementable without becoming a rule nobody can
   enforce?
4. **The fixture strategy's synthetic-by-construction rule** (§1 of
   `fixture-strategy.md`) and the fixtures now built under it. The rule is stronger
   than the plan requires: fixtures are hand-written to match a *verified* shape rather
   than derived from an export. Is that substitution sound now that it has actually been
   exercised twice — and does `tests/test_fixtures.py` pin enough of the verified
   structure to catch a fixture drifting away from it again?
5. **Command inventory §5, G-3 idempotency.** The proposal is to key on
   `ctx.interaction.id`. Is that sufficient for the Phase 5 commands that perform
   multiple rolls in a loop (`/learn`, `/craft` legendary), where a partial
   failure leaves in-memory state mutated?
6. **Whether anything in Phase 0 has silently pre-committed a Phase 1 decision**
   that should have stayed open.
7. **The §2e corrections to your own two findings** (§4.8). Specifically: is
   all-or-nothing parsing plus a read-only pin on column W the right handling for an
   unreadable cell, or should such a row instead be written with the unrecognised text
   retained verbatim beside the parsed entries? And is refusing the craft — rather than
   completing it and dropping the award — the right trade for a row that cannot be
   recorded?
8. **The §2f correction to your third finding** (§4.9). Specifically: is
   consolidation-by-summing the right policy for a duplicate entry, given that it
   silently repairs a cell no maintainer has looked at — or should a duplicate be
   treated as evidence that the row needs reconciling, and pinned read-only like any
   other cell the parser mistrusts? And is the **case-folded** boundary the right place
   to stop, leaving `Smith` beside `Smith's Tools` unmerged at read time so that
   read-time identity never depends on `_clean_tool_name()`'s tool-to-artisan bridge?
9. **The rule corrections in §2b.** Specifically: the RC-09 CRP gate's handling of
   the legacy untagged `"general"` CRP bucket (is counting it toward any tool the
   right call, or should it require Council migration first?); and whether gating
   at project start — rather than on every roll — is the right boundary, given it
   deliberately lets pre-existing under-qualified Master projects finish.

---

## 11. Statement of scope compliance

Per `.agents/AGENTS.md` and the instructions for this milestone:

- Work stayed within Phase 0 plus the explicitly scoped rule-correction task the
  maintainer authorised afterwards. **No web framework, database schema, migration
  or production integration was implemented.**
- No live service — Discord, Sheets, Foundry, PostgreSQL, Lavalink — was
  contacted, mutated or reconfigured.
- No secret or credential was read.
- **No real player data was committed**, and none is in the working tree. Two real
  Foundry Actor exports *were* read, with the maintainer supplying them for that
  purpose, for structural verification only; they are now outside the repository and
  ignored by pattern. The full statement is in §5 — the earlier flat claim that "no
  real player data was accessed" was inaccurate and has been withdrawn.
- The five rule mismatches were documented first and changed only **after** the
  maintainer confirmed them and ruled that the PDF governs. RC-07 was left
  unchanged because the PDF is silent there.

**Phase 0 is accepted and its gate is closed.** The rule corrections, the column W
fix, the fixture completion, the §2e corrections to the first Codex re-review's two
findings and the §2f correction to the second re-review's Blocking finding were all
scoped work inside Phase 0 or explicitly maintainer-authorised follow-ups. The
independent Codex review approved the architecture and data handling, and the
maintainer gave final acceptance on 2026-07-30.
