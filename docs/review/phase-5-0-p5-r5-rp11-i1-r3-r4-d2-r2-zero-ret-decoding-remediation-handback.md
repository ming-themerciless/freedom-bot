# Claude handback — D2-R2 zero-`ret` and independent-decoding remediation

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-D2-R2`

Date: 2026-09-30

Assignment:
[`phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r2-zero-ret-decoding-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r2-zero-ret-decoding-remediation-claude-prompt.md)
(SHA-256 `7b182696e95c97975d56e3a6f59528a5c3c094e3f75f44b875b48844091c3d15`)

Controlling review and decisions:
[`project-review-2026-09-30-p5-r5-rp11-r4-d2-r1-decisions.md`](project-review-2026-09-30-p5-r5-rp11-r4-d2-r1-decisions.md)
(SHA-256 `2748a9147e9a83ed5cdaec5552b30ba1cbdfd5866e7612352ad1c4c311f80d70`)

Amended proposal:
[`phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md)

* re-reviewed D2-R1 bytes: SHA-256
  `a70f013f77c83f448a03fc08b15b2075aa47efaa09da5e9290af3f1bfc295b81`
  (1 774 lines);
* returned D2-R2 bytes: SHA-256
  `5aea7c59cf16398cb147948b586cbcd46c6b0211523bb5efbfd383947d021b5d`
  (2 252 lines).

Earlier records, unchanged and still controlling except as the decisions and
the assignment change them: the
[D2-R1 assignment](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r1-static-launcher-design-remediation-claude-prompt.md)
(`57500b5b…`) and the
[D2-R1 handback](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r1-static-launcher-design-remediation-handback.md)
(`e985d512…`).

State: **returned as documentation only, for independent Codex re-review.
Claude has stopped. `R4-D2-R1-1` is not claimed closed; it remains Open,
Blocking.** Nothing is accepted, built, decoded or implemented. PO-9 and PO-14
remain open.

## 1. Summary

**Outcome: D-S1 retained, in its zero-`ret` form.** The amendment applies
LD-7 and LD-8 and remediates `R4-D2-R1-1` by the reviewer's first-preference
option, an independently implemented decoder that must agree exactly with the
committed listing.

* **Zero-`ret` form (LD-7) — now the selected design, not a fallback.**
  * The image has two functions. `_start` aligns the stack, pushes a zero word
    and enters `rp11_main` by **one direct `jmp`** (proposal §5.1).
  * The selection functions are `static inline __attribute__((always_inline))`
    definitions in `select.h`, included once by `launch.c`. `select.c` and
    `select.o` are withdrawn, and the link has two objects (§5.2, §5.3.3).
  * **No `call` and no `ret` in any form** (§5.14.1). CT-4 is now the single
    entry `jmp`. CT-5 is kept as a numbered row stating that return is
    absent.
  * RI-7's return argument is withdrawn and replaced: no reachable
    instruction takes a transfer target from a register or memory. RI-5 and
    RI-6 are kept for **data** integrity, the frame's literals and the
    `execve` arguments (§5.14.2).
  * SR-7 and SR-8 are added, and the expected listing shape is stated as a
    design expectation (§5.14.3).
  * T-L8 is narrowed exactly as LD-7 accepts. A freestanding shim compiled
    from the same `select.h` with the image's compile vector is linked into
    the hosted harness. It is source and compiler behavioural evidence and
    does not replace inspection of the installed image (§5.12.1).
  * **Every recommendation that permitted `ret` is withdrawn or superseded**
    (FD-6, §4.3, §4.4, §5.1, §5.14, §6.1, §8, §9 LD-7). FA-1 and FA-3 remain,
    both within the zero-`ret` form. **No return-based alternative is
    preserved**: it needs a new maintainer decision (§5.14.5, §4.5).
* **Independent decoding (`R4-D2-R1-1`).**
  * **XD** (§5.15, XD-1 … XD-11) reads the image file itself, not the
    listing, `objdump` or `readelf`. It decodes all of `.text` from `_start`,
    by linear sweep and by an independent reachability pass, under a closed
    encoding table written from the Intel and AMD manuals.
  * It emits every instruction's start, length, bytes, mnemonic, operands and
    direct target.
  * It fails on ambiguity, an unsupported encoding, an undecoded byte, an
    overlapping decode, a target into an instruction, out of its function or
    out of `.text`, an unreached instruction, or any disagreement (XD-5).
  * **T-L11** requires exact agreement with the listing on every boundary,
    byte field, mnemonic, operand and target T-L10 uses, through an injective
    spelling table. **No T-L10 result is accepted without a passing T-L11 on
    the same digests** (XD-7).
  * XD is class-E evidence tooling (X-17), never a build input,
    independently reviewed (XD-9), version-recorded (XD-8) and self-tested
    (T-L12).
  * **Codex re-derives or independently exercises the decoding at D9-2**
    (XD-11), so that neither binutils nor XD is a single authority.
    Re-derivation is recommended (new LD-9).
  * The change is traced through RI-2, BI-6, BI-10, T-L7, T-L10, P-3, P-4,
    D9-2, §6.3 and §8 (the proposal's §5.15.2 table), and through the
    dependent text.
  * **What remains trusted** is stated as TD-1 … TD-4 (§5.15.4) and in §8.
* **LD-8 conditions.** IC-1 passing is a precondition of the build-root claim.
  R-5 **must** actually vary at least one of HA-1 … HA-3 and record which;
  otherwise it does not pass. An unexplained difference remains a hard stop.
  **No diverse double compilation is required.** No text claims that
  reproducibility shows decoder correctness (§5.3.5, §5.3.7, §5.3.8, §5.12.3,
  §6.2, §6.3, §9).

## 2. Assignment requirement → amended section map

| Requirement | Proposal sections |
|---|---|
| **Zero-`ret`:** first build and every accepted image contain no `ret` | §5.1; §5.14 introduction; §5.14.1 (CT-5 absent, forbidden list); §5.14.5; §4.5 |
| promote FA-2; revise function and call structure | §5.1 (entry by `jmp`, `rp11_main` sole C function); §5.2 (`select.h` definitions, `select.c` withdrawn, shim); §5.3.3 (one compile, two objects); §5.14 contract function set |
| revise the CT set | §5.14.1 (CT-4 replaced, CT-5 absent, `call` and every `ret` forbidden, transfer forms stated as encodings, why a `c3` byte is not a `ret`) |
| revise the RI rules | §5.14.2 (RI-1 … RI-4 restated; RI-5, RI-6 as data integrity; RI-7 replaced; reachable graph) |
| revise the source discipline | §5.14.3 (SR-1, SR-2, SR-4 amended; SR-7, SR-8 new; IN-1, IN-2); §5.12.1 T-L1, T-L3 |
| revise the expected listing shape | §5.14.3 "Expected listing shape"; §5.10 (`rp11_main` returns row; stack exhaustion row) |
| remove or supersede every `ret`-permitting recommendation | §0 Result, FD-6; §4.3 C-1; §4.4 item 2; §5.14.5 (FA-2 row superseded); §6.1 P-4 and closing item 3; §8; §9 LD-7; Appendix D (D-1 … D-34) |
| state the T-L8 narrowing precisely | §5.12.1 T-L8 ("what it establishes", "what it does not establish"); §5.2 shim and harness rows |
| retain fail-closed withdrawal | §4.5 (amended FA bullet; new XD bullet; LD-8 bullet); §5.14.5 closing paragraph |
| **Independent decoder** consuming `.text` bytes, not `objdump` mnemonics or boundaries | §5.15.1 XD-1 |
| decode the complete `.text` from `_start` under the closed set | XD-2, XD-3 |
| emit starts, lengths, operands and direct targets | XD-4 |
| exact agreement with every listing boundary, byte field, mnemonic, operand and target used by T-L10 | XD-6; §5.12.1 T-L11; XD-7 |
| fail on ambiguity, unsupported encoding, undecoded byte, overlap, target into an instruction, any disagreement | XD-5 (a) … (g); T-L12 negative vectors (XD-10) |
| evidence tooling, independently reviewed, version-recorded, not a build input | XD-8; XD-9; §5.3.7 X-17; §5.2 rows; §5.11 manifest and H-1 record |
| re-derived or independently exercised by Codex at D9-2 | XD-11; §6.2 D9-2; §9 LD-9 |
| trace through RI-2, BI-6, BI-10, T-L7, T-L10, P-3, P-4, D9-2, §6.3, §8 | §5.14.2 RI-2; §5.12.2 BI-6, BI-10; §5.12.1 T-L7, T-L10; §6.1 P-3, P-4; §6.2 D9-2; §6.3 (two rows); §8 (three rows); summary table §5.15.2 |
| state exactly what remains trusted | §5.15.4 (TD-1 … TD-4, "no longer trusted", "not claimed"); §2.4 AD-14; §8; §5.15.3 |
| **LD-8:** IC-1 must pass | §5.3.7 (IC-1 closing paragraph); §5.12.3; §6.2 D9-3; §4.5 |
| R-5 must actually vary and identify at least one of HA-1 … HA-3 | §5.3.5 R-5; §5.3.8 HA-1 … HA-3 rows |
| unexplained difference remains a hard stop | §5.3.5 closing paragraph; §5.3.8 conditions paragraph |
| no diverse double compilation; no claim that reproducibility proves decoder correctness | §5.3.8; §5.12.3; §6.3 reproducibility row; §9 LD-8; §5.15.3; §5.15.4 |
| dated D2-R2 remediation note | §0-D2R2 (with its own section map); header; supersession marker on §0-D2R1 |

Appendix D quotes all 44 D2-R1 claims that D2-R2 withdraws, narrows,
corrects or supersedes. A script asserted each quotation against the
re-reviewed D2-R1 bytes (`a70f013f…`).

## 3. Requirements implemented

**Documentation only.** The D2 proposal is amended in place, provenance
preserved: the original and D2-R1 headers, the re-reviewed-bytes digest, a
dated §0-D2R2 note, *(D2-R2)* markers on changed text, a supersession marker
on the kept §0-D2R1 note, a new §2.4, a new §5.15 and Appendix D. Appendix C
is unchanged. This handback is new. Four concise pointer files are updated.

The C, assembly, encoding, flag, trace and table text in the proposal is
specification inside a design document. **No source, build script, decoder,
test, toolchain file, dependency, binary, manifest, generated artifact,
configuration or executable content was added or changed.**

## 4. Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md` | amended in place, as §2 maps (`a70f013f…` → `5aea7c59…`) |
| `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r2-zero-ret-decoding-remediation-handback.md` | **new**: this handback |
| `docs/review/Handover information` | title marked "returned"; new *Return state* section before *Return gate and restrictions*. Accepted decisions, active assignment, restrictions and archive links unchanged |
| `docs/project-management/status.md` | new current-status block; the previous block relabelled *Superseded current status*, text unchanged |
| `docs/implementation-plan.md` §20 | new current action (Codex re-reviews); the previous current action relabelled *Superseded current action*, text unchanged |
| `docs/operations/disposable-test-server.md` | a *Restriction at D2-R2 remediation return* banner above the existing D2-R2 assignment banner, which is unchanged |

**Not changed:** the D2-R2 assignment (`7b182696…`); the review and decision
record (`2748a914…`); the D2-R1 assignment (`57500b5b…`); the D2-R1 handback
(`e985d512…`); every other assignment, handback, review, decision, snapshot
and archive, including both archive indexes; R2, D-1, D-2, the
operational-evidence draft and the review manifest; and every Python file,
hook, test and `settings.json`.

**Snapshot note.** No displaced text needed a snapshot: the Handover and
status edits add a block or relabel one without removing text, and the
assignment forbids editing archives.

## 5. Migrations

None.

## 6. Security implications

* **The PO-9 control-flow claim no longer depends on stack integrity.** With
  no `ret`, no `call` and no indirect transfer, no target is read from
  machine state. Hostile `argv` and `envp` therefore cannot become a transfer
  target even through a stack defect (IN-2, RI-7). RI-5 and RI-6 remain, for
  the integrity of the data the kernel receives.
* **The disassembler is no longer a single trusted authority.** A decoding
  error in the pinned `objdump` now causes a T-L11 disagreement, which is a
  stop, instead of passing silently through T-L7, T-L9, T-L10 and R-5.
* **New trusted base, named:** AD-14 (the manuals' encodings and the CPU's
  conformance to them), TD-2 (no misreading common to XD and Codex's
  decoding), TD-3 (XD's provenance independence, a review fact) and TD-4 (the
  interpreters). None is discharged by this design.
* **Cost accepted with LD-7:** inlining removes the selection functions'
  symbol boundaries, so HR-4 attributes input loads from T-L10's load table
  and data flow rather than from a function range (§5.14.4, §8).
* **No environment content is recorded**, and no new host, build or
  operational action is specified beyond I-7's future authority.

## 7. Commands run and results

Tools used: Bash, Read, Edit, Write. Every command was a repository read, a
scratch-directory write or a documentation write.

| Command | Result |
|---|---|
| `cat`, `sed -n`, `grep`, `wc` of `CLAUDE.md`; `.agents/AGENTS.md` (complete); the plan's reading map, §0, §16, §17 and the current §20 entries; the Handover; the assignment; the review and decisions; the D2-R1 assignment and handback; the proposal (complete) | read. No secret file was named or opened |
| `git status --short`, saved to the session scratch directory | 79 entries before this work |
| `sha256sum` of the assignment, the decision record, the D2-R1 assignment and handback, and the proposal | as cited. The proposal equalled the re-reviewed D2-R1 bytes (`a70f013f…`) before amendment |
| a copy of the pre-amendment proposal into the scratch directory | used as the source of Appendix D's quotations |
| Edit tool and Python one-off scripts that replaced proposal and pointer text, each asserting that its anchor occurred exactly once | applied. One script stopped on a non-unique anchor before writing; it was rerun with a unique anchor |
| a Python script that asserted each of Appendix D's 44 quotations is a substring of the D2-R1 bytes, with line breaks normalised to spaces, and that the source digest begins `a70f013f` | all 44 present |
| a Python table-shape check over the proposal (pipe count per row, ignoring code spans) | 0 mismatched rows |
| `sha256sum` and `wc -l` of the amended proposal | `5aea7c59…021b5d`, 2 252 lines |
| documentation checks | §8 |

**Not run, as the assignment prohibits:** any compiler, assembler, linker,
`objdump`, `readelf`, decoder, verifier, tracer, package manager, download,
test suite, hook, `ssh`, `rsync`, `sudo`, `uname` or other host inspection. No
manual, kernel or toolchain source was fetched, so AD-14 and every XD table
citation are unrecorded, and the earlier assumptions remain uncited. No guard
or tool refusal occurred.

## 8. Documentation checks

| Check | Result |
|---|---|
| `git diff --check` over the four tracked pointer files | exit 0; no whitespace error |
| trailing-whitespace and tab counts in the amended proposal and this handback (both untracked) | 0 and 0 in both |
| table-shape check (pipe count per row, ignoring code spans) | 0 mismatched rows in the proposal and in this handback |
| relative-link resolution (Python, `pathlib`) over the six touched files | 346 links. 3 resolve only once URL-decoded: the pre-existing `%20`-encoded links to `Handover information`. **0 broken** |
| `git status --short \| wc -l`, compared with the saved listing | 79 before, 80 after. The only new entry is this handback; the proposal and the four pointer files were already listed. Unrelated user changes were preserved |

## 9. Checks not run, and why

* **No test suite, formatter, linter or type checker.** No code changed, and
  the assignment permits documentation, link and diff checks only. No suite
  figure is cited.
* **No build, binary inspection, decoder, verifier, IC-1 trace or
  reproducibility check.** All are prohibited. XD, T-L10, T-L11, T-L12, IC-1
  and R-1 … R-5 are specified, not performed. The expected listing shape is
  a design expectation, not an observation. Whether the pinned compiler emits
  no `call` and no `ret` for this source is **unknown** until a later build.
* **No manual citation.** The encoding rows XD-3 requires, and AD-14, are
  not written or cited here.
* **Manifest not regenerated or incremented.** No covered source changed.
* **No commit or push.** Not authorized.

## 10. Configuration, deployment and rollback

* **Configuration and deployment:** none.
* **Rollback of this return:**
  * restore the proposal to the D2-R1 bytes (`a70f013f…`). The file is
    untracked, so Git holds no earlier version. A copy was kept in the session
    scratch directory, which is not durable; the bytes are identifiable by
    digest;
  * delete this handback;
  * revert the four pointer edits: the Handover title and *Return state*
    section; the new `status.md` block and relabel; the new §20 action and
    relabel; and the new test-server banner.
* **Rollback of the later implementation:** proposal §5.13, unchanged.

## 11. Assumptions, obligations, decisions and questions for Codex

**Assumption added:** AD-14, load-bearing for P-3 and P-4, named as trusted
and not dischargeable by any decoder.

**Proof obligations:** PO-9's components are extended. D9-2 adds XD, T-L11,
T-L12, XD-9 and XD-11, and accepts T-L10 only with T-L11 (XD-7). D9-3 carries
LD-8's conditions. PO-14, PO-16, PO-17 and PO-18 are unchanged. Everything
remains open.

**Maintainer decisions:** LD-7 and LD-8 are recorded as decided. One new
decision is requested:

* **LD-9:** require Codex's D9-2 decoding to be a re-derivation (option (i)),
  or also accept an independent exercise of XD (option (ii)). The
  recommendation is (i).

Still required, and not granted: the M-14 implementation authority for I-7,
including XD and its corpus; the XD review (XD-9); H-1 and H-2 authority; the
PO-14 citation; and the remaining R2 decisions.

**Focused re-review questions for Codex:**

1. **Zero-`ret` completeness.** With no `call`, no `ret` and no indirect
   transfer, is any x86-64 user-space transfer still able to take its target
   from machine state, for example through a `syscall` return path, a signal
   with no handler, or a stop and continue? Are AD-8, AD-11 and AD-12 still
   the complete set of kernel-mediated cases?
2. **Entry by `jmp`.** Is `and $-16, %rsp; push $0; jmp rp11_main` the right
   entry, given the compiler's alignment assumption and that nothing reads
   the pushed word? Is the §5.10 account of a defective `ret` reaching
   address 0 accurate?
3. **Source discipline sufficiency.** Do `always_inline`, `noreturn`,
   `__builtin_trap()` and SR-1 … SR-8 give the compiler no reason to emit a
   `call` or `ret`? Is anything missing that the pinned GCC might emit, such as
   a `memcpy` or `memset` call or an outlined cold path, that the flags and
   FA-1 would not catch before T-L10?
4. **T-L8 narrowing.** Does §5.12.1 state the narrowing exactly as LD-7
   accepts? Is the freestanding shim plus hosted harness the right structure,
   and is anything claimed for it beyond source and compiler behaviour?
5. **XD independence.** Does XD-1's input rule — its own ELF reader, no
   listing, no binutils output or library, no code shared with T-L7 or T-L10 —
   make its decoding independent of `objdump` in the sense `R4-D2-R1-1`
   requires?
6. **XD failure set.** Is XD-5 complete? In particular, is failing on any
   unreached instruction (XD-5(f)) right, given that the reachability pass
   treats every `syscall`, `exit_group` included, as falling through?
7. **Agreement rule.** Does XD-6, with an injective spelling table and exact
   byte-field comparison, prevent a presentation mapping from hiding a real
   disagreement? Should the listing's operand text be compared at all, or
   only boundaries, bytes and targets?
8. **T-L10 precondition.** Is XD-7 — T-L10 accepted only with T-L11 on the
   same image and listing digests, and re-run over XD's own stream — the
   right precondition?
9. **D9-2 independence.** Is XD-11 option (ii) adequate at all, or should
   LD-9 require (i)? Does either option remove binutils and XD as common-mode
   authorities as the assignment requires?
10. **Trusted base.** Are TD-1 … TD-4 and AD-14 the complete statement of
    what remains trusted for decoding? Is anything else trusted that is not
    named?
11. **LD-8 conditions.** Do §5.3.5, §5.3.7, §5.3.8 and §5.12.3 make all four
    conditions normative, and does any text still imply that reproducibility
    shows decoder correctness?
12. **Residual `ret` text.** Is any recommendation, row or premise that
    permits `ret` still in force? The §0-D2R1 note and Appendix C are kept as
    records and carry supersession markers.
13. **Retention versus withdrawal.** Is retaining D-S1 honest, given that no
    build has shown the compiler emits no `call` or `ret`? Do §4.5's
    conditions state when it must be withdrawn?

## 12. Return state

The §8 checks ran against the returned proposal bytes (`5aea7c59…`). This
handback was edited afterwards only to record their results and to correct
one Appendix D range in §2.

Claude has stopped.

* **Next:** Codex independently re-reviews the amended design against
  `R4-D2-R1-1`, LD-7 and LD-8, then Peter Duscha decides.
* **No implementation assignment exists.**

Throughout: PO-9 and PO-14 remain open; RP-11 remains unwired and unmet;
neither pass is executable or authorized; `plan.is_executable=False`; P5.0-R5
remains Blocking; OD-62 G-A remains conditional; and Package 5.0 remains not
ready.
