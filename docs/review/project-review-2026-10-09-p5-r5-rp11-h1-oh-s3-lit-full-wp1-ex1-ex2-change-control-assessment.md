# EX-1 and EX-2 §0.2 impact assessment and Technical Lead review — 2026-10-09

## 1. Purpose and status

This record completes implementation-plan §0.2 steps 2 and the Technical Lead
part of step 3 for the two change items opened after Peter Duscha accepted WP-1
and selected B2-F, both lifecycle acts in, and B3-OUT. It assesses EX-1 and
EX-2 separately. Codex acts as the working Technical Lead for this bounded
change-control assessment at Peter's request.

This record is a recommendation, not approval. EX-1 and EX-2 remain proposed,
BC-4 remains unchanged and not yet effective for them, and WP-2 remains blocked
until Peter explicitly records the Product Owner recommendation and Acceptance
Authority approval and makes baseline v1.8 effective.

## 2. Common assessment

The selected combination is canonical matrix row F-1: B2-F; `AP-2` in; OS-6
`stop` in; B3-OUT. It contains EX-1 and EX-2, contains no EX-3, and needs no
B2-N or Python-free installer design before WP-2. It preserves the commissioned
WP-2 through WP-7 order and leaves BC-2 for any later WP-9 decision.

BC-4 already says to except “`sudo`-started procedures or the installer class
from LR-1 … LR-2 (BQ-2, BQ-3).” EX-1 is the narrower BQ-2 use specified by R8
§9.3—`sudo` alone outside LR-2—and EX-2 is the installer-class use expressly
named by BC-4. The assessment therefore finds that **BC-4 does not need to be
widened or reworded** for these choices. Approval makes the two selected uses
effective; it creates no EX-3 authority and no exception for a dynamic child.

The exceptions alter the accepted LIT-FULL release boundary. §0.2 step 5
therefore applies. The next baseline is **v1.8**, consisting only of the two
approved boundary exceptions and their recorded consequences. It does not
select LIT-FULL for implementation, establish concrete Route 3, approve BC-2,
or authorize WP-2, a host action, or implementation.

## 3. EX-1 impact assessment

**Change.** For `attest`, the `AP-2` holder-creation act and the OS-6
interruption, the root procedure begins at the first design-controlled static
image that `sudo` executes. `sudo`, and nothing else, is a launch preamble
outside the inventoried process tree and an exception to LR-2 only. LR-1 and
LR-3 through LR-6 apply in full to the first image and everything beneath it.

| §0.2 dimension | Assessed impact |
|---|---|
| Scope and affected requirements | Changes BQ-2, the LIT-FULL root-procedure boundary, LR-2's application to the launch preamble and the selected use of BC-4. It does not relax LR-1 or LR-3 through LR-6, exclude either lifecycle act, or permit `systemd-run`, `systemctl` or any other dynamic child beneath the first image. |
| Dependencies | Removes B2-N as a prerequisite. WP-2 through WP-7 must inventory, specify, build, prove and map static `attest`, `start` and `stop` roles. Their first images must apply RH-1 through RH-3 and satisfy the remaining LR criteria. EX-3 remains absent. |
| Estimate and schedule | Adds no pre-WP-2 work package and no current calendar commitment. Relative to B2-S it avoids the separate B2-N design. It does not remove the `start` and `stop` role work already allocated to WP-2 through WP-7; WP-7 remains responsible for the readiness estimate. |
| Risk | Accepted residual: the distribution `sudo` binary, its dynamic loader and its pre-exec environment handling are outside the LIT-FULL process-tree proof. The exception is tightly bounded to `sudo`; a dynamic program at or below the first controlled image remains a failure. Risk is reduced by the static first-image requirement, RH-1 through RH-3 and the closed no-dynamic-child rule. |
| Testing | WP-5 proof must show the inventoried tree begins at the first controlled image; each executed image at or below it is static and has no `PT_INTERP`; no CPython, dynamic loader or dynamic child appears below it; and `attest`, `start` and `stop` meet their role-specific negative tests. Evidence must not claim to prove `sudo`'s own loader absent. |
| Migration and data | None. No schema, stored data, migration, data ownership, privacy or retention change. |
| Operations and security | No present sudoers, package, host, service or credential change. Later implementation must preserve the exact command-to-static-image mapping and fail closed if the first image or descendants do not match the approved proof. The exception grants no general permission to add dynamic privileged launchers. |
| Rollback/recovery | Before implementation, withdraw EX-1 and return BQ-2 to change control. After dependent design or implementation, a rollback requires a new boundary decision and either B2-N or withdrawal of the affected LIT-FULL design; it cannot silently move `sudo` inside LR-2. |

## 4. EX-2 impact assessment

**Change.** The installer class—H-1, RB-1, RS-1 and H-1R—is outside the
LIT-FULL root-procedure set as an exception to LR-1 and LR-2 under BC-4. HB-1
is the stated residual for the members that run under `sudo`'s environment.
The record asserts no invocation literal for H-1R.

| §0.2 dimension | Assessed impact |
|---|---|
| Scope and affected requirements | Changes BQ-3, the LIT-FULL root-procedure boundary, LR-1/LR-2 coverage for the named installer class, BC-4's selected use and HB-1's disposition. It does not remove installer integrity requirements, classify any other operation outside the set, or infer how H-1R is invoked. |
| Dependencies | Removes the Python-free installer as a prerequisite. H-1, RB-1 and RS-1 retain the accepted verified-exec-stub route and `/usr/bin/python3.14` contract; H-1R stays separately authorized with its invocation unresolved. AP-0, AM-0 and H-2 must re-verify installed artifacts against the H-1 record and maintainer-supplied A-2 pins before use. |
| Estimate and schedule | Adds no pre-WP-2 design package and no current calendar commitment. Relative to B3-IN it avoids designing and proving the largest additional static image. It preserves later inventory, interface, proof and mapping work needed to keep the boundary and verification chain explicit. WP-7 remains responsible for the readiness estimate. |
| Risk | Accepted residual: installer-class Python, its dynamic loader and `sudo` environment can affect installer execution outside the LIT-FULL tree. A faulty or compromised installer may write wrong bytes. The activation refuses to use those bytes unless the independent AP-0, AM-0 and H-2 checks match the H-1 record and maintainer-supplied pins. The installer remains outside the grant window, pass and consume step. HB-1 remains explicit rather than being claimed away. |
| Testing | Later installer and activation evidence must cover verified-exec refusal, source and installed-byte digest mismatch, pin mismatch, tamper before use and re-verification by AP-0, AM-0 and H-2. LIT-FULL process-tree tests must state that the installer class is excluded rather than treating its Python processes as an in-boundary pass. H-1R testing waits for a separately accepted invocation contract. |
| Migration and data | None. No schema, stored data, migration, data ownership, privacy or retention change. Installer evidence remains governed by its existing records and separate authorities. |
| Operations and security | No present installation, sudoers, package, host, service or credential change. Future installer operations remain separately authorized, outside activation, and fail closed on verification mismatch. EX-2 is not permission to weaken root ownership, pinning, verified execution or pre-use verification. |
| Rollback/recovery | Before implementation, withdraw EX-2 and reopen BQ-3. Moving the installer class into the set later requires B3-IN change control plus the separately authorized and independently reviewed Python-free installer design; exclusion cannot be erased by relabeling the current Python route. |

## 5. Combined effects and baseline decision

- **Scope:** only the two named LIT-FULL boundary exceptions change.
- **Architecture:** the in-boundary static-image architecture remains; its
  outer launch and installer boundaries become explicit.
- **Authority:** no execution authority is created. Approval changes the design
  boundary only.
- **Privacy and data ownership:** unchanged.
- **Release criteria:** changed, because LIT-FULL conformance is evaluated with
  EX-1 and EX-2 rather than literal LR-1/LR-2 coverage of those outer paths.
- **Phase order:** unchanged; WP-2 through WP-7 remain in dependency order.
- **Target range:** no current numeric range changes. WP-7 must estimate the
  selected F-1 design; no omitted prerequisite may be counted as completed work.
- **Testing and operations:** future evidence must state both exclusions and
  must not overclaim literal whole-host absence of CPython or dynamic loaders.
- **Migration:** not applicable; there is no persistent-data change.
- **Baseline:** v1.8 is required because the release boundary changes.

## 6. Product Owner recommendation prepared for adoption

The decision-ready Product Owner recommendation is:

> Approve EX-1 and EX-2 exactly as assessed in this record; make the selected
> uses of existing BC-4 effective without widening BC-4; accept HB-1 for EX-2;
> adopt controlled baseline v1.8 for these boundary changes; and retain every
> stated WP-2, later-design and no-host/no-implementation gate.

Peter must explicitly adopt this recommendation before it counts as the
Product Owner recommendation required by §0.2 step 3.

## 7. Technical Lead review

**Recommendation: approve both changes and baseline v1.8.** The changes are
coherent with the accepted R8 and WP-1 records, BC-4 already covers their exact
classes, the selected F-1 combination avoids uncommissioned prerequisite
designs, and the remaining risks are named with testable downstream controls.
No Blocking or Important technical issue prevents approval.

The recommendation is conditional only on Peter's explicit dual-role action:
adopt the Product Owner recommendation and approve the changes as Acceptance
Authority. The approval must not authorize WP-2 or implementation; those remain
separately gated.

## 8. Verification and limits

This was a repository-documentation assessment. The controlling WP-1 matrix,
R8 BC-4/HB-1 text, implementation-plan §0.2 and current decision records were
reviewed. No host, retained evidence, network, build, test, formatter, package,
service, database, implementation, commit or push action was required or run.

- [WP-1 acceptance and BQ decisions](project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-acceptance-and-bq-decisions.md)
- [WP-1 cumulative R6 proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r6-remediation-proposal.md)
- [Accepted R8 proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md)
- [Open change items](../project-management/change-log.md)
