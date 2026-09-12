# Package 5.0 — operation-by-operation contract for the smaller privileged runner

> **Superseded 2026-09-11 by
> [runner contract revision 2](phase-5-0-reserved-laboratory-runner-contract-r2.md).**
> This document is the submission the
> [September 11 review](project-review-2026-09-11.md) answered and is preserved
> unchanged below as history. Three of its claims were found not to hold and are
> **withdrawn**: the descriptor/baseline comparison of §9.2(b) as a remedy
> (PR-20260911-1), the unprovided operator copy described as a safeguard in §7
> (PR-20260911-2), and the `O_CREAT|O_EXCL` lock protocol of §9.2(c) together
> with the "zero permission delta" of §9.1 (PR-20260911-6). Revision 2 is the
> proposal; read this only for what was submitted, never for what is proposed.
> It remains **not accepted and not implemented**.

Date: 2026-09-11. Author: Claude. Change record: C-P5.0-LAB-1.

**Status: submitted for Codex technical review. Not accepted, not implemented,
and no execution is authorized.** Sections 1–8 describe the mechanism the
reserved-laboratory direction asks for. Section 9 is the **exact permission and
implementation diff** for the one part of it that needs a new privileged surface,
and that part is deliberately **not built**: the prompt's rule is that any newly
required privileged writer, verb, syscall surface or permission expansion is
presented for review *before* the mechanism is implemented, under the existing
design checkpoint.

Nothing here repairs **EH-R16-1**. It remains Open, the harness retains an
unconditional real-execution refusal (`reservation.REAL_EXECUTION_REFUSAL`), and
a reserved host does not close it — §4.4 says why in the finding's own terms.

## 0. What the reservation changes, and what it does not

The 2026-09-10 direction reserves the **whole host** for one accountable
executor. That is an operational exclusion enforced by trusted administrators and
one cooperative lock, and it changes exactly one thing about the threat model:

| | Before the reservation | After it |
|---|---|---|
| An unrelated cooperating writer (a test run, a sync, a dependency update) substitutes an object mid-run | possible, and undetected | excluded by the lock plus the pre-admission inventory, and a detected violation invalidates the affected evidence |
| A host administrator substitutes an object mid-run | possible | still possible. Trusted not to; not prevented, and not claimed to be |
| **This run's own experimental writers** substitute an object mid-run | possible | **still possible.** This is EH-R16-1 and the reservation does not touch it |

The third row is the one that matters, and the direction states it: *"The
whole-host reservation excludes unrelated cooperative work; it does not repair
substitution by experimental writers."* Every contract below is written against
that row, not against the first.

## 1. Vocabulary — four things that are not interchangeable

R2 finding PR-20260909-R2-1 required this distinction and it is restated because
the contract's rows depend on it:

1. an **observed baseline** — somebody looked, once, and recorded what was there.
   It says nothing about what is there now;
2. a **vector allowlist** — the argument strings a program may be given. It
   constrains the *request*, not the object the request resolves to;
3. a **held object reference** — an open descriptor. It names one object for as
   long as it is held, and it does not stabilize the *lookup* of any path
   component; and
4. an **exclusion boundary** — a guarantee that nobody else writes. It is
   operational here, not technical.

Today's executor has (1) and (2). EH-R16-1 is the gap between them and what the
operations below actually need.

## 2. Subjects and writable parents

The disposable root is `R = /opt/freedom-blades/evidence/<run>`. Every subject is
strictly inside it except `R` itself, which is why `ROOT_PATH` is a distinct
argument kind in the reviewed verb table admitting exactly one string.

| Subject | Writable parent | Who may write the parent during a run |
|---|---|---|
| `R` | `/opt/freedom-blades/evidence` | root only. Created by the exclusive `mkdir(2)` whose success is its own ownership proof (C-8 resolution) |
| `R/probe`, `R/probe-ro` | `R` | root, and the reviewed case program under the four disposable identities |
| `R/journal/*` | `R/journal` | root, `freedomjournal` group members |
| `R/before/*` — byte-exact pre-change captures | `R/before` | **root only.** §8 below is why |
| `R/bin/case-program` — the installed reviewed payload | `R/bin` | **root only** |
| `/etc/postgresql/16/main/pg_hba.conf`, `pg_ident.conf` | `/etc/postgresql/16/main` | root. Restored from `R/before` |

**The load-bearing asymmetry.** Three of these parents are writable by the
experimental identities and three are not. Every operation in §3 that acts on a
subject whose parent is in the first group is an operation EH-R16-1 applies to.

## 3. The operation inventory

Every ownership-dependent read and mutation, in run order. `Prerequisite` is what
must be true before the effect is issued. `Enforcement` is where that is
established today, and **`Gap`** marks a row where today's answer is a vector
allowlist or a stale baseline rather than the object's current identity.

### 3.1 Creation

| # | Operation | Subject / bytes | Resolution | Prerequisite | Enforcement today | Gap |
|---|---|---|---|---|---|---|
| C1 | `mkdir(2)` of `R`, exclusive | `R` | path | `R` does not exist | `EEXIST` is the proof. Success **is** ownership | — |
| C2 | `statroot` on `R` | `R` | path | C1 succeeded | re-stat, compared with C1's result | narrow: a replacement between C1 and C2 is detected, not prevented |

### 3.2 Provisioning

| # | Operation | Subject / bytes | Resolution | Prerequisite | Enforcement today | Gap |
|---|---|---|---|---|---|---|
| P1 | `install -d` of `R/bin`, `R/before`, `R/journal` | directories under `R` | path | `R` is the object C1 created | **vector allowlist only** | **yes** — the object `R` resolves to now is not checked |
| P2 | `install -m 0555` of the reviewed case program into `R/bin` | reviewed bytes | path | `R/bin` is the object P1 created; source bytes match `materialization.REVIEWED_DIGESTS` | digest of the *source*; destination by path | **yes** — destination parent identity unchecked |
| P3 | `useradd`/`groupadd` of the four disposable identities | `/etc/passwd`, `/etc/group` | name | names are not existing production identities (`targets.validate_account_name`) | name check against the approved target | — |
| P4 | `chattr +i` on the seal, `+a` on the journal | files under `R/journal` | path | the file is the one P2/stage created | **vector allowlist only** | **yes** |

### 3.3 Capture

| # | Operation | Subject / bytes | Resolution | Prerequisite | Enforcement today | Gap |
|---|---|---|---|---|---|---|
| K1 | read `pg_hba.conf` / `pg_ident.conf` | live bytes | path | nothing has been mutated yet | ordering: capture precedes the first mutation | — |
| K2 | `install` the captured bytes into `R/before` | the bytes K1 read | path | K1 succeeded | step-satisfaction check in `_revalidate_materialization` | partial — see §7 |
| K3 | digest the capture | `R/before/*` | path | K2 succeeded | SHA-256 recorded | **yes** — this is PR-20260909-R2-2: the digest is of a *re-read*, not of the bytes K1 held |

### 3.4 Materialization and experiments

| # | Operation | Subject / bytes | Resolution | Prerequisite | Enforcement today | Gap |
|---|---|---|---|---|---|---|
| M1 | write the reviewed `pg_hba.conf` / `pg_ident.conf` | reviewed bytes | path | K2 satisfied; content within `MAX_MATERIALIZED_BYTES` | digest of source; step-satisfaction of the capture | **yes** — destination |
| M2 | reload PostgreSQL, observe the temporary mapping in force | server state | — | M1 succeeded | post-reload control connection | — |
| X1…Xn | the reviewed case program under `E1 … E8` | files under `R` | path | the installed program is the object P2 installed; the subject is inside `R` | vector allowlist; `-I -S`; interpreter path/version/SHA-256 preflight | **yes** — both the program and every subject |

### 3.5 Cleanup

| # | Operation | Subject / bytes | Resolution | Prerequisite | Enforcement today | Gap |
|---|---|---|---|---|---|---|
| L1 | restore `R/before/*` over the live configuration | the bytes K3 verified | path | K3's digest matched | digest check, then a **separate** `install` by pathname | **yes** — PR-20260909-R2-2: the check and the write are not bound |
| L2 | reload and verify restoration in force | server state | — | L1 succeeded | post-reload observation; unverified ⇒ S-B | — |
| L3 | `chattr -i` / `-a`, then `rm`/`rmdir` of this run's objects, one named object at a time | objects under `R` | path | each was created by this run (baseline proved absent) | `executor.py:729` revalidates **the vector** | **yes — this is EH-R16-1 verbatim** |
| L4 | classify §2.13.2b state | — | — | L1–L3 attempted | `cleanup.classify_cleanup` | — |

**Seven rows carry a gap, and they are not seven findings.** They are one:
*every ownership-dependent effect in this harness is issued against a pathname
whose current resolution nobody checked at the moment of the effect.* A guard
placed only at L3 — which is what the earlier C-8 proposal offered — leaves P1
through X1 unprotected, and a cleanup refusal cannot undo an effect already
issued at P1.

## 4. Test identities

### 4.1 The four disposable OS identities

Created at P3, removed at cleanup, and never an existing production identity —
`targets.validate_account_name` refuses that against the approved target. They
are the identities the experiments assume and they are **not made trusted** by
the reservation: the direction is explicit that *"Experimental identities and
processes are not made trusted by this decision."*

### 4.2 `E1 … E8`

The eight capability identities of package plan §2.13.5c, constructed with
`capsh(1)` in the documented seven-step order. Each names its complete UID, GID,
supplementary groups, P/E/I/A/B sets and securebits. `E7` remains behind ten
unconfirmed target facts and the executor's gate 4 refuses while any is
unconfirmed. **This pass populates none of them.**

### 4.3 Each adversarial case names its own five facts

Per the direction: identity, capabilities, writable objects, timing, expected
observation, and its positive control. Test concurrency required by the package
stays *inside* the case rather than being ambient. A case with an unnamed writable
object is not admissible, because §3's inventory cannot be completed for it.

### 4.4 Why a deliberately root-capable case is not harmless

A case that runs with `CAP_LINUX_IMMUTABLE` and `CAP_FOWNER` can clear a flag on
the root-owned archive. Administrator trust says the *administrator* will not
interfere; it says nothing about what the experiment does. Such a case needs its
own accounting of possible effects — which objects it can reach, what each reach
would do, and what detects it — and that accounting is a prerequisite of the case,
not of the run.

## 5. Source custody

**Reviewed source and recovery inputs stay outside every experimentally writable
path.** Concretely:

* the reviewed case program is installed `0555` root-owned into `R/bin`, whose
  parent is root-only (§2);
* the interpreter is the documented Python 3.12 path, validated by preflight on
  path, version and executable SHA-256 (the 2026-09-06 Option B ruling), and runs
  `-I -S`;
* **staged-source substitution is not reintroduced.** The earlier proposal to
  stage sources into a writable location and install from there is withdrawn and
  stays withdrawn; and
* the review manifest pins 34 source files by SHA-256, and every generated
  artifact is review input until explicitly approved for execution.

**A held root descriptor does not protect every descendant.** `open(R, O_PATH)`
names `R` for as long as it is held. It does not stabilize the lookup of
`R/bin`, of `R/bin/case-program`, or of any final entry: each subsequent
component is resolved afresh. The earlier claim that a root descriptor plus
`journal/000001.seal` fixes the exposure was wrong about the still-resolved
`journal` component, and that correction stands.

## 6. Quiescence

**Do not infer quiescence from the parent command exiting.** Before any operation
that depends on an experimental process having finished, three observations are
required and none defaults to true:

1. every process the case started has exited — observed, not inferred from the
   parent's exit status;
2. every server-side transaction the case opened has settled. A `psql` client
   exiting says the client stopped waiting; and
3. no transient unit the case created is still active.

`reservation.ReleaseEvidence` carries the first two as `bool | None`, and `None`
— an observation nobody made — is treated exactly like `False` and reported
separately, because *"not checked"* and *"checked and false"* are different
things to tell an operator. `tests/phase_5_0_evidence/test_reservation.py` covers
the orphaned child and the delayed transaction as separate injected cases.

## 7. Verified capture, and the restore destination

PR-20260909-R2-2's requirement, restated as the contract this runner must meet:

**The capture side.** The recorded baseline must refer to *the bytes actually
captured*, established before the first configuration mutation. A second read of
the live pathname is not proof of what the first copy captured. So: one read
produces a buffer; the buffer is what is digested; the buffer is what is
installed into `R/before`; and a read failure, a size beyond the reviewed bound
or an inconsistent capture refuses **before** M1 rather than being retried.

**The restore side.** The exact bytes checked must be the bytes written. Today
L1 digests a capture and then asks a separate `install` to reopen that pathname,
so a replacement after the digest is installed despite a passing check, and the
root inode can be unchanged throughout. The bounded remedy is a **verify-and-write
over a held buffer**: read the capture into memory once, verify the digest of
that buffer, and write *that buffer* to the destination — never a second
pathname read between the check and the write.

**Destination substitution is not solved by fixing source substitution.** The
destination is `/etc/postgresql/16/main/…`, a root-only directory, so the
destination's exposure is to a host administrator rather than to an experimental
identity. That is a materially smaller exposure and it is not zero, and it is
recorded as such rather than described as proved.

**Independent configuration recovery is preserved.** If the disposable root is
unsafe — quarantined, or its ownership in doubt — the retained captures under
`R/before` cannot be the recovery basis, because their custody depends on the
root whose safety is in question. The recovery basis is then the operator's own
out-of-band copy and the four-step `cleanup.RECOVERY_PROCEDURE`, whose ownership
basis is separate and stated: it is root's, over `/etc/postgresql`, and it does
not pass through `R` at all.

## 8. Refusal and uncertainty

| Situation | Behaviour | Where |
|---|---|---|
| An operation's subject cannot be shown to be the object the prerequisite names | **refuse before the effect**, not after | §9's proposal; **not implemented** |
| The root or a descendant is substituted mid-run | refuse every subsequent dependent effect; report the substitution; state S-B | §9; **not implemented** |
| Cleanup cannot complete | S-B, exit 3, residue named by absolute path, next invocation refuses | `cleanup.classify_cleanup` — implemented |
| Cleanup state uncertain | S-B, and the executor refuses the next run *more* firmly than for known residue | `executor._refuse_when_blocked` — implemented |
| A pre-existing object is found where a subject would be created | preserve it, never remove it, report it as `preserved` | `CleanupOutcome.preserved` — implemented |
| Reservation release cannot establish its conditions | **quarantine**, durably; no takeover, no timeout | `reservation.release` — implemented |
| An unknown writer is on the host at admission | refuse and name it; never kill it, never disable it | `reservation.admit` — implemented |
| An S-B run on residue alone | reports no named operator recovery — **finding LAB-1**, §9.3 | observed, reported, not repaired |

## 9. The permission and implementation diff

### 9.1 What this pass added to the privileged surface: **nothing**

| Surface | Before | After this pass |
|---|---|---|
| `plan.PERMITTED_EXECUTABLES` | 22 absolute paths | **22, unchanged** |
| `case_program.VERBS` | 16 verbs | **16, unchanged** |
| `case_program.BOOTSTRAP_VERBS` | 2 | **2, unchanged** |
| `executor.PERMITTED_RUN_AS` | the identity contract | **unchanged** |
| `sudoers.EXPECTED_COMMANDS` | 2 `Cmnd_Alias` targets | **2, unchanged** |
| The one `ctypes` exception | `case_program._prctl_get_securebits` | **unchanged** |
| Syscalls the case program may issue | `open`, `pwrite`, `ftruncate`, `rename`, `unlink`, `symlink`, `statvfs`, two `ioctl`s, `mkdir`, `stat` | **unchanged** |
| New privileged writer | — | **none** |
| New sudoers rule, capability, unit or file mode | — | **none** |

Both modules added in this pass — `tools/phase_5_0_evidence/feasibility.py` and
`tools/phase_5_0_evidence/reservation.py` — are **planning tier**. They start no
process, open no file, reach no socket and import nothing from `execution/` or
from the product tree. `tests/phase_5_0_evidence/test_no_execution.py` asserts
the first against their source, and `test_feasibility.py` asserts the second.

The cooperative lock at `/run/freedom-blades/laboratory.lock` is an **ordinary
unprivileged advisory file**. It grants nothing, revokes nothing and is not a
privileged interface. The adapter that would actually take it is **not
implemented** and is item 9.2(c) below.

### 9.2 What the EH-R16-1 remedy would require — for review, not for building

The gap in §3 is that effects resolve pathnames afresh. Binding an effect to an
object requires descriptor-relative operations, and that is a syscall-surface
expansion. The exact diff, for Codex to accept or reject before anything is
built:

**(a) `case_program.VERBS` — four new verbs, each taking a directory descriptor
index rather than a parent path.**

```
  "openat":     (DIRFD, OPEN_MODE, COMPONENT),
  "unlinkat":   (DIRFD, COMPONENT),
  "renameat":   (DIRFD, COMPONENT, DIRFD, COMPONENT),
  "fstatat":    (DIRFD, COMPONENT),
```

* new argument kinds `DIRFD` (a small integer index into descriptors the program
  opened itself in this invocation, never a number a caller chooses freely) and
  `COMPONENT` (one path component: no `/`, no `.`, no `..`);
* new syscalls reached: `openat(2)` with `O_PATH|O_NOFOLLOW|O_DIRECTORY`,
  `unlinkat(2)`, `renameat2(2)` with `RENAME_NOREPLACE`, `fstatat(2)` with
  `AT_SYMLINK_NOFOLLOW`;
* verb count 16 → 20; `BOOTSTRAP_VERBS` unchanged at 2;
* **no new executable, no new sudoers rule, no new capability, no new identity.**

**(b) A descriptor chain walked once per run.** `R` is opened `O_PATH` at C1 and
each subsequent component is opened relative to its parent's descriptor and
`fstat`ed. An operation whose descriptor's `st_dev`/`st_ino` no longer matches
the recorded pair **refuses before issuing the effect**. This covers §3 rows P1,
P2, P4, X1 and L3. It does **not** cover in-place content mutation of a file
whose inode is unchanged; that is a separate exposure and stays separate.

**(c) A cooperative-lock adapter in the execution tier.** One new module,
`tools/phase_5_0_evidence/execution/host_lock.py`, roughly 120 lines: `open(2)`
with `O_CREAT|O_EXCL` on `HOST_LOCK_PATH`, `flock(2)` LOCK_EX|LOCK_NB, write the
reservation id and owner, `fsync`, and release by `flock(2)` LOCK_UN and
`unlink(2)`. It adds `fcntl` to the execution tier's import set and adds
`host_lock` to `EXECUTION_TIER_NAMES` and to `COVERED_SOURCES`. **No privilege:**
`/run/freedom-blades` is `0755` root-owned and the lock file is `0644`; a
participant that cannot create it refuses rather than proceeding.

**(d) Verify-and-write for §7's restore.** A bounded read-verify-write over a
held buffer, replacing the digest-then-`install` pair at L1. This is a change to
`execution/materializer.py` and does **not** add an executable or a verb: the
`install` invocation is replaced by a write the boundary already performs for
materialized content.

**Estimated scope: (a) + (b) together ≈ 350 lines of `case_program.py` and
`executor.py` plus ≈ 25 new injected test cases; (c) ≈ 120 lines plus 12 tests;
(d) ≈ 80 lines plus 10 tests.** None of it is built.

### 9.3 LAB-1 — a defect found by this pass, reported and not repaired

§2.13.2b requires an S-B run to report *the named operator recovery*, and
`journal.classify_cleanup_failure_state` compares that clause like the other six.
Two named recoveries exist and they are for different things:
`journal.RECOVERY_PROCEDURE` is the five-step residue recovery, and
`cleanup.RECOVERY_PROCEDURE` is the four-step configuration recovery.
`CleanupOutcome.recovery_procedure` carries **only the second**, and only when a
configuration capture was retained. A run that reaches S-B on **residue alone** —
which is both variants of `JNL-47-RECOVERY-STATE` — therefore reports no named
recovery at all and fails that clause.

The repair attaches the residue procedure to the outcome, which changes
`CleanupOutcome`'s accepted contract and adds a `cleanup` → `journal` dependency.
That is a mechanism change behind the outstanding design checkpoint, so it is
**submitted and not made**. `test_feasibility.py::test_the_recovery_case_reproduces_lab_1`
is a labelled defect reproduction and is deliberately an assertion that the record
**fails**; it was not weakened to make the clause appear satisfied.

Proposed classification: **Important**. It is a reporting gap in evidence
classification rather than a safety property, and it does not make any unsafe
operation reachable. Codex classifies it.

## 10. What this document does not do

It accepts nothing, approves no digest, populates none of the twelve unconfirmed
target facts, and authorizes no host action. It does not clear the operational
ineligibility control, does not move `is_executable`, and does not reduce the
three C-7 cases' unresolved status. EH-R16-1, PR-20260910-1/2/3 and the September
10 findings remain Open; Package 5.0 remains **not ready**, P5.0-R5 **Blocking**,
OD-62 **Open**.
