# Module installation record — `freedom-blades-export` 1.0.6

Date: 2026-08-10, 20:49:25 UTC
Performed by: Claude, on maintainer instruction ("install 1.0.6 to foundry1 and
foundry3")
Authorized by: Peter Duscha
Build installed: `freedom-blades-export` **1.0.6** (change-log **C-16**)
Build replaced: **1.0.5**, installed 2026-08-09, the build Rehearsals A and B ran on

This record exists because of the version identity control **CL3-I-2**:
`exporter.version` reaches `foundry_snapshots.exporter_version` and
checksum-bearing audit history, so which bytes carry which version string must be
written down rather than remembered.

## What was installed, and where

| Instance | Destination | Result |
|---|---|---|
| `foundry1` (port 30001, `foundry1.rpgworld.org`) | `/home/foundry/foundry1/foundrydata/Data/modules/freedom-blades-export` | 1.0.5 → **1.0.6** |
| `foundry3` (port 30003) | `/home/foundry/foundry3/foundrydata/Data/modules/freedom-blades-export` | 1.0.5 → **1.0.6** |

`foundry2` was not touched, and has no installation of this module.

The installed tree is the runtime subset the 1.0.5 installation already used —
`module.json`, `scripts/*.js` (8 files), `styles/*.css` — with no tests,
`package.json` or repository-only material. Both trees are **byte-identical to
the repository build** and to each other, verified with `cmp` per file after the
swap. Ownership `foundry:foundry` and modes (`2775` directories, `644` files) are
unchanged from the 1.0.5 installation.

## Method

1. Pre-flight, from `foundry-module/`: `npm test` → **154 passed, 0 fail, 0
   todo**; `node --check` over all 20 `scripts/*.js` and `tests/*.mjs`; manifest
   id/version confirmed, every `esmodules`/`styles` path confirmed present, and
   the source re-checked for an embedded credential or endpoint (none).
2. Each destination was confirmed to hold manifest id `freedom-blades-export` at
   version `1.0.5` before anything was moved.
3. The old and new trees were diffed: exactly three files differ —
   `module.json`, `scripts/canonical.js`, `scripts/transport.js`. That is the
   whole of C-16 in the module.
4. A complete new tree was staged **outside** `Data/modules`, so a second
   `module.json` carrying the same module id was never visible to a scanning
   Foundry.
5. The swap was two renames on one filesystem: the old tree moved out of
   `Data/modules` and became the rollback copy, then the staged tree moved in.
   The destination is never partially written.

## Rollback

The replaced 1.0.5 installations are retained, complete and unmodified:

```text
/home/foundry/module-backups/freedom-blades-export-1.0.5-2026-08-10T204925Z/foundry1/freedom-blades-export
/home/foundry/module-backups/freedom-blades-export-1.0.5-2026-08-10T204925Z/foundry3/freedom-blades-export
```

To roll back, move the current destination aside and move the copy back. They are
outside `Data/modules` and are not discoverable as modules while they sit there.

## What has **not** happened

- **No Foundry instance was restarted or reloaded.** All three processes have the
  same pm2 uptime as before the installation, and no user was disconnected. A
  restart of `foundry1` and `foundry3` is still required, and needs the
  maintainer's authorization because it disconnects players.
- **Until that restart, the running servers still hold the module list they read
  at boot, and any client that already has the page loaded is still running
  1.0.5 code.** An export produced before the restart may therefore stamp
  `exporter.version` `1.0.5` — which is exactly the ambiguity CL3-I-2 exists to
  prevent. **Do not perform a supervised export, rehearsal or submission until
  `foundry1` and `foundry3` have been restarted and the module-management screen
  shows 1.0.6.**
- The module was **not enabled, disabled or reconfigured** in any world. Its
  world-scoped settings were not read or written.
- No world content — Actor, Item, folder, compendium, journal or user — was read,
  exported, enumerated or changed. No credential was read or created. No
  reverse-proxy, firewall, CORS or DNS configuration was touched. `foundry2` was
  not accessed.

## Next manual actions for the maintainer

1. Authorize a restart of `foundry1` and `foundry3` at a time that suits the
   players. The pm2 process names are `foundry1` and `foundry3`.
2. After the restart, confirm on each instance's module-management screen that
   `freedom-blades-export` is discovered at version **1.0.6**.
3. Confirm the module is still enabled in the world it was enabled in; replacing
   files does not change enablement, but the screen is where that is observed.

Installing a build closes no gate, and C-16 still carries no independent review.
