# Project status

This file is the current operational status entry point. The complete
pre-acceptance state is preserved verbatim in
[`status-through-2026-09-29-r3-review.md`](status-through-2026-09-29-r3-review.md).
The decision register, RAID register, change log and dedicated review records
remain authoritative for their subjects.

## Current status — LB-2 system-manager environment remediation reviewed — 2026-09-29

Codex reviewed `C-P5.0-R5-RP11-I1-R3-R4-D1-R2` with **no Blocking,
Important or Optional finding**. `R4-D1-R1-1` is remediated at the
design-document level. The original LB-2 prevention claim is withdrawn; LB-2S
is conditional on a static first-image design, M-9/M-14/M-10 and load-bearing
PO-9/PO-14. No recommendation is ready and no implementation authority exists.
Peter Duscha decides the next bounded direction.

[Codex R2 review](../review/project-review-2026-09-29-p5-r5-rp11-r4-d1-r2-system-manager-environment.md)

**Superseded current status — R2 remediation returned.**

Claude returned `C-P5.0-R5-RP11-I1-R3-R4-D1-R2` documentation-only and
stopped. **No recommendation is ready.**

* **LB-2 as returned is withdrawn as prevention.** A systemd unit cannot build
  an allow-list environment: the manager's global environment is open and
  mutable, and `UnsetEnvironment=` is a finite deny-list.
* **LB-2S is the specified correction.** A static first image, `rp11-launch`,
  starts the entry with a literal environment. It depends on PO-9 and PO-14,
  and on new decision M-14 (a compiled build dependency).
* **Trust and threat scope.** Manager execution settings are reviewed root
  input, not prevention (R-10), and M-10 is revised.
* **Scope.** R4-D1-2 is not reopened.

Codex re-reviews independently; Peter Duscha then decides. The finding is not
claimed closed. No source, hook, manifest, artifact or draft changed.

[Claude R2 remediation handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r2-system-manager-environment-remediation-handback.md)

**Superseded current status — R2 remediation assigned.** Peter Duscha assigns Claude `C-P5.0-R5-RP11-I1-R3-R4-D1-R2`,
documentation-only, to remediate the remaining `R4-D1-R1-1` finding. Claude
must establish a credible closed pre-`execve` environment for LB-2 or
withdraw/narrow that direction truthfully, then stop for independent Codex
re-review. R4-D1-2 remains remediated at design level. No implementation or
operational authority exists.

[Claude R2 remediation assignment](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r2-system-manager-environment-remediation-claude-prompt.md)

**Superseded current status — remediation re-reviewed.**

**Independent re-review return.** Codex found one remaining Blocking design
defect. R4-D1-2 is remediated in the design, but R4-D1-1 remains open: the
recommended LB-2 unit does not establish a closed pre-loader environment, so
manager-level loader state could act before the entry's diagnostic check.
LB-2 and the conditional O-2/D-1 direction are not ready for selection.
Further documentation remediation and independent re-review are required.

[Codex remediation re-review](../review/project-review-2026-09-29-p5-r5-rp11-r4-d1-r1-c11-launcher-contract.md)

Claude returned `C-P5.0-R5-RP11-I1-R3-R4-D1-R1` documentation-only and
stopped. The proposal is amended in place as a decision-ready impossibility
result with minimum maintainer choices:

* **R4-D1-1.** Ambient loader state can be kept from the entry only by a
  host-established launch boundary (M-9, needing provisioning) under a chosen
  threat scope (M-10).
* **R4-D1-2.** Pass A becomes all-literal under draft amendment D-2. Pass B is
  out of scope (M-11).
* **D-1** is rewritten.

Codex re-reviews independently; Peter Duscha then decides. Neither finding is
claimed closed. No source, hook, manifest, artifact or draft changed.

**Superseded current status (remediation assigned).** Codex independently reviewed Claude's documentation-only R4-D1 return and found
two Blocking design defects. Ambient dynamic-loader state acts before the
proposed entry can refuse it, defeating the claimed in-process enforcement.
Separately, A1-12's runtime value does not exist when the client hook runs, so
the hook cannot inspect its final command before process start as O-2 and D-1
claim. O-2 and D-1 are not ready for Peter Duscha's decision. Claude remediation
`C-P5.0-R5-RP11-I1-R3-R4-D1-R1` is now assigned, documentation-only, followed
by independent Codex re-review. No implementation is authorized.

### Assignment context

Peter Duscha accepted `C-P5.0-R5-RP11-I1-R3-R3`. The post-open descriptor
leaks in `PosixFilesystem.create_file` and `openat` are closed as remediated.
Codex's independent review found no Blocking, Important or Optional issue.

Manifest version **26** and review-input digest
`526dd44648833ecb5b7bc5de111478323bf6b44c3ea076916896ba883c7f2f28`
are accepted as reviewed inputs, not as execution authority. Verification
reproduced 16 focused passes and **3364 passed, 0 skipped** at both the 1024 and
default descriptor limits; dry-run artifacts were byte-identical.

The accepted Option-1 metadata-only rule and the closures of
`RP11-I1-R3-1`, `RP11-I1-R3-2`, `RP11-I1-R3-3`, `RP11-I1-2`,
`RP11-I1-R2-1` and `RP11-I1-R1-1` remain unchanged.

RP-11 is still unwired and unmet. C-11 and the exact pinned launcher environment
remain unresolved; neither pass is executable or authorized; P5.0-R5 remains
Blocking; OD-62 G-A remains conditional; `plan.is_executable=False`; and
Package 5.0 remains not ready. No host, database, operational-pass, commit or
push authority exists.

**Superseded assignment context.** Peter Duscha assigned Claude
`C-P5.0-R5-RP11-I1-R3-R4-D1`, documentation-only, to produce options and a
recommendation for a guard-preserving capture boundary and closed `rsync`/`ssh`
environment contract. Claude stops after handback for independent Codex review;
no implementation authority exists.

## Records and archives

- [R4-D1-R2 Codex review](../review/project-review-2026-09-29-p5-r5-rp11-r4-d1-r2-system-manager-environment.md)
- [R4-D1-R2 Claude remediation handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r2-system-manager-environment-remediation-handback.md)
- [R4-D1-R2 Claude remediation assignment](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r2-system-manager-environment-remediation-claude-prompt.md)
- [R4-D1-R1 Codex remediation re-review](../review/project-review-2026-09-29-p5-r5-rp11-r4-d1-r1-c11-launcher-contract.md)
- [R4-D1-R1 Claude remediation handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r1-c11-launcher-contract-remediation-handback.md)
- [R4-D1-R1 Claude remediation assignment](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r1-c11-launcher-contract-remediation-claude-prompt.md)
- [R4-D1 Codex review](../review/project-review-2026-09-29-p5-r5-rp11-r4-d1-c11-launcher-contract.md)
- [R4-D1 proposal](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md)
- [R4-D1 Claude handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-handback.md)
- [R3 acceptance](../review/project-review-2026-09-29-p5-r5-rp11-i1-r3-r3-posix-post-open-release-acceptance.md)
- [R4-D1 Claude assignment](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-claude-prompt.md)
- [R3 Codex review](../review/project-review-2026-09-29-p5-r5-rp11-i1-r3-r3-posix-post-open-release.md)
- [R3 Claude handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r3-posix-post-open-release-handback.md)
- [Option-1 alignment acceptance](../review/project-review-2026-09-29-p5-r5-rp11-option-1-alignment-acceptance.md)
- [Status at the R3 review return](status-through-2026-09-29-r3-review.md)
- [Status archive index](status-archive/README.md)
