# Claude prompt — one-host H-1 design remediation R4

Work ID: `C-P5.0-R5-RP11-H1-D3-R4`

Date: 2026-10-04

## Assignment

Revise only the inactive proposal
`docs/review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md`
to adopt Peter Duscha's OH-D-10 decision: D3-R3 Option A with interruption
route iii-a. Preserve D3-R3 as history and add a D3-R4 section and handback.

Adopt the already-specified mechanical contract, reconcile every affected
table, proof obligation, traceability row and successor slice, and return for
independent Codex re-review. In particular:

- the Polkit rule grants `start` only;
- the capture unit contains the fixed `ExecStartPre=+... rp11_h1.py consume`
  step, with no requester-controlled operand or environment;
- consume removes and PK-verifies the grant before `ExecStart=` can run;
- a consume failure prevents `ExecStart=` and is not a pass;
- the consume step is one-shot and serialized with cleanup;
- manual interruption is the executor's A-2-authorized root
  `sudo -n /usr/bin/systemctl stop rp11-capture-pass-a.service` route;
- polling remains lifetime/recovery machinery only and establishes no grant
  boundary;
- GP-R3, ST-1.ur, `/run` boot clearing, automatic cleanup and separately
  authorized RB-1 remain intact; and
- PO-21 (n) through (r), PO-11 (g), H-0 facts and fail-closed gates remain
  explicit proposed proof obligations, not assumed host facts.

Perform repository-local, read-only consistency checks only. Do not run test
suites. Do not access any host, network, credential, retained evidence path or
secret; do not implement, build, install, activate, clean up, commit or push.

Return either **DESIGN REMEDIATION READY FOR RE-REVIEW** or **BLOCKED
REMEDIATION**. Do not declare `OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` or
`OH-H1-D3-2` closed. Stop after the repository-only handback.

