# Anonymized Fixture Strategy

Status: **Complete.** The strategy and the fixtures it governs are both delivered.
The **rules in §1–§3 and §8 are binding.**

**Both fixtures were regenerated against the verified structure on 2026-07-30**, and a
third was added. They are validated by `tests/test_fixtures.py`, which fails if a
fixture and the structural documentation disagree.

| File | Regenerated against |
|---|---|
| `sheet_characters_sample.csv` | The **real** 38 headers and the canonical column W format ([sheet-inventory.md §3](sheet-inventory.md#3-column-map--characters)) |
| `foundry_actor_sample.json` | F-F1–F-F5 ([foundry-mapping.md §4](foundry-mapping.md#4-field-mapping)): `"_id": null` as a manual export carries, derived values absent rather than invented, `system.tools` keyed by artisan, native Bastion facilities |
| `foundry_actor_anomalies.json` | **New.** The two must-fail cases — nonzero electrum (case 24) and an unsupported version tuple (case 25) |

What the previous versions got wrong is worth keeping, because it is the reason this
document has a §4 at all: `sheet_characters_sample.csv` carried a header row
*reconstructed from field names*, and its CRP values used a format the live sheet does
not use. That second gap was not cosmetic — it is why the column W data loss went
unnoticed (§6). `foundry_actor_sample.json` was written against the *proposed* field
paths, and five of them were wrong.

**One gap remains, and it is narrower than the deliverable.** The ten columns the bot
never reads (B, C, U, AD–AJ) now have known *meanings* and are populated here, but their
*value formats* were described rather than observed — see `tests/fixtures/README.md`.
The free-text columns V, X, Y, Z and AA have not been surveyed the way column W was.
Neither affects the columns the platform parses today.

**Note on the privacy framing below.** §1 and §4 were written assuming the sheet
held personal data. The maintainer has since clarified that the rows are fictional
D&D characters, and that the elaborate anonymisation procedure in §4 is
unnecessary. The *engineering* reasons for synthetic fixtures stand — a committed
fixture should assert an intended contract, not whatever production happens to
contain — and column **C** (Player Name) is genuine personal data and stays out of
fixtures. §4's questionnaire is retained as a record of how the structure was
actually verified.

Governing rules, all binding:

- *"Production data is never used in automated tests or committed fixtures."*
  (plan §3 principle 11)
- *"Tests must never contact live Discord, Sheets, production databases, Foundry,
  external media services. Do not use real player data or credentials in fixtures."*
  (`.agents/AGENTS.md`)
- Phase 0 acceptance: *"no secrets or real player records are committed."*

## 1. Principle: synthetic by construction, not anonymized after the fact

Fixtures in this repository are **invented**, not derived from production and
scrubbed.

This is a deliberately stronger rule than "anonymize before committing", for two
reasons. Scrubbing is a process that can be skipped, done partially, or done
correctly today and incorrectly by the next contributor. And a scrubbed record
still carries its original *shape* — a balance, a rare item, an unusual
proficiency combination — which can re-identify a player in a community of this
size just as effectively as a name.

The trade-off is real: synthetic data does not surprise you the way real data
does. Section 4 addresses that separately, and keeps the surprising parts out of
the repository.

## 2. What a fixture may and may not contain

**May contain**

- Invented character names drawn from the reserved set in §3.
- Invented Discord snowflakes from the reserved ranges in §3.
- Invented Foundry actor IDs matching Foundry's 16-character alphanumeric form.
- Rule-derived values: costs, DT, Moradinium and CRP taken from the Homebrew PDF
  tables, since those are rules, not player data.
- Deliberately malformed values, for the import-validation tests plan §12 Phase 2
  requires ("duplicates and malformed fields are reported").

**Must not contain**

- Any real character, player, Discord user, guild, channel or role name or ID.
- Any real Foundry actor, world or user ID.
- Any real Google Sheet ID, service-account address, key material or token.
- Any value copied from the live Sheet or a live Foundry world, even with the
  name changed.
- Any real balance, inventory or progress value.

## 3. Reserved synthetic values

Using a reserved set makes an accidental real value obvious in review — anything
outside these ranges in a fixture is a finding.

| Kind | Reserved form | Example |
|---|---|---|
| Character name | `Test <Role> <Letter>` | `Test Smith A` |
| Player handle | `testplayer<N>` | `testplayer01` |
| Discord user ID | `100000000000000001`–`100000000000000999` | `100000000000000001` |
| Discord guild ID | `200000000000000001` | |
| Discord role ID | `300000000000000001`–`300000000000000099` | |
| Discord channel ID | `400000000000000001`–`400000000000000099` | |
| Foundry actor `_id` | `TESTACTOR` + 6 chars | `TESTACTOR000001` |
| Foundry world ID | `test-world` | |
| Sheet ID | `TEST_SHEET_ID_NOT_REAL` | |

Real Discord snowflakes encode a timestamp in their high bits and are currently
around 1.1–1.5 × 10¹⁸. The reserved ranges above are an order of magnitude
smaller, so they cannot collide with a real ID and are recognisable at a glance.

## 4. Obtaining a real shape — **satisfied 2026-07-30**

Static analysis could not answer the questions in
[sheet-inventory.md §6](sheet-inventory.md#6-verification-status-of-the-original-six-unknowns) —
header text, the eleven unmapped columns, whether formulas exist, real data
quality.

**In the event, the maintainer simply answered them directly**, which was faster
and more reliable than any export-and-describe procedure: they authored the sheet
and the rules. All 38 headers, the eleven columns, the formula answer (none, but
three macros), the canonical CRP format and the row count came from that answer.
Only the tab names remain ([OD-01](open-decisions.md)).

The procedure below is kept because it is still the right shape for the *next*
unknown — and because case 7 in §6 shows the cost of guessing a format instead of
asking.

### Procedure

1. A **maintainer** exports the `Characters` tab, read-only, locally. No agent
   and no CI job performs this step.
2. The maintainer answers a structured questionnaire *about* the export:
   - the header text of rows 1–2 for every column A–AL;
   - for each of B, C, O, U, AD–AJ: what it holds, and whether the bot should
     ever write it;
   - for each column: does it contain a formula? (This is the Phase 2 blocker —
     see [sheet-inventory.md §4](sheet-inventory.md#4-formulas-and-macros).)
   - value *shapes* only for the free-text columns V, W, X, Y, Z, AA — e.g.
     *"column Y typically has 2–6 comma-separated entries, roughly a third
     carrying a parenthesised rank"*;
   - counts: total rows, any duplicate names, any row beyond 150;
   - a list of value forms the parsers would mishandle.
3. **Only the answers are committed.** In the event they were recorded inline in
   [sheet-inventory.md](sheet-inventory.md) and attributed there, rather than in a
   separate observations file. The export itself never leaves the maintainer's
   machine and is never attached to an issue, a pull request or a chat message.
4. Fixtures are then written by hand to cover the shapes described, using §3's
   reserved values.

**The Foundry half happened this way, and it worked.** The maintainer exported two
actors; they were read for structure only, and the field paths in
[foundry-mapping.md §4.2](foundry-mapping.md#42-character-mechanics--verified-against-two-real-actors)
were checked against them — five turned out to be wrong. The fixture is then
hand-written to match the *verified* shape, which is the point of the rule: a fixture
generated from an export would encode whatever production happens to contain, rather
than the contract the importer has to uphold.

**Disposition of those two exports.** They were supplied inside `docs/` and have been
**moved out of the repository** to `/opt/discord-bots/foundry-actor-exports/` — moved,
not deleted, because they are the maintainer's only copies. `.gitignore` now carries a
narrow `fvtt-Actor-*.json` rule so an export dropped anywhere in the tree cannot be
staged by accident. Neither file was ever committed.

### Why not just commit an anonymized export

Because the Freedom Blades community is small. A row with 4 000 gp, a legendary
item and Master rank in Smith's Tools identifies one person to anyone in the
guild, whatever the name column says. Renaming does not anonymize a shape.

## 5. Fixture layout

```text
tests/fixtures/
├── README.md                      # the rules, restated where they are used
├── sheet_characters_sample.csv    # synthetic Characters rows, incl. malformed
├── foundry_actor_sample.json      # synthetic dnd5e 5.3.3 actor, export shape
└── foundry_actor_anomalies.json   # electrum + unsupported version tuple
```

Validated by `tests/test_fixtures.py`. It reads `Actor.COLUMNS` out of
`models/actor.py` with `ast` rather than importing it, because importing
`models.actor` pulls in `config`, which reads `.env` — and no test here may touch
credentials (§8).

As later phases need them:

```text
├── sheet_characters_malformed.csv # dedicated import-failure cases
└── discord_member.json            # OAuth2 member payload shape
```

Fixtures are grouped by the **adapter contract** they exercise, not by the test
that happens to use them first, so that repository contract tests shared between
the Sheets fake and the database (`.agents/AGENTS.md`) can use the same data.

## 6. Coverage the fixtures must provide

Derived from plan §13.2's mandatory scenarios and the parser behaviour found in
Phase 0. Each row is a fixture case, not a test name.

| # | Case | Why |
|---|---|---|
| 1 | Minimal valid character | Baseline |
| 2 | Fully populated character | Every column exercised |
| 3 | Empty optional columns | Parsers default rather than fail (`safe_int`, `safe_number`) |
| 4 | `-` sentinel in V, W, X, Y, Z, AA | The codebase's "empty" marker |
| 5 | Comma decimal separator (`12,5`) | `safe_number` accepts it (`helpers/utils.py:11`) |
| 6 | CRP as bare number | `crp_dict = {"general": n}` path; the untagged legacy shape the import must report for one-time assignment ([OD-34](open-decisions.md)) |
| 7 | **CRP in the canonical form** | `7.5 (Brewer), 2.5 (Calligrapher)` — amount first, tool in parentheses. **The format the live sheet actually uses**; a fixture missing this is what let the column W data loss go unnoticed |
| 7a | CRP in the canonical form with comma decimals | `7,5 (Brewer)` — the separator is ambiguous with the list separator |
| 7b | CRP in the legacy colon form | `Brewer: 7.5` — rows the bot itself rewrote before the fix |
| 7c | CRP with an abbreviated tool | `120 (Calligraph)` vs `Calligrapher's Supplies` — resolves to 0.0 silently ([OD-06](open-decisions.md)) |
| 8 | CRP as literal `Master` | Post-mastery state; no running total is kept ([OD-29](open-decisions.md)) |
| 9 | Rank as `Tool (expert)` | First `_parse_item_level` form |
| 10 | Rank as `Expert Tool` | Second form |
| 11 | Rank absent | Falls back to journeyman (X) or `None` (Y) |
| 12 | Two progress entries for one target | Percent-merge repair path (`models/skills.py:124`) |
| 13 | Legendary craft project in V | `crafting <item> (<tool>)` form |
| 14 | Progress with no recognisable level | Defaults to `language` |
| 15 | Notable items, grouped form | `Rare: A, B` |
| 16 | Notable items, `(rarity)` suffix form | Fallback parse |
| 17 | Notable items, unrecognised | Classified `common` |
| 18 | Duplicate character names | First-match-wins behaviour (G-7) |
| 19 | Name differing only by case | Case-insensitive lookup |
| 20 | Non-numeric value in a numeric column | Silent coercion to default |
| 21 | Negative balance | Should be rejected by a DB check constraint |
| 22 | Downtime carrying more precision than thousandth-days can hold (`3.3333`) | ADR 0005 conversion reporting, revised 2026-07-30 from eighth-days |
| 23 | Character with no Foundry mapping | "explicitly unresolved" (plan §12 Phase 2) — the row says so in `Special Notes` |
| 24 | Foundry actor with electrum | [OD-13](open-decisions.md) — in `foundry_actor_anomalies.json`, since no real actor holds any (`ep: 0`) |
| 25 | Foundry actor, unsupported version tuple | Plan §12 Phase 7 fail-safe — same file |
| 26 | Foundry actor with a homebrew item | Rules §8 content must not break import |
| 27 | Foundry actor with a homebrew **facility** (empty `type.subtype`) | F-F4: the facility vocabulary needs an other/homebrew path, not a closed enum |
| 28 | Foundry `system.tools` alias keys (`scrolls`, `disg`, an instrument) | F-F3: the vocabulary is shared with the Sheet, with three exceptions |
| 29 | Foundry actor whose derived values are absent (`hp.max: null`, no `prof`, no `details.level`) | F-F2: the platform must compute them, not read them |

**Cases 7–7c are the ones that were missing, and it mattered.** The original
fixture set encoded only the colon form, which the code understood and production
did not — so nothing tested the format the live sheet actually holds, and `/craft`
silently destroyed per-tool CRP for months. All four shapes are now covered twice
over: by regression tests in `tests/test_skills.py`, and by fixture rows whose
parsed result `tests/test_fixtures.py` asserts through the real adapter code path.

Cases 3–5, 9–11, 14, 17 and 20 all exercise the same underlying property: **the
current parsers never reject.** They coerce. Phase 2's importer must do the
opposite — report the offending row and field (`.agents/AGENTS.md`) — so these
fixtures are the regression barrier between the two behaviours.

## 7. Test isolation

- Unit and application tests use in-memory fakes. No file, no network.
- Repository contract tests run against both the fake and real PostgreSQL, with
  the same assertions (`.agents/AGENTS.md`).
- Google, Discord and Foundry clients are always test doubles.
- Any test that would open a socket fails the build. A `pytest` fixture that
  patches `socket.socket` at session scope is the cheapest enforcement and should
  be added in Phase 1, when the first integration tests arrive.

## 8. Secret hygiene

Fixtures never contain credentials, including expired or revoked ones.

`.gitignore` already excludes `.env`, `*.env`, `.env.*`, `service_account.json`,
`*.pem` and `*.key`. The deployment gate (plan §14.2 step 4)
adds a secret scan.

If a secret is ever suspected to have reached Git history or a log,
`.agents/AGENTS.md` applies without exception: **stop, notify a maintainer, and
rotate the credential.** Deleting the line is not a remedy.
