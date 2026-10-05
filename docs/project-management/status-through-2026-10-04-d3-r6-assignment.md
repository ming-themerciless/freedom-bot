# Project status

This is the concise current operational-status entry point. The complete
superseded R2-assignment state is preserved verbatim in
[`status-through-2026-10-01-r5-r3-acceptance.md`](status-through-2026-10-01-r5-r3-acceptance.md).

## Current status — OS-6 decided; one-host H-1 design remediation R6 assigned — 2026-10-04

Peter Duscha accepts Codex's recommendation and decides OS-6: route iii-a is
available only while the capture unit is `active`, its invocation matches the
consume journal and `consumed` is durable. It is unavailable during
`activating`/`start-pre`; the finite start timeout bounds a hung consume step.

Claude is authorized for the narrow repository-only D3-R6 incorporation of
that decision and remediation of `OH-H1-D3-R5-1`, then must stop for
independent Codex re-review.

`OH-H1-D3-R4-1`, `OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` and `OH-H1-D3-2` remain
open.

No host, Git/network retrieval, credential, implementation, build,
installation, H-0/H-1/H-2, activation, evidence, rollback, cleanup, commit or
push authority exists.

[R6 authority](../review/project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r6-authority.md)
· [Claude prompt](../review/phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-r6-claude-prompt.md).

### Superseded D3-R5 re-review status

Codex independently re-reviewed Claude's D3-R5 return and found one Blocking
issue, `OH-H1-D3-R5-1`. D3-R5 proves the one-start-attempt property only by
narrowing route iii-a from `activating` or `active` to `active` after durable
consumption. That is a maintainer choice rather than an authorized refinement.

Peter must decide whether to accept OS-6 or retain the D3-R4 interruption
route and require a design that closes CX-4. `OH-H1-D3-R4-1`,
`OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` and `OH-H1-D3-2` remain open.

No host, Git/network retrieval, credential, implementation, build,
installation, H-0/H-1/H-2, activation, evidence, rollback, cleanup, commit or
push authority exists.

[Independent R5 re-review](../review/project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r5.md)
· [Claude return](../review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md#16-d3-r5-remediation-and-handback-d3-r5-2026-10-04).

### Superseded R5 remediation-assigned status

Peter Duscha accepts Codex's D3-R4 re-review and authorizes Claude's narrow
repository-only remediation of Blocking finding `OH-H1-D3-R4-1`. Claude must
make the one-start-attempt boundary true for every CP failure path, revise the
inactive proposal and stop for independent Codex re-review.

`OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` and `OH-H1-D3-2` remain open.

No host, Git/network retrieval, credential, implementation, build,
installation, H-0/H-1/H-2, activation, evidence, rollback, cleanup, commit or
push authority exists.

[R5 authority](../review/project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r5-authority.md)
· [Claude prompt](../review/phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-r5-claude-prompt.md).

### Superseded D3-R4 re-review status

Codex independently re-reviewed Claude's D3-R4 return and found one Blocking
defect, `OH-H1-D3-R4-1`: CP's one-shot marker is created only at CP-4, so a
failure at CP-0, CP-1 or CP-2 leaves no barrier against a later start in the
same activation. This contradicts the terminal table, proof item 7, CX-2 and
the required one-shot contract.

`OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` and `OH-H1-D3-2` remain open. Peter must
decide the review disposition and whether to authorize a narrow repository-only
successor remediation.

No host, Git/network retrieval, credential, implementation, build,
installation, H-0/H-1/H-2, activation, evidence, rollback, cleanup, commit or
push authority exists.

[Independent R4 re-review](../review/project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r4.md)
· [Claude return](../review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md#15-d3-r4-remediation-and-handback-d3-r4-2026-10-04).

### Superseded R4 remediation-assigned status

Peter Duscha accepts Codex's clean D3-R3 re-review, closes
`OH-H1-D3-R2-2`, decides OH-D-10 as Option A with interruption route iii-a,
and authorizes Claude's narrow repository-only R4 incorporation into the
inactive proposal. `OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` and `OH-H1-D3-2` remain
open pending the return and independent re-review.

No host, Git/network retrieval, credential, implementation, build,
installation, H-0/H-1/H-2, activation, evidence, rollback, cleanup, commit or
push authority exists.

[R3 re-review](../review/project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r3.md)
· [R4 authority](../review/project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r4-authority.md)
· [Claude prompt](../review/phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-r4-claude-prompt.md).

### Superseded R3 remediation-assigned status

Peter Duscha accepts Codex's D3-R2 re-review and authorizes Claude's narrow
repository-only remediation of Blocking findings `OH-H1-D3-R2-1` and
`OH-H1-D3-R2-2`. Claude must couple cleanup mechanically to the pass terminal
transition and complete attributable activation cleanup when evidence is
unwritable, then stop for independent Codex re-review. `OH-H1-D3-2` and
`OH-H1-D3-R1-1` remain open.

No host, Git/network retrieval, credential, implementation, build,
installation, H-0/H-1/H-2, activation, evidence, rollback, cleanup, commit or
push authority exists.

[R3 authority](../review/project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r3-authority.md)
· [Claude prompt](../review/phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-r3-claude-prompt.md).

### Superseded R2 re-review status

Codex independently re-reviewed Claude's D3-R2 return. The boot-cleared `/run`
and PID-1 supervision direction holds, but two Blocking findings remain:
`OH-H1-D3-R2-1` for the normal post-pass polling/cleanup interval with a live
grant, and `OH-H1-D3-R2-2` for attributable `pass-a.json` left indefinitely
when evidence remains unwritable. `OH-H1-D3-2` and `OH-H1-D3-R1-1` remain
open.

Peter must decide the review disposition and any narrow successor remediation.
No host, Git/network retrieval, credential, implementation, build,
installation, H-0/H-1/H-2, activation, evidence, rollback, cleanup, commit or
push authority exists.

[Independent R2 re-review](../review/project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r2.md)
· [Claude return](../review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md#13-d3-r2-remediation-and-handback-d3-r2-2026-10-04).

### Superseded R2 remediation-assigned status

Peter Duscha accepts Codex's D3-R1 re-review, closes `OH-H1-D3-1`, and
authorizes Claude's narrow repository-only remediation of Blocking finding
`OH-H1-D3-R1-1`. `OH-H1-D3-2` remains open. The successor must enforce the
one-pass/one-boot grant boundary across death, session loss, power loss and
reboot, then stop for independent Codex re-review.

No host, Git/network retrieval, credential, implementation, build,
installation, H-0/H-1/H-2, activation, evidence, rollback, cleanup, commit or
push authority exists.

[R2 authority](../review/project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r2-authority.md)
· [Claude prompt](../review/phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-r2-claude-prompt.md).

### Superseded D3-R1 re-review status

Codex independently re-reviewed Claude's D3-R1 return. `OH-H1-D3-1` is
remediated and ready for Peter to close. `OH-H1-D3-2` remains open under new
Blocking finding `OH-H1-D3-R1-1`: cleanup after process/session loss or reboot
is deferred until a later actor reaches the host, allowing a Polkit grant
authorized for the prior boot/pass to remain live.

Peter must decide the review disposition and any narrow successor remediation.
No host, Git/network retrieval, credential, implementation, build,
installation, H-0/H-1/H-2, activation, evidence, rollback, cleanup, commit or
push authority exists.

[Independent re-review](../review/project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation.md)
· [Claude return](../review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md#12-d3-r1-remediation-and-handback-d3-r1-2026-10-04).

### Superseded remediation-assigned status

Peter Duscha authorizes Claude to perform the repository-only remediation of
Blocking findings `OH-H1-D3-1` and `OH-H1-D3-2`. Claude must incorporate
accepted OH-D-1 through OH-D-9, revise the inactive proposal and stop for
independent Codex re-review. No host, Git/network retrieval, credential,
implementation, build, installation, H-0/H-1/H-2, activation, evidence,
rollback, cleanup, commit or push authority exists.

[Authority](../review/project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-authority.md)
· [Claude prompt](../review/phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-claude-prompt.md).

### Superseded decisions-recorded status

Peter Duscha accepts OH-D-1 through OH-D-9 on Codex's recommendation. Claude's
BLOCKED DESIGN return is accepted as valid, but the proposed H-1 portion is not
decision-ready: Blocking findings `OH-H1-D3-1` and `OH-H1-D3-2` require a
crash-consistent H-1 publication/recovery contract and a complete ACT/DEACT
publication, record and automatic-cleanup contract.

The current workspace host is confirmed as production and is prohibited as a
source, controller, relay, destination, fallback or rollback target. A later,
separately authorized workflow will retrieve the pinned commit directly from
the canonical Git remote on `oracle-test`; any required read-only credential
also needs separate authority. No host, network, credential, implementation,
build, installation, H-0/H-1/H-2, activation, evidence, cleanup, commit or
push authority exists.

[Decision](../review/project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-decisions.md)
· [Independent review](../review/project-review-2026-10-04-p5-r5-rp11-h1-oracle-test-one-host-design-amendment.md)
· [Claude proposal](../review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md).

### Superseded design-assigned status

Peter Duscha authorizes Claude's repository-only design amendment for local
H-1 installation and RP-11 evidence execution on `oracle-test` under `ubuntu`.
The production server remains outside scope. Claude returns an inactive
decision-ready proposal or BLOCKED DESIGN for independent Codex review. No
host, implementation, build or H-1 authority exists.

[Design authority](../review/project-review-2026-10-04-p5-r5-rp11-h1-oracle-test-one-host-design-authority.md)
· [Claude prompt](../review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-claude-prompt.md).

### Superseded topology-decision state

Peter Duscha supersedes the production-host H-1 direction. H-1 installation
and RP-11 test/evidence execution will be local to disposable `oracle-test`
under the existing `ubuntu` account. The production Freedom-Blades/Foundry
server is outside scope and must remain untouched. H-1 remains blocked pending
a reviewed one-host design amendment and all later bounded prerequisites.

[Topology correction](../review/project-review-2026-10-04-p5-r5-rp11-h1-oracle-test-topology-correction.md)
· [Archived displaced status](status-through-2026-10-04-production-host-h1-decision.md).

### Superseded decisions-pending state

Codex independently accepts Claude's BLOCKED PREPARATION return with no
finding. The repository is not ready for an H-1 assignment. D9-2 has complete
technical evidence and is recommended Complete, but Peter Duscha must record
that disposition and decide U-1 through U-4 and U-6 through U-10 before any
successor work is activated. No host, implementation or H-1 authority exists.

[Independent review](../review/project-review-2026-10-04-p5-r5-rp11-h1-assignment-preparation.md)
· [Claude handback](../review/phase-5-0-p5-r5-rp11-h1-installed-host-evidence-assignment-preparation-handback.md).

### Superseded preparation authority

Peter Duscha authorizes Claude's repository-only preparation of a
decision-ready static-launcher H-1 installed-host evidence assignment. Claude
must return either an exact inactive proposal or a BLOCKED PREPARATION record
with the prerequisite sequence; Codex then independently reviews it. Initial
inspection found four expected installation inputs and the committed launcher
executable absent. No host, implementation or H-1 execution authority exists.

[Preparation authority](../review/project-review-2026-10-04-p5-r5-rp11-h1-assignment-preparation-authority.md)
· [Claude task](../review/phase-5-0-p5-r5-rp11-h1-installed-host-evidence-assignment-preparation-claude-prompt.md).

### Accepted predecessor state

Peter Duscha accepts Gemini's complete R5 PASS and Codex's independent review.
The static-launcher independent-rebuild step R-5 is accepted and D9-3 is
Complete. The separate package RAID item `P5.0-R5` remains Blocking. PO-9,
PO-14, D9-4, H-1, RP-11 wiring, `plan.is_executable` and Package 5.0 readiness
remain open. No host or cleanup authority is active. The next controlled step
is a separate decision on preparing H-1 installed-host evidence.
[Acceptance](../review/project-review-2026-10-04-p5-r5-rp11-fresh-r5-pass-acceptance.md).

### Superseded acceptance-pending status

Gemini's one-run authority is consumed. Codex independently validates the R5
handback as a complete PASS with no finding and recommends accepting static-launcher R-5 and
treating D9-3 as complete. The result establishes reproducibility and
build-environment evidence only; PO-9, PO-14, D9-4, H-1, RP-11 wiring,
`plan.is_executable` and Package 5.0 readiness remain open. No host or cleanup
authority is active.
[Independent review](../review/project-review-2026-10-04-p5-r5-rp11-fresh-r5-pass.md).

### Superseded R5 activation status

Peter Duscha accepts the reviewed determinism remediation, closes
`FRESH-R4-HS-1`, accepts the D2 amendment and exact R5 assignment, confirms its
identifiers, retains the R4 evidence without cleanup and leaves S10 unchanged.
Focused commit `4cbdf0b6ecabad7484e64ff0485587a17f55dcaf` contains
exactly the 17 reviewed controlled files, and Gemini is activated for one
digest-pinned runner invocation. R-5 remains Blocking and unaccepted pending
the result and independent review.
[Acceptance and activation](../review/project-review-2026-10-04-p5-r5-rp11-fresh-r5-acceptance-and-gemini-activation.md).

### Superseded decisions-pending status

Claude returned the complete `cc1.v` determinism remediation and draft R5
assignment. Codex independently found no implementation finding and recommends
closing `FRESH-R4-HS-1`, confirming the proposed identifiers, retaining R4
remote evidence, leaving S10 unchanged, adding a dated D2 design amendment and
authorizing one focused controlled-file commit. No host, cleanup or R-5
authority is active pending Peter's decisions and the activation record.
[Independent review](../review/project-review-2026-10-04-p5-r5-rp11-fresh-r4-cc1-determinism-remediation.md).

### Superseded remediation-assigned status

Peter Duscha accepts the valid consumed R4 HARD STOP, Codex's independent
review and open Important finding `FRESH-R4-HS-1`. Claude is assigned the
repository-only complete `cc1.v` determinism audit and remediation. Codex will
independently review the return. A successor Gemini run is conditionally next
only after a clean review and an exact digest-pinned assignment and activation
record; no host authority is active now.

[Acceptance and authority](../review/project-review-2026-10-04-p5-r5-rp11-fresh-r4-hard-stop-acceptance-and-remediation-authority.md)
· [Claude prompt](../review/phase-5-0-p5-r5-rp11-fresh-r4-cc1-determinism-remediation-claude-prompt.md).

### Superseded decision-pending status

Gemini's accepted R4 invocation is complete and consumed. Codex independently
confirms a valid, correctly closed HARD STOP at S9. The fresh build passed the
same-invocation R-1/R-2 manifest gate and reproduced all four normative outputs
and the listing byte-for-byte. Only GCC's diagnostic GGC values differed:
baseline `100/131072`, actual `94/2169`. Important finding `FRESH-R4-HS-1`
records that the exact `cc1.v` contract includes host-resource-selected state.

Codex recommends acceptance of the terminal state followed by a repository-only
Claude remediation that pins both GGC values as explicit reviewed compiler
inputs and preserves exact byte equality. No host, cleanup, retry, remediation
or new-run authority is active. R-5 remains Blocking and unaccepted.
[Independent review](../review/project-review-2026-10-04-p5-r5-rp11-fresh-r4-hard-stop.md).

### Superseded R4 activation status

Peter Duscha accepts the clean R4-R1 re-review, closes `R4-D1-1`, confirms the
same-task wait/refusal/no-timeout/attestation decisions and activates Gemini
for one runner invocation. Focused commit `d216cb1b93125c83e13d43b989fd94c2ded01569`
contains exactly the 19 controlled files; their paths match `HEAD`, their pins
match and 75 focused tests pass. R-5 remains Blocking and unaccepted pending
the run, independent review and a further maintainer decision.
[Acceptance and activation](../review/project-review-2026-10-04-p5-r5-rp11-r4-r1-acceptance-and-gemini-activation.md).

### Superseded focused-commit-pending status

Codex independently re-reviewed Claude's wait-contract remediation, reproduced
75 passing focused tests and found no remaining finding. `R4-D1-1` is
recommended Closed as remediated. The 19 controlled runner/resource/test files
remain untracked, so R4 execution would correctly fail S1.4 until a focused
commit records their pinned bytes. No remote access or new run is authorized.
[Independent re-review](../review/project-review-2026-10-04-p5-r5-rp11-antigravity-delivery-redesign-r1.md).

### Superseded R4-R1-assigned status

Claude returned a digest-pinned non-interactive runner, 17 static command
resources, 75 focused tests and the R4 successor proposal. Codex independently
reproduced 75 passing focused tests and found one Important workflow issue:
`R4-D1-1` instructs Gemini to stop before the runner's terminal state if
Antigravity returns early. Claude is assigned a narrow same-task wait-contract
remediation. No remote access or new run is authorized.
[Review](../review/project-review-2026-10-04-p5-r5-rp11-antigravity-delivery-redesign.md)
· [R4-R1 prompt](../review/phase-5-0-p5-r5-rp11-antigravity-delivery-redesign-r1-claude-prompt.md).

### Superseded redesign-assigned status

Peter Duscha accepts the consumed R3 HARD STOP and its two Important findings.
Claude is assigned repository-only implementation and local testing of a
non-interactive, digest-pinned runner and complete successor assignment. It
must eliminate heredoc/EOF dependence and guarantee closeout after first
failure. No `oracle-test` access or new run is authorized.
[Acceptance](../review/project-review-2026-10-03-p5-r5-rp11-fresh-r3-hard-stop-acceptance.md)
· [Claude prompt](../review/phase-5-0-p5-r5-rp11-antigravity-delivery-redesign-claude-prompt.md).

### Superseded unaccepted-HARD-STOP status

Gemini's R3 activation is consumed. Antigravity's background-terminal task did
not execute or emit the Step 1 heredoc and returned exit 0 after approximately
53 minutes and an EOF. Required Step 1 evidence is absent, so the assignment's
HARD STOP rule applies. No remote step ran and `oracle-test` was not accessed.
The handback also lacks mandatory S12.start evidence. Codex records Important
findings `FRESH-R3-HS-1` and `FRESH-R3-HS-2` and recommends redesigning command
delivery before another run.
[Independent review](../review/project-review-2026-10-03-p5-r5-rp11-fresh-r3-hard-stop.md).

No host access, retry or new run is authorized. R-5 remains Blocking and
unaccepted; RP-11 remains unwired and unmet; `plan.is_executable=False`; PO-9
and PO-14 remain open; Package 5.0 remains not ready.

### Superseded R3 activation status

Peter Duscha accepts the independently reviewed R3 assignment, its strict S1.3
evidence rule, work ID `C-P5.0-R5-RP11-FRESH-R5-R3` and proposed handback
path, and activates Gemini for exactly one wholly new run using outer-host
`/var/tmp`. No retry, remediation or cleanup is authorized. R-5 remains
Blocking and unaccepted pending the run, independent review and a further
maintainer decision. [Acceptance and activation](../review/project-review-2026-10-03-p5-r5-rp11-fresh-assignment-r3-acceptance-and-gemini-activation.md).

### Superseded decision-pending status

Claude returned the R3 successor assignment at SHA-256
`9959d93da7fafb194f942657a3851e83652dc8e1b9ec332b0fa5abd7abb72909`
and 109,644 bytes. Codex independently found no Blocking, Important or
Optional issue. The maintainer may accept the strict S1.3 evidence rule,
confirm work ID `C-P5.0-R5-RP11-FRESH-R5-R3` and the proposed handback path,
and activate Gemini for one run. No host authority is active pending that
decision. [Independent review](../review/project-review-2026-10-03-p5-r5-rp11-fresh-assignment-r3.md).

### Superseded preparation status

Codex verified that the server root had 39 GiB free but `/tmp` was a separate
475.4 MiB tmpfs with only 95.1 MiB free. The retained run used about 377 MiB.
Codex deleted exactly the six authorized paths and verified them absent; `/tmp`
then had 470.6 MiB free. Cleanup authority is exhausted and no host access is
active. [Cleanup result](../review/phase-5-0-p5-r5-rp11-fresh-r5-cleanup-result.md).

Claude is assigned repository-only preparation of a standalone successor R-5
assignment using outer-host `/var/tmp` on the root filesystem, with a 4 GiB
preflight floor and complete Step 1 status output. Codex review and maintainer
activation remain required before Gemini may execute it.
[Preparation prompt](../review/phase-5-0-p5-r5-rp11-fresh-r5-new-run-assignment-preparation-claude-prompt.md).

### Superseded accepted-HARD-STOP status

Gemini's fresh-R-5 invocation ended correctly at Step 5 with `Errno 122: Disk
quota exceeded` while unpacking the pinned root under a separately mounted
approximately 475 MiB `/tmp` tmpfs. Peter Duscha accepts Codex's independent
review and the valid HARD STOP. The invocation is consumed and cannot resume.
Codex is now authorized only for bounded quota/mount/size inspection and
deletion of the six retained run paths. One wholly new Gemini run is authorized
for preparation after the cleanup result is incorporated into an exact
assignment. [Decision and authority](../review/project-review-2026-10-03-p5-r5-rp11-fresh-r5-hard-stop-acceptance-and-cleanup-authority.md).

R-5 remains Blocking and unaccepted; RP-11 remains unwired and unmet;
`plan.is_executable=False`; PO-9 and PO-14 remain open; Package 5.0 remains not
ready. `FRESH-R5-HS-1` remains open against the immutable closed handback.

### Superseded activation status

Claude implemented the accepted I-7 repository slice and returned it
([handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-i7-static-launcher-implementation-handback.md)):
the zero-`ret` launcher, pinned build boundary, XD, T-L1 … T-L12, IC-1,
R-1 … R-4, repository tests and manifest version 27. R-5 remains an independent
party's step. Codex's independent review passed the launcher bytes, XD-9 and
XD-11 but found IC-1's environment comparison under-constrained
([review](../review/project-review-2026-10-01-p5-r5-rp11-i7-static-launcher-implementation.md)).
Peter Duscha accepted the recommendations: D-1 is accepted and Claude was
assigned the narrow I-7-R1 exact-environment remediation
([prompt](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-i7-r1-ic1-environment-remediation-claude-prompt.md)).
Claude returned it and has stopped
([handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-i7-r1-ic1-environment-remediation-handback.md)).
IC-1 now compares every traced process's complete environment with a
specified one. A fresh pinned-root IC-1 passes at the R-2 and R-4(a)
checkouts with outputs byte-identical to R-2. The frozen image, listing and
XD digests are unchanged, and the manifest is version 28. Codex independently
found no Blocking, Important or Optional issue. Peter Duscha accepted the
remediation: `I7-R1-1` is Closed as remediated and D-2 is accepted as
implemented.

- [Amended D2 proposal](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md)
- [D2-R2 handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r2-zero-ret-decoding-remediation-handback.md)
- [Acceptance and LD-9 decision](../review/project-review-2026-10-01-p5-r5-rp11-r4-d2-r2-acceptance.md)
- [I-7 implementation prompt](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-i7-static-launcher-implementation-claude-prompt.md)
- [I-7 implementation handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-i7-static-launcher-implementation-handback.md)
- [I-7-R1 acceptance](../review/project-review-2026-10-01-p5-r5-rp11-i7-r1-acceptance.md)
- [I-7-R1 independent re-review](../review/project-review-2026-10-01-p5-r5-rp11-i7-r1-ic1-environment-remediation.md)

Peter accepted the Antigravity-reviewed
[R-5 assignment](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-independent-rebuild-assignment.md)
and named Gemini as the independent assignee
([review](../review/project-review-2026-10-01-p5-r5-rp11-r5-assignment-antigravity.md),
[acceptance](../review/project-review-2026-10-01-p5-r5-rp11-r5-assignment-acceptance.md)).
That assignment covered only one bounded run, which has since stopped; it
created no installation or operational authority. PO-9 and PO-14 remain open;
RP-11 remains unwired and unmet;
`plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; and Package 5.0 remains not ready.

The first R-5 attempt stopped before provisioning because `bubblewrap` was
absent. Codex confirmed the dependency and raised Important finding `R5-R1-1`
against a contradictory cleanup claim. Peter narrowly authorized Gemini to
install Ubuntu's `bubblewrap` package, record it, resume with wholly fresh
disposable directories, correct the handback and stop
([review](../review/project-review-2026-10-01-p5-r5-rp11-r5-bwrap-stop.md),
[authority](../review/project-review-2026-10-01-p5-r5-rp11-r5-bwrap-install-authority.md)).

The resumed run reproduced the frozen outputs with all three HA dimensions
varied, but R-5 is not accepted: the required same-invocation R-1/R-2 gate did
not run, and `cc1.v` changed without an exact explanation. The initial returned
handback also misstated the pinned snapshot date. Gemini's repository-only R2
remediation corrected that date, introduced the same-invocation R-1/R-2 manifest
gate and withdrew the erroneous R-5 PASS
([prompt](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r2-orchestration-remediation-gemini-prompt.md),
[handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r2-orchestration-remediation-handback.md)).
Codex's review then required R3: Gemini removed the unsafe causal regex
override from `cc1check.py`, so byte equality is the only route to `PASS`
([prompt](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r3-cc1-comparison-remediation-gemini-prompt.md),
[handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r3-cc1-comparison-remediation-handback.md)).
Codex independently reproduced 4,019 passing repository tests, with 12
toolchain-dependent skips because no accepted local root was available, plus
clean compilation, byte-range checks and `git diff --check`. Peter Duscha
accepted R3 on that recommendation
([acceptance](../review/project-review-2026-10-01-p5-r5-rp11-r5-r3-acceptance.md)).

Gemini's R4 bounded recovery ended in Branch B: no historical artifact was
recovered and no fixture was created. Codex found two record-accuracy defects;
Gemini corrected them in R4-R1, Codex found no remaining Blocking or Important
issue, and Peter accepted the correction and Branch B.

**Accepted baseline.** Peter Duscha accepted B1-R4 and the corrected B1-R3 record
on Codex's independent recommendation. `B1-R3-1` and `B1-R3-2` are Closed as
remediated. Manifest version 30 and aggregate digest
`28a4f4c2b7596e9042f6b12a34f5684b3499a3fafd997e306fe25f6798e8a526`
are the accepted baseline-contract review input. The diagnostic fixture remains
exactly 5,120 bytes with SHA-256 `b77f92dc…905b`; it is not a normative launcher
output. [Acceptance decision](../review/project-review-2026-10-02-p5-r5-rp11-b1-r4-acceptance.md).

Claude prepared and twice remediated a fresh R-5 assignment. Codex's R2
re-review found no Blocking, Important or Optional issue. Peter Duscha accepts
the R2 remediation, closes `FRESH-A1-R2-1` as remediated, and accepts the
assignment at SHA-256
`f5b4c4e935817e7a68df3c8d1b6f8cc78617e0db6622a86a45ea38c1f0c18f94`
as the execution procedure
([decision](../review/project-review-2026-10-02-p5-r5-rp11-fresh-assignment-r2-acceptance.md)).

In the superseded 2026-10-02 activation state, Peter Duscha named Gemini as the independent executor for work ID
`C-P5.0-R5-RP11-FRESH-R5` and confirms the fresh-R-5 handback filename
([activation](../review/project-review-2026-10-02-p5-r5-rp11-fresh-assignment-gemini-activation.md)).
Gemini was then permitted to perform the accepted assignment once, using only its exact
commands and substitutions. The run must be wholly fresh; Gemini may not read
or reuse its earlier R-5 or B1 artifacts. There is no retry, remediation,
package-change or privilege authority.

That authority is now consumed; the later R5 PASS is accepted and D9-3 is
Complete. RP-11 remains unwired and unmet; the distinct package RAID item
P5.0-R5 remains Blocking; `plan.is_executable=False`; and Package 5.0 remains
not ready.

## Records and archives

- [Pre-activation fresh-R-5 current state](status-through-2026-10-02-fresh-r5-procedure-acceptance.md)
- [Pre-acceptance fresh-R-5 current state](status-through-2026-10-02-fresh-r5-assignment-r2-acceptance.md)
- [Superseded B1-R3/B1-R4 current-action block](status-through-2026-10-02-r5-b1-r4-acceptance.md)
- [Superseded B1 current-action block](status-through-2026-10-01-r5-b1-reference-reproduction.md)
- [Superseded R4 current-action block](status-through-2026-10-01-r5-r4-branch-b.md)
- [Superseded R2-assignment snapshot](status-through-2026-10-01-r5-r3-acceptance.md)
- [Status archive index](status-archive/README.md)
