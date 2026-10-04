## 20. Immediate next actions

**Current action, 2026-10-02 — Peter Duscha accepted Claude's fresh-assignment
R2 remediation on Codex's independent recommendation. `FRESH-A1-R2-1` is
Closed as remediated, and the fresh R-5 assignment at SHA-256
`f5b4c4e935817e7a68df3c8d1b6f8cc78617e0db6622a86a45ea38c1f0c18f94`
is accepted as the execution procedure. No independent executor has been
named, so the procedure is unassigned and not executable. The next controlled
step is a separate activation record naming an eligible executor and
confirming the execution work ID and handback filename. Until then, no fresh
execution authority exists
([acceptance](review/project-review-2026-10-02-p5-r5-rp11-fresh-assignment-r2-acceptance.md)).**

R4 recovery found no historical artifact and created no fixture. R4-R1 bounded
the search claims and corrected the unavailable byte length; Codex found no
remaining Blocking or Important issue, and Peter accepted the corrected result
([decision](review/project-review-2026-10-01-p5-r5-rp11-r4-r1-acceptance-and-reference-reproduction-decision.md)).
Reference reproduction B1/B1-R1 produced the 5,120-byte `cc1.v.baseline` fixture
matching expected SHA-256 `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`
under kernel `6.8.0-139-generic`, CPU `AMD EPYC-Milan Processor`, and `bubblewrap 0.9.0`.

R-5 history: the returned rebuild matched the four frozen outputs across HA-1 …
HA-3 variation, but was not accepted because one-invocation R-1/R-2 gating was
absent and `cc1.v` changed without explanation. Gemini's R2 remediation
introduced the same-invocation R-1/R-2 gate and withdrew the erroneous R-5
PASS
([handback](review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r2-orchestration-remediation-handback.md)).
R3 removed the unsafe causal regex override, so byte equality is the only route
to `PASS`
([handback](review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r3-cc1-comparison-remediation-handback.md)).
Codex independently reproduced 4,019 passing repository tests, with 12
toolchain-dependent skips because no accepted local root was available, plus
clean compilation, byte-range checks and `git diff --check`; Peter Duscha
accepted R3
([acceptance](review/project-review-2026-10-01-p5-r5-rp11-r5-r3-acceptance.md)).

Gemini's first R-5 attempt stopped before provisioning because `bubblewrap` was
absent. Peter narrowly authorized the exact `apt-get update` and `apt-get
install -y bubblewrap` operations, after which Gemini resumed with wholly fresh
disposable directories, corrected Important finding `R5-R1-1`, wrote the
amended handback and stopped
([review](review/project-review-2026-10-01-p5-r5-rp11-r5-bwrap-stop.md),
[authority](review/project-review-2026-10-01-p5-r5-rp11-r5-bwrap-install-authority.md)).

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

`I7-R1-1` is Closed as remediated and D-2 is accepted as implemented. R-5
must actually vary and record at least one of HA-1 … HA-3, and every
unexplained difference is a hard stop. Codex has performed XD-9 and XD-11 for
the unchanged image. No fresh R-5 run is authorized until an executor is
named, and no installation, H-1/H-2, PO-14, RP-11 wiring or operational
authority exists. R-5 remains stopped, Blocking and unaccepted as evidence;
PO-9 and PO-14 remain open; RP-11 remains unwired and
unmet; P5.0-R5 remains Blocking; `plan.is_executable=False`; Package 5.0
remains not ready.

The immediately superseded §20 text is preserved in [`implementation-plan-through-2026-10-02-fresh-r5-assignment-r2-acceptance.md`](implementation-plan-through-2026-10-02-fresh-r5-assignment-r2-acceptance.md); earlier snapshots are indexed under [`implementation-plan-archive/`](implementation-plan-archive/README.md).
