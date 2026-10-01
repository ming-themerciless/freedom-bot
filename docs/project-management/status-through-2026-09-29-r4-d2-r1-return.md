# Project status

This is the concise current operational-status entry point. The complete
pre-decision state is preserved verbatim in
[`status-through-2026-09-29-r4-d1-r2-review.md`](status-through-2026-09-29-r4-d1-r2-review.md).

## Current status — LB-2S static-launcher design D2-R1 remediation returned for Codex re-review — 2026-09-29

Codex's review of the D2 design found one Blocking finding (`R4-D2-1`, the
PO-9 control-flow proof ignored `ret`) and two Important ones (`R4-D2-2`,
build-input closure; `R4-D2-3`, `execve` limits and the HX-5 diagnostic).
Claude returned `C-P5.0-R5-RP11-I1-R3-R4-D2-R1` documentation-only and
stopped. The amended proposal retains D-S1, with three corrections:

* a return-integrity discipline and a listing verifier for PO-9;
* a bound build root with named residual host inputs; and
* a hostile experiment with bounded vectors and exact expected traces.

No finding is claimed closed. Codex re-reviews; Peter Duscha then decides.

- [Amended design proposal](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md)
- [D2-R1 remediation handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r1-static-launcher-design-remediation-handback.md)
- [D2-R1 assignment](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r1-static-launcher-design-remediation-claude-prompt.md)

No runtime or toolchain is accepted. PO-9 and PO-14 remain open. No
implementation, compilation, host or operational authority exists. RP-11
remains unwired and unmet; `plan.is_executable=False`; P5.0-R5 remains
Blocking; OD-62 G-A remains conditional; and Package 5.0 remains not ready.

## Superseded current status — LB-2S static-launcher design returned for Codex review — 2026-09-29

Claude returned `C-P5.0-R5-RP11-I1-R3-R4-D2` documentation-only and stopped.
The proposal selects `D-S1`, a freestanding, syscall-only C image with an
assembly entry stub and no C library, and specifies how PO-9 would be proved
from the built binary. Nothing was built, and PO-9 and PO-14 remain open.
Codex reviews independently; Peter Duscha then decides.

- [Design proposal](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md)
- [Design handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-handback.md)

No runtime or toolchain is accepted. No implementation, compilation, host or
operational authority exists. RP-11 remains unwired and unmet;
`plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; and Package 5.0 remains not ready.

## Superseded current status — LB-2S static-launcher design assigned — 2026-09-29

Peter Duscha accepted Codex's R2 review with no finding, accepted M-14 for a
design pass, conditionally selected LB-2S under M-9, and retained T-A with the
explicit R-10 trust under M-10. T-B remains out of scope.

Claude is assigned `C-P5.0-R5-RP11-I1-R3-R4-D2`, documentation-only, to design
the static first image, reproducible toolchain and PO-9 evidence. Codex reviews
independently before any implementation decision.

- [Decision record](../review/project-review-2026-09-29-p5-r5-rp11-r4-d1-r2-launch-boundary-decision.md)
- [Claude design assignment](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-claude-prompt.md)
- [Codex R2 review](../review/project-review-2026-09-29-p5-r5-rp11-r4-d1-r2-system-manager-environment.md)

No runtime or toolchain is accepted. PO-9 and PO-14 remain open. No
implementation, compilation, host or operational authority exists. RP-11
remains unwired and unmet; `plan.is_executable=False`; P5.0-R5 remains
Blocking; OD-62 G-A remains conditional; and Package 5.0 remains not ready.

## Records and archives

- [Pre-decision status snapshot](status-through-2026-09-29-r4-d1-r2-review.md)
- [Status archive index](status-archive/README.md)
