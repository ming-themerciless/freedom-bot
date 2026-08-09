# Fixture identity correction — real Foundry IDs removed from test fixtures

Date: 2026-08-09
Raised by: Claude, independent reviewer, during Rehearsal A trial setup
Authorised by: Peter Duscha
Classification under implementation plan §16.4: **Important**

## What was found

Two real Foundry identifiers from the live `the-guild` world were committed in
the repository's test fixtures and in one normative contract example:

| Identifier | Real thing it names | Used in fixtures as |
|---|---|---|
| `52ywI3ttEcgf9iBv` | a real Actor | `FIRST_ACTOR_ID` |
| `smob5eya6XVBAuIb` | the real `Characters (active)` folder | `ACTIVE_FOLDER_ID` |

Both were verbatim, not derived. The remaining fixture folder ids
(`root…`, `inac…`, `nest…`, `arch…`, `miss…`, `jrnl…`, `aaaa…`, `bbbb…`) were the
same real folder id with its leading four characters replaced, so they carried
the real tail `5eya6XVBAuIb` as well.

The identifiers were confirmed real by comparison against two manual exports
held outside the repository at `/opt/discord-bots/foundry-actor-exports/`. The
Actor id appears in that export's *filename*; the folder id appears in the
document body as the `folder` field of both exported Actors.

## Why it mattered

Not for confidentiality. A Foundry id is an opaque 16-character token, the
affected character belongs to the maintainer, and no player name, mechanic or
credential was involved. Nothing required rotation.

It mattered because it falsified a control the Phase 2 evidence contract
depends on. `foundry-module/tests/fixtures.mjs` attested in its own header:

> every id, name and value here was invented for the test suite. No real Actor,
> real export or real world data is used, and none is ever committed.

and `docs/discovery/fixture-strategy.md` §1 states that fixtures are
"**invented**, not derived from production and scrubbed", explicitly rejecting
scrub-after-the-fact because "scrubbing is a process that can be skipped, done
partially, or done correctly today and incorrectly by the next contributor".

The prefix-substituted folder ids were precisely that rejected practice. Plan
§13.3 requires "deterministic synthetic snapshot fixtures covering the supported
schema without real character data", and a Data Owner attestation for Rehearsal
B would have inherited a claim that was checkably untrue.

## What was changed

Real identifiers were replaced with invented ones of the same shape (16
characters, alphanumeric, matching `FoundryActorId`/`FoundryFolderId`
validation). The readable four-character folder prefixes were kept because they
aid test legibility; only the shared real tail was replaced.

| Old | New |
|---|---|
| `52ywI3ttEcgf9iBv` | `5tYuIoPaSdFgHj6K` |
| `smob5eya6XVBAuIb` | `actvQwErTyUiOpAs` |
| `<prefix>5eya6XVBAuIb` | `<prefix>QwErTyUiOpAs` |

Files changed:

- `foundry-module/tests/fixtures.mjs`
- `foundry-module/tests/world-source.test.mjs`
- `foundry-module/tests/bundle.test.mjs`
- `tests/foundry_fixtures.py`
- `tests/test_exporter_contract.py`
- `tests/test_foundry_identity.py`
- `tests/test_snapshot_parser.py` (see below)
- `docs/rules/foundry-export-contract.md` — a specimen bundle, not a citation

The `ACTIVE_FOLDER_ID` prefix also changed from `smob` to `actv`, because `smob`
was itself the real id's leading characters rather than an invented label.

### One test needed a behavioural correction, not a rename

`test_selectable_folders_are_a_bounded_set_the_manager_chooses_from` asserted
folder *paths* in an order actually determined by folder *id* sort
(`SnapshotDocument.selectable_folders`, `application/foundry/parser.py:182-187`,
returns `sorted(self.selected_folder_ids)`). The old expectation
(retired before active) held only because `arch…` sorted before `smob…`. With
invented ids `actv…` sorts before `arch…`, so the expected order is reversed.

This is not a product defect — the documented "stable order" is the id sort and
it still holds. The test was silently coupled to the fixture values, so the
expectation was corrected and a comment now records why that order is what it
is.

## What was deliberately not changed

Five files still contain the real identifiers, correctly:

- `docs/discovery/foundry-mapping.md` and
  `docs/adr/0006-foundry-integration-boundary.md` cite the real export as the
  *evidence* for finding F-F1 — "a manual export has no `_id`; the real ID
  survives only in the filename". The identifier is the subject of the finding,
  not a fixture, and removing it would destroy the reasoning.
- `docs/review/phase-2-r4-500-actor-benchmark.md`,
  `docs/review/phase-2-i-03-prompt.md` and
  `docs/review/phase-2-supervised-rehearsal-2026-08-06.md` are historical
  evidence records. `.agents/AGENTS.md` requires corrections to be compensating
  actions rather than erased history, so they are left intact and this document
  is the compensating record.

The identifiers also remain in git history from `f632722` onward. No history
rewrite is recommended: AGENTS.md's history rule concerns secrets, and these are
neither secrets nor credentials.

## Verification

```text
./venv/bin/python -m pytest -q          → 1747 passed, 208 skipped, 0 failed
node --test foundry-module/tests/*.mjs  → 138 passed, 0 failed
node --check foundry-module/scripts/*.js → 7 files, all pass
git diff --check                         → clean
```

Every new identifier was checked to be 16 characters, alphanumeric, and absent
from both real export files. No real identifier fragment remains in any `.py`,
`.js` or `.mjs` file, nor in the contract specimen.

## Residual recommendation — Optional

Nothing currently prevents a future fixture from reusing a real identifier, and
the attestation is prose rather than an enforced property. A cheap guard would
be a test asserting that no fixture identifier appears in the identifiers
`docs/discovery/` cites as real. The stronger option — generating fixture ids
from a documented invented alphabet — is probably more machinery than this
repository needs.
