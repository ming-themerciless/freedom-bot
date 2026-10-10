# Independent re-review — LIT-FULL WP-3 R1 remediation

Date: 2026-10-10

Reviewer: Codex, Independent Reviewer

Reviewed work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP3-R1-20261010-22`

Reviewed deliverables:

- [R1-corrected cumulative interface contract](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-interface-contract.md);
- [R1 remediation handback](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-r1-remediation-handback.md);
- [accepted R1 remediation prompt](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-r1-remediation-claude-prompt.md);
- [R1 acceptance and Claude activation](project-review-2026-10-10-p5-r5-rp11-h1-oh-s3-lit-full-wp3-r1-remediation-acceptance-and-claude-activation.md); and
- [independent review that raised WP3-HS-R1 and WP3-HS-R2](project-review-2026-10-10-p5-r5-rp11-h1-oh-s3-lit-full-wp3-hard-stop.md).

## Recommendation

**No findings. Accept the R1 remediation and the WP-3 HARD STOP return as
complete evidence of the authorized WP-3 execution.**

This recommendation closes the two documentation findings only. It does not
close Q3-1 through Q3-7 or Q3-9, authorize WP-4 through WP-7, establish concrete
Route 3, select LIT-FULL for implementation, answer Q6-6 or Q6-7, decide BC-2,
or alter the accepted F-1/EX boundary. Peter Duscha retains the acceptance and
successor-authority decisions.

## Findings

No Blocking, Important or Optional findings.

`WP3-HS-R1` is closed. Section 3.0 now distinguishes cancelling a client wait
from cancelling a manager job, states proposed obligations `PO3-X1` through
`PO3-X3`, and gives an explicit treatment for all seven interfaces. Expanded
`UF-05` registers all four required missing facts for DI-2, DI-3, DI-4 and DI-S:
how a client cancels or abandons its wait, the fate of an accepted or queued job,
observation of the eventual result and effect, and mapping of cancellation,
disconnection and unconfirmed outcomes to the result and unknown-effect
boundaries. The affected interface sections, Q3 table, WP-4 input table,
reconciliation, checklist and stop result consistently carry that gap.

The classification boundary is preserved. SN-10/IS-8 remains an accepted `DR`
only for the historical DI-3 child and the DI-4 children at BS-2 and BS-3; its
mapping to non-child interactions remains Q6-6. DI-2, DI-S and DI-4 at BS-4 use
`PO3` rather than claiming an upstream fact, and the BS-4 extension remains
Q6-7. A cancelled wait is never treated as proof of no mutation or stopped job,
and no silent retry is granted.

DI-6 needs no additional unsupported-fact identifier. It is the authorization
subject conveyed to the enclosing DI-5 decision, not a separate asynchronous
manager job with its own client wait. DI-5 call cancellation remains in `UF-10`;
subject identity remains in `UF-12`/`UF-13`; later subject cleanup remains under
the accepted H-PROC/H-PK2 contract with mechanics deferred to Q4-1 and Q4-8.

The R1 revalidation correction is accurate. WP-2 section 7.1 defines call-site
counting and does not supply the former failure/cancellation sentence. New
citations C-33 and C-34 point instead to the WP-2 carried, unmapped obligation
and to R8 SN-10/IS-8. They do not convert a proposed replacement-interface
mapping into an accepted fact.

`WP3-HS-R2` is closed. The remediation handback quotes the original ambiguity,
does not rewrite the original handback or claim what its executor read, and
unambiguously states that the remediation executor read every one of the 26
listed items as required before the first edit. The new ledger is expressly the
evidence basis for the corrected cumulative contract. Its immutable-file
identities match independently checked repository files; the changed contract's
pre-edit identity matches the prior independent review, and the pre-return
handover snapshot matches the ledger identity.

## Checks and evidence

- The corrected contract matches the handback identity: 469 lines, 50,599
  bytes, SHA-256
  `b766c10f2c28ac2d32a7dc7ee4ab2c92a3cf80d67fd70f345a9f0dd7ba92c888`.
- The accepted R1 prompt and prior review match their recorded SHA-256 values;
  the unchanged original contract handback matches
  `b7a8e3724b5c6e5ac4ca18a2b0c8b5730137e255f317be00d02d1bd84e8b1416`.
- All independently checkable immutable entries in the 26-item reading ledger
  match their recorded SHA-256 values. The R1-authorization handover snapshot
  matches its ledger and archive-index digest.
- The contract contains 34 citation rows and 18 unsupported-fact rows. Its two
  interface tables each cover all seven interfaces, and the accepted call-site
  matrix remains 23 + 1 + 1 + 3 + 6 + 6 + 1 = 41.
- Fixed-string searches reproduce the stated cancellation search evidence:
  none of `CancelJob`, `JobRemoved`, `JobNew`, `GetJob`, `disconnect` or
  `queued job` occurs in R2, R8, the one-host design or WP-2; lower-case
  `cancel` occurs 1/0/3/1 times respectively, with no client-wait or manager-job
  cancellation contract for DI-2, DI-3, DI-4 or DI-S.
- The four R1-authorization snapshot digests appear in their archive indexes.
- `git diff --check` reports no whitespace errors.

No host, retained-evidence, network, secret, service, database, package, build,
application test, hook test, formatter, implementation, activation, rollback,
commit or push operation was performed for this review.

## Remaining gate

The substantive `HARD STOP` remains correct. Q3-1 through Q3-7 and Q3-9 are not
closed, and Q3-11 remains only a fail-closed record. An authorized source must
supply `UF-01` through `UF-18` as applicable before the dependent interfaces
may be built. Q4-1, Q4-7 and Q4-8, Q6-6, Q6-7, the BS-RM citation obligation,
the 109 unclassified run-time-varying names and BC-2 remain with their recorded
later owners.

Peter may accept the R1 remediation and the WP-3 HARD STOP return. That
acceptance does not authorize preparation or execution of WP-4, and it does not
establish concrete Route 3 or select LIT-FULL for implementation.
