# Claude assignment — LIT-FULL WP-2 R5 focused cumulative remediation

Date: 2026-10-09

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP2-R5-20261009-19`

Executor: Claude, once, under the bounded authority recorded in
`docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r5-remediation-acceptance-and-claude-activation.md`

## Objective

Correct the cumulative WP-2 operation inventory for exactly the one Blocking
finding in the independent R4 re-review:

- `WP2-R4-1` — `RT3.SN.1` conflates recovery of the interrupted stop-post
  cleanup with ownership of a child left behind by stop-post, contradicting the
  accepted R8 SN-RO owner table.

Produce a corrected, cumulative, self-contained WP-2 operation inventory that
replaces the R4 inventory as the proposed WP-2 result. This assignment does not
accept WP-2, authorize WP-3, establish concrete Route 3 or select LIT-FULL for
implementation.

## Required reading — binding precondition

Before editing any deliverable or current-state pointer, read every item below
completely, first byte through EOF. A search, excerpt, heading scan, prior read,
summary or tool-generated synopsis does not satisfy this precondition, except
that items 2 and 4 require the expressly named portions.

1. `.agents/AGENTS.md`;
2. the reading map and §§0, 16 and 20 of `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. the restriction banner in `docs/operations/disposable-test-server.md`;
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
25. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r3-remediation-claude-prompt.md`;
26. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r3-remediation-acceptance-and-claude-activation.md`;
27. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r3-remediation-handback.md`;
28. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r3.md`;
29. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r4-remediation-claude-prompt.md`;
30. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r4-remediation-acceptance-and-claude-activation.md`;
31. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r4-remediation-handback.md`;
32. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r4.md`;
33. this exact prompt; and
34. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r5-remediation-acceptance-and-claude-activation.md`.

The accepted one-host design, cumulative R8 remediation, accepted WP-1 R6
record, EX-1/EX-2 approval and every cleanly closed earlier WP-2 finding remain
governing. Earlier superseded rounds remain comparison evidence only.

Before the first edit, record in working notes for every item above its path,
line count, byte count and SHA-256 as read. The terminal handback must include
that complete ledger and state unambiguously that every required item was read
as specified before the first edit. If any required item cannot be read
completely, return `HARD STOP` before changing the inventory.

## Fixed boundary

Preserve without reinterpretation:

- LIT-FULL under R3-ROOT;
- in scope: RT-1 through RT-5, SA-1 (`start`) and SA-2 (`stop`);
- F-1: B2-F; both lifecycle acts in; B3-OUT;
- EX-1 and EX-2 effective, no EX-3;
- no dynamic child beneath a first design-controlled image;
- every retained process creation ultimately classified as a fork continuing
  in a static image or an `execve` of a design-controlled static image;
- H-1, RB-1, RS-1 and H-1R outside the root-procedure set;
- B2-N and a Python-free installer are not prerequisites;
- BC-2 remains a later WP-9 question;
- Q6-6 and Q6-7 remain unanswered, including the BS-4 and AM-0 gaps;
- concrete Route 3 remains unestablished; and
- the R3 BS-4 correction remains effective: SN-10 / A-I-16 apply to AK-1,
  BS-2 and BS-3 only; BS-4 remains the third DI-4 call site under open Q6-7.

Do not reopen or alter any of these items. Preserve `WP2-R3-1` as closed: the
withdrawn `T_s` formula must not return. Preserve the R4 row and step counts
unless the delivered tables actually change.

## Deliverables

1. Correct in place, cumulatively:
   `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md`.
2. Create the complete terminal handback:
   `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r5-remediation-handback.md`.
3. At terminal return, preserve the then-current four R5-authorization pointers
   in dated, verbatim `lit-full-wp2-r5-authorization` snapshots beside their
   canonical files, add their SHA-256 values to the four archive indexes, then
   update only:
   - `docs/review/Handover information`;
   - `docs/project-management/status.md`;
   - implementation-plan §20; and
   - the restriction banner in
     `docs/operations/disposable-test-server.md`.

Do not edit an earlier handback, independent review, prompt, activation record,
accepted proposal/acceptance record or historical snapshot.

## Required remediation — `WP2-R4-1`

The accepted R8 §7.5a.7 SN-RO table defines child ownership by the enclosing
procedure. Stop-post runs in the holder unit's stop-post context. The first
party that can end a child left behind by stop-post is PID 1 through
`FINAL_SIGTERM`, then `FINAL_SIGKILL` after another S, to “what remains”. The
boot is a later, separate recovery event. R8 §7.9 separately states what the
next procedure can know: a missing `run-end` may cause the backstop's CL or
`attest` to record `children-unknown`, but SN-9 forbids hunting or acting on the
child.

The existing RT-3 interruption rows state a different contract: who next
recovers unfinished cleanup and activation state after stop-post is
interrupted. That recovery chain is the backstop's CL if armed and spawnable,
otherwise later CP, boot and `attest`. It must remain in those interruption
rows, but it is not the SN-RO owner of a left-behind child.

Correct exactly this conflation:

1. Revise `RT3.SN.1` while preserving its two-tier child surface:
   - accepted today: DI-1 unit-state-read children and the DI-5 `pkcheck` and
     DI-6 subject children of CL-4;
   - LIT-FULL replacement: only the DI-6 subject intent remains; DI-1 and DI-5
     children are removed.
2. Preserve that H-SN governs any child that exists.
3. Replace “no unit owns it” and the cleanup-recovery chain as child owner with
   the accepted SN-RO owner contract: PID 1's `FINAL_SIGTERM`, then
   `FINAL_SIGKILL` after another S, to “what remains”; then the boot as a
   separate recovery event.
4. Preserve the accepted qualification exactly: “what remains” is established;
   whether it includes a `setsid` child remains the existing PO-SN (e) basis.
   Do not turn that basis into a new guarantee.
5. State the observer contract separately: CS-7, CS-8 and CS-10 have the
   durable child line; for CS-1 through CS-6 and CS-9 the next procedure sees
   only the missing `run-end`; the backstop's CL or `attest` may record
   `children-unknown`, but no later procedure hunts, signals, reaps or acts on
   the child.
6. Preserve the RT-3 cleanup-recovery chain unchanged in `RT3.FI.2` and the
   RT3.CL* interruption rows. Do not describe that chain as child ownership.
7. Reconcile `RT3.SN.1`'s blocking/bound cell with taxonomy row 3f's accepted
   class-M PID 1 signalling, without converting delivery into proof of exit or
   adding an elapsed-time guarantee.
8. Reconcile the R4 revision record, §6, §8.1, §9, §10, §11, §13, §14, §15
   and every summary, checklist, source citation or handback statement affected
   by this correction. Do not change a mechanical count unless the delivered
   tables make it change.

Do not alter the historical R4 prompt. Record in the R5 revision note that its
ownership instruction was superseded because it conflicted with accepted R8.

## Cumulative integrity requirements

- Preserve all fifteen original R1 operation-inventory requirements and every
  unaffected R2, R3 and R4 correction.
- Revalidate the complete cumulative inventory, not only the changed row.
- Every operation row must trace to accepted text; every mechanical count must
  be re-derivable from the delivered tables.
- Preserve every accepted operation, source citation, failure contract,
  interruption state, residual, unknown state and deferred question not
  touched by `WP2-R4-1`.
- A signal attempt is never proof of exit; a missing record is never proof of
  absence; no class-X call or scheduled-wait budget becomes an elapsed bound.
- The boot is a separate recovery event and is not evidence of a send, exit or
  reap. A later observer never searches for or acts on a left-behind child.
- Do not answer a WP-3, WP-4, WP-5, WP-6 or WP-7 question; prepare a WP-3
  prompt; estimate WP-7; or design an interface, language, parser, static
  image, proof method, evidence plan or equivalence disposition.
- Apply the original stop rule. If any accepted function requires a dynamic
  child or cannot be inventoried without changing accepted behavior, return a
  precise `HARD STOP`; do not propose SCDC or create a BC-3 exception.
- Report any newly discovered conflict or omission. Do not silently repair a
  matter outside `WP2-R4-1`.

## Checks and terminal evidence

Allowed checks are repository-only reads and searches, link/path checks,
`wc -l -c`, `sha256sum`, mechanical parsing of Markdown tables,
`git diff --check` and read-only Git status/diff.

Do not run application or hook suites, builds, formatters or linters. They are
outside this authority and cannot prove this documentation-only remediation.

The durable handback must report:

- `WP2-R4-1` and exactly how it was remediated;
- the complete 34-item pre-edit reading ledger;
- final deliverable paths, byte counts, line counts and SHA-256 values where a
  non-self-referential value is possible;
- files created and edited;
- final row, class, tag, step, taxonomy, DI, identifier-citation and question
  counts, explicitly stating every effect or non-effect of the correction;
- checks run and exact results;
- checks not run and why;
- unresolved later-package questions;
- confirmation that no prohibited action occurred; and
- reviewer focus for the independent re-review.

For the terminal link check, reserve a non-link-bearing result field in the
handback, run the check after all delivered files exist, populate the field and
rerun the identical check. The handback must contain the final exact file
scope, link count, broken count and exit/result. No link-bearing content may
change after the rerun.

## Prohibited operations

Do not use SSH or connect to any host. Do not access retained evidence,
secrets, credentials, player data, production, staging, `oracle-test`, Foundry
or a database. Do not perform network research, fact collection, package
operations, installation, implementation, configuration/infrastructure edits,
launcher work, builds, tests, formatters, service/database operations, cleanup,
workspace recreation, OH-S4/OH-S4p or later work, H-1/H-2, WP-3 through WP-7,
activation, rollback, commit or push.

The R5 and H-0G retained paths remain untouched pending separately gated LC-3
through LC-5 authority.

## Return and terminal state

Before replacing the four current-state pointers, preserve their exact
R5-authorization-state text in the required snapshots and index each SHA-256.

On successful completion the pointers and handback must say:

`WP-2 R5 REMEDIATION RETURNED — INDEPENDENT RE-REVIEW PENDING`

They must preserve baseline v1.8, F-1, EX-1/EX-2, the no-host restriction and
the separate WP-3 through WP-7 gates. Otherwise return `HARD STOP` with the
precise reason and make the terminal pointers consistent with it.

The terminal return does not accept WP-2, authorize WP-3, establish concrete
Route 3 or select LIT-FULL for implementation. A clean independent Codex
re-review and Peter's later acceptance are required before any WP-3 prompt or
authority may be prepared.
