# Claude prompt — remediate C-P5.0-R5-OP1-R1 capture durability

Prompt ID: `C-P5.0-R5-OP1-R2`

Date: 2026-09-27

State: **assigned; repository-only; no operational authority**

## 1. Assignment

Claude, remediate the one Blocking finding in the Codex independent re-review:

`docs/review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r1.md`

Read that review completely before editing. Also read, in the order required
by the repository entry point:

1. `.agents/AGENTS.md` completely;
2. `docs/implementation-plan.md` using its reading map, including §§0, 16 and
   20, Package 5.0 and its acceptance criteria, and §§13–14 because this task
   concerns evidence durability and operations;
3. `docs/review/Handover information`;
4. the first restriction banner and relevant contract in
   `docs/operations/disposable-test-server.md`;
5. the exact amended authorization draft identified in the Codex re-review;
6. the C-P5.0-R5-OP1-R1 remediation handback and its assignment; and
7. the original Codex review, so the resolved findings are not regressed.

The R1 re-review is the controlling defect list for this remediation. The
governing documents and MD-1 through MD-6 remain authoritative where it does
not speak.

## 2. Deliverables

Produce exactly these documentation results:

1. Amend
   `docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`
   in place. Keep it visibly **draft, unaccepted and unauthorized**.
2. Create
   `docs/review/phase-5-0-p5-r5-operational-evidence-prompt-r2-durability-remediation-handback.md`
   with the exact changes, unresolved prerequisites, validation performed,
   files changed, checks not run and final Git status relevant to the task.
3. Update `docs/review/Handover information`,
   `docs/project-management/status.md`, implementation-plan §20 and the first
   disposable-server restriction banner only when returning the completed
   remediation, so they point to the amended draft, this assignment, the new
   handback and the required Codex review.

Do not rewrite either Codex review, the original drafting handback, the R1
remediation assignment or the R1 remediation handback. They are durable
records of earlier bytes and dispositions.

## 3. Required correction — OP1-R1-1

Amend RP-11, §9.5 and every dependent statement necessary for internal
consistency so the future capture mechanism has a complete crash-consistent
publication contract.

### 3.1 Stream files

- Require stdout and stderr to be captured completely and closed to further
  writing before publication.
- Require each completed stream file to be flushed and successfully
  synchronized to stable storage before its SHA-256 is published in the
  per-act record.
- State that a failure to complete or synchronize either stream is an
  `inconclusive` act and consumes the pass under C-10 and §11.2.
- Preserve the existing maximum-size, separate-stream, retention, ownership,
  mode and redaction requirements.

### 3.2 Per-act records and directory entries

- Define the ordering: durable stream files first; then a complete record in a
  temporary name; then successful record-file synchronization; then atomic
  publication by rename; then successful synchronization of the containing
  directory before the next act begins.
- Require the record to bind the exact digests and names of the already-durable
  stream files.
- Treat failure of the record-file or directory-entry durability barrier as an
  `inconclusive` stop. Do not permit rewriting, repairing or reissuing the act.
- Do not weaken the rule that published records and stream files are never
  modified.

### 3.3 Capture index

- Specify how the pass-level capture index is created, advanced and finalized
  crash-consistently while keeping published per-act records immutable.
- The index must preserve the strict, gap-free sequence and ordered record
  digests already required by C-5 and C-12.
- Every published index state needed for recovery or review must use the same
  file-synchronization, atomic-publication and containing-directory barrier.
- Define an unambiguous finalization point and digest for the handback. A
  missing, stale, non-durable or internally inconsistent final index is an
  `inconclusive` stop, not something reconstructed from the transcript or
  memory.

### 3.4 Scope and accuracy

- This is a requirements correction only. Do **not** design or implement the
  capture tool, select a programming language or specific API, add source or
  tests, or claim RP-11 is satisfied.
- Use implementation-neutral terms such as successful file synchronization,
  atomic rename and successful containing-directory synchronization. It is
  acceptable to name the required durability semantics; do not invent an
  executable command.
- Reconcile RP-11, C-2 through C-12, §9.1, §9.3, §11.2, rollback/retention,
  the handback template and any admission text that currently treats only the
  record as durable. Avoid unrelated edits.
- Retain the existing rule that a capture failure stops the pass and nothing is
  retried or reissued.

## 4. Controls that must not change

- Preserve the resolved disposition of original findings OP1-R1, OP1-R2 and
  OP1-R3. Do not let Pass A observations become RP-1 inputs; do not defer row
  40; do not describe either pass as executable while RP-11 is absent.
- Preserve MD-1 through MD-6 exactly.
- P5.0-R5 remains **Blocking**.
- OD-62 G-A remains conditional and not binding.
- `plan.is_executable=False` remains controlling.
- Package 5.0 remains not ready.
- RP-10, RP-11, RP-12, A-6 and all other unresolved prerequisites remain
  fail-closed.
- Feasibility and production-code evidence remain separate and
  non-substitutable.
- The supervised reboot and RR-11, RR-14 and RR-16 remain mandatory.
- JNL-40(b) remains excluded from P5.0-R5 closure without weakening
  `R-5.0-13` or its external-evidence controls.

## 5. Authority boundary

This assignment authorizes repository reads and documentation edits only.

Do not:

- SSH, synchronize, inspect or otherwise contact `oracle-test`;
- run `sudo`, access PostgreSQL, invoke a verifier, harness or evidence band,
  provision anything, execute a controlled write or reboot;
- run the harness with `--execute` or clear a real-execution refusal;
- implement or modify source, tests, hooks, manifests, generated evidence,
  migrations, schema, infrastructure or configuration;
- create capture records or test the proposed durability sequence;
- access, inspect, `stat`, change, move, delete or reuse any protected
  historical `/tmp` artifact;
- run a secrets scan or issue a command expected to engage a secrets guard;
- retry or route around a guard or tool refusal;
- commit, push, rewrite history, restore files from `HEAD`, or alter unrelated
  dirty-worktree changes; or
- authorize either pass, accept the prompt, close P5.0-R5, bind OD-62 G-A or
  declare Package 5.0 ready.

If a correction requires an implementation choice or proof, leave it as part
of RP-11's later implementation-and-review obligation. Do not cross the
documentation boundary.

## 6. Validation and handback

Run only safe repository-local documentation checks:

1. search the amended draft for every claim using `durable`, `flush`,
   `synchron`, `atomic`, `rename`, `capture index`, `inconclusive` and
   `capture failure`, and verify the publication order and failure semantics
   agree throughout;
2. verify that stream files, per-act records, containing-directory barriers
   and the final capture index are all covered;
3. verify all new relative links resolve;
4. run `git diff --check` limited to the documentation files changed by this
   assignment; and
5. inspect the scoped diff and report pre-existing worktree changes without
   modifying them.

Do not run suites: this assignment changes documentation only and performs no
capture implementation or operational procedure.

Return the remediation handback and stop for Codex independent review. No
later action is implicitly authorized.
