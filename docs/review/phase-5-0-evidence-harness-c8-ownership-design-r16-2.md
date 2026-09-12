# Conflict C-8, second revision — ownership, custody and recovery

> **Superseded — erratum, 2026-09-09.** This revision was **not accepted** in
> project review R2 of 2026-09-09. It is superseded by
> [`phase-5-0-evidence-harness-c8-ownership-design-r16-3.md`](phase-5-0-evidence-harness-c8-ownership-design-r16-3.md).
> Its text below is preserved unchanged and is **not** a current proposal. Four
> statements in it are wrong and are corrected in r16-3 §1.3, §5, §9.3 and
> §9.5: the blanket "not closable on Linux" of §6; the claim in §6 that a
> descriptor's benefit "is already obtained by comparing the root's identity";
> the `/proc/self/fd` example in §6, which fixes only the first component and
> not the `journal` component it names; and P3's `[proved]` label in §7, which a
> digest-then-reopen sequence does not earn. R-C8-1 … R-C8-4 were **not**
> accepted and are restated in r16-3 §8. EH-R16-1 remains open with its existing
> identity.


**Design artifact submitted for Codex technical acceptance. Nothing here is
implemented.** No source file changed for EH-R16-1 in the submission that carries
this document. `cleanup.py`, `execution/executor.py` and
`execution/case_program.py` are byte-identical to the tree R16 reviewed, so the
defect R16 reproduced is still present and reproducible; §8 says how, and the
reproductions are in the tree and labelled as such.

Supersedes `phase-5-0-evidence-harness-c8-ownership-design-r16.md`, which was
**rejected**. §1 records why, in the reviewer's terms and without hedging.

Scope: EH-R16-1 only.

---

## 1. Why the first revision was wrong

Two claims in it were false and one was unreviewable. They are set out first
because everything below is shaped by them.

### 1.1 `mkdirat` followed by `openat` does not detect child replacement

The rejected §3.1 proposed

```text
fd    = open(parent, O_RDONLY|O_DIRECTORY|O_NOFOLLOW)
mkdirat(fd, name, mode)
child = openat(fd, name, O_RDONLY|O_DIRECTORY|O_NOFOLLOW)
fchmod(child, mode); fstat(child)
```

and said a replacement between the `mkdirat` and the `openat` "is detectable and
is treated as such", taking the exit-`66` path. **That is not true.** Holding
`fd` fixes which directory `name` is looked up *in*. It says nothing about
whether the entry `name` refers to is the entry `mkdirat` created. If the entry
is unlinked and a different directory is created under the same name in the
interval, `openat` succeeds, `fstat` returns the replacement's device and inode,
and the run records the replacement's identity as its own. There is no
comparison in that pseudocode, no second reading, and therefore no branch that
could reach exit `66`. The claim of detection was an assertion with no mechanism
under it.

The correction is not a better sequence. It is that **the sequence cannot exist
on Linux**, which §3 establishes and §4 works around.

### 1.2 The root-permission argument does not cover the plan's own directories

The rejected §5.1 said replacement of an entry inside the root "requires uid 0 or
`CAP_DAC_OVERRIDE`", and that an actor holding either "is outside the threat
model". Read against the generated plan, that is wrong twice.

* Two directories the plan creates are **group-writable by an identity the run
  itself constructs**: `probe` and `probe-ro` are `0770 root:freedomsheet`. Any
  member of `freedomsheet` may create, rename and unlink entries in them. That is
  not hypothetical: **the plan does exactly that**, as `freedomsheet`, in steps
  `B4-16`, `B4-17`, `B4-18`, `B4-22`, `B4-23`, `B4-29`, `B4-30` and `B4-31`.
* `CAP_DAC_OVERRIDE` is not an outside-the-model capability here either. The plan
  grants it **ambiently** to `fbprobe` in `B5-E4`, `B5-E6`, `B5-C6-01` … `B5-C6-04`
  (`--addamb=cap_dac_override --addamb=cap_dac_read_search`). An identity holding
  it can write in every directory under the root, including `before/` — which
  holds the two configuration recovery inputs — and `bin/`, which holds the
  program every ownership guard runs.

So "all relevant replacement requires an unrestricted root adversary" is false,
exactly as the review says. §5 replaces the assertion with the inventory.

### 1.3 Deferring the directory inventory made the risk unreviewable

The rejected design promised to enumerate the group-writable subset "in the
implementation". That put the one fact a reviewer needs to size the residual
behind the checkpoint that was supposed to size it. The inventory is §5, taken
from the generated plan as it stands today.

---

## 2. What this design does and does not set out to prove

It does **not** claim to make every dependent operation safe. It claims:

1. to say exactly what each ownership claim rests on, and to separate the claims
   that are **proved by an observation** from those that rest on a **trust
   boundary** and from those that are **residual and need acceptance**;
2. to remove the single highest-consequence effect — installing PostgreSQL
   authentication configuration from a capture — from dependence on any identity
   claim at all, by comparing content rather than custody; and
3. to reduce the exposed interval for every other dependent effect from *the
   whole run* to *one process spawn*, and to state plainly that the remaining
   interval cannot be closed by any design on Linux.

Every item in §7 is labelled with which of those three it is.

---

## 3. The lifecycle trace — object, descriptor, and every later resolution

Requirement 1 of the review. Each row names what the operation acts on and every
pathname resolution that happens after the identity was acquired. "Resolutions"
counts full-path resolutions of the reviewed absolute path by a fresh process.

| # | Phase | Operation | Acts on | Later resolutions of the same name |
|---|---|---|---|---|
| 1 | creation | `R-B-ROOT`: `stat` the root, must fail | a pathname | — establishes nothing (R14, EH-R14-1) |
| 2 | creation | `B3-01` `mkroot`: `mkdir(2)` on the root | a pathname in a parent resolved by the same call | — |
| 3 | creation | `mkroot`: `open(root, O_DIRECTORY\|O_NOFOLLOW)` | **a second resolution of the same pathname** | this is §1.1's gap |
| 4 | creation | `mkroot`: `fchmod`, `fstat` on that descriptor | the object the descriptor refers to | none — descriptor-addressed |
| 5 | provisioning | `B3-03` … `B3-12`: `install -d` / `install` for 6 directories and 6 files | pathnames under the root | one per step; 12 |
| 6 | provisioning | `B3-14` … `B3-18`, `B4-08`, `B5-C6-08`, `B5-C6-09`: `chattr` | pathnames | one per step; 7 |
| 7 | capture | `B6-01`, `B6-02`: `install` the live `pg_hba.conf` / `pg_ident.conf` into `before/` | the live file by pathname, the capture by pathname | 2 reads, 2 writes |
| 8 | materialization | the two `MaterializeStep`s write the reviewed configuration bytes over the live files | pathnames outside the root | 2 |
| 9 | execution | probe and capability steps `open`, `rename`, `unlink`, `symlink` under the root, several **as `freedomsheet`** and several as `fbprobe` with ambient `CAP_DAC_OVERRIDE` | pathnames | ≈40 |
| 10 | cleanup | `CL-01`, `CL-02`: `install` each `before/<file>` over its live file — **consumes the recovery input** | the capture by pathname, the live file by pathname | 2 reads, 2 writes |
| 11 | cleanup | `CL-03` reload, `CL-04`/`CL-05` verify | PostgreSQL, not the filesystem | — |
| 12 | cleanup | 29 reversals: `rm --force`, `rmdir`, `chattr -ia` | pathnames under the root | 29 |
| 13 | cleanup | `CL-37` `statroot`: re-read the root's identity | **a resolution of the root pathname** | the only comparison in the current design |
| 14 | cleanup | `CL-38` `rmdir` the root | a pathname | 1, after the comparison |

**The defect is rows 10 and 12 preceding row 13.** Thirty-one pathname
resolutions, two of which install bytes read from under the root as the disposable
instance's authentication configuration, happen before the one comparison.

**The other thing the trace shows** is that between row 4 and row 13 the harness
holds **no descriptor at all**. Every step is a separate process; nothing carries
a descriptor from one to the next. Identity, once acquired, is not held — it is
re-derived by name each time, and the current design re-derives it once.

---

## 4. What establishes that the created object is the opened object

Requirement 2. The honest answer has three parts.

### 4.1 On Linux, nothing does

There is no primitive that returns a descriptor to a newly created **directory**.

* `mkdir(2)` and `mkdirat(2)` return `0` or `-1`. They do not return a descriptor.
* `O_TMPFILE` creates an unnamed **regular file**; it is invalid with
  `O_DIRECTORY` and there is no unnamed-directory equivalent.
* `linkat(2)` refuses directories with `EPERM`, so the file pattern — create
  unnamed, `fstat` the descriptor, then `linkat` it into place, where `EEXIST`
  proves the name was free *and* the descriptor is the linked object — has no
  directory analogue.
* `renameat2(RENAME_NOREPLACE)` moves an existing directory; producing the
  existing directory is the same problem one level along.

So creation and identity acquisition **cannot be made atomic for a directory**.
Any design that claims otherwise is claiming a syscall that is not there. This is
stated as a property of the platform, not of this harness.

### 4.2 What is therefore claimed instead

> `mkroot`'s reported `(device, inode)` is the identity of *whatever directory
> occupied the reviewed root pathname at the instant immediately after `mkdir(2)`
> returned success*. It is the identity of the created object **if and only if no
> other actor had write access to the root's parent directory during the interval
> between the `mkdir` and the `open`.**

That is a trust boundary, and it is named as one. It is not detection.

### 4.3 Making the boundary checkable instead of assumed

The boundary is a statement about the **parent** directory's owner, group and
mode. Today the harness knows nothing about the parent:
`approved_target.APPROVED_TARGET_FACTS` records the host, kernel, filesystem root,
type, device, PostgreSQL instance and database — and **not** the parent's
ownership or mode. The rejected design leaned on an assumption about `/var/lib`
that this repository has never established.

**Proposal P1.** Add the parent's ownership and mode as **reviewed target facts**,
in the same shape and with the same fail-closed handling as the twelve existing
unconfirmed ones:

```text
root_parent_owner   root_parent_group   root_parent_mode
root_parent_device  root_parent_inode
```

`mkroot` reports the parent's observed `uid`, `gid`, `mode`, `device` and `inode`
from a descriptor it already needs — five additional observation keys on an
existing verb — and an expectation contract compares them with the reviewed facts
before the step may be satisfied. While any of the five is `UNCONFIRMED` the
executor refuses at the same gate that already refuses for the interpreter and
`E7` facts.

What this buys: the trust boundary stops being an assumption about a
distribution's conventions and becomes a reviewed value plus a compared
observation. What it does **not** buy: it does not close §4.1's interval. A parent
that is `root:root 0755` narrows *who* could have raced to uid 0 and
`CAP_DAC_OVERRIDE` holders; it does not prove none did.

**Authorization impact, stated rather than assumed:** obtaining the five values
requires reading `oracle-test`. That is the read-only preflight the maintainer has
authorized and **assigned to Codex**. This design does not perform it and does not
ask to. The five facts ship `UNCONFIRMED`, which means the executor refuses — the
same posture the interpreter facts have held since R11.

### 4.4 Residual R-C8-1, needing acceptance

> The interval between `mkdir(2)` returning and the identity read completing is
> not closed and cannot be closed on Linux. An actor with write access to the
> root's parent during that interval can substitute a directory whose identity the
> run will record as its own, and no subsequent guard will disagree, because every
> guard compares against that recorded identity.

Proposed disposition: **accept**, conditional on P1's parent facts being confirmed
and compared. Not accepted here; routed to the maintainer through Codex.

---

## 5. The ownership and mode inventory, from the generated plan

Requirement 3. Taken from the plan as generated by the current tree; every mode
and owner below appears verbatim in a rendered `install` vector, and the root's
mode is `case_program.ROOT_DIRECTORY_MODE`.

### 5.1 Who may create, rename or unlink an entry in each directory

| Directory | Mode / owner | May replace entries in it |
|---|---|---|
| the root's **parent** | **unknown — not a target fact** | unknown. P1 |
| `…/fb-evidence-p5-0` (root) | `0755 root:root` | uid 0; `CAP_DAC_OVERRIDE` |
| `…/journal` | `0750 root:freedomjournal` | uid 0; `CAP_DAC_OVERRIDE` |
| `…/archive` | `0750 root:freedomcoord` | uid 0; `CAP_DAC_OVERRIDE` |
| `…/before` | `0700 root:root` | uid 0; `CAP_DAC_OVERRIDE` |
| `…/bin` | `0755 root:root` | uid 0; `CAP_DAC_OVERRIDE` |
| `…/probe` | **`0770 root:freedomsheet`** | uid 0; `CAP_DAC_OVERRIDE`; **any member of `freedomsheet`** |
| `…/probe-ro` | **`0770 root:freedomsheet`** | uid 0; `CAP_DAC_OVERRIDE`; **any member of `freedomsheet`** |

`CAP_DAC_OVERRIDE` is held ambiently by `fbprobe` in `B5-E4`, `B5-E6` and
`B5-C6-01` … `B5-C6-04`. `freedomsheet` is the run identity of `B4-09` … `B4-31`.
Both identities are created by this run.

### 5.2 Which declared subjects are replaceable by a non-root identity

Seven of the 29 contained mutations, all in the two `0770` directories:

```text
…/probe/stage1.target      …/probe/stage1.moved
…/probe/stage2.target      …/probe/s4-1.target
…/probe-ro/s4-0.unlink     …/probe-ro/s4-0.moved
…/probe-ro/s4-2.target
```

Four of them are **already unlinked or renamed by the run itself**, as
`freedomsheet` (`B4-18`, `B4-23`, `B4-31`, and the `stage1`/`s4-0` rename pairs).
So for these paths the sequence *"the object this run created is gone, and
something else may be at its name"* is not an attack scenario — it is the plan's
own control flow, and cleanup's `rm --force` on those names is already a removal
of whatever is there.

### 5.3 The two subjects whose replacement matters most

* `…/before/pg_hba.conf` and `…/before/pg_ident.conf` are the **recovery inputs**.
  Cleanup reads them and installs them as the disposable instance's authentication
  configuration. Reachable by uid 0 and by `CAP_DAC_OVERRIDE`.
* `…/bin/case` is the **installed** case program. It is not what the guards run —
  `mkroot` and `statroot` are confined to the **bootstrap** copy in the repository
  tree — but it is what every experiment runs, and `P-04`/`P-05` assert its mode,
  owner and SHA-256 at one point in time, by pathname.

### 5.4 The guards' own trust chain

The guards run `case_program.py` from the repository worktree. That worktree is
**group-writable by `discordbot` and `freedomweb`** — residual `H-1`, decisions
`D5.0-12` / `OD-65` — and its integrity rests on the review manifest digest
recomputed on the host at plan time. This is stated because a design about
identity that did not state where its own instrument comes from would be
incomplete. It is not new risk and this design does not change it.

### 5.5 Symlinks and changed parent resolution

`statroot` opens with `O_DIRECTORY|O_NOFOLLOW`, so a symbolic link at the final
component is refused rather than followed, and a non-directory is refused. Every
**intermediate** component is followed normally, so a replaced parent resolves the
guard somewhere else — and is detected, because the identity it reports will not
match the recorded one. Detection of a changed parent is therefore a *consequence*
of comparing identity, not a separate check, and it holds only after row 4 of §3;
before that, §4.4 applies.

---

## 6. Replacement between a guard and its effect

Requirement 4.

**It cannot be closed for any deletion.** `rmdir(2)`, `unlinkat(2)` — with or
without `AT_REMOVEDIR` — and every coreutils removal name a **final path
component**. Linux has no `funlinkat(2)` (FreeBSD 13 does), so there is no way to
say *"remove the object this descriptor refers to"*. A descriptor-relative
operation fixes every component except the last, which is precisely the one whose
identity is in question.

Two alternatives were considered and are **not proposed**:

* **`/proc/self/fd/N` prefixing.** The boundary opens the root once, passes the
  descriptor to each child, and vectors are written
  `/proc/self/fd/3/journal/000001.seal`. This makes every intermediate component
  immune to renaming, because the descriptor keeps referring to the same inode.
  It does not fix the final component. Its costs are large and reviewable: the
  reviewed vectors would no longer be the reviewed absolute paths, so
  `DisposableTarget.contained_path` could no longer validate them as written; the
  design acquires a procfs dependency; and every permitted executable would have
  to inherit the descriptor. Cost is high, benefit is partial, and the benefit it
  does give is already obtained by comparing the root's identity.
* **Descriptor-addressed removal inside the case program**, i.e. a new `remove`
  verb that opens, verifies identity and calls `unlinkat` on a descriptor-relative
  name. This still names a final component, so it does **not** close the window;
  and it moves deletion out of `rm`/`rmdir`, whose argument vectors the plan pins
  and whose behaviour is `--force` on one named non-directory and `rmdir` on one
  empty directory, into the reviewed program's own code. That is a widening of the
  privileged interface for no closure. Rejected.

**Residual R-C8-2, needing acceptance.**

> Between a guard and the operation it protects there is one process spawn. A
> replacement performed in that interval is not detected by any mechanism in this
> design, and none is available.

Proposed disposition: **accept**, on the ground that the alternative closes
nothing and costs the reviewed-vector property. Not accepted here.

---

## 7. The proposed mechanism

Each item is labelled **[proved]** (an observation decides it), **[boundary]** (it
rests on a stated trust boundary), or **[residual]** (it needs acceptance).

### P1 — parent facts, compared *(§4.3)* — [boundary]

Five reviewed target facts, five additional observation keys on `mkroot`, one
expectation contract, executor refusal while unconfirmed. **No new verb, no new
argument kind, no new arity, no new privilege, nothing writable.** Authorization
impact: obtaining the values is the read-only preflight, which is Codex's.

### P2 — a root identity guard immediately before every root-dependent step — [proved, for whole-root substitution only]

A cleanup step is *root-dependent* when its correctness depends on the object at
the reviewed root path being the one whose identity `mkroot` recorded:

| Step kind | Root-dependent | Why |
|---|---|---|
| `RESTORE` | yes | its source is `…/before/<file>` |
| `REVERSAL` under the root | yes | it resolves a path under the root |
| `RELOAD`, `VERIFY` | yes, transitively | they make a restore effective and attribute its result |
| `REVERSAL` on account, group, membership, role, database, unit | **no** | their subjects are outside the filesystem hierarchy |

`CleanupPlan.for_mutations()` emits one `REVALIDATE` immediately before each
root-dependent step; that step's `requires_revalidated` names it; and
`ordering_holds()` gains a clause asserting the immediacy, so a plan that violates
it is a `PlanRefused` at generation time rather than a comment. In the current
plan that is 2 restores + 1 reload + 2 verifications + 29 reversals = **34**
guards, each a read-only `statroot` that creates and changes nothing.

**What P2 proves:** that the whole root was not substituted between two adjacent
cleanup steps. **What it does not prove:** anything about a descendant (§5.2), and
anything about the interval in §6.

### P3 — configuration restoration by content, not by custody — [proved]

This is the substantive change, and it makes the highest-consequence effect
independent of every identity claim above.

* The capture steps `B6-01`/`B6-02` additionally record the **SHA-256 of the live
  file they copied**, as an observation compared against nothing — it is a
  recorded fact, not an expectation.
* The cleanup `RESTORE` step is preceded by a **digest re-read of the capture it
  is about to install**, and runs only if that digest equals the one recorded at
  capture time.
* A mismatch is a new fixed category, `RESTORE_NOT_VERIFIED`: **the `install` is
  not issued at all**, the declared file stays out of `restored_files`, so
  `ConfigurationRestoration.problems()` reports it, and the state is S-B.

A capture substituted by any route — root replacement, descendant replacement,
`CAP_DAC_OVERRIDE`, uid 0 — has different bytes and is refused. Substituting it
with the *original* bytes is not an attack: those are the bytes the restore wants.

**Cost, stated:** this needs a read-only `digest <path>` verb on the case program.
That is a **new verb** — one path argument, no flags, no writes — and therefore a
widening of the reviewed interface, however small. It is identified here as
requirement 6 demands, and it is **not implemented**. If Codex prefers not to
widen the verb table, the fallback is P2 alone for the restores, which leaves them
protected only against whole-root substitution; this design recommends P3 and says
why: it is the only item that removes a dependent effect from the identity
argument altogether.

**Residual R-C8-3, needing acceptance:** the digest read and the `install` are two
processes, so §6's interval applies to the restore as well. The failure mode
narrows from *"install arbitrary substituted bytes"* to *"install bytes that
matched at check time and were swapped in the interval"*.

### P4 — recovery instructions that do not assume custody — [proved]

`RECOVERY_PROCEDURE` step 3 currently tells an operator to reinstall from the
retained captures. If a guard did not match, or a capture digest did not match,
the retained files are not established to be this run's, and that instruction
would tell the operator to do what P2 and P3 just refused.

`CleanupOutcome` gains `ownership_revalidated: bool | None` and
`recovery_inputs_verified: bool`; neither defaults to the safe-looking value, and
`None` selects the unverified path. A new `UNVERIFIED_RECOVERY_PROCEDURE` names
the retained paths, states that custody of the original bytes is not established,
and directs the operator to a source outside the disposable root. **It prescribes
no reinstall.**

### P5 — independently safe recovery proceeds — [proved]

Account, group, membership, role, database and unit reversals do not depend on any
filesystem identity claim; their ownership comes from Band-0 absence baselines and
the two catalog-listing baselines. A failed guard must not suppress them, or a
root-replacement scenario would additionally leave four groups, three accounts, a
role and a database behind.

### P6 — the descendant inventory is rendered, not argued — [residual]

§5.1 and §5.2 are generated into the rendered concrete plan from the plan's own
declared modes, so the seven replaceable subjects and the two ambient-capability
identities are visible to every reviewer of every future revision rather than
asserted in prose here.

**Residual R-C8-4, needing acceptance.**

> Cleanup's `rm --force` on the seven `probe` / `probe-ro` subjects removes
> whatever is at those names. A `freedomsheet` member can put something else
> there, and the plan's own steps unlink four of them, so the names are known to
> be free at cleanup time.

Two dispositions, and the choice is the maintainer's:

* **(a) accept**, with the inventory rendered. The removal is bounded — one named
  non-directory each, no recursion, no wildcard — and confined to two directories
  this run created; or
* **(b) refuse** to remove those seven, always reporting them preserved. This
  converts a possible wrongful deletion into guaranteed residue, and therefore
  makes **every** successful run end in S-B with an operator step.

This design recommends **(a)**, because (b) makes the S-B state meaningless by
making it universal, and a state that always fires reports nothing.

### P7 — what changes, exactly

| Surface | Change | Authorization impact |
|---|---|---|
| verbs | **one new**: `digest <path>`, read-only, one `TARGET_PATH` argument (P3) | widening — maintainer decision |
| verbs | `mkroot` reports five more observation keys (P1); no arity or argument change | observation widening — flagged |
| arguments, arities, privileges, identities | **none** | — |
| syscalls | `mkroot` gains `fstat` on the parent descriptor; `digest` reads a file | within the existing read-only surface |
| target facts | five new, shipping `UNCONFIRMED`; executor refuses while any is | requires the read-only preflight, which is Codex's |
| `cleanup.py` | `is_root_dependent`; one `REVALIDATE` per root-dependent step; `requires_revalidated` extended to `RESTORE`/`RELOAD`/`VERIFY`; `ordering_holds()` immediacy clause; `RESTORE_NOT_VERIFIED`; `UNVERIFIED_RECOVERY_PROCEDURE`; two `CleanupOutcome` fields | none |
| `execution/executor.py` | the `requires_revalidated` skip generalised beyond `REVERSAL`; capture-digest comparison before a restore; guard results threaded into `classify_cleanup` | none |
| `execution/case_program.py` | `mkroot` parent observation; `digest` verb | as above |
| source coverage | unchanged file set; every changed file already in `COVERED_SOURCES` | manifest version 9 → 10 |
| cleanup state | S-B additionally for an unverified capture or an unmatched guard; `preserved` unchanged in meaning | none |
| recovery instructions | a second, non-prescriptive procedure | none |

**Nothing in this design removes an object, raises a privilege, adds an identity,
adds a writable operation, or admits a new executable.**

---

## 8. The regression matrix

Requirement 7. Injected boundary and injected materializer only; every effect
fake; no host operation.

Two labels, and they mean different things:

* **[reproduction]** — asserts the behaviour of the **current, unfixed** tree.
  These are in the submission now, in
  `tests/phase_5_0_evidence/test_r16_1_ownership_reproduction.py`, and they will
  have to be inverted when the mechanism lands. They are evidence that the defect
  is real, not evidence that anything is fixed.
* **[proposed]** — cannot be written until the mechanism exists. Listed so Codex
  can accept or reject the coverage at the checkpoint rather than after.

| # | Review bullet | Case | Label |
|---|---|---|---|
| 1 | replacement between creation and identity read | `mkroot` records a replacement's identity, and every later guard agrees with it, so the run reports S-C | **[proposed]** — asserts §4.4 is **not** detected, which is the honest form |
| 2 | root replacement before cleanup, sentinel descendants, substitute captures | both `install` restores and all descendant removals are issued **before** the mismatch is seen | **[reproduction]** — present |
| 2b | the same, after the fix | no `install`, no `rm`, no `rmdir`, no `chattr` is issued; every subject residue; unverified recovery procedure | **[proposed]** |
| 3 | descendant-only replacement, root identity matching | the removal of a `probe` subject is issued although the object is not the created one | **[reproduction]** — present |
| 3b | entries in a `freedomsheet`-writable directory | the plan's own inventory names exactly the seven §5.2 subjects | **[reproduction]** — present, asserted against the generated plan |
| 4 | symlink substitution and unexpected parent resolution | `statroot` refusing (`O_NOFOLLOW`) and a differing device both fail the guard | **[proposed]** for the restores; the root case exists today |
| 5 | replacement between validation and effect | the guard matches and the effect still lands on a replaced object | **[proposed]** — asserts R-C8-2 is a stated limitation, not a closed hole |
| 6 | failed identity reads, uncertain creation, timeout, interruption | four cases | **[reproduction]** — the last three exist in `test_r14_remediation.py`; the failed-read case is added |
| 7 | no installation from unverified captures | a capture whose digest differs is not installed | **[proposed]** — P3 |
| 7b | safe recovery instructions when custody is not established | the unverified procedure is reported and prescribes no reinstall | **[proposed]** — P4 |
| 8 | successful ordinary cleanup and restoration | all guards match, both restores run, S-C, no retained inputs | **[reproduction]** — exists; must keep passing |
| 8b | safe independent recovery after a dependent operation is refused | accounts, groups, role and database are still removed when a guard fails | **[reproduction]** — present |

Every **[reproduction]** row asserts the **absence or presence of specific
commands** from the fake boundary's own call log, not an S-B label.

---

## 9. Summary of what needs a decision

| Id | What | Who decides |
|---|---|---|
| P1 | five parent target facts; obtaining them is the read-only preflight | maintainer, on Codex's recommendation |
| P3 | a new read-only `digest` verb | maintainer — it widens the reviewed interface |
| R-C8-1 | create-to-identify interval, not closable on Linux | maintainer, via Codex |
| R-C8-2 | guard-to-effect interval, not closable on Linux | maintainer, via Codex |
| R-C8-3 | digest-to-install interval for the restore | maintainer, via Codex |
| R-C8-4 | `rm` on the seven replaceable probe subjects — (a) accept or (b) refuse and always report residue | maintainer, via Codex |
| — | the rest of §7 | Codex technical acceptance |

Package 5.0 remains **not ready**, P5.0-R5 **Blocking**, OD-62 **Open**.
`is_executable` is `False` for the independent EH-R16-4 reason. Nothing in this
document is execution authority and no digest in this submission is an approved
one.
