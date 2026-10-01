# Project status

This is the concise current operational-status entry point. The complete
pre-decision state is preserved verbatim in
[`status-through-2026-09-29-r4-d2-r1-return.md`](status-through-2026-09-29-r4-d2-r1-return.md).

## Current status — D2-R2 design and LD-9 option (i) accepted — 2026-10-01

Peter Duscha accepted the documentation-only D2-R2 remediation after Codex's
independent review found no new Blocking or Important issue. The selected
design is zero-`ret`; XD independently decodes the image bytes; T-L11 must
agree exactly with the committed listing before T-L10 is evidence; and LD-8's
conditions are normative. `R4-D2-R1-1` is Closed as remediated at the design
level. Under decided LD-9 option (i), Codex must independently decode the
actual `.text` at D9-2; exercising XD alone is not sufficient.

- [Amended D2 proposal](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md)
- [D2-R2 handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r2-zero-ret-decoding-remediation-handback.md)
- [Acceptance and LD-9 decision](../review/project-review-2026-10-01-p5-r5-rp11-r4-d2-r2-acceptance.md)

No implementation, compilation, build, decoder, toolchain, host or operational
authority exists. A separate M-14/I-7 implementation assignment is required.
PO-9 and PO-14 remain open; RP-11 remains unwired and unmet;
`plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; and Package 5.0 remains not ready.

## Superseded current status — zero-ret and independent-decoding remediation required — 2026-09-30

Peter Duscha accepted Codex's D2-R1 recommendations. LD-7 requires a zero-`ret`
image from the first build. LD-8 accepts the bound build root plus HA-1 … HA-5
subject to IC-1, an R-5 run that actually varies at least one of HA-1 … HA-3,
recorded variation, and a hard stop on unexplained differences.

The original three D2 findings are remediated as framed. New Blocking finding
`R4-D2-R1-1` remains Open: T-L7 and T-L10 consume the pinned disassembler's
instruction boundaries without independently decoding `.text`, contrary to
the claim that toolchain correctness is not trusted. D2-R2 must make zero-`ret`
normative and require an independent decoder to agree exactly with the listing,
then return for independent Codex re-review.

- [Independent review and decisions](../review/project-review-2026-09-30-p5-r5-rp11-r4-d2-r1-decisions.md)
- [D2-R1 proposal](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md)
- [D2-R1 handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r1-static-launcher-design-remediation-handback.md)

No implementation, compilation, build, toolchain, host or operational
authority exists. PO-9 and PO-14 remain open; RP-11 remains unwired and unmet;
`plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; and Package 5.0 remains not ready.

## Records and archives

- [D2-R1 return status snapshot](status-through-2026-09-29-r4-d2-r1-return.md)
- [Status archive index](status-archive/README.md)
