# Phase 2 I-03 — Foundry v14 snapshot submission vertical slice

Package plan and impact assessment.

Date: 2026-08-03

Implementing agent and working Technical Lead: Claude (this package)

Acceptance Authority, Product Owner, Data Owner, Operations Owner: Peter Duscha

Status: **plan recorded, implementation delivered, not approved.** This document
is the controlled record the maintainer prompt requires. It recommends; it
closes no gate.

## 1. Outcome

A Foundry user with full access to a chosen Actor folder can submit that
folder's immutable snapshot to the Freedom Blades server from inside Foundry,
over HTTPS, with no SSH, no server filesystem path and no manual file placement.
The server authenticates a narrowly scoped service principal, independently
validates the bytes, stores the immutable artifact, and records **pending
provenance**. Applying an import remains a separate, explicitly confirmed,
currently-authorized Guild Council action.

## 2. Scope

### In scope

| # | Deliverable |
|---|---|
| 1 | `foundry-module/` — a Foundry v14 module: folder selection, canonical bundle construction, SHA-256, HTTPS submission, browser-download fallback |
| 2 | `application/foundry/submission.py` — the framework-free submission use case |
| 3 | `application/artifacts.py` + `adapters/artifacts/filesystem.py` — restricted, content-addressed artifact storage |
| 4 | `adapters/http/` — a dependency-free WSGI adapter exposing `POST /api/v1/foundry/snapshots` |
| 5 | `application/foundry/preview_service.py` — Council-authorized reconciliation preview of a pending submitted snapshot |
| 6 | migration `0004` — submission provenance columns on `foundry_snapshots` |
| 7 | exporter, storage, HTTP, authorization, PostgreSQL and cross-language contract tests |
| 8 | operations, contract, topology, configuration and change-control documentation |

### Explicitly out of scope

- **No Phase 3 portal.** No Discord OAuth, no sessions, no cookies, no CSRF
  surface, no templates, no member pages, no Council UI. The preview route
  refuses to serve until a Phase 3 authentication composition exists.
- **No live Foundry connection from the platform.** Phase 7's connector is not
  brought forward; the platform still never dials Foundry.
- **No Foundry write of any kind.** No document create, update or delete.
- **No character game-state field.** Submission writes identity-free provenance
  only; import continues to write identity, mappings and provenance and nothing
  else.
- **No raw-artifact download route** and no directory listing.
- **No apply from the service credential.**
- **No FastAPI, uvicorn, Jinja2, HTMX, npm, bundler or new runtime dependency.**

## 3. Phase-boundary impact assessment (plan §0.2)

This package moves two things across a phase boundary. Both are recorded here
rather than absorbed silently.

### 3.1 A narrow read-only part of Phase 7 is brought forward

Plan §12 Phase 7 delivers the "minimal versioned Foundry module" and "scoped
service authentication". This package delivers **the read-only submission half
of that module and nothing else**.

| Phase 7 deliverable | This package | Left to Phase 7 |
|---|---|---|
| minimal versioned Foundry module | submission only | live sync, retries, diagnostics |
| scoped service authentication | submit-only scope | any broader scope |
| compatible-version check | validated in module and server | unchanged |
| active-folder character snapshots | operator selects any folder | scheduled/automatic snapshots |
| field-level comparison | reuses the existing Phase 2 reconciliation | Council shared-field proposals |
| Council review for shared fields | not delivered | Phase 6 + Phase 7 |
| sync diagnostics and retry behavior | bounded upload retry only | connector diagnostics |

**Why this is safe to bring forward.** Every property ADR 0006 protects is
preserved: no LevelDB, no compendium, no platform-initiated Foundry access, world
identity keyed on world ID, exact (core, system) tuple validation failing closed,
mapping never inferred from a name, and no write-back. The artifact is the same
contract v1 bundle the accepted Phase 2 parser already validates; only its
*transport* changes, from a hand-carried file to an authenticated HTTPS POST of
the identical bytes.

**What it does not release.** No Phase 7 gate criterion is claimed. The live
connector, bidirectional concerns and Council shared-field proposals remain
unstarted.

### 3.2 A web/API boundary is introduced before Phase 3

Plan §12.0 makes the Phase 3 authentication/security gate the gate that releases
"production portal integration". This package adds an HTTP surface, so the
boundary matters.

The mitigation is that the surface is deliberately **not a portal**:

- exactly one production route, `POST /api/v1/foundry/snapshots`, authenticated
  by a bearer service credential rather than by a browser session — so none of
  the cookie, CSRF, OAuth or session machinery Phase 3 owns is created,
  half-created or bypassed;
- the one Council-authorized route, the reconciliation preview, is **inert
  without a Phase 3 authorization composition**. With none configured the route
  answers `503 authentication_unavailable` and reaches no application service.
  Tests compose a test authorization adapter to prove the contract; production
  cannot;
- no browser-facing surface at all: no HTML, no templates, no static assets, no
  cookies set, no CORS allowance.

**Blocker recorded:** production exposure of the preview route requires the
Phase 3 authentication and authorization composition and its security gate. This
is stated in the operations document and in the handoff.

### 3.3 Assessment against plan §0.2

| Dimension | Assessment |
|---|---|
| Scope | additive; no accepted Phase 2 requirement is withdrawn or weakened |
| Authority | unchanged. Submission ≠ apply. Council authority for apply, and Platform-Administrator/Council separation, are untouched |
| Data ownership | unchanged. No field changes owner; no field moves from `legacy` |
| Privacy | a new persisted artifact class (Actor mechanics at rest) already contemplated by plan §6.4 and by `foundry_snapshots.artifact_location`; retention documented |
| Architecture | one new adapter family (HTTP) and one new port (artifact storage). Dependency direction unchanged: domain imports nothing new |
| Migration | one additive, reversible Alembic revision; no applied migration edited |
| Release criteria | unchanged. Phase 2's gate still requires the supervised active-folder rehearsal and Data Owner attestation |
| Estimate | not re-baselined here; the Delivery Lead owns the forecast |

A new baseline version is **not** claimed. This is an implementation package
whose deliverable is recorded in the change log; the Acceptance Authority decides
whether it amends the Phase 2 or Phase 7 baseline.

## 4. Decisions taken inside the maintainer's authority

These follow directly from the maintainer decisions in the handoff and from
accepted documents. None changes data ownership, authorization, production
behaviour or the export contract.

| # | Decision | Reason |
|---|---|---|
| D1 | The HTTP adapter is a **stdlib WSGI application**, not FastAPI | ADR 0002 names FastAPI for the Phase 3 web application, which is not scaffolded. Adding it now would be framework scaffolding ahead of its gate and a drive-by dependency. WSGI is a stdlib-supported interface (`wsgiref`), needs no dependency, is fully testable, and mounts unchanged behind a Phase 3 FastAPI/uvicorn deployment. Recorded as [ADR 0009](../adr/0009-snapshot-submission-http-boundary.md) |
| D2 | The service credential is **configuration-supplied**, not a `service_principals` table | Plan §7.1 lists the table, but a database-backed principal needs a management surface (create, scope, revoke) that is Phase 3 administration. The handoff explicitly permits "an equivalently narrow mechanism". Rotation and revocation are a configuration change plus reload, documented in operations |
| D3 | The bundle carries **exactly one** selected folder from this module | Export contract §2.5 permits 1–8. The handoff permits one "unless the accepted contract and importer already require multiple selection". The importer selects one folder per import, so a single-folder bundle has no ambiguous semantics. The parser's 1–8 support is untouched and still tested |
| D4 | Actor scope is **direct children of the selected folder**, not recursive | Contract §2.6 requires every Actor's `folderId` to be in `selectedFolderIds`; with one selected folder, a recursive walk would produce Actors whose `folderId` is a sub-folder and the parser would refuse them. Direct membership is the only scope the accepted contract and parser admit. Sub-folders are reported to the operator before submission so an unexpected shape is visible rather than silently dropped |
| D5 | Submission stores the artifact **before** committing the database row | Storage is content-addressed and idempotent, so a crash between the two leaves a re-storable orphan and **no** database claim. The reverse order could leave a committed row pointing at bytes that were never stored |
| D6 | Idempotency reuses the existing `idempotency_keys` table | It already carries `(scope, key)` uniqueness, a 32-byte `request_hash` and a stored `response`, which is exactly "same key/same bytes returns the original receipt; same key/different bytes conflicts". No new table |
| D7 | Foundry role authority is `game.user.isGM` **plus** a per-Actor `testUserPermission(user, "OWNER")` check | A GM role is not proof of Discord Guild Council membership and is documented as a different authority. The per-Actor check is what makes "full access to every selected Actor" true rather than assumed |

## 5. Risks

| # | Risk | Response |
|---|---|---|
| R1 | Artifact at rest holds every exported Actor's mechanics | Restricted root outside the repository, `0700` directory / `0600` files, no download route, no directory listing, documented retention and deletion, checksum and audit survive deletion |
| R2 | A credential leaks from a Foundry client | Scope is submit-only; it cannot apply, read Council data, mutate characters or reach PostgreSQL. Worst case is an unwanted **pending** artifact. Revocation is documented and does not require redeployment |
| R3 | Exporter and Python parser drift | One cross-language contract test feeds the exporter's real serialization output to the real Python parser, and asserts the bytes equal the Python canonical encoding of the same document |
| R4 | An operator submits the wrong folder | Full path, stable ID, Actor count, sub-folder count and the deployment tuple are shown before confirmation; the server binds folder ID *and* path into every preview and apply |
| R5 | A large upload exhausts server memory | Bounded read at the adapter before any buffering, 64 MiB ceiling matching the contract, documented proxy body/time limits that must match |
| R6 | The preview route is exposed without Phase 3 | Fails closed with `503` when no authorization provider is composed; the composition root has no production provider to give it |

## 6. Evidence this package produces, and what it does not

**Produces:** exporter canonicalization and contract tests; storage atomicity,
containment and cleanup tests; HTTP authentication, limit, checksum, idempotency
and concurrency tests; preview authorization tests; PostgreSQL constraint and
append-only evidence; a cross-language golden contract test.

**Does not produce:** the supervised inactive-folder transport rehearsal, the
formal active-folder Phase 2 gate rehearsal, the Data Owner attestation, or any
statement that Phase 2, Phase 3 or Phase 7 may proceed. Both rehearsals are
documented procedures for the maintainer to run, and neither has been run.

## 7. Amendment, 2026-08-04 — independent-review remediation

Independent implementation review (B-1, I-1, I-2) and independent security
review (S-B-1, S-B-2, S-I-1) of this package are recorded in
`phase-2-i-03-codex-review.md` and `phase-2-i-03-codex-security-review.md`. The
remediation is `phase-2-i-03-remediation-submission.md`. Four entries above are
amended by it; none is withdrawn.

| # | Amendment |
|---|---|
| D2 | Unchanged in substance — the principal is still configuration-supplied, submit-only and revocable by reload. What changed is the **other end**: the secret is no longer stored in a Foundry world setting. Foundry 14.365 delivers every world-scoped setting value to every connecting client (`dist/packages/world.mjs`, an unfiltered `Setting.dump()`), and offers no setting option that is a read boundary, so the GM enters the credential per submission and it is persisted nowhere. See operations §4.1 |
| D5 | Reaffirmed, and its accepted consequence is now stated **truthfully everywhere** — see the §8 correction below, which is what "everywhere" turned out to require. Storing before recording does permit a database-unclaimed artifact; responses, notifications, the operator table and the recovery procedure said "nothing was stored", which the failing paths had not established. They now say no submission was *recorded or confirmed*. Operations §5.6 adds a read-only procedure for identifying unclaimed artifacts, and states that deleting them is neither automatic nor yet decided |
| R1 | Strengthened from asserted to **enforced** — and see §8, which found the enforcement itself was made by pathname. The restricted state is checked at startup and re-checked on every store, and an unsafe state is a refusal rather than a silent repair (S-B-2) |
| R2 | Response narrowed and made accurate. The old response was scope containment alone; it did not address a credential *readable by every client of the world*, which is a much larger population than "leaks from a Foundry client" implies. Containment still holds and is still the reason the worst case is bounded, but the exposure itself is now removed rather than tolerated |

**One new entry.**

| # | Item | Response |
|---|---|---|
| D8 | The submission route answers a bounded, allowlisted CORS preflight | The supported workflow is a cross-origin browser `fetch` with four non-safelisted headers, so the browser requires it (B-1). An explicit allowlist of exact origins, `POST` and those four headers only, no cookie authority, no reflection, and no permission for an unlisted origin. Recorded as a clarification on [ADR 0009](../adr/0009-snapshot-submission-http-boundary.md): a preflight is the same route's contract, not a second route |

**One new risk, and it is not closed.**

| # | Risk | Response |
|---|---|---|
| R7 | The browser workflow is still unverified from a real browser | Automated tests reproduce the preflight, and one exercises the endpoint over a real socket. Neither is a browser, and `curl` does not enforce CORS. Operations §8.2 is a maintainer-supervised real-origin check; **it has not been run**, and until it is, B-1 is remediated by construction and test rather than by observation |

## 8. Amendment, 2026-08-04 (second) — I-1 and S-B-2 reopened

The second independent implementation and security re-review found that the §7
remediation did not close two of the six findings. Both entries above are
corrected here rather than rewritten, because what the first attempt got wrong
is itself the evidence for what the second one had to do differently.

| # | Correction |
|---|---|
| D5 | The §7 claim that the wording was truthful **everywhere** was wrong. It was truthful in the places the review had named. `application/foundry/submission.py` still told a caller that nothing was stored on the unresolved-concurrency path — which runs *after* `_store_and_record` — and on both replay paths, which are reachable both before and after the store. `application/artifacts.py` built the sentence into every `ArtifactStorageError`, including `durability_unconfirmed`, whose whole contract is that a correct target may already be published. What a failure claims is now a declared `StorageOutcome` per raise, defaulting to the conservative one, and `tests/test_storage_claim_vocabulary.py` applies the rule to the whole repository so the next occurrence is a failing test rather than a third review finding |
| R1 | The §7 enforcement was real but **pathname-based**, which is a check-then-use race rather than a control: `lstat` the configured path, then create, open, publish and `fsync` through that same path. The root is now opened once with `O_DIRECTORY | O_NOFOLLOW` and every operation resolves its name against that descriptor, so replacing the path redirects nothing. Its type, owner and mode are re-proved through the descriptor on every store and every read; the ancestors that would have to be writable for such a replacement to be staged are refused at startup; and the descriptor's lifetime belongs to the composition root |

**One new item.**

| # | Item | Response |
|---|---|---|
| D9 | The artifact root is anchored for the life of the process | A directory descriptor is the trusted object, not a path. Consequence for operations, documented in §5.6 and `.env.example`: **moving or replacing the artifact root requires a service restart**, and a running service refuses `root_replaced` rather than following the name |

**One new risk, and it is not closed.**

| # | Risk | Response |
|---|---|---|
| R8 | The anchoring is not proven against a real second POSIX account | The automated suite may not create one and must not require privilege, so the substitution is exercised with controlled renames, replacement directories and descriptor inspection. What is established is that a pathname replacement cannot redirect a create, open, publication, read or directory `fsync`, and that unsafe type, owner and mode fail closed as this process observes them. A cross-account experiment on the deployment host is the observation nobody has made, and it is Peter's to schedule if he wants it |

## 9. Amendment, 2026-08-05 (third) — publication, the I-1 default, and test evidence

The third independent implementation and security re-review found the §8 root
anchoring materially correct: creation, reads, publication, `unlink`, `stat` and
directory `fsync` are all resolved relative to the anchored root, and the
pathname-redirection defect is fixed. It returned one Blocking finding and two
Important ones. As in §8, the earlier entries are corrected rather than
rewritten.

| # | Correction |
|---|---|
| D5 | Storing before recording is reaffirmed, and a second consequence of it is now handled that §7 and §8 both missed. Storing before recording means a *concurrent* submission of the same bytes is normal, and publication was `os.replace` — atomic about **replacing**. A checksum-named entry appearing between `_holds()` and the rename was removed and overwritten without being examined. That is not a wording problem; it contradicted immutability, refusal-not-repair, evidence preservation and "no artifact is implicitly deleted" at the same time. Publication is now `link(2)`, which creates the entry or fails `EEXIST` and has no mode in which it removes what is there. A concurrent winner is re-opened through the anchored descriptor and re-proved for type, owner, mode and content: valid, it is reused; invalid, it is refused and left byte for byte and mode for mode as it was found |
| R1 | The §8 statement that "what a failure claims is a declared `StorageOutcome`" was correct and insufficient. The **default** — `UNRESOLVED`, the sentence an unclassified reason inherits — still asserted that nothing already held had been changed or removed, which the publication defect made false. A conservative default may state what is structurally true of a content-addressed store; it may not make a positive claim about durable state on behalf of paths nobody has examined. It no longer does, and a third outcome (`PRESERVED`) now distinguishes "an entry was refused and left as found" from "there was nothing there" — a distinction that sends an operator to a different procedure |
| R8 | Restated more precisely. The residual is not only the absent cross-account experiment. Convergence of two writers is proven deterministically, by running a second writer inside the first's publication window, and not by a multi-process stress test; and the `EEXIST` guarantee is the kernel's, proven at startup on the configured filesystem rather than argued from documentation |

**One new item.**

| # | Item | Response |
|---|---|---|
| D10 | Publication is a hard link plus a temporary removal, not a rename | `renameat2(RENAME_NOREPLACE)` gives the same create-only guarantee in one syscall, but the standard library exposes no wrapper for it, and a hand-rolled `ctypes` syscall stub in the code path that stores every exported Actor's mechanics is a worse trade than one extra `unlink`. Consequence for operations, documented in §5.6 and `.env.example`: **the artifact root must be on a filesystem supporting hard links** — ext4, XFS, Btrfs, ZFS, tmpfs; not FAT/exFAT or some network mounts. Startup proves both that links work and that a link over an existing name fails, and refuses `link_unsupported` otherwise |

**Two new risks, neither closed.** Both are registered as R-16 and R-17 in the
RAID register.

| # | Risk | Response |
|---|---|---|
| R9 | A submission destroys an artifact the service did not write | Publication cannot remove an entry it has not validated, and cleanup is structurally unable to name anything but a `.incoming-*` temporary, so a failed cleanup cannot delete a published artifact. An unexpected entry under a checksum name now has a recovery procedure (operations §9) whose first instruction is to preserve it |
| R10 | The automated storage evidence was not reproducible in the review environment | On the review host `/` and `/tmp` are owned by uid 65534, and the startup ancestor rule refused 32 tests before they reached their own assertions — tests about publication, durability, anchoring and descriptor lifetime, none about ancestors. The rule is now an injectable `TrustedAncestors` policy, and those tests bound its walk at pytest's temporary root: the same code, the same real `os.lstat` results, walking only the directories the test created. The production walk is separately exercised unbounded against the real configured path, and the trusted, untrusted, sticky, writable, wrong-owner, symlinked, non-directory and absent cases are each tested directly. **The production owner rule was not weakened**; the review named that as a security-policy decision reserved to Peter, and it was not taken. The residual is that the deployment prerequisite is real and no test seam removes it (R-17) |

## 10. Amendment, 2026-08-05 (fourth) — the temporary-cleanup claim

The third re-review accepted the publication mechanism, I-1, root anchoring,
S-B-1 and S-I-1, and returned one Important **evidence-accuracy** finding,
I-3R-1: the third-remediation request's structural-guarantee table said "no
temporary survives success or an ordinary failure" because `_discard` runs on
each path. Running `_discard` is not removal — it swallows `OSError` — and
`test_a_failing_cleanup_leaves_the_published_artifact_alone` had all along
proved the opposite. **No code change was required by the finding, and none was
made to the publication mechanism.** The correction is to the record, plus an
operator procedure the record implied and did not have.

| # | Correction |
|---|---|
| D10 | Restated. The trade is a hard link **plus a best-effort temporary removal**, not a hard link plus a guaranteed one. The extra `unlink` that made `os.link` the cheaper choice over `renameat2(RENAME_NOREPLACE)` is allowed to fail, and the decision is still the right one — but its cost is now stated as it is: a store that returns successfully may leave one private `.incoming-*` hard link in the root. That link is `0600`, inside a `0700` root, served by no route and unable to affect the published artifact; it consumes an inode, and a full copy of the bytes once the artifact is deleted under retention |
| R9 | Unchanged in substance and sharpened in wording. "A failed cleanup cannot delete a published artifact" is true and remains the point. What the entry did not say is what a failed cleanup *can* do, which is leave storage behind that nobody is told about — the service swallows the error, so it never learns and never reports it |

**One new item.**

| # | Item | Response |
|---|---|---|
| D11 | Detection of leftover temporaries is an operator procedure, not an application capability | Operations §5.6, "Temporary files left by a failed cleanup": a read-only `find` bounded by `-maxdepth 1 -type f -name '.incoming-*' -mmin +60`, reporting the link count so an operator can tell a success-path leftover (two links; removing it frees an inode) from an unpublished one (one link; removing it frees the bytes). The age bound exists so the procedure cannot talk an operator into deleting a submission in flight. **No listing or deletion endpoint was added to the service**, and no automatic deletion of unknown entries: the store can create a temporary and unlink one it created in the attempt that is running, and nothing else. The rule is proved against synthetic files by three tests in `tests/test_artifact_store.py` |
| D12 | Retention decision D-c accepted 2026-08-05 | Peter Duscha accepted a **30-day maximum** for database-unclaimed raw artifacts, with earlier deletion when the corresponding rehearsal, retry or incident is closed. Checksum, provenance and sanitized audit remain permanent. Investigation precedes deletion; the maximum does not authorize erasing evidence for an open incident. Operations §5.6 is the executable procedure |

**One new risk, not closed.** Registered as R-18 in the RAID register.

| # | Risk | Response |
|---|---|---|
| R11 | Leftover temporaries accumulate unnoticed and consume the artifact filesystem | Each leftover requires an `unlink` to have failed, which in practice means the root's mode or ownership has drifted or the filesystem is full or read-only — all conditions the store refuses on its *other* paths, so a leftover is a leading indicator rather than a silent cost. It is not monitored automatically: nothing in the platform counts, lists or removes them, and this package deliberately does not add that. The detection procedure is manual and read-only, and how often an operator should run it is an operations decision that has not been taken |
