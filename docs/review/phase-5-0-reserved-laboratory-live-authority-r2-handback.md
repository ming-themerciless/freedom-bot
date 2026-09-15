# Claude handback — one issuance and one spend per work invocation

Date: 2026-09-15. Authorization: **C-P5.0-LAB-I-R2**.
Prompt answered: [one-shot authority remediation R2](phase-5-0-reserved-laboratory-live-authority-r2-claude-prompt.md).
Review answered: [Codex live-authority re-review](project-review-2026-09-14-reserved-laboratory-live-authority.md).
Previous handback: [live-authority handback](phase-5-0-reserved-laboratory-call-graph-remediation-r2-handback.md).
Design basis: [runner contract r6](phase-5-0-reserved-laboratory-runner-contract-r6.md), unedited.

**Returned for independent Codex technical and security re-review. Nothing here
closes a finding or a gate.** PR-20260914-LABI-R2-1 is **not closed on my
authority**. C-7 remains unresolved, EH-R16-1 **Open**, `plan.is_executable`
**False**, `reservation.REAL_EXECUTION_REFUSAL` in force, all twelve target facts
unconfirmed, D1 and D2 proposed, V6 unconfirmed, LAB-R6 **Open**, Package 5.0
**not ready**, P5.0-R5 **Blocking** and OD-62 **Open**.

**New review-input digest:**
`fe90f546a1032277d81f1f1d0384ce1d3d0e889300c4f86db76a597ebea96892`, replacing
`4407c6882fbcf449df1f351ad222c6f774ca72624559427be335746e26598f36`. **Review
input only. Do not pass it to `--execute`.**

---

## 1. Disposition of the Blocking finding

**PR-20260914-LABI-R2-1 — accepted in full.** The previous handback's statements
that *"nothing a caller can write registers an object"* and that clearing
`_authority` made the capability *"once, ever"* were false, as the review says.
Both the one-shot state (`_authority`, cleared on consumption) and the issuing
path (`_issue_authority`, which assigned a new permit whenever called) lived on
the object graph the work callback holds. Both reproductions were run unchanged
against the submitted tree before anything was edited, and failed exactly as the
reviewer reported (§5.1).

**The correction, in one sentence.** Each `run()`/`run_harness()` call now owns
one `_WorkInvocation` record, held **only as a local variable of that call**;
issuance is its single `OPEN → ISSUED` transition, consumption its single
`ISSUED → SPENT` transition, the end of the work its `→ ENDED` transition, and
both issuance and consumption find the record through the invocation's stack
frame rather than through any attribute. §3 is the mechanism and §4 is the
precise limit of the claim — which is narrower than "one-shot" said without
qualification, and is stated as such rather than softened.

### 1.1 Requirement → code → test

All tests are in `tests/phase_5_0_evidence/test_lab_live_authority.py` unless
another file is named. "R-…" refers to §5.3's reversals.

| Required behavior (prompt) | Code (`execution/participants.py`) | Public regression | Reversal that fails it |
|---|---|---|---|
| one durable start authorizes at most one execution | `_WorkInvocation.spend`; `EffectPermit.consume` ends in `invocation.spend()` | `test_the_same_live_authority_cannot_be_consumed_twice`, `test_restoring_every_reachable_attribute_does_not_re_arm_a_spent_authority` | R10 |
| issuance is a single transition; a second attempt refuses before constructing or registering, **after** consumption | `_WorkInvocation.issue` checks `OPEN` before `_grant_permit` runs; `_issue_authority` writes `_authority` only on success | `test_the_live_invocation_cannot_issue_a_second_authority` (reproduction 1, see §5.2) | **R-issue** |
| … and **before** consumption | same | `test_a_second_issuance_before_consumption_refuses_and_the_first_is_spent_once` | **R-issue** |
| … for the six as well | `run()` wraps its work identically | `test_a_non_harness_invocation_issues_once_as_well` | **R-issue** |
| issuance refuses when invocation state is **absent** | `_issue_authority`: `_live_invocation(self) is None` | `test_issuance_outside_a_live_invocation_refuses_and_registers_nothing`, `test_issuance_bound_to_anything_but_the_live_invocation_refuses[another integration point]` | R-issue-absent |
| issuance refuses when invocation state is **wrong** before the first issue | `_WorkInvocation.issue`: session, run and reservation must be the record's | `test_a_first_issuance_bound_to_anything_but_its_invocation_refuses` (three rows) | R-issue-bind |
| consumption depends on the invocation's actual issued state, not on a caller-writable permit, `_authority`, matching values or a boolean | `consume`: live record found from the frame, `integration._authority is self and invocation.owns(self)`, then `spend()` | `test_the_live_registration_cannot_be_replaced_by_mutable_state` (reproduction 2, unchanged) | **R-own** |
| direct `_grant_permit()`, direct `_authority` assignment, copied values, retained permits, equivalent integrations authorize nothing | as above | reproduction 2; `test_a_permit_built_from_the_module_attributes_authorizes_nothing`; `test_calling_the_grant_factory_directly_authorizes_nothing`; `test_a_retained_permit_refuses_against_an_equivalent_new_integration`; the forged half of `test_issuance_outside_a_live_invocation_…` | R-own, R0 |
| registration integrity — a replaced registration cannot become, or displace, the issued authority | the registration half of the same conjunct | `test_a_replaced_registration_refuses_even_the_genuine_authority` (cleared; a bound constructed permit) | **R-reg** |
| the genuine authority remains consumable exactly once | — | `test_issuance_bound_to_anything_but_the_live_invocation_refuses` (each row reaches the plan once, then refuses), `test_a_second_issuance_before_consumption_…` | R10 (the refusal half) |
| return, exception and `KeyboardInterrupt` revoke it | `_revoke_authority(invocation)` in the `finally` around the work: `invocation.end()` and `_authority = None` | `test_the_end_of_the_work_revokes_the_authority_inside_the_invocation` — returned, returned something else, raised, interrupted | **R11** |
| exact integration owns the exact open session | `consume`, unchanged | `test_a_closed_session_inside_the_work_reaches_no_effect`, `test_a_reopened_session_inside_the_work_reaches_no_effect` | R2, R3 |
| that session still holds the lock | unchanged | `test_a_released_lock_inside_the_work_reaches_no_effect` | R4 |
| stored run present, valid, the harness's, bound to the reservation, in progress | `_require_current_durable_state`, unchanged, via `ParticipantRunLedger.read_run` | the five in-work stored-run tests | R5–R8 |
| current reservation is this one in T8 `running` | unchanged, via `check_reservation_history` | `test_a_reservation_that_is_not_running_reaches_no_effect` | R9 |
| exactly one armed executor between T8 and T10a, then both terminal publications before T17 | `run_harness` order unchanged | `test_the_real_composition_reaches_the_armed_executor_exactly_once`; `test_lab_call_graph.py::test_the_composition_admits_starts_executes_then_publishes` | — (positive controls) |
| refusal before the boundary, materializer and effect issuer | `execute()` still calls `_require_accounted_run()` first | every refusal asserts `boundary.calls == []`, `materializer.requests == []`, `DescriptorBoundEffects._recorded == {}`; in-work tests also assert the run file's bytes unchanged | — |
| fixed, bounded refusal text | five new module constants in `AUTHORITY_REFUSALS`; no format fields | §8 | — |

---

## 2. The authority object graph and the T2–T17 sequence

### 2.1 What the callback reaches — the reviewed object graph

A work callback holds the permit it is passed and whatever its closure captures.
In production (`cli.execute_under_reservation.work`) that is the runner, and
`ExecutingRunner.session` is the integration point; in both reproductions the
closure captures the integration point directly. Following ordinary attributes:

```text
EffectPermit      participant, run_id, reservation_id, granted, grant, issuer, session
  └ issuer ─────▶ ParticipantIntegration
                    participant, host, target_identity, author, at, layout,
                    reservation_id, quarantine, wait_for_lock, session_factory,
                    _session, _authority
                    run(), run_harness(), recover(), close(), _open(),
                    _issue_authority(), _revoke_authority(), _release_evidence(), …
                    └ _session ─▶ LaboratorySession
                                   _lock (HostLock: path, wait, _fd), _inventory,
                                   _record, _ledger; open(), close(), admit(),
                                   record, ledger, holds_lock
module attributes  _grant_permit, _PERMIT_GRANT, EffectPermit, _WorkInvocation (the class),
                   _live_invocation, _INVOCATION_CODES
```

**Before:** the one-shot state was `ParticipantIntegration._authority`, and the
issuing capability was `_issue_authority`. Both are in that graph.

**After:** the one-shot state is a `_WorkInvocation` **instance**, and no
attribute of anything above refers to it. The class is importable; an instance a
caller builds is a local of no invocation frame and owns nothing an executor
accepts.

### 2.2 T2 to T17, before and after

Everything outside T9 is unchanged — the accepted call-graph repair, derived
release evidence, T7/T8 publication and §5.12's order.

```text
run_harness(run_id, work, request, observed_by)
  ├─ _require_request_binding(request)                    before the lock
  ├─ session = _open()                                    T2
  ├─ session.admit()                                      T3–T5
  ├─ session.ledger.begin(...)                            T6
  ├─ _publish_reservation_entries(session)                T7, T8
  │
  │  BEFORE                                  AFTER
  │  permit = _issue_authority(…)            invocation = _WorkInvocation(self, session, run, reservation)  [local only]
  │    └ _authority = new permit, always     try:
  │  try:                                      permit = _issue_authority(session, …)
  │    work(permit)                              └ _live_invocation(self) ─frame─▶ invocation
  │      └ consume():                            └ invocation.issue(…)   OPEN → ISSUED, or refuse
  │          _authority is self …                └ _authority = permit   (only on success)
  │          … durable checks                  work(permit)                                        T9
  │          _authority = None                   └ consume():
  │  finally:                                        issuer is integration
  │    _revoke_authority()                           _live_invocation(integration) is not None
  │      └ _authority = None                         _authority is self and invocation.owns(self)
  │                                                  open session, same session, lock held
  │                                                  read_run …, check_reservation_history …
  │                                                  invocation.spend()     ISSUED → SPENT, or refuse
  │                                              finally:
  │                                                _revoke_authority(invocation)
  │                                                  └ invocation.end()     → ENDED
  │                                                  └ _authority = None
  ├─ _release_evidence(session, observations)             (derived, unchanged)
  ├─ TerminalSequence.conclude(...)                       T10a–T12
  └─ finally: close()                                     T17
```

`run()` for the six follows the same pattern with an empty reservation.

---

## 3. The two transitions, and why replacement no longer authorizes

### 3.1 The record

```text
OPEN ──issue──▶ ISSUED ──spend──▶ SPENT
  └──────────────┴────────────────┴──end──▶ ENDED
```

`_WorkInvocation` has exactly three mutators. `issue` refuses unless `OPEN`,
then refuses unless the offered session, run and reservation are its own, and
only then calls `_grant_permit`. `spend` refuses unless `ISSUED`. `end` is
unconditional. Nothing moves a record backwards.

### 3.2 Finding it without an attribute

`_live_invocation(integration)` walks outward from its caller's frame to the
**nearest** frame whose code object **is** `ParticipantIntegration.run.__code__`
or `.run_harness.__code__` (identity, not equality — code objects compare equal
by structure) and whose `self` local **is** `integration`, and returns that
frame's `invocation` local. A nearest frame with no record yet returns `None`
rather than falling through to an older one. When the invocation returns, its
frame is gone; while it runs, the record is reachable from the stack and from no
attribute.

### 3.3 Each reviewed path, and what it meets now

| What the callback does, through the reviewed graph | Result | Evidence |
|---|---|---|
| calls `integration._issue_authority(session, …)` after the spend — **reproduction 1** | record is `SPENT`: refused **before** a permit is constructed; `_authority` unchanged | reproduction 1; R-issue |
| … before the spend | record is `ISSUED`: refused; the genuine authority still reaches the plan once | `test_a_second_issuance_before_…`; R-issue |
| calls `twin._issue_authority(...)` on an equal-looking integration point | no frame whose `self` is the twin: refused; twin registers nothing | `…[another integration point]` |
| builds a permit with `_grant_permit(issuer=integration, session=…)` and assigns it to `_authority` — **reproduction 2** | the record did not issue it: `owns()` is false, refused | reproduction 2; R-own |
| clears or replaces `_authority` and offers the genuine permit | the registration no longer names it: refused (fails closed) | `test_a_replaced_registration_…`; R-reg |
| constructs a `_WorkInvocation` of its own | it is the local of no invocation frame; `_live_invocation` never returns it | by construction (§3.2); R-issue-absent shows the frame lookup is load-bearing |
| writes **every** ordinary attribute of every package object reachable from the permit and the integration point back to its value at issuance — `object.__setattr__` included — then offers the spent permit | the record is not among them: refused | `test_restoring_every_reachable_attribute_does_not_re_arm_a_spent_authority`; R10 |
| retains the permit past the work's end, while `run_harness` is still on the stack and every durable conjunct still holds | record is `ENDED` and the registration cleared: refused | `test_the_end_of_the_work_revokes_…` (four endings); R11 |
| retains the permit past `run_harness`'s return | no invocation frame: refused | the five pre-existing retained-permit tests |
| calls `_revoke_authority(some_record)` | ends that record and clears the registration — can only remove authority | by construction |
| calls `integration.run_harness(...)` again from inside the callback | `_open` refuses while `_session` is set; with `_session` cleared, `flock` on a new open file description contends with the held one; with the lock released, admission refuses on the unsettled run and the `running` record | **reasoned, not tested** — see question 5 |

---

## 4. The Python trust boundary, stated precisely

**Inside one CPython interpreter there is no security boundary against the work
callback, and this correction does not create one.** The callback runs arbitrary
Python with this process's credentials. Specifically, any of these defeats any
in-interpreter guard, including this one:

* rebinding code: `ExecutingRunner._require_accounted_run`,
  `EffectPermit.consume`, `participants._live_invocation`,
  `_INVOCATION_CODES` or `_WorkInvocation.spend` — the call-graph suite's own
  negative control rebinds `_require_accounted_run` with `monkeypatch`;
* introspection: `sys._getframe`, `inspect.currentframe()`, a traceback's
  `tb_frame`, or `gc.get_referrers` reaches the record, and `object.__setattr__`
  on it resets its state. On CPython 3.13 and later, PEP 667 also makes
  `frame.f_locals` write-through, so the `invocation` local itself can be
  rebound. The deployed and tested interpreter is 3.12.3;
* `ctypes`, or simply calling `os` and `subprocess` directly and never touching
  the executor.

**What is claimed, and tested:** through **ordinary construction, method calls
and attribute assignment** — `object.__setattr__` on frozen and slotted objects
included — on every object reachable from the callback's arguments and from
`ExecutingRunner.session`, one invocation issues one authority and a consumer
spends it once. Underscores, frozen dataclasses, slots, the `_PERMIT_GRANT`
sentinel and object identity are **not** claimed as a boundary: the record is
protected by not being an attribute of anything in that graph, and the
full-graph write-back test is what checks that rather than asserting it.

**What an adversarial boundary would require.** Running the work in another
process, holding no descriptor on the lock, the record, the ledger or the
effects, with authority passed across that boundary. That is an architectural
change beyond this authorization, and I have not made it (question 1).

**Why stack discovery and not a closure or a context variable.** A closure only
helps if the executor calls it, and a callable taken from any attribute can be
replaced with one that always succeeds. A `contextvars.ContextVar` is set with an
ordinary method call. The activation record is the one place in the process that
belongs to the invocation, exists exactly as long as it does, and is not an
attribute of anything. Two consequences follow. A consumer running on another
thread, which does not have the invocation on its stack, is refused. And the
mechanism is CPython-specific, because it relies on `sys._getframe`.

---

## 5. Evidence

### 5.1 Failing-before — the two reproductions, verbatim, against the submitted tree

Run **before any edit**, with the reviewer's exact selection. Participants
`sha256 10dc7b2b…`, executor `1aee571c…`, test module `b38dde7c…`.

```text
$ env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs \
    tests/phase_5_0_evidence/test_lab_live_authority.py \
    -k 'live_invocation_cannot_issue or live_registration_cannot_be_replaced'
E           Failed: DID NOT RAISE <class 'tools.phase_5_0_evidence.execution.executor.ExecutorRefused'>
E           Failed: DID NOT RAISE <class 'tools.phase_5_0_evidence.execution.executor.ExecutorRefused'>
2 failed, 20 deselected in 0.22s
```

### 5.2 The one edit to a reproduction, and why

**Reproduction 2 is byte-for-byte unchanged.** **Reproduction 1 has one edit**,
and it is forced by the prompt's own requirement that *"a second issuance attempt
refuses"*. The reviewer's body called `_issue_authority()` and then drove an
executor with what it returned. A refusal at issuance means there is no return
value, and an exception raised inside `work` propagates out of `run_harness` and
fails the test. The attack is unchanged — the same call with the same arguments,
after the genuine permit was spent. The edit wraps that call in
`pytest.raises(ParticipantRefused)`, asserts the classification and that the
registration is untouched, and still drives a second armed executor under the
same start, now with the only permit the callback holds. That executor still
reaches nothing. The purpose is unchanged, and so is the name. I did not
deselect it, and it fails on the submitted tree with
`DID NOT RAISE ParticipantRefused` (§5.3, R0). **Question 3** asks whether this
edit is acceptable.

### 5.3 The new regressions against the submitted tree

The new and edited tests were written next and run against the still-unmodified
`tools/`:

```text
$ env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs \
    tests/phase_5_0_evidence/test_lab_live_authority.py
10 failed, 26 passed in 1.07s
```

Every failure was `Failed: DID NOT RAISE`, on `ParticipantRefused` or
`ExecutorRefused`:

* `test_the_live_invocation_cannot_issue_a_second_authority` (edited)
* `test_the_live_registration_cannot_be_replaced_by_mutable_state` (unchanged)
* `test_issuance_outside_a_live_invocation_refuses_and_registers_nothing`
* `test_issuance_bound_to_anything_but_the_live_invocation_refuses` × 4
* `test_a_second_issuance_before_consumption_refuses_and_the_first_is_spent_once`
* `test_restoring_every_reachable_attribute_does_not_re_arm_a_spent_authority`
* `test_a_non_harness_invocation_issues_once_as_well`

**Six new tests passed against the submitted tree, by design, and they are
controls rather than failing-before evidence:** the two
`test_a_replaced_registration_refuses_even_the_genuine_authority` rows (the
submitted registration check already refused them) and the four
`test_the_end_of_the_work_revokes_the_authority_inside_the_invocation` rows (the
submitted revocation already cleared the registration). What they show is
measured by R-reg and R11 below. **The three
`test_a_first_issuance_bound_to_anything_but_its_invocation_refuses` rows were
added afterwards** to cover R-issue-bind. On the submitted tree they fail with
`AttributeError` — the record class does not exist there — not with a behavioral
`DID NOT RAISE`, and I report them that way.

### 5.4 Passing-after, on the submitted tree

Restricted local pass, `TEST_DATABASE_URL` unset, run serially.

| Command (interpreter `/opt/discord-bots/venv-web/bin/python` unless stated) | Result |
|---|---|
| the two reproductions, reviewer's `-k` selection | **2 passed**, 37 deselected |
| `test_lab_live_authority.py` | **39 passed** (22 → 39) |
| `test_lab_live_authority.py` + `test_lab_call_graph.py` | **57 passed** (before the three record rows) |
| the focused six: live authority, call graph, integration, remediation, implementation, no-execution | **498 passed** |
| `test_no_execution.py` | **247 passed** |
| `tests/phase_5_0_evidence` | **2 225 passed, 0 skipped** |
| `tests/phase_5_0_evidence` under `/opt/freedom-blades/runtime/venv-web/bin/python` (pytest 9.1.1) | **2 225 passed, 0 skipped**, 2 `PytestConfigWarning`s (unknown `asyncio_default_fixture_loop_scope`; that venv lacks the plugin) |
| bot: `/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py` | **3 025 passed, 326 skipped**, 1 warning |
| web: `python -m pytest -q -rs tests/web` | **1 609 passed, 1 failed, 1 362 skipped** |
| `node --test foundry-module/tests/*.test.mjs` | **171 passed, 0 failed, 0 skipped** |
| `python3 .claude/hooks/test_guards.py` | **31 cases, all passed** |
| `python -m compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` | succeeded |
| `git diff --check`; `git diff --no-index --check` on the two untracked changed files | clean |

**Every skip is unverified.** Every bot and web skip reason is
`TEST_DATABASE_URL is not configured …`. The database-enabled web baseline is
**80** skips, not 1 362, and the run **still exits 0** without the variable. No
figure here is PostgreSQL evidence.

**The web failure is pre-existing and unrelated, re-demonstrated now.**
`tests/web/test_p3_4_static_assets.py::test_the_discovery_enumerates_untracked_files_rather_than_directories`
fails on its own guard, *"no untracked directory in this tree; this test proves
nothing"*, and `git status --short` shows no untracked directory. The code, test
and artifact work created no new path in the working tree — `git status --short`
had 81 entries before it and after it. The only new path is this handback, one
untracked **file** in an already tracked directory, which brings the count to 82
and cannot create the untracked directory that test requires.

**The submitted evidence-suite total was not re-measured**, so I do not state a
before-and-after delta for the whole suite. The previous handback reported 2 206,
and the reviewer added two tests after it.

### 5.5 Single-point reversals

`reversals.py` (scratchpad, not in the tree) applies each edit to
`participants.py` only, runs the focused six **with tests unchanged**, restores
the file from the bytes read at start and verifies SHA-256 `430965c8…` after
every reversal. The baseline and final runs are **498 passed**, and a digest of
the six test files is identical before and after. Final run:

| # | Removed | Focused-six result | Named public regression(s) that fail |
|---|---|---|---|
| R0 | the whole correction — the submitted `participants.py` | 13 failed | the 10 in §5.3, plus the 3 record rows (`AttributeError`) |
| **R-issue** | **issuance-once**: re-issue allowed from `ISSUED`/`SPENT` | 3 failed | `test_the_live_invocation_cannot_issue_a_second_authority`, `test_a_second_issuance_before_consumption_…`, `test_a_non_harness_invocation_issues_once_as_well` |
| R-issue-absent | issuance without a live invocation falls back to a fresh record | 2 failed | `test_issuance_outside_a_live_invocation_…`, `…[another integration point]` |
| R-issue-bind | issuance stops comparing session, run and reservation | 3 failed | `test_a_first_issuance_bound_to_anything_but_its_invocation_refuses` × 3 |
| **R-own** | **invocation ownership**: registration alone, the submitted check | 1 failed | `test_the_live_registration_cannot_be_replaced_by_mutable_state` |
| R-reg | registration integrity: ownership alone | 2 failed | `test_a_replaced_registration_refuses_even_the_genuine_authority` × 2 |
| R-consume-absent | consumption without a live invocation falls back to a fresh record | **0 failed — not independently load-bearing** | none (see below) |
| R2 | live session falls back to the permit's session | 1 | `test_a_closed_session_inside_the_work_reaches_no_effect` |
| R3 | session need not be the one issued over | 1 | `test_a_reopened_session_inside_the_work_reaches_no_effect` |
| R4 | held lock | 1 | `test_a_released_lock_inside_the_work_reaches_no_effect` |
| R5 | stored run readable and valid | 2 | `test_an_absent_stored_run_…`, `test_an_unreadable_stored_run_…` — these fail with an `AttributeError` on `None`, not with a clean pass-through |
| R6 | stored participant | 1 | `test_a_wrong_participant_stored_run_reaches_no_effect` |
| R7 | stored reservation binding | 1 | `test_a_differently_bound_stored_run_reaches_no_effect` |
| R8 | stored run in progress | 1 | `test_a_settled_stored_run_inside_the_work_reaches_no_effect` |
| R9 | reservation currently `running` | 1 | `test_a_reservation_that_is_not_running_reaches_no_effect` |
| R10 | consumption: `spend` neither checks nor transitions | 8 | `test_the_same_live_authority_cannot_be_consumed_twice`, reproduction 1, the four `…bound_to_anything…` rows, `test_a_second_issuance_before_…`, `test_restoring_every_reachable_attribute_…` |
| R11 | revocation: `_revoke_authority` does nothing | 4 | `test_the_end_of_the_work_revokes_the_authority_inside_the_invocation` × 4 |

The two controls the prompt names are **R-issue** and **R-own**. Each fails its
named reproduction with that test unchanged. The previous submission's reversals
for session, lock, durable run, reservation binding and state, consumption and
revocation are all preserved (R2–R11).

**R-issue-bind was not caught on the first run**, because inside `run_harness`
only the method's own issuance ever sees an `OPEN` record. I added the three
record-level rows, which test the record's first transition directly, and re-ran
the whole script. The table above is that second run.

**R-consume-absent is not caught, and I am not adding coverage by contrivance.**
A fresh record owns no permit, so ownership refuses one conjunct later. The
absence check exists to refuse with its own sentence, `AUTHORITY_NO_LIVE_INVOCATION`,
and to avoid dereferencing `None`; it adds no coverage. Question 4.

**R11 moved to a new regression.** The earlier revocation test,
`test_a_retained_permit_refuses_once_its_own_invocation_has_returned`, now refuses
after `run_harness` returns because no invocation frame exists, whatever
revocation does. The new four-ending test offers the kept, **unspent** permit
while `run_harness` is still on the stack, the same session holds the lock, the
run is in progress and the record says `running` — immediately before T10a on
normal return, and inside the lock-releasing `close()` on the other three. That
is the only window in which revocation alone decides.

---

## 6. The positive composition, observed while the work runs

`test_the_real_composition_reaches_the_armed_executor_exactly_once` is unchanged
and passes. It drives the real `cli.execute_under_reservation` with a real
`ExecutingRunner` holding a real, **armed** `DescriptorBoundEffects`, so the live
check really runs on the success path, including the new frame lookup, ownership
and spend. At the moment `execute()` is entered, it reads the laboratory's own
files and observes:

* stored run `RUN-LABI-R2` is `IN_PROGRESS` — T6 happened;
* the record's last entry is `running` — T7 and T8 happened, T10a–T12 have not;
* `integration._session.holds_lock` is `True`;
* the executor is entered exactly **once**.

Afterwards the boundary was reached (`boundary.calls` non-empty), the terminal
publication exists, and the lock is released. The call-graph composition test is
unchanged and passes too. Separately, every `…bound_to_anything…` row and
`test_a_second_issuance_before_…` shows the genuine authority reaching the plan
exactly once after a refused issuance attempt.

---

## 7. Files and interfaces changed

| File | Change |
|---|---|
| `tools/phase_5_0_evidence/execution/participants.py` | **New:** `_InvocationState`; `_WorkInvocation` (`issue`, `owns`, `spend`, `end`); `_live_invocation`; `_INVOCATION_CODES`; five refusal sentences (`AUTHORITY_NO_LIVE_INVOCATION`, `AUTHORITY_ALREADY_ISSUED`, `AUTHORITY_ISSUANCE_NOT_BOUND`, `AUTHORITY_ALREADY_SPENT`, `AUTHORITY_INVOCATION_ENDED`), added to `AUTHORITY_REFUSALS` and `__all__`. **Changed:** `EffectPermit.consume` (live record, ownership + registration, `spend()` instead of clearing `_authority`); `_issue_authority` (refuses without a live `OPEN` record; registers only on success); `_revoke_authority(invocation)` now takes the record, ends it and clears the registration; `run()` and `run_harness()` create the record and revoke through it; `AUTHORITY_NOT_THIS_INVOCATION` text narrowed to what now reaches it; module docstring (new sections *One issuance, one spend* and *The trust boundary, stated precisely*), `EffectPermit` table, `_authority` comment and the `finally` comment corrected. Imports `enum`, `sys`. **Unchanged:** `_grant_permit`, `_PERMIT_GRANT`, `EffectPermit` fields, `_require_current_durable_state`, the T2–T17 order, `HarnessObservations`, release evidence |
| `tools/phase_5_0_evidence/execution/executor.py` | docstring only: `_require_accounted_run` said *"Consumption clears it"*; it now describes the invocation's transition and points to the stated limit. No code change |
| `tests/phase_5_0_evidence/test_lab_live_authority.py` | reproduction 1's single edit (§5.2); reproduction 2 unchanged; 17 new test nodes in section 3b; module docstring paragraph |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json`, `…-concrete-plan.md` | regenerated (§9) |
| `docs/review/Handover information` | a dated entry at the top |
| this handback | new |

Interfaces a reviewer should read first: `_WorkInvocation`, `_live_invocation`,
`EffectPermit.consume`, `ParticipantIntegration._issue_authority` /
`_revoke_authority`, and the two `try/finally` blocks. No public signature used
outside `participants.py` changed. `_revoke_authority` gained its one parameter,
and nothing outside `participants.py` calls it.

---

## 8. Security, interruption and recovery

**Refusal surface.** All five new sentences are module constants with no
format fields, so they carry no path, stored byte, run or reservation id, caller
value or operating-system text. The classification stays
`PARTICIPANT_AUTHORITY_NOT_LIVE` inside the closed vocabulary, and the executor
still re-raises `from None` with the fixed sentence. `ParticipantRefused` raised
by a refused issuance inside a callback propagates like any work exception: no
completion or release is published, the start stays unsettled, and the lock is
released.

**Order and effects.** `_require_accounted_run` is still `execute()`'s first
statement. Every new refusal asserts the boundary, materializer and descriptor
issuer are untouched; the in-work tests also assert the run file's bytes are
unchanged.

**Interruption.** `_revoke_authority(invocation)` is in the `finally` around
issuance and work, so return, exception and `KeyboardInterrupt` all end the
record and clear the registration before T10a. Durable behavior is unchanged: an
interrupted run leaves `participant_started` unsettled and blocks every
successor until an attributed recovery. An issuance that refuses inside the
`try` still passes through revocation.

**Recovery.** Untouched. A recovered run is `RECOVERED`, and the durable
conjunct refuses it as before.

**Threads.** A consumer on a thread without the invocation on its stack is
refused. That is intended: T9 is the synchronous work call.

**Residual, stated.** §4's boundary is the main one. The lock's holder is
still compared with the reservation id, not with a process identity; the six
participants' completion conditions are still injected, and I9 is unperformed;
the release's two external observations are still operator-stated.

---

## 9. Generated artifacts and the review-only digest

`participants.py` and `executor.py` are covered sources, so both artifacts were
regenerated through the **non-executing** CLI only:

```text
python -m tools.phase_5_0_evidence.execution.cli --manifest-out <scratch>/genN/manifest.json --render <scratch>/genN/plan.md
```

No `--execute`, no `--confirm-target`, no `--reviewed-digest`.

* Generations 1 and 2 are byte-identical: manifest `sha256 27e11439…73f8`,
  plan `5b8d7559…c9641`. Generation 1 was installed, and generation 3 is
  byte-identical to the installed files.
* `COVERED_SOURCES` was read from `review_manifest.py`'s syntax tree: **43** paths,
  all under `tools/`. The manifest's path set equals it, unchanged from the
  submitted manifest.
* All **43** hashes were recomputed from disk: **zero mismatches**. Exactly two
  entries differ from the submitted manifest — `execution/executor.py` and
  `execution/participants.py` — and every other manifest field is identical.
* `manifest_version` stays **12**; `evidence_schema_version` stays **3**.
* Dry-run output: `executable : False`; `unresolved conflicts : 3 (C-7)`; the
  twelve unconfirmed facts listed.
* Digest `fe90f546a1032277d81f1f1d0384ce1d3d0e889300c4f86db76a597ebea96892`.
  **Review input only. Never to be passed to `--execute`.**

---

## 10. Interpreters, and checks not run

**Interpreters.** `/opt/discord-bots/venv-web/bin/python` (Python 3.12.3, pytest
8.4.2) ran the reproductions, evidence, focused and web suites, matching the
reviewer's command. `/opt/discord-bots/venv/bin/python` (3.12.3, pytest 8.4.2,
discord 2.6.1) ran the bot suite. Node v24.20.0 ran Foundry. Both are
**available local runners, not canonical environment evidence**.

**New observation about this workstation.** Previous handbacks said the local
`/opt/freedom-blades/runtime/venv-web/bin/python` had no pytest. It now has
**pytest 9.1.1**, no `discord` module, and no asyncio plugin. I ran the evidence
suite with it once as a cross-check, **2 225 passed**. It is the canonical
*path* on this workstation, not `oracle-test`, and the result is not a
canonical-environment result.

**Not run, and why:**

* anything on `oracle-test`: SSH, synchronization and host inspection are
  prohibited;
* database-enabled suites: `TEST_DATABASE_URL` must stay unset;
* formatter, linter, type checker: none is configured (no `pyproject.toml`,
  `setup.cfg`, `tox.ini`, `.flake8`, `mypy.ini` or pre-commit config) and none of
  `black`, `ruff`, `flake8`, `mypy`, `pylint`, `isort` is installed.
  **Unavailable, not a pass**;
* `--execute`, even to confirm it refuses: the previous handback did that, but
  this prompt prohibits it. The standing gates are asserted instead by
  `test_the_standing_operational_gates_are_all_still_closed` (both LAB modules)
  and the dry run's `executable : False`.

No preflight, provisioning, permission or group change, `systemd-tmpfiles`,
`/run`, `/var/lib` or `/etc` object, database operation, destructive drill,
service change, dependency installation, generated-vector execution, real
boundary or materializer, migration, deployment, cutover, commit, push, reset,
history rewrite or bot restart. No credential or secret file was read. Every
scratch artifact is in the session scratchpad, outside the tree.

---

## 11. Rollback

Repository-only; nothing was deployed or applied.

1. Delete this handback and the top entry of `docs/review/Handover information`.
2. Restore `participants.py`, `executor.py` and `test_lab_live_authority.py` to
   their submitted bytes: `sha256 10dc7b2b…0fb9b`, `1aee571c…88a44` and
   `b38dde7c…cdd2`. All three still carry uncommitted earlier C-P5.0-LAB-I work.
   `participants.py` and the test module are untracked, so restore whole files
   rather than reverting hunks against `HEAD`.
3. Regenerate the manifest and plan through the non-executing CLI. The digest
   returns to `4407c688…8f36`, with manifest `sha256 4fb92954…ce661a` and plan
   `da881f87…23e45c`.

Doing so restores the two failing reproductions.

---

## 12. Unresolved gates, target facts and contract proposals

* **PR-20260914-LABI-R2-1** — not closed here; the disposition is the
  reviewer's.
* **C-7** unresolved; **EH-R16-1** Open; **OD-62** Open; **P5.0-R5** Blocking;
  Package 5.0 **not ready**.
* **`plan.is_executable` False**; `REAL_EXECUTION_REFUSAL` in force; **all twelve
  target facts unconfirmed** — `interpreter_sha256`, `interpreter_real_path`
  and the ten `E7.*`.
* **V6**, **V8** and **V10** unconfirmed; **D1 and D2 proposed**; r6 unedited.
* **LAB-R6 Open** — the six non-harness wrappers are unwired. `run()` gained the
  same transition, exercised only over `tmp_path`.
* No r6 §7 item provisioned, no digest approved, no operational evidence
  claimed.
* `status.md`, the decision and RAID registers and implementation-plan §20 are
  **not edited** by this pass; they record the assignment and are the
  maintainer's to update on disposition.

---

## 13. Focused questions for independent re-review

1. **Is §4's scoped claim the property required?** It holds against ordinary
   construction, calls and attribute writes on the callback's object graph, and
   explicitly not against code rebinding, frame or `gc` introspection, `ctypes`
   or direct `os` use. If the required property is adversarial isolation from
   the work callback, the smallest honest correction is a process boundary.
   That is a separate architectural authorization, and I would rather be told
   than choose.
2. **Is stack-frame discovery of the invocation record acceptable?** §4 gives
   the alternatives considered and why each is replaceable through the graph.
   The costs are CPython specificity and a refusal for consumers on other
   threads.
3. **Is reproduction 1's single edit (§5.2) acceptable as "unchanged in
   purpose"?** A refusal at issuance cannot return a replacement for the
   original body to hand on.
4. **R-consume-absent** is not independently load-bearing (§5.5). Keep it for
   its distinct refusal sentence, or fold it into the ownership conjunct?
5. **Re-entry.** A callback calling `run_harness` again on the same integration
   point is argued in §3.3, not tested. Should it get a public regression?
6. **The record-level rows** construct `_WorkInvocation` directly to reach its
   `OPEN` binding check, which the real flow never offers a wrong value. Is that
   acceptable coverage for *"issuance refuses … if invocation state is wrong"*,
   or should that check be removed as unreachable?

---

**Stop point.** The next checkpoint is independent Codex technical and security
re-review. No preflight, provisioning or execution follows automatically.
