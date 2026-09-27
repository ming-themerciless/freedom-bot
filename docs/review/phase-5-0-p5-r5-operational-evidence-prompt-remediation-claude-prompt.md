# Claude prompt — remediate C-P5.0-R5-OP1 operational-evidence draft

Prompt ID: `C-P5.0-R5-OP1-R1`  
Date: 2026-09-27  
State: **assigned; repository-only; no operational authority**

## 1. Assignment

Claude, remediate the returned P5.0-R5 operational-evidence authorization
prompt in accordance with the complete Codex review:

`docs/review/project-review-2026-09-27-p5-r5-operational-evidence-prompt.md`

Read that review completely before editing. Also read, in the order required by
the repository entry point:

1. `.agents/AGENTS.md` completely;
2. `docs/implementation-plan.md` using its reading map, including §§0, 16, 20,
   the Package 5.0 milestone and its acceptance criteria;
3. `docs/review/Handover information`;
4. the restriction banner and relevant operational contract in
   `docs/operations/disposable-test-server.md`;
5. the existing authorization draft and its drafting handback;
6. the accepted P5.0-R5 evidence-reconciliation handback; and
7. the reviewed source passages governing E7 target facts and the concrete E7
   identity step.

The Codex review is the controlling defect list for this remediation. The
governing documents and MD-1 through MD-6 remain authoritative where the
review does not speak.

## 2. Deliverables

Produce exactly these documentation results:

1. Amend
   `docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`
   in place. Keep it visibly **draft and unauthorized**.
2. Create
   `docs/review/phase-5-0-p5-r5-operational-evidence-prompt-remediation-handback.md`
   with the exact changes, unresolved prerequisites, validation performed,
   files changed, checks not run and the final Git status relevant to the
   assignment.
3. Update `docs/review/Handover information`,
   `docs/project-management/status.md`, and implementation-plan §20 only when
   returning the completed remediation, so each points to the amended draft,
   this assignment, the remediation handback and the required Codex re-review.

Do not rewrite the original drafting handback or the Codex review. They are
durable records of the bytes and disposition reviewed.

## 3. Required corrections

### 3.1 RP-1 and E7 expectations

- Remove every claim that Pass A observations are the exclusive or sufficient
  source of `E7_TARGET_FACTS`.
- Do not use values observed from `grep`, `/proc`, `id`, `capsh`, P-01, P-02 or
  E7 itself as both the expectation and the later comparison target.
- Preserve the distinction between independently supplied reviewed
  expectations and corroborative observations.
- Specify the provenance and independent-review requirement for owner-stated
  expectations. If the governing sources do not provide a technically sound,
  reviewed method, leave a typed, fail-closed repository prerequisite and
  explain exactly what later assignment must resolve it.
- Do not invent target facts or claim that a different process represents the
  final interpreted E7 process.

### 3.2 `fsync` failure injection

- Reclassify reconciliation row 40 and A-5.0-5(k) as remaining P5.0-R5
  feasibility work.
- Require a bounded, reviewed fault-injection producer and evidence contract.
- If it does not exist, add an explicit repository prerequisite that blocks the
  affected band. Do not invent implementation or silently defer the work to
  the production gate.
- Do not make a new residual-risk or deferral decision on the maintainer's
  behalf.

### 3.3 Evidence capture

- Reconcile the per-act evidence fields with an exact client-side capture
  procedure capable of preserving separate stdout and stderr bytes, their
  SHA-256 digests, exact argv, UTC start/end and exit status.
- The method must not rely on a merged or potentially truncated transcript and
  must not create an unauthorized file on `oracle-test`.
- State the client-side artifact location, ownership, mode, retention,
  redaction boundary, failure behavior and how the handback binds each record
  to the command it describes.
- If no reviewed repository mechanism supports this, make it an unmet
  prerequisite. Do not call Pass A or Pass B executable without it.

### 3.4 Accuracy and admission

- Rename Pass A as synchronization plus read-only host preflight. Describe
  `rsync --delete` as the sole planned Pass A target mutation, subject to later
  authorization.
- Retain unresolved values, including `MI.run_record_path`, as typed blockers
  unless a governing source resolves them.
- Keep MD-5 unsatisfied until a durable independent acceptance record exists;
  local tests are preflight evidence only.
- Require a clean pinned commit, new manifest/review digest where affected and
  an independent review of the exact amended bytes before authorization.
- Ensure the matrix, prerequisites, admission bands, stop conditions,
  rollback, cleanup, handback and final-state survey agree with one another.

## 4. Decisions and restrictions that must not change

- Preserve MD-1 through MD-6 exactly.
- P5.0-R5 remains **Blocking**.
- OD-62 G-A remains conditional and not binding.
- `plan.is_executable=False` remains controlling.
- Package 5.0 remains not ready.
- Feasibility evidence remains distinct from later production-code evidence.
- MD-3's supervised reboot remains mandatory for feasibility closure.
- MD-4's RR-11, RR-14 and RR-16 recovery rehearsals remain mandatory.
- MD-6 continues to exclude JNL-40(b) from the closure requirement without
  weakening `R-5.0-13` or its external-evidence controls.
- Pass B remains blocked by every unmet repository prerequisite. Do not reduce
  or waive RP-1 through RP-9 merely to make the draft appear executable.

## 5. Authority boundary

This assignment authorizes repository reads and documentation edits only.

Do not:

- SSH, synchronize, inspect or otherwise contact `oracle-test`;
- run `sudo`, access PostgreSQL, invoke a verifier or evidence band, provision
  anything, execute a controlled write, or reboot;
- run the harness with `--execute` or clear any real-execution refusal;
- implement or modify source, tests, hooks, manifests, generated evidence,
  migrations, schema, infrastructure or configuration;
- access, inspect, `stat`, change, move, delete or reuse any protected
  historical `/tmp` artifact;
- run a secrets scan or issue a command expected to engage a secrets guard;
- retry or route around a guard or tool refusal;
- commit, push, rewrite history, restore files from `HEAD`, or alter unrelated
  dirty-worktree changes; or
- authorize either pass, accept the prompt, close P5.0-R5, bind OD-62 G-A or
  declare Package 5.0 ready.

If a required correction needs source implementation, a maintainer decision,
target observation or operational authority, document a typed prerequisite and
stop at the documentation boundary.

## 6. Validation and handback

Run only safe repository-local documentation checks:

1. search the amended documents for stale claims that Pass A supplies E7
   expectations, that row 40 is production-only, or that either pass is
   executable despite an unmet capture mechanism;
2. verify all new relative links resolve;
3. run `git diff --check` limited to the documentation files changed by this
   assignment; and
4. inspect the scoped diff and report pre-existing worktree changes without
   modifying them.

Do not run suites: this assignment changes documentation only and its remote
commands remain unexecuted by construction.

Return the remediation handback and stop for Codex independent re-review. No
later action is implicitly authorized.

