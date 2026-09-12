# Claude handback — bounded remediation of the September 11 review

Date: 2026-09-11. Author: Claude. Returned to: Codex, for technical review.
Change record: C-P5.0-LAB-1. Prompt answered:
[`project-review-remediation-2026-09-11-claude-prompt.md`](project-review-remediation-2026-09-11-claude-prompt.md).
Review answered: [`project-review-2026-09-11.md`](project-review-2026-09-11.md).

**Nothing here is accepted, no finding is closed, no digest is approved for
execution and no host was touched.** Package 5.0 remains **not ready**, P5.0-R5
**Blocking**, OD-62 **Open**, EH-R16-1 **Open**, `is_executable=False`, and the
three C-7 cases remain **declared unresolved**. SSH, target inspection,
synchronization, provisioning, database operation, service mutation, credential
access, generated-vector execution, `--execute`, the armed real
boundary/materializer, VM expansion, migration `0014`, product implementation,
deployment, cutover and Package 5.1+ all remain unauthorized and none was
performed.

**No decision is requested of Peter by this pass.** The one decision the previous
handback submitted — the readiness-versus-implementation criterion split for
`JNL-47-RECOVERY-STATE` — is **withdrawn**, because PR-20260911-5 showed the
rationale for it was wrong. §1 gives the reasoning. Two things still await a
maintainer, and both follow Codex's technical review rather than preceding it:
the §7 provisioning and permission delta in the revised contract, and LAB-1's
classification.

New review-input digest, **not execution approval**:
`e6d42228f5ccc4fd5eebc0861bb97eec42bbf16705d1aa209de5464e194bdba1`. Do not pass
it to `--execute`. The previous digest
`bbb3854fbdffae00696544465f1cd7bbdf22ad18583056490a6735444800e4fa` is superseded
and was review input only.

---

## 0. Disposition table

| Finding | Class | Disposition | Where |
|---|---|---|---|
| **PR-20260911-1** — the descriptor proposal does not bind all dependent effects | Blocking | **Revised design submitted, not implemented.** The descriptor/baseline comparison is withdrawn as a remedy. Three protections replace it, mapped per effect, with the uncoverable rows named | [contract r2](phase-5-0-reserved-laboratory-runner-contract-r2.md) §1 |
| **PR-20260911-2** — independent recovery depends on an unspecified copy | Blocking | **Revised design submitted, not implemented.** An independent root-owned store outside `R`, captured and verified before the first mutation, with restart discovery, retention and disposal; mutation refused if the basis cannot be established | contract r2 §2, §8.2 |
| **PR-20260911-3** — admission cannot distinguish a released host from a crashed reservation | Blocking | **Repaired locally.** Admission requires explicit lifecycle evidence with no default; nine refusal paths and three positive controls | `tools/phase_5_0_evidence/reservation.py`; §2 below |
| **PR-20260911-4** — release treats an omitted residue check as a successful check | Important | **Repaired locally.** Residue is a three-state observation; `advance()` is audited on both granting transitions | `reservation.py`; §2 below |
| **PR-20260911-5** — the criterion split rests on the wrong creation order | Important | **Repaired locally, and the split is withdrawn.** The model runs C1-including-cleanup → C2 → C5 through an injected publication sink | `tools/phase_5_0_evidence/feasibility.py`; §1 below |
| **PR-20260911-6** — the proposed unprivileged lock cannot be created by its participants | Important | **Revised design submitted, not implemented.** The `O_EXCL` protocol is withdrawn; a provisioned persistent `flock` inode plus a separately protected lifecycle record, with the exact provisioning delta | contract r2 §5, §7 |
| **LAB-1** — a residue-only S-B reports no named operator recovery | Important (proposed; confirmed by the review) | **Still reported, still not repaired.** Exact fix and regression expectations submitted; the reproduction was not weakened and the ordering repair did not implement it by the back door | contract r2 §8; §1.4 below |

**Local fixes** are PR-20260911-3, -4 and -5. **Proposed privileged changes**, all
unbuilt, are PR-20260911-1, -2, -6 and LAB-1. The two groups are kept apart
everywhere below.

---

## 1. Evidence ordering — PR-20260911-5, corrected first

### 1.1 What was wrong

The submitted model published the journal, seal, `current` link, `.close`
manifest and a registry row and *then* injected the cleanup failure, so a cleanup
failure appeared to follow a legitimately created generation. The package says
the opposite: **C1** runs the probe **and its cleanup** and *"if the `finally`
cleanup does not complete, the run ends in state S-B of §2.13.2b and no later
step executes"*; **C2** validates while *"nothing has yet been written under
`…/journal`"*; **C5** is *"the first persistent artifact Algorithm C creates"*;
and `JNL-47` (package plan line 4159) requires **no journal file, no seal, no
symlink, no `.close` manifest and no database row** for both cleanup-failure
variants.

Reproduced before the change:

```
PR-20260911-5  cleanup-failure arrangement, direct invocation:
   artifacts = ('journal', 'seal', 'current', 'close')  registry_row_present = True
   classified status = failed
```

### 1.2 The ordering model

`feasibility.SEQUENCE` names the five steps once — `C0`, `C1-probe`,
`C1-cleanup`, `C2`, `C5` — and `run_sequence()` drives them with one injected
fault. It is a **minimum ordering model**, not a second coordinator: five steps,
one branch each, no artifact content, no digests, no chain, no filesystem and no
database.

Publication goes through an injected `PublicationSink` that records **every
attempt in order**, so *creation never reached* and *creation undone* are two
observations rather than one. Absence is never produced by passing a constant
`False`: `classify_recovery_experiment` now reads `generation_present` and
`database_row_present` off the sink.

After the change, same invocation:

```
PR-20260911-5  cleanup-failure arrangement, direct invocation:
   stopped_at = C1-cleanup  publication_attempted = ()
   artifacts = ()  registry_row_present = False
   classified status = passed
```

The full behaviour of the model:

| Injection | Stops at | Publication attempted | Artifacts | Row |
|---|---|---|---|---|
| stage-1 … stage-4 | `C2` | none | none | no |
| `cleanup` | `C1-cleanup` | none | none | no |
| none (positive control) | — | journal, seal, current, close, row | all four | yes |
| `Arrangement.UNORDERED`, any injection | — | all five, **before C1** | all four | yes |

### 1.3 Named regressions

In `tests/phase_5_0_evidence/test_feasibility.py`, **62** tests, up from 46:

* `test_no_failure_point_ever_reaches_the_publication_sink` — five points; asserts
  **both** that publication was not attempted and that no artifact or row exists;
* `test_the_misordered_control_publishes_early_and_is_classified_failed` — five
  points; the intentionally misordered control publishes at C5 before C1 and the
  same classifier fails it;
* `test_a_cleanup_failure_never_reaches_publication` — both §2.13.2b variants;
* `test_the_passing_control_does_reach_publication` — the control that makes an
  empty sink attributable;
* `test_the_misordered_control_leaves_a_generation_behind_a_failed_cleanup` — the
  negative control for the two absence clauses specifically;
* `test_the_cleanup_point_stops_the_run_inside_c1`,
  `test_a_probe_stage_failure_stops_the_run_before_the_first_artifact`,
  `test_the_sequence_is_the_approved_one_and_cleanup_belongs_to_c1`,
  `test_the_cleanup_point_is_not_a_probe_stage`; and
* `test_the_publication_sink_refuses_a_name_that_is_not_a_generation_artifact`.

**Retained, not weakened:** corrupt output refused rather than repaired
(`test_corrupt_producer_output_is_refused_rather_than_repaired`), missing output
reported missing (`test_a_missing_variant_is_reported_missing_and_never_assumed`),
duplicate input refused (`test_duplicate_producer_output_is_refused`), the
per-stage and per-omission failure injections, and the synthetic-target refusal.

### 1.4 The three C-7 dispositions, reassessed

| Case | Before | After | Why |
|---|---|---|---|
| `JNL-51-PROVENANCE-OMITTED` | meaningful; 4 records `PASSED` | **unchanged** | C0's ordering was already modelled correctly; it now runs on the shared sequence |
| `JNL-47-NO-GENERATION-ON-FAILURE` | 4 records; `cleanup` declared "not describable by R7-A" | **5 records, all `PASSED`** | the `cleanup` point *is* describable: it fails inside C1, before C2 and C5, exactly as a Stage-1 failure does. That claim is **withdrawn** |
| `JNL-47-RECOVERY-STATE` | `meaningful_without_product_code=False`; criterion split submitted | **`True`; split withdrawn**; 2 records still `FAILED` | both absence clauses are now modelled against the sink with a control that publishes. Six of seven clauses hold; the seventh is LAB-1 |

`dependent_work_to_stop()` is now empty. `feasibility.py`'s docstrings carry the
correction inline, and the superseded handback's §3.4 carries a dated correction
block with the historical submission preserved beneath it.

**Is a readiness/implementation evidence split still necessary? No.** All three
cases now sit on the ordinary feasibility-versus-product boundary this module has
always had: the local producer establishes that the rule is constructible and
falsifiable, and the product half is carried by a named Package 5.0
implementation acceptance test. That is not a criterion split and it changes no
package acceptance criterion. **Nothing in this tree assumes the withdrawn split,
and the package acceptance criteria are unchanged.**

**LAB-1 was not implemented by the back door.** The recovery records are still
`FAILED`, and they still fail on the named-operator-recovery clause alone.
`test_the_recovery_case_reproduces_lab_1` is unchanged and still asserts the
failure. The cleanup-mechanism change stays behind the design checkpoint.

**All three cases stay unresolved in the shipped execution plan** pending
independent producer review: `producer_artifact_reviewed=False` for each, the
external coverage column is empty, `resolves_c7` is `False`, and
`is_executable` is `False`.

---

## 2. The local decision API — PR-20260911-3 and PR-20260911-4

Implemented with **injected observations only**. No host lock, no durable writer
and no operational integration is built in this pass, and `reservation.py`
imports nothing from `execution/` or from the product tree.

### 2.1 Before and after, on the review's own reproductions

| Reproduction | Before | After |
|---|---|---|
| `admit()` with a readable free lock, a complete inventory and no lifecycle history | `admitted=True`, 0 refusals | `admitted=False`, refuses: the durable record could not be read |
| `release()` with residue never inspected | `RELEASED`, `unmade_observations() == ()` | `QUARANTINED`, `unmade_observations() == ('residue',)` |
| `advance(RUNNING → RELEASED)` with no decision | returned `RELEASED` | `PlanRefused`: the transition requires a `ReleaseOutcome` whose state is `RELEASED` |

The before-run was taken against the tree as submitted, before any edit; the
after-run against the tree submitted here. Both used
`/opt/discord-bots/venv-web/bin/python` with `TEST_DATABASE_URL` unset.

### 2.2 Admission — explicit lifecycle evidence

`admit()` takes a new keyword argument `lifecycle: LifecycleHistory` **with no
default**. A default would be a statement about the predecessor that nobody made,
which is the finding.

`PredecessorDisposition` is a closed vocabulary in which **three values admit** —
`VERIFIED_FIRST_USE`, `RELEASED`, `OPERATOR_RECOVERED` — and every other value,
including `UNKNOWN`, refuses. The five distinctions the prompt names:

| Situation | Disposition | Outcome |
|---|---|---|
| verified first use | `VERIFIED_FIRST_USE`, no predecessor named | admits |
| verified released predecessor | `RELEASED` **plus** a `ReleaseRecord` binding to this host, this target and that reservation | admits |
| missing / unreadable / incomplete history | `readable=False`, `complete=False`, or `UNKNOWN` | refuses |
| active or recovering predecessor | `ACTIVE`, `RECOVERING` | refuses |
| quarantine | `QUARANTINED`, and separately the `quarantine` argument | refuses |

**Nothing stands in for it**, and each substitute the review named is refused by
its own test: a free process lock (`test_a_crashed_predecessor_with_a_free_lock_refuses`),
a complete inventory (the same case carries one), an elapsed deadline
(`test_an_elapsed_deadline_does_not_stand_in_for_a_release`), and an absent
quarantine argument (`test_a_crash_after_effects_but_before_quarantine_publication_refuses`).

**Binding to the correct host and reservation** is checked three ways: a history
read for another host refuses, a release record naming another reservation
refuses, and a release record naming another host or target refuses.

**The durable record's ordering** is specified in
`reservation.DURABLE_RECORD_ORDERING`, five items. Its third is the one the
finding needs: a quarantine record is an addition on a failure path and never a
precondition, so a crash before quarantine publication leaves the record at
`RUNNING`, which refuses every successor. **Absence of a quarantine record is
never evidence that a predecessor ended.** The storage contract that would
implement it is contract r2 §5.4, unbuilt.

### 2.3 Release, recovery and audited transitions

**Residue.** `ResidueObservation` has three states: *not made* (or the field left
`None`), *observed empty* with an author and a completeness claim, and *observed
present*. Only the middle one contributes to a release. An incomplete search is
not an observed-empty one. A bare path tuple is **refused rather than coerced**,
so the shape that caused the finding cannot be constructed.

**Audited transitions.** `GUARDED_TRANSITIONS` names the two transitions that
grant something — to `ADMITTED` and to `RELEASED` — and each requires the
corresponding validated decision object, of the right type, carrying the right
result. `RUNNING`, `RECOVERING` and `QUARANTINED` stay unguarded deliberately:
each is a move towards caution, and a guard that made quarantine harder to reach
would point the wrong way. Supplying a decision for an unguarded target is itself
refused.

**Recovery stays separate from admission.** `recover()` is unchanged in shape: an
incomplete attestation quarantines, a complete attestation without release
evidence quarantines, and a complete one still has to satisfy `release()`.
Quarantine survives a lost lock and an elapsed deadline
(`test_quarantine_survives_a_lost_lock_and_an_elapsed_deadline`). A **completed
operator recovery admits a new reservation and never resumes the quarantined
one**: reusing the quarantined reservation's own id refuses, and an
unattributed recovery refuses.

### 2.4 Named regressions

`tests/phase_5_0_evidence/test_reservation.py`, **81 tests, up from 41**. Every
case the prompt enumerates, and the positive controls without which the refusals
would prove nothing:

| Required case | Test |
|---|---|
| free/readable lock with missing lifecycle history | `test_a_free_readable_lock_with_no_lifecycle_history_refuses` |
| unreadable / incomplete / unclassified history | `test_an_unreadable_history_is_not_an_empty_history`, `test_an_incomplete_history_refuses_however_clean_the_part_that_was_read`, `test_an_unclassified_predecessor_refuses` |
| expired/crashed predecessor with no verified release | `test_a_crashed_predecessor_with_a_free_lock_refuses`, `test_a_recovering_predecessor_refuses`, `test_an_elapsed_deadline_does_not_stand_in_for_a_release` |
| crash after effects, before a quarantine record could be published | `test_a_crash_after_effects_but_before_quarantine_publication_refuses` |
| predecessor release for the wrong host or run | `test_a_release_record_for_another_reservation_refuses`, `test_a_release_record_for_another_host_refuses`, `test_a_history_read_for_another_host_refuses`, `test_a_released_state_with_no_release_record_refuses` |
| omitted vs observed-empty vs observed-present residue | `test_omitted_residue_evidence_quarantines`, `test_an_explicitly_unmade_residue_observation_quarantines_the_same_way`, `test_observed_empty_residue_releases`, `test_observed_present_residue_quarantines_and_names_the_paths`, `test_an_incomplete_residue_search_is_not_an_observed_empty_one`, `test_a_bare_path_tuple_is_refused_rather_than_coerced` |
| evidence-free admission/release through public helpers | `test_advance_refuses_to_release_without_a_release_outcome`, `test_advance_refuses_to_admit_without_an_admission_decision`, `test_advance_refuses_a_release_outcome_that_quarantined`, `test_advance_refuses_an_admission_decision_that_refused`, `test_advance_refuses_the_wrong_kind_of_decision`, `test_a_decision_supplied_for_an_unguarded_transition_is_refused` |
| orphaned children, delayed transactions, interrupted recovery | `test_an_orphaned_child_quarantines_rather_than_releasing`, `test_a_delayed_database_transaction_quarantines`, `test_an_interrupted_recovery_quarantines_and_names_what_is_missing` (retained from the previous pass) |
| three distinct positive controls | `test_verified_first_use_is_a_positive_control`, `test_a_verified_predecessor_release_is_a_positive_control`, `test_a_completed_operator_recovery_admits_a_new_reservation`; plus `test_advance_admits_and_releases_on_the_corresponding_validated_decision` |
| continued refusal of real execution | `test_real_execution_stays_refused_under_every_positive_control` — the refusal holds under both repaired admitting dispositions |

### 2.5 What these decisions do **not** do

`reservation.DECISIONS_DO_NOT_PERSIST` and `ADAPTER_RESPONSIBILITIES` say it in
the module, and tests assert both are present:

* they persist nothing, lock nothing and enforce nothing. An `AdmissionDecision`
  that admits **is not a reservation**; and
* the eventual adapter owns the lock, the durable record and its ordering, the
  inventory, the real release observations, and any enforcement at all. **None of
  it is implemented in this pass**, and no reservation is enforced by anything
  today.

---

## 3. The revised runner contract — PR-20260911-1, -2 and -6

[`phase-5-0-reserved-laboratory-runner-contract-r2.md`](phase-5-0-reserved-laboratory-runner-contract-r2.md),
**submitted for technical review, not accepted and not implemented.** It
explicitly supersedes
[revision 1](phase-5-0-reserved-laboratory-runner-contract.md), which is
preserved unchanged under a banner naming the three withdrawn claims.

Every technical claim in it is labelled **[D] documented**, **[P] proposed** or
**[A] assumed**. The documented ones were verified against the manual pages
installed on this workstation (`man-pages 6.7`): `open(2)` for `O_PATH`'s
permitted operations and its `EBADF` list, `unlink(2)` for `unlinkat`'s
directory-relative name resolution, `rename(2)` for `RENAME_NOREPLACE`'s
destination-only guarantee and its filesystem support table, `flock(2)` for locks
on open file descriptions, `execveat(2)` for `AT_EMPTY_PATH` and its
close-on-exec caveat, and `proc_pid_fd(5)` for `/proc/self/fd/N` being a fresh
open subject to a permission check.

### 3.1 Effect ownership (§1)

The four claims the review falsified are conceded first, then replaced. Three
protections — exclusive creation, descriptor-bound effect, exclusion — are mapped
per effect in an inventory that gives each one the exact object or bytes, the
resolving operation, the descriptor owner and lifetime, the prerequisite and the
enforcement **immediately before** the effect.

The pathname-based operations are replaced concretely rather than by verb name:
`install -d` becomes exclusive `mkdirat`; `install -m 0555` becomes
`openat(O_CREAT|O_EXCL)` + held buffer + `renameat2(RENAME_NOREPLACE)`; `chattr`
becomes `ioctl(FS_IOC_SETFLAGS)` on a verified `O_RDONLY` descriptor — which also
corrects revision 1, since an `O_PATH` descriptor cannot issue an ioctl; and
payload *use* becomes `execveat` on the interpreter descriptor with the script
reached through `/proc/self/fd/N`, which keeps the 2026-09-06 Option B ruling
intact while binding both objects.

Descriptor custody is one long-lived executor holding the chain, transferred by
**inheritance only** across `fork`/`execve` and credential drops, with a declared
descriptor table the `DIRFD` argument indexes. A descriptor handed to an
experimental identity is stated to be a capability granted to it, and each case
must enumerate the descriptors it receives among its writable objects.

**The uncoverable row is named rather than papered over.** There is no `funlink`:
final-entry removal cannot be inode-bound. Its protection is quiescence plus a
pre-check and a post-check, both of which are **detection**, and where quiescence
cannot be established the removal is refused, the objects are reported as residue
and the state is S-B. Experimental writers are accounted for separately from
trusted administrators throughout.

### 3.2 Independent recovery (§2, §8.2)

An independent store at `/var/lib/freedom-blades/recovery/<run-id>/`,
`root:root 0700` under a `0700` parent, **outside `R`** and unreachable by any
experimental identity. Capture is one read into a held buffer, a consistency
re-`fstat`, a digest of that buffer, a durable write with `fsync`/rename/`fsync`,
a durable record binding digest to source identity and destination, and a
**read-back-and-digest of the stored copy** — all before the first configuration
mutation, with every failure refusing M1 rather than being retried.

Restart discovery is `readdir` of the store and needs neither `R` nor the
executor's memory. Retention runs until restoration is verified **and** the
reservation released without quarantine; disposal is an explicit operator step.
Restore is a verify-and-write over a held buffer with all temporaries written
before any rename, a fixed rename order, one reload, and a separate post-reload
verification whose failure is S-B. Partial writes cannot reach the destination.

`cleanup.RECOVERY_PROCEDURE`'s dependence on `R/before` is the defect the review
identified; contract r2 §8.2 gives the exact replacement text. **The
capture/restore writer is not implemented in this pass**, and the procedure text
in `cleanup.py` is unchanged pending review.

### 3.3 Cooperative lock and lifecycle storage (§5)

The `O_CREAT|O_EXCL` protocol is **withdrawn**. The proposal is the review's
preferred shape: one persistent lock inode at
`/run/freedom-blades/laboratory.lock`, `root:freedomlab 0660` in a
`root:freedomlab 0750` directory, created by a `systemd-tmpfiles` fragment
because `/run` is a tmpfs, **never created or unlinked by a participant**, taken
with `open(O_RDWR)` + `flock(LOCK_EX|LOCK_NB)`; and a separately protected
lifecycle record at `/var/lib/freedom-blades/laboratory/lifecycle.json`,
`root:freedomlab 0640`, written only by the harness CLI as root and read by all
seven participants through group read.

All seven entry points are tabulated with their identity, what they hold and
whether they write the record. Six only serialize; one writes lifecycle state.
The successful normal path is stated end to end, and so are eight refusal paths.
The crash case is the argument for two objects rather than one: a crashed
executor's `flock` is released by the kernel, the record still says `RUNNING`, and
the next participant refuses — no automatic takeover, which is PR-20260911-3 at
the storage layer.

### 3.4 The exact permission delta

**It is not zero, and revision 1's claim that it was is withdrawn.** Revision 1
inferred zero from unchanged executable names; specifying the mechanism to the
syscall is what revealed the additions.

| Surface | Before | After, if built |
|---|---|---|
| `plan.PERMITTED_EXECUTABLES` | 22 | **20** — `/usr/bin/install` and `/usr/bin/chattr` removed |
| `case_program.VERBS` | 16 | **20** |
| `BOOTSTRAP_VERBS`, `PERMITTED_RUN_AS`, `sudoers.EXPECTED_COMMANDS` | 2 / contract / 2 | **unchanged** |
| `ctypes` exceptions | 1 | **2** — the flag ioctls and `execveat` |
| New system group | — | **`freedomlab`**, with `ubuntu` as a member |
| New provisioned paths | — | `/run/freedom-blades`, the lock file, `/var/lib/freedom-blades/laboratory`, `/var/lib/freedom-blades/recovery` |
| New systemd artifact | — | one `systemd-tmpfiles` fragment |
| New privileged writer, capability or unit | — | **none** |

Six provisioning items, V1–V6, are listed in contract r2 §7 with an explicit
**"approved? no"** column. V6 is a preflight check: `RENAME_NOREPLACE` requires
filesystem support, and the target's filesystem type is one of the twelve
unconfirmed facts.

### 3.5 Remaining proof obligations

Contract r2 §9 is a nineteen-row bounded matrix covering root, descendant and
final-entry substitution; replacement after a successful check; in-place capture
mutation; capture failure before mutation; wrong destination; executor
restart with lost memory; interrupted restore; unknown surviving writers; and
successful controls. It requires model tests to track **original and replacement
identities and the bytes actually affected** as separate values, and it states
that four specific rows must fail the withdrawn revision-1 mechanism and pass
this one — a matrix in which both pass is not testing the correction.

**They are labelled proposal models, not implementation proof, and none is
written.** Nothing in §9 may be cited as evidence for EH-R16-1.

---

## 4. Files changed

| File | Change |
|---|---|
| `tools/phase_5_0_evidence/feasibility.py` | the `SEQUENCE` ordering model, `PublicationSink`, `SequenceObservation`, `run_sequence`; the three experiments rebuilt on it; three dispositions reassessed; `dependent_work_to_stop()` now empty |
| `tools/phase_5_0_evidence/reservation.py` | `PredecessorDisposition`, `ReleaseRecord`, `LifecycleHistory`, `ResidueObservation`, `DURABLE_RECORD_ORDERING`, `ADAPTER_RESPONSIBILITIES`, `DECISIONS_DO_NOT_PERSIST`, `GUARDED_TRANSITIONS`; `admit()`, `release()` and `advance()` repaired |
| `tests/phase_5_0_evidence/test_feasibility.py` | 46 → **62** tests |
| `tests/phase_5_0_evidence/test_reservation.py` | 41 → **81** tests |
| `docs/review/phase-5-0-reserved-laboratory-runner-contract-r2.md` | **new**; submitted, not accepted, not implemented |
| `docs/review/phase-5-0-reserved-laboratory-runner-contract.md` | superseded banner; content preserved unchanged |
| `docs/review/phase-5-0-reserved-laboratory-handback.md` | dated correction block at §3.4 and at the head; the submission preserved |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json`, `…-concrete-plan.md` | regenerated through the non-executing CLI; **not hand-edited** |
| `docs/review/Handover information`, `docs/implementation-plan.md` §20, `docs/project-management/status.md`, `docs/operations/disposable-test-server.md` | pointer updates and dated errata |

**No migration was added. No product code, application service, repository,
adapter, web route or Discord command was touched. No configuration or deployment
change is required by this pass, and `.env.example` is unaffected.**

**Security implications.** All repairs are fail-closed and all narrow what is
accepted: admission now requires evidence it previously inferred, release now
requires a search it previously assumed, and two public transitions now require
the decision that justifies them. The CRP correction, its tests and its synthetic
fixtures were preserved untouched. No new privileged surface was created; the
proposed one is in the contract and is unbuilt.

**Rollback.** Revert the two source files and their two test files; the two
generated artifacts then regenerate to the previous digest
`bbb3854fbdffae00696544465f1cd7bbdf22ad18583056490a6735444800e4fa`. The documents
are additive or carry dated corrections and can be reverted independently.

---

## 5. Verification

**Canonical testing remains on `oracle-test` with
`/opt/freedom-blades/runtime/venv-web/bin/python`.** The active assignment forbids
remote execution, so these are the prompt's local exception. Both fallback
interpreters were verified before use: `/opt/discord-bots/venv-web/bin/python` and
`/opt/discord-bots/venv/bin/python` are both **Python 3.12.3**.
`TEST_DATABASE_URL` was explicitly unset in every Python command, and the bot
suite completed before the web suite began.

| # | Command (every Python command prefixed `env -u TEST_DATABASE_URL`) | Result |
|---|---|---|
| 1 | `…/venv-web/bin/python -m compileall -q` on the four changed Python files | passed |
| 2 | `…/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_no_execution.py` | **205 passed** |
| 3 | `…/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_reservation.py tests/phase_5_0_evidence/test_feasibility.py tests/phase_5_0_evidence/test_r16_1_ownership_reproduction.py` | **159 passed** |
| 4 | `…/venv/bin/python -m pytest -q -rs tests/test_skills.py` | **83 passed, 1 warning** |
| 5 | `…/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence` | **1546 passed** |
| 6 | `…/venv/bin/python -m pytest -q -rs tests/test_*.py` | **3016 passed, 326 skipped, 1 warning** |
| 7 | `…/venv-web/bin/python -m pytest -q -rs tests/web` | **1610 passed, 1362 skipped** |
| 8 | `node --test 'foundry-module/tests/'*.test.mjs` | **171 passed, 0 failed, 0 skipped** |
| 9 | `git diff --check` | passed |

Command 3 is the prompt's focused set; no additional focused module was changed
beyond the two it already names. Command 5 was re-run after the generated
artifacts were installed and returned the same figure.

**Comparison with the previous review's figures.** Harness 1490 → **1546**
(+56, and the arithmetic closes exactly: feasibility 46 → 62 is +16, reservation 41 → 81 is +40, and 1490 + 16 + 40 = 1546. No other module changed count.)
Skills 83 → 83. Bot 3016/326 → **3016/326**. Web 1610/1362 → **1610/1362**.
Foundry 171 → **171**.

**Every skip is an unverified assertion.** The 326 bot skips and the 1362 web
skips are database-marked tests that did not run. The canonical
database-enabled web skip baseline is **80**, not 1362, so this run establishes
**no PostgreSQL correctness whatever**. Reported as unverified, not as passed.

**Checks not run, and why.**

| Check | Why |
|---|---|
| The canonical `oracle-test` run on `/opt/freedom-blades/runtime/venv-web/bin/python` | the active assignment forbids SSH and remote execution |
| Any database-marked test | `TEST_DATABASE_URL` is unset by instruction; the local host is not the disposable database host |
| Formatter, linter, type checker | **unconfigured tooling, not a passed check.** This repository has no `pyproject.toml`, `setup.cfg`, `tox.ini`, `.flake8`, `mypy.ini`, `.ruff.toml` or `.pre-commit-config.yaml`, and none of ruff, flake8, black, mypy or pylint is on `PATH` or importable in either interpreter |
| The Codex read-only target preflight | authorized, assigned to Codex after implementation review, and neither performed nor expanded here |
| Any execution, armed boundary or materializer run | refused by the assignment and by `is_executable=False` |

### 5.1 Manifest and generated artifacts

Covered source changed — `feasibility.py` and `reservation.py` are both in
`COVERED_SOURCES` — so the manifest and the concrete plan were regenerated
through the **non-executing** CLI:

```
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m \
  tools.phase_5_0_evidence.execution.cli --manifest-out <out>.json --render <out>.md
```

run **twice** to separate output names. Both generations are **byte-identical to
each other**, and the installed artifacts are byte-identical to the second
generation. All **34** covered SHA-256 values were **independently recomputed
from disk** by a separate script and all 34 match.

**The coverage list did not change**: `COVERED_SOURCES` still holds 34 entries
and no entry was added or removed, which is why the only manifest delta is two
source hashes and the aggregate digest.

| | Value |
|---|---|
| Previous review-input digest | `bbb3854fbdffae00696544465f1cd7bbdf22ad18583056490a6735444800e4fa` |
| **New review-input digest** | `e6d42228f5ccc4fd5eebc0861bb97eec42bbf16705d1aa209de5464e194bdba1` |
| `is_executable` | **False** |
| Unresolved conflicts | **3 (C-7)** |
| Unconfirmed target facts | **12**, each refusing the executor before any command starts |

**The digest is review input only and must not be passed to `--execute`.** No
generated artifact was hand-edited, and no producer review is recorded as
performed.

### 5.2 Controls retained

`is_executable=False`; the operational-ineligibility control
(`EvidenceResult.eligible_for_operational_acceptance` unconditionally `False`);
the missing-coverage controls, with an empty external coverage column for all
three C-7 cases; `producer_artifact_reviewed=False` for each; the unconditional
real-execution refusal, now additionally asserted under both repaired admitting
dispositions; and the twelve unconfirmed target facts, none populated.

---

## 6. Next step

**Owner: Codex. Action: technical review of this remediation.** Required
evidence for that review, in the order the prompt sets:

1. the corrected ordering model against package plan §2.13.5a C1/C2/C5 and
   `JNL-47`, and whether the withdrawal of the criterion split is correct;
2. the repaired decision API against PR-20260911-3 and -4, including whether the
   lifecycle vocabulary admits anything it should not and whether
   `DURABLE_RECORD_ORDERING` is sufficient for the crash-before-quarantine case;
3. contract r2 §1 against the primary syscall documentation, with particular
   attention to the row this document concedes is **not bindable** — final-entry
   removal — and to whether quiescence is an acceptable protection for it;
4. contract r2 §2's independent recovery, and whether refusing the mutation is
   the right failure mode when its basis cannot be established;
5. contract r2 §5's lock and lifecycle storage against the real participant
   identities, and §7's six provisioning items; and
6. LAB-1's classification and the §8 repair.

**Then Peter**, on the §7 provisioning and permission delta and on LAB-1's
classification. **Nothing in this pass requires a criterion decision.**

Implementation review precedes the later read-only target preflight, which
precedes a separate execution decision. **Passing tests advance none of those
gates**, and this handback closes no finding on its own authority. Package 5.0
remains **not ready**, P5.0-R5 **Blocking**, OD-62 **Open**, EH-R16-1 **Open**,
and PR-20260911-1 … -6 remain **Open** pending review.

---

## Dated errata, 2026-09-11 — corrections from the independent re-review

The [September 11 re-review](project-review-2026-09-11-r2.md) found four defects
in the work this handback submitted. **The original text above is preserved
unchanged.** These corrections are appended rather than applied to it, and each
names the claim it corrects and where the correction now lives.

| # | What this handback claimed | The correction |
|---|---|---|
| E1 | that the repaired `admit()` answered PR-20260911-3 by requiring a positive statement about the predecessor | **Incomplete.** The RELEASED branch validated the release record's reservation, host and target and never checked `predecessor_state`, so a complete history with `predecessor_state=RUNNING` or `QUARANTINED` beside a matching release record **admitted** — PR-20260911-R2-1. A local reproduction found the same fall-through for a **malformed** disposition value, which matched no branch and admitted with no refusal at all. Repaired 2026-09-11 in `reservation.validate_lifecycle()`; see [r2 handback](project-review-remediation-2026-09-11-r2-handback.md) §1 and [contract r3](phase-5-0-reserved-laboratory-runner-contract-r3.md) §5.9 |
| E2 | that contract r2 §§1.3, 1.4.2 and 1.4.4 specified a usable descriptor chain | **Wrong.** The chain was opened `O_PATH`, including `bin_fd`, and `pgconf_fd` was defined `O_PATH`; r2 then required `fsync` on both. `open(2)` does not permit that operation on an `O_PATH` descriptor, so the proposed normal installation failed at its own directory durability barrier and restoration failed the same way after replacing a destination — PR-20260911-R2-2. Corrected in [r3](phase-5-0-reserved-laboratory-runner-contract-r3.md) §1.3, which gives every descriptor its flags, owner, lifetime, permitted uses and transfer policy |
| E3 | that contract r2 §2.3's capture publication established a recovery basis before the first mutation | **Incomplete.** It omitted the barrier on the **recovery parent** after creating the `<run-id>` directory. Synchronizing the run directory's contents does not make its own entry durable, so restart discovery by listing the parent was not guaranteed to find the advertised basis — PR-20260911-R2-2. Corrected in [r3](phase-5-0-reserved-laboratory-runner-contract-r3.md) §2.3, whose barrier graph is complete and ordered |
| E4 | that contract r2 §1.4.5 and §9 row 3 described a post-unlink check that detects a substituted removal and reports both identities | **Overclaimed.** The post-check observes whether a name exists. After the pre-check succeeds for A, a writer can rename A away, install B at the name and let `unlinkat` remove B; the post-check then returns `ENOENT`, exactly as after a correct removal. It detects nothing and learns no identity — PR-20260911-R2-3. Corrected in [r3](phase-5-0-reserved-laboratory-runner-contract-r3.md) §1.4.5 and §9 row 3, with the counterexample modelled |
| E5 | that contract r2 §§5.6–5.7 stated the storage protocol's normal path | **Incomplete in two ways.** The ordinary participants' denylist omitted **ADMITTED**, which the decision API classifies as an active predecessor, so a crash after a durable ADMITTED and before RUNNING left a free lock and an unnamed state. And §7's provisioning list created only a directory and never initialized a verified-first-use record, so the documented fresh-install path could not reach its successful control — PR-20260911-R2-4. Corrected in [r3](phase-5-0-reserved-laboratory-runner-contract-r3.md) §§5.6–5.8, with §7 item **V7** added |

**Not corrected, because the re-review did not find them wrong.** The
C1-cleanup → C2 → C5 publication ordering correction and the withdrawal of the
`JNL-47-RECOVERY-STATE` criterion split both received a positive technical
recommendation for the bounded model. Both stand, with their negative controls,
and neither is reopened.

**LAB-1 remains Important and unimplemented**, its reproduction unweakened.
EH-R16-1 remains **Open**. The review-input digest this handback reported,
`e6d42228f5ccc4fd5eebc0861bb97eec42bbf16705d1aa209de5464e194bdba1`, is
superseded by the digest in the r2 handback because covered source changed again.
Neither was, or is, approved for execution.
