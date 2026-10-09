# Accepted Claude prompt — LIT-FULL WP-2 R2 remediation

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP2-R2-20261009-16`

Status: **accepted, assigned to Claude and executable once**

## Authority and objective

Peter Duscha authorizes Claude to remediate only the two findings in the
independent WP-2 R1 review:

- `WP2-R1-1` — the operation inventory selects an AM-0 behavior that it also
  records as unresolved; and
- `WP2-R1-2` — the DI-3/DI-4 child surface and DI-4 call-site reconciliation
  are internally inconsistent.

Produce a corrected, cumulative WP-2 operation inventory that remains
self-contained and replaces the R1 inventory as the proposed WP-2 result. This
assignment does not accept WP-2, authorize WP-3, establish concrete Route 3 or
select LIT-FULL for implementation.

## Required reading

Before editing, read completely, first byte through EOF:

1. `.agents/AGENTS.md`;
2. the reading map and §§0, 16 and 20 of `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. the restriction banner in
   `docs/operations/disposable-test-server.md`;
5. the accepted R1 prompt
   `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r1-claude-prompt.md`;
6. every source required by that R1 prompt, items 5 through 15, completely;
7. the R1 inventory
   `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md`;
8. the R1 handback
   `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-handback.md`;
9. the independent review
   `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r1.md`;
10. this exact prompt and its acceptance/activation record.

The accepted one-host design, cumulative R8 remediation, accepted WP-1 R6
record and EX-1/EX-2 approval remain the governing sources. Earlier superseded
proposal rounds remain comparison evidence only.

## Fixed boundary

Preserve the accepted R1 boundary without reinterpretation:

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
   `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r2-remediation-handback.md`.
3. At terminal return, preserve the then-current four authorization pointers
   in dated, verbatim snapshots beside their canonical files, add their
   SHA-256 values to the four archive indexes, then update only:
   - `docs/review/Handover information`;
   - `docs/project-management/status.md`;
   - implementation-plan §20; and
   - the restriction banner in
     `docs/operations/disposable-test-server.md`.

Do not edit the R1 handback, the independent review, this prompt, its authority
record, an accepted proposal/acceptance record or any earlier snapshot.

## Required remediation — `WP2-R1-1`

The remediation must not decide whether AM-0 repeats AP-0's
“no unterminated activation” condition. That question remains Q6-7 unless a
later separately authorized decision resolves it.

In the cumulative inventory:

1. Remove the affirmative system-call-intent requirement currently stated by
   `RT2.AM0.7`, or replace it only with a non-operative gap statement that
   cannot be consumed as an instruction to list records or enforce the check.
2. Do not characterize the affirmative behavior as mechanically derived.
3. Preserve the accepted AM-0 operations that are unambiguous.
4. Keep Q6-7 explicit and unanswered, with WP-6 as owner under the accepted
   package allocation.
5. Reconcile the RT-2 AM0 step trace, operation-row totals, class totals, tag
   totals, question-to-row counts, coverage tables, acceptance checklist and
   handback. Do not preserve 317 merely as a target; report the count produced
   by the corrected tables.
6. State plainly that WP-2 has not selected either answer to the gap.

If accepted governing text genuinely resolves the question, do not silently
apply that reading. Return `HARD STOP` with the exact competing passages,
because this remediation is authorized to preserve the question, not make a
new procedure decision.

## Required remediation — `WP2-R1-2`

Separate accepted-today child behavior from the LIT-FULL replacement surface.

1. Correct `RT2.SN.1` and `RT4.SN.1` so they do not represent removed DI-3 or
   DI-4 distribution-program children as children that necessarily remain in
   the LIT-FULL root-procedure tree.
2. Preserve the accepted SN-10 / A-I-16 obligation that a mutating operation's
   effect may be `unknown` after an error, interruption or indeterminate
   completion. Carry its mapping to a non-child loader-free interaction as the
   unanswered Q6-6 obligation; do not invent the mapping.
3. Do not choose whether WP-3/WP-4 ultimately realizes a loader-free
   interaction in process, by a static child or by another admitted mechanism.
   If a later design chooses a child, BQ-4 still requires (F) or (X), never a
   distribution executable, and the applicable child contract must then be
   mapped by that later package.
4. Define §7.1's unit of counting as **logical accepted call sites**. For
   DI-4, reconcile all three conditional disarm sites: BS-2, BS-3 and BS-4's
   terminal disarm. A shared operation row may implement more than one call
   site, but the call-site table and row list must say so explicitly.
5. Reconcile §§7.1, 7.2, 8, 11.3(c), 11.5, 12 Q6-6, 13, 14 and every affected
   operation/step row. No closed-coverage claim may rely on a different unit
   of counting from the table it summarizes.
6. Re-run the document's mechanical closure checks against the delivered
   cumulative bytes and report their exact results. Recompute every affected
   count rather than editing totals by hand.

## Integrity and scope requirements

- Preserve every unaffected accepted operation, source citation, failure
  contract, interruption state, residual, unknown state and deferred question.
- Preserve all fifteen original operation-inventory requirements from the R1
  prompt. This is a remediation, not a reduced inventory.
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
`wc -l -c`, `sha256sum`, mechanical parsing of the Markdown tables,
`git diff --check` and read-only Git status/diff.

Do not run application or hook suites, builds, formatters or linters. They are
outside this authority and cannot prove this documentation-only remediation.

The handback must report:

- both findings and exactly how each was remediated;
- the final deliverable paths, byte counts, line counts and SHA-256 values;
- files created and files edited;
- the corrected operation, class, tag, step, taxonomy, DI and question counts;
- checks run and exact results;
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

Before replacing the four current-state pointers, preserve their exact
authorization-state text in dated snapshots and index the SHA-256 of each.

On successful completion the pointers and handback must say:

`WP-2 R2 REMEDIATION RETURNED — INDEPENDENT RE-REVIEW PENDING`

They must preserve baseline v1.8, F-1, EX-1/EX-2, the no-host restriction and
the separate WP-3 through WP-7 gates. Otherwise return `HARD STOP` with the
precise reason and make the terminal pointers consistent with it.

The terminal return does not accept WP-2, authorize WP-3, establish concrete
Route 3 or select LIT-FULL for implementation. A clean independent Codex
re-review and Peter's later acceptance are required before any WP-3 prompt or
authority may be prepared.
