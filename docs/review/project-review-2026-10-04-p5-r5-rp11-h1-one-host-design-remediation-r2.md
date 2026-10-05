# Independent re-review — `oracle-test` one-host H-1 design remediation R2

Date: 2026-10-04

Reviewer: Codex

Design author: Claude

Work ID: `C-P5.0-R5-RP11-H1-D3-R2`

Reviewed return:
[`phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md`](phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md#13-d3-r2-remediation-and-handback-d3-r2-2026-10-04).

## Outcome

Claude's **DESIGN REMEDIATION READY FOR RE-REVIEW** return is valid and makes
substantial progress: placing both activation files on boot-cleared `/run`,
arming PID-1 supervision before publication and retaining fail-closed proof
obligations closes D3-R1's cross-boot live-grant defect in principle.

The revised proposal is not yet decision-ready. I find two Blocking defects
in the same activation-cleanup contract. `OH-H1-D3-2` and
`OH-H1-D3-R1-1` remain open. No Important or Optional finding is raised.
Nothing in this review accepts or activates the proposal.

## Findings

### Blocking `OH-H1-D3-R2-1` — polling leaves the grant live after the pass terminal state

The accepted OH-D-7 contract says no live Polkit grant may remain after the
pass. The R2 prompt repeats that condition exactly. Section 4.2.5-R2(g),
however, has the holder poll the capture unit every `poll_ms`, and expressly
states that the rule is unlinked only within that interval plus CL-0 through
CL-3. The proof in §4.2.5-R2(n)(3) says HL ends at the pass's terminal state,
but mechanically it ends only when a later poll observes that state.

Consequently the design has a normal, non-failure interval after the pass has
ended in which the grant remains live. A bounded interval is still a grant
after the pass and does not satisfy OH-D-7. This is an authorization-boundary
defect, not merely a performance question.

Required remediation: couple the pass terminal transition to holder cleanup
mechanically, so cleanup is triggered by the transition rather than periodic
observation. Specify the ordering and failure behavior at the same level as
the current holder/backstop design. Polling may remain only as a backstop; it
cannot be the mechanism claimed to establish “no grant after the pass.” If
the unavoidable systemd ordering still permits a non-zero transition window,
the design must return BLOCKED REMEDIATION for a maintainer decision rather
than reinterpret the accepted absolute boundary.

### Blocking `OH-H1-D3-R2-2` — grant-priority mode intentionally leaves attributable pass configuration state

The R2 prompt requires the live grant to be disabled first and
`pass-a.json` then removed, and separately requires `pass-a.json` cleanup to
remain automatic. In §4.2.5-R2(h), grant-priority mode applies when the CL
attempt directory or journal cannot be created or a journal append fails.
It removes the A1-intact rule, runs the grant post-check and stops. The text
explicitly says that `pass-a.json` and its directories are removed only with
an attempt's write-ahead lines.

If the evidence filesystem remains unwritable, every periodic backstop attempt
re-enters GP and leaves the already attributable `pass-a.json` and tree P in
place for the rest of the boot. A kernel boot will eventually clear them, but
no boot is guaranteed. This is not automatic completion of the decided
activation cleanup contract and leaves a normal retry path permanently short
of ST-1.

Required remediation: after grant removal and verification, provide a safe
automatic cleanup path for A1-intact `pass-a.json` and activation directories
even when new evidence cannot be written, or prove why the exact accepted
contract requires a different maintainer decision. As with GP's rule removal,
the design must never claim recorded success without durable evidence; that
does not justify declining the cleanup itself.

## What held

- The `/run` placement mechanically prevents either activation file from
  surviving a kernel boot, subject to the proposed PO-11/PO-20/PO-21 proof
  obligations.
- The transient holder and backstop are armed before activation publication,
  are independent of the interactive session, and preserve grant-first
  cleanup after process death.
- The event matrix, boot-scoped attribution, activation-record v2 schema and
  attestation distinction are coherent apart from the two findings above.
- H-1 rollback remains separately authorized, and the accepted D3-R1
  publication/recovery protocol is not weakened.
- Claude stayed within the repository-only authority and kept the proposal
  inactive.

## Required successor

Peter should accept this re-review and authorize one narrow repository-only
remediation of `OH-H1-D3-R2-1` and `OH-H1-D3-R2-2`. The revised result needs
another independent Codex re-review before `OH-H1-D3-2` or
`OH-H1-D3-R1-1` can close and before any H-1 design, implementation, host or
activation step is accepted.

## Checks and authority boundary

I read the canonical current-state documents, the R2 authority and prompt,
the prior reviews and accepted OH-D decision, and the complete D3-R2 proposal.
I inspected repository status and performed repository-local documentation
consistency checks.

No SSH, network/Git retrieval, credential, retained-path inspection, upstream
research, implementation, build, installation, H-0/H-1/H-2, ACT/DEACT,
rollback, cleanup, test suite, commit or push was performed. Tests are
inapplicable to this documentation-only review and prohibited host checks were
not run.

D9-2 and D9-3 remain Complete. D9-1, D9-4, PO-9, PO-14, PO-17, PO-18,
PO-19, PO-20, PO-21 and H-1 remain open. RP-11 remains unwired and unmet;
package RAID item `P5.0-R5` remains Blocking; `plan.is_executable=False`;
Package 5.0 remains not ready.
