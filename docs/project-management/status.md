# Project status

Status date: 2026-08-12 (Phase 2 gate accepted)

Baseline: v1.5; accepted by Peter Duscha on 2026-08-02

Overall health: Amber — Phase 2 is accepted and Phase 3 readiness planning is
released. Phase 3 implementation is not yet opened because its separate
definition-of-ready inputs remain outstanding.

## Milestone status

| Milestone | State | Gate | Evidence / next condition |
|---|---|---|---|
| Phase 0 — Discovery and architecture | Accepted | Closed 2026-07-30 | `docs/discovery/phase-0-handoff.md`, `docs/review/phase-0-submission.md` |
| Phase 1 — Database foundation | Accepted | Closed 2026-07-31 | Maintainer acceptance is recorded at the head of `docs/review/phase-1-submission.md` |
| Phase 2 gate decision — supersedes the historical row below | **Accepted** | **Closed 2026-08-12** | C-24 and B-1 closed after independent re-review returned no findings. Peter Duscha accepted the data-integrity, identity and migration-safety gate. See `docs/review/phase-2-c-24-independent-re-review-2026-08-12.md`. |
| Phase 2 — Import and reconciliation | **The independent gate review was performed 2026-08-09 and recommended the gate not be closed.** I-1 is closed; **B-1 is open after ten remediations** and awaits independent **re**-review | Deferred | Disposable migration, backup/restore and runtime-role evidence passed 2026-08-05. Rehearsal A (non-live folder, 35 Actors) passed end to end on module 1.0.5 including step 10, §8.1 and both halves of §8.2. Rehearsal B (active folder, 32 Actors) previewed with **0 errors, 0 warnings**, all 32 Actors accounted for, zero unexplained identity discrepancies, nothing applied. Five rehearsal findings RA-1…RA-5; all closed or ruled (RA-1 profile `2026-08-09.1`; RA-2 change-log C-10, **corrected by C-12**; RA-5 change-log C-11; RA-3 referred to Phase 3; **RA-4's procedure note is now written into §6 step 10**). The Data Owner attestation was **signed 2026-08-10** and field profile `2026-08-09.1` **reviewed and accepted** the same day. **The independent review ([`../review/phase-2-gate-independent-review-2026-08-09.md`](../review/phase-2-gate-independent-review-2026-08-09.md)) then recommended against closing the gate**, on one Blocking finding (B-1, the lost-pin miss rule) and one Important finding (I-1, the canonical key boundary). Both are remediated in [`../review/phase-2-b-1-settlement-remediation.md`](../review/phase-2-b-1-settlement-remediation.md), 2026-08-10, and **carry no independent review**. The re-review of that record **accepted I-1 as closed and held B-1 open**: the settlement probe still inferred the endpoint's accept order from the client's issuance order, which the single-threaded server does not guarantee when the submission arrives through Caddy and the probe does not. A second remediation (S-B.1, change-log **C-14**) was **also held open**, because Caddy documents `caddy_http_requests_in_flight` as the requests *currently being handled* — not as evidence that the proxy is holding nothing — so the false miss remained reachable. B-1 was remediated a third time on 2026-08-10 — the probe and the gauge withdrawn, settlement the endpoint being stopped and staying stopped until the outcome is recorded, with a new step 4 to detect the residual after the restart (change-log **C-15**) — and the re-review **held it open again**: stopping the upstream does not settle a request the proxy holds and has not yet dialled upstream for, which makes its first dial after the restart, and "no upstream retry window" governs retries after a failed attempt rather than a first attempt that has not happened. Step 4 detected the resulting duplicate without preventing the false miss that authorized it. **B-1 was therefore remediated a fourth time on 2026-08-10 and is still open** (change-log **C-18**), on the maintainer's ruling between the two routes the reviewer offered: settlement now terminates the whole ingress path — the endpoint **and** Caddy, verified as absent processes rather than as drained ones — and step 4 brings the endpoint back behind a single-use route with the episode's own path retired, so a request held by a hop this host cannot terminate carries an address that no longer reaches the application. The cost is host-wide downtime for the duration of a reconciliation. **The re-review of C-18 on 2026-08-11 held B-1 open for the fifth time**, on one Blocking and two Important findings, and B-1 was remediated a fifth time the same day (change-log **C-19**) — **C-18's rule stands and none of it is withdrawn**. The Blocking finding: S-I.3 ("nothing will bring either of them back") was required by the procedure but evidenced only by `systemctl show caddy -p Restart` returning `no`, which speaks only to a process exiting on its own and is silent on socket activation, timers, path units, units that pull Caddy in, supervisors outside systemd and a second route to the endpoint's port; S-I.3 is now four checks with commands, any of which coming back positive **or being unreadable** is Unsettled, with the privileged half explicitly naming an operator without `sudo` as unable to establish it — the first worked example of a reachable **Unsettled**, which had been a standing open question. The two Important findings: C-18's claimed test mutation **had not been run as described** — the two settlement tests were hand-written copies whose sequences diverged, so deleting `proxy.terminate()` blocked on a `join()` instead of failing on the named assertion — and the pair is now rebuilt on one shared scenario with the mutation executed and its output recorded; and step 4 restored service **only after a settled miss**, leaving a hit, an ambiguous result and an unsettled episode with no executable way to bring the host back, so step 4 now has a restoration branch for every outcome, differing only in what answers the submission path afterwards. **The re-review of C-19 on 2026-08-11 held B-1 open for the sixth time**, on two Blocking findings, and B-1 was remediated a sixth time the same day (change-log **C-20**) — **neither C-18's nor C-19's rule is withdrawn**. First: C-19's S-I.3d could not establish its stated negative, because it listed names instead of reading jobs — `ls -la /etc/cron.d/` never opens a cron file, `/etc/crontab` and the other users' crontabs were not read, and a container listing says nothing about restart policies — which is the same overclaim C-19 itself identified for timer names one check earlier. S-I.3d is now a **bounded** inventory that states its bound: every start mechanism the topology record documents, read in full, with a user outside that record being Unsettled rather than a judgement call. Running it read-only against this host immediately found what the old check could not — **LXD is installed**, socket-activated, and C-19's evidence had run `docker ps -a` and `podman ps -a` and truthfully reported "no container runtime" while never looking at the one that is here; whether it holds an instance needs privilege these sessions do not have, so it is recorded as **Unsettled rather than passed**. Because no inventory forbids what happens after it is taken, **S-D gains S-D.2**: the same readings are taken at both ends of the down window and compared, and any difference is Unsettled rather than a miss — which is what actually closes the reviewer's window, since a start from an unenumerated mechanism still mints a new `InvocationID`. **A miss may not be recorded without the comparison.** Second: C-19's unresolved branch opened "the host is down now" and told the maintainer to `start` Caddy, but *Unsettled* expressly includes a Caddy still running and the hit branch reclassifies to Ambiguous **after** both services are back up — and `systemctl start` against a running unit is a no-op that reports success, so the amended Caddyfile need never load and the live submission route would survive the branch that exists to retire it. The branch now reads its entry state and uses `reload` when Caddy is active, with the rollback copy taken before the edit and `caddy validate` before anything loads; the foreground endpoint is left running if it is running. Writing S-D.2 also produced another self-reported overclaim: the first draft offered `NRestarts` as a restart detector, and the host shows `NRestarts=0` beside a non-zero `ActiveExitTimestampMonotonic` — it counts only `Restart=`-driven restarts, so it would have been silent for exactly the case S-D.2 exists to catch. **The re-review of C-20 on 2026-08-11 held B-1 open for the seventh time**, on one Blocking finding and one Important, and B-1 was remediated a seventh time the same day (change-log **C-21**) — **nothing in C-18, C-19 or C-20 is withdrawn except one sentence of C-20's**. The Blocking finding: S-D.2 detected only *Caddy* restarts. Its persistent readings — `InvocationID`, both timestamps and the journal — belong exclusively to `caddy.service`, and the listener list is sampled at the two ends of the window rather than being a state, so an unenumerated mechanism that transiently starts the endpoint and another listener on the public port, receives a request held upstream, commits it and exits leaves every reading unchanged and a miss was permitted. C-20's contrary sentence — that such a mechanism "still mints a new `InvocationID`" — is **withdrawn as false**: it holds only for a mechanism that starts Caddy, which is precisely the class S-I.3d's bound admits it cannot enumerate. S-D.2 now takes a third reading at both ends, the **commit watermark** over `foundry_snapshots` and over `audit_events` for the `foundry_snapshot` entity, and that is what a miss rests on: it reads the destination rather than the route, both tables are append-only with a trigger rejecting `UPDATE`/`DELETE`, so the counts move for any acceptance inside the window whoever served it and whether or not that process still exists. The counterexample is now **executed** rather than asserted, in `tests/test_snapshot_recovery_settlement.py`, with a control and a run mutation; C-20's test had only asserted that the procedure contained the proposed readings. The Important finding: S-I.3d's presence checks passed several names to one `command -v` and derived their conclusion from its exit status; both are now per-name loops. The finding's stated mechanism does not hold on this host — `bash` 5.2.21 and `dash` both exit `0` when at least one name is found, so the old line printed both LXD paths and no false conclusion — and the remedy is adopted anyway, because POSIX defines `command -v` for one operand and because the aggregated output is what let C-19's LXD gap stand. **The re-review of C-21 on 2026-08-11 held B-1 open for the eighth time**, on one Blocking finding, and B-1 was remediated an eighth time the same day (change-log **C-22**) — **nothing in C-18 to C-21 is withdrawn**, and the discovery-command correction was accepted as described. The Blocking finding: the commit watermark is still a comparison of two instants, and the miss is written down by hand *after* the second of them, so an unenumerated endpoint and proxy that start after the closing reading can commit the held request before the record is made — every reading matches, and the recorded miss is false. Holding the known Caddy and endpoint processes down does not prevent it, because the counterexample uses processes outside that inventory, and step 4's later query can discover the mistake but cannot make an already-recorded miss true; C-21's test had stopped its transient ingress *before* the closing reading, so it proved the watermark catches a commit between its two samples and not that the interval through recording is closed. **S-D gains S-D.3**: the closing watermark and the repeated query are taken inside a transaction holding `LOCK TABLE foundry_snapshots, audit_events IN SHARE MODE`, and the transaction stays open until the outcome has been written down — `SHARE` conflicts with the `ROW EXCLUSIVE` an `INSERT` takes, so nothing can commit an acceptance or a refusal while the miss is being recorded, and the reading becomes a state spanning the recording rather than an instant preceding it. It runs as the schema owner rather than as step 2's read-only account, every failure — a `lock_timeout` expiry, a deadlock, a lost session, a `COMMIT` that does not succeed — is **Unsettled rather than a miss**, and the platform-wide cost is stated: inserts into `audit_events` wait for the transaction to end. Retiring the route before the decisive read was considered and rejected as the mechanism, because the counterexample is not Caddy; the retirement stays in step 4, ~~where S-D.3 and it divide the timeline with no gap~~ — **that claim is withdrawn as false by C-23**. The counterexample and its control are executed in the settlement tests with a run mutation. **The re-review of C-22 on 2026-08-11 held B-1 open for the ninth time**, on one Blocking finding and one Important, and B-1 was remediated a ninth time the same day (change-log **C-23**) — **nothing in C-18 to C-21 is withdrawn; one sentence of C-22's is.** The Blocking finding: the `SHARE` lock **delays** a conflicting writer rather than disposing of it. An `INSERT` that arrives while the lock is held does not fail — it waits inside PostgreSQL — so the procedure could record a miss and authorize a fresh export while the episode's own submission sat queued behind the lock, and on `COMMIT` that submission committed at once, before step 4 retired anything. Route retirement cannot reach it: a transaction waiting on a lock has already been accepted and is past every address the retirement acts on, which is why C-22's "no gap" claim was false and why C-22's control test demonstrated the defect while reading it as the successful case. **S-D gains S-D.4**: the queue behind the lock is read with the decisive reading and again as the last statement before the `COMMIT` — **any ungranted request by another backend on either table is Unsettled** — and the miss is confirmed by a **drain read** taken after the lock is released, a second acquisition of the same lock which PostgreSQL grants only behind whatever was queued, so a figure that has moved **retracts the miss**. Recording a miss and authorizing a fresh export become two steps with the drain read between them. The Important finding: `SET idle_in_transaction_session_timeout = 0` left the platform-wide pause unbounded, so an operator called away mid-recording could hold every audit insert on the platform indefinitely; it is now `'10min'`, exceeding the recording window, with expiry classified as Unsettled and `0` named in §9 as forbidden. **A third correction was found by running the procedure rather than reading it**: the queue reading is over `pg_locks` alone, because `pg_stat_activity` is answered from a backend-status snapshot taken at the transaction's first read of it — so the joined form returned nothing while `pg_locks` showed the waiter, and the join survives only as a follow-up after `pg_stat_clear_snapshot()`. **The reviewer's request for a real PostgreSQL concurrency test is taken as written**: `tests/test_snapshot_settlement_postgresql.py` establishes against the disposable `freedom_test` database that the lock blocks the real submission service, that the blocked backend is an ungranted `RowExclusiveLock` in §9's own query, that it commits the instant the lock is released, that the drain read is granted only behind it, that the joined queue reading misses it, and that a bounded idle timeout ends both the pause and the episode. **The declared PostgreSQL-backed test set was run for the first time in these remediations** — 2,112 passed with `TEST_DATABASE_URL` configured — against the disposable database only. **S-D.2, S-D.3 and S-D.4 have never been run against `freedom` or as an operator procedure**, and no service was stopped, started, reloaded or reconfigured. That correction carries no review of any kind, and the reviewer's standing recommendation is that neither B-1 nor the gate be closed. Codex accepted the rest of the package: RA-1's `SNAPSHOT_ONLY` classifications, field profile `2026-08-09.1` and its maintainer review, C-11's throughput criterion, the signed active-folder attestation, and the Phase 3 disposition of RA-3.  **The re-review of C-23 on 2026-08-11 held B-1 open for the tenth time**, on one Blocking finding, and B-1 was remediated a tenth time on 2026-08-12 (change-log **C-24**) — and this one **withdraws the previous nine rather than adding to them**. The Blocking finding: S-D.4 moved the race into the drain transaction rather than closing it. A request accepted and paused **before its first conflicting statement** is queued behind nothing, appears in no `pg_locks` reading, moves no watermark, and commits after the drain read has matched and the miss has already authorized a fresh export; route retirement cannot reach a transaction that is already inside PostgreSQL. The reviewer's direction was to stop inferring quiescence from point-in-time observations altogether, because **an observation of a resource cannot exclude work that has been accepted but has not yet reached it** — which is the single defect all nine share. C-24 therefore replaces settlement-by-observation with a durable **admission fence**: `submission_admissions` holds one generation per submitting credential, moving `open` → `closed` once and never back, with `principal_id` unique for all time so a closed generation can never be succeeded by an open one for the same credential. Every submission transaction resolves the admission of the principal id in **its own `Authorization` header** — never "whichever generation is open now", which would silently upgrade a paused request — and re-reads its state as the last statement before its commit; the acceptance's `idempotency_keys.admission_id` foreign key takes a `KEY SHARE` lock that conflicts with the `FOR UPDATE` a closure takes, so a closure and an acceptance can never interleave in either direction. **Settlement is now one command** (`tools.submission_admission close`) and **costs no downtime**: S-A, S-I (including the S-I.3a–d inventory), S-D.2's watermark, S-D.3's `LOCK TABLE` and S-D.4's queue and drain readings are all withdrawn, the endpoint and Caddy stay up, and §5.4's terminable-ingress requirement is demoted to good practice. Recovery issues a **new credential** under a new principal id and opens a generation naming it. **Migration 0005** is additive and reversible, exercised `upgrade → downgrade → upgrade`, and backfills pre-fence receipts to a closed generation 0. Evidence: `tests/test_submission_admission_postgresql.py`, 17 tests against a real PostgreSQL using the real submission service and `threading.Event` rendezvous rather than sleeps, including the paused-before-first-statement regression the reviewer named, the two other pause boundaries, both lock orderings, retries on both sides of a closure, and the measured trap that a plain `UPDATE` does **not** conflict with the foreign key's lock; plus least-privilege evidence in `tests/test_runtime_grants_live.py` (the runtime role holds `SELECT` and is refused every write with SQLSTATE 42501). Four mutations were run and reverted, each failing a named regression. Full suite **1917 passed, 232 skipped**; **2149 passed** with `TEST_DATABASE_URL`. **C-23's closure claims are struck in place.** The Phase 3 obligation to settle an episode without a stop is **discharged** by this correction. C-24 **carries no independent review**, names three maintainer decisions (the fail-closed deployment state, the new-credential requirement after every closure, and the removal of the downtime requirement), and **B-1 is not closed and the Phase 2 gate remains open**. **A finishing pass on 2026-08-12 corrected four bounded defects in C-24's implementation and operator surface, and withdrew nothing from the design** (change-log **C-24 finishing pass**): the documented settlement commands could not run, because the runbook's `DATABASE_URL='postgresql+psycopg:///freedom'` fails `DatabaseSettings` validation against `APP_ENVIRONMENT` — every invocation now names its environment, its real database and the schema-owner role rather than the restricted runtime role, and a test drives the commands parsed out of the runbook itself through the tool's own configuration path; the admission row's `correlation_id`/`closed_correlation_id` were SQL-generated while the audit event minted its own, so the columns identified no event — one identifier per transition is now written to both records in one transaction, proved by joins; `lock_timeout`, connection failure and privilege denial escaped as tracebacks — the CLI now has seven documented exit codes with `lock_timeout` classified as **Unsettled and safe to retry**, no message carrying a traceback, URL, credential or SQL, and no non-zero exit able to claim a closure; and the `READ COMMITTED` assumption behind the pre-commit re-read is now pinned on the unit of work instead of inherited from the database or login role. **The isolation question was measured before anything was changed**: at `REPEATABLE READ` and `SERIALIZABLE` the decisive interleaving is aborted by PostgreSQL at the foreign key's `KEY SHARE` lock with **SQLSTATE 40001**, and at `READ COMMITTED` it produces the typed `admission_closed` refusal — **no level produced a durable post-closure acceptance**, so this is recorded as hardening evidence rather than a new B-1 failure; what the non-default levels lost was the typed refusal, which the pin restores. Full suite **1952 passed, 247 skipped** and **2199 passed** with `TEST_DATABASE_URL`; migration 0005 re-rehearsed `upgrade → downgrade → upgrade`; four mutations run and reverted, each failing a named regression. The finishing pass **carries no independent review and closes nothing**. **The independent review of the C-24 submission-admission fence on 2026-08-12 returned one Blocking and one Important finding, both remediated the same day (change-log C-24-R); the durable admission design is retained in full and nothing in it is withdrawn.** Blocking (C-24-R1): the fence was structurally incomplete. The ordinary same-key replay took the shared advisory lock, resolved the authenticated principal's admission, required it open and required the stored receipt's `admission_id` to match — but the **uniqueness-conflict recovery path did none of that**. A request that lost the `idempotency_key.scope_key` race had its transaction rolled back, releasing the shared lock; settlement could then close the generation and commit; and the loser's recovery read the winner's row in a bare transaction and returned its successful receipt after the closure. No post-closure write is needed for that to break the invariant — returning a successful receipt is forbidden as squarely as writing a row, because the module treats it as a submission that succeeded while the operator has recorded the episode as settled. The remediation is **consolidation rather than a second check**: `_replay_stored` is deleted and both callers — the ordinary retry and the race recovery — reach one principal-bound operation, `SnapshotSubmissionService._fenced_replay`, which in one transaction takes the shared lock first, resolves the admission of the principal id the request authenticated as, requires it open, requires the stored record's `admission_id` to equal it, and only then applies the digest check. `_store_and_record` no longer replays at all; it raises a private signal. Evidence: the five-step interleaving is reproduced against a real PostgreSQL in `tests/test_submission_admission_postgresql.py` with `threading.Event` rendezvous and no sleeps, with a control showing the same race replays normally without a closure; five application-level tests cover both callers; and two AST tests assert mechanically that a `SubmissionReceipt` is constructed in exactly two production places, that the stored-receipt rebuild is called from exactly one, and that the one is the fenced boundary — so a future recovery branch that reads a receipt back for itself fails the suite. Important (C-24-R2): `tools/submission_admission.py` classified every `DBAPIError` without a SQLSTATE as an inability to connect and told the operator, for `close`, that no generation was closed and the fence was unchanged. **That is not sound** — a connection can be lost while PostgreSQL is processing or acknowledging `COMMIT`, and client observation cannot distinguish a lost acknowledgement from a lost connection. The phase is now **recorded rather than inferred**: `CommandProgress` is marked inside the transaction, and a SQLSTATE-less failure is exit 3 ("nothing was written") only when no transaction was established, and otherwise **exit 7, Outcome unknown / Unsettled**, which claims nothing in either direction, sends the operator to `show` and the correlation/audit join first, and explains that `close` is idempotent after verification while an ambiguous `open` must be verified before another generation is attempted. Failures during an ordinary statement are deliberately reported as unknown too: separating them would mean trusting the client's account of how far it got, which is exactly what a lost connection makes unreliable. Runbook §5.2.1 documents the outcome and the verification; §9's "if it is not 0, nothing was closed" is corrected. Evidence includes a test in which the closure **commits for real** and only the acknowledgement is lost — the tool exits 7, makes no "fence unchanged" claim, leaks no SQL, and the generation is in fact closed — followed by the documented verification path end to end. Two mutations were run and reverted: restoring the unfenced `_replay_stored` is killed by `test_a_request_that_loses_the_key_race_cannot_replay_across_a_closure` (which then returns a receipt instead of refusing) and three application/AST tests; restoring `sqlstate is None => nothing committed` is killed by nine CLI tests including `test_a_lost_commit_acknowledgement_never_claims_the_fence_is_unchanged`. Migration 0005 is **unchanged**. Full suite **1967 passed, 253 skipped** and **2220 passed, 0 skipped** with `TEST_DATABASE_URL`; `foundry-module` 155 pass; `alembic check` reports no new upgrade operations. **C-24-R carries no independent review, closes neither C-24 nor B-1, and does not close the Phase 2 gate.** **The outstanding closeout criterion is the independent re-review**, then the Acceptance Authority's decision. No gate decision is recorded. |
| Phase 2 I-03 — snapshot submission | Code findings closed through `1.0.5`; no independent gate recommendation exists | Deferred, with the Phase 2 gate | The 1.0.2 lifecycle findings were closed by 1.0.3/1.0.4, and 1.0.4 was recommended for acceptance as an implementation. The 2026-08-09 rehearsal trial in the scratch world `test` returned four findings; the CL3 re-review closed R-1…R-3 and raised one Blocking (CL3-B-1, a false-miss in the lost-pin procedure), two Important and three Optional. CL3-I-1, CL3-I-2, CL3-O-1 and CL3-O-2 are closed — see `docs/review/phase-2-i-03-cl3-remediation.md`, which also records that the CL3-I/CL3-O changes were made by the reviewer who raised them, at maintainer instruction, and carry no independent review. **CL3-B-1 was recorded as closed on 2026-08-09 and was not**: the independent review's finding B-1 established that the window correction left a second false miss, where the reconciliation query runs before a timed-out request's transaction commits. It is **not yet closed**: the settlement rule in `docs/review/phase-2-b-1-settlement-remediation.md` has been rewritten four times — C-13's S-A/S-B, C-14's S-B.1/S-B.2, C-15's stopped endpoint, and **C-18**, which withdraws the endpoint-only stop as well and settles an episode by terminating the whole ingress path, with step 4 retiring the route the episode used — and completed a fifth time by **C-19**, which withdraws none of C-18's rule but gives S-I.3 four executable checks and an explicit Unsettled rule, rebuilds the settlement test pair on one shared scenario so its negative control is executed rather than described, and gives every step 3 outcome a restoration branch so no episode leaves the host down indefinitely — and a sixth time by **C-20**, which withdraws nothing again but replaces S-I.3d's name-listing with a bounded inventory whose sources are read in full, adds **S-D.2** so a restart during the down window is detected by comparing both ends of it rather than argued impossible, and gives step 4's unresolved branch an entry read so it reloads a running Caddy instead of issuing a `start` that would silently leave the live submission route in force — and a seventh time by **C-21**, which withdraws one sentence of C-20's and adds S-D.2's **commit watermark**, the reading that catches an ingress which is not `caddy.service` because it reads what a submission must durably commit rather than what served it, with the transient-ingress counterexample executed in the settlement tests. It was completed an eighth time by **C-22**, which withdraws nothing and adds **S-D.3**: the decisive watermark and the repeated query are taken under a `SHARE` lock on the two append-only tables and the lock is held until the outcome is recorded, so a commit landing between the closing reading and the record — the interval C-21 closed by ordering alone — cannot happen. **It was superseded outright on 2026-08-12 by C-24, which withdraws the whole observation-based settlement — S-A, S-I, S-D.2, S-D.3 and S-D.4 alike — and replaces it with a durable admission fence checked inside each submission's own transaction; settlement is now `tools.submission_admission close` and costs no downtime.** It had been completed a ninth time by **C-23**, which withdraws one sentence of C-22's and adds **S-D.4**: the lock only *delays* a conflicting writer, so the queue behind it is read — any waiter is Unsettled — and the miss is confirmed by a drain read taken after the lock is released, before any fresh export is authorized; the platform-wide pause is bounded by a ten-minute `idle_in_transaction_session_timeout`; and the whole mechanism is established against a real PostgreSQL in `tests/test_snapshot_settlement_postgresql.py`, which also found that the queue reading may not be joined to `pg_stat_activity` inside the settlement transaction. CL3-O-3 was closed on 2026-08-09 by executing the §9 query against PostgreSQL during Rehearsal A. `1.0.5` was installed on `foundry1` and `foundry3` on 2026-08-09 and is the build Rehearsal A exercised; **the current build is `1.0.6`**, installed on both instances on 2026-08-10, **with neither instance yet restarted**. **C-12 changed no module bytes**, so 1.0.5 remains the rehearsed build of record. **The NFC key-collision defect is fixed and the module is now `1.0.6`** (change-log **C-16**, 2026-08-10): the encoder normalised keys after sorting and could silently drop an exported value, and the verifier did not normalise keys at all and emitted a duplicate key for the same input. Both halves now refuse a collision with the new artifact code `nfc_key_collision`, the verifier also normalises string values, and the `xfail`/`todo` holds are removed. `docs/review/phase-2-canonical-nfc-key-collision.md` is closed. **`1.0.6` was installed on `foundry1` and `foundry3` on 2026-08-10 20:49 UTC** ([record](../review/phase-2-module-1.0.6-install-2026-08-10.md)), replacing `1.0.5`, which is retained as a rollback copy. Rehearsals A and B remain evidence for `1.0.5`, the build they exercised. **Superseded 2026-08-10 — see the `1.0.7` correction later in this row.** ~~Neither instance has been restarted, so no supervised export may be taken yet: until the restart the running servers still hold the module list they booted with, and `exporter.version` could still be stamped `1.0.5`.~~ Both worlds were launched at 20:55 that day, after `1.0.6` was installed, which reloaded the package registry. For every ASCII-keyed document — which is every artifact either rehearsal produced — `1.0.6` emits the same bytes as `1.0.5`. C-16 carries no independent review. **The independent review of the C-16 package returned one Blocking finding, now closed as change-log C-17**: the verifier encoded numbers with `json.dumps`, whose float formatting differs from `JSON.stringify`'s at both notation thresholds, so a conforming export carrying `1e20` or `1e-7` was reported non-canonical — the third instance of C-12's shape, and the first reachable by ordinary dnd5e fractional values. The verifier now implements `Number::toString`, reads every literal as the double the exporter would have, and refuses a literal outside the double range (`non_finite_number`) as the exporter does; contract §1.3 states the rule and the one deliberate asymmetry (`-0` is refused by the exporter and encoded as `0` by the Manager). **The exporter's output is unchanged byte for byte; the module is `1.0.7` only because the new code joins the client's bounded `SERVER_ARTIFACT_CODES` list.** **`1.0.7` was installed on `foundry1` and `foundry3` on 2026-08-10 23:24:18 UTC** ([record](../review/phase-2-module-1.0.7-install-2026-08-10.md)), replacing `1.0.6`, which is retained as a rollback copy; exactly two files differ from `1.0.6` and `canonical.js` is not one of them. **Both worlds were then launched at 23:40, so the running package registry holds `1.0.7` and the standing "no export until restarted" blocker is cleared** — by world relaunch, which is what reloads the package list, rather than by a process restart. **That also corrects a claim this row previously carried**: `exporter.version` reads `game.modules.get(MODULE_ID)?.version` from the server's registry, and both instances launched worlds at 20:55 on 2026-08-10, six minutes after `1.0.6` was installed — so the stamp was `1.0.6` from that moment, never `1.0.5`, and the processes never being restarted did not preserve `1.0.5` as the row claimed. No export has been taken, so no artifact has been observed carrying `1.0.7`. C-17 carries no independent review. The trialled 1.0.4 is a different build and is superseded everywhere. Passing tests close no gate. |
| Phase 3 and later | Not ready | Readiness planning released | Phase 2, OD-16 and OD-17 are closed. Claude is assigned backend, Gemini frontend and Codex independent/security-focused review. Phase 3 still requires accepted §12.1 visual direction and stable accepted backend/view-model contracts. |
| Frontend visual prototype | Ready to start | Separate visual gate | Gemini is assigned under `docs/review/phase-3-visual-prototype-gemini-prompt.md`; the clean maintainer-supplied PNG is the required identity asset. Acceptance requires functional clarity, usability, accessibility and a visually polished result. |

## Current critical path

1. ~~**Draft the replacement Phase 2 remediation plan**~~ — done 2026-08-02:
   [`../review/phase-2-v1.5-remediation-plan.md`](../review/phase-2-v1.5-remediation-plan.md).
2. ~~**Readiness check of that plan**~~ — done 2026-08-02. Independent review of
   the plan was not separately commissioned; the mandatory independent review at
   the §16.4 import/reconciliation checkpoint applies to the **implementation**
   and remains required at step 5.
3. ~~**Acceptance Authority approval**~~ — recorded 2026-08-02, together with
   the OD-42/I-05 ruling and the three delivery rulings in change-log C-2.
4. ~~**Remediate the independently confirmed lifecycle findings.**~~ — done.
   The 2026-08-08 findings were closed by module `1.0.3` and `1.0.4`, and the
   2026-08-09 trial findings R-1…R-4 and CL3-I-1/I-2/O-1/O-2 are closed in
   `1.0.5`. Recorded in
   [`../review/phase-2-i-03-cl3-remediation.md`](../review/phase-2-i-03-cl3-remediation.md).
   **CL3-O-3 was closed on 2026-08-09** by executing the §9 query against
   PostgreSQL during Rehearsal A. The CL3-I/CL3-O changes were implemented by the
   reviewer who raised them, at maintainer instruction, and therefore carry no
   independent review. **CL3-B-1's 2026-08-09 closure was withdrawn** on the
   independent review's finding B-1 and **remains open**. The settlement rule in
   [`../review/phase-2-b-1-settlement-remediation.md`](../review/phase-2-b-1-settlement-remediation.md)
   has been rewritten four times: the first three attempts were each held open by
   re-review — the probe's accept-order inference, then Caddy's in-flight gauge,
   then an endpoint-only stop that left a request the proxy had not yet dialled
   upstream for — and the current rule settles an episode by **terminating the
   whole ingress path**, endpoint and proxy, with step 4 retiring the route the
   episode used (change-log **C-18**, with S-B and the endpoint-only stop both
   withdrawn). None of the four carries independent review, and closing B-1 is the
   reviewer's to do.
5. **Independent gate review of the complete I-03 package and the Phase 2
   evidence**, closing every blocking security, identity, atomicity, migration,
   recovery and evidence-accuracy finding. **Performed 2026-08-09 by Codex
   (`../review/Handover information`), which recommended the gate not be
   closed** on one Blocking finding (B-1) and one Important finding (I-1). Both
   were remediated on 2026-08-10 in
   [`../review/phase-2-b-1-settlement-remediation.md`](../review/phase-2-b-1-settlement-remediation.md).
   The re-review of that record **closed I-1 and held B-1 open**, on the
   settlement probe's ordering assumption; a second remediation (S-B.1,
   change-log C-14) was held open in turn, because Caddy documents
   `caddy_http_requests_in_flight` as the requests *currently being handled* and
   not as a drain. B-1 was remediated a **third** time on 2026-08-10 — the probe
   and the gauge withdrawn, settlement a stopped endpoint (change-log C-15) — and
   that was held open too: stopping the upstream leaves a request the proxy holds
   and has not yet dialled upstream for, which connects after the restart, and
   step 4 detected the duplicate rather than preventing it. The **fourth**
   remediation, on the maintainer's ruling between the two routes the reviewer
   offered, terminates the whole ingress path and retires the episode's route
   (change-log **C-18**). **B-1 is open**, and the reviewer also recommended the
   Phase 2 gate not be closed. Every one of those changes
   **carries no independent review**, so the step is **not complete**: an
   independent **re**-review of the corrected package is required. No accepting
   recommendation exists. The 2026-08-08 and 2026-08-09 review documents are
   findings and finding closures, not acceptance.
6. ~~**Operational evidence**: upgrade/downgrade/upgrade, backup/restore/rerun
   and direct `freedom_runtime_test` denial of `UPDATE`, `DELETE` and `TRUNCATE`
   against the final retained schema.~~ — **run 2026-08-05 against the
   disposable `freedom_test` and all three passed**; exact commands and results
   in
   [`../review/phase-2-i-03-fourth-remediation-submission.md`](../review/phase-2-i-03-fourth-remediation-submission.md)
   §7. One stated limitation: the operator-visible importer rerun is
   `tools.bootstrap_manager`; a Council-authorized repeat apply has no CLI and
   is covered by automated tests. These are recommendations-supporting evidence
   and close no gate on their own.
7. **Repeat the maintainer-supervised real-export rehearsal.** ~~Rehearsal A~~ —
   **completed 2026-08-09** on module 1.0.5 against a real 35-Actor non-live
   folder: submission, three-way checksum agreement, preview at 4.92 s with zero
   errors, Foundry unchanged, step 10 landing on the corrected `duplicate =
   false` hit, §8.1 both halves plus a credential rotation, and §8.2 positive
   **and negative** — the origin allowlist had never previously been shown to be
   load-bearing. Recorded in
   [`../review/phase-2-supervised-rehearsal-2026-08-09.md`](../review/phase-2-supervised-rehearsal-2026-08-09.md);
   findings in
   [`../review/phase-2-rehearsal-a-findings-2026-08-09.md`](../review/phase-2-rehearsal-a-findings-2026-08-09.md).
   A temporary public Caddy route was published for the session and **reverted
   2026-08-09 22:38 UTC**, on the second attempt: the first restored a backup
   that had itself been captured after the route was added.
7b. ~~**Rehearsal B — the active-folder gate rehearsal.**~~ — **completed
   2026-08-09.** 32 Actors, 0 errors, 0 warnings, every Actor accounted for,
   zero unexplained identity discrepancies, nothing applied. Records:
   [`../review/phase-2-supervised-rehearsal-b-2026-08-09.md`](../review/phase-2-supervised-rehearsal-b-2026-08-09.md)
   and the drafted attestation
   [`../review/phase-2-data-owner-attestation-2026-08-09.md`](../review/phase-2-data-owner-attestation-2026-08-09.md),
   **signed by the Data Owner on 2026-08-10**. Environment torn down:
   credential and artifact shredded, `freedom_test` empty at `0004`.
8. **Close the Phase 2 data-integrity, identity and migration-safety gate.**
   Nine of the ten closeout criteria in
   [`../operations/phase-2-maintainer-closeout.md`](../operations/phase-2-maintainer-closeout.md)
   §1 now check. All four owner recommendations were **given
   2026-08-10** ([record](../review/phase-2-owner-recommendations-2026-08-10.md)).
   Remaining: the **independent gate review**, handed over in
   [`../review/Handover information`](../review/Handover%20information) and
   framed in
   [`../review/phase-2-gate-independent-review-request.md`](../review/phase-2-gate-independent-review-request.md),
   which cannot come from Claude — the profile change, the canonical-order
   change, the threshold ruling and the CL3 fixes were all implemented by the
   party that raised them, at maintainer instruction; and the Acceptance
   Authority's decision. The temporary Caddy route was removed and
   verified on 2026-08-09.

Running in parallel, releasing nothing: **Phase 2 I-03** (snapshot submission)
was independently reviewed on 2026-08-04 — three Blocking findings (B-1 the
browser CORS preflight, S-B-1 the credential in client-readable Foundry
configuration, S-B-2 unenforced artifact-storage permissions) and three others
(I-1, I-2, S-I-1). ADR 0009 was accepted on 2026-08-04, which settles the
architectural decision only — it accepts no implementation and releases no gate.

**The first remediation did not close all six**, and the record here previously
said it had. A second independent re-review on 2026-08-04 reopened two:

| Finding | What the first remediation missed |
|---|---|
| I-1 | It corrected the messages the review had named and left the equivalent claims elsewhere: the unresolved-concurrency and replay refusals in `application/foundry/submission.py`, and every `ArtifactStorageError` in `application/artifacts.py`, still asserted that nothing was stored on paths that had already run the artifact store |
| S-B-2 | It made the storage checks real but left them **pathname-based**, so the validated root could be replaced between the check and each later create, open, publish or `fsync` |

**The second remediation did not close them either.** A third independent
re-review on 2026-08-04 found the S-B-2 root anchoring materially correct — the
pathname-redirection defect is fixed — and returned three further findings:

| Finding | What the second remediation missed |
|---|---|
| Blocking — publication | Anchoring fixed *which directory* the final entry was created in and left *how* alone. Publication was still `os.replace`, which is atomic about **replacing**: a checksum-named entry appearing between the presence check and the rename was removed and overwritten without being examined |
| Important — I-1 again | `StorageOutcome.UNRESOLVED`, the conservative **default**, still asserted that nothing already held had been changed or removed — a positive claim about durable state, on the sentence every unclassified path inherits, made false by the publication race |
| Important — test evidence | On the review host `/` and `/tmp` are owned by uid 65534, and the startup ancestor rule refused **32 tests** before they reached their own assertions. The submitted count of 1912 passing tests could not be independently reproduced |

All three are addressed in a third remediation, recorded in the same submission
and review request. Publication is now `link(2)`, which creates the checksum
entry or fails `EEXIST` and never removes an entry the service has not validated;
a concurrent winner is fully revalidated and reused; a third `StorageOutcome`
distinguishes a preserved unsafe entry from having found nothing; and the
ancestor rule is an injectable policy object so that tests about publication and
descriptor lifetime no longer depend on who owns the host's `/`. The suite was
additionally run under a harness reproducing the review host's ownership and
passes there.

**A fourth independent implementation and security re-review on 2026-08-05 found
the publication fix, I-1, I-2, root anchoring, S-B-1 and S-I-1 all resolved or
preserved, and returned one Important evidence-accuracy finding:**

| Finding | What the third remediation's *evidence* got wrong |
|---|---|
| I-3R-1 | The third-remediation request claimed "no temporary survives success or an ordinary failure" because `_discard` runs on every path. Running a cleanup function is not removal: `_discard` swallows `OSError` by design, and `test_a_failing_cleanup_leaves_the_published_artifact_alone` had already proved a **successful** store can leave one private `.incoming-*` hard link. The implementation, the operations document and the test were right; the structural-guarantee table was not |

The fourth remediation corrects the record at its source, states the best-effort
cleanup contract consistently across the adapter docstring, operations, the
configuration contract, the review record and the controlled records, and adds
the operator hygiene procedure the record had implied and did not have
(operations §5.6, "Temporary files left by a failed cleanup", proved against
synthetic files by three new tests). **No code change was required by the
finding and none was made to the publication mechanism**; the `os.link` design
and the test-only bounded ancestor walk were accepted by the re-review and were
not reopened. Recorded as change-log **C-7**, risk **R-18**, package-plan §10.

**I-3R-1 was independently re-reviewed and closed by Peter Duscha on
2026-08-05.** The review returned no new finding and confirmed the truthfulness
of the gate-readiness traceability. No further security re-review was required
because no security-relevant code or contract changed. This finding closure is
not an I-03 acceptance or a Phase 2 gate decision.

**Phase 2 is not gate-ready**, and the fourth-remediation submission says so in
those words rather than "complete except for". A gate-readiness audit against
every Phase 2 acceptance criterion, mandatory test and §13.3 evidence
requirement is in
[`../review/phase-2-i-03-fourth-remediation-submission.md`](../review/phase-2-i-03-fourth-remediation-submission.md)
§5. It changed three dispositions **against** the earlier position:

- the field profile `2026-08-03.1` must be "reviewed by a maintainer" and **no
  such review is recorded** — supervised, pending;
- rollback/recovery and retention are documented, and **D-c was accepted on
  2026-08-05**: unclaimed raw artifacts have a 30-day maximum with earlier
  deletion after the associated rehearsal, retry or incident closes;
- independent review closure is itself required operational evidence. I-3R-1
  is closed, while the complete Phase 2 closure record remains outstanding.

Three disposable-environment rehearsals were run on 2026-08-05 against
`freedom_test` with synthetic fixtures and no real credential, and all passed:
upgrade/downgrade/upgrade with an identical 205-line schema digest;
backup/restore over a populated database with identity and audit rows
byte-identical afterwards and an importer rerun creating nothing; and the
operations §5.8 server-half smoke test. Direct restricted-runtime-role denial is
automated against the real `freedom_runtime_test` role and passed with no skips,
which closes the A-02 evidence gap recorded on 2026-08-02. The disposable
database was returned to `0004 (head)` with every table empty and both dumps
were deleted.

Several findings are remediated **by construction and test rather than by
observation**, and two of those need Peter present: operations §8.1 (the
credential is not in the client state an ordinary player is vended) and §8.2 (the
browser origin actually passes and fails preflight under the configured origin
policy). The 2026-08-06 attempt recorded the masked, empty credential field,
zero secret-shaped GM settings, no secret received by the ordinary player, and
the positive allowed-origin preflight and POST. Credential revocation/cleanup
and the negative removed-origin observation remain pending; `curl` cannot
substitute for either live-browser observation. The storage work is bounded in
the same way: the
anchoring and the publication guarantee are proven against substitutions
performed by the test process and against type, owner and mode as this process
observes them, **not by a cross-account experiment and not by a multi-process
stress test**.
I-03 claims no Phase 2, Phase 3 or Phase 7 gate criterion. The controlling
review request is
[`../review/Handover information`](../review/Handover%20information) and its
outcome is
[`../review/phase-2-i-03-r1-r4-claude-review.md`](../review/phase-2-i-03-r1-r4-claude-review.md);
the remediation of its findings is recorded in
[`../review/phase-2-i-03-cl3-remediation.md`](../review/phase-2-i-03-cl3-remediation.md).
The rehearsal rerun follows the finding closures rather than preceding them, so
that a blocking finding cannot invalidate maintainer-supervised evidence — and
it must use the corrected Rehearsal A step 10, not the version the trial ran.

Phase 3 is baselined only after that gate, and then only once named owners,
accepted frontend contracts and security-review capacity are available. Steps 4
onward do not start before step 3 is recorded.

## Current decisions and blockers

- Peter Duscha holds the solo-maintainer accountable roles defined in the
  governance record. Package-specific implementing and reviewing agents are
  assigned when each package is prepared.
- No calendar forecast is committed; maintainer availability and package-level
  agent capacity are established during readiness planning.
- OD-16 and OD-17 block Phase 3 planning; OD-39 blocks the affected Phase 5
  economy cutovers. See `decision-register.md`.
- The normalization correction of 2026-08-02 implements the accepted identity
  policy and does not amend the baseline, so it carries no change-log entry.
- **OD-41 closed 2026-08-02:** ADR 0008 was rejected; the controlled baseline
  assigns every Sheet-era field in the migration register to one typed owning
  package and defines legacy comparison as deferred.
- **Restricted-role evidence is no longer blocked on role creation.** The
  temporary role `freedom_runtime_test` exists and can be assumed: it is
  `NOLOGIN`, non-superuser, cannot create roles or databases, cannot replicate
  and cannot bypass RLS, and the owner/test login `foundry` is a member able to
  `SET ROLE freedom_runtime_test`. ~~What remains is applying the runtime grants
  for the final retained schema and testing denial directly under that role.~~
  **Closed 2026-08-05:** `infra/postgresql/runtime-grants.sql.tmpl` was corrected
  for the retained schema and `tests/test_runtime_grants_live.py` applies it and
  tests `UPDATE`, `DELETE` and `TRUNCATE` denial **directly under the role**
  against real PostgreSQL, with no skips in the 2026-08-05 run. A-02 is updated
  accordingly.
- **The example exports are available; the rehearsal was attempted and failed.** Two
  maintainer-authorized exports exist outside the repository at
  `/opt/discord-bots/foundry-actor-exports`. None was read during package
  planning. On 2026-08-06 the supervised browser rehearsal reached real export
  and submission but failed its inactive-folder duplicate check. No formal
  reconciliation preview or Data Owner attestation was completed; both remain
  outstanding maintainer actions. A-03 must retain that failed-attempt history.
- **I-05 closed 2026-08-02 by OD-42:** display names are not unique identities,
  multiple characters may share one, stable character IDs and external Actor IDs
  provide identity, and any legacy name-based candidate lookup fails closed when
  more than one candidate exists. No unique display-name constraint is added;
  application enforcement is accepted deliberately.
- **Three delivery rulings recorded with the plan acceptance** (change-log C-2):
  `tools/import_sheet_characters.py` reverts to its committed state and is
  dormant with its disposition owned by package 5.1; Codex performs both the
  independent review and a distinct security-focused pass; and the §9.4 windows
  are required before R4 rather than before any work.
- **Outstanding maintainer inputs blocking R4:** the maintainer decision/gate
  availability window and supervised real-export rehearsal window. **Closed
  2026-08-05:** zero-hour immediate verification/cleanup observation policy and
  5-second preview / 5-second fresh-apply thresholds for a synthetic 500-Actor
  artifact on this host.
- **D-01 was split** into D-01a (the only register dependency Phase 2 has) and
  D-01b (per-package vocabulary readiness). Future vocabulary readiness no
  longer reads as a Phase 2 blocker.
- No additional people or standing team are required by the baseline.

## Next status update

Update after the independent gate review returns. Until then the package is
complete and unreviewed, which is the single most important fact on this page.

Previous instruction, now satisfied: the non-live-folder rerun, the corrected
Rehearsal A step 10, the browser observations, the active-folder preview and the
sanitized Data Owner attestation are all recorded, and the module was reinstalled
as `1.0.5` before any of them.

**Open deployment obligation, partly discharged:** the repository build is now
`1.0.6` (change-log C-16). It was **installed on `foundry1` and `foundry3` on
2026-08-10, 20:49 UTC**, replacing `1.0.5`, and the 1.0.5 trees are retained as a
rollback copy — [`../review/phase-2-module-1.0.6-install-2026-08-10.md`](../review/phase-2-module-1.0.6-install-2026-08-10.md).
**Neither instance has been restarted**, so the running servers still hold the
module list they read at boot and an export taken now could still stamp
`exporter.version` `1.0.5`. **No supervised export, rehearsal or submission may
be performed until `foundry1` and `foundry3` are restarted** — which disconnects
players and needs maintainer authorization — **and each module-management screen
shows 1.0.6.** This does not invalidate Rehearsal A or B: both are evidence about
the build they ran on, and `1.0.6` differs from `1.0.5` only for documents with
non-NFC object keys, which neither artifact was shown to contain.

**Nothing recorded on 2026-08-09 or 2026-08-10 closes the Phase 2 gate.** What
remains needs two people rather than more work: the Independent Reviewer, and the
Acceptance Authority. Phase 3 additionally needs an accepted §12.1 visual
direction, a named security reviewer distinct from the implementer, and OD-16 and
OD-17 closed — none of which this package touches.
