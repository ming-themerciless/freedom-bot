# Claude handback — I3 controlled-write verification stopped before the first write — 2026-09-19

> **Historical blocker, decided 2026-09-19.** C-P5.0-LAB-I3-D1 withdraws P2's
> `CAP_FOWNER` dependency, fixes P2 at `root:root 0555`, and narrowly permits
> the armed verifier to create and remove temporary canonical `R`/`R/bin`.
> This handback remains evidence of why the earlier pass stopped; its open
> decision statements are not current authority.

Authorization: **C-P5.0-LAB-I3**. Implementing operator: Claude. Independent
Technical and Security Reviewer: Codex. Prompt:
[`phase-5-0-reserved-laboratory-i3-controlled-write-claude-prompt.md`](phase-5-0-reserved-laboratory-i3-controlled-write-claude-prompt.md).

## 1. Result

**Stopped before the first write. Nothing was created, linked, removed or
synchronized on any host.** No SSH session was opened, and neither
`oracle-test` nor any other host was inspected. The stop depends only on
repository facts, so no host observation was necessary under the assignment's
"necessary read-only inspection" limit.

The assignment's second and third preconditions both fail, and its first
precondition fails for the one I3 dependency the assignment names:

| Precondition | Result | Section |
|---|---|---|
| 1. Exact target, identity, naming, bytes, custody, barriers and cleanup | **Ambiguous.** I3 covers four exclusive publications in four directories under two identities. The assignment names one target and does not say which one. The two-names-present verification state and the removal of the final name have no reviewed procedure. | §3 |
| 2. The procedure exercises every I3 dependency, including P2/`CAP_FOWNER` | **Absent.** P2 publishes under `R/bin`. `R` does not exist, creating it is forbidden, and the only reviewed route to P2 is `--execute`. | §4 |
| 3. Reviewed invocation without V7, a participant, the harness, a generated vector or `--execute` | **Absent.** Every production `linkat` call site is reachable only through one of those five forbidden routes. | §2 |

The prompt requires this stop: *"If any of those is absent, ambiguous, not
provisioned or not already reviewed, stop before the first write."* No source
was added, no probe was written in shell, Python or `ctypes`, I3 was not
narrowed, `R` was not created and V7 was not initialized.

## 2. No reviewed operator route reaches `linkat` (precondition 3)

The repository has one `linkat` implementation:
`PosixFilesystem.renameat(..., noreplace=True)` in
`tools/phase_5_0_evidence/execution/descriptors.py` (`os.link` at line 854,
followed immediately by `os.unlink` of the source). r6 §6.2 names four
exclusive publications. I traced each production caller of the primitive to
its entry point:

| r6 publication | Directory, identity | Production caller | Only reviewed way to reach it | Forbidden by the assignment as |
|---|---|---|---|---|
| **T1**, first-use record (§5.10) | `/var/lib/freedom-blades/laboratory` (V4), root | `lifecycle_record.LifecycleRecord.initialize` → `lifecycle_storage.initialize_first_use_record` → `DurableRecordStore.publish(exclusive=True)` (`lifecycle_storage.py:571`) | operator initialization of `lifecycle.json` | **V7 initialization** (r6 §7.1 says this *"would perform that verification under another name"*) |
| **T6**, `participant_started` (§5.11) | `/var/lib/freedom-blades/laboratory/runs` (V9), `ubuntu` | `run_ledger` → `DurableRecordStore.publish(exclusive=True)` (`lifecycle_storage.py:3272`), called from `execution/participants.py` | a participant run after admission. With V7 absent, admission refuses all seven participants (r6 §7.1, row 80) | **participant / harness invocation**, and unreachable in any case |
| **§2.3.3** capture copy and record | `/var/lib/freedom-blades/recovery/<run-id>` (V5), root | `recovery_store._publish_object` (`recovery_store.py:866`) | the executor's M1 path, armed only by `execution/cli.py --execute` | **`--execute`** |
| **P2** case-program installation (§1.4.2) | `R/bin` = `/var/lib/fb-evidence-p5-0/bin`, root | `executor.DescriptorBoundEffects.install_case_program` (`executor.py:2457`) | the executor after C1 creates `R`, armed only by `--execute` | **`--execute`** and **creating `R`** |

The repository has four operator entry points, and none of them reaches a
publication by another route:

* `execution/provisioning_cli.py`: `--apply` only. It runs V12, V4, V9 and V5
  through `mkdirat`, and it refuses V7 as `item-not-in-this-release`.
* `execution/cli.py`: the harness. Its only effecting branch is `--execute`.
* `execution/evidence_cli.py`: the harness's artifact renderer. It publishes
  nothing on a target.
* `execution/case_program.py`: the reviewed case program. The executor runs it
  inside an armed run, and it has no `linkat` verb (r6 §6.2 lists `openat`,
  `unlinkat`, `renameat` and `fstatat`).

`docs/operations/disposable-test-server.md` has no I3 procedure. Its current
banner restates the authorization and names no command. r6 §9.3's I3 row says a
controlled write is needed and specifies no procedure. The I12/V6 closure review
and the R4 operational handback both state that I3 was not exercised.

**Missing:** a reviewed, non-effecting-by-default operator entry point that
reaches the reviewed publication primitive against one named I3 directory
without passing through V7, a participant, the harness, a generated vector or
`--execute`.

## 3. The target and the sequence are not fully specified (precondition 1)

1. **Which directory, and as which identity.** I3 is *"that exclusive
   publication's `linkat` succeeds on the target's filesystems under their
   hard-link policy"* (r6 §9.3). There are four such publications (§2 table).
   They use two execution identities, root for T1, §2.3.3 and P2 and `ubuntu`
   for T6, and two different `proc_sys_fs(5)` branches: the owner condition for
   T1, T6 and §2.3.3, and `CAP_FOWNER` for P2. The assignment authorizes *"one
   uniquely named temporary object"* in *"the exact target filesystem"*. That
   is enough for one of the four, and nothing selects which. V6/I12 recorded all
   four locations on the same ext4 root mount with `fs.protected_hardlinks=1`.
   A single link would therefore show filesystem support, but it would not show
   the hard-link-policy branch for the other identity or owner condition.
2. **Names and bytes.** No reviewed contract defines an I3 test name. The
   existing temporaries are `lifecycle.json.tmp`, the run-ledger temporaries,
   `<name>.tmp` in the recovery store and `.case-program.tmp`, and each final
   name belongs to a real record. Using any of them in V4 or V9 would publish an
   object that the admission path reads (`lifecycle.json` is exactly V7). No
   reviewed "harmless test bytes" are defined.
3. **The verification state.** The prompt's step 5 needs both names present
   so that byte equality and a shared `(st_dev, st_ino)` can be observed.
   The reviewed primitive calls `unlinkat` on the temporary right after
   `linkat`, in the same call, and returns nothing. The only reviewed way to
   observe r6 §6.2's second interruption state is fault injection in the suite.
   No reviewed operator step observes it on a target.
4. **Removal of the final name.** The only reviewed guarded removal,
   `DurableRecordStore.remove_publication_temporary`, removes *exactly the
   temporary* and never the published record (r6 §6.2). r6 §6.2 marks P2's
   residue removal as **[P]**, with no test and no route. No reviewed sequence
   removes a published final name with an identity comparison and then
   synchronizes the directory. Doing that by hand would be the improvised
   cleanup the prompt forbids.

**Missing:** a reviewed I3 procedure definition covering the target directory
or directories, execution identity or identities, temporary and final names,
harmless bytes and their digest, descriptor custody, how the two-names-present
state is observed, an identity-guarded removal of both names, the directory
barrier and the residue survey.

## 4. P2/`CAP_FOWNER` cannot be exercised under this authorization (precondition 2)

r6 §7.2(6), which was kept when V11 was withdrawn, and r6 §9.3's I3 row both
make P2's dependency part of I3. P2 `fchown`s its temporary away from the
executor's filesystem UID and sets mode `0555` before `linkat`. Neither the
owner condition nor the readable-and-writable condition then holds, so the link
succeeds under `fs.protected_hardlinks=1` only if the root executor holds
`CAP_FOWNER`. V6 read capability masks only for `ubuntu`. `provisioning.py`
states that a mask read under `ubuntu` *"says nothing about a root process's
mask"*.

Exercising the dependency in its real location needs `R/bin`. `R`
(`/var/lib/fb-evidence-p5-0`) is created only by the reviewed concrete plan's
`mkroot` step (r6 §1.3.3, decision B), and P2 runs only inside an executor run.
The assignment forbids creating `R` and using `--execute`. Performing the
`fchown`/`0555`/`linkat` sequence somewhere else, as root, would be a new probe
that has not been reviewed. It would also narrow I3 by moving P2 away from its
contracted directory. The prompt forbids both.

**Missing:** either a reviewed route and authorization that exercise P2's
`fchown`/`0555`/`linkat` sequence as the reviewed root identity in its
contracted directory, or a maintainer ruling that splits I3 into a
filesystem/owner-condition part (T1, T6, §2.3.3) and a P2/`CAP_FOWNER` part,
with the second one left open.

## 5. What this pass did

Read-only and repository-local:

* read `.agents/AGENTS.md` in full; the implementation plan's reading map,
  §0, §16, §17 and the current §20 pointer; the active `Handover information`
  entries; the disposable-server runbook's current banner; runner contract r6
  §§1.3.3, 5.10, 6.2, 7, 7.1, 7.2, 7.3 and 9.3; the relevant parts of the
  I12/V6 closure review and the RAID register; and the publication
  implementation paths listed in §2;
* traced every `noreplace=True` caller and every `argparse` entry point under
  `tools/phase_5_0_evidence`; and
* inspected Git status and recorded source identity (§6).

I did not read implementation-plan §§12–14 and the change/decision registers
in full. The stop is determined by r6 and the code, and nothing in those
sections could create a reviewed operator route. I list this reading gap so the
reviewer can weigh it.

**Not performed:** SSH, synchronization, host inspection, any filesystem write
on any host, V7, a participant, the harness, database access, a generated
vector, `--execute`, V8 and V10. The repository has no source or test change.
The only change is this handback and one short entry at the top of
`docs/review/Handover information`.

## 6. Source identity

This is review input only, not execution authority. `HEAD`
`2fb1d6fd88013752d53af76fc97b4db07fc31181`, on branch `docs/platform-plan`,
with 52 uncommitted or untracked paths that were present before this pass and
are left as they were. Working-tree SHA-256 at 2026-09-19T19:10:19Z:

| File | SHA-256 |
|---|---|
| `docs/review/phase-5-0-reserved-laboratory-runner-contract-r6.md` | `70f3f259736e92bf2a5915cc5d77b0c383eac1c9e35709e7be8c9ee3a907caf3` |
| `docs/review/phase-5-0-reserved-laboratory-i3-controlled-write-claude-prompt.md` | `70c9ea58949f872e2e1786584ec892296b415a47e4ca735a6a307e16de528e6b` |
| `tools/phase_5_0_evidence/execution/descriptors.py` | `625c29b46396056724cfee8687af5b2a21d643635d569f5d9a64883b185f1c00` |
| `tools/phase_5_0_evidence/execution/executor.py` | `a5b17330fb6bfe5c1903f8feb0aaf41203d68b1b2d781099ca646ecb97af48f5` |
| `tools/phase_5_0_evidence/execution/recovery_store.py` | `e6d0c18857439a43e6614b939425fd95667feadb1a0e2eb27a5dd3dbed576142` |
| `tools/phase_5_0_evidence/lifecycle_storage.py` | `7bbfc11ae5efd1d19f9c0de173e52488a87304beef4ee1c3060b7ff71f39882a` |
| `tools/phase_5_0_evidence/execution/lifecycle_record.py` | `e8151442c938cae4a126c3423838dcaf2714bd473909cb90a32faadc7e26169e` |
| `tools/phase_5_0_evidence/execution/run_ledger.py` | `735bf449260c2e909bac0f04d102d6802643eb96c42931412fb3f2a7ed953fbc` |
| `tools/phase_5_0_evidence/execution/participants.py` | `430965c81d6fc746d46cb64b6be626c70339047c355ffd28fbb93685b082199a` |
| `tools/phase_5_0_evidence/execution/cli.py` | `485f960f1dee97feaef4a6c1f8e002c27262a427db470cd91c5dd36f057cb4d1` |
| `tools/phase_5_0_evidence/execution/evidence_cli.py` | `68d185ca55c747b976917b6d215fcae976c476cb3ff2a94b7fa85791b89d8d3c` |
| `tools/phase_5_0_evidence/execution/provisioning_cli.py` | `f65cca5f84a36d791ec912b2166ff0806be3560c5bca451cf54cf3696abf343f` |
| `tools/phase_5_0_evidence/execution/provisioner.py` | `32ff8d9a9dc0bb4205ce59b2f73f67bb1834bab994d75fbe87aa57b54b8fd0e7` |
| `tools/phase_5_0_evidence/execution/case_program.py` | `188af751d2a306b88697b152332389d00d357a3dd0ee37859c6eb352f6359de0` |
| `tools/phase_5_0_evidence/provisioning.py` | `93de013129c4654cae6ff0b7a00e0df1ce52c9df15541e022cf3b3c4746d4354` |

## 7. Required evidence items, and why each is absent

The prompt lists the evidence for an executed verification. Because no write
was made, each item stands as follows:

* **procedure and invocation**: none exists (§2, §3);
* **preconditions, identity, groups, capabilities, mount, `protected_hardlinks`**:
  not re-observed in this pass, because no host inspection was needed. The last
  observation is the I12/V6 evidence: ext4 root mount and
  `fs.protected_hardlinks=1`, with capabilities read under `ubuntu` only;
* **commands, timestamps, exit statuses, output**: none were run on a host;
* **names, byte digest, `(st_dev, st_ino)` pairs, link counts**: none, because
  nothing was created;
* **removal and directory-synchronization evidence**: none, because nothing was
  removed;
* **final absence and residue survey**: not performed on the host. This pass
  made no host effect, so it could not have left residue. The residue state is
  the one the R4/I12 evidence left, and I did not re-observe it;
* **I3 dependencies confirmed**: **none.** Filesystem hard-link support,
  the owner-condition branch for root (T1, §2.3.3) and for `ubuntu` (T6), and
  P2/`CAP_FOWNER` all remain open.

## 8. Unchanged state

I3 unconfirmed. V7 excluded and absent. V8 and V10 unperformed.
`plan.is_executable=False`. `reservation.REAL_EXECUTION_REFUSAL`
unconditional. LAB-SECRETS-1 Open, Low. LAB-V6-P2 deferred. Package 5.0 **not
ready**. Claude closes no finding, approves no digest and advances no gate.

## 9. Proposed for maintainer decision, not recorded

* **Proposed RAID item LAB-I3-1** (Issue, Operations Owner and Technical
  Lead): I3 has no reviewed operator procedure or entry point, and its P2 part
  cannot be reached without `R` and `--execute`. This is the same kind of
  blocker as LAB-V6-P1. I have not added it to the register.
* **Options, for the maintainer.** Claude recommends none of them:
  (a) authorize a bounded repository pass that specifies and implements a
  dedicated, explicitly armed I3 verification entry point over the reviewed
  `PosixFilesystem` primitives. It would name the target directory or
  directories, identities, names, bytes, the two-names-present observation, a
  guarded removal of both names and the barrier. It would then go to
  independent review before a separate operational release. (b) Additionally
  rule on whether I3 is split so that P2/`CAP_FOWNER` stays open, or on how P2
  is exercised in `R/bin` without `--execute`. (c) Accept that I3 closes only
  through a later authorized real run.

## 10. Reviewer focus

1. Whether §2 missed any reviewed route to `linkat` that avoids all five
   forbidden routes. I believe there is none.
2. Whether the §3 ambiguities are real or are resolved by a reviewed document
   I did not read in full (§5 reading gap).
3. Whether §4's reading of r6 §7.2(6), that P2/`CAP_FOWNER` is inside the
   current I3, is correct.
