# Active handover — LB-2S static-launcher design D2-R1 remediation returned for Codex re-review — 2026-09-29

This is the concise active assignment and restriction entry point. The full
pre-decision state is preserved verbatim in
[`Handover-information-through-2026-09-29-r4-d1-r2-review.md`](Handover-information-through-2026-09-29-r4-d1-r2-review.md).

## Accepted decisions

Peter Duscha accepted Codex's R2 review with no finding and decided:

* **M-14:** commission a static-launcher design only;
* **M-9:** conditionally select LB-2S, subject to an accepted design and later
  discharge of PO-9 and PO-14; and
* **M-10:** keep T-A in scope while trusting reviewed root-controlled manager
  execution settings under R-10. T-B remains out of scope.

- [Decision record](project-review-2026-09-29-p5-r5-rp11-r4-d1-r2-launch-boundary-decision.md)
- [Codex R2 review](project-review-2026-09-29-p5-r5-rp11-r4-d1-r2-system-manager-environment.md)
- [R2 proposal](phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md)

## Active assignment

Codex's review of the D2 design found `R4-D2-1` (Blocking: the PO-9
control-flow proof ignored `ret`), `R4-D2-2` (Important: the build-input
closure omitted `/bin/sh`, `env` and runtime inputs) and `R4-D2-3`
(Important: hostile vectors could exceed `execve` limits, and HX-5 omitted
the diagnostic). Claude is assigned `C-P5.0-R5-RP11-I1-R3-R4-D2-R1`,
documentation-only, to remediate exactly those findings in the D2 proposal,
or withdraw D-S1 truthfully, and stop for Codex re-review. The original D2
assignment remains controlling except as corrected.

- [D2-R1 remediation assignment](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r1-static-launcher-design-remediation-claude-prompt.md)
- [Original D2 assignment](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-claude-prompt.md)

## Return state

Claude returned `C-P5.0-R5-RP11-I1-R3-R4-D2-R1` documentation-only and
stopped. D-S1 is retained, with three corrections:

* **The PO-9 argument.** `ret` is permitted only under closed
  control-transfer classes and return-integrity rules, checked by a new
  listing verifier and by human review. Fail-closed alternatives are named.
* **The build-input claim.** It now binds the whole build root and names the
  unpinnable host inputs.
* **The hostile experiment.** It has bounded vectors, entry evidence and
  exact golden sequences.

No finding is claimed closed, and nothing is discharged. **Next:** Codex
re-reviews independently; Peter Duscha then decides.

- [Amended design proposal](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md)
- [D2-R1 remediation handback](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r1-static-launcher-design-remediation-handback.md)
- [D2 design handback](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-handback.md)

## Restrictions and gates

**Documentation and repository reads only. No source, build, test, dependency,
binary, manifest, generated artifact, configuration, host or operational
change is authorized. No compilation, installation, download, SSH, rsync,
network or host inspection, `sudo`, database access, provisioning, controlled
write, reboot, verifier, evidence band, harness `--execute`, real participant,
real capture root, operational path, protected-artifact access, secrets scan,
commit or push is authorized.**

PO-9 and PO-14 remain open. RP-11 remains unwired and unmet; neither pass is
executable or authorized; `plan.is_executable=False`; P5.0-R5 remains
Blocking; OD-62 G-A remains conditional; and Package 5.0 remains not ready.

## Archives

- [Pre-decision handover snapshot](Handover-information-through-2026-09-29-r4-d1-r2-review.md)
- [Handover archive index](handover-archive/README.md)
