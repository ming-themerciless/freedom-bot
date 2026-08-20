# Project status

Status date: 2026-08-20 (twenty-eighth update: both required Codex reviews of
the bounded D-03 correction passed with no blocking findings. Peter/Acceptance
Authority accepted the corrected backend contract and explicitly released the
Gemini P3.4 implementation prompt. D-03 is closed; P3.G4, I-06 and A-05 remain
open.)

Update 2026-08-20 (twenty-eighth) — D-03 accepted; Gemini prompt released.

- **Independent reviews passed.** The implementation review and the distinct
  security-focused review found no blocking issue in D-03-1 through D-03-6.
  Review verification and its database-environment limitation are recorded in
  `docs/review/phase-3-d-03-codex-reviews-and-acceptance.md`.
- **Peter accepted the corrected backend contract.** D-03 is **closed** and
  `docs/review/phase-3-p3-4-gemini-implementation-prompt.md` is explicitly
  **released** for the bounded P3.4 production frontend integration.
- **The remaining gates are unchanged.** P3.G4 is open. I-06 isolated-staging
  evidence and A-05 administrator/WebAuthn readiness remain open. No staging
  exposure, deployment, production use, live-service contact or real-player-data
  use is authorized.
- Records: change-log `C-P3.4-C`; RAID D-03 closed; review and acceptance record
  as linked above.

Status date: 2026-08-20 (twenty-seventh update: the bounded D-03 backend-contract
correction authorized by `C-P3.4-A` is **implemented and submitted for review**.
D-03 remains open, both required reviews are pending, and Gemini's prompt remains
held.)

Update 2026-08-20 (twenty-seventh) — D-03 correction implemented and handed off.

- **All six accepted items are delivered.** `/static/` exists as mount **M-01**
  with `GET`/`HEAD` only, no authentication, trusted-host enforcement,
  kill-switch availability and fingerprint-aware caching, and mounts are now
  inside the closed inventory `TC-STRUCT-01` asserts. `ConfirmScope` (eight
  fields) and `CharacterFilters` (two) are defined in `vm-1`. VM-13's `csrf_token`
  is recorded and its false "Recorded in the P3.2 submission" claim is retracted —
  **without** editing the accepted P3.2 submission to manufacture the provenance.
  R-36's table cell now reads `200` HTML · VM-13 (`denied`), matching §5.1's prose
  and the accepted implementation. **VM-22 `DeniedView`** carries `state` and a
  closed-vocabulary `reason` and nothing else, and replaces VM-02 as the generic
  denial carrier at every portal and import boundary.
- **`VIEW_MODEL_VERSION` remains `vm-1`.** Every view-model change is additive
  under §1 rule 5. No field was removed, renamed or narrowed; no enum was
  narrowed; no versioning conflict arose.
- **No production frontend work.** No template, CSS, HTMX file, image or visual
  asset was created or modified. `denied.html` is byte-identical before and after
  — the new view model fits the template it already had. The static root holds one
  zero-byte `.gitkeep` and nothing else.
- **Evidence.** Portal suite **1524 passed, 80 skipped**; bot suite **2294
  passed**; both exit 0, run serially against the approved disposable database.
  `compileall` and `git diff --check` clean. Prototype freeze **14/14** before and
  after. Falsification demonstrated for the mount inventory guard — where the
  pre-existing route guard is shown to **pass** against an undeclared mount, which
  is the blindness D-03-1 identified — and for the denial leakage guard, where 12
  cases across three modules fail; the tree was restored and verified by SHA-256
  in both cases, and the suites above were run after restoration.
- **Not claimed.** No browser, real-device, screen-reader, staging or production
  evidence. No dependency added, no migration added or run outside the disposable
  test database, no network call, no live service, no `.env` or credential read.
  TC-UI-06 is **not** delivered; TC-SEC-14 asserts only the backend half.
- **Still NO-GO for Gemini.** D-03 is **open**. The independent Codex
  implementation review and the distinct security-focused review are **pending**.
  The implementation prompt remains **held**. P3.G4, I-06 and A-05 remain open;
  deployment, public exposure, live-service contact and real-player-data use
  remain unauthorized.
- **The decision waiting for Peter, after both reviews pass:** accept the
  corrected D-03 backend route/view-model contract and explicitly release
  `docs/review/phase-3-p3-4-gemini-implementation-prompt.md`.
- Records: `docs/review/phase-3-d-03-backend-contract-correction-submission.md`;
  change-log `C-P3.4-B`; RAID D-03 amended by addition.

Status date: 2026-08-19 (twenty-sixth update: Peter/Acceptance Authority accepted
`C-P3.4-A` as the bounded D-03 correction authorization. The six corrections now
have explicit dispositions. D-03 remains open pending implementation, independent
Codex implementation review, a distinct security-focused review and Peter's
acceptance of the corrected contract. Gemini's prompt remains held.)

Update 2026-08-19 (twenty-sixth) — D-03 correction decisions accepted.

- Application-served `/static/` is the accepted asset surface, with `GET`/`HEAD`,
  no authentication, trusted-host enforcement, kill-switch availability,
  fingerprint-aware caching and structural coverage of mounts.
- `ConfirmScope` and `CharacterFilters` receive the accepted implemented shapes;
  VM-13's CSRF field and R-36's `200` denied response are recorded accurately.
- A dedicated minimal `DeniedView` is required while byte-identical object-denial
  and absent-object `404` responses remain invariant.
- Claude/backend may implement only these bounded corrections. They require an
  independent Codex implementation review and a distinct security-focused review.
- **Still NO-GO for Gemini:** D-03 is not closed and the implementation prompt is
  not released. P3.G4, I-06 and A-05 remain open; deployment, public exposure,
  live-service contact and real-player-data use remain unauthorized.

Status date: 2026-08-19 (twenty-fifth update: the P3.4 implementation handover is
prepared. The accepted P3.1–P3.3 tree was revalidated against the frozen route and
view-model contracts and shows no drift; six remaining backend-contract items are
presented for the D-03 decision as change-log `C-P3.4-A`, which is **proposed, not
accepted**. P3.4 production frontend implementation remains **NO-GO** until Peter
records the D-03 disposition and explicitly releases the prepared Gemini prompt.)

Update 2026-08-19 (twenty-fifth) — P3.4 handover prepared; D-03 decision requested.

- **Revalidated, no drift.** The registered route inventory equals the accepted
  contract exactly (39 = 39, `DEFERRED_ROUTES` empty); the implemented view-model
  set equals the documented `vm-1` set (21 = 21, `DEFERRED_VIEW_MODELS` empty); no
  view-model field is missing, renamed or removed; the absence controls hold; and
  the 24 current templates carry zero `|safe`, zero `hx-on:`, zero inline script,
  zero `design-prototype/` references and zero remote origins.
- **D-03 is not closable on the existing gate record.** `C-P3.3-K` and `C-P3.3-L`
  both restate it as in force, and both were decided after P3.G2 closed and
  alongside the P3.G3 closure. Six concrete items remain; D-03-1 (no accepted
  static-asset surface) and D-03-2 (`ConfirmScope` undefined in `vm-1`) block a
  faithful P3.4 implementation.
- **Deliverables.** `docs/review/phase-3-p3-4-gemini-readiness-report.md` gains a
  dated addendum (§§A1–A10) preserving its historical 2026-08-14 NO-GO analysis;
  `docs/review/phase-3-p3-4-gemini-implementation-prompt.md` is written and
  **held**, released only by Peter's explicit decision.
- **Unchanged boundaries.** No deployment, public exposure, live-service contact
  or live-data use is authorized. I-06 requires isolated staging; A-05 remains an
  exposure prerequisite; P3.G4 is open and only Peter can close it.
- **Verification.** Visual freeze 14/14 before and after; `git diff --check`
  clean. No migration, live service, network call, browser, package installation
  or real player/Actor/guild data was used.

Status date: 2026-08-19 (twenty-fourth update: Peter/Acceptance Authority accepted
the recommended post-gate sequence. P3.4 development may begin; deployment and
public exposure remain unauthorized; I-06 will be addressed through isolated
staging; A-05 remains an exposure prerequisite; and D-03 must close before Gemini
production integration. Recorded as `C-P3.3-L`.)

Update 2026-08-19 (twenty-fourth) — post-gate sequencing decision.

- Begin P3.4 development under the approved plan and its review gates.
- Do not deploy or expose the service publicly under this authorization.
- Build isolated staging and produce the real I-06 evidence there.
- Complete A-05 with a protected administrator account and two independent real
  WebAuthn credentials before exposure.
- Close D-03 on a frozen backend route/view-model contract before Gemini
  production integration.
- Require a later explicit deployment/exposure decision.

Status date: 2026-08-19 (twenty-third update: Peter/Acceptance Authority closed
P3.G3 and authorized P3.4. P3.3 is accepted after the independent implementation
review, distinct security-focused review, acceptance of `C-P3.3-I`, and the
decisions recorded in `C-P3.3-J`. I-06 and A-05 remain open and continue to block
public staging/production exposure; this gate decision authorizes development,
not deployment.)

Update 2026-08-19 (twenty-third) — P3.G3 gate decision.

- **Decision:** Peter/Acceptance Authority accepted P3.3, closed stop gate
  **P3.G3**, and authorized **P3.4** to begin.
- **Basis:** all P3.3 maintainer decisions are recorded; the sixth correction
  passed independent implementation and distinct security-focused reviews; and
  `C-P3.3-I` is accepted.
- **Boundaries unchanged:** I-06 staging/browser/performance evidence and A-05
  protected-administrator/WebAuthn readiness remain open. No public exposure,
  deployment, production contact or live-data use is authorized by this gate.
- **Later gate unchanged:** D-03's backend route/view-model approval continues to
  govern later Gemini production integration.

Status date: 2026-08-19 (twenty-second update: the distinct security-focused
re-review of `C-P3.3-I` found no blocking or major security finding. The complete
rollback module and structural/rejected-scope guards passed, 120 tests total.
Peter/Acceptance Authority accepted `C-P3.3-I`. P3.G3 remains open for its
separate explicit gate decision, and P3.4 has not begun.)

Update 2026-08-19 (twenty-second) — `C-P3.3-I` accepted.

- **Security review passed.** The test-scoped backend termination is restricted
  to the holder identity captured as PID plus `backend_start`, uses bound SQL
  parameters, and is unreachable from production code.
- **Ownership accepted.** The holder is detached before threaded cleanup;
  orphaned calls are recorded and fail the case rather than being hidden.
- **Verification:** 120 passed in 23.16s across the rollback-boundary module,
  structural guards and rejected-scope controls.
- **Decision:** Peter/Acceptance Authority accepted `C-P3.3-I` on 2026-08-19.
  This does not separately accept defective `C-P3.3-H`.
- **Gate unchanged pending explicit decision:** P3.G3 remains open and P3.4 is
  not yet authorized.

Status date: 2026-08-19 (twenty-first update: Peter/Acceptance Authority accepted
the outstanding P3.3 product and operational decisions: D-09's rollback boundary;
I-11's `snapshot_folder_selections`; the narrow R-41/SM-05 exception; the §13
effect-publication recovery amendment; and derived limits 20, 3 and 10,000.
Recorded as `C-P3.3-J`. P3.G3 remains open for the distinct security-focused
review, and P3.4 has not begun.)

Update 2026-08-19 (twenty-first) — Acceptance Authority decisions.

- **D-09 accepted.** While a retained job records a committed apply effect,
  rollback is application rollback or roll-forward rather than schema downgrade
  below `0013`; the boundary reopens under the documented N-24 conditions.
- **I-11 accepted.** `snapshot_folder_selections` is the authoritative mutable,
  versioned current selection; append-only audit events retain its history.
- **R-41/SM-05 accepted.** A completed preview may become `stale` only while no
  apply names it. Completed applies and referenced previews remain immutable.
- **Section 13 accepted.** Effect-publication recovery is ratified with
  `EFFECT_RECOVERY_LIMIT = 20`, `EFFECT_PUBLICATION_GRACE_HEARTBEATS = 3`, and
  retention `MAX_LIMIT = 10 000`.
- **Gate unchanged.** This is not acceptance of `C-P3.3-I` or closure of P3.G3;
  the separate security-focused review remains required.

Status date: 2026-08-19 (twentieth update: the independent review of the fifth migration-rollback correction **did not accept** it — its ceiling counted only the subprocess reap and the writer join, while the same release also called `holding.rollback()` and `holder.close()` synchronously with no enforceable timeout, so a blocked rollback prevented the close and the writer join and a blocked close prevented the join, leaving the `alembic_version` row lock live in the shared disposable database. Every database cleanup call is now made on a thread of its own with a bounded wait, the holder is detached from its pool before anything can block it, an orphaned thread is recorded and reported rather than hidden, a new step disposes of the holder's backend independently, and the ceiling now counts all six waits. Three new deterministic cases and three mutation runs prove it. **No production change.** **Re-submitted** for independent implementation review and a distinct security-focused review; P3.G3 remains open and P3.4 has not begun)

Update 2026-08-19 (twentieth) — P3.3 sixth migration-rollback correction.
Recorded in section 19 of
[`../review/phase-3-p3-3-submission.md`](../review/phase-3-p3-3-submission.md).

- **One major finding, no blocking defect, and no production change.** The
  migration's DDL, guard, emitted SQL, constraints, grants, application statements
  and worker statements are byte-for-byte what the fifth correction left. `0011`,
  `0012`, `0013` and `migrations/env.py` were not edited, verified by SHA-256, and
  `docs/operations/web-portal.md` is unchanged. The diff is one test module's
  cleanup and four new cases, plus controlled-document wording.
- **The fifth correction is *not* accepted.** `C-P3.3-H` remains open. What it got
  right is retained and rerun — the bounded subprocess reap, the release order, the
  `add_note()` behaviour and TC-MIG-38…TC-MIG-41 — and its ceiling claim is
  corrected here rather than rewritten as though it had been right.
- **F1 — the 25-second ceiling omitted the two database calls.**
  `_HeldLockCleanup.release()` also called `holding.rollback()` and
  `holder.close()` synchronously, and neither SQLAlchemy nor psycopg offers an
  enforceable timeout for either. Catching an exception does not bound an
  operation that never returns. A blocked rollback meant the close, and a blocked
  close meant the writer join, were never reached at all — and the resource at
  stake is the externally taken `alembic_version` row lock in the **shared**
  disposable `freedom_test` database, so one stuck cleanup could have produced a
  page of unrelated failures in later cases. **Recorded as an unbounded
  failure-path cleanup defect, not a flake**: neither branch is reachable from
  healthy PostgreSQL, which is precisely why the fifth correction's real-database
  case and its instant fake transaction and connection falsified neither.
- **The correction, and its cost stated rather than hidden.** Each database call
  is made by a daemon thread of its own and it is the **wait** that is bounded,
  because that is the only part a test can control. A call that never returns
  therefore leaves that thread alive — so it is recorded on the cleanup, reported
  as a problem, and never followed by anything that touches what it owns. The
  holder is **detached from its pool at construction**, while only the calling
  thread can be inside it, so no orphaned thread can leave a usable pooled
  connection for a later case, on any path. Because a stuck connection object is
  off limits, a new step disposes of the **backend** from a different connection —
  `pg_terminate_backend()` on the test's own backend, matched on pid *and*
  `backend_start` — which releases the row lock and lets the stuck call return.
  The release runs six steps, records each before entering it, and runs every
  later one regardless of what an earlier one did.
- **The ceiling now counts every wait it performs:** `2 × 5 + 2 × 5 + 5 + 15 =
  40 s`, against the 60-second production-test ceiling, and calculation,
  documentation and tests agree.
- **Proved, not asserted.** TC-MIG-42 and TC-MIG-43 drive the rollback-blocked and
  close-blocked paths with deterministic stand-ins that block exactly where the
  real calls would and record the thread they were called on; TC-MIG-44 is the
  passing-path mirror for both. Each proves the release returns inside its complete
  ceiling and well inside the stand-in's period, reports the blocked step, attempts
  every later step, sets the writer's commit event and joins it, preserves the
  assertion under diagnosis, and accounts for the helper thread it left.
- **Falsified deterministically, three times, without hanging.** An unbounded
  direct `rollback()` fails exactly the two rollback cases (11.31s); an unbounded
  direct `close()` fails exactly the two close cases (11.54s); and the fifth
  correction's `communicate()` mutation is retained and reproduces the same four
  failures (10.52s). All were restored by checksum and none is in the final tree.
- **`_RecordingChild` stays an informal technical concurrence** — Peter's
  direction, applied here: no numbered RAID decision, no change-log decision entry
  of its own, and its existing localized documentation is sufficient.
- **Nothing else changed and nothing is weakened.** No identity assertion,
  queue-fairness assertion, migration, production statement, production pause
  hook, production timeout policy, marker, sidecar, tombstone, retention rule,
  runtime grant or hidden schema object was touched, and no test was relaxed,
  skipped, deleted or renamed away.
- **Nothing is accepted.** P3.G3 remains open pending the independent
  implementation re-review, the distinct security-focused re-review, ratification
  of the retention-aware rollback policy (**D-09**, change-log `C-P3.3-D`,
  `C-P3.3-E`, `C-P3.3-F`, `C-P3.3-G`, `C-P3.3-H`, **`C-P3.3-I` new**), and Peter's
  two unchanged decisions: **RAID I-11** (`snapshot_folder_selections`) and the
  **R-41 / SM-05 controlled-contract amendment**.
- **I-06 and A-05 are unchanged and still open.**


Status date at that update: 2026-08-19 (nineteenth update: the independent review of the fourth migration-rollback correction accepted the writer-identity remediation as sound and reran the rollback module against disposable PostgreSQL, and found one major defect — TC-MIG-37's failure-path cleanup killed a surviving migration subprocess and then collected it with an unbounded `communicate()`, so a stall could hang cleanup before the `alembic_version` row lock, the holder connection and the fence writer were released. Cleanup is now one ordered, bounded release owned by a test-local object, it reports rather than replaces the assertion under diagnosis, and four new deterministic cases prove it. **No production change.** **Re-submitted** for independent implementation review and a distinct security-focused review; P3.G3 remains open and P3.4 has not begun)

Update 2026-08-19 (nineteenth) — P3.3 fifth migration-rollback correction.
Recorded in section 18 of
[`../review/phase-3-p3-3-submission.md`](../review/phase-3-p3-3-submission.md).

- **One major finding, no blocking defect, and no production change.** The
  migration's DDL, guard, emitted SQL, constraints, grants, application statements
  and worker statements are byte-for-byte what the fourth correction left. `0011`,
  `0012`, `0013` and `migrations/env.py` were not edited. The diff is one test
  module's cleanup and four new cases, plus controlled-document wording.
- **The fourth correction's writer-identity result stands accepted as sound.**
  The reviewer confirmed the observed request is restricted to the announced
  writer pid, matched to the production `hold_for_effect` statement, and tied
  through `pid`, `virtualtransaction`, `backend_xid` and `xact_start` to the
  transaction that later commits, and that the recorded falsification checksum
  matches the current file. Their two passing runs are **historical**: a passing
  happy path is not evidence about failure cleanup.
- **F1 — TC-MIG-37 had an unbounded subprocess reap on failure.** Its `finally`
  block killed a surviving migration child and then called
  `migration.communicate()` with no timeout, so a stall in termination or pipe
  collection could hang cleanup indefinitely — before the externally held
  `alembic_version` row lock was rolled back, before the holder was closed and
  before the writer was joined. **Recorded as an unbounded failure-path cleanup
  defect, not a flake**: the passing case never executes that path.
- **The correction.** One test-local object owns every resource the case holds and
  runs a single ordered release on every exit path: release the writer's commit
  event first; end and boundedly reap a surviving migration child **before** the
  row lock is released, so a migration that is *released* rather than *ended*
  cannot commit its drops and a writer queued behind its table lock is freed; roll
  back the row lock; close the holder; then join the writer, bounded, and only if
  it was started and is still alive. The reap kills and collects with an explicit
  timeout, twice, and never waits without one; a child surviving both is reported
  and stepped over rather than stranding the resources that are still releasable.
  The release **never raises** — its problems are attached to the failing
  assertion with `add_note()`, so the primary failure stays diagnosable while
  cleanup failures are still reported. The same bounded reap replaces the
  identical unbounded shape in the module's three sibling concurrency cases.
- **Proved, not asserted.** TC-MIG-38 drives a **controlled** assertion failure
  against real PostgreSQL — the production revision, the production fence
  statement, the real Alembic child and the real writer all live — at two named
  points, and measures the release from the moment of failure: bounded, child
  reaped, writer and holder released, and no matching lock or activity left in
  `pg_locks`/`pg_stat_activity`. TC-MIG-39…TC-MIG-41 cover the timeout, pre-start
  and error-preservation branches deterministically.
- **Falsified deterministically, including by the real PostgreSQL case.** Against
  the pre-fix `kill(); communicate()` shape four of the five new cases fail in
  under ten seconds and without hanging: **both** TC-MIG-38 parameters — the
  surviving child collected with `timeout=None`, and the already-exited child not
  collected at all — plus TC-MIG-39 and TC-MIG-41. The bound is asserted at the
  *call*, because `SIGKILL` collects a real Alembic child immediately and an
  unbounded collection returns at once, so no timing assertion could see it. The
  mutation was restored by checksum and is not in the final tree.
- **Nothing else changed and nothing is weakened.** No identity assertion, queue-
  fairness assertion, migration, production statement, production pause hook,
  marker, sidecar, tombstone, retention rule or hidden schema object was touched.
- **Nothing is accepted.** P3.G3 remains open pending the independent
  implementation re-review, the distinct security-focused re-review, ratification
  of the retention-aware rollback policy (**D-09**, change-log `C-P3.3-D`,
  `C-P3.3-E`, `C-P3.3-F`, `C-P3.3-G`, **`C-P3.3-H` new**), and Peter's two
  unchanged decisions: **RAID I-11** (`snapshot_folder_selections`) and the
  **R-41 / SM-05 controlled-contract amendment**.
- **I-06 and A-05 are unchanged and still open.**


Status date at that update: 2026-08-19 (eighteenth update: the independent review of the third migration-rollback correction confirmed the controlled-document correction and the exact rollback-module count, and found one major defect — the new held-lock regression did not identify the ungranted lock it asserted on as belonging to its own fence writer. The assertion is now bound to the writer's announced backend pid and to its re-observed transaction identity, and is falsified deterministically against an unrelated queued session. **No production change.** **Re-submitted** for independent implementation review and a distinct security-focused review; P3.G3 remains open and P3.4 has not begun)

Update 2026-08-19 (eighteenth) — P3.3 fourth migration-rollback correction.
Recorded in section 17 of
[`../review/phase-3-p3-3-submission.md`](../review/phase-3-p3-3-submission.md).

- **One major finding, no blocking defect, and no production change.** The
  migration's DDL, guard, emitted SQL, constraints, grants, application statements
  and worker statements are byte-for-byte what the third correction left. The diff
  is one test case's identity assertions and controlled-document wording.
- **F1 — TC-MIG-37 did not identify its ungranted lock as the test writer.** It
  polled every ungranted `RowExclusiveLock` on `reconciliation_jobs` and asserted
  only that the migration holder's pid was absent, so an unrelated queued session
  could satisfy it while the intended writer was still awaiting scheduling, opening
  its connection or inside `seed_import()`. **This is recorded as a defective
  assertion, not as a timing flake**: it passed because the disposable database is
  quiet enough that the intended writer normally wins the race, which is precisely
  why a passing run was not evidence.
- **The correction.** The writer announces its PostgreSQL backend pid over a
  bounded queue, from inside its own transaction and before any production
  statement. The poll is scoped `AND l.pid = :pid`, and additionally requires
  `pg_stat_activity.query` for that pid to be the production `hold_for_effect`
  fence — matched by statement shape, not by driver placeholder spelling — rather
  than `seed_import`, connection setup or an unrelated statement. The transaction
  identity seen while the request is queued (`pid`, `virtualtransaction`,
  `backend_xid`, `xact_start`) is re-observed, still open and uncommitted, on the
  transaction that then commits the fence, so the queued request and the committing
  transaction are proved to be one — not inferred from thread liveness. The
  migration holder and the fence writer are named separately throughout. **No
  production pause hook, no revision change, no change to emitted SQL, no sleep
  used as proof, no unbounded wait.**
- **Falsified deterministically.** With the writer held on an event before its
  fence and only an unrelated session queued for the same mode on the same
  relation, the old broad predicate is satisfied — and its one identity assertion
  still holds — while the corrected predicate cannot be, and the case fails. The
  mutation was restored by checksum and is not in the final tree.
- **The queue-fairness case is not weakened.** TC-MIG-32 keeps every assertion and
  its deliberately broader observation, which proves a different condition; a
  narrowly named helper was added rather than the shared one being repurposed.
- **Nothing is accepted.** P3.G3 remains open pending the independent
  implementation re-review, the distinct security-focused re-review, ratification
  of the retention-aware rollback policy (**D-09**, change-log `C-P3.3-D`,
  `C-P3.3-E`, `C-P3.3-F`, **`C-P3.3-G` new**), and Peter's two unchanged decisions:
  **RAID I-11** (`snapshot_folder_selections`) and the **R-41 / SM-05
  controlled-contract amendment**.
- **I-06 and A-05 are unchanged and still open.** No marker, sidecar, tombstone,
  retention-policy change, production pause hook or hidden schema object was added.


Status date at that update: 2026-08-19 (seventeenth update: the independent review of the second migration-rollback remediation found three major defects and no new blocking defect. The controlled documents now state the retention-aware predicate consistently, the held-lock exclusion is proved from a **granted** `AccessExclusiveLock` by a new regression, the mis-named queue-fairness case is renamed to what it proves, and every required command is rerun against the final tree with internally consistent counts. **Re-submitted** for independent implementation review and a distinct security-focused review; P3.G3 remains open and P3.4 has not begun)

Update 2026-08-19 (seventeenth) — P3.3 third migration-rollback correction.
Recorded in section 16 of
[`../review/phase-3-p3-3-submission.md`](../review/phase-3-p3-3-submission.md).

- **No blocking defect this round, and no production change.** The migration's
  DDL, guard, emitted SQL, constraints, grants, application statements and worker
  statements are byte-for-byte what the second remediation left. The diff is one
  new test case, one renamed and re-scoped test case, two test-cleanup
  corrections, and controlled-document wording.
- **F1 — the controlled documents still stated the superseded boundary.** The
  predicate had been corrected in the migration and the runbook headline, and
  left standing as present-tense prose in the submission's answers, the
  logical-schema constraint note, the SM-05 subsection, this status record, RAID
  `I-18` and `RR-19`, the `C-P3.3-D` amendment bullet and the rollback-boundary
  test module. Every one of those now states: **downgrade below 0013 is refused
  while any *retained* reconciliation job records a committed effect, and becomes
  available only when no such job exists** — with the four database states
  (never-applied; retained completed; retained committed-but-unpublished, which
  no age makes retention-eligible; and retention-emptied with `snapshot_imports`
  and audit history preserved) distinguished wherever the rule is stated.
  Historical wording survives only where it is labelled superseded and paired
  with the corrected rule. **Retention is not a rollback technique**, and manual
  deletion, truncation, a shortened period and an early sweep are named as
  unsupported in the runbook.
- **F2 — the mandatory concurrency regression proved the wrong condition.** The
  case named `…a_fence_writer_arriving_after_the_lock_cannot_commit_until_it_finishes`
  held the migration's lock request **ungranted** throughout, so it established
  PostgreSQL lock-queue fairness, not the named condition. It is renamed
  `…arriving_behind_a_pending_lock_request_cannot_overtake_it` and kept as
  coverage of what it does prove (TC-MIG-32). **TC-MIG-37 is new** and proves the
  held-lock condition from observable state: a **granted** `AccessExclusiveLock`
  held by the production downgrade transaction, unchanged pid/`virtualtransaction`/
  `xact_start` across the writer's arrival, the production fence's `ROW
  EXCLUSIVE` request observed ungranted with nothing committed, the migration
  transaction ending, and only then the fence committing. The migration is held
  after the grant by locking Alembic's own `alembic_version` row from the test —
  **no production pause hook, no revision change, no change to emitted SQL, no
  sleep used as proof**.
- **F3 — the completion report contained impossible counts.** §15.4 reported 17
  passed for the rollback module alone and 15 passed for that module plus
  `test_migration_0013_round_trip.py`. Every required command is rerun against
  the final corrected tree and reported with its literal invocation and exact
  count; pre-fix results are kept and labelled historical.
- **Nothing is accepted.** P3.G3 remains open pending the independent
  implementation re-review, the distinct security-focused re-review, ratification
  of the retention-aware rollback policy (**D-09**, change-log `C-P3.3-D`,
  `C-P3.3-E`, **`C-P3.3-F` new**), and Peter's two unchanged decisions: **RAID
  I-11** (`snapshot_folder_selections`) and the **R-41 / SM-05 controlled-contract
  amendment**.
- **I-06 and A-05 are unchanged and still open.** No marker, sidecar, tombstone,
  retention-policy change, production pause hook or hidden schema object was
  added.


Update 2026-08-18 (fifteenth) — P3.3 migration-rollback remediation. Recorded in
section 14 of
[`../review/phase-3-p3-3-submission.md`](../review/phase-3-p3-3-submission.md).

- **One blocking finding, fixed and regression-tested against real PostgreSQL:
  migration `0013` could not round-trip a database that had processed a normal
  apply.** The commit fence writes `effect_result` inside the effect's own
  transaction and a check constraint makes the pair inseparable, so
  `downgrade 0012` — which correctly keeps `effect_committed_at`, that being
  `0012`'s column — destroyed the payload `upgrade 0013` then demanded back. Every
  truthfully completed apply failed the re-upgrade guard, and the database was
  **stranded one revision below head** with no permitted remedy. The rollback
  evidence the previous submission cited exercised only an **empty** schema.
- **The fix is a refusal, not a weakening.** `downgrade()` now counts the
  committed effects **before it changes anything** and refuses, naming the
  `completed` and committed-but-unpublished populations separately and the
  operator's action. Offline (`--sql`) scripts carry the same guard as executable
  SQL rather than a comment. **No constraint weakened, no invariant amended, no
  history deleted, no grant changed, no application or worker statement touched**
  — and `alembic check` still reports no metadata difference.
- **The evidence is now classified so neither class can be read as the other.**
  `test_migration_0013_round_trip.py` is retained and relabelled as empty-schema
  evidence; `test_migration_0013_rollback_boundary.py` is new and data-bearing,
  with every committed effect produced by the production apply path.
  TC-MIG-24…TC-MIG-30. All failed against the pre-remediation migration first.
- **One operational-contract amendment is proposed, not self-approved:** while
  any **retained** reconciliation job records a committed apply effect, rolling
  P3.3 back is application rollback or roll-forward rather than schema
  downgrade; the boundary reopens once no such job survives — either because no
  apply has committed, or because approved N-24 retention has removed every
  completed committed-effect job and its result and no committed-but-unpublished
  job remains. (Wording corrected 2026-08-19; the earlier "past the first
  committed apply effect" phrasing described a historical event the guard does
  not record, and retention is not a rollback technique.) Change-log `C-P3.3-D`, RAID **D-09**,
  runbook `docs/operations/web-portal.md` §3.6. The refusal itself is implemented
  because it is correct under either policy.
- **Nothing is accepted.** P3.G3 remains open pending the independent
  implementation re-review, the distinct security-focused re-review, D-09, and
  Peter's two unchanged decisions: **RAID I-11** (`snapshot_folder_selections`)
  and the **R-41 / SM-05 controlled-contract amendment**. New RAID rows: **I-18
  closed**, **RR-19** recorded, **D-09** open.
- **I-06 and A-05 are unchanged and still open.**

Update 2026-08-18 (fourteenth) — P3.3 effect-publication remediation. Recorded in
section 13 of
[`../review/phase-3-p3-3-submission.md`](../review/phase-3-p3-3-submission.md).

- **Two blocking findings against the previous remediation, both fixed and both
  regression-tested against real PostgreSQL.** Both were cases where a job could
  still deny an import the database was holding.
  1. **A committed effect could be cancelled after reaping.** Only the `running`
     branch of R-45's cancel statement carried the fence predicate, and the reaper
     deliberately requeued a job whose effect had committed but whose result had
     not been published. Both branches now carry it, so do `fail`,
     `cancel_under_lease` and `mark_stale_under_lease`, and migration `0013` adds
     `CHECK (effect_committed_at IS NULL OR state NOT IN ('failed','cancelled',
     'stale'))` — so the row is refused whatever statement writes it, including
     direct runtime-role SQL. The route answers the truthful `409`
     (`already_applied`) and **writes no audit event claiming a cancellation was
     requested**.
  2. **A committed effect could become `failed` on attempt three.** Neither reaper
     branch can describe a committed effect. The commit fence now stores the
     bounded result the run produced, in the same statement as
     `effect_committed_at`, and an explicit **effect-publication recovery** takes
     the expired lease instead: one transaction under the job row's write lock
     reads that payload and the immutable `snapshot_imports` receipt, inserts the
     result, completes the job and records the completion event. No artifact is
     re-parsed, no authority re-resolved, no lease minted and `attempts` is
     untouched, so **N-43 is neither spent nor disguised**.
- **RR-16 is withdrawn, not carried.** The previous remediation recorded finding
  2's condition as an accepted residual risk. The reviewer refused it as one, and
  was right to; it is now RAID **I-17, closed**.
- **Nothing is accepted.** P3.G3 remains open pending the independent
  implementation re-review, the distinct security-focused re-review, and Peter's
  two unchanged decisions: **RAID I-11** (`snapshot_folder_selections`) and the
  **R-41 / SM-05 controlled-contract amendment**.
- **One further contract amendment is proposed, not self-approved**, and it is
  larger than the last: SM-05 gains **one transition** (`running → completed`,
  performed by the recovery pass), three forbidden transitions, one column and two
  check constraints. **No state is added** — a seventh state `recovering` was
  considered and rejected — and no accepted numeric value changes. Recorded as
  change-log `C-P3.3-C` for Peter, alongside one new derived constant
  (`EFFECT_RECOVERY_LIMIT = 20`) and one new residual risk (**RR-18**).
- **I-06 and A-05 are unchanged and still open.**

Update 2026-08-18 (thirteenth) — P3.3 remediation. Recorded in the dated
remediation section of
[`../review/phase-3-p3-3-submission.md`](../review/phase-3-p3-3-submission.md).

- **Two blocking findings, both fixed and both regression-tested.**
  1. **The import effect was not fenced.** `SnapshotImportService.apply` committed
     the import, characters, mappings and success audit in one transaction, and
     the worker published the job's terminal state in a *second* one. In between,
     a cancellation, a timeout self-abandon, a kill-switch self-abandon or a
     reaper requeue could transition the job while the abandoned execution thread
     went on to commit real state — so a job could say `cancelled`, `queued`,
     `stale` or `failed` over a durable import. Migration `0012` adds
     `reconciliation_jobs.effect_committed_at`, written **inside the effect's own
     transaction** by a commit fence whose row lock serialises against all three
     writers. Seven race cases (TC-JOB-17…23) assert the actual import,
     character, mapping and audit rows, not a runtime return string.
  2. **The N-24 retention command could not run.** Its
     `UPDATE reconciliation_jobs SET result_id = NULL` violated
     `CHECK ((state = 'completed') = (result_id IS NOT NULL))` for every completed
     job, and it ignored the `parent_job_id … RESTRICT` graph. It is rewritten as
     one bounded atomic operation with a fixed-point retained-graph rule, and
     covered by twelve real-PostgreSQL cases (TC-OPS-06…17).
- **Nothing is accepted.** P3.G3 remains open pending the independent
  implementation re-review, the distinct security-focused re-review, and Peter's
  two decisions: **RAID I-11** (`snapshot_folder_selections`) and the **R-41 /
  SM-05 controlled-contract amendment** for the completed-unconfirmed-preview →
  `stale` exception.
- **One contract amendment is proposed, not self-approved.** SM-05's
  "cancelling a committed apply" mechanism cell described something the code did
  not do; it is corrected to name the fence. No state, transition or accepted
  numeric value changes. Recorded as change-log `C-P3.3-A` for Peter.
- **I-06 and A-05 are unchanged and still open.**

Update 2026-08-18 (twelfth) — P3.3 submitted. Recorded in
[`../review/phase-3-p3-3-submission.md`](../review/phase-3-p3-3-submission.md).

- **Starting authority.** P3.G2 was accepted on 2026-08-18 by change-log entry
  `C-P3.2-D`. That decision authorized P3.3 to begin and accepted no later gate.
- **Delivered.** The closed R-40…R-49 surface; migration `0011` and its three
  tables; the durable six-state job model of SM-05 with `FOR UPDATE SKIP LOCKED`
  claiming, per-claim lease fencing, the two-branch reaper and the worker
  self-abandon that shares it; a separate `freedom-worker` process and its
  systemd unit; bounded audit search; VM-14/15/17/18; the N-24 retention command;
  and the retirement of the inert Phase 2 preview endpoint.
- **Nothing here is accepted.** P3.3 is **submitted**. Its gate P3.G3 is open,
  and P3.4 has not started.
- **Three findings raised rather than resolved silently**, and one of them needs
  a maintainer decision: **RAID I-11** — the accepted schema names no table for
  the administrator's folder selection and the table it would belong to is
  append-only, so P3.3 added `snapshot_folder_selections` on the precedent P3.2
  set. **I-12** and **I-13** are closed by the package: S-11 is now
  process-aware in both directions, and a portal-applied import records the
  stable platform account rather than only a Discord snowflake.
- **I-06 stays open and is widened.** TC-PERF-02 — *measure a real-folder apply
  end to end* — has **never been measured at all**, and P3.3 delivers the job
  model that measurement needs without simulating the measurement. TC-PERF-01,
  TC-PERF-03, TC-LIM-02, TC-SEC-07's browser half and TC-OPS-01…05 remain unrun
  because staging does not exist.
- **A-05 stays open.** No public staging or production exposure is authorized
  until the protected administrator account and two real WebAuthn credentials are
  established and attested by Operations.


Update 2026-08-16 (eleventh, later the same day) — P3.G1 gate decision. The
complete independent implementation and distinct security-focused re-review is
recorded in
[`../review/phase-3-p3-g1-independent-and-security-re-review-2026-08-16.md`](../review/phase-3-p3-g1-independent-and-security-re-review-2026-08-16.md).

- **Review outcome:** no remaining blocking or important implementation or
  security finding. Fresh evidence: **712 portal tests** and **2260 bot tests**,
  no failures and no skips; changed Python modules compile; `git diff --check` is
  clean.
- **Decision:** Peter Duscha accepted P3.1 and closed stop gate **P3.G1** on
  2026-08-16. RAID I-07, I-09 and I-10 are closed. **P3.2 is authorized to
  begin.** P3.3 remains behind P3.G2 and is not authorized by this decision.
- **TC-BG-16 wording corrected:** enrolled and invented credential IDs produce
  the same externally meaningful outcomes — statuses and coarse error codes at
  the same attempts under the same configured window. Literal body equality is
  not claimed because correlation identifiers intentionally differ; literal
  `Retry-After` equality is timing-dependent and is not claimed.
- **I-06 remains open.** No staging environment exists, so TC-LIM-02,
  TC-SEC-07's browser half, TC-OPS-01…05 and TC-PERF-01…03 remain unrun. This
  does not block P3.2; it blocks staging/production exposure and final Phase 3
  production-readiness acceptance until the owning checks pass.
- **A-05 remains open.** The enrollment mechanism is accepted, but two real
  WebAuthn credentials have not been validated on a deployment host. This does
  not block P3.2; it blocks public staging/production exposure until the
  Operations Owner validates the prerequisite.


Update 2026-08-16 (tenth, later the same day) — appended, not rewritten. This one
records the **distinct security-focused review** and its remediation. Recorded in
[`../review/phase-3-p3-g1-security-review-remediation-submission-2026-08-16.md`](../review/phase-3-p3-g1-security-review-remediation-submission-2026-08-16.md),
against
[`../review/phase-3-p3-g1-security-review-2026-08-16.md`](../review/phase-3-p3-g1-security-review-2026-08-16.md).

- **Two blocking findings, both accepted.** N-32 requires a per-address **and** a
  per-account WebAuthn assertion budget; the second was implemented, validated and
  unit-tested, and **no production call site invoked it**, so attempts spread over
  fresh source addresses were bounded only per address. N-33 requires a per-address
  **and** a per-grant recovery budget; the second was incremented inside the
  redemption transaction, which every refusal rolls back, so an attempt matching a
  real but expired, invalidated or consumed grant counted for nothing and the cap
  could be walked past from new addresses.
- **The suite reported on the mechanisms, not on a request.** The account budget's
  only caller was a test calling it directly, and the per-grant case presented a
  token matching no grant row and asserted the stored count stayed **zero** — an
  assertion the defect satisfies perfectly. That case has been renamed and
  re-scoped to the property it really held rather than deleted.
- **One rule, applied twice.** An attempt counter must be spent in a transaction
  that commits whether or not the attempt succeeds. Both budgets are now consumed
  in their own committed transactions before the unit of work they bound — beside
  `_consume_rate_limit()`, which has always worked this way — with the account
  budget charged after the presented credential is resolved and before anything is
  verified, and the per-grant attempt charged through a service method that
  **returns** its refusal instead of raising it.
- **The limit is not an oracle.** A credential id that resolves to no account
  spends an equivalent keyed per-credential budget, so an enrolled credential and
  an invented one are refused at the same attempt with the same externally
  meaningful status and coarse error code. Correlation identifiers intentionally
  differ, and literal retry-hint equality is not claimed.
- **Evidence.** TC-BG-16 and TC-BG-17 added by addition, both direct HTTP against
  real PostgreSQL and both spending their budget from several source addresses;
  **712 portal and 2260 bot tests pass with no failures and no skips**, run
  serially against the guarded disposable database; four falsification mutations
  killed, including one that reintroduces the original rollback mechanism at the
  new boundary, every mutation reverted and verified byte-for-byte. **No accepted
  value, environment variable, route, schema, migration, dependency, deployment
  value or visual asset changed.**
- **Nothing here is accepted.** P3.G1, RAID I-09 and RAID I-10 remain open; P3.2
  and P3.3 have not started, and the security review's outcome stands until an
  independent security re-review says otherwise.


Update 2026-08-16 (ninth, later the same day) — appended, not rewritten. This one
**corrects the lifecycle contract recorded as complete by the third update**,
found by fresh independent implementation re-review
(`../review/Handover information`). Recorded in
[`../review/phase-3-p3-g1-composition-lifecycle-claim-remediation-submission-2026-08-16.md`](../review/phase-3-p3-g1-composition-lifecycle-claim-remediation-submission-2026-08-16.md).

- **The cleanup was right; nothing guarded the way in.** `WebComposition.aclose()`
  is permanent — it closes the provider's HTTP client and disposes an owned engine
  — and the ASGI lifespan performed no live-or-closed check before running the
  startup checks and yielding. A composition passed to two applications, or one
  application whose lifespan was entered again, answered
  `lifespan.startup.complete` and began serving with a closed Discord client behind
  R-03 and R-04. The first failure would have been an OAuth request, not a startup.
- **The resource checks were never going to catch it.** They never receive the
  provider, and `Engine.dispose()` does not invalidate an engine — it discards the
  pool and lets the next checkout build a replacement — so S-14 would have
  connected successfully and reported health for resources nobody may use.
- **The suite required the unsafe outcome.** The repeated-shutdown case entered a
  second lifespan over a closed composition and asserted
  `lifespan.startup.complete` from it, under the name of idempotency. That is not a
  repeated *shutdown*; it is a new *startup* after shutdown. This is I-09's shape in
  its lifecycle form — release one way, admit the other — and having the exit right
  is what made the entry look already handled.
- **Corrected by an explicit one-way lifecycle.** `CompositionLifecycle` runs
  `new -> started -> closing -> closed`; `claim_for_startup()` is the only
  transition out of `new` and is the lifespan's **first** statement — before the
  checks and **outside** the cleanup `try`, so an application that is refused a
  composition closes nothing belonging to the one still serving from it.
  `__setattr__` refuses every backward or sideways write to that state, so a spent
  composition cannot be reset and re-claimed. `aclose()`'s at-most-once,
  ownership, `finally` and re-raise behaviour is unchanged.
- **Evidence.** TC-STRUCT-11 amended by addition; the codifying case corrected and
  six new cases added, all driving the real ASGI lifespan protocol; **707 portal
  and 2260 bot tests pass with no failures and no skips**, run serially against the
  guarded disposable PostgreSQL database; five falsification mutations killed and
  one non-killing mutation disclosed with its explanation; every mutation reverted
  and verified byte-for-byte. **No accepted value, environment variable, route,
  schema, migration, dependency, deployment value or visual asset changed.**
- **Nothing here is accepted.** P3.G1, RAID I-09 and RAID I-10 remain open; P3.2
  and P3.3 have not started.

Update 2026-08-16 (eighth, later the same day) — appended, not rewritten. This
one **corrects the boundary the seventh update declared beside its own
correction**, found by fresh independent implementation re-review. Recorded in §16
of
[`../review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md`](../review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md).

- **The unwrapping was right; the limit stated beside it was not.** The seventh
  update excluded every selection in a callable position because "the source does
  not say which body runs", and said closing it would need a set-valued analysis.
  Both hold for `if flag`. Neither holds for an AST literal:
  `NOW = ((lambda: datetime.now(timezone.utc)) if True else (lambda: None))()`
  captures an instant at import, and `IfExp(test=Constant(True), …)` names the
  branch that runs. The detector returned nothing, because `_invoked_lambda()` did
  not handle `ast.IfExp` at all — and the control offered as evidence for the limit
  used a **name** as its test, so it never exercised the claim it was cited for.
  This is I-10's shape once more, now in a declared *limit*.
- **The detector was corrected to the invariant, and the limit narrowed to the
  truth.** A callable position now selects the reachable branch of a conditional
  whose test is an **exact** boolean literal, then continues through the lambda,
  call and named-expression chain already supported — one body, decidable from one
  node, no set-valued analysis. The boundary is **identity, not truthiness**: `1`,
  `1.0`, `'yes'`, `None`, a comparison, a `not`, a name and `or` are all left
  exactly where they were, each asserted as a case.
- **Ordinary evaluation is preserved, including what Python does not evaluate.**
  The conditional's test always runs and is always walked. When the test is a
  literal only the selected branch is walked, because the other expression is never
  evaluated — it builds no lambda and runs none of its defaults. A capture written
  there is therefore no longer reported; that is the one behaviour this correction
  removes, it is disclosed rather than left to be found, and it narrows no
  invariant, since no instant is captured by an expression that does not run.
- **Proved failing first, then proved on the real module.** With only the helper
  branch removed, the added case reports `{'true': [], 'false': []}` — the false
  negative reproduced. Inserted into the real module after `pytestmark`, each
  literal reproducer then failed TC-STRUCT-08 naming line 119, while the
  name-conditioned selection correctly did not fail. The literal-`False` run
  carries corroboration from outside this guard: CPython emitted
  `DeprecationWarning: datetime.datetime.utcnow() is deprecated` at line 119 during
  collection, which is the interpreter reporting the capture. Each mutation was
  restored byte-for-byte, verified by digest and by `cmp`, and the clean module
  reports nothing under both the pre-correction and the corrected detector.
- **The limit that remains is stated for the condition that creates it.** A
  selection whose test is not an exact boolean literal still executes one of two
  bodies at import and is still not reported; so is a lambda called through a name
  in a later statement. Both are asserted as cases, and closing either needs the
  data-flow analysis this task excludes.
- **Nothing was weakened, and no production file changed.** `OperationClock`,
  N-04's accepted lifetime, both live PostgreSQL expiry constraints and every
  earlier accepted example are untouched; no dependency, configuration value,
  schema or migration changed.

Verification: 701 portal tests and 2260 bot tests pass with **no failures and —
every run executed with `-rs` — no skips** against the guarded disposable
PostgreSQL database, run serially because both suites share it; the affected
module is 63 passed and the TC-STRUCT-08/10/11 selection 94 passed. `git diff
--check` is clean, `compileall` passes under both required interpreters, and the
visual-freeze manifest verifies 14/14. `alembic check` was **not** re-run and is
not re-claimed: no schema, migration, table or model was touched. No formatter,
linter or type checker is configured.

**Nothing here is accepted.** P3.G1, RAID I-09 and RAID I-10 remain **open**
pending a fresh independent implementation review and a distinct security-focused
review. P3.2 and P3.3 have not been started.

Update 2026-08-16 (seventh, later the same day) — appended, not rewritten.
**Superseded in part by the eighth update above:** the boundary this update
declared beside its correction — that a selection in a callable position can
never be unwrapped — is true of `if flag` and false of `if True`/`if False`. The
named-expression correction itself stands; the text below is left as it was
written.

This
one **corrects the reach of the detector the sixth update corrected**, found by
fresh independent implementation re-review that took the sixth update's own rule
at its word. Recorded in §14 of
[`../review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md`](../review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md).

- **The rule was right; the code did not recognise all of it.** The sixth update
  said a lambda is decided by *when its body runs*, and that a lambda invoked where
  it is written is decidable from the AST with no name resolution. But
  `_invoked_lambda()` knew only `ast.Lambda` and a chain of `ast.Call`, so
  `NOW = (reader := lambda: datetime.now(timezone.utc))()` and the curried
  `NOW = (factory := lambda: lambda: datetime.now(timezone.utc))()()` were reported
  clean. Both bodies execute during the import; neither needs a separately stored
  name resolved. This is I-10's shape once more, now in a claim about how far a
  corrected control reaches — verified against the constructs already raised rather
  than the ones it announced.
- **The detector was widened to its own rule, not the rule trimmed to the code.**
  A callable position is now read **through** an `ast.NamedExpr`: `(reader := L)`
  evaluates `L`, binds it as a side effect, and answers that same object to the call
  standing beside it. Three lines, recursive, so a walrus around a direct lambda,
  around a curried one, or nested in another walrus is one rule. The unwrapping
  decides only *whether the body runs* — the target is still walked (a target that
  is itself an instant name is still reported, and reported first) and the lambda's
  defaults are still walked, once each and in source order.
- **The boundary is closed and stated.** `ast.NamedExpr` is the only expression
  that yields its single operand, evaluated at that point, with neither a selection
  nor a lookup. A **selection** — `(f if flag else g)()` — is deliberately not
  unwrapped, because the source does not say which body runs.
- **Proved failing first, then proved on the real module.** With only the new
  branch removed, the added case reports `{'direct': [], 'curried': []}` — the false
  negative reproduced. Inserted into the real module after `pytestmark`, each
  reproducer then failed TC-STRUCT-08 naming line 119, while a lambda **stored and
  called through its name** correctly did not fail. Each mutation was restored
  byte-for-byte, verified by digest and by `cmp`, and the clean module reports
  nothing under both the pre-correction and the corrected detector.
- **Two limits are declared rather than left to be found.** A lambda called through
  a name in a later statement, and a lambda reached through a selection, are both
  live false negatives; both are asserted as cases so neither can be mistaken for
  coverage, and closing either needs the data-flow analysis this task excludes.
- **Nothing was weakened, and no production file changed.** `OperationClock`,
  N-04's accepted lifetime, both live PostgreSQL expiry constraints and every
  earlier accepted example are untouched; no dependency, configuration value,
  schema or migration changed.

Verification: 700 portal tests and 2260 bot tests pass with **no failures and —
every run executed with `-rs` — no skips** against the guarded disposable
PostgreSQL database, run serially because both suites share it; the affected
module is 62 passed and the TC-STRUCT-08/10/11 selection 93 passed. `git diff
--check` is clean, `compileall` passes under both required interpreters, and the
visual-freeze manifest verifies 14/14. `alembic check` was **not** re-run and is
not re-claimed: no schema, migration, table or model was touched. No formatter,
linter or type checker is configured.

**Nothing here is accepted.** P3.G1, RAID I-09 and RAID I-10 remain **open**
pending a fresh independent implementation review and a distinct security-focused
review. P3.2 and P3.3 have not been started.

Update 2026-08-16 (sixth, later the same day) — appended, not rewritten.
**Superseded in part by the seventh update above:** the corrected detector this
update describes recognised an invoked lambda only where it was written bare, so
its "invoked where it is written" claim was wider than the check it announced. The
lambda rule itself stands; the text below is left as it was written.

This one **corrects the detector the fifth update added**, found by fresh independent
implementation re-review that read the code rather than the claim. Recorded in
§12 of
[`../review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md`](../review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md).

- **The guard did not enforce the invariant it stated.** The fifth update's
  detector claimed to report *any* code that reads or constructs an instant while
  the module is imported, and its `visit_Lambda()` always skipped the lambda body.
  So `NOW = (lambda: datetime.now(timezone.utc))()` — a lambda invoked where it is
  written, whose body therefore runs during the import — produced no finding. The
  offered explanation ("a lambda body runs only when a test calls it") is true of a
  stored lambda and false of an invoked one. This is I-10's shape once more: the
  control was narrower than the claim made for it, and the gap was visible in the
  AST.
- **The detector was corrected to the invariant, not the invariant narrowed to the
  detector.** A lambda is now decided by **when its body runs**. Invoked in place —
  including the curried `(lambda: lambda: ...)()()` — its body is import-time code
  and is walked; stored, returned or passed, its body stays excluded; its defaults
  run at import and are walked either way. Function and method bodies, imports,
  annotations, class bodies, decorators, `timedelta` and `timezone` are unchanged.
- **Proved on the real module, before and after.** With the pre-correction
  detector the reproducer reported nothing; with the corrected one it reports
  `datetime.now` at its own source line. Inserted into the real module after
  `pytestmark`, the invoked form and the curried form each failed TC-STRUCT-08 with
  line 119 named, while a **stored** lambda reading the same clock correctly did
  not fail — the negative control that shows the fix did not simply widen the net.
  Each mutation was restored byte-for-byte, verified by digest and by `cmp`, and
  the clean module reports nothing under either detector.
- **Nothing was weakened, and no production file changed.** `OperationClock`,
  N-04's accepted lifetime, both live PostgreSQL expiry constraints and every
  earlier accepted example are untouched; no dependency was added.

Verification: 699 portal tests and 2260 bot tests pass with **no failures and —
every run executed with `-rs` — no skips** against the guarded disposable
PostgreSQL database, run serially because both suites share it; the affected
module is 61 passed and the TC-STRUCT-08/10/11 selection 92 passed. `git diff
--check` is clean, `compileall` passes under both required interpreters, and the
visual-freeze manifest verifies 14/14. `alembic check` was **not** re-run and is
not re-claimed: no schema, migration, table or model was touched. The declared
limits are unchanged and one is restated: the detector is name-based and
syntactic, so a clock reached through an indirectly named helper, or a lambda
called through a variable, is still outside it.

**Nothing here is accepted.** P3.G1, RAID I-09 and RAID I-10 remain **open**
pending a fresh independent implementation review and a distinct security-focused
review. P3.2 and P3.3 have not been started.

Update 2026-08-16 (fifth, later the same day) — appended, not rewritten.
**Superseded in part by the sixth update above:** the detector this update
describes did not report an immediately invoked lambda, so its "any code that runs
at import" statement was broader than the check it announced. The text below is
left as it was written.

This one **corrects a claim made in the fourth update's submission**, found by fresh
independent implementation re-review. Recorded in §10 of
[`../review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md`](../review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md).

- **"Asked of the AST rather than of a reader" was not true when it was written.**
  §3.1 of the clock submission described the absence of a module-level datetime as
  asserted over the AST, and the change-log entry repeated it. Nothing asserted it:
  `tests/web/test_canonical_settings_graph.py` did not import `ast`, no case parsed
  the module, and a module-import clock could have come back without failing
  anything. The absence was real and the `OperationClock` correction was
  unaffected — the defect was in the evidence, not in the fix — but it is I-10's
  own shape one level out: a property established by reading, then described as
  established by a control.
- **The regression was added rather than the claim withdrawn.** A case now parses
  the module and fails if any code that runs **at import** reads or constructs an
  instant: module-level statements, class bodies, decorator expressions and
  default arguments are all in scope; function bodies, imports and annotations
  deliberately are not, being respectively the operation's own clock, not a clock,
  and unevaluated. `timedelta` and `timezone` are not findings, because a duration
  and a fixed offset are not instants and banning them would state a broader
  invariant than the one claimed.
- **The detector is proved, not merely run.** Three mutations of the real module —
  the reintroduced `NOW = datetime.now(timezone.utc)`, a fixed module-scope
  `datetime(...)` constructor, and a capture hidden in a default argument — each
  failed the case with the offending line named, and each was restored
  byte-for-byte, verified by digest and by `cmp`. A second committed case falsifies
  the detector against synthetic sources on every run. It reads AST semantics
  rather than text by necessity: the clean module contains seven literal
  occurrences of `datetime.now(timezone.utc)` in comments, docstrings and test
  inputs, none of them executable.
- **Nothing was weakened, and no production file changed.** `OperationClock`,
  N-04's accepted lifetime and both live PostgreSQL expiry constraints are
  untouched; no dependency was added, since the guard uses the standard library's
  `ast`.

Verification: 698 portal tests and 2260 bot tests pass with **no failures and — every
run executed with `-rs` — no skips** against the guarded disposable PostgreSQL
database, run serially because both suites share it; the whole affected module is
60 passed, the TC-STRUCT-08/10/11 selection 91 passed, and the OAuth/WebAuthn/clock
selection 575 passed. `git diff --check` is clean, `compileall` passes under both
required interpreters, and the visual-freeze manifest verifies 14/14. `alembic
check` was **not** re-run and is not re-claimed: no schema, migration, table or
model was touched. One limit is declared rather than smoothed over — the detector
is name-based, so a capture reached through an indirectly named helper is not seen;
both forms that have actually occurred here, and the alias form, are caught.

**Nothing here is accepted.** P3.G1, RAID I-09 and RAID I-10 remain **open**
pending a fresh independent implementation review and a distinct security-focused
review. P3.2 and P3.3 have not been started.

Update 2026-08-16 (fourth, later the same day) — appended, not rewritten. This
one **corrects a claim made in the third update below**, found by fresh
independent re-review. Submitted in
[`../review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md`](../review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md).

- **"The constant is now anchored to the run's own clock" was a postponement, not
  a fix.** `NOW = datetime.now(timezone.utc)` in
  `tests/web/test_canonical_settings_graph.py` was evaluated at **module import**,
  while `created_at` is stamped later by two other authorities:
  `adapters.web.repositories.utcnow()` for `oauth_transactions`, and PostgreSQL's
  `server_default = now()` for `webauthn_challenges`. `expires_at` came from the
  injected instant, the two expiry check constraints compare them, and so the
  module still had **two clocks** and still depended on elapsed wall time — the
  failure simply moved from "noon on the day it was written" to "whenever more
  than N-04's ten minutes elapse between import and execution", which collection,
  an earlier case, a debugger pause or a slow worker can each produce.
- **The correction removes the second clock rather than widening the gap.** The
  constant is gone. A function-scoped fixture reads the instant from inside the
  operation's own transaction — PostgreSQL's transaction timestamp, which is by
  definition what the database will stamp `created_at` with — and binds the
  repository's clock to the same reading, so `expires_at - created_at` is exactly
  the configured lifetime no matter how much wall time passed beforehand. No
  sleep, no margin, no extended lifetime, no relaxed constraint, no module- or
  session-scoped timestamp, and **no production file changed**. Every original
  assertion, including N-04's accepted value, is preserved.
- **Two regressions name the defect.** One asserts on both affected tables that a
  row's expiry is exactly the accepted lifetime after that row's own creation —
  false for any non-zero elapsed time under the import-time model. The other
  injects a deliberately stale instant and requires PostgreSQL to refuse both
  rows, which proves the constraint is live rather than mocked away.

Verification: 696 portal tests and 2260 bot tests pass with **no skips and no
failures** against the guarded disposable PostgreSQL database, run serially;
`alembic check` reports no new upgrade operations; `compileall` is clean under both
required interpreters; the visual-freeze manifest verifies 14/14; and two
falsification runs restored the import-time model and reproduced both the
discriminator's failure and the original `expiry_after_creation` violation, then
restored the module byte-for-byte. A production observation is recorded rather than
acted on: `OAuthTransactionRepository.create()` re-reads the clock instead of
deriving `created_at` from the operation's `now`. It is not observable as a defect,
because every production caller injects the same process clock microseconds
earlier, and broadening this task to change it was not authorised.

**Nothing here is accepted.** P3.G1, RAID I-09 and RAID I-10 remain **open**
pending a fresh independent implementation review and a distinct security-focused
review. P3.2 and P3.3 have not been started.

Update 2026-08-16 (third, later the same day) — appended, not rewritten. This
one **corrects two claims made in the second update above**, both found by fresh
independent re-review, and both the same shape as the findings they were
correcting: a property established for one object or one path and then described
as established generally. Submitted in
[`../review/phase-3-p3-g1-request-authority-and-lifecycle-remediation-submission.md`](../review/phase-3-p3-g1-request-authority-and-lifecycle-remediation-submission.md).

- **"The routes are bound to the composition the factory accepted rather than to
  `app.state`" was true of the composition and false of the settings graph.**
  `create_app()` assigned the canonical graph to `app.state.settings`, and a
  `_settings(request)` helper read `request.app.state.settings` on **every call** —
  for the client and user-agent digests, mutation-origin validation, the session
  and login cookie names and attributes, CSRF key selection and the health view.
  Starlette's `State` is an ordinary mutable namespace, so one assignment gave an
  already-validated application a second complete settings graph to serve from: a
  different accepted `Origin`, a different CSRF key, a different cookie contract
  and different keyed audit and rate-limit identities. The correction is **which
  object the handler holds**: one frozen `RequestAuthority` built from the accepted
  graph, passed into route registration and the exception handler, with the four
  `app.state` references kept as diagnostics and proved inert against a second
  independently valid graph.
- **"`aclose()` is wired to the ASGI lifecycle" was true of a normal shutdown and
  false of a refused startup.** `create_app()` ran `run_resource_checks()` at
  factory time — after the composition had built the provider's `httpx.AsyncClient`
  and its owned SQLAlchemy engine, and before the `FastAPI` object the lifespan is
  installed on existed. A refusal therefore raised out of the factory with both
  resources live, no application returned, no lifespan able to execute and no
  caller for `aclose()` on the one path where the process was being told not to
  run. The checks now run **inside** the lifespan that owns the exact accepted
  composition, so a refusal is an ASGI startup failure that never reaches
  `lifespan.startup.complete`, still closes the provider exactly once and disposes
  an owned engine exactly once, leaves a lent engine alone, and surfaces the
  original typed `ConfigurationError` even when releasing the provider also fails.

A third, smaller correction was made in the same pass rather than deferred:
`WebComposition.__init__` builds an owned engine and can then raise while building
the envelope or the provider. No composition exists on that path, so nothing could
ever have released that engine; the constructor now disposes it before re-raising.
A provider that was constructed and then rejected is deliberately **not** closed
there — its `aclose()` is a coroutine and a synchronous constructor has no loop to
await it on — and that limit is recorded rather than papered over.

Verification: 694 portal tests and 2260 bot tests pass with **no skips and no
failures** against the guarded disposable PostgreSQL database, `alembic check`
reports no new upgrade operations, the visual-freeze manifest verifies 14/14, and
six falsification mutations each failed the intended regression for the intended
reason and were restored byte-for-byte. One defect was found and fixed in the
previous remediation's own uncommitted test module while running this sweep:
`tests/web/test_canonical_settings_graph.py` pinned its clock to a literal
`datetime(2026, 8, 16, 12, 0)`, which made five database cases start failing at
12:00 UTC on the day they were written, because the repositories stamp `created_at`
from the real clock and the expiry check constraints refuse a row that expires
before it was created. The constant is now anchored to the run's own clock; no
assertion changed.

**Nothing here is accepted.** P3.G1, RAID I-09 and RAID I-10 remain **open**
pending a fresh independent implementation review and a distinct security-focused
review. P3.2 and P3.3 have not been started.

Update 2026-08-16 (second, later the same day) — appended, not rewritten. This
one **corrects three claims made in the first update below**, which independent
re-review found were stated rather than established. Submitted in
[`../review/phase-3-p3-g1-provider-and-engine-authority-remediation-submission.md`](../review/phase-3-p3-g1-provider-and-engine-authority-remediation-submission.md).

- **"A test double still can" was not a type, only a name.** The composition kept
  a `provider_double: IdentityProvider` parameter and refused only a concrete
  `DiscordIdentityProvider`. `IdentityProvider` is a **structural protocol**, so a
  wrapper, a delegating adapter or an alternate implementation holding a second
  graph's client id, client secret, redirect URI, scopes, guild id and endpoints
  passed that exclusion and then built R-03's authorization URL and R-04's token
  exchange. The parameter is **removed**: production construction takes a settings
  graph and an optional HTTP transport, and nothing else.
- **The provider was checked once and remained replaceable.** `create_app()`
  compared it at startup while `WebComposition.provider` stayed publicly
  assignable and both routes dereferenced it per request, so an already-built
  application could be made to authenticate through a graph nothing validated —
  reproduced before the fix, with the replacement provider answering R-03.
  `settings`, `engine` and `provider` are now write-once behind read-only
  properties, the routes are bound to the composition the factory accepted rather
  than to `app.state`, and the startup comparison is **deleted** rather than kept
  as a check with nothing left to detect.
- **The engine seam was justified with the wrong argument.** The first update
  recorded that `settings.database.url` has exactly one reader, so an injected
  engine could not disagree with a second consumer. One reader and an injected
  engine do not make one authority — they make the configured database selection
  **ignorable**, and the S-14/S-15 checks then prove the injected engine is usable
  rather than that it is the database the graph names. Reproduced before the fix.
  The engine is now derived from the canonical graph, with ownership stated
  explicitly so a lent engine is never disposed by an application.

Test substitution is a `WebComposition` subclass in
`tests/web/composition_harness.py`, reached by overriding two protected hooks
rather than by passing an argument, importing nothing into production and
re-asking the suite's existing two-layer disposable-database guards about the
engine it lends.

Evidence is TC-STRUCT-09 and the amended TC-STRUCT-08, now 56 cases in
`tests/web/test_canonical_settings_graph.py`; **663 portal and 2260 bot tests with
no skips**; compilation under both configured interpreters; `alembic check` clean;
the visual freeze intact; four recorded falsification runs and two before/after
reproductions, each followed by a byte-for-byte checksum comparison of the
worktree.

**Nothing is accepted by this remediation.** No accepted numeric value moved, no
configuration variable was added, renamed or removed, `.env.example` is
unchanged, no schema, migration, route, service, worker behaviour or deployment
value changed, and the visual freeze is untouched. **I-09 and I-10 both remain
open**, **P3.G1 remains open**, and **P3.2 and P3.3 have not started.**

Previous status date: 2026-08-16 (one canonical settings graph per web process, including the identity provider; the graph's completeness proved independently of its declaration; I-09 and I-10 amended again; P3.G1 open)

Update 2026-08-16 (first) — appended, not rewritten. Submitted in
[`../review/phase-3-p3-g1-canonical-settings-graph-remediation-submission.md`](../review/phase-3-p3-g1-canonical-settings-graph-remediation-submission.md).

- **A web process now has one settings authority, not several (I-09/I-10).** The
  corrections below made each settings *type* valid by construction. That is a
  property of an object, not of a process: `WebComposition` still retained the
  caller's `WebSettings`, `create_app(settings_a, composition=composition_b)`
  gave middleware, cookies, digests and startup checks A while every service used
  B, and the two services that keep a graph re-read it per operation. The graph
  is now canonicalised **once**, at the composition root, all the way down —
  every field read once, every exact base type rebuilt through the constructor
  that holds the register — `create_app` takes exactly one configuration
  authority, and a consumer that retains settings requires that one object.
- **The identity provider was the last place two authorities could meet.** The
  composition accepted a ready-made provider, so a genuine
  `DiscordIdentityProvider` built from a second valid graph — its own client id,
  client secret, redirect URI, scopes, guild id, endpoints and timeout — could
  build R-03's authorization URL and R-04's token exchange for an application
  that had validated a different graph. S-05 checks the redirect URI against the
  public origin on the graph the process validated, so the check and the value
  used could diverge. The adapter is now **built by the composition** from its
  own `settings.discord` and cannot be injected; a test double, which holds no
  Discord configuration, still can, and an injected HTTP client supplies
  transport only.
- **The graph's completeness is no longer tested against itself.** The previous
  check iterated the entries the declaration already had, so a settings-valued
  field added to a dataclass and omitted from the table passed. The expected
  topology is now derived from the dataclasses' own annotations, with a narrow,
  explicit container grammar that fails closed; and canonicalising a settings
  type the graph does not declare is a runtime refusal rather than a silent
  "nothing nested here".
- **The adversarial suite offered as evidence for the first two points did not
  reach them.** Ten of its cases engaged their lie *before* calling the genuine
  constructor, so the object refused during test construction and the
  canonicalisation boundary was never exercised; its environment case used a
  variable name the reader does not recognise and a value inside its accepted
  range, so two of its four "problems" were never problems. Both are corrected
  and both corrections are falsified rather than asserted.

Evidence is TC-STRUCT-08, a new 46-case
`tests/web/test_canonical_settings_graph.py`; **653 portal and 2260 bot tests
with no skips**; compilation under both configured interpreters; `alembic check`
clean; the visual freeze intact; and four recorded falsification runs — the
mismatched-provider path restored, the premature-engagement harness restored, one
nested classification deleted, and the unrecognised variable name restored — each
followed by a byte-for-byte checksum comparison of the worktree.

**Nothing is accepted by this remediation.** No accepted numeric value moved, no
configuration variable was added, renamed or removed, `.env.example` is
unchanged, no schema, migration, route, service, worker behaviour or deployment
value changed, and the visual freeze is untouched. **I-09 and I-10 both remain
open**, **P3.G1 remains open**, and **P3.2 and P3.3 have not started.** The
residuals stated below are unchanged.

Previous status date: 2026-08-15 (N-23's worker lease corrected to an exact 60 seconds and the lease/heartbeat ordering question withdrawn; exact built-in `int` required at every register gate; the five I-10 settings types made valid by construction; I-09 and I-10 amended; P3.G1 open)

Update 2026-08-15 (seventh, later the same day) — appended, not rewritten. This
one **corrects a claim made in the sixth update below**, which independent review
found wrong. Submitted in
[`../review/phase-3-p3-1-n-23-exact-lease-remediation-submission.md`](../review/phase-3-p3-1-n-23-exact-lease-remediation-submission.md).

- **N-23's worker lease is a value, not a ceiling.** The settings-construction
  remediation defined `lease_seconds` as `PolicyBound(minimum=1, maximum=60)`,
  which accepted every exact integer from 1 to 60 as a lease. The accepted row
  states `60 seconds, heartbeat at most every 20 seconds` — one sentence, a lease
  **value** and a heartbeat **maximum** — and SM-05's
  `lease_expires_at = now() + 60s`, the logical schema's claim and renewal
  statements and the operational contract's `N-23 + N-44` recovery bound all read
  it as a fixed 60. A one-second lease was therefore a contradiction of the
  accepted documents, not a permitted tightening, and would have lost a live
  claim to ordinary heartbeat scheduling. The runtime entry is now
  `PolicyBound(minimum=60, maximum=60, policy="N-23")`; `heartbeat_seconds` is
  **unchanged** at 1…20.
- **The lease/heartbeat ordering question recorded below is withdrawn, not
  answered.** `lease_seconds=1, heartbeat_seconds=20` was cited as an
  in-register configuration proving an ordering rule was missing. It was never in
  the register — it was in the implementation. With the lease exactly 60 every
  accepted heartbeat is already far inside it, so **no ordering rule was added
  and none is needed**, **no relationship involving N-45 has been accepted**, and
  **nothing about N-23 blocks P3.3.** What P3.3 still owns is the *consumer*
  evidence for the worker's lease, heartbeat, attempt, timeout and queue bounds.

Evidence is TC-STRUCT-07 and TC-LIM-06 as corrected, with 20 further cases in
`tests/web/test_settings_construction_validation.py` (165 total, up from 145);
607 portal and 2260 bot tests with no skips; `alembic check` clean; the visual
freeze intact; and a falsification run restoring only the `1…60` entry in memory,
in which 10 of the new cases fail while every other portal test stays green and
`git status --short` is identical before and after.

**Nothing is accepted by this correction.** No accepted numeric value moved —
N-23's lease was and remains 60 seconds — no configuration variable was added,
renamed or removed, `.env.example` is unchanged (it already shipped
`WORKER_LEASE_SECONDS=60`), and no state machine, schema, migration, route,
service, worker behaviour or deployment topology changed. **I-09 and I-10 both
remain open**, **P3.G1 remains open**, and **P3.2 and P3.3 have not started.**
The other residuals stated below are unchanged and still stand:
`WEB_WEBAUTHN_USER_VERIFICATION` and `WEB_RECOVERY_GRANT_MINUTES` are validated
but read by no runtime consumer, N-09/N-10 have no P3.1 route consumer, N-21/N-22
have no consumer at all, and the worker's lease/heartbeat/attempt consumers are
P3.3's.

Update 2026-08-15 (sixth, later the same day) — appended, not rewritten. Two
connected corrections, submitted together in
[`../review/phase-3-p3-1-settings-construction-validation-remediation-submission.md`](../review/phase-3-p3-1-settings-construction-validation-remediation-submission.md).

- **The session validator did not require an exact `int` (I-09, sixth amendment).**
  The fifth remediation made both gates share one definition, and that
  definition still said `isinstance(value, int) and not isinstance(value, bool)`.
  That refuses `bool` and every float and accepts **every other subclass of
  `int`** — and an `int` subclass may override its rich comparisons, which
  Python consults in preference to the left operand's when the right-hand type
  is a subclass. `dataclasses.replace(settings, max_sessions_per_account=LyingInt(10))`
  therefore survived construction *and* `SessionPolicy.derive()`, and
  `len(live) >= maximum` was false for every live-session count: **N-66
  inoperative for the third time**, through the supported public constructor.
  The accepted rule is now the exact built-in type, `type(value) is int`.
- **The five I-10 settings types are now valid by construction (I-10).**
  `RateLimitSettings`, `BoundsSettings`, `WebAuthnSettings`,
  `DatabasePoolSettings` and `WorkerSettings` each enforce their accepted
  register in `__post_init__`, from one runtime `PolicyBound` per field that the
  environment reader and the constructor both call. The accepted non-numeric
  shapes are enforced with them, N-21's one cross-field rule is enforced at the
  object owning both fields, and every seam that re-reads a settings value reads
  each attribute once and validates that read.

Evidence is TC-AUTH-19(m), TC-STRUCT-07 and TC-LIM-06; 587 portal and 2260 bot
tests with no skips; `alembic check` clean; the visual freeze intact; and two
recorded falsification runs in which 16 of 22 new session cases fail against the
reviewed `isinstance` predicate and 81 of 145 new settings cases fail against the
previous reader-only model, while every pre-existing test stays green — neither
existing suite contained a counterexample.

**Nothing is accepted by this remediation.** No accepted numeric value moved, no
configuration variable was added, renamed or removed, no schema or migration
changed, and no deployment value changed. **I-09 and I-10 both remain open**,
**P3.G1 remains open**, and **P3.2 and P3.3 have not started.** Stated residuals:
N-09/N-10 have no P3.1 route consumer and N-21/N-22 have no consumer at all;
`WEB_WEBAUTHN_USER_VERIFICATION` and `WEB_RECOVERY_GRANT_MINUTES` are validated
but read by no runtime consumer; the worker's lease/attempt consumers are P3.3's;
and no ordering relationship between N-23's lease and heartbeat is enforced,
because no accepted document states one — that is an open maintainer question,
not a decision taken in a constructor.

Deferred validation gap recorded 2026-08-15: RAID **I-10** now tracks five
public `WebSettings` sub-dataclasses whose accepted numeric and related policy is
enforced by the environment reader but not by their own construction boundaries:
`RateLimitSettings`, `BoundsSettings`, `WebAuthnSettings`,
`DatabasePoolSettings` and `WorkerSettings`. This is not reported as an
environment-string bypass and no implementation change is claimed. It is a
future scoped remediation with security priority for rate limits, web bounds and
WebAuthn, availability priority for the database pool, and a mandatory pre-P3.3
condition for worker bounds. The acceptance contract explicitly requires exact
built-in integers (`type(value) is int`), direct/`replace`/subclass and real
consumer tests, preservation of aggregated redacted environment errors, and
independent review. See
[`../review/phase-3-settings-construction-validation-gap.md`](../review/phase-3-settings-construction-validation-gap.md).

Update 2026-08-15 (fifth, later the same day) — appended, not rewritten. Codex's
independent re-review of the session-bounds-construction remediation returned
**one blocking counterexample**, reported from two perspectives: F1 in the
implementation review and S1 in the distinct security-focused pass. They describe
the same defect, and it is a defect of *where the rule is defined* rather than of
what the rule says.

- `SESSION_CEILINGS` gave both enforcement gates the same **bounds** and left each
  to state independently what a value of these fields may **be**.
  `SessionSettings.__post_init__` required an actual `int`, never a `bool`,
  positive and within its ceiling. The derived-policy gate restated the rule as
  the two ordering comparisons `value < 1` and `value > ceiling`, and dropped the
  type half.
- Two ordering comparisons are not a whole-number rule, because `float("nan")`
  makes both of them false. A non-finite `max_sessions_per_account` therefore
  survived `SessionPolicy.derive()`, and `len(live) >= maximum` in
  `_enforce_session_limit` was false for **every** live-session count — **N-66
  revoked nothing**, and the bound on how many stolen or forgotten session
  credentials can be live for one account was inoperative.
- The route was ordinary, not forgery: `derive()` accepts `SessionSettings`
  subclasses deliberately, so a subclass whose inherited `__post_init__` observes
  the valid stored integer can answer differently on the single later derivation
  read. No `object.__new__`, no mutation of a frozen instance, no forged
  `SessionPolicy` and no private helper was needed.

Remediated on 2026-08-15 in
`docs/review/phase-3-p3-1-od-44-session-policy-numeric-validation-remediation-submission.md`
with **one authoritative runtime definition** rather than a third restatement.
`session_policy_problem` / `session_policy_problems` sit beside `SESSION_CEILINGS`
in `application/web/config.py`, and both `SessionSettings.__post_init__` and
`_validate_policy_values` in `application/web/sessions.py` — the function
`SessionPolicy.__post_init__` and `SessionPolicy.derive()` both go through — call
them. The accepted type is an `int` and never a `bool`, which refuses floats as a
class: integral-looking, fractional, infinite and NaN alike, rather than naming
the one non-finite value a review happened to find. Evidence is TC-AUTH-19(l) and
the new TC-SESS-08b in `tests/web/test_session_policy_numeric_validation.py`, 420
portal tests and 2260 bot tests passing with no skips, `alembic check` clean, and
a **recorded falsification run**: with the reviewed two-comparison validator
restored in memory, nine of the new cases fail while the whole pre-existing
54-test session-lifetime suite stays green — the earlier suite contained no
counterexample.
**Nothing is accepted by this remediation.** It is submitted for a fresh
independent implementation re-review and a separately reported security-focused
re-review; **P3.G1 remains open, and P3.2 has not started.** I-09 is amended
rather than closed. No accepted numeric value moved, no configuration variable was
added or renamed, no schema or migration change was made, and no deployment value
changed. The stated residual is that the other `WebSettings` sub-dataclasses have
**not** been audited for the same divergent-gate shape.

Previous update 2026-08-15 (fourth, later the same day) — appended, not rewritten. Codex's
independent re-review of the idle-policy-construction remediation returned **three
blocking counterexamples**, and together they say that an extensible policy object
was the wrong authority boundary rather than one that needed another guard.

- **F1.** `SessionIdlePolicy.from_settings()` validated only positivity, and
  `SessionSettings` was a public frozen dataclass with no construction-time
  validation. `SessionSettings(..., emergency_idle_minutes=60, ...)` was therefore
  an accepted object, and the policy derived from it returned sixty minutes for
  both break-glass methods. Closing the policy's constructor achieved nothing
  while the numbers it read were unconstrained, and environment-reader validation
  cannot make invalid instances of a public settings type impossible.
- **F2.** The refresh statement was generated by iterating the policy's public,
  overridable `__iter__`. An ordinary subclass inherited the supported factory and
  replaced the SQL's mapping while `for_method()` went on reporting fifteen
  minutes; the reproduction bound `idle_seconds = 3600.0` for all three methods.
  This is ordinary Python subclassing, not forgery, and the previous submission
  was wrong to treat it as out of scope.
- **F3.** `SessionService.__init__()` accepted a repository *and* an independently
  supplied policy and never required them to be the same. Correct wiring at the
  two production sites was true and was not an invariant of the boundary.

Remediated on 2026-08-15 in
`docs/review/phase-3-p3-1-od-44-session-bounds-construction-remediation-submission.md`
by simplifying the construction model rather than adding guards.
**`SessionIdlePolicy` is deleted.** `SessionSettings` validates the accepted
numeric register in `__post_init__`, so an out-of-register instance cannot exist
however it was built (F1). `SessionRepository` **derives** a `SessionPolicy` from
settings, reading each configured number exactly once, and accepts no policy
object; the `CASE` branches are generated by walking `AuthMethod` and asking an
explicit classification table, so there is nothing to iterate and nothing to
subclass into the SQL (F2). `SessionService` reads its bounds from the repository
and has no policy argument, so a graph with two independently configured bounds
sources is not constructible (F3). An authentication method with no explicit
classification now refuses at import and at repository construction instead of
inheriting the shorter window by inference. Evidence is TC-AUTH-19(k), 392 portal
tests and 2260 bot tests passing with no skips, `alembic check` clean, and the
recorded before/after reproductions of all three counterexamples.
**Nothing is accepted by this remediation.** It is submitted for a fresh
independent implementation re-review and a separately reported security-focused
re-review; **P3.G1 remains open, and P3.2 has not started.** I-09 is amended
rather than closed. Reachability is unchanged and still stated plainly: no P3.1
HTTP route calls `touch()`, so this correction is proven at the service and
repository boundary and not in request handling. No schema change, no migration
edit, no configuration-variable rename and no deployment-value change was
involved.

Previous update 2026-08-15 (third, later the same day) — appended, not rewritten. Codex's
independent re-review of the session-touch policy remediation returned **one
blocking finding**, and it is the same authority in a third position rather than a
new defect. Removing `idle` and `expected_auth_method` from
`SessionRepository.touch()` had moved the method-to-duration pairing into
`SessionIdlePolicy`'s public dataclass constructor: the mapping that gives *every*
authentication method N-06's 60-minute window is complete, duplicate-free and
positive, so the constructor accepted it, and a repository built with it selected
60 minutes for persisted WebAuthn and recovery-grant rows — N-15's 15-minute idle
limit bypassed again, up to the 60-minute emergency absolute bound. The policy
tests proved completeness, uniqueness and positivity and never attempted a
complete but semantically false mapping, so the previous submission's claims that
no supported API could pair a method with another policy's duration, and that
policy was built once and injected, were both false. A related composition defect
was found with it: `WebComposition.services()` built one policy for the repository
while `SessionService.__init__()` built another from settings — equivalent in
production, but two derivations rather than one instance. Remediated on 2026-08-15
in
`docs/review/phase-3-p3-1-od-44-session-idle-policy-construction-remediation-submission.md`:
the policy has **no public constructor**, its one factory takes `SessionSettings`,
which methods receive the emergency window is classification derived inside it
from `AuthMethod.is_break_glass`, and one instance is built at the composition
root and injected into the repository *and* the service. `SessionSettings` remains
the sole numeric source and every pair of values its contract accepts — including
an ordinary window shorter than the emergency one — maps by classification.
Evidence is TC-AUTH-19(j), 16 killed mutants with byte-identical restoration
verified by digest, 381 portal tests and 2260 bot tests passing with no skips.
**Nothing is accepted by this remediation.** It is submitted for a new Codex
independent implementation re-review and a separately reported security-focused
re-review; **P3.G1 remains open, and P3.2 has not started.** I-09 is amended
rather than closed. Reachability is unchanged and still stated plainly: no P3.1
HTTP route calls `touch()`, so this correction is proven at the service and
repository boundary and not in request handling — it is required now because P3.2
is intended to consume this API. No schema change, no migration edit and no
configuration change was involved.

Previous update 2026-08-15 (second, later the same day) — appended, not rewritten. Codex's
independent implementation and security re-reviews of the session-lifetime
remediation returned **one blocking finding**: the break-glass idle-policy
correction had been made in `SessionService` only. `SessionRepository.touch()`
still accepted `idle` and `expected_auth_method` as independent arguments and
verified only that the method matched the row, so a caller supplying a
break-glass session's **correct** method beside N-06's 60-minute duration matched
and extended that session's idle window to its absolute bound — N-15's 15 minutes
bypassed through the supported lower-level API, with every stated check passing.
The repository test offered as proof supplied a *mismatched* method and never
exercised that pairing; it has been replaced, not retained. Remediated on
2026-08-15 in
`docs/review/phase-3-p3-1-od-44-session-touch-policy-remediation-submission.md`:
the refresh duration is no longer a parameter at any layer, being selected inside
the atomic `UPDATE` by `CASE auth_method` from an immutable validated
`SessionIdlePolicy` built from configuration and injected once at the composition
root. Evidence is the rewritten TC-AUTH-19, 13 killed mutants with byte-identical
restoration verified by digest, 362 portal tests and 2260 bot tests passing with
no skips. **Nothing is accepted by this remediation.** It is submitted for a new
Codex independent implementation re-review and a separately reported
security-focused re-review; **P3.G1 remains open, and P3.2 has not started.**
I-09 is amended rather than closed. Reachability is unchanged and still stated
plainly: no P3.1 HTTP route calls `touch()`, so this correction is proven at the
service and repository boundary and not in request handling — it is required now
because P3.2 is intended to consume this API.

Previous update 2026-08-15 — appended, not rewritten. Codex's independent re-review of the
provider-binding and rotation-integrity remediation returned **two further
blocking findings**, both in the session idle refresh: `touch()` could revive an
idle-expired session from a stale record, and it gave WebAuthn and recovery-grant
sessions N-06's 60-minute idle window instead of N-15's 15-minute one. A refused
refresh was additionally reported as success. Both are remediated on 2026-08-15
(`docs/review/phase-3-p3-1-od-44-session-lifetime-remediation-submission.md`)
together with the documentation the rotation-lifetime correction left
outstanding: liveness is now enforced inside each conditional write, neither
continuation writes `absolute_expires_at`, the idle duration follows the persisted
authentication method, and both refusals are typed. Evidence is TC-AUTH-18 and
TC-AUTH-19, nine killed mutants with byte-identical restoration, 354 portal tests
and 2260 bot tests passing with no skips. **Nothing is accepted by this
remediation.** It is submitted for a new Codex independent implementation
re-review and a separately reported security-focused re-review; **P3.G1 remains
open, and P3.2 has not started.** New issue **I-09** tracks it. Note for the
reader: no P3.1 HTTP route calls `touch()`, so that half of the correction is
proven at the service and repository boundary and not in request handling.

Previous status date: 2026-08-14 (I-07 and I-08 ruled; OD-44 implemented, re-reviewed by Codex, and remediated again for provider binding and rotation integrity; P3.G1 open)

Baseline: v1.5; accepted by Peter Duscha on 2026-08-02

Overall health: Amber — Phases 0–2, the frontend visual-design track, Phase 3
readiness and P3.0 are accepted. P3.G0 is closed. **P3.1 was implemented,
reviewed by Codex, and partly remediated; it is not accepted.** The disposable
PostgreSQL prerequisite was confirmed on 2026-08-14 and the package's database
evidence was executed against it. Codex returned three blocking findings and one
important finding; two are remediated and Peter has now ruled **I-07** and
**I-08**. The OD-44 durable completion binding is now **implemented** as
migration 0009, with real-PostgreSQL concurrency, constraint, rollback and
mutation evidence, and is resubmitted. Codex's independent and security re-reviews
of that package returned two further blocking items — the completion claim did not
bind the transaction's recorded **provider**, and the partial unique index Peter
approved needed rotation integrity behind it — and both are now remediated in the
same revision 0009 and the OAuth, session and provider boundaries, with
TC-AUTH-15/16/17 and six killed mutations. P3.G1 now requires a Codex independent
implementation re-review plus a distinct security-focused pass before P3.2 may
start. Staging does not exist, so
every staging-class check in the traceability contract remains unrun. Gemini
production integration remains blocked.

## Decisions ruled on 2026-08-14

| # | Decision | Note | Blocks |
|---|---|---|---|
| I-07 / OD-44 | Durable one-way completion binding approved, with one authoritative unique `sessions.oauth_transaction_id` and no reverse FK | [`../review/phase-3-p3-1-sm-01-completion-binding-decision.md`](../review/phase-3-p3-1-sm-01-completion-binding-decision.md) | **Implemented 2026-08-14** as migration 0009; re-review still blocks P3.G1. See [`../review/phase-3-p3-1-od-44-remediation-submission.md`](../review/phase-3-p3-1-od-44-remediation-submission.md) |
| I-07 / OD-44 §8 | The scoped partial unique index confirmed as authoritative, **conditionally** on rotation-chain integrity; the completion claim must also bind the transaction's recorded provider | [`../review/phase-3-p3-1-sm-01-completion-binding-decision.md`](../review/phase-3-p3-1-sm-01-completion-binding-decision.md) §8 | **Implemented 2026-08-14** in the same uncommitted revision 0009 and the OAuth, session and provider boundaries; re-review still blocks P3.G1. See [`../review/phase-3-p3-1-od-44-provider-binding-remediation-submission.md`](../review/phase-3-p3-1-od-44-provider-binding-remediation-submission.md) |
| I-08 / OD-45 | Service/constraint evidence remains at P3.G1; direct-HTTP portions of TC-BG-05b/c/e are mandatory at P3.G2 | [`../review/phase-3-p3-1-tc-bg-05-http-evidence-decision.md`](../review/phase-3-p3-1-tc-bg-05-http-evidence-decision.md) | P3.G2 evidence; no waiver |

## Milestone status

| Milestone | State | Gate | Evidence / next condition |
|---|---|---|---|
| Phase 0 — Discovery and architecture | Accepted | Closed 2026-07-30 | `docs/discovery/phase-0-handoff.md`, `docs/review/phase-0-submission.md` |
| Phase 1 — Database foundation | Accepted | Closed 2026-07-31 | Maintainer acceptance at the head of `docs/review/phase-1-submission.md` |
| Phase 2 — Import and reconciliation | Accepted | Closed 2026-08-12 | C-24 and B-1 closed after independent re-review returned no findings; Peter Duscha accepted the data-integrity, identity and migration-safety gate. See `docs/review/phase-2-c-24-independent-re-review-2026-08-12.md` and change-log C-24-R. |
| §12.1 frontend visual-design track | Accepted | Closed 2026-08-13 | Peter accepted Steps 1–5, including real-mobile inspection. Fourteen frozen implementation/asset files verify against `docs/review/phase-3-visual-freeze-manifest.sha256`; current token and contrast tools pass. See `docs/review/phase-3-visual-prototype-handoff.md`. |
| Phase 3 — authentication, read-only portal and Council administration | P3.0 through **P3.3 accepted** | P3.G0 closed 2026-08-13; P3.G1 closed 2026-08-16; P3.G2 closed 2026-08-18; **P3.G3 closed 2026-08-19; P3.4 authorized** | P3.3 passed independent implementation and distinct security-focused reviews; Peter accepted `C-P3.3-I`, recorded the outstanding contract decisions in `C-P3.3-J`, accepted P3.3 and authorized P3.4. I-06 and A-05 remain open production-exposure conditions. Gemini production integration remains blocked until its later contract gate. |
| Phase 4 and later | Not ready | Predecessor gates apply | No later implementation is authorized. Follow implementation-plan §12.0 and package-specific definitions of ready. |

## Current critical path

1. **P3.0 contract/security design package — delivered 2026-08-13.** Produced
   from `docs/review/phase-3-p3-0-claude-prompt.md`. It adds no protected route
   and no framework scaffold. Five proposals need Peter's decision: a separate
   `freedom-worker` service, the tighter break-glass route boundary, apply-as-a
   -durable-job, the P3.0-proposed numeric values, and ADR 0010.
2. **P3.G1 — closed 2026-08-16; P3.2 is the current package.** P3.1 was
   delivered on 2026-08-14 from `docs/review/phase-3-p3-1-claude-prompt.md`,
   against a confirmed guarded disposable PostgreSQL database, and reviewed by
   Codex the same day. Two findings were remediated — the incomplete OAuth
   refusal auditing and the inaccurate migration reporting — and are recorded in
   `docs/review/phase-3-p3-1-remediation-submission.md`. Peter approved the
   durable one-way completion binding (OD-44) and moved only the unavailable
   HTTP evidence to P3.G2 (OD-45). The completion binding **was implemented on
   2026-08-14** as migration 0009 with the required concurrency, constraint,
   rollback and mutation evidence, recorded in
   `docs/review/phase-3-p3-1-od-44-remediation-submission.md`.
   Codex completed the independent implementation review and distinct
   security-focused pass on 2026-08-16; Peter accepted the package and closed
   P3.G1. P3.2 may now implement the member reads, identity evidence and access
   administration package. P3.3 remains behind P3.G2.
3. **Coordinated implementation.** Claude owns the backend foundation;
   Gemini owns production Jinja/static/HTMX integration only against accepted
   route/view-model contracts; Codex supplies independent and separate
   security-focused review recommendations. Peter records gate decisions.
4. **Backend contract package.** Authentication and server-side authorization
   precede every protected route. The measured 9.57-second, 32-Actor preview
   requires a durable asynchronous/progressive design rather than a synchronous
   HTTP handler or restart-unsafe in-memory queue.
5. **Stop at the contract/security review.** Gemini production integration does
   not begin until Claude's route/view-model contracts are stable and accepted.

## Closed readiness inputs

- Project reconciliation and accepted visual baseline commit: completed
  2026-08-13 without production implementation.
- Phase 2 gate: accepted 2026-08-12.
- OD-16 and OD-17: closed 2026-08-12.
- Backend/frontend/review delivery-agent allocation: Claude/Gemini/Codex.
- §12.1 visual direction: accepted 2026-08-13.
- Visual implementation freeze: 14/14 manifest entries verified.
- Static evidence tools on 2026-08-13: CSS tokens 71 defined, 62 referenced,
  zero undefined; contrast self-tests 11 passed; contrast matrix 49 pairs, 48
  passed, one disabled-state exemption, zero failures.

## Open Phase 3 conditions

- maintainer/reviewer availability windows before calendar forecasting;
- confirmed development, disposable PostgreSQL and staging environments — the
  disposable database was **confirmed on 2026-08-14** (`freedom_test`, reached
  over the local Unix-domain socket, proven through the repository's own
  `assert_disposable_target` / `verify_connected_unix_socket_target` guards) and
  the separate `freedom-web` virtualenv now exists; **staging still does not**,
  so every staging-class check in the traceability contract is unrun;
- expansion of the accepted traceability categories to exact implemented tests
  and evidence during each implementation handoff;
- accepted backend route/view-model contracts before production frontend work —
  accepted at P3.G0, with the later P3.G2/P3.G3 freeze gates still required;
- implementation and verification of the accepted configuration, deployment,
  monitoring and rollback contracts for the new `freedom-web` process; and
- two quantities remain unmeasured and block no P3.0 acceptance but must be
  measured before production: real-folder apply duration and worker peak memory.

## Scope controls

- `design-prototype/` remains static reference material and must not be imported
  or served by production code.
- Phase 3 remains read-only for character game state. Council character-link
  management and snapshot-import control are authorized administrative flows;
  generic character corrections and controlled-vocabulary editors remain with
  their owning later typed packages.
- The former Claude contrast-tooling prompt is superseded without execution. It
  is not a backend implementation prompt.
- No deployment, Caddy change, OAuth registration, production database change,
  Foundry mutation or Google Sheet mutation is authorized by reconciliation.

## Historical evidence

The detailed Phase 2 remediation chronology remains in the dated records under
`docs/review/`, `docs/operations/` and `docs/project-management/change-log.md`.
This current-status document intentionally does not repeat superseded open-gate
statements; Git history retains the earlier status narrative.

## Next status update

Update when P3.2 is submitted to P3.G2, or earlier if a new decision, critical
risk or environment constraint emerges. I-06 and A-05 must remain visible until
their staging/production-exposure acceptance criteria are satisfied.
