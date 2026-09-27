# Claude prompt — remediate Pass A retention verification before Pass B

Prompt ID: `C-P5.0-R5-OP1-R4`

Date: 2026-09-27

State: **assigned; repository-only; no operational authority**

## 1. Assignment

Claude, remediate the single Blocking finding in Codex's R3 independent
review:

`docs/review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r3.md`

Read that review completely before editing. Also read, in the order required
by the repository entry point:

1. `.agents/AGENTS.md` completely;
2. `docs/implementation-plan.md` using its reading map, including §§0, 16 and
   20, Package 5.0 and its acceptance criteria, and §§13–14;
3. `docs/review/Handover information`;
4. the first restriction banner and relevant contract in
   `docs/operations/disposable-test-server.md`;
5. the exact R3-amended authorization draft identified in the Codex review;
6. the C-P5.0-R5-OP1-R3 assignment and handback; and
7. the R2 review and earlier reviews needed to preserve their resolved
   dispositions.

The R3 review is the controlling defect list. The governing documents and
MD-1 through MD-6 remain authoritative where it does not speak.

## 2. Deliverables

Produce exactly these documentation results:

1. Amend
   `docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`
   in place. Keep it visibly **draft, unaccepted and unauthorized**.
2. Create
   `docs/review/phase-5-0-p5-r5-operational-evidence-prompt-r4-retention-verification-remediation-handback.md`
   with the exact changes, unresolved prerequisites, validation performed,
   files changed, checks not run and final Git status relevant to the task.
3. Update `docs/review/Handover information`,
   `docs/project-management/status.md`, implementation-plan §20 and the first
   disposable-server restriction banner only when returning the completed
   remediation, so they point to the amended draft, this assignment, the R4
   handback and the required Codex review.

Do not rewrite an earlier Codex review, assignment or handback. They are
durable records of earlier bytes and dispositions.

## 3. Required correction

### 3.1 OP1-R3-1 — fail-closed verification of Pass A retention

Add a reviewed, explicitly non-mutating Pass B admission requirement that
proves the C-8 retention condition before Pass B's X-1 creates
`MI.capture_root_B` and before any Pass B host command.

The check must establish all of the following from the Pass A handback and the
retained repository-host evidence:

1. the supplied `MI.capture_root_A` is exactly the capture root recorded in
   the Pass A handback;
2. that root and the final index state named by the Pass A handback still
   exist;
3. the re-derived SHA-256 of that final index state equals the Pass A
   handback's capture-index SHA-256; and
4. Pass A's X-4 validity check still succeeds for the retained index chain,
   records and bound stream files.

Absence, mismatch, invalidity, an unadmitted file not accounted for by the
final state, or inability to complete the verification is a fail-closed B0
stop. No `MI.capture_root_B` is created and no Pass B host command is issued.

The verification may read and list names under `MI.capture_root_A` and
re-derive digests only. It must not:

* write, move, rename, truncate, complete, repair, adopt, delete or change
  permissions on the root or anything beneath it;
* use Pass A's root or files as Pass B capture evidence;
* continue, copy or reuse Pass A's index chain for Pass B;
* weaken C-7, C-8, C-12, C-14, C-15 or X-4; or
* claim protection against changes that occur after the admission check.

Keep the existing rule that Pass A's root remains retained, unmodified and
unused **as Pass B evidence**. Reconcile wording that currently describes it
as wholly “unused” so the newly required read-only retention verification is
not contradictory.

Reconcile every dependent reference, including at least:

* §4.4 RP-11 and §4.5 inputs, including the Pass A handback root, final-state
  name and capture-index digest needed by the check;
* B0 and B0-08, or a new separately identified B0 admission step if that makes
  the ordering clearer;
* C-8, C-12 and X-4;
* §9.1, §9.4 and the §9.5 preamble;
* §10 retention/rollback wording;
* §11.2 Pass B admission and stop conditions;
* the Pass A and Pass B handback templates; and
* the final draft reminder and every other occurrence found by complete
  searches for `capture_root_A`, `retained`, `unmodified`, `unused`, `B0-08`,
  `X-4`, `final index` and `capture index SHA-256`.

Keep the requirements implementation-neutral. The interface, command,
language, filesystem-resolution method and proof that the check is safe belong
to RP-11's later implementation and independent review.

### 3.2 Scope and accuracy

This is one requirements correction only. Do not design or implement the
capture mechanism, invent executable commands, add source or tests, or claim
RP-11 is satisfied. Make the minimum consistent documentation changes needed
for OP1-R3-1. Do not add a continuous monitor, immutable filesystem mechanism
or guarantee about mutations after B0; those would expand the assignment.

## 4. Controls that must not change

* Preserve the resolved dispositions of OP1-R1, OP1-R2, OP1-R3, OP1-R1-1,
  OP1-R2-1 and OP1-R2-2.
* Preserve distinct `MI.capture_root_A` and `MI.capture_root_B`, one genesis
  state, index chain, final state and handback binding per pass, and the rule
  that neither root lies within the other.
* Preserve §9.5.3's one ordered stop transition and the no-X-3 rule after an
  interruption or without a durable *I*-0.
* Preserve MD-1 through MD-6 exactly.
* P5.0-R5 remains **Blocking**; OD-62 G-A remains conditional and not binding;
  `plan.is_executable=False`; Package 5.0 remains not ready.
* RP-1 through RP-12, A-6 and all other unresolved prerequisites remain
  fail-closed unless an accepted record already satisfies them.
* Do not let Pass A observations become RP-1 inputs, defer row 40, weaken the
  supervised reboot or RR-11/RR-14/RR-16, or include JNL-40(b) in P5.0-R5
  closure.
* The client transcript remains non-evidence, raw streams remain separately
  retained, and published evidence remains immutable.

## 5. Authority boundary

This assignment authorizes repository reads and documentation edits only.

Do not:

* SSH, synchronize, inspect or otherwise contact `oracle-test` or another
  host;
* run `sudo`, access PostgreSQL, invoke a verifier, harness, suite or evidence
  band, provision anything, execute a controlled write or reboot;
* run the harness with `--execute` or clear a real-execution refusal;
* implement or modify source, tests, hooks, manifests, generated evidence,
  migrations, schema, infrastructure or configuration;
* create, inspect or test a real capture root, record or durability sequence;
* access, inspect, `stat`, change, move, delete or reuse a protected historical
  `/tmp` artifact;
* run a secrets scan or issue a command expected to engage a secrets guard;
* retry or route around a guard or tool refusal;
* commit, push, rewrite history, restore files from `HEAD` or alter unrelated
  dirty-worktree changes; or
* authorize either pass, accept the draft, close P5.0-R5, bind OD-62 G-A or
  declare Package 5.0 ready.

If the correction requires an implementation choice or proof, leave it for
RP-11. Do not cross the documentation boundary.

## 6. Validation and handback

Run only safe repository-local documentation checks:

1. search every occurrence listed in §3.1 and read each hit in context;
2. trace Pass B admission in order and verify the retention check succeeds
   before `MI.capture_root_B` creation or any Pass B host command;
3. verify each failure mode stops fail-closed without modifying either root;
4. verify Pass A's root is read only for retention verification and is never
   reused as Pass B evidence;
5. verify OP1-R2-1 and OP1-R2-2 remain resolved;
6. verify all new relative links resolve;
7. run `git diff --check` limited to the documentation files changed by this
   assignment; and
8. inspect the scoped diff and report pre-existing worktree changes without
   modifying them.

Do not run suites: this assignment changes documentation only and performs no
capture implementation or operational procedure.

Return the R4 remediation handback and stop for Codex independent review. No
later action is implicitly authorized.
