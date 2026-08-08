# Independent review request — Phase 2 I-03, Foundry snapshot submission

Prepared for: **Codex, as Independent Reviewer**
Prepared by: Claude, working Technical Lead and implementer of this work
Requested by: Peter Duscha, Acceptance Authority
Date: 2026-08-04
State under review: the **uncommitted working tree** on branch
`docs/platform-plan`, `HEAD` at `c8a3da9`. Nothing was committed or pushed.

The implementation prompt this work was built from is preserved verbatim at
[`phase-2-i-03-prompt.md`](phase-2-i-03-prompt.md).

---

## 1. Your role, and its limits

You are the **Independent Reviewer** required by implementation plan §16.4. This
package touches three of its named checkpoints at once — *import/reconciliation*,
*authentication and authorization*, and the *Foundry connector* — so plan §0.3
applies in full: a reviewer who did not implement the work is **required**, and
if none is available the package stays `deferred`. It is not approved on the
implementer's own recommendation.

You are also asked for a **separate, separately reported security-focused pass**.
Please keep the two reports distinct rather than merging them; a security concern
absorbed into a general review is easy to lose. Suggested filenames, matching the
existing convention:

- `docs/review/phase-2-i-03-codex-review.md`
- `docs/review/phase-2-i-03-codex-security-review.md`

**You recommend; you do not approve.** Peter Duscha records the decision. Please
do not implement fixes — report findings and let the implementer address them, so
the re-review has something independent to check.

Classify every finding per plan §16.4:

- **Blocking** — security, data loss, authorization, rule correctness, migration,
  atomicity or production reliability;
- **Important** — material maintainability, testing, performance or operational
  weakness;
- **Optional** — improvement that does not block the milestone.

Blocking findings must be fixed and re-reviewed before dependent work starts.

### Do not

- **Do not run either rehearsal** in `docs/operations/foundry-snapshot-submission.md`
  §6 or §7. Both require the maintainer present and use the real world.
- **Do not access the prohibited Foundry sources**: world storage,
  `/home/foundry/shared/worlds`, LevelDB, or any compendium pack. Inspect
  repository source text only. (Reading the Foundry *application* JavaScript to
  verify an API name is permitted and is what the implementer did.)
- **Do not commit or push.**
- **Do not decide the open questions in §9.** They are Peter's.

---

## 2. What this work is, in one paragraph

A Foundry v14 module lets an authorized user select one Actor folder and submit
its immutable snapshot to the platform over HTTPS — no SSH, no server filesystem
path, no manual file placement. The server authenticates a submit-only service
principal, independently re-validates the bytes against the accepted export
contract, stores the artifact in restricted content-addressed storage, and
records **pending provenance**. It applies nothing: preview and apply remain the
existing Council-authorized services, unchanged. The artifact format is
`docs/rules/foundry-export-contract.md` v1, unchanged — only its *transport*
is new.

## 3. What to read

**Governing, in this order:**

1. `.agents/AGENTS.md`
2. `docs/implementation-plan.md` §§6.3–6.5, §7.1, §9.1–9.3, §12 Phase 2,
   §12 Phase 3, §12 Phase 7, §12.0, §13.3, §16.4
3. `docs/rules/foundry-export-contract.md` — especially the new §0.1 and §6
4. `docs/adr/0006-foundry-integration-boundary.md` (accepted, amended)
5. `docs/adr/0002-web-application-stack.md` (accepted) and
   `docs/adr/0009-snapshot-submission-http-boundary.md` (**accepted 2026-08-04**)

**This package:**

6. `docs/review/phase-2-i-03-package-plan.md` — scope, the phase-boundary impact
   assessment, and the seven decisions taken inside the maintainer's authority
   (D1–D7)
7. `docs/review/phase-2-i-03-submission.md` — the evidence record: every changed
   file, the exact commands and results, **§8a the defect found by running it**,
   and §10 the residual risks
8. `docs/operations/foundry-snapshot-submission.md` — installation, credential
   issue/rotation/revocation, proxy limits, storage and retention, the §5.8 smoke
   test, both rehearsals and the manual smoke checklist
9. `docs/project-management/change-log.md` entries **C-3** (the package and its
   impact assessment) and **C-4** (the ADR 0009 acceptance)

**The code**, roughly in dependency order:

```text
application/artifacts.py                  the storage port
application/idempotency.py                key, request hash, stored receipt
application/service_principals.py         scopes
application/foundry/submission.py         the use case          (~740 lines)
application/foundry/preview_service.py    Council preview contract
adapters/artifacts/filesystem.py          the store
adapters/http/credentials.py              credential → principal
adapters/http/wsgi.py                     the two routes
adapters/http/composition.py              the composition root
tools/snapshot_api.py                     loopback rehearsal server
migrations/versions/0004_snapshot_submission_provenance.py
foundry-module/scripts/*.js               the exporter
```

---

## 4. The governance question, which matters more than any line of code

**This package moves work across two phase boundaries. Please review that as a
decision, not only the code that implements it.**

1. It brings forward the **read-only submission half** of Phase 7's Foundry
   module and its scoped service credential. Package plan §3.1 tabulates what is
   and is not brought forward, and argues that every property ADR 0006 protects
   is preserved: no LevelDB, no compendium, no platform-initiated Foundry access,
   world-keyed identity, exact (core, system) tuple failing closed, mapping never
   inferred from a name, no write-back.
2. It introduces an **HTTP boundary before Phase 3**, whose gate (§12.0) is what
   releases "production portal integration". Package plan §3.2 argues the surface
   is deliberately not a portal: one bearer-authenticated machine route, no
   cookie/CSRF/OAuth/session/template surface, and a Council preview route that is
   **inert** without a Phase 3 authorization composition.

Please state plainly whether you agree, and in particular:

- Is anything here a Phase 7 or Phase 3 gate criterion being *claimed* rather
  than deferred?
- Does the WSGI adapter constitute framework scaffolding ahead of the Phase 3
  gate, or does it avoid it? ADR 0009 argues the latter and records the
  alternatives, and **was accepted on 2026-08-04** — so the decision is not
  yours to retake. What is still worth your judgement is whether the
  *implementation* stays inside it: whether `adapters/http/` does only transport,
  and whether anything in it has begun to grow into the Phase 3 web application.
- Is the "inert preview route" honest, or is it a partially-built authentication
  surface that Phase 3 will have to reconcile? The implementer's claim is that
  `build_application` passes `preview=None, preview_user_resolver=None` and there
  is **no** environment variable or code path that supplies them in production.

---

## 5. Implementation review — specific things to attack

These are the implementer's own hypotheses about where this is most likely to be
wrong. Please treat them as leads, not as a scope limit.

### 5.1 The defect found by running it, and its class

**Read `docs/review/phase-2-i-03-submission.md` §8a first.** The endpoint hung on
its first real HTTP request. `adapters/http/wsgi.py` read `Content-Length + 1`
bytes to detect an over-long body; under `io.BytesIO` — which all 49 HTTP tests
used — that returns short at EOF, and under `wsgiref`'s raw socket it blocks
forever. PEP 3333 forbids reading past `CONTENT_LENGTH`. `wsgiref.validate` did
not catch it either.

It is fixed (`_read_exactly`, `wsgi.py:360`) and has a regression test that uses
a stream which *raises* on over-read rather than blocking.

**The question this raises is the more important one: where else does a test
double stand in for real I/O, and hide a difference that matters?** Candidates
the implementer is aware of and could not fully rule out:

- `tests/fakes.py` `FakeUnitOfWork` vs. a real PostgreSQL transaction — the
  concurrency tests in `tests/test_submission_database.py` are the intended
  mitigation; are they sufficient?
- `FilesystemArtifactStore` against a real filesystem — `tmp_path` is real, but
  no test exercises a full disk, a read-only mount, or `fsync` failure;
- the Foundry module's fake `game` in `foundry-module/tests/fixtures.mjs` — it
  implements only the surface `world-source.js` reads. A real `game.actors`
  entry is a `Document` with behaviour the double does not have.

### 5.2 Idempotency, conflicts and the receipt

`application/foundry/submission.py`, `_persist` (477), `_store_and_record` (532),
`_replay_stored` (642), `_replay` (704).

- Can a `PersistenceError` ever be resolved into a duplicate receipt? The
  intent, following the accepted import-path reasoning, is **never**.
- The checksum-conflict path retries `_store_and_record` **once** and then falls
  through to the key-conflict branch. Is single retry correct, or is there an
  interleaving where it returns the wrong answer or loops?
- A retry's receipt is read from `idempotency_keys.response` and never
  recomputed (this is the shape finding B-1R required on the import path). Is
  `SubmissionReceipt.from_payload` strict enough that a corrupted stored receipt
  fails closed rather than being patched up?
- `_replay` sets `duplicate=True` on a value otherwise reconstructed from the
  stored payload. Is that the only field that legitimately describes *this
  attempt* rather than the original?

### 5.3 Ordering, and what each crash point leaves behind

`_store_and_record` stores the artifact **before** committing the row (package
plan D5). Please walk the crash points:

- between `artifacts.store()` and `commit()` → an orphaned, content-addressed
  file and **no** database claim. Re-submission re-stores it harmlessly. Is that
  right, and is the orphan ever a problem?
- the reverse order was rejected because it can commit a row pointing at bytes
  that were never written. Agreed?
- the refusal record is written in a **separate** transaction after rollback, and
  its failure is deliberately swallowed (`_record_refusal`). Is swallowing right,
  or does it lose evidence that matters?

### 5.4 The export contract, implemented twice

`foundry-module/scripts/canonical.js` and `bundle.js` reimplement, in JavaScript,
rules that `application/foundry/parser.py` enforces in Python.

- Is `tests/test_exporter_contract.py` a sufficient anti-drift control? It runs
  the exporter's real serialization path and feeds the output to the real parser,
  and asserts the bytes equal the Python canonical encoding. It **skips** if
  `node` is absent — is a skip here acceptable, or should it fail?
- `compareCodePoints` sorts by code point rather than UTF-16 code unit. Foundry
  keys are currently ASCII, so this is untested in production data. Is the
  implementation correct for surrogate pairs?
- Package plan **D4**: Actor scope is *direct children* of the selected folder,
  because contract §2.6 requires every Actor's `folderId` to be in
  `selectedFolderIds`. Is that reading of the contract right, and is showing the
  sub-folder count to the operator sufficient mitigation for the surprise?

### 5.5 Migration `0004`

- `received_via` defaults to `operator`, asserted to be truthful for every
  existing row. Verify.
- The two check constraints make `received_via`/`submitted_by_principal`
  consistent in both directions. Is the biconditional right, or does it forbid a
  legitimate future case?
- `foundry_snapshots` is append-only via a trigger from `0002`. Does adding
  columns weaken that? `tests/test_submission_database.py` asserts
  `UPDATE`/`DELETE` still fail. No runtime grant changed — confirm none was
  needed.
- Downgrade discards provenance. Is that documented adequately, and is
  upgrade/downgrade/upgrade genuinely clean?

### 5.6 Reuse, not duplication

Plan requires the web adapter to reuse existing authorization and reconciliation
services rather than restate their rules. `SnapshotPreviewService` is intended to
be a thin join. Is any rule restated anywhere — in the preview service, the WSGI
adapter, or the module?

---

## 6. Security review — specific things to attack

### 6.1 The credential

`adapters/http/credentials.py`.

- **Plain SHA-256** over a ≥32-character generated secret, not a password KDF.
  The argument (module docstring) is that this is high-entropy machine-generated
  material, not a human-chosen password, and that a deliberately slow hash on a
  per-request path is a denial-of-service lever. Is that sound?
- `MIN_SECRET_LENGTH` (61) is enforced at issue **and** at presentation, so a
  short secret cannot authenticate even if somehow configured. Verify.
- `authenticate` (144) compares against `_DUMMY_DIGEST` (67) when the principal
  id is unknown, so an unknown id costs the same as a wrong secret. Is the
  timing actually equalised, or does the dictionary lookup or the `partition`
  leak?
- Every failure — unknown id, wrong secret, malformed header, short secret —
  raises one undifferentiated error. Right call, or unhelpfully opaque?
- Is `<id>.<secret>` a sound credential format? Note the id may contain no `.`
  by construction; confirm that is enforced.

### 6.2 Authentication failures are deliberately not audited

An unauthenticated request writes **nothing**, on the grounds that append-only
history should not be an anonymous append channel. The trade-off is that
credential-guessing leaves no audit trail; the intent is that the reverse proxy's
access log and rate limiting own that. **Is this the right call?** If not, it is
a Blocking finding.

### 6.3 The request-bounding order

`adapters/http/wsgi.py` `_submit` (184). The intended order is: authenticate →
content type → idempotency key → declared length → bounded read. Please check
that nothing is buffered, hashed or parsed before the size bound holds, and that
no path reads `wsgi.input` unbounded.

Also: `Content-Length` is required and chunked bodies are refused with `411`.
Is that correct behind Caddy, and does it close the bound-before-read hole?

### 6.4 Audit content

Two new policies in `application/foundry/audit_policy.py`, enforced at the point
of writing by `enforced()`. Every allowed key has a written data classification,
and an existing test asserts the documentation covers them.

- Is any key a free-text channel wearing a vocabulary's name? Specifically
  `service_principal_id` (operator-chosen, validated to an id shape) and
  `artifact_code` (asserted equal to the parser's own code set by an AST walk in
  `tests/test_snapshot_submission.py`).
- The request key never reaches an audit row; a domain-separated
  `request_key_digest` does, distinct from the import path's. Confirm.
- Does any refusal path put a message, a path or an artifact byte into a payload?

### 6.5 Artifact storage

`adapters/artifacts/filesystem.py`.

- Names are derived from content, never from a caller. `source_name` is ignored.
  Is containment (`_path_for`) actually unreachable-by-construction, and is the
  check still worth keeping?
- Root `0700`, files `0600`, mode set at `os.open` so content is never briefly
  world-readable. Verify.
- Atomic write: temp in the same directory, `fsync`, verify bytes against the
  checksum, `os.replace` (142), `fsync` the directory. Any window where a
  partial or unverified file is visible under the checksum name?
- The port has no `list`, `delete` or `open`, and no route serves an artifact.
  Is there any other way bytes reach a caller?
- The store refuses a root inside the repository. Sufficient to keep artifacts
  out of Git?

### 6.6 The module, on clients the platform does not control

- Settings are `scope: "world"`, so writes are server-enforced by Foundry's
  `SETTINGS_MODIFY` permission, and `config: false` so the credential is never
  rendered into a settings sheet. Is that the right storage for a credential at
  all, given a GM's browser can read it?
- `main.js` builds dialog content as DOM nodes with `textContent`, because
  `DialogV2` sanitises rather than escapes. Any remaining injection path from a
  folder name?
- Does any notification, console message or thrown error carry an Actor name, a
  mechanic, raw JSON, the credential or an internal path? `notifyFailure`
  deliberately reports unknown exceptions as a category only.
- HTTPS is required with a loopback exception. Is the exception safely bounded?

---

## 7. Reproducing the verification

```bash
cd /opt/discord-bots/freedom-bot

# 1. exporter (72 tests, no npm, no install)
(cd foundry-module && node --test "tests/*.test.mjs")

# 2. this package's Python tests (147)
TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv/bin/python -m pytest -q \
  tests/test_artifact_store.py tests/test_snapshot_submission.py \
  tests/test_http_submission.py tests/test_snapshot_preview_service.py \
  tests/test_exporter_contract.py tests/test_submission_database.py

# 3. the full configured suite (1717, no skips)
TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv/bin/python -m pytest -q -rs

# 4. compileall, migration consistency, whitespace
./venv/bin/python -m compileall -q application adapters domain tools tests migrations
APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv/bin/alembic check
git diff --check
```

The optional end-to-end smoke test is
`docs/operations/foundry-snapshot-submission.md` §5.8 — loopback only,
`freedom_test`, synthetic fixtures, with cleanup. It is safe to run and was run
by the implementer; it is what surfaced §8a.

**No formatter, linter or type checker is configured in this repository** — ruff,
black, flake8, mypy, pyright, eslint and prettier are all absent and there is no
config file for any of them. Nothing was installed. `node --check` on all 14
JavaScript files was used as a substitute. If you think this package should ship
with one configured, that is an Important finding worth making.

---

## 8. What was not done, and is not claimed

- **Neither rehearsal was run.** No real Foundry export was produced, submitted,
  previewed or applied. No real Actor data was read or written at any point.
- **The manual Foundry smoke test was not run** — the Actor Directory button, the
  dialog and the download fallback need a running client
  (`foundry-snapshot-submission.md` §8).
- **There is no production server process.** The WSGI application exists;
  `tools/snapshot_api.py` is a loopback-only rehearsal server. Phase 3's
  `freedom-web` is the production process.
- **Nothing was committed or pushed.**
- No Phase 2, Phase 3 or Phase 7 gate criterion is claimed. The Phase 2 gate
  still requires the supervised active-folder rehearsal and the Data Owner
  attestation.

## 9. Decisions reserved to Peter Duscha

Please comment on these if you have a view, but do **not** decide them:

ADR 0009 was decided on 2026-08-04 and has left this list.

| # | Decision |
|---|---|
| 2 | Whether a configuration-supplied credential is acceptable in place of the `service_principals` table plan §7.1 lists |
| 3 | Artifact retention period, and confirmation that the store is in encrypted backups |
| 4 | Whether the bounded preview response (reconciliation summary, not the per-Actor narrative) is the right interim |
| 5 | One folder per export, where the contract permits 1–8 |
| 6 | Whether the rehearsal server is acceptable for Rehearsal A, or that must wait for `freedom-web` |

The full list with the implementer's recommendations is
`docs/review/phase-2-i-03-submission.md` §10.

---

## 10. Sequencing note for the Acceptance Authority

The implementer's recommendation is that **this review precedes both rehearsals
and any production configuration change**. The reason is not caution for its own
sake: a Blocking finding that changes the wire protocol, the storage layout or
the provenance columns would invalidate rehearsal evidence gathered beforehand
and require it to be redone with the maintainer present a second time. The §5.8
smoke test is the exception — disposable, synthetic, reversible, and useful to
run first because it gives the reviewer a known-working baseline.
