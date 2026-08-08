# Independent implementation review — Phase 2 I-03

Reviewer: Codex, Independent Reviewer
Date: 2026-08-04
State reviewed: uncommitted working tree on `docs/platform-plan`, `HEAD` at `c8a3da9`

## Recommendation

**Do not proceed to either supervised rehearsal.** The implementation has one
Blocking production-reliability finding. It must be fixed and independently
re-reviewed first. This is a recommendation only; Peter Duscha remains the
Acceptance Authority.

## Findings

### B-1 — Blocking — The supported browser workflow cannot pass a CORS preflight

The module sends the snapshot from the Foundry browser client with `fetch`, to a
configured HTTPS API URL, using `Authorization`, `Content-Type: application/json`,
`Idempotency-Key`, and `X-Snapshot-SHA256` headers
(`foundry-module/scripts/main.js:205-211`,
`foundry-module/scripts/transport.js:129-144`). Unless Foundry and the platform
are served from the same origin, this is a CORS-preflighted cross-origin request.

The WSGI application deliberately emits no `Access-Control-Allow-Origin`
(`adapters/http/wsgi.py:85-96`), has no preflight headers, and returns 405 for
`OPTIONS /api/v1/foundry/snapshots` (`adapters/http/wsgi.py:165-170`). The test
suite enshrines the absence of CORS rather than exercising a browser preflight
(`tests/test_http_submission.py:172`). The implementer's real-HTTP exercise used
`curl`, which does not enforce browser CORS, so it could not expose this class of
failure.

Impact: the primary supported direct-submission workflow fails in the deployed
cross-origin topology before the authenticated POST reaches application code.
This is production reliability and is Blocking under plan §16.4.

Required remediation: define the permitted Foundry origin(s), answer a bounded
unauthenticated `OPTIONS` preflight for this route, allow exactly the required
method and request headers, and emit the matching origin on the POST response.
Add an HTTP contract test that reproduces a browser preflight and an operational
test from the actual Foundry browser origin. Do not use an unrestricted reflected
origin. Reconcile the Caddy configuration and the security review with the chosen
policy.

### I-1 — Important — Failure responses make a false claim about artifact state

The chosen ordering stores the content-addressed artifact before the database
transaction commits (`application/foundry/submission.py:550-639`). Therefore a
database failure or crash after `artifacts.store()` may leave an orphaned artifact
with no database row; the package plan explicitly accepts that outcome.

The HTTP `database_unavailable` response nevertheless says “nothing was stored”
(`adapters/http/wsgi.py:281-287`), and the operations table makes the same claim
for both storage and database failures
(`docs/operations/foundry-snapshot-submission.md:247-255`). This is not merely
wording: it gives operators the wrong incident and retention model. The generic
500 response makes the same assertion even though an unexpected exception may
also occur after the artifact write (`adapters/http/wsgi.py:140-151`).

Required remediation: say that no submission was *recorded or confirmed* and
that retrying the same key is safe; do not claim the artifact filesystem is
unchanged. Document how orphaned content-addressed files are identified and
handled under the eventual retention policy.

### I-2 — Important — Directory durability failures are silently reported as success

The store describes the write as durable, but `_fsync_directory()` suppresses
both failure to open the directory and failure of `fsync`
(`adapters/artifacts/filesystem.py:204-215`). After `os.replace`, submission can
therefore proceed to a durable database commit even though persistence of the
directory entry was not established. A power loss can then leave a row whose
artifact rename was not durable—the exact state the store-first ordering is meant
to prevent.

Required remediation: treat a supported-filesystem directory-sync failure as an
artifact storage failure, or explicitly narrow and test the durability guarantee
for filesystems where directory sync is unavailable. Add injected open/fsync
failure tests covering the post-rename outcome and ensure the database cannot be
confirmed on an unacknowledged durability failure.

## Governance and scope assessment

No Phase 2, Phase 3, or Phase 7 gate criterion is actually claimed by the
submission. Bringing forward the read-only submission half of the Phase 7 module
does not introduce Foundry write-back, name-based identity, LevelDB access, or
platform-initiated Foundry access. Phase 2 still depends on the supervised
active-folder rehearsal and Data Owner attestation; Phase 3 still owns the real
web process and Discord-authenticated composition; Phase 7 still owns outbound
integration.

The accepted ADR 0009 boundary is respected in structure: the WSGI adapter is
transport code and the submission use case remains framework-independent. The
inert preview route is genuinely inert in the production composition
(`adapters/http/composition.py:84-96`), but it is still a second HTTP route even
though ADR 0009 says it “authorizes no further HTTP surface: a second route is a
new decision.” Peter should reconcile that textual scope mismatch before this
route becomes anything other than inert. I do not treat the inert route itself
as a Phase 3 surface or a blocking implementation defect.

## Other conclusions

- Artifact-before-row is the safer of the two non-transactional orderings. An
  orphan is recoverable and content-addressed; a committed row pointing at bytes
  never written is not.
- `PersistenceError` is not resolved as a duplicate. Only named uniqueness
  conflicts enter the replay branches.
- Stored receipt decoding is appropriately strict about keys and basic types,
  and replay changes only the attempt-relative `duplicate` field.
- The `0004` migration is additive and its operator/module provenance
  biconditional matches the two currently supported ingestion routes. Its
  downgrade data loss is documented.
- Direct-child folder selection is consistent with contract §2.6 and is made
  visible to the operator. It is a product choice, not a contract defect.

## Verification boundary

I inspected repository source and records only. I did not access Foundry world
storage, LevelDB, or compendium data; did not run Rehearsal A or B; and did not
commit or push. The package's reported automated results are useful evidence,
but they do not cover the browser-origin integration in B-1.
