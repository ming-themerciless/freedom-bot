# Claude prompt — remediate C-P5.0-R5-OP1-R2 capture-contract consistency

Prompt ID: `C-P5.0-R5-OP1-R3`

Date: 2026-09-27

State: **assigned; repository-only; no operational authority**

## 1. Assignment

Claude, remediate the two Blocking findings in Codex's R2 independent review:

`docs/review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r2.md`

Read that review completely before editing. Also read, in the order required
by the repository entry point:

1. `.agents/AGENTS.md` completely;
2. `docs/implementation-plan.md` using its reading map, including §§0, 16 and
   20, Package 5.0 and its acceptance criteria, and §§13–14 because this task
   concerns evidence durability and operations;
3. `docs/review/Handover information`;
4. the first restriction banner and relevant contract in
   `docs/operations/disposable-test-server.md`;
5. the exact R2-amended authorization draft identified in the Codex review;
6. the C-P5.0-R5-OP1-R2 remediation handback and assignment; and
7. the R1 re-review and original Codex review, so resolved findings are not
   regressed.

The R2 review is the controlling defect list for this remediation. The
governing documents and MD-1 through MD-6 remain authoritative where it does
not speak.

## 2. Deliverables

Produce exactly these documentation results:

1. Amend
   `docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`
   in place. Keep it visibly **draft, unaccepted and unauthorized**.
2. Create
   `docs/review/phase-5-0-p5-r5-operational-evidence-prompt-r3-contract-consistency-remediation-handback.md`
   with the exact changes, unresolved prerequisites, validation performed,
   files changed, checks not run and final Git status relevant to the task.
3. Update `docs/review/Handover information`,
   `docs/project-management/status.md`, implementation-plan §20 and the first
   disposable-server restriction banner only when returning the completed
   remediation, so they point to the amended draft, this assignment, the new
   handback and the required Codex review.

Do not rewrite either earlier Codex review, any earlier assignment, or any
earlier handback. They are durable records of earlier bytes and dispositions.

## 3. Required corrections

### 3.1 OP1-R2-1 — distinct retained capture roots

Replace the single ambiguous `MI.capture_root` contract with explicit,
pass-specific capture roots:

- `MI.capture_root_A` is used only by Pass A;
- `MI.capture_root_B` is used only by Pass B;
- the two absolute paths must be distinct;
- each path must independently meet C-6 and the accepted-filesystem condition;
- each path must be absent before its own pass, created exclusively by RP-11,
  and receive its own genesis state and capture-index chain; and
- Pass A's root remains retained, unmodified and unused while Pass B is
  admitted and executed. It is never removed, renamed, reused or modified to
  make Pass B's root absent.

Reconcile every dependent reference, including at least:

- the header's Pass A admission summary;
- §4.4 RP-11 where it describes the fixed repository-host location;
- §4.5 maintainer inputs and their used-by column;
- A0-08 for Pass A;
- B0, so it performs the equivalent check and X-1 creation against
  `MI.capture_root_B`, not by textually reusing Pass A's value;
- C-6, C-12 and C-14;
- §9.1, §9.4 and §9.5's preamble and subsections;
- rollback, retention and interruption text;
- §11.2 admission and stop conditions;
- the Pass A and Pass B handback templates or their pass-specific expansion;
  and
- the final draft reminder and every other occurrence found by a complete
  `capture_root` search.

Keep **one index per pass**. Do not introduce one shared parent index, reuse an
earlier chain, or weaken retention to solve the conflict. If a common parent
directory is named, both leaf roots must still be separately and exclusively
created and independently durable, and the parent must not create an
unreviewed collision or cleanup requirement.

### 3.2 OP1-R2-2 — one ordered stop/finalization transition

Make C-10, X-3, X-4, §9.5.3, §11.2 and every dependent statement describe one
unambiguous transition:

1. a failure or refusal stops all command execution immediately;
2. no host command is issued, retried or reissued after the stop;
3. if the capture mechanism and repository host remain available, the **only**
   permitted write after the failure/refusal is one X-3 finalization attempt;
4. the capture root becomes read-only when that finalization attempt reaches
   either outcome: its final directory barrier succeeds, or the attempt fails;
5. a failed finalization barrier is not retried or cured, and the resulting
   final state is not repaired, completed or reconstructed; and
6. if the capture mechanism or repository host was interrupted, no X-3 attempt
   is possible after recovery and X-4 applies directly.

Use precise language distinguishing:

- stopping further commands;
- the local X-3 finalization attempt;
- the X-3 finalization point on success; and
- the read-only state after the attempt or after an interruption.

Do not call the X-3 attempt a retry or repair. Do not permit it to alter any
stream, per-act record or earlier index state. Preserve the rule that a missing,
stale, non-durable or inconsistent final state makes the capture evidence
`inconclusive` and is never reconstructed.

### 3.3 Scope and accuracy

- This is a requirements correction only. Do **not** design or implement the
  capture tool, choose a programming language or API, add source or tests, or
  claim RP-11 is satisfied.
- Preserve P-1 through P-8, X-1 through X-4 and C-1 through C-15 except for the
  minimum wording needed to resolve these two findings consistently.
- Keep implementation-neutral durability terms. Do not invent an executable
  command.
- Avoid unrelated editorial changes and do not reopen questions that the R2
  review confirmed as resolved.

## 4. Controls that must not change

- Preserve the resolved disposition of OP1-R1, OP1-R2, OP1-R3 and OP1-R1-1.
- Do not let Pass A observations become RP-1 inputs; do not defer row 40; do
  not describe either pass as executable while RP-11 is absent.
- Preserve MD-1 through MD-6 exactly.
- P5.0-R5 remains **Blocking**.
- OD-62 G-A remains conditional and not binding.
- `plan.is_executable=False` remains controlling.
- Package 5.0 remains not ready.
- RP-1 through RP-12, A-6 and all other unresolved prerequisites remain
  fail-closed unless an existing accepted record already satisfies them. This
  assignment does not satisfy any of them.
- Feasibility and production-code evidence remain separate and
  non-substitutable.
- The supervised reboot and RR-11, RR-14 and RR-16 remain mandatory.
- JNL-40(b) remains excluded from P5.0-R5 closure without weakening
  `R-5.0-13` or its external-evidence controls.
- The client transcript remains non-evidence, raw streams remain separately
  retained, and published evidence remains immutable.

## 5. Authority boundary

This assignment authorizes repository reads and documentation edits only.

Do not:

- SSH, synchronize, inspect or otherwise contact `oracle-test`;
- run `sudo`, access PostgreSQL, invoke a verifier, harness or evidence band,
  provision anything, execute a controlled write or reboot;
- run the harness with `--execute` or clear a real-execution refusal;
- implement or modify source, tests, hooks, manifests, generated evidence,
  migrations, schema, infrastructure or configuration;
- create capture roots or records, or test the proposed durability sequence;
- access, inspect, `stat`, change, move, delete or reuse any protected
  historical `/tmp` artifact;
- run a secrets scan or issue a command expected to engage a secrets guard;
- retry or route around a guard or tool refusal;
- commit, push, rewrite history, restore files from `HEAD`, or alter unrelated
  dirty-worktree changes; or
- authorize either pass, accept the draft, close P5.0-R5, bind OD-62 G-A or
  declare Package 5.0 ready.

If a correction requires an implementation choice or proof, leave it as part
of RP-11's later implementation-and-review obligation. Do not cross the
documentation boundary.

## 6. Validation and handback

Run only safe repository-local documentation checks:

1. search the amended draft for every occurrence of `capture_root`,
   `capture root`, `A0-08`, `B0`, `stop`, `finaliz`, `read-only`, `C-10`,
   `X-3`, `X-4` and `interruption`, and verify the pass-specific roots and
   stop transition agree throughout;
2. verify each pass has exactly one distinct root, genesis state, index chain,
   final state and handback binding, with no retention conflict;
3. verify X-3 is the sole permitted post-stop write when possible and that
   read-only state begins after its one success-or-failure outcome;
4. verify all new relative links resolve;
5. run `git diff --check` limited to the documentation files changed by this
   assignment; and
6. inspect the scoped diff and report pre-existing worktree changes without
   modifying them.

Do not run suites: this assignment changes documentation only and performs no
capture implementation or operational procedure.

Return the R3 remediation handback and stop for Codex independent review. No
later action is implicitly authorized.
