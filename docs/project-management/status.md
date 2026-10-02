# Project status

This is the concise current operational-status entry point. The complete
superseded R2-assignment state is preserved verbatim in
[`status-through-2026-10-01-r5-r3-acceptance.md`](status-through-2026-10-01-r5-r3-acceptance.md).

## Current status — baseline contract accepted; fresh R-5 decision pending — 2026-10-02

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
XD digests are unchanged, and the manifest is version 28. Codex independently
found no Blocking, Important or Optional issue. Peter Duscha accepted the
remediation: `I7-R1-1` is Closed as remediated and D-2 is accepted as
implemented.

- [Amended D2 proposal](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md)
- [D2-R2 handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r2-zero-ret-decoding-remediation-handback.md)
- [Acceptance and LD-9 decision](../review/project-review-2026-10-01-p5-r5-rp11-r4-d2-r2-acceptance.md)
- [I-7 implementation prompt](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-i7-static-launcher-implementation-claude-prompt.md)
- [I-7 implementation handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-i7-static-launcher-implementation-handback.md)
- [I-7-R1 acceptance](../review/project-review-2026-10-01-p5-r5-rp11-i7-r1-acceptance.md)
- [I-7-R1 independent re-review](../review/project-review-2026-10-01-p5-r5-rp11-i7-r1-ic1-environment-remediation.md)

Peter accepted the Antigravity-reviewed
[R-5 assignment](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-independent-rebuild-assignment.md)
and named Gemini as the independent assignee
([review](../review/project-review-2026-10-01-p5-r5-rp11-r5-assignment-antigravity.md),
[acceptance](../review/project-review-2026-10-01-p5-r5-rp11-r5-assignment-acceptance.md)).
That assignment covered only one bounded run, which has since stopped; it
created no installation or operational authority. PO-9 and PO-14 remain open;
RP-11 remains unwired and unmet;
`plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; and Package 5.0 remains not ready.

The first R-5 attempt stopped before provisioning because `bubblewrap` was
absent. Codex confirmed the dependency and raised Important finding `R5-R1-1`
against a contradictory cleanup claim. Peter narrowly authorized Gemini to
install Ubuntu's `bubblewrap` package, record it, resume with wholly fresh
disposable directories, correct the handback and stop
([review](../review/project-review-2026-10-01-p5-r5-rp11-r5-bwrap-stop.md),
[authority](../review/project-review-2026-10-01-p5-r5-rp11-r5-bwrap-install-authority.md)).

The resumed run reproduced the frozen outputs with all three HA dimensions
varied, but R-5 is not accepted: the required same-invocation R-1/R-2 gate did
not run, and `cc1.v` changed without an exact explanation. The initial returned
handback also misstated the pinned snapshot date. Gemini's repository-only R2
remediation corrected that date, introduced the same-invocation R-1/R-2 manifest
gate and withdrew the erroneous R-5 PASS
([prompt](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r2-orchestration-remediation-gemini-prompt.md),
[handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r2-orchestration-remediation-handback.md)).
Codex's review then required R3: Gemini removed the unsafe causal regex
override from `cc1check.py`, so byte equality is the only route to `PASS`
([prompt](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r3-cc1-comparison-remediation-gemini-prompt.md),
[handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r3-cc1-comparison-remediation-handback.md)).
Codex independently reproduced 4,019 passing repository tests, with 12
toolchain-dependent skips because no accepted local root was available, plus
clean compilation, byte-range checks and `git diff --check`. Peter Duscha
accepted R3 on that recommendation
([acceptance](../review/project-review-2026-10-01-p5-r5-rp11-r5-r3-acceptance.md)).

Gemini's R4 bounded recovery ended in Branch B: no historical artifact was
recovered and no fixture was created. Codex found two record-accuracy defects;
Gemini corrected them in R4-R1, Codex found no remaining Blocking or Important
issue, and Peter accepted the correction and Branch B.

**Current action.** Peter Duscha accepted B1-R4 and the corrected B1-R3 record
on Codex's independent recommendation. `B1-R3-1` and `B1-R3-2` are Closed as
remediated. Manifest version 30 and aggregate digest
`28a4f4c2b7596e9042f6b12a34f5684b3499a3fafd997e306fe25f6798e8a526`
are the accepted baseline-contract review input. The diagnostic fixture remains
exactly 5,120 bytes with SHA-256 `b77f92dc…905b`; it is not a normative launcher
output. [Acceptance decision](../review/project-review-2026-10-02-p5-r5-rp11-b1-r4-acceptance.md).

The next controlled step is a newly prepared, independently reviewed and
explicitly accepted R-5 assignment. No fresh execution authority exists.

R-5 remains stopped, Blocking and unaccepted. RP-11 remains unwired and unmet;
`plan.is_executable=False`; and Package 5.0 remains not ready.

## Records and archives

- [Superseded B1-R3/B1-R4 current-action block](status-through-2026-10-02-r5-b1-r4-acceptance.md)
- [Superseded B1 current-action block](status-through-2026-10-01-r5-b1-reference-reproduction.md)
- [Superseded R4 current-action block](status-through-2026-10-01-r5-r4-branch-b.md)
- [Superseded R2-assignment snapshot](status-through-2026-10-01-r5-r3-acceptance.md)
- [Status archive index](status-archive/README.md)
