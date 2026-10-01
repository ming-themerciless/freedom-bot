# R4-D2-R1 independent re-review and maintainer decisions — 2026-09-30

Review ID: `C-P5.0-R5-RP11-I1-R3-R4-D2-R1-REV1`

Reviewer: Codex, Independent Reviewer

Decision authority: Peter Duscha, Product Owner and Acceptance Authority

## Review disposition

The D2-R1 remediation materially addresses the three findings that caused the
remediation:

* `R4-D2-1` is remediated as originally framed. CT-1 … CT-9, RI-1 … RI-7,
  T-L10 and HR-1 … HR-6 now account for `ret`, stack integrity and every stated
  control-transfer class.
* `R4-D2-2` is remediated. The proposal binds the build root, traces the named
  build and evidence tools, and states HA-1 … HA-5 as residual inputs instead
  of claiming that reproducibility removes them.
* `R4-D2-3` is remediated. HX-3 is bounded below the stated `execve` limits,
  EN-1 … EN-3 distinguish entry from driver failure, and the refusal cases
  have exact diagnostic and exit sequences.

One new load-bearing finding remains:

### `R4-D2-R1-1` — Blocking — instruction decoding is an unstated trusted input

T-L7 proves that the byte fields printed in the committed listing concatenate
to `.text`, while T-L10 reasons over the listing's already-decoded mnemonics
and instruction boundaries. Neither check independently decodes the machine
code. A common decoding error in the pinned `objdump` can therefore survive
T-L7, T-L10, same-tool reproduction and R-5 while affecting RI-2, BI-6, BI-10,
P-3 and P-4. That contradicts §5.3.1's statement that the toolchain is trusted
for identity but not correctness.

The correction must do one of the following, in preference order:

1. independently decode `.text` with a separately implemented decoder and
   require exact agreement with the committed listing;
2. record a complete independent manual byte-level decode of the image as
   D9-2 evidence; or
3. name disassembler decoding correctness as a load-bearing trusted assumption
   and obtain explicit maintainer risk acceptance.

The first option is recommended. The independent decoder is review tooling,
not a build input, and its implementation and evidence require independent
review. No finding is closed by the remediation author. PO-9 remains open.

## Maintainer decisions

Peter Duscha accepts the review recommendations and decides:

1. **LD-7 — require FA-2's zero-`ret` image from the start.** The initial
   implementation must contain no `ret`. The narrower T-L8 claim is accepted;
   T-L8 remains source/compiler behavioural evidence and does not replace
   inspection of the installed image. Permitting `ret` later requires a new,
   separately reviewed decision.
2. **LD-8 — accept the bound build root plus named residual inputs HA-1 …
   HA-5, conditionally.** IC-1 must pass; R-5 must actually vary at least one
   of HA-1 … HA-3 and record which input varied; every unexplained difference
   remains a hard stop; and `R4-D2-R1-1` must be resolved independently of
   reproducibility. A diverse double compilation is not required for PO-9.
3. **Archive authorization.** Create verbatim, hash-indexed snapshots of the
   displaced canonical Handover and status files as a separate
   documentation-only step, then keep their canonical files concise.

These decisions select design requirements only. They authorize documentation
updates and archive bookkeeping, not source, build scripts, dependencies,
toolchain acquisition, compilation, tests, binary inspection, manifest or
artifact regeneration, host work, installation, wiring or either operational
pass.

## Gate state and next action

`R4-D2-R1-1` is Open, Blocking. Claude may perform one bounded
documentation-only D2-R2 remediation that makes the zero-`ret` selection and
independent-decoding obligation normative throughout the proposal, records the
dependent evidence changes, and returns for independent Codex re-review.

PO-9 and PO-14 remain open. RP-11 remains unwired and unmet; neither pass is
executable or authorized; `plan.is_executable=False`; P5.0-R5 remains
Blocking; OD-62 G-A remains conditional; and Package 5.0 remains not ready.

References:

* [D2-R1 proposal](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md)
* [D2-R1 assignment](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r1-static-launcher-design-remediation-claude-prompt.md)
* [D2-R1 handback](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r1-static-launcher-design-remediation-handback.md)
