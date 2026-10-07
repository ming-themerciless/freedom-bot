# Claude prompt — OH-S3 R2 independent-review remediation (R3)

Status: **authorized by Peter Duscha on 2026-10-07, subject to the matching
authority record and prompt identity pin**

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-R3-20261007-03`

## Start instruction

Start Claude Code in `/opt/freedom-blades/platform`, then paste:

```text
Execute the authorized repository-only remediation assignment in docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r3-signal-operation-remediation-claude-prompt.md. Close the one Important independent-review finding against OH-S3 R2, produce one self-contained cumulative R3 proposal and durable handback, update only the four named current-state pointers, and stop for independent Codex re-review. Preserve the existing HARD STOP: concrete Route 3 not established. Do not access any host, retained evidence, secret, credential or player data; do not perform network research, implementation, launcher work, build, test, cleanup, activation, commit or push.
```

## Authority and terminal boundary

Peter Duscha, Product Owner and Acceptance Authority, authorizes this exact
repository-only documentation assignment. The matching authority record is
[`project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r3-signal-operation-remediation-authority.md`](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r3-signal-operation-remediation-authority.md).

OH-S3 R1 and R2 remain unaccepted and historically unchanged. R2's
`HARD STOP: concrete Route 3 not established` remains in force. This assignment
may replace R2's proposal as the cumulative forward candidate only by closing
the finding below. It may not accept either proposal, approve a decision,
broaden Route 3, resolve the Route 3 hard stop, authorize a successor, or change
any accepted evidence or disposition.

No SSH or other host connection, `oracle-test`, production, staging, Foundry or
database access, retained-evidence access, secret, credential or player-data
access, network research, package operation or installation, implementation or
configuration edit, launcher retarget or rebuild, application or hook test,
formatter, build, service/database mutation, cleanup, workspace recreation,
OH-S4/OH-S4p or later slice, H-1/H-2, activation, rollback, commit or push is
authorized.

The assignment ends at `HARD STOP: concrete Route 3 not established` after the
R3 remediation is ready for independent review, or at its first other defined
hard stop. Independent Codex re-review and Peter's later recorded decision
remain mandatory.

## Required reading and initial checks

Before editing, read completely:

1. `.agents/AGENTS.md`;
2. the reading map and §§0, 14, 16, 17 and 20 of
   `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. the restriction banner in
   `docs/operations/disposable-test-server.md`;
5. this R3 prompt and its matching authority;
6. the R2 prompt, authority, complete proposal and complete handback;
7. the R1 prompt, authority, complete proposal and complete handback, only as
   needed to check a carried obligation;
8. the accepted cumulative OH-S2 R2 citation record, its handback and
   acceptance, only at the exact sections cited by R2;
9. the cumulative one-host design amendment at the exact sections cited by R2;
10. the operational draft as a future consumer, without editing it; and
11. the current project-status pointer.

Inspect `git status` and preserve every unrelated or pre-existing change.
Verify this prompt's exact byte count and SHA-256 against its authority before
any edit. A mismatch is `HARD STOP: OH-S3 R3 prompt identity mismatch`.

Do not use recursive searches rooted at the repository, a workspace root, the
user's home, `/opt`, `/var`, `/tmp` or `/`. Search only exact named documents or
explicit safe tracked-file allowlists. Never read or test a secret-bearing path.

## Independent-review finding to remediate

### R3-F1 — R2-F2's required blocking-operation inventory omits signal sending

The R2 assignment expressly required the potentially blocking-operation
inventory to include signal handling, kill and reap. The cumulative R2 proposal
inventories signal delivery and handler execution and separately inventories
child reaping. It uses `SIGTERM` and `SIGKILL` delivery to a child's process
group as the consequence of an enforced wait expiring, but it does not inventory
the signal-sending operation itself, classify it, state how return errors are
handled, or define the fail-closed result when the target no longer exists or
the signal cannot be sent. The absolute wording in HS-5 and related rows
therefore assumes an operation whose failure contract is unstated.

This is an **Important** documentation/design-completeness finding, not a new
host fact and not authority for research. Remediate it as follows:

1. preserve R2 unchanged and create a self-contained cumulative R3 proposal;
2. add every signal-sending operation performed by `spawn()` or another helper
   to §7.3's inventory, including the initial group-directed termination signal,
   escalation to `SIGKILL`, and any signal used by cleanup or recovery;
3. distinguish the local signal-sending system call from PID 1's class-M signal
   delivery. Give the local operation the correct deadline class without
   inventing an elapsed-time bound;
4. define the result for success, `ESRCH`/an already absent target, permission or
   target-validation failure, and every other error. No error may authorize a
   pass, convert an unconfirmed result into confirmation, or be hidden;
5. state how the implementation validates and retains the intended child
   process-group identity so that it cannot signal an unrelated process after a
   PID or process-group reuse race. If repository evidence is insufficient for
   that contract, define the missing proof obligation explicitly; do not invent
   a kernel guarantee;
6. state what the helper does after a failed or indeterminate signal send,
   including how long it waits for reaping, when it abandons the child, what it
   records, and which next recovery owner applies. The helper may continue only
   with the operation's existing fail-closed result;
7. propagate the contract consistently through deadline class E, HS-5, PK/2,
   SG-4, the terminal-cause and interruption maps, evidence/record fields,
   invariants, residuals, and any Appendix A or Appendix B obligation affected;
8. add negative tests for successful send, `ESRCH`, other send errors, an
   already-exited child, a target-identity mismatch/reuse simulation, failure of
   `SIGTERM` followed by the escalation decision, failure of `SIGKILL`, and the
   resulting reap/abandon record; and
9. update the remediation map so it shows how R3-F1 and the previously incomplete
   R2-F2 item 1 are closed.

Do not silently strengthen R2's timing claims. Sending a signal is not proof
that the target exited, was reaped, or left an uninterruptible kernel call. The
R2 deadline classes, withdrawal of unsupported elapsed-time claims, PO-11(d′),
Route 3 boundary, SSW disposition, MF dispositions, and Route 3 hard stop remain
unchanged unless a directly necessary consistency correction is identified and
called out for review.

## Required cumulative R3 proposal

Create a self-contained cumulative R3 proposal. A reviewer must not need to
splice R2 prose into it. The safest method is to copy R2's proposal to the new
R3 path and make only the focused amendments required above, preserving all
other content and explicitly identifying each changed section.

The R3 proposal must:

1. carry forward the complete R2 proposal, including its title-level and closing
   `HARD STOP: concrete Route 3 not established`;
2. close R3-F1 without changing R2-F1's remediation or reopening the accepted
   Route 3 boundary;
3. retain explicit fact classes and mark any uncited signal-delivery behavior as
   a proposed, version-bound proof obligation rather than an established fact;
4. contain a focused R3 change summary and remediation map;
5. preserve the decisions, baseline-change separation, successor order and
   no-authority statements except for directly necessary cross-references; and
6. remain a proposal only. Nothing in it is accepted or executable authority.

If closing the finding requires a kernel or language fact that the named
repository evidence does not establish, add that fact to the relevant future
citation gate and retain the Route 3 hard stop. Do not perform network research.

## Deliverables

Create:

1. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r3-signal-operation-remediation-proposal.md`
   — the self-contained cumulative R3 proposal;
2. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r3-signal-operation-remediation-handback.md`
   — the complete durable handback.

Update only these current-state pointers:

- `docs/review/Handover information`;
- `docs/project-management/status.md`;
- §20 of `docs/implementation-plan.md`; and
- the restriction banner in `docs/operations/disposable-test-server.md`.

Do not edit R1, R2, any accepted historical evidence, the operational draft,
source code, tests, configuration, service files, migrations, archive snapshots,
archive indexes, the decision register or the change log.

The handback must report prompt identity, terminal state, finding remediated,
files changed, exact repository documents consulted, commands and checks,
checks not run, security implications, unresolved decisions and proposed
independent-review focus. It must distinguish pre-existing worktree changes and
confirm no host, retained-evidence, secret, network, implementation, launcher,
build, test, cleanup, commit or push action.

Mark this R3 authority and prompt consumed in all four pointers. Do not claim
Codex or Peter acceptance and do not authorize or propose activation of a
successor.

## Verification

Run only bounded local documentation checks:

- recompute this prompt's byte count and SHA-256 before work and at handback;
- verify links introduced in the six allowed files from an explicit target
  list;
- check trailing whitespace in the six allowed files;
- run `git diff --check` only for the four tracked pointers and two new
  deliverables;
- compare the R3 proposal to R2 and confirm every non-mechanical change is
  necessary to close R3-F1;
- scan the R3 proposal for the local signal-sending operation, PID-1 signal
  delivery, `SIGTERM`, `SIGKILL`, `ESRCH`, identity/reuse handling, reap,
  abandon, evidence fields, residuals and negative tests;
- verify that every send outcome fails closed and that no send success is
  treated as proof of exit or reaping;
- verify that the Route 3 boundary, SSW classification, MF-1 through MF-8
  dispositions and the hard stop are unchanged; and
- review the six-file diff for accidental host, implementation, successor,
  cleanup, credential, secret, commit or push authority.

Do not run application tests, hook tests, formatters, builds, package tools,
network checks or remote-host checks.

End the handback exactly with:

`HARD STOP: concrete Route 3 not established; OH-S3 R3 remediation awaits independent Codex re-review; no host, implementation, cleanup, OH-S4/OH-S4p or later slice is authorized.`
