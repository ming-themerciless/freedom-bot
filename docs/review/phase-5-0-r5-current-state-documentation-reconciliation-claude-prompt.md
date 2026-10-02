# Claude prompt — R-5 current-state documentation reconciliation

Work ID: `C-P5.0-R5-DOC-R1`

Date: 2026-10-01

Assignee: Claude

Status: **authorized repository-documentation task; may run concurrently with Gemini R4**

## 1. Objective

Reconcile the repository's canonical current-state documentation with the
accepted R-5 sequence through Gemini's R3 acceptance and the now-active,
bounded R4 baseline-recovery assignment.

The canonical handover, status, implementation-plan immediate action and
disposable-server restriction still describe Gemini R2 as current. Update them
truthfully without changing any technical decision, accepting R-5, or granting
host authority.

This work is intentionally file-disjoint from Gemini's concurrent R4 task.

## 2. Concurrency and exclusive file ownership

Gemini R4 exclusively owns and may touch only:

* `infra/rp11-launch/verify/fixtures/cc1.v.baseline`, and only after an exact
  historical digest match; and
* `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r4-cc1-baseline-recovery-handback.md`.

Claude must not create, modify, delete, rename, stage or format either path.
Claude must also not modify any file below `infra/rp11-launch/` or `tests/`.

Claude exclusively owns the documentation files listed in §5 for this task.
If any unlisted file appears necessary, stop and report it instead of widening
scope. Re-check `git status` before every write batch and at handback. If a
concurrent change appears in a Claude-owned file after Claude's initial read,
stop and report the collision; do not overwrite or merge it.

## 3. Required context

Before editing, read:

1. `.agents/AGENTS.md` completely;
2. the implementation-plan reading map, §0, §13, §16, §17 and §20;
3. `docs/review/Handover information`;
4. `docs/operations/disposable-test-server.md`;
5. the R-5 assignment and stopped R-5 handback;
6. the R2 and R3 prompts and handbacks;
7. Codex's R3 review disposition as recorded in the accepted R3 decision;
8. `project-review-2026-10-01-p5-r5-rp11-r5-r3-acceptance.md`;
9. Gemini's active R4 baseline-recovery prompt; and
10. the current status, change-log, decision-register and relevant archive
    indexes.

Inspect `git status` first. The worktree contains accepted, uncommitted work;
preserve it exactly outside this task.

## 4. Required reconciliation

Update the canonical documents so they consistently state:

* R2 introduced the same-invocation R-1/R-2 gate and withdrew the erroneous
  R-5 pass;
* R3 removed the unsafe causal regex override, made byte equality the only
  route to `PASS`, and was independently reviewed and accepted by Peter;
* Codex reproduced 4,019 passing repository tests, with 12 toolchain-dependent
  skips because no accepted local root was available, plus clean compilation,
  byte-range checks and `git diff --check`;
* Gemini R4 is the current action and is limited to recovery of Claude's
  historical `cc1.v` bytes with exact SHA-256
  `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`;
* R4 does not authorize rebuilding, baseline reproduction, SSH, `oracle-test`,
  downloads, provisioning or an R-5 rerun;
* failure to recover the exact bytes requires a handback and stop;
* success authenticates only the historical artifact and does not itself
  explain Gemini's differing `cc1.v` or accept R-5; and
* R-5 remains stopped, Blocking and unaccepted; RP-11 remains unwired and
  unmet; `plan.is_executable=False`; Package 5.0 remains not ready.

Preserve historical facts as historical facts. Remove or supersede stale
current-action wording, but do not rewrite archived evidence.

Before replacing canonical handover, status, implementation-plan immediate-
action text, or the disposable-server restriction banner, preserve the
displaced state verbatim under the appropriate existing archive convention,
record its SHA-256 in the relevant archive index, and maintain navigation back
to the canonical file. Do not create an archive if the applicable governance
rule or existing index says one is unnecessary; explain that determination in
the handback.

Add a concise change-log and decision-register entry for the R3 acceptance and
R4 recovery authority. These entries summarize the accepted decision; they do
not create new authority.

## 5. Authorized files

Claude may edit only:

* `docs/review/Handover information`;
* one verbatim handover snapshot and
  `docs/review/handover-archive/README.md`;
* `docs/project-management/status.md`;
* one verbatim status snapshot and
  `docs/project-management/status-archive/README.md`;
* `docs/implementation-plan.md`, limited to §20 current-action text;
* one verbatim implementation-plan snapshot and
  `docs/implementation-plan-archive/README.md`;
* `docs/operations/disposable-test-server.md`, limited to its current
  restriction banner;
* one verbatim disposable-server snapshot and
  `docs/operations/disposable-test-server-archive/README.md`;
* `docs/project-management/change-log.md`;
* `docs/project-management/decision-register.md`; and
* the single handback named in §7.

Use snapshot names ending in `through-2026-10-01-r5-r3-acceptance` unless an
existing same-day naming convention requires a more precise collision-free
suffix.

Do not edit either the R3 acceptance record or the R4 prompt. They are inputs,
not outputs.

## 6. Verification and restrictions

Verify:

1. all added relative Markdown links resolve;
2. every snapshot is byte-for-byte equal to its canonical source as read
   before the corresponding edit;
3. each archive-index SHA-256 equals the snapshot bytes;
4. current-action and restriction searches find no surviving claim that R2 or
   R3 is the active assignment;
5. current documents do not imply R-5 acceptance or host authority;
6. documentation-focused structural tests affected by these files pass; and
7. `git diff --check` is clean.

No source code, test code, launcher artifact, fixture, generated evidence
manifest, external host, SSH, synchronization, package operation, download,
provisioning, service, database, build, test-server run, harness `--execute`,
secrets scan, commit or push is authorized. Repository-local read-only commands
and documentation-focused tests are allowed.

Do not touch Gemini-owned files even if Gemini finishes while Claude is still
working. Do not incorporate an R4 result into this task; that result requires
separate independent review.

## 7. Required handback and stop gate

Write:

`docs/review/phase-5-0-r5-current-state-documentation-reconciliation-handback.md`

Include:

* files changed and before/after SHA-256;
* archive snapshot equality and indexed hashes;
* the precise current-state statements reconciled;
* link and structural-test results;
* concurrency checks and confirmation that Gemini-owned paths were untouched;
* checks not run and why;
* security, configuration, deployment and rollback implications; and
* proposed independent-review focus.

Stop after the handback. Do not review or act on Gemini's R4 result, authorize
an R-5 rerun, or advance another package.
