# D2-R2 zero-ret and independent-decoding acceptance — 2026-10-01

Decision ID: `C-P5.0-R5-RP11-I1-R3-R4-D2-R2-A1`

Peter Duscha accepts Claude's documentation-only
`C-P5.0-R5-RP11-I1-R3-R4-D2-R2` remediation on Codex's independent
recommendation. Codex found no new Blocking or Important issue in the amended
design. Blocking finding `R4-D2-R1-1` is **Closed as remediated at the design
level**: XD is specified as an independently implemented decoder of the image's
`.text`, T-L11 requires its exact agreement with the committed listing before
any T-L10 result is accepted, and reproducibility is not claimed as decoder
evidence.

Peter decides **LD-9 option (i)**. At D9-2, Codex must independently decode the
actual `.text` using its own decoder or a byte-by-byte manual derivation
prepared from the architecture manuals without reading XD's table. Codex's
instruction starts, lengths, mnemonics, operands and targets must agree with
XD and the committed listing. An independent exercise of XD without that
separate decoding is not sufficient.

This acceptance also confirms the D2-R2 application of the already-decided
LD-7 and LD-8 conditions: the selected image is zero-`ret` from the first
build; IC-1 must pass; R-5 must actually vary and record at least one of
HA-1 … HA-3; every unexplained difference is a hard stop; and diverse double
compilation is not required.

This is design acceptance only. It does not implement or authorize the
launcher, XD, T-L11, T-L12, a build, binary inspection, D9-2 evidence, host
work or an operational pass. PO-9 and PO-14 remain open; RP-11 remains unwired
and unmet; neither pass is executable or authorized; `plan.is_executable=False`;
P5.0-R5 remains Blocking; OD-62 G-A remains conditional; and Package 5.0
remains not ready. A separate M-14/I-7 implementation assignment is required.

No compiler, assembler, linker, decoder, verifier, test, SSH, synchronization,
host inspection, database operation, controlled write, manifest regeneration,
commit or push occurred in recording this decision.
