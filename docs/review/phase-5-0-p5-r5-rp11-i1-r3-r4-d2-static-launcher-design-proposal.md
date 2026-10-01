# Design proposal — the LB-2S static first image `rp11-launch`

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-D2`

Date: 2026-09-29

Author: Claude, design author

Independent reviewer: Codex

Decision owner: Peter Duscha

Assignment:
[`phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-claude-prompt.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-claude-prompt.md)
(SHA-256 `4a3176dfbdb32eed9aad60e27aeddcfa250879c6c414cde93d88e6aabfea53ba`)

Handback:
[`phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-handback.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-handback.md)

Controlling inputs, read unchanged:

* the R2 proposal
  [`phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md)
  (SHA-256 `f6405cd94a826e7883b80589c1edcd2be1e5b56b4481987d7cacdea96312f70b`),
  cited below as **R2**;
* the R2 handback
  [`phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r2-system-manager-environment-remediation-handback.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r2-system-manager-environment-remediation-handback.md)
  (SHA-256 `da3cc96be5fd9e6a4b839f00f3f5d564a6ccef75bda7a611a0df87df70ce45e3`);
* Codex's R2 review
  [`project-review-2026-09-29-p5-r5-rp11-r4-d1-r2-system-manager-environment.md`](project-review-2026-09-29-p5-r5-rp11-r4-d1-r2-system-manager-environment.md)
  (SHA-256 `f3c20ed7e2ef2bcc544f432ddcd5a0798d6128e2ff7d070473239457c1e5be14`);
  and
* the maintainer decision
  [`project-review-2026-09-29-p5-r5-rp11-r4-d1-r2-launch-boundary-decision.md`](project-review-2026-09-29-p5-r5-rp11-r4-d1-r2-launch-boundary-decision.md)
  (`C-P5.0-R5-RP11-I1-R3-R4-D1-R2-A1`, SHA-256
  `10daa59994f7b78101da446d89f1180350b67ca00690237fae177560de9c3b40`).

Remediation *(D2-R1)*: `C-P5.0-R5-RP11-I1-R3-R4-D2-R1`, assigned by
[`phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r1-static-launcher-design-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r1-static-launcher-design-remediation-claude-prompt.md)
(SHA-256 `57500b5b95822a01c6770368e8352fbefdc6629aba7f5abd82f154d7360ade76`).
The bytes Codex reviewed are the D2 return, SHA-256
`adc114bf795985ce1af5c90e3b9d8e7ca1cb012e1551e6eab590cfb8f28d8093`
(954 lines). This file is amended in place. §0-D2R1 records the amendment and
Appendix C quotes every withdrawn or narrowed claim.

Remediation handback:
[`phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r1-static-launcher-design-remediation-handback.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r1-static-launcher-design-remediation-handback.md)

Remediation *(D2-R2)*: `C-P5.0-R5-RP11-I1-R3-R4-D2-R2`, assigned by
[`phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r2-zero-ret-decoding-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r2-zero-ret-decoding-remediation-claude-prompt.md)
(SHA-256 `7b182696e95c97975d56e3a6f59528a5c3c094e3f75f44b875b48844091c3d15`),
under the decisions LD-7 and LD-8 recorded in
[`project-review-2026-09-30-p5-r5-rp11-r4-d2-r1-decisions.md`](project-review-2026-09-30-p5-r5-rp11-r4-d2-r1-decisions.md)
(SHA-256 `2748a9147e9a83ed5cdaec5552b30ba1cbdfd5866e7612352ad1c4c311f80d70`).
The bytes Codex re-reviewed are the D2-R1 return, SHA-256
`a70f013f77c83f448a03fc08b15b2075aa47efaa09da5e9290af3f1bfc295b81`
(1 774 lines). §0-D2R2 records the amendment and Appendix D quotes every D2-R1
claim it withdraws, narrows or supersedes.

D2-R2 remediation handback:
[`phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r2-zero-ret-decoding-remediation-handback.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r2-zero-ret-decoding-remediation-handback.md)

State: **design accepted, unimplemented. Amended under D2-R1 and D2-R2,
independently re-reviewed by Codex and accepted by Peter Duscha on 2026-10-01.
`R4-D2-R1-1` is Closed as remediated at the design level. LD-9 option (i) is
decided: Codex must independently decode the actual `.text` at D9-2. I-7
repository implementation was assigned on 2026-10-01 under
[`C-P5.0-R5-RP11-I1-R3-R4-I7`](phase-5-0-p5-r5-rp11-i1-r3-r4-i7-static-launcher-implementation-claude-prompt.md).**
Nothing in this document was compiled, built, installed, inspected or
executed. It adds no source, build script, toolchain file, test, binary,
manifest, artifact or configuration. **PO-9 and PO-14 remain open. RP-11
remains unwired and unmet. Neither pass is executable or authorized.
`plan.is_executable=False`. P5.0-R5 remains Blocking. OD-62 G-A remains
conditional. Package 5.0 remains not ready.**

Acceptance:
[`project-review-2026-10-01-p5-r5-rp11-r4-d2-r2-acceptance.md`](project-review-2026-10-01-p5-r5-rp11-r4-d2-r2-acceptance.md)

---

## 0-D2R2. Remediation note — D2-R2, 2026-09-30

Codex's independent re-review of the D2-R1 return (`a70f013f…fc295b81`) found
the three D2 findings remediated as framed and one new finding:

* **`R4-D2-R1-1` (Blocking) — instruction decoding is an unstated trusted
  input.** T-L7 proves that the byte fields printed in the committed listing
  concatenate to `.text`. T-L10 then reasons over the listing's
  already-decoded mnemonics and instruction boundaries. Nothing decodes the
  machine code independently, so a decoding error common to the pinned
  `objdump` survives T-L7, T-L10, same-tool reproduction and R-5, while
  affecting RI-2, BI-6, BI-10, P-3 and P-4. That contradicts §5.3.1's
  statement that the toolchain is trusted for identity and not for
  correctness.

Peter Duscha then decided:

* **LD-7:** FA-2's zero-`ret` image is required from the first build. The
  narrower T-L8 claim is accepted. T-L8 remains source and compiler
  behavioural evidence and does not replace inspection of the installed
  image. Permitting `ret` later requires a new, separately reviewed decision.
* **LD-8:** the bound build root plus HA-1 … HA-5 is accepted, provided that
  IC-1 passes, that R-5 actually varies at least one of HA-1 … HA-3 and
  records which, that every unexplained difference remains a hard stop, and
  that `R4-D2-R1-1` is resolved independently of reproducibility. Diverse
  double compilation is not required.

This amendment applies those decisions and remediates `R4-D2-R1-1` by the
reviewer's first-preference option. **It does not claim `R4-D2-R1-1`
closed.** Only Codex's independent re-review can decide that, and Peter Duscha
remains the decision and acceptance authority.

**Outcome.** D-S1 is retained in its **zero-`ret` form**, which is now the
selected design and not a fallback. The PO-9 control-flow argument no longer
depends on any transfer whose target is read from machine state: the image
contains no `ret` and no `call`. It depends instead on the instruction
boundaries and targets being decoded correctly, and that is now established
by a second, independently implemented decoder whose result must agree
exactly with the committed listing. The retention remains conditional, and
§4.5 gains withdrawal conditions for both changes.

**Zero-`ret` form — what changed (LD-7).**

1. **Call structure** (§5.1, §5.2, §5.14). The image has two functions,
   `_start` and `rp11_main`. `_start` pushes a zero word and enters
   `rp11_main` by one direct `jmp`. The selection functions are
   `static inline __attribute__((always_inline))` definitions in `select.h`,
   included once by `launch.c`, and appear in the image only inlined into
   `rp11_main`. `select.c` as a separate translation unit, and `select.o`, no
   longer exist. The link has two objects.
2. **Transfer set** (§5.14.1). CT-4 is now the single entry `jmp`. CT-5 is
   now **absent**: no `ret` in any form, and no `call` in any form. Every
   other class is unchanged.
3. **Return-integrity rules** (§5.14.2). RI-7's return argument is
   withdrawn, because nothing returns. RI-1 … RI-4 are restated for two
   functions and no `call`. RI-5 and RI-6 are kept, and their purpose is now
   stated as **data** integrity (the frame's literals and the `execve`
   arguments, P-5), not control integrity.
4. **Source discipline** (§5.14.3). SR-1 … SR-6 are restated, and SR-7 and
   SR-8 are added: `start.s` contains no `call` and enters `rp11_main` only by
   `jmp`; `select.h` holds only the two pure inline functions.
5. **Expected listing shape** (§5.14.3). `_start` of about eight
   instructions ending in the `jmp`, and one `rp11_main` containing no
   `call` and no `ret`, whose every exit ends in `ud2`.
6. **T-L8 narrowed** (§5.12.1). It links a freestanding shim compiled from
   the same `select.h` with the image's compile vector. It tests the
   selection source under the pinned compiler, not the image's bytes. The
   exact narrowing is stated there and in §6.3.
7. **Every recommendation that permitted `ret` is withdrawn or superseded**:
   §0 FD-6; §4.3 C-1; §4.4 item 2; §5.1; §5.14; §6.1 P-4 and the closing
   statement; §9 LD-7. Appendix D quotes each. **No return-based alternative
   is preserved.** FA-1 and FA-3 remain as fail-closed alternatives, both
   under the zero-`ret` rules (§5.14.5).

**Independent decoding — what changed (`R4-D2-R1-1`).**

1. **A second decoder, XD, is specified** (§5.15, XD-1 … XD-11). It reads the
   image file itself, not the listing, `objdump` or `readelf`. It decodes the
   whole of `.text` from `_start` under a closed encoding table written from
   the architecture manuals. It emits every instruction's start, length,
   bytes, mnemonic, operands and direct target. It fails on ambiguity, an
   unsupported encoding, an undecoded byte, an overlapping decode, a target
   into an instruction or outside `.text`, an unreached instruction, or any
   disagreement.
2. **Exact agreement is required before T-L10 evidence can be accepted.**
   The new T-L11 compares XD's stream with the committed listing on every
   boundary, byte field, mnemonic, operand and target that T-L10 uses. T-L10
   consumes the agreed stream, and its verdict is accepted only with a
   passing T-L11 over the same image and listing digests.
3. **XD is evidence tooling, not a build input.** It is class E (X-17), is
   independently reviewed, and its version is recorded with each verdict.
   Its self-test corpus is T-L12.
4. **Codex independently decodes the actual `.text` at D9-2** (XD-11), using
   its own decoder or byte-by-byte manual derivation prepared without reading
   XD's table, so that neither binutils nor XD is a common-mode authority.
5. **Traced through** RI-2, BI-6, BI-10, T-L7, T-L10, P-3, P-4, D9-2, §6.3
   and §8, and through the dependent §5.2, §5.3.7, §5.11, §5.12, §6.1, §9,
   §10 and §11 text.
6. **What remains trusted is stated** (§5.15.4, §8): the architecture
   manuals' encoding definitions and the executing CPU's conformance to them
   (AD-14); the absence of a misreading common to XD and Codex's decoding;
   XD's provenance independence from binutils, which is a review fact; and
   the Python interpreters that run the verifiers.

**LD-8 conditions — what changed.** R-5's pass condition now **requires** a
recorded variation of at least one of HA-1 … HA-3 (§5.3.5). IC-1 is a
precondition of accepting the build-root claim (§5.3.7, §5.12.3). An
unexplained difference remains a hard stop. **No diverse double compilation
is required**, and no text claims that reproducibility shows the correctness
of any instruction decoder (§5.3.8, §6.3).

**Section map.**

| Change | Where |
|---|---|
| zero-`ret` form (LD-7) | §0 (result text, FD-6); §4.3 C-1 (source-to-binary and reproducibility cells); §4.4; §4.5; §5.1; §5.2 (file table, build-input boundary); §5.3.3 (vectors, sibling-call rationale); §5.3.5 (R-2 outputs); §5.3.7 (X-8, X-9, IC-1); §5.6 (location note only); §5.10; §5.11; §5.12.1 (T-L1, T-L3, T-L4, T-L8, T-L10); §5.12.2 (BI-6, BI-7, BI-8, BI-10, BI-11); §5.14 (all subsections); §6.1 (claim, P-3, P-4, P-5, closing statement); §6.3; §8; §9 LD-7; §11; Appendix D |
| independent decoding (`R4-D2-R1-1`) | §0; §2.4 (AD-14); §4.4; §4.5; §5.2 (listing, XD and spelling-table rows); §5.3.1; §5.3.3 (closing sentence); §5.3.7 (X-16, **X-17**); §5.3.8; §5.11; §5.12.1 (T-L7, T-L9, T-L10, **T-L11, T-L12**); §5.12.2 (BI-6, BI-10, closing text); §5.14.2 (RI-2, RI-7); §5.14.4; **§5.15 (new)**; §6.1 (P-3, P-4, closing statement); §6.2 D9-2; §6.3; §8; §9 LD-9; §10; §11; Appendix D |
| LD-8 conditions | §4.5; §5.3.5 (R-5, closing paragraph); §5.3.7 (IC-1); §5.3.8 (HA rows, what reproducibility does not show, conditions); §5.12.3; §6.2 D9-3; §6.3 (reproducibility row); §9 LD-8 |

Sections not listed are unchanged. In particular the exact launcher contract
of §5.5 … §5.9, the system-call inventory, the hostile-environment experiment
of §5.12.4 and the refinements V-1 … V-8 are not changed; §5.6 gains only a
note that its function now lives in `select.h`. R2 is not amended.

---

## 0-D2R1. Remediation note — D2-R1, 2026-09-29

*(D2-R2)* This note is kept as the D2-R1 record. Where it says that `ret` is
permitted, that FA-2 is a fallback, or that the complete control-flow graph
rests on the listing's decoding alone, it is **superseded** by §0-D2R2 and
the sections it lists.

Codex's independent review of the D2 return (`adc114bf…f28d8093`) found three
defects, as transmitted in the D2-R1 assignment §1:

* **`R4-D2-1` (Blocking).** PO-9 premise P-4 treated the absence of indirect
  `call` and `jmp` instructions as a complete control-flow proof. It did not
  account for `ret`, or for any other transfer whose target comes from mutable
  machine state.
* **`R4-D2-2` (Important).** The claimed complete build-input closure omitted
  the `/bin/sh` interpreter and the `env` executable that the prescribed build
  runs, together with their runtime inputs.
* **`R4-D2-3` (Important).** The hostile-environment contract included input
  vectors that can exceed the kernel's `execve` limits before `rp11-launch`
  starts. HX-5 also contradicted the normative diagnostic-before-exit
  contract.

This amendment corrects the design text only. **It does not claim any finding
closed.** Only Codex's independent re-review can decide that, and Peter Duscha
remains the decision and acceptance authority.

**Outcome.** D-S1 is **retained**, with a corrected PO-9 argument and a
corrected build and test contract. The retention is conditional in the same
way as before, and it now names one further withdrawal condition: if no
build passes the new control-transfer and stack-write discipline (§5.14)
under any of the fail-closed alternatives FA-1 … FA-3, LB-2S is withdrawn
(§4.5).

**`R4-D2-1` — what changed.**

1. **`ret` is permitted, and only under a stated discipline** (§5.14). The
   image may contain the control-transfer classes CT-1 … CT-9 and nothing
   else. Every direct target must be an instruction start inside a listed
   function. The return-integrity rules RI-1 … RI-7 make each reachable `ret`
   provably return to the instruction after its matching direct `call`. The
   argument has four parts:
   * the stack depth is known statically at every instruction;
   * every memory store other than `push` and `call` is a
     constant-displacement `%rsp` store that lies strictly inside the current
     frame;
   * no system call in the inventory writes user memory as it is used; and
   * no signal handler can exist.
2. **No store address depends on input.** Hostile `argv` and `envp` can change
   loaded values and the outcomes of direct conditional branches. They cannot
   change where anything is written (§5.14.3). The fixed-size
   `INVOCATION_ID` copy is written as 32 constant-index assignments. The
   selection functions return values only, and they have no out-parameters.
3. **Mechanical and human evidence named.** A new toolchain-free verifier,
   T-L10, checks the committed listing against CT and RI. T-L7 ties the
   listing's instruction bytes to the image's `.text`. BI-6 and BI-7 are
   rewritten, and BI-10 and BI-11 are added. The human review HR-1 … HR-6 is
   defined (§5.14.4).
4. **Premises revised.** P-3, P-4 and P-5 and the §6.1 claim now name that
   evidence. New assumptions AD-11 (forced synchronous signals) and AD-12
   (system-call return) are added to the D9-1 citation.
5. **Every "no indirect branch" statement is qualified** (§0 FD-6, §4.3, §4.4,
   §5.3.3, §8). The complete disassembly is no longer equated with a complete
   reachable control-flow graph.
6. **Fail-closed alternatives are stated, not assumed to work** (§5.14.5):
   * FA-1, verified inlining;
   * FA-2, a zero-`ret` image; and
   * FA-3, the C-1A assembly fallback under the same rules.

**`R4-D2-2` — what changed.**

1. **Every executable in R-1 … R-5 is traced** (§5.3.7, table X-1 … X-16).
   That includes the provisioning and entry mechanism, `/usr/bin/env`,
   `/bin/sh` and its target, the compiler driver, `cc1`, the assembler, the
   linker and its automatically loaded plugins, and the inspection, digest and
   verifier tools. Each is classified:
   * **B**, can change the image bytes;
   * **E**, produces committed or digest-bound evidence; or
   * **P**, provisions or enters the environment.
2. **Runtime inputs are named.** These include the dynamic loader, shared
   libraries, loader cache and preload file, `glibc-hwcaps` variants, `gconv`
   modules, BFD plugins, compiler specs and program data.
3. **The closure is bound as a tree, not only as a package list.**
   `build-root.manifest` records every file in the build root. R-1 compares
   the provisioned root with it from inside the entered environment. A later
   input-closure trace, IC-1, checks that the build opens nothing outside it.
4. **The claim is narrowed where it cannot be closed.** The kernel, the CPU,
   and the P-class entry mechanism are **inputs that no lock pins**. They are
   stated as residual host assumptions HA-1 … HA-5 (§5.3.8). R-5 can detect
   byte drift they cause. It does not make them stop being inputs.
5. **R-2, `build_env`, `TMPDIR` and `umask` are reconciled.**
   * R-2 is now an exact vector.
   * The compiler runs with `-S` and assembles through the pinned `as`, so no
     temporary file and no `PATH` lookup occurs.
   * The `TMPDIR` and caller-`umask` variations are **removed from R-4**,
     because `env -i` and `build.sh`'s own `umask 022` stop them reaching the
     build.
   * R-4 now varies only the checkout path, time and source modification
     times, and the build user and host name. §5.3.5 says what each variation
     proves.
   * `-ffile-prefix-map`, which put an absolute path into a supposedly fixed
     flag vector, is removed.

**`R4-D2-3` — what changed.**

1. **Versioned `execve` limits are stated** as AE-1 … AE-5: the per-string
   limit, the aggregate limit and its dependence on `RLIMIT_STACK`, the
   pointer accounting, and the handling of `argc` 0.
2. **HX-3 is split** into HX-3a … HX-3d, with concrete sizes and counts. Every
   vector stays at or below 25 % of the aggregate limit and 75 % of the
   per-string limit. The supervisor computes and asserts both before it calls
   `execve`.
3. **Entering `rp11-launch` is established, not inferred.** Three things must
   agree:
   * an `O_CLOEXEC` pipe distinguishes a failed initial `execve`
     (`DRIVER-EXEC-FAILED`, never a launcher result);
   * the trace must show the entering `execve` returning 0 in the same process;
     and
   * that process's next system calls must match the launcher's golden
     sequence.
4. **HX-5 now requires the `launch-usage` line, then `exit_group(111)`.** HX-4
   and HX-7 are made exact, and HX-7 is split by descriptor. New cases HX-8 and
   HX-9 cover statuses 114 … 117 by fault injection. Every golden sequence
   gives exact bytes and lengths.
5. **Closed or blocked descriptor 2 is specified.** The diagnostic `write` is
   always attempted. When descriptor 2 is usable, its absence, or a short
   result, fails the case (§5.9, §5.12.4).
6. **The experiment stays corroboration.** No record may present it as proof
   of PO-9.

**Section map.**

| Finding | Where it is corrected |
|---|---|
| **`R4-D2-1`** (Blocking) | §0 (result text, FD-6); §2.3 (AD-11, AD-12); §4.3 C-1; §4.4; §4.5; §5.1; §5.2 (`select.c` role); §5.3.3 (flags and rationale); §5.10; §5.12.1 (T-L1, T-L4, T-L7, **T-L10**); §5.12.2 (BI-6, BI-7, **BI-10, BI-11**, closing text); **§5.14 (new)**; §6.1 (claim, P-3, P-4, P-5); §6.2 (D9-1, D9-2); §8; §9 (LD-7); §10; Appendix C |
| **`R4-D2-2`** (Important) | §2.3 (AB-1 … AB-4); §5.2 (file table, build-input boundary); §5.3.1; §5.3.2; §5.3.3; §5.3.4; §5.3.5; §5.3.6; **§5.3.7 and §5.3.8 (new)**; §5.11 (binding chain, manifest content, H-1 record); §5.12.1 (T-L3, T-L6); §5.12.3; §6.2 (D9-3); §6.3 (new row); §8; §9 (LD-8); Appendix C |
| **`R4-D2-3`** (Important) | §2.3 (AE-1 … AE-5, AD-13); §5.5 (`argc` 0); §5.9 (descriptor 2); **§5.12.4 (rewritten)**; §6.3 (hostile-testing row); Appendix C |

Sections not listed are unchanged. In particular these are not changed:

* the exact launcher contract of §5.5 … §5.8, apart from the `argc` 0 note;
* the system-call inventory; and
* the refinements V-1 … V-8.

R2 is not amended.

---

## 0. Result

**A design is selected: `D-S1`, a freestanding, syscall-only image written in
C11 with a hand-written x86-64 entry stub and no C library, runtime, loader or
start-up files** (§4.4, §5). Its PO-9 argument is **structural, not
empirical**. The kernel transfers control directly to the image's own entry
instruction, and no user-space instruction precedes it. Every instruction
after it appears in one reviewed listing of under 4 KiB of code.
*(amended D2-R1, D2-R2)* The listing alone does not make the control-flow
graph complete. That comes from three further things (§5.14, §5.15, §6):

* a closed set of permitted control-transfer classes that contains **no
  `ret` and no `call`**, so every transfer target is encoded in the
  instruction bytes (LD-7);
* instruction boundaries and direct targets decoded by a second,
  independently implemented decoder, XD, that must agree exactly with the
  committed listing; and
* a stack-write discipline that protects the data passed to the kernel.

Each is checked mechanically and by human review.

**This is a recommendation for the launcher design only.** It does not
discharge PO-9. PO-9 is discharged only when the build, binary-inspection,
reproducibility and installation components D9-1 … D9-4 of §6.2 have all been
produced under later, separate authority. It does not touch PO-14. LB-2S
remains conditional exactly as decision `…-R4-D1-R2-A1` states: if PO-9 or
PO-14 later fails, LB-2S is withdrawn, not weakened.

**Why no impossibility result.** Assignment §4 requires one if no candidate
supports a defensible PO-9 proof with an acceptable pinned toolchain. One
candidate does, for a reason that does not depend on trusting its toolchain:

* the pre-entry path is the kernel's ELF loader alone; and
* the complete post-entry behaviour can be read from the binary itself.

The toolchain's acceptability therefore rests on pinning and reproducibility
(§5.3), not on its correctness. §4.5 states the conditions under which this
result would reverse into withdrawal.

**Findings made during the design** (each is load-bearing somewhere below):

| # | Finding | Consequence |
|---|---|---|
| **FD-1** | A launcher that supports both LB-2S (`INVOCATION_ID` present) and LB-1 (`INVOCATION_ID` absent) would let the **environment block choose the image's behaviour**. The block is untrusted T-A input | the image has **one mode**. Without exactly one valid `INVOCATION_ID` it refuses. This diverges from R2 §4.4.2 and the §7.9 LB-1 row (§7, V-5) |
| **FD-2** | C-library signal wrappers refuse implementation-reserved signals: glibc refuses 32 and 33, and musl refuses 32, 33 and 34 (author's understanding, AD-9). A launcher that uses them **cannot** reset every disposition | the reset uses the raw `rt_sigaction` system call for every signal except `SIGKILL` and `SIGSTOP` (§5.7). This alone rules out using a C library's wrappers for the contract |
| **FD-3** | The kernel consults `binfmt_misc` registrations **before** its ELF handler (AD-4). A root-registered handler whose magic matches this image would start an interpreter **before `_start`**, under the unit's open block. A "static" image is not immune | PO-9 is scoped to "the kernel's ELF handler loads the image", and a new trusted-state check, **PO-17**, is added at H-1 and H-2 (§5.11, §8) |
| **FD-4** | A statically linked ELF can still run code before `main`: `.preinit_array`, `.init_array`, `IRELATIVE` (ifunc) relocations, TLS set-up and C-library start-up. **The static label proves nothing** | PO-9 is proved by the **structural absence** of all of them, checked on the built binary (§5.12.2, BI-1 … BI-9; *D2-R1:* BI-1 … BI-11) |
| **FD-5** | Distribution compilers enable code-generating defaults: stack-protector canaries (which read TLS through `%fs`), PIE, CET notes and instrumentation, `_FORTIFY_SOURCE`, build IDs and ISA property notes | each is disabled explicitly (§5.3.3). **The flags are not the evidence.** Binary inspection is, and it fails the build if any default survives |
| **FD-6** *(amended D2-R1, D2-R2)* | Because the image is tiny and contains no indirect `call` or `jmp`, no `call` and no `ret` (LD-7), every transfer target is encoded in the instruction bytes. Its **complete** disassembly is reviewable, and its reachable control-flow graph can be established once its decoding is independently verified. The listing is committed and bound by digest | neither the compiler nor the disassembler is **trusted for correctness**. Reproducibility ties the reviewed listing to the reviewed source (§5.3, §6). XD and T-L11 establish the listing's decoding independently of binutils (§5.15), and T-L10 and HR-1 … HR-6 then establish the control-flow graph (§5.14.4) |
| **FD-7** | R2's contract did not say what happens if descriptor 0, 1 or 2 is closed. A later `open` in the entry could then receive number 1 or 2 and mix evidence streams | a stdio check is added before descriptor closure (§5.7, S-3; V-1) |

---

## 1. Scope

**In scope:** the design of the compiled static first image `rp11-launch`
that LB-2S's unit names in `ExecStart=` (R2 §4.4.3.4), covering the thirteen
items of assignment §3.

**Not in scope, and not changed:**

* the R4-D1-2 command-knowability result (R2 §5.4, §6.6.1, §6.6.2, D-2, M-11);
* the unit text, polkit rule and bootstrap (R2 §4.4.3.4, §9), except where
  §5.11 names a pass-configuration field they already carry;
* `rp11-entry-env/1`'s LB-2S key set and literals (R2 §7.9);
* D-1, D-2, the operational-evidence draft and the R2 proposal, none of which
  is amended;
* PO-14, PO-15 and PO-16, which remain as R2 §14 states them; and
* the manifest, which is not incremented.

Where this design refines R2's `rp11-launch/1` text, §7 lists every
difference for acceptance. A refinement becomes effective only if Codex's
review and Peter Duscha's decision accept it.

---

## 2. Observations and assumptions

### 2.1 Observations (repository bytes only)

| # | Observation | Source |
|---|---|---|
| OD-1 | R2 §4.4.3.4 fixes `rp11-launch/1`: argv exactly `--pass A`; `envp` read only to select one `INVOCATION_ID` matching `[0-9a-f]{32}`; descriptors ≥ 3 closed, dispositions reset, mask cleared, `umask 077`, `chdir("/")`; then `execve("/usr/bin/python3.12", ["/usr/bin/python3.12", "-I", "-S", "/usr/local/libexec/freedom-blades-rp11/rp11_entry.py", "run", "--pass", "A"], ["LC_ALL=C", "PATH=/usr/bin", "INVOCATION_ID=⟨value⟩"])`; a fixed status per failed step; one fixed class line on standard error | R2 §4.4.3.4 items 1–6 |
| OD-2 | R2 names the failure classes `launch-usage`, `launch-invocation-id` and `launch-exec-failed` | R2 §7.7, §9 |
| OD-3 | R2 places the source and build definition at `infra/rp11-launch/`, and the installed image at `/usr/local/libexec/freedom-blades-rp11/rp11-launch`, root-owned, mode `0755`, with its digest in `pass-a.json` as `launcher_sha256` | R2 §4.4.3.4, §9, §11 |
| OD-4 | R2 excludes a glibc-static build (AS-11) and requires PO-9's discharge by a runtime-source citation, then a later loader experiment | R2 §2.3, §14 |
| OD-5 | The disposable server `oracle-test` is documented as Ubuntu 26.04.1 LTS, `x86_64`, kernel `7.0.0-31-generic`. That is **not** the repository host, where `rp11-launch` would be installed | `phase-5-0-evidence-harness-concrete-plan.md` §1; `disposable-test-server.md` §1 |
| OD-6 | No repository document records the **repository host's** architecture or kernel release | `grep` of `docs/` for architecture names; only `oracle-test` and a browser build are recorded |
| OD-7 | The repository is pure Python today. No compiled source, build script or toolchain pin exists | repository layout; AGENTS.md "Coding standards" requires dependencies to be added deliberately and locked reproducibly |

### 2.2 Assumptions (stated, not verified, because host inspection, compilation and binary inspection are prohibited)

| # | Assumption | Discharged by |
|---|---|---|
| AD-1 | The repository host is `x86_64` Linux | **PO-18** at H-1 (§5.4). If it is not, D-S1 as specified does not apply and needs the architecture variant of §5.13 |
| AD-2 | The repository host runs Linux 5.9 or later, which provides `close_range` | PO-18 at H-1 and H-2 |
| AD-3 | For an `ET_EXEC` ELF image with no `PT_INTERP`, the kernel's ELF handler maps the `PT_LOAD` segments, copies argv, envp and the auxiliary vector onto the new stack without interpreting any environment string, and starts user space at `e_entry`. No user-space instruction runs before `e_entry` | D9-1: a citation of the installed kernel series' `fs/binfmt_elf.c` and `fs/exec.c` (§6.2) |
| AD-4 | `binfmt_misc` registers its handler at the head of the kernel's format list, so its registrations are tried before the ELF handler. An enabled registration whose magic and mask match the image's header would redirect execution to its interpreter | D9-1 citation; PO-17 checks that no such registration exists (§5.11) |
| AD-5 | The pinned compiler honours `-ffreestanding -nostdinc -fno-builtin -fno-stack-protector -fcf-protection=none -fno-pic -fno-pie -fno-jump-tables -mgeneral-regs-only`, and the pinned linker honours `-T`, `--build-id=none` and `-z noexecstack` as documented | **not relied on.** BI-1 … BI-9 check the output (*D2-R1:* BI-1 … BI-11 and T-L10, which also cover the flags added in §5.3.3); a flag that did not work fails inspection (FD-5) |
| AD-6 | On x86-64 the kernel enters `_start` with `%rsp` 16-byte aligned and pointing at `argc`, followed by `argv[0 … argc-1]`, a null pointer, `envp[…]`, a null pointer and the auxiliary vector | the x86-64 psABI process-initialisation section; D9-1 |
| AD-7 | systemd formats `INVOCATION_ID` as 32 lowercase hexadecimal digits | the installed systemd's source, cited with PO-14. If it is wrong, every start refuses with `launch-invocation-id`: fail-closed |
| AD-8 | While a process has **no** signal handler installed, no system call it makes can return `EINTR`: a signal is ignored, stops the process or terminates it | kernel signal-delivery semantics, cited in D9-1 |
| AD-9 | The C-library signal-wrapper refusals of FD-2 | not load-bearing for D-S1, which uses no C library. It is load-bearing only for rejecting C-2 (§4.3) |
| AD-10 | The start-up behaviours attributed below to musl, nolibc, Rust `std` and Go are as stated | not load-bearing for D-S1. If one is wrong, that candidate's rejection weakens but D-S1's selection does not change (§4.4) |

### 2.3 Assumptions added by D2-R1 (stated, not verified)

| # | Assumption | Discharged by |
|---|---|---|
| AD-11 | A synchronous fault (`#PF`, `#GP`, `#UD` from `ud2`, and the others) in a process with **no** handler for the resulting signal terminates the process without running any user-space instruction. The kernel forces the signal: if it is ignored or blocked, the disposition is reset to default and the signal is unblocked | D9-1: a citation of the installed kernel series' `kernel/signal.c` (`force_sig_info_to_task` or its successor) and `arch/x86` trap handling. **Load-bearing for PO-9** (CT-7, CT-8) |
| AD-12 | On x86-64, a system call entered by `syscall` that returns to user space resumes at the instruction after the `syscall`, with `%rcx` and `%r11` clobbered. A call interrupted by a stop with no handler is restarted by re-executing the **same** `syscall` instruction, which is still in the listing. The only exceptions are these: signal delivery to a handler (none can exist, AD-8); `rt_sigreturn` (not in the inventory); a successful `execve` (the image is replaced); `exit_group` (it does not return); and a tracer's modification (T-B, or root, out of scope) | D9-1: `arch/x86/entry` citation. **Load-bearing for PO-9** (CT-6) |
| AD-13 | Since Linux 5.18, an `execve` with `argc` 0 is given a single empty `argv[0]` by the kernel, so the image sees `argc` 1. Earlier kernels deliver `argc` 0 | D9-1. Not load-bearing: both give `launch-usage` (§5.5) |
| AB-1 | The GNU compiler driver, run with `-S -o ⟨file⟩`, starts only `cc1`, found under its own configured `libexec` directory, and creates no temporary file. It reads its compiled-in specs and, if present, a `specs` file in its library directory | IC-1 (§5.3.7) and R-2 run with the temporary directories read-only (§5.3.5). If AB-1 is wrong, R-2 fails or IC-1 names the extra input: **fail-closed** |
| AB-2 | The BFD linker may load plugins automatically from its `bfd-plugins` directory. Anything it loads is a class-B input | IC-1. Plugins are in the closure whether or not they are loaded (§5.3.7) |
| AB-3 | With `LC_ALL=C` the tools use the C library's built-in C locale and open no locale archive. They may still open `gconv` modules | IC-1. Both are in the closure whether or not they are opened |
| AB-4 | The dynamic loader may select a library variant from a `glibc-hwcaps` subdirectory according to the CPU. So the CPU can choose which pinned bytes run | pinned as part of the tree. The CPU is residual assumption HA-2 (§5.3.8) |
| AE-1 | Per-string limit: each `argv` and `envp` string, **including** its terminating NUL, is at most `MAX_ARG_STRLEN` = 32 × page size. That is 131 072 bytes on `x86_64` with 4 KiB pages. A longer string fails the whole `execve` with `E2BIG` | citation of the test host kernel's `include/uapi/linux/binfmts.h` and `fs/exec.c`, recorded with the D9-5 run. **A proof input of the experiment, not of PO-9** |
| AE-2 | Aggregate limit on the string bytes, for Linux 5.9 through at least 6.x (`bprm_stack_limits()` or its inline predecessor): `L = max(min(RLIMIT_STACK.soft / 4, ¾ × _STK_LIM), ARG_MAX)`. Here `_STK_LIM` is 8 MiB and `ARG_MAX` is 32 pages (131 072 bytes). With a soft stack limit of 8 MiB, `L` = 2 MiB | as AE-1. The supervisor sets and records the soft stack limit before each case |
| AE-3 | Pointer accounting: before the strings are counted, `(max(argc, 1) + envc) × 8` bytes are subtracted from `L`. If `L` is not greater than that amount, the result is `E2BIG` | as AE-1 |
| AE-4 | Count limit: `MAX_ARG_STRINGS` is `0x7FFFFFFF`, so it does not bind for any vector here | as AE-1 |
| AE-5 | The page size of the test host is 4 KiB | recorded with the D9-5 run. A different page size changes AE-1 and AE-2, and the supervisor recomputes them |

### 2.4 Assumption added by D2-R2 (stated, not verified)

| # | Assumption | Discharged by |
|---|---|---|
| AD-14 | The x86-64 instruction encodings of every row of XD's closed table (§5.15) are as the cited revisions of the Intel 64 and IA-32 Architectures Software Developer's Manual and the AMD64 Architecture Programmer's Manual define them, and the repository host's CPU decodes and executes the image's bytes as those manuals define | **not dischargeable by any decoder.** Each XD table row cites its manual section, and the independent review of XD (XD-9) and Codex's D9-2 decoding (XD-11) check the rows against the manuals. A CPU that departs from its manual (an erratum) is not detected by any evidence in this design. **Load-bearing for PO-9** (P-3, P-4), and named as trusted in §5.15.4 and §8 |

---

## 3. Constraints carried forward unchanged

| # | Constraint | Source |
|---|---|---|
| K-1 | PO-9: nothing that runs before the image's own reviewed code reads an environment variable, calls `dlopen`, or initialises NSS, iconv, locale or tunables. The image's only read of `envp` is the `INVOCATION_ID` selection | R2 §14 PO-9 |
| K-2 | A glibc-static build does not qualify unless PO-9 disproves AS-11. An unknown pre-entry runtime is not accepted. Cleansing must not move into a dynamically linked helper | R2 AS-11, §4.4.1; assignment §4 |
| K-3 | A clean output environment is corroboration, not proof | assignment §4; R2 §4.4.3.5 |
| K-4 | The entry's environment is exactly `{INVOCATION_ID, LC_ALL=C, PATH=/usr/bin}` (LB-2S) | R2 §7.9 |
| K-5 | Manager execution settings are trusted, reviewed root input (R-10), not prevented. T-A remains in scope. T-B is out of scope | decision M-10; R2 §6.9 |
| K-6 | No environment content is recorded (C-9) | R2 §4.4.3.5, §7.9 |
| K-7 | PO-14 is independent and load-bearing. This design neither discharges nor weakens it | R2 §14; decision M-9 |
| K-8 | Every step fails closed with no fallback, retry or alternative `execve` | R2 §4.4.3.4 item 6 |
| K-9 | Evidence classes stay separate: source properties, compiler and linker output, reproducibility, binary inspection, installed-host evidence, hostile-environment testing and PO-14 | assignment §4 |

---

## 4. Candidate comparison

### 4.1 Criteria

Each candidate is assessed on the criteria assignment §3 lists:

1. **pre-entry execution** — what runs between the kernel's transfer of
   control and the first reviewed instruction;
2. **inputs consulted before or outside the reviewed code** — environment,
   auxiliary vector, locale, tunables, NSS, iconv and configuration files;
3. **dynamic-module loading**;
4. **architecture and ABI assumptions**, and **binary format**;
5. **toolchain pinning and acquisition**;
6. **reproducibility and byte-drift sources**;
7. **source-to-binary review**;
8. **installed-digest binding**;
9. **maintenance and supply-chain cost**; and
10. **how PO-9 can be proved rather than inferred from a successful test.**

### 4.2 Candidates

| ID | Candidate |
|---|---|
| **C-1** | **Freestanding C11 plus a hand-written assembly `_start`, no C library.** System calls through inline `syscall` instructions. Linked with `-nostdlib` and an explicit linker script |
| C-1A | the same contract written **entirely in assembly** |
| C-1N | C-1 using the Linux kernel's header-only **`nolibc`** for `_start` and system-call wrappers |
| C-2 | C against **musl**, statically linked |
| C-3 | **Rust `#![no_std]` / `#![no_main]`** with a custom `_start` and `panic = "abort"` |
| C-3S | Rust with **`std`** on a static musl target |
| C-4 | **Go**, statically linked |
| C-5 | C against **glibc**, statically linked |
| C-6 | a **distribution-provided static utility**, such as a static BusyBox `env -i`, named in `ExecStart=` |
| C-7 | anything that needs no image: a unit-only allow-list, or a static CPython |

### 4.3 Assessment

**C-1 — freestanding C with an assembly entry stub.**

| Criterion | Assessment |
|---|---|
| pre-entry execution | **none.** The kernel starts user space at `e_entry` (AD-3). `e_entry` is `_start`, about ten reviewed instructions that pass `argc`, `argv` and `envp` to the C function. There is no C runtime, `crt*.o`, `libgcc`, constructor, TLS set-up or relocation processing |
| inputs consulted | only the reviewed selection reads `envp` strings. **The auxiliary vector is never read.** No locale, tunable, NSS or iconv code exists in the image. No file is opened: `open`/`openat` are absent from the system-call inventory (§5.12.2 BI-6) |
| dynamic loading | none possible: no `PT_INTERP`, no `PT_DYNAMIC`, no `mmap`, no loader code |
| architecture and format | ELF64 `ET_EXEC`, `EM_X86_64`, non-PIE, fully resolved with no relocation section. The entry stub and system-call numbers are x86-64-specific (§5.4) |
| toolchain | a C compiler, assembler and linker: one distribution's GCC and binutils packages, pinned by exact version and package digest (§5.3). **No** libc headers, libc, kernel headers or `libgcc` are build inputs (`-nostdinc`, `-nostdlib`) |
| reproducibility | high. No timestamps, no debug information and no build ID, and only *(D2-R2)* two objects are linked in a fixed order under a fixed script. The drift sources are enumerated and neutralised in §5.3.4 |
| source-to-binary review | *(amended D2-R1, D2-R2)* the complete disassembly is under 4 KiB. It has no indirect `call` or `jmp`, no `call` and no `ret` (LD-7, §5.14), so every transfer target is encoded in the instruction bytes. Once XD's independent decoding agrees exactly with the listing (T-L11, §5.15), every reachable path is determined by T-L10 and the human review HR-1 … HR-6. It is committed and bound by digest (FD-6) |
| installed-digest binding | one SHA-256 over one file, expected value committed. It is independent of where the file was built (§5.11) |
| maintenance and supply chain | about 250 lines of C, 15 of assembly, a linker script and a build script. **No runtime dependency:** no library update ever requires a rebuild. The toolchain is needed only when the source or pin changes |
| PO-9 proof | **by construction over the built binary** (§6): the kernel semantics (D9-1), structural inspection (D9-2), the reviewed listing (D9-2), reproducibility (D9-3) and installed-digest equality (D9-4). The hostile-environment experiment only corroborates |

**C-1A — pure assembly.** PO-9 is identical to C-1's: the same pre-entry path
and the same inspection. It removes the compiler from the toolchain, and the
source maps one-to-one onto the listing. However, the grammar check, the
selection loop and the error handling become harder for this Python
repository's maintainers to review and change correctly. The selection logic
also cannot be linked, as the same object file, into a test harness written in
a readable language (§5.12.1, T-L8). **Credible, not selected.** It is the
fallback if C-1's compiler output cannot be made to pass inspection (§4.5).

**C-1N — `nolibc`.** In the versions the author knows, its `_start_c` stores
`environ`, walks the `envp` pointer array to find the auxiliary vector, and in
recent versions runs `.preinit_array`/`.init_array` constructors and
stack-protector initialisation before `main` (AD-10). None of that is needed.
It adds a third-party, version-dependent start-up that must be cited per
kernel-tree release, in exchange for system-call wrappers that are ten lines
here. **Credible, not selected.**

**C-2 — musl, static.**

| Criterion | Assessment |
|---|---|
| pre-entry execution | musl's `_start` → `_start_c` → `__libc_start_main` → `__init_libc`, `__init_tls`, `__init_ssp`, then `_init` and `.init_array` (AD-10) |
| inputs consulted | `__init_libc` walks `envp` to find the auxiliary vector and reads `AT_*` entries, including `AT_RANDOM`, `AT_SECURE`, `AT_HWCAP`, `AT_PAGESZ` and `AT_SYSINFO`. To the author's knowledge no environment **variable** is read before `main`, and locale data (`MUSL_LOCPATH`) is read only by `setlocale`. Under `AT_SECURE` it polls descriptors 0–2 and may open `/dev/null`. **All of that is a per-version citation, not a structural fact** |
| dynamic loading | a static musl `dlopen` fails. No NSS modules exist; `getpw*` reads files only when called |
| signal reset | musl's `sigaction` refuses signals 32–34 (FD-2). The contract would need raw system calls anyway |
| toolchain | `musl-gcc` or a musl cross toolchain, plus the pinned musl version. That is more pinned inputs than C-1 |
| source-to-binary review | the listing contains the linked musl objects as well as the contract's code |
| PO-9 proof | **inferable by citation**: a pinned musl version's start-up source, then binary inspection. The proof is larger and must be repeated at every musl pin change |

**Credible, not selected.** It meets PO-9 only by citing a larger start-up
path, and gives no benefit the contract needs.

**C-3 — Rust `no_std`.** With `#![no_main]`, a custom `_start` and
`panic = "abort"`, its pre-entry path equals C-1's. However:

* the toolchain is `rustc`, LLVM and a system linker, plus the **pre-compiled**
  `core` and `compiler_builtins` libraries shipped with the toolchain. They
  are binary inputs, not reviewed source;
* acquisition needs `rustup` downloads or a distribution `rustc`, pinned;
* reproducibility needs `--remap-path-prefix`, one codegen unit and a pinned
  sysroot; and
* nearly all of the code is `unsafe` raw-pointer and system-call work, so
  memory safety gains little.

**Credible, not selected**, because of the larger toolchain and binary input
surface for no PO-9 gain.

**C-3S — Rust with `std`.** Before `main`, `std`'s start-up installs a
`SIGSEGV` handler and alternate stack, sets `SIGPIPE` to ignored, and may
open `/dev/null` for closed standard descriptors (AD-10). It also brings the C
library's start-up (C-2 or C-5). **Rejected:** unknown pre-entry runtime
(assignment §4).

**C-4 — Go.** Its runtime reads `GODEBUG`, `GOGC`, `GOMAXPROCS` and
`GOTRACEBACK` from the environment during scheduler initialisation, before
`main.main` (AD-10). **Rejected:** it fails K-1 by design.

**C-5 — glibc, static.** Its start-up initialises tunables from
`GLIBC_TUNABLES`, applies `IRELATIVE` ifunc resolutions shaped by CPU-feature
tunables, and initialises library search paths from `LD_LIBRARY_PATH` for a
later `dlopen` (R2 AS-11). Its `sigaction` refuses signals 32 and 33.
**Rejected** (K-2).

**C-6 — a distribution static utility.** Its runtime is chosen by the
distribution (commonly glibc-static, therefore C-5), its size makes a complete
source-to-binary review infeasible, it cannot apply the `INVOCATION_ID`
grammar, and its version changes with distribution updates. R2 §4.4.1 already
rejects it. **Rejected.**

**C-7 — no image.** A unit-only allow-list does not exist (R2 S-4, §4.4.3.3),
and that is not reopened. A static CPython runs the interpreter's own
start-up, which reads its environment, before any reviewed code. **Rejected.**

### 4.4 Selection

**D-S1 = C-1** is selected because it is the only candidate whose PO-9 proof
has all three of these properties:

1. **structural:** the absence of pre-entry code is a property of the built
   file, checked by inspection, not a property of a runtime version cited
   from outside;
2. **complete:** every executed instruction is in one reviewed listing.
   *(amended D2-R1, D2-R2)* The reachable control-flow graph is fixed by the
   decoded listing: every transfer belongs to the closed classes
   CT-1 … CT-9, none of which takes its target from machine state, because
   the image has no `ret` and no `call` (§5.14). The decoding itself is
   checked by XD's exact agreement (§5.15); and
3. **independent of trusting the toolchain:** the listing, not the compiler,
   is reviewed, and its decoding is not taken on trust from the disassembler
   that printed it (§5.15). Reproducibility ties it to the source.

C-1A shares all three. It is not selected only on maintainability and
testability grounds, and it is kept as the fallback. The rejections of C-2,
C-3 and C-1N rest on proof size, toolchain surface and maintenance, not on a
claim that they would fail PO-9.

### 4.5 When this result reverses

LB-2S must be **withdrawn**, not weakened, if any of the following occurs:

* D9-1's citation refutes AD-3 or AD-4 for the installed kernel series, so
  that user-space code can run before `e_entry` for an image of this form;
* no build from the pinned toolchain passes BI-1 … BI-11, **and** C-1A cannot
  either;
* *(D2-R1, amended D2-R2)* no build in the zero-`ret` form passes T-L10 and
  the human review HR-1 … HR-6, either as first built or under the
  fail-closed alternatives FA-1 and FA-3 (§5.14.5). A form that permits `ret`
  is **not** a further alternative: it needs a new maintainer decision
  (LD-7);
* *(D2-R2)* for no such build can XD's decoding be made to agree exactly
  with the committed listing (T-L11), or the XD review (XD-9) or Codex's
  D9-2 decoding (XD-11) finds a defect in XD that cannot be corrected and
  re-reviewed. A persistent disagreement is **never** resolved by preferring
  one decoder's output: it is a stop;
* *(D2-R1)* D9-1's citation refutes AD-11 or AD-12, so that a fault, a signal
  or a returning system call could transfer control to an address that the
  listing does not fix;
* *(D2-R1)* the build-input closure cannot be bound. That covers two cases:
  R-1's tree manifest cannot be reproduced in a second, independently
  provisioned environment; or IC-1 finds that a class-B tool opens a path
  that cannot be brought into the manifest (§5.3.7);
* *(D2-R2, LD-8)* IC-1 cannot be made to pass, or no R-5 rebuild can be
  arranged that actually varies at least one of HA-1 … HA-3. LD-8's
  acceptance of the bound root is conditional on both (§5.3.5, §5.3.7);
* two independent builds cannot be made byte-identical, so no expected digest
  can be committed (D9-3);
* PO-17 cannot be established on the repository host, because a
  `binfmt_misc` registration matching the image must remain enabled; or
* PO-14 fails (R2).

No candidate in §4.3 is a fallback in those cases: C-2, C-3 and C-1N share
C-1's dependence on AD-3, AD-4 and PO-14, and C-3S, C-4, C-5 and C-6 fail K-1
or K-2.

---

## 5. The selected design, D-S1

### 5.1 Language, runtime and the pre-entry argument (item 1)

* **Language:** ISO C11, compiled freestanding (`-ffreestanding -nostdinc`),
  with no header from any library or from the kernel. Types and constants are
  declared in the source itself.
* **Entry** *(amended D2-R2)*: a hand-written x86-64 assembly `_start` in
  `start.s`. It clears `%rbp`, loads `argc` from `(%rsp)` into `%rdi`,
  computes `argv = %rsp + 8` into `%rsi` and `envp = argv + 8·(argc + 1)`
  into `%rdx`, aligns `%rsp` with `and $-16, %rsp`, executes `push $0`, and
  enters `rp11_main(argc, argv, envp)` by **one direct `jmp`**. After the
  `push`, `%rsp + 8` is 16-byte aligned, which is the alignment a C function
  expects at entry. The pushed zero occupies the slot where a return address
  would lie; nothing ever reads it as one, because the image contains no
  `ret` (LD-7, CT-5). `_start` reads nothing else from the stack, **in
  particular not the auxiliary vector**, and it ignores the `%rdx` value the
  ABI defines. It contains no `call` and no `ret`, and its last instruction
  is the `jmp`. It is the only function allowed to use `and $-16, %rsp`
  (RI-4).
* *(D2-R2)* **`rp11_main` is the only C function in the image.** It is
  declared `noreturn`, is entered only by `_start`'s `jmp`, and contains no
  `call` and no `ret`. Every exit is the inline `exit_group` wrapper followed
  by `ud2` (RI-3, SR-4). The two selection functions of §5.6 are
  `always_inline` into it (§5.2). *The D2-R1 text, in which `_start` called
  `rp11_main` and kept an unreachable `exit_group(117)` defence after the
  `call`, is superseded* (Appendix D).
* **Runtime:** none. System calls are made by inline `syscall` instructions
  in `launch.c`. The image has no writable data segment: its only mutable
  memory is the stack.
* **Why the pre-entry path satisfies PO-9:** the path from the kernel to the
  first reviewed instruction contains **no user-space code** (AD-3), and the
  image contains nothing that runs outside the control-flow graph of `_start`
  (FD-4, BI-2 … BI-5). The full argument, and what it depends on outside the
  image, is §6.

### 5.2 Source and build-input boundary (item 2)

**Proposed repository files** (created only by a later, separately authorized
slice I-7, R2 §12):

| Path | Content | Role |
|---|---|---|
| `infra/rp11-launch/start.s` | `_start`, as §5.1 | image source |
| `infra/rp11-launch/launch.c` | `rp11_main`: steps S-1 … S-9 of §5.7, the system-call wrappers and every literal of §5.8 and §5.9. *(D2-R2)* Its only preprocessing directive is the single `#include "select.h"` (SR-8) | image source |
| `infra/rp11-launch/select.h` *(rewritten D2-R2)* | the **definitions** of `rp11_check_argv` and `rp11_select_invocation_id`, each `static inline __attribute__((always_inline))`, and their result codes. They are pure functions with no system call, no global state, no static data and no `#include`. They are the only source that reads `argv` or `envp` strings. They return their result **only as a return value**: an integer, or a pointer to the 32 validated bytes, or a null pointer. They have no out-parameter and perform no memory store (SR-2). In the image they exist only inlined into `rp11_main` | image source, and included unchanged by the test shim (T-L8) |
| `infra/rp11-launch/select.c` | *(withdrawn D2-R2)* no longer exists. Under the zero-`ret` form no separate translation unit, object or symbol holds the selection functions (Appendix D) | — |
| `infra/rp11-launch/rp11-launch.ld` | the linker script: `ENTRY(_start)`; one read-and-execute `PT_LOAD` holding `.text` and `.rodata`; `PT_GNU_STACK` read-write; `ASSERT`s that `.data`, `.bss`, `.tdata`, `.tbss`, `.init_array`, `.fini_array`, `.preinit_array`, `.ctors`, `.dtors`, `.got`, `.got.plt`, `.plt`, `.rela.*`, `.interp` and `.dynamic` are empty or absent; `/DISCARD/` for `.note.*`, `.comment` and `.eh_frame*` | build definition |
| `infra/rp11-launch/build.sh` | the exact build as a POSIX `sh` script: `set -eu`, `umask 022`, relative source names, absolute tool paths taken from the lock, the fixed flag vectors of §5.3.3. It writes the image, the linker map, the listing and the verbose compiler command lines. *(D2-R1)* It uses **only shell built-ins and the tools named in the lock**. It uses no glob, no command substitution and no external utility such as `mkdir`, `cp`, `rm`, `cat` or `sed`, and it expects ⟨out⟩ to be an existing empty directory given as a relative path. It compiles each C file with `-S` and assembles every `.s` file with the pinned `as` directly (§5.3.3) | build definition |
| `infra/rp11-launch/toolchain.lock` | the toolchain pin (§5.3.2) | toolchain identity |
| `infra/rp11-launch/build-root.manifest` *(D2-R1)* | the complete build-root tree manifest of §5.3.2: every path, its type, mode, size and SHA-256, and every symbolic link's target. It is generated once in I-7 from the provisioned root, reviewed and committed | build-input identity |
| `infra/rp11-launch/expected.sha256` | the expected SHA-256 of the image, the listing and the linker map for the pinned toolchain and `x86_64`. *(D2-R1, amended D2-R2)* It also holds the digest of the one intermediate file `launch.s`, so that drift can be located | expected digests |
| `infra/rp11-launch/rp11-launch.x86_64.listing` | the reviewed listing: `readelf` header, program-header, section and symbol tables, the complete disassembly and a `.rodata` dump, produced by the pinned binutils. *(D2-R2)* The disassembly prints one instruction per line with its complete byte field, and elides no block of zero bytes (T-L3, T-L7). **Its decoding is not trusted**: XD must agree with it exactly (T-L11) | review evidence, committed (LD-4) |
| `infra/rp11-launch/test-harness/select_shim.c` *(D2-R2)* | a freestanding translation unit that includes the **same** `select.h` and defines two non-inline wrappers that call the two inline functions. It is compiled with the image's exact compile vector of §5.3.3 and assembled with the pinned `as`. It is never part of the image | test only |
| `infra/rp11-launch/test-harness/select_harness.c` | *(amended D2-R2)* a hosted test program that links the shim object and drives the wrappers over synthetic vectors. It is never part of the image. *The D2-R1 text, "links the **same** `select.o`", is withdrawn* (Appendix D) | test only |
| `infra/rp11-launch/verify/xdecode.py` *(D2-R2)* | XD, the independent decoder of §5.15, with its closed encoding table. Python standard library only. Class-E evidence tooling (X-17); **never a build input** | evidence tooling, covered like a test |
| `infra/rp11-launch/verify/xdecode-spelling.table` *(D2-R2)* | the reviewed, injective mapping from XD's canonical mnemonic and operand forms to the listing's spelling (XD-6). Presentation only | evidence tooling, covered like a test |

**Python-side data** (same slice): the `rp11-launch/1` contract data (§5.5 …
§5.9, the system-call inventory, and the expected digests read from
`expected.sha256`) in a module beside `entry_environment.py`, as R2 §9 and
§11 foresee. Tests compare the C literals with it (T-L2).

**The build-input boundary** *(rewritten D2-R1)*. The D2 text claimed a
complete set of three items and said that nothing else is read. That claim is
withdrawn (Appendix C). It omitted `/bin/sh`, `/usr/bin/env` and the runtime
inputs of every dynamically linked tool. The boundary is now as follows.

1. **Repository inputs:** *(amended D2-R2)* the five image-source and
   build-definition files above: `start.s`, `launch.c`, `select.h`,
   `rp11-launch.ld` and `build.sh`. The D2-R1 count of six included the
   withdrawn `select.c`. XD, its spelling table and the test shim are **not**
   build inputs.
2. **The build root:** every file in the tree that `build-root.manifest` binds
   (§5.3.2). That includes, as class B:
   * the tool binaries;
   * `/usr/bin/env` and `/bin/sh` with its target;
   * the dynamic loader and every shared library;
   * loader configuration, `gconv` modules, BFD plugins, compiler specs and
     program data.

   §5.3.7 traces which executable consumes which of them.
3. **The literal start state of R-2:** the exact vector, `build_env` and
   working directory of §5.3.5.
4. **Inputs that no lock can pin:** the kernel, the CPU, the P-class entry
   mechanism, wall-clock time and file modification times, and user and host
   identity. They are named as residual host assumptions
   HA-1 … HA-5 (§5.3.8), **not** declared absent.

Within that boundary, the **source-level** inputs to the image are narrower.
No C library, C-library header, kernel header, `libgcc`, `crt*.o`, default
linker script or search-path object is linked or included. BI-8 checks that
the linker's map names only the *(D2-R2)* two objects. That is a statement about what
is **linked into** the image. It is not a claim that the tools read nothing
else.

### 5.3 Toolchain pin and reproducible build (item 3)

#### 5.3.1 What is trusted, and for what

The toolchain is **not trusted to produce correct code.** The reviewed
listing is the object of review (FD-6). The toolchain is trusted only to be
**the same** each time, so that the listing and digest a reviewer accepted can
be regenerated from the reviewed source by anyone. The pin exists for that.

*(D2-R1)* "The same" now means the same **build root**, bound file by file
(§5.3.2), and not only the same package versions. Some inputs cannot be pinned
by any file: the kernel, the CPU, the entry mechanism, time and identity. They
are named in §5.3.8 instead of being declared absent.

*(D2-R2)* "Not trusted for correctness" now covers the **disassembler** as
well as the compiler, assembler and linker. D2-R1 let T-L7 and T-L10 consume
the pinned `objdump`'s instruction boundaries and mnemonics, so a decoding
error in `objdump` was an unstated trusted input (`R4-D2-R1-1`). The listing
remains the committed, human-readable object of review, but its decoding is
accepted only where XD, an independently implemented decoder, agrees with it
exactly (§5.15). The pinned binutils are then trusted only to reproduce the
same listing bytes (T-L9), which is an identity property.

#### 5.3.2 The pin *(amended D2-R1)*

`toolchain.lock` is a line-oriented `key=value` file, format
`rp11-toolchain-lock/1`, with these fields:

* `target`: `x86_64-linux-gnu` (ELF64, `EM_X86_64`, System V ABI);
* `distribution`: one distribution release (LD-3);
* `archive_snapshot`: the release archive's snapshot identifier, so that the
  exact package versions stay retrievable after the release moves on;
* one line per **package installed in the build root**, giving the package
  name, exact version and the SHA-256 of the package file. The build root holds
  nothing except a minimal base system and the toolchain. So this list is the
  whole installed set, not a hand-chosen "tool closure";
* one line per **class-B or class-E executable** of §5.3.7 that lives in the
  build root. Each line gives the absolute path, the target of every symbolic
  link on that path, the SHA-256 of the resolved file, and, where the tool has
  one, the exact first line of its `--version` output. The executables are
  `/usr/bin/env`; `/bin/sh` and its target; the compiler driver and `cc1`;
  `as`; `ld.bfd`; `objdump`; `readelf`; `sha256sum`; `find`; and, for IC-1
  only, the system-call tracer;
* `build_argv`: the exact R-2 vector (§5.3.5);
* `build_env`: exactly `LC_ALL=C`, `PATH=/usr/bin`, `SOURCE_DATE_EPOCH=0` and
  `TZ=UTC0`;
* `shell_added_env`: the variables, if any, that the pinned `/bin/sh` adds to
  its children's environment. IC-1 establishes the list (§5.3.7); it is empty
  unless IC-1 shows otherwise;
* `manifest_argv`: the exact `find` and `sha256sum` vectors that regenerate the
  tree manifest;
* `build_root_manifest_sha256`: the SHA-256 of `build-root.manifest`; and
* `entry_mechanism`: the type and version of the P-class mechanism used to
  provision and enter the root (X-3). **This is informative. It is not a pin,
  because nothing in the root can verify it** (HA-3).

`build-root.manifest`, format `rp11-build-root/1`, lists **every** entry of
the provisioned root, sorted by path bytes. Each line gives the type, octal
mode, numeric owner and group, and size. A regular file also gets its SHA-256,
and a symbolic link its target. The only exclusions are these:

* the kernel-provided mounts `/proc`, `/sys` and `/dev`;
* `/run`;
* `/tmp` and `/var/tmp`, which must exist, be empty and be mounted read-only
  for R-2;
* the checkout directory; and
* a named list of package-manager state, cache and log paths. Each needs a
  one-line reason stating that no class-B or class-E tool opens it.

**Any path that IC-1 observes a class-B or class-E tool opening cannot be
excluded.** `/etc/ld.so.preload` must be absent. `/etc/ld.so.cache` is
included like any other file. If it is not byte-identical in two independent
provisionings, R-5 stops, and the cause is fixed before any expected digest is
committed.

**Values.** This design fixes **what** is pinned and **how**. The values are
recorded by I-7 under an authority that permits the download (§5.3.6): the
versions, package and file digests, snapshot identifier and tree manifest. No
value is invented here.

#### 5.3.3 The flag vectors *(amended D2-R1)*

Compiling *(amended D2-R2)* `launch.c`, the only C translation unit, which
includes `select.h`, to assembly (`-S -o build-out/launch.s`):

```
-S -v -std=c11 -ffreestanding -nostdinc -fno-builtin
-fno-pic -fno-pie -fno-stack-protector -fno-stack-clash-protection
-fcf-protection=none -mindirect-branch=keep -mfunction-return=keep
-fno-asynchronous-unwind-tables -fno-unwind-tables
-fno-jump-tables -fno-tree-vectorize -fno-common -fno-ident
-fno-optimize-sibling-calls -fno-reorder-blocks-and-partition
-fno-partial-inlining -fno-ipa-cp-clone -fno-ipa-sra
-fno-tree-loop-distribute-patterns -fomit-frame-pointer
-falign-functions=1 -falign-jumps=1 -falign-loops=1 -falign-labels=1
-mgeneral-regs-only -mno-red-zone -march=x86-64 -mtune=generic
-frandom-seed=rp11-launch
-Os -g0 -U_FORTIFY_SOURCE
-Wall -Wextra -Wvla -Werror
```

Assembling *(amended D2-R2)* `start.s` and `build-out/launch.s`, each with
the pinned assembler directly:

```
--64 --noexecstack -mx86-used-note=no
```

Linking with the pinned BFD linker directly, not through the compiler driver,
so that no driver default is added:

```
-m elf_x86_64 -static -nostdlib --build-id=none -z noexecstack
-z norelro --no-dynamic-linker -T rp11-launch.ld -Map rp11-launch.map
-o rp11-launch start.o launch.o
```

*(D2-R2)* `start.o` is linked first, so `.text` begins with `_start` and is
followed immediately by `rp11_main` (RI-2, XD-2).

Each flag answers FD-5 or §5.14:

* **FD-5 defaults.** No canary, whose read of `%fs:0x28` would fault without
  TLS. No PIE, which would need self-relocation code. No CET instrumentation
  or property notes, no fortification, no unwind tables, no vector registers
  and no build ID.
* **No jump tables.** So no `switch` lowers to an indirect jump.
* **Indirect-branch and function-return thunks kept off.** No retpoline or
  return thunk (CT, §5.14.1).
* **No sibling calls.** No `jmp` leaves its function (RI-3). *(D2-R2)* Under
  the zero-`ret` form the flag is defence in depth: `rp11_main` contains no
  call, so it has no sibling call to optimise. The absence of every `call`
  and `ret` comes from the source discipline (`always_inline`, `noreturn`,
  `__builtin_trap()`; SR-1 … SR-8), and is **checked** only by XD, T-L11 and
  T-L10.
* **No block partitioning, partial inlining, cloning or IPA-SRA.** So no
  compiler-created `.cold`, `.part`, `.constprop` or `.isra` symbol exists
  (RI-1).
* **No loop-pattern distribution.** No synthesised `memcpy` or `memset` call.
  Such a call would be an undefined symbol: the link fails and BI-4 catches
  it.
* **No frame pointer and no red zone.** Every frame store is at a non-negative
  `%rsp` displacement (RI-5).
* **Alignment 1.** No padding between functions (RI-2).
* **`-Wvla`.** No dynamic stack adjustment (RI-4).
* **Fixed random seed.** Any seed-dependent name is fixed.
* **`-S`.** The driver starts only `cc1` and needs neither `PATH`, to find
  `as`, nor a temporary file (AB-1). The pinned `as` is then run by
  `build.sh` itself.

The D2 vector's `-ffile-prefix-map=⟨build dir⟩=.` is **removed**. It put an
absolute, build-specific path into a vector described as fixed, and into the
`-v` record that R-4 compares. It is not needed: every tool receives only
relative paths, and no debug information is emitted. The D2 `-Wa,…` options
move to the assembler vector, because the driver no longer assembles.

File names in these vectors are shown schematically. `build.sh` fixes their
exact relative spelling, and the working directory `build.sh` changes to for
each step with the `cd` built-in. T-L3 checks both.

**The effect of every flag is established only by BI-1 … BI-11 and T-L10**,
*(D2-R2)* over a decoding that XD has confirmed (T-L11).

#### 5.3.4 Byte-drift sources and how each is neutralised *(amended D2-R1)*

| Source of drift | Neutralised by |
|---|---|
| compiler, assembler or linker version, patch level or distribution configuration, including default flags and specs | the package and per-file pins and the tree manifest (§5.3.2); the explicit flag vectors; the `-v` record, compared across builds |
| shared libraries, loader, loader cache, `glibc-hwcaps` variants, `gconv` modules, BFD plugins and program data used by class-B tools | all are files of the build root, bound by `build-root.manifest` (R-1). IC-1 checks that no class-B tool opens anything outside it. The **choice** among pinned `glibc-hwcaps` variants depends on the CPU: HA-2 |
| `/bin/sh` and `/usr/bin/env` | class-B files of the build root, bound like the compiler (X-5, X-6) |
| host CPU | `-march=x86-64 -mtune=generic`, not `-march=native`, fixes the **target**. The host CPU remains an input to the tools (HA-2). R-5 on different hardware can detect drift |
| kernel of the build host | not pinnable by a file (HA-1). Recorded, and varied in R-5 where possible |
| build path | only relative paths on every tool command line; no debug information; R-4(a) |
| timestamps and source modification times | ELF carries none; no archive is built; R-4(b) |
| build ID and notes | `--build-id=none`; notes, `.comment` and unwind sections discarded; `-fno-ident` |
| compiler random seed | `-frandom-seed=rp11-launch` |
| input order | fixed object order on the link line; one linker script; no glob or directory read in `build.sh` |
| environment variables read by the tools (`GCC_EXEC_PREFIX`, `COMPILER_PATH`, `LIBRARY_PATH`, `CPATH`, `C_INCLUDE_PATH`, `TMPDIR`, `LD_*`, `GLIBC_TUNABLES`, locale variables and others) | `/usr/bin/env -i` starts `/bin/sh` with exactly `build_env`. IC-1 records each class-B process's environment, which must equal `build_env` plus `shell_added_env` |
| temporary files | `-S` removes the driver's temporary file (AB-1). `/tmp` and `/var/tmp` are empty and read-only during R-2, so an unexpected temporary file fails the build rather than becoming a silent input |
| `umask` and file ownership | cannot change digested **bytes**: only bytes are digested. `build.sh` sets `umask 022` so that output modes are stable. The caller's `umask` does not reach the tools, so R-4 no longer varies it |
| locale-dependent diagnostics | `LC_ALL=C` (AB-3) |
| user and host identity | R-4(c) |
| the P-class entry mechanism | HA-3. R-1 checks the tree from inside the entered session; R-5 uses a separately provisioned environment |

#### 5.3.5 The reproducible-build procedure *(amended D2-R1)*

| Step | Action | Pass condition |
|---|---|---|
| R-1 | Provision a disposable build root from `toolchain.lock`, verifying each package file's SHA-256 before installing it (X-1, X-2). Then, **inside the entered environment and in the same session that will run R-2**, regenerate the tree manifest with `manifest_argv`, using the pinned `find` and `sha256sum` (X-4) | every package digest equal; the regenerated manifest byte-equal to the committed `build-root.manifest`; `/etc/ld.so.preload` absent; `/tmp` and `/var/tmp` empty and read-only |
| R-2 | The entry mechanism starts, as the **first process in the build root**, as an unprivileged build user, with the checkout root as working directory, exactly this vector: `/usr/bin/env -i LC_ALL=C PATH=/usr/bin SOURCE_DATE_EPOCH=0 TZ=UTC0 /bin/sh infra/rp11-launch/build.sh build-out`. `build-out` is an existing empty directory inside the checkout. No interactive shell runs inside the root before it | exit 0; the image, map, listing, *(D2-R2)* `launch.s` and the `-v` record exist; `/tmp` and `/var/tmp` still empty |
| R-3 | Compare the digests of the image, map, listing and `.s` files with `expected.sha256`, and the listing bytes with the committed listing | all equal |
| R-4 | Repeat R-2 three times in the same verified root, varying one input each time: **(a)** a checkout at a different absolute path; **(b)** a later wall-clock time, with every source file's modification time changed; **(c)** a different unprivileged build user, with a different UID and user name, and where the entry mechanism allows, a different host name | image, map, listing and `.s` digests equal R-2's in every run |
| R-5 | *(amended D2-R2, LD-8)* An **independent rebuild** by a second party (LD-5), before H-1: a separately provisioned root from the same lock, performing R-1 … R-3. It **must** use at least one of: a different machine (CPU model, HA-2), a different kernel release (HA-1) or a different entry mechanism (HA-3). It uses more than one where available. Both parties record the kernel release, CPU model and entry mechanism of their builds, and the R-5 record states which of HA-1 … HA-3 actually differed | R-1 manifest equal to the committed one; image, listing, map and `launch.s` digests equal to `expected.sha256`; **and** the record shows at least one of HA-1 … HA-3 actually differed. A rebuild in which none differed is not R-5 and does not pass. *The D2-R1 wording "Where available", which let R-5 pass with no variation, is superseded* (Appendix D) |

**What each R-4 variation proves.** Each variation reaches the build, and
each is expected not to reach the bytes:

* **(a)** The absolute path reaches `cc1` as its working directory and reaches
  every tool through its arguments. R-4(a) shows it does not reach the output.
* **(b)** Time and modification times reach every tool through the clock and
  `stat`. R-4(b) shows they do not reach the output.
* **(c)** User and host identity reach every process. R-4(c) shows they do not
  reach the output.

**What R-4 no longer varies, and why.** The D2 text varied the caller's
`umask` and `TMPDIR`. Neither reached the build:

* `/usr/bin/env -i` discards `TMPDIR`;
* `build.sh`'s first action after `set -eu` is `umask 022`; and
* `umask` cannot affect digested bytes.

Varying them proved only that those two statements execute. The variations
are withdrawn (Appendix C). The absence of temporary files is now established
by R-2's read-only `/tmp` and by IC-1, not by a variation.

A difference at R-1, R-3, R-4 or R-5 is a stop. It is investigated and the
cause fixed in reviewed source, in the lock or in the manifest. The expected
digest is **never** updated to match an unexplained output. A difference that
correlates with HA-1 … HA-5 is a finding about the build, **not** a licence
to narrow the reproducibility claim silently. *(D2-R2)* This hard stop on
every unexplained difference is one of LD-8's conditions of acceptance.

#### 5.3.6 Acquisition

Package files come from the pinned distribution's signed archive at the
recorded snapshot, and are verified against the lock digests before use. The
build environment is disposable: a container, chroot or virtual machine that
holds nothing else. *(D2-R1)* The download, signature-verification,
installation and entry tools (X-1 … X-3) are class P. They are not pinned by
the lock. Their product, the build root, is bound by R-1, and their residual
influence is HA-3. **Downloading, installing and building are outside this
assignment and outside every current authority.** They need the M-14
implementation authority that decision `…-R4-D1-R2-A1` does not grant.

#### 5.3.7 Every executable in R-1 … R-5, and its runtime inputs *(new D2-R1)*

**Classes.**

* **B:** it runs during R-2 and can change the image bytes.
* **E:** it produces evidence that is committed or digest-bound, or a verdict
  that D9-2 or D9-3 relies on.
* **P:** it provisions or enters the build root, and influences the bytes only
  through the tree that R-1 then binds, or through HA-3.

Classes B and E are pinned wherever their output is committed or digest-bound.

| # | Executable | Class | Role | Runtime inputs it may consume | Pinned or bound by |
|---|---|---|---|---|---|
| X-1 | package download and signature-verification tools | P | fetch package files from the snapshot; verify the archive signature | network, archive keys | package-file SHA-256 in the lock, checked before installation; identity recorded |
| X-2 | package installer | P | unpack packages into the root, run maintainer scripts, and generate `/etc/ld.so.cache` | its own configuration and database | the resulting tree, bound by R-1; identity recorded |
| X-3 | entry mechanism (container runtime, `chroot`, or virtual machine) | P | presents the root; sets the user, mounts, limits and any confinement; starts R-2's vector | host configuration; host kernel | **not pinnable** (HA-3); `entry_mechanism` recorded |
| X-4 | `find` and `sha256sum` in the root, run with `manifest_argv` | E | regenerate the tree manifest for R-1 | loader, C library, their own shared libraries | tree manifest and lock tool lines |
| X-5 | `/usr/bin/env` | **B** | discards the environment; starts `/bin/sh` with `build_env` | loader; `/etc/ld.so.cache`; its `DT_NEEDED` libraries; `gconv` and locale files if opened (AB-3) | tree manifest; lock tool line |
| X-6 | `/bin/sh` and its symbolic-link target | **B** | runs `build.sh`; applies `set -eu` and `umask 022`; performs redirections; builds every tool's vector | as X-5 | tree manifest; lock tool line (link target included) |
| X-7 | compiler driver | **B** | parses the vector; applies specs; starts `cc1` | as X-5, plus its C++ runtime libraries, compiled-in specs, an optional `specs` file and its configured prefix directories (AB-1) | tree manifest; lock tool line; `-v` record |
| X-8 | `cc1` | **B** | compiles C to assembly. *(D2-R2)* It compiles `launch.c` only, and reads `select.h` through its one `#include` | as X-5, plus `libstdc++`, `libm`, `libgcc_s`, `libgmp`, `libmpfr`, `libmpc`, `libisl`, `libzstd`, `libz` or their equivalents for the pinned version, and `gconv` modules (AB-3) | tree manifest; lock tool line |
| X-9 | `as` | **B** | assembles *(amended D2-R2)* the two `.s` files, `start.s` and `launch.s` | as X-5, plus the BFD, opcodes and compression libraries it links | tree manifest; lock tool line |
| X-10 | `ld.bfd` | **B** | links; writes the map | as X-9, plus any plugin in its `bfd-plugins` directory (AB-2) | tree manifest; lock tool line; BI-8 on the map |
| X-11 | the dynamic loader, for every dynamically linked B or E tool | **B** | resolves libraries; may select `glibc-hwcaps` variants (AB-4) | `/etc/ld.so.cache`; `/etc/ld.so.preload`, which must be absent; the CPU (HA-2). It gets no `LD_*` or `GLIBC_TUNABLES`, because of `env -i` | tree manifest |
| X-12 | `objdump` | E | the listing's disassembly and `.rodata` dump | as X-9 | tree manifest; lock tool line; T-L9 regenerates byte-equal |
| X-13 | `readelf` | E | the listing's header, program-header, section and symbol tables | as X-9 | as X-12 |
| X-14 | `sha256sum` | E | the digests of R-3, R-4 and `expected.sha256` | as X-5 | tree manifest; lock tool line. The reviewer recomputes the image digest with an independent implementation (for example Python `hashlib`) at D9-2 |
| X-15 | system-call tracer, IC-1 only | E | records IC-1's `execve`, `open`, `openat` and `stat`-family calls | as X-9 | tree manifest while IC-1 runs; lock tool line. It is present only for IC-1, which is a separate run |
| X-16 | the Python interpreter running T-L7, T-L10 *(D2-R2)* and XD, T-L11 and T-L12 | E | the ELF-structure, listing-to-`.text`, decoding-agreement and control-transfer verdicts | its own installation, **outside** the build root | not in the build root. Version recorded with the verdict. The verdict is re-derived by the reviewer at D9-2. It never touches image bytes |
| X-17 *(D2-R2)* | XD, `infra/rp11-launch/verify/xdecode.py`, with its spelling table | E | the independent decoding of `.text` and its exact agreement with the listing (T-L11, §5.15) | the image file and the committed listing, read only; the X-16 interpreter | **not a build input and not in the build root.** It runs only after R-2, reads the image and listing, and writes only its own verdict and stream, which no build step reads. Its file digests and the interpreter version are recorded with every verdict (XD-8). Independently reviewed (XD-9) and checked against Codex's independently prepared D9-2 decoding (XD-11) |

**IC-1, the input-closure trace** (build-environment evidence, later
authority, in I-7). IC-1 runs R-2 once in a verified root under X-15 and
records:

* every `execve`'s path, vector and environment;
* every path opened; and
* every `stat`-family call.

It passes only if all of the following hold:

* every executed path is an X-5 … X-11 executable;
* every opened path is in `build-root.manifest` and outside its excluded set,
  apart from these: the five repository inputs *(D2-R2; six in D2-R1)*; `build-out/`; `/dev/null`;
  and any `/proc` or `/sys` path, which must be listed by name as
  kernel-provided input under HA-1;
* every class-B process's environment equals `build_env` plus
  `shell_added_env`;
* no path under `/tmp` or `/var/tmp` is created; and
* the outputs' digests equal R-2's.

IC-1 is evidence for one run. It is repeated after any change to the lock or
the manifest. It does not show what a tool would open on a different kernel or
CPU (HA-1, HA-2). *(D2-R2, LD-8)* **A passing IC-1 is a precondition of
LD-8's acceptance of the bound build root.** Until IC-1 has passed for the
current lock and manifest, the build-root claim of §5.3.8 is not made, and no
expected digest built under it is accepted (§5.12.3).

#### 5.3.8 Residual host assumptions, and what independent reproducibility can and cannot show *(new D2-R1)*

| # | Input no file can pin | How it reaches the build | Mitigation |
|---|---|---|---|
| HA-1 | the build host's kernel, including any `/proc` or `/sys` value a tool reads | every system call of every tool | release recorded in each build record; *(amended D2-R2)* one of the three candidates R-5 must vary (at least one of HA-1 … HA-3 must actually differ); IC-1 names every `/proc` or `/sys` path read |
| HA-2 | the build host's CPU | the loader's `glibc-hwcaps` choice (AB-4), and any CPU-dependent path inside the tools | model and feature flags recorded; *(amended D2-R2)* one of the three candidates R-5 must vary |
| HA-3 | the P-class entry mechanism and its configuration | the view of the root, mounts, limits and confinement between R-1 and R-2 | R-1 runs in the same session as R-2, from inside it. R-5 uses a separately provisioned environment and, where available, a different mechanism; *(amended D2-R2)* it is one of the three candidates R-5 must vary. **Trusted for the seconds between R-1 and R-2** |
| HA-4 | wall-clock time and file modification times | clock and `stat` | R-4(b) |
| HA-5 | user and host identity | every process | R-4(c) |

**What independent reproducibility adds, and what it does not.** R-5 shows
that, for one pair of environments that differ in some of HA-1 … HA-5, the
pinned root produced the same bytes. That detects drift and narrows the
residual trust to this: *the pinned tools produce the same bytes on the
variants tested.* It does **not**:

* make an unpinned input stop being an input;
* test a different toolchain, since a defect common to the pinned tools
  reproduces faithfully;
* cover variants that were not tested;
* replace the listing review, which is what PO-9 relies on (§5.3.1, §6); or
* *(D2-R2)* show that **any instruction decoder is correct**. R-5 reruns the
  same pinned `objdump`, so a decoding error in it reproduces byte for byte
  into the same listing. Decoding correctness is addressed only by XD's
  independent decoding and Codex's D9-2 decoding (§5.15), and **not** by
  reproducibility (LD-8).

*(D2-R2, LD-8)* Peter Duscha accepted this bound-root model on four
conditions, each now normative: IC-1 passes (§5.3.7); R-5 actually varies at
least one of HA-1 … HA-3 and records which (§5.3.5); every unexplained
difference is a hard stop (§5.3.5); and `R4-D2-R1-1` is resolved
independently of reproducibility (§5.15). **Diverse double compilation is not
required**, and none is specified.

A claim of "complete closed toolchain" is therefore **not made**. The claim is:
**the build root is closed and bound, and HA-1 … HA-5 are named residual
inputs.**

### 5.4 Target architecture and kernel ABI (item 4)

* **Architecture:** `x86_64` only (LD-2). ELF64, little-endian, `EM_X86_64`,
  `ET_EXEC`, OS ABI `SYSV`. It is not built for the x32 ABI or for i386
  compatibility mode. Any other architecture is a replacement under §5.13.
* **Process entry:** as AD-6. `_start` depends only on `argc`, `argv` and
  `envp`.
* **System-call ABI:** the `syscall` instruction. The number goes in `%rax`,
  arguments in `%rdi`, `%rsi`, `%rdx` and `%r10`, and `%rcx` and `%r11` are
  clobbered. A return value in `[-4095, -1]` is an error. The vDSO is never
  called.
* **System-call inventory, closed:**

  | Name | x86-64 number | Used in |
  |---|---|---|
  | `fcntl` (`F_GETFD` = 1 only) | 72 | S-3 |
  | `close_range` | 436 | S-4 |
  | `rt_sigaction` | 13 | S-5 |
  | `rt_sigprocmask` (`SIG_SETMASK` = 2 only) | 14 | S-6 |
  | `umask` | 95 | S-7 |
  | `chdir` | 80 | S-8 |
  | `execve` | 59 | S-9 |
  | `write` (descriptor 2 only) | 1 | diagnostics |
  | `exit_group` | 231 | every failure |

* **Minimum kernel:** Linux 5.9, for `close_range`. No fallback exists: on an
  older kernel, or where confinement denies `close_range`, S-4 fails closed
  (§5.10).
* **Where it is confirmed:** PO-18, at H-1 and H-2 (§5.11). The repository
  host's architecture is unrecorded (OD-6).

### 5.5 Accepted argv (item 5)

* `argc` must equal **3**.
* `argv[1]` must equal the bytes `--pass` followed by NUL, and `argv[2]` the
  bytes `A` followed by NUL. The comparison is byte-exact: no prefix match, no
  `--pass=A` form, no case folding and no option parsing.
* `argv[0]` is **not examined**. Its value, including an empty string, has no
  effect.
* Anything else, including `argc` 0, exits `111` (`launch-usage`) before any
  state operation. *(D2-R1)* It first writes the `launch-usage` line (§5.9).
  On Linux 5.18 and later, the kernel turns an `argc` 0 `execve` into `argc` 1
  with an empty `argv[0]` (AD-13). Either way the result is `111`.

### 5.6 `envp` handling (item 6)

`rp11_select_invocation_id(envp)` is the **only** code that reads an `envp`
string. It is a pure function in `select.c` *(D2-R2: in `select.h`, inlined into `rp11_main`; the behaviour below is unchanged)*:

```text
count := 0
for each pointer e in envp, until the terminating null pointer:
    compare e byte by byte with "INVOCATION_ID", stopping at the first mismatch
    if all 13 bytes match:
        if e[13] == '=':  count += 1; candidate := e + 14
        if e[13] == NUL:  count += 1; candidate := invalid
        otherwise:        not this name; ignore e (for example INVOCATION_IDX=…)
    otherwise: ignore e
if count != 1:                               refuse (launch-invocation-id)
if candidate is not exactly 32 bytes of [0-9a-f] followed by NUL:
                                             refuse (launch-invocation-id)
copy those 32 bytes into the stack buffer "INVOCATION_ID=" ⟨32⟩ NUL
```

| Case | Result |
|---|---|
| exactly one `INVOCATION_ID=` entry with 32 lowercase hex digits | accepted; the 32 bytes are copied |
| none | `112` |
| two or more, **even if identical** | `112` |
| an entry that is exactly `INVOCATION_ID`, with no `=` | counts as an occurrence and is invalid: `112` |
| `INVOCATION_ID=` with an empty value, 31 or 33 digits, an uppercase digit, or any other byte | `112` |
| `invocation_id=…`, ` INVOCATION_ID=…`, `INVOCATION_IDX=…` | a different name: ignored |
| any other entry, whether well-formed or not (no `=`, empty, non-ASCII, very long) | ignored |

**Bounds on what is read.** For a non-matching entry, at most the first 14
bytes are read, and fewer at the first mismatch or NUL. For a matching entry,
at most 47 bytes are read. **No other entry is copied, parsed, interpreted or
passed on.** Malformed entries of other names are deliberately not refused:
refusing them would require reading them, which is the input consumption K-1
forbids, and they cannot reach the entry.

**Provenance, not integrity.** A unit drop-in could set `INVOCATION_ID` (R2
§4.4.3.4 item 3). The value is grammar-constrained data that nothing
interprets, used only as diagnostic provenance (R2 §6.8).

### 5.7 State operations, in exact order (item 7)

| Step | Operation | Failure | Exit status |
|---|---|---|---|
| S-1 | argv check (§5.5). No system call | refusal | `111` `launch-usage` |
| S-2 | `envp` selection (§5.6). No system call | refusal | `112` `launch-invocation-id` |
| S-3 | `fcntl(fd, F_GETFD)` for `fd` = 0, 1 and 2, in that order | any error return | `113` `launch-stdio` |
| S-4 | `close_range(3, 0xFFFFFFFF, 0)` | any non-zero return | `114` `launch-descriptors` |
| S-5 | for each signal `s` from 1 to 64 **except 9 (`SIGKILL`) and 19 (`SIGSTOP`)**, in ascending order: `rt_sigaction(s, &{handler = SIG_DFL, flags = 0, restorer = 0, mask = 0}, NULL, 8)` | any non-zero return | `115` `launch-signals` |
| S-6 | `rt_sigprocmask(SIG_SETMASK, &0, NULL, 8)` | any non-zero return | `115` `launch-signals` |
| S-7 | `umask(0077)`. It returns the previous mask and cannot fail. The return value is ignored | — | — |
| S-8 | `chdir("/")` | any non-zero return | `116` `launch-chdir` |
| S-9 | `execve` of §5.8 | any return | `117` `launch-exec-failed` |

**Why this order.**

* **Input checks first (S-1, S-2).** A refusal then depends only on the
  inputs, and no state operation precedes it.
* **Standard descriptors before closure (S-3).** If descriptor 0, 1 or 2 were
  closed, a later `open` in the entry could receive that number and write
  evidence into what the journal treats as a stream (FD-7).
* **Dispositions before the mask (S-5, S-6).** Resetting dispositions first
  means that any signal still pending when the mask is cleared is delivered
  with the default action, never under an inherited `SIG_IGN`. A process
  image started by `execve` has no inherited handler, only inherited ignores:
  systemd ignores `SIGPIPE` by default, for example.
* **`umask` and `chdir` last.** They affect only what the entry creates and
  resolves.

**Not touched, and why.** Resource limits, `no_new_privs`, capabilities,
securebits, seccomp, Landlock, namespaces, cgroup, `personality`, scheduling,
`oom_score_adj` and interval timers come from the loaded unit configuration.
They are trusted root input (R-10, K-5). The image neither resets nor reports
them, and no record claims otherwise.

### 5.8 The literal `execve` (item 8)

* **Path:** `/usr/bin/python3.12`
* **argv** (7 entries, then a null pointer):
  1. `/usr/bin/python3.12`
  2. `-I`
  3. `-S`
  4. `/usr/local/libexec/freedom-blades-rp11/rp11_entry.py`
  5. `run`
  6. `--pass`
  7. `A`
* **envp** (3 entries, then a null pointer), in this order:
  1. `LC_ALL=C`
  2. `PATH=/usr/bin`
  3. `INVOCATION_ID=⟨the 32 selected bytes⟩`

Every byte except the 32 selected ones is a compiled literal in `.rodata`. The
`INVOCATION_ID` string and both pointer arrays live on the stack. This is
R2's vector and environment unchanged (OD-1, K-4).

### 5.9 Exit statuses and diagnostics (item 9)

| Status | Class | Standard-error line (exact bytes) |
|---|---|---|
| — | success | none: the process becomes the entry |
| `111` | `launch-usage` | `rp11-launch/1: launch-usage\n` |
| `112` | `launch-invocation-id` | `rp11-launch/1: launch-invocation-id\n` |
| `113` | `launch-stdio` | `rp11-launch/1: launch-stdio\n` |
| `114` | `launch-descriptors` | `rp11-launch/1: launch-descriptors\n` |
| `115` | `launch-signals` | `rp11-launch/1: launch-signals\n` |
| `116` | `launch-chdir` | `rp11-launch/1: launch-chdir\n` |
| `117` | `launch-exec-failed` | `rp11-launch/1: launch-exec-failed\n` |

* The range avoids shell conventions (126, 127, 128 + *n*) and systemd's own
  `EXEC_*` statuses (200 and above). Statuses 110, 118 and 119 are reserved
  and unused.
* **The entry's bootstrap must not use statuses 110 … 119**, so that a status
  in that range always means the launcher refused. That is an interface
  constraint on a later slice.
* **Non-sensitive by construction.** Each line is a compiled literal. No
  argument, environment value, `errno`, path or `INVOCATION_ID` is written.
* The line is written with one `write(2, …)`. Its result is ignored: a short
  or failed write never changes the exit status, and nothing is retried. Under
  `113` the line may be lost, because descriptor 2 may be the one that is
  closed. The status still identifies the class.
* *(D2-R1)* **Normative order for every refusal and failure**, statuses 111 …
  117: exactly one `write(2, ⟨line⟩, ⟨length⟩)` is **attempted**, then
  `exit_group(⟨status⟩)` is called. No other system call comes between them.
  The write is attempted whatever state descriptor 2 is in. The image never
  tests descriptor 2 before writing, and under `111` and `112` the write
  precedes S-3. The line lengths, in bytes including the newline, are as
  follows:

  | Class | Length |
  |---|---|
  | `launch-usage` | 28 |
  | `launch-invocation-id` | 36 |
  | `launch-stdio` | 28 |
  | `launch-descriptors` | 34 |
  | `launch-signals` | 30 |
  | `launch-chdir` | 28 |
  | `launch-exec-failed` | 34 |

* *(D2-R1)* **When the line may be absent or short.** Descriptor 2 is
  **usable** when it is open for writing and a write to it neither blocks nor
  raises a signal. Examples are an empty regular file, or a pipe whose reader
  is present and not full. When descriptor 2 is usable, the write returns the
  full length. The possible departures are these:
  * descriptor 2 closed, or open read-only: `-EBADF`;
  * a pipe with no reader and `SIGPIPE` ignored: `-EPIPE`;
  * a pipe with no reader and `SIGPIPE` at its default: the process is killed
    by `SIGPIPE` before `exit_group`. That is an interruption (§5.10): no
    `execve`, and no launcher status;
  * a full pipe or blocking device: the write blocks, which is an interruption
    (§5.10); and
  * a regular file at its size limit or on a full device: a short write, or
    `-EFBIG` or `-ENOSPC`. `SIGXFSZ` applies as for `SIGPIPE`.

  In every case except the two kills and the block, `exit_group(⟨status⟩)`
  follows. **Omission is never acceptable when descriptor 2 is usable**
  (§5.12.4).

### 5.10 Partial failure, interruption and unexpected kernel results (item 10)

| Situation | Behaviour |
|---|---|
| a step fails after earlier steps succeeded | the image writes the class line and calls `exit_group` with the step's status. **Every earlier step changed only this process's own state**, so nothing outside the process needs undoing. There is no fallback, retry or alternative path |
| a signal arrives before S-5 | its inherited disposition applies: an ignored signal is discarded; otherwise the default action terminates or stops the process. No `execve` happens after termination |
| a signal arrives after S-5 | the default action applies |
| `EINTR` | cannot occur: no handler is ever installed (AD-8) |
| `systemctl stop` of the unit | `SIGTERM` terminates the image with no `execve`. That is a §9.5.3 interruption, as R2 §4.4.3.4 states |
| a call expected to return 0 returns any non-zero value, including an out-of-range positive value | treated as failure for that step |
| `execve` returns | always an error: `117` |
| `execve` fails after the kernel's point of no return | the kernel kills the process. No status from this image exists, and systemd records a signal. No retry |
| `rp11_main` returns (a defect) | *(amended D2-R2)* cannot occur in an accepted image: `rp11_main` contains no `ret` (XD, T-L10, RI-3), and nothing follows `_start`'s `jmp`. Were a `ret` executed in a defective image, it would read the zero word `_start` pushed and transfer to address 0, which is unmapped, and the resulting fault terminates the process with no user-space code and no `execve` (AD-11, CT-8). *The D2-R1 row, in which `_start` called `exit_group(117)`, is superseded* (Appendix D) |
| the diagnostic `write` blocks | an interruption, handled as above. The operator may stop the unit |
| resource exhaustion | none is possible within the image: it allocates nothing. *(amended D2-R1)* Its maximum stack depth is computed from the listing by T-L10 (RI-4), and must not exceed the 1 KiB design bound. If the space left below the kernel-built argument area is smaller than that (a small `RLIMIT_STACK`, or a large hostile block), the first `push` or stack store that touches an unmapped page raises a synchronous fault *(amended D2-R2: the image contains no `call`)*. That terminates the process with no user-space code and no `execve` (AD-11, CT-8) |
| a synchronous fault anywhere in the image (a defect, or a read beyond a mapping) | the kernel forces the signal, and the process terminates with no user-space code and no `execve` (AD-11). No launcher status exists, and systemd records a signal |

### 5.11 Binding: manifest, pass configuration, H-1 and H-2 (item 11)

**The chain from reviewed source to the file that runs:**

| Link | Bound by | Checked when | Kind |
|---|---|---|---|
| source and build definition (§5.2) | `COVERED_SOURCES` → review-manifest digest | every manifest computation | repository binding |
| toolchain identity | `toolchain.lock`, a covered source | R-1 at every build | repository binding |
| build-root identity *(D2-R1)* | `build-root.manifest`, a covered source, whose digest is also in the lock | R-1 at every build, from inside the entered session; IC-1 after any lock change | repository binding of the class-B and class-E closure. HA-1 … HA-5 are **not** bound (§5.3.8) |
| reviewed listing | a covered source; its digest is in `expected.sha256` | R-3 | repository binding |
| expected image digest | `expected.sha256`, a covered source, **and** the serialised manifest field `rp11_launch.expected_sha256` (with `architecture = x86_64`) | R-3, R-5 | repository binding |
| `launcher_sha256` in `/etc/freedom-blades-rp11/pass-a.json` | must equal the manifest's expected digest. The pass configuration's digest is bound in the A-2 authorization (R2 §11) | H-1; diagnostically by the entry (`entry-launcher-mismatch`, R2 §6.5) | root-controlled input |
| installed file | the H-1 record | H-1, then H-2 before each pass | installation-time check and pre-pass review |

**Manifest content** (for the later implementation; **no increment now**),
refining R2 §11's `rp11-launch/1` item:

* the covered files of §5.2 except the test harness, which is covered as a
  test would be;
* serialised data: the accepted argv; the `execve` path, vector and
  environment literals; the `INVOCATION_ID` grammar; the status table of
  §5.9; the system-call inventory of §5.4; the architecture; the minimum
  kernel; the expected image, listing and map digests; and the
  `toolchain.lock` digest.
* *(D2-R1)* also serialised:
  * the `build-root.manifest` digest;
  * `build_argv`, `build_env` and `shell_added_env`;
  * the expected `.s` digests *(D2-R2: `launch.s` only)*; and
  * the contract data that T-L10 checks against: the permitted control-transfer
    classes and instruction list, the contract function set, the frame-size
    bound and the expected stack-bound value (§5.14). *(D2-R2)* The contract
    function set is `_start` and `rp11_main`; the permitted list contains no
    `call` and no `ret`.
* *(D2-R2)* also serialised: the SHA-256 of XD's source and of its spelling
  table, and the expected digest of the agreed instruction stream that T-L11
  emits for the expected image (§5.15, XD-8).

**The H-1 installation record** (written by root under its own future
authority) gains these launcher facts, in addition to R2 §4.4.3.7:

* the installed path, SHA-256, owner `root:root` and mode `0755`; no set-user-
  or set-group-ID bit; no file capability; no ACL entry granting write; and
  every parent directory up to `/` root-owned and not group- or
  world-writable;
* the SHA-256 equal to `expected.sha256` **and** to the pass configuration's
  `launcher_sha256`;
* the `toolchain.lock` digest and the identities of the parties whose builds
  reproduced the digest (R-2, R-5);
* *(D2-R1)* the `build-root.manifest` digest. For each build: the recorded
  kernel release, CPU model and entry mechanism (HA-1 … HA-3), and which of
  them differed between R-2 and R-5; the IC-1 record's digest; and the T-L10
  verdict and the version of the interpreter that produced it (X-16);
* *(D2-R2)* the T-L11 and T-L12 verdicts, the XD source and spelling-table
  digests, the agreed-stream digest, the interpreter version, and the record
  of Codex's independently prepared D9-2 decoding under XD-11;
* **PO-18:** the kernel's machine name (`x86_64`) and release, and the release
  being 5.9 or later; and
* **PO-17:** that no enabled `binfmt_misc` registration matches the image's
  first 128 bytes under its magic, mask and offset, or that `binfmt_misc` is
  not mounted. **No environment content is recorded.**

**The H-2 pre-pass check** re-reports the launcher facts above. Any difference
from H-1 stops the pass before it is requested, including a changed kernel
release. **H-1 and H-2 are reviews of root-controlled state at one moment
each, not prevention** (R2 R-10, S-7).

### 5.12 Tests, inspection, reproducibility and the later experiment (item 12)

#### 5.12.1 Repository tests (slice I-7; none exists now)

**Toolchain-free** tests run in the ordinary suite:

| ID | Test | Expected |
|---|---|---|
| T-L1 | *(refines R2 T-B13)* source structure: no `#include`; `envp` and `argv` strings are dereferenced only in `select.c`; `select.c` contains no `syscall`, no `asm`, no global and no `static` object; every `syscall` in `launch.c` uses a number from the §5.4 inventory; no function pointer; `_start` is the only symbol in `start.s`. *(D2-R1)* It also checks the source rules SR-1 … SR-6 of §5.14.3: `select.c` has no pointer-typed parameter written through and no assignment through a pointer; the `INVOCATION_ID` copy is 32 constant-index assignments; `rp11_main` is `noreturn`; every `exit_group` wrapper is followed by `__builtin_trap()`; no variable-length array, `alloca`, recursion or aggregate copy; and the non-inline function set equals the contract function set *(D2-R2)* Under the zero-`ret` form the rows naming `select.c` apply to `select.h`, and the following replace the D2-R1 text where they differ: the only `#include` in the three source files is the single `#include "select.h"` in `launch.c`; `select.h` contains no `#include`, `syscall`, `asm`, global or `static` object, and defines exactly the two selection functions, each `static inline __attribute__((always_inline))`; `start.s` contains no `call` and no `ret`, and its only transfer is one `jmp rp11_main`; `rp11_main` is the only non-inline C function; and SR-7 and SR-8 hold | as stated. **The docstring states that this checks source text, not the built image** |
| T-L2 | *(refines R2 T-B14)* drift: the C literals (path, vector, environment prefixes, grammar, status table, class lines) equal the Python contract module and `entry_environment.KEY_SETS["LB-2S"]` and `LITERALS` | equal |
| T-L3 | build definition: the flag vectors of §5.3.3 appear exactly in `build.sh`; the linker script contains the listed `ASSERT`s and `/DISCARD/`; `toolchain.lock` parses, and every field is present and well formed. *(D2-R1)* It also checks these properties. `build.sh` invokes only shell built-ins and the absolute tool paths named in the lock. It contains no glob, command substitution or external utility, and every tool argument is a relative path. `build_argv` in the lock equals R-2's vector. `build-root.manifest` parses, is sorted, and has an exclusion list in which every entry carries a reason. `/etc/ld.so.preload` is absent from it. *(D2-R2)* `build.sh` compiles only `launch.c`, assembles only `start.s` and `launch.s`, and links exactly `start.o` then `launch.o`; the listing is generated with options that print one instruction per line with its complete byte field and elide no zero block | as stated |
| T-L4 | *(amended D2-R1)* committed listing, **coarse text screen**: `_start` equals `e_entry`; no `%fs:` or `%gs:` operand; every `syscall` is preceded in its basic block by a load of `%eax` from the inventory; no `int $0x80` or `sysenter`; the `.rodata` dump contains exactly the literal strings. **It is not the control-flow check.** That is T-L10. The D2 row's "no indirect `call` or `jmp`" is subsumed by T-L10's closed instruction list. *(D2-R2)* It is a text screen over the listing's spelling only, and relies on no decoding claim | as stated |
| **T-L10** *(new D2-R1, amended D2-R2)* | **control-transfer and stack verifier** over the committed listing: a pure-Python, standard-library program that applies §5.14.1 and RI-1 … RI-6 mechanically. *(D2-R2)* Its input is the normalised instruction stream parsed from the listing, which T-L11 shows is identical, field by field, to XD's stream decoded from the image bytes: **the agreed stream**. It shares no decoding or parsing code with XD. **Its verdict is accepted as evidence only together with a passing T-L11 over the same listing digest and an image whose digest equals `expected.sha256`**; a T-L10 pass without that is not evidence of anything about the image. It emits the function table, the per-instruction `%rsp` offset, the store table (each store mapped to a frame slot), the call graph and the maximum stack depth. It checks all of them against the contract data serialised in the manifest. It fails on any instruction outside the permitted list, any violated rule, or any difference from the contract data | all rules hold, and the emitted function set and stack depth agree with the contract data. The emitted tables are kept as review evidence for HR-1 … HR-6. **The docstring states that it checks the listing text, not the kernel (D9-1), that T-L7 ties that text's bytes to the binary, and that T-L11 — not T-L7 or T-L9 — ties its decoding to the binary** *(amended D2-R2)* |
| **T-L12** *(new D2-R2)* | **XD self-test**, toolchain-free: XD over a committed corpus of hand-encoded byte sequences, each citing its manual section (XD-10). Positive vectors cover every row of XD's closed table; negative vectors cover every forbidden form of §5.14.1, every XD-5 failure class and an injected ambiguous table. The corpus and its expected outputs are written from the manuals, not from `objdump` output | every positive vector decodes to its expected instruction; every negative vector fails with its expected XD-5 class. **The docstring states that this tests XD against its author's reading of the manuals, not the manuals themselves (AD-14)** |

**Toolchain-dependent** tests run only where the M-14 implementation
authority provisions the pinned toolchain. Elsewhere each **skips with an
explicit reason**, and the skips are counted and reported under AGENTS.md's
"Running the suites". They are never presented as passes.

| ID | Test | Expected |
|---|---|---|
| T-L5 | build once (R-2) | the image digest equals `expected.sha256` |
| T-L6 | *(amended D2-R1)* the three R-4 variations: checkout path; time and modification times; build user and host name | identical image, map, listing and `.s` digests |
| T-L7 | a pure-Python ELF parser (standard library `struct` only) applies BI-1 … BI-5 to the built image. *(D2-R1)* It also checks that the concatenated instruction bytes of the committed listing equal the image's `.text` bytes exactly, so that the listing T-L10 checks cannot omit or add a byte (BI-10). *(D2-R2)* **That is byte equality only.** It shows nothing about where instructions begin, what they are, or where they transfer: those are the listing's decoding, which T-L11 checks | all pass |
| T-L8 | *(refines R2 T-B15; narrowed D2-R2, LD-7)* `select_harness`, linked with `select_shim.o`, which is compiled from the **same `select.h` source** with the image's exact compile vector and the pinned compiler, runs the §5.6 case table and a generated corpus, and its results are compared with a Python reference model. **What it establishes:** that the two selection functions, as written in the committed `select.h` and as compiled by the pinned compiler under the image's flags into a separate, non-inlined context, return the reference model's result for every vector tried. **What it does not establish:** anything about the instructions inlined into `rp11_main`, whose register allocation and scheduling differ; anything about the image's object bytes; or anything about the installed image. It is **source and compiler behavioural evidence and does not replace inspection of the installed image** (LD-7). The selection code in the image is covered by the listing review (HR-4) over the agreed stream (T-L11, T-L10). *The D2-R1 row, which linked the same `select.o` bytes as the image, is withdrawn* (Appendix D) | identical for every vector. **It tests the selection source and compiler, not the image or the loader** |
| T-L9 | regenerate the listing with the pinned binutils | byte-equal to the committed listing. *(D2-R2)* This is an **identity** check of the pinned tools, not a check of their decoding (§5.3.1, §5.3.8) |
| **T-L11** *(new D2-R2)* | **decoding agreement**: XD decodes the built image's `.text` from the image bytes (XD-1 … XD-5), and its stream is compared with the stream parsed from the committed listing on every instruction boundary, byte field, mnemonic, operand and direct target (XD-6). T-L10 is then re-run over XD's own stream | the streams are identical instruction for instruction, with equal counts; XD reports no XD-5 failure; T-L10 over XD's stream produces a verdict and tables identical to T-L10 over the listing. **Any disagreement is a stop**, never resolved by preferring either decoder (§4.5). The record carries the image, listing, XD source and spelling-table digests, the agreed-stream digest and the interpreter version (XD-8) |

#### 5.12.2 Binary inspection (D9-2)

Performed on the built image, in the build environment, by the implementer,
and **repeated independently by the reviewer**:

| # | Check |
|---|---|
| BI-1 | ELF header: `ELFCLASS64`, `ELFDATA2LSB`, OS ABI `SYSV`, `ET_EXEC`, `EM_X86_64`, and `e_entry` equal to the value of the symbol `_start` |
| BI-2 | program headers: exactly one `PT_LOAD` (read and execute) and one `PT_GNU_STACK` (read and write, not executable). **No `PT_INTERP`, `PT_DYNAMIC`, `PT_TLS`, `PT_NOTE`, `PT_GNU_PROPERTY`, `PT_GNU_RELRO` or `PT_GNU_EH_FRAME`**, and no writable loadable segment |
| BI-3 | sections: only `.text`, `.rodata`, `.symtab`, `.strtab` and `.shstrtab`. None of `.interp`, `.dynamic`, `.dynsym`, `.rela.*`, `.got*`, `.plt*`, `.init`, `.fini`, `.init_array`, `.fini_array`, `.preinit_array`, `.ctors`, `.dtors`, `.tdata`, `.tbss`, `.data`, `.bss`, `.eh_frame*`, `.note*` or `.comment` |
| BI-4 | symbols: none undefined; no `STT_GNU_IFUNC` and no `STT_TLS`; `_start` global |
| BI-5 | no relocation section of any kind |
| BI-6 | *(rewritten D2-R1, amended D2-R2)* disassembly: complete; every instruction is in the permitted list of §5.14.1, and every control transfer belongs to CT-1 … CT-9; *(D2-R2)* **no `call` and no `ret` in any form**; no `%fs`/`%gs` operand; the `syscall` sites and their numbers equal the §5.4 inventory, with `open`, `openat`, `mmap`, `brk`, `arch_prctl`, `set_tid_address`, `rseq`, `getrandom`, `rt_sigreturn` and every other number absent; every `exit_group` site is followed immediately by `ud2`. *(D2-R2)* Every one of these properties is judged over the **agreed stream**: the instruction boundaries, mnemonics and operands come from the listing only where XD, decoding the image bytes independently, agrees exactly (T-L11). **Mechanical: XD and T-L11, then T-L10.** *The D2 text's inference "no indirect `call` or `jmp`, so the control-flow graph is fully determined" is withdrawn* (Appendix C). It is replaced by BI-10, BI-11, §5.14 and §5.15 |
| BI-7 | *(amended D2-R1, D2-R2)* data flow: the `envp` pointer passes from `_start` to `rp11_main`, and within `rp11_main` only to the inlined `rp11_select_invocation_id` code, and is dereferenced nowhere else. Nothing reads the stack above `envp`'s terminator, which is where the auxiliary vector lies. Every load through an `argv` or `envp`-derived pointer lies in the inlined selection code or is one of the 32 copy loads, and respects the §5.6 bounds. *(D2-R2)* Because the selection functions are inlined, no symbol boundary marks that code: HR-4 attributes each such load from T-L10's load table over the agreed stream. **Human review, HR-4 and HR-6, supported by T-L10's load table** |
| **BI-10** *(new D2-R1, amended D2-R2)* | function tiling, decoding and targets (RI-1 … RI-3). The function set is exactly `_start` and `rp11_main`, with no compiler-created symbol. `.text` begins at `_start`, and the two function ranges tile it exactly. The listing's instruction bytes equal `.text` (T-L7). *(D2-R2)* XD decodes every byte of `.text` into exactly one instruction under its closed table, with no ambiguity, unsupported encoding, undecoded byte, overlapping decode or unreached instruction, and its stream agrees exactly with the listing (XD-2 … XD-6, T-L11). Every CT-2 and CT-3 target is an instruction start inside the same function; the single CT-4 `jmp` targets `rp11_main`'s first instruction; no target lies outside `.text`. Every function ends in an unconditional transfer or `ud2`. **The image contains no `call` and no `ret`.** *The D2-R1 text's "linear-sweep decoding leaves no undecodable byte", which rested on the listing's own decoding, is superseded by XD* (Appendix D). **Mechanical: T-L7, XD, T-L11 and T-L10** |
| **BI-11** *(new D2-R1, amended D2-R2)* | stack offset and store discipline (RI-4 … RI-6). The static `%rsp` offset is consistent at every join and never negative. *(D2-R2: the D2-R1 condition "zero at every `ret`" is vacuous and withdrawn, because no `ret` exists.)* Every memory store other than `push` is a constant-displacement `%rsp` store inside the current frame. No inventory system call is given a user-memory output pointer. The maximum stack depth is within the 1 KiB bound. **Mechanical: T-L10 over the agreed stream. Human review: HR-1 … HR-3 and HR-5** |
| BI-8 | the linker map names exactly *(amended D2-R2)* `start.o` and `launch.o`, in that order, with no archive member and no linker-provided input |
| BI-9 | the size of `.text` is under 4 KiB, a review-feasibility bound, not a security property |

*(amended D2-R1, D2-R2)* BI-1 … BI-6, BI-10 and BI-11 are mechanical (T-L4,
T-L7, XD, T-L11, T-L10). *(D2-R2)* The decoding they rest on is not the
disassembler's alone: it is accepted only where XD agrees exactly (§5.15), and
Codex independently decodes the actual `.text` at D9-2 (XD-11). The **human
review of the listing** (HR-1 … HR-6, §5.14.4) covers three things:

* confirming that the verifier's function, frame-slot, store and load tables
  mean what the source intends;
* BI-7's load bounds; and
* the literal-to-register data flow into `execve`.

That review remains the residual risk of this design (§8). *The D2 sentence
that made "BI-6's reachability" a human judgement is withdrawn* (Appendix
C): reachability is now fixed mechanically by CT and RI, *(D2-R2)* over the
agreed stream.

#### 5.12.3 Reproducibility checks (D9-3)

R-1 … R-5 of §5.3.5. R-5, the independent rebuild, is required before H-1.
*(D2-R1)* IC-1 (§5.3.7) is also part of D9-3. It is run in I-7, and again
after any change to the lock or the manifest. *(D2-R2, LD-8)* D9-3 passes
only if IC-1 has passed for the current lock and manifest, R-5 records an
actual variation of at least one of HA-1 … HA-3, and no difference is
unexplained. **D9-3 is not evidence that any decoder is correct**: that is
D9-2's XD and XD-11 evidence (§5.15).

#### 5.12.4 The later hostile-environment experiment (corroboration only) *(rewritten D2-R1)*

**Separately authorized, never by this assignment.** It needs three things:

* a disposable host whose architecture is `x86_64`, running Linux 5.9 or
  later;
* unprivileged user and mount namespaces; and
* the built image, with a digest equal to `expected.sha256`.

**Limits every vector must respect** (AE-1 … AE-5). Values are for 4 KiB
pages. The supervisor recomputes them for the recorded page size.

| Quantity | Value |
|---|---|
| per-string limit `S` (AE-1) | 131 072 bytes, NUL included |
| aggregate limit `L` (AE-2), with the soft `RLIMIT_STACK` that the supervisor sets to exactly 8 MiB | 2 097 152 bytes |
| pointer charge `P` (AE-3) | `(max(argc, 1) + envc) × 8` bytes |
| **headroom rule HD-1** | every `argv` and `envp` string ≤ 98 304 bytes, NUL included (75 % of `S`) |
| **headroom rule HD-2** | the sum of all string bytes, NULs included, plus `P`, ≤ 524 288 bytes (25 % of `L`) |

Before each `execve` the supervisor computes HD-1 and HD-2, records them with
the case and asserts them. A failed assertion is a **test-definition error**,
and the case is not run. The kernel release, page size, soft and hard
`RLIMIT_STACK` and strace version are recorded once for each run.

**Harness.**

* **Tracer.** `strace -f -v -s 4096 -o ⟨trace⟩`, started with a literal
  environment. It never receives a case's vector.
* **Supervisor.** A test-owned program, also started with a literal
  environment. For each case it does the following:
  * enters a private user and mount namespace;
  * mounts an empty `tmpfs` over `/usr/bin`, so that `/usr/bin/python3.12`
    does not exist (Method A), or bind-mounts the recorder there (Method B).
    Test libraries and marker directories live outside `/usr/bin`;
  * sets the soft `RLIMIT_STACK` to 8 MiB;
  * sets descriptor 0 to `/dev/null`, read-only, and descriptors 1 and 2 to
    two separate pipes that it drains. This is the **usable-descriptor-2
    default** of §5.9;
  * sets every signal disposition to default, an empty mask, `umask 022` and a
    test directory as working directory, unless the case says otherwise;
  * creates an `O_CLOEXEC` pipe on a descriptor ≥ 3; and
  * forks the child.
* **Child.** It applies any case-specific state last: closing a descriptor,
  ignoring or blocking signals, or installing a `seccomp` filter under
  `no_new_privs`. It then calls
  `execve(⟨image⟩, ⟨case argv⟩, ⟨case envp⟩)` directly, with no further fork.
  **The case's vector exists only as the arguments of that call.** It is never
  in the environment of the tracer, supervisor or child, so a hostile
  `LD_PRELOAD` cannot load into any harness process. If the `execve` returns,
  the child writes `E` and the `errno` value to the pipe and calls `_exit(90)`.
  Status 90 lies outside 110 … 119.

**Establishing that `rp11-launch` was entered: EN-1 … EN-3, all required.**

| # | Evidence |
|---|---|
| EN-1 | the supervisor reads the `O_CLOEXEC` pipe to end-of-file with **zero** bytes. Any byte is **`DRIVER-EXEC-FAILED`**, with the recorded `errno` (for example `E2BIG`). That is a harness or test-definition failure, **never a launcher result**, and the case is invalid |
| EN-2 | in the child's process ID, the trace shows `execve("⟨image⟩", …) = 0` |
| EN-3 | that process's next system calls are exactly the case's golden sequence below, from its first call to its last |

A successful supervisor return, or a child exit status in 111 … 117, is
**never** by itself evidence that the launcher was entered or behaved
correctly.

**Golden sequences.** In every sequence, `W(c, n)` stands for
`write(2, "rp11-launch/1: c\n", n) = n`, which is the result required when
descriptor 2 is usable. `SIGS` stands for 62 calls, one for each signal `s`
from 1 to 64 except 9 and 19, in ascending order:
`rt_sigaction(s, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, NULL, 8) = 0`.
`STDIO` stands for `fcntl(0, F_GETFD) = 0`, `fcntl(1, F_GETFD) = 0`,
`fcntl(2, F_GETFD) = 0`. `EXEC` stands for:

```
execve("/usr/bin/python3.12",
       ["/usr/bin/python3.12", "-I", "-S",
        "/usr/local/libexec/freedom-blades-rp11/rp11_entry.py",
        "run", "--pass", "A"],
       ["LC_ALL=C", "PATH=/usr/bin", "INVOCATION_ID=⟨the case's 32 bytes⟩"])
```

| Name | Sequence after EN-2 |
|---|---|
| **G-OK** | STDIO; `close_range(3, 4294967295, 0) = 0`; SIGS; `rt_sigprocmask(SIG_SETMASK, [], NULL, 8) = 0`; `umask(077)`; `chdir("/") = 0`; EXEC `= -1 ENOENT`; `W(launch-exec-failed, 34)`; `exit_group(117)` |
| **G-111** | `W(launch-usage, 28)`; `exit_group(111)` |
| **G-112** | `W(launch-invocation-id, 36)`; `exit_group(112)` |
| **G-113(k)**, for k = 0, 1 or 2 | `fcntl(j, F_GETFD) = 0` for each j < k; `fcntl(k, F_GETFD) = -1 EBADF`; then `W(launch-stdio, 28)` if k ≠ 2, or `write(2, "rp11-launch/1: launch-stdio\n", 28) = -1 EBADF` if k = 2; `exit_group(113)` |
| **G-114** | STDIO; `close_range(3, 4294967295, 0) = -1 EPERM`; `W(launch-descriptors, 34)`; `exit_group(114)` |
| **G-115a(s)** | STDIO; `close_range(…) = 0`; the SIGS calls for every signal below `s`, each `= 0`; `rt_sigaction(s, …) = -1 EPERM`; `W(launch-signals, 30)`; `exit_group(115)` |
| **G-115b** | STDIO; `close_range(…) = 0`; SIGS; `rt_sigprocmask(…) = -1 EPERM`; `W(launch-signals, 30)`; `exit_group(115)` |
| **G-116** | STDIO; `close_range(…) = 0`; SIGS; `rt_sigprocmask(…) = 0`; `umask(077)`; `chdir("/") = -1 EPERM`; `W(launch-chdir, 28)`; `exit_group(116)` |
| **G-117(e)** | as G-OK, with EXEC `= -1 e` |

**Any other system call, any change of order, a missing `write`, or a `write`
whose bytes or result differ fails the case.** In particular, the start-up of
any C library would show `brk`, `mmap`, `arch_prctl`, `set_tid_address`,
`set_robust_list`, `rseq`, `prlimit64` or `getrandom`.

**Cases.**

| # | Input and state | Expected |
|---|---|---|
| HX-1 | argv `⟨any⟩ --pass A`; `envp` = exactly one valid `INVOCATION_ID` | EN-1 … EN-3 with G-OK |
| HX-2 | HX-1 plus these hostile entries: `LD_PRELOAD` and `LD_AUDIT` naming test libraries whose constructors would create a marker file; `LD_LIBRARY_PATH`; `GLIBC_TUNABLES`; `MALLOC_*`; `LANG`/`LC_*`; `LOCPATH`; `NLSPATH`; `GCONV_PATH`; `TZ`; `HOSTALIASES`; `RES_OPTIONS`; `PYTHON*`. Each is ≤ 256 bytes | G-OK; EXEC's environment is the three-entry literal; **no marker file exists** in the test-owned marker directory after the child exits |
| HX-3a | **long entries:** the valid `INVOCATION_ID`, plus three entries of 98 304 bytes each, NUL included: `LD_LIBRARY_PATH=` followed by filler; `LONG=` followed by filler; and one of the same length with no `=`. Run three times, with the valid entry first, in the middle and last. Aggregate about 295 000 bytes, about 14 % of `L` | G-OK in each run |
| HX-3b | **many entries:** the valid `INVOCATION_ID`, plus 10 000 entries of exactly 40 bytes each, NUL included, of the form `E⟨5 digits⟩=⟨filler⟩`. Run with the valid entry first, in the middle and last. `envp` string bytes 400 047, plus `argv` strings of under 100 bytes, plus `P` = (3 + 10 001) × 8 = 80 032. The total is under 480 200: within HD-2's bound of 524 288, and about 22.9 % of `L` | G-OK in each run |
| HX-3c | **malformed entries:** the valid `INVOCATION_ID`, plus 256 entries of 63 bytes with no `=`, 256 empty entries (a lone NUL), and 256 entries of 63 bytes drawn from 0x80 … 0xFF that include invalid UTF-8 sequences, each followed by NUL. Run with the valid entry first, in the middle and last. Aggregate about 39 000 bytes | G-OK in each run |
| HX-3d | **near-name entries,** each ignored under §5.6: `INVOCATION_IDX=⟨32 hex⟩`, `invocation_id=⟨32 hex⟩`, ` INVOCATION_ID=⟨32 hex⟩`, `INVOCATION_I=⟨32 hex⟩` and `INVOCATION_ID` followed by byte 0x80, `=` and 32 hex digits. Plus one valid `INVOCATION_ID` whose digits differ from all of these | G-OK. EXEC carries the valid entry's digits |
| HX-4 | each §5.6 refusal, with valid argv: no `INVOCATION_ID`; two identical valid entries; two different valid entries; a bare `INVOCATION_ID`; one valid entry and one bare entry; an empty value; 31 digits; 33 digits; an uppercase digit; a non-hexadecimal byte | G-112 in every case. No `fcntl` or later call appears |
| HX-5 | each §5.5 refusal, run once with a valid `INVOCATION_ID` and once with none, which shows that S-1 precedes S-2: `argc` 0 (seen as `argc` 1 on Linux 5.18 and later, AD-13); `⟨x⟩`; `⟨x⟩ --pass`; `⟨x⟩ --pass B`; `⟨x⟩ --pass=A`; `⟨x⟩ --PASS A`; `⟨x⟩ --pass AA`; `⟨x⟩ --pass ""`; `⟨x⟩ --pass A extra` | **G-111** in every case: the `launch-usage` line, then `exit_group(111)`. *The D2 row's bare `exit_group(111)` is withdrawn* (Appendix C) |
| HX-6 | Method B. Inherited state: descriptors 3 … 1000 open (the supervisor raises the soft `RLIMIT_NOFILE` to at least 1024 and records it); `SIGPIPE` and `SIGINT` ignored; every blockable signal blocked; `umask 000`; a non-root working directory | the trace matches G-OK up to EXEC, which now returns 0, followed by the recorder's own calls. The recorder observes: no descriptor above 2; no ignored, blocked or caught signal; `umask` `0077`; working directory `/`; argv and environment equal to the literals |
| HX-7a … HX-7c | valid argv and `envp`; descriptor k closed in the child, for k = 0, 1, 2 respectively | **G-113(k)**. *The D2 row, "descriptor 1 or 2 closed → `exit_group(113)`" without the write and without descriptor 0, is withdrawn* (Appendix C) |
| HX-7d | descriptor 2 closed, with a §5.5 refusal | `write(2, "rp11-launch/1: launch-usage\n", 28) = -1 EBADF`; `exit_group(111)`. The write is still attempted |
| HX-7e | descriptor 2 a pipe with no reader, `SIGPIPE` ignored, with a §5.5 refusal | `write(…, 28) = -1 EPIPE`; `exit_group(111)` |
| HX-7f | as HX-7e, with `SIGPIPE` at its default | the `write` is attempted, and the trace ends with the process killed by `SIGPIPE`. No `exit_group` and no `execve` follow. It is recorded as an **interruption** (§5.10), not as a launcher status |
| HX-8a | a `seccomp` filter returns `EPERM` for `close_range` | G-114 |
| HX-8b | a `seccomp` filter returns `EPERM` for `rt_sigaction` whose first argument is `s`, for s = 1, 32 and 64 in separate runs | G-115a(s) |
| HX-8c | a `seccomp` filter returns `EPERM` for `rt_sigprocmask` | G-115b |
| HX-8d | a `seccomp` filter returns `EPERM` for `chdir` | G-116 |
| HX-9a … HX-9c | the interpreter path is absent (Method A); present but not executable; or present with an unrecognised format | G-117(ENOENT), G-117(EACCES) and G-117(ENOEXEC) respectively |

In HX-8 the filter is **test state** installed by the child just before the
`execve`, to reach the failure branches. It is not a claim about manager
settings, which remain R-10 trust. Every filter allows every other system
call.

**Environment content.** Every vector is synthetic. The tracer and supervisor
start with literal environments, and the trace records no host environment
(K-6).

**What it cannot show.** It observes one binary, on one kernel, at one time,
for the inputs tried. It does not test systemd, the executor (PO-14) or the
manager's environment (PO-16). The exact golden sequences and entry evidence
make each case's result attributable to `rp11-launch`. **They do not make the
experiment a proof. It is corroboration. No record may present it as the
proof of PO-9** (K-3).

### 5.13 Rollback and replacement (item 13)

| Change | Required action |
|---|---|
| **toolchain update** (a new package version or security fix) | The installed, reviewed image stays valid, because it was reviewed as a binary (§5.3.1). Nothing is urgent. A new pin is a covered-source change: rebuild (R-1 … R-5). If the image digest is unchanged, only the lock changes and is reviewed. If it changes, the listing diff is reviewed by Codex, the expected digest, manifest version and pass configuration are updated, and H-1 reinstalls |
| **runtime update** | not applicable: the image has no runtime, so no library update ever requires a rebuild |
| **kernel update** | H-2 stops the pass on a changed kernel release. The maintainer re-establishes PO-18, PO-17 and D9-1's kernel citation for the new series, and writes a new H-1 record. No rebuild. A kernel older than 5.9, or confinement that denies `close_range`, fails closed at S-4 |
| **systemd update** | outside this image. PO-14 is re-cited for the new version (R2). H-1 records the systemd version |
| **architecture change** | the `x86_64` image cannot start (`ENOEXEC`); systemd fails the unit: fail-closed. A new architecture needs a new entry stub, a new system-call table and a new pin. **That is a design change requiring its own review**, not a rebuild |
| **defect in the launcher** | fixed in reviewed source as `rp11-launch/1` if the contract is unchanged, or as `rp11-launch/2` if it changes, followed by the full chain above |
| **roll back an installation** | under H-1's authority: remove the installed image, together with the other R2 §4.4.3.7 files, and run `systemctl daemon-reload` |
| **roll back to a previous image** | reinstall the previous image, whose digest and listing remain in Git history, and restore the matching pass configuration. Both values are in the previous H-1 record |
| **emergency disable** | remove the polkit rule or the unit. No entry process can then exist |

Every rollback is an ordinary change. None is a history rewrite.

### 5.14 Control transfer and stack-write discipline (*new D2-R1, amended D2-R2*; premises P-3 … P-5)

A complete disassembly lists every instruction byte. It does **not** by
itself give the reachable control-flow graph. The graph also needs three
things:

1. every control-transfer class that can occur is known;
2. every direct target is an instruction start inside listed code; and
3. the target of every transfer taken from machine state is justified. That
   includes the integrity of the memory it is read from.

*(amended D2-R2, LD-7)* **In the selected zero-`ret` form, the image has no
transfer that takes its target from machine state.** There is no `ret`, no
`call`, and no indirect `call` or `jmp`. Item 3 is therefore satisfied by
absence, and the graph depends only on items 1 and 2: on the instruction
boundaries and encoded targets being decoded correctly. §5.15 establishes
that decoding independently of the disassembler. The D2 text relied on the
absence of indirect `call` and `jmp` alone, which was `R4-D2-1`. The D2-R1
text permitted `ret` under a return-integrity discipline; that permission is
**withdrawn** (Appendix D), and restoring it needs a new maintainer decision.

**The contract function set** *(amended D2-R2)* is `_start` (`start.s`) and
`rp11_main` (`launch.c`). Every other function, the two selection functions
of `select.h` and the system-call wrappers included, is
`static inline __attribute__((always_inline))` and must not appear as a
symbol.

#### 5.14.1 Permitted control transfers (closed)

| # | Class | Form | How the target is fixed |
|---|---|---|---|
| CT-1 | fall-through | any permitted non-transfer instruction | the next instruction in the same function. RI-3 forbids falling off a function's end |
| CT-2 | direct conditional branch | `jcc` with an 8- or 32-bit displacement | the encoded displacement. It must be an instruction start inside the same function (BI-10). *(D2-R2)* The displacement, the instruction's length and hence the target are those XD decodes from the bytes and the listing agrees with (T-L11) |
| CT-3 | direct unconditional jump | `jmp` with an 8- or 32-bit displacement | as CT-2. **No jump leaves its function**, *(D2-R2)* apart from the single CT-4 entry `jmp`, so tail calls do not exist |
| CT-4 | *(replaced D2-R2)* **the entry transfer** | exactly one direct `jmp` with an 8- or 32-bit displacement, located in `_start` as its last instruction | the encoded displacement, as decoded by XD and agreed (T-L11). The target must be the first instruction of `rp11_main`. No other instruction transfers between functions. *The D2-R1 row, "direct call … the entry of a listed function other than `_start`", is withdrawn* (Appendix D). **No `call` in any form exists in the image** |
| CT-5 | *(withdrawn D2-R2, LD-7)* **none: return is absent** | — | **no `ret` in any form exists in the image.** No instruction takes its target from the stack. *The D2-R1 row, which permitted `ret` (opcode `c3`) under RI-4 … RI-7 and expected it in the two `select.c` leaves, is withdrawn* (Appendix D). The row is kept so that the class numbering CT-1 … CT-9 is stable |
| CT-6 | system call | `syscall` | returns to the next instruction (AD-12) for `fcntl`, `close_range`, `rt_sigaction`, `rt_sigprocmask`, `umask`, `chdir`, `write` and a failed `execve`. A successful `execve` leaves the image, which is the intended end. `exit_group` does not return, and is followed immediately by `ud2` (RI-3) |
| CT-7 | trap | `ud2` | the forced `SIGILL` terminates the process with no user-space code (AD-11) |
| CT-8 | synchronous fault | any faulting instruction, for example a page fault from a bad read or from stack exhaustion | as CT-7 (AD-11) |
| CT-9 | asynchronous signal | none | no handler can exist. After `execve` every disposition is default or ignore (AD-8), and the image installs only `SIG_DFL` (S-5). Delivery terminates, stops or is discarded. A stop followed by a continue resumes at the interrupted instruction |

**Forbidden, and failing T-L10:**

* any indirect `call` or `jmp`, through a register or memory;
* *(D2-R2)* **every `ret`**: `c3`, `c2 iw`, and either with any prefix,
  including `f3 c3` and `f2 c3`; **every `call`**, including direct `e8`;
  far `call`, `jmp` and `ret`; and `iret` in every form;
* *(D2-R2)* every `jmp` that is not an intra-function CT-3 or the single CT-4
  entry transfer;
* `int n`, `int3`, `int1` and `into`; `sysenter`, `sysexit` and `sysret`;
* `loop` in every form, `jrcxz` and `jecxz`;
* `xbegin`, `xabort` and `xend`, because a transactional abort transfers
  control to a fallback address;
* `enter` and `leave`, and every string instruction, with or without a `rep`
  prefix;
* `endbr64`, `hlt` and every privileged instruction;
* any `%fs` or `%gs` operand; and
* **any instruction not on the permitted instruction list.**

The permitted non-transfer list is: integer `mov` and its zero- and
sign-extending forms, `lea`, `add`, `sub`, `and`, `or`, `xor`, `cmp`, `test`,
`inc`, `dec`, `neg`, `not`, the shifts, `setcc`, `cmovcc`, `push`, `pop`, the
`nop` forms, `syscall` and `ud2`. The exact list is contract data, fixed in
I-7 from the first build and reviewed. Adding to it is a reviewed contract
change. `_start` alone may also execute `and $-16, %rsp` (RI-4).

*(D2-R2)* **The permitted transfer forms are therefore exactly:** `jcc` and
`jmp` with 8- or 32-bit displacements, `syscall` and `ud2`. The list is
stated as **encodings**, not only mnemonics, in XD's closed table (§5.15,
XD-3), which must accept exactly the forms on these two lists and reject
everything else. A mnemonic on the list whose encoding XD's table does not
contain fails, and must be added by a reviewed contract change to both.

*(D2-R2)* **Why a `c3` byte elsewhere is not a `ret`.** The byte `c3` can
occur inside another instruction, for example in a displacement or an
immediate. It is a `ret` only at an instruction start. The zero-`ret` claim is
therefore a claim about the **decoded** instruction starts, and it is only as
good as the decoding. XD fixes those starts independently, rejects any
reachable position that is not one of them (overlap), and rejects any target
that lands inside an instruction (XD-5). That is why the zero-`ret` form and
independent decoding are one remediation.

#### 5.14.2 Structural and stack rules, RI-1 … RI-7 *(retitled and amended D2-R2; D2-R1 title "Return integrity")*

*(D2-R2)* The rule numbers are kept so that references stay stable. Under the
zero-`ret` form RI-1 … RI-4 fix the structure that makes every target
encoded; RI-5 and RI-6 now protect **data**, not control; and RI-7's return
argument is withdrawn because nothing returns.

| # | Rule | Checked by |
|---|---|---|
| RI-1 | **Function set.** *(amended D2-R2)* The image's function symbols are exactly `_start` and `rp11_main`. No compiler-created symbol exists, such as `.cold`, `.part.N`, `.constprop.N`, `.isra.N`, a thunk, an out-of-line copy of a selection function, or a `memcpy` or `memset` reference | T-L10; BI-4; BI-10; *(D2-R2)* XD reads the symbol table itself (XD-1) |
| RI-2 | **Tiling and decoding.** *(rewritten D2-R2)* `.text` begins at `_start`, which equals `e_entry`, and `_start`'s range is followed immediately by `rp11_main`'s; the two ranges tile `.text` exactly, with no gap. **XD** decodes every byte of `.text` from `_start` into exactly one instruction of its closed table, with no ambiguity, unsupported encoding, undecoded byte, overlapping decode or unreached instruction (XD-2 … XD-5). The listing's bytes equal `.text` (T-L7), **and** its boundaries, mnemonics, operands and targets equal XD's (T-L11). Every CT-2 and CT-3 target is an instruction start in the same function; the CT-4 target is `rp11_main`'s first instruction; no target lies outside `.text`. In particular no target lies in `.rodata`, which shares the executable `PT_LOAD` segment. *The D2-R1 rule, which took the decoding from the listing's own linear sweep, is superseded* (Appendix D) | T-L7; **XD; T-L11**; T-L10 |
| RI-3 | **Terminal instructions.** *(amended D2-R2)* `_start`'s last instruction is the CT-4 `jmp`. `rp11_main`'s last instruction, and the last instruction of `.text`, is `ud2` or an intra-function `jmp`. Every `exit_group` `syscall` is followed immediately by `ud2`. **No function contains `ret` or `call`.** `rp11_main` is `noreturn` | XD; T-L11; T-L10; T-L1 (source) |
| RI-4 | **Stack offset.** *(amended D2-R2)* Let `o(i)` be the number of bytes by which `%rsp` at instruction `i` of `rp11_main` lies below its value at `rp11_main`'s entry. At entry, `%rsp` points at the zero word `_start` pushed. `o(i)` is computed by abstract interpretation over `rp11_main`'s graph, which CT-1 … CT-3 fix. Only `push`, `pop`, `sub $imm, %rsp` and `add $imm, %rsp` change `%rsp` in `rp11_main`; `_start` alone uses `and $-16, %rsp` and one `push $0`. `o` agrees at every join and is never negative. There is no frame pointer (`%rbp` is a general register), no `call` and no recursion. The maximum depth, `_start`'s alignment and pushed word included, is at most **1 KiB**. *The D2-R1 conditions "`call` (with net effect zero on return)" and "0 at every `ret`" are withdrawn as vacuous* (Appendix D) | T-L10 over the agreed stream |
| RI-5 | **Store discipline.** Every instruction that writes memory, apart from the implicit store of `push`, has a memory operand `disp(%rsp)`, with a constant `disp` and no index register, satisfying `0 ≤ disp` and `disp + width ≤ o(i)`. **The slot lies wholly inside `rp11_main`'s frame, strictly below the entry slot that `_start` pushed.** There is no store through any other base register, no indexed store and no RIP-relative store, and the image has no writable segment in any case. *(D2-R2)* **Purpose:** the frame's literals, the `INVOCATION_ID` buffer and the `execve` pointer arrays cannot be overwritten, and no store reaches the kernel-built argument area (P-5, IN-3). It is no longer needed for control integrity | T-L10; HR-1 |
| RI-6 | **No other writer.** No inventory system call is given a user-memory output pointer: `rt_sigaction`'s old-action argument and `rt_sigprocmask`'s old-set argument are `NULL`, `F_GETFD` takes no pointer, and `chdir`, `execve` and `write` only read user memory. No signal frame is ever pushed, because no handler exists (CT-9). No other thread or shared mapping exists, because `clone` and `mmap` are not in the inventory. A tracer is T-B or root, and out of scope (R2 R-7, R-10). *(D2-R2)* **Purpose:** as RI-5, data integrity | T-L10 (arguments); D9-1 (AD-8); HR-5 |
| RI-7 | **Conclusion.** *(replaced D2-R2)* **No reachable instruction takes a transfer target from a register or from memory.** Every transfer is CT-1 … CT-4 with an encoded target, or CT-6 … CT-9, whose behaviour the cited kernel semantics fix. So the graph is determined by the decoded instruction bytes alone, and it is correct if the decoding is correct (RI-2, AD-14). *The D2-R1 conclusion, that every reachable `ret` returns to the instruction after its matching `call`, is withdrawn: no `ret` exists* (Appendix D) | follows from RI-1 … RI-3 and CT-1 … CT-9 |

**The reachable control-flow graph from `_start`** *(amended D2-R2)* is then
determined:

* `_start`'s straight-line code (CT-1);
* the single entry edge from `_start` to `rp11_main` (CT-4);
* `rp11_main`'s own graph (CT-1 … CT-3); and
* the terminal edges CT-6 … CT-9, whose behaviour AD-8, AD-11 and AD-12 fix.

There are no call or return edges. The graph is finite. T-L10 computes it over
the agreed stream, and XD's reachability pass computes the same set of
instruction starts independently (XD-2). **This, and not the absence of
indirect `call` and `jmp` alone, is premise P-4.**

#### 5.14.3 Source discipline, frame layout, and why hostile input cannot redirect control

**Source rules** (checked as text by T-L1; their effect on the binary is
checked by T-L10):

* **SR-1.** The non-inline function set equals the contract function set,
  *(amended D2-R2)* which is `_start` and `rp11_main` only.
  There is no function pointer and no recursion. No function takes more than
  six integer parameters, or takes or returns a structure, so no argument is
  passed on the stack.
* **SR-2.** `rp11_check_argv` and `rp11_select_invocation_id` perform no
  store through a pointer and have no out-parameter. They return an integer,
  or a pointer to the 32 validated bytes (or a null pointer). *(D2-R2)* They
  are defined in `select.h` as `static inline __attribute__((always_inline))`,
  so a failure to inline them is a compile error, not a silent call.
* **SR-3.** `rp11_main` writes its locals only at constant indices. It copies
  `INVOCATION_ID` only after validation has succeeded, as 32 written-out
  assignments `idbuf[14 + k] = id[k]` for k = 0 … 31. No loop writes memory.
* **SR-4.** `rp11_main` is `noreturn`. Every exit is the inline `exit_group`
  wrapper followed by `__builtin_trap()`. *(D2-R2)* `rp11_main` has no path
  that reaches its closing brace, so the compiler has no reason to emit a
  `ret`; whether it emitted one is decided only by XD, T-L11 and T-L10.
* **SR-5.** There is no variable-length array, no `alloca`, no aggregate
  assignment and no aggregate initialiser. Locals are set by explicit scalar
  assignments, so that nothing lowers to `memcpy` or `memset`.
* **SR-6.** Every system-call wrapper passes `NULL` for each output pointer.
* **SR-7** *(new D2-R2)*. `start.s` contains no `call` and no `ret`. Its only
  transfer is one `jmp rp11_main`, its last instruction, preceded by
  `and $-16, %rsp` and `push $0`.
* **SR-8** *(new D2-R2)*. `select.h` contains only the two selection
  functions and their result codes, with no `#include`, `asm`, `syscall`,
  global or `static` object. `launch.c`'s single `#include "select.h"` is the
  only preprocessing include in the image source. The test shim includes the
  same file unchanged.

**Expected frame of `rp11_main`.** This table is the design; the listing's
actual offsets are what HR-1 reviews.

| Object | Size in bytes | Contents, all written at constant displacements |
|---|---|---|
| `idbuf` | 47, 48 with padding | 14 constant bytes `INVOCATION_ID=`; the 32 validated bytes (SR-3); a NUL |
| `argv_out[8]` | 64 | seven `.rodata` addresses and a null pointer |
| `envp_out[4]` | 32 | two `.rodata` addresses, the address of `idbuf` and a null pointer |
| `sa`, the kernel `sigaction` (handler, flags, restorer, mask) | 32 | four zero words; `SIG_DFL` is 0 |
| `mask` | 8 | zero |
| register spills and callee-saved `push`es | as the listing shows | RI-5 stores or `push` |

The design bound is a frame of at most 512 bytes for `rp11_main`, and a
maximum image depth of at most 1 KiB (RI-4). *(amended D2-R2)* The inlined
selection code is expected to add only register use and spills to
`rp11_main`'s frame.

**Expected listing shape** *(new D2-R2; a design expectation, not an
observation)*:

* `_start`: about eight instructions — `xor %ebp,%ebp`, the loads of `argc`,
  `argv` and `envp` into `%rdi`, `%rsi` and `%rdx`, `and $-16,%rsp`,
  `push $0`, and `jmp rp11_main` last;
* `rp11_main`: one function containing the S-1 … S-9 sequence with the
  selection loops inlined; no `call`; no `ret`; direct `jcc` and `jmp` only
  within it; each `syscall` preceded by a constant load of `%eax`; every
  `exit_group` `syscall` followed immediately by `ud2`, possibly through one
  shared exit tail reached by intra-function `jmp`s; and a `ud2` as the last
  instruction of `.text`;
* no other symbol, and `.text` of well under 4 KiB.

If the first build departs from this shape in a way that breaks a rule, FA-1
or FA-3 applies (§5.14.5). A departure that breaks no rule is reviewed and
recorded, not silently accepted.

**Why hostile `argv` and `envp` cannot redirect control:**

* **IN-1.** Input bytes enter registers only through loads. Those loads are in
  the selection code, *(amended D2-R2)* inlined into `rp11_main` from
  `select.h`, plus the 32 loads in `rp11_main` from the validated pointer.
* **IN-2.** Input affects control only through the outcomes of direct
  conditional branches (CT-2), whose targets are encoded in the instruction.
  *(D2-R2)* Under the zero-`ret` form no transfer anywhere reads a target from
  a register or memory (RI-7), so no input value can become a target even if
  it reached the stack.
* **IN-3.** **No store address, store count or stack adjustment depends on
  input.** Every store is at a constant displacement (RI-5). Every loop that
  reads input writes nothing (SR-2, SR-3). `%rsp` changes only by constants
  (RI-4).
* **IN-4.** The only input-derived bytes written to memory are the 32
  validated bytes. They are written at constant displacements into `idbuf`,
  and nothing in the image branches on them afterwards. Only the kernel's
  `execve` reads them.

Very long or very many entries change only how many iterations the reading
loops make, within §5.6's bounds, and how much stack remains below the
argument area. If too little remains, the result is CT-8 termination.

#### 5.14.4 Mechanical and human evidence *(amended D2-R2)*

**Mechanical checks.** *(amended D2-R2)* In order:

1. **T-L7** ties the listing's instruction bytes to the image's `.text`, byte
   for byte. That is byte equality only.
2. **XD** decodes the image's `.text` from its bytes, independently of
   binutils, and **T-L11** requires its stream to equal the stream parsed from
   the listing on every boundary, byte field, mnemonic, operand and target
   (§5.15). **Until T-L11 passes, no T-L10 result is accepted.**
3. **T-L10** runs over the agreed stream and checks:
   * CT membership and the permitted instruction list, including the absence
     of every `call` and `ret`;
   * every direct target;
   * tiling and terminal instructions;
   * the `%rsp` offsets and the stack bound;
   * the store and load tables; and
   * the control-flow graph, which has no call or return edges.
4. **T-L9** ties the listing to the pinned binutils' output. That is an
   identity check, not a decoding check.

**Human review**, by the implementer and independently by the reviewer
(D9-2):

| # | Review |
|---|---|
| HR-1 | every entry of T-L10's store table maps to a named object in the frame table above and to a source assignment. No store slot is unexplained |
| HR-2 | the `INVOCATION_ID` copy occupies exactly the 32 contiguous slots at `idbuf + 14`. It is reached only on the path where validation succeeded. The prefix and the NUL are constants |
| HR-3 | `argv_out` and `envp_out` hold exactly the listed `.rodata` addresses and `idbuf`'s address. The `.rodata` strings equal the literals (T-L4 dump) |
| HR-4 | *(amended D2-R2)* every load through an `argv`- or `envp`-derived pointer is in the selection code inlined into `rp11_main`, or is one of the 32 copy loads, and respects §5.6's bounds (BI-7). Because inlining removes the symbol boundary, the reviewer attributes each such load from T-L10's load table and the data flow from `_start`'s `%rsi` and `%rdx`, not from a function range |
| HR-5 | at the `execve` site, `%rdi`, `%rsi` and `%rdx` hold the `.rodata` path, `argv_out` and `envp_out`. Every other system call's arguments equal the §5.7 values, and every output pointer is `NULL` (RI-6) |
| HR-6 | `_start` reads only `argc`, `argv` and `envp`. Nothing reads above `envp`'s terminator (BI-7) |

The human review confirms that the verifier's tables mean what the source
intends. **It does not decide reachability, which is mechanical.** T-L10 is
class-E tooling (X-16). A defect in it that accepted a violating listing would
be a common-mode failure of the mechanical layer. The reviewer's independent
re-derivation, and HR-1 … HR-6 applied to the raw listing, are the second
layer (§8). *(D2-R2)* **Decoding is not part of that human judgement either**:
it is XD's and T-L11's, with Codex's D9-2 decoding as its second layer
(XD-11).

#### 5.14.5 If the first build does not pass: fail-closed alternatives *(amended D2-R2)*

*(D2-R2, LD-7)* The zero-`ret` form is **the design**, not an alternative.
The first build is made in that form. If it fails XD, T-L11, T-L10 or HR-1 …
HR-6, the alternatives below are tried, each **within the zero-`ret` form**.
None of them is assumed to work. Each must pass XD, T-L11, T-L10 and HR-1 …
HR-6 under later authority.

| # | Alternative | What changes | Cost |
|---|---|---|---|
| FA-1 | **verified inlining and restructuring** | if a helper survives as a symbol, a compiler-created symbol appears, a `call` or `ret` appears, an instruction outside XD's closed table appears, or a store breaks RI-5, the source is restructured or the helper forced inline. The result is rebuilt and re-verified | none to the claim. Each change is a reviewed source change |
| FA-2 | *(superseded D2-R2)* **zero-`ret` image** — **now the selected design** (§5.1, §5.2, §5.14.1 … §5.14.3). *The D2-R1 row, which offered it as a fallback to a `ret`-permitting first build, is superseded* (Appendix D) | — | T-L8's narrowing is stated in §5.12.1 and accepted by LD-7 |
| FA-3 | **C-1A, pure assembly** | the same contract written in assembly, **in the zero-`ret` form**, under the same CT and RI rules and the assembly equivalents of SR-1 … SR-8. XD, T-L11 and T-L10 apply unchanged | as §4.3 C-1A |

**No return-based alternative exists.** A build that permits `ret` is not a
fail-closed alternative under this design: it requires a new, separately
reviewed maintainer decision (LD-7). If neither the first build nor FA-1 nor
FA-3 passes, **LB-2S is withdrawn** (§4.5). No alternative weakens PO-9.

### 5.15 Independent decoding, XD-1 … XD-11 *(new D2-R2; `R4-D2-R1-1`)*

**Why.** Under the zero-`ret` form every transfer target is encoded in the
instruction bytes, so the reachable graph is exactly as correct as the
decoding of those bytes. D2-R1 took that decoding from the pinned `objdump`:
T-L7 checked only that the listing's byte fields concatenate to `.text`, and
T-L10 reasoned over the listing's mnemonics and boundaries. A decoding error
common to the pinned binutils would reproduce into every listing, pass T-L7,
T-L9, T-L10, R-4 and R-5, and falsify RI-2, BI-6, BI-10, P-3 and P-4 without
any check failing. This section removes that single authority.

**XD** is a second decoder, implemented independently of binutils, whose
result must agree exactly with the committed listing before any T-L10
evidence is accepted.

#### 5.15.1 Requirements

| # | Requirement |
|---|---|
| XD-1 | **Input: the image bytes, not the listing.** XD reads the built image file itself with its own ELF reader (Python standard library `struct` only). From the ELF header, section headers and symbol table it takes `e_entry`, `.text`'s file offset, address and size, and the values and sizes of `_start` and `rp11_main`. It reads no listing, `objdump` or `readelf` output, uses no binutils library or opcode table, and shares no code with T-L7's parser or T-L10. Its section and symbol values must equal T-L7's and those in the listing's `readelf` tables: a three-way agreement |
| XD-2 | **Complete decoding from `_start`.** `_start` must equal `e_entry` and the first byte of `.text`. XD decodes by **linear sweep** from `_start` to the end of `.text`: every byte belongs to exactly one instruction, and the sweep ends exactly at the last byte. Independently, a **reachability pass** starts at `_start` and follows fall-through, every `jcc`'s two successors, every `jmp`'s target and every `syscall`'s fall-through (treated as always possible, whatever the number). Every position it reaches must be a sweep boundary, and every sweep instruction must be reached |
| XD-3 | **Closed encoding table.** XD decodes only the encodings in its own table. Each row gives: the permitted legacy prefixes (only `66`, and only on rows that list it); the REX forms permitted; the opcode bytes; any ModRM `mod`, `reg` or `rm` constraint; SIB and displacement handling; the immediate size; the canonical mnemonic; the operand roles and widths; the transfer class; the stack effect and memory read and write; and a citation of the manual section and revision that defines it (AD-14). The table covers exactly the permitted instruction and transfer lists of §5.14.1 and nothing else. It contains no `call`, no `ret` in any form, no indirect transfer, and none of the forbidden forms |
| XD-4 | **Output.** For every instruction: the address; the length; the raw bytes; the canonical mnemonic; each operand (register and width; memory base, index, scale, displacement and width; immediate value as encoded, and its width); for CT-2, CT-3 and CT-4, the absolute direct target; and the transfer class, stack effect and memory read and write. The stream and XD's verdict are serialised deterministically, and the stream's SHA-256 is recorded |
| XD-5 | **Failure, each a stop.** XD fails on: **(a) ambiguity** — more than one table row matches at a position. The table is checked for this when loaded, and every decode counts its matches; **(b) unsupported encoding** — no row matches. That includes any prefix outside the row, a repeated prefix, a REX byte not immediately before the opcode, an address-size `67`, segment, `lock`, `rep` or `repne` prefix, a VEX, EVEX or XOP escape, and an instruction longer than 15 bytes; **(c) undecoded byte** — the sweep cannot decode a byte, or an instruction would extend past the end of `.text`; **(d) overlapping decode** — the reachability pass reaches a position that is not a sweep boundary; **(e) bad target** — a direct target that is inside an instruction, outside its function (except the single CT-4 target, `rp11_main`'s first byte), or outside `.text`, including in `.rodata`; **(f) unreached instruction** — a sweep instruction that the reachability pass does not reach; and **(g) disagreement** — any difference in XD-6 |
| XD-6 | **Exact agreement with the listing, T-L11.** The disassembly lines of the committed listing are parsed into a stream by a fixed grammar. XD's stream is rendered into the listing's spelling through `xdecode-spelling.table`, a reviewed mapping of mnemonic spelling, register names, AT&T operand order and syntax, number radix and target printing. The mapping must be **injective**, checked when it is loaded, so that it cannot make two different decodings print alike. The streams must be equal instruction for instruction and in count, on every field T-L10 uses: **address and boundary, length, byte field, mnemonic, every operand and every direct target.** Every listing token must be produced by the rendering; a token the table cannot produce is a disagreement. The listing's function-start lines must equal XD's symbol values |
| XD-7 | **Precondition of T-L10 evidence.** T-L10's input is the stream parsed from the listing, which T-L11 shows equal to XD's stream from the image: the agreed stream. T-L10 is also run over XD's own stream and must produce an identical verdict and tables. **A T-L10 verdict is accepted only together with a passing T-L11 over the same listing digest and an image whose digest equals `expected.sha256`**, and its record names both digests and XD's version |
| XD-8 | **Evidence tooling, not a build input.** XD is class E (X-17). It is not in the build root, never runs in R-2, reads the image and the listing only after they exist, and writes only its verdict and stream, which no build step reads. It cannot change a byte of the image. Every verdict records the SHA-256 of `xdecode.py` and of `xdecode-spelling.table`, the interpreter version (X-16), the image and listing digests and the stream digest. XD and its table are covered by the review manifest as test tooling (§5.11) |
| XD-9 | **Independent implementation and review.** XD's table is written from the cited Intel and AMD manuals. It is **not** derived from binutils source, opcode tables or output, nor from the committed listing, and its author records that. At the I-7 review gate an Independent Reviewer who did not write XD checks every table row against the cited manual section, reviews the decoder and the spelling table, and reviews T-L12's corpus. The absence of binutils derivation is a **provenance and review fact**, not a mechanically provable property (§5.15.4). Any later change to XD or its table is a reviewed change and re-runs T-L11 and T-L12 |
| XD-10 | **Self-test, T-L12.** A committed corpus of hand-encoded byte sequences, each citing its manual section: every table row as a positive vector; and as negative vectors every forbidden form of §5.14.1, including `c3`, `c2 iw`, `f3 c3`, `f2 c3`, `cb`, `ca iw`, `cf`, `e8 rel32`, `ff /2`, `ff /3`, `ff /4`, `ff /5`, `cc`, `cd ib`, `f1`, `0f 34`, `c8`, `c9`, `e2`, `e3`, `c7 f8`, `f3 0f 1e fa`, `64` and `65` prefixes, `f0`, `f3 a4` and a VEX-prefixed form; each XD-5 class, by truncation, an overlapping pair of streams, a jump into an instruction, a jump into `.rodata`, an unreached instruction, and a deliberately ambiguous table that must fail to load. Toolchain-free; run in the ordinary suite |
| XD-11 | **Codex's independent decoding at D9-2, so that neither decoder is a single authority (LD-9, decided 2026-10-01).** Codex, as Independent Reviewer, decodes the actual `.text` with a decoder or a byte-by-byte manual decode of its own, prepared from the manuals without reading XD's table, and requires its instruction starts, lengths, mnemonics, operands and targets to equal XD's and the listing's. An independent exercise of XD without that separate decoding is not sufficient. The D9-2 decoding evidence is produced by Codex, not by XD's author |

#### 5.15.2 How the change traces through the dependent checks

| Item | D2-R1 basis | D2-R2 basis |
|---|---|---|
| RI-2 | the listing's own linear sweep and T-L7 byte equality | XD-2 … XD-5 on the image bytes, plus T-L7 byte equality **and** T-L11 agreement |
| BI-6 | T-L10 over the listing's mnemonics | T-L10 over the agreed stream; the absence of `call` and `ret` is an XD and T-L10 fact |
| BI-10 | T-L7 and T-L10 over the listing's boundaries and targets | T-L7, XD, T-L11 and T-L10 |
| T-L7 | described as tying "the listing T-L10 checks" to the binary | byte equality only; decoding is T-L11's |
| T-L10 | evidence on its own over the listing | accepted only with T-L11 on the same digests (XD-7) |
| P-3 | T-L7 and T-L10 | adds XD and T-L11 |
| P-4 | T-L10 over the listing, plus RI-4 … RI-7 for `ret` | T-L10 over the agreed stream; no machine-state transfer exists; decoding by XD, T-L11 and XD-11 |
| D9-2 | BI-1 … BI-11, T-L7, T-L10, HR-1 … HR-6 | adds XD, T-L11, T-L12 and XD-11 |
| §6.3 | a control-transfer verification row | adds an independent-decoding row and restates what reproducibility does not show |
| §8 | T-L10 and interpreter trust | adds XD, the manuals, the CPU and XD's provenance |

#### 5.15.3 What XD cannot do

* It does not show that the manuals are right or that the CPU follows them
  (AD-14).
* It does not show anything about the kernel (D9-1).
* It does not replace HR-1 … HR-6: it decodes instructions; it does not
  decide what a store or load means.
* It is not shown correct by reproducibility. R-4 and R-5 rerun the same
  pinned tools and never run XD. XD's correctness rests on XD-9, T-L12 and
  XD-11.
* Agreement between two decoders shows that they decode alike, not that
  either matches the CPU. It removes the single-authority risk of
  `R4-D2-R1-1`; it does not remove AD-14.

#### 5.15.4 What remains trusted

| # | Trusted | Why it cannot be removed here | Mitigation |
|---|---|---|---|
| TD-1 | the architecture manuals' encoding definitions for the image's instructions, and the repository host's CPU decoding and executing them as defined (AD-14) | every decoder, including the CPU, is a reading of the same definition; nothing in this design observes the CPU's decoding | per-row citations (XD-3); the small closed set; review against the manuals (XD-9, XD-11) |
| TD-2 | no **common misreading** of the manuals shared by XD and Codex's D9-2 decoding, for an encoding present in the image | two readers can err alike | independent preparation (XD-9, XD-11 (i)); citations per row; the listing as a third decoding that must also agree |
| TD-3 | XD's **provenance independence** from binutils | not mechanically provable | the author's record and the independent review (XD-9); XD-11 |
| TD-4 | the Python interpreters that run XD, T-L7, T-L10, T-L11 and T-L12 (X-16), and the one Codex uses at D9-2 | an interpreter defect could mis-execute a verifier | versions recorded (XD-8); Codex's decoding on its own interpreter or by hand (XD-11) |

**No longer trusted** for PO-9: the pinned binutils' **decoding**. They are
trusted only to reproduce the same listing bytes (T-L9), an identity
property. **Not claimed:** that reproducibility, IC-1, R-5 or any build
evidence shows the correctness of any decoder (LD-8).

---

## 6. PO-9: the proof and the separation of evidence

### 6.1 The proof

**Claim (PO-9 for D-S1).** Between the kernel's transfer of control to the
image and the image's `execve` of the interpreter:

1. no instruction runs that is not in the reviewed listing;
2. no instruction reads an environment string except those of
   `rp11_select_invocation_id`, *(D2-R2)* inlined into `rp11_main` and
   identified by HR-4, which read at most the bounds of §5.6;
3. no instruction reads the auxiliary vector; and
4. no locale, tunable, NSS, iconv, configuration-file or dynamic-module code
   exists or is reached.

**Premises and where each is established:**

| # | Premise | Established by |
|---|---|---|
| P-1 | the image that `ExecStart=` names is the image the kernel executes, and it is not handed to a `binfmt_misc` interpreter | AD-4 citation (D9-1) and PO-17 (H-1, H-2) |
| P-2 | for an `ET_EXEC` image with no `PT_INTERP`, control passes to `e_entry` with no user-space instruction first | AD-3 citation (D9-1) |
| P-3 | *(amended D2-R1, D2-R2)* `e_entry` is `_start`; the image has no interpreter, constructor, TLS or relocation; the function set is exactly `_start` and `rp11_main`, with no compiler-created symbol; and every byte of `.text` belongs to one of them and to exactly one instruction, **as decoded independently by XD and agreed by the listing** (RI-1, RI-2) | BI-1 … BI-5 and BI-10 (D9-2). **Mechanical:** T-L7 on the image, for the listing-to-`.text` byte equality; *(D2-R2)* **XD and T-L11**, for the decoding; and T-L10 on the agreed stream. **Independent:** XD-11 at D9-2. **Trusted:** AD-14 |
| P-4 | *(rewritten D2-R1, amended D2-R2)* the **reachable** control-flow graph from `_start` is complete. Every executed instruction is a CT-1 … CT-9 transfer or a permitted non-transfer instruction, **as decoded by XD and agreed by the listing**. Every direct target is an instruction start in its own function, or for the single CT-4 `jmp` the first instruction of `rp11_main`. **No instruction takes a transfer target from a register or memory: the image has no `ret`, no `call` and no indirect transfer** (RI-7). Faults, traps, signals and returning system calls transfer nowhere outside the listing (AD-8, AD-11, AD-12). So the listing contains every instruction that can run, and T-L10's graph over the agreed stream is every path | BI-6, BI-10 and BI-11 (D9-2). **Mechanical:** *(D2-R2)* XD and T-L11, then T-L10 on the agreed stream. **Independent:** XD-11 at D9-2. **Citation:** D9-1 for AD-8, AD-11 and AD-12. **Trusted:** AD-14. *The D2 premise, which rested completeness on BI-6's absence of indirect `call` and `jmp`, is withdrawn* (Appendix C). *The D2-R1 premise's return-integrity limb, and its reliance on the listing's own decoding, are withdrawn* (Appendix D) |
| P-5 | *(amended D2-R1, D2-R2)* the listing's `envp` and auxiliary-vector accesses are as claimed, and no input-derived value determines a store address, store count or stack adjustment (IN-1 … IN-4). *(D2-R2)* The data passed to the kernel, the frame's literals, `idbuf` and the `execve` pointer arrays, cannot be overwritten (RI-5, RI-6) | BI-7 and BI-11 (D9-2). **Human:** HR-2 … HR-6, using T-L10's load and store tables over the agreed stream. **Mechanical:** RI-5 in T-L10 |
| P-6 | the reviewed listing is the listing of the installed file | reproducibility (D9-3) and installed-digest equality (D9-4) |
| P-7 | the image that calls `execve` on `rp11-launch` is not itself loaded under the unit's block | **PO-14**: separate, and not discharged here |

P-1 … P-6 together give the claim for the image. P-7 is what makes the claim
useful for LB-2S. **The proof does not rely on any test outcome.** *(D2-R2)*
P-3 and P-4 also rest on AD-14, the manuals' encodings and the CPU's
conformance to them, which no evidence here discharges and §5.15.4 names as
trusted.

*(D2-R1, amended D2-R2)* **What makes the graph complete, stated once.** A
complete disassembly shows the instruction bytes. It is not the reachable
graph. The graph is complete because four things hold:

1. the permitted transfer classes are closed (CT-1 … CT-9);
2. every encoded target is checked against instruction boundaries that two
   independently implemented decoders agree on — XD from the image bytes and
   the committed listing — with Codex's D9-2 decoding as the second layer
   (RI-2, §5.15);
3. *(D2-R2)* **no transfer takes its target from machine state**: the image
   contains no `ret`, no `call` and no indirect transfer (LD-7, CT-4, CT-5,
   RI-7). *The D2-R1 item, which bound each `ret` to its call site by stack
   integrity, is withdrawn* (Appendix D); and
4. the kernel-mediated transfers are fixed by cited semantics (AD-8, AD-11,
   AD-12).

Each part is named with its evidence above. None rests on a test outcome.

### 6.2 PO-9 discharge components

| # | Component | Evidence class | When, and under what authority |
|---|---|---|---|
| D9-1 | citation of the installed kernel series' ELF and `binfmt_misc` handling (AD-3, AD-4, AD-6, AD-8), *(D2-R1)* forced-signal handling (AD-11) and system-call return and restart (AD-12) | documentation and source citation | I-7 or before H-1; documentation only, though it needs the kernel release, which is PO-18 |
| D9-2 | BI-1 … BI-11 on the built image, *(D2-R1)* including T-L7, T-L10 and the human review HR-1 … HR-6, by the implementer and independently by the reviewer. *(D2-R2)* Also XD's decoding and T-L11's exact agreement, **before any T-L10 result is accepted** (XD-7); T-L12; the independent review of XD (XD-9); and **Codex's independently prepared decoding of the actual `.text` (XD-11)** | binary inspection, *(D2-R2)* including independent decoding | I-7, under the M-14 implementation authority |
| D9-3 | R-1 … R-5, including the independent rebuild, *(D2-R1)* R-1's tree-manifest equality and IC-1. *(D2-R2, LD-8)* It passes only with a passing IC-1, an R-5 that records an actual variation of at least one of HA-1 … HA-3, and no unexplained difference. **It is not decoder evidence** | reproducibility and build-environment evidence | I-7 and before H-1 |
| D9-4 | the installed digest equals the expected digest, and PO-17 holds | installed-host evidence | H-1, then H-2 before each pass |
| D9-5 | the hostile-environment experiment | hostile-environment testing — **corroboration only** | separately authorized |

**PO-9 is discharged for a given installation only when D9-1 … D9-4 all
hold.** D9-5 corroborates. PO-16 corroborates LB-2S as a whole. PO-14 is
independent.

### 6.3 What each evidence class can and cannot show

| Class | Shows | Does not show |
|---|---|---|
| source properties (T-L1 … T-L3) | the reviewed text has the intended structure and literals | what the compiler emitted |
| compiler and linker output (the map and the `-v` record) | which inputs and flags the build used | that the output lacks pre-entry code |
| reproducibility (D9-3) | the reviewed listing is the deterministic product of the reviewed source and pin | that the listing is correct; *(D2-R2)* that the pinned disassembler, or any decoder, decodes correctly, because a decoding error reproduces faithfully (LD-8) |
| *(D2-R1)* build-environment evidence (R-1 tree manifest, IC-1) | the build ran in exactly the bound root; in the traced run, no class-B tool executed or opened anything outside it; and every class-B process's environment was the literal | that the tools are correct; anything about HA-1 … HA-5 beyond the variants tested; or what a tool would open on an untested kernel or CPU |
| *(D2-R1, amended D2-R2)* control-transfer verification (T-L10, with T-L7 and T-L9) | the agreed stream, which T-L7 byte-ties and T-L11 decode-ties to the image's `.text`, satisfies CT and RI, contains no `call` or `ret`, and its reachable graph and stack bound are as computed | the kernel semantics the rules rely on (D9-1); the meaning of each store, which is HR-1 … HR-6; the correctness of the verifier itself, which the reviewer re-derives; *(D2-R2)* or anything at all, unless T-L11 passed on the same digests (XD-7) |
| *(D2-R2)* independent decoding (XD, T-L11, T-L12, XD-11) | XD, Codex's independently prepared decoding of the image's `.text`, and the committed listing agree exactly on every instruction start, length, byte field, mnemonic, operand and target; every byte is decoded once under the closed table, with no overlap, bad target or unreached instruction | that the manuals are right or that the CPU follows them (AD-14); the absence of a misreading common to both decoders (TD-2); the meaning of any instruction's data flow (HR-1 … HR-6); or anything about the kernel |
| binary inspection (D9-2) | the image's structure, and every executable instruction *(D2-R2: as independently decoded)* | how the kernel starts it (D9-1), or which file is installed (D9-4) |
| installed-host evidence (D9-4, PO-17, PO-18) | this file, with this digest, is at the path on a compatible kernel, with no matching `binfmt_misc` registration, at one moment | anything after that moment (S-7) |
| hostile-environment testing (D9-5) | this binary, once EN-1 … EN-3 show it was entered, produced the exact golden sequence for the inputs tried, on one kernel, within AE-1 … AE-5 with HD-1 and HD-2 headroom | absence of behaviour on untried inputs, or anything a `DRIVER-EXEC-FAILED` case would have tested: **corroboration** |
| PO-14 | the executor is not loaded under the unit's block | anything about this image |

---

## 7. Differences from R2's `rp11-launch/1` text

R2 is not amended. These refinements take effect only if accepted (LD-6).

| # | R2 text | This design | Why |
|---|---|---|---|
| V-1 | four state operations | adds S-3, the stdio check, and status `113` | FD-7 |
| V-2 | "a fixed status per step" and three class names | numeric statuses `111` … `117`, seven classes and exact line bytes | item 9 requires exact values |
| V-3 | "entries whose name is exactly `INVOCATION_ID`" | also counts an entry that is exactly `INVOCATION_ID`, with no `=`, as an invalid occurrence | defines a case R2 left open |
| V-4 | "exactly one is required" | makes explicit that two identical entries refuse | defines duplicates |
| V-5 | R2 §4.4.2 and the §7.9 LB-1 row: the same image, started by the client, writes the two-entry literal | **the image has one mode and refuses without `INVOCATION_ID`**. `entry_environment.KEY_SETS["LB-1"]` has no image, and T-B14's LB-1 variant falls away. If LB-1 is ever chosen, it needs its own image | FD-1: presence or absence of a variable in an untrusted block must not select behaviour. M-9 conditionally selected LB-2S, so there is no current effect |
| V-6 | "resets every signal disposition" | signals 1 … 64 except 9 and 19, through the raw system call | FD-2; `SIGKILL` and `SIGSTOP` cannot be changed |
| V-7 | silent on `argv[0]` | `argv[0]` is not examined | it is the caller's choice and carries no meaning here |
| V-8 | a C-library runtime to be chosen by M-14 | no C library or runtime | §4.4 |

No refinement changes the unit, the polkit rule, `rp11-entry-env/1`'s LB-2S
key set or literals, the `execve` vector, or any R4-D1-2 result.

---

## 8. What remains trusted, and residual risk

| Item | Status |
|---|---|
| the kernel: `execve`, the ELF handler, signal delivery | trusted system state (R2 R-8), cited in D9-1 |
| `binfmt_misc` registrations | root-controlled system state. **New**: checked at H-1 and H-2 (PO-17). A registration added after H-2 is not prevented (S-7-like), exactly as R-10 treats other root input |
| LSM policy, seccomp, rlimits and the other §5.7 "not touched" items | manager execution settings, trusted and reviewed under R-10. A seccomp filter that denies one of the nine system calls fails closed |
| PID 1 and `systemd-executor` | trusted, subject to PO-14 |
| the toolchain | **not trusted for correctness.** It is trusted only to reproduce the reviewed listing, which D9-3 checks. *(D2-R2)* That now includes the disassembler: its **decoding** is not trusted, and is accepted only where XD agrees (§5.15) |
| *(D2-R1)* the build root and the unpinned host inputs | the root is bound file by file (R-1) and its use is traced (IC-1). The kernel, CPU, entry mechanism, time and identity (HA-1 … HA-5) are **named residual inputs**. R-5 detects drift they cause on the variants tested, and does not remove them. The entry mechanism is trusted for the interval between R-1 and R-2 (HA-3) |
| *(D2-R1)* the control-transfer verifier (T-L10) and the Python interpreter that runs it (X-16) | class-E tooling. A defect that accepted a violating listing is mitigated by the reviewer's independent re-derivation and by HR-1 … HR-6 applied to the raw listing |
| *(D2-R2)* instruction decoding | **no single decoder is trusted.** The pinned `objdump`'s decoding and XD's must agree exactly (T-L11), and Codex independently decodes the actual `.text` at D9-2 (XD-11). **What remains trusted** is TD-1 … TD-4 (§5.15.4): the manuals' encodings and the CPU's conformance to them (AD-14); the absence of a misreading common to XD and Codex's decoding; XD's provenance independence from binutils, a review fact; and the interpreters. Reproducibility is **not** a mitigation here (LD-8) |
| the human review of the listing *(amended D2-R1: HR-1 … HR-6, BI-7; D2-R2)* | **the residual risk of this design.** Reachability is now mechanical (CT, RI, T-L10), over an independently decoded stream (§5.15). What remains human is confirming that each store, load and system-call argument means what the source intends. It is mitigated by the listing's size, by the closed transfer classes *(D2-R2: with no `call` or `ret`)*, by the mechanical checks T-L4, T-L7, XD, T-L11 and T-L10, and by review by two independent parties. *(D2-R2)* Inlining the selection functions removes their symbol boundaries, which makes HR-4 heavier; that is a cost accepted with LD-7. *The D2 cell's reliance on "the absence of indirect branches" is withdrawn* (Appendix C); *the D2-R1 cell's reliance on "the return-integrity rules" is superseded* (Appendix D) |
| T-B | out of scope (M-10). An adversary with the operator's account cannot change the root-owned image, but can forge files as R2 R-7 states |

---

## 9. Maintainer decisions requested

| # | Decision | Options | Recommendation |
|---|---|---|---|
| **LD-1** | launcher runtime | **C-1** (D-S1); C-1A; C-2; decline (then LB-2S cannot exist and is withdrawn) | **C-1**, with C-1A as the fallback of §4.5 |
| **LD-2** | target architecture | `x86_64` only; add others later as replacements (§5.13) | `x86_64` only, confirmed at H-1 (PO-18) |
| **LD-3** | toolchain source | pinned distribution packages from a snapshot archive, with digests; or a container image pinned by digest (adds a container runtime to the build) | distribution packages. Ubuntu 26.04 LTS is suggested because it is the documented future production baseline (OD-5), though the image does not depend on the distribution. The values are set in I-7 |
| **LD-4** | commit the reviewed listing | yes; no (regenerate only) | **yes**, so that a toolchain change appears as a reviewable diff |
| **LD-5** | who performs the independent rebuild (R-5) | Codex; Peter Duscha; another agent that did not implement the image | a party other than the implementer, in a separately provisioned environment |
| **LD-6** | accept the refinements V-1 … V-8 | accept; accept some; reject | accept all |
| **LD-7** *(new D2-R1; decided 2026-09-30)* | control-flow form for PO-9 | *(D2-R1 options)* `ret` permitted under CT and RI, with FA-1 … FA-3 as the fail-closed sequence; or require FA-2's zero-`ret` image from the start, accepting the narrower T-L8 | **Decided by Peter Duscha: FA-2's zero-`ret` image from the first build**, with the narrower T-L8, which remains source and compiler behavioural evidence and does not replace inspection of the installed image. Applied in §5.1, §5.2, §5.12.1 and §5.14. **Permitting `ret` later requires a new, separately reviewed decision.** *The D2-R1 recommendation, "`ret` under CT and RI … FA-2 remains available if the first build fails T-L10", is withdrawn* (Appendix D) |
| **LD-8** *(new D2-R1; decided 2026-09-30, conditionally)* | the build-input claim | *(D2-R1 options)* accept the bound build root plus named residual inputs HA-1 … HA-5, with IC-1 in I-7; or require more, such as a diverse double compilation | **Decided by Peter Duscha: accepted, on four conditions, now normative**: IC-1 passes (§5.3.7); R-5 actually varies at least one of HA-1 … HA-3 and records which (§5.3.5); every unexplained difference is a hard stop (§5.3.5); and `R4-D2-R1-1` is resolved independently of reproducibility (§5.15). **Diverse double compilation is not required.** Reproducibility is not claimed to show decoder correctness (§5.3.8, §6.3) |
| **LD-9** *(new D2-R2; decided 2026-10-01)* | the form of Codex's D9-2 decoding evidence (XD-11) | (i) require re-derivation by a decoder or byte-level decode of Codex's own; or (ii) also accept an independent exercise of XD | **Decided by Peter Duscha: (i).** Codex must independently decode the actual `.text` with its own decoder or byte-by-byte manual derivation prepared without reading XD's table. Option (ii) is not sufficient. The D9-2 record binds Codex's independently derived instruction starts, lengths, mnemonics, operands and targets to XD and the listing |

**M-14/I-7 repository implementation authority was granted on 2026-10-01.**
Still required: H-1 and H-2 authority; the PO-14 citation; and every R2
decision not yet made (D-2, M-11, D-1, MD-C11 and others).

*(D2-R2)* Authority to implement XD and its test corpus is included in I-7.
The independent review of XD (XD-9) and Codex's D9-2 decoding (XD-11) remain
separate reviewer duties and are not delegated to the implementer.

---

## 10. Proof obligations

| # | Obligation | Status |
|---|---|---|
| PO-9 | as R2, now with components D9-1 … D9-5 (§6.2). *(D2-R1)* D9-1 adds AD-11 and AD-12. D9-2 adds BI-10, BI-11, T-L10 and HR-1 … HR-6. D9-3 adds the tree manifest and IC-1. *(D2-R2)* D9-2 adds XD, T-L11, T-L12, XD-9 and XD-11, and T-L10 is accepted only with T-L11 (XD-7). D9-3 adds LD-8's conditions. AD-14 is named as trusted, not discharged | **open.** Load-bearing. This design specifies how it is discharged; nothing is discharged |
| PO-14 | as R2 | **open**, unchanged, load-bearing |
| PO-16 | as R2 | open, unchanged; corroboration |
| **PO-17** *(new)* | no enabled `binfmt_misc` registration on the repository host matches `rp11-launch`, or `binfmt_misc` is not mounted | open. H-1 and H-2, under their own authority |
| **PO-18** *(new)* | the repository host's kernel reports machine `x86_64` and a release of 5.9 or later | open. H-1 and H-2 |

---

## 11. What this proposal does not establish

* It does not discharge PO-9, PO-14, PO-16, PO-17 or PO-18.
* It compiled, built, installed, inspected and executed nothing. Every
  statement about compiler, linker, kernel, musl, `nolibc`, Rust, Go, glibc or
  systemd behaviour is from documentation knowledge, stated as an assumption
  (AD-1 … AD-10; *D2-R1:* AD-11 … AD-13, AB-1 … AB-4, AE-1 … AE-5) and
  marked for citation.
* It does not verify the repository host's architecture or kernel (OD-6).
* *(D2-R1)* It does not show that any compiler output satisfies §5.14. The
  expected frame layout and function shape are design expectations, checked
  only by T-L10 and HR-1 … HR-6 on a later build.
* *(D2-R1)* It records no build-root manifest, IC-1 trace, `execve` limit or
  test-host value. AB-1 … AB-4, AE-1 … AE-5, AD-11 … AD-13 and HA-1 … HA-5
  are assumptions or named residual inputs.
* *(D2-R2)* It does not show that any compiler output can be built without
  `ret` or `call`, that `always_inline` and `noreturn` produce the expected
  listing shape, or that FA-1 or FA-3 would work. These are checked only by
  XD, T-L11, T-L10 and HR-1 … HR-6 on a later build.
* *(D2-R2)* It implements no decoder, writes no encoding table or spelling
  table, and cites no manual page: XD-1 … XD-11 are requirements. AD-14 is an
  assumption named as trusted, not a verified statement.
* It pins no toolchain version and records no package digest (§5.3.2).
* It does not authorize I-7, a download, a build, H-1, H-2, D9-5 or PO-16.
* It does not select LB-2S unconditionally, accept D-1 or D-2, choose MD-C11
  or reopen R4-D1-2.
* It does not amend R2, D-1, D-2, the operational draft or the manifest.

Throughout: RP-11 remains unwired and unmet; neither pass is executable or
authorized; `plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A
remains conditional; and Package 5.0 remains not ready.

---

## Appendix C — D2-R1 change record and withdrawn or narrowed claims

Each quotation below is verbatim from the reviewed D2 bytes
(`adc114bf…f28d8093`). A line break inside a quotation is shown as a space.
Appendix entries do not claim a finding closed.

* **C-1** (R4-D2-1; D2 §0 Result): “every instruction after it appears in one reviewed listing of under 4 KiB of code with a complete control-flow graph (§6).” — **narrowed**: the listing alone does not make the graph complete; §5.14 and §6.1 now state what does.
* **C-2** (R4-D2-1; D2 §0 FD-6): “Because the image is tiny and has no indirect branch, its **complete** disassembly is reviewable, and it is committed and bound by digest” — **narrowed**: `ret` is permitted only under §5.14, and the graph is established by T-L10 and HR-1 … HR-6.
* **C-3** (R4-D2-1; D2 §4.3 C-1, source-to-binary review): “the complete disassembly is under 4 KiB and has no indirect branch, so every executable path is visible.” — **withdrawn**: a visible instruction is not a determined path. Replaced by the amended cell.
* **C-4** (R4-D2-1; D2 §4.4 item 2): “**complete:** every executed instruction is in one reviewed listing, with no indirect branch; and” — **replaced** by CT-1 … CT-9 and RI-1 … RI-7.
* **C-5** (R4-D2-1; D2 §5.3.3): “no jump tables (so there is no indirect branch)” — **withdrawn**: `-fno-jump-tables` removes only switch-table indirect jumps.
* **C-6** (R4-D2-1; D2 §5.12.1 T-L4): “no indirect `call` or `jmp`;” — **narrowed**: T-L4 is a coarse text screen. The control-flow check is T-L10.
* **C-7** (R4-D2-1; D2 §5.12.2 BI-6): “complete, with no indirect `call` or `jmp`, so the control-flow graph is fully determined;” — **withdrawn**: replaced by BI-6 (rewritten), BI-10, BI-11 and §5.14.
* **C-8** (R4-D2-1; D2 §5.12.2, closing text): “BI-6's reachability and BI-7 are a **human review of the listing**.” — **replaced**: reachability is mechanical (T-L10). The human review is HR-1 … HR-6.
* **C-9** (R4-D2-1; D2 §6.1 P-4): “| P-4 | the control-flow graph from `_start` is complete, so the listing is every instruction that can run | BI-6 (D9-2) |” — **replaced** by the rewritten P-4, with its mechanical, human and citation evidence.
* **C-10** (R4-D2-1; D2 §8): “It is mitigated by the listing's size, the absence of indirect branches, the mechanical checks T-L4 and T-L7, and review by two independent parties” — **withdrawn** as a mitigation. Replaced by the amended row.
* **C-11** (R4-D2-1; D2 §5.10, resource exhaustion): “its stack use is bounded below 1 KiB” — **narrowed**: the bound is computed from the listing by T-L10 (RI-4), and 1 KiB is the design limit it must meet.
* **C-12** (R4-D2-2; D2 §5.2): “**The complete set of build inputs** is:” — **withdrawn** together with its three-item list: it omitted `/bin/sh`, `/usr/bin/env` and the tools' runtime inputs.
* **C-13** (R4-D2-2; D2 §5.2): “**Nothing else is read**: no libc, libc header, kernel header, `libgcc`, `crt*.o`, default linker script or system specs file affects the image.” — **narrowed** to what is *linked into* the image. It is no longer a statement about what the tools read.
* **C-14** (R4-D2-2; D2 §5.3.2): “The closure is every package that installs a tool binary, a tool data file or a shared library that the tools load: the compiler driver and `cc1`, the assembler, the BFD linker, `objdump` and `readelf`, and their library dependencies.” — **replaced**: the lock lists every installed package, and `build-root.manifest` binds every file (§5.3.2, §5.3.7).
* **C-15** (R4-D2-2; D2 §5.3.3 compile vector): “-ffile-prefix-map=⟨build dir⟩=.” — **withdrawn**: it put an absolute, build-specific path into a vector described as fixed. The `-Wa,…` options move to the assembler vector.
* **C-16** (R4-D2-2; D2 §5.3.4, environment row): “the build runs under `env -i` with the literal environment of §5.3.5” — **narrowed**: `env -i` and `/bin/sh` are themselves class-B inputs (X-5, X-6), and IC-1 checks the environment each tool receives.
* **C-17** (R4-D2-2; D2 §5.3.4, loader-state row): “Residual root-owned loader configuration on the build host is not trusted: reproducibility on a **second, independently provisioned** environment (R-5) and the listing review catch any effect on the output” — **withdrawn**: independent reproducibility does not make an omitted input stop being an input. Loader configuration is now in the bound tree, and the unpinnable inputs are HA-1 … HA-5 (§5.3.8).
* **C-18** (R4-D2-2; D2 §5.3.5 R-2): “run `env -i PATH=/usr/bin LC_ALL=C TZ=UTC0 SOURCE_DATE_EPOCH=0 /bin/sh infra/rp11-launch/build.sh ⟨out⟩`” — **replaced** by the exact vector starting `/usr/bin/env -i`, started as the first process in the root.
* **C-19** (R4-D2-2; D2 §5.3.5 R-4): “with `umask 077` set before the call, and with a different `TMPDIR`” — **withdrawn**: neither reaches the build. R-4 now varies (a) path, (b) time and modification times, and (c) identity.
* **C-20** (R4-D2-2; D2 §5.12.1 T-L6): “build twice in different directories, `umask` values and `TMPDIR`s (R-4)” — **replaced** by the three R-4 variations.
* **C-21** (R4-D2-3; D2 §5.12.4 HX-3): “| HX-3 | 10 000 extra entries; entries of 128 KiB; entries without `=`; empty entries; non-ASCII bytes | as HX-2 |” — **withdrawn**: a 128 KiB entry plus its NUL exceeds `MAX_ARG_STRLEN` (AE-1), and the combination can exceed the aggregate limit (AE-2). Replaced by HX-3a … HX-3d.
* **C-22** (R4-D2-3; D2 §5.12.4 HX-5): “| HX-5 | each §5.5 refusal case | `exit_group(111)` |” — **withdrawn**: it contradicted §5.9. Replaced by G-111.
* **C-23** (R4-D2-3; D2 §5.12.4 HX-7): “| HX-7 | descriptor 1 or 2 closed | `exit_group(113)` |” — **withdrawn**: it omitted the write and descriptor 0. Replaced by HX-7a … HX-7f.
* **C-24** (R4-D2-3; D2 §5.12.4 HX-4): “`write` of the class line, then `exit_group(112)`; nothing else” — **narrowed** to the exact G-112 bytes and length.
* **C-25** (R4-D2-3; D2 §5.12.4 Method A): “A driver `execve`s the image with a constructed argv and `envp`, under `strace -f`. Fault injection makes the image's own `execve` of `/usr/bin/python3.12` fail” — **replaced**: an `O_CLOEXEC` pipe and EN-1 … EN-3 establish entry; an empty `tmpfs` over `/usr/bin` produces `ENOENT`; the tracer never receives the case's vector.
* **C-26** (R4-D2-3; D2 §5.12.4 golden sequence): “**Golden sequence for HX-1 to HX-3:** `fcntl` ×3, `close_range`, `rt_sigaction` ×62, `rt_sigprocmask`, `umask`, `chdir`, `execve` (injected failure), `write`, `exit_group(117)`.” — **replaced** by the exact G-OK and the other golden sequences.

No claim of the D2 text about the launcher contract (§5.5 … §5.8), the
system-call inventory, the candidate comparison's rejections or V-1 … V-8 is
withdrawn. The D2 handback is not amended. Its question 3 asked whether "no
indirect branch" was enough to call the listing's control-flow graph
complete. `R4-D2-1` and this amendment answer it in the negative.

---

## Appendix D — D2-R2 change record and withdrawn, narrowed or superseded claims

Each quotation below is verbatim from the D2-R1 bytes Codex re-reviewed
(`a70f013f…fc295b81`). A line break inside a quotation is shown as a space.
Appendix entries do not claim `R4-D2-R1-1` closed. "LD-7" and "LD-8" mark
changes that apply Peter Duscha's decisions; "R4-D2-R1-1" marks changes that
remediate the finding.

* **D-1** (LD-7; D2-R1 §0 Result): “a return-integrity discipline that fixes the target of every reachable `ret`.” — **withdrawn**: no `ret` exists; the Result now names the zero-`ret` transfer set and XD.
* **D-2** (LD-7; D2-R1 §0 FD-6): “and admits `ret` only under the return-integrity discipline of §5.14” — **withdrawn**: the image admits no `ret` (§5.14.1).
* **D-3** (LD-7; D2-R1 §4.3 C-1, source-to-binary review): “and `ret` appears only under the return-integrity discipline of §5.14” — **withdrawn**: replaced by the amended cell (no `call`, no `ret`, XD agreement).
* **D-4** (LD-7; D2-R1 §4.4 item 2): “and every `ret` is bound to its call site by RI-1 … RI-7 (§5.14)” — **withdrawn**: no transfer takes its target from machine state; decoding checked by XD.
* **D-5** (LD-7; D2-R1 §4.5): “no build passes T-L10 and the human review HR-1 … HR-6 under any of the fail-closed alternatives FA-1 … FA-3 (§5.14.5);” — **narrowed**: the alternatives are FA-1 and FA-3 within the zero-`ret` form, and a `ret`-permitting form is not an alternative.
* **D-6** (LD-7; D2-R1 §5.1 Entry): “If `rp11_main` ever returns, `_start` issues `exit_group(117)`.” — **withdrawn**: `_start` enters `rp11_main` by `jmp`, and nothing follows it.
* **D-7** (LD-7; D2-R1 §5.1 Entry): “`_start`'s code after the `call` is therefore unreachable. It is kept as a defence, and it ends in `ud2`.” — **withdrawn**: `_start` contains no `call`, and its last instruction is the CT-4 `jmp`.
* **D-8** (LD-7; D2-R1 §5.2 `select.c` row, role): “image source, and linked unchanged into the test harness (T-L8)” — **withdrawn** with the row: `select.c` no longer exists, and `select.h` is included unchanged by the test shim.
* **D-9** (LD-7; D2-R1 §5.2 harness row): “a hosted test program that links the **same** `select.o` and drives it over synthetic vectors.” — **replaced**: the harness links a shim compiled from the same `select.h` with the image's compile vector.
* **D-10** (LD-7; D2-R1 §5.10): “| `rp11_main` returns (a defect) | `_start` calls `exit_group(117)` |” — **replaced**: an accepted image contains no `ret`; a `ret` in a defective image would transfer to 0 and fault.
* **D-11** (LD-7; D2-R1 §5.12.1 T-L8): “`select_harness`, linked with the **same `select.o` bytes** as the image,” — **narrowed** under LD-7: T-L8 is source and compiler behavioural evidence and does not replace inspection of the installed image.
* **D-12** (LD-7; D2-R1 §5.14 introduction): “In this image the only such transfer is `ret`.” — **withdrawn**: in the zero-`ret` form no transfer takes its target from machine state.
* **D-13** (LD-7; D2-R1 §5.14 contract function set): “**The contract function set** is `_start` (`start.s`), `rp11_main` (`launch.c`), and `rp11_check_argv` and `rp11_select_invocation_id` (`select.c`).” — **replaced**: the set is `_start` and `rp11_main`; the selection functions are inline in `select.h`.
* **D-14** (LD-7; D2-R1 §5.14.1 CT-4): “| CT-4 | direct call | `call` with a 32-bit displacement | the entry of a listed function other than `_start`. The call graph is acyclic |” — **replaced** by the single entry `jmp`; no `call` exists.
* **D-15** (LD-7; D2-R1 §5.14.1 CT-5): “| CT-5 | near return | `ret`, opcode `c3` only | **machine state**: the eight bytes at `%rsp`.” — **withdrawn**: CT-5 is now absent; no `ret` in any form.
* **D-16** (LD-7; D2-R1 §5.14.1 CT-5): “The expected shape is that only the two `select.c` leaves contain `ret`” — **withdrawn**: the expected shape is two functions with no `ret` (§5.14.3).
* **D-17** (LD-7; D2-R1 §5.14.2 RI-4): “and `call` (with net effect zero on return)” — **withdrawn** as vacuous: no `call` exists.
* **D-18** (LD-7; D2-R1 §5.14.2 RI-4): “is never negative, and is **0 at every `ret`**.” — **narrowed**: "never negative" is kept; "0 at every `ret`" is vacuous and withdrawn.
* **D-19** (LD-7; D2-R1 §5.14.2 RI-7): “At every reachable `ret`, the eight bytes at `%rsp` are the bytes written by the `call` that entered the function.” — **replaced**: RI-7 now states that no reachable instruction takes a transfer target from a register or memory.
* **D-20** (LD-7; D2-R1 §5.14.2, reachable graph): “* the direct call edges (CT-4); * the matching return edges (CT-5, RI-7); and” — **replaced**: the graph has one entry edge and no call or return edges.
* **D-21** (LD-7; D2-R1 §5.14.5 FA-2 row): “| FA-2 | **zero-`ret` image** |” — **superseded**: FA-2 is the selected design, not a fallback.
* **D-22** (LD-7; D2-R1 §5.14.5 FA-2 row, cost): “The harness compiles the same `select.c` source with the same flags.” — **narrowed**: a hosted harness cannot use the freestanding flags; a freestanding shim compiled with the image's vector includes `select.h`, and the hosted harness links it.
* **D-23** (LD-7; D2-R1 §6.1 P-4): “Every reachable `ret` returns to the instruction after its matching direct `call`, because the stack is balanced, every store stays inside its own frame, and nothing else writes the stack (RI-4 … RI-7).” — **withdrawn**: replaced by "no instruction takes a transfer target from a register or memory".
* **D-24** (LD-7; D2-R1 §6.1, what makes the graph complete, item 3): “the only transfer that takes its target from machine state, `ret`, is bound to its call site by the integrity of the stack slot it reads (RI-4 … RI-7); and” — **replaced**: no transfer takes its target from machine state.
* **D-25** (LD-7; D2-R1 §8, human review row): “by the closed transfer classes and the return-integrity rules,” — **superseded**: the closed classes contain no `call` or `ret`; XD and T-L11 are added.
* **D-26** (LD-7; D2-R1 §9 LD-7, recommendation): “`ret` under CT and RI. It keeps T-L8's object identity, and the RI evidence is mechanical. FA-2 remains available if the first build fails T-L10” — **withdrawn**: Peter Duscha decided FA-2's zero-`ret` image from the first build.
* **D-27** (LD-7; D2-R1 §5.12.2 BI-11): “The static `%rsp` offset is consistent at every join and zero at every `ret`.” — **narrowed**: "zero at every `ret`" is vacuous and withdrawn.
* **D-28** (LD-7; D2-R1 §5.2 build-input boundary): “the six image-source and build-definition files” — **corrected** to five: `select.c` is withdrawn.
* **D-29** (LD-7; D2-R1 §5.2 build-input boundary): “BI-8 checks that the linker's map names only the three objects.” — **corrected** to two objects.
* **D-30** (LD-7; D2-R1 §5.2 `expected.sha256` row): “It also holds the digests of the two intermediate files `launch.s` and `select.s`,” — **corrected**: one intermediate file, `launch.s`.
* **D-31** (LD-7; D2-R1 §5.3.3): “Compiling `launch.c` and `select.c`, each separately, to assembly” — **corrected**: only `launch.c` is compiled; it includes `select.h`.
* **D-32** (LD-7; D2-R1 §5.3.7 X-9): “assembles the three `.s` files” — **corrected** to two.
* **D-33** (LD-7; D2-R1 §5.3.7 IC-1): “the six repository inputs” — **corrected** to five.
* **D-34** (LD-7; D2-R1 §5.12.2 BI-8): “the linker map names exactly `start.o`, `launch.o` and `select.o`,” — **corrected** to `start.o` and `launch.o`, in that order.
* **D-35** (R4-D2-R1-1; D2-R1 §5.14.2 RI-2): “Linear-sweep decoding of `.text` leaves no undecodable byte, and the listing's bytes equal `.text` (T-L7).” — **replaced**: the decoding is XD's, from the image bytes, and must agree with the listing (T-L11); T-L7 is byte equality only.
* **D-36** (R4-D2-R1-1; D2-R1 §5.12.2 BI-10): “Linear-sweep decoding leaves no undecodable byte.” — **replaced** by XD-2 … XD-5 and T-L11.
* **D-37** (R4-D2-R1-1; D2-R1 §5.12.1 T-L7): “so that the listing T-L10 checks cannot omit or add a byte (BI-10)” — **narrowed**: T-L7 shows byte equality only, not decoding.
* **D-38** (R4-D2-R1-1; D2-R1 §5.12.1 T-L10, docstring): “and that T-L7 and T-L9 tie that text to the binary” — **withdrawn**: T-L7 ties bytes and T-L9 identity; only T-L11 ties the decoding to the binary.
* **D-39** (R4-D2-R1-1; D2-R1 §5.14.4): “T-L7 ties the listing's instruction bytes to the image's `.text`, and T-L9 ties the listing to the pinned binutils' output.” — **narrowed**: neither is a decoding check; XD and T-L11 are added before T-L10.
* **D-40** (R4-D2-R1-1; D2-R1 §6.1, what makes the graph complete, item 2): “every encoded target is checked against the decoded instruction boundaries (RI-2);” — **narrowed**: the boundaries are those two independent decoders agree on, with Codex's D9-2 decoding as the second layer.
* **D-41** (R4-D2-R1-1; D2-R1 §6.3, control-transfer verification row): “the committed listing, which is byte-tied to the image's `.text`, satisfies CT and RI,” — **narrowed**: the agreed stream, byte-tied by T-L7 and decode-tied by T-L11; no T-L10 result stands without T-L11.
* **D-42** (LD-8; D2-R1 §5.3.5 R-5): “Where available, it uses a different machine (CPU model, HA-2), a different kernel release (HA-1) and a different entry mechanism (HA-3).” — **superseded**: R-5 must actually vary at least one of HA-1 … HA-3 and record which, or it does not pass.
* **D-43** (LD-8; D2-R1 §5.3.8 HA-1 and HA-2 rows): “varied in R-5 where available” — **superseded** in both rows: each is one of the three candidates R-5 must vary.
* **D-44** (LD-8; D2-R1 §9 LD-8, recommendation): “A diverse toolchain is a further option. It is not needed for PO-9, which rests on the listing review” — **narrowed**: Peter Duscha decided diverse double compilation is not required; PO-9 rests on the listing review over an independently decoded stream, and not on reproducibility.

No claim of the D2-R1 text about the launcher contract (§5.5 … §5.9), the
system-call inventory, the build-input closure X-1 … X-15, the residual
inputs HA-1 … HA-5 as inputs, the hostile-environment experiment of §5.12.4
or V-1 … V-8 is withdrawn. Appendix C and the §0-D2R1 note are kept as the
D2-R1 record; the D2-R1 handback is not amended. Its question 5 asked whether
LD-7 should require a second, independent verifier, and its question 3 asked
whether RI-2 ruled out overlapping decoding. `R4-D2-R1-1` and this amendment
answer both by requiring XD's independent decoding and exact agreement.
