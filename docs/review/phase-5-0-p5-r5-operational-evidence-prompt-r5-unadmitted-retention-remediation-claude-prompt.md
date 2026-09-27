# Claude prompt — remediate unadmitted-file retention verification

Prompt ID: `C-P5.0-R5-OP1-R5`

Date: 2026-09-27

State: **assigned; repository-only; no operational authority**

## 1. Assignment

Claude, remediate the single Blocking finding in Codex's R4 independent
review:

`docs/review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r4.md`

Read that review completely before editing. Also read, in the order required
by the repository entry point:

1. `.agents/AGENTS.md` completely;
2. `docs/implementation-plan.md` using its reading map, including §§0, 16 and
   20, Package 5.0 and its acceptance criteria, and §§13–14;
3. `docs/review/Handover information`;
4. the first restriction banner and relevant contract in
   `docs/operations/disposable-test-server.md`;
5. the exact R4-amended authorization draft identified in the Codex review;
6. the C-P5.0-R5-OP1-R4 assignment and handback; and
7. the R3 review and earlier reviews needed to preserve their resolved
   dispositions.

The R4 review is the controlling defect list. The governing documents and
MD-1 through MD-6 remain authoritative where it does not speak.

## 2. Deliverables

Produce exactly these documentation results:

1. Amend
   `docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`
   in place. Keep it visibly **draft, unaccepted and unauthorized**.
2. Create
   `docs/review/phase-5-0-p5-r5-operational-evidence-prompt-r5-unadmitted-retention-remediation-handback.md`
   with the exact changes, unresolved prerequisites, validation performed,
   files changed, checks not run and final Git status relevant to the task.
3. Update `docs/review/Handover information`,
   `docs/project-management/status.md`, implementation-plan §20 and the first
   disposable-server restriction banner only when returning the completed
   remediation, so they point to the amended draft, this assignment, the R5
   handback and the required Codex review.

Do not rewrite an earlier Codex review, assignment or handback. They are
durable records of earlier bytes and dispositions.

## 3. Required correction

### 3.1 OP1-R4-1 — bidirectional retained-name verification

Amend B0-RA so its complete, non-mutating enumeration of Pass A's retained
capture root proves bidirectional agreement between the names present under
`MI.capture_root_A` and the names accounted for by Pass A's final state *F*.

The check must establish both directions:

1. **Observed to recorded.** Every name observed anywhere under the root is
   accounted for by *F* as exactly one of: *F* itself, a state in *F*'s chain,
   a listed per-act record, a stream file bound by a listed record, or a name
   *F* records as unadmitted.
2. **Recorded to observed.** Every such name accounted for by *F*, including
   every unadmitted name it records, exists under the root at the exact
   relative name and expected object type recorded by the contract.

The comparison must be over a complete recursive relative-name set, not only
the root's immediate children. It must reject duplicate or ambiguous names,
path aliases, traversal outside the root, unexpected object types and any
inability to complete enumeration or comparison. How RP-11 safely resolves
paths and detects those conditions remains an implementation-and-review
obligation; do not select an API or language here.

Any absent recorded name, unexpected observed name, name/type mismatch,
duplicate or ambiguous representation, escape from the root, or incomplete
comparison is a fail-closed B0 stop. B0-08 does not run, no
`MI.capture_root_B` is created, no Pass B X-1 occurs and no Pass B host command
is issued. Nothing under either capture root is changed, and the check is not
retried.

### 3.2 Evidentiary limit for unadmitted files

Unadmitted files do not have a content digest in the existing contract.
Therefore:

* B0-RA may prove that an unadmitted object remains present at its recorded
  relative name and has its recorded object type, when *F* records that type;
* B0-RA must **not** claim that presence proves the object's bytes or metadata
  are unchanged;
* if *F* does not currently record enough information to identify an
  unadmitted object's exact relative name and expected type without inference,
  amend the requirements minimally so future *F* states record those fields;
  and
* do not add a content digest for an unadmitted file unless doing so is already
  supported by the publication contract. A file whose durability barrier
  failed must not be promoted into evidence by hashing it later.

Keep C-8's retention requirement. State the distinction between verified
presence/name/type and unverified content integrity explicitly in B0-RA, X-4,
C-8 and the handback template wherever needed to prevent overclaiming.

### 3.3 Dependent references and scope

Reconcile every dependent reference, including at least:

* RP-11's retention-check requirement;
* B0-RA and its expected/failure result;
* C-8, C-12, C-15 and X-4;
* §9.4 review inputs and §9.5's retained-evidence description;
* §10 retention/rollback wording;
* §11.2 admission and stop conditions and §11.3 no-retry text;
* the Pass A final-state and Pass B B0-RA handback template fields; and
* every occurrence found by complete searches for `unadmitted`, `accounted`,
  `every name`, `B0-RA`, `retained`, `X-4`, `relative name`, `object type` and
  `content`.

This is one requirements correction only. Do not implement the check, invent
an executable command, add source or tests, or claim RP-11 is satisfied. Do
not add a continuous monitor or claim protection against changes after B0-RA.

## 4. Controls that must not change

* Preserve the resolved dispositions of OP1-R1, OP1-R2, OP1-R3, OP1-R1-1,
  OP1-R2-1, OP1-R2-2 and OP1-R3-1 except for the precise unadmitted-file gap
  described by OP1-R4-1.
* Preserve B0-RA's ordering before B0-08, Pass B's X-1 and every Pass B host
  command.
* Preserve distinct `MI.capture_root_A` and `MI.capture_root_B`, one genesis
  state, index chain, final state and handback binding per pass, and the rule
  that neither root lies within the other.
* Preserve §9.5.3's ordered stop transition and the no-X-3 rule after an
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

1. search every occurrence listed in §3.3 and read each hit in context;
2. model both set-difference directions and verify either non-empty difference
   stops Pass B before B0-08;
3. verify recursive relative-name and object-type requirements are consistent
   throughout;
4. verify no clause claims content integrity for an undigested unadmitted
   object or promotes it into admitted evidence;
5. verify B0-RA remains non-mutating, one-shot and ordered before Pass B's root
   creation and every Pass B host command;
6. verify OP1-R2-1, OP1-R2-2 and the rest of OP1-R3-1 remain resolved;
7. verify all new relative links resolve;
8. run `git diff --check` limited to the documentation files changed by this
   assignment; and
9. inspect the scoped diff and report pre-existing worktree changes without
   modifying them.

Do not run suites: this assignment changes documentation only and performs no
capture implementation or operational procedure.

Return the R5 remediation handback and stop for Codex independent review. No
later action is implicitly authorized.
