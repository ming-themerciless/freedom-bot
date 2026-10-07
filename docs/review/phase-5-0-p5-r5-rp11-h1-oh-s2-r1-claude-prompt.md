# Claude prompt — execute OH-S2 R1 version-bound citation work

Work ID: `C-P5.0-R5-RP11-H1-OH-S2-R1-20261006-07`

Date: 2026-10-06

Executor: Claude Code on the production workspace controller

## Objective and terminal boundary

Produce the repository-only OH-S2 citation record required by the accepted
one-host design and cumulative R3 amendment. Research the named authoritative
upstream sources read-only, bind every conclusion to the accepted H-0
versions, and return a decision-ready proposal and durable handback for
independent Codex review.

Run PO-14 first. If PO-14 is refuted or cannot be established, stop at
`HARD STOP: PO-14 not established`, record the precise reason and sources,
update the current-state pointers, and do not begin the remaining obligations.
Otherwise complete all authorized items and stop at
`OH-S2 CITATIONS READY FOR REVIEW`. Do not accept your own conclusions or
authorize a successor slice.

Create:

- `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s2-r1-citations.md`;
- `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s2-r1-handback.md`.

## Required reading

Before research or edits, read completely:

1. `.agents/AGENTS.md`;
2. `docs/implementation-plan.md` reading map, §0, §14, §16, §17 and §20;
3. `docs/review/Handover information`;
4. the restriction banner in `docs/operations/disposable-test-server.md`;
5. the accepted one-host design, especially §§4.2–4.4 and §4.7.4;
6. cumulative R3 §§6–7, §10, §13–14 and its acceptance;
7. the composed H-0 review and Peter's acceptance/U-9 restatement;
8. the R5 and H-0G handbacks only as durable repository evidence.

Inspect `git status` and preserve all pre-existing changes. Verify this
prompt's exact byte count and SHA-256 against its authority before research or
editing. A mismatch is `HARD STOP: prompt identity mismatch`.

## Fixed version and identity inputs

Bind conclusions to these accepted H-0 facts:

- kernel: `7.0.0-31-generic`, x86_64;
- systemd: `259.5-0ubuntu3.4`;
- polkitd: `127-2ubuntu1.1`;
- libc6/glibc package: `2.43-2ubuntu2.4`;
- `python3.14-minimal`: `3.14.4-1ubuntu0.2`;
- exact interpreter: `/usr/bin/python3.14`;
- interpreter SHA-256:
  `be9a2a5eada8c89c1c399fdfb8397179e877c20d8db0739c802f726d4d0e69fd`;
- interpreter dynamic-section facts must come from the accepted R5/H-0G
  evidence where present; if `DT_RUNPATH`/`DT_RPATH` was not actually recorded,
  mark that fact unestablished and assign its mechanical observation to the
  appropriate later gated slice. Do not infer it from another binary.

A missing or contradictory fixed input is a local fail-closed stop. Do not
inspect a host to fill it.

## Authorized sources and research method

Use only primary, authoritative sources:

- the exact Ubuntu source packages and patches corresponding to the installed
  package versions, from official Ubuntu archive/Launchpad sources;
- upstream systemd source and documentation for the matching 259 series;
- upstream Linux kernel source/documentation for the matching 7.0 series;
- upstream glibc 2.43 source and manuals, reconciled with Ubuntu's exact
  `2.43-2ubuntu2.4` source-package patches;
- upstream CPython 3.14.4 source and documentation, reconciled with Ubuntu's
  exact `3.14.4-1ubuntu0.2` source-package patches;
- upstream polkit 127 source/documentation plus the exact Ubuntu package
  patches where PO-11 requires them.

Network access is authorized only for this read-only upstream-source and
documentation research. Record every source URL, tag/version, relevant file
and line/range or section, retrieval date, and—where bytes are downloaded—the
SHA-256. Do not rely on search-result snippets, blogs, Q&A sites, generated AI
summaries, another distribution's behavior or an unversioned `main` branch.
Short quotations must respect copyright limits; prefer precise paraphrase.

Do not execute downloaded code, install packages, update package indexes, or
use upstream build/test systems. Static reading and local text/hash processing
of downloaded public source are allowed only in a fresh temporary directory
under `/tmp`; delete that temporary directory at the end and record the
disposition. Repository deliverables must contain the durable citations and
reasoning, not downloaded source archives.

## Ordered obligations

### 1. PO-14 first — load-bearing stop gate

Evaluate PO-14 and AD-7 for systemd `259.5-0ubuntu3.4`, including the exact
execution-environment provenance asserted by TR-7/LB-2S. State each premise,
source and conclusion separately. If any required premise is false,
unsupported for this version, or changed by an Ubuntu patch, stop immediately
as specified above. A plausible inference is not establishment.

### 2. Remaining systemd and Polkit obligations

Only after PO-14 is established, evaluate:

- PO-15, including the complete version-bound unit and manager property lists,
  `ExecStartPre` printed form and prefix/flag semantics;
- PO-8, S-1 through S-10;
- PO-11 (b) through (g), including the distribution-rule and rules-search-path
  claims;
- PO-20, including (g) and (h);
- every applicable PO-21 limb through (v), including D3-R4 and D3-R5 additions;
- **CL-21i**: give the closed list of automatic soft-reboot condition paths
  and non-path conditions for this systemd version. For every entry state the
  absolute path, predicate, whether `ubuntu` can observe it unprivileged, and
  how it is disarmed. If this version cannot automatically soft-reboot, state
  that with evidence and return an explicit empty list.

Any refuted PO-20, PO-11(d), PO-11(g), or PO-21 item returns the activation
design to review. Report that terminal disposition; do not smooth it into a
qualified pass.

### 3. CPython 3.14 obligations

Evaluate PO-12 and AS-8 for CPython 3.14.4 at the exact path with `-I -S`,
including startup path calculation and every environment/configuration input
the claims exclude or retain. Evaluate PT-8: whether Python 3.14's `os` module
exposes `renameat2` and `RENAME_NOREPLACE`; retain the reviewed `ctypes`
mechanism unless primary sources establish both required APIs.

A refuted PO-12 returns Route 1 to Route 3 design review.

### 4. U-9 / PO-19

Apply Peter's accepted U-9 wording to `/usr/bin/python3.14`. Evaluate PO-19
(a) through (d) for glibc 2.43 as patched by Ubuntu, covering:

- the executable's `DT_RUNPATH`/`DT_RPATH` as an explicit fact dependency;
- `/etc/ld.so.preload`, `/etc/ld.so.cache`, built-in trusted directories and
  `glibc-hwcaps`;
- why `INVOCATION_ID`, `LC_ALL` and `PATH` are or are not loader/tunable
  inputs, including `LD_*` and `GLIBC_TUNABLES`;
- `LC_ALL=C`, locale archive behavior and any possible `gconv` module loads;
- the boundary between source-established behavior and H-0 host facts.

Bind the accepted citation to libc6 `2.43-2ubuntu2.4`, Python package
`3.14.4-1ubuntu0.2`, the exact interpreter digest above, and the established
dynamic-section facts. Any drift requires re-citation before H-1. A refuted
PO-19 returns Route 1 to Route 3 design review.

### 5. Kernel and binfmt obligations

Evaluate D9-1 for Linux 7.0, including AD-3, AD-4, AD-6, AD-8, AD-11, AD-12,
the unmounted `binfmt_misc` case and entry grammar. Establish the
version-bound rules needed by the PO-17 mechanical matcher.

Do **not** claim PO-17 has passed against a new launcher image: OH-S4p creates
that image. Record precisely which source-bound PO-17 premises OH-S2
establishes and the later byte-level inputs/checks OH-S4p must supply.

## Deliverable requirements

The citation record must contain:

- a requirement-by-requirement verdict: `established`, `refuted`, or
  `not established`—never a vague partial pass;
- a traceability table from every obligation above to primary sources and
  exact accepted H-0 inputs;
- explicit separation of source facts, durable H-0 facts, mechanical facts
  still missing, and reasoned conclusions;
- the complete property lists and CL-21i result in machine-transcribable
  tables suitable for later implementation;
- U-9's exact accepted wording and its drift/re-citation gate;
- the PO-17/OH-S4p boundary;
- contradictions, patch uncertainty and every item returned to design review;
- no silent amendment of historical or accepted records.

The handback must report files changed, sources consulted, commands/checks and
exact results, checks not run, security implications, unresolved questions,
and proposed reviewer focus. Run a repository-relative link check and
`git diff --check`.

Update only the four current-state pointers:

- `docs/review/Handover information`;
- `docs/project-management/status.md`;
- §20 of `docs/implementation-plan.md`; and
- the restriction banner in `docs/operations/disposable-test-server.md`.

Mark the authority and prompt consumed. Do not claim Codex or Peter acceptance.

## Absolute prohibitions

No SSH or other host connection; no `oracle-test`, production, staging,
Foundry or database access; no retained-evidence-path access; no secret,
credential or player-data access; no package operation, build, executable
download/run, application test, service mutation, cleanup, workspace
recreation, implementation edit, launcher retarget/rebuild, OH-S3/OH-S4p or
later slice, H-1/H-2, activation, rollback, commit or push.
