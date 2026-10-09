# Gemini prompt — correct the WP-2 R1 independent-review record

Correction work ID:
`C-P5.0-R5-RP11-H1-OH-S3-RT3-WP2-R1-REV2-RR1-20261009-17`

## Objective

Correct one evidence-accuracy defect in Gemini's returned R1 review record.
This is a repository-only documentation correction. Do not execute WP-2, edit
the R1 candidate, accept it, authorize it or change any current-state pointer.

The preserved review record to correct cumulatively is:

`docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-assignment-r1.md`

Its expected identity is exactly:

- 8,962 bytes;
- 125 lines; and
- SHA-256
  `139530224b167e51484c2946c803ae37f3ce7d21653951e662272226052d30a4`.

The unchanged R1 candidate remains:

`docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r1-claude-prompt.md`

with exact identity 11,016 bytes, 207 lines and SHA-256
`6737e231e8237805a6517d006240321c4c4fb7aa14b1923aaa2b3a80cb2f6510`.

## Required reading and identity checks

Read completely, first byte through EOF:

1. `.agents/AGENTS.md`;
2. the reading map and §§0, 16 and 20 of `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. the active restriction banner in
   `docs/operations/disposable-test-server.md`;
5. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r1-gemini-rereview-prompt.md`;
6. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r1-claude-prompt.md`;
7. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-assignment-r1.md`; and
8. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-assignment-r1-review-assessment.md`.

Independently verify both pinned identities before editing. An identity mismatch
is a `HARD STOP`; report observed values and create no corrected record.

## Required correction

The preserved review record contains these inaccurate claims:

1. §3 item 12 says every required-read item, deliverable path and current-state
   pointer path "exists on disk".
2. §8 says physical existence was verified for all required-reading,
   deliverable and pointer paths.

The two deliverables named by the R1 candidate are future WP-2 outputs and are
correctly absent before authorization and execution:

- `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md`;
- `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-handback.md`.

Verify and state the three categories accurately:

- all required-read file paths resolve to existing readable files;
- all four current-state pointer paths resolve to existing files or the exact
  controlled section/banner within them; and
- both deliverable literals are valid repository-relative future output paths,
  their `docs/review/` parent exists, and the deliverable files are correctly
  absent because WP-2 has not run.

Do not create either deliverable. Do not change the R1 candidate. Preserve all
other review content only after verifying that it remains accurate. If the
correction reveals a candidate finding, report and classify it rather than
forcing a no-findings result.

## Authorized output

Create exactly one cumulative corrected review record:

`docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-assignment-r1-review-r1.md`

It must be self-contained and include:

1. the correction work ID, date and reviewer;
2. both observed pinned identities;
3. complete governing-source coverage;
4. the corrected path/existence analysis;
5. candidate findings and explicit counts by class;
6. one exact conclusion from the original review protocol;
7. an explicit disposition of `WP2-R1RR-1` as corrected;
8. confirmation that the two future deliverables remain absent and WP-2 was not
   executed; and
9. checks performed, checks not performed and prohibited-action confirmation.

Do not edit or delete the preserved review, candidate, assessment, preparation
record, any pointer, archive, index, accepted record or other file. Do not
commit or push. Return the corrected record to Peter and Codex.

## Restrictions

Repository reads and searches, `wc -l -c`, `sha256sum`, path-existence checks,
`git diff --check` and read-only Git status/diff are permitted. Creating the one
corrected review record above is permitted.

Do not use SSH or access any host, retained evidence, secret, credential,
player data, production, staging, `oracle-test`, Foundry or database. Do not use
the network, install packages, run application or hook suites, edit source or
configuration, perform implementation, mutate services, clean the workspace,
commit or push.
