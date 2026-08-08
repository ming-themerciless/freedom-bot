# Phase 2 I-03 — Foundry v14 snapshot submission vertical slice

Implementation handoff.

Date: 2026-08-04

Implementing agent and working Technical Lead: Claude

Branch: `docs/platform-plan`, `HEAD` at `c8a3da9`. **Nothing was committed or
pushed.** The working tree carries this package on top of the reviewed,
uncommitted Phase 2 remediation, which was preserved untouched.

**This is a recommendation, not an approval.** It claims no Phase 2, Phase 3 or
Phase 7 gate criterion. Peter Duscha remains Product Owner, Data Owner,
Operations Owner and Acceptance Authority.

Package plan and impact assessment:
[`phase-2-i-03-package-plan.md`](phase-2-i-03-package-plan.md).

---

## 1. Implemented workflow

```text
Foundry GM opens the Actor Directory
  → "Submit Freedom Blades Snapshot"
  → selects one Actor folder: full path, stable ID, Actor count, sub-folder count
  → sees the running deployment tuple beside the configured one
  → Submit  (or Download JSON as a fallback)
  → the module builds and validates the entire bundle locally
  → SHA-256 over the exact UTF-8 bytes
  → HTTPS POST of those exact bytes, bounded timeout, derived idempotency key
  → the server authenticates a submit-only service principal
  → the server independently validates size, checksum, canonical form, schema,
    deployment tuple, folder graph and Actor identity
  → the artifact is stored under its own checksum in restricted storage
  → pending provenance is recorded; snapshot id, checksum and count returned
  → the module shows a bounded receipt: no Actor name, mechanic or raw JSON
  → a currently authorized Council member previews it (contract implemented)
  → a separate, explicit confirmation invokes the existing apply service
```

No SSH. No server filesystem path. No manual file placement. No Foundry document
is created, updated or deleted at any point.

### Scope exclusions

- **No Phase 3 portal**: no OAuth, sessions, cookies, CSRF, templates, static
  assets or member pages.
- **No production server process.** The WSGI application exists;
  `tools/snapshot_api.py` serves it for supervised rehearsals only, on loopback.
  Phase 3's `freedom-web` is the production process. ADR 0009 records why.
- **The Council preview route is inert in production.** With no Phase 3
  authorization composition it answers `503 authentication_unavailable` and
  reaches no application service. Authentication was **not** faked.
- **No live Foundry connection**, no Foundry write-back, no character game-state
  field, no raw-artifact download route, no directory listing, and no apply from
  the service credential.

---

## 2. Every changed file

### New — Foundry module (`foundry-module/`)

| File | Purpose |
|---|---|
| `module.json` | v14 manifest, compatibility `14`–`14.365`, `dnd5e` ≥ `5.3.3` |
| `package.json` | declares `"type": "module"` only — no dependency, lockfile, install or build step |
| `scripts/canonical.js` | canonical JSON encoding (contract §1). Pure |
| `scripts/bundle.js` | bundle assembly and every structural bound. Pure |
| `scripts/transport.js` | SHA-256, HTTPS upload, derived idempotency key. Pure |
| `scripts/workflow.js` | the order the steps happen in. Pure |
| `scripts/world-source.js` | **the only file that reads Foundry** |
| `scripts/settings.js` | world-scoped configuration |
| `scripts/main.js` | Actor Directory button, dialog, notifications |
| `styles/freedom-blades-export.css` | local CSS; no font, CDN or image |
| `tests/*.test.mjs`, `tests/fixtures.mjs`, `tests/emit-golden.mjs` | 72 tests under `node --test`; the golden emitter feeds the Python contract test |
| `README.md` | layout, authority boundary, API table |

### New — application layer

| File | Purpose |
|---|---|
| `application/artifacts.py` | the artifact-store port: `store`, `load`, `contains`. No list, delete or open |
| `application/idempotency.py` | `IdempotencyRecord`, key validation, request hashing |
| `application/service_principals.py` | `ServicePrincipal`, `ServicePrincipalScope` (one scope) |
| `application/foundry/submission.py` | the submission use case |
| `application/foundry/preview_service.py` | Council-authorized preview of a pending snapshot |

### New — adapters and operator entry point

| File | Purpose |
|---|---|
| `adapters/artifacts/filesystem.py` | content-addressed store: atomic write, containment, verification, cleanup |
| `adapters/http/wsgi.py` | the two routes |
| `adapters/http/credentials.py` | bearer credential → scoped principal |
| `adapters/http/composition.py` | the composition root; no production preview service |
| `tools/snapshot_api.py` | loopback-only rehearsal server |

### New — migration and tests

| File | Purpose |
|---|---|
| `migrations/versions/0004_snapshot_submission_provenance.py` | `received_via`, `submitted_by_principal` + two check constraints |
| `tests/test_artifact_store.py` (16) | storage naming, containment, atomicity, permissions, cleanup |
| `tests/test_snapshot_submission.py` (46) | the use case, end to end, with fakes |
| `tests/test_http_submission.py` (49) | credentials, limits, safe errors, preview gate |
| `tests/test_snapshot_preview_service.py` (10) | preview authorization and read-only behaviour |
| `tests/test_exporter_contract.py` (10) | the cross-language contract |
| `tests/test_submission_database.py` (16) | PostgreSQL constraints, concurrency, append-only |

### Modified

| File | Change |
|---|---|
| `application/snapshots.py` | `SnapshotSource` enum; `received_via` and `submitted_by_principal` on `SnapshotRecord`, with both-directions validation |
| `application/repositories.py` | `IdempotencyRepository` protocol; added to `UnitOfWork` |
| `application/foundry/audit_policy.py` | two new action policies and their written data classification |
| `adapters/database/tables.py` | the two columns and their check constraints |
| `adapters/database/repositories.py` | `SqlAlchemyIdempotencyRepository`; the two columns in the snapshot repository |
| `adapters/database/unit_of_work.py` | wires the idempotency repository into the one shared session |
| `tests/fakes.py` | `FakeIdempotencyRepository`, with the adapter's own rule name |
| `.env.example` | `FREEDOM_SNAPSHOT_ARTIFACT_ROOT`, `FREEDOM_SNAPSHOT_PRINCIPALS` |
| `docs/rules/foundry-export-contract.md` | §0.1 the implementation and transport; §5 fixtures; §6 selection scope |
| `docs/operations/foundry-snapshot-import.md` | submission is the supported route; download is the fallback; §7a provenance |
| `docs/operations/topology.md` | §6a addendum: the new outbound-to-inbound path, limits and the Phase 3 blocker |
| `docs/adr/README.md` | ADR 0009 indexed as **Accepted 2026-08-04** |
| `docs/project-management/{change-log,status,raid-register}.md` | C-3 entry and impact assessment; **C-4**, the ADR 0009 acceptance; status row; risks R-10, R-11, R-12 |
| `docs/adr/0009-…md` | **Accepted 2026-08-04** (change-log C-4), with the limits of that acceptance stated in the status line |

### New — documentation

`docs/adr/0009-snapshot-submission-http-boundary.md`,
`docs/operations/foundry-snapshot-submission.md`,
`docs/review/phase-2-i-03-package-plan.md`,
`docs/review/phase-2-i-03-prompt.md` (the preserved implementation prompt),
`docs/review/phase-2-i-03-review-request.md` (the standalone review request),
`docs/review/Handover information` (the consolidated handover), this file.

### `docs/review/Handover information`

`phase-2-submission.md` records what this file is: the maintainer's working
exchange channel, *"a scratch channel, not a record"*. It was rewritten twice on
2026-08-04 at the maintainer's direction, and each time the content it replaced
was preserved under the repository's naming convention first — the file is
tracked-and-modified, so an overwrite destroys content no `git` operation can
restore.

| It held | Preserved as |
|---|---|
| the implementation prompt for this package | [`phase-2-i-03-prompt.md`](phase-2-i-03-prompt.md) |
| the standalone independent-review request | [`phase-2-i-03-review-request.md`](phase-2-i-03-review-request.md) |

It now holds the **consolidated handover**: current state, what was decided and
by whom, the defect found by running it, the recommended sequencing, and the
review request reproduced in full so it is self-contained.

### Preserved, not mine

The uncommitted Phase 2 remediation — `migrations/versions/0003_import_operation_digest.py`,
`adapters/database/translation.py`, `application/foundry/audit_policy.py` and the
`phase-2-remediation-*` review records — is intact. The only edit to any of it is
the two added audit policies and their written data classification, which is this
package's own change.

---

## 3. Foundry v14 public APIs used

Every one verified against the installed Foundry **14.365.0** application source
on this host, not from memory. The prohibited sources — world storage, LevelDB
and compendium packs — were **not** read; only the application's own JavaScript
was inspected.

| API | Verified in |
|---|---|
| `game.actors` | `client/game.mjs` (the world `Actors` collection) |
| `game.folders` | `client/game.mjs` (the world `Folders` collection) |
| `game.world.id`, `game.world.title` | `client/game.mjs`, `foundry.packages.World` |
| `game.version` | `client/game.mjs` — `get version()` returns `release.version` |
| `game.system.id`, `game.system.version` | `client/game.mjs` |
| `game.user.isGM` | `common/documents/user.mjs` |
| `game.settings.register` / `get` / `set` | `client/helpers/client-settings.mjs` |
| world setting write permission | `common/documents/setting.mjs` — `canUserCreate` requires `SETTINGS_MODIFY` |
| `Document#toObject()` | `common/abstract/document.mjs` |
| `Document#testUserPermission(user, "OWNER")` | `common/abstract/document.mjs` |
| `Folder#folder` (parent), `Folder#type` | `client/documents/folder.mjs` |
| `foundry.utils.saveDataToFile(data, type, filename)` | `client/utils/helpers.mjs` |
| `foundry.applications.api.DialogV2.wait` | `client/applications/api/dialog.mjs` |
| `Hooks.on("renderActorDirectory", …)` | `client/applications/api/application.mjs` dispatches `render{ClassName}` with `(application, element, context, options)` |
| `ui.notifications.*` | `client/ui.mjs` |

No private underscored internal is used where a public API exists.

---

## 4. Authorization boundaries

Four authorities, kept apart in code and in documentation.

| Authority | May | May not |
|---|---|---|
| Foundry GM | read and submit the selected folder | anything on the platform |
| the submit-only service principal | upload one snapshot | apply, read Council data, read audit history, mutate a character, reach PostgreSQL |
| a Guild Council member | preview a pending snapshot; separately, apply it | change a Foundry Actor |
| a Platform Administrator | operate the service, rotate credentials, manage retention | apply an import unless also Guild Council |

- **A Foundry GM role is not proof of Discord Guild Council membership.** The
  module says so in its dialog; the operations document says so in a table; and
  nothing in the code converts one into the other.
- The module additionally checks `testUserPermission(user, "OWNER")` **per
  Actor**, so "full access to every selected Actor" is established against each
  document rather than assumed from the role.
- `ServicePrincipalScope` has exactly one member. `submit()` requires it before
  anything else happens — before the bytes are read, hashed or parsed.
- `SnapshotPreviewService` resolves Council authority through the existing
  `AuthorizationPort` **at the moment of the call**, and the existing
  `SnapshotImportService.apply` resolves it again when it commits. A role
  revoked in between refuses the apply.
- A Platform Administrator alone is refused the preview
  (`test_a_platform_administrator_alone_is_refused`).

---

## 5. Wire protocol, idempotency and checksums

```http
POST /api/v1/foundry/snapshots
Authorization: Bearer <principal id>.<secret>
Content-Type: application/json
Content-Length: <bytes>
Idempotency-Key: foundry-module:<checksum>
X-Snapshot-SHA256: <client checksum>
```

`201` on a first submission, `200` on a duplicate — nothing was created by a
duplicate, and a client treating `201` as "new" would otherwise be misled.
The receipt carries snapshot id, checksum, size, Actor count, world id, exporter,
canonical-encoding flag, correlation id, duplicate flag, and each selected
folder's id, path and Actor count. **No Actor name or mechanic.**

- **The client is not believed about anything except the bytes.** The server
  computes its own SHA-256 over what arrived and refuses a mismatch with
  `checksum_mismatch`; the claim is compared to, never used as, the identity.
  Actor counts, folder paths, the world and the exporter all come from the
  server's own parse. There is no filename in the protocol at all.
- **The idempotency key is derived from the checksum**, not random, so a retry
  after a network failure is a retry rather than a second submission.
- Same key + same bytes → the **original stored receipt**, read back from
  `idempotency_keys.response`. Nothing is recomputed, so a retry cannot describe
  a different instant from the submission it names.
- Same key + different bytes → `409 request_key_conflict`. Nothing stored.
- Same bytes + different key → one artifact, one `foundry_snapshots` row, two
  receipts. The second reports `duplicate: true`.
- A lost race is resolved by **re-reading the winner** in a fresh transaction,
  never assumed from the rule name. A `PersistenceError` is never resolved into
  a duplicate; an unresolvable conflict is `409 concurrent_submission`.
- `Content-Length` is required (`411` otherwise): the size bound must hold
  before the first byte is buffered. One byte past the declared length is read,
  so a body longer or shorter than it claimed is refused rather than truncated
  and hashed.

---

## 6. Storage and retention

- Root is configured, absolute, and **refused if it is inside this repository** —
  an artifact holds every exported Actor's mechanics and must never be one
  `git add -A` from being committed.
- Files are named for their own SHA-256. A caller cannot influence the name at
  all; `SnapshotArtifact.source_name` is deliberately ignored.
- Root `0700`, artifacts `0600`, with the mode set on the temporary file
  *before* any byte is written, so content is never briefly world-readable.
- Write is atomic: temporary file in the same directory, `fsync`, verify the
  written bytes against the checksum, then `os.replace`, then `fsync` the
  directory. Every failure path removes the temporary file.
- Storing the same bytes twice is one file and one reference.
- `foundry_snapshots.artifact_location` holds an opaque `snapshot/<checksum>.json`
  reference — **not** a host path, because import history is readable by anyone
  who can read audit records.
- **No delete, no listing, no path accessor on the port.** Retention is an
  operator action against the filesystem; the checksum and audit record survive
  it, and a preview of a deleted artifact refuses with `snapshot_not_held`.

---

## 7. Migration, configuration and deployment

**Migration `0004_snapshot_submission_provenance`** — additive and reversible.
Adds `received_via` (default `operator`, which is truthfully how every existing
row arrived) and `submitted_by_principal`, plus two check constraints making the
pair consistent in both directions. No applied migration was edited. No table is
created or dropped, so `infra/postgresql/runtime-grants.sql.tmpl` is unchanged
and does not need reapplying. `foundry_snapshots` remains append-only, proven
against PostgreSQL. **Downgrading discards provenance** — take a backup.

**Configuration** — two new variables, documented in `.env.example` and the
operations guide: `FREEDOM_SNAPSHOT_ARTIFACT_ROOT` (required, absolute, outside
the repository) and `FREEDOM_SNAPSHOT_PRINCIPALS` (the SHA-256 **digest** of each
secret, never the secret). An empty value is valid and means "revoke
everything".

**Deployment** — Caddy must allow a 64 MiB body on this route and a read timeout
above the module's 120 s upload timeout; the snippet is in the operations guide.
Installation is copying `foundry-module/` into `Data/modules/`; there is no build
step. Rollback is disabling or deleting the module, which affects no Foundry
document because none was ever written.

---

## 8. Commands run, and their exact results

All run from `/opt/discord-bots/freedom-bot` with
`TEST_DATABASE_URL=postgresql+psycopg:///freedom_test` where a database was
needed. In the order the prompt specifies.

```text
1. cd foundry-module && node --test "tests/*.test.mjs"
   72 tests, 72 pass, 0 fail, 0 skipped

2. pytest -q tests/test_artifact_store.py tests/test_snapshot_submission.py \
       tests/test_http_submission.py tests/test_snapshot_preview_service.py \
       tests/test_exporter_contract.py
   131 passed in 0.40s

3. pytest -q tests/test_snapshot_artifact.py tests/test_snapshot_parser.py \
       tests/test_snapshot_import_service.py tests/test_snapshot_reconciliation.py \
       tests/test_snapshot_extraction.py tests/test_audit_payload_policy.py
   315 passed in 0.57s

4. pytest -q -m database
   233 passed, 1482 deselected, 1 warning in 7.91s

5. pytest -q -rs                       (the full configured suite)
   1715 passed, 1 warning in 9.96s     (no skips)
   Baseline without this package's six new test files: 1568 passed.
   This package adds 147 Python tests and 72 JavaScript tests.

6. formatter / linter / type checker
   NOT CONFIGURED. ruff, black, flake8, mypy, pyright, eslint and prettier are
   all absent, and the repository has no pyproject.toml, setup.cfg, .flake8,
   mypy.ini or eslint config. Nothing was installed or configured, because
   introducing a toolchain is a separate decision.
   Substitute performed: node --check on all 14 module and test files — all ok.

7. ./venv/bin/python -m compileall -q application adapters domain tools tests migrations
   passed

8. APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test'
   alembic upgrade head       → 0004 applied
   alembic downgrade 0003     → 1 downgrade executed
   alembic upgrade head       → 1 upgrade executed
   alembic check              → "No new upgrade operations detected."

9. git diff --check
   passed, no whitespace errors

10. repository-source scan (source text only)
    - no artifact, dump, snapshot or .json export is tracked or untracked
    - no private key, service-account payload or bearer token in new files
      (the only hits repository-wide are pre-existing variable names in
      adapters/sheets/read_only.py and a synthetic "not-a-key" placeholder in
      tests/test_import_cli.py)
    - no new Python module references leveldb, a compendium, /home/foundry,
      worlds/ or game.packs
    - no outbound network call in any new Python module
    - the only logging in new code is adapters.safe_logging.log_expected_failure,
      which records a fixed category and an exception class name and nothing else
    - a test asserts the same property for the JavaScript
      (world-source.test.mjs, "no module source reads the filesystem, LevelDB or
      a compendium")
```

The single warning is the pre-existing `discord.player` `audioop` deprecation.

---

## 8a. A defect found by running it, and fixed

**The first real HTTP request to the endpoint hung.** It was found by starting
the rehearsal server and submitting a synthetic bundle with `curl` — not by any
test, because no test could have caught it.

`adapters/http/wsgi.py` read `Content-Length + 1` bytes, so that a body longer
than it claimed could be refused rather than silently truncated. Against
`io.BytesIO`, which every test used, that returns a short read at end of file
and the extra byte simply is not there. Against a real server it does not:
`wsgiref.simple_server` hands over the **raw socket** as `wsgi.input`, and a
read for one byte past the body blocks until the peer sends something or the
connection dies. PEP 3333 is explicit that an application "should not attempt to
read more data than is specified by the `CONTENT_LENGTH` variable" — a server
*may* bound the stream, and is not required to. `wsgiref.validate` does not
bound it either, so the validator did not catch it.

**Fix.** `_read_exactly` reads in bounded chunks up to `Content-Length` and never
requests more. A short read is still reported as `incomplete_body`. Detecting an
over-long body is dropped, because an application cannot do it without
committing the over-read that caused this: framing belongs to the server and the
proxy, which treat trailing bytes as the next request on the connection and
reject them.

**Regression cover.** `test_the_body_is_never_read_past_its_declared_length`
drives the application with an `_UnboundedInput` double — a stream that raises
on an over-read instead of blocking, which is what a real socket does — so the
PEP 3333 rule is now asserted rather than assumed.
`test_trailing_bytes_still_cannot_forge_a_checksum` shows the declared prefix is
what gets hashed.

**Nothing was committed or stored by the hung request**: zero snapshot rows,
zero artifacts, verified afterwards.

**Second, minor:** `tools/snapshot_api.py` printed its startup banner without
flushing, so an operator redirecting stdout to a log saw nothing at all — not
even whether the process had started — until it exited. Now flushed.

### End-to-end verification after the fix

Rehearsal server on loopback, `freedom_test`, a synthetic bundle from the
committed fixtures, an artifact root in a temporary directory:

| Request | Result |
|---|---|
| first submission | `201`, receipt with checksum, `actor_count: 1`, folder path, `duplicate: false` |
| retry, same key and bytes | `200`, `duplicate: true`, same `snapshot_id` and `correlation_id` |
| same bytes, different key | `200`, `duplicate: true` — one artifact, one row |
| wrong secret | `401 unauthenticated` |
| wrong claimed checksum | `400 checksum_mismatch` |
| wrong content type | `415 unsupported_media_type` |
| preview route | `503 authentication_unavailable` |

Resulting state: **one** artifact file, `0600`, in a `0700` root, named for its
own SHA-256; **one** `foundry_snapshots` row with `received_via =
foundry_module` and `submitted_by_principal = foundry-the-guild`; `characters`,
`external_actor_mappings` and `snapshot_imports` all **zero**; three audit
events, all `service_principal` / `foundry` with no Discord user. The server log
contained no secret, no path and no Actor value. The disposable database and the
artifact were then cleared.

## 9. Not run, and not claimed

- **Neither maintainer-supervised rehearsal was performed.** Rehearsal A
  (inactive-folder transport) and Rehearsal B (formal active-folder Phase 2 gate)
  are documented procedures in
  `docs/operations/foundry-snapshot-submission.md` §6 and §7. No real Foundry
  export was produced, submitted, previewed or applied.
- **The manual Foundry smoke test was not run.** The Actor Directory button, the
  dialog and the browser download need a running Foundry client. The checklist is
  §8 of the same document. Everything beneath the UI is covered by automated
  tests.
- **No formatter, linter or type checker exists to run** (item 6 above).
- **No commit and no push.**
- No production data, credential or player record was read, used or written.
- The prohibited Foundry sources were not accessed. The Foundry *application*
  source was read to verify API names, which is not world data.

---

## 10. Residual risks and decisions for Peter Duscha

| # | Decision or risk | Recommendation |
|---|---|---|
| 1 | ~~**ADR 0009** — a stdlib WSGI adapter rather than the FastAPI stack~~ | **Closed 2026-08-04: accepted** by Peter Duscha (change-log C-4). The architectural decision only; this implementation is still unreviewed, and no further HTTP surface is authorized |
| 2 | **No production server process.** The endpoint runs only under the loopback rehearsal server until Phase 3 delivers `freedom-web` | Confirm that the rehearsal server is acceptable for Rehearsal A, and that production exposure waits for Phase 3 |
| 3 | **The Council preview route is inert.** It needs the Phase 3 Discord-authenticated boundary and answers `503` without it | Confirm that failing closed is preferred to any interim authentication. Authentication was not faked |
| 4 | **A configuration-supplied credential rather than a `service_principals` table** (plan §7.1) | Confirm. A database-backed principal needs create/scope/revoke administration, which is Phase 3 work. Rotation and revocation are documented and testable today |
| 5 | **Artifact retention.** No period is set; deletion is a manual operator action | Set a retention period, or record that artifacts are retained until a named operational trigger. R-10 |
| 6 | **Artifact backup treatment.** The store must be in the host's encrypted backups, and such a backup holds Actor mechanics | Confirm the store's path is covered and encrypted |
| 7 | **Proxy limits.** Caddy must allow 64 MiB and a read timeout above 120 s on this route | Apply the documented snippet before Rehearsal A, or a legitimate submission is cut off with no explanation |
| 8 | **The preview response is bounded to the reconciliation summary**, not the per-Actor narrative. Council members are entitled to more; how much a web response should carry is Phase 3's rendering and authorization work | Confirm the interim bound, or direct that Phase 3 widen it |
| 9 | **The request-key digest is unkeyed**, exactly as the accepted import-path equivalent. A short guessable key can be confirmed by anyone who guesses it | No change recommended. The module derives its key from the checksum, so it is not human-chosen |
| 10 | **One folder per export.** The contract permits 1–8 and the parser still supports that range | Confirm. Multi-folder selection has no unambiguous import semantics today |

---

## 11. Review requested

Under implementation plan §0.3 and §16.4, this package touches
import/reconciliation, authentication and authorization, and a first HTTP
boundary. It therefore needs **two reviews, by someone other than the
implementer**, and neither has been performed:

1. **Independent implementation review.** Suggested focus:
   - the submission service's conflict resolution and idempotency — in
     particular that no `PersistenceError` can become a duplicate receipt, and
     that a retry's receipt is read rather than recomputed;
   - the ordering in `_store_and_record`: artifact before database row, and what
     each crash point leaves behind;
   - the export contract's canonical encoding, implemented twice, and whether
     `tests/test_exporter_contract.py` is a sufficient anti-drift control;
   - the direct-membership Actor scope (package plan D4) against contract §2.6;
   - migration `0004`'s constraints, and that `foundry_snapshots` is still
     append-only under them.

2. **Separate security-focused review.** Suggested focus:
   - the credential construction: plain SHA-256 over a ≥32-character generated
     secret, constant-time comparison, and the fixed-dummy comparison for an
     unknown principal id — is the reasoning in `adapters/http/credentials.py`
     sound, and is a single undifferentiated authentication failure the right
     call?
   - that authentication failures are deliberately **not** audited, so an
     anonymous caller cannot append to permanent history;
   - the request-bounding order in `wsgi.py`, and whether anything can be
     buffered before the size bound holds;
   - the two new audit payload policies and their data classification;
   - artifact storage permissions, containment, and the absence of any route
     that serves an artifact;
   - the module's failure paths, and that no `fetch` or driver message text
     reaches a Foundry notification.

Blocking findings in security, data integrity, authorization, migration or
atomicity must be fixed and re-reviewed before this package is accepted. The
Acceptance Authority records the decision; passing tests do not close a gate.
