# Module installation record — `freedom-blades-export` 1.0.7

Date: 2026-08-10, 23:24:18 UTC
Performed by: Claude, on maintainer instruction ("install 1.0.7 to foundry1 and
foundry3, then restart")
Authorized by: Peter Duscha
Build installed: `freedom-blades-export` **1.0.7** (change-log **C-17**)
Build replaced: **1.0.6**, installed 2026-08-10 20:49:25 UTC
([record](phase-2-module-1.0.6-install-2026-08-10.md))

This record exists because of the version identity control **CL3-I-2**:
`exporter.version` reaches `foundry_snapshots.exporter_version` and
checksum-bearing audit history, so which bytes carry which version string must be
written down rather than remembered.

## What was installed, and where

| Instance | Destination | Result |
|---|---|---|
| `foundry1` (port 30001, `foundry1.rpgworld.org`) | `/home/foundry/foundry1/foundrydata/Data/modules/freedom-blades-export` | 1.0.6 → **1.0.7** |
| `foundry3` (port 30003) | `/home/foundry/foundry3/foundrydata/Data/modules/freedom-blades-export` | 1.0.6 → **1.0.7** |

`foundry2` was not touched and has no installation of this module.

The installed tree is the same runtime subset as 1.0.5 and 1.0.6 — `module.json`,
`scripts/*.js` (8 files), `styles/*.css` — with no tests, `package.json` or
repository-only material. Both trees are **byte-identical to the repository
build** and to each other, verified with `cmp` per file after the swap. Ownership
`foundry:foundry` and modes (`2775` directories, `644` files) are unchanged.

## What actually differs from 1.0.6

Exactly two files, and the diff is two lines:

```diff
module.json:          "version": "1.0.6",  ->  "version": "1.0.7",
scripts/transport.js: + "non_finite_number",
```

`canonical.js` is **unchanged**, which is C-17's central claim — the exporter's
output is unchanged byte for byte, and the version moved only because the new
refusal code joins the client's bounded `SERVER_ARTIFACT_CODES` list.

## Method

1. Pre-flight, from `foundry-module/`: `npm test` → **155 passed, 0 fail, 0
   todo**; `node --check` over all 8 `scripts/*.js` and 12 `tests/*.mjs`; manifest
   id and version confirmed; every `esmodules`/`styles` path confirmed present;
   the build re-scanned for an embedded credential or endpoint (none found).
2. Each destination was confirmed to hold `1.0.6` before anything moved; a
   destination at any other version aborts the swap for that instance.
3. The installed tree was diffed against the repository build, giving the two
   files above and nothing else.
4. A complete new tree was staged **outside** `Data/modules`, so a second
   `module.json` carrying the same module id was never visible to a scanning
   Foundry. Staging and destination were confirmed to share a filesystem
   (device `64769`) so the swap could be renames rather than copies.
5. The swap was two renames: the old tree out of `Data/modules` and into the
   rollback location, then the staged tree in. The destination is never partially
   written.
6. Verified after the swap: all ten files `cmp`-identical to the repository build
   on both instances.

`/home/foundry/dist/foundryN/modules` is bind-mounted onto each instance's
`Data/modules` (same inode, verified), so the swap is visible through both paths.

## Rollback

The replaced 1.0.6 installations are retained, complete and unmodified:

```text
/home/foundry/module-backups/freedom-blades-export-1.0.6-2026-08-10T232418Z/foundry1/freedom-blades-export
/home/foundry/module-backups/freedom-blades-export-1.0.6-2026-08-10T232418Z/foundry3/freedom-blades-export
```

To roll back, move the current destination aside and move the copy back. They are
outside `Data/modules` and are not discoverable as modules while they sit there.
The 1.0.5 copies from the previous install are also retained.

## Which version an export would now carry — and the claim this corrects

**This is the part that matters for the gate**, and the standing records had it
wrong.

`exporter.version` is not read from the served file. `scripts/main.js:320` reads
`game.modules.get(MODULE_ID)?.version`, which is the **server's package
registry**. That registry is populated when a world is launched — the launch log
prints `Launching World | Loading Package Data` — and not per browser request. So
what determines the stamp is the most recent **world launch**, not the process
start.

Observed from the instances' own logs:

| Event (all 2026-08-10 UTC) | foundry1 | foundry3 |
|---|---|---|
| 1.0.6 installed | 20:49:25 | 20:49:25 |
| world launched | **20:55:27** | **20:55:35** |
| 1.0.7 installed | 23:24:18 | 23:24:18 |
| world launched | **23:40:03** | **23:40:05** |

Neither process was restarted at any point: `foundry1` has run since 2026-08-08
00:44:58, and `foundry3` was restarted once, by this install, at 23:25.

Two consequences:

- **The current state is correct.** Both instances launched their worlds *after*
  1.0.7 was in place, so the registry holds 1.0.7 and an export taken now would
  stamp `1.0.7`. The standing blocker — "no supervised export may be taken until
  the instances are restarted" — is satisfied, by **world relaunch**, which is the
  operation that actually reloads the package list.
- **The earlier claim was wrong from 20:55:27 onward.** The review request and
  C-17 both stated that neither instance had been restarted and that
  `exporter.version` "could still be stamped `1.0.5`". The processes had indeed
  not been restarted, but both worlds were launched six minutes after 1.0.6 was
  installed, which reloaded the registry. From 20:55 onward the stamp would have
  been `1.0.6`, not `1.0.5`. The records are corrected accordingly.

**Not claimed:** no export has been taken, so no artifact has been observed
carrying `1.0.7`. The above is read from the code path and the launch logs, not
from a receipt. Rehearsals A and B remain evidence about `1.0.5`, the build they
ran on.

## One unexplained observation, recorded rather than resolved

During the install window, `foundry1` was observed to stop hosting `the-guild` —
116 open handles under `worlds/the-guild` immediately before the swap, none
afterwards, with the process untouched and **no shutdown entry in the debug log**.
The maintainer states that swapping a module on a live Foundry is safe and that
nothing unusual happened at 20:55 either, and relaunched both worlds at 23:40.
Cause is not established and none is asserted here. It is recorded because a live
world changing state during an install is worth knowing about the next time this
procedure runs, and because the 20:55 relaunch is what the section above rests on.
