# Package 5.0 — runner contract, revision 3

Date: 2026-09-11. Author: Claude. Change record: C-P5.0-LAB-1.

**Status: submitted for Codex technical review. Not accepted, not implemented,
and no execution is authorized.**

> **Superseded and erratum, 2026-09-11.** The
> [R3 re-review](project-review-2026-09-11-r3.md) requested changes, and
> [runner contract r4](phase-5-0-reserved-laboratory-runner-contract-r4.md)
> **supersedes this document in its entirety**. This revision is preserved
> unchanged as the submission that review answered; its historical conclusions
> are not rewritten. Five statements in it do not hold, and r4 replaces rather
> than amends them:
>
> 1. **§5.8's `not_durable` row — "nothing is treated as initialized".** True of
>    the writer and false of the filesystem. The rename has already happened, so
>    the record is readable and a process-only restart retains it
>    (PR-20260911-R3-1). r4 §5.6 adds the successor's re-seal.
> 2. **§5.4's ordering, and §5.7's refusal table, specified publication and
>    never specified reading.** There was no successor obligation between the
>    visible name and the barrier. r4 §5.6 and §5.7 are that protocol.
> 3. **§5.5's "a crashed test run is not a reservation and must not block the
>    host forever", and §5.2's six participants that write no lifecycle state.**
>    Withdrawn (PR-20260911-R3-2). r4 §5.11 gives all seven durable
>    in-progress and completion accounting; the "forever" concern is answered by
>    a bounded, attributable operator recovery rather than by an exemption.
> 4. **§5.8's `binding_mismatch` row.** The refusal was declared and no branch
>    produced it (PR-20260911-R3-3). r4 §5.10 gives it an enforcing path.
> 5. **§5.6's shape table, and §5.9's account of what the repair validated.**
>    Neither `verified_first_use` nor `operator_recovered` carried a target
>    binding, and the first-use attester and basis reached neither the parser nor
>    the validator (PR-20260911-R3-3). r4 §5.8 adds both, and the code change is
>    in `reservation.py`.
>
> §9's model rows 16b and 16c relied on `test_the_initialized_record_admits_every_participant`,
> which constructed a history rather than reading one; that end-to-end claim is
> **withdrawn**, the test is relabelled a unit test, and r4 §9 rows 39 and 40 are
> the connected replacements. §§1–4 and §8 are carried into r4 unchanged.

**This revision supersedes
[`phase-5-0-reserved-laboratory-runner-contract-r2.md`](phase-5-0-reserved-laboratory-runner-contract-r2.md)
in its entirety**, which supersedes
[revision 1](phase-5-0-reserved-laboratory-runner-contract.md). Both are
preserved unchanged as the submissions their reviews answered, r2 now carrying a
dated supersession and erratum notice. Where any two disagree, **this one is the
proposal and the earlier ones are history**.

It answers the September 11 re-review's Blocking finding **PR-20260911-R2-2** and
Important findings **PR-20260911-R2-3** and **PR-20260911-R2-4**, and it carries
forward every part of r2 that survived that review. **No contradictory r2 row is
left authoritative**: this document is the complete contract, including the
operation tables, recovery, lock and lifecycle storage, privilege inventory,
residuals and tests.

**PR-20260911-R2-1 is not answered here**, because it was a defect in code rather
than in design. It is repaired in `tools/phase_5_0_evidence/reservation.py`, and
§5.9 records what the repair was and where its regressions are.

Nothing here repairs **EH-R16-1**. It remains Open, the harness retains its
unconditional real-execution refusal (`reservation.REAL_EXECUTION_REFUSAL`), and
a reserved host does not close it — §1.1 says why in the finding's own terms.

The reserved-laboratory direction stands, VM work stays deferred, and ADR 0011
stays **Proposed**. This is not a second architecture survey.

---

## 0. How to read a claim in this document

Four kinds of statement appear below and they are not interchangeable. r2 used
three; the fourth is added because this revision carries model results and a
model result is neither a documented semantic nor a design inference.

| Label | What it means | How it may be checked |
|---|---|---|
| **[D] documented** | A semantic the primary manual page states. Verified against `man-pages 6.7` as installed on this workstation, cited by page, and cross-read against the pages the re-review links: [open(2)](https://man7.org/linux/man-pages/man2/open.2.html), [fsync(2)](https://man7.org/linux/man-pages/man2/fsync.2.html), [unlink(2)](https://man7.org/linux/man-pages/man2/unlink.2.html). | read the cited page |
| **[P] proposed** | A guarantee this design would provide *if* it were built and *if* its prerequisites hold. **Nothing below is built.** | review the argument; then the model rows of §9 |
| **[M] modelled** | A result observed from a bounded synthetic model in this repository, over injected effects. It establishes that the proposed rule is constructible and falsifiable, and **nothing about Linux or about `oracle-test`**. | run the named test; read `durability_model.MODEL_LIMITS` |
| **[A] assumed** | An operational premise nobody has verified on the target, or a trust statement about people. | it is not checked here, and §10 lists every one |

The twelve unconfirmed target facts remain unconfirmed and none is populated by
this document. Every **[A]** below is a statement about the design's premises,
not an observation of `oracle-test`.

**The separation the re-review asked for, stated once.** §9 separates documented
semantics, design inference, modelled results and unperformed target
verification, and §9.3 lists the implementation checks that would establish the
real properties. **None of those has been performed**, and no real filesystem
durability drill was run in this pass.

### 0.1 What the reservation changes, and what it does not

Unchanged from revisions 1 and 2, and restated because every row below depends
on it:

| | Before the reservation | After it |
|---|---|---|
| An unrelated cooperating writer (a test run, a sync, a dependency update) substitutes an object mid-run | possible, and undetected | excluded by the lock plus the pre-admission inventory **[P]**; a detected violation invalidates the affected evidence |
| A host administrator substitutes an object mid-run | possible | still possible. Trusted not to; not prevented, and not claimed to be **[A]** |
| **This run's own experimental writers** substitute an object mid-run | possible | **still possible.** This is EH-R16-1, and §1 is the whole of this document's answer to it |

---

## 1. Effect ownership — PR-20260911-1

### 1.1 What the earlier reviews established, conceded before the replacement

Four claims in revision 1 §§5 and 9.2 do not hold, and the mechanism below is
built on their negations rather than around them. This section is unchanged from
r2 and is not reopened.

1. **A held descriptor keeps referring to its original inode after the pathname
   is replaced.** `open(2)` is explicit that the descriptor refers to the opened
   file description and that later changes to the path do not change it **[D]**.
   So comparing a held descriptor's `fstat` with the `fstat` recorded when that
   same descriptor was opened compares a value with itself. It succeeds for every
   input, including the input it was supposed to detect. Revision 1 §9.2(b)
   offered exactly that comparison as the remedy. **It is withdrawn.**
2. **`unlinkat(dirfd, name, 0)` resolves `name` at the time of the call.**
   `unlink(2)` states that a relative pathname is interpreted relative to the
   directory the descriptor refers to **[D]** — the *prefix* is bound, the final
   component is not. A held, unchanged parent descriptor therefore removes
   whatever `name` resolves to now.
3. **`RENAME_NOREPLACE` protects the destination, not the source.**
   `rename(2)` says it returns `EEXIST` if `newpath` already exists **[D]**. It
   says nothing about the identity of the source entry, so it cannot bind a
   source to a previously observed inode.
4. **A descriptor local to one case-program invocation cannot cover a chain that
   spans the run.** The existing boundary launches each step as a separate
   process (`tools/phase_5_0_evidence/execution/boundary.py:841`), and revision 1
   specified `DIRFD` as an index into descriptors *the program opened itself in
   this invocation*. Those two statements are incompatible.

The consequence is the one the review drew: **retaining a descriptor can support
a remedy; the comparison revision 1 proposed is not that remedy.**

### 1.2 The three protections, and which one covers each effect

Unchanged from r2. There is no single syscall that binds every effect to an
object; there are three mechanisms with different reach.

| | Protection | What it binds | What it cannot bind |
|---|---|---|---|
| **B1** | **Exclusive creation.** `mkdirat`/`openat` with `O_CREAT\|O_EXCL\|O_NOFOLLOW`. Success proves nothing existed at that name, so the object is this run's by construction. | the created object's identity, absolutely | nothing about the object *after* creation |
| **B2** | **Descriptor-bound effect.** Obtain a descriptor for the final object first, verify it, then issue the effect on the **descriptor** — `fchown`, `fchmod`, `fsync`, `ftruncate`, `pwrite`, `ioctl(FS_IOC_SETFLAGS)`, `execveat(…, AT_EMPTY_PATH)`. | the object the effect lands on, exactly | the interval between the lookup that produced the descriptor and the `fstat` that verified it |
| **B3** | **Exclusion.** Issue the effect only while no experimental process exists, verified by the three quiescence observations of §1.6. | who else can be writing during the effect | a host administrator **[A]**; and it is an operational premise, not a technical one |

**Every lookup interval that B1 and B2 cannot close is closed by B3 or the effect
is refused.** §1.4 applies that rule row by row.

### 1.3 Descriptor custody — the complete table, with modes

**This section is the answer to PR-20260911-R2-2's first half.** r2 opened the
whole chain `O_PATH` and then required `fsync` on two of those descriptors. The
correction is not a flag change in one row: it is that **a descriptor's mode is
part of its contract**, so every descriptor is specified below with its open
flags, owner, lifetime, permitted uses and transfer policy.

#### 1.3.1 What an `O_PATH` descriptor may and may not do **[D]**

`open(2)` lists the permitted operations on a descriptor obtained with `O_PATH`:
`close`, `fchdir` on a directory, `fstat`, `fstatfs`, duplication, descriptor-flag
get/set, `F_GETFL`, passing as the `dirfd` argument of the `*at()` calls, and
passing over a Unix socket with `SCM_RIGHTS`. It states equally explicitly that
`read`, `write`, `fchmod`, `fchown`, `ioctl` and `mmap` **fail with `EBADF`**.

**`fsync` is not in the permitted list.** `fsync(2)` describes an operation on an
open file description that transfers modified data to the storage device; an
`O_PATH` description carries no such access. So `fsync(bin_fd)` and
`fsync(pgconf_fd)` as r2 specified them are not operations that can succeed, and
the whole of r2's durability story rested on two calls that cannot run.

#### 1.3.2 Two descriptors per directory, and how the second one is bound

Every directory this design touches is held **twice**, for two different jobs.

| | **Traversal descriptor** | **Synchronizable descriptor** |
|---|---|---|
| Flags | `O_PATH\|O_NOFOLLOW\|O_DIRECTORY` | `O_RDONLY\|O_NOFOLLOW\|O_DIRECTORY` |
| Obtained | once, at the directory's exclusive creation, or from the provisioned root's recorded identity | by `openat(<this directory's **traversal** descriptor of its parent>, name, O_RDONLY\|O_NOFOLLOW\|O_DIRECTORY)` |
| Permitted uses | **only** as the `dirfd` argument of `openat`, `mkdirat`, `unlinkat`, `renameat2`, `fstatat`, `execveat`; and `fstat` of itself | **only** `fsync`, and `fstat` of itself |
| Not permitted | read, write, `fsync`, `ioctl` **[D]** | use as a `dirfd`, so that a reader can tell the two apart by their use sites |
| Lifetime | the whole run, held by the executor | the whole run, held by the executor |
| Transfer | inheritance across `fork`/`execve` with `FD_CLOEXEC` cleared, and by nothing else | **never transferred.** No experimental step receives a synchronizable descriptor |

**How the second open avoids reintroducing an unchecked pathname lookup — the
re-review's explicit question.** Three properties together, and all three are
needed:

1. **it resolves one component, relative to a descriptor already held.** There is
   no lookup from `/`, and the prefix is bound by the traversal descriptor of the
   parent, exactly as `unlink(2)` describes the prefix being bound **[D]**;
2. **its result is compared, not assumed.** The chain recorded
   `(st_dev, st_ino)` for the entry when the traversal descriptor was opened. The
   new descriptor is `fstat`ed and compared with that pair. A mismatch **refuses
   the publication**; it does not retry and does not fall back to a path; and
3. **the residual interval is named and covered.** Between the `openat` and the
   `fstat` the entry could have been replaced, in which case the `fstat` reports
   the replacement and the effect refuses. That is detection, and the interval
   itself is covered by **B3** for directories an experimental identity can
   reach, and by the administrator-only premise **[A]** for `/var/lib` and
   `/etc/postgresql/16/main`, which no experimental identity may traverse.

**[M]** `test_r2_proposal_models.py::test_a_synchronizable_descriptor_is_bound_by_comparison_not_by_pathname`
injects a substitution between the two opens and asserts the refusal;
`…::test_a_separate_o_rdonly_descriptor_is_the_synchronizable_one` asserts the
two descriptors refer to one object in two modes; and
`…::test_fsync_on_an_o_path_descriptor_is_refused` is the invalid-operation
control.

#### 1.3.3 The complete descriptor inventory

`R = /opt/freedom-blades/evidence/<run>`. **Owner** is the executor in every row:
one long-lived privileged process per reservation, created before the first
effect, not exiting until cleanup has classified §2.13.2b state.

| # | Descriptor | Object | Flags | Lifetime | Permitted uses | Transfer |
|---|---|---|---|---|---|---|
| D1 | `evidence_pathfd` | `/opt/freedom-blades/evidence` | `O_PATH\|O_NOFOLLOW\|O_DIRECTORY` | run | `dirfd` for C1's `mkdirat` and for the by-name `fstatat` of §1.4.1 | none |
| D2 | `root_pathfd` | `R` | `O_PATH\|O_NOFOLLOW\|O_DIRECTORY` | run | `dirfd` for P1 | none |
| D3 | `root_syncfd` | `R` | `O_RDONLY\|O_NOFOLLOW\|O_DIRECTORY` | run | `fsync` after P1 | never |
| D4 | `bin_pathfd`, `before_pathfd`, `journal_pathfd`, `probe_pathfd`, `probe_ro_pathfd` | the five directories P1 creates | `O_PATH\|O_NOFOLLOW\|O_DIRECTORY` | run | `dirfd` for the effects under each | `bin_pathfd` and `journal_pathfd` are inherited by steps whose case enumerates them |
| D5 | `bin_syncfd`, `journal_syncfd` | the same two directories | `O_RDONLY\|O_NOFOLLOW\|O_DIRECTORY` | run | `fsync` after P2 and after L3's removals | never |
| D6 | `payload_fd` | the installed case program | `O_PATH\|O_NOFOLLOW` | run | `execveat(…, AT_EMPTY_PATH)`; `fstat` | inherited by X1 |
| D7 | `interp_fd` | the documented Python 3.12 interpreter | `O_PATH\|O_NOFOLLOW` | run | `execveat(…, AT_EMPTY_PATH)`; `fstat` | inherited by X1 |
| D8 | `flag_fd` | one file under `R/journal`, per effect | `O_RDONLY\|O_NOFOLLOW` | **one effect only**, closed immediately after | `fstat`; `ioctl(FS_IOC_SETFLAGS/GETFLAGS)` | never |
| D9 | `pgconf_pathfd` | `/etc/postgresql/16/main` | `O_PATH\|O_NOFOLLOW\|O_DIRECTORY` | run | `dirfd` for M1 and L1 | never |
| D10 | `pgconf_syncfd` | the same directory | `O_RDONLY\|O_NOFOLLOW\|O_DIRECTORY` | run | `fsync` after M1's and L1's renames | never |
| D11 | `recovery_pathfd` | `/var/lib/freedom-blades/recovery` | `O_PATH\|O_NOFOLLOW\|O_DIRECTORY` | run | `dirfd` for the run directory's `mkdirat` | never |
| D12 | `recovery_syncfd` | the same directory | `O_RDONLY\|O_NOFOLLOW\|O_DIRECTORY` | run | `fsync` after the run directory is created — **the barrier r2 omitted** | never |
| D13 | `runstore_pathfd` | `/var/lib/freedom-blades/recovery/<run-id>` | `O_PATH\|O_NOFOLLOW\|O_DIRECTORY` | run | `dirfd` for the copy and the record | never |
| D14 | `runstore_syncfd` | the same directory | `O_RDONLY\|O_NOFOLLOW\|O_DIRECTORY` | run | `fsync` after each rename in the store | never |
| D15 | `capture_fd` | one configuration file being captured | `O_RDONLY\|O_NOFOLLOW` | one capture | `read`; `fstat` | never |
| D16 | `write_fd` | one temporary being written | `O_CREAT\|O_EXCL\|O_WRONLY\|O_NOFOLLOW` | one write | `write`; `fchown`; `fchmod`; `fsync` | never |
| D17 | `lifecycle_pathfd`, `lifecycle_syncfd` | `/var/lib/freedom-blades/laboratory` | as D11/D12 | run | the lifecycle record's writes and its two barriers (§5.4, §5.8) | never |
| D18 | `lock_fd` | `/run/freedom-blades/laboratory.lock` | `O_RDWR`, **no `O_CREAT`, no `O_EXCL`** | the participant's whole run | `flock` | never |

**The transfer policy, stated once.** Descriptors move by **inheritance across
`fork`/`execve` and by nothing else**. The executor clears `FD_CLOEXEC` on
exactly the descriptors a given step needs, in a declared order starting at
descriptor 3, and passes the step a table naming each one. The case program's
`DIRFD` argument kind is an index into that table and into nothing else. A step
that needs a descriptor it was not given **refuses**; it does not open a path to
obtain one. **No synchronizable descriptor is ever transferred**, which is a
narrowing r2 did not state: a step that cannot `fsync` cannot make a durability
claim the executor did not make.

`SCM_RIGHTS` over a Unix socket is documented **[D]** and is *not* proposed: it
would require a socket, a protocol and a second trust decision about who may
connect to it, and inheritance already covers a parent-launched child.

**Custody across privilege transitions.** A descriptor survives `execve` when
`FD_CLOEXEC` is clear, and it survives a `setpriv`/`capsh` credential drop
because the drop changes credentials, not the descriptor table. Two consequences:

* the dropped identity **cannot re-open by path** what it was given by
  descriptor, if the path's permissions forbid it; and
* the dropped identity **can use the descriptor it was given**. A descriptor
  handed to an experimental identity is therefore a capability granted to that
  identity for the lifetime of that process **[P]**.

So the executor hands an experimental step only the descriptors whose reach is
intended for it, each case names them among its writable objects (revision 1
§4.3, retained), and a case whose descriptor set is not enumerated is not
admissible.

### 1.4 The operation inventory

For each effect: the exact object or bytes, the operation that resolves it,
whose descriptor and for how long, the prerequisite, and what enforces that
prerequisite **immediately before** the effect. `Protection` names B1/B2/B3.

The first column's identifiers are revision 1's, so all three documents can be
read side by side.

#### 1.4.1 Creation

| # | Effect | Object / bytes | Resolution | Descriptor | Prerequisite | Enforcement immediately before the effect | Protection |
|---|---|---|---|---|---|---|---|
| C1 | create `R` | the directory `R` | `mkdirat(D1, "<run>", 0700)`, exclusive | D2 opened immediately after; held for the run | `R` does not exist | `EEXIST` is the refusal. Success **is** the ownership proof | **B1** |
| C2 | record `R`'s identity | `R` | `fstat(D2)` | the same descriptor | C1 succeeded | the pair `(st_dev, st_ino)` is recorded once and every later `openat` is relative to this descriptor | **B1** |

**What C2 is not.** It is not a later detector of `R`'s replacement. Re-`fstat`ing
D2 later compares the descriptor with itself and always agrees — §1.1(1).
Replacement of the *pathname* `R` is detected only by
`fstatat(D1, "<run>", AT_SYMLINK_NOFOLLOW)` against the recorded pair, which is a
different call on a different descriptor, and even that is detection rather than
prevention. `/opt/freedom-blades/evidence` is root-only **[A]**, so the exposure
is administrator-only.

#### 1.4.2 Provisioning

| # | Effect | Object / bytes | Resolution | Descriptor | Prerequisite | Enforcement immediately before the effect | Protection |
|---|---|---|---|---|---|---|---|
| P1 | create `R/bin`, `R/before`, `R/journal`, `R/probe`, `R/probe-ro` | five directories | `mkdirat(D2, name, mode)`, exclusive, one call per name — **replacing `install -d <path>`** | D4 opened on each success; held for the run | D2 is the descriptor C1 created | exclusive creation: an existing entry is `EEXIST` and refuses | **B1** |
| P1b | **make the five entries durable** | `R`'s entries | `fsync(D3)` — **an `O_RDONLY` descriptor, obtained and bound per §1.3.2** | D3, held for the run | P1 succeeded for all five | a failure here refuses P2 and everything after it | **B2** |
| P2 | install the reviewed case program | the reviewed bytes, held in memory | `openat(D4.bin, ".case-program.tmp", O_CREAT\|O_EXCL\|O_WRONLY\|O_NOFOLLOW, 0500)`; `write` the held buffer; `fchown`; `fchmod 0555`; **`fsync(D16)`**; `renameat2(D4.bin, ".case-program.tmp", D4.bin, "case-program", RENAME_NOREPLACE)`; **`fsync(D5.bin)`** — **replacing `install -m 0555 src dst`** | D4.bin and D5.bin for the run; D16 for the write; D6 opened on the result and held | the source bytes digest to `materialization.REVIEWED_DIGESTS` | the bytes written are the bytes digested, from one buffer. `O_EXCL` proves the temporary name was free; `RENAME_NOREPLACE` proves the final name was free **[D]** | **B1 + B2** |
| P3 | create the four disposable identities | `/etc/passwd`, `/etc/group` | by name, through `useradd`/`groupadd` | — | the names are not existing production identities | `targets.validate_account_name` against the approved target | *name-resolved by nature*; see below |
| P4 | set `+i` on the seal, `+a` on the journal | one file each under `R/journal` | `openat(D4.journal, name, O_RDONLY\|O_NOFOLLOW)` → D8; `fstat`; compare with the recorded pair; `ioctl(D8, FS_IOC_SETFLAGS)` — **replacing `chattr +i <path>`** | D8 for this effect only; D4.journal for the run | the file is the object the creating step recorded | the flag change lands on the inode the descriptor holds, so a replacement of the *name* after the check cannot receive the flag | **B2 + B3** |

**The two corrections in this table.** `P1b` is new: r2 had no directory barrier
after provisioning at all. And P2's two `fsync` calls are now on **D16** (the
write descriptor, `O_WRONLY`) and **D5.bin** (the synchronizable directory
descriptor, `O_RDONLY`). r2 required the second on `bin_fd`, which it had defined
`O_PATH`, and that call cannot succeed **[D]**.

**P2's real replacement of `install`.** Revision 1 named four new verbs and left
`install` in place; the review's objection was that four verb names are not an
implementation contract for the effects `install` performs. The replacement above
is stated as the sequence of syscalls, and it removes `/usr/bin/install` from the
provisioning path entirely for `R/bin`. §2.4 replaces it in restoration too.

**P3 cannot be descriptor-bound and says so.** `useradd` resolves `/etc/passwd`
by pathname inside a tool this design does not own. The object is root-only and
the exposure is administrator-only **[A]**. It is listed as uncovered rather than
described as protected.

**P4's residual interval.** Between `openat` and `fstat` the entry could have been
replaced; the `fstat` then reports the replacement's identity and the effect is
refused. Between `fstat` and `ioctl` nothing can move the descriptor. So P4's
uncovered interval is the lookup itself, and B3 covers it: `R/journal` is
`0750 root:freedomjournal` and the disposable `freedomjournal` members are
experimental identities, so this effect is issued **only inside a verified
quiescence window** (§1.6). If quiescence cannot be established, P4 refuses and
every dependent effect refuses with it (§1.7).

#### 1.4.3 Capture

Specified in §2, which is the independent-recovery contract, because
PR-20260911-2 and PR-20260911-R2-2 are both about the property a table row cannot
carry.

#### 1.4.4 Materialization and experiments

| # | Effect | Object / bytes | Resolution | Descriptor | Prerequisite | Enforcement immediately before the effect | Protection |
|---|---|---|---|---|---|---|---|
| M1 | write the reviewed `pg_hba.conf`/`pg_ident.conf` | reviewed bytes, held in memory | `openat(D9, "<name>.tmp", O_CREAT\|O_EXCL\|O_WRONLY, 0640)` → D16; write; `fchown`; **`fsync(D16)`**; `renameat2(D9, tmp, D9, name, 0)`; **`fsync(D10)`** | D9 traversal and **D10 synchronizable**, both held for the run | **§2.3's publication reported `mutation_permitted`** — every barrier crossed | the publication's barrier set is re-checked; a missing barrier refuses **before** M1 | **B2**; destination parent is root-only **[A]** |
| M2 | reload and observe the mapping in force | server state | — | — | M1 succeeded | post-reload control connection | — |
| X1…Xn | run the reviewed case program under `E1 … E8` | the payload inode P2 installed; subjects under `R` | `execveat(D7, "", ["python3.12", "-I", "-S", "/proc/self/fd/<D6>", …], envp, AT_EMPTY_PATH)` | D6 and D7 held by the executor for the run and inherited by the step | the interpreter matches the 2026-09-06 Option B preflight on path, version and executable SHA-256; D6's `fstat` matches P2's record | both the interpreter and the script are reached through descriptors, so a replacement of either **pathname** between preflight and execution cannot be executed | **B2** |

**The correction in this table.** M1's second `fsync` is on **D10**, not on
`pgconf_fd`. r2 defined `pgconf_fd` as `O_PATH` and then required `fsync` on it
in both M1 and restoration; neither call can succeed **[D]**.

**Why X1's payload use is an effect on a retained object.** Two documented facts
make it work. `execveat(2)` executes the file the descriptor refers to when
`pathname` is empty and `AT_EMPTY_PATH` is set, and the descriptor may be one
obtained with `O_PATH` **[D]**. And `/proc/self/fd/N` is a symbolic link to the
object the descriptor refers to, so opening it reaches that object rather than
re-resolving the original path **[D]**.

Two caveats, both documented and both load-bearing:

* opening `/proc/self/fd/N` is a **new open subject to a fresh permission check
  on the underlying inode** — `proc_pid_fd(5)` gives the worked example in which
  an unprivileged process is refused **[D]**. The reviewed payload is `0555`
  root-owned, so the check passes for every disposable identity **[P]**, and any
  case that installs a payload with narrower modes must state that in its own
  five facts; and
* `execveat(2)` **BUGS** notes that `FD_CLOEXEC` cannot be set on the descriptor
  passed with `AT_EMPTY_PATH`, so that descriptor leaks into the executed program
  **[D]**. For us the leaked descriptor is the interpreter's own executable, read
  only; it is named in the step's descriptor table rather than left unremarked.

**Why the shebang is not used.** The 2026-09-06 Option B ruling rejects the
shebang and on-target compilation alternatives. `execveat` on the *interpreter*
with the script supplied through `/proc/self/fd/N` keeps the ruling's contract —
the named documented interpreter, `-I -S`, the exact reviewed vectors — while
binding both objects.

**What X1 still does not bind.** In-place content mutation of a file whose inode
is unchanged. A descriptor is a reference to an inode, not to its bytes. This
exposure is separate, it stays separate, and §1.7 refuses dependent effects that
would consume such bytes without a digest of the bytes actually read.

#### 1.4.5 Cleanup — and what the post-check actually establishes

| # | Effect | Object / bytes | Resolution | Descriptor | Prerequisite | Enforcement immediately before the effect | Protection |
|---|---|---|---|---|---|---|---|
| L1 | restore the pre-change configuration | the bytes §2's record binds | §2.4's verify-and-write over a held buffer | D9 traversal, **D10 synchronizable** | §2's record verifies against the retained copy | the buffer digested is the buffer written; there is no second pathname read between check and write | **B2** |
| L2 | reload and verify restoration in force | server state | — | — | L1 **durable**, not merely renamed | post-reload observation; unverified ⇒ S-B | — |
| L3 | clear flags, then remove this run's objects, one named object at a time | objects under `R` | `openat(parent, name, O_RDONLY\|O_NOFOLLOW)` → D8; `fstat` against the recorded pair; `ioctl(FS_IOC_SETFLAGS)` to clear; then `unlinkat(parent, name, 0)` or `AT_REMOVEDIR`; then `fstatat(parent, name, AT_SYMLINK_NOFOLLOW)` | each parent's traversal descriptor, held for the run; D5 for the barrier after | each object was created by this run, **and quiescence holds** | flag clearing is **B2**. The removal is **not bindable** — see below | **B2** for the flag; **B3** for the removal |
| L4 | classify §2.13.2b state | — | — | — | L1–L3 attempted | `cleanup.classify_cleanup` | — |

**L3 is the honest row, and PR-20260911-R2-3 found r2 still dishonest about it.**
There is no `funlink`. `unlinkat` resolves its final component at the time of the
call **[D]**, and no flag on it binds that component to a previously observed
inode. So removal cannot be made inode-bound by any syscall available here, and
this contract does not claim otherwise.

What it proposes instead, in order, **with prevention and evidence kept apart**:

1. **Prevention — and it is the only prevention.** L3 runs only inside a verified
   quiescence window (§1.6). No experimental process exists, so the only writers
   to the parent are the executor and an administrator **[A]**. Quiescence is a
   **prerequisite of name-based removal**, not a detector of its failure.
2. **Pre-check — the one genuine detection.** `openat` + `fstat` against the
   recorded pair. A mismatch refuses **before** the removal, names the recorded
   identity and the one found, and the run reports a detected substitution.
3. **Removal.** `unlinkat` removes whatever `name` resolves to at the moment of
   the call.
4. **Post-check — an absence check, and nothing more.** `fstatat` on the same
   name. **It observes whether a name exists. It cannot establish which object
   the removal took, and it cannot report a replacement's identity**, because the
   object is gone and the name is all that is left to look at.

   The counterexample, which this revision states rather than denies: the
   pre-check succeeds for **A**; a writer renames A away and installs **B** at
   the name; `unlinkat` removes B; the post-check returns `ENOENT`. That is
   **byte-for-byte the observation a correct removal of A produces**. A still
   exists under its new name and the post-check never learns it.

   A post-check that finds the name *still resolving* is informative — something
   is there that should not be, and the run reaches **S-B**. A post-check
   returning `ENOENT` is **not evidence that the intended object was removed**.
5. **Refusal.** If quiescence cannot be established — unobserved, observed false,
   or incomplete — L3 does not run. The objects are reported as residue by
   absolute path, §2.13.2b state is **S-B**, the dependent work refuses with it,
   and **independent recovery is preserved** because §2's store is outside `R`
   and was published before the first mutation. The next invocation refuses,
   which is the existing accepted behaviour and is preferable to a removal issued
   into an unknown state.

**What this does not do, stated because r2's repair attempt reached for it.** It
does not invent a new isolation architecture. It does not claim that
discretionary access control constrains root: the trusted-administrator premise
is retained as an operational exclusion over **people**, exactly as the direction
states it. And an injected substitution in §9 demonstrates the check's
**detection limit**; it is not a passing safety invariant and is not a claim that
the violation occurs under valid premises.

**[M]** `test_r2_proposal_models.py::test_the_exact_counterexample_removes_b_and_leaves_a_alive`,
`…::test_the_post_check_cannot_tell_the_two_removals_apart`,
`…::test_a_substitution_before_the_pre_check_is_genuinely_detected`,
`…::test_unobserved_false_or_incomplete_quiescence_refuses_the_effect` and
`…::test_the_intended_removal_succeeds_under_the_declared_exclusion_premise`.

### 1.5 Which effects each finding's coverage claim actually rests on

| Row | Revision 1 claimed | This revision proposes | Residual |
|---|---|---|---|
| P1 | descriptor comparison | **B1**, exclusive `mkdirat`, plus P1b's directory barrier | none for creation; the barrier can fail and then refuses |
| P2 | descriptor comparison | **B1 + B2**, `O_EXCL` + held buffer + `RENAME_NOREPLACE` + two barriers on correctly-moded descriptors | in-place mutation of the source before the digest; §2.4's rule applies |
| P4 | descriptor comparison | **B2** with a real `O_RDONLY` descriptor, **B3** for the lookup | the lookup interval, covered by quiescence or refused |
| X1 | descriptor comparison | **B2** via `execveat` + `/proc/self/fd/N` | in-place content mutation of a stable inode |
| L3 | descriptor comparison | **B2** for the flag; **B3** for the removal; the pre-check detects, **the post-check does not** | the removal's final-component lookup, **not bindable**, and **not detectable after the fact** |

### 1.6 Quiescence — the three observations, and what they cost

Before any effect that relies on **B3**, three observations, none defaulting to
true and each with an explicit *not made* value:

1. every process the case started has exited — observed, not inferred from the
   parent's exit status;
2. every server-side transaction the case opened has settled. A `psql` client
   exiting says the client stopped waiting; and
3. no transient unit the case created is still active.

`reservation.ReleaseEvidence` carries the first two as `bool | None`, and after
the September 11 repair it carries the residue search as a `ResidueObservation`
with an explicit *not made* value, so *"not checked"* and *"checked and false"*
stay apart. `durability_model.Quiescence` carries all three plus the *observation
not made* case, and `remove_by_name` refuses on any of them.

**The cost, stated.** B3 serializes the run: no effect that depends on it may
overlap a case process. Cases that require concurrency keep it *inside* the case,
as revision 1 §4.3 already required, and the executor's B3-dependent effects sit
between cases and never during one.

### 1.7 Refusal, and what survives a refusal

| Situation | Behaviour | Where |
|---|---|---|
| An effect's object cannot be shown to be the one the prerequisite names | **refuse before the effect** | §1.4; **not implemented** |
| A synchronizable descriptor does not `fstat` to the recorded identity | refuse the publication; no mutation | §1.3.2; **not implemented**, modelled **[M]** |
| Quiescence cannot be established before a **B3** effect | refuse the effect and every dependent effect; report residue; state S-B; independent recovery preserved | §1.6; **not implemented**, modelled **[M]** |
| A substitution is detected **by the pre-check** | refuse the removal; report the recorded and found identities; state S-B | §1.4.5(2); **not implemented**, modelled **[M]** |
| A substitution occurs **after** the pre-check | **not detected.** The post-check's `ENOENT` is indistinguishable from success | §1.4.5(4); modelled as a **detection limit** **[M]** |
| A publication barrier fails | **refuse the configuration mutation entirely**; nothing to recover from | §2.3; **not implemented**, modelled **[M]** |
| A restoration rename succeeds and its directory barrier fails | **not reported as a durable restoration**; S-B | §2.4; **not implemented**, modelled **[M]** |
| Cleanup cannot complete | S-B, exit 3, residue named by absolute path, next invocation refuses | `cleanup.classify_cleanup` — implemented |
| Cleanup state uncertain | S-B, and the executor refuses the next run *more* firmly | `executor._refuse_when_blocked` — implemented |
| A pre-existing object is found where a subject would be created | preserve it, never remove it, report it as `preserved` | `CleanupOutcome.preserved` — implemented |
| Reservation release cannot establish its conditions | **quarantine**, durably; no takeover, no timeout | `reservation.release` — implemented |
| An unknown writer is on the host at admission | refuse and name it; never kill it, never disable it | `reservation.admit` — implemented |
| Admission with no verified predecessor release | refuse | `reservation.admit`, repaired 2026-09-11 — implemented |
| **A contradictory lifecycle record** | **refuse**, naming which two halves disagree | `reservation.validate_lifecycle`, repaired 2026-09-11 — **implemented**, §5.9 |
| An S-B run on residue alone | reports no named operator recovery — **LAB-1**, §8 | observed, reported, **not repaired** |

**Independent recovery survives every refusal above.** That is §2's requirement
and it is why §2 refuses the mutation rather than the cleanup when its basis is
absent: a refusal before the first mutation leaves nothing to recover from.

---

## 2. Independent recovery and durability — PR-20260911-2 and PR-20260911-R2-2

### 2.1 What the reviews established

Revision 1 §7 said that when `R` is unsafe the recovery basis is *"the operator's
own out-of-band copy"*, and cited `cleanup.RECOVERY_PROCEDURE` as its named
procedure. Neither holds:

* no operation in revision 1's inventory creates, verifies or durably retains
  that copy, and nothing makes it a prerequisite of the first mutation. An
  unprovided copy is not a safeguard; and
* `cleanup.RECOVERY_PROCEDURE` step 2 instructs recovery **from the captures
  under the disposable root's `before/` directory**
  (`tools/phase_5_0_evidence/cleanup.py:1278`). Its custody is exactly the
  custody in question, so it is not an independent procedure.

Revision 2 introduced the independent store and then **published it
non-durably**: its §2.3 synchronized the captures and the run directory, and
never synchronized the recovery parent. PR-20260911-R2-2 is that omission.
`fsync(2)` is explicit that a containing directory must be synchronized
separately for a new entry to be durable **[D]**, so after a power loss, restart
discovery by listing the recovery parent is not guaranteed to find the advertised
recovery basis.

### 2.2 The independent store

**Location.** `/var/lib/freedom-blades/recovery/<run-id>/`, and **not** under
`R`, not under `/opt/freedom-blades/evidence`, and not under any path an
experimental identity can write.

| Property | Value | Why |
|---|---|---|
| Parent `/var/lib/freedom-blades` | `root:root`, `0755` | outside `/run`, so it survives reboot; a restarted executor and a human both find it |
| `/var/lib/freedom-blades/recovery` | `root:root`, `0700` | no experimental identity may traverse it, so no case can reach a capture even by descriptor |
| `<run-id>/` | `root:root`, `0700` | one directory per run, named by run id, so `readdir` is the discovery mechanism |
| each capture file | `root:root`, `0400` | read-only to root; rewritten only by replacing the whole directory |
| each record file | `root:root`, `0400` | the binding between bytes and metadata |

**Owner.** root, through the executor. No disposable identity, no group, no
`freedomsheet`, no `freedomjournal`.

**This is a provisioning delta and it is not approved.** §7 states it exactly.

### 2.3 The complete durability dependency graph

**This is the section PR-20260911-R2-2 requires.** Every barrier, its subject,
its order and its failure disposition, for every publication the run performs.

#### 2.3.1 The rule, stated before the table

> **No first configuration mutation may occur until both the recoverable bytes
> and all the metadata needed to discover and verify them after a crash are
> durably published.**

Two halves, and r2 satisfied only the first. *Recoverable bytes* is the copy.
*Metadata needed to discover them* includes the run directory's **own entry in
the recovery parent**, because discovery is `readdir` of that parent and an entry
is durable only when its containing directory is synchronized **[D]**.

**What is not a barrier**, stated because r2 §2.3 step 7 reads like one:

* a read-back of the stored copy and a digest comparison. It establishes that the
  bytes written are the bytes captured, and **nothing** about whether either
  survives a power loss;
* a successful `rename`. It changes the namespace; it does not synchronize the
  directory the namespace entry lives in; and
* a successful `write`. Data reaches the page cache, not the device.

A sequence that performs any of these in place of a barrier has performed no
barrier.

#### 2.3.2 Installation and provisioning barriers

| Order | Barrier | Subject | Descriptor | Failure disposition |
|---|---|---|---|---|
| 1 | provisioning entries | `R`'s five subdirectories | **D3** `O_RDONLY` | refuse P2 and everything after; no mutation has occurred, so nothing to recover |
| 2 | payload data | the case-program temporary | **D16** `O_WRONLY` | refuse P2; remove the temporary; refuse the run |
| 3 | payload entry | `R/bin` | **D5.bin** `O_RDONLY` | refuse; the reviewed program is not established as installed |

#### 2.3.3 Capture publication barriers — the ordered graph

| Order | Barrier | Subject | Descriptor | Why nothing later may proceed without it | Failure disposition |
|---|---|---|---|---|---|
| 1 | **`recovery-parent-entry`** | `/var/lib/freedom-blades/recovery` | **D12** `O_RDONLY` | the `<run-id>` directory's own entry lives here. Without it, `readdir` of the recovery parent after a power loss need not list the run at all, and the advertised recovery basis is undiscoverable however carefully its contents were written. **This is the barrier r2 omitted** | refuse; no mutation; nothing to recover from |
| 2 | `copy-data` | the captured copy | **D16** `O_WRONLY` | the captured bytes are not durable until the file itself is synchronized | refuse; no mutation |
| 3 | `copy-entry` | `<run-id>` | **D14** `O_RDONLY` | the copy's name is an entry in `<run-id>` | refuse; no mutation |
| 4 | `record-data` | the recovery record | **D16** `O_WRONLY` | a copy whose record did not survive is bytes nobody can verify or place | refuse; no mutation |
| 5 | `record-entry` | `<run-id>` | **D14** `O_RDONLY` | the record's name is an entry in `<run-id>` | refuse; no mutation |

The ordered sequence, with every failure refusing **before M1**:

1. open **D11** (`O_PATH`) and **D12** (`O_RDONLY`) on the recovery parent, D12
   bound by comparison per §1.3.2;
2. `mkdirat(D11, "<run-id>", 0700)`, exclusive. `EEXIST` refuses: a run id that
   already has a directory is a run id that was used;
3. **barrier 1** — `fsync(D12)`. Placed here, the earliest safe point, so that
   even a crash mid-capture leaves a *discoverable* run directory rather than
   nothing;
4. open **D13** and **D14** on `<run-id>`, D14 bound by comparison;
5. `openat(D9, name, O_RDONLY|O_NOFOLLOW)` → **D15**; `fstat` → record
   `st_dev`, `st_ino`, `st_size`, `st_mtim`, `st_mode`, `st_uid`, `st_gid`;
6. read to EOF into **one held buffer**. A short read, a read error, or a size
   beyond the reviewed bound (`MAX_MATERIALIZED_BYTES`) **refuses**; it is not
   retried, because a retry reads a possibly different file;
7. `fstat` D15 again and refuse unless `st_size` and `st_mtim` are unchanged.
   This is a consistency check on the read, not a substitution check — the
   descriptor cannot have moved;
8. `digest = SHA-256(buffer)`, computed over **the buffer**, never over a re-read
   of the pathname. This is PR-20260909-R2-2's requirement and it stays;
9. write the copy: `openat(D13, "<name>.tmp", O_CREAT|O_EXCL|O_WRONLY|O_NOFOLLOW,
   0400)` → D16; write; **barrier 2**; `renameat2(D13, tmp, D13, "<name>",
   RENAME_NOREPLACE)`; **barrier 3**;
10. write the record the same way: destination path, source identity from (5),
    `digest`, byte length, run id, reservation id, the capture time and the
    capturing identity; **barrier 4**; rename; **barrier 5**;
11. re-read the stored copy from the store and digest it. It must equal `digest`.
    **This is a verification, not a barrier**; and
12. only now is M1 permitted, and M1's own precondition is that the publication
    reported every barrier in §2.3.3 crossed.

**Digest/metadata binding.** The record names the digest **and** the source's
`(st_dev, st_ino, st_size, st_mtim)` **and** the destination pathname. A
restoration reads all three: a copy whose digest matches but whose record names a
different destination is not restored anywhere.

**[M]** `test_r2_proposal_models.py::test_the_positive_sequence_crosses_every_barrier_and_permits_the_mutation`,
`…::test_failure_at_any_barrier_prevents_the_first_configuration_mutation`
(parametrized over all five),
`…::test_a_crash_after_a_successful_publication_leaves_a_usable_recovery_basis`,
`…::test_the_revision_2_sequence_fails_the_corrected_property` and
`…::test_syncing_the_childs_contents_is_not_the_parents_entry_barrier`.

### 2.4 Restore, and its failure modes

| Order | Barrier | Subject | Descriptor | Failure disposition |
|---|---|---|---|---|
| 1 | `restore-data` | each restoration temporary | **D16** `O_WRONLY` | destination untouched; S-B; retry from the store |
| 2 | `restore-entry` | `/etc/postgresql/16/main` | **D10** `O_RDONLY` | **the rename is visible and not durable.** S-B; the restoration is **not reported durable** |

1. Read the stored copy into **one held buffer**; digest that buffer; compare
   with the record. A mismatch refuses and the run reaches **S-B**.
2. `openat(D9, "<name>.restore.tmp", O_CREAT|O_EXCL|O_WRONLY, 0640)` → D16;
   write **that buffer**; `fchown` to `postgres:postgres`; `fchmod 0640`;
   **barrier 1**.
3. Repeat (1)–(2) for every captured file: **all temporaries written and
   synchronized before any rename**.
4. Issue the renames in a fixed order recorded in the plan:
   `renameat2(D9, "<name>.restore.tmp", D9, "<name>", 0)`.
5. **Barrier 2** — `fsync(D10)`, **after the last rename**.
6. One reload, after the barrier. Then the post-reload verification of revision 1
   §7, unchanged: an ordinary local connection as `postgres` still succeeds, and
   a connection as the temporary OS identity asking for the temporary role is
   refused.

**Failure after a rename and before its directory sync — the case the re-review
names.** The destination's *name* now resolves to the restored bytes and the
*durable* namespace still holds the pre-restoration entry. A power loss at that
instant returns the destination to the mutated configuration. **A restoration is
therefore never reported durable from a rename alone**, `RestorationOutcome`
carries `renamed` and `durable` as two separate fields, and L2's reload
verification has `durable` as its prerequisite.

**Partial writes and interruption.** The destination is never half-written: the
bytes go to a temporary and the rename is atomic. An interruption leaves a
`.restore.tmp`, which is detected on restart by `readdir` of the destination
directory, reported, and removed before a retry. An interruption between two
renames leaves a mixed configuration, which is why the verification in (6) is a
separate observation and why failing it is **S-B** rather than a retry.

**Destination custody.** `/etc/postgresql/16/main` is root-only, so the
destination's exposure is to a host administrator rather than to an experimental
identity **[A]**. That is materially smaller and it is not zero, and it is
recorded as such rather than described as proved.

**[M]** `test_r2_proposal_models.py::test_a_complete_restoration_is_durable_and_says_so`,
`…::test_a_rename_without_its_directory_barrier_is_not_a_durable_restoration`,
`…::test_a_restoration_interrupted_before_its_rename_leaves_the_destination_alone`,
`…::test_a_multi_file_restoration_interrupted_between_renames_is_mixed` and
`…::test_a_record_naming_another_destination_restores_nowhere`.

### 2.5 Restart, retention and disposal

**Restart discovery, without the executor's memory.** A restarted executor, or a
human, lists `/var/lib/freedom-blades/recovery/` and finds one directory per run.
Each directory's record names the destination, the digest and the run. No index
file is needed and none is proposed, because an index is a second thing that can
be lost or disagree. **This is exactly why barrier 1 of §2.3.3 exists**: the
listing is the discovery mechanism, and an entry the parent never synchronized is
not in the listing.

**If `R` is replaced or unavailable.** Recovery reads only
`/var/lib/freedom-blades/recovery/<run-id>/`. It does not read `R/before`, it
does not require `R` to exist, and it does not require the executor to be alive.
`R/before` may be retained for evidence, but it is **not** a recovery basis and
the revised procedure in §8.2 stops calling it one.

**Retention.** A run's recovery directory is retained until **both** the
post-reload verification of §2.4(6) passed **and** `reservation.release` returned
`RELEASED`. A quarantined run's directory is never removed automatically.

**Disposal.** An explicit operator step, after the two conditions above, naming
the run id. It is not a command this design offers, for the same reason §2.13.2b
withdrew the automatic clean.

**And if the basis cannot be established:** M1 does not run. No configuration
mutation is issued, so no recovery is needed.

---

## 3. Source custody

Unchanged from revisions 1 and 2 except where §1 replaces a mechanism:

* the reviewed case program is installed `0555` root-owned into `R/bin` by
  §1.4.2 P2, from a held buffer, and used by descriptor (§1.4.4 X1);
* the interpreter is the documented Python 3.12 path, validated by preflight on
  path, version and executable SHA-256 (the 2026-09-06 Option B ruling), and now
  also **executed by descriptor** rather than by path;
* **staged-source substitution is not reintroduced.** The earlier proposal to
  stage sources into a writable location and install from there is withdrawn and
  stays withdrawn; and
* the review manifest pins the covered sources by SHA-256, and every generated
  artifact is review input until explicitly approved for execution.

**A held root descriptor still does not protect every descendant.** `open(R,
O_PATH)` names `R`; each subsequent component is resolved afresh. §1.3's chain
resolves each component **once** and holds it, which is a different thing from
resolving it repeatedly — and §1.4's residual columns say where even that is not
enough.

---

## 4. Test identities

Unchanged from revision 1 §4, with one addition from §1.3: **a descriptor handed
to an experimental step is part of that case's writable-object accounting.** A
case whose five facts do not enumerate the descriptors it receives is not
admissible, for the same reason a case with an unnamed writable path is not. **No
synchronizable descriptor is ever handed to a case**, so no case can make a
durability claim.

`E7` remains behind ten unconfirmed target facts and the executor's gate 4
refuses while any is unconfirmed. **This pass populates none of them.**

---

## 5. Cooperative lock and lifecycle storage — PR-20260911-6 and PR-20260911-R2-4

### 5.1 What the reviews established

Revision 1 §9.2(c) proposed an adapter that creates the lock with
`O_CREAT|O_EXCL` and unlinks it on release, in `/run/freedom-blades` described as
root-owned `0755`, and called the adapter unprivileged. Three things are wrong:

* ordinary participants cannot create or unlink an entry in a root-owned `0755`
  directory, so the **normal successful path does not exist**;
* precreating the lock does not rescue the protocol: `O_CREAT|O_EXCL` returns
  `EEXIST` while that entry exists **[D]**, so every participant refuses; and
* the stated fallback was refusal, which means the proposal had refusal paths and
  no success path at all.

**The O_EXCL protocol is withdrawn.** Revision 2 replaced it with a persistent
provisioned lock inode plus a separately protected lifecycle record, and
PR-20260911-R2-4 then found **that** protocol incomplete in two ways:

* §5.6–§5.7 gave ordinary participants a **denylist** — refuse on RUNNING,
  RECOVERING and QUARANTINED, otherwise proceed — which omits **ADMITTED**,
  despite the decision API classifying ADMITTED as an active predecessor. A crash
  after ADMITTED is persisted and before RUNNING is published leaves a free lock
  and exactly that omitted state; and
* the record being absent always refuses, correctly, while §7's provisioning list
  created only a directory and **never initialized a verified-first-use record**.
  The documented fresh-install path could not reach its successful control.

§5.6 through §5.8 are the corrections.

### 5.2 The participants and their real identities

All seven run on `oracle-test` as the OS user `ubuntu` **[A]**, which holds
passwordless `sudo` per the disposable-server profile. Two consequences decide
the design:

* as `ubuntu`, a participant is an **ordinary user** for file permissions, so the
  lock must be reachable without privilege; and
* `ubuntu` *could* obtain root through `sudo`. The design does not use that for
  the lock, because a lock every participant takes as root is a lock whose
  ordinary operation requires privilege escalation, and because `sudo` in a test
  runner is a permission this project should not normalize.

| # | Participant | Identity **[A]** | Holds the lock | Writes the lifecycle record |
|---|---|---|---|---|
| 1 | `tests/test_*.py` (bot suite) | `ubuntu` | for the whole serial run | no |
| 2 | `tests/web` (web suite) | `ubuntu` | for the whole serial run | no |
| 3 | `foundry-module/tests` (`node --test`) | `ubuntu` | for the whole run | no |
| 4 | §3.2 synchronization | `ubuntu` | from before `rsync` until the tree is consistent | no |
| 5 | §3.5 dependency updates | `ubuntu` | for the whole `uv pip install` | no |
| 6 | §4 environment reset | `ubuntu` | for the whole reset | no; **refuses while a quarantine record exists** |
| 7 | harness CLI | `ubuntu`, escalating to root for effects | for the reservation, across provisioning, execution, capture, restoration and cleanup | **yes**, as root |

**The asymmetry is the design.** Six participants only need to *serialize*. One
participant creates durable lifecycle state. So the lock is group-writable and
the record is root-written and group-readable, and neither object does the
other's job.

**What the asymmetry is not.** It is **not** a licence for six participants to
read the record more loosely than the seventh. §5.6 applies one allowlist to all
seven, and that is R2-4's requirement.

### 5.3 The lock — one persistent provisioned inode

| | Value |
|---|---|
| Path | `/run/freedom-blades/laboratory.lock` |
| Created by | `systemd-tmpfiles`, at boot, from a provisioned fragment — **not** by any participant |
| Directory | `/run/freedom-blades`, `root:freedomlab`, `0750` |
| File | `root:freedomlab`, `0660`, **never unlinked** |
| Group | new system group `freedomlab`, with `ubuntu` as a member |
| Taken by | `open(path, O_RDWR)` → **D18** — **no `O_CREAT`, no `O_EXCL`** — then `flock(D18, LOCK_EX\|LOCK_NB)` |
| Released by | `flock(D18, LOCK_UN)` and `close(D18)`, or by process exit |
| If the file is absent | **refuse.** An absent lock means the host was not provisioned, and creating it is a provisioning act, not a participant's |

**Why `flock` and not `O_EXCL` [D].** `flock(2)` states that locks are associated
with the **open file description**, that duplicates created by `fork` or `dup`
refer to the same lock, and that the lock is released by an explicit `LOCK_UN` on
any of them or when all are closed. So:

* a crashed holder's lock is released by the kernel when its descriptors close.
  **That is a feature here and it is also exactly why the lock cannot be the
  reservation**: see §5.5; and
* the file is never created and never removed by a participant, so the
  permissions a participant needs are `r`+`w` on an existing file and `x` on the
  directory — which `0750 root:freedomlab` with `ubuntu` in `freedomlab`
  provides **[P]**.

**Why `/run` needs `systemd-tmpfiles`.** `/run` is a tmpfs and does not survive
reboot **[A]**, so a one-off `mkdir` would silently stop existing. A tmpfiles
fragment re-creates the directory and the file at every boot with the stated
owner and mode. It is a provisioning artifact and §7 lists it.

### 5.4 The lifecycle record — separately protected, and durable

| | Value |
|---|---|
| Path | `/var/lib/freedom-blades/laboratory/lifecycle.json` |
| Directory | `root:freedomlab`, `0750` |
| File | `root:freedomlab`, `0640` |
| Written by | the harness CLI, as root, and by nothing else |
| Read by | all seven participants, as `ubuntu`, through group read |
| Descriptors | **D17**: `lifecycle_pathfd` `O_PATH` for the `*at()` calls, `lifecycle_syncfd` `O_RDONLY` for the two barriers. Bound by comparison per §1.3.2 |
| Not in `/run` | because it must survive reboot: a record that vanished on reboot would make every crashed run look like a first use |

Its content and ordering are `reservation.DURABLE_RECORD_ORDERING`, implemented
in the decision half on 2026-09-11 and reproduced here as the storage contract,
**with each item's two barriers named**:

1. the reservation record reaches durable storage — written, its **bytes**
   synchronized on the write descriptor, renamed, and its **entry** synchronized
   on `lifecycle_syncfd` — carrying `ADMITTED` **before the first effect of any
   kind**;
2. `RUNNING` is published the same way, both barriers, before the first
   mutation-bearing step;
3. a quarantine record is an **addition** on any failure path, never a
   precondition. A crash before it can be written leaves `RUNNING`, which refuses
   every successor. **Absence of a quarantine record is never evidence that a
   predecessor ended;**
4. a release record is published only after `release()` returns `RELEASED`, and
   it names the reservation, host and target it is a release of; and
5. nothing deletes or rewrites a prior record. Operator recovery **appends** an
   entry naming the reference; the quarantined reservation stays quarantined.

**How records stay attributable and history survives an update.** Every entry
names the reservation it is about, the host and approved target it is bound to,
who wrote it and when; an entry with no author is refused on read. A state change
is a **new entry appended** after the previous one, so the history is the file
and the current state is its last coherent entry. No entry is deleted or
rewritten, which is why `OPERATOR_RECOVERED` requires a `QUARANTINED` predecessor:
the recovery is the appended entry and the quarantine stays in its own.

### 5.5 Why two objects and not one

A crashed executor's `flock` is released by the kernel. If the lock were the
reservation, the next participant would find it free and proceed — which is
precisely finding PR-20260911-3. With the record separate, the next participant
finds the lock free, reads the record, sees `ADMITTED` or `RUNNING` with no
release record, and **refuses**. No automatic takeover exists, and none can be
produced by waiting. **No expiry and no free lock authorizes reuse.**

Conversely a test suite that crashes leaves no lifecycle record at all, because
participants 1–6 never write one. Its lock is released by the kernel and the next
suite proceeds. That is correct: a crashed test run is not a reservation and must
not block the host forever.

### 5.6 One allowlist of validated lifecycle outcomes, for all seven

**The correction R2-4 requires.** There is no participant-specific denylist. Every
participant, ordinary or executor, applies `reservation.validate_lifecycle()` —
the same function `reservation.admit()` calls — and proceeds only when its
verdict is a **validated outcome in the allowlist**.

`reservation.VALIDATED_LIFECYCLE_OUTCOMES` is that allowlist, and it holds
exactly three dispositions:

| Outcome | Proceeds | Required coherent shape |
|---|---|---|
| `verified_first_use` | yes | no predecessor state, no predecessor id, no release record, no recovery reference |
| `released` | yes | predecessor state `RELEASED`; predecessor named; release record present and bound to this host, target and predecessor; no recovery reference |
| `operator_recovered` | yes | predecessor state `QUARANTINED`; predecessor named; recovery reference present; no release record; and the requester's own id is **not** the recovered one |
| `active` | **no** | predecessor state `ADMITTED` **or** `RUNNING` |
| `recovering` | **no** | predecessor state `RECOVERING` |
| `quarantined` | **no** | predecessor state `QUARANTINED` |
| `unknown` | **no** | unconstrained; it refuses because it is unclassified |
| *anything else, or a malformed value* | **no** | refused as malformed before any comparison |

Two words in *"allowlist of validated outcomes"* are load-bearing.
**Allowlist**: a disposition outside the three refuses, so there is no
fall-through. **Validated**: membership is necessary and not sufficient — the
record carrying the disposition must first be *coherent*, and §5.9 is what that
means.

Three consequences the review asked for explicitly:

* **`ADMITTED` is active and refuses reuse even if the process lock is free.**
  Item 1 of §5.4 publishes ADMITTED before the first effect of any kind, so a
  crash between ADMITTED and RUNNING leaves a reserved host, a kernel-released
  lock and no release record;
* **unknown, malformed, incomplete and contradictory history also refuses**, for
  every participant, under the same validation; and
* the quarantine record refuses every participant, and the environment reset
  **especially**: a reset would destroy the residue the quarantine exists to
  preserve.

**[M]** `test_r2_proposal_models.py::test_all_seven_participants_share_one_allowlist`
is table-driven over thirteen histories and all seven participants;
`…::test_admitted_refuses_reuse_even_though_the_process_lock_is_free`;
`…::test_the_environment_reset_refuses_especially_while_a_quarantine_exists`;
`…::test_the_allowlist_is_the_reservation_modules_own_and_not_a_copy` asserts
identity rather than equality, so a second list cannot appear without failing.

### 5.7 Refusal paths

| Situation | Behaviour |
|---|---|
| Lock file absent | refuse: the host is not provisioned |
| Lock file present, permission denied | refuse: `ubuntu` is not in `freedomlab` |
| `flock` returns `EWOULDBLOCK` | wait or refuse; never proceed, never `LOCK_NB` in a loop that gives up and proceeds |
| Lock unreadable | refuse. An unreadable lock is not an unheld lock |
| `lifecycle.json` absent or unreadable | refuse. An unreadable record is not an empty one, and **initialization — §5.8 — is the only way out** |
| Record incomplete | refuse. A partial history establishes nothing about the reservations it omits |
| Record malformed, or its disposition unrecognised | refuse as malformed, before any comparison |
| Record **contradictory** — disposition and state disagree, or evidence is attached that the disposition forbids | refuse, naming which two halves disagree |
| Record says `ADMITTED` | **refuse.** This is R2-4 |
| Record says `RUNNING`/`RECOVERING` | refuse and name the reservation and its recovery owner |
| Record says `QUARANTINED` | refuse. Participant 6, the environment reset, refuses **especially** |
| Record says `RELEASED` with a bound release record and state `RELEASED` | proceed |
| Record says `VERIFIED_FIRST_USE` with no predecessor and no attached evidence | proceed |
| Record says `OPERATOR_RECOVERED` over a `QUARANTINED` predecessor with a reference, for a **new** reservation | proceed |
| Crash, then restart, lock free, record `ADMITTED` or `RUNNING` | **refuse.** This is §5.5 and it is the whole point |

### 5.8 Verified first use — a provisioning operation, proposed and unperformed

**The second half of R2-4.** A record that is absent always refuses, so the fresh
host needs a stated beginning. This is it, and **it provisions nothing**: it is a
proposed addition to the §7 provisioning inventory, and nothing in this pass
creates any of it.

| | Value |
|---|---|
| **Creator** | the operator provisioning the disposable host, **as root, out of band**. Not the harness, not a participant, and not a side effect of a run |
| **Authority** | the maintainer's approval of §7. **It is not approved**, and an unapproved provisioning step is a refusal rather than a default |
| **Path** | `/var/lib/freedom-blades/laboratory/lifecycle.json` — §5.4's object |
| **Host/target binding** | the record names the host and the approved target identity it is about. A record read for another host or another target is evidence about that one and refuses (`reservation.validate_lifecycle` already enforces the host half) |
| **Ownership and modes** | `root:freedomlab`, `0640`, in `root:freedomlab 0750` |
| **Creation rule** | **exclusive creation, no overwrite.** `O_CREAT\|O_EXCL` on the temporary and `RENAME_NOREPLACE` on the final name. An existing record is never reinitialized |
| **Durability** | the record's **bytes** are synchronized on the write descriptor, then renamed, then the containing directory's **entry** is synchronized on `lifecycle_syncfd`. Only after the second barrier is the record treated as existing at all |
| **Evidence of first use** | an operator attestation naming **who** established that this host has never been reserved and **how** — a fresh image, a rebuild reference. The claim is positive; its absence is not the claim |

**Refusals and their recoveries.**

| Refusal | When | Recovery |
|---|---|---|
| `already_initialized` | a record exists | read it. It is the history, and initialization is not how a history is replaced |
| `prior_use_not_excluded` | the host has been used before and the record is missing | **never reinitialize.** Every participant refuses, which is the correct fail-closed state. Recover by establishing what the predecessor was, or by a separately approved rebuild after which first use can be attested on the rebuild's own evidence |
| `interrupted_initialization` | a temporary from an earlier attempt is present | the temporary is reported by absolute path and **not removed automatically**, on the §2.13.2b precedent. An operator removes it after establishing that no record was published; the interrupted attempt published nothing, so nobody was ever admitted on it |
| `no_first_use_evidence` | nobody attested | obtain the attestation |
| `binding_mismatch` | the record would name another host or target | correct it |
| `not_durable` | either barrier failed | nothing is treated as initialized; a record a power loss would remove is not one any participant may be admitted on |

**Missing history on a previously used host must never be reinitialized as first
use.** That is the sentence this whole subsection exists for, and
`prior_use_not_excluded` is its refusal.

**[M]** `test_r2_proposal_models.py::test_fresh_provisioned_first_use_initializes_durably`,
`…::test_the_initialized_record_admits_every_participant` (the fresh-install path
reaching its successful control end to end),
`…::test_an_existing_record_is_never_reinitialized`,
`…::test_missing_history_on_a_previously_used_host_is_never_first_use`,
`…::test_first_use_without_a_complete_attestation_refuses`,
`…::test_an_interrupted_initialization_publishes_nothing_and_refuses`,
`…::test_a_leftover_temporary_is_reported_and_not_cleaned`, and
`…::test_a_host_with_no_record_refuses_every_participant_until_it_is_initialized`.

### 5.9 The decision repair — PR-20260911-R2-1, implemented

This one is code rather than design, and it is **the only thing in this document
that is built**.

**The defect.** `reservation.admit()` chose an admitting branch from
`history.disposition` alone and then validated only that branch's own evidence.
A readable, complete history with a matching `ReleaseRecord` and
`predecessor_state` set to `RUNNING` or `QUARANTINED` therefore returned
`admitted=True`: a release record was allowed to override the state it
contradicted. The local reproduction found the same fall-through for a **malformed**
disposition — a plain string `"released"` matched no `is` comparison, produced no
refusal, and admitted.

**The repair.** `reservation.validate_lifecycle()` validates the record as a
coherent whole, in four stages, and the first three run **before any admitting
branch is chosen**:

1. is this record about this host, was it read, and is it complete;
2. are its values inside the closed vocabularies at all — a malformed value is
   refused rather than compared;
3. does the record **agree with itself** under `reservation.LIFECYCLE_SHAPES`,
   which states for every disposition the predecessor states it may be paired
   with and whether the predecessor identity, the release record and the recovery
   reference are required, forbidden or unconstrained; and only then
4. is its disposition in `reservation.VALIDATED_LIFECYCLE_OUTCOMES`.

Coherence and admission stay separate: a coherent `ACTIVE` record is coherent and
refuses; an incoherent `RELEASED` record refuses **and** tells the operator which
two halves disagree. Nothing is normalized into a successful disposition.

The accepted combinations are the table in §5.6, stated in code as
`LIFECYCLE_SHAPES` rather than inferred from a chain of branches — which is what
let R2-1 through.

**What was preserved.** The wrong-host, wrong-target and wrong-reservation
release-record tests; the omitted-residue refusals; `GUARDED_TRANSITIONS`;
quarantine behaviour; and the unconditional real-execution gate, still asserted
under every repaired admitting disposition. **The repair is decision validation,
not an operationally enforced reservation**: `DECISIONS_DO_NOT_PERSIST` still
says an admitting decision is not a reservation, and `ADAPTER_RESPONSIBILITIES`
still names the lock, the durable record, the inventory and *any enforcement at
all* as things nothing in this pass implements.

**Regressions.** `tests/phase_5_0_evidence/test_reservation.py`, the section
headed *PR-20260911-R2-1*: the released-disposition state table, the reviewer's
exact reproduction, the first-use and operator-recovery audits, the refusing
dispositions audited for fall-through, and the malformed-value case.

---

## 6. Exact diff — what would be built, and what it would need

**None of this is built.** The estimates are for review, not for scheduling.

### 6.1 Modules and interfaces

| Module | Change | Size |
|---|---|---|
| `execution/descriptors.py` | **new.** §1.3's inventory: open each directory twice, in the two modes; `fstat`; record; bind the synchronizable descriptor by comparison; hand out by index; refuse an unregistered index; refuse to transfer a synchronizable descriptor | ≈ 260 lines |
| `execution/case_program.py` | new `DIRFD` and `COMPONENT` argument kinds; the four descriptor-relative verbs of §6.2; the `execveat` launch path for X1 | ≈ 260 lines |
| `execution/executor.py` | issue P1/P1b/P2/P4/L3 through the chain; the quiescence gate of §1.6; the pre-check/post-check of §1.4.5 with the corrected evidence claims | ≈ 200 lines |
| `execution/materializer.py` | §2.3's ordered capture-and-publish with all five barriers, and §2.4's verify-and-write with its two, replacing the digest-then-`install` pair | ≈ 240 lines |
| `execution/recovery_store.py` | **new.** The independent store of §2.2: paths, modes, record format, the barrier order, restart discovery, retention | ≈ 200 lines |
| `execution/host_lock.py` | **new.** §5.3's protocol: open existing, `flock`, read the record, apply `validate_lifecycle`, refuse. **No creation, no unlink** | ≈ 110 lines |
| `execution/lifecycle_record.py` | **new.** §5.4's writer and §5.8's initialization, with both barriers and the exclusive-creation rule | ≈ 170 lines |
| `cleanup.py` | LAB-1's §8.1 reporting fix; `RECOVERY_PROCEDURE` replaced by §8.2's independent procedure | ≈ 60 lines |
| `plan.py`, `review_manifest.py` | coverage for the five new modules; no new executable | ≈ 25 lines |

**Already written in this pass, and they are models rather than mechanism:**

| Module | What it is |
|---|---|
| `durability_model.py` | the bounded synthetic filesystem with separate volatile and durable state, explicit descriptor modes, the publication and restoration barrier graphs, and the removal model of §1.4.5. **Planning tier**: its whole "filesystem" is a dictionary |
| `lifecycle_storage.py` | the seven participants under one allowlist, and §5.8's initialization modelled over that filesystem. **Provisions nothing** |

### 6.2 Verbs, arguments and syscalls

```
  "openat":    (DIRFD, OPEN_MODE, COMPONENT)
  "unlinkat":  (DIRFD, COMPONENT)
  "renameat":  (DIRFD, COMPONENT, DIRFD, COMPONENT)
  "fstatat":   (DIRFD, COMPONENT)
```

* `DIRFD` — an index into the **inherited** descriptor table the executor handed
  this invocation, never a number a caller chooses freely and never a descriptor
  the program opened for itself. **A synchronizable descriptor is never in that
  table**;
* `OPEN_MODE` — a member of a closed set: `O_PATH|O_NOFOLLOW|O_DIRECTORY`,
  `O_RDONLY|O_NOFOLLOW`, `O_RDONLY|O_NOFOLLOW|O_DIRECTORY`, or
  `O_CREAT|O_EXCL|O_WRONLY|O_NOFOLLOW`. **This is an extra argument r2 did not
  have**, and it exists because a mode is part of a descriptor's contract;
* `COMPONENT` — one path component: no `/`, no `.`, no `..`;
* verb count **16 → 20**; `BOOTSTRAP_VERBS` unchanged at **2**;
* syscalls newly reached: `openat(2)` with the four modes above; `mkdirat(2)`;
  `unlinkat(2)` with `0` and `AT_REMOVEDIR`; `renameat2(2)` with
  `RENAME_NOREPLACE` and `0`; `fstatat(2)` with `AT_SYMLINK_NOFOLLOW`;
  **`fsync(2)` on `O_RDONLY` directory descriptors and on `O_WRONLY` file
  descriptors**; `execveat(2)` with `AT_EMPTY_PATH`; `flock(2)`; `ioctl(2)`
  `FS_IOC_SETFLAGS`/`FS_IOC_GETFLAGS` on an `O_RDONLY` descriptor rather than
  through `chattr`;
* `RENAME_NOREPLACE` requires filesystem support; `rename(2)` lists ext4 from
  Linux 3.15 and tmpfs from 3.17 **[D]**. The target's filesystem type is one of
  the twelve unconfirmed facts, so this is a **prerequisite to confirm at the
  Codex read-only preflight**, not an assumption to carry.

### 6.3 Descriptor transfer

Inheritance across `fork`/`execve` only, with `FD_CLOEXEC` cleared on a declared
set starting at descriptor 3 and a table naming each entry and its mode. No
`SCM_RIGHTS`, no re-open by path, no `/proc/<pid>/fd` traversal by any party
other than the executed program reading its own `/proc/self/fd/N` for X1, and
**no synchronizable descriptor in any transferred set**.

### 6.4 Executables, identities and the permission delta

| Surface | Before | After, **if built** |
|---|---|---|
| `plan.PERMITTED_EXECUTABLES` | 22 absolute paths | **20** — `/usr/bin/install` and `/usr/bin/chattr` are **removed** from the harness path, replaced by syscalls in the case program |
| `case_program.VERBS` | 16 | **20** |
| `case_program.BOOTSTRAP_VERBS` | 2 | **2, unchanged** |
| `executor.PERMITTED_RUN_AS` | the identity contract | **unchanged** |
| `sudoers.EXPECTED_COMMANDS` | 2 `Cmnd_Alias` targets | **unchanged** |
| The one `ctypes` exception | `case_program._prctl_get_securebits` | **a second one**: the `FS_IOC_SETFLAGS`/`FS_IOC_GETFLAGS` ioctls and `execveat`, which CPython does not expose |
| Descriptors opened per run | the chain, one mode | **the chain in two modes** — `O_PATH` for traversal, `O_RDONLY` for the seven directories that must be synchronized (D3, D5×2, D10, D12, D14, D17). No new privilege; more open descriptors and one more argument kind |
| New privileged writer | — | **none**; the executor is the existing one |
| New system group | — | **`freedomlab`**, with `ubuntu` as a member |
| New provisioned paths | — | `/run/freedom-blades` (`root:freedomlab 0750`), `/run/freedom-blades/laboratory.lock` (`root:freedomlab 0660`), `/var/lib/freedom-blades/laboratory` (`root:freedomlab 0750`), `/var/lib/freedom-blades/recovery` (`root:root 0700`) |
| **New provisioned object** | — | **`/var/lib/freedom-blades/laboratory/lifecycle.json`** (`root:freedomlab 0640`), created once at provisioning per §5.8. **New in r3** |
| New systemd artifact | — | one `systemd-tmpfiles` fragment for the two `/run` entries |
| New capability or unit | — | **none** |

**The permission delta is not zero, and revision 1's claim that it was is
withdrawn.** It is: one system group, one group membership, one tmpfiles
fragment, four provisioned paths, **one provisioned initial record**, one extra
case-program argument kind, and a second `ctypes` exception. Removing two
executables from the allowlist is a reduction and does not offset the additions.

**Do not infer a zero delta from unchanged executable names.** Revision 1 did
exactly that. r2 then inferred that specifying the syscalls had found the whole
delta; it had not, because §5.8's initial record had not been specified either.

### 6.5 Durable storage and manifest coverage

Five new execution-tier modules would join `COVERED_SOURCES` when written, so the
review-input digest changes again at that point. The two model modules written in
this pass are already covered, which is why the digest changed now. The recovery
store, the lifecycle record and its initial provisioned instance are new durable
state outside the disposable root; all are listed in §7 and none exists.

---

## 7. Provisioning and permission changes — required, and unapproved

Every one of these is a change to the disposable host. **None is approved by this
document, and calling the lock adapter unprivileged does not approve any of
them.** They are listed so a maintainer can approve or refuse them as a set.

| # | Change | Why | Approved? |
|---|---|---|---|
| V1 | create system group `freedomlab` | so ordinary participants can open the lock without `sudo` | **no** |
| V2 | add `ubuntu` to `freedomlab` | it is every participant's identity **[A]** | **no** |
| V3 | `systemd-tmpfiles` fragment creating `/run/freedom-blades` `0750 root:freedomlab` and `laboratory.lock` `0660 root:freedomlab` | `/run` is tmpfs; the lock must exist before any participant runs | **no** |
| V4 | create `/var/lib/freedom-blades/laboratory` `0750 root:freedomlab` | the durable lifecycle record must survive reboot | **no** |
| V5 | create `/var/lib/freedom-blades/recovery` `0700 root:root` | the independent recovery store of §2.2 | **no** |
| **V7** | **initialize `/var/lib/freedom-blades/laboratory/lifecycle.json` `0640 root:freedomlab` with a verified-first-use record, exclusively, durably, bound to the host and approved target, on a named operator attestation** | **§5.8. Without it the documented fresh-install path cannot reach its successful control. New in r3** | **no** |
| V6 | confirm the filesystem under `R` supports `RENAME_NOREPLACE` | §6.2; one of the twelve unconfirmed facts | **preflight**, unperformed |
| **V8** | **confirm that `fsync` on an `O_RDONLY` directory descriptor behaves as the containing-entry barrier on the target's filesystem** | **§2.3. The barrier graph depends on it, and it is not among the twelve existing facts. New in r3** | **preflight**, unperformed |

---

## 8. LAB-1 — the proposed reporting-contract fix

**Classification: Important, confirmed by the September 11 review and unchanged
by the re-review. It remains unimplemented, and this pass did not repair it or
weaken its reproduction.** It is a reporting gap in evidence classification rather
than a safety property, and it makes no unsafe operation reachable.

### 8.1 The fix

`§2.13.2b` requires an S-B run to report *the named operator recovery*, and
`journal.classify_cleanup_failure_state` compares that clause like the other six.
Two named recoveries exist and they are **for different things**:

* `journal.RECOVERY_PROCEDURE` — five steps, **residue** recovery: read the
  reported paths, `lsattr` each, clear `FS_IMMUTABLE_FL`/`FS_APPEND_FL` as root
  where that is why removal failed, remove the artifacts and then the
  directories, re-run `verify-capability`; and
* `cleanup.RECOVERY_PROCEDURE` — four steps, **configuration** recovery.

`CleanupOutcome.recovery_procedure` carries only the second, and only when a
configuration capture was retained. A run that reaches S-B on **residue alone** —
which is both variants of `JNL-47-RECOVERY-STATE` — therefore reports no named
recovery at all.

**Proposed change, and it keeps the two procedures distinct:**

```
class CleanupOutcome:
    ...
    recovery_procedure: tuple[str, ...] = ()           # configuration, unchanged
    residue_recovery_procedure: tuple[RecoveryStep, ...] = ()   # new
```

* `classify_cleanup` attaches `journal.RECOVERY_PROCEDURE` to
  `residue_recovery_procedure` **when and only when `residue` is non-empty**, and
  continues to attach `cleanup.RECOVERY_PROCEDURE` to `recovery_procedure` when
  and only when a configuration capture was retained;
* a run with both reports both, in that order, and they are never merged; and
* the evidence clause is satisfied when the outcome names **the procedure that
  applies to the state it reached** — residue-only ⇒ the residue procedure;
  configuration-only ⇒ the configuration procedure; both ⇒ both.

**Why it is not made in this pass.** It changes `CleanupOutcome`'s accepted
contract and adds a `cleanup` → `journal` module dependency. That is a mechanism
change behind the outstanding design checkpoint, so it is submitted here and the
reproduction stays as it is.
`test_feasibility.py::test_the_recovery_case_reproduces_lab_1` is a **labelled
defect reproduction** and deliberately asserts that the record **fails**. It was
not weakened in this pass, the recovery records are still `FAILED`, and they
still fail on exactly the recovery clause.

### 8.2 The second change LAB-1 travels with — `cleanup.RECOVERY_PROCEDURE`

Step 2 currently instructs recovery from `R/before`, which §2.1 shows is not an
independent basis. Proposed replacement, with only step 2 and step 4 changed:

> **2.** The byte-exact pre-change captures are retained **outside the disposable
> root**, under `/var/lib/freedom-blades/recovery/<run-id>/`, root-owned `0400`
> with a record binding each copy's SHA-256 to its destination and to the source
> identity it was taken from. **The run directory's entry in the recovery parent
> is durable**, so listing that parent finds it after a restart. Read the record,
> verify the copy against it, and compare with the live file before doing
> anything else. **Do not use `R/before`**: its custody depends on the root whose
> safety is in question.
>
> **4.** … Only then remove the run's directory under
> `/var/lib/freedom-blades/recovery/`, and only after the reservation has
> released without quarantine.

### 8.3 Regression expectations, if the fix is accepted

| # | Case | Expectation |
|---|---|---|
| 1 | S-B on residue alone | `residue_recovery_procedure` carries `journal.RECOVERY_PROCEDURE`'s five steps in order; `recovery_procedure` is empty |
| 2 | S-B on configuration risk alone | `recovery_procedure` carries the four configuration steps; `residue_recovery_procedure` is empty |
| 3 | S-B on both | both are populated, both complete, neither merged |
| 4 | S-A and S-C | both are empty |
| 5 | `JNL-47-RECOVERY-STATE`, both variants | the record's seventh clause is satisfied, and the record's status turns `PASSED` **only if** the six other clauses still hold |
| 6 | the labelled reproduction | replaced by (5) in the same file, with a dated note recording what it used to reproduce |
| 7 | the independent-recovery procedure | its step 2 names `/var/lib/freedom-blades/recovery/` and does **not** name `R/before`; a test asserts the absence |

---

## 9. The bounded proof matrix

### 9.1 How to read a row

**Model rows are proposal-model tests, not implementation proof.** Each tracks
the **original and replacement identities and the bytes actually affected** as
separate values, and the model's state is split into what a reader sees now and
what would survive a power loss. A passing row establishes that the proposed rule
is constructible and falsifiable. It establishes **nothing** about the built
mechanism, about Linux, or about `oracle-test`, and **nothing here may be cited
as evidence for EH-R16-1**.

Rows marked **[M]** are written and pass in this tree. Rows marked **[P]** are
specified and have no test, because they need the mechanism.

### 9.2 The matrix

| # | Scenario | Expected | What it falsifies | Status |
|---|---|---|---|---|
| 1 | `R` replaced between C1 and an `fstatat` by name | detected; dependent effects refused; S-B | that the root's exposure is nil | **[P]** |
| 2 | a descendant directory replaced after its chain entry was recorded | detected on the next `fstatat` by name; refused | §1.1(1)'s withdrawn claim | **[P]** |
| 3 | a final entry replaced after a successful pre-check and before `unlinkat` | **not** prevented and **not detected**: the post-check's `ENOENT` is indistinguishable from a correct removal. The oracle shows A surviving under its new name and B removed | **the r2 claim that the post-check detects the event and reports both identities** | **[M]** `test_the_exact_counterexample_removes_b_and_leaves_a_alive`, `test_the_post_check_cannot_tell_the_two_removals_apart` |
| 3b | a final entry replaced **before** the pre-check | detected; removal refused; both identities reported | that the pre-check is decorative | **[M]** `test_a_substitution_before_the_pre_check_is_genuinely_detected` |
| 4 | removal attempted with quiescence unobserved, observed false, or incomplete | refused; residue reported by absolute path; dependent work refused; S-B; independent recovery preserved | that quiescence is a detector rather than a prerequisite | **[M]** `test_unobserved_false_or_incomplete_quiescence_refuses_the_effect` |
| 4b | removal under verified quiescence, nothing injected | the intended object is removed | that the mechanism refuses everything | **[M]** `test_the_intended_removal_succeeds_under_the_declared_exclusion_premise` |
| 5 | a payload's inode replaced at its pathname after P2 | `execveat` runs the **original** inode | that pathname execution and descriptor execution are equivalent | **[P]** |
| 6 | a payload's **bytes** mutated in place, inode unchanged | **not** detected by any descriptor check | that descriptors bind content | **[P]** |
| 7 | capture read fails, or size exceeds the bound | M1 never runs; no mutation | that capture failure is recoverable after mutation | **[M]** `test_failure_before_any_barrier_prevents_the_mutation_too` |
| 8 | failure injected at **each** of the five publication barriers | M1 never runs; the configuration is unchanged; the missing barrier is named | that a held buffer or a read-back is a durable basis | **[M]** `test_failure_at_any_barrier_prevents_the_first_configuration_mutation` |
| 8b | **the r2 sequence** — every barrier but `recovery-parent-entry` | **fails**: publication refuses, and after a modelled crash the recovery parent's listing does not contain the run | **that syncing a child's contents makes its parent's entry durable.** The negative control | **[M]** `test_the_revision_2_sequence_fails_the_corrected_property`, `test_syncing_the_childs_contents_is_not_the_parents_entry_barrier` |
| 9 | wrong destination in the record | restore refuses; nothing is written | that a matching digest is sufficient | **[M]** `test_a_record_naming_another_destination_restores_nowhere` |
| 10 | executor restarts, memory lost, `R` gone, after a successful publication | recovery found by `readdir` of the store; record present; copy present; digest verifies | that recovery needs the executor or `R` | **[M]** `test_a_crash_after_a_successful_publication_leaves_a_usable_recovery_basis` |
| 11 | restore interrupted before its rename | destination unchanged; temporary detected and reported | that partial writes can reach the destination | **[M]** `test_a_restoration_interrupted_before_its_rename_leaves_the_destination_alone` |
| 11b | restore interrupted **after the rename and before the directory barrier** | `renamed` true, `durable` **false**; a modelled crash returns the destination to the mutated bytes | **that a rename is a durable restoration** | **[M]** `test_a_rename_without_its_directory_barrier_is_not_a_durable_restoration` |
| 12 | restore interrupted between two renames | mixed configuration; post-reload verification not claimed; S-B | that a multi-file restore is atomic | **[M]** `test_a_multi_file_restoration_interrupted_between_renames_is_mixed` |
| 12b | **invalid-O_PATH-operation control** — `fsync` on the traversal descriptor | refused, `EBADF`, naming the operation `open(2)` does not permit | **that r2's `fsync(bin_fd)`/`fsync(pgconf_fd)` could have succeeded** | **[M]** `test_fsync_on_an_o_path_descriptor_is_refused` |
| 12c | a synchronizable descriptor opened over a substituted name | refused before any barrier | that the second open may be trusted without comparison | **[M]** `test_a_synchronizable_descriptor_is_bound_by_comparison_not_by_pathname` |
| 13 | lock file absent | every participant refuses | that a participant may create it | **[P]** |
| 14 | lock held by another participant | wait or refuse | that `LOCK_NB` failure may be walked past | **[M]** `test_a_held_lock_makes_every_participant_wait_or_refuse` |
| 15 | lock free, lifecycle record says `RUNNING` | **refuse** | that a free lock is a released host | **[M]** in the participant table |
| 15b | lock free, record says **`ADMITTED`** | **refuse** | **r2 §5.6's denylist, which omitted it** | **[M]** `test_admitted_refuses_reuse_even_though_the_process_lock_is_free` |
| 15c | record unknown, malformed, incomplete or **contradictory** | refuse, for all seven | that an ordinary participant may read the record more loosely than the executor | **[M]** `test_all_seven_participants_share_one_allowlist` |
| 16 | lock free, record says `RELEASED` with a bound release record and state `RELEASED` | proceed | that the refusals above refuse everything | **[M]** in the participant table |
| 16b | fresh provisioned first use, initialized per §5.8 | initialization succeeds durably **and** every participant then proceeds | **that the fresh-install path has no reachable successful control** | **[M]** `test_fresh_provisioned_first_use_initializes_durably`, `test_the_initialized_record_admits_every_participant` |
| 16c | missing record on a **previously used** host | initialization refuses `prior_use_not_excluded`; no record is created | that an absent record may be reinitialized as first use | **[M]** `test_missing_history_on_a_previously_used_host_is_never_first_use` |
| 16d | initialization interrupted at each of its three points | nothing is published; a modelled crash finds no record; the leftover temporary is reported and not cleaned | that an interrupted initialization can leave a partial record somebody is admitted on | **[M]** `test_an_interrupted_initialization_publishes_nothing_and_refuses`, `test_a_leftover_temporary_is_reported_and_not_cleaned` |
| 17 | quarantine record present, participant 6 (environment reset) | refuse, and refuse **especially** | that a reset is a recovery | **[M]** `test_the_environment_reset_refuses_especially_while_a_quarantine_exists` |
| 18 | unknown surviving writer at admission | refuse and name it; never kill it | that an inventory may be completed by force | implemented in `reservation.admit`; `test_reservation.py` |
| 19 | **successful controls**: full provisioning, publication, restoration, removal, participant admission and first-use initialization, with nothing injected | every one succeeds | that the mechanism refuses everything | **[M]** rows 4b, 16b, and `test_the_positive_sequence_crosses_every_barrier_and_permits_the_mutation`, `test_a_complete_restoration_is_durable_and_says_so` |

Rows 3, 8b, 11b and 12b are the ones that must **fail** revision 2's mechanism
and hold under this one. A matrix in which revision 2 also passes is a matrix
that is not testing the correction.

### 9.3 The implementation checks that would establish the real properties

**None of these has been performed, and this pass ran no real filesystem
durability drill.** They belong to the eventual implementation review and the
separately authorized target work.

| # | Check | Why a model cannot stand in |
|---|---|---|
| I1 | that an `O_PATH` descriptor really refuses `fsync` with `EBADF` on the target kernel, and that the separately opened `O_RDONLY` directory descriptor really accepts it | the model refuses by construction. The kernel is the authority |
| I2 | that the target filesystem implements `fsync` on a directory as the containing-entry barrier the design relies on | this is filesystem behaviour, and it is proposed as new preflight fact **V8** |
| I3 | that the target filesystem supports `RENAME_NOREPLACE` | one of the twelve unconfirmed facts; preflight item **V6** |
| I4 | that a real power loss after a successful capture publication leaves the recovery parent listing the run directory, and that directory listing a verifiable copy and record | a modelled crash is an assignment. A real one involves a device |
| I5 | that a real restoration interrupted between the rename and the directory synchronization leaves the destination at its previous content | same |
| I6 | that the descriptor table a step inherits contains exactly the declared entries with the declared modes | the model hands out indices; a real run hands out kernel descriptors |
| I7 | that `execveat(…, AT_EMPTY_PATH)` with `/proc/self/fd/N` executes the reviewed payload under every disposable identity | needs the identities, the payload and the interpreter, none provisioned |

---

## 10. Assumptions, and what this document does not do

**Every [A] in one place.** `oracle-test`'s participants all run as `ubuntu`;
`ubuntu` holds passwordless `sudo`; `/run` is a tmpfs;
`/opt/freedom-blades/evidence`, `/var/lib/freedom-blades/recovery` and
`/etc/postgresql/16/main` are root-only; host administrators are trusted to obey
the reservation and are **not prevented from ignoring it, and are not claimed to
be**; the filesystem under `R` is unconfirmed, and `RENAME_NOREPLACE` support and
the directory-barrier semantics with it. None of these was verified on the target
by this document, and no host was inspected.

**It accepts nothing.** It approves no digest, populates none of the twelve
unconfirmed target facts, authorizes no host action, no SSH, no synchronization,
no provisioning, no database operation and no execution. It does not clear the
operational-ineligibility control, does not move `is_executable`, and does not
reduce the three C-7 cases' unresolved status.

EH-R16-1, PR-20260910-1/2/3, the September 10 findings, the six September 11
findings and the four September 11 re-review findings remain **Open**. Package
5.0 remains **not ready**, P5.0-R5 **Blocking**, OD-62 **Open**.

**The next step is Codex's technical review of this mechanism**, then Peter's
decision on the §7 provisioning and permission delta — now eight items — and on
LAB-1's classification. Implementation review precedes the later read-only target
preflight, which precedes a separate execution decision. **Passing tests advance
none of those gates.**
