# Claude prompt — R5 H-0 remediation decisions and disposable-host lifecycle

Status: **authorized by Peter Duscha on 2026-10-06**

Work ID:
`C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R5-DR2-20261006-04`

## Start instruction

Start Claude Code in `/opt/freedom-blades/platform`, then paste:

```text
Execute the authorized repository-only assignment in docs/review/phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r2-claude-prompt.md. Apply Peter's recorded D-1 through D-7 decisions, correct the HF-15 defect identified by independent review, specify the bounded disposable-Test cleanup and workspace-recreation lifecycle, produce the cumulative R2 proposal and complete handback, update only the authorized current-state pointers, and stop for independent Codex review. Do not access oracle-test, any retained evidence path, credentials, or secrets; do not perform cleanup or any other host mutation.
```

## Authority and terminal boundary

Peter Duscha, Product Owner and Acceptance Authority, authorizes this exact
repository-only documentation assignment. Its authority record is
[`project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-r2-authority.md`](project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-r2-authority.md).

This assignment records Peter's decisions, repairs the proposal, and designs
the later cleanup/recreation sequence. It does **not** authorize network or
`oracle-test` access, retained-evidence access, cleanup, deletion, checkout
creation, credential access, privilege, installation, build, test execution,
service/database mutation, H-0G, OH-S2, H-1/H-2, activation, rollback, commit
or push. It ends after the documentation and handback are returned for
independent Codex review.

## Required reading

Read completely before editing:

1. `.agents/AGENTS.md`;
2. the reading map and §§0, 16, 17 and 20 of `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. the restriction banner and relevant cleanup/workspace provisions in
   `docs/operations/disposable-test-server.md`;
5. the complete DR1 proposal and handback:
   - `docs/review/phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-proposal.md`;
   - `docs/review/phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-handback.md`;
6. DR1's authority and consumed Claude prompt;
7. the R3 hard-stop review, R5 prompt, R5 handback through “Checks not run”,
   and R5 independent review; and
8. the accepted one-host proposal sections and amendments cited by DR1 for
   HF-03, HF-15, HF-18, IA-12, repository placement, source-consuming slices,
   retention and cleanup.

Inspect `git status` first. Preserve every unrelated or pre-existing change.
Do not inspect any remote host or retained remote path.

## Decisions to record and apply

Peter has made the following decisions. They are no longer alternatives for
this assignment, but their prerequisites and later independent-review gates
remain in force.

1. **D-1:** use capture parent `/var/lib/rp11-capture`, `ubuntu:ubuntu`, mode
   `0700`, not a mount point and without a POSIX ACL extended attribute; use
   `/var/lib/rp11-capture/<activation_id>-pass-a` with the exact accepted
   activation-ID grammar.
2. **D-1b:** create the parent only through the separately authorized CPP
   provisioning act after H-1 PASS and before the first A-2.
3. **D-1c:** complete HF-15 by direct H-0G observation, not by accepting the
   DR1 ancestor inference alone.
4. **D-2:** withdraw HF-18 from H-0. Each later assignment that actually runs
   an agent client on `oracle-test` must name and verify that exact executable
   in its own fail-closed preflight. Human-shell assignments name no client
   and record the accepted no-hook case.
5. **D-3:** use Route 1, exact `/usr/bin/python3.14`. Preserve every DR1
   re-citation, rebuild, test, digest, manifest, U-9 restatement and independent
   review consequence; textual replacement alone discharges nothing.
6. **D-3b:** enforce the proposed version- and digest-equality gates. A package
   hold may later be separately considered but is not a substitute and is not
   authorized here.
7. **D-4:** add P-0p at H-1 before mutation and retain the AM-0 root re-check.
   `unreadable` is never absence.
8. **D-5:** split HF-20; CL-21i is an OH-S2 result and AP-0/AM-0 fail closed
   until its closed condition list is accepted.
9. **D-6:** use narrow H-0G composition with R5. Any changed composition
   anchor requires a full fresh H-0 under separate authority.
10. **D-7:** `/opt/freedom-blades/platform` remains the normal Test workspace,
    but is not an RP-11 evidence or execution source while its state is
    uncontrolled. Preserve it untouched until a later cleanup authority.
    Every RP-11 assignment that consumes repository source must instead create
    or receive a fresh, exclusive, anonymously retrieved checkout at an exact
    run-specific path, pinned to the accepted commit. Before use, that slice
    verifies the path, exact commit, clean detached state, ownership, modes,
    absence of remotes/credential-bearing configuration and the applicable
    accepted governing-file digests. Missing or nonconforming state is a
    `HARD STOP`. A retained checkout is evidence only and is never reused.
    Repository ownership therefore leaves HF-03/H-0 and becomes a per-source-
    consuming-slice preflight. H-0G remains repository-free.

## Required remediation

### 1. Correct HF-15

Independent review found DR1's H-0G command set impossible as written: GNU
`df` does not inspect a nonexistent target by resolving it to the nearest
existing ancestor.

Amend every affected HF-15 and H-0G passage so the procedure:

1. applies `lstat` and `listxattr` handling to
   `/var/lib/rp11-capture`, with `ENOENT` the expected pre-CPP result;
2. determines and records the nearest existing ancestor without searching
   unrelated paths; for this decided binding that ancestor is exactly
   `/var/lib` while the parent is absent;
3. runs `findmnt --target /var/lib` and `df --output ... /var/lib` explicitly,
   never those commands against the absent path;
4. records that these are ancestor filesystem facts rather than pretending
   they are a successful stat of the absent parent; and
5. requires CPP's later fail-closed preflight/postcondition to prove the new
   parent is a non-mount directory on that same filesystem.

Ensure the H-0G exit contract can actually pass on the expected `ENOENT` state.

### 2. Apply D-7 completely

Trace and amend HF-03, U-3, IA-12, §4.1.4 repository placement, FI-1, the R5
fact-disposition table, H-0G, OH-S3/OH-S4p/OH-S5 and every later slice that
reads repository bytes. Distinguish three objects precisely:

- the normal Test workspace `/opt/freedom-blades/platform`;
- a fresh run-specific pinned RP-11 checkout; and
- retained checkout/evidence paths, which are immutable evidence and never
  execution inputs.

Do not claim R5 observed checkout ownership: its inventory covers its evidence
directory, and its handback explicitly says repository ownership was not
observed. Do not infer ownership merely because `ubuntu` created a checkout.

Define a bounded ownership/mode inventory for each fresh checkout before its
first use. It must reject symlink substitution at the checkout root, an
unexpected owner/group, group- or world-writable repository content, a dirty
or non-detached tree, a commit mismatch, remotes, credential/helper settings,
active hooks, submodule recursion, replacement objects, or other state that
would defeat the accepted anonymous pinned-source contract. Reuse the accepted
R5 controls where applicable; do not silently invent a weaker Git contract.

H-0G performs no retrieval and touches no repository path. Source-consuming
slices need their own exact checkout path, work ID, authority, freshness check,
retention record and later cleanup disposition.

### 3. Specify the disposable-Test lifecycle

Record Peter's approved policy:

- Test is disposable; obsolete workspaces, run-specific checkouts and retained
  evidence should not accumulate indefinitely.
- No current object is deleted merely because this policy is recorded.
- R1–R5 retained paths and the current normal workspace remain untouched until
  the cumulative remediation is independently accepted and every evidence
  dependency is either closed or explicitly abandoned by Peter.
- After that gate, a separately authorized bounded cleanup may remove only an
  exact enumerated path list whose identity, retention disposition and
  non-dependency have been reviewed. No glob, recursive broad root, discovery-
  and-delete loop, or inferred path is acceptable.
- Cleanup must not target `/`, `/var/tmp`, `/opt`, `/opt/freedom-blades`, a
  workspace root by implication, credentials, application/player data, or an
  unreviewed path. Each target is checked against the approved literal list
  immediately before deletion; a mismatch is a hard stop.
- After accepted cleanup, recreate `/opt/freedom-blades/platform` as the normal
  clean Test workspace through a separately authorized synchronization or
  anonymous pinned-retrieval assignment. Verify its identity, ownership,
  expected branch/commit policy and clean status before ordinary test use.
- The normal workspace may be used for ordinary disposable-server testing but
  is not substituted for a fresh RP-11 checkout when independent pinned
  provenance is required.
- Every future run-specific checkout/evidence path receives an explicit
  retention disposition at its review gate and a later exact-path cleanup
  authority when no longer needed.

Design the sequence and its gates; do not write an executable cleanup command,
do not create cleanup authority, and do not perform cleanup. Identify which
accepted review must close before a cleanup prompt can safely enumerate its
targets.

### 4. Preserve all DR1 remediation

Carry forward the complete, corrected substance of DR1: D-1 through D-6,
Python Role A–H inventory, Polkit P-0p/AM-0, HF-20/CL-21i, FI-1 through FI-5,
R5 fact disposition, composition anchors, successor gates, and the prohibition
against treating a proposal or decision as execution authority.

## Deliverables

Create:

1. `docs/review/phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r2-proposal.md` — a self-contained cumulative proposal that supersedes DR1 if accepted;
2. `docs/review/phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r2-handback.md` — the complete durable handback.

Do not rewrite the consumed DR1 proposal, handback, prompt or authority.

Update only these concise current-state pointers:

- `docs/review/Handover information`;
- `docs/project-management/status.md`; and
- §20 of `docs/implementation-plan.md`.

The proposal must include decision traceability, exact normative amendments,
the corrected H-0G command semantics, the D-7 slice matrix, the Test cleanup
and recreation gates, the complete R5 composition table, remaining
prerequisites, and focused questions for independent Codex review.

The handback must distinguish pre-existing worktree changes; list files
changed, commands/checks and exact outcomes; report checks not run; confirm no
host or retained-path access; and identify the next review gate.

## Verification

Run only local documentation checks:

- `git diff --check`;
- repository-relative link target checks;
- targeted searches showing every DR1 decision and D-7 reference was carried
  forward consistently;
- a targeted scan proving no H-0G `df`/`findmnt` command uses the absent parent;
- a scope review for accidental execution authority, cleanup commands,
  secrets, player data, network access, commit or push language.

Do not run application tests, formatters, builds or remote checks.

End the handback exactly:

`R2 remediation awaits independent Codex review; no host cleanup, H-0G, OH-S2 or later slice is authorized.`
