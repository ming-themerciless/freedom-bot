# Gemini handoff — install the snapshot module on Foundry 1

Copy everything below this line into Gemini as one prompt.

---

Install the local Freedom Blades snapshot-submission module on **Foundry 1
only**, using the same host/deployment method you previously used successfully
for the AI-DM module.

Repository: `/opt/discord-bots/freedom-bot`

Module source: `/opt/discord-bots/freedom-bot/foundry-module`

Expected module ID: `freedom-blades-export`

Expected title: `Freedom Blades — Snapshot Submission`

Target instance: Foundry 1, internally associated with port `30001`

Target world: `the-guild`

External browser origin: `https://foundry1.rpgworld.org`

Maintainer-supplied Foundry 1 User Data Path:
`/home/foundry/foundry1/foundrydata`

Expected destination:
`/home/foundry/foundry1/foundrydata/Data/modules/freedom-blades-export`

Maintainer: Peter Duscha

Authorization date: 2026-08-05

## Authority

Peter explicitly authorizes installation of this module's files on Foundry 1
for the supervised Phase 2 rehearsal.

You may:

- inspect the host configuration needed to identify Foundry 1's process,
  service/container, user-data directory and module directory;
- inspect and reuse the exact successful AI-DM module installation method;
- validate the local module source and its `module.json`;
- copy/install the module under the target instance's module directory;
- set ownership and modes to match the working AI-DM module installation;
- restart or reload **Foundry 1 only** if installation genuinely requires it,
  but pause and ask Peter immediately before causing downtime; and
- verify that Foundry discovers the module on its Setup/module-management
  screen.

You may not:

- access or change Foundry 2 or any other instance;
- enable the module in a world without Peter's explicit confirmation in the UI;
- read, export, enumerate, log, copy or modify Actors, Items, folders,
  compendiums, journals, users or world database content;
- read or expose credentials, invitation links, cookies, tokens or `.env`;
- submit a snapshot or connect the module to an endpoint;
- change reverse-proxy, firewall, CORS or DNS configuration;
- modify the module source in the repository;
- install dependencies or use an external network source;
- commit, push or deploy any unrelated application code; or
- delete/overwrite an existing installation without a recoverable rollback
  copy and explicit target validation.

## Required procedure

1. Read the repository `AGENTS.md`, `.agents/AGENTS.md`, and the complete
   `docs/operations/phase-2-maintainer-closeout.md` before acting.
2. Run `git status --short` and preserve every existing uncommitted change.
3. Inspect `foundry-module/module.json` and verify:
   - ID is exactly `freedom-blades-export`;
   - version is `1.0.0`;
   - Foundry compatibility includes `14.365`;
   - D&D5e compatibility includes `5.3.3`;
   - every file named in `esmodules` and `styles` exists; and
   - no credential or production endpoint is embedded in the module source.
4. Run:

   ```bash
   cd /opt/discord-bots/freedom-bot/foundry-module
   node --test "tests/*.test.mjs"
   for file in scripts/*.js tests/*.mjs; do node --check "$file"; done
   ```

   Stop if either command fails.
5. Identify Foundry 1 by the same authoritative service/container configuration
   used for the AI-DM installation. Do not identify it from a directory name or
   port guess alone. Confirm the resolved process/service maps to internal port
   `30001` and external host `foundry1.rpgworld.org` without printing secrets.
6. Confirm the maintainer-supplied Foundry 1 User Data Path is exactly
   `/home/foundry/foundry1/foundrydata`. Confirm the working AI-DM module exists
   in that same instance's module directory. Record safe paths and
   ownership/mode facts only. If the service/container configuration or AI-DM
   installation points elsewhere, stop and report the discrepancy rather than
   choosing one.
7. Set the destination to exactly:

   ```text
   /home/foundry/foundry1/foundrydata/Data/modules/freedom-blades-export
   ```

   Adapt the `Data/modules` prefix only if the actual proven AI-DM installation
   demonstrates a different Foundry-supported layout.
8. If the destination exists:
   - stop;
   - compare its manifest/version with the source;
   - report whether this is an identical installation or an upgrade; and
   - obtain Peter's confirmation before replacing anything.
9. If the destination does not exist, install atomically:
   - stage a complete copy as a sibling temporary directory;
   - exclude repository-only material not required at runtime only when the
     existing AI-DM deployment method does so safely;
   - verify the staged manifest and all referenced runtime files;
   - set owner/group/modes to match the working AI-DM module, without granting
     broader permissions;
   - rename the staged directory to `freedom-blades-export`; and
   - leave no partial destination if any step fails.
10. Do not restart Foundry automatically. If a restart is necessary, report the
    exact service/container name and ask Peter:

    ```text
    Foundry 1 requires a restart to discover the new module. May I restart
    <exact target> now? This will disconnect current Foundry 1 users.
    ```

11. After restart/reload, verify only that Foundry's module-management surface
    discovers module ID `freedom-blades-export`, version `1.0.0`. Do not enter or
    inspect world content to prove discovery.
12. Tell Peter to enable the module manually for world `the-guild`. Do not enable
    it yourself unless Peter explicitly asks after seeing the installed module.

## Rollback

If installation fails before publication, remove only the named staging
directory you created and leave the destination absent.

If a newly published installation prevents Foundry 1 from starting, move only
the exact `freedom-blades-export` destination to a timestamped disabled sibling,
restart Foundry 1 after Peter approves, and retain the failed copy for review.

Never delete or replace the AI-DM module. Never run a recursive deletion against
the User Data Path, `Data/modules`, a variable that was not resolved and printed
for confirmation, or a wildcard.

## Required report

Return:

- exact Foundry 1 service/container identity;
- exact User Data Path and destination module path;
- source and installed module ID/version;
- module tests and syntax-check totals;
- whether a restart occurred and who authorized it;
- ownership and mode comparison with AI-DM;
- discovery result;
- rollback path/status;
- confirmation that no world data, credential, endpoint, export or other
  Foundry instance was accessed or changed; and
- the one next manual action Peter must perform.

End with exactly one of:

```text
Module installed on Foundry 1; Peter must enable it for world the-guild.
```

or

```text
Module installation blocked; Foundry 1 was left unchanged.
```
