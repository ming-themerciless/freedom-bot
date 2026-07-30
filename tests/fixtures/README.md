# Test Fixtures

**Every value in this directory is invented.** Nothing here is derived from the
live Google Sheet, a Foundry world, or any Discord guild.

Full rationale and procedure:
[`docs/discovery/fixture-strategy.md`](../../docs/discovery/fixture-strategy.md).

## Rules

1. **Synthetic by construction.** Write fixtures by hand. Never export production
   data and scrub it — a scrubbed row keeps its shape, and a shape identifies a
   player in a community this size.
2. **Use the reserved value ranges.** Anything outside them is a review finding:

   | Kind | Reserved form |
   |---|---|
   | Character name | `Test <Role> <Letter>` |
   | Discord user ID | `1000000000000000xx` |
   | Discord guild ID | `200000000000000001` |
   | Discord role ID | `3000000000000000xx` |
   | Discord channel ID | `4000000000000000xx` |
   | Foundry actor `_id` | `TESTACTOR` + 6 chars |
   | Foundry world ID | `test-world` |
   | Sheet ID | `TEST_SHEET_ID_NOT_REAL` |

   Real Discord snowflakes are around 1.1–1.5 × 10¹⁸ — an order of magnitude
   larger than the reserved ranges, so a real ID stands out immediately.
3. **No credentials.** Not even expired or revoked ones.
4. **Rule values are fine.** Costs, downtime, Moradinium and CRP figures come
   from `Freedom Blades - Homebrew Rules.pdf`. Those are rules, not player data.
5. **Malformed rows are intentional.** The current parsers never reject input;
   they coerce it. The importer must do the opposite, so the bad rows here are
   the regression barrier between those two behaviours.

## Files

| File | Purpose |
|---|---|
| `sheet_characters_sample.csv` | Synthetic `Characters` tab rows covering the valid, edge and malformed cases in fixture-strategy §6 |
| `foundry_actor_sample.json` | Synthetic `dnd5e` 5.3.3 actor in **manual-export shape**, for mapping and contract tests |
| `foundry_actor_anomalies.json` | Synthetic actor carrying the two must-fail cases: nonzero electrum, and an unsupported (core, system) version tuple |

`tests/test_fixtures.py` validates all three against the verified structural
documentation. If a fixture and the documentation disagree, that test fails — which
is the point: these files are a contract, not sample data.

## What is verified and what is not

**Verified, 2026-07-30.** The header row of `sheet_characters_sample.csv` is the
**real** header text for all 38 columns of the `Characters` tab, supplied by the
maintainer and recorded in
[sheet-inventory.md §3](../../docs/discovery/sheet-inventory.md#3-column-map--characters).
Every column letter `Actor.COLUMNS` (`models/actor.py:11`) maps lines up with its
real header, and `tests/test_fixtures.py` asserts that alignment. Column W uses the
**canonical** `7.5 (Brewer)` form the live sheet actually holds, alongside the legacy
`Brewer: 7.5` form, which coexists with it by design (OD-34).

The Foundry fixtures follow the structure verified against two real Actor exports
(F-F1–F-F5 in
[foundry-mapping.md §4](../../docs/discovery/foundry-mapping.md#4-field-mapping)):
`"_id": null` as a manual export carries, derived values absent rather than invented,
`system.tools` keyed by artisan, and native Bastion facilities.

**Still not verified: the *value shapes* of the ten columns the bot never reads.**
Their meaning is known (B long name, C player name, U weekly expenses, AD–AJ character
detail), and they are populated here so Phase 2's importer has something to read, but
the maintainer described what those columns hold rather than how their contents are
formatted. The `Abilities (STR/DEX/CON/INT/WIS/CHA)` value in particular is a plausible
guess at a layout, not an observed one. Row 2 of the live sheet is also a header row
whose text was not supplied.

Neither gap affects the columns the platform parses today, but an importer must not
treat this file as evidence for how AD–AJ are formatted. The free-text columns V, X, Y,
Z and AA have not been surveyed the way column W was — see
[sheet-inventory.md §6](../../docs/discovery/sheet-inventory.md#6-verification-status-of-the-original-six-unknowns),
item 6.
