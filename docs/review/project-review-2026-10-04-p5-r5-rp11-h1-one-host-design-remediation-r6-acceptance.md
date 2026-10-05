# Acceptance — one-host H-1 design remediation D3-R6

Date: 2026-10-04

Decision owner: Peter Duscha, Maintainer and Acceptance Authority

Independent reviewer: Codex

## Decision

Codex independently re-reviewed Claude's D3-R6 return and found no Blocking,
Important or Optional issue. Peter Duscha accepts that recommendation and the
cumulative one-host H-1 activation design in the inactive proposal.

The following findings are closed as remediated by D3-R1 through D3-R6:

- `OH-H1-D3-R5-1` — OS-6 is incorporated as Peter's decided amendment rather
  than an unauthorized refinement;
- `OH-H1-D3-R4-1` — SB-1, SB-2 and SB-3 enforce one start attempt across the
  authorized path, including pre-barrier failures;
- `OH-H1-D3-R2-1` — the start grant is consumed and PK-verified before
  `ExecStart=`, leaving no grant during or after a pass;
- `OH-H1-D3-R1-1` — PID-1 supervision, boot-scoped state and the backstop
  enforce the accepted one-pass/one-boot cleanup boundary; and
- `OH-H1-D3-2` — the cumulative ACT/DEACT publication, record and automatic
  cleanup contract is complete in design.

OS-6 remains decided exactly as recorded in the R6 authority. Route iii-a is
available only while the capture unit is `active`, its `InvocationID` matches
the consume journal and `consumed` is durable. It is unavailable during
`activating` and `start-pre`; the finite start timeout bounds a hung consume
step.

## Accepted residual and boundary

Peter knowingly accepts CX-4 as documented in §4.2.5-R6(f): it requires an
act outside A-2, specifically a non-route root `stop` or a prohibited orderly
transition during `start-pre`, plus the recorded additional conditions. It is
not an exception in the authorized path. Even in CX-4, no grant exists during
or after a pass.

This acceptance makes the proposal the accepted **inactive design basis**. It
does not activate, implement or install it and grants no host, network,
credential, implementation, build, H-0/H-1/H-2, evidence, rollback, cleanup,
commit or push authority.

## Review evidence

The review covered §4.2.5-R6, its D3-R6 reconciliation notes, the traceability
and successor tables, and the §17 handback. Repository-local consistency and
`git diff --check` passed. No test suite or host check was run because the R6
authority prohibited both. The review introduced no repository change.

## Next controlled step

The next proposed slice is OH-S1, the read-only H-0 fact collection described
in §4.7.4 of the proposal. It requires a new explicit authority. OH-S2 and all
later implementation, installation and evidence slices remain separately
gated.
