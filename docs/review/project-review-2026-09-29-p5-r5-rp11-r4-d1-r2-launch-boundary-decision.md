# R4-D1-R2 launch-boundary decision — 2026-09-29

Decision ID: `C-P5.0-R5-RP11-I1-R3-R4-D1-R2-A1`

Peter Duscha accepts Codex review
`C-P5.0-R5-RP11-I1-R3-R4-D1-R2-REV1` and decides:

1. **M-14 — accepted for design work only.** Commission a bounded design for
   a compiled static first image, including its runtime or language, pinned
   toolchain, reproducible build, installed-digest binding and PO-9 evidence.
2. **M-9 — LB-2S selected conditionally.** LB-2S is preferred only if the
   M-14 design is accepted and PO-9 and PO-14 are later discharged. If either
   fails, LB-2S is withdrawn rather than weakened.
3. **M-10 — T-A remains in scope.** Ambient manager environment must be
   prevented from reaching the entry. Manager execution settings are trusted
   as reviewed, root-controlled host input under R-10 and H-1/H-2. T-B remains
   out of scope for this package.

The rationale is that a static first image is the only identified boundary
capable of constructing a closed environment before Python's loader runs;
LB-2S also keeps client-derived process state away. LB-1 retains client
execution state, LB-2T is review rather than prevention, and LB-3 remains
dependent on open PAM/default inputs and inherited client state.

This closes only M-14's design authorization and the conditional M-9/M-10
direction. It does not choose a runtime or toolchain, establish PO-9 or PO-14,
accept D-1 or D-2, choose MD-C11, authorize implementation or host work, wire
RP-11, or make either pass executable.

RP-11 remains unwired and unmet; `plan.is_executable=False`; P5.0-R5 remains
Blocking; OD-62 G-A remains conditional; and Package 5.0 remains not ready.

References:

* [R2 proposal](phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md)
* [R2 handback](phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r2-system-manager-environment-remediation-handback.md)
* [Codex R2 review](project-review-2026-09-29-p5-r5-rp11-r4-d1-r2-system-manager-environment.md)
