# Project status

This is the concise current operational-status entry point. The complete
pre-cleanup state is preserved verbatim in
[`status-through-2026-10-01-d2-r2-acceptance.md`](status-through-2026-10-01-d2-r2-acceptance.md).

## Current status — I-7-R1 IC-1 environment remediation returned for re-review — 2026-10-01

Claude implemented the accepted I-7 repository slice and returned it
([handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-i7-static-launcher-implementation-handback.md)):
the zero-`ret` launcher, pinned build boundary, XD, T-L1 … T-L12, IC-1,
R-1 … R-4, repository tests and manifest version 27. R-5 remains an independent
party's step. Codex's independent review passed the launcher bytes, XD-9 and
XD-11 but found IC-1's environment comparison under-constrained
([review](../review/project-review-2026-10-01-p5-r5-rp11-i7-static-launcher-implementation.md)).
Peter Duscha accepted the recommendations: D-1 is accepted and Claude was
assigned the narrow I-7-R1 exact-environment remediation
([prompt](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-i7-r1-ic1-environment-remediation-claude-prompt.md)).
Claude returned it and has stopped
([handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-i7-r1-ic1-environment-remediation-handback.md)).
IC-1 now compares every traced process's complete environment with a
specified one. A fresh pinned-root IC-1 passes at the R-2 and R-4(a)
checkouts with outputs byte-identical to R-2. The frozen image, listing and
XD digests are unchanged, and the manifest is version 28. Codex re-reviews
next. D-2 remains unaccepted until then.

- [Amended D2 proposal](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md)
- [D2-R2 handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r2-zero-ret-decoding-remediation-handback.md)
- [Acceptance and LD-9 decision](../review/project-review-2026-10-01-p5-r5-rp11-r4-d2-r2-acceptance.md)
- [I-7 implementation prompt](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-i7-static-launcher-implementation-claude-prompt.md)
- [I-7 implementation handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-i7-static-launcher-implementation-handback.md)

Repository implementation and local evidence generation are authorized only
as the prompt states. No test-server, installation or operational authority
exists. PO-9 and PO-14 remain open; RP-11 remains unwired and unmet;
`plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; and Package 5.0 remains not ready.

## Records and archives

- [Pre-cleanup status snapshot](status-through-2026-10-01-d2-r2-acceptance.md)
- [Status archive index](status-archive/README.md)
