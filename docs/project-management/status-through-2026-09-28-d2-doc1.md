# Project status

This file is the current operational status entry point. Historical status
through 2026-09-28 is preserved verbatim in
[`status-through-2026-09-28.md`](status-through-2026-09-28.md). The decision
register, RAID register, change log and dedicated review records remain the
authoritative durable records for their subjects.

## Current status — RP-11 Option 1 accepted; exact-byte acceptance still pending — 2026-09-28

Peter Duscha accepted **Option 1** for the RP-11 unadmitted staging/final pair.
The exception is metadata-only and applies exclusively to the two names Pass
A's final state records for one unadmitted regular file. Both names must be
present, share one inode at link count two and share it with no third name.
The verifier never opens, reads, digests or admits the object. Every broader,
missing, mismatched or ambiguous alias state stops fail closed.

Codex independently re-reviewed the descriptor-release remediation with no new
Blocking or Important finding. Local review reproduced:

* focused descriptor regressions: **12 passed, 0 skipped**;
* `tests/phase_5_0_evidence` at soft descriptor limit 1024:
  **3348 passed, 0 skipped**;
* the same package at the default limit: **3348 passed, 0 skipped**; and
* deterministic dry-run artifacts at manifest version 24, digest
  `bccd26e59aa94a64dc8888eb6265c68da7d4c8c7d1705d85932e5ebad01a05d7`.

`RP11-I1-R3-1`, `RP11-I1-R3-2` and `RP11-I1-R3-3` are Closed. Documentation
alignment moved the review manifest to version 25 at review-input digest
`f63cf3596a95701e3c24813f5362955dcdb5524e7b4fcaf749159db66f91cdb8`;
the amended operational draft is SHA-256 `48bef661714c72393d61487470f0ee3619b32ea6d0f126b26dbe43742ca44ce2`.
Focused RP-11/structural verification is **774 passed, 0 skipped**. The whole
package is **3348 passed, 0 skipped** at both the 1024 and default descriptor
limits. The generated artifacts reproduce byte-identically. These exact bytes
now require independent review and maintainer acceptance.

This decision does **not** accept or wire RP-11. RP-11 remains unmet; C-11 and
the pinned launcher environment remain unresolved; neither pass is executable
or authorized; P5.0-R5 remains Blocking; OD-62 G-A remains conditional;
`plan.is_executable=False`; and Package 5.0 remains not ready. No host,
database, operational-pass, commit or push authority is created.

## Records and archives

- [Decision and independent-review record](../review/project-review-2026-09-28-p5-r5-rp11-i1-r3-r2-and-unadmitted-pair-decision.md)
- [Option-1 documentation-alignment handback](../review/phase-5-0-p5-r5-rp11-i1-r3-d2-option-1-documentation-alignment-handback.md)
- [R2 remediation handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r2-lifecycle-descriptor-release-remediation-handback.md)
- [Option-1 decision proposal](../review/phase-5-0-p5-r5-rp11-i1-r3-r1-unadmitted-pair-decision-proposal.md)
- [Status history through 2026-09-28](status-through-2026-09-28.md)
- [Status archive index](status-archive/README.md)
