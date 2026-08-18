# Operating C-04 — the Sheet-era identity-evidence migration

Status: operator runbook for **P3.2**. Authority: change-log entry
[`C-P3.2-A`](../project-management/change-log.md) (Peter Duscha, 2026-08-17) and
[`phase-3-identity-migration-contract.md`](../contracts/phase-3-identity-migration-contract.md)
§7. Read §7.2, §7.3.1 and §7.7 of that contract before running anything here.

C-04 is a **temporary migration/import utility with an end date.** It exists
because some current character/player data still lives in the legacy Google
Sheet. Google is migration *input*: not an operational database, not a platform
component, not a portal dependency, and not a participant in any decision.

```text
C-04 --dry-run --player-tab Players     Guild Council, in the portal
────────────────────────────────        ────────────────────────────
read the legacy Sheet, read-only  ──▶   R-28 lists one run's proposals
write proposals and candidates          R-29 confirms one → creates the link now
write NO character_access               R-30 rejects one → creates nothing
never write to Google                   nothing auto-confirms, nothing in bulk
```

There is no second command. A Guild Council confirmation creates the
`character_access` row itself, atomically with its decision and both audit
events; the withdrawn `C-05 --apply` step does not exist and its identifier is
retired. If you are waiting to "apply" a run, you are waiting for something that
already happened.

## 1. The separate operator environment

**C-04 cannot be run from `venv-web`, by design.** The Google client libraries are
deliberately absent from `requirements-web.txt` and its lock file
([configuration and dependency contract §1.2](../contracts/phase-3-configuration-and-dependency-contract.md)),
so the portal and the Discord bot never carry them. Provision a throwaway
environment for the migration window instead:

```bash
python3 -m venv /tmp/fb-identity-migration
/tmp/fb-identity-migration/bin/pip install -r requirements-web.txt
/tmp/fb-identity-migration/bin/pip install \
    'google-api-python-client>=2.136.0' 'google-auth>=2.33.0'
```

Properties this environment must have, and must not:

- it is **not deployed**, not referenced by any systemd unit and not on any
  service path;
- it holds the **read-only** service-account credential and no other;
- it is destroyed at retirement (§4).

Record the two extra package versions in the migration's evidence. They are not
an addition to the accepted dependency set; they are the operator environment's,
for the window.

## 2. Credentials and configuration

C-04 uses a narrow command settings type while delegating its database target to
the same database validator every other entry point uses — a command cannot be
pointed at production by an inherited `PGHOST`, and the environment/guild pairing
rule (S-07) is enforced here as it is in the portal. It does not require or accept a
reason to copy portal OAuth, WebAuthn, session, cookie or encryption secrets into
the temporary operator environment.

| Variable | Purpose |
|---|---|
| `WEB_ENVIRONMENT` | Selects the expected database name (`development`, `test`, `staging` or `production`) |
| `WEB_DATABASE_URL` | the PostgreSQL target the proposals are written to |
| `WEB_DISCORD_GUILD_ID` | the guild whose projected members may become proposal subjects. It must pair with `WEB_ENVIRONMENT` (S-07): a production run must name the production guild, and no other environment may name it. The command scopes its membership scan and every proposal row by this snowflake, so a mismatch writes a whole evidence run attributed to the wrong community |
| `GUILD_SHEET_ID` | the legacy spreadsheet to read |
| `SHEET_READONLY_SERVICE_ACCOUNT_JSON` | **the read-only service account.** Set it. If it is unset, `adapters/sheets/read_only.py` falls back to the shared `SERVICE_ACCOUNT_JSON` and says so on stderr — a warning worth reacting to, because the shared account can write |

The credential is granted `spreadsheets.readonly` and nothing else, and the
reader it builds has exactly one method, which reads one A1 range. There is no
write path in the reader, the adapter or the command.

## 3. Running it

```bash
/tmp/fb-identity-migration/bin/python -m tools.identity_migration \
    --dry-run --player-tab 'Players'
```

`--player-tab` is **required**. Peter Duscha confirmed on 2026-08-17 that the
one-time C-04 input tab is named **`Players`** (`C-P3.2-B`). It remains an
explicit argument rather than a default because this is temporary migration
input, not portal configuration or an ongoing Google dependency. Before the
first run, the operator must still visually verify that the selected legacy
spreadsheet contains that exact tab; the command never contacts Google merely to
discover or choose a tab.

The report is counts, the run id and what happens next. It contains no player
name, no Discord name, no snowflake and no Sheet cell — the evidence is reviewed
at R-28, behind Council authorization, which is where the personal data belongs.

### Exit codes

| Code | Meaning | What to do |
|---|---|---|
| `0` | the run committed | review it at `/v1/council/identity-migration` |
| `1` | **refused**; nothing was written | see the refusals below |
| `2` | configuration, credential or Sheet layout refused | fix the named variable or column |
| `3` | the Sheet could not be read | network, permission, quota, spreadsheet id |
| `4` | the database could not be reached or refused the work | check PostgreSQL and `WEB_DATABASE_URL` |
| `5` | another writer conflicted | re-run once the other change finishes |

### The three refusals, and their remedies

Each abandons the transaction before it commits, so **no partial run survives a
refusal** — there is no run row, no proposal and no control total for the problem
to hide in.

| Refusal | Meaning | Remedy |
|---|---|---|
| **duplicate player names** | two player-tab rows share one name, comparing the way the resolver does (NFC-normalised, case-folded) — `Ada` and `ADA`. The platform cannot tell which person a character's *Player Name* refers to, and it will not decide that by which row came second | resolve the duplicate **in the spreadsheet**, then re-run. Nothing in this workflow writes to Google, so the platform does not do it for you. The message names counts only |
| **unmapped source rows** | a `Characters` row the Phase 2 import never mapped, so no bucket can hold it | run the Phase 2 character import, then re-run |
| **unbalanced totals** | the buckets do not account for every source row | a defect; report it. PostgreSQL refuses to store such a run independently |

## 4. Verify, then retire

The migration is not finished when C-04 exits `0`. Its end state is Google being
gone.

1. **Verify in PostgreSQL.** Check the run's control totals against the
   spreadsheet, and spot-check per-character resolutions and candidate sets. §7.4
   requires every source row to land in exactly one bucket, and the report shows
   both sides of the arithmetic so it can be checked by reading it.
2. **Council decides.** Each proposal is confirmed or rejected individually at
   R-28. A confirmation creates the link immediately; a wrong one is revoked
   through R-26, which keeps the historical row and its reason.
3. **Hold the legacy access only for the approved verification/rollback window**
   recorded with the gate. Rolling back needs nothing undone in Google, because
   nothing was ever done to it.
4. **Retire it.** Revoke the read-only service account's access to the
   spreadsheet, delete the service account, remove
   `SHEET_READONLY_SERVICE_ACCOUNT_JSON` from the environment, and destroy the
   operator virtualenv. `.agents/AGENTS.md` requires the Google credentials to be
   removed once Sheets is retired; this is the P3.2 half of that.

Record the retirement date and who performed it. A credential that is merely
unused is not retired.

## 5. What this command never does

- it never writes to Google, in any mode, by any path;
- it never creates a `character_access` row or any authorization — the schema
  refuses one on every row it can write;
- it never reads a game-state column: only `Characters C` and the player tab's
  `A`, `B` and `D` (migration contract §9);
- it never derives capability from a Sheet value. `Active DM` is recorded as
  reconciliation evidence and read by no capability decision (OD-18);
- it never resolves an ambiguity by choosing. Two matching guild members means
  every candidate is recorded and none is chosen, and the proposal cannot be
  confirmed until it resolves to one snowflake.
