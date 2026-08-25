# Operations — offline Foundry snapshot import

Status: **Phase 2 working document.** The procedure below is the deliverable;
**no real import is authorized during development.** The maintainer-supervised
rehearsal against the real snapshot is a separate review-gate check.

Related: [export contract](../rules/foundry-export-contract.md),
[field profile](../rules/field-ownership.md),
[ADR 0006](../adr/0006-foundry-integration-boundary.md),
[database development](database-development.md).

## 1. What the Manager touches, and what it does not

| Does | Does not |
|---|---|
| read one artifact file a Council member exported | connect to Foundry, ever |
| verify its SHA-256 before parsing it | open a Foundry world directory or LevelDB |
| write PostgreSQL inside one transaction | write anything to Foundry |
| record checksum, folder, profile, actor, time, result | write Google Sheets |

Phase 2 makes no network call at all. If an import appears to need one,
something is wrong with the invocation, not with the world.

## 2. Producing the artifact (Guild Council)

**The supported workflow is direct submission from the Foundry module**, which
needs no file, no SSH and no server path. It is documented separately in
[foundry-snapshot-submission.md](foundry-snapshot-submission.md); read that
first. A submitted snapshot is already stored and already has a checksum and
provenance row, so §3 below is only the file-based fallback.

The rest of this section is that **fallback**, for when the endpoint is
unavailable or a submission needs diagnosing:

1. In the Foundry client, press *Submit Freedom Blades Snapshot* and choose
   **Download JSON** instead of Submit. The bytes are the same validated,
   checksummed document the submission would have sent.
2. Select the folder to export. The initial one is `Characters (active)`.
3. Keep the file name the module generated, or rename it to a plain name ending
   in `.json` — no directories, no second extension.
   `the-guild-2026-08-02.json` is a good name; `snapshot.json.exe` and
   `../snapshot.json` are refused.
4. Hand the file to the operator over a channel the Council is comfortable
   with. It contains every exported Actor's mechanics, so treat it as an
   operational record, not as a chat attachment.

`Export to Compendium` is **not** this, and the `Actors (shared)` compendium is
**not** a source: it is a copy that may be stale. The module reads the live
world.

Never commit an artifact to this repository. `.gitignore` excludes
`fvtt-Actor-*.json`, and committed fixtures are synthetic by construction.

## 3. Rehearsing the import (operator)

```bash
APP_ENVIRONMENT=development \
DATABASE_URL='postgresql+psycopg:///freedom_dev' \
  ./venv/bin/python -m tools.bootstrap_manager \
    --snapshot /srv/freedom-blades/snapshots/the-guild-2026-08-02.json
```

A rehearsal parses, validates, reconciles and prints a report. It writes
nothing — not a character, not a mapping, not a snapshot row.

Read the report before doing anything else:

- **errors** block the whole run. An import is all-or-nothing;
- **`unmapped_name_collision`** means an Actor with no mapping carries a name
  the platform already holds. Establish the mapping deliberately — never let
  the importer guess;
- **`foundry_out_of_date`** means the database and the Foundry Actor disagree
  on a field the *platform* authors, so the Foundry Actor has drifted from it.
  Somebody should update the **Foundry** Actor. The platform writes nothing
  back. No field carries this direction in Phase 2; the code exists for the
  fields later packages migrate;
- **`platform_display_name_stale`** means the Actor was **renamed in Foundry**
  and the platform's display record still holds the earlier name. Foundry is
  where a character is renamed, so Foundry is correct and the platform copy is
  the stale one. **Do not rename the Foundry Actor back.** Identity is the
  external Actor id, so the character stays mapped to the same Actor (OD-42),
  and Phase 2 reports the rename without updating anything — the display record
  is corrected by the package that owns it (5.1);
- **`unable_to_compare`** is neither agreement nor disagreement. The commonest
  causes are a field never bootstrapped, a multiclassed Actor, a nonzero
  electrum balance, and an item with no stable catalogue identity;
- **`absent_from_snapshot`** means a mapped character's Actor is not in this
  folder. Nothing is deleted, deactivated or unmapped;
- **`unknown_snapshot_path`** means the Actor carries a field the profile does
  not classify. It is reported and is never written. Classify it in
  `domain/foundry_profile.py` and `docs/rules/field-ownership.md` before
  relying on it.

## 4. The one-time supervised bootstrap

```bash
APP_ENVIRONMENT=staging \
DATABASE_URL='postgresql+psycopg:///freedom_staging' \
  ./venv/bin/python -m tools.bootstrap_manager \
    --snapshot /srv/freedom-blades/snapshots/the-guild-2026-08-02.json \
    --bootstrap --supervisor "Peter Duscha"
```

Preconditions, each enforced rather than trusted:

| Precondition | Enforced by |
|---|---|
| the target is the approved database for `APP_ENVIRONMENT` | `adapters/database/config.py`, before connecting |
| a supervisor is named | `SupervisedBootstrap`, which refuses a blank name |
| the bootstrap flag is explicit | `--supervisor` alone runs a rehearsal |
| the dataset is uninitialized | a query inside the applying transaction |
| it never runs twice | the `platform_initialization` singleton row |

After the first success the path closes permanently. Later imports require one
currently authorized Guild Council member; the bootstrap is not a way around
that and cannot be re-enabled by the application. Re-opening it is a
database-owner action against `platform_initialization`, which the runtime role
cannot perform and which the operations log must record.

## 5. Later imports

A later snapshot is a **new immutable record and an explicit reconciliation
event**, not a replacement for the first. Council triggers it; triggering it is
the authorization event and no second approval is required.

Re-applying the same artifact to the same folder under the same profile version
is a **successful no-op**: the database's partial unique index on
(snapshot, folder, profile version) makes a second apply impossible, and the
service returns a typed duplicate result.

### What a duplicate result contains, and what it deliberately does not

A duplicate is the **original import's own result**, read back from the
immutable `snapshot_imports` row: its import id, correlation id, operation
digest, counts and the reconciliation summary that import recorded. It is not a
fresh reconciliation, and reading it as one is the mistake to avoid — a
reconciliation run today reports the imported Actors as *already mapped*,
because the import mapped them, while the original correctly reported them as
create candidates.

So a duplicate has **no per-issue report**. `python -m tools.bootstrap_manager`
prints the recorded counts and the recorded issue *codes* for it, and names the
import they came from. If you need the narrative detail of what an import saw at
the time, it is in that run's output; if you need to know what the database
looks like now, run a rehearsal (no `--bootstrap`), which reconciles and writes
nothing.

## 5a. What identifies an attempt in permanent history

Three identifiers appear in audit rows, and they answer different questions:

| Identifier | Answers | Notes |
|---|---|---|
| `correlation_id` | which events belong to **this attempt** | new for every attempt, including a retry |
| `operation_digest` | **what was applied** — checksum, world, folder id and path, profile version, exporter | excludes the request key and the volatile aggregate versions |
| `request_key_digest` | which attempts share a **request key** | a one-way, domain-separated SHA-256 of the key |

The request key itself is caller-supplied text. It is stored verbatim in exactly
one place — `snapshot_imports.request_key`, because an exact match is what the
idempotency lookup does — and **never** in an audit payload, an import summary or
a refusal message. To find the audit history for a key you hold, digest it the
same way the application does:

```bash
./venv/bin/python -c \
  'import sys; from application.foundry.import_service import request_key_digest; \
   print(request_key_digest(sys.argv[1]))' "$REQUEST_KEY"
```

Do not paste a request key into a ticket, a chat channel or a shell history file
if it might carry a person's name or anything else private. The platform stops
it reaching permanent history; it cannot stop an operator copying it somewhere
else. A refused attempt is recorded under `refused:<digest>:<correlation id>`,
which keeps two refusals of one key distinct without keeping the text.

## 6. Snapshot retention — documented separately from the audit record

Two different things, with two different lifetimes:

| Record | Lifetime | Who may read it |
|---|---|---|
| checksum, provenance, counts, reconciliation summary, audit events | **permanent**, append-only | Guild Council and Platform Administrators |
| the raw artifact bytes | retained only as long as an operational need exists | Platform Administrators, on the host |

Audit visibility does **not** by itself grant permission to download the raw
artifact. The `foundry_snapshots.artifact_location` column holds a reference
into a restricted store, never the bytes, and no application route serves them.

Store artifacts under a directory readable only by the service account, with
the host's encrypted-backup treatment. When an artifact is deleted, its
checksum and audit record remain: the platform can still say which snapshot a
character came from, without holding the document.

## 7. Rollback and recovery

**Roll back first, restore second.** In order of preference:

1. **A refused or blocked import needs no recovery.** It committed nothing.
   Fix the reported issue and import again; the refused attempt does not block
   the retry.
2. **A failed apply rolls back completely.** The snapshot record, created
   characters, mappings, the import record and the success audit are one
   transaction. After the rollback, at most one safe attempted/refused record
   exists, under the same correlation ID. The previous database state is fully
   usable.
3. **An unwanted but successful import** is undone by a deliberate Council
   action against the affected characters and mappings — never by deleting the
   import's own record. Snapshot and import rows are append-only in the
   database, and deleting one would destroy the evidence of what happened.
   Note that an import creates identity and mappings only: it writes no
   character game-state field, so there is no game state to unwind.
4. **Database-level recovery** — a corrupted database, not an unwanted import —
   uses the documented backup restore in
   [database-development.md](database-development.md) and
   `infra/postgresql/backup-restore-drill.sh`. Take a backup **before** running
   migrations or a bootstrap.

Exceptional owner recovery of an append-only table requires disabling its
trigger explicitly:

```sql
-- As the schema owner, deliberately, and recorded in the operations log.
ALTER TABLE snapshot_imports DISABLE TRIGGER snapshot_imports_append_only;
-- … the corrective statement …
ALTER TABLE snapshot_imports ENABLE TRIGGER snapshot_imports_append_only;
```

This is outside the application and cannot be presented as ordinary history.
The runtime role has no `UPDATE`, `DELETE` or `TRUNCATE` on those tables and
therefore cannot reach this path at all.

## 7a. Where an artifact came from

`foundry_snapshots.received_via` distinguishes the two chains of custody, and
`submitted_by_principal` names the credential on the second:

| `received_via` | Means | Attribution |
|---|---|---|
| `operator` | a file placed on the host and imported with `tools.bootstrap_manager` | the operator who ran the command, plus `received_by_discord_user_id` where one applies |
| `foundry_module` | an HTTPS submission from the Foundry module | `submitted_by_principal` — there is no acting Discord user on that path |

A database check constraint keeps the pair consistent in both directions, so a
row can never claim a chain of custody it did not have. Both columns are
append-only along with the rest of the table.

## 8. Migrations

Migration `0004_snapshot_submission_provenance` adds `received_via` and
`submitted_by_principal`; see
[foundry-snapshot-submission.md](foundry-snapshot-submission.md) §9 for its
upgrade, downgrade and recovery notes.

Migration `0002_foundry_snapshot_and_identity` adds the snapshot, import and
initialization tables, the provenance columns on `external_actor_mappings`, and
the append-only triggers on `audit_events`, `foundry_snapshots` and
`snapshot_imports`.

It **replaced** an earlier uncommitted `0002` that also created
`character_state_values`, `character_balances` and `character_transactions`.
ADR 0008 was rejected on 2026-08-02, and because that revision existed neither
in committed history nor in a durable environment it was replaced in place
rather than corrected by a follow-on migration. If you have a database that was
built with the earlier revision, recreate it rather than migrating it: it is a
development or disposable database by definition, since the revision never
reached staging or production.

```bash
# Always back up first.
pg_dump --format=custom --file=/srv/backups/pre-0002.dump freedom_staging

APP_ENVIRONMENT=staging DATABASE_URL='postgresql+psycopg:///freedom_staging' \
  ./venv/bin/alembic upgrade head

# Then apply the runtime grants as the schema owner.
sed 's/__APP_ROLE__/freedom_staging_app/' \
  infra/postgresql/runtime-grants.sql.tmpl | psql freedom_staging
```

`alembic downgrade 0001` reverses it, dropping the triggers first and then the
tables. Downgrading discards Phase 2 data by design; take the backup.

## 9. What to check after an import

- the reconciliation report was read and its warnings understood;
- `snapshot_imports` has exactly one `applied` row for the input;
- `foundry_snapshots.checksum` matches the artifact you were handed
  (`sha256sum` it);
- every created character has a mapping whose
  `established_by_snapshot_id` points at that snapshot; and
- the audit events carry the acting user, the capability, the correlation ID
  and the checksum; and
- no audit payload contains a raw request key — it carries
  `request_key_digest` and `operation_digest` instead (§5a).
