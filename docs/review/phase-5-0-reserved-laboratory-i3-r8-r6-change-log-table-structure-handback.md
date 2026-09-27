# Claude remediation handback — C-P5.0-LAB-I3-R8-R6; change-log table structure — 2026-09-22

**Returned for independent Codex re-review. LAB-I3-R8-D1-TABLE-1 remains Open,
Important. The implementing agent closes nothing.**

**Authority.** The R8-R6 prompt at the head of `docs/review/Handover information`
was marked *draft only*. On 2026-09-22 the maintainer told Claude in a Claude
Code session to "implement docs/review/Handover information:1", and Claude took
that as Peter Duscha's acceptance and explicit assignment of the bounded
repository-only scope. No written acceptance banner existed before the pass. The
handover now records how the assignment was received, and **Peter Duscha should
confirm it**.

## 1. The finding addressed

**LAB-I3-R8-D1-TABLE-1 — Important, malformed controlled register, Open.** In
`docs/project-management/change-log.md` the maintainer decision row
`C-P5.0-LAB-I3-R8-D1` sat on line 7, between the table header (line 6) and the
delimiter (line 8). GitHub-flavoured Markdown needs the delimiter directly after
the header, so the change log did not render as a table.

## 2. What was done

1. **Change log, structure only.** Lines 7 and 8 were swapped: the delimiter
   `|---|---|---|---|---|---|---|` is now line 7, and the D1 row is line 8 as
   the first data row. Nothing else in the file changed. No change-log row was
   added for this repair, because the prompt limits the change log to the
   structural fix and keeps D1 as the first data row.
2. **Controlled summaries.** LAB-I3-R8-D1-TABLE-1 is recorded as **Open,
   Important, repaired and awaiting Codex re-review** in the status, RAID,
   plan §20, handover and disposable-server banner. The already-decided R8-R5
   state is restated as it was decided: **C-P5.0-LAB-I3-R8-R5 accepted;
   LAB-I3-R8-R2-ROLLBACK-1 Closed, remediated; no R8-R2 rollback wanted.** The
   handover's R8-R5 "Active state" block, which still showed ROLLBACK-1 as Open,
   is relabelled *Superseded* with a note; its text is unchanged. The server
   banner's stale "R8-R5 … awaiting independent Codex review" note is marked
   historical by a new top banner; the note itself is unchanged.
3. **Decision register not changed.** Its head already records the R8-R5
   acceptance, and its pending I3 decision is still accurate.

## 3. Files changed

| File | Change |
|---|---|
| `docs/project-management/change-log.md` | delimiter and D1 row swapped (lines 7–8); on follow-up (§8.1), rows R8-R6 and D2 added as lines 8–9 and one stray `\|` in `C-P5.0-LAB-I3-R5-I` replaced by `;` |
| `docs/project-management/status.md` | new current-status block; previous block marked superseded |
| `docs/project-management/raid-register.md` | repair paragraph added to the LAB-I3-R8-D1-TABLE-1 entry; state still Open, Important |
| `docs/implementation-plan.md` | §20 new current action; previous action marked superseded |
| `docs/operations/disposable-test-server.md` | new top "Restriction unchanged" banner |
| `docs/review/Handover information` | R8-R6 prompt retitled *Consumed* with assignment and consumption notes (prompt text retained unchanged); new R8-R6 active-state block; R8-R5 block relabelled superseded |
| `docs/review/phase-5-0-reserved-laboratory-i3-r8-r6-change-log-table-structure-handback.md` | this handback (new, untracked) |

No source, test, hook, manifest, generated artifact, migration, schema or
configuration file was changed. **No migrations were added.**

## 4. Checks run

| Check | Result |
|---|---|
| Pre-edit assertions (Python, bytes): line 6 starts with `\| Version / change \|`, line 7 starts with `\| **C-P5.0-LAB-I3-R8-D1 `, line 8 equals the 7-column delimiter | all held; the swap was written only after they passed |
| D1 row byte identity | SHA-256 `ef8debfac61e3e0a3b314a801e5c154d58fc3a35f06025b67639f9ee74cfba03`, 1,001 bytes, before (old line 7) and after (new line 8); bytes equal |
| Rest of file | every other line byte-identical to a pre-edit scratch copy; line count unchanged; `diff` shows only the one-line move |
| File digest | `a9314a1a…116c251` before → `c467e517…22626a04ad` after |
| Table structure (Python) | table runs from line 6 to line 123, 118 lines; line 7 matches the delimiter pattern; no other delimiter row inside the table; first data row is D1 |
| Column count | every row has 7 cells except line 28 (see §7) |
| `git diff --check` on the change log | clean, exit 0 |
| Consistency (`grep`) | TABLE-1 appears as Open, Important in status, RAID, plan §20 and the handover; ROLLBACK-1 appears as Closed wherever the current state is described |

*Method note:* one `sed -n 7p | sha256sum` check after the swap gave a different
digest. That was my error: after the swap, line 7 is the delimiter. The byte
comparison above is the correct check.

## 5. Checks not run, and why

- **No test suite, linter or type checker.** The prompt forbids running suites
  for this documentation-only repair, and no code changed. No suite figure is
  cited or claimed.
- **No secrets scan and no command expected to engage a secrets guard.** The
  prompt forbids them. **No guard or tool refused any call.**
- **No rendered-Markdown check on GitHub.** Rendering was checked structurally
  against the GFM table rules, not by viewing the page.
- **Nothing on `oracle-test`.** No SSH, synchronization, host inspection,
  verifier, suite or database access. The three protected `/tmp` artifacts
  were not accessed.

## 6. Repository state

- Branch `docs/platform-plan`; nothing committed, staged or pushed.
- **Before:** 97 paths in `git status --porcelain` (saved to a session
  scratch file).
- **After:** 98 paths. The only new path is this handback. The six edited
  documents were already modified by earlier passes, and their earlier-pass
  changes are preserved.

## 7. Security, configuration, deployment and rollback

- **Security:** none. No secret, credential or player data was read or written,
  and no guard or hook was changed.
- **Configuration and deployment:** none.
- **Rollback:** to undo the change-log repair, swap lines 7 and 8 back. Because
  the D1 row and the delimiter are byte-exact and no other change-log byte
  moved, that swap restores the pre-R8-R6 change log exactly; the pre-edit
  digest `a9314a1a…` confirms it. The summary edits are additive blocks and
  relabels that were reviewed as hunks. Reverse those only with a reviewed
  reverse patch, **never** `git checkout --` or a restore from `HEAD`: every
  edited document carries earlier-pass uncommitted work. No rollback is
  proposed.

## 8. Observations outside the original scope — fixed on follow-up instruction

As first returned, this section reported two observations and left them
untouched. The maintainer then told Claude, on 2026-09-22, to fix both before
the handback goes to Codex. The follow-up is in §8.1.

1. Change-log row `C-P5.0-LAB-I3-R5-I` (2026-09-20; line 28 when first
   reported, line 30 now) had 8 cells against the 7-column header.
   *Correction to the first description:* the extra `|` was **not** inside the
   last cell. It sat between the Reviews text and the `[Handback](…)` link, so
   the link became its own cell, the Approval text ("**Returned for independent
   Codex technical and security review…**") became an eighth cell, and GFM
   **dropped that Approval text** from the rendered table.
2. The R8-R5 acceptance decision had no row of its own in the change log.

## 8.1 Follow-up, 2026-09-22

- **Row `C-P5.0-LAB-I3-R5-I`:** the one stray ` | ` before `[Handback](…)` was
  replaced by `; `. This puts the link in the Reviews cell, as in the
  neighbouring rows (for example `C-P5.0-LAB-I3-R5-A`), and restores the
  Approval cell. Pre-edit assertions checked that the row started as expected
  and that the replaced text occurred exactly once. `diff` against a pre-edit
  scratch copy shows only that one change.
- **Row `C-P5.0-LAB-I3-R8-D2`** (requester Peter Duscha, Acceptance
  Authority) records the R8-R5 acceptance as the decision register and
  handover state it: R8-R5 review accepted, LAB-I3-R8-R2-ROLLBACK-1 closed as
  remediated, no R8-R2 rollback, and TABLE-1 raised. It says it was recorded
  under R8-R6 and links the decision register, because no separate decision
  record file exists.
- **Row `C-P5.0-LAB-I3-R8-R6`** records this pass and the change to a
  historical row, because the change log is append-only. It is the newest
  row, then D2, then D1.
- **This changes the first return in two ways.** D1 is no longer the first data
  row; its bytes are unchanged. And §2's "no change-log row added" no longer
  holds. The summaries in status, RAID, plan §20, the handover and the server
  banner are updated to match.
- **Checks:** all 120 table lines (header, delimiter and 118 data rows) have 7
  cells. The only delimiter row is line 7. `git diff --check` is clean across
  the working tree. No suite, secrets scan or host action; no guard refused a
  call.
- **Rollback:** delete change-log lines 8 and 9 (the R8-R6 and D2 rows), and
  change the `; [Handback]` in the `C-P5.0-LAB-I3-R5-I` row back to
  ` | [Handback]`. Do this by a reviewed edit, never by a checkout.

## 9. Proposed independent reviewer focus

1. Confirm the final change-log delta: the delimiter move, the R5-I separator
   correction, and the two added R8-R6/D2 rows; confirm that the table renders.
2. Confirm that no prior disposition was reopened or altered, and that
   LAB-I3-R8-D1-TABLE-1 is shown as Open everywhere it is summarized.
3. Check the §8.1 follow-up: the one-character fix to `C-P5.0-LAB-I3-R5-I`,
   and whether D2 faithfully records the maintainer's R8-R5 decision without
   adding to it.
4. Confirm the assignment basis recorded at the head of the handover.

## 10. Disposition

LAB-I3-R8-D1-TABLE-1 remains **Open, Important**, for Codex re-review.
PR-20260920-LAB-I3-R6-1 and PR-20260920-LAB-I3-R6-2 remain **Open, Blocking**;
I3 remains performed but unconfirmed; `plan.is_executable=False`; Package 5.0
remains **not ready**; **no action on `oracle-test` is authorized.** No scope,
schedule or risk baseline change. The pass stops here.
