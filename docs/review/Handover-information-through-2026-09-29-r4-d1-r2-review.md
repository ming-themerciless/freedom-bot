# Active handover — LB-2 system-manager environment remediation reviewed — 2026-09-29

This file is the active assignment and restriction entry point. The complete
pre-acceptance state is preserved verbatim in
[`Handover-information-through-2026-09-29-r3-review.md`](Handover-information-through-2026-09-29-r3-review.md).
Dedicated prompts, handbacks, reviews and acceptance records remain durable.

## Current state

Peter Duscha accepted `C-P5.0-R5-RP11-I1-R3-R3` after Codex's independent
review found no Blocking, Important or Optional issue. The correction makes
`PosixFilesystem.create_file` and `openat` release a descriptor exactly once
when acquisition fails after `os.open`, preserves the first causal failure and
performs no pathname cleanup.

Manifest version **26** and review-input digest
`526dd44648833ecb5b7bc5de111478323bf6b44c3ea076916896ba883c7f2f28`
are accepted as reviewed repository inputs only. Independent verification
reproduced 16 focused passes and **3364 passed, 0 skipped** for the whole
evidence package at both the 1024 and default descriptor limits, plus
byte-identical dry-run artifacts.

- [Assignment](phase-5-0-p5-r5-rp11-i1-r3-r3-posix-post-open-release-claude-prompt.md)
- [Claude handback](phase-5-0-p5-r5-rp11-i1-r3-r3-posix-post-open-release-handback.md)
- [Codex review](project-review-2026-09-29-p5-r5-rp11-i1-r3-r3-posix-post-open-release.md)
- [Acceptance record](project-review-2026-09-29-p5-r5-rp11-i1-r3-r3-posix-post-open-release-acceptance.md)

## Next required work

Peter Duscha assigns Claude `C-P5.0-R5-RP11-I1-R3-R4-D1`, a
documentation-only, decision-ready design for C-11 guard-preserving capture and
the exact pinned `rsync`/`ssh` launcher environment.
[Assignment](phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-claude-prompt.md).
Claude must return a proposal and handback, then stop for independent Codex
review. No implementation or wiring is authorized.

## Return state — 2026-09-29

Claude returned R4-D1 documentation-only and has stopped. It recommends O-2
(closed act catalogue; the digest-pinned hook bytes evaluated in-process before
X-1 and every launch, and by catalogue-resolving client hooks) and a closed
`rp11-launcher-env/1` map (`PATH=/usr/bin`, `LC_ALL=C`, and `SSH_AUTH_SOCK`
only under agent authentication). Every viable option needs draft amendment
D-1; M-1 … M-8 are open maintainer decisions. **Codex reviews independently;
Peter Duscha then decides.** No source, hook, manifest or draft changed.

- [Proposal](phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md)
- [Claude handback](phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-handback.md)

## Independent review return — 2026-09-29

Codex found two Blocking design defects: ambient native-loader state can act
before the proposed in-process refusal or gate, and the client hook cannot
inspect A1-12's final runtime-substituted command before the entry process
starts. O-2 and D-1 are not ready for maintainer selection. Claude remediation
and independent re-review are required; no implementation is authorized.

- [Codex review](project-review-2026-09-29-p5-r5-rp11-r4-d1-c11-launcher-contract.md)

## Active remediation assignment — 2026-09-29

Peter Duscha assigns Claude `C-P5.0-R5-RP11-I1-R3-R4-D1-R1`, documentation-only,
to correct both Blocking findings without implementing or wiring RP-11. Claude
must amend the proposal in place, create the named remediation handback, update
concise pointers and stop for independent Codex re-review.

- [Claude remediation assignment](phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r1-c11-launcher-contract-remediation-claude-prompt.md)

## Remediation return state — 2026-09-29

Claude returned R4-D1-R1 documentation-only and has stopped. The proposal is
amended in place (§0 remediation note; Appendix A quotes every withdrawn claim)
as a **decision-ready impossibility result**, not as a recommendation that
meets today's constraints.

* **R4-D1-1.** No repository-only design on the client's ordinary path keeps
  ambient loader state from the entry. Prevention needs a host-established
  boundary (**M-9**: LB-2 service-manager unit, LB-3 `sudo` rule, or LB-1
  static launcher) and a threat-scope choice (**M-10**).
* **R4-D1-2.** Pass A can be made all-literal by amendment **D-2** to A1-12.
  Pass B cannot meet the pre-start criterion as drafted (**M-11**).
* **D-1** is rewritten.

**Codex re-reviews independently; Peter Duscha then decides.** Neither finding
is claimed closed.

- [Amended proposal](phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md)
- [Claude remediation handback](phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r1-c11-launcher-contract-remediation-handback.md)

## Independent remediation re-review return — 2026-09-29

Codex found one remaining Blocking design defect. R4-D1-2 is remediated in the
design: D-2 can make Pass A all-literal, and M-11 truthfully excludes Pass B.
R4-D1-1 remains open because the recommended LB-2 unit adds two environment
variables but does not establish a closed pre-loader environment; manager-level
loader state can still act before the entry's diagnostic check. LB-2 and the
conditional O-2/D-1 direction are not ready for selection. Further
documentation remediation and independent re-review are required.

- [Codex remediation re-review](project-review-2026-09-29-p5-r5-rp11-r4-d1-r1-c11-launcher-contract.md)

## Active R2 remediation assignment — 2026-09-29

Peter Duscha assigns Claude `C-P5.0-R5-RP11-I1-R3-R4-D1-R2`,
documentation-only, to correct the remaining `R4-D1-R1-1` LB-2
pre-loader-environment defect. Claude must establish a credible closed
pre-`execve` environment or withdraw/narrow LB-2 truthfully, amend the proposal
in place, create the named R2 handback, update concise pointers and stop for
independent Codex re-review. R4-D1-2 remains remediated at design level and is
not reopened.

- [Claude R2 remediation assignment](phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r2-system-manager-environment-remediation-claude-prompt.md)

## R2 remediation return state — 2026-09-29

Claude returned R4-D1-R2 documentation-only and has stopped. The proposal is
amended in place (§0-R2; Appendix B quotes every withdrawn or narrowed claim).
**No recommendation is ready.**

* **LB-2 as returned is withdrawn as prevention.** A systemd unit's
  environment is the manager's open global environment plus unit settings,
  less a finite `UnsetEnvironment=` list. No directive builds an allow-list.
* **LB-2S is the specified correction.** `ExecStart=` names a static first
  image, `rp11-launch`, that reads no environment at start-up (PO-9). It
  starts the interpreter with a literal `{INVOCATION_ID, LC_ALL, PATH}`. The
  design also depends on PO-14 (the executor's start environment).
* **Manager execution settings are trusted root input**, reviewed at H-1 and
  H-2. That is not prevention (R-10).
* **New decision M-14** (a compiled static image as a build dependency);
  **M-10 is revised**. LB-3 is not ready. R4-D1-2 is not reopened.

**Codex re-reviews independently; Peter Duscha then decides.** The finding is
not claimed closed.

- [Amended proposal](phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md)
- [Claude R2 remediation handback](phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r2-system-manager-environment-remediation-handback.md)

## Independent R2 review return — 2026-09-29

Codex reviewed R4-D1-R2 with **no Blocking, Important or Optional finding**.
`R4-D1-R1-1` is remediated at the design-document level: the original LB-2
prevention claim is withdrawn, and LB-2S makes a static first image—subject to
load-bearing PO-9 and PO-14—the only pre-loader environment boundary. No
recommendation is ready. Peter Duscha decides whether to commission M-14 and
make M-9 and M-10; no implementation or operational authority is created.

- [Codex R2 review](project-review-2026-09-29-p5-r5-rp11-r4-d1-r2-system-manager-environment.md)

## Restrictions and gates

**No SSH, rsync, synchronization, network or host inspection, `sudo`, database
access, provisioning, controlled write, reboot, verifier, evidence band, harness
`--execute`, real participant, real capture root, operational path,
protected-artifact access, secrets scan, commit or push is authorized.**

Neither operational pass is executable or authorized; `plan.is_executable=False`;
P5.0-R5 remains Blocking; OD-62 G-A remains conditional; and Package 5.0
remains not ready.

## Archives

- [Handover at the R3 review return](Handover-information-through-2026-09-29-r3-review.md)
- [Handover archive index](handover-archive/README.md)
