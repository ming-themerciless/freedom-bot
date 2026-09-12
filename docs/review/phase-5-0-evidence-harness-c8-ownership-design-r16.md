# Conflict C-8, revised — the ownership and recovery design, submitted for Codex technical review

**Status: design only. Not implemented.** This document is the technical review
checkpoint the original C-8 assignment required and the R16 review recorded as
not performed (*"The requested prior C-8 design checkpoint was not performed
before implementation; reviewing the combined submission now does not
retroactively satisfy it."*). The mechanism described below is **not** in the
tree. No source file changed for EH-R16-1. Implementation waits on Codex's
technical acceptance of this design.

Scope: EH-R16-1 only. EH-R16-2, EH-R16-3 and EH-R16-4 are independent and are
implemented in the same submission; they are described in the handback, not here.

Superseded by this document: §3 of
`phase-5-0-evidence-harness-c6-c7-c8-handback.md`, which R16 did not accept.

---

## 1. The finding, restated in terms of what the code does

`CleanupPlan.for_mutations()` generates exactly one `REVALIDATE` step, and it
generates it immediately before the reversal that removes the disposable root.
Reversals run in reverse declaration order and the root is declared first, so
that pair is the **last** two steps of the cleanup plan. Everything before them
runs on ownership inferred once, at `B3-01`, from an exclusive `mkdir(2)` that
may have returned minutes earlier.

The consequence R16 reproduced: if the root is renamed and another directory
occupies its path before cleanup, the executor

1. runs both `RESTORE` steps, each an `install` of `<root>/before/<file>` over
   the live `pg_hba.conf` and `pg_ident.conf` — reading its bytes from the
   **replacement's** `before/` directory, and installing them as the disposable
   PostgreSQL instance's authentication configuration;
2. reloads, and runs the two post-reload observations, which then attribute a
   refusal to a restoration that restored a substituted file;
3. clears file attributes and removes 28 declared paths **inside the
   replacement**; and only then
4. reaches `CL-37`, observes the root inode differs, and skips `CL-38`'s
   `rmdir`.

Thirty cleanup commands reference the root before the only check. Skipping the
final `rmdir` protects the replacement's directory inode and nothing else.

The defect is not that the check is in the wrong place. It is that **ownership
was treated as a property established once and thereafter held**, when what the
`mkdir(2)` established is a property of an object at one instant. Every later
operation resolves the path again, and a path lookup is not an ownership proof.

---

## 2. What the revised design establishes, and what it does not

### 2.1 The claim

> No cleanup operation whose safety depends on the disposable root being the
> object this run created is performed unless an identity reading taken
> **immediately before that operation**, through the reviewed bootstrap program,
> matched the identity `mkroot` reported. An operation whose guard did not match
> is not attempted, its subject is reported as residue, and the run is S-B.

### 2.2 What it does not claim

It does not claim that a descendant of the root is the object this run created.
That is §5, stated as a residual with its trust assumption, not glossed.

It does not claim to close the interval between the guard and the operation it
guards. `rmdir(2)`, `rm(1)`, `chattr(1)` and `install(1)` take **paths**, not
descriptors, and none of the permitted executables accepts a descriptor. That
interval is §5.2, bounded and stated.

---

## 3. The mechanism

### 3.1 Ownership at creation — unchanged, and unchanged deliberately

`B3-01` runs `mkroot` through the bootstrap copy. `mkdir(2)` returns or reports
`EEXIST`; the successful call **is** the ownership, with no preliminary absence
observation and therefore no window between an observation and a creation.
`fchmod(2)` and `fstat(2)` are applied to the descriptor of the directory just
created — `os.open(path, O_RDONLY|O_DIRECTORY|O_NOFOLLOW)` on the same path,
which is one further path resolution.

**R16 requires this be accounted for**: *"Successful exclusive creation must
establish ownership of the actual object. Account for replacement between
`mkdir`, opening and recording identity."*

The revision closes it inside the program rather than around it. `_do_mkroot`
becomes:

```text
fd = os.open(parent_of(path), O_RDONLY|O_DIRECTORY|O_NOFOLLOW)   # the parent
os.mkdir(basename, mode, dir_fd=fd)                              # mkdirat(2)
child = os.open(basename, O_RDONLY|O_DIRECTORY|O_NOFOLLOW, dir_fd=fd)
os.fchmod(child, mode); facts = os.fstat(child)
```

`mkdirat(2)` and the `openat(2)` that follows resolve the final component
**relative to the same directory descriptor**, so the two calls cannot disagree
about which directory the parent is. What remains is that the created entry may
be unlinked and replaced between the `mkdirat` and the `openat`. That is
detectable and is treated as such: it is not a refusal — a directory may exist —
so it takes the `ObservationUnavailable` path, exit `66`, which satisfies no
step, grants no ownership, and makes the path **bounded residue**. This is the
existing "created and could not be identified" outcome, reached by one more
route rather than by a new one.

The parent path is not itself validated as an object; it is resolved once, and
the identity of what `mkdirat` created under it is what the run records. A
replaced *parent* therefore produces a device/inode pair that no later reading
of the reviewed root path can match, which is §4.3.

**No new verb, no new argument kind, no new arity.** `mkroot` keeps its single
`ROOT_PATH` argument, whose only admissible value is the target's own root path.
The privileged interface is not widened; the syscalls behind one existing verb
change.

### 3.2 The guard step

`CleanupStepKind.REVALIDATE` already exists and already runs
`build_bootstrap_vector(target, "statroot", target.root_path)` — a read-only
`openat`/`fstat` pair reporting `root_device` and `root_inode`, with
`O_DIRECTORY|O_NOFOLLOW` so a symbolic link or a non-directory at the final
component is a refusal rather than a redirection.

What changes is **how many are generated and where**.

### 3.3 Which cleanup steps are root-dependent

A cleanup step is *root-dependent* when the correctness of what it does depends
on the object at the reviewed root path being the object `B3-01` created. That is
a property of the step's inputs and its subject, and it is decided from the
reviewed plan, not at run time:

| Step kind | Root-dependent? | Why |
|---|---|---|
| `RESTORE` | **yes** | its source is `<root>/before/<file>`; a substituted source is installed as the live authentication configuration |
| `REVERSAL`, subject at or under the root | **yes** | `rm`, `rmdir` and `chattr` resolve a path under the root |
| `RELOAD` | **yes, transitively** | it makes a possibly-substituted restore effective |
| `VERIFY` (control and proof) | **yes, transitively** | it attributes a refusal to a restoration whose input may be substituted |
| `REVERSAL`, `userdel` / `groupdel` / `gpasswd` | no | its subject is an OS account or group; ownership comes from a Band-0 absence baseline |
| `REVERSAL`, `psql` `DROP ROLE` / `DROP DATABASE` | no | its subject is a catalog object; ownership comes from the two catalog-listing baselines |
| `REVERSAL`, `systemctl stop` | no | its subject is a transient unit |

The second group is the *"independently safe recovery work"* R16 permits to
proceed. It is not merely permitted: it is the work that stops a failed
revalidation from leaving accounts, groups and catalog objects behind as well.

### 3.4 One guard per root-dependent step

`CleanupPlan.for_mutations()` emits a `REVALIDATE` **immediately before every
root-dependent step**, and that step's `requires_revalidated` names it.

Not one guard for the phase. Two reasons, and the second is the load-bearing one:

* a single guard at the head of cleanup leaves the whole configuration phase —
  two `install`s, a reload, and two `psql` connections that each wait on a server
  — between the check and the last descendant removal; and
* a per-step guard makes the invariant **checkable rather than described**.
  `CleanupPlan.ordering_holds()` gains a fourth clause: *every root-dependent
  step is preceded immediately by the `REVALIDATE` its `requires_revalidated`
  names, and every `REVALIDATE`'s `applies_with` is the mutation set of the step
  that follows it.* A plan that violates it is a `PlanRefused` at generation
  time.

Cost: one read-only `openat`/`fstat` per root-dependent step. For the current
plan that is 2 restores + 1 reload + 2 verifications + 29 contained reversals =
**34 guards**, each a two-number reading that creates and changes nothing.

### 3.5 What a failed guard does

The executor already skips a removal whose `requires_revalidated` did not
succeed, reports `REMOVAL_NOT_REVALIDATED` and makes the subject residue. The
revision extends that to the two kinds it does not yet cover, with the fixed
categories kept separate because the situations differ:

| Guarded step | On a failed guard |
|---|---|
| `REVERSAL` under the root | not attempted; subject → `unremoved`; `REMOVAL_NOT_REVALIDATED` |
| `RESTORE` | **not attempted**; the file is not written; the declared file stays out of `restored_files`, so `ConfigurationRestoration.problems()` reports it and the state is S-B; new category `RESTORE_NOT_REVALIDATED` |
| `RELOAD`, `VERIFY` | not attempted; `reload_succeeded` and `verification_control_succeeded` stay `None`, which `problems()` already treats as unresolved risk |

`RESTORE_NOT_REVALIDATED` is a new constant and is the direct answer to *"Never
restore PostgreSQL configuration from substituted files."* The restore is not
performed at all; there is no branch in which an unverified `before/` file is
installed.

### 3.6 Recovery inputs, when ownership was not proved

This is the part §3 of the previous handback did not have, and it is a
correctness change rather than a reporting one.

`RECOVERY_PROCEDURE` step 3 currently tells an operator to *"Reinstall each
retained capture over its live file as root"*. If the root's identity was **not**
revalidated, the retained captures are inside an object this run did not create,
and that instruction would tell the operator to do exactly what §3.5 just refused
to do.

So the outcome distinguishes two retention states:

* **retained and trustworthy** — every root guard matched, and the restoration
  failed for some other reason. `RECOVERY_PROCEDURE` is reported unchanged; the
  captures are the bytes this run wrote and comparing and reinstalling them is
  sound.
* **retained and unverified** — a root guard did not match. A new
  `UNVERIFIED_RECOVERY_PROCEDURE` is reported instead. It names the retained
  paths, states that the object at the disposable root is not the object this run
  created, states that the files under it are **not** established to be this
  run's captures, and instructs the operator to establish the live
  configuration's correctness from a source outside the disposable root before
  changing anything. It prescribes no reinstall.

`CleanupOutcome` gains `ownership_revalidated: bool | None` and
`recovery_inputs_verified: bool`; `classify_cleanup()` takes the guard results
and selects the procedure. Neither field is defaulted to the safe-looking value:
`None` means no guard ran, and `None` selects the unverified procedure.

### 3.7 Uncertain creation, and the run that never reached cleanup

Unchanged from the accepted part of the previous submission, and restated because
the guards must not weaken it: a creation that is neither satisfied nor in
`ROOT_NOTHING_CREATED_STATUSES` — an internal failure, an unreadable identity, a
timeout, a launch that never reported, an interruption — puts its mutation in
`uncertain_creations`, whose subjects are residue on every path including the one
where no cleanup step applies at all. Such a run has no recorded
`created_identity`, so every guard fails closed, and every root-dependent step is
skipped. Nothing under an uncertain root is removed or restored from.

---

## 4. The replacement cases, and what each one produces

| # | Situation | What the design does |
|---|---|---|
| 4.1 | Root unlinked and replaced by another **directory** before cleanup | every guard reports a different inode (or device); no restore, no descendant removal, no root removal; all subjects residue; unverified recovery procedure; S-B |
| 4.2 | Root replaced by a **symbolic link** to another directory | `statroot`'s `O_NOFOLLOW` refuses at the final component; the guard exits non-zero; identical outcome to 4.1 |
| 4.3 | A **parent** component replaced so the root path resolves elsewhere | the guard resolves to a different object; device and/or inode differ; identical outcome to 4.1. Detected as a consequence of comparing identity rather than by inspecting the parent |
| 4.4 | Root replaced **between two guards** — some steps run, some do not | the steps before the replacement ran against the object this run created and were correct; every step after it is skipped. This is the property per-step guards buy over a single phase guard |
| 4.5 | Root replaced **between a guard and the step it guards** | **not detected.** §5.2 |
| 4.6 | Root removed entirely before cleanup | `statroot` reports `ENOENT`; guard fails; nothing is removed; subjects residue. The harness does not decide that an absent root means a completed cleanup |
| 4.7 | Creation returned and identity could not be read | exit `66`; no ownership; no `created_identity`; every guard fails closed; subject residue |
| 4.8 | Creation interrupted, timed out, or never reported | `uncertain_creations`; same as 4.7 |
| 4.9 | A **descendant** replaced | **not detected.** §5.1 |
| 4.10 | Cleanup interrupted part-way | unchanged: `_cleanup_uncertain`, declared residue from the applicable plan, next invocation refuses |

---

## 5. Residual risk, stated precisely

### 5.1 Descendant replacement

The guards establish the identity of the **root**. They establish nothing about
the 28 declared paths inside it. `rm --force -- <path>` on a file that was
unlinked and replaced deletes the replacement.

Closing this by observation would need a per-path identity reading and a
removal that takes a descriptor — `unlinkat(2)` with `AT_REMOVEDIR`, addressed
relative to a directory descriptor the harness opened and verified. That is a new
verb, a new arity and a **removal** performed by the case program rather than by
`rm(1)` and `rmdir(1)`. It moves deletion from two coreutils binaries whose
argument vectors the plan pins into the reviewed program's own code, which is a
widening of the privileged interface and a maintainer decision, not an
implementation detail. It is **not** proposed here.

What is offered instead is the trust assumption, stated so a reviewer can accept
or reject it:

> The disposable root is created `0755 root:root`, by `mkdir(2)` from a process
> whose uid and gid are 0. Creating, unlinking or replacing an entry directly
> inside it therefore requires write permission on a root-owned `0755`
> directory, which requires uid 0 or `CAP_DAC_OVERRIDE`. An actor holding either
> on the disposable host can already do everything this harness does, including
> writing the reviewed configuration files directly, and is outside the threat
> model these controls address.

This assumption is **narrower than it looks and does not extend to every
declared path**: the plan creates subdirectories under the root with other owners
and modes, and an entry inside a group-writable subdirectory can be replaced by a
member of that group. The design does not claim otherwise. The bounded statement
is: *root replacement is detected; descendant replacement is not, and the paths
for which the containing directory is not root-owned-and-not-group-writable are
the ones where the assumption above does not hold.* Enumerating that subset from
the plan's own declared modes, and reporting it in the rendered plan, is included
in the implementation so the residual is visible rather than argued.

### 5.2 The guard-to-operation interval

`rmdir(2)`, and `rm`, `chattr` and `install` as invoked here, take paths. A
replacement performed between the guard and the operation it guards is not
detectable by any design that keeps deletion in the coreutils binaries. The
interval is one process spawn, and it is not zero.

Closing it requires the same descriptor-addressed removal §5.1 declines to
propose. It is stated, not accepted silently: the design reduces the exposed
interval from *the whole run* to *one process spawn per operation*, and says so.

### 5.3 What the identity comparison rests on

Device and inode numbers identify an object on a mounted filesystem. They are
reused after an object is destroyed. A design that unlinked the root, created a
new directory that happened to receive the same inode on the same device, and
did so between the creation and a guard, would compare equal. The reviewed target
fixes the filesystem device as a target fact, and the harness performs no
unlink of the root before cleanup, so the reuse would have to be arranged by the
same actor §5.1's assumption already excludes. Stated for completeness.

---

## 6. What changes, file by file

Nothing in this list is implemented. It is here so the review has the surface.

| File | Change |
|---|---|
| `execution/case_program.py` | `_do_mkroot` uses `mkdirat`/`openat` against one parent descriptor (§3.1). No verb, arity or argument-kind change |
| `cleanup.py` | `is_root_dependent` on `CleanupStep`, derived from kind and subject; one `REVALIDATE` generated per root-dependent step; `requires_revalidated` extended to `RESTORE`, `RELOAD` and `VERIFY`; `ordering_holds()` gains the immediacy clause; `RESTORE_NOT_REVALIDATED`; `UNVERIFIED_RECOVERY_PROCEDURE`; `CleanupOutcome.ownership_revalidated` and `.recovery_inputs_verified`; `classify_cleanup()` takes the guard result |
| `execution/executor.py` | the `requires_revalidated` skip generalised beyond `REVERSAL`; restores and verifications skipped rather than run; guard results threaded into `classify_cleanup` |
| `concrete_plan.py` | the C-8 narrative, the `CL-…` ids in it, and the enumerated §5.1 subset |
| `review_manifest.py` | `MANIFEST_VERSION` 8 → 9, with the paragraph saying what a version-8 digest covered |

Every generated `REVALIDATE` is a `statroot` on the reviewed root path through
the bootstrap copy. No new executable, no new verb, no new argument kind, no new
identity, no new capability, and nothing that removes an object.

---

## 7. The regressions this design is to be accepted or rejected with

Injected boundary and injected materializer only; no host operation; every effect
fake.

1. **Replacement root containing sentinel files and substitute `before/` files.**
   The run completes; guards report `999/999`. Asserted: **no `install` was
   issued against either configuration file**, no `rm`, `rmdir` or `chattr` was
   issued against any contained path, the sentinel subjects are reported as
   residue, the recovery procedure reported is the **unverified** one, and the
   outcome is S-B. Asserted as *the absence of the commands*, from the boundary's
   own call log — not from the final state.
2. **Descendant replacement.** A contained subject replaced; asserted that the
   design does **not** claim to detect it, that the §5.1 subset the plan renders
   names that path, and that the root guards still hold. A test that asserted
   detection here would be asserting something this design does not do.
3. **Failed identity read at the guard.** `statroot` reports one key
   `unreadable`; asserted that the guard fails closed and produces case 4.1's
   outcome, not a match.
4. **Interruption during cleanup, after some guards.** Asserted: the steps after
   the interruption are not run, the outcome is S-B, and the interruption
   propagates.
5. **Uncertain creation.** Exit `66`; asserted that no guard can match, no
   root-dependent step runs, and the subject is residue rather than preserved.
6. **Successful cleanup control.** Every guard matches; asserted that both
   restores, the reload, both verifications and all 29 removals run in the
   generated order and the outcome is S-C. Without this the suite would pass with
   a cleanup that never does anything.
7. **Configuration-restoration control.** Guards match, restore succeeds, reload
   succeeds, both post-reload observations satisfied; asserted S-C and
   `retained_recovery_inputs` empty.
8. **Ordering invariant.** `ordering_holds()` refuses a hand-built plan in which
   a root-dependent step is not immediately preceded by its guard.
9. **`mkdirat` identity.** The program's own emitted key set is unchanged and
   `test_case_program.py`'s policy/contract agreement still holds.

---

## 8. What this design does not touch

The accepted C-6 experiments; R14's ownership corrections; R13's
configuration-recovery safeguards, retention rule and four-step procedure for the
*verified* case; the pre-existing-object tests; the executor's six gates; the
`is_executable` gate; and the standing prohibition on execution. `is_executable`
is `False` in this submission for the independent reason EH-R16-4 requires
(Band 7's producers are unresolved again), and this design neither depends on
that nor changes it.

Package 5.0 remains **not ready**, P5.0-R5 **Blocking**, OD-62 **Open**. No
digest in this submission is execution authority.
