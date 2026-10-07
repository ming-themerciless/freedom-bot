# Claude prompt — OH-S3 R7 independent-review remediation (R8)

Status: **authorized by Peter Duscha on 2026-10-07, subject to the matching
authority record and prompt identity pin**

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-R8-20261007-08`

## Start instruction

Start Claude Code in `/opt/freedom-blades/platform`, then paste:

```text
Execute the authorized repository-only remediation assignment in docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-claude-prompt.md. Close R8-F1 and R8-F2, produce one self-contained cumulative R8 proposal and durable handback, update only the four named current-state pointers, and stop for independent Codex re-review. Preserve HARD STOP: concrete Route 3 not established. Do not access any host, retained evidence, secret, credential or player data; do not perform network research, implementation, launcher work, build, test, cleanup, activation, commit or push.
```

## Authority and terminal boundary

Peter Duscha, Product Owner and Acceptance Authority, authorizes this exact
repository-only documentation assignment through the matching
[authority record](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r8-remediation-authority.md).

R1 through R7 remain unchanged and unaccepted. This assignment permits only the
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
with the R8 remediation ready for independent Codex review. Peter's later recorded
decision is required before any successor.

## Required reading and initial checks

Before editing, read:

1. `.agents/AGENTS.md` completely;
2. the implementation plan's reading map and §§0, 14, 16, 17 and 20;
3. `docs/review/Handover information`, the current project-status pointer and
   the restriction banner in `docs/operations/disposable-test-server.md`;
4. this R8 prompt and its authority completely;
5. the R7 prompt, authority, complete cumulative proposal and complete handback;
6. the R6 proposal only at the grace-deadline, S0/S1, record and interruption
   passages needed to verify that the repair preserves the R7 corrections;
7. the R5 and R4 proposals only at exact sections cited by changed R7 claims,
   where needed to confirm no regression of the earlier accepted review findings;
8. the accepted OH-S2 R2 citation record and one-host design only at exact
   sections cited by changed R7 claims; and
9. the operational draft only at exact Appendix B consumer sections affected
   by this remediation, without editing it.

Do not defer a required repository read or cross-reference check that can be
performed under this authority. Carrying an unchanged citation is allowed if it is
clearly identified as carried; it is not re-verification.

Inspect `git status` and preserve every pre-existing change. Verify this prompt's
byte count and SHA-256 against the authority before any edit and again at handback.
A mismatch is `HARD STOP: OH-S3 R8 prompt identity mismatch`; write its durable
handback and stop without performing remediation.

Read and search exact named documents or explicit safe tracked-file allowlists
only. No recursive search rooted at the repository, a workspace root, home,
`/opt`, `/var`, `/tmp` or `/`, and no secret-bearing path access is permitted.

## Findings to remediate

### R8-F1 — the grace-deadline invariant conflates child history with the current SN invocation (Important)

R7 correctly defines `s0_ran` and `grace_deadline_ms` as durable per-child record
facts: `s0_ran` is true exactly when S0 has run for that child, and the integer
deadline created by that S0 is then retained. It also correctly makes a later SN
call on a settled handle bypass S0 and perform no new clock read. The new text does
not consistently distinguish those two scopes:

* the §7.5a.6e path table marks “S0 ran” as `no` for every settled-handle call,
  while the same row allows an abandoned handle to retain `s0_ran: true` and its
  previously recorded integer deadline; and
* INV-26 says without qualification that “a settled handle” reads no `t_g`, even
  though an abandoned settled handle necessarily retains the `t_g` read by its
  earlier S0. NT-NS-2 states the intended behavior correctly: the re-entry reads
  no **new** `t_g`, while the earlier integer and `s0_ran: true` remain unchanged.

Remediate as follows:

1. Define `s0_ran` unambiguously as a per-child historical fact: true if and only
   if S0 has ever run for that child. It is not reset or reinterpreted by a later
   SN invocation.
2. Distinguish “S0 ever ran for this child” from “S0 runs on this invocation” in
   the §7.5a.6e path table and every dependent narrative. A settled-handle
   re-entry does not run S0 and reads no **new** clock, but it may preserve an
   earlier `s0_ran: true` and integer `grace_deadline_ms`.
3. Correct INV-26 and every affected case, schema statement, Appendix A/B row,
   review question and handback claim so that none says or implies that every
   settled handle has never read `t_g`.
4. Preserve the machine-checkable schema invariant
   `s0_ran == (grace_deadline_ms != null)`. Add or refine a focused paper-only
   case covering both settled histories: a child settled before any S0 and an
   abandoned child settled after S0. The first retains false/null; the second
   retains true/integer; neither re-entry runs S0, reads a new clock, writes a
   second line or starts another grace period.
5. Recheck the pre-S0 `reap-error` path, a child reaped within c, spawn failure,
   every post-S0 path and every settled re-entry. Do not change their sends,
   waits, outcomes or fail-closed behavior merely to simplify the wording.

### R8-F2 — the canonical current-state narrative is out of causal order (Optional)

In each of the four canonical current-state pointers, the R7 execution block was
inserted immediately after R4 and before the R5 and R6 blocks that produced it.
The facts, authority states and restrictions are individually correct, but the
current entry points narrate R4 → R7 → R5 → R6 and therefore obscure the review
chain.

Remediate as follows:

1. In each of the four permitted current-state pointers, order the OH-S3 history
   R1 → R2 → R3 → R4 → R5 → R6 → R7 → R8 return.
2. Move existing blocks without silently rewriting their substantive historical
   facts. Preserve every work ID, prompt identity, finding, disposition,
   acceptance state, restriction and link.
3. Keep each pointer's own style and relative-link form. Do not move this history
   to an archive, edit an archive or shorten it beyond changes directly required
   to restore causal order and add the R8 return.

## Cumulative proposal and scope controls

Create one self-contained cumulative R8 proposal based on the complete R7
proposal. Preserve R1 through R7 historically. Include a focused change summary,
the two findings and their remediation map, and mark every section changed by R8
so a reviewer can compare R8 against R7 without splicing documents.

Preserve R7's substantive repairs: a pre-S0 `reap-error` creates no `t_g`; S0
runs only for a running handle; `s0_ran` and a nullable `grace_deadline_ms` encode
the child's history; after any `reap-error`, no later signal, retry, alternate
primitive, poll, wait or process search occurs; the sole-reaper invariant is
load-bearing; SN-4 is only a detector; no validation guarantee against a foreign
reap or coincidental reuse is claimed; and all four child-handle states remain in
the current vocabulary.

Preserve the safety kernel, existing fact classes, conditional proof obligations,
deadline classes and parameter values, PO-11(d′), accepted Route 3 boundary, SSW
classification, MF dispositions, decisions, baseline-change separation, successor
order and `HARD STOP: concrete Route 3 not established`. Preserve the one absolute
`t_g` for each child whose S0 ever ran, remaining-time sleep caps, separation of
wait budget from elapsed time, at-most-once escalation, no-send-result inference,
conservative observer rule, owner-by-enclosing-procedure rule and interactive
`attest` with no automatic owner.

No kernel, language or systemd behavior may be invented or researched. Any needed
behavior absent from named repository evidence remains a proposed, version-bound
proof obligation at the existing citation gate. If closing a finding needs a
material scope or design decision beyond this assignment, return `HARD STOP:
OH-S3 R8 remediation requires maintainer direction`, state the exact unresolved
decision and preserve the Route 3 hard stop as well.

## Deliverables and permitted edits

Create only:

1. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md`;
2. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-handback.md`.

Update only the OH-S3 narrative, heading and links in:

* `docs/review/Handover information`;
* `docs/project-management/status.md`;
* §20 of `docs/implementation-plan.md`; and
* the restriction banner and its links in
  `docs/operations/disposable-test-server.md`.

Do not edit prior proposals, prompts, authorities or handbacks, accepted historical
evidence, source, tests, configuration, service files, migrations, operational
draft, archives, decision register or change log. Use `apply_patch` for file edits;
bounded local documentation checks on explicit named files are permitted.

The handback must report prompt identity, terminal state, both findings and their
disposition, changed files, exact reading and carried citations, commands/checks
and results, checks not run, security implications, unresolved decisions and
review focus. Distinguish pre-existing changes and confirm the prohibited actions
did not occur. Link the durable handback from the current handover before returning
in chat. Mark R8's authority and prompt consumed in all four pointers. Claim no
acceptance and create no successor authority.

## Verification and handback

Run only bounded local documentation checks on explicit named targets:

* prompt byte count and SHA-256 before edits and at handback;
* unchanged-input digests for R7's proposal, handback, prompt and authority
  recorded before editing and compared after;
* links introduced in the six allowed files, using an explicit target list;
* trailing whitespace and `git diff --check` for the six allowed files;
* R8-versus-R7 comparison: every content change closes a finding or a directly
  necessary consistency correction;
* manual cross-check that `s0_ran` is consistently per-child history and that a
  settled re-entry reads no new clock while preserving any earlier deadline;
* manual cross-check of false/null and true/integer settled histories, including
  the path table, INV-26, schema, cases and Appendix A/B consumers;
* verify no regression of R7-F1 through R7-F3, R6-F1 or R6-F2: no invented
  deadline, no signal after `reap-error`, no send after any `not-sent`, no false
  validation guarantee and all four handle states retained;
* verify the four current-state narratives are in causal R1 → R8 order and that
  every authority state, restriction, finding and link is preserved;
* verify no wait after `t_g`, no restarted grace period, no class-X time bound,
  no send-result inference of exit/reaping and no missing `attest` owner case;
* verify all retained Route 3, MF and authority restrictions; and
* review the six-file diff for accidental host, implementation, cleanup,
  activation, successor, commit or push authority.

Do not run application tests, hook tests, formatters, builds, package tools,
network checks or remote-host checks.

At the normal terminal state end the handback exactly with:

`HARD STOP: concrete Route 3 not established; OH-S3 R8 remediation awaits independent Codex re-review; no host, implementation, cleanup, OH-S4/OH-S4p or later slice is authorized.`

At another defined hard stop, record its exact reason and end with:

`OH-S3 R8 stopped at the recorded hard stop; Route 3 remains not established; no host, implementation, cleanup, OH-S4/OH-S4p or later slice is authorized.`
