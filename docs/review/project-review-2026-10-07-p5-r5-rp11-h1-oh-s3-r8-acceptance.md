# Acceptance — OH-S3 R8 cumulative design remediation

Date: 2026-10-07

Acceptance authority: Peter Duscha, Product Owner and Acceptance Authority

Accepted work ID: `C-P5.0-R5-RP11-H1-OH-S3-R8-20261007-08`

Peter Duscha accepts Codex's independent OH-S3 R8 re-review and accepts the
cumulative R8 proposal, with the editorial R9-F1 correction below, as the
inactive forward design basis.

The review returned no Blocking or Important finding and one Optional finding:
`R9-F1`. The R8 proposal had said that all four current-state pointers placed R7
before R5 and R6, while the durable handback correctly recorded that only the
Handover, status and implementation-plan §20 pointers were out of order; the
disposable-server restriction banner was already ordered and received only its
R8 return update. Peter accepts the finding and authorizes the proposal's
editorial correction. The correction changes no design, historical authority,
finding, disposition, restriction or link. `R9-F1` is closed.

Peter accepts `R8-F1` and `R8-F2` as remediated. The accepted R8 basis keeps
`s0_ran` as durable per-child history, distinguishes it from whether S0 runs on
the current SN invocation, preserves both settled-handle histories, and retains
the machine-checkable invariant
`s0_ran == (grace_deadline_ms != null)`. R1 through R7 remain unchanged,
unaccepted historical proposals; their useful content is superseded by the
self-contained cumulative R8 proposal.

The accepted basis does **not** establish concrete Route 3. The standing
`HARD STOP: concrete Route 3 not established` remains. DEC-1 through DEC-6 are
not made by this acceptance, and Peter has not yet selected the G-1b Route 3
direction. Those decisions are the next gate and require a separate current
record before any successor is authorized.

This acceptance creates no host or retained-evidence authority and authorizes
no network research, cleanup, workspace recreation, implementation, launcher
work, build, test, package or service/database operation, OH-S4/OH-S4p or later
slice, H-1/H-2, activation, rollback, commit or push. The R5 and H-0G retained
paths remain untouched pending separately gated LC-3 through LC-5 authority.

- [Accepted cumulative R8 proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md)
- [R8 handback](phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-handback.md)
- [Consumed R8 authority](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r8-remediation-authority.md)
- [Consumed R8 prompt](phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-claude-prompt.md)
- [Archived pre-acceptance handover](Handover-information-through-2026-10-07-oh-s3-r8-return.md)
