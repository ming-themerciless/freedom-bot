# Project status

Status date: 2026-08-10 (after Rehearsals A and B)

Baseline: v1.5; accepted by Peter Duscha on 2026-08-02

Overall health: Amber — the management baseline and technical foundations are
accepted, and the Phase 2 mapped-name normalization correction was independently
reviewed and accepted on 2026-08-02. The milestone itself remains incomplete.

## Milestone status

| Milestone | State | Gate | Evidence / next condition |
|---|---|---|---|
| Phase 0 — Discovery and architecture | Accepted | Closed 2026-07-30 | `docs/discovery/phase-0-handoff.md`, `docs/review/phase-0-submission.md` |
| Phase 1 — Database foundation | Accepted | Closed 2026-07-31 | Maintainer acceptance is recorded at the head of `docs/review/phase-1-submission.md` |
| Phase 2 — Import and reconciliation | **The independent gate review was performed 2026-08-09 and recommended the gate not be closed.** I-1 is closed; **B-1 is open after four remediations** and awaits independent **re**-review | Deferred | Disposable migration, backup/restore and runtime-role evidence passed 2026-08-05. Rehearsal A (non-live folder, 35 Actors) passed end to end on module 1.0.5 including step 10, §8.1 and both halves of §8.2. Rehearsal B (active folder, 32 Actors) previewed with **0 errors, 0 warnings**, all 32 Actors accounted for, zero unexplained identity discrepancies, nothing applied. Five rehearsal findings RA-1…RA-5; all closed or ruled (RA-1 profile `2026-08-09.1`; RA-2 change-log C-10, **corrected by C-12**; RA-5 change-log C-11; RA-3 referred to Phase 3; **RA-4's procedure note is now written into §6 step 10**). The Data Owner attestation was **signed 2026-08-10** and field profile `2026-08-09.1` **reviewed and accepted** the same day. **The independent review (`docs/review/Handover information`) then recommended against closing the gate**, on one Blocking finding (B-1, the lost-pin miss rule) and one Important finding (I-1, the canonical key boundary). Both are remediated in [`../review/phase-2-b-1-settlement-remediation.md`](../review/phase-2-b-1-settlement-remediation.md), 2026-08-10, and **carry no independent review**. The re-review of that record **accepted I-1 as closed and held B-1 open**: the settlement probe still inferred the endpoint's accept order from the client's issuance order, which the single-threaded server does not guarantee when the submission arrives through Caddy and the probe does not. A second remediation (S-B.1, change-log **C-14**) was **also held open**, because Caddy documents `caddy_http_requests_in_flight` as the requests *currently being handled* — not as evidence that the proxy is holding nothing — so the false miss remained reachable. B-1 was remediated a third time on 2026-08-10 — the probe and the gauge withdrawn, settlement the endpoint being stopped and staying stopped until the outcome is recorded, with a new step 4 to detect the residual after the restart (change-log **C-15**) — and the re-review **held it open again**: stopping the upstream does not settle a request the proxy holds and has not yet dialled upstream for, which makes its first dial after the restart, and "no upstream retry window" governs retries after a failed attempt rather than a first attempt that has not happened. Step 4 detected the resulting duplicate without preventing the false miss that authorized it. **B-1 was therefore remediated a fourth time on 2026-08-10 and is still open** (change-log **C-18**), on the maintainer's ruling between the two routes the reviewer offered: settlement now terminates the whole ingress path — the endpoint **and** Caddy, verified as absent processes rather than as drained ones — and step 4 brings the endpoint back behind a single-use route with the episode's own path retired, so a request held by a hop this host cannot terminate carries an address that no longer reaches the application. The cost is host-wide downtime for the duration of a reconciliation. That correction carries no review of any kind, and the reviewer's standing recommendation is that neither B-1 nor the gate be closed. Codex accepted the rest of the package: RA-1's `SNAPSHOT_ONLY` classifications, field profile `2026-08-09.1` and its maintainer review, C-11's throughput criterion, the signed active-folder attestation, and the Phase 3 disposition of RA-3. **The outstanding closeout criterion is the independent re-review**, then the Acceptance Authority's decision. No gate decision is recorded. |
| Phase 2 I-03 — snapshot submission | Code findings closed through `1.0.5`; no independent gate recommendation exists | Deferred, with the Phase 2 gate | The 1.0.2 lifecycle findings were closed by 1.0.3/1.0.4, and 1.0.4 was recommended for acceptance as an implementation. The 2026-08-09 rehearsal trial in the scratch world `test` returned four findings; the CL3 re-review closed R-1…R-3 and raised one Blocking (CL3-B-1, a false-miss in the lost-pin procedure), two Important and three Optional. CL3-I-1, CL3-I-2, CL3-O-1 and CL3-O-2 are closed — see `docs/review/phase-2-i-03-cl3-remediation.md`, which also records that the CL3-I/CL3-O changes were made by the reviewer who raised them, at maintainer instruction, and carry no independent review. **CL3-B-1 was recorded as closed on 2026-08-09 and was not**: the independent review's finding B-1 established that the window correction left a second false miss, where the reconciliation query runs before a timed-out request's transaction commits. It is **not yet closed**: the settlement rule in `docs/review/phase-2-b-1-settlement-remediation.md` has been rewritten four times — C-13's S-A/S-B, C-14's S-B.1/S-B.2, C-15's stopped endpoint, and now **C-18**, which withdraws the endpoint-only stop as well and settles an episode by terminating the whole ingress path, with step 4 retiring the route the episode used. CL3-O-3 was closed on 2026-08-09 by executing the §9 query against PostgreSQL during Rehearsal A. `1.0.5` was installed on `foundry1` and `foundry3` on 2026-08-09 and is the build Rehearsal A exercised; **the current build is `1.0.6`**, installed on both instances on 2026-08-10, **with neither instance yet restarted**. **C-12 changed no module bytes**, so 1.0.5 remains the rehearsed build of record. **The NFC key-collision defect is fixed and the module is now `1.0.6`** (change-log **C-16**, 2026-08-10): the encoder normalised keys after sorting and could silently drop an exported value, and the verifier did not normalise keys at all and emitted a duplicate key for the same input. Both halves now refuse a collision with the new artifact code `nfc_key_collision`, the verifier also normalises string values, and the `xfail`/`todo` holds are removed. `docs/review/phase-2-canonical-nfc-key-collision.md` is closed. **`1.0.6` was installed on `foundry1` and `foundry3` on 2026-08-10 20:49 UTC** ([record](../review/phase-2-module-1.0.6-install-2026-08-10.md)), replacing `1.0.5`, which is retained as a rollback copy. Rehearsals A and B remain evidence for `1.0.5`, the build they exercised. **Neither instance has been restarted, so no supervised export may be taken yet**: until the restart the running servers still hold the module list they booted with, and `exporter.version` could still be stamped `1.0.5`. For every ASCII-keyed document — which is every artifact either rehearsal produced — `1.0.6` emits the same bytes as `1.0.5`. C-16 carries no independent review. **The independent review of the C-16 package returned one Blocking finding, now closed as change-log C-17**: the verifier encoded numbers with `json.dumps`, whose float formatting differs from `JSON.stringify`'s at both notation thresholds, so a conforming export carrying `1e20` or `1e-7` was reported non-canonical — the third instance of C-12's shape, and the first reachable by ordinary dnd5e fractional values. The verifier now implements `Number::toString`, reads every literal as the double the exporter would have, and refuses a literal outside the double range (`non_finite_number`) as the exporter does; contract §1.3 states the rule and the one deliberate asymmetry (`-0` is refused by the exporter and encoded as `0` by the Manager). **The exporter's output is unchanged byte for byte; the module is `1.0.7` only because the new code joins the client's bounded `SERVER_ARTIFACT_CODES` list, and `1.0.7` is not installed anywhere.** Install `1.0.7` in place of the staged, never-loaded `1.0.6` before the restart. C-17 carries no independent review. The trialled 1.0.4 is a different build and is superseded everywhere. Passing tests close no gate. |
| Phase 3 and later | Not ready | Not opened | Phase 2 gate and applicable decisions/dependencies must close first |
| Frontend visual prototype | Status to be recorded by Product Owner | Separate visual gate | May proceed only within §12.1 constraints |

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
