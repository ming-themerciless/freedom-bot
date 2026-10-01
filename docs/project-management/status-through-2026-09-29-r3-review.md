# Project status

This file is the current operational status entry point. Historical status is
preserved verbatim in
[`status-through-2026-09-28.md`](status-through-2026-09-28.md) and
[`status-through-2026-09-28-d2-doc1.md`](status-through-2026-09-28-d2-doc1.md).
The decision register, RAID register, change log and dedicated review records
remain the authoritative durable records for their subjects.

## Current status — Posix post-open descriptor remediation reviewed; acceptance pending — 2026-09-29

Peter Duscha accepted **Option 1** for the RP-11 unadmitted staging/final pair.
The exception is metadata-only and applies exclusively to the two names Pass
A's final state records for one unadmitted regular file. Both names must be
present, share one inode at link count two and share it with no third name.
The verifier never opens, reads, digests or admits the object. Every broader,
missing, mismatched or ambiguous alias state stops fail closed.

Codex independently re-reviewed the descriptor-release remediation with no new
Blocking or Important finding, then aligned the documentation with the
decision under `C-P5.0-R5-RP11-I1-R3-D2-DOC1`. Its review manifest moved to
version 25 at review-input digest
`f63cf3596a95701e3c24813f5362955dcdb5524e7b4fcaf749159db66f91cdb8`.

Claude reviewed that return, and on Peter Duscha's instruction corrected it under
`C-P5.0-R5-RP11-I1-R3-D2-DOC1-R1`:

* it restored the historical decision proposal byte-for-byte (`ac504ce1…`) and
  recorded an erratum instead;
* it corrected the draft's amendment attribution, stale-pin list and B0-RA
  unresolved clause; the draft is now SHA-256
  `5c6046fc3dc0b9a931cc32076233b1ea9185dc14c5d0ea1abc193687dcca7de6`;
* it restored three Open findings to the current state.

No covered source changed, so manifest version 25 and `f63cf359…` are
unchanged and reproduce byte-identically by dry run. The whole package is
**3348 passed, 0 skipped** at both the 1024 and default descriptor limits.
Codex independently reviewed these exact bytes with no finding and reproduced
the whole-package results. Peter Duscha accepted the review on 2026-09-29.

**Findings.** `RP11-I1-R3-1`, `RP11-I1-R3-2` and `RP11-I1-R3-3` are Closed.
`RP11-I1-2` (Blocking), `RP11-I1-R2-1` (Blocking) and `RP11-I1-R1-1`
(Important) are **Closed as superseded** by the accepted I1-R3 design.

This does **not** accept or wire RP-11. RP-11 remains unmet; C-11 and
the pinned launcher environment remain unresolved; neither pass is executable
or authorized; P5.0-R5 remains Blocking; OD-62 G-A remains conditional;
`plan.is_executable=False`; and Package 5.0 remains not ready. No host,
database, operational-pass, commit or push authority is created.

**Returned for review.** Claude returned `C-P5.0-R5-RP11-I1-R3-R3`, the
bounded repository-only correction of the post-open descriptor leaks in
`PosixFilesystem.create_file` and `openat`, and stopped
([handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r3-posix-post-open-release-handback.md)). The whole package is **3364 passed, 0 skipped**
at both the 1024 and default descriptor limits. Manifest version 26, digest
`526dd44648833ecb5b7bc5de111478323bf6b44c3ea076916896ba883c7f2f28`, is review
input only. Codex independently reviews; Peter Duscha decides.

**Independent review complete.** Codex found no Blocking, Important or Optional
issue and recommends acceptance. It independently reproduced the 16 focused
tests, both **3364 passed, 0 skipped** whole-package runs and the byte-identical
version-26 dry-run artifacts at digest `526dd446…`. Peter Duscha decides.

## Records and archives

- [Decision and independent-review record](../review/project-review-2026-09-28-p5-r5-rp11-i1-r3-r2-and-unadmitted-pair-decision.md)
- [Alignment review acceptance](../review/project-review-2026-09-29-p5-r5-rp11-option-1-alignment-acceptance.md)
- [R3 Claude assignment](../review/phase-5-0-p5-r5-rp11-i1-r3-r3-posix-post-open-release-claude-prompt.md)
- [R3 Codex review](../review/project-review-2026-09-29-p5-r5-rp11-i1-r3-r3-posix-post-open-release.md)
- [D2-DOC1-R1 correction handback](../review/phase-5-0-p5-r5-rp11-i1-r3-d2-doc1-r1-alignment-review-remediation-handback.md)
- [Option-1 documentation-alignment handback](../review/phase-5-0-p5-r5-rp11-i1-r3-d2-option-1-documentation-alignment-handback.md)
- [R2 remediation handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r2-lifecycle-descriptor-release-remediation-handback.md)
- [Option-1 decision proposal](../review/phase-5-0-p5-r5-rp11-i1-r3-r1-unadmitted-pair-decision-proposal.md)
- [Status history through 2026-09-28](status-through-2026-09-28.md)
- [Status at the D2-DOC1 return](status-through-2026-09-28-d2-doc1.md)
- [Status archive index](status-archive/README.md)
