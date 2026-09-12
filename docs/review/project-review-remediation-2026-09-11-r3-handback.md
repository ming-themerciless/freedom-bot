# Handback — complete lifecycle remediation (R3)

> **Dated errata, 2026-09-11 — added after the [R4 re-review](project-review-2026-09-11-r4.md).**
> Four claims in this handback are corrected. Nothing else in it is rewritten,
> and the findings it reports are preserved as reported.
>
> | # | Claim in this handback | Correction |
> |---|---|---|
> | **E9** | §2's *"two connected lifecycle traces read the bytes their predecessors wrote, through initialization, admission, operation, crash, recovery and successor admission"*, offered as establishing the complete sequence | **partly withdrawn.** The traces did read stored bytes, and that part stands. But the successful one published the harness's completion **before** the release its own completion conditions require, and supplied both of those conditions as injected observations while the reservation record still said `running`. The sequence it certified had no reachable successful path — PR-20260911-R4-3 — and the claim that it established the complete terminal sequence is withdrawn. The corrected order is r5 §5.12 and the trace now runs it. |
> | **E10** | §1's and §3's statements that stored histories reach the shared validator and that a contradictory history refuses | **too strong as stated.** The *binding* reached the validator, which is what R3-3 asked for and what the R4 review recommended closing. But the order rules did not require a transition to belong to the currently active reservation, so a stale terminal entry for a finished reservation was accepted and the derivation took the last entry — PR-20260911-R4-1. r5 §5.5 replaces the rules with a state machine over the current reservation. |
> | **E11** | §1's statement that durable in-progress and completion accounting for all seven participants means an interrupted run of any of them blocks every successor | **true only for a run whose file is a valid run history.** The accounting compared no participant, run id, identity or filename with the stored start, checked evidence for presence rather than content, and classified a file from its last entry alone; and an omitted ledger skipped accounting entirely — PR-20260911-R4-2. r5 §5.11.1 adds the validator and r5 §5.8 requires the ledger. |
> | **E12** | This handback's suite figures — structural 217, harness 1723, bot 3018/326, web 1610/1362, Foundry 171 — and the review-input digest `45b3c6c0313e5cb8b48e116aea7716b47f1a2d231f12719975d63166d3458201` | **evidence about the pre-R4 tree only.** Covered source has changed since. The [R4 handback](project-review-remediation-2026-09-11-r4-handback.md) carries its own figures and its own digest. |
>
> The R4 re-review's positive recommendations are preserved: the
> target/attribution repair (R3-3) is recommended for closure in its stated
> scope, and the successor directory barrier under the file-before-rename writer
> contract is technically supported as design evidence.

Date: 2026-09-11. Author: Claude, working Technical Lead for C-P5.0-LAB-1.
Answering: [independent re-review `project-review-2026-09-11-r3.md`](project-review-2026-09-11-r3.md),
under [the bounded remediation prompt](project-review-remediation-2026-09-11-r3-claude-prompt.md).

**Status: returned to Codex for technical re-review. Nothing here is accepted, no
finding is closed on the implementer's authority, no digest is approved for
execution, and no privileged mechanism, filesystem writer, lock adapter,
operational integration, provisioning, host action or preflight was performed.**

Package 5.0 remains **not ready**, P5.0-R5 **Blocking**, OD-62 **Open**,
EH-R16-1 **Open**, LAB-1 **Important and unimplemented**.

Submitted design, **not accepted and not implemented**:
[runner contract r4](phase-5-0-reserved-laboratory-runner-contract-r4.md), which
supersedes [r3](phase-5-0-reserved-laboratory-runner-contract-r3.md) in its
entirety. r3 now carries a dated supersession and a five-item erratum; the
[R2 handback](project-review-remediation-2026-09-11-r2-handback.md) carries
dated errata **E6–E8**.

New review-input digest, **not execution approval**:
`45b3c6c0313e5cb8b48e116aea7716b47f1a2d231f12719975d63166d3458201`.
It supersedes `55af840fbb28f0ea8ae447e732644c5b2f81dace83f6ccd499f24ebc8864cff2`
because covered source changed. **Do not pass either to `--execute`.**

---

## 1. The three findings, and where each is answered

All three had one cause and are answered as one lifecycle rather than three
patches: **r3 specified a record and never specified the act of reading one.**

### 1.1 PR-20260911-R3-1 — Blocking — failed initialization leaves an admissible-looking record

| | |
|---|---|
| **Accepted** | in full. The reproduction is reproduced unchanged and is now a permanent regression |
| **r4 sections** | §5.6 (publication, the restart gap, the re-seal), §5.7 (T1, T3, T7, T8, T12, T15 and their uncertainty columns), §5.9 (refusal paths), §5.10 (`not_durable` corrected) |
| **The mechanism** | a rename is visible immediately and durable when the containing entry is synchronized **[D]**. Between those points the record is readable and would not survive a power loss, and the writer's knowledge of which case it is in dies with the writer. A **process-only restart** leaves the filesystem untouched — and r3's model called the power-loss operation for both, which is why nothing showed |
| **The correction** | the successor **establishes** the durability rather than asking about it: under the lock, before acting on the content, it `fsync`s the record's and the ledger's **containing directory entries** through `O_RDONLY` descriptors. It is idempotent, so the reader never has to know which case it was in. If it fails, the participant publishes nothing, takes nothing and names the recovery owner |
| **The permission implication, resolved** | the re-seal needs **read and search on a directory and no write permission on anything**. So the root-written record stays root-written and the six ordinary participants discharge the obligation exactly as the executor does. This is r4 §5.6 and it adds nothing to the permission delta |
| **What it does not establish, stated** | not that the bytes are complete. A visible final name implies the bytes barrier returned success **only because the specified order puts it before the rename** — a labelled design inference, falsifiable by a writer that renamed first. A power loss keeping the entry and losing the bytes leaves a **truncated** record, which §5.5 refuses rather than reading as the shorter history its prefix spells |
| **No stored durability claim** | the record carries no `durable` field in any form, and a test asserts the string does not appear in the stored bytes. A writer that could record it would have had to survive the barrier |
| **Regressions** | `test_r3_lifecycle.py`: `test_the_reviewers_reproduction_still_reproduces_against_the_writer`, `test_a_process_restart_and_a_power_loss_are_different_events`, `test_the_revision_3_protocol_admits_on_a_record_a_power_loss_removes` (**negative control**), `test_a_successor_establishes_the_durability_the_writer_could_not`, `test_a_failed_re_seal_refuses_pending_an_attributable_recovery`, `test_a_concurrent_participant_arriving_during_initialization_waits`, `test_a_successful_durable_initialization_admits_every_participant`, `test_every_publication_point_carries_the_same_uncertainty` (3 cases), `test_a_release_that_never_reached_its_barrier_still_refuses_a_successor`, `test_recovery_never_overwrites_a_valid_prior_history`, `test_an_unreadable_history_is_never_replaced_by_a_recovery`, `test_a_partial_history_refuses_rather_than_selecting_an_earlier_entry`, `test_the_re_seal_needs_no_write_permission_and_says_so`, `test_the_record_carries_no_durability_claim_a_reader_could_believe` |

**The oracle restriction the review asked for is enforced structurally.** No
function in `lifecycle_storage.py` consults the model's durable-state map:
`test_the_lifecycle_model_makes_no_oracle_observation` parses the module and
refuses the attribute names `entry_is_durable` and `durable`. The initializer's
own `entry_is_durable` post-check, which r3 had, is **removed** — a real writer
knows durability only from `fsync` returning success, and consulting the oracle
is exactly the observation R3-1 says no reader has.

### 1.2 PR-20260911-R3-2 — Blocking — ordinary participant crashes bypass lifecycle protection

| | |
|---|---|
| **Accepted** | in full. **No exemption is proposed for any participant**, and r3 §5.5's *"a crashed test run is not a reservation and must not block the host forever"* is withdrawn as stated |
| **r4 sections** | §5.2 (all seven write a run entry), §5.4 (the two objects and their permissions), §5.11 (the per-participant table), §5.7 (T5, T6, T10, T11, T16), §5.9 |
| **The accounting** | each participant persists its **non-reusable state before its first relevant effect** and publishes **reusable completion only after its stated conditions are observed**. An unsettled or unreadable run refuses every successor — the harness and the environment reset included — until a recovery is published |
| **Never completion evidence** | a free lock (`flock(2)` releases on descriptor close, whether or not the run finished **[D]**), a wrapper's exit status, an elapsed deadline, an absent quarantine record |
| **Permissions, resolved rather than assumed** | the reservation record is root-written and six participants cannot write it. Making it group-writable would buy nothing, because a group-writable record is one any participant can replace whole. So the ledger is a **separate group-writable directory** (`3770`, setgid and sticky) and the record keeps its stricter mode. This is the one new write permission for ordinary participants and it is **V9**, unapproved |
| **What the modes do not do, said plainly** | all seven run as the same OS user and that user holds passwordless `sudo`, so neither mode constrains a participant that ignores the protocol. They prevent accidents. Separating the seven identities is the only thing that would make them a barrier; it is **V10**, a preflight fact **and** a decision request, and it is unapproved |
| **The "forever" concern, answered differently** | an interrupted run blocks until its recovery is **published** — a bounded, attributed operator action with a named owner, not an indefinite dead end. Row 32 of the matrix is the control that shows a recovered host admitting a new run |
| **The reset's exemption refused especially** | it is the participant whose effect is the destruction of the evidence an earlier interruption left, so it is the one that must not run into unresolved state |
| **Regressions** | `test_every_participant_has_an_identity_writer_lifetime_and_recovery`, `test_the_non_reusable_state_is_persisted_before_the_first_effect`, `test_a_clean_wrapper_exit_and_a_free_lock_are_not_completion_evidence` (**negative control**), `test_an_uncertain_predecessor_blocks_every_successor` (**5 injected interruptions × 7 successors**), `test_clean_completion_admits_the_next_participant`, `test_a_verified_recovery_admits_a_new_run_without_a_dead_end`, `test_a_recovery_preserves_the_interrupted_runs_own_history`, `test_a_recovered_runs_own_identity_is_never_reused`, `test_an_interrupted_ledger_publication_blocks_and_is_not_cleaned`, `test_the_environment_reset_refuses_especially_while_a_quarantine_exists`, `test_the_proof_obligations_are_named_and_unperformed` |

**The five injected interruptions are the ones the review named**: a wrapper
that died with a child surviving; a wrapper that died with a server-side
transaction unsettled; a partial synchronization; an interrupted dependency
update; an interrupted environment reset. Each leaves exactly **one** stated
completion condition unobserved, and the refusal names that condition — so the
refusal is attributable to it rather than to an empty observation.

**Operation-specific proof obligations that need future target evidence**, named
in r4 §5.11 and collected as **I9**: that a database backend can be attributed
to one run at all; that the two suites' backends are distinguishable on the
shared cluster; that `node --test` workers are enumerable as children; **what
the synchronization's whole-tree consistency check concretely is on the
target**; that the dependency check detects a half-unpacked distribution rather
than only a missing one; that the reset's declared baseline is observable.
**None has been performed.** A completion condition nobody can observe is a run
that never settles, and that is a real residual risk rather than a formality.

Nothing infers settlement from a stopped client, permits the reset to erase
unresolved evidence, kills an unknown process or turns a deadline into takeover
authority.

### 1.3 PR-20260911-R3-3 — Important — first-use and recovery histories lose target binding

| | |
|---|---|
| **Accepted** | in full. The reviewer's synthetic check admitted 7/7 against two different target identities; it now refuses 7/7 against the wrong one and admits 7/7 against the right one |
| **r4 sections** | §5.5 (the bounded versioned schema and its refusals), §5.8 (the shape table, with the binding required for every admitting disposition), §5.10 (initialization's binding refusal) |
| **Repaired in `reservation.py`** | `LifecycleHistory` gains `target_identity`, `first_use_attested_by`, `first_use_basis` and `recovery_authored_by`; `LifecycleShape` gains `target_binding`, `first_use_attestation` and `recovery_author`, stated for all seven dispositions; the validator refuses an absent binding, a wrong binding, a missing attester, a missing basis, a missing recovery author, and each of those fields appearing where its disposition forbids it |
| **Repaired in `lifecycle_storage.py`** | a bounded, versioned record schema with a serializer and a parser; the history-order rules; and `derive_lifecycle_history`, which carries the host, the approved target, the attester, the basis, the release record's author and the recovery's reference and author **out of the stored bytes and into the shared validator** |
| **`BINDING_MISMATCH`** | now has an enforcing branch. Initialization refuses when the record would name a host or target other than the approved one, and no record is created. r3 declared the value with nothing that produced it; the claim is not withdrawn, it is implemented |
| **Refusals, none normalized** | `ABSENT`, `MALFORMED`, `TRUNCATED`, `UNSUPPORTED_SCHEMA`, `CONTRADICTORY`, `HISTORY_ORDER`, `MISSING_BINDING`, `WRONG_BINDING`. A refused parse returns **no entries at all**, because handing back the prefix that parsed is how a truncated history becomes a shorter one |
| **Not a generic event store** | one schema version, ten entry kinds, a fixed field set per kind, no extension point, and six history-order rules each of which exists because breaking it produces a history that would otherwise admit somebody |
| **Regressions** | `test_a_first_use_history_for_another_target_refuses` (**the reproduction**, 7 participants × 2 targets), `test_an_initialization_bound_to_the_wrong_target_refuses`, `test_a_first_use_without_a_complete_attestation_refuses`, `test_the_attestation_survives_the_trip_from_bytes_to_decision`, `test_a_release_and_a_recovery_carry_their_author_and_reference`, `test_a_history_round_trips_through_serialization_and_parsing`, `test_a_tampered_record_refuses_and_is_never_normalized` (**10 stored-field tampers**), `test_a_record_naming_two_hosts_is_refused_rather_than_reconciled`, `test_a_history_that_is_not_one_produces_no_decision_input` (3 cases), `test_the_order_rules_are_stated_and_bounded`; and in `test_reservation.py` the R3-3 section: `test_an_admitting_history_bound_to_another_target_refuses` (3), `test_an_admitting_history_with_no_binding_at_all_refuses` (3), `test_a_first_use_without_its_attestation_refuses_at_the_validator`, `test_an_operator_recovery_without_a_named_author_refuses`, `test_a_predecessor_record_carrying_a_first_use_attestation_refuses`, `test_every_admitting_shape_requires_the_binding_and_its_evidence` |

**The end-to-end claim the review rejected is withdrawn.**
`test_the_initialized_record_admits_every_participant` constructed
`environment_reset_history(HOST)` and handed it to the decision. It is renamed
`test_a_constructed_first_use_history_admits_every_participant`, documented as a
**unit test** that reads no stored byte, and it asserts its own helper's
membership of `lifecycle_storage.UNIT_TEST_CONSTRUCTORS` — the two constructors
that build a history rather than reading one. The connected replacements are the
two lifecycle traces in §2 below.

---

## 2. The complete lifecycle trace, from a fresh process with no prior memory

Traced once before handback, as the prompt requires. Both traces are executed as
tests; nothing below is narration of code that was not run.

### 2.1 The successful lifecycle — `test_a_complete_successful_lifecycle_admits_a_successor_from_stored_evidence`

1. **provisioning.** The laboratory directory and the runs directory exist and
   are durable. Nothing else does.
2. **initialization.** The operator writes one `first_use` entry: temporary
   created exclusively, bytes synchronized, `RENAME_NOREPLACE`, containing entry
   synchronized. Both barriers returned success **in that process**.
3. **first admission.** A process that was not the initializer takes the lock,
   re-seals both parent entries, reads the record's bytes **through a
   descriptor**, parses them against the bounded schema, checks the order rules,
   derives a `LifecycleHistory` carrying the approved target, the attester and
   the basis, and hands it to `reservation.validate_lifecycle()`. Verdict:
   `verified_first_use`, admitted.
4. **ADMITTED**, appended and made durable **before any effect of any kind**.
5. **the participant's own run entry**, published exclusively **before its first
   relevant effect**.
6. **RUNNING**, appended before the first mutating step.
7. **the effects**, injected.
8. **completion**, published only after every stated condition of that
   participant's profile was observed by a named observer.
9. **RELEASED**, appended and made durable.
10. **the process restarts.** Memory gone; filesystem unchanged.
11. **the successor** takes the lock, re-seals, reads the bytes step 9 wrote,
    parses a four-entry history — `first_use`, `admitted`, `running`,
    `released` — validates the release record's binding and author, surveys a
    settled ledger, and is admitted. **Its admission rests on the predecessor's
    stored release, not on a history this test built.**

### 2.2 The failed lifecycle — `test_a_complete_failed_lifecycle_refuses_then_recovers_then_admits`

Steps 1–6 as above, then:

7. **the executor dies** between `running` and any release. Process-only
   restart: its memory is gone and the filesystem is intact.
8. **a successor refuses.** The last reservation entry is `running`, so the
   disposition is `active`; and the ledger holds one unsettled run. Two
   independent refusals, both naming what is unresolved. **The free lock
   authorizes nothing.**
9. **quarantine**, appended by an operator with a reason. The successor still
   refuses.
10. **an unattributed recovery refuses** — no author, no reference, no
    publication.
11. **an attributed recovery** is appended to the run file and an
    `operator_recovered` entry to the reservation record. The quarantine entry
    and the in-progress entry both remain in place, byte for byte.
12. **a new participant is admitted** on the stored recovery, carrying its
    reference and its author. The recovered reservation's **own id is still
    refused**, and the recovered run's own id cannot be reused because exclusive
    creation refuses it.

### 2.3 Every crash window in the transition table

r4 §5.7 has nineteen transitions. **Sixteen are exercised in the synthetic
model**; three are **future implementation checks** because they need the
mechanism:

| Transition | Status |
|---|---|
| T0 provisioning | **[P]** — future implementation check. Nothing here provisions |
| T9 the reviewed effects | **[P]** — needs the executor, the boundary and the materializer |
| T14 the deadline path to `RECOVERING` | **[P]** for the deadline itself; the **refusal** it produces is modelled |
| T1–T8, T10–T13, T15–T18 | **[M]** — modelled, with the named tests in r4 §5.7 Table B |

### 2.4 Four kinds of state, kept apart

The review asked for this distinction explicitly, and the model enforces it:

| | What it is | Who can see it |
|---|---|---|
| **Writer-visible** | which barriers returned success in this process | the writer, until it exits. `PublicationOutcome.barriers` carries it and **nothing stores it** |
| **Reader-visible** | what a name resolves to and what bytes are behind it | any participant, through a descriptor. This is all the protocol may use |
| **Test-oracle** | the model's durable-state map | the tests only. A structural guard refuses the module access to it |
| **Durability guarantee** | what would survive a power loss | **nobody observes it.** It is established by a barrier, or it is not established |

**A power loss may retain unsynchronized changes.** The model discards
everything no barrier made durable, which is the *worst* case. A real power loss
may leave more, possibly everything. Nothing in r4 or here claims that Linux
guarantees the model's outcome; the barriers are specified so the worst case is
survivable. r4 §10 says this in the contract itself.

---

## 3. What is code, and what is proposed and unbuilt

### 3.1 Repaired in code — pure decision, validation and bounded models

| File | Change |
|---|---|
| `tools/phase_5_0_evidence/reservation.py` | four fields on `LifecycleHistory`, three rules on `LifecycleShape`, the seven shape rows, and the coherence checks for binding, attestation and recovery authorship |
| `tools/phase_5_0_evidence/lifecycle_storage.py` | the record schema, serializer and parser; the history-order rules and the derivation into the shared validator; `DurableRecordStore` with its publication order and re-seal; `RunLedger` and the seven participant profiles; the connected `read_and_admit`; the reworked first-use initializer with its enforcing binding refusal |
| `tools/phase_5_0_evidence/durability_model.py` | `restart_process()`, the process-only restart, beside `crash()`, the power loss |
| `tests/phase_5_0_evidence/test_r3_lifecycle.py` | **new**, 56 tests |
| `tests/phase_5_0_evidence/test_reservation.py` | the R3-3 validator section; three fixtures carry their binding |
| `tests/phase_5_0_evidence/test_r2_proposal_models.py` | the `Store` fixture uses the contract's record object; the withdrawn end-to-end claim |

**No new module was added to the package**, by preference: the prompt asked for
existing model modules to be extended and they were. So
`PERMITTED_PHASE_5_0_EVIDENCE_HARNESS`, `COVERED_SOURCES` and
`test_no_execution.py`'s tier enumerations are **unchanged**, and the structural
count is unchanged at 217.

**One guard refused a change and the change was made to fit the guard.**
`test_no_execution.py::test_no_module_opens_reads_or_writes_a_file` refuses the
attribute name `read_bytes` anywhere in the planning tier, because it cannot
tell `pathlib.Path.read_bytes` from a method that borrows the name. The store's
method is named `read_record_bytes` instead. The guard was not relaxed and no
exception was added to it; a refusal is a stop condition.

### 3.2 Proposed and **not** built

The lock adapter; the reservation-record writer; the run-ledger writer; the
re-seal's real `fsync`; `execution/host_lock.py`, `execution/lifecycle_record.py`,
`execution/run_ledger.py`, `execution/descriptors.py`,
`execution/recovery_store.py`; every path and permission in r4 §7; LAB-1's
reporting fix. `reservation.DECISIONS_DO_NOT_PERSIST` and
`ADAPTER_RESPONSIBILITIES` are unchanged and still say that an admitting
decision is not a reservation and that **enforcing anything at all** is
something nothing in this pass implements.

**The models are models.** `lifecycle_storage`'s whole filesystem is a
dictionary in `durability_model`. `MODEL_LIMITS` travels in every result. No
real syscall was invoked, no descriptor opened, no file written, no crash taken,
and **no real filesystem durability drill was run in this pass**.

---

## 4. The deltas, and every approval still pending

### 4.1 Provisioning and permissions — r4 §7, now **ten** items

| # | Change | Approved? |
|---|---|---|
| V1 | system group `freedomlab` | **no** |
| V2 | `ubuntu` in `freedomlab` | **no** |
| V3 | `systemd-tmpfiles` fragment for `/run/freedom-blades` and the lock inode | **no** |
| V4 | `/var/lib/freedom-blades/laboratory` `0750 root:freedomlab` | **no** |
| V5 | `/var/lib/freedom-blades/recovery` `0700 root:root` | **no** |
| V7 | the initial `lifecycle.json` `0640`, bound to host **and approved target** | **no** |
| **V9** | **`/var/lib/freedom-blades/laboratory/runs` `3770 root:freedomlab` — new in r4** | **no** |
| V6 | `RENAME_NOREPLACE` support under `R` | **preflight**, unperformed |
| V8 | `fsync` on an `O_RDONLY` directory descriptor as the containing-entry barrier | **preflight**, unperformed |
| **V10** | **that all seven participants really run as `ubuntu`, and whether to separate their identities — new in r4** | **preflight and a maintainer decision**, unperformed |

**The delta grew from eight to ten, for the third revision running.** Specifying
the descriptors revealed `OPEN_MODE`; specifying the storage revealed the
initial record and the directory-barrier preflight; **specifying the reading
revealed the ledger directory and the identity question.** A further
specification pass may reveal more. Stated as an expectation rather than as a
settled cost.

### 4.2 Interface, writer, identity, path and syscall deltas

| Surface | After, **if built** |
|---|---|
| New modules | six, of which `run_ledger.py` is new in r4 |
| New privileged writer | **none** |
| New writer identities | **none.** Ordinary participants write their own run entries as `ubuntu` |
| New write permission for ordinary participants | **one directory**: the run ledger. The reservation record stays root-written |
| New descriptors | **D19**, `runs_pathfd`/`runs_syncfd`; and **D17 and D19 are opened by every participant**, not only the executor, for the re-seal |
| New syscall | none beyond r3's set. The re-seal is `fsync(2)` on an `O_RDONLY` directory descriptor — a call already in it, now issued by a participant holding **no write permission** |
| `PERMITTED_EXECUTABLES` | 22 → **20** |
| `case_program.VERBS` | 16 → **20**; `BOOTSTRAP_VERBS` **2, unchanged** |
| `sudoers.EXPECTED_COMMANDS` | **unchanged** |
| `ctypes` exceptions | one → **two** |
| New capability or unit | **none** |

**Every one of these remains proposed and unapproved.**

---

## 5. Evidence, commands and limits

### 5.1 Commands run, exactly, on the final submitted tree

Interpreters verified before use. `/opt/discord-bots/venv-web/bin/python` and
`/opt/discord-bots/venv/bin/python` are both **Python 3.12.3**; `node` is
**v24.20.0**. These are the historical local fallbacks the prompt names as
exceptions for this restricted pass. **The canonical interpreter remains
`/opt/freedom-blades/runtime/venv-web/bin/python` on `oracle-test`, and it was
not used, because SSH and synchronization are forbidden here.**
`TEST_DATABASE_URL` was unset throughout; the bot and web suites ran serially.

| # | Command | Result |
|---|---|---|
| 1 | `env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_no_execution.py` | **217 passed**, zero skips |
| 2 | `… -m pytest -q -rs tests/phase_5_0_evidence/test_reservation.py tests/phase_5_0_evidence/test_r2_proposal_models.py tests/phase_5_0_evidence/test_feasibility.py tests/phase_5_0_evidence/test_r16_1_ownership_reproduction.py` | **268 passed**, zero skips |
| 3 | `… -m pytest -q -rs tests/phase_5_0_evidence/test_r3_lifecycle.py` | **56 passed**, zero skips |
| 4 | `… -m pytest -q -rs tests/phase_5_0_evidence` | **1723 passed**, zero skips |
| 5 | `env -u TEST_DATABASE_URL /opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py` | **3018 passed, 326 skipped** |
| 6 | `env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web` | **1610 passed, 1362 skipped** |
| 7 | `node --test 'foundry-module/tests/'*.test.mjs` | **171 passed, 0 failed** |
| 8 | `git diff --check` | **passed** |
| 9 | `python -m compileall -q` on the six changed Python files | **clean** |

**The independent R3 baseline was 217 structural and 1657 harness**, and no
other suite was rerun by that review. The harness figure moves 1657 → **1723**:
+56 from the new lifecycle module and +10 from the R3-3 validator section, with
none removed. **These are comparisons, not that review's results.**

**Every skip is an unverified assertion.** The 326 bot skips and the 1362 web
skips are database-marked tests that did not run, so this pass establishes **no
PostgreSQL correctness whatever**. The documented database-enabled web baseline
is **80**, not 1362. No database suite was run anywhere else to evade the
restriction.

### 5.2 Failing-before, passing-after

Both Blocking reproductions and the Important one were run against the **tree as
it stood before this pass**:

```text
R3-1  failed initialization : False not_durable
      visible record        : True
      durable record        : False
      retry                 : already_initialized
R3-3  survey(target="target-A") : 7 of 7 admitted
      survey(target="target-B") : 7 of 7 admitted
```

Both match the review's reported output exactly. After the pass, R3-1's window
still exists in the **writer** — it is a property of publication, not a bug to
delete — and is closed in the **reader**; R3-3's second line refuses 7 of 7.

**The corrections were mutation-tested**, because a test that passes against a
broken implementation proves nothing:

| Mutation | Tests that failed |
|---|---|
| the reader consults the oracle's durable map | 1 |
| the successor skips the re-seal (default policy set to r3's) | 6 |
| the parser drops its wrong-binding refusal | 2 |
| the ledger stops blocking on unsettled runs | 7 |
| the validator's `target_binding` relaxed to unconstrained | **0 at first** |

**The last row found a real gap and it is reported rather than smoothed over.**
Relaxing the shared validator's binding rule broke nothing, because the parser
refuses a wrong-target record before the validator ever sees one. R3-3 asks for
the binding through serialization, parsing **and the shared validator**, so the
validator's rule is defence in depth and needed its own regression. Seven tests
were added to `test_reservation.py` that exercise `validate_lifecycle` directly;
the same mutation now fails **7**.

### 5.3 Checks not run, and why

| Check | Why |
|---|---|
| The canonical `oracle-test` run | SSH, synchronization and remote execution are forbidden by the assignment |
| Any database-marked test | `TEST_DATABASE_URL` unset by instruction. Reported as unverified |
| **Formatter, linter, type checker** | **unconfigured and unavailable tooling, not a passed check.** No `pyproject.toml`, `setup.cfg`, `tox.ini`, `.flake8`, `mypy.ini`, `.ruff.toml` or `.pre-commit-config.yaml` exists, and none of ruff, flake8, black, mypy, pylint or isort is on `PATH` or importable in either interpreter. Re-checked in this pass and unchanged |
| **Any real filesystem durability drill** | forbidden, and not performed. Every durability result here is a model result |
| Host inspection, provisioning, SSH, synchronization, service change, credential access | forbidden and not performed |
| Generated-vector execution, `--execute`, the armed real boundary or materializer | refused by the assignment and by `is_executable=False` |
| The Codex read-only target preflight | assigned to Codex after implementation review. V6, V8 and V10 are **proposed** additions to it, not collection steps taken now |
| r4 §9.3 implementation checks **I1–I10** | each needs the built mechanism and target authorization. **None performed.** I8 and I9 are new and are the two that decide whether this correction is implementable as specified |

### 5.4 Manifest, generated artifacts and the digest

Covered source changed — `reservation.py`, `lifecycle_storage.py` and
`durability_model.py` were modified — so the manifest and the concrete plan were
regenerated through the **non-executing** CLI:

```text
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m \
  tools.phase_5_0_evidence.execution.cli --manifest-out <out>.json --render <out>.md
```

run **twice**, to separate output names. Both generations are **byte-identical
to each other**, and the installed artifacts are byte-identical to the second.
All **36** covered SHA-256 values were **independently recomputed from disk** by
a separate script reading `COVERED_SOURCES`, and all 36 match; the artifact's
entry set was checked to equal `COVERED_SOURCES` in both directions.

**The coverage list did not change.** It stays at **36**: no module was added to
the package and none removed, because the prompt's preference for extending the
existing model modules was followed.

| | Value |
|---|---|
| Previous review-input digest | `55af840fbb28f0ea8ae447e732644c5b2f81dace83f6ccd499f24ebc8864cff2` |
| **New review-input digest** | `45b3c6c0313e5cb8b48e116aea7716b47f1a2d231f12719975d63166d3458201` |
| `is_executable` | **False** |
| Unresolved conflicts | **3 (C-7)** |
| Unconfirmed target facts | **12** |

**The digest is review input only and must not be passed to `--execute`.** No
generated artifact was hand-edited, and no producer acceptance is recorded as
performed.

**Git.** `git status` was checked before work and unrelated changes were
preserved. Nothing was staged, committed, pushed, reset or rewritten.

---

## 6. Dated evidence-claim corrections

| # | Claim | Correction |
|---|---|---|
| **E6** | The R2 handback's *"the fresh-install path now reaches its successful control end to end"* | **withdrawn.** That test constructed a history and read no stored byte, which is why neither R3-1 nor R3-3 could show in it. Recorded as erratum E6 on the R2 handback |
| **E7** | The R2 handback's and r3 §5.8's *"an interrupted initialization publishes nothing"* | true after a power loss, **false after a process-only restart**: the record is visible. Recorded as E7 and as r3 erratum item 1 |
| **E8** | The R2 handback's suite figures and digest | **evidence about the pre-R3 tree only.** This handback carries its own |
| **E9–E12** | this handback's own four corrected claims, added 2026-09-11 | recorded in the banner at the top of this document after the R4 re-review: the successful trace's terminal order, the reach of the history validation, the reach of the participant accounting, and the superseded suite figures and digest |
| **r4-1…r4-4** | r4's four superseded statements — §5.5's order rules, the missing participant binding in §§5.5/5.8/5.11, §5.7's unachievable T11/T12 order, and §9.2 row 39's claim | recorded as a four-item dated erratum on r4, which is otherwise **preserved unchanged** |
| **r3-1…r3-5** | r3's five superseded statements — the `not_durable` row, the unspecified reading, the crashed-suite exemption, the unreachable `binding_mismatch`, and the shape table's missing binding and attestation | recorded as a five-item dated erratum on r3, which is otherwise **preserved unchanged** |

The disposable-server document carries a **third erratum** recording all three
corrections and r4's ten-item delta.

**Preserved and not reopened**, as the prompt requires: the R2
contradictory-state repair; the usable directory-descriptor design; the
recovery-parent barrier; the corrected post-unlink evidence; the C1 → C2 → C5
ordering; the withdrawal of the `JNL-47-RECOVERY-STATE` criterion split; the CRP
fix; the synthetic skills fixture; the sanitized crafting report; the production
alias fix. **The bot was not restarted.** LAB-1 remains **Important and
unrepaired**, and its labelled reproduction
(`test_feasibility.py::test_the_recovery_case_reproduces_lab_1`) is unchanged
and still asserts that the record **fails**. EH-R16-1 remains **Open**, the
unconditional real-execution refusal is retained, and its gated remedy is not
implemented.

---

## 7. Remaining proof obligations, risks and decisions

### 7.1 Proof obligations

| # | Obligation | Owner |
|---|---|---|
| 1 | r4 §9.3 **I1–I10**. **I8** — that a participant holding only read and search on the record's directory can really `fsync` it — is the single assumption that decides whether R3-1's correction is implementable as specified. **I9** — that each participant's completion condition is observable at all — decides whether R3-2's accounting can ever settle a run | implementation review, then the separately authorized target work |
| 2 | Every **[P]** row of r4 §9 — rows 13, T0, T9 and the deadline half of T14 | implementation |
| 3 | The twelve unconfirmed target facts, plus **V6, V8 and V10** | Codex, at the read-only preflight, after implementation review |
| 4 | EH-R16-1's actual remedy. **Nothing in this pass touches it** | implementation, after design acceptance |
| 5 | The three C-7 cases' producers | still unresolved; no facsimile resolves one |

### 7.2 Risks

* **The models could be wrong about Linux.** They implement a *reading* of
  `open(2)`, `fsync(2)`, `rename(2)`, `unlink(2)` and `flock(2)`. If the reading
  is wrong the model is confidently wrong, which is why `MODEL_LIMITS` says the
  manual page wins. Obligations I1, I2 and **I8** are the checks.
* **The re-seal rests on one design inference.** That a visible final name
  implies the bytes barrier returned success is an inference from the specified
  order, not an observation. A writer that renamed before synchronizing would
  falsify it, which is why the order is a contract obligation — but the model
  cannot detect a non-conforming writer, and nor could a reader.
* **Five completion conditions are not known to be observable.** r4 §5.11 names
  them per participant. If one is not observable on the target, that
  participant's runs never settle and the ledger becomes a permanent refusal
  rather than a control. This is the most likely place the design meets reality
  badly.
* **The delta grew again**, and specifying the next layer may grow it further.
* **Quiescence is an operational premise about people and processes**, not a
  technical guarantee, and it is still the only prevention for final-entry
  removal.
* **The file modes are an accident guard, not a barrier**, while all seven
  participants share one identity that holds passwordless `sudo`. V10 is the
  decision that would change it.

### 7.3 Decisions requested

**None of Peter by this pass.** Three await a maintainer **after Codex's
review**, one of them new:

1. r4 §7's provisioning and permission delta, **now ten items**;
2. **V10 — whether the seven participants' identities should be separated**, on
   which r4 §5.4's modes and §6.4's delta both depend; and
3. LAB-1's classification.

---

## 8. Stop point

**Next action: Codex technical re-review of the complete lifecycle.** No finding
is closed on the implementer's authority and no implementation approval is
requested before that checkpoint. Passing tests accept no risk and advance no
operational gate: Package 5.0 remains **not ready**, P5.0-R5 **Blocking**, OD-62
**Open** and EH-R16-1 **Open**. All three C-7 cases remain declared unresolved,
`is_executable` remains **False**, the operational-ineligibility and
missing-coverage controls are unchanged, and the twelve target facts remain
unconfirmed. No host action, provisioning, migration, deployment, cutover or
Package 5.1+ work is authorized by this handback.
