# Claude prompt — OH-S3 R1 independent-review remediation (R2)

Status: **authorized by Peter Duscha on 2026-10-07, subject to the matching
authority record and prompt identity pin**

Work ID: `C-P5.0-R5-RP11-H1-OH-S3-R2-20261007-02`

## Start instruction

Start Claude Code in `/opt/freedom-blades/platform`, then paste:

```text
Execute the authorized repository-only remediation assignment in docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r2-remediation-claude-prompt.md. Remediate both independent-review findings against OH-S3 R1, produce one self-contained cumulative R2 proposal and durable handback, update only the four named current-state pointers, and stop for independent Codex re-review. Do not access any host, retained evidence, secret, credential or player data; do not perform network research, implementation, launcher work, build, test, cleanup, activation, commit or push.
```

## Authority and terminal boundary

Peter Duscha, Product Owner and Acceptance Authority, authorizes this exact
repository-only documentation assignment. The matching authority record is
[`project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r2-remediation-authority.md`](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r2-remediation-authority.md).

OH-S3 R1 remains unaccepted and historically unchanged. This assignment may
replace its proposal as the cumulative forward candidate but may not accept it,
approve a decision, broaden Route 3, or authorize a successor.

No SSH or other host connection, `oracle-test`, production, staging, Foundry or
database access, retained-evidence access, secret, credential or player-data
access, network research, package operation or installation, implementation or
configuration edit, launcher retarget or rebuild, application or hook test,
formatter, build, service/database mutation, cleanup, workspace recreation,
OH-S4/OH-S4p or later slice, H-1/H-2, activation, rollback, commit or push is
authorized.

The assignment ends at `OH-S3 R2 REMEDIATION READY FOR REVIEW` or its first
defined `HARD STOP`. Independent Codex re-review and Peter's later recorded
decision remain mandatory.

## Required reading and initial checks

Before editing, read completely:

1. `.agents/AGENTS.md`;
2. the reading map and §§0, 14, 16, 17 and 20 of
   `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. the restriction banner in
   `docs/operations/disposable-test-server.md`;
5. this R2 prompt and its matching authority;
6. the R1 prompt, authority, complete proposal and complete handback;
7. the accepted cumulative OH-S2 R2 citation record, its handback and
   acceptance;
8. the cumulative one-host design amendment, especially its accepted Route 3
   definition and §§4.1–4.7;
9. the accepted H-0 completeness proposal and acceptance;
10. the accepted C11 launcher contract and relevant D2 records cited by R1;
11. the operational draft as a future consumer, without editing it; and
12. the current project-status pointer.

Inspect `git status` and preserve every unrelated or pre-existing change.
Verify this prompt's exact byte count and SHA-256 against its authority before
any edit. A mismatch is `HARD STOP: OH-S3 R2 prompt identity mismatch`.

Do not use recursive searches rooted at the repository, a workspace root, the
user's home, `/opt`, `/var`, `/tmp` or `/`. Search only exact named documents or
explicit safe tracked-file allowlists. Never read or test a secret-bearing path.

## Independent-review findings to remediate

### R2-F1 — the recommended RT3-A does not satisfy the authorized Route 3 boundary

The R1 assignment required a concrete Route 3 that eliminates the ambient
CPython-startup dependency, including dynamic-loader inputs for root helper
processes. The already accepted DR1 definition describes Route 3 as abandoning
the Python-dependent path. R1 instead re-scoped “Route 3” to elimination of
environment-derived inputs, retained CPython and glibc in every root-helper
path, left file-based loader inputs to MF-1, MF-2 and MF-4, and asked Peter to
confirm that new scope in DEC-1.

A static first image can close inherited environment and descriptors, but it
does not eliminate the dynamic loader, interpreter or their file-based inputs
from the root-helper path. RT3-A may therefore remain a separately named,
bounded alternative, but R2 must not call it conforming Route 3 or recommend it
as the answer to the existing requirement unless a prior, separately recorded
scope decision explicitly changes that requirement. This assignment does not
make that decision.

Remediate as follows:

1. preserve R1 unchanged and state that its recommended RT3-A did not meet the
   authorized Route 3 boundary;
2. restore the accepted Route 3 meaning throughout the cumulative proposal:
   the root procedures that touch the grant and activation mechanism do not run
   through CPython or a dynamic loader;
3. produce a decision-ready concrete design only if repository evidence is
   sufficient to define that Python-free root path without inventing facts;
4. if repository evidence is insufficient, present exact bounded alternatives,
   including the work needed to make literal Route 3 decision-ready, and end at
   `HARD STOP: concrete Route 3 not established` as the R1 prompt required;
5. keep RT3-A, if useful, under a new unambiguous name such as
   `STATIC-SCRUB-WRAPPER`; describe it as a scope-change alternative, not Route
   3, and identify the explicit baseline decision needed before it could be
   selected;
6. do not use DEC-1 to make a material scope change inside acceptance of the
   remediation proposal. Any change to the accepted Route 3 boundary must follow
   implementation-plan §0.2 change control before design acceptance;
7. re-evaluate the Role A–H inventory, PO-12′, PO-19, MF-1 through MF-8,
   OH-S4/OH-S4p split, rebuild chain, PO-17 boundary, trusted/runtime-surface
   comparison and successor order under the corrected boundary; and
8. do not claim that root-owned dynamic inputs cease to be inputs merely because
   the threat model excludes an unprivileged writer.

### R2-F2 — claimed cleanup bounds contain unbounded local work

R1 says CL's worst-case duration is
`lock_wait_ms + local work + (pk_op_ms + pk_call_ms)` and then claims it is less
than `TimeoutStopSec` “by the S grammar.” The grammar merely reserves a fixed
30-second margin; it does not bound the named local work. That work includes
filesystem inspection, full hashing, process creation and reaping, journal
writes and `fsync`. R1 similarly claims that IGR acts within “about ten seconds”
after accounting for interrupted sleeps or child waits, while its own IGR
procedure also performs descriptor verification, a full hash, `unlinkat`, a
directory `fsync` and journal operations without a stated deadline or proved
maximum.

Remediate as follows:

1. inventory every potentially blocking operation in ACT, CP, IGR, CL,
   backstop and verification, including process waits, reads, hashing, metadata
   and extended-attribute inspection, writes, `fsync`, `unlinkat`, signal
   handling, kill and reap;
2. distinguish operations whose elapsed time is enforced by a monotonic
   deadline from operations that are merely expected to be quick;
3. do not infer a bound for filesystem or kernel work from a fixed arithmetic
   margin;
4. either give each claimed component a mechanically enforced deadline and a
   fail-closed consequence, or withdraw the elapsed-time claim and state exactly
   how `TimeoutStartSec=`, `TimeoutStopSec=`, `RuntimeMaxSec=` and the next
   recovery rung terminate or recover from the procedure;
5. account for the fact that terminating CL at `TimeoutStopSec=` may interrupt
   it before rule removal, after rule removal but before verification, or during
   evidence publication, and map every interruption point to a state and next
   recovery owner;
6. specify when the holder installs its signal handlers relative to AM-2, and
   ensure the design does not depend on an interruptible Python `finally` block
   completing within an unsupported elapsed-time bound;
7. handle a signal received during IGR itself, including re-entry or a second
   termination signal, with an idempotent, fail-closed state transition;
8. correct every affected formula, table, invariant, negative test, Appendix A
   amendment, Appendix B obligation and recommended parameter decision; and
9. retain the central PO-11(d′) rule: no Polkit reload-time bound is claimed and
   every operational timeout fails closed.

## Required cumulative R2 proposal

Create a self-contained cumulative R2 proposal. A reviewer must not need to
splice R1 prose into it. It must:

1. carry forward the repaired PO-20(f), PO-21(c), PO-21(s) and PO-11(d) design
   only after applying R2-F1 and R2-F2;
2. retain explicit fact classes and distinguish accepted evidence, proposed
   obligations, design choices and unresolved host facts;
3. include revised state machines, terminal-cause and interruption tables,
   authority windows, recovery ownership, evidence records, invariants and
   negative tests;
4. include a corrected executable/runtime boundary and complete Role A–H
   inventory;
5. include reproducible source, build, pinning, digest, ownership,
   installation, update, rollback and drift contracts without performing them;
6. include the byte-level PO-17/OH-S4p boundary and identify every claim needing
   independent security re-review;
7. include a complete MF-1 through MF-8 disposition and define any genuinely
   new missing fact rather than hiding it in a threat-model assertion;
8. include exact cumulative amendment tables for the one-host design and
   operational draft;
9. identify decisions Peter may make only after clean independent review and
   identify separately any material baseline change that requires §0.2 change
   control;
10. define successor order and gates without authorizing them; and
11. contain a remediation map showing where R2-F1 and R2-F2 are closed.

If literal Route 3 cannot be made decision-ready from repository evidence, the
cumulative document may still preserve the repaired activation design and exact
Route 3 alternatives, but its title, outcome and handback must clearly carry the
defined hard stop. Do not label a scope-change alternative as completion.

## Deliverables

Create:

1. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r2-remediation-proposal.md` — the
   self-contained cumulative R2 proposal or hard-stop alternatives record;
2. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r2-remediation-handback.md` — the
   complete durable handback.

Update only these current-state pointers:

- `docs/review/Handover information`;
- `docs/project-management/status.md`;
- §20 of `docs/implementation-plan.md`; and
- the restriction banner in `docs/operations/disposable-test-server.md`.

Do not edit R1, any accepted historical evidence, the operational draft,
source code, tests, configuration, service files, migrations, archive snapshots,
archive indexes, the decision register or the change log.

The handback must report prompt identity, terminal state, findings remediated,
files changed, exact repository documents consulted, commands and checks,
checks not run, security implications, unresolved decisions and proposed
independent-review focus. It must distinguish pre-existing worktree changes and
confirm no host, retained-evidence, secret, network, implementation, launcher,
build, test, cleanup, commit or push action.

Mark this R2 authority and prompt consumed in all four pointers. Do not claim
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
- scan the cumulative proposal for `R2-F1`, `R2-F2`, the accepted Route 3
  definition, every affected timing claim, MF-1 through MF-8 and every required
  successor gate;
- compare every carried obligation and identifier against R1 and the accepted
  OH-S2 R2 record using exact named-file searches;
- verify that no formula claims to bound a component described elsewhere as
  unbounded or merely expected to finish within a margin;
- verify that no occurrence of RT3-A or a renamed wrapper alternative is
  described as satisfying literal Route 3 absent an explicit prior §0.2 scope
  decision; and
- review the six-file diff for accidental host, implementation, successor,
  cleanup, credential, secret, commit or push authority.

Do not run application tests, hook tests, formatters, builds, package tools,
network checks or remote-host checks.

End the handback exactly with one of:

`OH-S3 R2 remediation awaits independent Codex re-review; no host, implementation, cleanup, OH-S4/OH-S4p or later slice is authorized.`

or:

`HARD STOP: concrete Route 3 not established; no host, implementation, cleanup, OH-S4/OH-S4p or later slice is authorized.`
