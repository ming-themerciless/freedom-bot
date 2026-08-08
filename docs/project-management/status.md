# Project status

Status date: 2026-08-08

Baseline: v1.5; accepted by Peter Duscha on 2026-08-02

Overall health: Amber — the management baseline and technical foundations are
accepted, and the Phase 2 mapped-name normalization correction was independently
reviewed and accepted on 2026-08-02. The milestone itself remains incomplete.

## Milestone status

| Milestone | State | Gate | Evidence / next condition |
|---|---|---|---|
| Phase 0 — Discovery and architecture | Accepted | Closed 2026-07-30 | `docs/discovery/phase-0-handoff.md`, `docs/review/phase-0-submission.md` |
| Phase 1 — Database foundation | Accepted | Closed 2026-07-31 | Maintainer acceptance is recorded at the head of `docs/review/phase-1-submission.md` |
| Phase 2 — Import and reconciliation | In remediation; supervised rehearsal attempted 2026-08-06 and failed | Deferred | The accepted replacement plan remains controlling. Disposable migration, backup/restore, runtime-role and performance evidence passed. The real-export rehearsal exposed exporter defects; active-folder preview, Data Owner attestation, complete independent gate review, owner recommendations and the gate decision remain outstanding. |
| Phase 2 I-03 — snapshot submission | Lifecycle remediation `1.0.2` independently reviewed 2026-08-08; two Blocking lifecycle findings and three Important findings remain open | Deferred, with the Phase 2 gate | Codex reproduced the reviewed edge cases. A `409 original_result_unavailable` clears an already-spent key, and overlapping different-payload submissions or a page reload can lose the exact bytes/key for an indeterminate delivery. Server-code classification, response-field validation and folder-blind fallback download also require remediation. The module suite passes 126/126, but passing tests do not close these findings. See `docs/review/phase-2-i-03-lifecycle-codex-review.md` and the security-focused companion. No reinstall or rehearsal rerun occurs until fixes are independently re-reviewed. |
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
4. **Remediate the independently confirmed lifecycle findings.** The 2026-08-08
   Codex review confirmed that `original_result_unavailable` loses a spent key
   and upgraded cross-payload overlap/page-reload key loss to Blocking. It also
   confirmed Important classifier-ordering, response-validation and fallback
   download weaknesses. The implementation is checkpointed at `6db51e7`; the
   reviewed module snapshot remains `f632722` until a focused fix is committed.
5. **Independent re-review of the fixed implementation**, closing every
   blocking security, identity, atomicity, migration, recovery and
   evidence-accuracy finding. The 2026-08-08 review documents are findings, not
   acceptance.
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
7. **Repeat the maintainer-supervised real-export rehearsal** after independent
   acceptance of the lifecycle remediation. The 2026-08-06 attempt failed
   during the inactive-folder duplicate check after recording six pending
   snapshots; it was cleaned up without imports, characters or mappings. The
   negative-origin observation, final confidentiality cleanup, inactive-folder
   preview, active-folder gate preview and Data Owner attestation remain
   incomplete.
8. **Close the Phase 2 data-integrity, identity and migration-safety gate.**

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
I-03 claims no Phase 2, Phase 3 or Phase 7 gate criterion. The prior review request is
[`../review/Handover information`](../review/Handover%20information); the
superseded for current execution by the `1.0.2` lifecycle remediation. Its
independent review must finish **before** the rehearsal rerun, so that a blocking
finding cannot invalidate further maintainer-supervised evidence.

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

Update after remediation and independent re-review of the prepared-snapshot
lifecycle findings. Do not mark
the supervised rehearsal complete until the inactive-folder rerun, remaining
browser observations, active-folder preview and sanitized Data Owner attestation
are all recorded.
