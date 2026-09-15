# Claude — reserved-laboratory one-shot authority remediation R2

Date: 2026-09-15. Authorization: **C-P5.0-LAB-I-R2**, a bounded
repository-local remediation only.

Review to remediate:
[Codex live-authority re-review](project-review-2026-09-14-reserved-laboratory-live-authority.md).
Submitted handback:
[live-authority handback](phase-5-0-reserved-laboratory-call-graph-remediation-r2-handback.md).
Design basis:
[runner contract r6](phase-5-0-reserved-laboratory-runner-contract-r6.md).

## Assignment

Repair the remaining **Blocking** finding
**PR-20260914-LABI-R2-1**. The current live-state checks establish the open
session, held cooperative lock, in-progress stored run and current `running`
reservation. They do not make the invocation authority one-shot: during the
same synchronous callback, code can call
`ParticipantIntegration._issue_authority()` after the genuine permit was
consumed, or construct a fully bound permit and replace the writable
`ParticipantIntegration._authority` registration. Under the same durable T6--T8
state, a second armed executor reaches the reviewed plan.

Make issuance a single invocation transition and make consumption depend on
invocation-owned state that cannot be replaced through the reviewed callback
object graph. Preserve the accepted live-state reads, call-graph ownership,
derived release evidence, terminal ordering and standing execution refusals.
Retain the two public failing reproductions and add focused negative controls
showing the corrected issuance and registration-integrity controls are each
load-bearing. Return the result for independent Codex technical and security
re-review.

This assignment authorizes repository changes and local tests with
`TEST_DATABASE_URL` unset only. It authorizes no operational or database action.

## Governing context

Before planning or changing anything, read completely:

1. `.agents/AGENTS.md`;
2. the reading map and §§0, 12 (Package 5.0), 13, 16 and 20 of
   `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. the restriction banner in
   `docs/operations/disposable-test-server.md`;
5. runner contract r6, especially §§5.6, 5.7, 5.11, 5.11.1, 5.12, 5.13 and
   9.2--9.3;
6. the review, handback and earlier remediation prompt linked above;
7. the active Package 5.0 plan, project status, decision register and RAID
   register; and
8. `execution/participants.py`, `execution/executor.py`,
   `execution/host_lock.py`, `execution/run_ledger.py`, `execution/cli.py` and
   every live-authority/call-graph test.

Inspect Git status and preserve unrelated and reviewer-authored changes. Trace
the complete reachable object graph from T2 lock acquisition through T6 durable
start, T7/T8 reservation publication, T9 effects, T10a--T12 terminal
publication and T17 lock release. In particular, include the integration point
reachable through `ExecutingRunner.session` and every ordinary method or field
the callback can reach without relying on language-level secrecy.

## Blocking reproductions that must remain public

Keep these tests unchanged in purpose and passing after remediation:

1. `test_the_live_invocation_cannot_issue_a_second_authority` — the first armed
   executor consumes the genuine authority; a callback call to
   `_issue_authority()` must not authorize a second executor under the same
   start.
2. `test_the_live_registration_cannot_be_replaced_by_mutable_state` — a fully
   bound permit made through `_grant_permit()` and assigned to `_authority` must
   not authorize any effect.

Before implementation, run both against the submitted tree and preserve the
exact failing-before result. The independent reviewer observed two
`DID NOT RAISE ExecutorRefused` failures; do not deselect either test when
presenting focused evidence.

Every refusal must occur before the recording process boundary, materializer
or descriptor-bound effect issuer is reached. Assert all three remain empty.
Where a durable fixture exists, prove that the refused executor did not change
its bytes or parsed state.

## Required behavior

- One durable `participant_started` entry authorizes at most one execution of
  the reviewed effects.
- Authority issuance is a single transition for one invocation. A second
  issuance attempt refuses before constructing or registering usable
  authority, including after the first authority has been consumed.
- Consumption is tied to the invocation's actual issued state, not solely to a
  caller-writable permit, `_authority` reference, matching values or a boolean
  that the callback can replace through the reviewed object graph.
- Direct `_grant_permit()` calls, direct `_authority` assignment, copied field
  values, retained permits and equivalent integration objects authorize
  nothing.
- The final pre-effect check still establishes, through the existing
  authoritative paths:
  - the exact integration owns the exact open session;
  - that session still holds the cooperative lock;
  - the stored run is present, valid, the harness's, bound to the exact
    reservation and still in progress; and
  - the current reservation is that reservation in T8 `running` state.
- Normal return, exception and `KeyboardInterrupt` still revoke authority.
- Preserve the successful positive composition: exactly one armed executor may
  run between T8 and T10a, followed by the two terminal publications before
  T17 lock release.
- Keep refusal classifications and details fixed, bounded and free of paths,
  raw stored content, hostile values and operating-system exception text.

Do not claim that underscores, frozen dataclasses, slots, name mangling, an
importable sentinel or ordinary Python object identity create a security
boundary. Do not solve the finding only by adding another callback-writable
flag. If the claimed adversarial boundary cannot be enforced inside one Python
interpreter while the callback retains the current object graph, state that
precisely and make the smallest architectural correction that removes the
unneeded authority-bearing object from that graph; do not paper over the
limitation with documentation.

Do not add a second ledger reader, reservation walker or state machine. Reuse
`ParticipantRunLedger.read_run` and `check_reservation_history` for the durable
conjuncts.

## Required tests and sensitivity evidence

In addition to the two reproductions, retain all existing live-authority tests
and add focused public coverage for:

- issuance refuses before first issue if invocation state is absent or wrong;
- a second issuance refuses both before and after consumption;
- direct registration replacement cannot become the invocation's issued
  authority;
- the genuine authority remains consumable exactly once;
- return, exception and interruption revoke it;
- missing/closed/reopened session, released lock, absent/unreadable/wrong or
  settled run, and non-running reservation still refuse; and
- the real composition still reaches the armed executor exactly once.

Provide single-point reversals that independently disable:

1. issuance-once enforcement; and
2. registration-integrity/invocation-ownership enforcement.

Each reversal must make its named public regression fail while the test remains
unchanged. Preserve the existing reversals for session, lock, durable-run,
reservation binding/state, consumption and revocation. Restore the tree after
every reversal and verify restoration.

## Contract, gate and authority boundaries

- D1 and D2 remain proposed and unapproved; r6 remains unedited and V6 remains
  unconfirmed.
- The six non-harness wrappers remain unwired under LAB-R6. Do not wire or
  invoke them in this assignment.
- `plan.is_executable` remains `False`.
- `reservation.REAL_EXECUTION_REFUSAL` remains in force.
- All twelve target facts remain unconfirmed.
- C-7 remains unresolved and EH-R16-1 remains Open.
- Package 5.0 remains not ready, P5.0-R5 remains Blocking and OD-62 remains
  Open.
- No production bot, web, database, migration or Foundry behavior changes.
- The implementing agent approves no gate, finding or digest.

## Verification procedure

1. Run and record the two failing-before regressions without deselection.
2. Implement the smallest cohesive correction.
3. Run the two regressions, the complete live-authority module, existing
   call-graph/integration tests, the focused evidence set, structural
   no-execution tests and all of `tests/phase_5_0_evidence`, locally with
   `TEST_DATABASE_URL` unset.
4. Run locally available bot, web and Foundry suites only within this
   restriction and serially. Report every skip as unverified. Do not present the
   database-disabled web result as the database-enabled baseline.
5. Run scoped `compileall`, `git diff --check`, and configured formatter,
   linter and type checks. Do not install missing tools; report them as
   unavailable.
6. If a covered source changes, regenerate covered artifacts only through the
   non-executing CLI, repeat generation, compare bytes and independently verify
   every covered-source hash. A resulting digest is review input only and must
   never be passed to `--execute`.
7. Review the final diff for secrets, hostile values in refusals, unrelated
   changes, generated debris and any weakening of the standing execution gate.

The repository guidance names the disposable server's canonical interpreter,
but this assignment explicitly forbids using that server. If only a historical
local interpreter is installed, identify it as an available local runner and a
limitation; do not represent it as canonical environment evidence.

## Explicit prohibitions

Do not perform SSH, synchronization, host inspection, preflight, provisioning,
permission or group changes, `systemd-tmpfiles`, creation or modification of
`/run`, `/var/lib` or `/etc` objects, database operations, destructive drills,
service changes, dependency installation, generated-vector execution,
`--execute`, real process-boundary or materializer use, migration, deployment,
cutover, commit, push, reset, history rewrite or bot restart. Do not read
credentials or secret files.

Do not mark V6, V8, V10 or another target fact confirmed. Do not close C-7,
EH-R16-1, LAB-R6, P5.0-R5, OD-62 or PR-20260914-LABI-R2-1 on the implementer's
authority, declare Package 5.0 ready, approve a digest or claim operational
evidence.

## Handback and stop point

Return one dated remediation handback containing:

- the Blocking finding disposition and requirement-to-code/test traceability;
- the authority object graph and exact T2--T17 sequence before and after;
- the single issuance and consuming transitions and why callback-reachable
  replacement no longer authorizes a second execution;
- an accurate statement of the Python trust boundary;
- exact failing-before, passing-after and per-control reversal evidence;
- the positive composition trace observed while the work invocation is live;
- files and interfaces changed;
- security, interruption and recovery analysis;
- generated-artifact reproduction and review-only digest, if changed;
- exact commands, interpreters, results, skips and unavailable checks;
- rollback for repository-only changes;
- every unresolved gate, target fact and contract proposal; and
- focused questions for independent re-review.

Stop after the handback. The next checkpoint is independent Codex technical and
security re-review. No preflight, provisioning or execution follows
automatically.
