# Claude assignment — LIT-FULL WP-3 R1 focused cumulative remediation

Date: 2026-10-10

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP3-R1-20261010-22`

Executor: Claude, once, under the bounded authority recorded in
`docs/review/project-review-2026-10-10-p5-r5-rp11-h1-oh-s3-lit-full-wp3-r1-remediation-acceptance-and-claude-activation.md`

## Objective

Remediate exactly the two Important findings in the independent review of the
WP-3 HARD STOP return:

- `WP3-HS-R1`: cancellation semantics for DI-2, DI-3, DI-4 and DI-S are not
  explicitly supported or registered as missing; and
- `WP3-HS-R2`: the original handback's reading ledger does not unambiguously
  establish that every required source was read completely before the first
  edit.

Produce a corrected cumulative interface contract and a new durable remediation
handback. Preserve the substantive WP-3 `HARD STOP`: the authorized sources
still do not establish the complete loader-free client contract. This
assignment does not accept WP-3, authorize WP-4 through WP-7, establish concrete
Route 3, select LIT-FULL for implementation, or authorize new source research.

## Required reading — binding precondition

Before editing the interface contract, a current-state pointer, an archive
index or any deliverable, read every item below completely, first byte through
EOF. A search, excerpt, heading scan, earlier read, summary or generated synopsis
does not satisfy this precondition, except that items 2 and 4 require exactly
the named portions.

1. `.agents/AGENTS.md`;
2. the reading map and §§0, 16 and 20 of `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. the active restriction banner in
   `docs/operations/disposable-test-server.md`;
5. `docs/review/project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-g1-decisions.md`;
6. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md`;
7. `docs/review/project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r8-acceptance.md`;
8. `docs/review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md`;
9. `docs/review/project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r6-acceptance.md`;
10. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s2-r2-citations.md`;
11. `docs/review/project-review-2026-10-06-p5-r5-rp11-h1-oh-s2-r2-acceptance.md`;
12. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r6-remediation-proposal.md`;
13. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r6-remediation.md`;
14. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-acceptance-and-bq-decisions.md`;
15. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-ex1-ex2-change-control-approval.md`;
16. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md`;
17. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r5-remediation-handback.md`;
18. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r5.md`;
19. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-acceptance.md`;
20. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-claude-prompt.md`;
21. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp3-acceptance-and-claude-activation.md`;
22. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-interface-contract.md`;
23. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-handback.md`;
24. `docs/review/project-review-2026-10-10-p5-r5-rp11-h1-oh-s3-lit-full-wp3-hard-stop.md`;
25. this exact prompt; and
26. `docs/review/project-review-2026-10-10-p5-r5-rp11-h1-oh-s3-lit-full-wp3-r1-remediation-acceptance-and-claude-activation.md`.

Before the first edit, record in working notes each required item's path, line
count, byte count and SHA-256. The new remediation handback must contain the
complete 26-item ledger and state unambiguously that every item was read as
specified before the first edit. If any item cannot be read completely as
specified, return `HARD STOP` before editing the interface contract.

The new reading establishes the remediation execution's evidence basis. Do not
rewrite the original handback or claim that its executor completed a read that
the historical record does not prove.

## Fixed accepted boundary

Preserve without reinterpretation:

- baseline v1.8;
- LIT-FULL under R3-ROOT remains only a readiness investigation and is not
  selected for implementation;
- concrete Route 3 remains unestablished;
- in scope remain exactly RT-1 through RT-5, SA-1 (`start`) and SA-2 (`stop`);
- F-1 remains B2-F, both lifecycle acts remain in and B3-OUT remains effective;
- EX-1 and EX-2 remain effective only for their accepted uses; no EX-3 exists;
- no dynamic child or distribution executable is admitted beneath a first
  design-controlled root image;
- DI-6 remains the only retained replacement-child intent;
- H-1, RB-1, RS-1 and H-1R remain outside the set;
- Q6-6 and Q6-7 remain unanswered;
- BC-2 remains a later WP-9 decision; and
- WP-4 through WP-7 remain separately gated and unauthorized.

No remediation text may weaken an accepted failure, interruption, residual,
unknown-effect, no-retry or fail-closed rule. A cancelled client wait is not
proof that a queued job stopped or that a mutating request had no effect.

## Deliverables

1. Correct cumulatively in place:
   `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-interface-contract.md`.
2. Create the complete terminal handback:
   `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-r1-remediation-handback.md`.
3. At terminal return, preserve the then-current four R1-authorization pointers
   in dated, verbatim `lit-full-wp3-r1-remediation-authorization` snapshots
   beside their canonical files, add their SHA-256 values to the four archive
   indexes, then update only:
   - `docs/review/Handover information`;
   - `docs/project-management/status.md`;
   - implementation-plan §20; and
   - the restriction banner in
     `docs/operations/disposable-test-server.md`.

Do not edit the original WP-3 prompt, original handback, independent review,
activation record, WP-2 inventory, accepted proposals/acceptances or any
historical snapshot.

## Required remediation — `WP3-HS-R1`

Correct the cancellation gap without supplying an upstream fact that the
authorized sources do not establish:

1. Expand `UF-05` so its exact missing fact includes, for DI-2, DI-3, DI-4 and
   DI-S:
   - how a client cancels or abandons its wait;
   - whether an already accepted or queued job continues after that event;
   - how the eventual job result and mutation effect are observed; and
   - how cancellation, client disconnection and an unconfirmed outcome map to
     the accepted `refused`/`error` and unknown-effect boundaries.
2. Amend the common contract and §§3.2, 3.3, 3.4 and 3.7 to name this gap
   explicitly. Preserve the distinction between cancelling a client wait and
   cancelling a manager job.
3. State cancellation treatment explicitly for every interface:
   - DI-1: preserve the proposed fail-closed `error`, clearly classified as a
     proposed obligation rather than an upstream fact;
   - DI-2, DI-3, DI-4 and DI-S: identify the expanded `UF-05` gap and state
     that cancellation/abandonment never proves no effect and never permits a
     silent retry;
   - DI-5: preserve `UF-10` as owning Polkit call cancellation;
   - DI-6: state precisely whether cancellation belongs to the enclosing DI-5
     decision and later subject cleanup, or register any additional unsupported
     interface fact. Do not design the WP-4 process mechanics.
4. Reconcile the Q3 closure table, unsupported-fact registry, WP-4 input table,
   reconciliation, acceptance checklist, headline and stop result. If the
   expanded `UF-05` is sufficient, keep the existing identifier rather than
   renumbering later UFs merely for presentation.
5. Preserve Q6-6 and Q6-7 unanswered. Do not decide the unknown-effect mapping
   for DI-3 or DI-4/BS-2/BS-3, and do not extend it to BS-4.

The corrected contract must still return `HARD STOP`; this remediation makes
the missing-fact account complete, not the upstream interface supported.

## Required remediation — `WP3-HS-R2`

1. Leave the original handback unchanged as historical evidence.
2. In the new remediation handback, quote the original ledger defect accurately
   and state that the original wording does not prove complete pre-edit reading.
3. Include the complete 26-item remediation reading ledger and state, without
   alternatives or qualifications, that every required item was read exactly as
   specified before the first remediation edit.
4. State that this new complete read is the evidence basis for the cumulative
   corrected contract and supersedes reliance on the original ambiguous ledger;
   it does not rewrite or make a claim about the original executor's actions.
5. If that statement cannot be made truthfully, return `HARD STOP` before
   editing the contract and report the precise unreadable or incomplete item.

## Cumulative integrity requirements

- Preserve the seven-interface roster and all 41 logical call sites unless a
  mechanical re-parse proves the earlier count wrong; report any discrepancy
  rather than silently changing it.
- Preserve exactly the nine Q3 identifiers and their existing closure states:
  Q3-1 through Q3-7 and Q3-9 remain not closed; Q3-11 remains the fail-closed
  record required by the accepted prompt.
- Revalidate every citation and every `SF`, `MD`, `DR`, `PO3` and `UF`
  classification affected by the edits.
- Do not turn a proposed obligation into an accepted fact.
- Do not browse, query a host, inspect installed packages or binaries, or use
  memory to fill an unsupported fact.
- Do not design a language, library, syscall sequence, static image, parser,
  process-creation mechanism, proof plan, equivalence disposition or cost
  estimate.
- Do not prepare or authorize WP-4 through WP-7.

## Checks and terminal evidence

Allowed checks are repository-only reads and searches, link/path checks,
`wc -l -c`, `sha256sum`, mechanical Markdown-table parsing,
`git diff --check` and read-only Git status/diff.

Do not run application or hook suites, builds, formatters or linters. They are
outside this documentation-only authority and cannot establish the missing
interface facts.

The new handback must report:

- both findings and exactly how each was remediated;
- the complete 26-item pre-edit reading ledger;
- final deliverable paths, line counts, byte counts and SHA-256 values where a
  non-self-referential value is possible;
- files created and edited;
- final interface, call-site, Q3, citation and unsupported-fact counts;
- exact checks and results, and checks not run with reasons;
- every unresolved later-package question;
- confirmation that no prohibited action occurred; and
- focused questions for independent re-review.

## Prohibited operations

Do not use SSH or connect to any host. Do not access retained evidence,
secrets, credentials, player data, production, staging, `oracle-test`, Foundry
or a database. Do not perform network research, fresh fact collection, package
operations, installation, implementation, configuration/infrastructure edits,
launcher work, builds, tests, formatters, service/database operations, cleanup,
workspace recreation, OH-S4/OH-S4p or later work, H-1/H-2, activation,
rollback, commit or push.

The R5 and H-0G retained paths remain untouched pending separately gated LC-3
through LC-5 authority.

## Return and terminal state

Before replacing the four current-state pointers, preserve their exact
R1-authorization state in the required snapshots and index each SHA-256.

On successful remediation, the handback and pointers must say:

`WP-3 R1 REMEDIATION RETURNED — HARD STOP PRESERVED — INDEPENDENT RE-REVIEW PENDING`

Otherwise return `HARD STOP` with the precise reason and make the terminal
pointers consistent with it.

The return does not accept WP-3, authorize WP-4, establish concrete Route 3 or
select LIT-FULL for implementation. A different independent reviewer must
re-review the complete cumulative return, and Peter must later decide its
acceptance before any successor assignment may be prepared.

## Invocation

Execute exactly:

```text
Execute the exact accepted assignment in docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-r1-remediation-claude-prompt.md. Proceed autonomously through every authorized repository-only step until the prompt-defined terminal state. Do not perform any prohibited operation or prepare WP-4 through WP-7. Write the complete durable handback and current-state return before stopping.
```
