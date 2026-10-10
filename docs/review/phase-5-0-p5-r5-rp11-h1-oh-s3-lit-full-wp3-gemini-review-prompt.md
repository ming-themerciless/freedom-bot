# Gemini prompt — independent review of the proposed LIT-FULL WP-3 assignment

Review work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP3-REV1-20261009-21`

## Role and objective

Peter Duscha assigns Gemini to perform an **independent, repository-only
review** of the proposed WP-3 assignment. Review the assignment prompt itself;
do not execute WP-3, produce its interface contract, accept it, or authorize
any later work.

The candidate under review is:

`docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-claude-prompt.md`

Its expected identity is exactly:

- 12,650 bytes;
- 244 lines; and
- SHA-256
  `e09605d27daa8d25174302079a43ebccac64f69169007bad78496a8907457576`.

This assignment authorizes only the independent review, its durable review
record, and the bounded current-state/archive reconciliation specified below.
It does not accept the candidate, appoint a WP-3 executor, authorize WP-3,
establish concrete Route 3, select LIT-FULL for implementation, or authorize
WP-4 or any later package.

## Governing instructions and required reading

Before reviewing, read completely, first byte through EOF, except where a
named portion is expressly sufficient:

1. `.agents/AGENTS.md`;
2. the reading map and §§0, 16 and 20 of `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. the active restriction banner in
   `docs/operations/disposable-test-server.md`;
5. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-claude-prompt.md`;
6. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp3-assignment-preparation.md`;
7. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md`;
8. `docs/review/project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r8-acceptance.md`;
9. `docs/review/project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-g1-decisions.md`;
10. `docs/review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md`;
11. `docs/review/project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r6-acceptance.md`;
12. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s2-r2-citations.md`;
13. `docs/review/project-review-2026-10-06-p5-r5-rp11-h1-oh-s2-r2-acceptance.md`;
14. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r6-remediation-proposal.md`;
15. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r6-remediation.md`;
16. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-acceptance-and-bq-decisions.md`;
17. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-ex1-ex2-change-control-approval.md`;
18. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md`;
19. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r5-remediation-handback.md`;
20. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r5.md`; and
21. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-acceptance.md`.

The accepted cumulative R8 proposal, accepted OH-S2 R2 citation record,
accepted WP-1 R6 boundary and accepted WP-2 R5 inventory are the controlling
technical inputs. Earlier superseded drafts are comparison evidence only.

Before substantive review, independently run `wc -l -c` and `sha256sum` on
the candidate. If any expected identity value differs, do not review the
changed bytes. Write the review record with an identity `HARD STOP`, report the
observed values, reconcile the current-state documents as specified below, and
stop.

## Review standard

Determine whether the exact candidate is safe, complete, internally
consistent and decision-ready for Peter's later acceptance as the WP-3
assignment. Review the prompt, not the future WP-3 work product. Do not
remediate the candidate during this review.

At minimum, verify:

1. **Authority and gates:** WP-2 acceptance, baseline v1.8, the fixed F-1 and
   EX-1/EX-2 boundary, the unestablished concrete Route 3 state and the later
   BC-2/WP-9 decision are represented accurately; the prompt creates no
   authority by itself.
2. **Exact question scope:** the prompt answers exactly Q3-1, Q3-2, Q3-3,
   Q3-4, Q3-5, Q3-6, Q3-7, Q3-9 and Q3-11. It neither omits one nor invents a
   Q3 identifier, and it leaves Q6-6 and Q6-7 unanswered.
3. **Interface and call-site scope:** the required contract covers exactly
   DI-1 through DI-6 plus the SA-2 stop-unit call and reconciles them to all 41
   logical call sites in the accepted WP-2 inventory. It does not confuse
   logical call-site count with operation-row count.
4. **Required outcomes:** the nine stated Q3 outcomes preserve the accepted
   semantics for unit-state reads, transient holder creation, backstop timer
   and service creation, timer disarm, noninteractive Polkit authorization,
   DI-6 subject identity, stop-unit behavior, explicit baseline properties and
   direct on-disk/kernel baseline acquisition.
5. **Citation authority:** every material interface claim must be traceable to
   an authorized repository source or identified accepted design requirement;
   version-bound claims name systemd `259.5-0ubuntu3.4` or polkit
   `127-2ubuntu1.1` as applicable; accepted facts, mechanical derivations,
   proposed obligations and missing facts remain distinct.
6. **Fail-closed research boundary:** no browsing, host query, package query,
   memory-based fact or new fact collection is permitted. An unsupported fact
   needed for a WP-3-owned answer must cause the precise `HARD STOP`, not an
   invented citation or silent deferral.
7. **No-dynamic-child rule:** the candidate preserves static first root images,
   admits no dynamic child or distribution executable, and does not create an
   SCDC/BC-3 exception. DI-6 remains the only retained replacement-child
   intent.
8. **Package separation:** WP-3 does not design static images, select a
   language, library or syscall sequence, choose DI-6 process mechanics,
   implement parsing or blocking behavior, create proof plans, decide
   equivalence/unknown-effect mappings, estimate cost, or make the WP-9 route
   selection. WP-4 through WP-7 remain separately gated.
9. **Semantic safety:** the prompt preserves failure, cancellation,
   interruption, residual and unknown-effect distinctions; it does not turn a
   signal attempt into proof of exit, a missing record into proof of absence,
   or a historical class-E wait budget into an interface elapsed-time bound.
10. **Deliverability:** the two WP-3 deliverables, reading ledger, contract
    contents, citation matrix, Q3 closure, WP-4 input table, reconciliation,
    checks, stop rules, snapshot/index handling and terminal states are
    unambiguous and feasible.
11. **Historical integrity:** accepted inputs and archived evidence cannot be
    rewritten; only the four named current-state pointers and their new
    snapshots/index rows may change on the later WP-3 return.
12. **Operational restrictions:** the candidate grants no host, retained-
    evidence, secret, network, implementation, test, package, service,
    database, cleanup, activation, rollback, commit or push authority.
13. **Identity and paths:** every required-read, deliverable, current pointer,
    snapshot family and archive-index path is exact and compatible with the
    repository; there is no stale identity, missing source or wrong filename.
14. **Acceptance clarity:** Peter can accept these exact candidate bytes and
    appoint an executor without relying on an unstated interpretation or
    accidentally widening the assignment.

Do not treat verbosity, wording preference or a possible enhancement as a
finding unless it affects correctness, auditability, safety or executability.

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

- a stable ID such as `WP3-AR1`;
- class;
- exact candidate line or section;
- governing evidence with exact source section;
- impact; and
- the smallest sufficient correction.

Do not invent findings to fill a category. If there are none, say so
explicitly.

## Authorized review record

Create exactly one substantive review record:

`docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp3-assignment.md`

That record is also this assignment's durable handback. It must contain:

1. review identity, date and reviewer;
2. observed candidate line count, byte count and SHA-256;
3. governing sources reviewed;
4. findings ordered Blocking, Important, Optional;
5. an explicit count for each finding class;
6. one of these exact candidate conclusions:
   - `ACCEPTABLE FOR PETER'S EXPLICIT ACCEPTANCE — NO FINDINGS`;
   - `ACCEPTABLE FOR PETER'S EXPLICIT ACCEPTANCE — OPTIONAL FINDINGS ONLY`;
   - `REMEDIATION REQUIRED BEFORE ACCEPTANCE`; or
   - `HARD STOP — CANDIDATE IDENTITY MISMATCH`;
7. a statement that the review neither accepts nor authorizes WP-3 and that
   Peter must still accept the exact candidate and appoint its executor;
8. checks performed, checks not performed and confirmation that no prohibited
   action occurred; and
9. the review-assignment terminal state defined below.

## Current-state reconciliation

Before editing any current-state pointer, preserve its exact pre-review-return
bytes in these snapshots beside the canonical files:

1. `docs/review/Handover-information-through-2026-10-09-lit-full-wp3-assignment-review-pending.md`;
2. `docs/project-management/status-through-2026-10-09-lit-full-wp3-assignment-review-pending.md`;
3. `docs/implementation-plan-through-2026-10-09-lit-full-wp3-assignment-review-pending.md`; and
4. `docs/operations/disposable-test-server-through-2026-10-09-lit-full-wp3-assignment-review-pending.md`.

Add each snapshot's SHA-256 to, respectively,
`docs/review/handover-archive/README.md`,
`docs/project-management/status-archive/README.md`,
`docs/implementation-plan-archive/README.md` and
`docs/operations/disposable-test-server-archive/README.md`. Do not overwrite
or rewrite an existing snapshot.

Reconcile only these four current-state pointers after the review record is
complete:

1. `docs/review/Handover information`;
2. `docs/project-management/status.md`;
3. implementation-plan §20; and
4. the restriction banner in
   `docs/operations/disposable-test-server.md`.

All four must link the durable review record and agree on one state:

- for a no-findings or optional-only conclusion: `WP-3 ASSIGNMENT REVIEWED —
  PETER ACCEPTANCE AND EXECUTOR APPOINTMENT PENDING`;
- for any Blocking or Important finding: `WP-3 ASSIGNMENT REVIEWED
  — REMEDIATION REQUIRED BEFORE ACCEPTANCE`; or
- for candidate identity mismatch: `HARD STOP — WP-3 CANDIDATE IDENTITY
  MISMATCH`.

Preserve baseline v1.8, the fixed F-1/EX boundary, unanswered Q6-6/Q6-7,
unestablished concrete Route 3, the no-host restriction and every later gate.
Do not imply that this review accepts the candidate or appoints an executor.

The archive/index entries and bounded pointer reconciliation are clerical
review-handback work, not permission to alter historical evidence or any
technical decision.

## Terminal states

- `PASS`: the exact candidate identity matched, the substantive review and
  durable record are complete, and the required archive/pointer reconciliation
  is complete. `PASS` means the **review assignment** completed; it does not
  mean the candidate was accepted and may accompany either a no-findings or a
  remediation-required candidate conclusion.
- `HARD STOP`: the candidate identity mismatched or a required governing source
  could not be read. Record the precise condition and observed identity where
  applicable, reconcile the current state, and stop without substantive review.
- `INVALID RUN`: reviewer independence was compromised, a prohibited action
  occurred, or the review cannot truthfully establish what bytes or sources it
  examined. Record the precise invalidating condition, reconcile the current
  state without a candidate verdict, and stop.

At the first terminal state, finish the durable handback and pointer
reconciliation, then stop. Do not proceed into remediation or WP-3 execution.

## Permitted and prohibited operations

Repository reads and searches, `wc -l -c`, `sha256sum`, mechanical Markdown
table/path/link checks, `git diff --check`, and read-only Git status/diff are
permitted. Writing the single review record, the four exact snapshots, four
archive-index rows and bounded four-pointer reconciliation is permitted.

Do not edit the candidate, its preparation record, any accepted technical
input, an earlier prompt/handback/review/acceptance, application or
infrastructure source, configuration, test, retained-evidence artifact or
existing snapshot. Do not use SSH or access any host, retained evidence,
secret, credential, player data, production, staging, `oracle-test`, Foundry
or database. Do not use the network, install packages, run application or hook
suites, implement anything, mutate services, clean or recreate the workspace,
commit or push. These operations cannot establish whether this assignment
prompt is correct.

## Resolved Gemini invocation

Hand this assignment to Gemini with exactly:

```text
/goal Execute the active assignment in docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-gemini-review-prompt.md. Proceed autonomously through every authorized step in order until the defined terminal state (PASS, INVALID RUN, or HARD STOP). Do not post intermediate progress updates, do not yield turns for user confirmation on background tasks, and do not stop until the final handback and closing record are fully written.
```
