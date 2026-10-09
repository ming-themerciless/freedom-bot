# Active handover — OH-S3 R8 accepted; Route 3 decision gate next — 2026-10-07

Peter Duscha accepts Codex's independent OH-S3 R8 re-review and accepts the
cumulative R8 proposal, with the authorized R9-F1 editorial correction, as the
inactive forward design basis. `R8-F1`, `R8-F2` and `R9-F1` are closed. R1
through R7 remain unchanged, unaccepted historical proposals; the accepted R8
proposal is the self-contained forward reference.

The accepted design keeps `s0_ran` as durable per-child history, distinct from
whether S0 runs on a particular SN invocation. Both settled-handle histories
are preserved and the schema invariant
`s0_ran == (grace_deadline_ms != null)` remains in force.

**Current hard stop:** concrete Route 3 is not established. The next gate is
Peter's recorded G-1a decisions (DEC-1 through DEC-6) and G-1b Route 3
direction. This acceptance makes none of those decisions and authorizes no
successor.

No host or retained-evidence access, network research, cleanup, workspace
recreation, implementation, launcher work, build, test, package or
service/database operation, OH-S4/OH-S4p or later slice, H-1/H-2, activation,
rollback, commit or push is authorized. The R5 and H-0G retained paths remain
untouched pending separately gated LC-3 through LC-5 authority.

- [Acceptance record](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r8-acceptance.md)
- [Accepted cumulative R8 proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md)
- [R8 handback](phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-handback.md)
- [Accepted cumulative OH-S2 R2 citation record](phase-5-0-p5-r5-rp11-h1-oh-s2-r2-citations.md)
- [Archived pre-acceptance handover](Handover-information-through-2026-10-07-oh-s3-r8-return.md)
- [Handover archive index](handover-archive/README.md)
