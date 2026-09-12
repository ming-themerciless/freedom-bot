# C-6, C-7 and C-8 implementation handback — 2026-09-09

Submitted for **independent Codex review**. Nothing here is closed, nothing is
approved, and this grants no execution authority. Package 5.0 remains
`not ready`, `P5.0-R5` remains **Blocking** and `OD-62` remains **Open**.

Review input, never execution approval:
`79ed6ed615b3a2eeb74e5b07d51f76bac0e4b0d4451f636436cf1aec523e7324` — the R14
tree R15 accepted. The tree submitted here regenerates to

```text
765b299bf680b06bce4edd34ed236dea13dff466c39e6d457d7da190b5772acd
```

which identifies **this** tree and nothing else. It has never been passed to
`--execute` and must not be: twelve reviewed target facts are still unsupplied,
and the executor refuses on each of them before a command starts.

The R13.2 digest `8875b165…` and the R14/R15 digest `79ed6ed6…` are both
**superseded**.

---

## 0. What this submission does, and the two gates it does not touch

The maintainer approved Codex's recommendations for C-6, C-7 and C-8 on
2026-09-09, assigned implementation here and independent review to Codex. All
three are implemented. `ConcretePlan.unresolved` is now empty and
`is_executable` is `True` for the first time since R13 — and that is a statement
about the **plan**, not permission to run it. Two things are unchanged and are
stated before anything else:

* **Operational execution remains a separate gate.** No `--execute`, no real
  generated vector, no armed boundary or materializer, no target provisioning, no
  database mutation, no destructive drill, no deployment and no cutover. None of
  it was performed and none of it is authorized by this submission.
* **The read-only target preflight is authorized for the later stage only.** The
  maintainer authorized it **after Codex reviews this implementation**; that
  authorization is recorded in §7 and is not requested again. This assignment did
  not instruct Claude to perform that stage, and it was not performed:
  `oracle-test` was not contacted, inspected or synchronized.

The maintainer also assigned **step 5 to Codex**: review the final manifest and
the exact disposable-host execution plan, decide whether the execution review
gate is satisfied, and coordinate operational evidence collection and cleanup
verification. §6 and §7 are written to support that review. Nothing here
substitutes Claude's approval for it.

---

## 1. C-6 — the three immutable-flag experiments

### 1.1 What was missing, and why R14 refused to approximate it

R13's Blocking finding **EH-R13-4** was that Band 5 emitted seven `capsh`
vectors ending in the `identity` verb and attributed `JNL-49`/`JNL-50` to them.
An identity observation is a **prerequisite** for those cases; it is not their
result. §2.13.8's cases are one per capability/artifact pairing, and none of the
three operations was in the plan — so a reader counting case ids found them all
present and a reader looking for the experiments found none.

R14 declared them unresolved rather than approximating them with `FS_APPEND_FL`,
and said why: *"an `+a` experiment run under `E4`, `E5` and `E6` would produce a
passing record for a case about `+i`, which is worse than a declared gap: it
would be evidence for a claim nobody made."* That remains the right refusal, and
it is why the extension below is to the **flag** and to nothing else.

### 1.2 The extension, stated as what it widens

Two verbs join the closed table in `execution/case_program.py`:

| Verb | Arity | Argument kind | What it does |
|---|---|---|---|
| `getimmutable` | 1 | `target_path` | `FS_IOC_GETFLAGS`, reporting `fs_immutable_fl` |
| `clearimmutable` | 1 | `target_path` | `FS_IOC_SETFLAGS` writing `flags & ~FS_IMMUTABLE_FL`, then reading the bit back |

**What is not widened.** There is no general `ioctl`, no mask and no arbitrary
path. `FS_APPEND_FL` and `FS_IMMUTABLE_FL` are two separate constants named in
two separate function bodies; the two ioctl request numbers are unchanged; no
argument kind carries a flag, a mask or a request number; and each clearing verb
contains exactly one `~` and only `&` operations, so no verb can **set** a bit.
`test_r16_c6_c7_c8.py::test_each_flag_verb_touches_exactly_one_bit_and_names_it_itself`
asserts all of that against the program's syntax tree, because no test in this
suite can perform the operation: clearing `FS_IMMUTABLE_FL` needs
`CAP_LINUX_IMMUTABLE` **and** the owner authorization, and nothing here runs as
root.

The new key `fs_immutable_fl` is separate from `fs_append_fl` in
`capture._KEY_VALUE_KEYS`, so an append-only observation can never satisfy an
immutable-flag expectation. That is the substitution R14 refused, made
structurally impossible rather than avoided by convention.

### 1.3 The generated steps

Eleven steps, `B5-C6-01 … B5-C6-11`, in Band 5 after the seven identity
observations. `_validate_capability_experiment_ordering` refuses a generated plan
in which an operation runs under a constructed identity before that identity was
observed — §2.13.5c's assertion contract, made checkable.

| Step | Identity | Operation | Role | Satisfied by |
|---|---|---|---|---|
| `B5-C6-01` | `E7` | `getimmutable` on the archived journal | control | exit 0, `fs_immutable_fl=1` |
| `B5-C6-02` | **`E4`** | `clearimmutable` on the archived journal | dependent | exit 10 — **`EPERM`** |
| `B5-C6-03` | `E7` | `getimmutable` on the same inode | control | exit 0, `fs_immutable_fl=1` |
| `B5-C6-04` | **`E6`** | `clearimmutable` on the same inode | control | exit 0, `fs_immutable_fl=0` |
| `B5-C6-05` | `E7` | `getimmutable` on the archived seal | control | exit 0, `fs_immutable_fl=1` |
| `B5-C6-06` | **`E5`** | `clearimmutable` on the archived seal | control | exit 0, `fs_immutable_fl=0` |
| `B5-C6-07` | **`E5`** | `open wronly` on the same file | dependent | exit 11 — **`EACCES`** |
| `B5-C6-08/09` | `E7` | `chattr +i` on both files | — | exit 0 |
| `B5-C6-10/11` | `E7` | `getimmutable` read-back | control | exit 0, `fs_immutable_fl=1` |

**The expected outcomes are §2.13.5c's, not the run's.** `E4` holds
`CAP_DAC_OVERRIDE`, `CAP_DAC_READ_SEARCH` and `CAP_LINUX_IMMUTABLE` and holds
neither **A10** nor **A11**, so it reaches and opens the inode and the ioctl's
**owner check** refuses it — and the owner check is evaluated *before*
`CAP_LINUX_IMMUTABLE` is consulted, which is why the errno is `EPERM` and not
`EACCES`. `E5` holds **A1 + A11** and a `freedomcoord` membership, so its clear
succeeds and its subsequent write open is refused by the discretionary check with
`EACCES`. Each step names **one** errno; a step admitting both would be satisfied
whichever kernel path had been taken. Five injected mismatches — including `E4`
returning, `E4` refused with the wrong errno, `E6` clearing nothing, `E5`'s
denial arriving as `EPERM`, and an initial state that was not what the case is
about — are asserted to stop the run rather than to move an expectation.

### 1.4 Semantic prerequisites, initial state and ordering

* **Each experiment establishes its own initial state, separately, immediately
  before it.** `B5-C6-01` for `E4`, `B5-C6-03` for `E6`, `B5-C6-05` for `E5`,
  each requiring `fs_immutable_fl=1` on **its own** subject.
* **`E5`'s subject is a different archive file** from `E4`'s and `E6`'s, so
  `E6`'s successful clear cannot make `E5`'s case meaningless — and the reading
  proves it rather than the ordering implying it.
* **`E6` is ordered second, and that is forced by control form C-I.** §2.13.5c
  requires the isolating control to hold *"same uid, gid, supplementary list,
  securebits, case binary, path, inode and mount"* and vary one capability.
  Holding the **inode** fixed is possible in exactly one order: `E4`'s attempt is
  expected to be refused, so it leaves the flag set and `E6` can then perform the
  identical call on the identical inode. Running the control first would clear
  the flag `E4`'s case is about. `B5-C6-03` is what makes that sound — it reads
  the flag back **as root** after `E4`'s refusal and requires it still to be set,
  so `E6` returning cannot be consistent with `E4` having quietly succeeded. The
  two vectors are asserted to differ in `cap_fowner` in `--drop`'s complement, in
  `--inh`, in one `--addamb`, and in nothing else.
* **`JNL-50`'s two halves are separately ordered steps.** A single vector
  performing both would report one exit status and nobody could say which
  operation it belonged to. The clear is a `CONTROL`; the denial is `DEPENDENT`.
  Because `inode_permission()` refuses `MAY_WRITE` on an immutable inode with
  `EPERM` *before* it evaluates DAC, an observed `EACCES` has already proved the
  flag was gone — which is exactly why the clear must have succeeded for the
  denial to mean anything.
* **Setup, reset and cleanup are in the plan.** `B5-C6-08/09` set `+i` back on
  both files and `B5-C6-10/11` read it back, so the hierarchy the rest of the
  plan documents is the hierarchy it runs against. Both reset steps declare the
  same `file_attribute` mutations Band 3 declared — one mutation, one reversal,
  performed twice — and cleanup clears both flags before removing either file
  whether or not this band was reached.
* **Failure path.** Every step is satisfied by exactly the statuses its case
  states, so the first unsatisfied step stops the run, its role says what that
  invalidates, and the full derived cleanup runs. A refused clear leaves the flag
  set; a clear that unexpectedly succeeded leaves it cleared; cleanup reverses
  either.

**Preserved unchanged:** every append-only experiment, `JNL-52`'s access matrix,
the seven identity contracts, `P-01 … P-06`, and every bounded observation.

---

## 2. C-7 — evidence connected to classification, with no execution capability

### 2.1 The shape of the resolution

R14's account was right about the harness and wrong about the shape. Band 7's
cases are not vectors this plan failed to express: they are observations of the
coordinator tooling §2.12.5a and §2.13.5a describe, running in situations an
operator arranges — `init-generation` with its provenance record removed, a probe
with a failure injected at one stage, a cleanup that did not complete. **No
argument vector this harness could write produces one.**

So they are declared as `concrete_plan.ExternalCase`: a required case with a
**named producer** and a **named collection procedure**, in a third column
`required_cases.check_case_coverage` now enforces. A case is produced by a step,
declared unresolved, or externally produced — in exactly one of the three, and a
plan violating that is a `PlanRefused`.

### 2.2 The importer — `tools/phase_5_0_evidence/observations.py`

A **planning-tier** module. It starts no process, opens no file, and imports
nothing from `execution/` at all.

* **Strict, versioned and bounded.** One envelope
  (`freedom-blades/phase-5.0/supplied-observation`, version 1), at most 64
  records, at most 256 KiB. An unknown key and a missing key are both refusals.
* **No free text anywhere.** A record names a `case_id` and a `variant` from the
  closed table, and carries exactly that variant's declared fields, each matched
  against the closed shape its field can have (`yes_no`, `count`,
  `refusal_code`, `cleanup_state`, `exit_code`). `collected_by` is a **role** in
  a narrow character class, never a person; `collected_at` is a date.
* **Bound to its target, run, manifest, case, identity and control.** The target
  identity, the run identifier and the review-manifest digest come from the
  **caller**, which reads them from the plan and recomputes the digest from the
  live tree; a record that disagrees is refused. A record can therefore only ever
  fail to match a value it did not choose.
* **What a record structurally cannot do.** Select a command, an executable, an
  interpreter or an argument vector; select a process identity, uid, gid or
  capability set; select a target path, database, role or unit; supply an
  approval token or a reviewed digest; supply a reviewed expected value; or
  construct anything that can start a process. Every expectation the classifiers
  compare against comes from their own constants.
* **Refusals implemented and tested:** malformed (seven payload shapes), unknown
  case, unknown variant, unknown custody, unknown or missing key, a value that is
  not its field's shape, duplicate `case#variant`, mismatched target / run /
  digest, and four **contradictory** records whose own fields cannot describe one
  situation.

### 2.3 Custody, because target, run and digest authenticate nothing

A record carrying the right target, run and digest has demonstrated that whoever
wrote it read the plan. It has not demonstrated where the observation came from.
Every record therefore declares its custody from a closed vocabulary:

| Custody | What it asserts | Operationally acceptable? |
|---|---|---|
| `synthetic_fixture` | written to exercise the classifier | **never** |
| `operator_attested` | a named role ran the procedure and reports the result | **no** — an attestation is a claim this harness cannot check |
| `reviewer_verified` | the independent reviewer verified it against the producer's own output | **yes**, and only then |

`EvidenceResult.eligible_for_operational_acceptance` is true only when the result
is complete, nothing is synthetic, and every record is `reviewer_verified`. It is
a **report and not an approval**, and the CLI prints it as one.

**Synthetic fixtures stay visibly synthetic.** A synthetic payload must be bound
to the synthetic target identity and an operational one to a real target — the
mismatch is refused in both directions — every classified record carries its
custody, collector and date in `detail`, and a synthetic record's
`target_identity` is stamped with the marker, so no rendering of the artifact can
take one for an observation of the approved target.

### 2.4 Connection to the existing classifiers

| Case | Classifier | Records |
|---|---|---|
| `JNL-51-PROVENANCE-OMITTED` | `provenance.classify_missing_provenance` | four: the `J-26` refusal at C0, no generation artifact, no registration row, and the probe never invoked |
| `JNL-47-NO-GENERATION-ON-FAILURE` | `journal.classify_stage_failure`, once per stage | five — Stage 1 … Stage 4 and cleanup |
| `JNL-47-RECOVERY-STATE` | `journal.classify_cleanup_failure_state`, once per variant | two — cleanup failure after a probe-stage failure, and after a fully passing probe, kept apart because they leave the host in the same place and mean different things |

`journal.py` gains those two classifiers; nothing else in the band moved.
`manifest.py`'s two classifiers are **not** wired, and the reason is stated
rather than left as an omission: their case is `JNL-46`, which is not in
`required_cases.REQUIRED_CASES`. Adding a required case is a reviewer's decision
and not an importer's, so this module neither requires an observation for it nor
accepts one.

### 2.5 An importer cannot supply experimental evidence

This is the half an ingestion stage does not answer, and it is enforced rather
than promised:

* `classify_supplied_observations` **refuses to count a case covered** while the
  plan declares it unresolved, however many well-formed records arrive for it —
  the case appears in `unresolved_cases`, never in `covered`, and no record is
  produced for it;
* a record for a case nobody requires is refused outright; and
* `EvidenceResult.complete` is false while any required case **or any variant**
  has no validated record, and the missing keys are named.

### 2.6 The trust boundary — `execution/evidence_cli.py`

R14 asked what stops a supplied payload reaching the component that constructs
the process boundary. The answer is not a flag on `cli.py`, which is the one
module that constructs a `SubprocessBoundary` and a `SystemMaterializer`. The
answer is a **different program with a different import graph**:

`execution/evidence_cli.py` imports the planner, the review manifest, the
importer and the records tier. It imports **no** `boundary`, **no** `executor`,
**no** `materializer`, and it does not import `cli`. There is therefore no call
path from a payload to a process.
`test_no_execution.py::test_the_ingestion_entry_point_cannot_reach_a_process`
asserts that against its syntax tree, asserts it defines none of `--execute`,
`--confirm-target` or `--reviewed-digest`, and asserts it names none of
`SubprocessBoundary`, `SystemMaterializer` or `ExecutingRunner` in its code.

### 2.7 The run record and the classified artifact are different documents

They are written by different programs to different destinations under different
schemas. `execution/artifact.py` writes the **run record** — what ran and what
was observed — from `cli.py` after an `--execute`. `evidence_cli.py` writes the
**classified evidence artifact**: one `records.EvidenceRecord` per case, each
carrying its expectation, its observation and its derived status.

The artifact is **persisted and validated before a path is reported**:
`serialize_records` validates the set before producing bytes, the bytes are
written, **read back from disk**, passed through `deserialize_records` — which
reconstructs every record through the same constructor, so a stored status that
disagrees with its own stored observations is a refusal — and the digest of what
came back is compared with the digest of what went out. Every failure returns a
refusal, never a path. A tampered artifact is asserted not to read back.

---

## 3. C-8 — the concrete creation design, submitted for technical review

**This section is the design the earlier recommendation asked to have reviewed
before implementation.** It is submitted here in full, with the implementation
beside it, so Codex can review the mechanism and direct changes to it. Nothing in
it has been executed.

### 3.1 Why a better probe was never available

R13 proved the disposable root absent with `stat --format=%F` exiting 1 and made
that one observation the ownership of every path under it. Coreutils gives every
failure the same 1 — `ENOENT`, `ENOTDIR`, `ELOOP`, `ENAMETOOLONG`, `EACCES` and
`EIO` are one number — so a directory that existed on a filesystem returning
`EIO` satisfied the baseline and cleanup's `rmdir` was entitled to it. R14
conceded that and blocked the baseline; the 29 path mutations were owned by
nothing and the plan created no file at all.

`stat`, `lsattr` and `getcap` report absence only as a generic failure; `namei`
distinguishes them only in message text, which is locale- and version-dependent
host prose this harness does not parse; and no permitted creation reports
pre-existence the way `groupadd` and `useradd` report exit 9 — `install -d`
succeeds on a directory that is already there and `install` overwrites a file
that is.

And a probe is the wrong **shape** regardless. Between *"it was not there"* and
*"create it"* there is a window in which the object can arrive.

### 3.2 The bounded creation mechanism

**`mkdir(2)`, and the successful creation is the ownership.** There is no
preliminary absence check, so there is no window. `mkdir(2)` reports a path that
is already occupied as **`EEXIST`**, uniquely and documentedly, and reports it
for a directory, a regular file, a symbolic link **and a dangling symbolic
link** alike — which is precisely what R14 said the filesystem did not have.

The operation is the case program's new `mkroot` verb: `os.mkdir(path, 0o755)`,
then `open(path, O_RDONLY|O_DIRECTORY|O_NOFOLLOW)`, then `fchmod(fd, 0o755)` so
the process umask cannot decide the mode and no path is resolved a second time,
then `fstat(fd)`. Owner and group are `root:root` by construction: `mkdir(2)`
gives the directory the creating process's uid and gid, and this vector runs as
`E7`.

### 3.3 The bootstrap location, and the dependency it answers

A helper that creates the disposable root cannot first be installed inside that
root, and installing it anywhere else would create a second host object with the
same unprovable pre-existence — the problem one directory up.

The creation therefore runs **the reviewed source in the repository tree**:

```text
/opt/freedom-blades/runtime/venv-web/bin/python -I -S \
  /opt/freedom-blades/platform/tools/phase_5_0_evidence/execution/case_program.py \
  mkroot /var/lib/fb-evidence-p5-0
```

That file is **not a host object this run creates, modifies or removes** — its
lifecycle is the repository's, exactly as `capsh`'s is the operating system's. It
is already a covered source of the review manifest, and `install` later copies
those exact bytes to `<root>/bin/case`, so **one digest covers both copies** and
the program that creates the root is the program that runs the experiments.

The partition between the two copies is **total in both directions and enforced
twice** — by `case_runtime.validate_case_vector` before a process exists, and by
`execution/case_program.py` from its own constants:

| Copy | `sys.argv[0]` | Verbs it may run |
|---|---|---|
| bootstrap | the reviewed source path | `mkroot`, `statroot`, and no other |
| installed | `<root>/bin/case` | every other verb, and neither of those |

A third program path is refused. A run that lost its installed program cannot
fall back to the repository and keep going; an experiment cannot be run from the
repository copy.

### 3.4 The approved root, and the argument that names it

The one admissible value of the new `ROOT_PATH` argument kind is the confirmed
target's own `root_path`, `/var/lib/fb-evidence-p5-0`. It exists as a kind
because the root is the one path that is not *strictly inside* the root; it
admits exactly one string, so it is a constant the vector states rather than a
path a caller composes. `/var/lib/fb-evidence-p5-0/journal`, `/var/lib`, a
trailing slash and any near miss are refused by both validators.

### 3.5 The result vocabulary

| Outcome | Exit | What it establishes |
|---|---|---|
| the call returned | `0` | **ownership.** `created=yes`, and the device and inode of the directory this call made |
| something is already at the path | `15` (`EEXIST`) | nothing. The run stops, ownership is **withdrawn**, and no path under the root is removed |
| the parent does not resolve to a directory | `16`/`1` (`ENOENT`, `ENOTDIR`) | nothing. Unexpected parent resolution stops the run |
| any other refusal | `10`–`14`, `1` (`EPERM`, `EACCES`, `EROFS`, `ELOOP`, `EIO`) | nothing. None of them is *absent* and none is a creation |
| created, identity unreadable | `66` | **bounded residue.** `mkdir` returned and the `open`/`fstat` did not |
| interrupted, timed out, never reported | — | the same as `66` |

`nothing_created_statuses` enumerates the first four rows; **everything else is
the uncertain case**, and `CommandStep.created_nothing` answers `False` for every
status a step did not enumerate — including the executor's own `-1` for a launch
that never reported. That is the conservative default rather than an omission.

### 3.6 The ownership evidence, and what it reaches

`B3-01` declares `establishes_ownership_by_creation = ("directory:<root>",)` and
`establishes_ownership_of_contained` — the **28** declared mutations strictly
inside it, enumerated in the plan and pinned in the manifest rather than derived
at run time. Together they are the 29 R14 left owned by nothing.

**The one inference this rests on, stated because it is not a direct
observation:** `mkdir(2)` returns a directory containing nothing but `.` and
`..`, so at the instant the creation is satisfied there is no object under that
path for a later step to overwrite and no object this run could later delete that
it did not itself put there. `CommandStep._validate_exclusive_creation` requires
every contained id to name a path strictly inside a directory the same step
creates exclusively.

The executor grants both **after** the step is satisfied and only then; the
ownership gate that runs before every other mutation is exempted for exactly the
mutation the step is creating, because there is nothing that could have satisfied
it. `B3-02` then reads the created directory's owner, group, mode and type back
with `stat` and compares all four.

**`R-B-ROOT` is unchanged and establishes nothing.** Ownership was deliberately
**not** reattached to it. It is retained as a precondition that stops an
obviously doomed run before a single identity is provisioned; a run that reaches
`B3-01` regardless is stopped there by `EEXIST`.

### 3.7 Cleanup validation, and what a replaced path does not inherit

A new cleanup step kind, `REVALIDATE`, is generated immediately before the one
`rmdir` that removes the root — which is the end of the plan, because the root is
declared first and reversals run in reverse declaration order. Its vector is the
same bootstrap copy running `statroot`, and it reads the root's device and inode
with `O_DIRECTORY|O_NOFOLLOW`, so a symbolic link or a non-directory at the path
is a refusal rather than a redirection.

The executor compares that reading with the one **the creation** made, and with
nothing else: the expected value is the earlier of the two observations, so the
identity is never learned from the reading it is judging. Three ways to answer
no — no recorded creation identity, a reading missing or unreadable in either
key, or a disagreement — and all three skip the removal, report the path as
**residue**, and leave the run at S-B. Replacement of a path does not inherit
permission to delete its replacement.

**The residual window is stated rather than glossed.** `rmdir(2)` takes a path
and not a descriptor, so a replacement performed between this reading and the
removal is not detectable by this design. What is closed is the window between
the creation and the cleanup, which is the whole of the run.

The revalidation applies **exactly when the removal applies** — it declares
`applies_with` naming the root's mutation — so a run that created nothing never
re-reads a root it never made. It reverses nothing, `CleanupStep` refuses one
that claims to, and it is the only cleanup step permitted to record an
observation.

### 3.8 Interruption, uncertain outcomes and retention

* An exclusive creation that did not return and did not enumerate its status is
  an **uncertain creation**: the mutation is recorded as attempted, ownership is
  never granted, the reversal is skipped, and the path is reported as **residue**
  with the named operator recovery. It is deliberately not reported as
  *preserved*, because *preserved* claims this run did not create the object and
  an uncertain creation cannot support that claim.
* An operator interruption and a boundary that raised are the same case, by the
  same rule.
* **Configuration-backup retention is unchanged.** The two byte-exact captures,
  and the directories holding them, are retained unless the restore, the single
  reload and both post-reload observations were satisfied — R13's EH-R13-2 — and
  the capture directory is inside this root, so it is retained by the same rule
  whether or not the root is removable.

### 3.9 Mutation accounting and cleanup applicability

| Figure | R14/R15 | This tree |
|---|---|---|
| Ownership from a probe | 10 steps over 12 mutations | 10 steps over **12**, unchanged |
| Ownership from an exclusive creation | — | **1 step over 29** |
| Blocked mutations | **29** | **0** |
| Mutations with no ownership route | 0 | 0 |
| Cleanup steps | 46 | **47** — the revalidation |

The two `postgres_config_line` mutations remain in neither set, unchanged: their
reversal is a restore of a byte-exact pre-change capture, not a removal.

**Retained without change:** the R14 database and role catalog corrections
(`R-B-DB` and `R-B-ROLE` still read a listing the server returns and compare a
subject and a control), `getent`'s documented exit 2, `R-B-UNIT`'s compared
`LoadState`, and every pre-existing-object test — a pre-existing group, account,
database, role or unit still stops the run and is still never removed.

---

## 4. Files changed

| File | Change |
|---|---|
| `tools/phase_5_0_evidence/execution/case_program.py` | `getimmutable`, `clearimmutable`, `mkroot`, `statroot`; `FS_IMMUTABLE_FL`; `ROOT_DIRECTORY_MODE`; the `ROOT_PATH` argument kind and `validate_root`; `BOOTSTRAP_PROGRAM_PATH` and the two-copy partition |
| `tools/phase_5_0_evidence/case_runtime.py` | the four verb specs; `ArgumentKind.ROOT_PATH`; `BOOTSTRAP_VERBS`; `ROOT_PREEXISTING_STATUS`; `ROOT_NOTHING_CREATED_STATUSES`; `build_bootstrap_vector`; the bootstrap half of `validate_case_vector` |
| `tools/phase_5_0_evidence/capture.py` | `fs_immutable_fl`, `created`, `root_device`, `root_inode` in `CASE_RESULT`; the `wide_number` shape |
| `tools/phase_5_0_evidence/plan.py` | `establishes_ownership_by_creation`, `establishes_ownership_of_contained`, `nothing_created_statuses`, `created_nothing()`, `_validate_exclusive_creation` and the one bounded exception to the mutation-capture rule |
| `tools/phase_5_0_evidence/cleanup.py` | `CleanupStepKind.REVALIDATE`; `CleanupStep.capture`, `requires_revalidated`, `applies_with`; `_revalidate_root`; applicability decided from `applies_with` for a step that reverses nothing |
| `tools/phase_5_0_evidence/concrete_plan.py` | `_create_disposable_root`; the C-8 blocker removed; `_band_5_immutable_experiments` replacing `_band_5_unresolved_operations`; `_band_7` rewritten as `ExternalCase`s; `ExternalCase`; `_validate_capability_experiment_ordering`; `_RETURNED_FACTS` extended |
| `tools/phase_5_0_evidence/observations.py` | **new.** The importer, the closed Band-7 schema, custody, the producer mapping and `EvidenceResult` |
| `tools/phase_5_0_evidence/execution/evidence_cli.py` | **new.** The ingestion entry point, with no import path to a process |
| `tools/phase_5_0_evidence/journal.py` | `classify_stage_failure`, `classify_cleanup_failure_state`, and their reviewed constants |
| `tools/phase_5_0_evidence/required_cases.py` | the third coverage column, `supplied_externally` |
| `tools/phase_5_0_evidence/review_manifest.py` | `MANIFEST_VERSION` **7 → 8**; the two new covered sources; per-step creation-ownership fields; per-cleanup-step `capture`, `requires_satisfied`, `requires_revalidated`, `applies_with`; `external_cases`; `supplied_observations`; `creation_ownership_count` and `external_case_count` in the digest |
| `tools/phase_5_0_evidence/execution/executor.py` | ownership by creation granted after satisfaction; uncertain creations tracked and reported as residue; the cleanup revalidation and its comparison; `_uncertain_residue`; `_preserved` narrowed |
| `tools/phase_5_0_evidence/execution/cli.py` | §5c rewritten, §5d added, §6 rewritten; the dry run reports creation ownership and external cases |
| `tests/phase_5_0_evidence/test_r16_c6_c7_c8.py` | **new**, 64 tests |
| `tests/phase_5_0_evidence/harness_fixtures.py` | `runnable_plan()` no longer reattaches any ownership; `revalidation_observations`, `cleanup_observations_for`, `creation_step` |
| `tests/phase_5_0_evidence/test_r14_remediation.py` | the six blocked-baseline tests replaced by the exclusive-creation ones, including the replaced-path and uncertain-creation cases |
| `tests/phase_5_0_evidence/test_r13_remediation.py` | `FakeHost` models `mkroot` and `statroot`; the ownership partition now has two routes; the gate test asserts a synthetically blocked plan |
| `tests/phase_5_0_evidence/test_no_execution.py` | the two new modules declared in their tiers; the ingestion entry point's import graph and the importer's asserted |
| `tests/phase_5_0_evidence/test_concrete_plan.py`, `test_executor.py`, `test_executor_cleanup.py`, `test_expectations.py`, `test_late_binding.py`, `test_root_identity.py`, `test_case_program.py` | updated for the new steps, the new kind and the new ordering |
| `tests/web/test_p3_4_static_assets.py` | the two new harness sources declared in the permitted set |
| `docs/review/phase-5-0-evidence-harness-concrete-plan.md` | regenerated, never hand-edited |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json` | regenerated |

**The manifest version moves to 8** because a digest approved under 7 covered a
plan that ran none of the experiments, created no file at all and had no
ingestion stage. That is a different plan, not a differently rendered one, so it
stops matching rather than being reinterpreted.

No production file was changed. The dirty worktree was preserved; nothing was
staged, committed, reset or pushed.

---

## 5. Required case → producer → collection procedure

Generated by `observations.producer_mapping()` from `REQUIRED_CASES` and the
plan, so a case with no producer is visible as exactly that.

| Case | Band | Producer | In this harness? | Produced by | Collection procedure |
|---|---|---|---|---|---|
| `JNL-49-E4-CLEAR-ARCHIVE-IMMUTABLE` | capability | this plan's own step under `E4` | **yes** | `B5-C6-02` | the executor records the step's observation directly |
| `JNL-49-E6-CLEAR-ARCHIVE-IMMUTABLE` | capability | this plan's own step under `E6` | **yes** | `B5-C6-04` | as above |
| `JNL-50-E5-CLEAR-THEN-DENIED-OPEN` | capability | this plan's own steps under `E5` | **yes** | `B5-C6-06`, `B5-C6-07` | as above |
| `JNL-51-PROVENANCE-OMITTED` | provenance | a run of `init-generation` on the disposable host after D8 was suppressed, or after `PVR` was deleted from a successful deployment | **no** | — | record whether `APR` and `PVR` are present; run `init-generation` and record its refusal code; list `…/journal` and record which of the four generation artifacts exist; query `sheet_writer_journal_generations`; establish from the syscall trace whether `verify-capability` was invoked |
| `JNL-47-NO-GENERATION-ON-FAILURE` | journal | a run of the §2.13.2a probe and `init-generation` with a failure injected at one named stage | **no** | — | inject the failure at the named stage; list `…/journal`; query for a generation row. **One record per stage**, and the case is not covered until all five are supplied |
| `JNL-47-RECOVERY-STATE` | journal | a run whose cleanup failed, once after a probe-stage failure and once after a fully passing probe | **no** | — | record the exit code and §2.13.2b state; count the residue paths; record generation and database absence; attempt a second run and record whether it refused; record whether the operator recovery was named. **One record per variant** |

**No required case has a missing producer.** The three externally produced cases
have a named producer that is not this harness, and the importer cannot close one
of them for a plan that declares it unresolved.

---

## 6. Verification

`TEST_DATABASE_URL` was **explicitly unset** throughout. Structural
no-execution checks were run first, then the focused suites, then the complete
harness suite, then the other available non-database suites serially.

| # | Command | Result |
|---|---|---|
| 1 | `pytest -q tests/phase_5_0_evidence/test_no_execution.py` | **193 passed** |
| 2 | `pytest -q tests/phase_5_0_evidence/test_r16_c6_c7_c8.py test_r14_remediation.py test_r13_remediation.py` | **165 passed** |
| 3 | `pytest -q tests/phase_5_0_evidence` | **1335 passed** |
| 4 | `pytest -q -rs tests/test_*.py` | **2990 passed, 326 skipped** |
| 5 | `pytest -q -rs tests/web` | **1610 passed, 1362 skipped** |
| 6 | `node --test "foundry-module/tests/"*.test.mjs` | **171 pass, 0 fail** |
| 7 | `compileall tools/phase_5_0_evidence tests/phase_5_0_evidence` | exit 0 |
| 8 | `git diff --check` | clean |

Before this change, tests 1 and 3 stood at **181** and **1255** on the R14/R15
tree, which is the tree R15 accepted.

**The skip counts are the restriction, not a pass.** `TEST_DATABASE_URL` is unset
under this prompt, so every database-marked test skipped: 326 in the bot suite
and 1362 in the web suite, against the 80 a properly configured disposable
PostgreSQL would leave. **No database-backed assertion in this submission was
executed**, and no earlier passing total is reused: every figure above was
produced against the tree submitted here.

**Two web-suite failures were found and fixed, and they were this change's.**
`tests/web/test_p3_4_static_assets.py` polices which files under `tools/` a
change may touch and requires every evidence-harness source in the tree to be
declared. `observations.py` and `execution/evidence_cli.py` were undeclared; both
are now in the permitted set with the reason they exist. The suite is green
against the submitted tree.

**Interpreters, reported as the fallbacks they are.** The canonical `oracle-test`
interpreter is `/opt/freedom-blades/runtime/venv-web/bin/python`. A file exists at
that path on this workspace host and **it is not that interpreter**: it has no
`pytest`. Tests 1, 2, 3, 5 and 7 ran under
`/opt/discord-bots/venv-web/bin/python` (CPython 3.12.3, pytest 8.4.2) and test 4
under `/opt/discord-bots/venv/bin/python`, both **explicitly local fallbacks**.
An interpreter path on one host does not establish its availability on another,
and **nothing was run on `oracle-test`**.

**Configured tooling, reported honestly.** No formatter, linter or type checker is
configured in this repository: there is no `pyproject.toml`, `setup.cfg`,
`.flake8`, `mypy.ini`, `ruff.toml` or pre-commit configuration. They were not run
because there is nothing configured to run, not because they were skipped.
`compileall` and a trailing-whitespace, tab and conflict-marker scan of every
changed file stand in their place; `git diff --check` covers tracked files only,
because the harness tree is still untracked.

### 6.1 Failure and cleanup evidence, asserted rather than described

Every row is a test in the submitted tree, driven across injected fakes. No host,
socket, database or process was involved in any of them.

| Situation | Asserted outcome |
|---|---|
| the root already exists; `stat` gives its generic failure | the run stops at `B3-01` with **exit 15**, ownership is withdrawn, the directory survives, no `rmdir` and no `rm` is requested, and the path is reported as *preserved* |
| the same, continued | **no `install` is reached at all** |
| `mkdir` returned and the identity could not be read (exit 66) | the mutation is attempted, ownership is never granted, the path is **residue**, the state is **S-B**, no `rmdir` is requested, and the artifact is not admissible |
| the boundary raised on the creation | the same, by `nothing_created_statuses` not admitting the executor's `-1` |
| the root is replaced between the creation and the cleanup | `statroot` reports a different inode, the comparison fails, `rmdir -- <root>` is **never called**, the path is residue and the state is **S-B** |
| the revalidation agrees | the removal runs, the root is gone, the state is **S-C** |
| an interruption at each mutation prefix | the applicable cleanup runs exactly once; a prefix that stopped on the creation itself leaves residue rather than a reversal |
| `E4` returns, or is refused with `EACCES` | the step is unsatisfied, the run stops there, nothing after it runs |
| `E6`'s control clears nothing | the same — and `JNL-49`'s `E4` case is therefore inconclusive rather than passed |
| `E5`'s denial arrives as `EPERM` | the same: it would mean the flag was still set and the discretionary check was never reached |
| an initial-state reading that reports `fs_immutable_fl=0` | the same: an experiment against an inode whose flag is already gone asserts nothing |
| a supplied payload that is malformed, unknown, duplicated, mismatched or contradictory | refused, in twenty-four parametrised rows |
| a supplied record for a case the plan declares unresolved | validated, **not counted**, reported unresolved, and the result is not complete |
| a payload missing two variants | `complete` is `False` and both missing keys are named |
| a tampered classified artifact | does not read back |
| an unwritable artifact destination | a refusal, and no path is reported |

### 6.2 Generated artifacts, regenerated twice and compared

Both were produced by

```sh
python -m tools.phase_5_0_evidence.execution.cli \
  --render docs/review/phase-5-0-evidence-harness-concrete-plan.md \
  --manifest-out docs/review/phase-5-0-evidence-harness-review-manifest.json
```

which is a dry run: it prints what would run and starts nothing. They were then
generated a second time to a scratch directory and compared byte for byte:
**identical**.

| Artifact | SHA-256 of the file |
|---|---|
| `docs/review/phase-5-0-evidence-harness-review-manifest.json` | `663f603035c967010f12ca5e900d3688262aad1ca224a38eacb2ade4e5314bc5` |
| `docs/review/phase-5-0-evidence-harness-concrete-plan.md` | `7d8a9892c0be6b68b4637d20dfa1bc3c80eb50e01998af35e8b707dba498f76b` |

| Figure | R14/R15 | This tree |
|---|---|---|
| Covered sources | 30 | **32** |
| Command steps | 127 | **139** |
| Cleanup steps | 46 | **47** |
| Mutations | 43 | 43, unchanged |
| Materializations | 2 | 2, unchanged |
| Expectation contracts | 66 | **77** |
| Binding sites | 21 | **33** |
| Ownership baselines | 10 steps over 12 | 10 steps over 12, unchanged |
| Creation ownership | — | **1 step over 29** |
| Blocked mutations | 29 | **0** |
| Unresolved items | 7 | **0** |
| External cases | — | **3** |
| Conflicts | C-6, C-7, C-8 | **none** |
| `executable` | False | **True** |
| Manifest version | 7 | **8** |

Every new trusted module and every new input contract is inside the manifest:
`observations.py` and `execution/evidence_cli.py` are covered sources, the
importer's schema, version, bounds, custody vocabulary, synthetic marker and
per-case field shapes are pinned in `supplied_observations`, the external cases
and their producers are pinned in `external_cases`, and the creation-ownership
fields and the cleanup revalidation are pinned per step.

---

## 7. The read-only preflight, proposed and not performed

**Authorization, recorded here so it is not requested again.** The maintainer
authorized a bounded read-only target preflight for the stage **after Codex
reviews this implementation**. Codex coordinates it and verifies its evidence.
This assignment did not instruct Claude to perform it, and it was not performed:
`oracle-test` was not contacted, inspected or synchronized, and the twelve facts
remain `UNCONFIRMED`.

### 7.1 The exact future launcher context

Every fact below must be observed **in the process the reviewed vector actually
produces**, and a fact taken from a different SSH, `sudo` or process context must
not be substituted. Specifically:

* the interpreter facts are properties of the executable at
  `/opt/freedom-blades/runtime/venv-web/bin/python` **on `oracle-test`**, read
  through the same `-I -S` isolation the reviewed vector uses; and
* the ten `E7` facts are properties of **the harness's own root process on
  `oracle-test`, at the moment it would run the plan** — the process that would
  be `ExecutingRunner`'s, entered the way the operational run will enter it. A
  reading taken from an interactive `ssh oracle-test sudo -i` shell, from a
  different `sudo` rule, from a systemd unit, from a container, or from a login
  path with a different bounding set is a reading of **another process**, and
  §2.13.5c's `E7` row would then be wrong for the run that matters.

The preflight is a **read**. It creates nothing, modifies nothing and removes
nothing, and it inspects only the approved `oracle-test` target — never
credentials, never `.env`, never a service-account file, and never a production
or staging system.

### 7.2 The twelve facts, and the command proposed for each

| # | Fact | Constant it supplies | Proposed read-only command |
|---|---|---|---|
| 1 | interpreter SHA-256 | `case_runtime.EXPECTED_INTERPRETER_SHA256` | `sha256sum -- /opt/freedom-blades/runtime/venv-web/bin/python` |
| 2 | interpreter resolved path | `case_runtime.EXPECTED_INTERPRETER_REAL_PATH` | `readlink -f -- /opt/freedom-blades/runtime/venv-web/bin/python` |
| 3 | `E7` uid | `capability.E7_TARGET_FACTS["uid"]` | `awk '/^Uid:/{print $2}' /proc/self/status` |
| 4 | `E7` gid | `…["gid"]` | `awk '/^Gid:/{print $2}' /proc/self/status` |
| 5 | `E7` supplementary groups | `…["groups"]` | `awk '/^Groups:/{$1="";print}' /proc/self/status` |
| 6 | `E7` `CapInh` | `…["cap_inh"]` | `awk '/^CapInh:/{print $2}' /proc/self/status` |
| 7 | `E7` `CapPrm` | `…["cap_prm"]` | `awk '/^CapPrm:/{print $2}' /proc/self/status` |
| 8 | `E7` `CapEff` | `…["cap_eff"]` | `awk '/^CapEff:/{print $2}' /proc/self/status` |
| 9 | `E7` `CapBnd` | `…["cap_bnd"]` | `awk '/^CapBnd:/{print $2}' /proc/self/status` |
| 10 | `E7` `CapAmb` | `…["cap_amb"]` | `awk '/^CapAmb:/{print $2}' /proc/self/status` |
| 11 | `E7` `NoNewPrivs` | `…["no_new_privs"]` | `awk '/^NoNewPrivs:/{print $2}' /proc/self/status` |
| 12 | `E7` securebits | `…["securebits"]` | `/usr/sbin/capsh --print` — the `securebits:` line, and no other |

Facts 3–11 are one read of `/proc/self/status` in the launcher's own process;
they are listed separately because each supplies a separate reviewed constant.

**Fact 12 needs a word about which process it describes, because R13's EH-R11-2
was exactly that mistake.** The kernel exposes securebits through `prctl(2)` and
through no file. `capsh --print` reports the securebits of **`capsh`'s own**
process, which R13 correctly refused as evidence of a *constructed* identity's
final state — a `capsh` construction changes the value between that reading and
the `execve` the case runs in. **`E7` is the one identity that constructs
nothing**: securebits survive `execve` except `SECBIT_KEEP_CAPS`, which is never
set here, so a `capsh --print` run directly by the launcher reports the launcher's
own word. That is the reason this command is admissible for `E7` and would not be
for `E1 … E6` or `E8`.

Codex may prefer to read it in-process instead, with the same
`prctl(PR_GET_SECUREBITS)` the reviewed case program makes. Either way it must be
read in **the same process** as facts 3–11, or it describes a different one.

Two facts §2.13.5c depends on and that are worth reading in the same pass, though
they are not among the twelve: `CAP_LAST_CAP` from `/proc/1/status`'s `CapBnd`,
and `getcap`/`stat` on the interpreter to confirm it carries no file capability
and no set-user-ID bit.

**Every one of the twelve remains unconfirmed** until the authorized later stage
supplies the evidence and Codex verifies it. Supplying one changes a covered
source, which changes the manifest digest, which triggers exactly the re-review
it should.

---

## 8. Remaining limitations, and what this submission does not do

* **It closes no finding and no gate.** `EH-R13-4`, `EH-R14-1`, the C-6/C-7/C-8
  dispositions and the readiness of Package 5.0 are the independent reviewer's.
* **`is_executable` is `True` and confers nothing.** The executor still refuses
  at gate 3 (the two interpreter facts), gate 4 (`E7`'s ten facts), gate 5 (the
  exact confirmation token) and gate 6 (a reviewer-supplied digest for this exact
  tree). A passing suite and an executable-on-paper plan are not operational
  execution authority.
* **`JNL-46` has no supplied-observation route.** `manifest.py`'s two classifiers
  remain callable and unwired, because `JNL-46` is not in `REQUIRED_CASES` and
  adding a required case is a reviewer's decision.
* **The C-8 residual window is real.** `rmdir(2)` takes a path, not a descriptor,
  so a replacement performed between the revalidation and the removal is not
  detectable by this design.
* **Contained ownership is an inference**, stated in §3.6 and pinned in the
  manifest, not a direct observation.
* **Nothing establishes that the reviewed producers exist.** The three externally
  produced cases name a producer this harness does not contain, and their
  observations do not exist yet.
* **No operational observation has been supplied.** Every payload exercised here
  is a synthetic fixture, bound to the synthetic target identity, and is
  structurally ineligible for operational acceptance.

## 9. Operational restrictions observed

No SSH. `oracle-test` was not contacted, inspected or synchronized. No generated
vector was run, `--execute` was not used, no real process boundary or
materializer was armed, no database operation was performed and the destructive
backup/restore drill was not run. `TEST_DATABASE_URL` was left unset throughout.
No host object was created, and no `git` write of any kind was performed.
General administrative access to the disposable server was not treated as
permission for any of it.

Package 5.0 remains **not ready**. `P5.0-R5` remains **Blocking** and `OD-62`
remains **Open**. Migration `0014`, product implementation, deployment, cutover
and Package 5.1+ remain unauthorized and none was performed.

**Stopping here for Codex's independent implementation review.** Codex owns that
review, the technical design review of §3, and the subsequent preflight
coordination.
