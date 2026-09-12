# Handback — September 11 re-review remediation (R2)

Date: 2026-09-11. Author: Claude, working Technical Lead for C-P5.0-LAB-1.
Answering: [independent re-review `project-review-2026-09-11-r2.md`](project-review-2026-09-11-r2.md),
under [the bounded remediation prompt](project-review-remediation-2026-09-11-r2-claude-prompt.md).

**Status: returned to Codex for technical re-review. Nothing here is accepted, no
finding is closed on the implementer's authority, no digest is approved for
execution, and no privileged mechanism, provisioning, host action or preflight
was performed.**

Package 5.0 remains **not ready**, P5.0-R5 **Blocking**, OD-62 **Open**, EH-R16-1
**Open**, LAB-1 **Important and unimplemented**.

New review-input digest, **not execution approval**:
`55af840fbb28f0ea8ae447e732644c5b2f81dace83f6ccd499f24ebc8864cff2`.
It supersedes `e6d42228f5ccc4fd5eebc0861bb97eec42bbf16705d1aa209de5464e194bdba1`
because covered source changed. **Do not pass either to `--execute`.**

> **Errata E6–E8, 2026-09-11.** The
> [R3 re-review](project-review-2026-09-11-r3.md) requested changes, and the
> [R3 handback](project-review-remediation-2026-09-11-r3-handback.md) answers it.
> This document is preserved unchanged; three of its evidence claims do not hold
> and are corrected here rather than edited away.
>
> * **E6.** Its account of the first-use control said the fresh-install path
>   *"now reaches its successful control end to end"*. It did not. The test
>   named there constructed `environment_reset_history(HOST)` and handed it to
>   the decision, so no stored byte was read and neither the storage/admission
>   gap (R3-1) nor the lost target binding (R3-3) could show. **The end-to-end
>   claim is withdrawn.** The connected replacements are
>   `tests/phase_5_0_evidence/test_r3_lifecycle.py`'s two lifecycle traces.
> * **E7.** Its statement that an interrupted initialization *"publishes
>   nothing"* is true after a power loss and false after a process-only restart:
>   a failure between the rename and the directory barrier leaves the record
>   **visible**. The corrected statement is r4 §5.6.
> * **E8.** Its figures — 217 structural, 1657 harness, 3018/326 bot,
>   1610/1362 web, 171 Foundry, digest
>   `55af840fbb28f0ea8ae447e732644c5b2f81dace83f6ccd499f24ebc8864cff2` — are
>   evidence about the tree of 2026-09-11 before the R3 remediation and are
>   **not** evidence about any later tree. The R3 handback carries its own.
>
> The digest above remains **review input only** and must not be passed to
> `--execute`; it is superseded as the current review input by
> `45b3c6c0313e5cb8b48e116aea7716b47f1a2d231f12719975d63166d3458201`.

---

## 0. Disposition at a glance

| Finding | Class | Disposition | Where |
|---|---|---|---|
| **PR-20260911-R2-1** — contradictory predecessor state still admits | Blocking | **Repaired in code**, with failing-before regressions | §1; `reservation.validate_lifecycle()`; [contract r3](phase-5-0-reserved-laboratory-runner-contract-r3.md) §5.9 |
| **PR-20260911-R2-2** — the durability sequence uses invalid descriptors | Blocking | **Design corrected and modelled. Mechanism not built** | §2; r3 §1.3, §2.3, §2.4, §6.2 |
| **PR-20260911-R2-3** — the post-unlink check overclaims detection | Important | **Claim withdrawn and corrected; counterexample modelled** | §3; r3 §1.4.5, §9 row 3 |
| **PR-20260911-R2-4** — the storage protocol omits first use and ADMITTED | Important | **Design corrected and modelled. Nothing provisioned** | §4; r3 §5.6–§5.8, §7 item V7 |

**One finding is code and three are design.** That distinction is load-bearing
and §5 restates it: R2-1 was a defect in a function that exists, so it is fixed;
R2-2, -R2-3 and -R2-4 are defects in a proposal, so the proposal is corrected and
**submitted**, and bounded synthetic models were written so the corrections can
be falsified rather than only asserted.

---

## 1. PR-20260911-R2-1 — repaired

### 1.1 The defect, reproduced before anything was changed

The reviewer's reproduction, re-run locally against the unmodified tree: a
synthetic host and target, an empty complete inventory, `LockView()`, a readable
and complete history, and one matching `ReleaseRecord`, varying only
`predecessor_state`.

```text
BEFORE the repair — disposition RELEASED, varying predecessor_state:
  admitted    -> admitted=True  refusals=()
  running     -> admitted=True  refusals=()
  recovering  -> admitted=True  refusals=()
  quarantined -> admitted=True  refusals=()
  requested   -> admitted=True  refusals=()
  None        -> admitted=True  refusals=()
  released    -> admitted=True  refusals=()
```

**Two further fall-throughs the local reproduction found, beyond the review's
case**, and both are reported rather than quietly fixed:

```text
BEFORE the repair — VERIFIED_FIRST_USE carrying a release record
                    and an operator recovery reference:  admitted = True
BEFORE the repair — OPERATOR_RECOVERED over a RUNNING predecessor:  admitted = True
BEFORE the repair — a malformed disposition, the plain string 'released':
                    admitted = True   refusals = ()
```

The malformed case is the worst of the three. `PredecessorDisposition` is a
`str` enum and the branches compared with `is`, so a value carrying the right
*text* matched no branch, produced no refusal, and **admitted with an empty
refusal tuple** — a decision that admits while nobody has classified anything.

### 1.2 The repair

`tools/phase_5_0_evidence/reservation.py`. The admitting branch is no longer
chosen first.

* **`LIFECYCLE_SHAPES`** — a table stating, for each of the seven dispositions,
  the predecessor states it may be paired with and whether the predecessor
  identity, the release record and the recovery reference are **required**,
  **forbidden** or **unconstrained**, each with the reason quoted into its
  refusal. The accepted combinations are now stated in code rather than inferred
  from a chain of `elif`s, which is what let the finding through.
* **`VALIDATED_LIFECYCLE_OUTCOMES`** — the explicit allowlist. Three
  dispositions admit; everything else, including anything unrecognised, refuses.
* **`validate_lifecycle()`** — the shared decision, in four stages, the first
  three running **before any admitting branch is selected**: is the record about
  this host, readable and complete; are its values inside the closed vocabularies
  at all; does it **agree with itself**; and only then, is its disposition in the
  allowlist.
* **`LifecycleValidation`** — carries `coherent` and `admits` as two fields,
  because a coherent ACTIVE record refuses for one reason and an incoherent
  RELEASED record refuses for a different one the operator has to go and fix.
* **`admit()`** now calls `validate_lifecycle()`. Its own refusals — target,
  quarantine, lock, inventory, real execution — are unchanged.

**A release record does not override contradictory state**, and no combination is
normalized into a successful disposition: a contradiction refuses, naming which
two halves disagree.

### 1.3 After

```text
AFTER the repair — disposition RELEASED, varying predecessor_state:
  admitted -> False | running -> False | recovering -> False
  quarantined -> False | requested -> False | None -> False
  released -> True                                  ← the valid control
malformed 'released' -> False
  "the record's disposition 'released' is malformed: it is not one of [...]"
```

### 1.4 Regressions — failing before, passing after

`tests/phase_5_0_evidence/test_reservation.py`, section *PR-20260911-R2-1*.
**81 → 113 tests (+32).** Every one of them admits against the pre-repair code
and refuses after it, except the positive controls, which do the reverse.

| Group | Cases |
|---|---|
| The required table | RELEASED paired with ADMITTED, RUNNING, RECOVERING, QUARANTINED, REQUESTED, **missing state**, and the valid RELEASED control — parametrized, seven rows |
| The reviewer's exact input | RUNNING and QUARANTINED, with the reviewer's own inventory and lock |
| Retained bindings | wrong reservation, wrong host, wrong target on the release record, all still refusing |
| **Verified first use, audited** | contradictory state; a named predecessor; an attached release record; an attached recovery reference. Plus `…stays_distinguishable_from_missing_history`: the claim admits, *unclassified* refuses, *unread* refuses, and the three are different inputs |
| **Operator recovery, audited** | must name the predecessor; requires a **QUARANTINED** predecessor (five non-quarantined states parametrized); refuses an attached release record; permits only a **new** reservation while the quarantined one keeps its history |
| **Refusing branches, audited for fall-through** | each coherent refusing disposition still refuses; an ACTIVE record carrying stale release metadata refuses **twice**, once for the contradiction and once for the active predecessor |
| **Malformed values** | a malformed disposition and a malformed predecessor state both refuse as malformed rather than falling through |
| Shape/allowlist integrity | every disposition has a stated shape; `shape.admits` agrees with the allowlist; `validate_lifecycle()` and `admit()` agree on four representative histories |

### 1.5 What the repair is not

**Decision validation, not an operationally enforced reservation.**
`DECISIONS_DO_NOT_PERSIST` still says an admitting decision is not a reservation;
`ADAPTER_RESPONSIBILITIES` still names the lock, the durable record and its
ordering, the inventory, the real release observations and *any enforcement at
all* as things nothing in this pass implements. No reader, no storage
implementation and no host effect was added to validate the inputs: every
observation still arrives as an argument from a caller that made it.

Preserved and re-asserted: omitted-residue refusals, `GUARDED_TRANSITIONS`,
quarantine terminality, and the unconditional real-execution gate — now asserted
under **both** repaired admitting dispositions.

---

## 2. PR-20260911-R2-2 — corrected in design, modelled, not built

### 2.1 Conceded

Both halves of the finding are conceded in full.

* **The descriptors.** r2 opened the chain `O_PATH`, including `bin_fd`, defined
  `pgconf_fd` as `O_PATH`, and then required `fsync` on both.
  [open(2)](https://man7.org/linux/man-pages/man2/open.2.html) enumerates what an
  `O_PATH` descriptor may be used for and synchronizing it is not among them. The
  proposed normal installation failed at its own durability barrier, and
  restoration failed the same way **after** it had replaced a destination.
* **The omitted barrier.** r2 §2.3 synchronized the captured copy, the record and
  the `<run-id>` directory, and never synchronized the **recovery parent**.
  [fsync(2)](https://man7.org/linux/man-pages/man2/fsync.2.html) states the
  separate containing-directory requirement, so the run directory's own entry was
  not durable when the first configuration mutation was permitted, and restart
  discovery by listing the parent was not guaranteed to find the advertised
  basis.

### 2.2 The descriptor contract — r3 §1.3

Every descriptor is now specified with **open flags, owner, lifetime, permitted
uses and transfer policy**, in an eighteen-row inventory (r3 §1.3.3). The design
choice is concrete:

**Every directory is held twice.** An `O_PATH|O_NOFOLLOW|O_DIRECTORY` *traversal*
descriptor, used only as the `dirfd` of the `*at()` calls; and an
`O_RDONLY|O_NOFOLLOW|O_DIRECTORY` *synchronizable* descriptor, used only for
`fsync`. Seven directories need the second: `R`, `R/bin`, `R/journal`,
`/etc/postgresql/16/main`, the recovery parent, the run store, and the lifecycle
directory.

**How the second descriptor is obtained without reintroducing an unchecked
pathname lookup** — the review's explicit question, answered by three properties
together:

1. it resolves **one component relative to the traversal descriptor already
   held**. There is no lookup from `/`, and the prefix is bound exactly as
   `unlink(2)` describes a prefix being bound;
2. its result is **compared, not assumed**: the new descriptor is `fstat`ed
   against the `(st_dev, st_ino)` pair the chain recorded, and a mismatch
   **refuses the publication** rather than retrying or falling back to a path; and
3. the residual interval between the `openat` and the `fstat` is **named**, and
   covered by quiescence for directories an experimental identity can reach, and
   by the administrator-only premise for `/var/lib` and `/etc/postgresql/16/main`.

**Extra permissions and arguments in the interface delta** (r3 §6.2, §6.4): no
new privilege, and two concrete additions — a new `OPEN_MODE` argument kind on
the case program's descriptor verbs, drawn from a closed set of four flag
combinations, and `fsync(2)` newly reached on `O_RDONLY` directory descriptors
and `O_WRONLY` file descriptors. **No synchronizable descriptor is ever
transferred to a step**, which is a narrowing r2 did not state: a step that cannot
`fsync` cannot make a durability claim the executor did not make.

### 2.3 The complete durability dependency graph — r3 §2.3

Stated for installation, capture, recovery-record publication, configuration
replacement and lifecycle publication, each barrier with its subject, its
descriptor, its order and its failure disposition. The capture publication's five
barriers, in order:

| Order | Barrier | Subject | Descriptor |
|---|---|---|---|
| 1 | **`recovery-parent-entry`** | the recovery parent | `O_RDONLY` — **the barrier r2 omitted** |
| 2 | `copy-data` | the captured copy | `O_WRONLY` |
| 3 | `copy-entry` | `<run-id>` | `O_RDONLY` |
| 4 | `record-data` | the recovery record | `O_WRONLY` |
| 5 | `record-entry` | `<run-id>` | `O_RDONLY` |

Barrier 1 is placed immediately after the run directory's exclusive creation —
the earliest safe point — so a crash mid-capture still leaves a *discoverable*
run directory rather than nothing.

**The governing rule, restated in the contract:** no first configuration mutation
may occur until both the recoverable bytes **and all the metadata needed to
discover and verify them after a crash** are durably published. r3 §2.3.1 also
names what is **not** a barrier: a read-back, a digest comparison, a successful
`rename` and a successful `write`. A sequence performing any of those in place of
a barrier has performed no barrier.

**Restoration** (r3 §2.4) has two barriers, all temporaries written and
synchronized before any rename, the renames in a fixed recorded order, and the
directory barrier after the last one. `RestorationOutcome` carries `renamed` and
`durable` as **two separate fields**, so a restoration is never reported durable
from a rename alone, and L2's reload verification takes `durable` as its
prerequisite.

Preserved unchanged: held-buffer verification/write binding, destination custody,
ordered multi-file restoration, the reload checks, quarantine, and independent
recovery when `R` or executor memory is lost.

### 2.4 The bounded synthetic model

`tools/phase_5_0_evidence/durability_model.py` — planning tier, in-memory, no
process, no file, no socket.

* **distinct volatile and durable state.** Two namespaces and two data maps. A
  directory entry becomes durable when its **containing directory** is
  synchronized; a file's bytes when **that file** is. `crash()` discards the
  volatile half and drops every object no durable entry reaches;
* **explicit descriptor modes.** `DescriptorMode` on every descriptor, and
  `fsync` on an `O_PATH` descriptor **refuses with `EBADF`**;
* **injection at every barrier**, plus the two pre-barrier stages; and
* **`BarrierPolicy.R2_OMITTED_PARENT`**, which reproduces r2's sequence so the
  corrected property can be shown to fail against it.

**Modelled results** — `tests/phase_5_0_evidence/test_r2_proposal_models.py`:

| Property | Result |
|---|---|
| Pre-mutation failure at each of the five barriers prevents M1 | **holds**, parametrized; the configuration is asserted unchanged in every case |
| Failure before any barrier (run-directory creation, capture read) prevents M1 | **holds** |
| A modelled crash after a successful publication leaves a **discoverable, verifiable** basis | **holds**: the parent lists the run, the record and copy are present, the copy digests to the record |
| **The r2 sequence fails that property** | **fails, as required.** Publication refuses; after the crash the recovery parent's listing does not contain the run, though its contents had been synchronized |
| Positive sequence | **holds**: every barrier crossed, mutation permitted |
| **Invalid-O_PATH-operation control** | **refuses**, `EBADF`, naming the operation `open(2)` does not permit |
| A synchronizable descriptor opened over a substituted name | **refuses** before any barrier |
| Rename without its directory barrier | `renamed` true, `durable` **false**; a modelled crash returns the destination to the mutated bytes |
| Multi-file restoration interrupted between renames | mixed configuration; reload verification not claimed |
| A record naming another destination | the digest matches and the destination does not; restores nowhere |

**These are proposal-model tests, not Linux runtime proof.** r3 §9.3 states
separately the seven implementation checks that would establish the real
properties — actual descriptor modes, filesystem support for the directory
barrier and `RENAME_NOREPLACE`, real crash recovery, real restoration
interruption, the inherited descriptor table and `execveat` under the disposable
identities. **None has been performed, and no real filesystem durability drill
was run in this pass.**

**Primary documentation.** `open(2)` and `fsync(2)` were read for the descriptor
and containing-directory semantics, and `unlink(2)` for §3. Every claim in r3
carries one of four labels — `[D]` documented, `[P]` proposed, `[M]` modelled,
`[A]` assumed — and r3 §0 says what each may be checked against. The `[M]` label
is new in r3 precisely so a model result is never read as a documented semantic.

---

## 3. PR-20260911-R2-3 — the claim is withdrawn

### 3.1 What r2 claimed, and what is true

r2 §1.4.5 step 3 and §9 row 3 promised that the post-check would detect a
substituted removal and report both identities. **It does neither.** The
post-check observes whether a **name** resolves;
[unlink(2)](https://man7.org/linux/man-pages/man2/unlink.2.html) removes a name,
resolving its final component at the time of the call, and after the object is
gone the name is all that remains to look at.

r3 §1.4.5 now states the four steps with prevention and evidence kept apart:
quiescence is the **prevention** and is a prerequisite; the **pre-check** is the
one genuine detection; the removal resolves the final component then; and the
**post-check is an absence check and nothing more**. A post-check that finds the
name still resolving is informative and reaches S-B. A post-check returning
`ENOENT` is **not evidence that the intended object was removed**.

### 3.2 The counterexample, modelled

`durability_model` tracks A, B and the namespace separately.

| Assertion | Held by |
|---|---|
| **A survives**, under the name it was renamed to | the test oracle, reading the namespace |
| **B is removed** | the test oracle, comparing the object it installed against the namespace |
| The post-check is **indistinguishable** from a successful intended unlink | `RemovalObservation.indistinguishable_from`, comparing only the fields a production observer has |

`RemovalObservation` has **no field for the removed object's identity**, so a test
cannot accidentally borrow what the oracle knows. `Substitution.installed`
records B for the oracle and is never read by the observation.

Also modelled: a substitution **before** the pre-check is genuinely detected and
the removal is refused; the intended removal succeeds under the declared
exclusion premise; and unobserved, false or incomplete quiescence **refuses the
effect and its dependent work, reports residue by absolute path, reaches S-B and
preserves independent recovery**.

### 3.3 What was not done

* **No new isolation architecture** was invented to repair the evidence claim.
* **The trusted-administrator premise is retained**, as an operational exclusion
  over people, and r3 does not claim that discretionary access control
  constrains root.
* The injected substitution is labelled a **detection limit**. It is not a
  passing safety invariant and is not a claim that the violation occurs under
  valid premises.
* All repeated claims were corrected: r3 §1.4.5, §1.5 row L3, §1.7 (which now has
  two rows, one for detected-by-pre-check and one for the undetectable case) and
  §9 rows 3 and 3b. A dated erratum E4 was appended to the prior handback.

---

## 4. PR-20260911-R2-4 — corrected in design, modelled, nothing provisioned

### 4.1 One allowlist, seven participants — r3 §5.6

There is no participant-specific denylist any more. All seven apply
`reservation.validate_lifecycle()` — **the same function `admit()` calls** — and
proceed only on a validated outcome in `VALIDATED_LIFECYCLE_OUTCOMES`. The
allowlist is shared by **identity**, not by copying:
`test_the_allowlist_is_the_reservation_modules_own_and_not_a_copy` asserts `is`,
so a second list cannot appear without failing a test.

* **ADMITTED is active and refuses reuse even if the process lock is free.** The
  durable record reaches ADMITTED before the first effect of any kind, so a crash
  between ADMITTED and RUNNING leaves a reserved host, a kernel-released lock and
  no release record.
* **Unknown, malformed, incomplete and contradictory history also refuses**, for
  every participant, under the same validation.
* The persistent lock inode and the durable history stay separate objects, and
  **no expiry and no free lock authorizes reuse**.

**Modelled:** a table-driven check over **thirteen histories × seven
participants**, asserting that they *agree* — there is no state on which the
executor refuses and a test suite proceeds, or the reverse. Plus the free-lock
ADMITTED case, a held lock, an unreadable lock, and the environment reset
refusing **especially** while a quarantine record exists.

### 4.2 Verified first use as a provisioning operation — r3 §5.8

Specified with creator (the operator, as root, out of band — not the harness, not
a participant, not a side effect of a run), authority (the maintainer's approval
of §7, **which is not given**), exact host/target binding, path, ownership and
modes, exclusive-creation/no-overwrite rule, file and parent durability barriers,
and what evidence supports first use (a named operator attestation with its
basis; the claim is positive and its absence is not the claim).

Six typed refusals with their recoveries, the important one being
**`prior_use_not_excluded`**: *missing history on a previously used host must
never be reinitialized as first use*. Also `already_initialized`,
`interrupted_initialization` (the temporary is reported by absolute path and
**not cleaned**, on the §2.13.2b precedent), `no_first_use_evidence`,
`binding_mismatch` and `not_durable`.

**Modelled** in `tools/phase_5_0_evidence/lifecycle_storage.py`: fresh
provisioned first use initializing durably and surviving a modelled crash; the
initialized record then admitting **every** participant, which is the fresh-install
path reaching its successful control end to end for the first time; an existing
record never reinitialized; a previously used host refused; an incomplete
attestation refused; initialization interrupted at each of its three points
publishing nothing; a leftover temporary reported and not cleaned; and an absent
record refusing every participant until initialization.

**Nothing is provisioned.** The record is created only inside the in-memory
synthetic filesystem. `PROPOSED_PROVISIONING` states the delta and every row of it
is unapproved.

**How records stay attributable and history survives an update** (r3 §5.4): every
entry names the reservation, host, target, author and time; a state change is a
**new appended entry**, so the history is the file and the current state is its
last coherent entry; operator recovery is an appended entry and the quarantined
reservation keeps its own.

### 4.3 The revised permission and provisioning delta — r3 §6.4, §7

**The delta grew, and r2's statement of it is superseded.**

| | r2 | r3 |
|---|---|---|
| System group, group membership, tmpfiles fragment | 1, 1, 1 | unchanged |
| Provisioned paths | 4 | 4 |
| **Provisioned objects** | 0 | **1** — the initial `lifecycle.json`, item **V7** |
| Case-program argument kinds | `DIRFD`, `COMPONENT` | **plus `OPEN_MODE`**, a closed set of four flag combinations |
| Descriptors opened per run | the chain, one mode | **the chain in two modes**; seven directories held twice |
| `ctypes` exceptions | 1 → 2 | unchanged |
| Executables removed from the allowlist | `/usr/bin/install`, `/usr/bin/chattr` | unchanged |
| New privileged writer, capability, unit, sudoers rule | none | none |
| Preflight facts | V6 (`RENAME_NOREPLACE`) | **plus V8** — that `fsync` on an `O_RDONLY` directory descriptor is the containing-entry barrier on the target's filesystem |

**Unchanged executable names do not establish a zero permission delta**, and r3
says so in the same place r2 did: revision 1 inferred exactly that, r2 then
inferred that specifying the syscalls had found the whole delta, and it had not —
because §5.8's initial record had not been specified either. **All eight items
remain unapproved** pending the established review and maintainer sequence.

---

## 5. Implemented versus proposed — the line, stated plainly

**Implemented in this pass, and it is pure decision code over injected
observations:**

* `reservation.validate_lifecycle()`, `LIFECYCLE_SHAPES`, `LifecycleShape`,
  `LifecycleValidation`, `EvidenceRule`, `VALIDATED_LIFECYCLE_OUTCOMES`, and
  `admit()` calling the shared validator.

**Written in this pass as bounded synthetic models of an unbuilt proposal:**

* `durability_model.py` and `lifecycle_storage.py`, both planning tier, both
  carrying `MODEL_LIMITS` in every result.

**Proposed and NOT built. None of it exists, and this pass created none of it:**

* the privileged mechanism; the filesystem writer; the lock adapter; the
  lifecycle-record writer; the recovery store; the descriptor chain; any
  operational integration;
* every provisioning item V1–V5, **V7** and V8, and preflight item V6; and
* LAB-1's repair, which stays proposed in r3 §8.

Design acceptance and the required maintainer permission decisions remain
prerequisites of that implementation.

---

## 6. Preserved corrections and open controls

| Item | State |
|---|---|
| C1 cleanup → C2 → C5 publication ordering | **preserved** with its negative controls; positively recommended by the re-review and not reopened. `feasibility.py` untouched in this pass |
| Withdrawal of the `JNL-47-RECOVERY-STATE` criterion split | **preserved and not reopened.** No criterion decision is requested |
| A second product coordinator | **not built**, and nothing here approaches one |
| **LAB-1** | Important and **unimplemented**. `test_feasibility.py::test_the_recovery_case_reproduces_lab_1` is unchanged, still a labelled defect reproduction, still asserting the record **fails** on the recovery clause. The gated cleanup mechanism was not repaired and the reproduction was not weakened |
| Separate residue and configuration recovery procedures | **retained** as proposals, r3 §8.1 and §8.2 |
| The three C-7 cases | **declared unresolved**, all three |
| Producer-review claims | unchanged; `producer_artifact_reviewed=False` for each |
| `is_executable` | **False** |
| Operational-ineligibility control | unchanged, unconditionally `False` |
| Missing-coverage controls | unchanged, empty external coverage column for all three C-7 cases |
| The twelve target facts | **unconfirmed**, none populated; each refuses the executor before any command starts |
| EH-R16-1 | **Open**; `REAL_EXECUTION_REFUSAL` unconditional and re-asserted under both repaired admitting dispositions |
| The digest | review input only; never passed to `--execute` |
| The CRP fix, the synthetic skills fixture, the sanitized crafting report, the production alias fix | **preserved untouched.** The bot was not restarted |

---

## 7. Files changed

| File | Change |
|---|---|
| `tools/phase_5_0_evidence/reservation.py` | `EvidenceRule`, `LifecycleShape`, `LIFECYCLE_SHAPES`, `LifecycleValidation`, `VALIDATED_LIFECYCLE_OUTCOMES`, `validate_lifecycle()`; `admit()` rewired; `_lifecycle_refusals()` replaced |
| `tools/phase_5_0_evidence/durability_model.py` | **new**, planning tier. The synthetic filesystem with separate volatile/durable state, descriptor modes, the publication and restoration barrier graphs, and the removal model |
| `tools/phase_5_0_evidence/lifecycle_storage.py` | **new**, planning tier. Seven participants under one allowlist, and the proposed first-use initialization |
| `tools/phase_5_0_evidence/review_manifest.py` | `COVERED_SOURCES` 34 → **36**; the two new modules added |
| `tests/phase_5_0_evidence/test_reservation.py` | 81 → **113** tests |
| `tests/phase_5_0_evidence/test_r2_proposal_models.py` | **new**, **67** tests |
| `tests/phase_5_0_evidence/test_no_execution.py` | the two new modules declared in `PLANNING_TIER_NAMES`; 205 → **217** tests |
| `tests/web/test_p3_4_static_assets.py` | the two new modules declared in `PERMITTED_PHASE_5_0_EVIDENCE_HARNESS`. **Required**: `tools/` is a watched prefix and an undeclared file under it is a scope violation |
| `docs/review/phase-5-0-reserved-laboratory-runner-contract-r3.md` | **new**; submitted, not accepted, not implemented |
| `docs/review/phase-5-0-reserved-laboratory-runner-contract-r2.md` | dated supersession banner with a five-item erratum; **content preserved unchanged** |
| `docs/review/project-review-remediation-2026-09-11-handback.md` | dated errata E1–E5 appended; **original text preserved unchanged** |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json`, `…-concrete-plan.md` | regenerated through the non-executing CLI; **not hand-edited** |
| `docs/review/Handover information`, `docs/implementation-plan.md` §20, `docs/project-management/status.md`, `docs/operations/disposable-test-server.md` | pointer updates and dated errata |

**No migration was added. No product code, application service, repository,
adapter, web route or Discord command was touched. No configuration or deployment
change is required by this pass, and `.env.example` is unaffected.**

**Security implications.** Every change narrows what is accepted. Admission now
refuses contradictory and malformed history it previously admitted; the two new
modules are inert planning-tier models that open nothing; the two new allowlist
entries are declarations, not permissions. No new privileged surface was created;
the proposed one is in r3 and is unbuilt.

**Rollback.** Revert `reservation.py`, delete the two new modules, revert the
four test files and the two allowlist entries; the two generated artifacts then
regenerate to `e6d42228f5ccc4fd5eebc0861bb97eec42bbf16705d1aa209de5464e194bdba1`.
The documents are additive or carry dated notices and revert independently.

---

## 8. Verification

**Canonical testing remains on `oracle-test` with
`/opt/freedom-blades/runtime/venv-web/bin/python`.** The active assignment forbids
SSH and remote execution, so the interpreters below are the prompt's
restricted-pass exception. **Both were verified before use**:
`/opt/discord-bots/venv-web/bin/python` and `/opt/discord-bots/venv/bin/python`
are both **Python 3.12.3**; `node` is **v24.20.0**. `TEST_DATABASE_URL` was
explicitly unset in every Python command, and the bot suite completed before the
web suite began.

| # | Command (every Python command prefixed `env -u TEST_DATABASE_URL`) | Result |
|---|---|---|
| 1 | `…/venv-web/bin/python -m compileall -q` on the eight changed Python files | **passed** |
| 2 | `…/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_no_execution.py` | **217 passed** |
| 3 | `…/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_reservation.py tests/phase_5_0_evidence/test_feasibility.py tests/phase_5_0_evidence/test_r16_1_ownership_reproduction.py` | **191 passed** |
| 4 | `…/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_r2_proposal_models.py` | **67 passed** |
| 5 | `…/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence` | **1657 passed** |
| 6 | `…/venv/bin/python -m pytest -q -rs tests/test_*.py` | **3018 passed, 326 skipped, 1 warning** |
| 7 | `…/venv-web/bin/python -m pytest -q -rs tests/web` | **1610 passed, 1362 skipped** |
| 8 | `node --test 'foundry-module/tests/'*.test.mjs` | **171 passed, 0 failed, 0 skipped** |
| 9 | `git diff --check` | **passed** |

Command 4 is the prompt's *"each additional changed/new proposal-model regression
module"* line. Command 3 is the prompt's focused set; `test_feasibility.py` and
`test_r16_1_ownership_reproduction.py` were **not modified** and are run as
regression controls.

**Comparison with the re-review's independent baseline.** Structural 205 →
**217** (+12). Harness 1546 → **1657** (+111). The arithmetic closes exactly:
reservation 81 → 113 is +32, the new proposal-model module is +67, and
structural +12 — and 32 + 67 + 12 = 111, with no other module's count changed.
The re-review did not rerun the bot, web or Foundry suites; the figures above for
those are this pass's own, against this tree.

**An intermediate failure, reported rather than smoothed over.** The first web
run against this tree returned **2 failed**:
`test_no_unrelated_production_files_modified` and
`test_every_evidence_harness_source_in_the_tree_is_declared`, both because the
two new modules were undeclared in `PERMITTED_PHASE_5_0_EVIDENCE_HARNESS`. The
guard did exactly what it exists to do. Declaring them is the fix, and the figure
in row 7 is from the re-run after that.

**Every skip is an unverified assertion.** The 326 bot skips and the 1362 web
skips are database-marked tests that did not run. **The documented
database-enabled web baseline is 80, not 1362**, so this run establishes **no
PostgreSQL correctness whatever**. Reported as unverified, not as passed.

### 8.1 Checks not run, and why

| Check | Why |
|---|---|
| The canonical `oracle-test` run on `/opt/freedom-blades/runtime/venv-web/bin/python` | the assignment forbids SSH, synchronization and remote execution |
| Any database-marked test | `TEST_DATABASE_URL` is unset by instruction; the local host is not the disposable database host. No database suite was run elsewhere to evade the restriction |
| **Formatter, linter, type checker** | **unconfigured and unavailable tooling, not a passed check.** The repository has no `pyproject.toml`, `setup.cfg`, `tox.ini`, `.flake8`, `mypy.ini`, `.ruff.toml` or `.pre-commit-config.yaml`, and none of ruff, flake8, black, mypy, pylint or isort is on `PATH` or importable in either interpreter. This was re-checked in this pass and is unchanged |
| **Any real filesystem durability drill** | forbidden by the prompt, and not performed. Every durability result in this pass is a model result |
| Host inspection, provisioning, SSH, synchronization, service change, credential access | forbidden and not performed |
| Generated-vector execution, `--execute`, the armed real boundary or materializer | refused by the assignment and by `is_executable=False` |
| The Codex read-only target preflight | authorized, assigned to Codex after implementation review, and neither performed nor expanded here. Items V6 and V8 are **proposed** additions to it, not collection steps taken now |
| r3 §9.3 implementation checks I1–I7 | each needs the built mechanism and target authorization. **None performed** |

### 8.2 Manifest and generated artifacts

Covered source changed — `reservation.py` was modified and the two new modules
were added — so the manifest and the concrete plan were regenerated through the
**non-executing** CLI:

```
env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m \
  tools.phase_5_0_evidence.execution.cli --manifest-out <out>.json --render <out>.md
```

run **twice** to separate output names. Both generations are **byte-identical to
each other**, and the installed artifacts are byte-identical to the second
generation. All **36** covered SHA-256 values were **independently recomputed
from disk** by a separate script that reads `COVERED_SOURCES`, and all 36 match;
the artifact's entry set was checked to equal `COVERED_SOURCES` in both
directions.

**The coverage list changed, and the explanation is the two new modules.**
`COVERED_SOURCES` goes 34 → 36: `durability_model.py` and `lifecycle_storage.py`
are added, nothing is removed. They are covered because they are planning-tier
modules in the reviewed package, on the same rule every other module in it
follows — a file added to the package without a decision about whether it belongs
in the reviewed set should fail the suite rather than be swept in.

| | Value |
|---|---|
| Previous review-input digest | `e6d42228f5ccc4fd5eebc0861bb97eec42bbf16705d1aa209de5464e194bdba1` |
| **New review-input digest** | `55af840fbb28f0ea8ae447e732644c5b2f81dace83f6ccd499f24ebc8864cff2` |
| `is_executable` | **False** |
| Unresolved conflicts | **3 (C-7)** |
| Unconfirmed target facts | **12** |

**The digest is review input only and must not be passed to `--execute`.** No
generated artifact was hand-edited, and no producer acceptance is recorded as
performed.

**Git.** `git status` was checked before work and unrelated changes were
preserved. Nothing was staged, committed, pushed, reset or rewritten.

---

## 9. Remaining proof obligations, risks and decisions

### 9.1 Proof obligations

| # | Obligation | Owner |
|---|---|---|
| 1 | r3 §9.3 I1–I7 — real descriptor modes, the directory barrier on the target's filesystem, `RENAME_NOREPLACE`, real crash recovery, real restoration interruption, the inherited descriptor table, `execveat` under the disposable identities | implementation review, then the separately authorized target work |
| 2 | Every `[P]` row of r3 §9 — rows 1, 2, 5, 6, 13 — which need the mechanism | implementation |
| 3 | The twelve unconfirmed target facts, plus proposed V6 and V8 | Codex, at the read-only preflight, after implementation review |
| 4 | EH-R16-1's actual remedy. **Nothing in this pass touches it** | implementation, after design acceptance |
| 5 | The three C-7 cases' producers | still unresolved; no facsimile resolves one |

### 9.2 Risks

* **The models could be wrong about Linux.** `durability_model` implements a
  *reading* of `open(2)`, `fsync(2)` and `unlink(2)`. If the reading is wrong the
  model is confidently wrong, which is why `MODEL_LIMITS` says the manual page
  wins and the disagreement is a defect in the module. Obligation 1 is the check.
* **The delta grew between r2 and r3, and may grow again.** Specifying the
  descriptors revealed `OPEN_MODE` and the second descriptor set; specifying the
  storage revealed V7 and V8. A further specification pass may reveal more. It is
  named here rather than presented as a settled cost.
* **Quiescence is an operational premise about people and processes**, not a
  technical guarantee, and it is the only prevention for final-entry removal.

### 9.3 Decisions requested

**None of Peter, by this pass.** Two items await a maintainer **after Codex's
review**, both carried forward and one enlarged:

1. r3 §7's provisioning and permission delta, **now eight items** (V1–V5, V7, V8
   and preflight V6); and
2. LAB-1's classification.

No criterion decision is requested, and no criterion split is assumed anywhere in
the tree.

---

## 10. Next owner and checkpoint

**Owner: Codex. Action: technical re-review of this remediation.** Required
evidence, in the order the prompt sets:

1. the repaired `validate_lifecycle()` against R2-1 — whether `LIFECYCLE_SHAPES`
   states the accepted combinations correctly, whether any incoherent record can
   still reach an admitting branch, and whether the malformed-value refusal is
   complete;
2. r3 §1.3 against `open(2)` — whether the two-descriptor design is usable,
   whether the comparison genuinely binds the second open, and whether the
   transfer policy's narrowing is right;
3. r3 §2.3 and §2.4 against `fsync(2)` — whether the barrier graph is complete
   for all five publications, whether barrier 1's placement is right, and whether
   refusing the mutation is the correct failure mode;
4. r3 §1.4.5 and §9 rows 3/3b against `unlink(2)` — whether the corrected
   evidence claim is now accurate and whether quiescence is an acceptable
   prevention for an undetectable event;
5. r3 §5.6–§5.8 — whether one allowlist for seven participants is correctly
   applied, and whether §5.8's initialization is complete and safe; and
6. r3 §6.4 and §7 — whether the revised delta is accurate and whether anything
   further has been missed.

**Then Peter**, on §7's eight items and on LAB-1's classification.

Implementation review precedes the later read-only target preflight, which
precedes a separate execution decision. **Passing tests advance none of those
gates**, and this handback closes no finding on its own authority. Package 5.0
remains **not ready**, P5.0-R5 **Blocking**, OD-62 **Open**, EH-R16-1 **Open**,
and PR-20260911-R2-1 … -R2-4 remain **Open** pending review.
