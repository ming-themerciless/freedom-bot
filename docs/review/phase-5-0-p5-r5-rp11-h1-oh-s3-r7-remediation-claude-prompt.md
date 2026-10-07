# Claude prompt — OH-S3 R6 independent-review remediation (R7)

Status: **authorized by Peter Duscha on 2026-10-07, subject to the matching
authority record and prompt identity pin**

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-R7-20261007-07`

## Start instruction

Start Claude Code in `/opt/freedom-blades/platform`, then paste:

```text
Execute the authorized repository-only remediation assignment in docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r7-remediation-claude-prompt.md. Close R7-F1, R7-F2 and R7-F3, produce one self-contained cumulative R7 proposal and durable handback, update only the four named current-state pointers, and stop for independent Codex re-review. Preserve HARD STOP: concrete Route 3 not established. Do not access any host, retained evidence, secret, credential or player data; do not perform network research, implementation, launcher work, build, test, cleanup, activation, commit or push.
```

## Authority and terminal boundary

Peter Duscha, Product Owner and Acceptance Authority, authorizes this exact
repository-only documentation assignment through the matching
[authority record](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r7-remediation-authority.md).

R1 through R6 remain unchanged and unaccepted. This assignment permits only the
focused remediation below and directly necessary consistency corrections. It does
not accept a design, decide a residual, change the accepted Route 3 boundary,
resolve its hard stop, add a new identity mechanism or authorize a successor.

No SSH or other host connection, `oracle-test`, production, staging, Foundry or
database access, retained-evidence access, secret, credential or player-data
access, network research, package operation or installation, implementation or
configuration edit, launcher retarget or rebuild, application or hook test,
formatter, build, service/database mutation, cleanup, workspace recreation,
OH-S4/OH-S4p or later slice, H-1/H-2, activation, rollback, commit or push is
authorized.

The normal terminal state remains `HARD STOP: concrete Route 3 not established`
with the R7 remediation ready for independent Codex review. Peter's later recorded
decision is required before any successor.

## Required reading and initial checks

Before editing, read:

1. `.agents/AGENTS.md` completely;
2. the implementation plan's reading map and §§0, 14, 16, 17 and 20;
3. `docs/review/Handover information`, the current project-status pointer and
   the restriction banner in `docs/operations/disposable-test-server.md`;
4. this R7 prompt and its authority completely;
5. the R6 prompt, authority, complete cumulative proposal and complete handback;
6. the R5 proposal only at the reap-attempt boundary and paper cases needed to
   confirm that the remediation does not regress R5-F1 or R5-F2;
7. the R4 proposal only at table SN-S, table SN-R, WB-5 and IM-S where needed to
   confirm that the remediation does not regress R4-F1 or R4-F2;
8. the R3 proposal only at the signal-sending contract where needed to confirm
   that the remediation does not regress R3-F1;
9. the accepted OH-S2 R2 citation record and one-host design only at exact
   sections cited by changed R6 claims; and
10. the operational draft only at exact Appendix B consumer sections affected
    by this remediation, without editing it.

Do not defer a required repository read or cross-reference check that can be
performed under this authority. Carrying an unchanged citation is allowed if it is
clearly identified as carried; it is not re-verification.

Inspect `git status` and preserve every pre-existing change. Verify this prompt's
byte count and SHA-256 against the authority before any edit and again at handback.
A mismatch is `HARD STOP: OH-S3 R7 prompt identity mismatch`; write its durable
handback and stop without performing remediation.

Read and search exact named documents or explicit safe tracked-file allowlists
only. No recursive search rooted at the repository, a workspace root, home,
`/opt`, `/var`, `/tmp` or `/`, and no secret-bearing path access is permitted.

## Findings to remediate

### R7-F1 — the pre-S0 `reap-error` path has no defined grace-deadline record (Important)

R6 correctly sends a `reap-error` in a poll of the enclosing E wait directly
through S8 and S7. That path occurs before a deadline or flag triggers SN and
therefore before S0 creates `t_g`. The record schema nevertheless requires
`grace_deadline_ms`, INV-22 says each child has one grace deadline, and NT-RE-11
asserts one `t_g` read across random attempt positions. NT-RE-7 is therefore not
implementable together with the schema, invariant and test as written.

Remediate as follows:

1. Define one explicit representation for a child whose enclosing-wait poll
   raises before S0. `grace_deadline_ms` must be absent or `null` for that path;
   do not invent a deadline, enter S0, read a clock merely for the record, or
   start a grace period.
2. State that `t_g` exists exactly when S0 ran. Preserve the rule that, once it
   exists, it is read once and never moved, extended or restarted. A pre-S0
   `reap-error` reads it zero times.
3. Correct §7.5a.9, §8.5, INV-22, NT-SN-9, NT-RE-7, NT-RE-11, NT-RE-12 and every
   dependent record, schema, Appendix A/B and handback statement. Make the
   distinction machine-checkable rather than implicit.
4. Add or refine a focused paper-only case proving: enclosing poll raises before
   S0; no `t_g` read; `grace_deadline_ms` absent or null; zero send, wait, further
   poll or search; S8/S7 record the `reap-unknown` result; the enclosing operation
   fails closed.

### R7-F2 — CC-30 assumes validation always detects a foreign reap and reuse (Important)

R6 NT-SN-12 injects a foreign reaper, leaves the handle state unchanged, and then
claims validation necessarily returns `identity-mismatch` or
`identity-unverifiable`, so no stale number is signalled. That does not follow. A
released PID and process-group number can be reused by a new process whose PID,
PGID and SID have the same structural relationship; the `start_ticks` check is
optional under PO-SN (d). SN-4 is a detector, not the reuse defence. The actual
reuse defence remains SI-3's sole-reaper invariant plus PO-SN (b), (c) and (f).

Remediate as follows:

1. Withdraw CC-30's universal claim that ordinary validation detects every
   foreign reap/reuse and that the injected state necessarily reaches S1-b.
2. Keep the sole-reaper contract explicit and load-bearing: no thread, signal
   disposition, destructor, foreign `wait*` call or other path may reap outside
   `reap_step()`. Its version-bound obligations and AP-0 refusal stay unchanged.
3. Treat an injected foreign reap as a deliberate violation of the design
   precondition, not as a supported runtime state. NT-SN-12 should prove the
   structural sole-reaper properties. If it retains a detector exercise, label
   it as a non-universal detector case with a deliberately mismatching fake
   identity; do not infer a guarantee against coincidental reuse.
4. State the consequence honestly: after the sole-reaper invariant is violated,
   this design makes no reuse-safety claim from SN-4 alone. Do not add a mandatory
   `start_ticks`, pidfd or other new identity mechanism in this remediation.
5. Correct CC-30, NT-SN-12, the reuse narrative, invariants, review questions,
   security-review rows and remediation map wherever they carry the false claim.

### R7-F3 — the child-handle vocabulary omits `reap-unknown` (Optional)

The normative handle definition in §7.5a.3 correctly has four states, but the
vocabulary row for CH still lists only `running`, `reaped` and `abandoned`. This
contradicts R6's CC-26 propagation statement.

Remediate as follows:

1. Add `reap-unknown` to the CH vocabulary state set.
2. Check every current, non-historical definition of the handle state set for
   the same omission. Historical descriptions and withdrawn-claim tables remain
   historical and must not be silently rewritten.

## Cumulative proposal and scope controls

Create one self-contained cumulative R7 proposal based on the complete R6
proposal. Preserve R1 through R6 historically. Include a focused change summary,
the three findings and their remediation map, and mark every section changed by R7
so a reviewer can compare R7 against R6 without splicing documents.

Preserve R6's substantive repair: after any `reap-error`, no later signal, retry,
alternate primitive, poll, wait or process search occurs; `reap-unknown` permits
both kernel truths; PO-SN (c′) remains evidence-only; and the S1 settled-handle and
identity-rejection branches remain distinct. Preserve the safety kernel, existing
fact classes, conditional proof obligations, deadline classes and parameter
values, PO-11(d′), accepted Route 3 boundary, SSW classification, MF dispositions,
decisions, baseline-change separation, successor order and
`HARD STOP: concrete Route 3 not established`.

Preserve the one absolute `t_g` for every sequence in which S0 ran, remaining-time
sleep caps, separation of wait budget from elapsed time, at-most-once escalation,
no-send-result inference, conservative observer rule, owner-by-enclosing-procedure
rule and interactive `attest` with no automatic owner. Change only what closing
R7-F1 through R7-F3 directly requires, and identify each consistency correction.

No kernel, language or systemd behavior may be invented or researched. Any needed
behavior absent from named repository evidence remains a proposed, version-bound
proof obligation at the existing citation gate. If closing a finding needs a
material scope or design decision beyond this assignment, return `HARD STOP:
OH-S3 R7 remediation requires maintainer direction`, state the exact unresolved
decision and preserve the Route 3 hard stop as well.

## Deliverables and permitted edits

Create only:

1. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r7-remediation-proposal.md`;
2. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r7-remediation-handback.md`.

Update only the R7 current-state paragraph, heading and links in:

- `docs/review/Handover information`;
- `docs/project-management/status.md`;
- §20 of `docs/implementation-plan.md`; and
- the restriction banner and its links in
  `docs/operations/disposable-test-server.md`.

Do not edit prior proposals, prompts, authorities or handbacks, accepted historical
evidence, source, tests, configuration, service files, migrations, operational
draft, archives, decision register or change log. Use `apply_patch` for file edits;
bounded local documentation checks on explicit named files are permitted.

The handback must report prompt identity, terminal state, all three findings and
their disposition, changed files, exact reading and carried citations,
commands/checks and results, checks not run, security implications, unresolved
decisions and review focus. Distinguish pre-existing changes and confirm the
prohibited actions did not occur. Link the durable handback from the current
handover before returning in chat. Mark R7's authority and prompt consumed in all
four pointers. Claim no acceptance and create no successor authority.

## Verification and handback

Run only bounded local documentation checks on explicit named targets:

- prompt byte count and SHA-256 before edits and at handback;
- unchanged-input digests for R6's proposal, handback, prompt and authority
  recorded before editing and compared after;
- links introduced in the six allowed files, using an explicit target list;
- trailing whitespace and `git diff --check` for the six allowed files;
- R7-versus-R6 comparison: every content change closes a finding or a directly
  necessary consistency correction;
- manual cross-check of the enclosing-wait pre-S0 `reap-error` path through S8
  and S7, including clock-read count and every record field;
- manual cross-check that every path with S0 has exactly one `t_g`, every path
  without S0 has none, and neither case starts or restarts a grace period;
- manual cross-check of the sole-reaper invariant, CC-30's replacement,
  NT-SN-12 and every PID/group-reuse claim; SN-4 must remain a detector only;
- verify the current CH vocabulary and every current handle-state definition list
  all four states;
- verify no regression of R6-F1 or R6-F2: no signal after `reap-error`, no send
  after any `not-sent`, and the S1/S4 branches and matrix remain consistent;
- verify no wait after `t_g`, no restarted grace period, no class-X time bound,
  no send-result inference of exit/reaping and no missing `attest` owner case;
- verify all previously retained Route 3, MF and authority restrictions; and
- review the six-file diff for accidental host, implementation, cleanup,
  activation, successor, commit or push authority.

Do not run application tests, hook tests, formatters, builds, package tools,
network checks or remote-host checks.

At the normal terminal state end the handback exactly with:

`HARD STOP: concrete Route 3 not established; OH-S3 R7 remediation awaits independent Codex re-review; no host, implementation, cleanup, OH-S4/OH-S4p or later slice is authorized.`

At another defined hard stop, record its exact reason and end with:

`OH-S3 R7 stopped at the recorded hard stop; Route 3 remains not established; no host, implementation, cleanup, OH-S4/OH-S4p or later slice is authorized.`
