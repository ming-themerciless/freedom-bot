# Project status

Status date: 2026-08-09 (updated after Rehearsal A)

Baseline: v1.5; accepted by Peter Duscha on 2026-08-02

Overall health: Amber — the management baseline and technical foundations are
accepted, and the Phase 2 mapped-name normalization correction was independently
reviewed and accepted on 2026-08-02. The milestone itself remains incomplete.

## Milestone status

| Milestone | State | Gate | Evidence / next condition |
|---|---|---|---|
| Phase 0 — Discovery and architecture | Accepted | Closed 2026-07-30 | `docs/discovery/phase-0-handoff.md`, `docs/review/phase-0-submission.md` |
| Phase 1 — Database foundation | Accepted | Closed 2026-07-31 | Maintainer acceptance is recorded at the head of `docs/review/phase-1-submission.md` |
| Phase 2 — Import and reconciliation | **Rehearsals A and B both completed 2026-08-09**; awaiting independent gate review | Deferred | Disposable migration, backup/restore and runtime-role evidence passed 2026-08-05. Rehearsal A (non-live folder, 35 Actors) passed end to end on module 1.0.5 including step 10, §8.1 and both halves of §8.2. Rehearsal B (active folder, 32 Actors) previewed with **0 errors, 0 warnings**, all 32 Actors accounted for, zero unexplained identity discrepancies, nothing applied. Five findings RA-1…RA-5; **all closed or ruled** (RA-1 profile `2026-08-09.1`; RA-2 change-log C-10; RA-5 change-log C-11; RA-3 referred to Phase 3; RA-4 a procedure note). The Data Owner attestation is drafted and **awaiting signature**. **Outstanding: the signature, the recorded maintainer review of profile `2026-08-09.1`, the independent gate review — which none of today's implementers can supply — and the Acceptance Authority decision.** |
| Phase 2 I-03 — snapshot submission | Code findings closed through `1.0.5`; no independent gate recommendation exists | Deferred, with the Phase 2 gate | The 1.0.2 lifecycle findings were closed by 1.0.3/1.0.4, and 1.0.4 was recommended for acceptance as an implementation. The 2026-08-09 rehearsal trial in the scratch world `test` returned four findings; the CL3 re-review closed R-1…R-3 and raised one Blocking (CL3-B-1, a false-miss in the lost-pin procedure), two Important and three Optional. CL3-B-1, CL3-I-1, CL3-I-2, CL3-O-1 and CL3-O-2 are now closed — see `docs/review/phase-2-i-03-cl3-remediation.md`, which also records that the CL3-I/CL3-O changes were made by the reviewer who raised them, at maintainer instruction, and carry no independent review. CL3-O-3 was closed on 2026-08-09 by executing the §9 query against PostgreSQL during Rehearsal A. The current build is **1.0.5**; it was installed on `foundry1` and `foundry3` on 2026-08-09 and is the build Rehearsal A exercised. The trialled 1.0.4 is a different build and is superseded everywhere. Passing tests close no gate. |
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
   2026-08-09 trial findings R-1…R-4 and CL3-B-1/I-1/I-2/O-1/O-2 are closed in
   `1.0.5`. Recorded in
   [`../review/phase-2-i-03-cl3-remediation.md`](../review/phase-2-i-03-cl3-remediation.md).
   **CL3-O-3 remains open**, and the CL3-I/CL3-O changes were implemented by the
   reviewer who raised them at maintainer instruction and therefore carry no
   independent review.
5. **Independent gate review of the complete I-03 package and the Phase 2
   evidence**, closing every blocking security, identity, atomicity, migration,
   recovery and evidence-accuracy finding. No such recommendation exists. The
   2026-08-08 and 2026-08-09 review documents are findings and finding
   closures, not acceptance.
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
   A temporary public Caddy route was used and reverted. **Still outstanding:**
   the active-folder Rehearsal B and the Data Owner attestation, plus RA-1 —
   the field profile does not classify ten paths that real Actors carry, which
   is a Phase 2 acceptance criterion in its own right.
7b. ~~**Rehearsal B — the active-folder gate rehearsal.**~~ — **completed
   2026-08-09.** 32 Actors, 0 errors, 0 warnings, every Actor accounted for,
   zero unexplained identity discrepancies, nothing applied. Records:
   [`../review/phase-2-supervised-rehearsal-b-2026-08-09.md`](../review/phase-2-supervised-rehearsal-b-2026-08-09.md)
   and the drafted attestation
   [`../review/phase-2-data-owner-attestation-2026-08-09.md`](../review/phase-2-data-owner-attestation-2026-08-09.md),
   **which the Data Owner has not yet signed**. Environment torn down:
   credential and artifact shredded, `freedom_test` empty at `0004`. The
   temporary Caddy route still needs reverting.
8. **Close the Phase 2 data-integrity, identity and migration-safety gate.**
   Remaining, in order: the attestation signature; the recorded maintainer
   review of field profile `2026-08-09.1`; the **independent gate review**,
   which cannot come from Claude — today's profile change, canonical-order
   change, threshold ruling and CL3 fixes were all implemented by the reviewer
   who raised them, at maintainer instruction; and the Acceptance Authority's
   decision.

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

Update after the supervised rehearsal rerun. Do not mark it complete until the
inactive-folder rerun, the corrected Rehearsal A step 10, the remaining browser
observations, the active-folder preview and the sanitized Data Owner attestation
are all recorded. The module must be reinstalled as `1.0.5`; the trialled 1.0.4
is a different build.

**Nothing in the 2026-08-09 finding closures moves the Phase 2 gate.** What the
gate still needs is operational evidence and two decisions, none of which an
implementing or reviewing agent can supply: the rehearsal itself, the Data Owner
attestation, the recorded maintainer review of field profile `2026-08-03.1`, the
independent gate recommendation, and the Acceptance Authority's decision. Phase 3
additionally needs an accepted §12.1 visual direction, a named security reviewer
distinct from the implementer, and OD-16 and OD-17 closed.
