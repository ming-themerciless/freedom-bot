# Claude implementation handoff — Foundry v14 snapshot submission vertical slice

You are the implementing agent and working Technical Lead for the next scoped
Freedom Blades package in:

`/opt/discord-bots/freedom-bot`

Implement a production-shaped, read-only Foundry VTT v14 snapshot exporter and
the narrow platform ingestion/preview path it needs. A user must be able to
select an Actor folder in Foundry and submit its immutable snapshot directly to
the Freedom Blades server without SSH, without locating a Foundry database, and
without manually placing a file on the server.

Do not commit or push. Peter Duscha remains Product Owner, Data Owner,
Operations Owner and Acceptance Authority. You recommend; you do not approve a
gate.

## 1. Read before planning or editing

Read these files completely:

1. `AGENTS.md`
2. `.agents/AGENTS.md`
3. `docs/implementation-plan.md`
4. `docs/rules/foundry-export-contract.md`
5. `docs/rules/field-ownership.md`
6. `docs/adr/0006-foundry-integration-boundary.md`
7. `docs/operations/foundry-snapshot-import.md`
8. `docs/operations/database-development.md`
9. `docs/review/phase-2-remediation-3-submission.md`
10. `docs/review/phase-2-remediation-3-codex-re-review.md`
11. `docs/review/phase-2-remediation-3-codex-security-re-review.md`
12. the complete existing artifact, parser, reconciliation, authorization,
    audit, repository, database and bootstrap paths and their tests

Inspect `git status` first. The working tree contains intentional, reviewed,
uncommitted Phase 2 remediation. Preserve every unrelated change. Do not reset,
discard, commit, push or rewrite existing migrations.

Before implementation, produce a concise package plan and impact assessment.
This work brings forward a narrow read-only part of the later Foundry connector
and introduces a web/API boundary. Record the required controlled plan/change
documentation rather than silently pretending the phase boundary did not
change. Stop for maintainer direction only if a decision materially changes
data ownership, authorization, production behavior or the accepted export
contract beyond what is explicitly decided below.

## 2. Maintainer decisions for this package

These decisions are explicit:

- Real Actor exports must **never be committed to Git**, embedded in tests,
  copied into documentation, printed in logs, or included in review evidence.
- Actor mechanics are campaign data, not production financial or personal
  records. They still receive ordinary access control and data minimisation,
  but do not invent a stronger secrecy claim than the maintainer has made.
- Automated unit/contract tests remain deterministic and synthetic.
- A maintainer-supervised integration rehearsal may use a real export from a
  selected non-live folder such as `Characters (inactive)` against the
  disposable `freedom_test` environment. Ordinary pytest runs must not depend
  on that data and may erase it.
- The formal Phase 2 gate rehearsal still separately requires a read-only
  preview accounting for every Actor in `Characters (active)`. An inactive
  folder rehearsal does not satisfy that gate.
- The Foundry module must allow the operator to select the Actor folder. Do not
  hard-code `Characters (active)` or `Characters (inactive)`.
- Export/submission is read-only in Foundry. Nothing in this package may create,
  update or delete an Actor, Item, Folder, Compendium, setting containing Actor
  data, or any other Foundry document.
- Do not use the existing `Actors (shared)` compendium as the source. It is a
  copy that may be stale. Do not modify or delete it.
- Do not read Foundry LevelDB, world storage or compendium files. The shared
  physical host does not weaken this boundary.
- Direct HTTPS submission is the primary workflow. Browser download may be
  provided as an explicit fallback and diagnostic path, but manual server file
  placement is not the supported user workflow.
- Snapshot submission never applies character or mapping changes. It creates a
  pending immutable artifact/provenance record and makes a reconciliation
  preview available. Apply remains a distinct, explicitly confirmed,
  currently-authorized Council action.
- The Foundry submitter is a narrowly scoped service principal. It can submit a
  snapshot only; it cannot apply imports, read Council data, mutate characters,
  search audit history, or access PostgreSQL directly.

## 3. Supported baseline

The observed supported deployment is:

- Foundry VTT `14.365`
- `dnd5e` system `5.3.3`
- world ID `the-guild`
- initial active folder name `Characters (active)`
- observed active folder ID `smob5eya6XVBAuIb`

Validate the actual runtime tuple and export it as provenance. Treat these as
the currently supported compatibility tuple, not as values to fabricate when
the runtime differs. An unsupported tuple fails before Actor bytes are sent.

## 4. Required user workflow

Deliver this end-to-end flow:

```text
Authorized Foundry user opens the Actor Directory
  -> presses "Submit Freedom Blades Snapshot"
  -> selects one Actor folder and sees its full path, stable ID and Actor count
  -> chooses Submit (or Download JSON fallback)
  -> module builds the canonical bundle from supported Foundry document APIs
  -> module calculates the SHA-256 of the exact UTF-8 bytes
  -> module uploads those exact bytes over HTTPS to its configured endpoint
  -> server authenticates the scoped Foundry service principal
  -> server independently validates size, checksum, canonical form and schema
  -> server stores the immutable artifact in restricted artifact storage
  -> server records pending provenance and returns snapshot ID/checksum/count
  -> module displays a bounded success receipt without Actor names or mechanics
  -> an authorized Council user opens the website/API preview for that snapshot
  -> the platform reconciles without applying character or mapping changes
  -> a later, separate confirmation invokes the existing safe apply service
```

No step requires SSH. No user supplies a server filesystem path. Do not build a
server-side picker that exposes host paths.

## 5. Foundry v14 module

Create the module under the repository's planned `foundry-module/` boundary.
Use a valid `module.json`, plain JavaScript compatible with Foundry v14, local
templates/CSS only where useful, and no npm, bundler, SPA framework, CDN,
tracker or runtime dependency.

Use only supported public Foundry v14 APIs. Verify API names against official
v14 documentation or the installed v14 runtime before relying on them. Expected
concepts include `game.actors`, world `Folder` documents, Actor/Item document
source conversion, Web Crypto and `foundry.utils.saveDataToFile()` for the
fallback. Do not rely on private underscored internals when a public API exists.

The module must:

1. Add a clearly labelled control in an appropriate Actor Directory UI
   location.
2. Fail closed unless the current Foundry user has a role/capability that
   guarantees full access to every selected Actor. Do not claim that a Foundry
   role proves Discord Guild Council membership. Document the boundary.
3. List selectable world Actor folders using stable IDs, full paths and names.
4. Select exactly one folder for the initial vertical slice unless the accepted
   contract and importer already require multiple selection. Do not implement
   ambiguous partial semantics. If supporting the contract's bounded 1–8
   selection is straightforward and fully tested, it is acceptable.
5. Show Actor count and deployment/exporter versions before confirmation.
6. Read the current world Actors directly, not a compendium copy.
7. Include only Actors in the selected scope according to the controlled
   contract's direct/recursive rule. Do not guess; reconcile contract, parser
   and tests.
8. Preserve real stable world Actor IDs. Never match or identify by name.
9. Refuse missing/malformed/duplicate Actor or Folder IDs, missing ancestors,
   parent cycles, ambiguous folders, unreadable Actors and all configured
   limits.
10. Build and validate the entire artifact before upload or download.
11. Calculate SHA-256 over the exact UTF-8 bytes sent/downloaded.
12. Upload with bounded timeout and safe failure handling. A retry must be
    idempotent and must not create duplicate pending artifacts.
13. Never log or display Actor names, mechanics, embedded items, raw JSON,
    credentials or internal paths.
14. Offer an optional browser JSON download of the same validated bytes. It is
    a fallback, not the normal remote-server workflow.
15. Make no Foundry document mutation and no direct database/filesystem call.

The upload endpoint and credential are module configuration, writable only by
an appropriate Foundry administrator. Permit only HTTPS outside an explicit
local-development exception. Never put a real credential in source, manifest,
tests, logs, downloaded artifacts or documentation.

## 6. Exact export contract and canonical bytes

Implement `docs/rules/foundry-export-contract.md` exactly. Do not invent a
parallel format and do not weaken the Python importer to accept exporter bugs.

The top-level keys are exactly:

```json
{
  "schema": "freedom-blades.foundry-export",
  "schemaVersion": 1,
  "exporter": {
    "id": "freedom-blades-export",
    "version": "<module version>"
  },
  "exportedAt": "<RFC 3339 UTC ending Z>",
  "world": {
    "id": "<actual world ID>",
    "title": "<actual world title>",
    "coreVersion": "<actual Foundry version>",
    "systemId": "<actual system ID>",
    "systemVersion": "<actual system version>"
  },
  "selectedFolderIds": [],
  "folders": [],
  "actors": []
}
```

Read the real parser and tests for the exact nested shapes. At minimum:

- include selected folders and all required ancestors;
- include only the accepted Actor keys (`id`, `folderId`, `name`, `system`,
  `items`) unless the controlled contract explicitly says otherwise;
- omit ownership, users, permissions, tokens, scenes, chat and unrelated
  document metadata;
- recursively normalise strings to Unicode NFC;
- recursively sort object keys by Unicode code-point order;
- sort folders and actors ascending by stable ID;
- preserve all other array order reported by Foundry unless the contract says
  otherwise;
- reject `undefined`, functions, symbols, cycles, `NaN`, infinities, negative
  zero and unsupported/non-JSON values rather than silently coercing them;
- serialize compactly with `,` and `:` separators, UTF-8 without BOM, LF and
  exactly one trailing LF;
- enforce depth 64, artifact 64 MiB, folder/ancestor and Actor-count limits
  before transmission;
- ensure validation, checksum, upload and fallback download all use identical
  bytes.

## 7. Server submission boundary

Add the smallest production-shaped HTTP/API surface needed for snapshot
submission and preview. Follow the approved FastAPI/Jinja direction if the web
stack is now present; if it is not yet scaffolded, add only a focused,
independently testable adapter and composition boundary. Do not create a broad
Phase 3 portal as a side effect.

A suitable contract is conceptually:

```http
POST /api/v1/foundry/snapshots
Authorization: Bearer <scoped service credential>
Content-Type: application/json
Idempotency-Key: <opaque generated identifier>
X-Snapshot-SHA256: <client checksum>
```

You may improve the wire shape if there is a concrete security or framework
reason, but document it. Requirements:

- authenticate a dedicated, revocable, constant-time-compared service
  credential or an equivalently narrow mechanism;
- keep credential/configuration at the adapter/composition boundary;
- enforce content type, request-size limit, read timeout and one-document body;
- compute SHA-256 server-side over received bytes and require it to match the
  claimed digest;
- run the existing artifact/parser validation, including canonical encoding,
  deployment, folder, depth and count rules;
- bind idempotency to the exact snapshot checksum and submission operation;
- same key/same bytes returns the original pending receipt;
- same key/different bytes is a safe typed conflict;
- same bytes under another key produces one immutable artifact identity, not a
  duplicate raw copy;
- do not trust filenames, client counts, client folder paths or client metadata
  outside the validated bundle;
- return a bounded JSON receipt containing no Actor names or mechanics;
- use safe error codes/messages without raw payloads, secrets, SQL, paths or
  exception detail;
- do not authorize apply from the service credential;
- add rate/size controls appropriate to a maximum 64 MiB upload, and document
  proxy/body/time limits that must match;
- log only safe category, correlation ID, service-principal ID, checksum and
  bounded result classification.

## 8. Artifact storage and PostgreSQL representation

Do not store the raw Actor bundle in Git or an audit payload. Prefer the
existing design: immutable raw bytes in restricted artifact storage and
PostgreSQL holding the checksum, provenance, storage reference and bounded
facts.

Implement a safe storage adapter with:

- configured absolute storage root outside the repository;
- generated checksum-based name, never a caller filename;
- containment validation;
- restrictive file permissions;
- atomic write (temporary file in the same storage boundary, fsync/replace as
  appropriate);
- exact-byte verification after write;
- idempotent handling of an already stored checksum;
- cleanup of failed temporary writes;
- no directory listing or raw-download endpoint in this package;
- explicit retention/deletion documentation.

If tests need files, use a per-test temporary directory and synthetic bytes.
Never configure tests to scan or ingest an existing export directory.

Reuse or safely extend the current snapshot/import tables and repositories.
Do not create a second competing import model. A submission must be representable
as pending provenance without claiming that an import was applied. Preview must
write no character or mapping state. If a schema change is genuinely required,
add a new follow-on Alembic migration; never edit an applied migration. Explain
upgrade, downgrade and recovery.

The normal automated database remains `freedom_test` and synthetic. A supervised
rehearsal may intentionally load real `Characters (inactive)` data there, with
the understanding that the database is disposable and pytest may erase it.
Never make the full suite depend on that rehearsal state, and never capture it
as a fixture or dump in the repository.

## 9. Preview and authorization

Provide a narrow way for a currently authorized Discord Guild Council user to
request reconciliation of a pending submitted snapshot. Reuse the existing
application authorization and reconciliation services; do not duplicate their
rules in the web adapter.

Keep these authorities separate:

- Foundry role/capability: may read and submit the selected Foundry folder;
- Foundry service principal: may upload a snapshot only;
- Discord Council user: may view/trigger the protected reconciliation preview;
- existing apply authority: may later confirm the exact bound preview.

Platform Administrator alone must not gain game-policy apply authority. A
submission must not apply automatically. Preview must bind checksum, world,
folder ID/path, exporter/profile versions and current aggregate versions so a
stale apply still fails closed under the existing service.

If the complete Discord-authenticated website boundary is not yet available,
do not fake authentication. Deliver the application/API contract with a test
authorization adapter and clearly identify the missing Phase 3 composition as a
blocker to production exposure. The Foundry upload endpoint may still be fully
implemented and exercised in integration tests.

## 10. Tests

All committed tests and fixtures must be synthetic. Add focused tests at each
boundary.

### Exporter tests

Cover at least:

- exact valid bundle shape accepted by the real Python parser;
- selectable folder and full ancestor path;
- duplicate folder names with distinct IDs/parents;
- correct direct/recursive scope;
- real world Actor IDs retained;
- actors outside scope excluded;
- accepted embedded Item shape;
- deterministic canonical object ordering;
- NFC normalization;
- compact separators, UTF-8 without BOM and exact trailing LF;
- required array ordering;
- unsupported deployment tuple;
- empty/ambiguous selection and every folder/Actor/depth/size bound;
- missing/malformed/duplicate IDs, missing ancestors and cycles;
- insufficient Actor read permission;
- invalid JSON-domain values and cyclic objects;
- upload and download receive the exact validated/checksummed bytes;
- upload failure/retry cannot partially submit;
- no Foundry mutation API is invoked;
- no filesystem, LevelDB or compendium source is used.

Keep pure canonical bundle construction separate from Foundry UI integration so
it can be tested without a running Foundry instance. Avoid introducing npm or a
build system merely for tests. Use available runtime tooling where practical;
document any UI behavior requiring a manual Foundry smoke test.

### Server/storage tests

Cover at least:

- authenticated valid submission and bounded receipt;
- missing, invalid, revoked and wrong-scope credential;
- ordinary user/Council credential cannot substitute for service credential;
- wrong content type, empty, malformed, oversized, truncated and slow input;
- claimed/server checksum mismatch;
- noncanonical and unsupported bundle refusal;
- same key/same bytes idempotency;
- same key/different bytes conflict;
- same bytes/different key deduplicated immutable storage;
- concurrent identical and conflicting submissions;
- atomic file write and cleanup after injected failure;
- storage-root containment and caller filename ignored;
- database, storage and audit failure leave no false success or partial state;
- safe logs/errors contain no Actor values, secrets, raw bytes or paths;
- runtime/database constraints for immutable history;
- submission cannot apply, create characters or create mappings;
- authorized preview is read-only and unauthorized/revoked access is denied.

Add one cross-language golden/contract test: a small synthetic artifact emitted
by the exporter's actual pure serialization path must be consumed by the real
Python artifact/parser path. Do not maintain two unrelated hand-written formats
that can drift.

## 11. Manual rehearsals to document, not fabricate

Document two maintainer-run procedures. Do not claim either was run unless the
maintainer actually performs it.

### A. Inactive-folder transport rehearsal

1. Configure the module for a non-production/test ingestion endpoint.
2. Select `Characters (inactive)` or another explicitly chosen non-live folder.
3. Confirm folder ID/path, versions and Actor count.
4. Submit through the module.
5. Confirm server and module checksums match.
6. Preview against the disposable test/rehearsal database.
7. Optionally exercise apply only in the disposable database.
8. Confirm Foundry Actors/items/folders and the compendium are unchanged.
9. Confirm no JSON, dump, logs or Actor content entered Git.
10. Reset/delete disposable database state and raw artifact according to the
    recorded rehearsal decision.

### B. Formal active-folder Phase 2 gate rehearsal

1. Select `Characters (active)`.
2. Submit and run reconciliation preview only in the approved environment.
3. Account for every stable external Actor ID as mapped, create-candidate or
   explicitly unresolved.
4. Resolve or explain every identity discrepancy; require zero unexplained
   discrepancy.
5. Store only the sanitized Data Owner attestation required by the implementation
   plan under `docs/review/`.
6. Do not commit the artifact, names, mechanics, raw report or unnecessary
   player/campaign data.

Inactive-folder evidence proves transport/integration but does not replace the
active-folder gate evidence.

## 12. Documentation and operations

Update the relevant contract, operations, topology, configuration example,
project-management and change-control documents. State clearly:

- the supported workflow is direct module-to-server HTTPS submission;
- browser download is a fallback;
- `Export to Compendium` and `Actors (shared)` are not snapshot submission;
- no SSH or server path is needed;
- neither component reads Foundry storage;
- installation, configuration, credential rotation/revocation and module
  disable/removal rollback;
- proxy/body/time limits and maximum artifact size;
- artifact location, access, retention and deletion;
- pending submission, preview and apply authority separation;
- safe monitoring and operator-visible failure categories;
- test/rehearsal environment cleanup;
- backup/restore and database migration recovery if schema changes.

Do not put an actual endpoint credential, raw snapshot, Actor name, mechanics,
server secret or environment-specific private URL in documentation.

## 13. Verification and handoff

Run, in order:

1. narrow exporter canonicalization/contract tests;
2. narrow server/auth/storage/preview tests;
3. relevant existing artifact/parser/import/reconciliation tests;
4. PostgreSQL integration, concurrency, failure-injection and restricted-role
   tests using only the approved disposable test database;
5. the full configured suite;
6. configured JavaScript/Python formatter, linter and type checks, or explicitly
   state what is not configured;
7. `compileall` for affected Python modules;
8. Alembic consistency and upgrade/downgrade/upgrade if schema changed;
9. `git diff --check`;
10. repository-source diff scan for secrets, real Actor data, unsafe logging,
    raw artifacts, network overreach and prohibited-path access.

Do not access the prohibited Foundry sources while scanning. Inspect repository
source text only.

The handoff must report:

- implemented workflow and scope exclusions;
- every changed file;
- exact Foundry v14 public APIs used;
- service-principal and Council authorization boundaries;
- wire protocol, idempotency and checksum behavior;
- storage and retention behavior;
- migration/configuration/deployment changes;
- exact commands/results, skips, warnings and checks not configured;
- manual smoke/rehearsal steps not run;
- confirmation that no real Actor data or artifact was committed;
- confirmation that no prohibited source, LevelDB or compendium file was read;
- rollback and credential-revocation steps;
- residual risks and decisions requiring Peter Duscha;
- request for independent implementation and separate security-focused review.

Do not claim Phase 2, Phase 3 or Phase 7 approval. Do not perform the real
inactive or active folder rehearsal without the maintainer present. Do not
commit or push.
