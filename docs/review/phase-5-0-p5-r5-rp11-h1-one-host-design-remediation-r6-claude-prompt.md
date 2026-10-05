# Claude prompt — one-host H-1 design remediation R6

Work ID: `C-P5.0-R5-RP11-H1-D3-R6`

Date: 2026-10-04

## Assignment

Revise only the inactive proposal
`docs/review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md`
to incorporate Peter Duscha's OS-6 decision and remediate Blocking issue
`OH-H1-D3-R5-1` from Codex's
[D3-R5 re-review](project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r5.md).
Preserve D3-R5 as history and add a D3-R6 section and handback.

The decided condition is exact:

- route iii-a is available only while the capture unit is `active`;
- its `InvocationID` must equal the consume journal's
  `run-start.invocation_id`;
- the consume journal must contain a durable `consumed` line;
- route iii-a is unavailable while the unit is `activating` or during
  `start-pre`; and
- a hung consume step ends through the finite, fail-closed start timeout.

The fixed literal, executor, A-2 authority and §9.5.3 classification for a
running pass remain unchanged.

Reconcile every place that still treats D3-R4's `activating`/`active` timing as
current or treats OS-6 as undecided. In particular:

- record OS-6 as a decided amendment to route iii-a, not merely a refinement;
- make contract OSA's authority boundary and CX-4 classification follow from
  that decision explicitly;
- reconcile D-1, A-2, the terminal-cause and boundary tables, traceability,
  successor decisions, implementation tests and OH-S8b fault drills;
- preserve the root-outside-A-2 residual honestly without presenting it as an
  authorized-path exception;
- preserve the D3-R5 SB-1/SB-2/SB-3 mechanism, CQ ordering, shared-lock
  protocol, fail-closed start timeout and proposed proof obligations unless a
  concrete inconsistency requires a narrowly explained correction; and
- state whether `OH-H1-D3-R5-1` is addressed in design without declaring it,
  `OH-H1-D3-R4-1`, `OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` or `OH-H1-D3-2` closed.

Perform repository-local, read-only consistency checks only. Do not run test
suites. Do not access any host, network, credential, retained evidence path or
secret; do not implement, build, install, activate, clean up, commit or push.

Return either **DESIGN REMEDIATION READY FOR RE-REVIEW** or **BLOCKED
REMEDIATION**. Stop after the repository-only handback.
