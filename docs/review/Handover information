# Active handover — D2-R2 design accepted; implementation authority pending — 2026-10-01

This is the concise active assignment and restriction entry point. The complete
pre-decision state is preserved verbatim in
[`Handover-information-through-2026-09-29-r4-d2-r1-return.md`](Handover-information-through-2026-09-29-r4-d2-r1-return.md).

## Accepted decisions

Peter Duscha accepted Codex's D2-R1 recommendations:

* **LD-7:** require FA-2's zero-`ret` image from the start. Permitting `ret`
  later requires a separate reviewed decision.
* **LD-8:** accept the bound build root plus HA-1 … HA-5, provided IC-1 passes,
  R-5 actually varies and records at least one of HA-1 … HA-3, unexplained
  differences stop, and the independent-decoding finding is resolved.
* archive the displaced Handover and status text as verbatim, hash-indexed
  snapshots.
* **LD-9:** require Codex to independently decode the actual `.text` at D9-2
  using its own decoder or byte-by-byte manual derivation prepared without
  reading XD's table. An independent exercise of XD alone is not sufficient.

- [Independent review and decision record](project-review-2026-09-30-p5-r5-rp11-r4-d2-r1-decisions.md)
- [D2-R2 acceptance and LD-9 decision](project-review-2026-10-01-p5-r5-rp11-r4-d2-r2-acceptance.md)

## Completed assignment

Claude is assigned a bounded, documentation-only D2-R2 remediation. Amend the
D2 proposal so LD-7's zero-`ret` form is normative from the first build, remove
the conditional recommendation to permit `ret`, and add an independent
machine-code decoder whose result must agree exactly with the committed
listing before T-L10 evidence is accepted. Trace the affected BI, RI, P, D9,
T-L and trust statements together. Create a remediation handback and stop for
independent Codex re-review.

- [D2-R2 remediation assignment](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r2-zero-ret-decoding-remediation-claude-prompt.md)

The assignment is complete and accepted at the design level. Do not implement
the launcher or decoder. Do not build, compile, inspect a
binary, acquire a toolchain, run a verifier or test, regenerate a manifest or
artifact, or amend prior assignments, handbacks, reviews, decisions, snapshots
or archives.

## Return state

Claude returned `C-P5.0-R5-RP11-I1-R3-R4-D2-R2` documentation-only and has
stopped. The D2 proposal is amended in place with a dated §0-D2R2 note and
Appendix D:

* the zero-`ret` form is the selected design: two functions, `_start`
  entering `rp11_main` by one `jmp`, no `call` and no `ret`, the selection
  functions inlined from `select.h`, and T-L8 narrowed as LD-7 accepts;
* a second, independently implemented decoder, XD (§5.15, XD-1 … XD-11),
  decodes `.text` from the image bytes and must agree exactly with the
  listing (T-L11) before any T-L10 result is accepted; Codex independently
  decodes the actual `.text` at D9-2; and
* LD-8's conditions are normative, and reproducibility is not claimed to show
  decoder correctness.

Codex independently re-reviewed the remediation with no new Blocking or
Important issue. Peter accepted it and decided LD-9 option (i).

- [Amended D2 proposal](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md)
- [D2-R2 remediation handback](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r2-zero-ret-decoding-remediation-handback.md)

## Return gate and restrictions

`R4-D2-R1-1` is Closed as remediated at the design level. A separate M-14/I-7
assignment is required before implementation. PO-9 and PO-14 remain open.

**Documentation and repository reads only. No source, build, test, dependency,
binary, manifest, generated artifact, configuration, host or operational
change is authorized. No compilation, installation, download, SSH, rsync,
network or host inspection, `sudo`, database access, provisioning, controlled
write, reboot, verifier, evidence band, harness `--execute`, real participant,
real capture root, operational path, protected-artifact access, secrets scan,
commit or push is authorized.**

RP-11 remains unwired and unmet; neither pass is executable or authorized;
`plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; and Package 5.0 remains not ready.

## Archives

- [D2-R1 return snapshot](Handover-information-through-2026-09-29-r4-d2-r1-return.md)
- [Handover archive index](handover-archive/README.md)
