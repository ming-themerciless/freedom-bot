# Claude prompt — OH-S3 R4 independent-review remediation (R5)

Status: **authorized by Peter Duscha on 2026-10-07, subject to the matching
authority record and prompt identity pin**

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-R5-20261007-05`

## Start instruction

Start Claude Code in `/opt/freedom-blades/platform`, then paste:

```text
Execute the authorized repository-only remediation assignment in docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r5-remediation-claude-prompt.md. Close R5-F1 and R5-F2, produce one self-contained cumulative R5 proposal and durable handback, update only the four named current-state pointers, and stop for independent Codex re-review. Preserve HARD STOP: concrete Route 3 not established. Do not access any host, retained evidence, secret, credential or player data; do not perform network research, implementation, launcher work, build, test, cleanup, activation, commit or push.
```

## Authority and terminal boundary

Peter Duscha, Product Owner and Acceptance Authority, authorizes this exact
repository-only documentation assignment through the matching
[authority record](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r5-remediation-authority.md).

R1, R2, R3 and R4 remain unchanged and unaccepted. This assignment permits
only the focused remediation below and directly necessary consistency
corrections. It does not accept a design, decide a residual, change the accepted
Route 3 boundary, resolve its hard stop or authorize a successor.

No SSH or other host connection, `oracle-test`, production, staging, Foundry or
database access, retained-evidence access, secret, credential or player-data
access, network research, package operation or installation, implementation or
configuration edit, launcher retarget or rebuild, application or hook test,
formatter, build, service/database mutation, cleanup, workspace recreation,
OH-S4/OH-S4p or later slice, H-1/H-2, activation, rollback, commit or push is
authorized.

The normal terminal state remains `HARD STOP: concrete Route 3 not established`
with the R5 remediation ready for independent Codex review. Peter's later
recorded decision is required before any successor.

## Required reading and initial checks

Before editing, read:

1. `.agents/AGENTS.md` completely;
2. the implementation plan's reading map and §§0, 14, 16, 17 and 20;
3. `docs/review/Handover information`, the current project-status pointer and
   the restriction banner in `docs/operations/disposable-test-server.md`;
4. this R5 prompt and its authority completely;
5. the R4 prompt, authority, complete cumulative proposal and complete handback;
6. the R3 proposal only at the interruption-map and signal-sequence text carried
   into R4, as needed to confirm the remediation does not regress R3-F1;
7. the accepted OH-S2 R2 citation record and one-host design only at the exact
   sections cited by changed R4 claims; and
8. the operational draft only at the exact Appendix B consumer sections affected
   by this remediation, without editing it.

Do not defer a required repository read or cross-reference check that can be
performed under this authority. Carrying an unchanged citation is allowed if it
is clearly identified as carried; it is not re-verification.

Inspect `git status` and preserve every pre-existing change. Verify this prompt's
byte count and SHA-256 against the authority before any edit and again at
handback. A mismatch is `HARD STOP: OH-S3 R5 prompt identity mismatch`; write its
durable handback and stop without performing remediation.

Read and search exact named documents or explicit safe tracked-file allowlists
only. No recursive search rooted at the repository, a workspace root, home,
`/opt`, `/var`, `/tmp` or `/`, and no secret-bearing path access is permitted.

## Findings to remediate

### R5-F1 — IM-S omits reaping completed inside an interrupted reap attempt (Important)

R4 defines T3 and T5 as including a reap attempt and defines T6 only after the
sequence has decided. The T3 and T5 matrix cells map to CS-2, CS-3 or CS-4,
whose direct-child descriptions allow only alive or exited-and-unreaped states.
But E1 and NT-IS-8 admit that the helper can end after the kernel has reaped the
direct child and before the helper has durably represented that result. T6 cannot
cover an interruption inside the attempt because T6 begins after the decision.
NT-IS-1 therefore cannot truthfully prove that every reachable cell has the
exact state named by the matrix.

Remediate as follows:

1. Define the exact interruption boundary of a reap attempt, including the case
   where the kernel has reaped the direct child but the helper ends before its
   handle state or `child` line records that result.
2. Make T3, T5 and T6 mutually consistent with that boundary. Do not classify an
   interruption inside an attempt as T6 unless T6 is explicitly redefined so it
   no longer means that the sequence has already decided.
3. Extend or refine the common child-state set and matrix so every reachable
   interruption has a state that permits the true direct-child condition. It is
   acceptable to map the relevant T3/T5 case to CS-5 if CS-5 is defined to cover
   a reap completed in the kernel with no durable record, or to introduce a
   separate state if needed. Do not infer the state from a send result.
4. Preserve the conservative observer rule: without a durable `child` line, a
   later procedure learns no reap fact and records only the applicable gap or
   `children-unknown`. A kernel reap that was not durably recorded is not later
   evidence that the group is empty.
5. Correct E1, the matrix narrative, INV-18/INV-20/INV-23, terminal-state and
   record text, review questions, Appendix A/B rows and every affected reference.
6. Correct NT-IS-1 and NT-IS-8 and add any focused paper-only case needed to
   distinguish: interruption before the reap call; inside the call before a reap;
   after the kernel reap but before handle-state update; after handle-state update
   but before the durable line; and after the durable line. Every matrix dash
   claimed unreachable must actually be unreachable.

### R5-F2 — NT-WB-5 gives one impossible expectation to two slow-validation runs (Important)

NT-WB-5 combines an S1 validation costing 2,100 ms with a second run in which
S4's validation costs 2,100 ms, then asserts for both that S3 and S5 skip every
timed wait and that both `SIGTERM` and `SIGKILL` are late. Those assertions fit a
slow S1 that consumes g. They do not necessarily fit a run in which S1 and the
first send are prompt and only S4 is slow: S3 may already have made its capped
wait, and `SIGTERM` need not be late.

Remediate as follows:

1. Split NT-WB-5 into explicit slow-S1 and slow-S4 cases, whether as subcases or
   separate rows.
2. For slow S1, state the expected S3/S5 waits and `late` fields from the actual
   clock: after S1 consumes g, no later timed wait begins; the sends made after
   the deadline are recorded late.
3. For slow S4, give S1, `SIGTERM` and S3 explicit costs or clock positions. Allow
   S3's capped wait when it begins before `t_g`; do not mark `SIGTERM` late unless
   its own return is at or after `t_g`. A slow S4 consumes the remaining grace,
   so S5 makes no timed wait once the deadline has passed; `SIGKILL` is late when
   its return is at or after `t_g`.
4. Keep the shared assertions: one `t_g`, no restarted grace, no timed wait starts
   at or after it, each send is attempted at most once, scheduled waiting remains
   within g and no class-X operation receives an elapsed-time bound.
5. Propagate the split to the case table, remediation map, handback summary and
   any cross-reference that counts or names the R5 paper-only cases.

## Cumulative proposal and scope controls

Create one self-contained cumulative R5 proposal based on the complete R4
proposal. Preserve R1, R2, R3 and R4 historically. Include a focused change
summary, the two findings and their remediation map, and mark changed sections so
a reviewer can compare the R5 candidate against R4 without splicing documents.

Preserve the safety kernel, existing fact classes, conditional proof
obligations, deadline classes and parameter values, PO-11(d′), accepted Route 3
boundary, SSW classification, MF dispositions, decisions, baseline-change
separation, successor order and `HARD STOP: concrete Route 3 not established`.
Preserve R4's one absolute `t_g`, remaining-time sleep caps, separation of wait
budget from elapsed time, at-most-once escalation, no-send-result inference,
owner-by-enclosing-procedure rule and interactive `attest` with no automatic
owner. Change only what closing R5-F1/R5-F2 directly requires, and identify each
consistency change.

No kernel, language or systemd behavior may be invented or researched. Any
needed behavior absent from named repository evidence remains a proposed,
version-bound proof obligation at the existing citation gate. If closing a
finding needs a material scope or design decision beyond this assignment, return
`HARD STOP: OH-S3 R5 remediation requires maintainer direction`, state the exact
unresolved decision and preserve the Route 3 hard stop as well.

## Deliverables and permitted edits

Create only:

1. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r5-remediation-proposal.md`;
2. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r5-remediation-handback.md`.

Update only the R5 current-state paragraph, heading and links in:

- `docs/review/Handover information`;
- `docs/project-management/status.md`;
- §20 of `docs/implementation-plan.md`; and
- the restriction banner and its links in
  `docs/operations/disposable-test-server.md`.

Do not edit prior proposals, prompts, authorities or handbacks, accepted
historical evidence, source, tests, configuration, service files, migrations,
operational draft, archives, decision register or change log. Use `apply_patch`
for file edits; local bounded documentation checks are permitted.

The handback must report prompt identity, terminal state, both findings and
their disposition, changed files, exact reading and carried citations,
commands/checks and results, checks not run, security implications, unresolved
decisions and review focus. Distinguish pre-existing changes and confirm the
prohibited actions did not occur. Link the durable handback from the current
handover before returning in chat. Mark R5's authority and prompt consumed in
all four pointers. Claim no acceptance and create no successor authority.

## Verification and handback

Run only bounded local documentation checks on explicit named targets:

- prompt byte count and SHA-256 before edits and at handback;
- unchanged-input digests for R4's proposal, handback, prompt and authority
  recorded before editing and compared after;
- links introduced in the six allowed files, using an explicit target list;
- trailing whitespace and `git diff --check` for the six allowed files;
- R5-versus-R4 comparison: every content change closes a finding or a directly
  necessary consistency correction;
- manual cross-check of the reap-attempt boundary, T3/T5/T6, E1, CS states, every
  matrix cell and dash, `children-unknown`, NT-IS-1 and NT-IS-8;
- manual cross-check of both slow-validation cases, their clock positions,
  waits, sends and `late` values;
- verify no wait after `t_g`, no restarted grace period, no class-X time bound,
  no send-result inference of exit/reaping and no missing `attest` owner case;
- verify all previously retained Route 3, MF and authority restrictions; and
- review the six-file diff for accidental host, implementation, cleanup,
  activation, successor, commit or push authority.

Do not run application tests, hook tests, formatters, builds, package tools,
network checks or remote-host checks.

At the normal terminal state end the handback exactly with:

`HARD STOP: concrete Route 3 not established; OH-S3 R5 remediation awaits independent Codex re-review; no host, implementation, cleanup, OH-S4/OH-S4p or later slice is authorized.`

At another defined hard stop, record its exact reason and end with:

`OH-S3 R5 stopped at the recorded hard stop; Route 3 remains not established; no host, implementation, cleanup, OH-S4/OH-S4p or later slice is authorized.`
