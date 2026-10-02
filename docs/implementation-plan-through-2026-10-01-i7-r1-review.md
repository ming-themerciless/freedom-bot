# Superseded implementation-plan §20 — I-7-R1 independent re-review

Verbatim §20 current-action text immediately before Peter Duscha accepted the
I-7-R1 remediation on 2026-10-01:

## 20. Immediate next actions

**Current action, 2026-10-01 — Codex independently re-reviews Claude's
returned I-7-R1 remediation of the Blocking IC-1 exact-environment finding
([review](review/project-review-2026-10-01-p5-r5-rp11-i7-static-launcher-implementation.md),
[prompt](review/phase-5-0-p5-r5-rp11-i1-r3-r4-i7-r1-ic1-environment-remediation-claude-prompt.md),
[handback](review/phase-5-0-p5-r5-rp11-i1-r3-r4-i7-r1-ic1-environment-remediation-handback.md)).
Claude has stopped. Peter Duscha alone accepts it.**

Peter Duscha authorizes `C-P5.0-R5-RP11-I1-R3-R4-I7`
([implementation prompt](review/phase-5-0-p5-r5-rp11-i1-r3-r4-i7-static-launcher-implementation-claude-prompt.md))
under the accepted D2-R2 design
([amended proposal](review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md),
[handback](review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r2-zero-ret-decoding-remediation-handback.md),
[acceptance](review/project-review-2026-10-01-p5-r5-rp11-r4-d2-r2-acceptance.md)).
The zero-`ret` image is the selected design, with no `call` and no `ret`. An
independently implemented decoder, XD, must decode `.text` from the image
bytes and agree exactly with the committed listing before any T-L10 result
is accepted. LD-8's conditions are normative. `R4-D2-R1-1` is Closed as
remediated at the design level. LD-9 option (i) requires Codex to independently
decode the actual `.text` at D9-2 using its own decoder or byte-by-byte manual
derivation prepared without reading XD's table; exercising XD alone is not
sufficient.

Narrow repository remediation, isolated toolchain acquisition where required,
local build/verifier work and repository tests are authorized. R-5 remains
independent; Codex has performed XD-9 and XD-11 for the unchanged image. No test-server,
installation, H-1/H-2, PO-14, RP-11 wiring or operational authority exists.
PO-9 and PO-14 remain open; RP-11 remains unwired and unmet; P5.0-R5 remains
Blocking; `plan.is_executable=False`; Package 5.0 remains not ready.

Historical immediate-action text is preserved in [`implementation-plan-through-2026-10-01-d2-r2-acceptance.md`](implementation-plan-through-2026-10-01-d2-r2-acceptance.md) and indexed under [`implementation-plan-archive/`](implementation-plan-archive/README.md).
