# Claude prompt — R5 H-0 completeness and host-contract remediation

Status: **authorized by Peter Duscha on 2026-10-06**

Proposed work ID:
`C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R5-DR1-20261006-03`

## Start instruction

Start Claude Code in `/opt/freedom-blades/platform`, then paste:

```text
Execute the authorized repository-only remediation assignment in docs/review/phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-remediation-claude-prompt.md. Work autonomously within its documentation-only boundary. Produce the decision-ready remediation proposal and complete durable handback, update the authorized current-state pointers, then stop for independent Codex review. Do not access oracle-test or any retained evidence path.
```

## Purpose and terminal boundary

Prepare a repository-only, decision-ready remediation for the independent R5
review. The result must resolve the specification gaps that made the reported
`H-0 PASS` incomplete and reconcile the accepted design with the observed
CPython 3.14 host. It must not collect new host facts or claim that H-0 passed.

Peter Duscha authorizes this exact repository-only assignment under the work ID
above. Its authority record is
`docs/review/project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-authority.md`.

This assignment ends after the documentation proposal and handback are written.
It does not authorize OH-S2, another H-0 run, implementation, installation,
testing on `oracle-test`, H-1/H-2, activation, cleanup, commit or push.

## Required reading

Read completely before editing:

1. `.agents/AGENTS.md`;
2. the reading map, §0, §16 and §20 of `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. the restriction banner in `docs/operations/disposable-test-server.md`;
5. `docs/review/project-review-2026-10-06-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-incomplete.md`;
6. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-handback.md`, through the end of **Checks not run**; do not re-parse or rewrite its appendices unless needed to verify a cited retained value;
7. the accepted one-host proposal's §4.1.1–§4.1.5, §4.2.3, §4.4.1,
   §4.4.2b, §4.7.4 and cumulative D3-R1 through D3-R6 amendments; and
8. the R5 authority and prompt, for scope history only.

Inspect `git status` and preserve all unrelated and pre-existing changes.

## Authorized scope

Repository documentation only. You may:

- create one remediation proposal under `docs/review/`;
- create one complete handback under `docs/review/`;
- update the concise current-state links in `docs/review/Handover information`,
  `docs/project-management/status.md` and implementation-plan §20 to record
  the terminal remediation state and durable handback; and
- use local, read-only Git and filesystem commands to inspect the repository.

No network access is authorized. Do not SSH to `oracle-test`; do not inspect,
copy, hash, list, repair, retry or clean up any `/var/tmp/p5-r5-rp11-*` path;
do not inspect the fixed checkout on `oracle-test`; and do not read secrets,
credentials, SSH configuration or application/player data.

## Required remediation

Produce a cumulative amendment proposal that addresses every item below without
silently changing an accepted decision.

### 1. HF-15 and `MI.capture_root_A`

- Identify every accepted constraint on `MI.capture_root_A`, including the
  exclusions in §4.1.5.
- Recommend one exact capture-root template and one exact parent directory on
  `oracle-test`. Do not use `/tmp`, `/var/tmp`, the repository, either excluded
  `/var/lib` subtree, or an RP-11 installation/record path.
- Prefer a parent whose filesystem facts R5 already collected if that is
  compatible with every accepted constraint. Cite the exact R5 command IDs.
- State clearly whether binding the maintainer input to the recommended parent
  makes existing R5 HF-15 evidence complete or whether a narrowly scoped
  successor observation is still required. Do not call the binding accepted;
  present it as a Peter Duscha decision unless an authority accompanying this
  prompt already records that decision.
- Amend the future H-0 contract so the capture-root parent is a fixed input
  before execution and absence of that input is a pre-execution `HARD STOP`,
  never a fact recorded as `not specified` at `H-0 PASS`.

### 2. HF-18 and the interactive client

- Trace OH-D-2, IA-10, TR-0 through TR-3, the hook boundary and HF-18.
- Determine whether a specific interactive-client executable is load-bearing.
- If it is load-bearing, propose the exact path-selection decision and require
  that exact path as a fixed input to any successor fact collection. Do not
  guess a host path or infer presence from controller-side state.
- If it is not load-bearing, propose a precise amendment removing HF-18 and
  explain why this does not weaken the hook grammar, local-only topology,
  authorization boundary or trusted-path argument.
- Present materially different alternatives and a recommendation for Peter.
  Until Peter decides, retain HF-18 as incomplete.
- Amend the future H-0 contract so a required client path missing from the
  assignment causes a pre-execution `HARD STOP`.

### 3. CPython 3.12 versus 3.14

- Enumerate every normative `/usr/bin/python3.12`, Python 3.12 package and
  version-bound reference affected across the cumulative accepted design,
  including TR-9, unit/activation literals, HF-06 through HF-10, PO-12,
  PO-19, command catalogues, records, schemas, tests and successor slices.
- Use R5 only for the observed facts: `/usr/bin/python3.12` and its named
  packages are absent; `/usr/bin/python3` resolves to `/usr/bin/python3.14`;
  the executable is CPython 3.14.4 with the recorded owner, mode, digest,
  package ownership and isolated/no-site flags.
- Compare at least these decision routes:
  1. revise the design to the exact `/usr/bin/python3.14` executable and redo
     every version-bound citation and test;
  2. require a separately authorized installation of Python 3.12, without
     performing or presupposing it; and
  3. abandon the Python-dependent route if neither can satisfy the proof
     obligations.
- Recommend one route, with security, reproducibility, package-drift,
  operational and review consequences. Do not use unversioned
  `/usr/bin/python3` in an installed or privileged contract.
- Make clear that changing `3.12` to `3.14` textually does not discharge
  PO-12, PO-19 or any other version-bound obligation; those return to OH-S2
  citation and independent review.

### 4. Polkit unknown and PO-21(i)

- Preserve R5's `unreadable` result for `/etc/polkit-1/rules.d` and the
  unknown presence of `50-freedom-blades-rp11.rules`.
- Specify the earliest later gate that must establish the collision/absence
  fact under separate privilege authority. No proposal may infer absence.
- Trace PO-21(i)'s required condition paths. Either enumerate them from an
  already accepted local source or state exactly which OH-S2 citation/design
  result must name them before a host check can run.
- Define fail-closed behavior: absent path definitions cannot be reported as a
  successful HF-20 observation or used to release AP-0.

### 5. R5 evidence composition and successor shape

- Preserve R5's accepted facts and evidence digests without rewriting its
  handback or independent review.
- Give a fact-by-fact disposition: accepted from R5, incomplete, invalidated by
  a later design decision, or requiring a fresh observation.
- Propose the smallest successor shape. Prefer a narrow, separately authorized
  gap collection that composes explicitly with R5 if this is sound; otherwise
  explain why a full fresh H-0 is necessary.
- Any proposed successor must use a fresh work ID and exclusive evidence path,
  must not reuse or inspect R5's retained remote paths, and must end fail-closed
  on a missing fixed input. Do not create an authority record or mark the
  successor authorized.

## Deliverables

Write:

1. a cumulative remediation proposal at
   `docs/review/phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-proposal.md`;
2. a complete handback at
   `docs/review/phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-handback.md`.

The proposal must include:

- a finding-to-change traceability table;
- an explicit decision table with recommendation, decision owner and effect;
- exact proposed amendments, not merely commentary;
- a complete inventory of affected Python 3.12 references grouped by semantic
  role rather than a blind global replacement;
- the R5 fact disposition and evidence-composition table;
- successor entry/exit criteria and prohibitions;
- unresolved decisions and the exact independent-review questions; and
- a statement that no accepted baseline, authority or gate changes until Peter
  decides and Codex re-reviews the resulting amendment.

The handback must report requirements addressed, files changed, commands and
checks run with exact results, checks not run, security implications, remaining
decisions and reviewer focus. Report pre-existing worktree changes separately.

## Verification

Run only local documentation checks appropriate to the edits:

- `git diff --check`;
- link/path existence checks for every repository-relative link you add;
- targeted searches proving all normative Python 3.12 occurrences were
  inventoried and that no accidental blanket replacement occurred; and
- a diff review for accidental authority language, remote-operation language,
  secrets, player data and changes outside the authorized documentation scope.

Do not run application tests: this assignment changes documentation only.

End the handback exactly:

`Remediation awaits independent Codex review and Peter's recorded decisions; no H-0 successor, OH-S2 or later slice is authorized.`
