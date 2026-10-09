# Disposable Linux Test Server

**Active restriction, 2026-10-09 — WP-2 R2 remediation returned, independent re-review pending; repository-only; no host authority.**

**WP-2 R2 REMEDIATION RETURNED — INDEPENDENT RE-REVIEW PENDING.**

Claude executed the accepted WP-2 R2 remediation prompt once, under its bounded
repository-only authority (work ID `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP2-R2-20261009-16`),
and returns the corrected cumulative LIT-FULL system-call-intent operation
inventory and its complete R2 handback for independent re-review. No `HARD STOP`
arose. The corrected inventory is 220,050 bytes, 1,410 lines and SHA-256
`e2960f233d4d5e540a68011f6dab2bc297442088eab28d36867b5736f13e3012`.
It delivers 317 table rows (316 operation, contract or composition rows and one
non-operative gap row), traces all 76 accepted steps of RT-1 through RT-5, SA-1
(`start`) and SA-2 (`stop`), covers all 29 R8 §7.3 taxonomy rows, counts 41
logical accepted call sites across DI-1 through DI-6 and the stop-unit call, and
leaves 24 questions to WP-3, WP-4, WP-6 and WP-7 unanswered.

`WP2-R1-1` is remediated by replacing `RT2.AM0.7` with a non-operative gap row:
whether AM-0 repeats AP-0's “no unterminated activation” condition remains the
open Q6-7 (owner WP-6), and WP-2 selects neither answer. `WP2-R1-2` is remediated
by separating today's DI-3/DI-4 children from the LIT-FULL replacement child set,
carrying the SN-10 / A-I-16 `effect: "unknown"` obligation unmapped as Q6-6, and
counting logical accepted call sites, with DI-4 reconciled at BS-2, BS-3 and the
BS-4 terminal disarm. The handback holds the exact changes and checks.

WP-2 remains unaccepted. This return does not accept WP-2, authorize WP-3,
establish concrete Route 3 or select LIT-FULL for implementation.

**Preserved effective boundary:** baseline v1.8 remains effective. The F-1
combination remains B2-F; `AP-2` and the OS-6 `stop` in the final
root-procedure set; H-1, RB-1, RS-1 and H-1R outside it. EX-1 and EX-2 remain
effective under their approved BC-4 uses; EX-3 is not selected. B2-N and a
Python-free installer are not WP-2 prerequisites. Concrete Route 3 remains
unestablished and BC-2 remains unresolved for any later WP-9 selection.

**Current action:** independent Codex re-review of the complete R2 return is
required, followed by Peter's later acceptance decision. WP-3 through WP-7
remain separately gated; none may begin, and no WP-3 prompt may be prepared,
before a clean re-review and Peter's later acceptance.

The no-host restriction is unchanged: no SSH connection to `oracle-test`, no host or retained-evidence access, no fact collection (MF-1 through MF-8 remain uncollected),
network research, cleanup, workspace recreation, implementation,
configuration/infrastructure edit, launcher work, build, test, formatter,
package or service/database operation, OH-S4/OH-S4p or later slice, H-1/H-2,
activation, rollback, commit or push is authorized. The R5 and H-0G retained
paths remain untouched pending separately gated LC-3 through LC-5 authority.

[WP-2 operation inventory (R2)](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md)
· [WP-2 R2 remediation handback](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r2-remediation-handback.md)
· [WP-2 R1 handback](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-handback.md)
· [Independent WP-2 review](../review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r1.md)
· [Accepted WP-2 R2 remediation prompt](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r2-remediation-claude-prompt.md)
· [R2 acceptance and Claude activation](../review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r2-remediation-acceptance-and-claude-activation.md)
· [Accepted WP-2 R1 prompt](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r1-claude-prompt.md)
· [Acceptance and Claude activation](../review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r1-acceptance-and-claude-activation.md)
· [EX-1/EX-2 approval and baseline v1.8](../review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-ex1-ex2-change-control-approval.md)
· [Archived WP-2 R2 authorization restriction](disposable-test-server-through-2026-10-09-lit-full-wp2-r2-authorization.md)
· [Archived WP-2 authorization restriction](disposable-test-server-through-2026-10-09-lit-full-wp2-r1-authorization.md)
· [Archived WP-2 return restriction](disposable-test-server-through-2026-10-09-lit-full-wp2-r1-return.md)
· [Archived WP-2 independent-review restriction](disposable-test-server-through-2026-10-09-lit-full-wp2-r1-review.md)
· [Archived pre-acceptance restriction](disposable-test-server-through-2026-10-09-lit-full-wp2-r1-acceptance-pending.md).

Agents that support skills should use the `run-suites` skill, which carries
