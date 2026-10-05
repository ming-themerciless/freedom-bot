# Independent review — `oracle-test` one-host H-1 design amendment

Date: 2026-10-04  
Reviewer: Codex  
Design author: Claude  
Work ID: `C-P5.0-R5-RP11-H1-D3`

Reviewed return:
[`phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md`](phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md).

## Outcome

Claude's terminal state **BLOCKED DESIGN** is valid. The proposal correctly
identifies that the one-host topology changes evidence and authority semantics
that Claude was not authorized to choose. In particular, OH-D-1 through
OH-D-9 require maintainer decisions before a complete amendment can be
accepted.

The proposed H-1 portion is **not yet decision-ready**, however. I find two
Blocking design defects in its mutation/recovery contract. They do not make
the BLOCKED DESIGN return invalid; they mean Peter should not accept the
proposal's statement that H-1 itself is fully specified, and should not decide
the nine OH-D items as if they were the only remaining design work.

No Important or Optional finding is raised separately. No design, decision,
host action or implementation is accepted or activated by this review.

## Findings

### Blocking OH-H1-D3-1 — the publication journal cannot recover every published final path

The file-publication sequence creates the final name with `link(T, P)` and
only afterwards appends `created P dev ino sha256` to the journal (§4.2.4,
steps 5–6). A process exit, host failure or write/fsync failure in that window
leaves a complete root-owned final path at `P` without the journal line that
Guard G requires before removing it (§4.6.2).

The result is a reachable ST-0.x state that RB-1 must leave in place. A future
H-1 then refuses because the path already exists. This contradicts the claims
that rollback is defined for every mutation state and that the H-1
installation portion is fully specified. The proposal itself names this
crash window as a review focus, but does not close it.

Required remediation: define a crash-consistent intent/commit/recovery
protocol that can attribute and digest-guard the final link even if execution
stops immediately after the namespace mutation. It must cover file and
directory publication, journal durability and directory durability, and must
prove that recovery never removes an unrelated pre-existing path. The
remediation must also state the exact terminal state and successor authority
when recovery cannot establish ownership.

### Blocking OH-H1-D3-2 — `ACT`/`DEACT` lacks the publication, record and partial-failure contract needed for U-8

`ACT` says only to "publish" `pass-a.json`, then the live Polkit rule, then an
activation record (§4.2.5). It does not define an activation run identifier,
journal, atomic publication algorithm, activation-record schema or digest,
or a Guard-G binding for those files. Nevertheless §4.6.2 relies on Guard G
to remove the rule after an ACT HARD STOP.

This is most serious at the authority boundary: failure after the active rule
is linked but before its creation is durably attributable can leave the usable
Polkit grant standing, while the proposed automatic cleanup is unable to pass
its own removal guard. Failure after publishing `pass-a.json` but before the
rule also has no complete rollback path: the table explicitly leaves removal
for separate authority, so ST-1 is not restored. `DEACT` is described as
"digest-guarded" without defining the digest source or how it binds to this
activation. The proposal therefore does not yet satisfy U-8 or the
assignment's demand for partial-failure and rollback rules for every mutation
state.

Required remediation: specify `ACT` and `DEACT` to the same mechanical level
as H-1, including deterministic activation identity and record bytes,
pre-existing-path refusal, crash-consistent journal/namespace ordering,
digest and inode bindings, every partial state, automatic emergency removal
of the live rule under the accepted authority, disposition of `pass-a.json`,
and the evidence retained after cleanup. This remediation depends on Peter's
OH-D-7 and OH-D-8 decisions but cannot be replaced by them.

## What held

Subject to the findings and the still-open decisions, the proposal does useful
and largely complete work:

* it identifies the controller/target assumptions invalidated by one-host
  execution rather than merely substituting a hostname;
* it keeps the production server mechanically outside the proposed workflow;
* it separates staged H-1 state from the later Polkit activation in the right
  direction for U-8;
* it defines a bounded H-0 fact set, version-first citation order, local pinned
  rebuild, H-1/H-2 record direction and successor slices; and
* it preserves the distinctions between D9-3 and package RAID item
  `P5.0-R5`, and between static-launcher H-1/R-5 and similarly named records.

I did not find evidence that Claude crossed the active restriction. Its
reported repository-only work is consistent with the returned artifact and
the current worktree.

## Required next decision and successor

Peter should accept the BLOCKED DESIGN terminal state, keep the proposal
inactive, and decide whether to authorize a repository-only Claude remediation
that:

1. closes OH-H1-D3-1 and OH-H1-D3-2;
2. preserves OH-D-1 through OH-D-9 as undecided choices unless Peter decides
   them first; and
3. returns a revised, still-inactive design for independent re-review.

The smallest safe order is:

1. Peter decides OH-D-7 and OH-D-8, because the activation recovery contract
   depends on them;
2. Claude performs the bounded design remediation; and
3. Codex independently re-reviews the revised proposal before Peter accepts
   any H-1 design or activates H-0, implementation, build, installation or
   evidence work.

OH-D-1 through OH-D-6 and OH-D-9 may be decided in the same record, but no
host step is released by doing so. If Peter does not decide OH-D-7/OH-D-8,
the remediation must return BLOCKED DESIGN again rather than choosing them.

## Checks and authority boundary

I read the canonical working agreement, the implementation plan's required
and relevant sections, the active Handover, the disposable-server restriction,
the design authority and task, the complete returned proposal, and the
relevant C11/D2 and H-1-preparation records. I inspected `git status` and
preserved all pre-existing changes.

No SSH, `rsync`, host inspection, retained-path inspection, upstream research,
implementation, build, installation, privilege, service/database action,
H-0/H-1/H-2, evidence pass, cleanup, test suite, commit or push was performed.
The checks were documentation review only; tests are inapplicable to this
review and prohibited host checks remain unrun.

D9-2 and D9-3 remain Complete. D9-1, D9-4, PO-9, PO-14, PO-17, PO-18 and H-1
remain open. RP-11 remains unwired and unmet; package RAID item `P5.0-R5`
remains Blocking; `plan.is_executable=False`; Package 5.0 remains not ready.
