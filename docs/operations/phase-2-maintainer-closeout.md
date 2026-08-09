# Phase 2 maintainer closeout — step-by-step runbook

Status: maintainer working document

Owner: Peter Duscha

Purpose: finish the evidence and decisions required to close the Phase 2 data
integrity, identity and migration-safety gate.

This document is written for a maintainer who is not expected to know Git,
PostgreSQL, Foundry module development or the project's governance structure.
Follow it from top to bottom. Do not skip a red stop condition.

## 1. What “finished” means

Phase 2 is finished only after all boxes in this list are checked:

- [x] four operating thresholds are decided and recorded — observation policy and retention (D-c) 2026-08-05; performance restated per megabyte by change-log **C-11** on 2026-08-09 after finding RA-5 showed the C-9 wall-clock figures were calibrated on unrepresentative data;
- [x] field profile **`2026-08-09.1`** is reviewed and accepted — `docs/review/phase-2-field-profile-maintainer-review-2026-08-10.md`. (`2026-08-03.1` was superseded by finding RA-1; it was never reviewed and no longer needs to be.);
- [x] the inactive-folder Foundry rehearsal passes — Rehearsal A, `docs/review/phase-2-supervised-rehearsal-2026-08-09.md`;
- [x] the credential-confidentiality observation passes — §8.1 both halves, Rehearsal A section C;
- [x] the real-browser origin observation passes positively and negatively — §8.2 both halves, Rehearsal A section D. The negative case had never been run before 2026-08-09;
- [x] the active-folder preview accounts for every Actor with zero unexplained
      identity discrepancy — Rehearsal B, 32 of 32, 0 errors and 0 warnings;
- [x] a sanitized Data Owner attestation is written **and signed** 2026-08-10 — `docs/review/phase-2-data-owner-attestation-2026-08-09.md`;
- [ ] an independent reviewer reviews the complete Phase 2 gate package;
- [ ] Peter records the Data, Security, Operations and Product Owner
      recommendations;
- [ ] Peter records the final Phase 2 gate decision.

The cross-account POSIX experiment and multi-process publication stress test are
not gate requirements. A production `freedom-web` process is Phase 3 work and
does not block Phase 2.

## 2. Safety rules

Stop immediately and tell Codex what happened if any of these occurs:

- a real Actor export, raw reconciliation report, database dump, secret, token,
  or player name appears in `git status`;
- the rehearsal targets any database other than the disposable
  `freedom_test` database;
- the Foundry module changes an Actor, Item, Folder or compendium;
- an Actor cannot be classified as mapped, create-candidate or explicitly
  unresolved;
- an identity difference cannot be explained;
- a browser receives the synthetic credential belonging to another user;
- browser submission succeeds after its origin is removed from the allowlist;
- a command or screen differs materially from this runbook.

Never paste a credential, raw Actor export or player data into ChatGPT/Codex,
Git, a Markdown record, a shell-history example or a screenshot committed to
the repository. Codex may prepare commands containing placeholders, but Peter
enters the real or synthetic secret locally.

## 3. How responsibilities are split

Peter performs only the decisions and the observations that require a real
person, Foundry client or browser. Codex or another implementation agent
prepares the disposable database, starts and stops the rehearsal endpoint,
generates synthetic load, measures performance, performs scheduled technical
checks, inspects sanitized output, drafts records, runs tests and updates
documentation. Peter is not expected to watch a process continuously or perform
a synthetic benchmark by hand.

Whenever this runbook says “send Codex”, copy the quoted request into the chat.
Codex must pause before accessing Foundry, installing the module, using an
export, creating a credential or changing a gate record unless that request
explicitly authorizes the action.

## 4. Step 1 — settle scheduling, performance and retention

The implementation plan uses the confusing word “window”. It does **not** ask
for Peter's usual working hours or a permanent support schedule. This is a
hobby project and no such schedule exists.

### 4.1 Scheduling

Record these facts:

1. General maintainer availability: **sporadic**, normally around 20:00–02:00
   and on weekends; daytime work is usually 10:00–19:00 but is not reserved for
   this project.
2. Specific supervised-rehearsal appointment: choose this only when ready to
   run Steps 4–7. Until then record `not scheduled` rather than inventing a
   regular window.

The appointment exists so an agent knows when Peter will be present for the
Foundry/browser actions. It can be one evening or weekend session.

### 4.2 Post-rehearsal observation

This is not continuous human watching. After the active-folder rehearsal, the
technical operator or agent checks at agreed points that:

- the rehearsal endpoint has no new error or refusal category;
- `freedom_test` still has the expected snapshot, preview, identity and audit
  counts;
- no duplicate record or unexplained mutation appeared;
- the artifact checksum and restricted permissions remain correct;
- the artifact root has no unexpected `.incoming-*` leftover;
- no secret, raw artifact or player data entered Git or logs.

**Decision, Peter Duscha, 2026-08-05:** use a **zero-hour observation period
with immediate post-run verification, shutdown and cleanup**. A 24-hour watch
would provide no useful evidence after the disposable endpoint is stopped and
its rehearsal state is removed. The technical operator or agent performs every
check listed above before cleanup and records the result; Peter does not need to
watch the process continuously.

### 4.3 Synthetic 500-Actor performance benchmark

Peter does **not** preview or apply 500 Actors and does not operate this test.
Gemini generates a completely synthetic artifact, runs it against
`freedom_test`, measures preview and apply, and proposes limits. Peter's only
job is to accept the proposed limits or ask for different ones. The benchmark
must not use Foundry, a real export or player data.

Give Gemini this task:

> Benchmark preview and apply with a synthetic 500-Actor artifact in
> `freedom_test`. Do not access Foundry or real Actor data. Report the timings
> and recommend conservative Phase 2 thresholds. Do not record a decision yet.

The complete ready-to-copy Gemini handoff, including database guards,
measurement protocol, cleanup and report format, is
`docs/review/phase-2-r4-gemini-performance-benchmark-prompt.md`. Use that full
prompt instead of the short summary above when assigning the work.

After receiving the measurements, Peter responds with either `I accept the
recommended thresholds` or names a different limit. This is an Operations Owner
decision, not manual technical work.

**Decision, Peter Duscha, 2026-08-05:** accept the Phase 2 R4 rehearsal
thresholds of **5 seconds for preview** and **5 seconds for fresh apply**, based
on the synthetic 500-Actor performance benchmark report
([`docs/review/phase-2-r4-500-actor-benchmark.md`](../review/phase-2-r4-500-actor-benchmark.md))
and Codex's independent reproduction of those maxima and recommendations.

### 4.4 Artifact retention

**Decision, Peter Duscha, 2026-08-05:** use a **30-day maximum** for a
database-unclaimed raw snapshot if it is needed to investigate or retry a
failed submission. The complete accepted rule is:

> Retain a database-unclaimed raw snapshot for at most 30 days, and delete it
> sooner when the corresponding rehearsal, retry or incident is closed. Keep
> only its checksum, provenance and sanitized audit record permanently.

This applies to sensitive raw Foundry snapshot files, not database exports.

### 4.5 Leftover `.incoming-*` checks

An `.incoming-*` file is **not an export from the database**. It is a temporary
filesystem name created while receiving a Foundry snapshot. Normally it is
removed within the same request. If removal fails, it can consume storage even
though the valid checksum-named snapshot is unaffected.

There are two different “check now” meanings:

- **storage-hygiene check:** look for failed-cleanup `.incoming-*` files on the
  platform host. This says nothing about whether current Foundry Actor data is
  fresh;
- **current-data submission:** export the currently selected Foundry Actor
  folder and submit a new immutable snapshot. The module's existing **Submit**
  action already does this; it does not export data from PostgreSQL.

**Clarification, Peter Duscha, 2026-08-05:** “Check now” means a current-data
submission. The module's existing **Submit** action satisfies that request. No
new button, endpoint or Phase 2 capability is required.

The current Phase 2 implementation deliberately provides only a manual,
read-only command and gives the application no directory-listing capability.
Because the Phase 2 endpoint is disposable and the selected observation policy
ends with immediate shutdown and cleanup, the technical operator runs the
documented read-only storage-hygiene check immediately before cleanup. There is
no continuously running Phase 2 service that needs a daily timer. Production
monitoring cadence belongs to the Phase 3 deployment package and must be decided
before that service is released.

No automatic deletion is authorized. The check reports age, size and link
count; a human deliberately handles a result using
`foundry-snapshot-submission.md` §5.6. A web button would require Phase 3
authentication and object-level authorization and must not be improvised in
the Phase 2 rehearsal server.

This preserves package decision D11: storage-hygiene detection remains an
operator procedure and no application listing or deletion surface is added.

### 4.6 Record the settled decisions

After the benchmark and the choice of observation/checker design, send Codex:

> Record the Phase 2 R4 schedule, zero-hour immediate-verification-and-cleanup
> observation policy, accepted Gemini synthetic 500-Actor performance
> thresholds, 30-day maximum retention decision D-c, the existing module Submit
> action as the current-data check, and the immediate pre-cleanup storage-hygiene
> check in the proper controlled records.
> Treat D-a, short-lived token
> exchange, and D-b, automatic storage-permission repair, as deferred to later
> work and not required for Phase 2. Show me the exact diff before claiming the
> decisions are recorded.

Codex should update at least:

- `docs/review/phase-2-v1.5-remediation-plan.md` §9.4;
- `docs/review/phase-2-i-03-package-plan.md` for D-c;
- `docs/project-management/decision-register.md` or the authoritative linked
  decision record, as appropriate;
- `docs/project-management/raid-register.md` for R-18's cadence; and
- `docs/project-management/status.md`.

Pass condition: the rehearsal is either specifically scheduled or explicitly
not yet scheduled; the zero-hour observation policy is recorded; Gemini's
synthetic performance limits are measured and accepted; retention is numeric;
the existing Submit action and immediate storage-hygiene check are recorded;
and the diff says who decided each item and on what date.

## 5. Step 2 — review the field profile

Open these files:

1. `docs/rules/field-ownership.md`
2. `domain/field_profile.py`
3. `docs/project-management/data-migration-register.md`

The question is not whether every technical detail looks pretty. Confirm these
plain-language facts:

- every supported Foundry field has exactly one classification;
- identity fields belong to Phase 2;
- snapshot-only fields can be read but not independently edited in PostgreSQL;
- Sheet-era game fields say `legacy_authority_deferred` and name one future
  migration package;
- Phase 2 does not pretend a Sheet-era value matches or differs from Foundry
  when no typed PostgreSQL value exists;
- no field is silently ignored or owned by two packages.

If any row looks wrong or incomprehensible, do not approve it. Send Codex the
field name and your question. No code or profile correction should be inferred
from an ambiguous answer.

If you accept it, send Codex exactly:

> As Data Owner, I reviewed field profile `2026-08-03.1` against
> `docs/rules/field-ownership.md` and the data migration register. I accept its
> classifications and package ownership on [YYYY-MM-DD]. Record this maintainer
> review without claiming the Phase 2 gate.

Codex should add a dated review record under `docs/review/` and update
`docs/project-management/status.md`.

Pass condition: a repository review record names Peter, the exact profile
version and the review date. Committing it is a separate maintainer action.

## 6. Step 3 — schedule one supervised rehearsal session

Reserve enough uninterrupted time to run Steps 4 through 7 together. Have
available:

- administrator/GM access to the rehearsal Foundry world;
- a separate ordinary-player account;
- two browser profiles, such as normal Firefox and a private/second-profile
  window;
- access to the host running this repository;
- the authorized Foundry exports outside the repository;
- permission to install the local module in the rehearsal world;
- confirmation that PostgreSQL database `freedom_test` is disposable.

Send Codex:

> Prepare the Phase 2 supervised rehearsal for [date/time]. Use only
> `freedom_test`, synthetic credentials and the local I-03 module. Give me the
> exact module-installation path and environment-specific startup commands, but
> do not install, start, access Foundry or read a real export until I explicitly
> authorize each step. Create a timestamped sanitized rehearsal-notes template.

Codex should create a notes file such as:

`docs/review/phase-2-supervised-rehearsal-YYYY-MM-DD.md`

The file initially contains only checkboxes, expected results and blank places
for safe counts, stable IDs and checksums. It must contain no secret or Actor
payload.

## 7. Step 4 — run the inactive-folder transport rehearsal

This step proves that Foundry can submit an export without changing Foundry.
It does not satisfy the active-folder gate evidence.

### 7.1 Before clicking anything

Ask Codex to:

1. verify `freedom_test` is the configured database;
2. run the documented server-half smoke test with synthetic data;
3. show that the disposable database and artifact directory are clean;
4. prepare a synthetic one-use credential without printing or recording it;
5. start the loopback/non-production snapshot endpoint;
6. tell you the exact endpoint URL and permitted browser origin.

Do not proceed unless the smoke test returns:

- first submission: HTTP `201`;
- duplicate submission: HTTP `200` and `duplicate: true`;
- one `0600` artifact named for its SHA-256;
- no `.incoming-*` leftover;
- zero characters and zero imports created merely by submission.

### 7.2 In Foundry

1. Install and enable the local `Freedom Blades — Snapshot Submission` module
   only after Codex gives the exact environment-specific installation path.
2. Log in as GM.
3. Open the Actor Directory.
4. Confirm the export button is visible.
5. Open the dialog.
6. Confirm it shows the actual Foundry, D&D system and world versions.
7. Confirm each folder shows full path, stable folder ID and direct Actor count.
8. Select `Characters (inactive)` or another explicitly non-live folder.
9. Record only the folder ID and Actor count in the rehearsal notes. Do not
   record Actor names or mechanics.
10. Click **Download JSON** without entering a credential.
11. Locally calculate its SHA-256 using the command Codex supplies. Record only
    the checksum.
12. Confirm **Submit** with an empty credential refuses with
    `missing_credential` and sends nothing.
13. Enter the synthetic credential and submit.
14. Confirm the receipt contains Actor count and checksum but no Actor name,
    mechanic or raw JSON.
15. Submit the same unchanged export again and confirm it reports that the same
    snapshot is already held.

### 7.3 Verification with Codex

Tell Codex only the checksum, folder ID and count, then ask it to verify:

- the receipt, database and downloaded file checksums agree;
- preview works in `freedom_test`;
- optional apply, if performed, affects only `freedom_test`;
- Foundry Actor, Item, Folder and `Actors (shared)` compendium counts did not
  change;
- `git status` contains no JSON export, dump, log or Actor data.

Pass condition: every item agrees and Foundry remains unchanged. Record PASS or
FAIL and a safe reason in the rehearsal notes.

## 8. Step 5 — credential-confidentiality observation

Keep the rehearsal endpoint and synthetic credential from Step 4.

1. As GM, reopen the export dialog. Confirm the credential field is masked,
   empty and not pre-filled.
2. Submit once using the synthetic credential.
3. In the GM browser console, run:

   ```js
   (function () {
     var count = 0;
     var settings = game.settings.storage.get("world").contents;
     for (var i = 0; i < settings.length; i++) {
       var key = String(settings[i].key);
       if (
         key.startsWith("freedom-blades-export.") &&
         /credential|secret|token/i.test(key)
       ) count++;
     }
     return count;
   })()
   ```

4. The result must be `0`.
5. In a genuinely separate browser profile, join the same world as an ordinary
   player.
6. In that player's console run:

   ```js
   JSON.stringify(
     [...game.settings.storage.get("world")].map(s => s.value)
   ).includes("PASTE THE SYNTHETIC SECRET LOCALLY");
   ```

7. The result must be `false`.
8. Do not copy the secret or complete console output into the notes. Record only
   `GM secret-shaped settings: 0` and `player received secret: false`.
9. Ask Codex to rotate/revoke the synthetic credential after Step 6 below.

Pass condition: no secret-shaped world setting and the ordinary player's test
returns `false`.

## 9. Step 6 — real-browser origin observation

1. Ask Codex to put the rehearsal Foundry instance's exact origin in
   `FREEDOM_SNAPSHOT_ALLOWED_ORIGINS` and restart the rehearsal endpoint.
2. Submit from the Foundry browser.
3. Open browser developer tools, then the **Network** tab.
4. Confirm an `OPTIONS` request occurs before `POST`.
5. Select `OPTIONS` and confirm:
   - status is `204`;
   - `Access-Control-Allow-Origin` exactly equals the Foundry origin.
6. Confirm the following `POST` succeeds and the module shows a receipt.
7. Ask Codex to remove the origin from the allowlist and restart the endpoint.
8. Submit again.
9. Confirm the module reports a network failure and no successful POST occurs.
10. Ask Codex to confirm the server recorded a refused preflight without a
    secret or payload.
11. Ask Codex to restore the allowlist.

Record only the origin, positive `204`/receipt result, and negative refusal
result. Do not record headers containing authorization.

Pass condition: allowed origin works; removed origin fails. Both halves are
required.

## 10. Step 7 — formal active-folder preview

This is the Phase 2 gate rehearsal. It is preview-only. It must not change
Foundry and must not apply character game state.

1. Confirm with Codex that the target remains `freedom_test`.
2. In Foundry select `Characters (active)`.
3. Record the world ID, folder ID, Actor count, exporter version and field
   profile version. Do not record Actor names.
4. Submit the snapshot.
5. Record its SHA-256 checksum only.
6. Ask Codex to run reconciliation preview only.
7. For every stable external Actor ID, assign exactly one disposition:
   - `mapped` — already tied to the correct database character;
   - `create-candidate` — no mapping exists and creating identity later is
     appropriate;
   - `unresolved` — identity cannot yet be decided, with a safe explanation.
8. Investigate every warning or discrepancy. Names may be viewed during the
   supervised session but must not be copied into Git.
9. Stop if any Actor has no disposition or any identity discrepancy remains
   unexplained.
10. Confirm the preview created no character or mapping changes.
11. Confirm no raw export, raw report, Actor name or mechanic entered Git.

Pass condition: the three disposition counts total exactly the selected-folder
Actor count and there are zero unexplained identity discrepancies.

## 11. Step 8 — write the signed Data Owner attestation

After Step 7 passes, send Codex:

> Draft the sanitized Phase 2 Data Owner attestation from these safe facts only:
> [date, checksum, exporter version, profile version, world ID, folder ID,
> total count, mapped stable IDs/count, create-candidate stable IDs/count,
> unresolved stable IDs/count and safe reasons]. Do not include Actor names,
> mechanics, raw snapshot content or unnecessary player data. Show me the draft
> before recording my acceptance.

Create:

`docs/review/phase-2-data-owner-attestation-YYYY-MM-DD.md`

It must contain this structure:

```markdown
# Phase 2 Data Owner reconciliation attestation

Date: YYYY-MM-DD
Data Owner: Peter Duscha
Snapshot SHA-256: <checksum>
Exporter version: <version>
Field-profile version: 2026-08-03.1
World ID: <stable world ID>
Selected folder ID: <stable folder ID>

| Disposition | Count | Stable external Actor IDs |
|---|---:|---|
| Mapped | 0 | ... |
| Create-candidate | 0 | ... |
| Explicitly unresolved | 0 | ... |
| Total | 0 | — |

Unresolved dispositions and safe reasons: <none, or one safe reason per ID>

I confirm that every Actor in the selected folder is accounted for, there are
zero unexplained identity discrepancies, the exercise was preview-only, and no
raw artifact or real Actor payload was committed to this repository.

Signed: Peter Duscha, Data Owner, YYYY-MM-DD
```

Check the arithmetic yourself: mapped + create-candidate + unresolved must
equal total Actors.

## 12. Step 9 — request the final independent gate review

After Steps 1 through 8 pass, send Codex:

> Perform the final independent Phase 2 implementation and security gate review
> across packages R1-R4. Review every Phase 2 acceptance criterion, mandatory
> test, supervised record, migration/recovery item and all previously Blocking
> findings. Do not implement fixes and do not approve the gate. Produce one
> implementation recommendation and one distinct security-focused
> recommendation. State every remaining finding and whether Phase 2 is
> gate-ready.

The reviewer must not be the agent that implemented the work being reviewed.
Any new Blocking finding returns to remediation and re-review before continuing.

Pass condition: the independent review recommends gate approval and no Blocking
finding remains open.

## 13. Step 10 — record Peter's owner recommendations

If all earlier steps pass, send Codex the following completed statement. Change
any line you do not actually accept to `I do not accept` and explain why.

> Date: [YYYY-MM-DD]. As Data Owner, I accept field profile `2026-08-03.1` and
> the signed active-folder reconciliation attestation. As Security Owner, I
> accept the credential, browser-origin, authorization and restricted-storage
> evidence. As Operations Owner, I accept the deployment prerequisites,
> recovery procedures, retention period of [N days], and temporary-file hygiene
> cadence of [N days]. As Product Owner, I accept or explicitly dispose of
> change-log entries C-3 through C-7. Record these as separate role
> recommendations. Do not close the Phase 2 gate yet; first show me the proposed
> gate record and list any remaining unmet criterion.

Codex should update the change log, status, RAID/decision records and the gate
package without rewriting historical submissions.

## 14. Step 11 — make the final gate decision

Codex must first show Peter a final table containing every Phase 2 acceptance
criterion with one of: passed, not applicable, or failed. There must be no
pending or failed gate requirement for an unconditional approval.

If everything passes, Peter sends:

> As Acceptance Authority, I approve the Phase 2 data-integrity, identity and
> migration-safety gate on [YYYY-MM-DD]. I accept the documented residual risks
> and owner recommendations. Record the gate as approved, close dependency
> D-02, mark Phase 2 accepted, and mark Phase 3 ready for its own planning only.
> Do not start or implement Phase 3 in this action.

Codex then updates:

- `docs/project-management/status.md`;
- `docs/project-management/change-log.md`;
- `docs/project-management/raid-register.md`, including D-02;
- the final Phase 2 gate record under `docs/review/`; and
- any review request that is explicitly a live status document.

The record must say `approved`, name Peter Duscha, give the date, link the
attestation and independent reviews, and state that Phase 3 is released for
planning rather than silently started.

If anything remains missing, the decision is `deferred`, not “almost approved”.
Record the missing item, its owner and the next action.

## 15. Cleanup after either pass or failure

Ask Codex to supervise these checks:

- stop the rehearsal endpoint;
- revoke/rotate the synthetic credential;
- return `freedom_test` to migration head with no rehearsal rows;
- delete disposable raw artifacts and downloads according to the rehearsal
  decision;
- confirm no export, dump, secret, log or Actor payload is under Git;
- retain only sanitized Markdown evidence;
- run `git diff --check` and show `git status --short`.

Do not delete a file merely because it is named `.incoming-*`. Follow
`foundry-snapshot-submission.md` §5.6 and inspect its age and link count first.

## 16. Current starting point

As of 2026-08-09:

- automated tests and disposable PostgreSQL rehearsals pass;
- I-3R-1 is closed;
- the module was installed for the 2026-08-06 supervised rehearsal attempt;
  version 1.0.1 reached submission after correcting the initial
  `undefined_value` refusal, then failed the duplicate-unchanged-submission
  check by producing new timestamps, checksums and pending snapshots;
- version 1.0.2 introduced a bounded prepared-snapshot lifecycle whose retry
  and malformed-response paths an independent review reopened; 1.0.3 and 1.0.4
  closed those findings, and 1.0.4 was recommended for acceptance as an
  implementation;
- **module version identity.** A 1.0.4 build was installed on the `foundry3`
  instance for the 2026-08-09 rehearsal trial in the scratch world `test`. The
  current repository build is **not** that build — it adds `notifications.js`,
  changes the operator-visible failure text and surfaces `artifact_code` — and
  is versioned **1.0.5** for that reason. `exporter.version` reaches
  `foundry_snapshots.exporter_version` and checksum-bearing audit history, so
  the two builds must not share a string. Nothing has been installed anywhere
  as 1.0.5. The trial database was destroyed, so no stored row needs
  correcting;
- ~~no active-folder Data Owner attestation exists~~ — signed 2026-08-10, `docs/review/phase-2-data-owner-attestation-2026-08-09.md`;
- ~~field profile `2026-08-03.1` has no recorded maintainer acceptance~~ — superseded: `2026-08-09.1` was reviewed and accepted on 2026-08-10;
- the positive credential-confidentiality facts and allowed-origin browser
  path were observed; credential cleanup/revocation confirmation and the
  negative removed-origin browser path remain pending;
- D-c is accepted: 30 days maximum, with earlier deletion after the associated
  rehearsal, retry or incident closes; the §9.4 synthetic 500-Actor thresholds
  are accepted at 5 seconds for preview and 5 seconds for fresh apply;
- the inactive-folder preview, active-folder gate preview, Data Owner
  attestation, owner recommendations and final Phase 2 gate decision are
  pending.

This section is a convenience summary. `docs/project-management/status.md`
remains the controlled current-status record.
