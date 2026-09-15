# Claude handback — reserved-laboratory implementation remediation

Date: 2026-09-14. Authorization: **C-P5.0-LAB-I-R1**.
Assignment: [remediation prompt](phase-5-0-reserved-laboratory-implementation-remediation-claude-prompt.md).
Review answered: [Codex technical and security review](project-review-2026-09-13-reserved-laboratory-implementation.md).
Design basis: [runner contract r6](phase-5-0-reserved-laboratory-runner-contract-r6.md).
Contract delta raised, not applied: [D1/D2 proposed amendment](phase-5-0-reserved-laboratory-r6-d1-d2-proposed-amendment.md).

**Returned for independent Codex technical and security re-review. Nothing here
closes a finding or a gate.** C-7 remains unresolved, EH-R16-1 remains **Open**,
`is_executable` remains **False**, the twelve target facts remain unconfirmed,
no item of the r6 §7 delta is provisioned, Package 5.0 remains **not ready**,
package-level P5.0-R5 remains **Blocking**, and OD-62 remains **Open**.

**New review-input digest:**
`eeafb24c18894835fb92ffbd4ae9e347a315260b4ba4c89e24faf3c76cb58fee`, replacing
`aabba2d718f5c0231c2b92b177e733fca7e6ce3c5c85283dda4730b14c3c91d4`. **It is
review input only. Do not pass it to `--execute`.**

---

## 1. The three findings, in one paragraph each

**LABI-1** — `RecoveryStore.publish()` took the destination from its caller,
verified only the stored copy's digest and set `mutation_permitted` from barrier
membership. The reviewed **capture set** is now a first-class object bound at the
integration boundary: one configuration directory and the exact component names
under it. A request is validated against it **before the recovery run directory
exists**, the destination the record binds is *derived* from the set rather than
taken from the request, publication verification establishes the same one-to-one
record/copy/destination correspondence `restore_configuration()` consumes, and
restart discovery applies that binding too. Codex's `/wrong/destination`
reproduction now refuses with `capture-destination-not-bound`, leaves no
directory behind, and permits no mutation.

**LABI-2** — both ownership comparisons were conditional on the recorded
identity being truthy. A non-empty creating-step identity for the exact
`(directory_role, name)` is now a **mandatory prerequisite** of setting a flag,
clearing a flag and removing an object. Three inputs refuse, all before `ioctl`,
`unlinkat` or `rmdir`: no record, no object at the pre-check, and an identity
that is not equal. Equality is the only admitting branch. Every production
creation path records the identity **inside the effect that creates the object**,
so no caller has to remember a separate optional call. Codex's unrecorded-removal
reproduction now refuses with `creating-step-identity-not-recorded` and the file
survives.

**LABI-3** — the mechanism was consumed only by its own tests. It is now the
repository's actual call graph. `execution/participants.py` is the integration
point for all seven `PARTICIPATING_ENTRY_POINTS`; the CLI's `--execute` branch
assembles the session, the descriptor inventory, the independent recovery store
and an armed effect issuer beside the boundary and materializer it already
built; the boundary receives and validates the declared descriptor table; 27
reviewed plan steps and 8 derived cleanup steps that used to be `/usr/bin/install`
and `/usr/bin/chattr` vectors are descriptor-bound effects; and
`plan.PERMITTED_EXECUTABLES` is **20**, with neither retired executable reachable
from any string literal in the package.

---

## 2. Finding-by-finding disposition, with requirement-to-code traceability

### LABI-1 — bind the recovery destination before mutation can be permitted

| Requirement (prompt) | Where it is implemented | Where it is tested |
|---|---|---|
| Define the reviewed capture set at the integration boundary — exact component, exact destination, exact correspondence | `recovery_store.ConfigurationCaptureSet`; `RecoveryStore.capture_set` / `bind_capture_set`; built in `executor._publish_recovery_basis` from `plan.target.postgres_config_directory` and the effect's reviewed components | `test_lab_remediation.py::test_the_positive_multi_file_publication_still_permits_the_mutation` |
| A caller must not be able to substitute an arbitrary absolute destination | `RecoveryStore._validate_capture_set` returns the **derived** mapping; `publish()` captures from it and never from `sources` | `…::test_the_reviewers_wrong_destination_reproduction_no_longer_permits_mutation` |
| Validate the whole set **before** the run directory or any temporary, copy or record | `publish()` step 0, ahead of `_create_run_directory` | every row of `…::test_every_unreviewed_capture_set_shape_refuses_before_anything_is_written` asserts `not (recovery/RUN-1).exists()` |
| Missing, additional, duplicate, malformed, cross-directory, mismatched all refuse | `CAPTURE_SET_INCOMPLETE`, `CAPTURE_COMPONENT_NOT_REVIEWED`, `CAPTURE_DESTINATION_DUPLICATED`, `CAPTURE_COMPONENT_MALFORMED`, `CAPTURE_DESTINATION_NOT_BOUND` | the eight parametrized rows, plus `…::test_a_duplicated_component_destination_is_refused_by_name` |
| Verification establishes the record/copy/destination correspondence restoration consumes | `RecoveryStore._verify_correspondence` — record decodes, names **this** run, names the reviewed destination for the copy it sits beside, digest and byte length match, and the directory holds exactly the reviewed names | `…::test_publication_verification_establishes_the_record_copy_destination_binding` |
| `mutation_permitted=True` only on the exact reviewed set, all five barriers, complete basis | `publish()`'s final `complete and exact` | `…::test_the_positive_multi_file_publication_still_permits_the_mutation` |
| Restart discovery and restoration apply the same binding | `RecoveryStore._discover_one`: orphan copy, orphan record, wrong run id, copy-name mismatch, duplicate destination, unbound destination, digest, byte length | `…::test_restart_discovery_applies_the_same_binding` (4 shapes) |
| Refusals fixed and bounded, no hostile text | `CAPTURE_REFUSALS`, `DISCOVERY_REASONS` — closed vocabularies; no reason interpolates a stored value | `…::test_a_refused_destination_never_reaches_an_operator_as_its_own_text` |
| A store with no reviewed set publishes nothing | `RecoveryStore._reviewed` → `CAPTURE_SET_NOT_BOUND` | `…::test_a_publication_with_no_reviewed_set_bound_refuses` |
| Retain positive publication, discovery and restore coverage | unchanged | `…::test_discovery_and_restore_still_find_the_positive_basis`, and the whole of `test_lab_implementation.py`'s §2.2–2.5 block |

`DESTINATION_BINDING_RULE` states the rule as a constant in the module, in the
finding's own terms.

### LABI-2 — ownership identity is mandatory, never optional

| Requirement (prompt) | Where it is implemented | Where it is tested |
|---|---|---|
| A non-empty creating-step identity is a **mandatory prerequisite** of set, clear and removal | `executor.DescriptorBoundEffects._require_recorded`, called first in `_open_and_verify` and in `remove_object` | `test_lab_remediation.py::test_no_effect_proceeds_without_a_recorded_creating_step_identity` (×3) |
| Missing record, absent object, unequal identity: three refusing inputs, all before `ioctl` / `unlinkat` / `rmdir` | `EFFECT_IDENTITY_NOT_RECORDED`, `EFFECT_OBJECT_ABSENT`, `EFFECT_IDENTITY_MISMATCH` | `…::test_an_object_absent_at_the_pre_check_refuses_before_any_syscall` (×3), `…::test_an_unequal_identity_refuses_and_the_substitute_survives` (×3) |
| Equality is the only admitting branch; no optional truthiness, no default empty, no skipped comparison | `_open_and_verify` and `remove_object` both `if found != recorded: raise` after a mandatory record | the three single-conjunct controls in `…::test_the_ownership_control_admits_the_refused_input` |
| The object survives every refusal | the refusals precede the syscall | every refusal test asserts `target.exists()` / `read_bytes()` |
| Preserve the accepted distinction: pre-check detects, quiescence prevents, post-check establishes absence only | `remove_object`'s docstring and `RemovalRecord`; `POST_CHECK_ESTABLISHES` unchanged | `…::test_the_documented_post_check_limitation_is_unchanged`, and `test_lab_implementation.py::test_the_post_check_cannot_tell_the_two_removals_apart` |
| Every production creation path records the identity at the point r6 specifies | `create_run_directories`, `create_directory_object`, `create_object`, `install_case_program` each write `_recorded[(role, name)]` inside the creation | `…::test_every_production_creation_path_records_its_own_identity` |

`OWNERSHIP_BINDING_RULE` states the rule as a constant beside the effects.
`EffectRefused` now carries a `classification` from the closed `EFFECT_REFUSALS`
set and refuses a value outside it at construction.

**Codex's exact reproduction:** `…::test_the_reviewers_unrecorded_removal_reproduction_refuses`.

### LABI-3 — integrate the mechanism through the real call graph

| Prompt item | Where it is implemented | Where it is tested |
|---|---|---|
| 1. Seven integration points: lock → re-seal/read/validate in §5.6 order → refuse before the first effect → durable `participant_started` → exact profile evidence → completion; an interrupted run blocks every successor | `execution/participants.py` — `ParticipantIntegration.run`, one object for all seven; the decision is `lifecycle_storage.read_and_admit`'s and the ledger is `ParticipantRunLedger` | `test_lab_integration.py` §§1–4 |
| 2. Harness CLI and executor over the same session, record and ledger; §5.12 preserved exactly | `cli.main`'s `--execute` branch builds `ParticipantIntegration`; `ParticipantIntegration.run_harness` delegates the tail to `run_ledger.TerminalSequence` → `conclude_reservation` | `…::test_the_execute_branch_assembles_the_whole_mechanism`, `…::test_the_dry_run_branch_assembles_none_of_it` |
| 3. Descriptor issuance and declared transfer connected to boundary launch; `DIRFD` an index into the declared table; `FD_CLOEXEC` cleared only for them; no synchronizable descriptor | `TransferEntry.number`; `DescriptorInventory.declare_transfer`; `ProcessBoundary.run(descriptors=…)`; `boundary._transferable` and `boundary._remap`; `executor._transfer_for` | `…::test_the_boundary_is_handed_the_declared_table`, `…::test_no_synchronizable_descriptor_is_ever_in_a_declared_table`, `…::test_the_launch_refuses_every_undeclared_descriptor` (4), `…::test_a_declared_directory_table_is_accepted` |
| 4. P1/P1b/P2/P4/L3 through `DescriptorBoundEffects`; pre-M1 capture through `RecoveryStore`; M1 requires its `mutation_permitted`; restoration through verify-and-write; old `install`/`chattr` steps no longer emitted or executable | `plan.EffectKind` / `plan.DescriptorEffect`; `CommandStep.effect`, `CleanupStep.effect`; `executor._issue_effect`/`_apply_effect`/`_issue_cleanup_effect`; `_revalidate_materialization`'s `publication_permits_mutation` re-check; `concrete_plan._create_directory`/`_create_empty_file`/`_set_flag`; `cleanup._clear_attributes`/`_restore_config` | `…::test_the_executor_dispatches_every_reviewed_effect_kind`, `…::test_the_plan_routes_every_retired_effect_through_the_issuer`, `…::test_the_materialization_requires_the_publication_and_not_the_step` |
| 5. `PERMITTED_EXECUTABLES` 22 → 20; generator and reviewed vectors updated; neither executable reachable | `plan.PERMITTED_EXECUTABLES`, `plan.RETIRED_EXECUTABLES` | `…::test_neither_retired_executable_is_reachable_from_the_package` (AST over every `.py` in the package), `test_concrete_plan.py::test_neither_retired_executable_appears_anywhere_in_the_plan` |
| 6. Every operational gate closed | unchanged | `…::test_the_standing_operational_gates_are_all_still_closed` |

**Bounded before it becomes a name** — the reviewer's condition on fixed refusal
roles. `participants.validate_run_identifier` bounds a caller's run id to 64
characters of `[A-Za-z0-9._-]` starting alphanumeric, **before** it becomes a
ledger filename, a `runstore:<run-id>` role in a refusal or a recovery directory
name. `…::test_a_caller_supplied_run_identifier_is_bounded_before_it_is_a_name`
asserts seven hostile shapes refuse and that the refusal never echoes the value.

---

## 3. The complete call graph, before and after

### Before (what Codex found)

```text
cli.main --execute
  └─ ExecutingRunner(plan, SubprocessBoundary(armed), SystemMaterializer(armed))
       ├─ boundary.run(step_id, argv, run_as, capture, timeout, catalog)
       │     └─ /usr/bin/install ×21, /usr/bin/chattr ×14   ← pathname-resolved
       └─ materializer.materialize(...)

LaboratorySession · ParticipantRunLedger · RecoveryStore · DescriptorBoundEffects
  └─ (no production consumer — tests only)

tests/test_*.py · tests/web · foundry-module/tests · §3.2 · §3.5 · §4
  └─ (no lock, no ledger, no admission)
```

### After

```text
cli.main --execute
  ├─ ParticipantIntegration(HARNESS_CLI, …)         ← r6 §5, takes the lock
  ├─ DescriptorInventory / PosixFilesystem
  ├─ RecoveryStore(inventory, filesystem)            ← r6 §2.2, independent
  └─ ExecutingRunner(
        plan,
        boundary   = SubprocessBoundary(armed=True),
        materializer = SystemMaterializer(armed=True),
        effects    = DescriptorBoundEffects(inventory, filesystem,
                                            recovery=store, armed=True),
        session    = integration, run_id, reservation_id)
       ├─ _require_accounted_run()  ← armed issuer ⇒ a participant run accounts for it
       ├─ per step:
       │    ├─ effect step  → _issue_effect → DescriptorBoundEffects
       │    │     create_directory · create_object · install_payload ·
       │    │     set_flag · clear_flag ·
       │    │     capture_configuration → RecoveryStore.publish (5 barriers)
       │    │     restore_configuration → materializer.restore_configuration
       │    └─ command step → boundary.run(…, descriptors=inventory.declared_transfer())
       │            └─ _transferable() → pass_fds + dup2 into 3…3+n
       └─ _materialize_after → publication_permits_mutation(publication) ⇒ M1

ParticipantIntegration.run(run_id, work, observed_by)          ← all seven
  ├─ LaboratorySession.open()      lock (wait|refuse), 4 descriptors
  ├─ session.admit()               read_and_admit: re-seal → read → parse →
  │                                order → validate → survey → decide
  ├─ ledger.begin(...)             durable participant_started, before any effect
  ├─ work(EffectPermit(granted))   ← the only object that says the start is durable
  ├─ observation.missing(profile)  the participant's exact conditions
  ├─ ledger.complete(...)          durable participant_completed
  └─ session.close()               release the lock, here and nowhere earlier

ParticipantIntegration.run_harness(...)  ← §5.12 steps 0–4
  └─ TerminalSequence.conclude → conclude_reservation
       step 0 binding · step 1 release decision · step 2 RELEASED ·
       step 3 harness completion · step 4 lock released by close()
```

**The six non-harness entry points** each construct
`integration_for(Participant.X, …)` and pass their wrapper as `work`. **Under
this authorization the wrappers are defined and exercised only over `tmp_path`
with injected local fakes**; no shell, systemd unit or documented procedure was
changed to call them, because the prompt forbids invoking any of them against a
real participant. That is the one part of item 1 that is deliberately not
delivered as an operational change, and it is named again in §11.

---

## 4. Files and interfaces

### Added — one source, two test files

| File | Lines | What it is |
|---|---|---|
| `tools/phase_5_0_evidence/execution/participants.py` | 632 | r6 §5's integration point for all seven entry points |
| `tests/phase_5_0_evidence/test_lab_remediation.py` | 765 | LABI-1 and LABI-2 regressions and controls |
| `tests/phase_5_0_evidence/test_lab_integration.py` | 1 027 | LABI-3 structural and behavioural tests and controls |

### Changed — production

| File | Change |
|---|---|
| `execution/recovery_store.py` | `ConfigurationCaptureSet`; `capture_set` / `bind_capture_set`; `_validate_capture_set`; `_verify_correspondence`; the binding in `_discover_one`; 7 new refusal classifications; 10 fixed discovery reasons; `DESTINATION_BINDING_RULE` |
| `execution/executor.py` | `EffectRefused.classification` and `EFFECT_REFUSALS`; `_require_recorded`; the rewritten `_open_and_verify` and `remove_object`; `recorded_identity`; `create_directory_object`; `create_object`; `publish_recovery_basis`; `restore_configuration`; `declared_transfer`; `OWNERSHIP_BINDING_RULE`; `FLAG_VALUES`; `_issue_effect`, `_apply_effect`, `_issue_cleanup_effect`, `_resolved_ownership`, `_transfer_for`, `_require_accounted_run`; `effects`/`session`/`run_id`/`reservation_id` fields; M1's publication re-check |
| `plan.py` | `EffectKind`, `DescriptorEffect`, `EFFECT_FLAGS`, `ROOT_ROLE`, `EVIDENCE_ROLE`, `CONFIGURATION_ROLE`, `RETIRED_EXECUTABLES`; `CommandStep.effect` and `is_effect`; `PERMITTED_EXECUTABLES` 22 → **20** |
| `concrete_plan.py` | `_component`, `_create_directory`, `_create_empty_file`, `_set_flag`; the case-program install, the six `chattr` steps and the two configuration captures rebuilt as effects; `CAPTURED_CONFIGURATION`; `EMPTY_SOURCE` retired |
| `cleanup.py` | `CleanupStep.effect` and `is_effect`; `_Reversed`; `_clear_attributes` and `_restore_config` as effects; `NON_DESTRUCTIVE_WHEN_ABSENT` loses both retired executables; `is_safe_to_rerun` states why an effect is re-runnable |
| `execution/boundary.py` | `descriptors=` on the protocol, the real boundary and the recording one; `_transferable`, `_remap`, `_TransferRefused`; 6 new launch classifications |
| `execution/descriptors.py` | `TransferEntry.number`, populated by `declare_transfer` from the traversal descriptor |
| `execution/host_lock.py` | `LaboratorySession` holds and hands out a `ParticipantRunLedger` |
| `execution/cli.py` | the `--execute` branch assembles the integration, inventory, store and armed issuer; `--run-id`, `--reservation`, `--author`, `--at` |
| `review_manifest.py` | `MANIFEST_VERSION` 11 → **12**; `COVERED_SOURCES` 42 → **43**; `_effect_row` pins every effect |

### Changed — tests

`harness_fixtures.py` gains `RecordingEffects` and `refusing_effects`;
`test_r13_remediation.py` gains `HostEffects`, the host-backed issuer with the
same binding;`lab_fixtures.py` binds the reviewed capture set;
`test_r16_1_ownership_reproduction.py` has its §1 and §2 cases **inverted**, as
that module always said they would be. Ten further modules were updated for the
effect/command split.

### Interfaces a reviewer should read first

* `RecoveryStore._validate_capture_set` — the binding, in one method, before
  anything exists;
* `DescriptorBoundEffects._require_recorded` — nine lines, and the whole of
  LABI-2;
* `ParticipantIntegration.run` — §5.6's order with nothing between the steps;
* `boundary._transferable` — five refusing inputs, all before a process exists.

---

## 5. Failing-before, passing-after, negative controls

### Failing-before — run against the submitted tree

`test_lab_remediation.py` was written first and run unchanged against the
submitted implementation. The names the correction adds are imported **inside**
the tests that need them, so the module still collects and the two reviewer
reproductions fail on their assertions rather than on an import:

```text
$ python -m pytest -q tests/phase_5_0_evidence/test_lab_remediation.py
...
31 failed, 6 passed
```

**LABI-1's reproduction, verbatim:**

```text
>           assert not publication.published
E           AssertionError: assert not True
E            +  where True = StorePublication(published=True, mutation_permitted=True,
E                barriers_crossed=('recovery-parent-entry', 'copy-data', 'cop…
```

**LABI-2's reproduction, verbatim:**

```text
>           with pytest.raises(EffectRefused) as refusal:
E           Failed: DID NOT RAISE <class '…executor.EffectRefused'>
```

`test_lab_integration.py` does not collect against the submitted tree at all:
`tools/phase_5_0_evidence/execution/participants.py` does not exist there, which
is LABI-3 restated as an import error.

### Passing-after

| Suite | Result |
|---|---|
| `tests/phase_5_0_evidence` (whole) | **2 165 passed, 0 skipped** (from 2 074) |
| `test_lab_remediation.py` | 37 passed |
| `test_lab_integration.py` | 44 passed |
| `test_lab_implementation.py` | 110 passed |
| `test_no_execution.py` | 247 passed |

### Negative controls — thirteen single-point reversals

Each removes **exactly one** load-bearing conjunct in a scratch copy of
`tools/`, with `tests/` unchanged, and the whole `tests/phase_5_0_evidence`
suite is then run. A check nothing catches is a check that was not load-bearing.

| # | Finding | What is removed | Failures |
|---|---|---|---|
| 1 | LABI-1 | the pre-publication capture-set validation | **11** |
| 2 | LABI-1 | the record/copy/destination correspondence check | **1** |
| 3 | LABI-1 | discovery's destination binding | **1** |
| 4 | LABI-2 | the mandatory-record conjunct (the reviewer's own shape) | **4** |
| 5 | LABI-2 | the removal's present-object conjunct | **1** |
| 6 | LABI-2 | the removal's equality conjunct | **2** |
| 7 | LABI-3 | M1's re-check of the publication's barrier set | **2** |
| 8 | LABI-3 | an armed issuer's accounted-run requirement | **1** |
| 9 | LABI-3 | the durable-start requirement before the work | **1** |
| 10 | LABI-3 | the exact-profile-conditions requirement | **7** |
| 11 | LABI-3 | the run-identifier bound | **2** |
| 12 | LABI-3 | the boundary's descriptor-table validation | **1** |
| 13 | LABI-3 | re-admitting `install` and `chattr` to the allowlist | **2** |

Three further controls run **in process**, as `test_lab_remediation.py` and
`test_lab_integration.py` do for the conjuncts a scratch reversal cannot isolate:
`test_the_binding_control_permits_the_wrong_destination_again` subclasses
`RecoveryStore`, overrides exactly the two binding methods, and publishes
`/wrong/destination` with `mutation_permitted=True` again;
`test_the_ownership_control_admits_the_refused_input` re-issues the production
sequence three times with one comparison omitted each time; and
`test_the_survey_control_admits_over_an_unsettled_run` calls `read_and_admit`
with `ledger=None` and shows the unsettled run disappears from the refusal set.

The suite's preserved positive controls hold under every reversal.

---

## 6. Security analysis

### Recovery destination binding

The property is that **the destination a record binds is never a value a caller
chose**. Four things carry it:

1. the reviewed set is constructed at the integration boundary from
   `plan.target.postgres_config_directory` and the effect's reviewed components,
   and `RecoveryStore.capture_set` is the only place `publish()` reads it from;
2. the request is compared with the set **before** the run directory exists, so
   a refused request leaves no directory, no temporary, no copy and no record —
   nothing for a later discovery to find and nothing for an operator to explain;
3. what is captured is the **derived** destination, not the requested one, even
   when the two agree, so there is no path on which a caller's string reaches a
   stored record; and
4. verification and discovery apply the same correspondence restoration
   consumes, so a basis restoration would refuse is reported not-usable at
   publication time rather than discovered after the mutation.

**Refusal text.** Every capture refusal is one of seven fixed classifications
and every discovery reason is one of ten fixed strings. None interpolates a
component, a destination, stored bytes or an operating-system message.
`test_a_refused_destination_never_reaches_an_operator_as_its_own_text` asserts
the reviewer's own hostile path is absent from the rendered refusal.

**Residual, stated.** The store's `0700 root:root` parent is provisioning item
**V5** and is unprovisioned. Until it is applied the independence is a
definition. In-place mutation of a captured source between the `fstat` and the
read is refused by the size/mtime consistency check, which is a consistency
check on the read and not a substitution check — unchanged from r6 §2.3.3(7).

### Ownership binding

Three refusing inputs, all **before** the syscall, and equality as the only
admitting branch. The flag path takes **one** lookup — `openat` then `fstat` of
the descriptor it returned — so the effect is issued on the object the
comparison saw, and there is no second interval between two of this run's own
calls. The removal's pre-check is `fstatat`, and r6 §1.4.5's honesty is intact:
it **detects**, quiescence is the only **prevention** for the final-component
interval, and the post-check establishes absence and never which inode was
removed.

**What this changes about EH-R16-1.** The half of the finding that was about a
pathname re-resolved after an ownership check is now covered for the executor's
own effects: there is no `install` or `chattr` vector left to find a replacement
through. The half that is not covered is unchanged and is asserted rather than
described — the removals still resolve names, the experiments still resolve
names, and in-place content mutation of a stable inode is not covered by a
descriptor at all. **EH-R16-1 stays Open**, and
`test_r16_1_ownership_reproduction.py` is where the residual lives.

### Descriptor transfer

`_transferable` refuses five inputs before any process exists: an index outside
the consecutive table starting at 3, a **synchronizable** descriptor, a closed
descriptor, a non-directory, and a duplicated index. `declare_transfer` puts
only traversal descriptors in a table, so the synchronizable refusal is enforced
at both ends. `pass_fds` closes every descriptor the table does not name, and
the `dup2` into 3…3+n happens in the forked child, so `FD_CLOEXEC` is cleared
for exactly the declared set and for nothing else.

**Residual, stated.** The remap uses a `preexec_fn`, which is documented as
unsafe in a threaded parent. The harness is single-threaded and the callable
allocates nothing, imports nothing and logs nothing. It is named here rather
than left unremarked.

### Participant ordering and interruption

The permit is the only object that says the start is durable and it is
constructed in exactly one place. An admission refusal, a lock refusal and a
start that did not publish each return **without calling the work**, which three
behavioural tests assert by observing an empty recorder. An interrupted run —
started and not completed — refuses all seven successors including the
environment reset, and the test walks all seven and then shows the attributed
recovery unblocking them. The reset is given no exemption and has its own test
saying so.

**Residual, unchanged and largest.** The six participants' completion conditions
are **injected and attributable**. Nothing here observes a process, a database
backend or a tree, and r6 §9.3's **I9** remains unperformed for all five it
names. A completion condition nobody can observe is a run that never settles.

### Refusal text, overall

Every classification this pass adds comes from a closed set — `CAPTURE_REFUSALS`,
`EFFECT_REFUSALS`, `PARTICIPANT_REFUSALS`, and the six new `LAUNCH_FAILURES`
members. `EffectRefused` and `ParticipantRefused` both refuse a classification
outside their vocabulary at construction. A caller-supplied run id is bounded
before it can become a role label, and the bound's own refusal does not echo the
value it refused.

---

## 7. The D1/D2 contract delta — proposed, not self-approved

Written as a separate, separately reviewable document:
[phase-5-0-reserved-laboratory-r6-d1-d2-proposed-amendment.md](phase-5-0-reserved-laboratory-r6-d1-d2-proposed-amendment.md).

**r6 is unedited by this pass.** The amendment gives the exact text proposed for
§6.2, §6.4 and §7 (D1: the `linkat`/`unlinkat` substitute, its two-syscall,
two-name interruption state, the preserved temporary, and V6's scope narrowing
**without** V6 closing) and for §1.3.2, §1.3.3, §6.2 and §6.4 (D2: descriptor
**D20**, the short-lived `"."`-relative listing descriptor, used for one
`readdir` and never retained, transferred, synchronized or used as a `dirfd`).

**Until it is accepted, V6 stays unconfirmed and neither deviation is closed.**
No broader `ctypes` exception was added and no trusted syscall or descriptor
surface was widened to avoid documenting the decision.

I found no existing maintainer disposition that authorizes either point: the
2026-09-12 direction accepts the ten-item §7 delta and the shared `ubuntu`
identity, and says nothing about §1.3.3 or §6.2.

---

## 8. Generated artifacts and the review-only digest

* Generated **five times** through the non-executing CLI (`--manifest-out`,
  `--render`; no `--execute`, no `--confirm-target`). The first three were
  byte-identical; the first was installed and a fourth generation compared
  byte-identical with the installed files; a fifth and sixth were taken after
  the last source change and compared again.
* `COVERED_SOURCES` read from `review_manifest.py`'s **syntax tree** and all
  **43** hashes recomputed independently against the files on disk: **zero
  mismatches**, and the manifest's pinned set equals the AST-read set.
* One path **added**: `execution/participants.py`. None removed.
* `manifest_version` **11 → 12**; `supplied_observations.schema_version` stays
  **3**; the run-record schema stays **3**; `is_executable` **False**;
  `unresolved conflicts 3 (C-7)`; unconfirmed facts still the twelve.
* **26** plan steps and **8** cleanup steps are pinned as effects rather than as
  vectors; no pinned vector names either retired executable.
* Digest:
  `eeafb24c18894835fb92ffbd4ae9e347a315260b4ba4c89e24faf3c76cb58fee`.
  **Review input only. It must not be passed to `--execute`.**

---

## 9. Commands, interpreters and results

**Restricted local pass, `TEST_DATABASE_URL` unset**, as the authorization
requires. The canonical `oracle-test` interpreter
`/opt/freedom-blades/runtime/venv-web/bin/python` exists on this workstation and
**has no pytest**, and `oracle-test` may not be reached under C-P5.0-LAB-I-R1,
so the same restricted-local exception the accepted LAB-1 handbacks used
applies: `/opt/discord-bots/venv-web/bin/python` and
`/opt/discord-bots/venv/bin/python`, both Python **3.12.3** with pytest
**8.4.2**, and node **v24.20.0**.

| Command | Result |
|---|---|
| `python -m pytest -q -rs tests/phase_5_0_evidence` | **2 165 passed, 0 skipped** |
| `python -m pytest -q tests/phase_5_0_evidence/test_lab_remediation.py` | **37 passed** |
| `python -m pytest -q tests/phase_5_0_evidence/test_lab_integration.py` | **44 passed** |
| `python -m pytest -q tests/phase_5_0_evidence/test_lab_implementation.py` | **110 passed** |
| `python -m pytest -q tests/phase_5_0_evidence/test_no_execution.py` | **247 passed** |
| `python -m pytest -q -rs tests/test_*.py` (bot) | **3 025 passed, 326 skipped** |
| `python -m pytest -q tests/web` (web) | **1 609 passed, 1 failed, 1 362 skipped** |
| `node --test foundry-module/tests/*.test.mjs` | **171 passed** |
| `python -m compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` | succeeded |
| `git diff --check` | clean |
| `python3 .claude/hooks/test_guards.py` | **31 cases, 19 refused and 12 allowed, all passed** |
| 13 single-point reversals, whole suite each | every one caught — see §5 |

**Every skip is unverified.** The database-enabled web baseline is **80**, not
1 362; the 1 362 figure is what an unset `TEST_DATABASE_URL` produces and the
run still exits 0. The bot suite's 326 are the same class.

**The one web failure is pre-existing and unrelated, and I verified that rather
than citing the earlier handback.**
`tests/web/test_p3_4_static_assets.py::test_the_discovery_enumerates_untracked_files_rather_than_directories`
asserts *"no untracked directory in this tree; this test proves nothing"* — it
requires the working tree to contain an untracked **directory**, and it does
not. This change adds only untracked **files** inside already-tracked
directories, so it cannot create or remove one. Demonstrated: creating one
temporary untracked directory makes the test pass, and removing it again makes
it fail. The bot suite runs on `/opt/discord-bots/venv/bin/python`, because the
web environment has no `discord` module.

**Checks not run, and why.** No formatter, linter or type checker is configured
in this repository or installed in either environment — `black`, `ruff`,
`flake8`, `mypy`, `pyright` and `isort` are all absent and there is no
configuration file for any of them. That is **unavailable, not a pass**. The
bot, web and Foundry suites were run on this workstation and **not** on
`oracle-test`, which this authorization excludes.

---

## 10. Rollback

Repository changes only; nothing was deployed, migrated or provisioned.

1. Delete the three added files:
   `tools/phase_5_0_evidence/execution/participants.py`,
   `tests/phase_5_0_evidence/test_lab_remediation.py`,
   `tests/phase_5_0_evidence/test_lab_integration.py`, and this handback and the
   D1/D2 amendment under `docs/review/`.
2. `git checkout --` the files §4 lists as changed, **except** that
   `execution/artifact.py`, `journal.py`, `observations.py`, `cleanup.py`,
   `feasibility.py`, `review_manifest.py`, `case_runtime.py` and
   `execution/case_program.py` also carry the previously uncommitted LAB-1 and
   C-P5.0-LAB-I work, which must be preserved. Revert those by removing only the
   hunks §4 attributes to this pass.
3. Regenerate the manifest and concrete plan through the non-executing CLI; the
   digest returns to
   `aabba2d718f5c0231c2b92b177e733fca7e6ce3c5c85283dda4730b14c3c91d4`.
4. There is nothing else: no migration, no schema change, no configuration
   applied to any host, no service touched and no bot restart.

---

## 11. Unconfirmed target facts, unresolved gates, and what this pass did not do

**All twelve target facts remain unconfirmed** — `interpreter_sha256`,
`interpreter_real_path`, and E7's ten. The CLI still reports each as refusing
the executor before any command starts.

**The r6 §7 preflight items remain unperformed:** V6, V8 and V10. **No item of
the ten-item §7 delta is provisioned.** No object was created under `/run`,
`/var/lib` or `/etc`, and
`test_lab_implementation.py::test_the_production_layout_is_data_and_no_test_builds_over_it`
asserts all three production paths are **absent**.

**Gates unchanged:** C-7 unresolved; EH-R16-1 **Open**, with the harness's
unconditional real-execution refusal in force; `is_executable` **False**;
Package 5.0 **not ready**; package-level P5.0-R5 **Blocking**; OD-62 **Open**.
LAB-1's local remediation stays closed on the R3 re-review.

**What item 1 of the prompt does not yet deliver operationally.** The six
non-harness integration points exist, are exercised end to end and enforce the
whole protocol — but nothing outside this repository calls them yet. Wiring
`tests/test_*.py`, `tests/web`, `foundry-module/tests`, §3.2, §3.5 and §4 to
invoke them would mean changing how those participants actually run on
`oracle-test`, and the authorization says plainly that the wrappers *"may not be
invoked against real participants in this assignment"*. **This is stated as an
incomplete item rather than as a completed one**, and it is the first question
in §12.

**Nothing was executed, provisioned or inspected.** No SSH, synchronization,
host inspection, preflight, permission or group change, `systemd-tmpfiles`,
provisioning, creation of any `/run` or `/var/lib` object, database operation,
destructive drill, service change, dependency installation, generated-vector
execution, `--execute`, real boundary or materializer use, migration,
deployment, cutover, commit, push, reset, history rewrite or bot restart. No
credential or secret file was read — the repository's secrets guard refused one
command of mine whose *search pattern* named a secret file, and the scan was
rewritten rather than routed around. Both Codex review records were left
untouched.

---

## 12. Focused questions for independent re-review

1. **The six participants' wrappers are defined and not called.** §11 says why.
   Is a follow-up authorization to change how the six actually run on
   `oracle-test` the right next slice, or should the integration points stay
   library-only until the §7 delta is provisioned — since an integration point
   that refuses on an absent lock would stop every suite on an unprovisioned
   host the moment it were wired?
2. **D1 and D2.** The proposed amendment is in its own document. Are the two
   texts the right ones, and is narrowing V6's scope without closing it the
   right disposition?
3. **The reviewed capture set is constructed by the executor** from the plan's
   target and the effect's declared components. Is the **effect** the right
   place for that declaration, or should the reviewed set be a constant in
   `targets.py` that both the plan and the store read?
4. **`R/before` is now retained evidence written from the store**, after the
   basis is durable, so it can neither precede the basis nor be mistaken for it.
   r6 §2.5 permits retaining it. Is writing it from the store the right shape,
   or should the plan stop declaring those two `file:` mutations altogether —
   which would also retire the EH-R13-2 retention machinery that protects them?
5. **`rm` and `rmdir` stay permitted and stay pathname-resolved.** r6 §6.4's
   table removes only `install` and `chattr`, and §1.4.5 says the removal's
   final component is not bindable — but the contract's own L3 row describes
   `unlinkat`. Is keeping the removals as command steps the reading you intend,
   or should L3's removal half also become an effect (which would take the
   allowlist below 20 and contradict §6.4's count)?
6. **Security: `preexec_fn`.** The child-side remap into descriptors 3…3+n is
   the only way to place inherited descriptors at declared indices from
   `subprocess`. Is that acceptable, or should the transfer be declared and
   validated but left unperformed until a launcher that does not need
   `preexec_fn` exists?
7. **Security: the run-identifier bound.** 64 characters of `[A-Za-z0-9._-]`
   starting alphanumeric. Is that the right shape for a value that becomes a
   filename, a directory name and a role label, and should the **reservation**
   identifier be bounded the same way at the same place?
8. **`test_r16_1_ownership_reproduction.py` inverted five cases.** That module
   always said it would have to. Is the residual it now states — the removals,
   the experiments' own verbs, and in-place mutation of a stable inode — the
   right statement of what EH-R16-1 still is?

**Stop point.** No read-only preflight, provisioning or execution follows
automatically. The next checkpoint is independent Codex technical and security
re-review of this remediation.
