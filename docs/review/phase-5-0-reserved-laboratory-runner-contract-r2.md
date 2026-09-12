# Package 5.0 — runner contract, revision 2

> **SUPERSEDED, 2026-09-11.** This revision is superseded in its entirety by
> [`phase-5-0-reserved-laboratory-runner-contract-r3.md`](phase-5-0-reserved-laboratory-runner-contract-r3.md),
> which answers the September 11 re-review's findings
> [PR-20260911-R2-2, -R2-3 and -R2-4](project-review-2026-09-11-r2.md).
> **The text below is preserved unchanged as the submission that review
> answered.** It is history, not the proposal; where the two disagree, r3 is the
> proposal.
>
> **Erratum — the four statements this revision made that do not hold.**
>
> 1. **§1.3, §1.4.2 P2 and §1.4.4 M1 assign `O_PATH` to descriptors the document
>    then requires `fsync` on.** `fsync(bin_fd)` and `fsync(pgconf_fd)` cannot
>    operate on an `O_PATH` descriptor. The proposed normal installation failed at
>    its own directory durability barrier and restoration failed the same way
>    after replacing a destination. Corrected in r3 §1.3, which gives every
>    descriptor its open flags, owner, lifetime, permitted uses and transfer
>    policy, and obtains a separate `O_RDONLY` descriptor bound by comparison.
> 2. **§2.3 omits the recovery parent's durability barrier.** A newly created
>    `<run-id>` directory must have its entry in the recovery parent synchronized
>    before configuration mutation is permitted; synchronizing the child's
>    contents does not make that entry durable. Corrected in r3 §2.3, whose
>    barrier graph is complete and ordered.
> 3. **§1.4.5 steps 2–3 and §9 row 3 overclaim the post-unlink check.** It
>    observes whether a name exists. It cannot establish which object `unlink`
>    removed and cannot report a replacement's identity. Corrected in r3 §1.4.5
>    and §9 row 3.
> 4. **§5.6–§5.7 omit `ADMITTED` and never initialize a first-use record.** The
>    ordinary participants had a denylist weaker than the executor's rule, and the
>    documented fresh-install path could not reach its successful control.
>    Corrected in r3 §5.6–§5.8.
>
> Nothing else in this document is withdrawn by this notice, and its concessions
> in §1.1 stand. r3 remains **submitted for technical review, not accepted and
> not implemented**.

Date: 2026-09-11. Author: Claude. Change record: C-P5.0-LAB-1.

**Status: submitted for Codex technical review. Not accepted, not implemented,
and no execution is authorized.**

**This revision supersedes
[`phase-5-0-reserved-laboratory-runner-contract.md`](phase-5-0-reserved-laboratory-runner-contract.md)
in its entirety.** That document is preserved unchanged as the submission the
September 11 review answered; where the two disagree, this one is the proposal
and the earlier one is history. It answers Blocking findings **PR-20260911-1**
and **PR-20260911-2** and Important finding **PR-20260911-6**, and it carries the
proposed repair for **LAB-1**.

It is one concrete preferred mechanism with a complete operation table. It is not
a second architecture survey: the reserved-laboratory direction stands, VM work
stays deferred, and ADR 0011 stays Proposed.

Nothing here repairs **EH-R16-1**. It remains Open, the harness retains its
unconditional real-execution refusal (`reservation.REAL_EXECUTION_REFUSAL`), and
a reserved host does not close it — §1.1 says why in the finding's own terms.

---

## 0. How to read a claim in this document

Three kinds of statement appear below and they are not interchangeable. Every
row and paragraph that makes a technical claim is one of them, and the review
found that the previous revision blurred the second into the first.

| Label | What it means | How it may be checked |
|---|---|---|
| **[D] documented** | A semantic the primary manual page states. Verified against the page installed on this workstation, `man-pages 6.7`, and cited by page. | read the cited page |
| **[P] proposed** | A guarantee this design would provide *if* it were built and *if* its prerequisites hold. Nothing below is built. | review the argument; then the model tests of §9 |
| **[A] assumed** | An operational premise nobody has verified on the target, or a trust statement about people. | it is not checked here, and §10 lists every one |

The twelve unconfirmed target facts remain unconfirmed and none is populated by
this document. Every **[A]** below is a statement about the design's premises,
not an observation of `oracle-test`.

### 0.1 What the reservation changes, and what it does not

Unchanged from revision 1 and restated because every row below depends on it:

| | Before the reservation | After it |
|---|---|---|
| An unrelated cooperating writer (a test run, a sync, a dependency update) substitutes an object mid-run | possible, and undetected | excluded by the lock plus the pre-admission inventory **[P]**; a detected violation invalidates the affected evidence |
| A host administrator substitutes an object mid-run | possible | still possible. Trusted not to; not prevented, and not claimed to be **[A]** |
| **This run's own experimental writers** substitute an object mid-run | possible | **still possible.** This is EH-R16-1, and §1 is the whole of this document's answer to it |

---

## 1. Effect ownership — PR-20260911-1

### 1.1 What the review established, conceded before the replacement is presented

Four claims in revision 1 §§5 and 9.2 do not hold, and the mechanism below is
built on their negations rather than around them.

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
   says nothing at all about the identity of the source entry, so it cannot bind
   a source to a previously observed inode.
4. **A descriptor local to one case-program invocation cannot cover a chain that
   spans the run.** The existing boundary launches each step as a separate
   process (`tools/phase_5_0_evidence/execution/boundary.py:841`), and revision 1
   specified `DIRFD` as an index into descriptors *the program opened itself in
   this invocation*. Those two statements are incompatible, and revision 1 made
   both.

The consequence is the one the review drew: **retaining a descriptor can support
a remedy; the comparison revision 1 proposed is not that remedy.** What follows
is a different mechanism.

### 1.2 The three protections, and which one covers each effect

There is no single syscall that binds every effect to an object. There are three
mechanisms with different reach, and the contract's job is to say which one
covers each effect and what remains uncovered.

| | Protection | What it binds | What it cannot bind |
|---|---|---|---|
| **B1** | **Exclusive creation.** `mkdirat`/`openat` with `O_CREAT\|O_EXCL\|O_NOFOLLOW`. Success proves nothing existed at that name, so the object is this run's by construction. | the created object's identity, absolutely | nothing about the object *after* creation |
| **B2** | **Descriptor-bound effect.** Obtain a descriptor for the final object first, verify it, then issue the effect on the **descriptor** — `fchown`, `fchmod`, `fsync`, `ftruncate`, `pwrite`, `ioctl(FS_IOC_SETFLAGS)`, `execveat(…, AT_EMPTY_PATH)`. | the object the effect lands on, exactly | the interval between the lookup that produced the descriptor and the `fstat` that verified it |
| **B3** | **Exclusion.** Issue the effect only while no experimental process exists, verified by the three quiescence observations of §1.6. | who else can be writing during the effect | a host administrator **[A]**; and it is an operational premise, not a technical one |

**Every lookup interval that B1 and B2 cannot close is closed by B3 or the effect
is refused.** That is the rule this section exists to state, and §1.4 applies it
row by row.

### 1.3 Descriptor custody — one owner, inheritance only

**The owner.** One long-lived privileged process, the executor, is the sole
holder of the descriptor chain for the whole run. It is created before the first
effect and it does not exit until cleanup has classified §2.13.2b state. There is
exactly one such process per reservation.

**How the chain is built.** `R` is opened once, at the moment of its exclusive
`mkdir`, with `O_PATH|O_NOFOLLOW|O_DIRECTORY`. Every subsequent directory is
opened relative to its parent's descriptor with the same flags, and `fstat`ed
once. The chain is a list of `(component, dirfd, st_dev, st_ino)` and it is
walked **once**; no path string is ever re-resolved from `/`.

**What an `O_PATH` descriptor may and may not do [D].** `open(2)` lists the
permitted operations: `close`, `fchdir` on a directory, `fstat`, `fstatfs`,
duplication, descriptor-flag get/set, `F_GETFL`, passing as the `dirfd` argument
of the `*at()` calls, and passing over a Unix socket with `SCM_RIGHTS`. It
states equally explicitly that `read`, `write`, `fchmod`, `fchown`, `ioctl` and
`mmap` **fail with `EBADF`**. Revision 1's proposal to change filesystem flags
through a retained descriptor is therefore wrong as written if that descriptor is
`O_PATH`: the flag ioctls need a real `O_RDONLY` descriptor. §1.4 row P4 uses
one, and that is a permission the design must account for rather than assume.

**Custody across process invocations.** Descriptors are transferred by
**inheritance across `fork`/`execve` and by nothing else**. The executor clears
`FD_CLOEXEC` on exactly the descriptors a given step needs, in a declared order
starting at descriptor 3, and passes the step a table naming each one. The case
program's `DIRFD` argument kind is an index into that table and into nothing
else. A step that needs a descriptor it was not given **refuses**; it does not
open a path to obtain one. This replaces revision 1's per-invocation `DIRFD`,
which could not span the run.

`SCM_RIGHTS` over a Unix socket is documented **[D]** and is *not* proposed: it
would require a socket, a protocol and a second trust decision about who may
connect to it, and inheritance already covers a parent-launched child.

**Custody across privilege transitions.** A descriptor survives `execve` when
`FD_CLOEXEC` is clear, and it survives a `setpriv`/`capsh` credential drop
because the drop changes credentials, not the descriptor table. Two consequences,
and the second is the one that constrains the design:

* the dropped identity **cannot re-open by path** what it was given by
  descriptor, if the path's permissions forbid it; and
* the dropped identity **can use the descriptor it was given**. A descriptor
  handed to an experimental identity is therefore a capability granted to that
  identity for the lifetime of that process. **[P]**

So the rule is: the executor hands an experimental step only the descriptors
whose reach is intended for it, each case names them among its writable objects
(§4.3 of revision 1, retained), and a case whose descriptor set is not enumerated
is not admissible. Experimental writers are accounted for here separately from
administrators: an administrator is trusted **[A]**, an experimental identity is
**not**, and §1.6's quiescence is what keeps the second out of the lookup
intervals the first is merely trusted not to enter.

### 1.4 The operation inventory

`R = /opt/freedom-blades/evidence/<run>`. For each effect: the exact object or
bytes, the operation that resolves it, whose descriptor and for how long, the
prerequisite, and what enforces that prerequisite **immediately before** the
effect. `Protection` names B1/B2/B3 from §1.2.

The first column's identifiers are revision 1's, so the two documents can be read
side by side.

#### 1.4.1 Creation

| # | Effect | Object / bytes | Resolution | Descriptor owner and lifetime | Prerequisite | Enforcement immediately before the effect | Protection |
|---|---|---|---|---|---|---|---|
| C1 | create `R` | the directory `R` | `mkdirat(evidence_dirfd, "<run>", 0700)`, exclusive | executor opens `R` `O_PATH` immediately after; held for the whole run | `R` does not exist | `EEXIST` is the refusal. Success **is** the ownership proof | **B1** |
| C2 | record `R`'s identity | `R` | `fstat(root_fd)` | the same descriptor | C1 succeeded | the pair `(st_dev, st_ino)` is recorded once and every later `openat` is relative to this descriptor | **B1** |

**What C2 is not.** It is not a later detector of `R`'s replacement. Re-`fstat`ing
`root_fd` later compares the descriptor with itself and always agrees — §1.1(1).
Replacement of the *pathname* `R` is detected only by `fstatat(evidence_dirfd,
"<run>", AT_SYMLINK_NOFOLLOW)` against the recorded pair, which is a different
call on a different descriptor, and even that is detection rather than
prevention. `/opt/freedom-blades/evidence` is root-only **[A]**, so the exposure
is administrator-only.

#### 1.4.2 Provisioning

| # | Effect | Object / bytes | Resolution | Descriptor owner and lifetime | Prerequisite | Enforcement immediately before the effect | Protection |
|---|---|---|---|---|---|---|---|
| P1 | create `R/bin`, `R/before`, `R/journal`, `R/probe`, `R/probe-ro` | five directories | `mkdirat(root_fd, name, mode)`, exclusive, one call per name — **replacing `install -d <path>`** | executor opens each `O_PATH` on success; held for the run | `root_fd` is the descriptor C1 created | exclusive creation: an existing entry is `EEXIST` and refuses | **B1** |
| P2 | install the reviewed case program | the reviewed bytes, held in memory | `openat(bin_fd, ".case-program.tmp", O_CREAT\|O_EXCL\|O_WRONLY\|O_NOFOLLOW, 0500)`; `write` the held buffer; `fchown`; `fchmod 0555`; `fsync`; `renameat2(bin_fd, ".case-program.tmp", bin_fd, "case-program", RENAME_NOREPLACE)`; `fsync(bin_fd)` — **replacing `install -m 0555 src dst`** | `bin_fd` from P1, held for the run; the payload descriptor is opened here and held for the run | the source bytes digest to `materialization.REVIEWED_DIGESTS` | the bytes written are the bytes digested, from one buffer. `O_EXCL` proves the temporary name was free; `RENAME_NOREPLACE` proves the final name was free **[D]** | **B1 + B2** |
| P3 | create the four disposable identities | `/etc/passwd`, `/etc/group` | by name, through `useradd`/`groupadd` | — | the names are not existing production identities | `targets.validate_account_name` against the approved target | *name-resolved by nature*; see below |
| P4 | set `+i` on the seal, `+a` on the journal | one file each under `R/journal` | `openat(journal_fd, name, O_RDONLY\|O_NOFOLLOW)`; `fstat`; compare with the recorded pair; `ioctl(fd, FS_IOC_SETFLAGS)` on **that descriptor** — **replacing `chattr +i <path>`** | the file descriptor lives for this effect only; `journal_fd` for the run | the file is the object the creating step recorded | the flag change lands on the inode the descriptor holds, so a replacement of the *name* after the check cannot receive the flag | **B2 + B3** |

**P2's real replacement of `install`.** Revision 1 named four new verbs and left
`install` in place; the review's objection was that four verb names are not an
implementation contract for the effects `install` performs. The replacement above
is stated as the sequence of syscalls, and it removes `/usr/bin/install` from the
provisioning path entirely for `R/bin`. `install` remains only where §1.4.5's
restore uses it, and §2 replaces it there too.

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

Superseded by §2, which is the independent-recovery contract. The rows are stated
there with their durability, because PR-20260911-2 is about exactly the property
a table row cannot carry.

#### 1.4.4 Materialization and experiments

| # | Effect | Object / bytes | Resolution | Descriptor owner and lifetime | Prerequisite | Enforcement immediately before the effect | Protection |
|---|---|---|---|---|---|---|---|
| M1 | write the reviewed `pg_hba.conf`/`pg_ident.conf` | reviewed bytes, held in memory | `openat(pgconf_fd, "<name>.tmp", O_CREAT\|O_EXCL\|O_WRONLY, 0640)`; write; `fchown`; `fsync`; `renameat2(pgconf_fd, tmp, pgconf_fd, name, 0)` | `pgconf_fd` = `/etc/postgresql/16/main` opened `O_PATH` once, held for the run | §2's capture is durable and verified | the capture's durability is re-read and re-verified; a failure refuses **before** M1 | **B2**; destination parent is root-only **[A]** |
| M2 | reload and observe the mapping in force | server state | — | — | M1 succeeded | post-reload control connection | — |
| X1…Xn | run the reviewed case program under `E1 … E8` | the payload inode P2 installed; subjects under `R` | `execveat(interp_fd, "", ["python3.12", "-I", "-S", "/proc/self/fd/<payload>", …], envp, AT_EMPTY_PATH)` | `interp_fd` and the payload descriptor are held by the executor for the run and inherited by the step | the interpreter matches the 2026-09-06 Option B preflight on path, version and executable SHA-256; the payload descriptor's `fstat` matches P2's record | both the interpreter and the script are reached through descriptors, so a replacement of either **pathname** between preflight and execution cannot be executed | **B2** |

**Why X1's payload use is now an effect on a retained object.** Two documented
facts make it work. `execveat(2)` executes the file the descriptor refers to when
`pathname` is empty and `AT_EMPTY_PATH` is set, and the descriptor may be one
obtained with `O_PATH` **[D]**. And `/proc/self/fd/N` is a symbolic link to the
object the descriptor refers to, so opening it reaches that object rather than
re-resolving the original path **[D]**, which is what lets the interpreter read
the reviewed script without a second pathname lookup.

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

#### 1.4.5 Cleanup

| # | Effect | Object / bytes | Resolution | Descriptor owner and lifetime | Prerequisite | Enforcement immediately before the effect | Protection |
|---|---|---|---|---|---|---|---|
| L1 | restore the pre-change configuration | the bytes §2's record binds | §2.4's verify-and-write over a held buffer | `pgconf_fd`, held for the run | §2's record verifies against the retained copy | the buffer digested is the buffer written; there is no second pathname read between check and write | **B2** |
| L2 | reload and verify restoration in force | server state | — | — | L1 succeeded | post-reload observation; unverified ⇒ S-B | — |
| L3 | clear flags, then remove this run's objects, one named object at a time | objects under `R` | `openat(parent_fd, name, O_RDONLY\|O_NOFOLLOW)`; `fstat` against the recorded pair; `ioctl(FS_IOC_SETFLAGS)` to clear; then `unlinkat(parent_fd, name, 0)` or `AT_REMOVEDIR`; then `fstatat(parent_fd, name, AT_SYMLINK_NOFOLLOW)` to confirm absence | each parent's descriptor, held for the run | each object was created by this run, and quiescence holds | flag clearing is **B2**. The removal is **not bindable** — see below | **B2** for the flag; **B3 + detection** for the removal |
| L4 | classify §2.13.2b state | — | — | — | L1–L3 attempted | `cleanup.classify_cleanup` | — |

**L3 is the honest row, and it is the one the review will judge this document
by.** There is no `funlink`. `unlinkat` resolves its final component at the time
of the call **[D]**, and no flag on it binds that component to a previously
observed inode. So removal cannot be made inode-bound by any syscall available
here, and this contract does not claim otherwise.

What it proposes instead, in order:

1. **Exclusion.** L3 runs only inside a verified quiescence window (§1.6). No
   experimental process exists, so the only writers to the parent are the
   executor and an administrator **[A]**.
2. **Pre-check.** `openat` + `fstat` against the recorded pair. A mismatch
   refuses before the removal, and the run reports a detected substitution.
3. **Post-check.** After the `unlinkat`, `fstatat` on the same name. If the name
   still resolves, or resolves to a different object, the removal removed
   something other than the intended entry and the run reports it as a detected
   substitution and reaches state S-B.
4. **Refusal.** If quiescence cannot be established, L3 does not run. The objects
   are reported as residue by absolute path, §2.13.2b state is **S-B**, and the
   next invocation refuses — which is the existing accepted behaviour and is
   preferable to a removal issued into an unknown state.

Steps 2 and 3 are **detection**. Step 1 is the prevention, and it is an
operational exclusion over experimental identities rather than over
administrators. Saying this plainly is the point: revision 1 described a
comparison as a remedy, and the review was right that it was not one.

### 1.5 Which effects each finding's coverage claim actually rests on

Revision 1 claimed §9.2 covered P1, P2, P4, X1 and L3. Corrected:

| Row | Revision 1 claimed | This revision proposes | Residual |
|---|---|---|---|
| P1 | descriptor comparison | **B1**, exclusive `mkdirat` | none for creation |
| P2 | descriptor comparison | **B1 + B2**, `O_EXCL` + held buffer + `RENAME_NOREPLACE` | in-place mutation of the source before the digest; §2.4's rule applies |
| P4 | descriptor comparison | **B2** with a real `O_RDONLY` descriptor, **B3** for the lookup | the lookup interval, covered by quiescence or refused |
| X1 | descriptor comparison | **B2** via `execveat` + `/proc/self/fd/N` | in-place content mutation of a stable inode |
| L3 | descriptor comparison | **B2** for the flag; **B3 + detection** for the removal | the removal's final-component lookup, **not bindable** |

### 1.6 Quiescence — the three observations, and what they cost

Before any effect that relies on **B3**, three observations, none defaulting to
true:

1. every process the case started has exited — observed, not inferred from the
   parent's exit status;
2. every server-side transaction the case opened has settled. A `psql` client
   exiting says the client stopped waiting; and
3. no transient unit the case created is still active.

`reservation.ReleaseEvidence` carries the first two as `bool | None`, and after
the September 11 repair it carries the residue search as a `ResidueObservation`
with an explicit *not made* value, so *"not checked"* and *"checked and false"*
stay apart. `tests/phase_5_0_evidence/test_reservation.py` covers the orphaned
child, the delayed transaction and the interrupted recovery as separate injected
cases.

**The cost, stated.** B3 serializes the run: no effect that depends on it may
overlap a case process. Cases that require concurrency keep it *inside* the case,
as revision 1 §4.3 already required, and the executor's B3-dependent effects sit
between cases and never during one.

### 1.7 Refusal, and what survives a refusal

| Situation | Behaviour | Where |
|---|---|---|
| An effect's object cannot be shown to be the one the prerequisite names | **refuse before the effect** | §1.4; **not implemented** |
| Quiescence cannot be established before a **B3** effect | refuse the effect and every dependent effect; report; state S-B | §1.6; **not implemented** |
| A substitution is detected before or after an effect | refuse every subsequent dependent effect; report the original and replacement identities; state S-B | §1.4.5; **not implemented** |
| The configuration recovery basis cannot be established | **refuse the configuration mutation entirely** | §2.5; **not implemented** |
| Cleanup cannot complete | S-B, exit 3, residue named by absolute path, next invocation refuses | `cleanup.classify_cleanup` — implemented |
| Cleanup state uncertain | S-B, and the executor refuses the next run *more* firmly | `executor._refuse_when_blocked` — implemented |
| A pre-existing object is found where a subject would be created | preserve it, never remove it, report it as `preserved` | `CleanupOutcome.preserved` — implemented |
| Reservation release cannot establish its conditions | **quarantine**, durably; no takeover, no timeout | `reservation.release` — implemented |
| An unknown writer is on the host at admission | refuse and name it; never kill it, never disable it | `reservation.admit` — implemented |
| Admission with no verified predecessor release | refuse | `reservation.admit`, repaired 2026-09-11 — implemented |
| An S-B run on residue alone | reports no named operator recovery — **LAB-1**, §8 | observed, reported, not repaired |

**Independent recovery survives every refusal above.** That is §2's requirement
and it is why §2 refuses the mutation rather than the cleanup when its basis is
absent: a refusal before the first mutation leaves nothing to recover from.

---

## 2. Independent recovery — PR-20260911-2

### 2.1 What the review established

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

So after configuration mutation and loss of `R`'s custody, the specified run has
no trustworthy restoration input. A correct held-buffer restore does not solve
restart after the buffer is lost.

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

### 2.3 Capture, before the first mutation

In order, and every failure below refuses **before M1**:

1. `openat(pgconf_fd, name, O_RDONLY|O_NOFOLLOW)`; `fstat` → record
   `st_dev`, `st_ino`, `st_size`, `st_mtim`, `st_mode`, `st_uid`, `st_gid`.
2. Read to EOF into **one held buffer**. A short read, a read error, or a size
   beyond the reviewed bound (`MAX_MATERIALIZED_BYTES`) **refuses**; it is not
   retried, because a retry reads a possibly different file.
3. `fstat` the same descriptor again and refuse unless `st_size` and `st_mtim`
   are unchanged. This is a consistency check on the read, not a substitution
   check — the descriptor cannot have moved.
4. `digest = SHA-256(buffer)`, computed over **the buffer**, never over a re-read
   of the pathname. This is PR-20260909-R2-2's requirement and it stays.
5. Write the buffer into the store: `openat(run_fd, "<name>.tmp", O_CREAT|O_EXCL|
   O_WRONLY|O_NOFOLLOW, 0400)`; write; `fsync(file)`; `renameat2(run_fd, tmp,
   run_fd, "<name>", RENAME_NOREPLACE)`; `fsync(run_fd)`.
6. Write the **record** the same way: destination path, source identity from (1),
   `digest`, byte length, run id, reservation id, the capture time and the
   capturing identity. `fsync(file)`; `rename`; `fsync(run_fd)`.
7. **Re-read the stored copy from the store and digest it.** It must equal
   `digest`. This is a read of a different object from the buffer, so it is a
   genuine check that the durable copy is the bytes that were captured.
8. Only now is M1 permitted.

**Digest/metadata binding.** The record names the digest **and** the source's
`(st_dev, st_ino, st_size, st_mtim)` **and** the destination pathname. A
restoration reads all three: a copy whose digest matches but whose record names a
different destination is not restored anywhere.

### 2.4 Restore, and its failure modes

1. Read the stored copy into **one held buffer**; digest that buffer; compare
   with the record. A mismatch refuses and the run reaches **S-B**.
2. `openat(pgconf_fd, "<name>.restore.tmp", O_CREAT|O_EXCL|O_WRONLY, 0640)`;
   write **that buffer**; `fchown` to `postgres:postgres`; `fchmod 0640`;
   `fsync(file)`.
3. `renameat2(pgconf_fd, "<name>.restore.tmp", pgconf_fd, "<name>", 0)`;
   `fsync(pgconf_fd)`.
4. Repeat (1)–(3) for every captured file, **all temporaries written before any
   rename**, and the renames then issued in a fixed order recorded in the plan.
5. One reload, after the last rename. Then the post-reload verification of
   revision 1 §7, unchanged: an ordinary local connection as `postgres` still
   succeeds, and a connection as the temporary OS identity asking for the
   temporary role is refused.

**Partial writes and interruption.** The destination is never half-written: the
bytes go to a temporary and the rename is atomic. An interruption leaves a
`.restore.tmp`, which is detected on restart by `readdir` of the destination
directory, reported, and removed before a retry. An interruption between two
renames leaves a mixed configuration, which is why the verification in (5) is a
separate observation and why failing it is **S-B** rather than a retry.

**Destination custody.** `/etc/postgresql/16/main` is root-only, so the
destination's exposure is to a host administrator rather than to an experimental
identity **[A]**. That is materially smaller and it is not zero, and it is
recorded as such rather than described as proved.

### 2.5 Restart, retention and disposal

**Restart discovery, without the executor's memory.** A restarted executor, or a
human, lists `/var/lib/freedom-blades/recovery/` and finds one directory per run.
Each directory's record names the destination, the digest and the run. No index
file is needed and none is proposed, because an index is a second thing that can
be lost or disagree.

**If `R` is replaced or unavailable.** Recovery reads only
`/var/lib/freedom-blades/recovery/<run-id>/`. It does not read `R/before`, it
does not require `R` to exist, and it does not require the executor to be alive.
`R/before` may be retained for evidence, but it is **not** a recovery basis and
the revised procedure in §8.2 stops calling it one.

**Retention.** A run's recovery directory is retained until **both** the
post-reload verification of §2.4(5) passed **and** `reservation.release` returned
`RELEASED`. A quarantined run's directory is never removed automatically.

**Disposal.** An explicit operator step, after the two conditions above, naming
the run id. It is not a command this design offers, for the same reason §2.13.2b
withdrew the automatic clean.

**And if the basis cannot be established:** M1 does not run. No configuration
mutation is issued, so no recovery is needed. That is the refusal in §1.7 row 4
and it is the whole answer to *"what if the store cannot be written"*.

---

## 3. Source custody

Unchanged from revision 1 except where §1 replaces a mechanism:

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

**A held root descriptor still does not protect every descendant**, and revision
1 was right about that even though it was wrong about what a descriptor
comparison detects. `open(R, O_PATH)` names `R`; each subsequent component is
resolved afresh. §1.3's chain resolves each component **once** and holds it, which
is a different thing from resolving it repeatedly — and §1.4's residual columns
say where even that is not enough.

---

## 4. Test identities

Unchanged from revision 1 §4, with one addition from §1.3: **a descriptor handed
to an experimental step is part of that case's writable-object accounting.** A
case whose five facts do not enumerate the descriptors it receives is not
admissible, for the same reason a case with an unnamed writable path is not.

`E7` remains behind ten unconfirmed target facts and the executor's gate 4
refuses while any is unconfirmed. **This pass populates none of them.**

---

## 5. Cooperative lock and lifecycle storage — PR-20260911-6

### 5.1 What the review established

Revision 1 §9.2(c) proposed an adapter that creates the lock with
`O_CREAT|O_EXCL` and unlinks it on release, in `/run/freedom-blades` described as
root-owned `0755`, and called the adapter unprivileged. Three things are wrong
and the review named all three:

* ordinary participants cannot create or unlink an entry in a root-owned `0755`
  directory, so the **normal successful path does not exist**;
* precreating the lock does not rescue the protocol: `O_CREAT|O_EXCL` returns
  `EEXIST` while that entry exists **[D]**, so every participant refuses; and
* the stated fallback was refusal, which means the proposal had refusal paths and
  no success path at all.

**The O_EXCL protocol is withdrawn.** What follows is the review's own preferred
shape — a persistent provisioned lock inode plus a separately protected lifecycle
record — evaluated against the actual participant identities.

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
the record is root-written and world-readable within the group, and neither
object does the other's job.

### 5.3 The lock — one persistent provisioned inode

| | Value |
|---|---|
| Path | `/run/freedom-blades/laboratory.lock` |
| Created by | `systemd-tmpfiles`, at boot, from a provisioned fragment — **not** by any participant |
| Directory | `/run/freedom-blades`, `root:freedomlab`, `0750` |
| File | `root:freedomlab`, `0660`, **never unlinked** |
| Group | new system group `freedomlab`, with `ubuntu` as a member |
| Taken by | `open(path, O_RDWR)` — **no `O_CREAT`, no `O_EXCL`** — then `flock(fd, LOCK_EX\|LOCK_NB)` |
| Released by | `flock(fd, LOCK_UN)` and `close(fd)`, or by process exit |
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
  provides. **[P]**

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
| Not in `/run` | because it must survive reboot: a record that vanished on reboot would make every crashed run look like a first use |

Its content and ordering are `reservation.DURABLE_RECORD_ORDERING`, implemented
in the decision half on 2026-09-11 and reproduced here as the storage contract:

1. the reservation record reaches durable storage — written, `fsync`ed, directory
   `fsync`ed — carrying `ADMITTED` **before the first effect of any kind**;
2. `RUNNING` is published the same way before the first mutation-bearing step;
3. a quarantine record is an **addition** on any failure path, never a
   precondition. A crash before it can be written leaves `RUNNING`, which refuses
   every successor. **Absence of a quarantine record is never evidence that a
   predecessor ended;**
4. a release record is published only after `release()` returns `RELEASED`, and
   it names the reservation, host and target it is a release of; and
5. nothing deletes or rewrites a prior record. Operator recovery **appends** an
   entry naming the reference; the quarantined reservation stays quarantined.

### 5.5 Why two objects and not one

This is the part the review asked to be evaluated rather than asserted.

A crashed executor's `flock` is released by the kernel. If the lock were the
reservation, the next participant would find it free and proceed — which is
precisely finding PR-20260911-3. With the record separate, the next participant
finds the lock free, reads the record, sees `RUNNING` with no release record,
and **refuses**. No automatic takeover exists, and none can be produced by
waiting.

Conversely a test suite that crashes leaves no lifecycle record at all, because
participants 1–6 never write one. Its lock is released by the kernel and the next
suite proceeds. That is correct: a crashed test run is not a reservation and must
not block the host forever.

### 5.6 The normal successful path, stated end to end

1. Participant opens `/run/freedom-blades/laboratory.lock` `O_RDWR`. **[P]** it
   exists, because tmpfiles created it at boot.
2. `flock(LOCK_EX|LOCK_NB)`. If `EWOULDBLOCK`, the participant **waits or
   refuses** — never proceeds.
3. Participant reads `lifecycle.json`. Unreadable ⇒ refuse. States `RUNNING`,
   `RECOVERING` or `QUARANTINED` ⇒ refuse, naming the reservation.
4. A non-executor participant now runs, holding the lock, writing no record.
5. The executor additionally publishes `ADMITTED` and then `RUNNING` per §5.4
   before any effect, runs, and publishes the release record before releasing the
   lock.
6. Release: `flock(LOCK_UN)`, `close`. The file stays.

### 5.7 Refusal paths

| Situation | Behaviour |
|---|---|
| Lock file absent | refuse: the host is not provisioned |
| Lock file present, permission denied | refuse: `ubuntu` is not in `freedomlab` |
| `flock` returns `EWOULDBLOCK` | wait or refuse; never proceed, never `LOCK_NB` in a loop that gives up and proceeds |
| `lifecycle.json` absent or unreadable | refuse. An unreadable record is not an empty one |
| Record says `RUNNING`/`RECOVERING` | refuse and name the reservation and its recovery owner |
| Record says `QUARANTINED` | refuse. Participant 6, the environment reset, refuses **especially**: a reset would destroy the residue the quarantine exists to preserve |
| Record says `RELEASED`, or no reservation has ever been made | proceed |
| Crash, then restart, lock free, record `RUNNING` | **refuse.** This is §5.5 and it is the whole point |

---

## 6. Exact diff — what would be built, and what it would need

**None of this is built.** The estimates are for review, not for scheduling.

### 6.1 Modules and interfaces

| Module | Change | Size |
|---|---|---|
| `execution/descriptors.py` | **new.** The chain of §1.3: open, `fstat`, record, hand out by index, refuse an unregistered index. Holds the run's descriptor table and its `FD_CLOEXEC` policy | ≈ 220 lines |
| `execution/case_program.py` | new `DIRFD` and `COMPONENT` argument kinds; the four descriptor-relative verbs of §6.2; the `execveat` launch path for X1 | ≈ 260 lines |
| `execution/executor.py` | issue P1/P2/P4/L3 through the chain; the quiescence gate of §1.6; the pre-check/post-check of §1.4.5 | ≈ 180 lines |
| `execution/materializer.py` | §2.3's capture-and-publish and §2.4's verify-and-write over a held buffer, replacing the digest-then-`install` pair | ≈ 200 lines |
| `execution/recovery_store.py` | **new.** The independent store of §2.2: paths, modes, record format, restart discovery, retention | ≈ 180 lines |
| `execution/host_lock.py` | **new.** §5.3's protocol: open existing, `flock`, read the record, refuse. **No creation, no unlink** | ≈ 90 lines |
| `cleanup.py` | LAB-1's §8.1 reporting fix; `RECOVERY_PROCEDURE` replaced by §8.2's independent procedure | ≈ 60 lines |
| `plan.py`, `review_manifest.py` | coverage for the four new modules; no new executable | ≈ 20 lines |

### 6.2 Verbs, arguments and syscalls

```
  "openat":    (DIRFD, OPEN_MODE, COMPONENT)
  "unlinkat":  (DIRFD, COMPONENT)
  "renameat":  (DIRFD, COMPONENT, DIRFD, COMPONENT)
  "fstatat":   (DIRFD, COMPONENT)
```

* `DIRFD` — an index into the **inherited** descriptor table the executor handed
  this invocation, never a number a caller chooses freely and never a descriptor
  the program opened for itself;
* `COMPONENT` — one path component: no `/`, no `.`, no `..`;
* verb count **16 → 20**; `BOOTSTRAP_VERBS` unchanged at **2**;
* syscalls newly reached: `openat(2)` with `O_PATH|O_NOFOLLOW|O_DIRECTORY` and
  with `O_CREAT|O_EXCL|O_WRONLY|O_NOFOLLOW`; `mkdirat(2)`; `unlinkat(2)` with `0`
  and `AT_REMOVEDIR`; `renameat2(2)` with `RENAME_NOREPLACE` and `0`;
  `fstatat(2)` with `AT_SYMLINK_NOFOLLOW`; `execveat(2)` with `AT_EMPTY_PATH`;
  `flock(2)`; `ioctl(2)` `FS_IOC_SETFLAGS`/`FS_IOC_GETFLAGS` on an `O_RDONLY`
  descriptor rather than through `chattr`;
* `RENAME_NOREPLACE` requires filesystem support; `rename(2)` lists ext4 from
  Linux 3.15 and tmpfs from 3.17 **[D]**. The target's filesystem type is one of
  the twelve unconfirmed facts, so this is a **prerequisite to confirm at the
  Codex read-only preflight**, not an assumption to carry.

### 6.3 Descriptor transfer

Inheritance across `fork`/`execve` only, with `FD_CLOEXEC` cleared on a declared
set starting at descriptor 3 and a table naming each entry. No `SCM_RIGHTS`, no
re-open by path, no `/proc/<pid>/fd` traversal by any party other than the
executed program reading its own `/proc/self/fd/N` for X1.

### 6.4 Executables, identities and the permission delta

| Surface | Before | After, **if built** |
|---|---|---|
| `plan.PERMITTED_EXECUTABLES` | 22 absolute paths | **20** — `/usr/bin/install` and `/usr/bin/chattr` are **removed** from the harness path, replaced by syscalls in the case program |
| `case_program.VERBS` | 16 | **20** |
| `case_program.BOOTSTRAP_VERBS` | 2 | **2, unchanged** |
| `executor.PERMITTED_RUN_AS` | the identity contract | **unchanged** |
| `sudoers.EXPECTED_COMMANDS` | 2 `Cmnd_Alias` targets | **unchanged** |
| The one `ctypes` exception | `case_program._prctl_get_securebits` | **a second one**: the `FS_IOC_SETFLAGS`/`FS_IOC_GETFLAGS` ioctls and `execveat`, which CPython does not expose |
| New privileged writer | — | **none**; the executor is the existing one |
| New system group | — | **`freedomlab`**, with `ubuntu` as a member |
| New provisioned paths | — | `/run/freedom-blades` (`root:freedomlab 0750`), `/run/freedom-blades/laboratory.lock` (`root:freedomlab 0660`), `/var/lib/freedom-blades/laboratory` (`root:freedomlab 0750`), `/var/lib/freedom-blades/recovery` (`root:root 0700`) |
| New systemd artifact | — | one `systemd-tmpfiles` fragment for the two `/run` entries |
| New capability or unit | — | **none** |

**The permission delta is not zero, and revision 1's claim that it was is
withdrawn.** It is: one system group, one group membership, one tmpfiles
fragment, four provisioned paths, and a second `ctypes` exception. Removing two
executables from the allowlist is a reduction and does not offset the additions.

**Do not infer a zero delta from unchanged executable names.** Revision 1 did
exactly that: the executable list was unchanged because the mechanism had not
been specified down to the syscall, and specifying it is what revealed the new
group, the provisioning and the ioctl exception.

### 6.5 Durable storage and manifest coverage

Four new modules join `COVERED_SOURCES`, so the review-input digest changes when
they are written. The recovery store and the lifecycle record are new durable
state outside the disposable root; both are listed in §7 and neither exists.

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
| V6 | confirm the filesystem under `R` supports `RENAME_NOREPLACE` | §6.2; one of the twelve unconfirmed facts | **preflight**, unperformed |

---

## 8. LAB-1 — the proposed reporting-contract fix

**Classification: Important, confirmed by the September 11 review.** It is a
reporting gap in evidence classification rather than a safety property, and it
makes no unsafe operation reachable.

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
reproduction stays as it is. `test_feasibility.py::test_the_recovery_case_reproduces_lab_1`
is a **labelled defect reproduction** and deliberately asserts that the record
**fails**. It was not weakened, and the September 11 ordering repair did not
silently implement this fix through the producer: the recovery records are still
`FAILED` and still fail on exactly the recovery clause.

### 8.2 The second change LAB-1 travels with — `cleanup.RECOVERY_PROCEDURE`

Step 2 currently instructs recovery from `R/before`, which §2.1 shows is not an
independent basis. Proposed replacement, with only step 2 and step 4 changed:

> **2.** The byte-exact pre-change captures are retained **outside the disposable
> root**, under `/var/lib/freedom-blades/recovery/<run-id>/`, root-owned `0400`
> with a record binding each copy's SHA-256 to its destination and to the source
> identity it was taken from. Read the record, verify the copy against it, and
> compare with the live file before doing anything else. **Do not use
> `R/before`**: its custody depends on the root whose safety is in question.
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

**Model tests, not implementation proof.** Each row below is a test against a
model of the mechanism, tracking the **original and replacement identities and
the bytes actually affected** as separate values. A passing row establishes that
the proposed rule is constructible and falsifiable. It establishes nothing about
the built mechanism, and nothing here may be cited as evidence for EH-R16-1.

| # | Scenario | Expected | What it falsifies |
|---|---|---|---|
| 1 | `R` replaced between C1 and an `fstatat` by name | detected; dependent effects refused; S-B | that the root's exposure is nil |
| 2 | a descendant directory replaced after its chain entry was recorded | detected on the next `fstatat` by name; refused | §1.1(1)'s withdrawn claim — the model must show a descriptor self-comparison **passing** while the name resolves elsewhere |
| 3 | a final entry replaced after a successful pre-check and before `unlinkat` | **not** prevented; post-check detects; S-B; original and replacement identities both reported | that removal is inode-bound |
| 4 | the same, inside a verified quiescence window with no experimental process | no experimental writer can perform it; an administrator still can | that B3 is a technical guarantee |
| 5 | a payload's inode replaced at its pathname after P2 | `execveat` runs the **original** inode; the replacement is never executed | that pathname execution and descriptor execution are equivalent |
| 6 | a payload's **bytes** mutated in place, inode unchanged | **not** detected by any descriptor check; refused only where a digest of the read bytes is required | that descriptors bind content |
| 7 | capture read fails, or size exceeds the bound | M1 never runs; no mutation; no recovery needed | that capture failure is recoverable after mutation |
| 8 | capture succeeds, store write fails | M1 never runs | that a held buffer is a durable basis |
| 9 | wrong destination in the record | restore refuses; nothing is written | that a matching digest is sufficient |
| 10 | executor restarts, memory lost, `R` gone | recovery found by `readdir` of the store; verified; restored | that recovery needs the executor or `R` |
| 11 | restore interrupted between temp and rename | destination unchanged; temp detected and reported | that partial writes can reach the destination |
| 12 | restore interrupted between two renames | mixed configuration; post-reload verification fails; S-B | that a multi-file restore is atomic |
| 13 | lock file absent | every participant refuses | that a participant may create it |
| 14 | lock held by another participant | wait or refuse | that `LOCK_NB` failure may be walked past |
| 15 | lock free, lifecycle record says `RUNNING` | **refuse** | that a free lock is a released host |
| 16 | lock free, record says `RELEASED` with a bound release record | proceed | that the refusals above refuse everything |
| 17 | quarantine record present, participant 6 (environment reset) | refuse | that a reset is a recovery |
| 18 | unknown surviving writer at admission | refuse and name it; never kill it | that an inventory may be completed by force |
| 19 | **successful controls**: full provisioning, execution, capture, restore, cleanup, release, with nothing injected | every effect reaches its intended object; release returns `RELEASED` | that the mechanism refuses everything |

Rows 2, 3, 5 and 6 are the ones that must **fail** the withdrawn revision-1
mechanism and pass this one; a matrix in which revision 1 also passes is a matrix
that is not testing the correction.

---

## 10. Assumptions, and what this document does not do

**Every [A] in one place.** `oracle-test`'s participants all run as `ubuntu`;
`ubuntu` holds passwordless `sudo`; `/run` is a tmpfs; `/opt/freedom-blades/evidence`
and `/etc/postgresql/16/main` are root-only; host administrators are trusted to
obey the reservation and are not prevented from ignoring it; the filesystem under
`R` is unconfirmed and `RENAME_NOREPLACE` support with it. None of these was
verified on the target by this document, and no host was inspected.

**It accepts nothing.** It approves no digest, populates none of the twelve
unconfirmed target facts, authorizes no host action, no SSH, no synchronization,
no provisioning, no database operation and no execution. It does not clear the
operational-ineligibility control, does not move `is_executable`, and does not
reduce the three C-7 cases' unresolved status.

EH-R16-1, PR-20260910-1/2/3, the September 10 findings and the six September 11
findings remain **Open**. Package 5.0 remains **not ready**, P5.0-R5
**Blocking**, OD-62 **Open**.

**The next step is Codex's technical review of this mechanism**, then Peter's
decision on the §7 provisioning and permission delta and on LAB-1's
classification. Implementation review precedes the later read-only target
preflight, which precedes a separate execution decision. Passing tests advance
none of those gates.
