# Active handover — OS-6 decided; one-host H-1 design remediation R6 assigned — 2026-10-04

Peter Duscha accepts Codex's recommendation and decides OS-6: route iii-a is
available only while the capture unit is `active`, its invocation matches the
consume journal and `consumed` is durable. It is unavailable during
`activating`/`start-pre`; the finite start timeout bounds a hung consume step.

Claude is authorized for the narrow repository-only D3-R6 incorporation of
that decision and remediation of `OH-H1-D3-R5-1`, then must stop for
independent Codex re-review.

`OH-H1-D3-R4-1`, `OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` and `OH-H1-D3-2` remain
open. No host, Git/network retrieval, credential, implementation, build,
installation, H-0/H-1/H-2, activation, evidence, rollback, cleanup, commit or
push authority is active. The current workspace host is production and must
not participate.

- [R6 authority](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r6-authority.md)
- [Claude prompt](phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-r6-claude-prompt.md)

## Superseded D3-R5 re-review handover

Codex independently re-reviewed Claude's D3-R5 return and found one Blocking
issue, `OH-H1-D3-R5-1`. D3-R5 proves the one-start-attempt property only by
narrowing route iii-a from `activating` or `active` to `active` after durable
consumption. That is a maintainer choice, not an authorized refinement; without
it, CX-4 remains an exception inside the decided route.

Peter must decide whether to accept OS-6 or retain the D3-R4 interruption
route and require a design that closes CX-4. `OH-H1-D3-R4-1`,
`OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` and `OH-H1-D3-2` remain open. No host,
Git/network retrieval, credential, implementation, build, installation,
H-0/H-1/H-2, activation, evidence, rollback, cleanup, commit or push authority
is active. The current workspace host is production and must not participate.

- [Independent R5 re-review](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r5.md)
- [Claude return](phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md#16-d3-r5-remediation-and-handback-d3-r5-2026-10-04)

## Superseded R5 remediation-assigned handover

Peter Duscha accepts Codex's D3-R4 re-review and authorizes Claude's narrow
repository-only remediation of Blocking finding `OH-H1-D3-R4-1`. Claude must
make the one-start-attempt boundary true for every CP failure path, revise the
inactive proposal and stop for independent Codex re-review.

`OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` and `OH-H1-D3-2` remain open. No host,
Git/network retrieval, credential, implementation, build, installation,
H-0/H-1/H-2, activation, evidence, rollback, cleanup, commit or push authority
is active. The current workspace host is production and must not participate.

- [R5 authority](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r5-authority.md)
- [Claude prompt](phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-r5-claude-prompt.md)

## Superseded D3-R4 re-review handover

Codex independently re-reviewed Claude's D3-R4 return and found one Blocking
defect, `OH-H1-D3-R4-1`: CP's one-shot marker is created only at CP-4, so a
failure at CP-0, CP-1 or CP-2 leaves no barrier against a later start in the
same activation. This contradicts the terminal table, proof item 7, CX-2 and
the required one-shot contract.

`OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` and `OH-H1-D3-2` remain open. Peter must
decide the review disposition and whether to authorize a narrow repository-only
successor remediation. No host, Git/network retrieval, credential,
implementation, build, installation, H-0/H-1/H-2, activation, evidence,
rollback, cleanup, commit or push authority is active. The current workspace
host is production and must not participate.

- [Independent R4 re-review](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r4.md)
- [Claude return](phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md#15-d3-r4-remediation-and-handback-d3-r4-2026-10-04)

## Superseded R4 remediation-assigned handover

Peter Duscha accepts Codex's clean D3-R3 re-review, closes
`OH-H1-D3-R2-2` as remediated and decides OH-D-10 as Option A with
interruption route iii-a. Claude is authorized for the narrow repository-only
R4 incorporation of the start-consumed grant design into the inactive
proposal, then must stop for independent Codex re-review.

`OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` and `OH-H1-D3-2` remain open. No host,
Git/network retrieval, credential, implementation, build, installation,
H-0/H-1/H-2, activation, evidence, rollback, cleanup, commit or push authority
is active. The current workspace host is production and must not participate.

- [R3 independent re-review](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r3.md)
- [R4 authority](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r4-authority.md)
- [Claude prompt](phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-r4-claude-prompt.md)

## Superseded R3 remediation-assigned handover

Peter Duscha accepts Codex's D3-R2 re-review and authorizes Claude's narrow
repository-only remediation of Blocking findings `OH-H1-D3-R2-1` and
`OH-H1-D3-R2-2`. Claude must mechanically couple cleanup to the pass terminal
transition, complete attributable activation cleanup when evidence is
unwritable, revise the inactive proposal and stop for independent Codex
re-review. `OH-H1-D3-2` and `OH-H1-D3-R1-1` remain open.

No host, Git/network retrieval, credential, implementation, build,
installation, H-0/H-1/H-2, activation, evidence, rollback, cleanup, commit or
push authority is active. The current workspace host is production and must
not be a source, controller, relay, destination, fallback or rollback target.

- [R3 authority](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r3-authority.md)
- [Claude prompt](phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-r3-claude-prompt.md)

## Superseded R2 re-review handover

Codex independently re-reviewed Claude's D3-R2 return. The boot-cleared `/run`
and PID-1 supervision direction holds, but the activation cleanup still has
two Blocking defects: `OH-H1-D3-R2-1` leaves the grant live for the polling
and cleanup interval after the pass ends, and `OH-H1-D3-R2-2` leaves
attributable `pass-a.json` state indefinitely when evidence remains
unwritable. `OH-H1-D3-2` and `OH-H1-D3-R1-1` remain open.

Peter must decide the review disposition and whether to authorize a narrow
repository-only successor remediation. No host, Git/network retrieval,
credential, implementation, build, installation, H-0/H-1/H-2, activation,
evidence, rollback, cleanup, commit or push authority is active.

- [Independent R2 re-review](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r2.md)
- [Claude return](phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md#13-d3-r2-remediation-and-handback-d3-r2-2026-10-04)

## Superseded R2 remediation-assigned handover

Peter Duscha accepts Codex's D3-R1 re-review, closes `OH-H1-D3-1` as
remediated, and authorizes Claude's narrow repository-only remediation of
Blocking finding `OH-H1-D3-R1-1`. `OH-H1-D3-2` remains open. Claude must make
death/reboot activation cleanup enforce the accepted one-pass/one-boot grant
boundary, revise the inactive proposal and stop for independent Codex
re-review.

No host, Git/network retrieval, credential, implementation, build,
installation, H-0/H-1/H-2, activation, evidence, rollback, cleanup, commit or
push authority is active. The current workspace host is production and must
not be a source, controller, relay, destination, fallback or rollback target.

- [R2 authority](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r2-authority.md)
- [Claude prompt](phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-r2-claude-prompt.md)

## Superseded D3-R1 re-review handover

Codex independently re-reviewed Claude's D3-R1 return. `OH-H1-D3-1` is
remediated and ready for Peter to close. `OH-H1-D3-2` remains open under new
Blocking finding `OH-H1-D3-R1-1`: after process/session loss or reboot the
design defers `DEACT` until a later actor reaches the host, so a Polkit grant
authorized for one boot may remain live in the next boot and after the pass.

Peter must decide the review disposition and whether to authorize a narrow
repository-only successor remediation. No host, Git/network retrieval,
credential, implementation, build, installation, H-0/H-1/H-2, activation,
evidence, rollback, cleanup, commit or push authority is active.

- [Independent re-review](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation.md)
- [Claude return](phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md#12-d3-r1-remediation-and-handback-d3-r1-2026-10-04)

## Superseded remediation-assigned handover

Peter Duscha authorizes Claude's repository-only remediation of Blocking
findings `OH-H1-D3-1` and `OH-H1-D3-2`. Claude must incorporate accepted
OH-D-1 through OH-D-9, revise the inactive one-host proposal and stop for
independent Codex re-review.

No host, Git/network retrieval, credential, implementation, build,
installation, H-0/H-1/H-2, activation, evidence, rollback, cleanup, commit or
push authority is active. The current workspace host is production and must
not be a source, controller, relay, destination, fallback or rollback target.

- [Remediation authority](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-authority.md)
- [Claude prompt](phase-5-0-p5-r5-rp11-h1-one-host-design-remediation-claude-prompt.md)

## Superseded decisions-recorded handover

Peter Duscha accepts OH-D-1 through OH-D-9 on Codex's recommendation. Claude's
BLOCKED DESIGN return is valid, but its H-1 portion has two Blocking findings:
`OH-H1-D3-1` (crash-consistent publication/recovery) and `OH-H1-D3-2`
(complete ACT/DEACT publication, record and automatic cleanup). The proposal
remains inactive and unaccepted pending repository-only remediation and Codex
re-review.

The current workspace host is confirmed as production and may not be a source,
controller, relay, destination, fallback or rollback target. Later retrieval
must occur directly from the canonical Git remote on `oracle-test`, under
separate authority; any required read-only credential also needs separate
authority. No host, network, credential, implementation, build, installation,
H-0/H-1/H-2, activation, evidence, rollback, cleanup, commit or push authority
is active.

- [Decision record](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-decisions.md)
- [Independent review](project-review-2026-10-04-p5-r5-rp11-h1-oracle-test-one-host-design-amendment.md)
- [Claude proposal](phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md)

## Superseded design-assigned handover

Peter Duscha authorizes Claude to prepare the repository-only design amendment
for complete local H-1 installation and RP-11 test/evidence execution on
`oracle-test` under `ubuntu`. The production server remains outside scope.
Claude must return a decision-ready inactive proposal or BLOCKED DESIGN; Codex
then independently reviews it.

No SSH, host inspection, upstream research, implementation, build,
installation, H-1/H-2, evidence pass, cleanup, commit or push authority is
active.

- [Design authority](project-review-2026-10-04-p5-r5-rp11-h1-oracle-test-one-host-design-authority.md)
- [Claude prompt](phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-claude-prompt.md)

## Superseded topology-decision state

Peter Duscha supersedes the production-host H-1 direction. The complete H-1
installation and RP-11 test/evidence workflow will run locally on the
disposable `oracle-test` server under its existing unprivileged `ubuntu`
account. The Freedom-Blades production server and production Foundry service
must not be accessed or changed by this workflow.

D9-2 remains Complete. U-2 and U-4 through U-10 remain decided for the new
topology. H-1 is blocked pending a repository-only one-host design amendment,
independent review and later explicit authorities. No host access,
implementation, build, installation, H-1/H-2, evidence pass, cleanup, commit
or push authority is active.

- [Topology correction](project-review-2026-10-04-p5-r5-rp11-h1-oracle-test-topology-correction.md)
- [Archived displaced handover](Handover-information-through-2026-10-04-production-host-h1-decision.md)

## Superseded decisions-pending state

Codex independently accepts Claude's BLOCKED PREPARATION return with no
Blocking, Important or Optional finding. The repository is not ready for an
H-1 assignment. Codex recommends declaring D9-2 Complete from the existing
I-7 evidence; Peter Duscha must decide D9-2 and U-1 through U-4 and U-6 through
U-10 before any successor assignment is activated.

No host, implementation, citation-source access, launcher staging,
installation, H-1/H-2, evidence-pass, cleanup, commit or push authority is
active.

- [Independent review](project-review-2026-10-04-p5-r5-rp11-h1-assignment-preparation.md)
- [Claude handback](phase-5-0-p5-r5-rp11-h1-installed-host-evidence-assignment-preparation-handback.md)

## Superseded preparation authority

Peter Duscha authorizes Claude to prepare a decision-ready static-launcher H-1
installed-host evidence assignment. The preparation is repository-only and
must return either an exact inactive proposal or a BLOCKED PREPARATION record
with the prerequisite sequence. Codex independently reviews the return.

Initial inspection found four expected installation inputs and the committed
launcher executable absent, so Claude must verify readiness rather than assume
that H-1 can execute. No host, implementation or H-1 execution authority is
active.

- [Preparation authority](project-review-2026-10-04-p5-r5-rp11-h1-assignment-preparation-authority.md)
- [Claude task](phase-5-0-p5-r5-rp11-h1-installed-host-evidence-assignment-preparation-claude-prompt.md)

## Superseded R-5 acceptance state

Peter Duscha accepts Gemini's complete R5 PASS and Codex's independent review.
The static-launcher independent-rebuild step R-5 is accepted and D9-3 is
Complete. This does not close the distinct package RAID item `P5.0-R5`, which
remains Blocking, or PO-9, PO-14, D9-4, H-1, RP-11 wiring,
`plan.is_executable` or Package 5.0 readiness.

No host or cleanup authority is active. The next controlled step is a separate
decision on preparation of an H-1 installed-host evidence assignment.
[Acceptance](project-review-2026-10-04-p5-r5-rp11-fresh-r5-pass-acceptance.md).

## Superseded acceptance-pending state

Gemini's one-run authority is consumed. Codex independently validates the R5
handback as a complete PASS with no Blocking, Important or Optional finding and
recommends accepting static-launcher R-5 and treating D9-3 as complete. This establishes
reproducibility/build-environment evidence only; PO-9, PO-14, D9-4, H-1,
RP-11 wiring, `plan.is_executable` and Package 5.0 readiness do not close.

No host or cleanup authority is active. The R4 and R5 retained paths remain
untouched pending Peter Duscha's decision.
[Independent review](project-review-2026-10-04-p5-r5-rp11-fresh-r5-pass.md).

## Superseded R5 activation state

Peter Duscha accepts the determinism remediation, closes `FRESH-R4-HS-1`,
accepts the dated D2 amendment, confirms the R5 identifiers, retains the R4
remote evidence without cleanup, leaves S10 unchanged and accepts the exact R5
assignment. Focused commit `4cbdf0b6ecabad7484e64ff0485587a17f55dcaf`
contains exactly the 17 reviewed controlled files; controlled paths are clean
and every Appendix C identity passes.

Gemini is activated for exactly one R5 runner invocation. Only the assignment's
single command and same-task waiting are authorized.
[Acceptance and activation](project-review-2026-10-04-p5-r5-rp11-fresh-r5-acceptance-and-gemini-activation.md).

Gemini invocation:

```text
/goal Execute the active assignment in docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r5.md. Proceed autonomously through every authorized step in order until the defined terminal state (PASS, INVALID RUN, or HARD STOP). Do not post intermediate progress updates, do not yield turns for user confirmation on background tasks, and do not stop until the final handback and closing record are fully written.
```

## Superseded decisions-pending state

Claude returned the complete `cc1.v` determinism remediation and draft R5
assignment. Codex independently found no Blocking, Important or Optional
implementation issue. `FRESH-R4-HS-1` is ready to close as remediated. Codex
recommends confirming the proposed R5 identifiers, retaining the R4 remote
evidence, leaving S10 unchanged, adding a dated D2 design amendment and
authorizing one focused controlled-file commit before R5 acceptance and Gemini
activation.

No host, cleanup or R-5 authority is active pending Peter Duscha's decisions
and the required commit/activation record.
[Independent review](project-review-2026-10-04-p5-r5-rp11-fresh-r4-cc1-determinism-remediation.md).

## Superseded remediation-assigned state

Peter Duscha accepts Gemini's valid consumed R4 HARD STOP, Codex's independent
review and open Important finding `FRESH-R4-HS-1`. Claude is assigned a
repository-only audit and remediation of the complete `cc1.v` determinism
contract. The preferred correction pins the two GGC values as explicit reviewed
compiler inputs, but Claude must account for every diagnostic-byte consequence
and must not weaken exact comparison.

Codex independent review is authorized after Claude returns. A successor Gemini
run is the conditionally approved third stage only after a clean review and a
complete digest-pinned assignment and activation record; there is no current
host activation. No remote access, cleanup, retry or R-5 execution is authorized.

- [Acceptance and staged authority](project-review-2026-10-04-p5-r5-rp11-fresh-r4-hard-stop-acceptance-and-remediation-authority.md)
- [Claude prompt](phase-5-0-p5-r5-rp11-fresh-r4-cc1-determinism-remediation-claude-prompt.md)

## Superseded decision-pending state

Gemini's accepted R4 invocation is complete and consumed. Codex independently
confirms a valid, correctly closed HARD STOP at S9: all four normative outputs
and the listing were byte-identical, but `cc1.v` differed only in GCC's
host-resource-selected GGC values (`100/131072` versus `94/2169`). Important
finding `FRESH-R4-HS-1` records that the exact diagnostic contract contains an
uncontrolled host-resource input.

Codex recommends accepting the consumed HARD STOP and assigning Claude a
repository-only remediation that pins both GGC parameters as explicit reviewed
compiler inputs, preserving exact byte comparison rather than weakening the
verifier. Peter's acceptance and remediation authority are required first.
There is no host, cleanup, retry, remediation or new-run authority.
[Independent review](project-review-2026-10-04-p5-r5-rp11-fresh-r4-hard-stop.md).

## Superseded R4 activation state

Peter Duscha accepts R4-R1, closes `R4-D1-1`, confirms U-14 … U-17 and the
proposed identifiers, and activates Gemini for exactly one runner invocation.
The 19 controlled files are committed at
`d216cb1b93125c83e13d43b989fd94c2ded01569`; the controlled-path status is
clean and 75 focused tests pass.
[Acceptance and activation](project-review-2026-10-04-p5-r5-rp11-r4-r1-acceptance-and-gemini-activation.md).

Gemini invocation:

```text
/goal Execute the active assignment in docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r4.md. Proceed autonomously through every authorized step in order until the defined terminal state (PASS, INVALID RUN, or HARD STOP). Do not post intermediate progress updates, do not yield turns for user confirmation on background tasks, and do not stop until the final handback and closing record are fully written.
```

## Superseded focused-commit-pending state

Claude returned the narrow wait-contract remediation. Codex independently
reproduced 75 passing focused tests and found no Blocking, Important or
Optional issue; `R4-D1-1` is recommended Closed as remediated. The 19
controlled runner/resource/test files remain untracked and must be committed
at their pinned bytes before R4 can pass Step 1. No remote access or run is
authorized pending Peter's focused commit and later activation decisions.
[Independent re-review](project-review-2026-10-04-p5-r5-rp11-antigravity-delivery-redesign-r1.md).

## Superseded R4-R1-assigned state

Claude returned the non-interactive runner and R4 successor proposal. Codex's
independent review found no Blocking issue and one Important workflow finding,
`R4-D1-1`: R4 tells Gemini to stop if Antigravity returns before the runner's
final line, conflicting with the required autonomous terminal state. Claude is
assigned a repository-only remediation authorizing same-task Antigravity
waiting without input, EOF, signal, reinvocation or user yield. No remote
access or new run is authorized.

- [Independent review](project-review-2026-10-04-p5-r5-rp11-antigravity-delivery-redesign.md)
- [R4-R1 prompt](phase-5-0-p5-r5-rp11-antigravity-delivery-redesign-r1-claude-prompt.md)

## Superseded redesign-assigned state

Peter Duscha accepts the consumed R3 HARD STOP and open findings
`FRESH-R3-HS-1` and `FRESH-R3-HS-2`. Claude is assigned repository-only design,
implementation and local testing of a deterministic non-interactive runner and
standalone successor assignment. No remote access or new run is authorized.

- [Acceptance and redesign authority](project-review-2026-10-03-p5-r5-rp11-fresh-r3-hard-stop-acceptance.md)
- [Claude redesign prompt](phase-5-0-p5-r5-rp11-antigravity-delivery-redesign-claude-prompt.md)

## Superseded unaccepted-HARD-STOP state

Gemini's accepted R3 run ended before any remote action. Antigravity's
background-terminal transport emitted none of the Step 1 heredoc output and
returned exit 0 only after an interactive EOF; the required Step 1 timestamps
and evidence are absent. Gemini correctly did not proceed to Step 2. The
mandatory S12.start block is also absent. Codex confirms a valid consumed HARD
STOP and records Important findings `FRESH-R3-HS-1` and `FRESH-R3-HS-2`.
[Independent review](project-review-2026-10-03-p5-r5-rp11-fresh-r3-hard-stop.md).

No host access or new run is authorized. The next controlled decision is
whether to accept the consumed HARD STOP and authorize a narrow redesign of
the command-delivery method for Antigravity before any further run.

## Superseded R3 activation state

Peter Duscha accepts the independently reviewed R3 assignment, including the
strict S1.3 evidence rule, confirms work ID
`C-P5.0-R5-RP11-FRESH-R5-R3` and the R3 handback path, and activates Gemini
for exactly one wholly new run. Only the assignment's exact actions are
authorized. [Acceptance and activation](project-review-2026-10-03-p5-r5-rp11-fresh-assignment-r3-acceptance-and-gemini-activation.md).

Gemini invocation:

```text
/goal Execute the active assignment in docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r3.md. Proceed autonomously through every authorized step in order until the defined terminal state (PASS, INVALID RUN, or HARD STOP). Do not post intermediate progress updates, do not yield turns for user confirmation on background tasks, and do not stop until the final handback and closing record are fully written.
```

## Superseded decision-pending state

Claude returned the standalone R3 successor assignment. Codex independently
reviewed it with no Blocking, Important or Optional finding. The reported
“open items” reduce to accepting the strict S1.3 evidence rule and confirming
the proposed work ID and handback path; the remaining notes are technically
resolved in the review. No host authority is active.
[Independent review](project-review-2026-10-03-p5-r5-rp11-fresh-assignment-r3.md).

## Superseded preparation state

Codex completed the bounded inspection and cleanup. The six retained stopped-run
paths are absent; `/tmp` recovered to 470.6 MiB available but remains a fixed
475.4 MiB tmpfs, independent of the 39 GiB free on `/`. No host authority is
active. [Cleanup result](phase-5-0-p5-r5-rp11-fresh-r5-cleanup-result.md).

Claude is assigned repository-only preparation of a complete successor
assignment using outer-host `/var/tmp`, including a 4 GiB preflight floor and
the prospective fix for `FRESH-R5-HS-1`. The proposal must be independently
reviewed and accepted before Gemini activation.
[Claude prompt](phase-5-0-p5-r5-rp11-fresh-r5-new-run-assignment-preparation-claude-prompt.md).

## Superseded accepted-HARD-STOP state

Gemini's one accepted invocation is complete and consumed. Peter Duscha accepts
the valid Step 5 HARD STOP and authorizes Codex's bounded filesystem/quota
inspection and deletion of only the six retained run paths. Peter also
authorizes preparation of one wholly new Gemini run after that result is
incorporated into an exact assignment. See the
[decision and cleanup authority](project-review-2026-10-03-p5-r5-rp11-fresh-r5-hard-stop-acceptance-and-cleanup-authority.md)
and [independent review](project-review-2026-10-03-p5-r5-rp11-fresh-r5-hard-stop.md).

R-5 remains Blocking and unaccepted. `FRESH-R5-HS-1` remains open against the
closed handback and must not be repaired by editing that immutable record.

## Superseded activation record

This is the concise active assignment and restriction entry point. The complete
superseded R2-assignment state is preserved verbatim in
[`Handover-information-through-2026-10-01-r5-r3-acceptance.md`](Handover-information-through-2026-10-01-r5-r3-acceptance.md).

## Accepted decisions

Peter Duscha accepted Codex's D2-R1 recommendations:

* **LD-7:** require FA-2's zero-`ret` image from the start. Permitting `ret`
  later requires a separate reviewed decision.
* **LD-8:** accept the bound build root plus HA-1 … HA-5, provided IC-1 passes,
  R-5 actually varies and records at least one of HA-1 … HA-3, unexplained
  differences stop, and the independent-decoding finding is resolved.
* archive the displaced Handover and status text as verbatim, hash-indexed
  snapshots.
* **LD-9:** require Codex to independently decode the actual `.text` at D9-2
  using its own decoder or byte-by-byte manual derivation prepared without
  reading XD's table. An independent exercise of XD alone is not sufficient.

- [Independent review and decision record](project-review-2026-09-30-p5-r5-rp11-r4-d2-r1-decisions.md)
- [D2-R2 acceptance and LD-9 decision](project-review-2026-10-01-p5-r5-rp11-r4-d2-r2-acceptance.md)

## Accepted I-7-R1 decision

Peter Duscha accepts Claude's I-7-R1 remediation on Codex's independent
recommendation. `I7-R1-1` is Closed as remediated and D-2 is accepted as
implemented. Claude and Codex have stopped. The durable decision record is:

- [I-7-R1 acceptance](project-review-2026-10-01-p5-r5-rp11-i7-r1-acceptance.md)
- [I-7-R1 independent re-review](project-review-2026-10-01-p5-r5-rp11-i7-r1-ic1-environment-remediation.md)

- [I-7 review](project-review-2026-10-01-p5-r5-rp11-i7-static-launcher-implementation.md)
- [I-7-R1 remediation prompt](phase-5-0-p5-r5-rp11-i1-r3-r4-i7-r1-ic1-environment-remediation-claude-prompt.md)
- [I-7-R1 remediation handback](phase-5-0-p5-r5-rp11-i1-r3-r4-i7-r1-ic1-environment-remediation-handback.md)

Accepted: IC-1 requires the exact ordered sequence of ten `execve` calls,
and each one's complete environment, as specified for the run's controlled
checkout. The four driver values are derived from `build.sh` and the pinned
driver, not taken from a trace. 368 focused IC-1 tests cover missing, changed,
extra, duplicate and malformed variables, `PWD`/`OLDPWD` at R-2 and R-4(a), and
each driver variable. The pre-remediation checker passed 42 missing and 24
changed mutations. A freshly provisioned root gives R-1 equal and R-2
unchanged. IC-1 passes at `/rp11/co` and `/rp11/alt/checkout` with outputs
byte-identical to R-2. T-L11/T-L10 pass, and every frozen digest is
unchanged. The manifest is version 28, digest `02d660c3…5abb`. One derivation
correction R1-D-1 is accepted: GCC's `prune_options` drops
`-fno-pic`. R-5 is not performed.

- [I-7 implementation prompt](phase-5-0-p5-r5-rp11-i1-r3-r4-i7-static-launcher-implementation-claude-prompt.md)
- [I-7 implementation handback](phase-5-0-p5-r5-rp11-i1-r3-r4-i7-static-launcher-implementation-handback.md)
- [Accepted D2 proposal](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md)
- [D2-R2 handback](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r2-zero-ret-decoding-remediation-handback.md)
- [Acceptance and LD-9 decision](project-review-2026-10-01-p5-r5-rp11-r4-d2-r2-acceptance.md)

## R-5 history to date

Peter accepted the Antigravity-reviewed R-5 assignment and named Gemini. The
first attempt stopped on missing `bubblewrap`; Peter authorized only its
installation. The resumed run reproduced the four frozen outputs across HA-1 …
HA-3 variation, but Codex found that R-1 and R-2 were not gated by one
`enter.py build` invocation and that `cc1.v` changed without explanation.

- [R-5 assignment](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-independent-rebuild-assignment.md)
  · [stopped R-5 handback](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-independent-rebuild-handback.md)
  · [acceptance](project-review-2026-10-01-p5-r5-rp11-r5-assignment-acceptance.md)
  · [bubblewrap review](project-review-2026-10-01-p5-r5-rp11-r5-bwrap-stop.md)
  · [bubblewrap authority](project-review-2026-10-01-p5-r5-rp11-r5-bwrap-install-authority.md)

**R2 (completed).** Gemini added the same-invocation R-1/R-2 manifest gate to
`enter.py build` and `ic1`, corrected the snapshot date, and withdrew the
erroneous R-5 PASS in the stopped handback.
[Prompt](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r2-orchestration-remediation-gemini-prompt.md)
· [handback](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r2-orchestration-remediation-handback.md).

**R3 (accepted).** Gemini removed the unsafe caller-supplied regex override
from `cc1check.py`; byte equality is now the only route to `PASS`, and every
non-identical pair is `HARD_STOP` with exact byte offsets, lengths and values.
Codex independently reproduced 4,019 passing repository tests, with 12
toolchain-dependent skips because no accepted local root was available, plus
clean compilation, byte-range and unreadable-input checks and `git diff
--check`. Peter Duscha accepted R3 on that recommendation.
[Prompt](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r3-cc1-comparison-remediation-gemini-prompt.md)
· [handback](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r3-cc1-comparison-remediation-handback.md)
· [acceptance](project-review-2026-10-01-p5-r5-rp11-r5-r3-acceptance.md).

## Superseded 2026-10-02 activation state

Peter Duscha accepted B1-R4 and the corrected B1-R3 record on Codex's
independent recommendation. `B1-R3-1` and `B1-R3-2` are Closed as remediated.
The accepted baseline contract is manifest version 30, aggregate digest
`28a4f4c2b7596e9042f6b12a34f5684b3499a3fafd997e306fe25f6798e8a526`.
The diagnostic fixture remains exactly 5,120 bytes with SHA-256
`b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`.

- [Acceptance decision](project-review-2026-10-02-p5-r5-rp11-b1-r4-acceptance.md)
- [B1-R3 handback](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r3-baseline-contract-verification-remediation-handback.md)
- [B1-R4 handback](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r4-verification-record-accuracy-remediation-handback.md)

Peter Duscha accepted Claude's R2 remediation on Codex's independent
recommendation. `FRESH-A1-R2-1` is Closed as remediated, and the fresh R-5
assignment at SHA-256
`f5b4c4e935817e7a68df3c8d1b6f8cc78617e0db6622a86a45ea38c1f0c18f94`
is accepted as the execution procedure.

- [Acceptance decision](project-review-2026-10-02-p5-r5-rp11-fresh-assignment-r2-acceptance.md)
- [Accepted assignment](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md)
- [R2 handback](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r2-handback.md)
- [Independent re-review](project-review-2026-10-02-p5-r5-rp11-fresh-assignment-r2.md)

Peter Duscha names Gemini as the independent executor for work ID
`C-P5.0-R5-RP11-FRESH-R5`. The confirmed handback is
`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-handback.md`.
[Activation decision](project-review-2026-10-02-p5-r5-rp11-fresh-assignment-gemini-activation.md).

The next controlled step is Gemini's one bounded run under the exact accepted
assignment. Gemini must first write the §2 independence attestation, must use
wholly fresh resources and must not read or reuse its earlier R-5 or B1
artifacts.

Gemini invocation:

```text
/goal Execute the active assignment in docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md. Proceed autonomously through every authorized step in order until the defined terminal state (PASS, INVALID RUN, or HARD STOP). Do not post intermediate progress updates, do not yield turns for user confirmation on background tasks, and do not stop until the final handback and closing record are fully written.
```

**Only Gemini is authorized to perform the assignment's exact §6 blocks and
standalone `rsync`, once and in order.** There is no `sudo`, package change,
host configuration, retry, remediation, service or database action, H-1/H-2,
PO-14 discharge, RP-11 wiring, controlled write, reboot, evidence band,
harness `--execute`, operational path, secrets scan, commit or push authority.

R-5 remains stopped, Blocking and unaccepted as evidence. RP-11 remains unwired and unmet;
neither pass is executable or authorized; `plan.is_executable=False`; PO-9 and
PO-14 remain open; OD-62 G-A remains conditional; and Package 5.0 remains not
ready.

## Archives

- [Pre-activation fresh-R-5 current state](Handover-information-through-2026-10-02-fresh-r5-procedure-acceptance.md)
- [Pre-acceptance fresh-R-5 current state](Handover-information-through-2026-10-02-fresh-r5-assignment-r2-acceptance.md)
- [Superseded B1-R3/B1-R4 current-action block](Handover-information-through-2026-10-02-r5-b1-r4-acceptance.md)
- [Superseded B1 current-action block](Handover-information-through-2026-10-01-r5-b1-reference-reproduction.md)
- [Superseded R4 current-action block](Handover-information-through-2026-10-01-r5-r4-branch-b.md)
- [Superseded R2-assignment snapshot](Handover-information-through-2026-10-01-r5-r3-acceptance.md)
- [Handover archive index](handover-archive/README.md)
