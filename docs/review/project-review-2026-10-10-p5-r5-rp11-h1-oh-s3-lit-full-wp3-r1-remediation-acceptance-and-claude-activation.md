# WP-3 R1 remediation acceptance and Claude activation — 2026-10-10

Decision owner: Peter Duscha, Acceptance Authority

Executor: Claude

## Decision

On the maintainer's explicit instruction to provide an authorized, ready-to-go
Claude remediation prompt, the Acceptance Authority accepts and activates
exactly:

- [WP-3 R1 remediation prompt](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-r1-remediation-claude-prompt.md);
- work ID `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP3-R1-20261010-22`;
- 12,684 bytes and 242 lines; and
- SHA-256
  `0452dd4c77aa4f92196ffa24ca0292e810f1bf1765133161eab2f57b34f553d9`.

The accepted review basis is the
[independent WP-3 HARD STOP review](project-review-2026-10-10-p5-r5-rp11-h1-oh-s3-lit-full-wp3-hard-stop.md),
3,786 bytes, 77 lines and SHA-256
`f486bab827e935de6fac56a5345f0729f26e0727ed815cc549a0af8b8e97b6a6`.
It records zero Blocking, two Important and zero Optional findings and confirms
that the underlying HARD STOP remains valid.

## Bounded authority

Claude is authorized to execute the exact remediation prompt once, producing
only:

1. a cumulative correction to
   `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-interface-contract.md`;
2. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-r1-remediation-handback.md`;
3. the return-time dated snapshots and four archive-index rows required by the
   accepted prompt; and
4. the four bounded current-state pointer updates required by the prompt.

The prompt's complete-reading precondition, truthfulness rule, fixed boundary,
remediation requirements, checks, terminal states and prohibited operations are
binding. Claude must not edit the historical original handback or imply that
its ambiguous ledger proves the original executor's reading.

This authority permits repository-only reads, searches and the specified
Markdown remediation. It grants no SSH, host, retained-evidence, secret,
network, package, service, database, implementation, configuration, launcher,
build, test, formatter, cleanup, workspace-recreation, OH-S4/OH-S4p or later
slice, H-1/H-2, activation, rollback, commit or push authority.

## Boundary preserved

The substantive WP-3 HARD STOP remains in force. This activation does not
accept WP-3, establish concrete Route 3, select LIT-FULL for implementation,
authorize WP-4 through WP-7, resolve Q6-6, Q6-7 or BC-2, change baseline v1.8,
widen EX-1 or EX-2, introduce EX-3, change F-1, or authorize access to the R5
or H-0G retained paths.

Authority ends when Claude writes the complete terminal remediation handback
and return pointers, or returns the prompt-defined `HARD STOP`. The return
requires independent re-review before Peter may accept it or authorize any
successor work.

## Invocation

```text
Execute the exact accepted assignment in docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-r1-remediation-claude-prompt.md. Proceed autonomously through every authorized repository-only step until the prompt-defined terminal state. Do not perform any prohibited operation or prepare WP-4 through WP-7. Write the complete durable handback and current-state return before stopping.
```
