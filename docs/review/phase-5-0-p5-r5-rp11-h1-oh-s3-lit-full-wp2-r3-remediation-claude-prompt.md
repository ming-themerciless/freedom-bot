# Accepted Claude prompt — LIT-FULL WP-2 R3 remediation

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP2-R3-20261009-17`

Status: **accepted, assigned to Claude and executable once**

## Authority and objective

Peter Duscha authorizes Claude to remediate only the three findings in the
independent WP-2 R2 re-review:

- `WP2-R2-1` — the one-time R2 execution did not satisfy its binding complete-
  reading precondition;
- `WP2-R2-2` — the inventory extends SN-10 / A-I-16 from accepted BS-2/BS-3
  sites to BS-4 without accepted authority; and
- `WP2-R2-3` — the durable handback omits the final exact link-check result.

Produce a corrected, cumulative WP-2 operation inventory that remains
self-contained and replaces the R2 inventory as the proposed WP-2 result. This
assignment does not accept WP-2, authorize WP-3, establish concrete Route 3 or
select LIT-FULL for implementation.

## Required reading — binding precondition

Before editing any deliverable or current-state pointer, read every item below
completely, first byte through EOF. A search, excerpt, heading scan, prior read,
summary, tool-generated synopsis or statement that the file is too large does
not satisfy this precondition.

1. `.agents/AGENTS.md`;
2. the reading map and §§0, 16 and 20 of `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. the restriction banner in
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
15. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-ex1-ex2-change-control-assessment.md`;
16. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-ex1-ex2-change-control-approval.md`;
17. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r1-claude-prompt.md`;
18. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md`;
19. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-handback.md`;
20. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r1.md`;
21. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r2-remediation-claude-prompt.md`;
22. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r2-remediation-acceptance-and-claude-activation.md`;
23. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r2-remediation-handback.md`;
24. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r2.md`;
25. this exact prompt; and
26. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r3-remediation-acceptance-and-claude-activation.md`.

The accepted one-host design, cumulative R8 remediation, accepted WP-1 R6
record and EX-1/EX-2 approval remain governing sources. Earlier superseded
proposal rounds remain comparison evidence only.

Before the first edit, record in working notes for every item above its path,
line count, byte count and SHA-256 as read. The complete terminal handback must
include that reading ledger and state unambiguously that every item was read
first byte through EOF before the first edit. If any item cannot be read
completely, return `HARD STOP` before changing the inventory; do not substitute
searches or excerpts.

## Fixed boundary

Preserve the accepted R2 boundary without reinterpretation:

- LIT-FULL under R3-ROOT;
- in scope: RT-1 through RT-5, SA-1 (`start`) and SA-2 (`stop`);
- F-1: B2-F; both lifecycle acts in; B3-OUT;
- EX-1 and EX-2 effective, no EX-3;
- no dynamic child beneath a first design-controlled image;
- every retained process creation ultimately classified as a fork continuing
  in a static image or an `execve` of a design-controlled static image;
- H-1, RB-1, RS-1 and H-1R outside the root-procedure set;
- B2-N and a Python-free installer are not prerequisites;
- BC-2 remains a later WP-9 question; and
- concrete Route 3 remains unestablished.

Do not reopen or alter any of these items.

## Deliverables

1. Correct in place, as a cumulative document:
   `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md`.
2. Create the complete terminal handback:
   `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r3-remediation-handback.md`.
3. At terminal return, preserve the then-current four R3-authorization pointers
   in dated, verbatim snapshots beside their canonical files, add their
   SHA-256 values to the four archive indexes, then update only:
   - `docs/review/Handover information`;
   - `docs/project-management/status.md`;
   - implementation-plan §20; and
   - the restriction banner in
     `docs/operations/disposable-test-server.md`.

Do not edit either earlier handback, either independent review, an earlier
prompt or activation record, an accepted proposal/acceptance record or any
earlier snapshot.

## Required remediation — `WP2-R2-1`

1. Complete the binding reading precondition before any edit.
2. Revalidate the entire cumulative inventory, not only the changed rows,
   against all governing sources. Preserve every unaffected accepted operation,
   source citation, failure contract, interruption state, residual, unknown
   state and deferred question.
3. Report any newly discovered conflict, omission or competing accepted passage
   that affects a procedure operation, question or closed-coverage claim. Do not
   silently repair a matter outside the three authorized findings.
4. If complete reading shows that Q6-7's AM-0 question is genuinely resolved,
   or that a required accepted function cannot be inventoried inside the fixed
   boundary, return `HARD STOP` with exact passages; do not select an answer.
5. Put the complete reading ledger in the durable handback. A statement in chat
   is not evidence and cannot repair an incomplete ledger.

## Required remediation — `WP2-R2-2`

Preserve BS-2, BS-3 and BS-4 terminal disarm as three logical DI-4 call sites.
Call-site coverage and failure-contract authority are separate questions.

Unless complete governing text explicitly resolves the point:

1. State SN-10 / A-I-16's accepted `effect: "unknown"` obligation only for
   DI-3 at AK-1 and DI-4 at BS-2 and BS-3.
2. Do not state or imply that SN-10, A-I-16 or the BS-2/BS-3 unknown-effect
   contract applies to BS-4 merely because it has the same call form.
3. Preserve BS-4's accepted terminal-disarm operation and accepted failure
   contract exactly as stated by its own governing passages.
4. Carry the unresolved question whether the unknown-effect obligation extends
   to BS-4 as an unanswered accepted-text gap under Q6-7, owned by WP-6. WP-2
   selects neither extension nor exclusion. Do not create a new question ID.
5. Keep Q6-6 for the accepted obligation and its unmapped non-child realization
   at DI-3, BS-2 and BS-3 only.
6. Reconcile at minimum `RT4.BS4.2`, `RT4.SN.1`, §7, §8.1, §11, §12 Q6-6 and
   Q6-7, §13, §14, §15, every affected tag/count/coverage table and the
   handback.

If complete governing text explicitly says that the obligation applies to
BS-4, do not silently use that passage. Return `HARD STOP` with the exact
competing passages because this remediation is authorized to preserve the gap,
not decide new procedure behavior.

## Required remediation — `WP2-R2-3`

1. Make the inventory, R3 handback, four terminal pointers, four authorization
   snapshots and four archive-index rows complete, including all link-bearing
   content. Reserve a non-link-bearing result field in the handback, run the
   check, populate that field, then rerun the same check after population. No
   link-bearing content may change after the rerun.
2. Put the rerun's exact scope, link count, broken-link count and exit/result in
   the durable R3 handback itself. Replacing the reserved result field does not
   alter the link graph; the rerun is the terminal link check.
3. The handback may explain why it cannot contain its own SHA-256, but it may
   not defer any required check result, reading evidence or substantive return
   fact to terminal chat.
4. The terminal chat may summarize or link the handback; it must not be the only
   place where required evidence exists.

## Integrity and scope requirements

- Preserve all fifteen original operation-inventory requirements from the R1
  prompt and every unaffected R2 correction.
- Every operation row must trace to accepted text; every mechanical statement
  must be re-derivable from the delivered tables.
- A signal attempt is never proof of exit, and a missing record is never proof
  of absence.
- Do not turn a class-X call or scheduled-wait budget into an elapsed-time
  bound.
- Do not answer a WP-3, WP-4, WP-5, WP-6 or WP-7 question.
- Do not prepare a WP-3 prompt or estimate WP-7 effort.
- Do not design an interface, language, parser, static image, proof method,
  evidence plan or equivalence disposition.
- Apply the original stop rule. If any accepted function requires a dynamic
  child or cannot be inventoried without changing accepted behavior, return a
  precise `HARD STOP`; do not propose SCDC or create a BC-3 exception.

## Checks

Allowed checks are repository-only reads and searches, link/path checks,
`wc -l -c`, `sha256sum`, mechanical parsing of Markdown tables,
`git diff --check` and read-only Git status/diff.

Do not run application or hook suites, builds, formatters or linters. They are
outside this authority and cannot prove this documentation-only remediation.

The durable handback must report:

- all three findings and exactly how each was remediated;
- the complete pre-edit reading ledger required above;
- final deliverable paths, byte counts, line counts and SHA-256 values where a
  non-self-referential value is possible;
- files created and files edited;
- corrected operation, class, tag, step, taxonomy, DI and question counts;
- checks run, their exact scope and exact results, including the final link
  check after every delivered file exists;
- checks not run and why;
- unresolved later-package questions;
- confirmation that no prohibited action occurred; and
- reviewer focus for the independent re-review.

## Prohibited operations

Do not use SSH or connect to any host. Do not access retained evidence,
secrets, credentials, player data, production, staging, `oracle-test`, Foundry
or a database. Do not perform network research, fact collection, package
operations, installation, implementation, configuration/infrastructure edits,
launcher work, builds, tests, formatters, service/database operations, cleanup,
workspace recreation, OH-S4/OH-S4p or later work, H-1/H-2, activation,
rollback, commit or push.

The R5 and H-0G retained paths remain untouched pending separately gated LC-3
through LC-5 authority.

## Return and terminal state

Before replacing the four current-state pointers, preserve their exact R3-
authorization-state text in dated snapshots and index the SHA-256 of each.

On successful completion the pointers and handback must say:

`WP-2 R3 REMEDIATION RETURNED — INDEPENDENT RE-REVIEW PENDING`

They must preserve baseline v1.8, F-1, EX-1/EX-2, the no-host restriction and
the separate WP-3 through WP-7 gates. Otherwise return `HARD STOP` with the
precise reason and make the terminal pointers consistent with it.

The terminal return does not accept WP-2, authorize WP-3, establish concrete
Route 3 or select LIT-FULL for implementation. A clean independent Codex
re-review and Peter's later acceptance are required before any WP-3 prompt or
authority may be prepared.
