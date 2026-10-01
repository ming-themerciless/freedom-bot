# Claude prompt — RP-11 I1-R3-R1 retained-alias review remediation

Prompt ID: `C-P5.0-R5-RP11-I1-R3-R1`

Date: 2026-09-28

State: **assigned by Peter Duscha's instruction to execute this prompt;
repository-only remediation and decision preparation; no host or operational
authority**

## 1. Assignment

Claude, remediate the three findings from Codex's independent review of
`C-P5.0-R5-RP11-I1-R3-I1`:

* **RP11-I1-R3-1, Blocking:** the treatment of a recorded unadmitted
  staging/final pair is not yet supported by a confirmed decision of record;
* **RP11-I1-R3-2, Important:** the reported whole-package result of 3320
  passed and 0 skipped did not reproduce; and
* **RP11-I1-R3-3, Important:** the amended operational-evidence draft still
  says that RP-11 or its mechanism does not exist, although an unwired,
  unaccepted implementation now exists.

Read, in this order, before planning or editing:

1. `.agents/AGENTS.md` completely;
2. `docs/implementation-plan.md` using its reading map, including §§0, 13, 14,
   16 and 20 and the Package 5.0 milestone and acceptance criteria;
3. `docs/review/Handover information`;
4. the first restriction banners and relevant contract in
   `docs/operations/disposable-test-server.md`;
5. `docs/review/phase-5-0-p5-r5-rp11-i1-r3-retained-alias-implementation-claude-prompt.md`;
6. `docs/review/project-review-2026-09-28-p5-r5-rp11-i1-r3.md`;
7. `docs/review/phase-5-0-p5-r5-rp11-i1-r3-retained-alias-implementation-handback.md`;
8. `docs/review/phase-5-0-p5-r5-rp11-i1-r3-publication-redesign-proposal.md`
   and its maintainer acceptance;
9. the proposed amended
   `docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`,
   especially RP-11, A0-08, B0-RA, B0-08 and §§9.5–9.5.4;
10. the RP-11 capture, retention and descriptor source and focused tests; and
11. the review manifest, generated plan and directly affected structural and
    no-execution tests.

The accepted requirements baseline remains the R5 bytes at SHA-256
`5e06a38811462613244ee258524461eb23b5598862ce43efa3ec77365040acb3`.
The I1-R3 draft at SHA-256
`402126322f341d378c569cc302c8eb3607b746a1b5c8fc81a91d6af8b19cbe28`,
the version-23 manifest review-input digest `264674da…`, and the implementation
remain proposed and unaccepted. This remediation must not describe any of them
as accepted or as satisfying RP-11.

## 2. RP11-I1-R3-1 — prepare the decision; do not block the other remediation

This assignment is executable now. The absence of the policy decision does
**not** block repository reading, the descriptor-exhaustion diagnosis,
RP11-I1-R3-2 remediation, RP11-I1-R3-3 remediation, tests, or the handback.

For a staging/final pair left after the final link but before admission by a
durable successor state, analyze these two policies:

1. **Permit metadata-only.** If the final state records both unadmitted names,
   X-4 and B0-RA may permit them to share one inode only when both exact names
   are present as regular files, identify the same inode, each reports link
   count two and no third name under the complete enumeration reaches that
   inode. Nothing is opened, read, digested, admitted or used as evidence, and
   no unchanged identity, content, owner, mode, size or digest is claimed.
2. **Refuse unadmitted aliases.** The alias exception remains limited to
   admitted objects. Any unadmitted pair sharing an inode makes X-4
   inconclusive and makes B0-RA stop fail-closed.

The implementation handback reports an in-session answer selecting option 1,
but explicitly says it still needs confirmation as the decision of record.
Do not infer that confirmation. Instead:

1. inspect the existing implementation and tests for both policies;
2. compare their fail-closed behavior, evidence meaning, operational effect
   after a stopped Pass A, and consistency with accepted R5 retention rules;
3. recommend one policy with concrete reasons;
4. create
   `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r1-unadmitted-pair-decision-proposal.md`
   for Peter's decision; and
5. leave source semantics unchanged pending that decision.

The decision proposal must contain explicit `accept option 1` and `accept
option 2` decision text that Peter can adopt without reinterpretation. It is a
proposal, not an acceptance record. RP11-I1-R3-1 remains Open and Blocking on
return unless Peter supplies a decision while this assignment is active.

## 3. RP11-I1-R3-1 — align requirements, source and tests

Audit the complete path and use it to support the §2 recommendation:

* the RP-11 row and B0-RA contract in the operational-evidence draft;
* the six publication states and X-1 through X-4;
* `capture_contract.accounted_objects` and its pair representation;
* the store's known-object and publication-state accounting;
* final-state construction and its unadmitted set;
* retention enumeration, admitted-pair verification and alias checking; and
* every positive, negative, race and no-read test for unadmitted objects.

For the currently implemented option 1, verify that the exception is exactly
one recorded pair and no
wider. At minimum, refuse a lone member with link count two, divergent members,
a third link inside or outside the expected pair, a cross-object alias, a name
in two pairs or categories, an unrecorded pair, a non-regular member, an absent
member, and any incomplete or changing enumeration. Prove that neither member
is opened, read or digested.

For option 2, identify the exact requirements, source and tests that a later
decision implementation would change. Do not implement that branch in this
assignment. Do not unlink, rename, repair, complete or adopt either name.

Preserve the accepted R5 bidirectional name/type comparison and evidentiary
limit. Preserve the I1-R3 publication direction: named exclusive staging,
one no-follow non-replacing hard link, both names retained, no automatic
cleanup, and admission only by the next durable state. Keep the mechanism
unwired.

## 4. RP11-I1-R3-2 — reproduce and diagnose the suite discrepancy

Codex reproduced the focused RP-11 selection exactly:

* `test_rp11_capture.py test_rp11_retention.py`: **367 passed, 0 skipped**.

Codex did not reproduce the handback's whole-package claim. With the stated
interpreter and prefix, a serial run of `tests/phase_5_0_evidence` produced:

* **2941 passed, 379 failed, 0 skipped**;
* the first visible RP-11 failures occurred after file-descriptor exhaustion;
* later failures cascaded through RP-11 and provisioning tests with
  `OSError: [Errno 24] Too many open files`; and
* the reviewing shell's soft descriptor limit was 1024.

Diagnose this using repository-local tests and pytest temporary directories
only. Determine and report:

1. whether the exact whole-package command reproduces the failure in a fresh
   process;
2. the first failing test and the earliest point at which descriptor growth is
   attributable to a test or production path;
3. whether the retained-alias changes introduce, expose or merely follow the
   leak;
4. the exact descriptor ownership/release defect, if one exists;
5. why the earlier 3320-pass run differed, or that the discrepancy remains
   unresolved; and
6. whether the focused and whole-package selections pass from fresh processes
   after remediation.

Use a narrowly scoped, test-only descriptor-count observation if necessary.
It may observe the current pytest process but must not inspect another process,
another host, protected artifacts, secrets or the environment. Do not raise
the descriptor limit, reorder or split the whole-package suite, suppress
failures, or weaken assertions to manufacture a green result. Do not classify
the cascade as 379 independent defects when one earlier leak explains it.

If the cause is outside the files authorized by §8, stop and return the exact
source and the smallest proposed follow-up scope. Do not edit unrelated
production or test modules under this assignment.

## 5. RP11-I1-R3-3 — correct stale existence claims

Amend the proposed operational-evidence draft so its state statements are
factually precise and mutually consistent. Replace claims such as:

* `No such mechanism exists in the repository`;
* `Unresolved: RP-11 does not exist`; and
* equivalent A0-08, B0-RA or B0-08 statements,

with wording that distinguishes these facts:

* repository source and focused tests for the unwired mechanism exist;
* the implementation, requirements amendment and digest are unaccepted;
* the mechanism is not wired to any operational command;
* C-11 synchronization capture and the pinned launcher environment remain
  unresolved;
* no real capture root or Pass A handback exists;
* A0-08, B0-RA and B0-08 therefore remain unusable; and
* RP-11 remains unmet.

Do not turn a wording correction into acceptance, a manifest pin, operational
authorization or finding closure. Recompute and report the amended draft's
full SHA-256.

## 6. Required tests

Retain and extend focused tests as needed to prove the selected §2 policy and
the diagnosis. At minimum run, serially and from fresh processes where stated:

1. `test_rp11_capture.py test_rp11_retention.py`;
2. the I1 focused selection recorded in the I1-R3 handback;
3. `tests/phase_5_0_evidence` as one whole-package pytest process;
4. directly affected structural, manifest, generated-plan and no-execution
   tests; and
5. the harness CLI dry run only, never `--execute`.

Every pytest command must explicitly unset `TEST_DATABASE_URL`, set
`PYTHONDONTWRITEBYTECODE=1`, disable the pytest cache provider, run serially and
include `-rs`. Zero focused skips are required. Record exact pass, fail and skip
counts and all warnings. If the whole-package run still fails, report the first
causal failure and the final totals; do not claim it passed.

Also run scoped `git diff --check`, compile the changed Python modules, verify
relevant Markdown links and independently recompute every changed source,
draft and generated-artifact digest reported in the handback.

Do not run the full bot or web suites. Do not use `oracle-test`.

## 7. Deliverables

1. Create the §2 decision proposal; preserve current source semantics pending
   Peter's decision.
2. Correct the stale operational-draft state wording from §5.
3. Make only the narrowly necessary source/test correction established by the
   descriptor diagnosis. If none is needed in this slice, do not manufacture
   one.
4. Update `review_manifest.py` and regenerate the existing review artifacts
   through the established dry-run workflow only if covered source bytes
   change. Increment the manifest version with a precise reason when required.
   A regenerated digest is review input, never approval.
5. Create
   `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r1-retained-alias-review-remediation-handback.md`
   containing:
   * the §2 decision proposal, recommendation and still-open decision status;
   * a disposition for each of RP11-I1-R3-1 through RP11-I1-R3-3;
   * exact files changed and before/after SHA-256 values;
   * the requirements/source/test consistency map;
   * the descriptor-exhaustion reproduction and root-cause analysis;
   * exact commands, fresh-process boundaries and results;
   * manifest and generated-artifact effects;
   * unwired confirmation;
   * checks not run and why;
   * task-relevant Git status; and
   * proposed independent-review focus.
6. On return only, update `docs/review/Handover information`,
   `docs/project-management/status.md`, implementation-plan §20 and the first
   disposable-server restriction banner to point to this remediation, its
   handback and mandatory independent Codex re-review.

Do not edit historical handbacks, reviews or acceptance records. Do not add an
acceptance record or mark any finding closed. Stop after the handback and
current-state pointer updates.

## 8. Authorized files and stop conditions

The authorized edit scope is limited to:

* `docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`;
* the RP-11 files under `tools/phase_5_0_evidence/` already changed by I1-R3,
  but only where required by the selected policy or demonstrated descriptor
  defect;
* directly affected tests under `tests/phase_5_0_evidence/`;
* `tools/phase_5_0_evidence/review_manifest.py` and the two existing generated
  review artifacts, only if their inputs change;
* the new remediation handback; and
* the new §2 decision proposal; and
* the four current-state pointers named in §7.

Stop and return without expanding scope if:

* the descriptor leak is owned by another module not listed above;
* remediation would change C-11, the launcher environment, another RP,
  MD-1 through MD-6, I3 behavior, an accepted R5 requirement, architecture,
  data authority, authorization or operational strategy; or
* a guard or tool refuses a call.

Do not bypass a stop by copying logic, altering test order, increasing a
resource limit or weakening a check.

## 9. Authorization and prohibitions

Peter Duscha's instruction to execute this prompt assigns this repository-only
remediation. It authorizes repository reads, the scoped edits in §8, and
bounded local synthetic tests under pytest temporary directories with
`TEST_DATABASE_URL` unset. It does not authorize Claude to record Peter's
decision on the §2 policy.

It does **not** authorize:

* SSH, rsync, synchronization, network or host inspection;
* `sudo`, database access, provisioning, controlled writes, reboot, verifier,
  evidence band, harness `--execute` or real participant invocation;
* creation, inspection or reuse of a real capture root, probe path or
  operational path;
* protected historical `/tmp` artifact access;
* a secrets scan or a command expected to engage the secrets guard;
* guard, hook or governing-rule changes;
* C-11 or launcher-environment decisions, operational wiring, another RP or
  MD-1 through MD-6;
* acceptance of the requirements, implementation or manifest digest;
* marking RP-11 satisfied, setting `plan.is_executable=True`, accepting either
  pass, closing P5.0-R5, binding OD-62 G-A or declaring Package 5.0 ready; or
* a commit or push.

Do not read secrets or print the environment. Preserve unrelated worktree
changes. A guard or tool refusal is a stop condition and must not be retried,
rephrased, bypassed or escalated.

## 10. Return state

Return the remediation for independent Codex technical, security, operational
and evidence re-review, then stop.

Until that re-review and a later explicit maintainer acceptance:

* RP11-I1-R3-1 remains Open, Blocking;
* RP11-I1-R3-2 and RP11-I1-R3-3 remain Open, Important;
* RP11-I1-R1-1, RP11-I1-R2-1 and RP11-I1-2 remain Open;
* the requirements amendment, implementation and digest remain unaccepted;
* RP-11 remains unmet;
* neither pass is executable or authorized;
* P5.0-R5 remains Blocking;
* OD-62 G-A remains conditional;
* `plan.is_executable=False`; and
* Package 5.0 remains not ready.
