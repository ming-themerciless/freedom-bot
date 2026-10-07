# Claude prompt — OH-S3 R5 independent-review remediation (R6)

Status: **authorized by Peter Duscha on 2026-10-07, subject to the matching
authority record and prompt identity pin**

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-R6-20261007-06`

## Start instruction

Start Claude Code in `/opt/freedom-blades/platform`, then paste:

```text
Execute the authorized repository-only remediation assignment in docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r6-remediation-claude-prompt.md. Close R6-F1 and R6-F2, produce one self-contained cumulative R6 proposal and durable handback, update only the four named current-state pointers, and stop for independent Codex re-review. Preserve HARD STOP: concrete Route 3 not established. Do not access any host, retained evidence, secret, credential or player data; do not perform network research, implementation, launcher work, build, test, cleanup, activation, commit or push.
```

## Authority and terminal boundary

Peter Duscha, Product Owner and Acceptance Authority, authorizes this exact
repository-only documentation assignment through the matching
[authority record](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r6-remediation-authority.md).

R1 through R5 remain unchanged and unaccepted. This assignment permits only the
focused remediation below and directly necessary consistency corrections. It does
not accept a design, decide a residual, change the accepted Route 3 boundary,
resolve its hard stop or authorize a successor.

No SSH or other host connection, `oracle-test`, production, staging, Foundry or
database access, retained-evidence access, secret, credential or player-data
access, network research, package operation or installation, implementation or
configuration edit, launcher retarget or rebuild, application or hook test,
formatter, build, service/database mutation, cleanup, workspace recreation,
OH-S4/OH-S4p or later slice, H-1/H-2, activation, rollback, commit or push is
authorized.

The normal terminal state remains `HARD STOP: concrete Route 3 not established`
with the R6 remediation ready for independent Codex review. Peter's later recorded
decision is required before any successor.

## Required reading and initial checks

Before editing, read:

1. `.agents/AGENTS.md` completely;
2. the implementation plan's reading map and §§0, 14, 16, 17 and 20;
3. `docs/review/Handover information`, the current project-status pointer and
   the restriction banner in `docs/operations/disposable-test-server.md`;
4. this R6 prompt and its authority completely;
5. the R5 prompt, authority, complete cumulative proposal and complete handback;
6. the R4 proposal only at table SN-S, table SN-R, WB-5 and IM-S where needed to
   confirm the remediation does not regress R4-F1 or R4-F2;
7. the R3 proposal only at the signal-sending contract carried into R5 where
   needed to confirm the remediation does not regress R3-F1;
8. the accepted OH-S2 R2 citation record and one-host design only at the exact
   sections cited by changed R5 claims; and
9. the operational draft only at the exact Appendix B consumer sections affected
   by this remediation, without editing it.

Do not defer a required repository read or cross-reference check that can be
performed under this authority. Carrying an unchanged citation is allowed if it is
clearly identified as carried; it is not re-verification.

Inspect `git status` and preserve every pre-existing change. Verify this prompt's
byte count and SHA-256 against the authority before any edit and again at handback.
A mismatch is `HARD STOP: OH-S3 R6 prompt identity mismatch`; write its durable
handback and stop without performing remediation.

Read and search exact named documents or explicit safe tracked-file allowlists
only. No recursive search rooted at the repository, a workspace root, home,
`/opt`, `/var`, `/tmp` or `/`, and no secret-bearing path access is permitted.

## Findings to remediate

### R6-F1 — `reap-error` can permit a root signal to a reused group (Blocking)

R5 correctly exposes the interval in which the kernel may have consumed the
direct child's status before the handle records it, but leaves row 3g, S4 and SN-4
unchanged when `Popen.poll()` raises. The design reads every `reap-error` as
*unreaped* and may continue to an identity validation and root `SIGKILL`. R5 also
admits that, if the exception arose after `waitpid` consumed the status, the PID
and process-group number may have been released and SN-4 is only a detector, not a
reuse defence.

PO-SN (c) is currently phrased as a question about what CPython does, and AP-0
requires only that the obligation be accepted. That does not encode the required
safe outcome: a later citation could establish that the post-reap exception is
possible and still be called an accepted factual answer. The design must not allow
that answer to license a signal to a potentially reused number.

Remediate as follows:

1. Make the design fail closed after **any** `reap-error`: no later signal is sent
   to that child by the helper, including S4's `SIGKILL`; no retry, alternate signal
   primitive or process search is permitted.
2. Define the handle and sequence transition explicitly. Introduce or refine a
   child state that permits either truth—still unreaped, or reaped in the kernel
   without a handle update—because the helper does not know which occurred. Do not
   label that state `reaped`, `unreaped` or `abandoned` as a fact.
3. Preserve the child handle and `Popen` object for the helper's remaining life,
   record `reap-error`, the send suppression and `effect: "unknown"` for a mutating
   child, and return the enclosing operation's existing fail-closed result. The
   owning procedure and later observer rules remain those of R5; no later procedure
   acts on or searches for the child.
4. Correct row 3g, table SN-S, SN-4/SN-7/SN-8 as needed, RB-5, the RA/point mapping,
   the common child-state set, every affected IM-S cell and dash, records,
   invariants, residuals, review questions, security-review rows, Appendix A/B rows
   and every dependent reference. Keep the at-most-once send rule and the one
   absolute `t_g`; suppression after `reap-error` starts no new wait or grace.
5. Rephrase PO-SN (c) so its citation remains useful evidence about CPython but is
   no longer a safety precondition for deciding whether to send after
   `reap-error`. A factual answer that post-reap exceptions are possible must not
   make the design unsafe or make AP-0 silently pass an unsafe branch.
6. Add focused paper-only cases covering a `reap-error` before a kernel reap and
   after a kernel reap, at S3, S5 and the final attempt; prove zero later sends,
   no PID/group reuse exposure, the indeterminate child truth, fail-closed result,
   correct record or gap, and no later search or retry.

### R6-F2 — SN-S and IM-S disagree on `not-sent(reaped)` (Important)

R5 table SN-S sends every S1 `not-sent` result to S5. Table SN-R rows 3 and 9 and
WB-5(a), however, say that an already-reaped child ends the sequence immediately.
The IM-S outcome `u` includes `not-sent(reaped)`, but the T5/`u` matrix cell is a
dash and the proposal claims every dash is unreachable. The state machine and its
completeness tests therefore cannot all be true.

Remediate as follows:

1. Split S1's branches explicitly:
   - `not-sent(reaped)` or `not-sent(abandoned)` makes no call, begins no wait and
     ends the sequence through the applicable settled-state record path;
   - `not-sent(identity-mismatch)` or
     `not-sent(identity-unverifiable)` makes no send and proceeds to the existing
     capped S5 reap/final-attempt path.
2. Apply the same distinction wherever a send is validated, including the PK-only
   S4 path, without introducing a send after any `not-sent` result.
3. Make table SN-R, table SN-S, WB-5, the outcome definition, T0/T1/T5/T6/T7,
   every affected matrix cell and dash, NT-SN-5/6/7, NT-IS-1/5/6/16 and every
   dependent narrative mutually consistent. If T0 or T1 admits a handle already
   reaped by an enclosing poll, state exactly when the settled-state decision and
   durable record occur; do not place one interruption simultaneously at T0/T1 and
   T7.
4. Add a focused paper-only case that steps interruption before, during and after
   the S1 branch for each `not-sent` subtype and proves the matrix cell, number of
   send calls, waits, handle state and record state. Every dash claimed unreachable
   must actually be unreachable.

## Cumulative proposal and scope controls

Create one self-contained cumulative R6 proposal based on the complete R5
proposal. Preserve R1 through R5 historically. Include a focused change summary,
the two findings and their remediation map, and mark changed sections so a reviewer
can compare the R6 candidate against R5 without splicing documents.

Preserve the safety kernel, existing fact classes, conditional proof obligations,
deadline classes and parameter values, PO-11(d′), accepted Route 3 boundary, SSW
classification, MF dispositions, decisions, baseline-change separation, successor
order and `HARD STOP: concrete Route 3 not established`. Preserve R5's one absolute
`t_g`, remaining-time sleep caps, separation of wait budget from elapsed time,
at-most-once escalation, no-send-result inference, conservative observer rule,
owner-by-enclosing-procedure rule and interactive `attest` with no automatic owner.
Change only what closing R6-F1/R6-F2 directly requires, and identify each
consistency change.

No kernel, language or systemd behavior may be invented or researched. Any needed
behavior absent from named repository evidence remains a proposed, version-bound
proof obligation at the existing citation gate, but the design must be safe for
both answers to the post-reap-exception question. If closing a finding needs a
material scope or design decision beyond this assignment, return `HARD STOP: OH-S3
R6 remediation requires maintainer direction`, state the exact unresolved decision
and preserve the Route 3 hard stop as well.

## Deliverables and permitted edits

Create only:

1. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r6-remediation-proposal.md`;
2. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r6-remediation-handback.md`.

Update only the R6 current-state paragraph, heading and links in:

- `docs/review/Handover information`;
- `docs/project-management/status.md`;
- §20 of `docs/implementation-plan.md`; and
- the restriction banner and its links in
  `docs/operations/disposable-test-server.md`.

Do not edit prior proposals, prompts, authorities or handbacks, accepted historical
evidence, source, tests, configuration, service files, migrations, operational
draft, archives, decision register or change log. Use `apply_patch` for file edits;
local bounded documentation checks are permitted.

The handback must report prompt identity, terminal state, both findings and their
disposition, changed files, exact reading and carried citations, commands/checks
and results, checks not run, security implications, unresolved decisions and review
focus. Distinguish pre-existing changes and confirm the prohibited actions did not
occur. Link the durable handback from the current handover before returning in chat.
Mark R6's authority and prompt consumed in all four pointers. Claim no acceptance
and create no successor authority.

## Verification and handback

Run only bounded local documentation checks on explicit named targets:

- prompt byte count and SHA-256 before edits and at handback;
- unchanged-input digests for R5's proposal, handback, prompt and authority
  recorded before editing and compared after;
- links introduced in the six allowed files, using an explicit target list;
- trailing whitespace and `git diff --check` for the six allowed files;
- R6-versus-R5 comparison: every content change closes a finding or a directly
  necessary consistency correction;
- manual cross-check of every `reap-error` branch before and after a kernel reap,
  the send-suppression rule, the handle state, child-state set, records and owners;
- manual cross-check of S1 and S4 for every `not-sent` subtype, T0/T1/T5/T6/T7,
  every affected matrix cell and dash, and the focused paper-only cases;
- verify no wait after `t_g`, no restarted grace period, no class-X time bound, no
  send-result inference of exit/reaping and no missing `attest` owner case;
- verify all previously retained Route 3, MF and authority restrictions; and
- review the six-file diff for accidental host, implementation, cleanup,
  activation, successor, commit or push authority.

Do not run application tests, hook tests, formatters, builds, package tools,
network checks or remote-host checks.

At the normal terminal state end the handback exactly with:

`HARD STOP: concrete Route 3 not established; OH-S3 R6 remediation awaits independent Codex re-review; no host, implementation, cleanup, OH-S4/OH-S4p or later slice is authorized.`

At another defined hard stop, record its exact reason and end with:

`OH-S3 R6 stopped at the recorded hard stop; Route 3 remains not established; no host, implementation, cleanup, OH-S4/OH-S4p or later slice is authorized.`
