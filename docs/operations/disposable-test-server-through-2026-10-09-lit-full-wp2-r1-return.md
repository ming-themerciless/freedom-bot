# Disposable Linux Test Server

**Active restriction, 2026-10-09 — WP-2 operation inventory returned, independent review pending; repository-only; no host authority.**

**WP-2 OPERATION INVENTORY RETURNED — INDEPENDENT REVIEW PENDING.**

Claude executed the accepted WP-2 R1 prompt once, under its bounded
repository-only authority (work ID `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP2-R1-20261009-15`), and returns the LIT-FULL
system-call-intent operation inventory and its handback for independent
review. No `HARD STOP` arose: 317 operation rows trace all 76 accepted steps of
RT-1 through RT-5, SA-1 (`start`) and SA-2 (`stop`), cover all 29 R8 §7.3
taxonomy rows and DI-1 through DI-6 plus the stop-unit call, and leave 24
questions to WP-3, WP-4, WP-6 and WP-7 unanswered. The inventory is 189,687
bytes, 1,291 lines and SHA-256
`d86431759ad9c23f48acabdf7f663a8a6eddca21751e30cec07c8dea28e36c0a`; the handback
is 9,987 bytes, 102 lines and SHA-256
`e324f18aa3ad3550bd1a02c1c1b12d414f40cc95e55e9e81315c99e7e62a099f`.

This return does not accept WP-2, authorize WP-3, establish concrete Route 3 or
select LIT-FULL for implementation. Independent Codex review of the complete
return and Peter's later acceptance are required before any WP-3 prompt or
authority may be prepared.

**Preserved effective boundary:** baseline v1.8 remains effective. The F-1
combination remains B2-F; `AP-2` and the OS-6 `stop` in the final
root-procedure set; H-1, RB-1, RS-1 and H-1R outside it. EX-1 and EX-2 remain
effective under their approved BC-4 uses; EX-3 is not selected. B2-N and a
Python-free installer are not WP-2 prerequisites. Concrete Route 3 remains
unestablished and BC-2 remains unresolved for any later WP-9 selection.

**Current action:** independent review of the WP-2 return. WP-3 through WP-7
remain separately gated; none may begin, and no WP-3 prompt may be prepared,
before that review and Peter's acceptance.

The no-host restriction is unchanged: no SSH connection to `oracle-test`, no host or retained-evidence access, no fact collection (MF-1 through MF-8 remain uncollected),
network research, cleanup, workspace recreation, implementation,
configuration/infrastructure edit, launcher work, build, test, formatter,
package or service/database operation, OH-S4/OH-S4p or later slice, H-1/H-2,
activation, rollback, commit or push is authorized. The R5 and H-0G retained
paths remain untouched pending separately gated LC-3 through LC-5 authority.

[WP-2 operation inventory](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md)
· [WP-2 handback](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-handback.md)
· [Accepted WP-2 R1 prompt](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r1-claude-prompt.md)
· [Acceptance and Claude activation](../review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r1-acceptance-and-claude-activation.md)
· [EX-1/EX-2 approval and baseline v1.8](../review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-ex1-ex2-change-control-approval.md)
· [Archived WP-2 authorization restriction](disposable-test-server-through-2026-10-09-lit-full-wp2-r1-authorization.md)
· [Archived pre-acceptance restriction](disposable-test-server-through-2026-10-09-lit-full-wp2-r1-acceptance-pending.md).

Agents that support skills should use the `run-suites` skill, which carries
this document's synchronization and execution procedure together with the
skip-count and serial-execution traps from `.agents/AGENTS.md`. The skill
checks the restriction banner above first and cites both documents rather
than replacing either.

The server exists so that **Codex, Claude Code, Antigravity, and maintainers have full administrative (root) access** to execute end-to-end tests, destructive PostgreSQL migration drills, dependency builds, and system-level experiments in complete isolation from the production/staging host.

---
