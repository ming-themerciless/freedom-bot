# Claude prompt — one-host H-1 design remediation R5

Work ID: `C-P5.0-R5-RP11-H1-D3-R5`

Date: 2026-10-04

## Assignment

Revise only the inactive proposal
`docs/review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md`
to remediate Blocking finding `OH-H1-D3-R4-1` from Codex's
[D3-R4 re-review](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r4.md).
Preserve D3-R4 as history and add a D3-R5 section and handback.

The defect is exact: CP-3 checks the consume-evidence name, but CP-4 creates
it. CP-0, CP-1 and CP-2 can therefore fail before any one-shot barrier exists,
while the D3-R4 terminal table, proof item 7 and CX-2 claim that every failed
consume prevents every later start in the same activation from running the
pass.

Revise the mechanical contract so the one-start-attempt property is true and
proved for every path. In particular:

- distinguish a start with no valid active activation from a consume attempt
  that has identified the active activation, without turning an ST-1 root
  probe into an activation marker;
- once CP has identified the active activation, durably and atomically consume
  its single start attempt before any remaining fallible precondition can
  return, while holding the same activation lock used by cleanup;
- specify the exact publication protocol, ownership, mode, identity,
  durability point and closed journal operations for the attempt barrier;
- specify every crash, kill, timeout, contention, malformed/missing input and
  cleanup race before, during and after that durability point;
- prove that a pre-barrier failure cannot later become a valid start in the
  same activation, or narrow the pre-barrier class with a complete proof that
  no such later start is possible without a new root-authorized activation;
- make CP, CL, HL and the backstop agree on classification and recovery, with
  no interval in which a repeated start can race cleanup into `ExecStart=`;
- keep consume failure fail-closed: `ExecStart=` does not run, no pass is
  claimed, and a later start of the same activation cannot run the pass;
- reconcile CP-0 through CP-7, the terminal-cause table, ST-2.c/ST-2.f, the
  boundary table, proof item 7, CX-2, records and journals, traceability,
  implementation tests and OH-S8b fault drills; and
- state any new residual honestly. If satisfying the accepted contract needs
  a maintainer choice or changes OH-D-10 rather than refining it, return
  **BLOCKED REMEDIATION** with the exact decision required.

Preserve all unaffected D3-R4 properties: the rule grants `start` only; the
fixed root `ExecStartPre=` removes and PK-verifies the grant before
`ExecStart=`; route (iii-a) is the executor's A-2-authorized root stop;
polling establishes no grant boundary; GP-R3, ST-1.ur, `/run` boot clearing,
automatic cleanup and separately authorized RB-1 remain intact; and PO-21 (n)
through (r), PO-11 (g), H-0 facts and fail-closed gates remain explicit
proposed proof obligations rather than assumed host facts.

Perform repository-local, read-only consistency checks only. Do not run test
suites. Do not access any host, network, credential, retained evidence path or
secret; do not implement, build, install, activate, clean up, commit or push.

Return either **DESIGN REMEDIATION READY FOR RE-REVIEW** or **BLOCKED
REMEDIATION**. Do not declare `OH-H1-D3-R4-1`, `OH-H1-D3-R2-1`,
`OH-H1-D3-R1-1` or `OH-H1-D3-2` closed. Stop after the repository-only
handback.
