# Gemini prompt — correct the WP-3 independent-review record

Correction work ID:
`C-P5.0-R5-RP11-H1-OH-S3-RT3-WP3-REV1-RR1-20261009-22`

## Objective

Correct the two audit-record findings in Gemini's returned WP-3 assignment
review. This is a repository-only documentation correction. Do not execute
WP-3, edit the candidate, accept it, appoint an executor or authorize any later
work.

The preserved review record to correct cumulatively is:

`docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp3-assignment.md`

Its expected identity is exactly:

- 10,878 bytes;
- 136 lines; and
- SHA-256
  `9d59619aef3c81a99063f042d7ee3109d9bcab156f0306299ad796981f0d52b3`.

The unchanged candidate remains:

`docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-claude-prompt.md`

with exact identity 12,650 bytes, 244 lines and SHA-256
`e09605d27daa8d25174302079a43ebccac64f69169007bad78496a8907457576`.

## Required reading and identity checks

Before editing, read completely, first byte through EOF, except where a named
portion is expressly sufficient:

1. `.agents/AGENTS.md`;
2. the reading map and §§0, 16 and 20 of `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. the active restriction banner in
   `docs/operations/disposable-test-server.md`;
5. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-gemini-review-prompt.md`;
6. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-claude-prompt.md`;
7. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp3-assignment.md`;
8. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp3-assignment-review-assessment.md`;
9. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp3-assignment-preparation.md`;
10. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md`;
11. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-acceptance.md`;
12. `docs/implementation-plan-archive/README.md`;
13. `docs/operations/disposable-test-server-archive/README.md`;
14. `docs/implementation-plan-through-2026-10-09-lit-full-wp3-assignment-review-pending.md`; and
15. `docs/operations/disposable-test-server-through-2026-10-09-lit-full-wp3-assignment-review-pending.md`.

Independently verify both pinned identities before editing. Also verify the two
snapshot identities:

- implementation-plan snapshot: 128,370 bytes, 2,610 lines, SHA-256
  `fbda54c8f4b9eae79026c5d95bf2bc27e69de84d291a1c19d51208e2323c785b`;
- disposable-server snapshot: 15,353 bytes, 330 lines, SHA-256
  `e458674dc6d4cd5750af73699d87cc84c8a0f968739e93d1269201c2c49e06a4`.

Any identity mismatch is a `HARD STOP`: create the corrected review record with
the exact mismatch and stop without changing an archive index.

## Required corrections

### WP3-RR-1 — review-record accuracy

The preserved review record lists 21 numbered required-reading items and says
all 21 were read, but its §8 then says physical existence was checked for 19
required-reading files. Correct the cumulative record to state the verified
count accurately: 21 numbered required-read paths.

The same section claims that working-tree inspection confirmed a clean
repository for read-only operations. Retract that claim. At minimum, the active
Gemini review prompt was an untracked pre-existing file before the review
created its return artifacts. Inspect and report the current tree accurately,
but do not pretend that the current status reconstructs the exact pre-edit
porcelain listing. If no contemporaneous pre-edit listing was preserved, say
that its exact entry count cannot now be established. Distinguish:

1. the pre-existing active review prompt and any other status known from the
   preserved evidence;
2. the files created or edited by the completed review assignment; and
3. the files this correction creates or edits.

This correction does not by itself invalidate the candidate identity check or
the substantive review. If the recheck reveals a material uncertainty about
the bytes or sources actually reviewed, return `INVALID RUN` rather than
forcing the former verdict.

### WP3-RR-2 — archive scope wording

After matching both snapshot identities, edit only the scope-description cell
of each new archive-index row:

1. in `docs/implementation-plan-archive/README.md`, describe
   `implementation-plan-through-2026-10-09-lit-full-wp3-assignment-review-pending.md`
   as the complete proposed-WP-3-assignment implementation plan immediately
   before independent review completion, including its then-current §20
   pointer;
2. in `docs/operations/disposable-test-server-archive/README.md`, describe
   `disposable-test-server-through-2026-10-09-lit-full-wp3-assignment-review-pending.md`
   as the complete disposable-test-server document immediately before
   independent review completion, including its then-current restriction
   banner.

Keep both existing snapshot links and SHA-256 values byte-for-byte unchanged.
Do not edit, replace, regenerate or rename either snapshot.

## Authorized output

Create exactly one cumulative corrected review record:

`docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp3-assignment-review-r1.md`

It is this correction assignment's durable handback. It must be self-contained
and include:

1. correction work ID, date and reviewer;
2. observed identities for the candidate, preserved review and both snapshots;
3. complete required-reading coverage;
4. accurate correction of the 21-versus-19 count;
5. an accurate working-tree statement with no invented historical count;
6. explicit dispositions of `WP3-RR-1` and `WP3-RR-2`;
7. candidate findings and counts by Blocking, Important and Optional class;
8. one exact candidate conclusion from the original review protocol;
9. confirmation that the candidate and both snapshots remain unchanged and
   WP-3 was not executed or authorized;
10. checks performed and not performed, files created and edited, and
    prohibited-action confirmation; and
11. one correction terminal state: `PASS`, `INVALID RUN` or `HARD STOP`.

The only other authorized edits are the two archive-index scope-description
cells specified under `WP3-RR-2`. Do not edit or delete the preserved review,
candidate, assessment, preparation record, snapshot, current-state pointer,
other archive/index row, accepted record or other file. Do not commit or push.
Return the corrected record to Peter and Codex for verification and current-
state reconciliation.

## Terminal states

- `PASS`: all four pinned identities match, the cumulative corrected review is
  complete and accurate, and both archive descriptions are corrected without
  changing either link or digest.
- `HARD STOP`: any pinned identity mismatches or a required source cannot be
  read. Record the exact mismatch or missing source and stop without editing an
  archive index.
- `INVALID RUN`: the correction cannot truthfully establish what candidate
  bytes or governing sources the original review examined, reviewer
  independence is compromised, or a prohibited operation occurs.

At the first terminal state, finish the durable corrected record and stop. Do
not continue into candidate remediation, acceptance or WP-3 execution.

## Permitted and prohibited operations

Repository reads and searches, `wc -l -c`, `sha256sum`, path/link checks,
`git diff --check`, and read-only Git status/diff are permitted. Creating the
single corrected review record and changing the two exact archive-index scope
cells are permitted.

Do not use SSH or access any host, retained evidence, secret, credential,
player data, production, staging, `oracle-test`, Foundry or database. Do not use
the network, install packages, run application or hook suites, edit source or
configuration, implement anything, mutate services, clean or recreate the
workspace, commit or push.

## Resolved Gemini invocation

Hand this assignment to Gemini with exactly:

```text
/goal Execute the active assignment in docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-gemini-review-record-correction-prompt.md. Proceed autonomously through every authorized step in order until the defined terminal state (PASS, INVALID RUN, or HARD STOP). Do not post intermediate progress updates, do not yield turns for user confirmation on background tasks, and do not stop until the final handback and closing record are fully written.
```
