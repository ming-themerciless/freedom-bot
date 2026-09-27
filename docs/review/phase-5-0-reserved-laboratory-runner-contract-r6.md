# Package 5.0 — runner contract, revision 6

Date: 2026-09-11. Author: Claude. Change record: C-P5.0-LAB-1.

**Current amendment, 2026-09-20 — C-P5.0-LAB-I3-R5, target identity.** Peter
decides Option A for LAB-I3-TARGET-1: the approved target keeps `host` as the
operational SSH alias `oracle-test` and gains a separately approved kernel
nodename fact, `Test`. §7.4.2's admission step 2 is corrected accordingly — it
compares `os.uname().nodename` with `APPROVED_TARGET_FACTS.kernel_nodename`,
while kernel release and architecture keep comparing their own approved facts.
The two names are two facts about two layers and are never substituted for one
another. Because the nodename is approved identity, `TARGET_IDENTITY_DIGEST`,
`CONFIRMATION_TOKEN`, the review manifest (version **17**) and the review-input
digest all move; the previously accepted `be9e110f…` is not evidence for the
reconciled tree. This amendment authorizes repository reconciliation and
independent review only. It releases no host access, synchronization,
controlled write, verifier invocation or retry; **I3 remains unconfirmed and
unperformed**, V7 excluded, `plan.is_executable=False`.

**Superseded amendment, 2026-09-19 — C-P5.0-LAB-I3-D1.** Peter rules that P2's
case program is `root:root 0555` and its protected-hardlink publication relies
on the filesystem-UID owner condition, not `CAP_FOWNER`. The actual
operation-time capability masks remain required observations; `CapBnd` is not
evidence of `CapEff`. Decision B is narrowly amended so the separately armed
I3 verifier may temporarily create canonical `R` and `R/bin` solely for I3,
with reviewed ownership/modes, identity-guarded removal, and non-success on
any mismatch, residue or cleanup/barrier failure. This amendment authorizes
repository remediation only. It does not release synchronization, host access,
controlled writes or verifier execution; I3 remains unconfirmed.

**Dated remediation, 2026-09-19 — C-P5.0-LAB-I3-R2, implementing
C-P5.0-LAB-I3-D1.** The ruling is carried into code, tests and generated
artifacts. `case_runtime.CASE_PROGRAM_MODE` is `0555`, so P2's effect row and
`P-04`'s compared expectation now say `root:root 0555`; the owner and group are
unchanged. `provisioning.VERIFICATION_PROCEDURE` no longer states a P2
`CAP_FOWNER` dependency. The exclusive link is factored out of
`renameat(noreplace=True)` as the one primitive `PosixFilesystem.linkat` (§6.2),
because the fused call could not expose the two-name state. **§7.4 is new**: the
complete procedure of the separately armed I3 verifier — two gates, two
identities as separate invocations, admission before the first write, the four
contexts, decision B's `R`/`R/bin` exception, operation-time capability
evidence, guarded removal, partial-state accounting, the survey, safe output and
exit statuses. §9.2 rows **90–105** trace it and §9.3's I3 row names it.
Passages this remediation changed are marked *amended 2026-09-19,
C-P5.0-LAB-I3-R2*. **Nothing was applied to any host**: the verifier is
implemented and unperformed, I3 stays unconfirmed, no finding is closed on the
implementer's authority, and no digest is approved.

**Dated acceptance, 2026-09-17 — C-P5.0-LAB-V6-D-R1-A.** Peter accepted
Codex's independent technical and security re-review of the R1 correction with
no finding and closed **PR-20260917-LAB-V6D-R1-1**. This confirms the operative
topology below: canonical `R = /var/lib/fb-evidence-p5-0`, D1 on `R`'s parent
`/var/lib`, and the `/opt` form only in explicitly labelled history. It
approves no digest, authorizes no host action and advances no gate. V6 remains
performed-but-not-closed; I3 unconfirmed; V7 excluded; V8, V10 and I12
unperformed; `is_executable=False`; Package 5.0 not ready. See the
[independent re-review](project-review-2026-09-17-reserved-laboratory-v6-d-r1-contract-correction.md).

**Dated amendment, 2026-09-17 — C-P5.0-LAB-V6-D.** Peter accepted the
independent R4 review and closed PR-20260916-LAB-V6R3-1. V11 and
`/opt/freedom-blades/evidence` are withdrawn; no ownership change to
`/opt/freedom-blades` is made. The sole canonical `R` is the approved
`/var/lib/fb-evidence-p5-0`. V12 creates persistent
`/var/lib/freedom-blades` as `root:root 0755` before V4 and V5. Production
`EVIDENCE_ROLE` registration is deferred until its real consumer receives
separate implementation and review authority. This amendment supersedes every
contrary operative V11/location statement retained below as historical design
evidence. It authorizes repository remediation only, not provisioning or
execution.

**Dated correction, 2026-09-17 — C-P5.0-LAB-V6-D-R1, Blocking
PR-20260917-LAB-V6D-R1-1.** Codex's
[independent review of the topology disposition](project-review-2026-09-17-reserved-laboratory-v6-topology-disposition.md)
found that the amendment above had not reached two operative rows: §1.3.3's
descriptor inventory still opened with `R = /opt/freedom-blades/evidence/<run>`
six lines above its own amended D1 row, and §7's live V6 row still directed the
survey to observe the withdrawn `/opt/freedom-blades/evidence` and reported it
as **unperformed**. **A dated banner is not a correction of a normative row** —
the same control failure Blocking PR-20260917-LAB-V6D-2 named — so the rows are
corrected in place: §1.3.3 defines `R = /var/lib/fb-evidence-p5-0` and D1 on
`R`'s parent `/var/lib`; §7's V6 row observes only the canonical locations and
states V6 **performed 2026-09-16 and not closed**; §7's remaining *unperformed*
sentences, §2.2's location, §7.3's decision-B closing sentence and §9.3's I12
are corrected with them. Passages this correction changed are marked *amended
2026-09-17, C-P5.0-LAB-V6-D-R1*. **No approved value moves**: `R`, V12's mode,
the released subset and its order, V7's exclusion and every `approved` flag are
unchanged, no code is changed and no artifact is regenerated. **Nothing was
applied to any host**, V6 remains performed-but-not-closed, **I3 stays
unconfirmed**, no finding is closed on the implementer's authority and no
preflight, provisioning or execution is authorized.

**Implementation authorization, 2026-09-13:** Peter authorizes
C-P5.0-LAB-I, bounded repository implementation and local tests of this accepted
design. The authorization includes provisioning definitions but not their
application, and it excludes all disposable-server access, preflight,
provisioning and execution. The active assignment is the
[Claude implementation prompt](phase-5-0-reserved-laboratory-implementation-claude-prompt.md).
Implementation must return for independent Codex technical and security review;
no finding or gate closes merely because code is written or local tests pass.

**Status: submitted for technical review, not accepted and not implemented, and
no execution is authorized.**

**Dated disposition, 2026-09-12:** this status describes the document when
submitted. Peter has since accepted the ten-item delta as the lab design, chosen
shared `ubuntu`, and accepted the bounded LAB-1 fix, which is implemented
locally pending independent review. This is not acceptance of every r6 claim,
not permission to apply any provisioned change, and not execution authorization.

**Dated amendment, 2026-09-15 — D1 and D2, change record C-P5.0-LAB-D12:** Peter
approved D1, exclusive publication by `linkat` then `unlinkat` in place of
`renameat2(RENAME_NOREPLACE)`, and D2, the short-lived listing descriptor D20.
The [amendment record](phase-5-0-reserved-laboratory-r6-d1-d2-proposed-amendment.md)
holds the proposal as approved. Every passage the amendment changed is marked
*amended 2026-09-15, D1* or *D2*. The first application added the approved
paragraphs but left the operative steps specifying `renameat2`; those steps, one
§6.4 row and the interruption state were corrected the same day
([correction handback](phase-5-0-reserved-laboratory-r6-d1-d2-correction-handback.md)),
pending Codex's review. The amendment changes contract text only: it confirms no
target fact, closes no finding and authorizes no preflight, provisioning or
execution.

**Dated remediation, 2026-09-15 — C-P5.0-LAB-D12-R1, Blocking
PR-20260915-LAB-D12-1.** Codex's
[re-review of the corrected D1/D2 delta](project-review-2026-09-15-reserved-laboratory-d1-d2-corrections.md)
accepted it except for one Blocking admission defect: an interrupted
lifecycle-record publication did not refuse all seven participants. The final
record was valid and readable, the admission re-sealed and parsed it without
asking whether its publication had finished, and the six ordinary participants
proceeded while only the harness refused later at T7. **The admission now
refuses on the record's leftover publication temporary, before any of the seven
proceeds** (§§5.6, 5.9, 6.2, 9.2 rows 74–78). In the same pass, T1's and T6's
operator recovery requires an immediately preceding `(st_dev, st_ino)`
comparison before the temporary is removed (§§5.10, 6.2); the unresolved X1
`execveat` route is given an owner, its required evidence and its execution stop
condition (§6.4); and Peter's approved V6 disposition is incorporated (§§7, 9.3,
10). Passages this remediation changed are marked *amended 2026-09-15, D1
remediation*. **No route is chosen for X1, no target fact is confirmed, no
finding is closed and no preflight, provisioning or execution is authorized.**

**Dated remediation, 2026-09-16 — C-P5.0-LAB-V6-R1, the incomplete provisioning
contract.** The released V6 read-only survey found `/opt/freedom-blades/evidence`
**absent**, and §7 had assigned it no owner, group, numeric mode, creation
mechanism, persistence behaviour or provisioning item — §1.4.1 called it only
*"root-only [A]"*. The approved prerequisite provisioning therefore could not be
applied as one exact, reviewable delta. **The §7 set grows by one item to
eleven: V11, `/opt/freedom-blades/evidence`, `0700 root:root`**, with §7.2
deriving that mode from the identity that opens D1 rather than choosing it,
§7.1 recording the released subset and V7's exclusion with its stop condition,
and §7.3 reporting the two parents the delta still does not define — including
that the observed `/opt/freedom-blades` is `1001:1001 0755`, which **defeats
§1.4.1's administrator-only exposure argument for the entry** and is raised
rather than repaired. §§1.3.3, 1.4.1, 6.4, 9.2 (rows 80–86), 9.3 and 10 are
amended to match, and passages this remediation changed are marked *amended
2026-09-16, V6 remediation*. **Nothing was applied to any host**, V7 is
excluded, **I3 stays unconfirmed**, V6 remains performed-but-not-closed, no
finding is closed and no preflight, provisioning or execution is authorized.

**Dated remediation, 2026-09-16 — C-P5.0-LAB-V6-R2, Blocking
PR-20260916-LAB-V6R1-1.** Codex's
[review of the completed §7 delta](project-review-2026-09-16-reserved-laboratory-v6-provisioning-remediation.md)
accepted V11, V7's exclusion, the read-only verification boundary and the three
reported stop conditions, and found one Blocking defect in the applier: after
its `mkdirat` succeeded, a failure in the `open`, `fchown`, `fchmod` or
read-back path escaped as a raw `OSError` with the directory already on disk and
no identity recorded, and the handled parent-barrier failure returned
`applied == ()` while the same result said the object was visible. **Every
failure after a successful `mkdirat` is now a closed refusal that carries the
created object**: six classifications, the object returned in
`ProvisioningRun.applied`, `(st_dev, st_ino)` preserved wherever the object can
still be observed, and an object whose identity was never established reported
as residue that guarded rollback refuses. §7.1's applier row and §9.2 row **87**
state it. Nothing else moves: V11's definition, V7's exclusion, the V7-absent
fail-closed state, the separation of provisioning identity from declared owner,
the read-only verification boundary and the pre-`rmdir` emptiness check are
unchanged, and **LAB-V6-1, LAB-V6-2 and LAB-V6-3 remain open maintainer stop
conditions**. Passages this remediation changed are marked *amended 2026-09-16,
V6-R2 remediation*. **Nothing was applied to any host**, **I3 stays
unconfirmed**, V6 remains performed-but-not-closed, no finding is closed and no
preflight, provisioning or execution is authorized.

**This revision supersedes
[`phase-5-0-reserved-laboratory-runner-contract-r5.md`](phase-5-0-reserved-laboratory-runner-contract-r5.md)
in its entirety**, which supersedes
[r4](phase-5-0-reserved-laboratory-runner-contract-r4.md),
[r3](phase-5-0-reserved-laboratory-runner-contract-r3.md),
[r2](phase-5-0-reserved-laboratory-runner-contract-r2.md) and
[revision 1](phase-5-0-reserved-laboratory-runner-contract.md). All five are
preserved as the submissions their reviews answered, r2, r3, r4 and r5 each
carrying a dated supersession and erratum notice. Where any two disagree, **this
one is the proposal and the earlier ones are history.** No contradictory r5 row
is left authoritative: §§1–4 and §8 are carried forward, and §§0 and 5–10 replace
r5's.

It answers the September 11 R5 re-review's single Blocking finding
**PR-20260911-R5-1**: the harness's completion recorded a reservation id and
nothing stored bound it to the run, so a release of reservation `A` published a
valid RELEASED entry and then a valid completion into an already-started harness
run `B`. **This is a missing identity binding, not a reason to redesign the
lifecycle store.** The r5 architecture, the terminal order and the existing
modules are kept; one field is added to one entry kind and five values are
required to agree.

It also carries r5's answers to **PR-20260911-R4-1**, **PR-20260911-R4-2** and
**PR-20260911-R4-3** forward, with R4-1's positive technical recommendation
recorded and R4-2 and R4-3 still **open** pending this review — no finding is
closed here on the implementer's authority.

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

**One distinction was new in r4 and it carries §5.** A **design inference** —
"the specified order implies this" — is a **[P]**, never a **[D]** and never an
**[M]**. §5.6 depends on exactly one, names it as one, and says what would
falsify it.

**A third distinction is new in r6 and it carries §§5.5 and 5.11.1.** A
**durable binding** is a fact a record stores, and a **checked claim** is a value
a caller supplies. The two are never interchangeable, and a claim is only ever
compared with a binding, never trusted in place of one. r5's harness completion
carried a reservation id as a claim with no binding on the other side of the
comparison, which is R5-1 in one sentence. §5.5 adds the binding to the
`participant_started` entry and §5.11.1 states the comparison.

**A second distinction is from r5 and it carries §§5.11 and 5.12.** A
completion condition is either **lifecycle-owned** or **external**, and the two
are not interchangeable. A lifecycle-owned condition is a fact about an
operation this protocol itself performed, and it is **derived** from that
operation's outcome. An external condition is a fact about the host — a process,
a backend, a tree — and it is **injected by a named observer** and attributable
to them. r4 had no such distinction, so the harness's two conditions, which are
facts about a release this protocol publishes, were supplied as observations;
that is how a completion came to assert a release that had not been published.
**The model does not claim to verify a real process or a real database backend,
and every external condition remains an injected, attributed claim.**

### 0.1 What the reservation changes, and what it does not

Unchanged from revisions 1, 2 and 3, and restated because every row below
depends on it:

| | Before the reservation | After it |
|---|---|---|
| An unrelated cooperating writer substitutes an object mid-run | possible, and undetected | excluded by the lock plus the pre-admission inventory **[P]**; a detected violation invalidates the affected evidence |
| A host administrator substitutes an object mid-run | possible | still possible. Trusted not to; not prevented, and not claimed to be **[A]** |
| **This run's own experimental writers** substitute an object mid-run | possible | **still possible.** This is EH-R16-1, and §1 is the whole of this document's answer to it |

---

**§§1 through 4 are carried forward unchanged**, as they were in r4 and r5.
Neither the R3, the R4 nor the R5 re-review made a finding against them. The R3 re-review recorded
that R2-2's named design corrections — the usable `O_RDONLY` directory
references and the recovery-parent barrier — are satisfactory, and that R2-3's
corrected post-unlink claim should be closed; the R4 re-review preserved those
positive recommendations along with the R2 state-shape repair, the successor
directory barrier under the file-before-rename writer contract, the distinction
between process restart and power loss, the accounting for all seven
participants, and the C1 → C2 → C5 ordering with the withdrawn JNL-47 criterion
split. **The R5 re-review added one positive recommendation to that list** — R4-1's
reservation state machine, recommended for closure of that specific defect and
recorded here rather than closed. They are reproduced here rather than cited so
that this document is the complete contract.

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
| Permitted uses | **only** as the `dirfd` argument of `openat`, `mkdirat`, `unlinkat`, `linkat`, `renameat`, `fstatat`, `execveat`; and `fstat` of itself. *Amended 2026-09-15, D1: `linkat` and `renameat` replace `renameat2`* | **only** `fsync`, and `fstat` of itself |
| Not permitted | read, write, `fsync`, `ioctl` **[D]** | use as a `dirfd`, so that a reader can tell the two apart by their use sites |
| Lifetime | the whole run, held by the executor | the whole run, held by the executor |
| Transfer | inheritance across `fork`/`execve` with `FD_CLOEXEC` cleared, and by nothing else | **never transferred.** No experimental step receives a synchronizable descriptor |

**A third, short-lived descriptor exists for one operation — amended
2026-09-15, D2.** `readdir`
requires a descriptor with read access, which the traversal descriptor does
not have **[D]**, and the synchronizable descriptor may not be used as a
`dirfd`, which is how a reader tells the two apart by their use sites. D20 is
opened `"."`-relative to the traversal descriptor of the directory being
listed, so it resolves **one component that is the directory itself** and
reaches no object the traversal descriptor does not already refer to. It is
used for exactly one listing and closed before the listing returns. The
implementation's listing is one `os.listdir`, which duplicates the descriptor
and issues `fcntl` (`F_DUPFD_CLOEXEC`, `F_GETFL`, `F_SETFD`), `fstat`,
`getdents64`, `lseek` and `close` on the duplicate — that is, `fdopendir`,
`readdir`, `rewinddir` and `closedir`. A trace of that sequence on this
workstation shows exactly those calls; it is not an observation of the target.

It is **never** retained, never transferred, never synchronized and never used
as a `dirfd`. A listing is a read of names and establishes nothing about any
object those names resolve to; every such object is reached afterwards through
the traversal descriptor and compared, exactly as it is today.

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

**`R = /var/lib/fb-evidence-p5-0`** — the sole canonical disposable root: the
approved target's own `root_path`, normally created exclusively by the reviewed
concrete plan's `mkroot` and **not** by prerequisite provisioning. The one
narrow exception is the separately armed I3 verifier, which may create and
remove temporary `R`/`R/bin` topology solely under C-P5.0-LAB-I3-D1 (§7.3,
decision B; §7.4 is its procedure, and the verifier holds `R`'s parent under its
own role name and never registers `plan.EVIDENCE_ROLE` — *amended 2026-09-19,
C-P5.0-LAB-I3-R2*;
`provisioning.EVIDENCE_ROOT` reads it from `approved_target.APPROVED_TARGET`
rather than restating it). Its final component is the one
`targets.validate_mutation_root` admits, so the `"<run>"` name C1's `mkdirat` and
§1.4.1's by-name `fstatat` resolve **is `R`'s own final component** and no
directory above it. **`R`'s parent is `/var/lib`** — root-owned, not group- or
other-writable, administrator-only **[A]** (§1.3.2, §10) — and that parent, not a
provisioned evidence directory, is the object D1 holds. The withdrawn
`/opt/freedom-blades/evidence/<run>` form this inventory previously stated as
current defines nothing here; it survives only where it is marked as design
history (§1.4.1, §7.2, §7.3) — *amended 2026-09-17, C-P5.0-LAB-V6-D-R1, on
Blocking PR-20260917-LAB-V6D-R1-1*. **Owner** is the executor in every row:
one long-lived privileged process per reservation, created before the first
effect, not exiting until cleanup has classified §2.13.2b state.

| # | Descriptor | Object | Flags | Lifetime | Permitted uses | Transfer |
|---|---|---|---|---|---|---|
| D1 | `evidence_pathfd` | ~~`/opt/freedom-blades/evidence`, V11~~ — **`R`'s parent, `/var/lib`**: the directory `R` is created in, root-owned, not group- or other-writable, administrator-only **[A]**, and **not** a provisioning item (§7.3, decision C). The provisioned evidence root this row formerly named is withdrawn with V11 (§7, §7.3); `R` is the approved target's own `/var/lib/fb-evidence-p5-0`, created by the reviewed concrete plan, and nothing stands between it and this descriptor — *amended 2026-09-17, C-P5.0-LAB-V6-D; object corrected to `R`'s parent 2026-09-17, C-P5.0-LAB-V6-D-R1, matching `executor`'s "the disposable root and its parent" and `plan.EVIDENCE_ROLE`*. No production caller registers this role and registration stays deferred (decision D) | `O_PATH\|O_NOFOLLOW\|O_DIRECTORY` | run | `dirfd` for C1's `mkdirat` and for the by-name `fstatat` of §1.4.1. **These two, and no `linkat`**: no exclusive publication happens in this directory (§7.2(5)) | none |
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
| **D20** | **`listing_fd`** | **any directory this design lists: the recovery parent, `<run-id>`, the ledger directory and `/etc/postgresql/16/main`** | **`O_RDONLY\|O_NOFOLLOW\|O_DIRECTORY`, obtained by `openat(<that directory's traversal descriptor>, ".", …)`** | **one listing only, closed before the call that opened it returns** | **one directory read: `getdents64`, with the `fcntl`, `fstat`, `lseek` and `close` that `os.listdir` issues on its duplicate (§1.3.2). Never a `dirfd`, never `fsync`. Amended 2026-09-15, D2** | **never** |

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
prevention.

**Where `R` lives, and why the `/opt` form below is historical** — *amended
2026-09-17, C-P5.0-LAB-V6-D*. This subsection was written against
`R = /opt/freedom-blades/evidence/<run>`, whose root-only claim rested on the
*entry* being root-only as well as the directory. V6 found the parent
`/opt/freedom-blades` as `1001:1001 0755`, so `ubuntu` — every participant's
identity — could rename or unlink the `evidence` entry whatever mode V11 put on
the directory, and **the administrator-only exposure argument did not hold on
`oracle-test`**. The maintainer **withdrew the location** rather than widening
the rule or re-owning a path that holds the repository worktree. The sole
canonical `R` is `/var/lib/fb-evidence-p5-0` — the approved target's root,
created by the reviewed concrete plan, under a `/var/lib` that is root-owned and
not group- or other-writable. The `/opt/freedom-blades/evidence` form is
retained **only in this dated paragraph**, as the design history that led to that
decision, and states nothing operative. §1.3.3's inventory preamble and its D1
row now state the canonical topology directly — `R = /var/lib/fb-evidence-p5-0`
and D1 on its parent `/var/lib` — rather than leaving a withdrawn path in a
current table to be read against an amendment elsewhere, and C1's `"<run>"` is
`R`'s own final component under that topology — *amended 2026-09-17,
C-P5.0-LAB-V6-D-R1, on Blocking PR-20260917-LAB-V6D-R1-1*.

#### 1.4.2 Provisioning

| # | Effect | Object / bytes | Resolution | Descriptor | Prerequisite | Enforcement immediately before the effect | Protection |
|---|---|---|---|---|---|---|---|
| P1 | create `R/bin`, `R/before`, `R/journal`, `R/probe`, `R/probe-ro` | five directories | `mkdirat(D2, name, mode)`, exclusive, one call per name — **replacing `install -d <path>`** | D4 opened on each success; held for the run | D2 is the descriptor C1 created | exclusive creation: an existing entry is `EEXIST` and refuses | **B1** |
| P1b | **make the five entries durable** | `R`'s entries | `fsync(D3)` — **an `O_RDONLY` descriptor, obtained and bound per §1.3.2** | D3, held for the run | P1 succeeded for all five | a failure here refuses P2 and everything after it | **B2** |
| P2 | install the reviewed case program | the reviewed bytes, held in memory | `openat(D4.bin, ".case-program.tmp", O_CREAT\|O_EXCL\|O_WRONLY\|O_NOFOLLOW, 0500)`; `write` the held buffer; `fchown`; `fchmod 0555`; **`fsync(D16)`**; `linkat(D4.bin, ".case-program.tmp", D4.bin, "case-program", 0)`; `unlinkat(D4.bin, ".case-program.tmp", 0)`; **`fsync(D5.bin)`** after both — **replacing `install -m 0555 src dst`**; *amended 2026-09-15, D1* | D4.bin and D5.bin for the run; D16 for the write; D6 opened on the result and held | the source bytes digest to `materialization.REVIEWED_DIGESTS` | the bytes written are the bytes digested, from one buffer. `O_EXCL` proves the temporary name was free; `linkat`'s `EEXIST` proves the final name was free **[D]** | **B1 + B2** |
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
| M1 | write the reviewed `pg_hba.conf`/`pg_ident.conf` | reviewed bytes, held in memory | `openat(D9, "<name>.tmp", O_CREAT\|O_EXCL\|O_WRONLY, 0640)` → D16; write; `fchown`; **`fsync(D16)`**; `renameat(D9, tmp, D9, name)` (*D1*); **`fsync(D10)`** | D9 traversal and **D10 synchronizable**, both held for the run | **§2.3's publication reported `mutation_permitted`** — every barrier crossed | the publication's barrier set is re-checked; a missing barrier refuses **before** M1 | **B2**; destination parent is root-only **[A]** |
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
| P2 | descriptor comparison | **B1 + B2**, `O_EXCL` + held buffer + exclusive `linkat` (*D1*) + two barriers on correctly-moded descriptors | in-place mutation of the source before the digest; §2.4's rule applies |
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
`R`, not under the withdrawn `/opt/freedom-blades/evidence` (V11, withdrawn
2026-09-17 — §7, §7.3; nothing is provisioned under `/opt`), and not under any
path an experimental identity can write — *withdrawal noted 2026-09-17,
C-P5.0-LAB-V6-D-R1*.

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
   0400)` → D16; write; **barrier 2**; `linkat(D13, tmp, D13, "<name>", 0)`;
   `unlinkat(D13, tmp, 0)`; **barrier 3** — *amended 2026-09-15, D1*;
10. write the record the same way: destination path, source identity from (5),
    `digest`, byte length, run id, reservation id, the capture time and the
    capturing identity; **barrier 4**; link and unlink; **barrier 5**;
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
   `renameat(D9, "<name>.restore.tmp", D9, "<name>")` — *amended 2026-09-15,
   D1*.
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

## 5. The complete lifecycle — R3-1 to R3-3, R4-1 to R4-3, and R5-1

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

**The R4 re-review then found three more, and all three are one kind of
mistake**: r4 stored the right records and read them wrongly.

**R4-1, Blocking — a stale terminal entry hid a newer active reservation.**
§5.5's checker remembered whether an id had *ever* been admitted and never asked
whether a transition belonged to the reservation that is currently active.
`finished` was consulted only for a new `admitted` entry. So
`FIRST_USE → ADMITTED A → RELEASED A → ADMITTED B → RUNNING B → RELEASED A`
was accepted, the derivation took the **last** entry, reported A released, lost
the unresolved B, and admitted C. A stale duplicate publication or a
syntactically valid corrupt history could therefore authorize reuse. The
analogous repeated operator-recovery entry had the same missing predecessor.

**R4-2, Blocking — participant completion was not bound to the started run.**
§5.11's ledger chose the completion conditions from the **caller's** participant
and appended to the **caller's** filename, comparing neither with the stored
start. `begin(run_id="web-1", participant=WEB_SUITE)` followed by
`complete(run_id="web-1", participant=FOUNDRY_TESTS)` on Foundry evidence
published, and admission returned true with an unfinished web run outstanding —
Foundry completion observes neither the web suite's database backends nor its
fixture cleanup. The survey declared a file settled from its last entry's kind
alone, so a lone `participant_completed` entry with no start was a settled run,
and an empty evidence string was proof because the field was present. In the
same boundary, an omitted ledger skipped both the re-seal and the survey, so
unavailable accounting read as an empty, settled one.

**R4-3, Important — the successful trace assumed a future release.** The harness
profile requires `release()` to have returned RELEASED **and** the release entry
to have reached durable storage, while §5.7 published participant completion at
T11 and RELEASED at T12. No process could obtain that observation in that order.
The successful test hid it by injecting both facts while the record still said
RUNNING, so a green row certified a sequence with no reachable successful path.

**What r5 changed, in one sentence each.** §5.5 validates every transition
against the **current reservation** and its current state, over
`reservation.TRANSITIONS` rather than a second table. §5.11 adds one
participant-history validator that both writers and the survey apply, binding
run, participant, identity, filename and evidence content to the stored start,
and requires the ledger rather than tolerating its absence. §5.12 states the
achievable terminal-publication order and the argument that no half of it
authorizes reuse. §5.13 says which layer owns which check.

**The R5 re-review then found one more, and it is the binding those three
repairs still did not establish.**

**R5-1, Blocking — a release could settle another reservation's harness run.**
`CompletionEvidence` carried a reservation id for the harness and §5.11.1's P7
checked only that it was **non-empty**. The stored `participant_started` entry
carried no reservation field at all, so there was no stored fact on the other
side of that check; and `conclude_reservation()` took an independent
caller-supplied `run_id` without comparing it with `request.reservation_id`. The
reviewer's reproduction, through the same fixture and the same public APIs:

```text
initialize
ADMITTED A
begin B-harness as HARNESS_CLI
RUNNING A
conclude_reservation(reservation=A, run_id=B-harness)

{'concluded': True, 'release': True, 'completion': True,
 'completed': ('B-harness',)}
```

A's release evidence published a valid RELEASED entry for A and a valid
completion into B's already-started run file. If B was the outstanding ledger
account for a different reservation, A's release settled it and the final
conjunction admitted a successor once no other unsettled file remained. r5 §5.12
claimed the completion *"names the reservation it concluded, so the binding can
be checked."* **It recorded the name and had nothing to check it against**, and
that sentence is withdrawn in r5's erratum.

**What r6 changes, and it is deliberately narrow.** §5.5 adds one field to one
entry kind: the `participant_started` entry names the reservation the run owns,
and the schema version is raised so an r5 record is refused by name rather than
reinterpreted. §5.11.1's P7 becomes an equality against that stored field
instead of a presence check, and gains P9 for the start's own shape. §5.12 gains
**step 0**, a binding check before the release decision. §5.13 records where the
comparison lives. **Nothing else moves:** no new isolation mechanism, no
scheduler, no change to the lifecycle store's architecture, and no change to the
permission and provisioning delta, which stays at ten unapproved items.

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
schema=2
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
| `schema=` | in `{2}`, or refuse `UNSUPPORTED_SCHEMA` | a reader that interpreted a record written under other meanings by the meanings it happens to know is guessing. **Raised from 1 in r6**, and `1` is *not* in the accepted set |
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

**The exact field set per entry kind, since r6 changes one of them.** The
permitted set for a kind is exactly the six common fields plus the kind's own,
and a field outside it, or a missing one, is `MALFORMED`.

| Entry kind | Fields beyond the six common ones |
|---|---|
| `first_use` | `basis` |
| `admitted`, `running` | `reservation` |
| `released` | `reservation`, `released_at` |
| `quarantined` | `reservation`, `reason` |
| `recovering` | `reservation`, `recovery_owner` |
| `operator_recovered` | `recovers`, `reference` |
| `participant_started` | `run`, `participant`, `identity`, **`reservation`**, `effects` |
| `participant_completed` | `run`, `participant`, `identity`, `evidence` |
| `participant_recovered` | `run`, `participant`, `identity`, `reference` |

**`participant_started.reservation` is the whole of R5-1's stored repair.** It is
published before the run's first effect, it is never rewritten, and it is the
only fact the protocol keeps about which reservation a run belongs to.

| Property | Rule |
|---|---|
| Shape | **one representation, required in both directions.** A participant with lifecycle-owned completion conditions — today only the harness — carries a reservation identity. The six whose conditions are external carry the field **exactly empty** |
| Optionality | **none.** A field that may or may not be populated carries no information, which is the state r5's completion field was in. Missing, empty, whitespace-only, padded, or changed between entries all refuse for the harness; any non-empty value refuses for the six |
| Grammar | the value equals its own stripped form, contains no line break, and contains no `\|` — the completion evidence's field separator. An identity that cannot survive the codec that transports it is refused where it is written, not where the comparison would silently fail |
| Where it is checked | **before an append and on read**, by the one participant-history validator of §5.11.1, which the record store looks up for itself |
| What it is not | **not derived from the run's filename.** No prefix, suffix or other string convention over a run name is read, checked or relied on. `RES-1-harness` is a name; the stored field is the fact. A run named `RES-9-harness` and started for `RES-1` belongs to `RES-1` |

**No filename convention is adopted, and that is a decision rather than an
omission.** A convention would be a second place the binding could be read from,
and a second place is a second chance for the two to disagree — which is the
shape of every finding from R4-1 onward. If a later revision wants one as an
*additional* invariant it must state its grammar, validate it on the writer and
the reader path, and argue its necessity; it may never replace the stored field.

**The compatibility consequence for r5 records, stated plainly.** An r5
`participant_started` entry declares `schema=1` and carries no reservation field.
Such a record is refused as `UNSUPPORTED_SCHEMA`, which is a named refusal an
operator can act on. It is **not** read as a start whose reservation is empty:
that would read an r5 harness run as one whose binding happens to satisfy
whichever branch the reader reached, which is R5-1 with extra steps. A run file
declaring schema 2 and omitting the field is `MALFORMED` for the same reason.
There is **no dual-meaning parser and no migration path in the reader**: a
laboratory holding r5 run files is re-initialized, or its outstanding runs are
recovered by an attributed operator entry, before r6's protocol runs. Both
refusals block every successor, so neither is a silent widening.

**The order rules, corrected in r5 and stated for this protocol and no wider.**
r4's version is superseded; where the two disagree this one is the proposal.

The history is walked as a state machine that carries **one current
reservation** and its current state.

1. A first use appears once, at sequence 1, and is never appended later.
2. The **current reservation** is the one the most recent `admitted` entry
   named. Every `running`, `released`, `quarantined` and `recovering` entry
   names that reservation; an entry naming any other is refused rather than
   filed against it. **This is R4-1.**
3. A transition of the current reservation is legal only when it appears in
   `reservation.TRANSITIONS`. **There is no second transition table**: the
   accepted state machine is the one the reservation module already states, and
   a history that disagrees with it is refused rather than reconciled.
4. `released` and `quarantined` are terminal and name no successor. A further
   entry for a finished reservation — a duplicate terminal event, a stale
   release, a repeated recovery — refuses. It is never read as a later state.
5. A reservation id is used once. A new `admitted` may not name an id this
   history has already seen, so a terminal identity never reappears.
6. An `admitted` entry is published only when the current reservation **admits a
   successor**: there is none, it `released`, or it was `quarantined` and an
   operator recovery has been appended for it. `admitted`, `running`,
   `recovering` and an unrecovered `quarantined` all refuse.
7. An `operator_recovered` entry names the **current** reservation, that
   reservation is `quarantined`, and it has not been recovered already. The
   quarantine entry stays where it is. **The recovery is an attributed addition
   that permits a new reservation; it neither revives nor rewrites the terminal
   one it recovers**, and the distinction between the quarantined run's terminal
   state and permission for a new run is preserved exactly there.
8. **The current reservation and its current state are the decision input** —
   not the last entry, and never an earlier, more convenient admitting one. A
   history these rules refuse produces no decision input at all.

**Duplicate delivery refuses explicitly, and that is the stated policy.** R4-1
permits either an idempotent handling that appends no new terminal event and
hides no newer run, or an explicit refusal. This contract refuses: the record is
append-only, so a second delivery would either add an entry the first already
covers or be silently discarded, and choosing between those is not a decision a
reader should take alone. The refusal names the duplicate as a duplicate, and
the first terminal entry still stands and still admits the next reservation.

**The same check runs on both sides of the store.** A publication validates the
history it is about to write **before any byte is written**, so a refused append
leaves the stored bytes exactly as they were and leaves no temporary behind. A
reader validates the complete stored history it read. Neither excuses the other:
a corrected writer cannot unwrite a record an earlier revision published, and a
correct reader is no reason to publish a contradictory history.

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
                  →  compare the record's two names   (§6.2, D1 remediation)
                  →  read the record's bytes through a descriptor
                  →  parse      (§5.5's bounded schema)
                  →  check order(§5.5's history rules)
                  →  validate   (reservation.validate_lifecycle)
                  →  survey     (§5.11's ledger)
                  →  decide
   [if admitted]  →  publish this participant's own started entry
                  →  issue effects
   [six others]   →  observe the external completion conditions
                  →  publish completion
                  →  release the lock
   [executor]     →  evaluate the release decision   (§5.12 step 1)
                  →  publish RELEASED                (§5.12 step 2)
                  →  publish its own completion      (§5.12 step 3)
                  →  release the lock                (§5.12 step 4)
```

**The executor's tail changed in r5 and §5.12 is the whole argument for it.**
r4 published participant completion before RELEASED while requiring the
completion to observe the release, which no process could do.

**No participant reads before it re-seals, and no participant writes before it
reads.** A reader that acted on content it had not re-sealed is revision 3.

**The publication comparison, and why it is a step of its own — *amended
2026-09-15, D1 remediation*.** One `fstatat` on the record's temporary and one
on its final name, immediately after the re-seal and **before** the bytes are
read. A temporary that resolves refuses **every** participant, whatever the
bytes beside it say. It is not part of the parse and it cannot be, because r6
§6.2's second interruption state leaves a *valid, complete* record under the
final name: the publication that wrote it never finished, and nothing in its
bytes records that. Codex's **PR-20260915-LAB-D12-1** is exactly that gap — the
six ordinary participants admitted on such a record and only the harness refused
later, at T7, when its own publication met the temporary. A failed `fstatat` is
a failed observation and **not** an absent temporary, on the same rule §5.9
applies to an unreadable lock. The two names are left exactly as they are:
removing one is an operator recovery (§5.10, §6.2) and never a participant's.

### 5.7 The transition and publication table — every phase, provisioning to reuse

**How to read it.** One row per transition, split across two tables because ten
columns do not fit one. `T-n` is the same transition in both. **Every row is
[P]** — proposed, unbuilt — except where a **[M]** names the model test that
exercises it. Nothing here is **[D]** except the barrier semantics §5.6 cites.

**Table A — actor, custody, bytes and barriers.**

| # | Transition | Actor | Lock custody | Bytes read / written | Identity binding | File barrier | Directory barrier |
|---|---|---|---|---|---|---|---|
| T0 | provision the directories, the lock inode and the ledger directory | operator, root, out of band | none; the lock does not exist yet | none | none yet | — | the provisioning tool's own |
| T1 | initialize the first-use record | operator, root, out of band | none; nobody may be running | writes the whole history, one entry | host **and** approved target, plus attester and basis | `fsync` the temporary's bytes | `fsync` the laboratory directory after the exclusive `linkat` and `unlinkat` (*D1*) |
| T2 | take the cooperative lock | any participant, `ubuntu` | acquires it | none | none | — | — |
| T3 | **re-seal** the record's and the ledger's parent entries | any participant, `ubuntu` | **holds it** | none | none | — | `fsync` both parents, `O_RDONLY`, no write permission |
| T4 | **compare the record's two names (*D1 remediation*)**, then read, parse, check order, validate | any participant | holds it | **`fstatat` on the temporary and the final name**, then reads the whole record | compares the record's host and target with this run's; **a temporary that resolves refuses all seven before the bytes are read** | — | — |
| T5 | survey the ledger | any participant | holds it | reads every run file | each run file's own host/target | — | — |
| T6 | publish `participant_started` | that participant, `ubuntu` | holds it | writes its own run file, one entry | host, target, participant, identity, declared effects **and — new in r6 — the reservation the run owns, empty for the six** | `fsync` the temporary | `fsync` the runs directory after the exclusive `linkat` and `unlinkat` (*D1*) |
| T7 | publish `admitted` | executor, root | holds it | reads the history, writes it plus one entry | host, target, reservation id | `fsync` the temporary | `fsync` the laboratory directory after the rename |
| T8 | publish `running` | executor, root | holds it | same | same | same | same |
| T9 | issue the reviewed effects | executor, root | holds it | none of this record | — | — | §2.3's capture barriers |
| T10 | observe the **external** completion conditions, or evaluate the release decision | the six participants observe; the executor calls `release()` over its own observed evidence | holds it | none | — | — | — |
| **T10a** | **check the reservation binding — new in r6, and it precedes T10 for the executor** | executor, root | holds it | **reads its own run file** | **exact equality between the stored start's reservation and `request.reservation_id`; the stored participant is the harness; the stored phase is in progress** | — | — |
| T11 | publish `released` — **reordered in r5** | executor, root | holds it | reads the history, writes it plus one entry | host, target, reservation, released-at, author | `fsync` | `fsync` |
| T12 | publish `participant_completed` — **reordered in r5** | that participant; the executor last | holds it | reads its run file, writes it plus one entry | as T6, plus the observer's name and the run; **and for the executor the reservation is taken from the stored start rather than from the caller — new in r6** | `fsync` | `fsync` |
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
| T1 | create exactly one record | **publication succeeded, barrier failed**: visible, not durable. A stop between `linkat` and `unlinkat` is §6.2's second interruption state (*D1*) | the readable record and no trace of the failure. **This is R3-1.** In §6.2's second state a readable record is also reachable **beside its temporary**, and every participant refuses on it at T4 — *amended 2026-09-15, D1 remediation* | the next participant's re-seal, or an operator if it fails. For the leftover temporary: an operator, on §5.10's recovery, **after the immediately preceding `(st_dev, st_ino)` comparison** | **[M]** `test_the_reviewers_reproduction_still_reproduces_against_the_writer`, `test_a_successor_establishes_the_durability_the_writer_could_not`; rows 74–78 |
| T2 | none | lock unreadable | wait or refuse; an unreadable lock is not an unheld one | — | **[M]** `test_a_concurrent_participant_arriving_during_initialization_waits` |
| T3 | **none. It is a barrier, not a write** | the barrier fails | nothing was taken and nothing published | the record's recovery owner, attributably | **[M]** `test_a_failed_re_seal_refuses_pending_an_attributable_recovery` |
| T4 | none | bytes malformed, truncated, contradictory or wrongly bound | the same refusal, deterministically | operator | **[M]** `test_a_tampered_record_refuses_and_is_never_normalized` (ten cases) |
| T5 | none | a run file unreadable, or a leftover temporary | the run counts as unsettled and blocks | operator | **[M]** `test_an_interrupted_ledger_publication_blocks_and_is_not_cleaned` |
| T6 | **none yet — this precedes the first effect** | published or not | if absent, no effect was issued either; if present, the run blocks until settled | operator | **[M]** `test_the_non_reusable_state_is_persisted_before_the_first_effect` |
| T7 | **none yet — ADMITTED precedes the first effect of any kind** | as T1, at a different entry | `admitted` stands and refuses every successor | operator | **[M]** `test_every_publication_point_carries_the_same_uncertainty` |
| T8 | none yet — RUNNING precedes the first **mutating** step | as T1 | `running` stands and refuses every successor | operator | **[M]** same |
| T9 | the reviewed mutation, capture, materialization, restoration, cleanup | any of §§1–2's failure modes | whatever §2's barriers made durable; the record still says `running` | operator, from §2.2's independent store | **[P]** — needs the mechanism |
| T10 | none | a condition unobserved, or the release decision quarantines | the run stays in progress and blocks; a quarantining decision publishes neither terminal entry and leaves the reservation where it was | operator | **[M]** `test_a_clean_wrapper_exit_and_a_free_lock_are_not_completion_evidence`, `test_a_refused_release_decision_publishes_neither_half` |
| **T10a** | **none. It is a comparison, not a write** | the run file is absent, unreadable, invalid, started by another participant, already settled, or bound to another reservation | **nothing was published at all**: the reservation stays where it was and the named run stays exactly as it was, still blocking every successor | operator, through an attributed `participant_recovered` for the run that is genuinely outstanding | **[M]** `test_the_reviewers_wrong_reservation_completion_reproduction`, `test_the_refused_conclusion_leaves_a_released_entry_nowhere`, `test_concluding_a_non_harness_run_refuses`, `test_concluding_an_already_settled_run_refuses` |
| T11 | none | **failed release publication**: renamed, barrier failed | `released` is visible; the successor re-seals it and it survives. If the rename never happened, `running` stands and refuses. **Either way the executor's own run is still started in the ledger and blocks** | the successor's re-seal, else an operator | **[M]** `test_every_publication_point_carries_the_same_uncertainty`, `test_a_release_that_never_reached_its_barrier_still_refuses_a_successor`, `test_no_intermediate_terminal_state_authorizes_reuse` |
| T12 | none | completion published or not | absent ⇒ the run blocks, **even though the reservation says `released`**; present ⇒ both halves hold and a successor may admit | operator, through an attributed `participant_recovered` | **[M]** `test_clean_completion_admits_the_next_participant`, `test_a_restart_between_the_two_terminal_publications_is_blocked_by_the_ledger` |
| T13 | none | the crash beat the quarantine | the **previous** entry stands, which refuses. Absence of a quarantine is never an ending | operator | **[M]** in the failed lifecycle trace |
| T14 | none | as T12 | `recovering` refuses; the deadline authorizes nobody | the named recovery owner | **[P]** the deadline path; **[M]** the refusal |
| T15 | none | **interrupted operator recovery**: the recovery entry renamed, barrier failed | the recovery is visible and the successor's re-seal makes it durable. If the history could not be read, the append refuses and **nothing is overwritten** | operator | **[M]** `test_recovery_never_overwrites_a_valid_prior_history`, `test_an_unreadable_history_is_never_replaced_by_a_recovery` |
| T16 | none | as T15 | the started entry stands and the run blocks | operator | **[M]** `test_a_verified_recovery_admits_a_new_run_without_a_dead_end` |
| T17 | none | the holder died instead of releasing | the kernel released the lock. **The record decides, not the lock** | — | **[M]** carried from r3's participant table |
| T18 | whatever its own profile permits | as T4 | as T4 | as T4 | **[M]** `test_a_complete_successful_lifecycle_admits_a_successor_from_stored_evidence` |

**Three consequences the re-review asked to see stated.**

* **A wrong reservation binding is T10a and it publishes nothing.** The check
  precedes the release decision, so the release-before-completion order is never
  entered. This placement is deliberate: checking the binding at T12 instead
  would publish RELEASED and then refuse the completion, leaving a reservation
  that reads terminal beside a run that can never settle — an intermediate state
  needing an operator recovery for a mistake that was detectable before any byte
  was written. **What happens to the wrongly offered release entry is therefore
  that it does not exist.**
* **Failed release publication is T11 and it is covered.** A release that renamed
  without its barrier is made durable by the next participant's re-seal, and a
  release that never renamed leaves `running`, which refuses. In **both** cases
  the executor's own run is still `participant_started` in the ledger, so the
  release alone admits nobody — which is §5.12's argument for the order.
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

**Two admission conditions were new in r4** and both apply to all seven:

* the **re-seal** of §5.6 must have succeeded; and
* the **ledger** of §5.11 must hold no unsettled and no unreadable run.

**Three more are new in r5**, and all three apply to all seven:

* the stored reservation history must be **valid under §5.5's order rules**, and
  the disposition is derived from the **current reservation**, not the tail;
* every run file in the ledger must be a **valid participant history** under
  §5.11's binding rules. An invalid account of a run is not an account that it
  ended, so it blocks exactly as an unsettled run does; and
* **new in r6:** every run file's own reservation binding must be the shape its
  participant's profile requires, and a completion's evidence must name exactly
  the reservation its stored start owns. A run file that fails either is
  `invalid` and blocks, so a record r5 wrote, or a corrupt implementation writes,
  refuses on the reader's path and not only at a corrected writer; and
* the ledger must be **present and readable**. Contract §5.8 requires it for
  every participant, so **an absent ledger is a refusal and never an empty,
  settled one**. The intentionally isolated reservation-layer unit path is a
  separate, labelled function that decides a history alone and admits nobody on
  its own; the full protocol has no option to skip accounting. A provisioned
  ledger directory that was surveyed and found empty still admits — the refusal
  is for accounting that was not available, not for accounting that was empty.

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
| **Record's transitions do not belong to the current reservation** | **refuse, naming the current reservation and its state. New in r5 — R4-1.** A stale terminal entry is never read as the current state |
| **Record reuses a terminal reservation identity** | **refuse. New in r5** |
| **Any run unsettled or unreadable in the ledger** | **refuse, every participant, the harness and the reset included. New in r4** |
| **Any run file that parses and is not a run history** | **refuse. New in r5 — R4-2.** Terminal without a start, a completion by another participant, a changed identity, a run filed under another name, evidence whose content is absent or wrong |
| **The ledger is absent or unreadable** | **refuse. New in r5 — R4-2.** Unavailable accounting is not empty accounting |
| **A completion supplies a lifecycle-owned condition as an observation** | **refuse. New in r5 — R4-3.** Those are derived from the operations this process performed |
| **A leftover run-publication temporary** | **refuse and report it. It is not removed automatically** |
| **A leftover record-publication temporary** | **refuse, every participant, before the record's bytes are read — new in the D1 remediation, PR-20260915-LAB-D12-1.** The final name may carry a valid, complete record and still be a publication nobody finished. Report which of §6.2's three states it is and remove nothing |
| **The record's temporary cannot be observed** | **refuse. A name whose resolution is unknown is not an absent name**, exactly as an unreadable lock is not an unheld one |
| Crash, restart, lock free, record `ADMITTED` or `RUNNING` | **refuse.** No expiry and no free lock authorizes reuse |

### 5.10 Verified first use — a provisioning operation, proposed and unperformed

Carried from r3 §5.8, with three changes.

| | Value |
|---|---|
| Creator | the operator provisioning the host, as root, out of band. Not the harness, not a participant |
| Authority | the maintainer's approval of §7. **It is not approved** |
| Creation rule | exclusive creation: `O_CREAT\|O_EXCL` on the temporary, an exclusive `linkat` on the final name, then `unlinkat` of the temporary — *amended 2026-09-15, D1* |
| Durability | bytes synchronized, then link and unlink, then the containing entry synchronized |
| **Binding — changed** | the record names the host **and the approved target**, and initialization **refuses `binding_mismatch`** when either would differ from the approved one. r3 declared this refusal and had no branch that produced it |
| **Evidence — changed** | the attester's **name and basis are written into the record**, travel through the parser, and are **required by the validator**. In r3 they reached neither |
| **`not_durable` — changed** | still refuses, and the record may now be **visible**. r3 said *"nothing is treated as initialized"*, which was true of the writer and not of the filesystem. The successor's re-seal is what closes it |

Refusals and recoveries are otherwise r3's: `already_initialized` (read it),
`prior_use_not_excluded` (**never reinitialize**; establish the predecessor or
rebuild), `interrupted_initialization` (the temporary is reported by absolute
path and not removed. **Every participant refuses while it is there**, whether
or not the final record parses — *amended 2026-09-15, D1 remediation*. **If the
final name resolves to the same inode, the record was published** — §6.2's
second interruption state — so the operator removes only the temporary and
initialization is not repeated; *corrected 2026-09-15, D1*. **The `(st_dev,
st_ino)` comparison is required and must immediately precede the removal**: a
removal taken without one, or on a comparison that has since stopped holding,
removes an object nobody has identified, and both are refused rather than
performed — *amended 2026-09-15, D1 remediation*), `no_first_use_evidence` (obtain the attestation),
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
| 7 | harness CLI | the reviewed mutation and its restoration; the disposable root; the recovery store | `release()` returned RELEASED on observed evidence **and** the release entry reached durable storage. **Both are lifecycle-owned and are derived from §5.12's steps 1 and 2, never injected**, and **both are facts about the reservation the run's stored start names — new in r6** | the quarantine stays; an operator appends an attributed recovery; the recovered id is never reused | every §9.3 implementation check |

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

#### 5.11.1 One participant-history validator — R4-2

**New in r5.** r4 had no semantic check over a run file at all. The parser
validated field names, sequence and host/target; the ledger then chose the
completion profile from the caller's participant and appended to the caller's
filename; and the survey declared a file settled from its last entry's kind.
Every binding between the three was missing.

One validator now decides what a run file says, and **the same function runs
before an append and over the bytes a survey reads**.

| # | Rule | The path it closes |
|---|---|---|
| P1 | a run **begins with a start**. A terminal entry with no start refuses | a lone `participant_completed` file read as a settled run |
| P2 | the participant is one of the seven and is **stable** across entries. **The required conditions come from the operation that started**, never from a value the completion caller supplies; a caller's participant is a checked claim | R4-2's exact reproduction: a web run completed as the Foundry suite |
| P3 | the identity is stable across entries and is the participant's declared identity | a run whose account of who ran it changed between its two entries |
| P4 | the run id is stable and **binds to the name the file is stored under** | a run record filed under another run's name, surveyed as that run |
| P5 | there is **one terminal entry** and no second start | a duplicate terminal event, and a recovery appended over a completion |
| P6 | a completion's evidence **decodes to this protocol's evidence**, names **this run**, lists **exactly this participant's conditions**, and names an observer | an empty or arbitrary string that was proof because the field was present |
| P7 | a completion's evidence names **exactly the reservation the stored start owns**. Equality, both ways, not containment and not presence | **R5-1's exact reproduction**: a release of reservation `A` published as the completion of a run started for `B`. r5 checked that the field was non-empty, which is a check with nothing on the other side of it |
| P8 | a recovery carries its reference and its author, and P2–P5 apply to it exactly as to a completion | an unattributable recovery turning an unknown predecessor into a clean one |
| P9 | the **start** carries the reservation field in the shape its profile requires — an identity for a participant with lifecycle-owned conditions, exactly empty for one without — and that identity satisfies §5.5's grammar | a run that never durably said which reservation it belongs to, and a run claiming a binding its profile never establishes |

Host and target agreement, within the file and against the run being performed,
is the schema's own `CONTRADICTORY` / `WRONG_BINDING` pair from §5.5 and is not
repeated here.

**The evidence is a bounded encoding, not prose.** A completion entry carries the
run, the reservation (empty for the six), the observer and one field per stated
condition, in a form a reader decodes and compares. Anything that does not decode
is refused. This is what lets P6 check the evidence's **content and
completeness** rather than the presence of a field — and it is what makes an
empty string a refusal rather than a claim.

**The five values P7 makes equal, and why five rather than two — new in r6.**

| # | Value | Where it comes from |
|---|---|---|
| 1 | the reservation in the **stored start** | the durable record, published before the run's first effect. **The only one that is a binding; the other four are claims compared with it** |
| 2 | `ReservationRequest.reservation_id` | the caller concluding a reservation. Compared at §5.12's step 0 |
| 3 | `ReleasePublication.reservation_id` | the executor's own release publication. Compared before any completion evidence is built |
| 4 | `CompletionEvidence.reservation_id` | **written from value 1**, so a caller cannot choose it; compared with value 1 again on every read |
| 5 | the reservation the **terminal result** reports | the conclusion's own account of what it concluded |

Two would not be enough. r5 had values 3 and 4 agreeing with each other, which is
what made its claim look satisfied: the completion copied the reservation off the
publication, so the comparison was a value against itself. The binding has to be
a fact somebody wrote **before** the release existed, and that is value 1.

**The writer reads the stored start before it derives anything.** The completion
profile, the required conditions and the reservation written into the evidence all
come from the stored `participant_started` entry. A caller's `participant`,
`run_id`, reservation and release publication are **checked claims**: each is
compared with the stored record, and a disagreement refuses without writing a
byte. r5's writer took the profile from the caller and the reservation from the
publication, which is why its two safe-looking checks could both pass over the
wrong run.

**What the model still does not do.** It does not verify that a process exited,
that no backend remains, or that a tree was removed. Those are the six
participants' external conditions: they are **injected and attributable**, they
are listed in the table above as unconfirmed proof obligations, and I9 collects
them. A validated run history establishes that somebody stated the right
conditions for the right run and was named doing it; it establishes nothing
about the host.

### 5.12 The terminal publication order — R4-3

**The recommendation the re-review asked to be evaluated is adopted, and this is
the argument rather than a swapped pair of calls.**

| Step | What happens | Who | Under the lock |
|---|---|---|---|
| **0** | **check the reservation binding — new in r6.** Read the named run's stored history; require a valid harness run, still in progress, whose stored start owns exactly the reservation being concluded. A mismatch refuses and **publishes nothing** | executor, root | yes |
| 1 | **evaluate the release decision.** `release()` over the observed evidence returns RELEASED, or quarantines | executor, root | yes |
| 2 | **publish the reservation's `released` entry durably** — bytes, rename, containing entry | executor, root | yes |
| 3 | **publish the harness participant's completion**, whose two conditions are exactly the outcomes of steps 1 and 2 | executor, root | yes |
| 4 | **release the lock** | executor | it is released here and nowhere earlier |

**Why step 0 comes before step 1, and what it does to the wrongly offered
release entry.** The binding is the cheapest check and the one whose failure is
entirely the caller's error, so it is taken before anything is decided or
written. **The consequence, stated rather than left to inference: A's RELEASED
entry is never published.** The reservation record is untouched, so the
reservation stays in whatever state it was — `running` in the reproduction, which
refuses every successor on its own — and the run the caller named stays exactly
as it was, `participant_started`, still blocking every successor including the
harness and the environment reset.

**The intermediate state is not hidden; it is not created.** The alternative
placement — checking the binding at step 3 — would publish RELEASED durably and
then refuse the completion, leaving a reservation that reads terminal beside a run
that can never be settled by it. That state is recoverable, but it requires an
operator for a mistake a comparison could have caught first, and it puts a
terminal entry in an append-only record on the strength of a claim nobody
checked. **Step 0 is therefore the placement, and the wrongly offered release
entry has no existence to account for.**

**The bounded attributable recovery for the refused conclusion.** Two runs are
outstanding and each ends the only way the contract allows. The run the caller
wrongly named belongs to its own reservation: if that reservation is genuinely
outstanding it is concluded normally, and if its executor is gone an operator
appends an attributed `participant_recovered` entry for it. The reservation whose
conclusion was refused is then concluded against **its own** harness run, and the
successor admits on the stored release. Nothing is rewritten, no identity is
reused, and the quarantine path is untouched.
**[M]** `test_the_bounded_attributable_recovery_of_the_refused_conclusion`.

**Why the harness may know step 2's outcome.** The executor is the writer of the
release entry, in this process, holding the lock. Whether its own `fsync` on the
containing directory returned success is the one durability fact a writer
legitimately has. It is **not** a fact a successor has — that asymmetry is R3-1,
and §5.6's re-seal exists precisely because the successor cannot read it. The
correction therefore derives the condition from the writer's own call and
preserves the asymmetry rather than softening it. Nothing reads a stored
durability flag, and §5.5's "no stored durability flag, in any form" is intact.

**Why no half of this authorizes reuse.**

* **Before step 2** the reservation record still says `running`, and `running`
  refuses every successor. Nothing has changed for a reader.
* **Between steps 2 and 3** the record says `released` **and** the executor's own
  run is still `participant_started` in the ledger. §5.11's rule is that an
  unsettled run refuses every successor including the harness and the
  environment reset, so the release alone admits nobody. This is the window the
  re-review asked to be argued, and the still-started ledger entry is the whole
  of the argument.
* **After step 3** both halves hold: the reservation released and the run
  settled. That is the only state in which a successor is admitted.

**What a restart between the two publications finds.** The `released` entry,
whose durability the next participant re-establishes under the lock or refuses
(§5.6), and an unsettled harness run that blocks it either way. The recovery is
bounded and attributable: an operator appends a `participant_recovered` entry
for that run, after which a new reservation is admitted on the stored release.
Nothing is rewritten, the quarantine path is untouched, and the recovered run's
own id is never reused. A failure **inside** either publication before its
rename leaves a temporary, which §2.13.2b reports and never removes
automatically, so the recovery for those states begins with an operator removing
it by absolute path.

**A power loss in the same window is a different event and is kept separate.** It
discards what no barrier made durable, so a release that renamed without its
containing-entry barrier is simply gone and the record is back at `running`,
which refuses. The process-only restart is the case that leaves the visible
record and destroys only the writer's memory.

**Why not the reverse order.** Completing the participant first requires its
evidence to assert a release that has not been published — r4's contradiction.
The only way to keep r4's order would be to drop the publication requirement
from the harness's completion conditions, which would let a run be settled while
the record still said `running`; the reservation's own state and the ledger
would then disagree about the same run, and the disagreement would be resolved
in favour of whichever a reader consulted first. **No order may authorize reuse
from one satisfied half, and that is the constraint both alternatives fail.**

**Stale release evidence from another reservation refuses at step 1.**
`release()` compares the evidence's reservation, target and lock holder with the
request's, so a release of `RES-1` offered to conclude `RES-2` quarantines, and
neither terminal entry is published. **This is a different refusal from step 0's**
and both are kept: step 1 compares the *evidence* with the request, and step 0
compares the *stored run* with it. r5 had the first and not the second, which is
why a coherent release of A could still be applied to B's run.

### 5.13 Which layer owns which check

**Made explicit in r5**, because three of the four findings since r2 were a
check that existed at one layer and was assumed at another.

| Layer | Owns | Does not own |
|---|---|---|
| **Schema parsing** | magic, version, entry boundaries, the bounded field set per kind, duplicate keys, unknown kinds, sequence numbering, the terminator, host/target presence and agreement, the binding to this host and approved target | what the entries **mean** together. It refuses shapes, not histories |
| **Reservation semantics** | §5.5's order rules: the current reservation, legal transitions over `reservation.TRANSITIONS`, terminal states, identity reuse, the applicable quarantined predecessor for a recovery | anything about a participant's run, and anything about a lock |
| **Participant semantics** | §5.11.1's rules P1–P9: start, stable run/participant/identity, filename binding, one terminal entry, evidence content and completeness, recovery attribution, **and the stored reservation binding — the start's own shape and the completion's equality with it** | the reservation's state, and whether the host is quiescent |
| **The terminal publication — new in r6** | §5.12's step 0: that the run being concluded is a valid, in-progress harness run whose stored start owns the reservation in the request, checked **before** any decision or publication | the participant semantics themselves, which it obtains by calling the validator rather than repeating it |
| **The shared validator** | the coherence of one derived lifecycle record against `LIFECYCLE_SHAPES`, and whether its disposition is in the allowlist | the bytes, the order, and the ledger |
| **The final conjunction** | the admission decision: lock free, re-seal succeeded, record parsed, reservation semantics held, shared validator admitted, **ledger present**, every run file valid and settled, no quarantine for this host. Every one of these is necessary | nothing. It is where they are and'd, and it names every refusal rather than the first |

**No layer trusts another's input.** A safe writer does not excuse an unsafe
reader of pre-existing records, and a safe reader does not excuse publishing a
contradictory history, so the reservation and participant checks each run on
both sides of the store.

**And no layer trusts a caller's identity claim.** The participant, the run id and
the reservation arrive as arguments and are compared with the stored start before
anything is derived from them. **This is the rule R5-1 broke**: r5's writer took
three of them as authority, and the only reason the resulting record looked valid
is that its two consistency checks compared values that came from the same
untrusted source.

### 5.14 What is repaired in code, and what is only proposed

**Repaired, and this is the whole of it:**

| Finding | Repair | Where |
|---|---|---|
| R3-3 | `LifecycleHistory` carries the approved target, the first-use attester and basis, and the recovery's author; `LIFECYCLE_SHAPES` states for each disposition whether each is required or forbidden; the validator refuses wrong, absent and contradictory bindings | `reservation.py` |
| R3-3 | a bounded, versioned record schema with a serializer and a parser, the history-order rules, and the derivation that carries stored evidence into the shared validator; `BINDING_MISMATCH` gains its enforcing branch | `lifecycle_storage.py` |
| R3-1 | the publication path, the re-seal, and the process-only restart kept distinct from the power loss | `lifecycle_storage.py`, `durability_model.py` |
| R3-2 | the seven participant profiles, the run ledger and the completion rule | `lifecycle_storage.py` |
| **R4-1** | **the reservation history walked as a state machine over `reservation.TRANSITIONS`, carrying the current reservation and its current state; the derivation reads that rather than the last entry; the record store validates a proposed history before any byte is written** | `lifecycle_storage.py` |
| **R4-2** | **one participant-history validator applied by both writers and the survey — start, stable run/participant/identity, filename binding, one terminal entry, decoded evidence checked for content and completeness; the completion profile read from the stored start; an absent ledger refused** | `lifecycle_storage.py` |
| **R4-3** | **the terminal publication order performed as one operation, with the harness's two conditions derived from the release decision and the release publication, and an injected lifecycle-owned observation refused** | `lifecycle_storage.py` |
| **R5-1** | **the `participant_started` entry carries the reservation the run owns; the schema version is raised so an r5 record refuses by name; the participant validator checks the start's shape and requires the completion's evidence to name exactly that reservation, on both the writer and the reader path; the ledger writer reads the stored start before deriving a profile, a condition or a reservation; and `conclude_reservation()` checks the binding before the release decision, so a mismatch publishes nothing** | `lifecycle_storage.py` |

**Still only proposed, and r6 adds nothing to the list:** the lock adapter, the
record writer, the ledger writer, the re-seal's real `fsync`, the provisioning of
every path in §7, and every permission in it. R5-1's repair is one stored field
and a set of comparisons, so it needs no mechanism r5 did not already need. `reservation.DECISIONS_DO_NOT_PERSIST` and
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
| `execution/run_ledger.py` | **new in r4, grown in r5.** §5.11's per-participant ledger: begin, complete, recover, survey, over the same codec and the same barriers, **plus §5.11.1's validator applied on both sides and §5.12's derived completion facts** | ≈ 230 lines |
| `execution/lifecycle_record.py` | **r5 addition to the same module**: §5.5's corrected order rules as a state machine over `reservation.TRANSITIONS`, and the pre-publication check | ≈ 60 lines on top |
| `execution/run_ledger.py` | **r6 addition to the same module**: the `reservation` field on the start, the reader that returns a validated stored run, the binding comparison before a completion is derived, and §5.12's step 0 | ≈ 50 lines on top |
| `cleanup.py` | LAB-1's §8.1 reporting fix; `RECOVERY_PROCEDURE` replaced by §8.2's independent procedure | ≈ 60 lines |
| `plan.py`, `review_manifest.py` | coverage for the six new modules; no new executable | ≈ 30 lines |

**Already written in this pass, and they are models rather than mechanism:**

| Module | What it is |
|---|---|
| `durability_model.py` | the bounded synthetic filesystem, with `restart_process()` added beside `crash()` so a process-only restart is never modelled by calling the power-loss operation. **Planning tier**: its whole filesystem is a dictionary |
| `lifecycle_storage.py` | the record schema, parser, publication path, re-seal, run ledger, the seven profiles, and the connected successor protocol. **r5 added** the reservation state machine, the participant-history validator, the bounded completion-evidence codec and the terminal publication order. **r6 adds** the stored reservation binding on the start, its bounded grammar, the equality rules, the stored-start reader every writer uses, and §5.12's step 0. **Provisions nothing, and reads no live host** |
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
modes; `mkdirat(2)`; `unlinkat(2)` with `0` and `AT_REMOVEDIR`; `linkat(2)` with
`0` for exclusive publication and `renameat(2)` for non-exclusive publication —
*amended 2026-09-15, D1, replacing `renameat2(2)`*; `fstatat(2)` with
`AT_SYMLINK_NOFOLLOW`; `getdents64(2)` on a directory descriptor opened
`O_RDONLY` for one listing (*D2*);
`fsync(2)` on `O_RDONLY` directory descriptors and `O_WRONLY` file descriptors —
**including the re-seal of §5.6, which is the same call issued by a participant
that holds no write permission**; `execveat(2)` with `AT_EMPTY_PATH`;
`flock(2)`; `ioctl(2)` `FS_IOC_SETFLAGS`/`FS_IOC_GETFLAGS`.

**What exclusive publication needs from the target — amended 2026-09-15, D1.**
r6 first specified `renameat2(RENAME_NOREPLACE)`, whose filesystem support
`rename(2)` lists for ext4 from Linux 3.15 and tmpfs from 3.17 **[D]**. No
publication in this design uses it now, so that support is no longer a
prerequisite. `linkat` has two target dependencies of its own, and each refuses
with `EPERM` before anything is published **[D]**:

* `link(2)` refuses on a filesystem that does not support hard links; and
* with `/proc/sys/fs/protected_hardlinks` set to `1`, `proc_sys_fs(5)` permits a
  link only when the caller holds `CAP_FOWNER`, or its filesystem UID owns the
  file, or the file is a regular, non-set-user-ID file the caller may read and
  write. T1, T6 and §2.3.3 link a temporary their own writer created. **P2 sets
  the temporary to `root:root 0555` before linking and runs under the reviewed
  root filesystem identity**, so it relies on the same owner condition. P2 has
  no `CAP_FOWNER` dependency. Its actual capability masks are still observed,
  and `CapBnd` is never substituted for `CapEff`.

The target's filesystems and its hard-link policy are unconfirmed, so preflight
item **V6** is re-scoped to observe them, read-only (§7).

**Exclusive publication, and the substitute this design uses — amended
2026-09-15, D1.** `renameat2(RENAME_NOREPLACE)` is not reachable from the
interpreter the 2026-09-06 Option B ruling names: Python 3.12's `os` exposes
`renameat` and not `renameat2`, and the single `ctypes` exception is granted
elsewhere. The substitute is `linkat(dirfd, tmp, dirfd, name, 0)` followed by
`unlinkat(dirfd, tmp, 0)`, and then the containing directory's barrier.

`link(2)` fails with `EEXIST` when the destination exists **[D]**, so the final
name is claimed exclusively by the kernel rather than by a check the caller
performs, and there is no window in which the final name resolves to an object
this run did not write.

**One `linkat`, factored rather than duplicated — *amended 2026-09-19,
C-P5.0-LAB-I3-R2*.** The exclusive claim is `PosixFilesystem.linkat`, and
`renameat(noreplace=True)` is that call followed by the `unlinkat` of the
temporary; T1, T6, §2.3.3 and P2 still reach the link through the fused call,
unchanged. **Why reuse was unsafe for I3:** the fused call removed the temporary
before it returned, so the second interruption state below — both names, one
inode, link count two — could not be observed through it, and a second `os.link`
in the verifier would have been a divergent implementation of the same
exclusive, no-follow guarantee. `descriptors.EXCLUSIVE_LINK_PRIMITIVE` states
this, and §9.2 row 105 asserts that `descriptors.py` holds the package's only
`os.link`. `release()` beside it reports a failed `close()` instead of
swallowing it, and `DescriptorInventory.release_all()` names each role whose
release failed; `close()` on both is unchanged for every existing caller.

**The three interruption states — corrected 2026-09-15, D1.** The first
application of this amendment said a stop between the two calls leaves "the
temporary in place" and cited package-plan §2.13.2b and §5.9 for the refusal.
§2.13.2b is the precedent for refusing rather than cleaning, not a reader of
publication temporaries, and §5.9 covers only the run ledger. More importantly,
in the new state the final name **is** published:

| Stopped | Final name | Temporary | Published? | Under `renameat2` |
|---|---|---|---|---|
| before `linkat` | absent | present | nothing | the same: a stop before the rename |
| **after `linkat`, before `unlinkat`** | **present, with the synchronized bytes** | **present: a second name for the same inode, `st_nlink` 2** | **yes: visible, not yet durable** | **no such state** |
| after `unlinkat`, before the directory barrier | present | absent | visible, not yet durable | the same: renamed without the barrier |

A power loss before the directory barrier can leave any of the three. An
operator tells the second state from the first by comparing the two names'
`(st_dev, st_ino)`: equal is the second state. A final name that resolves to any
other object is neither, and refuses until an operator establishes what it is.

A recovery written for "temporary present, so nothing was published" is wrong
for the second state. §5.10's `interrupted_initialization` recovery said exactly
that, and it is corrected here and in `lifecycle_storage.FIRST_USE_RECOVERY`.

**The second state is never reported as a success.** When `unlinkat` fails, the
publication raises rather than returning, so no caller counts a barrier it did
not reach. What each reader then does:

| Exclusive publication | Reader that meets the second state | Result | Operator recovery | Evidence for the result |
|---|---|---|---|---|
| T1 first-use record, §5.10 | **the admission of all seven, at T4 (*D1 remediation*)**; initialization, which checks the temporary before the final name; the record's next publication | **every participant refuses before its work is called**, naming which of the three states it met; `interrupted_initialization`; T7's `admitted` refuses `interrupted_publication` | remove only the temporary, **after the immediately preceding `(st_dev, st_ino)` comparison**; do **not** repeat initialization; the next re-seal (T3) makes the record durable | §9.2 rows 70, 74–78 |
| T6 `participant_started`, §5.11 | the ledger survey; the writer's own retry | the survey counts the temporary unreadable and all seven participants refuse; a retry refuses `interrupted_publication` | remove the temporary, **on the same required comparison**; the run is then visible as started and unsettled, **it still blocks**, and T16's attributed recovery settles it | rows 71, 79 |
| §2.3.3 copy or record | the publication; restart discovery | the publication refuses before M1, so no configuration mutation happens; discovery reports the basis unusable for its leftover temporary | §2.5's operator disposal, naming the run id | row 72 |
| P2 case program, §1.4.2 | the executor | installation raises and records no identity for either name; §1.4.5's removal refuses both names; a second installation refuses `EEXIST` on the temporary | remove both names by absolute path, as residue under `R` | row 73 |

**The operator's removal is no longer [P] — *amended 2026-09-15, D1
remediation*.** It was prose, and prose cannot require a step. The recovery for
T1 and T6 is now one guarded operation over the same publication path both
objects share, `DurableRecordStore.remove_publication_temporary`, and **the
comparison is its argument**: a removal that compared nothing refuses
`no_observed_comparison`, one whose comparison does not show two names on one
inode refuses `identity_mismatch`, one whose comparison no longer holds at the
moment of the call refuses `stale_comparison`, one presenting another record's
comparison refuses `foreign_comparison`, and an unattributed one refuses
`unattributed`. Rows 75–79 exercise all five. It removes **exactly the
temporary**: never the record, never a republication, never a repeated
initialization, and it settles no run. The three recoveries the table's *other*
rows name — §2.5's disposal and P2's residue removal — remain **[P]**, and no
test performs either.

**The temporary is preserved and never cleaned by a retry, and never by a
participant.** A retry over an unexplained temporary is a write into a state
nobody has established, and an admission that stepped over one is
PR-20260915-LAB-D12-1.

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
| The one `ctypes` exception | `case_program._prctl_get_securebits` | **unchanged.** The two ioctls are reached through `fcntl.ioctl`, as implemented. `renameat2` is not reached at all (§6.2, D1). **How X1's `execveat(…, AT_EMPTY_PATH)` is reached without `ctypes` is not yet established:** Python 3.12's `os` has no `execveat`; the candidate is `os.execve` on a descriptor, whose `fexecve(3)` uses `execveat(2)` since glibc 2.27 where the kernel provides it, and otherwise `/proc` **[D]**. X1 is unimplemented, so this is an open implementation item, not a claim. *Corrected 2026-09-15*; given an owner, its required evidence and its execution stop condition below, *amended 2026-09-15, D1 remediation* |
| Descriptors opened per run | the chain, one mode | the chain in two modes, **plus one `O_RDONLY` directory descriptor per participant per run for the re-seal**, and — *amended 2026-09-15, D2* — **one short-lived `O_RDONLY` directory descriptor (D20) per listing, closed before the listing returns**. No new privilege, no new path, no retained descriptor |
| New privileged writer | — | **none** in the laboratory mechanism. *Amended 2026-09-19, C-P5.0-LAB-I3-R2:* the separately armed I3 verifier of §7.4 is a root-run writer outside it, authorized by C-P5.0-LAB-I3-D1 for transient objects only — one payload per publication context and the transient `R`/`R/bin` — all removed through identity guards before success. It adds no persistent object, capability, unit, group or identity |
| New system group | — | **`freedomlab`**, with `ubuntu` as a member |
| New provisioned paths — *amended 2026-09-17, C-P5.0-LAB-V6-D* | — | **`/var/lib/freedom-blades` (`0755 root:root`) — V12, new 2026-09-17**, `/run/freedom-blades` (`0750`), `/run/freedom-blades/laboratory.lock` (`0660`), `/var/lib/freedom-blades/laboratory` (`0750`), `/var/lib/freedom-blades/recovery` (`0700 root:root`), and **`/var/lib/freedom-blades/laboratory/runs` (`3770`) — new in r4**. **`/opt/freedom-blades/evidence` is withdrawn with V11** and nothing is provisioned under `/opt`. V12 adds no access to any existing object: it creates the parent §2.2 already stated and §7 had left without an item, at the mode §2.2 already gave it |
| New provisioned object | — | `/var/lib/freedom-blades/laboratory/lifecycle.json` (`0640`) |
| New systemd artifact | — | one `systemd-tmpfiles` fragment for the two `/run` entries |
| **New write permission for ordinary participants** | — | **one directory only**: the run ledger. **The reservation record stays root-written, and the re-seal needs no write permission at all** |
| New capability or unit | — | **none** |

**X1's `execveat` route — owner, evidence and stop condition. *Added
2026-09-15, D1 remediation*, on Codex's disposition that the unresolved route
*"needs an explicit owner and execution stop condition before execution
readiness"*. No route is chosen here and none is implemented: C-P5.0-LAB-D12-R1
forbids choosing one, and the point of writing this down is that an
unimplemented step with no owner is a step that gets implemented by whoever
reaches it first, at the moment of execution, under pressure.**

| | |
|---|---|
| **Item** | §1.4.4 X1's `execveat(D7, "", argv, envp, AT_EMPTY_PATH)`. Python 3.12's `os` has no `execveat`; the candidate is `os.execve` on a descriptor, whose `fexecve(3)` uses `execveat(2)` since glibc 2.27 where the kernel provides it and otherwise falls back to `/proc` **[D]** |
| **Owner** | the implementing agent Peter designates as Package 5.0's working Technical Lead, under implementation-plan §0.3. Not the Independent Reviewer's, and not closed on the implementer's own recommendation |
| **Required evidence, all of it** | which call is issued and from where; whether the one `ctypes` exception (`case_program._prctl_get_securebits`) would be widened, which is a **separate approval** and not part of this item; that the `/proc` fallback is either reached deliberately or refused rather than reached silently — a `/proc`-mediated execution re-resolves a pathname and gives up exactly the descriptor binding X1 exists for (§1.4.4); and §9.3's **I7**, that the reviewed payload executes under every disposable identity |
| **Execution stop condition** | while the item is open, **X1 is not executed**. `plan.is_executable` stays `False`, `reservation.REAL_EXECUTION_REFUSAL` stands unconditionally, and no `--execute` run is taken on the grounds that the remaining route is obvious. Choosing the route is a separate authorized pass |
| **Where it is stated in code** | `execution.descriptors.UNIMPLEMENTED_EXECUTION_ROUTE`, asserted by `test_lab_implementation.py::test_the_unimplemented_execveat_route_has_an_owner_and_a_stop_condition` |
| **Status** | **open**. RAID item **LAB-X1** |

**The delta grew from eight items to ten in r4**, and the reason was worth
stating because it had happened three revisions running: specifying the
descriptors revealed `OPEN_MODE`; specifying the storage revealed the initial
record and the directory-barrier preflight; specifying the reading revealed the
ledger directory and the identity question.

**In r5 it did not grow. In r6 as submitted it did not grow either. On
2026-09-16 it grew by exactly one item, to eleven, and on 2026-09-17 that
eleventh item was replaced — *amended 2026-09-17, C-P5.0-LAB-V6-D*.**
Specifying the provisioning revealed that §1.3.3's **D1** had a descriptor, a
role name and a set of permitted uses, and no owner, group or mode anywhere.
V11 stated them and §7.2 derived them. The maintainer then **withdrew the
location**: `R` is `/var/lib/fb-evidence-p5-0`, the approved target's root,
created by the reviewed concrete plan and not by prerequisite provisioning, and
`/opt/freedom-blades/evidence` is gone with V11. In its place **V12** states the
persistent parent `/var/lib/freedom-blades` that V4 and V5 hang from.

**The count is unchanged at eleven and the delta is narrower than it was.** V12
widens nothing — no new path an identity may reach, no new capability, unit,
group, identity or descriptor, no access to an object that already exists — and
withdrawing V11 removes a proposed path under `/opt` rather than adding one.
Everything below about the r5/r6 delta stands unchanged.

**The proposed permission delta was unchanged at ten items through r5 and r6's
submission.** All three R4 corrections were pure
validation and ordering over records the protocol already stores, and R5-1's is
one additional field in a file the harness already writes, one comparison against
bytes it already reads, and one check moved ahead of a decision it already took.
The start entry grows by one line inside a file whose owner, mode and directory
are unchanged; the stored-start read uses the group read the ledger already
requires; and no new path, mode, group, identity, capability, unit or descriptor
is required. **No expansion is proposed here, and the rule that pure validation is
not a reason to expand permissions is the reason to say so explicitly rather than
leave it inferred.** If a later pass finds one necessary it will be proposed as
its own item and left unapproved.

---

## 7. Provisioning and permission changes — required, and unapproved

**Dated maintainer direction, 2026-09-17 — C-P5.0-LAB-V6-D. This supersedes the
2026-09-16 direction below.** Peter approves the **prerequisite subset** V1, V2,
V3, **V12**, V4, V9 and V5, in that order, subject to independent Codex
technical and security acceptance of the remediation that records it. **V11 is
withdrawn** with `/opt/freedom-blades/evidence`; no ownership change to
`/opt/freedom-blades` is made. **V7 remains excluded from that release** — §7.1
states the exclusion and its stop condition — and V6, V8 and V10 remain
observations. The approval is not applied by this document and was not applied
by the remediation: no object was created on any host.

**Dated maintainer direction, 2026-09-16 — C-P5.0-LAB-V6-R1, superseded above.**
Peter approved the prerequisite subset V1, V2, V3, **V11**, V4, V9 and V5. That
subset is no longer the released one; the row order and V11's membership are
what the 2026-09-17 direction changed.

**The set is eleven items. It grew to eleven on 2026-09-16 and its eleventh
changed identity on 2026-09-17 — *amended 2026-09-17, C-P5.0-LAB-V6-D*.** The
released V6 survey of 2026-09-16 found `/opt/freedom-blades/evidence` **absent**
and this section had described it only as *"root-only [A]"* — an assumption,
with no owner, group, numeric mode, creation mechanism, persistence behaviour or
item. V11 stated it, and §7.2 derived its mode. **The maintainer then withdrew
that location rather than widening the parent rule it broke**: V6 observed
`/opt/freedom-blades` as `1001:1001 0755`, writable by the identity every
participant runs as, so a root-only object under it would have sat behind an
entry `ubuntu` could rename. The sole canonical `R` is the already approved
`/var/lib/fb-evidence-p5-0`, created by the reviewed concrete plan and not by
prerequisite provisioning.

**V12 is the eleventh item.** It states the persistent parent `/var/lib/freedom-blades`
that V4 and V5 hang from, at `root:root 0755` — the value §2.2 already stated —
and it is applied **before** both of them. §7.3 was the section that raised that
parent as undefined; the disposition closes it.
`provisioning.PROVISIONING_ITEMS` carries the set and
`provisioning.delta_item_count()` derives the total, so the number is not a
literal in six places.

**Dated maintainer direction, 2026-09-12:** the then ten-item set below is
accepted as the proposed lab design, and the identity decision is shared
`ubuntu` for all seven participants. This supersedes the proposal's unanswered design question,
but does not rewrite its historical approval column or authorize applying any
item. Actual identity confirmation (V10), filesystem checks (V6/V8), and all
provisioning remain unperformed and separately gated. See the
[maintainer direction and LAB-1 follow-up](project-review-2026-09-12-lab1-disposition.md).

**None is approved by this document**, and calling the re-seal unprivileged
approves none of them. They are listed so a maintainer can approve or refuse
them as a set.

**The set was unchanged in r6 as submitted, as it was in r5; it grew by exactly
one item on 2026-09-16, and on 2026-09-17 that item was replaced by another —
*amended 2026-09-17, C-P5.0-LAB-V6-D*.** V11 is **removed**, and removing it
withdraws access rather than granting any. V12 grants no access to an existing
object and no capability, unit, identity or group either: it creates one new
directory, `root:root 0755`, at a path §2.2 already stated and V6 observed
absent. The three R4 corrections and R5-1's binding need no permission r4 did
not already need. At submission on 2026-09-11, the two preflight items and the
identity choice were unperformed and undecided. The identity choice is
superseded by the dated maintainer direction above. **Of the two observations,
V6 was performed on 2026-09-16 as the approved read-only survey, repeated as
I12 after provisioning, and **closed by Peter on 2026-09-19**; V8 remains
unperformed** — *amended 2026-09-17, C-P5.0-LAB-V6-D-R1; status updated
2026-09-19, C-P5.0-LAB-V6-C*.

| # | Change | Why | Approved? |
|---|---|---|---|
| V1 | create system group `freedomlab` | so ordinary participants can open the lock without `sudo` | **no** |
| V2 | add `ubuntu` to `freedomlab` | it is every participant's identity **[A]** | **no** |
| V3 | `systemd-tmpfiles` fragment creating `/run/freedom-blades` `0750 root:freedomlab` and `laboratory.lock` `0660 root:freedomlab` | `/run` is tmpfs; the lock must exist before any participant runs | **no** |
| V4 | create `/var/lib/freedom-blades/laboratory` `0750 root:freedomlab` | the durable reservation record must survive reboot | **no** |
| V5 | create `/var/lib/freedom-blades/recovery` `0700 root:root` | the independent recovery store of §2.2 | **no** |
| ~~V11~~ | ~~create `/opt/freedom-blades/evidence` `0700 root:root`~~ | **Withdrawn 2026-09-17, C-P5.0-LAB-V6-D.** The maintainer withdrew the location rather than widening §1.4.1's root-only parent rule to fit the `1001:1001 0755` parent V6 observed. `R` is `/var/lib/fb-evidence-p5-0`, created by the reviewed concrete plan, not by prerequisite provisioning. §7.2's derivation is retained as the design evidence behind that decision. `provisioning.PROVISIONING_ITEMS` does not carry it | **withdrawn — not an item** |
| **V12** | **create `/var/lib/freedom-blades` `0755 root:root`, before V4 and V5** | **§2.2 already stated this path and this mode, and no §7 item created it — §7.3 raised it as the parent the delta did not define. V4's laboratory directory and V5's independent recovery directory are both created beneath it, so without an item for it each child applier would resolve its `dirfd` from an object nobody approved. V6 observed it absent. It is the persistent parent; it is **not** the disposable run root `R`. New 2026-09-17, C-P5.0-LAB-V6-D** | **no** |
| V7 | initialize `lifecycle.json` `0640 root:freedomlab` with a verified-first-use record, exclusively, durably, bound to host **and approved target**, on a named operator attestation | §5.10. Without it the fresh-install path cannot reach its successful control | **no; and explicitly excluded from the 2026-09-16 release — §7.1** |
| **V9** | **create `/var/lib/freedom-blades/laboratory/runs` `3770 root:freedomlab` — setgid and sticky** | **§5.11. Every participant must be able to publish its own in-progress and completion state, and the reservation record must not become group-writable to allow it. New in r4** | **no** |
| V6 | *re-scoped 2026-09-15, D1; **approved 2026-09-15 as a read-only prerequisite survey**, D1 remediation; **observed set corrected and status stated 2026-09-17, C-P5.0-LAB-V6-D-R1, on Blocking PR-20260917-LAB-V6D-R1-1***: observe, read-only, the **filesystem and mount type** under each directory that holds an exclusive publication — the filesystem `R` (`/var/lib/fb-evidence-p5-0`, created by the reviewed concrete plan) is created on, and the one `/var/lib/freedom-blades` (V12), `/var/lib/freedom-blades/laboratory` (V4), its `runs` child (V9) and `/var/lib/freedom-blades/recovery` (V5) would be created on — the value of `/proc/sys/fs/protected_hardlinks`, the **execution identity**, the **file ownership and mode assumptions**, and the **relevant capability state**. **The withdrawn `/opt/freedom-blades/evidence` is not among them**: V11 is withdrawn, nothing is provisioned under `/opt`, and no observation of that path is directed or expected (§7.3, decisions A and B). Hard-link support is read from the filesystem type; a type whose support is not established leaves V6 unconfirmed. **No link is created**: a write probe is not read-only and is not part of V6. **It does not prove that the real `linkat` publication succeeds and it does not close I3**; a controlled write verification requires separate authorization before execution | §6.2; one of the twelve unconfirmed facts | **approved as a read-only survey**; **performed 2026-09-16, not closed**. The survey found both then-candidate location families on the same ext4 root mount and `fs.protected_hardlinks=1`, and found every exact publication directory and the `freedomlab` group **absent**, so their required ownership and mode assumptions could not be confirmed on the target. It stays **performed-but-not-closed** until the accepted provisioning is applied and the read-only survey is repeated — that repetition is **I12** and `provisioning.VERIFICATION_PROCEDURE`, it is unperformed and separately authorized, and neither it nor V6 is the controlled write verification that would close I3 |
| V8 | confirm that `fsync` on an `O_RDONLY` directory descriptor behaves as the containing-entry barrier on the target's filesystem | §2.3 and **§5.6, which now depends on it for every participant rather than only the executor** | **preflight**, unperformed |
| **V10** | **confirm that all seven participants really run as `ubuntu`** | **§5.2 and §5.4. The identity is an [A] that the whole ledger's attribution rests on. The shared identity means file modes are accident guards, not barriers between participants. New in r4** | **preflight**, unperformed; shared identity choice recorded 2026-09-12 |

**The V10 choice is resolved; its target fact is not.** Peter chose not to
separate the seven identities, so no identity-driven contract revision is
needed. The preflight must still confirm that all seven really run as `ubuntu`.
The honest statement in §5.2 remains: the modes guard against accidents and not
against the participants.

**V6 re-scoped 2026-09-15 and closed 2026-09-19 after I12.** No
publication path in this design depends on `RENAME_NOREPLACE` after the §6.2
amendment: the exclusive publications use `linkat`/`unlinkat` and the
non-exclusive ones use `renameat`. The first application said no other item
waits on V6. The dependency moved rather than disappeared — §6.2 names what
`linkat` needs from the target — so V6 now observes that instead. Both
dependencies refuse with `EPERM` before anything is published, so V6 is an
operational prerequisite rather than a safety one. V6 was first performed on
2026-09-16 but remained open because the objects whose ownership and mode it
had to confirm were absent. After provisioning, I12 repeated the complete
read-only observation and every row matched the reviewed definition. Peter
accepted the independent evidence review and **closed V6 on 2026-09-19**
through C-P5.0-LAB-V6-C. Closure confirms only this read-only prerequisite
survey: I3 remains unconfirmed and separately authorized; V7 remains excluded;
V8 and V10 remain unperformed; `plan.is_executable` remains false; and Package
5.0 remains not ready. [Independent review](project-review-2026-09-19-reserved-laboratory-i12-v6-closure.md).

**Peter's disposition, 2026-09-15, on Codex's recommendation — *D1
remediation*.** The question the correction handback put is answered: **V6 is
approved as a read-only prerequisite survey.** It may record the filesystem and
mount type, `fs.protected_hardlinks`, the execution identity, the file ownership
and mode assumptions, and the relevant capability state. It does **not** prove
that the real `linkat` publication succeeds and **it does not close I3**. A
controlled write verification requires **separate authorization before
execution**. The preflight in which V6 would be observed remains authorized and
queued; approving what V6 observes is not releasing it.


### 7.1 The released subset, and why V7 is not in it

**Added 2026-09-16, C-P5.0-LAB-V6-R1; *amended 2026-09-17, C-P5.0-LAB-V6-D* —
V11 withdrawn, V12 added ahead of V4 and V5.**

| | |
|---|---|
| **Released prerequisite subset, in application order** | V1, V2, V3, **V12**, V4, V9, V5 — `provisioning.RELEASED_PREREQUISITE_SUBSET` |
| Applied by an operator, out of band | V1 `groupadd`, V2 `usermod --append`, V3 the fragment and `systemd-tmpfiles`. Each item's `creation` field carries the exact command; **this repository performs none of them** |
| Applied by a repository artifact | **V12**, V4, V9, V5 — the four directory items, through `execution/provisioner.py` — `provisioning.APPLIED_DIRECTORY_ITEMS`. Exclusive `mkdirat`, `fchown` and `fchmod` on the descriptor the creation opened, then the parent's containing-entry barrier. **The order is parent before child**: V12 before both of its children, V4 before its `runs` child. **Every failure after the `mkdirat` succeeds is a closed refusal carrying the object it left, and so is a failure to release any descriptor the application held** — `provisioner.POST_CREATION_REFUSALS`, *amended 2026-09-16, V6-R2 remediation; extended 2026-09-16, V6-R3 remediation*; see below |
| **V12's location is derived from both of its children** — *added 2026-09-17, C-P5.0-LAB-V6-D review* | `provisioner.directory_targets` reads the laboratory **and** the recovery directory, refuses `creation-refused` for V12 if they do not share one parent, and verifies V12 against **their** names rather than two literals. Deriving the parent from one child would build a V12 that is not the other's parent and declare children it does not have — the implicit parent this item exists to prevent, one level down |
| **Excluded** | **V7**, and V7 alone — `provisioning.excluded_item_ids()` |
| Still observations | V6, V8, V10 |

**Why V7 is excluded.** §5.10's first use is an exclusive publication:
`O_CREAT|O_EXCL` on the temporary, the bytes synchronized, `linkat` of the final
name, `unlinkat` of the temporary, then the containing entry's barrier. That
`linkat` is the **first real exclusive publication on the target**, and whether
it succeeds there is implementation check **I3**. The released V6 survey
observed the prerequisites and, as its own approved contract states, does not
close I3; a controlled write verification needs separate authorization before
execution. Initializing the record would perform that verification under
another name.

**Consumed authorization, 2026-09-19 — C-P5.0-LAB-I3.** Peter authorized one
bounded controlled-write verification of I3 using the reviewed
`linkat`/`unlinkat` sequence in the exact target filesystem. The operation is
limited to one uniquely named temporary object and hard link, byte and shared
`(st_dev, st_ino)` verification, removal of both names, the containing-entry
barrier and proof of no residue. It stops on discrepancy or cleanup failure and
does not initialize V7, invoke a participant or harness, access the database,
run a generated vector or use `--execute`. Success confirms I3 only. Codex
remains Independent Reviewer. The assigned pass stopped before implementation
because the P2 contract was contradictory; it grants no remaining host action.

**Current decision, 2026-09-20 — C-P5.0-LAB-I3-R3.** Peter accepted the
independent C-P5.0-LAB-I3-R2 review with no Blocking or Important finding and
ruled on the two contract discrepancies it reported, in favour of this contract
in both cases. **Canonical `R` is created `root:root 0700`** — §1.4.1's C1 row
and §7.2's derivation, not the `0755` the concrete plan carried — and **P2
alone creates its exclusive publication temporary `0500`**, §6.2's P2 row. The
already-open writable descriptor remains the authority for completing and
synchronizing P2's write despite the temporary's pathname mode, and P2 applies
and reads back the final `root:root 0555` on that descriptor before exclusive
publication; the creation mode never becomes the published mode. T1, T6 and
§2.3.3 retain the shared `0600` exclusive-creation default, which is why the
`0500` is an explicit input passed at P2's call rather than a change to
`descriptors.EXCLUSIVE_CREATION_MODE`. Source, tests, this contract and the
generated artifacts were reconciled in one bounded repository-only pass;
manifest version moves to **16**. Nothing operational is released: I3 remains
unconfirmed, V7 excluded, V8 and V10 unperformed, `is_executable=False`, and
Package 5.0 not ready.

**Superseded decision, 2026-09-19 — C-P5.0-LAB-I3-D1.** P2 is `root:root 0555`
and relies on the filesystem-UID owner condition. The `CAP_FOWNER` dependency
is withdrawn. The armed verifier may temporarily create canonical `R` and
`R/bin`, then must remove both directories through identity guards before
success. Contract/code/test reconciliation and independent review are required
before a new operational release.

**The stop condition, and what an absent record leaves** — *amended 2026-09-17,
C-P5.0-LAB-V6-D*. With V1–V5, V9 and **V12** applied and V7 absent, the host is
provisioned and **closed**:

* §5.9's *record absent or unreadable* refuses, and it refuses **all seven**.
  `lifecycle_storage.read_and_admit` is the one admission path,
  `host_lock.LaboratorySession.admit` is its only caller, and
  `execution/participants.py` returns before any participant's work is called.
  §9.2 row **80** drives all seven over a really-provisioned model host and
  asserts exactly that;
* §5.10 states that initialization is the only way out of absent, that it is
  the **operator's** act, out of band, on a named attestation, and never the
  harness's or a participant's. So the absence is not a gap the next run fills;
* `plan.is_executable` stays `False` and `reservation.REAL_EXECUTION_REFUSAL`
  stands unconditionally. **A provisioned host is a host on which the refusals
  can finally be reached honestly. It is not a host that may run anything.**

`execution/provisioner.py` refuses V7 by name — classification
`item-not-in-this-release` — and refuses V1, V2 and V3 as
`item-not-applied-by-this-tool`. Neither refusal is a policy a caller can pass
an argument to.

**What a partial application returns — *added 2026-09-16, V6-R2 remediation;
extended 2026-09-16, V6-R3 remediation*.** The `mkdirat` is the line either side
of which a failure is a different fact. Before it, nothing exists and
`creation-refused` is the whole story. After it, a directory is at a provisioned
name, and three rules hold for every one of the six failure points — opening the
created directory, `fchown`, `fchmod`, the read-back's own `fstat`, a read-back
that disagrees, and the parent's barrier — **and for the release of the
descriptor each of them was issued through**, which is the seventh and is
described after them:

1. **the failure is classified, not raised.** Each becomes one of
   `provisioner.POST_CREATION_REFUSALS`, which names no path, no directory
   content and no operating-system message, so a refusal stays safe to put in an
   operator-facing artifact. A raw `OSError` reaching a caller would be a
   refusal nobody classified about an object nobody recorded;
2. **the object is in the returned result.** `ProvisioningRun.applied` holds it
   beside the items that completed, because `applied` answers *what is on disk*;
   the refusal is what says it is unfinished, and `not_attempted` names every
   later item. A live provisioner's private state is not evidence an operator
   can read; and
3. **identity is preserved where the object can still be observed, and claimed
   nowhere else.** Every failure after the open still holds the descriptor the
   creation opened, so `(st_dev, st_ino)` comes from the object itself and the
   guarded reversal of each item's `rollback` field remains available. If the
   open is what failed there is no such descriptor, and resolving the name again
   would record an identity this application cannot attribute to its own
   `mkdirat` — the substitution the guard exists to catch. That object is
   reported as residue with no identity, and `rollback()` refuses the **whole**
   reversal while one is present rather than removing what it can and stopping.

**Releasing the descriptor is the seventh failure point — *added 2026-09-16,
V6-R3 remediation*.** Each of the six above is issued through a descriptor, and
releasing it can fail on its own. Three are released on the application path:
the one opened on the created object, and the parent's synchronizable and
traversal descriptors. A `close()` that reports failure used to escape raw and
to **replace** whatever refusal was unwinding through the same `finally`, which
is Codex Blocking PR-20260916-LAB-V6R2-1. Two rules close it:

4. **the first causal refusal wins.** A release that fails while an ownership,
   mode, read-back, barrier or parent refusal is in flight is subordinate to it
   and does not replace it: the operator is told about their object, not about a
   descriptor. Every descriptor is still released whichever one reports first,
   so a failure on one does not leak the next; and
5. **a release failure with nothing else in flight is its own refusal.**
   `descriptor-not-released`, the seventh member of
   `provisioner.POST_CREATION_REFUSALS`, carrying the result the item had
   already reached — **never a second `AppliedItem` for the same object**, so
   the returned run and the provisioner's own account of what it created still
   agree. A created object keeps the `(st_dev, st_ino)` its read-back
   established, so the guarded reversal survives; where the failure is on the
   created object's own descriptor the barrier is **not** issued afterwards, and
   the refusal says so. It is the one member not tied to a `mkdirat`: `ensure`
   releases the same two parent descriptors after verifying an
   already-provisioned object, and there the refusal carries that verification's
   item and `created` stays empty.

**An ambiguous close is treated as ambiguous.** The descriptor is not reused and
`close()` is not retried on it — a second `close()` of a number the kernel has
already released can close a descriptor something else has since been handed.
Nothing establishes that the descriptor leaked and nothing establishes that it
did not; what is refused on is the application's inability to say the step
finished cleanly.

**Verification and reversal release their descriptors under the same rule —
*added 2026-09-16, V6-R4 remediation*.** The five rules above cover the three
descriptors the application path holds. `_verify_one`, which `verify()` and the
already-provisioned path use, and `_remove`, which guarded rollback uses, hold
two each, and until this remediation both released them with a bare `os.close`
that still raised — Codex Blocking **PR-20260916-LAB-V6R3-1**. Three further
rules close it, and none of them widens what is provisioned:

6. **the read-only re-observation stays complete.** `verify()` returns one
   observation for every target it is given. A descriptor it cannot release is
   a finding about the observation, **appended** to that item's
   `discrepancies` as `descriptor-not-released` and never displacing the owner,
   group, mode, link count or content it already read — and never an exception,
   which would abandon every later target unobserved over a descriptor rather
   than over anything about an object. `provisioner.OBSERVATION_DISCREPANCIES`
   is that closed vocabulary. The same condition reached through `_existing()`
   inside `ensure()` is the closed refusal `descriptor-not-released`, carrying
   the `already-provisioned` result the verification reached, once, with
   `created` still empty because nothing was created. Where the object itself
   also disagrees with its definition, **that disagreement is the refusal** and
   the release is subordinate to it;
7. **a reversal refuses before an effect, and the `rmdir` is the line.** A
   release failure while an identity-mismatch or not-empty refusal is unwinding
   is subordinate to it, exactly as on the application path. A failure to
   release the descriptor the object was *identified* through, with nothing else
   in flight, means the `rmdir` is **not issued**:
   `rollback-descriptor-not-released-nothing-removed`, the object is exactly
   where it was, and it is still this application's to reverse; and
8. **a reversal's account of what it removed is truthful.** Where `rmdir`
   returned success and the parent descriptor then failed to release, the object
   **is** gone: `rollback-descriptor-not-released-object-removed` says so, the
   object is in the refusal's `removed` account, `DirectoryProvisioner.created`
   no longer holds it, and a second reversal cannot aim at it. Every reversal
   refusal now carries what it had already removed, and each removal leaves the
   live account as it goes rather than at the end of the loop — so a reversal
   that stops part-way no longer names objects that are not there.
   `provisioner.ROLLBACK_REFUSALS` is the closed vocabulary and
   `RollbackRefused` makes the combination that would lie about an effect —
   *removed*, with the object absent from the account, or *not removed*, with it
   present — unconstructible.

Nothing here adds automatic rollback to an application. Reversing a partly
provisioned host remains the operator's decision, on the per-item `rollback`
field, and **an unidentified residue is an operator's object to inspect by
hand.**

### 7.2 V11's mode, derived — the identity and descriptor trace *(historical)*

**Added 2026-09-16, C-P5.0-LAB-V6-R1**, because `"root-only [A]"` is an
assumption and a provisioning item needs a number.

**Withdrawn as an operative section, 2026-09-17 — C-P5.0-LAB-V6-D.** V11 is
withdrawn, so nothing below defines an item any more. **The section is retained
because it is the evidence the maintainer decided on**: step 4 is what made the
root-only claim depend on the parent, and §7.3's first row is what showed the
observed parent could not carry it. Step 6's former `CAP_FOWNER` conclusion is
also historical and was superseded by C-P5.0-LAB-I3-D1 on 2026-09-19.
`provisioning.EVIDENCE_ROOT_TRACE` no
longer carries this derivation; it records the disposition instead, and the
derivation lives here.

1. **Who opens D1.** `DescriptorInventory.open_provisioned_root` is the only
   way a directory the run did not create enters the inventory, and §1.3.3 gives
   D1 to the executor alone. The open is issued **in the executor's own
   process**, not through the process boundary, so the real, effective and
   filesystem identity of that `openat` is the executor process's own.
2. **Which identity that is.** Every reviewed effect step is `run_as="root"` —
   all 34 of them in the current concrete plan — and `boundary.ProcessBoundary`
   refuses a root step from a launcher that is not already effective UID **and**
   GID 0, classifying it `root-identity-unavailable` before any process exists.
   An executor that is not root reaches no effect at all, so the process holding
   D1 is root whenever D1 is used for anything.
3. **Who creates each `R`.** The same process. §1.4.1's C1 is
   `mkdirat(D1, "<run>", 0700)` issued in-process by
   `executor.DescriptorBoundEffects`, exclusively, `EEXIST` refusing; C2 records
   `(st_dev, st_ino)` from the descriptor opened on the result. **No other
   participant calls either.** The six ordinary participants reach only the
   lock, the laboratory directory and its `runs` child.
4. **Therefore `root:root 0700`.** Owner `rwx` is exactly what `mkdirat` and
   `fstatat` need from this directory for the one identity that issues them. No
   group or other bit has a consumer: every object under `R` is reached by an
   **inherited descriptor**, and §1.3.3 states that a step needing a descriptor
   it was not given **refuses** rather than opening a path. The zero bits are
   also what make §1.4.1's own argument true rather than assumed — §1.4.1
   concedes that `R`'s *name* can be replaced and is only ever detected, and
   rests the exposure on this directory being root-only.
5. **`fs.protected_hardlinks=1` does not bear on this item.** **No exclusive
   publication happens in this directory.** D1's permitted uses are C1's
   `mkdirat` and §1.4.1's by-name `fstatat`, and neither is a `linkat`. §6.2's
   four exclusive publications are T1 under V4, T6 under V9, §2.3.3's capture
   under V5 and P2 under `R/bin`. V11's mode is decided by what `mkdirat` needs
   from a directory and by nothing the hard-link policy says.
6. **Historical conclusion, superseded 2026-09-19.** V6 found zero inheritable, permitted, effective and
   ambient capabilities **for a process running as `ubuntu`**. That is the right
   observation for T6, whose linked temporary `ubuntu` created, so
   `proc_sys_fs(5)`'s owner condition holds with no capability. It is **not** an
   observation about a root process, and none is drawn here. The later ruling
   fixes P2 at `root:root 0555`; its reviewed root filesystem identity therefore
   satisfies the owner condition. P2 has no `CAP_FOWNER` dependency. Actual
   operation-time capability masks must nevertheless be observed without
   treating `CapBnd` as proof of `CapEff`.

### 7.3 The four things the delta did not define — how each was disposed of

**Added 2026-09-16, C-P5.0-LAB-V6-R1, as four open items. *Resolved
2026-09-17, C-P5.0-LAB-V6-D*:** Peter's decisions A–D dispose of all four.
`provisioning.PREREQUISITE_PARENTS` and
`provisioning.UNRECONCILED_CONTRACT_DISCREPANCIES` are now both empty, and that
emptiness is the claim this section makes — **no parent of an applied item is
undefined**. The rows are kept so the disposition is readable against what it
disposed of.

| What was raised | V6 found | Disposition, 2026-09-17 |
|---|---|---|
| `/opt/freedom-blades`, as V11's parent | present, **`1001:1001 0755`** | uid 1001 is `ubuntu`. This parent's mode governs who may rename or unlink the **`evidence` entry**, whatever mode V11 put on the directory, so on the observed target `ubuntu` could replace `/opt/freedom-blades/evidence` — **contradicting §1.4.1's root-only [A] and the exposure argument built on it**. **Decision A: the location is withdrawn, not repaired.** `chown root:root /opt/freedom-blades` is not made; it is a permission change to a path holding the repository worktree and it is not needed once nothing is provisioned beneath it. No applied item has a parent under `/opt` any more. |
| `/var/lib/freedom-blades`, as V4's and V5's parent | **absent** | V4 and V5 are created beneath it and §2.2 states it as `root:root 0755`, but no §7 item created it. **Decision C: it becomes item V12**, applied before both children by the same exclusive `mkdirat`, descriptor `fchown`/`fchmod`, read-back and parent-barrier sequence. The applier no longer refuses `parent-absent` for V4 and V5 on a correctly ordered application; V12's own parent `/var/lib` is not an item and an absent or unsafe one there still refuses. |
| **`R`'s location** | — | §1.3.3 wrote `R = /opt/freedom-blades/evidence/<run>` while `approved_target.APPROVED_TARGET.root_path` is `/var/lib/fb-evidence-p5-0`, the concrete plan's `mkroot` step creates exactly that, and `targets.validate_mutation_root` **would refuse** `/opt/freedom-blades/evidence/<run>` — its last component does not begin with `fb-evidence-`. Both could not be `R`. **Decision B: `/var/lib/fb-evidence-p5-0` is the sole canonical `R`**, normally created by the reviewed concrete plan rather than by prerequisite provisioning. **Amended 2026-09-19, C-P5.0-LAB-I3-D1:** the separately armed I3 verifier is the only second creator; it may create temporary canonical `R` and `R/bin` solely for I3 and must identity-guardedly remove both before success. `provisioning.EVIDENCE_ROOT` reads the location from the approved target rather than restating it. **Corrected in place 2026-09-17, C-P5.0-LAB-V6-D-R1**, on Codex Blocking PR-20260917-LAB-V6D-R1-1: §1.3.3's inventory preamble still opened with the `/opt` form as the current definition, and a head banner is not a correction of a normative row. §1.3.3 now defines `R = /var/lib/fb-evidence-p5-0` and D1 on its parent `/var/lib`; the `/opt` form survives only in the dated historical passages of §1.4.1, §7.2 and this section. |
| **`plan.EVIDENCE_ROLE` has no production caller** | — | The role is defined and re-exported and **nothing in the package registers a directory under it**: the only `open_provisioned_root("evidence", …)` calls in the repository are in the suite, over a temporary directory. **Decision D: registration stays deferred** until a real consumer receives separate implementation and review authority. It is **not** resolved by provisioning a directory, and §9.2 row **86** asserts mechanically that no production caller appeared. |

### 7.4 The I3 controlled-write verifier — the complete procedure

**Added 2026-09-19, C-P5.0-LAB-I3-R2, implementing C-P5.0-LAB-I3-D1.** This is
the reviewed route to §9.3's **I3** that C-P5.0-LAB-I3 found missing. It is
**implemented and unperformed**: nothing below has run on `oracle-test`, no
digest is approved and no host action is released. A verified invocation is
evidence for a maintainer decision on I3; it closes nothing itself.

**Where it is.** Mechanism `execution/i3_verifier.py`; its only operator entry
point `execution/i3_verifier_cli.py`. Neither imports `cli.py`, the executor, the
materializer, the case program, the lifecycle record, the ledger, the lock or any
participant. The entry point takes `boundary.SystemIdentityLookup` — the one
reader of the host's accounts — and nothing else from the execution tier.

#### 7.4.1 Authority, gates and identities

| | |
|---|---|
| **Authority** | C-P5.0-LAB-I3-D1: P2 is `root:root 0555` under the filesystem-UID owner condition; decision B's narrow exception lets this verifier, and nothing else outside the concrete plan, temporarily create canonical `R` and `R/bin` solely for I3 |
| **Default** | non-effecting. Without `--arm-i3-controlled-write` the entry point returns before it constructs a lookup, a probe or a verifier, and reads neither the account database nor the filesystem — exit `3` |
| **First gate** | the command-line flag, passed as the verifier's `armed` and as nothing else |
| **Second gate** | `I3ControlledWriteVerifier.armed` must be exactly `True`; `run()` refuses `verifier-not-armed` before its first read, and every creating effect — `mkdirat` of `R`/`R/bin` and the exclusive open of every temporary — re-checks it. Deleting either gate leaves the other (§9.2 row 91) |
| **Identities** | two separate invocations, and **no identity or capability change by the program**. `--identity root` runs T1 under V4, §2.3.3 under V5 and P2 under canonical `R/bin`, in that order; `--identity ubuntu` runs T6 under V9. The operator runs each invocation as the identity it names |

#### 7.4.2 Admission — every observation before the first write

In order; the first mismatch refuses with its own member of
`i3_verifier.ADMISSION_REFUSALS` and **nothing is written**:

1. the fixed payload hashes to its pinned SHA-256;
2. `uname(2)` reports the approved target's **kernel nodename**, active kernel
   and architecture (`APPROVED_TARGET_FACTS.kernel_nodename`, `.active_kernel`,
   `.architecture`, read, not restated). The nodename is `Test`; it is a
   separate approved fact from `host`, the runbook §2 SSH alias `oracle-test`,
   which `uname(2)` cannot observe and which admission never compares.
   *Corrected 2026-09-20, C-P5.0-LAB-I3-R5, on Peter's Option A decision for
   LAB-I3-TARGET-1: r6 previously said `host` here, and the verifier compared
   it, which refused the C-P5.0-LAB-I3-R4 pass with `target-mismatch` before its
   first controlled write;*
3. every reviewed account and group — the invocation's, `root`, `freedomlab`,
   P2's owner and group — resolves through the lookup;
4. `/proc/self/status` reports the invocation's uid and primary gid in **all four**
   fields — real, effective, saved and **filesystem** — and `getresuid`/
   `getresgid` agree; the participant invocation already holds `freedomlab`;
5. `CapInh`, `CapPrm`, `CapEff`, `CapBnd`, `CapAmb` and `NoNewPrivs` are each
   present exactly once in kernel form, and `CapEff ⊆ CapPrm` and
   `CapAmb ⊆ CapPrm ∩ CapInh` hold;
6. `fs.protected_hardlinks` is exactly `1`;
7. `/proc/self/mountinfo` parses;
8. `R`'s parent (`/var/lib`) is opened `O_PATH|O_NOFOLLOW|O_DIRECTORY` by
   pathname — the only pathname the verifier opens — and is a directory owned by
   `root` with no group- or other-write bit; V12, V4 and V5 (root) or V12, V4 and
   V9 (participant) are then held one no-follow component at a time and each is
   exactly its §7 item's type, owner, group and numeric mode;
9. every held directory's device is mounted only as the approved filesystem type
   and device, read-write;
10. each publication directory's synchronizable descriptor binds by comparison
    (§1.3.2), and so does `R`'s parent for the root invocation;
11. canonical `R` is absent (root invocation); no name beginning
    `.fb-i3-verify-` is present in any publication directory;
12. each context's 16-byte nonce yields a temporary `.fb-i3-verify-<32 hex>-staged`
    and a final `.fb-i3-verify-<32 hex>-linked`, both outside the run-identifier,
    lifecycle, ledger, recovery and case-program grammars and both unoccupied;
13. every file the invocation will link is owned by exactly the observed
    filesystem uid — the owner condition, stated before it is exercised.

The capability masks are **evidence**, not an admission value. No reviewed
exact mask exists for either identity — `capability.E7_TARGET_FACTS` are
unconfirmed, and V6/I12 recorded `ubuntu`'s masks as an observation — so
admission requires them observable, well-formed and internally consistent, and
records them. `securebits` is not observed: it is readable only through
`prctl(2)`, and the one `ctypes` exception belongs to the case program.

#### 7.4.3 The four contexts

| Context | Directory | Identity | Temporary created | File immediately before `linkat` | Source of the value |
|---|---|---|---|---|---|
| T1 | V4 | root | `0600` | creator-owned, `0600` | `descriptors.EXCLUSIVE_CREATION_MODE`; the lifecycle record applies no other |
| §2.3.3 | V5 | root | `0600` | creator-owned, `0400` | creation `descriptors.EXCLUSIVE_CREATION_MODE`; final `recovery_store.STORED_OBJECT_MODE` |
| T6 | V9 | `ubuntu` | `0600` | creator-owned, group `freedomlab` by V9's setgid bit, `0600` | as T1 |
| P2 | canonical `R/bin` | root | **`0500`** | `root:root 0555`, `fchown` and `fchmod` on the descriptor | creation `case_runtime.CASE_PROGRAM_TEMPORARY_MODE`; final `case_runtime.CASE_PROGRAM_OWNER/GROUP/MODE` |

**The two mode columns are different modes — C-P5.0-LAB-I3-R3, 2026-09-20.**
The *creation* column is the mode the exclusive `openat` of step 1 below gives
the temporary **pathname**; the *final* column is the mode step 4 applies to the
descriptor and steps 5 and 9 read back. Only P2 distinguishes them. P2's `0500`
constrains nothing in the sequence, because every step between creation and
publication acts on the writable descriptor `openat` returned rather than on the
name: the payload is written to it, `fsync`ed on it, and `fchown`ed and
`fchmod`ed on it. `descriptors.PosixFilesystem.create_file` therefore takes an
explicit creation mode whose default is the unchanged `EXCLUSIVE_CREATION_MODE`,
and only P2's call passes a value. A `0500` observed on a *published* name would
be a mismatch, not a pass.

For P2 the verifier first creates `R` (`root:root 0700`) under `R`'s parent and
`R/bin` (`root:root 0755`) under `R`: exclusive `mkdirat`, an `O_RDONLY|O_NOFOLLOW`
descriptor compared with the recorded `(st_dev, st_ino)`, `fchown`, `fchmod`, a
read-back of type, owner, group, mode and link count, the parent's barrier, and
the mount re-observed for both.

#### 7.4.4 The publication, observation and removal, per context

1. exclusive `openat(O_CREAT|O_EXCL|O_WRONLY|O_NOFOLLOW, <creation mode>)` of
   the temporary, at §7.4.3's creation mode for the context — `0600` for T1,
   §2.3.3 and T6, `0500` for P2; its `(st_dev, st_ino)` is recorded from the
   descriptor;
2. the complete payload written;
3. `fsync` on the write descriptor — the data barrier;
4. P2 only, `fchown`; every context, `fchmod` — on the descriptor;
5. read-back on the descriptor: regular file, the recorded identity, owner,
   group, mode, link count one, size — and the file's owner equal to the
   observed filesystem uid (**the owner condition, observed**);
6. the write descriptor released; a release that reports failure stops the
   context before `linkat`;
7. `/proc/self/status` read again and required equal to admission's; its masks
   are recorded as the **operation-time** capability evidence;
8. `PosixFilesystem.linkat(dir, temporary, dir, final)` — the one reviewed
   primitive (§6.2); `EEXIST` means the name is occupied and nothing there is
   touched;
9. **both names observed**: each `fstatat(AT_SYMLINK_NOFOLLOW)` resolves to the
   recorded identity as a regular file with link count **two** and the reviewed
   owner, group and mode; each is opened `O_RDONLY|O_NOFOLLOW`, its descriptor
   compared with the identity, and read back as exactly the payload with the
   pinned digest;
10. the temporary removed after an immediately preceding identity comparison,
    then the final name observed with link count one — the state a completed
    publication leaves — then removed after its own comparison;
11. the containing directory's barrier; both names observed absent.

P2 then removes `R/bin` and `R`, each after an immediately preceding identity
comparison **and** an emptiness check, each followed by its parent's barrier,
and observes `R` absent.

**The post-removal observation is an absence check and nothing more** (§1.4.5).

#### 7.4.5 Partial states, cleanup and the final survey

Every created object is tracked from the moment it exists, with the identity
its creating descriptor recorded or with none. The first causal failure is
recorded as `(stage, classification)` from closed vocabularies, and later
contexts are `not-attempted`. Cleanup then walks the context's objects in
reverse: an object with an identity that still resolves to it — and, for a
directory, is empty — is removed and its parent barriered. Everything else is
**never removed** and is reported by fate:

| Fate | Meaning |
|---|---|
| `removed` | removed after a matching comparison; absence observed |
| `residue-identity-never-established` | created, identity never recorded |
| `residue-name-resolves-to-another-object` | the name now holds a foreign or replacement object |
| `name-absent-before-removal` | the recorded object was gone before the removal |
| `residue-directory-not-empty` | a directory that holds something |
| `residue-removal-failed` / `residue-removal-not-confirmed` | the removal or its absence check failed |

A foreign object at an occupied name is never tracked. The final survey lists
each held publication directory once (bounded at 4096 entries) and checks `R`,
and counts any `.fb-i3-verify-` name or a present `R` as a finding. All
inventory descriptors are then released; a failed release is counted and never
retried.

#### 7.4.6 Result, output and exit status

| Status | Exit | When |
|---|---|---|
| `verified` | `0` | every context verified, every object `removed`, no barrier, descriptor or survey finding |
| `not-armed` | `3` | no arm; nothing read or written |
| `refused-before-write` | `4` | an admission refusal; nothing written |
| `failed-no-residue` | `5` | a failure after which every object was removed through its guard, every barrier and descriptor finished, the survey is clean, no foreign object was met and no removal barrier failed |
| — | `6` | an exception the verifier did not classify; nothing about it is printed |
| `failed-operator-attention` | `7` | anything else: residue, a foreign or replaced object, an occupied name, a failed removal barrier, a cleanup-barrier, descriptor or survey failure |

Every printed field is an enumeration value admitted by membership, an integer
rebuilt from its value, a mask rebuilt as sixteen hexadecimal digits, a nonce
admitted by shape, or one of the two fixed statements `NOT_ATTRIBUTION` and
`SECUREBITS_NOT_OBSERVED`. No path, host account name or number, listing,
environment value or exception text is printed.

**Capability evidence semantics.** The rendering shows each of the five masks
and, for `CAP_DAC_OVERRIDE`, `CAP_DAC_READ_SEARCH` and `CAP_FOWNER`,
membership in each mask separately. `CapBnd` is never read as `CapEff`. **The
verifier does not isolate, require or prove `CAP_FOWNER`**: a root process with
effective `CAP_DAC_OVERRIDE` also satisfies the read-and-write branch, so a root
link that succeeds cannot show which branch the kernel took. What it shows is
that the owner condition held.

**What it does not establish.** Nothing about V8 or I2 — its barriers are issued,
not verified; nothing about V10; nothing about the concrete plan's own P2, which
it does not run. It creates no V7 record, invokes no participant or harness,
runs no generated vector and uses no `--execute`.

---

## 8. LAB-1 — the proposed reporting-contract fix

**Dated follow-up, 2026-09-12:** Peter accepted this bounded fix and it has been
implemented locally, pending independent technical review. The proposal text
below is retained as the design rationale and snapshot of r6; its statements
that the fix is unimplemented and not made in that pass are historical. See the
[direction and remediation note](project-review-2026-09-12-lab1-disposition.md).

**Second dated follow-up, 2026-09-12:** a review of that implementation found the
third bullet of §8.1 — *the procedure that applies to the state it reached* —
**not implemented**. The first pass compared one boolean over both procedures, so
a run that left residue and named only the configuration recovery satisfied the
clause; that is LAB-1's own shape relocated into the evidence record.
`classify_cleanup_failure_state` now takes the two causes and the two procedures
separately and requires each **present** cause to name its own procedure. This
raises the supplied-observation schema to **version 3** and the review manifest to
**version 10**, both recorded in the note above. The same review found the S-B
**message** named no procedure either, so the operator reading a non-zero exit
never saw what the result carried; it now names the procedure each present cause
calls for. The clause below now describes implemented behavior.

**Third dated follow-up, 2026-09-12:** the independent Codex re-review of that
implementation found **PR-20260912-LAB1-1** — the clause held in the outcome and
in the classifier, and **not in the run record that carries them**.
`validate_run_record()` checked each residue-recovery entry for three keys, a
consecutive order and non-empty strings, and compared none of them with
`journal.RECOVERY_PROCEDURE` or with the residue that requires it, so a schema-2
S-B record carrying one arbitrary ordered instruction was accepted on read-back.
The [bounded remediation](project-review-remediation-2026-09-12-lab1-handback.md)
raises the **run-record schema to version 3** and binds content to cause there
too: residue present requires the exact canonical five-step procedure and residue
absent requires none; retained recovery inputs require the exact
`cleanup.RECOVERY_PROCEDURE` and no retained inputs require none; the two causes
are independent; and the document read back is compared whole with the document
that was written. The supplied-observation schema stays at **version 3** and the
review manifest at **version 10**, because the manifest does not declare the
run-record document contract. §8.3's regression table below is extended by that
handback's matrix rather than replaced. LAB-1 remains **Important and not
closed**, pending Codex's re-review of this correction.

**Fourth dated follow-up, 2026-09-13:** the Codex R2 re-review found
**PR-20260912-LAB1-2** — the whole-document read-back the third follow-up records
was made *after* parsing, so it compared the parsed mapping and a fresh canonical
re-serialization of it and never the bytes. `b"\n" + serialized + b"\n"` and a
duplicate `schema_version` member carrying the value it already had were both
accepted through the public writer. The
[bounded remediation](project-review-remediation-2026-09-13-lab1-r2-handback.md)
retains the bytes `destination.read_bytes()` returns and compares them directly
with the bytes serialized, as the first and short-circuiting conjunct of the one
named comparison; the completed path is read → decode and parse → compare →
`validate_run_record`, and it establishes three distinct claims rather than one.
**No schema version moves** — the run record stays at **3**, the
supplied-observation schema at **3** and the review manifest at **10**, because a
valid schema-3 document means exactly what it meant before and only the writer's
implementation changed. §8.3's regression table is extended by that handback's
matrix rather than replaced. LAB-1 remains **Important and not closed**, pending
Codex's re-review of this correction.

**Fifth dated follow-up, 2026-09-13:** Codex's independent
[R3 re-review](project-review-2026-09-13-lab1-rereview-r3.md) accepts
PR-20260912-LAB1-2 with no residual finding. The raw bytes returned by the
destination are bound directly to the serialized bytes, while schema validation
continues to bind each cause to its canonical recovery procedure. LAB-1's local
remediation is closed. This changes no operational or package gate: C-7 and
EH-R16-1 remain unresolved, the twelve target facts remain unconfirmed,
`is_executable` remains `False`, P5.0-R5 remains Blocking and OD-62 remains Open.

**Classification: Important, confirmed by the September 11 review.** The
maintainer accepted the bounded correction and it is implemented locally, pending
independent technical review. It is a reporting gap in evidence classification
rather than a safety property, and it makes no unsafe operation reachable. This
does not resolve C-7 or close a Package 5.0 gate.

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

**Accepted change, keeping the two procedures distinct:**

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
  configuration-only ⇒ the configuration procedure; both ⇒ both. The clause is
  compared **per cause**: `JNL-47-RECOVERY-STATE` carries
  `residue_recovery_named`, `configuration_capture_retained` and
  `configuration_recovery_named` rather than one `recovery_procedure_named`, and
  a present cause whose procedure is unnamed fails the record by name. One
  boolean over both would let the wrong procedure answer the clause.

**Original submission rationale (historical):** r6 did not make this change
because it modifies `CleanupOutcome`'s contract and adds a `cleanup` → `journal`
dependency. Peter has since accepted the bounded change; the current
implementation and tests are recorded in the dated follow-up above.

### 8.2 The second change LAB-1 travels with — `cleanup.RECOVERY_PROCEDURE`

The external-store alternative below remains **proposed, not implemented or
provisioned**. Current code still retains configuration captures under
`R/before`; its recovery instruction now says not to rely on those copies if the
root or capture integrity is in question. The dated disposition note records
this limit.

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

| **41** | **the R4 reproduction: `FIRST_USE → ADMITTED A → RELEASED A → ADMITTED B → RUNNING B → RELEASED A`**, through the writer and planted around it | the append refuses and the stored bytes are byte-identical; the planted history parses and still refuses on read; B is reported `running` and C is refused | **R4-1.** Before the repair the append published, the reader took the final entry and C was admitted | **[M]** `test_the_reviewers_stale_release_reproduction`, `test_the_stale_release_history_refuses_on_read_as_well` |
| **42** | **the analogous stale operator recovery**, repeated after a newer `admitted`/`running` pair | refuse at the writer and at the reader | R4-1's second half | **[M]** `test_the_reviewers_stale_recovery_reproduction` |
| **43** | **twenty-one stored reservation histories — fifteen illegal and six legal.** Illegal: stale release, wrong current id, transition after `released`, transition after `quarantined`, duplicate release, duplicate quarantine, repeated recovery, terminal identity readmitted, admission over `admitted`, over an unrecovered quarantine and over `recovering`, `recovering` moved back to `running`, a transition never admitted, a recovery of a reservation never quarantined, a recovery naming an earlier reservation. Legal: a first use alone, **three sequential reservations each released**, a quarantine-recovery-successor sequence, a recovery awaiting a new run, an unrecovered quarantine and a run that reached its deadline | each illegal row refuses naming its own rule and derives no disposition; each legal row derives the stated disposition and admits or refuses accordingly | **that the matrix refuses everything**, and that only one fresh run was ever exercised | **[M]** `test_the_reservation_transition_audit`, twenty-one rows |
| **44** | **duplicate terminal delivery** | refuses explicitly, names the duplicate, leaves the bytes intact, and the first release still admits the next reservation | that the policy is unstated or that an append is silently idempotent | **[M]** `test_a_duplicate_terminal_delivery_refuses_explicitly` |
| **45** | **the R4 reproduction: `begin web-1 as WEB_SUITE`, `complete web-1 as FOUNDRY_TESTS` on Foundry evidence** | the completion refuses, the web run's stored history is unchanged, and **all seven** successors still refuse on the unsettled web run | **R4-2.** Before the repair it published and admission returned true | **[M]** `test_the_reviewers_cross_participant_completion_reproduction` |
| **46** | **seventeen stored run files**: wrong participant, wrong run, wrong filename, changed identity, an identity that is not the participant's, an unknown participant, empty evidence, arbitrary evidence, evidence missing a condition, evidence about another run, evidence nobody observed, a reservation binding claimed and a reservation binding missing, a duplicate terminal entry, a recovery over a completion, a second start, a recovery with no reference | each refuses, is reported `invalid`, and **refuses every successor including the harness and the environment reset** | that field presence is evidence, and that the survey may classify from the last entry | **[M]** `test_the_participant_history_audit`, seventeen rows |
| **47** | **a terminal run entry with no start, and a recovery with no start**, planted around the writer | both refuse on read and block | **that a corrected writer is enough.** A reader must refuse a history no writer can now produce | **[M]** `test_a_terminal_run_file_with_no_start_refuses_on_read`, `test_a_recovery_with_no_start_refuses_on_read` |
| **48** | **the ledger omitted, and the ledger unreadable** | refuse in both cases, naming §5.8's requirement | **R4-2's second path**, where `ledger=None` skipped accounting and admitted with an unfinished web run | **[M]** `test_a_missing_ledger_refuses_rather_than_reading_as_empty`, `test_an_unreadable_ledger_refuses` |
| **49** | **a provisioned ledger surveyed and found empty** | admits | that the new rule refuses whenever accounting is inconvenient. **The preserved control** | **[M]** `test_a_valid_provisioned_observed_empty_ledger_still_admits` |
| **50** | **all seven participants, each completed and each interrupted-then-recovered** | both paths settle the ledger and admit the next participant; the harness's completion goes through §5.12's order | that the accounting covers some participants and not others | **[M]** `test_every_participant_completes_and_recovers`, seven × two |
| **51** | **§5.12's order**: normal completion; a refused release decision; a failure injected at each of the three points of **each** of the two publications; a restart between them; a power loss in the same window; stale release evidence from another reservation | the successful path is reachable **without injecting either lifecycle-owned fact**; every intermediate state refuses or is completed by the successor's re-seal, as the row states; every one has a bounded attributable recovery; the prior history is preserved throughout | **R4-3.** r4's declared order had no reachable successful path and its green test injected the future facts | **[M]** `test_the_terminal_publications_have_a_reachable_successful_path`, `test_an_injected_lifecycle_fact_is_refused`, `test_a_completion_without_a_terminal_publication_refuses`, `test_a_refused_release_decision_publishes_neither_half`, `test_no_intermediate_terminal_state_authorizes_reuse` (six rows), `test_a_restart_between_the_two_terminal_publications_is_blocked_by_the_ledger`, `test_a_power_loss_in_the_window_remains_a_distinct_scenario`, `test_stale_release_evidence_from_another_reservation_refuses` |
| **52** | **three sequential reservations from stored bytes only**, with a process restart before every admission: one concluded normally, one interrupted and recovered, one concluded normally, then a fourth admission | every decision is taken from bytes a predecessor published; the ledger reports two completed and one recovered; no retired identity may be readmitted | **that the corrected lifecycle was only shown for one fresh run** | **[M]** `test_three_sequential_reservations_from_stored_bytes_only` |

| **53** | **the R5 reproduction: `initialize`, `ADMITTED A`, `begin B-harness as HARNESS_CLI`, `RUNNING A`, `conclude_reservation(reservation=A, run_id=B-harness)`** | the conclusion refuses **before any publication**; no `released` entry exists; B's started bytes are byte-identical; B is still `unsettled`; **all seven** successors refuse on it | **R5-1.** Before the repair it returned `concluded=True`, published both entries, reported B completed and admitted a successor | **[M]** `test_the_reviewers_wrong_reservation_completion_reproduction`, `test_the_refused_conclusion_leaves_a_released_entry_nowhere` |
| **54** | **the same wrong binding one layer down**, a release publication for `A` handed to `RunLedger.complete()` for a run started for `B` | refuses, writes nothing, and both runs stay in progress | that the repair lives only in the higher-level conclusion helper | **[M]** `test_the_wrong_reservation_completion_refuses_at_the_ledger_writer_too` |
| **55** | **the refused conclusion's recovery**: an attributed `participant_recovered` for the wrongly named run, then the reservation concluded against its own run | the recovery publishes, the correct conclusion publishes both halves, the survey reports one completed and one recovered, and the successor admits | **that the refusal is a dead end** | **[M]** `test_the_bounded_attributable_recovery_of_the_refused_conclusion` |
| **56** | **a harness start with no reservation, and with an empty one**, through the writer | both refuse as `invalid_history`; no run file is created | that the binding is optional for the participant that owns one | **[M]** `test_a_harness_start_with_no_reservation_refuses_at_the_writer`, and the seven-participant shape control |
| **57** | **all seven participants' start shapes, both ways**: the right shape publishes, the wrong one refuses | the harness publishes with an identity and refuses with an empty field; each of the six publishes with an empty field and refuses with an identity | that the representation is one-directional, or that the six may claim a binding | **[M]** `test_every_participants_start_carries_its_own_shape_of_the_field`, seven × two |
| **58** | **the stored reservation grammar**: an identity, nothing, whitespace, a padded identity, the evidence separator, a line break | the first is accepted and the other five refuse, each naming its own rule | that non-empty is the whole check | **[M]** `test_the_stored_reservation_grammar_is_bounded`, six rows |
| **59** | **eight planted run files**, written around the writer: a harness start with no reservation, with whitespace, with a padded identity; a completion naming a different reservation from its start; a completion naming none over a bound start; a web start, a web completion and a reset start each carrying a reservation | each refuses on **read**, is reported `invalid`, and refuses **all seven** successors | **that a corrected writer is enough.** These are the records r5 published, and a reader must refuse them on its own | **[M]** `test_the_planted_reservation_binding_audit`, eight rows × seven successors |
| **60** | **a planted start and completion that agree about the reservation** | read as a completed run; the successor admits | that the new rule refuses whenever a reservation is mentioned. **The preserved positive control** | **[M]** `test_a_planted_matching_harness_pair_is_read_as_settled` |
| **61** | **an r5 run file — `schema=1`, no reservation field — and a schema-2 file omitting the field** | `unsupported_schema` and `malformed` respectively; both count as unreadable and block; neither is read as a start whose reservation is empty | **that a reader may accept both old and new meanings.** This is the compatibility consequence, asserted | **[M]** `test_an_r5_participant_start_refuses_as_an_unsupported_schema`, `test_a_current_schema_start_without_the_field_refuses_as_malformed` |
| **62** | **request, publication and completion disagreement in each direction**: a request naming a later and an earlier reservation than the start; a publication naming a later, an earlier and an empty one | every row refuses and writes nothing; the run stays in progress | **that the comparison is containment or one-directional** rather than exact equality | **[M]** `test_a_request_disagreeing_with_the_stored_start_refuses` (two rows), `test_a_release_publication_disagreeing_with_the_start_refuses` (three rows) |
| **63** | **a run named `RES-9-harness` started for `RES-1`** | concluding `RES-1` succeeds; concluding `RES-9` refuses | **that the binding is inferred from the run's name.** This row fails the moment an implementation reads a reservation out of a filename | **[M]** `test_the_binding_is_not_inferred_from_the_run_name` |
| **64** | **a completion of a run nobody started; a conclusion of a non-harness run; a conclusion of an already-settled run** | each refuses, naming which claim failed, and writes nothing | that the caller's run id is authority | **[M]** `test_a_completion_of_a_run_nobody_started_refuses`, `test_concluding_a_non_harness_run_refuses`, `test_concluding_an_already_settled_run_refuses` |
| **65** | **three sequential reservations with three distinct harness runs, every decision read from stored bytes after a process restart**, and at each step every *other* reservation offered against the current run | each conclusion succeeds only against its own run; all six cross-offers refuse; the survey reports three completed; a fourth reservation admits and a retired identity may not be readmitted | **that the binding was only shown for one reservation**, which is how R5-1 survived r5's matrix | **[M]** `test_sequential_reservations_with_distinct_harness_runs_from_stored_bytes` |
| **66** | **failure after the release publication and before the completion, on a correctly bound run** | the release is published and durable; the completion is not; the leftover temporary is reported and not removed; after an operator removes it the run is `unsettled`; every successor refuses; an attributed recovery admits the next reservation | that the window is only reachable for a wrongly bound run, or that it is a dead end | **[M]** `test_a_failure_between_the_release_and_the_completion_blocks_and_recovers` |
| **67** | **identity reuse and stale release evidence, under the binding**: a recovered harness run's own id begun again; release evidence for `RES-1` offered to conclude a correctly bound `RES-2` run | the reuse refuses as `already_published`; the stale evidence refuses at **step 1**, and neither terminal entry is published | that the binding replaced either control | **[M]** `test_a_recovered_harness_runs_identity_is_not_reused`, `test_stale_release_evidence_from_another_reservation_still_refuses` |
| **68** | **the six participants completing on their own external conditions**, with the binding in force | each publishes; the stored start and the stored evidence both carry the field empty | that the new rule makes the six carry a reservation | **[M]** `test_the_six_still_complete_on_their_own_external_conditions`, six rows |
| **69** | **the same validator on both sides**: one mismatching pair checked as a proposed history and as stored bytes | the two problem lists are **equal**, and both name R5-1 | that the writer's rule and the reader's rule are two functions that can drift | **[M]** `test_the_validator_is_the_same_function_on_both_sides` |
| **70** | **D1's second interruption state at T1**: the first-use record's `unlinkat` of its temporary fails after `linkat` succeeded | initialization does not report success; the record and the temporary are one inode; a second initialization refuses `interrupted_initialization` with a recovery that names the same-inode case and does not repeat initialization; `admitted` refuses `interrupted_publication`; the temporary remains | that the substitute can report a published record as unpublished, or that a retry cleans the temporary | `test_lab_implementation.py::test_d1_a_first_use_record_stopped_between_link_and_unlink_is_kept_and_refused` |
| **71** | **the same state at T6** | `begin` does not report publication; a retry refuses `interrupted_publication`; the survey counts the temporary unreadable; all seven participants refuse admission; the temporary remains | that a started run can hide behind its own temporary | `…::test_d1_a_run_start_stopped_between_link_and_unlink_blocks_every_successor` |
| **72** | **the same state in §2.3.3's capture publication** | the publication refuses and permits no mutation; restart discovery reports the basis unusable with its leftover temporary; the temporary remains | that M1 can follow a half-finished publication | `…::test_d1_a_capture_stopped_between_link_and_unlink_permits_no_mutation` |
| **73** | **the same state at P2** | installation raises; neither name is recorded; removal refuses both names; a second installation refuses `EEXIST`; the temporary remains | that cleanup or a retry removes an object this run did not record | `…::test_d1_a_payload_stopped_between_link_and_unlink_is_neither_recorded_nor_removed` |
| **74** | **PR-20260915-LAB-D12-1**: D1's second interruption state at T1, then **all seven participants' real integration points** driven over it | every participant refuses at T4 **before its work is called**; the refusal is the `SuccessorAdmission` the one admission path produced and carries its `(st_dev, st_ino)` comparison; the re-seal still precedes the read; both names, the record's bytes and the ledger are byte-identical afterwards | **that a valid final record admits while its publication is unresolved** — which is exactly what six of the seven did before this row | `test_lab_implementation.py::test_d1_a_record_publication_temporary_refuses_all_seven_before_their_work` |
| **75** | **the successful control for row 74**: the same seven passes over a record published without interruption | all seven admit, reach their work once and settle; the comparison reports no temporary | **that the new check refuses everything**, which is how a refusal passes for a rule | `…::test_d1_a_clean_record_with_no_temporary_still_admits_all_seven_control` |
| **76** | **a temporary whose inode differs from the final record** | all seven refuse; the refusal says the two names are different objects; **nothing removes it**, and both objects' bytes are unchanged | that an unexplained object beside the record is cleaned by the next run | `…::test_d1_a_temporary_that_is_not_the_record_refuses_and_is_never_removed` |
| **77** | **the temporary's `fstatat` refuses** | the participant refuses, naming a failed observation and not an absent temporary | that a name whose resolution is unknown reads as absent — §5.9's rule for the lock, applied here | `…::test_d1_a_temporary_whose_resolution_is_unknown_is_not_an_absent_one` |
| **78** | **T1's operator recovery, its five refusals and its one admitting branch**: identity match; mismatch; no comparison at all; another record's comparison; an unattributed removal; a comparison that no longer holds | the match removes **only** the temporary, leaves the record byte-identical at `st_nlink` 1 and readmits all seven; each of the other five refuses and removes nothing | **that the required comparison is prose an operator can skip** | `…::test_d1_the_t1_recovery_removes_the_temporary_only_on_an_identity_match`, `…_refuses_a_mismatch_and_removes_nothing`, `…_refuses_an_unobserved_comparison`, `…_refuses_a_comparison_that_no_longer_holds` |
| **79** | **T6's operator recovery on the same guard** | the unobserved removal refuses; the matched one removes the temporary; the run is then `unsettled`, not settled, and **every participant still refuses** | that removing a temporary settles the run it belonged to | `…::test_d1_the_t6_recovery_uses_the_same_guard_and_settles_nothing` |
| **80** | **the V7 stop, end to end**: the four directory items applied by the real applier over a model host, the lock inode present, `lifecycle.json` **absent** because V7 is excluded, and all seven participants' admission driven over it | every participant refuses, naming the record it could not read; nothing is created — no record, no temporary, no run entry; the laboratory directory still holds only `runs` | **that provisioning a host opens it.** A provisioned host with no first-use record is fail-closed, and the absence is the state rather than a gap the next run fills | **[M]** `test_v6_provisioning.py::test_a_provisioned_host_without_v7_refuses_all_seven_participants` |
| **81** | **clean application of V12, V4, V9 and V5** over a model host whose parent exists and belongs to the applying identity — *amended 2026-09-17, C-P5.0-LAB-V6-D* | all four created, each with its reviewed owner, group and numeric mode; V9 carries **both** the setgid and the sticky bit | that a provisioning tool can report success for objects it did not verify | **[M]** `…::test_a_clean_application_creates_all_four_exactly` |
| **81a** | **V12's location is derived from both of its children** — *added 2026-09-17, C-P5.0-LAB-V6-D review*. A layout whose laboratory and recovery directories have different basenames, a layout that puts them under **different parents**, a layout that gives them one name, and a laboratory path with no parent-and-name reading | V12's `expected_children` are the two children's **own** basenames; the divergent-parent, shared-name and malformed-path layouts each refuse `creation-refused` for item V12 before anything is created | **that a derived parent may be read off one child.** Reading `laboratory_directory` alone builds a V12 that is not V5's parent, reports it created, and declares two children it does not have — and `expected_children` is the gate `object-unexpected-content` refuses on, so an idempotent re-application would refuse against objects the delta itself created. It is the implicit parent V12 exists to prevent, one level down; 124 focused tests passed while it stood | **[M]** `…::test_v12_is_the_parent_of_v4_and_v5_and_names_their_real_children`, `…::test_v12s_expected_children_follow_the_layout_rather_than_two_literals`, `…::test_children_under_two_different_parents_refuse_rather_than_picking_one`, `…::test_one_name_for_both_children_refuses`, `…::test_a_layout_path_with_no_parent_and_name_reading_refuses` (three forms) |
| **82** | **an idempotent re-run** over the same host | all four report `already-provisioned`; **every inode and every `st_ctime_ns` is unchanged**; nothing is removable by the second application | **that idempotence may be a swallowed `EEXIST`** — which is what `install --directory` does, and what §1.4.2 replaced with an exclusive `mkdirat` | **[M]** `…::test_a_re_run_is_idempotent_and_writes_nothing` |
| **83** | **every wrong-object refusal**: a regular file and a symbolic link at the name; the wrong owner; the wrong group; the wrong mode; an unexpected file; an unexpected subdirectory | each refuses with its own classification, **nothing is repaired or replaced**, and the object is byte- and inode-identical afterwards. The subdirectory case refuses on content **and** link count; the file case on content alone, which is the control that keeps them apart | that an unexplained object at a provisioned name may be adopted, corrected or overwritten | **[M]** `…::test_an_object_of_the_wrong_type_refuses_and_is_left_alone` and the five beside it |
| **84** | **the parent refusals**: an absent parent, a parent an identity other than the applying one may write, a parent that is not a directory, and a run started as an identity the items do not declare | each refuses **before anything is created**, and the parent is never created. The second is `/opt/freedom-blades`'s observed shape and it is not worked around by widening the entry | **that a provisioning tool creates whatever it needs.** An object no reviewed item describes is not one a run may invent | **[M]** `…::test_an_absent_parent_refuses_rather_than_being_created`, `…::test_a_parent_the_provisioning_identity_does_not_own_exclusively_refuses`, `…::test_a_run_that_is_not_the_declared_owner_refuses_before_it_creates` |
| **85** | **a partial application and its rollback boundaries**: a refusal part-way; then a reversal over a not-empty directory, over an object that is no longer the one created, and over an item the application only verified | the partial run names what exists, what refused and what was never attempted; the reversal removes **only** what this application created, in reverse order, on a re-observed `(st_dev, st_ino)`, and each of the three boundaries refuses and removes nothing | that a reversal may remove an object it did not create, one that has been replaced, or one that still holds somebody's state | **[M]** `…::test_a_partial_application_reports_what_exists_and_what_was_never_tried`, `…::test_a_rollback_removes_exactly_what_this_application_created` and the four refusal rows |
| **86** | **the trace's two structural claims**: every reviewed effect step's identity, and whether anything registers the evidence role | all 34 effect steps are `run_as="root"`; **no production caller registers the evidence role at all**, and the evidence root's literal appears in exactly one module | **that D1 is opened by something today.** It is specified, named and unbuilt, and a provisioned directory is not evidence that anything opens it | **[M]** `…::test_every_reviewed_effect_step_runs_as_root`, `…::test_no_production_caller_registers_the_evidence_role`, `…::test_no_module_that_publishes_exclusively_names_the_evidence_root` |
| **87** | **a failure at each of the six points after a successful `mkdirat`** — the open of the created directory, `fchown`, `fchmod`, the read-back's `fstat`, the read-back's listing and the parent's `fsync` — each injected at the real syscall over real temporary-directory objects, plus one injected part-way through the sequence and the four reversal boundaries over the residue | no raw `OSError` escapes; each refuses with its own member of `POST_CREATION_REFUSALS`, carrying no path and no operating-system message; the directory that now exists is in the returned `applied` and `created` beside the items completed before it, and every later item is `not_attempted`; the identity is recorded for the five failures that still hold the created descriptor and declared **unknown** for the open failure; guarded rollback removes a residue whose identity still matches, and refuses — removing **nothing**, including the identified objects — when the identity is unknown, changed, or the directory is not empty | **that a provisioning tool may report `applied == ()` while a root-owned directory it created sits at the target**, or let an ordinary `OSError` out of the window between the creation and the barrier. Codex Blocking PR-20260916-LAB-V6R1-1: both were reproduced, and 45 focused tests passed while they stood, because none injected inside creation | **[M]** `…::test_a_failure_after_creation_is_closed_and_reports_the_residue` (six rows), `…::test_the_two_reviewer_reproductions_are_closed`, `…::test_a_post_creation_failure_reports_the_objects_completed_before_it`, `…::test_a_rollback_removes_a_residue_whose_identity_is_known`, `…::test_a_rollback_refuses_a_residue_whose_identity_was_never_established`, `…::test_an_unidentified_residue_stops_the_whole_reversal`, `…::test_a_rollback_of_a_residue_refuses_an_object_that_has_been_replaced`, `…::test_a_rollback_of_a_residue_refuses_a_directory_that_is_not_empty`, `…::test_an_applied_item_cannot_pair_an_outcome_with_the_wrong_identity`, `…::test_every_post_creation_failure_point_has_its_own_closed_classification` — *new 2026-09-16, V6-R2 remediation* |
| **88** | **a failure to release each of the three descriptors the application path holds** — the created object's, and the parent's synchronizable and traversal descriptors — injected at the real `os.close` over real temporary-directory objects, in **both** orders a `close()` can fail in: releasing the descriptor and then reporting failure, and reporting failure having released nothing. Each is also run **against every one of the six refusals of row 87**, and against a parent refusal and a wrong-object refusal raised before any creation | no raw `OSError` escapes; a release failure with nothing else in flight refuses `descriptor-not-released` carrying the object **exactly once** in `applied` and `created`, with the identity its read-back established, every later item `not_attempted` and the provisioner's private account agreeing with the returned run; a release failure **while a refusal is unwinding never replaces it**, in all eight pairings; every descriptor after a failing one is still released; no descriptor is passed to `os.close` twice; the barrier is not issued after the decision to refuse; and an already-provisioned item refuses while `created` stays empty and nothing is written | **that a `finally: os.close(fd)` is cleanup rather than an operation.** It can fail, and when it does it either escapes unclassified or silently overwrites the refusal it was unwinding — turning a fact about an operator's object into an unclassified error about a descriptor. Codex Blocking PR-20260916-LAB-V6R2-1: the first was reproduced with V11 on disk, `provisioner.created == ()` and no `ProvisioningRun` returned, and 60 focused tests passed while it stood, because none injected into a release | **[M]** `…::test_a_close_failure_at_each_descriptor_is_closed_and_accounts_for_the_object` (three descriptors x two orders), `…::test_the_reviewer_reproduction_is_closed`, `…::test_a_failure_to_release_the_created_descriptor_refuses_before_the_barrier`, `…::test_a_close_failure_reports_the_objects_completed_before_it`, `…::test_a_cascading_close_failure_still_releases_the_descriptor_after_it`, `…::test_a_descriptor_whose_release_failed_is_never_closed_again`, `…::test_a_close_failure_never_replaces_an_established_refusal` (six refusals x two orders), `…::test_a_close_failure_never_replaces_a_refusal_raised_before_any_creation`, `…::test_a_close_failure_after_identity_is_established_keeps_guarded_rollback`, `…::test_an_already_provisioned_item_whose_descriptor_will_not_release_refuses`, `…::test_the_application_path_releases_every_descriptor_through_one_helper` — *new 2026-09-16, V6-R3 remediation* |
| **89** | **a failure to release each of the four descriptors `verify()` and guarded `rollback()` hold** — the observed object's and its parent's in `_verify_one`, and the same pair in `_remove` — injected at the real `os.close` over real temporary-directory objects, in **both** orders a `close()` can fail in, and each run against the reversal's own identity-mismatch, not-empty and `rmdir` refusals and against a wrong-object refusal reached through `ensure()` | no raw `OSError` escapes; `verify()` returns **one observation per target** with the release reported as an appended `descriptor-not-released` discrepancy and every later target still observed, writing nothing — no inode and no `st_ctime_ns` moves; the same condition through `_existing()` refuses `descriptor-not-released` with the item represented **exactly once** as `already-provisioned`, `created` empty and every later item `not_attempted`; a release failure never replaces an object's own finding or a reversal's identity, emptiness or `rmdir` refusal; a failure on the object's descriptor **before** the `rmdir` removes nothing and leaves the live created account unchanged; a parent-release failure **after** a successful `rmdir` reports the removal, drops the object from `created` exactly once and cannot be retried against it; every descriptor after a failing release is still attempted and none is passed to `os.close` twice | **that `verify()` may abandon the re-observation, and that a reversal may report an effect it did not have.** The read-only V6 re-observation of §9.3 **I12** promises every finding; raising over a descriptor returned none of them, including for the targets the failure says nothing about. And a `close()` after a successful `rmdir` raised before `rollback()` updated its account, so the live provisioner went on naming an object it had just removed and offered it for a second reversal. Codex Blocking PR-20260916-LAB-V6R3-1: all four sites were reproduced, and 88 focused tests passed while they stood, because none injected into these four | **[M]** `…::test_the_verification_returns_every_observation_when_a_release_fails` (two descriptors x two orders), `…::test_a_verification_release_failure_does_not_stop_the_later_targets`, `…::test_a_verification_release_failure_never_replaces_the_objects_findings`, `…::test_an_already_provisioned_apply_whose_verification_cannot_release_refuses`, `…::test_a_verification_release_failure_never_replaces_an_apply_refusal`, `…::test_a_reversal_release_failure_never_replaces_the_causal_refusal` (three refusals x two orders), `…::test_a_release_failure_before_the_rmdir_removes_nothing`, `…::test_a_release_failure_after_the_rmdir_reports_the_removal`, `…::test_a_reversal_that_refuses_part_way_reports_what_it_already_removed`, `…::test_every_verification_descriptor_after_a_failing_release_is_still_attempted`, `…::test_a_reversals_parent_descriptor_is_released_after_its_object_descriptor_fails`, `…::test_the_four_reported_release_sites_no_longer_raise`, `…::test_no_release_anywhere_in_the_module_is_a_bare_close`, `…::test_a_reversal_refusal_cannot_disagree_with_what_it_removed`, `…::test_an_observation_reports_only_findings_from_the_closed_vocabulary`, `…::test_a_removal_effect_exists_only_where_the_object_is_gone` — *new 2026-09-16, V6-R4 remediation* |
| **90** | **no arm** — C-P5.0-LAB-I3-R2, §7.4. The entry point without `--arm-i3-controlled-write`, with it but no `--identity`, and the verifier constructed unarmed or with a truthy stand-in for `True` | the entry point constructs no lookup, probe or verifier and exits `3` (`4` without an identity); the unarmed verifier returns `not-armed` before its first read — no account lookup, no `/proc` read — and nothing is written | that an operator entry point may observe or write before it is armed | **[M]** `test_i3_verifier.py::test_no_arm_reads_nothing_and_writes_nothing`, `…::test_armed_without_an_identity_reads_nothing`, `…::test_an_unarmed_verifier_reads_nothing_and_writes_nothing`, `…::test_the_in_code_gate_admits_only_true_itself` |
| **91** | **the two gates, each reversed alone**: the command-line check deleted from the entry point's syntax tree; the in-code gate's body deleted from the verifier's | with the command-line check gone the verifier is armed from the absent flag and refuses before any read; with the in-code gate gone the entry point still returns before constructing anything. **Negative control:** the unarmed verifier with its gate deleted does write, so the gate is load-bearing | that one gate is the whole defence | **[M]** `…::test_the_arm_is_the_flag_itself_and_the_route_follows_the_check`, `…::test_reversal_the_command_line_arm_removed_still_writes_nothing`, `…::test_reversal_the_in_code_gate_removed_is_stopped_by_the_arm` |
| **92** | **every admission mismatch**: approved host, kernel or architecture; payload digest; any reviewed account unresolved; any of the four uid or gid fields; `getresuid`/`getresgid` disagreeing with status; the participant without `freedomlab`; an absent, repeated or malformed status field or mask; `CapEff ⊄ CapPrm`; `CapAmb ⊄ CapPrm ∩ CapInh`; `fs.protected_hardlinks` `0`, other or unreadable; a mount of another type, device, read-only or unparseable; a directory absent, a symbolic link, a file, of the wrong owner, group or mode; a group- or other-writable state parent; canonical `R` present; an earlier verifier name; an unavailable nonce; an occupied name; an unrecognized invocation; an underivable layout | each refuses with its own member of `ADMISSION_REFUSALS` **before the first write**: no stage completes and the model host is inode-for-inode unchanged. **Negative control:** with the policy parse reversed, a policy-`0` host is written to | that a precondition may be established after the first write, or not at all | **[M]** `…::test_every_status_mismatch_refuses_before_the_first_write` (13 cases), `…::test_malformed_status_bytes_refuse`, `…::test_an_unreadable_status_refuses`, `…::test_process_ids_that_disagree_with_status_refuse`, `…::test_the_participant_must_already_hold_the_laboratory_group`, `…::test_the_hardlink_policy_must_be_exactly_one`, `…::test_the_mount_must_be_the_approved_filesystem`, `…::test_every_directory_mismatch_refuses_before_the_first_write` (13 cases), `…::test_account_and_ownership_mismatches_refuse`, `…::test_a_directory_owned_by_another_account_refuses`, `…::test_a_participant_that_is_not_the_named_identity_refuses`, `…::test_an_unavailable_nonce_refuses`, `…::test_an_occupied_name_refuses_when_the_residue_listing_missed_it`, `…::test_only_the_approved_target_is_admitted`, `…::test_a_changed_payload_refuses_before_the_first_write`, `…::test_an_unrecognized_invocation_refuses`, `…::test_the_layout_is_derived_or_refused`, `…::test_reversal_the_policy_admission_removed_writes` |
| **93** | **all four contexts under both reviewed identities**: root runs T1 under V4, §2.3.3 under V5 and P2 under canonical `R/bin`; the participant runs T6 under V9 | each context verifies: the owner condition observed, link count two with both names and one after the temporary is removed, the pinned bytes through both names, every object removed, a clean survey, every descriptor released, and the model host unchanged afterwards | that I3 may be closed on fewer than the four publication contexts | **[M]** `…::test_the_four_contexts_and_two_identities_are_the_reviewed_ones`, `…::test_both_invocations_verify_all_four_contexts_and_leave_nothing`, `…::test_the_production_layout_is_read_from_the_reviewed_definitions` |
| **94** | **P2 is `root:root 0555` under the owner condition — C-P5.0-LAB-I3-D1** — and decision B's exception: `R` `0700` and `R/bin` `0755`, both `root:root` | the P2 file is `fchown`ed to the reviewed root owner and group and `fchmod`ed `0555` on its descriptor before `linkat`, and both names are observed at that mode; `R` and `R/bin` are created, moded, recorded and removed; `case_runtime`, P2's effect row and `P-04` all carry `0555` | that P2's installed mode may differ from the contract, or that the verifier may leave `R` behind | **[M]** `…::test_p2_is_root_root_0555_published_under_the_owner_condition`, `…::test_p2_and_p04_now_install_and_assert_root_root_0555`, `test_r13_remediation.py::test_a_compliant_observation_from_real_output_satisfies_its_contract[P-04-0 0 555 regular file]` |
| **95** | **capability evidence at the operation**: the five masks and `NoNewPrivs` read at admission and again immediately before each `linkat`; a state that changes between the two | each mask is classified from its own field; `CAP_DAC_OVERRIDE`, `CAP_DAC_READ_SEARCH` and `CAP_FOWNER` are reported per mask; a changed state fails the context before `linkat` and is cleaned up | that the admission-time state may stand in for the state at the operation | **[M]** `…::test_capability_evidence_keeps_permitted_effective_and_bounding_apart`, `…::test_capability_state_is_observed_again_at_every_link`, `…::test_a_process_state_change_before_the_link_fails_and_cleans_up` |
| **96** | **only `CapBnd` changes** | the reported effective set is unchanged. **Negative control:** with `CapEff` read from `CapBnd` in the classification's syntax tree, an effective capability the process does not hold is reported | PR-20260919-LAB-I3R1-1 — that `CapBnd` is evidence of `CapEff` | **[M]** `…::test_changing_only_capbnd_never_changes_what_is_reported_effective` (3 cases), `…::test_reversal_reading_capbnd_as_capeff_is_caught` |
| **97** | **no `CAP_FOWNER` claim** | the only sentence about `CAP_FOWNER` in any rendering is `NOT_ATTRIBUTION`, which disclaims; no operative source still says P2 depends on it | that the verifier isolates, requires or proves `CAP_FOWNER` | **[M]** `…::test_no_result_claims_that_p2_required_or_proved_cap_fowner`, `…::test_no_operative_source_keeps_p2s_cap_fowner_dependency` |
| **98** | **an occupied name**: a foreign object appears at the final name between admission and `linkat`, or at the temporary name before the exclusive open | `linkat`'s `EEXIST` (or `O_EXCL`'s) refuses; the foreign object keeps its bytes and is never tracked or removed; the verifier's own temporary is removed through its guard; the run needs an operator. **Negative control:** with the exclusive claim reversed to a rename onto the name, the occupant's bytes are destroyed | that a publication may overwrite what it did not create | **[M]** `…::test_an_occupied_destination_is_never_overwritten`, `…::test_reversal_a_non_exclusive_link_overwrites_the_occupant`, `…::test_a_foreign_temporary_name_is_never_touched` |
| **99** | **the two-name observation** | at the first removal both names already resolved to one regular file, link count two, with the pinned bytes, and the verifier had recorded `two-name-observation` immediately after `exclusive-link` | that the second interruption state of §6.2 is unobservable, or that removal may precede observation | **[M]** `…::test_both_names_are_one_inode_with_link_count_two_and_exact_bytes_before_removal` |
| **100** | **success** | the temporary is removed, then the published name, then the containing directory is barriered; no verifier name remains and the survey is clean | that success may leave residue or skip the barrier | **[M]** `…::test_success_removes_both_names_barriers_the_parent_and_leaves_no_residue` |
| **101** | **every state boundary, injected at the real syscall** — the exclusive open, the write, the data barrier, `fchmod`, P2's `fchown`, `linkat` in T1, §2.3.3, P2 and T6, the two-name `fstatat` and read, both unlinks, the entry barrier, `mkdirat`, `fchmod` and the barrier of `R` and `R/bin`, and both `rmdir`s — plus an open that created its name and then reported failure | never `verified`; the failing context records its stage and a member of `STAGE_FAILURES`; later contexts are `not-attempted`; every tracked fate agrees with the disk; a failure whose objects were all removed through their guards, with every barrier and descriptor finished, is `failed-no-residue` and leaves the host unchanged; residue, a failed removal barrier or an unidentified object is `failed-operator-attention`; an object whose identity was never established is never removed | that a partial state may be unaccounted or reported as success | **[M]** `…::test_every_injected_boundary_failure_is_accounted_and_never_success` (20 cases), `…::test_the_participant_invocation_is_accounted_the_same_way`, `…::test_a_temporary_whose_creation_outcome_is_unknown_is_never_removed` |
| **102** | **foreign or replaced objects**: the published name replaced after `linkat`; `R/bin` replaced before its removal; `R` replaced before its removal | the replaced name is never removed and is reported `residue-name-resolves-to-another-object`; a directory holding one is `residue-directory-not-empty`; the run needs an operator. **Negative control:** with the identity comparison reversed to accept any object, the foreign file is removed | that a removal may take an object the verifier did not identify | **[M]** `…::test_a_replaced_published_name_is_left_alone`, `…::test_reversal_without_the_identity_comparison_the_foreign_object_is_removed`, `…::test_a_replaced_bin_directory_is_not_removed`, `…::test_a_replaced_canonical_root_is_not_removed` |
| **103** | **cleanup, descriptor-finalization and barrier failures**: a cleanup barrier; a write descriptor that is released and then reports failure; a directory descriptor at finalization; each accounting condition of `final_status` | each is non-success with the failure counted, never retried; only a fully clean account is `verified`. **Negative control:** with `final_status` reversed to ignore accounting, a run with residue reports `failed-no-residue` | that cleanup, finalization or a barrier may fail silently | **[M]** `…::test_a_cleanup_barrier_failure_is_non_success`, `…::test_a_write_descriptor_that_is_not_released_is_non_success`, `…::test_a_directory_descriptor_that_is_not_released_at_the_end_is_non_success`, `…::test_the_final_status_needs_every_object_removed_and_a_clean_survey`, `…::test_reversal_ignoring_residue_would_report_a_clean_failure` |
| **104** | **safe output**: secret-looking status lines, masks, account-lookup text, mount lines and operating-system messages injected; hostile values placed directly in a run; an exception escaping the verifier | no injected text, path, traceback or `errno` reaches either stream; values outside a vocabulary render as `unrecognized`; an escaping exception exits `6` and prints nothing about itself; the six exit statuses are distinct and only `verified` is `0` | that host data or exception text may reach an operator surface | **[M]** `…::test_malformed_host_data_and_exception_text_never_reach_the_output`, `…::test_values_outside_the_vocabulary_render_as_unrecognized`, `…::test_the_refusal_field_is_admitted_by_membership`, `…::test_an_unclassified_exception_prints_nothing_about_itself`, `…::test_the_exit_codes_are_distinct_and_only_verified_is_zero`, `…::test_the_cli_exit_status_follows_the_run` |
| **105** | **structure**: the names; the payload; the one `linkat`; the imports | both names are outside the run-identifier, lifecycle, ledger, recovery and case-program grammars; the payload hashes to its pin; `descriptors.py` holds the package's only `os.link` and `renameat(noreplace=True)` calls `linkat`; the verifier imports no participant, harness, executor, materializer, case program, ledger or lock, registers no `EVIDENCE_ROLE` and reads no environment; `is_executable` stays `False` | that the verifier is a second implementation of the primitive, or a route to anything else | **[M]** `…::test_names_are_outside_every_lifecycle_ledger_recovery_and_case_program_grammar`, `…::test_the_payload_is_fixed_harmless_and_pinned`, `…::test_there_is_one_exclusive_link_and_the_fused_publication_uses_it`, `…::test_the_verifier_reaches_no_participant_harness_or_executor`, `…::test_the_standing_gates_are_unchanged` |
| **106** | **the two ruled creation modes — C-P5.0-LAB-I3-R3** | `case_program.ROOT_DIRECTORY_MODE` and the verifier's `CANONICAL_ROOT_MODE` are both `0700` and `B3-02` compares `700`, so canonical `R` is created at §1.4.1 C1's mode; `R/bin` stays `0755`; `case_runtime.CASE_PROGRAM_TEMPORARY_MODE` is `0500` and exactly one exclusive file creation in the root invocation uses it | that `R` may be created `0755`, or that P2's temporary mode is the shared default | **[M]** `…::test_mkroot_creates_canonical_r_as_0700_not_0755`, `…::test_p2_alone_creates_its_temporary_0500` |
| **107** | **the `0600` default is unchanged, and the `0500` never publishes** | T1, §2.3.3 and T6 pass no creation mode and every creation they make is `EXCLUSIVE_CREATION_MODE`; the root invocation's creations are exactly `0500, 0600, 0600` and the `ubuntu` invocation's is `0600`; P2's descriptor carries `fchown` then `fchmod 0555` before its `linkat`, and every mode observed at a link is a context's **final** mode, never `0500`; P2's real installation path publishes `0555` from a `0500` temporary | that P2's creation mode reaches a published name, or that the ruling moved the shared default | **[M]** `…::test_t1_capture_and_t6_keep_the_shared_0600_default`, `…::test_p2_is_root_root_0555_on_the_descriptor_before_linkat`, `test_lab_implementation.py::test_p2_creates_its_temporary_0500_and_publishes_0555` |

**Rows 74–79 were added on 2026-09-15 by the C-P5.0-LAB-D12-R1 remediation, and
they are not [M] either.** They drive the real writers, the real admission and
the seven real integration points over real files under a temporary directory on
this workstation. Row 74 is the finding's own reproduction: it **fails against
the submitted tree**, where all seven admit. **The single-point reversal that
catches it is RV-admit-temporary** — deleting
`refusals.extend(interruption.refusals())` from `lifecycle_storage.read_and_admit`
— and it also catches rows 76 and 77. Five further reversals, one per added
conjunct, catch rows 77, 78 and 79; all six are recorded in the
[remediation handback](phase-5-0-reserved-laboratory-d12-r1-remediation-handback.md).
**Row 75 is caught by no reversal and must not be**: it is the successful
control, and a control that failed when a refusal was removed would be testing
the refusal rather than controlling for it.

**Rows 80–86 were added on 2026-09-16 by the V6 provisioning remediation,
C-P5.0-LAB-V6-R1, and all seven are [M].** They drive the real applier and the
real admission path over a **model host under a temporary directory** — two
parent directories, four provisioned directories, a lock inode and no
`lifecycle.json` — with an injected account database that resolves the declared
owner to the running process's own ids. **That establishes the mechanism's
behaviour there and nothing about `oracle-test`**, where not one of the eleven
items has been applied. No test creates a link, so none of them bears on
**I3**; none needs privilege; and none reads the host's account database.

**Rows 70–73 were added on 2026-09-15 by the D1 correction, and they are not
[M].** They drive the real writers over real files under a temporary directory
on this workstation, reaching the state by failing the one `unlinkat` after
`linkat` succeeded. That establishes the mechanism's behavior there and nothing
about the target.

**Rows 21, 28, 30 and 35 must fail revision 3's protocol and hold under this
one. Rows 41–52 must fail revision 4's, and rows 53–69 must fail revision 5's**,
and that was checked rather than asserted.

For r5, with the three r5 repairs reversed in a scratch copy of the package,
**49 of the 76 rows in the R4 regression module failed**, including all three
named reproductions and the omitted-ledger case; that figure is r5's and is not
re-earned here.

For r6, with the R5-1 repair reversed in a scratch copy — schema back to 1, the
reservation field removed from the start, the presence check restored in place of
the equality, the writer's stored-start read removed, and §5.12's step 0 removed
— **36 of the 58 rows in the R5 regression module fail**, the reviewer's
reproduction among them. The **22** that pass are named rather than glossed: six
are the grammar rows for a pure helper that has no r5 counterpart, one is the
statement of the binding contract text, and the remaining fifteen are the
preserved controls that must hold under both revisions — the six-participant
completions, the matching positive control, the injected-fact refusal, the stale
evidence refusal, the identity-reuse refusal, the R4-2 profile refusal and the
release/completion window. **A matrix in which the superseded revision also
passes is a matrix that is not testing the correction**, and the rows that do
pass are there to show the repair broke nothing.

**Rows 39 and 40 were corrected in r5.** Row 39's successful trace previously
published participant completion before the release its completion asserted, and
supplied both lifecycle-owned facts as observations; it now runs §5.12's order and
derives them. The claim that it established the complete sequence is withdrawn and
dated in §9.4.

**Rows 50, 51 and 52 are corrected in r6.** Each of them begins a harness run,
and each now begins it **bound to the reservation it concludes**. Row 51's
successful path additionally passes §5.12's step 0, and row 52's three sequential
reservations are each concluded against their own run. Their earlier statements
are not withdrawn — the sequences they exercised did happen — but they did not
establish the binding, because there was none to establish. §9.5 dates that.

### 9.3 The implementation checks that would establish the real properties

**None of these has been performed, and this pass ran no real filesystem
durability drill.** They belong to the eventual implementation review and the
separately authorized target work.

| # | Check | Why a model cannot stand in |
|---|---|---|
| I1 | that an `O_PATH` descriptor really refuses `fsync` with `EBADF`, and the separately opened `O_RDONLY` directory descriptor really accepts it | the model refuses by construction. The kernel is the authority |
| I2 | that the target filesystem implements `fsync` on a directory as the containing-entry barrier | filesystem behaviour; preflight **V8** |
| I3 | that exclusive publication's `linkat` succeeds on the target's filesystems under their hard-link policy — *re-scoped 2026-09-15, D1; amended 2026-09-19, C-P5.0-LAB-I3-D1* | filesystem behaviour and a kernel policy; preflight **V6** observes prerequisites and **does not close this check**. Closing it needs a separately released controlled write verification. P2 is `root:root 0555` and relies on the filesystem-UID owner condition, like the other owner-condition publications; it has no `CAP_FOWNER` dependency. The verifier must still observe actual operation-time capability masks and must not equate `CapBnd` with `CapEff`. V7 remains excluded until I3 closes. **§7.4 is the reviewed route to that verification** — implemented 2026-09-19 under C-P5.0-LAB-I3-R2, traced by §9.2 rows 90–105, and **unperformed**; a verified invocation is evidence for the maintainer's decision and closes nothing itself. |
| I4 | that a real power loss after a successful publication leaves the parent listing the entry | a modelled crash is an assignment |
| I5 | that a real restoration interrupted between rename and barrier leaves the destination at its previous content | same |
| I6 | that the inherited descriptor table contains exactly the declared entries with the declared modes | the model hands out indices |
| I7 | that `execveat(…, AT_EMPTY_PATH)` executes the reviewed payload under every disposable identity | needs identities, payload and interpreter, none provisioned |
| **I8** | **that a participant holding only read and search on the record's directory can really `fsync` it** — that the re-seal needs no write permission on the target kernel and filesystem | **§5.6 rests on it for all seven participants, and it is the single assumption that decides whether the correction is implementable as specified** |
| **I9** | **that each participant's completion condition is observable at all** — a backend attributable to one run, a whole-tree consistency check, a half-unpacked distribution, a post-reset baseline | **§5.11 names five of these and none is confirmed. A completion condition nobody can observe is a run that never settles** |
| **I10** | **that all seven participants run as `ubuntu`** | preflight **V10**. The ledger's attribution rests on it |
| **I11** | **that a reservation identity is unique over the laboratory's whole lifetime on the target**, not merely within one record's history | the model refuses a readmitted identity inside one history it can read. Nothing here establishes that an operator or a future tool cannot mint the same identity against a re-initialized record, and the binding's value depends on it |
| **I12** | **that the provisioned objects on the target really are what §7 defines** — the released subset V1, V2, V3, V12, V4, V9 and V5 — *new 2026-09-16, V6 remediation; **evidence-entry clause withdrawn 2026-09-17, C-P5.0-LAB-V6-D-R1*** | §7's verification fields and `provisioning.VERIFICATION_PROCEDURE` say what to observe; the applier's `verify()` performs the type/owner/group/mode half over real objects. **Nothing has been applied to `oracle-test`**, so this is unperformed. The `evidence` entry this row also named is gone with V11: §7.3's first row is **decided**, not open — the maintainer withdrew the location (decision A), nothing is provisioned under `/opt`, and no entry there is observed or expected to fail. This check is the post-provision repetition of the read-only survey, so **V6 stays performed-but-not-closed until it is separately authorized and performed** |

### 9.4 Dated erratum — the superseded successful-trace claim

**2026-09-11.** r4 §5.7 T11/T12 and §9.2 row 39 stated that the successful
lifecycle trace established the complete terminal sequence. **It did not.** The
trace supplied `release()` returned RELEASED and the release entry reached
durable storage as injected observations at a point where the reservation record
still said `running`, and only appended the release afterwards. The order it
certified had no reachable successful path, and the green row masked the
contradiction rather than establishing the sequence. The claim is **withdrawn**.
What is now claimed for row 39, and for row 51 beside it, is the order in §5.12,
with both conditions derived from the operations that produced them.
### 9.5 Dated erratum — the unestablished reservation binding

**2026-09-11.** r5 §5.12 stated that the harness's completion *"names the
reservation it concluded, so the binding can be checked"*, and r5 §5.11.1's P7
presented the completion's reservation field as that binding. **Neither claim
holds.** The completion recorded the name and there was no stored fact to check it
against: the `participant_started` entry carried no reservation, and the value on
the evidence was copied from the release publication the same caller supplied. The
claim is **withdrawn**. r5 §9.2 rows 50–52 exercised harness runs that were not
bound to the reservations concluding them, so whatever else those rows
established, they did not establish this. What is now claimed is §5.5's stored
field, §5.11.1's P7 and P9, and §5.12's step 0, with rows 53–69 as the model
evidence and the reviewer's own reproduction among them.

---

## 10. Assumptions, and what this document does not do

**Every [A] in one place.** `oracle-test`'s participants all run as `ubuntu` —
now preflight item **V10** rather than a carried assumption; `ubuntu` holds
passwordless `sudo`; `/run` is a tmpfs; `/var/lib/freedom-blades/recovery` and
`/etc/postgresql/16/main` are root-only — **and `/opt/freedom-blades/evidence`
is no longer an [A] because it is no longer anything**, *amended 2026-09-17,
C-P5.0-LAB-V6-D*: §7.3's first row observed its **parent** as `1001:1001 0755`,
which defeated the root-only claim for the entry, and the maintainer withdrew
the location rather than widening the rule. `R` is `/var/lib/fb-evidence-p5-0`,
whose parent `/var/lib` is root-owned and not group- or other-writable, and
nothing is provisioned under `/opt`;
host administrators are trusted to obey the reservation and are **not prevented
from ignoring it, and are not claimed to be**; the filesystem under `R` is
unconfirmed, with its hard-link support and hard-link policy (V6, re-scoped from
`RENAME_NOREPLACE` by D1 and approved 2026-09-15 as a **read-only prerequisite
survey** that does not prove real `linkat` viability and does not close I3 — a
controlled write verification needs separate authorization before execution) and
the directory-barrier semantics with it; **that each participant's completion condition is observable**, which
§5.11 names per participant and I9 collects; and — **new in r6** — **that a
reservation identity is never minted twice over the laboratory's lifetime**,
which is I11 and on which the stored binding's value depends. None was verified on
the target by this document, and no host was inspected.

**A power loss may retain unsynchronized changes.** The model discards
everything no barrier made durable, which is the *worst* case and not a promise
about Linux. A real power loss may leave more than the model does — it may even
leave everything. Nothing in this contract may be read as the claim that Linux
guarantees the model's outcome; the barriers are specified so that the worst
case is survivable, and `MODEL_LIMITS` says the manual page wins wherever the
model and it disagree.

**It accepts nothing.** It approves no digest, populates none of the twelve
unconfirmed target facts, authorizes no host action, no SSH, no synchronization,
no provisioning, no database operation and no execution. **The 2026-09-16 V6
remediation and the 2026-09-17 topology disposition change none of that** —
*amended 2026-09-17, C-P5.0-LAB-V6-D*: V12 is a definition, V11 is withdrawn,
`execution/provisioner.py` is an artifact for review, **nothing was applied to
any host**, V6 remains performed-but-not-closed, and V7 is excluded from the
release it completes. It does not clear the
operational-ineligibility control, does not move `is_executable`, and does not
reduce the three C-7 cases' unresolved status.

EH-R16-1, PR-20260910-1/2/3, the September 10 findings, the six September 11
findings, the four September 11 re-review findings, the three R3 findings, the
three R4 findings and **PR-20260911-R5-1** remain **Open** until a reviewer says
otherwise. **PR-20260915-LAB-D12-1 is remediated and not closed**: the repair and
its evidence are §§5.6, 5.9, 6.2 and rows 74–79, and the finding stays Open until
an independent Codex re-review accepts them. **LAB-X1 is a new open item**, with
the owner, evidence and execution stop condition §6.4 records. **R4-1 carries a positive technical recommendation from the R5
re-review and is still not closed here**; R4-2 and R4-3 remain open pending this
binding. **No finding is closed on the implementer's authority.** LAB-1 remains
**Important and unrepaired**, and its labelled reproduction is unchanged. Package
5.0 remains **not ready**, P5.0-R5 **Blocking**, OD-62 **Open**.

**Current next step, corrected 2026-09-13:** the independent R3 review above
accepted LAB-1's local remediation. Peter has already selected the shared
`ubuntu` identity design and accepted the ten-item §7 delta as a design basis;
neither choice confirms actual target identity or authorizes provisioning. The
remaining sequence is maintainer direction on C-7/EH-R16-1 and the unimplemented
delta, implementation plus independent review if authorized, the separately
authorized read-only target preflight, and only then a separate execution
decision. **Passing tests advance none of those gates.**
