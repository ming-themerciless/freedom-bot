# Claude assignment — LIT-FULL WP-2 R4 focused cumulative remediation

Date: 2026-10-09

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP2-R4-20261009-18`

Executor: Claude, once, under the bounded authority recorded in
`docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r4-remediation-acceptance-and-claude-activation.md`

## Objective

Correct the cumulative WP-2 operation inventory for exactly the two Important
findings in the independent R3 re-review:

- `WP2-R3-1` — two inventory statements present a withdrawn start-timeout
  formula as current; and
- `WP2-R3-2` — the roster names the material `RT-3.SN` child-contract sub-role,
  but the per-procedure tables contain no corresponding row.

Produce a corrected, cumulative, self-contained WP-2 operation inventory that
replaces the R3 inventory as the proposed WP-2 result. This assignment does not
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
25. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r3-remediation-claude-prompt.md`;
26. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r3-remediation-acceptance-and-claude-activation.md`;
27. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r3-remediation-handback.md`;
28. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r3.md`;
29. this exact prompt; and
30. `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r4-remediation-acceptance-and-claude-activation.md`.

The accepted one-host design, cumulative R8 remediation, accepted WP-1 R6
record, EX-1/EX-2 approval and the cleanly closed R2 findings remain governing.
Earlier superseded rounds remain comparison evidence only.

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
- Q6-6 and Q6-7 remain unanswered, including the BS-4 and AM-0 gaps; and
- concrete Route 3 remains unestablished.

Do not reopen or alter any of these items. Preserve the R3 correction that
limits SN-10 / A-I-16 to AK-1, BS-2 and BS-3 while retaining BS-4 as the third
DI-4 call site with the extension question open under Q6-7.

## Deliverables

1. Correct in place, cumulatively:
   `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md`.
2. Create the complete terminal handback:
   `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r4-remediation-handback.md`.
3. At terminal return, preserve the then-current four R4-authorization pointers
   in dated, verbatim `lit-full-wp2-r4-authorization` snapshots beside their
   canonical files, add their SHA-256 values to the four archive indexes, then
   update only:
   - `docs/review/Handover information`;
   - `docs/project-management/status.md`;
   - implementation-plan §20; and
   - the restriction banner in
     `docs/operations/disposable-test-server.md`.

Do not edit an earlier handback, independent review, prompt, activation record,
accepted proposal/acceptance record or historical snapshot.

## Required remediation — `WP2-R3-1`

The accepted R8 proposal §7.7 W-7 expressly withdraws the earlier
`T_s ≥ ⌈(P + c)/1,000⌉ + 30` rule. R8 §7.6 N1 is the current necessary sizing
condition: `T_s · 1,000 ≥ W_show + W_series + ρ`, with `W_show = c + g` and
`W_series = P + c + g`.

1. Remove the unsupported/current-condition wording `≥ ⌈P/1000⌉ + 30` from
   `RT1.FI.2` and the §11.1 `T_s` row.
2. Preserve that `T_s` is the capture unit's loaded finite
   `TimeoutStartUSec`, is PID 1's class-M deadline and must satisfy N1.
3. Do not reinstate W-7, invent a replacement margin or convert N1 into an
   elapsed-time guarantee. Preserve that N1 is a necessary condition only and
   CP's elapsed time is not claimed.
4. Search the complete inventory for every statement of the withdrawn or
   unsupported formula and reconcile any dependent summary, source citation,
   acceptance-checklist or handback statement.

## Required remediation — `WP2-R3-2`

The original R1 inventory requirements demand rows per procedure and material
sub-role. The roster names `RT-3.SN (child contract)`, but §5.3 has no
procedure-specific row.

1. Add `RT3.SN.1` to §5.3, grounded only in accepted text and parallel in
   structure to the other procedure-specific SN rows.
2. State the stop-post child surface in the same two tiers as §8.1:
   - accepted today: its DI-1 unit-state-read children and the DI-5 `pkcheck`
     and DI-6 subject children of CL-4;
   - LIT-FULL replacement: only the DI-6 subject intent remains; DI-1 and DI-5
     children are removed.
3. State that H-SN governs any child that exists and preserve the accepted
   stop-post-specific recovery ownership: after stop-post ends or is
   interrupted, the backstop's CL is the next owner if armed and spawnable,
   otherwise a later CP, then the boot, then `attest`. Derive the exact row
   language from the accepted R8 owner table and existing RT-3 interruption
   rows; invent no new owner, signal, wait, result or guarantee.
4. Reconcile §3, §§4–5, §8.1, §11 row/class/tag and identifier-citation counts,
   §13, §14, §15 and every closed-coverage statement affected by the added row.
   The total row count must increase if and only if the delivered tables do.
5. Do not tag the row with Q6-6 or Q6-7 unless accepted text independently
   requires it. RT-3 performs neither DI-3 nor DI-4.

## Cumulative integrity requirements

- Preserve all fifteen original R1 operation-inventory requirements and every
  unaffected R2/R3 correction.
- Revalidate the complete cumulative inventory, not only the changed lines.
- Every operation row must trace to accepted text; every mechanical count must
  be re-derivable from the delivered tables.
- Preserve all accepted operations, source citations, failure contracts,
  interruption states, residuals, unknown states and deferred questions not
  touched by these two findings.
- A signal attempt is never proof of exit; a missing record is never proof of
  absence; no class-X call or scheduled-wait budget becomes an elapsed bound.
- Do not answer a WP-3, WP-4, WP-5, WP-6 or WP-7 question; prepare a WP-3
  prompt; estimate WP-7; or design an interface, language, parser, static
  image, proof method, evidence plan or equivalence disposition.
- Apply the original stop rule. If any accepted function requires a dynamic
  child or cannot be inventoried without changing accepted behavior, return a
  precise `HARD STOP`; do not propose SCDC or create a BC-3 exception.
- Report any newly discovered conflict or omission. Do not silently repair a
  matter outside `WP2-R3-1` and `WP2-R3-2`.

## Checks and terminal evidence

Allowed checks are repository-only reads and searches, link/path checks,
`wc -l -c`, `sha256sum`, mechanical parsing of Markdown tables,
`git diff --check` and read-only Git status/diff.

Do not run application or hook suites, builds, formatters or linters. They are
outside this authority and cannot prove this documentation-only remediation.

The durable handback must report:

- both findings and exactly how each was remediated;
- the complete 30-item pre-edit reading ledger;
- final deliverable paths, byte counts, line counts and SHA-256 values where a
  non-self-referential value is possible;
- files created and edited;
- corrected row, class, tag, step, taxonomy, DI, identifier-citation and
  question counts, including the exact effect of `RT3.SN.1`;
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
R4-authorization-state text in the required snapshots and index each SHA-256.

On successful completion the pointers and handback must say:

`WP-2 R4 REMEDIATION RETURNED — INDEPENDENT RE-REVIEW PENDING`

They must preserve baseline v1.8, F-1, EX-1/EX-2, the no-host restriction and
the separate WP-3 through WP-7 gates. Otherwise return `HARD STOP` with the
precise reason and make the terminal pointers consistent with it.

The terminal return does not accept WP-2, authorize WP-3, establish concrete
Route 3 or select LIT-FULL for implementation. A clean independent Codex
re-review and Peter's later acceptance are required before any WP-3 prompt or
authority may be prepared.
