# Package 5.0 — runner contract, revision 4

> **Superseded, 2026-09-11.** This revision is replaced in its entirety by
> [`phase-5-0-reserved-laboratory-runner-contract-r5.md`](phase-5-0-reserved-laboratory-runner-contract-r5.md),
> which answers the [R4 re-review](project-review-2026-09-11-r4.md). It is
> preserved as the submission that review answered. **Where it and r5 disagree,
> r5 is the proposal and this is history.**
>
> **Erratum, 2026-09-11.** Four statements below are withdrawn as incorrect.
>
> 1. **§5.5's order rules are incomplete.** "The last reservation entry is the
>    current state" and the membership rules around it do not require a
>    transition to belong to the currently active reservation, so a stale
>    terminal entry for a finished reservation, appended after a newer
>    `admitted`/`running` pair, is accepted and becomes the decision. This is
>    PR-20260911-R4-1. r5 §5.5 replaces the rules with a state machine over the
>    current reservation.
> 2. **§§5.5, 5.8 and 5.11 state no binding between a participant's completion
>    and the run that started.** The completion profile is chosen from the
>    caller's participant and appended to the caller's filename, a terminal
>    entry with no start is read as a settled run, and evidence is checked for
>    presence rather than content. This is PR-20260911-R4-2. r5 §5.11.1 adds the
>    validator, and r5 §5.8 requires the ledger rather than tolerating its
>    absence.
> 3. **§5.7's T11/T12 order is not achievable.** Participant completion is
>    published before the release its own completion conditions require, so no
>    process can obtain its stated observation in that order. This is
>    PR-20260911-R4-3. r5 §5.12 states the corrected order and its argument.
> 4. **§9.2 row 39's claim is withdrawn.** The successful trace did not
>    establish the complete terminal sequence; it injected both lifecycle-owned
>    facts while the record still said `running`. See r5 §9.4.
>
> §§1–4 and §8 are carried into r5 unchanged, and the R4 re-review's positive
> recommendations on the target/attribution repair and the successor durability
> step stand within their stated scope.

Date: 2026-09-11. Author: Claude. Change record: C-P5.0-LAB-1.

**Status: submitted for technical review. Not accepted, not implemented, and no
execution is authorized.**

**This revision supersedes
[`phase-5-0-reserved-laboratory-runner-contract-r3.md`](phase-5-0-reserved-laboratory-runner-contract-r3.md)
in its entirety**, which supersedes
[r2](phase-5-0-reserved-laboratory-runner-contract-r2.md) and
[revision 1](phase-5-0-reserved-laboratory-runner-contract.md). All three are
preserved as the submissions their reviews answered, r2 and r3 each carrying a
dated supersession and erratum notice. Where any two disagree, **this one is the
proposal and the earlier ones are history.** No contradictory r3 row is left
authoritative: §§1–4 and §8 are carried forward, and §§0 and 5–10 replace r3's.

It answers the September 11 R3 re-review's Blocking findings
**PR-20260911-R3-1** and **PR-20260911-R3-2** and its Important finding
**PR-20260911-R3-3**, as **one lifecycle** rather than three patches — because
all three had one cause, which §5.1 states.

Nothing here repairs **EH-R16-1**. It remains Open, the harness retains its
unconditional real-execution refusal (`reservation.REAL_EXECUTION_REFUSAL`), and
a reserved host does not close it — §1.1 says why in the finding's own terms.

The reserved-laboratory direction stands, VM work stays deferred, and ADR 0011
stays **Proposed**. This is not a second architecture survey.

---

## 0. How to read a claim in this document

Four kinds of statement appear below and they are not interchangeable.

| Label | What it means | How it may be checked |
|---|---|---|
| **[D] documented** | A semantic the primary manual page states. Verified against `man-pages 6.7` as installed on this workstation and cross-read against [open(2)](https://man7.org/linux/man-pages/man2/open.2.html), [fsync(2)](https://man7.org/linux/man-pages/man2/fsync.2.html), [rename(2)](https://man7.org/linux/man-pages/man2/rename.2.html), [unlink(2)](https://man7.org/linux/man-pages/man2/unlink.2.html) and [flock(2)](https://man7.org/linux/man-pages/man2/flock.2.html). | read the cited page |
| **[P] proposed** | A guarantee this design would provide *if* it were built and *if* its prerequisites hold. **Nothing below is built.** | review the argument; then the model rows of §9 |
| **[M] modelled** | A result observed from a bounded synthetic model in this repository, over injected effects. It establishes that the proposed rule is constructible and falsifiable, and **nothing about Linux or about `oracle-test`**. | run the named test; read `durability_model.MODEL_LIMITS` |
| **[A] assumed** | An operational premise nobody has verified on the target, or a trust statement about people. | it is not checked here, and §10 lists every one |

The twelve unconfirmed target facts remain unconfirmed and none is populated by
this document. Every **[A]** below is a statement about the design's premises,
not an observation of `oracle-test`.

**One distinction is new in r4 and it carries §5.** A **design inference** —
"the specified order implies this" — is a **[P]**, never a **[D]** and never an
**[M]**. §5.6 depends on exactly one, names it as one, and says what would
falsify it.

### 0.1 What the reservation changes, and what it does not

Unchanged from revisions 1, 2 and 3, and restated because every row below
depends on it:

| | Before the reservation | After it |
|---|---|---|
| An unrelated cooperating writer substitutes an object mid-run | possible, and undetected | excluded by the lock plus the pre-admission inventory **[P]**; a detected violation invalidates the affected evidence |
| A host administrator substitutes an object mid-run | possible | still possible. Trusted not to; not prevented, and not claimed to be **[A]** |
| **This run's own experimental writers** substitute an object mid-run | possible | **still possible.** This is EH-R16-1, and §1 is the whole of this document's answer to it |

---

**§§1 through 4 are carried forward from revision 3 unchanged.** The R3
re-review made no finding against them, and recorded that R2-2's named design
corrections — the usable `O_RDONLY` directory references and the recovery-parent
barrier — are satisfactory, and that R2-3's corrected post-unlink claim should
be closed. They are reproduced here rather than cited so that this document is
the complete contract.

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
| D17 | `lifecycle_pathfd`, `lifecycle_syncfd` | `/var/lib/freedom-blades/laboratory` | as D11/D12 | run | the reservation record's writes and its two barriers (§5.4, §5.10), **and every participant's re-seal of its parent entry (§5.6)** | never |
| D18 | `lock_fd` | `/run/freedom-blades/laboratory.lock` | `O_RDWR`, **no `O_CREAT`, no `O_EXCL`** | the participant's whole run | `flock` | never |
| **D19** | **`runs_pathfd`, `runs_syncfd`** | **`/var/lib/freedom-blades/laboratory/runs`** | **as D11/D12** | **the participant's whole run** | **its own run entry's writes and barriers, and the re-seal of §5.6. New in r4** | **never** |

**D17 and D19 are opened by every participant, not only the executor** —
r3's inventory had D17 as the executor's alone, which is the shape §5.6
corrects. Both are `O_RDONLY` for the barrier and neither grants any write
permission on the objects inside them.

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
| **A contradictory lifecycle record** | **refuse**, naming which two halves disagree | `reservation.validate_lifecycle`, repaired 2026-09-11 — **implemented**, §5.12 |
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

## 5. The complete lifecycle — PR-20260911-R3-1, -R3-2 and -R3-3

### 5.1 What the re-review established

Revision 3 §§5.1–5.9 replaced the withdrawn `O_EXCL` lock protocol with a
persistent provisioned inode plus a separately protected lifecycle record, and
gave all seven participants one allowlist. The re-review found three things
wrong with what was left, and this section is the whole of the answer.

**R3-1, Blocking — a failed publication leaves an admissible-looking record.**
§5.8's initialization renames the record before synchronizing the containing
directory. If that barrier fails the function returns `not_durable` and the
final record is **already readable**. A process-only restart retains it, a retry
returns `already_initialized` whose recovery says to read it, and the
initializer's in-memory outcome died with the initializer. The protocol admitted
a readable, coherent first-use record with no specified way to establish that
its publication had ever completed. Revision 3 had **no successor obligation at
all** at this point, and the interruption test called the model's power-loss
`crash()` immediately, which hid the process-only case.

**R3-2, Blocking — ordinary participant crashes bypass lifecycle protection.**
§5.2's asymmetry — one participant writes the record, six only serialize — was
presented as the design. §5.5 then drew the consequence explicitly: *"a test
suite that crashes leaves no lifecycle record at all … the next suite
proceeds."* Those six include the database suites, the synchronization, the
dependency update and the environment reset. A synchronization wrapper that dies
having replaced half a tree, or a database suite that dies with a server-side
transaction unsettled, leaves the previous record unchanged and the next
participant takes a free lock and proceeds. Calling the interrupted operation a
test rather than a reservation does not establish that its effects ended.

**R3-3, Important — first use and recovery lose their target binding.**
`LifecycleHistory` had no target field. Target identity was compared only inside
a `ReleaseRecord`, so `VERIFIED_FIRST_USE` and `OPERATOR_RECOVERED` admitted
against any approved target on a matching hostname; and the first-use evidence's
author and basis never travelled from storage into the decision at all.
`BINDING_MISMATCH` was declared in the refusal vocabulary with no branch that
could produce it.

All three share one cause: **revision 3 specified a record and never specified
the act of reading one.** §§5.4–5.9 below specify publication, reading,
re-sealing, parsing, ordering and admission as one protocol.

### 5.2 The participants, their identities and their writers

All seven run on `oracle-test` as the OS user `ubuntu` **[A]**, which holds
passwordless `sudo` per the disposable-server profile.

| # | Participant | Identity **[A]** | Holds the lock | Writes the reservation record | Writes a run entry |
|---|---|---|---|---|---|
| 1 | `tests/test_*.py` (bot suite) | `ubuntu` | for the whole serial run | no | **yes — new in r4** |
| 2 | `tests/web` (web suite) | `ubuntu` | for the whole serial run | no | **yes** |
| 3 | `foundry-module/tests` (`node --test`) | `ubuntu` | for the whole run | no | **yes** |
| 4 | §3.2 synchronization | `ubuntu` | from before `rsync` until the tree is consistent | no | **yes** |
| 5 | §3.5 dependency updates | `ubuntu` | for the whole `uv pip install` | no | **yes** |
| 6 | §4 environment reset | `ubuntu` | for the whole reset | no | **yes**; and it refuses while a quarantine or an unsettled run exists |
| 7 | harness CLI | `ubuntu`, escalating to root for effects | for the reservation | **yes**, as root | **yes** |

**Revision 3's asymmetry is withdrawn as a licence and kept as a fact about one
object.** Six participants still do not write the *reservation* record, because
they are not reservations. Every one of them now writes its own *run* entry,
because every one of them can leave an effect that outlives its wrapper, and
R3-2 is that those effects were unaccounted for. The two objects and their two
permissions are §5.4.

**What the file modes do, and what they do not.** All seven run as the same OS
user and that user holds passwordless `sudo`, so neither the record's mode nor
the ledger's constrains a participant that chooses to ignore the protocol. The
modes prevent accidental and misdirected writes; they are not a barrier against
the participants, and revision 3 should not have implied otherwise by calling
the record *"written by the executor as root, and by nothing else"* without that
qualification. Separating the seven identities would be a real barrier. It is a
permission decision nobody has taken, it is **V10** in §7, and it is unapproved.

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


### 5.4 The two durable objects

| | Reservation record | Participant run ledger |
|---|---|---|
| Path | `/var/lib/freedom-blades/laboratory/lifecycle.json` | `/var/lib/freedom-blades/laboratory/runs/<run-id>` |
| Directory | `root:freedomlab`, `0750` | `root:freedomlab`, **`3770`** — setgid and sticky |
| File | `root:freedomlab`, `0640` | `ubuntu:freedomlab`, `0640`, created by its own participant |
| Written by | the harness CLI, as root | each participant, for its own run only |
| Read by | all seven, through group read | all seven, through group read |
| Re-sealed by | any participant holding the lock, with **no write permission** | the same |
| Not in `/run` | it must survive reboot | the same |

**Why two objects and not one.** The reservation record is root-written. Six
participants are ordinary users and cannot write it, so accounting for their
effects inside it would mean making the record group-writable — which buys
nothing, because a group-writable record is one any participant can replace
whole. The ledger is a separate group-writable directory instead, and the
reservation record keeps its stricter mode. **Why two and not three:** they
share one schema, one publication path and one re-seal, so there is one set of
rules to get right rather than two that can drift.

**What setgid and sticky do here.** Setgid makes each run entry group-owned so
every participant can read it. Sticky means only an entry's owner may remove or
rename it — the `/tmp` protocol. **Between these seven it constrains nothing**,
because they are the same UID; it is a guard against a future identity split and
against an unrelated user, and it is stated as that rather than as protection
the design relies on.

### 5.5 The record schema — bounded, versioned and parsed

**R3-3's requirement, and the thing revision 3 never wrote down.** A record is a
sequence of appended entries in one file, in a line-oriented format with a
closed field vocabulary per entry kind:

```text
freedom-blades-laboratory-lifecycle
schema=1
begin-entry
sequence=1
kind=first_use
host=oracle-test
target=oracle-test
author=peter duscha, operations owner
at=2026-09-11T08:00:00Z
basis=the host was rebuilt from a fresh image on 2026-09-11
end-entry
end-history
```

| Property | Rule | Why |
|---|---|---|
| Magic line | exact, or refuse `MALFORMED` | bytes from elsewhere are not a history |
| `schema=` | in `{1}`, or refuse `UNSUPPORTED_SCHEMA` | a reader that interpreted a newer record by the meanings it happens to know is guessing |
| Terminator | `end-history` required, or refuse `TRUNCATED` | **this is the truncation detector.** A record whose tail was lost spells a shorter history, and a shorter history can end on an admitting entry |
| Entry fields | exactly the six common fields plus the kind's own, or refuse `MALFORMED` | the schema is **bounded**: an unknown field is a refusal, not something to ignore, so a writer cannot smuggle a claim past a reader |
| Duplicate key | refuse `MALFORMED` | two meanings, and a reader that took the last would be choosing |
| Unknown kind | refuse `MALFORMED` | skipping an unrecognised entry hides the run it describes |
| `host`/`target` | non-empty in every entry, or refuse `MISSING_BINDING` | an unbound record is evidence about an unnamed target, not a wildcard |
| Two entries disagreeing | refuse `CONTRADICTORY` | one file describing two hosts is refused, not reconciled |
| Another host or target | refuse `WRONG_BINDING` | **R3-3.** A history for the same hostname is not a history for another approved target |
| Sequence | `1..N` strictly increasing, or refuse `HISTORY_ORDER` | a gap is a lost entry; a repeat is two statements claiming one place |

**Refusals return no entries at all.** Handing back the prefix that parsed is
precisely how a truncated history gets read as a shorter one, so a refused parse
carries a refusal and nothing else.

**The order rules, stated for this protocol and no wider.** A first use appears
once, at sequence 1. An `admitted` entry follows a first use, a release or an
operator recovery and nothing else. `running`, `released`, `quarantined` and
`recovering` name a reservation this history already admitted. A reservation
that reached `released`, `quarantined` or `operator_recovered` is finished and
its id never appears again. An `operator_recovered` entry names a reservation
this history shows `quarantined`, and the quarantine entry stays where it is.
**The last reservation entry is the current state**, so no reader ever selects
an earlier, more convenient admitting entry. A history these rules refuse
produces no decision input at all.

**This is not a general event-storage system**, and it is deliberately not one.
It has one schema version, ten entry kinds, a fixed field set per kind and no
extension point. Every rule above exists because breaking it produces a history
that would otherwise admit somebody.

**What the record does not carry.** There is **no stored durability flag**, in
any form. A writer that could record *"this was made durable"* would have had to
survive the barrier in order to write it, which is the case that does not arise.

### 5.6 Publication, the restart gap, and the re-seal — R3-1

**The mechanism, stated before the correction.**

1. a rename is visible immediately and durable only when the **containing
   directory's entry** is synchronized **[D]**, [fsync(2)](https://man7.org/linux/man-pages/man2/fsync.2.html);
2. between the rename and that barrier the record is readable and would not
   survive a power loss;
3. the writer's knowledge of which case it is in lives in the writer's memory;
   and
4. a **process-only restart** destroys that memory and leaves the filesystem
   exactly as it was. This is not a power loss and revision 3's model called the
   power-loss operation for both, which is why nothing showed.

So the reader cannot ask whether the record is durable, and **no artefact it can
read answers the question**: an existing name proves a rename happened, and a
stored boolean proves only that somebody wrote a boolean.

**The correction: the reader makes it durable.**

| | Rule |
|---|---|
| **Who** | any participant holding the cooperative lock, as `ubuntu`. Not only the executor |
| **When** | immediately after the lock is taken, and **before the record's content is acted on** |
| **What** | `fsync` on a separately opened `O_RDONLY` descriptor for the record's **containing directory**, and the same for the ledger directory |
| **Which bytes** | **none.** The re-seal covers the parent entry only |
| **Which parent entry** | `/var/lib/freedom-blades/laboratory` for the record; `/var/lib/freedom-blades/laboratory/runs` for the ledger |
| **Permission** | read and search on those directories. **No write permission on anything**, so the root-written record stays root-written and an ordinary participant still discharges the obligation. This is R3-1's permission implication, resolved rather than assumed |
| **Idempotence** | re-sealing an already durable entry is a successful no-op, so the reader never has to know which case it is in |
| **If it fails** | **refuse.** Publish nothing, take nothing, name the record's recovery owner. A failed barrier is an attributable operator recovery, never a reason to continue on the visible name |

**What the re-seal does not establish, said plainly.** It does not establish that
the bytes behind the name are complete. The record's own bytes are the writer's
barrier and the writer issues it *before* the rename, so a visible final name
implies that barrier returned success — **a design inference from the specified
order, not an observation**, and it is falsifiable: a writer that renamed before
synchronizing its bytes would break it, which is why the order is a contract
obligation rather than an implementation detail. A power loss that kept the
entry and lost the bytes leaves a **truncated** record, and §5.5 refuses that
rather than reading the shorter history its surviving prefix spells.

**The reader/writer order under the lock**, once, because every row of §5.7
depends on it:

```text
acquire the lock  →  re-seal the record's parent entry
                  →  re-seal the ledger's parent entry
                  →  read the record's bytes through a descriptor
                  →  parse      (§5.5's bounded schema)
                  →  check order(§5.5's history rules)
                  →  validate   (reservation.validate_lifecycle)
                  →  survey     (§5.11's ledger)
                  →  decide
   [if admitted]  →  publish this participant's own started entry
                  →  issue effects
                  →  observe the completion conditions
                  →  publish completion
   [executor]     →  publish RELEASED
                  →  release the lock
```

**No participant reads before it re-seals, and no participant writes before it
reads.** A reader that acted on content it had not re-sealed is revision 3.

### 5.7 The transition and publication table — every phase, provisioning to reuse

**How to read it.** One row per transition, split across two tables because ten
columns do not fit one. `T-n` is the same transition in both. **Every row is
[P]** — proposed, unbuilt — except where a **[M]** names the model test that
exercises it. Nothing here is **[D]** except the barrier semantics §5.6 cites.

**Table A — actor, custody, bytes and barriers.**

| # | Transition | Actor | Lock custody | Bytes read / written | Identity binding | File barrier | Directory barrier |
|---|---|---|---|---|---|---|---|
| T0 | provision the directories, the lock inode and the ledger directory | operator, root, out of band | none; the lock does not exist yet | none | none yet | — | the provisioning tool's own |
| T1 | initialize the first-use record | operator, root, out of band | none; nobody may be running | writes the whole history, one entry | host **and** approved target, plus attester and basis | `fsync` the temporary's bytes | `fsync` the laboratory directory after `RENAME_NOREPLACE` |
| T2 | take the cooperative lock | any participant, `ubuntu` | acquires it | none | none | — | — |
| T3 | **re-seal** the record's and the ledger's parent entries | any participant, `ubuntu` | **holds it** | none | none | — | `fsync` both parents, `O_RDONLY`, no write permission |
| T4 | read, parse, check order, validate | any participant | holds it | reads the whole record | compares the record's host and target with this run's | — | — |
| T5 | survey the ledger | any participant | holds it | reads every run file | each run file's own host/target | — | — |
| T6 | publish `participant_started` | that participant, `ubuntu` | holds it | writes its own run file, one entry | host, target, participant, identity, declared effects | `fsync` the temporary | `fsync` the runs directory after `RENAME_NOREPLACE` |
| T7 | publish `admitted` | executor, root | holds it | reads the history, writes it plus one entry | host, target, reservation id | `fsync` the temporary | `fsync` the laboratory directory after the rename |
| T8 | publish `running` | executor, root | holds it | same | same | same | same |
| T9 | issue the reviewed effects | executor, root | holds it | none of this record | — | — | §2.3's capture barriers |
| T10 | observe the completion conditions | the participant, and an operator for the executor | holds it | none | — | — | — |
| T11 | publish `participant_completed` | that participant | holds it | reads its run file, writes it plus one entry | as T6, plus the observer's name | `fsync` | `fsync` |
| T12 | publish `released` | executor, root | holds it | reads the history, writes it plus one entry | host, target, reservation, released-at, author | `fsync` | `fsync` |
| T13 | publish `quarantined` | executor, root, on any failure path | holds it | same | same, plus the reason | `fsync` | `fsync` |
| T14 | publish `recovering` | executor or operator, on deadline or crash | held or free | same | same, plus the recovery owner | `fsync` | `fsync` |
| T15 | publish `operator_recovered` | operator | **must hold it** | reads the history, writes it plus one entry | host, target, recovered reservation, reference, author | `fsync` | `fsync` |
| T16 | publish `participant_recovered` | operator | must hold it | reads that run file, writes it plus one entry | run, participant, reference, author | `fsync` | `fsync` |
| T17 | release the lock | the holder | releases it | none | — | — | — |
| T18 | a successor admits from stored evidence | the next participant | acquires it | reads what T12 or T15 wrote | as T4 | — | as T3 |

**Table B — effects, uncertainty, restart and recovery.**

| # | Permitted effects | The uncertain outcome | What a restart observes | Recovery owner | Status |
|---|---|---|---|---|---|
| T0 | create paths and the group | a partially provisioned host | some paths present, some absent; every participant refuses on the absent lock or record | operator; **never a participant** | **[P]** |
| T1 | create exactly one record | **rename succeeded, barrier failed**: visible, not durable | the readable record and no trace of the failure. **This is R3-1** | the next participant's re-seal, or an operator if it fails | **[M]** `test_the_reviewers_reproduction_still_reproduces_against_the_writer`, `test_a_successor_establishes_the_durability_the_writer_could_not` |
| T2 | none | lock unreadable | wait or refuse; an unreadable lock is not an unheld one | — | **[M]** `test_a_concurrent_participant_arriving_during_initialization_waits` |
| T3 | **none. It is a barrier, not a write** | the barrier fails | nothing was taken and nothing published | the record's recovery owner, attributably | **[M]** `test_a_failed_re_seal_refuses_pending_an_attributable_recovery` |
| T4 | none | bytes malformed, truncated, contradictory or wrongly bound | the same refusal, deterministically | operator | **[M]** `test_a_tampered_record_refuses_and_is_never_normalized` (ten cases) |
| T5 | none | a run file unreadable, or a leftover temporary | the run counts as unsettled and blocks | operator | **[M]** `test_an_interrupted_ledger_publication_blocks_and_is_not_cleaned` |
| T6 | **none yet — this precedes the first effect** | published or not | if absent, no effect was issued either; if present, the run blocks until settled | operator | **[M]** `test_the_non_reusable_state_is_persisted_before_the_first_effect` |
| T7 | **none yet — ADMITTED precedes the first effect of any kind** | as T1, at a different entry | `admitted` stands and refuses every successor | operator | **[M]** `test_every_publication_point_carries_the_same_uncertainty` |
| T8 | none yet — RUNNING precedes the first **mutating** step | as T1 | `running` stands and refuses every successor | operator | **[M]** same |
| T9 | the reviewed mutation, capture, materialization, restoration, cleanup | any of §§1–2's failure modes | whatever §2's barriers made durable; the record still says `running` | operator, from §2.2's independent store | **[P]** — needs the mechanism |
| T10 | none | a condition unobserved | the run stays in progress and blocks | operator | **[M]** `test_a_clean_wrapper_exit_and_a_free_lock_are_not_completion_evidence` |
| T11 | none | completion published or not | absent ⇒ the run blocks; present ⇒ it does not | operator | **[M]** `test_clean_completion_admits_the_next_participant` |
| T12 | none | **failed release publication**: renamed, barrier failed | `released` is visible; the successor re-seals it and it survives. If the rename never happened, `running` stands and refuses | the successor's re-seal, else an operator | **[M]** `test_every_publication_point_carries_the_same_uncertainty`, `test_a_release_that_never_reached_its_barrier_still_refuses_a_successor` |
| T13 | none | the crash beat the quarantine | the **previous** entry stands, which refuses. Absence of a quarantine is never an ending | operator | **[M]** in the failed lifecycle trace |
| T14 | none | as T12 | `recovering` refuses; the deadline authorizes nobody | the named recovery owner | **[P]** the deadline path; **[M]** the refusal |
| T15 | none | **interrupted operator recovery**: the recovery entry renamed, barrier failed | the recovery is visible and the successor's re-seal makes it durable. If the history could not be read, the append refuses and **nothing is overwritten** | operator | **[M]** `test_recovery_never_overwrites_a_valid_prior_history`, `test_an_unreadable_history_is_never_replaced_by_a_recovery` |
| T16 | none | as T15 | the started entry stands and the run blocks | operator | **[M]** `test_a_verified_recovery_admits_a_new_run_without_a_dead_end` |
| T17 | none | the holder died instead of releasing | the kernel released the lock. **The record decides, not the lock** | — | **[M]** carried from r3's participant table |
| T18 | whatever its own profile permits | as T4 | as T4 | as T4 | **[M]** `test_a_complete_successful_lifecycle_admits_a_successor_from_stored_evidence` |

**Three consequences the re-review asked to see stated.**

* **Failed release publication is T12 and it is covered.** A release that renamed
  without its barrier is made durable by the next participant's re-seal, and a
  release that never renamed leaves `running`, which refuses.
* **Interrupted operator recovery is T15 and T16, and it cannot overwrite.**
  Every publication re-serializes the prior entries verbatim and appends one, so
  the only difference between the old file and the new is the last entry. A
  history that will not parse refuses the append outright: replacing it would be
  substituting a history this writer invented for one nobody read.
* **Admission failures are T4, T5 and T18**, and each names which of the ten
  refusals it is rather than reporting that something was wrong.

### 5.8 One allowlist of validated lifecycle outcomes, for all seven

Carried from r3 §5.6 and unchanged in substance. Every participant applies
`reservation.validate_lifecycle()` — the function `reservation.admit()` calls —
and proceeds only on a validated outcome in `VALIDATED_LIFECYCLE_OUTCOMES`.

| Outcome | Proceeds | Required coherent shape, **with r4's additions in bold** |
|---|---|---|
| `verified_first_use` | yes | no predecessor state, no predecessor id, no release record, no recovery reference; **the approved target binding; the attester's name; the basis** |
| `released` | yes | predecessor state `RELEASED`; predecessor named; release record bound to this host, target and predecessor; no recovery reference; **the approved target binding; no first-use attestation** |
| `operator_recovered` | yes | predecessor state `QUARANTINED`; predecessor named; recovery reference present; no release record; the requester's own id is not the recovered one; **the approved target binding; the recovery's author** |
| `active` | **no** | predecessor state `ADMITTED` **or** `RUNNING` |
| `recovering` | **no** | predecessor state `RECOVERING` |
| `quarantined` | **no** | predecessor state `QUARANTINED` |
| `unknown` | **no** | unconstrained; it refuses because it is unclassified |
| *anything else, or a malformed value* | **no** | refused as malformed before any comparison |

**The binding is required for every disposition that makes a positive statement
about a run**, not only the admitting three, because a record is about a host
*and* a target and one that says otherwise is about neither.

**Two admission conditions are new in r4** and both apply to all seven:

* the **re-seal** of §5.6 must have succeeded; and
* the **ledger** of §5.11 must hold no unsettled and no unreadable run.

### 5.9 Refusal paths

| Situation | Behaviour |
|---|---|
| Lock file absent | refuse: the host is not provisioned |
| Lock file present, permission denied | refuse: `ubuntu` is not in `freedomlab` |
| `flock` returns `EWOULDBLOCK` | wait or refuse; never `LOCK_NB` in a loop that gives up and proceeds |
| Lock unreadable | refuse. An unreadable lock is not an unheld lock |
| **Re-seal of either parent entry fails** | **refuse, pending an attributable operator recovery. New in r4** |
| Record absent or unreadable | refuse. Initialization is the only way out, and it refuses on a used host |
| Record malformed, truncated, unsupported, contradictory, missing-binding or wrong-binding | refuse, **naming which of the eight it is**. Nothing is normalized |
| Record's entry order is not a history | refuse. No disposition is derived from the tail |
| Record `ADMITTED` or `RUNNING` | refuse and name the reservation and its recovery owner |
| Record `RECOVERING` or `QUARANTINED` | refuse. Participant 6 refuses **especially** |
| Record `RELEASED`, `VERIFIED_FIRST_USE` or `OPERATOR_RECOVERED`, coherent and bound | proceed |
| **Any run unsettled or unreadable in the ledger** | **refuse, every participant, the harness and the reset included. New in r4** |
| **A leftover run-publication temporary** | **refuse and report it. It is not removed automatically** |
| Crash, restart, lock free, record `ADMITTED` or `RUNNING` | **refuse.** No expiry and no free lock authorizes reuse |

### 5.10 Verified first use — a provisioning operation, proposed and unperformed

Carried from r3 §5.8, with three changes.

| | Value |
|---|---|
| Creator | the operator provisioning the host, as root, out of band. Not the harness, not a participant |
| Authority | the maintainer's approval of §7. **It is not approved** |
| Creation rule | exclusive creation: `O_CREAT\|O_EXCL` on the temporary, `RENAME_NOREPLACE` on the final name |
| Durability | bytes synchronized, then rename, then the containing entry synchronized |
| **Binding — changed** | the record names the host **and the approved target**, and initialization **refuses `binding_mismatch`** when either would differ from the approved one. r3 declared this refusal and had no branch that produced it |
| **Evidence — changed** | the attester's **name and basis are written into the record**, travel through the parser, and are **required by the validator**. In r3 they reached neither |
| **`not_durable` — changed** | still refuses, and the record may now be **visible**. r3 said *"nothing is treated as initialized"*, which was true of the writer and not of the filesystem. The successor's re-seal is what closes it |

Refusals and recoveries are otherwise r3's: `already_initialized` (read it),
`prior_use_not_excluded` (**never reinitialize**; establish the predecessor or
rebuild), `interrupted_initialization` (the temporary is reported by absolute
path and not removed), `no_first_use_evidence` (obtain the attestation),
`binding_mismatch` (correct the binding), `not_durable` (above).

### 5.11 Durable in-progress and completion accounting for all seven — R3-2

**The rule, before the table.** Each participant persists its **non-reusable
state before its first relevant effect**, and publishes **reusable completion
only after the conditions below are observed**. An unsettled or unreadable run
refuses every successor, including the harness and the environment reset, until
a recovery is published.

**What is never completion evidence**, and each has produced an incident class
in the reviews that led here:

* a **free lock**. `flock(2)` associates the lock with the open file description
  and the kernel releases it when the holder's descriptors close **[D]** —
  which happens whether the run finished or was killed;
* a **wrapper's exit status**. Its children, its server-side transactions and
  the tree it was halfway through writing do not exit with it;
* an **elapsed deadline**. It moves a run to `RECOVERING` and names an owner; it
  is never takeover authority; and
* an **absent quarantine record**. A crash before one could be written leaves
  the previous entry standing.

| # | Participant | Effects that can outlive the wrapper | Completion evidence — all required | Recovery | Proof obligation, **unperformed** |
|---|---|---|---|---|---|
| 1 | bot suite | rows and temporary schemas in the disposable database; backends holding transactions; fixture trees | the process and every child exited; **no backend attributable to this run remains**; the fixture trees were removed and the removal observed | an operator terminates nothing; residue is reported by name, the test schema is dropped and recreated under an attributed entry | that a backend can be attributed to one run at all |
| 2 | web suite | the same database — finding F-6, which is why the two are serial; application-opened transactions; uploaded fixtures | as row 1 | as row 1; the shared database means either one's recovery is one both wait for | that the two suites' backends are distinguishable on the shared cluster |
| 3 | Foundry tests | `node --test` workers; temporary trees | the runner and every worker exited; the trees were removed and the removal observed | surviving workers are reported and **left alone** until an operator establishes what they are | that the workers are enumerable as children of the runner |
| 4 | synchronization | **a partially replaced tree** — files from two revisions side by side, with transfer temporaries among them | the transfer reported success **and** a whole-tree consistency check against the source revision passed after it **and** no transfer temporary remains | re-run the complete synchronization from the source of truth under an attributed entry | **what that consistency check is, concretely, on the target** |
| 5 | dependency update | a partially updated virtual environment, with a distribution left half-unpacked | the installer reported success **and** an environment consistency check over the locked set passed after it | reinstall the complete locked set under an attributed entry | that the check detects a half-unpacked distribution, not only a missing one |
| 6 | environment reset | **destruction of state — the most dangerous to interrupt**, because its effect is the removal of the evidence an earlier interruption left | every step reported success **and** the post-reset state matched the declared baseline | re-run under an attributed entry, and only after establishing that nothing unresolved was pending. **It never runs while a quarantine or an unsettled run exists** | that the declared baseline is observable at all |
| 7 | harness CLI | the reviewed mutation and its restoration; the disposable root; the recovery store | `release()` returned RELEASED on observed evidence **and** the release entry reached durable storage | the quarantine stays; an operator appends an attributed recovery; the recovered id is never reused | every §9.3 implementation check |

**No exemption is proposed for any participant.** r3's *"a crashed test run is
not a reservation and must not block the host forever"* is withdrawn as stated.
The second half of it is kept and answered differently: a crashed run blocks
until its recovery is **published**, which is a bounded operator action with a
named owner, not an indefinite dead end — and §9's row 22 is the control that
shows a recovered host admitting a new run.

**The reset's exemption in particular is refused.** It was the most tempting one,
because a reset is how an operator would want to clear a mess. It is exactly the
participant that must not run into unresolved evidence, so it is refused
especially rather than granted an exception.

### 5.12 What is repaired in code, and what is only proposed

**Repaired, and this is the whole of it:**

| Finding | Repair | Where |
|---|---|---|
| R3-3 | `LifecycleHistory` carries the approved target, the first-use attester and basis, and the recovery's author; `LIFECYCLE_SHAPES` states for each disposition whether each is required or forbidden; the validator refuses wrong, absent and contradictory bindings | `reservation.py` |
| R3-3 | a bounded, versioned record schema with a serializer and a parser, the history-order rules, and the derivation that carries stored evidence into the shared validator; `BINDING_MISMATCH` gains its enforcing branch | `lifecycle_storage.py` |
| R3-1 | the publication path, the re-seal, and the process-only restart kept distinct from the power loss | `lifecycle_storage.py`, `durability_model.py` |
| R3-2 | the seven participant profiles, the run ledger and the completion rule | `lifecycle_storage.py` |

**Proposed and not built:** the lock adapter, the record writer, the ledger
writer, the re-seal's real `fsync`, the provisioning of every path in §7, and
every permission in it. `reservation.DECISIONS_DO_NOT_PERSIST` and
`ADAPTER_RESPONSIBILITIES` are unchanged and still say that an admitting
decision is not a reservation and that **enforcing anything at all** is
something nothing in this pass implements.

**The models are models.** `lifecycle_storage`'s whole filesystem is a
dictionary in `durability_model`, and `MODEL_LIMITS` travels in every result it
returns. The module makes **no observation of the model's durable-state map**,
because a reader that could ask whether an entry is durable would be a reader
with a fact the mechanism does not have — and
`test_r3_lifecycle.py::test_the_lifecycle_model_makes_no_oracle_observation`
asserts that against the module's syntax tree rather than promising it here.

---

## 6. Exact diff — what would be built, and what it would need

**None of this is built.** The estimates are for review, not for scheduling.

### 6.1 Modules and interfaces

| Module | Change | Size |
|---|---|---|
| `execution/descriptors.py` | **new.** §1.3's inventory: open each directory twice, in the two modes; `fstat`; record; bind the synchronizable descriptor by comparison; hand out by index; refuse an unregistered index | ≈ 260 lines |
| `execution/case_program.py` | new `DIRFD` and `COMPONENT` argument kinds; the four descriptor-relative verbs of §6.2; the `execveat` launch path for X1 | ≈ 260 lines |
| `execution/executor.py` | issue P1/P1b/P2/P4/L3 through the chain; the quiescence gate of §1.6; the pre-check/post-check of §1.4.5 | ≈ 200 lines |
| `execution/materializer.py` | §2.3's ordered capture-and-publish with all five barriers, and §2.4's verify-and-write with its two | ≈ 240 lines |
| `execution/recovery_store.py` | **new.** The independent store of §2.2 | ≈ 200 lines |
| `execution/host_lock.py` | **new.** §5.3's protocol: open existing, `flock`, **re-seal**, read, parse, validate, survey, refuse. **No creation, no unlink** | ≈ 150 lines |
| `execution/lifecycle_record.py` | **new.** §5.4's reservation-record writer, §5.5's codec, §5.6's publication order and re-seal, §5.10's initialization | ≈ 260 lines |
| `execution/run_ledger.py` | **new in r4.** §5.11's per-participant ledger: begin, complete, recover, survey, over the same codec and the same barriers | ≈ 180 lines |
| `cleanup.py` | LAB-1's §8.1 reporting fix; `RECOVERY_PROCEDURE` replaced by §8.2's independent procedure | ≈ 60 lines |
| `plan.py`, `review_manifest.py` | coverage for the six new modules; no new executable | ≈ 30 lines |

**Already written in this pass, and they are models rather than mechanism:**

| Module | What it is |
|---|---|
| `durability_model.py` | the bounded synthetic filesystem, with `restart_process()` added beside `crash()` so a process-only restart is never modelled by calling the power-loss operation. **Planning tier**: its whole filesystem is a dictionary |
| `lifecycle_storage.py` | the record schema, parser, publication path, re-seal, run ledger, the seven profiles, and the connected successor protocol. **Provisions nothing, and reads no live host** |
| `reservation.py` | the shared validator, now carrying the binding and the attributable evidence |

### 6.2 Verbs, arguments and syscalls

```
  "openat":    (DIRFD, OPEN_MODE, COMPONENT)
  "unlinkat":  (DIRFD, COMPONENT)
  "renameat":  (DIRFD, COMPONENT, DIRFD, COMPONENT)
  "fstatat":   (DIRFD, COMPONENT)
```

Unchanged from r3: `DIRFD` is an index into the inherited table and never a
number a caller chooses; `OPEN_MODE` is a closed set; `COMPONENT` is one path
component; verb count **16 → 20**; `BOOTSTRAP_VERBS` unchanged at **2**; no
synchronizable descriptor is ever in a transferred set.

Syscalls newly reached, with r4's additions in bold: `openat(2)` in the four
modes; `mkdirat(2)`; `unlinkat(2)` with `0` and `AT_REMOVEDIR`; `renameat2(2)`
with `RENAME_NOREPLACE` and `0`; `fstatat(2)` with `AT_SYMLINK_NOFOLLOW`;
`fsync(2)` on `O_RDONLY` directory descriptors and `O_WRONLY` file descriptors —
**including the re-seal of §5.6, which is the same call issued by a participant
that holds no write permission**; `execveat(2)` with `AT_EMPTY_PATH`;
`flock(2)`; `ioctl(2)` `FS_IOC_SETFLAGS`/`FS_IOC_GETFLAGS`.

`RENAME_NOREPLACE` requires filesystem support; `rename(2)` lists ext4 from
Linux 3.15 and tmpfs from 3.17 **[D]**. The target's filesystem type is one of
the twelve unconfirmed facts, so this is a **prerequisite to confirm at the
Codex read-only preflight**, not an assumption to carry.

### 6.3 Descriptor transfer

Unchanged from r3. Inheritance across `fork`/`execve` only, `FD_CLOEXEC` cleared
on a declared set starting at descriptor 3, a table naming each entry and its
mode, no `SCM_RIGHTS`, no re-open by path, and **no synchronizable descriptor in
any transferred set**.

### 6.4 Executables, identities and the permission delta

| Surface | Before | After, **if built** |
|---|---|---|
| `plan.PERMITTED_EXECUTABLES` | 22 absolute paths | **20** — `/usr/bin/install` and `/usr/bin/chattr` removed, replaced by syscalls |
| `case_program.VERBS` | 16 | **20** |
| `case_program.BOOTSTRAP_VERBS` | 2 | **2, unchanged** |
| `executor.PERMITTED_RUN_AS` | the identity contract | **unchanged** |
| `sudoers.EXPECTED_COMMANDS` | 2 `Cmnd_Alias` targets | **unchanged** |
| The one `ctypes` exception | `case_program._prctl_get_securebits` | **a second one**: the two ioctls and `execveat` |
| Descriptors opened per run | the chain, one mode | the chain in two modes, **plus one `O_RDONLY` directory descriptor per participant per run for the re-seal**. No new privilege |
| New privileged writer | — | **none** |
| New system group | — | **`freedomlab`**, with `ubuntu` as a member |
| New provisioned paths | — | `/run/freedom-blades` (`0750`), `/run/freedom-blades/laboratory.lock` (`0660`), `/var/lib/freedom-blades/laboratory` (`0750`), `/var/lib/freedom-blades/recovery` (`0700 root:root`), **`/var/lib/freedom-blades/laboratory/runs` (`3770`) — new in r4** |
| New provisioned object | — | `/var/lib/freedom-blades/laboratory/lifecycle.json` (`0640`) |
| New systemd artifact | — | one `systemd-tmpfiles` fragment for the two `/run` entries |
| **New write permission for ordinary participants** | — | **one directory only**: the run ledger. **The reservation record stays root-written, and the re-seal needs no write permission at all** |
| New capability or unit | — | **none** |

**The delta grew again, from eight items to ten**, and the reason is worth
stating because it has now happened three revisions running: specifying the
descriptors revealed `OPEN_MODE`; specifying the storage revealed the initial
record and the directory-barrier preflight; **specifying the reading revealed
the ledger directory and the identity question**. A further specification pass
may reveal more. It is named here rather than presented as a settled cost.

---

## 7. Provisioning and permission changes — required, and unapproved

**None is approved by this document**, and calling the re-seal unprivileged
approves none of them. They are listed so a maintainer can approve or refuse
them as a set.

| # | Change | Why | Approved? |
|---|---|---|---|
| V1 | create system group `freedomlab` | so ordinary participants can open the lock without `sudo` | **no** |
| V2 | add `ubuntu` to `freedomlab` | it is every participant's identity **[A]** | **no** |
| V3 | `systemd-tmpfiles` fragment creating `/run/freedom-blades` `0750 root:freedomlab` and `laboratory.lock` `0660 root:freedomlab` | `/run` is tmpfs; the lock must exist before any participant runs | **no** |
| V4 | create `/var/lib/freedom-blades/laboratory` `0750 root:freedomlab` | the durable reservation record must survive reboot | **no** |
| V5 | create `/var/lib/freedom-blades/recovery` `0700 root:root` | the independent recovery store of §2.2 | **no** |
| V7 | initialize `lifecycle.json` `0640 root:freedomlab` with a verified-first-use record, exclusively, durably, bound to host **and approved target**, on a named operator attestation | §5.10. Without it the fresh-install path cannot reach its successful control | **no** |
| **V9** | **create `/var/lib/freedom-blades/laboratory/runs` `3770 root:freedomlab` — setgid and sticky** | **§5.11. Every participant must be able to publish its own in-progress and completion state, and the reservation record must not become group-writable to allow it. New in r4** | **no** |
| V6 | confirm the filesystem under `R` supports `RENAME_NOREPLACE` | §6.2; one of the twelve unconfirmed facts | **preflight**, unperformed |
| V8 | confirm that `fsync` on an `O_RDONLY` directory descriptor behaves as the containing-entry barrier on the target's filesystem | §2.3 and **§5.6, which now depends on it for every participant rather than only the executor** | **preflight**, unperformed |
| **V10** | **confirm that all seven participants really run as `ubuntu`, and record whether separating their identities is wanted** | **§5.2 and §5.4. The identity is an [A] that the whole ledger's attribution rests on, and separating the seven is the only thing that would make the file modes a barrier between them rather than an accident guard. New in r4** | **preflight and a maintainer decision**, unperformed |

**V10 is a decision request as well as a fact.** If Peter wants the seven
separated, §5.4's modes and §6.4's delta both change and this contract needs
another revision. If he does not, the honest statement is §5.2's: the modes
guard against accidents and not against the participants.

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


---

## 9. The bounded proof matrix

### 9.1 How to read a row

**Model rows are proposal-model tests, not implementation proof.** The model's
state is split into what a reader sees now and what would survive a power loss,
and **no modelled participant can read the second one** — that separation is the
whole of R3-1 and `test_the_lifecycle_model_makes_no_oracle_observation` asserts
it against the module's syntax tree. A passing row establishes that the proposed
rule is constructible and falsifiable. It establishes **nothing** about the
built mechanism, about Linux, or about `oracle-test`, and **nothing here may be
cited as evidence for EH-R16-1**.

Rows marked **[M]** are written and pass in this tree. Rows marked **[P]** are
specified and have no test, because they need the mechanism.

### 9.2 The matrix

Rows 1–12c are carried from r3 unchanged and are not restated; they cover effect
ownership, the publication and restoration barrier graphs, the removal
post-check and the descriptor modes, and their negative controls (3, 8b, 11b,
12c) still fail revision 2's mechanism and hold under this one.

| # | Scenario | Expected | What it falsifies | Status |
|---|---|---|---|---|
| 13 | lock file absent | every participant refuses | that a participant may create it | **[P]** |
| 14 | lock held by another participant | wait or refuse | that `LOCK_NB` failure may be walked past | **[M]** |
| 15 | lock free, record `RUNNING` | refuse | that a free lock is a released host | **[M]** |
| 15b | lock free, record `ADMITTED` | refuse | r2 §5.6's denylist | **[M]** |
| 15c | record unknown, malformed, incomplete or contradictory | refuse, all seven | that an ordinary participant may read more loosely than the executor | **[M]** |
| 16 | lock free, record `RELEASED`, bound | proceed | that the refusals refuse everything | **[M]** |
| 16b–16d | first-use initialization: fresh, previously used, interrupted at each point | as r3 | that the fresh-install path has no reachable successful control | **[M]** |
| 17 | quarantine present, participant 6 | refuse, and **especially** | that a reset is a recovery | **[M]** |
| 18 | unknown surviving writer at admission | refuse and name it; never kill it | that an inventory may be completed by force | **[M]** |
| **19** | **initialization renames and its directory barrier fails, then a process-only restart** | the record is visible, its entry is not durable, and a retry says `already_initialized` | **nothing — it is the reproduction.** It is asserted so that a change which quietly removed the window fails here | **[M]** `test_the_reviewers_reproduction_still_reproduces_against_the_writer` |
| **20** | **a process restart and a power loss, from the same state** | the restart keeps the visible record; the power loss removes it | **that the two are one event.** r3's model called `crash()` for both | **[M]** `test_a_process_restart_and_a_power_loss_are_different_events` |
| **21** | **revision 3's successor reads the visible record, then a power loss** | it **admits**, and the record is then gone, leaving a used host with no history and no way back | **the corrected property. The negative control** | **[M]** `test_the_revision_3_protocol_admits_on_a_record_a_power_loss_removes` |
| **22** | **revision 4's successor re-seals, then a power loss** | the record survives and the successor still admits | that the re-seal is decorative | **[M]** `test_a_successor_establishes_the_durability_the_writer_could_not` |
| **23** | **the re-seal fails** | refuse, publish nothing, name the recovery owner | that a failed barrier may be walked past on a visible name | **[M]** `test_a_failed_re_seal_refuses_pending_an_attributable_recovery` |
| **24** | **a concurrent participant arrives during initialization** | wait or refuse; it does not re-seal somebody else's half-published record | that the re-seal is a repair anyone may attempt at any time | **[M]** `test_a_concurrent_participant_arriving_during_initialization_waits` |
| **25** | **failure injected at each of the three points of the release publication**, then restart | the successor's re-seal makes whatever is visible survive a power loss; a release that never renamed leaves `running`, which refuses | that only initialization has this window | **[M]** `test_every_publication_point_carries_the_same_uncertainty`, `test_a_release_that_never_reached_its_barrier_still_refuses_a_successor` |
| **26** | **an operator recovery appended over a quarantine** | every earlier entry is byte-identical afterwards, and the quarantine entry is still there | that a recovery may rewrite the history it recovers | **[M]** `test_recovery_never_overwrites_a_valid_prior_history` |
| **27** | **a recovery attempted over a history that will not parse** | refuse. Nothing is written | that an unreadable history may be replaced by one the writer invented | **[M]** `test_an_unreadable_history_is_never_replaced_by_a_recovery` |
| **28** | **a truncated history whose surviving prefix ends on an admitting `released` entry** | the prefix **is** shown to admit, and the truncated record **refuses** | **that a reader may select the convenient prefix.** The control that makes the terminator load-bearing | **[M]** `test_a_partial_history_refuses_rather_than_selecting_an_earlier_entry` |
| **29** | **wrapper death with a surviving child, an unsettled server-side transaction, a partial synchronization, an interrupted dependency update and an interrupted reset** | one stated condition unobserved in each, and **all seven** successors refuse | **r3 §5.5's "the next suite proceeds"** | **[M]** `test_an_uncertain_predecessor_blocks_every_successor`, five cases × seven participants |
| **30** | **a clean wrapper exit, status 0, lock released, no condition observed** | completion **refuses** | that a wrapper's fate is its effects' fate | **[M]** `test_a_clean_wrapper_exit_and_a_free_lock_are_not_completion_evidence` |
| **31** | **clean completion on observed conditions** | published, and all seven then proceed | that the ledger refuses everything | **[M]** `test_clean_completion_admits_the_next_participant` |
| **32** | **an interrupted run, then an unattributed recovery, then an attributed one** | the unattributed one refuses; the attributed one admits a new run | **that an interruption is an indefinite dead end** | **[M]** `test_a_verified_recovery_admits_a_new_run_without_a_dead_end` |
| **33** | **a recovered run's own identity reused** | exclusive creation refuses it | that a recovery may be resumed | **[M]** `test_a_recovered_runs_own_identity_is_never_reused` |
| **34** | **a run-publication temporary left by an interrupted start** | reported, not removed, and it blocks | that a temporary may be cleaned by the next participant | **[M]** `test_an_interrupted_ledger_publication_blocks_and_is_not_cleaned` |
| **35** | **a first-use history read against a different approved target** | refuse, all seven | **R3-3's reproduction, which admitted 7/7 twice before this pass** | **[M]** `test_a_first_use_history_for_another_target_refuses` |
| **36** | **initialization bound to an unapproved target** | refuse `binding_mismatch`; no record is created | **that `BINDING_MISMATCH` is unreachable**, which r3 left it | **[M]** `test_an_initialization_bound_to_the_wrong_target_refuses` |
| **37** | **ten stored-field tampers**: wrong target, emptied binding, removed basis, added field, truncated tail, unclosed entry, unsupported schema, missing magic, unknown kind, renumbered sequence | each refuses, with its own refusal value, and returns no entries | that a reader normalizes what it can read | **[M]** `test_a_tampered_record_refuses_and_is_never_normalized` |
| **38** | **a first use with no attester, or no basis; a recovery with no author; a released record also carrying an attestation** | each refuses at the **shared validator**, not only at the parser | that the binding is checked in one place and may be checked in one place | **[M]** `test_reservation.py`, the R3-3 section |
| **39** | **the complete successful lifecycle** — initialize, admit, start, run, complete, release, restart, admit a successor | every step reads the bytes the previous one wrote; the successor admits on the stored release | **that the model's successes are constructed rather than read** | **[M]** `test_a_complete_successful_lifecycle_admits_a_successor_from_stored_evidence` |
| **40** | **the complete failed lifecycle** — initialize, admit, start, run, die, refuse, quarantine, recover, admit | the same path through interruption and attributable recovery; the recovered reservation is never resumed | that the failure path is described rather than exercised | **[M]** `test_a_complete_failed_lifecycle_refuses_then_recovers_then_admits` |

**Rows 21, 28, 30 and 35 are the ones that must fail revision 3's protocol and
hold under this one.** A matrix in which revision 3 also passes is a matrix that
is not testing the correction.

### 9.3 The implementation checks that would establish the real properties

**None of these has been performed, and this pass ran no real filesystem
durability drill.** They belong to the eventual implementation review and the
separately authorized target work.

| # | Check | Why a model cannot stand in |
|---|---|---|
| I1 | that an `O_PATH` descriptor really refuses `fsync` with `EBADF`, and the separately opened `O_RDONLY` directory descriptor really accepts it | the model refuses by construction. The kernel is the authority |
| I2 | that the target filesystem implements `fsync` on a directory as the containing-entry barrier | filesystem behaviour; preflight **V8** |
| I3 | that the target filesystem supports `RENAME_NOREPLACE` | preflight **V6** |
| I4 | that a real power loss after a successful publication leaves the parent listing the entry | a modelled crash is an assignment |
| I5 | that a real restoration interrupted between rename and barrier leaves the destination at its previous content | same |
| I6 | that the inherited descriptor table contains exactly the declared entries with the declared modes | the model hands out indices |
| I7 | that `execveat(…, AT_EMPTY_PATH)` executes the reviewed payload under every disposable identity | needs identities, payload and interpreter, none provisioned |
| **I8** | **that a participant holding only read and search on the record's directory can really `fsync` it** — that the re-seal needs no write permission on the target kernel and filesystem | **§5.6 rests on it for all seven participants, and it is the single assumption that decides whether the correction is implementable as specified** |
| **I9** | **that each participant's completion condition is observable at all** — a backend attributable to one run, a whole-tree consistency check, a half-unpacked distribution, a post-reset baseline | **§5.11 names five of these and none is confirmed. A completion condition nobody can observe is a run that never settles** |
| **I10** | **that all seven participants run as `ubuntu`** | preflight **V10**. The ledger's attribution rests on it |

---

## 10. Assumptions, and what this document does not do

**Every [A] in one place.** `oracle-test`'s participants all run as `ubuntu` —
now preflight item **V10** rather than a carried assumption; `ubuntu` holds
passwordless `sudo`; `/run` is a tmpfs; `/opt/freedom-blades/evidence`,
`/var/lib/freedom-blades/recovery` and `/etc/postgresql/16/main` are root-only;
host administrators are trusted to obey the reservation and are **not prevented
from ignoring it, and are not claimed to be**; the filesystem under `R` is
unconfirmed, with `RENAME_NOREPLACE` support and the directory-barrier semantics
with it; and **that each participant's completion condition is observable**,
which §5.11 names per participant and I9 collects. None was verified on the
target by this document, and no host was inspected.

**A power loss may retain unsynchronized changes.** The model discards
everything no barrier made durable, which is the *worst* case and not a promise
about Linux. A real power loss may leave more than the model does — it may even
leave everything. Nothing in this contract may be read as the claim that Linux
guarantees the model's outcome; the barriers are specified so that the worst
case is survivable, and `MODEL_LIMITS` says the manual page wins wherever the
model and it disagree.

**It accepts nothing.** It approves no digest, populates none of the twelve
unconfirmed target facts, authorizes no host action, no SSH, no synchronization,
no provisioning, no database operation and no execution. It does not clear the
operational-ineligibility control, does not move `is_executable`, and does not
reduce the three C-7 cases' unresolved status.

EH-R16-1, PR-20260910-1/2/3, the September 10 findings, the six September 11
findings, the four September 11 re-review findings and the three R3 findings
remain **Open** until a reviewer says otherwise. Package 5.0 remains **not
ready**, P5.0-R5 **Blocking**, OD-62 **Open**.

**The next step is Codex's technical re-review of this lifecycle**, then Peter's
decision on the §7 provisioning and permission delta — now ten items — on V10's
identity question, and on LAB-1's classification. Implementation review precedes
the later read-only target preflight, which precedes a separate execution
decision. **Passing tests advance none of those gates.**
