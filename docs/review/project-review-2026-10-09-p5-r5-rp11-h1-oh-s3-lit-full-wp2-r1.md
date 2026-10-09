# Independent review — LIT-FULL WP-2 R1 operation inventory

Date: 2026-10-09

Reviewer: Codex, Independent Reviewer

Reviewed work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP2-R1-20261009-15`

Reviewed deliverables:

- [operation inventory](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md);
- [handback](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-handback.md);
- [accepted R1 prompt](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r1-claude-prompt.md); and
- [acceptance and Claude activation](project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r1-acceptance-and-claude-activation.md).

## Recommendation

**Do not accept WP-2 yet. Remediation and independent re-review are required.**

The return has one Blocking and one Important finding. The inventory's hashes,
317 operation-row total, class totals, four authorization-snapshot digests and
archive-index entries reconcile, and the fixed F-1 boundary is preserved. The
findings concern the semantic authority of one operation row and the closed
DI/child reconciliation that WP-3 would otherwise consume.

This review does not accept WP-2, authorize remediation, authorize WP-3, establish
concrete Route 3 or select LIT-FULL for implementation. Peter Duscha retains the
acceptance and assignment decisions. WP-3 through WP-7 remain gated.

## Findings

### WP2-R1-1 — Blocking — AM-0 inventory selects an unresolved behavior

Inventory row `RT2.AM0.7` requires AM-0 to list the activation-record directory
and enforce AP-0's “no unterminated activation” condition. It labels that
requirement mechanically derived. The same inventory later records, in Q6-7,
that whether AM-0 repeats that AP-0 condition is an accepted-text gap that must
be restated or confirmed later.

Those two positions cannot both stand. A mechanically derived row may not choose
the affirmative answer to a question the inventory says is unresolved. Doing so
also conflicts with the assignment's requirements that every row trace to
accepted text without adding behavior and that later-package questions remain
unanswered. Because the row changes a fail-closed activation precondition and
could become an implementation input, this is a procedure-correctness and
production-reliability issue.

**Required remediation:** make the cumulative inventory consistent without
deciding the gap. Either cite accepted governing text that unambiguously requires
the AM-0 check and remove the question, or leave the behavior unresolved and
represent only the accepted operation/intention that can be stated without
choosing an answer. Reconcile the row tag, step trace, question map, counts and
handback accordingly.

Evidence: inventory row `RT2.AM0.7` and Q6-7; accepted one-host design
§4.2.5-R2(d), whose AM-0 wording says to re-check AP-0's `boot_id`, `/run` and
absence conditions while AP-0 separately names the no-unterminated-activation
condition.

### WP2-R1-2 — Important — DI-4 and child-surface reconciliation is internally inconsistent

The LIT-FULL replacement classification correctly says DI-3 and DI-4 dynamic
children are removed and only a loader-free interaction intent remains. The
per-procedure child rows do not consistently carry that boundary:

- `RT2.SN.1` calls DI-3 a “mutating child” after defining the holder's children
  as DI-6 subjects and their waits;
- `RT4.SN.1` includes the DI-4 call among children created, signalled, reaped or
  abandoned through H-SN, while §8 classifies that child as removed; and
- §7.1 reports two RT-4 DI-4 rows and §7.2 lists only `RT4.BS2.2` and
  `RT4.BS4.2`, although `RT4.BS3.1` is a third accepted disarm call site (it
  delegates to the `RT4.BS2.2` operation). Section 8 does name BS-2, BS-3 and
  BS-4, so the reconciliation tables disagree with one another rather than
  documenting an accepted absence.

This leaves WP-3 unable to tell from the claimed closed tables whether H-SN is
part of the replacement contract for DI-3/DI-4 or only historical behavior that
Q6-6 must map to the in-process/interface outcome. It also makes the assertion
that every required DI cell and operation is reconciled unreliable.

**Required remediation:** distinguish today's accepted dynamic-child behavior
from the LIT-FULL replacement child set in the RT-2/RT-4 SN rows; keep the
accepted `effect: "unknown"` obligation without representing removed DI-3/DI-4
children as remaining H-SN children; and reconcile BS-3 consistently in §§7.1,
7.2, 8, 11.3(c), the checklist and handback counts/claims. State whether §7.1
counts logical call sites, operation rows or composition rows and apply that
definition consistently.

Evidence: inventory rows `RT2.AK1.2`, `RT2.SN.1`, `RT4.BS2.2`, `RT4.BS3.1`,
`RT4.BS4.2`, `RT4.SN.1`; inventory §§7.1, 7.2 and 8 PC-4/PC-5; accepted R8
§§7.3, 7.5a, 9.3 and 9.5.

## Verified evidence

- The accepted prompt is 207 lines, 11,016 bytes and SHA-256
  `6737e231e8237805a6517d006240321c4c4fb7aa14b1923aaa2b3a80cb2f6510`.
- The inventory is 1,291 lines, 189,687 bytes and SHA-256
  `d86431759ad9c23f48acabdf7f663a8a6eddca21751e30cec07c8dea28e36c0a`.
- The handback is 102 lines, 9,987 bytes and SHA-256
  `e324f18aa3ad3550bd1a02c1c1b12d414f40cc95e55e9e81315c99e7e62a099f`.
- Independent parsing of the operation tables found 317 rows and reproduced
  every class total reported in inventory §11.2.
- The four `lit-full-wp2-r1-authorization` snapshots exist; their SHA-256
  values match the handback and all four archive indexes.
- The current return pointers preserve baseline v1.8, F-1, EX-1/EX-2, the
  no-host restriction and the separate WP-3 through WP-7 gates.
- `git diff --check` reported no whitespace errors before this review record
  and current-state transition were written.

## Checks not run and boundary

No host, retained-evidence, network, secret, service, database, package, build,
test, formatter, implementation, activation, rollback, commit or push operation
was performed. Application and hook suites were not run: the active restriction
forbids them, and they would not establish the correctness of this documentation-
only inventory.

The no-host restriction remains unchanged. The R5 and H-0G retained paths remain
untouched pending separately gated LC-3 through LC-5 authority.

## Required next gate

WP-2 remains unaccepted. A separately authorized cumulative remediation must
close `WP2-R1-1` and `WP2-R1-2`, preserve all unaffected accepted content and
current restrictions, and return for independent re-review. No WP-3 prompt may
be prepared and no WP-3 through WP-7 work may begin before that clean re-review
and Peter's later acceptance.
