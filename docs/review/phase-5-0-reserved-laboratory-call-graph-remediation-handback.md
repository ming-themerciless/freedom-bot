# Claude handback — the executable harness call graph

Date: 2026-09-14. Authorization: **C-P5.0-LAB-I-R1**, continued.
Review answered: [Codex technical and security re-review](project-review-2026-09-14-reserved-laboratory-remediation.md).
Previous handback: [implementation remediation](phase-5-0-reserved-laboratory-implementation-remediation-handback.md).
Design basis: [runner contract r6](phase-5-0-reserved-laboratory-runner-contract-r6.md).
Contract delta still proposed, still not applied: [D1/D2 amendment](phase-5-0-reserved-laboratory-r6-d1-d2-proposed-amendment.md).

**Returned for independent Codex technical and security re-review. Nothing here
closes a finding or a gate.** C-7 remains unresolved, EH-R16-1 remains **Open**,
`is_executable` remains **False**, the twelve target facts remain unconfirmed,
no item of the r6 §7 delta is provisioned, Package 5.0 remains **not ready**,
package-level P5.0-R5 remains **Blocking**, and OD-62 remains **Open**.

**New review-input digest:**
`f1190e4b44c85b3d3c1fc37dff83550e0ee7805b8e796146150d5f8d56d0f44f`, replacing
`eeafb24c18894835fb92ffbd4ae9e347a315260b4ba4c89e24faf3c76cb58fee`. **It is
review input only. Do not pass it to `--execute`.**

---

## 1. The finding, and what it was

**PR-20260914-LABI-R1-1 — Blocking.** The previous pass built
`execution/participants.py` and constructed a `ParticipantIntegration` in the
CLI's `--execute` branch. It then handed that object to
`ExecutingRunner(session=…)` and called `runner.execute()` beside it. No caller
invoked `run_harness()` or `run()`, so every production call to `session.admit()`
lived inside two unused methods; and `_require_accounted_run()` refused only when
`session is None` or `run_id` was empty, so `session=object()` satisfied it
exactly as the real integration did.

Constructing the objects is not calling the protocol. The armed executor could
have reached its first effect without taking the cooperative lock and without
durably publishing `participant_started`, once the independent standing gates
were resolved.

**The order now, and it is the order the re-review specified:**

```text
ParticipantIntegration.run_harness(run_id, work, request, observed_by)
  ├─ LaboratorySession.open()          take the lock, or refuse  (§5.7 T2)
  ├─ session.admit()                   re-seal → read → parse → order →
  │                                    validate → survey → decide  (T3–T5)
  ├─ ledger.begin(...)                 durable participant_started  (T6)
  ├─ record.admit_reservation(...)     durable `admitted`           (T7)
  ├─ record.start_running(...)         durable `running`            (T8)
  ├─ permit = _grant_permit(...)       the only granted permit there is
  ├─ work(permit)                      ← the CLI's closure          (T9)
  │     ├─ runner.accept_permit(permit)    the hand-off, checked
  │     ├─ runner.execute()                the reviewed plan
  │     └─ runner.run_observations(outcome, …).with_quiescence(q)
  ├─ TerminalSequence.conclude(...)    §5.12 steps 0–3              (T10a–T12)
  └─ session.close()                   release the lock, and nowhere earlier (T17)
```

---

## 2. The five required corrections, item by item

| # | Required correction (re-review §Finding) | Where it is implemented | Where it is tested |
|---|---|---|---|
| 1 | `run_harness()` owns the executable harness call, or an equivalently single typed orchestration path performs its complete sequence | `participants.ParticipantIntegration.run_harness`; `cli.execute_under_reservation` is the single orchestration path and `cli.main` calls nothing else | `test_lab_call_graph.py::test_the_orchestration_path_calls_the_participant_protocol`, `…::test_the_executor_is_driven_from_inside_the_work_closure`, `…::test_the_composition_admits_starts_executes_then_publishes` |
| 2 | Replace the non-`None` sentinel with an unforgeable run permit produced only after durable `begin()`, bound to the exact harness participant, run id and reservation id | `participants._PERMIT_GRANT` and `_grant_permit`; `EffectPermit.issued` / `.binds()`; `executor.ExecutingRunner.accept_permit` / `_validate_permit` / `_require_accounted_run` | `…::test_an_armed_executor_with_a_sentinel_session_reaches_no_effect`, `…::test_a_permit_cannot_be_constructed_granted`, `…::test_a_permit_for_another_run_does_not_account_for_this_one`, `…::test_only_the_permit_s_reservation_differs_and_it_still_refuses`, `…::test_the_permit_and_the_integration_point_name_one_participant`, `…::test_a_second_hand_off_refuses` |
| 3 | Feed the executor's actual cleanup/reload/residue outcome into the terminal release decision; publish release and completion before releasing the lock; exceptions and interruptions leave the durable start unsettled | `executor.ExecutingRunner.run_observations` and `cleanup_uncertain`; `participants.HarnessObservations` and `_release_evidence`; the `finally: self.close()` after `TerminalSequence.conclude` | `…::test_the_release_evidence_comes_from_the_cleanup_outcome`, `…::test_the_lock_holder_is_read_from_the_open_descriptor`, `…::test_an_unobserved_quiescence_quarantines_the_reservation`, `…::test_an_exception_in_the_work_leaves_the_durable_start_unsettled` |
| 4 | A public behavioural regression: an armed executor receives `session=object()` and a non-empty run id, and no effect is reached; plus a focused reversal that restores the presence-only check and makes it fail | `…::test_an_armed_executor_with_a_sentinel_session_reaches_no_effect`; the reversal is `…::test_the_presence_control_admits_the_sentinel_session` and reversal **R1** of §5 | both named at left |
| 5 | A CLI composition test that observes the actual admit → durable start → executor → terminal sequence rather than construction or source substrings | `…::test_the_composition_admits_starts_executes_then_publishes` drives `cli.execute_under_reservation` over a laboratory under `tmp_path` and reads the **durable files** at the moment the work is reached | also `…::test_the_executor_is_reached_only_through_the_protocol` |

### How the permit is unforgeable

`EffectPermit` carries a `grant` field compared by **identity** against a
module-private sentinel, excluded from equality and from `repr`.
`__post_init__` refuses `granted=True` without it, so a caller outside
`participants.py` cannot construct a granted permit at all — there is nothing for
the executor to detect, because there is nothing to detect. `_grant_permit` is
the only function that holds the sentinel and it is called in exactly two places,
both immediately after a `begin()` that returned `published`.

`binds()` compares the participant, the run id and the reservation id — equality
on all three, both ways, which is r6 §5.11.1's rule applied to the object that
carries the start's authority forward. `_require_accounted_run` additionally
requires `session` to be a real `ParticipantIntegration`, the permit's
participant to equal the session's, and the session's reservation to equal the
executor's.

### How the release evidence became derived

`HarnessObservations` is what the work returns. It carries **no reservation, no
target and no lock holder**: those three — the exact fields
`reservation.release()` compares against the request — are derived by
`_release_evidence` from the integration point's own reservation, its own target
and its own **open lock descriptor** (`LaboratorySession.holds_lock`, new). A run
that let go of the lock early reports no holder and quarantines.

The two fields the work does supply come from the executor's real result:
`run_observations` builds the `ResidueObservation` from `CleanupOutcome.residue`
and from whether cleanup could prove what it left behind, and
`configuration_restored` from `configuration_risk` and
`retained_recovery_inputs`. An uncertain cleanup yields an **incomplete** search
and a `None` restoration, not a false one — *"not observed"* and *"observed
false"* stay apart, which is PR-20260911-4's rule applied to the derivation.

`child_processes_ended` and `database_transactions_settled` are r6 §1.6's
external observations. No process in this package can make them, so they are
`None` unless a named observer states them, and `with_quiescence` reads them from
the **same** `Quiescence` object that gates the B3-dependent effects — one
observation, one reader.

### Why `admitted` and `running` are now published

r6 §5.7's **T7** and **T8**. Without them the release at the tail names a
reservation the stored history never admitted, and `conclude_reservation` refuses
with *"a run that was never admitted here is a run this record does not cover"* —
so §5.12 had **no reachable successful path**, which is R4-3's defect at a
different entry. The two entries are published durably, in the contract's order,
after this participant's own `participant_started` and before the first effect.
A failure of either returns a `reservation-entry-not-durable` refusal and leaves
the durable start exactly where it is, for an operator to recover.

---

## 3. Files and interfaces

### Added

| File | Lines | What it is |
|---|---|---|
| `tests/phase_5_0_evidence/test_lab_call_graph.py` | 946 | the PR-20260914-LABI-R1-1 regression set — behavioural, structural, and one reversal |

### Changed — production

| File | Change |
|---|---|
| `execution/participants.py` | `_PERMIT_GRANT`, `_grant_permit`; `EffectPermit.reservation_id` / `.grant` / `.issued` / `.binds()`; `HarnessObservations` and `HarnessWork`; `run_harness` reshaped — it takes the work and the request, derives `current_state`, publishes T7 and T8, derives the release evidence and returns `HarnessRun`; `_require_request_binding`, `_publish_reservation_entries`, `_release_evidence`; `PARTICIPANT_RESERVATION_NOT_DURABLE` added to the closed refusal vocabulary |
| `execution/executor.py` | `permit` field; `accept_permit`; `_validate_permit`; `_require_accounted_run` rewritten; `cleanup_uncertain` property; `run_observations`; `session` retyped to `ParticipantIntegration \| None` |
| `execution/host_lock.py` | `LaboratorySession.holds_lock` |
| `execution/cli.py` | `HarnessRunner`, the small consumer-owned protocol the orchestration needs; `execute_under_reservation` — the single orchestration path; `_quiescence`; the `--execute` branch calls it instead of driving the runner; the terminal result is reported beside the run's; `--reservation-owner`, `--requested-at`, `--deadline`, `--recovery-owner`, `--observed-by`, `--processes-ended`, `--transactions-settled`, `--transient-units-inactive` |

### Changed — tests

`test_lab_integration.py::test_an_armed_effect_issuer_refuses_an_unaccounted_run`
asserted that `session=object()` **satisfied** the guard. That assertion was the
finding, written down as a passing test, and it is inverted: the sentinel now
refuses, and the negative control for the unarmed issuer is unchanged.

### Interfaces a reviewer should read first

* `cli.execute_under_reservation` — a handful of statements; the whole orchestration;
* `participants.run_harness` — §5.6's order with nothing between the steps and
  §5.12's tail after them;
* `executor._require_accounted_run` — the three conjuncts, each with its own
  refusal;
* `executor.run_observations` — where the release's two derivable facts come from.

---

## 4. Failing-before, passing-after

The five conjuncts the re-review named did not exist in the submitted tree, so
the regression set does not merely fail there — most of it could not be written
against it. What can be demonstrated exactly, and was, is the behaviour the
submitted tree had. Reversal **R1** of §5 restores `_require_accounted_run`'s
presence-only body verbatim — `if self.session is None or not self.run_id:` — and
against that body:

```text
$ python -m pytest -q tests/phase_5_0_evidence/test_lab_call_graph.py \
                     tests/phase_5_0_evidence/test_lab_integration.py
FAILED …test_lab_call_graph.py::test_an_armed_executor_with_a_sentinel_session_reaches_no_effect
FAILED …test_lab_integration.py::test_an_armed_effect_issuer_refuses_an_unaccounted_run
2 failed, 63 passed
```

Reversal **R4** removes `runner.accept_permit(permit)` from the orchestration —
the submitted tree's shape, where the executor is driven without ever receiving a
permit — and the same two-test pair plus the composition test fail.

`test_the_presence_control_admits_the_sentinel_session` carries the same reversal
**in process**, so the demonstration is in the committed suite and not only in
this document: it monkeypatches the presence-only guard onto `ExecutingRunner`,
runs an armed executor with `session=object()`, and asserts that the boundary
**was** reached — which is the fail-open path, made visible.

### Passing-after

| Suite | Result |
|---|---|
| `tests/phase_5_0_evidence` (whole) | **2 186 passed, 0 skipped** (from 2 165) |
| `test_lab_call_graph.py` (new) | **21 passed** |
| `test_lab_integration.py` | **44 passed** |
| `test_lab_remediation.py` | **37 passed** |
| `test_lab_implementation.py` | **110 passed** |
| `test_no_execution.py` | **247 passed** |
| the focused set — the five above | **459 passed** |

---

## 5. Negative controls — thirteen single-point reversals, every one caught

Each removes **exactly one** load-bearing conjunct from `tools/`, with `tests/`
unchanged, runs the focused set, and restores the file. A conjunct nothing
catches is a conjunct that was not load-bearing, and **five of these were
uncovered on the first pass and the coverage was added rather than the finding
dropped** — the table is the result after that.

| # | What is removed | Focused-set failures |
|---|---|---|
| R1 | the executor's guard becomes presence-only again (the finding) | **2** |
| R2 | a granted permit may be constructed by anybody | 1 |
| R3 | the permit's own reservation is no longer compared | 1 |
| R4 | the executor is driven without the permit | **2** |
| R5 | the lock holder is asserted rather than read from the open descriptor | 1 |
| R6 | the request binding is no longer checked before the lock | 1 |
| R7 | the residue observation ignores the cleanup's result | 1 |
| R8 | the reservation's `admitted` / `running` entries are not published | 1 |
| R9 | the harness work's return value is no longer checked | 1 |
| R10 | an unmade quiescence observation becomes an observed one | 1 |
| R11 | the permit's participant is not compared with the session's | 1 |
| R12 | a second hand-off may be accepted | 1 |
| R13 | an interrupted work publishes its completion anyway | 1 |

The five that were initially missed were **R3**, **R5**, **R10**, **R11** and
**R12**. R3 and R11 were shadowed by a broader comparison beside them and are now
isolated by tests in which every other field agrees. R5 and R10 had no test at
all and now have one each. R12's original guard compared permit **values**, and
two permits for one run compare equal — so the branch could not be taken by any
input; it was replaced with a guard on the second **call**, which can be, and is
tested.

---

## 6. Security analysis

**The fail-open path is closed at the object graph, not at a comment.** The only
granted `EffectPermit` in existence is one `_grant_permit` produced after a
`begin()` that returned `published`, and the armed executor refuses without one.
There is no attribute a duck-typed object can carry to satisfy the guard and
none it can carry to trip it: every check is a type check or an identity
comparison.

**A refusal publishes nothing.** The standing gates —
`plan.is_executable is False` and the twelve unconfirmed target facts — refuse in
`ExecutingRunner.__post_init__`, which runs **before** the lock is taken, so
today's `--execute` writes no ledger entry, no reservation entry and no run
directory. Verified: the CLI refuses with the C-7 message and exit 4.
`_require_request_binding` likewise refuses before the lock.

**An interruption is unsettled, and unsettled blocks everything.** If the work
raises — `KeyboardInterrupt` included — no completion and no release is
published, the `finally` releases the lock, and the durable
`participant_started` stands. `test_an_exception_in_the_work_leaves_the_durable_start_unsettled`
asserts the run file is still in progress, that the record carries no `released`
entry, and that the survey reports the run unsettled, which refuses every
successor including the environment reset.

**An intermediate terminal state authorizes nothing.** Between §5.12's steps 2
and 3 the record says `released` and the harness's own run is still in progress;
`HarnessRun.released` is both halves or neither, and the CLI prints both lines.

**Fail-closed by default at every new option.** The three quiescence options
default to *not observed*, which gates every B3-dependent effect **and**
quarantines the reservation at release. `--observed-by` has no default: a residue
search with no observer is refused at the observation's own constructor.

**Residual, stated.** The six non-harness participants' completion conditions are
still injected and attributable; r6 §9.3's **I9** remains unperformed for all
five it names. The release's two external observations are operator-stated, which
is what r6 §1.6 requires and is not a substitute for the preflight that would
establish them. `reservation.release` compares the lock holder with the
reservation id; the identity of the *process* holding it is not established by
anything here.

---

## 7. What this pass did not do, named as such

**The six non-harness wrappers remain unwired — RAID item LAB-R6, unchanged.**
Nothing outside this repository calls them. The re-review agreed this must not be
closed here: the correct fail-closed wrapper refuses on an absent lock, so wiring
the six on an unprovisioned host would stop every suite, and closing the gap
needs a separately authorized, ordered provisioning-and-wiring rollout. No
wrapper was weakened and no lock is created on demand.

**D1 and D2 remain proposed.** r6 is unedited, V6 is unconfirmed, and neither
deviation is closed. The re-review said the amendment can be read after this
Blocking defect is remediated; it is unchanged since it was written.

**Nothing was executed, provisioned or inspected.** No SSH, synchronization, host
inspection, preflight, provisioning, permission or group change, `systemd-tmpfiles`,
creation of any `/run`, `/var/lib` or `/etc` object, database operation,
destructive drill, service change, dependency installation, generated-vector
execution, `--execute`, real boundary or materializer use, migration, deployment,
cutover, commit, push, reset, history rewrite or bot restart. No credential or
secret file was read. Both Codex review records were left untouched.

---

## 8. Generated artifacts and the review-only digest

* Generated **three times** through the non-executing CLI (`--manifest-out`,
  `--render`; no `--execute`, no `--confirm-target`): byte-identical, and
  byte-identical with the installed files under `docs/review/`.
* `COVERED_SOURCES` read from `review_manifest.py`'s **syntax tree** — **43**
  paths — and all 43 hashes recomputed independently against the files on disk:
  **zero mismatches**, and the manifest's pinned set equals the AST-read set.
* No path added and none removed. `manifest_version` stays **12**.
* `is_executable` **False**; `unresolved conflicts 3 (C-7)`; the unconfirmed
  facts are still the twelve.
* Digest:
  `f1190e4b44c85b3d3c1fc37dff83550e0ee7805b8e796146150d5f8d56d0f44f`.
  **Review input only. It must not be passed to `--execute`.**

---

## 9. Commands, interpreters and results

**Restricted local pass, `TEST_DATABASE_URL` unset**, as the authorization
requires. The canonical `oracle-test` interpreter
`/opt/freedom-blades/runtime/venv-web/bin/python` exists on this workstation and
**has no pytest**, and `oracle-test` may not be reached under C-P5.0-LAB-I-R1, so
the same restricted-local exception the accepted LAB-1 handbacks used applies:
`/opt/discord-bots/venv-web/bin/python` and `/opt/discord-bots/venv/bin/python`,
both Python **3.12.3** with pytest **8.4.2**, and node **v24.20.0**.

| Command | Result |
|---|---|
| `python -m pytest -q tests/phase_5_0_evidence` | **2 186 passed, 0 skipped** |
| `python -m pytest -q` over the focused five modules | **459 passed** |
| `python -m pytest -q tests/phase_5_0_evidence/test_lab_call_graph.py` | **21 passed** |
| `python -m pytest -q -rs tests/test_*.py` (bot) | **3 025 passed, 326 skipped** |
| `python -m pytest -q tests/web` (web) | **1 609 passed, 1 failed, 1 362 skipped** |
| `node --test foundry-module/tests/*.test.mjs` | **171 passed** |
| `python -m compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` | succeeded |
| `git diff --check` | clean |
| `python3 .claude/hooks/test_guards.py` | **31 cases, 19 refused and 12 allowed, all passed** |
| `python -m tools.phase_5_0_evidence.execution.cli` (dry run) | `executable False`, `C-7`, twelve unconfirmed facts |
| `python -m tools.phase_5_0_evidence.execution.cli --execute …` | **REFUSED, exit 4**, before the lock, nothing published |
| 13 single-point reversals, focused set each | every one caught — §5 |

**Every skip is unverified.** The database-enabled web baseline is **80**, not
1 362; the 1 362 figure is what an unset `TEST_DATABASE_URL` produces and the run
still exits 0. The bot suite's 326 are the same class.

**The one web failure is pre-existing and unrelated, and I verified it rather
than citing the earlier handback.**
`tests/web/test_p3_4_static_assets.py::test_the_discovery_enumerates_untracked_files_rather_than_directories`
fails on its own guard assertion — *"no untracked directory in this tree; this
test proves nothing"*. It requires the working tree to contain an untracked
**directory**; this change adds one untracked **file** inside an already-tracked
directory, so it can neither create nor remove one. The bot suite runs on
`/opt/discord-bots/venv/bin/python`, because the web environment has no `discord`
module.

**Checks not run, and why.** No formatter, linter or type checker is configured
in this repository or installed in either environment — `black`, `ruff`, `flake8`
and `mypy` are all absent and there is no configuration file for any of them.
That is **unavailable, not a pass**. The bot, web and Foundry suites were run on
this workstation and **not** on `oracle-test`, which this authorization excludes.

---

## 10. Rollback

Repository changes only; nothing was deployed, migrated or provisioned.

1. Delete `tests/phase_5_0_evidence/test_lab_call_graph.py` and this handback.
2. Revert the four production files §3 lists. Each also carries the previous
   pass's uncommitted C-P5.0-LAB-I and C-P5.0-LAB-I-R1 work, which must be
   preserved: revert only the hunks §3 attributes to this pass.
3. Restore `test_lab_integration.py::test_an_armed_effect_issuer_refuses_an_unaccounted_run`
   to its previous body — but note that doing so restores an assertion that the
   sentinel session is accepted, which is the finding.
4. Regenerate the manifest and concrete plan through the non-executing CLI; the
   digest returns to
   `eeafb24c18894835fb92ffbd4ae9e347a315260b4ba4c89e24faf3c76cb58fee`.
5. There is nothing else: no migration, no schema change, no configuration
   applied to any host, no service touched and no bot restart.

---

## 11. Questions for the maintainer

1. **The six wrappers.** LAB-R6 needs an ordered provisioning-and-wiring
   authorization — the lock inode and the lifecycle record first, then the
   wrappers — and it is not this assignment's to take.
2. **The reservation's `admitted` and `running` entries.** §5.7's T7 and T8 are
   published by `run_harness` because without them §5.12 has no reachable
   successful path. If the intent is that a reservation is granted out of band by
   an operator before the harness runs, that is a different owner for two durable
   writes and I would rather be told than infer it.
3. **The four reservation options and the three observation options.** They are
   the minimum `ReservationRequest` and `reservation.release()` require from a
   caller. If the reservation is to be read from a file or a record instead of
   from the command line, that is a maintainer's decision about where the
   reservation lives.
4. **D1 and D2** remain unanswered from the previous handback.
