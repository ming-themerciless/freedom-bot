# Claude prompt — remediate the LB-2S static-launcher design

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-D2-R1`

Date: 2026-09-29

Assignee: Claude, remediation author

Independent reviewer: Codex

State: **assigned repository-only, documentation and read-only analysis only.**
Stop after the amended proposal and remediation handback for independent Codex
re-review.

## 1. Objective

Remediate exactly the three findings from Codex's independent review of the
returned D2 static-launcher design:

1. **`R4-D2-1` — Blocking:** PO-9 premise P-4 treats the absence of indirect
   `call` and `jmp` instructions as a complete control-flow proof but does not
   account for `ret` or any other indirect transfer whose target is derived
   from mutable machine state.
2. **`R4-D2-2` — Important:** the claimed complete reproducible-build input
   closure omits the `/bin/sh` interpreter and the `env` executable used by
   the prescribed build procedure, including whatever runtime inputs those
   programs require.
3. **`R4-D2-3` — Important:** the hostile-environment test contract includes
   input vectors that may exceed kernel `execve` limits before `rp11-launch`
   starts, and HX-5 contradicts the normative diagnostic-before-exit contract.

Do not implement, compile or test a correction. Amend the existing D2 proposal
in place, create the remediation handback named in §6, update only the concise
current-state pointers needed to return the remediation, and stop for
independent re-review.

The selected D-S1 direction is not rejected by these findings, but it may be
retained only if the amended design supplies a complete and truthful PO-9
argument and a reproducible-build and test contract that can actually be
executed as specified. If that cannot be done, return the decision-ready
withdrawal required by the original assignment rather than weakening PO-9.

## 2. Controlling inputs

Read completely before editing:

* `.agents/AGENTS.md`;
* the implementation-plan reading map, §0, §16 and §20;
* `docs/review/Handover information`;
* [the original D2 assignment](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-claude-prompt.md);
* [the D2 proposal](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md);
* [the D2 handback](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-handback.md);
* [the R2 proposal](phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md),
  especially §0-R2, §4.3, §4.4, §7.9 and §9–§14;
* [Codex's R2 review](project-review-2026-09-29-p5-r5-rp11-r4-d1-r2-system-manager-environment.md);
  and
* [the controlling maintainer decision](project-review-2026-09-29-p5-r5-rp11-r4-d1-r2-launch-boundary-decision.md).

The original D2 assignment's constraints, threats, gates, evidence separation,
prohibitions and recommendation discipline remain in force except where this
prompt expressly requires correction. The three findings above control over
the returned D2 proposal.

## 3. Required correction for R4-D2-1

Repair the PO-9 control-flow argument so that it covers **every** way execution
can move outside ordinary direct fall-through, not only indirect `call` and
`jmp` instructions. The amended proposal must:

* enumerate the complete set of control-transfer instruction classes permitted
  in the built image, including direct branches, direct calls, returns, system
  calls and any architecture-specific transfer the compiler or assembler could
  emit;
* state explicitly whether `ret` is permitted. If it is, specify how binary
  inspection proves that every reachable return target corresponds to the
  intended direct-call site and that no reachable stack write can corrupt a
  saved return address;
* account for `_start`'s call into C, every non-inlined C call, all epilogues,
  tail calls, compiler-generated thunks and fall-through between symbols or
  sections;
* define the stack frame and stack-write review needed for hostile `argv` and
  `envp` inputs, including the fixed-size `INVOCATION_ID` copy and every local
  object;
* strengthen BI-6, BI-7, T-L4 and any related source or listing check so that
  they establish the revised claim instead of merely searching for indirect
  `call` and `jmp` mnemonics;
* revise P-3, P-4 and the §6.1 proof text to name the exact mechanical and
  human-review evidence that makes the reachable control-flow graph complete;
* remove or qualify every statement that says the image has "no indirect
  branch" if reachable `ret` instructions remain; and
* state a fail-closed design alternative if the compiler output cannot support
  a tractable proof—for example verified inlining, direct tail transfers or the
  C-1A assembly fallback—without assuming that alternative already works.

Do not equate a complete disassembly with a complete reachable control-flow
graph. A listing shows instruction bytes; the amended proof must also justify
the targets of every reachable indirect transfer and the integrity of the
machine state from which those targets are obtained.

## 4. Required correction for R4-D2-2

Make the source-to-binary and reproducible-build boundary internally complete.
The amended proposal must:

* trace every executable that runs in R-1 through R-5, including the program
  that constructs the clean environment, the interpreter of `build.sh`, the
  compiler driver and subprograms, assembler, linker, inspection tools and
  digest/comparison tools;
* identify the shared libraries, program data, configuration and other runtime
  inputs each dynamically linked build tool may consume;
* either include `/bin/sh`, `env` and their applicable runtime closure in
  `toolchain.lock`, or replace the claim of a complete closed toolchain with an
  exact, narrower host-tool assumption and explain how independent
  reproducibility limits that assumption;
* distinguish inputs that can change the image bytes from tools used only to
  inspect, serialise or compare evidence, while pinning both classes wherever
  their output is committed or digest-bound;
* reconcile the literal R-2 invocation, `build_env`, `TMPDIR` variation and the
  `build.sh` internal `umask 022` so that R-4 varies only inputs that actually
  reach the build and describes what each variation proves;
* revise §5.2, §5.3.2, §5.3.4, §5.3.5, R-1 … R-5, the manifest binding and the
  evidence-separation table together; and
* preserve the rule that an unexplained byte difference is a stop and never a
  reason merely to update `expected.sha256`.

Do not claim that independent reproducibility makes an omitted executable or
runtime input cease to be an input. It may detect byte drift or constrain the
residual trust, but the input boundary and the evidence claim must still be
stated truthfully.

## 5. Required correction for R4-D2-3

Rewrite the later hostile-environment experiment so every case can establish
that the launcher, rather than the test driver or kernel argument ingestion,
produced the observed result. The amended proposal must:

* state the applicable per-string and aggregate `execve` limits as versioned
  assumptions or later-cited proof inputs, including their dependence on the
  kernel and relevant process limits;
* give concrete sizes and counts for HX-3 that remain below those limits with
  deliberate headroom, while still exercising long entries, many entries,
  entries without `=`, empty entries and non-ASCII bytes;
* require the driver to distinguish failure of its initial `execve` from a
  refusal or failure inside `rp11-launch`;
* split cases when one vector cannot simultaneously exercise all intended
  boundaries without exceeding the aggregate limit;
* make HX-5 require the normative `launch-usage` diagnostic write followed by
  `exit_group(111)`, consistent with §5.9 and the general failure contract;
* review HX-4, HX-7 and every other refusal case for the same exact diagnostic,
  ordering and exit-status consistency;
* state how a closed or blocked standard-error descriptor affects the expected
  trace without silently accepting omission of a diagnostic when descriptor 2
  is usable; and
* keep the experiment explicitly corroborative: none of these corrections may
  promote it into proof of PO-9.

Update the golden sequences and test-result wording together. Do not use a
successful driver return alone as evidence that `rp11-launch` was entered.

## 6. Deliverables

1. Amend in place:
   `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md`.
   Preserve its provenance and add a dated D2-R1 remediation note identifying
   `R4-D2-1`, `R4-D2-2` and `R4-D2-3`, including every claim withdrawn,
   narrowed or replaced.
2. Create:
   `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r1-static-launcher-design-remediation-handback.md`.
   It must satisfy implementation-plan §16.3, map each finding to exact amended
   sections, disclose every unresolved assumption, proof obligation and
   maintainer decision, and give Codex focused re-review questions.
3. Update only concise current-state pointers needed to return the remediation
   for independent review. Do not edit prior assignments, handbacks, reviews,
   decisions, snapshots or archives.

Neither deliverable may claim a finding closed. Only independent Codex
re-review may determine whether the design findings are remediated, and Peter
Duscha remains the decision and acceptance authority.

## 7. Scope and prohibitions

This remains **documentation-only**. Do not add or change C, assembly, linker
scripts, build scripts, toolchain files, tests, binaries, manifests, generated
artifacts, systemd or polkit files, configuration, migrations, dependencies or
any executable content. Do not amend D-1, D-2, the operational-evidence draft,
the R2 proposal, any prior handback or any decision record. Do not increment
the manifest.

No compilation, package installation, dependency download, binary inspection,
loader experiment, interpreter-entry probe, test suite, hook run, `systemctl`,
`systemd-run`, `loginctl`, `busctl`, `sudo`, `ssh`, `rsync` or operational
component is authorized. Repository documentation and source may be read.
Only documentation, relative-link and diff checks may run.

**No SSH, rsync, synchronization, network or host inspection, `sudo`, database
access, provisioning, controlled write, reboot, verifier, evidence band,
harness `--execute`, real participant, real capture root, operational path,
protected-artifact access, secrets scan, commit or push is authorized.**

Preserve unrelated worktree changes. A guard or tool refusal is a stop
condition and must not be routed around.

## 8. Return gate

Claude stops after the amended proposal, D2-R1 remediation handback and concise
pointer updates. Codex independently re-reviews:

* the complete reachable control-flow proof, including returns and stack
  integrity;
* the build-input and tool-runtime closure;
* the feasibility and exact expected traces of the hostile test vectors;
* all dependent PO-9 premises, binary-inspection checks, reproducibility claims
  and evidence-class boundaries; and
* the honesty of the retained recommendation or required withdrawal.

Peter Duscha then decides whether to accept the launcher design or request
further remediation. No implementation assignment exists. PO-9 and PO-14
remain open; RP-11 remains unwired and unmet; neither pass is executable or
authorized; `plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A
remains conditional; and Package 5.0 remains not ready.
