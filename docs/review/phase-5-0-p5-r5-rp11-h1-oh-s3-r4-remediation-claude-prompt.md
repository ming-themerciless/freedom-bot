# Claude prompt — OH-S3 R3 independent-review remediation (R4)

Status: **authorized by Peter Duscha on 2026-10-07, subject to the matching
authority record and prompt identity pin**

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-R4-20261007-04`

## Start instruction

Start Claude Code in `/opt/freedom-blades/platform`, then paste:

```text
Execute the authorized repository-only remediation assignment in docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r4-remediation-claude-prompt.md. Close R4-F1 and R4-F2, produce one self-contained cumulative R4 proposal and durable handback, update only the four named current-state pointers, and stop for independent Codex re-review. Preserve HARD STOP: concrete Route 3 not established. Do not access any host, retained evidence, secret, credential or player data; do not perform network research, implementation, launcher work, build, test, cleanup, activation, commit or push.
```

## Authority and terminal boundary

Peter Duscha, Product Owner and Acceptance Authority, authorizes this exact
repository-only documentation assignment through the matching
[authority record](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r4-remediation-authority.md).

R1, R2 and R3 remain unchanged and unaccepted. This assignment permits only the
focused remediation below and directly necessary consistency corrections. It
does not accept a design, decide a residual, change the accepted Route 3 boundary,
resolve its hard stop, or authorize a successor.

No SSH or other host connection, `oracle-test`, production, staging, Foundry or
database access, retained-evidence access, secret, credential or player-data
access, network research, package operation or installation, implementation or
configuration edit, launcher retarget or rebuild, application or hook test,
formatter, build, service/database mutation, cleanup, workspace recreation,
OH-S4/OH-S4p or later slice, H-1/H-2, activation, rollback, commit or push is
authorized.

The normal terminal state remains `HARD STOP: concrete Route 3 not established`
with the R4 remediation ready for independent Codex review. Peter's later
recorded decision is required before any successor.

## Required reading and initial checks

Before editing, read:

1. `.agents/AGENTS.md` completely;
2. the implementation plan's reading map and §§0, 14, 16, 17 and 20;
3. `docs/review/Handover information`, the current project-status pointer and
   the restriction banner in `docs/operations/disposable-test-server.md`;
4. this R4 prompt and its authority completely;
5. the R3 prompt, authority, complete cumulative proposal and complete handback;
6. the R2 proposal at the deadline, signal, interruption and amendment sections
   carried by R3, as needed for consistency;
7. the accepted OH-S2 R2 citation record and one-host design at the exact sections
   relevant to the changed claims; and
8. the operational draft at the exact Appendix B consumer sections affected by
   this remediation, without editing it.

Do not defer a required repository read or a cross-reference check to a future
slice when it can be performed under this authority. Carrying an unchanged
citation is allowed if clearly identified as carried; it is not re-verification.

Inspect `git status` and preserve all pre-existing changes. Verify this prompt's
byte count and SHA-256 against the authority before any edit and again at handback.
A mismatch is `HARD STOP: OH-S3 R4 prompt identity mismatch`; write its durable
handback and stop without performing remediation.

Read and search exact named documents or explicit safe tracked-file allowlists
only. No recursive search rooted at the repository, a workspace root, home,
`/opt`, `/var`, `/tmp` or `/`, and no secret-bearing path access is permitted.

## Findings to remediate

### R4-F1 — the send sequence can exceed its stated wait budget (Important)

R3's table SN-S sets `t_g` before the first send at S0. S3 then waits a full
`slice_ms` after `SIGTERM` returns without checking the remaining grace period.
If the class-X send consumed all of g, this adds waiting beyond `t_g` while R3
retains W_show = c + g and W_series = P + c + g as wait budgets.

Remediate as follows:

1. Keep one absolute `t_g`, set before the first send. Cap every S3 and S5 wait
   by the remaining interval to that deadline; no new grace period starts after
   a send, validation, poll, error or signal receipt.
2. If a send or validation returns at or after `t_g`, skip all subsequent timed
   waits. Preserve the existing at-most-once, identity-validated escalation
   decision at S4, which may still make a class-X call; do not present it as
   completion within g. Then take the appropriate reap-or-abandon result.
3. Specify boundary ordering for a child already reaped, one that exits during
   a send, and one still unreaped when the deadline is reached. A non-blocking
   reap attempt is class X and must not become an unbounded timed wait.
4. State the wait budget separately from elapsed procedure time. No send,
   validation or other class-X operation acquires a time bound. No sizing rule
   becomes a completion guarantee.
5. Correct every dependent sentence and test, including CC-1, CC-2, SN-R,
   SN-S, SN-6, HS-5, PK/2, SG-4, the parameter notes, invariants and amendment
   tables. In particular, remove any unconditional claim that return occurs
   within g or that every signal is sent only after a full slice.
6. Define regression cases on a fake clock for a send consuming less than,
   exactly, and more than g; a send leaving less than one slice; a slow
   validation; an expired deadline before S3/S5; successful and failed sends;
   and a child reaped at the boundary. Assert no timed wait begins after `t_g`
   and total scheduled waiting stays within the existing budget. Define these
   tests on paper only; do not implement or execute them.

### R4-F2 — the interruption map assumes successful signal delivery (Important)

R3's IM-S labels T2 "signalled" and T3 "killed, or alive in an uninterruptible
call" although SN permits failed, indeterminate and unmade sends. A child can
remain alive because delivery failed. The map also uses "as S0" and "as S3"
where its own rows are T0 through T5, and does not preserve the interactive
`attest` case with no automatic recovery owner. These statements contradict
SN-7 and INV-20's rule that no send result proves exit or reaping.

Remediate as follows:

1. Rewrite IM-S so every interruption point represents successful, failed,
   indeterminate and unmade sends. "Sent" means only the proposed kernel send
   result; only a recorded reap status proves the direct child was reaped.
   After any send the target may remain alive. Do not infer group emptiness
   from reaping the direct child.
2. Map the cross-product of interruption point and send outcome explicitly,
   using a compact table plus a clearly defined common state set if useful.
   Include validation failure, `ESRCH`, other errors, partial escalation,
   death of the helper during a send, reaping, and abandonment.
3. Correct every row reference. Separate local sends already attempted from
   the absence of further sends by the terminated helper; remove the absolute
   statement that every interrupted helper leaves children "unsignalled by
   anyone" when earlier sends or proposed PID-1 cleanup may apply.
4. Preserve recovery ownership by enclosing procedure: holder, CP, stop-post,
   backstop service and interactive `attest`. Use SN-RO's proposed cgroup
   obligations for unit cases; explicitly retain `attest`'s lack of an
   automatic owner. State the boot as a separate recovery event, not evidence
   that a signal succeeded.
5. Propagate the corrected states to terminal-cause rows 19/20, RO-7,
   records and gaps, invariants, review focus and affected Appendix A/B rows.
   Preserve mutating-child effect `unknown` and the existing fail-closed
   enclosing result; do not grant a retry or a process-hunting operation.
6. Define stepped regression cases interrupting each IM-S point after success,
   `ESRCH`, another send error, identity rejection and an unmade send, with a
   child still alive, exited but unreaped, reaped, or abandoned as applicable.
   Include the interactive `attest` case and lost child records. Assert the
   state and owner without deriving exit or reaping from a send result.
   Define these tests on paper only; do not implement or execute them.

## Cumulative proposal and scope controls

Create one self-contained cumulative R4 proposal based on the complete R3
proposal. Preserve R1, R2 and R3 historically. Include a focused change summary,
the two findings and their remediation map, and mark changed sections so a
reviewer can compare the R4 candidate against R3 without splicing documents.

Preserve the safety kernel, existing fact classes, conditional proof obligations,
deadline classes and parameter values, PO-11(d′), accepted Route 3 boundary,
SSW classification, MF dispositions, decisions, baseline-change separation,
successor order and `HARD STOP: concrete Route 3 not established`. Change only
what closing R4-F1/R4-F2 directly requires, and identify each consistency change.

No kernel, language or systemd behavior may be invented or researched. Any
needed behavior absent from named repository evidence remains a proposed,
version-bound proof obligation at the existing citation gate. If closing a
finding needs a material scope or design decision beyond this assignment,
return `HARD STOP: OH-S3 R4 remediation requires maintainer direction`, state
the exact unresolved decision and preserve the Route 3 hard stop as well.

## Deliverables and permitted edits

Create only:

1. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r4-remediation-proposal.md`;
2. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r4-remediation-handback.md`.

Update only the R4 current-state paragraph, heading and links in:

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
handover before returning in chat. Mark R4's authority and prompt consumed in
all four pointers. Claim no acceptance and create no successor authority.

## Verification and handback

Run only bounded local documentation checks on explicit named targets:

- prompt byte count and SHA-256 before edits and at handback;
- unchanged-input digests for R3's proposal, handback, prompt and authority
  recorded before editing and compared after;
- links introduced in the six allowed files, using an explicit target list;
- trailing whitespace and `git diff --check` for the six allowed files;
- R4-versus-R3 comparison: every content change closes a finding or a directly
  necessary consistency correction;
- scan and manual cross-check of SN-S, SN-R, IM-S, SN-RO, CC-1/CC-2, HS-5,
  PK/2, SG-4, records, invariants, residuals and Appendix A/B obligations;
- verify no wait after `t_g`, no restarted grace period, no class-X time bound,
  no send-result inference of exit/reaping, and no missing `attest` owner case;
- verify all previously retained Route 3, MF and authority restrictions; and
- review the six-file diff for accidental host, implementation, cleanup,
  activation, successor, commit or push authority.

Do not run application tests, hook tests, formatters, builds, package tools,
network checks or remote-host checks.

At the normal terminal state end the handback exactly with:

`HARD STOP: concrete Route 3 not established; OH-S3 R4 remediation awaits independent Codex re-review; no host, implementation, cleanup, OH-S4/OH-S4p or later slice is authorized.`

At another defined hard stop, record its exact reason and end with:

`OH-S3 R4 stopped at the recorded hard stop; Route 3 remains not established; no host, implementation, cleanup, OH-S4/OH-S4p or later slice is authorized.`
