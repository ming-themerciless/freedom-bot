# Independent re-review — LIT-FULL WP-1 R4 remediation

Date: 2026-10-08

Reviewer: Codex, Independent Reviewer

Reviewed work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP1-R4-20261008-13`

Reviewed deliverables:

- [R4 remediation proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-proposal.md)
- [R4 remediation handback](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-handback.md)
- [R3 pointer-archive erratum](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-pointer-archive-erratum.md)
- [Consumed R4 prompt](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-claude-prompt.md)
- [Consumed R4 authority](project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-authority.md)

## Recommendation

**Changes requested. Do not accept WP-1 or authorize WP-2.**

The two substantive Blocking findings assigned to R4 are repaired: the post-B2-N
process-tree result is unambiguous, and the compact gate requires every applicable
governance closure and design prerequisite across all sixteen combinations. The
missing R3 snapshot is also recorded honestly without fabricated bytes. The R4
return nevertheless repeats the archival-control failure for the R4-authorization
pointers themselves and carries one stale checklist assertion.

### WP1-R4R-1 — Important — the R4 return again replaced current-state text without dated, indexed snapshots

The handback states that the return overwrote all four R4-authorization pointers,
created no archive snapshot, and kept their verbatim text only in Appendix A. It
expressly says Appendix A is not an archive snapshot and is not indexed, then leaves
creation of compliant snapshots as something for the controller to decide.

That does not satisfy implementation-plan §16.3 or the repository's current-state
archive convention. It also contradicts the new erratum's own forward control:
current-state text **must** be snapshotted and indexed before replacement, and a
prompt may not prohibit that governing obligation. The prompt restriction therefore
was a conflict to resolve before replacement, not a reason to defer the archive again.

Unlike the R3 gap, the R4-authorization bytes remain recoverable: Appendix A records
the two whole files and the exact §20 and restriction-banner blocks with byte counts
and SHA-256 digests. Under explicit remediation authority, create dated snapshots in
the four canonical archive locations, verify them against Appendix A, and add one
accurate entry to each archive index. Do this before another current-state transition.

### WP1-R4R-2 — Optional — RC-16 is stale in the cumulative checklist

Proposal §14 carries RC-16 as “Only the proposal, the handback and the four pointers
changed.” The R4 handback correctly records three created files and eight changed
files, including the archival erratum and four archive indexes. A cumulative R5
proposal should remove RC-16 as no longer applicable or replace it with an exact R5
scope assertion; it must not present the old R1 file set as the R4/R5 result.

## Checks and evidence

- The R4 prompt matches its authority pin: 12,936 bytes, 245 lines, SHA-256
  `218040bc5bc5ee34e27cb1e1eeaceb66443992f25ebb30629a2053ae7c473620`.
- The R4 proposal matches the handback pin: 1,542 lines, 133,795 bytes, SHA-256
  `00e15e5cb5e8575d829d7f1fd8ae93d273fd43f536f53308b5a07926c24d8737`.
- The erratum matches the handback pin: 151 lines, 10,162 bytes, SHA-256
  `eca8aff5fd18b5f2eb3c58684345b5472cca34cff90d33faa74637af57d2df4e`.
- Table A, PT-1 through PT-5, §12.2 and the sixteen worked rows consistently state
  that an in-set B2-S act begins at B2-N's loader-free path with no `sudo`, while an
  out act remains wholly outside under EX-3.
- §0.2 step 5, U6 and §10.3 consistently require steps 1–3 plus every applicable
  item among steps 4 and 4′.
- The four archive indexes contain the R3 erratum and R3-return snapshots, but no
  dated snapshot of the superseded R4-authorization pointers.

No host, retained-evidence, network, secret, service, database, package, build,
test, formatter, implementation, activation, rollback, commit or push operation
was performed for this review.

This review accepts nothing, decides neither BQ-2 nor BQ-3, opens no §0.2 change,
and authorizes no successor implementation. Independent Codex re-review remains
required after remediation before Peter can accept WP-1.
