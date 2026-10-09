# WP-2 R2 remediation acceptance and Claude activation — 2026-10-09

Decision owner: Peter Duscha, Acceptance Authority

Executor: Claude

## Decision

At Peter Duscha's explicit request for an authorized, ready-to-go Claude
remediation prompt, Peter accepts and activates exactly:

- [WP-2 R2 remediation prompt](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r2-remediation-claude-prompt.md);
- work ID `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP2-R2-20261009-16`;
- 9,640 bytes and 205 lines; and
- SHA-256
  `4fb48bcd3c482fe053623256ebe54d5d2cf379913605099146a04544cb10d14b`.

The accepted remediation basis is the [independent WP-2 R1 review](project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r1.md).
It records one Blocking finding (`WP2-R1-1`) and one Important finding
(`WP2-R1-2`). This activation authorizes correction of those two findings; it
does not accept WP-2.

## Bounded authority

Claude is authorized to execute the exact WP-2 R2 remediation prompt once,
producing only:

1. the corrected cumulative
   `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md`;
2. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r2-remediation-handback.md`;
3. the return-time dated snapshots and four archive-index entries required by
   the accepted prompt; and
4. the four bounded current-state pointer updates required by the accepted
   prompt.

The prompt's reading, fixed-boundary, remediation, integrity, scope, check,
stop, return and prohibited-operation clauses are binding. Claude must return
either `WP-2 R2 REMEDIATION RETURNED — INDEPENDENT RE-REVIEW PENDING` or the
prompt-defined `HARD STOP`.

This authority permits repository-only reading, searching, mechanical
Markdown-table parsing and Markdown work. It grants no SSH, host,
retained-evidence, secret, network, package, service, database,
implementation, configuration, launcher, build, test, formatter, cleanup,
workspace-recreation, H-1/H-2, OH-S4/OH-S4p or later slice, activation,
rollback, commit or push authority.

## Boundary preserved

This acceptance authorizes only the two-finding WP-2 remediation. It does not
establish concrete Route 3, select LIT-FULL for implementation, accept WP-2,
authorize WP-3 through WP-7, resolve BC-2 for WP-9, alter baseline v1.8, widen
EX-1 or EX-2, introduce EX-3, change the accepted F-1 boundary, answer Q6-6 or
Q6-7, or authorize access to the R5/H-0G retained paths.

Authority ends when Claude writes the complete terminal handback and return
pointers, or returns a prompt-defined `HARD STOP`. A clean independent Codex
re-review and Peter's later acceptance are required before any WP-3 prompt or
authority may be prepared.

## Invocation

```text
Execute the exact accepted assignment in docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r2-remediation-claude-prompt.md. Proceed autonomously through the authorized repository-only WP-2 R2 remediation until the prompt-defined terminal state. Do not execute WP-3 or any prohibited operation. Return the complete handback for independent re-review.
```
