# Claude handback — reserved-laboratory mechanism implementation

Date: 2026-09-13. Authorization: **C-P5.0-LAB-I**.
Assignment: [implementation prompt](phase-5-0-reserved-laboratory-implementation-claude-prompt.md).
Design basis: [runner contract r6](phase-5-0-reserved-laboratory-runner-contract-r6.md).
Prior checkpoint: [LAB-1 R3 re-review](project-review-2026-09-13-lab1-rereview-r3.md).

**Returned for independent Codex technical and security review. Nothing here
closes a finding or a gate.** C-7 remains unresolved, EH-R16-1 remains Open,
`is_executable` remains `False`, the twelve target facts remain unconfirmed, no
item of the r6 §7 delta is provisioned, Package 5.0 remains **not ready**,
package-level P5.0-R5 remains **Blocking**, and OD-62 remains **Open**.

**New review-input digest:**
`aabba2d718f5c0231c2b92b177e733fca7e6ce3c5c85283dda4730b14c3c91d4`, replacing
`6ef61afbaa96dcbd5eda408eed5042aff3a227ce32cb56b149111e531f7a2408`. **It is
review input only. Do not pass it to `--execute`.**

---

## 1. What was built, in one paragraph

r6 §6.1's mechanism exists in code: the descriptor custody chain, the four
descriptor-relative case-program verbs, the executor's exclusive creation,
payload installation, flag and removal effects behind a quiescence gate, the
independent recovery store with all five publication barriers, verify-and-write
restoration with its two, the cooperative lock adapter over the pre-existing
provisioned inode, and the reservation record and seven-participant run ledger
on disk. The r6 §7 definitions for V1–V5, V7 and V9 are written down as data.
Three C-7 producers gained the adapter that renders their runs as importer
records, so the producer-to-importer path is exercised end to end — and every
safeguard that keeps it out of coverage is asserted rather than described.

**One design decision runs through all of it and is the thing to review first.**
The new modules add **no rule**. `lifecycle_storage` already carries r6 §5.5's
codec and history order rules, §5.11.1's participant validator and §5.12's
terminal order, over an injected filesystem. The mechanism supplies a second
implementation of that *filesystem* — real descriptors, real files, real `fsync`
— and reuses the validators unchanged. A mechanism with its own copy of those
checks would be a second reader, and every finding from R3-1 to R5-1 is a drift
between two readers of one fact.

---

## 2. Requirement-to-code traceability

| r6 requirement | Where it is implemented | Where it is tested |
|---|---|---|
| §1.3.1 an `O_PATH` description permits no `fsync` | `execution/descriptors.py` `PosixFilesystem.fsync` | `test_fsync_on_the_traversal_descriptor_is_refused`, `test_the_kernel_also_refuses_fsync_on_an_o_path_description` |
| §1.3.2 two descriptors per directory, the second **bound by comparison** | `DescriptorInventory.bind_synchronizable` | `test_a_directory_is_held_twice_and_the_two_descriptors_differ`, `test_a_substitution_between_the_two_opens_is_detected` |
| §1.3.2 the two descriptors are told apart by their use sites | `PosixFilesystem._directory_descriptor`, `fsync_entry` | `test_a_synchronizable_descriptor_may_not_be_traversed` |
| §1.3.3 transfer by inheritance only; **no synchronizable descriptor is transferred** | `DescriptorInventory.declare_transfer`, `refuse_synchronizable_transfer` | `test_no_synchronizable_descriptor_is_ever_in_a_transferred_set` |
| §1.3.3 `DIRFD` is an index into a declared table | `DescriptorInventory.dirfd_for_index` | `test_an_index_outside_the_declared_table_refuses` |
| §1.4.1 C1 exclusive creation is the ownership proof | `DescriptorInventory.create_directory` | `test_the_five_run_directories_are_created_exclusively` |
| §1.4.2 P1 five `mkdirat`s, P1b the root's barrier | `executor.DescriptorBoundEffects.create_run_directories` | same |
| §1.4.2 P2 install from one held buffer, both barriers, exclusive publication | `…install_case_program` | `test_the_reviewed_payload_is_installed_from_one_held_buffer`, `test_a_payload_whose_digest_moved_is_refused_rather_than_installed`, `test_the_payload_is_published_exclusively` |
| §1.4.2 P4 the flag lands on the inode a descriptor holds | `…set_inode_flags` / `clear_inode_flags` | `test_the_flag_effect_is_issued_on_the_descriptor_and_not_on_a_name`, `test_a_flag_change_on_a_substituted_name_refuses` |
| §1.4.5 L3 pre-check detects, post-check does not | `…remove_object`, `RemovalRecord`, `POST_CHECK_ESTABLISHES` | `test_a_substitution_before_the_pre_check_is_genuinely_detected`, `test_the_post_check_cannot_tell_the_two_removals_apart` |
| §1.6 three quiescence observations, none defaulting to true | `…require_quiescence` over `durability_model.Quiescence` | `test_an_unestablished_quiescence_refuses_every_b3_effect` (unobserved / observed-false / incomplete) |
| §2.2 the independent store, outside the disposable root | `execution/recovery_store.py` `RecoveryStore` | `test_discovery_is_a_listing_of_the_recovery_parent`, `test_a_stored_copy_is_read_only_and_owned_by_the_writer` |
| §2.3.3 five ordered barriers; **no mutation until all are crossed** | `RecoveryStore.publish`, `materializer.publication_permits_mutation` | `test_the_positive_sequence_crosses_every_barrier_and_permits_the_mutation`, `test_failure_at_any_barrier_prevents_the_first_configuration_mutation` (×5) |
| §2.3.3 barrier 1 is `recovery-parent-entry` — the one r2 omitted | `RecoveryStore.publish` step 3 | `test_the_recovery_parent_entry_barrier_is_the_one_revision_2_omitted` |
| §2.3.3 the digest is over **the buffer**, never a re-read | `RecoveryStore._capture` returns `(source, buffer)` | `test_a_tampered_stored_copy_is_reported_present_and_not_usable` |
| §2.4 verify-and-write; `renamed` and `durable` are two fields | `materializer.restore_configuration`, `RestorationOutcome` | `test_a_complete_restoration_is_durable_and_says_so`, `test_a_rename_without_its_directory_barrier_is_not_a_durable_restoration` |
| §2.4 a record naming another destination restores nowhere | same | `test_a_record_naming_another_destination_restores_nowhere` |
| §2.4 an interrupted restoration leaves the destination alone; its temporary is reported and not removed | same | `test_a_restoration_interrupted_before_its_rename_leaves_the_destination_alone`, `test_a_leftover_restoration_temporary_is_reported_and_blocks` |
| §2.5 discovery is `readdir` of the recovery parent | `RecoveryStore.discover` | `test_discovery_is_a_listing_of_the_recovery_parent` |
| §5.3 open existing, `flock`, never create, never unlink, never break | `execution/host_lock.py` `HostLock` | `test_an_absent_lock_refuses_and_is_never_created`, `test_a_held_lock_refuses_rather_than_proceeding`, `test_the_lock_file_is_never_unlinked_or_replaced` |
| §5.4 two durable objects, one publication path | `execution/lifecycle_record.py`, `execution/run_ledger.py` over `lifecycle_storage` | `test_verified_first_use_writes_a_durable_record`, `test_serialized_history_is_what_reaches_the_disk` |
| §5.5 bounded, versioned schema; a refusal returns no entries | `ReservationRecord.read` → `parse_history` | `test_a_tampered_stored_record_refuses_and_is_never_normalized` (ten tampers + the positive control) |
| §5.6 re-seal before the content is acted on; needs no write permission | `ReservationRecord.reseal`, `LaboratorySession.admit` | `test_the_reseal_needs_no_write_permission_and_is_idempotent`, `test_a_failed_reseal_refuses_the_whole_pass` |
| §5.6 the three publication points, and R3-1's visible-not-durable one | `DurableRecordStore.publish` over `PosixFilesystem` | `test_an_interruption_at_each_publication_point_is_distinguished` (×3) |
| §5.8 fail-closed admission, ledger required | `LaboratorySession.admit` → `read_and_admit` | `test_a_missing_ledger_directory_refuses_rather_than_reading_as_empty`, `test_a_provisioned_ledger_observed_empty_still_admits` |
| §5.10 verified first use, with every refusal and recovery | `ReservationRecord.initialize` | five initialization tests, including `test_a_missing_record_on_a_used_host_is_never_reinitialized` |
| §5.11 all seven write a run entry; no exemption, and the reset least of all | `execution/run_ledger.py` `ParticipantRunLedger` | `test_every_participant_completes_and_blocks_until_it_does` (×7), `test_an_unsettled_run_refuses_every_successor_including_the_reset` |
| §5.11 a clean wrapper exit is not completion evidence | same | `test_a_clean_wrapper_exit_is_not_completion_evidence` (×7) |
| §5.11.1 P9 the start's binding shape, both directions | same | `test_a_harness_start_with_no_reservation_refuses_at_the_writer`, `test_the_six_carry_the_binding_exactly_empty` (×6) |
| §5.12 step 0 before the release decision; a mismatch publishes nothing | `run_ledger.TerminalSequence.conclude` → `conclude_reservation` | `test_the_wrong_reservation_conclusion_publishes_nothing` |
| §5.12 the binding is not inferred from the run's name | same | `test_the_binding_is_not_inferred_from_the_run_name` |
| §5.12 failure between the two publications blocks | same | `test_failure_between_the_release_and_the_completion_blocks` |
| §6.2 four descriptor-relative verbs; 16 → 20; `BOOTSTRAP_VERBS` unchanged at 2 | `execution/case_program.py`, `case_runtime.py` | `test_the_two_new_verbs_name_one_flag_each_and_take_no_flag_argument`, `test_the_reviewed_prefix_is_accepted_for_every_verb` |
| §7 V1–V5, V7, V9 as definitions | `provisioning.py` | `test_the_production_layout_is_data_and_no_test_builds_over_it` |
| §8.2 the recovery procedure names the independent store | `cleanup.RECOVERY_PROCEDURE` steps 2–4 | `test_the_configuration_recovery_names_the_independent_store` |

### r6 §9 matrix rows this pass moves

Rows **1–12c** (effect ownership, the barrier graphs, the removal post-check,
the descriptor modes and their negative controls) and rows **13–69** were
`[M]` — modelled over a dictionary. They stay `[M]` and are unchanged.

What this pass adds is a **mechanism column** for the rows that were `[P]`
because they needed the mechanism, and for a subset of the `[M]` rows that can
now also be run against real descriptors:

| Row | Status before | Status now |
|---|---|---|
| 13 lock file absent | `[P]` | mechanism: `test_an_absent_lock_refuses_and_is_never_created` |
| 14 lock held by another participant | `[M]` | also mechanism: `test_a_held_lock_refuses_rather_than_proceeding` |
| 15/15b/15c record `RUNNING`/`ADMITTED`/malformed | `[M]` | also mechanism: `test_an_admitted_record_refuses_even_with_a_free_lock`, `test_a_tampered_stored_record_refuses_and_is_never_normalized` |
| 16 lock free, record `RELEASED`, bound | `[M]` | also mechanism: `test_a_provisioned_ledger_observed_empty_still_admits` |
| 16b–16d first-use initialization, fresh/used/interrupted | `[M]` | also mechanism: the five initialization tests |
| 19 renamed, barrier failed, process-only restart | `[M]` | also mechanism: `test_an_interruption_at_each_publication_point_is_distinguished[record-entry]` |
| 29/30/31 unsettled predecessor, clean exit, clean completion | `[M]` | also mechanism, all seven participants |
| 32/34 attributable recovery, leftover temporary | `[M]` | also mechanism |
| 35 first-use history for another approved target | `[M]` | also mechanism: `test_a_record_for_another_approved_target_refuses_all_seven` |
| 44 duplicate terminal delivery | `[M]` | also mechanism: `test_a_duplicate_terminal_entry_refuses_explicitly` |
| 53/54 the R5 wrong-binding reproduction | `[M]` | also mechanism: `test_the_wrong_reservation_conclusion_publishes_nothing` |
| 63 the binding is not read from the filename | `[M]` | also mechanism |
| 66 failure after the release and before the completion | `[M]` | also mechanism |
| I1 `fsync` on `O_PATH` vs on the `O_RDONLY` directory descriptor | implementation check, unperformed | **performed on this workstation's ext4**, both directions. **Not performed on the target** |

**I2–I11 remain unperformed.** In particular **I8** — that a participant holding
only read and search can really `fsync` the record's directory — is exercised
here as the same *user* that owns the temporary directory, which is not the
permission situation the target presents. It is **not** evidence for V8.

---

## 3. Files and interfaces

### Added — six sources, two test files

| File | Lines | What it is |
|---|---|---|
| `tools/phase_5_0_evidence/execution/descriptors.py` | 1 032 | r6 §1.3's inventory and `PosixFilesystem` |
| `tools/phase_5_0_evidence/execution/host_lock.py` | 398 | §5.3's lock adapter and `LaboratorySession` |
| `tools/phase_5_0_evidence/execution/lifecycle_record.py` | 319 | the reservation record on disk |
| `tools/phase_5_0_evidence/execution/run_ledger.py` | 307 | the run ledger and §5.12's sequence on disk |
| `tools/phase_5_0_evidence/execution/recovery_store.py` | 662 | §§2.2–2.5's independent store |
| `tools/phase_5_0_evidence/provisioning.py` | 429 | §7's V1–V5, V7, V9 as data |
| `tests/phase_5_0_evidence/lab_fixtures.py` | 202 | a laboratory under `tmp_path` |
| `tests/phase_5_0_evidence/test_lab_implementation.py` | 1 873 | 106 mechanism tests |

### Changed

| File | Change |
|---|---|
| `execution/case_program.py` | `DIRFD` and `COMPONENT` argument kinds; `openat`, `unlinkat`, `renameat`, `fstatat`; `validate_dirfd`, `validate_component`, `_require_directory_fd`. **No new import**: `S_IFMT`/`S_IFDIR` are literals rather than a widened permitted-import set |
| `case_runtime.py` | the matching two kinds, the four `VerbSpec`s and their planner-side validation |
| `execution/executor.py` | `DescriptorBoundEffects`, `EffectRefused`, `RemovalRecord`, `QUIESCENCE_COST`, `POST_CHECK_ESTABLISHES`, the two `ioctl` request numbers and two flag constants |
| `execution/materializer.py` | `RECOVERY_BASIS_RULE`, `publication_permits_mutation`, `RestorationOutcome`, `restore_configuration`, six restore refusals, `MATERIALIZATION_RECOVERY_BASIS_MISSING` |
| `cleanup.py` | `RECOVERY_PROCEDURE` steps 2–4 now name the independent store and refuse `R/before` — r6 §8.2 |
| `feasibility.py` | `RecoveryRun.as_fields`, `producer_records`, `producer_report` — the C-7 producer-to-importer adapter |
| `review_manifest.py` | `MANIFEST_VERSION` 10 → 11; `COVERED_SOURCES` 36 → 42 |
| `tests/web/test_p3_4_static_assets.py` | the six new sources declared in the watched-prefix allowlist |
| `tests/phase_5_0_evidence/test_no_execution.py` | the six new modules declared in their tiers |

### Interfaces a reviewer should read first

* `DescriptorInventory.bind_synchronizable` — the comparison the whole
  descriptor story rests on, in nine lines;
* `RecoveryStore.publish` — the ordered barrier sequence, with the verification
  after it and labelled as not a barrier;
* `materializer.restore_configuration` — all temporaries written and
  synchronized before any rename, and `durable` set only after the last barrier;
* `run_ledger.TerminalSequence` — the docstring is §5.12's argument, and the
  code is four lines that delegate to the shared `conclude_reservation`.

---

## 4. Failing-before, passing-after, negative controls

### Failing-before — the two places an implementation seam existed

Most of this pass is new modules. A new module has no seam, so there is no
failing-before to produce for it and none is claimed. **Two changes did have
one**, and both were run with the new tests against the pre-change
implementation, in a scratch copy:

```text
tools/ reverted to the submitted cleanup.RECOVERY_PROCEDURE and the
16-verb tables; tests/ kept at the submitted state

FAILED test_plan_and_cleanup.py::test_the_configuration_recovery_names_the_independent_store
FAILED test_r16_c6_c7_c8.py::test_the_two_new_verbs_name_one_flag_each_and_take_no_flag_argument
2 failed, 230 passed
```

The first fails on the step-2 text; the second on the two absent argument kinds.

### Negative controls — nine single-point reversals

Each reversal removes **exactly one** load-bearing conjunct in a scratch copy
of `tools/`, with `tests/` unchanged, and the whole
`tests/phase_5_0_evidence` suite is then run. A check nothing catches is a check
that was not load-bearing.

| # | What is removed | Failures |
|---|---|---|
| 1 | the identity comparison in `bind_synchronizable` | **1** |
| 2 | this module's refusal of `fsync` on an `O_PATH` description | **1** |
| 3 | the refusal to traverse a synchronizable descriptor | **1** |
| 4 | exclusive publication, leaving a plain rename | **1** |
| 5 | the barrier-set re-check in `publication_permits_mutation` | **6** |
| 6 | reporting a rename without its barrier as durable | **1** |
| 7 | the quiescence gate | **3** |
| 8 | the removal pre-check's comparison | **1** |
| 9 | letting the lock adapter create an absent lock | **1** |

All nine applied together: **16 failed, 2 052 passed**.

The suite's own preserved positive controls hold under every reversal — a matrix
in which the weakened version also fails everything is a matrix that is not
testing the checks.

### Passing-after

`tests/phase_5_0_evidence`: **2 074 passed, zero skipped** (from 1 936 at the
submitted tree). The new file contributes **106**; the rest are the
parametrizations the new verbs and covered sources add to existing tables.

**One test was replaced rather than added**, and it is named because replacing a
test is a thing a reviewer should see:
`test_the_configuration_recovery_does_not_present_the_captures_as_trusted`
pinned the interim wording for a store that did not exist, and is now
`test_the_configuration_recovery_names_the_independent_store`, asserting the
r6 §8.2 text in both directions — the independent location is named, and
`R/before` appears only as the thing not to use.

---

## 5. Security analysis

### Descriptor binding

The property is that **no effect is bound to a pathname re-resolved after
ownership was checked**. Three mechanisms carry it and each is separately
defeatable, which is why each has its own control:

* **B1** — `mkdirat`/`openat` with `O_CREAT|O_EXCL|O_NOFOLLOW`. Success proves
  nothing existed at the name. `EEXIST` refuses, and the refusal is the kernel's.
* **B2** — every effect after the lookup lands on the descriptor: `fchmod`,
  `fchown`, `fsync`, `ioctl`, `write`. `fchmod` rather than a `chmod` by name is
  deliberate in the recovery store: the mode lands on the object the descriptor
  holds, so a replacement of the name cannot receive it.
* **B3** — the quiescence gate, which is a **prerequisite** of name-based
  removal and not a detector of its failure. It refuses on three inputs —
  unobserved, observed false, incomplete — and none defaults to true.

**The residual exposures, stated rather than closed.** The removal's final
component is not bindable by any syscall available here, and the post-check is
an absence check: `test_the_post_check_cannot_tell_the_two_removals_apart`
constructs the counterexample and asserts the two runs are indistinguishable to
the production observation. In-place mutation of a file whose inode is unchanged
is not covered by a descriptor at all, and is unchanged from r6 §1.4.4. The
interval between `openat` and `fstat` is detection, not prevention.

### Lifecycle durability

The publication order is bytes → rename → containing entry, every time, and the
mechanism inherits it from the one `DurableRecordStore.publish` the model uses.
There is **no stored durability flag in any form**: a writer that could record
*"this was made durable"* would have had to survive the barrier to write it.
`PosixFilesystem` deliberately has **no durable-state accessor** — the model's
`durable()` exists so a test can see what a power loss would keep, and a reader
with that fact would be a reader holding something the mechanism does not have,
which is R3-1 in one sentence.

The re-seal is the successor's obligation, needs read and search and **no write
permission**, and a failure refuses and names a recovery owner rather than
proceeding on a visible name.

### Identities

All seven participants are the shared `ubuntu` identity, by the 2026-09-12
maintainer direction. `provisioning.IDENTITY_NOTE` says at the mode table what
that means: the modes are **accident guards, not barriers between the
participants**, because one UID with passwordless `sudo` is not constrained by
either object's mode. Nothing in this implementation treats a mode as a security
boundary between participants, and nothing claims V10 is confirmed.

The recovery store's `0700 root:root` parent **is** a real boundary against an
experimental identity — and it is unprovisioned. Until V5 is applied it is a
definition.

### Participant completion

A caller's participant, run id and reservation are **checked claims**, compared
with the stored start before anything is derived from them; the stored start is
the only binding. The harness's two conditions are lifecycle-owned and derived
from the release decision and the release publication this process performed;
an injected observation of either refuses. A free lock, a wrapper's exit status,
an elapsed deadline and an absent quarantine record are each refused as
completion evidence, and the wrapper-exit refusal is asserted for all seven.

**What the mechanism does not do, and it is the largest residual:** it observes
no process, no database backend and no tree. The six participants' external
conditions are injected and attributable, and r6 §9.3's **I9** — whether each is
observable at all — is unperformed for all five it names. A completion condition
nobody can observe is a run that never settles.

### Recovery

Recovery is attributable, append-only and never reuses an identity: every
publication re-serializes the prior entries verbatim and appends one, a history
that will not parse refuses the append outright, and a recovered run's own id is
refused by exclusive creation. Every leftover temporary — publication,
restoration or ledger — is **reported and never removed automatically**, in all
three stores.

### Refusal messages

Every refusal this pass adds carries a **fixed classification from a closed
vocabulary** and a **role name**, never a path, never a byte of the content it
refused, never an operating-system message, never a credential and never player
data. `DescriptorRefused` refuses a classification outside its vocabulary at
construction; `LockRefused` does the same. `test_a_refusal_names_a_role_and_never_a_path`
asserts the absence of the path and of the OS text on a real failure.

Two places were checked specifically because they are where hostile bytes could
reach an operator: the record parser's refusals come from
`lifecycle_storage`'s existing closed `RecordRefusal` vocabulary and carry no
stored bytes, and the recovery store's discovery reports names and reasons from
a fixed set rather than the content it failed to decode.

---

## 6. Two deviations from r6 §6.2, and one gap in the accepted contract

These are the items I most want a reviewer to rule on. All three are recorded in
the source as constants, not only here.

**D1 — `RENAME_NOREPLACE` is not reachable, and the substitute is `linkat` +
`unlinkat`.** Python 3.12's `os` exposes `renameat` and not `renameat2`, and
`ctypes` is refused outside `case_program._prctl_get_securebits` by a structural
guard that is a stop condition. `link(2)` fails with `EEXIST` when the
destination exists, so exclusivity is the kernel's rather than a check this
module performs. The exact difference: `renameat2` leaves no temporary on
success and this sequence leaves one if the process stops between the two calls
— a state the publication path already reports and never cleans, so it fails
closed. **A consequence worth ruling on:** the publication path no longer
depends on `RENAME_NOREPLACE`, so preflight item **V6** is no longer a
prerequisite of it. V6 remains unconfirmed and is not closed by that.
(`descriptors.EXCLUSIVE_PUBLICATION_SUBSTITUTE`.)

**D2 — a listing descriptor is not in r6 §1.3.3's inventory, and `readdir` is
required.** §2.5's recovery discovery and §5.11's ledger survey both list a
directory, and the contract enumerates neither a descriptor for it nor a
permitted use on an existing one. `DescriptorInventory.listing` opens a third,
short-lived descriptor `.`-relative to the traversal descriptor, performs one
`readdir`, and closes it; it resolves no name and reaches no object the
traversal descriptor does not already refer to. **This is a gap in an accepted
contract and I am reporting it rather than treating the addition as authorized.**
(`descriptors.CONTRACT_GAPS`.)

**D3 — `plan.PERMITTED_EXECUTABLES` is still 22, not r6 §6.4's 20.** Removing
`/usr/bin/install` and `/usr/bin/chattr` requires the **plan generator** to stop
emitting steps that use them, which changes the reviewed argument vectors
themselves across `concrete_plan.py`'s provisioning, flag-setting and restore
steps. r6 §6.1's row for `plan.py` asks for *"coverage for the six new modules;
no new executable"*, and §6.4's table is captioned *"After, **if built**"*. The
executor-side replacements for P1, P1b, P2, P4 and L3 are built and tested; the
generator migration that would retire the two binaries is a separate, reviewable
slice and I did not take it inside this authorization. **The two executables
remain permitted and the plan still names them.**

---

## 7. C-7 producers

The three producers existed. What did not was the **adapter** that renders a
producer run as the importer's record, so the producers computed classified
records while the importer accepted hand-written ones and nothing joined the
two. `feasibility.producer_records` closes that: eight records, one per variant
of all three cases, every field read off a real producer run.

**It resolves C-7 for nobody, and the assertions say so in the strongest form
available:**

* every record carries `SYNTHETIC_TARGET_IDENTITY` and
  `Custody.SYNTHETIC_FIXTURE`, and the same payload pointed at the approved
  target is **refused** by the importer for naming the wrong target
  (`test_the_adapters_records_are_refused_against_the_approved_target`);
* with all eight variants supplied and every record well formed, all three cases
  are still `unresolved`, none is `covered`, `eligible_for_operational_acceptance`
  is `False`, and the importer classifies **nothing at all** — `records == ()`.
  There is not even a passing record for somebody to cite
  (`test_a_complete_producer_payload_still_resolves_no_c7_case`);
* the false-success control runs the **same adapter** under the defective
  arrangement and produces different observations that the band's own classifier
  fails — not an absence, which would be indistinguishable from a producer that
  never ran; and
* `ExternalCase.producer_artifact_reviewed` is still `False` for all three, and
  the manifest pins it.

**Synthetic feasibility is not operational evidence**, and nothing here should
be read as narrowing C-7.

---

## 8. Generated artifacts and the review-only digest

* Generated **three times** through the non-executing CLI
  (`--manifest-out`, `--render`; no `--execute`, no `--confirm-target`). All
  three byte-identical. Installed, then generated a **fourth** time and compared
  with the installed files: byte-identical.
* `COVERED_SOURCES` read from `review_manifest.py`'s **syntax tree** and every
  one of the **42** hashes recomputed independently against the file on disk:
  **zero mismatches**, and the manifest's pinned set equals the AST-read set.
* Six paths **added** (the five execution-tier modules and `provisioning.py`);
  none removed. Ten moved — `case_runtime`, `cleanup`, `execution/artifact`,
  `execution/case_program`, `execution/executor`, `execution/materializer`,
  `feasibility`, `journal`, `observations`, `review_manifest`. `artifact.py`,
  `journal.py` and `observations.py` carry the **uncommitted LAB-1 remediation**
  already in the working tree, which this pass preserved and did not touch.
* `manifest_version` **10 → 11**; `supplied_observations.schema_version` stays
  **3**; the run-record schema stays **3**; `is_executable` **False**;
  `unresolved conflicts 3 (C-7)`; `unconfirmed facts` still the twelve.
* Digest: `aabba2d718f5c0231c2b92b177e733fca7e6ce3c5c85283dda4730b14c3c91d4`.
  **Review input only. It must not be passed to `--execute`.**

---

## 9. Commands, interpreters and results

**Restricted local pass, `TEST_DATABASE_URL` unset**, as the authorization
requires. The canonical `oracle-test` interpreter
`/opt/freedom-blades/runtime/venv-web/bin/python` exists on this workstation and
**has no pytest**, and `oracle-test` may not be reached under C-P5.0-LAB-I, so
the same restricted-local exception the two accepted LAB-1 handbacks used
applies: `/opt/discord-bots/venv-web/bin/python` and
`/opt/discord-bots/venv/bin/python`, both Python **3.12.3** with pytest
**8.4.2**, and node **v24.20.0**.

| Command | Result |
|---|---|
| `python -m pytest -q -rs tests/phase_5_0_evidence` | **2 074 passed, 0 skipped** |
| `python -m pytest -q tests/phase_5_0_evidence/test_lab_implementation.py` | **106 passed** |
| `python -m pytest -q tests/phase_5_0_evidence/test_no_execution.py` | **243 passed** |
| focused LAB set (feasibility, plan_and_cleanup, r13, r16_c6_c7_c8, r16_remediation, lab_implementation) | **476 passed** |
| `python -m pytest -q -rs tests/test_*.py` (bot) | **3 024 passed, 326 skipped** |
| `python -m pytest -q tests/web` (web) | **1 609 passed, 1 failed, 1 362 skipped** |
| `node --test foundry-module/tests/*.test.mjs` | **171 passed** |
| `python -m compileall -q tools/phase_5_0_evidence tests/phase_5_0_evidence` | succeeded |
| `git diff --check` | clean |
| `python3 .claude/hooks/test_guards.py` | **31 cases, 19 refused and 12 allowed, all passed** |

**Every skip is unverified.** The database-enabled web baseline is **80**, not
1 362; the 1 362 figure is what an unset `TEST_DATABASE_URL` produces and it
still exits 0. The bot suite's 326 are the same class.

**The one web failure is pre-existing and unrelated, and I verified that rather
than citing the earlier handback**: `test_the_discovery_enumerates_untracked_files_rather_than_directories`
asserts this tree contains an untracked *directory*; with the entire working
tree stashed including untracked files, it still fails. Two other failures in
that module **were** mine — the six new sources were undeclared in the watched-
prefix allowlist — and are fixed by declaring them.

**Checks not run, and why.** No formatter, linter or type checker is configured
in this repository or installed in either environment — `black`, `ruff`,
`flake8`, `mypy`, `pyright` and `isort` are all absent and there is no
configuration file for any of them. That is **unavailable, not a pass**. The
bot, web and Foundry suites were run on this workstation and not on
`oracle-test`, which this authorization excludes.

---

## 10. Provisioning definitions — **none applied**

`provisioning.py` defines seven of r6 §7's ten items: **V1** the `freedomlab`
group, **V2** `ubuntu`'s membership, **V3** the `systemd-tmpfiles` fragment with
its exact two lines, **V4** the laboratory directory, **V5** the recovery parent,
**V7** the initialized `lifecycle.json` with a first-use **template** whose
attester, basis and target are placeholders, and **V9** the setgid/sticky ledger
directory.

* `ProvisioningItem.approved` is a property that returns `False` and takes no
  constructor argument. There is no way to write an approved item.
* Nothing in the module creates a group, writes a file, installs a fragment,
  changes a mode or runs a command, and `test_no_execution.py` asserts that
  against the source.
* **No object was created under `/run`, `/var/lib` or `/etc`**, and
  `test_the_production_layout_is_data_and_no_test_builds_over_it` asserts all
  three production paths are **absent** — so a run that provisioned one by
  mistake fails the suite.
* **V6, V8 and V10 are deliberately not defined.** They are observations of the
  target, and a value written here would be the substitution EH-R16-4 refused in
  a different costume. `UNCONFIRMED_TARGET_FACTS` names them and carries none.

---

## 11. Rollback

Repository changes only; nothing was deployed, migrated or provisioned.

1. Delete the eight added files: `tools/phase_5_0_evidence/execution/{descriptors,host_lock,lifecycle_record,run_ledger,recovery_store}.py`,
   `tools/phase_5_0_evidence/provisioning.py`,
   `tests/phase_5_0_evidence/{lab_fixtures,test_lab_implementation}.py`.
2. `git checkout --` the changed files listed in §3, **except** that
   `execution/artifact.py`, `journal.py`, `observations.py`, `cleanup.py`,
   `feasibility.py` and `review_manifest.py` also carry the previously
   uncommitted LAB-1 remediation, which must be preserved. Revert those six by
   removing only the hunks §3 attributes to this pass.
3. Regenerate the manifest and concrete plan through the non-executing CLI; the
   digest returns to `6ef61afbaa96dcbd5eda408eed5042aff3a227ce32cb56b149111e531f7a2408`.
4. There is nothing else: no migration, no schema change, no configuration
   applied to any host, no service touched and no bot restart.

---

## 12. Unconfirmed target facts and unresolved gates

**All twelve target facts remain unconfirmed** — `interpreter_sha256`,
`interpreter_real_path`, and E7's ten. The CLI still reports each as refusing
the executor before any command starts.

**The r6 §7 preflight items remain unperformed:** V6, V8 and V10. The shared-
identity *choice* is recorded; the *fact* that all seven run as `ubuntu` is not.

**No item of the ten-item §7 delta is provisioned.**

**Gates unchanged:** C-7 unresolved; EH-R16-1 **Open**, with the harness's
unconditional real-execution refusal in force; `is_executable` **False**;
Package 5.0 **not ready**; package-level P5.0-R5 **Blocking**; OD-62 **Open**.
LAB-1's local remediation stays closed on the R3 re-review and is not reopened
by this pass.

**Nothing was executed, provisioned or inspected.** No SSH, synchronization,
host inspection, preflight, permission or group change, `systemd-tmpfiles`,
provisioning, creation of any `/run` or `/var/lib` object, database operation,
destructive drill, service change, dependency installation, generated-vector
execution, `--execute`, real boundary or materializer use, migration,
deployment, cutover, commit, push, reset, history rewrite or bot restart. No
credential or secret file was read. Both Codex review records were left
untouched.

---

## 13. Focused questions for independent technical and security review

1. **D1 — is `linkat` + `unlinkat` an acceptable substitute for
   `renameat2(RENAME_NOREPLACE)`?** The alternative is a second `ctypes`
   exception, which the structural guard refuses and which is a decision about
   the trusted computing base. If the substitute is accepted, does V6 stay a
   preflight item for anything else?
2. **D2 — the listing descriptor.** The contract requires `readdir` and
   enumerates no descriptor for it. Is the short-lived `.`-relative descriptor
   the right answer, or should §1.3.2's permitted-use set be widened explicitly?
3. **D3 — `PERMITTED_EXECUTABLES` stays at 22.** Is deferring the plan
   generator's migration off `install` and `chattr` the right scope boundary, or
   should it have been inside this authorization?
4. **Is reusing `lifecycle_storage`'s validators the right call**, or does a
   mechanism that shares its rules with a model risk the model's limits being
   read as the mechanism's guarantees? I believe sharing is strictly safer —
   two readers are what every finding since R3-1 has been about — but it is the
   central architectural decision here and it should be ruled on rather than
   inherited.
5. **`DescriptorRefused` subclasses `ModelRefused`** so that one publication
   path catches a real barrier failure exactly as it catches a modelled one. The
   name is the model's. Is the sharing right and the name a defect to fix, or is
   the sharing itself wrong?
6. **Security: are the fixed refusals bounded enough?** Each carries a
   classification and a role. Is a role name — `journal`, `runstore:<run-id>` —
   already too much for an operator-facing artifact, given a run id is
   caller-supplied?
7. **Security: `PosixFilesystem.close` refuses to close an inventory-held
   descriptor**, so a caller cannot take a barrier away from a later
   publication. Is that the right place for the rule, or should the inventory
   own the whole descriptor table?
8. **I8 and I9.** I8 is exercised only as the directory's own owner, which is
   not the target's permission situation; I9 is untouched. Both are the largest
   remaining gaps between this implementation and a mechanism that would work on
   `oracle-test`. What would a read-only preflight have to observe to close
   them?

**Stop point.** No read-only preflight, provisioning or execution follows
automatically. The next checkpoint is independent Codex technical and security
review of this implementation.
