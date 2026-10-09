# Gemini prompt — independent re-review of the proposed LIT-FULL WP-2 R1 assignment

Review work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP2-R1-REV2-20261009-16`

## Role and objective

Peter Duscha asks Gemini to perform an **independent, repository-only review**
of the proposed WP-2 assignment. Review the assignment prompt; do not execute
WP-2, produce its operation inventory, or authorize it.

The candidate under review is:

`docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r1-claude-prompt.md`

Its expected identity is exactly:

- 11,016 bytes;
- 207 lines; and
- SHA-256
  `6737e231e8237805a6517d006240321c4c4fb7aa14b1923aaa2b3a80cb2f6510`.

Gemini's first review found one Important path defect, `WP2-AR1`. R1 claims to
correct only that substantive defect while preserving the assignment boundary.
Re-review the correction and perform a complete regression review; do not limit
the review to the changed lines.

This review prompt authorizes only the read-only review and the single review
record named below. It does not accept the candidate, appoint its executor,
authorize WP-2, establish concrete Route 3, select LIT-FULL for implementation,
or authorize any later work package.

## Governing instructions and required reading

Before reviewing, read completely, first byte through EOF:

1. `.agents/AGENTS.md`;
2. the reading map and §§0, 16 and 20 of `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. the active restriction banner in
   `docs/operations/disposable-test-server.md`;
5. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r1-claude-prompt.md`;
6. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-assignment-preparation.md`;
7. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md`;
8. `docs/review/project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r8-acceptance.md`;
9. `docs/review/project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-g1-decisions.md`;
10. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r6-remediation-proposal.md`;
11. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r6-remediation.md`;
12. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-acceptance-and-bq-decisions.md`;
13. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-ex1-ex2-change-control-assessment.md`;
14. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-ex1-ex2-change-control-approval.md`;
15. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-assignment.md`; and
16. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-assignment-r1-remediation.md`.

The accepted cumulative R8 proposal and WP-1 R6 proposal are controlling
technical inputs. Earlier superseded drafts are comparison evidence only.

Before substantive review, independently run `wc -l -c` and `sha256sum` on the
candidate. If any expected identity value differs, do not review the changed
bytes. Write the review record with an identity `HARD STOP`, report the observed
values, and stop.

## Review standard

Determine whether the exact candidate is safe, complete, internally consistent
and decision-ready for Peter's later acceptance as the WP-2 assignment. Review
the prompt itself, not the future WP-2 work product.

At minimum, verify:

1. **Authority and gates:** WP-1 acceptance, the recorded BQ decisions, EX-1
   and EX-2 approval, HB-1 and baseline v1.8 are represented accurately; EX-3
   is not introduced; BC-2 remains a later WP-9 question; and the prompt creates
   no authority by itself.
2. **Exact scope:** the inventory covers exactly RT-1 through RT-5 plus SA-1
   `start` and SA-2 `stop`; the unprivileged entry and the EX-2 installer class
   H-1, RB-1, RS-1 and H-1R remain outside; no H-1R invocation is invented.
3. **WP-2 completeness:** every obligation of accepted R8 §9.5 and the
   applicable R8 §7.3 taxonomy, including rows 1 through 22 and 3a through 3g,
   is carried forward. Check the applicable WP-1 R6 §§10 through 12 constraints,
   including FR-1 and BQ-4.
4. **Operation coverage:** the requested inventory cannot silently omit process
   creation, credential change, descriptors, filesystem/metadata operations,
   locks, clocks, sleeps, polling, signals, identity validation, reaping,
   hashing, parsing, record publication, synchronization or unit/authorization
   interactions required by accepted behavior.
5. **No-dynamic-child rule:** every process-creation intent must resolve to a
   fork continuing in a static image or an `execve` of a design-controlled
   static image. The stop rule must prevent a distribution executable, SCDC or
   a silent BC-3 exception from being accepted as a WP-2 result.
6. **Traceability and reconciliation:** per-procedure and sub-role rows, accepted
   source tracing, DI-1 through DI-6 mapping inputs, SN/WB/RE/GD coverage, and
   closed reconciliation requirements are sufficient to expose omissions.
7. **Package separation:** the candidate does not perform or pre-decide WP-3
   interface design, WP-4 static-image design, WP-5 proof design, WP-6 mapping
   disposition or WP-7 estimation, and does not select concrete syscalls,
   libraries, languages, parsers or protocols prematurely.
8. **Semantic safety:** the prompt preserves fail-closed results, interruptions,
   residuals and unknown states; it does not convert a signal attempt into proof
   of exit, absence of a record into proof of absence, or a blocking class into
   an unsupported elapsed-time guarantee.
9. **Deliverability:** the two deliverables, terminal states, snapshot/index
   handling and four current-pointer updates are unambiguous, feasible and do
   not permit historical records to be rewritten.
10. **Operational restrictions:** the assignment authorizes no host or retained-
    evidence access, network research, secrets, implementation, test execution,
    package/service/database action, cleanup, commit, push or later slice.
11. **Identity and paths:** every named required-read and deliverable path is
    exact and exists where it is supposed to exist; no stale date or wrong-name
    defect is present.
12. **Acceptance clarity:** Peter can accept the exact candidate and appoint an
    executor without relying on an unstated interpretation or accidentally
    widening its scope.

Do not treat verbosity, wording preference or a possible enhancement as a
finding unless it affects correctness, auditability, safety or executability.
Do not remediate the candidate during this review.

## Finding classes

Use these classes consistently:

- **Blocking:** accepting the prompt could authorize work on a wrong, unsafe,
  contradictory or materially incomplete boundary, or an applicable gate is
  not actually closed.
- **Important:** the prompt is materially ambiguous, incomplete or
  insufficiently auditable, but the defect does not itself change the accepted
  boundary.
- **Optional:** a concrete, worthwhile improvement with no effect on correct
  execution or acceptance safety.

For every finding provide:

- a stable ID such as `WP2-AR1`;
- class;
- exact candidate line or section;
- governing evidence with exact source section;
- impact; and
- the smallest sufficient correction.

Do not invent findings to fill a category. If there are none, say so explicitly.

## Authorized output

Create exactly one durable review record:

`docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-assignment-r1.md`

The record must contain:

1. review identity, date and reviewer;
2. observed candidate line count, byte count and SHA-256;
3. governing sources reviewed;
4. findings ordered Blocking, Important, Optional;
5. an explicit count for each finding class;
6. one of these exact conclusions:
   - `ACCEPTABLE FOR PETER'S EXPLICIT ACCEPTANCE — NO FINDINGS`;
   - `REMEDIATION REQUIRED BEFORE ACCEPTANCE`; or
   - `HARD STOP — CANDIDATE IDENTITY MISMATCH`;
7. a statement that the review neither accepts nor authorizes WP-2 and that
   Peter must still accept the exact candidate and appoint its executor; and
8. checks performed, checks not performed and confirmation that no prohibited
   action occurred.

Do not edit the candidate, its preparation record, the four current-state
pointers, any archive or index, any accepted record, or any other file. Do not
commit or push. Return the review record to Peter and Codex for disposition.

## Permitted and prohibited operations

Repository reads and searches, `wc -l -c`, `sha256sum`, `git diff --check`, and
read-only Git status/diff are permitted. Creating the single review record above
is permitted.

Do not use SSH or access any host, retained evidence, secret, credential,
player data, production, staging, `oracle-test`, Foundry or database. Do not use
the network, install packages, run application or hook suites, edit source or
configuration, perform implementation, mutate services, clean the workspace,
commit or push. These operations cannot establish whether this assignment
prompt is correct.
