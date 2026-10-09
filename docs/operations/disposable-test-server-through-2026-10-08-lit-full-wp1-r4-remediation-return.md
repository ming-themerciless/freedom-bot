# Disposable Linux Test Server

**Active restriction, 2026-10-08 — LIT-FULL WP-1 R4 remediation returned; no host authority.**

Claude Code executed the exact repository-only R4 remediation prompt under work ID
`C-P5.0-R5-RP11-H1-OH-S3-RT3-WP1-R4-20261008-13` (12,936 bytes, 245 lines, SHA-256
`218040bc5bc5ee34e27cb1e1eeaceb66443992f25ebb30629a2053ae7c473620`) and returned
`WP-1 R4 REMEDIATION RETURNED — DECISION AND §0.2 GATE PENDING`. The R4 prompt and its
authority are consumed by this return.

The cumulative R4 proposal (1,542 lines, 133,795 bytes, SHA-256
`00e15e5cb5e8575d829d7f1fd8ae93d273fd43f536f53308b5a07926c24d8737`) closes the
three findings of the independent R3 re-review. It states one process-tree result: after
B2-N an in-set act's inventoried tree begins at B2-N's loader-free start path and contains no
`sudo`, while an act PD-2b leaves out is not started by B2-N and its whole `sudo` path stays
outside the boundary under EX-3. It makes the compact gate require steps 1–3 and every
applicable governance closure and design prerequisite, verified for all sixteen worked
combinations. A dated archival erratum (151 lines, 10,162 bytes, SHA-256
`eca8aff5fd18b5f2eb3c58684345b5472cca34cff90d33faa74637af57d2df4e`) records, without
reconstructing it, the R3-authorization pointer text that no repository snapshot holds. The
earlier corrections and boundaries are preserved.

**WP-1 remains `changes requested` and is NOT accepted; BQ-2 and BQ-3 are
undecided; PD-2a, PD-2b and PD-3 are undecided; EX-1, EX-2, EX-3, BC-4 and BC-2
are neither decided nor approved; concrete Route 3 remains unestablished; WP-2
is not authorized.**

**Gate before WP-2.** Independent Codex re-review of the R4 remediation and
Peter's recorded BQ-2 and BQ-3 decisions, including PD-2a, PD-2b and PD-3, are
always necessary. If either chosen answer contains an exception, including EX-1,
EX-2 or EX-3 under BC-4, the complete implementation-plan §0.2 change-control
process must close before WP-2 may be prompted, authorized or rely on that
boundary. A Peter decision on BQ-2 or BQ-3 is not by itself §0.2 approval. Every
separately required design prerequisite must also exist under its own authority
and independent review before WP-2 may rely on it. If Peter retains literal
no-exception LIT-FULL, WP-2 remains blocked until the required loader-free
privileged-start and, where B3-IN is selected, installer designs make the
boundary attainable, or Peter withdraws the affected design. BC-2 remains
unresolved for any later WP-9 selection. WP-1 remains changes-requested and is
not accepted; BQ-2 and BQ-3 are undecided.

No SSH connection to `oracle-test`, host or retained-evidence access, fact
collection, cleanup, workspace recreation, privilege, package operation,
installation, build, test, formatter, service/database mutation, H-1/H-2,
OH-S4/OH-S4p or later slice, activation, rollback, commit or push is authorized.
No successor implementation is authorized. MF-1 through MF-8 remain
uncollected. The R5 and H-0G retained paths remain untouched pending separately
gated LC-3 through LC-5 authority.

[R4 remediation proposal](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-proposal.md)
· [R4 remediation handback](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-handback.md)
· [R4 remediation authority](../review/project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-authority.md)
· [Exact R4 remediation prompt (consumed)](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-claude-prompt.md)
· [Independent R3 re-review](../review/project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation.md)
· [R3 pointer-archive erratum](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-pointer-archive-erratum.md)
· [R3 remediation proposal](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-proposal.md)
· [R3 remediation handback](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-handback.md)
· [G-1 decision record](../review/project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-g1-decisions.md)
· [Accepted cumulative R8 proposal](../review/phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md)
· [Archived R3-return restriction](disposable-test-server-through-2026-10-08-lit-full-wp1-r3-remediation-return.md).

