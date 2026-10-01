# Codex independent review — R4-D1-R2 system-manager environment remediation

Review ID: `C-P5.0-R5-RP11-I1-R3-R4-D1-R2-REV1`

Date: 2026-09-29

Reviewed returns:

* [`phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md)
* [`phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r2-system-manager-environment-remediation-handback.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r2-system-manager-environment-remediation-handback.md)

Controlling finding:
[`R4-D1-R1-1`](project-review-2026-09-29-p5-r5-rp11-r4-d1-r1-c11-launcher-contract.md)

Disposition: **no Blocking, Important or Optional finding. R4-D1-R1-1 is
remediated at the design-document level.** The return is ready for Peter
Duscha's decision on whether to commission the static-launcher design and make
the other named choices. This review does not select LB-2S, accept M-14, close
any proof obligation, authorize implementation, satisfy RP-11 or make either
pass executable.

## Review result

The amendment corrects the remaining contradiction rather than moving it to
another dynamically loaded process:

* The original LB-2 unit is explicitly withdrawn as prevention. The proposal
  now states that systemd unit directives add to, override or finitely remove
  names from an open manager environment and do not create a general
  allow-list for a dynamically linked `ExecStart=` image.
* LB-2U's finite `UnsetEnvironment=` list and LB-2T's reviewed snapshot are
  correctly classified as deny-list hardening and review, respectively—not
  prevention.
* The proposed LB-2S boundary places the only environment-prevention claim in
  `rp11-launch`: a static first image whose pre-`main` runtime must consume no
  environment and which performs the entry interpreter's `execve` with a
  closed literal map. The Python environment check remains diagnostic only.
* Manager environment, manager execution settings, unit-text properties,
  installation checks, pre-pass checks, host proof obligations and prevention
  are distinguished. Ambient manager environment remains in T-A; execution
  settings are an explicit root-state trust for maintainer decision M-10.
* Non-Claude callers receive the same in-entry enforcement only if the chosen
  launch boundary exists. The proposal does not credit absent client hooks
  with protection.
* R4-D1-2 remains remediated: D-2 and M-11 are unchanged, and the D-1 edit is
  only the traced consequence of renaming the conditional boundary to LB-2S.

## Conditions that remain open, but are not review findings

The proposal truthfully says that **no recommendation is ready**. LB-2S is a
conditional direction requiring all of the following before any implementation
or operational use can be considered:

1. Peter Duscha's decisions M-9, M-14 and M-10;
2. a separate design for the compiled static image, runtime, pinned toolchain,
   reproducible build and installed-digest binding;
3. discharge of load-bearing PO-9 and PO-14, with withdrawal of LB-2S if
   either fails;
4. separately authorized implementation, installation and pre-pass work; and
5. all other retained decisions and proof obligations before RP-11 can be
   satisfied.

Those are accurately presented as prerequisites and limitations rather than
as evidence already obtained. The unverified systemd semantics and proposed
static runtime therefore do not create a review finding in this
documentation-only impossibility/decision result.

## Review conclusion

No implementation, hook, source, manifest, artifact, configuration,
operational draft or launcher was changed or tested by this review. Review
activity was repository-local and read-only except for this review record and
concise current-state pointers. No SSH, rsync, synchronization, network or host
inspection, protected-artifact access, secrets scan, operational path, commit
or push occurred.

RP-11 remains unwired and unmet; neither pass is executable or authorized;
`plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; and Package 5.0 remains not ready. Peter Duscha is the decision
and acceptance authority.
