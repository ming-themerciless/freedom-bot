# Claude handback — C-P5.0-LAB-V6-R1, the V6 provisioning contract

> **Historical evidence; P2 conclusion superseded 2026-09-19.** This handback's
> statement that P2 depends on `CAP_FOWNER` was replaced by
> C-P5.0-LAB-I3-D1. P2 is `root:root 0555` and relies on the filesystem-UID
> owner condition. The original text remains below as the evidence reviewed at
> the time.

Date: 2026-09-16. Authorization: **C-P5.0-LAB-V6-R1**, one bounded
repository-local remediation of the incomplete provisioning contract the
released V6 survey exposed.
Assignment: [the Claude prompt](phase-5-0-reserved-laboratory-v6-provisioning-remediation-claude-prompt.md).
Input it answers: [the D12-R1 acceptance and V6 record](project-review-2026-09-16-reserved-laboratory-d12-r1-acceptance-and-v6-preflight.md).
Contract amended: [runner contract r6](phase-5-0-reserved-laboratory-runner-contract-r6.md).

**Returned for independent Codex technical and security review. Nothing here
closes a finding, confirms a target fact, approves a digest or advances a gate.**
C-7 unresolved; EH-R16-1, LAB-R6, LAB-X1, P5.0-R5 and OD-62 **Open**;
`plan.is_executable` **False**; **I3 unconfirmed**; V6 **performed but not
closed**; V8 and V10 unperformed; Package 5.0 **not ready**.

**No target mutation occurred.** No SSH, no synchronization, no target
inspection, no `sudo`, no user or group creation, no edit under `/etc`, nothing
created under `/run`, `/var/lib` or `/opt/freedom-blades`, no
`systemd-tmpfiles`, no hard link, no controlled write verification, no
lifecycle-record initialization, no V8, no V10, no participant wiring, no
database access, no generated-vector execution, no real boundary or
materializer, and no `--execute`. Every object any test created lives under a
`tmp_path` pytest removed.

**New review-input digest:**
`326764327034549a4667528690ad13192c9597748c39b1e9c3415dd466ed63e2`, replacing
`e7b23fb428cb5eaddcff58bc36caec8030813cbfcce95b74c95bfc54863b8f5a`. **Review
input only. It was not passed to `--execute` and must not be.**

---

## 1. The trace, and the root-only-parent issue

The assignment's first requirement was to trace who opens D1, under which real,
effective and filesystem identity, and who creates each per-run `R`, then
reconcile that with the root-only parent claim, `fs.protected_hardlinks=1` and
the observed absence of `CAP_FOWNER`. The result is r6 §7.2 and
`provisioning.EVIDENCE_ROOT_TRACE`; two of its claims are asserted mechanically
rather than argued (§9.2 row 86).

**Who opens D1.** `DescriptorInventory.open_provisioned_root` is the only way a
directory the run did not create enters the inventory, and r6 §1.3.3 gives D1 to
the executor alone. The open is issued **in the executor's own process**, not
through `execution/boundary.py`, so the real, effective and filesystem identity
of that `openat` is the executor process's own.

**Which identity that is.** Every reviewed effect step is `run_as="root"` — all
**34** of them in the current concrete plan, asserted in
`test_every_reviewed_effect_step_runs_as_root` — and
`boundary.ProcessBoundary._credential_for` raises `PrivilegeUnavailable` for a
root step from a launcher that is not already effective UID **and** GID 0,
classified `root-identity-unavailable` before any process exists
(`test_boundary_identity.py::test_a_non_root_launcher_cannot_run_a_root_step_as_itself`).
An executor that is not root reaches no effect at all, so **the process holding
D1 is root whenever D1 is used for anything**. r6 §5.2 row 7's *"`ubuntu`,
escalating to root for effects"* is the escalation of the whole executor, not of
individual effects.

**Who creates each `R`.** The same process. C1 is `mkdirat(D1, "<run>", 0700)`
issued in-process by `executor.DescriptorBoundEffects`, exclusively, with
`EEXIST` as the refusal; C2 records `(st_dev, st_ino)` from the descriptor
opened on the result. **No other participant calls either** — the six ordinary
participants reach only the lock, the laboratory directory and its `runs` child
through `execution/participants.py`.

**Resolution of the root-only-parent issue.** It holds for the **directory** and
requires nothing to be widened, so no contradiction is reported there: the one
identity that must search and write it is root, and `0700 root:root` grants
exactly that. No group or other bit has a consumer, because every object under
`R` is reached by an **inherited descriptor** and r6 §1.3.3 states that a step
needing a descriptor it was not given refuses rather than opening a path.

**It does not hold for the entry, and that contradiction is reported.** V6
observed the parent `/opt/freedom-blades` as `1001:1001 0755`. The entry's
rename and unlink are governed by the **parent's** write permission, so on the
target `ubuntu` can replace `/opt/freedom-blades/evidence` whatever mode V11
sets — which withdraws r6 §1.4.1's administrator-only exposure argument. §1.4.1
now says so in place, §7.3 records it, and the applier refuses
`parent-unsafe-ownership` rather than provisioning under it. **It is not
repaired here**: `chown root:root /opt/freedom-blades` is a permission change to
an existing path that holds the repository worktree, it is outside the approved
subset, and it is Peter's decision. RAID **LAB-V6-1**.

**`fs.protected_hardlinks=1` does not bear on this item.** **No exclusive
publication happens in this directory.** D1's permitted uses are C1's `mkdirat`
and §1.4.1's by-name `fstatat`. r6 §6.2's four exclusive publications are T1
under V4, T6 under V9, §2.3.3's capture under V5 and P2 under `R/bin`. V11's
mode is decided by what `mkdirat` needs and by nothing the hard-link policy
says.

**The absent `CAP_FOWNER`, and the dependency left open.** V6's zero
inheritable, permitted, effective and ambient sets were observed **for a process
running as `ubuntu`**. That is the right observation for T6, whose linked
temporary `ubuntu` created, so `proc_sys_fs(5)`'s owner condition holds with no
capability. It is **not** an observation about a root process and none is drawn.
**P2 still depends on `CAP_FOWNER`**: it `fchown`s its temporary away from the
executor's filesystem UID and sets mode `0555` before linking, so neither the
owner condition nor the readable-and-writable condition holds. That dependency
is under `R`, it is **unresolved**, it is part of **I3**, and nothing here
closes it. The unresolved V10 assumption is used as evidence nowhere.

## 2. The new provisioning item, and the revised total

**V11 — `/opt/freedom-blades/evidence`, `root:root`, `0700`.** r6 §7's table
carries it; `provisioning.PROVISIONING_ITEMS` carries it as data.

| Field | Value |
|---|---|
| Owner, group, numeric mode | `root`, `root`, **`0o700`** |
| Creation | as root, out of band, before any participant runs (r6 §5.7 T0): `mkdirat(<parent traversal fd>, "evidence", 0o700)` **exclusively**; then `openat(<parent>, "evidence", O_RDONLY\|O_NOFOLLOW\|O_DIRECTORY)` and `fchown(fd, 0, 0)`, `fchmod(fd, 0o700)` on **that descriptor**, so the umask does not decide the mode and no pathname is resolved a second time; then `fsync` of the parent's own `O_RDONLY` descriptor |
| Persistence | V6 observed `/opt/freedom-blades` on `/dev/sda1`, ext4, mounted at `/`. It is on the root filesystem and **survives reboot**; it needs no `systemd-tmpfiles` fragment, which is the whole difference from V3. Its contents do not persist by this item: each `R` is a per-run object |
| Rationale | §1.3.3 holds it as **D1**; §1.4.1's C1 creates every `R` relative to it and its by-name `fstatat` is the only thing that can detect a replacement of `R`'s name. Without it there is no D1, no C1 and no run |
| Verification | read-only `fstatat(<parent>, "evidence", AT_SYMLINK_NOFOLLOW)`: a directory, `st_uid` 0, `st_gid` 0, `st_mode & 0o7777 == 0o700`, `st_nlink == 2` while it holds no run, no entry inside — **and the parent's own `st_uid` and write bits** |
| Rollback | non-recursive `rmdir`, only while empty, only after re-observing the `(st_dev, st_ino)` recorded at creation. Never `/opt/freedom-blades`, never a run directory, never recursive |

**The mode is derived, not chosen**, by §1 above. The zero group and other bits
are what make §1.4.1's own argument true rather than assumed, and no test
required widening them — the tests are driven with an injected account database
that resolves the declared owner to the running process's ids, so the real
`fchown` and `fchmod` run unchanged without privilege and without relaxing a
single bit.

**The revised total is eleven.** Eight defined items — V1, V2, V3, **V11**, V4,
V9, V5, V7 — and three observations, V6, V8 and V10.
`provisioning.delta_item_count()` **derives** it from the two tuples, so the
number is not a literal in six places that can stop agreeing. Every statement of
the old count was updated: r6 §7's heading, §6.4's delta paragraph and
provisioned-paths row, §10's assumption list, `provisioning.py`'s docstring and
`NOT_APPLIED`, `review_manifest.py`'s version note and
`tests/web/test_p3_4_static_assets.py`'s allowlist comment. The three surviving
occurrences of *"ten-item"* in r6 are **dated historical statements** of what
Peter accepted on 2026-09-12 and 2026-09-13; rewriting those would be rewriting
the record, so the top-of-document amendment note states the change instead.

## 3. The approved prerequisite subset, and V7's exclusion

`provisioning.RELEASED_PREREQUISITE_SUBSET` — **V1, V2, V3, V11, V4, V9, V5**,
in that order: identity before anything group-owned, parent before child. r6
§7.1 is the same table.

* **V1, V2, V3 are operator steps** and this repository performs none of them.
  Each item's `creation` field is the exact command. V2's is
  `usermod --append --groups freedomlab ubuntu`, and the `--append` is
  load-bearing: the plain `--groups` form **replaces** the supplementary set,
  and V6 observed `ubuntu` in `adm`, `cdrom`, `sudo`, `dip` and `lxd` — so the
  plain form would silently remove `sudo` from the identity the whole design
  runs as.
* **V11, V4, V9, V5 are applied by `execution/provisioner.py`**, and by nothing
  else.
* **V7 is excluded, and it is the only defined item that is** —
  `provisioning.excluded_item_ids()` returns `("V7",)`.

**V1, V2, V3, V4, V5 and V9 are preserved exactly.** No owner, group or mode
changed; the trace proved no contradiction in any of them. What each gained is
the four fields the completed contract now requires of every item — creation,
persistence, verification and rollback — which state what was already true
rather than deciding anything new.

**Why V7 is excluded.** §5.10's first use is an exclusive publication whose
`linkat` is the **first real exclusive publication on the target**, and whether
it succeeds there is **I3**. V6 observed the prerequisites and, as its own
approved contract states, does not close I3; a controlled write verification
needs separate authorization before execution. Initializing the record would
perform that verification under another name.

**The stop condition.** With the subset applied and V7 absent, the host is
provisioned and **closed**. r6 §5.9's *record absent or unreadable* refuses, and
it refuses **all seven**: `lifecycle_storage.read_and_admit` is the one
admission path, `host_lock.LaboratorySession.admit` its only caller, and
`execution/participants.py` returns before any participant's work is called.
§5.10 states that initialization is the only way out of absent and that it is
the operator's act, out of band, on a named attestation. So the absence is not a
gap the next run fills — it is the fail-closed state, and it holds until V7
receives its own release. `plan.is_executable` stays `False` and
`reservation.REAL_EXECUTION_REFUSAL` stands unconditionally. §9.2 row **80**
drives all seven over a really-provisioned model host and asserts exactly this.

## 4. The applier — preconditions, refusals, idempotency, rollback, reboot

`tools/phase_5_0_evidence/execution/provisioner.py`, execution tier, declared in
`test_no_execution.py` and in the static-asset allowlist, and covered by the
review manifest.

**Preconditions, all refusing before anything is created.**

| Precondition | Refusal | Why it is not a flag |
|---|---|---|
| The provisioner is armed | `provisioner-not-armed` | unarmed by default, so an instance assembled by mistake writes nothing |
| The item is in the release | `item-not-in-this-release` (V7) / `item-not-applied-by-this-tool` (V1–V3) | refused **by name**; no argument turns either off |
| The owner and group resolve | `identity-unknown` | through an injected lookup; the module reads no account database of its own |
| **The process already is the declared owner** | `provisioning-identity-refused` | a run started as `ubuntu` would create four directories it cannot chown and leave a half-provisioned host |
| The parent exists and is a directory | `parent-absent` / `parent-not-a-directory` | an object no reviewed item describes is not one a run may invent |
| **The parent belongs to the provisioning identity alone** | `parent-unsafe-ownership` | the `/opt/freedom-blades` finding, as a mechanical refusal |
| The parent's second lookup is the same object | `parent-replaced-between-lookups` | r6 §1.3.2's comparison, for a provisioned root |

**Refusal on an unexplained object — all six, and none repaired.**
`object-wrong-type`, `object-wrong-owner`, `object-wrong-group`,
`object-wrong-mode`, `object-wrong-link-count`, `object-unexpected-content`.
They are collected rather than short-circuited, so an operator sees the whole
disagreement; the object is left byte- and inode-identical, and the refusal
carries no path, no content and no operating-system message.

**Idempotency is a verification, not a swallowed `EEXIST`.** A second
application verifies each object completely and returns `already-provisioned`
without writing a byte — `test_a_re_run_is_idempotent_and_writes_nothing`
asserts every inode **and** every `st_ctime_ns` is unchanged. `install
--directory` succeeding on a pre-existing directory is exactly what r6 §1.4.2
replaced with an exclusive `mkdirat`, and an idempotence built on a swallowed
`EEXIST` would report success for an object nobody checked.

**Partial failure.** `apply()` returns a `ProvisioningRun` rather than raising:
what now exists, which item refused with which classification, and which were
**never attempted**. Nothing is rolled back automatically — reversing a partly
provisioned host is the operator's decision.

**Rollback boundaries.** In reverse creation order, child before parent, and
three conditions that each refuse:

* the item is one **this application created**. An object it merely verified
  belongs to whoever provisioned it and is never removed;
* the `(st_dev, st_ino)` recorded at creation is **re-observed immediately
  before** the `rmdir`. Same guard as
  `lifecycle_storage.remove_publication_temporary`, and the same honest limit,
  stated in the method's own docstring: a substitution in the window between the
  comparison and the call is detected by nothing, because `rmdir` is not
  bindable to a previously observed inode; and
* the directory is **empty**. A run directory, a ledger entry or a recovery
  basis inside one stops the reversal instead of being deleted with it.

**Reboot behaviour.** Every directory item is on the ext4 root filesystem V6
observed and **survives reboot**; none needs a `systemd-tmpfiles` fragment. V3
is the one item whose objects are on tmpfs and are re-created at every boot from
the fragment, which is why the fragment and not a `mkdir` is what provisions the
lock. Each item's `persistence` field states its own case.

## 5. The post-provision V6 re-observation

`provisioning.VERIFICATION_PROCEDURE` — eight ordered steps, each stating what
it establishes **and what it does not**. The applier's `verify()` performs the
type/owner/group/mode half over real objects and **returns findings rather than
raising**, because an operator verifying a host needs the whole picture.

The eight: the execution identity; the capability state; `fs.protected_hardlinks`;
the mount and filesystem identity; each item's exact type, owner, group and
mode; **each item's parent**; the group and its membership; and **V7's absence**.

**It creates no link, takes no lock and writes nothing.** That is asserted
structurally, not promised: `test_the_verification_writes_nothing_and_creates_no_link`
reads the module's syntax tree and checks that the read-only functions call no
mutating `os` function, that the whole module's `os` surface is exactly
`{close, fchmod, fchown, fstat, fsync, geteuid, listdir, mkdir, open, rmdir,
stat}`, and that `os.link`, `os.symlink` and `os.rename` appear nowhere.
**It therefore cannot close I3 and does not claim to.** It also does not close
V8/I2, V10 or I8, and each step says so. The procedure is added to r6 §9.3 as
implementation check **I12**, unperformed.

## 6. Tests, reversals and generated artifacts

**45 new tests**, in `tests/phase_5_0_evidence/test_v6_provisioning.py`, mapped
to r6 §9.2 rows **80–86**. The suite total moves by **49**: those 45, plus four
parametrized structural rows that pick the new module up automatically because
they are driven from `COVERED_SOURCES` and from the execution-tier file list. They cover clean creation in a disposable local
model, the idempotent re-run, every wrong-object refusal, every parent and
identity refusal, partial-failure reporting, all four rollback boundaries, the
V7/I3 stop end to end over the real admission path, and the two structural
claims of the trace. **No test touches real `/run`, `/var/lib`, `/etc`, a user
or a group**, none needs privilege, none reads the host account database, and
none creates a link.

**Nine single-point reversals, eight caught.**

| Reversal | Caught by |
|---|---|
| `RV-parent-ownership` — delete the parent uid/write-bit check | `…does_not_own_exclusively_refuses` |
| `RV-existing-verification` — accept a pre-existing object without checking it | six tests, including all four wrong-object rows |
| `RV-rollback-identity` — delete the re-observed `(st_dev, st_ino)` comparison | `…no_longer_the_one_created` |
| `RV-v7-stop` — delete the release check | `test_v7_is_refused_by_name_and_so_is_every_operator_step` |
| `RV-link-count` — delete the `st_nlink` conjunct | two tests |
| `RV-unexpected-content` — delete the content conjunct | four tests |
| `RV-armed-default` — arm by default | `test_an_unarmed_provisioner_creates_nothing` |
| `RV-provisioning-identity` — delete the euid gate | `…refuses_before_it_creates` |
| **`RV-rollback-empty`** — delete the explicit emptiness check | **nothing, and that is correct and reported.** The kernel enforces the same rule: `rmdir(2)` fails with `ENOTEMPTY` and the fallback raises the same classification, so the behaviour does not change. The check buys the refusal happening *before* the call, which is the discipline every other effect follows, and the code says so in place |

**Suites, this workstation, `TEST_DATABASE_URL` unset, serial.**

| Suite | Result |
|---|---|
| `tests/phase_5_0_evidence` | **2 288 passed, 0 failed, 0 skipped**, 2 warnings (pytest config options, pre-existing) |
| `tests/test_*.py` (bot) | 3 026 passed, 326 skipped |
| `tests/web` | 1 609 passed, **1 failed**, 1 362 skipped |
| `foundry-module/tests` | 171 passed, 0 failed |
| `.claude/hooks/test_guards.py` | **31/31** — 19 refused, 12 allowed |
| `compileall` | successful over `tools/phase_5_0_evidence` and `tests/phase_5_0_evidence` |
| `git diff --check` | clean |

**The one web failure is the same pre-existing one the D12-R1 handback reported**
— `test_the_discovery_enumerates_untracked_files_rather_than_directories` fails
on its own guard, *"no untracked directory in this tree; this test proves
nothing"*. This work created no untracked **directory**: `git status` lists
sixteen modified files and six untracked files — and of those six, three predate
this pass (the D12-R1 handback, this assignment's prompt and the V6 acceptance
record), while the three this pass added are all files.

**Every skip is unverified and none of it is PostgreSQL evidence.** The 80-skip
database run was **not performed**; this authorization permits
`TEST_DATABASE_URL` unset only. **No formatter, linter or type checker is
configured** in this repository, so none was run — a statement about the
repository, not a check skipped. **Interpreters:**
`/opt/freedom-blades/runtime/venv-web/bin/python` (3.12.3, pytest 9.1.1) for the
evidence suite; `/opt/discord-bots/venv/bin/python` and
`/opt/discord-bots/venv-web/bin/python` (3.12.3, pytest 8.4.2) for the bot and
web suites; node v24.20.0. **These are local runners on this workstation, not
canonical-environment evidence.** `.agents/AGENTS.md` names the first path **on
`oracle-test`**, and a path existing here establishes nothing about there.

**Generated artifacts.** Two covered sources changed and one was added, so the
artifacts were regenerated through the **non-executing** CLI only:

```text
python -m tools.phase_5_0_evidence.execution.cli --manifest-out <scratch>/genN/manifest.json --render <scratch>/genN/plan.md
```

No `--execute`, no `--confirm-target`, no `--reviewed-digest`.

* Three consecutive generations against the submitted tree are **byte-identical**,
  and the third was compared against the installed files byte for byte.
* `COVERED_SOURCES` is **44** paths, equal to the manifest's path set. All 44
  hashes recomputed from disk: **zero mismatches**.
* Exactly **one** `source_digests` entry added
  (`execution/provisioner.py`) and **two** changed (`provisioning.py`,
  `review_manifest.py`). The only other manifest field that moved is
  `manifest_version`, **12 → 13**, for the reason version 11 and 12 moved: the
  covered set grew.
* The installed plan differs from the previous one in **one line**, its digest.
* Dry run: `executable : False`; `unresolved conflicts : 3 (C-7)`; twelve
  unconfirmed facts listed, each refusing the executor before any command
  starts.

**The digest is review input only. Do not pass it to `--execute`.**

## 7. Files changed

| File | Change |
|---|---|
| `tools/phase_5_0_evidence/provisioning.py` | V11; four required fields on every item; `EVIDENCE_ROOT`, `EVIDENCE_ROOT_TRACE`, `PREREQUISITE_PARENTS`, `UNRECONCILED_CONTRACT_DISCREPANCIES`, `RELEASED_PREREQUISITE_SUBSET`, `APPLIED_DIRECTORY_ITEMS`, `V7_EXCLUSION`, `VERIFICATION_PROCEDURE`; `delta_item_count`, `released_items`, `excluded_item_ids`; V6's fact text, `NOT_APPLIED` and the docstring |
| `tools/phase_5_0_evidence/execution/provisioner.py` | **new** — the applier, the verification and the reversal |
| `tools/phase_5_0_evidence/review_manifest.py` | `COVERED_SOURCES` + 1; `MANIFEST_VERSION` 12 → 13 with its reason |
| `docs/review/phase-5-0-reserved-laboratory-runner-contract-r6.md` | top amendment note; §1.3.3 D1 row; §1.4.1; §6.4; §7 heading, table and new §§7.1–7.3; §9.2 rows 80–86; §9.3 I3 and new I12; §10 |
| `tests/phase_5_0_evidence/test_v6_provisioning.py` | **new** — 45 tests |
| `tests/phase_5_0_evidence/test_no_execution.py` | `provisioner` declared in the execution tier |
| `tests/phase_5_0_evidence/test_r16_remediation.py` | the manifest-version literal, with its reason |
| `tests/web/test_p3_4_static_assets.py` | the new file declared; the item count |
| `docs/operations/disposable-test-server.md` | a dated restriction banner |
| `docs/project-management/raid-register.md` | a dated entry; **LAB-V6-1, LAB-V6-2, LAB-V6-3** opened |
| `docs/review/Handover information` | a dated entry at the top |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json`, `…-concrete-plan.md` | regenerated (§6) |
| this handback | new |

**Five further files are modified in the working tree and were not touched by
this pass**: `lifecycle_storage.py`, `execution/descriptors.py`,
`execution/lifecycle_record.py`, `execution/run_ledger.py` and
`test_lab_implementation.py`. They are the **uncommitted D12-R1 remediation**,
which was still awaiting Codex's acceptance when this work began, and they are
preserved unchanged. A reviewer reading `git status` sees both passes; the table
above is this one.

No migration, no configuration change, no deployment change. `status.md`, the
decision register, implementation-plan §20 and the change log are **not edited**:
they record Peter's decisions and are the maintainer's to update on disposition.

## 8. What is raised and not resolved

Three items, each needing a maintainer ruling. None was taken here, and none is
worked around by widening anything.

1. **LAB-V6-1 — the observed parent defeats the root-only claim.**
   `/opt/freedom-blades` is `1001:1001 0755`, so `ubuntu` can rename or unlink
   the `evidence` entry whatever V11 sets. r6 §1.4.1's administrator-only
   exposure argument **does not hold on `oracle-test` as it stands**. The
   candidate fix is `chown root:root /opt/freedom-blades`, which is a permission
   change to an existing path holding the repository worktree, outside the
   approved subset. The applier refuses until it is ruled.
2. **LAB-V6-2 — `/var/lib/freedom-blades` is absent and no item defines it.**
   V4 and V5 are created beneath it and r6 §2.2 states it as `root:root 0755`.
   It is the same class of defect as V11's, one path along. A twelfth item is
   **not** defined here: the assignment authorizes one, and Peter's approval
   names V1–V5, V9 and that one, so defining and applying a twelfth under that
   approval would read the approval wider than it was given. The applier refuses
   `parent-absent` for V4 and V5.
3. **LAB-V6-3 — `R`'s location is unreconciled.** r6 §1.3.3 writes
   `R = /opt/freedom-blades/evidence/<run>`, which is what makes the evidence
   root D1 and what V6 surveyed. `approved_target.APPROVED_TARGET.root_path` is
   `/var/lib/fb-evidence-p5-0`, the concrete plan's `mkroot` creates exactly
   that, and `targets.validate_mutation_root` **would refuse** the former —
   its last component does not begin with `fb-evidence-`. Both cannot be `R`.
   Relatedly, `plan.EVIDENCE_ROLE` has **no production caller**: nothing in the
   package registers a directory under it, so D1 is specified, named and
   unbuilt. Until this is ruled, **one of the two paths is provisioned for a
   consumer that does not exist**, and a reviewer should weigh whether V11
   should be applied before it is.

Also unresolved and unchanged: **P2's `CAP_FOWNER` dependency** (§1), part of
I3; V8/I2's directory barrier; V10's identity; I8's group-read `fsync`; and
LAB-X1's `execveat` route, untouched by this pass.

## 9. Security observations

* **The change strictly narrows.** Every new code path is a refusal. The one new
  class of mutating operation is `mkdir`/`fchown`/`fchmod`/`rmdir` under an
  explicitly armed provisioner whose every path arrives as an argument.
* **No permission is widened anywhere.** V11 grants access to no existing
  object; the delta adds no capability, unit, group, identity or descriptor; and
  `plan.PERMITTED_EXECUTABLES` stays at 20 and the verb table at 20.
* **The applier cannot reach a process or a shell.** It imports `os` and
  `stat`, no `subprocess`, no `ctypes`, no network or database client, and the
  execution-tier guards assert that against its syntax tree rather than its
  docstring.
* **The account database is read in one class, still.** The provisioner defines
  a two-method `OwnershipLookup` protocol and takes it as a **required**
  constructor argument with no default, so importing or constructing one reads
  nothing; `boundary.SystemIdentityLookup` satisfies it structurally.
* **No refusal carries a path, a byte of content or an OS message**, so a
  refusal is safe in an operator-facing artifact.
* **`rmdir` is not bindable to a previously observed inode**, and the rollback
  says so rather than claiming prevention.
* **Not established here:** anything about `oracle-test`. `tmp_path` is tmpfs or
  ext4 on this workstation; that a `mkdir`, an `fchmod` and an `fsync` behave
  here says nothing about V6, V8, V10, I3 or any of the twelve facts.

## 10. Rollback of this change

Repository-only. Nothing was deployed, provisioned or applied, and no host was
touched.

1. Delete `tools/phase_5_0_evidence/execution/provisioner.py`,
   `tests/phase_5_0_evidence/test_v6_provisioning.py` and this handback.
2. Delete the top entries of `docs/review/Handover information`,
   `docs/project-management/raid-register.md` and
   `docs/operations/disposable-test-server.md`.
3. `git checkout --` the modified files to restore the committed tree. The
   previous artifacts are also copied in the session scratchpad under `before/`.
4. The digest returns to `e7b23fb4…f5a` and the manifest version to 12.

There is no data change, no migration and no recovery step: the only
operator-visible behaviour added is a set of refusals in a tool nobody has run
against a host.

## 11. Questions for Codex

1. **Should V11 be applied at all before LAB-V6-3 is ruled?** If `R` really
   lives at `/var/lib/fb-evidence-p5-0`, `/opt/freedom-blades/evidence` is a
   directory nothing opens. The item is defined because V6 surveyed it and the
   assignment named it; whether it should be *created* before the contradiction
   is resolved is a maintainer call this handback does not take.
2. **The parent precondition's subject.** It asks whether the parent belongs to
   the **provisioning process's own effective UID**, not to the uid the item's
   owner name resolves to. On the target those are the same, because a run that
   is not the declared owner refuses at a separate gate. Is that the right
   decomposition, or should both be one check?
3. **`/var/lib/freedom-blades`.** Defining it would have made the delta
   applicable end to end and would have exceeded the approval's stated scope.
   Was refusing the right call, or should a twelfth item have been proposed as
   explicitly unapproved?
4. **`expected_children` for V4 is `("runs",)` only.** A present
   `lifecycle.json` therefore refuses as unexpected content while V7 is
   excluded, which surfaces an unattributed initialization. Is that the right
   fail-closed shape, or should the record's name be tolerated once V7 has its
   own release?
5. **The uncaught reversal.** `RV-rollback-empty` is caught by no test because
   the kernel enforces the same rule. Is keeping the redundant pre-check right —
   it makes the refusal precede the call, as every other effect does — or should
   it go, so that every conjunct in the module is load-bearing?

---

**Stop point.** The next checkpoint is **independent Codex technical and
security review** of this remediation. **The implementer closes no finding,
marks no V6 or I3 fact confirmed, approves no digest and advances no gate.**
Peter's provisioning approval applies only after that review accepts the
returned contract and code, and applying it is a separate act on the host that
this pass did not take and is not authorized to take.
