# Disposable Linux Test Server

**Active restriction, 2026-10-10 — WP-3 HARD STOP returned; repository-only; no host authority.**

**Current state:** **HARD STOP — WP-3 INTERFACE CONTRACT NOT COMPLETED — INDEPENDENT REVIEW PENDING.**

Claude executed the accepted WP-3 prompt once (work ID
`C-P5.0-R5-RP11-H1-OH-S3-RT3-WP3-20261009-20`) and ended at the prompt's stop rule.
The authorized repository sources do not support the facts the Q3 closures need.
The exact unsupported facts are `UF-01` … `UF-14` for Q3-1 … Q3-7 and Q3-9: the
client transport, authentication and message framing (UF-01); unit-name to object
resolution (UF-02); the wire types of the eight DI-1 properties and the typed-to-text
rule (UF-03); bus-error representation (UF-04); the job-completion mechanism
(UF-05); the `StartTransientUnit` signature and job mode (UF-06); write-side
property names, types, units and exec-command structure (UF-07); timer and service
creation and the timer properties (UF-08); the `StopUnit` signature, mode and
already-inactive / not-loaded behaviour (UF-09); the Polkit check method, subject
encoding, flags and cancellation (UF-10); the authority-result to
`authorized`/`not-authorized`/`error` mapping (UF-11); the unit and encoding of a
process subject's start time (UF-12); polkitd's treatment of that start time and
uid (UF-13); and whether a per-property read reaches `HIDDEN`/`EXPLICIT`
properties (UF-14). Q3-11 is answered as a fail-closed record (UF-15 … UF-18). Q3-1 …
Q3-7 and Q3-9 are not closed. No citation was manufactured and nothing was
researched. The exact statements are in §6 of the
[interface contract](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-interface-contract.md) (419 lines, 39,708 bytes, SHA-256
`050254be8d42533301d24fe9df55e7ce839893b2c7a49e382310235d8816f733`); the
[handback](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-handback.md) reports the full ledger and checks.

**Preserved effective boundary:** baseline v1.8, F-1 B2-F, both lifecycle acts
in, B3-OUT, effective EX-1/EX-2 and no EX-3 remain unchanged. Q6-6 and Q6-7
remain unanswered. Concrete Route 3 remains unestablished, BC-2 remains a later
WP-9 question and LIT-FULL is not selected for implementation.

**Current action:** independent review of the returned HARD STOP and a maintainer
decision on how the client-side facts are to be supplied by an authorized record.
WP-4, WP-5, WP-6 and WP-7 remain separately gated and unauthorized; none has been
prepared.

The no-host restriction is unchanged: no host or retained-evidence access,
network research, cleanup, workspace recreation, implementation,
configuration/infrastructure edit, launcher work, build, test, formatter,
package or service/database operation, OH-S4/OH-S4p or later slice, H-1/H-2,
activation, rollback, commit or push is authorized. The R5 and H-0G retained
paths remain untouched pending separately gated LC-3 through LC-5 authority.

[WP-3 interface contract (HARD STOP)](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-interface-contract.md)
· [WP-3 handback](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-handback.md)
· [Accepted WP-3 prompt](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-claude-prompt.md)
· [WP-3 acceptance and Claude activation](../review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp3-acceptance-and-claude-activation.md)
· [Accepted WP-2 inventory](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md)
· [Archived WP-3-authorization restriction](disposable-test-server-through-2026-10-09-lit-full-wp3-authorization.md)
· [Archived review-pending restriction](disposable-test-server-through-2026-10-09-lit-full-wp3-assignment-review-pending.md)
· [Restriction archive](disposable-test-server-archive/README.md).
