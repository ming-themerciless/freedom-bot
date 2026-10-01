# Claude prompt — design the LB-2S static first image

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-D2`

Date: 2026-09-29

Assignee: Claude, design author

Independent reviewer: Codex

State: **assigned repository-only, documentation and read-only analysis only.**
Stop after the design proposal and handback for independent Codex review.

## 1. Objective

Produce a decision-ready design for the compiled static first image
`rp11-launch` used by the conditionally selected LB-2S boundary.

Peter Duscha has decided:

* **M-14:** accept and commission this design pass only;
* **M-9:** conditionally select LB-2S, subject to an accepted launcher design
  and later discharge of PO-9 and PO-14; and
* **M-10:** keep T-A in scope while trusting manager execution settings as
  reviewed, root-controlled input under R-10. T-B remains out of scope.

Design the launcher; do not implement, compile, install or execute it. Do not
redesign the already-remediated R4-D1-2 command-knowability result.

## 2. Controlling inputs

Read completely before designing:

* `.agents/AGENTS.md`;
* the implementation-plan reading map, §0, §16 and §20;
* `docs/review/Handover information`;
* [the R2 proposal](phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md), especially §0-R2, §4.3, §4.4, §7.9 and §9–§14;
* [the R2 handback](phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r2-system-manager-environment-remediation-handback.md);
* [Codex's R2 review](project-review-2026-09-29-p5-r5-rp11-r4-d1-r2-system-manager-environment.md); and
* [the maintainer decision](project-review-2026-09-29-p5-r5-rp11-r4-d1-r2-launch-boundary-decision.md).

The proposal's retained constraints, threats, gates, environment contracts and
proof obligations remain controlling. The decision record controls M-9, M-10
and M-14.

## 3. Required design

Compare technically credible approaches for a tiny static first image and
select one only if the evidence supports it. At minimum assess:

* a freestanding or syscall-only implementation;
* a static non-glibc C runtime such as musl, if applicable;
* a Rust `no_std` or minimal-runtime approach, if applicable; and
* any simpler viable approach identified during analysis.

For each candidate, analyze pre-entry execution; environment, auxiliary-vector,
locale, tunable, NSS, iconv and configuration reads; dynamic-module loading;
architecture and ABI assumptions; binary format; toolchain pinning and
acquisition; reproducibility and byte-drift sources; source-to-binary review;
installed-digest binding; maintenance and supply-chain cost; and how PO-9 can
be proved rather than inferred from a successful test.

The selected design must specify exactly:

1. language/runtime and why its pre-entry path satisfies PO-9;
2. the complete source and build-input boundary;
3. pinned toolchain and reproducible-build procedure;
4. supported target architecture and kernel ABI;
5. accepted argv: exactly `--pass A` after `argv[0]`;
6. `envp` handling: select exactly one grammar-valid `INVOCATION_ID`, copy no
   other input, and define duplicate and malformed-entry handling;
7. descriptor closure, signal reset, signal-mask reset, umask and working
   directory operations in exact order, with failure semantics;
8. literal Python `execve` path, argv and environment;
9. fixed exit codes and non-sensitive diagnostics;
10. partial-failure, interruption and unexpected-kernel-result behaviour;
11. manifest, pass-configuration, H-1 and H-2 binding of sources, build
    definition, toolchain identity, expected binary digest and installed file;
12. repository tests, binary inspection, reproducibility checks and the later
    separately authorized hostile-environment experiment; and
13. rollback and replacement after toolchain, runtime, kernel or architecture
    changes.

## 4. Proof and recommendation discipline

Keep source properties, compiler/linker output, reproducibility, binary
inspection, installed-host evidence, hostile-environment testing and PO-14
separate. PO-14 is not discharged by this launcher design.

A clean output environment is corroboration, not proof that no hostile code
ran before `main`. A static ELF label alone is not proof of PO-9. Do not assume
glibc-static qualifies, accept an unknown pre-entry runtime, or move cleansing
into a dynamically linked helper.

If no candidate supports a defensible PO-9 proof with an acceptable pinned
toolchain, return a decision-ready impossibility result and withdraw the
conditional LB-2S direction. Do not recommend the least-uncertain candidate.

## 5. Deliverables

1. Create
   `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md`.
2. Create
   `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-handback.md`.
3. Update only concise current-state pointers needed to return the design for
   independent review. Do not amend prior proposals, handbacks, reviews,
   decisions, snapshots or archives.

The handback must satisfy implementation-plan §16.3, map every requirement to
proposal sections, disclose assumptions and proof obligations, state commands
and checks, and give Codex focused review questions.

## 6. Scope and prohibitions

This assignment is **documentation-only**. Do not add source, build scripts,
toolchain files, tests, binaries, manifests, generated artifacts, systemd or
polkit files, configuration, migrations, dependencies or executable content.
Do not amend D-1, D-2, the operational-evidence draft or the R2 proposal. Do
not increment the manifest.

No compilation, package installation, dependency download, binary inspection,
loader experiment, interpreter-entry probe, hook run, `systemctl`,
`systemd-run`, `loginctl`, `busctl`, `sudo`, `ssh`, `rsync` or operational
component is authorized. Repository documentation and source may be read.

**No SSH, rsync, synchronization, network or host inspection, `sudo`, database
access, provisioning, controlled write, reboot, verifier, evidence band,
harness `--execute`, real participant, real capture root, operational path,
protected-artifact access, secrets scan, commit or push is authorized.**

Preserve unrelated worktree changes. A guard or tool refusal is a stop
condition and must not be routed around.

## 7. Return gate

Claude stops after the proposal, handback and concise pointer updates. Codex
independently reviews runtime start-up, PO-9 reasoning, toolchain and
reproducibility, the exact syscall/state contract, evidence separation,
manifest/install binding and recommendation honesty. Peter Duscha then decides
whether to accept a launcher design and authorize any later implementation
slice.

No implementation assignment exists. PO-9 and PO-14 remain open. RP-11
remains unwired and unmet; neither pass is executable or authorized;
`plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; and Package 5.0 remains not ready.
