# Claude — reserved-laboratory live-authority remediation

Date: 2026-09-14. Authorization: **C-P5.0-LAB-I-R1**, continued only for
this bounded repository remediation.

Handback to remediate:
[executable harness call-graph handback](phase-5-0-reserved-laboratory-call-graph-remediation-handback.md).
Design basis:
[runner contract r6](phase-5-0-reserved-laboratory-runner-contract-r6.md).
Prior review:
[Codex reserved-laboratory remediation review](project-review-2026-09-14-reserved-laboratory-remediation.md).

## Assignment

Repair the remaining **Blocking** defect in PR-20260914-LABI-R1-1: an armed
executor currently accepts authority represented only by a reusable Python
value and a matching `ParticipantIntegration` object. A permit can be forged by
reading ordinary module attributes, and a genuinely issued permit can be
retained and replayed after `run_harness()` has published both terminal entries
and released the cooperative lock. In either case the executor can pass
`_require_accounted_run()` without a live T2–T8 protocol instance.

Make T9 reachable only while the exact integration is holding the cooperative
lock and the exact stored harness run is durably `participant_started`, bound to
the current reservation, and still in progress. Make that authority one-shot so
it cannot be retained, copied, reconstructed or replayed after the work call or
terminal publication. Add failing-before public regressions and focused
single-conjunct negative controls, preserve the accepted call-graph and terminal
ordering repairs, regenerate covered artifacts through the non-executing path
when required, and return one remediation handback for independent Codex
technical and security re-review.

This authorization is for repository changes and local tests with
`TEST_DATABASE_URL` unset only. It authorizes no host or database operation and
no real participant, generated vector, real boundary, materializer or
`--execute` invocation.

## Governing context

Before planning or changing anything, read completely:

1. `.agents/AGENTS.md`;
2. the implementation-plan reading map and §§0, 12 (Package 5.0), 13, 16 and
   20;
3. `docs/review/Handover information`;
4. the restriction banner in
   `docs/operations/disposable-test-server.md`;
5. runner contract r6, especially §§5.6, 5.7, 5.11, 5.11.1, 5.12, 5.13 and
   9.2–9.3;
6. the handback named above and the prior Codex review it answers;
7. the active Package 5.0 plan, project status, decision register and RAID
   register; and
8. `execution/participants.py`, `execution/executor.py`,
   `execution/host_lock.py`, `execution/run_ledger.py`, `execution/cli.py` and
   their call-graph tests.

Inspect Git status and preserve all unrelated and reviewer-authored changes.
Trace the exact runtime object graph from T2 lock acquisition through T6 durable
start, T7/T8 reservation publication, T9 effects, T10a–T12 terminal publication
and T17 lock release. Do not infer live authority from class identity, matching
strings, module-private naming or an object that was once valid.

## Blocking finding — the executor does not require live authority

The submitted correction improved the CLI composition and rejects
`session=object()`, but its new authority check is not the property claimed.

### Reproduction A — the token is constructible

`participants._PERMIT_GRANT` is an ordinary readable module attribute,
`participants._grant_permit` is an ordinary callable module attribute, and
`EffectPermit.grant` is a public dataclass field. A leading underscore and
exclusion from `repr` or equality provide no access boundary in Python. Codex
constructed this without opening a session or publishing a run:

```python
from tools.phase_5_0_evidence.execution import participants
from tools.phase_5_0_evidence.lifecycle_storage import Participant

permit = participants.EffectPermit(
    participant=Participant.HARNESS_CLI,
    run_id="RUN-LABI-R1",
    reservation_id="RES-LABI-R1",
    granted=True,
    grant=participants._PERMIT_GRANT,
)
assert permit.issued
assert permit.binds(
    participant=Participant.HARNESS_CLI,
    run_id="RUN-LABI-R1",
    reservation_id="RES-LABI-R1",
)
```

The submitted `test_a_permit_cannot_be_constructed_granted` proves only that
omitting the publicly readable sentinel refuses. It does not prove that a caller
cannot obtain or supply the sentinel.

### Reproduction B — a genuine permit is replayable

The public test helper `_issued_permit` demonstrates that a work callback can
retain the genuine permit it receives. It returns that permit only after
`run_harness()` has concluded the reservation and released the lock. The permit
remains `issued=True` forever.

`ExecutingRunner._require_accounted_run()` then checks only:

- that `session` is an instance of `ParticipantIntegration`;
- that permit, runner and integration carry matching participant/run/reservation
  values; and
- that the effect issuer is armed.

It does **not** establish that this integration currently owns an open
`LaboratorySession`, that the cooperative lock is currently held, that the
stored run is present and in progress, or that this permit is being consumed
inside the one work invocation for which it was issued. A retained permit plus
the original closed integration—or a new integration with equal fields—can
therefore drive the executor directly after T12/T17.

This violates r6 §§5.6–5.7: T9 must occur while the executor holds the lock and
after the current durable T6/T7/T8 state, not merely after such a state existed
at some earlier time.

## Required behavior

- The executor's first effect must require a **live**, exact protocol
  capability owned by the active `ParticipantIntegration` invocation.
- At the final check immediately before effects, establish all of:
  - the exact integration owns an open session;
  - that session still holds the cooperative lock;
  - the exact stored run exists, is valid, is the harness participant, is bound
    to the exact reservation and remains `participant_started`/in progress;
  - the reservation record is in the exact T8 `running` state for that same
    reservation; and
  - the authority has not previously been consumed.
- A closed, never-opened, equivalent-but-distinct or wrong integration refuses.
- A completed, recovered, missing, unreadable, differently bound or otherwise
  non-current run refuses.
- Authority must be one-shot and scoped to the synchronous `work` invocation.
  Retaining an object received by `work`, copying its visible data, reading
  module attributes, calling an internal-looking factory, or replaying a
  formerly genuine object after return must authorize nothing.
- Refusal must occur before the process boundary, materializer or
  descriptor-bound effect issuer is reached.
- Keep refusal text fixed, bounded and free of paths, raw stored content,
  hostile caller values and operating-system exception text.
- Preserve the accepted order:

  ```text
  T2 lock → T3–T5 admission → T6 durable start → T7 admitted → T8 running
  → T9 work/effects → T10a–T12 terminal publications → T17 lock release
  ```

- Preserve the derived release evidence, terminal release-before-completion
  order, interruption behavior, quiescence behavior and standing operational
  refusals from the submitted handback.

Do not solve this by documenting that underscore-prefixed Python attributes are
private, by adding another boolean, by checking only object type or matching
values, by trusting callback lifetime, or by leaving an importable bearer token
whose possession alone is accepted indefinitely. Do not add a second lifecycle
reader or duplicate the reservation state machine: reuse the authoritative
record and ledger validation paths.

## Required failing-before regressions

Add public behavioral tests first and run them unchanged against the submitted
tree. Preserve exact failing-before output for at least:

1. importing/reading `_PERMIT_GRANT` and constructing an accepted granted permit
   without `ledger.begin()`;
2. directly calling `_grant_permit` without a durable start;
3. retaining a genuine permit from a successful `run_harness()`, then driving
   an armed executor with the original now-closed integration;
4. the same replay with a newly constructed integration whose fields equal the
   completed run;
5. replay after the stored run is completed;
6. replay after an attributed recovery;
7. execution while the integration exists but its session is absent or its lock
   has been released;
8. execution against a missing, unreadable, wrong-participant, wrong-reservation
   or non-running durable state; and
9. consuming the same live authority twice.

For each refusal, assert that the recording process boundary has no calls and
that no descriptor-bound effect or materialization was reached. Where durable
fixture state exists, assert its bytes or parsed state remain unchanged.

Retain positive behavioral coverage proving that the real
`execute_under_reservation()` composition reaches the executor exactly once
between T8 and T10a, while the lock is held and the stored run is in progress,
then publishes both terminal halves before releasing the lock. The remediation
must not pass by refusing every execution.

## Negative controls and sensitivity

Provide focused single-point reversals that independently remove at least:

- the live-session requirement;
- the held-lock requirement;
- the in-progress stored-run requirement;
- the stored reservation/participant binding;
- the current `running` reservation-state requirement; and
- one-shot consumption or revocation.

Each reversal must make a named public regression fail with tests otherwise
unchanged. Include a control for whichever mechanism prevents module-attribute
construction from becoming accepted authority. If Python cannot make object
construction literally impossible, state that accurately and prove instead
that any reconstructed object lacks the live, one-shot state needed by the
executor. Do not claim language-level secrecy that Python does not provide.

## Contract and decision boundaries

r6 §5.7 already assigns T7 and T8 to the **executor, root**. The harness
executor's `run_harness()` orchestration is consistent with that recorded actor;
do not move those writes out of band or reopen their ownership as an unresolved
question in this pass.

D1 and D2 remain proposed and unapproved. V6 remains unconfirmed. Do not edit r6
as though either proposal were accepted, broaden the syscall or descriptor
surface, or claim either deviation closed.

The six non-harness wrappers remain unwired under LAB-R6. Do not wire or invoke
them in this assignment; that requires separately authorized provisioning and
rollout. Preserve their fail-closed integration interfaces and tests.

## Preserved scope and gates

- `plan.is_executable` remains `False`.
- `reservation.REAL_EXECUTION_REFUSAL` remains in force.
- All twelve target facts remain unconfirmed.
- C-7 remains unresolved and EH-R16-1 remains Open.
- Package 5.0 remains not ready, P5.0-R5 remains Blocking and OD-62 remains
  Open.
- No production bot, web, database, migration or Foundry behavior changes.
- No gate, finding or digest is approved by the implementing agent.

## Test and artifact procedure

1. Add and run the failing-before regressions against the submitted tree.
2. Implement the smallest cohesive live-authority correction.
3. Run the narrow new regressions, the existing call-graph/integration tests,
   the focused five-module set, structural no-execution tests and the complete
   `tests/phase_5_0_evidence` suite locally with `TEST_DATABASE_URL` unset.
4. Run locally available bot, web and Foundry suites only within the active
   restriction. Run suites serially. Report every skip as unverified and do not
   mistake the database-disabled 1,362-skip web result for the 80-skip
   database-enabled baseline.
5. Run scoped `compileall`, `git diff --check` and configured formatter, linter
   and type checks if present. Do not install missing tools or dependencies;
   report them as unavailable rather than passed.
6. If a covered source changes, regenerate the concrete plan and review manifest
   only through the non-executing CLI. Generate at least twice, compare bytes,
   independently recompute every covered-source hash and report the new digest
   as **review input only**. Never pass it to `--execute`.
7. Inspect the final diff for secret material, unrelated changes, unsafe
   refusal text, generated debris and any bypass of the standing execution
   refusal.

## Explicit prohibitions

Do not perform SSH, synchronization, host inspection, preflight, provisioning,
permission or group changes, `systemd-tmpfiles`, creation or modification of
`/run`, `/var/lib` or `/etc` objects, database operations, destructive drills,
service changes, dependency installation, generated-vector execution,
`--execute`, real process boundary or materializer use, migration, deployment,
cutover, commit, push, reset, history rewrite or bot restart. Do not read
credentials or secret files.

Do not mark V6, V8, V10 or any target fact confirmed. Do not close C-7,
EH-R16-1, LAB-R6, P5.0-R5, OD-62 or PR-20260914-LABI-R1-1 on the implementer's
authority; declare Package 5.0 ready; approve a digest; or claim operational
evidence.

## Handback and stop point

Return one dated remediation handback containing:

- the Blocking finding disposition and requirement-to-code/test traceability;
- the live authority object graph and exact T2–T17 sequence before and after;
- why forged, retained, copied and replayed objects authorize nothing;
- how the executor establishes the live session, held lock, stored in-progress
  run, current reservation state and one-shot consumption without a second
  lifecycle reader;
- exact failing-before, passing-after and per-conjunct reversal evidence;
- the positive composition trace observed from durable files while work runs;
- files and interfaces changed;
- security, interruption and recovery analysis;
- generated-artifact reproduction and the review-only digest, if changed;
- exact commands, interpreters, results, skips and unavailable checks;
- rollback for repository-only changes;
- every unresolved gate, target fact and contract proposal; and
- focused questions for independent re-review.

Stop after the handback. The next checkpoint is independent Codex technical and
security re-review. No preflight, provisioning or execution follows
automatically.
