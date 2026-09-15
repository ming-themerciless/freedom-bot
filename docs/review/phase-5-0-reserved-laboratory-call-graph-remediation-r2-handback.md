# Claude handback — the executor's live, one-shot effect authority

Date: 2026-09-14. Authorization: **C-P5.0-LAB-I-R1**, continued.
Prompt answered: [reserved-laboratory call-graph remediation R2](phase-5-0-reserved-laboratory-call-graph-remediation-r2-claude-prompt.md).
Review answered: [Codex technical and security re-review](project-review-2026-09-14-reserved-laboratory-remediation.md).
Previous handback: [call-graph remediation](phase-5-0-reserved-laboratory-call-graph-remediation-handback.md).
Design basis: [runner contract r6](phase-5-0-reserved-laboratory-runner-contract-r6.md).
Contract delta still proposed, still not applied: [D1/D2 amendment](phase-5-0-reserved-laboratory-r6-d1-d2-proposed-amendment.md).

**Returned for independent Codex technical and security re-review. Nothing here
closes a finding or a gate.** C-7 remains unresolved, EH-R16-1 remains **Open**,
`plan.is_executable` remains **False**, `reservation.REAL_EXECUTION_REFUSAL`
remains in force, the twelve target facts remain unconfirmed, no item of the
r6 §7 delta is provisioned, Package 5.0 remains **not ready**, package-level
P5.0-R5 remains **Blocking**, OD-62 remains **Open**, LAB-R6 remains **Open**
and PR-20260914-LABI-R1-1 is **not closed on my authority**.

**New review-input digest:**
`4407c6882fbcf449df1f351ad222c6f774ca72624559427be335746e26598f36`, replacing
`f1190e4b44c85b3d3c1fc37dff83550e0ee7805b8e796146150d5f8d56d0f44f`. **It is
review input only. Do not pass it to `--execute`.**

---

## 1. Disposition of the Blocking finding

**PR-20260914-LABI-R1-1 — the executor did not require live authority.**
Accepted in full, in both reproductions, and I want to be explicit that the
previous pass's claim was wrong rather than merely incomplete. Its handback §2
said the permit was *"unforgeable"* because a caller outside `participants.py`
*"cannot construct a granted permit at all"*. That is not true in Python and the
review demonstrated it. Every statement of that claim in the tree has been
corrected rather than softened — `participants.py`'s module docstring and
`_PERMIT_GRANT` comment, `executor.ExecutingRunner.permit`'s comment, and the two
docstrings in `test_lab_call_graph.py` that repeated it.

| Reproduction | What it did | Why it no longer authorizes anything |
|---|---|---|
| **A — constructible** | read `participants._PERMIT_GRANT`, set `EffectPermit.grant` and `granted=True`, or call `participants._grant_permit` directly | both still work and are exercised as tests. The resulting permit has `issued is True` and `binds(...) is True`, and `consume()` refuses it: it is registered on no integration point, so it belongs to no invocation |
| **B — replayable** | retain the genuine permit a work callback received, then drive an armed executor after T12 and T17 | the authority is registered on the integration point for one `work` call and cleared in that call's `finally`. After the work returns the same object refuses, and so does the same object with the same session re-opened and the durable state untouched |

**What is not claimed.** No language-level secrecy. `_PERMIT_GRANT` is readable,
`_grant_permit` is callable, `EffectPermit` is constructible with any field
values, and the marker is kept only because it costs nothing and catches an
accidental `granted=True`. The property that closes the path is live state, and
§4 proves it by starting from objects built out of exactly those attributes.

### 1.1 Requirement → code → test

| Required behavior (prompt §Required behavior) | Code | Test |
|---|---|---|
| the first effect requires a **live**, exact protocol capability owned by the active invocation | `participants.ParticipantIntegration._issue_authority` / `._revoke_authority` / `._authority`; `participants.EffectPermit.consume`; `executor.ExecutingRunner._require_accounted_run` tail | `test_lab_live_authority.py::test_a_permit_built_from_the_module_attributes_authorizes_nothing`, `…::test_calling_the_grant_factory_directly_authorizes_nothing` |
| the exact integration owns an **open session** | `EffectPermit.consume`, conjunct 2 (`integration._session is not None` **and** `is self.session`) | `…::test_a_closed_session_inside_the_work_reaches_no_effect`, `…::test_a_reopened_session_inside_the_work_reaches_no_effect` |
| that session **still holds the cooperative lock** | `EffectPermit.consume`, conjunct 3, over `LaboratorySession.holds_lock` — the session's own open descriptor | `…::test_a_released_lock_inside_the_work_reaches_no_effect` |
| the stored run exists, is valid, is the harness, is bound to the exact reservation and is still `participant_started` | `EffectPermit._require_current_durable_state`, via `ParticipantRunLedger.read_run` | `…::test_an_absent_stored_run_inside_the_work_reaches_no_effect`, `…::test_an_unreadable_stored_run_inside_the_work_reaches_no_effect`, `…::test_a_wrong_participant_stored_run_reaches_no_effect`, `…::test_a_differently_bound_stored_run_reaches_no_effect`, `…::test_a_settled_stored_run_inside_the_work_reaches_no_effect` |
| the reservation record is in the exact T8 `running` state for that reservation | `EffectPermit._require_current_durable_state`, via `lifecycle_storage.check_reservation_history` | `…::test_a_reservation_that_is_not_running_reaches_no_effect` |
| the authority has **not previously been consumed** | `EffectPermit.consume`'s first conjunct plus `integration._authority = None` on success | `…::test_the_same_live_authority_cannot_be_consumed_twice` |
| a closed, never-opened, equivalent-but-distinct or wrong integration refuses | conjunct 1 (`self.issuer is not integration`, `integration._authority is not self`) | `…::test_a_retained_permit_refuses_against_its_own_closed_integration`, `…::test_a_retained_permit_refuses_against_an_equivalent_new_integration`, and `test_lab_call_graph.py::test_an_armed_executor_with_a_sentinel_session_reaches_no_effect` for `session=object()` |
| a completed, recovered, missing, unreadable or differently bound run refuses | as above | `…::test_a_retained_permit_refuses_after_the_stored_run_is_completed`, `…::test_a_retained_permit_refuses_after_an_attributed_recovery`, plus the five stored-run rows |
| authority is one-shot and **scoped to the synchronous `work` invocation** | the `try: work(permit) finally: self._revoke_authority()` in both `run()` and `run_harness()` | `…::test_a_retained_permit_refuses_once_its_own_invocation_has_returned` |
| refusal occurs **before** the boundary, materializer or effect issuer | `execute()` calls `_require_accounted_run()` on its first line, ahead of `_refuse_when_blocked()` and the step loop | every refusal test asserts `boundary.calls == []`, `materializer.requests == []` and `DescriptorBoundEffects._recorded == {}` |
| refusal text fixed, bounded and safe | the closed `AUTHORITY_*` sentences plus `PARTICIPANT_AUTHORITY_NOT_LIVE`; `raise … from None` in the executor | §6 |
| the accepted T2→T17 order preserved | unchanged in `run_harness` | `test_lab_live_authority.py::test_the_real_composition_reaches_the_armed_executor_exactly_once`, `test_lab_call_graph.py::test_the_composition_admits_starts_executes_then_publishes` |

---

## 2. The live authority object graph, and the exact sequence

### 2.1 What was there before

```text
EffectPermit  = frozen dataclass (participant, run_id, reservation_id, granted, grant)
              ── grant compared by identity with a readable module attribute
              ── no reference to anything; valid for ever

executor._require_accounted_run()
  isinstance(session, ParticipantIntegration)     ← a type
  permit.issued and permit.binds(...)             ← four values
  permit.participant is session.participant       ← a value
  session.reservation_id == self.reservation_id   ← a value
  → issue effects
```

Every conjunct is a statement about an object's contents. None of them reads the
lock, the ledger or the record, so all of them are equally true of a permit
built from module attributes and of a permit kept from a run that finished an
hour ago.

### 2.2 What is there now

```text
ParticipantIntegration
  ._session   : LaboratorySession | None     the open session, or nothing
  ._authority : EffectPermit    | None       the permit of the invocation
                                             running *now*, or nothing

EffectPermit  = frozen dataclass (…, issuer, session)
              ── issuer/session compared by IDENTITY, repr=False, compare=False
              ── carries no authority of its own; consume() asks the protocol

LaboratorySession.holds_lock                the holder's own open descriptor
ParticipantRunLedger.read_run(run_id)       the authoritative run reader
lifecycle_storage.check_reservation_history the authoritative reservation walk
```

`EffectPermit.consume(integration=…)`, in order, refusing with one fixed
sentence each:

| # | Conjunct | Read from |
|---|---|---|
| 1 | `integration` is a `ParticipantIntegration`, is **this permit's issuer**, and has **this permit** registered | `self.issuer`, `integration._authority` — identity, both |
| 2 | that integration owns an open session, and it is **the session this was issued over** | `integration._session`, `self.session` — identity |
| 3 | the session still holds the cooperative lock | `LaboratorySession.holds_lock`, i.e. its own `flock` descriptor |
| 4 | the stored run is present, parses and validates as a run history | `ParticipantRunLedger.read_run` |
| 5 | the stored start is **this participant's** | the same `StoredRun` |
| 6 | the stored start owns **this reservation** (equality, both ways) | the same `StoredRun` |
| 7 | the stored run is still `IN_PROGRESS` | the same `StoredRun` |
| 8 | the reservation record's **current** reservation is this one and its **current state** is `RUNNING` (harness only; the six own no reservation state — P9) | `check_reservation_history` over `ReservationRecord.read()` |
| ✓ | spend it: `integration._authority = None` | — |

**No second lifecycle reader and no second state machine.** Conjuncts 4–7 use the
reader every writer in this package already calls before it derives a
lifecycle-owned fact, and conjunct 8 uses the same walk `derive_lifecycle_history`
reads the current reservation and its state from. Nothing is re-implemented and
no rule is restated.

### 2.3 The sequence — before and after, T2 to T17

Unchanged, and deliberately so: the accepted call-graph repair and terminal
ordering are preserved exactly. **The only difference is the pair of lines
around T9.**

```text
ParticipantIntegration.run_harness(run_id, work, request, observed_by)
  ├─ _require_request_binding(request)        before the lock; a mismatch publishes nothing
  ├─ LaboratorySession.open()                 take the lock, or refuse       (T2)
  ├─ session.admit()                          re-seal → read → parse → order →
  │                                           validate → survey → decide     (T3–T5)
  ├─ ledger.begin(...)                        durable participant_started    (T6)
  ├─ record.admit_reservation(...)            durable `admitted`             (T7)
  ├─ record.start_running(...)                durable `running`              (T8)
  ├─ permit = _issue_authority(session, …)    ← NEW: registered on `self`
  ├─ try: work(permit)                        the CLI's closure              (T9)
  │     ├─ runner.accept_permit(permit)           the hand-off, value-checked
  │     ├─ runner.execute()
  │     │     └─ _require_accounted_run()
  │     │           └─ permit.consume(integration=session)  ← NEW: the live check
  │     │                 … then, and only then, the first effect
  │     └─ runner.run_observations(outcome, …).with_quiescence(q)
  │  finally: _revoke_authority()             ← NEW: T9 ends here, for everybody
  ├─ TerminalSequence.conclude(...)           §5.12 steps 0–3            (T10a–T12)
  └─ finally: session.close()                 release the lock, nowhere earlier (T17)
```

**Why the revocation is in a `finally` and not after the call.** An exception,
a `KeyboardInterrupt` and a normal return must all end the authority, because
all three end the invocation. The interrupted case is the interesting one: the
durable start stays unsettled and the record still says `running`, so every
*durable* conjunct still holds — and the authority is gone anyway.
`test_a_retained_permit_refuses_once_its_own_invocation_has_returned` is exactly
that scenario, and reversal **R11** is what shows the line is load-bearing.

### 2.4 Why forged, retained, copied and replayed objects authorize nothing

* **Forged from module attributes.** `issuer` and `session` default to `None`,
  and nothing a caller can write registers an object on an integration point:
  `_issue_authority` is the only assignment to `_authority` besides the two that
  clear it. Conjunct 1 refuses. (Reversal **R1** removes conjunct 1; the forged
  permits are then caught by conjunct 2 instead, and the two tests that reversal
  *does* break are named in §5. I state this rather than claim R1 alone catches
  them.)
* **Copied.** `EffectPermit` is frozen; a copy of its *data* has `issuer=None`
  unless the copier also copies the two references, and a copy that does carry
  them still fails conjunct 1, because `integration._authority` holds the
  original object and the comparison is `is`.
* **Retained past the call.** Revocation clears the registration; conjunct 1
  refuses.
* **Replayed with the state reconstructed.** Re-opening the integration point
  gives a *different* `LaboratorySession`, so conjunct 2 refuses; putting the
  *same* session object back still fails conjunct 1.
* **Reconstructed wholesale, with the protocol genuinely performed.** If a caller
  takes the lock, publishes a durable `participant_started`, publishes `admitted`
  and `running` and then issues effects, it has not bypassed the protocol — it
  has executed it. That is the correct outcome and it is stated here so the
  boundary of the claim is visible: the guard establishes that the protocol state
  is live, not that any particular source file called it.

---

## 3. Files and interfaces

### Added

| File | Lines | What it is |
|---|---|---|
| `tests/phase_5_0_evidence/test_lab_live_authority.py` | 846 | the PR-20260914-LABI-R1-2 regression set — 20 public behavioral tests, 16 of which fail against the submitted tree |

### Changed — production

| File | Change |
|---|---|
| `tools/phase_5_0_evidence/execution/participants.py` | `PARTICIPANT_AUTHORITY_NOT_LIVE` added to the closed refusal vocabulary; the eight fixed `AUTHORITY_*` sentences and `AUTHORITY_REFUSALS`; `ParticipantRefused.detail`; `EffectPermit.issuer` / `.session` / `.consume()` / `._require_current_durable_state()`; `_grant_permit` takes the two references, both defaulting to `None`; `ParticipantIntegration._authority`, `._issue_authority()`, `._revoke_authority()`; `run()` and `run_harness()` wrap `work(permit)` in `try/finally`; module docstring, `_PERMIT_GRANT` comment and `EffectPermit` docstring corrected to withdraw the secrecy claim |
| `tools/phase_5_0_evidence/execution/executor.py` | `_require_accounted_run` gains the `permit.consume(integration=self.session)` conjunct, wrapped into `ExecutorRefused … from None`; `ParticipantRefused` imported; the `permit` field comment corrected |

### Changed — tests

`test_lab_call_graph.py` — two docstrings only, no assertion changed:
`_issued_permit` and `test_a_permit_cannot_be_constructed_granted` each said the
permit could not be constructed. Both now say what they actually prove and point
at the module that proves the rest. The 21 tests in that file are unchanged and
still pass.

### Changed — generated artifacts

`docs/review/phase-5-0-evidence-harness-review-manifest.json` and
`docs/review/phase-5-0-evidence-harness-concrete-plan.md`, regenerated through
the non-executing CLI. See §7.

### Interfaces a reviewer should read first

* `participants.EffectPermit.consume` — the eight conjuncts, each with one fixed
  refusal;
* `participants.EffectPermit._require_current_durable_state` — the two
  authoritative readers, called rather than reimplemented;
* `participants.ParticipantIntegration._issue_authority` / `_revoke_authority`
  and the two `try/finally` blocks around `work(permit)`;
* `executor.ExecutingRunner._require_accounted_run` — the three value conjuncts,
  then the one that is about now.

---

## 4. Failing-before and passing-after

### Failing-before — the regression set against the submitted tree

`test_lab_live_authority.py` was written first and run unchanged against the
submitted tree. Exact output, `/opt/discord-bots/venv-web/bin/python -m pytest -q
tests/phase_5_0_evidence/test_lab_live_authority.py`, `TEST_DATABASE_URL` unset:

```text
FAILED …::test_a_permit_built_from_the_module_attributes_authorizes_nothing
FAILED …::test_calling_the_grant_factory_directly_authorizes_nothing
FAILED …::test_a_retained_permit_refuses_against_its_own_closed_integration
FAILED …::test_a_retained_permit_refuses_against_an_equivalent_new_integration
FAILED …::test_a_retained_permit_refuses_after_the_stored_run_is_completed
FAILED …::test_a_retained_permit_refuses_after_an_attributed_recovery
FAILED …::test_a_retained_permit_refuses_once_its_own_invocation_has_returned
FAILED …::test_a_closed_session_inside_the_work_reaches_no_effect
FAILED …::test_a_released_lock_inside_the_work_reaches_no_effect
FAILED …::test_an_absent_stored_run_inside_the_work_reaches_no_effect
FAILED …::test_an_unreadable_stored_run_inside_the_work_reaches_no_effect
FAILED …::test_a_wrong_participant_stored_run_reaches_no_effect
FAILED …::test_a_differently_bound_stored_run_reaches_no_effect
FAILED …::test_a_settled_stored_run_inside_the_work_reaches_no_effect
FAILED …::test_a_reservation_that_is_not_running_reaches_no_effect
FAILED …::test_the_same_live_authority_cannot_be_consumed_twice
16 failed, 3 passed in 0.69s
```

Every one of the sixteen fails the same way —
`Failed: DID NOT RAISE <class '…executor.ExecutorRefused'>` — because the
submitted guard accepted the object it was handed. `test_a_reopened_session_…`
was added after that capture; reversal **R0** below reproduces the submitted
tree's behavior with the current tests and catches all seventeen.

The three that passed on the submitted tree are the ones that must:
`test_the_real_composition_reaches_the_armed_executor_exactly_once` (the
preserved positive path), `test_this_suite_builds_over_no_production_path` and
`test_the_standing_operational_gates_are_all_still_closed`.

### Passing-after

| Suite | Result |
|---|---|
| `tests/phase_5_0_evidence` (whole) | **2 206 passed, 0 skipped** (from 2 186) |
| the focused six | **479 passed** (from 459) |
| `test_lab_live_authority.py` (new) | **20 passed** |
| `test_lab_call_graph.py` | **21 passed** |
| `test_lab_integration.py` | **44 passed** |
| `test_lab_remediation.py` | **37 passed** |
| `test_lab_implementation.py` | **110 passed** |
| `test_no_execution.py` | **247 passed** |

### The positive composition, observed from durable files while the work runs

`test_the_real_composition_reaches_the_armed_executor_exactly_once` drives the
real `cli.execute_under_reservation` over a laboratory under `tmp_path`, with a
real `ExecutingRunner` holding a **real, armed `DescriptorBoundEffects`** — so
the live check is genuinely exercised on the success path, not skipped by an
unarmed issuer. At the moment `execute()` is entered it reads the laboratory's
own files and asserts:

* the stored run `RUN-LABI-R2` is `IN_PROGRESS` — T6 happened;
* the reservation record's last entry is `running` — T7 and T8 happened, T10a–T12
  have not;
* `integration._session.holds_lock` is `True` — the lock is held;
* the executor is entered exactly **once**.

It then asserts that the boundary really was reached (`boundary.calls` non-empty
— the remediation does not pass by refusing everything), that the terminal
publication happened, and that the lock is released afterwards
(`integration._session is None`).

---

## 5. Negative controls — twelve single-point reversals, every one caught

Each removes **exactly one** conjunct from `tools/`, leaves `tests/` untouched,
runs the focused six, and restores the file from a byte-identical backup. The
run is scripted so the restore cannot be forgotten, and the suite is green
before the first reversal and after the last (**479 passed** both times).

| # | What is removed | Focused-set failures | Which named regression |
|---|---|---|---|
| R0 | the whole live check — the submitted tree's behavior | **17** | every negative test in §4 plus `test_a_reopened_session_…` |
| R1 | the registration conjunct, so module-attribute construction is accepted | 2 | `test_a_retained_permit_refuses_once_its_own_invocation_has_returned`, `test_the_same_live_authority_cannot_be_consumed_twice` |
| R2 | the live-session requirement falls back to the session the permit remembers | 2 | `test_a_closed_session_inside_the_work_reaches_no_effect`, `test_a_reopened_session_inside_the_work_reaches_no_effect` |
| R3 | the session need not be **the** session the authority was issued over | 1 | `test_a_reopened_session_inside_the_work_reaches_no_effect` |
| R4 | the held-lock requirement | 1 | `test_a_released_lock_inside_the_work_reaches_no_effect` |
| R5 | the stored run need not be readable or valid | 2 | `test_an_absent_stored_run_…`, `test_an_unreadable_stored_run_…` |
| R6 | the stored run's participant is no longer compared | 1 | `test_a_wrong_participant_stored_run_reaches_no_effect` |
| R7 | the stored run's reservation binding is no longer compared | 1 | `test_a_differently_bound_stored_run_reaches_no_effect` |
| R8 | the stored run need not still be in progress | 1 | `test_a_settled_stored_run_inside_the_work_reaches_no_effect` |
| R9 | the reservation's current `running` state is no longer required | 1 | `test_a_reservation_that_is_not_running_reaches_no_effect` |
| R10 | one-shot consumption — the authority is not spent | 1 | `test_the_same_live_authority_cannot_be_consumed_twice` |
| R11 | revocation — the authority survives the work invocation | 1 | `test_a_retained_permit_refuses_once_its_own_invocation_has_returned` |

**The six the prompt names are R2/R3 (live session), R4 (held lock), R8 (in
progress), R6 and R7 (stored participant and reservation binding), R9 (current
running state) and R10/R11 (one-shot consumption and revocation). R1 is the
control for the mechanism that stops module-attribute construction becoming
accepted authority**, and I report honestly that R1 alone is caught by the two
one-shot/revocation regressions rather than by the forgery regressions: with the
registration gone, a forged permit is still refused one conjunct later, by the
live session. The forgery regressions therefore rest on R1 **and** R2 together,
which is what a defense-in-depth arrangement looks like when it is measured
rather than asserted.

**How each in-work reversal is reachable at all.** Six of the conjuncts can only
be isolated from *inside* one live invocation, because a dead invocation fails an
earlier conjunct and there is then nothing durable left to read. So the tests
perturb exactly one fact from inside the `work` callback — close the session,
release the lock, remove the run file, corrupt it, replace it with another
participant's or another reservation's valid start, publish an attributed
recovery for it, or quarantine the reservation — and then drive the armed
executor. Each also asserts that the run file's bytes are unchanged across the
refused execution.

---

## 6. Security, interruption and recovery analysis

**The refusal surface is fixed and closed.** `PARTICIPANT_AUTHORITY_NOT_LIVE`
joins the closed `PARTICIPANT_REFUSALS` vocabulary — `ParticipantRefused` still
raises on any classification outside it — and the eight detail sentences are
module constants collected in `AUTHORITY_REFUSALS`. None contains a path, a
stored byte, a run id, a reservation id, a caller-supplied value or an
operating-system message. The executor re-raises as `ExecutorRefused` with
`from None`, so no chained exception text escapes either. An absent run file and
an unreadable one both arrive as a parse refusal rather than an `OSError`, so
there is no path on which errno text reaches an operator-facing string.

**A refusal publishes nothing and reaches nothing.** `_require_accounted_run` is
`execute()`'s first statement, ahead of `_refuse_when_blocked` and the step loop.
Every negative test asserts `boundary.calls == []`, `materializer.requests == []`
and `DescriptorBoundEffects._recorded == {}` — no process was started, no file
was materialized and no descriptor-bound object was created — and the in-work
tests additionally assert the ledger bytes are unchanged.

**The window the check closes.** Previously the guard's conjuncts were all true
at construction time and stayed true for ever, so the interval between T8 and T9
was unguarded: anything that happened to the lock, the ledger or the record
after the start was published could not be seen. The check is now taken at the
last instruction before the first effect and reads the state under the current
hold, which is r6 §5.7's placement of T9 rather than an approximation of it.

**Interruption.** Unchanged in substance and strengthened in one respect. If the
work raises — `KeyboardInterrupt` included — no completion and no release is
published, the durable `participant_started` stands and blocks every successor
including the environment reset, and the lock is released by the `finally`. The
addition is that the authority is revoked on the same path, so the interrupted
run's permit cannot drive an executor afterwards even though its durable state
still looks exactly like a run in progress. That is
`test_a_retained_permit_refuses_once_its_own_invocation_has_returned`.

**Recovery.** Untouched. An interrupted run is settled by an operator's
attributed `participant_recovered` entry; the recovered id is never reused; and a
recovered run is `RECOVERED`, not `IN_PROGRESS`, so conjunct 7 refuses any later
attempt to issue effects under it. That is
`test_a_retained_permit_refuses_after_an_attributed_recovery` and
`test_a_settled_stored_run_inside_the_work_reaches_no_effect`.

**The six non-harness participants.** `run()` issues and revokes authority
through the same two methods, and `consume()` skips conjunct 8 for them because
r6 §5.11.1's P9 gives them no reservation state to be in. They remain unwired
(LAB-R6) and their work is still injected only by tests over `tmp_path`.

**Residual, stated.** The lock's holder is compared with the reservation id and
not with the identity of the process holding it — unchanged from the previous
handback and not addressed here. The six participants' completion conditions are
still injected and attributable, and r6 §9.3's **I9** remains unperformed for all
five it names. The two external release observations are operator-stated, which
is what r6 §1.6 requires and is not a substitute for the preflight that would
establish them. And the guard establishes that the protocol state is live, not
which source file produced it — §2.4's last row says so explicitly.

---

## 7. Generated artifacts and the review-only digest

Two covered sources changed — `execution/executor.py` and
`execution/participants.py` — so both generated artifacts were regenerated
through the **non-executing** CLI (`--manifest-out`, `--render`; no `--execute`,
no `--confirm-target`).

* Generated **twice** after the final source state and compared byte for byte:
  identical (`sha256` of the manifest `4fb9295466…1ce661a`, of the plan
  `da881f873e…3d23e45c`), and the installed files are byte-identical to them.
  An earlier intermediate state was generated three times, also identical.
* `COVERED_SOURCES` read from `review_manifest.py`'s **syntax tree** — **43**
  paths, all under `tools/` — and the manifest's pinned path set equals it. No
  path added, none removed.
* All **43** hashes recomputed independently against the files on disk: **zero
  mismatches**. Exactly two entries differ from the previous manifest, and they
  are the two files this pass changed.
* `manifest_version` stays **12**; `evidence_schema_version` stays **3**.
* Dry run: `executable False`; `unresolved conflicts 3 (C-7)`; the unconfirmed
  facts are still the twelve.
* New digest:
  `4407c6882fbcf449df1f351ad222c6f774ca72624559427be335746e26598f36`.
  **Review input only. It must not be passed to `--execute`.**

---

## 8. Commands, interpreters and results

**Restricted local pass, `TEST_DATABASE_URL` unset**, as the authorization
requires. The canonical `oracle-test` interpreter
`/opt/freedom-blades/runtime/venv-web/bin/python` exists on this workstation and
**has no pytest** (verified again this pass), and `oracle-test` may not be
reached under C-P5.0-LAB-I-R1, so the same restricted-local exception the
accepted LAB-1 handbacks used applies: `/opt/discord-bots/venv-web/bin/python`
and `/opt/discord-bots/venv/bin/python`, both Python **3.12.3** with pytest
**8.4.2**, and node **v24.20.0**. Suites were run **serially**.

| Command | Result |
|---|---|
| `python -m pytest -q tests/phase_5_0_evidence/test_lab_live_authority.py` (submitted tree) | **16 failed, 3 passed** |
| `python -m pytest -q tests/phase_5_0_evidence` | **2 206 passed, 0 skipped** |
| `python -m pytest -q` over the focused six | **479 passed** |
| `python -m pytest -q tests/phase_5_0_evidence/test_lab_live_authority.py` | **20 passed** |
| `python -m pytest -q -rs tests/test_*.py` (bot) | **3 025 passed, 326 skipped** |
| `python -m pytest -q tests/web` (web) | **1 609 passed, 1 failed, 1 362 skipped** |
| `node --test foundry-module/tests/*.test.mjs` | **171 passed, 0 failed, 0 skipped** |
| `python -m compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` | succeeded |
| `git diff --check` | clean |
| `python3 .claude/hooks/test_guards.py` | **31 cases, 19 refused and 12 allowed, all passed** |
| `python -m tools.phase_5_0_evidence.execution.cli` (dry run) | `executable False`, `C-7`, twelve unconfirmed facts |
| `python -m tools.phase_5_0_evidence.execution.cli --execute …` with the new digest | **REFUSED, exit 4**, before the lock; `/run/laboratory.lock` and `/var/lib/freedom-blades` still absent |
| 12 single-point reversals, focused six each | every one caught — §5 |

**Every skip is unverified.** The database-enabled web baseline is **80**, not
1 362; the 1 362 figure is what an unset `TEST_DATABASE_URL` produces and the run
**still exits 0**. The bot suite's 326 are the same class. No figure here is
evidence about a database-enabled run.

**The one web failure is pre-existing and unrelated, and I verified it again
rather than citing the previous handback.**
`tests/web/test_p3_4_static_assets.py::test_the_discovery_enumerates_untracked_files_rather_than_directories`
fails on its own guard assertion — *"no untracked directory in this tree; this
test proves nothing"*. It requires the working tree to contain an untracked
**directory**; I confirmed there is none, and this change adds untracked
**files** inside already-tracked directories, so it can neither create nor
remove one. The bot suite runs on `/opt/discord-bots/venv/bin/python`, because
the web environment has no `discord` module.

**Checks not run, and why.** No formatter, linter or type checker is configured
in this repository or installed in either environment — `black`, `ruff`,
`flake8`, `mypy`, `pylint` and `isort` are all absent and there is no
`pyproject.toml`, `setup.cfg`, `tox.ini`, `.flake8`, `mypy.ini` or
`.pre-commit-config.yaml`. That is **unavailable, not a pass**. The bot, web and
Foundry suites were run on this workstation and **not** on `oracle-test`, which
this authorization excludes. No SSH, synchronization, host inspection,
preflight, provisioning, permission or group change, `systemd-tmpfiles`,
creation or modification of any `/run`, `/var/lib` or `/etc` object, database
operation, destructive drill, service change, dependency installation,
generated-vector execution, `--execute`, real boundary or materializer use,
migration, deployment, cutover, commit, push, reset, history rewrite or bot
restart was performed. No credential or secret file was read; the repository's
secrets guard refused one of my own diff-review commands because its pattern
named a secret-bearing path, and I re-ran the review without it rather than
routing around it.

**Working tree preserved.** `git status --short` went from 77 entries to 78;
the single new entry is `tests/phase_5_0_evidence/test_lab_live_authority.py`.
Every unrelated and reviewer-authored change is untouched, both Codex review
records included, and no generated debris was left in the repository — every
intermediate artifact was written to a scratch directory outside the tree.

---

## 9. Rollback

Repository changes only; nothing was deployed, migrated or provisioned.

1. Delete `tests/phase_5_0_evidence/test_lab_live_authority.py` and this
   handback, and remove this pass's section from `docs/review/Handover
   information`.
2. Revert the two production files §3 lists. Each also carries the previous
   passes' uncommitted C-P5.0-LAB-I and C-P5.0-LAB-I-R1 work, which must be
   preserved: revert only the hunks §3 attributes to this pass — in
   `participants.py` the `AUTHORITY_*` block, `ParticipantRefused.detail`,
   `EffectPermit.issuer`/`.session`/`.consume`/`._require_current_durable_state`,
   `_grant_permit`'s two new parameters, `_authority`/`_issue_authority`/
   `_revoke_authority` and the two `try/finally` blocks; in `executor.py` the
   `permit.consume` block and the `ParticipantRefused` import.
3. Restore the two corrected docstrings in `test_lab_call_graph.py` — but note
   that doing so restores a claim of Python-level secrecy that is false.
4. Regenerate the manifest and concrete plan through the non-executing CLI; the
   digest returns to
   `f1190e4b44c85b3d3c1fc37dff83550e0ee7805b8e796146150d5f8d56d0f44f`.
5. There is nothing else: no migration, no schema change, no configuration
   applied to any host, no service touched and no bot restart.

---

## 10. Unresolved gates, target facts and contract proposals

* **C-7** unresolved; **EH-R16-1** Open; **OD-62** Open; **P5.0-R5** Blocking;
  Package 5.0 **not ready**.
* **`plan.is_executable` False**; `reservation.REAL_EXECUTION_REFUSAL` in force;
  **all twelve target facts unconfirmed** — `interpreter_sha256`,
  `interpreter_real_path` and the ten `E7.*`.
* **V6 unconfirmed**; **V8** and **V10** unconfirmed; **D1 and D2 remain
  proposed**, r6 is unedited and neither deviation is closed.
* **LAB-R6 Open** — the six non-harness wrappers are unwired, no wrapper was
  weakened and no lock is created on demand.
* **PR-20260914-LABI-R1-1 is not closed here.** The finding's disposition is the
  reviewer's.
* No item of r6 §7's provisioning delta is provisioned; no digest is approved;
  no operational evidence is claimed.

---

## 11. Focused questions for independent re-review

1. **Is conjunct 8 the right owner's check?** The executor reads the reservation
   record to establish that it is in `running` for its own reservation. It is a
   read, not a write, and it goes through `check_reservation_history` rather than
   a second state machine — but it does put the reservation's state on the
   executor's critical path for the first time. If the intent is that the
   reservation's state is the integration point's business and not the executor's,
   the conjunct belongs in `run_harness` immediately before `work()` instead, and
   I would rather be told than choose.
2. **Is the boundary of the claim in §2.4's last row acceptable?** A caller that
   genuinely performs T2, T6, T7 and T8 and then issues effects is permitted,
   because the protocol state it created is real. The guard is about liveness,
   not about provenance. If the intended property is stronger — that only
   `cli.execute_under_reservation` may reach an armed executor — that is a
   different mechanism and a different authorization.
3. **R1's measured coverage.** The registration conjunct is caught by the
   one-shot and revocation regressions rather than by the forgery ones, because
   the live-session conjunct catches forged permits one step later. Is a
   defense-in-depth pair acceptable here, or should the forgery regressions be
   restructured so that R1 alone breaks one of them?
4. **The reservation's `admitted` and `running` entries** — carried forward
   unanswered from the previous handback. r6 §5.7 assigns T7 and T8 to the
   executor, root, and `run_harness` publishes them; if the intent is that a
   reservation is granted out of band by an operator before the harness runs,
   that is a different owner for two durable writes.
5. **D1 and D2** remain unanswered from two handbacks ago.

---

**Stop point.** The next checkpoint is independent Codex technical and security
re-review. No preflight, provisioning or execution follows automatically.
