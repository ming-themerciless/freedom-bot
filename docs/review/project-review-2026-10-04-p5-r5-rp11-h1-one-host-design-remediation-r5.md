# Independent re-review — `oracle-test` one-host H-1 design remediation R5

Date: 2026-10-04

Reviewer: Codex

Design author: Claude

Work ID: `C-P5.0-R5-RP11-H1-D3-R5`

Reviewed return: [D3-R5 remediation and handback](phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md#16-d3-r5-remediation-and-handback-d3-r5-2026-10-04).

## Outcome

Claude's **DESIGN REMEDIATION READY FOR RE-REVIEW** return is structurally
complete, but I find one Blocking issue, `OH-H1-D3-R5-1`. D3-R5 obtains its
one-start-attempt proof by narrowing the already-decided interruption route
iii-a. That narrowing is a maintainer choice, not an authorized refinement.

`OH-H1-D3-R4-1`, `OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` and `OH-H1-D3-2` remain
open. Nothing in this review accepts or activates H-1.

## Finding

### `OH-H1-D3-R5-1` — Blocking — OS-6 changes the decided route and hides CX-4 outside the proof

D3-R4 route iii-a expressly permitted the executor's A-2-authorized root
`stop` while the capture unit was `activating` or `active`, and its terminal
table covered a stop during `start-pre`. The R5 authority required preservation
of OH-D-10 Option A with route iii-a, while the R5 prompt required Claude to
return **BLOCKED REMEDIATION** if satisfying the contract needed a maintainer
choice or changed OH-D-10.

D3-R5 instead introduces OS-6, which permits route iii-a only while the unit is
`active` with a durable `consumed` line, and forbids it while `activating`.
Contract OSA then excludes CX-4 because a root stop during `start-pre` is
classified as an act “against A-2's terms.” That exclusion is essential: if
such a stop ends the first attempt `inactive`, τ₀ was `0`, and the unit unloads,
neither SB-1 nor SB-2 exists, so a later start can run the pass.

This is not merely a clearer precondition. It removes an interruption case
that D3-R4 deliberately allowed and that the R4 successor drill required.
Claude's own §16.1 and §16.9 item 6 recognize the question, but the return
nevertheless says no maintainer decision is required. Until Peter decides
OS-6, the proposal has not proved the requested one-start-attempt property for
every authorized path and should have returned **BLOCKED REMEDIATION**.

The issue is Blocking because it affects the authorization boundary and the
correctness of the activation state machine.

## Required decision

Peter must choose one of these directions before another remediation:

1. accept OS-6 as an amendment to route iii-a, making manual interruption
   available only after the unit is `active` and the consume journal has a
   durable `consumed` line; or
2. retain D3-R4's `activating`/`active` route and require a design that closes
   CX-4 for an authorized stop during `start-pre`.

The successor must then reconcile the authority wording, D-1, A-2, the
terminal and boundary tables, contract OSA, CX-4, traceability, tests and the
OH-S8b drill. The systemd end-state fact in PO-21 (u) remains a proposed
version-bound obligation; it cannot be assumed to eliminate CX-4 before the
citation gate.

## Review notes

Apart from this decision dependency, the D3-R5 mechanism directly addresses
the D3-R4 defect: the claim is the first mutation under the activation lock;
PID 1 start history covers attempts in which CP cannot publish a claim; the
rule token bounds successful consumption; HL decides its end under the shared
lock; and the proposal reconciles the requested states, records, tests and
fault drills. These points do not cure the unapproved route narrowing.

## Checks and authority boundary

I read the canonical current-state documents, the R5 authority and prompt,
the D3-R4 review, and the relevant D3-R5 proposal sections, proof,
reconciliations and handback. I performed repository-local, read-only
consistency inspection before writing this review record. No host,
network/Git retrieval, credential, retained-path inspection, upstream
research, implementation, build, installation, H-0/H-1/H-2, activation,
evidence, rollback, cleanup, test-suite, commit or push action occurred.
